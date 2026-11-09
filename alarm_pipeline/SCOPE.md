# alarm_pipeline ALARM_PIPELINE_V1: scope (SCOUT, 6 Nov 2026; status RELEASED, playground tool, TEST, NOT REVIEWED)

Edition ALARM_PIPELINE_V1_4_1 (SCO-A183, 7 Nov 2026): reads the Alarm edition ALARM_V1_22_1 (pipe_mac_v3 INSTALL) and runs the bridge MAC_DESK_V49_3; scope otherwise as below (V1_4: Sep-Mar windows).

Owner seat SCOUT (built SCO-A153/A154, installed SCO-A159). Source: tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py docstring.

## What it is for
Runs the whole alarm design process (ALARM_BUILD V18, 22 steps from INPUT to HANDOFF) from ONE agent-written input; the agent only analyzes.

## Inputs
- INPUT.json (template tree/team/SCOUT/pack_kit/alarm_pipeline_v1/INPUT_TEMPLATE.json): task, seat, run, idea, def and def_sha16, claim, window, block, registry_mode (write or replay), and more.
- PIPE_SETTINGS.json: runner root and queue, kit paths.

## Outputs
In the run folder only: STEP_<nn>_<NAME>.json per step (command, outputs with sha16, numbers copied from the tool output), PENDING/FILING files, and at step 22 ALARM_CARD_<ALARM>.md/.tsv, ALARM_CARDS/<MECHANISM>/<ALARM>/, HANDOFF.json and one INDEX.tsv row (twin first).

## The one command
python3 -B tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py init <run folder> --input INPUT.json --settings PIPE_SETTINGS.json
then python3 -B tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py run <run folder>  (also next, status, retry)

## Refusals
STOP <nn> <NAME> <CODE>: <why>. Exit 0 DONE, 10 WAIT, 3 STOP, 2 usage. Months outside Sep 2025 to Mar 2026 are refused. A replay never adds a try.

## Tests (from writable copies proven equal with diff -rq)
- Mac, job 20270215 (Q_V16, exit 0): pipeline_v1 41 of 41, card_v2 4 of 4, mechanism_v2 17 of 17.
- VM: card_v2 4 of 4, mechanism_v2 17 of 17; pipeline_v1 log shows 28 PASS, 0 FAIL, then ends without a RESULT line (not complete on the VM).
- Planted and fake runner data only: never run end to end on a real alarm from this install.

## What it never does
Never bypasses a kit refusal; never re-grades a graded variant; no rm, no git; writes nothing outside the run folder except through the kit tools and step 22.
