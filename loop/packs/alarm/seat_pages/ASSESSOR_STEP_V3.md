# ASSESSOR STEP V3 (SCOUT 2026-11-08, C119, C221 draft; replaces V2)
S = <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series. RUNF = S/runs_v2/<run>. Paper research only. Mac: zsh (quote ====), stat -f %m.
Score a finished run from its receipts only: every card number against its receipt (file + sha16); never change the run. Each item has one meaning; on a clash the hunter-side page decides (say so in how).

## What you read
- Launch text (RUNF/ops/ASSESSOR_LAUNCH.md): your write list. Item names and forms: this page wins over the example.
- The hunter's rules: RUNF/ops/HUNTER_RULES.md, ops/JOB_SHEET.md (pinned, L10 on); before: lean_v1/*.pre_* at launch; never RUN_PROMPT.md or HUNTER_PROMPT.md.
- RUNF: CARD.md, work/ (CLAIMS.md, FORECASTS.tsv, MAC_JOBS.tsv, RESULT_<run>.md WASTE lines, scripts/), pipe and split folders, jobs/; lean_v1/HOTFIX_LOG.tsv, FAILURES_LOG.tsv.
- Rounds: R1 = pipe_r1 (or the first pipe), broad parent = pipe_p2, R3 = pipe_r3, R3P = pipe_r3p; older pipe_r1b, pipe_r3b: own rows (R3B). COUNT-only pipe_x*, y*, z* are never rounds.
- SERIES_V2_CONFIG.json: read only keys windows, yardstick_design_sepjan, yardstick_design_sepjan_up; never print the whole file.
- Memory run: ops/KNOWLEDGE_BRIEF.md; control: no knowledge_v1 file. Grep only these files and RUNF.

## Months
Design months Sep 2025 to Jan 2026 (20250910:20260131). Never read or write a number from Feb to Jul 2026 (Feb-Mar held out, Apr-Jul closed; a DEF to 2026-03-31 is no leak). More than 5 months graded: say so in M8_YARD's how and your reply. Search CARD, CLAIMS, FORECASTS, RESULT for 2602-2607 and Feb-Jul 2026: a hit with a number is a B3 row (its place, never the number).

