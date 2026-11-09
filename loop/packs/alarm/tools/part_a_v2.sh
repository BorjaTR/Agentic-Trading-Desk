# SCOUT Part A of HUNTER_PROMPT_TEMPLATE_V2.md for one V2 run (SCO-A182). No rm, no git, no shared temp file: every output goes to the
# run's own folder RUNF=$LS/runs_v2/<arm><nn> or to $LS/prep/v2/<arm><nn>_*.txt, so several runs can prepare at once.
# usage: bash part_a_v2.sh <L|C> <n> [--behind] [--dry-test]
#   --dry-test: planted config dry_test_v2/SERIES_V2_CONFIG_DRY.json, runs under dry_test_v2/runs_v2, a planted brief, no kit_new,
#               no launch_v1, no start_run, no KIT init, no Mac job, no market data (checks, the order and limit rule, the build).
ARM=$1; N=$2; shift 2 || { echo "usage: part_a_v2.sh <L|C> <n> [--behind] [--dry-test]"; exit 2; }
BEHIND=; DRY=
for x in "$@"; do case $x in --behind) BEHIND=--behind;; --dry-test) DRY=--dry-test;; *) echo "STOP unknown option $x"; exit 2;; esac; done
MNT=$HOME/mnt; [ -d $MNT ] || MNT=$HOME   # C27: Mac host has no mnt (VM layout)
FR=$MNT/dev/TradingPlatform_repo/volat-agent/forensics; R=$MNT/volat_release; LS0=$FR/team/SCOUT/loop_day_20261105/learning_series
B2=$LS0/build/build_run_v2.py
if [ -n "$DRY" ]; then LS=$LS0/dry_test_v2; CFG=${V2_DRY_CFG:-$LS/SERIES_V2_CONFIG_DRY.json}; else LS=$LS0; CFG=$LS/SERIES_V2_CONFIG.json; fi
BR() { python3 -B $B2 "$@" --ls $LS --config $CFG $DRY; }
# words for this run (TASK, RUN_ID, RUNF, RK, paths) from the config: one computation, in build_run_v2.py env
ENVF=$(BR env --arm "$ARM" --run "$N") || { echo "$ENVF"; echo "A0 STOP env"; exit 2; }
eval "$ENVF"
OUTP=$LS/prep/v2; mkdir -p $OUTP $LS/runs_v2/ops
echo "PART_A_V2 $RUN_ID $TASK RUNF $RUNF RK $RK $(date -u +%FT%TZ)"
fail() { echo "$1"; [ -d "$RUNF/ops" ] && printf '%s %s\n' "$(date -u +%FT%TZ)" "$1" >> $RUNF/ops/PART_A_FAILED.txt; exit 1; }
# A0 to A2 under one lock (flock on runs_v2/ops/PART_A.lock): two Part A runs never pass the job limit on the same free slot
exec 9>>$LS/runs_v2/ops/PART_A.lock; { if command -v flock >/dev/null 2>&1; then flock -w 120 9; else python3 -c 'import fcntl,time,sys
for i in range(240):
    try: fcntl.flock(9, fcntl.LOCK_EX | fcntl.LOCK_NB); sys.exit(0)
    except OSError: time.sleep(0.5)
sys.exit(1)'; fi; } || { echo "A0 STOP lock busy 120 s"; exit 1; }
# A0: order rule and the seat job limit (2 until ALARM_V1_22_0 is current, then 6, 8 with --behind; 2 slots per open run)
BR check-launch --arm "$ARM" --run "$N" $BEHIND > $OUTP/${RUN_ID}_CHECK_LAUNCH.txt 2>&1; rc=$?; cat $OUTP/${RUN_ID}_CHECK_LAUNCH.txt
[ $rc -eq 0 ] || { echo "A0 STOP (rc $rc)"; exit 1; }
# A1: the day's RUN key (one RUN per seat per day: shared; started once, guarded by an mkdir marker)
RKD=$FR/team/RESEARCH/ALARM_DESIGN/runs/$RK
if [ -n "$DRY" ]; then
  [ -d $RKD ] && echo "A1 RUN KEY $RK exists (dry: used as it is)" || echo "A1 RUN KEY $RK absent (dry: would start it with start_run_v1)"
elif [ ! -d $RKD ]; then
  if mkdir $LS/runs_v2/ops/RK_START_$RK 2>/dev/null; then
    cd $FR && python3 -B $START_RUN --settings $SET $RK --dry > $LS/runs_v2/ops/RK_START_$RK/DRY.txt 2>&1 && \
    python3 -B $START_RUN --settings $SET $RK > $LS/runs_v2/ops/RK_START_$RK/START.txt 2>&1; echo "rc=$?" >> $LS/runs_v2/ops/RK_START_$RK/START.txt
  fi
  for i in 1 2 3 4 5 6; do [ -d $RKD ] && break; sleep 5; done
  [ -d $RKD ] || { echo "A1 STOP RUN key $RK not started (see runs_v2/ops/RK_START_$RK)"; exit 1; }
  echo "A1 RUN KEY $RK started"
else
  echo "A1 RUN KEY $RK exists (shared)"
fi
# A2: kit_new into the run's own folder (must not exist)
[ -e $RUNF ] && { echo "STOP $RUNF exists"; exit 1; }
mkdir -p $(dirname $RUNF) && mkdir $RUNF || { echo "A2 STOP mkdir $RUNF"; exit 1; }
mkdir -p $RUNF/prep $RUNF/ops
{ command -v flock >/dev/null 2>&1 && flock -u 9; } || exec 9>&-
KIT() { python3 -B "$KITPY" "$@"; }
if [ -n "$DRY" ]; then
  printf '# Brief %s: planted dry-test brief (SCO-A182 dry test; not made by launch_v1; no knowledge, no market data)\nYou are %s, a planted hunter of the dry test. Paper only.\n' $TASK $TASK > $RUNF/prep/BRIEF.md
  mkdir -p $RUNF/library/ALARM_BUILD $RUNF/root; printf 'DRY TEST stand-in folders for what kit_new makes (library/ALARM_BUILD, root); empty\n' > $RUNF/library/DRY_STANDIN.txt
  sed -e "s#@HOME@#$HOME#g" -e "s#@SEAT@#SCOUT#g" $PST > $RUNF/ops/PIPE_SETTINGS_RUN.json
  echo "A2/A3 DRY: kit_new and launch_v1 not run; planted brief $RUNF/prep/BRIEF.md; stand-in library/ and root/; A4 settings from $PST"
else
  cd $FR && KIT kit_new SCOUT $TASK $RUNF --type ALARM_BUILD --version $PACKV > $OUTP/${RUN_ID}_KIT_NEW.txt 2>&1; echo rc=$? >> $OUTP/${RUN_ID}_KIT_NEW.txt
  tail -1 $OUTP/${RUN_ID}_KIT_NEW.txt | grep -q rc=0 || fail "A2 FAIL kit_new (see $OUTP/${RUN_ID}_KIT_NEW.txt)"
  # A3: the brief (goal and pass rule V2 with the config slots filled)
  BR fill --file $LS/GOAL_SERIES_V2.txt > $RUNF/prep/GOAL.txt && BR fill --file $LS/PASS_RULE_SERIES_V2.txt > $RUNF/prep/PASS_RULE.txt || fail "A3 FAIL fill"
  cd $FR && LOOP_ROOT=$RUNF/root LOOP_LIBRARY=$RUNF/library python3 -B $LV --type ALARM_BUILD --seat SCOUT --goal "$(cat $RUNF/prep/GOAL.txt)" --pass-rule "$(cat $RUNF/prep/PASS_RULE.txt)" --window $GATEWIN --min-n $TASKNUM --root $RUNF/root --library $RUNF/library --out $RUNF/prep/BRIEF.md > $RUNF/prep/LAUNCH_V1.txt 2>&1; echo rc=$? >> $RUNF/prep/LAUNCH_V1.txt
  tail -1 $RUNF/prep/LAUNCH_V1.txt | grep -q rc=0 || fail "A3 FAIL launch_v1"
  grep -q "$TASK" $RUNF/prep/LAUNCH_V1.txt || fail "A3 TASK MISMATCH"
  # A4: the run's pipe settings
  sed -e "s#@HOME@#$HOME#g" -e "s#@SEAT@#SCOUT#g" $PST > $RUNF/ops/PIPE_SETTINGS_RUN.json
fi
# A5: the hunter prompt (arm slots, config slots, all checks)
cd $FR && BR build --arm $ARM --run $N --task $TASK --brief $RUNF/prep/BRIEF.md --out $RUNF/HUNTER_PROMPT.md --runf $RUNF --run-key $RK > $RUNF/ops/BUILD_V2.txt 2>&1; rc=$?; cat $RUNF/ops/BUILD_V2.txt
[ $rc -eq 0 ] || fail "A5 FAIL build (rc $rc)"
# A6: kit init (RUN_PROMPT.md, RUN_ENV.sh, time log)
if [ -n "$DRY" ]; then
  echo "A6 DRY: KIT init not run"
else
  cd $FR && KIT init SCOUT $TASK $RUNF --type ALARM_BUILD --version $PACKV --brief $RUNF/HUNTER_PROMPT.md --settings $SET > $RUNF/ops/RUN_INIT_STDOUT.txt 2>&1; echo rc=$? >> $RUNF/ops/RUN_INIT_STDOUT.txt
  tail -1 $RUNF/ops/RUN_INIT_STDOUT.txt | grep -q rc=0 || fail "A6 FAIL KIT init"
  echo RUN_PROMPT $(sha256sum $RUNF/ops/RUN_PROMPT.md | cut -c1-16)
fi
date -u +%FT%TZ > $RUNF/ops/PART_A_DONE_UTC.txt
echo "PART_A_V2 DONE $RUN_ID $TASK $(cat $RUNF/ops/PART_A_DONE_UTC.txt); next: launch one fresh agent with RUN_PROMPT.md, date -u into ops/LAUNCH_UTC.txt"
