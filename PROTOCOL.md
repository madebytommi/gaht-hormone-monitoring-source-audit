# Research Protocol

## Serum Hormone Monitoring Recommendations in Selected GAHT Guidance Documents: A Reproducible Source Audit

**Protocol status:** Draft
**Project status:** Source verification not yet begun
**Intended use:** Research methodology and reproducibility
**Clinical use:** Prohibited
**Protocol owner and human verifier:** Tommi
**Last updated:** 2026-08-02

---

## 1. Status Notice

This repository is an early research scaffold.

No clinical findings, recommended hormone ranges, consensus conclusions, or comparative results have yet been established. Nothing in this repository may be used for diagnosis, treatment, medication adjustment, laboratory interpretation, or other clinical decision-making.

No source recommendation may be included in an analysis or visualization until it has been traced to an official source, extracted with its required context, and explicitly marked as human verified.

---

## 2. Project Purpose

This project will conduct a reproducible documentary audit of how selected gender-affirming hormone therapy guidance documents describe serum estradiol and testosterone monitoring recommendations for adults.

The project will preserve the context surrounding each recommendation rather than reducing all guidance to simple numerical ranges.

The project will examine:

* What each document explicitly recommends
* Whether a recommendation is numerical, qualitative, or laboratory-dependent
* Whether a value is a therapeutic target, threshold, reference interval, safety ceiling, or another type of instruction
* Which treatment route or formulation the recommendation concerns
* When a specimen should be collected relative to treatment administration
* Which population and treatment phase the recommendation applies to
* Whether the recommendation originated in the document or was adapted from another source
* Whether recommendations from different documents are genuinely comparable

This project will not determine which hormone concentration is medically correct for an individual patient.

---

## 3. Primary Research Question

**How do selected gender-affirming hormone therapy guidance documents specify and contextualize serum estradiol and testosterone monitoring recommendations for adults, including recommendation type, numerical threshold or interval, route or formulation, specimen timing, intended population, and relationship to upstream sources?**

---

## 4. Secondary Research Questions

1. Which recommendations are stated directly by each document?

2. Which recommendations are adapted, reproduced, or derived from another guidance document?

3. Does each recommendation describe a therapeutic target, upper threshold, lower threshold, physiologic range, laboratory reference range, monitoring frequency, or qualitative instruction?

4. Which recommendations can be directly compared without removing clinically important context?

5. Which recommendations are comparable only with qualifications?

6. Which recommendations cannot be responsibly compared?

7. How do the documents address route of administration, formulation, dosing interval, treatment phase, and specimen timing?

8. How often do documents direct readers to use local laboratory reference ranges or individualized treatment goals rather than a universal numerical interval?

9. Where are recommendations ambiguous, incomplete, internally inconsistent, or dependent on another source?

---

## 5. Study Design

This project is a comparative documentary source audit.

It is not currently designed as:

* A systematic review
* A scoping review
* A meta-analysis
* A clinical trial
* A patient-level observational study
* A clinical decision-support system
* A treatment guideline
* A consensus-development exercise

The project examines a predefined group of guidance documents and records their recommendations in a structured, auditable format.

Any future expansion into a systematic or scoping review would require a separate protocol amendment, formal search strategy, eligibility process, and reporting framework.

---

## 6. Initial Source Set

The initial candidate source set consists of:

1. Endocrine Society clinical guidance published in 2017
2. World Professional Association for Transgender Health Standards of Care, Version 8, published in 2022
3. University of California, San Francisco transgender-care guidance

The complete official titles, versions, publication details, permanent links, corrections, and access dates must be recorded in `data/sources.csv`.

A source is not considered verified merely because its organization and year are known.

---

## 7. Source Eligibility Criteria

A document may be included when it:

* Is issued by the organization named in the source record
* Is available through an official publisher, organizational website, or authoritative repository
* Contains adult GAHT monitoring guidance relevant to serum estradiol or testosterone
* Provides sufficient source location information for extraction
* Can be examined without relying exclusively on a secondary summary
* Has its version, publication year, and correction status established

A document may include adolescents and adults, but only adult-specific recommendations may be treated as adult recommendations.

Mixed-population recommendations must be labeled as mixed and must not be silently reclassified as adult-only.

---

## 8. Source Exclusion Criteria

A document must not be treated as a primary included guidance document when it is:

* A news article
* A patient forum post
* An unsourced webpage
* A commercial laboratory advertisement
* A general search-result summary
* An AI-generated summary
* A secondary article that merely describes another guideline
* A superseded version used without an explicit historical reason
* A document whose authenticity or version cannot be established

