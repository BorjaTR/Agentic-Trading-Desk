# 05 Profile: the move before the fire

For every fire of an alarm, using only what is known at the fire: where the price move really started, how far and how long it ran to
the fire, how much it gave back from its extreme, and (for the liquidation alarms) the liquidations around it, their speed and shape,
open interest, and 125 context values. The first look (part 06) reads it as item 1, "the move spent".

Only released editions are here (the owner, 30 Oct 2026, option a: "released editions only" in GitHub). Every file is a byte copy of
the team's dev tree (`SOURCES.tsv`: each file's dev path and sha16), never edited here.

## Layout
- One folder per tool at the top, with its README, SCOPE, ARCHITECTURE and CHANGELOG: [alarm_profile/](alarm_profile),
  [alarm_context/](alarm_context). A README there is a byte copy of the tool's own; SCOPE, ARCHITECTURE and CHANGELOG say on their
  first line when SCOUT wrote them for the repo (the dev tree has none for these two tools).
- `tree/`: the byte copies of every file the tools run, in the dev tree's layout under `team/RESEARCH` (`tree/tools/<tool>/`,
  `tree/QUANT/receipts/`), so the tools' relative paths (`../alarms`, `../alarm_context`) work unchanged.

## Tools
| tool | what it does | owner | edition here | status |
|---|---|---|---|---|
| [alarm_profile](alarm_profile) (`tree/tools/alarm_profile`) | edition 1: the episode at the liquidation alarms A02, A02_1, A02N (run start, run end, the 36 values in 8 blocks, proof cards); its README is the manual with every definition | QUANT | 1, release `RELEASE_profile_V1_8.json` | released; running; pinned by the outcome tool and the grade chain |
| [alarm_context](alarm_context) (`tree/tools/alarm_context`) | the 129 context values around an alarm (market, coin, liquidations, OI, funding ...); edition 1 of alarm_profile joins them | LEAD / LAYERS | 1, release `RELEASE_context_V1_7.json` | released |
| `tree/tools/alarms` | `a01_onset_v2.py`, `a02_climax_v3.py`, `alarm_view_v1.py`: the alarm definitions the episode code imports | SCOUT, QUANT | as pinned by the releases | copies (their own part is 01 Detection) |
| `tree/QUANT/receipts/COSTS_PER_COIN_V4.tsv` | the cost per coin, read by alarm_context | QUANT | V4 | copy |

What changed in each release: [CHANGELOG.md](CHANGELOG.md).

## In development (not here)
| tool | where (dev tree) | status |
|---|---|---|
| alarm_profile editions 2, 2.1, 2.2 (any alarm list, generic subjects) | `team/RESEARCH/tools/alarm_profile_v2/` | 2: failed review E; 2.1: withdrawn; 2.2: TEST, used by the first look: reviewer I PASS on its outputs (30 Oct), reviewer H pending |
| alarm_context editions 2 and 3 | `team/RESEARCH/tools/alarm_context/alarm_context_ed2.py`, `_ed3.py` | candidates |

## Run from this folder (Alarm/05_Profile)
No data is needed: the tests plant their own.
```
L=$(cd ../_vendor/LAB3_code && pwd)
python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_profile/test_alarm_profile.py $L          # 30 tests
python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_profile/test_epi_output_proofs.py         # 11 tests
python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_profile/test_proof_plan_v1.py
LAB3_CODE=$L python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_context/test_alarm_context.py       # 34 tests
LAB3_CODE=$L python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_context/test_ctx_output_proofs.py  # 12 tests
LAB3_CODE=$L python3 -B ../_tools/run_isolated_v1.py tree/tools/alarm_context/test_p09_v1.py             # 2 tests
```
Proof that they run from here and from a copy of the Alarm folder elsewhere: [RUN_PROOF.md](RUN_PROOF.md).

## Data and settings
A real build (edition 1, its README "Run") reads the lab days and writes the shared research store; it runs as a job on the Mac.
Settings keys it needs (`../settings/SETTINGS_<MACHINE>.env`): `LAB_DAYS`, `RESEARCH_STORE`, `HL_FILLS`, `PYTHON`.
Still built into the code (`MACHINE_PATHS.tsv`, status BUILT_IN): edition 1 writes to `<DATA_ROOT>/research_days`
(`tree/tools/alarm_profile/alarm_profile.py:27`) and reads Hyperliquid fills at `<SCRATCH>/work_SCOUT/hl_fills_npz_dev` (`:38`);
`tree/tools/alarm_context/alarm_context.py:8,29` names the same store. On another machine these need a new edition that reads them from the settings file.
The release files' Python path is a record of the run, not a path the code opens (status TEXT).
