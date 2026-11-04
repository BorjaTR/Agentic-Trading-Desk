"""i2g_rules_fast_v1.py (speed scope V2 step 3, grader thread, 26 Oct 2026; TEST twin): the exit walk of i2g_rules_v1_2 with the per-bin
Python loop replaced by array scans over blocks of bins. Same rules, same arithmetic on the same values, so the same results bit for bit
(proved by test_rules_fast_v1.py against i2g_rules_v1_2, imported unchanged):
  barrier_exit  i2g_rules_v1_2.barrier_exit: the first PATH_HOLE gap or the first bin that hits a level (alarm_contract_v1.bin_exit's
                rule, written as arrays), whichever comes first; a hole at the same bin comes first, as in the loop
  path_values   i2g_rules_v1_2.path_values, calling this barrier_exit
Nothing else of i2g_rules_v1_2 is copied: every other name is read from it."""
import numpy as np
import i2g_rules_v1_2 as RU

US = RU.US
BLOCK = 512


def barrier_exit(tl, px, hi, lo, i_start, t_from_us, entry_px, side, target_pct, stop_pct, limit_s, known_end, resting_target=False,
                 max_stale_s=RU.MAX_STALE_S):
    """as i2g_rules_v1_2.barrier_exit, same arguments and result"""
    if not (np.isfinite(target_pct) and np.isfinite(stop_pct) and target_pct > 0 and stop_pct > 0):
        return None, None, np.nan
    tp = entry_px * (1 + side * target_pct / 100.0); sl = entry_px * (1 - side * stop_pct / 100.0)
    end = t_from_us + int(limit_s * US); last = min(end, known_end); stale = int(max_stale_s * US)
    j1 = int(np.searchsorted(tl, last, 'right'))
    j0 = max(i_start + 1, int(np.searchsorted(tl, t_from_us, 'right')))      # the loop skips bins whose last trade is at or before t_from
    prev = int(t_from_us)
    for a in range(j0, j1, BLOCK):
        b = min(a + BLOCK, j1)
        seq = tl[a:b]
        if seq.dtype.kind != 'i':
            seq = np.array([int(x) for x in seq], np.int64)                 # the loop's int() of each clock
        gaps = np.diff(seq, prepend=np.int64(prev))
        hole = np.flatnonzero(gaps > stale)
        if side > 0:
            hit_s = lo[a:b] <= sl
            hit_t = hi[a:b] > tp if resting_target else hi[a:b] >= tp
        else:
            hit_s = hi[a:b] >= sl
            hit_t = lo[a:b] < tp if resting_target else lo[a:b] <= tp
        hit = np.flatnonzero(hit_s | hit_t)
        h = int(hole[0]) if len(hole) else None
        k = int(hit[0]) if len(hit) else None
        if h is not None and (k is None or h <= k):
            return 'PATH_HOLE', int(seq[h]), np.nan
        if k is not None:
            j = a + k
            if not hit_s[k]:
                return 'TARGET', int(tl[j]), side * 100.0 * (tp / entry_px - 1.0)
            code = 'AMBIGUOUS_STOP' if hit_t[k] else 'STOP'
            x = min(sl, px[j]) if side > 0 else max(sl, px[j])
            return code, int(tl[j]), side * 100.0 * (x / entry_px - 1.0)
        prev = int(seq[-1])
    if end > known_end:
        return None, None, np.nan
    j = RU._last_at_or_before(tl, end, i_start)
    if j < 0:
        return None, None, np.nan
    if end - int(tl[j]) > stale:
        return 'PATH_HOLE', int(end), np.nan
    return 'TIME', int(tl[j]), side * 100.0 * (px[j] / entry_px - 1.0)


