# alarm_profile: tool card

What each liquidation alarm's episode looked like at the alarm, and named groupings over those values; each value with its proof status. The code: [alarm_profile.py](../05_Profile/tree/tools/alarm_profile/alarm_profile.py) (edition 1, QUANT). More: [README](../05_Profile/alarm_profile/README.md). First look's job uses edition 2.2: see alarm_profile_v2/TOOL_CARD.md in 05_Profile/tree/tools.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_profile/alarm_profile.py build <lab> <code_dir> <alarms> <subject> <first> <last> [out]
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_profile/alarm_profile.py profile <out> <code_dir> <subject> <first> <last> <name> [2 more]
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_profile/alarm_profile.py profiles
python3 -B <INSTALL>/05_Profile/tree/tools/alarm_profile/alarm_profile.py status [metrics]
```
- Also `show` and `catalog` (`catalog` writes beside the code: never inside an install). A sealed day counts as REFUSED in the BUILD line; a wrong command prints the tool's text and stops.
