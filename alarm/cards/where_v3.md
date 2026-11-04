# where_v3: tool card

Find a metric or value code by its code, its name or words of its meaning, in the metric tables of this Alarm folder. The code: [where_v3.py](../01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py). Exact commands: [TOOL.json](where_v3.TOOL.json). Every output column: [dictionary](../dictionaries/where_v3_COLUMNS.tsv). Card by SCOUT helper K13, 31 Oct 2026 (R7 F32).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: owner LAB1, edition by SCOUT for the clean release.

## What it does
- Searches METRICS_V1, the HL candidates, the register METRICS_V2 (its DROPPED rows and the HL readings the others lack) and the value catalogues CTX, EPI, STAMP, FEED and LIVELAYER; prints the best hits, one per code.
- Each hit: the kind and the code, the owner and the table, the card path, what it is and how to read it.

## When to use it
- Step 2 METRICS of AGENTS.md, before the claim: to find which code says what your idea needs. Then read every hit with metric_brief_v2 before it goes in a rule.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env "long liquidations" --kind metric --n 50
```
- `--kind metric` for metric codes, `--kind code` for value codes, none for both; `--n 50` to see more than 5 hits; the words are one argument.

## What it gives
- printed: one hit (three lines) (columns: [dictionary](../dictionaries/where_v3_COLUMNS.tsv))
- printed: NOT FOUND line (columns: [dictionary](../dictionaries/where_v3_COLUMNS.tsv))
- A hit is a pointer, not a reading: its status (STOP, CAUTION) and how the detector's gate treats it come from metric_brief_v2 and DEF_TEMPLATE_V4.md (The metric gate).

## Limits and refusals
- exit 0: hits printed.
- exit 1: NOT FOUND: no table holds the words; the line names the tables searched.
- exit 2: refused: no words (it prints its usage), --check (that is where_v2's), a settings file missing or refused, a metric table missing from this Alarm folder.
- It prints only --n hits (5 by default) and no word when more exist (R7 F15); DROPPED rows may come first (R7 F07).

## Where its data comes from
- Only the metric tables inside this Alarm folder, under 01_Detection/tree/team/ (listed in the TOOL.json reads). No settings key is read; no market data.
