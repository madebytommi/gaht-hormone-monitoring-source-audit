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
    "analyte": {"estradiol", "total_testosterone"},
    "recommendation_type": {"target_interval", "upper_threshold", "lower_threshold", "physiologic_range", "laboratory_reference_range", "monitoring_frequency", "specimen_timing", "qualitative_instruction", "not_specified"},
    "comparison_operator": {"less_than", "less_than_or_equal", "greater_than", "greater_than_or_equal", "between", "within_reference_range", "approximately", "not_applicable", "not_specified"},
    "specimen_timing": {"peak", "trough", "mid_cycle", "before_next_dose", "after_application", "any_time", "route_specific", "not_specified"},
    "comparable_status": {"directly_comparable", "comparable_with_qualification", "not_comparable", "undetermined"},
    "verification_status": {"pending", "verified", "needs_revision", "excluded"},
    "another_review_needed": {"yes", "no"}
}

def parse_decimal(val):
    if not val: return None
    try:
        d = Decimal(val)
        if d.is_nan() or d.is_infinite():
            return None
        return d
    except InvalidOperation:
        return None

def is_valid_date(val):
    if not val: return False
    try:
        datetime.strptime(val, "%Y-%m-%d")
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
        
    def log_error(self, file, row, field, msg):
        self.errors.append(f"{file} row {row} field '{field}': {msg}")

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
                    # Empty file is rejected, header is required
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
        src_id = row['source_id']
        if not re.match(r"^SRC\d{4}$", src_id):
            self.log_error(self.sources_path, row_idx, "source_id", "Invalid format")
        if src_id in self.source_ids:
            self.log_error(self.sources_path, row_idx, "source_id", "Duplicate ID")
        self.source_ids.add(src_id)
        
        self.source_verification[src_id] = row['verification_status']

        pub_year = row['publication_year']
        if not re.match(r"^\d{4}$", pub_year):
            self.log_error(self.sources_path, row_idx, "publication_year", "Must be 4-digit integer")

        if not is_valid_date(row['access_date']):
            self.log_error(self.sources_path, row_idx, "access_date", "Invalid date format")

        for field, vocab in SOURCE_VOCABS.items():
            if row[field] not in vocab:
                self.log_error(self.sources_path, row_idx, field, f"Value '{row[field]}' not in {vocab}")

        if row['document_type'] == 'other' and not row['source_notes']:
            self.log_error(self.sources_path, row_idx, "source_notes", "Required when document_type is other")
            
        if row['geographic_scope'] == 'national' and not row['source_notes']:
            self.log_error(self.sources_path, row_idx, "source_notes", "Required when geographic_scope is national")

        ups = row['upstream_source_ids']
        if ups:
            for u in ups.split(';'):
                if not re.match(r"^SRC\d{4}$", u):
                    self.log_error(self.sources_path, row_idx, "upstream_source_ids", f"Invalid format '{u}'")
                elif u == src_id:
                    self.log_error(self.sources_path, row_idx, "upstream_source_ids", "Self-referential")

        vstatus = row['verification_status']
        h_ver_by = row['human_verified_by']
        h_ver_date = row['human_verification_date']
        if vstatus == 'verified':
            if not h_ver_by:
                self.log_error(self.sources_path, row_idx, "human_verified_by", "Required when verified")
            if not is_valid_date(h_ver_date):
                self.log_error(self.sources_path, row_idx, "human_verification_date", "Required and valid date when verified")
        else:
            if h_ver_by or h_ver_date:
                self.log_error(self.sources_path, row_idx, "human_verified_by", "Must be blank unless verified")

    def validate_rec_row(self, row, row_idx):
        rec_id = row['recommendation_id']
        if not re.match(r"^REC\d{4}$", rec_id):
            self.log_error(self.recs_path, row_idx, "recommendation_id", "Invalid format")
        if rec_id in self.rec_ids:
            self.log_error(self.recs_path, row_idx, "recommendation_id", "Duplicate ID")
        self.rec_ids.add(rec_id)

        src_id = row['source_id']
        if src_id not in self.source_ids:
            self.log_error(self.recs_path, row_idx, "source_id", "Foreign key missing")
            
        ext_id = row['extraction_note_id']
        if not re.match(r"^EXT\d{4}$", ext_id):
            self.log_error(self.recs_path, row_idx, "extraction_note_id", "Invalid format")
        if ext_id in self.ext_ids:
            self.log_error(self.recs_path, row_idx, "extraction_note_id", "Duplicate ID")
        self.ext_ids.add(ext_id)
        
        self.check_evidence_note(ext_id, rec_id, row_idx)

        for field, vocab in REC_VOCABS.items():
            if row[field] not in vocab:
                self.log_error(self.recs_path, row_idx, field, f"Value '{row[field]}' not in {vocab}")

        oa = row['original_or_adapted']
        up_id = row['upstream_source_id']
        if oa in ('adapted', 'reproduced', 'derived'):
            if not up_id:
                self.log_error(self.recs_path, row_idx, "upstream_source_id", f"Required when original_or_adapted is {oa}")
            elif not re.match(r"^SRC\d{4}$", up_id):
                self.log_error(self.recs_path, row_idx, "upstream_source_id", "Invalid format")
            elif up_id == src_id:
                self.log_error(self.recs_path, row_idx, "upstream_source_id", "Self-referential")
            elif up_id not in self.source_ids:
                self.log_error(self.recs_path, row_idx, "upstream_source_id", "Foreign key missing")
        elif oa in ('original', 'not_applicable'):
            if up_id:
                self.log_error(self.recs_path, row_idx, "upstream_source_id", "Must be blank")

        numeric_fields = ["lower_bound", "upper_bound", "single_threshold"]
        has_numeric = False
        parsed_nums = {}
        for nf in numeric_fields:
            val = row[nf]
            if val:
                d = parse_decimal(val)
                if d is None:
                    self.log_error(self.recs_path, row_idx, nf, "Invalid numeric value")
                else:
                    has_numeric = True
                    parsed_nums[nf] = d

        if has_numeric and not row['unit']:
            self.log_error(self.recs_path, row_idx, "unit", "Required when numeric field populated")

        # Structural rules
        op = row['comparison_operator']
        rt = row['recommendation_type']
        
        lb = row['lower_bound']
        ub = row['upper_bound']
        st = row['single_threshold']

        if op == 'between':
            if not lb or not ub or st:
                self.log_error(self.recs_path, row_idx, "comparison_operator", "between requires lower and upper bound, no single threshold")
            elif 'lower_bound' in parsed_nums and 'upper_bound' in parsed_nums:
                if parsed_nums['lower_bound'] > parsed_nums['upper_bound']:
                    self.log_error(self.recs_path, row_idx, "lower_bound", "greater than upper_bound")
        elif op in ('less_than', 'less_than_or_equal', 'greater_than', 'greater_than_or_equal'):
            if not st or lb or ub:
                self.log_error(self.recs_path, row_idx, "comparison_operator", "single-sided requires only single_threshold")
        elif op == 'approximately':
            has_single = bool(st)
            has_both = bool(lb and ub)
            if not (has_single ^ has_both):
                self.log_error(self.recs_path, row_idx, "comparison_operator", "approximately requires either single_threshold OR both bounds")
        elif op in ('within_reference_range', 'not_applicable', 'not_specified'):
            if lb or ub or st:
                self.log_error(self.recs_path, row_idx, "comparison_operator", f"{op} requires blank numeric fields")

        if rt == 'target_interval' and op != 'between':
            self.log_error(self.recs_path, row_idx, "recommendation_type", "target_interval requires between")
        if rt == 'upper_threshold' and op not in ('less_than', 'less_than_or_equal'):
            self.log_error(self.recs_path, row_idx, "recommendation_type", "upper_threshold requires less_than or less_than_or_equal")
        if rt == 'lower_threshold' and op not in ('greater_than', 'greater_than_or_equal'):
            self.log_error(self.recs_path, row_idx, "recommendation_type", "lower_threshold requires greater_than or greater_than_or_equal")
        if rt in ('physiologic_range', 'laboratory_reference_range') and op != 'within_reference_range':
            self.log_error(self.recs_path, row_idx, "recommendation_type", f"{rt} requires within_reference_range")
            
        if rt in ('physiologic_range', 'laboratory_reference_range', 'monitoring_frequency', 'specimen_timing', 'qualitative_instruction'):
            if not row['non_numeric_instruction']:
                self.log_error(self.recs_path, row_idx, "non_numeric_instruction", f"Required for {rt}")

        # Non-numeric operators numeric checking is inherently covered above.

        # Verification rules
        vstatus = row['verification_status']
        h_ver_by = row['human_verified_by']
        h_ver_date = row['human_verification_date']
        
        if vstatus == 'verified':
            if not h_ver_by:
                self.log_error(self.recs_path, row_idx, "human_verified_by", "Required when verified")
            if not is_valid_date(h_ver_date):
                self.log_error(self.recs_path, row_idx, "human_verification_date", "Required and valid date when verified")
            if src_id in self.source_verification and self.source_verification[src_id] != 'verified':
                self.log_error(self.recs_path, row_idx, "verification_status", "Recommendation cannot be verified if source is not verified")
        else:
            if h_ver_by or h_ver_date:
                self.log_error(self.recs_path, row_idx, "human_verified_by", "Must be blank unless verified")

        comp = row['comparable_status']
        cg = row['comparison_group']
        cr = row['noncomparability_reason']
        if comp == 'not_comparable' and not cr:
            self.log_error(self.recs_path, row_idx, "noncomparability_reason", "Required when not_comparable")
        if comp in ('directly_comparable', 'comparable_with_qualification') and not cg:
            self.log_error(self.recs_path, row_idx, "comparison_group", f"Required when {comp}")

    def check_evidence_note(self, ext_id, rec_id, row_idx):
        path = os.path.join(self.evidence_dir, f"{ext_id}.md")
        if not os.path.isfile(path):
            self.log_error(self.recs_path, row_idx, "extraction_note_id", f"Evidence note missing: {path}")
            return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if f"# Extraction Note: {ext_id}" not in content:
                self.log_error(self.recs_path, row_idx, "extraction_note_id", "Evidence note missing correct # Extraction Note title")
            
            if f"Recommendation ID: {rec_id}" not in content:
                self.log_error(self.recs_path, row_idx, "extraction_note_id", "Evidence note missing correct Recommendation ID")
                
            required_sections = [
                "## Recommendation", "## Source", "## Exact Location", "## Supporting Excerpt",
                "## Faithful Paraphrase", "## Required Context", "## Source Relationship",
                "## Comparability Assessment", "## Unknowns or Ambiguities",
                "## Claims This Source Does Not Support", "## Verification"
            ]
            for sec in required_sections:
                if sec not in content:
                    self.log_error(self.recs_path, row_idx, "extraction_note_id", f"Evidence note missing section: {sec}")
        except Exception as e:
            self.log_error(self.recs_path, row_idx, "extraction_note_id", f"Failed to read note - {e}")

    def validate_post_process(self):
        if getattr(self, 'sources_rows', None):
            for i, row in enumerate(self.sources_rows, start=2):
                ups = row['upstream_source_ids']
                if ups:
                    for u in ups.split(';'):
                        if u not in self.source_ids:
                            self.log_error(self.sources_path, i, "upstream_source_ids", f"Foreign key {u} missing")

def get_analysis_eligible_recommendations(recs_path):
    eligible = []
    try:
        with open(recs_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('verification_status') == 'verified':
                    eligible.append(row)
    except:
        pass
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
