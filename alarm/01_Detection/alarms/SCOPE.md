Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/alarms/README.md, BASELINE.tsv and the docstrings of the landed finders; not the owner's document (owner seat: SCOUT for the bench; QUANT for the landed finders).

# alarms (the alarm bench, landed finders only): scope

## Purpose and user
Each finder turns lab-day readings into one registered alarm's fire list (EVENTS.tsv: coin, t, side, ...) exactly as its card says,
with a second computation (a plain-loop twin) for proof. Users: the research desk and the lab engine (alarm_design imports onset_band_v6).
Bench owner SCOUT (20 Oct 2026); the landed finders are QUANT's, landed after review (BASELINE.tsv status LANDED).

## In scope (here)
The 11 landed finders: onset_band_v4 (N5, N2 V2, N3 V2, N9 V2, N4 V2), onset_band_v6 (Q1 OFI BURST, Q4 BASIS JUMP), n1_busy_burst_v2 (N1),
k0_busy_now_v1 (K0, a control), b7_wide_pressed_v1 (B7), b8_roll_v1 (B8), o1_flush_v2 (O1 and O2), o5_both_v1 and o5_both_v2 (O5),
q16_vwap_v1 (Q16), and the shared reader alarm_view_v1 that o5_both_v2 and q16_vwap_v1 use.

## Out of scope
- Finders that are DRAFT or have no BASELINE row (A01, A02, A03, A08, A18, B6, C1, M1-M5, N6-N11, P2-P11, the check runner): TEST editions,
  not here (README.md, "In development").
- Outcomes and money (the offer test lives in tools/alarm_check, not here).

## What success means
Each finder's own tests pass from this folder; its fires equal its twin and the sealed or rebuilt rows named in BASELINE.tsv.