def path_values(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct):
    """as i2g_rules_v1_2.path_values (the same lines), with this module's barrier_exit"""
    names = RU.value_names(); v = dict.fromkeys(names, np.nan)
    v['move15_pct'], v['rv5_pct'], v['c_pct'] = move_pct, rv_pct, c_pct
    st, i_f, t_f, p_f = taker
    v['tk_filled'] = 1.0 if st == 'FILLED' else 0.0
    holes = []
    if st == 'FILLED':
        for h, r in zip(RU.HORIZON_NAMES, RU.horizon_returns(pv_tl, pv_px, i_f, t_f, p_f, side_traded, known_end, holes=holes)):
            v['ret_%s' % h] = r
        for name, kind, a, b, lim in RU.EXITS:
            tg, sp = RU.exit_levels(kind, a, b, rv_pct, c_pct)
            code, _, g = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, i_f, t_f, p_f, side_traded, tg, sp, lim, known_end)
            v['tk_%s' % name] = g; v['tk_%s_code' % name] = RU.EXIT_CODES.get(code, np.nan); holes += [name] if code == 'PATH_HOLE' else []
    rs, j, t_r, L = RU.passive_entry(pv_tl, pv_px, pv_lo, pv_hi, t_dec_us, side_traded)
    v['rs_filled'] = 1.0 if rs == 'FILLED' else 0.0 if rs == 'UNFILLED' else np.nan
    if rs == 'FILLED':
        v['rs_wait_s'] = (t_r - t_dec_us) / US
        for name, kind, a, b, lim in RU.EXITS:
            tg, sp = RU.exit_levels(kind, a, b, rv_pct, c_pct)
            c1, _, g = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, j, t_r, L, side_traded, tg, sp, lim, known_end)
            code, _, g2 = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, j, t_r, L, side_traded, tg, sp, lim, known_end, resting_target=True)
            v['re_%s' % name] = g; v['rb_%s' % name] = g2; v['rb_%s_code' % name] = RU.EXIT_CODES.get(code, np.nan)
            holes += [name] * ((c1 == 'PATH_HOLE') + (code == 'PATH_HOLE'))
    v['path_holes'] = float(len(holes))
    return np.array([v[n] for n in names], float)


def walk_all(tl, px, hi, lo, i_start, t_from_us, entry_px, side, asks, known_end, max_stale_s=RU.MAX_STALE_S):
    """every barrier_exit of ONE start (same tl, px, hi, lo, i_start, t_from, entry, side, known_end) in one pass over the bins.
    asks: [(target_pct, stop_pct, limit_s, resting_target)] -> [barrier_exit(...) for each ask], the same results bit for bit.
    The first hole is one position for every ask; the first bin that reaches a level is found on the running extremes (NaN bins never
    reach a level, as in the loop), so each ask is two binary searches."""
    out = [None] * len(asks)
    live = []
    for q, (tg, sp, lim, rest) in enumerate(asks):
        if not (np.isfinite(tg) and np.isfinite(sp) and tg > 0 and sp > 0):
            out[q] = (None, None, np.nan)
        else:
            live.append(q)
    if not live:
        return out
    stale = int(max_stale_s * US)
    j0 = max(i_start + 1, int(np.searchsorted(tl, t_from_us, 'right')))
    ends = {q: t_from_us + int(asks[q][2] * US) for q in live}
    jmax = max(int(np.searchsorted(tl, min(ends[q], known_end), 'right')) for q in live)
    n = max(jmax - j0, 0)
    seq = tl[j0:j0 + n]
    if seq.dtype.kind != 'i':
        seq = np.array([int(x) for x in seq], np.int64)
    hole = np.flatnonzero(np.diff(seq, prepend=np.int64(int(t_from_us))) > stale) if n else np.zeros(0, np.int64)
    h = int(hole[0]) if len(hole) else n
    h_ = hi[j0:j0 + n]; l_ = lo[j0:j0 + n]
    if side > 0:
        fav = np.maximum.accumulate(np.where(np.isnan(h_), -np.inf, h_)) if n else h_      # target side: highs
        adv = -np.minimum.accumulate(np.where(np.isnan(l_), np.inf, l_)) if n else l_      # stop side: lows, negated (ascending)
    else:
        fav = -np.minimum.accumulate(np.where(np.isnan(l_), np.inf, l_)) if n else l_      # target side: lows, negated
        adv = np.maximum.accumulate(np.where(np.isnan(h_), -np.inf, h_)) if n else h_      # stop side: highs
    for q in live:
        tg, sp, lim, rest = asks[q]
        tp = entry_px * (1 + side * tg / 100.0); sl = entry_px * (1 - side * sp / 100.0)
        end = ends[q]
        ne = int(np.searchsorted(tl, min(end, known_end), 'right')) - j0
        if side > 0:
            kt = int(np.searchsorted(fav[:ne], tp, 'right' if rest else 'left'))       # first high > tp (or >= tp)
            ks = int(np.searchsorted(adv[:ne], -sl, 'left'))                          # first low <= sl
        else:
            kt = int(np.searchsorted(fav[:ne], -tp, 'right' if rest else 'left'))      # first low < tp (or <= tp)
            ks = int(np.searchsorted(adv[:ne], sl, 'left'))                           # first high >= sl
        k = min(kt, ks)
        if h < ne and h <= k:
            out[q] = ('PATH_HOLE', int(seq[h]), np.nan)
            continue
        if k < ne:
            j = j0 + k
            if ks != k:
                out[q] = ('TARGET', int(tl[j]), side * 100.0 * (tp / entry_px - 1.0))
            else:
                x = min(sl, px[j]) if side > 0 else max(sl, px[j])
                out[q] = ('AMBIGUOUS_STOP' if kt == k else 'STOP', int(tl[j]), side * 100.0 * (x / entry_px - 1.0))
            continue
        if end > known_end:
            out[q] = (None, None, np.nan); continue
        j = RU._last_at_or_before(tl, end, i_start)
        if j < 0:
            out[q] = (None, None, np.nan)
        elif end - int(tl[j]) > stale:
            out[q] = ('PATH_HOLE', int(end), np.nan)
        else:
            out[q] = ('TIME', int(tl[j]), side * 100.0 * (px[j] / entry_px - 1.0))
    return out


