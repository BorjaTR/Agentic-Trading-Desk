# IDEA_GUIDE_V1: which ideas pass, which fail, and why (SCOUT, 29 Oct 2026, rounds 1 and 2). TEST, NOT REVIEWED.
An opinion built from the runs' POSTMORTEMS rows (the why column) and the registry. Read it before you pick your two ideas
(the owner 29 Oct 19:02 Berlin: "every time they try better ideas and do not waste time on the ideas that have less chance").
Each line names its run; the files are listed under Sources with their sha16.

## 1. What made the 4 NEW PASSes: a new input that shows a forced trader, and the moment its flow ends
| alarm | new input | who is forced | side, numbers | waves Sep-Dec |
|---|---|---|---|---|
| AD2 OIFLUSH OF1 | open interest falls in its own top 1 pct during a big 10 min move | positions leaving | FADE; the FOLLOW side under random at 1 h in 4 of 4 months (CARD_OF1 FOLLOW 1h -2.7) | 1,485 |
| AD2 HLFLUSH HF1 | the same on Hyperliquid open interest | positions leaving | FADE; FOLLOW 1h -4.9 | 1,351 |
| AD1 FORCEDBREAK FB5 | forced flow over the coin's own 99th pct while the price breaks yesterday's range | liquidated traders at a level | FADE +8.8 at 15m, +5.5 at 1h; FOLLOW +1.5, -3.8 | 897 |
| GPT2 LATEBASIS LB2 | mark premium dislocation while small fills fight large fills | arbitrageurs and late chasers | FADE; LB1 (2,091 fires) R1 only, LB2 with a wider tail (2,919 fires) R2 PASS | 1,391 |
Pattern: each names a trader who must trade NOW and an input no registry alarm used. In all four the OTHER side lost (FOLLOW under
random at 1 h), not only the lean side won.

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

## 4. Round 2, not decided (AD4, AD5, AD6 stopped at 18:02Z; the hand-off files only, never a decision)
- AD4 SETTLEBACK (unwinding around funding settlements): V3 R1 PASS and R2 PASS; V2 R1 only; V1 no. Do not take funding-settlement
  timing ideas: they would copy it.
- AD5 PACECOOL (volatility pace cooling): PC2 R1 only; PC1 and PC3 no. AD6 BASISJUMP (premium jumps): BJ3 R1 only; BJ1 and BJ2 no.
- GPT2 (decided): LATEFILL LC1 NEEDS MORE MONTHS, LC2 STOP; CHASEEND CE1 STOP; MARKETTURN MT1 NEEDS MORE MONTHS; AFTERFLUSH AF1
  NEEDS MORE MONTHS; LATEBASIS LB1 NEEDS MORE MONTHS, LB2 PASS (NEW, nearest OF1 1.3 pct same fires).

## 5. Before you claim: six questions (an idea that fails one is a weak idea)
1. Who must trade, and why now? (liquidated, margin-called, a funding payer, an arbitrageur closing, stop orders past a level.) Name them.
2. What is their fuel, and when does it run out? The fire is the moment it runs out (FADE) or starts (FOLLOW).
3. Which input in K5/METRIC_FAMILIES_V1.md shows that trader, and is it one no registry alarm uses?
4. Will it fire often enough: 1,000 or more waves Sep-Dec, on many coins?
5. Why should the OTHER side lose? (Pattern 1: if both sides can win, it is a volatility marker.)
6. Is it a filter on an old moment? Then it is a copy: drop it.

## Sources (sha16 at 18:46Z, 29 Oct)
- runs/AD1_20261029/registers/POSTMORTEMS.tsv 4c579de075e60e31
- runs/AD2_20261029/registers/POSTMORTEMS.tsv 9883f58c104f42bf
- runs/AD3_20261029/registers/POSTMORTEMS.tsv 593bce4094bec31d
- runs/GPT1_20261029/registers/POSTMORTEMS.tsv 152a6fb20f47781a
- runs/GPT2_20261029/registers/POSTMORTEMS.tsv ab6a5279b9068c72; runs/GPT2_20261029/registers/DECISIONS.tsv 4fc2128fb0dc255a
- REGISTRY/ALARM_REGISTRY_V1.tsv 4bbcfe908324eb5f; REGISTRY/SCOREBOARD.md 135918473b655eaf
- Round 2 hand-offs (receipts/<GRADE job>/HANDOFF/REAL_SEALED/): AD4 20263864_GRADE_SETTLEBACK REAL_RULES_V1 f1ef40280ee45924,
  V2 776270cb96d8b8e5, V3 faa489a184fe3bf4; AD5 20263863_GRADE_PACECOOL PC1 62d1c820d30fdb44, PC2 4cb35c9f17c7508d, PC3 f3c58504aeb1e689;
  AD6 20263861_GRADE_BASISJUMP BJ1 eec0275cdb62c2ef, BJ2 f3f3ac3245a15e8c, BJ3 7837fcdfd80c3016
