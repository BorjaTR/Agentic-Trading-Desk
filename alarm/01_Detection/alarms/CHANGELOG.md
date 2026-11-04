Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/alarms/BASELINE.tsv and README.md; not the owner's document (owner seat: SCOUT for the bench; QUANT for the landed finders).

# alarms (landed finders): changelog (newest first; times UTC from BASELINE.tsv landed_utc)
| landed | file (sha16) | what and why | test receipt (BASELINE.tsv) |
|---|---|---|---|
| 21 Oct 07:56 | alarm_view_v1.py 6e25ccaf (replaces f22497cc) | + minute_sums and View.bin_minutes, for Q16 | test_alarm_view_v1.py 05a2d0e6: 19 tests (J33579) |
| 21 Oct 07:56 | q16_vwap_v1.py 2ca92bb9 | new: Q16 TAKER VWAP PRESSURE on alarm_view | test_q16_vwap_v1.py 85423878; SCOUT rebuild J36221 equal |
| 21 Oct 07:07 | o5_both_v2.py 3a99d5ca, o5_both_v1.py d1a1c9b0 | O5 on alarm_view (v2), v1 kept as its reference | test_o5_both_v2.py 43fe9534: equal to v1 on 1,515 DEV lines |
| 21 Oct 07:07 | alarm_view_v1.py f22497cc | new: the alarm layer, look-ahead proof once (owner 21 Oct: "build something on top ... so we do it once only") | test_alarm_view_v1.py 74bcf483: 21 tests |
| 21 Oct 02:24 | o1_flush_v2.py 4f0f2121 | new: O1 LONG FLUSH / O2 SHORT SQUEEZE | test_o1_flush_v2.py 3a61c4ea; SCOUT rebuild 9,851 of 9,851 |
| 21 Oct 01:54 | b7_wide_pressed_v1.py eee64345 | new: B7 WIDE AND PRESSED | test_b7_wide_pressed_v1.py d3dd58f2; rebuild 116,866 of 116,866 |
| 21 Oct 01:11 | b8_roll_v1.py 991d0eed | new: B8 ROLL SPREAD | test_b8_roll_v1.py 7c54fba5; rebuild 14,480 of 14,480 |
| 21 Oct 00:10 | onset_band_v6.py 9acf9cc8 | v4 + Q1 OFI BURST and Q4 BASIS JUMP; v4 alarms unchanged | test_onset_band_v6.py da64fbd1; rebuild 31,275 and 7,780 equal |
| 20 Oct 20:40 | k0_busy_now_v1.py 9869be3a | new: K0 PRICE SWING (control) | test_k0_busy_now_v1.py b07c91df; rows K0-* reproduced |
| 20 Oct 20:15 | n1_busy_burst_v2.py 9c511bd0 | N1 v2 BUSY BURST | test_n1_busy_burst_v2.py 67d774aa; rows N1-* reproduced |
| 20 Oct 20:15 | onset_band_v4.py af9b49e6 | new: the own-band onset finder (N5, N2 V2, N3 V2, N9 V2 proven; N4 V2 not) | test_onset_band_v4.py 88c53387; reproduces N5 sealed rows byte for byte |