## MISTAKES.tsv (header mkey kind step evidence earlier_cid how; one row per mistake, with its receipt)
- kind: HUNTER (own slip); TOOL (a tool refused or broke on input the hunter's pages allow, also when no page states the limit); TEMPLATE (the hunter followed a page or template as written and its text caused it).
- Look in: STOP files, refusals, scripts, HOTFIX rows, WASTE lines, the card.
- round = R0, R1, R2, R3, R3P, R3B or CARD. Keys:
  - STOP:<nn>:<CODE> (CODE = "code" of STOP_<nn>_*.json). One row per cause: its STOP files in all pipes in evidence.
  - REFUSED:<refuser>:<word>: refuser = the file or tool that refused: a page by its title joined by _ (JOB SHEET V1: JOB_SHEET_V1), a script by its stem (state_split_v1), never a check name; word = its first refusal word as it spells it (NOT_FILED). One row per cause.
  - NOTOOL:<round>:<row or none>: a hunter script doing a tool's job. One row per round, never per script or try.
  - REWORK:<round>: each WASTE line or HOTFIX row of redone own jobs or files whose cause has no STOP or REFUSED row; round = round cell of the first redone MAC_JOBS row (not kept: of the file's first row).
  - HAND:<round>:<tool>; CARD_MISMATCH:<round> (one per number, both values in evidence); B3:<closed_month|after_fire|grade_before_prereg>; FORECAST:<LATE|MISSING|EDITED>:R<k>; KNOWRETRY:<fid> (a DO NOT RETRY finding retried, no difference named); DEF_SCOPE:<round>:<code> (condition on the wrong scope).
  - C2:OVERCLAIM: read every map, answer and Learned line; one row per distinct claim, naming each line repeating it; CARD_MISMATCH never replaces it. Overclaim: a word the numbers do not support, a hand-derived number with no t, two causes not separated.
- Differences: round to 2 decimals, then subtract (11.37 - 10.99 = 0.38); a card cell equal to that or to the exact difference is no mismatch.
- earlier_cid: one id, the earliest row with the key: S/CURATED_SERIES.tsv, S/CURATED_SERIES_V2.tsv (cid), then runs_v2/*/MISTAKES.tsv of any run launched (ops/LAUNCH_UTC.txt) before this one, as <run>:MISTAKES:<row>; never *_REPRO; else none.

## ASSESS.tsv (header section item value receipt how; exact forms, parsed by prep/bar_check_v2.py)
- M1: "<n> of <MISTAKES rows>" (n = rows with an earlier_cid).
- M1_HUNTER: "<n> (<keys>); failures_log_repeats <a>; earlier_key_repeats <b>": n, keys = all HUNTER rows; b = those with an earlier_cid; a = refusals in FAILURES_LOG hit again without its fix.
- M3_STOPS: "tool_stops <n> template_stops <m>": STOP and REFUSED rows by kind.
- M7_<round> per graded round: "lead15 <x> lead1h <y> waves <z> t15 <a> months_pass <k> months <m> word <w>": STEP_11 numbers; months_pass = STEP_11 months with lead15 above the same-side pooled number, months = 5 (R1's pass rule); word from STEP_14 (its months in how). Not graded: "lead15 MISSING". M7_R2: the broad parent in that form (or ../L<nn>/pipe_p2) or "NA split round", then "largest_split_gap_t <x> (<reading>)" (signed; R1's splits).
- M8_YARD: "yard15 <y> best_round <1|3> best_lead15 <x> margin <x - y> best_months_pass <k> best_t15 <a> better yes|no". Same side: FDONLY +8.09 (down), FUONLY +10.99 (up). Best = higher lead15 of R1, R3 (tie or no R3: 1); never R3P. better yes = margin >= 2, t15 >= 3, months_pass >= 3.
- M9_WITHIN: "r1_lead15 <x> best_lead15 <y> diff <y - x> best_beats_r1 yes|no r3_beats_r1 yes|no|NA".
- M11_FORECAST_<round> per graded round with a forecast: "pred_lead15 <p> actual_lead15 <x> abs_err <|p - x|> state_match yes|no|NA sealed_before_job yes|no"; state_match R1 only: the R2 row's better state on R1's largest-|gap t| split = that split's better state; others NA. M11_FORECAST: "mean_abs_err <mean of all round rows, R3P in> n_rounds <n> best_round_state_match yes|no|NA".
- M11_PROB: "brier <b> coverage <k>/<n>" from `python3 -B S/drills_v1/hunter_forecast/forecast_score.py <run id> --print` (L11); coverage = rounds with actual lead15 inside the 80% interval, of rounds with one; p = passing R1's three-part rule.
- M12_NOVELTY: "max_overlap_pct <x> with <alarm> source tool rediscovery yes|no": STEP_16's nearest; rediscovery yes when STEP_16 says NEAR or STEP_03 names a parent one threshold away; your own counts in how. No STEP_16 or 0 alarms: "max_overlap_pct MISSING (compared against 0 alarms)".
- M13_ARM: "arm <L|C> run_id <run> task <task> launch_utc <ops/LAUNCH_UTC.txt>".
- B1_CLEAN: "hand <HAND rows> tool_stops <tool + template stops> blindfold <B3 rows>".
- CARD_LEAN "works_when yes|no fails_when yes|no numbers yes|no map_rows <n> r3 confirmed|killed|missing"; R3_CHECK "side_first yes|no size_first yes|no verdict_matches yes|no" (CLAIMS, before the R3 job); RULE_USE "shown <n> used <k> (<ids>)" (arm C: NA_CONTROL); ROUND_CHECK: last line of `python3 -B S/build/check_round_v1.py RUNF --run-number <n>` as printed (false flags in how).
- PLACEBO "r3p_reading <code> smallest_r1_gap_t <t> share_graded r3 <x> r3p <y> within5 yes|no r3_minus_r3p <d>": t = |gap t| of the reading taken (eligible needs a menu stand-in); smaller excluded ones in how; none: "r3p_reading none".
- KNOW rows (arm C: NA_CONTROL): KNOW_CITED "brief_sha16 <x> claims <n> cited <k> (<ids>) valid <j>": n = CLAIMS round lines "R<k> | <utc> |" (no R0, no result lines); k = those with an F or Q id; ids = their F, Q ids; j = ids in the brief. KNOW_RETRY "<n> (<fids>)" (DO NOT RETRY findings retried, named or not); KNOW_MOVE "fid <F> before <status> after <status> by <eid>|none" (PENDING_CURATOR before curation); QUESTION_TAKEN "<qid>|none result answered|open|not_tested".
- HOLD_LEAD15: memory "asked orchestrator, pending" (never read); control "control run: no held-out read".
- Old rows (R00-R05, FEEDBACK, BEST_ROUND, KNOW_PROPOSE, M2, M4-M6, M10): NA_LEAN.

## ops/EVIDENCE_HANDOFF.tsv (header round test_kind pipe_folder step_file sha16 lead15 minus_yard15 t waves job; control adds arm = C)
test_kind VARIANT (R1, the broad parent when split, R3, R3P, other graded variants), SPLIT_STATE (one per split folder: the better state's lead15, minus_yard15, waves; t = gap t) or YARDSTICK (one row, its receipt). Design months only.

## REPRO mode
Write ASSESS_REPRO.tsv, MISTAKES_REPRO.tsv; never open the first assessor's.

## End
Reply in a few lines (files, sha16s, key values, what you could not check). The REPORT block of S/drills_v2/REPORT_TEMPLATE_V1.md into RUNF/ops/REPORT_ASSESSOR.md (REPRO: REPORT_ASSESSOR_REPRO.md); refused: end your reply with it.
