# alarm_process: tool card

The Sep-Dec grade chain and its report steps; the GRADE job runs edition v2_0_7. The code: [alarm_grade_chain_v2_0_7_to20251231.sh](../03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_7_to20251231.sh), [d1_reports_v3.py](../03_Grading/tree/tools/alarm_process/d1_reports_v3.py), [d1_mem_v2.py](../03_Grading/tree/tools/alarm_process/d1_mem_v2.py) (a library). The grader and detector it calls are under 01_Detection/tree/team/RESEARCH/tools/alarm_process.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
AL=<INSTALL> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate or empty> RESEARCH_STORE=<research days> [LEAN=..] bash <INSTALL>/03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_7_to20251231.sh <V> <DEF> <WORK> [menu]
```
- Exit 2 with the refusals of month_parts (BAD_VARIANT, NO_DEFINITION, NO_<KEY>, NOT_AN_ALARM_FOLDER, CHAIN_OUTSIDE_ALARM, NO_MENU, SHA_MISMATCH); d1_reports_v3 NO_WINDOWS. Agents queue GRADE (queue_job), never this by hand.
