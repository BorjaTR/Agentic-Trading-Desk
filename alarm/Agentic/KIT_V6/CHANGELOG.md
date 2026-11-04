Written by SCOUT for the repo on 30 Oct 2026 from KIT_V6/README.md ("Changes from KIT_V5" and the round sections) and
tree/ALARM_DESIGN/KIT_V6/MANIFEST_SHA16.txt; not the owner's document (owner seat: SCOUT).

# CHANGELOG: ALARM_DESIGN KIT_V6 (newest first)

The kit's record is MANIFEST_SHA16.txt (round 6 edition, 29 Oct 23:23:03Z; its first line says TEST, NOT REVIEWED); the earlier files
are twins in the dev tree's KIT_V6/_old/twins/ (SCOUT's tidy, 30 Oct 12:20Z). Every line below is from the README; evidence rows in
LEARNINGS_V6.tsv.

| round (before, UTC) | what changed | evidence |
|---|---|---|
| 6 (30 Oct 00:15) | the goal is a FOUND alarm: a new PASS whose Jan-Apr MONTH holds in 3 or more of 4 months, its MONTH queued at once and read before DONE; COUNT first; seal both ideas and queue both GRADEs before reading either; agents read their failed step's log on SCRATCH_DISK; MONTH jobs get the 26 coin parts once reviewed; IDEA_GUIDE_V4 | V6-47 to V6-54 (the owner 29 Oct 23:13 and 23:30 Berlin) |
| 5 (29 Oct 21:55) | the forward-only route (KIT_V5 queue MONTH --forward-only, decide_forward_v1.py); decide_v1.py --entry-too-big; families: proven ones with new inputs, one exploration family at most; IDEA_GUIDE_V3 | V6-41 to V6-45 (the owner 29 Oct 22:02 Berlin) |
| 4 (29 Oct 20:20) | the best variant graded alone first; fires under about 20,000 per variant; link the card before ENTRY; run disk budget 10,000 MB; a STOP whose other side won is a forward-only candidate; REGISTRY/SCOREBOARD.md; IDEA_GUIDE_V2 | V6-32 to V6-37 |
| 3 (29 Oct 19:00) | a clock in every prompt; two ideas from the start in two named families; WHY FAILED and NEXT IDEA lines; IDEA_GUIDE_V1; the card names its family, new input and expected waves; a 5-minute reading list | V6-24 to V6-31 |
| 1-2 (29 Oct, from 17:20) | KIT_V6 itself: the goal is one NEW alarm that passes, then stop; one card per idea; audit at checkpoints; waiting that fits the VM; setup and memory measured before COUNT; the KIT_V5 tool fixes of round 1; from round 2 at most 8,000 MB of uncleaned scratch a run | V6-01 to V6-18; FINDINGS_AGENTTEST_V1 L4 |

`tools/idea_time_v1.py` (29 Oct 18:01) is in the folder but not in the manifest.
