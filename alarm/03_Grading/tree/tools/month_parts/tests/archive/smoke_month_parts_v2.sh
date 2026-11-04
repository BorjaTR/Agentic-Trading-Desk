#!/bin/bash
# smoke_month_parts_v2.sh (SCOUT 29 Oct 2026; TEST, NOT REVIEWED): second small run, after smoke v1 (job 20264079: S2 EXACT, S1 part A
# peaked 2029518848 bytes over Sep-Apr, 1.89 GiB, review 1 expected 1.70). Fixes from review 1 (pins, exit codes, no reuse of W or OUT).
#   bash smoke_month_parts_v2.sh <DEFINITION.json> <W on SCRATCH_DISK> <OUT on dev>
# S1 every eighth of the roster over Sep-Apr with the chain's own slicer and detect call: peak memory of each (stops at a refusal).
# S3 a window split: part A over Jan-Apr only (--first 20260101, same research window 20250901:20260430): its memory, and its rows must
#    equal S1 part A's rows with t >= 1767225600 (2026-01-01), byte for byte.
set -uo pipefail
DEF=$1; W=$2; OUT=$3
PY=<PYTHON>; F=<LAB_REPO>/forensics; R=$F/team/RESEARCH
DET=$R/tools/alarm_process/detect_aw1.py; ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
CH=$R/tools/month_parts/alarm_grade_chain_v2_2_to20260430.sh
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export METRIC_TRAPS=$R/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv CATALOGS=$R/tools/alarm_context/CTX_CATALOG_V1.tsv:$R/tools/alarm_profile/EPI_CATALOG_V1.tsv:$F/team/LAB3/METRICS_HL_ADD_V1.tsv:$R/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv
[ "$(shasum -a 256 $DET | cut -c1-16)" = 228630e3d0c30b20 ] || { echo "SHA_MISMATCH detect_aw1.py"; exit 2; }
[ "$(shasum -a 256 $CH | cut -c1-16)" = 86ff2af4f2318b6f ] || { echo "SHA_MISMATCH chain"; exit 2; }
[ "$(shasum -a 256 $DEF | cut -c1-16)" = 94c2d5188ef9d715 ] || { echo "SHA_MISMATCH definition"; exit 2; }
[ ! -e "$W" ] && [ ! -e "$OUT/S1.tsv" ] || { echo "USED W or OUT"; exit 2; }
mkdir -p "$W" "$OUT" || exit 2
mem(){ $PY -c "import json,sys;m=json.load(open(sys.argv[1]));mm=m.get('memory',{});print(m.get('status'),max(mm.get('worker_peak_rss_bytes') or [0]),mm.get('parent_peak_rss_bytes'),m.get('events'),sep=chr(9))" "$1/DETECT_RUN.json" 2>&1; }
part(){ $PY -c "import json,sys;c=json.load(open(sys.argv[1]))['coins'];n,i=int(sys.argv[2]),int(sys.argv[3]);k=len(c);print(','.join(c[i*k//n:(i+1)*k//n]))" $ROSTER 8 $1; }
printf 'part\tcoins\trc\tseconds\tstatus\tworker_peak_bytes\tparent_peak_bytes\tevents\n' > $OUT/S1.tsv
ok=1
for i in 0 1 2 3 4 5 6 7; do h=$(echo ABCDEFGH | cut -c$((i+1))); C=$(part $i)
  t0=$(date +%s); nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $C --first 20250910 --last 20260430 --research-window 20250901:20260430 --out $W/s1_$h --workers 3 > $W/s1_$h.log 2>&1; r=$?
  if [ $r -eq 0 ]; then printf '%s\t%s\t%s\t%s\t%s\n' $h $C $r $(( $(date +%s)-t0 )) "$(mem $W/s1_$h)" >> $OUT/S1.tsv
  else printf '%s\t%s\t%s\t%s\t%s\n' $h $C $r $(( $(date +%s)-t0 )) "$(tail -n 1 $W/s1_$h.log | tr '\t' ' ')" >> $OUT/S1.tsv; ok=0; break; fi
done
cat $OUT/S1.tsv
C=$(part 0); t0=$(date +%s)
nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $C --first 20260101 --last 20260430 --research-window 20250901:20260430 --out $W/s3_A --workers 3 > $W/s3_A.log 2>&1; r3=$?
echo "S3 rc $r3 seconds $(( $(date +%s)-t0 ))"; tail -n 1 $W/s3_A.log
if [ $r3 -eq 0 ] && [ -f $W/s1_A/EVENTS.tsv ]; then echo "S3 memory $(mem $W/s3_A)"
  grep -v '^#' $W/s1_A/EVENTS.tsv | tail -n +2 | awk -F'\t' '$2 >= 1767225600' > $W/s1_A_janapr.tsv
  grep -v '^#' $W/s3_A/EVENTS.tsv | tail -n +2 > $W/s3_A_rows.tsv
  echo "S3 rows $(grep -c . $W/s3_A_rows.tsv) vs S1 part A Jan-Apr rows $(grep -c . $W/s1_A_janapr.tsv)"
  if cmp -s $W/s3_A_rows.tsv $W/s1_A_janapr.tsv; then echo "S3 EXACT: byte-equal"; else echo "S3 DIFFERENT"; ok=0; fi
else ok=0; fi
echo "end $(date -u +%FT%TZ) ok $ok"
[ $ok -eq 1 ] && exit 0 || exit 3
