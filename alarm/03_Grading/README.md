# 03 Grading: fires against matched random moments, month by month

For every fire of an alarm the grade draws 3 random moments matched to it (the alarm's own moments left out, each wave counted once)
and asks of each fire and each random moment: does the price move two round-trip costs the alarm's way before it moves one cost
against it (the race +2c before -1c), within 5 minutes, 15 minutes and 1 hour, on both sides (FADE and FOLLOW)? The alarm's rate
minus its random moments' rate, month by month with waves as the unit, is the grade (CARD_<V>.txt, SUM_<V>.tsv); the per-fire file
keeps one row per fire and per random moment. The alarm kit's GRADE job grades the design months (10 Sep-31 Dec 2025) and its MONTH
job (part 04) grades 10 Sep 2025-30 Apr 2026 with the chain released here; both jobs are in [../Agentic](../Agentic), the alarm kit.

Only released editions are here (the owner, 30 Oct 2026 12:33 Berlin, option a: "released editions only"). Every file is a byte copy
of the team's dev tree (`SOURCES.tsv`: each file's dev path and sha16), never edited here.

## Layout
- One folder per released tool at the top: [month_parts/](month_parts) (README, SCOPE, ARCHITECTURE, REQUIREMENTS: byte copies of the
  tool's own; CHANGELOG written for the repo, its first line says so).
- `tree/`: the byte copies in the dev tree's layout under team/RESEARCH (`tree/tools/month_parts/`).
- The alarm kit (KIT_V5: the GRADE job template, PROCESS_V7, the queue) is in [../Agentic](../Agentic) since 30 Oct (the owner, 13:5x
  Berlin: "everything that is agentic we keep it in one folder at the top level of ALARM").

## Tools
| tool | what it does | owner | edition here | main file (sha16) | status |
|---|---|---|---|---|---|
| [month_parts](month_parts) | the grade chain over 10 Sep 2025-30 Apr 2026, with the detection in 26 coin parts so each stays under detect's 2 GiB worker cap; the MONTH job runs it | SCOUT | chain v2_2; release record `tree/tools/month_parts/BASELINE.tsv` (58c62fa609ed216d) | `tree/tools/month_parts/alarm_grade_chain_v2_2_to20260430.sh` (583672d036d2ad85) | released 30 Oct 00:24Z: review 1 PASS, review 2 final PASS on the Mac run of job 20264083 |
| the GRADE job (in [../Agentic](../Agentic)) | the Sep-Dec grade job: chain v2_0 per variant, the per-fire file, the hand-off test; filled and queued only by `queue_job_v4.py` | SCOUT | KIT_V5 (`Agentic/tree/ALARM_DESIGN/KIT_V5/jobs/JOB_GRADE_V5.job.sh.txt`, a520be2650b27910) | | in use by the alarm agents; TEST, NOT REVIEWED, as is every step it runs (below). The templates in use now: ../AGENTS.md |

What changed in each release: [CHANGELOG.md](CHANGELOG.md).

## Earlier editions in the dev tree
State on 30 Oct 2026, kept as history; the editions in use now are in ../AGENTS.md. In ~/volat_release means released: what follows says what each piece is and what is unproven.
TEST editions: no RELEASE json, BASELINE row or kit manifest pin shows a review. The chains the jobs run now, v2_0_7 and v2_2_7, are here under
tree/tools; the run tools the kit pins (the per-fire file, its check, split_v1, the hand-off test) are copied, TEST, with the kit in ../Agentic.
| tool | where (dev tree; sha16) | status |
|---|---|---|
| grade chain v2_1 (Sep-Apr in 2 coin halves) | `team/RESEARCH/tools/alarm_process/alarm_grade_chain_v2_1_to20260430.sh` (99e8a229617cb2e2; `_to20260331` 331452973d209868, `_to20260531` 9124f750833c3392) | TEST, NOT REVIEWED (STRATEGY 28 Oct; TOOLS_REGISTRY status KIT); v2_2 replaced it in the MONTH job on 30 Oct |
| grade chain v2_0 (Sep-Dec) | `team/RESEARCH/tools/alarm_process/alarm_grade_chain_v2_0_to20251231.sh` (94273faf1e927ddc) | TEST, NOT REVIEWED (KIT); the GRADE job runs it |
| the chains' step tools | `team/RESEARCH/tools/alarm_process/`: `detect_aw1.py` (f03254fd5420e56b), `idea_to_grade_aw1.py` (1f0c7a2f04e32d12) with `I2G_PINS_AW1.json` (5005d586747bedfc), `event_outcomes_aw1.py` (e4a4792db69e71fb) with `RELEASE_event_outcomes_AW1.json` (05c49431febc990d) and `WINDOWS_ALARM_V1.tsv` (efc602a6428aaf59), `OUTCOMES_MENU_ALARM_V1.json`, `AW1_SPEC_V1.json` | TEST (STRATEGY's aw1 copies, 28 Oct; that release json says "TEST, NOT REVIEWED") |
| the alarm card | `team/RESEARCH/tools/alarm_process/alarm_card_v1_3.py` (a616c4378a02852b, chains v2_1 and v2_2), `alarm_card_v1_2.py` (c3172f94e389cadb, chain v2_0) | KIT; no release record |
| matched random, the menu | `team/RESEARCH/LEAD/loop2/make_random_v3.py` (d5881d3b95e4dff3), `menu_v2.py` (945a89b99c30abff) | LEAD loop 2; no release record |
| the per-fire file and its check | `team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/perfire_v1_to20260430.py` (2072f03fba520e72), `test_perfire_v1.py` (12996df3af189030), `split_v1.py` (e481ca008c72d6f5) | TEST, NOT REVIEWED (CLAUDE1 28 Oct); the GRADE and MONTH jobs run them |
| Outcomes V3 | `team/RESEARCH/tools/event_outcomes/event_outcomes.py` (341038cb717f8c31) | CANDIDATE: NOT APPROVED (`RELEASE_event_outcomes_V3_CANDIDATE.json`) |
| the hand-off test the GRADE job runs | `team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/lead_null_v1_to20251231.py` (22b58c1c72aab4f2) | TEST, NOT REVIEWED (CLAUDE1 29 Oct; part 09 lists it too) |
On 30 Oct the chain called these tools at their dev paths; chains v2_0_7 and v2_2_7 refuse to run from outside the Alarm folder (CHAIN_OUTSIDE_ALARM).

