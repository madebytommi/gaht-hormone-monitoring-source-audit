# GAHT Hormone Monitoring Source Audit

> **STATUS NOTICE:** This project is in the protocol-development and source-verification stage. No clinical findings, recommended hormone ranges, consensus conclusions, or comparative results have been established.
>
> This repository is not ready for citation or release and must not be used for diagnosis, treatment, medication adjustment, laboratory interpretation, or other clinical decision-making.

## Overview

This repository is an early research scaffold for a reproducible documentary audit of how selected gender-affirming hormone therapy guidance documents describe adult serum estradiol and testosterone monitoring recommendations.

The project is designed to preserve the context surrounding each recommendation, including:

* Recommendation type
* Numerical threshold or interval, when explicitly stated
* Comparison operator and unit
* Therapy direction and intended population
* Route, formulation, and dosing context
* Specimen timing
* Treatment phase
* Exact source location
* Relationship to upstream guidance
* Comparability and human-verification status

The project will not create a new therapeutic range, average guideline boundaries, infer missing values, or provide patient-specific clinical guidance.

## Research Protocol

The tracked [`PROTOCOL.md`](PROTOCOL.md) defines the authoritative research question, scope, eligibility rules, extraction process, human-verification requirements, comparability rules, analysis limits, and release criteria.

No recommendation may enter an analysis or visualization until it has been traced to an authoritative source and explicitly marked as human verified.

## Current Status

The repository is currently being stabilized and prepared for structured source extraction.

At this stage:

* No source recommendations have been verified.
* No research dataset has been completed.
* No comparative analysis has been performed.
* No visualization has been approved.
* No citation metadata, release, DOI, or Zenodo archive should be created.

## Current Script

`gaht_reference_ranges.py` is a temporary draft-status placeholder. It contains no clinical values and does not perform an analysis or generate a visualization.

To verify its current behavior:

```bash
python gaht_reference_ranges.py
```

Expected output:

```text
STATUS: Data under source verification.
No visualization will be generated until a human-verified source-extraction dataset is added.
This repository currently serves as an early draft scaffold.
```

## Planned Workflow

The planned workflow is:

1. Finalize the research protocol.
2. Create the source and recommendation extraction schemas.
3. Record authoritative source metadata.
4. Extract recommendations with complete context.
5. Human-verify every included recommendation.
6. Assess source dependencies and comparability.
7. Implement validation and descriptive analysis.
8. Consider visualizations only when the verified data support them.
9. Review the repository against the release criteria in `PROTOCOL.md`.

## Initial Candidate Sources

The initial candidate source set includes guidance from:

* The Endocrine Society
* WPATH Standards of Care, Version 8
* UCSF Transgender Care

These names do not establish verified clinical values. Complete source metadata, corrections, recommendation language, and contextual details must be verified and recorded through the protocol-defined workflow.

## License

Original code and project documentation are provided under the terms of the repository’s [`LICENSE`](LICENSE).

Short source excerpts may be included only when necessary to document an extraction. Full copyrighted guidance documents will not be stored in this repository.
