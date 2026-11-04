# Why COUNT waves exceed graded waves by about 10 percent (SCOUT, 2 Nov 2026)

Answer: COUNT counts every wave of the fire list. The grade counts a wave only when at least one of its fires has a usable matched random moment and an outcome. Fires are the same (3,108 in both for BAGHOLD); the waves without a comparison fall out. Nothing is lost by the wave rule or the window.

Rebuilt from the GRADE's own files with wave_gap/wave_gap_v1.py; every month equals REAL_<V>.tsv exactly on all 4 ideas (receipts/REAL_SMOKE.log):

| GRADE | COUNT waves | graded | gap | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|
| BAGHOLD V1 | 1,190 | 1,076 | 9.6 pct | 69 | 12 | 16 | 17 |
| ATHINHOUR V1 | 979 | 877 | 10.4 pct | 73 | 8 | 10 | 11 |
| CBIGHOUR V1 | 1,144 | 1,011 | 11.6 pct | 91 | 10 | 16 | 16 |
| CR6STOCKOUT V2 | 806 | 742 | 7.9 pct | 39 | 10 | 12 | 3 |

Reasons, dropped waves (BAGHOLD, ATHINHOUR, CBIGHOUR, CR6STOCKOUT):
- COMPARISON_UNAVAILABLE 70, 68, 91, 34. Census status: the matcher will not draw, reason CONSERVATIVE_FULL_DAY_SUPPORT_OR_PRICE_COVERAGE_UNAVAILABLE. Mostly fires of 12 to 17 Sep, whose candidate days reach 4 to 9 Sep, before the window (UNAVAILABLE.json names those days).
- ONLY_OWN_EDGES 42, 24, 35, 29. Census says MATCHED, but every drawn moment is the fire's own, and lead_null skips own edges (read_edges).
- The rest, at most 8 waves an idea: NO_ELIGIBLE, NO_COVARIATE, PARENT_OUT_OF_SPLIT, or no finite outcome.

Where the code does it: lead_null_v1_1_to20251231.py pair_draws (fires_without_edges), fire_leads (complete cases), wave_table (a wave with no complete fire has no lead). SUMMARY.tsv's fires_dropped_15m (510 for BAGHOLD) is this same set, not a bug.

What it means:
- Not a fault in either number, and the lead is not affected: a dropped wave has no comparison to read.
- COUNT overstates September by 30 to 40 pct and the other months by 1 to 6 pct. A rule near the line of 30 waves in September can pass COUNT and not count that month at GRADE. Read COUNT's September as about 60 pct of itself.
- The ungraded waves are not random: they are concentrated in one week of September. Not tested here whether that moves a lead.

Limits: 4 GRADEs of one run, all Sep-Dec 2025; no market file read, no later month. A fix to COUNT itself (printing graded waves) would need the matcher's census and is not built.
