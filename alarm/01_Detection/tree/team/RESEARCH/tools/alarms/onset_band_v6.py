"""QUANT onset_band_v6 (= v5 f7f6af45 + Q4 BASIS JUMP, card alarms/Q4_BASIS_JUMP_CARD_V1.md eb124211: x = E3.S01(k) - E3.S01(k - L),
both rows finite (D - 1's last rows before k = L), |x| top q 99.9 (Q4), 99.5 (Q4b, beside), L 5 min (Q4c, beside); bench side = the
sign of x; M1 our bins' 60 s move has that sign, M2 the lab's C1.S10 at the minute end has it, M3 "lag|flat": a coin minute move beyond
its D - 1 median |r| at a minute end 1 to 5 min before, and the perp flat at t (|r| under that median)). onset_band_v5 (= v4 af9b49e6 + Q1 OFI BURST, card alarms/Q1_OFI_BURST_CARD_V1.md 477a74fd: X1.BOOKX.S04 |x| top
q 99.9 (Q1) and 99.5 (Q1b, beside); bench side = the book's sign; the 60 s price direction beside in <A>p_EVENTS.tsv; M1 the net
taker dollars B1.S09 of steps k - 1, k agree with the sign, M2 the price over the 10 s ending at t moved that way, M3 the trades under half
the OFI dollars X1.BOOKX.S03 x price). onset_band_v4 (= v3 f5bb4147 + the V2 cards of N3, N4, N9: a run of r steps past the edge (N3 V2 r 2, N9 V2 r 6),
the two-venue condition (N4 V2: Hyperliquid's E2.S06 the same sign), and their V2 D2 lines; alarms N3v2, N4v2, N9v2). onset_band_v3 (= v2 fb10ced9 + N2 M3 and its unit check in USD: the bins' buy and sell are quote dollars, J33319;
card N2 V2). onset_band_v2 (research desk, PLAN_TONIGHT_20261020_V1 phase 3; 20 Oct 2026; DRAFT, reviewer and rebuilder SCOUT). v2 = v1
4a3e02c9 + SCOUT's card review d01ffc26: N5 in dollars (5 x the rate rows), N2 M3 (a new block in our bins) and its unit check, N3 M3
(stayed thin), N4 D3 cadence, N9 M3 (no book reset); the m3 column.
THE OWN-BAND ONSET finder for the cards alarms/N2_WHALE_SWEEP, N3_BOOK_THINS, N4_OI_JUMP, N5_FLOW_BURST, N9_SPREAD_BLOWOUT (_CARD_V1.md;
rule index alarms/ONSET_RULE_QUANT_V1.txt): x(k) of one coin at the code's own clock; the edge of day D = a percentile of the coin's clean x
over its history days among the 14 built days before D (a history day: at least 70 pct of the day's columns clean; at least 2); FIRE at the
first step past the edge after a clean step not past it, more than 15 min after the coin's last fire, across midnight (from D - 1).
Side = the price direction over the 60 s ending at the fire (lab bins, the desk bench's reading); the code's own sign in its column.
D2 meaning columns per card (after the fact, never in the rule). Usage:
python3 onset_band_v1.py <alarm N2|N3|N4|N5|N9> <lab_days> <lab3 code dir> <out dir> <first day> <last day> <last readable day> <coin> ...
Writes <A>_EVENTS.tsv (coin t side S mode: the desk bench's input), <A>_FIRES.tsv (with the D2 columns), <A>_PROOF.txt (D1 per day)."""
import datetime, os, sys
import numpy as np

HIST_MAX, HIST_MIN, DAY_SHARE = 14, 2, 0.70
REFR_S = 900
REF_MAX, REF_MIN = 7, 2

