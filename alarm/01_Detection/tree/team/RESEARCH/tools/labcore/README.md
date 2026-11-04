# labcore: the lab's ONE shared package of functions (TOOL_DESIGN V4.2 section 0d; the owner 11:30-11:34Z 23 Oct 2026)
Owner LAB1. Built by BUILD2 (moving tested code), tested by TEST1. Value readers write no value data. Retired consume_look creates
authorization-state markers only in isolated synthetic tests; outcome_allowed is read-only and does not call it (OX-SKEPTIC A15-05).
Tools IMPORT it; a copied helper is a defect.
Readiness records distinguish executed tests, unresolved findings, pending reviews and scientific-use authorization, and cite the exact
release manifest. Historical checklists (below) are dated records, not current approval.
Registry: FUNCTIONS_V1.tsv (function, module, does, inputs_outputs, used_by, tests, owner, moved_from, sha16 of the function's source).
Tests are pytest-only (plain unittest discover finds none): `cd tests; python3 -B -m pytest -q`.
Import: `sys.path.insert(0, '<forensics>/team/RESEARCH/tools'); from labcore import waves, gates, settings, ids`

## SET LIST (what a tool uses before writing its own; a tool's design names the items it uses)
READERS (the one reader per store; labcore points to them, it never re-codes them)
| item | where | status |
|---|---|---|
| lab days (ROWS, CLOCK) | team/LAB3/code/lab3/days.py (Days(root, purpose).rows / read / at) | the one reader |
| raw 3 s bins | lab3/bins.py read_bins | the one reader; a coin-day cache over it is step 2 (labcore.prices) |
| as-of reads | lab3/asof.py | the one reader |
| stored tables (EPI, CTX, STAMP) | alarm_profile, alarm_context, alarm_stamp read() | owners keep them; re-export in labcore.stores is step 2 |
| the recorder | team/FEED/code/feed_v2_read.py | LIVE4's |
| the news feed | team/LIVE4/tools/news_feed/news_feed_read.py (day, follow) | LIVE4's |

PROCESSORS
| item | module | status |
|---|---|---|
| sha16 of a file or text | labcore.ids | STEP 1, moved |
| settings loader with sha check | labcore.settings | STEP 1, moved + want_sha16 |
| window and outcome gates (law.py, PREREG) | labcore.gates | STEP 1, moved |
| waves, wave weights, by-wave bootstrap | labcore.waves | STEP 1, moved (THE one wave module, LAB1 11:13:30Z) |
| coin-day price cache, close_at, path | labcore.prices (PriceCache) | STEP 2 built; equal to money_v1.lab_close_at on 200 real asks |
| lookahead guards: prefix, future plant, join | labcore.lookahead | STEP 2 built |
| times on rows (check_times) | labcore.times | STEP 2 built |
| stored-table readers re-exported | labcore.stores | STEP 2 built (identity) |
| metric brief call, refuse_inputs | labcore.briefs (calls reading-metrics metric_brief.py) | STEP 2 built |
| one cost c | labcore.costs (cost_c = bucket_proof load_cost) | STEP 2, moved |
| exit walk | tools/exit_engine (T03, when built), imported | not here |

## Step 1 (BUILD2, 23 Oct): moved, verbatim, from pinned files
team/RESEARCH/tools/bucket_proof/bucket_proof.py 2b615f53396155d0 (sha16_file, load_settings, month_last_day, check_window, ledger_rows,
outcome_allowed, waves, wave_weights) and money_v1.py 3bb9bf378008aed5 (by_wave). Proof: tests/test_move_v1.py (12 tests): each function's
code is the original's (ast), and the same output on plants, refusals included. The old tools still hold their copies until their owner
(QUANT) switches the imports by a new version; until then the copies are named here, not hidden.
Speed: all step 1 functions are numpy-vectorised or constant time; by_wave's bootstrap is a Python loop of B draws, named, left as moved.
Measured here 23 Oct: by_wave B = 1000 on 1,043 waves 6 ms; waves() on 1,000,000 fires 85 ms.

## Checklist
- [x] looked first: LEAD/SHARED_FUNCTIONS_V1.tsv c3d7d78c names every member and where it lives today
- [x] own folder, README with the set list, FUNCTIONS_V1.tsv, tests; no data writes; no rm
- [x] step 1 moved with a move proof
- [ ] TEST1's tests of labcore (all modules), with the SPEED rows
- [ ] review: QUANT (old owner) + LAB1
- [x] step 2 built to LEAD/LABCORE_STEP2_SPEC_V1.md b75998c5 (prices, costs, lookahead, times, stores, briefs; waves v2)
- [ ] TEST1's step 2 tests and SPEED rows; LAB1 review
