# DATA_FORMAT_V2: the one format the engine reads

V2, 4 Nov 2026. TEST, NOT REVIEWED. For the user's agent. Read this before docs/CONVERT_YOUR_DATA_V2.md.
The desk ships no market data and no converter. This page says what the engine reads, so an agent can write the user's data in that form.

## How to read the sources
Each statement ends with its source: `[file:line]`. Short names:
| short | path from the repo folder |
|---|---|
| L3/ | alarm/01_Detection/tree/team/LAB3/code/lab3/ (the one reader and the one writer) |
| LAB3/ | alarm/01_Detection/tree/team/LAB3/ |
| TOOLS/ | alarm/01_Detection/tree/team/RESEARCH/tools/ |
| KIT/ | alarm/Agentic/tree/ALARM_DESIGN/KIT_V5/ |
| TG/ | alarm/03_Grading/tree/tools/true_gate/ |
| CHAIN | alarm/03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_7_to20251231.sh |
| HC | alarm/01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_defs_v4_to20251231.py |
| PROFILE | alarm/05_Profile/tree/tools/alarm_profile_v2/alarm_profile_v2_3.py |
| REF | the lab's own one-format store (not shipped), read on 4 Nov 2026: what is seen there, not a rule of the code |
| OPINION | not in the code: the writer's judgment |
File pins on 4 Nov 2026 (sha256, first 16): L3/days.py ecf85ffb7bc0fa69, L3/write.py 99e43dc0bc01f55a, L3/bins.py f5c0f9a5f9cb8537,
L3/asof.py d511d6af57eb9d3a, LAB3/METRICS_V1.tsv 85b14987d2059cd6.

## 1. The layout
```
DATA_ROOT/lab_days/FORMAT.json
DATA_ROOT/lab_days/day=YYYYMMDD/PRICE/index.json      prices: kind BIN (required)
DATA_ROOT/lab_days/day=YYYYMMDD/PRICE/BIN.<field>.lz4
DATA_ROOT/lab_days/day=YYYYMMDD/<PART>/index.json     metric codes: kind CLOCK (any part name)
DATA_ROOT/lab_days/day=YYYYMMDD/<PART>/<code>.<field>.lz4
DATA_ROOT/lab_days/day=YYYYMMDD/<PART>/REASONS.txt    the part's reason texts, one JSON string a line
DATA_ROOT/lab_days/day=YYYYMMDD/<PART>/WORDS/<code>.txt
DATA_ROOT/research_days/                              the research store (section 9)
```
- The desk reads `DATA_ROOT/lab_days` and `DATA_ROOT/research_days` [desk/desk.py:83].
- The layout of a part, index.json written last [L3/days.py:6-8].
- A part is a folder that holds index.json, with no `.tmp_` and no `.aside_` in its name [L3/days.py:100-101].
- A day is a UTC calendar day: `day=YYYYMMDD` starts at 00:00 UTC [L3/days.py:90-92].
- A missing index.json is refused as NotBuilt, never served as "no value" [L3/days.py:176-180].
- A code must sit in exactly one part of a day: none is NotBuilt, two is Duplicate [L3/days.py:207-213].
- A part may name input parts with their index sha16; a changed input is refused as StaleInput [L3/days.py:214-221].
- The part name of a code is free: the reader finds the code through every part's `readings` [L3/days.py:193-205].
  The lab keeps METRICS_V1 codes in part BASE and add-ons in parts X1.<GROUP> [KIT/METRIC_MENU_V2.tsv column part; REF].
- The price part is named PRICE: the writer's default [L3/bins.py:28], the detector reads `index(day, 'PRICE')` [TOOLS/idea_to_grade/detect_v2.py:376].

