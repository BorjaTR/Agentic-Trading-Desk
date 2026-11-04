# ledger_add_v7: tool card

The tries ledger's writer for the Alarm kit: ledger_add_v5 (team/RESEARCH/tools/ledger, a8039ae0f4f23e31) made ready to ship. Released in ALARM_V1_21 (V1_21 fixes, run SCOUTR12_20261103); TEST, NOT REVIEWED.
Why: on the real ledger v5 refused every call with `ValueError: malformed or duplicate ledger row` (a traceback, no line): TRIES_LEDGER_V1.tsv line 513 repeats ask_id SCOUT-RECUT of line 512 (another writer's status rows, 1 Nov 2026). With no working tool, agents wrote ledger_row=NOT_RECORDED, which add_row accepts.
Code: [ledger_add_v7.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/ledger_add_v7.py).
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/ledger_add_v7.py --settings <S> prereg <idea> <purpose> <setting file> [<days_from> <days_to>]
python3 -B ... ledger_add_v7.py --settings <S> result <ask_id> <result file> PASS|FAIL|UNSURE|KILL <setting file>
python3 -B ... ledger_add_v7.py --settings <S> withdraw <ask_id> <reason> | count <idea> | check | has <ask_id>
```
- The ledger is <RESEARCH_ROOT>/TRIES_LEDGER_V1.tsv of the settings file. prereg, result, withdraw and count keep v5's rules (v5's test suite passes on v7).
- A row with the wrong number of fields or a bad stamp refuses every call: `REFUSED MALFORMED_LEDGER: <file> line <n> ...`. A repeated ask_id of this tool's own (PREREG_<idea>_<stamp>, _R, _W) refuses: DUPLICATE_OWN_ID. A repeated ask_id of another writer is a WARN line on stderr, naming both lines, and the call goes on (this tool never looks those rows up).
- `check`: every fault, exit 0 none, 3 warnings only, 2 malformed. `has <ask_id>`: exit 0 FOUND, 3 NOT FOUND (use it before a TRIED row's ledger_row).
- Every refusal is one line `REFUSED <CODE>: why` on stderr, exit 2, never a traceback. `door` is refused (DOOR_NOT_IN_KIT: it runs ledger_add_v2, not in the kit).
