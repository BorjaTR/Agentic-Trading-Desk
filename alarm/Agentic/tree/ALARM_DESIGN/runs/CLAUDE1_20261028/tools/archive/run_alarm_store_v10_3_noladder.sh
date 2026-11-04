#!/bin/bash
# run_alarm_store_v10_3_noladder.sh (SCOUT, run CLAUDE1_20261028, 29 Oct 2026; TEST, NOT REVIEWED) = STRATEGY's run_alarm_store_v10_3.sh
# (9601156a694e4755) with ONE change: step (3), the ED3.2 exit ladder, is removed (it wrote 8 to 21 GB a job on SCRATCH_DISK on 29 Oct and S2, the
# markout, does not read it). Step (1), the grader store run (STRATEGY S0), is byte for byte the original. Same arguments.
# run_alarm_store_v10_3.sh (STRATEGY, 28 Oct 2026; STRATEGY_DESIGN runs/STRATEGY_C_R2) = run_alarm_store_v10_2.sh with ONE change: an alarm that is
# not in ALARM_REGISTRY_V1_1 (a frozen alarm-kit alarm such as C2F1) gets a SCRATCH registry row in its grader folder (csize_chain_v1_1.sh's
# format: registry_id card version definition definition_sha16 family), so the grader runs it as TEST; the team's registry is never edited.
#   bash run_alarm_store_v10_3.sh AID FIRST LAST EVENTS SHA16 [DEF_REL CARD_REL FAMILY]   (the last three only for an alarm not in the registry)
# run_alarm_store_v10_2.sh (v10_2 = v10_1 with the ladder settings for the window: a 2026 window reads ED3_2_TEST_M_V1_JANFEB.json (first/last
# 20260101-20260228, run window 20250901-20260228); v10_1's ladder refused every Jan-Feb price day (settings window 20250901-20251231).
# run_alarm_store_v10_1.sh (v10_1 = v10 + optional EVENTS SHA16 args: a window's own event list (ALARM's Jan-Feb detector runs, coordinator 17:59Z);
# then the universe is built from that list (i2g_universe_v1.py), not from UNIVERSE_ALARMS_V1/V3; the list's sha16 must match or exit 2.
#   bash run_alarm_store_v10_1.sh AID FIRST LAST [EVENTS SHA16]
# run_alarm_store_v10.sh (26 Oct 2026, the owner 17:52Z: Jan-Feb open for checking ideas; coordinator 17:54Z: build the Jan-Feb stores on SCRATCH_DISK).
# = run_alarm_chain_v9.sh steps (1) grader store and (3) ED3.2.1 ladder only, for any BUILD window FIRST..LAST (the signed grader refuses any
# non-BUILD month itself: WINDOWS_V1 BUILD = 20250901-20260228). No group/classify/risk: the cards for Jan-Feb come from CTXLIB/PROFLIB/CAUSELIB.
# Refuses (exit 6) when the alarm's event list has no fire in the window. Writes STATUS.tsv in its chain folder. Never deletes.
#   bash run_alarm_store_v10.sh AID FIRST LAST     e.g. ALM_C_V1 20260101 20260228
set -uo pipefail
AID=$1; FIRST=$2; LAST=$3; EVX=${4:-}; EVSHA=${5:-}; RDEF=${6:-}; RCARD=${7:-}; RFAM=${8:-}
LCFG=<DEV>/_scratch_ED3/ed3_2_test/ED3_2_TEST_M_V1.json; [ "${FIRST:0:4}" = 2026 ] && LCFG=<DEV>/_scratch_ED3/ed3_2_test/ED3_2_TEST_M_V1_JANFEB.json
PY=<PYTHON>
F=<LAB_REPO>/forensics
R=$F/team/RESEARCH
# the universe that holds the alarm: V1 (the M recipe) when it has it, else V3 (V2_1 rows + A02P); the registry V1_1 has every id
U1=$R/LIBRARY/UNIVERSE_ALARMS_V1.tsv; U3=$R/LIBRARY/UNIVERSE_ALARMS_V3.tsv
if grep -q "^# source ${AID}=" "$U1"; then U=$U1; U2=$U1; else U=""; U2=$U3; fi
REG=$R/LIBRARY/alarm_library/ALARM_REGISTRY_V1_1.tsv
# context cards: the V4.2 run (M recipe) when it has the alarm, else the newest V4.4 commit that has it
CARDS=$R/LIBRARY/context_split/runs_v42/commit_e730e87799cffba1/STATE_CARDS_${AID}_V41.tsv
[ -f "$CARDS" ] || CARDS=$(ls -t $R/LIBRARY/context_split/runs_v44/commit_*/STATE_CARDS_${AID}_V41.tsv 2>/dev/null | head -1)
G=<DEV>/_scratch_tooltrial/grouper_v1
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
C=<SCRATCH>/work_TOOLTRIAL/chain/${AID}_${FIRST}_${LAST}_${STAMP}
mkdir -p "$C"; S=$C/STATUS.tsv
printf 'step\trc\tseconds\tout\tutc\n' > "$S"
st(){ printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date -u +%FT%TZ)" >> "$S"; }

EV=$(grep "^# source ${AID}=" "$U2" | head -1 | sed -E "s/^# source ${AID}=([^ ]+) .*/\1/")
if [ -n "$EVX" ]; then EV=$EVX; U=""; [ "$(shasum -a 256 "$EV" | cut -c1-8)" = "${EVSHA:0:8}" ] || { st events 2 0 "EVENTS_SHA_NOT_${EVSHA}"; exit 2; }; fi
[ -f "$EV" ] || { st events 2 0 "NO_EVENT_LIST_FOR_${AID}"; exit 2; }
st events 0 0 "$EV"

