# queue_job_v16: tool card

queue_job_v15 (5f4ea462e06373df), loaded byte for byte from beside it and run as it is, plus the menu gate at SEAL ([menu_gate_v1](menu_gate_v1.md)), nothing else. Released in ALARM_V1_21_16 (ALARM_V1_21_15 held, never current); TEST, NOT REVIEWED. Every kind, item, option, template, size and refusal is queue_job_v15's ([queue_job_v15.md](queue_job_v15.md)).
Code: [queue_job_v16.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v16.py).
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v16.py --settings <S> <RUN> <KIND> <IDEA> <ITEMS> [the options of queue_job_v15] [--dry]
```
- After every queue_job_v15 check passed for a sealed variant (GRADE, TRUE, ENTRY, MONTH, FIRSTLOOK; COUNT is not gated: nothing is sealed yet) and before any job is filled or a number claimed: the variant's sealed definition, card and VARIANTS reason, and for TRUE the claim given (for GRADE every ideas/<IDEA>/TRUE_<V>_*.json already written), go through menu_gate_v1. A pickable NO code with no named exception: `REFUSED: MENU GATE <V>: MENU_NOT_PICKABLE: ...` and a NEXT line; nothing is written or claimed.
- The gate's lines (MENU GATE, MENU EXCEPTION, MENU NOTE) print before queue_job_v15's own output. For a variant the gate admits, the job text, the twin and the RUNS row are queue_job_v15's byte for byte (test_menu_gate_v1 KEEP_Fdaoi).
- Refused at start: `queue_job_v15.py MISSING OR CHANGED` when the file beside it is not 5f4ea462e06373df.
