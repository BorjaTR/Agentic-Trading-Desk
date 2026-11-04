# DEF_TEMPLATE_V3: the blank alarm definition, field by field

Owner: SCOUT (the alarm kit). New edition by SCOUT for the clean release (K7, 30 Oct 2026; the owner 23:07 Berlin: agents must "know
instantly how to use each tool and where everything is"). Old file: `team/RESEARCH/ALARM_DESIGN/KIT_V2/templates/DEF_TEMPLATE_V2.json`
3a0b5e15a769c257, a real alarm (N1 LQ), which agents copied with its claim, codes and lines. `DEF_TEMPLATE_V3.json` beside this file is a
blank: every text says REPLACE, the five inputs are an example of the shape. It parses in detect (DETECT_V1) with the COUNT job's metric
gate, so a copy that keeps the shape stays valid. Tests: `test_def_template_v3.py` beside it.

The format's own document: `01_Detection/alarm_design/README.md` section 2 and its V3 contract (the parser `load_def` in
`alarm_design_v2.py` 70de3f03faaeaa74, the admission `load_definition` in `detect.py` 83c52bfd27166f76; where they differ from the README,
the code wins). JSON allows no comments, so everything is explained here.

## How to fill it, in order
1. Copy the JSON to your run: `ideas/<IDEA>/defs/<V>.json`.
2. Find codes by words: `where_v3.py <words> --kind metric` (01_Detection/tree/team/LAB3/LAB1/tools/where_v2/).
3. Read every code before it goes in: `metric_brief_v2.py <CODE>` (01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/).
   STOP is never used; CAUTION and UNPROVEN codes are refused by detect's gate.
4. Replace every REPLACE, the example inputs, conditions and side. Keep every key of the shape.
5. Hand check (first fires, fires per coin-day, Sep-Dec only), from 01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/:
   `python3 -B hc_defs_v2_to20251231.py --settings <settings> <V>.json 20251001 20251002 BTC 5 <input,input>` (PRICE index coin names).
6. Memory before COUNT: `python3 -B hc_mem_probe_v1.py --settings <settings> <V>.json` (half B, 8 days; PASS at or under 732 MB).

## Top level

| key | what | rules (who checks) |
|---|---|---|
| `_header` | this template's header (owner, old file). Not read by any tool | may stay or go |
| `id` | the idea's name, capitals and digits (e.g. FORCEDBREAK) | required (load_def); printed by the hand check |
| `family` | the idea family of the launch prompt (e.g. POSITIONS_LEAVING) | not read by detect; the registry and the card use it |
| `version` | the definition's version, a string ("1") | required (load_def) |
| `claim` | what the alarm claims (below) | required (load_def) |
| `window` | `first`, `last`: the days the definition may ever be run on | required; 8-digit real days, first <= last (detect DEFINITION_INVALID); the kit uses 20250901 to 20260531 |
| `grid_s` | the step the rule is checked on, in seconds | a whole multiple of 5 above 0 (load_def), at most 86400 (detect GRID_RANGE); 60 = once a minute |
| `inputs` | named series, each with its `op` and that op's fields (below) | each op known with its fields; operands bound; no cycle (detect) |
| `conditions` | the rule: a list of tests (below) | at least one with role claim (load_def) |
| `fire` | onset, refractory, side (below) | detect FIRE_RULE |
| `truth` | labels for alarm_design's own run and card | required with `primary` (load_def); COUNT, GRADE and the hand check never read them |
| `primary` | the name of one `truth` label | must name a label (load_def) |
| `base` | alarm_design's fair comparison base (`match_on`, `scope`, `k`, `caliper`) | required; `{}` keeps its defaults; the kit's grade does not read it |

## claim

| key | what |
|---|---|
| `one_line` | the moment, who must trade or what changes, the expected move and its side, in one line |
| `side_meaning` | what +1 and -1 mean, and whether the idea follows or fades that side |
| `type` | DETECT (an event already happening), PREDICT (a future event) or CONTINUATION (the same episode goes on); frozen before any data (load_def). DETECT needs a `primary` label with `"when": "present"`; PREDICT and CONTINUATION need a label after t |
| `footprint_s` | the trigger event's footprint in seconds, a whole number >= 0 (load_def) |
| `note` | free text: the time scale and its reason (never a result), the codes and how each was read |

