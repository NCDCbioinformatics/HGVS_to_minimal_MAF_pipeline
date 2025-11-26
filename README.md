# HGVS-to-minimal-MAF pipeline
Pipeline for creating minimal MAF with HGVS

# outline:
   - Using the HGVS (HGVSc) information in Excel \
     First, annotate GRCh37 VEP, if that doesn't work, then annotate GRCh38 VEP \
     Converting GRCh38→GRCh37 coordinates using Ensembl assembly map API \
     Finally, all generate minimal MAF based on GRCh37 (hg19) coordinates

# Requirements:
   - Available at https://grch37.rest.ensembl.org and https://rest.ensembl.org \
   - Install Python 3, pandas, and requests

# How to use:
   chmod +x minimal_maf_vep_hg38tohg19_V.1.0.0.sh \
   ./minimal_maf_vep_hg38tohg19_V.1.0.0.sh minimal_maf_test_normalized.xlsx [sheet] [threads]


# Columns required for input Excel:
   - sample ID \
   - Gene \
   - HGVSc        (ex: c.422G>A, Requirements) \
   - HGVSp        (ex: p.Cys141Tyr) \
   - HGVSp_short  (ex: p.C141Y) \

