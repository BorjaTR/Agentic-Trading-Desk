# TEST: every included test, run from a byte copy of this edition as a NEW seat (SCOUT, 8 Nov 2026, C218, C223, C230; LEARNING_LOOP_V1, built as RC5)

## How it was run (new seat, seat variables SET)
- `cp -Rp` of this folder to <SCRATCH_DISK>/tmp_SCOUT/rc4_newseat/release; `diff -rq` equal before and after the run.
- The runner ships here: `python3 -B TEST_RUN.py --release <copy> --seat <new seat folder> --tmp <temp off the internal disk> [--watch <folder no test may open>]`. It makes the seat (registers from generic/registers_template, pack_strategy from packs/strategy_draft, RULES.md), then sets every seat variable of generic/SETTINGS_TEMPLATE.md as README step 0 says (LL_SEAT_ROOT, LL_REGISTERS, LL_SEAT_ROOT_NAME, LL_REPORT_TEMPLATE, LEAK_SCAN_PATTERN_FILE, LL_GENERIC, LL_PACK, LL_SKILLS, LL_TEST_TMP, KNOW_V2_TMP) and leaves the alarm-only ones unset (KNOW_V2_SERIES, ALARM_SERIES_DIR, ALARM_SERIES_HEADER, ALARM_RUNS_DIR).
- Watch: an audit hook (sitecustomize.py on PYTHONPATH) logged every open, listing, copy or subprocess naming forensics/team/SCOUT: 0 lines, so no test read or wrote the alarm seat.
- The seat's registers were byte-equal before and after tests 1 to 13 (install report U1 fixed: test 3 now uses its own temp registers).
- `python3 -B`, PYTHONDONTWRITEBYTECODE=1: 0 `__pycache__` in the copy or the seat. Both temp folders were removed after the run.
- Set LL_TEST_TMP and KNOW_V2_TMP before any test: a test given none writes to its old default folder (<SCRATCH_DISK>/... or, for test 10, dry_test_v2 beside the series).

| # | test | command (folder in brackets) | result 8 Nov 18:2xZ (RC4) | time |
|---|---|---|---|---|
| 1 | knowledge_v2 | [generic/tools/knowledge_v2] `python3 -B -m unittest test_build_knowledge_v2` | Ran 33, OK (skipped=2: the v1 equality tests, reason printed) | 0.24 s |
| 1b | knowledge_v2 C218 fixes | [same] `python3 -B -m unittest test_knowledge_v2_c218` | Ran 5, OK (UNKNOWN_FID; held-out row before the finding; evidence change after a held-out row; init makes the folder; EVIDENCE values) | 0.06 s |
| 2 | reg.py audit | [generic/tools/registers] `python3 -B test_reg_audit.py` | Ran 6, OK | 0.04 s |
| 3 | reg.py import-report, seat LL_REGISTERS set | [same] `python3 -B test_reg_report.py` | Ran 4, OK; seat registers unchanged | 0.05 s |
| 3b | reg.py baseline (B6) | [same] `python3 -B test_reg_baseline.py` | Ran 4, OK | 0.25 s |
| 4 | messy_triage_v1 | [same] `python3 -B test_messy_triage_v1.py` | PASS 8 planted lines (7 open, 1 fixed skipped; M8 NO_LIVE_FILE) | 0.14 s |
| 5 | blind_kit_v1 | [generic/tools/drills] `python3 -B test_blind_kit_v1.py` | Ran 8, OK (3 gold-check tests C218; 3 N1 tests C223: no gold row, make with no --gold, make with a bad --gold) | 0.41 s |
| 6 | leak_scan_v1 | [same] `python3 -B test_leak_scan_v1.py` | Ran 7, OK | 0.18 s |
| 7 | agreement_v1 | [same] `python3 -B test_agreement_v1.py` | Ran 6, OK (one-value case NOT_COMPUTABLE) | 0.14 s |
| 8 | agreement_v1 self test | [same] `python3 -B agreement_v1.py --self-test` | SELF_TEST PASS (published Krippendorff example) | 0.08 s |
| 9 | alarm pack: queue_job_v15_scout | [packs/alarm/playground] `python3 -B test_queue_job_v15_scout.py` | Ran 7, OK | 0.44 s |
| 10 | alarm pack: bar_check_v2 | [packs/alarm/tools] `python3 -B test_bar_check_v2.py` | Ran 10, OK | 4.15 s |
| 11 | alarm pack: forecast_score | [packs/alarm/tools] `python3 -B test_forecast_score.py` | Ran 4, OK | 0.05 s |
| 12 | alarm pack: check_round_v1 | [packs/alarm/tools] `python3 -B test_check_round_v1.py` | Ran 8, OK (C219: 2 new, row quotes per job, old file quotes) | 0.35 s |
| 13 | alarm pack: pool_splits_v1 | [packs/alarm/tools] `python3 -B test_pool_splits_v1.py` | Ran 2, OK | 0.05 s |
| 13b | alarm pack: speed_report_v1 (C230) | [packs/alarm/tools] `python3 -B test_speed_report_v1.py` | Ran 3, OK (empty drill no crash, per-round step minutes, no receipts is no data) | 0.1 s |
| 14 | smoke: a new seat's empty registers | `reg.py check` | CHECK PASS drill runs 0 improvements 0 | 0.02 s |
| 14b | new seat ledger (B6): template PARTS.tsv, then the seat's own PARTS.tsv, `reg.py baseline who=<seat>`, `reg.py ledger-check` | `reg.py ledger-check`; README step 3 (a) to (c) | before: LEDGER_CHECK FLAG files 69 flags 69, exit 1 (as the review found); after the rewrite (4 files resolve in a new seat: its RULES.md and the {GENERIC} cells): BASELINE rows 4, then LEDGER_CHECK PASS files 4 flags 0 | 0.09 s |
| 15 | smoke: a new store, folder not made first, strategy pack with TODO bars | `build_knowledge_v2.py init --pack <seat>/pack_strategy/strategy_v0.json --dir <seat>/store_new/store` | exit 0 (note 1 fixed) | 0.03 s |
| 15b | smoke: a new store, alarm pack | `init --pack packs/alarm/alarm.json --dir <seat>/store_alarm` | exit 0 | 0.03 s |
| 16 | smoke: check of the new store | `check --pack packs/alarm/alarm.json --dir <seat>/store_alarm` | CHECK PASS errors 0 | 0.03 s |
| 16b | strategy pack check | `check --pack <seat>/pack_strategy/strategy_v0.json ...` | exit 1, REFUSED TODO value(s), by design (OPEN item 1) | 0.03 s |
| 17 | leak scan without a pattern (env unset) | `leak_scan_v1.py --secrets generic/LOOP.md --targets generic/prompts` | exit 2, REFUSED NO_PATTERN | 0.02 s |
| 18 | leak scan with the alarm pattern | `leak_scan_v1.py --pattern-file packs/alarm/HELDOUT_PATTERN.txt --secrets generic/LOOP.md --targets generic/prompts` | LEAK_SCAN PASS files 5 hits 0 | 0.02 s |
Result: TEST_RUN PASS, 25 of 25 runner rows (TEST.md row 14b = runner rows 14b.1 to 14b.3); WATCH_LOG_LINES 0; PYCACHE 0; registers unchanged by tests 1 to 13; copy byte-equal before and after.
RC5 (LEARNING_LOOP_V1): the same rows plus 13b, 26 runner rows; results from a byte copy as a new seat and from a copy of the install: release_staging/LEARNING_LOOP_V1_RELEASE_RECEIPT.md.

