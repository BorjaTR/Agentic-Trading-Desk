# MECHANISM_MAP_V1: alarms pooled by cause (STRATEGY owns it; 2026-11-06T08:20Z; DRAFT, PLAYGROUND, not reviewed)
The three layers (the owner 2026-11-06T07:54Z: "The whole edge will be in our analysis. An alarm itself has no edge."; SCOUT hb/SCOUT.txt
08:00:09Z lines 2502-2503; STRATEGY decision 08:01Z, STATE decisions rev 103):
1. ALARM: an event with enough offer around it; no edge is claimed.
2. MECHANISM: alarms pooled by cause, so a strategy gets a sample big enough to prove something (ALARM_NEED_V1.md N1, N2).
3. STRATEGY: inside one MECHANISM, entry, market and coin per wave find what is cashable and why (STRATEGY_HUNT V2).
KIND keeps its ALARM_BUILD meaning (where an alarm fires, as-of or AFTER, never an edge split; QUESTIONS_V13 near line 465, cards K36,
K40-K42). It is not used here.

## How an alarm joins a mechanism (rule of this map)
- At CLAIM, the alarm card names ONE mechanism id of this map, with this map's sha16.
- At GRADE, membership is proven by the as-of share of the alarm's fires where the mechanism's membership rule holds at the fire second
  (DECISION fields only, CONTRACT_V3 R). A member needs that share >= 0.90 on the opened months it is graded on (STRATEGY proposal; SCOUT may
  set the number). Fire counts never prove membership.
- A control alarm has the same move and lacks the cause; it is graded beside the members, never pooled with them.
- Source rows: the forced-trade map of the alarm kit, KIT_V5/FORCED_TRADE_MAP_V1.md (release ALARM_V1_21_16, Agentic/tree/ALARM_DESIGN,
  sha16 84949bf3c749d985), one mechanism per forced trader row; rows not yet used here are listed at the end.

## Mechanisms
| id | cause in words | membership rule over card fields (at the fire second) | members | control | source |
|---|---|---|---|---|---|
| FORCED_OUT | leveraged longs are closed by force (exchange liquidation, positions leaving) and sell at market into a falling coin; someone absorbs them and the price comes back if the selling was only forced | side FADE of a down move AND Binance long liquidations over 15 min above the coin's own p90 (A1.S08 family) AND Hyperliquid open interest falling over the last 10 min (E2.S06 / hloi) | FDAOI (PG_FDAOI_DEF_V1_1 cc2a8887ee33b5c9), FDAOIV (PG_FDAOIV_DEF_V1 be14d1633a009873) | FDONLY (PG_FDONLY_DEF_V1 ffb49d05fa32a55c): the same down move, no liquidation and no open-interest condition | forced-trade map row 1 (liquidated traders) |
| FORCED_OUT_SHORTS | leveraged shorts are closed by force and buy at market into a rising coin | side FADE of an up move AND Binance short liquidations above own p90 AND Hyperliquid open interest falling | candidates FUOI (e75f1233300950d9), FUOIV (7ee36dd8beb1051d); not graded on their own (sell) side | none yet | row 1, up side |
| CROWDED_LATE | crowded leveraged traders not yet liquidated, whose margin breaches as the price keeps going | not defined yet (funding E1.S01, OI change E2.S04 with a BTC move against the crowd) | none | none | row 2 |

## Rows of the kit map not yet used (no member alarm in STRATEGY's work; listed so the map is complete, no rule written)
row 3 stop orders beyond a level; row 4 funding payers; row 5 market makers with inventory; row 6 perp-spot arbitrage; row 7 news
reactions; row 8 alt quoters lagging BTC; row 9 market-wide repricing (not forced); row 10 late small-fill chasers; row 11 scheduled flows;
row 12 volatility-driven traders. Each becomes a mechanism row only with a membership rule and a source.

## Open
- O1 the membership share threshold (0.90 here) and how GRADE computes it: for SCOUT (ALARM_BUILD MECHANISM line, next version).
- O2 FDAOIV fires that are not FDAOI fires (700 of 2,090 in Sep-Dec 2025; STRATEGY check 08:08Z) come from a different condition set or
  universe; why is not checked.
