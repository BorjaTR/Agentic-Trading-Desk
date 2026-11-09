# QUESTIONS_V26 for ALARM_BUILD (SCO-A147, SCOUT 2026-11-06, V18 CANDIDATE, the V16 question file with only lines 1 and 3 changed and no question changed; V16: SCO-A137, V16 CANDIDATE, the V15 question file with only lines 1 and 3 changed and no question changed; V15: SCO-A134, V15 CANDIDATE, the V14 question file with only lines 1 and 3 changed and no question changed; V14: SCO-A100, V14 CANDIDATE, the V10 question file of SCO-A95 with only lines 1 and 3 changed and, in V14 (SCO-A121, CURATED_GH.tsv 8ac1e5981bf5a064), Q46 to Q48 appended after Q45; PROVISIONAL playground library, not adopted): the current question file; from ## Q01 to the end of the Q41 block byte equal to the V9 file; Q42 to Q45 added (CANDIDATE)

History (provenance, not a route): V16 is QUESTIONS_V16.md 49a79948c22f91b7 (SCO-A137); V17 (SCO-A147) changes only lines 1 and 3 above the first question. V15 is QUESTIONS_V15.md 30253c8f25f1151e (SCO-A134); V16 (SCO-A137) changes only lines 1 and 3 above the first question. V14 is QUESTIONS_V14.md 7df992b97ff9065b (SCO-A121); V15 (SCO-A134) changes only lines 1 and 3 above the first question. V10 is QUESTIONS_V10.md f8a1e6bfa34b0840 (SCO-A95); V14 (SCO-A100) changes only lines 1 and 3 above the first question, and V14 (SCO-A121) appends Q46 to Q48. V9 is QUESTIONS_V9.md 745f641a8d519e88 (SCO-A61); V10 adds Q42 to Q45 after Q41 and changes only lines 1, 3 and 5 above the first question. History (provenance of the render, not a route): QUESTIONS_V8.md 4c9f88f7d692cd4a, the lossless Markdown render of QUESTIONS_V7.tsv sha256 b807f58efb2e8a9cce62545eb58c5a5e3796531eb27e52c284a8c2b361bc337d (frozen, unchanged); this file is that render with only lines 1, 3 and 5 changed (SCO-A61, brief team/SCOUT/loop_day_20261105/briefs/SCO-A61_LIBRARY_V9.md b2c8286dd9f0c19e; GPT V8 HOLD1 M1 (ALARM_LIBRARY_V8 REVIEW f5e500fd99c4dcd2, CHECKS b2075535c66e7e23)). 40 questions (Q01 to Q23, Q25 to Q41). No question text, applies, source or status field changed.

Each heading is the row qid; under it the question text, then every TSV field of that row in a JSON block (keys sorted). The source block below keeps the V7 TSV comment line and column order: Q01 to Q41 rebuild that TSV byte for byte; Q42 to Q45 (SCO-A95, curator SHADOW CURATED_EF.tsv, CANDIDATE) are new rows in the same JSON shape, so a TSV rebuilt from this file has 44 rows. The applies field is part of each question. Changes: CHANGES_V10.tsv.

```json
{
  "tsv_columns": [
    "qid",
    "step",
    "question",
    "answer_from",
    "skill",
    "answer_names",
    "origin",
    "kind",
    "applies",
    "decision_ref"
  ],
  "tsv_comment_line": "# QUESTIONS_V7 for ALARM_BUILD (SCO-A54, SCOUT 2026-11-05, PROVISIONAL playground library, not adopted; brief team/SCOUT/loop_day_20261105/briefs/SCO-A54_LIBRARY_V7.md abf47b9b2c86569c): QUESTIONS_V6 f6df530ca2078bf5 with V7 names, plus Q38 to Q40 (trial D SCT-D1 better_questions, CANDIDATE, curator trial D SHADOW decisions a1ed41f475b0efbf applied by SCOUT, see CHANGES_V7, never blocking) and Q41 (parts wave 3, CANDIDATE). 40 questions (Q01 to Q23, Q25 to Q41): SHADOW_QUESTION 27, CANDIDATE 8, WARNING 4, REWRITTEN_PENDING 1. The applies column is part of each question. Changes: CHANGES_V7.tsv. INSTALL=<RELEASE_ROOT>/Alarm/alarm/ALARM_V1_21_16",
  "tsv_sha256": "b807f58efb2e8a9cce62545eb58c5a5e3796531eb27e52c284a8c2b361bc337d"
}
```

## Q01

What decision does this alarm serve, and by which words will it be judged (R1, R2, PASS, NEEDS MORE MONTHS, STOP, FOUND, SIZE, SIDE)?

```json
{
  "answer_from": "INSTALL/playbook/PLAYBOOK.md 729dea0b663e9ea3 lines 20-29; INSTALL/playbook/ALARM_GOALS_V1.md; START_V7.md section 4 (word map)",
  "answer_names": "the bar by name and file line",
  "applies": "Curator condition: Before research name the decision and each stage's current bar with file/line. Distinguish race, truth, novelty, SIZE and SIDE; neither equivalent PASS words nor legacy FOUND alone satisfy the complete handoff. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q01 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK Words; STUCK_CHECK 1; CURATOR_SHADOW approve",
  "qid": "Q01",
  "question": "What decision does this alarm serve, and by which words will it be judged (R1, R2, PASS, NEEDS MORE MONTHS, STOP, FOUND, SIZE, SIDE)?",
  "skill": "pro-practice-first section 0-1; volat-alarm-design (old words: use the kit's)",
  "step": "START"
}
```

## Q02

Which edition of each tool is current today?

```json
{
  "answer_from": "INSTALL/AGENTS.md 09d4586046f18aca (wins among tool documents of this installed release only; owner laws and narrower briefs govern; recheck the current link at launch)",
  "answer_names": "tool name, path and sha16",
  "applies": "Curator condition: At launch pin the installed edition and its contract. A historical pin does not establish the later current link; tool-document precedence never overrides user law. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q02 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "LESSONS_ALARM_V1 line 12 (lesson 1); CURATOR_SHADOW approve",
  "qid": "Q02",
  "question": "Which edition of each tool is current today?",
  "skill": "none",
  "step": "START"
}
```

## Q03

Which months may I read? Every other month is closed and is not named.

```json
{
  "answer_from": "GATES_V7.json allowed_window (its holdout is the machine guard; never name it in prose); LESSONS_ALARM_V1 lines 4, 71, 104",
  "answer_names": "the window FROM:TO; closed months are not named",
  "applies": "Evidence asked, not a rule: Supply active brief, exact gate hash and authority for restricted extensions; current launch limits remain absolute. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q03 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "WARNING",
  "origin": "LESSONS_ALARM_V1 lessons 35, 60; EVIDENCE_REQUESTED: GATES_V1 lacks a resolved verified path and historical lessons cannot grant access.",
  "qid": "Q03",
  "question": "Which months may I read? Every other month is closed and is not named.",
  "skill": "none",
  "step": "START"
}
```

## Q04

Who must trade, and why now?

```json
{
  "answer_from": "INSTALL KIT_V5/FORCED_TRADE_MAP_V1.md 84949bf3c749d985; PLAYBOOK line 41",
  "answer_names": "the trader and the moment",
  "applies": "Curator condition: Ask who must trade and why now; record mechanism evidence separately from inference. The map is hypothesis discovery, not empirical validation or access authority. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q04 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK six questions 1; lesson 7; CURATOR_SHADOW approve",
  "qid": "Q04",
  "question": "Who must trade, and why now?",
  "skill": "pro-practice-first section 3 (outside search, closest case first)",
  "step": "IDEA"
}
```

## Q05

What is their fuel, and when does it run out (fire as it runs out: FADE; as it starts: FOLLOW)?

