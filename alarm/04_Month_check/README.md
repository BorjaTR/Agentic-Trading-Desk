# 04 Month check: January to April 2026, month by month

An alarm decided PASS or NEEDS MORE MONTHS on the design months (10 Sep-31 Dec 2025), or the other side of a STOP (forward-only), is
tested on the four forward months. First its forecast for each month (the range its race gap should land in at 15 minutes and 1 hour)
is sealed by sha16; then one MONTH job grades it over 10 Sep 2025-30 Apr 2026 (the chain of part 03), writes the per-fire file and reads
each month 2601 to 2604 against the sealed range: STRONGER, HELD, WEAKER, BROKE, or NO READ under 30 waves. An alarm counts as FOUND
only when its Jan-Apr months hold (the owner, 29 Oct; `../03_Grading/month_parts/README.md`). A forward-only variant passes when 3 or more of
the 4 months read HELD or STRONGER (`decide_forward_v1.py`).

**This part holds documents only.** The month check is the alarm kit's MONTH job (`KIT_V5/jobs/JOB_MONTH_V5.job.sh.txt`, queued by
`KIT_V5/tools/queue_job_v4.py`) plus `KIT_V5/tools/decide_forward_v1.py`, kept with the rest of the kit in [../Agentic](../Agentic)
since 30 Oct (the owner, 13:5x Berlin: "everything that is agentic we keep it in one folder at the top level of ALARM"). The kit is in
use by the alarm agents; its own README says TEST, NOT REVIEWED, PROPOSED for the owner. Editions below are the state on 30 Oct 2026; the ones in use now: ../AGENTS.md.

## Where each piece is
| piece | what it does | where | status |
|---|---|---|---|
| the MONTH job | per variant: the Sep-Apr grade, each coin part's memory and data and code versions, the per-fire file and its check, the 4 month reads against the sealed ranges, the conditions | [../Agentic](../Agentic): `tree/ALARM_DESIGN/KIT_V5/jobs/JOB_MONTH_V5.job.sh.txt` (f19e13c55a2aa283) | in use; its wiring to chain v2_2 had review 1B PASS and review 2 PASS (03_Grading BASELINE.tsv, last row) |
| the queue | queues a MONTH job only with a Sep-Dec decision and 4 sealed forecasts; never twice | [../Agentic](../Agentic): `tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v4.py` (dccce8e5e119fe48) | in use, TEST, NOT REVIEWED |
| the forward-only decision | FORWARD PASS = HELD or STRONGER in 3 or more of the 4 months | [../Agentic](../Agentic): `tree/ALARM_DESIGN/KIT_V5/tools/decide_forward_v1.py` (b6c153cf4b304bf9) | in use, TEST, NOT REVIEWED |
| the month reader and the conditions | the verdict of one month; the conditions (descriptive) | [../Agentic](../Agentic): `tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/month_read_v3.py` (b3480cfd670b28f4), `conditions_v1.py` (2f4aaebe1f259278) | TEST, NOT REVIEWED (CLAUDE1 28 Oct) |
| the grade chain v2_2 | the Sep-Apr grade in 26 coin parts | [../03_Grading/month_parts](../03_Grading/month_parts) (583672d036d2ad85) | released (BASELINE.tsv) |
The kit's documents (SCOPE, ARCHITECTURE, CHANGELOG): [../Agentic/KIT_V5/](../Agentic/KIT_V5).

## Tests
The kit's tests (59, on a sandbox with stub tools; the MONTH job filled and run end to end) run from ../Agentic:
`python3 -B ../_tools/run_all_tests_v1.py <settings file> --part Agentic` (proof: ../Agentic/RUN_PROOF.md). Nothing runs from here.

## Data and settings
A real MONTH job needs `RESEARCH_ROOT`, `RUNNER_QUEUES`, `SCRATCH`, `PYTHON` and, through the chain, `LAB_DAYS`
(`../settings/SETTINGS_<MACHINE>.env`). Every one is still built into the kit (../Agentic/MACHINE_PATHS.tsv) and the chain
(../03_Grading/MACHINE_PATHS.tsv).

## Files here
README.md, CHANGELOG.md, RUN_PROOF.md, MANIFEST.tsv and SOURCES.tsv (empty: nothing copied), MACHINE_PATHS.tsv (empty), REMOVE.tsv (the
34 files of the earlier layouts, which SCOUT moves out of the repo).
