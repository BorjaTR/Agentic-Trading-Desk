# idea_time_v2: tool card

Where an agent's time went, from files only. The code: [idea_time_v2.py](../Agentic/tree/ALARM_DESIGN/KIT_V6/tools/idea_time_v2.py). Exact commands: [TOOL.json](idea_time_v2.TOOL.json). Every output column: [dictionary](../dictionaries/idea_time_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- For each run named, reads the seat's board stamps, the registers (RUNS, VARIANTS, DECISIONS), the job receipts (STAGES.tsv) and the claim files, never what the agent says.
- Prints, per idea, the minutes from claim to job, each job's run time, the agent's lag from a job's end to its next step, and claim to decision; per seat, how much of the time had no job of its own running.
- Read-only: prints a table, writes nothing.

## When to use it
- After a run or a round, not a step of the alarm loop (the owner 29 Oct 18:55 Berlin: "log why and where they are wasting time").
- It answers: where did the time go, idea by idea, and how long did the seat sit with no job running?

## Run it
```
python3 -B <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V6/tools/idea_time_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029
```
- Several runs at once: list them. `--launch SEAT=YYYY-MM-DDTHH:MM:SSZ`: the seat's launch time (default its START line). `--now YYYY-MM-DDTHH:MM:SSZ`: the end for a seat with no DONE line (default the clock).
- Real output, read-only (SCOUT's VM, 30 Oct 2026): `GIVENA 14:42:55Z 0 1 10 9 2 4 21 52 GA1 PASS` ... and `seat AD1: launch to first claim 2 min; no job running 62 pct, one 25 pct, two or more 13 pct of 143 min; first own PASS after 80 min`.

## What it gives
- Printed, per run:
  - `== <RUN>  launch ..  START ..  DONE ..`;
  - a header and one row per idea: idea, claimed, claim_to_first_job, count_run, grade_queued_after_count_end, grade_run, read_lag_after_grade, entry_run, decided_after_entry_end, claim_to_first_decision (all in minutes), states;
  - `seat <SEAT>: launch to first claim .. min; no job running .. pct, one .. pct, two or more .. pct of .. min; first own PASS after .. min`.
- A missing stamp prints `-`. Every field: the dictionary.

## Limits and refusals
- exit 0: printed.
- exit 2: no run named (it prints its usage), no `--settings`, or a settings file the reader refuses (RESEARCH_ROOT and BOARD must be set).
- A run tag that does not exist prints an empty report, not an error.

## Where its data comes from
- RESEARCH_ROOT: the runs ALARM_DESIGN/runs/<RUN> (registers and receipts) and the claim files ALARM_DESIGN/runs/IDEAS_CLAIMED.
- BOARD: each seat's board file BOARD/<SEAT>.txt (START, CLAIM and DONE lines).
