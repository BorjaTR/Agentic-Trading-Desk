Written by SCOUT for the repo on 30 Oct 2026 from the 12 release files tree/team/RESEARCH/tools/alarm_design/RELEASE_alarm_design_V*.json (fields by, landing, changed, replaces, tests_result) and README.md; not the owner's document (owner seat: ALARM).

# CHANGELOG: alarm_design (newest first)
Every release is FROZEN: any change to a listed file is a new release, and every run checks the files first.

| release (written, UTC) | by, and why | files changed |
|---|---|---|
| V3_8_1 (25 Oct 15:27; in use; pinned by idea_to_grade V2_3_1) | A54 builder under the owner's authorization; an independent checker signed the closure. The final A54-FINAL-01 repair: a shared condition known to be false makes the step a decided OFF predecessor, so the next valid step can be an onset; BASE and GRID call one shared conditions_known. Replaces V3_7 (V3_8 was an unapproved intermediate cut) | alarm_design_v2.py, README.md, test_onset_knownness.py |
| V3_8 (25 Oct 14:25) | A54 builder: the first cut of the same repair, replaced by V3_8_1 | alarm_design_v2.py, README.md, test_onset_knownness.py |
| V3_7 (25 Oct 14:25) | LAB1, labcore V2_7 cycle (the v2_7 package, S1 run check, S3 selection, S2 quality, lab3 write, bins and days fixes) | alarm_design_v2.py, mutants_alarm_design_v2.py, test_alarm_design_v2.py |
| V3_6 (25 Oct 03:21) | LAB1, labcore V2_6 cycle (lab3/write.py: no_prev D-1 once) | the same three files |
| V3_5 (24 Oct 07:46) | LAB1, labcore V2_5 cycle (law.STORES gains hl_node_cols, candidate_days) | the same three files |
| V3_4 (23 Oct 21:05) | BUILD1, recut for STRATEGY-161519: the A35-AD-01 fix (passed by diff by LAB1 and QUANT); 70 tests | the same three files |
| V3_3 (23 Oct 20:45) | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | not listed in the record |
| V3_2 (23 Oct 20:22) | ALARM: V3_1 plus offer_edges_v1 (the offer after the fire, on the draw V3 base); nests costs V3_4 | offer_edges_v1 and its tests added (the landing text) |
| V3_1 (23 Oct 19:35) | BUILD1, recut for STRATEGY-161519; 63 tests | none (changed: [] in the record) |
| V3 (23 Oct 19:27) | ALARM: V2 plus grade_edges_v1 (LAB1's MUST: start_s honoured, label start check), the list-of-record filter, a verdict without 10-11 Oct beside every verdict | grade_edges_v1 and its tests added (the landing text) |
| V2_1 (23 Oct 19:29) | BUILD1, labcore V2_3 cycle | not listed in the record |
| V2 (23 Oct 18:58) | ALARM: alarm_design_v2 = v1 plus the outside review's D05 (a sealed day stops the run, grid_s), S06 (past-only base, nothing read after the last day, estimand), S07 (typed claims, footprint, one tries ledger, null calibration); LAB1 PASS | the first release of alarm_design_v2.py |

Before V2: alarm_design.py (v1, the design of sections 1-8 of the README), not released. Detection here uses only the engine's
definition semantics (alarm_design_v2.py); the outcome files added in V3 and V3_2 are not copied (ARCHITECTURE.md).
