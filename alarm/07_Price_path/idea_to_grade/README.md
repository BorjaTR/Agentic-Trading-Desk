# idea_to_grade — from an alarm idea to its opportunity grade, in one command (VERSION I2G_V1)
Owner 25 Oct 2026 11:59Z: "finish the tool and launch it as soon as possible". Paper research only: reads stored lab data, never trades.
Design: ARCHITECTURE.md. Detector contract: INTERFACE_V1.md. Builders: i2g_detector (detect.py), i2g_grader (everything else).

## What it answers (plain words)
After every alarm of an idea: if you entered with the alarm (FOLLOW) or against it (FADE) - filled at the first 3 s close traded after
alarm + 9 s (6 s execution delay + BED fill_v2's own 3 s) - how often did the price then give
you +0.2 % ... +2.0 % within 15 min ... 4 h, how much did it first go against you (heat), how long did it take, and how does that compare with
up to 10 "matched moments" of the same coin (same week, same hour, similar activity, no alarm just before) where nothing fired?
It describes opportunity. It does not say the alarm makes money, or why.

## Run it (normal priority, nice 10; the team slot tool first)
```
PY=<PYTHON>; T=<LAB_REPO>/forensics/team/RESEARCH/tools/idea_to_grade
R=<LAB_REPO>/forensics/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json
SLOTS=<LAB_REPO>/forensics/team/RESEARCH/LEAD/tools/slots_v1.py
# an idea (fresh detection), all 52 roster coins
python3 $SLOTS run <agent> 8 -- env PYTHONDONTWRITEBYTECODE=1 nice -n 10 $PY -B $T/idea_to_grade.py --idea <definition.json> --roster $R \
   --coins ALL --first 20250912 --last 20260228 --research-window 20250901:20260228 --out <new folder> --workers 8
# an event list instead of an idea (coverage from the PRICE index; the list is pinned by its sha16)
... $T/idea_to_grade.py --events <list.tsv> --events-sha16 <sha16> --roster $R --coins BTC,ETH,SOL --first ... --last ... --research-window ... --out ...
# a named group: --group <NAME> --group-file <TSV with group (or sector) and coin columns>, e.g. team/RESEARCH/tools/cause_label/SECTORS_V1.tsv
```
- `--research-window FIRST:LAST` is required (no date lives in the code). Every month in it must be a BUILD month of
  team/RESEARCH/tools/freeze_judge/WINDOWS_V1.tsv and pass lab3/law.py, and first..last must lie inside it; else REFUSED before any read.
  Today's BUILD window is 20250901:20260228. Prices after the window's last day are never read (the known path stops at that midnight).
- Exactly one input: `--idea` (detect.py definition), `--events` + `--events-sha16`, or `--detect-run` (tests only).
- `--workers` 1..8 (team cap 8), `--max-rss-gb` (default 16: the sampled RSS of the whole process tree stops the run above it).
- The command must run under `nice -n 10` (else NICE10_REQUIRED) and with the recorder gate RUN (else GATE_NOT_RUN).
- Exit 0 prints one JSON line {status COMPLETE, out, wall_s, timing_s by phase, parents, tree_peak_gb}. Exit 2 = REFUSED <CODE> (table
  below). Exit 1 = an unexpected error (a bug: the staged folder is kept as <out>.failed_<stamp> with FAILED.json).
- Code identity: I2G_PINS_V2.json lists every Python file a run executes (39: this tool, detect.py, the kernels, lab3, labcore, the
  outside modules); the run refuses before staging when one differs (KERNEL_DRIFT) or a process executes an unlisted file (UNPINNED_MODULE),
  checks every worker's files and the detector's code list, and re-hashes every pin before publishing (CODE_CHANGED). A changed file is a
  new release: `release_pins.py <new pins file>`.

## Refusals (exit 2, `REFUSED <CODE>: detail`)
| when | codes |
|---|---|
| before anything is staged (no folder written) | BAD_DAY (not a real YYYYMMDD day), RESEARCH_WINDOW, RESEARCH_WINDOW_NOT_BUILD, RESEARCH_WINDOW_SEALED, SELECTION_OUTSIDE_WINDOW, WORKERS, GATE_NOT_RUN, NICE10_REQUIRED, OUTPUT_EXISTS, PINS_FILE, KERNEL_DRIFT, UNPINNED_MODULE, EVENT_LIST_MISSING, EVENT_LIST_SHA, EVENT_LIST_INVALID (fractional time, onset after the alarm, duplicate, bad side), EVENT_SIDE (side 0), DEFINITION_WINDOW_MALFORMED, DETECT_<code> (the detector's admission: definition, roster, coins, group), DETECT_RUN_MISSING / _INVALID / _EXTRA_FILE / _FILE_CHANGED, FIXTURE_DETECT_RUN |
| during the run (the staged folder becomes <out>.failed_<stamp>/FAILED.json; no RUN.json ever) | SOURCE_CHANGED (a PRICE part changed, appeared or disappeared while the run used it), MEMORY_LIMIT, GATE_NOT_RUN, DETECT_<code>, DETECT_RANGE, DETECT_READ_OUTSIDE_WINDOW, KERNEL_DRIFT / UNPINNED_MODULE (a worker), CENSUS_POPULATION, INCOMPLETE_EDGES, OBSERVATION_IDENTITY / _CONFLICT / _COUNT, COHORT_CENSUS, EVENT_LIST_CHANGED, IDEA_CHANGED, CODE_CHANGED |
| reading a run (`verify_run` / `read_run`) | RUN_NOT_PUBLISHED, RUN_INCOMPLETE, RUN_CHANGED_AFTER_COMMIT (a listed file changed or missing, a file added, the RUN.json body edited), RUN_SCHEMA, RUN_INVENTORY (the manifest does not name exactly the required files), RUN_INCONSISTENT (cohorts, parents, detail arrays or measured rows disagree with RUN.json) |
A missing frame file inside an existing PRICE part is an integrity error (the run fails), never "no prices"; only lab3's NotBuilt (no
PRICE part that day) means no prices. A hard-killed run leaves no worker: each worker exits within 0.2 s of its parent's death.

## Clocks (when each published row is known)
- OBSERVATIONS.tsv known_at_us = as_of_us + 14,466 s (alarm_stamp.offset_s: 6 s delay + 60 s longest fill wait + 4 h hold).
- PARENTS.tsv known_at_us = the latest of its own observation, its eligible controls' observations and, for a drawn parent (MATCHED,
  NO_ELIGIBLE), 00:00 after its last candidate day (+7 d inside its split part). Matched controls are a benchmark built from the week
  around the alarm, never a live input.
