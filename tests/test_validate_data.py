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
        # All values are synthetic and non-clinical.
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
        # All values are synthetic and non-clinical.
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

    def test_1_current_header_only_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())
        self.assertEqual(len(v.errors), 0)
        
    def test_2_incorrect_headers_fail(self):
        self.write_csv(self.sources_path, ["wrong_header"], [])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        
        self.write_csv(self.sources_path, SOURCES_HEADER, [])
        self.write_csv(self.recs_path, ["wrong_header"], [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())

    def test_3_blank_required_source_fields_fail(self):
        # Blank org
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"organization": ""})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("organization" in e and "blank" in e for e in v.errors))

    def test_4_blank_required_rec_fields_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"short_source_excerpt": ""})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("short_source_excerpt" in e and "blank" in e for e in v.errors))

    def test_5_extraction_date_validation(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        # malformed
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"extraction_date": "08-01-2026"})])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("extraction_date" in e and "Invalid date format" in e for e in v.errors))
        
        # blank
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"extraction_date": ""})])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("extraction_date" in e and "Cannot be blank" in e for e in v.errors))

    def test_6_whitespace_only_required_values_fail(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"document_title": "   "})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [])
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("document_title" in e and "Cannot be blank" in e for e in v.errors))

    def test_7_qualitative_instruction_between_with_bounds_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        # Type qualitative, but uses between and has bounds.
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "qualitative_instruction", 
            "comparison_operator": "between", 
            "lower_bound": "1", 
            "upper_bound": "2", 
            "unit": "pg/mL"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("numeric fields must be blank for qualitative_instruction" in e for e in v.errors))

    def test_8_monitoring_frequency_with_numeric_fields_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "monitoring_frequency", 
            "comparison_operator": "not_applicable", 
            "single_threshold": "100", 
            "unit": "pg/mL"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("numeric fields must be blank for monitoring_frequency" in e for e in v.errors))

    def test_9_not_specified_rec_with_numeric_fails(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({
            "recommendation_type": "not_specified", 
            "comparison_operator": "less_than", 
            "single_threshold": "50", 
            "unit": "pg/mL"
        })])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("numeric fields must be blank for not_specified" in e for e in v.errors))

    def test_10_exact_evidence_note_title_required(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        content = """# Wrong Title
## Recommendation
Recommendation ID: REC9999
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
        self.write_note("EXT9999", "REC9999", content)
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("title on first line" in e for e in v.errors))

    def test_11_evidence_note_headings(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        
        # Missing heading
        content_missing = """# Extraction Note: EXT9999
## Recommendation
Recommendation ID: REC9999
## Source
## Exact Location
## Supporting Excerpt
## Faithful Paraphrase
## Required Context
## Source Relationship
## Comparability Assessment
## Unknowns or Ambiguities
## Verification
"""
        self.write_note("EXT9999", "REC9999", content_missing)
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("missing section: ## Claims This Source Does Not Support" in e for e in v.errors))
        
        # Duplicate heading
        content_dup = """# Extraction Note: EXT9999
## Recommendation
Recommendation ID: REC9999
## Recommendation
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
        self.write_note("EXT9999", "REC9999", content_dup)
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("Duplicate heading" in e for e in v.errors))
        
        # Out of order
        content_order = """# Extraction Note: EXT9999
## Source
## Recommendation
Recommendation ID: REC9999
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
        self.write_note("EXT9999", "REC9999", content_order)
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("out of order" in e for e in v.errors))
        
        # Rec ID outside section
        content_outside = """# Extraction Note: EXT9999
## Recommendation
## Source
Recommendation ID: REC9999
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
        self.write_note("EXT9999", "REC9999", content_outside)
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        self.assertTrue(any("missing correct Recommendation ID within ## Recommendation section" in e for e in v.errors))

    def test_12_analysis_eligibility_errors(self):
        # Missing file
        with self.assertRaises(FileNotFoundError):
            get_analysis_eligible_recommendations(os.path.join(self.tdir.name, 'nonexistent.csv'))
            
        # Malformed header
        self.write_csv(self.recs_path, ["bad_header"], [])
        with self.assertRaises(ValueError):
            get_analysis_eligible_recommendations(self.recs_path)
            
        # Malformed row length
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [["just one val"]])
        with self.assertRaises(ValueError):
            get_analysis_eligible_recommendations(self.recs_path)

    def test_13_error_messages_contain_ids(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row({"source_id": "SRC1234", "document_type": "invalid"})])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row({"recommendation_id": "REC5678", "therapy_direction": "invalid"})])
        self.write_note("EXT9999", "REC5678")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertFalse(v.run())
        err_str = " ".join(v.errors)
        self.assertIn("SRC1234", err_str)
        self.assertIn("REC5678", err_str)

    def test_14_fully_populated_synthetic_pending_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [self.get_valid_source_row()])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [self.get_valid_rec_row()])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_15_fully_populated_synthetic_verified_passes(self):
        self.write_csv(self.sources_path, SOURCES_HEADER, [
            self.get_valid_source_row({"verification_status": "verified", "human_verified_by": "User", "human_verification_date": "2026-08-01"})
        ])
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({
                "verification_status": "verified", "human_verified_by": "User", "human_verification_date": "2026-08-01", 
                "comparison_operator": "between", "lower_bound": "100", "upper_bound": "200", "unit": "pg/mL", 
                "recommendation_type": "target_interval"
            })
        ])
        self.write_note("EXT9999", "REC9999")
        v = Validator(self.sources_path, self.recs_path, self.ev_dir)
        self.assertTrue(v.run())

    def test_16_analysis_eligibility_returns_verified(self):
        self.write_csv(self.recs_path, RECOMMENDATIONS_HEADER, [
            self.get_valid_rec_row({"recommendation_id": "REC0001", "verification_status": "pending"}),
            self.get_valid_rec_row({"recommendation_id": "REC0002", "verification_status": "verified"})
        ])
        eligible = get_analysis_eligible_recommendations(self.recs_path)
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['recommendation_id'], 'REC0002')

if __name__ == '__main__':
    unittest.main()