```json
{
  "answer_from": "PLAYBOOK lines 42, 47-49; lessons 26, 48",
  "answer_names": "the fuel series and the minute",
  "applies": "Curator condition: Ask what supplies the flow and how its start/end is observed, then predeclare direction. Do not infer universal FADE/FOLLOW correctness or duration from examples. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q05 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK six questions 2; CURATOR_SHADOW approve",
  "qid": "Q05",
  "question": "What is their fuel, and when does it run out (fire as it runs out: FADE; as it starts: FOLLOW)?",
  "skill": "volat-alarm-design section 1 (claim and mechanism first)",
  "step": "IDEA"
}
```

## Q06

Which data shows that trader IN THIS DATA WORLD (the codes it actually holds), is each code proven for rules, and is the forced trader measured or only inferred?

```json
{
  "answer_from": "KIT_V5/METRIC_FAMILIES_V1.md 163a6dc2e76797ab; where_v3 --kind metric; metric_brief_v2",
  "answer_names": "code names with metric_brief lines; measured or inferred",
  "applies": "Curator condition: Before DEFINE identify actual-world trigger and independent label families, proof routes and metric contracts; distinguish measured from inferred. A menu listing does not prove availability; missing routes remain gaps. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q06 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK six questions 3; lessons 38, 40, 53; CURATOR merge of trial A Q24 (d1c6505dcecca8c8 into CR-4056ff6b); CURATOR_SHADOW approve",
  "qid": "Q06",
  "question": "Which data shows that trader IN THIS DATA WORLD (the codes it actually holds), is each code proven for rules, and is the forced trader measured or only inferred?",
  "skill": "reading-metrics",
  "step": "IDEA"
}
```

## Q07

Has this, or a filter on the same moment, been tried? Name the registry and sibling universe actually searched; a desk-only search is WORDS ONLY for the lab.

```json
{
  "answer_from": "tried_search_v1.py (words, then --def --self); REGISTRY/SCOREBOARD.md avoid list; IDEAS_CLAIMED; PROCESS/2_ALARMS/TRIED_ALARMS_V1.tsv; desk-trial loop LQS rows (not searchable: read by hand)",
  "answer_names": "the saved search output sha16 and the 3 nearest",
  "applies": "Evidence asked, not a rule: Supply exact unindexed priors/LQS paths and an authorized search census with coverage gaps. INCOMPLETE is not novelty; named-copy reproduction differs from a new idea. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q07 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "WARNING",
  "origin": "PLAYBOOK six questions 6; lessons 5, 6, 25; CURATOR approve d70c2e8f9be0b1e6; EVIDENCE_REQUESTED: Released copy search exists but this composite source list includes unresolved LQS locations.",
  "qid": "Q07",
  "question": "Has this, or a filter on the same moment, been tried? Name the registry and sibling universe actually searched; a desk-only search is WORDS ONLY for the lab.",
  "skill": "research-learning-loop (loop_find.py)",
  "step": "IDEA"
}
```

## Q08

Why should the OTHER side lose? If both sides can win, it marks volatility, not direction.

```json
{
  "answer_from": "PLAYBOOK What fails row 1 (line 33 of the excerpt: GB1 example); lesson 33; for a SIDE claim only: CURATED_V7 K09 overrides PLAYBOOK line 119 ('no answer, no idea') for a SIZE-only claim",
  "answer_names": "one sentence, written before any data",
  "applies": "Curator condition: For SIDE ask why the other side should lose before outcomes. For unsigned SIZE explicitly mark no side claimed; a technical lean is bookkeeping, not directional proof. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q08 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK six questions 5; CURATOR_SHADOW approve",
  "qid": "Q08",
  "question": "Why should the OTHER side lose? If both sides can win, it marks volatility, not direction.",
  "skill": "volat-idea-to-alarm (six quick checks: DIRECTION)",
  "step": "IDEA"
}
```

## Q09

What result would prove the idea wrong, and what is measured vs inferred?

```json
{
  "answer_from": "seed prompt team/RESEARCH/PROCESS/PROMPTS/files/alarm_launch_ALARM_V1_5.md 4ff93b53b847fc2c line 5; GATES_V7 CLAIM receipt needs the words SIZE and wrong",
  "answer_names": "the kill result in numbers",
  "applies": "Curator condition: Before outcomes record a measurable falsifier and measured/inferred components. Do not assert automated word enforcement without the exact verified GATES contract. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q09 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "seed prompt line 5; lessons 40, 58; CURATOR_SHADOW approve",
  "qid": "Q09",
  "question": "What result would prove the idea wrong, and what is measured vs inferred?",
  "skill": "pro-practice-first section 4 (pass rules before results)",
  "step": "CLAIM"
}
```

## Q10

Is the claim SIZE, SIDE or both, and which test checks which?

```json
{
  "answer_from": "PLAYBOOK line 29 (first look words); ALARM_GOALS_V1.md lines 11-17",
  "answer_names": "SIZE, SIDE or SIZE+SIDE with its test",
  "applies": "Curator condition: Name SIZE, SIDE or both and bind each to its own test and missing/failed gates. One dimension's pass does not pass the other or authorize strategy/live execution. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q10 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "ALARM_GOALS_V1; lesson 58; CURATOR_SHADOW approve",
  "qid": "Q10",
  "question": "Is the claim SIZE, SIDE or both, and which test checks which?",
  "skill": "none",
  "step": "CLAIM"
}
```

## Q11

Does each metric mean what its name says (definition, sign, unit, scope, when known, empty)?

```json
{
  "answer_from": "metric_brief_v2 plus the code's MEANING card; KIT_V5/METRIC_MENU_V2.tsv 97a967bd24b34757 pickable YES only",
  "answer_names": "for each code: unit, scope, pickable, PROVEN or not",
  "applies": "Curator condition: Read actual code definition, unit, sign, scope, window, knownness and empties; record readability/admission separately. Any exception needs its applicable authorized contract; this question grants none. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q11 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "STUCK_CHECK 6; lessons 2, 3, 10, 13; CURATOR_SHADOW approve",
  "qid": "Q11",
  "question": "Does each metric mean what its name says (definition, sign, unit, scope, when known, empty)?",
  "skill": "reading-metrics",
  "step": "DEFINE"
}
```

## Q12

Does the rule fire at the moment the claim names (onset vs after the peak)?

```json
{
  "answer_from": "DEF_TEMPLATE_V4 fields written in market words; lesson 4 (MEANING CHECK)",
  "answer_names": "each DEF field in market words",
  "applies": "Curator condition: Translate DEF fields into the claimed moment and check knownness/first-true behavior. An after-peak statement needs an ending condition; document checking is not an execution result. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q12 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "lesson 4; CURATOR_SHADOW approve",
  "qid": "Q12",
  "question": "Does the rule fire at the moment the claim names (onset vs after the peak)?",
  "skill": "none",
  "step": "DEFINE"
}
```

## Q13

Will it fire often enough and not too much? Count the rule's ticks by authorized month first, then the qualifying waves and the fires. Name which number is the installed contract's current COUNT support or resource bar (file and line) and which is a rough sizing guide (about 30 or more waves a month, 1,000 or more in Sep-Dec 2025, under about 20,000 fires). There is no universal clock cutoff.

```json
{
  "answer_from": "hc_size_v1, hc_defs_v4 --out, COUNT job; lessons 11, 12 (lesson 54, LESSONS_ALARM_V1 line 95, is overridden by CURATED_V7 K14; its correction is LESSONS_ALARM_V1 line 8); PLAYBOOK What fails rows 3 and 4",
  "answer_names": "ticks, waves and fires by authorized month from a tool output; each number marked contract bar (with file) or rough guide; OPEN O-07 if no contract names it",
  "applies": "Curator repair: Replace with monthly ticks, qualifying waves, fire volume and current support/resource bars; distinguish rough sizing targets from required thresholds. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q13 REJECT; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "REWRITTEN_PENDING",
  "origin": "PLAYBOOK six questions 4; REWRITTEN after CURATOR REJECT (withdrawn cutoff, LESSONS_ALARM_V1 line 8)",
  "qid": "Q13",
  "question": "Will it fire often enough and not too much? Count the rule's ticks by authorized month first, then the qualifying waves and the fires. Name which number is the installed contract's current COUNT support or resource bar (file and line) and which is a rough sizing guide (about 30 or more waves a month, 1,000 or more in Sep-Dec 2025, under about 20,000 fires). There is no universal clock cutoff.",
  "skill": "none",
  "step": "DEFINE"
}
```

