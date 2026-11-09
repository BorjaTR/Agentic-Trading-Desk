# STUCK CHECK: what are we missing? (learning loop, V1.1, 4 Nov 2026; for any project, examples in brackets are volat-agent)
why: the owner 4 Nov 15:51-15:52 Berlin ("This is one thing you need to add to the loop each time. what are we missing?"); research and sources: team/RESEARCH/plans/PLAN_STUCK_CHECKLIST_20261104.md.
When: before every round, one line per question, numbered as here, never merged or skipped (in the learning loop: the `R0 stuck <n>` lines of CLAIMS; elsewhere: the setting's `## What are we missing` section). When the same question has failed 2 rounds in a row, the full write-up goes in the thought file, and the next round must change at least one of: the question, the metric, the groups, the data.
Rule: each answer names a file, a number or a test. "Checked" alone is not an answer.

## A. The question
1. Are we asking the right question? Restate it in one line, differently. What decision does it serve? What easier related question could we solve first? (Polya)
2. Which explanations of the failure are still alive (at least 3)? For each, the one test that would kill it. (Chamberlin; Platt)
3. Premortem: the next round has failed. Write the 3 most likely reasons now. (Klein; Mitchell et al.)

## B. Fundamentals and sides
4. What is the mechanism (who sells, who buys, why the price comes back)? Which side are we not measuring? (the owner 1, 4)
5. What else on this topic did we not look at? Search the record (loop_find.py, THREAD findings) and outside (pro-practice-first). Did we use all the data we hold? (the owner 3; Polya)

## C. Measurement
6. Does each metric mean what its name says: definition read in the tool code, sign, unit, stamp? (the owner 2; Aguinis and Vandenberg; LS47)
7. Is the outcome the right one? Can it show the effect (room to move, comparable across units)? Fixed stops and fixed horizons are not comparable across coins of different volatility. (Kane; Lopez de Prado)
8. Is the data complete and clean: missing rows per month, look-ahead, a constant per unit that fakes a pattern (fixed cost)? (here: June lost in R50, fixed coin cost in R52; Kenett)

## D. Comparisons and groups
9. What do I need to compare, against what: baseline, control, same-size random? (the owner 5)
10. Am I comparing two different kinds of events? Are the things in the same basket comparable (cascade vs lone dump, rally dip vs crash, major vs meme, volatility, cost)? A pooled result can reverse inside groups. (the owner 7, 8; Alin, Simpson's paradox)
11. Are we splitting the data in the right groups: by mechanism, fixed before results, enough independent events per group? (the owner 15:52; Kane)

## E. Signal, noise and more data
12. Is the real signal buried in noise? Count independent units (events, days), not rows. What is the smallest effect this sample can show (power)? (the owner 15:52; McKenzie; Kolari and Pynnonen; Lopez de Prado)
13. How can we get more events? A wider event set (here: alarm-independent sell-offs, 6,651, of which 3,720 cascades), lower thresholds, other venues, forward months. (the owner 6, "we have thousands of cascades")
14. How many tries have we made on this question? Is the bar raised for that (Holm, family null)? (Harvey, Liu, Zhu; Lopez de Prado)

## F. Stop rule
15. Is "no effect" credible (enough power), or is it "not testable with this data"? Then name the data that would make it testable. Five whys on the last failure, down to a process cause. (Favero et al.; Serrat)
