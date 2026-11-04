# settings: where the data lives on each machine

the owner, 30 Oct 2026 (10:46-10:48 Berlin): "if now I clone the repository in another machine. That machine should be able to execute
everything as well with a settings file" ... "The alarm folder is one package on its own ... outside the alarm folder only data should
be outside ... and the settings folder would set where the data is".

So every tool, table, template and document the alarm pipeline needs is inside `Alarm/`; only data (lab days, the research data,
scratch, the job runner) is outside, and one settings file per machine says where it is. The format is the team's tool protocol
V4.12 (rule H4), the same as `tools/ctx_grade`: `KEY=VALUE` lines, read as text, unknown keys refused.

| file | what |
|---|---|
| `SETTINGS_EXAMPLE.env` | every key, documented, with placeholder paths |
| `SETTINGS_LOCAL.env` | the owner's Mac |
| `PYTHON_PACKAGES.txt` | the Python packages the tools import, pinned |

## Setup: Python
the owner, 30 Oct 2026 (23:49-23:57 Berlin): "Python itself is a machine install, not bundled: a setup step checks it is installed on the
path and downloads it if it isn't". The step is `_tools/setup_python_v1.sh`: bash only (macOS's bash 3.2 or newer), no Python needed to
run it. It never deletes anything.
```
cd Alarm
bash _tools/setup_python_v1.sh --check                      # python3 on PATH: 3.10 or newer, with every line of PYTHON_PACKAGES.txt
bash _tools/setup_python_v1.sh --install <folder> --dry     # when not OK: what it would do (the pinned build's URL and sha256, the steps)
bash _tools/setup_python_v1.sh --install <folder>           # makes <folder>/venv; its last line: PYTHON=<folder>/venv/bin/python3
```
Put that `PYTHON=` line in `settings/SETTINGS_<MACHINE>.env`. Later, `bash _tools/setup_python_v1.sh --check --python <that python>`
says whether it is still good (after a change of PYTHON_PACKAGES.txt, for example).
- `--check`: one line per item (OK, MISSING, WRONG; UNCHECKED when there is no good python3 to ask), then `CHECK OK` or `CHECK FAILED`
  naming each item not OK. A package line is `name==version` (exact) or `name>=version` (a minimum); versions compare as numbers
  (1.15.10 is newer than 1.15.3). Exit 0 all OK, 1 not, 2 usage or a packages line it cannot read.
- `--install <folder>`: a new or empty folder outside the Alarm folder (else REFUSED, exit 2). A python3 3.10 or 3.11 on PATH is used as
  it is; otherwise the pinned CPython 3.11.18 for this machine is downloaded into `<folder>/download/`, its sha256 checked against the
  table in the script, and unpacked into `<folder>/python`. Then `<folder>/venv`, `pip install -r settings/PYTHON_PACKAGES.txt` in it
  (it needs the internet: GitHub for the build, PyPI for the packages), and `--check` with the venv's python. A failed step exits 1 and
  leaves what it made: run again with a new folder. A venv cannot be moved: make a new one.
- The pinned builds (python-build-standalone release 20261026, "install_only"; the release page and its SHA256SUMS are named in the
  script): Apple silicon Mac (aarch64-apple-darwin), Intel Mac (x86_64-apple-darwin), Linux with glibc on x86-64 or ARM64
  (x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu). Any other machine: install Python 3.11 yourself, then `--check`.
- Tests: `_tools/tests/test_setup_python_v1.py` (35, no network); planted bugs: `_tools/tests/mutants_setup_python_v1.py` (33 of 33 killed).

## A new machine
```
cd Alarm
bash _tools/setup_python_v1.sh --check                               # not OK: --install <folder> ("Setup: Python" above)
cp settings/SETTINGS_EXAMPLE.env settings/SETTINGS_<MACHINE>.env     # then set this machine's paths (empty = not on this machine) and PYTHON
python3 -B _tools/settings_v1.py check settings/SETTINGS_<MACHINE>.env    # python3: the PYTHON of that file
python3 -B _tools/tests/test_settings_v1.py                          # the reader's own tests
```
Each part's RUN_PROOF.md lists its tests: they need no data. A real run needs only the keys its part's README names
("Data and settings"); `check <file> LAB_DAYS,RESEARCH_ROOT` checks just those.

