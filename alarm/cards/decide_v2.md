# decide_v2: tool card

The decision of one graded variant, from its job receipts only. The code: [decide_v2.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v2.py). Exact commands: [TOOL.json](decide_v2.TOOL.json). Every output column: [dictionary](../dictionaries/decide_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Gives one graded variant its label, from the receipts of its GRADE job (and its ENTRY job when needed). No market data is read.
- The labels:
  - PASS: R2 passed. NEEDS MORE MONTHS: R1 passed, R2 missed. STOP: R1 missed.
  - INSUFFICIENT: fewer than 3 counted months (a counted month has 30+ waves on Sep-Dec): the study cannot be read.
  - INVALID: the grade or hand-off failed, a receipt is missing, or the hand-off's status or gate is not OK.
  - NO ENTRY: R1 passed but its ENTRY job would need more than the run's disk budget, so it can never run.
- R1: the LEAD +3 in at least 2 of every 3 counted months, at 15 min or 1 h. R2: R1 and a t of at least 3.
- CLEAR (the price path, from STRATEGY's markout at wait 0, 15 min or 1 h: Sep-Dec 95 pct range above 0 and both halves above 0) is printed beside the label and never changes it.

## When to use it
- Step 7 DECIDE of the loop (ALARM_PIPELINE_V1 section 1): after the GRADE job ended; for a variant whose hand-off R1 passed, after its ENTRY job too.
- It answers: what label does this variant get, and is its price path CLEAR?
- Run it without `--write` to read it; add `--write` once to record it.

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 FORCEDBREAK FB5 --grade 20263757_GRADE_FORCEDBREAK --entry 20263767_ENTRY_FORCEDBREAK
```
- Real output, read-only (SCOUT's VM, 30 Oct 2026): `DECISION FORCEDBREAK FB5: PASS | R1 PASS R2 PASS | LEAD 15m +7.63 (t +2.79) 1h +9.96 (t +3.42) | waves 830, months counted 4 passing 3 | CLEAR CLEAR ret_15m,ret_1h | price gate PASS (15 of 18) | ...`
- A variant without R1 needs no `--entry`: `... AD1_20261029 GIVENB GB1 --grade 20263709_GRADE_GIVENB` printed `DECISION GIVENB GB1: STOP | R1 no R2 no | ...`.
- `--entry-too-big`: records NO ENTRY for a variant with R1 whose ENTRY job cannot fit the disk budget (refused when it fits).
- `--write`: appends the DECISIONS row (refused when the same decision is already the latest one).

## What it gives
- Printed: `DECISION <IDEA> <V>: <label> | R1 .. R2 .. | LEAD 15m .. (t ..) 1h .. (t ..) | waves .., months counted .. passing .. | CLEAR .. .. | price gate .. | TOUGH 15m .. 1h .. | money TT .. RR .. | <note>`, then `SOURCES` (every receipt read, with its sha16).
- With `--write`: one row of RUN/registers/DECISIONS.tsv (26 columns), then `WRITTEN <stamp> DECISIONS`.
- Every column: the dictionary. TOUGH and money are read from the markout files; what they measure is not documented in the code.

## Limits and refusals
- exit 0: decided (printed; written too with `--write`).
- exit 2: refused, `REFUSED: <reason>` on stderr:
  - bad usage or names; no `--settings`; the variant not in VARIANTS; `--grade` not a GRADE job of the idea; no receipts, or no end line;
  - the variant not graded in that job; a variant with R1 and no `--entry` ("run its ENTRY job first"); `--entry-too-big` when its ENTRY fits;
  - read_stratentry_v1.py or reg_append_v1.py changed; the same decision already written.
- No `--help`: with no arguments it prints `REFUSED: USAGE decide_v2.py ...` (exit 2).
- `--entry-too-big` reads the run disk budget (`RUN_BUDGET_MB`) from queue_job_v5.py beside this file.

## Where its data comes from
- RESEARCH_ROOT: the run ALARM_DESIGN/runs/<RUN>:
  - registers/VARIANTS.tsv (the lean) and registers/DECISIONS.tsv (for `--write`);
  - receipts/<GRADE>/: STAGES.tsv, HANDOFF/SUMMARY.tsv, HANDOFF/REAL_SEALED/REAL_RULES_<V>.tsv and REAL_<V>.tsv;
  - receipts/<ENTRY>/: STAGES.tsv and <V>/MARKOUT/CURVE.tsv, GATES.json, TABLE_W0.tsv.
- Code, only inside this Alarm folder: reg_append_v1.py and read_stratentry_v1.py (Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools, each pinned by sha16).