ALARMS = {
    'N2': dict(code='B1.S06', band='top', q=99.0, floor=25000.0, xform='abs', sign='taker', extra=('B1.S04', 'B1.S01', 'B1.S02')),
    'N3': dict(code='D3.S01', band='bottom', q=1.0, floor=None, xform='pos', sign=None, extra=('X1.COST.S04', 'X1.COST.S05')),
    'N4': dict(code='E2.S04', band='top', q=99.0, floor=None, xform='abs', sign='oi', extra=('E2.S02', 'E2.S06')),
    'N5': dict(code='B1.S09', band='top', q=99.9, floor=None, xform='sum6abs', sign='taker', extra=('X1.BOOKX.S03',), scale=5.0),
    'N9': dict(code='X1.COST.S01', band='top', q=99.9, floor=None, xform='nonneg', sign=None, extra=('D3.S01',)),
    'N3v2': dict(code='D3.S01', band='bottom', q=1.0, floor=None, xform='pos', sign=None, extra=('X1.COST.S04', 'X1.COST.S05'), run=2),
    'N4v2': dict(code='E2.S04', band='top', q=99.0, floor=None, xform='abs', sign='oi', extra=('E2.S02', 'E2.S05'), cond='E2.S06'),
    'Q1': dict(code='X1.BOOKX.S04', band='top', q=99.9, floor=None, xform='abs', sign='book', extra=('B1.S09', 'X1.BOOKX.S03')),
    'Q1b': dict(code='X1.BOOKX.S04', band='top', q=99.5, floor=None, xform='abs', sign='book', extra=('B1.S09', 'X1.BOOKX.S03')),
    'Q4': dict(code='E3.S01', band='top', q=99.9, floor=None, xform='diff1abs', sign='book', extra=('C1.S10',), lag=1),
    'Q4b': dict(code='E3.S01', band='top', q=99.5, floor=None, xform='diff1abs', sign='book', extra=('C1.S10',), lag=1),
    'Q4c': dict(code='E3.S01', band='top', q=99.9, floor=None, xform='diff1abs', sign='book', extra=('C1.S10',), lag=5),
    'N9v2': dict(code='X1.COST.S01', band='top', q=99.9, floor=None, xform='nonneg', sign=None, extra=('D3.S01',), run=6),
}


def transform(v, xform):
    """v (n,) raw values (for sum6abs: with 5 earlier rows prepended by the caller) -> (x, raw sign source, clean mask)"""
    v = np.asarray(v, float)
    if xform == 'abs':
        ok = np.isfinite(v); return np.where(ok, np.abs(v), np.nan), v, ok
    if xform == 'pos':
        ok = np.isfinite(v) & (v > 0); return np.where(ok, v, np.nan), v, ok
    if xform == 'nonneg':
        ok = np.isfinite(v) & (v >= 0); return np.where(ok, v, np.nan), v, ok
    if xform == 'sum6abs':
        fin = np.isfinite(v); c = np.concatenate([[0.0], np.cumsum(np.where(fin, v, 0.0))]); m = np.concatenate([[0], np.cumsum(fin)])
        s = np.full(len(v), np.nan)
        if len(v) >= 6:
            ss = c[6:] - c[:-6]; mm = m[6:] - m[:-6]
            s[5:] = np.where(mm == 6, ss, np.nan)
        ok = np.isfinite(s); return np.where(ok, np.abs(s), np.nan), s, ok
    raise ValueError(xform)


def edges(hist, q, floor):
    """hist: list of (coins, steps) transformed arrays of the days before D (oldest first) -> (coins,) the edge; NaN when under 2 history
    days (a history day: at least DAY_SHARE of its columns clean for the coin); None when under 2 days were read; floor: max(edge, floor)"""
    if len(hist) < HIST_MIN:
        return None
    H = [np.asarray(h, float) for h in hist[-HIST_MAX:]]
    out = np.full(H[0].shape[0], np.nan)
    for i in range(H[0].shape[0]):
        vals = [h[i][np.isfinite(h[i])] for h in H]
        vals = [v for v, h in zip(vals, H) if len(v) >= DAY_SHARE * h.shape[1]]
        if len(vals) >= HIST_MIN:
            e = float(np.percentile(np.concatenate(vals), q))
            out[i] = max(e, floor) if floor is not None else e
    return out


def price_step(hist_rows):
    """N9 (card part 0 c3, SCOUT 19:14:27Z): the coin's price step in half-spread bps = the smallest positive value seen over its history
    rows (a list of 1-d arrays); NaN when none"""
    v = [h[np.isfinite(h) & (h > 0)] for h in hist_rows]
    v = [a for a in v if len(a)]
    return float(min(a.min() for a in v)) if v else np.nan


def past(x, edge, band):
    with np.errstate(invalid='ignore'):
        return (x > edge) if band == 'top' else (x < edge)


