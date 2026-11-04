# decide_v5: tool card

decide_v4 with one change: a variant with R1 is decided without its ENTRY job. Released in ALARM_V1_21 (V1_21 fixes, run SCOUTR12_20261103); TEST, NOT REVIEWED. The code: [decide_v5.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v5.py). The rest: [decide_v4](decide_v4.md), [decide_v3](decide_v3.md).
Why: decide_v4 refused `V1 HAS R1: run its ENTRY job first`, forcing a money job before the label, while the launch prompt says alarms are never judged on money. The state never used ENTRY: it comes from the GRADE hand-off alone (R1, R2, counted months). ENTRY fills only clear, clear_at, price_gate, tough_15m, tough_1h, money_tt, money_rr.
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v5.py --settings <S> <RUN> <IDEA> <V> --grade <GRADE job> [--entry <ENTRY job> | --entry-too-big] [--write]
```
- Without --entry: the same state as with it; the money columns are `-` and the note ends `money not read (no --entry): money is information only, the strategy stage`. With --entry: as decide_v4 (a second DECISIONS row with the entry job is allowed).
- No pass rule changed: INVALID, INSUFFICIENT, STOP, NEEDS MORE MONTHS, PASS and NO ENTRY are decide_v4's (test KEEP_PassRules: 12 cases equal). MONTH still needs a PASS or NEEDS MORE MONTHS row, which this writes.
- audit_run_v5 recomputes these rows in A6 with decide_v5 (audit_run_v4's A6 used decide_v2, which refuses a row without ENTRY).
