# idea_to_grade: tool card

STRATEGY's grader, V3.2: after an alarm's fires, how often and how fast the price moves your way, the heat first, against matched moments. It describes opportunity, not money. The code: [idea_to_grade_v3_2.py](../07_Price_path/tree/tools/idea_to_grade/idea_to_grade_v3_2.py). The ENTRY job uses the kit's own editions. More: [README](../07_Price_path/idea_to_grade/README.md), [SCOPE](../07_Price_path/idea_to_grade/SCOPE.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/07_Price_path/tree/tools/idea_to_grade/idea_to_grade_v3_2.py (--idea I | --events E --events-sha16 S | --detect-run R) --roster <ROSTER> --first <F> --last <L> --out <OUT> --delay-s <seconds> --ledger-ask <ask id> --alarm-id <registry id> [--lab-root L] [--costs C] [--registry R]
```
- Argument errors stop through argparse (exactly one input; --events needs --events-sha16; --roster needed). Exit 2 `REFUSED <CODE>`, `REFUSED DETECT_<CODE>`. Some defaults are machine paths: pass --lab-root, --costs, --registry, --ledger, --pins off the Mac; each default was not checked for this card.
