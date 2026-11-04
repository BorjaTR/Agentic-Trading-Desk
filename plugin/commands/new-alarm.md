---
description: Design and test one new alarm idea end to end through the fixed engine, then log the try
argument-hint: <the idea in a few words, or empty to pick one>
---

You design one new alarm idea in this Crypto Alarm Desk repo. The idea: $ARGUMENTS (if empty, pick one: read the lessons first and say
why you chose it).

Load the skills alarm-desk and learning-loop first and follow them. The engine in `alarm/` is read-only: verdicts come only from its
tools, run through `python3 -B desk/desk.py` from the repo root. If a step needs a tool that is not in the repo, say so and stop.

1. Read docs/DESK_REFERENCE.md, CLAIMS.md, alarm/AGENTS.md, loop/LESSONS_GENERAL_V1.tsv, alarm/playbook/ALARM_GOALS_V1.md and PLAYBOOK.md.
2. Before any data: search what was tried (loop_find, then tried_search_v1 on your words). Start your thought file. Write your claim:
   which moment; whether it claims SIZE only or SIDE too; who must trade now and why; what is measured and what is inferred; what
   would prove it wrong; the closest existing idea or alarm.
3. Start a run (`desk.py start <RUN>`, NAME capitals and digits, at most 12), post its START line, then follow the loop of the
   alarm-desk skill in order: METRICS and CLAIM, DEFINE, HAND CHECK, copy search with --def, COUNT, SEAL (card, menu gate, VARIANTS
   row, TRUE label checked), GRADE, TRUE, DECIDE, NOVELTY and FIRST LOOK, audit. One variant first; a second only for a named result,
   at most 3.
4. Build months only (Sep-Dec 2025 in this edition). Never money. A refusal is reported word for word and the try stops there.
5. Run `audit_run_v5.py S <RUN> --write` and `python3 -B loop/scripts/loop_check.py loop --accept` before you call it done.
6. Log the try: one TRIED row with add_row.py (verdict PLANNED if no outcome was read), and a lesson row for anything that cost time,
   failed or surprised you.
7. Report under 15 lines (alarm-desk skill section 6), every number with its file and sha16. If a reviewer is configured
   (the alarm-reviewer agent or the desk's own), ask it for a must-fix review of the sealed card and the receipts after the run.
