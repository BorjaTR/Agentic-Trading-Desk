# decide_v1: decision tool V1 (DECIDE seat, 26 Oct 2026, research use)

**What it is.** One generic command for any alarm, any coin set and any day range. For each fire it reads the frozen cards of the three libraries, joined by the fire key (alarm id, coin, second, push side):
- context V4.1, fields prefixed `ctx.`;
- profile V5.1, fields prefixed `prof.`;
- pre-move V1.2, fields prefixed `pmm.`.

It then applies the alarm's rulebook and writes one decision per fire. It never reads a price or an outcome and never runs a producer. No alarm, coin or date is held in the code; a test reads the code and refuses any.

**How it decides (decide_rules_v1.py).** The slots run in order and the first one that decides wins:
1. **Data gate.** A push side other than +1 or -1 gives SKIP BAD_DATA. (The rules give BAD_DATA for a missing row or an empty cell; the command refuses those first, as SELECTION_NOT_COVERED and CARD_MALFORMED, so on real runs BAD_DATA means a declared reason.) Every field an active line uses must hold one of its declared states. Each line declares its field's **states** and its **reasons** (the library's own words for "no reading", exact or as a family such as `UNKNOWN*`). A declared reason gives SKIP BAD_DATA. A word that is neither refuses the whole run, so a real state is never thrown away as bad data. Nothing is judged by how a word is spelled: NOT_BROKEN_TODAY or NO_FORCED_FLOW are states when the line says so (review fix, 26 Oct).
2. **Regime gate.** The safety file's off days and off states give SKIP OFF_STATE. The safety file is EMPTY until the owner sets it.
3. **Side.** FADE, FOLLOW or UNSET.
4. **Skip lines.** At most 3 active lines. The first true line gives SKIP SKIP_RULE. If none is true, the fire is TAKE.

Size, entry and exit come from the rulebook. Entry and exit are only names of existing lab tool settings listed in `LAB_TOOLS_V1.json` (today idea_to_grade V3.1: TT, RT and RR entries and its 8 exits), or UNSET. There is no default, and nothing here computes a fill, an exit or a cost.

**Who writes a line.** Only a loop finding:
1. A passing cell of a frozen loop.
2. A written mechanism.
3. The evidence file with its sha16, checked at every run.
4. The outcome loop through idea_to_grade V3.1 on Sep-Dec.
5. One look at Jan-Feb.

Line status runs CANDIDATE, then FROZEN or FAILED. Research mode uses CANDIDATE and FROZEN lines. Paper mode uses FROZEN lines only.

