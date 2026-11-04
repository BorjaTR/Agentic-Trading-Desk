"""i2g_rules_fast_v2.py (speed scope V2 step 3, grader thread, 26 Oct 2026; TEST twin): i2g_rules_fast_v1 with walk_all's per-ask work
compiled (numba). The same rules, comparisons and arithmetic as i2g_rules_fast_v1.walk_all (itself bit-equal to i2g_rules_v1_2.barrier_exit),
so the same results bit for bit (test_rules_fast_v2.py):
  - the binary searches are numpy's searchsorted rule written out, NaN-aware as numpy is (a NaN level is found at the end);
  - a prefix of length ne is taken as Python slices it (a negative ne counts from the end);
  - the money arithmetic is the same expressions in the same order, no fastmath.
Without numba, or with a time line that is not int64, walk_all is i2g_rules_fast_v1.walk_all. Nothing else is copied: every other name is
read from i2g_rules_fast_v1 and i2g_rules_v1_2."""
import numpy as np
import i2g_rules_v1_2 as RU
import i2g_rules_fast_v1 as F1

US = RU.US
barrier_exit = F1.barrier_exit
CODES = (None, 'PATH_HOLE', 'TARGET', 'STOP', 'AMBIGUOUS_STOP', 'TIME')

try:
    import numba
    _jit = numba.njit(cache=False, nogil=True)
except ImportError:                    # no compiler: the same loops in plain Python (tests only; slow)
    numba = None
    _jit = lambda f: f


@_jit
def _lt(a, b):
    """numpy's sort order: NaN after every number"""
    return a < b or (b != b and a == a)


@_jit
def _ss_left(a, n, v):
    lo = 0; hi = n
    while lo < hi:
        mid = (lo + hi) >> 1
        if _lt(a[mid], v):
            lo = mid + 1
        else:
            hi = mid
    return lo


@_jit
def _ss_right(a, n, v):
    lo = 0; hi = n
    while lo < hi:
        mid = (lo + hi) >> 1
        if _lt(v, a[mid]):
            hi = mid
        else:
            lo = mid + 1
    return lo


@_jit
def _ss_int_right(a, v):
    lo = 0; hi = a.shape[0]
    while lo < hi:
        mid = (lo + hi) >> 1
        if v < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


@_jit
def _plen(ne, n):
    """len(x[:ne]) for len(x) == n"""
    if ne < 0:
        return max(n + ne, 0)
    return min(ne, n)


