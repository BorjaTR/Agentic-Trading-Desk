# CARD <IDEA> (<RUN>, <stamp from the clock>). TEST, NOT REVIEWED.
<!-- CARD_V6 (KIT_V6): ONE card per idea = idea card + alarm card + PREREG + forecasts (KIT_V5 had four files). Draft it, run COUNT,
fill SUPPORT, then seal it: its sha16 goes in the VARIANTS rows (prereg_rel = this file) and in the 4 FORECASTS rows. A sealed card
never changes; a 2nd or 3rd variant with a reason from a result you read gets CARD_<IDEA>_2.md. Every number with its file and sha16. -->

## 1. The idea (plain words)
- Who is forced to trade, or what fails, and why the price should come back (FADE) or keep going (FOLLOW):
- What ends it (the fuel and when it runs out):
- Registry check: the 3 nearest alarms in REGISTRY/ALARM_REGISTRY_V1.tsv (id, state, why this is different). Not a COPY of a PASS;
  not a retry of a STOP without a new mechanism (name it):
- Family (a name from REGISTRY/FAMILY_TAGS_V1.tsv, or NEW: <name>) and the input that is new (no registry alarm uses it):
- Why the OTHER side should lose, not only why yours wins (KIT_V6/IDEA_GUIDE_V1.md pattern 1: if both sides can win, it marks volatility):
- Waves expected Sep-Dec (aim for 1,000 or more; under 800 usually ends at NEEDS MORE MONTHS) and fires (keep under about 20,000:
  a grade takes 4 min at 3,000 fires and 25 min or more at 55,000; LEARNINGS_V6 V6-37):

## 2. Six quick checks (K5/IDEA_TO_ALARM_V4.md; one number or file each)
| check | result | file |
|---|---|---|
| MOMENT (known at the fire, from data at that minute) | | |
| SIDE (FADE or FOLLOW, and why) | | |
| METRIC CONTRACT (each input's card: metric_brief output) | | |
| SCOPE (fires on many coins, not BTC only) | | |
| SUPPORT (from COUNT: 30+ waves in 3 or more of Sep-Dec) | | |
| MEMORY (helper on half B, 8 days: at or under 732 MB) | | |

## 3. Inputs (metric_brief.py output quoted; on the VM with the env line of SKILL section 6)
| code | means | unit | status | EMPTY means | never read as | last day seen in the data (never metric_brief's LAST DAY) |
|---|---|---|---|---|---|---|

## 4. Rule and definition
In words, every line with its unit; side; onset, refractory; what an unknown input does. Definition: ideas/<IDEA>/defs/<V>.json <sha16>.

## 5. Hand check (no outcome read; the helper's output plus one raw-row check)
- Must fire: <coin, time, raw values, helper says>.
- Must not fire (boundary): <...>.
- Missing input: <...>.
- Matched coins = requested coins: <n of n>.

## 6. Variants (at most 3 graded; the 2nd and 3rd name the result that motivates them)
| V | definition | sha16 | lean | differs from V1 by | reason |
|---|---|---|---|---|---|

## 7. Forecast before any outcome (Sep-Dec, per variant)
| V | LEAD 15m low to high | LEAD 1h low to high | months with LEAD +3 (of 4) | R1 | R2 | CLEAR | why |
|---|---|---|---|---|---|---|---|

## 8. Forecast Jan-Apr (optional now; else after a PASS or NEEDS MORE MONTHS with K5/templates/FORECAST_V5.md, before the MONTH job)
| V | month | gap 15m low | gap 15m high | gap 1h low | gap 1h high |
|---|---|---|---|---|---|
| | 2601 | | | | |
| | 2602 | | | | |
| | 2603 | | | | |
| | 2604 | | | | |

## 9. What would prove it wrong
<the result, in numbers>

## 10. Jobs and decision
COUNT <job>; GRADE <job>; ENTRY <job> when R1 passed; decided by decide_v1.py (PASS = hand-off R2, NEEDS MORE MONTHS = R1 only,
STOP = R1 missed; CLEAR beside it); novelty_v1.py on the kept fire list after CLEAN (NEW or NEW SIDE counts as new); MONTH <job>.

## 11. After the decision (written in FINDINGS_<IDEA>.md and the POSTMORTEMS why column, never here: this card is sealed)
`WHY FAILED: <the mechanism, with the number that shows it>` (or `WHY IT PASSED: ...`) and `NEXT IDEA: <what to try instead>`.
