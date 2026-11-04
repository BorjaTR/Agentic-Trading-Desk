# PROCESS V7: from an idea to an alarm that can go to strategy (SCOUT, run CLAUDE1_20261028, 2026-10-29T12:20:22Z from the clock). PROPOSED for the owner. TEST, NOT REVIEWED.
the owner 29 Oct 11:47 Berlin: "THE MAIN GOAL OF TODAY IS TO DELIVER A PROCESS THAT GOES FROM IDEA TO ALARM ... THAT BUILDS ALARMS THAT CAN
MOVE ON TO THE STRATEGY PHASE". 12:05 Berlin: "direction alone is enough for the alarm ... what we need to prove is that the machinery works
first ... in synthetic data it can find what it claims to find and then ... in real ideas it shows that the alarms can become a strategy".
This file is the whole path on one page. It promotes PROCESS_V6 section 9 (22d03e1f72ad740f, CLAUDE1 with CODEX1) to the process, keeps
its front end IDEA_TO_ALARM_V4 (15bdefeab9f306b6) and sections 2 to 8, closes the GAPs it listed, and adds the proof (section 4).
Where V6 and this file differ, this file wins. Rule book: team/LAB/notes/WORKING_SESSION/WORKING_SESSION_V15.md.

## 1. In short
- An alarm is a moment named from data known at that moment, with a side (FADE or FOLLOW) and a horizon. Direction alone is enough.
- It passes when, after it fires, its side wins the race (+2c before -1c) more often than at 3 matched random moments AND more than the
  other side does (the LEAD), in most months, with a luck bar (t of at least 3).
- Before it goes to strategy, STRATEGY's own entry check runs on it here (their grader + price path, Sep-Dec): it arrives admitted.
- Every machine in this path was first shown to work on made-up alarms with a known answer (section 4).
- Money (which fires to take, exits, size) is the strategy stage's job, never a reason to stop an alarm here.

## 2. The steps
| # | Step | Do | Stops when | Tool (proof status) |
|---|---|---|---|---|
| 1 | Idea | why price should move after this moment; the strongest other explanation | no reason in plain words | templates/IDEA_CARD_V5.md (22548c37d2d2c679) |
| 2 | Six quick checks | PREMISE, METRIC CONTRACT, SIZE/COST, SUPPORT, PRIOR, DIRECTION: each PASS, GAP, FAIL or NOT_CHECKED with one number | FAIL on METRIC CONTRACT or SUPPORT | IDEA_TO_ALARM_V4.md; QUICK_CHECK_EXAMPLES_V2.md; METRIC_MENU_V1.tsv; metric_brief.py |
| 3 | Alarm card and hand check | registry readings, the exact rule as a definition (sha16), three cases worked by hand (fire, boundary, missing) | the engine disagrees with a hand case | templates/ALARM_CARD_V3.md (cc7a3e9f97d43858); detect (planted and look-ahead tests: idea_to_grade/test_detect.py ef3b5e9a5d1c189e); tools/hc3_v1 |
| 4 | Freeze and log | rule, side, horizons and forecast sealed by sha16 before any outcome; every variant counts as a try | | a PREREG file; tools/reg_append_v1.py (VARIANTS, FORECASTS, THOUGHTS) |
| 5 | Grade on the design months | (a) direction: both sides against 3 matched random moments, race +2c before -1c at 5 m, 15 m, 1 h, by month, waves as the unit; (b) price path: STRATEGY's grader store and markout on the fire list (section 3) | (a) FAILED TEST on the full Sep-Dec count; (b) STRATEGY's own gate stops it (no edge before cost against calm moments at any wait and horizon in both halves). CLEAR (the edge's 95 pct range above 0 at 15 m or 1 h, both halves above 0) is the reading that counts: PROPOSED as a PASS condition (section 5, item 1) | (a) alarm_grade_chain_v2_0_to20251231.sh 94273faf1e927ddc, PROVEN (section 4); (b) job template ideas/STRATENTRY/job_twins/TEMPLATE_STRATENTRY_V3.job.sh.txt, read with tools/read_stratentry_v1.py: PROVEN on real alarms and made-up controls with V2 (section 4, step 2); V3 drops only the exit ladder, which S2 never reads, and has not run yet |
| 6 | Forward months | one opened month at a time, forecast sealed first, postmortem with a Conditions reason or UNEXPLAINED | | alarm-month-cycle; alarm_grade_chain_v2_1_to20260430.sh 99e8a229617cb2e2 (same code, wider window); tools/month_read_v3.py; tools/conditions_v1.py |
| 7 | Hand-off test | per wave: LEAD = (lean minus its random) minus (other side minus its random). R1: LEAD +3 or more at 15 m or 1 h in at least 2 of every 3 counted months (30+ waves). R2: R1 AND pooled t of at least 3 (waves as the unit, day-block error; over 40 tries in the idea family: the Bonferroni z, 50: 3.09, 100: 3.29, 200: 3.48) | R1 misses | tools/lead_null_v1_to20251231.py 22b58c1c72aab4f2, PROVEN (section 4) |
| 8 | Decision | PASS (R2; PROPOSED: and CLEAR): to strategy with the package (section 3). NEEDS MORE MONTHS (R1 only; PROPOSED: or R2 without CLEAR): kept, re-tested as months open. STOP (not R1): the reason written | | DECISIONS row (reg_append_v1.py) |

Outcome states, what never closes an alarm, the month walk and the working rules: PROCESS_V6 sections 4, 5, 7 and 8, unchanged, plus two
rules from 29 Oct (the drive filled): declare a job's WRITES_MB from a measured run, and read hb/DSK at every check while a job runs.
B3 (+5 above random) and B4 (lean ahead by +3) stay as the month readings; the hand-off decision is step 7.

## 3. The hand-off package (what strategy receives; their S0 and S2 done here)
1. The frozen card (ALARM_CARD_V3) with its definition sha16, the fire list and its sha16, the sealed forecasts and the try count.
2. The grade cards by month and the hand-off result (R1, R2, LEAD and t at 15 m and 1 h, waves).
3. STRATEGY's S0: their grader (idea_to_grade_v3_2_s6) run on the fire list cut to 10 Sep-31 Dec 2025, with a scratch registry row (their
   registry is never edited), through tools/run_alarm_store_v10_3_noladder.sh (45ac17404e5dc762): STRATEGY's run_alarm_store_v10_3.sh
   minus its ED3.2 exit ladder. Never run the ladder for S2: it wrote 8 to 21 GB a job and filled SCRATCH_DISK on 29 Oct (SCOUT's error;
   FINDINGS_STRATENTRY_V1, Incident). This closes PROCESS_V6's step 5 GAP: the markout needed a grader run, and the grader knew only 6
   registry alarms.
