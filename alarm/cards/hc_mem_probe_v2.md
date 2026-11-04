# hc_mem_probe_v2: tool card

Will this definition fit in memory: the hand check on half B of the roster for 20251009..20251016, with its peak, waves and MB per input. The code: [hc_mem_probe_v2.py](../01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_mem_probe_v2.py).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_mem_probe_v2.py --settings <S> <DEF.json> [--limit-mb 732]
```
- Exit 0 PASS; 1 OVER; 2 `REFUSED` (usage, settings, NO ROSTER, NO HAND CHECK, DEFINITION UNREADABLE, no "inputs" object, HAND CHECK FAILED). These days hold the 10 Oct crash: size on a quiet week with hc_size_v1.
