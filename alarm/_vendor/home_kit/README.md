# home_kit V1.3 (STRATEGY, 30-31 Oct 2026; TEST; V1.3 reviewed)

**Agents: read `TOOL_CARD.md` first** (then `TOOL.json` for exact commands and `DATA_DICTIONARY.tsv` for every output field); the Strategy start page is `AGENTS.md` one folder up (GitHub `Trading/Strategy/AGENTS.md`).

The three small scripts that make a tool home self-contained, traceable and portable, in ONE source place. Every tool home holds exact
copies of them (vendored like any other copy, listed in its VENDOR.tsv). Change them here only, then vendor again into each home.

Owner the owner, 30 Oct 2026: "Everything that is needed to execute should be copied in the home folder of the tool"; "every tool should be
able to be executed only from its home folder"; "if now I clone the repository in another machine, that machine should be able to
execute everything as well with a settings file". The rules are skill research-tool-design, section H (the list of its rules lives
in the skill only).

| file | copy in a tool home | what it does |
|---|---|---|
| `home_v1.py` | `bin/home_v1.py` | `vendor <dev root> [--update]`: copies every VENDOR_PLAN.tsv row from the dev tree, applies PATCHES_V1.json (a machine path -> a setting; each `old` text found exactly once), writes VENDOR.tsv (dev sha16, home sha16, bytes, change); a file it replaces is kept first in the home's hidden `.twins/` folder. `check [<dev root>]`: every copy and every RELEASE file still has its sha16 (HOME_CHANGED fails), dev sources changed since the copy are DEV_DRIFT. `release <NAME>`: RELEASE_<NAME>.json, every file of the home with its sha16. `publish <dest>`: copies exactly the release's files to the GitHub repo folder, checks each sha16, never overwrites. |
| `path_scan_v1.py` | `bin/path_scan_v1.py` | no machine path (/Users/ /Volumes/ /home/ /private/ /mnt/ C:\) in any code or table file of the home unless PATH_ALLOW.tsv names the file, the text and the reason. settings/, *.md and the copy records are left out by design. |
| `isolation/sitecustomize.py` | `bin/isolation/sitecustomize.py` | the isolation proof: with bin/isolation first on PYTHONPATH and CTXG_ISOLATE=1, every Python process of a run (workers included) logs each file it opens under CTXG_FORBID (the dev tree) outside CTXG_ALLOW (the home, the interpreter, the settings' files). Empty log = ISOLATION OK. |
| `python_env_v1.py` | `bin/python_env_v1.py` | V1.2: checks that the Python running it is the tools' Python (REQUIREMENTS_PY311.txt: 3.11, every pin, no other package, outside FORBID). |
| `setup_python_v1.sh` | `bin/setup_python_v1.sh` | V1.2: makes that Python on a machine once (Python 3.11 found or downloaded; the pins from PyPI by sha256); prints PYTHON= for the settings. |
| `REQUIREMENTS_PY311.txt` | `bin/REQUIREMENTS_PY311.txt` | V1.2: the 12 pinned packages with their wheel sha256. |
| `test_home_kit_v1.py` | `tests/test_home_kit_v1.py` | 81 hand-answer checks on planted files (copy, check, release, publish, install, current, github, path scan and its settings rule, .serena/ left out (V1.3), isolation (V1.3.3: hook V1.2, M3 and M5), the Python env check, the setup's refusals); runs from here or from a tool home, by the tools' Python. |

How a tool uses it
1. Add four rows to the tool's VENDOR_PLAN.tsv (role "home kit"):
   `bin/home_v1.py  team/RESEARCH/tools/home_kit/home_v1.py`, `bin/path_scan_v1.py  team/RESEARCH/tools/home_kit/path_scan_v1.py`,
   `bin/isolation/sitecustomize.py  team/RESEARCH/tools/home_kit/isolation/sitecustomize.py`,
   `tests/test_home_kit_v1.py  team/RESEARCH/tools/home_kit/test_home_kit_v1.py`.
2. The first time, copy `home_v1.py` into the new home's bin/ by hand, then run `python3 -B bin/home_v1.py vendor <dev root>`
   (it then copies itself exactly and records it).
3. The tool's entry script runs `bin/home_v1.py check` and `bin/path_scan_v1.py` in its `check` and `units`, `tests/test_home_kit_v1.py`
   in `units`, and turns isolation on for every run (see context_tool/context.sh `iso_on`, `iso_result`).

Tests: `python3 -B team/RESEARCH/tools/home_kit/test_home_kit_v1.py <new scratch dir>` (exit 0 = PASS).
Users: context_tool V1.0, group_and_grade_tool V1.0, ctx_grade V2.0 (team/RESEARCH/tools/). First built inside ctx_grade V1.0 (30 Oct),
proven there by job 288 (check, units, isolation OK on every run); the environment names CTXG_* come from that first home.

## The release procedure (research-tool-design H20-H21; the owner 30 Oct 14:01)

Every change to a tool, the same 7 steps. `K` = the kit's source `team/RESEARCH/tools/home_kit/home_v1.py`, `H` = the tool's dev home,
`A` = `~/volat_release/<area>` (Strategy, Alarm, Live, ...), `R` = `~/Documents/GitHub/Trading/<area>`, `X` = an archive folder on SCRATCH_DISK.

| step | what | command |
|---|---|---|
| 1 | change the dev home (or the source tool, then `vendor --update`); quick tests in the VM | the tool's tests |
| 2 | new edition: version up, CHANGELOG line, release | `python3 -B $K --home $H release <TOOL>_V<x>_<y>` |
| 3 | install the edition into its own read-only folder `A/<tool>/<RELEASE>/` (the old edition stays) | `python3 -B $K --home $H install $A` |
| 4 | test from the install: check, units, one real run; the dev tree and the repo forbidden (FORBID) | a runner job running the installed `<RELEASE>/<tool>.sh` |
| 5 | passed: `current` -> the new edition (rollback: point it back) | `python3 -B $K --home $H current $A` |
| 6 | RUN_PROOF.md and BASELINE.tsv on the home's top; the repo gets the current edition only (the old one moves whole to X) | `python3 -B $K --home $H github $R $X` |
| 7 | the owner commits the repo | (the owner) |

Steps 3-6 write outside the agents' VM (volat_release is not linked), so they run as one runner job, which stops before step 5 when a test
fails (current and the repo stay on the old edition). A chain (ctx_grade) that pins a changed tool gets its own new edition with the new pins.
