# alarm_stamp: tool card

After each alarm, entered at a decision time, how much heat came before each offer. An outcome, known only after the hold: never context. The code: [alarm_stamp.py](../07_Price_path/tree/tools/alarm_stamp/alarm_stamp.py) (QUANT). More: its [README](../07_Price_path/tree/tools/alarm_stamp/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/07_Price_path/tree/tools/alarm_stamp/alarm_stamp.py build <lab> <code_dir> <efill> <eladder> <events> <subject> <FADE|FOLLOW> <first> <last> [out] [decisions,..]
python3 -B <INSTALL>/07_Price_path/tree/tools/alarm_stamp/alarm_stamp.py show <6 arguments>
python3 -B <INSTALL>/07_Price_path/tree/tools/alarm_stamp/alarm_stamp.py catalog
```
- A sealed day counts as REFUSED in the BUILD line; a wrong command prints the tool's text and stops. `catalog` writes beside the code: never inside an install.