**Files.**
| file | role |
|---|---|
| decide_rules_v1.py | the pure rules (seven slots, file checks) |
| decide_v1.py | the command: reads fires and cards, checks the pinned evidence and lab tool releases, writes the outputs |
| tests_decide_v1.py, mutants_decide_v1.py | 25 tests and 51 mutants (all killed; the unchanged copy must pass first). The no-names test reads every coin from the frozen universe and every alarm, card and definition name from the registry, and refuses dates as text and as numbers |
| meaning_decide_v1.py | the meaning checker: recomputes every row from the raw cards without importing the tool; finds inputs from the roots it is given, so it runs on the Mac or the VM |
| ADMITTED_INPUTS_V1.json | which signed release record admits each input kind (universe, ctx., prof., pmm.), the receipts it names, and which library field statuses may be used (context: CANDIDATE only) |
| receipts_kit_v1/ | the kit receipts: tests, mutants, edges, old vs new probes, the split tamper probe |
| KIT_DECIDE_V1.md | one line per row of the 25 Oct test kit |
| LAB_TOOLS_V1.json | the entry and exit names a rulebook may use, each with its release sha16 |
| SAFETY_V1.json | off days, off states, kill limits: EMPTY placeholders (the owner's) |
| rulebooks/RULES_DEFAULT_V1.json | any alarm: take every fire, side, entry and exit UNSET (the take-all baseline) |
| rulebooks/RULES_ALM_M_V1.json | M (version 2, V1.0.1): FADE (CANDIDATE); skip line S1 (`ctx.LIQ_COIN.SPREAD` = TIGHTER) is FAILED by the outcome loop and never decides. No active line reads a field, so the data gate reads nothing and M takes all its fires (the 1,407 fires with no spread reading are no longer skipped); entry and exit UNSET |
| loop_v1/ | the outcome loop for M through idea_to_grade V3.1: PREREG, settings, group split, reader with its tests, run script |
| rulebooks/RULES_ALM_S3W_V1.json | S3W: side UNSET (no side finding exists; the S3 study found the push continues), skip when `ctx.ACT_COIN.PACE_5M_VS_1H` = FASTER (CANDIDATE) |
| run_decide_all_v1.sh | the six alarms with the default rulebook, plus M and S3W with their own |
| LAB_TOOLS_INVENTORY_V1.md | what the lab already has, and why V1 only names it |

**Outputs per run (a new folder).** Every header is fixed (it never depends on the data or the rulebook) and per-fire files start with the fire key `alarm_id, coin, t, side` (side = the fire's push side), per the pipeline contract.
- DECISIONS.tsv: one row per fire: the fire key, utc, parent, wave, weight, action, slot, reason, detail, trade side, entry, exit, size, card rows found, and `used_values` (`field=value;...`).
- TAKE_EVENTS.tsv and SKIP_EVENTS.tsv: `alarm_id, coin, t, side, onset_t, trigger, event_id`, with onset_t, trigger and event_id copied unchanged from the alarm's source event list (the one the universe header names, at its sha16), read by `idea_to_grade_v3.py --events ... --events-subset --universe` (it reads columns by name).
- VALUE_COUNTS.tsv: `alarm_id, field, value, kind, fires`, kind STATE, REASON, MISSING_ROW or EMPTY (a summary, not a per-fire file).
- RUN.json: every input sha16, the code, the pinned checks, the admitting release of each input, the source list, the tally and the time of each phase. It is written last: a folder without RUN.json is not a finished run.

**Before it decides, it refuses.** Every refusal prints `REFUSED <CODE>: why` and exits 2, with no traceback and no output folder. The codes: BAD_DATE, OUTSIDE_WINDOW, NOT_WHOLE, BAD_SIDE, BAD_WEIGHT, DUPLICATE_FIRE, NOT_ADMITTED, PIN_MISMATCH, NO_SOURCE_LIST, SOURCE_MISMATCH, MISSING_COLUMNS, NO_FIRES, BAD_VALUE (a used value holds ; or =), FIELD_NOT_IN_CARDS, FIELD_NOT_ADMITTED, SELECTION_NOT_COVERED (a used field has no card row for a selected fire: the library does not cover it, which is not bad data), CARD_MALFORMED (a used cell is empty), UNDECLARED_VALUE, LAB_ID_UNKNOWN, RULEBOOK_INVALID, BAD_INPUT_FILE, INPUT_CHANGED (an input changed during the run), OUT_EXISTS.

**Checking a finished run.** `python3 -B decide_v1.py --verify <run folder>` (or `decide_v1.verify_run()`) refuses RUN_NOT_COMMITTED or RUN_CHANGED_AFTER_COMMIT when a file is edited, missing or extra. The loop's split calls it before it reads a run, and the loop script calls it again before grading.

**Run.**
```
D=<forensics>/team/RESEARCH/tools/decide_v1
python3 -B $D/tests_decide_v1.py; python3 -B $D/mutants_decide_v1.py
bash $D/run_decide_all_v1.sh <forensics> <SCRATCH>/work_PROFLIB/cards_v5_1 <new out folder> [where /Volumes is mounted; empty on the Mac]
```
Speed: all 8 runs take about 5 s (SPEED_BUDGET_DECIDE_V1.md). Stdlib only. File sha16s are in RELEASE_DECIDE_V1_CANDIDATE.json only, written from disk by make_release_decide_v1.py, so this README never holds a stale pin.

**Outcome loop for M (26 Oct 2026, V1.0.1).** loop_v1_1_run, 4 GRADED idea_to_grade V3.1 runs, release e76e30fb282f6990, PREREG V1.1 and ADDENDUM_1, audit AUDIT_DECIDE_LOOP_V1_1_INDEP.md 972a812dea5bb3c2 PASS. NOTHING PAYS: S1 passes in 0 of 22 cells and taking every valued fire pays in 0 of 22 (no cell nets above zero at the stress cost). The fade beats the tough baseline (P1 6 of 6 TT cells), but the skipped TIGHTER fires faded at least as well as the rest (P2 9 of 22), so S1 is FAILED. The grader graded slightly fewer fires than the event files hold, by its own eligibility rules (parents: VALUED 9,340 of 9,357, TAKE 8,590 of 8,607, SKIPRULE 750 of 750, BADDATA 1,380 of 1,407). Final note: FINAL_NOTE_DECIDE_V1.md.

**Limits.**
- A decision row is not a result: whether a TAKE pays is the grader's answer.
- The M rulebook's data gate skips the 1,407 M fires whose spread is UNKNOWN:HOLE (13%). They are not scattered: 1,388 are every M fire on 12-23 Sep, when the spread has no 14 days of history yet, and 19 are on 28-31 Dec. So the outcome loop compares TAKE with SKIP_RULE only on fires where the spread has a reading (24 Sep on), and reports the BAD_DATA block by itself. Comparing TAKE with all fires would mix the skip line with dropping two weeks of September. (For the context owner: a warm-up with no 14-day history should read NO_HISTORY, not UNKNOWN:HOLE.)
- S2B0 and S2R1 have 20 and 7 fires with no profile and no pre-move row. They decide nothing today, because the default rulebook uses no field.
- RUN.json records each input's path on the run machine and its path relative to --root (`root_rel`), so a check on another machine finds it.
- Each entry and exit id must appear quoted in the code its lab tool release names (every code file at its release sha16), so a typo is refused.
- A used field with no card row refuses the whole run (SELECTION_NOT_COVERED). S2B0 and S2R1 have 27 fires on 10-11 Sep with no profile and no pre-move card, so a line on a `prof.` or `pmm.` field for them needs `--first 20250912`.
- The meaning checker takes a 4th argument, where the Mac's /Volumes is on this machine (/Volumes on the Mac, $HOME/mnt on the VM), so it runs on either.
