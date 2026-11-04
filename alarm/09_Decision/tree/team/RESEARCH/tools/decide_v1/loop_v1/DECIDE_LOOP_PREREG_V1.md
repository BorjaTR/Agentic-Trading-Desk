# Decision tool V1, outcome loop for ALM_M_V1: written before any outcome is read (DECIDE seat, 26 Oct 2026)

**What is tested.** Whether the M rulebook (RULES_ALM_M_V1.json: side FADE, skip line S1 = skip when `ctx.LIQ_COIN.SPREAD` is TIGHTER) picks fires that pay after cost, and with which entry and exit of the lab's grader. Nothing is graded by the decision tool itself: every number is a row of **idea_to_grade V3.1** (release 593ac5a21fd85b25), FADE side.

**Inputs (pinned in DECIDE_LOOP_SETTINGS_V1.json).**
- Decision run: `<SCRATCH>/work_DECIDE/run_v1_2/ALM_M_V1_OWN` (DECISIONS.tsv 3d131e6867b8aa9a), from the refrozen candidate after the review of 26 Oct (the release sha16 is in DECIDE_LOOP_SETTINGS_V1.json).
- **Only fires with a reading are compared** (review, 26 Oct). The 1,407 BAD_DATA fires are not scattered: 1,388 are every M fire of 12-23 Sep, before the spread has 14 days of history, and 19 are on 28-31 Dec. So TAKE and SKIPRULE are compared with each other and with VALUED = TAKE + SKIPRULE (all from 24 Sep on), never with all fires, and the BAD_DATA block is reported by itself.
- Four groups, each graded as its own GRADED run (one PREREG row each, idea ALM_M_V1, type SETTING_CHOICE, family EXH, flagged: FAMILIES_V2 has no family for the new alarms, and EXH is what the other library loops used):

| group | fires | events file | sha16 |
|---|---:|---|---|
| VALUED (every fire whose spread has a reading, 24 Sep - 31 Dec) | 9,357 | `work_DECIDE/loop_v1_split_v2/VALUED_EVENTS.tsv` | 1bf6fbc326975a7d |
| TAKE | 8,607 | `work_DECIDE/loop_v1_split_v2/TAKE_EVENTS.tsv` | 50e1a643a8d60eed |
| SKIPRULE (S1 true: spread TIGHTER) | 750 | `work_DECIDE/loop_v1_split_v2/SKIPRULE_EVENTS.tsv` | 2efc2fa1241eb0a5 |
| BADDATA (spread UNKNOWN:HOLE, the data gate; described only) | 1,407 | `work_DECIDE/loop_v1_split_v2/BADDATA_EVENTS.tsv` | 54c698f783ea103c |

- Grader settings, unchanged from the signed full population run: days 20250901 to 20251231 (Sep-Dec only, never Jan on), roster ROSTER_BUILD.json, delay 2 s, the frozen universe UNIVERSE_ALARMS_V1.tsv 13c4722a for wave weights, COSTS_PER_COIN_V1 with the honest gap 0.032 and stress gap 0.144, 2 workers, nice 10. No producer or detector is run.

**Settings compared (22 cells, fixed now).** Entries TT, RT, RR times exits V1_1h, V2_1h, C2C1_1h, V1_4h, V2_4h, C4C2_4h (18), plus V1_15m and V2_15m with RT and RR only (4), per the coordinator's horizon choice for M (1 h and 4 h; 15 min only with resting entries). TT with a 15 min exit and the raw returns ret_15m, ret_1h, ret_4h are printed but can never be chosen. All 22 cells count as tries of this one setting choice.

## The bar (fixed now, coded in decide_loop_read_v1.py; FADE, honest cost unless named; edge = TOUGH_EDGE, the trade minus the tough baseline; net = PARENT, net per trade; intervals are 95% with waves as the unit)
In a cell, **S1 passes** only when all five hold:
- a. TAKE beats the tough baseline: TAKE edge lower bound > 0.
- b. TAKE pays: TAKE net > 0 at the honest AND the stress cost.
- c. The skipped fires are clearly worse: SKIPRULE edge upper bound < TAKE edge lower bound (the intervals do not touch).
- d. Every month: in each month where both groups have at least 30 waves, TAKE edge > SKIPRULE edge, and at least 2 such months.
- e. Half the effect still pays: VALUED net + 0.5 x (TAKE net - VALUED net) > 0, at honest AND stress cost.

**Taking every valued fire pays** in a cell when the VALUED edge lower bound > 0 and VALUED net > 0 at honest and stress cost.

**Choice (no reader judgement).** Among the 22 cells where S1 passes, the one with the highest TAKE edge lower bound is the rulebook's entry and exit, and S1 stays CANDIDATE for the one Jan-Feb look. If S1 passes nowhere, S1 becomes FAILED; if taking every valued fire pays somewhere, the cell with the highest VALUED edge lower bound is named instead. If nothing pays, entry and exit stay UNSET and the verdict says NOTHING PAYS. BADDATA is described only: it never changes a choice, but its numbers show what the data gate costs or saves.

No luck test, no shuffle, no count against chance (project rule). The numbers must be due to what we think: hence c (a clear gap), d (every month) and e (half the effect).

## Predictions (scored by the reader, beside the verdict)
| # | prediction | who does what (mechanism) |
|---|---|---|
| P1 | On the valued fires, FADE beats the tough baseline (edge > 0) in all 6 TT cells | an M fire is a coin's 15 min move in its own top 1% of 14 days; such a push overshoots and partly comes back (loop 2: +6.8 points against the move vs cleaned random on +2c before -1c in 1 h, 1,435 waves, every month) |
| P2 | The skipped TIGHTER fires are worse than TAKE (SKIPRULE edge < TAKE edge) in all 22 cells | a tighter than usual book at the fire means real two-sided interest, not a thin push: the move is information and keeps going, so a fade is on the wrong side. Note: the context loop cell measured FOLLOW (TIGHTER FOLLOW reach +8c in 1 h 44.91 vs 23.97, +18.4 points, 750 fires, 420 waves); that the fade loses there is the inference this loop tests directly |
| P3a | Resting entries (RT, RR) net more than TT on the same exit in most of the 12 pairs | the resting leg pays 1.5 bp plus half the gap instead of a taker fee plus the whole gap |
| P3b | The missed resting fills, taken TT, net more than TT on all TAKE fires in most pairs | adverse selection: a fade order rests against the push and is missed when the price turns at once, which are the best fades |
| P4 | At stress cost the 4 h exit nets more than its 1 h twin in most of the 9 pairs | moves grow faster than cost: about 2.5x cost at 1 h and 5x at 4 h (project note) |
BADDATA has no prediction (a feed hole on the spread says nothing about who trades).

## Boring explanations, checked
1. Volatility: the edge is against the tough baseline (same move and volatility cell), not against nothing.
2. One month: rule d.
3. Overfit choice among 22 cells: rule e (half the effect), all cells counted as tries, and the one Jan-Feb look later for the chosen cell only.
4. Resting fills look good only because the bad trades were not filled: P3b and the fill share are printed beside every RT and RR cell.
5. Cost: every pass needs the stress cost to pay too.

**Order.** (1) The independent review of decide V1 candidate 9a9639ce53b773f7 passes. (2) `bash run_decide_loop_v1.sh <new folder>` writes each PREREG row just before its run, runs the 4 GRADED runs (VALUED, TAKE, SKIPRULE, BADDATA) one after the other (about 6 min each) and then the reader. (3) A RESULT row per ask (ledger_add_v6 result, with DECIDE_LOOP_SETTINGS_V1.json). (4) Report. Nothing here is a strategy or live parity.
