# DEF_TEMPLATE_V4: the alarm definition format, field by field, and the rules the code applies

Owner: SCOUT (the alarm kit). New edition by SCOUT helper K13 for release ALARM_V1_5 (31 Oct 2026), from round 7's findings
(team/SCOUT/R7_FIXES_V1.tsv: F24 window, F25 dollar floors, F26 side, F27 format, F29 history and empty values, F35 metric tables, and
the market op of F32). Old files, untouched: `DEF_TEMPLATE_V3.md` 12a2515a590212f6 and `DEF_TEMPLATE_V3.json` 1afcc5d78c8d0a06 (this
folder). TEST, NOT REVIEWED.

**This file is the definition format.** The parser is `load_def` in alarm_design_v3.py (ENG lines 88-121); the admission is
`load_definition` in detect_v2.py (DET lines 145-235). Older texts are history: `01_Detection/alarm_design/README.md` section 2 keeps the
V3 contract as it was, and DEF_TEMPLATE_V3.md named past editions (alarm_design_v2, detect). Where any text differs, this file and the
code win. `DEF_TEMPLATE_V4.json` beside this file is a blank: every text says REPLACE; the five inputs show the shape. JSON allows no
comments, so everything is explained here. Tests: `test_def_template_v4.py` beside it (the code table below is checked byte for byte).

## The code each rule comes from (paths from the Alarm folder; sha16 of release ALARM_V1_4)
| tag | file | sha16 |
|---|---|---|
| ENG | `01_Detection/tree/team/RESEARCH/tools/alarm_design/alarm_design_v3.py` | 9c8db646354a28f0 |
| DET | `01_Detection/tree/team/RESEARCH/tools/idea_to_grade/detect_v2.py` | 11dfdeba60dd01ae |
| OB | `01_Detection/tree/team/RESEARCH/tools/alarms/onset_band_v6.py` | 9acf9cc8a0b24f53 |
| BR | `01_Detection/tree/team/RESEARCH/tools/labcore/briefs.py` | b1ad0fd9168649d8 |
| MB | `01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief.py` | 77d2f63edd3b07bf |
| MB2 | `01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py` | cfb953391141d77e |
| HC | `01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_defs_v2_to20251231.py` | 4ec448aa6688cf36 |
| LAW | `01_Detection/tree/team/LAB3/code/lab3/law.py` | c54e24bdd9b0debe |
| DAYS | `01_Detection/tree/team/LAB3/code/lab3/days.py` | ecf85ffb7bc0fa69 |
| CARD | `01_Detection/tree/team/RESEARCH/tools/alarm_process/alarm_card_v1_2_1.py` | e0f8ae68ac20ab32 |
| MENU | `01_Detection/tree/team/RESEARCH/tools/alarm_process/menu_v2_1.py` | f74706414c0a55c5 |
| M2 | `01_Detection/tree/team/LAB3/METRICS_V2.tsv` | 0e7caa99fa654672 |
| Q | `Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v5.py` | 55ad02cf0356bcc7 |
| JC | `Agentic/tree/ALARM_DESIGN/KIT_V5/jobs/JOB_COUNT_V6.job.sh.txt` | 020c3e8192c0fe36 |
| JG | `Agentic/tree/ALARM_DESIGN/KIT_V5/jobs/JOB_GRADE_V7.job.sh.txt` | dd8cfceb81f3e9bf |
| CG | `03_Grading/tree/tools/alarm_process/alarm_grade_chain_v2_0_2_to20251231.sh` | 702987b96f7c3f57 |
| CM | `03_Grading/tree/tools/month_parts/alarm_grade_chain_v2_2_2_to20260430.sh` | dd8859721c66b4ed |
| JM | `Agentic/tree/ALARM_DESIGN/KIT_V5/jobs/JOB_MONTH_V7.job.sh.txt` | 658a3063f420a052 |
| DA | `01_Detection/tree/team/RESEARCH/tools/alarm_process/detect_aw1_rel1.py` | b1894b3bade40fa2 |

## How to fill it, in order
1. Copy the JSON to your run: `ideas/<IDEA>/defs/<V>.json`.
2. Find codes by words: `where_v3.py <words> --kind metric --n 50` (01_Detection/tree/team/LAB3/LAB1/tools/where_v2/).
3. Read every code before it goes in: `metric_brief_v2.py <CODE>`. STOP is never used; CAUTION and UNPROVEN are refused by the gate
   (below). metric_brief_v2 does not show every table the COUNT job's gate reads: see "The metric gate".
