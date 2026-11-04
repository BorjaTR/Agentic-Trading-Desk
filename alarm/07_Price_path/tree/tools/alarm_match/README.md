# tools/alarm_match: the random-moment baseline's rows

Owner seat: QUANT. Reviewer: SCOUT. Built to TOOL_DESIGN_V2.

- **Question.** What does a random moment give, with no alarm, on the same coin, at a similar hour and similar busy-ness? It is the baseline the alarm must beat.
- **Rows.** The matched moments that `QUANT/proposals/stage2/fire_path_v1.py` drew for the A02 alarms (J33614, `q_33614/out/PATHS.tsv`, kind MATCH, 11,634 rows):
  - 10 per alarm, fixed seed;
  - same coin;
  - within ±7 days, UTC hour ±1;
  - 15-min busy-ness before the moment within 0.8 to 1.25 × the alarm's;
  - more than 30 min from any alarm;
  - each moment takes its alarm's side.
- **What this tool does.** `match_events.py` turns them into an EVENTS list (subject `A02_MATCH`), with each moment once. Nothing is drawn here.
- **Used by:**
  - `alarm_context`, subject `A02_MATCH`, with `hist_path` = the alarm list, so the history questions count alarms, not other moments;
  - `alarm_stamp`, subject `A02_MATCH`.
- **The list is text input** (like the alarm list), not stored values. The values go to the one format through those two tools.

```
python3 match_events.py <q_33614/out/PATHS.tsv> <out EVENTS tsv>
```
