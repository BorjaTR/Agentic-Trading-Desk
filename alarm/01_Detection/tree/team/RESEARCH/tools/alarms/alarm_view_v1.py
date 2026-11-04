"""QUANT alarm_view_v1 (kanban AV1, the owner 08:34-08:35 Berlin 21 Oct 2026): one layer over lab3 that every alarm reads through, so the
indexing mistakes that let the future in cannot be written, and the lookahead proof is made once, here, by planted-future unit tests.

THE TIMELINE. A run covers whole UTC days d = 0 .. nd - 1 (built or not); minute end t = d * 1440 + j is the instant day_d 00:00 + 60 j
(j = 0 .. 1439). Every array the layer returns has the shape (coins, nd * 1440) on that timeline, NaN where nothing is known. The value at t
is what was known at that instant and nothing later:
  - a lab code of clock c seconds (1 min, 30 s, 5 s) gives its column k = 60 j / c of day d (lab3's rule: column k is known at day 00:00 +
    c k); codes(...) does that mapping once;
  - prices(...) gives the close of the last lab bin with trades whose last trade time tl <= t, and its age t - tl (the bins of earlier days
    carry over midnight); bin_counts() the bins' trades with end time te in (t - 60, t]; bin_minutes(per_bin) any per-bin values summed
    over the same minute (buy and sell dollars, dollars over the close for a VWAP, bins with a side).
CAUSAL TOOLS (all on the timeline, all vectorised, none looks past t):
  lag(x, k)            the value at t - k (k >= 0 minutes)
  roll(x, n, how, ...) a statistic of the n values ending at t (inclusive) or of the n before t (prior=True): sum, mean, count, median,
                       std (ddof 0 or 1), any pct (numpy linear), max, min; a minimum count of finite values (else NaN); sums by cumsum,
                       median, pct, max, min by pandas' C rolling windows when present (else numpy windows: the same numbers, tested equal);
                       std always by numpy windows (pandas 2.3's online std drifts after a spike: SCOUT's review item 4, J33570)
  fresh_move(p, age, k, fresh)  ln p(t) - ln p(t - k) when both prices are at most `fresh` seconds old
  day_edge(x, built, q, hist, day_min, min_days, window)  per day d: the q-th pct (or 'max', 'min', 'median') of the finite x of the
                       days before d: window='built' (default) the last `hist` BUILT days before d, window='calendar' the built days among
                       the `hist` calendar days d - hist .. d - 1 (they differ only when a day is missing; the card names which); only days
                       with at least day_min values count, at least min_days of them; spread over d's minutes
  onset(hold, ok, refr, first_day)  the cards' rule: a fire at t when hold(t), ok(t - 1) and not hold(t - 1), more than refr minute ends
                       after the coin's last fire; ONE-DAY CHAIN (the cards' definition): for each day d, d - 1's fires are found fresh from
                       d - 1 00:00 (its j = 0 not an onset), then d's from them; fires of days before first_day are not returned. It can
                       differ from one chain over the whole run when candidates sit within refr of each other across a whole day.
  card_t(d, j, ends)   the timeline index of a card's minute j of day d: ends='j' for cards whose minute ends are D 00:00 + 60 j (index
                       d * 1440 + j), ends='j+1' for cards whose minute ends are D 00:00 + 60 (j + 1) (P3, A08, P5, C1, M4, M5: index + 1).
                       Every port names its card's convention through it, so no port is one minute off in silence.
NUMBERS. sum/mean over n <= 64 values are plain window sums (np.sum of the window, the rebuild's arithmetic); longer windows use cumsum
(within rtol 1e-9 of plain sums, tested; keep strict-edge plants away from long sums). Quantiles: pandas' C windows equal numpy's to 1e-12.
LOADERS. View(... R=, LB=) takes a lab3 Days and bins module (a fake in the tests); prices compare trade times in integer microseconds
(a trade at t + 1 us is not used at t); codes that fail to read are listed in View.skipped (day, code, reason), never silent.
Usage: from alarm_view_v1 import View; v = View(lab_days, lab3_code, first, last, coins, before=17); x = v.code('E2.S04'); p, age = v.prices()
"""
import datetime as dt
import numpy as np

