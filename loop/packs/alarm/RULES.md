# HUNTER RULES (live page; why: lean_v1/HUNTER_RULES_WHY.md)
You hunt ONE idea in 3 rounds and write a card. Paper only.
Paths: work/, setup/, jobs/, ops/, CARD.md in $RUNF; lean_v1/, build/, drills_v2/ in $S (launch prompt).
Files you write, only: in work/: CLAIMS.md, FORECASTS.tsv, MAC_JOBS.tsv, RESULT_<run>.md, scripts/ (when no tool gives the number); CARD.md, your job files (jobs/ and the queue IN/ copy), your pipe, split and idea folders, setup/INPUT_*.json, the two idea claim files (JOB_SHEET 2), one row in lean_v1/HOTFIX_LOG.tsv per new fix.

## Read first, in this order
1. This page (your run's pinned copy, ops/HUNTER_RULES.md).
2. ops/KNOWLEDGE_BRIEF.md (memory runs only; a control reads "the brief" as this page and the yardsticks).
3. ops/JOB_SHEET.md: the exact job commands. Memory runs also read ops/ADOPTED_RULES.md: binding; on a conflict this page wins (say so in a MESSY line).

## Months
- Design months: Sep 2025 to Jan 2026 (2509-2601). Read only these.
- Feb-Mar 2026: held out: never open, quote or estimate them; only the orchestrator reads them (best round, R3, R3P).
- Apr-Jul 2026: closed.

## Step 0, before choosing the idea
1. /pro-practice-first on "how do professionals choose the next experiment here": 5 lines with links (no plans/ file).
2. Stuck check: ~/.claude/skills/research-learning-loop/STUCK_CHECK.md, one short line per question.
3. Both go in work/CLAIMS.md under "## R0 step 0", with: at least 2 candidate tests and the status each could move; your pick without step 0; your pick now and why.

## Before every round
1. CLAIMS line "R<k> | <utc> |": change, why, the F or Q ids it builds on or tests ("none fits" if none), what result moves which finding. The brief's DO NOT RETRY list (REFUTED findings): retry one only when this line names what differs.
2. FORECASTS row (p_beat_yardstick holds the p below, *_net15 lead15), sealed before the round's first job; base p = k of n similar brief rounds that met this round's pass rule (name the set), lead15 a named brief number (control: yardstick); then adjust (no set size or shrink weight: write yours and why in the row):
   - R1: p(R1 passes all three parts of its rule), lead15 point, 80% interval.
   - R2: per reading, the state you expect to pay more and the gap t you expect.
   - R3 and R3P: p(passes R1's three-part rule, not R3's), lead15, 80% interval, plus gain vs R1, its 80% interval. Shrink R3's gain toward its move kind's MOVES mean (that row's mean when n >= 2, else the brief's pooled mean; control: 0), R3P's toward 0.

## The 3 rounds
| round | question | do | pipe | pass |
|---|---|---|---|---|
| R1 claim | more than the plain move? | mechanism FORCED_OUT or FORCED_OUT_SHORTS, its conditions | --until 6 (COUNT, fire cap), then --until 17 (READINGS for R2) | lead15 minus the same-side yardstick on Sep-Jan >= +2, STEP_11 t15 (vs 0) >= 3, lead15 above the same-side pooled number below (+8.09 or +10.99) in >= 3 of 5 months (STEP_11 by month; a not-counted month stays in the 5, never above) |
| R2 explain | when does it pay more, less, why? | split plan in CLAIMS first: 3 or 4 readings (one own-size; at least one R3P-eligible (Placebo below), never R3's gate), 2 states each, cut at the wave first-fire median, a state >= 50 waves (50-299: runs and counts, cannot pass; R1's split passes only from 600 R1 graded waves in all), a reason each | none for R1's splits; the broad parent's pipe when the power line asks (already graded: split its pipe, no new grade) | abs gap t >= 2.5 at 15 min; 1 h gap and Dec, Jan month gaps of its sign; >= 300 waves a state |
| R3 sharpen | a better alarm from the explanation? | ONE change: a gate from R2 or a tighter own condition | --until 6 (COUNT), then --until 14 | per run: R3 minus R1 > 0, >= 300 graded waves, R1's months part; across runs: R3 minus R3P >= +1, p < 0.10 (orchestrator pools) |

### R2
- Power line in the split plan: gap needed for t 2.5 = 2.5 x sqrt(se1^2 + se2^2), each half's se about R1 se x sqrt(2). Gap needed over 10 points: also split the broad parent (R1 without its added conditions; over the fire cap: keep R1's trigger cut) on every split-plan reading, in one parent pipe, cut at its own wave medians.
- At least one reading is the size of the alarm's OWN condition (e.g. C2.S02's move), even if a REFUTED finding names it: say what differs.
- Cuts: wave medians per split pipe (JOB_SHEET 5); quote each sha16 in the R2 CLAIMS line; then state_split --cuts <median_cut>.

