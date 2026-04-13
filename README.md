# HGVS_to_minimal_MAF_pipeline

Utilities for converting spreadsheet HGVS annotations into a minimal MAF-style table.

## Repository role

This repository is a component of the CURE-NGS panel harmonization framework described in the manuscript "Multi-Institutional Harmonization Framework for Heterogeneous Panel-Based NGS in Precision Oncology."

Umbrella repository: https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework

## Available workflows

- `scripts/hgvs_to_minimal_maf.py`: Python entrypoint for Excel-to-minimal-MAF conversion
- `scripts/run_hgvs_to_minimal_maf.sh`: shell wrapper for command-line execution
- `scripts/minimal_maf_vep_hg38tohg19_V.1.0.3.sh`: legacy workflow snapshot

## Quick start

```bash
bash scripts/run_hgvs_to_minimal_maf.sh input.xlsx output.tsv 0 8
```

## Required input columns

- `sample ID`
- `Gene`
- `HGVSc`
- `HGVSp`
- `HGVSp_short`

## Requirements

- Linux or WSL
- Python 3
- `pandas`
- `requests`
- Access to [grch37.rest.ensembl.org](https://grch37.rest.ensembl.org) and [rest.ensembl.org](https://rest.ensembl.org)

## Notes

- The workflow prefers GRCh37 annotations first.
- If only GRCh38 annotations are available, it falls back to Ensembl assembly mapping from GRCh38 to GRCh37.
- Output is written as a tab-delimited minimal MAF-style table.

## Software metadata

- Operating system(s): Linux; Windows users can run supported workflows via WSL where needed
- Programming language(s): Bash shell, Python
- License: MIT License