@_jit
def _walk(tl, px, hi, lo, i_start, t_from_us, entry_px, side, tg, sp, lim, rest, live, known_end, stale, code, tout, gout, fromp):
    nq = tg.shape[0]
    ends = np.zeros(nq, np.int64)
    j0 = max(i_start + 1, _ss_int_right(tl, t_from_us))
    jmax = -1
    for q in range(nq):
        if live[q]:
            ends[q] = t_from_us + np.int64(lim[q] * US)
            jj = _ss_int_right(tl, min(ends[q], known_end))
            if jj > jmax:
                jmax = jj
    n = max(jmax - j0, 0)
    h = n
    prev = t_from_us
    for i in range(n):
        if tl[j0 + i] - prev > stale:
            h = i
            break
        prev = tl[j0 + i]
    fav = np.empty(n); adv = np.empty(n)
    fm = -np.inf; am = np.inf
    for i in range(n):
        if side > 0:
            x = hi[j0 + i]; y = lo[j0 + i]
            if not np.isnan(x) and x > fm:
                fm = x
            if not np.isnan(y) and y < am:
                am = y
            fav[i] = fm; adv[i] = -am
        else:
            x = lo[j0 + i]; y = hi[j0 + i]
            if not np.isnan(x) and x < am:
                am = x
            if not np.isnan(y) and y > fm:
                fm = y
            fav[i] = -am; adv[i] = fm
    for q in range(nq):
        if not live[q]:
            continue
        tp = entry_px * (1 + side * tg[q] / 100.0); sl = entry_px * (1 - side * sp[q] / 100.0)
        end = ends[q]
        ne = _ss_int_right(tl, min(end, known_end)) - j0
        m = _plen(ne, n)
        if side > 0:
            kt = _ss_right(fav, m, tp) if rest[q] else _ss_left(fav, m, tp)
            ks = _ss_left(adv, m, -sl)
        else:
            kt = _ss_right(fav, m, -tp) if rest[q] else _ss_left(fav, m, -tp)
            ks = _ss_left(adv, m, sl)
        k = min(kt, ks)
        if h < ne and h <= k:
            code[q] = 1; tout[q] = tl[j0 + h]; gout[q] = np.nan
            continue
        if k < ne:
            j = j0 + k
            if ks != k:
                code[q] = 2; tout[q] = tl[j]; gout[q] = side * 100.0 * (tp / entry_px - 1.0)
            else:
                pj = px[j]
                if side > 0:
                    x = pj if pj < sl else sl              # Python's min(sl, px[j])
                    fromp[q] = pj < sl
                else:
                    x = pj if pj > sl else sl              # Python's max(sl, px[j])
                    fromp[q] = pj > sl
                code[q] = 4 if kt == k else 3; tout[q] = tl[j]; gout[q] = side * 100.0 * (x / entry_px - 1.0)
            continue
        if end > known_end:
            code[q] = 0; gout[q] = np.nan; continue
        j = _ss_int_right(tl, end) - 1
        if j < i_start or j < 0:                       # RU._last_at_or_before gives -1, then the loop's j < 0
            code[q] = 0; gout[q] = np.nan
        elif end - tl[j] > stale:
            code[q] = 1; tout[q] = end; gout[q] = np.nan
        else:
            code[q] = 5; tout[q] = tl[j]; gout[q] = side * 100.0 * (px[j] / entry_px - 1.0); fromp[q] = True


def walk_all(tl, px, hi, lo, i_start, t_from_us, entry_px, side, asks, known_end, max_stale_s=RU.MAX_STALE_S):
    """i2g_rules_fast_v1.walk_all, the same results bit for bit; the per-ask work compiled"""
    if numba is None or getattr(tl, 'dtype', None) != np.int64 or px.dtype != np.float64 or hi.dtype != np.float64 \
            or lo.dtype != np.float64:
        return F1.walk_all(tl, px, hi, lo, i_start, t_from_us, entry_px, side, asks, known_end, max_stale_s)
    out = [None] * len(asks)
    nq = len(asks)
    tg = np.empty(nq); sp = np.empty(nq); lim = np.empty(nq); rest = np.zeros(nq, np.bool_); live = np.zeros(nq, np.bool_)
    for q, (a, b, c, r) in enumerate(asks):
        tg[q] = a; sp[q] = b; lim[q] = c; rest[q] = bool(r)
        if np.isfinite(a) and np.isfinite(b) and a > 0 and b > 0:
            live[q] = True
        else:
            out[q] = (None, None, np.nan)
    if not live.any():
        return out
    code = np.zeros(nq, np.int64); tout = np.zeros(nq, np.int64); gout = np.full(nq, np.nan); fromp = np.zeros(nq, np.bool_)
    _walk(tl, px, hi, lo, int(i_start), int(t_from_us), float(entry_px), int(side), tg, sp, lim, rest, live, int(known_end),
          int(max_stale_s * US), code, tout, gout, fromp)
    for q in range(nq):
        if live[q]:
            c = int(code[q])
            g = gout[q] if fromp[q] else float(gout[q])    # v1's types: a value from px is numpy's float64
            out[q] = (None, None, np.nan) if c == 0 else (CODES[c], int(tout[q]), g)
    return out


def path_values_walk(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct):
    """i2g_rules_fast_v1.path_values_walk with this walk_all (the function's own code, its walk_all name rebound)"""
    return _PVW(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct)


import types as _types
_g = dict(F1.__dict__); _g['walk_all'] = walk_all
_PVW = _types.FunctionType(F1.path_values_walk.__code__, _g, 'path_values_walk')
