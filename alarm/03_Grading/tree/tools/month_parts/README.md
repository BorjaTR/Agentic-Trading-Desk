# tools/month_parts (owner SCOUT; 29 Oct 2026). TEST, NOT REVIEWED until BASELINE.tsv shows 2 PASS.

What: alarm_grade_chain_v2_2_to20260430.sh, the Sep-Apr grade chain of the ALARM_DESIGN MONTH job with the detection in PARTS coin
parts (default 26: 2 coins a part) instead of 2 halves. Everything else is alarm_process/alarm_grade_chain_v2_1_to20260430.sh (99e8a229617cb2e2) unchanged.

Why: over Sep-Apr, detect_aw1.py refused AD13 LIQGAP LG4 at its 2 GiB worker cap: MONTH 20264053 (log `REFUSED WORKER_RSS_CAP:
2147991552 bytes`) and its run again 20264064 (2149875712), both after about 25 s (SCRATCH_DISK judge_scratch/work_AD13_20261029/<job>/
det_LG4_v1_A.log). LG4 is SERIAL_FORCED: one process holds every day. Its Sep-Dec halves peaked at 1565130752 and 1531199488 bytes
(GRADE 20264037 DETECT_RUN.json, read by SCOUT and review 2 before CLEAN 20264075 removed it at 22:49:30Z). AD8 RECLAIM RC2's MONTH
20263985 stopped at the same step after 25 s; its refusal code was lost with its log. the owner's rule (hb/SCOUT.txt 22:16:02Z, 23:13
Berlin): an alarm counts as FOUND only when its Jan-Apr MONTH holds, so a MONTH that cannot run blocks an alarm for good.

Memory (review 1): a per-day index cache of about 6.6 MB a day for any coin list plus a share that grows with the coins; parts cut
only the coin share. Estimated LG4 peaks over Sep-Apr: half 2.14 GiB, quarter 1.85 GiB, eighth 1.7 GiB; never under about 1.55 GiB.
Measured (smoke job 20264079): part A of 8 over Sep-Apr peaked 2029518848 bytes (1.89 GiB; 1982840832 in smoke 20264080, so about
0.04 GiB of run-to-run noise). Review 1 (delta): the cache part of the model holds (SUI alone peaked 1689976832 bytes, 1.57 GiB, smoke
20264081); the coin share is larger than modelled and not additive.
Smoke 20264080 (receipts S1.tsv): parts A to E of 8 over Sep-Apr peaked 1.81 to 1.89 GiB, part F (PEPE to SUI) was refused at
2150924288 bytes, and G and H never ran (the smoke stops at the first refusal). Smoke 20264081: 1 or 2 coins peaked 1.57 to 1.65 GiB
(1689976832 to 1775812608 bytes; 3 of the 26 pairs measured). Hence 26 parts of 2 coins. Smoke v4 (job 20264083) measured all 26 over Sep-Apr: 1671380992 to 1780858880 bytes (part H, DOT and ENA),
0.34 GiB under the cap; every part's peak is kept in the MONTH receipts (DETECT_MEM_<V>.tsv).
Smoke 20264080 S3: a window split (Jan-Apr alone) is NOT exact (1 of 522 rows moved, AAVE 1767709260 to 1767709425: own_pct needs
its 14 prior days; the diff: receipts/20264080_SMOKE2/S3_DIFF.txt).

Use (only through the KIT_V5 MONTH job; never by hand):
  PARTS=26 LEAN=FADE bash alarm_grade_chain_v2_2_to20260430.sh <V> <DEFINITION.json> <W>
Tests (no lab data; 113 s on the VM in review 2, in one call that cannot be split):
  python3 -B tests/test_month_parts_v1.py     (the chain's own step-1 block with tests/fake_detect.py; 19 planted bugs)
Small runs (runner jobs, lab data, minutes, all on AD13 LIQGAP LG4; before the first full MONTH):
  smoke v1 (job 20264079): S1 part A of 8 over Sep-Apr, its memory; S2 Sep-Dec in 8 parts equals the GRADE job's kept list byte for byte.
  smoke v2 (job 20264080): each eighth over Sep-Apr (it stops at the first refusal: F refused); S3 the window split.
  smoke v3 (job 20264081): part F's coins 1 or 2 at a time (measurement only: it always exits 0).
  smoke v4 (30 Oct; review 2 delta: the 26-part code had never run on the Mac): the chain's own block with PARTS=26 under the Mac's
  bash, S1 Sep-Dec byte-equal to the GRADE list, S2 Sep-Apr with every part's memory and one data and one code version:
    bash tests/smoke_month_parts_v4.sh <DEF> <GRADE_LIST> <W> <OUT>     (exit 0: every check holds; 3: one fails; 2: a bad input)
The KIT_V5 MONTH template is wired to this chain only after smoke v4 passes and both reviews PASS (BASELINE.tsv).
Outputs: the same files as v2_1 in <W> (STATUS_<V>.tsv shows detect_A to detect_Z).
Docs: SCOPE.md, REQUIREMENTS.md, ARCHITECTURE.md; BASELINE.tsv (sha16 of each live file, the reviews, the test receipts).
