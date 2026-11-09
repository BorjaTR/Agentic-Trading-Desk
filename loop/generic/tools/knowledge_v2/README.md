# knowledge_v2: the generic knowledge store tool (V1 release candidate, drill-proven, outside review pending)
Status (LEARNING_LOOP_V1_RC2, 8 Nov 2026): V1 release candidate. Drill rows: P35V2-pair (P35_R3, 44/46, alpha 0.95) and P35V2-pair2 (P35_R4, 45/46, alpha 0.84), both fresh agents on GEN_V2 with the strategy pack V1; the P35V2-pair2 finding names knowledge_v2 as the only code change the second pack needed. Store format and status rules carry over from v1 (R2-KNOW_TOOL, a v1 drill). Unit proof: the 33 tests below (a new seat runs 31, 2 skip without knowledge_v1). Outside review: pending (none yet). TOOL_CARD.md and TOOL.json beside this page.
why: the owner 2026-11-08 16:31Z "let's then start making the generic version" (16:10Z: we are in the playground, no release). Found by the P35 portability drill (P35_R1): SPLIT.tsv D20, D21, D22, D25 and GEN_V1/CHANGES.md "Not changed" (hard-coded mechanism list, "vs FUONLY" label, 300-wave floor). Change id C209.

## What changed from v1
- `build_knowledge_v2.py` is a copy of `../knowledge_v1/build_knowledge_v1.py`. Every alarm-only constant and text now comes from a pack file passed as `--pack <file.json>`: mechanism names, design window and its labels, the note words (SEPMAR_ONLY, WRONG_SIDE_YARDSTICK), sides with their yardstick names (FDONLY / FUONLY), the measure label in the brief (lead15), round names (R1 / R3 / R3P), every status bar, the BASE RATES pass bars and text, the brief title and header lines, and where the DEFINITIONS section looks.
- No date constant is left in the code (v1 had DESIGN = 20250910, 20260131).
- Store format unchanged: same five TSV files, same columns (a store written by v1 is read by v2; the golden test proves it on a copy of the live store).
- `--pack` and `--dir` are required (v1 defaulted `--dir` to its own folder; a generic tool has no home store).
- A status bar set to `"TODO"` is allowed in a pack: then `init`, `EVIDENCE`, `QUESTION` and `MOVE` ops work, and `check`, `brief` and the finding ops (ADD, UPDATE, MERGE, RETIRE, HOLDOUT_SAME_SIGN) are refused with a message naming the TODO keys.
- Kept in code (format of the generic loop, same for every seat): column names, arms L / C / V1 (memory arm L feeds BASE RATES), test kinds, finding types, statuses, LINE_CAP 260, section layout of the brief.
- `../knowledge_v1/` is not changed; L11 keeps running on v1.

## The --pack contract (JSON; keys starting with `_` are comments)
| key | meaning | alarm value (packs/alarm.json) |
|---|---|---|
| pack_name | name of the pack | alarm |
| brief_title | first line of the brief | `# KNOWLEDGE BRIEF (alarm learning series)` |
| design_window | eligible evidence window, YYYYMMDD:YYYYMMDD | 20250910:20260131 |
| window_label | the window's name in brief headings | Sep-Jan |
| outside_window_note | note word that makes a row not counted | SEPMAR_ONLY |
| outside_window_label | name used for not-counted rows and the withheld-number mask | Sep-Mar |
| wrong_yardstick_note | note word: the row's margin is against the other side's yardstick (margin unknown) | WRONG_SIDE_YARDSTICK |
| mechanisms OR mechanisms_file | allowed mechanism names: a list, or a text file (one name a line, `#` comments) relative to the pack file; exactly one of the two | FORCED_OUT, FORCED_OUT_SHORTS, CROWDED_LATE |
| sides | list of {key, label, yardstick, mechanisms}; mechanisms is a list of names or `"*"` (all others; exactly one side). BEST SO FAR prints one line per side, in this order | down "down-side fades" FDONLY `*`; up "up-side fades" FUONLY [FORCED_OUT_SHORTS] |
| measure_label | brief word for the lead15 column | lead15 |
| rounds.select / fitted / placebo | variant-id prefixes of the select round, the fitted-change round and its placebo (null: none) | R1 / R3 / R3P |
| status_bars.t_bar | t bar for REFUTED R1 (<= -bar), strong evidence (>= bar), REFUTED R2 (no abs t >= bar) | 2.5 |
| status_bars.supported_min_waves | waves floor for SUPPORTED S1 | 300 |
| status_bars.confirmed_min_runs | runs with strong evidence for CONFIRMED | 2 |
| status_bars.confirmed_min_mechanisms | mechanisms with strong evidence for CONFIRMED | 2 |
| status_bars.confirmed_needs_holdout | CONFIRMED also needs a HOLDOUT_SAME_SIGN op (else SUPPORTED S1+C1WAIT) | true |
| status_bars.refuted_min_runs | runs with a known t for REFUTED R2 | 2 |
| status_bars.s2_fitted_beats_select | rule S2 on: a fitted-round variant that beats its run's select variant and the yardstick is SUPPORTED | true |
| base_rates.pass_margin / pass_t | BASE RATES share of runs whose select round met margin >= and t >= | 2 / 3 |
| base_rates.measure_word | word in the "R1 <word>: mean" line | lead |
| base_rates.pass_line | text of the share line, with {n} {total} {runs} | v1 text |
| base_rates.extra_lines | lines added at the end of BASE RATES | v1 yardsticks-by-month and lead15 definition lines |
| intro_lines | header lines after DEFINITIONS; `{LINE_CAP}` is filled | the four v1 lines (Built-by line keeps the v1 name) |
| definitions | null (section says "not set in this pack") or {team_up, runs_dir, glob, show_prefix}: team folder = store folder up team_up levels; files = team/runs_dir/glob with {alarm} and {v} filled | {4, RESEARCH/ALARM_DESIGN/runs, `*/ideas/{alarm}/defs/{v}.json`, team} |

