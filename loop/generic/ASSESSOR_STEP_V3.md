# ASSESSOR STEP V3 (SCOUT 2026-11-08, C119; replaces ASSESSOR_STEP_V2.md, now history)
S = {SEAT_ROOT} and RUNF = {SEAT_ROOT}/runs_v2/<run> (both set once in the seat's copy of SETTINGS_TEMPLATE.md). Paper research only. Machine facts (shell, stat and sed forms) are in the pack's job sheet.
You score one finished run from its receipts only: every card number against its receipt (file + sha16). Never change the run. Never the hunter or the curator of this run.

## What you read
- Your launch text (RUNF/ops/ASSESSOR_LAUNCH.md, made from the pack's launch page {PACK}/ASSESSOR_LAUNCH.md; not shipped in this release, write it from generic/prompts/assessor.md). It names your write list and wins over this page where they differ.
- The rules the hunter followed: RUNF/ops/HUNTER_RULES.md (pinned, L10 on); before that the pages as they stood at launch ({PACK}/*.pre_* twins). The exact job commands are in RUNF/ops/JOB_SHEET.md (the pack's job sheet, since C143); RUN_PROMPT.md and HUNTER_PROMPT.md in older runs are retired kit text: never score against them.
- The run folder: CARD.md, work/CLAIMS.md, work/FORECASTS.tsv, work/MAC_JOBS.tsv, work/RESULT_<run>.md, the pipe folders, the split folders, jobs/.
- Rounds: R1 = pipe_r1 (or the run's first pipe), broad parent = pipe_p2 (when the power line asked for it), R3 = pipe_r3, placebo R3P = pipe_r3p. COUNT-only folders (pipe_x*, pipe_y*, pipe_z*) are never rounds. pipe_r1b, pipe_r3b (older runs): each graded variant is its own row (R3B ...).
- SERIES_V2_CONFIG.json: only the keys windows, yardstick_design_sepjan and yardstick_design_sepjan_up. A memory run's ops/KNOWLEDGE_BRIEF.md for the KNOW rows; a control run: no knowledge store file at all.
- grep only the files named here and the run folder, never the whole series folder.

## Months
Design months Sep 2025 to Jan 2026 (window 20250910:20260131). Feb-Mar 2026 are held out and Apr-Jul 2026 closed: never read or write a number from Feb to Jul 2026. A DEF to 2026-03-31 is no leak. A run that graded more than the 5 design months: say so in M8_YARD's how and your reply. Text-search the run's CARD, CLAIMS, FORECASTS and RESULT for 2602 to 2607 or Feb to Jul 2026: a hit with a number from those months is a B3 row (name its place, never copy the number); the held-out line and rule text without numbers are not.

## MISTAKES.tsv (header mkey kind step evidence earlier_cid how; one row per mistake, each with its receipt)
- kind: HUNTER (own slip); TOOL (a tool refused or broke on input the hunter's pages allow, also when no page states the limit); TEMPLATE (the hunter followed a page or template as written and its text caused it).
- Other keys (the forms above win where they differ; check the run's work/scripts/ and HOTFIX rows for NOTOOL and REWORK rows: a hunter script that does a tool's job is NOTOOL): NOTOOL:<step>:<row or none>; HAND:<step>:<tool>; REWORK:<step>; REFUSED:<tool>:<first refusal word>; STOP:<nn>:<CODE> (CODE = the "code" field of STOP_<nn>_*.json, e.g. STOP:05:JOB_EXIT; the cause words from its log go in how); CARD_MISMATCH:<round> (a card number that differs from its receipt; one row per number, card cell and receipt value in evidence); B3:<closed_month|after_fire|grade_before_prereg>; C2:OVERCLAIM (read every line of the card's map, answers and Learned; one row per distinct claim with no t, naming every line that repeats it; a CARD_MISMATCH row never stands in for one); FORECAST:<LATE|MISSING|EDITED>:R<k>; KNOWRETRY:<fid>; DEF_SCOPE:<round>:<code> (a condition read on the wrong scope). An overclaim is a word the numbers do not support, a number derived by hand with no t, or two causes not separated.
- earlier_cid: one id, the earliest row with the key, never a *_REPRO row: the cid of an earlier MISTAKE row with the same key ({SEAT_ROOT}/CURATED_SERIES.tsv (the seat's own list of curated runs; a new seat starts it with its header line only), {SEAT_ROOT}/CURATED_SERIES_V2.tsv (alarm seat), earlier runs' MISTAKES.tsv) from before this run's ops/LAUNCH_UTC.txt; an earlier row found only in a run's MISTAKES.tsv: <run>:MISTAKES:<row number>.

## ASSESS.tsv (header section item value receipt how; every value in the exact "key value" form below: the pack's proof tool parses it (alarm pack: {PACK}/tools/bar_check_v2.py))
- M1: "<n> of <rows of MISTAKES.tsv>" (n = rows whose key repeats an earlier key).
- M1_HUNTER: "<n> (<keys>); failures_log_repeats <a>; earlier_key_repeats <b>" (hunter rows only; a refusal already in {PACK}/FAILURES_LOG.tsv hit again without its logged fix is a failures_log repeat).
- M3_STOPS: "tool_stops <n> template_stops <m>" (each counted alone).
- M7_<round> per graded round (M7_R1, M7_R3, M7_R3P, M7_R3B ...): "lead15 <x> lead1h <y> waves <z> t15 <a> months_pass <k> months <m> word <w>" from STEP_11 and STEP_14; not graded: "lead15 MISSING", stop words in how. M7_R2: the broad parent's numbers in the same form from its STEP_11 (also when graded in an earlier run: ../L<nn>/pipe_p2), else "NA split round"; then "largest_split_gap_t <x> (<reading>)".
- M8_YARD: "yard15 <same-side yardstick> best_round <1|3> best_lead15 <x> margin <x - yard15> best_months_pass <k> best_t15 <a> better yes|no". Same side: the pack's yardstick for the run's side (alarm pack: FDONLY down-side, FUONLY up-side). Best round = the higher lead15 of R1 and R3 (a tie, or R3 not graded: R1); a placebo R3P is never the best round.
- M9_WITHIN: "r1_lead15 <x> best_lead15 <y> diff <y - x> best_beats_r1 yes|no r3_beats_r1 yes|no|NA".
- M11_FORECAST_<round> per graded round with a forecast: "pred_lead15 <p> actual_lead15 <x> abs_err <|p - x|> state_match yes|no|NA sealed_before_job yes|no". M11_FORECAST: "mean_abs_err <mean over every M11_FORECAST_<round> row with a number, R3P included> n_rounds <n> best_round_state_match yes|no|NA".
- M11_PROB: "brier <b> coverage <k>/<n>" from `python3 -B {PACK}/tools/forecast_score.py <run id> --print` (alarm pack tool) (a run id such as L11, not a path; writes nothing); coverage = graded rounds whose actual lead15 is inside its 80% interval, of rounds with one. p = the chance of passing every part of R1's pass rule; the broad parent has no p.
- M12_NOVELTY: "max_overlap_pct <x> with <alarm> source <card|tool> rediscovery yes|no"; when the novelty step compared against 0 registry alarms: "max_overlap_pct MISSING (compared against 0 alarms)".
- M13_ARM: "arm <L|C> run_id <run> task <task> launch_utc <ops/LAUNCH_UTC.txt>".
- B1_CLEAN: "hand <n> tool_stops <M3 tool_stops plus template_stops> blindfold <B3 rows>" (here tool_stops is the sum).
- Lean rows: CARD_LEAN "works_when yes|no fails_when yes|no numbers yes|no map_rows <n> r3 confirmed|killed|missing"; R3_CHECK "side_first yes|no size_first yes|no verdict_matches yes|no" (in CLAIMS before the R3 job); RULE_USE "shown <n> used <k> (<ids>)" (arm C: NA_CONTROL); PLACEBO "r3p_reading <code> smallest_r1_gap_t <t> share_graded r3 <x> r3p <y> within5 yes|no r3_minus_r3p <d>" (and whether the reading is excluded, and why); ROUND_CHECK: the last line of `python3 -B S/build/check_round_v1.py RUNF --run-number <n>`.
- KNOW rows (memory runs; arm C: NA_CONTROL for all four): KNOW_CITED "brief_sha16 <x> claims <n> cited <k> (<ids>) valid <j>"; KNOW_RETRY "<n> (<fids>)"; KNOW_MOVE "fid <F> before <status> after <status> by <eid>|none" (PENDING_CURATOR before curation); QUESTION_TAKEN "<qid>|none result answered|open|not_tested".
- HOLD_LEAD15: memory runs "asked orchestrator, pending" (never read it); control runs "control run: no held-out read".
- Old rows (R00-R05, FEEDBACK, BEST_ROUND, KNOW_PROPOSE, M2, M4-M6, M10): NA_LEAN.

## ops/EVIDENCE_HANDOFF.tsv (header round test_kind pipe_folder step_file sha16 lead15 minus_yard15 t waves job; a control run adds a column arm = C)
test_kind is exactly VARIANT, SPLIT_STATE or YARDSTICK. VARIANT: one row each for R1, the broad parent (always when the run split it, also when graded in an earlier run), R3, R3P, any other graded variant. SPLIT_STATE: one row per split folder the run made (each reading on each pipe, once). YARDSTICK: one row, its existing receipt. minus_yard15 = lead15 minus the same-side yardstick, both rounded to 2 decimals first (11.37 - 10.99 = 0.38). Numbers copied from the receipts, design months only.

## REPRO mode (a second fresh assessor)
Write ASSESS_REPRO.tsv and MISTAKES_REPRO.tsv; never open the first assessor's files.

## End
Reply in a few lines (files, sha16s, key values, what you could not check); write the REPORT block of {GENERIC}/REPORT_TEMPLATE_V1.md into RUNF/ops/REPORT_ASSESSOR.md (a REPRO assessor: ops/REPORT_ASSESSOR_REPRO.md). If that write is refused, end your reply with the block and say so: the orchestrator loads it from the reply.
