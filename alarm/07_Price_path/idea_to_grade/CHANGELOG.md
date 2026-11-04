Written by SCOUT for the repo on 30 Oct 2026 from the release records (tree/tools/idea_to_grade/RELEASE_idea_to_grade_*.json and, for candidates, the same files in the dev tree), README.md, README_V3.md and README_V3_2.md; not the owner's document (owner seat: STRATEGY/LEAD, per idea_to_grade.py; V3 to V3.2 built by the ALARMLIB seat).

# idea_to_grade: every edition, newest first

Here = copied in this repo (released). Dev only = a TEST or CANDIDATE edition, in the dev tree under team/RESEARCH/tools/.

| edition | date (UTC) | by | status | where |
|---|---|---|---|---|
| V3.4.0 Step A/B (vectors, grade) | 26 Oct | grader thread | CANDIDATE (i2g_v3_3/RELEASE_idea_to_grade_V3_4_0*_CANDIDATE.json) | dev only |
| S2, S3, S6 speed twins | 26 Oct | grader thread | TEST (each file says TEST; no release) | dev only |
| V3.2.1 | 26 Oct 12:46 | grader thread | CANDIDATE, builder side (RELEASE_idea_to_grade_V3_2_1.json) | dev only |
| V3.2 | 26 Oct 08:25 | ALARMLIB | released (RELEASE_idea_to_grade_V3_2.json) | here |
| V3.1 | 25 Oct 21:52 | ALARMLIB | released after independent review (RELEASE_idea_to_grade_V3_1.json) | record here; code superseded by V3.2 |
| V3 | 25 Oct (README_V3.md) | ALARMLIB | CANDIDATE, NOT READY (review) | dev only |
| V2.3.1 | not in the record | i2g_grader for STRATEGY/LEAD | released (RELEASE_idea_to_grade_V2_3_1.json) | here (its files are V3.2's base) |
| V2.3 | not in the record | i2g_grader | released (RELEASE_idea_to_grade_V2_3.json) | record here |
| V2.2 | not in the record | i2g_grader | released (RELEASE_idea_to_grade_V2_2.json) | record here |
| V2.1, V2, V1 | 25 Oct 13:58, 13:45, 12:40 | i2g_grader | CANDIDATE (review or diff recheck pending) | dev only |

## V3.4.0 Step A/B, S2-S6, V3.2.1 (in development, not here)
- V3.2.1: a NO_COST coin's row is unknown in EVERY net row; V3.2 kept RR target exits of those coins in RR HONEST and STRESS rows (only
  winners entered). Proof: 108 of 7,200 ALL rows change on the M store, all RR net. Review round 1: fix right
  (RELEASE_idea_to_grade_V3_2_1.json: change, proof, review).
- S2, S3, S6: speed twins of V3.2, each the same values bit for bit (S2 one-pass exit walk; S3 + V3.4's vector grade; S6 + array setup,
  day text memo, sliced tough window). Pins I2G_PINS_V3_2_S6.json, 60 files (the docstrings of idea_to_grade_v3_2_s2/s3/s6.py).
- Why not here: the owner 30 Oct, option a: the repo holds released editions only.

## V3.2 (released; the edition here)
- B1: the HONEST and STRESS fill share leave out NO_COST parents (GROSS keeps them) (i2g_grade3_v3_2.grade).
- B2: a resting entry whose decision price is older than 60 s is NO_PRICE (i2g_rules_v1_2.passive_entry, the only rules function changed).
- Every other file differs from V3.1 only in names, VERSION I2G_V3_2, run schema I2G_RUN_V3_2 and the pins file name; the signed V3.1
  files stay unchanged because the exit engine ED3 imports i2g_rules_v1.py.
- Why: the two blockers of the external review REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1.md (owner 26 Oct 08:01Z); its backlog is out of scope.
- Evidence: pure 26/26, mutants 43/43, real 13 passed (Mac); full population ALM_M_V1 COMPLETE, VERIFIED, 421 s; regression PASSED
  (fill share 0.9415227198170552 reproduced; 240 of 7,200 table rows change, all net FILL_SHARE).
- Sources: RELEASE_idea_to_grade_V3_2.json (changes, tests, regression_ext, full_population); README_V3_2.md (V3.2 section).

## V3.1 (released after review)
- V3 plus the six fixes and two follow-ups of the independent review: F1 feed holes (a price older than 60 s is unknown; PATH_HOLE), F2
  the universe checked and every input re-hashed before commit, F3 the ledger counts tries (one ask, one run), F4 the 15 min move signed
  per row, F5 --alarm-id required and checked against the registry, F6 one shared copy of the rules (alarm_contract_v1.py); NO_COST coins
  graded before cost only; chain-split sensitivity.
- Why: REVIEW_IDEA_TO_GRADE_V3_INDEP.md; re-review REVIEW_IDEA_TO_GRADE_V3_1_INDEP.md: CODE OK.
- Sources: RELEASE_idea_to_grade_V3_1.json (review, tests); README_V3.md and README_V3_2.md (V3.1 section).

## V3 (candidate, not ready)
- New files beside V2.3.1: matched controls as of the moment; each event counted once (frozen universe weights); event id
  coin_second_side; the TOUGH baseline; one fixed grid of returns and exits; entry types TT, RT, RR with costs per coin; --delay-s and
  --ledger-ask required; --compat-v2.
- Why: owner 25 Oct: stop the alarm library as a separate project and move its useful fixes into the grading tool, generic for any alarm.
- Sources: README_V3_2.md ("What changed against V2.3.1"); RELEASE_idea_to_grade_V3_1.json (supersedes V3_CANDIDATE: NOT READY).

## V2.3.1, V2.3, V2.2 (released)
- V2.3.1: detect.py changed (23f9cec148975cea to 83c52bfd27166f76) with the shared engine alarm_design V3.8.1: a known-false shared
  prefilter is kept as an OFF predecessor, which recovers a missed real BTC alarm at 2025-10-10 14:58 (the A54-FINAL-01 onset repair).
  Sources: README.md (Evidence); the two release records' file lists.
- V2.3: the shared engine release alarm_design V3.7 to V3.8; pins and documents updated, no grader code changed (the file lists of
  RELEASE_idea_to_grade_V2_2.json and RELEASE_idea_to_grade_V2_3.json differ only in ARCHITECTURE.md, README.md, I2G_PINS_V2.json).
- V2.2: a PRICE day's absence is part of the run's frozen source identity; a day seen in two states refuses the run (SOURCE_CHANGED).
  Source: README.md.

## V2.1, V2, V1 (candidates)
- V2.1: the PRICE index cache revalidated by sha16; the reader's exact file inventory (RUN_INVENTORY) and counts (RUN_INCONSISTENT).
- V2: guards and records only (refusals before staging, strict days, pins, worker watchdog, PRICE frame integrity, verify_run, known_at
  columns); the numbers are unchanged from V1 (three-coin equality re-run).
- V1: the first edition: replaces the outside team's unfinished detector-to-grading chain with the same meaning, imported, in one command.
- Sources: README.md (Evidence, V2.1/V2.2 notes); ARCHITECTURE.md; RELEASE_idea_to_grade_V1/V2/V2_1_CANDIDATE.json (dev tree).
