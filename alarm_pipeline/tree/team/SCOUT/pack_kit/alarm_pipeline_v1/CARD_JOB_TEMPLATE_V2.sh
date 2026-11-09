# JOB {NAME} -- alarm_pipeline_v1 step 17 CARD for {ALARM} (task {TASK}; SCO-A153 SCOUT, PLAYGROUND, TEST, NOT REVIEWED): alarm_understand bundle --from-job the GRADE job, then mech_cards_run_v1 on a one-alarm config (draw_v3 matched moments, readings_builder_v1, alarm_cards_v1 card), then mechanism_v2 (the map's own membership codes: the bundle, the DEF, readings E2.S06) (CARD_JOB_TEMPLATE_V2, SCO-A154). Never deletes.
# WRITES {OUT}/
# QUEUE {QUEUE} (declared minutes: 40)
# WRITES_MB: 800
# MEM_MB: 8000
# CORES 1
# TASK: {TASK}
set -u
PY={PY}
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
R={OUT}; [ -e $R ] && { echo "RECEIPTS EXIST $R"; exit 4; }; mkdir -p $R || exit 4
export AU_SCRATCH=$R/scratch
date -u +%FT%TZ > $R/STAMP.txt
case {BLOCK} in SEPMAR) FIRST=20250910; LAST=20260331;; SEPDEC) FIRST=20250910; LAST=20251231;; JANMAR) FIRST=20260101; LAST=20260331;; *) echo "STOP block" >> $R/STAMP.txt; exit 5;; esac
$PY -B {AU}/alarm_understand_v1.py bundle $R/BUNDLE --from-job {GRADE_NUM} --runner {RN} --alarm {ALARM} --block {BLOCK} --true-row {TRUE_ROW} --def-sha16 {DEF_SHA16} > $R/BUNDLE.txt 2>&1 || { echo "STOP bundle" | tee -a $R/STAMP.txt; exit 6; }
grep -v '^#' $R/BUNDLE/FIRES.tsv > $R/FIRES_LIST.tsv
printf 'alarm\tblock\tbundle\tfires_list\tdraw\tdef\tdef_sha16\tgrade_key\n{ALARM}\t{BLOCK}\t%s\t%s\tNEW\t{DEF}\t{DEF_SHA16}\t{ALARM}\n' $R/BUNDLE $R/FIRES_LIST.tsv > $R/CONFIG.tsv
cp {GRADES} $R/GRADES.tsv
$PY -B {AU}/mech_cards_run_v1.py $R/CARDS --mechanism {ALARM} --config $R/CONFIG.tsv --grades $R/GRADES.tsv > $R/CARDS.txt 2>&1 || { echo "STOP cards" | tee -a $R/STAMP.txt; exit 7; }
$PY -B {PIPE}/mechanism_v2.py $R/MECHANISM.json --bundle $R/BUNDLE --def {DEF} --readings $R/CARDS/RD_{ALARM}_{BLOCK} --first $FIRST --last $LAST --lean {LEAN} --map {MAP} --card-tsv $R/CARDS/ALARM_CARDS_{ALARM}.tsv --card-alarm {ALARM} > $R/MECHANISM.txt 2>&1 || { echo "STOP mechanism" | tee -a $R/STAMP.txt; exit 8; }
(cd $R && shasum -a 256 *.txt *.tsv *.json BUNDLE/* CARDS/*.tsv CARDS/*.md CARDS/*.txt) > $R/SHA16.txt 2>/dev/null
echo "END $(date -u +%FT%TZ)" >> $R/STAMP.txt
exit 0
