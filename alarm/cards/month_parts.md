# month_parts: tool card

The Sep-Apr grade chain with the detection in coin parts, so no worker hits detect's 2 GiB cap. The MONTH job runs edition v2_2_7. The code: [alarm_grade_chain_v2_2_7_to20260430.sh](../03_Grading/tree/tools/month_parts/alarm_grade_chain_v2_2_7_to20260430.sh). More: [README](../03_Grading/month_parts/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
AL=<INSTALL> PY=<python> LAB_DAYS=<lab days> FEED_GATE=<gate or empty> RESEARCH_STORE=<research days> [PARTS=2..26] [LEAN=..] bash <INSTALL>/03_Grading/tree/tools/month_parts/alarm_grade_chain_v2_2_7_to20260430.sh <V> <DEF> <WORK> [menu]
```
- Exit 2 with BAD_VARIANT, NO_DEFINITION, NO_AL, NO_PY, NO_LAB_DAYS, NO_FEED_GATE, NO_RESEARCH_STORE, NOT_AN_ALARM_FOLDER, CHAIN_OUTSIDE_ALARM, NO_MENU, STATUS_EXISTS, SHA_MISMATCH. Agents queue MONTH (queue_job), never this by hand.
