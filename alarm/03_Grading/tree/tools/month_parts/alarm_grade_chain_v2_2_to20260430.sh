#!/bin/bash
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
CARD_SHA=a616c4378a02852b; DET_SHA=482a4a1eaf1faff5; I2G_SHA=a98936da5aaf93b4; PINS_SHA=c0c523ed00403f58; EO_SHA=76adc225ef3bc102; REL_SHA=7ca10b08f1254a69; WIN_SHA=69c3327ebf4e15a1
V=$1; DEF=$2; W=$3
[[ "$V" =~ ^[A-Za-z0-9]+$ ]] || { echo "BAD_VARIANT $V"; exit 2; }
[ -f "$DEF" ] || { echo "NO_DEFINITION $DEF"; exit 2; }
PY=<PYTHON>; F=<LAB_REPO>/forensics; R=$F/team/RESEARCH
T=$R/tools; L2=$R/LEAD/loop2; ROSTER=$F/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
G=${4:-$T/alarm_process/OUTCOMES_MENU_ALARM_V1.json}; [ -f "$G" ] || { echo "NO_MENU $G"; exit 2; }
export METRIC_TRAPS=$L2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv CATALOGS=$T/alarm_context/CTX_CATALOG_V1.tsv:$T/alarm_profile/EPI_CATALOG_V1.tsv:$F/team/LAB3/METRICS_HL_ADD_V1.tsv:$L2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv
export W PYTHONDONTWRITEBYTECODE=1
mkdir -p "$W" || exit 2; S=$W/STATUS_${V}.tsv; [ -f "$S" ] && { echo "STATUS_EXISTS $S (variant already run here)"; exit 2; }
printf 'step\trc\tseconds\tout\tutc\n' > "$S"; st(){ printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date -u +%FT%TZ)" >> "$S"; }
AP=$T/alarm_process; DET=$AP/detect_aw1.py; I2G=$AP/idea_to_grade_aw1.py; EO=$AP/event_outcomes_aw1.py
ckf(){ [ "$(shasum -a 256 $AP/$1 | cut -c1-16)" = "$2" ] || { echo "SHA_MISMATCH $1"; exit 2; }; }
ckf alarm_card_v1_3.py $CARD_SHA; ckf detect_aw1.py $DET_SHA; ckf idea_to_grade_aw1.py $I2G_SHA; ckf I2G_PINS_AW1.json $PINS_SHA
ckf event_outcomes_aw1.py $EO_SHA; ckf RELEASE_event_outcomes_AW1.json $REL_SHA; ckf WINDOWS_ALARM_V1.tsv $WIN_SHA
printf 'chain\t%s\t%s\nwindow\t%s\t%s\ncard\t%s\t%s\ninput\t%s\t%s\nmenu\t%s\t%s\nbase\t%s\n' "$(shasum -a 256 $0 | cut -c1-16)" "$0" "$FIRST" "$LAST" "$CARD_SHA" "$AP/alarm_card_v1_3.py" "$(shasum -a 256 $DEF | cut -c1-16)" "$DEF" "$(shasum -a 256 $G | cut -c1-16)" "$G" "${BASE:-none} lean ${LEAN:-FADE} screen ${SCREEN:-0}" > "$W/INPUTS_${V}.txt"
printf 'windows\t%s\t%s\ndetect\t%s\t%s\ngrade\t%s\t%s\npins\t%s\t%s\noutcomes\t%s\t%s\nrelease\t%s\t%s\n' "$WIN_SHA" "$AP/WINDOWS_ALARM_V1.tsv" "$DET_SHA" "$DET" "$I2G_SHA" "$I2G" "$PINS_SHA" "$AP/I2G_PINS_AW1.json" "$EO_SHA" "$EO" "$REL_SHA" "$AP/RELEASE_event_outcomes_AW1.json" >> "$W/INPUTS_${V}.txt"
D=$W/det_${V}_v1; LIST=$W/${V}_FIRES_V1_LIST.tsv
if [[ "$DEF" == *.tsv ]]; then
  [ "$(head -1 "$DEF" | cut -f1-3)" = "$(printf 'coin\tt\tside')" ] || { st list 2 0 "LIST_HEADER $DEF"; exit 3; }
  cp -n "$DEF" "$LIST"; st list_given 0 0 "$DEF"
