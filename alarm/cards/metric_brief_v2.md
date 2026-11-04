# metric_brief_v2: tool card

Read a metric code before it goes in a rule: its meaning, unit, scope, step, window, status, what empty means and what it must never be read as. The code: [metric_brief_v2.py](../01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py). Exact commands: [TOOL.json](metric_brief_v2.TOOL.json). Every output column: [dictionary](../dictionaries/metric_brief_v2_COLUMNS.tsv). Card by SCOUT helper K13, 31 Oct 2026 (R7 F32).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: owner LEAD, edition by SCOUT for the clean release.

## What it does
- Prints one brief per code: a header line, a STOP, RULE or CAUTION line when the status is not PROVEN, the status, then the card's fields (MEANS, UNIT, SCOPE, STEP, WINDOW, MAY USE, FIRST DAY, LAST DAY, CARD) and LAB4's reading rules (EMPTY MEANS, NEVER READ AS, READ IT AS).

## When to use it
- Step 2 METRICS of AGENTS.md: for every code your rule will read, before the claim and before the definition. SCOPE says the op: coin codes with raw, market codes with market (DEF_TEMPLATE_V4.md, The market op).

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env A1.S08 E2.S04
```
- `--family E2` for every code of a family; `--grep "wave age"` for every code whose code, name or meaning holds the words (long).

## What it gives
- printed: a brief (a header line, then LABEL: value lines) (columns: [dictionary](../dictionaries/metric_brief_v2_COLUMNS.tsv))
- A STOP, CAUTION or UNPROVEN code is refused by the detector's gate in a rule.

## Limits and refusals
- exit 0: printed; an unknown code prints a NOT FOUND line and still exits 0: read the output.
- exit 2: refused: a settings file missing or refused, a table missing from this Alarm folder, a run outside an Alarm folder; an unknown option prints the usage.
- It reads METRICS_V1 and METRIC_TRAPS_V3 only: the COUNT job's gate also admits the owner-cleared Hyperliquid codes (X1.HLFLOWX.S08, S09), which it calls NOT FOUND (R7 F35; DEF_TEMPLATE_V4.md, The metric gate).
- LAST DAY is the card's, not where the data ends.

## Where its data comes from
- Four tables inside this Alarm folder, under 01_Detection/tree/team/: METRICS_V1, METRIC_TRAPS_V3 and the CTX and EPI catalogues (the TOOL.json reads). No settings key is read; no market data.
