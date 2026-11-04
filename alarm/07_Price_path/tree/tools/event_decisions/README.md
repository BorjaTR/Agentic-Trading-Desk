# event_decisions — Decisions, code VERSION 3.2 (A50 fixes + tester rounds 1 and 2; staged candidate, the LEAD's joint re-cut pending)
**The one Decisions tool, in its one home folder.** Architecture: ARCHITECTURE.md. Release record: RELEASE_event_decisions_V3_2_CANDIDATE.json,
cut by the LEAD's one joint re-cut with the final Situations, Profile and Context bytes (until then the file does not exist and the public
build / check refuse: the release is checked first). Superseded: RELEASE_event_decisions_V3_1_CANDIDATE.json (V3.1), RELEASE_event_decisions_V3_CANDIDATE.json (V3).
**V3.2 needs the shared Situations changes of situations_fixer** (check_run days=, bind_event_lists events_path=, the loader's column
check): on event_situations 1f3abc5c the V3.2 calls fail; the joint re-cut pins the event_situations bytes that carry them.
Owner the owner 10:31:22Z: "take in the correct input, make decisions and give a clear output. Generic, with settings, fast".
**Status: RESEARCH ONLY, paper only.** No live parity is claimed (see Limits). Not signed off: the independent review of this exact
release is PENDING; LAB1 release integration is pending (LAB1 stopped).

## 1. What it does
For each event of any list and each card of a settings file, from what was known at the event time F: an action (FADE, FOLLOW, SKIP,
UNDECIDED), the side (+1 long, -1 short, 0 none), entry option, exit row, size, the rule that decided, why (NO_RULE_HOLDS,
UNKNOWN_INPUT, NO_DIRECTION) and, new in VERSION 3, **which inputs were unknown and why** (`unknown`, e.g. `news:SOURCE_EMPTY:...`,
`mech:FAMILY_BY_DEFAULT`, `side_used:NO_SOURCE_ROW`). No money (the factory), no outcome, no recomputation of any upstream value.
- Rules of a card: ordered; the first TRUE rule decides; an UNKNOWN rule stops the card as UNDECIDED (a later rule never trades in its
  place); all FALSE = SKIP. FADE trades against the push, FOLLOW with it; the push is the list's side, else Cause's side_used.
- Inputs come only through the shared engine and readers of event_situations VERSION 2 (one home: no private reader in this tool).

## 2. Quick start (one public command, any list, coins and dates)
```
PY=<PYTHON>; F=<LAB_REPO>/forensics; T=$F/team/RESEARCH/tools
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
nice -n 10 $PY -B $T/event_decisions/event_decisions.py check <same arguments as build>      # every admission check, writes nothing
nice -n 10 $PY -B $T/event_decisions/event_decisions.py build $F/team/LAB3/code <events.tsv> $T/event_decisions/DECIDE_CORE_V2.json \
    <SUBJECT> <first YYYYMMDD> <last YYYYMMDD> <NEW out_root> <ctx_root> <epg_root> <cause_root> <sit_root> \
    [--coins BTC,ETH | --group-file <tsv> --group NAME] [--source-events SRC=<list.tsv> ...] [--admitted-last 20260228]
nice -n 10 $PY -B $T/event_decisions/event_decisions.py show <out_root> $F/team/LAB3/code <SUBJECT>
nice -n 10 $PY -B $T/event_decisions/event_decisions.py verify <out_root> $F/team/LAB3/code <SUBJECT>     # VERIFY PASS or REFUSED
```
**Before you start (README-only trial gaps U1-U4 of the independent tester):**
- **One SUBJECT for the whole chain.** Use the same subject name (capital letters, digits, _) in all six commands (Context x3, Profile,
  Cause, Situations, Decisions): each tool writes and reads parts named `<SOURCE>.<SUBJECT>`.
