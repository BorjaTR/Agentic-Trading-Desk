# IDEA_GUIDE_V4: which ideas pass, which hold on unseen months, which fail, and why (SCOUT, 29 Oct 2026, rounds 1 to 5). TEST, NOT REVIEWED.
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
| AD7 WAVEHOLD WH2 | a big move inside a running market liquidation wave (A4) while the coin's open interest has not left since the wave began (A7) | positions that did not leave | FADE; LEAD 1h +8.59 (t 4.85); Jan-Apr HELD in 3 of 4 months (claimed after reading CH1: Jan-Apr was its honest test) | 1,201 |
| AD8 RECLAIM RC2 | a close past a 2 h edge touched 4 or more times, back inside within 2 min (C9 touches) | stops run past a tested level | FADE; LEAD 1h +6.34 (t 4.61), 4 of 4 months | 880 |
| AD12 DEPTHBACK D3 | the book refills (D3.S01 top-of-book dollars back at their own median) after a forced sweep emptied it during a big move | market makers back after a sweep | FADE; LEAD 1h +7.89 (t 4.19), 4 of 4 months, FOLLOW under random at 1h every month | 1,144 |
| AD10 NEWSLATE V4 | GDELT news count jumps (Z2.S02, read 15 to 30 min late) after a big market move: late news readers, a wider tail than V1 | late readers who chase a move | FADE; LEAD 1h +11.32 (t 3.83), 4 of 4 months; V1 (401 waves) was R1 only | 624 |
| AD13 LIQGAP LG4 | liquidations (A1.S05, A1.S06: 25,000 USD net in 5 min) just stopped while the perp's instant premium (X1.POSX.S06) still stands in its own top 1 pct | the liquidation engine, which trades the perp only | FADE; LEAD 1h +8.18 (t 4.11), 4 of 4 months, FOLLOW under random at 1h every month; decided 37 min after START (round 5); Jan-Apr not read yet | 1,239 |
Pattern: each names a trader who must trade NOW and an input no registry alarm used. All 14 new PASS variants are FADE (V6-49). In every one the OTHER side lost (FOLLOW under
random at 1 h), not only the lean side won. A scheduled forced trader (a known minute, a known payment) gave the strongest result;
AD4's stricter lines on the same moment (V1 open interest fell, V2 the price footprint) only cut waves (96 and 178).

## 1b. The real test: Jan-Apr 2026, months no one has seen (month_read_v3: HELD = gap 5 or more at 15m and 1h)
| alarm | Sep-Dec LEAD 1h (t) | 2601 | 2602 | 2603 | 2604 | months held |
|---|---|---|---|---|---|---|
| AD1 FORCEDBREAK FB5 | +9.96 (3.42) | HELD | HELD | WEAKER | HELD | 3 |
| AD2 OIFLUSH OF1 | +6.29 (3.37) | WEAKER | HELD | HELD | HELD | 3 |
| AD4 SETTLEBACK V3 | +16.89 (4.33) | WEAKER | HELD | HELD | HELD | 3 |
| AD7 WAVEHOLD WH2 | +8.59 (4.85) | HELD | WEAKER | HELD | HELD | 3 |
| AD10 NEWSLATE V4 | +11.32 (3.83) | WEAKER | STRONGER | HELD | WEAKER | 2 |
| AD2 HLFLUSH HF1 | +9.07 (4.47) | BROKE | HELD | WEAKER | WEAKER | 1 |
| GPT2 LATEBASIS LB2 | +7.77 (3.30) | WEAKER | HELD | WEAKER | WEAKER | 1 |
| AD7 PAYERWIN PW1 | +11.23 (5.81) | WEAKER | WEAKER | WEAKER | HELD | 1 |
| AD12 DEPTHBACK D3 | +7.89 (4.19) | WEAKER | WEAKER | WEAKER | HELD | 1 |
| AD9 RUNEND RE2 | +5.62 (3.20) | WEAKER | WEAKER | WEAKER | WEAKER | 0 |
- The side beat random at both horizons in 39 of 40 months (one BROKE: HF1 in January), but the size fell: the 5-point bar held in
  18 of 40, and in some WEAKER months the other side did as well (D3 January: other side +4.9 at 15m).
- Nothing in Sep-Dec told which would hold: not the LEAD or its t (PW1 t 5.81 held 1 month, OF1 t 3.37 held 3), not the Sep-Dec
  gaps (OF1 1h gaps +2.4 to +5.7 held 3; NEWSLATE V1 had both gaps over 5 in 2 months and read WEAKER 4 of 4).
- The four that held each name positions that must close at a known moment: positions leaving in a big move (OF1), forced flow
  through yesterday's range (FB5), funding payers at the settle (SETTLEBACK V3), a big move inside a liquidation wave with open
  interest still in (WH2). Small sample: read it as a hint.
