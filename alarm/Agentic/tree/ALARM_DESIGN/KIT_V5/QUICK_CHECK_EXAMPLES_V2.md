# QUICK CHECK EXAMPLES V2 (CLAUDE1 + CODEX1, 2026-10-29T08:21:26Z from the clock). TEST, NOT REVIEWED. Replaces V1 (kept).
The six checks of IDEA_TO_ALARM_V4, each PASS / GAP / FAIL / NOT_CHECKED. Labels say the stage an idea passed or stopped at. Grade results
are exposed summaries from our own runs (development months), not independent audits; they come after the checks, never inside them.

## Passed the checks
| idea | PREMISE | METRIC CONTRACT | SIZE/COST | SUPPORT | PRIOR | DIRECTION | stage reached |
|---|---|---|---|---|---|---|---|
| DAYPOKE: price pokes past a 24 h high or low older than 2 h and is back inside within 2 min; FADE | PASS (price pattern; stops used up HYPOTHESIZED) | PASS (price op, prior_max excludes now, first 2 min of each day unknown) | NOT_CHECKED (the payoff is the return; unknown before a grade) | PASS (1,359 waves Sep-Dec, 267-381 a month) | PASS (new; desk P12 is the held break) | PASS (FADE; opposite = a real breakout) | grade Sep-Dec: FADE 15m +4.9, 1h +4.6; 3 of 4 months pass |
| FLUSHED: liquidation wave 10+ min old, the coin fell hard, 3 pct+ of its OI already left; FADE | PASS (fewer sellers left HYPOTHESIZED; alternative = overshoot whatever the OI, tested by the twin UNFLUSH) | PASS (A4.S04/S05 MARKET row, empty with no wave, handled; A7.S01/S03 and COIN_C3.S02 coin rows) | NOT_CHECKED (the 8c median is the move BEFORE the fire, not what is left) | GAP (waves 20/133/128/46: Sep under 30) | PASS as an extension of desk O1/O2 (QUANT, SCOUT) | PASS | alarm card written; no grade read |
| FACTORSTRETCH (CODEX1) | PASS | PASS (8,224 full input replays, 5,574 complete comparison sets) | not recorded | PASS | not recorded | PASS | grade: the frozen price hypothesis FAILED 0 of 6. Passing the checks is not passing the alarm |
| ALTCASCADE: big BTC move against a crowded alt; FOLLOW | PASS (alternative = overshoot) | PASS after a rebuild (BTC's move = COIN_C3.S02 minus COIN_C3.S06) | NOT_CHECKED | PASS (196 waves, 42/64/59/31) | PASS | PASS | grade: FAILED; the other side won (FADE +8.0 at 15m), 0 of 4 months |

## Stopped, and where
| idea | stopped at | the number or evidence | what it means |
|---|---|---|---|
| BTC's move read with raw C1.S16 on alts | METRIC CONTRACT FAIL (invalid mapping) | C1.S16 has values on BTC's row only (15 Oct 2025 probe); on alts empty, zero fires, no error | that specification stops; the idea goes on with COIN_C3.S02 minus COIN_C3.S06 (within 0.006 points) |
| C08 venue gap (CODEX1) | METRIC CONTRACT HOLD | the quotes route selects by exchange time without arrival filtering; HL books are live snapshots, not the needed history | held until a reader gives the joint historical quotes |
| C03 "low net flow = no trading" (CODEX1) | METRIC CONTRACT FAIL (killed interpretation) | buy 100 / sell 100 and buy 0 / sell 0 both net 0 | a narrower net-restart reading may still work |
| FUNDSETTLE: payers close before the settle; FOLLOW | SIZE/COST FAIL for the payment-saving trade | abs funding above about the median round trip (0.002 per 8 h) in 99 of 22,026 coin-settles Sep 10-Dec 31 | under those assumptions nobody closes to save the payment; other pressure is not bounded. Graded before this check existed: lean -4.0 at 15m, 1 of 4 months |
| MACROPRINT: follow the move after a US print | SUPPORT FAIL for this study | 50 print minutes in Sep 10-Dec 31 (14/11/8/17 a month) | support-limited, not disproven |
| RETAILCHASE: small fills chase a move, big fills against | PRIOR: REUSE of LU | the same lone-pump moments; 4.2 fires a coin-day on the hand check | grade LU (passes 6 of 8 months), not a new alarm |
| UNFORCED: a big move with no liquidations; FOLLOW | not stopped: PREMISE PASS (late traders; alternative = overshoot), DIRECTION GAP | M's FOLLOW side, exposed: +2.6 at 15m, -2.6 at 1h | needs its own card; the old kill (no forced trader) was wrong |