## Q14

Does it fit under the 2 GiB worker cap?

```json
{
  "answer_from": "hc_mem_probe_v3; PLAYBOOK What fails row 5; Waste: Memory",
  "answer_names": "probe MB",
  "applies": "Curator condition: Ask whether this definition fits the fixed release's budget using its current probe and own MB threshold. Distinguish probe/worker units; do not raise the cap or infer full-run success from a small probe. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q14 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK What fails; CURATOR_SHADOW approve",
  "qid": "Q14",
  "question": "Does it fit under the 2 GiB worker cap?",
  "skill": "none",
  "step": "DEFINE"
}
```

## Q15

Is the data complete in every month (codes empty in Sep or early Oct 2025, where data ends)?

```json
{
  "answer_from": "COUNT by month; lessons 13, 28; PLAYBOOK What fails rows 7 and 10",
  "answer_names": "per-month counts",
  "applies": "Curator condition: Ask for permitted-window coverage and knownness by code/month, including warmup and end-of-data evidence. Do not infer present coverage from historical examples or enumerate protected dates. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q15 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "STUCK_CHECK 8; CURATOR_SHADOW approve",
  "qid": "Q15",
  "question": "Is the data complete in every month (codes empty in Sep or early Oct 2025, where data ends)?",
  "skill": "none",
  "step": "DEFINE"
}
```

## Q16

Against what is it compared (matched random, the other side, the mirror on the same fires)? Which no-price label families does THIS world hold, what is each one's proof status, and which authorized route proves it? None: NOT_TESTABLE, ask the route owner, never bypass the guard.

```json
{
  "answer_from": "grade R1/R2 against random (PLAYBOOK line 25); true_gate; lesson 57",
  "answer_names": "the comparison named in the card",
  "applies": "Curator condition: Before required TRUE work identify the actual world's independent label/mirror families, compatible outside-proof readers and admission route. Missing proof is a gap, never permission to substitute trigger or price. No current family status is certified here. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q16 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "STUCK_CHECK 9; lesson 57; CURATOR approve 4056ff6b3cc9df7e (merges 8256de5645126e80, b29bb4f70c5fedca, 601a5fa434a2d859); CURATOR_SHADOW approve",
  "qid": "Q16",
  "question": "Against what is it compared (matched random, the other side, the mirror on the same fires)? Which no-price label families does THIS world hold, what is each one's proof status, and which authorized route proves it? None: NOT_TESTABLE, ask the route owner, never bypass the guard.",
  "skill": "volat-alarm-design (TRUE grade)",
  "step": "GRADE"
}
```

## Q17

Is it a copy of an existing alarm's timing?

```json
{
  "answer_from": "novelty_v5 on the GRADE fire list; name the sibling and waves near; lesson 25 (lesson 14, LESSONS_ALARM_V1 line 33, names novelty_v2 and is overridden by CURATED_V7 K19); NEW holds only against the registry unless the claimed siblings' fire lists were compared (CURATED_V7 K38, CANDIDATE)",
  "answer_names": "novelty word and the sibling",
  "applies": "Curator condition: Ask for installed novelty on the actual GRADE fire list, naming sibling and waves-near basis; bound newness to checked coverage. NEW SIDE alone does not prove new SIZE timing. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q17 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "PLAYBOOK What fails row 6; CURATOR_SHADOW approve",
  "qid": "Q17",
  "question": "Is it a copy of an existing alarm's timing?",
  "skill": "none",
  "step": "GRADE"
}
```

## Q18

Which classification word applies at each step, in the kit's words?

```json
{
  "answer_from": "START_V7.md section 4 (word map, from ALARM_ONBOARD_V1 section 5)",
  "answer_names": "the word and its tool line",
  "applies": "Evidence asked, not a rule: Supply reconciled stage/dimension mapping with exact tool contracts and independent acceptance. Preserve original tool words, not approximate PASS/STOP equivalences. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q18 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "WARNING",
  "origin": "ONBOARD gap 5; EVIDENCE_REQUESTED: Approximate mappings are labeled SCOUT OPINION; legacy FOUND omits dimension-specific gates.",
  "qid": "Q18",
  "question": "Which classification word applies at each step, in the kit's words?",
  "skill": "none",
  "step": "CLASSIFY"
}
```

## Q19

How many tries on this idea so far, in full: attempted ideas and variants, graded variants, refused, failed or incomplete attempts, and merges or retries (a retry of the same operation is not a new idea)? Is one variant first enough?

```json
{
  "answer_from": "the canonical TRIED and ledger rows and the local ledger receipt (K31) for this idea; Waste: Variant pile-ups for the graded budget (at most 3 graded, this released process only, K20); the luck-family tool is not released and not a step; no supported census artifact is named yet (OPEN O-08)",
  "answer_names": "census: attempts in total, graded, refused, failed, incomplete, retries or merges, each with its row id; then graded against the budget of 3 (fixture: 1 graded + 1 pre-grade refusal + 1 incomplete reads 3 attempts, 1 graded)",
  "applies": "Evidence asked, not a rule: Name a supported full try/variant accounting artifact and launch budget; separate the census from uncalibrated luck. Do not execute the unreleased tool because this question names it. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q19 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "WARNING",
  "origin": "STUCK_CHECK 14; REWRITTEN after CURATOR REQUEST",
  "qid": "Q19",
  "question": "How many tries on this idea so far, in full: attempted ideas and variants, graded variants, refused, failed or incomplete attempts, and merges or retries (a retry of the same operation is not a new idea)? Is one variant first enough?",
  "skill": "none",
  "step": "GRADE"
}
```

## Q20

Is no effect credible (power) or not testable with this data? Which data would make it testable?

```json
{
  "answer_from": "lessons 51, 55; STUCK_CHECK 12, 15",
  "answer_names": "the smallest effect this sample can show, or the missing data",
  "applies": "Curator condition: Ask what the declared test/data can resolve and what is unmeasurable; cite applicable sensitivity evidence or identify the missing input. Do not invent power or use a withdrawn kill gate. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q20 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "STUCK_CHECK 15; CURATOR_SHADOW approve",
  "qid": "Q20",
  "question": "Is no effect credible (power) or not testable with this data? Which data would make it testable?",
  "skill": "research-learning-loop (STUCK_CHECK.md)",
  "step": "DECIDE"
}
```

## Q21

What are we missing? Answer the 15 STUCK_CHECK questions, one line each, each naming a file, number or test.

```json
{
  "answer_from": "research-learning-loop/STUCK_CHECK.md 7e677d234468d55d",
  "answer_names": "15 lines",
  "applies": "Curator condition: Answer relevant STUCK_CHECK questions with file, measured quantity or test; mark non-applicable/unanswered explicitly. Checked alone is not evidence; completing this grants no permissions. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q21 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "pro-practice-first 1b; CURATOR_SHADOW approve",
  "qid": "Q21",
  "question": "What are we missing? Answer the 15 STUCK_CHECK questions, one line each, each naming a file, number or test.",
  "skill": "pro-practice-first 1b; research-learning-loop",
  "step": "EVERY ROUND"
}
```

## Q22

Have I walked every step to the end on paper, and can every command run on my route (queue, bridge, allow-list)?