def fires_vec(x, prev_last, edge, band, last_k, refr_steps):
    """one coin-day: x (steps,) transformed, prev_last D-1's last transformed value (NaN if none), last_k the step of the coin's last fire
    counted from D 00:00 (None = none) -> fire steps"""
    if edge is None or not np.isfinite(edge):
        return []
    xx = np.concatenate([[prev_last], np.asarray(x, float)]); ok = np.isfinite(xx)
    p = past(xx, edge, band)
    cross = ok[1:] & p[1:] & ok[:-1] & ~p[:-1]
    out, last = [], last_k
    for k in np.flatnonzero(cross):
        if last is None or k - last > refr_steps:
            out.append(int(k)); last = int(k)
    return out


def fires_run(x, prev_x, edge, band, last_k, refr_steps, r=1, cond=None, prev_cond=None):
    """v4: FIRE at the first step k where the r steps k-r+1 .. k are all clean, past the edge and (cond) true, and step k-r is clean and
    not so; prev_x, prev_cond: D-1's last r values (NaN / False when not read); cond None = always true -> fire steps"""
    if edge is None or not np.isfinite(edge):
        return []
    x = np.asarray(x, float); n = len(x)
    px = np.full(r, np.nan) if prev_x is None else np.asarray(prev_x, float)[-r:]
    if len(px) < r:
        px = np.concatenate([np.full(r - len(px), np.nan), px])
    xx = np.concatenate([px, x]); ok = np.isfinite(xx)
    cc = np.ones(len(xx), bool)
    if cond is not None:
        pc = np.zeros(r, bool) if prev_cond is None else np.asarray(prev_cond, bool)[-r:]
        if len(pc) < r:
            pc = np.concatenate([np.zeros(r - len(pc), bool), pc])
        cc = np.concatenate([pc, np.asarray(cond, bool)])
    P = ok & past(xx, edge, band) & cc
    allr = np.ones(n, bool)
    for s in range(r):
        allr &= P[r - s:r - s + n]
    cross = allr & ok[0:n] & ~P[0:n]
    out, last = [], last_k
    for k in np.flatnonzero(cross):
        if last is None or k - last > refr_steps:
            out.append(int(k)); last = int(k)
    return out


def fires_run_loop(x, prev_x, edge, band, last_k, refr_steps, r=1, cond=None, prev_cond=None):
    """D1: the V2 cards' words at every step"""
    if edge is None or not (edge == edge):
        return []
    px = [float('nan')] * r if prev_x is None else list(prev_x)[-r:]
    px = [float('nan')] * (r - len(px)) + px
    xx = px + [float(v) for v in x]
    if cond is None:
        cc = [True] * len(xx)
    else:
        pc = [False] * r if prev_cond is None else [bool(v) for v in list(prev_cond)[-r:]]
        pc = [False] * (r - len(pc)) + pc
        cc = pc + [bool(v) for v in cond]
    def P(j):
        v = xx[j]
        return v == v and ((v > edge) if band == 'top' else (v < edge)) and cc[j]
    out, last = [], last_k
    for k in range(len(x)):
        j = k + r
        if all(P(j - s) for s in range(r)) and xx[j - r] == xx[j - r] and not P(j - r) and (last is None or k - last > refr_steps):
            out.append(k); last = k
    return out


def fires_loop(x, prev_last, edge, band, last_k, refr_steps):
    """D1: the card's words at every step"""
    if edge is None or not (edge == edge):
        return []
    out, last = [], last_k
    for k in range(len(x)):
        a = float(x[k]); b = float(prev_last) if k == 0 else float(x[k - 1])
        pa = (a > edge) if band == 'top' else (a < edge); pb = (b > edge) if band == 'top' else (b < edge)
        if a == a and b == b and pa and not pb and (last is None or k - last > refr_steps):
            out.append(k); last = k
    return out


# ---- prices (lab bins as the desk bench reads them) and D2 helpers
def last_px(tl, px, t):
    i = np.searchsorted(tl, t, 'right') - 1
    return float(px[i]) if i >= 0 else np.nan


def move_sign(tl, px, t, w):
    a, b = last_px(tl, px, t - w), last_px(tl, px, t)
    return 0 if not (a == a and b == b) or a == b else (1 if b > a else -1)


def range_bp(tl, px, hi, lo, t):
    a, b = np.searchsorted(tl, t - 60, 'right'), np.searchsorted(tl, t, 'right'); p0 = last_px(tl, px, t - 60)
    if b <= a or not p0 == p0 or p0 <= 0:
        return np.nan
    return float((hi[a:b].max() - lo[a:b].min()) / p0 * 1e4)


