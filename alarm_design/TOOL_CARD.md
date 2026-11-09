# TOOL CARD: alarm_design ALARM_BUILD_V26 (V26)
The ONE alarm design pack: PROCESS, FLOWCHART, LEARNING_LOOP, START, PROMPT, QUESTIONS, GATES, TOOLS, CHANGES, checks, launchers (history).
- Command (first step): python3 -B <RELEASE_ROOT>/Learning_Loop/run_kit/current/tree/team/SCOUT/pack_kit/run_kit_v3_1/run_kit_v3_1.py kit_new SEAT TASK FOLDER --type ALARM_BUILD --version V26 (then PROCESS_V26.md S2 to S9 and START_V26.md HOW TO LAUNCH).
- Reads: the PROCESS_REGISTER_V1.tsv row ALARM_BUILD (frozen in the run_kit edition). Writes: nothing; a run writes its own folder.
- Windows: design 20250910..20260331; out of sample 20260401..20260731, one look per alarm (holdout_month HOLDOUT_MONTH_V1_1); never seen 20260801..20261130 (refused by name). Yardstick: FDONLY Sep 2025 to Mar 2026: +5.88 at 15 min (t +3.42), +6.87 at 1 h, 1786 waves, 5 of 7 months (team/SCOUT/receipts/20270531_A176_YARD).
- Check, from any folder (not only the forensics root): python3 -B <RELEASE_ROOT>/Learning_Loop/pack_check/current/tree/team/SCOUT/pack_kit/pack_check_v4_1.py <RELEASE_ROOT>/Learning_Loop/pack_template/current/tree/team/SCOUT/pack_kit/PACK_TEMPLATE_V3 <RELEASE_ROOT>/Alarm/alarm_design/ALARM_BUILD_V26 MANIFEST_V26.tsv; route_check_v26; rules_check_v26 --root <forensics> --release <RELEASE_ROOT>; start_paths_check.py START_V26.md --section "HOW TO LAUNCH" (team/SCOUT/loop_day_20261105/v21_current/start_paths_check.py). Results: RELEASE_PACK_CHECKS.txt and the SCO-A183 job receipts.
- Output of a run: $RUN/STEP_01_INPUT.json to $RUN/STEP_22_HANDOFF.json, the ALARM CARD in team/RESEARCH/LEAD/ALARM_CARDS.
- Refusals: pack_check FAIL R1 to R10 lines; route and rules FAIL lines; start_paths_check MISSING lines; rc nonzero. A run: STOP_<nn>_<NAME>.json (STOP OUT_OF_SAMPLE, STOP NEVER_SEEN for closed months).
- Status: RELEASED 2026-11-07, V26 PROVISIONAL, TEST, NOT REVIEWED.

## How to change it
Make V27 in the library, check it, release a new edition through the volat-release skill.
