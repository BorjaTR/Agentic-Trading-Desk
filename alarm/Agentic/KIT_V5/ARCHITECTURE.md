Written by SCOUT for the repo on 30 Oct 2026 from tree/ALARM_DESIGN/KIT_V5/ (jobs/JOB_GRADE_V5.job.sh.txt, jobs/JOB_MONTH_V5.job.sh.txt,
tools/queue_job_v4.py, tools/decide_forward_v1.py, templates/FORECAST_V5.md, tests/test_kit5_tools.py, tests/sim_env.py, README.md,
PROCESS_V7.md, MANIFEST_SHA16.txt); not the owner's document (owner seat: SCOUT).

# ARCHITECTURE: ALARM_DESIGN KIT_V5

## Inputs
| input | format | where (on the Mac) |
|---|---|---|
| the run | tag `<SEAT>_<YYYYMMDD>`; registers/*.tsv (VARIANTS, FORECASTS, RUNS, DECISIONS, POSTMORTEMS, LEARNINGS_PROPOSED, PROBLEMS, TOOLS_BUILT: headers in runs/TEMPLATE_V3/registers), ideas/<IDEA>/ (definitions, PREREG, cards, forecasts) | `RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>` |
| a job's inputs | definitions and PREREG (sha16 in VARIANTS); for ENTRY and MONTH the GRADE job's receipts (`--from-job`); for MONTH 4 FORECASTS rows (gap15_lo, gap15_hi, gap1h_lo, gap1h_hi per month) | `<RUN>/ideas/`, `<RUN>/receipts/` |
| the job templates | jobs/JOB_<KIND>_V5.job.sh.txt, pinned in queue_job_v4.py TEMPLATE_SHA | read from the dev tree `ALARM_DESIGN/KIT_V5/jobs/` (queue_job_v4.py:480) |
| lab days | read by the tools the jobs run, never by the kit | `LAB_DAYS` |

## Steps
1. Queue: `queue_job_v4.py <RUN> <KIND> <IDEA> <ITEMS> [--from-job J] [--forward-only] [--queue Q_Vn] [--behind] [--dry]` (`plan()` lines
   166-339, `main()` 447-559): the checks (SCOPE), the template filled (the variants block and, for MONTH, each month's sealed ranges,
   e.g. `1:9,2:12`), the number from the live allocator, the twin `<RUN>/jobs/<n>_<KIND>_<IDEA>.job.sh`, the RUNS row through
   reg_append_v1.py (a failed row queues nothing), the copy into the queue's IN.
2. Run (the job runner on the Mac). GRADE (`JOB_GRADE_V5`): lines 8-19 roots, W and the receipts folder (existing receipts: exit 4); 20-23
   pins (chain v2_0, card v1_2, perfire, its check, lead_null, PREREG, definitions); 24 the quiet window; 27-38 per variant: SCRATCH_DISK
   free, `LEAN=<lean> bash alarm_grade_chain_v2_0_to20251231.sh <V> <def> <W>`, perfire, its check, the FIRES.tsv row, copies; 39-49 the
   hand-off manifest and lead_null (10,000 flips); 50-53 DISK.tsv, SHA16.txt. MONTH (`JOB_MONTH_V5`): 20-24 pins (chain v2_2, card
   v1_3, perfire, its check, month_read_v3, conditions_v1, split_v1, PREREG, definitions, forecasts); 25 the quiet window; 28-44 per
   variant: `PARTS=26 LEAN=<lean> bash alarm_grade_chain_v2_2_to20260430.sh <V> <def> <W>`, DETECT_MEM and DETECT_LOG of every part,
   perfire, its check, month_read_v3 for 2601-2604 at `15m,1h`, conditions_v1 at 15 m and 1 h (cut months 2509-2512); 45-47 DISK.tsv,
   SHA16.txt. COUNT, ENTRY and CLEAN follow the same frame.
3. Read and decide: POSTMORTEMS rows; `decide_v1.py <RUN> <IDEA> <V> --grade <J> [--entry <J> | --entry-too-big] [--write]`;
   `decide_forward_v1.py <RUN> <IDEA> <V> --month <J> [--write]`; board lines (`board_line_v1.py`).
4. Check and clean: `audit_run_v2.py <RUN>` (17 checks: A5 forecasts sealed before each MONTH job, A6 every decision recomputed from the
   receipts, ...); a CLEAN job copies the fire lists and per-fire files to the receipts, then removes the job's SCRATCH_DISK scratch.

## Outputs
W = `SCRATCH/work_<RUN>/<n>_<KIND>_<IDEA>/`; receipts `<RUN>/receipts/<n>_<KIND>_<IDEA>/`: STAGES.tsv, per variant CARD, SUM, STATUS, INPUTS,
MENU, logs; GRADE: FIRES.tsv and HANDOFF/; MONTH: MONTH_READ_<V>_2601..2604.txt, CONDITIONS_<V>_15m/1h.txt, <V>_FIRES_V1_LIST.tsv,
DETECT_MEM_<V>.tsv, DETECT_LOG_<V>.txt; always DISK.tsv and SHA16.txt. Job exit: 0 done (or not started near the quiet window), 3 a pin
changed, 4 receipts exist, 7 disk. The tools: `REFUSED ...` messages before anything is written; DECISIONS rows only with --write.

## Files (tree/ALARM_DESIGN/KIT_V5/; sha16 as MANIFEST_SHA16.txt 76b46b91edeffc3c pins them)
| file | what |
|---|---|
| tools/queue_job_v4.py (dccce8e5e119fe48) | the queue and its checks |
| tools/decide_v1.py (8c345946c673530a), tools/decide_forward_v1.py (b6c153cf4b304bf9) | the decisions |
| tools/audit_run_v2.py (0593141fa5f9e166), tools/board_line_v1.py (ea7b62eb1437170d), tools/clean_scratch_v1.py (fe4ed906b1466278) | audit, board, CLEAN |
| jobs/JOB_COUNT_V5 (c803323612fb5fff), JOB_GRADE_V5 (a520be2650b27910), JOB_ENTRY_V5 (1cfc36246087008c), JOB_MONTH_V5 (f19e13c55a2aa283), JOB_CLEAN_V5 (146adc2ce61ff57b) | the job templates |
| PROCESS_V7.md, skills/alarm-design-v5/SKILL.md, LEARNINGS_V5.tsv, LAUNCH_PROMPT_V5.md, LAUNCH_PROMPTS_29OCT.md, IDEA_TO_ALARM_V4.md, QUICK_CHECK_EXAMPLES_V2.md, METRIC_MENU_V1.tsv, METRIC_FAMILIES_V1.md, FORCED_TRADE_MAP_V1.md | the way of working |
| templates/ (6), runs/TEMPLATE_V3/ (README_RUN.md, 8 register headers) | cards, forecasts, write-ups, the run folder |
| tests/test_kit5_tools.py (f947971a7d40b001), tests/sim_env.py (aad7636a88036a51), tests/mutants_v1.py (482bfe42036382f5) | tests, sandbox, planted bugs |
| README.md (dd80f0b5acf34737), MANIFEST_SHA16.txt (76b46b91edeffc3c) | the manual and the record |
The run tools the jobs and tools pin are in `tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/` (Agentic README).

## Settings keys a real run needs
`RESEARCH_ROOT`, `RUNNER_QUEUES`, `SCRATCH`, `PYTHON`, and `LAB_DAYS` through the tools the jobs run. Today all are built in: `_roots()`
and `CFG` in every tool, the templates' F, PY, W and `cd` (Agentic MACHINE_PATHS.tsv).

## Tests
`tests/test_kit5_tools.py`: 59 tests (41 functions; the audit and clean classes rerun the 9 flow tests) on a sandbox from
`tests/sim_env.py` with stub tools, a fake runner and a fake allocator; every filled template runs in bash. GRADE: stages, per-fire,
hand-off and FIRES.tsv (`test_grade_entry_decide_month`), a failed grade, a changed pin, the disk guard. MONTH: refused without a
decision or sealed forecasts or with a changed forecast, the ranges reach the job, the month reads run, never MONTH-graded twice
(`test_grade_entry_decide_month`); forward-only (`test_forward_only`). Run with `proof_harness/kit5_tests_main.py`.
`tests/mutants_v1.py`: 36 planted bugs, not run (Agentic README).
