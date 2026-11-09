# LEARNING_LOOP_V1_1: the generic learning loop (SCOUT, 8 Nov 2026; LEARNING_LOOP_V1, built as release candidate RC5, and its documents edition V1_1)

Status: released as LEARNING_LOOP_V1 (code) and LEARNING_LOOP_V1_1 (the same code, pages corrected: CHANGELOG.md), installed at `<RELEASE_ROOT>/Learning_Loop/learning_loop/LEARNING_LOOP_V1_1` (`current` points to it). the owner 8 Nov 17:20Z: "if L11 is ready we will then release the V1 of the learning loop so that other agents can start implementing their own packs to use it. First one will be strategy." L11 finished (runs_v2/L11/ops/L11_CHECKS_SUMMARY.md). RC5 = RC4 (signed off: release_staging/RC4_SIGNOFF_RECEIPT.md on REVIEW_LEARNING_LOOP_V1_RC3.md) plus the alarm-seat changes made in and after L11 (ledger C219 to C230) and their generic part: the reader step (LOOP.md step 7), the two-readings check (REPORT_TEMPLATE_V1.md), the fixed mistake-key forms (ASSESSOR_STEP_V3.md) and the C224 reasoning rubric (drills/REASONING_QUALITY_V3.md). CHANGELOG.md, section LEARNING_LOOP_V1. Card: TOOL_CARD.md. What is still open: OPEN.md.

## What the loop is
A research loop for paper research by any seat. Each run takes one idea through fixed rounds, seals a forecast before every round, writes a card with a receipt for every number, then is scored by an assessor and turned into knowledge by a curator, only through the knowledge tool. A control run with no memory runs beside it, so the proof is "memory beats control", never "it looks better". Every part of the loop is drilled on its own with fresh agents and a sealed key, and every drill and every fix is a row in the registers.

The loop is split in two (generic/SPLIT.tsv, 38 documents, each marked generic, pack or both):
- `generic/`: the same for every seat. The loop page, the rules template, the step pages, the role prompts and skills, the templates, the knowledge tool, the registers tool, the drill tools.
- `packs/<seat>/`: what only one kind of research knows. Rounds, pass bars, yardsticks, data traps, mechanism names, job templates, the run builder, the held-out route.

Proof that the split works: the P35 portability drill. Fresh agents with only `GEN_V2` (from which `generic/` was built; RC1 to RC4 then changed or added the generic pages and tools marked "changed in" or "new in" in MANIFEST.tsv, which are not drill-proven: OPEN.md item 5) and the strategy pack V1 ran a planted series. Rounds P35_R3 and P35_R4 passed on KEY_V3 (44/46 and 45/46, alpha 0.95 and 0.84, gate 2 "no seat file read" passed from the call logs), with no change beyond knowledge_v2. DRILL_RUNS.tsv rows `P35V2-pair` and `P35V2-pair2`.

