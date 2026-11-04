# alarms: tool card

The landed finders: each turns lab days into one registered alarm's fire list as its card says, with a plain-loop twin. The code: [the folder](../01_Detection/tree/team/RESEARCH/tools/alarms) (a01_onset_v2, a02_climax_v3, b7_wide_pressed_v1, b8_roll_v1, k0_busy_now_v1, n1_busy_burst_v2, o1_flush_v2, o5_both_v2, onset_band_v6, q16_vwap_v1 and others). Status words per alarm: 01_Detection/tree/team/RESEARCH/alarms/ALARMS_V1.tsv. More: [README](../01_Detection/alarms/README.md).
Read from the code and README for ALARM_V1_19 (SCOUT helper, 2 Nov 2026); not run for this card. Status in the code: TEST, unless it says otherwise.

## Run it
```
python3 -B <INSTALL>/01_Detection/tree/team/RESEARCH/tools/alarms/<finder>.py <arguments>
```
- The arguments differ by finder and are positional, with no usage check (k0_busy_now_v1, o1_flush_v2: 6 and more; onset_band_v6: 7 and more): read the finder's text first. A new alarm goes through the loop in AGENTS.md, not through a new finder. alarm_design imports onset_band_v6.
