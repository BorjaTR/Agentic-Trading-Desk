# RULES TEMPLATE (generic; a pack copies this to RULES.md and fills every {SLOT}; the alarm pack's RULES.md is a filled example)
A pack writes one page, {PACK}/RULES.md: this page with every slot filled. Hunters read only that page. The fixed sections here (Step 0, Before every round, End) are copied into it unchanged.
You run ONE idea through the rounds below and write a card. Paper research only. Files you write: work/CLAIMS.md, work/FORECASTS.tsv, work/MAC_JOBS.tsv, CARD.md, work/RESULT_<run>.md, your job files and work folders, one HOTFIX_LOG row per new fix. Nothing else.

## Read first
1. ops/KNOWLEDGE_BRIEF.md (memory runs only). 2. This page. 3. ops/JOB_SHEET.md (the pack's job sheet) only for exact job commands.

## Months
{MONTHS: design months you may read; held-out months (orchestrator only); closed months}

## Step 0, before choosing the idea
/pro-practice-first and the stuck check (STUCK_CHECK.md), written into CLAIMS as the R0 block in this form (templates/CLAIMS.md), one item a line:
- `R0 pro <1-5> | <line>`: five lines.
- `R0 stuck <n> | <answer>`: one line for EACH question of STUCK_CHECK.md, numbered as there; each answer names a file, a number or a test. Never two questions on one line, a skipped number, "...", "all checked" or "as before"; a question that does not apply: `n/a: <why>`.
- `R0 candidate <k> | <test> | could move: <F or Q id, or new finding> to <status> if <result>`: at least 2 candidates, each with its own could-move field.
- `R0 pick | without step 0: <test> | now: <test> | why: <which result can change which status>`.
Pick the candidate whose result can change a finding's status. A memory run keeps the form; its candidates come from the brief's questions, findings and moves.

## Before every round
1. CLAIMS line: change, why, the F or Q ids it builds on, what result moves which finding; no retry of a REFUTED finding unless you name the difference.
2. FORECASTS line, sealed before the round's first job. Start from the round's base in the brief, named in the note: the finding or move it builds on (its best row and every pass part the brief records for it); with neither, the pack's yardstick. BASE RATES inform p. Forecast every part of the pack's pass rule: in its column where the template has one, the others in the note as `<part> <value>`. p = the chance of passing every part; its note names the parts the base failed and why this round could pass them.
3. A gain over R1 (fitted-change round): the note names the start and the move's mean, `gain from <start> toward move mean <m> (n <k>)`; start 0 when no gain is known, or your last sealed forecast of this move. The forecast moves from the start toward the mean: the mean itself is allowed, the start itself and anything past the mean are not. No move in the brief: shrink toward 0 and say so.
4. A try of a move the brief holds repeats it as filed (same settings; a ladder: every rung), so its n grows; a changed move is a new move.

## The rounds
{ROUNDS: one row per round: question, do (in order), job, pass}
{ROUND_MAP: which of the pack's rounds plays each generic role: select (alarm R1), split (alarm R2), fitted change (alarm R3), placebo (alarm R3P); a role the pack lacks: none}
{CAPS: e.g. fire or trade cap, enforced by the job template}

## Yardsticks
{YARDSTICKS: one per side or per kind, with window and numbers}

## Known data traps
{DATA_TRAPS: every trap found in drills or FAILURES_LOG, with the right way}

## Small scripts
Only when no released tool gives the number; script and saved output in work/scripts/, quoted with sha16; never a shared scratch folder.

## Card
{CARD: template path, answers, NEXT TESTS format; every number with its receipt; words match numbers}

## When something refuses
grep FAILURES_LOG first; a new fix: one HOTFIX_LOG row; two failed tries on one step: stop, BLOCKED with the tool words. Never edit a tool's own output files or another agent's job.

## Never
Grade, assess or curate your own run. Delete anything. Read held-out or closed months. {NEVER_EXTRA}

## End
work/RESULT_<run>.md first line: DONE <utc>, best round and its numbers (every part of the pass rule), then "passed" or "no round passed: <the parts that failed>"; then the card sha16.
