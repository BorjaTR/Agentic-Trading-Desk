# tools/alarm_stamp — heat before offer, after each alarm

Owner seat: QUANT. Reviewer: SCOUT. Built to `RESEARCH/KNOWLEDGE/TOOL_DESIGN_V2.md`.

This tool replaces the TSV stamps of J33689 (`STAMP_ALARM_FADE.tsv` / `STAMP_ALARM_FOLLOW.tsv`). Those had two problems: times were printed rounded (`%.6g`), so they could not be joined, and the entry was fixed at the alarm.

## Design note

1. **QUESTION.** After each alarm, entered at a decision time, how much heat came before each offer? This is the owner's 18:50 Berlin ask: classify every trade by the heat it took before 0.2 … 2%, and stamp each alarm by what it gives over 15 min to 4 h.
2. **UNIT.** One row is one alarm × one decision time × one direction. Decisions are a setting, in minutes after the alarm. The direction is the part: FADE goes against the alarm's push, FOLLOW goes with it.
3. **KNOWN AT.** This is an outcome, so it is known only after the whole hold. `known_at_us` = decision + 6 s delay + 60 s (the fill's longest wait) + 4 h hold. No as-of reader can take it for context. `as_of_us` is the alarm. `read()` gives back `t_alarm` and `t_decision`; `join()` matches rows with `alarm_context` on coin, alarm and decision, to the millisecond.
4. **INPUTS.**
   - The alarm list (EVENTS tsv).
   - Lab 3 s Binance bins, read through `lab3` with purpose `research`.
   - The entry is SCOUT's `heat_offer_v2.entry_row`, unchanged:
     - BED `fill_v2` taker fill after the 6 s execution delay (BED's own +3 s inside);
     - BED `ladder_v6` first touches of 25 levels, 0.1 … 2.5%;
     - a bin that crosses both levels counts as heat first.
   - Settings: decisions, delay, hold.
5. **NOT IN IT.** No context (that is `tools/alarm_context`), no costs, no trails, no PnL.

## Stored (the raw measurement, once)

| name | meaning |
|---|---|
| `filled` | 1 = filled; 0 = not, and the reason says why (STALE, NO_FILL, GAP, NO_DATA) |
| `fill_wait_s` | seconds from decision + delay to the fill |
| `move_wait_pct` | move in the entry side from the alarm to the decision |
| `known_s` | seconds of path known after the fill: the hold, or less when prices stop at a sealed or unbuilt day |
| `fill_px` | the fill price; the fill time = decision + 6 s + `fill_wait_s` (to re-check touches against raw bins, or add costs later, without re-running BED) |
| `ot_01` … `ot_25` | seconds to the first touch of offer +0.1 … +2.5%; empty NOT_REACHED |
| `ht_01` … `ht_25` | seconds to the first touch of heat −0.1 … −2.5%; empty NOT_REACHED |

## Stamps (derived when read: `stamps(read(...), offers, horizons)`)

| name | meaning |
|---|---|
| `reach_<o>_<H>m` | 1 = offer o came within H minutes; 0 = it did not; NaN = path not known that far |
| `hb_<o>_<H>m` | heat before offer o: the largest heat first touched at or before the offer (0 = none); NaN if not reached |
| `hw_<H>m` | the largest heat within H minutes |

The defaults are offers 0.2 … 2.0 and horizons 15, 30, 60, 120 and 240 min. Any other set comes from the same stored touches, with no rebuild.

## Subjects

- **`A02`:** the alarms.
- **`A02_MATCH`:** the matched random moments (`tools/alarm_match`), the baseline the alarm must beat.

## Output: the one format

- **Writer:** `lab3.write.write_part`, into `<DATA_ROOT>/research_days`.
- **Part:** `STAMP.A02.FADE` or `STAMP.A02.FOLLOW`, store kind ROWS, 54 codes each (`STAMP.A02.<FADE|FOLLOW>.<name>`; a code name may not be held by two parts of one day: J36476), listed in the generated `STAMP_CATALOG_V1.tsv`.
- **Generated once.** The seal holds the settings. The sources hold the sha16 of:
  - the alarm list;
  - this code and the catalog;
  - `alarm_context.py`, SCOUT's `heat_offer_v2.py`, BED's `fill_v2.py`, `ladder_v6.py` and `ladder_v2.py`;
  - every lab bins index it read.
- **Sealed days** come from `alarm_context.SEALED`: every day from 1 Jan 2026 (December 2025 opened by the owner 21 Oct 22:06 / 23:09 Berlin; the tests seal December for themselves):
  - Their prices are never asked for, so a path stops at the sealed day and `known_s` is shorter.
  - Alarm days and decision times on them are not written.
  - **1 Jan 2026** is refused as an alarm day, as in alarm_context (`sealed_read`), so every stamp row has its context row. Its raw prices are fine.
  - Reading them is refused.

## Run

```
python3 alarm_stamp.py build <lab_days> <lab3 code> <BED e_fill> <BED e_ladder> <EVENTS tsv> A02 FADE 20250912 20251130 [out root] [decisions min]
python3 alarm_stamp.py show  <DATA_ROOT>/research_days <lab3 code> A02 FADE 20250912 20251130
```

## Checklist (TOOL_DESIGN_V2)

- [x] design note (above)
- [x] own folder: README, code, STAMP_CATALOG_V1.tsv, tests, mutants
- [x] values only through lab3.write; read through lab3.days; text only for meaning
- [x] catalog for every value; sources by sha16; settings as the seal
- [x] generated once; determinism and range tests (Mac, `OneFormat`)
- [x] tests: 19 in total. They cover:
  - BED's real fill and ladder on planted 3 s paths, checked by hand;
  - FADE and FOLLOW as mirrors;
  - same second counts as heat first;
  - each horizon sees only its own minutes;
  - a touch after a data hole is not seen;
  - a path that stops at an unbuilt day;
  - 30 Nov never reads December (planted ±50% in December leaves every value unchanged);
  - sealed and cutoff alarm days refused;
  - not-filled rows say why;
  - exact keys;
  - the join with alarm_context;
  - both directions in one root, read back (J36476 found the clash);
  - known_at pinned to decision + 14,466 s and never before fill + hold (SCOUT MUST 1);
  - read() refuses December and the cutoff (SCOUT MUST 2);
  - a touch at exactly H minutes counts within H;
  - 1 Jan refused.
- [x] mutants:
  - `python3 -B mutants_alarm_stamp.py <tools dir>`: 15 planted bugs, all killed.
  - SCOUT's `alarm_stamp_mutants_scout_v1.py`: 14 of 14 killed (VM).
- [x] Mac job: J36477, max RSS 0.3 GB.
- [x] SCOUT review 18:28Z: PASS WITH 2 MUST (tests only). Fixed in v1b.

## Old stamps (J33689) vs these (J36477)

| | old | new |
|---|---|---|
| reach 0.5% within 60 min, FADE | 0.629 | 0.648 |
| FIRE rows, 12 Sep – 30 Nov | 1,040 | 1,164 |

**Opinion, not checked:** the gap is the alarm set. J33689 read the rows of the lag-6 cube (`CUBE_BO0.5`), not every alarm of `q_33614/EVENTS.tsv`. Its times were printed with 6 significant digits, so its rows cannot be matched one by one to check this. The entry rule is the same (SCOUT's entry_row, +6 s).