4. Replace every REPLACE, the example inputs, conditions and side. Keep every key.
5. Hand check (Sep-Dec 2025 only), from 01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/:
   `python3 -B hc_defs_v2_to20251231.py --settings <settings> <V>.json 20251001 20251002 BTC,ETH 5 <INPUT>,<INPUT>`. The last argument
   is input names of your definition, not codes (HC line 111). Its first line `PARSE OK` is the COUNT gate's admission (HC lines 91-95).
6. Memory before COUNT: `python3 -B hc_mem_probe_v1.py --settings <settings> <V>.json` (half B, 8 days; PASS at or under 732 MB).

## Top level

| key | what | rules (who checks) |
|---|---|---|
| `_header` | this template's header (owner, old file). Not read by any tool | may stay or go |
| `id` | the idea's name, capitals and digits (e.g. FORCEDBREAK) | required (ENG line 88); printed by the hand check |
| `family` | the idea family of the launch prompt (e.g. POSITIONS_LEAVING) | not read by detect; the registry and the card use it |
| `version` | the definition's version, a string ("1") | required (ENG line 88) |
| `claim` | what the alarm claims (below) | required (ENG line 88) |
| `window` | `first`, `last`: the days the definition may ever be run on. Write first 20250901, last 20260430 (next section) | 8-digit real days, first <= last (DET line 214) |
| `grid_s` | the step the rule is checked on, in seconds | a whole multiple of 5 above 0 (ENG lines 97-98), at most 86400 (DET lines 156-157); 60 = once a minute |
| `inputs` | named series, each with its `op` and that op's fields (below) | each op known with its fields; operands bound; no cycle (DET lines 158-198) |
| `conditions` | the rule: a list of tests (below) | at least one with role claim (ENG line 100) |
| `fire` | onset, refractory, side (below) | DET lines 201-210 (FIRE_RULE) |
| `truth` | labels for alarm_design's own run and card | required with `primary` (ENG lines 88, 107-116); COUNT, GRADE and the hand check never read them |
| `primary` | the name of one `truth` label | must name a label (ENG lines 112-113) |
| `base` | alarm_design's fair comparison base (`match_on`, `scope`, `k`, `caliper`) | required; `{}` keeps its defaults; the kit's grade does not read it |

## The window: first 20250901, last 20260430, and why (F24)
- The queue refuses a definition whose window does not cover 20250910 to 20260430 (Q lines 228-235): one definition serves the Sep-Dec
  COUNT and GRADE and the Sep-Apr MONTH job.
- The jobs run 10 Sep to 31 Dec 2025 (JC line 14; CG line 40) or 10 Sep 2025 to 30 Apr 2026 (CM line 53), each with the research window
  20250901 to its last day (JC line 33; CG line 76; CM line 91). detect_v2 refuses a run whose days leave the definition's window (DET
  lines 812-814, DEFINITION_WINDOW), and so does the MONTH chain's detector detect_aw1_rel1, detect_v2 with the aw1 window table
  (DA lines 822-824).
- First 20250901 is the research window's first day. The lab's first built day is 10 Sep 2025: earlier days read as no coins (ENG lines
  136-143), so nothing fires before 10 Sep.
- Last 20260430 is the MONTH job's last day, and the team rule is never May 2026 or later (AGENTS.md). The code's own seal is 1 Jun 2026
  (LAW line 18), so this window is what keeps a hand-made run off May: detect_v2 refuses any day after `last`.
- DEF_TEMPLATE_V3.json (lines 13-16) said 20260531: the queue took it, but it let a run reach May 2026.

## claim

| key | what |
|---|---|
| `one_line` | the moment, who must trade or what changes, the expected move and its side, in one line |
| `side_meaning` | what +1 and -1 mean as the event's direction (+1 = the event pushes the price up); the lean is not here (see fire) |
| `type` | DETECT (an event already happening), PREDICT (a future event) or CONTINUATION (the same episode goes on); frozen before any data (ENG lines 103-104). DETECT needs a `primary` label with `"when": "present"`; PREDICT and CONTINUATION need a label after t (ENG lines 107-111) |
| `footprint_s` | the trigger event's footprint in seconds, a whole number >= 0 (ENG lines 105-106) |
| `note` | free text: the time scale and its reason (never a result), the codes and how each was read |

