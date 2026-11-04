# 01 Detection: the alarm's rule makes the fire list

An alarm is a rule on data known at the moment. Detection runs that rule over the lab days, coin by coin, and writes the fire list: one
row per fire with the coin, the time (unix seconds) and the side (+1 or -1), plus what was known on every coin-day. Nothing after the
fire is read here (no price path, no outcome). The fire list then goes to the freeze (part 02) and the grade (part 03).

Only released editions are here (the owner, 30 Oct 2026, option a: "released editions only" in GitHub). Every file under tree/ is a
byte copy of the team's dev tree (`SOURCES.tsv`: each file's dev path and sha16), never edited here.

## Layout
- One folder per tool at the top, with its README, SCOPE, ARCHITECTURE and CHANGELOG: [detect/](detect), [alarm_design/](alarm_design),
  [alarms/](alarms). Each README is a byte copy of the tool's own (detect/ARCHITECTURE.md too: the idea_to_grade architecture). The other
  documents say on their first line that SCOUT wrote them for the repo.
- `tree/`: the byte copies of every file the tools run, in the dev tree's layout from the forensics root (`tree/team/RESEARCH/tools/<tool>/`,
  `tree/team/LAB3/...`, `tree/team/OUTSIDE/...`), so the tools' relative paths work unchanged.
- `proof_harness/pytest_main.py`: written in this repository (not a copy). It hands its arguments to pytest, so that
  `_tools/run_isolated_v1.py` can run the pytest files; `--gate-run` points labcore's run switch at a temporary file reading RUN, for the
  test process only (no tool file is changed).
- `MANIFEST.tsv` (what is copied), `SOURCES.tsv` (sha16s), `MACHINE_PATHS.tsv`, `RUN_PROOF.md`, `CHANGELOG.md`, `REMOVE.tsv` (files SCOUT
  deletes before the commit).

## Tools
| tool | what it does | owner | edition here | status |
|---|---|---|---|---|
| [detect](detect) (`tree/team/RESEARCH/tools/idea_to_grade/detect.py`) | one alarm definition (JSON) in, its fire list out: EVENTS.tsv (coin, t, side) and COVERAGE.tsv (every coin-day: PRESENT, NOT_LISTED, NOT_BUILT, HOLE, REFUSED), for any coins and days inside a research window | STRATEGY/LEAD (built by i2g_detector) | DETECT_V1 in release idea_to_grade V2_3_1 (25 Oct), detect.py 83c52bfd27166f76 | released (two signatures, README section V2.3.1); the KIT_V5 COUNT job checks this sha16 |
| [alarm_design](alarm_design) (`tree/team/RESEARCH/tools/alarm_design/`) | the lab engine: what a definition means (inputs on the 5 s clock, conditions, onset, refractory, side); detect imports it | ALARM | release V3_8_1 (25 Oct), alarm_design_v2.py 70de3f03faaeaa74 | released (an independent checker signed) |
| [alarms](alarms) (`tree/team/RESEARCH/tools/alarms/`) | the landed finders: each turns lab days into one registered alarm's fire list (N1, N2, N3, N4, N5, N9, K0, Q1, Q4, B7, B8, O1 and O2, O5, Q16), with a plain-loop twin for proof | SCOUT (the bench), QUANT (the finders) | the 11 files LANDED in BASELINE.tsv (20-21 Oct), e.g. onset_band_v6.py 9acf9cc8a0b24f53 | released (landed after review) |

Also copied, because these tools run them: `model_v1/matched_controls_v1.py`, `event_profile/` (clock_series, event_profile), `labcore/`
(release V2_7 files), the metric gate `metric_brief.py` and its four tables, the window table `freeze_judge/WINDOWS_V1.tsv`, lab3 (the 9
files the release pins; the same bytes as `../_vendor/LAB3_code`), the coin roster and one real definition. idea_to_grade.py is here only
for `read_detect`, the reader of a detect run that a test uses; grading itself is part 03.
What changed in each release: [CHANGELOG.md](CHANGELOG.md).

## In development (not here)
Dev tree: `<LAB_REPO>/forensics/`. sha16 on 30 Oct 2026.
| tool | where (dev tree) | status |
|---|---|---|
| finders not landed: a01_onset v1, v2, v3; a02_climax_v3; a02_grid_v1, a02_grid_read_v2; a03_wave_v1, a03_inwave_v1; a08 (3); a18; b6; c1; m1-m5; n6 (3), n7, n8 (3), n10, n11; p2-p11; ref_fires_a01a02_v1; and the helpers n8_c11_check_v1, n10_codes_peek_v1, alarm_offer_v1 (SUPERSEDED) | `team/RESEARCH/tools/alarms/` | DRAFT in BASELINE.tsv, or no row (TEST) |
| the alarm check runner (alarm_checks_v1.py, ALARM_CHECKS_V1.tsv) | `team/RESEARCH/tools/alarms/` | no BASELINE row (TEST) |
| detect_aw1.py: detect.py with the alarm agents' window table (Mar-May) | `team/RESEARCH/tools/alarm_process/detect_aw1.py` (f03254fd5420e56b) | TEST, NOT REVIEWED (STRATEGY 28 Oct); TOOLS_REGISTRY status KIT |
| the grade chain's list step: detect.py on two roster halves, merged into `<V>_FIRES_V1_LIST.tsv` | `team/RESEARCH/tools/alarm_process/alarm_grade_chain_v2_0_to20251231.sh` (94273faf1e927ddc), `..._v2_1_to20260430.sh` (99e8a229617cb2e2, runs detect_aw1) | TEST, NOT REVIEWED; the chain is part 03 |
| the COUNT job of the alarm kit (fires, waves and coins per month; runs detect.py) | `team/RESEARCH/ALARM_DESIGN/KIT_V5/jobs/JOB_COUNT_V5.job.sh.txt` | KIT_V5: TEST, NOT REVIEWED |
| hand checks of a definition (three cases by hand: fire, boundary, missing) | `team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/` (hc_defs_v1_to20251231.py, hc3_v1/, defcheck_v1-v3) | BUILT or TEST in that run's TOOLS_BUILT.tsv |
| the definition template and an example | `team/RESEARCH/ALARM_DESIGN/KIT_V2/templates/DEF_TEMPLATE_V2.json`; `runs/CLAUDE1_20261028/ideas/LOOP2/defs/LP2_DAYPOKE_DEF_V2.json` | kit and run files; the format itself is in alarm_design/README.md section 2 |
Not this part: month_parts (the Sep-Apr chain with detection in 26 coin parts) is in 03_Grading.

