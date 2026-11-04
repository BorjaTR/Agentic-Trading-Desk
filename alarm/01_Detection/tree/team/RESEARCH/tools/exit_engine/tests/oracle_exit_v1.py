"""TEST2 oracle_exit_v1 (23 Oct 2026): the exit walk of tools/exit_engine/README.md V2.4 f096e1bee1928fc0 section 2, written as plain
per-trade, per-bar Python on purpose (an independent recompute, never the engine's vectorised form). It is the tests' answer key and the
body the MUTANTS run on (env EXIT_MUTANT=<name>): every mutant must make at least one test FAIL (run_teeth_exit_v1.py).
Not a tool: never imported by the engine or any caller. The engine is judged against the README; where this file reads the README one way,
the post on hb/TEST2.txt names it (OPINION) for STRATEGY / BUILD1.

Grid: 3 s bars; bar i ends at t0_us + i x 3 s. An empty bar = close, hi and lo all NaN (unknown, never a price).
Per trade: entry_bar e (its close is the fill, entry_px given by the caller), side +1 / -1, the path starts at bar e + 1.
Per bar after the entry, in this order: 1 ADVERSE (stop, early stop, or the trail once armed), 2 TAKE (trade-through only),
3 ARM and trail update (acting from the next bar), 4 MONITOR (a reason known at bar k's close books bar k+1's close), 5 TIME.
"""
import math, os
import numpy as np

KINDS = ('stop', 'trail', 'take', 'monitor', 'time', 'noprice')
BAR_US = 3_000_000
MUTANTS = ('drop_adverse_first', 'trail_same_bar', 'stop_at_level', 'missing_unit_default', 'monitor_same_bar', 'take_on_touch',
           'cut_short', 'join_guard_off', 'future_time_close', 'side_ignored', 'min_hold_ignored', 'hole_is_price',
           'monitor_skips_hole', 'holes_only_at_levels', 'known_at_default', 'extreme_from_entry', 'extreme_guard_off')
# SKEPTIC REVIEW 03 (STRATEGY-130408, BUILD1-130859): 03-06 a monitor whose bar k+1 is empty books the first valid bar after it
# (gap_len_bars = that hole); 03-07 hole_bars = empty bars from entry+1 to the exit (or to the walk's end) on every trade, path_gap = > 0;
# 03-08 a non-pct unit without known_at refused; stop_from 'extreme' measures the stop from units extreme_px, known at extreme_known_at_us.


def mutant():
    m = os.environ.get('EXIT_MUTANT', '')
    if m and m not in MUTANTS:
        raise ValueError('unknown mutant %r' % m)
    return m


def bars_of(minutes):
    return None if minutes is None else int(round(float(minutes) * 20))


def _mult(row, units, i):
    u = row['unit']
    if u == 'pct':
        return 1.0
    v = None if units is None or units.get(u) is None else float(np.asarray(units[u], float)[i])
    if v is None or not math.isfinite(v) or v <= 0:
        if mutant() == 'missing_unit_default':
            return 1.0
        raise ValueError('trade %d: unit %s missing: refused (never a default)' % (i, u))
    return v


