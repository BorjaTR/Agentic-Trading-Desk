# Speed budget of decision tool V1 (DECIDE seat, 26 Oct 2026)

Honesty note: this budget is written AFTER the first runs (26 Oct ~06:00Z: the 8 runs took about 3 s), not before measuring. It is set from the workload, not from that number, and then measured again at the refreeze.

Workload: the 8 runs of run_decide_all_v1.sh: 6 alarms, 18,740 fires, M read twice; each run reads its alarm's context, profile (3 slices) and pre-move cards once. Machine: the Cowork VM on the Mac (warm page cache), nice 10, one process. Cold cache is not budgeted (the cards are on the Mac's disk, read in under a second).

| phase | budget | limit | measured 26 Oct ~06:36Z | measured after the kit fixes, 26 Oct ~06:50Z |
|---|---|---|---|---|
| the 8 runs, wall | 10 s | 30 s | 3.8 s | 5.5 s (admission now hashes every release, receipt and the source list) |
| one M run (10,764 fires), wall | 3 s | 10 s | 1.1 s | 1.2 s: admission 0.15, read 0.74, compute 0.06, write 0.27 (RUN.json timing_s) |
| one M run, peak memory | 1.5 GB | 2.5 GB | 0.83 GB (VM limit 3.9 GB) | not measured again (the rewrite holds the same rows) |
| tests_decide_v1.py | 10 s | 30 s | under 1 s | under 1 s (25 tests) |
| edges_decide_v1.py | 5 s | 10 s | under 1 s | under 1 s |
| mutants_decide_v1.py | 120 s | 180 s | 3 s (33) | 6 s (51) |
| meaning_decide_v1.py on the 8 runs | 30 s | 90 s | 1.3 s | 1.3 s (67 checks) |

Every run now writes its own phase times to RUN.json (timing_s: admission, read, compute, write), so a slow phase shows where it is.
