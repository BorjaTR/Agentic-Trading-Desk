# settings_v1: tool card

Reads a machine's settings file, for every tool of the package. KEY=VALUE text, only the keys of settings/SETTINGS_EXAMPLE.env, absolute paths outside the Alarm folder. The code: [settings_v1.py](../_tools/settings_v1.py).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/_tools/settings_v1.py check <settings file> [KEY,...]
python3 -B <INSTALL>/_tools/settings_v1.py get <settings file> KEY
```
- `check`: exit 0 all OK, 3 some MISSING or EMPTY, 2 refused. `get`: exit 2 refused or the key empty. Refusals: NO SETTINGS FILE, NOT KEY=VALUE, KEY TWICE, KEYS MISSING, UNKNOWN KEYS, NOT AN ABSOLUTE PATH, DATA INSIDE ALARM, NO SUCH KEY, EMPTY, NOT INSIDE AN ALARM PACKAGE.
