# inputs_read_v1: tool card

Which metric codes the registry's alarms read, and the OK codes no alarm reads yet, per idea family. The code: [inputs_read_v1.py](../08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/inputs_read_v1.py). Exact commands: [TOOL.json](inputs_read_v1.TOOL.json). Every output column: [dictionary](../dictionaries/inputs_read_v1_COLUMNS.tsv). Settings key: RESEARCH_ROOT.

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Reads each registry alarm's definition (def_rel under ALARM_DESIGN, checked against its def_sha16) and lists the metric codes its inputs name (an input with a code: raw, market, ...).
- Puts beside each code its flag, as metric_brief_v2 words it: OK (a PROVEN status), RULE, CAUTION, STOP (the detector refuses STOP and CAUTION in a decision line), NO ROW (no LAB4 status: refused as UNPROVEN), NOT IN TABLES; and the alarms that read it, their states (the scoreboard's PASS, NEEDS MORE MONTHS, STOP) and families, and how many are FOUND.
- The page: per idea family (FAMILY_TAGS_V1.tsv, SCOUT's classification), the codes its alarms read with each alarm's state, and the OK codes no alarm reads in the same groups; then, per group, every OK code no alarm reads. A group is the part before the code's station: A1.S01 and A1.S07.grid_off are A1, X1.LIQX.S01 is X1.LIQX.

## When to use it
- Step 1 IDEA of the loop (AGENTS.md): read your family's section of REGISTRY/INPUTS_READ_V1.md before you pick the input. Round 7 (31 Oct): picking the input was 6.8 of 17 and 10.5 of 22 minutes, because no page said which inputs no alarm reads.
- SCOUT runs it after each registry build (registry_build_v2, then scoreboard_v2, then this).

## Run it
```
python3 -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/inputs_read_v1.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env
```
- `--registry` (default REGISTRY/ALARM_REGISTRY_V1.tsv), `--tags` (default REGISTRY/FAMILY_TAGS_V1.tsv), `--out` (default REGISTRY/INPUTS_READ_V1.tsv), `--page` (default REGISTRY/INPUTS_READ_V1.md). Relative paths are under RESEARCH_ROOT/ALARM_DESIGN, from any working folder.
- Real run (SCOUT's VM, 31 Oct 2026, a copy of release ALARM_V1_2 with this tool): `WROTE REGISTRY/INPUTS_READ_V1.tsv aba5f6853115f17f codes 4055 read 67; WROTE REGISTRY/INPUTS_READ_V1.md bbcc746a76bec6d0` (109 definitions read; 737 OK codes, 65 of them read by an alarm).

## What it gives
- `--out`: one row per code (the dictionary). `--page`: the page above. A file that exists is twinned first (<file>.pre_SCOUT_<stamp>).
- Printed: `WROTE <out> <sha16> codes <n> read <n>; WROTE <page> <sha16>`.

## Limits and refusals
- exit 0: written.
- exit 2: `REFUSED: <reason>` on stderr: no `--settings`, a settings file the reader refuses (RESEARCH_ROOT empty among them), an `--out` or `--page` inside the Alarm package, this file outside an Alarm package, a missing metric table or metric_brief_v2.py.
- exit 1: `USAGE: ...` for an unknown argument.
- A definition that is missing, changed since its decision (sha16 not the recorded one) or no JSON is counted on the page and skipped: its codes are never counted. Desk triggers have no definition.
- It reads the codes a definition names, not how it reads them: a code an alarm reads can still hold a new moment; the card must say why.

## Where its data comes from
- RESEARCH_ROOT: ALARM_DESIGN/REGISTRY (ALARM_REGISTRY_V1.tsv, FAMILY_TAGS_V1.tsv) and the definitions under ALARM_DESIGN/runs.
- Code and tables: only this Alarm folder (novelty_v2.py and scoreboard_v2.py beside it; metric_brief_v2.py and its four tables in 01_Detection/tree).
