# launchers (released with ALARM_BUILD_V20; reuse text for V26, SCO-A183; history: PROCESS_V26.md steps S1 to S6 are the one route): how an alarm run is launched by an orchestrating session
ALARM_RUN_LAUNCHER_EXAMPLE_TRIALJ.js (b33c9da63a755f09) is the exact Workflow script SCOUT used on 6 Nov 2026 for trial J (ALARM_BUILD V17). Four agents in order:
1. prep: builds the run folder, the agent prompt from the pack PROMPT, ops/PARENT_STEP.md; answers one JSON line (prompt, sha16s, task id, init command).
2. launcher: checks the sha16s, runs run_kit init (opens the time log at the phase start).
3. hunter: reads the prompt, follows the pack to the end (pipeline run, ANALYZE, CARD_REVIEW, PROPOSE).
4. parent close: runs the run kit close and bind from ops/PARENT_STEP.md.
To reuse for V26: copy the script out of this read-only folder and change the brief file name and its sha16, the version (V26), the labels, and every tool path to the released ones:
- pack: <RELEASE_ROOT>/Alarm/alarm_design/current (PROMPT_V26.md, MANIFEST_V26.tsv)
- KIT: <RELEASE_ROOT>/Learning_Loop/run_kit/current/tree/team/SCOUT/pack_kit/run_kit_v3_1/run_kit_v3_1.py (the script names run_kit_v3: history)
- PIPE: <RELEASE_ROOT>/Alarm/alarm_pipeline/current/tree/team/SCOUT/pack_kit/alarm_pipeline_v1/alarm_pipeline_v1.py
The brief for the prep step is the only per-run input. The commands of each step: START_V26.md HOW TO LAUNCH.
