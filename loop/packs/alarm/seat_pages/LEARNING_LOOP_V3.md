# THE LEARNING LOOP V3 (SCOUT 2026-11-08; replaces LEARNING_LOOP_V2.md)
S = <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series. Paper research only.
Goal (the owner): prove the agents learn and get better every run, and keep every part of the process strong.
Who does what, in which order, and where each rule lives (table 1); this page copies no rule. State and numbers: team/SCOUT/NOW_SCOUT.md and the scorecard.

## 1. One home per topic (read the home, never a copy)
| topic | home |
|---|---|
| how a hunter runs the 3 rounds, pass rules, months, yardsticks, card, data traps | S/lean_v1/HUNTER_RULES_V2.md (the rules page; each run reads its pinned copy runs_v2/<run>/ops/HUNTER_RULES.md) |
| why each rule exists | S/lean_v1/HUNTER_RULES_WHY.md |
| hunter launch prompt | S/lean_v1/HUNTER_LAUNCH_V1.md |
| rules earlier runs proved; job commands | runs_v2/<run>/ops/ADOPTED_RULES.md (from S/PROMPT_ADD_V2.tsv, adopted only after a drill) and ops/JOB_SHEET.md (from S/lean_v1/JOB_SHEET_V1.md), both written by S/build/lean_ops_v1.py |
| what the agents know | S/knowledge_v1/ (store + KNOWLEDGE_BRIEF.md, built only by build_knowledge_v1.py) |
| how any part of the process is changed | S/drills_v2/PROCESS_IMPROVEMENT_V1.md |
| parts, scores, drills, changes, reports | S/drills_v2/registers/ (README.md; reg.py view, history, audit, ledger-check) |
| fair scoring; documents | S/build/blind_kit_v1.py, S/build/agreement_v1.py; S/drills_v2/DOCUMENT_PROCESS_V1.md |
| proof that memory helps | S/PROOF_RULES_V2.md, S/prep/bar_check_v2.py |
| held-out read | S/release_staging/LEARNING_LOOP_V2/alarm_pack/HELDOUT.md; results only in team/SCOUT/receipts/<holdout folder>/ (orchestrator) |
| assessor and curator steps | S/ASSESSOR_STEP_V3.md, S/CURATOR_STEP_V3.md (launch templates S/lean_v1/ASSESSOR_LAUNCH_V1.md, CURATOR_LAUNCH_V1.md) |
| run builder | S/build/build_run_v2.py (with S/prep/part_a_v2.sh) |
| role skills | ~/.claude/skills/volat-hunter, volat-assessor, volat-curator, volat-orchestrator |

## 2. Roles (one agent per role, one role per agent)
| role | reads | writes |
|---|---|---|
| Orchestrator | NOW page, its skill, this page | NOW page, logs, registers, held-out receipts |
| Hunter (memory run, arm L) | pinned rules page, the brief, JOB_SHEET, ADOPTED_RULES, the arm's previous run | the files the rules page lists |
| Control hunter (arm C) | pinned rules page and JOB_SHEET only (no brief, no adopted rules); example: the previous control run | the same |
| Assessor | the run folder, receipts, the brief the hunter saw, ASSESSOR_STEP_V3.md | ASSESS.tsv, MISTAKES.tsv, ops/EVIDENCE_HANDOFF.tsv |
| Curator | card, ASSESS, evidence hand-off, CURATOR_STEP_V3.md | knowledge store (tool only), CURATE.tsv, proposal checks |
| Drill agent / scorer | only the files its task names | exactly 1 file |
Every agent ends its RESULT or reply with MESSY, WASTE and PROPOSE (PROCESS_IMPROVEMENT_V1.md step 1).

