#!/bin/bash
# alarm_grade_chain_v2_2_6_to20260430.sh (SCOUT, 31 Oct 2026, V2_0 stage 2 D1; TEST, NOT REVIEWED): alarm_grade_chain_v2_2_5_to20260430.sh
# 7e99c6c084469162 with only steps 5-7 changed (the owner 31 Oct 2026 13:34 Berlin: GRADE and MONTH under 60 s; team/SCOUT/D1_BUILD_PLAN_V1.md): ONE
# process, d1_reports_v2.py chain, runs both Outcomes runs (event_outcomes_aw1_rel1 run(0), each in its own process, its rows kept as they are
# written, beside the root as <root>.mem.pkl), then the menu and the card (alarm_card_v1_3_1) in its process from those rows (event_outcomes.read
# answered from memory, checked against the store's subject, days and coins); step 0 job 20265186: 338 of 338 columns equal, the
# reports byte for byte. The STATUS lines come from its steps file in the old order; an Outcomes failure exits 6 as before. The rest
# of this header is the parent's:
# alarm_grade_chain_v2_2_5_to20260430.sh (SCOUT, 31 Oct 2026, V2_0 stage 1; TEST, NOT REVIEWED): alarm_grade_chain_v2_2_4_to20260430.sh
# 756c52a6a515bf1c with only the order of steps 5-7 changed (the owner 31 Oct 2026 12:37 Berlin: "agents need to run tools as fast as
# possible"; team/SCOUT/SPEED_V2_0_DESIGN_V1.md Q1, Q2): the Outcomes runs on the alarm and the random lists work at the same time
# (two roots, no shared write), then the menu and the card at the same time (both only read the two roots). Each waits for its own
# process; the STATUS lines are written after the waits, in v2_2_4's order; on a failure every started run ends first, then the
# first failure in v2_2_4's order exits with v2_2_4's code. The tools, their arguments, inputs and outputs are v2_2_4's.
# The rest of this header is v2_2_4's:
# alarm_grade_chain_v2_2_4_to20260430.sh (SCOUT K16, 31 Oct 2026, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_2_3_to20260430.sh 5895b8034a46b55d with only the detection (step 1) changed (K16 T6; SCOUT 31 Oct, with the fixes
# of the reviews REV1 and REV2): the part count is the chain's rule, never the job's: 2 parts, or 26 up front for a SERIAL_FORCED
# definition (detect_aw1_rel1.py's own parallel_mode: one process for all days; LG4's halves, see v2_2's header below); a part the
# detector refuses with WORKER_RSS_CAP is re-split alone into new folders, its own folder kept and never merged; a coin census before
# the merge; the merge sorts with LC_ALL=C; DETECT_PARTS_<V>.tsv names every try and the STATUS rows detect_plan, resplit_<part> and
# census say which way it went. Why: job 20264959 (team/SCOUT/receipts/20264959_K16PROF): MONTH's 26 parts took 93 s, 2 parts 11 + 12 s
# (x1, with a merge typed for that test: the same fire list, 01b21824046afc8d); a 2-part tree peaked at 3,355,115,520 bytes (x1
# DETECT_RUN_B.json sum_peak_rss_bytes; its workers 0.96 to 1.25 GB, under the 2 GiB cap). Detection is per coin, so the fire list does
# not depend on the parts (v2_2's header). INPUTS_<V>.txt is unchanged. The rest of this header is v2_2_3's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [PARTS=2..26] [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_4_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_2_3_to20260430.sh (SCOUT K12, 31 Oct 2026, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_2_2_to20260430.sh dd8859721c66b4ed with only Outcomes (step 5) changed (SCOUT 31 Oct: "take the feed-gate dev
# path out of GRADE and MONTH"): event_outcomes_aw1_rel1.py (60da1138b40b24c0: event_outcomes_aw1.py with the feed's stop gate from
# FEED_GATE, never labcore.jobgate's built-in dev-tree GATE, and the research days from RESEARCH_STORE; run 0 as before) with its
# release record RELEASE_event_outcomes_AW1_REL1.json (d137f9c224e34bac); both checked by sha16 and named in INPUTS_<V>.txt, which also gets a
# research line; the caller gives RESEARCH_STORE (the settings key: an absolute path) as it gives FEED_GATE, and the chain exports
# both to Outcomes. The rest of this header is v2_2_2's.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> RESEARCH_STORE=<research days> [PARTS=2..26] [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_3_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_2_2_to20260430.sh (SCOUT 31 Oct 2026, K12, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_2_1_to20260430.sh 2c7adbe6921e6cf9 (SCOUT K4, 30 Oct) with only the aw1 grader and detector changed to their clean
# editions (CLEAN_RELEASE_V1; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only"). Why: from the
# install, idea_to_grade_aw1.py refuses UNPINNED_MODULE as idea_to_grade.py did in GRADE job 20264797 (its pins I2G_PINS_AW1.json name the
# dev tree's absolute paths; its code loads its kernels from the dev tree). Changed, nothing else:
#   step 1: detect_aw1_rel1.py (b1894b3bade40fa2: detect_v2 with detect_aw1's window classes) with --gate="$FEED_GATE";
#   step 3: idea_to_grade_aw1_rel1.py (f1e881d598ae8155: idea_to_grade_rel1 with idea_to_grade_aw1's changes) with --gate="$FEED_GATE" and
#           --pins I2G_PINS_AW1_REL1.json (9faa1dc1f753a47a: the same 39 files as I2G_PINS_AW1.json, the clean editions in place of the old,
#           paths relative to the tree);
#   the caller gives FEED_GATE in the environment (the settings key FEED_GATE; set and empty: no gate, a machine without the feed);
#   METRICS_V1 is exported beside METRIC_TRAPS and CATALOGS (the lab tree's team/LAB3/METRICS_V1.tsv: the detector's metric gate read the
#   dev tree's by its built-in default); INPUTS_<V>.txt names the new files and appends one gate line.
# Parts, window, steps, other tools, arguments and outputs otherwise unchanged. v2_2_1's header follows.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate file or empty> [PARTS=2..26] [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_2_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_2_1_to20260430.sh (SCOUT 30 Oct 2026, K4, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED):
# alarm_grade_chain_v2_2_to20260430.sh 64b42a022bb8e3bd (SCOUT 29 Oct, released) with only its paths changed (CLEAN_RELEASE_V1; the owner
# 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only"): the caller gives AL, PY and LAB_DAYS in the
# environment (below); every step tool and table comes from the lab tree <AL>/01_Detection/tree (the dev layout), never the dev tree;
# the lab days go to detect_aw1, the grade and Outcomes as an argument (detect_aw1 and idea_to_grade_aw1 had the Mac's as their
# built-in default); matched random, the menu and the card are the paths-only editions make_random_v3_1, menu_v2_1 and
# alarm_card_v1_3_1 (alarm_process). Parts, window, steps, arguments and outputs otherwise unchanged (the merged EVENTS.tsv note still
# names v2_2: detection output byte-equal). v2_2's header follows.
#   AL=<Alarm> PY=<python> LAB_DAYS=<lab days> [PARTS=2..26] [LEAN=..] [BASE=..] [SCREEN=1] bash alarm_grade_chain_v2_2_1_to20260430.sh <V> <DEF.json|FIRES.tsv> <W> [MENU.json]
# alarm_grade_chain_v2_2_to20260430.sh (SCOUT 29 Oct 2026, home team/RESEARCH/tools/month_parts; TEST, NOT REVIEWED): v2_1_to20260430
# with ONE change: the detection runs in PARTS coin parts (env PARTS, 2 to 26, default 26; contiguous slices of the roster in roster
# order: PARTS=2 gives v2_1's two halves exactly), merged the same way. Why: over Sep-Apr detect_aw1.py hit its 2 GiB WORKER_RSS_CAP for
# AD13 LIQGAP LG4 (MONTH 20264053: REFUSED WORKER_RSS_CAP 2147991552 bytes; 20264064: 2149875712). LG4 is SERIAL_FORCED (one process
# for all days); its Sep-Dec halves peaked at 1565130752 and 1531199488 bytes (GRADE 20264037 DETECT_RUN.json, read before its CLEAN).
# Review 1 (29 Oct): memory = a per-day index cache (about 6.6 MB a day for any coin list) + a share that grows with the coins; parts
# cut only the coin share: estimated peaks for LG4 over Sep-Apr: a half 2.3 GB, a quarter 1.85 GiB, an eighth 1.7 GiB. Detection is per
# coin, so the fire list does not depend on the parts. Measured on the Mac (smoke jobs 20264080, 20264081): over Sep-Apr an eighth
# peaked 1.81 to 1.89 GiB and part F was refused (2150924288 bytes); 1 or 2 coins peaked 1.57 to 1.65 GiB: hence 26 parts of 2 coins.
# Everything else is v2_1, unchanged. v2_1's header follows.
# alarm_grade_chain_v2_1_to20260430.sh, aw1 (STRATEGY 28 Oct 2026, ALARM_DESIGN kit; TEST, NOT REVIEWED; the owner 28 Oct 2026: Mar-May for the alarm agents only): v2_0_to20260228 with LAST=20260430 and the alarm window tools: detect_aw1.py,
# idea_to_grade_aw1.py, event_outcomes_aw1.py (run 0, in this process) read WINDOWS_ALARM_V1.tsv (BUILD to 31 May 2026); card v1_3. Each file is
# checked by sha16 below; INPUTS_<V>.txt names them. The team table WINDOWS_V1 and every release are unchanged.
# alarm_grade_chain_v2_0_to20260228.sh (STRATEGY 28 Oct 2026; ALARM_DESIGN KIT_V2; TEST, NOT REVIEWED): v1_3 with a HARDCODED date range, FIRST and LAST below
# (detect, grade, matched random and Outcomes read 20250910..20260228 only, research window 20250901:20260228), the card v1_2 (its own
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
set -uo pipefail
FIRST=20250910; LAST=20260430   # this version's hardcoded date range (UTC days): never a setting
D1_SHA=aae457889f5075ad; MEM_SHA=3cd95039ba6e1a70   # V2_0 stage 2 D1: d1_reports_v2.py and d1_mem_v2.py, in ../alarm_process
CARD_SHA=3c496708f9d44651; DET_SHA=932bd2957cd3592d; I2G_SHA=d50d277f44aad95f; PINS_SHA=82a0d10372bbe744; EO_SHA=fc1fb81710a44342; REL_SHA=8780a3b9000a322b; WIN_SHA=69c3327ebf4e15a1
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
AP=$T/alarm_process; DET=$AP/detect_aw1_rel1.py; I2G=$AP/idea_to_grade_aw1_rel1.py; EO=$AP/event_outcomes_aw1_rel1.py; PINS=$AP/I2G_PINS_AW1_REL1.json
ckf(){ [ "$(shasum -a 256 $AP/$1 | cut -c1-16)" = "$2" ] || { echo "SHA_MISMATCH $1"; exit 2; }; }
ckf alarm_card_v1_3_1.py $CARD_SHA; ckf detect_aw1_rel1.py $DET_SHA; ckf idea_to_grade_aw1_rel1.py $I2G_SHA; ckf I2G_PINS_AW1_REL1.json $PINS_SHA
ckf event_outcomes_aw1_rel1.py $EO_SHA; ckf RELEASE_event_outcomes_AW1_REL1.json $REL_SHA; ckf WINDOWS_ALARM_V1.tsv $WIN_SHA
H=$(cd "$(dirname "$0")/../alarm_process" && pwd -P)
for x in d1_reports_v2.py:$D1_SHA d1_mem_v2.py:$MEM_SHA; do [ "$(shasum -a 256 $H/${x%%:*} | cut -c1-16)" = "${x##*:}" ] || { echo "SHA_MISMATCH ${x%%:*}"; exit 2; }; done
printf 'chain\t%s\t%s\nwindow\t%s\t%s\ncard\t%s\t%s\ninput\t%s\t%s\nmenu\t%s\t%s\nbase\t%s\n' "$(shasum -a 256 $0 | cut -c1-16)" "$0" "$FIRST" "$LAST" "$CARD_SHA" "$AP/alarm_card_v1_3_1.py" "$(shasum -a 256 $DEF | cut -c1-16)" "$DEF" "$(shasum -a 256 $G | cut -c1-16)" "$G" "${BASE:-none} lean ${LEAN:-FADE} screen ${SCREEN:-0}" > "$W/INPUTS_${V}.txt"
printf 'windows\t%s\t%s\ndetect\t%s\t%s\ngrade\t%s\t%s\npins\t%s\t%s\noutcomes\t%s\t%s\nrelease\t%s\t%s\n' "$WIN_SHA" "$AP/WINDOWS_ALARM_V1.tsv" "$DET_SHA" "$DET" "$I2G_SHA" "$I2G" "$PINS_SHA" "$PINS" "$EO_SHA" "$EO" "$REL_SHA" "$AP/RELEASE_event_outcomes_AW1_REL1.json" >> "$W/INPUTS_${V}.txt"
printf 'gate\t%s\n' "${FEED_GATE:-none}" >> "$W/INPUTS_${V}.txt"
printf 'research\t%s\n' "$RESEARCH_STORE" >> "$W/INPUTS_${V}.txt"
printf 'd1\t%s\t%s\nd1mem\t%s\t%s\n' "$D1_SHA" "$H/d1_reports_v2.py" "$MEM_SHA" "$H/d1_mem_v2.py" >> "$W/INPUTS_${V}.txt"
D=$W/det_${V}_v1; LIST=$W/${V}_FIRES_V1_LIST.tsv
if [[ "$DEF" == *.tsv ]]; then
  [ "$(head -1 "$DEF" | cut -f1-3)" = "$(printf 'coin\tt\tside')" ] || { st list 2 0 "LIST_HEADER $DEF"; exit 3; }
  cp -n "$DEF" "$LIST"; st list_given 0 0 "$DEF"