## 2. FORMAT.json
The writer writes this, and refuses a root whose FORMAT.json differs [L3/write.py:30-33, 345-360]:
```
{"absent": {"a": -2147483648, "e": 255, "k": -9223372036854775808, "o": -9223372036854775808, "v": "NaN", "w": -1}, "block": "(coins, steps) C order", "clock": "column k = the value as known at t_k = D 00:00 UTC + step x k (edition 2 rule)", "codec": "pyarrow lz4 frame", "dtype": {"a": "<i4", "e": "|u1", "k": "<i8", "o": "<i8", "off": "<i8", "u": "<i8", "v": "<f8", "w": "<i2", "x": "|u1"}, "edition": 3, "rule": "C1 as-of (lab3/asof.py)", "steps": [3, 5, 30, 60], "store": "lab_days"}
```
- These bytes (sha16 f5b92c13036c6eb6) are REF's FORMAT.json, and the shipped writer wrote the same bytes in a test on 4 Nov 2026 (section 7).
- The reader checks only `"edition": 3` [L3/days.py:131-136]. A `layout` key sends the root to another reader (evt1) [L3/days.py:108-121]: never write one.
- Never write FORMAT.json by hand: let the writer write it [L3/write.py:345-360].

## 3. Time basis (every part)
- Times are microseconds since 1970 UTC, int64 [L3/days.py:25; L3/bins.py:23; LAB3/METRICS_V1.tsv:3 (timestamp_us)].
- A CLOCK code has a step of 5, 30 or 60 s [L3/write.py:28]. Column k of day D is the value as known at t_k = D 00:00 UTC + step x k,
  k = 0 to 86,400 / step - 1 [L3/write.py:101-103, 115-117; FORMAT.json "clock"].
- The as-of rule [L3/asof.py:5-11; L3/write.py:85-98]: each source row has `as_of_us` (the time the value is about) and `known_at_us`
  (when it was known). The answer at t_k is the last row, in key order, with as_of <= t_k and known_at <= t_k. Rows with a null as_of or
  known_at are never kept. 00:00 to 00:59 also reads the rows of day D-1 [L3/asof.py:19; L3/write.py:101-111].
- No row known: reason NO_ROW_KNOWN [L3/asof.py:21].
- The writer keeps no maximum age: the last row answers every later step end of that day, with a growing age `a` [L3/write.py:85-98, 240].
  So a value that must not be carried needs its own empty row with a reason (CONVERT section 4).
- The engine puts every input on a 5 s clock by this rule: base step j takes column floor(j x 5 / step)
  [TOOLS/alarm_design/alarm_design_v3.py:201-210]. A step that is not a multiple of 5 or does not divide the day is refused, NATIVE_CLOCK
  [TOOLS/idea_to_grade/detect_v2.py:407-409].
- PRICE bins: 3 s bins; the bin end te is on the 3 s grid of the day; the last trade tl is in [te - 3 s, te) [L3/bins.py:24, 73-74].

## 4. Kind BIN: the PRICE part
Files: `BIN.<field>.lz4` for off and the 8 fields; in each file one lz4 frame a coin, back to back [L3/bins.py:16-18, 125-134].
| field | dtype | what it holds | source |
|---|---|---|---|
| off | <i8 | coins + 1 offsets: coin i's bins are rows [off[i], off[i+1]) | [L3/bins.py:27, 151-152, 165] |
| te | <i8 | bin end, us; a whole second; on the day's 3 s grid; rising; in (D 00:00, D + 1 day] | [L3/bins.py:59-60, 72-75] |
| tl | <i8 | time of the bin's last trade, us; a whole millisecond; in [te - 3 s, te) | [L3/bins.py:59-60, 74] |
| px | <f8 | the bin's close (its last trade price), > 0; hi >= px >= lo | [L3/bins.py:69-71] |
| hi, lo | <f8 | highest and lowest trade price of the bin | [L3/bins.py:70-71] |
| n | <i4 | trades in the bin, a whole number >= 1: a bin exists only when it holds a trade | [L3/bins.py:57-58; "Present 3 s bins only" L3/bins.py:4] |
| buy, sell | <f8 | dollars traded in the bin, by side | [the PX3S source columns buy_usd, sell_usd: alarm/01_Detection/tree/team/BED/scripts/e_fill/fill_v2.py:73; bins "array for array" L3/bins.py:4-5] |
- buy, sell side: OPINION: buy = trades where the buyer took liquidity (the taker bought). The code names the columns only.
  REF, BTC, 20251001: buy + sell is about 20.1 billion dollars for the day (sum of both fields).
