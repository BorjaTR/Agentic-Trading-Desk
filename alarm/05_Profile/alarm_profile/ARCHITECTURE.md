Written by SCOUT for the repo on 30 Oct 2026 from tree/tools/alarm_profile/README.md, alarm_profile.py, episode_blocks.py and the
release files; not the owner's document (owner seat: QUANT).

# ARCHITECTURE: alarm_profile (edition 1, release V1_8)

## Inputs
| input | format | read by |
|---|---|---|
| the alarm list | TSV: coin, t (unix s), side (+1 pushed up, shorts forced; -1 pushed down), onset_t | `alarm_profile.py build` |
| lab days: A1.S01 / A1.S02 (5 s liquidation rows), E2.S02 / E2.S03 (Binance OI at minute ends), PRICE (3 s bins) | the lab's one format, read only through `lab3.days` (purpose research) | `episode_blocks.Ep` |
| Hyperliquid fills `HLF_<coin>_<day>.npz` | npz per coin and day (liquidation fills; the liquidated account's rows `lself = 1`) | the hyperliquid block |
| the settings | `EB.SETTINGS` plus subject, candidate, Hyperliquid folders: all of it is the seal | build |

## Steps
1. `episode_blocks.Ep` cuts every input at the alarm (5 s rows up to the alarm's row, price bins ending at or before it, OI minute
   ends at or before it, Hyperliquid fills at or before it, daily totals of whole days before the burst's day).
2. The blocks (functions in `episode_blocks.py`, each with docstring lines `column: meaning [unit]`) compute the 36 values.
3. Values are written with `lab3.write.write_part` as part `EPI.<SUBJECT>` (ROWS), codes `EPI.<SUBJECT>.<column>`; an unknown value
   has no bits and reason NOT_KNOWN. The index holds the seal and the sources' sha16s; the same inputs give `UP TO DATE`.
4. `profile` reads the stored values back by profile (`PROFILES_V1.tsv`); `status` gives each value's proof status.

## Outputs
The research store (settings key `RESEARCH_STORE`; built into `alarm_profile.py:27` today), part `EPI.A02` (and A02_1, A02N).

## Files (tree/tools/alarm_profile/)
| file | what |
|---|---|
| `alarm_profile.py` | the command: build, profile, status, catalog |
| `episode_blocks.py` | the cut at the alarm and the value blocks |
| `episode_twin.py` | the second computation the tests compare against |
| `EPI_CATALOG_V1.tsv`, `PROFILES_V1.tsv`, `CTX_INPUTS_V1.tsv` | the catalog (generated from the docstrings), the profiles, the context inputs it joins |
| `PROOFS_V1.tsv`, `PROOF_RESULTS_V1.tsv`, `EPI_OUTPUT_PROOFS_V1.tsv`, `proof_alarm_profile.py` | the proof cards, their results, the output proofs and the proof runs |
| `test_alarm_profile.py`, `test_epi_output_proofs.py`, `test_proof_plan_v1.py`, `mutants_alarm_profile.py` | tests and planted bugs |
| `draw_eye_run.py`, `eye_charts_v1.py`, `score_eye_run.py`, `profile_split.py` | eye checks and the profile split |
| `RELEASE_profile_V1*.json` | the 9 releases (each pins every file by sha16) |

It imports `../alarms/a01_onset_v2.py`, `../alarms/a02_climax_v3.py`, `../alarms/alarm_view_v1.py` and `../alarm_context` (copied
beside it under tree/tools/), and lab3 (the shared copy `Alarm/_vendor/LAB3_code`).

## Settings keys a real run needs
`LAB_DAYS`, `RESEARCH_STORE`, `HL_FILLS`, `PYTHON` (`../settings/SETTINGS_<MACHINE>.env`). Edition 1 still has the store and the
Hyperliquid folder built in (`MACHINE_PATHS.tsv` of the part): another machine needs a new edition that reads them from the settings.

## Tests
`test_alarm_profile.py` (30: known-at, the mirror, planted answers, holes, the second computation, catalog, profiles, proof cards,
determinism, memory, sealed days), `test_epi_output_proofs.py` (11), `test_proof_plan_v1.py`; planted bugs `mutants_alarm_profile.py`.
They need no data; the part's RUN_PROOF.md shows them run from the repo and from a copy.
