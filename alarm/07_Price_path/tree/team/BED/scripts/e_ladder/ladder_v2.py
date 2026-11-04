"""E-LADDER v2 (BED, 16 Oct 2026; LAB_ARCH_V6 ed. 5 D3, D5, D11, D12, 13.5 EXECUTION; R43 to R45; tests first: test_ladder_v2.py).
ENGINE MODE, per trade, on PX3S v2 bins (E-PX2), in PERCENT OF MONEY (D3): a long's r = 100 x expm1(dlp), a short's r = -100 x expm1(dlp).
  A long reads OFFERS on each bin's hi and HEATS on its lo; a short offers on lo and heats on hi (ed. 3 row 108).
  Levels 0.1 .. 2.5 (25, index 0 = 0.1): offer k touched when round(r / level, 9) >= 1, heat k when <= -1 (label_at_np's tie rule).
  Level 0.0 (index 0 of the 26-arrays, BED's build note 07:24:31Z): offer 0.0 = the first bin with r > 0, heat 0.0 = r < 0 (strict).
  best_offer_before_heat[k] = the best offer over the bins STRICTLY BEFORE heat k's first bin (a bin crossing both = heat first, D11),
  the whole hold when heat k is never touched; worst_heat_before_offer[k] the same the other way; both clipped at 0 (no offer = 0).
  The hold = the bins whose last trade is in (t_fill, t_fill + max_hold]. A gap over 40 s inside it CUTS only the levels first touched on
  the first bin after it: they are flagged (offer_gap, heat_gap) and the trade goes on (BED-H17); END = the data stops before the hold ends.
  The MINUTE PATH (D12 ed. 4, ed. 5 float64): at each minute end of the hold, r at the last close at or before it, the best offer and the
  worst heat so far: (n_minutes, 3) float64, for clock exits, time-outs and minute trailing rules on the cache.
TRAILING (BED-H21): the anchor (the best offer so far, from 0) moves only on EARLIER bins; a bin whose heat side crosses anchor - trail is
  the touch even if the same bin makes a new high (heat first).
BENCH MODE (KA1, KA2, E-AGREE): closes only, log units, the bench's entry (the last close at or before t), CUT at a gap as opportunity():
  the prototype exec_v0.ladder that passed KA1 (54,972 of 54,972 = c22 both_sides), ported line for line."""
import numpy as np

US = 1_000_000
GAP_US = 40 * US
LEVELS = np.round(np.arange(1, 26) * 0.1, 10)


def r_money(side, dlp):
    """percent of money for a move dlp in log price (D3): long 100 expm1(dlp), short -100 expm1(dlp)"""
    return side * 100.0 * np.expm1(dlp)


def _first(mask):
    """first True along the last axis, -1 when none"""
    m = np.asarray(mask)
    if m.ndim == 1:
        return int(m.argmax()) if m.any() else -1
    return np.where(m.any(-1), m.argmax(-1), -1)


def _window(pv, fill, max_hold_s):
    t1 = fill.t_us + int(max_hold_s) * US
    a = fill.i + 1; b = int(np.searchsorted(pv.tl, t1, side='right'))
    return a, b, t1


