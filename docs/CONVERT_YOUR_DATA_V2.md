# CONVERT_YOUR_DATA_V2: put the user's own data into the desk's one format

V2, 4 Nov 2026. TEST, NOT REVIEWED. For the user's agent (the agent working in this desk folder for its user).
The desk ships no market data and no converter. You write a small converter for this user's files, with the engine's own writer.
The format itself, with every source line: docs/DATA_FORMAT_V2.md (called FORMAT below; "FORMAT 4" = its section 4).
Short names (L3/, LAB3/, KIT/, TG/, HC, REF, OPINION) are FORMAT's.

## The rules (read them first)
1. Never invent a value. A value you cannot compute from the user's raw rows is left out (no code) or written empty with a reason.
2. Never fill a gap: no forward fill past a code's window, no 0 for "no data", no value copied from another venue or another coin.
3. 0 is a value only when the source was seen and showed none (REF: a minute with no liquidation holds 0.0, reason none; FORMAT 8, A1).
4. Write only with `lab3.bins.write_bins` and `lab3.write.write_part` (FORMAT 6). Never hand-made lz4, never a hand-made FORMAT.json.
5. Write into a new data folder. After the conversion it is read only. It must not overlap OUTPUT_ROOT and must not be inside alarm/
   [desk/desk.py:63-68]; paths only letters, digits and `_ . / -` [desk/desk.py:73-74].
6. Small first: 2 coins and 1 day, checked by hand against the source, before any full run (step 5).
7. The engine in alarm/ is read only. Keep the converter in the user's own folder, named in the conversion report with its sha16.
8. Any refusal (a tool, a check, a permission) is reported word for word and that step stops.

## Step 1. See what the user has
List, read only: the folders, the file kinds, the columns (the header row), the time stamps (unit, time zone, exchange or receive
time), the venues, the coins, the first and last day, the holes. Ask the user only what you cannot read. One question at a time.

Then check the fit:
| need | why | source |
|---|---|---|
| days 20250910 to 20251231 (warm-up from 20250820) | COUNT and GRADE read exactly these days; the hand check warm-up starts 20250820 | [KIT/jobs/JOB_COUNT_V7.job.sh.txt:14; HC:41] |
| days 20260101 to 20260430 for MONTH | MONTH reads Jan to Apr 2026 | [alarm/AGENTS.md step 10] |
| no day from 20260601 | research reads refuse them | [L3/law.py:18] |
| coins named as the roster (BTC, not BTCUSDT) | the jobs read the 52 roster coins only | [HC:24; FORMAT 10] |
| trades of each coin | PRICE (3 s bins) needs single trades; 1 min candles are not enough | [L3/bins.py:24, 57-58] |
| one non-price source (open interest, funding or liquidations) | TRUE needs a label that is not price; a decision without its TRUE row does not finish | [alarm/AGENTS.md step 5c and the TRUE paragraph; plugin/skills/desk-setup/SKILL.md section 4] |
Data that misses the 2025 days cannot run COUNT or GRADE in this edition: say so and STOP.
Data with price only can run COUNT and GRADE, but no TRUE: no idea can finish (a GO WITH GAPS at best).

## Step 2. Choose the parts
| the user has | build | leave out |
|---|---|---|
| trades (time, price, size, taker side) | PRICE; B1 to B3 only if their formulas are clear (FORMAT 8) | nothing else follows from trades alone |
| 1 min candles (OHLC) | C11.S01, S02, S05 (FORMAT 8, C11) | PRICE (needs trades) |
| liquidation orders (time, side, price, size) | A1 (FORMAT 8, A1) | A2, A4, A5, A7, COIN_C2 unless their formulas are clear |
| open interest at least every 61 s | E2.S02, E2.S04, E2.S07 | E2 from 5 min open interest (see 3d) |
| funding estimate with next settle time | E1.S01, E1.S03, E1.S04, Z3.S01 | E1.S09, S10 unless paid rates too |
| nothing | Z3.S02 (minutes to the next whole UTC hour) | |
| Hyperliquid fills by account with liquidation flag | X1.HL* (FORMAT 8, X1) | everything X1.HL* without them |
| order book | C1, C12, D1 to D5 only if their formulas are clear | |
Build a code only when its METRICS_V1 row (meaning, unit, window, empty_when) lets you write its formula without a guess. Else leave it
out and name it in the report. The catalog does not hold every formula (FORMAT 8, OPINION).

