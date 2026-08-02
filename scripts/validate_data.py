import csv
import argparse
import sys
import re
import os
from decimal import Decimal, InvalidOperation
from datetime import datetime

SOURCES_HEADER = [
    "source_id", "organization", "document_title", "document_type", "version",
    "publication_year", "doi", "official_url", "access_date", "population_scope",
    "geographic_scope", "source_status", "correction_status", "upstream_source_ids",
    "source_notes", "verification_status", "human_verified_by", "human_verification_date"
]

RECOMMENDATIONS_HEADER = [
    "recommendation_id", "source_id", "extraction_note_id", "original_or_adapted",
    "upstream_source_id", "section", "subsection", "table_or_figure", "page",
    "paragraph_or_item", "age_group", "therapy_direction", "population_qualifiers",
    "treatment_phase", "analyte", "measurement_name", "unit", "assay_or_lab_context",
    "recommendation_type", "comparison_operator", "lower_bound", "upper_bound",
    "single_threshold", "non_numeric_instruction", "route", "formulation",
    "dosing_interval", "specimen_timing", "time_since_dose_or_application",
    "short_source_excerpt", "faithful_paraphrase", "required_context", "unknowns",
    "claims_not_supported", "comparison_group", "comparable_status",
    "noncomparability_reason", "extracted_by", "extraction_date", "verification_status",
    "human_verified_by", "human_verification_date", "another_review_needed"
]

SOURCE_VOCABS = {
    "document_type": {"clinical_practice_guideline", "standards_of_care", "clinical_guidance", "other"},
    "population_scope": {"adults_only", "adolescents_and_adults", "lifespan_or_mixed_age", "not_specified"},
    "geographic_scope": {"international", "national", "institutional", "not_explicitly_stated"},
    "source_status": {"current_as_of_access_date", "superseded", "withdrawn", "archived", "unclear"},
    "correction_status": {"not_checked", "none_found_as_of_access_date", "correction_found_incorporated", "correction_found_not_incorporated", "unclear"},
    "verification_status": {"pending", "verified", "needs_revision", "excluded"}
}

REC_VOCABS = {
    "original_or_adapted": {"original", "adapted", "reproduced", "derived", "unclear", "not_applicable"},
    "age_group": {"adult", "adolescent_and_adult", "mixed_age", "not_specified"},
    "therapy_direction": {"feminizing", "masculinizing", "general_gaht", "not_specified"},
    "treatment_phase": {"initiation", "dose_adjustment", "stable_maintenance", "general", "not_specified"},
    "analyte": {"estradiol", "total_testosterone", "testosterone_unspecified"},
    "recommendation_type": {"target_interval", "upper_threshold", "lower_threshold", "physiologic_range", "laboratory_reference_range", "monitoring_frequency", "specimen_timing", "qualitative_instruction", "conditional_action_threshold", "not_specified"},
    "comparison_operator": {"less_than", "less_than_or_equal", "greater_than", "greater_than_or_equal", "between", "within_reference_range", "approximately", "not_applicable", "not_specified"},
    "specimen_timing": {"peak", "trough", "mid_cycle", "before_next_dose", "after_application", "any_time", "route_specific", "not_specified"},
    "comparable_status": {"directly_comparable", "comparable_with_qualification", "not_comparable", "undetermined"},
    "verification_status": {"pending", "verified", "needs_revision", "excluded"},
    "another_review_needed": {"yes", "no"}
}

REQUIRED_SECTIONS = [
    "## Recommendation", "## Source", "## Exact Location", "## Supporting Excerpt",
    "## Faithful Paraphrase", "## Required Context", "## Source Relationship",
    "## Comparability Assessment", "## Unknowns or Ambiguities",
    "## Claims This Source Does Not Support", "## Verification"
]

def parse_decimal(val):
    if not val.strip(): return None
    try:
        d = Decimal(val.strip())
        if d.is_nan() or d.is_infinite():
            return None
        return d
    except InvalidOperation:
        return None

def is_valid_date(val):
    v = val.strip()
    if not v: return False
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", v): return False
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return True
    except ValueError:
        return False

