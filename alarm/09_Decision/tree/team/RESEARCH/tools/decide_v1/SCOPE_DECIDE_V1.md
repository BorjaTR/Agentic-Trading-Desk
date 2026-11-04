# Scope, architecture and acceptance of decision tool V1 (DECIDE seat, written 26 Oct 2026 ~06:40Z, at the refreeze after review)

Honesty note: this scope was written after the first build (26 Oct ~05:50Z) and after the first independent review (NOT READY, 06:20Z), not before coding. It writes down what the code was built to, plus the review's fixes, so the reviewer can check the code against it.

## Purpose
Turn every fire of any alarm into a decision the grader can test: TAKE or SKIP, why, on which side, and the names of the lab's entry and exit settings. A decision rests only on the frozen library cards and on rulebook lines that a loop finding wrote. Whether a decision makes money is the grader's answer, never this tool's.

## In scope
- Any alarm of the registry, any coin set, any day range inside a research window (no alarm, coin or date in the code).
- Inputs: the frozen universe and the source event list its header names, context V4.1, profile V5.1 and pre-move V1.2 cards, one rulebook, SAFETY_V1.json, LAB_TOOLS_V1.json, ADMITTED_INPUTS_V1.json (which release record admits each input).
- Slots, in order: data gate, regime gate, side, at most 3 skip lines. Research mode (CANDIDATE and FROZEN lines) and paper mode (FROZEN only).
- Outputs for the grader (TAKE and SKIP event lists) and for the pipeline (fixed headers, fire key first).

## Out of scope
- Prices, fills, exits, costs, money, outcomes (idea_to_grade V3.1 and the tools it names).
- Running any producer, detector or library.
- Sending, sizing or managing orders; enforcing kill limits (recorded only; the owner sets them).
- Choosing a line, a side, an entry or an exit (the loops and their PREREG rows choose; the rulebook only records).

## Architecture
decide_rules_v1.py (pure rules, no files) <- decide_v1.py (the command: files, pins, refusals, outputs) -> DECISIONS / TAKE / SKIP / VALUE_COUNTS / RUN.json -> loop_v1 (split into groups, grade each through idea_to_grade V3.1 under its own PREREG row, read with a fixed bar). Checks apart: tests, edges, mutants, the meaning checker, the reviewer's recompute. Stdlib only, one process.

## Acceptance criteria (done when every line holds, with its receipt)
| # | criterion | receipt |
|---|---|---|
| A1 | every edge case of EDGES_DECIDE_V1.tsv gives its exact answer | receipts_kit_v1/EDGES.txt (33 of 33) |
| A2 | every test passes and every mutant is killed, the unchanged copy passing first | receipts_kit_v1/TESTS.txt (25 of 25), MUTANTS.txt (51 of 51) |
| A3 | no real state is ever written as BAD_DATA; a word neither declared state nor declared reason refuses the run | test declared_states_not_spelling, edge E09/E10, probe_yday_old_vs_new.txt (fails on the old code), PROBES.txt on the real M cards |
| A4 | every real decision row equals a recompute that does not import the tool | MEANING_DECIDE_V1.txt (67 of 67) and the reviewer's recompute_decide_v1_indep.py |
| A5 | no alarm, coin or date name in the code, checked against the universe and the registry | test generic_code_no_alarm_coin_or_date, generic_test_catches_the_review_probes |
| A6 | every output header is fixed and per-fire files start alarm_id, coin, t, side | test planted_run_end_to_end, meaning Q8, mutants V12 V13 |
| A7 | same inputs give the same bytes | 8 runs made twice, 32 of 32 files identical (release record) |
| A8 | every pinned evidence file, lab tool release and release code file is checked at every run | tests planted_refusals, mutants V09 V10 V11 |
| A9 | inside the speed budget | SPEED_BUDGET_DECIDE_V1.md |
| A10 | the independent reviewer says READY | the reviewer's file |
| A12 | every row of the 25 Oct test kit is PASS with a failing-before and passing-after receipt, or NOT_APPLICABLE with a reason | KIT_DECIDE_V1.md |
| A13 | every input is admitted by its library's signed release record; a finished run is tamper evident and every consumer checks it | tests planted_refusals_with_codes, finished_run_is_tamper_evident, receipts_kit_v1/split_tamper_old_vs_new.txt |
| A11 | the outcome loop runs under its PREREG rows and is read with its fixed bar | loop_v1 (after A10) |
