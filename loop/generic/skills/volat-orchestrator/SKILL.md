---
name: volat-orchestrator
description: The orchestrator role of a volat-agent learning loop (any seat, any pack): build and launch memory and control runs, watch every 3 minutes, fix and log at once, run assessor and curator, do the held-out read alone, clean its own scratch, run drills and keep the registers. Use when you take over or run a learning series, even if the prompt only says "recover L<n>", "keep the runs going" or "drill this part".
---
# volat-orchestrator (generic, LEARNING_LOOP_V1_RC2, 8 Nov 2026)
Read first: {SEAT_ROOT}/NOW_{SEAT}.md (current state and next steps; rewrite it at every step), then {GENERIC}/prompts/orchestrator.md (the run steps) and {GENERIC}/LOOP.md. Every {PLACEHOLDER}: the seat's copy of {GENERIC}/SETTINGS_TEMPLATE.md. After a reset, start the 3-minute check again for any live run.
- Runs: the 12 steps of prompts/orchestrator.md (gate, build with this series' key, pin, launch, watch with the pack's round checker, assessor, reports and leak scan with the pack's pattern file, curator, series row, held-out read alone, clean, upkeep, next run).
- Registers only through `python3 -B {GENERIC}/tools/registers/reg.py` with LL_REGISTERS={REGISTERS} and LL_SEAT_ROOT={SEAT_ROOT}; load every agent's REPORT block with `reg.py import-report <file> --from <id>`.
- A refusal during a live run: an emergency change (copy first, fix now; log FAILURES_LOG, HOTFIX_LOG, the ledger; drill it after the run). Never edit a run's pinned rules; a control hunter never hears a memory run's workaround or result.
- Improving any part: {GENERIC}/drills/PROCESS_IMPROVEMENT_V1.md. Fair scoring only: blind kits (tools/drills/blind_kit_v1.py), 2 scorers, 2 gold items, agreement (tools/drills/agreement_v1.py) >= 0.80; never score your own change.
- Work order: `reg.py scorecard`, weakest level first per category.
- Limits: the owner's agent cap; deletes outside your own scratch, git push, money and any release need the owner's word. With the owner: verdict first, plain words, one question at a time.
