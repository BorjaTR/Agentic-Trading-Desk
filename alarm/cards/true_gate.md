# true_gate: tool card
Is the claim of an alarm true on a stored metric it does not read, against equally busy moments, and in its direction? Released in ALARM_V1_20_3 (ALARM_V1_20, _1 and _2 stay held, never current: GPT found faults in the first two, fixed here; _2 had a broken test); ALARM_V1_21 adds its queue kind TRUE (queue_job_v15); step 5c of AGENTS.md's loop. Print-only: the word changes no decide_v4 state. Sep-Dec 2025 only: last after 20251231 is refused; Jan-Feb 2026 gets one look, on the owner's word, in a new edition. NOT BLIND: the rule and its known-case sorting were fixed on Sep-Dec after seeing earlier rounds; no blind check has run. X1 source families are guesses (status GUESS in SOURCE_FAMILIES_V1.tsv, 155 codes). TEST, NOT REVIEWED until a reviewer says so.

## Run it (in a runner job; S = `--settings` is not taken: the claim names the lab days)
```
$PY -B 03_Grading/tree/tools/true_gate/true_gate_v3.py check <claim.json>
$PY -B 03_Grading/tree/tools/true_gate/true_gate_v3.py run <claim.json> <out dir (new)>
$PY -B 03_Grading/tree/tools/true_gate/true_gate_v3.py fp <claim.json> <out.tsv (new)> <sets> <rows|waves>
```
The claim: 03_Grading/tree/tools/true_gate/CLAIM_TEMPLATE.json. activity.code must be the label's code: `check` (admit) refuses otherwise with `REFUSED BAD_CLAIM` (ALARM_V1_21_4). def and def_sha16 are required, the VARIANTS row's; idea and V name the variant; the PERFIRE must be named PERFIRE_<V>.tsv. Event dates must be real, 20250910 to 20251231; the activity history alone reads up to 14 days before an event. The PERFIRE is the GRADE job's (FIRES.tsv names its folder; DSK sweeps it: run soon after the GRADE). bz_a and bz_r may name stored busy tables; with none, `run` builds them with busy_v2 inside the out dir. Queue it as KIND TRUE: `queue_job_v15.py S <RUN> TRUE <IDEA> <V>=ideas/<IDEA>/TRUE_<V>_<LABEL>.json --from-job <NUM>_GRADE_<IDEA>` (JOB_TRUE_V1; cards/queue_job_v15.md; ALARM_V1_21; `--from-job` takes the GRADE job's receipts folder name, `<NUM>_GRADE_<IDEA>` (e.g. `20267780_GRADE_WINDFALL`), not a bare job number; use the full GRADE receipts folder name even after the job finishes): never write the job by hand, its twin would have no RUNS row (audit A16).

## The label (kind metric_test; label formats in true_gate_v1.py's docstring)
code or code_by_side; when window (t + start_s, t + end_s] or present (t - end_s, t]; agg sum, mean, max, min, last; test >=, <=, falling, rising; change abs or pct; thr, thr_code (read as of t, known_at <= t) or thr_input; sign none, same, opposite; max_age_s required. Stale, missing, with a reason, or known after t in a present label: NOT KNOWN (NaN), never false. The mirror reads the same code the other way.

## The word
Under half of the claim's known fires matched on both claim and mirror prints UNSURE, whatever the numbers; the card prints claim known, mirror known, jointly known, matched on both, paired waves. TRUE: gap >= +0.05, its interval above 0, claim minus mirror >= +0.05, its interval above 0. NOT SUPPORTED: the top of either interval under +0.05. Otherwise UNSURE. The gap is the share of fires hitting the label minus equally busy random moments' share (fl_read_v11's band pairs, inside groups of the coin's own activity percentile, 14 days before the day, known at t; a fire with no two-value cell is priced on the normal-move band alone and counted), one value per wave (1800 s), wave bootstrap widened by the random moments' error. Every month and ex 10-11 Oct are printed. The luck line (flip p) is uncalibrated and never decides. Flow removed is printed only.

## Refusals (exit 2, `REFUSED <CODE>: why`)
BAD_MIRROR (not the exact opposite: code, window, agg, change, sign, age equal; falling with rising at one threshold, <= with >= at opposite thresholds), SAME_CODE, SAME_FAMILY (the label or mirror reads the trigger's code or source family), PRICE_DERIVED, UNKNOWN_SOURCE (no card or no rule: A6, COIN_C1, COIN_C1B, LAB, PCT24, PCTX, Y3; an event list with no events_family), UNKNOWN_OP, BAD_LABEL, BAD_CLAIM, MONTHS, DEF_CHANGED, PERFIRE_CHANGED, OUT_EXISTS.

## What you get
TRUE_CARD.txt (the word, gaps, coverage by group, months), TRUE_ROW.tsv (one row: dictionaries/true_gate_COLUMNS.tsv; it binds idea, V, def_sha16, perfire_sha16, label, mirror, card) and TRUE_ROW.sha16. audit_run_v4 A18 reads them: a decision from 2026-11-02T23:00:00Z on with no intact row, with another variant's PERFIRE, a required seal gone, or a label not the one on its sealed card (`check` prints the true_label and true_mirror line for it) is FINISHED NO, exit 3; a job from before the seal prints UNVERIFIED. Any word finishes.

## What was measured (playground, jobs named; Sep-Dec, not blind)
Known cases, J20267058: 10 of 12 as fixed before the run; all 7 cases that test the gate right (the bias case, FDA2APR big opening; 4 controls with no closing claim; 2 circular refusals); 3 of 5 mechanism words right (FB5 expected UNSURE read NOT SUPPORTED; LF2 expected TRUE read UNSURE). False positives, 400 random sets per label, J20267064 and J20267068: at most 0.020 read TRUE. FDA2APR: closing TRUE +0.145, big closing TRUE +0.300, big opening NOT SUPPORTED. FDAOI, exploratory, J20267157 (its PERFIRE built by that job from the kit's draw, coin costs taken from FDA2APR's PERFIRE, no recorded per-coin cost join): closing TRUE +0.156, big closing TRUE +0.309, big opening NOT SUPPORTED.

## Weak points, known
1. For falling and rising the mirror is close to the complement, so claim minus mirror is about 2 x the gap and adds no check; only thresholded labels test direction.
2. Busy fires move open interest both ways: FDA2APR big opening reads gap +0.093; only the direction test stops it.
3. Most fires are priced on the normal-move band alone: coverage came at the cost of a looser match.
4. Intervals run narrow on random sets: the lower bound is above 0 in up to 17 pct of one set against a nominal 2.5 (an interval edge, not a TRUE rate; TRUE stayed at most 0.020); the +0.05 bars do the work.
5. False positives measure noise, not selection. A liquidation trigger lowers Binance open interest by itself: read flow removed.
6. A18 checks the row exists and binds, not that the label fits the claim: the label stays the author's choice, sealed on the card. The queue kind TRUE (queue_job_v15, ALARM_V1_21) refuses a claim whose label digests are not on the card.
