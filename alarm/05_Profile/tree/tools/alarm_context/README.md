# tools/alarm_context — what was happening around each alarm

Owner seat: QUANT. Reviewer: SCOUT. Built to `RESEARCH/KNOWLEDGE/TOOL_DESIGN_V2.md`. SCOUT's reviews are folded in:

- 17:29Z on the guideline: known-at = the decision time; December refused.
- 17:54Z on this tool (`REVIEW_ALARM_CONTEXT_SCOUT.md`): sealed days never read; the 9 Mar cutoff; mirror tests; empty minutes; the since-the-alarm columns.

## Design note

1. **QUESTION.** What was happening around each alarm at the moment we would decide? There are three parts, chosen by a setting:
   - **EVENT:** the alarm itself.
   - **MARKET:** the whole market, BTC first.
   - **COIN:** the alarm's coin.
2. **UNIT.** One row is one alarm × one decision time. The setting `decisions` is in minutes after the alarm, default `0` = at the alarm. Several decision times give several rows for the same alarm.
3. **KNOWN AT.** The decision time:
   - Lab values are read at the last minute end at or before it.
   - Channels and bands are read from the minute before.
   - Alarm-history questions count only alarms strictly before the described alarm.
   - Two columns, `fires_coin_since` and `fires_other_since`, count the alarms after the alarm and before the decision time.
   - Tests plant a huge value from the first minute after the decision time, and the output must not change.
4. **INPUTS.**
   - The alarm list (EVENTS tsv: coin, t, side, S). Side +1 means pushed up (shorts forced); −1 means pushed down (longs forced).
   - lab_days, read through `lab3.days` with purpose `research`.
   - Lab days read:
     - EVENT: the day before, up to the last decision day.
     - MARKET and COIN: the 31 days before, for the 7-day and 30-day questions.
   - Tables, used by COIN only:
     - `QUANT/receipts/COSTS_PER_COIN_V4.tsv`. This is today's cost table applied to the past, so it is an approximation.
       A09-02 (OUTSIDE, 23 Oct): as DECISION features, `cost_bp` and `cost_tier` are NOT_KNOWN unless the table row carries a source vintage
       at or before the decision (this table has none, so they are NOT_KNOWN). Today's table applied to the past lives only in the separately
       named RETROSPECTIVE values `cost_bp_retro` and `cost_tier_retro` (cost sensitivity, never a decision feature).
     - `COIN_TYPES_V1.tsv`, a hand list of major / alt / meme that the owner may edit.
5. **NOT IN IT.** No outcomes of any kind: no heat, no offer, no PnL. Those live in their own parts, such as `STAMP.A02`, and are joined only when reading.

**Signs.** Every directional value is in the alarm's push direction: + means the way the alarm pushed. Shares of "up" become shares "with the push".

## When a context value is PROVEN (OUTSIDE A09-01, adopted 23 Oct)

A context value is PROVEN only when its own output proof card (`CTX.<value>` in PROOFS_V1.tsv) exists and every required proof passed on
the frozen output version; a failed proof means FAILED, missing evidence means OPEN, and upstream validity alone never proves downstream
arithmetic or meaning. Every value stays OPEN until its own card and result exist (alarm_profile applies this rule).

## Subjects

- **`A02`:** the alarms.
- **`A02_MATCH`:** the matched random moments (`tools/alarm_match`). They are built with `[history EVENTS tsv]` = the alarm list, so the history questions count real alarms.

## Output: the one format

- **Writer:** `lab3.write.write_part`, into the research root `<DATA_ROOT>/research_days`. The writer creates the folder; DSK watches its space.
- **Parts:**
  - Each level is its own part: `CTX.A02.EVENT`, `CTX.A02.MARKET`, `CTX.A02.COIN`.
  - Adding a question to one level rebuilds only that level.
  - Store kind is ROWS. `as_of_us` is the alarm and `known_at_us` is the decision time.
- **Codes:**
  - Codes are `CTX.A02.<column>`, all listed in `CTX_CATALOG_V1.tsv`. The catalog uses METRICS_V1 columns, plus meaning, unit, level and block.
  - The catalog is generated from the block docstrings in `context_blocks.py`, and a test keeps the two equal.
  - The writer refuses any code that is not in it.
- **Unknown values.** A value that is not known is written with no bits and reason `NOT_KNOWN`, and reads back as NaN.
- **Generated once.**
  - Each day's index holds the `seal` (the settings) and the `sources`: the sha16 of the alarm list, the code, the catalog, the tables its level uses, and every lab index it read.
  - Running again with the same settings and inputs writes nothing (`UP TO DATE`).
  - A changed input rebuilds only the parts that read it. The old part is moved aside, never deleted.
