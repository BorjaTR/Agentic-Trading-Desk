Written by SCOUT for the repo on 30 Oct 2026 from KIT_V6/README.md and tree/ALARM_DESIGN/KIT_V6/ (PROCESS_V8.md, MANIFEST_SHA16.txt,
tools/idea_time_v1.py); not the owner's document (owner seat: SCOUT).

# ARCHITECTURE: ALARM_DESIGN KIT_V6

## Inputs
| input | where |
|---|---|
| the round's launch prompt (seat, run tag, theme, families, the clock) | LAUNCH_PROMPT_V6.md, filled in LAUNCH_PROMPTS_<date>_R<n>.md |
| KIT_V5's tools, job templates and front-end documents | Agentic/tree/ALARM_DESIGN/KIT_V5/ (run from the dev tree) |
| the alarm registry (index, one page per alarm, novelty_v1.py) | `RESEARCH_ROOT/ALARM_DESIGN/REGISTRY/` (part 08; not copied) |
| the agent runs (board stamps, registers, receipts, claims) for idea_time_v1.py | `RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>` |

## Steps (PROCESS_V8)
1. One idea, start to end (section 2): pick from what the registry does not hold, ONE card, COUNT, GRADE, the money path (ENTRY) for R1
   variants, decide (decide_v1.py), new or copy (novelty_v1.py), forward months (MONTH) for a new PASS, stop at the first new PASS.
2. The registry (section 3): every decided variant of every round, rebuilt from the run files, never deleted.
3. The learning loop (section 4): launch, watch (every ASK SCOUT answered; a kit defect fixed at once), wrap-up, harvest (every PROBLEMS
   and LEARNINGS_PROPOSED row accepted or rejected with a reason into the next LEARNINGS), registry rebuild and ROUNDS.tsv.
4. Speed (section 5): minutes from launch to the first new PASS per seat, the share with no job running, time lost and why.
   `python3 -B KIT_V6/tools/idea_time_v1.py <RUN> [<RUN> ...] [--launch SEAT=<time> ...] [--now <time>]` prints the table (read-only).

## Files (tree/ALARM_DESIGN/KIT_V6/; MANIFEST_SHA16.txt, round 6 edition 29 Oct 23:23:03Z, pins 17 of them)
| file | what |
|---|---|
| README.md (7b8eb1ab9a05a34d), MANIFEST_SHA16.txt | the manual, the record |
| PROCESS_V8.md (887dd197b03d83ca) | the process |
| skills/alarm-design-v6/SKILL.md (dd7b640b2fd3e57f) | the agent's instructions |
| LEARNINGS_V6.tsv (f8b361f28a996101) | the rules and their evidence |
| templates/CARD_V6.md (1df0cab7716611a8), templates/REPORT_V6.md (243faa19f9507be1) | the card, the report |
| LAUNCH_PROMPT_V6.md and LAUNCH_PROMPTS_29OCT_R2 to R5, LAUNCH_PROMPTS_30OCT_R6 | the prompt and each round's prompts |
| IDEA_GUIDE_V1.md to V4.md | the idea guides (V4 is current) |
| ROUNDS.tsv (4ec5503c9411888a) | the speed table |
| tools/idea_time_v1.py | the time table (not in the manifest; no test of its own) |

## Settings keys a real run needs
None of its own: the jobs are KIT_V5's (Agentic MACHINE_PATHS.tsv). idea_time_v1.py finds the dev tree itself (`_roots()`, lines 14-18:
BUILT_IN) and reads the runs under `RESEARCH_ROOT/ALARM_DESIGN`.

## Tests
None in KIT_V6. The job tools it uses are tested with KIT_V5 (59 tests, Agentic RUN_PROOF.md).