- **Preparing an event list from an alarm file.** A tab-separated file with the columns `coin`, `t` (the alarm time F in whole UTC
  seconds), `side` (+1 / -1 / 0; blank = 0), optionally `onset_t` (whole seconds, <= t) and `trigger` (a registered CLOCK code). The column
  `S` (the alarm size) is read by Context (burst_log_usd, days_since_bigger_alarm); other columns (mode, forced, ...) are ignored. The
  header line is required: a list without the columns coin, t and side refuses INVALID_EVENT_LIST (the shared loader). One row per
  (coin, second). Cut by time with the header kept, for example
  `awk -F'\t' 'NR==1 || ($2 >= 1760486400 && $2 < 1760572800)' ALARMS.tsv > LIST.tsv` (one UTC day), and never keep rows from
  March 2026 onward. Keep the same file for every tool of the chain: each part records the list's sha16 and Decisions refuses a mismatch.
  A list without `onset_t` (and without `trigger`) can give an almost empty Profile (its event readings are NO_ONSET): an upstream limit.
- **Context's last argument.** The trailing `0` of `alarm_context_ed2.py build ... <out root> 0` is the list of decision offsets in
  seconds after the alarm; 0 = the alarm itself. Situations and Decisions read decision 0 only.
- **Which Situations settings.** DECIDE_CORE_V1 and DECIDE_CORE_V2 read the column names of SITUATIONS_CORE_V1 (MECHANISM,
  NEWS__truth, MARKET_FLUSH__truth, COIN_FORCED__truth, NEW_MONEY__truth): build Situations with SITUATIONS_CORE_V1.json for these
  cards. A run built with SITUATIONS_CORE_V2 (renamed lines) is refused at admission (UPSTREAM_COLUMN_MISSING).
Worked example (the six-event funding chain, A50's new-user trial, all public commands; 25 Oct receipts in
`<SCRATCH>/work_LEAD/dec_fix/`):
```
EV=<SCRATCH>/work_LEAD/ed2/epg/FUNDPOS_EPG_INPUT.tsv; LAB=<DATA_ROOT>/lab_days; C=$F/team/LAB3/code; W=<new scratch folder>
for L in EVENT MARKET COIN; do nice -n 10 $PY -B $T/alarm_context/alarm_context_ed2.py build $LAB $C $EV FUNDPOS $L 20260115 20260117 $W/ctx 0; done
nice -n 10 $PY -B $T/event_profile/event_profile.py build $LAB $C $EV $T/event_profile/PROFILE_CORE_V2.json FUNDPOS 20260115 20260117 $W/epg
nice -n 10 $PY -B $T/event_cause/event_cause.py build $LAB $C $EV $T/event_cause/CAUSE_CORE_V2.json FUNDPOS 20260115 20260117 $W/cause
nice -n 10 $PY -B $T/event_situations/event_situations.py build $C $EV $T/event_situations/SITUATIONS_CORE_V1.json FUNDPOS 20260115 20260117 $W/sit $W/ctx $W/epg $W/cause
nice -n 10 $PY -B $T/event_decisions/event_decisions.py build $C $EV $T/event_decisions/DECIDE_CORE_V2.json FUNDPOS 20260115 20260117 $W/dec $W/ctx $W/epg $W/cause $W/sit
nice -n 10 $PY -B $T/event_decisions/event_decisions.py show $W/dec $C FUNDPOS
```
Expected: 6 events; MECHANISM_V2 SKIP 4, UNDECIDED 2 (BTC 1768475580 and 1768606560: NEWS unknown, reason carried in `unknown`);
FLUSH_FADE_ONLY SKIP 6. With an existing full chain (A02P), only the Decisions command is needed (section 7).
Rules of operation: analyst python, nice 10 once, one numeric thread, one process; the first line of team/FEED/stops/BACKFILL_GATE.txt
must say RUN (the tool waits through labcore.jobgate before the job and between days). Each run needs a NEW out_root.