## 3. One run, in order (orchestrator)
1. Gate: `python3 -B S/drills_v2/registers/reg.py ledger-check` PASS, and no open MESSY line on a file the run reads.
2. Build: `export SERIES_RUN_KEY=SCOUT_20261107` (this series' key; a new series takes a new key); `cd S/prep && bash part_a_v2.sh L <n>` (C for a control). Every path below is under S; write it out in full.
3. Pin: `python3 -B S/build/lean_ops_v1.py --run <run> --task <task> --arm L|C --prev <previous run of the same arm>` writes ops/HUNTER_RULES.md (+ sha16), HUNTER_LAUNCH.md, JOB_SHEET.md, ADOPTED_RULES.md.
4. Launch (the hunter picks its idea in step 0 of the rules page): date -u into ops/LAUNCH_UTC.txt; one fresh hunter agent with ops/HUNTER_LAUNCH.md.
5. Watch every 3 minutes (CronCreate or any host timer; with none, check at every turn): TIMES.tsv, STOP files, MAC_JOBS, `python3 -B S/build/check_round_v1.py runs_v2/<run> --run-number <n>` (a control: no --run-number, so every check runs); send card flags to the hunter before it ends. A refusal: a logged one gets its logged fix (a repeat; a control hunter gets only its machine-fact part and its pinned page, never a memory run's workaround or result); a new one is an emergency change (fix now, log, drill after the run).
6. Assessor: fill lean_v1/ASSESSOR_LAUNCH_V1.md into runs_v2/<run>/ops/ASSESSOR_LAUNCH.md; one fresh agent with the volat-assessor skill.
7. Reports, leak scan, then curator: load each block with reg.py import-report: the hunter's (end of work/RESULT_<run>.md); then 2 fresh readers (fill lean_v1/READER_LAUNCH_V1.md with the run and ids R1, R2; launch both at once; memory and control alike), loaded from ops/REPORT_READER_R1.md, _R2.md --from <run>R1 / <run>R2; then the assessor's (ops/REPORT_ASSESSOR.md); a refused write loads from its author's reply; a refused block is fixed by its author (" / " inside fields) and loaded whole; run `python3 -B S/build/leak_scan_v1.py --secrets team/SCOUT/receipts/{HELDOUT_YARDSTICK_FEBMAR_{,UP_}V1,SEPMAR_YARDSTICK_V1}.json and all held-out result files there --allow S/knowledge_v1/EVIDENCE.tsv S/SERIES_V2.tsv S/SERIES_V2_CONFIG.json --targets S/runs_v2/<run> S/knowledge_v1` (orchestrator only; a held-out number stops the curator); then fill lean_v1/CURATOR_LAUNCH_V1.md into runs_v2/<run>/ops/CURATOR_LAUNCH.md; one fresh curator agent with the volat-curator skill (knowledge work, then it checks every PROPOSED row logged before its launch; later rows wait for the next curator; rows about the curator's own skill or the orchestrator's own drafts, marked "fresh checker", go to one fresh agent at step 11). Memory runs only add findings; a control run's evidence rows carry arm C and are never cited.
8. Series row: `python3 -B S/prep/bar_check_v2.py row --runf runs_v2/<run> --run-id <run> --series S/SERIES_V2.tsv --config S/SERIES_V2_CONFIG.json --write` (a placebo round is never the best round).
9. Held-out read (orchestrator only, memory runs): the best round (higher of R1 and R3 lead15) and R3 and R3P, per HELDOUT.md; a sign read; results only in receipts, never a card or brief (status words only); the assessor's HOLD_LEAD15 says "asked orchestrator, pending" (a control: "control run: no held-out read").
10. Clean own scratch: `python3 -B S/build/scratch_clean_v1.py --run <the series run key of step 2> --keep-from <the lowest first job among the 2 most recently curated runs; never above the first job of a run not yet curated> --receipts <LAB_REPO>/forensics/team/RESEARCH/ALARM_DESIGN/runs/<series run key>/receipts --log <SCRATCH_DISK>/scout_keep/deleted_<utc>.log` (dry run, then --apply).
11. Upkeep: log the curator's report lines; re-score the parts the run touched (reg.py score); rewrite the NOW page.
12. Next run: a memory run L(n+1) may start once L(n) is curated (step 7) and the step 1 gate passes; steps 8-11 of L(n) may run beside it; controls run beside memory runs. A BLOCKED run: assessed for mistakes only, no findings, no series row; rerun.

## 4. Proof that memory helps
Memory runs against control runs on the design months, by PROOF_RULES_V2.md (B3: memory minus control >= +2 points, permutation p < 0.10, and fewer repeated mistakes). the owner's current ruling there (8 Nov 14:25Z) wins: first every part is checked independently; then 10 more runs prove it (their split and bars set when they start); until then bar_check_v2's B3 is a pilot read only. An exact p < 0.10 needs over 10 ways to split the runs: 3 memory + 2 control cannot reach it, 4 + 2 or 3 + 3 can (pilot read). Learning also shows in reasoning (REASONING_QUALITY_V3.md) and forecasts (forecast_score.py).

## 5. Improving the loop itself
Every part of the process (registers/PARTS.tsv) has a drill (registers/DRILLS.tsv), a score (SCORES.tsv) and a ledger (LEDGER.tsv). Changes go through PROCESS_IMPROVEMENT_V1.md: report, log, check, draft on a copy, drill old vs new (2 fresh agents per side for a judged drill, blind 2-scorer kit with gold items), adopt by its step 5 (whether) and step 6 (when). Weakest part per category first. A part is strong only with hidden items passed, 2 scorers agreeing (>= 0.80), a live run confirming it and its speed target met.