Secondary materials may help locate an official source but may not replace verification against that source.

---

## 9. Scope Boundaries

### 9.1 Population

The primary population is adults receiving or considering gender-affirming hormone therapy.

Recommendations limited to pediatric or adolescent care are outside the primary analysis unless retained only to explain why they were excluded.

### 9.2 Analytes

The initial analysis is limited to:

* Serum estradiol
* Serum total testosterone

Free testosterone, sex hormone-binding globulin, estrone, gonadotropins, prolactin, hematocrit, liver markers, lipids, and other laboratory measures are outside the initial scope unless needed to explain the context of an included estradiol or testosterone recommendation.

Adding another analyte requires a documented protocol amendment.

### 9.3 Therapy Directions

The initial analysis includes:

* Feminizing hormone therapy
* Masculinizing hormone therapy

Recommendations must not be assumed to apply to nonbinary, individualized, or partial-feminization or partial-masculinization goals unless the source explicitly says so.

### 9.4 Recommendation Types

The project may include:

* Numerical target intervals
* Upper thresholds
* Lower thresholds
* Physiologic-range instructions
* Laboratory-reference-range instructions
* Monitoring-frequency recommendations
* Specimen-timing instructions
* Qualitative monitoring recommendations

A recommendation does not need to contain a numerical value to be eligible.

---

## 10. Claims This Project Will Not Make

The project will not:

* Propose a new therapeutic hormone range
* Average boundaries from multiple guidelines
* Create a synthetic consensus interval
* Present the union of several intervals as consensus
* Treat the intersection of several intervals as a new clinical recommendation
* Rank documents by medical correctness
* Treat organizations as statistically independent observations
* Treat repeated recommendations as independent evidence
* Claim that numerical agreement proves strong evidence
* Claim that numerical disagreement proves clinical conflict
* Infer an unspecified lower or upper boundary
* Convert “less than” into an interval beginning at zero
* Convert “within the physiologic range” into a fixed interval without an explicitly cited source
* Offer patient-specific interpretation
* Recommend medication or dosing changes
* Market the repository as a clinical tool

---

## 11. Unit of Extraction

The unit of extraction is one distinct recommendation or monitoring instruction.

A separate record must be created when recommendations differ by:

* Analyte
* Therapy direction
* Route
* Formulation
* Dosing schedule
* Specimen timing
* Treatment phase
* Population
* Comparison operator
* Recommendation type
* Source location
* Upstream source relationship

Multiple values must not be combined into one record merely because they appear in the same table.

---

## 12. Identifier System

Sources will use stable identifiers:

* `SRC0001`
* `SRC0002`
* `SRC0003`

Recommendations will use stable identifiers:

* `REC0001`
* `REC0002`
* `REC0003`

Extraction notes will use stable identifiers:

* `EXT0001`
* `EXT0002`
* `EXT0003`

Identifiers must never be reused after a record is deleted or excluded.

Renumbering existing records is prohibited once they have been committed.

---

## 13. Repository Data Structure

The planned public structure is:

```text
.
├── PROTOCOL.md
├── README.md
├── LICENSE
├── data/
│   ├── sources.csv
│   ├── recommendations.csv
│   └── data-dictionary.md
├── extraction/
│   └── evidence-notes/
│       ├── EXT0001.md
│       ├── EXT0002.md
│       └── EXT0003.md
├── scripts/
│   └── analyze_recommendations.py
└── tests/
    └── test_analysis.py
```

Files and folders may be added only when they serve the protocol.

No visualization is required until verified data support one.

---

## 14. Source-Level Data

Each row in `data/sources.csv` must include:

* `source_id`
* `organization`
* `document_title`
* `document_type`
* `version`
* `publication_year`
* `doi`
* `official_url`
* `access_date`
* `population_scope`
* `geographic_scope`
* `source_status`
* `correction_status`
* `upstream_source_ids`
* `source_notes`
* `verification_status`
* `human_verified_by`
* `human_verification_date`

The `upstream_source_ids` field must record known source dependencies.

An empty upstream-source field means only that no relationship has yet been recorded. It must not automatically be interpreted as proof of independence.

---

## 15. Recommendation-Level Data

Each row in `data/recommendations.csv` must include:

### Identity and provenance

* `recommendation_id`
* `source_id`
* `extraction_note_id`
* `original_or_adapted`
* `upstream_source_id`

### Source location

* `section`
* `subsection`
* `table_or_figure`
* `page`
* `paragraph_or_item`

### Population and treatment

* `age_group`
* `therapy_direction`
* `population_qualifiers`
* `treatment_phase`