- **Sealed days.** A sealed day is never read: the canonical seal is team/LAB3/code/lab3/law.py (read through lab3.days and this tool's sealed(); never a date copied here): today it refuses 1 Jun 2026 on (BLIND), and research reads 10 Sep 2025 to 31 May 2026. Permission to READ a day is not authorization to USE it for a research stage: that is STRATEGY's RUN_GATE (OX-SKEPTIC A09-S05). (History: 21 Oct the seal was 1 Jan 2026; December 2025 was opened by the owner that night.) The tests seal December for themselves, so the machinery below stays tested:
  - The lab reader treats them as unbuilt, so no price is carried from them.
  - Their minutes are NaN on every timeline the questions see.
  - Their alarms are removed from the history.
  - A decision time that falls on one is not written.
  - Building and reading both refuse them.
  - **The day after a sealed period** (in the tests 1 Jan; for real the first BLIND day's next day) is sealed for lab reads and alarm days too. The lab's own 24 h and prior-day windows (C1.S14, C4.S05, NAUTILUS 1440-candle, D2.S05, D3.S17, C11.S08, C10) carry December into it (SCOUT re-review 18:14Z).
- **Empty minutes.** The lab writes 0 for a minute with nothing in it, and NaN only for a hole (NO_FILE, THIN_FEED, TRADES_HOLE; J36470). A window sum with any hole reads NaN, never a smaller sum.
- **Log of USD.** `log10 usd` columns read 0 when there is nothing (0 USD), not 1 USD.

## The questions (129 values; `python3 alarm_context.py catalog` regenerates the catalog)

| level | blocks |
|---|---|
| EVENT (39) | identity, burst (forced USD, vs earlier bursts, forced vs other side, forced vs taker), history (alarms before, and since the alarm), move (5 min to 4 h), structure (Donchian 4 h / 24 h, VWAP, Bollinger, day extreme, swing), walls (liquidation levels ahead / behind) |
| MARKET (24) | BTC (15 min to 6 h, 6 h range position, straightness), BTC trend (24 h, 7 d, 24 h straightness, volatility vs its 30-day normal), basket, breadth, liquidation wave, spread and depth vs 24 h, weekend and hour |
| COIN (32) | move and vs basket, range (1 h / 4 h position and width, yesterday's range break), leg vs usual, volatility and pace, funding / OI / basis, cost and tier, 24 h / 7 d trend and volatility regime, days since a bigger alarm, coin class |

Adding a question means adding one block (a function with `@block(level, name)` and docstring lines `column: meaning [unit]`), then running `catalog`.

## Run

```
python3 alarm_context.py build <lab_days> <lab3 code dir> <EVENTS tsv> A02 <EVENT|MARKET|COIN> <first> <last> [out root] [decisions, e.g. 0,15,60]
python3 alarm_context.py show  <out root> <lab3 code dir> A02 <first> <last> [values, comma]
```

From code: `read(out_root, code_dir, 'A02', first, last, values=['burst_log_usd', 'btc_move_1h', 'cost_bp'])` returns the chosen values of any parts. Rows are joined on (coin, alarm, decision).

## v2 (21 Oct, the owner's yes at 21:30 Berlin)

- **What was added:** 30 new values (EVENT +15, MARKET +6, COIN +9), from the meaning sheet `PROPOSED_BLOCKS_V2.md`. Each was checked against METRICS_V1 before it was written. SCOUT checked every sign (19:55Z); D3.S05 is +1 = bids, measured.
- **Dropped in v2b:** BTC implied-vol rank (X1.VOLX.S08). It needs 90 days of DVOL, so it is empty for all of Sep–Nov (J38000).
- **Known only from mid-October:** the 14 to 30-day values (whales, heat rank, range rank, jumps, OI vs 30 d, funding z, implied minus real). The lab says NO_HISTORY before that, because it starts 10 Sep 2025 (J38000).
- **Random moments (A02_MATCH)** come from fire_path_v1's draw (`q_33614/out/PATHS_SEPNOV.tsv`; the full file holds December outcomes and was moved aside on SCOUT's MUST, 19:56Z). Notes:
  - The draw skips moments within 30 min before or after an alarm, so the baseline is a little calmer than a true random busy moment.
  - Late-October alarms lose the moments that fall in November when only Sep–Oct is built.
  - The draw's t is printed in whole seconds.
- **New tests:**
  - every code any block reads is set to 1e12 from the first minute after the decision, and nothing changes;
  - the mirror test covers every new directional column;
  - 7 more planted bugs (33 in all).

## Not here yet

- **Listing age.** We have no listing dates; the lab and the klines both start on 10 Sep 2025.
- **First weeks.** The 30-day volatility regime needs at least 10 earlier days, so it is NaN in the first weeks.
- **Paths around the event.** Metrics at −60 … +240 min would be a separate tool, `alarm_path` (proposed to the owner 21 Oct).

## Checklist (TOOL_DESIGN_V1)

- [x] design note: question, unit, known-at, inputs and settings, what is NOT in it
- [x] own folder with README, code, CTX_CATALOG_V1.tsv, tests
- [x] values only through lab3.write to research_days, read only through lab3.days; text only for meaning
- [x] catalog rows for every value; sources by sha16; settings as the seal
- [x] generated once; same inputs + settings = same sha16s (tested on the Mac: `OneFormat.test_determinism`)
- [x] tests: 29, covering:
  - known-at (planted after the decision, every level);
  - every directional column, side +1 vs side −1 (the mirror test);
  - window edges, and a hole is not zero;
  - history before only, and since the alarm;
  - catalog, determinism, memory;
  - sealed days (planted December and 1 Jan, January and 30 Nov rows unchanged; 1 Jan and the cutoff refused);
  - the real lab3 reader lists December and 1 Jan as unbuilt (Mac).
- [x] mutants: `python3 -B mutants_alarm_context.py <tools dir>` plants 25 bugs (SCOUT's 16 + 9 sealed-day and window ones); all 25 are killed.
- [x] job with honest MEM_MB: J36446 max RSS 0.9 GB.
- [x] reviewed by SCOUT:
  - 17:54Z: PASS WITH 3 MUST;
  - 18:14Z re-review: PASS WITH 1 small MUST (1 Jan), fixed in v1c.
