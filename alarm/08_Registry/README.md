# 08 Registry: every alarm already found or tried

This part keeps one table of every alarm the team has found or tried, the registry: one row per alarm with its state (PASS, NEEDS
MORE MONTHS, STOP ...), its novelty verdict (NEW, COPY ...), its numbers (the LEAD and its t at 15 min and 1 h, months, CLEAR, money
after cost), how it was found and the files behind each number; one page per alarm; the scoreboard (which kinds of idea pass); and the
index (one line per alarm). Agents read it before they claim an idea, the novelty check says whether a new PASS is a copy of a known
alarm, and the lead rebuilds it after each round.

The tools are under `tree/ALARM_DESIGN/REGISTRY/`: `tools/registry_build_v2.py`, `tools/novelty_v2.py`, `tools/novelty_v3.py`, `tools/scoreboard_v2.py`, `tools/inputs_read_v1.py`, `index_v2.py`, each with a card in ../cards. Status in their code: TEST, NOT REVIEWED; they have no tool folder of their own here.

## Tools
See above and ../AGENTS.md (step 9 and the tools table). Their earlier editions: next section.

## Earlier editions in the dev tree
State on 30 Oct 2026, kept as history; the editions in use now are in ../AGENTS.md. In <RELEASE_ROOT> means released: what follows says what each piece is and what is unproven.
Dev tree: `<LAB_REPO>/forensics/team/RESEARCH/ALARM_DESIGN/`; sha16 read on 30 Oct 2026; the
status is each file's own words. None has a RELEASE json, a BASELINE.tsv row or a pin in a kit manifest (`KIT_V6/MANIFEST_SHA16.txt`
2624703457fbcec8 lists no registry tool and says TEST, NOT REVIEWED).
| tool | what it does | dev path and sha16 | owner | status |
|---|---|---|---|---|
| registry builder | builds `ALARM_REGISTRY_V<n>.tsv` and `alarms/<ID>.md` from the runs' files only; the same files give the same bytes | `REGISTRY/tools/registry_build_v1.py` a72fa17b037c1b8a; tests `REGISTRY/tests/test_registry_novelty_v1.py` d0ae133feaf86c81 (planted tests, then 18 mutants that must all be killed) | SCOUT (KIT_V6) | TEST, NOT REVIEWED |
| novelty check | one fire list against every registry alarm before it: COPY, NEW SIDE, MIRROR (50 pct or more of its fires), NEAR (40 to under 50), NEW (every overlap under 40), UNKNOWN | `REGISTRY/tools/novelty_v1.py` ed8cc2298b6f8b62 (the builder imports it) | SCOUT (KIT_V6) | TEST, NOT REVIEWED |
| scoreboard | which kinds of idea pass, per family: four lists that never overlap; new PASS and FOUND counts | `REGISTRY/tools/scoreboard_v1.py` 57636274dab38760; test `REGISTRY/tests/test_scoreboard_v1.py` 5dd112134c727927 | SCOUT (KIT_V6) | TEST, NOT REVIEWED |
| index maker | writes `REGISTRY/ALARM_REGISTRY_V1_INDEX.md`, one line per alarm | `index_v1.py`: copied on 30 Oct from SCOUT's VM work folder into the dev tree (`team/RESEARCH/ALARM_DESIGN/REGISTRY/index_v1.py`); TEST, so not here | SCOUT | TEST, NOT REVIEWED |
| the registry manual | files, kinds (the row order), novelty verdicts, how agents use it, known limits | `REGISTRY/README.md` 1650b02ff7ab6701 | SCOUT | TEST, NOT REVIEWED |
| the kit it belongs to | the process (states: section 1; the registry at steps 1 and 7), the kit rules behind every registry change | `KIT_V6/PROCESS_V8.md` 887dd197b03d83ca, `KIT_V6/README.md` 7b8eb1ab9a05a34d, `KIT_V6/LEARNINGS_V6.tsv` f8b361f28a996101 | SCOUT | KIT_V6: TEST, NOT REVIEWED; PROCESS_V8 PROPOSED |

What defines the registry (all in the dev tree, read 30 Oct 2026):
- The 55 columns: `registry_build_v1.py` line 35 (`COLS`): alarm_id, kind, seat, run, idea, V, state, lean, side, parent, one_line,
  the novelty verdict and its nearest alarm, r1, r2, LEAD and t at 15 m and 1 h, waves, months, clear, price gate, tough, money,
  forward months, clocks, the card, prereg, findings and job files, the fire list and its sha16, do_not, page.
- The kinds, in row order (the "before" of the novelty check): DESK_TRIGGER, QUICK_LOOK, KNOWN, SYNTHETIC, REFERENCE, PLANTED,
  PLANTED_VARIANT, OWN (`REGISTRY/README.md`, "Kinds").
- The states: `KIT_V6/PROCESS_V8.md` section 1: PASS (hand-off R2), NEEDS MORE MONTHS (R1 only), STOP (R1 missed), INSUFFICIENT,
  INVALID; FORWARD PASS (`KIT_V6/README.md`, round 5); FOUND = a new PASS, or a new R1-only alarm, whose Jan-Apr months hold in 3 or
  more of 4 (`KIT_V6/LEARNINGS_V6.tsv` V6-53, V6-62).
- The novelty line: under 40 pct overlap counts as new (the owner 30 Oct 06:20 Berlin; `LEARNINGS_V6.tsv` V6-61).

## Run from this folder
The commands are in each tool's card in ../cards.

## Data and settings
Data, never copied (under `RESEARCH_ROOT`, `ALARM_DESIGN/REGISTRY/`; sha16 on 30 Oct 2026): `ALARM_REGISTRY_V1.tsv` b383f6107dc9e32b
(174 rows, 55 columns), `alarms/<ID>.md` (174 pages), `SCOREBOARD.md` 8448513fa1a9918b, `ALARM_REGISTRY_V1_INDEX.md`
ebc0a9d74e6c8ddb, `FAMILY_TAGS_V1.tsv` 5f63362dfa9892c6, `fire_lists/` (12 fire lists copied from the scratch disk).
A run needs `PYTHON` and `RESEARCH_ROOT` (`../settings/SETTINGS_<MACHINE>.env`): the builder's `--h` is
`RESEARCH_ROOT/ALARM_DESIGN`, its `--f` the folder two above `RESEARCH_ROOT`; the novelty check takes `--h` and `--registry`; the
scoreboard runs from the `ALARM_DESIGN` folder or takes `--registry`, `--tags`, `--out`.
Built into the TEST builder on 30 Oct 2026 (it would be a BUILT_IN row of `MACHINE_PATHS.tsv`): `registry_build_v1.py` lines 235-236 read a
known alarm's fire list only when its path starts with the Mac prefix
`<LAB_REPO>/forensics/team/RESEARCH/ALARM_DESIGN/` (the same file named another way is not
recognised); line 237 names `<SCRATCH_DISK>/` (a list there is never read: its copy in `fire_lists/` with the same sha16 is used).