- UNAVAILABLE.json known_at_us = 00:00 after the latest candidate day whose coverage decided the abstention.

## What you get (<out>/, all at once; RUN.json is written last and lists every file with its sha16)
| file | content |
|---|---|
| RUN.json | inputs (idea or list + sha16, roster, selector, dates, window), settings, counts, phase times, memory, every code sha16 |
| detect/EVENTS.tsv, COVERAGE.tsv, DETECT_RUN.json | the alarms and every requested coin-day's coverage (INTERFACE_V1.md) |
| matches/CENSUS.tsv | every parent: MATCHED, NO_ELIGIBLE, NO_COVARIATE, PARENT_OUT_OF_SPLIT or COMPARISON_UNAVAILABLE, its match count and activity |
| matches/EDGES.tsv | every matched moment (parent, moment, side, weight 1/n, draw index, own flag BEFORE_30M / WITHIN_H / empty = eligible) |
| matches/BALANCE.tsv, COMPARISON_COVERAGE.json, UNAVAILABLE.json | balance by month (SMD before/after), census by month, abstained parents and why |
| measurements/OBSERVATIONS.tsv + VALUES.npy + NAMES.json + REASONS.json | one row per parent or eligible moment x FOLLOW/FADE: the 55 STAMP fields (filled, fill wait, known seconds, fill price, seconds to each offer / heat level 0.1 .. 2.5 %); empty cells keep their reason (NOT_REACHED, STALE, NO_FILL, GAP, NO_DATA) |
| grading/COHORTS.json | 190 cohorts (FOLLOW/FADE x offer 0.2 .. 2.0 x 15, 30, 60, 120, 240 min) x (ALL + each month): standalone and paired summaries |
| grading/PARENT_DETAIL.npz | per cohort x parent (ALL slice): status (0 UNMATCHED, 1 PARENT_REACH_UNKNOWN, 2 CONTROL_REACH_UNKNOWN, 3 PAIRED), parent reach, control reach, paired gap, unknown control mass; eligible edges and mass per parent |
| grading/PARENTS.tsv, GRADED_EDGES.tsv | parent ids, event ids, wave ids, census, observation rows; the graded edges per direction |
| grading/REPORT.md | the outside report's table (reach and paired gap for every cohort) and coverage by month |
Read it in code: `idea_to_grade.read_run(out)` (refuses a run that is not COMPLETE or changed after commit).