## inputs: one entry per series, `"name": {"op": ..., fields}`
A field `of`, `a`, `b`, `if`, `pos` or `neg` names another input or is a finite number (DET lines 167-172); `w_s` (seconds) and `n`, `h`
are above 0; `q` is 0 to 100 (DET lines 180-183).

| op | fields | gives |
|---|---|---|
| `raw` | `code` | the coin's own row of a lab code (coin-scope codes; the metric gate reads it) |
| `market` | `code` | the code's MARKET row, the same value for every coin (market-scope codes; see "The market op") |
| `price` | none | the coin's price: the last 3 s close known at each 5 s step |
| `known` | `of` | 1 where `of` has a value, else 0 (the way to test for an empty reading on purpose) |
| `pospart`, `negpart` | `of` | max(of, 0), min(of, 0); empty stays empty |
| `abs`, `neg`, `sign` | `of` | abs(of), -of, the sign of of (-1, 0, 1) |
| `ratio`, `mul`, `add`, `sub` | `a`, `b` | a / b (empty where b is 0), a x b, a + b, a - b; empty if either is empty |
| `maxof` | `a`, `b` | the larger of a and b |
| `pick` | `if`, `pos`, `neg` (`tie` optional) | pos where if > 0, neg where if < 0, empty at 0 unless tie names pos or neg |
| `sum`, `max` | `of`, `w_s` | the sum, the max of the last w_s / 5 rows of the 5 s clock (rule 3 below; max needs scipy) |
| `prior_max`, `prior_min` | `of`, `w_s` | the max, the min of the w_s seconds BEFORE this row |
| `change`, `lag` | `of`, `w_s` | of now minus of w_s seconds ago; of w_s seconds ago (one row w_s back: exact at whole minutes) |
| `accel` | `of`, `n` | 1 when of rose n 5 s rows in a row from a value above 0 |
| `hour_block` | `h` | the hour of the day (UTC) divided by h, whole |
| `own_pct` | `of`, `q` (`floor` optional) | the coin's own q-th percentile of `of` over its 14 evaluated days before the day (rule 5 below) |
| `trail_pct` | `of`, `w_s`, `q` | the q-th percentile of `of` over the w_s seconds before t (D's earlier minutes too) |
| `ev_since`, `ev_side`, `ev_value`, `ext_since_ev` | `events` (+ `of`) | an event list's last event: seconds since, its side, `of` at it, the extreme of `of` since; needs `events` and `events_cover` at the top level |

The template's example: `x` = A1.S08 (long liquidations of the minute just ended, USD), `x_top` its own top 1 pct, `px` the price, `move`
the 5 min price change, `side` its sign.

## Values, empty values and windows: the rules the code applies (F29)
1. The 5 s clock. Every input lives on a 5 s clock (ENG lines 33-34). A code with a 60 s step: its value known at D0 + 60m (the minute
   that ended then) fills the 12 rows from D0 + 60m to D0 + 60m + 55 s (ENG to_base, lines 201-209: row j takes column floor(5 j / step)).
2. The grid. The rule is checked at D0 + k x grid_s (ENG find_fires line 520). At a 60 s grid that is each minute's first row, where a
   1-minute code holds the minute just ended.
3. A window over a 1-minute code counts 5 s rows, not minutes. `sum` and `max` take w_s / 5 rows (ENG lines 319-320, 233-240). At a 60 s
   grid, `sum` over w_s = 60 N counts the newest minute once, the N - 1 minutes before it 12 times each and the oldest 11 times (V3's
   "about 12 times" missed the two ends). At a 5 s grid, at D0 + 60m + 5j, the newest minute counts j + 1 times and the oldest 11 - j.
   To add the last N whole minutes once each, add the code and its lags at 60 s steps: x + lag(x, 60) + ... + lag(x, 60 (N - 1)).
   AD13 LIQGAP LG4 (runs/AD13_20261029/ideas/LIQGAP/defs/LG4.json 94c2d5188ef9d715) builds its 5 min liquidation sum this way.
4. Empty values. A value is empty when lab3 does not know it (DET header lines 33-36); empty is never 0.
   - A condition with an empty side is false and not known (ENG cond_mask lines 467-470).
   - A row is known when every shared condition is known and the claim is decided: every claim condition known, or one known false
     (ENG lines 483-509).
   - Onset: a fire needs the grid step before to be known and not all true (ENG line 524; DET line 511). One empty step blocks the fire
     at the next step.
   - Side: an empty side input gives side 0, and side 0 never fires (ENG side_of lines 511-512).
   - `sum`: one empty 5 s row in the window empties the sum (ENG roll_sum lines 233-240); a lag sum (rule 3) is empty when one minute is.
     `max` skips empty rows unless all are empty (ENG lines 243-245).
5. `own_pct`: the coin's own line.
   - History: the coin's minute samples (the value at each whole minute) of its last 14 evaluated days before D (OB line 23 HIST_MAX 14;
     ENG push_hist lines 444-450, keep_days lines 456-463).
   - A history day counts only when at least 70 pct of its 1,440 minute samples have a value (OB line 23 DAY_SHARE 0.70; OB lines 63-77).
   - It needs at least 2 such days; with fewer the line is empty for that coin on D (OB line 23 HIST_MIN 2; OB lines 66-67, 73), so every
     condition that reads it is false and not known.
   - The line is the q-th percentile of the good days' samples pooled; with `floor`, max(line, floor) (OB lines 74-75). It is one value
     for the whole day D (ENG line 425).
   - The lab starts on 10 Sep 2025 (ENG lines 136-143), so an own_pct line exists from 12 Sep at the earliest (2 good days).
   - `of` may be any input (AD2 OIFLUSH OF1 takes the own 90th pct of the absolute 10 min return). If that input itself reads a
     percentile, detect_v2 runs the rule in one process, slower (DET lines 697-709, SERIAL_FORCED).

