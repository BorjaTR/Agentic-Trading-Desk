# TOOL CARD: generic/tools/registers (LEARNING_LOOP_V1)
Every command, argument and env setting below is also in TOOL.json beside this card, read from the code. Placeholders: {GENERIC}/SETTINGS_TEMPLATE.md.

## reg.py
- Answers: the one writer and reader of the drill registers (DRILL_RUNS, IMPROVEMENTS, MESSY, SCORES, LEDGER, PROPOSALS) and the checks over them (check, ledger-check, scorecard, view, history, audit, import-report).
- Does not: edit a row (a correction is a new row), score a drill, or know any pack.
- Run: `LL_REGISTERS={REGISTERS} LL_SEAT_ROOT={SEAT_ROOT} python3 -B reg.py <drill|improve|mess|score|ledger|proposal> k=v ...` or `reg.py <check|ledger-check|scorecard|view|audit|history P01|import-report FILE --from ID>`. Both variables default to today's alarm seat layout (beside reg.py, two folders up).
- Refusals: REFUSED with the reason (unknown or missing field, unknown part_id, no such file, no change since the last ledger row); `baseline`: REFUSED BASELINE_MISSING with each missing PARTS.tsv file listed, nothing written.
- New seat (C218): rewrite PARTS.tsv `files` cells to the seat's own copies ({NAME} = env LL_<NAME>), then `reg.py baseline who=<seat>` (one BASELINE row per file), then `reg.py ledger-check` gives LEDGER_CHECK PASS.
- Tests: test_reg_audit.py (6), test_reg_report.py (4; uses its own temp registers even when the seat's LL_REGISTERS is set), test_reg_baseline.py (4).

## messy_triage_v1.py
- Answers: for every open MESSY row, which live file it names, whether that file is retired (REPLACED_FILE) and who acts.
- Run: `python3 -B messy_triage_v1.py [--registers DIR] [--series DIR]` (defaults: LL_REGISTERS, LL_SEAT_ROOT); a seat's own name map: LL_TRIAGE_MAP (TSV name, path); LL_SEAT_ROOT_NAME (folder name stripped from quoted paths).
- Classes include NO_LIVE_FILE (C218): the named file does not exist; NO_QUOTE now means the file exists and the line quotes nothing checkable.
- Tests: test_messy_triage_v1.py (8 planted lines).
