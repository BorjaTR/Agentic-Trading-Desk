"""QUANT n1_busy_burst_v2 (research desk, card alarms/N1_BUSY_BURST_CARD_V2.md; 20 Oct 2026; DRAFT, reviewer SCOUT). v2 = v1 (9c1880a2) +
the bar of the hour: the step must also be above HOUR_X times the median of the coin's last 60 clean minute ends before it (v1 fired
every 15 min on a day busy all day: J33317, 4 Nov 2025, M1 54.8 pct).
N1 BUSY BURST: the first 5 s step at which a coin's Binance trades in the last minute (X1.FLOWX.S10) rise above the coin's own edge
(the 99th percentile of its minute-end values over its history days among the 14 UTC days before, at least 2; a history day
has at least 1,000 clean minute ends), after a clean step at or under it, with a
15 min refractory per coin across midnight. Side = the price direction over the 60 s ending at the fire (lab bins). S = x / edge.
Meaning beside (never in the rule): M1 our bins' trades in the 60 s ending at the fire over their median at the 60 minute ends m = t - 60 i, i = 1 .. 60
(each window (m - 60, m], so m in [t - 3600, t - 60]); M2 the 60 s
range at the fire over the median of the up to 7 days before's daily medians of minute-end 60 s ranges (at least 2 days).
Usage: python3 n1_busy_burst_v1.py <lab_days> <lab3 code dir> <out dir> <first day> <last day> <coin> [<coin> ...]
Writes N1_EVENTS.tsv (coin t side S mode: the desk bench's input), N1_FIRES.tsv (with the meaning columns), N1_PROOF.txt (D1 per day)."""
import datetime, os, sys
import numpy as np

STEP = 5                      # s, the 5 s clock
DAY_STEPS = 17280
MIN_STEPS = 12                # a minute end every 12 steps
EDGE_Q = 99.0
HIST_MAX, HIST_MIN = 14, 2    # days of edge history
DAY_MIN = 1000                # clean minute ends that make a history day
REF_MAX, REF_MIN = 7, 2       # days of M2 reference history
REFR = 180                    # steps (15 min)
CODE = 'X1.FLOWX.S10'
HOUR_X = 2.0                  # v2: the bar of the hour
HOUR_N, HOUR_MIN = 60, 30     # the last 60 minute ends, at least 30 clean


def clean(x):
    x = np.asarray(x, float)
    return np.isfinite(x) & (x >= 0)


def minute_ends(a):
    """(coins, 17280) -> (coins, 1440): the columns 12 j"""
    return np.asarray(a, float)[..., ::MIN_STEPS]


def edges(hist):
    """hist: list of (coins, 1440) minute-end arrays of the days before D, oldest first -> (coins,) EDGE_Q percentile of the clean values
    of the coin's HISTORY DAYS among the last HIST_MAX days (a history day has at least DAY_MIN clean minute ends for that coin; SCOUT
    18:42:16Z item 1); NaN for a coin with fewer than HIST_MIN history days; None when fewer than HIST_MIN days were read at all"""
    if len(hist) < HIST_MIN:
        return None
    H = [np.asarray(h, float) for h in hist[-HIST_MAX:]]
    out = np.full(H[0].shape[0], np.nan)
    for i in range(H[0].shape[0]):
        vals = [h[i][clean(h[i])] for h in H]
        vals = [v for v in vals if len(v) >= DAY_MIN]
        if len(vals) >= HIST_MIN:
            out[i] = np.percentile(np.concatenate(vals), EDGE_Q)
    return out


