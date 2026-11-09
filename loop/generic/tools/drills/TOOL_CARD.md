# TOOL CARD: generic/tools/drills (LEARNING_LOOP_V1)
Every command, argument and env setting below is also in TOOL.json beside this card, read from the code. Placeholders: {GENERIC}/SETTINGS_TEMPLATE.md.

## blind_kit_v1.py
- Answers: makes a blind scorer kit (shuffled items, gold items, SCORER_TASK.md) and scores the scorers' files against it.
- Run: `python3 -B blind_kit_v1.py make --kit DIR --key KEY [--rubric F] --item F ... --gold F=<known total> ... [--elements a,b]` and `blind_kit_v1.py score --kit DIR --scorers A.tsv B.tsv ... [--gold-tol 1]`. The REPORT template the scorer task names: env LL_REPORT_TEMPLATE (set it to {GENERIC}/REPORT_TEMPLATE_V1.md).
- Gold check (C218): every gold needs a TOTAL from every scorer within --gold-tol, else `NO_SCORES k of n scorers` or SCORER_OFF; an item with no TOTAL prints `ITEM ... NO_SCORES`; any of these gives GOLD_CHECK FAIL, exit 3. C223 (RC3 review N1): a kit whose map has no gold row prints `GOLD NONE` and GOLD_CHECK FAIL, exit 3; `make` refuses with `REFUSED NO_GOLD` (no --gold) or `REFUSED BAD_GOLD <arg>` (a --gold value with no =<known total> that is a number), exit 2, and writes nothing. Not yet: `score` ignores agreement_v1's exit code and its ADJUDICATE line uses a fixed spread of 1 (OPEN.md).
- Tests: test_blind_kit_v1.py (8: 2 kit tests, 3 gold-check tests (C218), 3 N1 tests (C223): no gold row, make with no --gold, make with a bad --gold).

## agreement_v1.py
- Answers: do 2 or more scorers agree on the same items (exact, within-1, Krippendorff alpha ordinal and interval); which units go to a third scorer.
- Run: `python3 -B agreement_v1.py A.tsv B.tsv [--units run,item] [--points points] [--adjudicate 1] [--self-test]`. Read: alpha >= 0.80 RELIABLE, 0.667 to 0.80 TENTATIVE, below FIX_THE_SCALE; every unit with one value only: alpha `n/a (one value)` and NOT_COMPUTABLE (C218; was 1.000 RELIABLE).
- Exit: 0 done; 2 NO COMMON UNITS; a message and nonzero exit with fewer than 2 files.
- Tests: test_agreement_v1.py (6, synthetic, one of them the one-value case) and `--self-test` (published Krippendorff example).

## leak_scan_v1.py
- Answers: is a held-out marker or number in any file a hunter, assessor or curator reads? Orchestrator only; prints file, line and kind, never the number.
- Run: `python3 -B leak_scan_v1.py --pattern-file <pack pattern> --secrets <held-out files> --targets <files or dirs> [--allow <design-month number files>] [--out report.tsv]`. The pattern is the pack's (alarm pack: packs/alarm/HELDOUT_PATTERN.txt; env LEAK_SCAN_PATTERN_FILE works too).
- Exit: 0 no hit; 3 hits (open each by hand: a number can match by chance); 2 REFUSED NO_PATTERN (no --pattern-file, no LEAK_SCAN_PATTERN_FILE and no build_run_v2.py beside the tool; the alarm seat's source copy sits beside its builder and uses its pattern by default). Limit: skips folders named jobs, pipe*, split*, library, root, prep, setup, curator_scripts, time_log* and reads only .md .tsv .json .txt files.
- Tests: test_leak_scan_v1.py (7: plants, allow list, marker plus number, alarm pattern equals the builder's, a second pack's pattern, refusal without a pattern, main with the pattern file).