## Run from this folder (Alarm/03_Grading)
No data is needed: the test plants its own (the chain's own step-1 text, run in bash with a fake detect).
```
python3 -B ../_tools/run_isolated_v1.py tree/tools/month_parts/tests/test_month_parts_v1.py     # about 2 min: TESTS PASS, MUTANTS 19 of 19 killed
```
Proof that it runs from here and from a copy of the Alarm folder elsewhere: [RUN_PROOF.md](RUN_PROOF.md).
All tests of the Alarm folder, with a fresh temporary folder each: `python3 -B ../_tools/run_all_tests_v1.py <settings file> --part 03_Grading`
(add `--copy` to run them from a copy of the Alarm folder elsewhere).
Not run here: `tree/tools/month_parts/tests/smoke_month_parts_v1.sh` to `v4.sh` (runner jobs on the lab days, Mac only; their results
are in BASELINE.tsv) and the GRADE job (a template: the kit tests in ../Agentic fill it and run it with stub tools).

## Data and settings
A real grade runs only as a KIT_V5 job on the Mac. Settings keys it needs (`../settings/SETTINGS_<MACHINE>.env`, read with
`python3 -B ../_tools/settings_v1.py get <file> <KEY>`): `PYTHON`, `LAB_DAYS`, `SCRATCH` (the work folder), `RESEARCH_ROOT` (the run
folder: definitions, PREREG, receipts).
Still built in (`MACHINE_PATHS.tsv`, 26 rows BUILT_IN): the chain's interpreter and dev root (`alarm_grade_chain_v2_2_to20260430.sh:35`),
the roster, metric tables and every step tool at their dev paths (`:36-45, 59, 70, 73, 78, 81, 83`), the lab days (`:78`), and the same
in the four small runs. The GRADE job's own paths are in ../Agentic/MACHINE_PATHS.tsv. On another machine these need new editions that
read the settings file and take their tools from inside Alarm.