## 3. Inputs and admission (refused before any value is read; exit 2 `REFUSED <CODE>: ...`)
- Files first (V3.2): a settings file that is missing or not JSON refuses SETTINGS_FILE; a missing event list EVENTS_FILE; a lab3 code
  folder without lab3/days.py BAD_CODE_DIR. A list without a header, or without the columns coin, t and side, refuses INVALID_EVENT_LIST.
- Event list: TSV coin, t (whole seconds), side (-1/0/+1, blank = 0), optional onset_t, trigger; loaded by the shared loader
  (event_situations.load_events -> event_profile.load_alarms): a repeated (coin, t) (coins compared without case), a fraction of a
  second or a side outside -1/0/+1 refuses (DUPLICATE_EVENT_KEY, INVALID_EVENT_LIST); the output contract is checked again.
- Dates: real days, first <= last (INVALID_DATE, INVALID_RANGE) and lab3/law.py on every day (SEALED_DAY: exit 2, nothing read). There
  is no date constant in this code (owner's rule): the research window is a RUN setting, the run's first..last plus the optional run
  option `--admitted-last YYYYMMDD` (no default; a later last day refuses OUTSIDE_ADMITTED_WINDOW before any read). This team's research
  runs pass `--admitted-last 20260228` (no March 2026 onward data); lab3/law.py inside the reader is the seal (research refused from 20260601).
- Population: all coins of the list in the dates, `--coins A,B` (INVALID_COIN, UNKNOWN_COIN) or `--group-file <tsv: group|sector, coin>
  --group NAME` (UNKNOWN_GROUP): the shared resolver (event_situations.resolve_selection). A selection with no event is a valid empty run.
- Upstream roots: one per source the settings use (and CAUSE2 when an event has side 0); '-' for an unused one. Situations is read only
  from a COMPLETE event_situations VERSION 2 run (its RUN_MANIFEST.json; a VERSION 1 root is refused NO_RUN_MANIFEST).
  A CAUSE2 root (needed when a card binds CAUSE2 inputs or an event has side 0) must pass Cause's own admission (a committed Cause run;
  CAUSE_RUN_NOT_ADMITTED); `--cause-v2-legacy` reads a recorded Cause V2 root without a commit, recorded in the run.
  Every event day must have its part (UPSTREAM_PART_MISSING); every part must name THIS event list by sha16 (EVENT_LIST_MISMATCH), or a
  `--source-events SRC=<list>` bridge whose events hold every selected (coin, t, side, onset_t, trigger) and every other field an upstream
  reads, the size S that Context reads included (V3.2: the shared binder is given this list's path; a different or missing S refuses
  EVENT_IDENTITY_MISMATCH); a part naming no list refuses (UPSTREAM_EVENT_LIST_UNRECORDED).
  The Situations run check covers only this run's event days and selected coins (V3.2): a SIT run that lacks a selected coin refuses
  SELECTION_NOT_COVERED already in `check`; days of the SIT run outside the window are never opened. Column types come from the upstream catalog or part index (never from the values).
- Settings: known keys only (SETTINGS_KEY), typed conditions (the shared validate: no booleans, no NaN, `>`/`<` take numbers), each
  literal against the bound column type (TYPE_MISMATCH: a WORD input takes =, != and in with words; a NUMBER input takes numbers, so
  `1` is never `"1"`), taker entries with a finite `delay_s >= 0` (SETTINGS_ENTRY), trade rules with a declared entry, an exit row of the
  exits file (pinned by sha16) and a finite `0 < size <= 1` (SETTINGS_RULE).

## 4. Settings
```
"inputs":  {"news": "SIT:NEWS__truth", "flush": "SIT:MARKET_FLUSH__truth", "c15": "CTX:coin_move_15m", "oi": "CAUSE2:OI_CONTRACTION__truth", ...},
"entries": {"TAKER_6S": {"kind": "taker", "delay_s": 6}},
"exits":   {"path": ".../exit_engine/EXITS_V1.tsv", "sha16": "db575a2fcb179798"},
"cards": [{"name": "MECHANISM_V2", "rules": [
            {"name": "NEWS_RIDE", "when": {"all": [["news", "=", 1]]}, "action": "FOLLOW", "entry": "TAKER_6S", "exit": "EXIT_T1", "size": 1}, ...],
           "else": "SKIP"}]
```
- DECIDE_CORE_V2.json (b2d0f1935d340b7d, use this): MECHANISM_V2 = SCOUT's draft hypotheses on the four ORDERED Situations truths
  (NEWS > MARKET_FLUSH > COIN_FORCED > NEW_MONEY): an unknown higher truth stops the card (A50 F03); FLUSH_FADE_ONLY.
