"""i2g_patch_s4_v1.py (speed twin S4, grader thread, 26 Oct 2026, TEST): two process-local speedups for the store build's workers, each
the same values bit for bit; applied by patch(k) to the modules K.load() returns (no file is changed; the signed modules are read, and
their own functions are what the new ones call):
  1 calendar  draw_v3 / draw_prepared_v1 day_of and month_of call datetime.strftime once per call (about 484k calls on M's largest task).
              Here each is memoised per UTC day: for a float x whose part after the whole second is below 0.999999, datetime rounds it
              to microseconds inside the same second, so the day is floor(x) // 86400 and the text is the module's own function at that
              day's first second. Any other x (the last microsecond of a second, NaN, inf) goes to the module's own function. _day_start
              is memoised per day text. part_of, same_window and days_for are the module's own code; they read these names at call time.
  2 ladder    the STAMP projection reads only offer_t, heat_t and end of LD.ladder (heat_offer_projection_v1.entry_row with
              projection 'stamp'). ladder_stamp computes those with LD's own _window, r_money, _kernel and numpy calls in LD.ladder's
              order and skips the rest (gaps, before/after arrays kept, minute path dropped). Other modes go to LD.ladder.
No date, coin or alarm is held here."""
import math
import numpy as np

DONE = '_i2g_patch_s4_v1'


def cal_memo(orig):
    """orig(t) -> text of the UTC day (or month) of t; the same text for every t, memoised per day"""
    memo = {}

    def f(t):
        x = float(t)
        if x == x and abs(x) < 1e15:
            s = math.floor(x)
            if x - s < 0.999999:
                k = int(s) // 86400
                v = memo.get(k)
                if v is None:
                    v = memo[k] = orig(k * 86400)
                return v
        return orig(t)
    f.orig = orig
    return f


def str_memo(orig):
    memo = {}

    def f(d):
        k = str(d)
        v = memo.get(k)
        if v is None:
            v = memo[k] = orig(d)
        return v
    f.orig = orig
    return f


def ladder_stamp(LD):
    full = LD.ladder

    def ladder(pv, fill, side, max_hold_s, mode='engine'):
        if mode != 'engine' or side not in (1, -1):
            return full(pv, fill, side, max_hold_s, mode)
        a, b, e, t1 = LD._window(pv, fill, max_hold_s)
        lp0 = np.log(pv.px[fill.i])
        up_side, dn_side = (pv.hi, pv.lo) if side == 1 else (pv.lo, pv.hi)
        ro = LD.r_money(side, np.log(up_side[a:e]) - lp0)
        rh = LD.r_money(side, np.log(dn_side[a:e]) - lp0)
        n = b - a; m = e - a; tl = pv.tl[a:e]
        ro[n:] = -np.inf
        out = dict(n=n, end=bool(t1 > pv.tl[-1]), t_fill=fill.t_us, t_end=t1, edge=bool(e > b))
        if m == 0:
            z25 = np.full(25, -1, np.int64)
            out.update(offer_t=z25, heat_t=z25.copy(), offer0_t=-1, heat0_t=-1)
            return out
        cmax = np.maximum.accumulate(ro); cmin = np.minimum.accumulate(rh)
        cmax0 = np.maximum(cmax, 0.0); cmin0 = np.minimum(cmin, 0.0)
        oi, hi_, o0, h0, best, worst = LD._kernel(ro, rh, cmax, cmin, cmax0, cmin0, LD.LEVELS)
        o0 = int(o0); h0 = int(h0)
        out['offer_t'] = np.where(oi >= 0, tl[np.maximum(oi, 0)], -1).astype(np.int64)
        out['heat_t'] = np.where(hi_ >= 0, tl[np.maximum(hi_, 0)], -1).astype(np.int64)
        out['offer0_t'] = int(tl[o0]) if o0 >= 0 else -1; out['heat0_t'] = int(tl[h0]) if h0 >= 0 else -1
        return out
    ladder.orig = full
    return ladder


def patch(k, ladder=True):
    """k = K.load(): memoise the calendar of k.D and k.DP; with ladder, LD.ladder -> ladder_stamp (only for the STAMP projection's
    callers: this process runs nothing else). Once per module."""
    for mod in {id(k.D): k.D, id(k.DP): k.DP}.values():
        if not getattr(mod, DONE, False):
            mod.day_of = cal_memo(mod.day_of); mod.month_of = cal_memo(mod.month_of); mod._day_start = str_memo(mod._day_start)
            setattr(mod, DONE, True)
    if ladder and not getattr(k.LD, DONE, False):
        k.LD.ladder = ladder_stamp(k.LD); setattr(k.LD, DONE, True)
