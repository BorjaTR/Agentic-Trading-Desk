Written by SCOUT for the repo on 30 Oct 2026 from KIT_V6/README.md and tree/ALARM_DESIGN/KIT_V6/ (PROCESS_V8.md, MANIFEST_SHA16.txt, ROUNDS.tsv,
tools/idea_time_v1.py); not the owner's document (owner seat: SCOUT).

# SCOPE: ALARM_DESIGN KIT_V6

**Purpose and user.** Make each round of alarm agents faster than the last and never lose an alarm they found. the owner, 29 Oct 18:01
Berlin (PROCESS_V8): "Sessions to find alarms should be faster and faster, learning loops should be faster and faster continuously.
And we should keep a registry of alarms with idea card, alarm card and how it was found so agents can get inspired and also know what
not to copy anymore." Users: the alarm agents (any model), SCOUT and the lead who run the rounds.

**In scope.** How agents work and learn (PROCESS_V8): one idea from start to end with ONE card (templates/CARD_V6.md) and a run report
with minutes per step (templates/REPORT_V6.md); the agent skill (skills/alarm-design-v6/SKILL.md); the learnings with their evidence
(LEARNINGS_V6.tsv: the 45 rows of LEARNINGS_V5 plus V6-01 to V6-54); the launch prompt and each round's filled prompts (rounds 2 to 6);
the idea guides (IDEA_GUIDE_V1 to V4: what made new PASSes, copies and STOPs); the speed table, one row per round (ROUNDS.tsv);
`tools/idea_time_v1.py` (where an agent's time went, from files only; read-only).

**Out of scope.** The job tools and templates: KIT_V5's (queue_job_v4.py, decide_v1.py, decide_forward_v1.py, audit_run_v2.py, the 5 jobs;
KIT_V6/README "Used from elsewhere"). What makes an alarm good: PROCESS_V7 (KIT_V5). The alarm registry and the novelty check
(`ALARM_DESIGN/REGISTRY/`, part 08). Money (the strategy stage).

**Success.** Each round beats the last on minutes from launch to the first new PASS (ROUNDS.tsv; PROCESS_V8 section 5); every decided
alarm is in the registry with its page; from round 6 the goal is a FOUND alarm: a new PASS whose Jan-Apr MONTH holds in 3 or more of 4
months (README "Round 6 changes").