4. STRATEGY's S2: markout_v1_1 (3239e4685080894e) at waits 0, 60, 300 s, halves at 1 Nov: the edge before cost against calm moments
   (CALM_EDGE) and against same-move moments (TOUGH_EDGE), and money after our cost (V2_1h, market and waiting orders, HONEST cost).
   One runner job per alarm: python3 -B tools/file_entry_job_v2.py <V> <Q_Vn> [--behind] (12f508e3fc6e447f, files from the no-ladder
   template ideas/STRATENTRY/job_twins/TEMPLATE_STRATENTRY_V3.job.sh.txt fe0851a5040afa63; inputs table: one row per alarm with its fire
   list, definition, card, lean). The template pins its prereg and inputs table: for new alarms, copy it with the new sha16s. Declare WRITES_MB from a measured run (DSK sizes the first one). Measured today: 997 fires
   54 s, 1,979 fires about 1.5 min, 5,042 fires about 4.5 min (9,202 fires: store 134 s + markout 333 s; 17,101 fires: 202 s + 545 s; three jobs at once).
5. Read: python3 -B tools/read_stratentry_v1.py <inputs.tsv> <receipts dir> (per alarm: GATE, CLEAR, TOUGH, money, gates A and B).
Strategy then starts at its S3 (contract): S0 and S2 are done, S1 (one money ledger) is theirs.

## 4. Proof that the machinery works (the owner's ladder, 29 Oct 12:02 Berlin: hand cases, no edge, planted edge, traps)
Step 1, made-up data (FINDINGS_SYNTH_V1 3cd4db6cdb1e4f35; PREREG_SYNTH_V1 bb60a3e949c8240c; jobs 20263645-48): verdict WORKS.
DAYPOKE2's 5,039 real fires (Sep 10-Dec 31, 1,223 waves) with only the side made up (tools/plant_sides_v1_to20251231.py 047811e403074f8b,
11 tests, 7 of 7 mutants caught), so the true LEAD of each copy is known:
| copy | true LEAD 15 m | measured 15 m (t) | hand-off | should be |
|---|---|---|---|---|
| SYN0A no skill | -1.8 | -1.5 (-0.8) | STOP | STOP |
| SYN0B no skill | +1.7 | +0.9 (+0.5) | STOP | STOP |
| SYN5 small edge | +7.5 | +6.4 (3.2) | PASS | PASS |
| SYN10 edge | +11.2 | +11.8 (7.0) | PASS | PASS |
| SYN20 big edge | +19.7 | +18.7 (10.1) | PASS | PASS |
| SYNM10 wrong way | -10.3 | -9.8 (-5.5) | STOP | STOP |
- Every measured LEAD within 1.53 points of its truth (the bar: 3 points or 2 SE).
- Luck: no-skill copies pass the hand-off 0.3 to 1.3 pct of the time; with the months rule alone (R1) 7.7 to 15.8 pct: keep the t bar.
- Power on a 1,223-wave alarm: a true +3 passes 6 to 13 pct, +5 32 to 49 pct, +7 65 to 86 pct. Small alarms see less (294 to 580
  waves: +5 passes 2.5 to 8.8 pct). NEEDS MORE MONTHS is the normal answer for a weak alarm, not a failure.