- Price units: dollars per contract unit. REF prices PEPE at 0.0093, BONK at 0.019, SHIB at 0.012 on 20251001 (1000-coin contracts).
  PROFILE:76 names the lab's 1000-coin contracts.
- Every listed coin with bins is checked by the writer before anything is written (BadBins names the rule) [L3/bins.py:48-80, 150].
- index.json keys [L3/bins.py:174-178]: day (int), part, kind "BIN", coins (the day's coin list, the part's row order), rows,
  coins_with_rows, coins_missing (coins with no source, never also in coins [L3/bins.py:146-149]), sources ({coin: sha16 of the raw it
  came from} [L3/bins.py:12]), bins ({field: {dtype, rows, frames: [[pos, bytes, sha16, rows] one a coin]}}), readings {} , inputs {},
  aside, format, code_sha16, built_utc.
- The detector evaluates on a day only the coins the PRICE part lists [TOOLS/idea_to_grade/detect_v2.py:44, 367-383].
- The engine's price at a 5 s step is the last 3 s close with te <= the step [TOOLS/alarm_design/alarm_design_v3.py:183-198].
- GRADE reads PRICE only for its matched random moments and outcomes [TOOLS/idea_to_grade/i2g_engine_rel1.py:9-17].

## 5. Kind CLOCK: metric codes
Per code and field one file `<code>.<field>.lz4`, shape (coins, 86,400 / step) [L3/days.py:238-249; L3/write.py:481].
| field | dtype | meaning | absent | source |
|---|---|---|---|---|
| v | <f8 | the value (NUMBER codes) | NaN | [L3/write.py:14; L3/days.py:23-24] |
| w | <i2 | a word id into WORDS/<code>.txt (WORD codes) | -1 | [L3/write.py:14-15] |
| a | <i4 | age: t_k - known_at in whole seconds, half to even | INT32_MIN | [L3/write.py:15, 122-124, 240] |
| e | u1 | reason id into REASONS.txt; 0 = none | 255 | [L3/write.py:15; L3/days.py:24] |
| o | <i8 | t_k - as_of of the answering row, us (0 = a row at this very step end) | INT64_MIN | [L3/write.py:15-16, 238, 253; L3/days.py:12] |
| k | <i8 | known_at, us; only for codes whose catalog row says exact_k | INT64_MIN | [L3/write.py:16, 175, 428] |
- NUMBER codes keep v, a, e, o; WORD codes w, a, e, o [L3/write.py:34]; plus k when exact_k [L3/write.py:175].
- A reason is the row's empty_reason, with ";STALE" added (or "STALE" alone) when stale is 1 [L3/asof.py:43-47].
  At most 255 reason texts a part [L3/write.py:233-234].
- Codes of scope market keep one row named MARKET; coin codes never do; coin+market codes both [L3/write.py:390-411].
  REF's BASE part lists 51 coins and then MARKET [REF day=20251001 BASE index.json coins].
- index.json keys [L3/write.py:492-494]: day, part, coins, coins_missing, readings, inputs, aside, sources ({raw file name: 16-hex
  sha16} [L3/write.py:419-422]), seal (text or null), format, code_sha16, built_utc.
- readings[code] [L3/write.py:473-481]: kind "CLOCK", value_kind "NUMBER" or "WORD", step, exact_k, coins_with_rows, fields, dtypes,
  files ({field: sha16 of the .lz4 file}), shape [coins, 86,400 / step], and no_prev when the source has no D-1 [L3/write.py:476-477].
- What the detector counts as KNOWN: v finite AND e == 0 AND a >= 0 AND o >= 0 AND (when k is kept) k set and k <= the column time;
  else UNKNOWN (NaN). A NotBuilt code-day is a whole UNKNOWN code-day [TOOLS/idea_to_grade/detect_v2.py:34-36, 410-425].
