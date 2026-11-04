# Outcomes (the yardstick) — the one architecture, code VERSION 3 (STRATEGY/LEAD builder, 25 Oct 2026; A51 successor)
Owner the owner 10:37:54Z: "we should be able to choose any yardstick, any labels and get the results for the alarms ... This tool is vital
because it will be able to grade and improve every other tools meaning and significance". ONE TOOL, ONE HOME: team/RESEARCH/tools/event_outcomes.
VERSION 3 answers the independent review A51 (team/OUTSIDE/A51/outcomes_review_v1, code 2017ed1cc2e4c6dd): A51_ANSWERS_V3.md.

## 1. Scope
- QUESTION: what happened after each event, by every label a settings file names, in each chosen direction.
- IN THE LOOP: Alarms -> Context + Profile -> Cause -> Situations -> Decisions -> **Outcomes** -> grading (by wave, matched moments, rivals,
  fairness bar) -> freeze_judge. Outcomes labels; it never grades, never chooses trades, never trades (paper).
- OUT OF SCOPE: grading, risk limits, HL fills, live parity (research-only labels on Binance 3 s model paths).

## 2. Inputs, reads, output
- INPUT: any event list (coin, t, side) through load_events: event_profile.load_alarms' strict contract (exact whole seconds, side
  -1/0/+1, one identity per coin and second), kept in this tool without importing event_profile (proven equal by a test; the one shared
  loader is a labcore candidate); the caller's authorized outcome window (run argument --run-window, or a run setting); a settings file.
- READS (all canonical, all pinned): lab_days PRICE 3 s bins through labcore.prices.PriceCache (lab3.bins); the PRICE index per day for the
  listing state and the partition vintage; EPI.<subject> through alarm_profile.read (nm, its stored known_at); the static cost table through
  labcore.costs.cost_c (c); the cost of record and HL funding through factory_v2.costs_of / trade_cost (costs V3_5, hl_funding_pull_v1);
  exits through exit_engine.run_frozen; coverage through bucket_proof/label_ewsd_v2.path_first_gap; authorization through
  labcore.gates.outcome_allowed (lab3/law.py + freeze_judge WINDOWS_V1). No date is held in this code.
- OUTPUT: lab3 one format, part OUT.<SUBJECT>, ROWS, one row per requested event (as_of = F), 83 columns for OUTCOMES_CORE_V3, each with
  its real unit, closed empty reasons and its own availability clock (README 'Output'); OUT_CATALOG_<SUBJECT>.tsv; RUN_FROZEN.json (the
  frozen identity); RUN_MANIFEST.json (the terminal manifest: parts and their sha16, selection, coverage by column and reason, checks,
  terminal status, wall, memory).

## 3. The pipeline of one run
1. ADMISSION (check / run, before any data read): settings (finite numbers, whole-bar horizons, distinct directions, no colliding names,
   pinned exits / cost tables, no exit row needing unbound inputs); the event list; subject and dates; the window: selection inside it,
   every month of the events and of every forward support through gates.outcome_allowed; the per-label embargo (a label whose latest
   possible bar, first grid bar + 60 s + window, is not strictly before the window's end is EMBARGO_SUPPORT).
2. FREEZE: release candidate + import closure (every loaded code file pinned by the release graph); the code inventory as a fresh worker
   computes it; every configured file (settings, events, cost table, exits registry, cost settings and its tables, law.py, WINDOWS_V1:
   A51R-01); the vintages of every input: PRICE index per day, EPI index per event day, funding month file per coin and month.
3. STAGE: run_manifest_candidate.stage -> <out_root>.pending_<pid>_<stamp>; RUN_FROZEN.json written into it.
4. WORKERS (run_parallel 'outcomes', N day chunks, nice 10, one thread): each re-checks settings, events, window, roots and its own code
   inventory against RUN_FROZEN.json, then every PRICE / EPI / funding vintage before it reads it; waits on the recorder gate between days.
5. LABELS per event: entry (the factory's rule: first priced 3 s bar within 60 s of the first bar ending at or after F + delay + one bar);
   listing state of every support day (NO_COIN / NOT_LISTED / NOT_BUILT; the grid is cut before an unavailable day, which is never read);
   units (c with its fallback rule, nm with its clock); per direction: non-exit labels on the bars of their window only (floor(H / 3 s)),
   one coverage answer per window (path_first_gap), inclusive price-level touches; one frozen exit-engine call per event and exit row
   (every traded side at once), CLEAN value only, booking / evidence / holes kept; money_full through factory_v2.trade_cost.
6. VERIFY: each worker reads every day it wrote back through the canonical lab3 block reader (verify_day) and keeps a receipt bound to
   the part's index sha16 (every requested event x column exactly once, typed as the catalog, a closed reason for every empty cell,
   outcome clocks never before F and input clocks never after the decision, the part's sources the frozen ones); before publication run
   checks exactly the requested days were written and every receipt is present, bound to the current index and counts every requested
   event x column; then every configured file, code file and input vintage is re-checked unchanged.
7. PUBLISH: run_manifest_candidate.commit (one rename of the staging folder, RUN_MANIFEST.json last). Any failure: abort ->
   <out_root>.failed_<stamp> with FAILED.json. Consumers: event_outcomes.read / show / verify -> load_complete(prefix 'OUT.').

## 4. Shared code reused (never copied)
labcore (prices, costs, gates, ids, release, jobgate, lookahead via the engine), exit_engine_v1.run_frozen, label_ewsd_v2.path_first_gap,
factory_v2.costs_of / trade_cost, alarm_profile.read, event_profile/run_parallel.py, and
event_decisions/run_manifest_candidate.py (the whole-run publication helper, decisions_fixer's labcore candidate; event_outcomes is its
second consumer; event_situations V2 implements the same pattern inline). One rule is still repeated: the 60 s entry rule of
factory_v2.trade (the released factory exports no entry function; equality proven on the 8 real factory trades).

## 5. Speed and memory
One price read per coin-day (PriceCache, days before D-1 dropped), one coverage answer per window per event, one frozen exit call per
event and exit row. Budgets and the small measurements: README 'Budgets'. The full-scale measurement is the lead's combined run.

## 6. Evidence, review, limits
README 'Evidence' and A51_ANSWERS_V3.md. Independent re-review: REREVIEW_BRIEF_A51_V3.md (this builder does not approve its own repair).
Limits: README 'Known limits'.