## The keys
| key | what | owner's Mac |
|---|---|---|
| PYTHON | the interpreter for real runs | <PYTHON> |
| LAB_DAYS | the lab days: LAB1's lab3 store (bars, prints, liquidations, OI per coin and day) | <DATA_ROOT>/lab_days |
| RESEARCH_STORE | QUANT's shared research store (alarm_profile edition 1 writes A02 there; editions 2+ refuse it) | <DATA_ROOT>/research_days |
| HL_FILLS | Hyperliquid fills, read by alarm_profile's hyperliquid block (A02 only) | <SCRATCH>/work_SCOUT/hl_fills_npz_dev |
| SCRATCH | the big scratch disk: build out roots, outcome tables before extract | <SCRATCH> |
| RESEARCH_ROOT | the research data, in the team's layout: ALARM_DESIGN (definitions, cards, registry, runs and their PERFIRE files), tools/&lt;tool&gt;/inputs, receipts, results | <LAB_REPO>/forensics/team/RESEARCH |
| BOARD | the team board folder (hb, one board file per seat): the kit's board_line and audit write and read it | <LAB_REPO>/forensics/hb |
| RUNNER_QUEUES | the job runner (Q_V1..Q_V21, IN and RUN); empty = no queueing | <RUNNER_TREE>/forensics/orch1_20260817/runner |
| RUNNER_ALLOC | the job runner's job number allocator (job_alloc.py: it keeps its claims beside the runner, so it is run where it is); empty = no queueing | <RUNNER_TREE>/forensics/tools/job_alloc.py |
| RUNNER_RELEASE | the Alarm release folder the job runner runs jobs from, as a path on the runner's machine (a queued job's @@ALARM@@); empty = the Alarm folder the queue runs from. Set only on a machine that queues for another (a VM: <RELEASE_ROOT>/Alarm/alarm/current) | empty (the Mac queues from the install itself; a path into the install would be refused: DATA INSIDE ALARM) |
| FEED_GATE | the live feed's batch gate file (first line RUN or PAUSE): detect waits while it reads PAUSE; empty = no feed here, no gate | <LAB_REPO>/forensics/team/FEED/stops/BACKFILL_GATE.txt |
| FORBID | the code folder no run may read (the team's dev tree): runs prove isolation; empty = not checked | <DEV> |

SCOUT's Linux VM sees the Mac's folders under `~/mnt/...`, so it keeps its own file (the same keys, the VM's paths) outside the repo.
FEED_GATE was added on 30 Oct 2026 (late) for detect's gate, which was a path written into labcore.jobgate. BOARD and RUNNER_ALLOC were added on 30 Oct 2026 for the kit's queue (CLEAN_RELEASE_V1 section 3), and RUNNER_RELEASE the same evening
(the queue fills a job with the runner machine's paths: queue_job_v5.py --job-settings): a settings file without them is refused
(KEYS MISSING), so every machine's file needs the three lines.

## The reader: `_tools/settings_v1.py`
- `get <file> KEY` prints a value (an empty key is refused); `check <file> [KEY,...]` says OK, MISSING or EMPTY per key (exit 0;
  3 when one is not OK; 2 when refused).
- Refused (exit 2): no settings file, a line that is not KEY=VALUE, a key missing, an unknown key, a key twice, a value that is not an
  absolute path (quotes, spaces, `~`, `$variables`), and any path inside the Alarm folder (code lives inside, data outside).
- Tests: `_tools/tests/test_settings_v1.py` (23); planted bugs: `_tools/tests/mutants_settings_v1.py` (17 of 17 killed).
