# hc_size_v1: tool card

How many waves a definition will give a month, before COUNT: the hand check on the full roster for a quiet week (20251110-17) and the probe week. The code: [hc_size_v1.py](../01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_size_v1.py).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_size_v1.py --settings <S> <DEF.json>
```
- Exit 0 done; 2 `REFUSED` (usage, settings, NO ROSTER, NO HAND CHECK, DEFINITION UNREADABLE, HAND CHECK FAILED). Prints one SIZE line a week and a HINT under 30 waves a month on the quiet week; fire lists and logs go to a fresh temp folder. Reads no outcome.
