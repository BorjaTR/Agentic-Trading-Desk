# JOB @N@_judge_SCOUT_LS@RUN@_SPLIT -- learning series V2 run @RUN@ (task @TASK@; kit SCO-A182 V2): FEEDBACK market-state split of the round graded in @PIPE@ by ONE reading, with the released Alarm/state_split current (STATE_SPLIT_V1_0 at kit time, SCO-A181; the grade's own code path, REPRO of STEP_11 first). Filed by the hunter after the round's pipe ended DONE ALL (the card step wrote the READINGS); needs the GRADE work folder, so it runs before the run-end clean.
# WRITES team/SCOUT/loop_day_20261105/learning_series/runs_v2/@RUN@/@OUT@/ (new folder; the tool refuses OUT_EXISTS)
# QUEUE @Q@ (declared minutes: 15)
# WRITES_MB: 50
# MEM_MB: 3000
# CORES: 1
# TITLE: @N@_SCOUT_LS@RUN@_SPLIT -- state split of @PIPE@ by @READING@ (yardstick @YNAME@ @Y15@ at 15 min, @Y1H@ at 1 h). Never deletes.
# TASK: @TASK@ LEARNING SERIES
set -u
case "@YNAME@@Y15@@Y1H@" in *@*) echo "REFUSED UNFILLED_YARDSTICK"; exit 5;; esac
FR=<LAB_REPO>/forensics; PY=<PYTHON>
SS=<RELEASE_ROOT>/Alarm/state_split/current/tree/team/SCOUT/pack_kit/state_split_v1/state_split_v1.py
B=$FR/team/SCOUT/loop_day_20261105/learning_series/runs_v2/@RUN@
export PYTHONDONTWRITEBYTECODE=1
echo "utc $(date -u +%FT%TZ) edition $(readlink <RELEASE_ROOT>/Alarm/state_split/current) state_split_v1 $(shasum -a 256 $SS | cut -c1-16)"
[ -f $B/@PIPE@/STEP_11_GRADE.json ] || { echo "NOT GRADED $B/@PIPE@"; exit 4; }
$PY -B $SS run $B/@PIPE@ --out $B/@OUT@ --reading @READING@ --yardstick15 @Y15@ --yardstick1h @Y1H@ --yardstick-name @YNAME@
rc=$?
echo "STATE_SPLIT rc $rc"
echo "END $(date -u +%FT%TZ)"
exit $rc
