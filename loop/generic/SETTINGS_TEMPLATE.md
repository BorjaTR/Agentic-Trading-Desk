# SETTINGS TEMPLATE (generic; LEARNING_LOOP_V1_RC2; the one place every placeholder is defined)
A seat copies this page into its own folder as SETTINGS.md and fills the "your value" column once. Every `{NAME}` in the generic pages, prompts, skills and `registers_template/PARTS.tsv` means the value written here. The tools never read this page: they read the environment variables of the second table. Each variable has a default, which is the alarm seat's (SCOUT's) value of today, so the alarm seat runs unchanged; a new seat sets every variable it uses.

## Placeholders in pages
| placeholder | meaning | your value | alarm seat value today (example only) |
|---|---|---|---|
| `{SEAT}` | the seat's name | | SCOUT |
| `{SEAT_ROOT}` (pages also write `S`, prompts `{S}`) | the seat's own loop folder: runs, drills, series file live under it | | <LAB_REPO>/forensics/team/SCOUT/loop_day_20261105/learning_series |
| `{RUNF}` | one run's folder | | {SEAT_ROOT}/runs_v2/<run> |
| `{GENERIC}` | the installed `generic/` folder of this release (read only) | | this folder |
| `{PACK}` | the seat's pack folder; `{PACK}/<pack>.json` is its knowledge pack file | | packs/alarm (alarm.json) |
| `{STORE}` | the seat's own knowledge store folder (never another seat's); made with `build_knowledge_v2.py init --pack ... --dir {STORE}` | | {SEAT_ROOT}/knowledge_v1 (the alarm seat moves to v2 after L11) |
| `{REGISTERS}` | the seat's register folder; starts as a copy of `generic/registers_template/` | | {SEAT_ROOT}/drills_v2/registers |
| `{TMP}` | temp folder off the internal disk, for tests and scratch | | <SCRATCH_DISK>/tmp_SCOUT |
| `{SKILLS}` | where the role skills are installed (`cp -R generic/skills/<skill> {SKILLS}/`) | | ~/.claude/skills |

## Environment variables the tools read (default = the alarm seat's value)
| variable | read by | meaning (placeholder) |
|---|---|---|
| `LL_SEAT_ROOT` | tools/registers/reg.py, messy_triage_v1.py (`--series` default) | {SEAT_ROOT}; relative part files in PARTS.tsv resolve here |
| `LL_REGISTERS` | tools/registers/reg.py, messy_triage_v1.py (`--registers` default) | {REGISTERS} |
| `LL_SEAT_ROOT_NAME` | messy_triage_v1.py | the folder name of {SEAT_ROOT} stripped from quoted paths (default `learning_series`) |
| `LL_TRIAGE_MAP` | messy_triage_v1.py | a seat's own TSV (name, path) of file names to their live path; default: the alarm seat's map in the code |
| `LL_REPORT_TEMPLATE` | tools/drills/blind_kit_v1.py | the REPORT template a scorer follows; set it to {GENERIC}/REPORT_TEMPLATE_V1.md |
| `LEAK_SCAN_PATTERN_FILE` | tools/drills/leak_scan_v1.py (or `--pattern-file`) | the pack's held-out marker pattern; alarm pack: {PACK}/HELDOUT_PATTERN.txt; no default: the tool refuses without one |
| `LL_GENERIC`, `LL_PACK`, `LL_SKILLS`, `LL_SEAT`, `LL_STORE` | tools/registers/reg.py (C218) | {GENERIC}, {PACK}, {SKILLS}, {SEAT}, {STORE} inside a PARTS.tsv `files` cell: reg.py reads `{NAME}` as env `LL_<NAME>`; unset stays literal and counts as missing |
| `LL_TEST_TMP`, `KNOW_V2_TMP` | every test | {TMP}; set it before every test (a test given none writes to its old default folder) |
| `KNOW_V2_SERIES` | knowledge_v2 tests | alarm seat only: the folder holding knowledge_v1 and the live store (the 2 v1 equality tests skip without it) |
| `ALARM_SERIES_DIR`, `ALARM_SERIES_HEADER`, `ALARM_RUNS_DIR` | alarm pack tools (forecast_score.py, test_bar_check_v2.py, pool_splits_v1.py) | the alarm series folder, the SERIES_V2 header file, the runs folder |

## Rules
- One value per placeholder, written here once; never a second copy in another page.
- A path a tool needs is an argument or one of the variables above, never typed into the tool.
- Temp and test output only under {TMP}, never on the internal disk; clean your own temp after each run.
