# IDEA_GUIDE_V2: which ideas pass, which fail, and why (SCOUT, 29 Oct 2026, rounds 1 to 3). TEST, NOT REVIEWED.
An opinion built from the runs' POSTMORTEMS rows (the why column) and the registry. Read it before you pick your two ideas
(the owner 29 Oct 19:02 Berlin: "every time they try better ideas and do not waste time on the ideas that have less chance").
Each line names its run; the files are listed under Sources with their sha16.

## 1. What made the new PASSes: a new input that shows a forced trader, and the moment its flow ends
| alarm | new input | who is forced | side, numbers | waves Sep-Dec |
|---|---|---|---|---|
| AD2 OIFLUSH OF1 | open interest falls in its own top 1 pct during a big 10 min move | positions leaving | FADE; the FOLLOW side under random at 1 h in 4 of 4 months (CARD_OF1 FOLLOW 1h -2.7) | 1,485 |
| AD2 HLFLUSH HF1 | the same on Hyperliquid open interest | positions leaving | FADE; FOLLOW 1h -4.9 | 1,351 |
| AD1 FORCEDBREAK FB5 | forced flow over the coin's own 99th pct while the price breaks yesterday's range | liquidated traders at a level | FADE +8.8 at 15m, +5.5 at 1h; FOLLOW +1.5, -3.8 | 897 |
| GPT2 LATEBASIS LB2 | mark premium dislocation while small fills fight large fills | arbitrageurs and late chasers | FADE; LB1 (2,091 fires) R1 only, LB2 with a wider tail (2,919 fires) R2 PASS | 1,391 |
| AD4 SETTLEBACK V3 | the coin's funding settle minute with a payment of 3 bp or more due (Z3.S01, E1.S01) | funding payers who closed into the settle | FADE the payers' closing way: FADE 15m +8.0, 1h +8.4, FOLLOW -5.8, -8.5 (4 of 4 months); LEAD 1h +16.9 (t 4.33), the largest so far; Jan-Apr HELD in 3 of 4 months | 383 graded |
| AD7 PAYERWIN PW1 | a big 10 min move in favour of the side paying an extreme funding estimate (E1.S01) | crowded payers who take the windfall | FADE +4.9 at 15m, +4.7 at 1h; FOLLOW -5.7 at 1h (4 of 4 months); LEAD 1h +11.23 (t 5.81) | 1,499 graded |
| AD9 RUNEND RE2 | a one-sided taker run (B2.S02 own top 0.5 pct within 15 min) with a big 15 min move, at the minute the takers turn (B1.S09) | takers who ran out | FADE 1h +2.0 over random, FOLLOW -2.9 (under random in 4 of 4 months); LEAD 1h +5.62 (t 3.20) | 1,516 |
Pattern: each names a trader who must trade NOW and an input no registry alarm used. In every one the OTHER side lost (FOLLOW under
random at 1 h), not only the lean side won. A scheduled forced trader (a known minute, a known payment) gave the strongest result;
AD4's stricter lines on the same moment (V1 open interest fell, V2 the price footprint) only cut waves (96 and 178).

## 2. What made copies (7 PASSes that do not count)
A filter on a known alarm's fires keeps the same moments: AD3 LF1, LF2, LF3 (the N1 liquidation lines split by market calm), AD2 GA2
(a given idea plus "open interest fell"), AD3 GB2 and PV1 (lone-coin filters), GPT1 FT1 (a 24 h poke plus taker flow = DAYPOKE2).
Rule: a new filter on an old moment is not a new alarm. Start from a moment that a new input makes on its own.

## 3. Why ideas failed: the patterns, with the numbers that show them
| pattern | examples (run, idea, the number) | do instead |
|---|---|---|
| Both sides beat random: the moment marks volatility, not direction | AD1 GB1 thin book: FADE +3.9, FOLLOW +2.9 at 15m; AD2 OB1 open interest building: FADE +4.3, FOLLOW +3.9; AD2 OF2 lone flush: FADE +5.0, FOLLOW +2.2; AD3 AL1 lone run: both near +3 | a big-move line alone is not an alarm: add WHO is forced and WHEN their flow ends, and say in the card why the other side loses |
| A coin moving alone keeps going | AD3 AL1, GB2, PV1 (FOLLOW ahead in every month), AB1 (Nov and Dec the other way) | do not FADE a lone coin move; LONE_COIN_MOVE has 1 PASS or NMM in 6 |
| Too few waves for the t bar (R1 only = NEEDS MORE MONTHS) | AD3 LF1 770 waves, AB2 722; GPT2 AF1 61 to 143 waves a month; GPT2 MT1 4 of 4 months passing but R2 no | aim for 1,000 or more waves Sep-Dec (about 250 a month); a 2nd variant that widens the tail can lift R1 to R2 (GPT2 LB1 to LB2) |
| Small fills alone are weak | GPT2 LC1 LEAD 15m +2.2 (t 0.77), LC2 STOP (2 of 4 months), CE1 STOP (1h -2.4, 0 of 4 months) | retail-size flow is a filter, not a trader who must trade |
| The premise ran the other way | GPT2 CE1 (waiting for small net flow to reverse), AD3 PV1 and AB1 | write in the card what proves it wrong before the grade; a STOP with the other side ahead is not a new alarm for that side either (ASK SCOUT) |
| Memory | AD1 FB1: 47 inputs passed 2 GiB on half B | few inputs; measure the helper first (LEARNINGS V6-06) |
| Pace or volatility alone | AD5 PC1: a cooled volatility jump, FADE +1.0 and FOLLOW +2.7 at 15m (both win) | volatility markers have no side; PC2 (positions leaving during the jump) did fade: +3.8, 4 of 4 months, too few waves |
| A premium gap that arbitrage closes fast | AD6 BJ1 and BJ2: FADE +1.7 and +2.7 at 15m, LEAD +3 in 1 or 2 of 4 months; BJ3 not CLEAR | a premium move needs a forced trader behind it (LB2 had the fill-size conflict) |
| A break of a tested level runs on | AD8 TOUCHBREAK TB1, TB3: FOLLOW 2c<1c 5m +6.0 and +4.6, 15m +4.2 and +2.9, every month; FADE only a small late edge (TB3 1h +1.52) | stops past a tested level are momentum fuel for minutes: never FADE the break itself; fade the failed break (AD8 RECLAIM) |
| A move against a crowd that does not leave comes back | AD7 CROWDHIT CH1 (FOLLOW the squeeze): FADE beat FOLLOW in 4 of 4 months (LEAD 1h -6.33, t -3.30) | when open interest does not fall, expect the move to revert, not a squeeze |
| A market-level premium turn has no side | AD9 PREMTURN PM5: FADE +0.3, FOLLOW +1.9 at 15m | premium speed alone marks activity |
| The rarest version of a good moment is noisier | AD9 RUNEND RE1 (top 0.1 pct): 990 waves, 2 of 4 months; RE2 (top 0.5 pct): 1,516 waves, 4 of 4 | prefer the wider line with more waves |
| Too many fires make a grade too slow to finish in a round | AD8 WAVEEND WE2: 79,543 fires (52 a wave) still grading after 60 min | one coin per wave, a refractory; under about 20,000 fires (V6-37) |

