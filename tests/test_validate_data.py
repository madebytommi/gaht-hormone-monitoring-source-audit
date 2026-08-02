import unittest
import tempfile
import os
import csv
from scripts.validate_data import Validator, SOURCES_HEADER, RECOMMENDATIONS_HEADER, get_analysis_eligible_recommendations

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

    def write_note(self, ext_id, rec_id):
        path = os.path.join(self.ev_dir, f"{ext_id}.md")
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
            "organization": "Test Org",
            "document_title": "Test Title",
            "document_type": "clinical_guidance",
            "version": "1.0",
            "publication_year": "2026",
            "doi": "",
            "official_url": "http://test",
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
            "section": "Sec 1",
            "subsection": "",
            "table_or_figure": "",
            "page": "1",
            "paragraph_or_item": "1",
            "age_group": "adult",
            "therapy_direction": "feminizing",
            "population_qualifiers": "",
            "treatment_phase": "general",
            "analyte": "estradiol",
            "measurement_name": "E2",
            "unit": "",
            "assay_or_lab_context": "",
            "recommendation_type": "qualitative_instruction",
            "comparison_operator": "not_applicable",
            "lower_bound": "",
            "upper_bound": "",
            "single_threshold": "",
            "non_numeric_instruction": "Test instruction",
            "route": "",
            "formulation": "",
            "dosing_interval": "",
            "specimen_timing": "not_specified",
            "time_since_dose_or_application": "",
            "short_source_excerpt": "Test excerpt",
            "faithful_paraphrase": "Test paraphrase",
            "required_context": "",
            "unknowns": "",
            "claims_not_supported": "",
            "comparison_group": "",
            "comparable_status": "undetermined",
            "noncomparability_reason": "",
            "extracted_by": "TestUser",
            "extraction_date": "2026-08-01",
            "verification_status": "pending",
            "human_verified_by": "",
            "human_verification_date": "",
            "another_review_needed": "no"
        }
        if overrides: row.update(overrides)
        return [row[h] for h in RECOMMENDATIONS_HEADER]

    def test_1_current_header_only_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())
        self.assertEqual(len(v.errors), 0)

    def test_2_incorrect_source_header_fails(self):
        self.write_csv(self.sources_path, ["wrong_header"], [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_3_incorrect_rec_header_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, ["wrong_header"], [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_4_invalid_and_duplicate_ids_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [
            self.get_valid_source_row({"source_id": "BAD999"}),
            self.get_valid_source_row({"source_id": "SRC9999"}),
            self.get_valid_source_row({"source_id": "SRC9999"})
        ])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        err_str = " ".join(v.errors)
        self.assertIn("Invalid format", err_str)
        self.assertIn("Duplicate ID", err_str)

    def test_5_invalid_vocab_values_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"document_type": "invalid_type"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_6_invalid_dates_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"access_date": "08-01-2026"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_7_missing_source_foreign_keys_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"source_id": "SRC9999"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertIn("Foreign key missing", str(v.errors))

    def test_8_missing_evidence_note_files_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        # Do not create note
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertIn("Evidence note missing", str(v.errors))

    def test_9_mismatched_evidence_note_ids_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        self.write_note("EXT9999", "REC0000") # mismatched rec id
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertIn("missing correct Recommendation ID", str(v.errors))

    def test_10_adapted_without_upstream_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"original_or_adapted": "adapted", "upstream_source_id": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Required when original_or_adapted is adapted" in e for e in v.errors))

    def test_11_original_with_upstream_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row(), self.get_valid_source_row({"source_id":"SRC8888"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"original_or_adapted": "original", "upstream_source_id": "SRC8888"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Must be blank" in e for e in v.errors))

    def test_12_numeric_without_units_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparison_operator": "less_than", "single_threshold": "100", "unit": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("unit" in e and "Required when numeric" in e for e in v.errors))

    def test_13_less_than_represented_with_bounds_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparison_operator": "less_than", "lower_bound": "0", "upper_bound": "100", "unit": "pg/mL", "single_threshold": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_14_valid_single_threshold_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparison_operator": "less_than", "single_threshold": "100", "unit": "pg/mL", "recommendation_type": "upper_threshold", "non_numeric_instruction": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_15_target_intervals_missing_boundary_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparison_operator": "between", "lower_bound": "100", "upper_bound": "", "unit": "pg/mL", "recommendation_type": "target_interval"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_16_qualitative_guidance_with_blank_numeric_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_17_qualitative_guidance_with_invented_bounds_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparison_operator": "not_applicable", "lower_bound": "100", "unit": "pg/mL"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_18_not_comparable_without_reason_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"comparable_status": "not_comparable", "noncomparability_reason": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_19_verified_records_without_metadata_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "verified"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_20_unverified_records_with_metadata_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "pending", "human_verified_by": "TestUser"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_21_rec_verified_before_source_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"verification_status": "pending"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"verification_status": "verified", "human_verified_by": "TestUser", "human_verification_date": "2026-08-01"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_22_another_review_needed_vocab(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"another_review_needed": "maybe"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_23_pending_records_excluded_from_analysis(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({"recommendation_id": "REC0001", "verification_status": "pending"}),
            self.get_valid_rec_row({"recommendation_id": "REC0002", "verification_status": "verified", "human_verified_by": "User", "human_verification_date": "2026-08-01"})
        ])
        eligible = get_analysis_eligible_recommendations(self.recs_path)
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['recommendation_id'], "REC0002")

    def test_24_complete_synthetic_verified_record_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [
            self.get_valid_source_row({"verification_status": "verified", "human_verified_by": "User", "human_verification_date": "2026-08-01"})
        ])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({"verification_status": "verified", "human_verified_by": "User", "human_verification_date": "2026-08-01", "comparison_operator": "between", "lower_bound": "100", "upper_bound": "200", "unit": "pg/mL", "recommendation_type": "target_interval"})
        ])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        res = v.run()
        if not res:
            print("Errors in test 24:", v.errors)
        self.assertTrue(res)

if __name__ == '__main__':
    unittest.main()
