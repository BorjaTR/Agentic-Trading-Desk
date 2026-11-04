# run_isolated_v1: tool card

The isolation check every test of the package runs through (run_all_tests_v1.py uses it, so it stays current). The code: [run_isolated_v1.py](../_tools/run_isolated_v1.py). Exact commands: [TOOL.json](run_isolated_v1.TOOL.json). Every output column: [dictionary](../dictionaries/run_isolated_v1_COLUMNS.tsv). Its newer sibling for real runs: [run_isolated_v2](run_isolated_v2.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Runs one script of this Alarm folder (a test or a tool) as `__main__`, with its own arguments, and proves at the end:
  1. every Python module it imported came from this Alarm folder or from the interpreter (its standard library and installed packages);
  2. it opened no file under a forbidden folder (the interpreter's own files do not count).
- Unlike run_isolated_v2 it reads no settings file and allows no data under the forbidden folder: right for tests (they plant their own data), not for a real run on the Mac, whose research data sits in the dev tree.

## When to use it
- Not a loop step: run_all_tests_v1.py runs every test of _tools/TESTS.tsv through it, with the settings' FORBID as `--forbid`.
- It answers: did this test run touch the dev tree or import code from outside the release?
- For a real run on real data, use [run_isolated_v2](run_isolated_v2.md).

## Run it
```
python3 -B <INSTALL>/_tools/run_isolated_v1.py --forbid /path/to/the/dev/tree <INSTALL>/_tools/tests/test_settings_v1.py
```
- `--forbid <dir>` (repeatable): the folders no file may be opened under. Without it, the defaults written in its code: the dev trees, when they exist (listed as KNOWN in MACHINE_PATHS_KNOWN.tsv). Always pass it.
- The script must be inside this Alarm folder; its own arguments follow it.

## What it gives
- The script's own output, then `ISOLATION OK: <n> modules from <Alarm>, the rest from the interpreter; no file opened under <forbidden>; script exit <rc>`.
- Or `ISOLATION FAILED: modules from outside [...]; files opened under [...]: [...]` (the first 20 files).
- Every field: the dictionary.

## Limits and refusals
- exit 0, or the script's own exit code: isolated.
- exit 3: isolation failed (the lists are printed).
- exit 1: no script (it prints its usage) or a script outside this Alarm folder (`NOT IN THIS ALARM FOLDER`).

## Where its data comes from
- No settings key: the forbidden folders come from `--forbid` (run_all_tests_v1 passes the settings' FORBID).
- The script named, inside this Alarm folder.
