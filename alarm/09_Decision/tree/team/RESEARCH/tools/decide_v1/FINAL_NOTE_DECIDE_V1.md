# Decision tool V1: final note (DECIDE seat, 26 Oct 2026)

**Verdict.** The tool is DONE for research use. The first rule it tested, the M skip line, FAILED, and nothing pays for M after cost. The tool works and tells the truth. The idea it carried did not make money.

## The tool
- **What it does.** One generic command for any alarm, coin set or day range. It turns every fire into TAKE or SKIP with a reason, from the frozen library cards and a rulebook. The lab's grader, idea_to_grade V3.1, then grades the decisions. The tool never reads a price.
- **Releases.**
  - RELEASE_DECIDE_V1_CANDIDATE.json e76e30fb282f6990: reviewed READY for research (REVIEW_DECIDE_V1_INDEP.md 65e95a087803a5bc); builder signed, SIGNOFF_V1 row 82.
  - RELEASE_DECIDE_V1_0_1.json: doc-only on top of it. The code that decides is unchanged (decide_v1.py d8cd9acfd7b126d5, decide_rules_v1.py unchanged). It changes:
    - the M rulebook (S1 FAILED);
    - this note and the README;
    - the meaning checker (runs on the Mac too, and reports a changed rulebook instead of crashing);
    - make_release, which now lists the loop files.
- **How it was checked.**
  - Tests 25/25, mutants 51/51, edge cases 33/33.
  - The 25 Oct kit: 10 rows PASS with old vs new receipts, 8 NOT_APPLICABLE with reasons (KIT_DECIDE_V1.md).
  - Two identical runs gave the same bytes. The meaning loop passed 67/67.
  - The reviewer's own recompute found 0 differences on 33,861 rows.

## The outcome loop (ALM_M_V1, Sep-Dec 2025, taken vs skipped on 24 Sep - 31 Dec)
Folder <SCRATCH>/work_DECIDE/loop_v1_1_run. It ran 4 GRADED runs, each with its own ledger PREREG row before it started. The PREREG is DECIDE_LOOP_PREREG_V1_1.md, with ADDENDUM_1 raising the bar for 22 tries. The independent audit passed: AUDIT_DECIDE_LOOP_V1_1_INDEP.md 972a812dea5bb3c2.

| what | result |
|---|---|
| verdict | NOTHING PAYS |
| skip line S1 (skip the fade when the book is TIGHTER) | passes in 0 of 22 cells: FAILED |
| take every fire with a reading | pays in 0 of 22 cells (no cell nets above zero at the stress cost) |
| P1: the fade beats the tough baseline (TT) | 6 of 6: the fade is real against comparable moments |
| P2: TIGHTER fires are worse to fade | 9 of 22: contradicted (their fade edge is higher than TAKE's in 13 of 22) |
| P3a: resting entries net more than TT | 16 of 16 |
| P4: 4 h nets more than 1 h at stress cost | 8 of 9 pairs |
| ledger RESULT rows | VALUED FAIL, TAKE FAIL, SKIPRULE FAIL, BADDATA UNSURE |

**In plain words.** M's fade is a real effect, but it is smaller than the cost. Skipping tight-book fires does not help: those fires fade as well as the others. Resting orders and longer holds point the right way (P3a, P4), but they still do not pay.

## What changed because of it
- RULES_ALM_M_V1.json version 2: S1 is FAILED, kept as a record, and never decides. Entry and exit stay UNSET. The Jan-Feb look is not spent.
- With no active line, M's decisions are TAKE for all 10,764 fires (run_v1_6).

## Open items (none block)
- S3W: its side is UNSET and its FASTER skip has not been graded. When an S3W loop is written, read the skip on the FADE side only.
- Name ADDENDUM_1 in the next PREREG row of the M idea.
- The grader grades slightly fewer fires than the event files hold, by its own eligibility rules (TAKE 8,590 of 8,607). Give parents beside event counts in the next loop.
- An external team review is the owner's wish, now that our reviewers have said go.
