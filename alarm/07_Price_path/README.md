# 07 Price path: the price after an alarm, read STRATEGY's way

After an alarm passes its grade, STRATEGY reads the price path of its fire list: how far the price moves after each fire before
cost, against calm moments of the same coin when nothing fired and against moments with the same move (the edge before cost), and
what entering a little later changes (the markout). The markout re-reads a store run of STRATEGY's grader, idea_to_grade: the
grader finds the calm and same-move moments, measures every fire and moment on one fixed grid, and grades them by month.

Only released editions are here (the owner, 30 Oct 2026, option a: "released editions only" in GitHub): the grader, edition V3.2.
The markout and the job tools that run it for one alarm are TEST editions; they stay in the dev tree (list below). Every file here
is a byte copy of the team's dev tree (`SOURCES.tsv`: each file's dev path and sha16), never edited here.

## Layout
| path | what |
|---|---|
| [idea_to_grade/](idea_to_grade) | the grader's documents at the top: README.md (V1 to V2.3.1), README_V3_2.md (the edition here), README_V3.md, INTERFACE_V1.md, ARCHITECTURE.md (byte copies); SCOPE.md and CHANGELOG.md (written for the repo: the dev tree has none) |
| `tree/` | every byte copy in the dev tree's layout: `tree/` stands for `team/RESEARCH`; files of `team/BED` and `team/OUTSIDE` are under `tree/_team/` |
| `MANIFEST.tsv`, `SOURCES.tsv` | what is copied from the dev tree, and each file's sha16 (`../_tools/sync_from_dev_v1.py`) |
| `MACHINE_PATHS.tsv` | every machine path in the copied files, and what a new edition must change |
| `RUN_PROOF.md` | the tests run from the repo and from a copy of the whole Alarm folder |
| `REMOVE.tsv` | files SCOUT deletes before the commit: TEST editions copied earlier, and old paths moved under `tree/` |

## Tools
| tool | what it does | owner | edition here | status |
|---|---|---|---|---|
| [idea_to_grade](idea_to_grade) (`tree/tools/idea_to_grade`) | grades an alarm's fires against matched calm moments and same-move (TOUGH) moments, by month, each event counted once, before cost and after an honest and a stress cost; its store run is what the markout reads | STRATEGY/LEAD (`idea_to_grade.py`); V3 to V3.2 built by the ALARMLIB seat | V3.2: `RELEASE_idea_to_grade_V3_2.json` (26 Oct 08:25Z); pins `I2G_PINS_V3_2.json` 8d46fbaa9b791f34 (46 files); `idea_to_grade_v3_2.py` 78512a2235c580fd | released; its 26 tests pass from here |
| the kernels it runs: `tree/tools/` alarm_match, alarm_stamp, entry_card, alarm_context, event_decisions, event_profile, alarm_design, alarms, model_v1, labcore; `tree/_team/` BED fill and ladder, OUTSIDE projections and comparisons | the matcher of calm moments, the 55 STAMP fields, the taker fill and first touches, the comparison kernels, detection | their own seats | as pinned by V3.2: the 35 files outside the grader's folder, 26 here and lab3's 9 in `../_vendor/LAB3_code` | copies |
| tables: `tree/QUANT/receipts/COSTS_PER_COIN_V1.tsv`, `tree/tools/freeze_judge/WINDOWS_V1.tsv`, `tree/_team/OUTSIDE/.../ROSTER_BUILD.json` | the cost per coin, the window table (BUILD months), the 52-coin roster | QUANT, the freeze judge, OUTSIDE | as read by V3.2 | copies |

What changed in each edition and why: [idea_to_grade/CHANGELOG.md](idea_to_grade/CHANGELOG.md). Every pinned file is here at its
pinned sha16 (46 of 46 checked on 30 Oct: 37 in this part, 9 in `../_vendor/LAB3_code`).

