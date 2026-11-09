# 03 Grading: what changed in each release (newest first)
- ALARM_V1_22_0 (SCO-A179, 7 Nov 2026): month_parts/alarm_grade_chain_v2_2_7_to20260331.sh (the Sep-Mar grade of the kit), true_gate/true_gate_v4.py (events to 20260331) and tests/test_true_gate_v4.py; law pins moved (law.py 099d649e603074e1).

Sources: `tree/tools/month_parts/BASELINE.tsv` (the release record of chain v2_2: each file's sha16, both reviews, the test receipts) and
the kit's `MANIFEST_SHA16.txt` (in `../Agentic/tree/ALARM_DESIGN/KIT_V5/`). The tool's own CHANGELOG has the detail:
[month_parts/CHANGELOG.md](month_parts/CHANGELOG.md).
## ALARM_V1_21_16_6 (SCO-A162, 6 Nov 2026)
the fast grade chain alarm_grade_chain_v2_0_10_to20251231.sh (c8814705a0796736; the owner 6 Nov 17:55Z "more processes ... running in parallel", 20:37 Berlin "fast version released"): v2_0_7 with idea_to_grade --workers $GRADE_WORKERS (a whole number 1 to 8, default 8) and d1_reports_v6.py (30dcf4aa30b9ab30: Outcomes run(n) from D1_EO_WORKERS, default ALARM=3,RND=5, both lists together at most 8 processes, a list with 0 workers counting 1, a non-integer refused, exit 2), the CHAIN_OUTSIDE_ALARM check kept, and the feed gate named in the STATUS file (gate FOUND <file> <word>, NONE, or MISSING and exit 8).
Tests: test_chain_v2_0_10 6/6, test_d1_v6 9/9, mutants 21/21 caught; proof jobs 20270269, 20270270 (SCO-A161) and the re-proof from the install in the release job.

## month_parts: the grade chain v2_2 (owner SCOUT)
| release | when (UTC), by | what changed and why |
|---|---|---|
| v2_2, 26 parts (583672d036d2ad85) | landed 29 Oct 23:17:48 (SCOUT); review 1 delta PASS; review 2 final PASS 30 Oct 00:24 | v2_1 with the detection in 26 coin parts of 2 coins: over Sep-Apr detect_aw1.py hit its 2 GiB worker cap for AD13 LIQGAP LG4 (MONTH jobs 20264053, 20264064); an eighth still hit it (smoke 20264080); all 26 parts measured on the Mac at most 1780858880 bytes, Sep-Dec rows byte-equal to the GRADE list (smoke v4, job 20264083). Docs fixed 23:43:27; MONTH job wired 30 Oct 00:23:54 |
| v2_2, 8 parts | 29 Oct, review 1 PASS 23:08, review 2 PASS 23:09 | the first reviewed version (not kept: replaced by 26 parts the same night) |

## The GRADE job (KIT_V5)
Since 30 Oct the alarm kit, with its GRADE job template (a520be2650b27910, unchanged since 29 Oct 13:51), is in
[../Agentic](../Agentic): its history is [../Agentic/KIT_V5/CHANGELOG.md](../Agentic/KIT_V5/CHANGELOG.md).

Not released, so not here: chains v2_0 and v2_1, the card, the aw1 step tools, matched random, the menu and the per-fire file
([README.md](README.md), "In development").
