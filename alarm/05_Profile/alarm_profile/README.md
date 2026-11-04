# tools/alarm_profile: what each liquidation looked like, proven to mean what it says

Owner seat: QUANT. Reviewer: SCOUT. Built to the research-tool-design skill. The owner asked for three things (22 Oct, Berlin):

- 13:03: "all the things relevant for the liquidation", so one liquidation can be compared with others.
- 13:08: "different profiles from all the metrics depending on how we want to group them".
- 13:13: "the most important thing is that we prove that whatever profile we design, whatever metric we use we prove it means what it says".

## Design note

1. **QUESTION.** What did each liquidation alarm's episode look like at the alarm? Seven parts:
   - where the move really started;
   - how far it went before the liquidations and during them;
   - how fast it moved;
   - how big the liquidations were, against the coin's own normal;
   - their shape over time;
   - the other side's liquidations;
   - what open positions and another exchange (Hyperliquid) did in the same burst.
2. **UNIT.** One row is one alarm, at the alarm (`as_of_us` = `known_at_us` = the alarm).
3. **KNOWN AT: the alarm.** `episode_blocks.Ep` cuts every input at the alarm before any block runs:
   - 5 s rows up to the alarm's row;
   - price bins ending at or before it;
   - open interest minute ends at or before it;
   - Hyperliquid fills at or before it;
   - daily totals of whole days before the burst's day.

   A test plants 1e12 everywhere after the alarm, and nothing may change.
4. **INPUTS.**
   - **The alarm list**, with `coin, t, side, onset_t`. A02 is QUANT's `q_471121_A02_REDESIGN_FIRES.tsv`, candidate D0 (A02M, equal to SCOUT's a02_climax_v3 fires).
   - **The lab**, read only through `lab3.days` (purpose research):
     - A1.S01 / A1.S02 (5 s liquidation rows);
     - E2.S02 / E2.S03 (Binance open interest at minute ends, and whether it was carried);
     - PRICE (3 s bins).
   - **SCOUT's Hyperliquid files** (`HLF_<coin>_<day>.npz`, from hl_fills_v1 on the node fills): every liquidation fill. The liquidated account's own rows are `lself = 1`.
   - **The settings** are `EB.SETTINGS` plus the subject, the candidate and the Hyperliquid folders. All of it is the seal.
5. **NOT IN IT.** Nothing after the alarm, and no outcome: no heat, offer or money. Those stay in their own tools (`STAMP.*`) and are joined only when reading. The context around the alarm (market, coin, book, positions at the alarm) stays in `tools/alarm_context` (CTX), and the profiles join the two.

## Words used (one definition each)

- **Push.** The alarm's price direction:
  - side +1 means pushed UP (shorts forced);
  - side -1 means pushed DOWN (longs forced).

  Every price value is push-signed: + means the way the alarm pushed.
