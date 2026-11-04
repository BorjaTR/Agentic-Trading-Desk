# PLAYBOOK: from a market question to a FOUND alarm (K10 for SCOUT, 30 Oct 2026, 23:00Z). TEST, NOT REVIEWED.
Read this before you pick an idea. Built from the files below only. Every number carries a source tag; the table gives each file and its sha16. FOUND.tsv (this folder) has one row per FOUND, PASS or new R1-only alarm, with a file and sha16 for every number. CONTRADICTIONS.md lists where these sources disagree, for SCOUT to settle.
archive/ holds past editions: read only, never run.
Edited in place by SCOUT helper K13, 31 Oct 2026 (round 7, team/SCOUT/R7_FIXES_V1.tsv F06, F16, F25, F30): each recipe's Readings, the codes or the ops that build them with their refractory and lines, from the registry's own definitions (def_rel and def_sha16 of REGISTRY/ALARM_REGISTRY_V1.tsv 10a7944011fcdf66); size lines and dollar floors; novelty on the GRADE fire list; no raw-row check. The definition format is DEF_TEMPLATE_V4.md (01_Detection/tree/team/RESEARCH/ALARM_DESIGN/KIT_V2/templates/).

## Sources (paths under team/RESEARCH/)
| tag | file | sha16 |
|---|---|---|
| G | ALARM_DESIGN/KIT_V6/IDEA_GUIDE_V4.md (29 Oct 23:22Z) | 8b593553081b8c57 |
| L | ALARM_DESIGN/KIT_V6/LEARNINGS_V6.tsv (rows named as L V6-37) | f8b361f28a996101 |
| P8, P7 | ALARM_DESIGN/KIT_V6/PROCESS_V8.md; ALARM_DESIGN/KIT_V5/PROCESS_V7.md (the pass rule P8 keeps) | d1ac38f4239983e6; 0b368cabce30bbe5 |
| I2A, MAP | ALARM_DESIGN/KIT_V5/IDEA_TO_ALARM_V4.md; ALARM_DESIGN/KIT_V5/FORCED_TRADE_MAP_V1.md | 15bdefeab9f306b6; 84949bf3c749d985 |
| MF, MENU | ALARM_DESIGN/KIT_V5/METRIC_FAMILIES_V1.md; ALARM_DESIGN/KIT_V5/METRIC_MENU_V1.tsv | 163a6dc2e76797ab; 5e5868eed744eb88 |
| R, SB | ALARM_DESIGN/REGISTRY/ALARM_REGISTRY_V1.tsv (built 05:48Z); ALARM_DESIGN/REGISTRY/SCOREBOARD.md (06:13Z) | b383f6107dc9e32b; 8448513fa1a9918b |
| RM, FT | ALARM_DESIGN/REGISTRY/README.md; ALARM_DESIGN/REGISTRY/FAMILY_TAGS_V1.tsv | 1650b02ff7ab6701; 5f63362dfa9892c6 |
| FL, FLR | tools/alarm_first_look/results/TRY4_FL1_20264600/FL_RULE9.tsv (FL2: ee92064488c832a1); tools/alarm_first_look/README.md | dbe4f2d4927c398b; ec746cbb50250e5c |
| F | FOUND.tsv here: its MONTH_READ files (Jan-Apr), DECISIONS files and alarm pages, each with its sha16 | per row |
Alarm pages are ALARM_DESIGN/REGISTRY/alarms/<alarm id>.md; their sha16 is given where they are used.

