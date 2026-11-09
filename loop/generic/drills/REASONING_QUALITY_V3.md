# REASONING QUALITY V3 (SCOUT 2026-11-08; V3 = V2 + Q5 and Q3 wording from round 2 (C100); V2 = V1 + 5 wording fixes from its first two-scorer round, MESSY M025-M029; V1 agreement alpha 0.895)
Adopted by C224 (8 Nov 2026, ledger G1143) after the L11 two-scorer round (alpha 0.54): one meaning for Q5, Q6 and Q7; on it the L11 scorers agreed 1.00 (L11_CHECKS_SUMMARY K43). Paths to S/drills_v2 below are the alarm seat's, as examples: a seat keeps its copy in its own drills folder.
Why: results can look good by luck; we want the thinking to improve run by run. Scored by a separate scorer agent (never the hunter), from the run's own files (CLAIMS, FORECASTS, CARD, split receipts), with this rubric, every run; written as REASONING rows in the run's ASSESS.tsv and one row per run in drills_v2/registers/DRILL_RUNS.tsv (drill_id REASONING).

## Where the rubric comes from (pro-practice-first; scholarly connectors Scite/alphaXiv are on the account but not in this Mac session, so web sources were used)
- Strong inference (Platt 1964; Chamberlin's multiple working hypotheses 1890/1897): keep several explanations alive and run the test that can exclude one ([Platt 1964 PDF](https://people.csail.mit.edu/ythomas/InterestingArticles/Strong_Inference.pdf); [50 years of strong inference, J Exp Biol](https://cob.silverchair.com/jeb/article/217/8/1202/13095/Fifty-years-of-J-R-Platt-s-strong-inference)).
- Scoring step-by-step reasoning without a reference answer: each step correct (supported by its source) and informative (adds to the conclusion) (ROSCOE, Golovneva et al. 2022, [arXiv 2212.07919](https://arxiv.org/abs/2212.07919); ReCEval, Prasad et al. 2023, [arXiv 2304.10703](https://arxiv.org/pdf/2304.10703)).
- Forecast skill: calibration and sharpness (Brier, interval coverage; already measured, forecast_score.py).

## The rubric (0, 1 or 2 points each; 16 max per run)
| # | item | 2 points | 1 point | 0 |
|---|---|---|---|---|
| Q1 | alternatives (Chamberlin) | the R0 block lists >= 2 candidate tests with the status each could move, and >= 2 live explanations for the mechanism (no R0 block: read the R1 CLAIMS line) | one of the two, or an R1 line naming a rival explanation | neither |
| Q2 | crucial test (Platt) | the chosen test's result can move a status either way, stated before data | stated but one-sided | none |
| Q3 | prediction before data | every round with a job (R1, R2 splits, R3, R3P) has a FORECASTS row before its first job; its starting point (base rate or earlier rounds) is named in that row or in the CLAIMS line of the same round written before the job | rows before the jobs but one round missing, or no starting point named | two or more rounds missing, or a row after its job |
| Q4 | power | R2 power line with the gap needed, and the parent split when needed | gap needed stated only | none |
| Q5 | step correctness (ReCEval) | every cause line on the card (defined in "Q5 in full" below) has a receipt and the t of its own effect | exactly one cause line without | two or more cause lines without |
| Q6 | no overclaim | 0 overclaims (defined in "Q6 in full" below) | 1 | 2 or more |
| Q7 | update after results | all three parts of "Q7 in full" below: forecast vs actual, the status that moved or held, and how the prior moves and why | part (a) and one of (b) or (c) | part (a) missing, or (a) alone |
| Q8 | informativeness (ROSCOE/ReCEval) | NEXT TESTS: each line is decisive (a stated result moves a status) and none repeats a test refuted in the brief the hunter saw | some lines | none |
Read it as: total per run, and its trend across runs (memory runs should rise; compare with controls on Q1-Q4 and Q6, which do not need memory to score).

## Units and the split between Q5, Q6 and Q8 (read first)
- A unit is one sentence (up to a full stop) of the card's prose, or one table cell. Each unit is scored under at most one of Q5 and Q6 (rules below), and a claim written in several units is one claim.
- NEXT TESTS lines are scored under Q8 only. The header lines (idea, why chosen, mechanism, yardstick, parent), the Receipts list, the split-table list and the Rules used line are scored under no item.
- A unit marked QUESTION or HYPOTHESIS, or hedged (likely, may, might, could, suggests, descriptive), is never a cause line and never an overclaim. The mark must be in the unit itself: a reason cell, Learned line or answer stated as fact is charged even when a CAUSES line on the same point says QUESTION (the card then states it two ways).

## Q5 in full (step correctness)
A cause line is a unit that gives a reason for a market result (why a lead, a gap, a month, a state or a round paid what it paid), and is one of:
- a sentence with because, so (meaning "therefore"), or since (meaning "because", not a time);
- a cell of a table column headed reason;
- a CAUSES block line not marked QUESTION.
Not cause lines: a because, so or since that gives the reason for a choice, a rule outcome or a method step (why this test was picked, why there is no t, why a state cannot pass a rule); a reason cell that is empty, only restates its row's numbers, only says its row shows no separation (flat, not stable), only names the mechanism, or only points to a QUESTION line (for example "see CAUSES (a question)"); a colon clause with no marker word.
Each cause line needs both:
- a receipt: a sha16 or file on the unit, or in the CAUSES line or table row that carries the same reading and the same number (the scorer names that line);
- the t of the effect the line claims, on the unit or in another column of the same row. A t of a different effect does not count: the t of a lead against the yardstick is not the t of a step between two rounds, and "no t" or "t=none" is a missing t.
Worked scale:
- 2: every cause line has both. Example: a reason cell "past the median rise the lead halves" in a row whose t column holds the split gap t and whose reading has a CAUSES line with a receipt.
- 1: exactly one cause line lacks a receipt or its own t. Example: one reason cell whose t column says "no t".
- 0: two or more lack one. Example: that cell, plus a Learned sentence "X, so it changed the entries" whose effect has no t anywhere on the card.
A cause line that has both is then read under Q6 for whether its t supports it. A cause line that lacks either is charged here only, never also under Q6 (a cause with no number, or no t, is Q5, not Q6).

## Q6 in full (no overclaim)
An overclaim is a claim stated as fact that its own number does not support. Count each distinct claim once, however many units repeat it.
- A claim is a unit that says more than its numbers: a shape (hump, dial, monotone), where an effect lives or does not live, a cause, a status or a bar result (met, passes, refuted), or a general rule. A unit that lists measured numbers with their t, or says which state had the higher measured lead, is a report, not a claim.
- Its own number does not support it when: the number or its t is under the bar the rules page sets for that kind of claim (a split or state effect: gap t 2.5, HUNTER_RULES_V2 R2; a round, a step or a status: that round's or status's own bar), or the number has the opposite sign to the claim. A claim about a return (lead, gap, month, step, shape across states) whose number has no t is under the bar. A claim about counts (fires, waves, shares cut) is checked against the counts alone.
- A claim of no difference (flat, no separation, not stable) is supported when its t is under the bar; it is an overclaim only when its t is at or over the bar.
- Units scored under Q5 (cause lines lacking a receipt or a t) are not counted here.
- Run with an assessor: read its C2:OVERCLAIM keys in MISTAKES.tsv first as candidates; each key counts when its quoted unit meets this definition; a key whose unit is a cause line lacking its t is moved to Q5; then read the rest of the card for claims the assessor missed. Run with no assessor: read the card alone.
Worked scale:
- 2: no claim stated as fact against its own number. Example: "Q024 met by its own bar (+0.75 at or above +13.3 with t >= 3 on >= 300 waves)" with +15.76, t 5.42, 479 waves.
- 1: one. Example: "a hump above the floor, not a monotone dial" with a split gap t of -2.13 (under 2.5), written in a table cell and again in Learned: one claim.
- 0: two or more. Example: that hump claim, plus "the step lives in the legless set" from a +4.46 step with no t.

## Q7 in full (update after results)
"How the prior moves" requires three parts on the card (answers, Forecasts paragraph, Learned or Verdict):
- (a) forecast vs actual for every round that had a FORECASTS row: the forecast (centre and interval, or p), the actual, and in, out or where in the interval.
- (b) which status moved or held because of the result, named by id (a Q answered, an F status kept or changed, the explanation confirmed or not).
- (c) the prior's move: a sentence that names the prior the run started from (a forecast centre, p, base rate or earlier rounds), says in which direction the result moves it for the next forecast of the same kind (up, down, wider, or unchanged with the reason), and says why by naming the number that moves it. A streak or a lesson that never says what the next forecast should start from is not (c).
Worked scale:
- 2: (a), (b) and (c). Example: "R3 gate built on R2's largest gap lost for the third run (L09 -7.60, L10 -5.87, L11 -6.91): the next R3 gain forecast starts below 0, not near 0 as here (-0.4)".
- 1: (a) and one of (b) or (c). Example: forecasts vs actuals per round plus "Q024 met by its own bar", with no sentence on what the next forecast starts from.
- 0: (a) missing, or (a) alone.

## How to score (every run, after the assessor)
1. A fresh scorer agent reads only the run's CLAIMS.md, FORECASTS.tsv, CARD.md, MISTAKES.tsv and the check_round output, plus this page.
2. It writes REASONING.tsv in the run folder: item, points, the line quoted as evidence. Any item without a quoted line scores 0. For Q5 and Q6 it quotes every unit it charged (Q5: the cause line and what it lacks; Q6: the claim and the number with the bar it misses) and, for a 2, the line "no cause line without" or "no overclaim" with the units it read.
3. The orchestrator adds the total to DRILL_RUNS.tsv (drill_id REASONING) and to the series row.
Back-score L05-L09 once with the same rubric, so the trend starts from real runs.
