# alarm_profile, generic for every alarm: design note V1 (QUANT, 30 Oct 2026, DRAFT, not built)

Ask: SCOUT hb 07:24:16Z, the owner 30 Oct 08:13-08:15 Berlin: alarm_profile goes into the alarm process and must work for every alarm.
Today (alarm_profile.py VERSION 3): SUBJECTS fixed to A02, A02_1, A02N (line 34); build() refuses others (line 284); the list needs onset_t;
burst values need liquidation rows.

## 1. What a subject becomes
A row in a new file SUBJECTS_V1.tsv (not code): subject, alarm list path, candidate column, KIND (LIQ or ANY), onset rule, CTX subject.
- KIND LIQ: today's A02 family, unchanged.
- KIND ANY: any alarm list with coin, t, side. onset rule = the list's onset_t when it has one, else "t" (the alarm itself), and the rule
  used is written on every row (new column onset_rule), never silent.

## 2. Which blocks run for which kind (EPI_CATALOG_V1 blocks)
| block | ANY | LIQ | why |
|---|---|---|---|
| run (move start, run age, normal move) | yes | yes | price only |
| split (move before vs since onset) | yes | yes | anchor = onset (or t: then "since onset" is empty -> NOT_KNOWN, not 0) |
| speed | yes | yes | same anchor rule |
| oi (open interest change) | yes | yes | price + OI only |
| size / other (liquidations vs the coin's own normal, both sides) | yes, as context | yes | the rows exist for any coin; for ANY they describe, they do not define the burst |
| shape (flushes, peak) | no | yes | only means something when liquidations are the trigger |
| hyperliquid (lead, forced USD) | no | yes | same; SCOUT's HL fills cover 12 Sep - 26 Oct 2025 only |

## 3. What stays the same
Known at the alarm (episode_blocks.Ep cuts every input at the alarm); June 2026 onward sealed; one row per alarm; A02 outputs must come out
byte-equal after the change (identity proof on the existing A02 days, first test).

## 4. Out root
Each ANY subject writes to its own root: research_days/alarm_profile/<subject>/ (private; nothing shared changes for A02).

## 5. Tests before any run
Units: a planted ANY list with and without onset_t; NOT_KNOWN (not 0) when the anchor is the alarm; the subject file refuses an unknown
KIND; A02 identity. Mutants: onset fallback silent; shape block run for ANY; out root shared. Then one real ANY subject (SCOUT names it).

## Open (for SCOUT / the owner)
- Which first real alarm list (SCOUT)?
- Is "liquidations around the alarm" useful context for non-liquidation alarms, or noise? (my view: keep, it is cheap and proven)
