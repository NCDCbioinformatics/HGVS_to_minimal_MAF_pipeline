#!/usr/bin/env python3
"""Convert spreadsheet HGVS records into a minimal MAF-style table.

The script prefers Ensembl GRCh37 coordinates and falls back to GRCh38 plus
assembly mapping when only GRCh38 annotations are available.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import pandas as pd
import requests

GRCH37_VEP = "https://grch37.rest.ensembl.org"
GRCH38_VEP = "https://rest.ensembl.org"
ASSEMBLY_MAP = "https://rest.ensembl.org"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


@dataclass
class MinimalMafRow:
    hugo_symbol: str
    tumor_sample_barcode: str
    chromosome: str
    start_position: int
    end_position: int
    reference_allele: str
    tumor_seq_allele2: str
    reference_assembly: str


def build_hgvs(row: pd.Series) -> Optional[str]:
    gene = str(row.get("Gene", "")).strip()
    if not gene:
        return None
    for column in ("HGVSc", "HGVSp", "HGVSp_short"):
        value = row.get(column)
        if pd.notna(value):
            text = str(value).strip()
            if text:
                return f"{gene}:{text}"
    return None


def reverse_complement(base: str) -> str:
    table = str.maketrans("ACGTacgt", "TGCAtgca")
    return base.translate(table)[::-1]


def parse_alleles(allele_string: str) -> Optional[tuple[str, str]]:
    if "/" not in allele_string:
        return None
    ref, alt = allele_string.split("/", 1)
    return ref.upper(), alt.upper()


def vep_lookup(base_url: str, hgvs: str) -> Optional[dict]:
    url = f"{base_url}/vep/human/hgvs/{quote(hgvs, safe='')}"
    response = requests.get(url, params={"canonical": 1}, headers=HEADERS, timeout=30)
    if response.status_code != 200:
        return None
    payload = response.json()
    if not isinstance(payload, list) or not payload:
        return None
    return payload[0]


def map_grch38_to_grch37(chrom: str, start: int, end: int, strand: int) -> Optional[dict]:
    region = f"{chrom}:{start}..{end}:{strand}"
    url = f"{ASSEMBLY_MAP}/map/human/GRCh38/{region}/GRCh37"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if response.status_code != 200:
        return None
    payload = response.json()
    mappings = payload.get("mappings") or []
    if not mappings:
        return None
    return mappings[0].get("mapped")


def record_to_maf(record: dict, assembly: str) -> Optional[MinimalMafRow]:
    alleles = parse_alleles(record.get("allele_string", ""))
    chrom = record.get("seq_region_name")
    start = record.get("start")
    end = record.get("end")
    if not alleles or chrom is None or start is None or end is None:
        return None
    ref, alt = alleles
    return MinimalMafRow(
        hugo_symbol="",
        tumor_sample_barcode="",
        chromosome=str(chrom),
        start_position=int(start),
        end_position=int(end),
        reference_allele=ref,
        tumor_seq_allele2=alt,
        reference_assembly=assembly,
    )


def resolve_variant(hgvs: str) -> Optional[MinimalMafRow]:
    record37 = vep_lookup(GRCH37_VEP, hgvs)
    if record37:
        maf = record_to_maf(record37, "GRCh37")
        if maf:
            return maf

    record38 = vep_lookup(GRCH38_VEP, hgvs)
    if not record38:
        return None

    alleles = parse_alleles(record38.get("allele_string", ""))
    chrom = record38.get("seq_region_name")
    start = record38.get("start")
    end = record38.get("end")
    strand = int(record38.get("strand", 1))
    if not alleles or chrom is None or start is None or end is None:
        return None

    mapped = map_grch38_to_grch37(str(chrom), int(start), int(end), strand)
    if not mapped:
        return None

    ref, alt = alleles
    mapped_strand = int(mapped.get("strand", 1))
    if mapped_strand == -1 and len(ref) == 1 and len(alt) == 1:
        ref = reverse_complement(ref)
        alt = reverse_complement(alt)

    return MinimalMafRow(
        hugo_symbol="",
        tumor_sample_barcode="",
        chromosome=str(mapped["seq_region_name"]),
        start_position=int(mapped["start"]),
        end_position=int(mapped["end"]),
        reference_allele=ref,
        tumor_seq_allele2=alt,
        reference_assembly="GRCh38->GRCh37",
    )


def process_row(index: int, row: pd.Series) -> Optional[dict]:
    hgvs = build_hgvs(row)
    if not hgvs:
        return None

    maf = resolve_variant(hgvs)
    if not maf:
        return None

    maf.hugo_symbol = str(row.get("Gene", "")).strip()
    maf.tumor_sample_barcode = str(row.get("sample ID", "")).strip()
    return {
        "_index": index,
        "Hugo_Symbol": maf.hugo_symbol,
        "Tumor_Sample_Barcode": maf.tumor_sample_barcode,
        "Chromosome": maf.chromosome,
        "Start_Position": maf.start_position,
        "End_Position": maf.end_position,
        "Reference_Allele": maf.reference_allele,
        "Tumor_Seq_Allele2": maf.tumor_seq_allele2,
        "Reference_Assembly": maf.reference_assembly,
        "HGVS_Input": hgvs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--excel-in", required=True, help="Input Excel file")
    parser.add_argument("--maf-out", required=True, help="Output TSV/MAF path")
    parser.add_argument("--sheet", default="0", help="Worksheet index or name")
    parser.add_argument("--threads", type=int, default=8, help="Parallel worker count")
    args = parser.parse_args()

    sheet = int(args.sheet) if str(args.sheet).isdigit() else args.sheet
    dataframe = pd.read_excel(args.excel_in, sheet_name=sheet)
    dataframe.columns = [str(column).strip() for column in dataframe.columns]

    required = {"sample ID", "Gene", "HGVSc", "HGVSp", "HGVSp_short"}
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise SystemExit(f"Missing columns: {', '.join(missing)}")

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.threads)) as executor:
        futures = [executor.submit(process_row, index, row) for index, row in dataframe.iterrows()]
        for future in as_completed(futures):
            result = future.result()
            if result:
                rows.append(result)

    if not rows:
        raise SystemExit("No variants could be resolved from the input spreadsheet.")

    rows.sort(key=lambda item: item["_index"])
    for row in rows:
        row.pop("_index", None)

    output = pd.DataFrame(rows)
    output.to_csv(args.maf_out, sep="\t", index=False)


if __name__ == "__main__":
    main()
