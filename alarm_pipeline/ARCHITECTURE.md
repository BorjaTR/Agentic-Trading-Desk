# ARCHITECTURE: alarm_pipeline ALARM_PIPELINE_V1_4_1 (SCOUT, 7 Nov 2026; status: RELEASED, TEST, NOT REVIEWED)

ALARM_PIPELINE_V1_4_1 (SCO-A183): the V1_4 design (block SEPMAR graded, OUT_OF_SAMPLE and NEVER_SEEN refusals in step 01) with pipe_mac_v3 on ALARM_V1_22_1 and the bridge MAC_DESK_V49_3; the sections below are the V1_3_3 text with the V1_4 changes named in README.md and CHANGELOG.md.

From volat_release/Templates/ARCHITECTURE_TEMPLATE_V1.md, short form. Facts from the code docstrings and job 20270215.

## 1. Identity
| field | value |
|---|---|
| tool | Alarm/alarm_pipeline |
| version | ALARM_PIPELINE_V1 |
| owner seat | SCOUT |
| reviewers | none yet |
| status | RELEASED (RELEASE_ALARM_PIPELINE_V1.json), TEST, NOT REVIEWED |
| related | the Alarm kit (queue_job, ledger, registry), alarm_understand (step 17 CARD), classify_line (step 19) |

## 2. Purpose and scope
See SCOPE.md. Not done here: grading rules (Alarm/alarm kit), card answers (alarm_understand).

## 5. Data
| input | where |
|---|---|
| INPUT.json | written by the agent, template tree/team/SCOUT/pack_kit/alarm_pipeline_v1/INPUT_TEMPLATE.json |
| PIPE_SETTINGS.json | runner root, queue, kit paths |
| runner status files | <runner>/<Q>/logs/<job>.status (exit=) |
Outputs: the run folder (STEP_<nn>_<NAME>.json each), the card files and INDEX row of step 22.

## 6. Design
| part | file | job |
|---|---|---|
| entry, step engine | tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py | init, next, run (45 s budget), status, retry |
| card writer | tree/team/SCOUT/pack_kit/alarm_pipeline_v1/card_v2.py (card_v1 kept) | ALARM_CARD md/tsv, INDEX row with version column; the "hypothesis at CLAIM" line from the meta json (sealed INPUT mechanism_hypothesis), never the mechanism json (V1_3_2) |
| mechanism | tree/team/SCOUT/pack_kit/alarm_pipeline_v1/mechanism_v2.py (mechanism_v1 kept) | one alarm to one MECHANISM_MAP_V1 id (pinned 36faecd0eaa59b85), NONE, UNKNOWN or CANDIDATE |
| job template | tree/team/SCOUT/pack_kit/alarm_pipeline_v1/CARD_JOB_TEMPLATE_V2.sh | the step 17 runner job |
| shipped copies | tree/team/RESEARCH/PLAYGROUND/tools/PG20261105_alarm_understand, tree/team/SCOUT/pack_kit/classify_line_v1 and v2, tree/team/RESEARCH/LEAD/MECHANISM_20261106/MECHANISM_MAP_V1.md | dev layout kept |
Steps: 01 INPUT ... 11 GRADE ... 17 CARD 18 MECHANISM 19 CLASSIFY 20 LOG_TRIED 21 LOG_LEDGER 22 HANDOFF.
Exit codes: 0 DONE, 10 WAIT, 3 STOP, 2 usage.

## 6e. V1_3_3
V1_3_3 (SCO-A172 fix, released by SCO-A171, SCOUT, 7 Nov 2026; learning series runs 1 to 3: step 18 MECHANISM read UNKNOWN, legs never measured): the step 17 bundle is built --from-job (kitq GRADE) and bundle_builder_v1.py writes STORE_RUN and CONTEXT.tsv only on the --from-gg path, so mechanism_v2 found no binding of the DEF and counted 0 onsets. mechanism_v2.py (a6e81cb5a0fb8a86) now binds the DEF on the kitq route (binding KITQ_GRADE_JOB) and measures the legs. Tests: test_mechanism_v2.py 26 (t18 to t26 new; the V1_3_2 code is red on t18 and t26), mutants_mechanism_v2.py 25 (mu18 to mu25 new). Replay J20270489 (read only): run_3 BIDCATCH_V1 UNKNOWN -> FORCED_OUT, share 1.0, 25681 of 25681 onsets; run_1 LIQLEAD_V1 stays UNKNOWN (oi now measured, its liq DEF condition is not the map leg, K1-43). Every other file is V1_3_2 byte for byte (card_v2.py a85e1c0e29acc332 kept).

