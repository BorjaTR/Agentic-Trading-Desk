# Lab tools inventory for decision tool V1 (26 Oct 2026)

**Verdict.** The lab already has signed, generic tools for grading, entry types, exits and cost. Decision tool V1 should compute nothing about money. It only has to pick which fires to take and on which side, then hand that list to **idea_to_grade V3.1**. That tool already grades three entry types, eight exits, cost per coin, the tough baseline and waves, for any alarm.

R = `<LAB_REPO>/forensics`. Status comes from `R/team/RESEARCH/LEAD/SIGNOFF_V1.tsv` (row numbers) and each tool's own RELEASE file, as read on 26 Oct.

## 1. Grading, outcome and money

| Tool | Path | What it does | Version and status | Generic? | Use in V1 |
|---|---|---|---|---|---|
| **idea_to_grade** | `team/RESEARCH/tools/idea_to_grade/idea_to_grade_v3.py` | Takes any event list, coin set and dates. Gives returns at 10 s to 4 h, 8 fixed exits, 3 entry types (TT, RT, RR) with cost per coin at the honest and stress gap, fill share and what missed fills did, the tough baseline, frozen wave weights, and per-month rows. Refuses to run without a PREREG ledger row. | V3.1, rows 73-74: RELEASED FOR TEST RUNS (builder and independent reviewer). GRADED runs need a PREREG row in TRIES_LEDGER_V1. | Yes: "No alarm, coin or date is held in this code" | **The grader.** V1 hands it the TAKE list with `--events-subset --universe` |
| event_outcomes | `team/RESEARCH/tools/event_outcomes/` | The outcome labels tool (OUTCOMES_CORE_V3) | V3 CANDIDATE, not approved, re-review pending | Yes, by settings | Not used (not approved) |
| factory | `team/RESEARCH/tools/factory/factory_v2.py` | Batch runner for strategy cards: trades after full cost, rivals, fairness bar | V7. Planted data only, no real money run. Reads the OLD profile, context and cause parts. No signoff row. | Yes | Not used (old inputs, not signed) |
| fairness_bar | `team/RESEARCH/tools/fairness_bar/` | The luck bar over a batch | V2_3 CLEARED_FOR_USE (row 56) | Yes | Not used (our rule: no luck tests) |
| freeze_judge | `team/RESEARCH/tools/freeze_judge/` | Judges a frozen card once on an unseen window | V2_8, last row FIXING (row 60) | Yes | Later, for the one Jan-Feb look, once fixed |
| bucket_proof | `team/RESEARCH/tools/bucket_proof/` | Tests whether a bucket file separates outcomes better than rivals | Pinned in label_ewsd V2_6, frozen until outside approvals | Yes | Not used |
| alarm_match | `team/RESEARCH/tools/alarm_match/` | Rows for the random matched moments | V3_4 CLEARED_FOR_USE (row 67) | Yes | Inside idea_to_grade already |

## 2. Entry and resting orders

| Tool | Path | What it does | Status | Use in V1 |
|---|---|---|---|---|
| idea_to_grade entry types | as above, `i2g_rules_v1.py` | TT = taker in and out. RT = resting entry at the decision price, filled only on a trade-through within 60 s, taker out. RR = resting entry and resting target, taker stop and time exit. Resting leg = 1.5 bp fee plus half the gap. | Signed with V3.1 | **Yes**: the rulebook names TT, RT or RR, and the loop tries all three |
| maker_fill | `team/RESEARCH/tools/maker_fill/` | Limit entry grid: 6 distances x 5 placing delays x 3 waits. Gives fill share, time to fill, gain against taker, and the move missed after no fill. | Research desk tool (SCOUT, QUANT). No release file, no signoff row. The "fall back to taker" half is not built. | Not in V1. Could be added after its release |
| entry_timing (T08) | `team/RESEARCH/tools/entry_timing/` | First second after a fire when an entry trigger turns true | Architecture and tests only, no release | Not in V1 |

## 3. Exits