## Words
- Alarm: a moment known when it happens (a coin, a minute) plus a side. FADE bets the move just made comes back; FOLLOW bets it goes on.
- Fire: one moment the rule is true. Wave: fires close in time on any coin, counted once (a fire more than 30 min after the previous one starts a new wave [FLR]); waves are the unit of every count.
- c: the coin's cost unit (cost in bp / 100 + 0.032) [FLR]. The race: price reaches +2c before -1c [P7].
- LEAD: (how often the side wins the race, minus 3 matched random moments) minus (the same for the other side), in points, at 15 min and 1 h [P7].
- R1: LEAD +3 or more at 15 min or 1 h in at least 2 of every 3 counted months (a month counts with 30 or more waves). R2: R1 plus a luck bar, pooled t of at least 3 [P7]. PASS = R2; NEEDS MORE MONTHS = R1 only; STOP = R1 missed [P8].
- Jan-Apr 2026 is the honest test: months nobody saw while designing. Each reads HELD (gap over random 5 points or more at 15 min and at 1 h), STRONGER, WEAKER or BROKE [G 1b].
- FOUND: new (novelty NEW or NEW SIDE) and Jan-Apr HELD or STRONGER in 3 or more of 4 months, for a PASS or an R1-only alarm [L V6-53, V6-62].
- Novelty: COPY = 50 pct or more of its fires are fires of an alarm on the same side; NEAR = 40 to 50 pct; NEW = every overlap under 40 pct; NEW SIDE = it gives a side to a desk trigger that had none [RM].
- First look (edition 11): SIZE = busy fires move 4c either way within 1 h more often than equally busy random moments; SIDE = the side wins its 1 h race more than random. Sep-Dec needs z 2 or more, Jan-Apr confirms at z 1 or more, 3 of 4 months each [FLR].

## Where we are
- FOUND: 6 [SB; REGISTRY/SCOREBOARD.md a36a934260de8d82, 31 Oct 02:07Z]: AD13 LIQGAP LG4, AD1 FORCEDBREAK FB5, AD2 OIFLUSH OF1,
  AD4 SETTLEBACK V3, AD7 WAVEHOLD WH2, and the R1-only AD4 SETTLEBACK V2 (Jan-Apr 3 of 4 STRONGER; FOUND.tsv). All FADE. Each names traders who must close at a known moment: forced flow through a level, positions leaving, payers at the settle, a market wave pushing a coin whose positions stayed, the liquidation engine on the perp [G 1b, F].
- 15 new PASS on Sep-Dec: 5 FOUND, 10 did not hold (8 on SB; PW2 0 of 4 and PW3 1 of 4 were read after it) [F].
- 17 new R1-only alarms: 15 read. AD4 SETTLEBACK V2 holds 3 of 4 on its MONTH files, not yet on SB; it is V3's moment plus one line (SCOUT to settle). GPT2 AF1 and LC1 have no MONTH yet [F].
- Every new PASS is a FADE (15 of 15 [R]); FOLLOW was tried in 3 of 59 variants and never passed [L V6-49]; in each of the first 14 the other side lost too, not only the lean side won [G 1].
- Nothing in Sep-Dec told which would hold: not the LEAD or its t (PW1 t 5.81 held 1 month, OF1 t 3.37 held 3) [L V6-47].

## How to come up with an idea: six questions [G 5]
1. Who must trade, and why now? Name them: liquidated traders, margin calls, funding payers, arbitrageurs closing, stops past a level.
2. What is their fuel, and when does it run out? Fire at the minute it runs out (FADE) or starts (FOLLOW).
3. Which data shows that trader (MF; the 12 forced or late traders of MAP), and does any registry alarm already use it?
4. Will it fire often enough: 1,000 or more waves in Sep-Dec (about 250 a month), on many coins [G 3]?
5. Why should the OTHER side lose? If both sides can win, the moment marks volatility, not direction.
6. Is it a filter on an old moment? Then it is a copy: drop it.
What passed: a trader who must trade now, a data series no alarm used, and the minute their flow ends, faded [L V6-28, G 1].
The strongest result: a scheduled forced trader, a known minute with a known payment (SETTLEBACK V3, LEAD 1h +16.89) [R, G 1].
A FOLLOW idea must name a forced flow that STARTS and lasts an hour or more [L V6-49].

