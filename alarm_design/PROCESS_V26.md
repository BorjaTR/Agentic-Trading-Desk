# ALARM_BUILD process V26 PROVISIONAL (owner SCOUT, 2026-11-07, SCO-A183: SCOUT brief 2026-11-07 (the owner 7 Nov 08:51-08:54 and 09:13 Berlin: research reads to 20260331, the out-of-sample months one look per alarm, the never-seen months refused; goal today: the PROOF_RULES_V2 measured block starts when this set is current)): the one alarm design process: who does what, in what order, with which tool and which file (SCO-A177 ONE_PROCESS_V1), then the checked step lines of V25 with the V26 pins.
History: V25 (SCO-A171, current from job 20270490) is PROCESS_V25.md f819f3c3eb3d0e55; V26 keeps its six agent steps and 22 pipeline steps and adds row T03-05 (state_split) to step 3.
History: V24 (SCO-A169, current from job 20270436) is PROCESS_V24.md 00915cd915a2425f; V25 keeps its six agent steps and 22 pipeline steps.
History: V23 (SCO-A162, installed held, never current) is PROCESS_V23.md 529520cf6f57eeab; V24 keeps its six agent steps and 22 pipeline steps.
History: V22 (SCO-A163) is PROCESS_V22.md 07185947d62ac83c; V23 keeps its six agent steps and 22 pipeline steps; P17 CARD runs mech_cards_run_v2, the settings come from the session-free PIPE_SETTINGS_V3_TEMPLATE.json, and step 2 names the released pipeline.
History: V21 (SCO-A160) is PROCESS_V21.md b84aaaf55ec7553e; V22 keeps its six agent steps and 22 pipeline steps; START_V26 HOW TO LAUNCH lists the 22 steps with their tools and outputs.
History: V20 (SCO-A157) is PROCESS_V20.md 6779f91fcc2cf579; V21 keeps its six agent steps and 22 pipeline steps and changes only tool rows (TOOLS_V26.tsv, CHANGES_V26.tsv).
History: V19 (SCO-A154) is PROCESS_V19.md 46a0a3dd9055204a; V20 keeps its six agent steps and 22 pipeline steps and changes only tool rows (TOOLS_V26.tsv, CHANGES_V26.tsv).
History: V18 (SCO-A153) is PROCESS_V18.md 9238d64c89ba2718; V19 keeps its six agent steps and 22 pipeline steps and changes only tool rows (TOOLS_V26.tsv, CHANGES_V26.tsv) and the pipeline settings.
History: V17 (SCO-A147) is PROCESS_V17.md 64a131d9fc67652b; its steps 1 DRY_WALK, 2 SMOKE, 3 COPY_SEARCH, 4a, 4b, 5 DEFINE (the DEF is written at CLAIM), 6 to 14 are pipeline steps P01 to P22 or the agent steps below.

## The one process (ONE_PROCESS_V1, SCO-A177; owner words the owner 7 Nov 08:59 Berlin)
Status: RELEASED in ALARM_BUILD_V26 (SCO-A183 landed the SCO-A177 draft 6f3f06ea0ca96597; windows, yardstick and tool editions made current). The step lines the pack and rules checks read follow this part, under "The checked step lines".
Owner words (the owner 7 Nov 08:59 Berlin): "We should have 1 process, 1 flowchart page, 1 skill for alarm design (+ the other skills needed), 1 prompt, 1 learning loop".
Paths: FR = $HOME/mnt/dev/TradingPlatform_repo/volat-agent/forensics (Mac <LAB_REPO>/forensics); R = $HOME/mnt/volat_release (Mac <RELEASE_ROOT>); LS = FR/team/SCOUT/loop_day_20261105/learning_series; PACK = R/Alarm/alarm_design/current.

