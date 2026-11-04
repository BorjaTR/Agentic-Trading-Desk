# board_line_v2: tool card

Posts one line on your board, checked against the board rules. The code: [board_line_v2.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/board_line_v2.py). Exact commands: [TOOL.json](board_line_v2.TOOL.json). Every output column: [dictionary](../dictionaries/board_line_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Appends one line `<UTC stamp> <SEAT> <KIND> <text>` to your board file BOARD/<SEAT>.txt. The stamp comes from the clock; the seat from the run tag.
- Twins the whole board first (BOARD/<SEAT>.txt.pre_<RUN>_<stamp>; `_2`, `_3` for two lines in one second). Never deletes.

## When to use it
- At every step of a kit run: START, CLAIM, COUNT, PREREG, JOB, DECISION, STUCK, ASK, ANSWER, CHECKPOINT, DONE, NOTE.
- It answers: how do I post a board line that passes the rules (stamp first, under 578 characters, no em dash)?

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/board_line_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 DECISION "GIVENB GB1: STOP (decide_v2.py): R1 missed, 1 of 4 months (receipts/20263709_GRADE_GIVENB/HANDOFF/REAL_SEALED/REAL_RULES_GB1.tsv c0627b7443ac9fd1)"
```
- The text says what, with its files and sha16 (the example is AD1's real decision of 29 Oct, as it would be posted now).
- There is no dry mode: every call that passes the checks posts. Try a line with care.

## What it gives
- One line appended to BOARD/<SEAT>.txt (its fields: the dictionary), and the board's twin.
- Printed: `POSTED <board file> <n> chars`.

## Limits and refusals
- exit 0: posted.
- exit 2: refused, `REFUSED: <reason>` on stderr, nothing posted: bad usage; no `--settings`; BOARD empty in the settings; a bad run tag; a KIND not in the list; a tab, newline or em dash in the text; a text under 10 characters; a line of 578 characters or more.
- No `--help`: with no arguments it prints `REFUSED: USAGE board_line_v2.py ...` (exit 2).

## Where its data comes from
- BOARD: the team board folder (hb), one <SEAT>.txt per seat.
- Nothing else is read.
