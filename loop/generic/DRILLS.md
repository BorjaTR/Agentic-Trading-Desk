# DRILLS (generic): how to drill any part of the loop
## Frame (every drill)
- Kit: TASK.md (names at most 3 files to read and exactly 1 file to write, with fixed headings; tool-call and time caps), MATERIAL/, key/KEY.md written BEFORE any agent runs and never in MATERIAL. Keys live apart from the tasks: the folder given to a drill agent holds no key (alarm pack: tasks in packs/alarm/drills/<kit>/, keys in packs/alarm/drill_keys/<kit>/, KEYS.md).
- Agents: fresh and isolated (prompts/drill_agent.md); 2-3 per version (BRIEF vs NONE, old page vs new page, with vs without a skill).
- Snapshots: the brief a past run actually saw; score against what that run really did. Never a held-out number in any material (grep before launch).
- Score by script where the answer is a number or id, else by a separate scorer with the key; never by the drilled agent.
- Log: python3 -B tools/registers/reg.py drill k=v ... (one row per agent); a fix: tools/registers/reg.py improve ... (found_by, before, after, verified_by); then rerun the same drill.
## The parts to drill (generic names; the pack lists its own kits)
| part | drill | pass (example) |
|---|---|---|
| run builder | planted leaks (knowledge in a control, held-out number, missing adopted rule) | every plant refused |
| brief | quiz (combine + traps) brief vs raw notes vs nothing; replay (brief at run n -> what run n+1 found) | brief >= notes + 3; replay 2/2 |
| choosing the idea (step 0) | snapshot brief -> idea; with vs without the skills | cites >= 2 ids, 0 retries, value of information |
| forecast | blind forecasts of past rounds; with vs without base rates | size error below the live hunters' |
| each round | the pack's round drills with planted traps | pack key |
| card | rewrite a past card from its run files | 0 wrong numbers, 0 false words |
| whole process | 12-13 questions on the rules page; rules page vs full prompt | >= 12/13 |
| assessor | a card with planted errors | all caught |
| curator | a finished card, key first | all numbers in EVIDENCE, 0 invented names |
| knowledge tool | planted runs, unknown names, moves | unit tests |
| held-out check | same-definition regrade reproduces the design months | within 1 point |
| proof | planted gap vs null | gap found (p < 0.01), null not (p > 0.10) |