## 6d. V1_3_2
V1_3_2 (SCO-A170, SCOUT, 7 Nov 2026; learning series run 1, curator row R1-11, card review R04): the card line "hypothesis at CLAIM" now comes from the run's sealed INPUT mechanism_hypothesis, which step 22 already writes into HANDOFF_META.json as hypothesis; card_v2.py (a85e1c0e29acc332, claim_hypothesis) never reads it from the mechanism json, a result (the card job runs mechanism_v2 without --hypothesis, its MECHANISM.json holds null, and V1_3_1 printed "hypothesis at CLAIM: None" on LIQLEAD_V1 although INPUT, HANDOFF_META and STEP_18 say FORCED_OUT); no hypothesis in the meta prints "-". Nothing else changes: the card tsv, the INDEX row and every other line are byte equal (real-input check on run_1/pipe3: V1_3_1 reproduces the filed card byte for byte, V1_3_2 differs only on that line). card_v2.py is replaced in place, not added as a new name, because every pipeline settings file pins current/.../card_v2.py: the fix reaches the hunters when current moves. tests/test_card_v2.py c5 to c7 (7 tests; c5 to c7 fail on V1_3_1), tests/mutants_card_v2.py (4 planted faults on the changed lines). card_v1.py (history, not in the pipeline settings) keeps the old line.

## 6c. V1_3
V1_3_1 (SCO-A162R, 7 Nov 2026): V1_3 (held, job 20270422: install, 3/3, 52/52, 14/14, then test_pipe_e2e_v2 E5 4 of 5: MAC_SCRATCH named a folder not made yet) with only that test making its scratch folder; V1_3 stays held history, never current. V1_3 (SCO-A162R, SCOUT, 7 Nov 2026; the owner 22:53 Berlin "The pipeline has to work for any date and any alarm built on any metrics we choose"): (1) alarm_pipeline_v1_3 (c6bb3152c6c0153e): the window is made true. The E2E matrix found V1_2 checked the INPUT window only against the open months and then never used it: step 11 GRADE always grades the kit block 10 Sep to 31 Dec 2025 (chain *_to20251231), so a Dec-Jan window ran to DONE ALL graded Sep-Dec and a JANMAR window crashed at step 17 CARD (tests t42 to t49 red on v1_1, 0 of 8). Now step 01 checks the window against its block and refuses by name: WINDOW_OUTSIDE_BLOCK (a window month outside the block; one run reads one block), BLOCK_NOT_GRADED (JANMAR: the pack grades Jan-Mar only by a MONTH job on a frozen rule; GRADE and hc_defs_v4 read Sep-Dec only), WINDOW_NOT_GRADED (no graded day in the window), HC_OUTSIDE_WINDOW, BAD_BLOCK; STEP_01 records block, graded_days, window_graded, window_months; STEP_11 adds window_read, the GRADE's own by-month lead, waves and counted of the window's months (copied, never recomputed; a window shorter than a month is read at month grain, said in window_note); DECIDE still reads the whole block. Step 08 SEAL_MENU: the gate's refusal (rc 2) is STOP MENU_REFUSED with the gate's own line (V1_2 showed TOOL_RC "menu rc 2"). (2) pipe_mac_v2 (pipe_mac_v1 loading alarm_pipeline_v1_3 at its pin), test_pipe_mac_v2 (M2 now proves the rel tool ran in RUN by its cwd; the old check matched the absolute arguments, mutant cwd_lost survived in job 20270403), mutants_pipe_mac_v2 (no_dry on the replay code). (3) pipe_e2e_v2: a case passes on 22 of 22 or on exactly the named refusal its INPUT asks for (e2e_expect); a pipe_mac rc other than 0, 3, 10 is CRASH; E2E_RESULT.tsv gains expect, verdict, pipe_rc; test_pipe_e2e_v2 (5). (4) The matrix acceptance shipped: e2e/E2E_MATRIX.sh and e2e/matrix_v1 (24 cases: each month Sep 2025 to Mar 2026, a month-end range, one day, a window across the block end, 14 graded alarms of 7 metric families: funding, open interest incl. market-wide, liquidations, flows incl. market-wide, price move, premium, engine; SIZE and SIDE; one coin and five; 202 to 18483 fires) and e2e/E2E_RUN_V2.sh (the two V1_2 cases on pipe_e2e_v2). Matrix pass 0 (job 20270411, dev source, before the last three fixes): dates 10 of 10 as asked (Sep, Oct, Nov, Dec, the month-end range and the one day 22 of 22 in 146 to 163 s; Jan, Feb, Mar BLOCK_NOT_GRADED; the Dec-Jan window WINDOW_OUTSIDE_BLOCK); alarms 22 of 22 for CROWDDRAG, CLOSEOUT, LIQCHAIN (one coin), BOTHFLUSH, MAKERTIDE, WICKBACK, LEGSTRETCH, HLCROWD (69 to 499 s, FIRSTLOOK and the card most of it). Found there and fixed in V1_3: the menu gate's refusal hidden as TOOL_RC (WINDFALL E2.S01, MKTCUT E2.S05, SIGNFLIP E1.S04, now MENU_REFUSED, asked by those cases), FIRSTLOOK refused ALREADY LOOKED on replays whose input names no FIRSTLOOK job (ENGINEHOUR, WIDESWEEP, now adopted), R1 PASS never looked (PERPHOUR, WICKBACK, now looked); PERPHOUR stops at 20 TRIED_DIFFERS by design (TRIED WORKED, ledger UNSURE). The two release passes are in the release report. The V1_2 files stay byte equal (pipe_mac_v1, pipe_e2e_v1, E2E_RUN.sh: the V1_2 acceptance).

