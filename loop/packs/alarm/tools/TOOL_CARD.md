# TOOL CARD: packs/alarm/tools (LEARNING_LOOP_V1)
Every command, argument and env setting below is also in TOOL.json beside this card, read from the code. Placeholders: {GENERIC}/SETTINGS_TEMPLATE.md.

These tools read alarm receipts (ASSESS.tsv, SERIES_V2.tsv, STEP_11_GRADE.json, STATE_SPLIT_*CTX*.tsv, CARD.md lead15 cells), so they belong to the alarm pack, not to generic/.

## bar_check_v2.py
- Answers: the PROOF_RULES_V2 bars B1 to B4 and the kill rule over the series file; the RUN row of one run; the LOOK row after the one held-out look.
- Run: `bars --series SERIES_V2.tsv [--config SERIES_V2_CONFIG.json]`, `row --runf RUN --series F [--config F] [--write]`, `look --run-id L03 --series F --by-month a,b,c,d --t-pooled x --receipt SHA16 [--write]`.
- Exit: 0 done; 3 MISMATCH. Tests: test_bar_check_v2.py (temp under LL_TEST_TMP; header from SERIES_V2_HEADER.tsv).

## forecast_score.py
- Answers: Brier score and 80 pct coverage of each run's sealed forecasts against the pass rule.
- Run: `python3 -B forecast_score.py [L02 L03 ...]` with env ALARM_SERIES_DIR = the series folder (runs_v2/ and SERIES_V2_CONFIG.json; else the config beside the tool). Writes FORECAST_SCORES.tsv beside the tool (cannot write in a read-only install: OPEN.md).
- Tests: test_forecast_score.py.

## pool_splits_v1.py
- Answers: per CTX reading, the gap between the highest and lowest state pooled over memory runs by inverse variance, with sign agreement, I2 and a dependence-adjusted t (rho 0.5, written down, not fitted). Controls never read.
- Run: `python3 -B pool_splits_v1.py [--runs DIR] [--out FILE] [--rho 0.5] [--horizon 15m]` (default runs: env ALARM_RUNS_DIR). Exit 0.
- Tests: test_pool_splits_v1.py (2, planted, numbers worked by hand).

## check_round_v1.py
- Answers: while a run goes on, is any required step missing (step 0 block, CLAIMS and FORECASTS before each round's first job, power line, placebo, card cells equal to their receipts, card sha16 in RESULT, held-out cell left to the orchestrator)?
- Run: `python3 -B check_round_v1.py RUNF [--run-number N]`. Exit 0 nothing missing; 3 a step missing.
- C219 (RC4, from the alarm seat, L11 assessors): the FORECASTS check is per job: each MAC_JOBS forecast quote must equal the sha16 of its round's own sealed row(s) (JOB_SHEET_V1 (b)); an old `(file X)` quote must hash a start of FORECASTS.tsv.
- Tests: test_check_round_v1.py (8; C219 added 2: row quotes per job, old file quotes).

## build_run_v2.py, combine_readings_v1.py, part_a_v2.sh
- The alarm run builder (part_a_v2.sh calls build_run_v2.py) and the round 2 reading combiner. C225: the pooled Sep-Mar yardstick is read only from the orchestrator-only file the config names (yardstick_sepmar_file); a missing file is refused, SEPMAR_FILE_MISSING. test_build_run_v2.py ships (20 tests in the seat) but reads the alarm seat layout (ALARM_SERIES_DIR, dry_test_v2): run it in the seat, not from the release (OPEN item 16).

## speed_report_v1.py (C230)
- Answers: run, round and drill minutes against the targets (run <= 40, round <= 10, drill <= 5 min), from logs that already exist (LAUNCH_UTC.txt, RESULT DONE line, FORECASTS seals, DRILL_RUNS.tsv).
- Run: `python3 -B speed_report_v1.py --out <tsv> [--runs L07,L08] [--root <series folder>]` (pass --root from the release: the default is the folder above this one). Writes --out (kind, id, n, median_min, target_min, within) and prints a summary; a drill, part or step with no numeric minutes prints "no data" (was a crash on L11).
- Tests: test_speed_report_v1.py (3; temp under LL_TEST_TMP).
