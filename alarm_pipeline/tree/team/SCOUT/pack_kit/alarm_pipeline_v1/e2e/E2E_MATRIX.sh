#!/bin/bash
# E2E_MATRIX.sh (SCO-A162R, SCOUT, 6 Nov 2026; the owner 22:53 Berlin "The pipeline has to work for any date and any alarm built on any metrics
# we choose"): the pipeline's matrix acceptance from this install, one command, no agent, as ONE runner job on the Mac (CORES 8, MEM_MB 12000):
# every INPUT_*.json in matrix_v1/ beside this file (24 cases: each month Sep 2025 to Mar 2026, a month-end range, one day, a window across
# the block end, 14 graded alarms of 7 metric families, SIZE and SIDE, one coin and five, few and many fires) through all 22 steps in a new
# pipe folder each (pipe_e2e_v1); a case passes on 22 of 22, or on the named refusal its INPUT asks for (e2e_expect). Run it twice into two
# new folders and compare them: python3 -B compare_ab_v1.py <a> <b> <out.tsv> (results and every STEP json, run identity aside). Usage: bash E2E_MATRIX.sh <out root (new)>
set -u
H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-<PYTHON>}; OUT=$1
CASES=(); for f in "$H"/matrix_v1/INPUT_*.json; do n=$(basename "$f" .json); CASES+=("${n#INPUT_}=$f"); done
echo "cases ${#CASES[@]}"
$PY -B "$H/../pipe_mac/pipe_e2e_v2.py" "$OUT" --template "$H/PIPE_SETTINGS_V3_TEMPLATE.json" --home <VM_SESSION> --seat SCOUT --budget-s 1500 "${CASES[@]}"