### R3
- State-gate state: one that passed the R2 rule (parent split first, then R1's; several: the largest |gap t|); none passed: the largest |gap t| on R1's split, card: "explanation not confirmed".
- Name at least 2 different candidate moves (the state gate above, tighten the own condition to the R2 own-size state), each with its MOVES base rate (control: 0) and waves after the cut; pick the best expected gain that keeps >= 300 graded waves (R1 under 334: the most waves); say why in the R3 CLAIMS line.
- The cut removes >= 10 pct of R1's graded waves: before filing, estimate: COUNT waves x R1's graded/COUNT ratio; after GRADE the graded share decides. R1 under 334 graded waves (a 10 pct cut leaves under 300): cut anyway; R3 is then "under 300 waves: a question" (R1 under 300: R1 keeps its rule; R3 cannot pass).
- R3 and R3P never gate on a CTX code: a stand-in, pickable YES in METRIC_MENU_V2 (JOB_SHEET 5), same time span (op sum or mean, ranked with op own_pct; level: share rules).
- Placebo R3P beside R3: a gate (its stand-in) on the reading with the smallest |gap t| among R1-split readings not the own condition, not R3's reading, not tied to the lead by any finding (any status), with a stand-in, cut to remove the same share of waves as R3 (within 5 pct points of R1's graded waves; no eligible reading: "no placebo" in CLAIMS and card); its own CLAIMS and FORECASTS lines; --until 14. The card reports R3 minus R1, R3P minus R1, R3 minus R3P.

### Every round
- Fire cap: COUNT (step 06, row month ALL) <= 10,000 before GRADE (step 11). Over: tighten, re-COUNT (JOB_SHEET 2).

## Yardsticks (Sep-Jan, 15 min)
- FORCED_OUT (down-side fades): FDONLY +8.09 (t 3.70, 1235 waves).
- FORCED_OUT_SHORTS (up-side fades): FUONLY +10.99 (t 5.30, 1382 waves).

## Card (CARD.md, from lean_v1/templates/CARD.md)
- The template's 8 answers; works when (state, numbers, reason); fails when; best round; "held on Feb-Mar": write "orchestrator only".
- Every number with its receipt (file + sha16). Words match numbers.
- CAUSES block: each "because", "band", "which waves" or "X failed, not Y" sentence is one line: receipt=<file sha16> number= t= differs_in=<one definition field>. No t, or 2+ fields differ: a question.
- NEXT TESTS: the template's form and its three rules (up to 3 lines).
- Market lines: each names its window and share of coins (or "not known"); skill market-reading-protocol.

## Data traps (check every code before COUNT)
- BTC codes C1.S15-S21 live only on the BTC row (op raw fires on BTC alone, op market is empty): no coin alarm gates on them.
- Market codes (SCOPE market: C2.S02, C8.S06, C1.S22-S24): op market, never op raw. C1.S22-S24 failed the L02 hand check: prefer C2.S02.
- CTX.* readings: for R2 splits only, push-signed (positive = push direction); never a definition input.
- Empty is not 0 (no fire).
- A code whose card says "MEANING NOT YET TESTED" is never a gate.

## When something refuses
- grep lean_v1/FAILURES_LOG.tsv for the words; apply its logged fix to your files or job text; a new fix: one HOTFIX_LOG row. Two failed tries on one step: stop; RESULT first line BLOCKED <utc> with the tool's words, then the REPORT block.
- Never edit a pipeline, STEP, PENDING, TIMES or runner file, or another job.

## Never
Assess or curate your own run, or judge your own card. Delete anything. Put git, sudo, rm, rmdir, dd, sleep, timeout or alarm in job text. Read Feb-Jul numbers.

## End
work/RESULT_<run>.md: first line DONE <utc>, best round (of R1 and R3 the higher lead15; never R3P), lead15, lead minus yardstick, t, waves, months above the same-side pooled number; then the card sha16; then the REPORT block of drills_v2/REPORT_TEMPLATE_V1.md.
