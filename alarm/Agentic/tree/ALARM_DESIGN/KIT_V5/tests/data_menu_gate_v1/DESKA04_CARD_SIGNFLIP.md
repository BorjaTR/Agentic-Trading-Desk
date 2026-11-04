# CARD SIGNFLIP (DESKA04_20261103, 2026-11-03T17:07Z from the clock). TEST, NOT REVIEWED.
Prereg of idea SIGNFLIP, one variant V1 (DESK_V0 arm A, task T04: the idea is given and run as given). Sealed before any outcome.
Claim file: ideas/SIGNFLIP/CLAIM_SIGNFLIP.md d24dbaf9483930ad.

## 1. The idea (plain words)
- Who is forced: carry traders who received funding on the old side now pay after the sign flip; they unwind against the premium move that made the flip. FADE the new payers' side (side = sign of E1.S01).
- What ends it: the unwind of the old carry; at half the default rate the payment is small, so the forced part is likely small (inferred, not measured).
- Registry check: AD15_PAYFLIP_PF2 (STOP; def cb716bcc0e4304a3): the SAME rule (tried_search_v1 --def: VERDICT DEF COPY, hc/TRIED_DEF_V1.txt 317982bece124045). SIGNFLIP is a NAMED COPY of a STOP, run as the desk brief orders; no new mechanism. AD15_PAIDLEFT_PL1 (STOP; same codes, other side), AD7_PAYERWIN_PW1 (PASS, not held; E1.S01 with a 10 min move).
- Family: FUNDING_CROWD. No new input (E1.S09 already read by PF2, PL1, PB3).
- Why the other side should lose: the flip was made by a premium move; when carry unwinds and the new payers pay, the premium leans back. FOLLOW needs a new crowd still arriving; not measured. PF2 found both sides on random.
- Waves expected Sep-Dec: COUNT 1,461 waves, 2,784 fires (below; PF2 COUNT 1,461).

## 1b. TRUE claim
- PREDICT: after the flip the old carry unwinds, so the coin's Binance open interest (E2.S01) falls more than 0.5 pct over the next 60 min.
- Label: E2.S01, when window start_s 0 end_s 3600, test falling, change pct, thr 0.5, max_age_s 120. Mirror: same, test rising. Activity: E2.S01 mode change. Claim file ideas/SIGNFLIP/TRUE_V1_OIFALL.json (perfire filled after the GRADE).
- Why: unwinding a perp leg lowers open interest; no price in it; family OI_BN, not the trigger's FUNDING_BN. It tests closing on the coin, not who closes (inferred).
- check: OK, trigger reads E1.S01,E1.S04,E1.S09; families FUNDING_BN. true_label=768f5cf34f628a1e true_mirror=68d46fd4e772f6fa
- Words: TRUE = OI falls after these fires more often than at equally busy moments and more often than it rises; NOT SUPPORTED = no unwind seen; UNSURE = too few matched fires or too wide. Forecast: NOT SUPPORTED or UNSURE (small rates, opinion).

## 2. Six quick checks
| check | result | file |
|---|---|---|
| MOMENT | E1.S01, E1.S09, E1.S04 known at the minute end (1 min step) | defs/V1.json ba27ffd4a95e1339 |
| SIDE | +1 = live estimate positive (longs now pay); lean FADE | defs/V1.json |
| METRIC CONTRACT | metric_brief_v2: all three PROVEN, flag OK (hc/HC_V1.txt 55845119c74b6efb). Menu V2: E1.S01 PROVEN pickable YES; E1.S04 CAUTION (LAB4 PARTLY) pickable NO; E1.S09 UNPROVEN (LAB4 NOT_PROVEN) pickable NO. Used anyway: the idea is the paid rate scaled by the interval; said here | METRIC_MENU_V2.tsv 97a967bd24b34757 |
| SCOPE | 50 coins with fires, 1 of 2,784 on BTC | receipts/20268022_COUNT_SIGNFLIP/COUNT_V1.tsv b33d231c37db7fe9 |
| SUPPORT | waves 182, 384, 449, 446 (Sep-Dec): 4 of 4 months with 30+ | COUNT_V1.tsv b33d231c37db7fe9 |
| MEMORY | hc_mem_probe_v3 PEAK 429 MB, limit 1272: PASS | hc/MEM_V1.txt 55562a4e1bef3e9c |

## 3. Inputs
| code | scope | means | unit | status | EMPTY means | never read as |
|---|---|---|---|---|---|---|
| E1.S01 | coin, raw | Binance live funding estimate for the next settle | fraction per 8 h | PROVEN; menu PROVEN | NO_FILE 9,412 rows on 8 d | a payment |
| E1.S09 | coin, raw | rate PAID at the last settle | fraction per the coin's own interval | PROVEN; menu UNPROVEN | also LATE_RATE | across coins without scaling to 8 h |
| E1.S04 | coin, raw | funding interval | hours | PROVEN; menu CAUTION | as E1.S01 | - |

## 4. Rule and definition
At a minute end (60 s grid): E1.S01 oppsign (E1.S09 / E1.S04 x 8), |E1.S09 / E1.S04 x 8| >= 0.00005, |E1.S01| >= 0.00005. Onset, refractory 7200 s. fire.side = sign(E1.S01) x 1. Definition ideas/SIGNFLIP/defs/V1.json ba27ffd4a95e1339 (PF2's lines; window 20250901 to 20260430).

## 5. Hand check
- 1-2 Oct BTC,ETH: 0 fires (hc/HC_V1.txt 55845119c74b6efb). Oct 2025, 5 coins: 21 fires (SOL 8, DOGE 5, ETH 4, XRP 4), e.g. SOL 2025-10-02 03:57 side -1 fe -5.1e-05 p8 +7.9e-05 (hc/HC_OCT5_V1.txt 4797c687110e684e).
- Size: quiet week 114 waves (427.5 a month), probe week 110 (412.5) (hc/SIZE_V1.txt 4ec65132832c0ed4).
- Novelty preview on the 21 Oct fires: COPY of AD15_PAYFLIP_PF2, 100 pct same fires (hc/NOVELTY_PREVIEW_V1.txt 6fe02b1efd03e78d).

## 6. Variants
| V | definition | sha16 | lean | differs from V1 by | reason |
|---|---|---|---|---|---|
| V1 | ideas/SIGNFLIP/defs/V1.json | ba27ffd4a95e1339 | FADE | - | the idea as given (desk T04), named copy of PF2 |

## 7. Forecast before any outcome (Sep-Dec)
| V | LEAD 15m low to high | LEAD 1h low to high | months with LEAD +3 (of 4) | R1 | R2 | CLEAR | why |
|---|---|---|---|---|---|---|---|
| V1 | -2 to +3 | -2 to +3 | 1 | no | no | - | same rule as PF2 (15m +0.47, 1h +0.27, 1 of 4); opinion |

## 8. Forecast Jan-Apr: none (no MONTH in this task).

## 9. What would prove it wrong
LEAD under +3 at both 15 min and 1 h in 2 of 3 counted months (STOP); FOLLOW gap as large as FADE's; TRUE NOT SUPPORTED.

## 10. Jobs and decision
COUNT 20268022; seal (this card, VARIANTS row); GRADE (queue_job_v15, JOB_GRADE_V14); TRUE (KIND TRUE); decide_v5; novelty_v5 on the GRADE fire list with --lean FADE; no ENTRY, no MONTH (desk brief).