## How to read a cohort summary (COHORTS.json -> cohorts[i].profiles[j].summary)
- standalone.reach_probability: the share of alarms (each WAVE of alarms within 30 min counts once; its alarms share its weight) that
  reached the offer within the horizon, among those whose answer is known. conditional.hb / offer_s / alarm_offer_s: quantiles 0.5 / 0.75 /
  0.9 of heat before the offer (%), seconds from the fill to the offer, seconds from the alarm to the offer, over the alarms that reached it.
- paired: only alarms with a known answer whose every eligible matched moment is also known; parent vs control reach_probability and
  reach_gap (alarm minus moments). conditional_quantile_differences: alarm minus moments, per quantile.
- coverage: parents, eligible edges, paired parents, unmatched, unknown. A gap is descriptive: no uncertainty band is claimed
  (dependence between alarms is not established).

## Evidence
CURRENT BYTES (V2.3.1, A54-FINAL-01 onset repair): idea_to_grade.py 60aa3efb19048028, i2g_engine.py 10c1286722bf19e2,
i2g_grade.py 73892d5719a7e2c3, detect.py 83c52bfd27166f76; pins I2G_PINS_V2.json (39 files; its sha16 is in the release record). The release record is cut on
labcore V2_7: `release_pins.py` (when an executed file changed) then `release_record.py RELEASE_idea_to_grade_V2_3_1.json <nested releases>`.
Reading a run: this tool's checks first (body digest, schema, exact inventory, files on disk, counts), then the shared S1 run check
(run_manifest_candidate 1a99409b: sealed manifest, root-file inventory, bytes).
V2.3.1 adds: shared alarm_design V3.8.1 preserves a known-false shared prefilter as an OFF predecessor, even when a slow claim was skipped.
This recovers the missed real BTC alarm at 2025-10-10 14:58:00. The shared engine sha16 is 70de3f03faaeaa74.
Other knownness rules and matching/measurement/grading computations are unchanged. Existing definitions and run schemas remain valid;
affected definitions need a fresh run to recover omitted alarms. Final evidence and both signatures: 'team/OUTSIDE/A54/i2g_review_v1/repair_v23/CLOSURE.md'.
V2.2 added: source ABSENCE is part of the run's frozen source identity. Every PRICE day a task consults (read, or the coverage shortcut) is
recorded as its index sha16 or ABSENT; a day seen in two states, or that changed / appeared / disappeared before the task returns or
before publication, refuses the run (SOURCE_CHANGED); RUN.json sources.price_state_by_day lists every state. (S1's recheck_inputs freezes
inputs known at admission; the PRICE days are discovered inside the tasks, so the engine binds them itself.)
V2.1 added: the PRICE index cache revalidated by sha16; the reader's exact file inventory (RUN_INVENTORY) and count consistency
(RUN_INCONSISTENT). Outside tests: A54 test_faults 11/11 (V2 10/11), A54 re-check test_fix_boundaries + test_worker_absence 7/7 (V2.1 5/7).
The V2 changes are guards and records only (refusals before staging, strict days, pins, worker watchdog, integrity of PRICE frames, verify_run,
known_at columns); the numerical path (matching, measurement, grading kernels and their order) is unchanged, so the V1 numbers below stand
(the three-coin equality is re-run on V2: RELEASE V2 names the receipt).
V1 receipts (25 Oct 2026; code idea_to_grade.py 8fe1a57ea9238421, i2g_engine.py 0b540339ea2ac089, i2g_grade.py 364efc8b6a52c4c5,
detect.py 770e0afa0221276f; under <SCRATCH>/work_LEAD/i2g/grade; record RELEASE_idea_to_grade_V1_CANDIDATE.json):
- ACCEPTANCE (the one full run): BN_OI idea, all 52 roster coins, 20250912..20260228, fresh detection, 8 workers, normal priority, nice 10,
  one numeric thread: 29.07 s external wall. Phases: detect 0.67 s, matching + measurements 15.06 s, aggregate 2.78 s, grading 9.74 s,
  publication 0.43 s. Whole-tree memory peak 8.9 GiB (sampled every 0.1 s; limit 16 GiB). 14,289 alarms (= the outside 52-coin selection),
  12,718 matched, 96,600 eligible matched moments, 221,778 measured rows, 190 cohorts x 7 slices. accept/oi52_full_v1.
