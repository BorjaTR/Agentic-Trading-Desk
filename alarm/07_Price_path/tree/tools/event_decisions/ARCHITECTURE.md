# Decisions — the one architecture (code VERSION 3, decisions_fixer for STRATEGY/LEAD, 25 Oct 2026)
Owner the owner 10:31:22Z: "It needs to take in the correct input, make decisions and give a clear output. Generic, with settings, fast."
ONE TOOL, ONE HOME: team/RESEARCH/tools/event_decisions. README.md is the manual. Parent: VERSION 1 code ff115ad48cadaf9f ('Decisions V2',
twin ARCHITECTURE.md.pre_LEAD_20261025T111050Z), reviewed by A50 (team/OUTSIDE/A50/decisions_review_v1: NOT READY, F01-F07).

## 1. Scope
- QUESTION: for each event and each strategy card, what to do from what was known at the event: FADE, FOLLOW, SKIP or UNDECIDED, side,
  entry option, exit row, size, the rule that decided, why, and which inputs were unknown.
- USER: the factory (money), Results / T07 (learning which card to use, later), the LEAD and the owner (plain counts with `show`).
- IN THE LOOP: Alarms -> Context ed2 + Profile -> Cause -> Situations -> **Decisions** -> money (factory) -> judgement (fairness bar,
  freeze_judge). Decisions only reads what the steps before it wrote for the same event list.
- OUT OF SCOPE: money, fills, costs (factory); learning rules from outcomes (T07); any reading, situation or cause (their own tools).
- SUCCESS: every selected event gets one row per card with all eight fields; nothing unknown is ever traded; the output is reproducible,
  bound to its exact inputs and code, and consumable only as a complete run; the factory can take it without re-deciding.

## 2. Input, reads, output
- INPUT: any event list (coin, t whole seconds, side -1/0/+1, optional onset_t, trigger), any dates (the run's own window setting; lab3/law.py is the only seal), any
  population (all coins, `--coins`, a named group of a group file), through the shared loader and resolver of event_situations.
- READS: CTX (Context ed2, decision 0), EPG (Profile), CAUSE2 (Cause) through event_situations.read_inputs; SIT through
  event_situations.read_rows_part (only from a COMPLETE Situations V2 run); all through lab3 with the fixed purpose 'research'. A value is
  used only when available and known by F; otherwise it is unknown with its reason. Never a producer, a recomputation or an outcome.
- OUTPUT: part DEC.<SUBJECT>, ROWS, one row per event, as_of = known_at = F; eight fields per card; the catalog; DEC_RUN_<SUBJECT>.json.
- SETTINGS: one JSON: inputs, derived, entries (taker, delay_s), the exits file by sha16, cards. A new card = a block in a NEW file.

## 3. The rule of a card (three-valued)
Ordered rules {when (all / any, three-valued: FALSE AND UNKNOWN = FALSE, TRUE OR UNKNOWN = TRUE), action, entry, exit, size}. The first
TRUE rule decides; an UNKNOWN rule stops the card as UNDECIDED (UNKNOWN_INPUT, its unknown inputs and reasons in `unknown`); all FALSE =
SKIP (NO_RULE_HOLDS). FADE = -push, FOLLOW = +push; push = the list's side, else Cause's side_used (-1/0/+1 or unavailable); push 0 or
unavailable = UNDECIDED (NO_DIRECTION). A Situations family word is known only when its __by_default is a known 0 (F03): Situations passes
an unknown situation over when it names a group, so the label alone cannot carry that uncertainty. With one rule, the trades equal the
factory's decide() (test); the factory admits readings up to F + delay and calls UNDECIDED what Decisions calls SKIP when one condition is
unknown and another known false (both: no trade).

## 4. Admission, binding and publication (A50 F01, F02, F05, F06, F07, K1, K2)
1. Admission (no value read, nothing written): subject; dates (shared validate_window: calendar, order, law per day; no date constant in code);
   settings (own keys and fields + the shared validate); event list (shared load_events) and its contract; population (shared resolver);
   roots; the Situations run (shared check_run); column types (catalog / part index; shared bind_types and check_types).
2. Binding: every upstream part-day of every event day is opened (lab3 index, research purpose: law, quarantine and corrupt indexes
   propagate; a missing part refuses), fingerprinted (index + reasons + words, the shared part_fingerprint) and bound to this event list
   (shared bind_event_lists; a part naming no list refuses). run_id = sha16 of code pins, settings, list, selection and fingerprints.
3. Read through the shared readers; the read fingerprints must equal the admitted ones. Decide. Check the output contract (sides +-1/0,
   sizes, actions).
4. Publish: stage in <out_root>.pending_*, write the catalog and the day parts (lab3.write reads each part back), check row counts,
   recheck every fingerprint, file and loaded code file (SOURCE_CHANGED refuses), rename to <out_root>, commit DEC_RUN_<SUBJECT>.json
   last (run_manifest_candidate.py, a labcore candidate). A failure renames the staging to <out_root>.failed_*. Consumers read only a
   COMPLETE run whose committed files are unchanged and which holds no extra DEC part.

## 5. Speed and resources (budget frozen before the VERSION 3 code: dec_fix/baseline_20261025T110646Z/PERF_BUDGET_V3.json)
Full A02P (8,158 events, 2 cards, prepared upstream): budget 30 s wall and 512 MiB peak on one process; measured about 3 s and 85 MiB
(admission 0.1 s, read 0.3 s, decide 0.004 s, write + verify 2.5 s). The six-event funding Decisions command: budget 5 s / 256 MiB;
measured 0.2 s / 58 MiB. No parallel mode (one complete input, vectorised rules; the cost is lab3 writing 170 day parts).

## 6. What it replaces and what it feeds
- tools/decisions (QUANT, T07 design): its learner is the Results step that WRITES decision cards; unchanged.
- The factory (tools/factory, factory_v2) decides inside itself from the old EPI table. Its DEC consumer is staged as
  factory_dec_adapter_candidate.py (factory not edited): decisions from DEC, money by factory_v2.trade(). Promotion: a LAB1 release cycle.

## 7. Evidence, review, limits
Evidence and the 44-item checklist: A50_CLOSE_V1.md and CHECKLIST_A50_V2.tsv in this folder. Independent review of this exact release:
PENDING. Limits: README section 10 (RESEARCH ONLY; taker entries; fixed sizes; no WAIT; no live parity).
