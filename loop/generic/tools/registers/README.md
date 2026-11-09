# Drill registers (SCOUT, from 2026-11-08; the owner 07:41Z "log all of this in some register so we keep everything logged for all drills")
- DRILL_RUNS.tsv: one row per drill run (one agent, one arm, one snapshot): what was asked, score, pass, minutes, tool calls, finding, output file.
- IMPROVEMENTS.tsv: one row per process change: the problem, evidence, change, files, the drill that found it, before and after, the drill rerun that verified it.
- Write only with reg.py (python3 -B reg.py drill|improve|mess|score|ledger|proposal k=v ...); read with reg.py check, ledger-check, scorecard, view, history, audit. PARTS.tsv is the one exception: a new part is a new row added by the orchestrator, logged with reg.py ledger. reg.py check after each batch. Rows are never edited; a correction is a new row.
- Detail of each improvement: PROCESS_CHANGES_SCOUT.md (C ids); detail of each drill: drills_v2/hunter/H<nn>/ (TASK, MATERIAL, KEY, OUT, RESULTS) and drills_v1/RESULTS.tsv (older drills).

## Parts, scores and the file ledger (the owner 09:02Z "a ledger where we log each improvement of each part, each document, each prompt, each skill")
- PARTS.tsv: every part of the learning process (34 on 8 Nov, P01-P34, each with a category): files, how each is measured, its drills, its pass bar. Change it only by appending a part.
- SCORES.tsv: one row each time a part is scored (score, max, status PROVEN | WORKS | WEAK | NOT_MEASURED, good, to improve, evidence run ids). `reg.py scorecard` prints the latest per part.
- LEDGER.tsv: one row per change to any file of any part, with the file's sha16 before and after, the change id (C47...), who found the need and which drill verified it. `reg.py ledger ...` fills the shas itself.
- `reg.py ledger-check` (run before every run and every release): FLAG when a part file's bytes differ from its last ledger row, so no change to a prompt, rule, skill, tool or document goes unlogged. Started 8 Nov with one BASELINE row per file (G0001-G0052); history before that: IMPROVEMENTS.tsv and PROCESS_CHANGES_SCOUT.md.
- Knowledge content (findings, evidence) is not in this ledger: the knowledge tool (tools/knowledge_v2/build_knowledge_v2.py) logs every op in {STORE}/OPS_LOG.tsv.
- Folders (RC2): reg.py reads and writes the registers in env LL_REGISTERS ({REGISTERS}; default beside reg.py) and resolves relative part files under env LL_SEAT_ROOT ({SEAT_ROOT}; default two folders up); messy_triage_v1.py takes the same two as defaults of --registers and --series, LL_SEAT_ROOT_NAME (folder name stripped from quoted paths) and LL_TRIAGE_MAP (a seat's own name-to-path map). A new seat starts its registers as a copy of generic/registers_template/.

## Is the improvement loop followed? (`reg.py audit [--all]`, drill LOOP_AUDIT, test: test_reg_audit.py)
- A ledger row stays open (FLAG UNVERIFIED) until a drill row that STARTED after the change (its utc minus its minutes: rows are logged at the end) says "verifies <G id or C id>" in its finding (several ids may follow one "verifies"; ids match whole), or its verified_by names a drill or run instead of pending/none.
- A LOOP_AUDIT row saying "superseded <G id>" closes a change whose flagged text a later change replaced; that later change stays open until its own drill.
- Also listed: proposals adopted without a drill before and after, and open MESSY ids. Other MESSY, PROPOSALS and MISTAKE rows: PROCESS_IMPROVEMENT_V1.md.
