# STATUS: Crypto Alarm Desk, V1 (kept current; 3 Nov 2026, 23:0xZ)

Since 9 Nov 2026 (branch update-20261109): engine ALARM_V1_22_1, design pack ALARM_BUILD_V26 (alarm_design/), pipeline ALARM_PIPELINE_V1_4_1
(alarm_pipeline/) and learning loop LEARNING_LOOP_V1_1 (loop/: generic loop and alarm pack), copied by desk/build/copy_v2.py (206 files left out,
desk/build/EXCLUDED.tsv), scrubbed by scrub_v1.py. Tests on 9 Nov: engine 133 PASS, 19 KNOWN, 0 FAIL of 152; desk 30 passed, 5 expected failures.
The steps below are the V1 and V2 record (ALARM_V1_21_16, the old stage-folder loop).
Not released. No git here; publishing is the owner's.

## V2 (4 Nov 2026): conversion instructions, not a converter
V2 ships no market data and no converter. It ships instructions that the user's own agent follows to convert the user's data into the
one format: `docs/DATA_FORMAT_V2.md` (the format, each rule with its code line) and `docs/CONVERT_YOUR_DATA_V2.md` (the steps, the
mapping, the proofs, the families each missing source rules out). The desk-setup skill and `/desk-setup` point to them at the data step.
Proof of the format page (4 Nov 2026, a scratch folder outside the repo): the shipped writer (lab3 write_bins, write_part) wrote PRICE
and two A1 codes; they read back as written; FORMAT.json equal to the lab's byte for byte; the price-only hand check on 5 coins and 2 days
gave the same 22 output lines (88 fires) as on the lab's data. Not yet proven: a conversion by a fresh agent from raw files (no raw
exchange file was at hand; the download host was refused by this session's proxy); a GRADE on converted data.

