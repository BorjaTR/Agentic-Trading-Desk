# hc_mem_probe_v3: tool card

hc_mem_probe_v2 with the limit from the code: WORKER_RSS_CAP (2 GiB) over 1.61, the worst worker per probe MB of seven pairs: 1,272 MB. The code: [hc_mem_probe_v3.py](../01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_mem_probe_v3.py). The rest: [v2](hc_mem_probe_v2.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_mem_probe_v3.py --settings <S> <DEF.json> [--limit-mb MB]
```
- v2's exits and refusals; --limit-mb above the cap is refused. A small sample: a rule past 1.61 can still stop at the cap in COUNT or GRADE.