## In development (not here)
TEST or CANDIDATE editions: no release after reviews. Dev tree: `<LAB_REPO>/forensics/team/RESEARCH/`;
sha16 read on 30 Oct 2026; the status is the file's own words.
| tool | dev path and sha16 | status |
|---|---|---|
| markout v1 and v1.1 (STRATEGY): the edge before cost at later entries (waits 0 to 3600 s), against calm and same-move moments, per half; gates A, A2, B | `tools/markout/markout_v1_1.py` 3239e4685080894e, `markout_v1.py` 5cf136180e6feb90, `README.md` a8e7ee10fe5bef46 | TEST, NOT REVIEWED (README and docstrings); no RELEASE json, no BASELINE.tsv |
| grader speed twins S2, S3, S6: the store the price path job runs (PROCESS_V7 section 3) | `tools/idea_to_grade/idea_to_grade_v3_2_s6.py` 7f8d935faf1034f8; pins `I2G_PINS_V3_2_S6.json` 75aee82e3ab5f99d: 60 files, the same 35 outside files as V3.2 at the same sha16s plus 25 in `idea_to_grade/` and `i2g_v3_3/` | TEST (each file's docstring); no RELEASE json |
| grader V3.2.1: the NO_COST fix of RR net rows | `tools/idea_to_grade/i2g_grade3_v3_2_1.py` 0a0c22f6c073ecfb; `RELEASE_idea_to_grade_V3_2_1.json` 6d24c73c1ef55cad | CANDIDATE, builder side (its record; review round 1: fix right) |
| grader V3.3 and V3.4.0: one measurement, any grouping; vectors and grade | `tools/i2g_v3_3/i2g_v3_4_vectors.py` 68a2194e9c4f3da8, `i2g_v3_4_grade.py` 20765205cffb3ed8 | CANDIDATE records only (`tools/i2g_v3_3/RELEASE_idea_to_grade_V3_3*` and `V3_4_0*_CANDIDATE.json`) |
| the price path job for one alarm (SCOUT): filer, store script, reader | `ALARM_DESIGN/runs/CLAUDE1_20261028/tools/file_entry_job_v2.py` 12f508e3fc6e447f, `run_alarm_store_v10_3_noladder.sh` 45ac17404e5dc762, `read_stratentry_v1.py` efe30de7fdfd2c59 | TEST, NOT REVIEWED |
| its job template and preregistration | `ALARM_DESIGN/runs/CLAUDE1_20261028/ideas/STRATENTRY/job_twins/TEMPLATE_STRATENTRY_V3.job.sh.txt` fe0851a5040afa63, `ideas/STRATENTRY/PREREG_STRATENTRY_V1.md` de6b9079aa444fa7 | TEST, NOT REVIEWED |
| KIT_V5: the ENTRY job and the process (section 3: what STRATEGY receives) | `ALARM_DESIGN/KIT_V5/jobs/JOB_ENTRY_V5.job.sh.txt` 1cfc36246087008c, `ALARM_DESIGN/KIT_V5/PROCESS_V7.md` 0b368cabce30bbe5 | TEST, NOT REVIEWED (`KIT_V5/MANIFEST_SHA16.txt` 76b46b91edeffc3c); PROCESS_V7 PROPOSED |
| the run register writer (CLAUDE1) | `ALARM_DESIGN/runs/CLAUDE1_20261028/tools/reg_append_v1.py` c301c5977ecd6860 | TEST, NOT REVIEWED |

## Run from this folder
The tests of the edition here (26). They need no lab data, only the library registry, which is data (`RESEARCH_ROOT`):
```
cd Alarm/07_Price_path
S=../settings/SETTINGS_<MACHINE>.env
PY=$(python3 -B ../_tools/settings_v1.py get $S PYTHON)
FO=$(mktemp -d)/fo; L=$FO/team/RESEARCH/LIBRARY/alarm_library; mkdir -p $L
ln -s $PWD/tree/tools $FO/team/RESEARCH/tools; ln -s $PWD/tree/QUANT $FO/team/RESEARCH/QUANT
ln -s $PWD/tree/LIBRARY/alarm_library/alarm_core_v1_1.py $PWD/tree/LIBRARY/alarm_library/alarm_core_v1_2.py $L/
cp "$($PY -B ../_tools/settings_v1.py get $S RESEARCH_ROOT)/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv" $L/
I2G_FORENSICS=$FO $PY -B ../_tools/run_isolated_v1.py tree/tools/idea_to_grade/test_i2g_v3_2.py     # Ran 26 tests, OK; ISOLATION OK
```
Why the links: the test finds its kernels through the dev tree's layout (`I2G_FORENSICS/team/RESEARCH/tools`, `.../QUANT`,
`.../LIBRARY`); the links give it that layout with every file from `tree/`. Proof from here and from a copy: [RUN_PROOF.md](RUN_PROOF.md).

