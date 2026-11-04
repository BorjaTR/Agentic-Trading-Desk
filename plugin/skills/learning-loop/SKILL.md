---
name: learning-loop
description: Use at the start and end of every try in the Crypto Alarm Desk repo - find what was tried and learned before, write the thought file first, log one row per try with add_row.py (never by hand), turn each mistake into a lesson row with its evidence, and check the loop with loop_check.py. This is how the desk learns from every try, failed ones included.
---

# The learning loop: log every try, learn from each one

The loop lives in `loop/` at the repo root. One folder per stage (`1_IDEA`, `2_METRICS`, `3_DEFINE`, `4_HANDCHECK`, `5_COUNT`, `6_GRADE`,
`7_TRUE`, `8_DECIDE`, `9_TOOLS`), each with the same files: `TRIED_<STAGE>_V1.tsv` (one row per try), `LESSONS_<STAGE>_V1.tsv`,
`GAPS_<STAGE>_V1.tsv` (what is missing), `CHANGES_<STAGE>_V1.tsv` (what changed because of a lesson), `thoughts/` and `START_HERE.md`.
The desk starts with the lab's lessons: `loop/LESSONS_GENERAL_V1.tsv` (G rows hold anywhere, M rows are alarm method) and
`loop/KIT_LEARNINGS_V5.tsv`, `_V6.tsv` (the engine's rules with their evidence). Read the G and M rows before your first try.

## Before a try
1. Was it tried? `python3 -B loop/scripts/loop_find.py loop <playground folder or loop> <word> [<word> ...]` (add `--any` when nothing
   is found: an old idea may be worded differently), and the engine's own copy search (alarm-desk skill, step 1).
2. Start the thought file at once: `loop/<stage>/thoughts/<id>.md` (why this idea, what you doubt, what would prove it wrong). The row
   that comes later points to it; a row without its thought file is refused.

## After a try (always, also when it failed, was refused or was stopped)
Write one row, only with the tool:
```
python3 -B loop/scripts/add_row.py loop/<stage>/TRIED_<STAGE>_V1.tsv id=<id> process=<stage> seat=<RUN name> run=<RUN> \
  what_tried="..." thought_file=thoughts/<id>.md expected="..." actual="..." verdict=<VERDICT> failed_stage=<stage or none> \
  fail_layer=<LAYER> why="..." went_well="..." failed="..." slowed="..." gaps="..." improve="..." faster_next="..." not_waste="..." \
  minutes_active=<n> minutes_waiting=<n> minutes_blocked=<n> closest_existing="..." tools_used="..." playground_ref=none \
  receipts="<paths>" ledger_row=<RESULT id or none> months_read=<months or none> prompt_id=none prompt_fix=none model=<model> \
  next_action="..." lesson_id=<id or none> reviewed_by=none
```
- verdict: PLANNED (no outcome read), WORKED, FAILED, INVALID_TEST, NOT_MEASURABLE, UNSURE, STOPPED.
- fail_layer: NONE, PREMISE, MEASURE, RULE, DATA, TOOL, PROCESS, PROMPT, COST (where it broke, not who).
- expected is what you wrote BEFORE the run; never edit it after.
- ledger_row is the RESULT id the engine's ledger printed for the result, never the prereg id; none if no outcome was read.
- The stamp is the clock's, filled by the tool. Every number in actual carries its file and sha16.

## Turning a mistake into a lesson
When a try cost time, failed or surprised you, add a LESSONS row in the stage it belongs to (or `loop/LESSONS_GENERAL_V1.tsv` for one
that holds anywhere): `what_happened`, `root_cause`, `rule_now` (the rule a next agent follows), `evidence` (the receipt, file and
sha16). A rule that changes how the desk works also gets a CHANGES row (`from_lesson`, `measure`, `before`, `after`): that is how the
desk shows whether a lesson helped. A missing tool, metric or test is a GAPS row, not a workaround.

## What may become a lesson (training provenance only)
A lesson, change or prompt line may come only from tries the desk is allowed to learn from (its own work, or the learning tasks of an
evaluation).
- A trial agent may read its OWN assigned brief and the inputs that brief approves, and log its own try as usual; when the trial is a
  held-out task, its logs and lessons are QUARANTINED: kept for the record, never read by the evolve step or any learning memory until
  the evaluation ends.
- The evolve step, the learning memory and the reviewer never read a held-out brief, a held-out trial's output or logs, any sealed key,
  or another trial's transcript or grade, at any time during an evaluation.
- If any of these was seen by accident, write a PROBLEMS row naming it and mark every lesson written after it as EXPOSED (quarantined:
  not used until the evaluation ends). The held-out judge is the harness, never this agent or its reviewer.

## Checks
- `python3 -B loop/scripts/loop_check.py loop --accept`: FULL_PASS, or the list of problems (a hand-written row, a missing thought file, a
  bad verdict word). Run it at the end of every try; a FAIL is fixed before the next try.
- Never write or edit a row by hand, never delete a row: a correction is a new row that names the one it corrects.