## Folder
| path | what |
|---|---|
| `generic/LOOP.md` | the loop: roles, one run in order, knowledge, proof, drills, logs, making a pack |
| `generic/RULES_TEMPLATE.md` | the rules page with slots; a pack fills the slots; its fixed sections apply to every pack |
| `generic/ASSESSOR_STEP_V3.md`, `generic/CURATOR_STEP_V3.md` | the generic step pages (P35 versions, differ from the alarm seat's live pages) |
| `generic/REPORT_TEMPLATE_V1.md`, `generic/STUCK_CHECK.md`, `generic/KNOWLEDGE_README.md` | REPORT block form, stuck check, knowledge commands |
| `generic/prompts/` | hunter, assessor, curator launch prompts |
| `generic/skills/` | volat-hunter, volat-assessor, volat-curator skill copies |
| `generic/templates/` | CLAIMS.md, FORECASTS.tsv |
| `generic/drills/` | DOCUMENT_PROCESS_V1, PROCESS_IMPROVEMENT_V1, KEYCHECK and KEYFIX templates |
| `generic/tools/knowledge_v2/` | build_knowledge_v2.py, every alarm constant moved to `--pack <file.json>`; tests; README (the pack contract) |
| `generic/tools/registers/` | reg.py (drill, improve, mess, score, ledger, proposal, import-report; baseline, check, ledger-check, scorecard, audit), messy_triage_v1.py, tests, README |
| `generic/tools/drills/` | blind_kit_v1.py (blind scorer kits), agreement_v1.py (scorer agreement), leak_scan_v1.py (held-out leak scan), tests |
| `generic/SETTINGS_TEMPLATE.md` | every placeholder of the generic pages and every environment variable of the tools, defined once; a seat copies it and fills its values |
| `generic/DRILLS.md`, `generic/prompts/orchestrator.md`, `generic/prompts/drill_agent.md`, `generic/skills/volat-orchestrator/` | how to drill any part; the generic orchestrator steps and skill |
| `*/tools/*/TOOL_CARD.md`, `TOOL.json` | the card of each tool folder (TOOL.json generated from the code) |
| `packs/alarm/tools/` (RC2) | also bar_check_v2.py, forecast_score.py, pool_splits_v1.py, check_round_v1.py with tests; packs/alarm/HELDOUT_PATTERN.txt (the leak scan pattern) |
| `OPEN.md` | what still blocks the release |
| `generic/registers_template/` | an empty copy of every register (header line only) and the alarm seat's PARTS.tsv in full, as the example a new seat rewrites for its own files (How a seat starts, step 3) |
| `generic/SPLIT.tsv`, `generic/GEN_V2_CHANGES.md` | the split of documents; why GEN_V2 differs from GEN_V0 (fixes X1 to X7 and the B1 line) |
| `packs/alarm/` | the first pack: RULES.md (= live HUNTER_RULES_V2.md), JOB_SHEET_V1.md, templates/, CARD_TEMPLATE.md, ROUNDS.md, HELDOUT.md, MECHANISMS.txt, FAILURES_LOG, HOTFIX_LOG, ADOPTED_NOTES, alarm.json, drills/ (the task folders of kits H01, H03, H04, H05, H06, H08; H02 and H07 are not shipped), drill_keys/ (their answer keys, apart from the tasks: orchestrator and scorers only, KEYS.md), jobs/, tools/ (build_run_v2.py, combine_readings_v1.py, part_a_v2.sh, SERIES_V2_CONFIG.json), playground/ (held-out launcher pipe_mac_v3_heldout.py, queue_job_v15/v16_scout.py and its test), seat_pages/ (the alarm seat's live ASSESSOR_STEP_V3, CURATOR_STEP_V3, LEARNING_LOOP_V3, PROOF_RULES_V2) |
| `packs/alarm/launch/`, `packs/alarm/seat_pages/REASONING_QUALITY_V3.md`, `REPORT_TEMPLATE_V1.md`, `packs/alarm/tools/speed_report_v1.py` (new in RC5) | the alarm seat's assessor and reader launch pages, its reasoning rubric and report template (live twins of the generic pages), the speed table of runs, rounds and drills (P34) |
| `generic/drills/REASONING_QUALITY_V3.md` (new in RC5) | the reasoning rubric (C224) any seat scores runs with, two blind scorers |
| `packs/strategy_draft/` | the second pack, DRAFT: STRATEGY_PACK_V1.md, MECHANISMS.txt, strategy_v0.json (every status bar TODO for the owner); DRAFT.md says what is open |
| `MANIFEST.tsv` | every file: sha16 (first 16 hex of sha256) and its source path |
| `TEST.md` | the exact test commands from this copy and their results |
| `CHANGELOG.md` | this candidate, and every change made to a copy |
| `PROOF_RECEIPTS.tsv` | each part with its latest score and the DRILL_RUNS rows that prove it |
| `ARCHIVE_PLAN.tsv` | old loop folders and files this V1 replaces, with reason and target (nothing moved) |
| `SEAT_PATHS.tsv` | every SCOUT-only or machine path still inside generic/ |

## How a seat starts
0. Its copy of this release: copy this folder once into the seat folder (for example `{SEAT_ROOT}/release/`) and use it read only; `{GENERIC}` is that copy's `generic/`. Its settings: copy `generic/SETTINGS_TEMPLATE.md` into the seat's folder, fill every value once, and set the environment variables it lists (every `{PLACEHOLDER}` in the pages means that value).
1. Its own store folder, never another seat's: `python3 -B generic/tools/knowledge_v2/build_knowledge_v2.py init --pack <its pack.json> --dir <its store>` (init makes the folder when it is missing). Command forms, with `--set` repeated per key: generic/KNOWLEDGE_README.md, Examples.
2. Its own pack: copy `packs/strategy_draft/` (or `packs/alarm/` as the worked example) to the seat's folder; write its one rules page `{PACK}/RULES.md`: `generic/RULES_TEMPLATE.md` with every slot filled (strategy draft: the fills are in STRATEGY_PACK_V1.md); hunters read only that page; write ROUNDS (purpose, process, pass, fail meaning, measure, drill per round); set MECHANISMS.txt; fill every `TODO` of the pack JSON with the owner (the tool refuses `check`, `brief` and finding ops while a bar is TODO); write its own job sheet and builder settings.
3. Its own registers: copy `generic/registers_template/*.tsv` into the seat's {REGISTERS} folder and set LL_REGISTERS and LL_SEAT_ROOT (SETTINGS_TEMPLATE.md; without them reg.py reads and writes beside itself); then its first ledger rows, once: (a) PARTS.tsv in the template names the alarm seat's files, so point each `files` cell at the seat's own copies (this one rewrite at start is allowed; `{GENERIC}`, `{PACK}`, `{SKILLS}`, `{SEAT_ROOT}` in a cell are read from env LL_GENERIC, LL_PACK, LL_SKILLS, LL_SEAT_ROOT); (b) `python3 -B {GENERIC}/tools/registers/reg.py baseline who={SEAT}` writes one BASELINE ledger row per file and refuses, writing nothing, while any file is missing (it lists them); (c) `reg.py ledger-check` must print LEDGER_CHECK PASS (TEST.md row 14b). After that change PARTS.tsv only by adding rows. Run `python3 -B reg.py check` after each batch and `reg.py ledger-check` before every run and release.
4. Before the first run: the process drill (H08 kit in `packs/alarm/drills/H08`, key in `packs/alarm/drill_keys/H08`, as the model; its tasks name alarm pages, so the seat points them at its own RULES.md) on the filled RULES.md with 3 fresh agents, pass 12 of 13 (LOOP.md section 7).
5. Copy a file before changing it; at most 3 agents at once unless the owner says more; no deletes outside the seat's own scratch.

## The order of roles (one agent per role, never two roles in one agent)
1. Orchestrator builds the run with the pack's builder (memory runs get the brief and adopted rules, controls get none; the builder refuses a leak or a held-out number).
2. Hunter: step 0 (R0 lines), then for every round a CLAIMS line and a sealed FORECASTS line, then the pack's rounds, then the card.
3. Control hunter: the same run with no memory, beside the memory run; nothing it finds enters knowledge.
4. Assessor: every card number against its receipt; ASSESS, MISTAKES, evidence hand-off.
5. Curator: only through the knowledge tool (op, check, brief); statuses by numbers only.
6. Orchestrator: held-out read (best round, rule frozen, once, words only), clean, next run from the new brief.
7. Drill agents: one part at a time, fresh and isolated, one file in and one file out.

## Where each proof receipt is
Source: `drills_v2/registers/SCORES.tsv` (latest row per part) and `DRILL_RUNS.tsv`. Full rows, with failing rows and missing evidence ids: `PROOF_RECEIPTS.tsv`. The latest scores are from 11:55Z or earlier; drills after that are in DRILL_RUNS but not yet scored.

| part | name | latest status | passing DRILL_RUNS rows (run_id) |
|---|---|---|---|
| P01 | Hunter rules page | PROVEN | BLIND-H08, HID-H08-a, HID-H08-b, K1B-o_a, K1B-o_b, K1B-s_a and 9 more |
| P02 | Hunter full prompt | WEAK | R014, R015 |
| P03 | Role skills | PROVEN | RD6-a, RD6-b, TAKEOVER-BLIND |
| P04 | Assessor and curator | PROVEN | ASSESS-C03, ASSESS-C04, ASSESS-L10, CUR-L10, K2B-o_a, K2B-o_b and 7 more |
| P05 | Card template | PROVEN | BLIND-H07 |
| P06 | Research step and idea choice | PROVEN | R2-H01-L06, R2-H01-L07 |
| P07 | Forecasts | WORKS | P07N-o_a, P07N-o_b, P07N-s_a, P07N-s_b, P07R2-pair (score evidence FCST-PRINT-1111 is not a DRILL_RUNS row) |
| P08 | Round 1: the claim | PROVEN | R2-H04-BLIND |
| P09 | Round 2: explain | WEAK | R2-H05-BLIND |
| P10 | Round 3: sharpen | WEAK | none (BLIND-H06-R3v3: no) |
| P11 | Next questions | WORKS | H11-L05-a, H11-L09-a, P11N-o_a, P11N-o_b, P11N-s_a, P11N-s_b and 1 more |
| P12 | Reasoning quality | PROVEN | P12-o_a, P12-o_b, P12-s_a, P12-s_b, REAS2 |
| P13 | Messy reports | WEAK | RPT1-a, RPT1-b |
| P14 | Held-out read | PROVEN | R012 |
| P15 | Scratch cleanup | PROVEN | CLEANUP-1 |
| P16 | Knowledge store and builder | PROVEN | R2-KNOW_TOOL (v1 tool; v2 proof is its test suite, TEST.md) |
| P17 | Knowledge brief | WORKS | P17-o_a, P17-o_b, P17-s_a, P17-s_b |
| P18 | Run builder | PROVEN | R008, R2-LEAK_HELDOUT |
| P19 | Job template and fire cap | PROVEN | R009, R2-FIRE_CAP |
| P20 | Round checker | PROVEN | CHK-1, CHK-L10, CHK-L10b |
| P21 | Round 2 tools | PROVEN | R2TOOL-NULL, R2TOOL-POS |
| P22 | Proof tool | PROVEN | BARS-C90 |
| P23 | Forecast scorer | PROVEN | none (evidence FCST-PRINT-1111 not in DRILL_RUNS) |
| P24 | Handover and restart | PROVEN | RESTART-BLIND |
| P25 | Registers | PROVEN | none (AUDIT-1: no); tests in TEST.md |
| P26 | Process documents | PROVEN | K4R2-SCORE, RDD9-a, RDD9-b |
| P27 | Memory beats control | WORKS | none (BARS-B3-1, BARS-B3-2: no) |
| P28 | Market understanding | WORKS | H12-L09-a, P28N-o_a, P28N-o_b, P28N-s_a, P28N-s_b, P28R2-pair |
| P29 | Process improvement loop | WORKS | K2MIX-SCORE-v, K2MIX2-SCORE-v, K3MIX-SCORE-v, K3MIX2-SCORE-v, K4MIX-SCORE-v, P29A-chain and 1 more |
| P30 | Knowledge store content | WORKS | R2-H01-L06, R2-KNOW_TOOL |
| P31 | Metric use | PROVEN | BLIND-H04-R1v3, R2-H04-BLIND |
| P32 | Drill keys and rubrics | PROVEN | BLIND-H04-R1v3, K1B-SCORE, K1R2-SCORE, K2B-SCORE, K2MIX3-SCORE, K3MIX2-SCORE and 3 more |
| P33 | Safety and data integrity | PROVEN | LEAK-1, LEAK-2, LEAK-3 (evidence R-builder not in DRILL_RUNS) |
| P34 | Speed and cost | WEAK | none (evidence SPEED_20261108_L10 is a file, not a drill row) |
| P35 | Generic loop portability | not scored, not a PARTS.tsv row | P35V2-pair, P35V2-pair2 (rows logged under part P26, drill P35_PORT) |

Read it as three answers: computed (the rows exist and say yes), meaning (the part did what its drill asks on that snapshot), stable (only where two or more independent rows agree). Parts with "none" have no drill row that says yes: their status rests on a score row alone.

## What is still open
Nothing blocks this edition. Still open (OPEN.md): owner item 1 (the strategy pack bars, needed before the first strategy run) and the technical items 4 onward.