## The market op: how a coin definition reads a market-scope code
- METRICS_V1's scope column says coin or market. A market-scope code (A2.S05, A4.S04, Z2.S02) holds its values in the MARKET row only:
  on 1 Oct 2025 each had 0 of 1,440 values in BTC's row and 1,440, 296 and 1,440 in the MARKET row; the coin code A1.S08 had 1,440 in
  BTC's row and 0 in MARKET (team/SCOUT/K13/logs/market_rows_20251001.txt aa8ce2a9bf8d4b51).
- `{"op": "market", "code": "<CODE>"}` reads that MARKET row and gives every coin the same value (ENG lines 294-296; DET line 489).
- `{"op": "raw", "code": "<CODE>"}` reads the coin's own row (DAYS lines 237-253). On a market code that row is empty, so the rule
  never fires, and nothing warns you. `market` on a coin code is empty the same way.
- A market code can feed `own_pct` like any input: AD10 NEWSLATE V4 (1c7b423d732c90c4) fires when market Z2.S02 is above its own 80th pct.

## conditions: a list of `{name, lhs, cmp, rhs, role}` (the parser's form, F27)

| key | what |
|---|---|
| `name` | the test in words, with its unit (it is printed on the card) |
| `lhs`, `rhs` | an input name or a finite number (DET lines 167-172, 199-200) |
| `cmp` | `>`, `>=`, `<`, `<=`, `samesign`, `oppsign` (ENG line 89, checked at lines 117-119). samesign: sign(lhs) x sign(rhs) > 0; oppsign: < 0 (ENG line 469); a 0 on either side makes both false |
| `role` | `claim` (the idea's own condition; at least one) or `shared` (a filter the fair base keeps true) (ENG line 100) |

A fire needs every condition true. A row is known when every shared condition is known and the claim is decided (rule 4).

## Size lines and dollar floors (F25)
- The read_as of the liquidation codes holds: read a size as the coin's own percentage, never a fixed dollar line (METRICS_V2 rows
  A1.S01 and A1.S08, M2 lines 15 and 24). A dollar line covers very different shares of minutes on different coins (playbook "What
  fails": a line in each coin's own units).
- So the size test is an `own_pct` line. A fixed dollar value may stay only as a stray-print filter: a small floor far below the own line
  of the coins that matter, so a few dollars on a quiet coin never count as its top 1 pct. Write it as own_pct's `floor` (the line is
  then max(own line, floor)) or as a `shared` condition, and say "stray-print filter" in its name.
- Past alarms: AD1 FORCEDBREAK FB5 (64eb0c06e2072687) used the filter form, own_pct q 99 with floor 5000 on A1.S08 and A1.S09.
  AD13 LIQGAP LG4 (94c2d5188ef9d715; 25,000 USD on its 5 min net sum) and AD17 WAVEFORCE WF1 (eac6a36ccf2c8a6d; 5,000 USD a minute on
  A1.S08 and A1.S09) used a fixed dollar line as the size test. They were graded as written; new definitions follow the read_as.

## fire (F26)

