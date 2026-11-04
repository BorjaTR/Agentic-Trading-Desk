#!/bin/bash
# smoke_month_parts_v1.sh (SCOUT 29 Oct 2026; TEST, NOT REVIEWED): the small runs before the first full MONTH with the parts chain
# (team rule: tiny tests, planted bugs, made-up data, SMALL RUNS, then the full run). Run only as a runner job (it reads lab data).
#   bash smoke_month_parts_v1.sh <DEFINITION.json> <REF_FIRE_LIST.tsv> <W on SCRATCH_DISK> <OUT on dev>
# S1 memory: part A of 8 over Sep-Apr, the chain's own slicer and detect call; peak memory from its DETECT_RUN.json.
# S2 exactness: the chain's own step-1 block run with LAST=20251231 and PARTS=8; its list (rows without '#') must equal, byte for byte,
#    the GRADE job's kept fire list (REF), made by v2_1-era detection in two halves.
set -uo pipefail
DEF=$1; REF=$2; W=$3; OUT=$4
PY=<PYTHON>; F=<LAB_REPO>/forensics; R=$F/team/RESEARCH
DET=$R/tools/alarm_process/detect_aw1.py; ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
CH=$R/tools/month_parts/alarm_grade_chain_v2_2_to20260430.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export METRIC_TRAPS=$R/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv CATALOGS=$R/tools/alarm_context/CTX_CATALOG_V1.tsv:$R/tools/alarm_profile/EPI_CATALOG_V1.tsv:$F/team/LAB3/METRICS_HL_ADD_V1.tsv:$R/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv
[ "$(shasum -a 256 $DET | cut -c1-16)" = 228630e3d0c30b20 ] || { echo "SHA_MISMATCH detect_aw1.py"; exit 2; }
[ -f "$DEF" ] && [ -f "$REF" ] || { echo "NO_INPUT $DEF $REF"; exit 2; }
mkdir -p "$W" "$OUT" || exit 2
mem(){ $PY -c "import json,sys;m=json.load(open(sys.argv[1]));mm=m.get('memory',{});print('status',m.get('status'),'| worker_peak_rss_bytes',mm.get('worker_peak_rss_bytes'),'| parent_peak_rss_bytes',mm.get('parent_peak_rss_bytes'))" "$1/DETECT_RUN.json" 2>&1; }
echo "S1 start $(date -u +%FT%TZ) chain $(shasum -a 256 $CH | cut -c1-16) def $(shasum -a 256 $DEF | cut -c1-16)"
C=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]))['coins'];n,i=int(sys.argv[2]),int(sys.argv[3]);k=len(c);print(','.join(c[i*k//n:(i+1)*k//n]))" $ROSTER 8 0)
t0=$(date +%s); nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $C --first 20250910 --last 20260430 --research-window 20250901:20260430 --out $W/s1_A --workers 3 > $W/s1_A.log 2>&1; r1=$?
echo "S1 rc $r1 seconds $(( $(date +%s)-t0 )) coins $C"; tail -n 2 $W/s1_A.log
[ $r1 -eq 0 ] && mem $W/s1_A
echo "S2 start $(date -u +%FT%TZ)"
S=$W/STATUS_S2.tsv
printf 'step\trc\tseconds\tout\tutc\n' > "$S"; st(){ printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date -u +%FT%TZ)" >> "$S"; }
D=$W/s2_det; FIRST=20250910; LAST=20251231; PARTS=8
BLK=$(sed -n '/^# 1 detect in PARTS parts/,/> \$D\/EVENTS.tsv$/p' $CH)
[ -n "$BLK" ] || { echo "S2 NO_BLOCK"; exit 3; }
( eval "$BLK" ); r2=$?
cat "$S"; echo "S2 rc $r2"
for h in A B C D E F G H; do [ -f ${D}_$h/DETECT_RUN.json ] && echo "S2 part $h $(mem ${D}_$h)"; done
if [ $r2 -eq 0 ] && [ -f $D/EVENTS.tsv ]; then grep -v '^#' $D/EVENTS.tsv > $W/s2_LIST.tsv
  echo "S2 list $(shasum -a 256 $W/s2_LIST.tsv | cut -c1-16) rows $(( $(grep -c . $W/s2_LIST.tsv) - 1 )); reference $(shasum -a 256 $REF | cut -c1-16) rows $(( $(grep -c . $REF) - 1 ))"
  cmp -s $W/s2_LIST.tsv $REF && echo "S2 EXACT: byte-equal" || echo "S2 DIFFERENT"
  cp $W/s2_LIST.tsv $OUT/S2_LIST.tsv; fi
cp $W/STATUS_S2.tsv $OUT/STATUS_S2.tsv 2>/dev/null; [ -f $W/s1_A/DETECT_RUN.json ] && cp $W/s1_A/DETECT_RUN.json $OUT/S1_A_DETECT_RUN.json
echo "end $(date -u +%FT%TZ)"
