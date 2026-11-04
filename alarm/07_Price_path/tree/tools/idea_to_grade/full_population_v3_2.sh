#!/bin/bash
# full_population_v3_2.sh (ALARMLIB seat, 26 Oct 2026; new name for full_population_v3_1.sh ab05ff9e): review gates G1/G2 for idea_to_grade V3.2. One stored alarm list (no producer or
# detector is run), the whole roster, Sep-Dec 2025 (BUILD months), the frozen universe, 2 workers (3 processes), nice 10; wall time and
# memory from /usr/bin/time -l and RUN.json. A scratch ledger holds the PREREG row (the real ledger is only read), so the run is TEST.
#   bash full_population_v3_2.sh <ALARM_ID> <stored EVENTS.tsv>
set -euo pipefail
AID=$1; EV=$2
PY=<PYTHON>
F=<LAB_REPO>/forensics
T=$F/team/RESEARCH/tools/idea_to_grade
ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
U=$F/team/RESEARCH/LIBRARY/UNIVERSE_ALARMS_V1.tsv
FIRST=20250901; LAST=20251231
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
D=<SCRATCH>/work_ALARMLIB/i2g_v3_2/full_${AID}_${STAMP}
mkdir -p "$D"
ASK=PREREG_I2GV31FULL_${AID}_${STAMP}
printf '# scratch ledger of full_population_v3_2.sh\ntry_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\tstatus\n%s\t%s\t%s\tfull population gate G1 G2\tPREREG\t%s\t%s\t\tPREREG\n' \
  "$STAMP" "$ASK" "$AID" "$FIRST" "$LAST" > "$D/LEDGER_FULL.tsv"
SHA=$($PY -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:16])" "$EV")
echo "events $EV $SHA ($(grep -vc '^#' "$EV") lines)"
cd "$D"
/usr/bin/time -l nice -n 10 $PY -B $T/idea_to_grade_v3_2.py --events "$EV" --events-sha16 "$SHA" --roster "$ROSTER" \
  --first $FIRST --last $LAST --research-window $FIRST:$LAST --out "$D/run" --delay-s 2 --ledger "$D/LEDGER_FULL.tsv" --ledger-ask "$ASK" \
  --alarm-id "$AID" --universe "$U" --workers 2 > "$D/stdout.txt" 2> "$D/time_and_stderr.txt" || { echo "RUN FAILED"; tail -20 "$D/time_and_stderr.txt"; exit 1; }
cat "$D/stdout.txt"
grep -E "real|maximum resident" "$D/time_and_stderr.txt" || true
$PY -B -c "
import json,sys; sys.path.insert(0,'$T'); import idea_to_grade_v3_2 as I3
I3.verify_run('$D/run'); b=json.load(open('$D/run/RUN.json'))
print('VERIFIED', b['run_class'], 'parents', b['counts']['parents'], 'coins', len(b['selection']['coins']), 'tough_covered', b['counts']['tough_covered'])
print('timing_s', json.dumps({k: round(v, 1) for k, v in b['timing_s'].items()}))
m=b['memory']; print('memory tree peak GB %.2f, processes %s, worker peaks MB %s' % (m['tree_peak_sampled_bytes']/1024**3, m['tree_peak_processes'],
      sorted(int(v/1024**2) for v in m['worker_ru_maxrss_bytes'].values())))
print('unavailable coin-days', len(b['selection']['unavailable_coin_days']))
"
sed -n 1,8p "$D/run/grade3/REPORT3.md"
echo "OUT $D"
