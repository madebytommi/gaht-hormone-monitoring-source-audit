# GAHT Reference Range Analysis

## Abstract
This project provides an open-research analysis that models and harmonizes target serum hormone ranges across three major clinical protocols for Gender-Affirming Hormone Therapy (GAHT): the Endocrine Society 2017, WPATH SOC 8 2022, and UCSF 2016 Guidelines. By unifying these reference ranges, this repository serves as a foundational dataset and visualization tool for clinical researchers and practitioners.

## Methods
We extracted and modeled target hormone ranges for three key categories:
- Feminizing Estradiol (pg/mL)
- Feminizing Testosterone (ng/dL)
- Masculinizing Testosterone (ng/dL)

Data was synthesized from the published guidelines of the Endocrine Society, WPATH, and UCSF. We developed a Python script (`gaht_reference_ranges.py`) leveraging `matplotlib` and `numpy` to visualize these ranges for comparative analysis.

## Results
The target ranges exhibit significant consensus across the clinical protocols, particularly for feminizing estradiol which remains consistently targeted at 100 - 200 pg/mL across all three guidelines. Minor variations exist in masculine testosterone ranges; for instance, WPATH SOC 8 suggests 350 - 1000 ng/dL compared to UCSF's narrower 400 - 700 ng/dL. The resulting visualization (`gaht_target_ranges.png`) provides a clear, unified comparative view of these targets.

## Script Execution
To run the analysis script and generate the plot locally:

```bash
# 1. Install required dependencies
pip install matplotlib numpy

# 2. Execute the script
python gaht_reference_ranges.py
```

Execution will output `gaht_target_ranges.png` to the repository root.

## Citation
If you use this work in your research, please refer to the included `CITATION.cff` file or use the ORCID-linked DOI release via Zenodo.
