# idea_to_grade: the interface between the two builders (STRATEGY/LEAD, 25 Oct 2026; owner 11:59Z: "finish the tool and launch it as soon as possible")
Detection (i2g_detector) writes ONE committed detector run; the grading chain (i2g_grader) reads only committed runs.
Detector run folder <out>/detect/:
- EVENTS.tsv: '#' header lines (definition id and sha16, roster sha16, first, last, selection) then columns coin, t (whole UTC seconds),
  side (+1 / -1), onset_t (whole seconds, <= t), trigger (the definition's metric code), event_id (stable: sha16 of definition sha16|coin|t|side).
  Loadable by team/RESEARCH/tools/event_profile/event_profile.py load_alarms (the shared loader of every event_* tool).
- COVERAGE.tsv: coin, day, status (PRESENT / NOT_LISTED / NOT_BUILT / HOLE / REFUSED with reason) for every requested coin-day.
- DETECT_RUN.json written LAST (terminal manifest): definition path + sha16, roster, selection, first/last, requested / present /
  unavailable coin-days, event count, code sha16s, source part fingerprints read, phase timings, wall time, peak memory, status COMPLETE.
  A folder without a COMPLETE DETECT_RUN.json is not a run (consumers refuse it).
The public command (owned by i2g_grader) runs detection then grading in one process tree and writes <out>/RUN.json last.

## DETECT (i2g_detector, 25 Oct 2026; detect.py DETECT_V1): the contract details the detector adds
- Call: detect.run(definition, first, last, out_dir, roster, coins='ALL'|'A,B'|list, group=None, group_file=None, workers=8,
  lab_root='<DATA_ROOT>/lab_days') -> absolute path of out_dir/DETECT_RUN.json. out_dir IS the run folder (<out>/detect) and
  must not exist. A refusal raises detect.Refusal (CODE: detail) and commits nothing. The worker pool (spawn, <= 8, nice 10, one numeric
  thread) is joined before run() returns. CLI: python3 detect.py --definition D --roster R --first YYYYMMDD --last YYYYMMDD --out OUT
  [--coins ALL|A,B | --group-file F --group NAME] [--workers 8]. detect.read_run(dir) is the consumer's read (refuses not-COMPLETE / changed).
- Roster: JSON with a 'coins' list (ROSTER_BUILD.json) or a TSV with a coin column. Group file: TSV with group (or sector) and coin columns.
- EVENTS.tsv: every fire of the selected coins with t in [first 00:00Z, last+1 00:00Z), sorted by t then coin; onset_t = t (the onset
  rule fires at the onset); trigger = the definition's raw/market codes joined by '+'.
- COVERAGE.tsv columns: coin, day, status, reason, slots, known_slots, predecessor_known, full_known (i2g_grader's matcher needs them).
  PRESENT: the day's PRICE part lists the coin and every raw input's part is built and lists it, with >= 1 known slot. NOT_LISTED (reason
  PRICE or '<part> <code>'), NOT_BUILT (reason PRICE or the code: lab3 NotBuilt), HOLE (listed, no known slot), REFUSED (lab3/law.py
  research_refusal text). known = the engine's mask: every shared condition known AND the claim decided. slots = 86400 / grid_s;
  known_slots over the day's slots; predecessor_known = the slot D0 - grid_s, read from D-1's data; full_known = PRESENT AND
  known_slots == slots AND predecessor_known == 1. slots / known_slots / predecessor_known are empty for cells not evaluated (not in PRICE,
  REFUSED); NOT_BUILT cells of an input code are evaluated (all UNKNOWN).
- DETECT_RUN.json also holds: grid_s, fire {onset, refractory_s, side}, side {input, sign}, conditions, trigger, execution_path (GRID or
  BASE), cells {requested, present, unavailable, by_status, full_known}, files {EVENTS.tsv, COVERAGE.tsv: sha16}, sources {day=D/PART:
  index sha16} (every part read; re-hashed unchanged at the end of each chunk), phase_s, workers, memory, wall_s, test_hooks (true only
  for test runs with a planted reader or a forced path).
- DETECT_RUN.json parallel {mode, reason, chunks} (detect.py 770e0afa0221276f): CHUNKED (no state crosses days), CHUNKED_ENTRY_WARMUP
  (percentile history: each later chunk rebuilds every coin's last keep_days LISTED days from the serial start, listing gaps included,
  never calendar days; equal to the serial run for every coin), SERIAL_FORCED (a history source depends on history: one process).
  workers.chunks[].warm {mode CALENDAR|ENTRIES, days, coin_days}.
- GUARDS (i2g_check REVIEW_DETECT_V1 fixes, detect.py after 770e0afa0221276f): run(..., research_window='FIRST:LAST' or (FIRST, LAST)) is
  REQUIRED (no default): every month BUILD (labcore.gates.windows) and law.py-readable, first..last inside it, else REFUSED before any read;
  no day outside it is ever opened (DETECT_RUN.json research_window {first, last, days_never_opened}); the window's first 00:00 step has an
  UNKNOWN predecessor. CLI --research-window. DETECT_RUN.json manifest_sha16 = sha16 of the canonical body (sorted keys, no spaces, every
  key but itself); code_sha16 = every module the parent and each worker loaded from the forensics tree (sys.modules + the engine), taken at
  admission and compared before the commit (CODE_CHANGED_DURING_RUN). read_run refuses NOT_A_RUN, MANIFEST_INVALID, NOT_COMPLETE,
  MANIFEST_CHANGED, FILE_MISSING, FILE_CHANGED, EXTRA_FILE. Workers stop when their parent dies.
