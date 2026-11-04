# run_isolated_v2: tool card

The RUN proof of a clean tool: a real run imports and opens code only from the release folder. The code: [run_isolated_v2.py](../_tools/run_isolated_v2.py). Exact commands: [TOOL.json](run_isolated_v2.TOOL.json). Every output column: [dictionary](../dictionaries/run_isolated_v2_COLUMNS.tsv). Settings keys: [settings/README.md](../settings/README.md).

archive/ holds past editions: read only, never run; to rerun one, use the old release install.

`<INSTALL>` is the Alarm release folder: on the owner's Mac <RELEASE_ROOT>/Alarm/alarm/current (a Cowork VM sees it under ~/mnt/volat_release/Alarm/alarm/current). Status in the code: TEST, NOT REVIEWED.

## What it does
- Runs one script of this Alarm folder as `__main__`, with its own arguments, and proves at the end:
  1. every Python module it imported came from this Alarm folder or from the interpreter;
  2. every file it opened under a forbidden folder lies under a data key of the settings file and is no code;
  3. nothing it opened or imported lies in an archive/ folder of this Alarm folder (past editions are read only, never run; an archive/ folder in the data is data).
- Data keys: LAB_DAYS, RESEARCH_STORE, HL_FILLS, SCRATCH, RESEARCH_ROOT, RUNNER_QUEUES, BOARD and FEED_GATE (one file: the feed gate). Code: a .py, .pyc, .pyo, .sh, .so or .dylib file, or a job template (.job.sh.txt).
- On the Mac the research data lives inside the dev tree (RESEARCH_ROOT), so data under a key is allowed there; a dev tool's code is not.

## When to use it
- Not a loop step: a release proof (CLEAN_RELEASE_V1 section 1, RUN), once per tool on a real run from the install.
- It answers: did this run use only the release's code and only the settings' data?

## Run it
```
python3 -B <INSTALL>/_tools/run_isolated_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v2.py --settings <INSTALL>/settings/SETTINGS_LOCAL.env AD1_20261029 GIVENB GB1 --grade 20263709_GRADE_GIVENB
```
- `--forbid <dir>` (repeatable): the folders no code may come from; default the settings' FORBID (folders split on `:`).
- The script must be inside this Alarm folder; its own arguments follow it.

## What it gives
- The script's own output, then `RUN ISOLATION OK: modules from <Alarm> and the interpreter only; <n> data files opened under the settings keys; no code and nothing else opened under <forbidden>; script exit <rc>`.
  (it also says `no past edition (archive/) opened`).
- Or `RUN ISOLATION FAILED: modules from outside [...]; files under [...] that are no data of the settings (or are code): [...]; past editions (archive/) opened or imported: [...]` (the first 20 of each).
- Every field: the dictionary.

## Limits and refusals
- exit 0, or the script's own exit code: isolated.
- exit 3: isolation failed: a module from outside, a forbidden file, or a past edition (the lists are printed).
- exit 2: refused: no script (it prints its usage), no settings file or a bad one, no forbidden folder (neither `--forbid` nor FORBID), a script outside this Alarm folder.
- The interpreter's own files never count.

## Where its data comes from
- FORBID: the forbidden folders (the team's dev tree), unless `--forbid` names them.
- The data keys: LAB_DAYS, RESEARCH_STORE, HL_FILLS, SCRATCH, RESEARCH_ROOT, RUNNER_QUEUES, BOARD, FEED_GATE (the files the script may open under a forbidden folder).
- The settings file, read by this package's _tools/settings_v1.py.
