# alarm_first_look ARCHITECTURE (SCOUT, 30 Oct 2026)

```
REGISTRY -> tools/money_direction/mk_targets_v1.py -> MD lists (T01..T28, Sep 10 - Apr 30) and TARGETS.tsv
  lists with a MONTH PERFIRE ---------------------------------------------\
  lists without (KNOWN, SYN, DPK) -> fl_grade_jobs_v1.py (JOB_FLGRADE_V1):  > PERFIRE_<V>.tsv (A rows, R rows + w, race per fire)
        alarm_grade_chain_v2_1_to20260430.sh LIST mode + perfire_v1 ----/
PERFIRE -> fl_lists_v2.py (v1 + --codes, --perfire-dir) -> inputs/<batch>/A_<code>_EVENTS.tsv, R_<code>_EVENTS.tsv, R_<code>_W.tsv, TARGETS_FL.tsv
inputs -> fl_jobs_v1.py (JOB_FLOUT_V1, parts of <= 150,000 events, queues from Q_V21 down):
        event_outcomes_aw1.py run 0 + OUTCOMES_FIRSTLOOK_V1.json -> SCRATCH_DISK om_<A|R><code> -> night_export_v3.py -> X_*.tsv (SCRATCH_DISK)
        -> fl_extract_v1.py -> receipts/<job>/<A|R><code>.tsv.gz (dev)
A lists -> fl_aprof_jobs_v3.py (JOB_APROF_V3, parts of <= 60,000 fires; v1 ran edition 2, v2 ran the withdrawn 2.1):
        tools/alarm_profile_v2/alarm_profile_v2_2.py build twice (subject G_<code>: run end in the fire's last 60 s; subject H_<code>, mode
        hour: the hour's extreme; own out roots on SCRATCH_DISK) -> export with the list -> receipts/<job>/AP_<code>.tsv and APH_<code>.tsv (dev)
A and R lists -> busy_v1.py build (one job; alarm_profile 2.2's LabSource prices, episode_blocks Ep.normal unchanged) -> receipts/<job>/BZ/
        BZ_<A|R>_<code>.tsv.gz + BUSY_V1.json; busy_v1.py prove (fires vs AP_<code>.tsv) -> receipts/<job>/PROVE_BZ.tsv
receipts (+ <BUSY job>/BZ) -> fl_read_v11.py (= v10 + the grade's 30 min waves from labcore; v10 = v9 + Look's wave ids; v9 = v8 +
        edition 9; v8 = v7 + two bars; imports md_v1.py and labcore/waves.py) ->
        results/<name>/FL_SUMMARY.tsv, FL_RULE30.tsv and FL_RULE7.tsv (beside), FL_RULE8.tsv (two bars, z 2 both periods),
        FL_RULE9.tsv (the rule: Jan-Apr confirms at z 1), FL_<code>*.{json,tsv}
the same receipts -> fair_v4.py (= fair_v3 on fl_read_v11) -> results/<name>/FAIR_RUNS.tsv, FAIR_SUMMARY.tsv, FAIR_CALIB.tsv,
        FAIR_V4.json (the bars on made-up alarms; fair_v3, fair_v2 and fair_v1 beside)
A and R lists + lab3 (C13.S05, X1.COST.S06, S08, S10, S11) -> bar_v1.py build -> receipts/<job>/BAR/BAR_<A|R>_<code>.tsv.gz + BAR_V1.json (edition 12's B per moment)
BAR_V1.json + BAR tables -> fl_read_v12.bars_of / load_bar (digest, edition, settings, counts, bar_v1.row_fault; refused before a verdict) -> reader and fair_v5
the same receipts + BAR -> fl_read_v12.py (runs fl_read_v11 unchanged, then SIZE at B through size_view into edition 11's match7 and bar8; hit_b reads the stored BEST columns) -> also FL_RULE12.tsv, FL_<code>_RULE12.tsv, FL_RULE12_UNKNOWN.tsv, FL_RULE12_SUPPORT.tsv, FL12.json
the same + BAR -> fair_v5.py (imports fair_v4 unchanged; SIZE at B on each made-up row's own bar; --seed-base) -> FAIR_RUNS, FAIR_SUMMARY, FAIR_CALIB, FAIR_V5.json; check_fl12_v1.py: real-data checks inside the job
SCRATCH_DISK scratch of the outcome jobs -> clean_scout_scratch_v2.py inside JOB_SCOUTCLEAN_V2 (mk_clean_job_v2.py) after the proof is on dev
(next) registry pages and the process step (PROCESS_V7)
```
- No new price or outcome code: every label is event_outcomes_aw1's (settings checked by its own load_settings), the random is
  make_random_v3's, the races are the grade's, the move spent is alarm_profile's (edition 2 = edition 1's code, byte for byte, plus the
  generic subject). fl_read_v2.py only averages, weights, joins and compares.