def day_median_range(tl, px, hi, lo, t0):
    if len(tl) == 0:
        return np.nan
    m = t0 + 60.0 * np.arange(1, 1441)
    a = np.searchsorted(tl, m - 60, 'right'); b = np.searchsorted(tl, m, 'right'); idx = np.flatnonzero(b > a)
    if len(idx) == 0:
        return np.nan
    end = b[idx[-1]]
    mx = np.maximum.reduceat(hi[:end], a[idx]); mn = np.minimum.reduceat(lo[:end], a[idx])
    p0 = np.array([last_px(tl, px, u - 60) for u in m[idx]]); ok = np.isfinite(p0) & (p0 > 0)
    return float(np.median((mx[ok] - mn[ok]) / p0[ok]) * 1e4) if ok.any() else np.nan


def day_median_move10(tl, px, t0):
    """N4 V2 M2's reference: the median over D's minute ends m of |the price move from m - 600 to m| in bp (last prices at or before)"""
    if len(tl) == 0:
        return np.nan
    m = t0 + 60.0 * np.arange(10, 1441)
    i1 = np.searchsorted(tl, m, 'right') - 1; i0 = np.searchsorted(tl, m - 600, 'right') - 1
    ok = (i1 >= 0) & (i0 >= 0)
    if not ok.any():
        return np.nan
    a, b = px[i0[ok]], px[i1[ok]]
    return float(np.median(np.abs(b / a - 1.0)) * 1e4)


def sgn(v):
    return 0 if not (v == v) or v == 0 else (1 if v > 0 else -1)


def shift(D, k):
    return (datetime.datetime.strptime(D, '%Y%m%d') + datetime.timedelta(days=k)).strftime('%Y%m%d')