def ladder(pv, fill, side, max_hold_s, mode='engine'):
    if mode == 'bench':
        raise ValueError('bench mode takes the decision time: ladder_bench(pv, t_us, side, max_hold_s)')
    if side not in (1, -1):
        raise ValueError('side is +1 or -1')
    a, b, t1 = _window(pv, fill, max_hold_s)
    lp0 = np.log(pv.px[fill.i])
    up_side, dn_side = (pv.hi, pv.lo) if side == 1 else (pv.lo, pv.hi)
    ro = r_money(side, np.log(up_side[a:b]) - lp0)       # the offer side of each bin
    rh = r_money(side, np.log(dn_side[a:b]) - lp0)       # the heat side
    n = b - a; tl = pv.tl[a:b]
    out = dict(n=n, end=bool(t1 > pv.tl[-1]), t_fill=fill.t_us, t_end=t1)
    gap_first = np.zeros(n, bool)
    if n:
        prev = np.concatenate([[pv.tl[a - 1]], tl[:-1]])
        gap_first = (tl - prev) > GAP_US
    out['n_gaps'] = int(gap_first.sum())
    if n == 0:
        z25 = np.full(25, -1, np.int64)
        out.update(offer_t=z25, heat_t=z25.copy(), offer0_t=-1, heat0_t=-1, best_offer_before_heat=np.zeros(26),
                   worst_heat_before_offer=np.zeros(26), offer_gap=np.zeros(25, bool), heat_gap=np.zeros(25, bool),
                   minute_path=np.zeros((0, 3)))
        return out
    cmax = np.maximum.accumulate(ro); cmin = np.minimum.accumulate(rh)
    oi = _first(np.round(cmax[None, :] / LEVELS[:, None], 9) >= 1)
    hi_ = _first(np.round(cmin[None, :] / LEVELS[:, None], 9) <= -1)
    o0 = _first(ro > 0); h0 = _first(rh < 0)
    o26 = np.concatenate([[o0], oi]); h26 = np.concatenate([[h0], hi_])
    cmax0 = np.maximum(cmax, 0.0); cmin0 = np.minimum(cmin, 0.0)
    out['best_offer_before_heat'] = np.array([cmax0[h - 1] if h > 0 else (0.0 if h == 0 else cmax0[-1]) for h in h26])
    out['worst_heat_before_offer'] = np.array([cmin0[o - 1] if o > 0 else (0.0 if o == 0 else cmin0[-1]) for o in o26])
    out['offer_t'] = np.where(oi >= 0, tl[np.maximum(oi, 0)], -1).astype(np.int64)
    out['heat_t'] = np.where(hi_ >= 0, tl[np.maximum(hi_, 0)], -1).astype(np.int64)
    out['offer0_t'] = int(tl[o0]) if o0 >= 0 else -1; out['heat0_t'] = int(tl[h0]) if h0 >= 0 else -1
    out['offer_gap'] = np.where(oi >= 0, gap_first[np.maximum(oi, 0)], False)
    out['heat_gap'] = np.where(hi_ >= 0, gap_first[np.maximum(hi_, 0)], False)
    # the minute path: minute ends in (t_fill, t1]
    m0 = (fill.t_us // (60 * US) + 1) * 60 * US
    ends = np.arange(m0, t1 + 1, 60 * US, dtype=np.int64)
    k = np.searchsorted(tl, ends, side='right') - 1                     # the last bin of the hold at or before each minute end
    rc = r_money(side, np.log(pv.px[a:b]) - lp0)
    mp = np.zeros((len(ends), 3))
    ok = k >= 0
    mp[ok, 0] = rc[k[ok]]; mp[ok, 1] = cmax0[k[ok]]; mp[ok, 2] = cmin0[k[ok]]
    out['minute_path'] = mp; out['minute_ends'] = ends
    return out


def trailing(pv, fill, side, trail, max_hold_s):
    """the first bin where the heat side crosses (the best offer so far from EARLIER bins, from 0) - trail; -1 when none"""
    a, b, t1 = _window(pv, fill, max_hold_s)
    lp0 = np.log(pv.px[fill.i])
    up_side, dn_side = (pv.hi, pv.lo) if side == 1 else (pv.lo, pv.hi)
    ro = r_money(side, np.log(up_side[a:b]) - lp0); rh = r_money(side, np.log(dn_side[a:b]) - lp0)
    if b <= a:
        return dict(touch_t=-1, anchor=0.0)
    anchor_prev = np.maximum(np.concatenate([[0.0], np.maximum.accumulate(ro)[:-1]]), 0.0)
    hit = np.round((rh - anchor_prev) / trail, 9) <= -1
    i = _first(hit)
    return dict(touch_t=int(pv.tl[a + i]) if i >= 0 else -1, anchor=float(anchor_prev[i]) if i >= 0 else float(anchor_prev[-1]), i=i)


def ladder_bench(pv, t_us, side, hold_s):
    """exec_v0.ladder (KA1 PASS) on a PriceView: closes only, log units, entry = the last close at or before t, CUT at a gap or END"""
    ts = pv.tl / 1e6; lp = np.log(pv.px)
    d = np.diff(ts); g = np.flatnonzero(d > 40); ga, gb = ts[g], ts[g + 1]
    t_from = t_us / 1e6; i0 = int(np.searchsorted(ts, t_from, side='right')) - 1
    t1 = t_from + hold_s
    out = {'cut': None}
    if i0 < 0 or t1 > ts[-1]:
        out['cut'] = 'END'; return out
    j1 = int(np.searchsorted(ts, t1, side='right'))
    if len(ga):
        m = (gb > t_from) & (ga < t1)
        if m.any():
            out['cut'] = 'GAP'
            j1 = min(j1, int(np.searchsorted(ts, ga[m].min(), side='right')))
    r = side * (lp[i0 + 1:j1] - lp[i0]) * 100.0
    out['n'] = len(r)
    if len(r) == 0:
        out.update(up=0.0, down=0.0); return out
    seg = lp[i0 + 1:j1]; out['up'] = float(seg.max() - lp[i0]); out['down'] = float(lp[i0] - seg.min())
    return out
