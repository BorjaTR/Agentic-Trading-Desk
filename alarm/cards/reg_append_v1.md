# reg_append_v1: tool card

Appends one row to a run register; the stamp comes from the clock; never rewrites. The code: [reg_append_v1.py](../Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/reg_append_v1.py). Status in the code: TEST, NOT REVIEWED.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/reg_append_v1.py <RUN_DIR> <REGISTER> <FIELDS.json | ->
```
- Stops with a message, nonzero exit: USAGE, NO REGISTER, BAD HEADER, EMPTY ROW, UNKNOWN COLUMNS, THE STAMP COMES FROM THE CLOCK, TAB OR NEWLINE IN, EM DASH IN. REGISTER is the name without .tsv (THOUGHTS, VARIANTS, FORECASTS). Missing columns are written empty.
