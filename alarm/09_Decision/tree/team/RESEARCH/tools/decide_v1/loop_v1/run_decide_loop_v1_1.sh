#!/bin/bash
# run_decide_loop_v1_1.sh (DECIDE seat, 26 Oct 2026 ~07:05Z; = run_decide_loop_v1.sh, which is frozen in release e76e30fb, plus a release check and PREREG V1.1 named in each ledger row): the outcome loop of decision tool V1 for ALM_M_V1. Four GRADED idea_to_grade V3.1 runs,
# one after the other (2 workers + 1 = 3 processes, nice 10): VALUED, TAKE, SKIPRULE, BADDATA (all --events-subset). Each run gets
# its own PREREG row in TRIES_LEDGER_V1 (ledger_add_v6, idea ALM_M_V1, type SETTING_CHOICE, family EXH) written just before it starts.
# No producer or detector is run. Then decide_loop_read_v1.py applies the fixed bar. Run only after the independent review of decide V1 passes.
#   bash run_decide_loop_v1_1.sh <new out folder>
set -euo pipefail
O=$1; [ -e "$O" ] && { echo "REFUSED: $O exists"; exit 1; }
PY=<PYTHON>
F=<LAB_REPO>/forensics
T=$F/team/RESEARCH/tools/idea_to_grade
D=$F/team/RESEARCH/tools/decide_v1/loop_v1
SET=$D/DECIDE_LOOP_SETTINGS_V1.json
LEDGER=$F/team/RESEARCH/tools/ledger/ledger_add_v6.py
ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
U=$F/team/RESEARCH/LIBRARY/UNIVERSE_ALARMS_V1.tsv
FIRST=20250901; LAST=20251231
SPLIT=<SCRATCH>/work_DECIDE/loop_v1_split_v3
sha() { $PY -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:16])" "$1"; }
want() { $PY -c "import json,sys;S=json.load(open(sys.argv[1]));print(S['events_sha16'][sys.argv[2]])" "$SET" "$1"; }
mkdir -p "$O"
echo "settings $(sha $SET)" | tee "$O/RUNS.txt"
# the release graded is the reviewed one, with every file still at its sha16
REL=$F/team/RESEARCH/tools/decide_v1/RELEASE_DECIDE_V1_CANDIDATE.json
[ "$(sha $REL)" = "9c83cf0306d20410" ] || { echo "REFUSED: release is $(sha $REL), not 9c83cf0306d20410"; exit 1; }
$PY -B $F/team/RESEARCH/tools/decide_v1/make_release_decide_v1.py --check $F $REL | tee -a "$O/RUNS.txt" | grep -q "every file at its sha16" || { echo "REFUSED: a release file moved"; exit 1; }
echo "release 9c83cf0306d20410 checked; PREREG V1.1 $(sha $D/DECIDE_LOOP_PREREG_V1_1.md)" | tee -a "$O/RUNS.txt"
# the decision run must still be committed and unchanged (kit rows 3 and 11), and its DECISIONS.tsv the one the settings pin
RUN=<SCRATCH>/work_DECIDE/run_v1_4/ALM_M_V1_OWN
$PY -B -c "import sys;sys.path.insert(0,'$F/team/RESEARCH/tools/decide_v1');import decide_v1 as DV;DV.verify_run('$RUN');print('decision run VERIFIED $RUN')" | tee -a "$O/RUNS.txt"
[ "$(sha $RUN/DECISIONS.tsv)" = "$($PY -c "import json,sys;print(json.load(open(sys.argv[1]))['decisions']['sha16'])" "$SET")" ] || { echo "REFUSED: DECISIONS.tsv is not the one the settings pin"; exit 1; }
for G in VALUED TAKE SKIPRULE BADDATA; do
  EV=$SPLIT/${G}_EVENTS.tsv; SUB="--events-subset"
  S=$(sha "$EV"); [ "$S" = "$(want $G)" ] || { echo "REFUSED: $G events $S differ from the settings"; exit 1; }
  ASK=$($PY -B $LEDGER prereg ALM_M_V1 "decide V1 release 9c83cf0306d20410 outcome loop group $G, taken vs skipped compared on 24 Sep-31 Dec only (predictions team/RESEARCH/tools/decide_v1/loop_v1/DECIDE_LOOP_PREREG_V1_1.md $(sha $D/DECIDE_LOOP_PREREG_V1_1.md))" \
        "$SET" $FIRST $LAST --type SETTING_CHOICE --family EXH | awk '{print $1}')
  echo "$G events $EV $S ask $ASK start $(date -u +%Y%m%dT%H%M%SZ)" | tee -a "$O/RUNS.txt"
  ( cd "$O" && nice -n 10 $PY -B $T/idea_to_grade_v3.py --events "$EV" --events-sha16 "$S" --roster "$ROSTER" --first $FIRST --last $LAST \
      --research-window $FIRST:$LAST --out "$O/$G" --delay-s 2 --ledger-ask "$ASK" --alarm-id ALM_M_V1 --universe "$U" $SUB --workers 2 \
      > "$O/$G.stdout.txt" 2> "$O/$G.stderr.txt" ) || { echo "$G RUN FAILED" | tee -a "$O/RUNS.txt"; tail -20 "$O/$G.stderr.txt"; exit 1; }
  $PY -B -c "import sys;sys.path.insert(0,'$T');import idea_to_grade_v3 as I;I.verify_run('$O/$G');import json;b=json.load(open('$O/$G/RUN.json'));print('$G VERIFIED',b['run_class'],b['counts']['parents'])" | tee -a "$O/RUNS.txt"
done
$PY -B $D/decide_loop_read_v1.py "$SET" "$O/VALUED" "$O/TAKE" "$O/SKIPRULE" "$O/BADDATA" "$O/read" | tee -a "$O/RUNS.txt"
echo "DONE $(date -u +%Y%m%dT%H%M%SZ)" | tee -a "$O/RUNS.txt"