# (1) grader store run: full_population_v3_2.sh's recipe (delay 2, 2 workers, scratch ledger, TEST), Sep-Dec 2025 only; a source list
#     reaching past Dec is cut to Sep-Dec and declared a slice (--events-subset), so no holdout day is read
t0=$(date +%s)
T=$R/tools/idea_to_grade
D=<SCRATCH>/work_ALARMLIB/i2g_v3_2/full_${AID}_${FIRST}_${LAST}_${STAMP}; mkdir -p "$D"
# an alarm missing from V1: its own V1-format universe from its WHOLE source list (the strict V1 reader refuses V2/V3 columns)
if [ -z "$U" ]; then U=$D/UNIVERSE_${AID}_V1FMT.tsv; $PY -B $T/i2g_universe_v1.py "$U" "${AID}=${EV}" > "$C/0_universe.log" 2>&1 || { st universe 2 0 "$U"; exit 2; }; st universe 0 0 "$U"; fi
EVS=$EV; SUB=""
NOUT=$($PY -c "import csv,sys,datetime as d;r=[x for x in csv.DictReader((l for l in open(sys.argv[1]) if not l.startswith('#')),delimiter='\t')];print(sum(1 for x in r if not sys.argv[2]<=d.datetime.utcfromtimestamp(int(x['t'])).strftime('%Y%m%d')<=sys.argv[3]))" "$EV" $FIRST $LAST)
if [ "$NOUT" != "0" ]; then
  EVS=$D/EVENTS_${FIRST}_${LAST}.tsv; SUB=--events-subset
  $PY -c "import sys,datetime as d
src,out,a,b=sys.argv[1:5];fo=open(out,'x');n=0
for l in open(src):
    if l.startswith('#'): fo.write(l); continue
    c=l.rstrip('\n').split('\t')
    if c[0]=='coin' or (c[1].isdigit() and a<=d.datetime.utcfromtimestamp(int(c[1])).strftime('%Y%m%d')<=b): fo.write(l); n+=c[0]!='coin'
print('events in window', n)
sys.exit(0 if n else 6)" "$EV" "$EVS" $FIRST $LAST > "$C/0_events.log" 2>&1 || { st events_window 6 0 "NO_EVENTS_${FIRST}_${LAST}"; exit 6; }
fi
# v10_3: a scratch registry row when the alarm is not in the team's registry (the team's file is never edited)
if ! awk -F'\t' -v a="$AID" '$1==a{f=1} END{exit !f}' "$REG"; then
  [ -n "$RDEF" ] && [ -f "$F/$RDEF" ] && [ -n "$RCARD" ] && [ -n "$RFAM" ] || { st registry 2 0 "NOT_IN_REGISTRY_AND_NO_SCRATCH_ROW_${AID}"; exit 2; }
  REG=$D/REGISTRY_SCRATCH.tsv; DSHA=$(shasum -a 256 "$F/$RDEF" | cut -c1-16)
  printf '# scratch registry of run_alarm_store_v10_3.sh (TEST)\nregistry_id\tcard\tversion\tdefinition\tdefinition_sha16\tfamily\n%s\t%s\t1\t%s\t%s\t%s\n' "$AID" "$RCARD" "$RDEF" "$DSHA" "$RFAM" > "$REG"
  st registry 0 0 "$REG"
fi
ASK=PREREG_I2GV31FULL_${AID}_${STAMP}
printf '# scratch ledger of run_alarm_chain.sh\ntry_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\tstatus\n%s\t%s\t%s\tchain store run\tPREREG\t%s\t%s\t\tPREREG\n' "$STAMP" "$ASK" "$AID" "$FIRST" "$LAST" > "$D/LEDGER_FULL.tsv"
SHA=$($PY -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:16])" "$EVS")
# v4: store by the S4b twin (grader thread, byte-equal to V3.2 on M, S3W, A02P), driver and pins sha pinned
[ "$(shasum -a 256 $T/idea_to_grade_v3_2_s6.py | cut -c1-16)" = 7f8d935faf1034f8 ] && [ "$(shasum -a 256 $T/I2G_PINS_V3_2_S6.json | cut -c1-16)" = 75aee82e3ab5f99d ] || { st grader_store 4 0 "S6_NOT_PINNED"; exit 4; }
( cd "$D" && /usr/bin/time -l nice -n 10 $PY -B $T/idea_to_grade_v3_2_s6.py --events "$EVS" --events-sha16 "$SHA" $SUB \
    --roster $F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json \
    --first $FIRST --last $LAST --research-window $FIRST:$LAST --out "$D/run" --delay-s 2 --ledger "$D/LEDGER_FULL.tsv" --ledger-ask "$ASK" \
    --alarm-id "$AID" --universe "$U" --registry "$REG" --workers 3 --pins $T/I2G_PINS_V3_2_S6.json ) > "$C/1_store.log" 2>&1; rc=$?
RUN=$D/run
st grader_store $rc $(( $(date +%s)-t0 )) "$RUN"
[ $rc -eq 0 ] && [ -f "$RUN/RUN.json" ] || exit 3

# (3) exit ladder: REMOVED in this copy (not needed by the markout; see the header)
st done $rc 0 "$C"
exit $rc