```json
{
  "answer_from": "PROCESS_V7 steps 1 and 2 (2 SMOKE is CANDIDATE); CURATED_V7 K22 (K23 merged), K32, K33 (carried by SMOKE) and K34 (CANDIDATE); SMOKE lessons P5_p5a.tsv 69b4a065a41d4c16; LESSONS_SCOUT_V1 rows 1 and 11; ALARM_ONBOARD_V1 gaps 1 and 3",
  "answer_names": "the DRY_WALK receipt",
  "applies": "Curator condition: Before this desk trial walk required steps and check named dependencies/admission on paper. Record the receipt and unresolved paths; do not execute unauthorized commands or treat the walk as runtime acceptance. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q22 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "LESSONS_SCOUT_V1 rows 1, 11; CURATOR_SHADOW approve",
  "qid": "Q22",
  "question": "Have I walked every step to the end on paper, and can every command run on my route (queue, bridge, allow-list)?",
  "skill": "none",
  "step": "DRY_WALK"
}
```

## Q23

Which question would have caught this earlier? Which question had no source? Which question cost time and changed nothing?

```json
{
  "answer_from": "START_V7.md section 5",
  "answer_names": "question_missing, question_unanswered, question_useless debrief lines",
  "applies": "Curator condition: Record missing, unanswered and useless questions with evidence at close. Keep proposed library changes SHADOW pending independent review and paired promotion testing; debrief alone proves no improvement. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-CUR2-Q23 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 776c4f6c3b8587f1",
  "kind": "SHADOW_QUESTION",
  "origin": "pro-practice-first 1b (debrief); CURATOR_SHADOW approve",
  "qid": "Q23",
  "question": "Which question would have caught this earlier? Which question had no source? Which question cost time and changed nothing?",
  "skill": "pro-practice-first 1b",
  "step": "CLOSE"
}
```

## Q25

SHADOW for the description (curator grouping approve Q0-01, Q1-02, Q5-01): KIND is a description of where an alarm fires, never an edge split. Which unit is labelled and when is its information known (as-of the fire, or AFTER)? What share of fires falls in each kind (own crowding QUIET or CROWDED, position FIRST or LATER) against the share of the declared comparison moments, with UNKNOWNs shown, and what are each kind's fire rate, the matching same-state control rate and the gap under one unit contract, each wave counted once? DECIDE never reads it; no family word; market kinds UNKNOWN. The COPY part moved to Q33.

```json
{
  "answer_from": "team/SCOUT/grouping_loop/GROUPING_V1.md f115a2827e2b357c sections 1, 3 and 4 (playground TEST, not reviewed); CURATED_V7 K36; no released tool prints it yet: mark UNANSWERED when no route runs it",
  "answer_names": "kind shares per alarm with fire rate, same-state control rate and gap, labelled as-of or AFTER, as descriptions; or UNANSWERED",
  "applies": "Curator condition: For a grouping label, which unit is labelled, when is the required information known, and is the proposed use as-of or AFTER? Check the exact unit/clock contract; do not approve a future-informed label for decisions. Do matching control outcome rates differ by the proposed kind, and are fire/control rates and their gap reported under the same unit contract? Do not infer incremental effect from raw fire rates. What share of admitted fires falls in each kind relative to the declared comparison moments, with units and UNKNOWNs shown? Treat this as description, not evidence for an entry/skip rule. | Evidence asked, not adopted: Keep current KIND outputs descriptive and the source finding bounded to this study. Supply independent validation of the pooled correlated-alarm comparison and authorized fresh evidence before adopting a general no-split or activation rule. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "GROUPING_SHADOW_V1 Q0-01, Q1-02, Q5-01 APPROVE_EVIDENCE; L10-01 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 9c061c8c7fd2271e",
  "kind": "SHADOW_QUESTION",
  "origin": "GROUPING_V1 f115a2827e2b357c; team/SCOUT/grouping_loop/QUESTIONS_MISSING.tsv d50bf91224bf0bf3 rows 1, 4, 11 (Q0-01, Q1-02, Q5-01); CURATED_V7 K36",
  "qid": "Q25",
  "question": "SHADOW for the description (curator grouping approve Q0-01, Q1-02, Q5-01): KIND is a description of where an alarm fires, never an edge split. Which unit is labelled and when is its information known (as-of the fire, or AFTER)? What share of fires falls in each kind (own crowding QUIET or CROWDED, position FIRST or LATER) against the share of the declared comparison moments, with UNKNOWNs shown, and what are each kind's fire rate, the matching same-state control rate and the gap under one unit contract, each wave counted once? DECIDE never reads it; no family word; market kinds UNKNOWN. The COPY part moved to Q33.",
  "skill": "none",
  "step": "CLASSIFY"
}
```

## Q26

CANDIDATE (the owner D202611051618_1252 in alarm words, curator not yet seen): where did the alarm work, where did it fail, why didn't it fail more, why didn't it work more?

```json
{
  "answer_from": "the GRADE and TRUE receipts; novelty_v5 output",
  "answer_names": "four lines, each naming a file and a number",
  "applies": "all",
  "decision_ref": "D202611051623_84ee",
  "kind": "CANDIDATE",
  "origin": "the owner D202611051618_1252 (STRATEGY 16:18:47Z), SCOUT 2026-11-05",
  "qid": "Q26",
  "question": "CANDIDATE (the owner D202611051618_1252 in alarm words, curator not yet seen): where did the alarm work, where did it fail, why didn't it fail more, why didn't it work more?",
  "skill": "pro-practice-first 1b",
  "step": "GRADE"
}
```

## Q27

SHADOW (the owner D202611051623_84ee; curator SCO-THINK1 approve): which question about the alarm, the metrics or the approach would have reached the answer sooner, and how should I think differently next time?

```json
{
  "answer_from": "START_V7.md How to think and section 5",
  "answer_names": "better_questions and think_better debrief lines",
  "applies": "Curator condition: At CLOSE, propose a better question about the alarm, metrics or approach and a change in reasoning; name the step, cite the observed issue/evidence and state next time, before X, ask or check Y. Label anticipated benefit as a hypothesis; absent observations stay an explicit evidence gap. No demonstrated speed or performance gain is implied. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO-THINK1-Q27 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 424924a679be364d",
  "kind": "SHADOW_QUESTION",
  "origin": "the owner D202611051623_84ee",
  "qid": "Q27",
  "question": "SHADOW (the owner D202611051623_84ee; curator SCO-THINK1 approve): which question about the alarm, the metrics or the approach would have reached the answer sooner, and how should I think differently next time?",
  "skill": "pro-practice-first 1b",
  "step": "CLOSE"
}
```

## Q28

SHADOW (curator trial C approve): what do the race and the proposed truth label each test, and how will a discordant or UNSURE result limit the claim?

```json
{
  "answer_from": "the card's CLAIM lines; decide_v6 and true_gate words (START_V7 section 4); trial C R10_TRUE.md 3d70517b4db51035, DECIDE_V1.txt 0855ae96554468bb",
  "answer_names": "one line per test: what it tests, and what a discordant or UNSURE result does to the claim, written before outcomes",
  "applies": "Curator condition: At CLAIM, state what the race and proposed truth label each test and predeclare how discordant or UNSURE results limit the claim under the authorized contract. Retain untested mechanism assumptions. | Curator scope: Original external SCOUT trial observations and prospective process questions only; prior CURATOR-derived library efficacy excluded. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO_TRIALC 16a948b081d9fe06:Q1 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS a5957ed6910d77b7",
  "kind": "SHADOW_QUESTION",
  "origin": "trial C RESULT 417b750dc90de109 better_questions (1); CURATOR SCO_TRIALC_SHADOW_V1 approve",
  "qid": "Q28",
  "question": "SHADOW (curator trial C approve): what do the race and the proposed truth label each test, and how will a discordant or UNSURE result limit the claim?",
  "skill": "volat-alarm-design (TRUE grade)",
  "step": "CLAIM"
}
```

## Q29

SHADOW (curator trial C approve): before selecting an idea, which admitted claim files and attempt records name its proposed trigger, and what do the meaningful matches show?