- DECIDE_CORE_V1.json (353eb01ab3553150, kept as run, never edited): the same cards on the family word SIT:MECHANISM. VERSION 3 reads a
  family word as known only when its `__by_default` is a known 0, so V1 also stops on an unknown earlier situation (FAMILY_BY_DEFAULT).
- Starter cards are hypotheses written before any outcome: rule execution is checked, the market mechanism and profit are NOT proven.
  The Situations builder notes that SCOUT's names (NEWS, MARKET_FLUSH, ...) overstate what the predicates show (A49-07,
  SITUATIONS_CORE_V2 renames them); a card on the renamed lines is a meaning decision for the LEAD, not made here.
- A new card is one block in a NEW settings file; a settings file that was run is never edited.

## 5. Output
- Part DEC.<SUBJECT>, ROWS, one row per event, as_of = known_at = F (the decision is known at F; execution is F + the entry delay).
- Codes DEC.<SUBJECT>.<CARD>__action | side | size | entry | exit | rule | reason | unknown (catalog DEC_CATALOG_<SUBJECT>.tsv).
- `DEC_RUN_<SUBJECT>.json`: the run (status COMPLETE, exit_status 0, run_id, selection requested and observed with per-coin counts, every
  committed part index sha16, the catalog, settings / exits / events / bridge / group-file sha16s, every upstream part-day fingerprint,
  every loaded code file sha16, input availability counts by reason, action counts, timings). A run is consumable only through it.
- Publication: the run is written in `<out_root>.pending_<pid>_<stamp>`, checked (sources unchanged, parts read back, row counts), renamed
  to `<out_root>`, then the manifest is committed last. A failure leaves `<out_root>.failed_<stamp>` (with FAILED.json), never out_root.
  An existing out_root refuses OUTPUT_EXISTS unless it holds the identical run (same code, settings, list, selection, upstream): UP TO DATE.
  The run_id is printed by `build` and stored in DEC_RUN_<SUBJECT>.json; it binds the loaded code, so this README cannot give a fixed
  run_id for the worked example (the expected counts above are the check). It also includes the event list's PATH: the same list copied
  to another path is a new run (OUTPUT_EXISTS in an old root, never a false UP TO DATE).