A missing key, a wrong type, a bad window, a side naming an unknown mechanism, or not exactly one `"*"` side: refused with `REFUSED pack <file>: ...` before any command runs.

## How a new seat starts
1. Make its own store folder (never another seat's): `python3 -B build_knowledge_v2.py init --pack <its pack> --dir <its store>`.
2. Copy a pack (`packs/strategy_v0.json` for strategy) to its own folder, fill every TODO with the owner, point `mechanisms_file` at its MECHANISMS.txt.
3. Curator after each run: `op ... --pack <pack> --dir <store>`, then `check` and `brief` with the same two flags.
- packs/strategy_v0.json (from PACK_V1, best effort): YARD_PLAIN yardstick, one side, measure "net", rounds R1 / R2 / none, pass bars +2.00 bp and t 3 from PACK_V1 section 3, mechanisms from PACK_V1/MECHANISMS.txt. All seven status bars, the window start day and the definitions folder are TODO for the owner (listed in its `_todo`); no bar was invented.
- The alarm seat moving to v2: `--pack packs/alarm.json --dir ../knowledge_v1` gives the same brief byte for byte (only when the owner moves it; today L11 runs v1).

## Tests
`cd knowledge_v2 && python3 -B -m unittest -v test_build_knowledge_v2` (temp folders under KNOW_V2_TMP, default <SCRATCH_DISK>/tmp_SCOUT, removed at the end; the live store is only read).
Result 2026-11-08: 33 tests, OK, 0.34 s.
- Part 1, 23 + 3 tests: every test of v1 (tests/test_build_knowledge_v1.py and test_planted_3run_series.py, bodies unchanged) on v2 with the alarm pack: all status rules and every refusal (UNKNOWN_MECHANISM, CONTROL_EVIDENCE, UNKNOWN_EID, DUP_MOVE_EID, QUESTION refusals).
- Part 2, 7 tests. Golden: v1 and v2 each on its own copy of the live store (100 evidence rows, 25 findings): KNOWLEDGE_BRIEF.md byte-identical (29,799 bytes, DEFINITIONS with real files) and `check` output identical (CHECK PASS); live store hashes unchanged. The v1 brief on the copy also equals the live KNOWLEDGE_BRIEF.md.
- Strategy pack: as filed, names come from MECHANISMS.txt and check, brief and ADD are refused for TODO bars; with a temp copy plus one planted name (SQUEEZE_PLANTED) and planted test bars, v1 refuses the name, v2 accepts it, check passes, and the brief says YARD_PLAIN and net, never FUONLY, FDONLY or lead15.
- Bars from the pack (t_bar 3.5, 500 waves, holdout off change the statuses); every required key missing is refused with its name; bad values refused; the CLI refuses a call without --pack or --dir.

## Examples (C218; `K` = `python3 -B {GENERIC}/tools/knowledge_v2/build_knowledge_v2.py --pack {PACK}/<pack>.json --dir {STORE}`)
`--set` takes one `key=value`; repeat it for each key.
- EVIDENCE (columns: eid, utc, run, arm, mechanism, alarm, variant, test_kind, statement, window, lead15, minus_fdonly15, lead1h, t, waves, months_up, months_total, job, source_file, notes; `t` and `waves` are numbers or empty; `window` is YYYYMMDD:YYYYMMDD, real days, first <= last):
  `K op --who CURATOR --op EVIDENCE --set run=L12 --set arm=L --set mechanism=FORCED_OUT --set alarm=A --set "variant=R1 V1" --set test_kind=VARIANT --set "statement=one line" --set window=20250910:20260131 --set t=3.1 --set waves=410 --set lead15=12 --set minus_fdonly15=2.0 --set source_file=RUNF/ASSESS.tsv --reason "L12 R1"`
- ADD: `K op --who CURATOR --op ADD --set type=STATE --set "statement=..." --set evidence_eids=E0101,E0102 --reason "L12"`
- QUESTION (columns: qid, question, would_move_fid, test_sketch, priority, source_run, status, answered_by_eid; priority 1, 2 or 3 and a question are required):
  `K op --who CURATOR --op QUESTION --set action=ADD --set priority=1 --set "question=does the split hold on the first fire of a wave?" --set would_move_fid=F0003 --set "test_sketch=..." --reason "L12 NEXT TEST"`
- HOLDOUT_SAME_SIGN (orchestrator only, by process rule: `--who` is free text, the tool does not check the role): `K op --who ORCH --op HOLDOUT_SAME_SIGN --target F0003 --reason "frozen best round, same sign"`. Refused for a fid that does not exist (UNKNOWN_FID). It counts only when it comes after the finding's last evidence change (ADD, an UPDATE of evidence_eids, a MERGE into it): after such a change the finding waits for a new held-out read.
- Refusals added in C218: UNKNOWN_FID, NOT_A_NUMBER t|waves, BAD_WINDOW; `init` makes a missing store folder.
