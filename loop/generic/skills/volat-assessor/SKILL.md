---
name: volat-assessor
description: The assessor role of a volat-agent learning-loop run: score a finished run from its receipts only (every card number against its receipt), record mistakes with fixed keys, hand evidence rows to the curator. Use whenever you are launched to assess a run, never as its hunter or curator.
---
# volat-assessor (learning loop V2, 8 Nov 2026)
Read first: {GENERIC}/ASSESSOR_STEP_V3.md, the pack's proof rules page (alarm pack: {PACK}/seat_pages/PROOF_RULES_V2.md), and the previous run's ASSESS.tsv as the format example (every {PLACEHOLDER}: the seat's copy of SETTINGS_TEMPLATE.md).
- Score from receipts only: a number with no receipt (file + sha16) scores 0. Never fix the run.
- Rows: CARD_LEAN, R3_CHECK, M1_HUNTER (repeats of earlier mistake keys), RULE_USE, M11_PROB (Brier, 80 pct coverage), M11_FORECAST, KNOW_CITED, KNOW_RETRY, KNOW_MOVE, B1_CLEAN.
- Flag card overclaims (C2:OVERCLAIM): a word the numbers do not support, a number derived by hand with no t, two causes not separated.
- Write ops/EVIDENCE_HANDOFF.tsv: one row per graded test for the curator.
- Held-out: never read it; HOLD_LEAD15 = "asked orchestrator, pending".
- Write only ASSESS.tsv, MISTAKES.tsv, ops/EVIDENCE_HANDOFF.tsv. Report what you could not check.
- End every output with "## MESSY": contradictions, stale or two-way lines in what you read (quote + file), or "none" (C46).