else
# 1 detect (K16 T6, v2_2_4): the part count is the chain's rule, never the job's. detect_aw1_rel1.py's own parallel_mode on this
#   definition: SERIAL_FORCED (one process for all days) takes 26 parts up front, any other mode 2 parts; PARTS=2..26 in the environment
#   overrides the rule (tests and reruns; JOB_MONTH_V9 passes PARTS empty). Parts are contiguous slices of the roster in roster order. A
#   part the detector refuses with WORKER_RSS_CAP (rc 2, the log line 'REFUSED WORKER_RSS_CAP: ...') is re-split, alone, into new folders
#   <part>1 to <part>k (k: its coins over the 26-part slice, rounded up); its own folder and log are kept and never merged. Any other
#   failure, a re-split part that fails, or a part refused at the 26-part size stops the chain (exit 3), as v2_2_3 did. DETECT_PARTS_<V>.tsv
#   has a row per try (part, folder, rc, n_coins, use, coins). Before the merge, a coin census: every merged part is a COMPLETE run, their
#   coin lists are disjoint, their union is the roster, and every fire's coin is in its part's list. The merge sorts with LC_ALL=C.
NF=26; LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z); PT=$W/DETECT_PARTS_${V}.tsv
MODE=$($PY -B -c "import importlib.util as u,sys;s=u.spec_from_file_location('detect_aw1_rel1_mode',sys.argv[1]);m=u.module_from_spec(s);s.loader.exec_module(m);print(m.parallel_mode(m.load_definition(sys.argv[2])[0])[0])" $DET "$DEF" 2> $W/detect_mode_${V}.log); rc=$?
[ $rc -eq 0 ] && [ -n "$MODE" ] || { st detect_plan 2 0 "MODE_UNREADABLE $DEF: $(tail -n 1 $W/detect_mode_${V}.log | cut -c1-160)"; exit 3; }
if [ -n "${PARTS:-}" ]; then NP=$PARTS; WHY="PARTS=$PARTS from the caller (parallel_mode $MODE)"
elif [ "$MODE" = SERIAL_FORCED ]; then NP=$NF; WHY="SERIAL_FORCED (detect_aw1_rel1 parallel_mode): $NF parts up front"
else NP=2; WHY="parallel_mode $MODE"; fi
[[ "$NP" =~ ^([2-9]|1[0-9]|2[0-6])$ ]] || { st detect_plan 2 0 "BAD_PARTS $NP (2 to 26)"; exit 2; }
st detect_plan 0 0 "$NP parts: $WHY"
ALLC=$($PY -c "import json,sys;print(','.join(json.load(open(sys.argv[1]))['coins']))" $ROSTER); NALL=$(echo "$ALLC" | tr ',' '\n' | grep -c .)
slice(){ $PY -c "import sys;c=sys.argv[1].split(',');n,i=int(sys.argv[2]),int(sys.argv[3]);k=len(c);print(','.join(c[i*k//n:(i+1)*k//n]))" "$1" $2 $3; }
ncoins(){ echo "$1" | tr ',' '\n' | grep -c .; }
row(){ printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$1" "${D}_$1" "$2" "$(ncoins "$4")" "$3" "$4" >> $PT; }
try(){ local t0; t0=$(date +%s)
  nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $2 --first $FIRST --last $LAST --research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$1 --workers 3 > ${D}_$1.log 2>&1; TRC=$?
  st detect_$1 $TRC $(( $(date +%s)-t0 )) ${D}_$1; [ $TRC -ne 0 ] || [ -f ${D}_$1/EVENTS.tsv ] || TRC=3; }
cap(){ [ $TRC -eq 2 ] && grep -q '^REFUSED WORKER_RSS_CAP:' ${D}_$1.log; }
printf 'part\tfolder\trc\tn_coins\tuse\tcoins\n' > $PT
for i in $(seq 0 $((NP-1))); do h=${LET[$i]}; C=$(slice "$ALLC" $NP $i)
  [ -n "$C" ] || { st detect_$h 2 0 "EMPTY_PART $i of $NP"; exit 3; }
  try $h $C; [ $TRC -eq 0 ] && { row $h 0 merged $C; continue; }
  n=$(ncoins $C); k=$(( (n * NF + NALL - 1) / NALL ))
  cap $h || { row $h $TRC failed $C; exit 3; }
  [ $k -ge 2 ] || { row $h $TRC failed $C; st resplit_$h 2 0 "WORKER_RSS_CAP in part $h ($n coins) at the 26-part size: no finer split"; exit 3; }
  row $h $TRC refused_kept_unmerged $C
  st resplit_$h 0 0 "WORKER_RSS_CAP in part $h ($n coins): ${D}_$h kept, never merged; re-split into $k parts ${h}1 to ${h}$k"
  for j in $(seq 1 $k); do hh=$h$j; CC=$(slice $C $k $((j-1)))
    [ -n "$CC" ] || { st detect_$hh 2 0 "EMPTY_PART $j of $k (part $h)"; exit 3; }
    try $hh $CC; [ $TRC -eq 0 ] || { row $hh $TRC failed $CC; exit 3; }
    row $hh 0 merged $CC; done
done
# the coin census of the merged parts, then the merge (rows sorted by t then coin, LC_ALL=C)
$PY -B - $PT "$ALLC" > $W/census_${V}.txt 2>&1 <<'CENSUS'
import csv, json, os, sys
rows = [r for r in csv.DictReader(open(sys.argv[1]), delimiter='\t') if r['use'] == 'merged']
roster = sys.argv[2].split(','); seen = {}; bad = []
for r in rows:
    own = r['coins'].split(',')
    for c in own:
        if c in seen:
            bad.append('coin %s in parts %s and %s' % (c, seen[c], r['part']))
        seen[c] = r['part']
    run = os.path.join(r['folder'], 'DETECT_RUN.json')
    if not os.path.isfile(run) or json.load(open(run)).get('status') != 'COMPLETE':
        bad.append('part %s is not a COMPLETE run' % r['part']); continue
    own = set(own); hdr = None
    for line in open(os.path.join(r['folder'], 'EVENTS.tsv')):
        if line.startswith('#'):
            continue
        f = line.rstrip('\n').split('\t')
        if hdr is None:
            hdr = f
            if 'coin' not in hdr:
                bad.append('part %s: no coin column' % r['part']); break
            ci = hdr.index('coin'); continue
        if f[ci] not in own:
            bad.append('a fire of coin %s in part %s' % (f[ci], r['part'])); break
miss = [c for c in roster if c not in seen]; extra = sorted(set(seen) - set(roster))
if miss:
    bad.append('in no merged part: ' + ','.join(miss[:5]))
if extra:
    bad.append('not in the roster: ' + ','.join(extra[:5]))
if not rows:
    bad.append('no merged part')
print('CENSUS_FAILED ' + '; '.join(bad[:5]) if bad else '%d coins in %d merged parts: COMPLETE, disjoint, their union is the roster, every fire in its part' % (len(seen), len(rows)))
sys.exit(1 if bad else 0)
CENSUS
rc=$?; st census $rc 0 "$(tail -n 1 $W/census_${V}.txt | cut -c1-300)"; [ $rc -eq 0 ] || exit 3
ML=$(tail -n +2 $PT | awk -F'\t' '$5=="merged"{printf "%s ", $1}'); P1=${ML%% *}
mkdir -p $D && { grep '^#' ${D}_$P1/EVENTS.tsv; echo "# merged by alarm_grade_chain_v2_2_4_to20260430.sh: parts ${ML}(DETECT_PARTS_${V}.tsv, $NP planned), rows sorted by t then coin (LC_ALL=C)"
  grep -v '^#' ${D}_$P1/EVENTS.tsv | head -1
  { for h in $ML; do grep -v '^#' ${D}_$h/EVENTS.tsv | tail -n +2; done; } | LC_ALL=C sort -t$'\t' -k2,2n -k1,1; } > $D/EVENTS.tsv
grep -v '^#' $D/EVENTS.tsv > $LIST
fi
N=$(( $(grep -c . $LIST) - 1 )); st list 0 0 "$LIST ($N fires)"; [ $N -gt 0 ] || exit 3
if [ "${SCREEN:-0}" = 1 ]; then XS="ALARM"; st screen 0 0 "no grading, no random"; else XS="ALARM RND"
# 3 grade from the list
SH=$(shasum -a 256 $LIST | cut -c1-16); t0=$(date +%s)
nice -n 10 $PY -B $I2G --events $LIST --events-sha16 $SH --roster $ROSTER --coins ALL --first $FIRST --last $LAST --research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins $PINS --out $W/gradeL_${V}_v1 --workers 1 > $W/gradeL_${V}_v1.log 2>&1; rc=$?
st grade $rc $(( $(date +%s)-t0 )) $W/gradeL_${V}_v1; [ $rc -eq 0 ] || exit 4
# 4 matched random (own moments out, 3 per fire)
t0=$(date +%s); nice -n 10 $PY -B $AP/make_random_v3_1.py $W/gradeL_${V}_v1 $LIST $W/RND_${V}_V1 3 > $W/RND_${V}_V1.log 2>&1; rc=$?
st random $rc $(( $(date +%s)-t0 )) $W/RND_${V}_V1_LIST.tsv; [ $rc -eq 0 ] || exit 5
fi
# 5-7 (V2_0 stage 2 D1): ONE process from Outcomes to the menu and the card (d1_reports_v2.py chain); its steps file gives the STATUS
#   lines in the old order (outcomes_alarm, outcomesRND, menu, card); an Outcomes failure exits 6, the card's rc is the chain's rc
nice -n 10 $PY -B $H/d1_reports_v2.py chain "$F" "$W" "$V" "$LAB_DAYS" "$G" $FIRST $LAST 20250901:$LAST "${LEAN:-FADE}" "${SCREEN:-0}" "${BASE:-}" "$XS" "$EO" "$AP/alarm_card_v1_3_1.py" < /dev/null > $W/d1_${V}.log 2>&1; rd=$?
[ $rd -eq 0 ] && [ -f $W/d1_${V}_steps.tsv ] || { st d1 $rd 0 $W/d1_${V}.log; exit 6; }
rc=0; rc2=9
while IFS=$'\t' read -r k r s o; do st $k $r $s $o
  case $k in outcomes*) [ $r -eq 0 ] || exit 6;; card) rc2=$r;; esac; done < $W/d1_${V}_steps.tsv
[ $rc -eq 0 ] && rc=$rc2; st done $rc 0 "$W"; exit $rc