def path_values_walk(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct):
    """as i2g_rules_v1_2.path_values, every exit of the taker start and of the resting start from walk_all"""
    names = RU.value_names(); v = dict.fromkeys(names, np.nan)
    v['move15_pct'], v['rv5_pct'], v['c_pct'] = move_pct, rv_pct, c_pct
    st, i_f, t_f, p_f = taker
    v['tk_filled'] = 1.0 if st == 'FILLED' else 0.0
    holes = []
    lv = [RU.exit_levels(kind, a, b, rv_pct, c_pct) + (lim,) for _, kind, a, b, lim in RU.EXITS]
    if st == 'FILLED':
        for h, r in zip(RU.HORIZON_NAMES, RU.horizon_returns(pv_tl, pv_px, i_f, t_f, p_f, side_traded, known_end, holes=holes)):
            v['ret_%s' % h] = r
        res = walk_all(pv_tl, pv_px, pv_hi, pv_lo, i_f, t_f, p_f, side_traded, [x + (False,) for x in lv], known_end)
        for (name, *_), (code, _, g) in zip(RU.EXITS, res):
            v['tk_%s' % name] = g; v['tk_%s_code' % name] = RU.EXIT_CODES.get(code, np.nan); holes += [name] if code == 'PATH_HOLE' else []
    rs, j, t_r, L = RU.passive_entry(pv_tl, pv_px, pv_lo, pv_hi, t_dec_us, side_traded)
    v['rs_filled'] = 1.0 if rs == 'FILLED' else 0.0 if rs == 'UNFILLED' else np.nan
    if rs == 'FILLED':
        v['rs_wait_s'] = (t_r - t_dec_us) / US
        res = walk_all(pv_tl, pv_px, pv_hi, pv_lo, j, t_r, L, side_traded, [x + (False,) for x in lv] + [x + (True,) for x in lv], known_end)
        ne = len(lv)
        for q, (name, *_) in enumerate(RU.EXITS):
            c1, _, g = res[q]; code, _, g2 = res[ne + q]
            v['re_%s' % name] = g; v['rb_%s' % name] = g2; v['rb_%s_code' % name] = RU.EXIT_CODES.get(code, np.nan)
            holes += [name] * ((c1 == 'PATH_HOLE') + (code == 'PATH_HOLE'))
    v['path_holes'] = float(len(holes))
    return np.array([v[n] for n in names], float)
