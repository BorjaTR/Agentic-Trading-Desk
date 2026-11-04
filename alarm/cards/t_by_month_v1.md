# t_by_month_v1: tool card

Lead and day-clustered t per month and horizon. A sign of spread, never a pass: the pass rule stays the decide tool's pooled t. The code: [t_by_month_v1.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/t_by_month_v1.py).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/t_by_month_v1.py (--wave-leads F | --perfire F --lean FADE|FOLLOW [--edges EDGES.tsv]) [--real REAL.tsv] [--last YYYYMMDD]
```
- Exit 2 `REFUSED:` NO FILE, NO <X> COLUMN, BAD ROW, NOT AN EDGES FILE, --perfire NEEDS --lean, --last IS NOT A DAY, GIVE ONE OF. --real alone prints lead and waves with no t. --perfire is an approximation: random by month.
