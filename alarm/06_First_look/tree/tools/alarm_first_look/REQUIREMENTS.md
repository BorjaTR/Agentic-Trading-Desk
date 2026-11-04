# alarm_first_look REQUIREMENTS (SCOUT, 30 Oct 2026). fl_read_v3: tests/test_fl_read_v3.py (48); planted bugs mutants_fl_read_v3.py (51 of 51).
# (fl_read_v2: test_fl_read_v2.py 28, mutants 30 of 30; F1-F20 hold in v3, rerun by its tests; F18's 'twice refused' became 'twice: move NOT RUN'.)
(fl_read_v1: tests/test_fl_read_v1.py 18, mutants_fl_read_v1.py 19 of 19; F1-F14 are the same code in both.)

| id | requirement | test |
|---|---|---|
| F1 | random = weighted mean (make_random_v3 weights) over the same month's R rows; weighted median | T01Basics.test_weighted, test_edge_is_above_the_months_random |
| F2 | waves 900 s, a wave's month and day = its first fire's | T02Month.test_wave_month_is_its_first_fire (md_v1 tests for the waves) |
| F3 | levels in c = cost_bp/100 + 0.032, each coin its own c | test_one_hour_window_and_own_cost |
| F4 | month holds: median per-wave offer at 1 h >= 4c AND (edge vs random >= 2c OR offer-first share > random) | test_offer_boundary, test_edge_boundary_and_first |
| F5 | PASS: >= 3 of 4 design months hold | test_three_of_four |
| F6 | top 2 coins, top 5 waves, best 5 days each strictly under half of the design edge | test_two_coins_under_half, test_exact_half_is_not_under_half, test_top5_waves_and_days |
| F7 | >= 30 waves in every design month | test_thirty_waves |
| F8 | FOLLOW lean reads __FOLLOW | test_lean_follow_reads_follow |
| F9 | without DASH, VVV, ZEC; without the top 5 waves | test_without_top5_and_excluded_coins |
| F10 | race and LEAD from PERFIRE: LEAD = (lean a - r) - (other a - r) | T04Race.test_lead |
| F11 | speed: offer = own side's REACH4, heat = the other side's REACH4 | T05Reported.test_speed_sides |
| F12 | money beside: market g - c; waiting only if WORST_1M > 0 | test_money_and_counts |
| F13 | May refused | test_may_refused; fl_extract_v1 refusals |
| F14 | jobs: no forbidden word, bash -n, every input pinned | fl_jobs_v1.py, fl_grade_jobs_v1.py and fl_aprof_jobs_v1.py asserts |
| F15 | move spent in the fire coin's own c (run, giveback, normal move); minutes as they are | T06Move.test_in_c_and_median_over_waves, test_own_cost |
| F16 | move spent: each wave once (mean of its fires with a known value), then the median over waves; not known never counted; capped share | test_each_wave_once, test_not_known_and_capped |
| F17 | move spent by period and month (design apart from forward); none without an AP file | test_periods_apart_and_no_ap; T08 |
| F18 | the AP rows join the fires by (coin, t), not by order; a (coin, t) twice or a missing column refused; a fire without a row or a row without a fire: move NOT RUN with the counts, the rest of the look unchanged | T07Join, test_misaligned_refused, T08 |
| F19 | the random's median offer at 1 h printed beside rule 1; the rule itself unchanged | test_random_offer_beside_rule_1, T08 |
| F20 | main finds AP_<code>.tsv in the receipts folders given (one per code) and writes the move columns in FL_SUMMARY and FL_<code>_MONTHS | T08EndToEnd |
| F21 | v3: rule 1 is the median over waves (a wave of several fires counts once at its mean), not over fires | T09RulePinned.test_rule1_median_over_waves_not_fires |
| F22 | v3: the random is weighted (unequal weights change it); the weighted median uses the weights; the weights file is used | test_weighted_mean_and_median_with_unequal_weights, test_weights_change_the_random |
| F23 | v3: a month holds only when rule 1 AND rule 2 hold; the 30-waves rule counts design months only; the edge is a mean over waves | test_month_needs_both_rules, test_forward_months_outside_the_count, test_edge_is_a_mean_over_waves |
| F24 | v3: the excluded coins leave the random too; the race uses its weights; speed is per wave; a coin's share of the edge is split across its wave's fires | test_excluded_coins_leave_the_random_too, test_race_uses_its_weights, test_speed_per_wave, test_coin_share_split_across_its_wave |
| F25 | v3: PUSH / NO PUSH from the median run (normal moves, per wave, design); both AP kinds (push at the fire, hour's peak) | T10Beside.test_push_flag, test_two_ap_kinds |
| F26 | v3: the random moments in the hour before a same-coin fire, and the result without them; the random's coverage of the grade's waves; fires dropped (no cost, no 1 h) | test_prefire_mask, test_drop_R_leaves_the_random, test_coverage_and_counts |
| F27 | v3: refused: weights not one to one; a list, weights or table not TARGETS_FL's or not its list; c not the outcome tool's; race NOT RUN with its reason; an AP twice stops only the move | T11Inputs, T12EndToEnd.test_refusals, test_race_not_run_says_why, test_an_ap_row_twice_stops_the_move, test_a_bad_ap_file_stops_only_the_move |
| F28 | v3: every item by month: windows, speeds, shares, the three 'without' results, for each month and both periods | T12EndToEnd.test_full_run |

Cleaner (clean_scout_scratch_v2.py; tests/test_clean_scout_scratch_v2.py 19; mutants_clean_scout_scratch_v2.py 22 of 22, 23 when not root):

| id | requirement | test |
|---|---|---|
| K1 | removes only <WDB>/judge_scratch/<BASE>/<JOB>; the base stays; logs kept; CLEANED.tsv start then done, with the real path, files, bytes | T01Good.test_dry_then_apply, test_md_job |
| K2 | never through a link: judge_scratch, BASE, the job folder, the receipts folder and STAGES.tsv must be real; a link inside the job never followed | T02Links (all), test_links_inside_not_followed |
| K3 | BASE, receipts root and job type tied by a fixed table; whole-name match (no newline, '..', '/'); FLGRADE and APROF refused | T03Names.test_type_and_base_tied |
| K4 | a job named twice, or any job refused: nothing removed at all | test_twice_and_usage, test_one_bad_job_removes_nothing |
| K5 | proof on dev: every stage rc 0 and an end 0; at least one extract; each extract's file real, whole (gzip to its end) and with the rows its log names, in this job's folder | T04Proof (all) |
| K6 | CLEANED.tsv or scratch_logs present (even a dangling link): refused; receipts not writable: refused | test_dangling_cleaned_link, test_receipts_not_writable |
| K7 | scratch and receipts never nested | test_scratch_and_receipts_nest |
| K8 | an error in one job is written (start, error), the scratch stays, the next job goes on, exit 1 | T05Failure |
| K9 | the job file: the cleaner pinned, run with -I -B, the worst rc ends the job; every name and PART checked; the dry look first | mk_clean_job_v2.py asserts |

Editions 8 to 11 (fl_read_v8.py to fl_read_v11.py; tests/test_fl_read_v9.py 123: edition 8's 112, T24, T25 and T26;
tests/test_fl_read_v11.py 132 adds T27, T28 and T29):

| id | requirement | test |
|---|---|---|
| E1 | SIZE bar = edition 7's MOVES verdict (same pass, z, points; label SIZE) | T20Rule8.test_size_bar_is_edition_7 |
| E2 | SIDE bar per fire = lean race at 1 h minus its wave month's random, pre-fire moments out; equals Look.net_test; fires without a cost out; the 1 h race only | T20.test_side_bar_is_net_test, T22.test_side_* |
| E3 | each bar: STEADY (3 of 4 months, THIN under 10 waves, z line), BROAD (top 2 coins, best 5 days), COUNT (30 waves with a 1 h value, the counts given); the limits: z on the line passes, 10 waves are not THIN, 30 waves count; a FOLLOW lean reads FOLLOW | T20, T22, T26Rule9Limits |
| E4 | RULE label: SIZE+SIDE, SIZE, SIDE, NEEDS MORE MONTHS (<bars passing Sep-Dec>), NOT PASS; SIZE NOT RUN without BZ | T20.test_overall8, test_size_not_run_without_bz |
| E5 | FL_RULE8, FL_<code>_RULE8 and FL_RULE9 hold the JSON's verdicts; a code without tables gets a NOT RUN row with every column | T21, T23, T25 |
| E6 | edition 9: Sep-Dec z >= 2, Jan-Apr z >= 1 (PERIODS9); Jan-Apr keeps 3 of 4 months, THIN, BROAD and COUNT; the z line reaches both bars; FL_RULE8 byte for byte edition 8's | T24Rule9, T25Rule9Run, T26Rule9Limits |
| E8 | edition 11: the fires' waves are labcore's waves with a 30 min gap (the grade's; no copy): 20 min apart one wave, a gap of exactly 30 min one wave, 30 min and 1 s two; given ids still win | T28GradeWaves (tests/test_fl_read_v11.py) |
| E7 | edition 10: Look's wid: default md_v1's waves (every table edition 9's, job 20264593); given ids are the bars' unit; a wave's month and day its first fire's; misaligned or negative ids refused | T27WaveIds (tests/test_fl_read_v10.py) |
| E9 | review D (30 Oct): a no-edge alarm whose 3-fire grade waves win and whose lone fires lose, its random weighing each grade wave 1, reads 0 on the grade's waves and +50 pts on 15 min waves (the fires need the random's unit) | T29UnitWorld (tests/test_fl_read_v11.py) |

The ladder (fair_v1.py, fair_v2.py; tests/test_fair_v2.py 31: fair_v1's 27 and T10, T11):

| id | requirement | test |
|---|---|---|
| L1 | null: per fire one random moment (same coin, 7 days, hour of day 1 h on the circle, not pre-fire, never twice); the rest is its random; pre-fire moments (the real alarm's and its own) out | T01Candidates, T02MadeUp, T08.test_prefire_*, test_made_up_fires_own_prefire_moments_out |
| L2 | side_flip: whole UTC days flipped, fires and random by coins apart, the 1 h race; the bar reads the flipped random | T03Coins, T08.test_side_flip_*, test_flip_and_plant_read_the_flipped_random |
| L3 | plants: lost races turned won with D / (100 s); misses turned into 4c moves with D / (100 (1 - h)), h over busy fires; hits and ties kept; the null unchanged; built on the seed's flip and null | T04Plants, T08.test_side_plant_with_many_ties, test_size_plant_*, test_plants_are_built_on_their_seeds_flip_and_null |
| L4 | the made-up alarm reads its own COUNT; summary: NOT RUN is no run; rates by period and both; EITHER needs one bar in both periods; each row's z line | T08.test_null_reads_its_own_count, T06Summary, test_rates_by_period, T10ZLines, T11FilesZ |
| L5 | refusals (unfinished job, existing out, settings, unknown code) and no half-written output | T07Files.test_refusals, T09FilesPlanted |

fair_v3.py (tests/test_fair_v3.py 43: fair_v2's with the null's tests rewritten, and T12-T15); L1 is fair_v1 and fair_v2's null;
fair_v4.py = fair_v3 on edition 11 (tests/test_fair_v4.py 54: fair_v3's 43, T16: on edition 11, the real rows read 30 min waves, and
review C's T17, T18):

| id | requirement | test |
|---|---|---|
| L6 | the null by weight: p = min(w, 0.5), 0 for a real pre-fire moment or one without a cost or a weight; each moment drawn with p, in order, seeded; each made-up fire its own wave; the rest weighted w / (1 - p); its own pre-fire moments stay in; against unequal waves it reads 0 where drawn alike it reads +50 pts | T01NullRows, T02MadeUp, T08.test_made_up_fires_own_prefire_moments_stay_in, T12NullWeights |
| L7 | plants sized by wave, as the bar weights | T12.test_plants_sized_by_wave, T08.test_size_plant_sized_on_busy_fires |
| L8 | FAIR_CALIB: per code mean, sd, z shares, LEANS over 3 errors; ALL CALIBRATED at |mean z| <= 0.2, sd within 0.8 to 1.25, spread <= 1.3 times its noise, 5 alarms or more; null and side_flip only | T13Calib |
| L9 | summary: Jan-Apr given Sep-Dec; the both-period rate's interval over alarms (codes resampled, seeded); EITHER rates; files: FAIR_CALIB, the waves column, FAIR_V3.json | T14SummaryV3, T15FilesV3 |
| L10 | the reporting (review C): the interval of the both-period passes at 2.5 and 97.5 pct; EITHER's Jan-Apr given Sep-Dec over its both-period passes; the sd within alarms the root of their mean variance; P(z >= 2) counts a z of exactly 2, per alarm and for ALL; LEANS over 3 errors, not 2; ALL's runs and mean over all runs; no pre-fire cut of its own (5 min); FAIR_V4.json's share over the moments that can be drawn | T17ReviewC, T18ReviewCFiles |

## Edition 12 (SCOUT, 2 Nov 2026; plans/PLAN_FL12_PERCOIN_BAR_20261102.md). tests/test_fl12_v1.py 65; mutants_fl12_v1.py 73 of 73; job 20266502.
| id | requirement | test |
|---|---|---|
| N1 | B = max(6 x dated cost, own line); either unknown: unknown, with its reason | T01Bar |
| N2 | the line: 87th pct of hourly peaks, pct of price, 14 days, at least 303, equal to moment_v1's definitions | T01Bar, moment cross-check; real: check_fl12_v1 bars, 60 of 60 |
| N3 | look-ahead: the moment's own minute, any later minute, a window ending exactly at t change nothing; a past window does | T02LookAhead |
| N4 | the cost is the moment's own hour and day cell | T02.test_cost_hour_cell_of_the_moment |
| N5 | hit over and under its dated B; unknown bar or path stays unknown; a crossing seen before a gap counts; a miss needs both BEST_60M; no window over 60 | T03Hit |
| N6 | unknown never a miss, fire or random; each random its own B; thin month cannot hold, COUNT untouched | T04Reader |
| N7 | edition 11's tables byte equal; SIDE columns guarded; refused runs publish nothing | T05Files; real: same_fl1, same_fl2 |
| N8 | counts: unknown by reason, and the all, busy, known, matched funnel by fires and waves | T05.test_unknown_table_counts, test_support_funnel |
| N9 | the ladder: SIDE rows equal fair_v4; each made-up row keeps its own bar; seed base moves draws; exact bounds | T06Ladder; real: side_rows |

Edition 12, added 2 Nov 2026 (GPT 10:30:53Z): a threshold table is admitted only with its manifest's digest, edition and settings, consistent rows and counts; else refused before a verdict, in reader and ladder. Every RULE_12 row keeps RULE_9 beside; labels are retrospective.
