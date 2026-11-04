# 09 Decision: what changed in each release (newest first)

Source of every line: the two release files of DECIDE_V1 (compared file by file) and its FINAL_NOTE_DECIDE_V1.md. Full table:
[decide_v1/CHANGELOG.md](decide_v1/CHANGELOG.md).

## DECIDE_V1 (owner DECIDE)
| release | what changed and why |
|---|---|
| DECIDE_V1_0_1 (26 Oct 07:23Z, in use) | the code that decides is unchanged (decide_v1.py d8cd9acfd7b126d5); the M outcome loop found NOTHING PAYS and the skip line S1 FAILED, so the M rulebook keeps S1 as a record that never decides; the meaning checker and make_release fixed; the final note and the loop V1.1 files added |
| DECIDE_V1_CANDIDATE (26 Oct 06:55Z) | the first edition, reviewed READY for research by the independent reviewer; tests 25, mutants 51, edges 33, the meaning loop 67 of 67, same bytes on two runs |

The step's own tools (the kit's variant decision, forward-only decision, audit, register row, hand-off test and package jobs) have no
release yet: README, "In development".

The alarm kit is kept in one folder since 30 Oct, [../Agentic](../Agentic); its history: [../Agentic/KIT_V5/CHANGELOG.md](../Agentic/KIT_V5/CHANGELOG.md),
[../Agentic/KIT_V6/CHANGELOG.md](../Agentic/KIT_V6/CHANGELOG.md).