def simulate(close, hi, lo, entry_bar, entry_px, side, row, units=None, monitor=None, t0_us=0, signal_us=None):
    M = mutant()
    close, hi, lo = (np.asarray(x, float) for x in (close, hi, lo))
    e_all = np.asarray(entry_bar, np.int64); m = len(e_all); n = len(close)
    p0_all = np.asarray(entry_px, float); s_all = np.asarray(side, np.int64)
    if M == 'side_ignored':
        s_all = np.ones(m, np.int64)
    entry_us = t0_us + e_all * BAR_US
    has = units is not None and units.get('known_at_us') is not None
    if not has and row['unit'] != 'pct' and M != 'known_at_default':
        raise ValueError('unit %s without known_at_us: refused (03-08)' % row['unit'])
    ukn = np.full(m, -1, np.int64) if not has else np.asarray(units['known_at_us'], np.int64)
    ext = None
    if row.get('stop_from') == 'extreme':
        if units is None or units.get('extreme_px') is None or units.get('extreme_known_at_us') is None:
            raise ValueError('stop_from extreme needs extreme_px and extreme_known_at_us (03-08)')
        ext = np.asarray(units['extreme_px'], float)
        if M != 'extreme_guard_off' and np.any(np.asarray(units['extreme_known_at_us'], np.int64) > entry_us):
            raise ValueError('JOIN GUARD: extreme known after the entry')
        if M == 'extreme_from_entry':
            ext = None
    if M != 'join_guard_off' and row['unit'] != 'pct':
        bad = np.nonzero(ukn > entry_us)[0]
        if len(bad):
            raise ValueError('JOIN GUARD: unit values known after the entry for trades %s: refused' % bad[:5].tolist())
    out = {k: [] for k in ('exit_bar', 'exit_px', 'kind', 'ret_pct', 'heat_pct', 'best_pct', 'bars_to_arm', 'gap_bp', 'gap_len_bars',
                           'touched_not_filled', 'hole_bars')}
    tl, mh, em = bars_of(row['time_limit_min']), bars_of(row.get('min_hold_min')) or 0, bars_of(row.get('early_min'))
    if M == 'min_hold_ignored':
        mh = 0
    for i in range(m):
        e, p0, s = int(e_all[i]), float(p0_all[i]), int(s_all[i])
        k_ = _mult(row, units, i)
        lv = lambda x, sg: None if x is None else p0 * (1 + sg * s * float(x) * k_ / 100.0)
        stop_lv, early_lv = lv(row.get('stop'), -1), lv(row.get('early_stop'), -1)
        if ext is not None and row.get('stop') is not None:
            stop_lv = float(ext[i]) * (1 - s * float(row['stop']) * k_ / 100.0)
        take_lv, arm_lv = lv(row.get('take'), +1), lv(row.get('arm'), +1)
        give = None if row.get('give') is None else float(row['give']) * k_
        mon = -1 if monitor is None else int(monitor[i])
        end = e + tl
        armed, best, trail, t_arm = False, p0, None, -1
        adv_x, fav_x, hole, tnf, holes = None, None, 0, 0, 0
        res = None                                                           # (bar, px, kind, gap_bp, gap_len)
        worse = (lambda a, b: min(a, b)) if s > 0 else (lambda a, b: max(a, b))
        better = (lambda a, b: max(a, b)) if s > 0 else (lambda a, b: min(a, b))
        for j in range(e + 1, min(end, n - 1) + 1):
            k = j - e
            c, h, l = close[j], hi[j], lo[j]
            if not (math.isfinite(c) and math.isfinite(h) and math.isfinite(l)):
                if M == 'hole_is_price':
                    c = h = l = close[j - 1] if math.isfinite(close[j - 1]) else p0
                else:
                    hole += 1; holes += 1
                    continue
            adv, fav = (l, h) if s > 0 else (h, l)
            adv_x = adv if adv_x is None else worse(adv_x, adv)
            fav_x = fav if fav_x is None else better(fav_x, fav)
            in_hold = k < mh
            if M == 'trail_same_bar' and armed:
                best = better(best, fav); nt = best * (1 - s * give / 100.0); trail = better(trail, nt)
            # 1 ADVERSE first
            def adverse():
                if armed and not in_hold:
                    return trail, 'trail'
                if early_lv is not None and em is not None and k <= em:
                    return early_lv, 'stop'
                return stop_lv, 'stop'
            lvl, ka = adverse()
            hit_adv = lvl is not None and s * (adv - lvl) <= 0
            if M == 'drop_adverse_first' and take_lv is not None and not in_hold and s * (fav - take_lv) > 0:
                res = (j, take_lv, 'take', 0.0, 0); break
            if hit_adv:
                px = lvl if M == 'stop_at_level' else worse(lvl, c)
                res = (j, px, ka, s * (lvl - px) / p0 * 1e4, hole); break
            # 2 TAKE: trade-through only, at its level
            if take_lv is not None and not in_hold:
                d = s * (fav - take_lv)
                if d > 0 or (M == 'take_on_touch' and d == 0):
                    res = (j, take_lv, 'take', 0.0, 0); break
                if d == 0:
                    tnf += 1
            # 3 ARM, the trail acts from the NEXT bar
            if arm_lv is not None:
                if not armed and s * (fav - arm_lv) >= 0:
                    armed, t_arm = True, k
                if armed:
                    best = better(best, fav); nt = best * (1 - s * give / 100.0)
                    trail = nt if trail is None else better(trail, nt)
            # 4 MONITOR: a reason known at bar mon's close books bar mon + 1's close
            if mon >= e and (j == mon if M == 'monitor_same_bar' else (j == mon + 1 if M == 'monitor_skips_hole' else j >= mon + 1)):
                g = 0
                while g < hole and j - 1 - g > mon:
                    g += 1
                res = (j, c, 'monitor', 0.0, g); break
            hole = 0
            # 5 TIME
            if j == end:
                if M == 'future_time_close' and j + 1 < n and math.isfinite(close[j + 1]):
                    c = close[j + 1]
                res = (j, c, 'time', 0.0, 0); break
        if res is None and M == 'cut_short' and end > n - 1 and math.isfinite(close[n - 1]):
            res = (n - 1, close[n - 1], 'time', 0.0, 0)
        if res is None:
            res = (-1, float('nan'), 'noprice', 0.0, 0)
        b, px, kind, gbp, glen = res
        out['exit_bar'].append(b); out['exit_px'].append(px); out['kind'].append(kind)
        out['ret_pct'].append(s * (px / p0 - 1) * 100 if kind != 'noprice' else float('nan'))
        out['heat_pct'].append(float('nan') if adv_x is None or kind == 'noprice' else s * (adv_x / p0 - 1) * 100)
        out['best_pct'].append(float('nan') if fav_x is None or kind == 'noprice' else s * (fav_x / p0 - 1) * 100)
        out['bars_to_arm'].append(t_arm); out['gap_bp'].append(gbp); out['gap_len_bars'].append(glen)
        out['touched_not_filled'].append(tnf)
        out['hole_bars'].append(0 if (M == 'holes_only_at_levels' and kind not in ('stop', 'trail')) else holes)
    o = {k: np.asarray(v) for k, v in out.items()}
    o['exit_bar'] = o['exit_bar'].astype(np.int64); o['kind'] = o['kind'].astype(str)
    o['hole_bars'] = o['hole_bars'].astype(np.int64); o['path_gap'] = o['hole_bars'] > 0
    o['signal_us'] = entry_us.copy() if signal_us is None else np.asarray(signal_us, np.int64)
    o['entry_us'] = entry_us
    o['exit_us'] = np.where(o['exit_bar'] >= 0, t0_us + o['exit_bar'] * BAR_US, -1)
    o['known_at_us'] = o['exit_us'].copy()
    o['units_known_at_us'] = ukn
    return o