M = 1440


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def day0(d):
    return int(dt.datetime.strptime(d, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())


# ---------------------------------------------------------------- pure causal tools (the lookahead proof is on these)
def to_minutes(v):
    """one day's code values (coins, ncol) of any clock -> (coins, 1440): the column known at each minute end D 00:00 + 60 j"""
    ncol = v.shape[1]
    if ncol % M:
        raise ValueError('a clock that does not divide the day into minutes: %d columns' % ncol)
    return v[:, ::ncol // M]


def lag(x, k):
    """value at t - k (k >= 0) along the last axis; NaN before the start"""
    if k < 0:
        raise ValueError('lag needs k >= 0: a negative lag looks ahead')
    out = np.full(x.shape, np.nan)
    if k == 0:
        out[...] = x
    elif k < x.shape[-1]:
        out[..., k:] = x[..., :-k]
    return out


def _windows(x, n, prior):
    """(N,) -> (N, n) view: row t = x[t - n + 1 .. t] (inclusive) or x[t - n .. t - 1] (prior), NaN padded at the start"""
    pad = np.concatenate([np.full(n, np.nan), np.asarray(x, float)])
    w = np.lib.stride_tricks.sliding_window_view(pad, n)          # row i = pad[i .. i + n - 1] = x[i - n .. i - 1]
    return w[:-1] if prior else w[1:]


def roll(x, n, how='mean', prior=False, min_count=1, q=None, ddof=0, chunk=4096, engine='pandas'):
    """a statistic over n values ending at t (or before t with prior=True) for every t; x (N,) or (coins, N)"""
    x = np.asarray(x, float)
    if x.ndim == 2:
        return np.vstack([roll(r, n, how, prior, min_count, q, ddof, chunk, engine) for r in x])
    N = len(x); fin = np.isfinite(x); xv = np.where(fin, x, 0.0)
    if how in ('sum', 'mean') and n <= 64:                     # plain window sums: the rebuild's arithmetic
        Wv = _windows(xv, n, prior); Wf = _windows(fin.astype(float), n, prior)
        s = np.nan_to_num(Wv).sum(1); cnt = np.nan_to_num(Wf).sum(1)
        out = s if how == 'sum' else np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)
        return np.where(cnt >= min_count, out, np.nan)
    if how in ('sum', 'mean', 'count'):
        c = np.concatenate([np.zeros(n + 1), np.cumsum(xv)]); k = np.concatenate([np.zeros(n + 1), np.cumsum(fin)])
        hi = np.arange(N) + (n + 1) - (1 if prior else 0); lo = hi - n        # sums over x[t - n + 1 .. t] or x[t - n .. t - 1]
        s = c[hi] - c[lo]; cnt = k[hi] - k[lo]
        if how == 'count':
            return cnt.astype(float)
        out = s if how == 'sum' else np.where(cnt > 0, s / np.maximum(cnt, 1), np.nan)
        return np.where(cnt >= min_count, out, np.nan)
    if how == 'std':
        engine = 'numpy'                                     # pandas 2.3's rolling std drifts after a spike (online sums): exact windows
    if engine == 'pandas':
        try:
            import pandas as pd
        except ImportError:
            engine = 'numpy'
    if engine == 'pandas':                                   # C rolling windows (skip list): the same numbers, about 500x faster
        s = pd.Series(x)
        if prior:
            s = s.shift(1)
        r = s.rolling(n, min_periods=max(min_count, 1))
        if how == 'median':
            v = r.median()
        elif how == 'pct':
            v = r.quantile(q / 100.0, interpolation='linear')
        elif how == 'std':
            v = r.std(ddof=ddof)
        elif how == 'max':
            v = r.max()
        elif how == 'min':
            v = r.min()
        else:
            raise ValueError(how)
        return v.to_numpy(dtype=float)
    W = _windows(x, n, prior); out = np.full(N, np.nan)
    import warnings
    for a in range(0, N, chunk):
        w = W[a:a + chunk]; cnt = np.isfinite(w).sum(1)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            if how == 'median':
                v = np.nanmedian(w, axis=1)
            elif how == 'pct':
                v = np.nanpercentile(w, q, axis=1)
            elif how == 'std':
                v = np.nanstd(w, axis=1, ddof=ddof)
            elif how == 'max':
                v = np.nanmax(w, axis=1)
            elif how == 'min':
                v = np.nanmin(w, axis=1)
            else:
                raise ValueError(how)
        out[a:a + chunk] = np.where(cnt >= min_count, v, np.nan)
    return out


def fresh_move(p, age, k, fresh=60.0):
    """ln p(t) - ln p(t - k) where both last trades are at most `fresh` s old (k in minutes)"""
    p0, a0 = lag(p, k), lag(age, k)
    ok = np.isfinite(p) & np.isfinite(p0) & (p > 0) & (p0 > 0) & (age <= fresh) & (a0 <= fresh)
    out = np.full(np.shape(p), np.nan)
    with np.errstate(invalid='ignore', divide='ignore'):
        out[ok] = np.log(p[ok] / p0[ok])
    return out


def day_edge(x, built, q, hist=14, day_min=1000, min_days=2, window='built'):
    """x (coins, nd * 1440); built (nd,) bool -> (coins, nd * 1440): day d's edge from the days before d (window 'built' or 'calendar')"""
    if window not in ('built', 'calendar'):
        raise ValueError('window is built or calendar')
    x = np.asarray(x, float); C = x.shape[0]; nd = x.shape[1] // M; out = np.full((C, nd), np.nan)
    days = np.flatnonzero(built); xd = x.reshape(C, nd, M)
    import warnings
    for c in range(C):
        fin = {e: xd[c, e][np.isfinite(xd[c, e])] for e in days}           # each day's finite values once per coin
        for d in range(nd):
            prev = days[days < d][-hist:] if window == 'built' else days[(days < d) & (days >= d - hist)]
            parts = [fin[e] for e in prev if len(fin[e]) >= day_min]
            if len(prev) < min_days or len(parts) < min_days:
                continue
            v = np.concatenate(parts)
            out[c, d] = v.max() if q == 'max' else (v.min() if q == 'min' else float(np.percentile(v, 50.0 if q == 'median' else q)))
    return np.repeat(out, M, axis=1)


def onset(hold, ok, refr, first_day=0):
    """hold, ok (coins, nd * 1440) -> list per coin of fire indices t (days >= first_day), the cards' one-day chain"""
    hold = np.asarray(hold, bool); ok = np.asarray(ok, bool)
    C, N = hold.shape; nd = N // M
    ph = np.concatenate([np.zeros((C, 1), bool), hold[:, :-1]], 1); po = np.concatenate([np.zeros((C, 1), bool), ok[:, :-1]], 1)
    cand = hold & po & ~ph
    out = []
    for c in range(C):
        idx = np.flatnonzero(cand[c]); fires = []
        for d in range(max(first_day, 0), nd):
            last = None
            for t in idx[(idx > (d - 1) * M) & (idx < d * M)] if d > 0 else []:      # d - 1 fresh, its j = 0 not an onset
                if last is None or t - last > refr:
                    last = t
            for t in idx[(idx >= d * M) & (idx < (d + 1) * M)]:
                if last is None or t - last > refr:
                    fires.append(int(t)); last = t
        out.append(fires)
    return out


def card_t(d, j, ends):
    """timeline index of a card's minute j of day index d: ends 'j' (m = D 00:00 + 60 j) or 'j+1' (m = D 00:00 + 60 (j + 1))"""
    if ends == 'j':
        return d * M + j
    if ends == 'j+1':
        return d * M + j + 1
    raise ValueError("ends is 'j' or 'j+1'")


def minute_sums(te, vals, t0):
    """bins' end times te (s) and per-bin values (k, nbins) of one day -> (k, 1441): column c sums the bins with te in
    (t0 + 60 (c - 1), t0 + 60 c] (c = 1440: the next day's first minute end)"""
    vals = np.atleast_2d(np.asarray(vals, float)); k = np.ceil((np.asarray(te, float) - t0) / 60.0).astype(int); ok = (k >= 0) & (k <= M)
    out = np.zeros((vals.shape[0], M + 1))
    for r in range(vals.shape[0]):
        np.add.at(out[r], k[ok], vals[r][ok])
    return out


def minute_counts(te, n, t0):
    """bins' end times te (s) and trade counts n of one day -> (1441,): k = 0 .. 1440 sums the bins with te in (t0 + 60 (k - 1), t0 + 60 k]
    (k = 0 holds the bins ending in the minute before t0 + 0, k = 1440 those that end at the next day's first minute end)"""
    k = np.ceil((np.asarray(te, float) - t0) / 60.0).astype(int); ok = (k >= 0) & (k <= M)
    out = np.zeros(M + 1); np.add.at(out, k[ok], np.asarray(n, float)[ok]); return out


# ---------------------------------------------------------------- the loader on lab3 (reads only; values as known at each minute end)
class View:
    def __init__(self, root, code_dir, first, last, coins, before=17, R=None, LB=None):
        if R is None:
            import sys
            sys.path.insert(0, code_dir)
            from lab3 import days as LD, bins as LB
            R = LD.Days(root, 'research')
        self.LB = LB; self.R = R; have = set(self.R.days()); self.skipped = []
        self.days = []; d = shift(first, -before)
        while d <= last:
            self.days.append(d); d = shift(d, 1)
        self.built = np.array([d in have for d in self.days]); self.coins = list(coins); self.first_day = self.days.index(first)
        self.t = np.concatenate([day0(d) + 60.0 * np.arange(M) for d in self.days])

    def code(self, name):
        """(coins, N) of a lab code on the timeline; NaN for a coin or day the code lacks"""
        C = len(self.coins); out = np.full((C, len(self.days) * M), np.nan)
        for e, d in enumerate(self.days):
            if not self.built[e]:
                continue
            try:
                zc = list(self.R.index(d, self.R.part_of(name, d))['coins'])
            except Exception as ex:                              # said, never silent: the day stays unvalued for this code
                self.skipped.append((d, name, '%s: %s' % (type(ex).__name__, str(ex)[:100]))); continue
            got = [c for c in self.coins if c in zc]
            if not got:
                self.skipped.append((d, name, 'none of the coins in its part')); continue
            v = to_minutes(np.asarray(self.R.read(name, 'v', [d], got)[0], float))
            for i, c in enumerate(self.coins):
                if c in got:
                    out[i, e * M:(e + 1) * M] = v[got.index(c)]
        return out

    def prices(self):
        """(p, age) (coins, N): the last bin close with tl <= t and t - tl; bins carry over midnight"""
        C = len(self.coins); N = len(self.days) * M; p = np.full((C, N), np.nan); age = np.full((C, N), np.inf)
        carry = [None] * C
        for e, d in enumerate(self.days):
            t = (day0(d) + 60 * np.arange(M, dtype=np.int64)) * 1000000                     # minute ends in integer microseconds
            if self.built[e]:
                off, b = self.LB.read_bins(self.R, d, self.coins)
                if len(off) != C + 1:
                    raise ValueError('read_bins %s: %d offsets for %d coins' % (d, len(off), C))
            for i in range(C):
                tl = np.zeros(0, np.int64); px = np.zeros(0)
                if self.built[e]:
                    s_, e_ = off[i], off[i + 1]; k = b['n'][s_:e_] > 0
                    tl = np.asarray(b['tl'][s_:e_][k], np.int64); px = np.asarray(b['px'][s_:e_][k], float); o = np.argsort(tl, kind='stable'); tl, px = tl[o], px[o]
                if carry[i] is not None:
                    tl = np.concatenate([[carry[i][0]], tl]).astype(np.int64); px = np.concatenate([[carry[i][1]], px])
                j = np.searchsorted(tl, t, side='right') - 1; ok = j >= 0
                p[i, e * M:(e + 1) * M][ok] = px[j[ok]]; age[i, e * M:(e + 1) * M][ok] = (t[ok] - tl[j[ok]]) / 1e6
                if len(tl):
                    carry[i] = (tl[-1], px[-1])
        return p, age

    def bin_counts(self):
        """(coins, N): trades (the bins' n, aggregated trades) in the minute (t - 60, t], by the bins' end time te"""
        C = len(self.coins); out = np.zeros((C, len(self.days) * M))
        for e, d in enumerate(self.days):
            if not self.built[e]:
                continue
            off, b = self.LB.read_bins(self.R, d, self.coins); t0 = day0(d)
            for i in range(C):
                s_, e_ = off[i], off[i + 1]; mc = minute_counts(b['te'][s_:e_] / 1e6, b['n'][s_:e_], t0)
                out[i, e * M:(e + 1) * M] += mc[:M]
                if (e + 1) * M < out.shape[1]:
                    out[i, (e + 1) * M] += mc[M]
        return out

    def bin_minutes(self, per_bin):
        """per_bin(b, s, e) -> dict name: per-bin values of one coin's bins b[f][s:e] of a day; -> dict name: (coins, N), the sums over
        the bins with end time te in (t - 60, t] (a day's last bins that end at the next day's 00:00 go to that day's j = 0)"""
        C = len(self.coins); N = len(self.days) * M; out = {}
        for e, d in enumerate(self.days):
            if not self.built[e]:
                continue
            off, b = self.LB.read_bins(self.R, d, self.coins); t0 = day0(d)
            if len(off) != C + 1:
                raise ValueError('read_bins %s: %d offsets for %d coins' % (d, len(off), C))
            for i in range(C):
                s_, e_ = off[i], off[i + 1]; vals = per_bin(b, s_, e_); names = list(vals)
                for nm in names:
                    out.setdefault(nm, np.zeros((C, N)))
                ms = minute_sums(np.asarray(b['te'][s_:e_]) / 1e6, np.array([vals[nm] for nm in names]).reshape(len(names), -1), t0)
                for r, nm in enumerate(names):
                    out[nm][i, e * M:(e + 1) * M] += ms[r, :M]
                    if (e + 1) * M < N:
                        out[nm][i, (e + 1) * M] += ms[r, M]
        return out

    def day_of(self, tidx):
        return self.days[tidx // M], tidx % M
