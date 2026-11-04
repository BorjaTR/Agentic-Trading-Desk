# ARCHITECTURE: tools/month_parts V1 (SCOUT, 29 Oct 2026; revised after reviews 1 and 2). TEST, NOT REVIEWED.

## Where it sits
KIT_V5 MONTH job (ALARM_DESIGN/KIT_V5/jobs/JOB_MONTH_V5.job.sh.txt; wired only after 2 PASS and the small runs) ->
PARTS=26 LEAN=<lean> bash month_parts/alarm_grade_chain_v2_2_to20260430.sh <V> <def> <W> -> CARD_<V>.txt, SUM_<V>.tsv -> perfire,
month_read_v3.py per month (unchanged; none of them reads det_*, DETECT_RUN or per-part STATUS rows: review 1).

## The chain (steps of v2_1; only step 1 changed)
1 detect: for part i in 0..PARTS-1, coins = roster[i*k//n : (i+1)*k//n] (roster order), detect_aw1.py --coins <part> --first 20250910
  --last 20260430 --research-window 20250901:20260430 --workers 3 -> det_<V>_v1_<A..Z>/EVENTS.tsv; a failing part stops (exit 3).
  merge: '#' lines of part A, the column header of part A, then every part's rows, sorted by t (numeric) then coin.
2 the plain fire list (rows without '#'); 3 idea_to_grade_aw1.py; 4 make_random_v3.py; 5 event_outcomes_aw1.py; 6 menu_v2.py;
7 alarm_card_v1_3.py. All as v2_1, same pins.

## Memory (review 1, detect_aw1.py and lab3/days.py read in full)
detect_aw1.py stops a worker at 2 GiB (WORKER_RSS_CAP, a released constant at line 58, checked at lines 657-658). A SERIAL_FORCED definition (an own_pct built on
another own_pct, as LG4) runs every day in one process whatever --workers says (lines 690-695, 815-817). That process's lab3 reader keeps
every part index of every day it reads (about 6.6 MB a day, any coin list: 1.6 GB over 242 days) plus the coin data. Parts cut only the
coin share: LG4 estimates over Sep-Apr: half 2.14 GiB, quarter 1.85 GiB, eighth 1.7 GiB, floor about 1.55 GiB. Measured on the Mac
(smoke job 20264079): part A of 8 peaked 1.89 GiB over Sep-Apr; Sep-Dec parts 1.00 to 1.17 GiB (S2). Smoke 20264080: parts A to E of 8
1.81 to 1.89 GiB over Sep-Apr, part F refused at 2150924288 bytes, G and H not run; smoke 20264081: 1 or 2 coins 1.57 to 1.65 GiB (3 of
the 26 pairs). So 26 parts of 2 coins: smoke v4 (job 20264083) measured all 26: at most 1780858880 bytes (part H), 0.34 GiB under the cap, about 0.3 GiB after
run-to-run noise (part A peaked 1982840832 and 2029518848 bytes in two runs); one coin a part would gain at most 0.08 GiB. Smoke v4
S2 measures all 26 parts before the first full MONTH.
A window split is not exact (smoke 20264080 S3: Jan-Apr alone moved 1 of 522 rows; own_pct reads the 14 built days before D). A window to 31 May would
need more than parts (V2: free the index cache, outside this tool's scope).

## Failure modes
BAD_PARTS (exit 2), EMPTY_PART (exit 3), a part's detect refusal (exit 3, its log det_<V>_v1_<h>.log beside it), every later step as v2_1.

## Known limits (V1)
- Parts run one after another and each detect only proves its own reads unchanged: a lab_days rebuild during a job could mix data
  versions across parts (v2_1 had the same gap with 2 halves). The wired MONTH job writes each part's sources and code sha16 into
  DETECT_MEM_<V>.tsv and SCOUT checks one value each before CLEAN (REQUIREMENTS R7). V2: the chain compares them before the merge.
- The tests do not check the per-part log names: review 2's mutant that writes every part's log to det_A.log survives (diagnostic
  only; the wired MONTH job keeps each part's log tail in DETECT_LOG_<V>.txt).
- The merged EVENTS.tsv keeps part A's '#' lines (its selection names part A's coins); the fire list ignores '#' lines.
- INPUTS_<V>.txt does not record PARTS (the MONTH job's STAGES note does); BAD_PARTS is found after STATUS is written (a retry needs a
  fresh W, as every chain run does).

## Tests (tests/test_month_parts_v1.py, tests/fake_detect.py)
The chain's own step-1 block (status line, guard, loop, detect call, merge) runs in bash with fake_detect.py (same arguments, refuses
an existing out folder, per-coin rows written in descending coin order, t values of 3 and 4 digits): PARTS 2, 3, 4 and 8 on a 12-coin
roster out of alphabetical order and PARTS 13, 26 and unset on a 52-coin roster give the expected list; detect arguments checked;
PARTS 1, 27, 30, x, 0 and 9x stop with BAD_PARTS; 5 coins in 8 parts and 12 coins in 26 parts stop with EMPTY_PART; a refused part
stops the chain. Hand-checked partitions of 10 coins, v2_1's halves for 2 parts of 52, cover for 2 to 26. 19 planted bugs, 19 caught.
Review 2 (delta) mutants that survive change nothing (swapped letters, sort -u, no -k1,1), fail loudly on a value nobody uses (a
guard rejecting 9 or 19; ${PARTS-26} with an empty PARTS) or are diagnostic only (every log to det_A.log; --definition "$ROSTER"
with the fake detect). The run takes about 2 minutes (113 s on the VM).

## Small runs (tests/smoke_month_parts_v1.sh to v4.sh, runner jobs, LG4)
v1: S1 part A of 8 over Sep-Apr with the real detect, its memory; S2 the chain's own block with LAST=20251231 and PARTS=8 on the real
roster, its list byte-equal to the GRADE job's kept list (REQUIREMENTS R6). v2: each eighth over Sep-Apr (stops at the first refusal)
and a window split. v3: part F's coins 1 or 2 at a time (measurement only, exit 0). v4: the chain's own block (lines 1 to its first
"fi") with PARTS=26 under the Mac's bash: S1 with LAST=20251231 byte-equal to the GRADE list; S2 Sep-Apr, every part's memory and
one data and one code version, and its rows before 2026-01-01 byte-equal to the GRADE list (exit 0 / 3 / 2).

## Versions
v2_2 = v2_1_to20260430 (99e8a229617cb2e2) + step 1 in parts; default 4 in the first draft, 8 after review 1, 26 after smokes v2 and v3 (583672d036d2ad85). sha16 in BASELINE.tsv.
