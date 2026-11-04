# ALARM_DESIGN KIT_V5 (SCOUT, 29 Oct 2026). TEST, NOT REVIEWED. PROPOSED for the owner.
The kit for alarm agents (Claude or any other agent): one process, one skill, one list of learnings, 5 job templates, 5 tools.
Start: the launch prompt LAUNCH_PROMPT_V5.md (the owner gives it with a run tag). Agents never edit this folder.

## What is here
| file | what |
|---|---|
| PROCESS_V7.md | the process: idea, quick checks, alarm card and hand check, freeze, grade, price path, hand-off, decision (with its proof, section 4) |
| skills/alarm-design-v5/SKILL.md | how to run it: the rules, the path of one idea, jobs, registers, board, learning (a Claude skill; any agent reads it as its instructions) |
| LEARNINGS_V5.tsv | 40 rules, tools and checks plus 4 design hints, filtered from CODEX1, CODEX2, CLAUDE1, KIT_V1, KIT_V2 and 29 Oct; each says where it is enforced |
| IDEA_TO_ALARM_V4.md, QUICK_CHECK_EXAMPLES_V2.md, METRIC_MENU_V1.tsv, METRIC_FAMILIES_V1.md | the front end (CLAUDE1 with CODEX1): the six quick checks, examples, the readable metric codes |
| templates/ | IDEA_CARD_V5, ALARM_CARD_V4, PREREG_V5, FORECAST_V5, FINDINGS_V5, REPORT_V5 |
| jobs/ | JOB_COUNT_V5, JOB_GRADE_V5, JOB_ENTRY_V5, JOB_MONTH_V5, JOB_CLEAN_V5 (filled only by queue_job_v4.py) |
| tools/ | queue_job_v4.py, decide_v1.py, board_line_v1.py, audit_run_v2.py; clean_scratch_v1.py (inside CLEAN jobs only) |
| runs/TEMPLATE_V3/ | what each agent copies to H/runs/<RUN>/ (8 registers with headers, README_RUN.md) |
| tests/ | test_kit5_tools.py (52 tests on a sandbox with stub tools, every template run end to end), mutants_v1.py, sim_env.py |
| LAUNCH_PROMPT_V5.md | the prompt for an agent of any model (fill run tag, seat, theme) |
| MANIFEST_SHA16.txt | the sha16 of every kit file |

## The loops
- Research, per idea: the skill's path A-J (claim, cards, COUNT, PREREG, GRADE with hand-off, ENTRY, decide, forward months, CLEAN).
- Learning: a POSTMORTEMS row after every job read; a LEARNINGS_PROPOSED row (RULE, TOOL, CHECK or SKILL) only with its evidence file.
- Reporting: board lines (CLAIM, JOB, DECISION, CHECKPOINT, DONE), FINDINGS per idea, REPORT per run, the audit file; the lead reports
  to the owner.
- Improvement: the lead merges accepted rows into LEARNINGS_V5.n and SKILL V5.n after the owner's OK, with a CHANGES line; a change is
  judged on later ideas, never on the one it came from.
- Scorecard: audit_run_v2.py (17 checks, run after every job read) and the lead's test lines (runs/CLAUDE1_20261028/ideas/AGENTTEST).

## Proof that the kit works (29 Oct)
- Sandbox: tests/test_kit5_tools.py, 52 tests with stub tools, every job template run end to end; tests/mutants_v1.py, 34 mutants (each breaks one guard).
- Update 29 Oct (agents' findings): ENTRY declared size from 6 measured receipts (AD3, GPT1), audit A2 skips CLEAN labels (AD2, AD3),
  board twins unique within a second (GPT1); 16:3xZ: a variant whose job failed may be queued again under its name (no extra try).
- Real runner: runs/KITCHECK_20261029 (ideas/KITDP/FINDINGS_KITDP.md): DAYPOKE2's logic through COUNT, GRADE, ENTRY, decide_v1 and
  CLEAN reproduced its hand-off to 4 decimals in every month and its markout byte for byte; the mirror control was STOP; CLEAN removed
  746 MB and logged 319 MB of protected store places for DSK; audit 17 PASS, 0 FAIL.

## The decision (PROCESS_V7 step 8; the owner 29 Oct 2026 14:23 Berlin: "for now we keep them separate and report both")
PASS = hand-off R2; NEEDS MORE MONTHS = R1 only; STOP = R1 missed; INSUFFICIENT = fewer than 3 counted months; INVALID = a stage
failed or a file is missing. CLEAR (STRATEGY's price path) is reported beside it and never changes it. decide_v1.py writes it.

## Why V5 (28-29 Oct: two agents, 25 versions, 28+ jobs, 0 alarms)
They compared ideas with other alarms instead of matched random; added gates nobody asked for (18 of 25 versions closed before any
outcome); built tools and wrote documents instead of testing; watched the board; ran unsized jobs (the drive filled twice).
KIT_V5 answers each with a tool or a check, not a sentence: one comparison, one decision tool, a try budget, a job budget, a disk guard
in every job, receipts copied by every job, and an audit that recomputes every decision from the receipts.

## Changes from KIT_V2
8 registers instead of 16; no exam; jobs only through queue_job_v4.py (live allocator, budgets, pins, disk, empty queue, all or nothing);
decisions only through decide_v1.py; every job copies its receipts to dev (agents never read SCRATCH_DISK); one month window per tool kept;
each run cleans its own scratch with CLEAN jobs after the proof is on dev, under a 15,000 MB budget (the owner 29 Oct 14:52 Berlin);
the ENTRY store places sit in protected folders (work_TOOLTRIAL is a symlink into research/, work_ALARMLIB is protected): CLEAN logs
them as left for DSK, about 0.3 GB per 5,000 fires (KITCHECK).