- Reading: `event_decisions.read_decisions(out_root, code_dir, SUBJECT)` (the one DEC reader), `show` or `verify`. Each first runs the
  shared check `run_manifest_candidate.verify_committed` (team/RESEARCH/LEAD/SHARED_RUN_CHECK_NOTE_V1.md): every committed file of every
  part (index, REASONS.txt, WORDS/*.txt holding the word values, payload blocks) against the digest committed with the run, and every
  payload block through lab3's own integrity check. A missing, interrupted or changed run is refused before any value is returned
  (RUN_NOT_PUBLISHED, RUN_INCOMPLETE, RUN_CHANGED_AFTER_COMMIT, CORRUPT_RUN). An UP TO DATE rerun is reported only after the same check.
- The factory's consumer of this output is the candidate `factory_dec_adapter_candidate.py` (section 9).

## 6. Troubleshooting (codes on stderr, exit 2)
| code | meaning | do |
|---|---|---|
| SEALED_DAY / OUTSIDE_ADMITTED_WINDOW | a day lab3/law.py seals, or past the run's --admitted-last | change the dates (the run setting) |
| INVALID_DATE / INVALID_RANGE | not a calendar day, or first > last | fix the dates |
| NO_RUN_MANIFEST / RUN_NOT_COMPLETE / CORRUPT_RUN | the SIT root is not a complete Situations V2 run | rebuild Situations into a new root |
| UPSTREAM_PART_MISSING | an event day has no part of a source the settings use | build that source for those days |
| EVENT_LIST_MISMATCH / EVENT_IDENTITY_MISMATCH | upstream was built from another list | rebuild upstream from this list, or bridge with --source-events |
| TYPE_MISMATCH / SETTINGS_* | settings literal or field invalid | fix the settings in a NEW file |
| SOURCE_CHANGED | an upstream part, the list, settings or code changed during the run | run again into a new root |
| OUTPUT_EXISTS | out_root holds another run or a partial one | choose a new out_root |
| RUN_CHANGED_AFTER_COMMIT / CORRUPT_RUN | a published run's file or payload changed after the commit (or it predates V3.1) | rebuild into a new root |
| INVALID_DATE | a day or --admitted-last is not a calendar YYYYMMDD | fix the run setting |
| SETTINGS_FILE / EVENTS_FILE / BAD_CODE_DIR | the settings file is missing or not JSON; the event list is missing; the code folder has no lab3 | fix the path (V3.2) |
| INVALID_EVENT_LIST | the list has no header, or no coin, t or side column, or a bad value | fix the list (keep its header) |
| SELECTION_NOT_COVERED / RANGE_NOT_COVERED | the Situations run does not hold every selected coin or day | build Situations for the selection |
| FIRE_IDENTITY_INVALID (adapter) | a fire's time is not whole seconds or its side is not -1 / 0 / +1 | fix the fire list |

## 7. Evidence (25 Oct 2026; receipts in <SCRATCH>/work_LEAD/dec_fix/; record A50_CLOSE_V1.md)
- V3.2 (tester round 2, staged, not cut): 106 tests pass in a scratch copy tree (dec_fix/v32_tree_20261025T131504Z: the team folder
  linked, real copies of the five tools and lab3, the tester's proposed Situations changes applied to the COPY of event_situations, a
  scratch V3_2 cut): the 86 of V3.1, the tester's round-2 file (N4, L2, K6 x6, R3 x2, G8, N5: 12 tests) unchanged, test_N6 and the
  staged run module tests. Mutation report MUTATION_V32.json (the scratch release re-cut for each mutant, so a release refusal never
  counts as a kill): 9 of 10 killed, each by its own test; M08 (UP TO DATE through load_complete) survives and is equivalent (run_id
  binds the code; load_complete already checks part digests). No team release was cut and no full run was made (the LEAD's joint re-cut).
- V3.1 (tester round 1): 86 tests (the 72 below, the tester's 4, test_event_decisions_v3_1.py 5, test_run_manifest_candidate.py 5).
  Small real check on the FUNDPOS chain (real_v3_1_*/REAL_V3_1.json): build, verify (VERIFY PASS), show and UP TO DATE through the
  public commands; an edited word file, an edited REASONS.txt and one flipped payload byte are each refused (show and the adapter check:
  exit 2, RUN_CHANGED_AFTER_COMMIT); an impossible day or a malformed --admitted-last is refused INVALID_DATE (exit 2).
- Tests (72): `python3 -m pytest -q -p no:cacheprovider test_event_decisions.py test_event_decisions_a50.py test_event_decisions_shared.py
  test_factory_dec_adapter_candidate.py`. Every A50 finding has a test that failed on the reviewed V2 with the reviewed shared code
  (receipts_tests/BEFORE_V2_on_A50_shared.xml: 42 failed) and passes on this release (final_20261025T114950Z/TESTS_FINAL.xml).
