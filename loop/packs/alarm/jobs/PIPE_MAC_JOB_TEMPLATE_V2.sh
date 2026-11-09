# JOB @N@_judge_SCOUT_LS@RUN@_PIPE -- learning series V2 run @RUN@ (task @TASK@; kit SCO-A182 V2, from PIPE_MAC_JOB_TEMPLATE.sh): the pipeline in ONE Mac runner job, pipe_mac_v3 of the released Alarm/alarm_pipeline current (the edition current at the job; SCO-A162R route, its README "Run it on the Mac: one runner job"), no VM bridge, no time window.
# WRITES team/SCOUT/loop_day_20261105/learning_series/runs_v2/@RUN@/pipe/ (STEP and STOP files, logs, PENDING, TIMES.tsv, MAC_SETTINGS.json); the COUNT, GRADE, TRUE and CARD jobs pipe_mac files go to the runner its settings name (rootq); the card under the settings cards_root
# QUEUE @Q@ (declared minutes: 50)
# WRITES_MB: 800
# MEM_MB: 2000
# CORES: 1
# TITLE: @N@_SCOUT_LS@RUN@_PIPE -- learning series V2 run @RUN@ pipeline, Mac mode. Never deletes.
# TASK: @TASK@ LEARNING SERIES (SCO-A184: pipe_mac_v3 = alarm_pipeline_v1_4, ALARM_PIPELINE_V1_4_1; was pipe_mac_v2 = v1_3)
set -u
FR=<LAB_REPO>/forensics; PY=<PYTHON>
PM=<RELEASE_ROOT>/Alarm/alarm_pipeline/ALARM_PIPELINE_V1_4_2/tree/team/SCOUT/pack_kit/alarm_pipeline_v1/pipe_mac/pipe_mac_v3_sepjan_v2.py
P=$FR/team/SCOUT/loop_day_20261105/learning_series/runs_v2/@RUN@/pipe
export PYTHONDONTWRITEBYTECODE=1
echo "utc $(date -u +%FT%TZ) edition $(readlink <RELEASE_ROOT>/Alarm/alarm_pipeline/current) pipe_mac_v3 $(shasum -a 256 $PM | cut -c1-16)"
[ -f $P/INPUT.json ] && [ -f $P/SETTINGS.json ] || { echo "NO INIT $P"; exit 4; }
# FIRE CAP gate (C25, SCOUT 2026-11-08): no GRADE (step 07+) while STEP_06 COUNT is over 10000 fires
CAP=10000; UNTIL=$(printf '%s' "@EXTRA@" | sed -n 's/.*--until \([0-9][0-9]*\).*/\1/p')
PAST6=1; [ -n "$UNTIL" ] && [ "$UNTIL" -le 6 ] && PAST6=0
if [ $PAST6 = 1 ] && [ ! -f $P/STEP_06_COUNT.json ]; then
  $PY -B $PM run $P --vm-prefix @VMPREFIX@ --mac-home <HOME> --budget-s 2700 --poll-s 5 --until 6
  rc=$?; [ $rc = 0 ] || { echo "PIPE_MAC rc $rc (count part)"; echo "END $(date -u +%FT%TZ)"; exit $rc; }
fi
if [ $PAST6 = 1 ] && [ -f $P/STEP_06_COUNT.json ] && [ ! -f $P/STEP_11_GRADE.json ]; then
  FIRES=$($PY -c 'import json,sys; d=json.load(open(sys.argv[1])); r=d["numbers"]["count_rows"]; a=[x for x in r if x.get("month")=="ALL"]; print(int(a[0]["fires"]) if a else sum(int(x["fires"]) for x in r))' $P/STEP_06_COUNT.json)
  echo "COUNT fires $FIRES cap $CAP"
  [ "$FIRES" -le $CAP ] || { echo "FIRE_CAP REFUSED: $FIRES fires > $CAP: tighten the change and re-COUNT in a fresh pipe folder"; echo "END $(date -u +%FT%TZ)"; exit 7; }
fi
$PY -B $PM run $P --vm-prefix @VMPREFIX@ --mac-home <HOME> --budget-s 2700 --poll-s 5 @EXTRA@
rc=$?
echo "PIPE_MAC rc $rc"
echo "END $(date -u +%FT%TZ)"
exit $rc