def day0(D):
    return int(datetime.datetime.strptime(D, '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp())


def day_list(first, last, before):
    d, e, out = shift(first, -before), last, []
    while d <= e:
        out.append(d); d = shift(d, 1)
    return out


def read_code(R, code, D, coins):
    """-> (coins, steps) values of the code on day D (NaN rows for coins the part lacks); None when the code is not built that day"""
    try:
        zc = list(R.index(D, R.part_of(code, D))['coins'])
    except Exception:
        return None
    got = [c for c in coins if c in zc]
    if not got:
        return None
    v = np.asarray(R.read(code, 'v', [D], got)[0], float)
    a = np.full((len(coins), v.shape[1]), np.nan)
    for j, c in enumerate(got):
        a[coins.index(c)] = v[j]
    return a


def main(alarm, root, code_dir, out_dir, first, last, last_ok, coins):
    A = ALARMS[alarm]
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); os.makedirs(out_dir, exist_ok=True)
    days = [d for d in day_list(first, last, HIST_MAX + 1) if d in have and d <= last_ok]
    hist, refs = [], {c: [] for c in coins}
    last_t = {c: None for c in coins}; prev_raw = None; prev_cond = None; prev_x = np.full(len(coins), np.nan); prev_day = None
    ev = open(os.path.join(out_dir, '%s_EVENTS.tsv' % alarm), 'x'); ev.write('coin\tt\tside\tS\tmode\n')
    evp = None
    if A['sign'] == 'book':
        evp = open(os.path.join(out_dir, '%sp_EVENTS.tsv' % alarm), 'x'); evp.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, '%s_FIRES.tsv' % alarm), 'x')
    fr.write('coin\tt\tday\tk\tside\tsign\tx\tedge\tm1\tm2\tm3\n')
    proof = open(os.path.join(out_dir, '%s_PROOF.txt' % alarm), 'x')
    for D in days:
        t0 = day0(D); consecutive = prev_day is not None and day0(prev_day) + 86400 == t0
        raw = read_code(R, A['code'], D, coins)
        if raw is None:
            raw = np.full((len(coins), 17280 if A['code'] in ('B1.S09', 'X1.COST.S01', 'X1.BOOKX.S04') else 1440), np.nan)
        steps = raw.shape[1]; clock = 86400 // steps; refr = REFR_S // clock
        if A['xform'] == 'sum6abs':
            lead = prev_raw[:, -5:] if consecutive and prev_raw is not None and prev_raw.shape[1] == steps else np.full((len(coins), 5), np.nan)
            X, S, OK = [], [], []
            sc = A.get('scale', 1.0)
            for i in range(len(coins)):
                x, s, ok = transform(np.concatenate([lead[i], raw[i]]), 'sum6abs'); X.append(sc * x[5:]); S.append(sc * s[5:])
            X = np.array(X); SG = np.array(S)
        elif A['xform'] == 'diff1abs':
            L = A['lag']
            lead = prev_raw[:, -L:] if consecutive and prev_raw is not None and prev_raw.shape[1] == steps else np.full((len(coins), L), np.nan)
            vv = np.concatenate([lead, raw], axis=1); SG = vv[:, L:] - vv[:, :-L]; X = np.abs(SG)
        else:
            X = np.empty_like(raw); SG = raw.copy()
            for i in range(len(coins)):
                X[i] = transform(raw[i], A['xform'])[0]
        if not consecutive:
            prev_x[:] = np.nan
        E = edges(hist, A['q'], A['floor'])
        write = D >= first
        need_px = write or alarm in ('N9', 'N9v2')
        rr = A.get('run', 1); COND = None
        if A.get('cond'):
            c6 = read_code(R, A['cond'], D, coins)
            c6 = np.full(raw.shape, np.nan) if c6 is None or c6.shape != raw.shape else c6
            with np.errstate(invalid='ignore'):
                COND = np.isfinite(c6) & (c6 != 0) & (np.sign(c6) == np.sign(raw))
        prevX = hist[-1] if (consecutive and hist and hist[-1].shape == X.shape) else None
        prevC = prev_cond if (consecutive and prev_cond is not None and COND is not None and prev_cond.shape == COND.shape) else None
        if need_px:
            seq = [d for d in (shift(D, -1), D, shift(D, 1)) if d in have and d <= last_ok]
            px = {}
            for d in seq:
                off, b = LB.read_bins(R, d, coins)
                for i, c in enumerate(coins):
                    s, e = off[i], off[i + 1]; m = b['n'][s:e] > 0
                    px.setdefault(c, []).append((b['tl'][s:e][m] / 1e6, b['px'][s:e][m], b['hi'][s:e][m], b['lo'][s:e][m],
                                                 np.asarray(b['buy'][s:e][m], float), np.asarray(b['sell'][s:e][m], float)))
        extra = {}
        if write:
            for code in A['extra']:
                blocks = [read_code(R, code, d, coins) if (d in have and d <= last_ok) else None for d in (shift(D, -1), D, shift(D, 1))]
                st = next((b.shape[1] for b in blocks if b is not None), None)
                if st is not None:
                    extra[code] = (np.concatenate([b if b is not None else np.full((len(coins), st), np.nan) for b in blocks], axis=1), st)
        n_same = n_diff = n_f = 0; unit_ratio = None; two_steps = [0, 0]
        cad = None
        if write and alarm == 'N4':
            fin = np.isfinite(raw[:, 1:]) & np.isfinite(raw[:, :-1])
            cad = float((raw[:, 1:] != raw[:, :-1])[fin].mean()) if fin.any() else float('nan')
        for i, c in enumerate(coins):
            edge = None if E is None else E[i]
            lk = None if last_t[c] is None else int(round((last_t[c] - t0) / clock))
            if rr > 1 or COND is not None:
                args = (X[i], None if prevX is None else prevX[i], edge, A['band'], lk, refr, rr,
                        None if COND is None else COND[i], None if prevC is None else prevC[i])
                ks = fires_run(*args)
                if write and i % 4 == 0:
                    same = ks == fires_run_loop(*args); n_same += same; n_diff += (not same)
            else:
                ks = fires_vec(X[i], prev_x[i], edge, A['band'], lk, refr)
                if write and i % 4 == 0:
                    same = ks == fires_loop(X[i], prev_x[i], edge, A['band'], lk, refr); n_same += same; n_diff += (not same)
            if need_px:
                tl = np.concatenate([p[0] for p in px[c]]); pp = np.concatenate([p[1] for p in px[c]])
                hh = np.concatenate([p[2] for p in px[c]]); ll = np.concatenate([p[3] for p in px[c]]); o = np.argsort(tl, kind='stable')
                bb = np.concatenate([p[4] for p in px[c]]); ss_ = np.concatenate([p[5] for p in px[c]])
                tl, pp, hh, ll, bb, ss_ = tl[o], pp[o], hh[o], ll[o], bb[o], ss_[o]
                if write and alarm == 'N2' and c == 'BTC':
                    unit_ratio = n2_unit_ratio(extra, i, tl, pp, bb, ss_, t0)
            if write:
                r7 = refs[c][-REF_MAX:]; ref = float(np.median(r7)) if len([v for v in r7 if v == v]) >= REF_MIN else np.nan
                for k in ks:
                    t = t0 + clock * k; side = move_sign(tl, pp, t, 60); own = sgn(SG[i][k]) if A['sign'] else 0
                    rawc = np.concatenate([prev_raw[i] if (consecutive and prev_raw is not None and prev_raw.shape[1] == steps) else np.full(steps, np.nan), raw[i]])
                    m1, m2, m3 = d2(alarm, extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, X[i], raw[i], last_ok, D, bb, ss_, rawc)
                    if evp is not None:
                        evp.write('%s\t%d\t%d\t%.4f\t%s\n' % (c, t, side, float(X[i][k] / edge) if edge else np.nan, alarm + 'p'))
                        side = own
                    ev.write('%s\t%d\t%d\t%.4f\t%s\n' % (c, t, side, float(X[i][k] / edge) if edge else np.nan, alarm))
                    g = lambda v: '' if v is None or v != v else ('%.4f' % v if isinstance(v, float) else str(v))
                    fr.write('%s\t%d\t%s\t%d\t%d\t%d\t%.4f\t%.4f\t%s\t%s\t%s\n' % (c, t, D, k, side, own, X[i][k], edge, g(m1), g(m2), g(m3)))
                    n_f += 1
                    if alarm in ('N9', 'N9v2'):
                        stp = price_step([h[i] for h in hist[-HIST_MAX:]])
                        if stp == stp:
                            two_steps[1] += 1; two_steps[0] += int(X[i][k] <= 2 * stp * (1 + 1e-9))
            if ks:
                last_t[c] = t0 + clock * ks[-1]
            if alarm in ('N9', 'N9v2') and need_px:
                sel = (tl > t0) & (tl <= t0 + 86400)
                refs[c].append(day_median_range(tl[sel], pp[sel], hh[sel], ll[sel], t0))
            prev_x[i] = X[i][-1]
        hist.append(X); hist = hist[-HIST_MAX:]; prev_raw = raw; prev_day = D; prev_cond = COND
        if write:
            line = 'DAY %s coins %d steps %d edge %s fires %d D1 same %d differ %d' % (D, len(coins), steps, 'none' if E is None else 'yes',
                                                                                n_f, n_same, n_diff)
            if alarm == 'N2':
                line += ' unit_ratio_BTC %s' % ('none' if unit_ratio is None or unit_ratio != unit_ratio else '%.3f' % unit_ratio)
            if alarm == 'N4':
                line += ' cadence_changed %.3f' % cad
            if alarm in ('N9', 'N9v2'):
                line += ' fires_at_most_2_steps %d of %d' % tuple(two_steps)
            proof.write(line + '\n'); print(line, flush=True)
    ev.close(); fr.close(); proof.close()
    if evp is not None:
        evp.close()