## Step 3. Map the source columns
The column names below come from the vendors' public files, not from this repo: check each one against the file's own header first.

### 3a. PRICE from trades (Binance aggTrades, Tardis trades, an exchange CSV)
| PRICE field | from a trade list of one coin and one UTC day |
|---|---|
| te | bin end: D0 + 3 s x (floor((t - D0) / 3 s) + 1), t = trade time in us; one bin a 3 s slot that holds a trade |
| tl | the bin's last trade time in us, a whole millisecond (ms x 1000) |
| px | the bin's last trade price |
| hi, lo | the bin's highest and lowest trade price |
| n | trades in the bin (aggTrades: sum of last_trade_id - first_trade_id + 1; OPINION) |
| buy, sell | dollars (price x size) of the bin's taker buys and taker sells (aggTrades: is_buyer_maker false = taker buy; OPINION) |
The writer's rules (te on the 3 s grid, tl in [te - 3 s, te), hi >= px >= lo, n >= 1) are FORMAT 4 [L3/bins.py:48-80].
Time stamps: Binance files give ms, Tardis gives us; use the exchange's trade time, in UTC.
Symbols: the coin name is the roster name. REF's PEPE, BONK and SHIB are priced as 1000-coin contracts (FORMAT 4): with
desk/data/download_binance.py pass `--coins 1000PEPE` (it adds USDT [desk/data/download_binance.py:63]) and write the coin as PEPE.
Download (Binance public files, checked against Binance's own checksum; the desk's yes first, never without it):
`python3 -B desk/data/download_binance.py <raw folder> --coins BTC,ETH --first 20251001 --last 20251001 --kinds aggTrades,klines_1m,metrics --dry`
then the same without `--dry` [desk/data/download_binance.py:5-12, 16-17]. Its MANIFEST.tsv holds each file's sha256 and checksum_ok.

### 3b. A1 from liquidation orders (Tardis liquidations, a recording of Binance forceOrder)
- A1.S08 (S09) = dollars (price x size) of long (short) liquidations whose exchange time is in (t_k - 60 s, t_k]; one row a minute end.
  Long liquidations are forced sells (they push price down [TOOLS/alarm_design/alarm_design_v3.py:36]); OPINION: in Tardis liquidations
  side "sell" is a long liquidated: check it on a known crash minute.
- A1.S01, S02 the same over 5 s at every 5 s end; S03, S04 over 30 s; A1.S12, S13 the sum over the roster coins seen, on the MARKET row.
- A row in the window counts only if it was received by t_k (Tardis local_timestamp <= t_k). known_at = t_k or the last receive time used,
  never later than t_k [FORMAT 5: k <= the column time].
- download_binance.py fetches no liquidation file (its kinds are klines_1m, metrics, aggTrades) [desk/data/download_binance.py:16-17].

### 3c. E1 funding and Z3.S01 (Tardis derivative_ticker: funding_rate, funding_timestamp)
- E1.S01 = the live estimate in force at t_k, scaled to 8 h: funding_rate x 8 / interval hours (OPINION, from METRICS_V1's own
  recompute of S05: "each coin's funding_rate x 8 / its interval" [LAB3/METRICS_V1.tsv:807]). Empty (STALE_VALUE) when the last row is
  older than 61 s [LAB3/METRICS_V1.tsv:797 window, empty_when].
- E1.S03 = the next settle time in us; E1.S04 = the interval in hours. REF, 20251001: E1.S03 = 00:00 at 00:00, then 08:00; E1.S04 = 8.
- Z3.S01 = (E1.S03 - t_k) / 60 s. REF, 20251001: 0 at 00:00, 479 at 00:01, 1 at 07:59, 0 at 08:00.
- Binance's public funding history holds paid rates only: E1.S09 and S10, not the live estimate S01 (OPINION).

### 3d. E2 open interest (Tardis derivative_ticker open_interest; Binance metrics files)
- E2.S02 = open interest in contract coins in force at t_k, empty (STALE_VALUE) when the last row is older than 61 s [LAB3/METRICS_V1.tsv:822].
- E2.S04 = 100 x (S02 at t_k / S02 at t_k - 600 s - 1), empty when either is empty (OPINION from "changed in the last 10 minutes, percent").
- Binance metrics files hold one open interest every 5 minutes (sum_open_interest): 4 of 5 minutes would be older than 61 s. Do not
  carry them: leave E2 out, or write those minutes empty with STALE_VALUE and say how few minutes are left (OPINION).

