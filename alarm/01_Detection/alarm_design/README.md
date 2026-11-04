# tools/alarm_design: one tool to define an alarm and prove it is what it claims (BUILT; current code alarm_design_v2.py; sections 1-8 are the V1 design, kept as history: their dates and the April seal are NOT authorization, see 'V3 contract' at the end)

Owner seat: ALARM. Reviewers: STRATEGY (LEAD) and LAB1, BEFORE it scores anything. Built to RESEARCH/KNOWLEDGE/TOOL_DESIGN_V2.md and
the volat-alarm-design skill (QUANT method v3). Status: DESIGN, no code yet, no data read.

## 1. Design note (TOOL_DESIGN_V2 section 1)
1. QUESTION: for an alarm written as a DEFINITION file, when does it fire on Sep 2025 to Mar 2026, and does the forced event it claims
   happen more after its fires than after FAIR comparison moments that share every condition except the claimed one?
2. UNIT: one row = one fire (or one comparison moment) x one truth horizon. Fires and comparison moments are twin parts.
3. KNOWN AT: a fire at t uses only values with known_at <= t (lab3 C1 as-of rule). Every own-history threshold is taken from days BEFORE
   the fire day (walk-forward by construction). A truth row is known at t + its horizon end; it is never an input to anything.
4. INPUTS: lab_days through lab3 Days(root, 'research') (refuses 20260401 on); stored event lists (A01 onsets, A02N, D-WAVE, D-HL, EXH,
   their EVENTS tsv); hl_oi_2025 and oi6_2025 only when a definition names them. SETTINGS: the definition file (section 2).
5. NOT IN IT: no prices after a fire, no money, no costs. The AHEAD grade stays in alarm_stamp + offer_ladder_v1; context and profile
   stay in alarm_context and alarm_profile. This tool hands them the fire list (EVENTS tsv) and its comparison list.