### Measurement

* `analyte`
* `measurement_name`
* `unit`
* `assay_or_lab_context`

### Recommendation structure

* `recommendation_type`
* `comparison_operator`
* `lower_bound`
* `upper_bound`
* `single_threshold`
* `non_numeric_instruction`

### Treatment context

* `route`
* `formulation`
* `dosing_interval`

### Specimen context

* `specimen_timing`
* `time_since_dose_or_application`

### Evidence record

* `short_source_excerpt`
* `faithful_paraphrase`
* `required_context`
* `unknowns`
* `claims_not_supported`

### Comparability

* `comparison_group`
* `comparable_status`
* `noncomparability_reason`

### Verification

* `extracted_by`
* `extraction_date`
* `verification_status`
* `human_verified_by`
* `human_verification_date`
* `another_review_needed`

---

## 16. Controlled Vocabulary

### 16.1 Verification status

Permitted values:

* `pending`
* `verified`
* `needs_revision`
* `excluded`

Only `verified` recommendations may enter an analysis or visualization.

### 16.2 Recommendation type

Permitted values:

* `target_interval`
* `upper_threshold`
* `lower_threshold`
* `physiologic_range`
* `laboratory_reference_range`
* `monitoring_frequency`
* `specimen_timing`
* `qualitative_instruction`
* `not_specified`

### 16.3 Comparison operator

Permitted values:

* `less_than`
* `less_than_or_equal`
* `greater_than`
* `greater_than_or_equal`
* `between`
* `within_reference_range`
* `approximately`
* `not_applicable`
* `not_specified`

An operator must reflect the source language. It must not be inferred merely to make plotting easier.

### 16.4 Original or adapted

Permitted values:

* `original`
* `adapted`
* `reproduced`
* `derived`
* `unclear`
* `not_applicable`

### 16.5 Comparability status

Permitted values:

* `directly_comparable`
* `comparable_with_qualification`
* `not_comparable`
* `undetermined`

### 16.6 Treatment phase

Permitted values:

* `initiation`
* `dose_adjustment`
* `stable_maintenance`
* `general`
* `not_specified`

### 16.7 Specimen timing

Permitted values may include:

* `peak`
* `trough`
* `mid_cycle`
* `before_next_dose`
* `after_application`
* `any_time`
* `route_specific`
* `not_specified`

The exact source wording must still be preserved in the evidence note.

---

## 17. Evidence Notes

Every recommendation must have a corresponding Markdown evidence note under `extraction/evidence-notes/`.

Each evidence note must contain:

```text
# Extraction Note: EXT####

## Recommendation

Recommendation ID:

## Source

Source ID:
Organization:
Document title:
Version:
Publication year:
Official source:
Access date:

## Exact Location

Section:
Subsection:
Table or figure:
Page:
Paragraph or item:

## Supporting Excerpt

[Insert a short excerpt sufficient to support the extraction.]

## Faithful Paraphrase

[Describe what the source says without adding interpretation.]

## Required Context

- Population:
- Therapy direction:
- Analyte:
- Route:
- Formulation:
- Dosing interval:
- Specimen timing:
- Treatment phase:
- Unit:
- Comparison operator:

## Source Relationship

Original, adapted, reproduced, derived, or unclear:
Upstream source:
Evidence supporting this classification:

## Comparability Assessment

Comparison group:
Comparability status:
Reason:

## Unknowns or Ambiguities

[Record information that is absent, unclear, conflicting, or unresolved.]

## Claims This Source Does Not Support

[Explicitly state tempting interpretations that must not be made.]

## Verification

Extracted by:
Extraction date:
Verification status:
Human verified by:
Human verification date:
Another review needed:
Verification notes:
```

Only short excerpts needed to document the extraction may be included. Full copyrighted guidance documents must not be copied into the repository.

---

## 18. Extraction Workflow

Each source must proceed through the following sequence:

1. Identify the authoritative version.
2. Record the complete source metadata.
3. Check for corrections, updates, or corrigenda.
4. Identify all relevant adult estradiol and testosterone monitoring passages.
5. Create one recommendation record per distinct instruction.
6. Create a supporting evidence note for every record.
7. Record route, formulation, timing, population, and treatment phase exactly when available.
8. Mark missing information as `not_specified` rather than guessing.
9. Record whether the recommendation appears original or dependent on another document.
10. Assess comparability only after the contextual extraction is complete.
11. Leave the record as `pending`.
12. Conduct human verification against the source.
13. Correct any discrepancy.
14. Mark the record `verified` only after explicit human approval.

