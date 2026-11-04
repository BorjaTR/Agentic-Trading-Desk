# ALARM <IDEA> <V> (<RUN>, <stamp from the clock>). TEST, NOT REVIEWED. Idea: ideas/<IDEA>/IDEA_CARD.md.
<!-- ALARM_CARD_V4 (KIT_V5) = ALARM_CARD_V3 (CLAUDE1 + CODEX1) with the KIT_V5 path in Next. IDEA_TO_ALARM_V4. -->
## Inputs (metric_brief.py output quoted; METRIC_MENU_V1.tsv probe; the card file and its sha16)
| code | means | unit, type | scope, rows with values | step, window, known at | status | EMPTY means | never read as | card, sha16 |
|---|---|---|---|---|---|---|---|---|
## Rule
In words, every line with its unit; side and lean; onset, refractory; what an unknown input does; the trigger names the market reading
that changed (never the time since the detector's last fire). Definition ideas/<IDEA>/defs/<V>.json <sha16>.
## Hand check (no outcome read)
Case that must fire: <coin, time, raw values, expected, engine>. Boundary case that must not: <...>. Missing-input case: <...>.
Line at 5 fires (not on a default): <...>. Fires on non-BTC coins: <yes, or BTC only by design>. Changes: V1 to V2 because ... (no outcome read).
## Next
COUNT job <id> (COUNT_<V>.tsv <sha16>); PREREG <path> <sha16>; GRADE job <id>; decided by decide_v1.py (PROCESS_V7 step 8).
