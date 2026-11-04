# [i2g_engine_v3_2_s2_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026;
# the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only"). Old file: i2g_engine_v3_2_s2.py
# daacdf249ff0f9cc, never edited. Changed: it imports i2g_engine_rel1 in place of i2g_engine. rel1 = release edition 1: the files of one
# chain that run from the Alarm release folder; no value, rule or output format changes. The rest of this text is its text.]
# [speed twin S2 of i2g_engine_v3_2.py (signed, kept unchanged), grader thread, 26 Oct 2026, TEST: written by make_engine_s2.py from that file
# with two changes, each proved byte-equal: (1) the V3 path columns come from i2g_rules_fast_v1.path_values_walk (every exit of a start in
# one pass, the same results bit for bit as i2g_rules_v1_2.path_values); (2) the as-of features of a day's observations are computed in one
# call per day (asof_features is per clock, so the values are the same). Everything else is the signed text. S2 = S1 with this header as
# comments (S1's header broke the file's own docstring).]
"""[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file i2g_engine_v3.py 69e17ed9e2350a66 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
i2g_engine_v3_2.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026): the per-coin work of idea_to_grade V3. It is the V2.3.1 engine
(i2g_engine.py, imported UNCHANGED: kernels, pins, PRICE reads, the matcher drive, the 55 STAMP fields) with five changes, each a task
setting (task['v3']); with task['v3'] = None this function returns exactly what i2g_engine.coin_job returns:
  1 eligibility 'asof'  a drawn control is eligible when no alarm or parent of the coin lies in [t - 4 h, t] (i2g_rules_v1_2.asof_flag);
                        the V2 rule (draw_v3.own_flag: also drops a control that lies BEFORE its own parent, a future exclusion) is kept
                        beside it in every edge for the sensitivity table; eligibility 'v2' grades with the V2 rule (compatibility)
  2 identity            parent ids carry the side (coin_t_+1); the matcher's random stream stays the moment's (coin_t), so both sides of one
                        second draw the same controls
  3 delay_s             the execution delay is a setting (alarm_stamp's 6 s was a constant of V2)
  4 tough pool          per parent up to 10 same-coin moments with a similar signed 15 min move and 5 min volatility (i2g_rules_v1_2.tough_pick),
                        measured exactly as the parent (kind 'tough')
  5 path values         per observation the V3 columns (i2g_rules_v1_2.value_names): fixed horizons, the fixed exit grid, the resting entry
No date, coin or alarm is held here: all of them come from the task."""
import os, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
import i2g_engine_rel1 as E2
import i2g_rules_v1_2 as RU
import i2g_rules_fast_v1 as RF

US = E2.US
K = E2.K
ms_us, day_of, shift, calendar, sha16, process_modules = E2.ms_us, E2.day_of, E2.shift, E2.calendar, E2.sha16, E2.process_modules
SourceChanged, price_state, ABSENT, index_sha16 = E2.SourceChanged, E2.price_state, E2.ABSENT, E2.index_sha16


def _grid(starts, grid_s):
    """the candidate grid of the tough pool: every grid_s-th second of the given days (moments without prices get no feature and drop)"""
    out = [np.arange(int(d0), int(d0) + 86400, grid_s, dtype=float) for d0 in starts]
    return np.concatenate(out) if out else np.zeros(0)


def fill_rows(idx, obs, values, values3, reasons, memo, measure, m15):
    """the measured rows of the observations idx. One measurement serves every observation with the same clock and TRADED side
    (measure(t_us, side, direction, traded) -> (V2 row, reasons, V3 row, UNSIGNED 15 min move)); such observations can belong to parents
    of either side (+1 FADE and -1 FOLLOW trade the same side), so the memo keeps the unsigned move and each row signs it by its own
    parent side (review F4)"""
    for i in idx:
        kind, t_us, side, d = obs[i]
        eff = (t_us, -side if d == 'FADE' else side)
        if eff not in memo:
            memo[eff] = measure(t_us, side, d, eff[1])
        row, why, row3, mv0 = memo[eff]
        values[i] = row; values3[i] = row3; values3[i, m15] = side * mv0
        if why:
            reasons[i] = dict(why)


