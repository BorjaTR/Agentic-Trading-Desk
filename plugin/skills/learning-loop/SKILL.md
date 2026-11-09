---
name: learning-loop
description: Use at the start and end of every alarm try in the Crypto Alarm Desk repo - the generic learning loop in loop/generic with its alarm pack in loop/packs/alarm - read the knowledge brief first, seal a forecast before every round, write the card with a receipt for every number, then score the run (assessor) and turn it into knowledge (curator) only through the knowledge tool. This is how the desk learns from every try, failed ones included.
---

# The learning loop: every try starts from what was proven and feeds back what it learned

The loop lives in `loop/` at the repo root (edition LEARNING_LOOP_V1_1, copied by `desk/build/copy_v2.py`):
- `loop/generic/`: the same for every kind of research. Start with `loop/generic/LOOP.md` (roles, one run in order, knowledge, proof,
  drills). Every `{PLACEHOLDER}` in the pages is defined once in `loop/generic/SETTINGS_TEMPLATE.md`.
- `loop/packs/alarm/`: what only alarm research knows. `RULES.md` (the one rules page a hunter reads), `ROUNDS.md`, `JOB_SHEET_V1.md`,
  `CARD_TEMPLATE.md`, `templates/` (CLAIMS, FORECASTS, CARD, CURATE), `alarm.json` (the pack file every knowledge call names),
  `MECHANISMS.txt`, `tools/` (the round checker, the proof bars, the forecast scorer).
- `loop/README.md` (section "How a seat starts") and `loop/TOOL_CARD.md`: setting up a desk's own store and registers once.
The lab's held-out route (its pattern file and launcher) is not shipped: held-out files are never read here.

## Once per desk
1. Copy `loop/generic/SETTINGS_TEMPLATE.md` into your output folder and fill every value (`{STORE}`, `{REGISTERS}`, `{TMP}`, ...).
   Set `LL_TEST_TMP` and `KNOW_V2_TMP` to a temp folder before any test.
2. A store: `python3 -B loop/generic/tools/knowledge_v2/build_knowledge_v2.py init --pack loop/packs/alarm/alarm.json --dir <STORE>`.
3. Registers: copy `loop/generic/registers_template/*.tsv` to `<REGISTERS>` and follow `loop/README.md` step 3 (PARTS.tsv rewrite,
   `reg.py baseline`, then `reg.py ledger-check` must print LEDGER_CHECK PASS).

## Before a try
1. Read the brief: `python3 -B loop/generic/tools/knowledge_v2/build_knowledge_v2.py brief --pack loop/packs/alarm/alarm.json --dir <STORE>`
   (best so far, findings, do-not-retry, open questions), and run the engine's own copy search (alarm-desk skill, step 1).
2. Step 0 of `loop/packs/alarm/RULES.md` (the stuck check, at least two candidate tests), then for every round a CLAIMS line (the
   findings it builds on; no retry of a refuted finding without naming the difference) and a sealed FORECASTS line, before any outcome.

## After a try (always, also when it failed, was refused or was stopped)
- The card from `loop/packs/alarm/CARD_TEMPLATE.md`: every number with its receipt (file and sha16), and NEXT TESTS.
- Assessor (`loop/generic/prompts/assessor.md`, a separate agent): every card number against its receipt; ASSESS and MISTAKES.
- Curator (`loop/generic/prompts/curator.md`, a separate agent): only through `build_knowledge_v2.py op|check|brief`; statuses come
  from the numbers, never set by hand; `check` must print CHECK PASS.
- A fix of the process is a row in the registers (`loop/generic/tools/registers/reg.py`), never an edit by hand; then `reg.py check`.

## What may become knowledge (training provenance only)
Knowledge may come only from tries the desk is allowed to learn from (its own work, or the learning tasks of an evaluation).
- A trial agent may read its OWN assigned brief and the inputs that brief approves; when the trial is a held-out task, its logs are
  QUARANTINED: kept for the record, never read by the curator or any learning memory until the evaluation ends.
- The curator, the brief and the reviewer never read a held-out brief, a held-out trial's output or logs, any sealed key, or another
  trial's transcript or grade, at any time during an evaluation. A control run's evidence is stored, never cited.
- If any of these was seen by accident, record it and treat every finding changed after it as EXPOSED (not used until the evaluation
  ends). The held-out judge is the harness, never this agent or its reviewer.

## Checks
- `build_knowledge_v2.py check` (CHECK PASS) after every curator step; `reg.py check` and `reg.py ledger-check` before every run.
- The loop's own tests: `loop/TEST.md`; `desk/tests/test_loop_v1.py` runs them from a copy.
- One agent per role, never two roles in one agent; never write or edit a store or register row by hand.
