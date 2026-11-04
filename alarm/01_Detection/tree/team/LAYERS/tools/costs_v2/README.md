# costs_v2: the cost of record (board T04), ARCHITECTURE V1 (step 2). LAYERS, 23 Oct 2026; ask STRATEGY-143903

Research: team/LAYERS/research/RESEARCH_COST_MODEL.md 02384f623b98a0b9 (SIGNED STRATEGY 13:31:02Z with Q1-Q5; LAB1 gate PASS 13:33:50Z;
SCOUT PASS + 1 MUST 13:32:57Z). Owner LAYERS (design), builder BUILD2 (labcore.costs V3 = this design), tester TEST1, panel QUANT + SCOUT,
LAB1 gate. PAPER F258. Replaces labcore.costs fc2ae669 (V1 table + gap, median fallback, no funding): the old load_cost stays importable,
marked superseded, until every caller moves (list in section 8).

## 1. Design note
1. QUESTION: what one trade costs, as ONE number every tool uses, split in its parts: fee, book, gap, funding; and the same cost at 1.5x
   and 2x; plus the cost KNOWN AT THE FIRE for any decision that compares a move with cost.
2. UNIT: one trade (coin, side, entry time, exit time, size); or one moment (coin, t) for the cost alone.
3. KNOWN AT: cost_fire at the decision time (stored X1.COST values with known_at <= t only, join guard); charging cost (table of
   record) is a fixed assumption, NEVER a feature; funding_paid is known at the exit (known_at = t_out).
4. INPUTS (sha16 at the time of writing; the build pins them in RELEASE):
   | input | path | sha16 | use |
   |---|---|---|---|
   | cost table V1 | team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv | ff157578098a2f47 | book part per coin (hl or binance walk, the dearer) |
   | cost table V4 | team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V4.tsv | 906f6d3b3403944c | book by coin and UTC hour (cost_bp - 9 fee) |
   | HL settled hourly funding | <DATA_ROOT>/hl_funding_hourly/<COIN>/<YYYYMM>.tsv (hl_funding_pull_v1 06457547, reader read_month) | per file, MANIFEST | funding_paid |
   | the old receipt | team/RESEARCH/QUANT/receipts/q_471169_HL_FUNDING_HOURLY.tsv | c372caf7829d450a | cross-check only (test C9), never read by the API |
   | X1.COST.S04, S05 | lab_days part X1.COST via lab3.days (5 s, PROVEN; metric_brief) | the part's index | cost_fire |
   | settings | tools/costs_v2/settings/COSTS_SETTINGS_V1.json: fee_side_pct 0.045, gap_leg_pct 0.072, size_usd 10000, stress [1.5, 2], table paths + sha16 | its sha16 | all |
   APPROXIMATION (STRATEGY M3): funding is charged on the ENTRY notional, not on the hourly mark value of the position.
5. NOT IN IT: no maker fill, rebate, tier or HYPE discount (fee taker both legs, tier 0); no size above 10,000 USD (refused, until an
   HL size curve exists); no fill model (delay, missed: T12 paper_fill_record); no HL book (until 4 weeks of the HL recorder).