| Tool | Path | What it does | Status | Use in V1 |
|---|---|---|---|---|
| idea_to_grade exits | `i2g_rules_v1.py` EXITS | Eight fixed exits: V1 and V2 vol barriers (1x and 2x the 5 min volatility) with 15 min, 1 h and 4 h limits, plus +2c before -1c in 1 h and +4c before -2c in 4 h | Signed with V3.1 | **Yes**: the rulebook names one id, and the loop tries them |
| exit_engine | `team/RESEARCH/tools/exit_engine/` (registry `EXITS_V1.tsv`, settings `EXITS_ED2_CORE_V2.json`) | Any named exit on given trades: fixed take and stop (pct, c or vol1h), trails, ATR trails, time limits, exit on the next or an opposite alarm | ED2.1 READY FROZEN (row 72), with an independent oracle at zero differences | V1.1 option. Its `nm` unit is only stored for the old liquidation alarm, so on the new alarms only the pct, c, vol1h and atr5m exits apply. It also needs a trade list with entry prices. |

## 4. Cost

| Tool | Path | What it does | Status | Use in V1 |
|---|---|---|---|---|
| COSTS_PER_COIN_V1 (inside idea_to_grade) | pinned by V3.1 | Round trip c per coin, plus the honest gap 0.032 or the stress gap 0.144 | Signed with V3.1 | **Yes**, through the grader |
| costs_v2 (T04, cost of record) | `team/LAYERS/tools/costs_v2/` | Fee plus book walk per coin and hour, plus gap and HL funding | V3_5 CLEARED_FOR_USE (row 68). V3_8 frozen and waiting for signs. | Not directly. It is the factory's and exit_engine's cost. |
| costs_r7, hl_books | `team/RESEARCH/tools/` | Older cost studies (Binance per hour, HL books) | Drafts | No |

## 5. Decision tools (old)

| Tool | Status | Use |
|---|---|---|
| event_decisions V3.2 + factory_dec_adapter CANDIDATE_3 | CANDIDATE, reads Situations and Cause V4.3 names that no longer exist | Reuse the idea only (ordered lines, UNKNOWN means no trade) |
| decisions (T07) | Never built | None |
| strategy_book | DRAFT (QUANT) | None |

## 6. Inputs V1 reads (all frozen and signed)
- Fires: `team/RESEARCH/LIBRARY/UNIVERSE_ALARMS_V1.tsv` 13c4722a (18,740 fires, wave weights).
- Context V4.1 cards: `team/RESEARCH/LIBRARY/context_split/runs_v41/commit_974f4eeb79487e91/STATE_CARDS_<alarm>_V41.tsv` (row 76).
- Profile V5.1 cards: `<SCRATCH>/work_PROFLIB/cards_v5_1/{a,b,c}/CARDS_<alarm>.tsv` (rows 77-78).
- Pre-move V1.2 cards: `team/RESEARCH/LIBRARY/cause_lib/run_v1_2/PMM_<alarm>.tsv` (rows 79-80).

## 7. How V1 plugs in
1. **decide_v1** (new and small) reads the fires and the 3 cards and applies the rulebook: data gate, regime gate, side, at most 3 skip lines. It writes DECISIONS.tsv plus TAKE and SKIP lists in the grader's event format. It never reads a price.
2. The rulebook's entry and exit are **only names of existing tool settings**: an idea_to_grade entry type (TT, RT or RR) and exit id, or UNSET. Nothing is defaulted to resting. A small `LAB_TOOLS_V1.json` lists the allowed ids, each with its release sha16, so a rulebook cannot name something the lab does not have.
3. **idea_to_grade V3.1** grades the TAKE list (and the SKIP list, and all fires) with `--events-subset --universe UNIVERSE_ALARMS_V1.tsv`, under a PREREG ledger row. It gives every entry type, exit and both sides, after cost, against the tough baseline, by wave and month.
4. The loop reads those grade tables and keeps, per alarm, the entry, exit and skip lines that pay after cost on Sep to Dec, then one look at Jan to Feb. Nothing in money is computed in the decision tool.