- NEWSLATE V4 was strongest at 15 minutes (15m gap +7.0 to +10.8 every month, above its forecast); its 1h gap fell under 5 in
  January and April.

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
| Market breadth alone has no side | AD11 TIDEEND TE1: both sides beat random at 15m (FADE +2.9, FOLLOW +1.7) | breadth marks a market-wide move, not who must unwind |
| Widening a moment dilutes it | AD11 JUMPLEFT JL4 (2 of 4 months), JL8 (2 of 4); the side held (FOLLOW under random at 1h) but the lead fell; waves cap near 1,250 for coin moments in busy half hours, so widening adds fires, not waves (V6-46) | widen only a tail that already passed R1 and is well under the cap (NEWSLATE V1 401 to V4 624 waves, LB1 to LB2) |
| Rare events give too few waves | AD12 PRINTSNAP: 45 waves (SUPPORT FAIL); AD10 NEWSLATE V1: 401 waves (R1 only) | count waves before a card; market-wide events give one wave each |
| Funding on Hyperliquid runs the other way | AD10 HLSETTLE V1: FADE under random every month, FOLLOW +4.0 at 15m (4 of 4) | the Binance settle fade (SETTLEBACK) does not carry to Hyperliquid hourly settles |
| The other side's Sep-Dec win did not hold forward | forward-only CH1R (FADE of CROWDHIT): 0 of 4 months held (Jan BROKE); PC3R: 0 of 4 | a side read after a grade is a weak lead; only Jan-Apr decides it |
| A second liquidation wave runs on before it turns | AD14 REFLUSH RF4, RF8: FOLLOW over random at 5m every month (RF8 +5.5), FADE only +1.3 at 15m; 2 of 4 and 1 of 4 months | fade the END of a wave (its forced flow stopping), never its first minutes |
| A level broken twice traps nobody | AD14 PRIORDAY PD1 (failed re-break of yesterday's high or low): FADE under random at 15m in 3 of 4 months; AD14 EDGE4H EH4 (failed break of a 4 h edge): FOLLOW +2.5 at 15m | fade the first failed break of a level that still holds stops (AD8 RECLAIM) |
| A funding move that costs nobody much | AD15 PAYFLIP PF2 (estimate flips sign at small rates): both sides on random (LEAD 1h +0.27); PAIDLEFT PL1 (estimate back to default after a paid settle): LEAD 1h +1.29, 2 of 4 | funding moments need a payment that costs something, at a known minute (AD4 SETTLEBACK: 3 bp or more at the settle) |
| Absorbed taker flow marks activity | AD15 MAKERLOAD ML1 (big net taker flow, small move, FOLLOW): FOLLOW +1.7 and FADE +1.5 at 15m | both sides win: name who is forced and when it ends |
| A perp runaway that returns to the mark keeps going | AD13 MARKSNAP MS6: FOLLOW +5.3 over random at 15m in 4 of 4 months, FADE -1.1 at 1h | fade a runaway only with a forced trader behind it (AD13 LIQGAP LG4: liquidations, new PASS) |
| Right side, too few waves | AD15 STALLPUSH SP1 (takers push, no progress, FADE): 4 of 4 months, LEAD 1h +6.71, t 2.44 on 890 waves; the wider SP6 (1,165 waves) fell to t 1.90, SP4 to a STOP | widen only a tail well under the wave cap (V6-46); more waves come from more coins or months |

## 4. Decided in rounds 2 to 5 (registry REGISTRY/ALARM_REGISTRY_V1.tsv; every page has the WHY FAILED line)
- Round 2: GPT2 LATEBASIS LB2 PASS (NEW); LATEFILL LC1 NEEDS MORE MONTHS, LC2 STOP; CHASEEND CE1 STOP; MARKETTURN MT1 and AFTERFLUSH AF1
  NEEDS MORE MONTHS. AD4 SETTLEBACK V3 PASS (NEW), V2 NEEDS MORE MONTHS, V1 INSUFFICIENT. AD5 PACECOOL PC2 NEEDS MORE MONTHS, PC1 and PC3
  STOP. AD6 BASISJUMP BJ3 NEEDS MORE MONTHS (not CLEAR), BJ1 and BJ2 STOP. Never graded (agents stopped): HLHOUR (Hyperliquid hourly
  settles, counted: V3 1,117 waves), CALMBREAK, MARKLAG.
- Round 3 (decided by 20:05Z): AD7 PAYERWIN PW1, PW2, PW3 PASS (NEW; one idea, three variants), CROWDHIT CH1 STOP, WAVEHOLD WH2 R1 and
  R2 in its hand-off (deciding). AD8 TOUCHBREAK TB1 and TB3 STOP, RECLAIM RC2 R1 and R2 in its hand-off (deciding), WAVEEND grading.
  AD9 RUNEND RE2 PASS (NEW), RE1 STOP, PREMTURN PM5 no edge (grading). Both new alarms came from 'new alarms found here' families
  (FUNDING_CROWD, TAKER_FLOW) with a new input, and in both the other side lost in every month.

- Round 4: AD12 DEPTHBACK D3 PASS (NEW), BLOCKEND B1 STOP, B2 NEEDS MORE MONTHS, PRINTSNAP SUPPORT FAIL. AD10 NEWSLATE V4 PASS
  (novelty pending at 21:31Z), V1 NEEDS MORE MONTHS, HLSETTLE V1 STOP (the other side won). AD11 JUMPLEFT JL7 NEEDS MORE MONTHS, JL4 and JL8
  STOP, TIDEEND TE1 STOP. Forward-only (SCOUT): CROWDHIT CH1R and PACECOOL PC3R FORWARD STOP.

- Round 5: AD13 LIQGAP LG4 PASS (NEW; Jan-Apr MONTH refused at the 2 GiB worker cap twice: SCOUT reruns it with the detection in 26
  coin parts), MARKSNAP MS6 STOP (the other side won). AD14 EDGE4H EH4, REFLUSH RF4 and RF8, PRIORDAY PD1 STOP. AD15 STALLPUSH SP1 and SP6
  NEEDS MORE MONTHS, SP4 STOP; PAYFLIP PF2, MAKERLOAD ML1, PAIDLEFT PL1 STOP. The agents were stopped at about 22:30Z by a session
  interrupt; SCOUT closed the runs (decisions, CLEAN, FINDINGS).

## 4b. Forward-only candidates: the OTHER side won (never graded on Sep-Dec again; V6-35)
| from | the side that won | numbers |
|---|---|---|
| AD7 CROWDHIT CH1 (FOLLOW a move against the funding payers, open interest not falling) | FADE | FADE LEAD +4.16 at 15m (t 2.27), +6.33 at 1h (t 3.30), 4 of 4 months |
| AD5 PACECOOL PC3 (FADE a coin's own cooled jump) | FOLLOW | FOLLOW 15m +3.4, 1h +2.7, 4 of 4 months |
| AD3 ALONE AL1, GB2, PV1 (FADE lone coin moves) | FOLLOW | FOLLOW ahead in every month (round 1) |
| AD8 TOUCHBREAK TB1, TB3 (FADE the break of a tested 2 h edge) | FOLLOW, read at 5 to 15 min | FOLLOW 5m +6.0 and +4.6, 15m +4.2 and +2.9, every month |
| AD10 HLSETTLE V1 (FADE the payers' way at Hyperliquid hourly settles) | FOLLOW | FOLLOW 15m +4.0, 1h +3.7, 4 of 4 months; FADE under random every month |
| AD13 MARKSNAP MS6 (FADE a perp runaway back at the mark) | FOLLOW | FOLLOW 15m +5.3 (4 of 4 months), 1h +2.2 (+0.5 to +4.8) |
Forward-only route (the owner 29 Oct 22:02 Berlin; LEARNINGS V6-43): SCOUT seals the side that won as its own variant (FORWARD ONLY OF <V0>) and tests it on Jan-Apr only (queue_job_v4.py MONTH --forward-only, decide_forward_v1.py: FORWARD PASS = HELD or STRONGER in 3 or more of 4 months). Results: CH1R 0 of 4 months held, PC3R 0 of 4 (FORWARD STOP, 21:30Z). HLSETTLE V1R and MS6R not run yet (runner slots kept for the rounds).

## 5. Before you claim: six questions (an idea that fails one is a weak idea)
1. Who must trade, and why now? (liquidated, margin-called, a funding payer, an arbitrageur closing, stop orders past a level.) Name them.
2. What is their fuel, and when does it run out? The fire is the moment it runs out (FADE) or starts (FOLLOW).
3. Which input in K5/METRIC_FAMILIES_V1.md shows that trader, and is it one no registry alarm uses?
4. Will it fire often enough: 1,000 or more waves Sep-Dec, on many coins?
5. Why should the OTHER side lose? (Pattern 1: if both sides can win, it is a volatility marker.)
6. Is it a filter on an old moment? Then it is a copy: drop it.

## Sources (sha16 at 20:07Z, 21:32Z and 23:00Z, 29 Oct)
- POSTMORTEMS.tsv (why column) of runs AD1, AD2, AD3, GPT1, GPT2 (sha16 at 18:46Z: 4c579de075e60e31, 9883f58c104f42bf, 593bce4094bec31d,
  152a6fb20f47781a, ab6a5279b9068c72) and AD7 66ec640f7e8df5dc, AD8 7d3a042023682e0d, AD9 557fcf9dc38f5dd7 (20:07Z).
- Round 2 closed by SCOUT: runs/AD4_20261029, AD5_20261029, AD6_20261029 REPORT.md and FINDINGS files (18:58Z-19:10Z).
- REGISTRY/ALARM_REGISTRY_V1.tsv 186052c729cf66d0 (131 rows, 20:05Z); REGISTRY/SCOREBOARD.md 13c36b9065cefa90; FAMILY_TAGS_V1.tsv 82ac6824a2df0826.
- Round 4 runs AD10, AD11, AD12 registers (DECISIONS, POSTMORTEMS) at 21:32Z; forward-only decisions runs/AD7_20261029 and runs/AD5_20261029 DECISIONS 21:30:28Z.
- Round 5 runs AD13, AD14, AD15 registers and FINDINGS (closed by SCOUT 22:48Z to 22:54Z); REGISTRY/ALARM_REGISTRY_V1.tsv 8e5bdb9bf66f5735 (rounds 1 to 5).
- Jan-Apr table (section 1b): MONTH_READ files of each MONTH job; scout_work/gap_vs_forward.py (22:00Z).
