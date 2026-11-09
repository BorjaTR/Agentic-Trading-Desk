# PROOF_RULES_V2: when the agents learn and the process works (the bar for release)
CURRENT RULING (the owner, 8 Nov 2026 14:25Z) wins over every earlier ruling below; see its section at the end.
Owner: the owner, 7 Nov 2026 10:40 Berlin ("yes, we need to get there as soon as possible"). Written BEFORE any measured run; PROOF_RULES_V1 (runs 1-7) stays as history. Changing this file needs the owner's word.

## Design
- Measured block starts at the first run after ALARM_BUILD_V26 and pipeline V1_4 are current (new windows: design Sep 2025-Mar 2026; one look Apr-Jul 2026; never seen Aug-Nov 2026; yardstick FDONLY Sep-Mar +5.88 at 15 min, t +3.42, 5 of 7 months).
- Two arms, run alternately (L, C, L, C ...), same pack, same tools, same three-round format, same windows:
  - L (learning): the hunter gets the curated KNOWLEDGE page, the adopted PROMPT_ADD rows, earlier L runs' results; the curator curates after each L run.
  - C (control, no memory): the hunter gets the same pack prompt with an empty knowledge page, no PROMPT_ADD rows, no earlier runs; nothing a C run finds enters the knowledge table or prompts.
- At least 10 runs per arm. The process (template, step files, tools) is FROZEN inside the block; a fix found during the block is logged and applied only after it (a tool crash may be fixed only if it blocks every run, logged as such).
- Every hunter writes a FORECAST before each grade: predicted 15-min lead and the better and worse market state.

## The five bars (all must hold)
B1 PROCESS RUNS CLEAN: 5 consecutive runs (either arm) with 0 hand work, 0 stops made by our template or tools, 0 blindfold breaches, and assessor scores reproducible from receipts (a second assessor run on the same receipts gives the same ASSESS.tsv numbers).
B2 LEARNING SHOWS (arm L): (a) within run: best round beats round 1 at 15 min in at least 6 of 10 L runs; (b) across runs: mean best-round margin over the yardstick in L runs 6-10 exceeds L runs 1-5 by at least 2 points; (c) forecasts: mean absolute error of the predicted 15-min lead in L runs 6-10 below L runs 1-5, and the predicted better state matches the state-split tool's better state in at least 3 of 5 L runs 6-10 (typo fix 7 Nov: the first text said 6 of 10, impossible for 5 runs; same bar of 60 percent).
B3 LEARNING BEATS NO-MEMORY: over the block, arm L beats arm C on the mean best-round margin over the yardstick by at least 2 points AND on repeated mistakes per run (fewer), with a permutation test across runs at p below 0.10 for the margin.
B4 RESULTS HOLD WHERE NOBODY LOOKED: at least 3 distinct alarms (overlap below 50 percent of waves with any earlier alarm, not a rediscovery) whose best round, opened once on Apr-Jul 2026 with its rule frozen, beats the yardstick's Apr-Jul figure in at least 3 of 4 months with pooled t at least 2; then the single best is opened once on Aug-Nov 2026 by the owner.
B5 OTHERS CAN REPEAT IT: a fresh agent in a fresh account runs one full run from the released documents alone and reproduces its receipts; the outside reviewer passes the method (process, measures, these rules).

## Kill and change rules
- If after 10 L runs B2(b) and B3 both fail: the learning design is changed (not tuned), with a plan from pro-practice-first, and a new block starts.
- If B1 fails for tool reasons: fix tools, restart the B1 count; B2-B4 data stay valid only if the fix did not change any grade number.

## Measures (from ASSESS.tsv): M1-M10 of ASSESSOR_STEP plus M11_FORECAST (absolute error of predicted lead, state match), M12_NOVELTY (wave overlap with earlier alarms), M13_ARM (L or C).

## Notes fixed before the block
- Apr-Jul one-look results are written only to SERIES_V2 LOOK rows during the block, never to knowledge or prompt rows (later L prompts must not see that window).
- B4 yardstick: FDONLY graded once on Apr-Jul with the holdout tool after V26 is current, before any L or C best round is opened.

## Ruling (the owner, 7 Nov 13:33 Berlin)
- Control arm: 5 runs, not 10, placed beside memory runs 1, 3, 5, 7, 9. B3 is tested on 10 memory runs vs 5 control runs (permutation p < 0.10).
- "The first 10 runs will probably be to improve all our workflow and learnings and the loops": runs 1-10 are improvement runs. The process may change between them, with every change logged by run number. The frozen proof block is counted after them.

## Ruling (the owner, 7 Nov 16:30 Berlin): per-run held-out score
- From L03 and C02: hunters design on Sep 2025 to Jan 2026 only (INPUT window 20250910:20260131). Feb-Mar 2026 is each run's held-out check: the best round, rule frozen, is read once on Feb-Mar by the orchestrator (hold_lead15), from the grade receipts. Hunters never read Feb-Mar numbers.
- Apr-Jul stays the final one-look test of the best ideas of the series (B4), untouched until then.
- Kill rule: design lead passes but hold_lead15 fails = search memory, not learning.
- Added per run (plan PLAN_AGENT_LEARNING_PROOF_20261107.md): hold_lead15, r1_margin, forecast as probability of beating the yardstick plus an 80% interval (Brier, coverage), hunter-only repeated mistakes, rule use, blind 0-12 reasoning score (judge agent, the owner checks 20%).

## Ruling (the owner, 8 Nov 2026 14:25Z): the current one, it replaces the 7 Nov rulings above where they differ
His words: "where we are today is: 1. We need to check every part of the process including documents independently. Which is what we are doing. 2. Once everything is clear, we will do 10 more runs to prove it. Forget yesterday's ruling. Everything changes so fast that yesterday's rulings are not up to date".
- Now: every part of the process, documents included, is checked independently (drills, blind scoring, packets K1-K4 and the parts after them). Changes that pass may go live; no run is in a frozen block yet.
- Then: once everything is clear, 10 more runs prove it. How those runs split between memory and control, and their bars, are set when that block starts (ask the owner); until then bar_check's B3 is a pilot read only.
- Held-out read (the owner 8 Nov 15:21Z, "memory runs only"): after each memory run the orchestrator reads its best round on Feb-Mar 2026 (HELDOUT.md); control runs get none.
