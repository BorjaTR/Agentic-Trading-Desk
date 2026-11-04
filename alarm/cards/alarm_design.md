# alarm_design: tool card

The lab engine: an alarm written as a definition file, its fires on a window, and its truth card. The code: [alarm_design_v3.py](../01_Detection/tree/team/RESEARCH/tools/alarm_design/alarm_design_v3.py) (v2's rules, the lab days from the caller; release V3_8_1). More: [README](../01_Detection/alarm_design/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/tools/alarm_design/alarm_design_v3.py run <def.json> <first> <last> <out_root> <receipt dir> <lab_days>
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/tools/alarm_design/alarm_design_v3.py card <def.json> <out_root> <receipt dir> <ledger> ...
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/tools/alarm_design/alarm_design_v3.py try <def.json> <ledger> [note]
```
- Stops with a message (SystemExit) on: no lab days; a sealed day; a window outside the definition; 23:30-00:15Z (no runs); a catalog that differs from the definition; `card` without the one tries ledger or its PREREG row; `try` when a try row exists. Agents do not call it by hand: the loop's hand check and detect use its engine.
