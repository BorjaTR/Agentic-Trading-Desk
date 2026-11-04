# idea_to_grade V3.1 (ALARMLIB seat, 25 Oct 2026): the alarm-library fixes inside the grading tool

Owner 25 Oct: stop the alarm library as a separate project; alarms stay idea -> detector -> grading tool; move the useful fixes into the
grading tool and keep it generic for any alarm, any coin, any day range. V3 is NEW files beside V2.3.1; V2.3.1's files are unchanged and
still run on I2G_PINS_V2.json. V3.1 = V3 plus the six fixes and two follow-ups of the independent review
(team/OUTSIDE/DATA/REVIEW_IDEA_TO_GRADE_V3_INDEP.md, re-review REVIEW_IDEA_TO_GRADE_V3_1_INDEP.md).

| file | role |
|---|---|
| idea_to_grade_v3.py | the V3.1 command (same inputs as V2: --idea or --events, roster, coins, days, research window) |
| i2g_engine_v3.py | per coin: the V2 engine imported unchanged, plus as-of controls, side ids, the delay setting, the tough pool, the V3 columns |
| i2g_rules_v1.py | the rules, pure and tested (no path, alarm, coin or date) |
| alarm_contract_v1.py | the ONE shared copy of the as-of rule, the cluster chain, the same-bin rule and the trade-through rule (also used by team/RESEARCH/LIBRARY/alarm_library/alarm_core_v1_2.py) |
| i2g_grade3.py | the V3 tables (grade3/TABLE.tsv, WEIGHTS.tsv, REPORT3.md) |
| i2g_universe_v1.py | builds ONE frozen cluster universe from whole fire lists, before any grading run |
| release_pins_v3.py | writes the pins file (I2G_PINS_V3_1.json) |
| test_i2g_v3.py, mutants_i2g_v3.py | pure tests (01-21; 13-21 are the V3.1 fixes and fail on the V3 candidate) and 40 mutants |
| test_i2g_v3_real.py | real-data tests on the Mac (R0-R8): V2 compatibility, as-of controls and tough moments re-derived, delay moves the fill, a second alarm on other coins and days, ledger refusal, a buy and a sell in one second, one ask one run, alarm id refusals, the real frozen universe passes the row check |
| full_population_v3_1.sh | the full-population run of one stored alarm list (review gates G1, G2) |

What changed against V2.3.1
1. Matched controls AS-OF: a control is dropped only when an alarm or parent of its coin lies in [t - 4 h, t] (closed at t: a same-second
   fire makes the moment busy). V2's rule (draw_v3.own_flag) also dropped a control that lies before its own parent, using a later event;
   it stays in every edge (EDGES.tsv column own_v2) and in the CALM_V2_EDGE sensitivity rows only.
2. Each event counted once: weights come from a frozen universe (--universe U.tsv --alarm-id ID): clusters per alarm over its whole fire
   list (30 min gap, a cluster never spans more than 4 h: the chain is split and flagged CHAIN_SPLIT), weight 1 / size. A month, coin or
   filter slice reads them; nothing is rebuilt. Without --universe the run builds RUN_LOCAL clusters and is TEST only.
3. Event identity: parent id = coin_second_side (BTC_1760000000_+1). Two opposite-side fires in one second are two events (also in the
   event list reader). The matcher's random stream stays the moment's, so both sides draw the same controls.
4. TOUGH baseline (a V3 definition, not the context library's move x volatility cell): per parent up to 10 same-coin moments (60 s grid,
   the matcher's +-7 day domain, same split part, as-of eligible) whose 15 min move signed by the parent's side is within max(0.5 c, 25%)
   of the parent's and whose 5 min realized volatility is within 0.8-1.25 x; seeded by (seed, parent id); measured by the same path as the
   parent. Parents with fewer than 3 known tough moments drop from TOUGH rows only (the share covered is printed).
5. One fixed grid for every alarm: returns 10 s, 1 min, 5 min, 15 min, 1 h, 4 h after the taker fill; eight exits (1x and 2x the row's own
   5 min volatility with 15 min / 1 h / 4 h limits, +2c before -1c in 1 h, +4c before -2c in 4 h); target and stop inside one 3 s bin
   count as the stop; a stop pays the worse of its level and the bin's close; an exit past the known path is unknown, never a time exit.
   The volatility unit is the row's OWN realized volatility from its 3 s bins over the 5 min up to its clock (not the context library's
   coin_vol_5m); the same rule for alarm, control and tough rows.
6. Entry types and costs: TT taker in and out (round trip = c = cost_bp of COSTS_PER_COIN_V1 + gap); RT resting entry at the decision
   price, filled only on a strict trade-through within 60 s, taker out; RR resting entry and resting target (trade-through), taker stop and
   time exit. Resting leg = 1.5 bp fee + half the gap. Honest gap 0.032, stress 0.144, and GROSS. Costs are ONE STATIC number per coin
   (the cost table), not a cost as of the entry time. Fill share and the TT result of the missed trades are shown.
7. --delay-s is required (the measured live delay, or 6 to compare with V2). The fill, the clocks and the known_at follow it.
8. --ledger-ask is required (see V3.1 below).
9. --compat-v2: V2 eligibility, V2 ids, V2 waves, no tough pool. Its V2 files must equal V2.3.1's on the same events (a compatibility check,
   not proof).