### 3e. C11 from 1 min candles (Binance klines_1m: open_time, high, low, close)
- At the minute end t_k: today's high H = the highest high of the minutes closed by t_k since 00:00 UTC; low L likewise; P = the close of
  the minute that ended at t_k. METRICS_V1: S01 "how far the last price is under today's high, in percent; 0 = at the high"
  [LAB3/METRICS_V1.tsv:352]. The exact formula is not in this repo: OPINION 100 x (H - P) / P; prove it (step 5) before any rule reads it.

### 3f. X1 Hyperliquid
- Needs Hyperliquid fills by block, by account, with the liquidation flag and each account's position change (FORMAT 8, X1).
  This repo names no public file that holds them. Without them leave every X1.HL* code out.

## Step 4. Write the parts
- One row a coin a code at every step end t_k of the day (as_of = t_k), as REF does (FORMAT 5). value_kind 1 with the value's bits, or
  value_kind 0 with an empty_reason word when the source cannot give it at t_k (a hole, a stale row, a coin not listed). The writer keeps
  no maximum age (FORMAT 3): a missing empty row lets an old value answer later steps as if it were fresh.
- Reason words: use the ones METRICS_V1 lists for the code (empty_when), e.g. NO_FILE, TRADES_HOLE, THIN_FEED, STALE_VALUE, NO_PRIOR_DAY
  [LAB3/METRICS_V1.tsv:14, 352, 797, 822]. Any reason makes the cell UNKNOWN to the detector (e != 0) [FORMAT 5].
- A coin with no source that day: leave it out of the part's coins (it reads ABSENT) [L3/days.py:296-299]; in PRICE list it in
  `missing`, never in coins [L3/bins.py:146-149].
- Market codes: one row named MARKET [L3/write.py:390-411].
- sources: every raw file with its sha16; seal: one text naming the converter and its sha16 [L3/write.py:415-422; L3/bins.py:12].
- `no_prev: True` only on the first day the source holds [L3/write.py:10-11].
- Size, REF 20251001: PRICE about 42 MB a day for 51 coins; BASE (992 codes) about 358 MB a day.
The write example in FORMAT 6 ran on 4 Nov 2026 (FORMAT 7).

## Step 5. Prove the conversion before any use
Recomputing your own formula on your own rows is not a check. Each check compares with something you did not write.
5a. One coin-day first (BTC, 20251001), then 2 coins and 2 days (BTC, ETH, 20251001 and 20251002).
- Raw against source: each downloaded file's checksum_ok in download_binance.py's MANIFEST.tsv; the file's row count and first and last
  time; no time outside the day.
- PRICE against 1 min candles (an outside record): for 10 minutes (00:00, the busiest minute, 23:59, and 7 more), the sum of n equals
  the candle's trade count, buy + sell equals its quote volume, buy equals its taker buy quote volume, the last px equals its close, the
  max hi and min lo equal its high and low. Print both sides. A difference is explained or the part is not used.
- A1: on 3 minutes with liquidations, print the raw rows and the stored value side by side; on a known crash minute the sum is large.
- E2.S02: against Binance's published 5 minute open interest (metrics file) at 10 marks: the lab's agreed within 1% in 98.3 to 99.8% of
  marks [LAB3/METRICS_V1.tsv:822 read_as].
- E1.S01: one minute before a settle it is near the paid rate (S01 equalled the paid rate in only 16 to 43% of settles, off by about
  0.0001 points [LAB3/METRICS_V1.tsv:797 read_as]).
