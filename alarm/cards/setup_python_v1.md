# setup_python_v1: tool card

The Python setup step of a machine: it checks the python3 on PATH and the packages the release needs, and makes a Python for this machine when there is no good one (the pinned CPython 3.11.18, its sha256 checked). The code: [setup_python_v1.sh](../_tools/setup_python_v1.sh) (bash; no Python needed to run it). Settings keys: [settings/README.md](../settings/README.md) (this tool prints the PYTHON line). DRAFT by SCOUT's K14 (31 Oct 2026) for cards/setup_python_v1.md; SCOUT applies it.

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current); on a new machine, the cloned Alarm folder. Status in the code: TEST, NOT REVIEWED.

## What it does
- `--check`: asks the python3 on PATH (or the one `--python` names) for its version (at least 3.10; the team runs 3.11) and, for each line of `settings/PYTHON_PACKAGES.txt`, whether the package imports and at which version: `name==version` must be that version, `name>=version` at least it (versions compare as numbers: 1.15.10 is newer than 1.15.3). Comments and blank lines are skipped. The probes run from `/`, so a module in the current folder cannot stand in for a package.
- `--install <folder>`: makes a Python for this machine in <folder>, outside the release. A python3 3.10 or 3.11 on PATH is used as it is; otherwise the pinned build for this machine is downloaded, its sha256 checked against the table in the script, and unpacked. Then a venv, `pip install -r settings/PYTHON_PACKAGES.txt` in it, and `--check` with the venv's python.
- `--dry` (with `--install`): prints the URL, the sha256 and every step; changes nothing.
- It never deletes or overwrites anything.

## When to use it
- On a new machine, first (settings/README.md, "Setup: Python").
- When a run fails on an import, or after PYTHON_PACKAGES.txt changes: `--check --python <the PYTHON of the settings file>`.
- Not a loop step and not a job: run by hand, once per machine.

## Run it
```
bash <INSTALL>/_tools/setup_python_v1.sh --check
bash <INSTALL>/_tools/setup_python_v1.sh --check --python <PYTHON>
bash <INSTALL>/_tools/setup_python_v1.sh --install ~/venvs/alarm_py --dry
bash <INSTALL>/_tools/setup_python_v1.sh --install ~/venvs/alarm_py
```
- `--python <path>`: the python3 to check instead of the one on PATH (a path, or a command name on PATH). Only with `--check`.
- `<folder>`: new, or an empty folder, outside the Alarm folder; a relative path is read from the current folder and printed absolute.

## What it gives
- `--check`: one line per item, `<status> <item> <what was found>`. OK; MISSING (no python3, or a package that does not import); WRONG (a python3 older than 3.10 or whose version probe failed; a package at a version that does not hold, or whose version is not known); UNCHECKED (no good python3 to ask). Then `CHECK OK: python3 <version> (<path>) and the <n> packages of <file>`, or `CHECK FAILED: <k> of <n> items not OK: <items> (<file>)`.
- `--install`: the lines `INSTALL`, `PYTHON3`, `PLATFORM`, `URL`, `SHA256`, one `STEP` line per step and a `DONE` line as each ends, pip's own output, the check's lines, and last `PYTHON=<folder>/venv/bin/python3`: copy that line into `settings/SETTINGS_<MACHINE>.env`.
- `--dry`: the same up to the `STEP` lines, between `DRY RUN: nothing is changed` and `DRY RUN: nothing was changed`; no `PYTHON=` line.
- In <folder>: `download/<the pinned tarball>` and `python/` (only when it downloaded), and `venv/`.

## Limits and refusals
- exit 0: all OK (`--check`); done, the `PYTHON=` line printed (`--install`); the plan can run (`--dry`).
- exit 1: something missing or wrong (`--check`, each named). For `--install`, a step failed (`FAILED <step>: <why>`, then `INSTALL FAILED`): no pinned build for this machine and no python3 3.10 or 3.11 on PATH; neither curl nor wget; the download; a sha256 that is not the table's (the file is kept, nothing is unpacked); the unpack; the venv; pip; the new venv's check. What was made stays: run again with a new folder.
- exit 2: `USAGE` (no or unknown arguments, `--dry` without `--install`, `--python` with `--install`), or `REFUSED`: a <folder> inside the Alarm folder (links and `..` are resolved first), a <folder> that exists and is not an empty folder (dot files count), a path that is not a folder, no packages file, or a packages line that is not `name==version` or `name>=version` (`~=`, `<`, extras, markers and URLs are refused).
- Pinned builds: aarch64-apple-darwin, x86_64-apple-darwin, x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu (glibc). Any other machine (Alpine's musl, FreeBSD, Windows): install Python 3.11 yourself, then `--check`.
- A python3 3.12 or newer on PATH passes `--check` when its packages hold, but `--install` does not build on it: it takes 3.10 or 3.11 only, the versions the release is tested on, and downloads the pinned 3.11.18 otherwise.
- A venv cannot be moved: make a new one. pip needs PyPI; the download needs GitHub.

## Where its data comes from
- `settings/PYTHON_PACKAGES.txt` of the same Alarm folder (the package lines).
- The pinned table in the script: python-build-standalone release 20261026 (CPython 3.11.18), read from https://github.com/astral-sh/python-build-standalone/releases/tag/20261026 and its SHA256SUMS file.
- No settings file is read (it prints the PYTHON line that goes into one), and no data.
