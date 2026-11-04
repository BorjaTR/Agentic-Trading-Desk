# audit_run_v3: tool card

The scorecard of one kit run: 17 checks, each PASS, WARN or FAIL. The code: [audit_run_v3.py](../Agentic/tree/ALARM_DESIGN/KIT_V5/tools/audit_run_v3.py). Exact commands: [TOOL.json](audit_run_v3.TOOL.json). Every output column: [dictionary](../dictionaries/audit_run_v3_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Reads one run's registers, receipts, files and board, and checks them against the kit rules. Writes nothing unless `--write`.
- The checks:
  - A1 REGISTERS: the 8 registers exist, with the kit's headers, every row full width.
  - A2 CLAIMS: every idea with a variant, job or decision has its claim file.
  - A3 SEALED: each GRADE, ENTRY or MONTH job's variants were registered before it was queued; PREREG and definitions unchanged.
  - A4 BUDGET: at most 3 graded variants an idea. A5 FORECASTS: each MONTH job's Jan-Apr forecasts registered before it was queued.
  - A6 SOURCED: each DECISIONS row equals what decide_v2.py (or decide_forward_v2.py) computes again from the receipts now.
  - A7 PICKUP: each finished job was read (a DECISIONS or POSTMORTEMS row names it) within 20 minutes of its end.
  - A8 DISK: each job wrote no more than its declared WRITES_MB.
  - A9 POSTMORTEM: each decided variant has a POSTMORTEMS row. A10 FINDINGS: each decided idea has ideas/<IDEA>/FINDINGS_<IDEA>.md.
  - A11 BOARD: your board lines start with the stamp, stay under 578 characters, have no em dash; there is a START line.
  - A12 WORDS: no "does not exist" and no em dash in your ideas/ markdown.
  - A13 STUCK: a second failed job of one kind for one idea has a PROBLEMS row and a STUCK board line.
  - A14 LEARN: LEARNINGS_PROPOSED rows are of kind RULE, TOOL, CHECK or SKILL, with their evidence file and sha16.
  - A15 TOOLS: TOOLS_BUILT rows name a tool and a test that exist with their sha16.
  - A16 JOBS: every job twin in RUN/jobs has its RUNS row; your jobs in the queues are all in RUNS.
  - A17 CLEAN: a cleaned GRADE job kept its fire lists; a decided job still uncleaned 60 minutes after its last decision is a WARN; the run's uncleaned scratch over 10,000 MB is a FAIL.

## When to use it
- At every step of a kit run, and always before you hand a run over. It answers: does my run follow the kit rules, and what must I fix?

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/audit_run_v3.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029
```
- Real output, read-only (SCOUT's VM, 30 Oct 2026): 16 checks PASS, `A7 PICKUP WARN (1)` (`20263720_ENTRY_GIVENA: read 21 min after its end`), then `SCORE 16 PASS, 1 WARN, 0 FAIL`.
- Add `--write` to keep the scorecard as RUN/audit/AUDIT_<stamp>.txt.

## What it gives
- Printed (and in the AUDIT file with `--write`):
  - `AUDIT <RUN> (audit_run_v3.py, <stamp>). TEST, NOT REVIEWED.`
  - one line per check: id, name, status, and the count of failures or warnings in brackets; then up to 8 of them, each on a line starting `- `;
  - `COUNTS ideas claimed ..; variants registered ..; jobs ..; decisions (latest per variant) ..; problems ..; learnings proposed ..; uncleaned scratch .. MB; left for DSK (protected store places) .. MB`;
  - `SCORE <n> PASS, <n> WARN, <n> FAIL`.
- With `--write`: `WRITTEN <path> <sha16>`.

## Limits and refusals
- exit 0: the audit ran, whatever it found: read the SCORE line, not the exit code.
- exit 1: `USAGE audit_run_v3.py --settings <settings file> RUN [--write]` (bad usage, no `--settings`), `REFUSED: SETTINGS: ...` (a settings file the reader refuses; RESEARCH_ROOT and BOARD must be set), or `NO RUN FOLDER ...`.
- A check that crashes is reported as `A?` with `audit step failed: ...`; the other checks still run.
- No `--help`: with no arguments it prints its usage (exit 1).

## Where its data comes from
- RESEARCH_ROOT: the run ALARM_DESIGN/runs/<RUN> (registers, receipts, jobs, ideas) and the claims ALARM_DESIGN/runs/IDEAS_CLAIMED.
- BOARD: your board file BOARD/<SEAT>.txt (A11, A13).
- RUNNER_QUEUES: the queues, for A16 (empty: the queues are not read).
- Code, only inside this Alarm folder: decide_v2.py and decide_forward_v2.py beside it (A6).
