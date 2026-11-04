# factory: ARCHITECTURE V1 (V4.2 step 2; owner STRATEGY/LEAD; builder BUILD4 (started 14:16Z); tester TEST1;
# reviewers QUANT, SCOUT (panel) + LAB1; outside OX-SKEPTIC + OX-CODE1; paper only)
Research: RESEARCH_FACTORY.md. Plan: LEAD/STRATEGY_FACTORY_V1.md.

## 1. Design note
1. QUESTION: for a frozen batch of strategy cards of one alarm family, what does each card earn per trade and per wave on BUILD months after
   full cost, against its rivals, and which cards clear the fairness bar computed over the whole batch?
2. UNIT: one row = one card x one fire (trade or skip, with reason); one batch receipt per run.
3. KNOWN AT: every decision input is joined with labcore.join_guard at the card's decision time; outcomes only through labcore.gates on BUILD
   months (embargo applied); nothing after a trade's exit time is used for that trade.
4. INPUTS: the batch PREREG file (json, sha16, ledger PREREG row); the fire list of record (alarm card by sha16); stored EPI/CTX/CAUSE rows
   through their readers; prices through labcore.prices; exits through exit_engine.run_frozen; cost through labcore.costs; waves through
   labcore.waves; the bar through fairness_bar.
5. NOT IN IT: no new label, no new reading, no exit or cost logic of its own, no choice of survivors by hand, no CHECK or BLIND read
   (that is freeze_judge's open), no order code.

## 2. Commands
- `generate <prereg.json>`: validates the PREREG (every input briefed via labcore.briefs; STOP refused; CAUTION never in a decision; causes
  only at the status the use needs; exit rows and cost table by sha16; rivals present; windows BUILD only), expands it into cards
  (STRATEGY_CARD_V1, freeze_judge schema), writes cards/<batch_sha16>/ and a ledger row per card (ledger_add_v5); refuses a batch whose card
  count exceeds the PREREG's stated budget.
- `run <batch_sha16>`: runs every card and rival; writes TRADES.<card> parts (lab3.write: as_of, known_at, entry/exit times, booking and
  path_evidence status, net after cost, wave, month) and BATCH_<sha16>.tsv (per card: trades, waves, eligible / skipped / EMBARGO /
  UNDECIDED / NOPRICE counts, net per trade and per wave with whole-wave interval, per month, T02 bar line, verdict CLEARS / FAILS /
  INCOMPLETE / UNRELIABLE). Survivors are only the cards whose line says CLEARS.
- `sheet <batch_sha16>`: the one page for the owner (plain words: what was tried, how many, what cleared, money per trade and per month).

## 3. Data (0c) and reuse (0d)
| value | already computed? where | reader |
|---|---|---|
| fires | the alarm's list of record (A02N/A02P card sha16) | the alarm tool's list reader |
| profile, context, causes | research_days EPI/CTX/CAUSE parts | alarm_profile.read, alarm_context.read, cause_label.read |
| prices | lab_days PRICE | labcore.prices.PriceCache |
| exits | exit_engine.run_frozen | (library) |
| cost, funding | labcore.costs V2 | (library) |
| waves, bootstrap | labcore.waves | (library) |
| bar | fairness_bar V2 bar() | (library) |
New computation: only the per-card trade assembly and the batch receipt. Release: RELEASE_factory_V1.json pins every module it imports.

## 4. Tests (written first by TEST1; plants; seconds)
planted batch with a known edge clears and a planted null fails; a card reading a future value is refused (join guard); a fire in Mar-May
refused; an embargoed fire never scored; rivals present or refused; batch sha16 changes when any card changes; survivors = CLEARS only;
determinism (two runs, same sha16s); the bar counts every card of the batch (a mutant that counts only survivors must fail).

## 5. Proof of meaning (PROOF_FACTORY_V1.tsv; bars set now)
| item | claims | proof | bar |
|---|---|---|---|
| net per trade | money after full cost | equals exit_engine + costs on planted cards, one real card hand-checked | exact |
| CLEARS | beats the batch's bar | planted edge clears, planted null fails at the stated rate in 200 synthetic nulls | false-clear rate <= the bar's alpha |
| rivals | same events, costs, capital | event sets equal by sha16 | exact |
| speed | a batch of 50 cards over BUILD in minutes | timed by TEST1 on the real store | under 10 min on 3 processes |

## 6. Run 0
Batch 0 = A02P: NO TRADE, ALARM-ONLY FADE, ALARM-ONLY FOLLOW, entry fire + 6 s taker, exit EXIT_T1, cost V2, BUILD months (FIRST_MONEY_TEST_V1).

## factory_v2 (BUILD3, 23 Oct 2026; STRATEGY-210500, the 4 rulings of STRATEGY 20:58:51Z) = the tool of record, RELEASE_factory_V1.json
- Cost of record: PREREG `cost` = {settings, settings_sha16, record, record_sha16} (costs_v3, COSTS_SETTINGS_V1.json); each trade costs
  fee + book + gap + HL funding over the hold. Funding missing for a traded fire caps the batch at INCOMPLETE (counted in `funding_missing`).
- SIGN: FADE trades against the push (a down push is faded with a BUY). Test F4 and mutant M1.
- MATCHED rival: PREREG `matched` = {path, sha16} of alarm_match NOOWN edges. Every non-NO_TRADE card is run on its fires' matched moments
  (weight-averaged per fire); it clears only if the per-wave gain over that twin has a 90 pct whole-wave lower bound above 0
  (`matched_gain_lo`). The twin is a rival, never a counted try.
- Entries: taker only; a triggered entry needs T08 RANDOM_DELAY first (refused).
- Tests: `python3 -B tests/test_factory_v2.py` (analyst venv): 12 tests + 5 mutants. No real-data money run until the reviews pass.
- LAB1 21:19:21Z MUSTs (RELEASE_factory_V2): (1) every card's trades replay in time order through T13's entry cap and T09's risk limits
  (PREREG `limits` = T09 and T13 module files pinned by sha16, or a STRATEGY deferral ruling); capped or refused entries are MISSED rows
  (net 0, would-be path and reason in MISSED_<card>.tsv), counted on the batch and the sheet. (2) fire times and edge parent times must be
  whole seconds (a fraction is refused). (3) matched moments use their own unit known at their own time (`matched_units_fn`); a unit exit
  without one is refused. T09 and T13 exist as designs only today: run 0 needs them built, or STRATEGY's deferral.
- STRATEGY 21:22:39Z deferral (RELEASE_factory_V3): while T09 and T13 are not built, a BUILD research batch may name
  `limits: {deferred: <ruling>}`; every trade then carries `open_at_entry` and `coin_open_usd` (TRADES part), every result row has
  `limits = risk limits not replayed` and `max_open_at_entry`, and the sheet says so. No CHECK look and no paper use until run 0 is
  replayed through the real T09 and T13.
