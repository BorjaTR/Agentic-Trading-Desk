# LEARNING_LOOP: the one learning loop of alarm design (ONE_PROCESS_V1 draft for ALARM_BUILD_V26; SCO-A177 for SCOUT, 20261107)
Status: RELEASED in ALARM_BUILD_V26 (SCO-A183 landed the SCO-A177 draft 5987e9d7841c6d66, replacing the V25 run kit loop text; windows and yardstick made current).
Owner words (the owner 7 Nov 00:02 Berlin): "take one mechanism and have agents learn and build alarms over and over and over again at least 10 times. We want to prove that the agents learn ... if they do not learn and get better then we need to change something in the process".

## 1. One run, four seats, in this order
| seat | does | reads | writes (tool) |
|---|---|---|---|
| SCOUT | prepares and launches (PROCESS S1 to S6); after the curator: the out-of-sample look and the cleanup (S7, S8) | the register row, PROMPT, PROMPT_ADD.tsv | RUNF/HUNTER_PROMPT.md (build_run_v1.py), holdout receipts (holdout_month), cleanup receipt |
| hunter (fresh agent) | 3 rounds of claim, pipeline, analyze; best round; stuck check; five PROPOSE parts | PROMPT only, the knowledge page, UNTESTED.md, CURATED_SERIES.tsv, earlier results | RUNF/work/* (receipts), RUNF/pipe, pipe_v2, pipe_r2, pipe_r3 (alarm_pipeline) |
| assessor (fresh agent) | trusted close, grading, mistakes, measures | the hunter's files, STEP json, runner status files | RUNF/ASSESS.tsv, RUNF/MISTAKES.tsv (grade_k_parent.py, blindfold_scan_k.py, run_kit close and bind, pack_check_v4_1) |
| curator (fresh agent) | judges every proposal from receipts, writes knowledge and prompt rows, prunes, applies the change rule | ASSESS.tsv, MISTAKES.tsv, the hunter's PROPOSE and receipts | RUNF/CURATE.tsv; appends CURATED_SERIES.tsv, PROMPT_ADD.tsv, TRIED_BY.tsv; KNOWLEDGE_SCOUT_V1.tsv (add_row.py only); SERIES.tsv (series_row_v1.py only) |
No seat does another seat's work: the hunter never grades or curates itself; the assessor never curates; the curator never edits a pack row or a tool (it files a DEFER to the owner).

## 2. Rounds inside one run (learning within the run, C7)
- Round 1: QUESTIONS, step 0B (stuck-check and pro-practice-first skills), CLAIM, RUN, ANALYZE, CARD_REVIEW.
- After each round: FEEDBACK_R<k>.md: lead and lead minus FDONLY at 15 min and 1 h, months passing, t; WHY HERE AND NOT THERE (lead minus FDONLY by market state, at least 50 waves per state, card READINGS CTX.* codes or one logged analysis script on pipe files); EVENT PROFILE (minute path of the 5 best and 5 worst fires); what the next round changes and why.
- Rounds 2 and 3: a new sealed claim (a revised DEF Vn of the same idea, or a new idea), a new pipe folder; nothing graded is ever changed.
- BEST_ROUND.md: the round with the best lead minus FDONLY; its frozen DEF path and sha16 go to the one out-of-sample look. Whether round 3 beat round 1 is the within-run learning measure (M9).
- The paired legs-only control (C5) grades V1 minus its added condition, so the added condition's own effect is visible.

## 3. Yardstick and windows
- Yardstick: FDONLY on Sep 2025 to Mar 2026: +5.88 at 15 min, t +3.42, +6.87 at 1 h, 1786 waves, 5 of 7 months passing (SCO-A176 job 20270531, team/SCOUT/receipts/20270531_A176_YARD; the Sep-Dec +8.01 is history). A better moment beats it with more months passing and t at least 3; by market state the split comes from state_split (TOOLS row T03-05).
- Windows from run 8 (the owner 7 Nov 08:54 Berlin): in sample 20250910 to 20260331 (rounds); out of sample 20260401 to 20260731 (SCOUT, one look per alarm, best round only, holdout_month); never seen 20260801 to 20261130 (refused by name). The tools that hold them are current with ALARM_BUILD_V26: ALARM_PIPELINE_V1_4_1 (block SEPMAR), HOLDOUT_MONTH_V1_1 (one row per alarm in HOLDOUT_OPENS_APRJUL.tsv; it refuses a changed DEF, a second open and the never-seen months by name).

## 4. The assessor (LS/ASSESSOR_STEP.md)
1. Trusted close: run_kit close (TCL-03) and bind, the hunter's Mac jobs and the pipeline's inner jobs against the runner status files, pack_check_v4_1 and rules_check on the pack (DRILL_GRADE B2).
2. BLINDFOLD (DRILL_GRADE B3), three counts: closed month named (blindfold_scan_k.py), a reading after the fire used as input, a grade output read before STEP_10 sealed the claim. Any count above 0 voids the run.
3. DRILL_GRADE_V1 sections A, B, E, F by grade_k_parent.py; C (claim, analyze overclaims, card review, stuck check) and D (PROPOSE parts with receipts, slowdowns with minutes) by hand from the files.
4. Mistakes: one row per mistake in MISTAKES.tsv with a fixed key (NOTOOL:<step>:<row>, HAND:<step>:<tool>, REWORK:<step>, REFUSED:<tool>:<word>, STOP:<nn>:<CODE>, CLOSE:<word>, C2:OVERCLAIM, BADREPEAT:<kid>); a key equal to an earlier curated mistake key is a repeat (M1).
5. Measures into ASSESS.tsv, each with its receipt and sha16 (section 6).

## 5. The curator (LS/CURATOR_STEP.md)
1. CURATE.tsv: one row per PROPOSE item, knowledge row, mistake and untested question taken. ADOPT only when the cited receipt holds it and the next run can follow it without a new tool; DEFER when it needs a tool, pack row or another seat (posted "FOR <owner>"); REJECT when the receipt does not hold it, it repeats an adopted row, names a closed month, or optimizes the outcome inside one run.
2. Knowledge rows: add_row.py (R/Learning_Loop/add_row/current, ADD_ROW_V2) into FR/team/RESEARCH/KNOWLEDGE/ALARM/KNOWLEDGE_SCOUT_V1.tsv, one per call. Columns kid, mechanism, layer (OBSERVE, MECHANISM, ARCHETYPE, GOOD, BAD, BACKGROUND), claim, metric_codes, evidence_ref, evidence_kind, waves, tries, status, depends_on, supersedes, curator_ref, topic. SUPPORTED or REFUTED only from this run's grade with waves and the pipeline's word; everything else HYPOTHESIS. A correction is a new row with supersedes; a row is never edited. Then loop_check.py --knowledge must print VERDICT PASS.
3. PROMPT_ADD rows: each ADOPT becomes one imperative line (at most 300 characters) with applies_from_run N+1; build_run_v1.py puts every ADOPTED row into the next prompt. Pruning first (C7): a row none of the last 3 runs used, or one that narrowed ideas, is filed RETIRED with that evidence. A row is never edited.
4. CURATED_SERIES.tsv (every curated row, the next hunter's "Mistakes not to repeat") and SERIES.tsv (series_row_v1.py; numbers come from ASSESS.tsv, never typed).
5. Change rule (PROOF_RULES_V1): if 3 runs in a row after the last change show no improvement on M1 and M2, the curator names the cause with receipts and changes ONE thing it may change (a PROMPT_ADD or RETIRED row, a knowledge note row, a new hunter template edition beside the old); a pack row or tool change is a DEFER to its owner. Judged on the next 3 runs.

## 6. What is measured (PROOF_RULES_V1 M1 to M7; C7 adds M7_R2 to M10)
| measure | what | learning means |
|---|---|---|
| M1 | repeated mistakes (key match with earlier curated mistakes) | goes down |
| M2 | wall minutes, split thinking, tool, waiting (time_log_v4) | goes down |
| M3 | hand data steps and NO TOOL lines | 0, no worse |
| M4 | claim quality (4 items) and the signature check | no worse |
| M5 | knowledge rows cited at CLAIM; BAD directions repeated without a stated difference | cited above 0 from run 2; repeats 0 |
| M6 | knowledge rows proposed and adopted | the table grows each run |
| M7, M7_R2, M7_R3 | lead at 15 min and 1 h, waves, t, months per round | trend only, never optimized in one run |
| M8_YARD | lead at 15 min minus FDONLY per round, BETTER yes or no | above 0 |
| M9_WITHIN | best round minus round 1; did round 3 beat round 1 | above 0 |
| M10_WHY | each FEEDBACK names a better and a worse market state with at least 50 waves per state | yes |
Pass (agents learn), all of: M1 in runs 6 to 10 at most half of runs 1 to 5; median M2 of runs 6 to 10 at least 30 pct below runs 1 to 5; M3 and M4 no worse; the knowledge table grows and is cited from run 2; no BLINDFOLD breach. Better alarms (M7) are a trend; about 100 events are needed for a money claim.

## 7. From a run to the next pack edition
- Inside the series: the curator's adopted PROMPT_ADD and knowledge rows reach the next run through build_run_v1.py, the same hour.
- Pack or tool changes: the curator files DEFER "FOR <owner>"; SCOUT makes the next edition in the library, checks it (pack_check_v4_1, route_check, rules_check), releases it with the volat-release skill and a run_kit edition that carries the register row; the current link moves only on SCOUT GO (or the owner).
- Every run ends with the cleanup step (DISK_RETENTION_V1.md, SCO-A175, pending): receipts, STEP json, cards and ledgers kept; regenerable bulk of that run deleted.

## 8. Skills the loop uses (and why)
| skill | where | used at | why |
|---|---|---|---|
| volat-alarm-design | R/Skills/volat-alarm-design (thin pointer) | start | finds the pack and the one start command |
| stuck-check | source R/Skills/research-learning-loop/STUCK_CHECK.md 7e677d234468d55d | step 0B and step 5 | the 15 "what are we missing?" questions before a round and after three |
| pro-practice-first | R/Skills/pro-practice-first | step 0B and synthesis | how professionals detect and trade the mechanism, mapped onto our codes, before claiming |
| reading-metrics | R/Skills/reading-metrics | CLAIM | each code's meaning, unit, NEVER READ AS line before it enters a DEF |
| research-learning-loop | R/Skills/research-learning-loop | every seat | the row formats, add_row, loop_check, lessons with checks |
| everything-we-have | R/Skills/everything-we-have | any step | where a tool, metric or store is |
| volat-release | R/Skills/volat-release | edition change | the one release procedure |
| volat-strategy-design | account skill | after a card | strategy work starts from a proven alarm card, never inside this loop |