## 2. The definition (one JSON file per alarm, frozen with its sha16 and a `date -u` board line BEFORE any data is read)
File: team/RESEARCH/ALARM/defs/<ID>_DEF_V<n>.json. The tool adapts to each alarm through this file only; a new alarm never needs code.
```
id, version, claim {who_forced, must_do, why_ahead, side_meaning}, window {first, last}  (last <= 20260331, refused after)
grid_s            5 or 60: the step the alarm is checked on
inputs            named series, each = {code: <lab code from METRICS_V1>, op: <one op from the registry>, args}
conditions        list of {name, test: [input, '>=' | '<=' | '>' | '<' | 'sign==', value or input], role: 'shared' | 'claim'}
fire              {onset: true (first step all conditions hold after a step they did not), refractory_s, side: <input or rule>}
truth             list of labels, each {kind: <one label from the registry>, start_s, end_s, side: 'same' | 'other', args}
base              {match_on: [inputs, each with a tolerance in quantile bins], scope: 'coin-month' | 'coin-day', k: 5, seed}
lead_vs           optional event list the alarm must beat in time (N2: A01), reported in seconds
overlap_with      event lists to report overlap and lift against (A01, A02N, DWAVE, DHL, EXH by default)
```
- Op registry (fixed, tested once, reused by every alarm): `raw`, `sum(w)`, `change(w)`, `ratio(a,b)`, `abs`, `sign`, `accel(n)` (n
  rising bins in a row), `own_pct(q, days=14)` (the coin's own q-th percentile over the 14 built days before D, as onset_band_v6 does),
  `edge(h)` (distance to the h-hour high or low in the coin's normal move), `max(w)`, `min(w)`, `since(event)`, `market(code)`.
- Label registry (no price inside any of them): `forced_usd` (same- or other-side liquidation USD in (t+start, t+end] over the coin's
  own normal of that window), `event_within` (an event list, e.g. A01 onsets that way, starting AFTER start_s so the fire's own prints are
  never its label), `oi_unwind` (E2 OI change), `hl_forced` (HL fills; only where stored). A label always starts after the fire's own
  seconds: start_s >= the longest window any condition reads.
- New ops or labels are added as registered blocks with their own planted test, never by editing an alarm's code path.

## 3. The fair comparison base (the core of "is it what it claims")
- Candidate moments: every grid step of the same coin in the same scope where ALL `shared` conditions hold and the `claim` condition
  FAILS, refractory and onset applied the same way. So a base moment is the same kind of moment in every way except the claimed one
  (QUANT's B3 v2 lesson: the base must share the edge, the size, the flow).
- Matching: for each fire, k moments matched on the definition's `match_on` inputs (e.g. first-print size AND the coin-hour's activity
  for N2), nearest in quantile bins, fixed seed, no reuse of a moment for two fires of the same wave.
- If a fire has no fair partner it is reported as UNMATCHED (count and share), never silently dropped.
- Beside it, for reading only: a plain busy base (matched_controls_v1) so the gap between "busy" and "fair" is shown, as B3 v2 did.

## 4. Outputs
- Values in the one format (TOOL_DESIGN_V2 section 3): research_days parts `ADES.<ID>` (fires) and `ADES.<ID>_MATCH` (fair moments),
  ROWS kind, one row per fire x label: label value, inputs at the fire, wave id, episode id, matched-set id. Catalog ADES_CATALOG_V1.tsv.
- `<ID>_EVENTS.tsv` and `<ID>_MATCH_EVENTS.tsv` in the EVENTS format, so alarm_stamp / alarm_context / alarm_profile can be run on them
  unchanged (each subject line added to their SUBJECTS with a twin and LAB1's review, as LAB1 ruled 21:33Z).
- The TRUTH CARD (text, receipt only), per month Sep to Mar, plus pooled, plus ex 10-11 Oct and ex the 5 best days:
  - counts: fires, coins, days, fires per coin-day, waves (any coin within 30 min), same-coin episodes, unmatched share;
  - label share fires vs fair base, the difference, a 95 pct interval by WAVE bootstrap, a p by WAVE-level shuffle of fire vs base
    labels inside matched sets (2,000 draws, seed fixed);
  - every horizon in the definition side by side (e.g. N1: 10 s, 60 s, 2 min; latency rule: the share that lands after +10 s);
  - lead over `lead_vs` (median and quartiles of seconds before the reference event; the share leading by more than 6 s);
  - overlap with the other alarms and the lift without the overlap;
  - the walk-forward view: the same table month by month in time order, each month judged with nothing tuned on it.
- No fixed minimum sample: small counts are shown with their wide interval and the verdict says how sure we are, in words.
- Verdict line per method v3 section 3: TRUE / NOT TRUE / UNSURE (interval crosses the line), with the reason.

## 5. Safety and running
- Seal: refuses any day >= 20260401 itself (a second guard beside lab3's), test included.
- CPU: one process per month, at most 3 at once (xargs -P 3, checked with ps), nice 10; refuses to start 23:50 to 00:15Z.
- Never writes over a part (lab3's Duplicate refusal); a rerun is a new version id.

## 6. Tests before any real read (TOOL_DESIGN_V2 section 6)
- planted series: onset, refractory across midnight, side, accel op, own_pct uses only earlier days;
- prefix test: cutting all data after t never changes a fire at t (no look-ahead);
- the base never contains a moment where the claim condition holds, and always holds every shared condition;
- a label never counts the fire's own seconds (start_s rule);
- sign plant: a down push planted as up must flip the side and the label (sign_plant_test_v1 pattern);
- mutants: dropping the claim condition from the base split, or moving start_s to 0, must FAIL a test;
- seal: a 20260401 day is refused.

## 7. Proof runs, in order (LEAD 06:00:39Z)
1. R-B4 takers into the crowd (card cadc5ad9, known answer on 12-31 Oct: 21 fires, +0.028 vs busy): the tool must reproduce B4's fires
   on 12-31 Oct before running 10 Oct 2025 to 31 Mar 2026 with the fair base.
2. N2 early onset (first new idea), with LEAD's four conditions: USD not counts plus X1.LIQX.S02, label starts after the onset seconds,
   base matched on first-print size AND coin-hour activity, lead over A01 reported (under 6 s adds nothing).
Then N1, N3, N4, N5, N6, R-B5 one after another, each with a definition file and an alarm card, pass or fail.

## 8. Inputs checked on 23 Oct (ALARM, read only, one day each of Sep, Oct, Feb, Mar)
A1.S01/S02 (5 s, about 100 pct filled), X1.LIQX.S02 (5 s), E2.S02 (60 s), E3.S01 (60 s), X1.POSX.S06 (5 s), POSX.S12/S03 (60 s, empty
before October: 30-day history), X1.FLOWX.S01/S10 (5 s, empty before 10 Oct, about 75 to 85 pct filled after). A01 onsets for Jan to Mar:
QUANT's producer run (QUANT 05:59:45Z plan), else the existing finder tools/alarms/a01_onset_v2.py (a COMPUTE line first).

## V2 (alarm_design_v2.py, 23 Oct 2026 afternoon; v1 kept unchanged for its receipts)
- OUTSIDE D05: a refused (sealed) day raises PermissionError and stops the run, named (D05-01); grid_s must be a positive int multiple of 5
  (D05-02). The outside suite tests/grading/test_d05.py pointed at v2: 8 of 8.
- OUTSIDE S06 (matched base), applied to this tool:
  - estimand on every card: ALARM-TIME CONDITIONAL PREDICTION, not a causal effect (rule 1);
  - a fair-base moment is excluded only within the refractory AFTER a PAST fire of its coin (a later fire never removes it) (rule 2);
  - nothing is read after the run's last day (Ctx.read_last): a label crossing it is NOT KNOWN, an event list is cut there (rule 2);
  - base sides come from the same side rule at the base moment, never borrowed from the fire (rule 5);
  - fire rows carry match_code (0 matched, 1 no pool, 2 no exact key, 3 outside caliper, 4 taken) and pool_n; the RUN receipt carries
    balance (standardised mean gap before / after matching per key) and common support (rule 4);
  - the busy base (matched_controls_v1, QUANT's) still excludes alarms on both sides, so it is named a RETROSPECTIVE QUIET REFERENCE
    and is never the verdict; alarm_match V3 (QUANT) will replace it.
- Tests: test_alarm_design_v2.py (29), mutants_alarm_design_v2.py (16 of 16 KILLED).
- Card: month rows and the verdict read BUILD months only from a windows settings file (ALARM/settings/WINDOWS_V1.json); CHECK months are
  never opened by this tool.

## V3 contract (OUTSIDE S07, all accepted; binds over sections 1-8 where they differ)
1. Windows: this README authorizes nothing. Every run resolves its dates and label horizons through CHECK_WINDOW_RULE_V3 + RUN_GATE_V1
   (STRATEGY GO) and lab3/law.py; cards read BUILD months only through a windows settings file; nothing is read after the run's last day.
   Sections 1-8 mention 20260401 and Mar proof runs: history only.
2. Typed claims: every definition carries claim.type (DETECT an event already happening / PREDICT a future event / CONTINUATION of the
   same episode) and claim.footprint_s, frozen before any read; load_def refuses a definition without them (test + mutant). The card
   names them. Verdicts: TRUE_FOR_REFERENCE (the label only; a mechanism claim needs attribution evidence), NOT_SUPPORTED (only when the
   interval is precise and under the frozen min_effect), UNSURE (wide: gather more, never a kill). No-price labels are named with their
   limits (A1 = AT LEAST; OI falling does not certify forced closing).
3. Four intervals on every card: the conditions' fitting windows (e.g. 14-day own band), the trigger footprint (claim.footprint_s), the
   decision t and arrival t + 6 s, the label (t + start, t + end]. Section 2's 'start_s >= the longest condition window' is WITHDRAWN
   (LEAD 06:04:23Z change 2): labels start after t and exclude the fire's own row; a fitting window never moves the label.
4. Selection family: every scored definition version is a TRIES_LEDGER row (ledger_add_v5 prereg) before its read; the card prints the
   family's try count. The wave sign-flip null assumes a symmetric fire-minus-matched gap under no effect; until the synthetic
   calibration (skewed, persistent, reused-control nulls) is run, p values are marked UNCALIBRATED.
5. Rivals: a fixed preregistered all-fire policy is allowed as a benchmark only (RULE ZERO stands for search); overlap with existing
   alarms is reported with the added detection beyond them, apart from any money.

## V3 contract additions (23 Oct evening)
- ONE tries ledger: `card` reads team/RESEARCH/TRIES_LEDGER_V1.tsv (ledger_add_v5) and refuses unless a PREREG row carries the sha16 of the
  run settings file, and that file names this definition's sha16; the RESULT row is added with `ledger_add_v5 result`. TRY_LEDGER.tsv
  (the tool's own file until now) is history only.
- Null calibration (S07-04): null_calibration_v1.py, synthetic symmetric / skewed / persistent / reused-base nulls; receipt
  ALARM/receipts/null_cal/NULL_CAL_V1.txt: false-positive rates inside their Monte Carlo bands at 400 trials. Not covered: fires sitting in
  other regimes than their base (a matching question, handled by the fair base and the balance lines).

## V3.8.1: known-false shared onset predecessor
A shared condition that is known false now makes the row decided OFF even when the claim is unknown or its trailing-percentile
calculation was skipped. This fixes A54-FINAL-01 (real BTC onset 2025-10-10 14:58:00). Otherwise the existing shared-known/claim-decided
contract is unchanged; truly unknown predecessors still suppress onsets. Definitions and schemas are unchanged. Rerun affected
definitions to recover omitted events; existing stored outputs remain historical. The shared implementation is alarm_design_v2.py;
RELEASE_alarm_design_V3_8_1.json pins this repair and test_onset_knownness.py. It is consumed by idea_to_grade V2.3.1.
The independent closure evidence is team/OUTSIDE/A54/i2g_review_v1/repair_v23/CLOSURE.md (relative to forensics).
BASE and GRID both call the shared conditions_known helper; the fast detector must not maintain a different knownness formula.
