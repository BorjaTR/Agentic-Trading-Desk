# alarm_first_look: the ALARM FIRST LOOK (SCOUT, 30 Oct 2026). TEST. Current: reader edition 11 (fl_read_v11.py: edition 9's rule, the grade's 30 min waves) and the ladder v4 (fair_v4.py). New, TEST, not reviewed, beside them: edition 12 (fl_read_v12.py, bar_v1.py, fair_v5.py: SIZE at the coin's own dated bar; section "Edition 12"). Reviewed: editions 9-10 and ladders v2-v3 (reviews A to D, reviews/); edition 11 and v4: follow-up next.

the owner 30 Oct 2026 08:30 Berlin (from STRATEGY; replaces the MD prompt): for every alarm, before it goes to STRATEGY, report on the design
months and each forward month. "Reuse the tools we have, do not build a new tool from scratch, the new tool is a command to call the other
built tools." 08:4x: "which came first" = offer +4c vs heat 4c, whichever price level is touched first (the outcome tool's offer_before_heat).
08:50-08:53: the move spent comes from alarm_profile made generic (tools/alarm_profile_v2; edition 1 keeps running).

## This folder (tidied 30 Oct 2026; nothing deleted)
- At the top: these docs (README, SCOPE, ARCHITECTURE, REQUIREMENTS, BASELINE), the current code and the job templates the job makers
  read (`JOB_*.job.sh.txt`). The reader is `fl_read_v11.py` (current, section "Edition 11"; made by `mk_v11.py` from `fl_read_v10.py`,
  `mk_v10.py` from `fl_read_v9.py`, `mk_v9.py` from `fl_read_v8.py`, `mk_v8.py` from `fl_read_v7.py`; editions 5-10 stay beside; the rule in
  force is edition 9's). The ladder `fair_v4.py` (made by `mk_fair_v4.py` from `fair_v3.py`, made by `mk_fair_v3.py` from `fair_v2.py`)
  proves the bars on made-up alarms (section "The ladder"). The waves come from `../labcore/waves.py` (THE ONE wave module). `busy_v1.py` gives how busy any moment was (the normal move, the last hour's range), for the fires
  and the random alike. `fl_read_v4.py` stays because
  `studies/busy_cut_v1.py` imports it, `fl_read_v3.py` because `studies/why_months_v1-v3.py` import it. The scratch cleaner (`clean_scout_scratch_v2.py`, `mk_clean_job_v2.py`) is its own
  tool kept here because its job maker names this folder.
- `tests/` the tests; `studies/` the studies; `inputs/` the alarm lists; `jobs/` the job files sent; `receipts/` and `results/` the runs.
- `_old/`: the replaced editions (reader v1 and v2, lists v1, aprof jobs v1 and v2, cleaner v1) with their tests and job templates, and
  `twins/` (the backups made before edits). `_old/MOVES.tsv` lists every move, so any file can be put back.

## What it calls (no new price code)
| step | tool (existing) | gives |
|---|---|---|
| fires and matched random | the grade chain's PERFIRE (MONTH job; LIST-mode chain run for lists without one: fl_grade_jobs_v1.py, JOB_FLGRADE_V1: alarm_grade_chain_v2_1_to20260430.sh + perfire_v1_to20260430.py) | A rows (fires), R rows (make_random_v3: 3 matched random moments a fire, weights w), the race 2c<1c per fire |
| the two lists of each alarm | fl_lists_v2.py (v1 + --codes and --perfire-dir for the lists graded by FLGRADE) | A_<code>_EVENTS.tsv, R_<code>_EVENTS.tsv, R_<code>_W.tsv, TARGETS_FL.tsv (their sha16s) |
| offer, heat, which came first, speed, money | event_outcomes_aw1.py (run 0) with OUTCOMES_FIRSTLOOK_V1.json, night_export_v3.py (STRATEGY), fl_extract_v1.py (fl_jobs_v1.py, JOB_FLOUT_V1) | best / worst at 1-180 min both sides, OBH4 (offer 4c vs heat 4c first, seconds), REACH4 within 180 min (seconds), returns 15 m, 1 h, 3 h |
| move spent (item 1) | alarm_profile edition 2.2 (tools/alarm_profile_v2/alarm_profile_v2_2.py, RELEASE_profile_V2_2) by fl_aprof_jobs_v3.py (JOB_APROF_V3), each list built twice | AP_<code>.tsv: the push still going at the fire (run end in its last 60 s); APH_<code>.tsv: the hour's extreme (run net of a pullback, with the giveback) |
| waves (edition 11) | tools/labcore/waves.py (imported) | the grade's 1,800 s waves (editions 3 to 10: md_v1's 900 s) |
| months, costs | tools/money_direction/md_v1.py (imported) | months, honest c |
| busyness of fires and random (edition 7) | busy_v1.py (this folder): alarm_profile 2.2's LabSource prices and episode_blocks' Ep.normal, reused unchanged; one job (SCOUT/jobs/20264452_judge_SCOUT_BUSY1.job.sh) | receipts/<job>/BZ/BZ_<A\|R>_<code>.tsv.gz: normal_move_pct, range60_pct, move15_pct; BUSY_V1.json; PROVE_BZ.tsv (the fires' normal move equals the AP files) |

## The reader (fl_read_v3.py; v1 made TRY0, v2 TRY1) and the PASS rule
Unit: each wave once (fires within 15 min of the previous, any coin; a wave belongs to the month and day of its first fire). Levels in
units of the coin's c = cost_bp/100 + 0.032 (must equal the outcome tool's own unit__c on every fire, else refused). Random = weighted
mean over the R rows of the same month. PASS to STRATEGY (design months Sep-Dec; all must hold), the owner's words:
- in at least 3 of 4 months: median per-wave offer within 1 h >= 4c AND (lean offer minus heat at 1 h beats random by >= 2c, OR the lean
  offer comes first at 1 h more often than random);
- top 2 coins, top 5 waves, best 5 days: each under half of the design edge (offer minus heat at 1 h above its month's random, summed over waves);
- at least 30 waves (with a 1 h value) in every design month.
Choices he did not specify, as built: the month edge is the mean over waves; a month holds only when both rules hold; the shares can pass
1 when the total edge is small; the random's weights count 30 min grade waves, the fires 15 min waves; speed is timed from the entry bar.
Reported beside, never a rule, for every month and for Sep-Dec and Jan-Apr: item 1 both ways (push at the fire; the hour's peak) and
PUSH / NO PUSH (median run under one normal 15 min move: the alarm's side is not a price push, e.g. AD4 SETTLEBACK V3's funding sign, so its
move spent is not a move), the random's median offer at 1 h beside rule 1, the windows 1-180 min both sides with which came first, both
sides' speeds and the random's, race and LEAD (PERFIRE; NOT RUN with its reason when missing or changed), the concentration shares, the
result without DASH, VVV, ZEC, without the top 5 waves and without the random moments that sit in the hour before a same-coin fire, the
random's coverage of the grade's waves (flag under 0.8), fires dropped (no cost row; no 1 h value), days with fires, fires and waves,
money after cost (market, waiting) at 15 m, 1 h, 3 h.
Refused: a list, weights file or PERFIRE that is not TARGETS_FL's (sha16); an A or R table that is not exactly its list (coin, t, side);
weights that do not join the random rows one to one; c different from the outcome tool's. An AP file that does not join one to one only
makes that move NOT RUN.

## Edition 7: the alarm's criteria (the owner 30 Oct 2026 15:44-16:06 Berlin)
An alarm marks WHEN; the side is the strategy's call ("the alarm has to be valid for both"). On busy fires only (normal 15 min move
>= 1.12c), all must hold on Sep-Dec, and AGAIN on Jan-Apr (RULE_7 PASS = both; NEEDS MORE MONTHS = Sep-Dec only):
- MOVES: price moves 4c either way within 1 h (OBH4_60M +1 or -1) more often than at equally busy random moments: the busy random in the same
  band pair (normal move in c: thirds; last hour's range in normal moves: 7 bands, cut at 50/80/90/95/98/99 pct; bands from the period's busy
  random, weighted; priced by the fire's own month, else the four months when the month's cell is under 20 effective; a fire busier or
  calmer than every random moment is left out); per wave the mean of (hit - expected);
- STEADY: above 0 in at least 3 of 4 months (under 10 matched busy waves: thin, cannot count) and z >= 2 over the period (waves clustered
  by day + the random's error per cell);
- BROAD: still above 0 without the 2 coins that add most, and without the 5 best days;  COUNT: 30 waves a month.
Beside, never a rule: the lean (edition 6's direction, months and z), MOVES matched on the normal move only, matched / fallback / outside
shares, recent_ratio and normal_ratio (the matched fires' busyness over their cells' random: 1 = equal). No loss check.
Outputs: FL_RULE7.tsv (one row per alarm id), FL_<code>_RULE7.tsv (by month); the JSON's rule_7 and busy_v1 notes.
```
python3 -B tools/alarm_first_look/busy_v1.py build <lab_days> <lab3 code dir> <out dir (new)> <list.tsv>=<name> ...   # inside a job
python3 -B tools/alarm_first_look/busy_v1.py prove <out.tsv> <BZ_A_<code>.tsv.gz>=<AP_<code>.tsv> ...
python3 -B tools/alarm_first_look/fl_read_v7.py <TARGETS_FL.tsv> ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv <out> <FLOUT receipts> ... <APROF22 receipts> ... <BUSY receipts>/BZ
python3 -B tools/alarm_first_look/tests/test_busy_v1.py ; python3 -B tools/alarm_first_look/mutants_busy_v1.py
python3 -B tools/alarm_first_look/tests/test_fl_read_v7.py ; python3 -B tools/alarm_first_look/mutants_fl_read_v7.py
```
First run (job 20264463, 30 Oct): results/TRY4_FL1_20264463/FL_RULE7.tsv (14f94b3595f6abca), results/TRY4_FL2_20264463/FL_RULE7.tsv
(bc490086c22ad89b), busyness from job 20264452 (BUSY_V1.json f3865b04c1a28d47; PROVE_BZ 24 of 24 lists equal).

## Edition 8: two bars (the owner 30 Oct 2026 17:40-17:44 Berlin)
"can be that one alarm has one of both right? maybe we should have more than one bar and a way of proving that we keep the edges and
remove what has no edge"; "okay build it". An alarm passes on either bar; the label says which.
- SIZE (when): edition 7's MOVES: busy fires move 4c either way within 1 h more often than equally busy random moments (same band pair).
- SIDE (which way): every fire with a cost: its lean's 1 h race (+1 offer first, -1 heat first, 0 neither) minus its wave month's random
  (pre-fire moments out, weighted); the same numbers as Look.net_test.
- Each bar, each period: STEADY (above 0 in 3 of 4 months, a month under 10 waves is THIN; z over the period's line), BROAD (above 0
  without the 2 coins that add most, and without the 5 best days), COUNT (30 waves with a 1 h value in every month).
- RULE_8: SIZE+SIDE, SIZE or SIDE (the bars passing Sep-Dec and Jan-Apr, both at z >= 2); NEEDS MORE MONTHS (<bars>) when a bar passes
  Sep-Dec only; else NOT PASS. Tables FL_RULE8.tsv (one row per alarm id) and FL_<code>_RULE8.tsv (per month and bar); the JSON's rule_8.
  Which label wins (review A, 30 Oct): a bar passing both periods names only the bars that pass both (a second bar passing Sep-Dec only
  is not in the label; its columns show it); without BZ tables SIZE is NOT RUN, so a failing SIDE reads NOT PASS though SIZE was never judged.
- First run: job 20264507: results/TRY4_FL1_20264507/FL_RULE8.tsv 0df700a50ba25395, results/TRY4_FL2_20264507/FL_RULE8.tsv 1414d07f53bf01ec.

## Edition 9 (the rule in force, read by edition 11): Jan-Apr confirms (the owner 30 Oct 2026 19:21 Berlin "Okay"; 19:35 "let's make that version the new one")
FDA2APR's side beat random in 8 of 8 months but missed Jan-Apr's z 2 (z 1.33). Jan-Apr now confirms what Sep-Dec found: a bar passes
Jan-Apr at z >= 1 (CONFIRM_Z_MIN), with 3 of 4 months, BROAD and COUNT as before; Sep-Dec keeps z >= 2 (NET_Z_MIN). PERIODS9 holds each
period with its z line (one place, read by the reader and the ladder). RULE_9 is in FL_RULE9.tsv, with RULE_8 beside; FL_RULE8.tsv is byte
for byte edition 8's. RULE_9's month table is FL_<code>_RULE8.tsv (the months do not depend on the z line). Decided on the ladder first
(job 20264539): a no-edge alarm got a label 0 of 400 times on SIDE, 5 of 200 on SIZE. Review A (30 Oct): OF1 and LB2 confirm Jan-Apr on
SIZE at z 1.55 and 1.24, while their own no-edge runs pass Jan-Apr 4 and 5 of 10 (both periods 0 of 10): their Jan-Apr adds little.
- First run: job 20264539: results/TRY4_FL1_20264539/FL_RULE9.tsv 56dbe28289d5aef0, results/TRY4_FL2_20264539/FL_RULE9.tsv
  b72ae6d179458973: 5 new labels (FDA2APR SIDE, HF1 SIDE, OF1, LB2 and WF1 SIZE), none lost; 17 of 20 FL1 alarms pass.

## Edition 12 (TEST, not reviewed; edition 11 untouched): SIZE at the coin's own bar, known then
Since ALARM_V1_19_1 through the queue: `queue_job_v14 ... FIRSTLOOK ... --reader v12`, the chain builds the BAR tables in the job.
why: team/RESEARCH/plans/PLAN_FL12_PERCOIN_BAR_20261102.md (spec and pass rules, fixed before any result). the owner: price moves either way within 1 h by at least B, B = the larger of 6 costs and the coin's own top 13 pct 1 h move over the previous 14 days, known at the moment. Files: FL12_FILES.tsv.
- bar_v1.py builds B for every moment (one run for all lists): cost_pct = (9 + X1.COST.S06 + S08 + 3.2) / 100, the moment's UTC hour cell (Binance 10k walk proxy, never Hyperliquid's); line_pct = 87th percentile of hourly peaks in pct of price on C13.S05, windows ended strictly before t, within 14 days, at least 303 peaks. Definitions from the stopped moment tool (moment_v1.py), checked equal on planted data and on 60 real moments; differences: percent not cost multiples, strict end, 303 not 168. The exhausted guard (> 0.5) never fired and cannot fire on a valued cell (GPT 09:45:02Z: at most 240 of 840): kept as a guard, redundant.
- The hit is stored: BEST_<h>M__FADE and __FOLLOW up to 60 min in the first look tables, 3 s closes of Binance's model price from the entry bar (F+6 to F+9 s), 1,200 bars; a move inside a bar is unseen. HIT if any reaches B; MISS only if both BEST_60M have a value under B; else unknown. On all 48 tables BEST either way >= 4c equals |OBH4_60M| = 1 on all 1,268,486 rows with both (238 rows have OBH only). So the path and edition 11's hit are one source.
- Unknown: a moment with no bar or no path is left out on its own side, never a miss, and counted (FL_RULE12_UNKNOWN.tsv; FL_RULE12_SUPPORT.tsv: all, busy, known, matched, by fires and waves, per month). Costs start 24 Sep, the line needs its 303 peaks.
- Months: THIN (under 10 matched waves) cannot hold, as always; Sep-Dec still needs 3 holding, so a THIN Sep means Oct, Nov and Dec all hold. COUNT is edition 11's (30 waves with a 1 h value, whatever the bar), so unknown bars cannot fail it.
- Named limit: the busy filter and the band cells stay edition 11's, on the October 2026 table c: a retrospective comparison on that population, with only the target B as known then. An alarm-time population needs its own dated membership (open).
- SIDE: fl_read_v12 runs fl_read_v11 unchanged first. Job 20266502: all 105 FL1 and 25 FL2 edition 11 tables byte equal to job 20264600 (FL_RULE9 dbe4f2d4927c398b); fair_v5's 1,240 SIDE rows equal fair_v4's on seeds 0-9; the reader refuses to publish if FL_RULE12's SIDE columns leave FL_RULE9's.
```
python3 -B tools/alarm_first_look/bar_v1.py build <lab_days> <lab3 code> 20250910 20260430 <BAR dir (new)> <list.tsv>=<A_T05> ...
python3 -B tools/alarm_first_look/fl_read_v12.py <TARGETS_FL.tsv> ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv <out> --bar <BAR dir> <receipts dirs as v11>
python3 -B tools/alarm_first_look/fair_v5.py <TARGETS_FL.tsv> ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv <out> 10 5,10 --bar <BAR dir> --plant-seeds 5 [--seed-base 1000] <receipts dirs>
python3 -B tools/alarm_first_look/tests/test_fl12_v1.py ; python3 -B tools/alarm_first_look/mutants_fl12_v1.py ; check_fl12_v1.py: the real-data checks in the job
```
Job 20266502 (team/SCOUT/jobs/; receipts/20266502_FL12/STAGES.tsv; rerun of 20266492 with the support table, same numbers): tests 65 OK, planted bugs 73 of 73.
Ladder fair_v5, FL1, 20 alarms x 10 seeds (plants 5 seeds), SIZE at B, both periods: null fresh seeds 1000-1009: 0 of 200 (exact 95 pct bound 1.83 pct; Sep-Dec 2, Jan-Apr 13 of 200); seeds 0-9: 0 of 200 (1, 8). CALIBRATED both (FAIR_CALIB 8d3fb075e328a920, 77b79a34544d9dbe; z mean 0.10, -0.05; 0.06, -0.09). +10 caught 90 and 89 pct, +5 57 and 52 pct. Seeds are repeats on common data over 20 alarms, not 200 independent trials. SIDE in the same runs: made-up 0 and 1 of 200.
Labels (results/TRY12_FL1_20266502/FL_RULE12.tsv aec5b2b6190616d0; TRY12_FL2_20266502 7f65e1d5bdf97dfa; receipts/20266502_FL12/LABELS_FL1.tsv, LABELS_FL2.tsv), RULE_9 -> RULE_12, 10 of 20 FL1 codes change (14 of 24 ids):
- lost SIZE: T05 (KNOWN_DAYPOKE2, GB1, GA1, its 5 ids; Sep-Dec z 1.95, a hair under 2) SIZE -> NOT PASS; FT1 (z 1.48) SIZE -> NOT PASS; RC2 (z 0.05) SIZE -> NOT PASS; LB2 (z 1.86) NEEDS MORE MONTHS (SIZE) -> NOT PASS;
- gained SIZE: PW1, PW2, RE2, NEWSLATE_V4 NOT PASS -> SIZE; PW3, HF1 SIDE -> SIZE+SIDE.
- FL2: FDA2APR SIDE -> SIZE+SIDE; SYN0A, SYN0B NEEDS MORE MONTHS (SIZE) -> NOT PASS, SYN10 NEEDS MORE MONTHS (SIZE+SIDE) -> (SIDE), the same Sep-Dec z 1.95.
Reading the gains with care (SCOUT's opinion): V4 goes from z 0.44 to 5.39 and RE2 from 0.84 to 3.39; B follows the coin's last 14 days, so a fire when a coin is livelier than its own fortnight hits B more easily; the bands do not hold that fixed and the null cannot see it. Unproved either way.
Unknown (FL1, all rows): fires' bar unknown Sep 16,343 of 25,536 (64 pct), other months 0.3 to 2.8 pct; path unknown 0.1 to 0.7 pct. Busy waves to matched: Sep 2,790 to 986 (35 pct kept), other months 92 to 97 pct kept. Random bar unknown 4.0 pct overall, 61 pct of them in Sep. THIN Sep: only T17 (2 waves) and T18 (6); no label changed by it. T05's 1.95 may be within what the missing Sep would move; not measurable: the costs do not exist. Random hit at B per code and month: 12 to 35 pct, not 13: entry clock, 3 s against minute mids, the 6 cost floor and the random's own population differ.
Not changed: FOUND.tsv, registry, releases.
Input admission (GPT's hold 10:30:53Z; J20266502's outputs stand, all 48 tables match): bars_of now refuses, before any verdict, a BAR table whose bytes differ from BAR_V1.json's `out` digest (read and checked from one read), a manifest of another edition or settings, other row counts or reasons, and a row whose known and unknown fields disagree or whose bar is not max(6 costs, line); fl_read_v12 and fair_v5 both pass through it. cost_of: S10 or S11 empty now reads NO_COST (real cells with that: 0 of 266,802, job 20266523, so no stored table moves).
How to read the labels: all are retrospective. FDA2APR's V12 SIZE+SIDE stays beside V11's SIDE, its label when it was chosen; it appeared after the choice, cannot become the reason for it and is no strategy return. T05 stays NOT PASS at Sep-Dec z 1.95 against 2.00; Jan-Apr z 2.77 does not rescue it. The null's 0 of 200 (upper 1.83 pct) is a binomial reference under independent draws from this construction, not a false-positive bound for future alarms. FL_RULE12.tsv holds RULE_12 and RULE_9 in every row.

## Edition 11 (current reader): the grade's 30 min waves (the owner 30 Oct 2026 21:11 Berlin: "30 minutes")
A fire more than 30 min after the previous one (any coin) starts a wave: labcore's waves (team/RESEARCH/tools/labcore/waves.py
f61b22c588ee6b9a, THE ONE wave module), the same waves make_random_v3 weighs the random by. Before, the fires were in md_v1's 15 min
waves while the random counted 30 min waves (review B S5; job 20264600 moved points by up to 3.3: FB5 SIDE Sep-Dec 4.3 to 7.6, against job 20264539's FL_RULE9). mk_v11.py writes fl_read_v11.py from
fl_read_v10.py (8 replacements). Job 20264600 (FL1, 24 alarm ids in 20 codes): 9 labels change; 13 of 20 codes pass, against 17
(results/TRY4_FL1_20264600/FL_RULE9.tsv dbe4f2d4927c398b; team/SCOUT/receipts/20264600_WAVE30/rule9_changes_FL1.tsv):
- lost: NEWSLATE_V4 (SIDE), OF1, PW1, PW2 (SIZE); LB2 SIZE -> NEEDS MORE MONTHS (SIZE);
- changed: PW3 SIZE -> SIDE; WF1 and FB5 SIZE -> SIZE+SIDE; gained: RC2 NOT PASS -> SIZE;
- FL2 (FDA2APR and the SYN controls): no label changes (FL_RULE9 ee92064488c832a1); FDA2APR SIDE Jan-Apr z 1.33 -> 2.12.
Across alarms SIZE's z falls and SIDE's rises (SCOUT's reading, an opinion: in 15 min waves one burst counted as several waves).
COUNT counts the same 30 min waves (30 with a 1 h value a month), so it is stricter than before. Reviews C and D (reviews/) read the FL1
alarms on the grade's waves on their own and got the same labels (all 28 rows equal FL_RULE9). Why one unit matters (tests/test_fl_read_v11.py
T29UnitWorld, review D): a no-edge alarm whose 3-fire grade waves win and whose lone fires lose reads 0 on the grade's waves and +50 pts
on 15 min waves.

## Edition 10: Look takes the fires' wave ids (review B, 30 Oct 2026)
Look(..., wid=None) keeps md_v1's waves, so every real reading is edition 9's: job 20264593 wrote all 25 FL2 and 105 FL1 tables byte for
byte as job 20264539 (team/SCOUT/receipts/20264593_FAIR3/STAGES.tsv). Given ids (one non-negative integer a fire) replace them, and the
reader still makes each wave's month and day (its first fire's). Only the ladder gives ids: each made-up fire its own wave. mk_v10.py
writes fl_read_v10.py from fl_read_v9.py (4 replacements).

## The ladder: are the bars fair? (fair_v1.py for edition 8, fair_v2.py for edition 9, fair_v3.py: the null by weight; fair_v4.py (current): fair_v3 on edition 11)
On each alarm's own fires and random moments (no new data), both bars run on made-up alarms whose answer is known, both periods:
- null (no edge; both bars), fair_v3: each random moment with a cost and a weight, not a real fire's pre-fire moment, is a made-up fire
  with probability p = min(w, 0.5), each its own wave; the rest is its random, each moment weighted w / (1 - p). The made-up fires and
  their random then have the same expected weighted mean in every cell, and are disjoint (the random's own error stays in). fair_v1 and
  fair_v2 drew one random moment per fire (same coin, 7 days, 1 h of the hour of day): review B found it leaned (below);
- size_plant +D (SIZE): the null with misses turned into 4c moves, so it moves D pts more often than equally busy random;
- side_flip (no side; SIDE): the real fires, each UTC day's 1 h races flipped by a coin, the random's days by their own coins;
- side_plant +D (SIDE): side_flip with lost races turned won, so the lean leads by D pts;
- real: the alarm itself (its rows equal the reader's table).
Every draw is seeded by (seed, code, kind, plant); a plant on seed s is built on that seed's null or flip. Outputs: FAIR_RUNS.tsv (a row
per code, kind, plant, seed, bar and period; fair_v2: its z line), FAIR_SUMMARY.tsv (ALL and per code: runs, passes per period and both,
rates, median z and pts; fair_v2: an EITHER row for the runs that read both bars; fair_v3: Jan-Apr given Sep-Dec and the both-period
rate's 95 pct interval over alarms), fair_v3's FAIR_CALIB.tsv (is the null centred?), FAIR_V1.json, FAIR_V2.json or FAIR_V3.json.
Fair means: the null is CALIBRATED (FAIR_CALIB: |mean z| <= 0.2, sd within alarms 0.8 to 1.25, the alarms' means spread at most 1.3
times their noise; SCOUT's lines, set before job 20264593), a no-edge alarm gets a label (both periods) in under 5 pct of runs, and +10
plants are caught in most runs.

| FL1, 20 alarms x 10 seeds (plants x 5 seeds) | edition 8, ladder v1 (job 20264513, FAIR_SUMMARY d5242ad5c7ed5376) | edition 9, ladder v2 (job 20264539, 71fd3a3c3644214a) | edition 9, ladder v3 (job 20264593, af4bd575990274fa) | edition 11, ladder v4 (job 20264600, ec8cc1d57a43317e) |
|---|---|---|---|---|
| the null centred (FAIR_CALIB) | not measured | not measured (review B: no) | CALIBRATED, all 6 (d0041d61ae7195e3) | CALIBRATED, all 6 (1d0ae290f3a5e8da) |
| SIDE no edge, both periods (made-up; flipped) | 0 of 200; 0 of 200 | 0 of 200; 0 of 200 | 1 of 200 (T11); 0 of 200 | 1 of 200; 0 of 200 |
| SIZE no edge, both periods | 1 of 200 | 5 of 200 (D3 3, GA2 1, PW2 1) | 0 of 200 | 0 of 200 |
| either bar, both periods (exact 95 pct bound) | - | 5 of 200 (at most 5.7 pct) | 1 of 200 (at most 2.75 pct) | 1 of 200 (at most 2.75 pct) |
| a Sep-Dec pass passing Jan-Apr too (null; plain Jan-Apr rate) | - | SIZE 5 of 8 | SIZE 0 of 3 (13.5 pct); SIDE 1 of 9 (14.5 pct) | the same (the null by weight is unchanged) |
| SIDE caught +5; +10 (both periods) | 49; 90 pct | 55; 91 pct | 55; 91 pct | 49; 92 pct |
| SIZE caught +5; +10 (both periods) | 82; 95 pct | 85; 95 pct | 56; 90 pct | 56; 90 pct |
| real alarms labelled (of 20 codes) | - | 17 | 17 | 13 |

Notes (reviews C and D, 30 Oct): the bounds are exact (Clopper-Pearson, 95 pct two-sided; 0 of 200 is at most 1.83 pct). FAIR_SUMMARY's
both_lo and both_hi (a bootstrap over alarms) cannot see rare passes: 0 of 200 reads 0 to 0. SIZE's +5 and +10 are over all 100 plant
runs, but T18's made-up alarm never passes COUNT in Sep-Dec: over the 90 eligible runs +5 is 56 of 90 (62 pct) and +10 is 90 of 90.
"A Sep-Dec pass passing Jan-Apr too" (0 of 3, 1 of 9) is too few to judge (95 pct: 0 to 71 and 0.3 to 48 pct). Ladder v4's null and
size_plant runs equal v3's row for row (they carry their own wave ids); side_flip and side_plant are built on the real fires and changed.

Answered (review B, 30 Oct, reviews/REVIEW_B_FAIR2_20261030.md; corrected by reviews C and D): the SIZE lean of WH2, D3 and GA2 was
partly the ladder's and partly the reader's own: editions 3 to 10 averaged the real fires per 15 min wave while the random counts 30 min
grade waves (fixed by edition 11, above).
fair_v1 and fair_v2's made-up fires counted one each in waves of their own while their random is weighted per grade wave, and their own
pre-fire moments were cut from the random (null z per alarm spread 0.66 to 0.71 against side_flip's 0.29 to 0.35). Review B's fix (each
made-up fire in its real fire's wave) still leaned on WH2 (SIZE null z +1.13 / +1.80 over 10 seeds, SCOUT's VM check, not a receipt),
so fair_v3 draws by weight. SIZE +5 is caught less (56 against 85 pct): the old lean had flattered it. diag_size_lean_v1.py is not needed.
Calibration (review D, reviews/REVIEW_D_FAIR3_20261030.md; its VM checks, not receipts): FAIR_CALIB's 2 LEANS rows (T13 SIDE Sep-Dec
+0.79, T25 SIDE Jan-Apr -0.83; v4 1d0ae290f3a5e8da) are chance: about 1.2 are expected among 80 null rows (2 or more: 0.34), and fresh
seeds read +0.11 and -0.03. SIDE Sep-Dec's null P(z >= 2) is 10 of 200 (5.0 pct, against 2.3 nominal; fresh seeds 2.5 and 3.3 pct):
the lines judge the centre and the spread, not the tail; tail lines (P(z >= 1), P(z >= 2) in binomial bands) wait for the next ladder.
```
python3 -B tools/alarm_first_look/fl_read_v11.py <TARGETS_FL.tsv> ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv <out> <FLOUT receipts> ... <APROF22 receipts> ... <BUSY receipts>/BZ
python3 -B tools/alarm_first_look/fair_v4.py <TARGETS_FL.tsv> ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv <out> <seeds> <plants, e.g. 5,10> [--codes T04] [--plant-seeds N] <the same receipts dirs>
python3 -B tools/alarm_first_look/tests/test_fl_read_v11.py ; python3 -B tools/alarm_first_look/mutants_fl_read_v11.py    (editions 10, 9, 8: _v10, _v9, _v8)
python3 -B tools/alarm_first_look/tests/test_fair_v4.py ; python3 -B tools/alarm_first_look/mutants_fair_v4.py              (fair_v3, v2, v1: _v3, _v2, _v1)
```

## Commands (from team/RESEARCH)
```
python3 -B tools/alarm_first_look/fl_lists_v2.py ALARM_DESIGN tools/money_direction/inputs/<MD batch>/TARGETS.tsv tools/alarm_first_look/inputs/<batch> [--codes T04,...] [--perfire-dir <FLGRADE receipts>]
python3 -B tools/alarm_first_look/fl_jobs_v1.py <batch> plan | <P1,P2,...> [--dry]            # offer, heat, first, speed (outcome tool)
python3 -B tools/alarm_first_look/fl_grade_jobs_v1.py <G1,...> [--dry]                      # lists without a PERFIRE
python3 -B tools/alarm_first_look/fl_aprof_jobs_v3.py <batch> plan | <A1,...|CODE:T17> [--dry]   # move spent, alarm_profile 2.2, both modes
python3 -B tools/alarm_first_look/fl_read_v3.py tools/alarm_first_look/inputs/<batch>/TARGETS_FL.tsv ALARM_DESIGN QUANT/receipts/COSTS_PER_COIN_V1.tsv tools/alarm_first_look/results/<name> tools/alarm_first_look/receipts/<FLOUT job> ... tools/alarm_first_look/receipts/<APROF22 job> ...
python3 -B tools/alarm_first_look/tests/test_fl_read_v3.py ; python3 -B tools/alarm_first_look/mutants_fl_read_v3.py
```
Outputs per alarm: FL_<code>.json, FL_<code>_MONTHS.tsv, FL_<code>_WINDOWS.tsv (every month and both periods); one row per alarm id in FL_SUMMARY.tsv.

## Cleaning SCOUT's own scratch (clean_scout_scratch_v2.py; v1 failed reviews A and B; v2 PASS by both, 30 Oct)
the owner 29 Oct 14:52 Berlin: clean up after yourselves, logging the proof of what was run. Only inside a CLEAN job on the Mac
(JOB_SCOUTCLEAN_V2, queued by mk_clean_job_v2.py after the cleaner's own --dry on the VM). It removes
<SCRATCH>/<BASE>/<JOB> of SCOUT's MDOUT and FLOUT jobs only (a fixed table: base, receipts root, job type), only
when the job's proof is on dev (every stage rc 0; every extracted table whole, with the rows its extract log names), never through a
link, and writes receipts/<JOB>/CLEANED.tsv (start, then done or error) after copying the scratch's top-level logs to
receipts/<JOB>/scratch_logs/. Open SHOULDs of both reviewers (a v3): repeat the link checks just before the removal; require an extract
for every outcome; a damaged gz (zlib) as a refusal.
```
python3 -B tools/alarm_first_look/mk_clean_job_v2.py <PART> MD:<job,...> FL:<job,...> [--dry]
python3 -I -B tools/alarm_first_look/tests/test_clean_scout_scratch_v2.py ; python3 -I -B tools/alarm_first_look/mutants_clean_scout_scratch_v2.py
```

## Status
fl_read_v11 (current reader): tests 132 (tests/test_fl_read_v11.py 44af6a5724e1978d: edition 10's 127, T28 and review D's T29), planted
bugs 29 of 29 (receipts/MUTANTS_FLREAD11_20261030T205907Z.txt 74c4b5fcbb16d8a8); fair_v4 (current ladder): tests 54
(tests/test_fair_v4.py 5b923209422ca2d2: fair_v3's 43, T16 and review C's T17, T18), planted bugs 79 of 79 (review C's 10 added;
receipts/MUTANTS_FAIR4_20261030T205622Z.txt b7cc2433e5466d2b). On the Mac, job 20264600 ran the earlier test files: 130 and 45 OK.
Reviews C (PASS WITH ITEMS) and D (FAIL on one claim, fixed by edition 11) of v10 and v3: reviews/, SCOUT's answers at the top of each;
a follow-up on v11 and v4: next.
fl_read_v10 (superseded by v11): tests 127 (tests/test_fl_read_v10.py 0ef941ef9110be68: edition 9's 123 and T27), planted bugs 27 of 27 (its
4 and edition 9's 23; receipts/MUTANTS_FLREAD10_20261030T195749Z.txt 51fd769a46b15e22); fair_v3 (superseded by v4): tests 43
(tests/test_fair_v3.py 0727751190b6ef5b), planted bugs 67 of 67 (its 25, fair_v1's and fair_v2's on fair_v3: 38 as they are, 3 adapted,
12 on code fair_v3 no longer has; receipts/MUTANTS_FAIR3_20261030T195852Z.txt 3b8ab56287a89def). On the Mac, job 20264593: 127, 43 and
test_fair_v2's 31 OK (review B P1). Reviews A and B (30 Oct, reviews/) were of editions 8-9 and fair_v2; v10 and v3: reviews C and D.
fl_read_v9 (superseded): tests 123 (tests/test_fl_read_v9.py f930336a0e5071d0; review A's 6 added as T26), planted bugs in edition 9's code
23 of 23 (receipts/MUTANTS_FLREAD9_20261030T190521Z.txt); fl_read_v8: tests 112 (d15d22398c87e798), 42 of 42; fair_v2 (superseded): tests 31
(14e431016bcb8157), 12 of 12; fair_v1: tests 27 (622646ddae0cb99f), 41 of 41 (VM 30 Oct). On the Mac: job 20264507 ran test_fl_read_v8
(112) and test_fair_v1 (27); job 20264539 ran test_fl_read_v9 31d25ebbc1248587 (117) and test_fair_v2 a77a6f9ac937757d (30). Review A
(reader, 30 Oct): PASS WITH ITEMS (reviews/REVIEW_A_FL9_20261030.md); review B (the ladder): FAIL on SIZE
fairness, answered by ladder v3 (reviews/REVIEW_B_FAIR2_20261030.md).
busy_v1: tests 22 of 22, planted bugs 18 of 18 (VM and container, 30 Oct). fl_read_v7: tests 87 (edition 6's 66 + 21), planted bugs in
edition 7's code 29 of 29 (30 Oct). Both TEST, NOT REVIEWED (2 reviews to name).
fl_read_v3: tests 48 of 48; planted bugs 51 of 51 killed (v2's, reviewer C's 11 that lived on v2's tests, edition 3's own). Reviews of v2:
C FAIL (3 MUST, fixed in v3), D PASS (4 SHOULD, done in v3); v3 itself: 2 reviews to name. fl_read_v2: 28 tests, 30 of 30; fl_read_v1:
18, 19 of 19. clean_scout_scratch_v2: 19 tests, 23 of 23 (non-root). First batch FL1_20261030: 20 registry alarms with a MONTH PERFIRE;
FL2_20261030: KNOWN FDA2APR and the controls SYN0A, SYN0B, SYN10 (PERFIRE from FLGRADE G1); G2, G3 (KNOWN N1APR, LUAPR, PP2APR; DPK) to run.
