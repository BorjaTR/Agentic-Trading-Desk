# CLAIMS: what this repo says, and what it does not

## Alarms are not strategies
An alarm here is a rule that fires at a moment; the desk tests whether that moment is real, new, and followed by a move on one side more
often than matched random moments. That is all. An alarm says nothing about entries, exits, position size, costs you will pay, or
whether anyone can trade it. Turning an alarm into a strategy is separate work with its own tests, and it is not in this repo.

## Novelty is relative to this desk
The copy search and the novelty step compare an idea with this desk's own registry and claims. A fresh desk ships with an empty registry (the lab's found alarms are not in this repo), so NEW means not in this desk: it does not mean new to the world, to the lab, or to the playbook's recipes (alarm/playbook/PLAYBOOK.md), which a user compares by reading.

## No money claims
Nothing in this repo claims, implies or promises profit. No number here is a return you can expect. The grading compares moves after a
fire with moves after matched random moments; it is a research measure on past data, read by wave, and it can be wrong. The cost tables
that ship inside `alarm/` were measured on the lab's own trading venue and size; your costs differ. Nothing here is financial advice.

## No alarms ship
The lab's found alarms, its registry of alarms, its scoreboard and its receipts are not in this repo (desk/build/EXCLUDES.tsv). The
example detectors inside `alarm/` are engine parts and test fixtures, not recommendations. A run starts with no alarm.

## What is proven, and how
| claim | proof | where |
|---|---|---|
| the 31 judge files listed in desk/build/JUDGE_PARITY.tsv are the released judge's bytes (decide_v5, decide_v6, audit_run_v5, true_gate_v3, true_gate_v4, menu_gate_v1, tried_search_v1, wave_gap_v1, labcore waves, gates and jobgate, law.py, and the .py files they load by name); runtime data files (e.g. true_gate's SOURCE_FAMILIES_V1.tsv) and modules chosen at run time (e.g. fl_read_v11.py, alarm_design_v3.py, queue_job_v16.py) are not yet in this comparison | byte compare with release ALARM_V1_22_1: identical, or identical after the scrub's text replacement, or that plus sha16 pins re-pointed to the scrubbed files (each pin checked against PIN_MAP.tsv) | desk/build/judge_parity_v1.py, desk/build/JUDGE_PARITY.tsv |
| no machine path, owner name, machine or host name, and no lab seat as a requirement, outside listed exceptions | path scan, with planted failures for each kind in desk/tests | desk/build/path_scan_v1.py, desk/PATH_ALLOW.tsv |
| the engine's tests pass from this folder with the lab's folders forbidden: 133 PASS, 19 KNOWN (each with its reason, apart), 0 FAIL of 152 (ALARM_V1_22_1, 9 Nov 2026) | `desk.py tests` (run_all_tests_v4) with the lab tree, the release, the data store and the GitHub folder forbidden (an open there fails the test), on the Mac | desk/build/KNOWN_TESTS.tsv |
| the learning loop's own suites pass from a copy of loop/ (13 of 16, 3 KNOWN with their reasons), a new alarm store checks clean, and the leak scan refuses without a pattern | desk/tests/test_loop_v1.py | loop/ |
| a COUNT runs end to end through desk.py in local mode, and gives the lab's numbers | one COUNT of a past lab definition on the lab's one-format data, read-only, Sep-Dec 2025: rows equal to the lab runner's COUNT of the same definition; no data file touched | STATUS.md step 1c |
| the plugin's skills and commands hold the steps above | read by fresh agents in the trials | plugin/, STATUS.md step 5 (pending) |

## What is not proven
- That the desk installs on another machine: every run so far was on the machine that built it (a stranger's install is untested).
- That the engine works on data from any other source: V2 ships no converter, only the steps your agent follows to convert your data (docs/CONVERT_YOUR_DATA_V2.md). No conversion made from those steps on a desk's own data has been tested yet.
- That any alarm made with the desk is true, new or useful: the grading and the truth gate are research tools with known weak points
  (alarm/cards/true_gate.md, alarm/cards/decide_v6.md).
- That GRADE, TRUE, ENTRY, MONTH and FIRSTLOOK jobs run end to end in local mode: until the trials of STATUS.md step 5 run, only COUNT was run.
- That a fresh agent can finish the loop from this folder with the plugin alone: the three trials of STATUS.md step 5 are pending.
- That the desk learns: V1 claims only that it starts with the lab's lessons and logs and learns from every try; whether an agent improves is the V2 test (30 tasks, held-out tasks, a placebo arm).
- That the reworded lessons are right in every line: the kit tables were reworded by machine and not reviewed by hand.
- Anything about months after 2025: no 2026 data was read while building this repo.
