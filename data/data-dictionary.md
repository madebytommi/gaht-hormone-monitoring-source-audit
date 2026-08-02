# Data Dictionary

## Global Data Rules

This project adheres to the research rules defined in `PROTOCOL.md`.
- **Identifiers**: Sources use `SRC####`, recommendations use `REC####`, and extraction notes use `EXT####`. Identifiers are stable and must not be reused.
- **Encoding & Formatting**: All CSV files use **UTF-8** encoding. There must be exactly one record per CSV row. Commas within fields are handled through standard CSV quoting.
- **Dates**: All dates must use the ISO format `YYYY-MM-DD`.
- **Multi-value Delimiter**: For fields that may contain multiple values (such as `upstream_source_ids`), use a semicolon `;` as a consistent delimiter.
- **Numeric Fields & Blank Values**: An intentionally blank numeric field means the value is missing or not specified; it is distinct from a literal zero. Do not substitute zero for missing data. Qualitative guidance may have all numeric fields left blank.
- **Thresholds**: Recommendations using `less_than`, `greater_than`, or similar comparative operators must use the `single_threshold` field. Do not invent lower and upper bounds to represent a single threshold.
- **Verification Workflow**: All AI-assisted records must begin with a `verification_status` of `pending`. A status of `verified` requires that `human_verified_by` and `human_verification_date` be completed explicitly by a human verifier.
- **Upstream Sources**: A blank upstream source field means only that no relationship has yet been recorded; it does not prove independence.
- **Analysis Rules**: Only `verified` records may enter analysis or visualization. Non-comparable recommendations must not be forced into shared interval comparisons.
- **Controlled Vocabularies**: Do not invent new controlled-vocabulary values that conflict with `PROTOCOL.md`. If a necessary value is undefined, the field must be documented as pending a protocol amendment.

---

## File: `data/sources.csv`

### `source_id`
* **Purpose**: Unique identifier for the source document.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Pattern `SRC####` (e.g., `SRC0001`)
* **Blank-value behavior**: Must not be blank.

### `organization`
* **Purpose**: Organization issuing the guidance document.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `document_title`
* **Purpose**: Official title of the guidance document.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `document_type`
* **Purpose**: The type of document (e.g., guideline, standard of care).
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`clinical_practice_guideline`, `standards_of_care`, `clinical_guidance`, `other`).
* **Blank-value behavior**: Must not be blank.

### `version`
* **Purpose**: Document version or edition.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if no version is explicitly stated.

### `publication_year`
* **Purpose**: Year the document was published.
* **Data type**: Integer
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `doi`
* **Purpose**: Digital Object Identifier for the source.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if no DOI is available.

### `official_url`
* **Purpose**: Permanent link or official URL to access the source.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `access_date`
* **Purpose**: Date the source was accessed for extraction.
* **Data type**: Date
* **Requirement**: Required
* **Validation notes**: Must use `YYYY-MM-DD`.
* **Blank-value behavior**: Must not be blank.

### `population_scope`
* **Purpose**: The intended population for the source.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`adults_only`, `adolescents_and_adults`, `lifespan_or_mixed_age`, `not_specified`).
* **Blank-value behavior**: Must not be blank.

### `geographic_scope`
* **Purpose**: The geographic applicability of the document.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`international`, `national`, `institutional`, `not_explicitly_stated`).
* **Blank-value behavior**: Must not be blank.

### `source_status`
* **Purpose**: Status of the document (e.g., current, superseded).
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`current_as_of_access_date`, `superseded`, `withdrawn`, `archived`, `unclear`).
* **Blank-value behavior**: Must not be blank.

### `correction_status`
* **Purpose**: Whether corrections, updates, or corrigenda have been issued and incorporated.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`not_checked`, `none_found_as_of_access_date`, `correction_found_incorporated`, `correction_found_not_incorporated`, `unclear`).
* **Blank-value behavior**: Must not be blank.

### `upstream_source_ids`
* **Purpose**: Identifiers of any known upstream sources upon which this source depends.
* **Data type**: String (delimited)
* **Requirement**: Optional
* **Validation notes**: Separate multiple values using `;`. A blank upstream source does not prove independence.
* **Blank-value behavior**: Leave blank if no relationship is recorded yet.

### `source_notes`
* **Purpose**: Additional context or notes regarding the source.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if no notes are necessary.

### `verification_status`
* **Purpose**: Status of the source metadata extraction.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`pending`, `verified`, `needs_revision`, `excluded`).
* **Blank-value behavior**: Must not be blank. AI-assisted records start as `pending`.

### `human_verified_by`
* **Purpose**: Name of the designated human verifier.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `verification_status` is `verified`).
* **Blank-value behavior**: Must be blank if unverified.

### `human_verification_date`
* **Purpose**: Date the source metadata was verified.
* **Data type**: Date
* **Requirement**: Conditionally required (Required if `verification_status` is `verified`).
* **Validation notes**: Must use `YYYY-MM-DD`.
* **Blank-value behavior**: Must be blank if unverified.

