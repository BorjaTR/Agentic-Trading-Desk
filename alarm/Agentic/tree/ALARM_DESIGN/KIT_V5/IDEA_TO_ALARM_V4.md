# IDEA TO ALARM V4: FINAL PROPOSAL, CLAUDE1 + CODEX1 (CLAUDE1_20261028, 2026-10-29T08:20:55Z from the clock). TEST, NOT REVIEWED.
Agreed with CODEX1 on the board (CODEX1-QUICKCHECKS-RESPONSE 08:17:41Z, all his changes applied). Replaces IDEA_TO_ALARM_V3 (kept).
Scope: from an idea to an alarm rule our registry can measure, and the quick checks before any grade. The grade itself is PROCESS_V6.
The full rules live in CODEX1's canonical package (runs/CODEX1_20261028/process/IDEA_TO_ALARM_V1/volat-idea-to-alarm, manifest V2); this is
the short view. Examples: QUICK_CHECK_EXAMPLES_V2.md.

## The steps
| step | do | with |
|---|---|---|
| 1 Idea | why should price move after this moment, and the strongest other explanation | FORCED_TRADE_MAP_V1.md is one source of ideas, not a requirement |
| 2 Readings | the codes that show the moment | METRIC_FAMILIES_V1.md, METRIC_MENU_V1.tsv, metric_brief.py |
| 3 Idea card | six fields + the six checks | templates/IDEA_CARD_V5.md |
| 4 Alarm card | the inputs from the registry, the exact rule, the definition and its sha16 | templates/ALARM_CARD_V3.md |
| 5 Hand check | three cases worked by hand, no outcomes | below |
| 6 Seal and grade | prereg and sealed forecast, then one Sep-Dec grade, decided by the alarm bars | PROCESS_V6 |

## The six checks (each: PASS / GAP / FAIL / NOT_CHECKED, one number or evidence path, the next action)
| check | the question | PASS needs |
|---|---|---|
| PREMISE | why should price move after this moment, and what is the strongest other explanation? | an observable premise and its alternative; a forced trader is optional and, if claimed, evidenced (else HYPOTHESIZED) |
| METRIC CONTRACT | do the registry readings measure exactly this? | the card's meaning, unit, type, the rows with values, the reader or op, clock, EMPTY meaning and coverage of the months |
| SIZE/COST | is what is left to gain after the fire bigger than the cost, in the same units? | a measured or bounded number (a payment against the round trip; never the move before the fire); UNKNOWN allowed with a reason |
| SUPPORT | enough events for the study? | eligible waves a month under the study's own rule (PROCESS_V6 B2: 30 waves count a month), counted from readings only |
| PRIOR | is it an existing alarm? | the exact prior and its exposure; a match is REUSE (grade that alarm, credit its author); owner closures honored |
| DIRECTION | which side and horizon, and what would the opposite side or no edge look like? | the prediction and its strongest opposite, before any result |
What stops what: a FAIL on METRIC CONTRACT stops that specification (fix the mapping and try again). A FAIL on SUPPORT stops that study, it does not
disprove the idea. Unknown is NOT_CHECKED, never a zero. No check needs a forced trader. Scores, if used, only order the work.

## The hand check (before any job; no outcomes)
1. Parse and metric gate (detect.load_definition: STOP, CAUTION, UNPROVEN codes refused). 2. Three cases on a small fixed sample of coins
and days: one that must fire, one at or just past the boundary that must not, one with a missing input. 3. For each, the expected answer
worked out by hand from the raw rows (not from the engine's own print), and compared. 4. The line's value at a few fires: it must not
sit on a default (funding at 0.0001). 5. The fire rate and the waves, reported (not a pass line). Helper: tools/hc_defs_v1_to20251231.py
(a candidate: it prints from the same engine, so the hand calculation is the proof; a zero from it alone does not prove no support).

## Four reading traps (METRIC CONTRACT)
BTC-scope codes sit on BTC's row only (raw on an alt is empty: zero fires, no error); word codes (E1.S02, Z1.S02/S04/S05/S08) are not readable
by raw; market codes need the op market and are empty when there is no wave or event; an own percentile of a series that sits on a default
returns the default. A one-day probe (METRIC_MENU_V1.tsv, 15 Oct 2025) does not prove the research months or the control histories.
