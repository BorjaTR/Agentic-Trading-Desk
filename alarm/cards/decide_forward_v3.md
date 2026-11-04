# decide_forward_v3: tool card

The decision of a forward-only variant, from its MONTH job receipts only. The code: [decide_forward_v3.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_forward_v3.py). Exact commands: [TOOL.json](decide_forward_v3.TOOL.json). Every output column: [dictionary](../dictionaries/decide_forward_v3_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- When a STOP showed the OTHER side winning, that side is sealed as a new variant (same definition, other lean, VARIANTS reason `FORWARD ONLY OF <V0>`) and tested on Jan-Apr 2026 only, never graded on Sep-Dec again.
- This tool labels that variant from its MONTH job (month_read_v3 reads, one per month 2601 to 2604):
  - FORWARD PASS: HELD or STRONGER in 3 or more of the 4 months. FORWARD STOP: otherwise.
  - INSUFFICIENT: fewer than 3 months could be read (a month with under 30 waves is NO READ). INVALID: a month stage failed or a read is missing.
- The parent's Sep-Dec numbers are not used: that side was read after the grade, so they are no test.

## When to use it
- Step 9 MONTH of the loop (ALARM_PIPELINE_V1 section 1), for a forward-only variant, after its MONTH job ended.
- It answers: did the other side of a STOP hold forward, on Jan-Apr?

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_forward_v3.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD5_20261029 PACECOOL PC3R --month 20264006_MONTH_PACECOOL
```
- Real output, read-only (SCOUT's VM, 30 Oct 2026): `DECISION PACECOOL PC3R: FORWARD STOP | months read 4, holding 0 | 2601 BROKE (15m +1.9, 1h -1.5, 279 waves); ...; parent PC3 STOP 2026-10-29T18:49:24Z`.
- Add `--write` once to record it.

## What it gives
- Printed: `DECISION <IDEA> <V>: <label> | months read .., holding .. | <per month: verdict (15m gap, 1h gap, waves)>; parent <V0> STOP <stamp>`, then `SOURCES`.
- With `--write`: one row of RUN/registers/DECISIONS.tsv (the same 26 columns as decide_v3; most are `-` here), then `WRITTEN ...`.

## Limits and refusals
- exit 0: decided (printed; written too with `--write`).
- exit 2: refused, `REFUSED: <reason>` on stderr: bad usage or names; no `--settings`; the variant not in VARIANTS or not forward-only; its parent not a STOP; `--month` not a MONTH job of the idea, or without the variant; reg_append_v1.py changed; the same decision already written.
- No `--help`: with no arguments it prints `REFUSED: USAGE decide_forward_v3.py ...` (exit 2).

## Where its data comes from
- RESEARCH_ROOT: the run ALARM_DESIGN/runs/<RUN>: registers/VARIANTS.tsv and DECISIONS.tsv; receipts/<MONTH>/STAGES.tsv and MONTH_READ_<V>_<2601..2604>.txt.
- Code, only inside this Alarm folder: reg_append_v1.py (pinned by sha16).
