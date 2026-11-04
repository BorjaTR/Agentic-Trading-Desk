# event_profile: tool card

PROFILE V2: the profile of any alarm from settings alone: which metrics, operator, entity, onset rule. The code: [event_profile.py](../07_Price_path/tree/tools/event_profile/event_profile.py) with clock_series.py (STRATEGY/LEAD). Not the same as alarm_profile.
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/07_Price_path/tree/tools/event_profile/event_profile.py check <alarms> <settings> <subject> <first> <last> [--coins C] [--window W]
python3 -B <INSTALL>/07_Price_path/tree/tools/event_profile/event_profile.py build <lab> <code_dir> <alarms> <settings> <subject> <first> <last> <out> [--coins C] [--report R] [--window W]
python3 -B <INSTALL>/07_Price_path/tree/tools/event_profile/event_profile.py show <out> <code_dir> <subject> <first> <last>
```
- Exit 2 `REFUSED <CODE>: <reason>` for an input, law, integrity or look-ahead refusal; nothing written. Commands past `show`: not read for this card.