- A rule reads CLOCK codes only: kind ROWS is refused, CLOCK_REQUIRED [TOOLS/idea_to_grade/detect_v2.py:405-406]. ROWS codes (Y3
  events) need not be converted for rules.
- REF rows: every coin has a row at every step end (o == 0 at all 1,440 minutes of BTC for A1.S08, E2.S02, E1.S01, C11.S01, Z3.S01 on
  20251001) [REF]; METRICS_V1 says every coin has all 1,440 minute rows on each of its days [LAB3/METRICS_V1.tsv:8].
- An empty value is a row with value_kind 0, NaN and an empty_reason word: never read it as 0 [LAB3/METRICS_V1.tsv:4].

## 6. Block encoding
- Codec: pyarrow lz4 frame, `pa.Codec('lz4')` [L3/days.py:22]. A block is the array's raw C-order bytes in its dtype, compressed
  [L3/write.py:328-334; L3/bins.py:130]. dtypes [L3/days.py:23; L3/bins.py:27].
- sha16 = the first 16 hex of sha256 of the compressed file bytes [L3/days.py:73-75]. The reader refuses a block whose sha16 is not its
  index's, BlockChanged [L3/days.py:245-246; L3/bins.py:94-95].
- Decompress with the size from the index: prod(shape) x itemsize (CLOCK) [L3/days.py:247-249], rows x itemsize (BIN frame) [L3/bins.py:96].
- Library: pyarrow and numpy, the versions of alarm/settings/PYTHON_PACKAGES.txt (numpy 2.2.6, pyarrow 25.0.1).

