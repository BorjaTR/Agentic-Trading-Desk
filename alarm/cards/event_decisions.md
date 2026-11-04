# event_decisions: tool card

Here only the shared run check: is a committed run's every file present and at its digest. The code: [run_manifest_candidate.py](../07_Price_path/tree/tools/event_decisions/run_manifest_candidate.py). The Decisions program the folder's [README](../07_Price_path/tree/tools/event_decisions/README.md) describes is not in this folder.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/07_Price_path/tree/tools/event_decisions/run_manifest_candidate.py verify <root> <name> [prefix] [--code-dir D] [--days D1,D2] [--no-inputs]
```
- Exit 0 `VERIFY PASS ...`; 2 `REFUSED ...`; wrong arguments print the tool's text and stop.