## 2. The table of record (built once, C2)
COSTS_OF_RECORD_V1.tsv (tools/costs_v2/receipts/, written by make_record_v1.py, its header names both sources by sha16 and says
APPROXIMATION: books from Binance Oct-Dec 2025 x one HL day; funding on the entry notional): one row per (coin, hour_utc 0-23): book_bp = max(V4 cost_bp - 9, V1 cost_bp - 9) (the dearer, STRATEGY Q1), source
(V1 or V4), filled (V4's own mark). Coins: those in BOTH tables; a coin in one table only is named in the header and has no row (refused).
Measured on the research note: median coin-hour 16.2 bp (V4) -> 17.5 bp (dearer of, with the fee).

## 3. The API (labcore.costs V3; numpy, vectorised over trades; one table and one funding month read per process)
| function | returns | rule |
|---|---|---|
| cost_at(coin, t_us, purpose) | dict of arrays: fee_bp, book_bp, gap_bp, total_bp, total_x1_5_bp, total_x2_bp, reason | the record row of (coin, UTC hour of t); total = fee + book + gap; stress = fee + k (book + gap); unknown coin or hour: NaN + reason NO_COST (never a median, STRATEGY Q4); purpose is REQUIRED, 'charge' or 'select', and 'select' always raises ValueError (LAB1 MUST 2) |
| cost_fire(coin, t_us, purpose) | same keys + known_at_us | fee + (X1.COST.S04 + S05 at the last 5 s point u <= t with known_at <= t) + gap: the Binance round trip at 10k at the fire (SCOUT MUST); empty X1.COST cell: NaN + its EMPTY reason (BOOK_HOLE, EXH, ...), never filled; X1.COST is read through lab3.days with the CALLER's purpose (research stays research: the seal and the quarantine apply), never a reader of its own (LAB1 MUST 1) |
| funding_paid(coin, side, t_in_us, t_out_us, source='stored') | funding_bp, hours, missing, reason, source | sum over settled hour ends h with t_in < h <= t_out of rate(coin, h) x 1e4 x (+1 long, -1 short) (a long pays a positive rate); a missing hour: NaN + reason FUNDING_MISSING (never filled); known_at = t_out; source 'recorder' = the HL recorder's live rates (paper and live, LIVE4 T12), the same rule, the source named in every row (LAB1 MUST 3) |
| trade_cost(coin, side, t_in, t_out, size_usd) | the parts of cost_at at t_in + funding_paid; size > size_usd: reason SIZE_REFUSED | what money tools subtract (bp of the entry notional): total = fee + book + gap + funding_bp |

SIGN (STRATEGY M1): every cost part is positive when the trader PAYS. funding_bp > 0: the trader pays (a long under a positive rate, a
short under a negative rate); funding_bp < 0: the trader receives (a short under a positive rate, a long under a negative rate). Net
result = gross move (side-signed) - total.
| gap_bp(priced_on) | 2 x gap_leg (14.4 bp) when fills are priced on Binance, 0 when on HL trades | one setting, never a constant in a tool |
All values in bp of notional; one module-level settings load with sha check (labcore settings loader); no file written by the API.

## 4. Data (0c / 0d)
| store | format | months | one reader | already computed? |
|---|---|---|---|---|
| COSTS_OF_RECORD_V1.tsv | tsv (input-shaped table, 3b) | a fixed assumption | labcore.costs V3 | built once by make_record_v1 |
| hl_funding_hourly | tsv per coin-month (raw record, 3b) | Sep 2025 to May 2026 (one source: the API's settled rates; J20262079 widened to 202509..202605, see 9) | hl_funding_pull_v1.read_month, re-exported by labcore.costs | being downloaded |
| X1.COST | lab3 part | the BUILD window on lab_days | lab3.days (asof) | yes (PROVEN) |

## 5. Times and lookahead (0d f, g)
- cost_fire: join_guard(known_at_us <= t_us) on every X1.COST value it uses (labcore.lookahead 844c7c3a).
- cost_at: the record is built from Oct-Dec 2025 Binance books and 20 Oct 2026 HL books: it carries known_at = NaN and the API refuses
  it as a selector: purpose is required and 'select' always raises ValueError; gates and skips use cost_fire.
- funding_paid: known_at = t_out; a caller joining it to an entry decision trips the join guard.

## 6. Tests first (tests/test_costs_v3.py, planted, seconds)
C1 the record: dearer of V1 and V4 per coin-hour on a planted pair; a coin in one table only refused (NO_COST).
C2 cost_at: hour lookup at 23:59:59 and 00:00:00; total = fee + book + gap; stress lines fee + k(book + gap) (fee and funding exact).
C3 unknown coin or hour: NaN + NO_COST (a mutant with the median fallback fails).
C4 funding sign, both ways: a positive rate makes a long pay (funding_bp > 0) and a short receive (< 0); a NEGATIVE rate makes the short
   pay and the long receive (STRATEGY M1); hours counted as (t_in, t_out] (entry 10:00:00 exactly does not pay 10:00).
C5 funding missing hour: NaN + FUNDING_MISSING (a mutant filling with 0 or the interest rate fails).
C6 cost_fire known at: a huge X1.COST value planted 1 s after t changes nothing (future plant); prefix check; join guard refuses.
C7 size above 10k: SIZE_REFUSED.
C8 one c: label c, gate c and exit c of one planted fire are the same number through trade_cost (QUANT T03 M2).
C9 funding tie: the downloaded Sep-Dec 2025 hourly rates equal q_471169's per (coin, hour) (named differences only).
C11 purpose: cost_at and cost_fire without purpose raise; 'select' raises; cost_fire on a sealed day with purpose research is refused as lab3.days refuses it.
C12 live funding: funding_paid(source='recorder') equals source='stored' on an hour both hold (named differences only).
C10 determinism: two runs, the same arrays; the record file's sha16 the same.

## 7. Proof table (PROOF_COSTS_V1.tsv, step 6)
Rows: the record's sha16 and its V1/V4 shares; 5 hand-checked trades (fee, book, gap, funding by hand from the files); the funding tie
(C9 counts); a LOOKAHEAD row (C6); COVERAGE rows (STRATEGY M2): by month, the share of A02P fires (and of each money run's trades)
refused for NO_COST or FUNDING_MISSING, with the coins named; a money run above 5 pct refused is capped INCOMPLETE (the same 5 pct line as
exit_engine and the factory); a SPEED row: 1 million trade_cost calls on one month under 2 s (numpy, one table read).

## 8. Callers to move (each through labcore.costs, never a TSV by hand; their owners)
bucket_proof (load_cost V1 + gap), exit_engine T03 (BUILD1), paper V4 / T12 (LIVE4), alarm_context cost_bp/cost_tier V4 (flagged:
cost_tier may not select), alarm_triage V4, heat_offer v1/v2 V3, alarm_offer V2, model_v1 tools V1 (receipts, stay under their own
settings, STRATEGY 13:31:02Z).

## 9. Open (one line each, for the panel)
O1 cost_fire = the round trip at the fire (S04 + S05): YES (STRATEGY 14:41:52Z).
O2 one API funding source Sep 2025 to May 2026, q_471169 only for C9: YES (STRATEGY 14:41:52Z).

## Checklist
- [x] looked first (four tables, labcore.costs V1, X1.COST, the funding receipt and store)
- [x] design note; inputs with sha16; outputs; set list (lab3.days, labcore.lookahead, labcore settings loader)
- [ ] tests (BUILD2 writes them first from section 6); [ ] panel QUANT + SCOUT; [ ] LAB1; [ ] proof table; [ ] RELEASE json
