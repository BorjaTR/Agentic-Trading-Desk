# Card of decision tool V1 (decide_v1), lean workflow steps 1 to 3 (DECIDE seat, 26 Oct 2026)

Written to the lean workflow of volat-step1-uses-levels (the five parts, settings and edge cases as data), volat-step2-build-producer and volat-step3-test-producer (tests T1 to T6), with scope, architecture and a speed budget as the coordinator asked. Settings as data: SETTINGS_DECIDE_V1.tsv. Edge cases as data: EDGES_DECIDE_V1.tsv (33 cases, run by edges_decide_v1.py).

## 0. Scope and architecture
**In scope.** For any alarm, coin set and day range: read the frozen fires and the three frozen library cards, apply one rulebook, and write one decision per fire (take or skip, why, trade side, and the names of the lab's entry and exit settings), plus the event lists the grader reads.
**Out of scope.** Prices, fills, exits, costs, money, outcomes (all belong to idea_to_grade V3.1 and the lab tools it names); running any producer or detector; live or paper orders; enforcing kill limits (recorded only, the owner's).
**Architecture.** Three pieces, one direction:
1. `decide_rules_v1.py`: pure rules, no file access (checks of the rulebook, safety and lab tool files; `decide()` of one fire).
2. `decide_v1.py`: the command: reads files, checks every pin (evidence, lab tool releases and their code), refuses undeclared words before deciding, writes the outputs with fixed headers.
3. Checks written apart: `tests_decide_v1.py` (21 tests), `edges_decide_v1.py` (the 33 cases), `mutants_decide_v1.py` (33 breaks), `meaning_decide_v1.py` (recompute of every real row without importing the tool), and the independent reviewer's own recompute.
Downstream: `loop_v1/` grades the decision groups through idea_to_grade V3.1 (the outcome loop). Stdlib only, one process.

## 1. Purpose and meaning
**What it is.** A rulebook engine: a fire goes through 4 slots in order (data gate, regime gate, side, at most 3 skip lines) and the first slot that decides wins. The answer is TAKE or SKIP with the slot, a reason word and a detail that names the field and value.
**Used for.** Choosing, per alarm, which fires to trade and on which side, with lines that only a loop finding may write (evidence file, sha16, cell, mechanism). The take-all default rulebook is the baseline every rulebook is compared with.
**How to read it.** TAKE means no active line objects; it is not a forecast of money (the grader answers that). BAD_DATA means a field the rulebook needs had no reading (a declared reason, a missing card row or an empty cell). SKIP_RULE names the line. A CANDIDATE line is untested for money; only FROZEN lines act in paper mode.
**Readers.** The outcome loop (loop_v1) today; the pipeline (pipeline_v1) next; paper trading later, FROZEN lines only.
**The five decisions.** Entry: S06 (a name only). Side: S02. Fade or ride: S02 (FADE or FOLLOW). Exit: S07 (a name only). Why: the detail column and the line's evidence and mechanism.
**Settings.** S01 to S13, see SETTINGS_DECIDE_V1.tsv.
**Scale and limits.** Filled by the test runs (T6, part 5).

## 2. Inputs and outputs
**Inputs.** UNIVERSE_ALARMS_V1.tsv (13c4722a5f5ab86b: fires, waves, weights); context V4.1 cards (STATE_CARDS_<alarm>_V41.tsv), profile V5.1 cards (three day slices a, b, c), pre-move V1.2 cards (PMM_<short>.tsv), joined on the fire key (alarm id, coin, second, push side); the rulebook; SAFETY_V1.json; LAB_TOOLS_V1.json.
**Outputs (a new folder per run, fixed headers, the fire key first).** DECISIONS.tsv (one row per fire); TAKE_EVENTS.tsv and SKIP_EVENTS.tsv (`alarm_id, coin, t, side, onset_t, trigger`); VALUE_COUNTS.tsv (a summary: every value of every used field and its kind); RUN.json (inputs with sha16 and root-relative path, code sha16, pins checked, tally).
**No stamps of time.** A decision has no known_at of its own: it is as old as its cards, whose own stamps live in the libraries. RUN.json pins every input by sha16 instead.

## 3. Source and processing (each rule is tested: test or case in brackets)
1. Only fires of the alarm, inside the days and coins asked, are read; days inside the research window, else refused (V03 mutant, planted_refusals).
2. Cards of other alarms are never read; a fire twice in one library refuses (other_alarms_rows_are_not_read, V02).
3. Every pinned file is at its sha16, and every entry and exit id is quoted in its release's code at the release sha16, else refused (V09, V10, V11).
4. Slot 1: push side not +1 or -1 gives BAD_DATA (E12). A used field holding a declared reason, NO_CARD_ROW or NO_VALUE gives BAD_DATA (E05 to E08); a word neither state nor reason refuses the whole run before anything is written (E09, V01, R18). States and reasons are declared per line; nothing is judged by spelling (E10, R15a, R15b; the review blocker of 26 Oct).
5. Slot 2: an off day, then an off state (E13, E16); the data gate comes first (E15, R10).
6. Slot 3: the side's status must be active for the mode (E20).
7. Slot 4: the first true active skip line in file order decides (E03, R02); none true gives TAKE (E01).
8. Trade side: FADE = -push, FOLLOW = +push, UNSET = 0, kept on a skip-line SKIP, 0 on the other skips (E02, E21, E22, R01).
9. Rulebook checks: at most 3 active lines, skip_if a proper subset of states, reasons declared, no state equal to a reason, evidence and a mechanism for every non-DEFAULT item, entry and exit from the lab tools file (E25 to E32).
**OPEN.** None: the choices of side, lines, entry and exit are the rulebook's (data), and off states and kill limits are the owner's.

## 4. Edge cases
33 cases in EDGES_DECIDE_V1.tsv, each with the planted values and the exact answer. Run-level cases (files, pins, headers, refusals) are planted file tests in tests_decide_v1.py: planted_run_end_to_end, planted_refusals (11 refusals), other_alarms_rows_are_not_read, planted_coin_filter.

## 5. Test cases (results filled from the runs of 26 Oct)
- T1 every case through the tool: see TEST_RECEIPT_DECIDE_V1.txt (edges line).
- T2 the independent reading: meaning_decide_v1.py recomputes every real row (see MEANING_DECIDE_V1.txt); the reviewer's own recompute is the independent one.
- T3 the real data: 8 runs on the 6 frozen alarms (run_v1_2), every row recomputed, 0 differences.
- T4 stamps: not applicable (no time stamp of its own, part 2); replaced by the pins of RUN.json, checked by the meaning loop Q7.
- T5 same bytes: the 8 runs made twice, outputs byte-identical (see the release record).
- T6 scale and limits: see the release record (fires and tally per run, missing card rows).
- Breaks: 33 mutants, each must be killed, the unchanged copy passing first.

## 6. Speed budget (written before the timed run of the refreeze; the first runs, 26 Oct ~06:00Z, took about 3 s for 8 runs)
| what | budget | limit |
|---|---|---|
| the 8 runs on the 6 alarms (18,740 fires) | 10 s | 30 s |
| tests_decide_v1.py | 10 s | 30 s |
| mutants_decide_v1.py | 120 s | 180 s |
| meaning_decide_v1.py on the 8 runs | 30 s | 90 s |
Memory: under 1 GB (the cards are read once per run).