## Run from this folder (Alarm/01_Detection)
No data is needed: the tests plant their own. detect's tests read the metric tables through three variables (the defaults point into the
dev tree, MACHINE_PATHS.tsv), so set them first.
```
X=$PWD/tree/team; T=$X/RESEARCH/tools
export METRICS_V1=$X/LAB3/METRICS_V1.tsv METRIC_TRAPS=$X/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv CATALOGS=$T/alarm_context/CTX_CATALOG_V1.tsv:$T/alarm_profile/EPI_CATALOG_V1.tsv
python3 -B ../_tools/run_isolated_v1.py $T/alarm_design/test_alarm_design_v2.py                                        # 33 tests
python3 -B ../_tools/run_isolated_v1.py proof_harness/pytest_main.py -q -p no:cacheprovider $T/alarm_design/test_onset_knownness.py   # 3
python3 -B ../_tools/run_isolated_v1.py proof_harness/pytest_main.py --gate-run $T -q -p no:cacheprovider -k "not real and not hard_kill" $T/idea_to_grade/test_detect.py   # 20
python3 -B ../_tools/run_isolated_v1.py proof_harness/pytest_main.py --gate-run $T -q -p no:cacheprovider $T/idea_to_grade/test_detect_a53.py   # 6
for t in onset_band_v4 onset_band_v6 n1_busy_burst_v2 k0_busy_now_v1 b8_roll_v1 b7_wide_pressed_v1 o1_flush_v2 alarm_view_v1 o5_both_v2 q16_vwap_v1; do
  python3 -B ../_tools/run_isolated_v1.py $T/alarms/test_$t.py; done
```
Not runnable from here (RUN_PROOF.md): the 11 REAL tests of test_detect.py (they read the lab store at the built-in path and the
outside team's committed outputs under team/OUTSIDE, which are data) and test_hard_kill_leaves_nothing_running (it starts detect.py as a
child process, which reads the built-in run switch and the lab store).
Proof that the rest run from here and from a copy of the Alarm folder elsewhere: [RUN_PROOF.md](RUN_PROOF.md).

A real detection run (on the owner's Mac it runs as a runner job):
```
S=../settings/SETTINGS_<MACHINE>.env; PY=$(python3 -B ../_tools/settings_v1.py get $S PYTHON); LAB=$(python3 -B ../_tools/settings_v1.py get $S LAB_DAYS)
nice -n 10 $PY -B $T/idea_to_grade/detect.py --definition <definition.json> --lab-root $LAB --roster $X/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json \
  --coins ALL --first 20250912 --last 20251231 --research-window 20250901:20251231 --out <new folder outside Alarm> --workers 8
python3 -B $T/alarms/onset_band_v6.py <Q1|Q4|...> $LAB ../_vendor/LAB3_code <new out folder> <first day> <last day> <last readable day> <coin> ...
```

## Data and settings
Settings keys a real run needs (`../settings/SETTINGS_<MACHINE>.env`): `PYTHON`, `LAB_DAYS`. Everything else comes from this folder.
Still built into the code (`MACHINE_PATHS.tsv`, status BUILT_IN):
- the run switch `team/FEED/stops/BACKFILL_GATE.txt` of the dev tree (`tree/team/RESEARCH/tools/labcore/jobgate.py:14`): detect refuses
  GATE_NOT_RUN unless its first line is RUN. There is no settings key for it yet (the owner decides).
- the metric tables' default folder, the dev tree (`.../reading-metrics/scripts/metric_brief.py:13`): set METRICS_V1, METRIC_TRAPS and
  CATALOGS as above, or the run reads the dev tree (and fails on another machine).
- LAB1's protected store list (`tree/team/LAB3/code/lab3/law.py:55-57`).
- `test_detect_a53.py:7` puts the dev tree first on the import path: on the Mac this test imports the dev copies (its isolation fails
  there); in the VM that folder does not exist and the copies here load.
- I2G_PINS_V2.json and idea_to_grade.py lines 28-32 name dev paths too, but only a graded run reads them (part 03); detect does not.
Data is never copied: the lab days (LAB_DAYS) and the stored event lists a definition may name.
Nothing from May 2026 onward is read: detect refuses any month outside BUILD in WINDOWS_V1.tsv (Sep 2025-Feb 2026) and lab3's law seals the rest.
