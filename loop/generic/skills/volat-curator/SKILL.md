---
name: volat-curator
description: The curator role of a volat-agent learning-loop run: turn an assessed run into knowledge only through build_knowledge_v2.py with the seat's --pack and --dir (evidence, findings, moves, questions), adopt proven process rules, rebuild the brief. Use whenever you are launched to curate a run, after its assessor.
---
# volat-curator (learning loop V2, 8 Nov 2026)
Read first: {GENERIC}/CURATOR_STEP_V3.md and {GENERIC}/KNOWLEDGE_README.md (every {PLACEHOLDER}: the seat's copy of SETTINGS_TEMPLATE.md); the previous run's CURATE.tsv as the example.
- Every store write through `python3 -B {GENERIC}/tools/knowledge_v2/build_knowledge_v2.py op --pack {PACK}/<pack>.json --dir {STORE} --who CUR<run> ...`; never a hand edit. Statuses come from the tool by numbers only.
- Evidence rows for every graded test (from the assessor's EVIDENCE_HANDOFF); finding ops for what the run moves; an assessor-flagged overclaim is never a finding (at most a question with honest numbers).
- MOVE op per change of the fitted-change round (alarm R3; the pack's round map; a ladder is one change, its best rung; fail as CURATOR_STEP_V3 step 4); QUESTION ops (answers, new questions from NEXT TESTS).
- Mechanism names only from the pack's list (pack key mechanisms or mechanisms_file; alarm pack: FORCED_OUT, FORCED_OUT_SHORTS, CROWDED_LATE).
- PROMPT_ADD_V2 row only for a process rule the run proves; status word ADOPTED; twin the file first.
- Then: check (CHECK PASS), brief, and the pack's pooled check (alarm pack: {PACK}/tools/pool_splits_v1.py). Scripts in the run's ops/curator_scripts/.
- Never: held-out numbers, control-run evidence in findings, deletes.
- End every output with "## MESSY": contradictions, stale or two-way lines in what you read (quote + file), or "none" (C46).
