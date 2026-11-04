# 06 First look: does this moment offer enough movement, and which way

ALARM_V1_21_1.
Run it from the queue only: `queue_job_v15.py S <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job> [--month-job <MONTH job>] [--reader v11|v12] [--dry]`. Card: cards/first_look.md.

| file | what | edition |
|---|---|---|
| tree/tools/alarm_first_look/fl_read_v11.py | the reader; rule 9 in force, waves 30 min | released since V1_1 |
| tree/tools/alarm_first_look/fair_v4.py | the ladder: the bars on made-up alarms; not part of the queue chain | released |
| tree/tools/alarm_first_look/fl_read_v12.py, bar_v1.py | edition 12: `--reader v12`, the chain builds the BAR tables | V1_19; through the queue V1_19_1 |
| FIRSTLOOK_SETTINGS_V1.json | the readers (v11 the default, v12), the tools, the months | V1_19_1 |
| tree/tools/alarm_first_look/fl_lists_v3.py | the two lists of one variant from its PERFIRE, window as an argument | V1_19 (from fl_lists_v2) |
| tree/tools/alarm_first_look/busy_v2.py | how busy each moment was | V1_19 (busy_v1, profile's new place) |
| tree/tools/alarm_first_look/night_export_v4.py | a committed outcome run to one wide table | V1_19 (STRATEGY's night_export_v3, module by path) |
| tree/tools/alarm_first_look/fl_extract_v1.py, OUTCOMES_FIRSTLOOK_V1.json | the first-look columns; the labels | V1_19 (exact copies) |
| tree/tools/alarm_first_look/fl_receipt_v1.py | the receipt row and page | V1_19 (new) |
| ../05_Profile/tree/tools/alarm_profile_v2/alarm_profile_v2_3.py | the move spent | V1_19 (2.2 with the store paths from settings, EDITION still 2.2) |

Outcome labels run with the released event_outcomes_aw1_rel1.py (the feed gate and research days from settings), not aw1.
Not carried over on purpose: fl_jobs_v1, fl_aprof_jobs_v3, fl_grade_jobs_v1 and the JOB_FLOUT, JOB_APROF, JOB_FLGRADE templates (batch makers with hardcoded queues and ~/mnt; one variant runs through JOB_FIRSTLOOK_V1 instead). No batch of many alarms and no list without a GRADE from the queue.
