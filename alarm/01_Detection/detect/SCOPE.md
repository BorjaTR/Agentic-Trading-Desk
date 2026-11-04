Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/idea_to_grade/detect.py (docstring), README.md (section "Detection stage alone"), INTERFACE_V1.md (section DETECT) and RELEASE_idea_to_grade_V2_3_1.json; not the owner's document (owner seat: STRATEGY/LEAD).

# detect: scope

## Purpose and user
detect.py turns one alarm definition into its fire list: every (coin, time, side) where the rule fires, for the coins and days asked.
Users: the alarm agents (KIT_V5 COUNT jobs, grade chain v2_0 step 1 on Sep-Dec 2025) and STRATEGY's grader idea_to_grade.

## In scope
- One definition in the lab engine's format (alarm_design: inputs, conditions, onset, refractory, side), a roster, a coin selector
  (all, a set, a named group), first and last day, and a required research window.
- Every value read through the one lab3 reader (purpose research); a value counts only when its quality fields say it is known.
- Outputs in a new folder: EVENTS.tsv (coin, t, side), COVERAGE.tsv (every coin-day: PRESENT, NOT_LISTED, NOT_BUILT, HOLE, REFUSED),
  then DETECT_RUN.json last (status COMPLETE, file sha16s, code sha16s).
- Refusals with a code (exit 2) before anything is read or written; FAILED (exit 3) for an unexpected error.

## Out of scope
- Anything after the fire: prices, outcomes, grading, matched random moments, money.
- Days outside the research window (never opened) and months that are not BUILD in WINDOWS_V1 or that lab3/law.py seals (refused).
- Writing to any data store.

## What success means
- The same fires as the lab engine's own path (GRID equals BASE) and as the outside detector on the reference ideas.
- No look-ahead: a value planted after time T changes no fire at or before T; a run that ends a day earlier gives the same fires.
- Exit 0 with DETECT_RUN.json written last; a hard-killed run leaves no worker and no DETECT_RUN.json.
