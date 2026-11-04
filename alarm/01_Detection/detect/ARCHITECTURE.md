# idea_to_grade — architecture (STRATEGY/LEAD; builders i2g_detector (detection) and i2g_grader (everything after), 25 Oct 2026)
Owner 11:59Z: "finish the tool and launch it as soon as possible". It replaces the outside team's unfinished chain
(OUTSIDE/COORD/DETECTOR_TO_GRADING_HANDOVER_2026-10-25.md) with the SAME meaning, imported, and a new orchestration.

## 1. Scope
- QUESTION: after the alarms of one idea, how often and how fast does the price offer 0.2 .. 2.0 % in the chosen direction, how much heat
  comes first, and how does that compare with matched moments of the same coin where the alarm did not fire?
- IN: a registered idea definition (fresh detection) OR an event list (coin, t, side[, onset_t, trigger]) pinned by its sha16; a coin
  selector (ALL, a set, a named group); first/last days; the research window (a run setting, BUILD months only); an output folder.
- OUT: one run folder, published at once, RUN.json last. Opportunity description only: no profit, no causality, no trade.

## 2. Pipeline (one process tree; <= 8 numeric workers, nice 10, one numeric thread each, <= 16 GiB for the whole tree)
| stage | where | what | reused (imported, pinned) |
|---|---|---|---|
| admission | idea_to_grade.run | gate RUN, nice >= 10, window months all BUILD in WINDOWS_V1 + law.py, first..last inside it, inputs pinned, out new | labcore.gates, lab3/law.py |
| 1 detect | detect.run (i2g_detector) | fresh detection -> detect/EVENTS.tsv, COVERAGE.tsv, DETECT_RUN.json | INTERFACE_V1.md |
| 1' event list | idea_to_grade.event_list_run | strict load, selector, coverage from the PRICE index -> the same three files | event_profile.load_alarms, detect.select_coins |
| 2+3 per coin | i2g_engine.coin_job (pool) | each PRICE coin-day read once; matched controls; 55 STAMP fields for parents + eligible controls x FOLLOW, FADE | alarm_match/draw_v3 (via the outside draw_prepared_v1 + prepared_activity_v1, bit-audited), alarm_stamp + outside alarm_stamp_projection_v1, heat_offer_v2, BED fill_v2 / ladder_v6, lab3 bins/days |
| aggregate | idea_to_grade.aggregate | outside identities and order: parents (t, coin, side), ids coin_t, waves 1800 s over all parents, request rows, balance, coverage | labcore.waves, draw_v3.balance |
| 4 grade | i2g_grade.grade_task (pool, 20 tasks) | 190 cohorts x (ALL + months): stamps, standalone / paired summaries, per-parent detail | alarm_stamp.stamps, outside fast_compare.Prepared + opportunity_compare_v1 |
| 5 publish | run_manifest_candidate | staged folder, gate + inputs + code rechecked, one rename, RUN.json last; failure -> <out>.failed_<stamp>/FAILED.json | event_decisions/run_manifest_candidate.py |

## 3. Why it is fast (the outside V14 spent its minute in per-event machinery and repeated preparation)
- One task per coin does matching AND measurement: every PRICE coin-day is read once (five fields, not eight) and serves both.
- No per-stage process launches, no per-chunk JSON request/receipt files, no repeated admission of the same view: one spawn pool for
  the whole run (coin tasks longest first, then 20 grading tasks); workers keep the prepared comparison per (direction, month).
- Measurements memoised per (clock, traded side); the controls' outputs are joined back in the outside row order by the parent.
- Grading publishes one COHORTS.json (1,330 detail-free summaries) and per-parent arrays, instead of 190 files repeating every parent row
  per month (the outside's 190 x 440 KB on three coins would be ~2.7 GB on 52 coins).

## 4. Semantics kept (proved equal on the outside three-coin run, field by field: check_outside3_equality.py)
- Matching: draw_v3 S0 (k 10, 400 tries, +-7 d, hour +-1, pre-activity (t-5400, t-1800], caliper 0.8-1.25, 30 min past-clear,
  horizon 14,466 s in the same split part), split from WINDOWS_V1, seed 20261023 + crc32(fid), whole-parent abstention
  (COMPARISON_UNAVAILABLE) when a candidate day (or its previous day) is not fully known to the detector (COVERAGE full_known) or has no
  PRICE part; candidate days = every calendar day of the research window.
- Measurement: alarm_stamp's 55 fields, decision at the alarm, 6 s execution delay, BED taker fill, 4 h hold, ladder first touches of
  0.1 .. 2.5 %, the PriceView of D-1, D, D+1 inside the research window (a later day is never read: the known path stops at midnight).
  A control's clock = its draw time rounded to the millisecond (half-even on the binary value).
- Grading: frozen global waves (1800 s, all parents), standalone wave weights, paired inherited control masses, exact weighted quantiles,
  NOT_APPLICABLE vs UNKNOWN kept apart. The month slices reuse the global wave ids (never re-clustered).

## 5. Invariants checked in code
Census = every parent exactly once; edges per parent = its draw count; every request measured once; 190 cohorts; FOLLOW and FADE
see the same edges; inputs (idea / list sha16) and every kernel pin re-checked before publication; a sampled tree RSS over the limit stops
the run; the gate must stay RUN.

## 6. Not built / limits
Side-0 events are refused (the outside grading had none). An event list's own producer coverage is unknown: its coverage is the PRICE
listing. Prices are Binance 3 s model paths (no Hyperliquid fill). Fee / cost / money are out of scope (event_outcomes, exits).

## 7. V2.3.1 onset repair (A54-FINAL-01)
Baseline: I2G V2.2 release 033a4735c99c1512. The shared alarm_design masks evaluator must retain a known-false shared condition as a
decided OFF row, including when its slow claim was intentionally not evaluated. This lets the next valid row form an OFF-to-ON onset.
All other knownness rules, shared-base selection, clocks, windows, refractory handling, matching, measurements and grading remain as
before. Unknown shared inputs without a known-false shared condition retain the existing conservative treatment.
The knownness rule lives in alarm_design_v2.conditions_known and both BASE masks and GRID call it. It is released as
alarm_design V3.8.1, consumed by I2G V2.3.1. Existing definitions and output
schemas remain compatible; affected definitions must be rerun to recover previously omitted events. Historical outputs are not rewritten.
Acceptance: the unchanged real BTC test for 2025-10-10 14:58:00 passes; unknown predecessors still suppress onsets; a delayed percentile
does not erase a known-false prefilter; existing detector tests and focused numerical comparisons pass. A separate checker signs the exact
new release. Original full-population evidence is retained on its original hashes; no new broad review is part of this repair.