## 4. Decided in rounds 2 and 3 (registry REGISTRY/ALARM_REGISTRY_V1.tsv; every page has the WHY FAILED line)
- Round 2: GPT2 LATEBASIS LB2 PASS (NEW); LATEFILL LC1 NEEDS MORE MONTHS, LC2 STOP; CHASEEND CE1 STOP; MARKETTURN MT1 and AFTERFLUSH AF1
  NEEDS MORE MONTHS. AD4 SETTLEBACK V3 PASS (NEW), V2 NEEDS MORE MONTHS, V1 INSUFFICIENT. AD5 PACECOOL PC2 NEEDS MORE MONTHS, PC1 and PC3
  STOP. AD6 BASISJUMP BJ3 NEEDS MORE MONTHS (not CLEAR), BJ1 and BJ2 STOP. Never graded (agents stopped): HLHOUR (Hyperliquid hourly
  settles, counted: V3 1,117 waves), CALMBREAK, MARKLAG.
- Round 3 (decided by 20:05Z): AD7 PAYERWIN PW1, PW2, PW3 PASS (NEW; one idea, three variants), CROWDHIT CH1 STOP, WAVEHOLD WH2 R1 and
  R2 in its hand-off (deciding). AD8 TOUCHBREAK TB1 and TB3 STOP, RECLAIM RC2 R1 and R2 in its hand-off (deciding), WAVEEND grading.
  AD9 RUNEND RE2 PASS (NEW), RE1 STOP, PREMTURN PM5 no edge (grading). Both new alarms came from 'new alarms found here' families
  (FUNDING_CROWD, TAKER_FLOW) with a new input, and in both the other side lost in every month.

## 4b. Forward-only candidates: the OTHER side won (never graded on Sep-Dec again; V6-35)
| from | the side that won | numbers |
|---|---|---|
| AD7 CROWDHIT CH1 (FOLLOW a move against the funding payers, open interest not falling) | FADE | FADE LEAD +4.16 at 15m (t 2.27), +6.33 at 1h (t 3.30), 4 of 4 months |
| AD5 PACECOOL PC3 (FADE a coin's own cooled jump) | FOLLOW | FOLLOW 15m +3.4, 1h +2.7, 4 of 4 months |
| AD3 ALONE AL1, GB2, PV1 (FADE lone coin moves) | FOLLOW | FOLLOW ahead in every month (round 1) |
| AD8 TOUCHBREAK TB1, TB3 (FADE the break of a tested 2 h edge) | FOLLOW, read at 5 to 15 min | FOLLOW 5m +6.0 and +4.6, 15m +4.2 and +2.9, every month |

## 5. Before you claim: six questions (an idea that fails one is a weak idea)
1. Who must trade, and why now? (liquidated, margin-called, a funding payer, an arbitrageur closing, stop orders past a level.) Name them.
2. What is their fuel, and when does it run out? The fire is the moment it runs out (FADE) or starts (FOLLOW).
3. Which input in K5/METRIC_FAMILIES_V1.md shows that trader, and is it one no registry alarm uses?
4. Will it fire often enough: 1,000 or more waves Sep-Dec, on many coins?
5. Why should the OTHER side lose? (Pattern 1: if both sides can win, it is a volatility marker.)
6. Is it a filter on an old moment? Then it is a copy: drop it.

## Sources (sha16 at 20:07Z, 29 Oct)
- POSTMORTEMS.tsv (why column) of runs AD1, AD2, AD3, GPT1, GPT2 (sha16 at 18:46Z: 4c579de075e60e31, 9883f58c104f42bf, 593bce4094bec31d,
  152a6fb20f47781a, ab6a5279b9068c72) and AD7 66ec640f7e8df5dc, AD8 7d3a042023682e0d, AD9 557fcf9dc38f5dd7 (20:07Z).
- Round 2 closed by SCOUT: runs/AD4_20261029, AD5_20261029, AD6_20261029 REPORT.md and FINDINGS files (18:58Z-19:10Z).
- REGISTRY/ALARM_REGISTRY_V1.tsv 186052c729cf66d0 (131 rows, 20:05Z); REGISTRY/SCOREBOARD.md 13c36b9065cefa90; FAMILY_TAGS_V1.tsv 82ac6824a2df0826.
