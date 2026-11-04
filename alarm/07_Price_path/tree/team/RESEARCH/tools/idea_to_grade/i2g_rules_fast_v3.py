"""i2g_rules_fast_v3.py (speed twin S6, grader thread, 26 Oct 2026; TEST twin): i2g_rules_fast_v2 with walk_all's per-call setup done as
array operations: the asks become one float array (the same values: each ask's numbers and its resting flag, True/False as 1.0/0.0) and the
live mask is the same test (finite and above zero, both levels) on the columns. The compiled walk is i2g_rules_fast_v2._walk, called with
the same arguments, and the results are read out as in v2, so the same results bit for bit (test_rules_fast_v3.py). Without numba, or with
a time line that is not int64, walk_all is i2g_rules_fast_v1.walk_all, as in v2. Nothing else is copied."""
import types as _types
import numpy as np
import i2g_rules_v1_2 as RU
import i2g_rules_fast_v1 as F1
import i2g_rules_fast_v2 as F2

US = RU.US
numba = F2.numba
barrier_exit = F1.barrier_exit
CODES = F2.CODES
_NONE = (None, None, np.nan)


def walk_all(tl, px, hi, lo, i_start, t_from_us, entry_px, side, asks, known_end, max_stale_s=RU.MAX_STALE_S):
    """i2g_rules_fast_v2.walk_all, the same results bit for bit; the setup of the asks as array operations"""
    if numba is None or getattr(tl, 'dtype', None) != np.int64 or px.dtype != np.float64 or hi.dtype != np.float64 \
            or lo.dtype != np.float64:
        return F1.walk_all(tl, px, hi, lo, i_start, t_from_us, entry_px, side, asks, known_end, max_stale_s)
    nq = len(asks)
    if nq == 0:
        return []
    A = np.array(asks, dtype=np.float64).reshape(nq, 4)
    tg = np.ascontiguousarray(A[:, 0]); sp = np.ascontiguousarray(A[:, 1]); lim = np.ascontiguousarray(A[:, 2])
    rest = A[:, 3] != 0.0
    with np.errstate(invalid='ignore'):
        live = np.isfinite(tg) & np.isfinite(sp) & (tg > 0) & (sp > 0)
    if not live.any():
        return [_NONE] * nq
    code = np.zeros(nq, np.int64); tout = np.zeros(nq, np.int64); gout = np.full(nq, np.nan); fromp = np.zeros(nq, np.bool_)
    F2._walk(tl, px, hi, lo, int(i_start), int(t_from_us), float(entry_px), int(side), tg, sp, lim, rest, live, int(known_end),
             int(max_stale_s * US), code, tout, gout, fromp)
    out = [_NONE] * nq
    cl = code.tolist(); tol = tout.tolist(); fl = fromp.tolist(); lv = live.tolist()
    for q in range(nq):
        if lv[q]:
            c = cl[q]
            if c:
                out[q] = (CODES[c], tol[q], gout[q] if fl[q] else float(gout[q]))
    return out


def path_values_walk(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct):
    """i2g_rules_fast_v1.path_values_walk with this walk_all (the function's own code, its walk_all name rebound)"""
    return _PVW(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct)


_g = dict(F1.__dict__); _g['walk_all'] = walk_all
_PVW = _types.FunctionType(F1.path_values_walk.__code__, _g, 'path_values_walk')
