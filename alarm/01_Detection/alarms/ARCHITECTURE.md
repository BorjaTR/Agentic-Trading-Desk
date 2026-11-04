Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/alarms/README.md, BASELINE.tsv and the finders' code (imports, usage lines); not the owner's document (owner seat: SCOUT for the bench; QUANT for the landed finders).

# alarms (landed finders): architecture

## Inputs
Lab days (argument <lab_days>; settings key LAB_DAYS) read through lab3 (argument <lab3 code dir>: this part's tree/team/LAB3/code or
../_vendor/LAB3_code), a day range, the last readable day, coins. alarm_view_v1 uses pandas' rolling windows when pandas is there (else numpy windows: the same numbers).

## Steps (every finder)
1. Read the codes the card names on the 5 s clock (lab3 as-of rule), the 14 built days before each day for the coin's own band.
2. Own-band onset: fire at the first step past the edge after a clean step not past it; refractory per coin (15, 30 or 60 min, as the card says), across midnight.
3. A second computation (a plain-loop twin, or the v1 reference for o5_both_v2) checks the fires; the D2 columns describe the fire (never used by the rule).

## Outputs (in the <out dir> argument, a new folder per run)
<ALARM>_EVENTS.tsv (the fire list), <ALARM>_FIRES.tsv, <ALARM>_PROOF.txt (or _TIMES.txt).

## Files here (tree/team/RESEARCH/tools/alarms/; sha16 = BASELINE.tsv LANDED row)
| file | alarm | imports |
|---|---|---|
| onset_band_v4.py af9b49e682aad028 | N5, N2 V2, N3 V2, N9 V2, N4 V2 (rule alarms/ONSET_RULE_QUANT_V1.txt) | lab3 |
| onset_band_v6.py 9acf9cc8a0b24f53 | v4's alarms + Q1, Q4 | lab3 |
| n1_busy_burst_v2.py 9c511bd0bdbafe08 | N1 v2 | lab3 |
| k0_busy_now_v1.py 9869be3abb4829ad | K0 (control) | lab3, onset_band_v4 |
| b7_wide_pressed_v1.py eee6434571d63f45 | B7 | lab3, onset_band_v4 |
| b8_roll_v1.py 991d0eedc6893fd7 | B8 | lab3, onset_band_v4 |
| o1_flush_v2.py 4f0f2121deda5414 | O1, O2 | lab3, onset_band_v4 |
| o5_both_v1.py d1a1c9b084c392d9 | O5 (reference) | lab3 |
| o5_both_v2.py 3a99d5ca112c52fd | O5 | alarm_view_v1 |
| q16_vwap_v1.py 2ca92bb9a8d970af | Q16 | alarm_view_v1 |
| alarm_view_v1.py 6e25ccaf52f736c8 | the shared alarm layer (View) | lab3; pandas when present |
Each has test_<name>.py beside it (o5_both_v1 is tested through test_o5_both_v2). Cards: tree/team/RESEARCH/alarms/.

## Settings
LAB_DAYS (argument). No path is built into the landed finders (MACHINE_PATHS.tsv has no row for them).

## How it is tested
python3 -B _tools/run_isolated_v1.py 01_Detection/tree/team/RESEARCH/tools/alarms/test_<name>.py, one per finder (RUN_PROOF.md). Planted
data only.