def coin_job(task):
    """task: as i2g_engine.coin_job, plus v3 = None (exactly V2) or {eligibility 'asof'|'v2', identity 'side'|'v2', delay_s, tough bool,
    asof_before_s, c_pct (the coin's cost of record, pct)} -> the V2 result plus 'tough' [(pid, tough_t)], 'tough_census'
    [(pid, status, pool, chosen, move_pct, rv_pct)], 'values3' (rows x RU.value_names(), in 'obs' order)"""
    v3 = task.get('v3')
    if v3 is None:
        return E2.coin_job(task)
    t_start = time.perf_counter()
    k = K.load(); D = k.D; S = k.S
    coin = task['coin']; seed = int(task['seed']); s = dict(task['settings']); split = tuple(tuple(x) for x in task['split'])
    s['split'] = split
    delay = float(v3['delay_s']); before = float(v3.get('asof_before_s', RU.ASOF_BEFORE_S)); c_pct = float(v3['c_pct'])
    side_ids = v3.get('identity', 'side') == 'side'; mode = v3.get('eligibility', 'asof')
    if mode not in ('asof', 'v2'):
        raise ValueError('ELIGIBILITY %r' % mode)
    prices = E2.CoinPrices(task['lab_root'], coin, tuple(task['window']))
    known_days = set(task['known_days'])
    have = calendar(*task['window'])
    pid_of = (lambda t, sd: RU.parent_id(coin, t, sd)) if side_ids else (lambda t, sd: '%s_%d' % (coin, int(t)))
    # the draw sees the MOMENT id (its random stream); the parent keeps its own id
    tuples = sorted((float(t), int(sd), RU.moment_id(coin, t)) for t, sd in task['parents'])
    exclusions = D.exclusion_times(task['alarms'], [p[0] for p in tuples])
    busy = [float(x) for x in exclusions]
    edges, census, balance, unavailable, tough, tough_census = [], [], [], [], [], []
    missing_price = {}
    def no_price(d):
        if d not in missing_price:
            missing_price[d] = not prices.present(d)
        return missing_price[d]
    t_match = time.perf_counter()
    for part in sorted({D.part_of(t, split) for t, _, _ in tuples}, key=lambda x: (x is None, x)):
        if part is None:
            raise ValueError('PARENT_OUTSIDE_SPLIT %s' % coin)
        pts = [p for p in tuples if D.part_of(p[0], split) == part]
        days = D.days_for(have, [p[0] for p in pts], part, split, s)
        pdays = [d for d in days if not no_price(d)]
        ts, px = prices.match_arrays(pdays)
        ts.setflags(write=False); px.setflags(write=False)
        act = k.DP.PreparedPreActivity(ts, px)
        starts = [D._day_start(d) for d in days]
        lo, hi = {n: (x, y) for n, x, y in split}[part]
        if v3.get('tough'):
            gstarts = [D._day_start(d) for d in pdays if lo <= d <= hi]
            grid = _grid(gstarts, RU.TOUGH['grid_s'])
            inpart = np.array([D.part_of(g, split) == part and D.part_of(g + s['horizon_s'], split) == part for g in grid], bool) \
                if len(grid) else np.zeros(0, bool)
            grid = grid[inpart]
            g_mv, g_rv = RU.asof_features(ts, px, grid)
            g_ok = RU.asof_mask(grid, busy, before)
            p_mv, p_rv = RU.asof_features(ts, px, [p[0] for p in pts])
        for n_p, parent in enumerate(pts):
            t, side, mid = parent
            pid = pid_of(t, side)
            if D.part_of(t + s['horizon_s'], split) != part:
                e, c, b = k.DP.draw_coin(coin, [parent], exclusions, ts, px, starts, seed, s, activity=act)
                status_ok = True
            else:
                domain = [d for d in days if lo <= d <= hi and abs(D._day_start(d) - (t - t % 86400)) <= s['days'] * 86400]
                needed = set(domain) | {shift(d, -1) for d in domain}
                missing = ['PRICE:' + d for d in D.days_for(have, [t], part, split, s) if no_price(d)]
                missing += [d for d in sorted(needed) if d not in known_days]
                if missing:
                    e, c, b = [], [(mid, coin, t, side, 0, 'COMPARISON_UNAVAILABLE', float('nan'))], []
                    last_day = max(list(needed) + [d for d in D.days_for(have, [t], part, split, s)] + [day_of(t)])
                    unavailable.append({'fid': pid, 'reason': 'CONSERVATIVE_FULL_DAY_SUPPORT_OR_PRICE_COVERAGE_UNAVAILABLE', 'days': missing,
                                        'known_at_us': int(D._day_start(shift(last_day, 1))) * US})
                    status_ok = False
                else:
                    e, c, b = k.DP.draw_coin(coin, [parent], exclusions, ts, px, starts, seed, s, activity=act)
                    status_ok = True
            # the parent's own id in every row; each edge carries the graded flag, the V2 flag and the as-of flag
            c = [(pid,) + tuple(x[1:]) for x in c]
            for x in e:
                f2 = D.own_flag(x[2], x[3], s['horizon_s']); fa = RU.asof_flag(float(x[3]), busy, before)
                edges.append((pid,) + tuple(x[1:]) + ((fa if mode == 'asof' else f2), f2, fa))
            census += c; balance += b
            if v3.get('tough'):
                if not status_ok:
                    tough_census.append((pid, 'TOUGH_ABSTAINED', 0, 0, float(p_mv[n_p]), float(p_rv[n_p])))
                else:
                    near = np.abs((grid - grid % 86400) - (t - t % 86400)) <= RU.TOUGH['days'] * 86400   # the matcher's day domain
                    ch, st, pool = RU.tough_pick(pid, seed, side, float(p_mv[n_p]), float(p_rv[n_p]), c_pct, grid[near], g_mv[near], g_rv[near],
                                                 g_ok[near])
                    tough_census.append((pid, st, pool, len(ch), float(p_mv[n_p]), float(p_rv[n_p])))
                    tough += [(pid, g) for g in ch]
        del act
    t_measure = time.perf_counter()
    obs = []; values = None; values3 = None; reasons = {}
    if task.get('measure', True):
        seen = {}
        for pid, c_, t, side, n, status, cov0 in census:
            for d in ('FOLLOW', 'FADE'):
                key = ('parent', int(round(t)) * US, int(side), d)
                if key not in seen:
                    seen[key] = len(obs); obs.append(key)
        for e in edges:
            if (e[7] != '') if mode == 'v2' else (e[8] != '' and e[9] != ''):   # as-of grading also measures the V2 rule's controls
                continue
            ct = ms_us(e[3])
            for d in ('FOLLOW', 'FADE'):
                key = ('control', ct, int(e[4]), d)
                if key not in seen:
                    seen[key] = len(obs); obs.append(key)
        side_of = {}
        for pid, c_, t, side, *_ in census:
            side_of[pid] = int(side)
        for pid, g in tough:
            for d in ('FOLLOW', 'FADE'):
                key = ('tough', int(round(g)) * US, side_of[pid], d)
                if key not in seen:
                    seen[key] = len(obs); obs.append(key)
        names = S.NAMES; values = np.full((len(obs), len(names)), np.nan)
        names3 = RU.value_names(); values3 = np.full((len(obs), len(names3)), np.nan); m15 = names3.index('move15_pct')
        by_day = {}
        for i, (kind, t_us, side, d) in enumerate(obs):
            by_day.setdefault(day_of(t_us // US), []).append(i)
        memo = {}
        for day in sorted(by_day):
            pv, loaded = prices.view(day); tes = pv.te / 1e6
            tday = sorted({obs[i][1] for i in by_day[day]})
            fmv, frv = RU.asof_features(tes, pv.px, [t / US for t in tday])
            feats = {t: (fmv[q:q + 1], frv[q:q + 1]) for q, t in enumerate(tday)}
            def measure(t_us, side, d, traded, pv=pv, loaded=loaded, tes=tes, feats=feats):
                r = S.one_entry(pv, k.FV, k.LD, loaded, t_us / US, side, d, 0, delay, S.HOLD_S, entry_projection='stamp')
                row = np.array([np.nan if r[nm][0] is None else r[nm][0] for nm in names], float)
                why = {nm: r[nm][1] for nm in names if r[nm][1]}
                t_dec = t_us + int(round(delay * US))
                f = k.FV.fill(pv, t_dec, traded, 'taker')
                taker = (f.status, getattr(f, 'i', None), getattr(f, 't_us', None), getattr(f, 'px', None))
                kend = RU.known_end_us(loaded, (f.t_us if f.status == 'FILLED' else t_dec), day_of, shift, D._day_start)
                mv, rv = feats[t_us]
                row3 = RF.path_values_walk(pv.tl, pv.px, pv.hi, pv.lo, taker, t_dec, traded, kend, np.nan, float(rv[0]), c_pct)
                return row, why, row3, float(mv[0])
            fill_rows(by_day[day], obs, values, values3, reasons, memo, measure, m15)
            del pv, measure
    vintages = prices.recheck()
    t_end = time.perf_counter()
    return {'coin': coin, 'price_vintages': vintages, 'census': census, 'edges': edges, 'balance': balance, 'unavailable': unavailable, 'obs': obs,
            'values': values, 'values3': values3, 'tough': tough, 'tough_census': tough_census,
            'reasons': reasons, 'price_reads': prices.reads, 'price_read_s': prices.read_s,
            'missing_price_days': sorted(d for d, v in missing_price.items() if v),
            'seconds': {'match': t_measure - t_match, 'measure': t_end - t_measure, 'total': t_end - t_start}, 'pid': os.getpid(),
            'ru_maxrss': __import__('resource').getrusage(__import__('resource').RUSAGE_SELF).ru_maxrss, 'modules': process_modules()}