- Small real chains on THIS release, fresh with the current public commands (final_20261025T114950Z): FUNDPOS (6 events, 2 days),
  A01 one day (168 events, 44 coins), side-0 chosen times (3 events). An independent oracle (lab3 reader only), frozen before each
  Decisions run, matched every cell of both settings including clocks (192, 5,376, 96 cells; 0 mismatches). Decisions command: 0.2-0.3 s,
  66-95 MiB per run. FUNDPOS: the two NEWS-unknown events that V2 left SKIP are UNDECIDED with their upstream reasons (NO_ANCHOR,
  SLOW_START). Admission refusals, one coin, a changed range, an empty selection, an interrupted run and the UP TO DATE rerun were checked
  on the same real chain.
- Full A02P (8,158 events, 52 coins, 170 days) last ran at 11:45Z on the previous cut (event_decisions 4757a4868cd7a0ee; the only later
  change is the optional run option --admitted-last, outside the decision path) on the Situations V2 run a02p_core_v1 (code 1f199078):
  2.9-3.0 s wall and 89 MiB peak per run (budget 30 s / 512 MiB, frozen before the code; A50 measured V2 at 11.5 s / 193 MiB);
  MECHANISM FADE 856, FOLLOW 865, SKIP 6,437; FLUSH_FADE_ONLY FADE 728; equal to A50's frozen expectations (114,212 cells, identities and
  clocks) and to the oracle frozen before the run (261,056 cells, both settings); replay byte-identical (22,100 files). The full run on
  this exact release is part of the LEAD's one combined full run (owner 11:46Z).

## 8. Dependencies (pinned in the release; owners)
<!-- PINS: written by the release cut from RELEASE_event_decisions_V3_2_CANDIDATE.json; every hash here is a pin of that release -->
- event_situations.py 89bd38241bea653a (situations_fixer; pinned by file: the shared engine, readers, selection, event-list binding and run check of Situations)
- event_profile.py c033ca54875044dc + clock_series.py 3eea93aeefb8b6a0 (profile_fixer: the event loader and day helpers)
- alarm_context_ed2.py 0ff825572dd95d86 + context_blocks_ed2.py 14bd2ede3fdbdb76 (context_fixer: the CTX reader, used when a card binds CTX inputs)
- labcore release V2_7 b43f8168dc4a1c19 (LAB1: ids, settings, lookahead, jobgate, release, S1 run check; lab3 days / write / law through it)
- run_manifest_candidate.py 1a99409b69d6644a (this folder; the shared run check V3 with S1, pinned by labcore V2_7; users: Decisions, Situations, Outcomes, Context, Profile)
<!-- /PINS -->

## 9. Factory integration (candidate)
`factory_dec_adapter_candidate.py`: the factory's decide() step replaced by the DEC decisions (factory_v2 imported, not edited):
contract checks (complete run, pinned settings / exits / events, identity and side of every fire checked as given before any
conversion (whole seconds, -1 / 0 / +1: FIRE_IDENTITY_INVALID), clocks as_of = known_at = F, eight
fields decoded, only FADE/FOLLOW with side +-1, 0 < size <= 1, declared entry and exit trade), then factory_v2.trade() per trade with the
DEC entry delay, DEC exit row and DEC size x size_usd. `python3 factory_dec_adapter_candidate.py check <dec_root> <lab3 code> <SUBJECT>
<CARD> <fires.tsv>` reads a real DEC run through the contract and stops before money. Promotion into tools/factory = a LAB1 release cycle.

## 10. Limits
- RESEARCH ONLY: the inputs are research snapshots of Context ed2, Profile, Cause and Situations; whether the live recorder produces each
  input at decision time is not shown (no live parity test): never use for live or paper trading decisions.
- Taker entries only; fixed sizes; flat all/any conditions plus two-input derived comparisons; no WAIT / delayed re-evaluation, no
  learned sizes or model inference, no portfolio limits (A50 'Cards cannot currently express').
- Situations family words: a card that reads a family word gets FAMILY_BY_DEFAULT unknowns; reading the ordered truths (V2) is clearer.
- Stale, empty and known-at states of CTX / EPG / CAUSE2 inputs carry the shared reader's reasons; a reason it does not give reads UNKNOWN.