def hour_bar(me_prev, me_day):
    """me_prev, me_day: (1440,) minute-end values of D-1 (NaN if not read) and D -> (17280,) the bar of the hour at each step k of D:
    HOUR_X x the median of the clean values among the last HOUR_N minute ends strictly before k (D-1's included), NaN under HOUR_MIN"""
    me = np.concatenate([np.asarray(me_prev, float), np.asarray(me_day, float)])
    me = np.where(clean(me), me, np.nan)
    per_j = np.full(1441, np.nan)                     # per_j[q] = the bar from the minute ends 1440 + q - HOUR_N .. 1440 + q - 1
    for q in range(1441):
        w = me[1440 + q - HOUR_N:1440 + q]; w = w[np.isfinite(w)]
        if len(w) >= HOUR_MIN:
            per_j[q] = HOUR_X * float(np.median(w))
    k = np.arange(DAY_STEPS)
    return per_j[(k + MIN_STEPS - 1) // MIN_STEPS]    # minute ends strictly before k: columns 12 j < k, so j <= (k - 1) // 12


def fires_vec(x, prev_last, edge, last_fire_k, hbar=None):
    """one coin-day: x (17280,) the day's values, prev_last the value of D-1's last step (NaN if none), edge the day's edge, last_fire_k the
    step of the coin's last fire counted from D 00:00 (negative = on D-1; None = none), hbar (17280,) the bar of the hour (v2) ->
    fire steps k (0 .. 17279): x(k) > E(k) = max(edge, hbar(k)) and x(k-1) clean and <= E(k)"""
    if edge is None or not np.isfinite(edge):
        return []
    E = np.full(len(x), float(edge)) if hbar is None else np.where(np.isfinite(hbar), np.maximum(edge, hbar), np.nan)
    xx = np.concatenate([[prev_last], np.asarray(x, float)])
    ok = clean(xx)
    with np.errstate(invalid='ignore'):
        cross = ok[1:] & np.isfinite(E) & (xx[1:] > E) & ok[:-1] & (xx[:-1] <= E)
    out, last = [], last_fire_k
    for k in np.flatnonzero(cross):
        if last is None or k - last > REFR:
            out.append(int(k)); last = int(k)
    return out


def fires_loop(x, prev_last, edge, last_fire_k, me_prev=None, me_day=None):
    """D1: the card's words read literally at every step (the bar of the hour recomputed at each step from the minute ends)"""
    if edge is None or not (edge == edge):
        return []
    out, last = [], last_fire_k
    me = None if me_day is None else list(me_prev) + list(me_day)
    for k in range(len(x)):
        e = edge
        if me is not None:
            jl = 1440 + (k - 1) // 12                     # the last minute end strictly before k
            w = [v for v in me[jl - HOUR_N + 1:jl + 1] if v == v and v >= 0]
            if len(w) < HOUR_MIN:
                continue
            e = max(edge, HOUR_X * float(np.median(w)))
        a = float(x[k]); b = float(prev_last) if k == 0 else float(x[k - 1])
        a_ok = a == a and a >= 0; b_ok = b == b and b >= 0
        if a_ok and b_ok and a > e and b <= e and (last is None or k - last > REFR):
            out.append(k); last = k
    return out


def seg_counts(tl, n, t1, t2):
    """trades (sum of n) of bins with tl in (t1, t2], vectorised over t1, t2 arrays; tl sorted (s)"""
    cs = np.concatenate([[0], np.cumsum(n)])
    return cs[np.searchsorted(tl, t2, 'right')] - cs[np.searchsorted(tl, t1, 'right')]


def last_px(tl, px, t):
    i = np.searchsorted(tl, t, 'right') - 1
    return np.where(i >= 0, px[np.maximum(i, 0)], np.nan)


def range_bp(tl, px, hi, lo, t):
    """the 60 s range ending at t: (highest hi - lowest lo) of bins with tl in (t - 60, t] over the last price at or before t - 60, bp"""
    a, b = np.searchsorted(tl, t - 60, 'right'), np.searchsorted(tl, t, 'right')
    p0 = last_px(tl, px, t - 60)
    if b <= a or not np.isfinite(p0) or p0 <= 0:
        return np.nan
    return float((hi[a:b].max() - lo[a:b].min()) / p0 * 1e4)


def day_median_range(tl, px, hi, lo, t0):
    """the median of the 60 s ranges at the day's minute ends t0 + 60 j, j = 1 .. 1440 (empty minutes skipped), bp. The minute windows
    (m - 60, m] partition the day, so each non-empty minute is one reduceat segment"""
    if len(tl) == 0:
        return np.nan
    m = t0 + 60.0 * np.arange(1, 1441)
    a = np.searchsorted(tl, m - 60, 'right'); b = np.searchsorted(tl, m, 'right')
    idx = np.flatnonzero(b > a)
    if len(idx) == 0:
        return np.nan
    end = b[idx[-1]]
    mx = np.maximum.reduceat(hi[:end], a[idx]); mn = np.minimum.reduceat(lo[:end], a[idx])
    p0 = last_px(tl, px, m[idx] - 60)
    ok = np.isfinite(p0) & (p0 > 0)
    if not ok.any():
        return np.nan
    return float(np.median((mx[ok] - mn[ok]) / p0[ok]) * 1e4)


def day_median_range_loop(tl, px, hi, lo, t0):
    """the same, one minute at a time (the test's oracle)"""
    r = []
    for j in range(1, 1441):
        v = range_bp(tl, px, hi, lo, t0 + 60.0 * j)
        if v == v:
            r.append(v)
    return float(np.median(r)) if r else np.nan


def meaning(tl, n, px, hi, lo, t, ref):
    """-> (side, n_ratio, rng, ref) for a fire at t (s)"""
    p1, p0 = last_px(tl, px, t), last_px(tl, px, t - 60)
    side = 0 if not (np.isfinite(p1) and np.isfinite(p0)) or p1 == p0 else (1 if p1 > p0 else -1)
    now = seg_counts(tl, n, np.array([t - 60.0]), np.array([t]))[0]
    m = t - 60.0 * np.arange(1, 61)
    med = float(np.median(seg_counts(tl, n, m - 60, m)))
    ratio = float(now / med) if med > 0 else (np.inf if now > 0 else np.nan)
    return side, ratio, range_bp(tl, px, hi, lo, t), ref


def day_list(first, last, before):
    d0 = datetime.datetime.strptime(first, '%Y%m%d') - datetime.timedelta(days=before)
    d1 = datetime.datetime.strptime(last, '%Y%m%d'); out = []
    while d0 <= d1:
        out.append(d0.strftime('%Y%m%d')); d0 += datetime.timedelta(days=1)
    return out


def day0_s(D):
    return datetime.datetime.strptime(D, '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp()


def main(root, code_dir, out_dir, first, last, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days())
    os.makedirs(out_dir, exist_ok=True)
    days = [d for d in day_list(first, last, HIST_MAX + 1) if d in have]
    hist, refs = [], {c: [] for c in coins}       # minute-end arrays of past days; per coin the past daily median ranges
    last_t = {c: None for c in coins}             # the time (s) of the coin's last fire
    prev_last = np.full(len(coins), np.nan); prev_day = None; prev_me = None
    ev, fr, proof = [], [], []
    for D in days:
        t0 = day0_s(D)
        if prev_day is None or day0_s(prev_day) + 86400 != t0:
            prev_last[:] = np.nan                     # D-1 not read: no crossing at k = 0
            prev_me = None
        zc = list(R.index(D, R.part_of(CODE, D))['coins'])
        ask = [c for c in coins if c in zc]
        a = np.full((len(coins), DAY_STEPS), np.nan)
        if ask:
            got = R.read(CODE, 'v', [D], ask)[0]
            for i, c in enumerate(coins):
                if c in ask:
                    a[i] = got[ask.index(c)]
        E = edges(hist)
        off, b = LB.read_bins(R, D, coins)
        n_same = n_diff = n_f = 0
        for i, c in enumerate(coins):
            s, e = off[i], off[i + 1]
            keep = b['n'][s:e] > 0
            tl = b['tl'][s:e][keep] / 1e6; n = b['n'][s:e][keep].astype(float)
            px = b['px'][s:e][keep]; hi = b['hi'][s:e][keep]; lo = b['lo'][s:e][keep]
            o = np.argsort(tl, kind='stable'); tl, n, px, hi, lo = tl[o], n[o], px[o], hi[o], lo[o]
            edge = None if E is None else E[i]
            lk = None if last_t[c] is None else int(round((last_t[c] - t0) / STEP))
            mprev = prev_me[i] if prev_me is not None else np.full(1440, np.nan)
            hb = hour_bar(mprev, minute_ends(a[i]))
            ks = fires_vec(a[i], prev_last[i], edge, lk, hb)
            if D >= first and i % 4 == 0:
                same = ks == fires_loop(a[i], prev_last[i], edge, lk, mprev, minute_ends(a[i])); n_same += same; n_diff += (not same)
            r7 = refs[c][-REF_MAX:]; ref = float(np.median(r7)) if len([v for v in r7 if v == v]) >= REF_MIN else np.nan
            if D >= first:
                for k in ks:
                    t = t0 + STEP * k
                    side, ratio, rng, _ = meaning(tl, n, px, hi, lo, t, ref)
                    ev.append((c, t, side, float(a[i][k] / max(edge, hb[k])), 'BURST'))
                    fr.append((c, t, D, k, side, float(a[i][k]), float(edge), ratio, rng, ref))
                    n_f += 1
            if ks:
                last_t[c] = t0 + STEP * ks[-1]
            refs[c].append(day_median_range(tl, px, hi, lo, t0))
            prev_last[i] = a[i][-1]
        hist.append(minute_ends(a)); hist = hist[-HIST_MAX:]; prev_day = D; prev_me = minute_ends(a)
        if D >= first:
            proof.append('DAY %s coins %d edge %s fires %d D1 same %d differ %d' % (D, len(coins), 'none' if E is None else 'yes', n_f,
                                                                              n_same, n_diff))
            print(proof[-1], flush=True)
    with open(os.path.join(out_dir, 'N1_EVENTS.tsv'), 'x') as f:
        f.write('coin\tt\tside\tS\tmode\n')
        for r in ev:
            f.write('%s\t%d\t%d\t%.4f\t%s\n' % r)
    with open(os.path.join(out_dir, 'N1_FIRES.tsv'), 'x') as f:
        f.write('coin\tt\tday\tk\tside\tx\tedge\tn_ratio\trange_bp\tref_bp\n')
        g = lambda v: '' if v != v else ('inf' if v == np.inf else '%.4f' % v)
        for c, t, D, k, side, x, edge, ratio, rng, ref in fr:
            f.write('%s\t%d\t%s\t%d\t%d\t%.1f\t%.2f\t%s\t%s\t%s\n' % (c, t, D, k, side, x, edge, g(ratio), g(rng), g(ref)))
    with open(os.path.join(out_dir, 'N1_PROOF.txt'), 'x') as f:
        f.write('\n'.join(proof) + '\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6:])