Not runnable from this folder, and why:
- A real grader run. The pins name all 46 files by absolute dev path and the run re-hashes them there, and 32 of the 35 kernel files
  are loaded through folders built from `<DEV>/...` (`MACHINE_PATHS.tsv`, the SUMMARY row of `I2G_PINS_V3_2.json`). On
  the Mac a run started here would load and check the dev tree's kernels; on another machine it is refused at the start. A new
  edition must load them from `tree/`.
- `mutants_i2g_v3_2.py`: it fixes the forensics root at 4 folders above its own real path; from `tree/` that is the Alarm folder,
  so every mutant would fail at import: a KILLED that proves nothing. Its release record also notes that test_20 errors inside the
  mutant temp folder (`RELEASE_idea_to_grade_V3_2.json`, tests.mutants). It runs only in the dev tree.
- `test_i2g_v3_2_real.py`, `regress_v3_2_ext.py`, `full_population_v3_2.sh`: real data (lab days, a detector fixture on the scratch
  disk, two complete stored runs) and Mac paths written in the files. The shell file is only checked to parse.

A real run, for reference (`README_V3_2.md`): `nice -n 10 $PY -B tree/tools/idea_to_grade/idea_to_grade_v3_2.py --events <list>
--events-sha16 <sha> --roster <ROSTER_BUILD.json> --first D1 --last D2 --research-window FIRST:LAST --out <new folder> --delay-s <s>
--ledger-ask <PREREG id> --alarm-id <registry id> --universe <U.tsv>`.

## Data and settings
One settings file per machine, `../settings/SETTINGS_<MACHINE>.env`; read a key with
`python3 -B ../_tools/settings_v1.py get ../settings/SETTINGS_<MACHINE>.env KEY`.
- The tests: `PYTHON`, `RESEARCH_ROOT` (`LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv`).
- A real run: `PYTHON`; `LAB_DAYS` (`--lab-root`); `RESEARCH_ROOT` (`--universe LIBRARY/UNIVERSE_ALARMS_V1.tsv`, `--registry
  LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv`, `--ledger TRIES_LEDGER_V1.tsv`; the feed gate `../FEED/stops/BACKFILL_GATE.txt`);
  `SCRATCH` (the `--out` folder).
- Still built in (`MACHINE_PATHS.tsv`, status BUILT_IN, 109 rows): the dev root in `i2g_engine.py`, `i2g_grade.py` and
  `idea_to_grade.py` and the 46 absolute paths of `I2G_PINS_V3_2.json`; the feed gate (`idea_to_grade.py` line 30); in
  `full_population_v3_2.sh` the interpreter, the dev root, the roster, the universe, the scratch folder and macOS `/usr/bin/time -l`;
  in `test_i2g_v3_2_real.py` the interpreter, lab days, library, two scratch folders, an idea definition, the roster and the cost
  table; relative lookups that leave `tree/` (lab3 for `detect.py`, `alarm_design_v2.py`, `run_manifest_candidate.py` and
  `labcore/gates.py`; tables of other tools for `event_profile.py`, `labcore/briefs.py`, `alarm_context.py` and
  `clock_series.py`): each row says where the file is in Alarm.