## The five documents (one of each, and where each lives)
| one | file (home) | what it holds |
|---|---|---|
| process | PACK/PROCESS_V26.md (this text) | who does what, in what order, with which tool and which file |
| prompt | PACK/PROMPT_V26.md (ONE_PROCESS_V1/PROMPT.md) | the hunter prompt, the only prompt |
| learning loop | PACK/LEARNING_LOOP.md (ONE_PROCESS_V1/LEARNING_LOOP.md) | hunter, assessor, curator, rounds, knowledge table, proof rules |
| flowchart | PACK/FLOWCHART.html (ONE_PROCESS_V1/FLOWCHART.html) | the whole flow on one page |
| skill | R/Skills/volat-alarm-design/SKILL.md and the account skill (thin pointer) | when to use, where the pack is, the one start command |
Everything else that describes the process is HISTORY with a one-line pointer to the file above (ONE_PROCESS_V1/CHANGES.md). Nothing is deleted.

## Windows (the owner 7 Nov 08:51-08:54 and 09:13 Berlin; the tools that hold them are current with ALARM_BUILD_V26)
| window | dates | who reads it | tool that holds it |
|---|---|---|---|
| in sample (design) | 20250910 to 20260331 | the hunter, every round | alarm_pipeline step P01 (ALARM_PIPELINE_V1_4_1: block SEPMAR, graded by the kit GRADE of ALARM_V1_22_1) |
| out of sample | 20260401 to 20260731 | SCOUT only, one look per alarm, on the best round, rule frozen | holdout_month HOLDOUT_MONTH_V1_1 (armed by the law's holdout look, register HOLDOUT_OPENS_APRJUL.tsv) |
| never seen | 20260801 to 20261130 | nobody; refused by name; the owner opens it once | pipeline STOP NEVER_SEEN, holdout REFUSED NEVER_SEEN, lab3/law.py 099d649e603074e1 |
A month outside the window a step allows is never named in any file an agent writes.

## Yardstick
Beating matched random moments is not enough: a plain down move already does. The yardstick is FDONLY on Sep 2025 to Mar 2026 (the in-sample block): lead +5.88 at 15 min (t +3.42), +6.87 at 1 h (t +3.72), 1786 waves, 5 of 7 months passing, decide R1 PASS and R2 PASS (SCO-A176 job 20270531, team/SCOUT/receipts/20270531_A176_YARD/YARDSTICK_FDONLY_SEPMAR.tsv); the Sep-Dec figure +8.01 (867 waves, 3 of 4 months) is history. A round is a better moment only if its STEP_11 lead at 15 min beats FDONLY, with more months passing (or the same months and a higher lead) and t at least 3. Every lead is written "lead X, minus FDONLY = X - 5.88" through receipt_num_v3 (TOOLS row TEV-04); per market state the split comes from state_split (row T03-05).

## Who
- SCOUT (conductor): prepares the run, launches the three agents, files the holdout, runs the cleanup, never answers the hunter with hints.
- Hunter: one fresh agent per run; thinks, writes the claim, starts the pipeline, analyzes, three rounds, proposes. Never builds a data tool.
- Tools: every data step (22 pipeline steps in one Mac runner job).
- Assessor: a second fresh agent; trusted close, grading, mistakes, measures.
- Curator: a third fresh agent; adopts, defers or rejects, writes knowledge rows and prompt rows, prunes.

## Steps (each: who, tool with its TOOLS row or path, file it writes)
| # | step | who | tool | writes |
|---|---|---|---|---|
| S1 | make the run folder | SCOUT | run_kit kit_new (R/Learning_Loop/run_kit/current, run_kit_v3_1.py; register row of FR/team/SCOUT/pack_kit/PROCESS_REGISTER_V1.tsv) | RUNF/library, RUNF/root, prep/run_N_KIT_NEW.txt |
| S2 | make the brief | SCOUT | launch_v1.py (R/Learning_Loop/loop_gates/current) with GOAL_SERIES.txt and PASS_RULE_SERIES.txt | RUNF/prep/BRIEF.md |
| S3 | fill the pipeline settings | SCOUT | sed on PACK/PIPE_SETTINGS_V3_TEMPLATE.json (19ae5e4484a1b556) | RUNF/ops/PIPE_SETTINGS_RUN.json |
| S4 | build the prompt | SCOUT | LS/build/build_run_v1.py from PROMPT (adds the adopted PROMPT_ADD rows, earlier runs, checks paths, no em dash, no closed month) | RUNF/HUNTER_PROMPT.md |
| S5 | open the run | SCOUT | run_kit init (KIT init ... --brief RUNF/HUNTER_PROMPT.md) | ops/RUN_PROMPT.md, ops/RUN_ENV.sh, the time log |
| S6 | launch | SCOUT | one background Workflow agent with ops/RUN_PROMPT.md byte for byte | ops/LAUNCH_UTC.txt |
| H0 | questions | hunter | read_once_v2 (T00-02, T00-03) on START and QUESTIONS; loop_check.py --knowledge (the knowledge page); UNTESTED.md, TRIED_BY.tsv, SERIES.tsv, CURATED_SERIES.tsv | work/R00_QUESTIONS.md (with "Mistakes not to repeat"), work/KNOW_PAGE.txt, work/READ_ONCE.tsv |
| H0B | stuck and outside first | hunter | skills stuck-check and pro-practice-first (Scite, alphaXiv, web; papers only) | work/STUCK_PRE.md, work/PLAN_PRO_PRACTICE_<TASK>.md |
| H1 | claim | hunter | TOOLS rows T01-03 to T01-13: metric_brief_v2 and where_v3 per code (skill reading-metrics), DEF_TEMPLATE_V4, METRIC_MENU_V2 pickable YES only, CARD_V7, claim_fill_v1 seal and cardlabel, true_gate_v3 check in the hunter shell (C2) | work/R01_CLAIM.md (a who is forced, b FORCED_OUT or the map id, c what proves it wrong, d signature table, e files, f KNOWLEDGE CITED, g NEW IDEA, h BAD CHECK, i PRO PRACTICE), defs/V1.json, TRUE_V1_<LABEL>.json, work/INPUT_<IDEA>_V1.json |
| H2 | run | hunter, then tools | alarm_pipeline_v1_4.py init (PIPEV; ALARM_PIPELINE_V1_4_1), the TradingPlatform job allocator claim, LS/PIPE_MAC_JOB_TEMPLATE.sh (pipe_mac_v3 on ALARM_V1_22_1, one Mac runner job; first job --until 3) | RUNF/pipe/STEP_01..22 json, work/MAC_JOBS.tsv, work/R02_RUN.md |
| P01-P22 | the 22 data steps | tools | one released tool each (PACK/TOOLS_V26.tsv rows T02-02 to T02-31; list in START HOW TO LAUNCH section 3) | STEP_<nn>_<NAME>.json, or STOP_<nn>_<NAME>.json |
| H2c | paired control | hunter, then tools | the same pipeline on V2 = V1 minus the added condition (C5), folder pipe_v2, task <TASK>C; ends STOP 20 TRIED_EXISTS by design | RUNF/pipe_v2/STEP_*.json |
| H3 | analyze | hunter | read STEP json only; receipt_num_v3 (TEV-04) for every ratio and every "minus FDONLY"; numbers rule (C4) | work/R03_ANALYZE.md with AGAINST THE KNOWLEDGE |
| H4 | card review | hunter | read the filed card (row T04-01): ALARM_CARDS/<MECHANISM>/<ALARM>/ALARM_CARD_<ALARM>.md, HANDOFF.json, INDEX.tsv row | work/R04_CARD_REVIEW.md (ACCEPT or REJECT tied to a card row; LOW OVERLAP FLAG) |
| H5 | rounds 2 and 3 | hunter | per round: FEEDBACK (why here and not there: state_split, TOOLS row T03-05, lead minus FDONLY by market state, at least 50 waves per state; event profile of 10 fires), new sealed claim, new pipe folder pipe_r2, pipe_r3 | work/FEEDBACK_R<k>.md, work/R01_CLAIM_R<k>.md, work/R03_ANALYZE_R<k>.md |
| H6 | best round | hunter | the yardstick table of rounds 1 to 3 | work/BEST_ROUND.md (frozen DEF path and sha16 for the one out-of-sample look) |
| H7 | stuck check | hunter | skill stuck-check (R/Skills/research-learning-loop/STUCK_CHECK.md 7e677d234468d55d) on the three rounds | work/STUCK_CHECK.md |
| H8 | propose | hunter | five parts, each with a receipt (T05-01) | work/R05_PROPOSE.md, work/KNOW_PROPOSE.tsv |
| H9 | close | hunter | loop.py close (TCL-01), KIT bind; TCL-02 and TCL-06 not run in Mac mode (C3); TL end CLOSE | work/RESULT_<TASK>_LS<N>.md, work/CLOSE_V1.txt, work/BINDING_CHECK_V1.txt |
| A | assess | assessor | KIT close (TCL-03) and bind, pack_check_v4_1, rules_check, blindfold_scan_k.py, grade_k_parent.py, DRILL_GRADE_V1 C and D, the mistake keys | RUNF/ASSESS.tsv, RUNF/MISTAKES.tsv, ops/B2_B3.tsv |
| C | curate | curator | add_row.py (ADD_ROW_V2) for knowledge rows, loop_check.py --knowledge, series_row_v1.py, PROMPT_ADD with pruning | RUNF/CURATE.tsv; appends to CURATED_SERIES.tsv, PROMPT_ADD.tsv, TRIED_BY.tsv, SERIES.tsv, KNOWLEDGE_SCOUT_V1.tsv |
| S7 | out-of-sample look | SCOUT | holdout_month_v1_1.py check, then one runner job on the BEST_ROUND pipe folder (R/Alarm/holdout_month/current, HOLDOUT_MONTH_V1_1; the definition window must hold 20250910 to 20260731) | receipts HOLDOUT_<IDEA>_<V>.tsv, HOLDOUT_RESULT_<IDEA>_<V>.json, one OPENS row |
| S8 | cleanup (fixed step) | SCOUT | the end-of-run rule of DISK_RETENTION_V1.md (SCO-A175, pending): keep receipts, STEP json, cards, ledgers; delete only regenerable bulk of this run | a cleanup receipt in RUNF/ops |
| S9 | next run | SCOUT | starts from what the curator adopted (S1 again) | |

## Rules (each from a real slip)
- Never build a tool inside a run; a step runs only its TOOLS rows; a missing row is a NO TOOL line (work/NO_TOOL.tsv) with its owner and minutes. Hand work is logged in work/HAND_WORK.tsv; a small analysis script only on pipe files, logged in work/ANALYSIS_SCRIPTS.tsv as a tool to build.
- Blindfold: no closed month named; no reading after the fire second as a DEF input; no grade output read before STEP_10 sealed the claim. One breach voids the run.
- Every number goes through receipt_num_v3 or is quoted with file and sha16; never typed from memory.
- Times from date -u; twin before editing; no rm, git, sudo in shells or job texts; no em dashes.
- A stopped alarm is a successful task when it is logged and closed; a justified negative result is a pass.
- One job at a time per run; never edit a pipeline file, STEP json, PENDING, TIMES.tsv or a runner file.

## How this process changes
Edit only in the library (FR/team/SCOUT/loop_pilot_20261105/library/ALARM_BUILD), check with pack_check_v4_1, route_check, rules_check, release a new edition with the volat-release skill and a run_kit edition that carries the register row. The curator never changes a pack row or a tool: it files a DEFER to the owner.


## The checked step lines (pack_check and rules_check read these; V25 lines with V26 pins)
Starting point, in this order: START_V26.md, then QUESTIONS_V26.md and CURATED_V7.tsv (this folder); the current files and their sha16: MANIFEST_V26.tsv. The tool of every step: TOOLS_V26.tsv, one row per tool per step in the PACK_TEMPLATE_V3 columns (row_id, step, tool with its edition, route and allow, status, sha16, path, command, output, analysis_rule, next_input).
Each step: gate_v1.py check before it, gate_v1.py pass --receipt <file> after it (pinned invocations: START_V26.md section 8). A stopped alarm is a successful task when it is logged and closed. A HOLD or a refusal stops only the action or claim it names; other authorized work goes on.
Step times (V10, brief SCO-A95 c97c1f0796ae27e5): TL, the run_kit_v3 function of ops/RUN_ENV.sh (V17, row TEV-03): team/SCOUT/loop_day_20261105/str_gap4/a_time_log/time_log_v4.py (89dc6123dd89d4bc); TL switch <TASK> START_TASK DOC_READING first, TL next <TASK> <OLD> <NEW> <CAUSE> [NEW:<TOOL>] when a new step starts (one append, never end OLD && start NEW), TL switch <TASK> <STEP> <CAUSE> [NEW:<TOOL>] when the cause changes, TL show <TASK> --json at close, TL end <TASK> CLOSE last; GATES_V26 time_log keeps time_log_v3 a1d24faf3bc0bdf3, the template's shared key (pack_check R3), and a v4 journal closes and verifies under v3 (STR_GAP4_REPORT (a)); CAUSE is one of CODED, DATA_COMPUTE, DIDNT_KNOW_METRIC, DIDNT_KNOW_TOOL, TOOL_REFUSED_OR_BROKE, VM_LIMITS, DOC_READING, REWORK, WAITING, or THINK_WRITE (ordinary time); TOOL (NEW:NAME) only for CODED, the tool to release. Its show output feeds the slowdowns PROPOSE part (START_V26.md section 5). The tool is TEST, NOT REVIEWED and takes its TIME_LOG_* env from the parent (START_V26 O10-02).

Every step, launch and close: Tools (TOOLS_V26.tsv): TEV-01, TEV-02, TEV-03, TEV-04, TEV-05, TEV-06, TEV-07, TEV-08, TEV-09, TLA-01, TLA-02, TLA-03, TLA-04, TLA-05, TCL-01, TCL-02, TCL-06, TCL-03, TCL-04, TCL-05.
Rule (V15, kept; the owner 2026-11-06 about 11:15Z: "agents should never ever build a tool if one exists"): never build a tool inside a run, no script, shell function or one-off parser made by the task; a step runs only the commands of its TOOLS_V26.tsv rows; if TOOLS_V26.tsv has no row for what a step needs, or a NO TOOL row, stop that action and file NO TOOL with its owner. V18: every data step is a pipeline step; the agent never runs one by hand.
<!-- SHARED process_02 BEGIN -->
## Steps
<!-- SHARED process_02 END -->
<!-- SHARED process_03 BEGIN -->
0. QUESTIONS: read START_V<n>.md, then answer every question of QUESTIONS_V<n>.md that applies before its step and the 15 STUCK_CHECK questions, one line each naming a file, a number or a test; mark any question with no source UNANSWERED. Pass: the receipt holds every qid of QUESTIONS_V<n>.md (or NOT YET with the step it waits for) and the word STUCK (gate_v1 checks only Q01 and STUCK: START_V<n> section 8). Source: the owner 2026-11-05T11:39Z; pro-practice-first 1b; START_V<n>.md section 5.
<!-- SHARED process_03 END -->
Step 0 also: Read each source once (V10, brief SCO-A95 c97c1f0796ae27e5): one row per read in work/READ_ONCE.tsv (utc from date -u, file, sha16, lines read, why), written by read_once_v1 in the command that prints the lines (V16: row T00-02; row T00-03 prints the questions of one step and logs that read); later steps quote the lines they need from that read, and a second read of a file gets its own row saying why (trial F work/READ_ONCE.tsv 2f17e98debdb2b87; SLOWDOWNS_V1 0b99af261234fb41: DOC_READING 52.0 min, the top named cause inside trials B to E, the QUESTIONS step 6.6 to 13.7 min in every trial; trial F, with this log, 4.1 min by its own TIME_LOG, measured another way). Tools (TOOLS_V26.tsv): T00-01, T00-02, T00-03.
1. CLAIM: write the one input of the pipeline: the claim card (moment, SIZE or SIDE, who must trade and how much flow is left, what is measured and what inferred, what would prove it wrong, why the other side loses, the closest existing alarm), the DEF.json (codes by the prompt order, METRIC_MENU_V2 pickable YES only), the sealed TRUE claim and card label (claim_fill_v1 seal, cardlabel), the mechanism hypothesis (one MECHANISM_MAP_V1.md id or NONE) and INPUT_<IDEA>_<V>.json from INPUT_TEMPLATE.json (every key filled; registry_mode write for a new alarm, replay for one already graded). Pass: the receipt holds SIZE, wrong, the mechanism hypothesis and the INPUT.json sha16. Tools (TOOLS_V26.tsv): T01-01, T01-02, T01-03, T01-04, T01-05, T01-06, T01-07, T01-08, T01-09, T01-10, T01-11, T01-12, T01-13.
2. RUN: python3 -B RELEASE/Alarm/alarm_pipeline/current/tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py (003ea91ec6f5c486) init <run folder> --input INPUT_<IDEA>_<V>.json --settings <run folder>_PIPE_SETTINGS.json (filled from RELEASE/Alarm/alarm_design/ALARM_BUILD_V26/PIPE_SETTINGS_V3_TEMPLATE.json: sed @HOME@ and @SEAT@), then alarm_pipeline_v1.py run <run folder> every 5 minutes until DONE ALL; no hand step: every data step, seal, grade, decide, card, mechanism and log below is the pipeline's, each a runner job or a kit command it files and checks itself (status file exit=, opdone), each writing STEP_<nn>_<NAME>.json with its job id, exit, output sha16s and numbers. A WAIT is a running job; a STOP <nn> <NAME> <CODE> stops the run: report its words, fix only the input or file the owner, then retry. Pass: the status table with 22 DONE rows. Tools (TOOLS_V26.tsv): T02-01, T02-02, T02-03, T02-04, T02-05, T02-06, T02-07, T02-08, T02-09, T02-10, T02-11, T02-12, T02-13, T02-14, T02-15, T02-16, T02-17, T02-18, T02-19, T02-20, T02-21, T02-22, T02-23, T02-24, T02-25, T02-26, T02-27, T02-28, T02-29, T02-30, T02-31.
3. ANALYZE: one line per STEP json, what it shows, from its numbers only (quote the json sha16), no new script: COPY_SEARCH hits, COUNT waves by month and the COUNT bar, GRADE leads by month (where it worked, where it failed, why not more, why not less), TRUE verdict by month, DECIDE word, FIRSTLOOK rule, NOVELTY word, CARD strengths, MECHANISM id, share and failing leg, CLASSIFY line, LOG and ledger rows. Pass: the receipt names STEP_01 to STEP_22. Tools (TOOLS_V26.tsv): T03-01, T03-02, T03-03, T03-04, T03-05.
4. CARD_REVIEW: read the ALARM CARD the pipeline handed to STRATEGY (team/RESEARCH/LEAD/ALARM_CARDS/<MECHANISM>/<ALARM>/ALARM_CARD_<ALARM>.md, its HANDOFF.json and its row in team/RESEARCH/LEAD/ALARM_CARDS/INDEX.tsv): ACCEPT, or name the wrong row and the source it contradicts; never edit the card (a fix is a new pipeline run). Pass: the receipt names the ALARM_CARD_ file, HANDOFF.json and the INDEX.tsv row with their sha16. Tools (TOOLS_V26.tsv): T04-01, T04-02.
5. PROPOSE: four parts, each with its evidence path: process_change, better_questions, think_better, slowdowns (the TL show table). None is a rule until the curator reviews it. Pass: the receipt holds the four part names. Tools (TOOLS_V26.tsv): T05-01.

## Pipeline steps
Run by alarm_pipeline_v1 at step 2 RUN, never by hand; each writes STEP_<nn>_<NAME>.json; the kit command of each is its TOOLS_V26 row (the row ids are named by step 2).
- P01 INPUT (own): checks INPUT.json: every key, def and card sha16, window inside Sep 2025 to Mar 2026 (STOP BAD_INPUT, DEF_CHANGED, CARD_CHANGED, WINDOW_CLOSED). V26 (ALARM_PIPELINE_V1_4_1, alarm_pipeline_v1_4.py): block SEPMAR graded 20250910..20260331; STOP OUT_OF_SAMPLE and STOP NEVER_SEEN by name.
- P02 COPY_SEARCH (own): tried_search_v1 with the idea words (VERDICT line, hits).
- P03 COPY_SEARCH_DEF (own): tried_search_v1 --def --self (VERDICT DEF line).
- P04 HC_FIRES (rel): rel hc_defs_v4 on one month and five coins (indication fire list).
- P05 NOVELTY_HC (rel): rel novelty_v5 on that list (indication word).
- P06 COUNT (kitq): kitq COUNT, --dry first (waves by month, the COUNT bar line).
- P07 SEAL_TG (rel): rel true_gate_check check on the sealed claim.
- P08 SEAL_MENU (own): menu_gate_v1 check.
- P09 SEAL_VARIANTS (own): the VARIANTS row: appended in write mode, read back in replay.
- P10 SEAL_PREREG (rel): rel ledger_add_v7 prereg (write) or the prereg row read back (replay).
- P11 GRADE (kitq): kitq GRADE, --dry first; replay adopts the earlier job only when the kit refuses with ALREADY.
- P12 TRUE_FILL (own): claim_fill_v1 fill (write) or the perfire seal compared (replay).
- P13 TRUE (kitq): kitq TRUE --from-job the GRADE (adopted in replay when the kit says ALREADY).
- P14 DECIDE (own): decide_v6 (--write in write mode): the race word.
- P15 FIRSTLOOK (kitq): kitq FIRSTLOOK only on race PASS, R1 yes or both sides above random at 5 min in every month.
- P16 NOVELTY (rel): rel novelty_v5 on the GRADE fire list: the novelty word.
- P17 CARD (job): own runner job: alarm_understand_v1 bundle --from-job the GRADE, mech_cards_run_v2 on a one-alarm config (draw_v3, readings_builder_v2 in 8 worker processes, alarm_cards_v1), mechanism_v2 (CARD_JOB_TEMPLATE_V3.sh, settings card_job_template of PIPE_SETTINGS_V3.json).
- P18 MECHANISM (own): reads MECHANISM.json: one map id, NONE, UNKNOWN (a leg not measured at the fire second and the unknown fires could reach the threshold) or CANDIDATE (no threshold in the map), every share with its upper bound and legs (map rule: 0.90, map open item O1).
- P19 CLASSIFY (own): classify_line_v2 plus the mechanism id and share.
- P20 LOG_TRIED (own): add_row TRIED row (write) or the row read back (replay).
- P21 LOG_LEDGER (rel): rel ledger_add_v7 result with the K37 word (write) or read back (replay).
- P22 HANDOFF (own): card_v2 (card_v1 with the INDEX.tsv version column): ALARM_CARD_<ALARM>.md and .tsv, ALARM_CARDS/<MECHANISM>/<ALARM>/, HANDOFF.json, one INDEX.tsv row (twin first).

<!-- SHARED process_05 BEGIN -->
## Traps
<!-- SHARED process_05 END -->
- First rule (START_V26.md): a warning or candidate row never blocks (follow the kit line); a kit correction, the authority order or a route owner's permit resolves what DOC_CONFLICTS_V7 names; only two applicable authoritative texts that cannot both be met pause the dependent action, and you ask its owner.
- Walk every step to the end before a trial; three trials found three blockers one at a time (LESSONS_SCOUT_V1.md line 6).
- Results over 8 KB go as a copy file with the short lines only (LESSONS_SCOUT_V1.md line 7).
- Every agent call runs in the background; check before sending (LESSONS_SCOUT_V1.md line 8).
- Read hb/GPT.txt at every check; a HOLD stops the action or claim it names before anything else depends on it; other authorized work goes on (LESSONS_SCOUT_V1.md line 9, scoped by the owner D202611051501_57ad and GPT HOLD3 M1).
- Relays run in the foreground, line by line, under the shell's time limit; never pipe a relay, read its rc line (LESSONS_SCOUT_V1.md lines 11 and 12).
- Every kanban and board time comes from date -u in the same command (LESSONS_SCOUT_V1.md line 13).
- Judge files are never edited; check JUDGE_PARITY.tsv before editing any alarm tool (LESSONS_SCOUT_V1.md line 14).
- Run every command the recipe names through the bridge's allow-list before a trial (LESSONS_SCOUT_V1.md line 16).
- Grep market files only with day filters inside the data law (LESSONS_SCOUT_V1.md line 17).
- Count before writing any number (LESSONS_SCOUT_V1.md line 18): count the declared population with its exact filter in the same command that writes the line; quote other-source counts with attribution; keep corrected and historical receipt pins and a global FAIL as they are (curator trial C merges 6b449aed19b74e3c:count, e07b87eb28022388:logcount, 5eae5b554df225db:T1; SHADOW, mandatory=false).
- Windows (V26): the hunter reads 20250910 to 20260331 only; the out-of-sample months are read once per alarm by SCOUT through holdout_month; every other month is closed and is not named (Windows table above; CURATOR-DATE-INCIDENT 3d84e49bfcad67a0).
- A PROVEN menu status is a trap status, not proof a code can be read; ROWS and NOT_READABLE codes read as NaN with no warning (alarm_launch_ALARM_V1_5.md line 7).

- The gold example (D1.5 trial 3) ran on the desk's own engine, not the release: use INSTALL tools as AGENTS.md names them (ALARM_ONBOARD_V1 gap 1).
- Mac-only steps (hand check, COUNT, GRADE) need the Mac's PYTHON and numpy: name their route in DRY_WALK before any data (ALARM_ONBOARD_V1 gap 3; LESSONS_ALARM_V1 lesson 39).
- Jobs go to an empty queue of the live runner; confirm which runner folder is live before the first job (LESSONS_ALARM_V1 lesson 56).
- No CURATED_V7 row is adopted: SHADOW_RULE rows are shadow checklists (mandatory=false) valid only within their applies column; WARNING and CANDIDATE rows are warnings; REWRITTEN_PENDING rows wait for the curator (CURATED_V7.tsv kind column).

- On the full lab route, Mac-only tools run only through the bridge (mac_desk_v4 rel, relwait) and kit jobs only through kitq; every other tool runs in your shell with --settings $HOME/SETTINGS_SCOUT.env (ROUTE_B_V1 9cd90c4f831a8578).

<!-- SHARED process_07 BEGIN -->
## Pass rule of the task
<!-- SHARED process_07 END -->
<!-- SHARED process_08 BEGIN -->
The brief's pass rule, written before any data. A justified negative result is a success.
<!-- SHARED process_08 END -->
