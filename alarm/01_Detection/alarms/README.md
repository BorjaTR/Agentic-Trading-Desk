# tools/alarms: the alarm bench of the research desk (SCOUT, 20 Oct 2026; the owner 19:00 to 19:12 Berlin)
The owner's alarm test: does the moment offer more money than a random moment, on either side, and enough to cover a round trip?
- alarm_offer_v1.py: for an alarm's fires (EVENTS: coin, t, side, S, mode) on some days: the biggest move either way after the fire at
  15, 30, 60 min (BED's opportunity(), imported from team/BED/scripts/cusum/frozen_c22) vs 6 random moments a coin-hour; per cost third;
  the ratio with a whole coin-day band; the share covering 1, 2, 3 round trips of the coin's own cost (COSTS_PER_COIN_V2).
- a01_onset_v1.py: A01 FORCED ONSET exactly as team/RESEARCH/alarms/A01_FORCED_ONSET_SPEC_V1.md, with a second computation (plain loops)
  for the proof that we find the moments.
- alarm_offer_v1.py is SUPERSEDED by tools/alarm_check/alarm_bench_v1.py (QUANT; one computation, proven against BED); every offer now goes there.
- a01_onset_v2.py: A01 forced onset (card alarms/A01_FORCED_ONSET_CARD_V1.md), sliding-window sums (L23), a plain-loop twin.
- a03_wave_v1.py, a03_inwave_v1.py: A03 market forced wave (card NOT KEPT as an alarm; context for step 2).
- a02_climax_v3.py: A02 forced climax (card alarms/A02_FORCED_CLIMAX_CARD_V1.md s2): find_episode and a plain-loop twin, held, meaning (D2).
- a02_grid_v1.py: the A02 tuning grid (18 settings G x D x Q) in one pass; GRID_FIRES.tsv and the union of moments for one bench.
- a02_grid_read_v2.py: the declared tuning read (card s3b): choice on FIND without 10 Oct by the plateau rule, CHECK Nov-Dec, no row near
  CONFIRM. v1 superseded before use. Known limit: it forms CHECK for every setting (slip 18:19:25Z); v3 forms it for the choice only.
Every new alarm: a spec in team/RESEARCH/alarms/<ID>_SPEC_V1.md, a finder with planted tests and a second computation, then the offer test.
Runs as runner jobs (lab3 needs pyarrow). Owner SCOUT. Reviewer QUANT. Status DRAFT (BASELINE.tsv).
- onset_band_v4.py (QUANT, landed 20 Oct 2026 by SCOUT's delegation 20:13:03Z; SCOUT reviewer): THE OWN-BAND ONSET finder (rule
  alarms/ONSET_RULE_QUANT_V1.txt 6851e4e6) for N5 FLOW BURST (card N5_FLOW_BURST_CARD_V1.md), N2 V2 WHALE SWEEP, N3 V2 BOOK THINS, N9 V2
  SPREAD BLOWOUT (all four PROVEN: detection, offer every way, SCOUT's blind rebuilds, the rerun rows) and N4 V2 OI JUMP (not proven: its
  D2 has no independent positions record yet). x(k) of one coin at the code's own clock; the edge of day D = a percentile of the coin's
  clean x over its history days among the 14 built days before D; FIRE at the first step past the edge after a clean step not past it
  (V2: a run of r steps; N4 V2: Hyperliquid's own move the same sign), more than 15 min after the coin's last fire, across midnight.
  A plain-loop twin for D1; the D2 columns per card. Usage: python3 onset_band_v4.py <alarm N2|N3v2|N4v2|N5|N9v2> <lab_days> <lab3 code>
  <out dir> <first day> <last day> <last readable day> <coin> ...; writes <A>_EVENTS.tsv (the desk bench's input), <A>_FIRES.tsv, <A>_PROOF.txt.
  Tests test_onset_band_v4.py. Catalogue rows N5-*, N2-*, N3v2-*, N4v2-*, N9v2-*, V2-U.
- n1_busy_burst_v2.py (QUANT, landed as above): N1 v2 BUSY BURST (card N1_BUSY_BURST_CARD_V2.md, PROVEN): the first 5 s step at which the
  coin's Binance trades in the last minute (X1.FLOWX.S10) rise above max(its own edge, 2 x the median of its last 60 clean minute ends,
  at least 30) after a clean step at or under it; 15 min refractory per coin across midnight. Usage: python3 n1_busy_burst_v2.py <lab_days> <lab3 code> <out dir> <first day> <last day> <coin> ...; writes
  N1_EVENTS.tsv, N1_FIRES.tsv, N1_PROOF.txt. Tests test_n1_busy_burst_v2.py. Catalogue rows N1-*.
- k0_busy_now_v1.py (QUANT, landed 20 Oct 2026; PROVEN: SCOUT 20:32:27Z): K0 PRICE SWING (card alarms/K0_BUSY_NOW_CONTROL_CARD_V1.md):
  the coin's 60 s price range (our 3 s bins, last trade time in (t - 60, t]) over its own band of the 14 built days before D, five levels
  (99.0, 99.5, 99.8, 99.9, 99.95) in one pass, the own-band onset (helpers imported from onset_band_v4). Usage: python3 k0_busy_now_v1.py
  <lab_days> <lab3 code> <out dir> <first day> <last day> <last readable day> <coin> ...; writes K0_<q>_EVENTS.tsv, K0_FIRES.tsv,
  K0_PROOF.txt. Tests test_k0_busy_now_v1.py. Catalogue rows K0-*.

## onset_band_v6.py (QUANT, landed 2026-10-21T00:10:31Z)
= onset_band_v5 + v4 (af9b49e6, still here for its sealed rows) with two new alarms, both PROVEN tonight:
- Q1 OFI BURST (card alarms/Q1_OFI_BURST_CARD_V1.md 477a74fd): |X1.BOOKX.S04| beyond the coin's own 99.9th pct (14 built days), own-band
  onset, refractory 15 min; bench side = the book's sign; the 60 s price way in Q1p_EVENTS.tsv. Beside: Q1b (99.5).
- Q4 BASIS JUMP (card alarms/Q4_BASIS_JUMP_CARD_V1.md eb124211): |E3.S01(k) - E3.S01(k - 1)| beyond its 99.9th pct; side = sign of the
  change. Beside: Q4b (99.5), Q4c (5 min change).
Usage: python3 onset_band_v6.py <alarm> <lab_days> <lab3 code> <out> <first> <last> <last readable> <coin> ... ; tests test_onset_band_v6.py.
Evidence: DEV J33448-49, J33471-72; offers J33462 (x2.20, without 10 Oct x1.73) and J33489 (x2.68, x1.51); prefix J33451, J33474; SCOUT
rebuild J36089. Rows Q1-*, Q4-* in ALARM_CHECKS_V1.tsv.

## b8_roll_v1.py (QUANT, landed 2026-10-21T01:11:13Z)
B8 ROLL SPREAD SPIKE (card alarms/B8_ROLL_SPREAD_CARD_V1.md): Roll's spread of the 3 s bin closes over the last 15 min beyond the coin's
own 99th pct (14 built days), onset, refractory 15 min (the chain from the first day read, card s2 note); bench side the 60 s way. Beside:
99.5 (B8a), 5 min (B8b). Usage: python3 b8_roll_v1.py <lab_days> <lab3 code> <out> <first> <last> <last readable> <coin> ...; tests
test_b8_roll_v1.py. Evidence: DEV J33492-93, offer J33502 (x1.53, without 10 Oct x1.37), prefix J33508, SCOUT rebuild J36103-04. Rows B8-*.

## b7_wide_pressed_v1.py (QUANT, landed 2026-10-21T01:54:09Z)
B7 WIDE AND PRESSED (card alarms/B7_WIDE_AND_PRESSED_CARD_V1.md): at a 5 s step the half spread X1.COST.S01 and |X1.BOOKX.S04| both beyond
the coin's own 95th pct (beside 99th) over the history days' clean steps (both codes finite), onset, refractory 15 min (the chain from the
first day read, card s2 note); side the sign of S04. Usage: python3 b7_wide_pressed_v1.py <lab_days> <lab3 code> <out> <first> <last>
<last readable> <coin> ...; tests test_b7_wide_pressed_v1.py. Evidence: DEV J33445-46, offer J33457 (x1.61, without both storm days
x1.50), prefix J33450, SCOUT rebuild J36116-17. Rows B7-*.

## o1_flush_v2.py (QUANT, landed 2026-10-21T02:24:05Z)
O1 LONG FLUSH / O2 SHORT SQUEEZE (card alarms/O1_OI_FLUSH_CARD_V1.md): at a minute end the 10 min fall of Binance OI in coins (E2.S02, a
carried row E2.S03 not valued) beyond its 1st pct AND the 10 min price move beyond its 90th pct of |g| (edges over the minute ends with
both finite, 14 built days), onset after a valued minute end, refractory 30 min per side; side the price way (O1 -1, O2 +1). Beside: A
(0.5 pct), B (75th). M1 reads the coin's own A1.S08 / A1.S09. Usage: python3 o1_flush_v2.py <lab_days> <lab3 code> <out> <first> <last>
<last readable> <coin> ...; tests test_o1_flush_v2.py. Evidence: DEV J33469-70, offers J33479 (O1 x1.65) and J33484 (O2 x1.68), prefix
J33473, SCOUT rebuild J36120-21. Rows O1-*.

## alarm_view_v1.py (QUANT, AV1, landed 2026-10-21T07:07:14Z; the owner 08:34-08:35 Berlin 21 Oct: "build something on top ... so we do it once only")
THE LAYER every new alarm reads through. One continuous minute-end timeline over the run (t = d x 1440 + j is day_d 00:00 + 60 j);
View(lab_days, lab3, first, last, coins, before) gives any lab code on it (5 s column 12 j, 30 s 2 j, 1 min j: known at t), prices and
age from the bins (last trade at or before t, integer microseconds, carried over midnight), trades per minute (bin_counts), and lists
every unread day-code in View.skipped. Causal tools: lag, roll (sum/mean/count/median/pct/std/max/min of the n values ending at t or
before t), fresh_move, day_edge (the hist built days before d, or window='calendar'), onset (the cards' one-day chain), card_t (a card's
minute j for ends 'j' or 'j+1'). THE LOOKAHEAD PROOF IS MADE ONCE, HERE: test_alarm_view_v1.py plants garbage after many cuts and every
tool's values up to the cut stay the same; fakes of lab3's Days and read_bins test the loaders (a trade at t + 1 us unused at t, coin
order, absent coin, carry, 5 s columns). A port on the layer runs the whole period in one call with no per-fire prefix runs: all DEV
(111 days x 52 coins) in 30 to 60 s, against about 1 to 3.5 h for the per-day v1 code. Equality: o34_band_v3, q2b4q10_v3, o5_both_v2,
o6o8q5_v2 equal their v1/v2 code on EVERY output line over all DEV (J33572: 45,832 + 126,954 + 1,515 + 5,540 lines). Review: SCOUT
PASS WITH 6, all taken (SCOUT/receipts/REVIEW_QUANT_ALARM_VIEW_V1.md 31a10fec, QUANT/receipts/ANSWER_REVIEW_ALARM_VIEW_V1.md 3fddfe78).
std runs by numpy windows (pandas 2.3's rolling std drifts after a spike). Tests: test_alarm_view_v1.py (run them on the Mac's pandas).

## o5_both_v2.py (QUANT, landed 2026-10-21T07:07:14Z; o5_both_v1.py beside it as the reference its test compares with)
O5 DELEVERAGING ON BOTH VENUES (card alarms/O5_DELEVERAGE_BOTH_CARD_V1.md 14cc7704, FROZEN) on alarm_view_v1: Binance 10 min OI change
(E2.S04, fresh at t and t - 10) below its 1st pct AND some Hyperliquid 10 min OI change (E2.S06) below its own day's 1st pct in t - 9 .. t
(edges: 14 built days, 1,000 a day, 2 days); onset, refractory 60, one-day chain; side the 10 min price move; S = b / eb. M1: 10 min
liquidations above the day before's 90th pct. Usage: python3 o5_both_v2.py <lab_days> <lab3 code> <out> <first> <last> <coin> ...;
tests test_o5_both_v2.py. Evidence: DEV J33537 (v1), offer x2.69 (no 10 Oct x1.61, no D3 days x1.51), M1 0.655, v2 equal on every line
(J33569, J33572), SCOUT rebuild J36168 1,515 of 1,515. Rows O5-* (proof 4 by SCOUT).

## q16_vwap_v1.py (QUANT, landed 2026-10-21T07:56:09Z; with alarm_view_v1 6e25ccaf: + bin_minutes)
Q16 TAKER VWAP PRESSURE (card alarms/Q16_VWAP_PRESSURE_CARD_V1.md d6ddf4a2, SCOUT PASS WITH 2): at a minute end the dollar-weighted price
of the minute's taker buys (sells) from the 3 s bins (te in (m - 60, m], 1,000 USD and 3 bins a side) sits above (below) the book mid
C13.S05 of m - 60 by more than its 99.5th pct (14 built days); onset, refractory 30, one-day chain; side the pressure; S = g / e. BESIDE
Q16B (SCOUT item 1): the same against the mean of the mids at m - 60 and m (the minute's drift out). M1 the mid moved the side's way
(WEAK: near mechanical for the main, 0.996; the beside 0.686). Usage: python3 q16_vwap_v1.py <lab_days> <lab3 code> <out> <first> <last>
<coin> ...; tests test_q16_vwap_v1.py. Evidence: DEV J33579; offers main 1.76x [1.73] (without 10 and 11 Oct 1.70x), beside 1.65x
[1.62] (without 10 Oct 1.56x) (J33585, J33586, J33592); SCOUT blind rebuild J36221 (main 35,546 of 35,546; beside 38,717 of 38,717 with 2 traced to the VALUED wording, card s7); rows Q16-*.

alarm_view_v1.py 6e25ccaf (re-landed 2026-10-21T07:56:09Z with Q16): + minute_sums and View.bin_minutes (any per-bin values summed over (t - 60, t] by bin end time), tested on the fakes; nothing else changed, so the O5 rows and outputs stand.
Q16 status (QUANT 2026-10-21T08:11:40Z): PROVEN, WEAK MEANING (SCOUT proof 4 J36225 REPRODUCED). Read Q16B (drift out) as the pressure alarm; the main Q16 fires mostly in fast minutes (73 pct), its M1 is near mechanical.