else
# 1 detect in PARTS parts (roster order, contiguous slices), merged, rows sorted by t then coin
NP=${PARTS:-26}; [[ "$NP" =~ ^([2-9]|1[0-9]|2[0-6])$ ]] || { st detect 2 0 "BAD_PARTS $NP (2 to 26)"; exit 2; }
LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z); PL=""
for i in $(seq 0 $((NP-1))); do t0=$(date +%s); h=${LET[$i]}; PL="$PL $h"
  C=$($PY -c "import json,sys;c=json.load(open(sys.argv[1]))['coins'];n,i=int(sys.argv[2]),int(sys.argv[3]);k=len(c);print(','.join(c[i*k//n:(i+1)*k//n]))" $ROSTER $NP $i)
  [ -n "$C" ] || { st detect_$h 2 0 "EMPTY_PART $i of $NP"; exit 3; }
  nice -n 10 $PY -B $DET --definition "$DEF" --roster $ROSTER --coins $C --first $FIRST --last $LAST --research-window 20250901:$LAST --out ${D}_$h --workers 3 > ${D}_$h.log 2>&1; rc=$?
  st detect_$h $rc $(( $(date +%s)-t0 )) ${D}_$h; [ $rc -eq 0 ] && [ -f ${D}_$h/EVENTS.tsv ] || exit 3; done
mkdir -p $D && { grep '^#' ${D}_A/EVENTS.tsv; echo "# merged by alarm_grade_chain_v2_2_to20260430.sh: det_A to det_$h ($NP roster parts), rows sorted by t then coin"
  grep -v '^#' ${D}_A/EVENTS.tsv | head -1
  { for h in $PL; do grep -v '^#' ${D}_$h/EVENTS.tsv | tail -n +2; done; } | sort -t$'\t' -k2,2n -k1,1; } > $D/EVENTS.tsv
grep -v '^#' $D/EVENTS.tsv > $LIST
fi
N=$(( $(grep -c . $LIST) - 1 )); st list 0 0 "$LIST ($N fires)"; [ $N -gt 0 ] || exit 3
if [ "${SCREEN:-0}" = 1 ]; then XS="ALARM"; st screen 0 0 "no grading, no random"; else XS="ALARM RND"
# 3 grade from the list
SH=$(shasum -a 256 $LIST | cut -c1-16); t0=$(date +%s)
nice -n 10 $PY -B $I2G --events $LIST --events-sha16 $SH --roster $ROSTER --coins ALL --first $FIRST --last $LAST --research-window 20250901:$LAST --out $W/gradeL_${V}_v1 --workers 1 > $W/gradeL_${V}_v1.log 2>&1; rc=$?
st grade $rc $(( $(date +%s)-t0 )) $W/gradeL_${V}_v1; [ $rc -eq 0 ] || exit 4
# 4 matched random (own moments out, 3 per fire)
t0=$(date +%s); nice -n 10 $PY -B $L2/make_random_v3.py $W/gradeL_${V}_v1 $LIST $W/RND_${V}_V1 3 > $W/RND_${V}_V1.log 2>&1; rc=$?
st random $rc $(( $(date +%s)-t0 )) $W/RND_${V}_V1_LIST.tsv; [ $rc -eq 0 ] || exit 5
fi
# 5 Outcomes on the alarm list and the random list (honest cost)
for y in $XS; do t0=$(date +%s); if [ $y = ALARM ]; then x=""; IN=$LIST; else x=RND; IN=$W/RND_${V}_V1_LIST.tsv; fi
  nice -n 10 $PY -B $EO run 0 <DATA_ROOT>/lab_days $F/team/LAB3/code $IN $G IDEA2${V}${x}MENU $FIRST $LAST $W/om_${V}${x}_v1 --run-window 20250901:$LAST > $W/om_${V}${x}_v1.log 2>&1; rc=$?
  st outcomes${x:-_alarm} $rc $(( $(date +%s)-t0 )) $W/om_${V}${x}_v1; [ $rc -eq 0 ] || exit 6; done
# 6 the menu (LEAD's reader)
if [ "${SCREEN:-0}" != 1 ]; then t0=$(date +%s); $PY -B $L2/menu_v2.py $V om > $W/MENU_${V}_om.txt 2>&1; rcm=$?; st menu $rcm $(( $(date +%s)-t0 )) $W/MENU_${V}_om.txt; fi
# 7 the alarm card (races, reach, checks; with BASE the paired read and the random subsets of the base)
t0=$(date +%s); $PY -B $AP/alarm_card_v1_3.py $W $V ${BASE:+--base $BASE} --lean ${LEAN:-FADE} $([ "${SCREEN:-0}" = 1 ] && echo --screen) --tsv $W/SUM_${V}.tsv > $W/CARD_${V}.txt 2>&1; rc2=$?
st card $rc2 $(( $(date +%s)-t0 )) $W/CARD_${V}.txt
[ $rc -eq 0 ] && rc=$rc2; st done $rc 0 "$W"; exit $rc