| window field | where it acts (V1_3) |
|---|---|
| block | step 01: SEPDEC graded (20250910..20251231), JANMAR refused; step 17 card job FIRST/LAST |
| window | step 01: inside the block, at least one graded day; step 11 window_read (months); step 20 months_read |
| hc first, last | step 01: inside the window; step 04 hc_defs_v4 (one month, five coins) |

## 6b. V1_2
V1_2 (SCO-A162, 6 Nov 2026; the owner 22:02 Berlin "Can't you run it with remote control?", 22:52 "We need tools that work", 22:53 "any date and any alarm"): (1) alarm_pipeline_v1_1 (f4514978eba99d4e): step 20 LOG_TRIED writes the row the released add_row accepts (thought_file the sealed card path, fail_layer from the verdict, failed_stage none for WORKED, closest_existing the step 16 nearest line, the 16 learning columns unknown or none), and step 21 LOG_LEDGER runs before step 20 (the TRIED row names the ledger result row); numbers and names of the steps unchanged. (2) pipe_mac_v1 (710344943afa6f04): the Mac mode, all 22 steps inside one runner job, no VM bridge: rel tools pinned, run in the run folder with every path word absolute from RUN and the bridge log name; kitq through queue_job_v16 with the bridge job header (pipe_kitq_v1 7ca1bef077c352f3); the replay adoption of an ALREADY-graded job; the card job from ALARM_UNDERSTAND_V1_2; --refile-failed; per-step seconds in TIMES.tsv; no time window. (3) The end-to-end acceptance shipped: pipe_e2e_v1 (422b3fa2bf40ac2d) and e2e/E2E_RUN.sh, one command, no agent, each case in a new pipe folder; cases WIDEBLOCKS V1 Sep-Dec replay (compared with trial I) and CROWDDRAG V1 replay (drill K INPUT 4030570258a5484f). Job 20270400: two runs, 4 of 4 cases 22 of 22, trial I 16 of 16 SAME both times, run a and run b STEP numbers 44 of 44 SAME; WIDEBLOCKS 173 s and 148 s, CROWDDRAG 58 s and 62 s (the card step most of it). V1_1 (installed earlier, job 20270389) is history: it lacked the replay adoption, the absolute path words and the 21-before-20 order.

## Run it on the Mac: one runner job
```
<PYTHON> -B tree/team/SCOUT/pack_kit/alarm_pipeline_v1/pipe_mac/pipe_mac_v1.py run <pipe folder> [--budget-s 2700] [--poll-s 5] [--until N] [--retry-stop N] [--refile-failed N]
bash tree/team/SCOUT/pack_kit/alarm_pipeline_v1/e2e/E2E_RUN.sh <new out folder>     (the acceptance: all cases, 22 steps each)
```
The pipe folder holds INPUT.json and SETTINGS.json (VM paths are mapped to <HOME>; MAC_SETTINGS.json is written beside). Exit 0 done, 10 budget spent while a job runs (run again), 3 STOP, 2 refused.

## 7. The one command
python3 -B tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py init <run> --input INPUT.json --settings PIPE_SETTINGS.json; then run <run>.

## 9. Placement
volat_release/Alarm/alarm_pipeline/ALARM_PIPELINE_V1/tree/... (dev layout), current -> ALARM_PIPELINE_V1.

## 12. Tests
| test | Mac job 20270215 | VM |
|---|---|---|
| tests/test_pipeline_v1.py | 41 of 41 | 28 PASS shown, no RESULT line (incomplete) |
| tests/test_card_v2.py | 4 of 4 (V1_3_2: 7, c5 to c7 the CLAIM hypothesis; the release job of V1_3_2) | 7 of 7 (SCO-A170) |
| tests/test_mechanism_v2.py | 17 of 17 (V1_3_3: 26, t18 to t26 the kitq binding; mutants 25) | 26 of 26 (SCO-A172; the V1_3_3 release job) |
Mutant receipts in tree/team/SCOUT/pack_kit/alarm_pipeline_v1/tests/receipts. Planted and fake runner data only.

## 13. Release
Staged by SCO-A155 (stage_v1.py copy), tested from copies (job 20270215), installed by SCO-A159 with cp -pR, sealed into RELEASE_ALARM_PIPELINE_V1.json (every file sha16).

## 15. Safety
No rm, no git, twins before INDEX.tsv edits, never deletes.

## 19. Open
Not reviewed; no real end-to-end run from this install; the VM run of test_pipeline_v1 did not finish.