```json
{
  "answer_from": "tried_search_v1.py output (words, then --def); IDEAS_CLAIMED; TRIED rows; trial C thoughts/MAKERTIDE.md a9fe28032f4371b1",
  "answer_names": "the matching claim files and TRIED rows with their ids and what each shows; a code search alone is not novelty",
  "applies": "Curator condition: Before selecting an idea, ask which admitted claim files and attempt records name its proposed trigger, then inspect meaningful matches. A code search alone does not establish novelty or current metric fitness. | Curator scope: Original external SCOUT trial observations and prospective process questions only; prior CURATOR-derived library efficacy excluded. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO_TRIALC 16a948b081d9fe06:Q2 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS a5957ed6910d77b7",
  "kind": "SHADOW_QUESTION",
  "origin": "trial C RESULT 417b750dc90de109 better_questions (2); CURATOR SCO_TRIALC_SHADOW_V1 approve",
  "qid": "Q29",
  "question": "SHADOW (curator trial C approve): before selecting an idea, which admitted claim files and attempt records name its proposed trigger, and what do the meaningful matches show?",
  "skill": "research-learning-loop (loop_find.py)",
  "step": "IDEA"
}
```

## Q30

SHADOW (curator trial C approve): what are the declared directional statistic's chosen-side, opposite-side and matched-control components by month, with exact definitions and unrounded values?

```json
{
  "answer_from": "the GRADE output, unrounded; trial C R09_GRADE.md 2fa94f69adc06ef3",
  "answer_names": "three components by month, unrounded, with their definitions; no decomposition or mechanism from rounded summaries",
  "applies": "Curator condition: At GRADE, ask for the declared directional statistic's chosen-side, opposite-side and matched-control components by month, with exact definitions and unrounded values. Do not assert an arithmetic decomposition or volatility mechanism from rounded summaries. | Curator scope: Original external SCOUT trial observations and prospective process questions only; prior CURATOR-derived library efficacy excluded. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "SCO_TRIALC 16a948b081d9fe06:Q3 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS a5957ed6910d77b7",
  "kind": "SHADOW_QUESTION",
  "origin": "trial C RESULT 417b750dc90de109 better_questions (3); CURATOR SCO_TRIALC_SHADOW_V1 approve",
  "qid": "Q30",
  "question": "SHADOW (curator trial C approve): what are the declared directional statistic's chosen-side, opposite-side and matched-control components by month, with exact definitions and unrounded values?",
  "skill": "none",
  "step": "GRADE"
}
```

## Q31

SHADOW, only when the task reviews an own-evidence admission check (curator DT1 approve): Which real object from another owner could pass this check?

```json
{
  "answer_from": "team/SCOUT/loop_day_20261105/review_dt1/REVIEW_DT1_SCOUT.md b4c482387ebc860e; CURATED_V7 K39",
  "answer_names": "the object, the ownership relation, the expected and the observed refusal reason, and a passing same-shape control",
  "applies": "Curator condition: Before assessing an own-evidence admission check, ask which existing object from another child or owner has a valid shape and digest yet must be refused. Name the object, ownership relationship and expected refusal. | Curator scope: Ownership/evidence admission testing like this external native-debrief witness; not a universal requirement for every mutant set and not an empirical improvement claim. | Not an alarm-finding step. Documentary evidence verified independently by CURATOR; no rerun, code edits, code acceptance, automatic native rule approval, proposal-quality guarantee or market claim.",
  "decision_ref": "SCO_DT1 DT1-Q1 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 91e4dbc4dde76714",
  "kind": "SHADOW_QUESTION",
  "origin": "REVIEW_DT1_SCOUT b4c482387ebc860e; CURATOR SCO_DT1_PROPOSALS_SHADOW_V1 approve",
  "qid": "Q31",
  "question": "SHADOW, only when the task reviews an own-evidence admission check (curator DT1 approve): Which real object from another owner could pass this check?",
  "skill": "none",
  "step": "TOOL_REVIEW"
}
```

## Q32

SHADOW, only when the task reviews an own-evidence admission check (curator DT1 approve): Does the check refuse for the reason it names, and does a control with the same shape pass?

```json
{
  "answer_from": "team/SCOUT/loop_day_20261105/review_dt1/REVIEW_DT1_SCOUT.md b4c482387ebc860e; CURATED_V7 K39",
  "answer_names": "the object, the ownership relation, the expected and the observed refusal reason, and a passing same-shape control",
  "applies": "Curator condition: For the ownership/evidence refusal case, record the expected reason, the observed reason and a passing own-owner control of comparable shape; preserve evidence of no unintended write. | Curator scope: Ownership/evidence admission testing like this external native-debrief witness; not a universal requirement for every mutant set and not an empirical improvement claim. | Not an alarm-finding step. Documentary evidence verified independently by CURATOR; no rerun, code edits, code acceptance, automatic native rule approval, proposal-quality guarantee or market claim.",
  "decision_ref": "SCO_DT1 DT1-Q2 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 91e4dbc4dde76714",
  "kind": "SHADOW_QUESTION",
  "origin": "REVIEW_DT1_SCOUT b4c482387ebc860e; CURATOR SCO_DT1_PROPOSALS_SHADOW_V1 approve",
  "qid": "Q32",
  "question": "SHADOW, only when the task reviews an own-evidence admission check (curator DT1 approve): Does the check refuse for the reason it names, and does a control with the same shape pass?",
  "skill": "none",
  "step": "TOOL_REVIEW"
}
```

## Q33

SHADOW (curator grouping approve Q2-03, L0-04, L8-02): beside the novelty_v5 word, what are the raw overlap with the declared comparator and the containment in both directions (wave counts, definition, source version), and can the measure tell one-way containment from a mutual near-copy?

```json
{
  "answer_from": "novelty_v5 output on the GRADE fire list; CURATED_V7 K40, K41 and K38",
  "answer_names": "raw overlap and containment both ways as descriptions; the COPY, NEAR, NEW word only from novelty_v5",
  "applies": "Curator condition: Can the declared similarity measure distinguish one-way containment from mutual near-copy, including reverse direction and shared-state controls? No threshold or label is accepted solely by posing this question. | Raw overlap never gives SAME or COPY alone (L0-04); nesting is descriptive (L8-02); SUBSET is not a kit word (L2-05 REQUEST_EVIDENCE) | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "GROUPING_SHADOW_V1 Q2-03 APPROVE_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 9c061c8c7fd2271e",
  "kind": "SHADOW_QUESTION",
  "origin": "team/SCOUT/grouping_loop/QUESTIONS_MISSING.tsv d50bf91224bf0bf3 row 8 (Q2-03); CURATOR GROUPING_SHADOW_V1 approve",
  "qid": "Q33",
  "question": "SHADOW (curator grouping approve Q2-03, L0-04, L8-02): beside the novelty_v5 word, what are the raw overlap with the declared comparator and the containment in both directions (wave counts, definition, source version), and can the measure tell one-way containment from a mutual near-copy?",
  "skill": "none",
  "step": "NOVELTY"
}
```

## Q34

SHADOW (curator grouping approve Q12-01): does a declared wave hold both push sides, under a stated descriptive definition, and what does that imply for aggregation?

```json
{
  "answer_from": "the GRADE fire list by wave; CURATED_V7 K42",
  "answer_names": "the mixed-side share with its definition, as a description; never read as several events or a new grade unit",
  "applies": "Curator condition: Does the declared wave contain mixed sides under a stated descriptive definition, and what does that imply for aggregation? Do not equate mixed sides with multiple events or change a grade unit without separate evidence. | SHADOW checklist for the pinned ALARM_V1_21_16 or documented SCOUT desk route only, when its named step applies. User laws, active brief and current installed contract take precedence. Historical numerical examples are attributed source observations, not independently rerun results. No data-access, execution, adoption or publication authority.",
  "decision_ref": "GROUPING_SHADOW_V1 Q12-01 APPROVE_EVIDENCE; L12-01 REQUEST_EVIDENCE; SHADOW_NOT_ADOPTED; AWAITING_INDEPENDENT_REVIEW; mandatory=false; DECISIONS 9c061c8c7fd2271e",
  "kind": "SHADOW_QUESTION",
  "origin": "team/SCOUT/grouping_loop/QUESTIONS_MISSING.tsv d50bf91224bf0bf3 row 15 (Q12-01); CURATOR GROUPING_SHADOW_V1 approve; SOURCE_FLAGS L12_NUMERIC_AND_MEANING (source numbers not copied)",
  "qid": "Q34",
  "question": "SHADOW (curator grouping approve Q12-01): does a declared wave hold both push sides, under a stated descriptive definition, and what does that imply for aggregation?",
  "skill": "none",
  "step": "GRADE"
}
```