## inputs: one entry per series, `"name": {"op": ..., fields}`
A field `of`, `a`, `b`, `if`, `pos` or `neg` names another input or is a number; `w_s` (seconds) and `n`, `h` are above 0; `q` is 0 to
100. Values live on a 5 s clock (as-of: a value is known from its own time on); a window over a 60 s code counts it about 12 times (V5-11).

| op | fields | gives |
|---|---|---|
| `raw` | `code` | the coin's own series of a lab code (the metric gate reads it: STOP refused; CAUTION, UNPROVEN refused) |
| `market` | `code` | the code's MARKET row, the same for every coin |
| `price` | none | the coin's price |
| `known` | `of` | 1 where `of` has a value, else 0 |
| `pospart`, `negpart` | `of` | max(of, 0), min(of, 0) |
| `abs`, `neg`, `sign` | `of` | abs(of), -of, the sign of of (-1, 0, 1) |
| `ratio`, `mul`, `add`, `sub` | `a`, `b` | a / b (empty where b is 0), a x b, a + b, a - b |
| `maxof` | `a`, `b` | the larger of a and b |
| `pick` | `if`, `pos`, `neg` (`tie` optional) | pos where if > 0, neg where if < 0, empty at 0 unless tie names pos or neg |
| `sum`, `max` | `of`, `w_s` | the sum, the max of the last w_s seconds (max needs scipy) |
| `prior_max`, `prior_min` | `of`, `w_s` | the max, the min of the w_s seconds BEFORE this row |
| `change`, `lag` | `of`, `w_s` | of now minus of w_s seconds ago; of w_s seconds ago |
| `accel` | `of`, `n` | 1 when of rose n 5 s rows in a row from a value above 0 |
| `hour_block` | `h` | the hour of the day (UTC) divided by h, whole |
| `own_pct` | `of`, `q` (`floor` optional) | the coin's own q-th percentile of `of` over the 14 built days before the day (the usual line) |
| `trail_pct` | `of`, `w_s`, `q` | the q-th percentile of `of` over the w_s seconds before t |
| `ev_since`, `ev_side`, `ev_value`, `ext_since_ev` | `events` (+ `of`) | an event list's last event: seconds since, its side, `of` at it, the extreme of `of` since; needs `events` and `events_cover` at the top level |

The template's example: `x` = A1.S08 (long liquidations of the minute just ended, USD), `x_top` its own top 1 pct, `px` the price, `move`
the 5 min price change, `side` its sign.

## conditions: a list of `{name, lhs, cmp, rhs, role}`

| key | what |
|---|---|
| `name` | the test in words, with its unit (it is printed on the card) |
| `lhs`, `rhs` | an input name or a number (finite) |
| `cmp` | `>`, `>=`, `<`, `<=`, `samesign`, `oppsign` |
| `role` | `claim` (the idea's own condition; at least one) or `shared` (a filter the fair base keeps true) |

A fire needs every condition true. A row is known when every shared condition is known and the claim is decided.

## fire

| key | what |
|---|---|
| `onset` | true: fire only at the first grid step where all conditions hold after a known step where they did not |
| `refractory_s` | seconds after a coin's fire in which it cannot fire again, a whole number >= 0 (3600 = once an hour) |
| `side` | `input` and `sign`: the fire's side is the sign of that input times `sign` (1 or -1); 0 means no fire |

## truth: a list of labels, each `{name, kind, start_s, end_s, ...}`
Read only by alarm_design's own run and card (never by detect, COUNT, GRADE or the hand check), but required by the parser.

| key | what |
|---|---|
| `name` | the label's name (`primary` names one) |
| `kind` | `forced_usd` (liquidation dollars of a side in (t + start_s, t + end_s]) or `event_within` (an event list; needs `events` and `events_cover`) |
| `start_s`, `end_s` | the label's window after t, in seconds; start_s >= 0 (load_def) |
| `dir` | `same` or `opp`: the fire's side or the other side |
| `floor_usd` | the dollars that count as a hit (forced_usd) |
| `when` | `present` only for a DETECT claim: the window (t - end_s, t] |
