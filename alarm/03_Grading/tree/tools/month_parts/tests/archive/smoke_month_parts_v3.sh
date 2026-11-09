#!/bin/bash
# smoke_month_parts_v3.sh (SCOUT 29 Oct 2026; TEST, NOT REVIEWED): third small run. Smoke 2 (job 20264080): over Sep-Apr every eighth
# peaked 1.81 to 1.89 GiB and part F (PEPE PUMP RENDER SEI SHIB SOL SUI) was REFUSED WORKER_RSS_CAP 2150924288 bytes. This measures the
# floor: part F's coins 1 or 2 at a time over Sep-Apr (LG4).   bash smoke_month_parts_v3.sh <DEFINITION.json> <W> <OUT>
set -uo pipefail
DEF=$1; W=$2; OUT=$3
PY=<PYTHON>; F=<LAB_REPO>/forensics; R=$F/team/RESEARCH
DET=$R/tools/alarm_process/detect_aw1.py; ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export METRIC_TRAPS=$R/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv CATALOGS=$R/tools/alarm_context/CTX_CATALOG_V1.tsv:$R/tools/alarm_profile/EPI_CATALOG_V1.tsv:$F/team/LAB3/METRICS_HL_ADD_V1.tsv:$R/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv
[ "$(shasum -a 256 $DET | cut -c1-16)" = 482a4a1eaf1faff5 ] && [ "$(shasum -a 256 $DEF | cut -c1-16)" = 94c2d5188ef9d715 ] || { echo SHA_MISMATCH; exit 2; }
[ ! -e "$W" ] && [ ! -e "$OUT/S4.tsv" ] || { echo "USED W or OUT"; exit 2; }
mkdir -p "$W" "$OUT" || exit 2
mem(){ $PY -c "import json,sys;m=json.load(open(sys.argv[1]));mm=m.get('memory',{});print(m.get('status'),max(mm.get('worker_peak_rss_bytes') or [0]),m.get('events'),sep=chr(9))" "$1/DETECT_RUN.json" 2>&1; }
printf 'coins\trc\tseconds\tstatus\tpeak_bytes\tevents\n' > $OUT/S4.tsv
for C in PEPE,PUMP RENDER,SEI SHIB,SOL SUI; do h=$(echo $C | tr ',' '_')
  t0=$(date +%s); nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $C --first 20250910 --last 20260430 --research-window 20250901:20260430 --out $W/s4_$h --workers 3 > $W/s4_$h.log 2>&1; r=$?
  if [ $r -eq 0 ]; then printf '%s\t%s\t%s\t%s\n' $C $r $(( $(date +%s)-t0 )) "$(mem $W/s4_$h)" >> $OUT/S4.tsv; else printf '%s\t%s\t%s\t%s\n' $C $r $(( $(date +%s)-t0 )) "$(tail -n 1 $W/s4_$h.log | tr '\t' ' ')" >> $OUT/S4.tsv; fi
done
cat $OUT/S4.tsv; echo "end $(date -u +%FT%TZ)"
