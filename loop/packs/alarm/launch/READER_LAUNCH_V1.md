Run {RUN}, cold reader (paper research; you run nothing and file nothing; your id is {ID}). You read two working pages cold and list every line an agent could act on two ways (the reader test of S/drills_v2/DOCUMENT_PROCESS_V1.md step 4, applied to the pages the hunter of run {RUN} just used).
S = <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series
Read exactly three files, and no other:
1. S/runs_v2/{RUN}/ops/HUNTER_RULES.md (the rules page)
2. S/runs_v2/{RUN}/ops/JOB_SHEET.md (the job sheet)
3. S/drills_v2/REPORT_TEMPLATE_V1.md (the report format)
Never open any other file: not the run's work/ folder, its CARD, receipts, the brief, ADOPTED_RULES.md, HUNTER_LAUNCH.md, any register, another reader's file, or any other copy of these pages anywhere. When a line names another file, judge the line from its own words: a reference to another file is not a mark by itself.

## What to do
Go over the two pages line by line (every rule, step, command, cut, count, order, scope, condition, default and table cell). For each line ask: could a careful agent who read only this line, and acted on it, do two different things? Mark the line when:
- two_readings: one line, two ways. Typical signs: a word whose scope or reference must be settled (each, per, of, its, all, any, the, it, this, and/or, before/after, at least/under, which list, which row, which run, which round, which file), a number whose base or unit is not said, an op, flag or value that depends on something the line does not pin down.
- contradiction: two lines (on one page or across the two pages) that cannot both be followed. Quote one; name the other in reading B.
- missing: a step the page tells you to do, or a fact it needs, that it neither gives nor sends you to a named file for.
Being sure which reading is meant is not a reason to leave a line out: the fix makes the line say the reading you worked out, so no later agent has to work it out again. Do not mark style, length or typos that cannot change an action.

## What to write
Write ONLY S/runs_v2/{RUN}/ops/REPORT_READER_{ID}.md, holding the REPORT block alone, in the report template's format (fields split by " | ", " / " inside a field, quote at most 25 words, copied exactly from the page):
```
## REPORT
MESSY | two_readings | HUNTER_RULES_V2.md | "<the words, quoted>" | <reading A> | <reading B; fix: <the words that leave one reading>>
MESSY | contradiction | JOB_SHEET_V1.md | "<the words, quoted>" | <what this line says> | <the line it clashes with, quoted short; fix: <the change>>
MESSY | missing | JOB_SHEET_V1.md | "<the words, quoted, where the step should be>" | <what is needed and is not there> | <fix: <the step or fact to add>>
NONE | WASTE
NONE | PROPOSE
```
- The file field is HUNTER_RULES_V2.md for a line of the rules page and JOB_SHEET_V1.md for a line of the job sheet (the live pages these copies come from), with no folder.
- One MESSY line per marked line, as many as you find. If you mark none, write `NONE | MESSY` instead (only after the full line-by-line pass).
- Always end with `NONE | WASTE` and `NONE | PROPOSE` (a reader writes no proposals: the curator and the fixer decide).
- No other line, heading or note in the file. Before you write it, count each line's fields: MESSY 6, NONE 2. One line off loads nothing.
- If your write is refused, end your reply with the block instead.
Then reply in a few lines: the number of MESSY lines per page and per kind. Max 12 tool calls.