- EQUALITY with the outside three-coin run (new_oi_full3_parallel_v1, fed through INTERFACE_V1 by fixture_outside_view.py):
  check_outside3_equality.py ALL EQUAL: 415 parents and waves, census, 3,909 matched moments, balance, coverage, 7,410 x 55 measured
  values bit for bit, reasons, all 190 cohorts x 7 slices (1,330 summaries, 157,700 parent rows) and the report table text. Same with
  37-parent chunks. The BTC/ETH/SOL slice of the 52-coin acceptance is also bit-identical to the outside three-coin matching/measurements.
- INDEPENDENT ORACLE check_run.py (no engine, kernel or alarm_stamp import): every cohort's standalone reach, paired gap and heat median
  re-derived from the published arrays: difference 0.0 on every run below; a planted change makes it FAIL (test).
- TESTS test_idea_to_grade.py: 14 passed (clock rounding vs Decimal, window refusals from the window table, no read outside the window,
  one unknown day abstains exactly the parents the day arithmetic names, the known path cut at the window's last midnight, pinned list,
  all-or-nothing failure, no overwrite, fixture flag, oracle not vacuous).
- TRIALS (same code, no change per idea; all check_run PASS):
  | idea | clock | input | selector | dates | alarms | wall |
  |---|---|---|---|---|---|---|
  | BN_OI open interest contraction (E2.S04) | 60 s | definition | ALL 52 | 20250912..20260228 | 14,289 | 29.1 s |
  | A02P (QUANT list V3 6d24c9b74f871ed4) | 5 s | event list | ALL 52 | 20250912..20260228 | 8,158 | 15.4 s (7 workers) |
  | BOOK top-of-book updates (C12.S02) | 30 s | definition | group PRIVACY (DASH, XMR, ZEC) | 20251101..20251130 | 11,760 | 9.4 s |
  | FUNDING negative estimate (E1.S01) | 60 s, knowledge time | definition | set of 7 | 20251201..20260131 | 460 | 2.1 s |
  | FLOW net taker selling (B1.S09) | 5 s | definition | ETH only | 20250924..20250925 | 7,694 | 2.4 s |
  (FLOW over 2 days: every alarm COMPARISON_UNAVAILABLE by design: candidate days +-7 d are outside the detected range.)
- PRIORITY DIAGNOSTIC: 52 coins x Oct 2025 (3,914 alarms): 5.1 s at normal priority, 54.6 s under taskpolicy -b (10.7x).