---

## File: `data/recommendations.csv`

### `recommendation_id`
* **Purpose**: Unique identifier for the extracted recommendation.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Pattern `REC####` (e.g., `REC0001`)
* **Blank-value behavior**: Must not be blank.

### `source_id`
* **Purpose**: Foreign key to `sources.csv` identifying where the recommendation came from.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Must map to a valid `SRC####`.
* **Blank-value behavior**: Must not be blank.

### `extraction_note_id`
* **Purpose**: Foreign key to the corresponding Markdown evidence note.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Pattern `EXT####` (e.g., `EXT0001`).
* **Blank-value behavior**: Must not be blank.

### `original_or_adapted`
* **Purpose**: Whether the recommendation is original to the source or references another document.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`original`, `adapted`, `reproduced`, `derived`, `unclear`, `not_applicable`).
* **Blank-value behavior**: Must not be blank.

### `upstream_source_id`
* **Purpose**: The identifier for the upstream source document if adapted or reproduced.
* **Data type**: String
* **Requirement**: Conditionally required
* **Blank-value behavior**: Leave blank if `original` or unknown. Does not prove independence.

### `section`
* **Purpose**: The document section where the recommendation is located.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if inapplicable.

### `subsection`
* **Purpose**: The document subsection where the recommendation is located.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if inapplicable.

### `table_or_figure`
* **Purpose**: The table or figure containing the recommendation.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if inapplicable.

### `page`
* **Purpose**: The page number of the recommendation.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if inapplicable.

### `paragraph_or_item`
* **Purpose**: The specific paragraph or item line.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if inapplicable.

### `age_group`
* **Purpose**: Specified age group (e.g., adult).
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`adult`, `adolescent_and_adult`, `mixed_age`, `not_specified`).
* **Blank-value behavior**: Use `not_specified` if missing.

### `therapy_direction`
* **Purpose**: Direction of hormone therapy.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`feminizing`, `masculinizing`, `general_gaht`, `not_specified`).
* **Blank-value behavior**: Must not be blank.

### `population_qualifiers`
* **Purpose**: Any additional qualitative modifiers for the population.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if none.

### `treatment_phase`
* **Purpose**: The phase of treatment the monitoring applies to.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`initiation`, `dose_adjustment`, `stable_maintenance`, `general`, `not_specified`).
* **Blank-value behavior**: Must not be blank.

### `analyte`
* **Purpose**: The hormone being measured.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`estradiol`, `total_testosterone`, `testosterone_unspecified`).
* **Validation notes**: `testosterone_unspecified` requires exact wording in `measurement_name` and either `assay_or_lab_context` or `unknowns`. It cannot be `directly_comparable`.
* **Blank-value behavior**: Must not be blank.

### `measurement_name`
* **Purpose**: Specific naming convention used by the source for the measurement.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `analyte` is `testosterone_unspecified`).
* **Blank-value behavior**: Leave blank if same as analyte.

### `unit`
* **Purpose**: The unit of measurement (e.g., pg/mL, ng/dL).
* **Data type**: String
* **Requirement**: Conditionally required (Required if numeric fields are provided).
* **Blank-value behavior**: Leave blank only for purely qualitative recommendations.

### `assay_or_lab_context`
* **Purpose**: Specific assay or laboratory instructions provided in the context.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `analyte` is `testosterone_unspecified` and `unknowns` is blank).
* **Blank-value behavior**: Leave blank if not mentioned.

### `recommendation_type`
* **Purpose**: Categorization of the instruction.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`target_interval`, `upper_threshold`, `lower_threshold`, `physiologic_range`, `laboratory_reference_range`, `monitoring_frequency`, `specimen_timing`, `qualitative_instruction`, `conditional_action_threshold`, `not_specified`).
* **Validation notes**: `target_interval` requires `between`. `upper_threshold` requires `<` or `<=`. `lower_threshold` requires `>` or `>=`. `conditional_action_threshold` requires `<, <=, >, >=`. `physiologic_range` requires `within_reference_range`, `between`, or `approximately`. `laboratory_reference_range` requires `within_reference_range`.
* **Blank-value behavior**: Must not be blank.

### `comparison_operator`
* **Purpose**: Operator relating the threshold or interval.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`less_than`, `less_than_or_equal`, `greater_than`, `greater_than_or_equal`, `between`, `within_reference_range`, `approximately`, `not_applicable`, `not_specified`).
* **Validation notes**: `between` requires bounds, no single threshold. Single-sided (`<, <=, >, >=`) requires single threshold, no bounds. `approximately` requires either single threshold OR bounds. `within_reference_range`, `not_applicable`, and `not_specified` prohibit numeric fields.
* **Blank-value behavior**: Must not be blank.

### `lower_bound`
* **Purpose**: Lower numerical boundary of an interval.
* **Data type**: Decimal
* **Requirement**: Conditionally required (Required for `target_interval`, `between`, and `approximately` if bounds used).
* **Validation notes**: Prohibited for single-sided operators, `within_reference_range`, and `conditional_action_threshold`.
* **Blank-value behavior**: Leave blank if inapplicable or not specified. Do not substitute zero.

