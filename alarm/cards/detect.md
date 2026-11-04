# detect: tool card

The detection stage of idea_to_grade: a definition file to EVENTS.tsv, the fire list. The code: [detect_v2.py](../01_Detection/tree/team/RESEARCH/tools/idea_to_grade/detect_v2.py) (VERSION DETECT_V1; COUNT runs it). More: [README](../01_Detection/detect/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/tools/idea_to_grade/detect_v2.py --definition <DEF> --roster <ROSTER> --first <F> --last <L> --research-window <F>:<L> --out <OUT> --lab-root <LAB_DAYS> [--coins C | --group G | --group-file F] [--workers 8] [--gate=<FEED_GATE>]
```
- Exit 0 COMPLETE (one JSON line); 2 `REFUSED <CODE>` (e.g. LAB_ROOT_REQUIRED, GATE_NOT_RUN, WORKER_RSS_CAP), nothing committed; 3 FAILED. In the loop use the COUNT job, not this by hand.
