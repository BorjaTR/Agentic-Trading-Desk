# Crypto Alarm Desk: desk reference (V2)

The desk steps, commands, checks and folders. The front page is README.md; paths below are from the repo top.

A desk for designing and testing **alarms** on crypto perpetual futures: a rule that fires at a moment when some traders must trade, then
a fixed, sealed procedure that counts it, grades it against matched random moments, asks whether the claimed event is really there, and
writes a decision that an audit can recompute. Read CLAIMS.md before you read any result: an alarm is not a strategy and nothing here
claims money.

Status: **V1 draft, not released.** What runs and what does not is in STATUS.md (kept current) and at the end of this page.

## What is in the folder
| folder | what it is |
|---|---|
| `alarm/` | the alarm engine, a copy of a released edition (ALARM_V1_21_16) with the lab's own material left out and machine paths replaced (desk/build). Start inside it with `alarm/AGENTS.md`: it names every step and tool. |
| `desk/desk.py` | the one command of the desk (local mode, standard Python only) |
| `desk/local_alloc.py` | the job number allocator of local mode |
| `desk/data/` | the data side: the test sample manifest and its checker; a public-data downloader (not used in V1) |
| `desk/build/` | how `alarm/` was made, and the checks that prove it (copy, scrub, path scan, judge parity, known tests) |
| `desk/tests/` | the desk's own tests |
| `loop/` | the learning loop: one row format for every stage, the lessons it starts with, and its scripts |
| `plugin/` | the Claude Code plugin: skills (alarm-desk, learning-loop, desk-setup), commands `/new-alarm` and `/desk-setup`, the `alarm-reviewer` agent (plugin/README.md); `.claude-plugin/marketplace.json` lists it |
| `settings/desk.env.example` | the one settings file to copy |
| `out/`, `data/` | outputs and data (never part of the code; the scans skip them) |

## Install
1. Python 3.10 or 3.11 and the packages of `alarm/settings/PYTHON_PACKAGES.txt` (numpy, pyarrow, pytest, scipy, orjson), for example
   `python3.11 -m venv ~/venvs/desk && ~/venvs/desk/bin/pip install -r alarm/settings/PYTHON_PACKAGES.txt`.
2. `cp settings/desk.env.example settings/desk.env` and set three values: `DATA_ROOT` (the folder holding `lab_days/`), `OUTPUT_ROOT`
   (every run, job, log and scratch file; keep about 60 GB free: jobs stop under that floor) and `PYTHON` (the venv's python3).
   A settings file may sit anywhere: pass it with `--settings <file>` to every desk command.
3. `python3 -B desk/desk.py setup` then `python3 -B desk/desk.py check`.

## Data
The engine reads one-format day folders (`DATA_ROOT/lab_days/day=YYYYMMDD/<part>/index.json` and lz4 blocks; format in
`DATA_ROOT/lab_days/FORMAT.json`). **No market data ships with this repo, and no converter.** V2 ships conversion instructions
instead: the user's own agent follows them to write the user's data in the one format, with the engine's own writer (lab3).
- `docs/DATA_FORMAT_V2.md`: the layout, index.json, the block encoding (read and write examples), every field with its unit and time
  basis, what each metric family needs; each rule with the file and line of the code it comes from.
- `docs/CONVERT_YOUR_DATA_V2.md`: the steps: fit, which parts, column mapping from common sources (exchange CSVs, Tardis files, Binance
  public files from `desk/data/download_binance.py`), what to do when a field is missing (leave it out, never invent), the small proofs
  first, and which alarm families cannot run without liquidation or Hyperliquid data. `/desk-setup` points to it at its data step.
The test sample is fixed in `desk/data/SAMPLE_MANIFEST_V1.tsv` (2 days of 2025, 5 coins, 4 parts, each part's index pinned by sha16):
`python3 -B desk/data/sample_check.py <DATA_ROOT>/lab_days` says SAMPLE OK when your data holds it unchanged. It pins the lab's own
bytes, so converted data says CHANGED or MISSING there; pin your own sample with `--manifest <file> --make` (CONVERT step 5c).

## Commands
```
python3 -B desk/desk.py [--settings F] setup | check | env
python3 -B desk/desk.py [--settings F] start <RUN>                       # a run folder; RUN = <NAME>_<YYYYMMDD>, NAME capitals and digits
python3 -B desk/desk.py [--settings F] job <RUN> COUNT <IDEA> V1=ideas/<IDEA>/defs/V1.json [--dry]
python3 -B desk/desk.py [--settings F] run <alarm-relative script> [args]   # any alarm tool; a bare S becomes --settings <file>
python3 -B desk/desk.py [--settings F] tests                             # every test of alarm/_tools/TESTS.tsv, then desk/tests
```
`job` makes the job with the released queue (`queue_job_v16.py`: the same checks, claim, twin, RUNS row and seals as in the lab) and
runs it here in the foreground, one job at a time. The steps of an idea (IDEA, METRICS and CLAIM, DEFINE, HAND CHECK, COUNT, GRADE,
TRUE, DECIDE, AUDIT) and their tools are in `alarm/AGENTS.md`. Words that come from the lab: a run tag's first part (before `_`) is the
kit's "seat"; the kit's "board" is a plain run log, `OUTPUT_ROOT/runlog/<seat>.txt`, written by `board_line_v2.py` (the audit asks for
a START line there). Where a message tells you to wait for the lab's disk keeper (DSK), there is none here: free disk space yourself; never delete a run.

## With Claude Code (the plugin)
From the repo root: `/plugin marketplace add ./`, then `/plugin install crypto-alarm-desk@crypto-alarm-desk`. Then `/desk-setup` (install
check, trading style, data and register, fit: GO, GO WITH GAPS or STOP) and `/new-alarm <idea>` (one idea end to end, logged). The
`alarm-reviewer` agent is the default second reviewer: must-fix only, read-only.

## The learning loop
Every try of every stage gets one row in `loop/<n>_<STAGE>/TRIED_<STAGE>_V1.tsv`, written only with
`python3 -B loop/scripts/add_row.py <file> key=value ...`, after a thought file in that stage's `thoughts/`. Check the loop with
`python3 -B loop/scripts/loop_check.py loop --accept` (FULL_PASS or a list of problems). It starts with the lab's lessons, reworded:
`loop/LESSONS_GENERAL_V1.tsv` (G rows hold anywhere, M rows are alarm method) and `loop/KIT_LEARNINGS_V5.tsv`, `_V6.tsv` (the kit's
rules with their evidence, reworded by machine).

## Checks that this repo is clean
| check | command |
|---|---|
| no machine path, owner or host name, no seat as a requirement | `python3 -B desk/build/path_scan_v1.py` (allowed exceptions, each with a reason: `desk/PATH_ALLOW.tsv`) |
| the judge is the released judge | `python3 -B desk/build/judge_parity_v1.py <release folder>` (record: `desk/build/JUDGE_PARITY.tsv`) |
| what was left out | `desk/build/EXCLUDES.tsv` (rules) and `desk/build/EXCLUDED.tsv` (every file) |
| tests that cannot pass here | `desk/build/KNOWN_TESTS.tsv`: each reported KNOWN with its reason, never skipped |

## What does not work yet
See STATUS.md, section "Blocks a stranger's install".