| key | what |
|---|---|
| `onset` | true: fire only at the first grid step where all conditions hold after a known step where they did not (ENG line 524) |
| `refractory_s` | seconds after a coin's last accepted fire in which it cannot fire again, carried across midnight; a whole number >= 0 (ENG line 527; DET lines 204-206, 729-737). 3600 = once an hour |
| `side` | `input` and `sign`: the fire's side is the sign of that input times `sign` (1 or -1); 0 or empty means no fire (ENG lines 511-512; DET lines 208-209) |

- **fire.side is the event's direction: +1 when the event pushes the price up, -1 when it pushes it down.** Use `sign` 1 when the input's
  sign is already that push (a price change). Use `sign` -1 only when the input's sign is the opposite of the push: AD4 SETTLEBACK V3
  (7e3c71eccba7fa2c) reads the funding estimate, positive when longs pay, and their closing pushes the price down, so its sign is -1.
- **Never fold the lean into the side.** FADE (bet against the side) or FOLLOW (with it) is the `lean` column of your VARIANTS row. The
  queue refuses any other lean and gives it to the GRADE job (Q lines 296, 314, 324); the job passes it to the chain (JG line 28, LEAN),
  the chain to the card (CG line 100, --lean), as the MONTH job does (JM line 29; CM line 115), and the card reads the FADE or FOLLOW outcome of the fire's side (CARD lines 41-43; MENU
  line 65: FADE = against the move). novelty_v2 `--lean` reads it the same way (cards/novelty_v2.md line 28). A FADE written as sign -1
  with lean FADE is graded as FOLLOW.

## The metric gate: which tables admit a code (F35)
- detect_v2 sends every raw and market code to labcore.briefs as a decision code (DET lines 221-226). STOP, CAUTION and UNPROVEN are
  refused (BR lines 54-63); a code in no table is refused (BR lines 41-42).
- briefs reads metric_brief.py's tables (BR lines 12-13, 28-35): METRICS_V1 and the CATALOGS as cards, METRIC_TRAPS as statuses. Their
  paths come from the variables METRICS_V1, METRIC_TRAPS and CATALOGS; without them metric_brief.py falls back to dev-tree paths
  (MB lines 13-17).
- The COUNT job sets them (JC line 11, each pinned by sha16 in lines 21-23): METRICS_V1 = team/LAB3/METRICS_V1.tsv; METRIC_TRAPS =
  team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv (LAB4's traps plus the owner-cleared Hyperliquid rows);
  CATALOGS = CTX_CATALOG_V1, EPI_CATALOG_V1, team/LAB3/METRICS_HL_ADD_V1.tsv and
  team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv. The hand check sets the same tables (HC lines 31-34, 62-71, 91)
  and so gives the COUNT gate's answer. The GRADE and MONTH chains set the same three
  (CG line 57; CM line 69), and the MONTH detector detect_aw1_rel1 calls the same gate (DA lines 229-234).
- So the COUNT job and the hand check admit the owner-cleared Hyperliquid codes of LEAD/loop2/defs, X1.HLFLOWX.S08 and S09
  (test_def_template_v4.py checks it). metric_brief_v2, the step-2 reader, reads METRICS_V1 and METRIC_TRAPS_V3 only (MB2 lines 30-33)
  and prints NOT FOUND for them. Their status is not settled: METRICS_V2 lines 1238-1239 say IN_FORCE but signed false, use_may
  "Development validation only until independent approval", and 6 days of data, 20261024 to 20261029, none in Sep-Dec 2025 (M2). The
  owners LAB1, LAB4 and LEAD are asked for one status (R7 F34).
- Run detect_v2 by hand only through the hand check: run plain, it reads metric_brief.py's dev-tree defaults (missing on the VM, so
  every code is refused; the dev tree's own tables on the Mac).

## truth: a list of labels, each `{name, kind, start_s, end_s, ...}`
Read only by alarm_design's own run and card (never by detect, COUNT, GRADE or the hand check), but required by the parser.

| key | what |
|---|---|
| `name` | the label's name (`primary` names one) |
| `kind` | `forced_usd` (liquidation dollars of a side in (t + start_s, t + end_s]) or `event_within` (an event list; needs `events` and `events_cover`) |
| `start_s`, `end_s` | the label's window after t, in seconds; start_s >= 0 (ENG lines 114-116) |
| `dir` | `same` or `opp`: the fire's side or the other side |
| `floor_usd` | the dollars that count as a hit (forced_usd) |
| `when` | `present` only for a DETECT claim: the window (t - end_s, t] |
