# HGVS_to_minimal_MAF_pipeline

Structured or report-derived HGVS annotation to minimal-MAF conversion
component of the CURE-NGS panel harmonization framework.

> **Supported deployment:** reviewers and new users should install the unified
> [CURE-NGS Docker/OCI distribution](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework).
> This repository preserves historical component provenance. The single
> container package belongs to the umbrella repository, so **No packages
> published** in this component repository is expected.

## Role in the unified project

| Item | Value |
| --- | --- |
| Historical responsibility | HGVS spreadsheet/report conversion to minimal MAF |
| Supported command | `cure-ngs hgvs-table-to-minimal-maf` |
| Latest audited component release | `minimal_maf_vep_hg38tohg19_V.1.0.3` |
| Default output assembly | GRCh37/hg19; GRCh38 is explicitly supported |

## Install the supported Docker distribution

1. Install [Docker Desktop](https://docs.docker.com/desktop/) on Windows/macOS
   or [Docker Engine](https://docs.docker.com/engine/install/) on Linux.
2. Build the core image from the canonical repository:

```bash
git clone https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework.git
cd cure-ngs-panel-harmonization-framework
docker build --file docker/Dockerfile.core --tag cure-ngs-harmonizer:0.1.0-core .
```

After the umbrella repository publishes release `0.1.0`, it can instead be
downloaded with:

```bash
docker pull ghcr.io/ncdcbioinformatics/cure-ngs-harmonizer:0.1.0-core
```

Use the source build while the umbrella **Packages** panel says
`No packages published`.

## Verify and run this capability

The bundled example replays a frozen synthetic Ensembl response with container
networking disabled:

```bash
bash scripts/run_reviewer_demo.sh
```

The component-specific command used by that test is:

```bash
mkdir -p output
chmod 0777 output  # Linux: writable by the image's non-root UID 10001
docker run --rm --network none \
  --volume "$PWD/examples:/examples:ro" \
  --volume "$PWD/output:/data/output" \
  cure-ngs-harmonizer:0.1.0-core hgvs-table-to-minimal-maf \
  /examples/synthetic/hgvs_to_minimal_input.tsv \
  /data/output/minimal.grch37.maf \
  --failed /data/output/failed.tsv \
  --reference-fasta /examples/synthetic/tiny.grch37.fa \
  --assembly GRCh37 \
  --response-cache /examples/synthetic/rest-cache --offline-replay
```

For institutional data, replace the miniature synthetic FASTA with an exact
GRCh37 reference and retain the generated manifest and REST cache.

## Historical standalone workflows

- `scripts/hgvs_to_minimal_maf.py`: historical Python entry point
- `scripts/run_hgvs_to_minimal_maf.sh`: historical shell wrapper
- `scripts/minimal_maf_vep_hg38tohg19_V.1.0.3.sh`: release snapshot

Required input fields are `sample ID`, `Gene`, `HGVSc`, `HGVSp`, and
`HGVSp_short`. The consolidated implementation records failures instead of
silently choosing ambiguous mappings.

## Documentation and test data

- [Project structure](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/PROJECT_STRUCTURE.md)
- [HGVS/report route commands](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/COMMAND_REFERENCE.md#structured-hgvs-or-report-derived-route)
- [Synthetic HGVS and frozen REST fixtures](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/tree/main/examples/synthetic)
- [Reference-data policy](https://github.com/NCDCbioinformatics/cure-ngs-panel-harmonization-framework/blob/main/docs/REFERENCE_DATA.md)

License: MIT. No CURE-NGS patient-level data are distributed here.
