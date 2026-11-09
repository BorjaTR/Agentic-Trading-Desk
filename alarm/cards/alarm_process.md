# alarm_process: tool card

The Sep-Dec grade chain and its report steps; the GRADE job runs edition v2_0_7. The code: [alarm_grade_chain_v2_0_7_to20251231.sh](../03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_7_to20251231.sh), [d1_reports_v3.py](../03_Grading/tree/tools/alarm_process/d1_reports_v3.py), [d1_mem_v2.py](../03_Grading/tree/tools/alarm_process/d1_mem_v2.py) (a library). The grader and detector it calls are under 01_Detection/tree/team/RESEARCH/tools/alarm_process.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
AL=<INSTALL> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate or empty> RESEARCH_STORE=<research days> [LEAN=..] bash <INSTALL>/03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_7_to20251231.sh <V> <DEF> <WORK> [menu]
```
- Exit 2 with the refusals of month_parts (BAD_VARIANT, NO_DEFINITION, NO_<KEY>, NOT_AN_ALARM_FOLDER, CHAIN_OUTSIDE_ALARM, NO_MENU, SHA_MISMATCH); d1_reports_v3 NO_WINDOWS. Agents queue GRADE (queue_job), never this by hand.

## The fast chain v2_0_10 (ALARM_V1_21_16_6)
```
AL=<INSTALL> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate or empty> RESEARCH_STORE=<research days> [LEAN=..] [GRADE_WORKERS=8] [D1_EO_WORKERS=ALARM=3,RND=5] bash <INSTALL>/03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_10_to20251231.sh <V> <DEF> <WORK> [menu]
```
- Refusals as v2_0_7, plus exit 8 with STATUS gate MISSING <file> when FEED_GATE names no file; D1_EO_WORKERS outside 0 to 8: exit 2 before any run.
- STATUS_<V>.tsv first row is the gate: FOUND <file> <first word>, NONE, or MISSING.
- Workers and the core budget (v2_0_10, as v2_0_8 plus the admission of GPT SCO-A162-REV1 B1, B2 and REV2): detect 3 workers per half (as v2_0_7); grade idea_to_grade_gm1 --workers ${GRADE_WORKERS:-8} (was 1); Outcomes run(3) for the alarm list and run(5) for the random list side by side (8 processes; was two run(0)); menu and card read the committed Outcomes store (no .mem.pkl for a run(n) root). The job declares CORES 8 (the Mac has 15; the live feed keeps at least 4) and MEM_MB 16000 (tree peak 5.2 GB on a month for grade 8 workers). Measured, WIDEBLOCKS V1 Sep-Dec: the chain 408 s -> 128 s (jobs 20270124 and 20270269); every content output byte-equal (MENU, CARD, SUM, PERFIRE, the lists, HANDOFF, 221 of 221 Outcomes parts by cmp_parts_v2, job 20270270's COMPARE); only times, run ids, pids, memory and worker telemetry, paths, job ids and their seals differ.