### `upper_bound`
* **Purpose**: Upper numerical boundary of an interval.
* **Data type**: Decimal
* **Requirement**: Conditionally required (Required for `target_interval`, `between`, and `approximately` if bounds used).
* **Validation notes**: Prohibited for single-sided operators, `within_reference_range`, and `conditional_action_threshold`.
* **Blank-value behavior**: Leave blank if inapplicable or not specified. Do not substitute zero.

### `single_threshold`
* **Purpose**: Numerical boundary for single-sided operators.
* **Data type**: Decimal
* **Requirement**: Conditionally required (Required for `<, <=, >, >=`, and `conditional_action_threshold`).
* **Validation notes**: Prohibited for `between`, `within_reference_range`, and `physiologic_range`.
* **Blank-value behavior**: Leave blank if inapplicable or not specified. Do not invent bounds for single thresholds.

### `non_numeric_instruction`
* **Purpose**: Descriptive text for qualitative or non-numeric guidance.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `recommendation_type` is `qualitative_instruction`, `physiologic_range`, `laboratory_reference_range`, `monitoring_frequency`, `specimen_timing`, or `conditional_action_threshold`).
* **Blank-value behavior**: Leave blank if inapplicable.

### `route`
* **Purpose**: Route of administration context for the recommendation.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if missing (use `not_specified` if explicitly addressed but unresolved).

### `formulation`
* **Purpose**: Medication formulation context.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if missing.

### `dosing_interval`
* **Purpose**: Dosing frequency context.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if missing.

### `specimen_timing`
* **Purpose**: Timing of specimen collection relative to dosage.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`peak`, `trough`, `mid_cycle`, `before_next_dose`, `after_application`, `any_time`, `route_specific`, `not_specified`).
* **Blank-value behavior**: Must not be blank. Use `not_specified` if missing.

### `time_since_dose_or_application`
* **Purpose**: Specific numeric or textual timing offset if provided.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if not mentioned.

### `short_source_excerpt`
* **Purpose**: Brief verbatim text documenting the extraction.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `faithful_paraphrase`
* **Purpose**: Neutral interpretation without added assumptions.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `required_context`
* **Purpose**: Essential context from the surrounding text.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `unknowns`
* **Purpose**: Record of absent, unclear, conflicting, or unresolved information.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank if no unknowns exist.

### `claims_not_supported`
* **Purpose**: Explicitly warns against tempting interpretations.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `comparison_group`
* **Purpose**: Group ID or category for comparability assessment.
* **Data type**: String
* **Requirement**: Optional
* **Blank-value behavior**: Leave blank until comparability is assessed.

### `comparable_status`
* **Purpose**: Assessment of whether this can be safely compared to other records.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`directly_comparable`, `comparable_with_qualification`, `not_comparable`, `undetermined`).
* **Validation notes**: Non-comparable recommendations must not be forced into shared interval comparisons. `testosterone_unspecified` cannot be `directly_comparable` and may only be `comparable_with_qualification` if verified and a reason is given. `physiologic_range` cannot be marked `directly_comparable` (Amendment 0.3 limitation).
* **Blank-value behavior**: Must not be blank. Starts as `undetermined`.

### `noncomparability_reason`
* **Purpose**: Reason if not directly comparable.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `comparable_status` is `comparable_with_qualification` for `testosterone_unspecified`).
* **Blank-value behavior**: Leave blank if directly comparable.

### `extracted_by`
* **Purpose**: Identifier for the person or system that drafted the extraction.
* **Data type**: String
* **Requirement**: Required
* **Blank-value behavior**: Must not be blank.

### `extraction_date`
* **Purpose**: Date the extraction was initially drafted.
* **Data type**: Date
* **Requirement**: Required
* **Validation notes**: Must use `YYYY-MM-DD`.
* **Blank-value behavior**: Must not be blank.

### `verification_status`
* **Purpose**: Status of the extracted record against the source text.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`pending`, `verified`, `needs_revision`, `excluded`).
* **Blank-value behavior**: Must not be blank. AI-assisted records start as `pending`.

### `human_verified_by`
* **Purpose**: Name of the designated human verifier.
* **Data type**: String
* **Requirement**: Conditionally required (Required if `verification_status` is `verified`).
* **Blank-value behavior**: Must be blank if unverified.

### `human_verification_date`
* **Purpose**: Date the recommendation record was verified.
* **Data type**: Date
* **Requirement**: Conditionally required (Required if `verification_status` is `verified`).
* **Validation notes**: Must use `YYYY-MM-DD`.
* **Blank-value behavior**: Must be blank if unverified.

### `another_review_needed`
* **Purpose**: Flag indicating if further review or dispute resolution is required.
* **Data type**: String
* **Requirement**: Required
* **Controlled values**: Already defined in `PROTOCOL.md` (`yes`, `no`).
* **Blank-value behavior**: Must not be blank.
