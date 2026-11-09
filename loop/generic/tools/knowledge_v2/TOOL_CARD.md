# TOOL CARD: generic/tools/knowledge_v2 (LEARNING_LOOP_V1)
Every command, argument and env setting below is also in TOOL.json beside this card, read from the code. Placeholders: {GENERIC}/SETTINGS_TEMPLATE.md.

## build_knowledge_v2.py
- Answers: what the seat's knowledge store holds (evidence, findings with statuses computed from numbers, moves, open questions) and the brief a memory hunter reads.
- Does not: grade a run, read held-out numbers, set a status by judgement, or hold any pack constant in code (all come from `--pack`).
- Run: `python3 -B build_knowledge_v2.py init|check|brief|op --pack <pack.json> --dir <store> [--who ID] [--op ADD|UPDATE|MERGE|RETIRE|EVIDENCE|HOLDOUT_SAME_SIGN|MOVE|QUESTION] [--target ID] [--into ID] [--set k=v ...] [--reason TEXT]`. `--pack` and `--dir` are required.
- The pack contract (every key, the alarm and strategy values): README.md. Pages: {GENERIC}/KNOWLEDGE_README.md.
- Read the output: `check` prints CHECK PASS (exit 0) or the failing rows; `brief` writes {STORE}/KNOWLEDGE_BRIEF.md; every op is one OPS_LOG.tsv row.
- Refusals: unknown mechanism, control evidence in a finding, a TODO status bar for check/brief/finding ops, a duplicate move eid.
- Refusals added in C218: HOLDOUT_SAME_SIGN on a fid that does not exist (UNKNOWN_FID); a held-out row counts only after the finding's last evidence change; EVIDENCE with t or waves not a number (NOT_A_NUMBER) or a window not YYYYMMDD:YYYYMMDD with real days, first <= last (BAD_WINDOW). `init` makes a missing store folder. `--who` is free text: that only the orchestrator writes HOLDOUT_SAME_SIGN is a process rule.
- Tests: test_build_knowledge_v2.py, 33 (31 for a seat without knowledge_v1; 2 skip with a reason; the golden test records the one deliberate v2 difference, a CONFIRMED finding whose evidence changed after its held-out row); test_knowledge_v2_c218.py, 5.