## The loop and the current tools (paths under ALARM_DESIGN/ unless named; each current tool takes --settings <this machine's settings file>)
- Steps [P8]: 1 idea; 2 metrics (MF, MENU) and one card (KIT_V6/templates/CARD_V7.md, the prereg); 3 COUNT: fires, waves and coins per month, reads no outcome; 4 GRADE: Sep-Dec against 3 matched random moments per fire; 5 ENTRY: the money path, information only; 6 novelty: REGISTRY/tools/novelty_v2.py; 7 MONTH: Jan-Apr, read by month_read_v3.py (pinned b3480cfd670b28f4 by the MONTH V5 template); 8 decide: KIT_V5/tools/decide_v2.py (a forward-only side: decide_forward_v2.py).
- Jobs: AGENTS.md (its loop table and "Queue editions") names the current queue, templates and decide tools and wins over this page.
  Today (ALARM_V1_20): KIT_V5/tools/queue_job_v14.py (COUNT JOB_COUNT_V7, GRADE JOB_GRADE_V14, ENTRY JOB_ENTRY_V7, MONTH JOB_MONTH_V14, FIRSTLOOK JOB_FIRSTLOOK_V1), decide_v4.py and decide_forward_v3.py; novelty_v4.py; the TRUE gate 03_Grading/tree/tools/true_gate/true_gate_v3.py, required step 5c, by hand in a runner job (cards/true_gate.md); audit_run_v4.py, the run audit with the row required. The steps line above names the editions the findings came from.
- Also current: KIT_V5/tools/audit_run_v4.py (audit_run_v3.py plus A18 TRUE) and board_line_v2.py; KIT_V6/tools/idea_time_v2.py; REGISTRY/tools/registry_build_v2.py and scoreboard_v2.py; tools/alarm_first_look/fl_read_v11.py (first look edition 11) with fair_v4.py.
- Package proofs (both edited 30 Oct 23:01Z; sha16 at 23:08Z): tools/alarm_package/_tools/machine_paths_v2.py (STATIC: no machine path in code; 30d4f0c4f1556705); tools/alarm_package/_tools/run_isolated_v2.py (RUN on real data; 9d3f1fa4b72230fc; takes FORBID from the settings or --forbid and refuses without one; a run that opened or imported anything in archive/ fails).
- Past editions behind the findings here: every Sep-Dec label, novelty verdict, registry row and FOUND list came from decide_v1, queue_job_v4, novelty_v1, registry_build_v1 and scoreboard_v1 (their current editions change only where files are, per their own headers); forward-only labels from decide_forward_v1; Jan-Apr verdicts from month_read_v3; first look labels from edition 11 [F].
- Fast: write the definition and queue the COUNT at once; write the card while it runs; seal both ideas and queue both GRADEs before reading either [L V6-48]; grade the best variant alone first [L V6-33]; queue the MONTH of a new PASS or a new R1-only alarm at once, since the goal is FOUND [L V6-53, V6-62]. No quiet window now: "All jobs can be queued" (the owner 30 Oct 23:32 Berlin) [P8].