## Q35

CANDIDATE (the owner D202611051715_388c, in alarm words): in which months and events of the brief's window does the alarm work and in which does it fail, what do the good fires share that is known at the fire, and does that state, cut on earlier months only (at most 2 readings, 3 states), pick the good fires on later months of the same window?

```json
{
  "answer_from": "the GRADE output by month; the TRUE output; hb/STRATEGY.txt line 2439 (line sha16 1c4bdf0fe4f529d3)",
  "answer_names": "the alarm when state S, or no state found, each with its file and number; months only inside the brief's window",
  "applies": "A question, not a rule: it opens no month; later months means later months inside the brief's window | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051715_388c (STRATEGY ACK of OWNER_CONDITIONAL_LOOPS_V1 51824f9f7b460d9d, 2026-11-05T17:28:31Z)",
  "kind": "CANDIDATE",
  "origin": "the owner D202611051715_388c relayed by STRATEGY 2026-11-05T17:15:52Z (not a row of team/SCOUT/DECISIONS.tsv 208a70f8618555c5 (21 lines read; only D202611051623_84ee of today's loop rules is there): words from the STRATEGY board line that relays it); SCOUT 2026-11-05",
  "qid": "Q35",
  "question": "CANDIDATE (the owner D202611051715_388c, in alarm words): in which months and events of the brief's window does the alarm work and in which does it fail, what do the good fires share that is known at the fire, and does that state, cut on earlier months only (at most 2 readings, 3 states), pick the good fires on later months of the same window?",
  "skill": "pro-practice-first 1b",
  "step": "GRADE"
}
```

## Q36

CANDIDATE (the owner D202611051654_978d): does the definition fire after a fixed wait (x minutes after the moment) with no reason behind it? A delayed fire needs its own reason: a reading known at the fire second that says why waiting helps (for example the forced selling still running).

```json
{
  "answer_from": "DEF.json fields in market words (Q12); hb/STRATEGY.txt line 2433 (line sha16 2a2a8993a7d859d8)",
  "answer_names": "NO FIXED WAIT, or the wait with the reading known at the fire second that justifies it",
  "applies": "A question, not a rule | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051654_978d (STRATEGY ACK of OWNER_FIXED_WAIT_LESSON_V1 2ac82b666d8a5947, 2026-11-05T17:28:31Z)",
  "kind": "CANDIDATE",
  "origin": "the owner D202611051654_978d relayed by STRATEGY 2026-11-05T16:54:48Z (not a row of team/SCOUT/DECISIONS.tsv 208a70f8618555c5 (21 lines read; only D202611051623_84ee of today's loop rules is there): words from the STRATEGY board line that relays it); SCOUT 2026-11-05",
  "qid": "Q36",
  "question": "CANDIDATE (the owner D202611051654_978d): does the definition fire after a fixed wait (x minutes after the moment) with no reason behind it? A delayed fire needs its own reason: a reading known at the fire second that says why waiting helps (for example the forced selling still running).",
  "skill": "none",
  "step": "DEFINE"
}
```

## Q37

CANDIDATE (the owner D202611051811_277c): does a reading flip meaning between periods? Then the flip is the finding to explain: the next round asks why (who is forced; are forced traders left or has the flush happened: open interest built up, funding, liquidations already done, how far the market ran), turns it into a state known at the fire, and tests reading plus state on later months of the brief's window.

```json
{
  "answer_from": "the GRADE output by month; hb/STRATEGY.txt line 2467 (line sha16 ba90a669589f7007)",
  "answer_names": "the flip with its months inside the window and its candidate explanations, or NO FLIP",
  "applies": "A question, not a rule: it opens no month | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051811_277c (STRATEGY ACK of OWNER_FLIP_LESSON_V1 9e64cdfae90951e4, 2026-11-05T18:21:36Z)",
  "kind": "CANDIDATE",
  "origin": "the owner D202611051811_277c relayed by STRATEGY 2026-11-05T18:11:56Z (not a row of team/SCOUT/DECISIONS.tsv 208a70f8618555c5 (21 lines read; only D202611051623_84ee of today's loop rules is there): words from the STRATEGY board line that relays it); SCOUT 2026-11-05",
  "qid": "Q37",
  "question": "CANDIDATE (the owner D202611051811_277c): does a reading flip meaning between periods? Then the flip is the finding to explain: the next round asks why (who is forced; are forced traders left or has the flush happened: open interest built up, funding, liquidations already done, how far the market ran), turns it into a state known at the fire, and tests reading plus state on later months of the brief's window.",
  "skill": "pro-practice-first 1b",
  "step": "GRADE"
}
```

## Q38

CANDIDATE (trial D SCT-D1 better_questions 1; MERGE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf into the existing metric-admission question; never blocking): do the cards of my moment's codes (metric_brief_v2 MAY USE, NEVER READ AS) allow the reading the moment needs?

```json
{
  "answer_from": "metric_brief_v2 output for every code the moment names, quoted in the CLAIM receipt",
  "answer_names": "each code with its MAY USE and NEVER READ AS lines, and YES or NO for the reading the moment needs",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); MERGE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf into the existing metric-admission question; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialD/work/RESULT_SCT-D1_TRIALD.md 1c42dc40b107bb8b better_questions (1); evidence team/SCOUT/loop_pilot_20261105/trialD/work/R06_DEFINE.md 14ea69dbb2cb9fc8, team/SCOUT/loop_pilot_20261105/trialD/work/METRIC_BRIEF_V1.txt 3b3141e2a38ab8d0; events 32803a8e, 58a6a796, fcf046c7 (named by brief SCO-A54; not re-read)",
  "qid": "Q38",
  "question": "CANDIDATE (trial D SCT-D1 better_questions 1; MERGE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf into the existing metric-admission question; never blocking): do the cards of my moment's codes (metric_brief_v2 MAY USE, NEVER READ AS) allow the reading the moment needs?",
  "skill": "-",
  "step": "CLAIM"
}
```

## Q39

