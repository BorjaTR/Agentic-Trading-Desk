"""E-LADDER v6 (BED, 19 Oct 2026; kanban 4.24a, LAB1 18:19:28Z: numba for the ladder loops, bit for bit; tests first: test_ladder_v6.py)
= v5 (9b71b58594b1251e, kept, the oracle) with ONE change: the level search and the before/after arrays run as one compiled loop
(numba, no disk cache: a compiled copy per process, about 1 s once; a cache file would be written beside the code and breaks when the module is loaded under another name, as lab/trades.py does) instead of 25 x n numpy arrays. Every value is the same IEEE operation as v5's: r_money (log, expm1) stays numpy
on the same slices; cmax, cmin, cmax0, cmin0 are v5's own numpy calls (so a NaN or a -0.0 is what numpy gives on the machine); a level is touched when rint((c / L) * 1e9) / 1e9 >= 1
(heat: <= -1), which is numpy's round(x, 9) (multiply by 10**9, rint, divide); first index, -1 when none. Levels ascend, so
for a positive c, c / L falls with L and a level can be touched only after the ones below it: one pointer per side. Without numba the same
function runs as plain python (slow, same bits). v5's text follows (ladder_v5.py)."""
import numpy as np
from ladder_v2 import US, GAP_US, LEVELS, r_money, _first, trailing, ladder_bench   # noqa: F401  (re-exported, v2's own)

BIN_US = 3 * US
try:
    from numba import njit
    HAVE_NUMBA = True
except Exception:                                         # no numba, or a numba that fails to import (the year python's): same bits, python speed
    HAVE_NUMBA = False
    def njit(*a, **k):
        return (lambda f: f) if not (len(a) == 1 and callable(a[0])) else a[0]


@njit(cache=False)
def _kernel(ro, rh, cmax, cmin, cmax0, cmin0, levels):
    """first touches and the before/after arrays; cmax, cmin, cmax0, cmin0 come from numpy (v5's own calls, so a NaN or a -0.0
    is whatever numpy gives on this machine)"""
    m = ro.shape[0]; nl = levels.shape[0]
    oi = np.full(nl, -1, np.int64); hi = np.full(nl, -1, np.int64)
    o0 = -1; h0 = -1; ko = 0; kh = 0
    for j in range(m):
        if o0 < 0 and ro[j] > 0:
            o0 = j
        if h0 < 0 and rh[j] < 0:
            h0 = j
        # levels ascend and c / L falls as L rises (c > 0), so the first untouched level is the only one that can be touched next:
        # the same test as v5 on each (bin, level) pair until it is first true, the rest known false
        while ko < nl and np.rint((cmax[j] / levels[ko]) * 1e9) / 1e9 >= 1:
            oi[ko] = j; ko += 1
        while kh < nl and np.rint((cmin[j] / levels[kh]) * 1e9) / 1e9 <= -1:
            hi[kh] = j; kh += 1
    best = np.empty(nl + 1); worst = np.empty(nl + 1)
    for k in range(nl + 1):
        h = h0 if k == 0 else hi[k - 1]
        o = o0 if k == 0 else oi[k - 1]
        best[k] = cmax0[h - 1] if h > 0 else (0.0 if h == 0 else cmax0[m - 1])
        worst[k] = cmin0[o] if o >= 0 else cmin0[m - 1]
    return oi, hi, o0, h0, best, worst


def _window(pv, fill, max_hold_s):
    """a, b: the hold's bins [a, b) (v2); e >= b: the edge bins are [b, e)"""
    t1 = fill.t_us + int(max_hold_s) * US
    a = fill.i + 1; b = int(np.searchsorted(pv.tl, t1, side='right'))
    e = max(b, int(np.searchsorted(pv.te, t1 + BIN_US, side='right')))
    return a, b, e, t1


def ladder(pv, fill, side, max_hold_s, mode='engine'):
    if mode == 'bench':
        raise ValueError('bench mode takes the decision time: ladder_bench(pv, t_us, side, max_hold_s)')
    if side not in (1, -1):
        raise ValueError('side is +1 or -1')
    a, b, e, t1 = _window(pv, fill, max_hold_s)
    lp0 = np.log(pv.px[fill.i])
    up_side, dn_side = (pv.hi, pv.lo) if side == 1 else (pv.lo, pv.hi)
    ro = r_money(side, np.log(up_side[a:e]) - lp0)
    rh = r_money(side, np.log(dn_side[a:e]) - lp0)
    n = b - a; m = e - a; tl = pv.tl[a:e]
    ro[n:] = -np.inf
    out = dict(n=n, end=bool(t1 > pv.tl[-1]), t_fill=fill.t_us, t_end=t1, edge=bool(e > b))
    gap_first = np.zeros(m, bool)
    if m:
        prev = np.concatenate([[pv.tl[a - 1]], tl[:-1]])
        gap_first = (tl - prev) > GAP_US
    out['n_gaps'] = int(gap_first[:n].sum())
    if m == 0:
        z25 = np.full(25, -1, np.int64)
        out.update(offer_t=z25, heat_t=z25.copy(), offer0_t=-1, heat0_t=-1, best_offer_before_heat=np.zeros(26),
                   worst_heat_before_offer=np.zeros(26), offer_gap=np.zeros(25, bool), heat_gap=np.zeros(25, bool),
                   minute_path=np.zeros((0, 3)))
        return out
    cmax = np.maximum.accumulate(ro); cmin = np.minimum.accumulate(rh)              # v5's own numpy calls
    cmax0 = np.maximum(cmax, 0.0); cmin0 = np.minimum(cmin, 0.0)
    oi, hi_, o0, h0, best, worst = _kernel(ro, rh, cmax, cmin, cmax0, cmin0, LEVELS)
    o0 = int(o0); h0 = int(h0)
    out['best_offer_before_heat'] = best
    out['worst_heat_before_offer'] = worst
    out['offer_t'] = np.where(oi >= 0, tl[np.maximum(oi, 0)], -1).astype(np.int64)
    out['heat_t'] = np.where(hi_ >= 0, tl[np.maximum(hi_, 0)], -1).astype(np.int64)
    out['offer0_t'] = int(tl[o0]) if o0 >= 0 else -1; out['heat0_t'] = int(tl[h0]) if h0 >= 0 else -1
    out['offer_gap'] = np.where(oi >= 0, gap_first[np.maximum(oi, 0)], False)
    out['heat_gap'] = np.where(hi_ >= 0, gap_first[np.maximum(hi_, 0)], False)
    if n == 0:
        out['minute_path'] = np.zeros((0, 3)); return out
    m0 = (fill.t_us // (60 * US) + 1) * 60 * US
    ends = np.arange(m0, t1 + 1, 60 * US, dtype=np.int64)
    k = np.searchsorted(tl[:n], ends, side='right') - 1
    rc = r_money(side, np.log(pv.px[a:b]) - lp0)
    mp = np.zeros((len(ends), 3))
    ok = k >= 0
    mp[ok, 0] = rc[k[ok]]; mp[ok, 1] = cmax0[k[ok]]; mp[ok, 2] = cmin0[k[ok]]
    out['minute_path'] = mp; out['minute_ends'] = ends
    return out
