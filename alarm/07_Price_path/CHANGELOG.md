# 07 Price path: what changed (newest first)

## The tool here: idea_to_grade (details and sources: [idea_to_grade/CHANGELOG.md](idea_to_grade/CHANGELOG.md))
| edition | status | what changed and why | source |
|---|---|---|---|
| V3.2 (here) | released 26 Oct 08:25Z (ALARMLIB) | the two blockers of the external review: the net fill share leaves out NO_COST parents; a resting entry whose decision price is older than 60 s is NO_PRICE | tree/tools/idea_to_grade/RELEASE_idea_to_grade_V3_2.json (changes, tests), idea_to_grade/README_V3_2.md |
| V3.1 | released 25 Oct 21:52Z after the independent review (CODE OK) | V3 plus the review's six fixes (feed holes, universe check, ledger, signed move, alarm id, one shared rules copy) | tree/tools/idea_to_grade/RELEASE_idea_to_grade_V3_1.json (review) |
| V3 | candidate, not ready | the alarm library's fixes inside the grader: as-of controls, frozen weights, TOUGH baseline, one fixed grid, costs | idea_to_grade/README_V3_2.md |
| V2.3.1, V2.3, V2.2 | released | onset repair (detect.py, alarm_design V3.8.1); alarm_design V3.8; a missing source day frozen in the run's identity | idea_to_grade/README.md; the release records in tree/tools/idea_to_grade/ |
| V2.1, V2, V1 | candidates | price cache revalidation and run inventory; guards and records; the first edition | idea_to_grade/README.md; the CANDIDATE records in the dev tree |

Not here (TEST or CANDIDATE; README, "In development"): markout v1 and v1.1; the speed twins S2, S3, S6; V3.2.1; V3.3 and V3.4.0;
the price path job tools, template and prereg; the KIT_V5 ENTRY job and PROCESS_V7; reg_append_v1.

## This folder
- 30 Oct 2026, helper H3 (third start, for SCOUT): checked the earlier work against the dev tree (the status of every edition in
  its own files; 46 of 46 pinned files here at the pinned sha16s); added the SUMMARY row of how the grader loads its pinned files
  and one missed comment row to MACHINE_PATHS.tsv; the owner seat on the first line of idea_to_grade/SCOPE.md and CHANGELOG.md;
  the test and mutant roles in MANIFEST.tsv; README rewritten (layout, tools, in development, run, data and settings); the proof
  run again from the repo and from a fresh copy of the Alarm folder (RUN_PROOF.md).
- 30 Oct 2026, layout (coordinator): each tool's documents in `<tool>/` (idea_to_grade/), every byte copy under `tree/`; the old
  paths in REMOVE.tsv ("moved under tree/").
- 30 Oct 2026, released editions only (the owner, option a): the TEST editions copied before were taken out (REMOVE.tsv, "TEST edition,
  not released"); the grader V3.2's own release files added (I2G_PINS_V3_2.json, full_population_v3_2.sh, regress_v3_2_ext.py,
  test_i2g_v3_2_real.py) and the library code its test loads (alarm_core_v1_1.py, alarm_core_v1_2.py).
- 30 Oct 2026: the grader's kernels and tables copied in (BED, OUTSIDE, alarm_match, alarm_stamp, entry_card, event_decisions,
  alarm_context, labcore, event_profile, alarm_design, alarms, model_v1; the cost table, the window table, the roster), so every
  file its pins name is inside Alarm.
- 30 Oct 2026: first copy (the markout, the grader S6 chain, the price path job tools; helper H3 for SCOUT).
