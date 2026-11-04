Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/decide_v1/RELEASE_DECIDE_V1_CANDIDATE.json and RELEASE_DECIDE_V1_0_1.json (fields by, made_utc, files: compared file by file) and FINAL_NOTE_DECIDE_V1.md (section Releases); not the owner's document (owner seat: DECIDE).

# CHANGELOG: DECIDE_V1 (newest first)
| release (made, UTC) | what changed and why | files |
|---|---|---|
| DECIDE_V1_0_1 (26 Oct 07:23; in use) | documents and the M outcome on top of the reviewed candidate: the code that decides is unchanged (decide_v1.py d8cd9acfd7b126d5, decide_rules_v1.py 95fc214ed4055afb). The outcome loop for M (PREREG V1.1, 4 graded runs, an independent audit PASS) found NOTHING PAYS and the skip line S1 FAILED, so RULES_ALM_M_V1.json version 2 keeps S1 as a record that never decides. The meaning checker runs on the Mac too and reports a changed rulebook instead of crashing; make_release lists the loop files | changed: README_DECIDE_V1.md, RULES_ALM_M_V1.json, meaning_decide_v1.py, make_release_decide_v1.py; new: FINAL_NOTE_DECIDE_V1.md, loop_v1/DECIDE_LOOP_PREREG_V1_1.md, its ADDENDUM_1, run_decide_loop_v1_1.sh, summarize_decide_loop_v1_1.py (41 files in all) |
| DECIDE_V1_CANDIDATE (26 Oct 06:55; e76e30fb282f6990 in the final note) | the first edition, reviewed READY for research by the independent reviewer (REVIEW_DECIDE_V1_INDEP.md 65e95a087803a5bc, not copied); the builder signed (SIGNOFF_V1 row 82). Tests 25 of 25, mutants 51 of 51, edges 33 of 33; two identical runs gave the same bytes; the meaning loop 67 of 67 | 36 files |

Before the candidate, the first build (26 Oct about 05:50Z) was reviewed NOT READY at 06:20Z; the scope was written after it and says so
(SCOPE.md, honesty note).