Read one CLOCK block without lab3 (this ran on 4 Nov 2026 and equalled lab3's read):
```python
import json, numpy as np, pyarrow as pa
part = 'DATA_ROOT/lab_days/day=20251001/BASE'
r = json.load(open(part + '/index.json'))['readings']['A1.S08']
raw = open(part + '/A1.S08.v.lz4', 'rb').read()
v = np.frombuffer(pa.Codec('lz4').decompress(raw, decompressed_size=int(np.prod(r['shape'])) * 8, asbytes=True), '<f8').reshape(r['shape'])
```
Read through the one reader (the way every engine tool reads):
```python
import sys; sys.path.insert(0, 'alarm/01_Detection/tree/team/LAB3/code')
from lab3 import days as LD, bins as LB
R = LD.Days('DATA_ROOT/lab_days', 'research')
v = R.read('A1.S08', 'v', ['20251001'], ['BTC', 'ETH'])        # (days, coins, steps); a coin the day does not list reads ABSENT
off, b = LB.read_bins(R, '20251001', ['BTC'])                   # b['te'][off[0]:off[1]], b['px'][...]
```
[L3/days.py:284-300; L3/bins.py:193-213]. Purpose 'research' refuses days from 20260601 on [L3/law.py:18].

Write: use the shipped writer, never hand-made lz4. `lab3.bins.write_bins` for PRICE, `lab3.write.write_part` for CLOCK codes. Both check
everything first, write into `<PART>.tmp_<UTC>`, read the whole part back, then rename it in; an old part is moved aside, never deleted
[L3/bins.py:137-188; L3/write.py:415-504]. One writer a (day, part) at a time (flock) [L3/write.py:437-444].
```python
import sys, numpy as np; sys.path.insert(0, 'alarm/01_Detection/tree/team/LAB3/code')
from lab3 import bins as LB, write as LW, days as LD
ROOT = '<new data folder>/lab_days'
# PRICE: bins = {coin: {te, tl, px, hi, lo, n, buy, sell: 1-d arrays of one length}}
LB.write_bins(ROOT, '20251001', ['BTC', 'ETH'], bins, sources={'BTC': '<sha16 of the raw file>', 'ETH': '<sha16>'})
# CLOCK: rows = {coin: {day, as_of_us, known_at_us, value_kind, value_bits, value_txt, empty_reason, stale}: lists of one length}
bits = lambda x: int(np.array([x], '<f8').view('<u8')[0])        # value_bits = the float64's raw bits [L3/rows.py:18-19]
d0 = LD._day_start_us('20251001'); ends = [d0 + 60_000_000 * k for k in range(1440)]
rows = {'day': [20251001] * 1440, 'as_of_us': ends, 'known_at_us': ends, 'value_kind': [1] * 1440,
        'value_bits': [bits(0.0)] * 1440, 'value_txt': [None] * 1440, 'empty_reason': [''] * 1440, 'stale': [0] * 1440}
LW.write_part(ROOT, '20251001', 'BASE', {'A1.S08': {'step': 60, 'kind': 'NUMBER', 'rows': {'BTC': rows}}}, ['BTC'],
              sources={'my_liquidations_20251001.csv': '<sha16>'})
```
- value_kind: 0 empty, 1 a float, 2 a whole number, 3 and up a text [L3/asof.py:31-41]; a ROWS x field keeps kinds 0 to 7 [L3/write.py:307-309].
- write_part checks the rows against the catalog first: every code listed, step = its clock, exact_k and scope agree
  [L3/write.py:390-412, 427]. The default catalog is LAB3/METRICS_V1.tsv (columns code, store, clock, exact_k, scope)
  [L3/write.py:363-384]. Codes outside it (the Hyperliquid tables) need a catalog given by hand (section 8, X1).
- `no_prev: True` tells the writer the source has no D-1: then 00:00 to 00:59 is NO_PREV_DAY, never guessed [L3/write.py:10-11, 185-192].
  Set it only on the first day of the data.

## 7. Proof that this page is right (4 Nov 2026, in a scratch folder outside the repo)
- write_bins wrote PRICE for BTC, ETH, SOL, XRP, DOGE on 20250930 to 20251002 from REF's bins; write_part wrote A1.S08 and A1.S12 (MARKET).
- Read back: values, reasons, o, a and k as written; a coin not listed read NaN; FORMAT.json equal to REF's byte for byte; the raw
  pyarrow read equal to lab3's.
- The hand check on that folder (`HC` with desk/tests/data/SAMPLE_DEF_V1.json, 20251001 to 20251002, 5 coins) printed the same 22 lines
  as on REF: 88 fires (BTC 28, ETH 27, SOL 28, XRP 5).

## 8. Codes, families and what each needs
The catalog: LAB3/METRICS_V1.tsv, one row per code (1,214 rows): unit, unit_text, scope, step, window, meaning, empty_when, read_as,
store, clock, exact_k [LAB3/METRICS_V1.tsv header]. Units [LAB3/METRICS_V1.tsv:3]. The codes a rule may pick: KIT/METRIC_MENU_V2.tsv,
pickable YES only (157 of 552 rows) [KIT/METRIC_MENU_V2.tsv:2-3]. METRICS_V1 gives the meaning, unit and window of a code; it does not
give every formula (OPINION, from reading the rows: most read_as cells describe checks, not the computation).

The raw source each family reads (the TRUE gate's table) [TG/build_families_v1.py:15-30, 32-46; TG/SOURCE_FAMILIES_V1.tsv]:
| raw source family | code families |
|---|---|
| PRICE (trades) | C1 to C11, C13, COIN_C3, NAUTILUS, X1.RETX, X1.TIMEX, X1.VOLX (most) |
| LIQ_BN (Binance liquidations) | A1, A2, A4, X1.LIQX; with TRADES_BN: A5; with OI_BN: A7, COIN_C2 |
| OI_BN (Binance open interest) | E2.S01 to S04, E2.S07; some X1.POSX |
| FUNDING_BN (Binance funding) | E1; some X1.POSX |
| MARK_BN (mark price) | E3; some X1.POSX |
| TRADES_BN (trades by side and size) | B1, B2, B3, X1.FLOWX |
| BOOK_BN (order book) | C12, D1 to D5, X1.BOOKX, X1.COST |
| CALENDAR | Z1, Z3, X1.CALX |
| NEWS | Z2 |
| HL_FILLS, HL_POS (Hyperliquid fills, positions) | X1.HLFLOWX, X1.HLLIQX, X1.HLPOSX, X1.HLPOSM; E2.S05, E2.S06 |
| UNKNOWN (no reviewed source) | A6, COIN_C1, COIN_C1B, LAB.* and others: the TRUE gate refuses them as labels |
- C1 is filed under PRICE, but its empty reasons name BOOK_HOLE and it is "measured on the mid" [LAB3/METRICS_V1.tsv:228]: it needs the book.

### A1 liquidations (Binance)
| code | step | scope | k | unit | window | menu |
|---|---|---|---|---|---|---|
| A1.S01 / S02 | 5 s | coin | no | usd | 5 s | PROVEN YES |
| A1.S03 / S04 | 30 s | coin | S04 yes | usd | 30 s | PROVEN YES |
| A1.S05 / S06 | 1 min | coin | no | usd | 60 s, read at a fire second | PROVEN YES |
| A1.S08 / S09 | 1 min | coin | yes | usd | 60 s, the minute just ended | PROVEN YES |
| A1.S12 / S13 | 1 min | market | yes | usd | 60 s, summed over the roster coins seen | PROVEN YES |
[LAB3/METRICS_V1.tsv:14-19, 23-24, 27, 31; KIT/METRIC_MENU_V2.tsv:5-17]. Odd codes are longs forced out, even codes shorts.
- Input: every liquidation order of the coin: time, side, price, size. Dollars = price x size (unit usd, "US dollars, whole") [LAB3/METRICS_V1.tsv:14].
- Long liquidations push price down, short ones up [TOOLS/alarm_design/alarm_design_v3.py:36].
- Binance publishes only the last liquidation per coin per second: read as AT LEAST [LAB3/METRICS_V1.tsv:14 read_as].
- Empty reasons seen: THIN_FEED, NO_FILE, TRADES_HOLE; never read empty as 0 [LAB3/METRICS_V1.tsv:14 empty_when].
- REF: a minute with no liquidation holds 0.0 with reason none (BTC 20251001): 0 means "seen, none", NaN means "not seen".

### E1 funding (Binance)
| code | step | scope | k | unit | window | menu |
|---|---|---|---|---|---|---|
| E1.S01 | 1 min | coin | yes | ratio per 8 h | value in force, 61 s at most | PROVEN YES |
| E1.S03 | 1 min | coin | no | timestamp_us | next settle time | UNPROVEN NO |
| E1.S04 | 1 min | coin | no | hours | funding interval | CAUTION NO |
| E1.S06 | 1 min | market | no | ratio per 8 h | the middle coin's estimate | PROVEN YES |
| E1.S09 / S10 | 1 min | coin | no | ratio / timestamp_us | the rate paid at the last settle, its time | UNPROVEN NO |
[LAB3/METRICS_V1.tsv:797, 801-802, 807, 817, 819; KIT/METRIC_MENU_V2.tsv:346-355]
- Input: the exchange's live funding estimate with the next settle time and the interval; paid rates for S09 and S10.
- S01 is an estimate scaled to 8 h, not a payment; positive = longs pay [LAB3/METRICS_V1.tsv:797 read_as].
- The lab recomputed S05 "from the Tardis rows themselves (each coin's funding_rate x 8 / its interval ...)" [LAB3/METRICS_V1.tsv:807 read_as].
- E1.S02 (who pays) is a WORD code and NOT_READABLE: a rule uses sign(E1.S01) [KIT/METRIC_MENU_V2.tsv:347; KIT/METRIC_FAMILIES_V1.md:9-10].

### E2 open interest
| code | step | scope | k | unit | window | menu |
|---|---|---|---|---|---|---|
| E2.S02 | 1 min | coin | yes | coins_qty | value in force, 61 s at most | PROVEN YES |
| E2.S03 | 1 min | coin | no | flag | 60 s (the S02 row older than a minute) | CAUTION NO |
| E2.S04 | 1 min | coin | no | pct | 600 s change | PROVEN YES |
| E2.S07 | 1 min | market | no | pct | 60 s, the mean coin's change | PROVEN YES |
| E2.S05 / S06 | 1 min | coin | S05 yes | coins_qty / pct | Hyperliquid OI; 600 s change | UNPROVEN NO / PROVEN YES |
[LAB3/METRICS_V1.tsv:822, 824-825, 827, 829, 831; KIT/METRIC_MENU_V2.tsv:356-362]
- Input: Binance open interest in contract coins (thousands of coins for a 1000-prefixed contract), not dollars [LAB3/METRICS_V1.tsv:822 unit_text].
- The lab's S02 was within 1% of Binance's published 5 minute figure in 98.3 to 99.8% of marks [LAB3/METRICS_V1.tsv:822 read_as].
- E2.S05 and S06 read Hyperliquid positions (HL_POS) [TG/build_families_v1.py:34].

### C11 day levels (price)
| code | step | scope | unit | window | menu |
|---|---|---|---|---|---|
| C11.S01 | 1 min | coin | pct | under today's high; 0 = at the high | PROVEN YES |
| C11.S02 | 1 min | coin | pct | above today's low | PROVEN YES |
| C11.S05 | 1 min | coin | pct | from the nearer of today's high (+) and low (-) | PROVEN YES |
| C11.S03, S04, S06, S07, S08 | 1 min | coin | ratio, pct, side_pm1 | typical-minute units; yesterday's levels; side broken | UNPROVEN NO |
[LAB3/METRICS_V1.tsv:352-359; KIT/METRIC_MENU_V2.tsv:156-163]
- Window: the day so far, 00:00 UTC to e [LAB3/METRICS_V1.tsv:352].
- Input: 1 minute candles: the lab's values equal "the same formula on the klines within 1e-9 at 99.75% of coin-minutes" [LAB3/METRICS_V1.tsv:352 read_as].
- Empty reasons include NO_PRIOR_DAY (S06 to S08 need yesterday) [LAB3/METRICS_V1.tsv:352 empty_when].

### Z3 clocks (calendar)
| code | step | scope | unit | window | menu |
|---|---|---|---|---|---|
| Z3.S01 | 1 min | coin | minutes | to this coin's next Binance funding payment | UNPROVEN NO |
| Z3.S02 | 1 min | market | minutes | to the next whole UTC hour (Hyperliquid funding) | UNPROVEN NO |
[LAB3/METRICS_V1.tsv:1003, 1005; KIT/METRIC_MENU_V2.tsv:491-492]
- Z3.S01 is "recomputed exactly from E1 S03" [LAB3/METRICS_V1.tsv:1003 read_as]: it needs the next settle time.
- Z3.S02 needs no market data. REF holds it only on the MARKET row (BTC's row reads NO_ROW_KNOWN, 20251001).
- Both are pickable NO on the menu: a rule that reads them needs a MENU EXCEPTION at SEAL [alarm/AGENTS.md step 5b].

### X1 Hyperliquid (X1.HLFLOWX, X1.HLLIQX, X1.HLPOSX, X1.HLPOSM, X1.HLPX)
- Catalog: not METRICS_V1 but LAB3/METRICS_HL_ADD_V1.tsv:3-16 and
  alarm/01_Detection/tree/team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv:3-44 (code, store_part, clock, known_at, unit, meaning).
- Steps 5 s (FLOWX, LIQX, PX) and 1 min (POSX, POSM) [the same rows]. REF keeps a k field for them (X1.HLFLOWX.S08: fields v, a, e, o, k).
- Input: Hyperliquid fills by block, by account, with the liquidation flag and position change [the meanings: "every account, by its
  own position change", "liquidated account sold": KIT/METRIC_MENU_V2.tsv:544-556]; the lab's raw store is HL node fills by block
  [L3/law.py:55-57].
- Known at: "rows with block time <= u - 1 s only" (FLOWX) [METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv:10]; LIQX trades in (u-6 s, u-1 s]
  [LAB3/METRICS_HL_ADD_V1.tsv:3].
- Menu: every X1.HL row is pickable NO (kind NOT_PROBED, first day 20261024) [KIT/METRIC_MENU_V2.tsv:544-556]. The COUNT gate and the
  hand check also read the owner-cleared table, so they admit X1.HLFLOWX.S08 and S09 [alarm/AGENTS.md step 2].
- To write them with write_part give a catalog by hand: {code: {'kind': 'CLOCK', 'clock': 5 or 60, 'exact_k': True, 'scope': 'coin'}}
  [L3/write.py:366-384, 390-412]. OPINION: exact_k True follows REF; the HL tables have no exact_k column.

## 9. Reads beyond the definition
- The rule's own inputs: every code its definition names, through the one reader [TOOLS/idea_to_grade/detect_v2.py:34-36].
- The first look's profile reads A1.S01, A1.S02, E2.S02, E2.S03 [PROFILE:73]; a missing code reads NaN and is listed as skipped [PROFILE:262-271].
- The first look's profile reads Hyperliquid fill files HLF_<coin>_<day>.npz (fields t, lt, lpx, lsz, lside, lself) under HL_FILLS
  [PROFILE:74-75, 242-248, 284-298]; the desk sets HL_FILLS empty [desk/desk.py:87].
- A definition's truth label of kind forced_usd reads A1.S02 (up) or A1.S01 (down) [TOOLS/alarm_design/alarm_design_v3.py:36;
  desk/tests/data/SAMPLE_DEF_V1.json "truth"].
- GRADE's outcome unit c comes from a cost table of 52 coins; a coin not in it is EMPTY (NO_UNIT:COST_FALLBACK)
  [TOOLS/alarm_process/OUTCOMES_MENU_ALARM_V1.json:6, 21-25; alarm/01_Detection/tree/team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv].
- research_days: GRADE reads EPI parts there only for the unit nm [TOOLS/event_outcomes/event_outcomes_gm2.py:826-843, 905-955];
  every label of the GRADE menu uses unit c [TOOLS/alarm_process/OUTCOMES_MENU_ALARM_V1.json labels]. A missing EPI part is recorded
  NOT_BUILT [TOOLS/event_outcomes/event_outcomes_gm2.py:842]. OPINION: leave research_days an empty folder; a GRADE on an empty one is untested.
- Not read by any shipped engine tool: parts PCT (TABLE) and BAND.* (their writer lab3/tb.py is not shipped [L3/write.py:20]; a search of
  alarm/ for PCT24, PCTX and BAND finds them only in L3/write.py, L3/rows.py and L3/labgroups.py). Leave them out.

## 10. Coins and days the engine reads
- Coins: the PRICE index names, BTC, not BTCUSDT [HC:24]. The jobs take their coins from a fixed roster of 52 [KIT/jobs/JOB_COUNT_V7.job.sh.txt:10, 28-29;
  CHAIN:96, 119-120; alarm/01_Detection/tree/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json]:
  AAVE ADA APT ARB ASTER ATOM AVAX BCH BNB BONK BTC CRV DASH DOGE DOT ENA ETC ETH FET FIL HBAR HYPE ICP INJ LDO LINK LIT LTC NEAR ONDO OP
  PENGU PEPE PUMP RENDER SEI SHIB SOL SUI TAO TIA TRUMP TRX UNI VIRTUAL VVV WLD WLFI XLM XMR XRP ZEC. A coin outside it is never evaluated.
- COUNT and GRADE read 20250910 to 20251231 [KIT/jobs/JOB_COUNT_V7.job.sh.txt:14; CHAIN:75]; research window 20250901 to LAST
  [KIT/jobs/JOB_COUNT_V7.job.sh.txt:35]. The hand check reads 20250910 to 20251231, and warm-up days back to 20250820 [HC:41].
- MONTH reads Jan to Apr 2026 [alarm/AGENTS.md step 10]. The window table: BUILD 20250901 to 20260228, CHECK 20260301 to 20260531,
  BLIND from 20260601 [TOOLS/freeze_judge/WINDOWS_V1.tsv:2-4]. Research reads refuse every day from 20260601 [L3/law.py:18].