## Recipes: families that worked or nearly worked (FOUND first; numbers Sep-Dec unless named)
Size lines and dollar floors [R7 F25]: read a size as the coin's own pct, as the read_as of A1.S01 and A1.S08 says ("never a fixed dollar line"; METRICS_V2 lines 15, 24). A fixed dollar value stays only as a stray-print filter, far below the own line of the coins that matter, best as own_pct's floor. Example (FB5): `{"op": "own_pct", "of": "x", "q": 99, "floor": 5000}` = the coin's own top 1 pct, never under 5,000 USD. LG4 (25,000 USD over 5 min) and WF1 (5,000 USD a minute) used a fixed line as the size test: graded as written; new variants use the own pct line (DEF_TEMPLATE_V4.md "Size lines and dollar floors").
Readings [R7 F30]: each recipe's Readings line gives the code, or the op that builds the reading, its line, the grid and the refractory, from the alarm's definition (file and sha16 named). A 10, 15 or 60 min move has no code: build it with the price op. A market code (scope market in METRICS_V1) is read with the market op. Write them in DEF_TEMPLATE_V4.md's form.
### 1 FORCED_BREAK: forced flow through yesterday's range (FOUND: AD1 FORCEDBREAK FB5)
- Question: did forced liquidations just carry the price through yesterday's high or low, where stops sit? That fuel ends at once: FADE, 15 min to 1 h. Moment: in the last 2 min the price crossed yesterday's high (low) while forced buying (selling) in the minute just ended was in the coin's own top 1 pct of 14 days.
- Data: distance to yesterday's high and low (C11.S06, C11.S07); liquidations of the minute just ended (A1.S08 long, A1.S09 short). Lines: own 99th pct over 14 days; 1 min grid; one fire per coin per hour.
- Readings (FB5.json 64eb0c06e2072687): the cross: C11.S06 with A1.S09 (C11.S07 with A1.S08), each now and lagged 120 s; the forced flow: A1.S09 (A1.S08) above own_pct q 99 with floor 5000; grid 60 s; refractory 3600 s; side x 1.
- Fails at: COUNT on memory (FB1 read 47 inputs, 1,044 MB, over the 2 GiB worker cap) [L V6-06]; a break of today's high set 2 h before (DAYFORCE DF6) and a forced push then a 2 min pause (PUSHEND PE3) were STOP [SB, FT].
- Receipts: LEAD 1h +9.96 (t 3.42), 830 waves, Jan-Apr 3 of 4 [R, F]; page d6eda7db73b8a445; definition FB5.json 64eb0c06e2072687.
### 2 POSITIONS_LEAVING: positions close into a big move (FOUND: AD2 OIFLUSH OF1)
- Question: is a big move made by positions closing (open interest falling fast), not by new traders? Closing is a bounded fuel: FADE. Moment: a 10 min move beyond its own 90th pct while the 10 min open interest change is under its own 1st pct (14 built days).
- Data: Binance open interest change over 10 min (E2.S04); HF1 the same on Hyperliquid (E2.S06). 1 min grid; one fire per coin per 30 min.
- Readings (OF1.json db86784e7ce84fe5): the 10 min move: ratio(change(price, 600), lag(price, 600)), its absolute value above own_pct q 90; E2.S04 below its own_pct q 1; grid 60 s; refractory 1800 s; side = sign of the 10 min move x 1.
- Fails at: GRADE when both sides win: a lone-coin flush (OF2) or open interest building (OB1) [G 3]; MONTH: HF1 held 1 of 4 (January BROKE) [R]; cooled-jump and wave versions: JUMPLEFT JL4, JL8, LATEFLUSH LF2, WAVEEXIT WX6 STOP; JL7, WX3, WX4 R1 only and 0 to 1 of 4 in Jan-Apr [SB, F].
- Receipts: OF1 LEAD 1h +6.29 (t 3.37), 1,333 waves, Jan-Apr 3 of 4; NEW SIDE: 87.6 pct of its fires are the desk trigger O1's, which had no side [R, F]; page a3b1957b5bccd0fe; definition OF1.json db86784e7ce84fe5; HF1 page 508b5ef9dce97c89.
### 3 FUNDING_SETTLE: payers at the settle minute (FOUND: AD4 SETTLEBACK V3)
- Question: with a big funding payment due, payers close before the settle; after it their reason to stay out ends. FADE the payers' closing way (longs pay: buy). Moment: the coin's Binance settle minute with 3 bp or more due.
- Data: minutes to the coin's next settle (Z3.S01, 0.5 or less); the funding estimate 2 min before (E1.S01) times the interval in hours (E1.S04) over 8. One fire per coin per hour.
- Readings (V3.json 7e3c71eccba7fa2c): Z3.S01 <= 0.5 (shared); the payment: abs(lag(E1.S01, 120) x E1.S04 / 8) >= 0.0003 (3 bp); grid 60 s; refractory 3600 s; side = sign(lag(E1.S01, 120)) x -1 (E1.S01 positive = longs pay, and their closing pushes the price down).
- Fails at: COUNT: settles are few, stricter lines only cut waves (V1 114 and V2 215 COUNT waves against V3's 441) [page V3]; Hyperliquid hourly settles run the other way (HLSETTLE V1: FOLLOW +4.0 at 15 min, 4 of 4) [G 3]; small payments (PAYFLIP PF2, PAIDLEFT PL1) and PAYERSGONE PG3 STOP; PAYERSBACK PB3 R1 only, 1 of 4 in Jan-Apr [G 3, SB, F].
- Receipts: V3 LEAD 1h +16.89 (t 4.33) on 383 waves, Jan-Apr 3 of 4 [R, F]; page 6279b611caab55bd; definition V3.json 7e3c71eccba7fa2c. V2 (adds the 30 min price footprint): +19.16 (t 2.81) on 178 waves, R1 only, Jan-Apr 3 of 4 [R, F]; page 47a798225232d5f0.
### 4 FORCED_LIQUIDATION: a market wave pushes a coin whose positions stayed (FOUND: AD7 WAVEHOLD WH2)
- Question: in a running market liquidation wave, is the coin pushed by the market's forced flow while its own open interest has not left? The push is borrowed: FADE. Moment: a 10 min move beyond its own 95th pct with the wave, open interest at or above its level at the wave's start (A7.S01 long wave, A7.S03 short wave); one fire per coin per hour. WF1 adds the wave's age (A4.S04, A4.S05), the engine's share of the coin's taker flow (A5.S01, A5.S02: 0.10 or more) and liquidation dollars (A1.S08, A1.S09: 5,000 or more; a fixed dollar line, see Size lines).
- Readings (WH2.json 7a7f8c6dceea4f68): the 10 min move as in recipe 2, absolute value above own_pct q 95; open interest since the wave's start: pick(sign of the move, A7.S03, A7.S01) >= 0 (empty when no wave runs, so no fire); grid 60 s; refractory 3600 s; side = sign of the move. WF1 (WF1.json eac6a36ccf2c8a6d) turns each empty reading into -100 with known and pick, so it fails its line. Breadth across coins: A2.S05 (long), A2.S06 (short) count the roster coins with liquidations in the last minute (market codes: the market op); none of the 11 definitions named here reads them.
- Fails at: COUNT on fire count (WH1: 46,312 fires, up to 961 in a wave [page WH2]); novelty seen only after the GRADE (WF1: 27.6 pct the same fires as N1 [L V6-60]); a second wave runs on (REFLUSH RF4, RF8 STOP [G 3]); filters on N1's moments are copies [G 2].
- Receipts: WH2 LEAD 1h +8.59 (t 4.85), 1,201 waves, Jan-Apr 3 of 4 [R, F]; page 5c4404994579f429; definition WH2.json 7a7f8c6dceea4f68. WF1 +8.48 (t 3.37), Jan-Apr 2 of 4 [R, F]; page 89914ac85dd1dd70.
### 5 PREMIUM_GAP: forced flow pushed the perp away from spot (FOUND: AD13 LIQGAP LG4)
- Question: the liquidation engine trades the perp only; when its flow stops, the gap to spot and the price come back: FADE the forced way. Moment: net liquidations 25,000 USD or more over 5 min (a fixed dollar line, see Size lines) (A1.S05 long, A1.S06 short, each the last 60 s), the instant premium (perp book mid against spot index, X1.POSX.S06, outside the menu: check it first [MF]) in its own top 1 pct off its 14-day median the forced way, and no forced flow that way in the last 60 s. 5 s grid; one fire per coin per 30 min.
- Readings (LG4.json 94c2d5188ef9d715): the 5 min net forced flow: A1.S06 - A1.S05 now plus its lags at 60, 120, 180 and 240 s (each minute once: DEF_TEMPLATE_V4.md rule 3), absolute value >= 25,000 USD (a fixed line); the premium X1.POSX.S06 minus its own_pct q 50 (its own median) the forced way, and that gap's absolute value above its own_pct q 99; no net forced flow that way now; grid 5 s; refractory 1800 s.
- Fails at: GRADE for a premium move with no forced trader, which arbitrage closes fast (BASISJUMP BJ1, BJ2 STOP; BJ3 0 of 4 in Jan-Apr) [G 3, F]; a market premium turn has no side (PREMTURN PM5); a runaway back at the mark runs on (MARKSNAP MS6: FOLLOW +5.3 at 15 min) [G 3]; MONTH memory: LG4 ran only in 26 coin parts [L V6-51, V6-55].
- Receipts: LG4 LEAD 1h +8.18 (t 4.11), 1,239 waves, Jan-Apr 4 of 4, first look SIZE+SIDE [R, F, FL]; page cdb2d748dc26cc5b; definition LG4.json 94c2d5188ef9d715. LB2 (mark premium E3.S01 while small fills fight large fills): +7.77 (t 3.30), 1 of 4; page 042f96b2d1b18845.
### 6 FUNDING_CROWD: a paying crowd's windfall (PASS, not held: AD7 PAYERWIN PW1 to PW3)
- Question and moment: a big 10 min move (own 90th pct; PW3 95th) in favour of the side paying a funding estimate (E1.S01) of 0.0002 per 8 h or more (PW2 0.0005): the crowd takes its windfall; FADE; one fire per coin per 30 min.
- Readings (PW1.json dd49e52e00eadce1): the 10 min move as in recipe 2, above own_pct q 90; sign of the move x E1.S01 >= 0.0002 (E1.S01 per 8 h; positive = longs pay shorts, its read_as in METRICS_V1: so the move favours the payers); grid 60 s; refractory 1800 s; side = sign of the move.
- Fails at: MONTH: PW1 1 of 4, PW2 0, PW3 1 [F]; FOLLOW against the payers lost (CROWDHIT CH1) and its FADE side, sealed forward-only, held 0 of 4 [G 4b]; a sign flip at small rates has no side (PAYFLIP PF2) [G 3].
- Receipts: PW1 LEAD 1h +11.23 (t 5.81, the highest t), 1,499 waves [R]; page ce3233eccdf14720; PW3 page e0a700d50937d886.
### 7 NEWS_LATE: late news readers (PASS, 2 of 4: AD10 NEWSLATE V4)
- Question and moment: a big move makes the news; readers trade it late. The GDELT bitcoin-tagged count of the last readable batch (Z2.S02, market-wide, readable 15 to 30 min late) above its own 80th pct while the coin's 60 min move is in its own top 5 pct: their flow is spent; FADE, strongest at 15 min [G 1b]; one fire per coin per hour.
- Readings (V4.json 1c7b423d732c90c4): market Z2.S02 above its own_pct q 80 (the market op); the 60 min move ratio(price - lag(price, 3600), lag(price, 3600)), absolute value above own_pct q 95; grid 60 s; refractory 3600 s; side = sign of the 60 min move.
- Fails at: COUNT: a market-wide event gives one wave (V1 at the 90th pct: 401 waves, R1 only, 0 of 4 in Jan-Apr); the wider 80th pct line (624 waves) reached R2 [G 3, R, F]; MONTH: the 1 h gap fell under 5 in January and April [G 1b].
- Receipts: V4 LEAD 1h +11.32 (t 3.83), 624 waves [R]; page b48bbf195fefcdb6; definition V4.json 1c7b423d732c90c4.
### 8 BOOK_REFILL: makers back after a sweep (PASS, 1 of 4: AD12 DEPTHBACK D3)
- Question and moment: in the last 15 min the dollars at the best bid and ask (D3.S01) fell to their own bottom 5 pct during a 15 min move in its own top 10 pct, and now they are at or above their own 75th pct: the one-way flow is over; FADE; one fire per coin per 30 min.
- Readings (D3.json e91590abe62ee81e): D3.S01's lowest of the last 900 s at or under its own_pct q 5 (max(-D3.S01, 900) + own_pct q 5 >= 0); the 15 min move ratio(change(price, 900), price), absolute value above own_pct q 90; D3.S01 now at or above its own_pct q 75; grid 60 s; refractory 1800 s; side = sign(change(price, 900)).
- Fails at: MONTH (3 of 4 WEAKER) [F]; a thin book alone marks volatility (GB1: both sides beat random) or a lone move that runs on (GB2) [G 3].
- Receipts: LEAD 1h +7.89 (t 4.19), 1,144 waves, 22,195 fires (over the 20,000 guide, L V6-37) [R]; page 297894a2cd77da65.
### 9 FAILED_BREAK: a failed break of a tested edge (PASS, 0 of 4: AD8 RECLAIM RC2; known: DAYPOKE2)
- Question and moment: a minute closed past the 2 h high (low) touched 4 or more separate times (C9.S11, C9.S12) and the price is back inside within 2 min: the stops were run and the break failed; FADE; one fire per coin per hour. DAYPOKE2: a poke past a 24 h high or low older than 2 h, back inside [R].
- Readings (RC2.json da9d3f3e1f0f99a3): the edge: the 2 h high (prior_max of price over 7200 s) as it was 180 s ago; the price 60 or 120 s ago above it and now back under it; C9.S11 240 s ago above 3.5 (4 or more touches); the low side mirrored with prior_min and C9.S12; grid 60 s; refractory 3600 s.
- Fails at: fading the break itself, which runs on for minutes (TOUCHBREAK TB1, TB3: FOLLOW +6.0 and +4.6 at 5 min, every month); a level broken twice traps nobody (PRIORDAY PD1, EDGE4H EH4) [G 3]; size (23,092 fires [R]: ENTRY waited, MONTH only in 26 parts [L V6-40, V6-55]); a flow filter on DAYPOKE2 is a copy (FT1) [L V6-02].
- Receipts: RC2 LEAD 1h +6.34 (t 4.61), 880 waves, Jan-Apr 0 of 4 (January BROKE) [R, F]; page 91b84b0087c56dd8.
### 10 TAKER_FLOW: a one-sided taker run ends (PASS, 0 of 4: AD9 RUNEND RE2)
- Question and moment: how one-sided the last 1,000 fills were (B2.S02) reached its own top 0.5 pct within 15 min, the 15 min move is in its own top 10 pct, and takers now trade against the move (B1.S09): makers unload; FADE; one fire per coin per 30 min.
- Readings (RE2.json 1d05e938addba437): B2.S02's max of the last 900 s at or above its own_pct q 99.5; the 15 min move ratio(change(price, 900), price), absolute value above own_pct q 90; B1.S09 oppsign change(price, 900) (takers now trade against the move); grid 60 s; refractory 1800 s; side = sign(change(price, 900)).
- Fails at: the rarest version is noisier (RE1, top 0.1 pct: 990 waves, 2 of 4 months); absorbed taker flow marks activity (MAKERLOAD ML1: both sides win); STALLPUSH SP1 had the side but 890 waves (t 2.44), the wider SP6 t 1.90 [G 3], both 0 of 4 in Jan-Apr [F].
- Receipts: RE2 LEAD 1h +5.62 (t 3.20), 1,516 waves, Jan-Apr 4 of 4 WEAKER [R, F]; page 8c546f27d55f3f3f.

## What fails, and the cheap test that catches it early
| what fails | example | cheap early test |
|---|---|---|
| Both sides beat random: the moment marks volatility, not direction | GB1 FADE +3.9 and FOLLOW +2.9 at 15 min; OB1, OF2, AL1, PC1, TE1, ML1 the same [G 3] | the card says, before the COUNT, why the other side loses and what proves the idea wrong; no answer, no idea [G 3, L V6-19] |
| A lone coin's move keeps going | AL1, GB2, PV1: FOLLOW ahead in every month [G 3] | never FADE a lone move; it is a FOLLOW candidate [L V6-20] |
| Too few waves (R1 only) | LF1 770, AB2 722, AF1 about 400 waves [L V6-29] | the COUNT job reads no outcome: aim for 1,000 or more waves in Sep-Dec; under 30 a month cannot count [L V5-13, V6-29] |
| Too many fires | WE2: 79,543 fires (52 a wave) still grading after 60 min [G 3] | at COUNT, keep under about 20,000 fires: a refractory, a line that fires on a few coins of a wave [L V6-37] |
| The 2 GiB worker memory cap | FB1 (47 inputs, 1,044 MB) failed COUNT; AD18 CLOSEGAP and CLOSEMARK were refused at 2,148,483,072 to 2,162,704,384 bytes [L V6-06, V6-57] | the hand-check helper on half B (26 coins) for 8 days: hc_mem_probe_v3's limit, from the code's WORKER_RSS_CAP (1,272 MB); 4 or more raw codes with liquidations and price is at risk [L V6-06, V6-57; FB5 page d6eda7db73b8a445] |
| A copy | FT1: 99.1 pct of its fires were DAYPOKE2's [L V6-02]; LF3: 87.4 pct N1's [R] | read the registry and the 3 nearest pages first; run novelty_v2 on the GRADE job's fire list as soon as it is written (AGENTS.md step 9): the COUNT job keeps only its first 20 fires (JOB_COUNT_V6 line 52), so a check before the GRADE waits for a COUNT job that keeps its list [L V6-03, V6-60; R7 F06] |
| Empty or flat readings | codes on BTC's row only read empty on other coins (zero fires, no error); funding's own pct sits on its 0.0001 default [MF, L V5-10] | the menu must show values on the rows the rule reads; the hand check prints the line's value at 5 fires on non-BTC coins [L V5-10] |
| A line in each coin's own units | one line covers very different shares of minutes per coin [L V6-12] | print the share for 5 or more coins; 10 times apart: use the coin's own pct [L V6-12] |
| A signed calm-market line | C1.S23: 4,862 exact zeros in 158,400 minutes [L V6-13] | read a range, never a signed return [L V6-13] |
| A wrong data end | metric_brief's last day says 9 Mar 2026, yet FB5 had 531 April fires [L V6-05] | read where data ends from a COUNT by month [L V6-05] |
| The other side's Sep-Dec win | CH1R and PC3R held 0 of 4 in Jan-Apr (decide_forward_v1, a past edition) [G 4b] | never regrade it on Sep-Dec: seal it forward-only, Jan-Apr decides [L V6-35, V6-43] |
| Widening a moment | JUMPLEFT JL4 and JL8: 2 of 4 months; coin moments in busy half hours cap near 1,250 waves [G 3, L V6-46] | widen only a tail that already passed R1 and sits well under the cap (NEWSLATE V1 401 to V4 624 waves) [L V6-44, V6-46] |

## Waste to avoid
- Copies: never re-run a COPY; never retry a STOP without a new mechanism named in the card [L V6-03]. Filters on known moments made the copies LF1 to LF3, GA2, GB2, PV1 and FT1 [G 2, L V6-28].
- Oversized variants: an unsized setup chained into 73,743 fires in 700 waves [L V5-13]; an ENTRY needs 300 MB per 1,000 fires, so a variant over about 33,000 fires never gets one [L V6-40], and its GRADE could not be cleaned (5,896 MB locked) [L V6-41]; big fire lists overran their declared size [L V6-42].
- Memory: never raise the 2 GiB worker cap [L V6-06]; a Sep-Apr MONTH can fail after Sep-Dec passed (FT1 stopped at 2,153,529,344 bytes; LG4 and RC2 refused until the 26-part chain) [L V6-06, V6-51]; the margin under the cap is about 0.2 GiB [L V6-56]; COUNT and GRADE still detect in 2 coin halves [L V6-57].
- Variant pile-ups: at most 3 graded variants an idea, the 2nd and 3rd naming a result already read [L V5-07]; one variant per GRADE job keeps the novelty wait short [L V6-33, V6-39].
- Idle time: paperwork between jobs (four cards per idea, an audit after every job) took 28 to 53 pct of the time to the first PASS in round 1 [L V6-18]; sealing one idea at a time cost 6 to 23 min between COUNT and GRADE in round 4 [L V6-48].
- Hand-check harnesses: about 45 of AD3's 147 minutes [L V6-11]; use 3 cases from the helper's own output, with every raw input named in its last argument so each fire prints the inputs' values; the release has no raw-row reader, so there is no separate raw-row check [R7 F16].
- A skipped MONTH: no MONTH job is skipped on Sep-Dec numbers [L V6-47].
