# HGVS-to-minimal-MAF pipeline
HGVS로 minimal MAF를 만들기 위한 pipeline

# 개요:
   - 엑셀에 있는 HGVS (HGVSc/HGVSp) 정보를 이용해 \
     먼저 GRCh37 VEP를 annotation, 안 되면 GRCh38 VEP를 annotation 후 \
     Ensembl assembly map API로 GRCh38→GRCh37 좌표를 변환하여 \
     최종적으로 모두 GRCh37(hg19) 좌표 기준의 minimal MAF를 생성

# 요구:
   - https://grch37.rest.ensembl.org  와 https://rest.ensembl.org 에 접속 가능 \
   - 파이썬3, pandas, requests 설치

# 사용법:
   chmod +x minimal_maf_vep_hg38tohg19_V.1.0.0.sh \
   ./minimal_maf_vep_hg38tohg19_V.1.0.0.sh minimal_maf_test_normalized.xlsx [sheet] [threads]


# 입력 엑셀에 필요한 컬럼:
   - sample ID \
   - Gene \
   - HGVSc        (예: c.422G>A) \
   - HGVSp        (예: p.Cys141Tyr) \
   - HGVSp_short  (예: p.C141Y) \

