# METRIC FAMILIES V1: what a detector can read, by forced trader (CLAUDE1_20261028, 2026-10-29T07:40:15Z from the clock). TEST, NOT REVIEWED.
Read this with FORCED_TRADE_MAP_V1.md when you GENERATE ideas. Every code named here is in METRIC_MENU_V1.tsv (488 METRICS_V1 VALUE codes whose
trap status starts with PROVEN; the detector refuses STOP, CAUTION and UNPROVEN codes in a condition). The menu's probe columns say where each
code's values sit (15 Oct 2025): 51 coin rows (coin scope), the MARKET row (read with the op market), or BTC's row only.

## Four traps the menu catches (each one cost a hand check on 29 Oct)
1. BTC row only (18 codes: C1.S15, C1.S16, C4.S06 to S10, C6.*): raw on an alt reads NaN and the detector gives ZERO fires with no error.
   Use a coin code "less BTC" (BTC's 15 min move = the coin's own 15 min price return in pct minus COIN_C3.S06; checked to 0.006 points).
2. Not readable (word codes: E1.S02 who pays, Z1.S02/S04/S05/S06/S08 calendar kinds, A4.S02, Z2.S05): build the number instead (sign(E1.S01)
   for who pays; Z1.S01/S03/S10 to S13 for print times).
3. A series that sits on a default (funding at 0.0001 per 8 h): its own percentile is the default itself. Put the line in the mechanism's
   units (a payment worth avoiding: 0.0005 per 8 h is 5 bp; 939 of 22,026 coin-settles cleared it Sep 10 to Dec 31).
4. Kind ROWS (16 codes, fire-scope): event rows, not a clock; not readable by raw.

## Families by forced trader (map row: families; the codes most ideas need)
| map row | trader | readable families | key codes (scope) |
|---|---|---|---|
| 1 | liquidated traders | A1 coin liquidations, A2 market count, A4 market waves, A5 forced per taker dollar, COIN_C2 own-percentile liquidation flags | A1.S05/S06 60 s (coin), A1.S08/S09 minute (coin), A1.S12/S13 (MARKET), A2.S05/S06 coins hit (MARKET), A4.S04/S05 wave age (MARKET), A5.S01/S02 (coin) |
| 2 | crowded, not yet liquidated | E1 funding, E2 open interest, A7 OI left since the wave began | E1.S01 (coin, fraction per 8 h), E2.S04 OI change 10 min pct (coin), A7.S01/S03 (coin), COIN_C3.S06 for BTC's move |
| 3 | stop orders past a level | engine ops on price; C11 day distances; C9 range touches; C10 legs | price, prior_max, prior_min, max, lag; C11.S01/S02 today, C11.S06/S07 yesterday, C11.S08 which side broke; C9.S11 touches |
| 4 | funding payers | E1, Z3 | E1.S01 (abs, sign), E1.S09 paid rate with E1.S04 interval, Z3.S01 minutes to settle (8 h or 4 h coins) |
| 5 | market makers with inventory | B1 taker flow, B2 one-sidedness, D1/D3/D4 book | B1.S03 net 5 min, B1.S08 buy per sell, B1.S09 now; D3 depth at the top |
| 6 | perp-spot arbitrageurs | E3 mark premium | E3.S01 premium bp (coin), E3.S02/S03 premium speed (MARKET) |
| 7 | news readers | Z2 GDELT | Z2.S02 (MARKET; read 15-30 min late) |
| 8 | alt quoters after BTC | C2, COIN_C3 | C2.S01 BTC minus coin 60 s, COIN_C3.S06 coin less BTC 15 min, C2.S04/S05 vs the middle coin |
| 9 | market-wide repricing | C2 breadth, C5 dispersion, C7 typical coin, A2 | C2.S06/S07 share moving the coin's way, C2.S02/S03 middle coin return, C2.S08 to S10 alts vs BTC |
| 10 | late small-fill chasers | B1 by fill size | B1.S05 net under 25k (retail), B1.S04 25k and up (whale), B1.S06 blocks |
| 11 | scheduled flows | Z1 calendar, Z3, hour_block op | Z1.S01 minutes to the next print, Z1.S03 since the last, Z1.S10/S11/S12/S13 flags (MARKET) |
| 12 | volatility-driven traders | C4 pace, C6 BTC vol units (BTC row), C9 range | C4.S04/S05 pace ratios (coin), C4.S01 to S03 moves |
Codes outside METRICS_V1 (the HL add-on catalogue, LEAD owner-cleared rows) pass the detector only through the chain's catalogues: check them
with metric_brief before use.

## Tool gap (proposed, TOOL_IMPROVEMENTS)
No detector op reads BTC's row onto every coin (the op market reads the MARKET row). A 'btc' op would open the 18 BTC codes to alt ideas.