def n2_unit_ratio(extra, i, tl, pp, bb, ss_, t0):
    """N2's unit check (card M3): over the day's minute ends, the median of sum((buy + sell) x px) of the bins in the minute over
    B1.S01 + B1.S02 of that minute (both USD if buy and sell are in coins)"""
    if 'B1.S01' not in extra or 'B1.S02' not in extra:
        return np.nan
    a1, st = extra['B1.S01']; a2, _ = extra['B1.S02']
    cs = np.concatenate([[0.0], np.cumsum(bb + ss_)]); r = []
    for j in range(1, 1440):
        u = t0 + 60 * j; v = a1[i][st + j] + a2[i][st + j]
        if np.isfinite(v) and v > 0:
            got = cs[np.searchsorted(tl, u, 'right')] - cs[np.searchsorted(tl, u - 60, 'right')]
            r.append(got / v)
    return float(np.median(r)) if r else np.nan


def d2(alarm, extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, x, raw, last_ok, D, bb=None, ss_=None, rawc=None):
    """-> (m1, m2, m3) for one fire; None when not measurable (a cut window counts as None)"""
    m1, m2 = d2_v1(alarm, extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, x, raw, last_ok, D)
    m3 = None
    t0 = day0(D)
    if alarm == 'N2' and own != 0 and bb is not None:
        a, b = np.searchsorted(tl, t - 60, 'right'), np.searchsorted(tl, t, 'right')
        vol = (bb if own > 0 else ss_)[a:b]
        m3 = int(bool((vol >= 25000.0).any()))
    if alarm == 'N3' and rawc is not None and k + 1 < len(raw):
        kk = steps + k; w = rawc[kk - 60:kk]; w = w[np.isfinite(w) & (w > 0)]
        nxt = raw[k + 1]
        m3 = None if len(w) == 0 or not (np.isfinite(nxt) and nxt > 0) else int(nxt < np.median(w))
    if alarm == 'N3v2':
        m1 = d2_v1('N3', extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, x, raw, last_ok, D)[0]
        kk = steps + k
        a, b = rawc[kk - 2] if rawc is not None else np.nan, raw[k + 1] if k + 1 < len(raw) else np.nan
        m2 = None if k + 1 >= len(raw) else int(bool(np.isfinite(a) and a > 0 and np.isfinite(b) and b > 0))
        w = rawc[kk - 1 - 60:kk - 1] if rawc is not None else np.array([]); w = w[np.isfinite(w) & (w > 0)]
        m3 = None if (k + 1 >= len(raw) or len(w) == 0 or not (np.isfinite(b) and b > 0)) else int(b < np.median(w))
        return m1, m2, m3
    if alarm == 'N4v2':
        m1 = d2_v1('N4', extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, x, raw, last_ok, D)[0]
        def at5(u):
            if 'E2.S05' not in extra:
                return np.nan
            arr, st = extra['E2.S05']; c = int((u - t0) // (86400 // st)) + st
            return float(arr[i][c]) if 0 <= c < arr.shape[1] else np.nan
        h1, h0 = at5(t), at5(t - 600)                    # SCOUT 19:26:41Z: a positions record, not the price
        m2 = None if not (h1 == h1 and h0 == h0) or own == 0 or h1 == h0 else int(sgn(h1 - h0) == own)
        return m1, m2, None
    if alarm in ('Q1', 'Q1b'):
        return q1_d2(extra, i, k, t, t0, tl, pp, own)
    if alarm in ('Q4', 'Q4b', 'Q4c'):
        return q4_d2(extra, i, k, t, t0, tl, pp, own)
    if alarm == 'N9v2':
        r_ = range_bp(tl, pp, hh, ll, t); m1 = None if not (r_ == r_ and ref == ref) else int(r_ > ref)
        if k + 6 >= len(raw):
            m2 = None
        else:
            w = raw[max(k - 5 - 720, 0):max(k - 5, 0)]; w = w[np.isfinite(w)]
            m2 = None if len(w) == 0 or not np.isfinite(raw[k + 6]) else int(raw[k + 6] > np.median(w))
        arr, st = extra['D3.S01'] if 'D3.S01' in extra else (None, None)
        if arr is None:
            m3 = None
        else:
            c = int((t - t0) // 60) + st; v = arr[i][c] if 0 <= c < arr.shape[1] else np.nan
            m3 = int(bool(np.isfinite(v) and v > 0))
        return m1, m2, m3
    if alarm == 'N9' and 'D3.S01' in extra:
        arr, st = extra['D3.S01']; c = int((t - t0) // 60) + st
        v = arr[i][c] if 0 <= c < arr.shape[1] else np.nan
        m3 = int(bool(np.isfinite(v) and v > 0))
    return m1, m2, m3


def r60(tl, pp, u):
    a, b = last_px(tl, pp, u - 60), last_px(tl, pp, u)
    return np.nan if not (a == a and b == b) or a <= 0 or b <= 0 else float(np.log(b / a))


def q4_d2(extra, i, k, t, t0, tl, pp, own):
    """Q4 card s0 d, s4 and items: (m1, m2, 'lag|flat'); the reference |r| = the median |r| over D - 1's minute ends"""
    if own == 0:
        return None, None, None
    mv = move_sign(tl, pp, t, 60); m1 = None if mv == 0 else int(mv == own)
    m2 = None
    if 'C1.S10' in extra:
        arr, st = extra['C1.S10']; v = arr[i][st + k]
        m2 = None if not np.isfinite(v) or v == 0 else int(sgn(v) == own)
    ref = [abs(r60(tl, pp, t0 - 86400 + 60 * j)) for j in range(1, 1441)]
    ref = [x for x in ref if x == x]
    if len(ref) < 1000:
        return m1, m2, None
    med = float(np.median(ref)); rt = r60(tl, pp, t)
    lag = int(any(abs(r60(tl, pp, t - 60 * q)) > med for q in range(1, 6) if r60(tl, pp, t - 60 * q) == r60(tl, pp, t - 60 * q)))
    flat = '' if rt != rt else str(int(abs(rt) < med))
    return m1, m2, '%d|%s' % (lag, flat)


def q1_d2(extra, i, k, t, t0, tl, pp, own):
    """Q1 card s4 and items: (m1, m2, m3); None when not measurable or the book's sign is 0"""
    if own == 0:
        return None, None, None
    m1 = m3 = None
    if 'B1.S09' in extra:
        arr, st = extra['B1.S09']; a, b = arr[i][st + k - 1], arr[i][st + k]
        if np.isfinite(a) and np.isfinite(b):
            net = 5.0 * (a + b)
            m1 = None if net == 0 else int(sgn(net) == own)
            if 'X1.BOOKX.S03' in extra:
                o, so = extra['X1.BOOKX.S03']; ofi = o[i][so + k]; p = last_px(tl, pp, t)
                if np.isfinite(ofi) and p == p:
                    m3 = int(abs(net) < 0.5 * abs(ofi * p))
    mv = move_sign(tl, pp, t, 10)
    m2 = None if mv == 0 else int(mv == own)
    return m1, m2, m3


def d2_v1(alarm, extra, i, k, steps, clock, t, tl, pp, hh, ll, own, ref, x, raw, last_ok, D):
    """-> (m1, m2) for one fire (v1's lines); None when not measurable (a cut window counts as None)"""
    t0 = day0(D)
    def at(code, u):
        """the code's value of coin i known at time u (its own clock; D-1 .. D+1 only), NaN when outside or not read"""
        if code not in extra:
            return np.nan
        arr, st = extra[code]; c = int((u - t0) // (86400 // st)) + st
        return float(arr[i][c]) if 0 <= c < arr.shape[1] else np.nan
    if alarm == 'N2':
        m1 = None if own == 0 else int(move_sign(tl, pp, t, 60) == own)
        v = at('B1.S04', t); m2 = None if v != v else int(v != 0)
        return m1, m2
    if alarm == 'N3':
        cost = lambda u: np.nanmax([at('X1.COST.S04', u), at('X1.COST.S05', u)]) if np.isfinite([at('X1.COST.S04', u), at('X1.COST.S05', u)]).any() else np.nan
        w = np.array([cost(t - 5 * j) for j in range(1, 721)]); w = w[np.isfinite(w)]; now = cost(t)
        m1 = None if not (now == now) or len(w) == 0 else int(now > np.median(w))
        if k + 1 >= len(raw) or k < 1:
            return m1, None
        a, b = raw[k - 1], raw[k + 1]
        return m1, int(bool(np.isfinite(a) and a > 0 and np.isfinite(b) and b > 0))
    if alarm == 'N4':
        lv, lv0 = at('E2.S02', t), at('E2.S02', t - 600)
        m1 = None if not (lv == lv and lv0 == lv0) or own == 0 or lv == lv0 else int(sgn(lv - lv0) == own)
        h = at('E2.S06', t); m2 = None if not (h == h) or own == 0 or h == 0 else int(sgn(h) == own)
        return m1, m2
    if alarm == 'N5':
        m1 = None if own == 0 else int(move_sign(tl, pp, t, 30) == own)
        o = at('X1.BOOKX.S03', t); m2 = None if not (o == o) or own == 0 or o == 0 else int(sgn(o) == own)
        return m1, m2
    if alarm == 'N9':
        r = range_bp(tl, pp, hh, ll, t); m1 = None if not (r == r and ref == ref) else int(r > ref)
        if k + 6 >= len(raw):
            return m1, None
        w = raw[max(k - 720, 0):k]; w = w[np.isfinite(w)]
        m2 = None if len(w) == 0 or not np.isfinite(raw[k + 6]) else int(raw[k + 6] > np.median(w))
        return m1, m2
    return None, None


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7:])