Sources should be completed one at a time.

The initial planned order is:

1. Endocrine Society
2. WPATH SOC 8
3. UCSF

Completing the first source includes verifying all in-scope recommendations from that source before beginning comparative analysis.

---

## 19. Human Verification

Human verification is required for:

* Source identity
* Document version
* Source location
* Numerical values
* Units
* Comparison operators
* Route
* Formulation
* Specimen timing
* Population
* Treatment phase
* Recommendation type
* Source-dependency classification
* Comparability classification
* Faithful paraphrase
* Claims-not-supported field

AI output alone cannot satisfy human verification.

The human verifier must compare each record directly against the authoritative document and explicitly approve or return it for revision.

The designated verifier for the initial project is Tommi.

---

## 20. Permitted Use of AI

AI tools may assist with:

* Locating candidate passages
* Creating draft extraction records
* Formatting source metadata
* Identifying possible ambiguities
* Suggesting controlled-vocabulary values
* Checking internal consistency
* Writing validation code
* Drafting documentation

AI tools may not:

* Invent missing values
* Convert qualitative language into a numerical range
* Mark a record human verified
* Decide that two recommendations are clinically equivalent without documented reasoning
* Add a lower or upper boundary not stated by the source
* Replace the authoritative source
* Generate clinical advice
* Claim that code was executed unless it was actually executed
* Claim that a source was checked unless the source was actually accessed

All AI-generated extractions must initially be marked `pending`.

---

## 21. Handling Missing or Ambiguous Information

When a source does not specify a field:

* Use the controlled value `not_specified` when available.
* Leave numerical fields empty.
* Explain the missing context in `unknowns`.
* Do not infer a value from another source.
* Do not substitute a common laboratory interval.
* Do not convert qualitative guidance into a precise number.
* Do not exclude the recommendation merely because it cannot be plotted.

When two passages appear inconsistent:

* Preserve both passages as separate records when appropriate.
* Document the conflict.
* Check for corrections or version differences.
* Require another review.
* Do not silently reconcile them.

---

## 22. Source-Dependency Rules

Documents must not automatically be treated as independent evidence.

For every recommendation, the project must assess whether it is:

* Original to the source
* Adapted from another source
* Reproduced from another source
* Derived from another source
* Unclear in origin

When a source explicitly credits another document, that relationship must be recorded.

Repeated recommendations may be compared as documentary statements, but they must not be counted as multiple independent confirmations of the underlying clinical evidence.

---

## 23. Comparability Rules

Two recommendations may be marked `directly_comparable` only when all materially relevant dimensions align, including:

* Analyte
* Unit
* Therapy direction
* Population
* Recommendation type
* Route or applicable route scope
* Formulation or applicable formulation scope
* Specimen timing
* Treatment phase
* Meaning of the numerical value

Recommendations may be marked `comparable_with_qualification` when differences are understood and can be explicitly preserved.

Recommendations must be marked `not_comparable` when comparison would require removing or inventing important context.

Visual similarity alone does not establish comparability.

---

## 24. Analysis Plan

The initial analysis will be descriptive.

Permitted outputs may include:

* Counts of recommendations by source
* Counts by recommendation type
* Counts by analyte
* Counts with and without specified specimen timing
* Counts with and without route-specific context
* Counts classified as original, adapted, reproduced, derived, or unclear
* Counts by comparability status
* Tables displaying verified recommendations and their contexts
* Source-dependency maps
* Narrative comparisons

The analysis must not calculate:

* Mean lower boundaries
* Mean upper boundaries
* Pooled therapeutic intervals
* Statistical variance across guideline boundaries
* A synthetic consensus range
* A clinical recommendation score

No inferential statistics are planned.

---

## 25. Visualization Rules

A visualization may be generated only when:

* Every included record is marked `verified`.
* Each value has a documented source location.
* The recommendation type is represented accurately.
* Required route and specimen-timing context is visible or clearly linked.
* Adapted or reproduced recommendations are identified.
* Non-comparable values are not presented as though they were directly comparable.
* Qualitative recommendations are not forced into numeric intervals.
* The caption explains the limitations of the visualization.
* The graphic is clearly labeled as a documentary comparison rather than clinical guidance.

The script must refuse to generate a chart when:

* Any selected record remains pending.
* Required context is missing.
* A lower or upper boundary was inferred.
* Units are incompatible.
* Records marked `not_comparable` are requested as a shared numerical comparison.
* The source-extraction file fails validation.

---

## 26. Software Requirements

The analysis script must:

