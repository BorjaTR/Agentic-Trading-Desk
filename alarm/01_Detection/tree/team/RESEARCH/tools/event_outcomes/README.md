# event_outcomes — Outcomes, code VERSION 3 (the yardstick; A51 successor, NOT YET RE-REVIEWED)
**The one outcome-labels tool. Architecture: ARCHITECTURE.md. Every A51 finding, its fix and evidence: A51_ANSWERS_V3.md.**
Owner 10:39:49Z: "speed, settings to add any new label we want". Research labels on Binance 3 s model paths. Paper only, never an order.
Status: CANDIDATE (RELEASE_event_outcomes_V3_CANDIDATE.json). Not approved for grading until an independent re-review (REREVIEW_BRIEF_A51_V3.md).

## Run (analyst python; the public commands check the release candidate and the import closure first)
```
PY=<PYTHON>; F=<LAB_REPO>/forensics; T=$F/team/RESEARCH/tools/event_outcomes
$PY -B $T/event_outcomes.py check <lab_root> $F/team/LAB3/code <events.tsv> $T/OUTCOMES_CORE_V3.json <SUBJECT> <first> <last> --run-window FIRST:LAST
$PY -B $T/event_outcomes.py run 8 <lab_root> $F/team/LAB3/code <events.tsv> $T/OUTCOMES_CORE_V3.json <SUBJECT> <first> <last> <out_root> --run-window FIRST:LAST
$PY -B $T/event_outcomes.py verify <out_root> $F/team/LAB3/code      # THE shared run check: run_manifest_candidate.verify_committed
$PY -B $T/event_outcomes.py show   <out_root> $F/team/LAB3/code <SUBJECT> <first> <last>
```
- Selection (C1, LEAD ruling 25 Oct): `--coins A,B` (or `ALL`, the default) filters the given event list; every named coin must be on
  the lab's date-effective roster (the lab_days PRICE index of a selected day), else UNKNOWN_COIN; a roster coin without an event in the
  dates is an explicit empty selection (a committed run with 0 events). `--group-file F --group NAME` is refused SELECTOR_NOT_RELEASED until
  the ONE shared selector labcore/selection.py lands (ctxprof_shared's labcore V2_7 candidate, then LAB1); then both switch to it.
- `check`: every admission check and the input census (requested events, days, coins, embargoed labels and the events they belong to, the
  months authorized, the PRICE / EPI / funding vintages it would read). Reads indexes only; computes nothing.
- `run N` (N 1-8): freezes the run (RUN_FROZEN.json), stages it in `<out_root>.pending_<pid>_<stamp>`, runs N workers through the shared
  launcher (event_profile/run_parallel.py 'outcomes': each worker nice 10, one numeric thread; do NOT nice `run` itself), verifies, then
  publishes by one rename with RUN_MANIFEST.json committed last. A failure is kept as `<out_root>.failed_<stamp>` (FAILED.json), never
  consumable. An identical rerun answers UP TO DATE; any other run into an existing root is refused (OUTPUT_EXISTS): choose a new root.
  The recorder gate (team/FEED/stops/BACKFILL_GATE.txt) is waited on at the start and between days (labcore.jobgate). `--max-rss-gb`
  (default 48) stops the run if the process tree grows past it.
- Calling `run_parallel.py N outcomes ...` directly (the VERSION 2 way) still works as a worker launcher, but its root has no manifest:
  no consumer reads it. Use `run`.
- Optional `--ctx / --epg / --cause <root>` bind CTX / EPG / CAUSE2 units and Cause's side_used for side-0 events; they need
  event_situations, which is not released yet, so the closure check refuses such a run today (see Known limits).

## Frozen inputs (A51R-01)
At admission the run freezes the sha16 of EVERY configured file it reads, released or not: the settings, the event list, the static
cost table, the exits registry, the money cost settings and every table it names, lab3/law.py and WINDOWS_V1 (RUN_FROZEN.json 'config'),
plus every PRICE / EPI index and funding month file it will read ('inputs') and its code inventory. Each worker rechecks the configured
files before it parses the settings and again before it writes; run rechecks everything before the commit. Any change: INPUT_CHANGED,
nothing published (the staging folder is kept as .failed_). A file is never re-pinned to let a run pass.

## The authorized outcome window (A51-04; owner rule: no date in tool code)
The caller names the window it is authorized to read outcomes in: `--run-window FIRST:LAST` (or a `run_window {first, last}` key in a
run's own settings; both given = they must be equal). Before any read: the selected days must lie inside it (else SELECTION_OUTSIDE_WINDOW),
and the months of every event and of every forward support pass labcore.gates.outcome_allowed (lab3/law.py seal + WINDOWS_V1 classes;
else OUTCOME_REFUSED). A label whose window could need a 3 s bar at or after the end of the window is EMBARGO_SUPPORT: the event's row
stays, only that label is empty, and that price is never read. OUTCOMES_CORE_V3.json carries no window (the yardstick is reusable).
This repair's research window: --run-window 20250901:20260131.

## Settings (OUTCOMES_CORE_V3.json; V1 and V2 kept as run, refused by VERSION 3: their MONEY_T1 is the retired static-cost kind 'money')
- entry {delay_s, gap_s}; directions (distinct) from FADE FOLLOW LONG SHORT; cost {table, sha16, gap_pct, fallback unknown | median_flagged}
  (labcore.costs, the static c and the exit engine's frozen cost table); money {cost_settings {path, sha16}, size_usd} (money_full);
  units {nm: SOURCE:column}; exits {path, sha16}.
- labels: one line each, e.g. `{"name": "REACH_2C_60M", "kind": "reach", "target": 2, "horizon_min": 60, "unit": "c"}`.
  Kinds: return, best, worst {horizon_min}; reach, heat_before {target, horizon_min}; first {up, down, horizon_min};
  offer_before_heat {offer, heat, horizon_min}; exit, money_full {exit_id}. Refused before any read: a non-finite number, a horizon that is
  not a whole number of 3 s bars, a repeated direction, a name with '__' or colliding columns, an exit row needing monitor / extreme inputs
  (FADE_F1), kind 'money'.
- ADD A LABEL: one line, no code, in a NEW settings file (a file that was run is never edited). A new kind is a code change with its test.

## Output (part OUT.<SUBJECT>, ROWS, one row per requested event, as_of = F; catalog OUT_CATALOG_<SUBJECT>.tsv with real units)
| column | unit | known_at (availability clock) |
|---|---|---|
| entry__px / entry__s | price / seconds | the entry bar's end (NO_ENTRY: first grid bar + 60 s) |
| unit__c, unit__c_fallback | pct, flag | F (a static table) |
| unit__nm | pct (log-pct, EPI.A02N.normal_move_pct) | its stored known_at, never after the decision F + delay |
| `<LABEL>__<DIR>` (return best worst heat_before) | the label unit pct / c / nm | entry bar end + window |
| reach / first / offer_before_heat value | flag / sign (-1 0 +1) | entry bar end + window |
| `__t` | seconds from the entry bar end | entry bar end + window (exits: the exit bar end) |
| exit / money_full value | pct (CLEAN path only; money_full also complete funding) | the exit bar end |
| `__how`, `__path_evidence_status` | word | the exit bar end |
| `__hole_bars`, `__booked` | count, pct (the engine booking whatever the evidence) | the exit bar end |
| `__fee`, `__book`, `__gap` (A51-06 acceptance 2) | pct each (costs V3_5 parts / 100) | the exit bar end |
| `__cost_prefunding`, `__funding`, `__funding_ok` | pct (fee + book + gap), pct, flag | the exit bar end |
An unresolved exit (NO_PATH) gives every one of its columns the same reason and the clock entry + time limit. NO_DIRECTION and NO_UNIT are
known at the decision; EMBARGO_SUPPORT and NO_ENTRY / NO_COIN / NOT_BUILT at the (latest possible) window end. Empty reasons, a closed set
(detail after ':'): EMBARGO_SUPPORT NO_COIN NOT_BUILT NO_ENTRY NOT_LISTED NO_PATH PATH_GAP NO_PRICE NOT_REACHED NO_UNIT NO_DIRECTION
PATH_UNCERTAIN FUNDING_MISSING NO_COST (meanings in the catalog header and event_outcomes.REASONS). Price model
SIMULATED_BINANCE_3S_ADVERSE_FIRST, venue BINANCE (checked on every trade, carried in the catalog and the manifest): never a Hyperliquid fill.
MONEY_T1 is the factory's money of record (costs V3_5: fee + book + gap + funding on the entry notional, 10,000 USD). Missing funding ->
EMPTY FUNDING_MISSING (the factory's partial net = __booked - __cost_prefunding). It is never complete money.

## Grading contract (L1: what the grading step needs from Outcomes; the grading step itself is not built)
- READ: only a committed run: `event_outcomes.read(out_root, code_dir, SUBJECT, columns)` (or `RM.verify_committed` first for the full
  payload check). Bind the manifest's frozen settings / events / release sha16 in the grading receipt.
- IDENTITY: one row per requested event (coin, as_of = F); never drop a row: count EMBARGO_SUPPORT, NO_ENTRY, NO_COIN, NOT_BUILT,
  NO_UNIT and the rest by reason (RUN_MANIFEST coverage by_column gives them for the whole run).
- MONEY: use MONEY_T1__<dir> values only (CLEAN path, complete funding, a cost row); __booked / __fee / __book / __gap / __funding /
  __funding_ok explain every empty one; never impute 0 for an empty value (a SKIP or NO_TRADE rival books 0 by the grading's own rule).
- CLOCKS: every value's known_at is after F (outcomes are never joinable as inputs); units come from the catalog column 'unit'.
- WAVES, MATCHED MOMENTS, RIVALS, FAIRNESS BAR: the grading step's own (labcore.waves on as_of; the matched-moment list is another event
  list labelled by the SAME frozen settings in its own committed run; FADE-all / FOLLOW-all are the FADE / FOLLOW columns).
- WHAT OUTCOMES STILL NEEDS FROM GRADING: its consumer calling read / verify_committed (not a generic readback), its receipt naming this
  run's manifest sha16, and a planted check that it refuses an uncommitted root and keeps the reasons.

## Consumers
`event_outcomes.read(out_root, code_dir, SUBJECT, columns, first, last)` -> per column coin, as_of_us, known_at_us, value, reason, unit,
kind. It refuses (RUN_NOT_COMMITTED) a root without a COMPLETE RUN_MANIFEST.json, a changed committed file, or an OUT part the manifest
does not name. Grading must keep the reasons (never impute 0), group by wave and use only complete CLEAN money.

## Budgets and speed
THE BUDGET is the LEAD's target: `run 8` on the 7,039-event Sep-Jan A02P source (OUTCOMES_CORE_V3, 83 columns) <= 11 s wall, warm
page cache, the caller at normal priority, workers at absolute nice 10 (run_parallel), one numeric thread, at most 8 processes; memory is
reported, cap --max-rss-gb (default 48). GB = 10^9 bytes everywhere (the tool's log and cap included). E1: this budget was set after the
implementation; it is not claimed as a pre-implementation budget.
Measured: the internal checker's full run on release 133d9ebd took 13.18 s (median) and A51R2's normal-priority full run on 13e1e6d8
took 14.58 s whole job (manifest 12.31 s: preflight 1.71, workers 9.74, checks 0.31, pre-commit hashing 0.54 s): the 11 s target is
MISSED; it is tracked performance debt (BACKLOG_AFTER_CLOSE), not waived. The manifest's last phase stops before RM.commit (its own
digest work is outside it). Small warm checks: October 2025 (1,714 events) `run 8` 3.7 s, `run 1` 9.6 s; 1 vs 8 byte-identical.
Where the time goes per event (one-week profile): writing ~2.5 ms (lab3 write_part, 83 columns), labels ~1 ms, price reads ~0.8 ms,
the frozen exit call ~0.7 ms, costs and the read-back check the rest.

## Evidence (25 Oct; receipts <SCRATCH>/work_LEAD/out_fix, .../a51r_fix/build, .../a51r_fix/build/r3)
- A51R2 (FIX_ROUND3): the reviewer's test_review_v3.py and test_digest_swap.py (copied, never edited): 4 failed on f01bda34 (window before
  roster, SOURCE_HOLE unit, late unit clock, faster digest) and 8/8 pass after: admission is labcore v2_7 selection.check_window (S3)
  before any roster or index read; EPI units are read through lab3 rows and masked by labcore v2_7 quality.known (S2) with the source's
  reason (NO_UNIT:SOURCE_<reason>) and its own clock; every consumer and the UP TO DATE path use RM.verify_committed (every payload block).
- Tests: `python3 -m pytest -q -p no:cacheprovider test_event_outcomes.py test_a51_on_successor.py test_outcomes_v3.py` = 67 passed
  (9 original, 33 independent A51 regressions run on the successor, 25 targeted). The same A51 suite on the reviewed code 2017ed1c: 19 failed.
- A51R (re-review V2): test_rereview.py::test_custom_cost_mutation_before_commit_must_refuse fails on 988ea3a1 and passes now; the
  A51R tests in test_outcomes_v3.py add the unchanged-source success, a change seen by the worker before it reads, the exits registry and
  the cost-settings tables, fee / book / gap and the coin selector (73 tests in all).
- `acceptance_v3.py <out>` also runs listing (real NO_COIN ASTER / LIT, NOT_BUILT 5 Sep, the real FIL source hole as PATH_GAP), prefix
  (labcore.lookahead prefix, future-plant and mutant checks on 12 real events, the exit engine's join guard), selector and month (1 vs 8).
- `acceptance_v3.py <out>`: 112/112 A51 oracle values; 8/8 factory trades equal to the factory's full net (SOL FADE: FUNDING_MISSING);
  5 boundary events kept with EMBARGO_SUPPORT and 0 February files opened; NEAR exact 2.5 pct touch at 5,040 s (was 5,091 s);
  1 vs 2 workers byte-identical; per-column unit / reason / clock audit 0 violations; worker failure, interruption, restart, root
  preservation and UP TO DATE checked. Census of the 7,039-event selection by `check` (5 boundary events named; February refused).

## Known limits (owners in A51_ANSWERS_V3.md)
Binance prices (no HL fill). nm only for the A02 family (EPI.A02N); generic CTX units need event_situations released. The exit engine
counts every empty 3 s bar of a hold as a hole: on 13-14 Oct 20 pct of EXIT_T1 trades are PATH_UNCERTAIN (now named, never a clean value).
HL funding is missing for some coins / hours (FUNDING_MISSING) and LIT has no cost-of-record row (NO_COST). The entry rule repeats
factory_v2.trade's (the released factory exports no entry function). The grading step is not built. Named groups wait for the shared
selector. NOT_LISTED (a coin leaving the roster inside a window) has no real Sep-Jan case (no coin left the PRICE roster then); it is
proven on planted data only.

## What changed from VERSION 2 (2017ed1cc2e4c6dd)
A51-01 clocks; A51-02 one coverage rule (label_ewsd_v2.path_first_gap), return holes, clamped fallback, settled labels on short paths,
excursions >= 0, strict settings; A51-03 inclusive price-level touches (1e-9 relative); A51-04 enforced caller window with per-label
EMBARGO_SUPPORT rows; A51-05 run_frozen, evidence / holes / booked columns, uncertain never a clean value, shared reasons and clocks;
A51-06 money_full = factory money of record, static 'money' retired; A51-07 strict events, listing states, real units, release candidate,
import closure, frozen input vintages rechecked by workers and at publication, staged atomic publication, terminal manifest, consumer refusal.