CANDIDATE (trial D SCT-D1 better_questions 2; APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf (ask for exact end-to-end admission; runtime refusal and a new route not proven); CANDIDATE until GPT or STRATEGY select it; never blocking): TRUE label, checked again at SEAL: does the installed TRUE route admit, end to end, the label format that measures the mechanism directly? (trial D: code_by_side is in true_gate_v1's format but true_gate_v3 lines 184-186 need activity.code equal to label.code, so it is refused)

```json
{
  "answer_from": "true_gate_v3 label rules and the TRUE route of the DRY_WALK",
  "answer_names": "the label format, YES or NO with the refusing line, and the label used instead",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf (ask for exact end-to-end admission; runtime refusal and a new route not proven); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialD/work/RESULT_SCT-D1_TRIALD.md 1c42dc40b107bb8b better_questions (2); evidence team/SCOUT/loop_pilot_20261105/trialD/work/R05_CLAIM.md eb3c0360533ae7ca, event 915ded288d6b3130; events 32803a8e, 58a6a796, fcf046c7 (named by brief SCO-A54; not re-read)",
  "qid": "Q39",
  "question": "CANDIDATE (trial D SCT-D1 better_questions 2; APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf (ask for exact end-to-end admission; runtime refusal and a new route not proven); CANDIDATE until GPT or STRATEGY select it; never blocking): TRUE label, checked again at SEAL: does the installed TRUE route admit, end to end, the label format that measures the mechanism directly? (trial D: code_by_side is in true_gate_v1's format but true_gate_v3 lines 184-186 need activity.code equal to label.code, so it is refused)",
  "skill": "-",
  "step": "CLAIM"
}
```

## Q40

CANDIDATE (trial D SCT-D1 better_questions 3; APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf as an exploratory question, not a causal explanation or a validated state split; CANDIDATE until GPT or STRATEGY select it; never blocking): in the month the race fails, is the mechanism label weaker too, and if not, which state known at the fire separates the months? (trial D: Dec 2025 race FADE 2c<1c 15m +1.3 while the TRUE gap +0.239 was the strongest, as its RESULT file reports)

```json
{
  "answer_from": "the GRADE output by month and the TRUE output by month",
  "answer_names": "the race and the label by month, and the candidate state known at the fire, or NO SPLIT",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf as an exploratory question, not a causal explanation or a validated state split; CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialD/work/RESULT_SCT-D1_TRIALD.md 1c42dc40b107bb8b better_questions (3); evidence team/SCOUT/loop_pilot_20261105/trialD/work/R10_GRADE.md 3fc6849787a8588a, team/SCOUT/loop_pilot_20261105/trialD/work/R11_TRUE.md 0efcdb8483b5ac7e; events 32803a8e, 58a6a796, fcf046c7 (named by brief SCO-A54; not re-read)",
  "qid": "Q40",
  "question": "CANDIDATE (trial D SCT-D1 better_questions 3; APPROVE_EVIDENCE by curator SCO_TRIALD_SHADOW_V1 a1ed41f475b0efbf as an exploratory question, not a causal explanation or a validated state split; CANDIDATE until GPT or STRATEGY select it; never blocking): in the month the race fails, is the mechanism label weaker too, and if not, which state known at the fire separates the months? (trial D: Dec 2025 race FADE 2c<1c 15m +1.3 while the TRUE gap +0.239 was the strongest, as its RESULT file reports)",
  "skill": "-",
  "step": "GRADE,TRUE"
}
```

## Q41

CANDIDATE (parts wave 3; curator not yet seen; never blocking): when wave counts by month differ across COUNT, GRADE and TRUE, name the filter that removed them before reading the result.

```json
{
  "answer_from": "the COUNT, GRADE and TRUE outputs by month",
  "answer_names": "waves by month in each of the three, and the filter that removed each difference, or NO DIFFERENCE",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "SCOUT 2026-11-05 parts wave 3; curator not yet seen",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/parts_w3/PARTS_W3.md e757ced68a008a18; findings team/SCOUT/loop_pilot_20261105/parts_w3/out/P3_p3a.md c5c0cf93c1b48981 and team/SCOUT/loop_pilot_20261105/parts_w3/out/P3_p3b.md e3c0d17200ecbea0 (what_surprised and better_questions 1)",
  "qid": "Q41",
  "question": "CANDIDATE (parts wave 3; curator not yet seen; never blocking): when wave counts by month differ across COUNT, GRADE and TRUE, name the filter that removed them before reading the result.",
  "skill": "-",
  "step": "TRUE,NOVELTY"
}
```

## Q42

CANDIDATE (trial E SCT-E1 better_questions 1; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv E-BQ1; never blocking): which coins fire most, and are they coins that trend all day (where a stretch against the coin's own day is momentum, not exhaustion)? (trial E: the five coins that fire most were the worst for the fade, 15m +5.6 with them and +8.1 without, as its GRADE card prints)

```json
{
  "answer_from": "the COUNT fire list by coin when a released tool prints it; else UNANSWERED at COUNT (trial E COUNT_V1.tsv prints coins per month, not fires per coin) and, after GRADE, the GRADE card line all against without top-5 coins",
  "answer_names": "the top-5 coins with their share of fires, or UNANSWERED with the step it waits for; after GRADE the all and without top-5 coins numbers",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A95 ADOPT (team/SCOUT/loop_day_20261105/curator_ef/CURATED_EF.tsv E-BQ1); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialE/work/RESULT_SCT-E1_TRIALE.md 6bda8ef5c81c1558 better_questions (1); evidence team/SCOUT/loop_pilot_20261105/trialE/work/GRADE_CARD_V1.txt 7928245bd0eb4bfd line 52 (job 20270006), team/SCOUT/loop_pilot_20261105/trialE/work/COUNT_V1.tsv cac362461cb4f807 (job 20270003); trial F GRADE card 619a0553d108b451 line 52 shows no such effect (+3.0 against +2.7)",
  "qid": "Q42",
  "question": "CANDIDATE (trial E SCT-E1 better_questions 1; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv E-BQ1; never blocking): which coins fire most, and are they coins that trend all day (where a stretch against the coin's own day is momentum, not exhaustion)? (trial E: the five coins that fire most were the worst for the fade, 15m +5.6 with them and +8.1 without, as its GRADE card prints)",
  "skill": "-",
  "step": "COUNT"
}
```

## Q43

CANDIDATE (trial E SCT-E1 better_questions 2; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv E-BQ2; never blocking): does the TRUE label's mirror (same code, window and age, opposite test) also rise at equally busy moments, so the label reads activity rather than the mechanism? (trial E: claim +0.214, mirror +0.142, claim minus mirror +0.072 with interval -0.001..+0.141, busy match gap +0.093)

```json
{
  "answer_from": "before data: the label definition and How to think 9 (which assumption the label measures); after GRADE: this task's TRUE output, its DIFFERENCE claim minus mirror and busy match lines; never earlier tasks' outcomes",
  "answer_names": "the label and its mirror, YES, NO or UNKNOWN before data with the reason, and after TRUE the claim, mirror and busy-match numbers with their file and sha16",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A95 ADOPT (team/SCOUT/loop_day_20261105/curator_ef/CURATED_EF.tsv E-BQ2); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialE/work/RESULT_SCT-E1_TRIALE.md 6bda8ef5c81c1558 better_questions (2); evidence team/SCOUT/loop_pilot_20261105/trialE/work/TRUE_V1_LOG_20270008.txt c84a6a45ff7f0313 lines 117 and 124 (job 20270008)",
  "qid": "Q43",
  "question": "CANDIDATE (trial E SCT-E1 better_questions 2; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv E-BQ2; never blocking): does the TRUE label's mirror (same code, window and age, opposite test) also rise at equally busy moments, so the label reads activity rather than the mechanism? (trial E: claim +0.214, mirror +0.142, claim minus mirror +0.072 with interval -0.001..+0.141, busy match gap +0.093)",
  "skill": "-",
  "step": "CLAIM"
}
```

## Q44

CANDIDATE (trial F SCT-F1 better_questions 1; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv F-BQ1; the rule itself is PROCESS_V10 step 8): does the card carry the FOR THE CARD true_label= and true_mirror= line of the true_gate_v3 check before the VARIANTS row and the ledger prereg seal it? (trial F: printed by the check job, not copied; TRUE refused TRUE LABEL NOT SEALED and the task closed with TRUE none)

```json
{
  "answer_from": "grep -c -F of the true_label hash in the card, run in the command that writes the SEAL receipt (PROCESS_V10 step 8)",
  "answer_names": "the card_true_label line: the hash and its count in the card; 0 stops the seal",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A95 ADOPT (team/SCOUT/loop_day_20261105/curator_ef/CURATED_EF.tsv F-BQ1); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialF/work/RESULT_SCT-F1_TRIALF.md 62878dd639e74da9 better_questions (1); evidence team/SCOUT/loop_pilot_20261105/trialF/work/KITQ_TRUE_DRY1.txt 389bad00e2fb035d, team/SCOUT/loop_pilot_20261105/trialF/work/RELWAIT_TGCHECK2.txt dc113236f9e8f0db (job 20270023)",
  "qid": "Q44",
  "question": "CANDIDATE (trial F SCT-F1 better_questions 1; curator SHADOW SCO-A95 ADOPT, CURATED_EF.tsv F-BQ1; the rule itself is PROCESS_V10 step 8): does the card carry the FOR THE CARD true_label= and true_mirror= line of the true_gate_v3 check before the VARIANTS row and the ledger prereg seal it? (trial F: printed by the check job, not copied; TRUE refused TRUE LABEL NOT SEALED and the task closed with TRUE none)",
  "skill": "-",
  "step": "SEAL"
}
```

## Q45

CANDIDATE (trial F SCT-F1 better_questions 2; curator SHADOW SCO-A95 ADOPT with the step moved from CLAIM to SEAL, where true_gate_v3 check prints the hash; CURATED_EF.tsv F-BQ2; never blocking): is this TRUE label (its true_label hash) already in the VARIANTS register for an earlier idea? Then name that idea and its TRUE row word, and say what this claim adds (trial F: MIDJOLT's OICLOSE5 label has the hash of trial D's WICKBACK label)

```json
{
  "answer_from": "the true_label hash printed by the true_gate_v3 check against the VARIANTS register rows of the run",
  "answer_names": "NONE, or the earlier idea, its TRUE row word and what this claim adds",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A95 ADOPT (team/SCOUT/loop_day_20261105/curator_ef/CURATED_EF.tsv F-BQ2); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialF/work/RESULT_SCT-F1_TRIALF.md 62878dd639e74da9 better_questions (2); evidence team/SCOUT/loop_pilot_20261105/trialF/work/RELWAIT_TGCHECK2.txt dc113236f9e8f0db (job 20270023); team/RESEARCH/ALARM_DESIGN/runs/SCOUT_20261105/registers/VARIANTS.tsv 2757dc5b1564c026 lines 4 (WICKBACK) and 6 (MIDJOLT)",
  "qid": "Q45",
  "question": "CANDIDATE (trial F SCT-F1 better_questions 2; curator SHADOW SCO-A95 ADOPT with the step moved from CLAIM to SEAL, where true_gate_v3 check prints the hash; CURATED_EF.tsv F-BQ2; never blocking): is this TRUE label (its true_label hash) already in the VARIANTS register for an earlier idea? Then name that idea and its TRUE row word, and say what this claim adds (trial F: MIDJOLT's OICLOSE5 label has the hash of trial D's WICKBACK label)",
  "skill": "-",
  "step": "SEAL"
}
```

## Q46

CANDIDATE (trials G and H better_questions 1; curator SHADOW SCO-A121 ADOPT merged, CURATED_GH.tsv G-BQ1 and H-BQ1; never blocking): which actor does the claim say takes the other side (a taker who buys or sells, or a resting order that absorbs), which TRUE label family reads that actor and is left free by the trigger, and which of its coin codes are pickable YES on METRIC_MENU_V2 and carry a sign? Name the code, or MENU EXCEPTION and why when none is (trials G and H both used TAKEROPP15, one true_label hash, and both read NOT SUPPORTED)

```json
{
  "answer_from": "the claim's own words, true_gate_v3 SOURCE_FAMILIES_V1.tsv and KIT_V5/METRIC_MENU_V2.tsv pickable YES, before any data (How to think 9)",
  "answer_names": "the actor, the family, the code with its sign, or MENU EXCEPTION with why",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A121 ADOPT (team/SCOUT/loop_day_20261105/curator_gh/CURATED_GH.tsv 8ac1e5981bf5a064 G-BQ1 H-BQ1); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialG/work/RESULT_SCT-G1_TRIALG.md 13d88d686283583d better_questions (1); team/SCOUT/loop_pilot_20261105/trialH/work/RESULT_SCT-H1_TRIALH.md 98d1870a49b24907 better_questions (1); evidence in CURATED_GH.tsv rows G-BQ1 and H-BQ1",
  "qid": "Q46",
  "question": "CANDIDATE (trials G and H better_questions 1; curator SHADOW SCO-A121 ADOPT merged, CURATED_GH.tsv G-BQ1 and H-BQ1; never blocking): which actor does the claim say takes the other side (a taker who buys or sells, or a resting order that absorbs), which TRUE label family reads that actor and is left free by the trigger, and which of its coin codes are pickable YES on METRIC_MENU_V2 and carry a sign? Name the code, or MENU EXCEPTION and why when none is (trials G and H both used TAKEROPP15, one true_label hash, and both read NOT SUPPORTED)",
  "skill": "-",
  "step": "CLAIM"
}
```

## Q47

CANDIDATE (trial G better_questions 2 and process_change; curator SHADOW SCO-A121 ADOPT, CURATED_GH.tsv G-BQ2 and G-PC1; never blocking): does one market-wide wave carry a month? Read max_fires_in_a_wave by month in the COUNT receipt and name the month whose biggest wave is far above the others; after GRADE, would the race survive without that month: quote the REAL_V1 month leads as printed, never a lead recomputed by hand (trial G: one month's wave carried the whole 15m lead and decide_v6 counted 1 of 4 months passing)

```json
{
  "answer_from": "the COUNT receipt (max_fires_in_a_wave by month) at COUNT; the GRADE REAL_V1 month columns after GRADE",
  "answer_names": "NONE, or the month, its biggest wave against the others, and the REAL_V1 month leads as printed",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A121 ADOPT (team/SCOUT/loop_day_20261105/curator_gh/CURATED_GH.tsv 8ac1e5981bf5a064 G-BQ2 G-PC1); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialG/work/RESULT_SCT-G1_TRIALG.md 13d88d686283583d better_questions (2) and process_change; evidence in CURATED_GH.tsv rows G-BQ2 and G-PC1",
  "qid": "Q47",
  "question": "CANDIDATE (trial G better_questions 2 and process_change; curator SHADOW SCO-A121 ADOPT, CURATED_GH.tsv G-BQ2 and G-PC1; never blocking): does one market-wide wave carry a month? Read max_fires_in_a_wave by month in the COUNT receipt and name the month whose biggest wave is far above the others; after GRADE, would the race survive without that month: quote the REAL_V1 month leads as printed, never a lead recomputed by hand (trial G: one month's wave carried the whole 15m lead and decide_v6 counted 1 of 4 months passing)",
  "skill": "-",
  "step": "COUNT"
}
```

## Q48

CANDIDATE (trial H better_questions 2; curator SHADOW SCO-A121 ADOPT, CURATED_GH.tsv H-BQ2; never blocking): which registry alarm fires in the same half hours? Before the GRADE, as an indication only, run novelty_v5 on the hand check's --out fire list (INSTALL/AGENTS.md line 45); the NOVELTY word stays the one of step 12 on the GRADE fire list (trial H found NEAR AD8_WAVEEND_WE3 only after GRADE)

```json
{
  "answer_from": "novelty_v5 on the hand check --out fire list, an indication only (INSTALL/AGENTS.md line 45)",
  "answer_names": "NONE, or the alarm id with its waves near and excess, marked indication",
  "applies": "A question, not a rule: it blocks nothing | Library scope: not adopted, mandatory=false; owner laws and the active brief take precedence.",
  "decision_ref": "D202611051623_84ee (PROPOSE lines); curator SHADOW SCO-A121 ADOPT (team/SCOUT/loop_day_20261105/curator_gh/CURATED_GH.tsv 8ac1e5981bf5a064 H-BQ2); CANDIDATE until GPT or STRATEGY select it; never blocking",
  "kind": "CANDIDATE",
  "origin": "team/SCOUT/loop_pilot_20261105/trialH/work/RESULT_SCT-H1_TRIALH.md 98d1870a49b24907 better_questions (2); evidence in CURATED_GH.tsv row H-BQ2",
  "qid": "Q48",
  "question": "CANDIDATE (trial H better_questions 2; curator SHADOW SCO-A121 ADOPT, CURATED_GH.tsv H-BQ2; never blocking): which registry alarm fires in the same half hours? Before the GRADE, as an indication only, run novelty_v5 on the hand check's --out fire list (INSTALL/AGENTS.md line 45); the NOVELTY word stays the one of step 12 on the GRADE fire list (trial H found NEAR AD8_WAVEEND_WE3 only after GRADE)",
  "skill": "-",
  "step": "COPY_SEARCH_DEF"
}
```