V3.1 (review fixes)
- F1 feed holes: a price is known at x only when a bin's last trade lies in [x - 60 s, x] (MAX_STALE_S 60). A horizon return whose end
  price is stale is unknown (NaN). An exit that walks across a gap of more than 60 s between trades, or whose time exit price is stale, is
  unknown with code PATH_HOLE (5). The column path_holes counts the unknown values of each row; REPORT3 prints the rows with a hole.
  A hole earlier in the path does not null a horizon return whose end price is fresh (that price is known).
- F2 the universe is checked: the header must name this code's 30 min gap and 4 h span, and every row must equal the clusters rebuilt
  from the file's own fires (ids, weights 1 / size, sizes, flags, no fire twice). The sha16 of the universe, the cost table and the
  registry are taken at admission and rechecked before commit (UNIVERSE_CHANGED, COSTS_CHANGED, REGISTRY_CHANGED). RUN.json records the
  alarm's source line of the universe.
- F3 the ledger counts tries: the PREREG row's idea must equal --alarm-id and its days_from / days_to must equal --first / --last (blank
  days refused). One ask admits ONE complete run: a claim file I2G_RUN_CLAIMS/<ask>.json is created beside the ledger at commit (a second
  run is refused LEDGER_ASK_USED; a failed commit renames the claim .failed_<utc>). The ledger itself is only read.
- run_class: GRADED only with the canonical TRIES_LEDGER_V1 and ALARM_REGISTRY_V1, a --universe, no --compat-v2 and no reused detection;
  every other run is TEST (RUN.json run_class, REPORT3 line 1). A GRADED run needs a PREREG row in the real ledger (ledger_add_v6.py).
- F4 the 15 min move is signed per row by its own parent side (one measurement serves +1 FADE and -1 FOLLOW).
- F5 --alarm-id is required and must be a registry id (--registry, default ALARM_REGISTRY_V1); an --idea must be the registered definition
  (sha16); an --events list graded with a universe must be that alarm's source list (sha16), or be declared a slice with --events-subset
  (every event must then be in the alarm's universe).
- F6 one copy of the shared rules: alarm_contract_v1.py.
- Event list reader: load_events_v3 runs V2.3.1's row checks with the identity coin, second AND side (a buy and a sell in one second kept).
- NO_COST: a coin without a cost of record does not stop the run; its parents are graded before cost only (GROSS rows), are absent from
  HONEST and STRESS, get no tough pool (TOUGH_NO_COST: the tolerance needs c), and are listed in grade3/NO_COST.tsv and RUN.json counts.
- Chain-split sensitivity: REPORT3 prints how much the 95% half-widths of the ALL rows move when every split chain is merged back into one
  cluster (weights unchanged).

Statistic: per slice (ALL and each month) the weighted mean with frozen weights and a 95% interval with the cluster as the unit.
Outputs added to a run: matches/TOUGH.tsv, matches/TOUGH_CENSUS.tsv, measurements/VALUES3.npy, measurements/NAMES3.json,
grade3/TABLE.tsv, grade3/WEIGHTS.tsv, grade3/REPORT3.md, grade3/NO_COST.tsv (RUN schema I2G_RUN_V3_1).

Command:
  nice -n 10 $PY -B $T/idea_to_grade_v3.py --events <list> --events-sha16 <sha> --roster <ROSTER_BUILD.json> [--coins A,B] --first D1
    --last D2 --research-window FIRST:LAST --out <new folder> --delay-s <s> --ledger-ask <PREREG id> --alarm-id <registry id>
    --universe <U.tsv> [--events-subset] [--workers 2]
  python3 -B $T/i2g_universe_v1.py <new U.tsv> ID1=<fire list> ID2=<fire list> ...
  bash $T/full_population_v3_1.sh <registry id> <stored EVENTS.tsv>      (whole roster, Sep-Dec 2025, scratch ledger: TEST)

Range notes. From V2, kept for compatibility: a parent is graded only when the matcher's +-7 candidate days, each fully known, lie inside
--first..--last; a range shorter than about 15 days grades nothing, and parents in the first and last week of a range are recorded as
COMPARISON_UNAVAILABLE (never hidden). Pick ranges with a week of margin on each side. Forward support: a parent on --last reads the path
of the next day (up to its 4 h hold), which must lie inside --research-window (not inside --first..--last).

Speed and memory (review gate G2, measured by the independent reviewer on the Mac, 25 Oct 21:43Z): ALM_M_V1 stored list, all 52 roster
coins, 1 Sep - 31 Dec 2025, 10,764 parents, 2 workers, nice 10: 381.9 s wall, tree peak 4.37 GB sampled, largest worker 1.78 GB RSS
(budget 7,200 s, 16 GiB). Phases: match and measure 321 s, grade3 47 s, grade 9 s, aggregate 3 s.

Release: RELEASE_idea_to_grade_V3_1.json, pins I2G_PINS_V3_1.json (08a0c72015d4ca6e, 45 files), frozen universe
team/RESEARCH/LIBRARY/UNIVERSE_ALARMS_V1.tsv (13c4722a5f5ab86b: 18,740 fires of ALM_C_V1, ALM_M_V1, ALM_H0_V1, ALM_S2B0_V1, ALM_S2R1_V1,
ALM_S3W_V1, 10 Sep - 31 Dec 2025; 4,819 clusters, 9 chain splits), registry team/RESEARCH/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv.
Tests: pure 25/25, mutants 40/40, real data 13/13 on the Mac, full population COMPLETE and verified. Logs: V3_1_LOGS/.
Open, not blocking: a full-population run of a second alarm (D3); an operator other than the builder running from this README (J2).
