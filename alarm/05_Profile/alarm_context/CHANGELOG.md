Written by SCOUT for the repo on 30 Oct 2026 from the release files in tree/tools/alarm_context/ (fields `by`, `changed`) and its
README section "v2 (21 Oct)"; not the owner's document.

# CHANGELOG: alarm_context edition 1 (newest first)
| release | landed by, why | files changed |
|---|---|---|
| V1_7 | LAB1, labcore V2_7 cycle (v2_7 package, S1 run check, S3 selection, S2 quality, lab3 write/bins/days fixes) | CTX_CATALOG_V1.tsv, README.md, alarm_context.py, context_blocks.py, test_alarm_context.py |
| V1_6 | LAB1, labcore V2_6 cycle: lab3/write.py no_prev D-1 once | the same five files |
| V1_5 | LAB1, labcore V2_5 cycle: law.STORES gains hl_node_cols, candidate_days | the same five files |
| V1_4 | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | the same five files |
| V1_3 | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | the same five files |
| V1_2 | BUILD1, recut for STRATEGY-161519 | the same five files |
| V1_1 | BUILD1, recut for STRATEGY-161519 | CTX_CATALOG_V1.tsv, context_blocks.py |
| V1 | BUILD2 (STRATEGY: one JSON format, own files only) | the first release |

The values themselves grew in "v2" (21 Oct, the owner's yes at 21:30 Berlin): 30 new values (EVENT +15, MARKET +6, COIN +9), BTC
implied-vol rank dropped (needs 90 days of DVOL), 7 more planted bugs (33). Editions 2 and 3 (`alarm_context_ed2.py`, `_ed3.py`) are
candidates in the dev tree, not here.