## Alarm seat rows (the alarm series given on purpose; run for RC3, knowledge_v2 is unchanged in RC4)
| # | test | command | result | time |
|---|---|---|---|---|
| 19 | knowledge_v2 with knowledge_v1 and the live store (read only), from this folder | [generic/tools/knowledge_v2] `KNOW_V2_SERIES=<the alarm series folder> KNOW_V2_TMP=<tmp> python3 -B -m unittest test_build_knowledge_v2 test_knowledge_v2_c218` | Ran 38, OK (33 + 5) | 1.53 s |
| 20 | the same in the source | [S/knowledge_v2] `python3 -B -m unittest test_build_knowledge_v2` and `... test_knowledge_v2_c218` | Ran 33, OK; Ran 5, OK | 0.62 s |
Row 19 and 20 golden test: the v2 check of a copy of the live store prints one MISMATCH, F0001 stored CONFIRMED/C1, computed SUPPORTED/S1+C1WAIT, because evidence was added to F0001 (L08 to L10) after its held-out row of 8 Nov 07:35Z. This is the B2 rule on purpose; the test computes the expected line from OPS_LOG and checks v2 prints exactly that (OPEN.md item 12).

## Failing before, passing after (C218, each fix in the source; receipts: the "before" run used the .pre_SCOUT_C218_20261108T175949Z twin with the new test)
| fix | test | before | after |
|---|---|---|---|
| B1 gold check | test_blind_kit_v1.py | FAILED 2 of 5 (exit 0, GOLD_CHECK PASS with no totals) | Ran 5, OK |
| B2 held-out order, notes 1 and 2 | test_knowledge_v2_c218.py | 5 of 5 fail (CONFIRMED/C1 twice, no SystemExit twice, FileNotFoundError) | Ran 5, OK |
| B3 NO_LIVE_FILE | test_messy_triage_v1.py | M8 came out NO_QUOTE | PASS 8 planted lines |
| B6 baseline | test_reg_baseline.py | 4 of 4 fail (no LL_REGISTERS, no baseline command: KeyError) | Ran 4, OK |
| agreement one value | test_agreement_v1.py | 1 of 6 fails (alpha 1.000 RELIABLE) | Ran 6, OK |
| install U1 | test_reg_report.py with the seat's LL_REGISTERS set | 3 of 4 fail, 5 rows written into the seat registers | Ran 4, OK, seat registers header lines only |

## Failing before, passing after (C223, RC4; the fix in the source S/build/blind_kit_v1.py; the "before" run used the twin .pre_SCOUT_C223_20261108T181953Z with the new test, both from copies on <SCRATCH_DISK>/tmp_SCOUT)
| fix | test | before | after |
|---|---|---|---|
| N1 no gold item | test_blind_kit_v1.py test_no_gold_row_fails (MAP with one item I01, no gold; two scorers `I01 TOTAL 2`) | FAIL: exit 0, `GOLD_CHECK PASS` | OK: exit 3, `GOLD NONE`, `GOLD_CHECK FAIL 1` |
| N1 make with no --gold | test_make_refuses_no_gold | FAIL: exit 0, a kit written (`items 1 (gold 0)`) | OK: exit 2, `REFUSED NO_GOLD`, no map written |
| N1 make with a bad --gold (`g.md`, `g.md=`, `g.md=x`) | test_make_refuses_bad_gold | ERROR: IndexError traceback | OK: exit 2, `REFUSED BAD_GOLD`, no map written |
| all | test_blind_kit_v1.py | Ran 8, FAILED (failures=2, errors=1), exit 1 | Ran 8, OK, exit 0 |
