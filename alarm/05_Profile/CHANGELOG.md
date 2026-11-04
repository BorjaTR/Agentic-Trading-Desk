# 05 Profile: what changed in each release (newest first)

Source of every line: the release file named, field `by` (who landed it and why) and field `changed` (the files whose sha16 changed);
`text_changes` when present. Each alarm_profile release pins the alarm_context release named beside it.

## alarm_profile edition 1 (owner QUANT)
| release | landed by, why | files changed |
|---|---|---|
| V1_8 (`RELEASE_profile_V1_8.json`, pins context V1_7) | LAB1, labcore V2_7 cycle: the v2_7 package, S1 run check, S3 selection, S2 quality, lab3 write/bins/days fixes | CTX_INPUTS_V1.tsv |
| V1_7 (pins context V1_6) | LAB1, labcore V2_6 cycle: lab3/write.py no_prev D-1 once | CTX_INPUTS_V1.tsv |
| V1_6 (pins context V1_5) | LAB1, labcore V2_5 cycle: law.STORES gains hl_node_cols, candidate_days | CTX_INPUTS_V1.tsv |
| V1_5 (pins context V1_4) | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | CTX_INPUTS_V1.tsv (text: CTX_INPUTS_V1.tsv, PROFILES_V1.tsv) |
| V1_4 (pins context V1_3) | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | CTX_INPUTS_V1.tsv |
| V1_3 (pins context V1_2) | BUILD1, recut for STRATEGY-161519 | CTX_INPUTS_V1.tsv |
| V1_2 (pins context V1_2) | BUILD1, recut for STRATEGY-161519 | CTX_INPUTS_V1.tsv, README.md, alarm_profile.py |
| V1_1 (pins context V1_1) | BUILD1, recut for STRATEGY-161519 | EPI_CATALOG_V1.tsv, episode_blocks.py |
| V1 (pins context V1) | BUILD2 (STRATEGY 14:34:17Z, 14:45:21Z: one JSON format, own files only) | the first release |

## alarm_context edition 1 (owner LEAD / LAYERS)
| release | landed by, why | files changed |
|---|---|---|
| V1_7 (`RELEASE_context_V1_7.json`) | LAB1, labcore V2_7 cycle (as above) | CTX_CATALOG_V1.tsv, README.md, alarm_context.py, context_blocks.py, test_alarm_context.py |
| V1_6 | LAB1, labcore V2_6 cycle: lab3/write.py no_prev D-1 once | the same five files |
| V1_5 | LAB1, labcore V2_5 cycle: law.STORES gains hl_node_cols, candidate_days | the same five files |
| V1_4 | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | the same five files |
| V1_3 | BUILD1, labcore V2_3 cycle (STRATEGY-190912a) | the same five files |
| V1_2 | BUILD1, recut for STRATEGY-161519 | the same five files |
| V1_1 | BUILD1, recut for STRATEGY-161519 | CTX_CATALOG_V1.tsv, context_blocks.py |
| V1 | BUILD2 (STRATEGY: one JSON format, own files only) | the first release |

Editions not released yet (alarm_profile 2, 2.1, 2.2; alarm_context 2, 3) are listed in the README under "In development" and stay
in the dev tree until two reviews release them.