- The move spent joins to the fires by (coin, t); a fire without a row, a row without a fire, or a (coin, t) twice: that move is NOT RUN
  for that alarm (the rest of the look stands), with the counts written in FL_<code>.json. The reader checks every input against
  TARGETS_FL's sha16s and the tables against their lists before it computes anything (refused otherwise).
- Pins in every job: event_outcomes_aw1, night_export_v3, fl_extract_v1, the settings, TARGETS_FL, every list, lab3 law.py and days.py;
  FLGRADE: the chain, perfire_v1 and its test, every list; APROF: alarm_profile_v2.py, episode_blocks.py, EPI_CATALOG_V1.tsv,
  RELEASE_profile_V2_0.json, TARGETS_FL and every list.
- May never read: lists stop before 1 May 2026; the outcome window ends 30 Apr (later bars EMBARGO_SUPPORT); the profile build stops
  30 Apr; fl_extract and the readers refuse a time at or after 1 May.
- Scale: about 16 ms an event on the Mac for this settings file (3 h paths, 40 labels, both sides); alarm_profile about 1.5 min a list
  of 15,000 to 48,000 fires (231 days built once per list); one process a job, nice 10, so the shared Mac is never held.
- Edition 7's busyness: the normal move is alarm_profile's own (busy_v1 reuses Ep.normal and its prices; PROVE_BZ checks it equals the AP
  files on every fire); the last hour's range and the last 15 min move are busy_v1's (Ep.closes on a 1 min grid, cut at the moment).
- Waves: PERFIRE's and the random's weights are the grade's (labcore's waves, 1,800 s; make_random_v3); edition 11's fires use the same
  function and gap (one definition; the owner 30 Oct 21:11 Berlin "30 minutes"). Editions 3 to 10 used md_v1's 900 s waves.
- Editions 8 and 9: one bar function (bar8) for both bars (SIZE from match7, SIDE from side8); edition 9's periods and z lines are in
  PERIODS9, read by the reader and the ladder (RULE_8 keeps edition 8's periods, typed in run_code, z 2 both); RULE_8 and RULE_9 are
  written by one writer; RULE_9's month table is FL_<code>_RULE8.tsv (the months do not depend on the z line).
- Edition 10 adds only Look's wid (the fires' wave ids; default md_v1's waves): its tables are edition 9's byte for byte (job 20264593).
- Ladder v3's null (review B): each random moment with a cost and a weight, not a real fire's pre-fire moment, is a made-up fire with
  probability min(w, PI_MAX = 0.5) (null_p, null_rows), each its own wave (wid); the rest is its random, weighted w / (1 - p) (made_up).
  FAIR_CALIB judges the null itself (calib); fair_v1 and fair_v2's candidates and draw are gone from fair_v3.
- Open (review A, 30 Oct; for the next reader edition): three quantities still have two computations: the SIDE mean, error and z (side8 + stats7 and
  Look.net_test), waves_1h (counts8 and month_test), STEADY/BROAD/COUNT (bar8 and verdict7's own copy). They agree on fixtures and on
  every real alarm (0 differences, review A); the next edition keeps one path for each, proven by equal table sha16s. Also
  fair_v4.wave_share, a copy of stats7's per-wave mean (review C).
- The ladder admits its inputs through the reader's own checks (check_inputs, load_w, busy_of, the finished-job rule); it writes only its
  four files (FAIR_RUNS, FAIR_SUMMARY, FAIR_CALIB, FAIR_V<n>.json; fair_v1 and fair_v2 wrote three) into a new folder (.part, then renamed); every draw is seeded by (seed, code, kind, plant).
