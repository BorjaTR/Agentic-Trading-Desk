# ALARM_DESIGN KIT_V6 (SCOUT, 29 Oct 2026). TEST, NOT REVIEWED. PROPOSED for the owner.
KIT_V6 changes how agents work and learn (PROCESS_V8). The job tools and templates stay KIT_V5's (proven on the real runner, KITCHECK
29 Oct; fixed during round 1). Agents never edit this folder, KIT_V5 or REGISTRY.

## What is here
| file | what |
|---|---|
| PROCESS_V8.md | the process: one idea start to end, the registry, the learning loop, speed measured each round |
| skills/alarm-design-v6/SKILL.md | the agent's instructions (Claude skill; any agent reads it) |
| LEARNINGS_V6.tsv | the 45 rows of LEARNINGS_V5 plus V6-01 to V6-54 (rounds 1 to 5), each with its evidence |
| templates/CARD_V6.md | ONE card per idea (KIT_V5 had four) |
| templates/REPORT_V6.md | the run report, with minutes per step |
| LAUNCH_PROMPT_V6.md | the prompt; the round's filled prompts are in LAUNCH_PROMPTS_<date>.md |
| ROUNDS.tsv | the speed table, one row per round |
| MANIFEST_SHA16.txt | the sha16 of every file here |
Used from elsewhere: KIT_V5/tools (queue_job_v4.py, decide_v1.py, board_line_v1.py, audit_run_v2.py), KIT_V5/jobs, KIT_V5 front-end
docs (IDEA_TO_ALARM_V4.md, QUICK_CHECK_EXAMPLES_V2.md, METRIC_FAMILIES_V1.md, METRIC_MENU_V1.tsv); REGISTRY (the alarm registry and
novelty_v1.py).

## Changes from KIT_V5 (round 1 evidence in LEARNINGS_V6)
- Goal: one NEW alarm that passes, then stop (V6-01); new = not a copy of a registry alarm (V6-02, V6-03).
- One card per idea; audit at checkpoints and at the end (V6-18).
- Waiting fits the Cowork VM (a call is cut at about 60 s; V6-08); read every hb/SCOUT.txt line (V6-09).
- VM setup and metric_brief env written out (V6-04, V6-07); memory measured before COUNT (V6-06).
- Kit fixes made live in round 1, in KIT_V5's tools: ENTRY size from measured writes, audit A2 and CLEAN labels, board twins, failed
  variants run again under their name, CLEAN takes a failed job, --behind waits behind your own job; from round 2 a run holds at
  most 8,000 MB of uncleaned scratch (4 runs x 15,000 MB plus the 60 GB floor needed 120 GB; FINDINGS_AGENTTEST_V1 L4).

## Round 3 changes (29 Oct 2026, before 19:00Z; evidence in LEARNINGS_V6 V6-24 to V6-31)
- A clock in every prompt: six times from launch (+10 two claims, +15 first COUNT, +30 both counted and one graded, +60 target new
  PASS, +70 nothing new queued, +75 DONE); the round ends for everyone at DONE (V6-25).
- Two ideas from the start, one in each of two families the prompt names; two kept moving (V6-26).
- WHY FAILED and NEXT IDEA lines for every idea, in FINDINGS and POSTMORTEMS (V6-27).
- IDEA_GUIDE_V1.md: what made the new PASSes, the copies and the STOPs, and six questions before a claim (V6-28, V6-29).
- The card names its family, the new input, why the other side should lose and the waves expected (CARD_V6 section 1).
- A 5-minute reading list (V6-31).

## Round 4 changes (29 Oct 2026, before 20:20Z; evidence in LEARNINGS_V6 V6-32 to V6-37)
- Grade the best variant alone in its own GRADE job; a 2nd variant only after reading the first (V6-33): one variant took 4 min alone,
  three in one job 13 to 21 min, and the novelty check waits until every variant of the job is decided.
- Keep fires under about 20,000 per variant: grade time follows fires (V6-37).
- Link the card before an ENTRY job: ln -s CARD_<IDEA>.md ALARM_CARD.md (V6-32).
- Run disk budget 10,000 MB (KIT_V5 queue_job_v4.py and audit A17, from round 3 19:40Z; V6-34).
- A STOP whose other side won is a forward-only candidate, never graded again on Sep-Dec (V6-35); listed in IDEA_GUIDE_V2 section 4b.
- REGISTRY/SCOREBOARD.md: four lists that never overlap (V6-36). IDEA_GUIDE_V2.md replaces V1 (rounds 1 to 3).

## Round 5 changes (29 Oct 2026, before 21:55Z; evidence in LEARNINGS_V6 V6-41 to V6-45)
- Forward-only route (the owner 22:02 Berlin, V6-43): a STOP whose other side won is sealed as its own variant and tested on Jan-Apr only
  (KIT_V5 queue_job_v4.py MONTH --forward-only, decide_forward_v1.py: FORWARD PASS = HELD or STRONGER in 3 or more of 4 months).
  Agents write the candidate as NEXT IDEA; SCOUT runs it. The registry and scoreboard count FORWARD PASS as a PASS.
- decide_v1.py --entry-too-big: NO ENTRY for an R1 variant whose ENTRY can never fit the budget, so its GRADE job can be cleaned (V6-41).
- Families: proven families with new inputs or moments, one exploration family at most (V6-44); IDEA_GUIDE_V3.md (rounds 1 to 4).
- An idea claimed after reading another result gets its Jan-Apr MONTH before it is called new (V6-45).

## Round 6 changes (30 Oct 2026, before 00:15Z; evidence in LEARNINGS_V6 V6-47 to V6-54)
- The goal is a FOUND alarm (the owner 29 Oct 23:13 Berlin, V6-53): a new PASS whose Jan-Apr MONTH holds in 3 or more of 4 months; the
  MONTH goes in at once after the PASS and is read before DONE; REGISTRY/SCOREBOARD.md and the index show both counts.
- COUNT first (the card is written while it runs); seal both ideas and queue both GRADEs before reading either (V6-48, V6-54).
- Agents read the log of a failed step of their own job on SCRATCH_DISK; SCOUT reads SCRATCH_DISK directly (the owner 23:30 Berlin, V6-50).
- Jan-Apr is the real test: 4 of 10 new alarms read held; the side beat random in 39 of 40 months but the size fell (V6-47,
  IDEA_GUIDE_V4 section 1b). Every new PASS so far is a FADE (14 of 14, V6-49).
- MONTH jobs get the Sep-Apr detection in 26 coin parts of 2 coins (team/RESEARCH/tools/month_parts) once reviewed and smoke-tested (V6-51).
- After any interrupt SCOUT lists the agents at once (V6-52). IDEA_GUIDE_V4.md replaces V3 (rounds 1 to 5).
