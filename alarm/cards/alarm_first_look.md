# alarm_first_look: tool card

The folder of the first look reader and its job's steps: does this moment offer enough movement, and which way, against equally busy random moments. Use and read it through [first_look.md](first_look.md), the card of the job. The folder: [alarm_first_look](../06_First_look/tree/tools/alarm_first_look). More: [README](../06_First_look/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v14.py --settings <S> <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job> [--month-job <MONTH job>] --dry
# the reader, by hand, only on existing inputs:
python3 -B <INSTALL>/06_First_look/tree/tools/alarm_first_look/fl_read_v11.py <TARGETS> <H> <costs> <out> <result dirs...>
# the ladder of made-up alarms:
python3 -B <INSTALL>/06_First_look/tree/tools/alarm_first_look/fair_v4.py [--codes A,B] [--plant-seeds N] <TARGETS> <H> <costs> <out> <seeds> <plants> <result dirs...>
```
- Reader and ladder: exit 2 `REFUSED` with OUT EXISTS, JOB NOT FINISHED (a result folder whose STAGES.tsv has no `end 0`), and for the ladder SETTINGS and CODES NOT IN TARGETS. A failed run publishes no number. The queue's refusals: first_look.md. The reader in force is a setting, 06_First_look/FIRSTLOOK_SETTINGS_V1.json.