## Limits
Side-0 events refused. An event list's coverage is the PRICE listing (its producer's own coverage is unknown). Binance 3 s model prices,
taker fill at the first 3 s close traded after alarm + 9 s, no fees or funding (money is event_outcomes' job). Research only: no live parity. Background priority (taskpolicy -b) made a 52-coin x 1-month run
10.7x slower (54.6 s vs 5.1 s): run at normal priority.

## Detection stage alone (detect.py; i2g_detector, 25 Oct 2026)
```
python3 $SLOTS run <agent> 8 -- env PYTHONDONTWRITEBYTECODE=1 nice -n 10 $PY -B $T/detect.py --definition <definition.json> --roster $R \
   --coins ALL --first 20250912 --last 20260228 --research-window 20250901:20260228 --out <new folder> --workers 8
```
Python: `detect.run(definition, first, last, out_dir, roster, coins=..., group=..., group_file=..., workers=8, research_window='FIRST:LAST')`;
`detect.read_run(dir)` is the consumer's read. Contract: INTERFACE_V1.md (DETECT). Exit 0 COMPLETE, 2 REFUSED <CODE>, 3 FAILED.
- The research window is required and is the only date input besides first/last: every month BUILD (WINDOWS_V1) and law.py-readable.
  No day outside it is ever opened, support days included: an onset at the window's first 00:00 cannot fire (its predecessor, the day
  before at 23:59, is UNKNOWN), and history of percentile rules starts at the window's first day.
- Workers die with their parent (a parent-death check every 0.1 s); the command-line process also stops if its launcher (the slot
  wrapper) dies. A hard-killed run leaves no worker running and no DETECT_RUN.json (consumers refuse the folder).

| refusal code (detect.py) | meaning |
|---|---|
| RESEARCH_WINDOW_REQUIRED / RESEARCH_WINDOW | no window / not FIRST:LAST of real days |
| RESEARCH_WINDOW_NOT_BUILD / RESEARCH_WINDOW_SEALED | a month of the window is CHECK or BLIND / refused by lab3/law.py |
| SELECTION_OUTSIDE_WINDOW / DEFINITION_WINDOW / BAD_DAYS | first..last not inside the research window / the definition's window / not real days |
| DEFINITION_MISSING / DEFINITION_INVALID / UNSUPPORTED_OP / UNKNOWN_INPUT / FINITE_CONSTANT_REQUIRED / FIRE_RULE / EVENT_BINDING / EVENT_LIST_INVALID | the definition |
| METRIC_READING_REFUSAL | an input metric is STOP, CAUTION or UNPROVEN (labcore.briefs; the outside detector's rule) |
| ROSTER_MISSING / ROSTER_INVALID / INVALID_COIN / UNKNOWN_COIN / BAD_SELECTION / UNKNOWN_GROUP / EMPTY_GROUP | roster and selector |
| WORKERS / GATE_NOT_RUN / OUTPUT_EXISTS / AD_HOME_OVERRIDE_REFUSED | run settings |
| CLOCK_REQUIRED / NATIVE_CLOCK / CLOCK_SHAPE / WORKER_RSS_CAP | the store or a worker's memory (2 GiB each) |
| SOURCE_CHANGED_DURING_RUN / CODE_CHANGED_DURING_RUN / CENSUS / EVENT_OUTSIDE_EVALUATED_CELL / EVENTS_UNREADABLE | integrity: nothing committed |
| read_run: NOT_A_RUN / MANIFEST_INVALID / NOT_COMPLETE / MANIFEST_CHANGED / FILE_MISSING / FILE_CHANGED / EXTRA_FILE | a run folder that may not be consumed |

### Inherited engine limits (alarm_design_v2; percentile rules only: trail_pct / own_pct; none of today's ideas uses them)
1. Onset at 00:00: the engine fills a percentile only on day D's own rows, so the predecessor of D's 00:00 step (D-1 23:59) has no
   percentile, is UNKNOWN, and a true onset at 00:00 never fires (i2g_check: BTC 20251105 00:00 and RENDER 20251103 00:00 missed in a
   planted case, hand-checked). detect.py reproduces the engine; it does not patch it.
2. Stale days after a listing gap: the history keeps the coin's last N LISTED days (entries), so after a gap trail_pct's "w_s seconds
   before t" reads samples from before the gap (stale). detect.py's chunked runs reproduce the serial engine exactly (entry warm-up).
REQUEST to the alarm_design owner (ALARM): (1) compute the 23:59 percentile of D-1 from D-1's own history so a 00:00 onset is decided;
(2) make trail_pct's window calendar time (entries older than w_s are UNKNOWN), or refuse trail_pct across a listing gap. Until a new
engine release, percentile rules are graded with these two limits stated.