class Validator:
    def __init__(self, sources_path, recs_path, evidence_dir):
        self.sources_path = sources_path
        self.recs_path = recs_path
        self.evidence_dir = evidence_dir
        self.errors = []
        self.source_ids = set()
        self.rec_ids = set()
        self.ext_ids = set()
        self.source_verification = {}

    def log_error(self, file, row, id_val, field, msg):
        disp_id = id_val.strip() if id_val.strip() else "<blank>"
        self.errors.append(f"{file} row {row} (ID: {disp_id}) field '{field}': {msg}")

    def run(self):
        self.sources_rows = self.read_and_validate_header(self.sources_path, SOURCES_HEADER)
        self.recs_rows = self.read_and_validate_header(self.recs_path, RECOMMENDATIONS_HEADER)

        if self.sources_rows is not None:
            for i, row in enumerate(self.sources_rows, start=2):
                self.validate_source_row(row, i)

        if self.recs_rows is not None:
            for i, row in enumerate(self.recs_rows, start=2):
                self.validate_rec_row(row, i)

        self.validate_post_process()

        return len(self.errors) == 0

    def read_and_validate_header(self, path, expected_header):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if header is None:
                    self.errors.append(f"{path}: Missing headers.")
                    return None
                if header != expected_header:
                    self.errors.append(f"{path}: Headers do not match exactly. Expected {expected_header}, got {header}")
                    return None
                rows = []
                for i, row in enumerate(reader, start=2):
                    if len(row) != len(expected_header):
                        self.errors.append(f"{path} row {i}: Incorrect number of fields.")
                    else:
                        rows.append(dict(zip(expected_header, row)))
                return rows
        except Exception as e:
            self.errors.append(f"{path}: Failed to read file - {e}")
            return None

    def validate_source_row(self, row, row_idx):
        src_id = row['source_id'].strip()
        if not re.match(r"^SRC\d{4}$", src_id):
            self.log_error(self.sources_path, row_idx, src_id, "source_id", "Invalid format")
        if src_id in self.source_ids:
            self.log_error(self.sources_path, row_idx, src_id, "source_id", "Duplicate ID")
        if src_id:
            self.source_ids.add(src_id)

        self.source_verification[src_id] = row['verification_status'].strip()

        required_source_fields = [
            "source_id", "organization", "document_title", "document_type",
            "publication_year", "official_url", "access_date", "population_scope",
            "geographic_scope", "source_status", "correction_status", "verification_status"
        ]

        for field in required_source_fields:
            if not row[field].strip():
                self.log_error(self.sources_path, row_idx, src_id, field, "Cannot be blank")

        pub_year = row['publication_year'].strip()
        if pub_year and not re.match(r"^\d{4}$", pub_year):
            self.log_error(self.sources_path, row_idx, src_id, "publication_year", "Must be 4-digit integer")

        if row['access_date'].strip() and not is_valid_date(row['access_date']):
            self.log_error(self.sources_path, row_idx, src_id, "access_date", "Invalid date format")

        for field, vocab in SOURCE_VOCABS.items():
            val = row[field].strip()
            if val and val not in vocab:
                self.log_error(self.sources_path, row_idx, src_id, field, f"Value '{val}' not in {vocab}")

        if row['document_type'].strip() == 'other' and not row['source_notes'].strip():
            self.log_error(self.sources_path, row_idx, src_id, "source_notes", "Required when document_type is other")

        if row['geographic_scope'].strip() == 'national' and not row['source_notes'].strip():
            self.log_error(self.sources_path, row_idx, src_id, "source_notes", "Required when geographic_scope is national")

        ups = row['upstream_source_ids'].strip()
        if ups:
            for u in ups.split(';'):
                u = u.strip()
                if not re.match(r"^SRC\d{4}$", u):
                    self.log_error(self.sources_path, row_idx, src_id, "upstream_source_ids", f"Invalid format '{u}'")
                elif u == src_id:
                    self.log_error(self.sources_path, row_idx, src_id, "upstream_source_ids", "Self-referential")

        vstatus = row['verification_status'].strip()
        h_ver_by = row['human_verified_by'].strip()
        h_ver_date = row['human_verification_date'].strip()
        if vstatus == 'verified':
            if not h_ver_by:
                self.log_error(self.sources_path, row_idx, src_id, "human_verified_by", "Required when verified")
            if not is_valid_date(row['human_verification_date']):
                self.log_error(self.sources_path, row_idx, src_id, "human_verification_date", "Required and valid date when verified")
        else:
            if h_ver_by or h_ver_date:
                self.log_error(self.sources_path, row_idx, src_id, "human_verified_by", "Must be blank unless verified")

    def validate_rec_row(self, row, row_idx):
        rec_id = row['recommendation_id'].strip()
        if not re.match(r"^REC\d{4}$", rec_id):
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_id", "Invalid format")
        if rec_id in self.rec_ids:
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_id", "Duplicate ID")
        if rec_id:
            self.rec_ids.add(rec_id)

        required_rec_fields = [
            "recommendation_id", "source_id", "extraction_note_id", "original_or_adapted",
            "age_group", "therapy_direction", "treatment_phase", "analyte",
            "recommendation_type", "comparison_operator", "specimen_timing",
            "short_source_excerpt", "faithful_paraphrase", "required_context",
            "claims_not_supported", "comparable_status", "extracted_by",
            "extraction_date", "verification_status", "another_review_needed"
        ]

        for field in required_rec_fields:
            if not row[field].strip():
                self.log_error(self.recs_path, row_idx, rec_id, field, "Cannot be blank")

        src_id = row['source_id'].strip()
        if src_id:
            if not re.match(r"^SRC\d{4}$", src_id):
                self.log_error(self.recs_path, row_idx, rec_id, "source_id", "Invalid format")
            elif src_id not in self.source_ids:
                self.log_error(self.recs_path, row_idx, rec_id, "source_id", "Foreign key missing")

        ext_id = row['extraction_note_id'].strip()
        if ext_id and not re.match(r"^EXT\d{4}$", ext_id):
            self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Invalid format")
        if ext_id in self.ext_ids:
            self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Duplicate ID")
        if ext_id:
            self.ext_ids.add(ext_id)

        if ext_id and rec_id:
            self.check_evidence_note(ext_id, rec_id, row_idx)

        ext_date = row['extraction_date'].strip()
        if ext_date and not is_valid_date(ext_date):
            self.log_error(self.recs_path, row_idx, rec_id, "extraction_date", "Invalid date format")

        for field, vocab in REC_VOCABS.items():
            val = row[field].strip()
            if val and val not in vocab:
                self.log_error(self.recs_path, row_idx, rec_id, field, f"Value '{val}' not in {vocab}")

        oa = row['original_or_adapted'].strip()
        up_id = row['upstream_source_id'].strip()

        if up_id:
            if not re.match(r"^SRC\d{4}$", up_id):
                self.log_error(self.recs_path, row_idx, rec_id, "upstream_source_id", "Invalid format")
            elif up_id not in self.source_ids:
                self.log_error(self.recs_path, row_idx, rec_id, "upstream_source_id", "Foreign key missing")
            elif up_id == src_id:
                self.log_error(self.recs_path, row_idx, rec_id, "upstream_source_id", "Self-referential")

        if oa in ('adapted', 'reproduced', 'derived'):
            if not up_id:
                self.log_error(self.recs_path, row_idx, rec_id, "upstream_source_id", f"Required when original_or_adapted is {oa}")
        elif oa in ('original', 'not_applicable'):
            if up_id:
                self.log_error(self.recs_path, row_idx, rec_id, "upstream_source_id", "Must be blank")

        numeric_fields = ["lower_bound", "upper_bound", "single_threshold"]
        has_numeric = False
        parsed_nums = {}
        for nf in numeric_fields:
            val = row[nf].strip()
            if val:
                d = parse_decimal(val)
                if d is None:
                    self.log_error(self.recs_path, row_idx, rec_id, nf, "Invalid numeric value")
                else:
                    has_numeric = True
                    parsed_nums[nf] = d

        if has_numeric and not row['unit'].strip():
            self.log_error(self.recs_path, row_idx, rec_id, "unit", "Required when numeric field populated")

        # Structural rules
        op = row['comparison_operator'].strip()
        rt = row['recommendation_type'].strip()

        lb = row['lower_bound'].strip()
        ub = row['upper_bound'].strip()
        st = row['single_threshold'].strip()

        if op == 'between':
            if not lb or not ub or st:
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", "between requires lower and upper bound, no single threshold")
            elif 'lower_bound' in parsed_nums and 'upper_bound' in parsed_nums:
                if parsed_nums['lower_bound'] > parsed_nums['upper_bound']:
                    self.log_error(self.recs_path, row_idx, rec_id, "lower_bound", "greater than upper_bound")
        elif op in ('less_than', 'less_than_or_equal', 'greater_than', 'greater_than_or_equal'):
            if not st or lb or ub:
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", "single-sided requires only single_threshold")
        elif op == 'approximately':
            has_single = bool(st)
            has_both = bool(lb and ub)
            if not (has_single ^ has_both):
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", "approximately requires either single_threshold OR both bounds")
        elif op in ('within_reference_range', 'not_applicable', 'not_specified'):
            if lb or ub or st:
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", f"{op} requires blank numeric fields")

        if rt == 'target_interval' and op != 'between':
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_type", "target_interval requires between")
        if rt == 'upper_threshold' and op not in ('less_than', 'less_than_or_equal'):
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_type", "upper_threshold requires less_than or less_than_or_equal")
        if rt == 'lower_threshold' and op not in ('greater_than', 'greater_than_or_equal'):
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_type", "lower_threshold requires greater_than or greater_than_or_equal")

        qual_types = {'laboratory_reference_range', 'monitoring_frequency', 'specimen_timing', 'qualitative_instruction', 'not_specified'}
        if rt in qual_types:
            if lb or ub or st:
                self.log_error(self.recs_path, row_idx, rec_id, "recommendation_type", f"numeric fields must be blank for {rt}")

        if rt == 'laboratory_reference_range' and op != 'within_reference_range':
            self.log_error(self.recs_path, row_idx, rec_id, "recommendation_type", f"{rt} requires within_reference_range")

        req_non_numeric = {'laboratory_reference_range', 'monitoring_frequency', 'specimen_timing', 'qualitative_instruction'}
        if rt in req_non_numeric:
            if not row['non_numeric_instruction'].strip():
                self.log_error(self.recs_path, row_idx, rec_id, "non_numeric_instruction", f"Required for {rt}")

        # Analyte specific rules
        if row['analyte'].strip() == 'testosterone_unspecified':
            if not row['measurement_name'].strip():
                self.log_error(self.recs_path, row_idx, rec_id, "measurement_name", "Required to preserve exact source wording for testosterone_unspecified")
            if not row['assay_or_lab_context'].strip() and not row['unknowns'].strip():
                self.log_error(self.recs_path, row_idx, rec_id, "testosterone_unspecified", "Requires either assay_or_lab_context or unknowns to document missing specificity")
            if row['comparable_status'].strip() == 'directly_comparable':
                self.log_error(self.recs_path, row_idx, rec_id, "comparable_status", "testosterone_unspecified cannot be directly_comparable")
            if row['comparable_status'].strip() == 'comparable_with_qualification':
                if row['verification_status'].strip() != 'verified':
                    self.log_error(self.recs_path, row_idx, rec_id, "comparable_status", "testosterone_unspecified can only be comparable_with_qualification when verified")
                if not row['noncomparability_reason'].strip():
                    self.log_error(self.recs_path, row_idx, rec_id, "noncomparability_reason", "Required to explain qualification for testosterone_unspecified")

        # Recommendation type specific rules
        if rt == 'conditional_action_threshold':
            if op not in ('less_than', 'less_than_or_equal', 'greater_than', 'greater_than_or_equal'):
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", "conditional_action_threshold requires single-sided operator")
            if not st or lb or ub:
                self.log_error(self.recs_path, row_idx, rec_id, "conditional_action_threshold", "requires single_threshold and prohibits lower/upper bounds")
            if not row['non_numeric_instruction'].strip():
                self.log_error(self.recs_path, row_idx, rec_id, "non_numeric_instruction", "Required for conditional_action_threshold")

        if rt == 'physiologic_range':
            if op not in ('within_reference_range', 'between', 'approximately'):
                self.log_error(self.recs_path, row_idx, rec_id, "comparison_operator", "physiologic_range requires within_reference_range, between, or approximately")
            if op == 'within_reference_range' and (lb or ub or st):
                self.log_error(self.recs_path, row_idx, rec_id, "physiologic_range", "within_reference_range must have no numeric fields")
            if op in ('between', 'approximately') and (not lb or not ub):
                self.log_error(self.recs_path, row_idx, rec_id, "physiologic_range", "between or approximately requires both lower_bound and upper_bound")
            if st:
                self.log_error(self.recs_path, row_idx, rec_id, "single_threshold", "Prohibited for physiologic_range")
            if row['comparable_status'].strip() == 'directly_comparable':
                self.log_error(self.recs_path, row_idx, rec_id, "comparable_status", "physiologic_range cannot be directly_comparable as a hard target interval")
            if not row['non_numeric_instruction'].strip():
                self.log_error(self.recs_path, row_idx, rec_id, "non_numeric_instruction", "Required for physiologic_range")

        # Verification rules
        vstatus = row['verification_status'].strip()
        h_ver_by = row['human_verified_by'].strip()
        h_ver_date = row['human_verification_date'].strip()

        if vstatus == 'verified':
            if not h_ver_by:
                self.log_error(self.recs_path, row_idx, rec_id, "human_verified_by", "Required when verified")
            if not is_valid_date(row['human_verification_date']):
                self.log_error(self.recs_path, row_idx, rec_id, "human_verification_date", "Required and valid date when verified")
            if src_id in self.source_verification and self.source_verification[src_id] != 'verified':
                self.log_error(self.recs_path, row_idx, rec_id, "verification_status", "Recommendation cannot be verified if source is not verified")
        else:
            if h_ver_by or h_ver_date:
                self.log_error(self.recs_path, row_idx, rec_id, "human_verified_by", "Must be blank unless verified")

        comp = row['comparable_status'].strip()
        cg = row['comparison_group'].strip()
        cr = row['noncomparability_reason'].strip()
        if comp == 'not_comparable' and not cr:
            self.log_error(self.recs_path, row_idx, rec_id, "noncomparability_reason", "Required when not_comparable")
        if comp in ('directly_comparable', 'comparable_with_qualification') and not cg:
            self.log_error(self.recs_path, row_idx, rec_id, "comparison_group", f"Required when {comp}")

    def check_evidence_note(self, ext_id, rec_id, row_idx):
        path = os.path.join(self.evidence_dir, f"{ext_id}.md")
        if not os.path.isfile(path):
            self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", f"Evidence note missing: {path}")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find first nonblank line
            nonblank_lines = [l.strip() for l in lines if l.strip()]
            if not nonblank_lines:
                self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Evidence note is empty")
                return

            if nonblank_lines[0] != f"# Extraction Note: {ext_id}":
                self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Evidence note missing correct # Extraction Note title on first line")

            heading_indices = {}
            for i, line in enumerate(nonblank_lines):
                if line.startswith("## "):
                    if line in heading_indices:
                        self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", f"Duplicate heading: {line}")
                    else:
                        heading_indices[line] = i

            for sec in REQUIRED_SECTIONS:
                if sec not in heading_indices:
                    self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", f"Evidence note missing section: {sec}")

            # Check order of required headings
            found_req_headings = [h for h in nonblank_lines if h in REQUIRED_SECTIONS]
            if found_req_headings != REQUIRED_SECTIONS:
                self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Evidence note required headings are out of order")

            # Check Recommendation ID is within the Recommendation section
            if "## Recommendation" in heading_indices:
                start_idx = heading_indices["## Recommendation"]
                end_idx = heading_indices["## Source"] if "## Source" in heading_indices else len(nonblank_lines)
                rec_id_line = f"Recommendation ID: {rec_id}"
                rec_id_found = False
                for i in range(start_idx + 1, end_idx):
                    if rec_id_line in nonblank_lines[i]:
                        rec_id_found = True
                        break
                if not rec_id_found:
                    self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", "Evidence note missing correct Recommendation ID within ## Recommendation section")

        except Exception as e:
            self.log_error(self.recs_path, row_idx, rec_id, "extraction_note_id", f"Failed to read note - {e}")

    def validate_post_process(self):
        if getattr(self, 'sources_rows', None):
            for i, row in enumerate(self.sources_rows, start=2):
                src_id = row['source_id'].strip()
                ups = row['upstream_source_ids'].strip()
                if ups:
                    for u in ups.split(';'):
                        u = u.strip()
                        if u and u not in self.source_ids:
                            self.log_error(self.sources_path, i, src_id, "upstream_source_ids", f"Foreign key {u} missing")

def get_analysis_eligible_recommendations(recs_path):
    eligible = []
    if not os.path.isfile(recs_path):
        raise FileNotFoundError(f"Recommendations file not found: {recs_path}")

    with open(recs_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != RECOMMENDATIONS_HEADER:
            raise ValueError(f"Malformed recommendations header in {recs_path}")

        for row in reader:
            if len(row) != len(RECOMMENDATIONS_HEADER):
                raise ValueError(f"Malformed row in {recs_path}")
            row_dict = dict(zip(RECOMMENDATIONS_HEADER, row))
            if row_dict.get('verification_status', '').strip() == 'verified':
                eligible.append(row_dict)
    return eligible

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', default='data/sources.csv')
    parser.add_argument('--recommendations', default='data/recommendations.csv')
    parser.add_argument('--evidence-dir', default='extraction/evidence-notes')
    args = parser.parse_args()

    v = Validator(args.sources, args.recommendations, args.evidence_dir)
    try:
        if not v.run():
            for e in v.errors:
                print(e, file=sys.stderr)
            sys.exit(1)

        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
