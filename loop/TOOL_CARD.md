# TOOL CARD: learning_loop LEARNING_LOOP_V1_1 (the generic learning loop and its first pack; the code of LEARNING_LOOP_V1, pages corrected)

## In one line
The research loop any seat runs on paper: one idea through fixed rounds with a sealed forecast before each, a card with a receipt for every number, an assessor, a curator through the knowledge tool, a control run beside it, and drills of every part.

## What is in it
- `generic/`: the loop page (LOOP.md), rules template, step pages, prompts, skills, templates, registers template, drills, and three tool folders with their own cards: `generic/tools/knowledge_v2/`, `generic/tools/registers/`, `generic/tools/drills/`.
- `packs/alarm/`: the first pack (the worked example). `packs/strategy_draft/`: the strategy pack draft, every status bar TODO.
- `MANIFEST.tsv` (every file, sha16, source), `TEST.md`, `TEST_RUN.py`, `OPEN.md`, `CHANGELOG.md`, `SEAT_PATHS.tsv`, `ARCHIVE_PLAN.tsv`.

## Commands
- Prove the install works for a new seat (writes only under --seat and --tmp; copy the install first, it is read-only):
  `cp -Rp <RELEASE_ROOT>/Learning_Loop/learning_loop/current <copy>; python3 -B <copy>/TEST_RUN.py --release <copy> --seat <empty seat folder> --tmp <temp folder off the internal disk>`
  Output: one `ROW <n> PASS|FAIL` line per row, then `SEAT_REGISTERS_UNCHANGED_BY_TESTS_1_TO_13 yes`, `PYCACHE 0`, `TEST_RUN PASS` (exit 0). Any FAIL prints the tail of its output; exit 1.
- Knowledge: `python3 -B generic/tools/knowledge_v2/build_knowledge_v2.py <init|op|check|brief> --pack <pack.json> --dir <store>` (card in that folder). A pack with TODO bars is refused (`REFUSED ... TODO`, exit 1), by design.
- Registers: `python3 -B generic/tools/registers/reg.py <drill|improve|mess|score|ledger|proposal|import-report|baseline|check|ledger-check|scorecard|audit>` (card in that folder).
- Drills: `generic/tools/drills/blind_kit_v1.py`, `agreement_v1.py`, `leak_scan_v1.py` (card in that folder). `leak_scan_v1.py` with no pattern refuses `REFUSED NO_PATTERN` (exit 2).
- Every placeholder and variable: `generic/SETTINGS_TEMPLATE.md`.

## How a new seat starts (strategy first)
1. Read README.md section "How a seat starts" and `generic/LOOP.md`; copy `packs/strategy_draft/` to the seat's folder as its pack.
2. Fill `generic/SETTINGS_TEMPLATE.md` and the pack's bars (owner item 1 in OPEN.md); write `{PACK}/RULES.md` from `generic/RULES_TEMPLATE.md`.
3. Copy `generic/registers_template/` to the seat's registers, rewrite PARTS.tsv to its own files, run `reg.py baseline` and `reg.py ledger-check`, then the process drill before the first run.

## How to change this release
Never edit the installed folder. Change the source pages and tools first (their paths are in MANIFEST.tsv, column source_path), with a copy (`.pre_<seat>_<id>_<utc>`) and a ledger row (`reg.py ledger`). Build the next edition as a copy of this one (`LEARNING_LOOP_V1_1` for pages only, `LEARNING_LOOP_V2` for a changed loop), recut MANIFEST.tsv, TOOL.json pins, CHANGELOG.md, OPEN.md, README.md and this card so they name the new edition, run TEST_RUN.py from a byte copy as a new seat (every row PASS), install the edition held beside this one, run `release_index_v1.py check <RELEASE_ROOT> --tool Learning_Loop/learning_loop --edition <new>`, then move `current` and write the index (skill volat-release).