## V1 steps
| step | what | state | proof |
|---|---|---|---|
| 1a | path scan | CLEAN: 1361 files, 429 hits each allowed by one of 40 rows, 0 not allowed, 0 rows unused (4 Nov 01:0xZ, after the pin fixes; .twins/ is never shipped and not scanned) | `python3 -B desk/build/path_scan_v1.py` |
| 1b | judge parity with the release | OK: 31 files (14 identical, 9 same after the scrub, 8 same after the scrub and re-pointed pins; pins composed through PIN_MAP, PIN_MAP_V2 and PIN_MAP_V3) | `desk/build/judge_parity_v1.py`, desk/build/JUDGE_PARITY.tsv |
| 1c | local mode runs a real COUNT on the lab's data, read-only | PASS: run LOCALCOUNT_20261103, a past lab definition; COUNT rows equal to the lab runner's COUNT of the same definition (7,284 fires, 346 waves, 4 of 4 months); no lab data file newer than the run's start; 37 s | lab job 20268280 (receipts outside this repo) |
| 1d | every test from this folder | PASS: 131 PASS and 16 KNOWN of 147, desk tests 11 passed and 2 expected failures (the sample needs the lab data), with the lab tree, the release, the data store and the GitHub folder forbidden (lab job 20268284, 18 min, peak 1.2 GB); the first run's one FAIL was a flaky clock-stamp compare in test_menu_gate_v1, fixed at its cause here (the two WRITTEN stamps normalised). Rerun after V1.1 (4 Nov, lab job 20268464, 17 min): 131 PASS and 16 KNOWN of 147 again, desk tests 18 passed and 2 expected failures, rc 0 | `python3 -B desk/desk.py tests --forbid <dir>...` |
| 1e | GRADE runs from this folder (added 4 Nov after trial 1) | PASS: the engine's own release check of GRADE and MONTH OK with the desk PYTHON (lab job 20268327, desk.py check); a GRADE of the same past lab definition as 1c: SUM_V1 107 rows and CARD equal to the lab's GRADE (lab job 20268329, 190 s, read-only); test_gm1 now runs its release-graph test instead of skipping it (21 of 21, job 20268331). The fault it fixes: trial 1 below | `python3 -B desk/desk.py check`, desk/release_check_v1.py, desk/build/fix_pins_v2.py and fix_pins_v3.py (PIN_MAP_V2.tsv, PIN_MAP_V3.tsv) |
| 2 | learning pack | DONE: loop/LESSONS_GENERAL_V1.tsv (G01-G15 general, M01-M30 alarm method), loop/KIT_LEARNINGS_V5.tsv and _V6.tsv reworded by machine; one fix on 3 Nov: the reword turned the pass rules R1, R2 into "an agent" (desk/build/reword_learnings_v1.py corrected, tables regenerated); `loop_check.py loop --accept` FULL_PASS; desk/tests/test_loop_v1.py | loop/ |
| 3 | plugin | BUILT (not yet used by a fresh install): skills alarm-desk, learning-loop, desk-setup; commands /new-alarm, /desk-setup; agent alarm-reviewer | plugin/, .claude-plugin/marketplace.json |
| 4 | README and CLAIMS | drafts current with steps 1-3 | README.md (front page), docs/DESK_REFERENCE.md (desk steps), CLAIMS.md |
| 5 | three fresh-agent trials from a copy of this folder: known good, known bad, discovery | trial 1 (T01 known good, 4 Nov 00:15Z): REFUSED_STOP, expected PASS: the GRADE job refused RELEASE (interpreter pins scrubbed to <PYTHON>, a stale value pin of METRICS_V1, ALARMS_V1 pinned but not shipped): a build fault, fixed (step 1e); the agent stopped and reported it word for word as told. Trial 1 rerun (T01, seat CLEANT01B, 01:06-01:29Z, 23 min): PASS: decide PASS as expected, audit FINISHED with A18 PASS, fence unchanged, no canary, loop check FULL_PASS with its TRIED row; TRUE said NOT SUPPORTED (open interest falls after fires only +0.021 more often than at matched random moments, and no more often than it rises) and the first look under its bar (z 1.46 and 1.75), so the PASS is the engine's decide only; the agent named it a copy of a lab recipe. Two desk gaps it found: copy search and novelty compare with this desk's empty registry only; the TRUE claim template does not say what to write for the per-fire file before GRADE (it renamed its placeholder to pass the claim check: reported, judged a format fix, not a work-around). Trial 2 (T03 known bad, seat CLEANT03, 01:33-01:56Z, 23 min): PASS: decide NEEDS MORE MONTHS, inside the expected states (NEEDS MORE MONTHS or STOP); TRUE said TRUE (gap +0.064 on 327 waves), first look NOT PASS (SIZE z -2.62: the fires move less than busy random moments); audit FINISHED with A18 PASS, fence unchanged, no canary, loop check FULL_PASS; no tool refused anything. Trial 3 (D02 discovery): its first seat (CLEAND02) was restarted before any agent ran, because its brief demanded VERDICT DEF NEW, which a fresh desk's empty registry can never print (it prints DEF INCOMPLETE, 0 read); brief fixed, seat CLEAND02B (01:59-02:25Z, 26 min): PASS: a complete clean run (idea PAYEREXIT, funding payers before a settle; decide NEEDS MORE MONTHS, TRUE NOT SUPPORTED, first look NOT PASS; audit FINISHED with A18 PASS, fence unchanged, no canary, loop check FULL_PASS; one BRIDGE REFUSED LOAD 16.19, waited and rerun as told). Step 5 result: all three trials PASS (T01 on its rerun after the step 1e fix). Gaps the agents found, owed in V1.1: copy search and novelty on an empty registry; the TRUE claim's per-fire placeholder before GRADE (all three agents hit it); loop_find skips loop/LESSONS_GENERAL and the KIT learnings; tried_search reads no loop TRIED rows | lab harness trial_clean_v1.py (outside this repo) |
| 5b | V1.1: the gaps the trial agents found (4 Nov 02:3xZ, after the last trial) | DONE (docs and one data file; the engine unchanged): alarm-desk skill rows 1, 5c, 9 (empty registry, the TRUE claim's per-fire placeholder before GRADE, NEW is relative to this desk), CLAIMS section 'Novelty is relative to this desk', loop/SEARCH_ALSO.txt (loop_find reads the general lessons and kit learnings); loop_check FULL_PASS; path scan clean 1362 files; desk tests rerun PASS (lab job 20268464, row 1d) | lab file team/SCOUT/desk_mvp/clean/TRIALS_V1_RESULTS_20261104.md (outside this repo) |
| 6 | outside review of the package | pre-trial package: PASS 23:30Z after two HOLD rounds (8 items fixed). Trial results (4 Nov 02:35Z): HOLD on the trial harness, not the desk: the harness kept its own records in the folder the trial agent could write; the outside reviewer verified all four grades and kept the trials as workflow evidence (not proof of isolation or learning). Fix: the trial harness rebuilt three times (trial_clean_v2: records and judge outside the agent's folder; v3: no read through a link; v4: no read through a linked trial or grader folder); PASS 03:28Z for v4, scoped (grader and agent are still one OS user, so this is not proof of isolation) | team/RESEARCH/GPT/DESKPKG_V1_RECHECK2_OUTSIDE_20261103.md (lab, outside this repo) |

## After the outside review of the package (GPT HOLD 23:01Z, 6 items, all accepted)
- desk.py setup no longer creates or writes the data folders; it makes an empty registry (header only) so the first copy search runs on a
  fresh desk; every other command refuses before setup or after the settings change (desk/tests/test_desk_setup_v1.py, 3 tests, VM).
- GPT re-review HOLD 23:22Z, 2 items fixed: desk.py refuses a DATA_ROOT and OUTPUT_ROOT that overlap, symlinks resolved (test 4 of
  test_desk_setup_v1.py: nested, same and aliased roots, nothing written); the learning-loop skill lets a trial agent read its own brief
  while quarantining held-out logs from the evolve step.
- loop/scripts/add_row.py ran only on macOS (st_birthtime): fixed with a fallback; desk/tests/test_loop_v1.py passes on Linux.
- CLAIMS.md: the parity claim names its 31 files only; the months rule (Sep-Dec build, Jan-Feb exposed once on the owner's word) and the
  held-out separation are in the skills and the reviewer.

## Known tests (reported KNOWN with their reason, never skipped): desk/build/KNOWN_TESTS.tsv
16 rows, all of one of three kinds: the lab's registry and alarm universe (not shipped), the lab machine's settings file (not shipped), the
release's own sha16 table inside a page (the scrub changes code bytes; pages keep the release's numbers by design).

## Blocks a stranger's install
1. No converter from exchange files, by decision: V2 ships the instructions (docs/CONVERT_YOUR_DATA_V2.md), and the user's own agent
   converts; no conversion from raw files has been run end to end yet.
2. Never installed on another machine yet.
3. Reviewer: the plugin's alarm-reviewer agent is the default; the owner's choice of reviewer to ship is open.

## Packaging (when the owner publishes)
Ship: alarm/, desk/, loop/, plugin/, .claude-plugin/, settings/desk.env.example, README.md, CLAIMS.md, STATUS.md.
Never ship: out/, data/ contents, settings/desk.env, .twins/ (the edit twins of this folder), .DS_Store.
