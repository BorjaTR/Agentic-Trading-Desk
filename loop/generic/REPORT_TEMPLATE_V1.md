# REPORT TEMPLATE V1 (SCOUT 2026-11-08, C130; the one format for every agent's end report: hunter, assessor, curator, drill agent, scorer; C207: the two-readings check is required in every report)
Why: one format lets a tool load every line into the registers ({REGISTERS}: MESSY.tsv, PROPOSALS.tsv) with none lost or reworded.
Where it goes: hunter: at the end of work/RESULT_<run>.md (a BLOCKED result too); assessor: alone in ops/REPORT_ASSESSOR.md; curator: alone in ops/REPORT_CURATOR.md; a drill agent or scorer: where its task says (at the end of its output file, or alone in the file the task names). Copy the block below; one item per line; fields split by " | "; inside a field write " / " instead of " | " (for example when you quote a table cell).

```
## REPORT
MESSY | <kind> | <file> | "<the words, quoted, at most 25; any pipe in them written as />" | <reading A> | <reading B, or the fix you would make>
WASTE | <minutes> | <what took the time> | <why>
PROPOSE | <part id, e.g. P10> | <file> | <the change, one line> | <the score it should move, and by how much> | <the drill that would show it> | <evidence: file and sha16 or numbers>
```
- kind is one of: contradiction (two lines that cannot both be followed), two_readings (one line, two ways), stale (names something that changed), missing (a step or fact you needed and no file gives), unclear.
- two_readings also covers a line you had to choose a reading for, even when you are sure you chose right. Write it as: reading A = `picked: <the reading you used>`, reading B = `other: <the reading you did not use>; fix: <the words that leave only yours>`.
- Two-readings check (required in every report, before you write the MESSY list): go back over each rule line you acted on (a rule, cut, count, order, scope, condition or default you applied). For each, ask: could an agent who read only this line, carefully, have done something different? It could when the line has a word whose scope or reference you had to settle (each, per, of, its, all, any, the, it, this, and/or, before/after, at least/under, which list, row, run, round or file), a number whose base or unit is not said, or a value that depends on something the line does not pin down. Each such line is a MESSY two_readings line.
- At most one PROPOSE line. Any number of MESSY and WASTE lines.
- A quote keeps its words except the separator: a table cell or any text holding " | " is quoted with " / " ("+1.0 / +2.0", not "+1.0 | +2.0").
- Before you end, count each line's fields, split at " | ": MESSY 6, WASTE 4, PROPOSE 7, NONE 2. One line off loads nothing.
- A list with nothing in it gets one line: `NONE | MESSY`, `NONE | WASTE` or `NONE | PROPOSE`. Every report has all three lists. Write `NONE | MESSY` only after the two-readings check above found no line and no other kind applies.
- Example:
```
## REPORT
MESSY | two_readings | lean_v1/HUNTER_RULES_V2.md | "R1 under 334 graded waves: make the 10 pct cut" | cut 10 pct of 334 | cut 10 pct of R1's own waves
WASTE | 4 | a COUNT on a BTC code stopped NO FIRE ROWS | the data-trap line said use op market
MESSY | two_readings | {PACK}/JOB_SHEET_V1.md | "poll each job until it ends" | picked: poll every job filed, one at a time | other: poll only the last job filed; fix: "poll every job you filed, one at a time, until each ends"
NONE | PROPOSE
```
The orchestrator loads it with `python3 -B {GENERIC}/tools/registers/reg.py import-report <file> --from <your id or run>`. If an agent's write of its report file is refused, it ends its reply with the block and the orchestrator loads it from there. A refused line is fixed by its author (" / " inside fields); if the author is gone, the orchestrator copies the file, changes only the separators, logs that, and loads the copy. All or nothing: if any line is malformed, the tool names every bad line and loads none, so the block is fixed and loaded whole.
