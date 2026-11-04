Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/alarm_design/alarm_design_v2.py (docstring), alarm_design/README.md and RELEASE_alarm_design_V3_8_1.json; not the owner's document (owner seat: ALARM).

# alarm_design (the lab engine): scope

## Purpose and user
alarm_design_v2.py is the lab engine: it says what an alarm definition (a JSON file) means. detect.py imports it, never copies it: the
condition masks, the side rule, the onset rule and refractory, and the shared "is this step known" rule all come from here.
Owner seat ALARM; reviewers STRATEGY (LEAD) and LAB1. In this part it serves Detection; its own commands (run, try, card) also build fair
comparison moments, labels and a truth card.

## In scope (for Detection)
- Loading and checking a definition (load_def): inputs, shared and claim conditions, onset, refractory, side, grid_s (a multiple of 5 s),
  claim type and footprint.
- The 5 s internal clock (lab3 as-of rule), condition masks, conditions_known, side_of, find_fires.

## Out of scope
- Reading any day outside the run's window or past the seal LAB1 sets in lab3/law.py (refused: PermissionError).
- Prices after the fire, money, costs.

## What success means
- GRID and BASE paths agree (one shared conditions_known; V3.8.1).
- Its tests pass: test_alarm_design_v2.py (33) and test_onset_knownness.py (3), run here from this folder.
