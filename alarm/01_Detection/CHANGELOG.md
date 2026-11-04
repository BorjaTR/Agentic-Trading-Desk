# 01 Detection: what changed in each release (newest first)

Source of every line: the release file named (fields `by`, `landing`, `changed`, `status`) or the tools/alarms BASELINE.tsv row. The
tool folders hold the full tables: [detect/CHANGELOG.md](detect/CHANGELOG.md), [alarm_design/CHANGELOG.md](alarm_design/CHANGELOG.md),
[alarms/CHANGELOG.md](alarms/CHANGELOG.md).

## detect (owner STRATEGY/LEAD; detect.py keeps VERSION DETECT_V1; the editions are the idea_to_grade releases that pin it)
| release | detect.py | what changed and why |
|---|---|---|
| V2_3_1 (in use) | 83c52bfd27166f76 | the A54-FINAL-01 onset repair: a shared condition known to be false is a decided OFF step, so a real onset is no longer missed (BTC 2025-10-10 14:58); nests alarm_design V3_8_1; two signatures |
| V2_3 | 23f9cec148975cea | nests alarm_design V3_8 (the first cut of that repair); detect.py unchanged |
| V2_2 | 23f9cec148975cea | grader side only (PRICE source identity); detect.py unchanged |
| V2_1 CANDIDATE | 23f9cec148975cea | fixes for the outside review A53 (its 6 regressions are test_detect_a53.py) |
| V2 CANDIDATE | c536f0bc308ec5c9 | guards only: refusals before any output, a required research window, code pins per worker, worker watchdog |
| V1 CANDIDATE | 770e0afa0221276f | first edition: the outside detector's meaning; 14,289 alarms equal to the outside selection (BN_OI idea, 52 coins) |

## alarm_design (owner ALARM)
| release | what changed and why |
|---|---|
| V3_8_1 (in use) | the same onset repair, final: one shared conditions_known for BASE and GRID (alarm_design_v2.py, README.md, test_onset_knownness.py); an independent checker signed |
| V3_8 | its first cut (an unapproved intermediate, replaced) |
| V3_7, V3_6, V3_5 | LAB1's labcore cycles V2_7, V2_6, V2_5 (engine, tests and planted bugs re-pinned) |
| V3_4 | the A35-AD-01 fix (passed by diff by LAB1 and QUANT) |
| V3_3, V3_1, V2_1 | recuts for labcore cycles (no engine change listed) |
| V3_2, V3 | the outcome side added (offer_edges_v1, grade_edges_v1): not copied here |
| V2 | the first release of alarm_design_v2.py (the outside review's D05, S06, S07; LAB1 PASS) |

## alarms (the landed finders; owner SCOUT for the bench, QUANT for the finders; times UTC from BASELINE.tsv)
| landed | file (sha16) | what |
|---|---|---|
| 21 Oct 07:56 | alarm_view_v1.py 6e25ccaf, q16_vwap_v1.py 2ca92bb9 | the alarm layer gains minute sums (replaces f22497cc); new Q16 TAKER VWAP PRESSURE |
| 21 Oct 07:07 | o5_both_v2.py 3a99d5ca, o5_both_v1.py d1a1c9b0, alarm_view_v1.py f22497cc | O5 on the new alarm layer, v1 kept as its reference; the alarm layer with the look-ahead proof made once |
| 21 Oct 02:24 | o1_flush_v2.py 4f0f2121 | O1 LONG FLUSH and O2 SHORT SQUEEZE |
| 21 Oct 01:54 | b7_wide_pressed_v1.py eee64345 | B7 WIDE AND PRESSED |
| 21 Oct 01:11 | b8_roll_v1.py 991d0eed | B8 ROLL SPREAD |
| 21 Oct 00:10 | onset_band_v6.py 9acf9cc8 | v4 plus Q1 OFI BURST and Q4 BASIS JUMP (v4's alarms unchanged) |
| 20 Oct 20:40 | k0_busy_now_v1.py 9869be3a | K0 PRICE SWING (a control) |
| 20 Oct 20:15 | onset_band_v4.py af9b49e6, n1_busy_burst_v2.py 9c511bd0 | the own-band onset finder (N5, N2 V2, N3 V2, N9 V2 proven; N4 V2 not); N1 V2 BUSY BURST |

Editions not released yet (the DRAFT finders, detect_aw1, the chain's list step, the kit's COUNT job and hand checks) are listed in the
README under "In development" and stay in the dev tree until reviews release them.
