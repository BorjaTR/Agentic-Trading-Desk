# H04 KEY (SCOUT 2026-11-08, before any agent ran; source lean_v1/FAILURES_LOG.tsv rows on C1.S18, C1.S22-24, CTX)
Per idea 3 points: trap avoided (2), kill rule numeric (1).
I1 trap: C1.S18 has SCOPE BTC: read with op raw it exists only on the BTC row, so the rule would fire on BTC alone (C05 R3: 62 fires all on BTC). Right: op market (a market-row value) or flag it and check COUNT coins > 1 with --until 6 before GRADE; never op raw on coin rows.
I2 trap: C1.S22 (5 min market median) is a market code: op market, never op raw (EMPTY on coin rows); the hand check data lacked C1.S22-24 on coin rows (L02): best answer uses op market and flags the hand-check gap or uses C2.S02 (15 min) instead.
I3 trap: CTX readings are card readings, push-signed (positive = in the push direction) and not a DEF input: they are used only through state_split in round 2. Right: refuse as asked; build "coin fell more than the market" from codes (r15 minus C2.S02 with op market, sign checked) or move CTX.coin_vs_basket_15m to round 2.
Pass: >= 7/9 and all three traps named.
