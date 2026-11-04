# alarm_context: tool card

What was happening around each alarm at the moment we decide: EVENT, MARKET and COIN readings; no outcomes. The code: [alarm_context.py](../05_Profile/tree/tools/alarm_context/alarm_context.py) (QUANT). More: [README](../05_Profile/alarm_context/README.md). STRATEGY's context_tool is a separate released tool.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_context/alarm_context.py build <lab> <code_dir> <events> <subject> <level> <first> <last> [out] [decisions,..] [hist_path]
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_context/alarm_context.py show <6 arguments>
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_context/alarm_context.py catalog
```
- A sealed day counts as REFUSED in the BUILD line (written, up to date, refused); a wrong command prints the tool's text and stops. `catalog` rewrites its catalog file beside the code, so never run it inside an install.