* Read data from tracked source files rather than hardcoded clinical tuples
* Validate required fields
* Use only verified records
* Preserve comparison operators
* Distinguish thresholds from intervals
* Handle missing numeric values
* Produce clear error messages
* Exit nonzero when validation fails
* Avoid generating misleading output
* Be covered by tests for the primary validation rules

Tests must include at least:

* Rejection of pending records
* Rejection of invented interval boundaries
* Correct handling of `less_than`
* Correct handling of qualitative recommendations
* Rejection of incompatible units
* Rejection of non-comparable records in interval plots
* Acceptance of a complete verified record

---

## 27. Quality-Control Checks

Before analysis, confirm:

* Every recommendation references a valid source ID.
* Every recommendation references an evidence note.
* Every verified recommendation has a human verifier and date.
* Numerical records contain units.
* Thresholds are not represented as closed intervals.
* Missing values have not been replaced with zero.
* Adapted recommendations identify an upstream source when known.
* Comparable records share the necessary contextual dimensions.
* The README does not overstate the project’s status.
* No clinical recommendation is presented as originating from this project.

---

## 28. Change Control

Changes to formatting, spelling, code organization, or documentation do not necessarily require a protocol amendment.

A documented protocol amendment is required when changing:

* The primary research question
* The source set
* Population scope
* Included analytes
* Therapy-direction scope
* Eligibility criteria
* Extraction fields
* Comparability rules
* Analysis methods
* Visualization eligibility
* Release criteria

Protocol amendments must include:

* Date
* Description
* Reason
* Expected effect on existing records
* Whether prior extraction requires re-review
* Human approval

Material changes must not be applied retroactively without documentation.

---

## 29. Ethical and Safety Considerations

This project uses public guidance documents and does not collect patient-level data.

The repository must not contain:

* Private health information
* Patient records
* Identifying medical information
* Individual laboratory results
* Personalized treatment recommendations
* Instructions to alter medication
* Full copyrighted guideline documents

The project concerns clinically sensitive information. Language must be calibrated to avoid implying that documentary comparison can replace individualized care.

The repository must always include a visible statement that it is not a clinical decision-making tool.

---

## 30. Anticipated Limitations

Expected limitations include:

* The initial source set is selected rather than comprehensive.
* Included documents may differ in purpose, audience, and development process.
* Some documents may draw from the same upstream evidence or guidance.
* Recommendations may not be independent.
* Numerical values may depend on route, formulation, assay, laboratory, timing, or treatment goals.
* Some recommendations may be qualitative and unsuitable for interval plotting.
* The audit will describe documents but will not establish clinical effectiveness or safety.
* Human verification reduces but does not eliminate interpretation error.

These limitations must be preserved in future reports and releases.

---

## 31. Completion Criteria

The source-audit phase is complete only when:

* All included sources have verified metadata.
* All in-scope recommendations have been extracted.
* Each recommendation has an evidence note.
* All included recommendations have completed human verification.
* Source dependencies have been assessed.
* Comparability has been assessed.
* Outstanding ambiguities are documented.
* Validation tests pass.
* The README accurately describes the completed work.
* No unsupported clinical claims remain.

Completion of source extraction does not automatically mean the repository is ready for public release.

---

## 32. Release Criteria

A first public research release may be considered only after:

* The protocol is finalized.
* The source and recommendation datasets are complete.
* All release-included records are human verified.
* The analysis script reads only verified data.
* Required tests pass.
* All figures accurately preserve context.
* Limitations are prominently documented.
* Citation metadata contains real, verified author and repository information.
* No placeholder metadata remains.
* A human review confirms that the repository does not provide clinical advice.
* The release version is assigned intentionally.

Until all criteria are satisfied:

* Do not create a DOI.
* Do not create a formal research release.
* Do not describe the project as completed.
* Do not invite clinical use.
* Do not restore `CITATION.cff`.

---

## 33. Planned Next Steps

1. Finalize this protocol.
2. Rename the project to reflect its source-audit design.
3. Create empty source and recommendation schemas.
4. Create the data dictionary.
5. Create the evidence-note template.
6. Extract the first source.
7. Conduct human verification of the first source.
8. Refine the schema only through documented amendments.
9. Repeat extraction and verification for the remaining sources.
10. Design analyses only after the verified data structure is understood.

---

## 34. Protocol Version History

| Version | Date       | Status | Description                                                                                           |
| ------- | ---------- | ------ | ----------------------------------------------------------------------------------------------------- |
| 0.1     | 2026-08-02 | Draft  | Initial protocol for a reproducible source audit of selected adult GAHT monitoring guidance documents |
