#!/bin/bash
# alarm_grade_chain_v2_0_6_to20251231.sh (SCOUT, 31 Oct 2026, V2_0 stage 2 D1; TEST, NOT REVIEWED): alarm_grade_chain_v2_0_5_to20251231.sh
# e88dbe0aacba8ee8 with only steps 5-7 changed (the owner 31 Oct 2026 13:34 Berlin: GRADE and MONTH under 60 s; team/SCOUT/D1_BUILD_PLAN_V1.md): ONE
# process, d1_reports_v3.py chain, runs both Outcomes runs (event_outcomes_rel1 run(0), each in its own process, its rows kept as they are
# written, beside the root as <root>.mem.pkl), then the menu and the card (alarm_card_v1_2_1) in its process from those rows (event_outcomes.read
# answered from memory, checked against the store's subject, days and coins); step 0 job 20265186: 338 of 338 columns equal, the
# reports byte for byte. The STATUS lines come from its steps file in the old order; an Outcomes failure exits 6 as before. The rest
# of this header is the parent's:
# alarm_grade_chain_v2_0_5_to20251231.sh (SCOUT, 31 Oct 2026, V2_0 stage 1; TEST, NOT REVIEWED): alarm_grade_chain_v2_0_4_to20251231.sh
# 81885fb0c25f82b1 with only the order of steps 5-7 changed (the owner 31 Oct 2026 12:37 Berlin: "agents need to run tools as fast as
# possible"; team/SCOUT/SPEED_V2_0_DESIGN_V1.md Q1, Q2): the Outcomes runs on the alarm and the random lists work at the same time
# (two roots, no shared write), then the menu and the card at the same time (both only read the two roots). Each waits for its own
# process; the STATUS lines are written after the waits, in v2_0_4's order; on a failure every started run ends first, then the
# first failure in v2_0_4's order exits with v2_0_4's code. The tools, their arguments, inputs and outputs are v2_0_4's.
# The rest of this header is v2_0_4's:
# alarm_grade_chain_v2_0_4_to20251231.sh (SCOUT K16, 31 Oct 2026, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_0_3_to20251231.sh aa8ea2e5c86d5a70 with only Outcomes (step 5) changed (K16 T5; SCOUT 31 Oct: "T5 goes back into
# V1_7, for GRADE only"): event_outcomes_rel1.py runs in 3 worker processes (run 3) in place of 1 (run 1), on the alarm list and on the
# random list; the job declares 3 cores (JOB_GRADE_V9; WORKING_SESSION_V16 section 0.7: a job declares its cores). Why: job 20264959 x2
# (team/SCOUT/receipts/20264959_K16PROF/x2/PARTS_EQUAL.txt 23b6b94481fa2cfa): one Outcomes root in 24.2 s against 34.6 s (its worker
# phase 15.3 s against 28.7 s). The gate (REV2): every day's index readings, the REASONS and the WORDS files equal to run 1's, built_utc
# (the build's wall clock) excluded. x2 compared the manifest's parts: the 17,680 REASONS and WORDS files equal, the 104 index.json files
# not byte-equal; REV2 found them different only in built_utc and the 123,032 value blocks of their readings equal by sha16
# (team/SCOUT/REV2/evidence/T5_INDEX_COMPARE_V1.txt 2baf3ed0cd60c78a). The rest of this header is v2_0_3's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_0_4_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_0_3_to20251231.sh (SCOUT K12, 31 Oct 2026, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_0_2_to20251231.sh 702987b96f7c3f57 with only Outcomes (step 5) changed (SCOUT 31 Oct: "take the feed-gate dev
# path out of GRADE and MONTH"): event_outcomes_rel1.py (7c35f72782745b9c: event_outcomes.py with the feed's stop gate from FEED_GATE, never
# labcore.jobgate's built-in dev-tree GATE, and the research days from RESEARCH_STORE), its workers run_parallel_rel1.py (46302fd8cf630120), its
# release record RELEASE_event_outcomes_V3_REL1.json (da0dd8eee3d12679); the three checked by sha16 before any step and named in INPUTS_<V>.txt (4
# lines appended: outcomes, launcher, release, research); the caller gives RESEARCH_STORE (the settings key: an absolute path) as it
# gives FEED_GATE, and the chain exports both to Outcomes. The rest of this header is v2_0_2's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_0_3_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_0_2_to20251231.sh (SCOUT 31 Oct 2026, K12, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_0_1_to20251231.sh 43d6ce6aa4be89b5 (SCOUT K4, 30 Oct) with only the grader and the detector changed to their
# clean editions (CLEAN_RELEASE_V1; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only"). Why:
# GRADE job 20264797 (AD20, 31 Oct 02:20Z) ran v2_0_1 from the install and idea_to_grade.py refused UNPINNED_MODULE: its pins
# I2G_PINS_V2.json name the dev tree's absolute paths, and its code loads its kernels from the dev tree. Changed, nothing else:
#   step 1: detect_v2.py (97a822a20e08088d; detect.py with its paths changed, the same EVENTS) with --gate="$FEED_GATE";
#   step 3: idea_to_grade_rel1.py (edee6bbe51a2bbde, SCOUT K6: idea_to_grade.py V2.3.1 with its paths changed: tree root from its file,
#           kernels i2g_engine_rel1, i2g_grade_rel1 and their clean editions) with --gate="$FEED_GATE" and --pins I2G_PINS_V2_REL1.json
#           (b34c5d55cfcf48de: the same 39 files as I2G_PINS_V2.json, the 11 clean editions in place of the old, paths relative to the tree);
#   the caller gives FEED_GATE in the environment (the settings key FEED_GATE; set and empty: no gate, a machine without the feed);
#   the three files are checked by sha16 before any step and named in INPUTS_<V>.txt (4 lines appended: detect, grade, pins, gate);
#   METRICS_V1 is exported beside METRIC_TRAPS and CATALOGS (the lab tree's team/LAB3/METRICS_V1.tsv, c2335f86987c5045, the dev tree's
#   bytes): the detector's metric gate (labcore.briefs -> metric_brief.py) read it from the dev tree by its built-in default (T1, 31 Oct).
# Window, steps, other tools, arguments and outputs otherwise unchanged. v2_0_1's header follows.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_0_2_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_0_1_to20251231.sh (SCOUT 30 Oct 2026, K4, home team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_0_to20251231.sh 94273faf1e927ddc (STRATEGY 28 Oct) with only its paths changed (CLEAN_RELEASE_V1; the owner 30 Oct
# 2026 23:07 Berlin: "All alarm tools should work from the release folder only"): the caller gives AL, PY and LAB_DAYS in the
# environment (below); every step tool and table comes from the lab tree <AL>/01_Detection/tree (the dev layout), never the dev tree;
# the lab days go to detect, the grade and Outcomes as an argument (detect and idea_to_grade had the Mac's as their built-in default);
# matched random, the menu and the card are the paths-only editions make_random_v3_1, menu_v2_1 and alarm_card_v1_2_1 (alarm_process).
# Window, steps, arguments and outputs otherwise unchanged. v2_0's header follows.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_0_1_to20251231.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_0_to20251231.sh (STRATEGY 28 Oct 2026; ALARM_DESIGN KIT_V2; TEST, NOT REVIEWED): v1_3 with a HARDCODED date range, FIRST and LAST below
# (detect, grade, matched random and Outcomes read 20250910..20251231 only, research window 20250901:20251231), the card v1_2 (its own
# hardcoded range, its sha16 checked here), the window and the card sha16 written into INPUTS_<V>.txt, and the menu step
# (LEAD menu_v2.py, labelled Sep-Dec) no longer setting the final rc. Its sha16 says which months a run could read (TOOLS_REGISTRY.tsv).
# alarm_grade_chain_v1_3.sh (STRATEGY, 27 Oct 2026; v1_3 = v1_2 + SCREEN=1 in the env: no grading, no matched random, Outcomes on the
# fire list only and the card v1_1 with --screen (the reads against BASE only), to screen parts fast; card v1_1 also when not screening; team/RESEARCH/tools/alarm_process, TEST, NOT REVIEWED). The ALARM GRADER for one
# variant, in LEAD's loop 2 pipeline_v4.sh order with its own tools: 1 detect.py on the definition, in two coin halves of 3 workers each
# (the 2 GiB WORKER_RSS_CAP; proven exact on C, job 126) merged; 2 the plain fire list; 3 idea_to_grade.py graded from the list (matched
# moments); 4 make_random_v3.py (matched random, own moments out, 3 per fire, each wave once); 5 event_outcomes.py on the alarm list and
# the random list (honest cost) with the menu settings; 6 menu_v2.py -> MENU_<V>_om.txt; 7 alarm_card_v1.py -> CARD_<V>.txt (+ SUM_<V>.tsv).
# v1_1 = v1 + LIST mode (a .tsv instead of a definition: that list is the fire list, no detection; for delay controls) + the menu settings
# as an argument (default OUTCOMES_MENU_ALARM_V1.json = loop 2's labels + a race grid) + step 7 (BASE=<variant> in the env: paired read).
#   bash alarm_grade_chain_v1_1.sh <V> <DEFINITION.json | FIRES.tsv> <W_ROOT> [MENU.json]      V: letters and digits only
# Window (v1_3's was 20250910..20251231): this version's FIRST and LAST below. Never deletes. One worker after detection.
# v2_0_7 (BUILD5, ALARM_V1_10; made by team/BUILD5/proposals/v1_10/chains/make_chain_v2_0_7.py from v2_0_6 931cbddd85227a2b): the gm
# editions with the window GRADE (G1 D4) and the Outcomes store in evt1 (D2 step 3); nothing else changed.
set -uo pipefail
export EO_WINDOWS=GRADE   # v2_0_7: the window of every gm edition this chain runs (children inherit it)
FIRST=20250910; LAST=20251231   # this version's hardcoded date range (UTC days): never a setting
CARD_SHA=e71a0241a147f497   # v2_0_7: alarm_card_gm1.py (one card for GRADE and MONTH, --windows)
DET_SHA=ad3708259c8fcc38; I2G_SHA=49684513485c868f; PINS_SHA=a78e8319465fcfe4   # v2_0_7: detect_gm1.py, idea_to_grade_gm1.py, I2G_PINS_GM1.json
EO_SHA=cd502f49fe16415e; RP_SHA=3ed4ea58b74fddc9; REL_SHA=5ab652c414ca450c   # v2_0_7: event_outcomes_gm2.py, run_parallel_gm2.py, RELEASE_event_outcomes_GM2.json
D1_SHA=0b1717ba35a12b95; MEM_SHA=3cd95039ba6e1a70   # V2_0 stage 2 D1: d1_reports_v3.py and d1_mem_v2.py, beside this chain   # K12 v2_0_3: event_outcomes_rel1.py, run_parallel_rel1.py, RELEASE_event_outcomes_V3_REL1.json
V=$1; DEF=$2; W=$3
[[ "$V" =~ ^[A-Za-z0-9]+$ ]] || { echo "BAD_VARIANT $V"; exit 2; }
[ -f "$DEF" ] || { echo "NO_DEFINITION $DEF"; exit 2; }
# K4: the machine comes from the caller (the V6 jobs fill it from the settings file): AL the Alarm folder (code and tables; this file
# must be inside it), PY the interpreter (settings PYTHON), LAB_DAYS the lab days (settings LAB_DAYS); the lab tree F is <AL>/01_Detection/tree
for k in AL PY LAB_DAYS; do v=${!k:-}; [ -n "$v" ] && [ "${v#/}" != "$v" ] || { echo "NO_$k: set $k to an absolute path (the job fills it from the settings file)"; exit 2; }; done
# K12: the feed's stop gate (settings FEED_GATE): it must be SET; empty = no gate (a machine without the feed), else an absolute path
[ "${FEED_GATE+set}" = set ] || { echo "NO_FEED_GATE: set FEED_GATE to the feed's stop gate file, or to empty for none (the job fills it from the settings file)"; exit 2; }
[ -z "$FEED_GATE" ] || [ "${FEED_GATE#/}" != "$FEED_GATE" ] || { echo "NO_FEED_GATE: FEED_GATE is not an absolute path: $FEED_GATE"; exit 2; }
# K12 (v2_0_3, v2_2_3): the research days (settings RESEARCH_STORE) must be set, an absolute path; Outcomes reads them and the gate
# from the environment, so both are exported
[ -n "${RESEARCH_STORE:-}" ] && [ "${RESEARCH_STORE#/}" != "$RESEARCH_STORE" ] || { echo "NO_RESEARCH_STORE: set RESEARCH_STORE to the research days, an absolute path (the job fills it from the settings file)"; exit 2; }
export FEED_GATE RESEARCH_STORE
[ -f "$AL/_tools/settings_v1.py" ] && [ -d "$AL/settings" ] || { echo "NOT_AN_ALARM_FOLDER $AL (no _tools/settings_v1.py and settings/)"; exit 2; }
case "$(cd "$(dirname "$0")" && pwd -P)/" in "$(cd "$AL" && pwd -P)"/*) ;; *) echo "CHAIN_OUTSIDE_ALARM $0 is not inside $AL"; exit 2;; esac
F=$AL/01_Detection/tree; R=$F/team/RESEARCH
T=$R/tools; L2=$R/LEAD/loop2; ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
G=${4:-$T/alarm_process/OUTCOMES_MENU_ALARM_V1.json}; [ -f "$G" ] || { echo "NO_MENU $G"; exit 2; }
export METRICS_V1=$F/team/LAB3/METRICS_V1.tsv METRIC_TRAPS=$L2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv CATALOGS=$T/alarm_context/CTX_CATALOG_V1.tsv:$T/alarm_profile/EPI_CATALOG_V1.tsv:$F/team/LAB3/METRICS_HL_ADD_V1.tsv:$L2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv
export W PYTHONDONTWRITEBYTECODE=1
mkdir -p "$W" || exit 2; S=$W/STATUS_${V}.tsv; [ -f "$S" ] && { echo "STATUS_EXISTS $S (variant already run here)"; exit 2; }
printf 'step\trc\tseconds\tout\tutc\n' > "$S"; st(){ printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date -u +%FT%TZ)" >> "$S"; }
[ "$(shasum -a 256 $T/alarm_process/alarm_card_gm1.py | cut -c1-16)" = "$CARD_SHA" ] || { echo "CARD_SHA_MISMATCH"; exit 2; }
DET=$T/idea_to_grade/detect_gm1.py; I2G=$T/idea_to_grade/idea_to_grade_gm1.py; PINS=$T/idea_to_grade/I2G_PINS_GM1.json
ckf(){ [ "$(shasum -a 256 $1 | cut -c1-16)" = "$2" ] || { echo "SHA_MISMATCH $1 (want $2)"; exit 2; }; }
ckf $DET $DET_SHA; ckf $I2G $I2G_SHA; ckf $PINS $PINS_SHA
EO=$T/event_outcomes/event_outcomes_gm2.py; RP=$T/event_profile/run_parallel_gm2.py; REL=$T/event_outcomes/RELEASE_event_outcomes_GM2.json
ckf $EO $EO_SHA; ckf $RP $RP_SHA; ckf $REL $REL_SHA
H=$(cd "$(dirname "$0")" && pwd -P); ckf $H/d1_reports_v3.py $D1_SHA; ckf $H/d1_mem_v2.py $MEM_SHA
printf 'chain\t%s\t%s\nwindow\t%s\t%s\ncard\t%s\t%s\ninput\t%s\t%s\nmenu\t%s\t%s\nbase\t%s\n' "$(shasum -a 256 $0 | cut -c1-16)" "$0" "$FIRST" "$LAST" "$CARD_SHA" "$T/alarm_process/alarm_card_gm1.py" "$(shasum -a 256 $DEF | cut -c1-16)" "$DEF" "$(shasum -a 256 $G | cut -c1-16)" "$G" "${BASE:-none} lean ${LEAN:-FADE} screen ${SCREEN:-0}" > "$W/INPUTS_${V}.txt"
printf 'detect\t%s\t%s\ngrade\t%s\t%s\npins\t%s\t%s\ngate\t%s\n' "$DET_SHA" "$DET" "$I2G_SHA" "$I2G" "$PINS_SHA" "$PINS" "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"
printf 'outcomes\t%s\t%s\nlauncher\t%s\t%s\nrelease\t%s\t%s\nresearch\t%s\n' "$EO_SHA" "$EO" "$RP_SHA" "$RP" "$REL_SHA" "$REL" "$RESEARCH_STORE" >> "$W/INPUTS_${V}.txt"
printf 'd1\t%s\t%s\nd1mem\t%s\t%s\n' "$D1_SHA" "$H/d1_reports_v3.py" "$MEM_SHA" "$H/d1_mem_v2.py" >> "$W/INPUTS_${V}.txt"
D=$W/det_${V}_v1; LIST=$W/${V}_FIRES_V1_LIST.tsv
if [[ "$DEF" == *.tsv ]]; then
  [ "$(head -1 "$DEF" | cut -f1-3)" = "$(printf 'coin\tt\tside')" ] || { st list 2 0 "LIST_HEADER $DEF"; exit 3; }
  cp -n "$DEF" "$LIST"; st list_given 0 0 "$DEF"
else
# 1 detect in two halves (roster order), merged, rows sorted by t then coin
HA=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]))['coins'];print(','.join(c[:len(c)//2]))" $ROSTER)
HB=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]))['coins'];print(','.join(c[len(c)//2:]))" $ROSTER)
for h in A B; do t0=$(date +%s); [ $h = A ] && C=$HA || C=$HB
  nice -n 10 $PY -B $DET --windows GRADE --definition "$DEF" --roster $ROSTER --coins $C --first $FIRST --last $LAST --research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$h --workers 3 > ${D}_$h.log 2>&1; rc=$?
  st detect_$h $rc $(( $(date +%s)-t0 )) ${D}_$h; [ $rc -eq 0 ] && [ -f ${D}_$h/EVENTS.tsv ] || exit 3; done
mkdir -p $D && { grep '^#' ${D}_A/EVENTS.tsv; echo "# merged by alarm_grade_chain_v1_3.sh: det_A + det_B (two roster halves), rows sorted by t then coin"
  grep -v '^#' ${D}_A/EVENTS.tsv | head -1
  { grep -v '^#' ${D}_A/EVENTS.tsv | tail -n +2; grep -v '^#' ${D}_B/EVENTS.tsv | tail -n +2; } | sort -t$'\t' -k2,2n -k1,1; } > $D/EVENTS.tsv
grep -v '^#' $D/EVENTS.tsv > $LIST
fi
N=$(( $(grep -c . $LIST) - 1 )); st list 0 0 "$LIST ($N fires)"; [ $N -gt 0 ] || exit 3
if [ "${SCREEN:-0}" = 1 ]; then XS="ALARM"; st screen 0 0 "no grading, no random"; else XS="ALARM RND"
# 3 grade from the list
SH=$(shasum -a 256 $LIST | cut -c1-16); t0=$(date +%s)
nice -n 10 $PY -B $I2G --windows GRADE --events $LIST --events-sha16 $SH --roster $ROSTER --coins ALL --first $FIRST --last $LAST --research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins $PINS --out $W/gradeL_${V}_v1 --workers 1 > $W/gradeL_${V}_v1.log 2>&1; rc=$?
st grade $rc $(( $(date +%s)-t0 )) $W/gradeL_${V}_v1; [ $rc -eq 0 ] || exit 4
# 4 matched random (own moments out, 3 per fire)
t0=$(date +%s); nice -n 10 $PY -B $T/alarm_process/make_random_v3_1.py $W/gradeL_${V}_v1 $LIST $W/RND_${V}_V1 3 > $W/RND_${V}_V1.log 2>&1; rc=$?
st random $rc $(( $(date +%s)-t0 )) $W/RND_${V}_V1_LIST.tsv; [ $rc -eq 0 ] || exit 5
fi
# 5-7 (V2_0 stage 2 D1): ONE process from Outcomes to the menu and the card (d1_reports_v3.py chain); its steps file gives the STATUS
#   lines in the old order (outcomes_alarm, outcomesRND, menu, card); an Outcomes failure exits 6, the card's rc is the chain's rc
nice -n 10 $PY -B $H/d1_reports_v3.py chain "$F" "$W" "$V" "$LAB_DAYS" "$G" $FIRST $LAST 20250901:$LAST "${LEAN:-FADE}" "${SCREEN:-0}" "${BASE:-}" "$XS" "$EO" "$T/alarm_process/alarm_card_gm1.py" < /dev/null > $W/d1_${V}.log 2>&1; rd=$?
[ $rd -eq 0 ] && [ -f $W/d1_${V}_steps.tsv ] || { st d1 $rd 0 $W/d1_${V}.log; exit 6; }
rc=0; rc2=9
while IFS=$'\t' read -r k r s o; do st $k $r $s $o
  case $k in outcomes*) [ $r -eq 0 ] || exit 6;; card) rc2=$r;; esac; done < $W/d1_${V}_steps.tsv
[ $rc -eq 0 ] && rc=$rc2; st done $rc 0 "$W"; exit $rc
