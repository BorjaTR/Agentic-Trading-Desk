# Agentic: the alarm kit the agents work with (KIT_V5, KIT_V6)

**Status: in use by the alarm agents; TEST, NOT REVIEWED** (its own README says so, and PROPOSED for the owner); the owner
will gather the agentic process later. the owner, 30 Oct 2026 13:5x Berlin: "I would propose everything that is agentic we keep it in one
folder at the top level of ALARM. Once everything else is finished we will work on gather the alarm design agentic process on how
agents need to work, use the tools and all that."

The kit is how an alarm agent (Claude or any other model) goes from an idea to a decision: a launch prompt, the process (PROCESS_V7,
then PROCESS_V8 for how agents work and learn), a skill with the rules, the learnings of earlier rounds, the card and report templates,
5 job templates that run on the Mac's job runner (COUNT, GRADE, ENTRY, MONTH, CLEAN), and the tools: queue a job (the only way to
start one), decide a variant, decide a forward-only variant, audit a run, write a board line, clean a run's scratch; with tests on a
sandbox. KIT_V6 (29 Oct) changes how agents work and learn; its job tools and templates stay KIT_V5's. Every file here is a byte copy
of the team's dev tree (`SOURCES.tsv`), never edited here.

## Layout
- [KIT_V5/](KIT_V5), [KIT_V6/](KIT_V6): each kit's README (a byte copy) with SCOPE, ARCHITECTURE and CHANGELOG written for the repo (their
  first line says so).
- `tree/ALARM_DESIGN/KIT_V5/` (41 files) and `tree/ALARM_DESIGN/KIT_V6/` (19): the whole kit folders, in the dev layout below team/RESEARCH;
  `_old/`, twins (`.pre_*`) and `__pycache__` left out.
- `tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/`: the 9 run tools the kit's jobs and tools pin by sha16 and run (TEST, NOT REVIEWED):
  `reg_append_v1.py` (the register writer), `read_stratentry_v1.py`, `perfire_v1_to20260430.py`, `test_perfire_v1.py`, `split_v1.py`,
  `month_read_v3.py`, `conditions_v1.py`, `lead_null_v1_to20251231.py`, `run_alarm_store_v10_3_noladder.sh`.
- `tree/fixtures/kit5_test/`: the 5 files the kit tests copy into their sandbox (sim_env.py's REAL folder, outside the forensics tree).
- `proof_harness/kit5_tests_main.py`: written here (not a dev file): runs the kit tests with sim_env.py pointed at those fixtures.

## Which part uses which kit file
| part | kit files | what for |
|---|---|---|
| 01 Detection | `jobs/JOB_COUNT_V5` (detect: fires, waves and coins per month on Sep-Dec, no outcome) | the SUPPORT quick check before any grade |
| 02 Freeze | templates (IDEA_CARD_V5, ALARM_CARD_V4, PREREG_V5, FORECAST_V5; KIT_V6 CARD_V6), the run registers, `queue_job_v4.py` (refuses what is not sealed), `audit_run_v2.py` (A3, A5), `reg_append_v1.py` | freeze the card, variants and forecasts before any grade |
| 03 Grading | `jobs/JOB_GRADE_V5` (with `perfire`, its check, `lead_null`) | the Sep-Dec grade; its released chain v2_2 is in 03_Grading |
| 04 Month check | `jobs/JOB_MONTH_V5`, `tools/queue_job_v4.py` (MONTH), `tools/decide_forward_v1.py`; `month_read_v3`, `conditions_v1` | the forward months Jan-Apr |
| 07 Price path | `jobs/JOB_ENTRY_V5` (`run_alarm_store_v10_3_noladder.sh`, the markout), `read_stratentry_v1.py` | STRATEGY's entry check |
| 09 Decision | `tools/decide_v1.py`, `decide_forward_v1.py`, `audit_run_v2.py` (A6), templates FINDINGS_V5 and REPORT_V5 | the label and the package |
| every run | PROCESS_V7 and V8, the skills, the launch prompts, the learnings, `board_line_v1.py`, `jobs/JOB_CLEAN_V5` with `clean_scratch_v1.py` | the way of working |

## Run from this folder (Alarm/Agentic)
No data is needed: the tests build a sandbox with stub tools (59 tests, about 15 s).
```
python3 -B ../_tools/run_all_tests_v1.py <settings file> --part Agentic          # a fresh TMPDIR per test, removed after; --copy runs it from a copy
```
Run by hand instead, each test leaves one `k5sim_*` folder in TMPDIR (59 a run): `TMPDIR=<a folder with room> python3 -B
../_tools/run_isolated_v1.py proof_harness/kit5_tests_main.py`. Proof: [RUN_PROOF.md](RUN_PROOF.md).
Never run `tree/ALARM_DESIGN/KIT_V5/tests/mutants_v1.py` on a shared machine: for each of its 36 mutants it copies the kit and reruns the
whole suite, leaving every folder behind (on 30 Oct it filled the VM's disk). It is also broken: mutant 17's target text,
`if str(d.get(k, '')) != r.get(k, ''):`, is in `tools/audit_run_v2.py` (0593141fa5f9e166) twice, so the script stops there
(`assert s.count(a) == 1`) and mutants 17 to 36 are never judged (the kit README says 34 mutants; the file has 36).

## Not here (what the kit's jobs run elsewhere)
The jobs run lab tools at their dev paths: the grade chains v2_0 and v2_1, the cards v1_2 and v1_3 and the aw1 step tools
(`team/RESEARCH/tools/alarm_process/`, TEST editions: 03_Grading README), chain v2_2 (released: 03_Grading), `idea_to_grade/detect.py`
(COUNT), the markout (`tools/markout/`, ENTRY), Outcomes and labcore (imported by the run tools); KIT_V6 uses the alarm registry and
`novelty_v1.py` (`ALARM_DESIGN/REGISTRY/`, part 08). The agents' run folders (`ALARM_DESIGN/runs/<RUN>`) are data.

## Data and settings
A real kit job runs on the Mac through the job runner. Settings keys (`../settings/SETTINGS_<MACHINE>.env`): `RESEARCH_ROOT` (the runs,
registers and receipts), `RUNNER_QUEUES`, `SCRATCH` (SCRATCH_DISK), `PYTHON`, and `LAB_DAYS` through the tools the jobs run.
Still built in (`MACHINE_PATHS.tsv`, 58 rows BUILT_IN): every kit tool finds the dev tree and SCRATCH_DISK itself (`_roots()`); `queue_job_v4.py`
reads the job templates, the runner, the allocator and the register writer from the dev tree (lines 43-48, 480); each job template sets the
dev root, interpreter, run folder and scratch folder (lines 8-12), checks the scratch drive's free space (lines 17-20) and works from
<DEV> (lines 26-32); the run tools import Outcomes and labcore
from the dev tree; `tests/sim_env.py:5` names SCOUT's fixture folder (the harness points it here). On another machine these need a new
kit edition that reads the settings file.

What changed: [CHANGELOG.md](CHANGELOG.md).
