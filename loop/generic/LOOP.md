# THE LEARNING LOOP V2 (generic; any seat; paper research)
Goal: every run starts from what earlier runs proved, is scored the same way as a run with no memory, and feeds back what it learned. Each part is drilled on its own, so a weak part is found and fixed.
A seat uses this loop through its PACK: the pack fills the rounds, pass rules, yardsticks, data traps, mechanism list, job templates and run builder settings. Everything else is here.

## 1. Roles (one agent per role, never two roles in one agent)
| role | does | writes |
|---|---|---|
| Orchestrator | builds and launches runs, watches every 3 min, fixes and logs, held-out read, cleanup, drills, proof read | logs, registers, held-out receipts, handover |
| Hunter | one idea through the pack's rounds, then the card | CLAIMS, FORECASTS, job list, CARD, RESULT, its job files and work folders |
| Assessor | checks every card number against its receipt, scores the run | ASSESS, MISTAKES, evidence hand-off |
| Curator | turns the run into knowledge, only through the knowledge tool | store ops, CURATE, adopted rules |
| Control hunter | the same run with no memory | the same as a hunter; nothing it finds enters knowledge |
| Drill agent | one part at a time, fresh and isolated | exactly one file |
Prompts for every role: prompts/ (orchestrator.md, hunter.md, assessor.md, curator.md, drill_agent.md); skills: skills/. Every {PLACEHOLDER}: SETTINGS_TEMPLATE.md.

## 2. One run, in order
1. Build (orchestrator, the pack's builder): memory runs get the brief and adopted rules; controls get none; the builder refuses a leak, any held-out number, a missing forecast slot.
2. Hunter reads: the pack's RULES.md, the brief, the run's job sheet (ops/JOB_SHEET.md, from the pack's JOB_SHEET; job commands only).
3. Step 0: /pro-practice-first and the stuck check (STUCK_CHECK.md beside this page) in the R0 form of RULES_TEMPLATE (one line per stuck question; at least 2 candidates, each with what it could move; the without-step-0 line); pick the test whose result can change a finding's status.
4. Before every round: a CLAIMS line (ids it builds on; no retry of a refuted finding without naming the difference) and a sealed FORECASTS line (start from the finding or move it builds on, else the pack's yardstick; every part of the pass rule; RULES_TEMPLATE, Before every round).
5. The pack's rounds (for alarms: claim, explain by state, sharpen with a placebo). Generic pages name rounds by role: select (alarm R1), split (R2), fitted change (R3), placebo (R3P); the pack's round map says which of its rounds plays each role.
6. Card: the pack's template; every number with its receipt; NEXT TESTS.
7. Reports, then assess. Load the hunter's REPORT block (end of work/RESULT_<run>.md) with tools/registers/reg.py import-report. Then two fresh readers, launched at once, memory and control runs alike (the pack's reader launch page; alarm pack: {PACK}/launch/READER_LAUNCH_V1.md): each reads only the rules page and job sheet the hunter used (ops/HUNTER_RULES.md, ops/JOB_SHEET.md) and REPORT_TEMPLATE_V1.md, and writes only a REPORT block of every line an agent could act on two ways (contradiction, missing) to ops/REPORT_READER_R1.md and ops/REPORT_READER_R2.md, loaded with --from <run>R1 and <run>R2. Then assess (prompts/assessor.md) and load ops/REPORT_ASSESSOR.md the same way.
8. Curate (prompts/curator.md): only through tools/knowledge_v2/build_knowledge_v2.py <op|check|brief> --pack {PACK}/<pack>.json --dir {STORE}; statuses by numbers only; then the pack's pooled check (alarm pack: {PACK}/tools/pool_splits_v1.py) and the series row.
9. Held-out read (orchestrator only): the best round, rule frozen, once; same sign -> op HOLDOUT_SAME_SIGN (words only). Hunters and curators never see held-out numbers.
10. Clean: keep the stores of the last 2 curated runs; clear older working files; list every deleted file.
11. Next run starts from the new brief.
Controls run beside memory runs with steps 1-7; their evidence is stored, never cited.

## 3. Knowledge (tools/knowledge_v2/build_knowledge_v2.py --pack {PACK}/<pack>.json --dir {STORE}; the pack's mechanisms list sets the allowed names; KNOWLEDGE_README.md)
EVIDENCE (every graded test, append only) | FINDINGS (statuses HYPOTHESIS, SUPPORTED, CONFIRMED, REFUTED, RETIRED, computed) | MOVES (change types and their gains) | OPEN_QUESTIONS | OPS_LOG | KNOWLEDGE_BRIEF.md (built only by the tool: best so far, base rates, definitions, open states, findings, do not retry, moves, questions) | PROMPT_ADD_V2.tsv (adopted rules, status ADOPTED).
CONFIRMED needs the pack's status_bars (confirmed_min_runs, confirmed_min_mechanisms, t_bar) and, when confirmed_needs_holdout, the orchestrator's held-out read, logged after the finding's last evidence change (alarm pack example: 2 runs, 2 mechanisms, t >= 2.5).

## 4. Proof (the pack's proof tools; alarm pack: {PACK}/tools/bar_check_v2.py for the bars, {PACK}/tools/forecast_score.py for forecasts)
Memory beats control by >= 2 points with a permutation p < 0.10 over the block; forecasts: Brier and 80 pct coverage per run, size error. Log every run in the series file.

## 5. Drills (DRILLS.md, tools/registers/reg.py; scorer kits tools/drills/blind_kit_v1.py, agreement tools/drills/agreement_v1.py)
Every part has a drill: kit and key first, fresh agents (one file in, one file out), 2-3 agents per version, scored against what really happened. Every drill run is a row in DRILL_RUNS.tsv, every fix a row in IMPROVEMENTS.tsv (with the drill that found it and the drill that verified it). A failed drill: fix the part, rerun the same drill.

## 6. Logs and rules for every seat
FAILURES_LOG (what failed, cause, fix), HOTFIX_LOG (each quick fix), PROCESS_CHANGES (each process change with an id). Copy a file before changing it. No deletes outside your own scratch without the owner. Never a shared scratch folder for agent work. At most 3 agents at a time.

## 7. Making a pack for a new seat
Copy RULES_TEMPLATE.md and fill its slots; write ROUNDS (purpose, process, pass, fail meaning, measure, drill per round); set MECHANISMS.txt; adapt the job templates and the builder settings; run the process drill (H08) on the filled RULES.md with 3 fresh agents (pass 12/13) before the first run.
