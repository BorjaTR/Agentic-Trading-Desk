# KNOWLEDGE store (generic; LEARNING_LOOP_V1_RC2): what is in a seat's store and how to use it
The tool: `{GENERIC}/tools/knowledge_v2/build_knowledge_v2.py` (V1 release candidate; its README holds the `--pack` contract and TOOL_CARD.md its commands). Every call names the seat's pack file and store folder:
`K() { python3 -B {GENERIC}/tools/knowledge_v2/build_knowledge_v2.py "$@" --pack {PACK}/<pack>.json --dir {STORE}; }` (placeholders: SETTINGS_TEMPLATE.md).

## Files in {STORE}
- EVIDENCE.tsv: one row per graded test (VARIANT, SPLIT_STATE, YARDSTICK); append only, never edited. The curator appends through `K op --op EVIDENCE`. Control (arm C) rows are stored here only and never cited.
- FINDINGS.tsv: one row per finding; changes only by ADD, UPDATE, MERGE, RETIRE ops; the status is recomputed from EVIDENCE by the pack's numeric bars (never set by hand). `check` refuses control evidence in a finding (CONTROL_EVIDENCE).
- MOVES.tsv: change type x mechanism -> n, gain vs the select round and vs the forecast, fails; "works" only at n >= 2. Written only through `K op --op MOVE`.
- OPEN_QUESTIONS.tsv: ranked next tests with the finding they would move (`K op --op QUESTION --set action=ADD|TAKE|ANSWER`).
- OPS_LOG.tsv: every op (utc, who, op, target, old -> new, reason). twins/: a copy of a file before each edit.
- KNOWLEDGE_BRIEF.md: built only by `K brief`, read first by memory hunters (cite Fnnnn); never edited by hand.

## Commands
- `K init` (a new store), `K check` (must print CHECK PASS), `K brief`, `K op --who <id> --op ADD|UPDATE|MERGE|RETIRE|EVIDENCE|HOLDOUT_SAME_SIGN|MOVE|QUESTION [--target ...] [--into ...] --set k=v ... --reason "..."`.
- Mechanism names come only from the pack (key `mechanisms` or `mechanisms_file`); an unknown name is refused (UNKNOWN_MECHANISM).
- A pack whose status bars are still `"TODO"`: init, EVIDENCE, QUESTION and MOVE work; check, brief and the finding ops are refused with the TODO keys named.
- HOLDOUT_SAME_SIGN is the orchestrator's op only (a status word, never a held-out number).

## Who writes
The seat's curator (EVIDENCE, finding ops, MOVES, QUESTIONS) and its orchestrator (HOLDOUT_SAME_SIGN); hunters only read the brief.

## Tests
`cd {GENERIC}/tools/knowledge_v2 && KNOW_V2_TMP={TMP} python3 -B -m unittest -v test_build_knowledge_v2` (33 tests; a seat without knowledge_v1 runs 31 and skips 2: TEST.md).

## Examples (C218; `K` = `python3 -B {GENERIC}/tools/knowledge_v2/build_knowledge_v2.py --pack {PACK}/<pack>.json --dir {STORE}`)
`--set` takes one `key=value`; repeat it for each key.
- EVIDENCE (columns: eid, utc, run, arm, mechanism, alarm, variant, test_kind, statement, window, lead15, minus_fdonly15, lead1h, t, waves, months_up, months_total, job, source_file, notes; `t` and `waves` are numbers or empty; `window` is YYYYMMDD:YYYYMMDD, real days, first <= last):
  `K op --who CURATOR --op EVIDENCE --set run=L12 --set arm=L --set mechanism=FORCED_OUT --set alarm=A --set "variant=R1 V1" --set test_kind=VARIANT --set "statement=one line" --set window=20250910:20260131 --set t=3.1 --set waves=410 --set lead15=12 --set minus_fdonly15=2.0 --set source_file=RUNF/ASSESS.tsv --reason "L12 R1"`
- ADD: `K op --who CURATOR --op ADD --set type=STATE --set "statement=..." --set evidence_eids=E0101,E0102 --reason "L12"`
- QUESTION (columns: qid, question, would_move_fid, test_sketch, priority, source_run, status, answered_by_eid; priority 1, 2 or 3 and a question are required):
  `K op --who CURATOR --op QUESTION --set action=ADD --set priority=1 --set "question=does the split hold on the first fire of a wave?" --set would_move_fid=F0003 --set "test_sketch=..." --reason "L12 NEXT TEST"`
- HOLDOUT_SAME_SIGN (orchestrator only, by process rule: `--who` is free text, the tool does not check the role): `K op --who ORCH --op HOLDOUT_SAME_SIGN --target F0003 --reason "frozen best round, same sign"`. Refused for a fid that does not exist (UNKNOWN_FID). It counts only when it comes after the finding's last evidence change (ADD, an UPDATE of evidence_eids, a MERGE into it): after such a change the finding waits for a new held-out read.
- Refusals added in C218: UNKNOWN_FID, NOT_A_NUMBER t|waves, BAD_WINDOW; `init` makes a missing store folder.