- Traps: (a) a reading that peeks at the future is ignored by detection (test_detect.py test_real_future_plant_and_prefix); (b) busy
  moments: both no-skill copies beat random on BOTH sides at 5 m (+4.6 to +5.8): a "beats random" bar alone would credit them, the LEAD
  does not (why 5 m never counts alone); (c) a list built from the result: the grade cannot see how a list was made, so lists are for
  controls and proofs only, never an alarm.
Step 2, real ideas into strategy (FINDINGS_STRATENTRY_V1 d3ea05b14cc11498; PREREG_STRATENTRY_V1 de6b9079aa444fa7): verdict WORKS.
The 14 real versions of the hand-off and 3 made-up controls through STRATEGY's own grader and price path (Sep-Dec; jobs 20263654-67,
20263669-70; tools/read_stratentry_v1.py efe30de7fdfd2c59, 38 hand cases, 21 of 21 mutants caught):
| group | STRATEGY's gate | CLEAR | own edge (TOUGH) clear | money after cost, waiting orders, above 0 |
|---|---|---|---|---|
| kept by the hand-off (9) | 9 | 8 | 3 (FDA2APR, DAYPOKE2, N1APR) | 1 (FDA2APR) |
| stopped (3 of 5 read; N5APR, N4BAPR lost to the full drive) | 3 | 3 | 1 | 0 |
| no skill (SYN0A, SYN0B) | 1 | 0 | 0 | 0 |
| planted (SYN10) | 1 | 1 | 1 | 0 |
- The kept alarms carry their direction into the price before cost: they can enter strategy. Every run passed its own gates.
- STRATEGY's gate alone let an empty copy in; CLEAR did not: step 5b reads CLEAR.
- The race hand-off is the stricter test (stopped versions can be CLEAR on price; PPS2APR, one month short on Sep-Dec, held 4 of 4
  Jan-Apr months): the hand-off stays the decision, CLEAR is a second condition (section 5, item 1). CLEAR is statistical, not a size:
  with 17,000 fires an edge of a third of our cost is CLEAR (N2LAPR); the race (+2c before -1c) is what carries the size against cost.
- Taking every fire is not money after our cost: strategy's take-or-skip model and exits are what turn an edge into money.

## 5. Open (the owner decides, one at a time; SCOUT's pick first)
1. Does PASS need both views, the race hand-off (R2) AND a CLEAR price path (section 3)? Pick: yes. Two different measures of the same
   claim must agree before strategy spends work on it; an alarm with only one goes back as NEEDS MORE MONTHS.
2. Re-test the hand-off on all opened months (Sep 2025 to Apr 2026) for every alarm short of a bar (NEEDS MORE MONTHS, or not CLEAR).
   Pick: yes. Power grows with waves (section 4); the tools need a window twin to 30 Apr, units first, one job.
3. Report the alarm's own edge (TOUGH: beyond moments with the same move and volatility) on every card, never as a gate. Pick: yes.
   Direction alone is enough for an alarm; strategy will rank its work by it.

## 6. Commands in order (one new alarm V; RUN = team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028; every data step is a runner job)
1. Cards: templates/IDEA_CARD_V5.md and ALARM_CARD_V3.md; the definition JSON (example ideas/LOOP2/defs/LP2_DAYPOKE_DEF_V2.json);
   hand cases: tools/hc_defs_v1_to20251231.py or tools/hc3_v1.
2. Freeze: a PREREG file; python3 -B tools/reg_append_v1.py RUN VARIANTS - (and FORECASTS) with the row as JSON on stdin.
3. Grade (job): LEAN=FADE bash F/team/RESEARCH/tools/alarm_process/alarm_grade_chain_v2_0_to20251231.sh <V> <fire list> <work dir>
   (Sep-Dec; alarm_grade_chain_v2_1_to20260430.sh for opened months): CARD_<V>.txt, SUM_<V>.tsv.
4. Price path (job): one row in an inputs table, python3 -B tools/file_entry_job_v2.py <V> <Q_Vn>; read with tools/read_stratentry_v1.py.
5. Hand-off (job): one manifest row (ideas/HANDOFF/INPUTS_V1.tsv format), then
   <PYTHON> -B tools/lead_null_v1_to20251231.py --manifest <file> --out <new dir> --flips 10000.
6. Decision: python3 -B tools/reg_append_v1.py RUN DECISIONS - ; a PASS goes to STRATEGY with the package (section 3) and a FOR STRATEGY line.
7. A changed machine is proven again before any real use: tools/plant_sides_v1_to20251231.py on a real fire list, steps 3 and 5, read
   with tools/read_synth_v1.py by PREREG_SYNTH_V1's lines.

## 7. What this process does not prove
Money (strategy stages S3 to S10: contract, their own made-up data proof, one development run, exits, forward months); months after the
ones opened; the tools' own correctness beyond their units, gates and the proofs above.
