# novelty_v2: tool card

Is a fire list a new alarm, a copy, a mirror, or a known trigger given a side? The code: [novelty_v2.py](../08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v2.py). Exact commands: [TOOL.json](novelty_v2.TOOL.json). Every output column: [dictionary](../dictionaries/novelty_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Compares one fire list with every alarm of the registry that has a fire list on dev (SYNTHETIC rows never), and prints the 3 nearest and a verdict.
- Its measures, against each registry alarm:
  - same fires: the share of this list's fires (same coin and t) that are that alarm's fires;
  - same side: the share that are its fires with the same trading side (only when both have a side); other side: with the other side (its mirror);
  - waves near: the share of this list's waves with a fire of that alarm within 1800 s of the wave; baseline: what waves near reads for a list with no link to it.
- A wave: a fire more than 1800 s after the previous fire of any coin starts a new one. Rows with the same fires and lean are one group, named by its PASS row.
- The verdict, in this order: COPY (same side 50 pct or more of a sided alarm), NEW SIDE (same fires 50 pct or more of a trigger with no side: a desk trigger), MIRROR (other side 50 pct or more), NEAR (any of these 40 pct or more), NEW (all under 40 pct).

## When to use it
- Step 8 NOVELTY of the loop (ALARM_PIPELINE_V1 section 1), before you call an idea new, and before a second idea on the same input and moment.
- It answers: is this alarm new, or does the registry already hold it (or its mirror)?

## Run it
```
python3 -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env runs/AD1_20261029/receipts/20263757_GRADE_FORCEDBREAK/FB5_FIRES_V1_LIST.tsv --lean FADE --self AD1_FORCEDBREAK
```
- Real output, read-only (SCOUT's VM, 30 Oct 2026): `... lean FADE: 2843 fires, 897 waves; against 107 registry alarms ...`, nearest 1 `KNOWN_N1APR ... same fires 14.7 pct, same side 14.6 pct ...`, then `VERDICT NEW: every overlap under 40 pct`.
- FIRE_LIST: a tab file with `coin`, `t` (whole epoch seconds) and, when the alarm has one, `side` (1 or -1), as a GRADE job writes <V>_FIRES_V1_LIST.tsv. A relative path is under RESEARCH_ROOT/ALARM_DESIGN.
- `--lean FADE|FOLLOW`: the trading side (the fire's side times -1 for FADE, times 1 for FOLLOW). Without it, same fires stand in for same side and the verdict says so.
- `--registry`: another registry (default REGISTRY/ALARM_REGISTRY_V1.tsv). `--self <SEAT>_<IDEA>`: leave out that idea's own rows.

## What it gives
- Printed, nothing written:
  - `NOVELTY <list> (sha16 ..), lean ..: <n> fires, <n> waves; against <n> registry alarms (<registry> sha16 ..)`;
  - `nearest 1..3: <alarm> (<kind>, <state>, lean ..): same fires .. pct, same side .. pct, other side .. pct; waves near .. pct (its baseline .. pct)`;
  - `VERDICT <COPY|NEW SIDE|MIRROR|NEAR|NEW> ...` with its basis.
- Every field: the dictionary.

## Limits and refusals
- exit 0: compared.
- exit 2: refused, `REFUSED: <reason>` on stderr: no `--settings` (or twice), a settings file the reader refuses, RESEARCH_ROOT empty, a lean other than FADE or FOLLOW, a file without `coin` and `t` columns or without fire rows, a `t` or `side` that is not a whole number, a registry without its columns, this file outside an Alarm package.
- No `--help`: with no arguments it prints `REFUSED: --settings <file> IS NEEDED ONCE ...` (exit 2).

## Where its data comes from
- RESEARCH_ROOT: ALARM_DESIGN (the registry REGISTRY/ALARM_REGISTRY_V1.tsv, the fire lists its rows name in `fire_list_rel`, and a relative FIRE_LIST).
- Code: only this Alarm folder (its settings reader).