- C11: against the candles' own high and low by hand at 5 minutes; S01 is 0 at the day's high.
5b. The engine reads it:
- Read back with `lab3.days.Days(<data>/lab_days, 'research')`: shapes, a value at 3 chosen steps, the reason texts (FORMAT 6).
- The hand check, price only, 5 coins, 2 days (the desk's own test definition):
  `python3 -B desk/desk.py run 01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_defs_v4_to20251231.py S <repo>/desk/tests/data/SAMPLE_DEF_V1.json 20251001 20251002 BTC,ETH,SOL,XRP,DOGE 20 px,move`
  It must end with a `fires ... per coin` line. On REF's data it printed 88 fires (BTC 28, ETH 27, SOL 28, XRP 5) (FORMAT 7).
- For each converted code: a one-line definition that reads it, through the same hand check; at 0 fires its HINT line gives the share
  of numbers, EMPTY when none [HC:2-6]. Then `metric_brief_v2.py <CODE>` for its unit and window [alarm/AGENTS.md step 2].
5c. The sample check: `python3 -B desk/data/sample_check.py <DATA_ROOT>/lab_days` compares with the lab's own index bytes
[desk/data/sample_check.py:8-11]. Your own data will print CHANGED or MISSING and `SAMPLE FAILED`: expected, because an index holds its
build time and sources [L3/write.py:492-494]. Pin your own sample instead, once the checks above pass:
`python3 -B desk/data/sample_check.py <DATA_ROOT>/lab_days --manifest <OUTPUT_ROOT>/setup/MY_SAMPLE_V1.tsv --make 20251001,20251002 BTC,ETH,SOL,XRP,DOGE PRICE,<your parts>`
then the same without `--make ...` after every rebuild must say `SAMPLE OK` [desk/data/sample_check.py:5-6, 23-39]. Days of 2025 only
[desk/data/sample_check.py:48-49].
- `python3 -B desk/desk.py tests` runs desk/tests/test_sample_data_v1.py, which expects the lab's sample: on your own data its test
  test_sample_is_there_and_unchanged fails (it reads the lab manifest). Report it as that, not as a broken conversion.
5d. `python3 -B desk/desk.py setup` then `python3 -B desk/desk.py check`. Expected lines: EMPTY for HL_FILLS, RUNNER_RELEASE, FEED_GATE;
`DATA CHECK NOT BUILT` (no schema check ships) [desk/desk.py:218-224]; `RELEASE GRADE OK` and `RELEASE MONTH OK` need the Python the
release pins (3.11.3): with 3.10 they print REFUSED "python 3.10.12, release pins 3.11.3" (seen on 4 Nov 2026).
5e. Only now the full conversion (all coins, all days), then 5b on a quiet week and the crash week: `hc_size_v1.py S <DEF.json>` reads
20251110 to 20251117 and a week with 10 Oct 2025 [alarm/AGENTS.md step 4].

## Step 6. What a user cannot run without some data
| missing | families that cannot run | source |
|---|---|---|
| liquidations (LIQ_BN) | A1, A2, A4, A5, A7, COIN_C2, X1.LIQX; a definition truth of kind forced_usd; the first look's FORCED blocks read NaN | [TG/build_families_v1.py:16-17, 26; TOOLS/alarm_design/alarm_design_v3.py:36; PROFILE:73, 262-271] |
| Hyperliquid fills and positions (HL_FILLS, HL_POS) | X1.HLFLOWX, X1.HLLIQX, X1.HLPOSX, X1.HLPOSM, X1.HLPX; E2.S05, E2.S06; X1.POSX.S02, S05 | [TG/build_families_v1.py:28-29, 34, 37-38] |
| open interest (OI_BN) | E2.S01 to S04, S07; A7; COIN_C2; X1.POSX OI codes | [TG/build_families_v1.py:17, 33, 39-40] |
| funding (FUNDING_BN) | E1; Z3.S01; X1.POSX funding codes | [TG/build_families_v1.py:21, 37-38; LAB3/METRICS_V1.tsv:1003] |
| order book (BOOK_BN) | C12, D1 to D5, X1.BOOKX, X1.COST; C1 (mid) | [TG/build_families_v1.py:19-20, 26; LAB3/METRICS_V1.tsv:228] |
| every non-price source | TRUE (its label may not read price), so no finished decision | [alarm/AGENTS.md step 5c] |
| trades | PRICE, so nothing at all | [TOOLS/idea_to_grade/detect_v2.py:44] |
Liquidated traders (forced-trader map row 1) need A1 [KIT/METRIC_FAMILIES_V1.md:17]. Without liquidations and Hyperliquid the user can
still study rows 2 to 12 where the data holds their families (open interest, funding, price levels, calendar).

## Step 7. Report and hand over
Write `OUTPUT_ROOT/setup/CONVERSION_REPORT_<YYYYMMDDTHHMMSSZ>.md` (stamp from the clock): the raw files with sha16, the converter and its
sha16, days, coins, each part and code built, each code left out with why, each check of step 5 with its printed result. Then go back to
the desk-setup skill (section 3): GO WITH GAPS names every family of step 6 the data cannot serve.
