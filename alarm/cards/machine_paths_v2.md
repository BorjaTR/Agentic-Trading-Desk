# machine_paths_v2: tool card

The STATIC proof of a clean part: no machine path written into its code. The code: [machine_paths_v2.py](../_tools/machine_paths_v2.py). Exact commands: [TOOL.json](machine_paths_v2.TOOL.json). Every output column: [dictionary](../dictionaries/machine_paths_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Scans a part of the Alarm folder (the files its MANIFEST.tsv lists, or every file with `--all`) for machine paths: strings that name one machine's folders (the Mac's home and volume folders, a VM's mount and session folders, `~/`, `$HOME`).
- Gives each hit a kind:
  - CODE: in Python code or a string (not a docstring or comment), a shell line that is not a comment, any line of a job template, any JSON value;
  - TEXT: a docstring or comment, a document or table (.md, .tsv, .txt, ...), a release record;
  - MARKED: a Python line whose own comment says `machine-path-ok:` with a reason (test data, the scanner's own pattern);
  - KNOWN: a CODE row listed in the part's MACHINE_PATHS_KNOWN.tsv while the file's sha16 is still the one listed.
- Past editions live in archive/ folders (read only, never run, never called), so three more kinds:
  - CALLS_ARCHIVE: a current file whose code names a file of an archive/ folder (or imports its module), unless a current file has the same name: it fails the part, like CODE;
  - NAMES_ARCHIVE: the same in a test (a tests/ folder, or test_*, mutants_*, edges_*): listed, does not fail; an import of an archived module is CALLS_ARCHIVE even in a test;
  - ARCHIVE: a machine path in a file inside an archive/ folder: counted, not listed, never CODE.
- The verdict: CLEAN (no CODE and no KNOWN row), CLEAN EXCEPT KNOWN (only KNOWN rows left), NOT CLEAN (a CODE or CALLS_ARCHIVE row).

## When to use it
- Not a loop step: a release proof (CLEAN_RELEASE_V1 section 1, STATIC). Run it on every part before a release, and on any new tool file.
- It answers: does this part still have a machine path written into its code?

## Run it
```
python3 -B <INSTALL>/_tools/machine_paths_v2.py <INSTALL>/Agentic
```
- `--all`: every file under the folder instead of the MANIFEST. `--tsv OUT`: also write every row to the new file OUT.
- It takes no settings file: it reads only the part named.

## What it gives
- Printed: one line per CODE, CALLS_ARCHIVE, MARKED or NAMES_ARCHIVE row (`<kind> <file>:<line> <path>`), per KNOWN row (with its reason), per STALE row of MACHINE_PATHS_KNOWN.tsv (a row that matches nothing), then `<part>: <n> files, CODE <n>, CALLS_ARCHIVE <n>, KNOWN <n>, MARKED <n>, NAMES_ARCHIVE <n>, ARCHIVE <n>, TEXT <n> -> <verdict>`.
- `--tsv OUT`: every row (file, line, path, kind). Every field: the dictionary.

## Limits and refusals
- exit 0: no CODE and no CALLS_ARCHIVE row (CLEAN, or CLEAN EXCEPT KNOWN).
- exit 1: CODE or CALLS_ARCHIVE rows found (listed): NOT CLEAN.
- exit 2: refused: no part named (it prints its usage), no MANIFEST.tsv without `--all`, the `--tsv` file exists, a listed file missing, a MACHINE_PATHS_KNOWN.tsv row with an empty column or a line that is no number.
- Reads files only; writes nothing but the `--tsv` file.

## Where its data comes from
- The part folder named on the command line: its MANIFEST.tsv and MACHINE_PATHS_KNOWN.tsv (columns file, line, path, sha16, reason).
- No settings key.