- **Close at s.** The close of the last 3 s PRICE bin that ended at or before s (bin end times are whole microseconds; compare them as they are, never rounded to seconds). A close older than 60 s is unknown (STALE_PRICE, MAX_PRICE_AGE_S; LAYERS 23 Oct, STRATEGY-153335, QUANT's 60 s): a close is unknown when no bin ended at or before s, or when the last one ended more than 60 s before s, so a feed gap or a missing day is a hole, never a flat price.
- **Moves are in LOG units.** Every price value in pct is 100 x the push-signed change of the natural log of the close: a move from s1 to s2 is 100 x side x (ln close(s2) - ln close(s1)). "pct" in this tool always means this log percent.
- **Forced rows.** The lab's 5 s liquidation rows of the forced side: A1.S02 when pushed up, A1.S01 when pushed down. The other side's rows are the opposite code. A missing row is a hole, never zero. A row is named by its END time: the row at s covers (s - 5 s, s]. The ONSET ROW is the row ending at the onset; the ALARM ROW is the row ending at the alarm.
- **Onset.** The episode's A01 onset (`onset_t`): the first 5 s step whose 60 s forced sum went over the coin's bar. The bar is max(the p99.9 of the 60 s sums of the 6 h before, 20,000 USD).
- **Burst start.** The start of the first forced row that holds a print (known and above 0; holes are skipped), inside the onset's 60 s window (the 12 rows ending at the onset row). This is when the liquidations that crossed the bar began. With no such row there is no burst, and every burst value is unknown.
  - The **burst** runs from the burst start to the alarm.
  - Every burst value (dollars, price move, speed, open interest, Hyperliquid) covers that same span.
- **Run end (v2).** The price extreme since the burst start: the furthest close in the push direction among the close at the burst start (onset - 60 s when the burst has no start) and every 3 s bin that ended after it, up to the alarm. On ties the latest counts. When the alarm's own close is that extreme, the run end is the alarm.
- **Run grid.** The times alarm - 86,400 + 60 i (i = 0, 1, 2, ...) that are before the run end, plus the run end itself; x = side x ln(close) at each. The run start needs a known close at the run end and more than 60 known closes on the grid.
- **Swing start (v2).** On the run grid (unknown closes are skipped):
  1. Walk the grid in time order keeping H, the highest x since the walk started or since the last TURN. When an x is at or below H - h (h = max(3 normal moves, 0.1 pct); in log units), the point where H was reached (the first point at that height) is a TURN, and H restarts AT that x (H = that x, then the highest x seen from it on). The stretch is everything after the LAST turn's high; with no turn, the whole grid.
  2. The swing start is the LAST point of that stretch within one normal move of its lowest x.
- **Run start (where the move really started), v3 = the start of the final push.** Walk the run grid from the swing start to the run end (unknown closes are skipped). The price PROGRESSES at a close more than one normal move above the close of the last progress; the swing start counts as the first progress close. A PAUSE is the stretch from one progress close up to (not including) the next progress close, when the time between the two progress closes is 30 minutes or more; or the stretch from the last progress close to the run end (including it), when the run end's time minus that progress's time is 30 minutes or more. If there is at least one pause, the run start is the LAST point of the LAST pause within one normal move of that pause's lowest x. With no pause, the run start is the swing start. KNOWN BIAS (SCOUT 13:44:43Z, v3b sample): the last point within one normal move of the low can be 1 to 3 min AFTER the low, on the first uptick (4 of 12 charts), so run_pct can read short by up to one normal move (chart 2: 0.39 of 1.43 pct). Kept as is (the rule passed its eye check); a later version may take the last LOCAL low inside that band. `run_capped` = 1 when there was neither a turn nor a pause (the move may be older than its start).
  - Why (the owner chose it, 22 Oct 14:55:55 Berlin, "no progress, 30 min", from QUANT's chart of four rules over SCOUT's 12 eye alarms): after hours of sideways the eye puts the start at the final push, while the swing rule kept the old low (ETH 24 Sep: 373 min back, after a 5 h flat stretch; the final push 19 min).

  v1 (a02_run_start_v1, eye check 12 of 12 in J471127) searched up to the alarm itself. A02 fires after the climax, so a bounce of h or more between the extreme and the alarm restarted the run AT the alarm: run 0, age 0, giveback 0. QUANT found it in the J471128 eye charts (OP 3 Nov 15:32: 4.3 pct in the burst, read as no run). v2 stops the search at the extreme, so the bounce shows in `giveback_pct`, where it belongs. Where the alarm's close is the extreme, v2 = v1 (the proof run checks it).
- **Normal move.** The closes at alarm - 90,000 + 900 j (j = 0 .. 96, that is from alarm - 25 h to alarm - 1 h); the 96 moves |ln close(j) - ln close(j - 1)| between neighbours; their median (at least 48 known moves; with an even count, the mean of the two middle moves), in log units. normal_move_pct = 100 x that median.
- **Normal day.** The median forced-side USD of the 7 whole UTC days before the burst's day. Only days with at least 90 pct of rows known count, and at least 5 such days are needed.
- **Holes make sums unknown.** A sum over 5 s rows is unknown when any row in it is a hole: the burst's sums (forced_usd_log, size_vs_week, active_share, top5s_share, burst_vs_oi_bp, other_usd_log, other_share), the hour before the burst (pre_forced_usd_log), and every 15 s or 60 s sum (the peaks, the waves, the bar).
- **15 s and 60 s sums.** The 15 s sum at row k is rows k-2, k-1, k (unknown with a hole); the 60 s sum is rows k-11 .. k. The peaks (peak15_usd_log, peak60_usd_log, peak_s, growth) and the waves are read from the onset row to the alarm row; the burst's sums from the burst start.
- **Big waves (n_flushes).** p = the biggest known 15 s sum from the onset row to the alarm row. Walk the 15 s sums from the onset row to the alarm row: a sum at or above p/2 is HIGH; at or under p/10 is QUIET. The first HIGH is wave 1. After that, 3 CONSECUTIVE known QUIET sums arm the count (an unknown sum, a sum between p/10 and p/2, or a HIGH resets the quiet count to 0); once armed, the count stays armed until the next HIGH, which is a new wave and disarms it. Smaller bursts (under half the biggest) are not waves: this counts BIG waves only, and a burst before the onset row is not counted. n_flushes is unknown when no 15 s sum from the onset row to the alarm row is known, or when the biggest is 0.

## The values (36; `EPI_CATALOG_V1.tsv` is generated from the docstrings, `python3 alarm_profile.py catalog`)

| block | values |
|---|---|
| MOVE run | normal_move_pct, run_pct, run_norm, run_age_min, run_capped |
| MOVE split | pre_move_pct, burst_move_pct, forced_share, giveback_pct, giveback_share |
| SPEED | burst_s, onset_to_alarm_s, burst_speed_pct_min, pre_speed_pct_min, speed_ratio, burst_speed_vs_normal, max_move_60s_pct |
| FORCED size | forced_usd_log, peak15_usd_log, peak60_usd_log, size_vs_bar, size_vs_week, growth, pre_forced_usd_log |
| FORCED shape | peak_s, peak_to_alarm_s, n_flushes, active_share, top5s_share |
| FORCED other | other_usd_log, other_share |
| POSITIONS | oi_chg_burst_pct, burst_vs_oi_bp |
| HL (Hyperliquid) | hl_forced_usd_log, hl_other_usd_log, hl_lead_s |

Limits stated in the values themselves:

- **Binance publishes one liquidation print per coin per second.** Its dollars are a lower bound. SCOUT's M27r measured it: on caught events the prints are about 11 pct of the open interest drop in USD, and 1.4 pct on missed ones.
- **Hyperliquid's record is complete,** but it is another exchange. Our files cover 12 Sep to 26 Oct 2025 for now (SCOUT is downloading the rest, limited so the feed recorder is not starved). Hyperliquid values outside our files are NaN.

## Proof of meaning (the owner 13:13 Berlin)

Every value has a proof card in `PROOFS_V1.tsv`, written before any run: the proofs it must pass, and each pass line. Results go to `PROOF_RESULTS_V1.tsv` with their receipt.

- **Status PROVEN:** every proof on the card passed.
- **Status FAILED:** any proof failed.
- **Status OPEN:** anything else.

The profile view prints the status beside every value.

| proof | what it shows | values |
|---|---|---|
| P1 PLANT | A planted episode where every answer is known by hand (`test_alarm_profile.Planted`). Also: its mirror (a push down) gives the same answer, and 1e12 after the alarm changes nothing. | all 36 |
| P2 TWIN | `episode_twin.py`, written apart in plain loops from the definitions above, equals the built value read back from the one format on every alarm. 40 random episodes in the tests too. | all 36 |
| P2B BLIND | SCOUT rebuilds it from this README alone, on 24 alarms he draws himself. | run_pct, forced_usd_log, n_flushes |
| P3 PRICE RECORD | Another record: the lab's minute-end closes against Binance's own 1 min klines over the 24 h before 12 drawn alarms, and the run start and run move computed from both records. | the 16 price values |
| P4 EYE RUN | v3b: SCOUT judges 12 new fresh charts (seed 22102033, none already judged): is the marked start where the move began? YES on at least 9 and NO on at most 1 (set before the draw, 15:32 Berlin). RESULT: 10 YES, 2 UNSURE, 0 NO: PASS (J471134). v3's sample: 9 YES, 3 UNSURE, 0 NO of 12 fresh (line 11: FAIL as written), 4 of 4 changed. | the 10 values that rest on the run start (giveback_pct added in v2) |
| P4 EYE WAVES | SCOUT counts the waves on 12 charts of the forced rows without seeing the tool's count. | n_flushes |
| P4 OI LINE | A second record (Binance open interest): did positions really close during the burst, and more in bigger bursts? | forced_usd_log |
| P4 HL LINE | Another exchange: is Hyperliquid liquidating the same side more often when the Binance burst is big for its coin? | forced_usd_log, size_vs_week |
| P4 HL SIGN | The Hyperliquid side is read right: the side Binance forced holds most of Hyperliquid's liquidated dollars. | hl_forced_usd_log, hl_other_usd_log |

The 125 context values show their own evidence. `CTX_INPUTS_V1.tsv` lists the lab codes each one reads (a test checks that every listed code really is in its block). A context value is PROVEN only when all of these hold:

- every lab code it reads is RELIABLE and DEFINED (or CARD_SIGNED) in METRICS_V1;
- its own output proof card (`CTX.<value>` in PROOFS_V1.tsv) exists and every required proof passed on the frozen output version; a failed proof means FAILED, missing evidence means OPEN, and upstream validity alone never proves downstream arithmetic or meaning;
- its PRICE input passed P3;
- costs are not used: today's cost table applied to the past stays OPEN.

## Profiles: named groupings over all the values (`PROFILES_V1.tsv`)

A profile is only a list: the profile, the group, the tool (EPI = this tool, CTX = alarm_context), the value, and why it belongs. Adding or changing a profile computes nothing again. ALL (every value of both tools) is built in. The first profiles:

| profile | groups |
|---|---|
| LIQUIDATION | size, size for this coin, timing, shape, other side, other exchange, positions, breadth, history |
| MOVE | run, split, speed, recent, structure |
| POSITIONS | burst, open interest, funding, traders |
| FLOW_BOOK | flow, book, walls |
| MARKET_TIME | btc, market, liquidity, clock |
| COIN | kind, volatility, trend |

Cause flags (C1 to C7 of ALARM_DEFINITION_V1) will be declared rules over these values. Each flag will need its own proof on a second record before use.

## Output: the one format

- Written with `lab3.write.write_part` to `<DATA_ROOT>/research_days`.
- Part `EPI.<SUBJECT>` (ROWS), codes `EPI.<SUBJECT>.<column>`.
- An unknown value has no bits and reason NOT_KNOWN.
- **Generated once.** The index holds the seal and the sources: sha16 of the alarm list, the code, the catalog, every lab index read, and every Hyperliquid file read. The same inputs and settings give `UP TO DATE`.
- **Sealed.** A sealed day is never built or read: the canonical seal is team/LAB3/code/lab3/law.py (read through lab3.days and this tool's sealed(); never a date copied here): today it refuses 1 Jun 2026 on (BLIND), and research reads 10 Sep 2025 to 31 May 2026. Permission to READ a day is not authorization to USE it for a research stage: that is STRATEGY's RUN_GATE (OX-SKEPTIC A09-S05). The day after a sealed day is refused too. The tests seal December for themselves.
- **Memory.** Coins are read 16 at a time, and each alarm keeps only the rows and bins its blocks may read. 400 planted alarms stay under 300 MB (tested).

## Run

```
python3 -B test_alarm_profile.py <lab3 code dir>                                   # P1 and the format tests
python3 -B mutants_alarm_profile.py <lab3 code dir>                                # planted bugs: all must be killed
python3 -B alarm_profile.py build <lab_days> <lab3 code dir> <alarms tsv> A02 <first> <last> [out root]
python3 -B alarm_profile.py profile <out root> <lab3 code dir> A02 <first> <last> LIQUIDATION [<coin> <t>]
python3 -B alarm_profile.py status [METRICS_V1.tsv]                                # every value's proof status
python3 -B proof_alarm_profile.py ...                                              # P2, P3, P4 OI and HL lines, eye samples
```

## Checklist

- [x] design note: question, unit, known-at, inputs and settings, what is NOT in it
- [x] own folder with README, code, EPI_CATALOG_V1.tsv, tests
- [x] values only through lab3.write to research_days, read only through lab3.days; text only for meaning
- [x] catalog rows for every value; sources by sha16; settings as the seal
- [x] generated once; the same inputs and settings give the same sha16s (tested)
- [x] tests: known-at, the mirror, planted answers, holes, the second computation on planted and random episodes, catalog, profiles, proof cards, determinism, memory, sealed days
- [ ] mutants: all killed (receipt)
- [ ] job with honest MEM_MB
- [ ] proofs P2, P3 and the P4 lines run; eye checks and the blind rebuild by SCOUT
- [ ] reviewed by SCOUT; board line; journal
