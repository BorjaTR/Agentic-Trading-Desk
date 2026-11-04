Written by SCOUT for the repo on 30 Oct 2026 from tree/team/RESEARCH/tools/alarm_design/alarm_design_v2.py (functions and docstring), alarm_design/README.md and the RELEASE_alarm_design_V*.json files; not the owner's document (owner seat: ALARM).

# ARCHITECTURE: alarm_design, the lab engine (release V3_8_1)

## Inputs
| input | format | read by |
|---|---|---|
| a definition | JSON (README section 2 and "V3 contract"): inputs (op, code, windows), shared and claim conditions, side, onset, refractory_s, grid_s (a multiple of 5 s), claim.type, claim.footprint_s, window | `load_def` |
| lab days | the lab's one format, read only through lab3 `Days(root, 'research')` (lab3 refuses sealed days) | `LabSource` |
| stored event lists | TSV (coin, t, side ...), only when a definition uses an event op | `LabSource` |

## Steps (functions in alarm_design_v2.py)
1. `load_def` checks the definition and refuses a bad one.
2. `LabSource` and `Ctx` put every input on the 5 s clock (column k = the value known at day start + 5 s x k), with day D-1 beside D.
3. `cond_mask`, `masks`, `conditions_known`: which steps hold and which are decided (V3.8.1: one shared `conditions_known` for BASE and GRID).
4. `side_of`, `find_fires`: the fire steps after the onset rule and the refractory.
5. Not used by Detection: `base_rows`, `match`, `label_values`, `card` (fair comparison moments, labels, the truth card: the outcome side).

## Outputs
For detect.py: masks and fires in memory (detect writes the files). The engine's own run command writes parts through lab3.write.

## Files here (tree/team/RESEARCH/tools/...)
| file | what |
|---|---|
| alarm_design/alarm_design_v2.py | the engine (70de3f03faaeaa74) |
| alarm_design/test_alarm_design_v2.py | planted tests (33) |
| alarm_design/test_onset_knownness.py | the V3.8.1 onset knownness tests (3, pytest) |
| alarm_design/README.md | the manual (definition format, V3 contract, V3.8.1) |
| alarm_design/RELEASE_alarm_design_V2.json ... V3_8_1.json | the 12 release records (V3_8_1 is in use) |
| alarms/onset_band_v6.py | imported at load: the 14-day own band (pinned by V3_8_1; also a landed finder, see ../alarms) |
| model_v1/matched_controls_v1.py | imported at load: the busy base (pinned by V3_8_1) |
Release V3_8_1 lists 16 files. The 10 not copied are the outcome side, which Detection never runs: grade_edges_v1.py, offer_edges_v1.py,
null_calibration_v1.py, their tests and planted bugs, mutants_alarm_design_v2.py, tools/alarm_checks/offer_ladder_v1.py,
ALARM/settings/WINDOWS_V1.json and ALARM/receipts/null_cal/NULL_CAL_V1.txt.

## Settings keys a real run needs
`LAB_DAYS` (detect passes it as lab_root; the engine's own default `<DATA_ROOT>/lab_days` at line 26 is an argument default).
lab3 is found at `<forensics>/team/LAB3/code`, here `tree/team/LAB3/code` (relative, no setting). The engine refuses any day lab3's law
seals (PermissionError).

## Tests
`test_alarm_design_v2.py` (33) and `test_onset_knownness.py` (3) on planted data; no lab day is read. RUN_PROOF.md of the part shows
both run from the repo and from a copy.
