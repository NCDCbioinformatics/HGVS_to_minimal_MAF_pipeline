#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <input.xlsx> [output.maf.tsv] [sheet] [threads]" >&2
  exit 1
fi

INPUT_XLSX="$1"
OUTPUT_MAF="${2:-minimal_maf_from_hgvs.tsv}"
SHEET="${3:-0}"
THREADS="${4:-8}"

"${PYTHON_BIN}" "${SCRIPT_DIR}/hgvs_to_minimal_maf.py" \
  --excel-in "${INPUT_XLSX}" \
  --maf-out "${OUTPUT_MAF}" \
  --sheet "${SHEET}" \
  --threads "${THREADS}"
