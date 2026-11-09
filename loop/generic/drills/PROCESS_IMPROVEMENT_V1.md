# PROCESS IMPROVEMENT V1 (SCOUT 2026-11-08; the owner 09:09Z "what is the process to update each thing in the process? The agents propose changes, the curator checks, then we drill and check if it makes a difference")
Documents (rules pages, prompts, skills, step pages, templates, job sheets, the brief): the review, scoring and improvement flow with its chart is drills_v2/DOCUMENT_PROCESS_V1.md (C141).
One way to change any part of the learning process (registers/PARTS.tsv: prompts, rules pages, skills, templates, tools, documents). Three kinds of change (the orchestrator decides the kind; a change that adds or removes what an agent must do is never wording only): normal (a rule, tool or score change: drilled old vs new before it goes live, step 5; the after-arm of that drill is its verifying row), standard (wording only: no step 5 drill; it goes live at once, except between a run's build and its pin, and the next fresh-reader round verifies it; a page passes when two fresh readers agree on at most one problem line), emergency (a fix during a live run: goes live at once, whatever step 6 says; a running hunter's pinned copy is never edited, the hunter is told; drilled after the run). Each stays open in `reg.py audit` until a drill row verifies it.

## The 6 steps
1. REPORT. Every agent (hunter, assessor, curator, drill agent, scorer) ends its output with the REPORT block of {GENERIC}/REPORT_TEMPLATE_V1.md (C130): MESSY lines (kind contradiction, two_readings, stale, missing or unclear, each quoted with its file and both readings), WASTE lines (minutes, what, why) and at most one PROPOSE line (part id, file, change, the score it should move, the drill to show it, evidence); NONE where a list is empty.
2. LOG. The orchestrator loads the block with `reg.py import-report <file> --from <agent or run id>`: MESSY and WASTE lines go to registers/MESSY.tsv, the PROPOSE line to registers/PROPOSALS.tsv (status PROPOSED); a line with a missing field is refused and named, and nothing is loaded until the block is whole.
3. CHECK. The curator, in a separate step after its knowledge work, checks each PROPOSED row: real (the quote is in the file), new (not a duplicate or an already rejected proposal), one part, measurable (names the drill and the score it should move), safe (does not contradict another rule). Verdict CHECKED or REJECTED with one line why. A proposal about the curator's own skill or prompt is checked by a fresh agent instead. Any proposal that touches money, live trading, deletes or the held-out months goes to the owner.
4. DRAFT. The orchestrator makes the change on a copy (<file>_DRAFT or a new version file); the live file is untouched.
5. DRILL. The part's drill (PARTS.tsv drills column) on the live file and on the draft: same task, same key, fresh agents, 2 per side when the drill has a judgment score. Adopt only if the part's score rises, or the defect is gone, and no drill of another part the change touches scores lower (run those drills too). A part with no drill gets one built first (its proposal waits).
6. ADOPT (a change without its drill-after stays an open item: `reg.py audit` lists it until a DRILL_RUNS row says 'verifies <C id>'). Swap the draft live at any time except between a run's build and its pin (a hunter already running keeps its pinned copy; the next pin picks the change up), `reg.py ledger` (sha before/after), `reg.py score` (the part re-scored), PROPOSALS row ADOPTED with the change id (C..) and ledger id; the scorecard doc is updated. REJECTED rows stay, so the same idea is not proposed again without new evidence.

## Gaps and weak parts (C57, the owner 09:30Z "what do you do with gaps and weakest parts? how do we make sure that improves in each part?")
1. FIND: a gap = a part below its pass bar, with no drill, with an open MESSY line, or over its speed target (`reg.py view`). Each is an open item on its part.
2. ORDER: weakest level (NOT_MEASURED, then WEAK, WORKS, PROVEN) first within each PARTS.tsv category; ties go to the part with most effect on run results (P09, P10, P01, P07 first).
3. CAUSE before fix: a stuck check on the part (STUCK_CHECK.md), then the standard fix for its cause:
   | cause | standard fix | proof |
   |---|---|---|
   | unclear or contradictory page | rewrite; fresh-reader drill (H08 style, READER) | the stop rule below (2 readers agree on at most 1 line) + hidden items pass |
   | step skipped in runs | a tool that refuses to go on without it (checker, job template gate), not another rule line | round checker 0 misses in the next run |
   | slow | less to read, or a script does it | median minutes under target |
   | no test | build the drill first (key and hidden items before any agent runs) | drill exists in DRILLS.tsv |
   | wrong measure | change the instrument, re-score the baseline with it | agreement >= 0.80 on the new instrument |
4. ONE change at a time (so the effect is known), steps 4-6 above.
5. PROVE: before and after scores in SCORES and LEDGER; hidden items pass; the next live run shows fewer misses (check_round, assessor MISTAKES).
6. STAY: every run re-scores the parts it touched; hidden items re-checked every 3 runs; a drop below the level sends the part back to step 1; a fixed problem that comes back is a failed fix (counted, DORA change failure rate) and the next fix must be one level stronger (wording -> rule -> tool refusal -> step redesign).
7. STUCK: a part that does not rise after 2 loops changes approach (redesign the step, or a new tool), not wording; a change to the goal goes to the owner.

## When a page goes live (stop rule, C53; first used on the rules page 8 Nov: 11 -> 5/3 -> 3/2 -> 1/1 lines)
The stop rule (the one standard for every page): two fresh readers read the page in the same round; a line counts as a problem only when both report it (the same quoted words); the page passes when at most one such agreed line is left and it is fixed by wording only (no new rule). Lines only one reader reports are fixed when clearly real, and do not count. The page then passes; the next round on it (after any later change) must agree on 0 new lines, or the page goes back to step 4.

## One score for every document, prompt and skill (0, 1 or 2 points each; 10 max)
| check | 2 | 1 | 0 |
|---|---|---|---|
| clear | two fresh readers agree on 0 problem lines (the stop rule above) | 1-2 agreed | 3 or more agreed |
| correct | its task drill passes at its bar | passes with one slip | fails |
| lean | under its size budget (rules page 8 KB, skill 3 KB, prompt 20 KB) | up to 2x | over 2x |
| followed | round checker and assessor find no missed step it asks for | one | more |
| fresh | 0 stale lines (MESSY kind stale open) | 1 | 2 or more |
Tools are scored by their tests and planted drills instead (pass/fail, planted signal found, noise ignored); outcomes (P27, P28) by their own measure.

## Upkeep (part P29)
- After every run and every drill round: log the reports (step 2); proposals wait for the next curator (step 3; a fresh agent for proposals about the curator or the orchestrator's own drafts); `reg.py ledger-check` (0 unlogged changes), re-score the parts that changed or were drilled, update the scorecard doc.
- Before every run build and every release: `reg.py ledger-check` must PASS and no MESSY line on a file the run reads may be open. A MESSY line is closed by the orchestrator with a new row of the same id plus L (`reg.py mess mess_id=M0nnL ... status=fixed fixed_in=<C id>`) once its fix is in.
