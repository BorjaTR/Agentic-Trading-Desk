# CARD <IDEA> (<RUN>, <stamp from the clock>). TEST, NOT REVIEWED.
<!-- CARD_V7 (KIT_V6; new edition by SCOUT helper K13 for ALARM_V1_5, 31 Oct 2026; old file CARD_V6.md 1df0cab7716611a8, untouched).
ONE card per idea. THIS FILE IS THE PREREG: seal it before any GRADE, then give its path and sha16 in each VARIANTS row (prereg_rel =
ideas/<IDEA>/CARD_<IDEA>.md, prereg_sha16). Draft it, run COUNT, fill SUPPORT, seal. FORECASTS rows are optional (section 8). A sealed
card never changes (FORECASTS rows for a MONTH come later, before it is queued); a 2nd or 3rd variant with a reason from a result you read gets CARD_<IDEA>_2.md. Every number with its file and sha16.
Tools named here are the release's: queue_job_v5, decide_v2, novelty_v2, hc_defs_v2_to20251231, hc_mem_probe_v1, metric_brief_v2. -->

## 1. The idea (plain words)
- Who is forced to trade, or what fails, and why the price should come back (FADE) or keep going (FOLLOW):
- What ends it (the fuel and when it runs out):
- Registry check: the 3 nearest alarms in RESEARCH_ROOT/ALARM_DESIGN/REGISTRY/ALARM_REGISTRY_V1.tsv (id, state, why this is different).
  Not a COPY of a PASS; not a retry of a STOP without a new mechanism (name it):
- Family (a name from REGISTRY/FAMILY_TAGS_V1.tsv, or NEW: <name>) and the input that is new (no registry alarm uses it):
- Why the OTHER side should lose, not only why yours wins (playbook/PLAYBOOK.md "What fails": if both sides can win, it marks volatility):
- Waves expected Sep-Dec (aim for 1,000 or more; under 800 usually ends at NEEDS MORE MONTHS) and fires (keep under about 20,000:
  a grade takes 4 min at 3,000 fires and 25 min or more at 55,000; LEARNINGS_V6 V6-37):

## 1b. TRUE claim (required, ALARM_V1_20: checked by true_gate_v3.py check before the seal; AGENTS.md step 5c)
- The event in one sentence, DETECT (already happening at the fire) or PREDICT (after it):
- Label and mirror: code, when (present end_s, or window start_s and end_s), test, agg or change, threshold, sign, max_age_s (with the card's own staleness rule beside it). The claim file: ideas/<IDEA>/TRUE_<V>_<LABEL>.json:
- Why this label: which position, order or flow the claim says must move it; no price in it; no code or source family shared with the trigger:
- `check` word and families printed (a family printed as a guess, named here), and its line `true_label=... true_mirror=...`, copied here: audit_run_v4 binds the row to it:
- Does the trigger's flow move this label by itself (forced liquidations lower open interest)? Then read flow removed, and say so:
- What each word would mean: TRUE <...>; NOT SUPPORTED <...>; UNSURE <what more it needs>:

## 2. Six quick checks (KIT_V5/IDEA_TO_ALARM_V4.md; one number or file each)
| check | result | file |
|---|---|---|
| MOMENT (known at the fire, from data at that minute) | | |
| SIDE (the event's direction for +1 and -1; the lean FADE or FOLLOW, and why) | | |
| METRIC CONTRACT (each input's card: metric_brief_v2 output; the gate's word: the hand check's PARSE OK line) | | |
| SCOPE (fires on many coins, not BTC only) | | |
| SUPPORT (from COUNT: 30+ waves in 3 or more of Sep-Dec) | | |
| MEMORY (hc_mem_probe_v1 on half B, 8 days: at or under 732 MB) | | |

## 3. Inputs (metric_brief_v2.py output quoted; DEF_TEMPLATE_V4.md "The metric gate" says which tables the COUNT job admits)
| code | scope (coin: op raw; market: op market) | means | unit | status | EMPTY means | never read as | last day seen in the data (never metric_brief's LAST DAY) |
|---|---|---|---|---|---|---|---|

## 4. Rule and definition (written by DEF_TEMPLATE_V4.md)
In words, every line with its unit (a size line is the coin's own pct; a fixed dollar value only as a stray-print filter); fire.side as
the event's direction (+1 = the event pushes the price up; the lean is the VARIANTS row's, never the sign); onset, refractory; what an
empty input does. Definition: ideas/<IDEA>/defs/<V>.json <sha16>.

## 5. Hand check (no outcome read: hc_defs_v2_to20251231.py output, with every raw input named in its last argument, so each fire
## prints the inputs' values)
- Must fire: <coin, time, the printed input values, why they meet the rule>.
- Must not fire (boundary): <...>.
- Missing input: <...>.
- Matched coins = requested coins: <n of n>.

## 6. Variants (at most 3 graded; the 2nd and 3rd name the result that motivates them)
| V | definition | sha16 | lean | differs from V1 by | reason |
|---|---|---|---|---|---|

## 7. Forecast before any outcome (Sep-Dec, per variant)
| V | LEAD 15m low to high | LEAD 1h low to high | months with LEAD +3 (of 4) | R1 | R2 | CLEAR | why |
|---|---|---|---|---|---|---|---|

## 8. Forecast Jan-Apr (optional for COUNT, GRADE and ENTRY, here and in the FORECASTS register; audit_run_v3 A5 asks for the four
## rows before a MONTH job)
| V | month | gap 15m low | gap 15m high | gap 1h low | gap 1h high |
|---|---|---|---|---|---|
| | 2601 | | | | |
| | 2602 | | | | |
| | 2603 | | | | |
| | 2604 | | | | |

## 9. What would prove it wrong
<the result, in numbers>

## 10. Jobs and decision
COUNT <job>; seal (this card, VARIANTS rows); GRADE <job> (queue_job_v5, JOB_GRADE_V7); decided by decide_v2.py (PASS = hand-off R2,
NEEDS MORE MONTHS = R1 only, STOP = R1 missed, INSUFFICIENT, INVALID; CLEAR beside it); ENTRY <job> when R1 passed (decide_v2 asks for
it); novelty_v2.py on the GRADE job's fire list, receipts/<GRADE job>/<V>_FIRES_V1_LIST.tsv, with --lean (NEW or NEW SIDE counts as new);
MONTH <job> (JOB_MONTH_V7) for a PASS or NEEDS MORE MONTHS, after its four FORECASTS rows (audit_run_v3 A5).

## 11. After the decision (written in FINDINGS_<IDEA>.md and the POSTMORTEMS why column, never here: this card is sealed)
`WHY FAILED: <the mechanism, with the number that shows it>` (or `WHY IT PASSED: ...`) and `NEXT IDEA: <what to try instead>`.
