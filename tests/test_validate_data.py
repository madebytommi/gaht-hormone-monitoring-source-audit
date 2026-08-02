"""
All fixtures in this file are completely arbitrary, synthetic, and non-clinical.
They must never be interpreted as real GAHT recommendations or clinical target intervals.
"""
import unittest
import tempfile
import os
import csv
from scripts.validate_data import Validator, SOURCES_HEADER, RECOMMENDATIONS_HEADER, get_analysis_eligible_recommendations, REQUIRED_SECTIONS

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.tdir = tempfile.TemporaryDirectory()
        self.sources_path = os.path.join(self.tdir.name, 'sources.csv')
        self.recs_path = os.path.join(self.tdir.name, 'recs.csv')
        self.ev_dir = os.path.join(self.tdir.name, 'evidence-notes')
        os.makedirs(self.ev_dir)

    def tearDown(self):
        self.tdir.cleanup()

    def write_csv(self, path, header, rows):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    def write_note(self, ext_id, rec_id, content=None):
        path = os.path.join(self.ev_dir, f"{ext_id}.md")
        if content is None:
            content = f"""# Extraction Note: {ext_id}
## Recommendation
Recommendation ID: {rec_id}
## Source
## Exact Location
## Supporting Excerpt
## Faithful Paraphrase
## Required Context
## Source Relationship
## Comparability Assessment
## Unknowns or Ambiguities
## Claims This Source Does Not Support
## Verification
"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_valid_source_row(self, overrides=None):
        row = {
            "source_id": "SRC9999",
            "organization": "Synthetic Org",
            "document_title": "Synthetic Title",
            "document_type": "clinical_guidance",
            "version": "1.0",
            "publication_year": "2026",
            "doi": "",
            "official_url": "http://synthetic.local",
            "access_date": "2026-08-01",
            "population_scope": "adults_only",
            "geographic_scope": "international",
            "source_status": "current_as_of_access_date",
            "correction_status": "not_checked",
            "upstream_source_ids": "",
            "source_notes": "",
            "verification_status": "pending",
            "human_verified_by": "",
            "human_verification_date": ""
        }
        if overrides: row.update(overrides)
        return [row[h] for h in SOURCES_HEADER]

    def get_valid_rec_row(self, overrides=None):
        row = {
            "recommendation_id": "REC9999",
            "source_id": "SRC9999",
            "extraction_note_id": "EXT9999",
            "original_or_adapted": "original",
            "upstream_source_id": "",
            "section": "Synthetic Section",
            "subsection": "",
            "table_or_figure": "",
            "page": "1",
            "paragraph_or_item": "1",
            "age_group": "adult",
            "therapy_direction": "feminizing",
            "population_qualifiers": "",
            "treatment_phase": "general",
            "analyte": "estradiol",
            "measurement_name": "Synthetic Measure",
            "unit": "",
            "assay_or_lab_context": "",
            "recommendation_type": "qualitative_instruction",
            "comparison_operator": "not_applicable",
            "lower_bound": "",
            "upper_bound": "",
            "single_threshold": "",
            "non_numeric_instruction": "Synthetic non-numeric instruction",
            "route": "",
            "formulation": "",
            "dosing_interval": "",
            "specimen_timing": "not_specified",
            "time_since_dose_or_application": "",
            "short_source_excerpt": "Synthetic excerpt",
            "faithful_paraphrase": "Synthetic paraphrase",
            "required_context": "Synthetic context",
            "unknowns": "",
            "claims_not_supported": "None",
            "comparison_group": "",
            "comparable_status": "undetermined",
            "noncomparability_reason": "",
            "extracted_by": "SyntheticUser",
            "extraction_date": "2026-08-01",
            "verification_status": "pending",
            "human_verified_by": "",
            "human_verification_date": "",
            "another_review_needed": "no"
        }
        if overrides: row.update(overrides)
        return [row[h] for h in RECOMMENDATIONS_HEADER]

    def test_01_headers_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())
        self.assertEqual(len(v.errors), 0)

    def test_02_headers_fail(self):
        self.write_csv(self.sources_path, ["wrong_header"], [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Headers do not match exactly" in e for e in v.errors))

    def test_03_invalid_id_formats_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"source_id": "BAD1234"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_id": "WRONG_ID", "source_id": "BAD1234", "extraction_note_id": "EXT_NO"})])
        self.write_note("EXT_NO", "WRONG_ID")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        err = " ".join(v.errors)
        self.assertIn("BAD1234", err)
        self.assertIn("WRONG_ID", err)

    def test_04_duplicate_ids_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row(), self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row(), self.get_valid_rec_row()])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Duplicate ID" in e for e in v.errors))

    def test_05_invalid_vocab_values_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"document_type": "invalid_type"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"therapy_direction": "invalid_dir"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("invalid_type" in e for e in v.errors))

    def test_06_exact_iso_date_validation(self):
        # Mismatched padding
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"access_date": "2026-8-01"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

        # Impossible date
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"access_date": "2026-02-30"})])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

        # Valid
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"access_date": "2026-08-01"})])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_07_required_source_fields_fail_when_blank(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"organization": ""})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_08_required_rec_fields_fail_when_blank(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"short_source_excerpt": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_09_whitespace_only_required_fields_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"document_title": "   "})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_10_missing_source_foreign_keys_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"source_id": "SRC9999"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_11_missing_evidence_note_files_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_12_mismatched_evidence_note_ids_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        self.write_note("EXT9999", "WRONG_ID")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_13_adapted_reproduced_derived_without_upstream_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"original_or_adapted": "adapted", "upstream_source_id": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_14_original_with_upstream_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row(), self.get_valid_source_row({"source_id": "SRC8888"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"original_or_adapted": "original", "upstream_source_id": "SRC8888"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_15_unclear_with_malformed_or_self_referential_upstream_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        # Self referential
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"original_or_adapted": "unclear", "upstream_source_id": "SRC9999"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Self-referential" in e for e in v.errors))

    def test_16_source_level_upstream_ids_fail(self):
        # Malformed
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"upstream_source_ids": "BAD123"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

        # Self-referential
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"upstream_source_ids": "SRC9999"})])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_17_other_document_type_requires_notes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"document_type": "other", "source_notes": ""})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_18_national_geographic_scope_requires_notes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"geographic_scope": "national", "source_notes": ""})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_19_non_numeric_nan_infinite_values_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "upper_threshold", "comparison_operator": "less_than", "single_threshold": "NaN", "unit": "synthetic_unit"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_20_numeric_without_units_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "upper_threshold", "comparison_operator": "less_than", "single_threshold": "123.456", "unit": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_21_single_sided_incorrectly_represented_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "upper_threshold", "comparison_operator": "less_than", "lower_bound": "123.456", "upper_bound": "789.012", "single_threshold": "", "unit": "synthetic_unit"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_22_valid_single_threshold_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "upper_threshold", "comparison_operator": "less_than", "single_threshold": "123.456", "unit": "synthetic_unit", "non_numeric_instruction": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_23_missing_interval_boundaries_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "target_interval", "comparison_operator": "between", "lower_bound": "123.456", "upper_bound": "", "unit": "synthetic_unit"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_24_lower_bound_greater_than_upper_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "target_interval", "comparison_operator": "between", "lower_bound": "789.012", "upper_bound": "123.456", "unit": "synthetic_unit", "non_numeric_instruction": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_25_qualitative_records_with_blank_numerical_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "qualitative_instruction"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_26_qualitative_with_numerical_fields_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_type": "monitoring_frequency", "single_threshold": "123.456", "unit": "synthetic_unit"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_27_not_comparable_without_reason_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparable_status": "not_comparable", "noncomparability_reason": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_28_comparable_without_group_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparable_status": "directly_comparable", "comparison_group": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_29_verified_without_metadata_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "verified"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_30_unverified_with_metadata_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "pending", "human_verified_by": "SynthUser"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_31_recs_verified_before_source_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "pending"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"verification_status": "verified", "human_verified_by": "SynthUser", "human_verification_date": "2026-08-01"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_32_invalid_another_review_needed_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"another_review_needed": "maybe"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_33_analysis_eligibility(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [
            self.get_valid_source_row({"verification_status": "verified", "human_verified_by": "Synth", "human_verification_date": "2026-08-01"})
        ])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({"recommendation_id": "REC0001", "verification_status": "pending"}),
            self.get_valid_rec_row({"recommendation_id": "REC0002", "verification_status": "verified", "human_verified_by": "Synth", "human_verification_date": "2026-08-01", "comparison_operator": "between", "lower_bound": "123.456", "upper_bound": "789.012", "unit": "synthetic_unit", "recommendation_type": "target_interval", "non_numeric_instruction": ""}),
            self.get_valid_rec_row({"recommendation_id": "REC0003", "verification_status": "excluded"}),
            self.get_valid_rec_row({"recommendation_id": "REC0004", "verification_status": "needs_revision"})
        ])
        self.write_note("EXT9999", "REC0001")
        self.write_note("EXT9999", "REC0002")
        self.write_note("EXT9999", "REC0003")
        self.write_note("EXT9999", "REC0004")

        # Test analysis file
        eligible = get_analysis_eligible_recommendations(self.recs_path)
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['recommendation_id'], 'REC0002')

    def test_34_missing_analysis_files_raise(self):
        with self.assertRaises(FileNotFoundError):
            get_analysis_eligible_recommendations(os.path.join(self.tdir.name, 'nonexistent.csv'))

        self.write_csv(self.recs_path, ["bad_header"], [])
        with self.assertRaises(ValueError):
            get_analysis_eligible_recommendations(self.recs_path)

    def test_35_testosterone_unspecified_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "serum testosterone",
            "assay_or_lab_context": "Not specified in text",
            "comparable_status": "undetermined"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

    def test_36_testosterone_unspecified_missing_measurement_name(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "",
            "assay_or_lab_context": "Not specified in text"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("measurement_name" in str(e) for e in v.errors))

    def test_37_testosterone_unspecified_missing_specificity_context(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "serum testosterone",
            "assay_or_lab_context": "",
            "unknowns": ""
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_38_testosterone_unspecified_directly_comparable_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "serum testosterone",
            "assay_or_lab_context": "Not specified in text",
            "comparable_status": "directly_comparable",
            "comparison_group": "Group 1"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_39_testosterone_unspecified_qualified_without_verification_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "serum testosterone",
            "assay_or_lab_context": "Not specified",
            "comparable_status": "comparable_with_qualification",
            "comparison_group": "Group 1",
            "noncomparability_reason": "Assay unknown",
            "verification_status": "pending"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_40_testosterone_unspecified_qualified_without_reason_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "verified", "human_verified_by": "Synth", "human_verification_date": "2026-08-01"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "analyte": "testosterone_unspecified",
            "measurement_name": "serum testosterone",
            "assay_or_lab_context": "Not specified",
            "comparable_status": "comparable_with_qualification",
            "comparison_group": "Group 1",
            "noncomparability_reason": "",
            "verification_status": "verified",
            "human_verified_by": "Synth",
            "human_verification_date": "2026-08-01"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_41_conditional_action_threshold_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "conditional_action_threshold",
            "comparison_operator": "less_than",
            "single_threshold": "400",
            "unit": "ng/dL",
            "non_numeric_instruction": "adjust dose"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

    def test_42_conditional_action_threshold_invalid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        # Invalid operator
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "conditional_action_threshold",
            "comparison_operator": "between",
            "lower_bound": "100",
            "upper_bound": "200",
            "unit": "ng/dL",
            "non_numeric_instruction": "adjust dose"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

        # Missing instruction
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "conditional_action_threshold",
            "comparison_operator": "less_than",
            "single_threshold": "400",
            "unit": "ng/dL",
            "non_numeric_instruction": ""
        })])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_43_physiologic_range_between_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "physiologic_range",
            "comparison_operator": "between",
            "lower_bound": "320",
            "upper_bound": "1000",
            "unit": "ng/dL",
            "non_numeric_instruction": "typical male range"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

    def test_44_physiologic_range_approximately_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "physiologic_range",
            "comparison_operator": "approximately",
            "lower_bound": "320",
            "upper_bound": "1000",
            "unit": "ng/dL",
            "non_numeric_instruction": "approx male range"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

    def test_45_physiologic_range_within_reference_range_nonnumeric_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "physiologic_range",
            "comparison_operator": "within_reference_range",
            "non_numeric_instruction": "normal male range"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

    def test_46_physiologic_range_with_single_threshold_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "physiologic_range",
            "comparison_operator": "approximately",
            "single_threshold": "500",
            "unit": "ng/dL",
            "non_numeric_instruction": "approx normal"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_47_physiologic_range_directly_comparable_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "physiologic_range",
            "comparison_operator": "between",
            "lower_bound": "320",
            "upper_bound": "1000",
            "unit": "ng/dL",
            "non_numeric_instruction": "typical range",
            "comparable_status": "directly_comparable",
            "comparison_group": "Group 1"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_48_existing_estradiol_total_testosterone_remains_valid(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({
                "recommendation_id": "REC0001",
                "analyte": "estradiol",
                "recommendation_type": "target_interval",
                "comparison_operator": "between",
                "lower_bound": "100",
                "upper_bound": "200",
                "unit": "pg/mL"
            }),
            self.get_valid_rec_row({
                "recommendation_id": "REC0002",
                "analyte": "total_testosterone",
                "recommendation_type": "upper_threshold",
                "comparison_operator": "less_than",
                "single_threshold": "50",
                "unit": "ng/dL"
            })
        ])
        self.write_note("EXT9999", "REC0001")
        self.write_note("EXT9999", "REC0002")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run(), "\\n".join(v.errors))

if __name__ == '__main__':
    unittest.main()
