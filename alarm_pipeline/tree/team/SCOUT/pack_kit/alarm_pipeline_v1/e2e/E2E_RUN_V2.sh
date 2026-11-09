#!/bin/bash
# E2E_RUN_V2.sh (SCO-A162R, 7 Nov 2026): E2E_RUN.sh on pipe_e2e_v2 (alarm_pipeline_v1_3; named refusals). Was: E2E_RUN.sh (SCO-A162, SCOUT, 6 Nov 2026): the pipeline's end-to-end acceptance from this install, one command, no agent, as ONE runner
# job on the Mac (declare CORES 8 for the card step, MEM_MB 12000): every case through all 22 steps in a new pipe folder (pipe_e2e_v1),
# the WIDEBLOCKS replay compared with trial I (16 lines). Usage: bash E2E_RUN.sh <out root (new)> [CASE=INPUT.json ...]
# Default cases: the two replays beside this file. Prints E2E PASS|FAIL <case> <steps> <seconds>; E2E_RESULT.tsv in <out root>.
set -u
H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-<PYTHON>}; OUT=$1; shift
FR=${FR:-<LAB_REPO>/forensics}
CASES=("$@"); [ ${#CASES[@]} -eq 0 ] && CASES=(WIDEBLOCKS=$H/INPUT_WIDEBLOCKS_V1_REPLAY.json CROWDDRAG=$H/INPUT_CROWDDRAG_V1_REPLAY.json)
$PY -B $H/../pipe_mac/pipe_e2e_v2.py "$OUT" --template $H/PIPE_SETTINGS_V3_TEMPLATE.json --home <VM_SESSION> --seat SCOUT "${CASES[@]}"; rc=$?
if [ -f "$OUT/WIDEBLOCKS/STEP_22_HANDOFF.json" ]; then
  $PY -B $FR/team/SCOUT/loop_day_20261105/v18/compare_trialI_v18.py "$OUT/WIDEBLOCKS" "$OUT/COMPARE_TRIALI.tsv" | head -1 | tee "$OUT/COMPARE.txt"
  grep -q "DIFF 0 of" "$OUT/COMPARE.txt" || rc=1
fi
exit $rc
