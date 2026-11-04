# decide_v6: tool card

decide_v5 (7ce12d2845ad746b), loaded byte for byte from beside it and run as it is, plus the menu exceptions printed on the decision, nothing else. Released in ALARM_V1_21_16 (ALARM_V1_21_15 held, never current); TEST, NOT REVIEWED. The state, the DECISIONS row and the exit code are decide_v5's ([decide_v5.md](decide_v5.md)).
Code: [decide_v6.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v6.py).
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v6.py --settings <S> <RUN> <IDEA> <V> --grade <GRADE job> [--entry <ENTRY job> | --entry-too-big] [--write]
```
- After decide_v5's DECISION and SOURCES lines: the menu gate of the sealed variant (its definition, card, VARIANTS reason, and each ideas/<IDEA>/TRUE_<V>_*.json): `MENU GATE ... OK`, one `MENU EXCEPTION <code> (<status>): <reason>` per named exception, or `MENU GATE ...: REFUSED ... (printed only; the decision above stands)` for a variant sealed before ALARM_V1_21_15.
- The menu lines are made before decide_v5 runs (it may write its DECISIONS row); any fault in them (a malformed claim, a missing file) is a printed line, `MENU GATE ...: REFUSED <CODE> ...` or `MENU GATE: NOT READ (...)`, never an exit: after a written decision the exit is decide_v5's, with exactly one row (GPT V12115-TOOL item 2).
- decide_v5's output is a byte prefix of decide_v6's and the DECISIONS rows are equal (test_menu_gate_v1 KEEP_Fdaoi). audit_run_v5 and the desk grade recompute with decide_v5, unchanged.
