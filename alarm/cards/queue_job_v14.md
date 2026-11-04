# queue_job_v14: tool card

queue_job_v12 (ALARM_V1_16) plus KIND FIRSTLOOK, `--month-job`, `--reader` and `--unsealed-source`; GRADE and MONTH on their V14 templates (V13 plus PERFIRE_SEAL.tsv; chains, pins and outcomes unchanged). COUNT, ENTRY and the rest of GRADE and MONTH are as [queue_job_v12.md](queue_job_v12.md). Status: kept in ALARM_V1_21 (queue_job_v15 is current: v14 plus KIND TRUE, cards/queue_job_v15.md), TEST, NOT REVIEWED.
Code: [queue_job_v14.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v14.py). KIND FIRSTLOOK: [first_look.md](first_look.md).
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v14.py --settings <S> [--job-settings <MAC S>] <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job> [--month-job <MONTH job>] [--reader v11|v12] [--unsealed-source] [--dry]
```
