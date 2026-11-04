"""RESEARCH tools/alarm_context context_blocks (QUANT, 21 Oct 2026; DRAFT, reviewer SCOUT). THE QUESTIONS asked of every alarm, as BLOCKS:
a block is a function registered with @block(level, name) that reads a Ctx and returns {column: (n,) float array}, every value KNOWN AT
THE DECISION TIME of its row (lab values at the last minute end <= the decision; channels and bands from the minute before; alarm history
as of the alarm (t' < alarm) unless the column says "since the alarm"). SEALED days (Ctx sealed=) read as not known everywhere: their lab
minutes are NaN on every timeline the blocks see (SCOUT review 17:54Z MUST 1).
Its docstring lines 'column: meaning [unit]' are the catalog (CTX_CATALOG_V1.tsv is generated from them; a test keeps the two equal).
A line may name several columns 'name_1m / _5m': a name starting with '_' takes the first name's stem (up to its last '_').
Adding a question = adding one block here and regenerating the catalog (python3 alarm_context.py catalog).
Signs: + = in the alarm's push direction (side +1 = pushed UP, shorts forced; -1 = pushed DOWN, longs forced).
Levels: EVENT (moved from strategy_book/alarm_context_v1 31662904, J33691), MARKET, COIN.
Change from the prototype (determinism): the alarm-history questions (burst_rel_prior, fires_*) read Ctx.hist, the WHOLE alarm list, never
only the alarms of the dates being built, so an alarm's values do not depend on which dates a run covers."""
import datetime as dt
import numpy as np
BLOCKS = []


def block(level, name):
    def wrap(f):
        BLOCKS.append((level, name, f)); return f
    return wrap


MAX_PRICE_AGE_S = 60                                                  # STRATEGY-153335 (LAYERS; QUANT 16:00:47Z: 60 s, the draw V3 / proof_v3 / EWSD rule): older = NaN (STALE_PRICE)


class Ctx:
    """the rows to describe: ev = {coin, t (the DECISION time the row is known at), t_alarm (the alarm it describes), side, S}; src gives
    t (minute ends), code(name) -> (coins, N), prices() -> (p, age), market(name) / btc(name) -> (N,) (the lab's MARKET / BTC rows), and
    for the 30-day questions long_t, long(name) -> (coins, NL), long_btc(name) -> (NL,); hist = every alarm of the alarm list (coin, t, S),
    read only for alarms STRICTLY BEFORE the described alarm (t' < t_alarm); tables = {'costs': {(coin, hour): (cost_bp, tier)},
    'types': {coin: class}}. Every lab value is read at the last minute end <= the decision time."""
    def __init__(self, ev, src, coins, vt, hist=None, tables=None, sealed=None):
        ev = dict(ev); ev.setdefault('t_alarm', ev['t']); self.sealed = sealed
        self.ev = ev; self.src = src; self.coins = coins; self.vt = vt; self.n = len(ev['t'])
        self.hist = hist if hist is not None else {k: ev[k] if k != 't' else ev['t_alarm'] for k in ('coin', 't', 'S')}
        self.tables = tables or {}
        ci = {c: i for i, c in enumerate(coins)}; self.ci = np.array([ci[c] for c in ev['coin']], int)
        self.J = np.searchsorted(vt, ev['t'], 'right') - 1; self.sd = ev['side'].astype(float); self._c = {}; self._p = None; self._JL = None

    def _cut(self, A, t):
        """NaN on every minute end that falls on a sealed day (the day of a minute end t = its UTC day: lab3's rule, column k of day D
        is known at D 00:00 + 60 k)"""
        if self.sealed is None:
            return A
        A = np.array(A, float, copy=True); dn = np.floor(np.asarray(t, float) / 86400.0).astype(np.int64); bad = np.zeros(len(dn), bool)
        for u in np.unique(dn):
            if self.sealed(dt.datetime.fromtimestamp(int(u) * 86400, dt.timezone.utc).strftime('%Y%m%d')):
                bad[dn == u] = True
        if bad.any():
            A[..., bad] = np.nan
        return A

    def code(self, name):
        if name not in self._c:
            self._c[name] = self._cut(self.src.code(name), self.vt)
        return self._c[name]

    def at(self, name, lag=0):
        if not isinstance(lag, (int, np.integer)) or lag < 0:
            raise ValueError('lag must be a nonnegative integer; forward context reads are forbidden')
        A = self.code(name) if isinstance(name, str) else name; j = self.J - lag; ok = j >= 0; out = np.full(self.n, np.nan)
        out[ok] = A[self.ci[ok], j[ok]]; return out

    def _one(self, kind, name, lag=0):
        key = (kind, name)
        if key not in self._c:
            self._c[key] = self._cut(np.asarray(getattr(self.src, kind)(name), float), self.vt)
        x = self._c[key]; j = self.J - lag; ok = j >= 0; out = np.full(self.n, np.nan); out[ok] = x[j[ok]]; return out

    def mkt(self, name, lag=0):
        """the lab's MARKET row of a market-scope code"""
        return self._one('market', name, lag)

    def btc(self, name, lag=0):
        """the lab's BTC row of a BTC-scope code (C1.S15..S21, C4.S06..S10, C6.S01..S06) or of any coin code read for BTC"""
        return self._one('btc', name, lag)

    def _jl(self):
        if self._JL is None:
            self._JL = np.searchsorted(self.src.long_t, self.ev['t'], 'right') - 1
        return self._JL

    def lat(self, name, lags):
        """(n, len(lags)): a coin code on the 30-day timeline at the given minute lags"""
        key = ('long', name)
        if key not in self._c:
            self._c[key] = self._cut(np.asarray(self.src.long(name), float), self.src.long_t)
        A = self._c[key]; J = self._jl(); out = np.full((self.n, len(lags)), np.nan)
        for q, lag in enumerate(lags):
            j = J - lag; ok = j >= 0; out[ok, q] = A[self.ci[ok], j[ok]]
        return out

    def lbtc(self, name, lags):
        key = ('long_btc', name)
        if key not in self._c:
            self._c[key] = self._cut(np.asarray(self.src.long_btc(name), float), self.src.long_t)
        x = self._c[key]; J = self._jl(); out = np.full((self.n, len(lags)), np.nan)
        for q, lag in enumerate(lags):
            j = J - lag; ok = j >= 0; out[ok, q] = x[j[ok]]
        return out

    def push(self, x):
        """a signed value turned into the push direction (+ = the way the alarm pushed)"""
        return self.sd * np.asarray(x, float)

    def push_share(self, s):
        """a 0..1 share of 'up' turned into the share in the push direction"""
        s = np.asarray(s, float); return np.where(self.sd > 0, s, 1.0 - s)

    def sum_last(self, name, k):
        """sum of a per-minute code over the k minutes ending at the decision's minute; NaN unless all k minutes are known (the lab writes 0
        for a minute with nothing; NaN is a hole: NO_FILE, THIN_FEED, TRADES_HOLE, a sealed or unbuilt day: J36470)"""
        R = self.code(name) if isinstance(name, str) else name; A = np.nan_to_num(R); C = np.cumsum(A, axis=1)
        F = np.cumsum(np.isfinite(R), axis=1)
        hi = self.J; lo = self.J - k; out = np.full(self.n, np.nan); ok = (hi >= 0) & (lo >= -1)
        s = C[self.ci[ok], hi[ok]] - np.where(lo[ok] >= 0, C[self.ci[ok], np.maximum(lo[ok], 0)], 0.0)
        f = F[self.ci[ok], hi[ok]] - np.where(lo[ok] >= 0, F[self.ci[ok], np.maximum(lo[ok], 0)], 0)
        out[ok] = np.where(f == k, s, np.nan); return out

    def px(self, lag=0):
        """the close of the last PRICE bin at or before each minute end, NaN when that bin is older than MAX_PRICE_AGE_S (STALE_PRICE,
        STRATEGY-153335: a feed gap or a missing day never reads as a flat price); self.stale_px counts the stale cells"""
        if self._p is None:
            p, age = self.src.prices()[:2]; st = np.asarray(age, float) > MAX_PRICE_AGE_S
            self.stale_px = int((st & np.isfinite(np.asarray(p, float))).sum())
            self._p = self._cut(np.where(st, np.nan, p), self.vt)
        return self.at(self._p, lag)

    def pick(self, up_code, down_code, lag=0):
        """the value of up_code when the push was up (side +1), else down_code"""
        return np.where(self.sd > 0, self.at(up_code, lag), self.at(down_code, lag))


def lg(x):
    x = np.asarray(x, float); return np.where(x > 0, np.log10(np.where(x > 0, x, 1.0)), np.where(x == 0, 0.0, np.nan))


def _div(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); ok = np.isfinite(b) & (b != 0)
    return np.where(ok, a / np.where(ok, b, 1.0), np.nan)


@block('EVENT', 'identity')
def ev_identity(c):
    """hour_utc: hour of the alarm (UTC) [hour]
    weekday: 0 Monday .. 6 Sunday [day]
    forced_shorts: 1 = shorts were forced (price pushed up), 0 = longs forced (pushed down) [flag]"""
    d = [dt.datetime.fromtimestamp(float(t), dt.timezone.utc) for t in c.ev['t_alarm']]
    return dict(hour_utc=np.array([x.hour for x in d], float), weekday=np.array([x.weekday() for x in d], float), forced_shorts=(c.sd > 0).astype(float))


@block('EVENT', 'burst')
def ev_burst(c):
    """burst_log_usd: log10 of the alarm's size |S| from the EVENTS list (A02: its forced USD; another list: its own size, e.g. P3V2 |Lee-Mykland L|) [log10 of S's unit]
    burst_rel_prior: the burst over the median of this coin's EARLIER alarm bursts in the whole alarm list (NaN with fewer than 3 earlier) [ratio]
    forced_log_usd_1m / _5m / _15m / _60m: log10 USD liquidated on the FORCED side in the last 1 / 5 / 15 / 60 min (lab A1.S09 shorts, A1.S08 longs) [log10 usd, 0 = none]
    other_log_usd_15m: log10 USD liquidated on the OTHER side in the last 15 min [log10 usd, 0 = none]
    forced_share_15m: forced over forced + other liquidations, last 15 min [share]
    forced_over_taker_15m: forced USD over all aggressive USD in the push direction, last 15 min (B1 buys when up, sells when down): forced or real? [ratio]"""
    S = c.ev['S'].astype(float); prior = np.full(c.n, np.nan)
    hc = np.asarray(c.hist['coin']); ht = np.asarray(c.hist['t'], float); hS = np.asarray(c.hist['S'], float)
    for i in range(c.n):
        h = hS[(hc == c.ev['coin'][i]) & (ht < float(c.ev['t_alarm'][i])) & np.isfinite(hS)]
        if len(h) >= 3:
            prior[i] = _div(S[i], np.median(h))
    F = {k: np.where(c.sd > 0, c.sum_last('A1.S09', k), c.sum_last('A1.S08', k)) for k in (1, 5, 15, 60)}
    O15 = np.where(c.sd > 0, c.sum_last('A1.S08', 15), c.sum_last('A1.S09', 15))
    tk15 = np.where(c.sd > 0, c.sum_last('B1.S01', 15), c.sum_last('B1.S02', 15))
    out = dict(burst_log_usd=lg(S), burst_rel_prior=prior)
    out.update({'forced_log_usd_%dm' % k: lg(v) for k, v in F.items()})
    out.update(other_log_usd_15m=lg(O15), forced_share_15m=_div(F[15], F[15] + O15), forced_over_taker_15m=_div(F[15], tk15))
    return out


@block('EVENT', 'history')
def ev_history(c):
    """fires_coin_1h / _4h / _24h / _7d: this coin's alarms in the 1 h / 4 h / 24 h / 7 days before the alarm (whole alarm list, t' < alarm) [count]
    min_since_prev_fire: minutes from this coin's previous alarm to this alarm (NaN if none in the alarm list) [min]
    fires_other_5m / _60m: OTHER coins' alarms in the 5 / 60 min before the alarm (t' < alarm) [count]
    fires_coin_since / fires_other_since: this coin's / other coins' alarms AFTER the alarm and before the decision time (alarm < t' < decision; 0 at decision 0) [count]"""
    t = c.ev['t_alarm'].astype(float); coin = np.asarray(c.ev['coin'])
    ht = np.asarray(c.hist['t'], float); hc = np.asarray(c.hist['coin']); o = np.argsort(ht, kind='stable'); ts = ht[o]; cs = hc[o]
    out = {k: np.zeros(c.n) for k in ('fires_coin_1h', 'fires_coin_4h', 'fires_coin_24h', 'fires_coin_7d', 'fires_other_5m', 'fires_other_60m')}
    out['min_since_prev_fire'] = np.full(c.n, np.nan); out['fires_coin_since'] = np.zeros(c.n); out['fires_other_since'] = np.zeros(c.n)
    td = c.ev['t'].astype(float)
    for i in range(c.n):
        lo7 = np.searchsorted(ts, t[i] - 7 * 86400, 'left'); hi = np.searchsorted(ts, t[i], 'left')     # t' < t: strictly earlier
        w_t = ts[lo7:hi]; w_c = cs[lo7:hi]; same = w_c == coin[i]
        for key, s in (('1h', 3600), ('4h', 14400), ('24h', 86400), ('7d', 7 * 86400)):
            out['fires_coin_' + key][i] = np.sum(same & (w_t >= t[i] - s))
        for key, s in (('5m', 300), ('60m', 3600)):
            out['fires_other_' + key][i] = np.sum(~same & (w_t >= t[i] - s))
        prev = ts[:hi][cs[:hi] == coin[i]]
        if len(prev):
            out['min_since_prev_fire'][i] = (t[i] - prev[-1]) / 60.0
        a = np.searchsorted(ts, t[i], 'right'); b = np.searchsorted(ts, td[i], 'left'); mid = cs[a:b] == coin[i]
        out['fires_coin_since'][i] = np.sum(mid); out['fires_other_since'][i] = np.sum(~mid)
    return out


@block('EVENT', 'move')
def ev_move(c):
    """move_5m / _15m / _60m / _240m: price change in the push direction over the last 5 / 15 / 60 / 240 min, arithmetic: m = the decision minute (60 x floor(decision s / 60)), p(s) = close of the last PRICE bin ending at or before s, move_wm = 100 x side x (p(m) / p(m - 60w) - 1); NaN if either close is missing (P09-03) [pct]
    sudden_share: move_5m over move_60m (near 1 = it all happened in the last minutes; small = a slow grind before) [ratio]"""
    p0 = c.px(); out = {}
    for k in (5, 15, 60, 240):
        pk = c.px(k); out['move_%dm' % k] = np.where((pk > 0) & (p0 > 0), c.sd * 100.0 * (p0 / np.where(pk > 0, pk, 1) - 1.0), np.nan)
    m60 = out['move_60m']; out['sudden_share'] = np.where(np.abs(m60) > 1e-9, out['move_5m'] / np.where(np.abs(m60) > 1e-9, m60, 1), np.nan)
    return out


@block('EVENT', 'structure')
def ev_structure(c):
    """beyond_dc240 / beyond_dc1440: distance past the channel of the last 240 / 1440 observed candles, from the minute before; empty minutes are skipped, so this is not a fixed elapsed 4 h / 24 h window; > 0 = beyond the push-side edge: up push 100 x (p(m) / upper(m - 60) - 1), down push 100 x (lower(m - 60) / p(m) - 1) (reciprocal: edge 100, price 80 gives 25); m and p as in move; the channel counts candles, not elapsed hours after gaps (P09-03) [pct]
    vwap_dist: price vs NAUTILUS.S09 candle-based VWAP, + = stretched in the push direction; not trade VWAP, and around 00:00-00:10 the previous 23:59 bar can remain: not a guaranteed new-session VWAP: 100 x side x (p(m) / VWAP(m) - 1) (P09-03) [pct]
    boll1440_pos / boll240_pos: position in the typical-price Bollinger band of 1440 / 240 observed candles (minute before); gaps extend elapsed time; not BBANDS(close); + = towards push, +1 = at the band [band halves]
    to_day_extreme: distance to today's high (push up) or low (push down), 0 = at it (lab C11.S01 / S02) [pct]
    min_since_swing: legacy key for valid CANDLE COUNT since the last 5-candle swing high (push up) or low (push down); not elapsed minutes after gaps (NAUTILUS.S62 / S63) [candles]"""
    p = c.px(); out = {}
    for w, up, dn in (('240', 'NAUTILUS.S79', 'NAUTILUS.S81'), ('1440', 'NAUTILUS.S82', 'NAUTILUS.S84')):
        u, l = c.at(up, 1), c.at(dn, 1); u = np.where(u > 0, u, np.nan); l = np.where(l > 0, l, np.nan)    # a channel edge <= 0 is no edge
        out['beyond_dc' + w] = np.where(c.sd > 0, 100.0 * (_div(p, u) - 1.0), 100.0 * (_div(l, p) - 1.0))
    vw = c.at('NAUTILUS.S09'); vw = np.where(vw > 0, vw, np.nan); out['vwap_dist'] = c.sd * 100.0 * (_div(p, vw) - 1.0)
    for w, up, mid in (('1440', 'NAUTILUS.S73', 'NAUTILUS.S74'), ('240', 'NAUTILUS.S70', 'NAUTILUS.S71')):
        u, m = c.at(up, 1), c.at(mid, 1); half = u - m
        out['boll%s_pos' % w] = np.where(half > 0, c.sd * (p - m) / np.where(half > 0, half, 1), np.nan)
    out['to_day_extreme'] = c.pick('C11.S01', 'C11.S02')
    out['min_since_swing'] = c.pick('NAUTILUS.S62', 'NAUTILUS.S63')
    return out


@block('EVENT', 'walls')
def ev_walls(c):
    """wall_ahead_log_1pct / _2pct / _3pct: log10 USD of liquidation levels within 1 / 2 / 3 pct further in the push direction (A6 DISABLED: its card forbids analysis; always NaN pending review) [log10 usd, 0 = none]
    wall_behind_log_1pct / _2pct / _3pct: DISABLED A6 estimates on the other side; always NaN pending review [log10 usd, 0 = none]"""
    # A6 is explicitly barred from ANY ANALYSIS until its model/card is reviewed.
    # Retain legacy columns as missing so old readers cannot mistake these for 0.
    return {'wall_' + side + '_log_' + width: np.full(c.n, np.nan)
            for side in ('ahead', 'behind') for width in ('1pct', '2pct', '3pct')}


H = 60                                                               # minutes in an hour, for lags
DAY = 1440


def _compound(r):
    """(n, k) pct moves -> the pct move of all of them in a row (NaN if any is missing)"""
    r = np.asarray(r, float); ok = np.isfinite(r).all(1); out = np.full(r.shape[0], np.nan)
    out[ok] = 100.0 * (np.prod(1.0 + r[ok] / 100.0, axis=1) - 1.0); return out


def _straight(r):
    """(n, k) pct moves -> |their sum| over the sum of |each|: 1 = a straight walk, near 0 = back and forth (NaN if any missing)"""
    r = np.asarray(r, float); ok = np.isfinite(r).all(1); den = np.abs(r).sum(1); out = np.full(r.shape[0], np.nan)
    good = ok & (den > 0); out[good] = np.abs(r[good].sum(1)) / den[good]; return out


def _vol_regime(get, min_days=10):
    """the std of the 24 hourly moves ending now over the median of the same std at the same minute on each of the 30 days before;
    get(lags) -> (n, len(lags)) hourly pct moves; NaN with fewer than min_days earlier days"""
    x0 = get([H * k for k in range(24)]); ok0 = np.isfinite(x0).all(1); now = np.full(x0.shape[0], np.nan)
    now[ok0] = np.std(x0[ok0], axis=1)
    past = np.full((len(now), 30), np.nan)
    for d in range(1, 31):
        x = get([DAY * d + H * k for k in range(24)]); ok = np.isfinite(x).all(1)
        past[ok, d - 1] = np.std(x[ok], axis=1)
    cnt = np.isfinite(past).sum(1); med = np.full(len(now), np.nan)
    if (cnt >= min_days).any():
        med[cnt >= min_days] = np.nanmedian(past[cnt >= min_days], axis=1)
    return _div(now, med)


# ---------------------------------------------------------------- MARKET: what the whole market was doing at the decision time
@block('MARKET', 'btc')
def mk_btc(c):
    """btc_move_15m / _1h / _3h / _6h: BTC's move over the last 15 min / 1 h / 3 h / 6 h, + = in the alarm's push direction (lab C1.S16, S18, S19, S20) [pct]
    btc_pos_6h: where BTC sits in its 6 h range, 1 = at the push-side edge, 0 = at the other edge (lab C6.S05) [share]
    btc_straight_3h: how straight BTC walked over 3 h, + = towards the push side, -1..1 (lab C4.S09) [share]"""
    out = {'btc_move_%s' % k: c.push(c.btc(code)) for k, code in (('15m', 'C1.S16'), ('1h', 'C1.S18'), ('3h', 'C1.S19'), ('6h', 'C1.S20'))}
    out['btc_pos_6h'] = c.push_share(c.btc('C6.S05')); out['btc_straight_3h'] = c.push(c.btc('C4.S09'))
    return out


@block('MARKET', 'btc_trend')
def mk_btc_trend(c):
    """btc_move_24h / _7d: BTC's move over the last 24 h / 7 days, + = in the push direction (lab C1.S14 for BTC; 7 d = seven 24 h moves in a row) [pct]
    btc_straight_24h: how straight BTC walked over 24 h, from its 24 hourly moves: 1 = trending, near 0 = ranging (lab C1.S18) [share]
    btc_vol_regime: BTC's last-24 h volatility (std of its hourly moves) over its median at the same minute of the 30 days before (lab C1.S18; NaN with < 10 earlier days) [ratio]"""
    d7 = c.lbtc('C1.S14', [DAY * k for k in range(7)])
    hourly = lambda lags: c.lbtc('C1.S18', lags)
    return dict(btc_move_24h=c.push(d7[:, 0]), btc_move_7d=c.push(_compound(d7)), btc_straight_24h=_straight(hourly([H * k for k in range(24)])),
                btc_vol_regime=_vol_regime(hourly))


@block('MARKET', 'basket')
def mk_basket(c):
    """basket_move_15m / _1h: the typical (median) coin's move over 15 min / 1 h, + = in the push direction (lab C2.S02, S03) [pct]
    alts_vs_btc_1h: how far the typical alt beat BTC over the hour, + = alts ahead in the push direction (lab C2.S08) [pct]"""
    return dict(basket_move_15m=c.push(c.mkt('C2.S02')), basket_move_1h=c.push(c.mkt('C2.S03')), alts_vs_btc_1h=c.push(c.mkt('C2.S08')))


@block('MARKET', 'breadth')
def mk_breadth(c):
    """alts_with_push_15m: share of alts up over 15 min for an upward push; NaN for a downward push until a down-share source exists (C5.S04 excludes flat coins from up, so 1 - S04 is not down) [share]
    one_sided_5m: max(up coins, down coins) / all valued coins over 5 min, flat coins included; 1 = all one way, 0 = all flat; 0.5 does not uniquely mean split (C5.S01) [share]
    coins_strong_with_push_1h / coins_strong_against_push_1h: share of coins that moved 0.6 pct or more with / against the push over 1 h (lab C5.S05, S06) [share]"""
    up, dn = c.mkt('C5.S05'), c.mkt('C5.S06')
    return dict(alts_with_push_15m=np.where(c.sd > 0, c.mkt('C5.S04'), np.nan), one_sided_5m=c.mkt('C5.S01'),
                coins_strong_with_push_1h=np.where(c.sd > 0, up, dn), coins_strong_against_push_1h=np.where(c.sd > 0, dn, up))


@block('MARKET', 'liq_wave')
def mk_liq(c):
    """mkt_wave_age_min: minutes since the market's running liquidation wave of the FORCED side began (lab A4.S05 shorts, A4.S04 longs; NaN = no wave) [min]
    mkt_forced_share_1m: share of the market's liquidations in the last minute that hit the forced side (lab A5.S09) [share]
    mkt_forced_per_taker_1m: the market's forced dollars per dollar of taker flow in the push direction, last minute (lab A5.S04 up, A5.S03 down) [ratio]"""
    return dict(mkt_wave_age_min=np.where(c.sd > 0, c.mkt('A4.S05'), c.mkt('A4.S04')), mkt_forced_share_1m=c.push_share(c.mkt('A5.S09')),
                mkt_forced_per_taker_1m=np.where(c.sd > 0, c.mkt('A5.S04'), c.mkt('A5.S03')))


@block('MARKET', 'liquidity')
def mk_liquidity(c):
    """mkt_spread_vs_24h: standardized deviation of the median quoted spread from its last 24 h; read with mkt_spread_bp; not a widening or rare-stress claim, since ticks, prices and roster can move it (D2.S05) [robust units]
    mkt_spread_bp: the current median roster coin's full best-ask minus best-bid spread in basis points of mid; required beside mkt_spread_vs_24h, not market liquidity by itself (D2.S04) [bp]
    mkt_depth_vs_24h: the median coin's top-of-book dollars against its last 24 h, robust units, + = thinner than normal (lab D3.S17) [robust units]"""
    spread = c.mkt('D2.S04')
    deviation = c.mkt('D2.S05')
    return dict(mkt_spread_bp=spread, mkt_spread_vs_24h=np.where(np.isfinite(spread), deviation, np.nan),
                mkt_depth_vs_24h=c.mkt('D3.S17'))


@block('MARKET', 'time')
def mk_time(c):
    """weekend: 1 = the decision time falls on a Saturday or Sunday (UTC) [flag]
    decision_hour_utc: hour of the decision time (UTC) [hour]"""
    d = [dt.datetime.fromtimestamp(float(t), dt.timezone.utc) for t in c.ev['t']]
    return dict(weekend=np.array([x.weekday() >= 5 for x in d], float), decision_hour_utc=np.array([x.hour for x in d], float))


# ---------------------------------------------------------------- COIN: the alarm's own coin at the decision time
@block('COIN', 'move')
def cn_move(c):
    """coin_move_15m / _1h: the coin's mid move over 15 min / 1 h, + = in the push direction (lab C1.S12, S13) [pct]
    coin_vs_basket_15m / _1h: how far the coin beat the typical coin, + = ahead in the push direction (lab C2.S04, S05) [pct]
    coin_with_market_15m: how much of the rest of the market moved the coin's way over 15 min (lab C2.S06) [share]"""
    return dict(coin_move_15m=c.push(c.at('C1.S12')), coin_move_1h=c.push(c.at('C1.S13')), coin_vs_basket_15m=c.push(c.at('C2.S04')),
                coin_vs_basket_1h=c.push(c.at('C2.S05')), coin_with_market_15m=c.at('C2.S06'))


@block('COIN', 'range')
def cn_range(c):
    """range_pos_1h / _4h: position among observed trade candles in the trailing 60 / 240 min; 1 = push-side edge; SHORT_WINDOW can mean incomplete history, not certification of the full-window extreme (C9.S03, S17) [share]
    range_width_1h / _4h: width among observed trade candles in the trailing 60 / 240 min; SHORT_WINDOW can mean incomplete history, not the complete window's range (C9.S01, S15) [pct]
    broke_yday_range: +1 = today broke yesterday's range on the push side, -1 = on the other side (lab C11.S08) [side]"""
    return dict(range_pos_1h=c.push_share(c.at('C9.S03')), range_pos_4h=c.push_share(c.at('C9.S17')), range_width_1h=c.at('C9.S01'),
                range_width_4h=c.at('C9.S15'), broke_yday_range=c.push(c.at('C11.S08')))


@block('COIN', 'leg')
def cn_leg(c):
    """leg_vs_usual_025 / _05 / _1: the running leg against the coin's typical leg today, at swing size 0.25 / 0.5 / 1 dials (lab C10.S10, S24, S38) [ratio]
    leg_giveback_05: how much of the running 0.5-dial leg is undone, 0 = at its extreme, 1 = all given back (lab C10.S18) [share]"""
    return dict(leg_vs_usual_025=c.at('C10.S10'), leg_vs_usual_05=c.at('C10.S24'), leg_vs_usual_1=c.at('C10.S38'), leg_giveback_05=c.at('C10.S18'))


@block('COIN', 'vol')
def cn_vol(c):
    """coin_vol_5m / _1h: how much the coin's mid moved over the last 5 min / 1 h (lab C4.S01, S02) [pct]
    pace_5m_vs_1h: the last 5 min's pace over the last hour's from 1-minute mid returns, 1 = the same (lab C4.S04.step60_off, the owner's per-minute C4; LAB1 16:38:28Z: the 1 s C4.S04 ranks coin-minutes far from the kline pace) [ratio]
    pace_1h_vs_24h: the last hour's pace over the last 24 h's (lab C4.S05) [ratio]"""
    return dict(coin_vol_5m=c.at('C4.S01'), coin_vol_1h=c.at('C4.S02'), pace_5m_vs_1h=c.at('C4.S04.step60_off'), pace_1h_vs_24h=c.at('C4.S05'))


@block('COIN', 'derivs')
def cn_derivs(c):
    """funding_forced_pays_bp: live funding estimate in bp per 8 h (normalized: E1.S01 is already scaled to 8 h, so a 4 h coin's raw 0.0001 reads 2 bp), + = forced side would pay IF this estimate held; not an actual settled payment (E1.S01; OX-DATA V06-01) [bp per 8h]
    oi_chg_10m: the coin's Binance open interest change over 10 min, + = positions opened (lab E2.S04) [pct]
    oi_chg_1h / _24h: the open interest change over 1 h / 24 h (lab E2.S02) [pct]
    basis_push_bp: Binance mark-price premium over its spot index, + = in the push direction; partly smoothed and funding-anchored, not the tradable mid premium (legacy basis key; E3.S01) [bp]"""
    oi = c.at('E2.S02')
    return dict(funding_forced_pays_bp=-c.push(c.at('E1.S01')) * 1e4, oi_chg_10m=c.at('E2.S04'),
                oi_chg_1h=100.0 * (_div(oi, c.at('E2.S02', H)) - 1.0), oi_chg_24h=100.0 * (_div(oi, c.at('E2.S02', DAY)) - 1.0),
                basis_push_bp=c.push(c.at('E3.S01')))


@block('COIN', 'cost')
def cn_cost(c):
    """cost_bp: the round-trip cost of the coin at the decision hour, a DECISION feature: only from a cost table row whose source vintage (int64 us) is at or before the decision, else NOT_KNOWN (COSTS_PER_COIN_V4 has no vintage, so NOT_KNOWN today; OUTSIDE A09-02) [bp]
    cost_tier: 1 cheap, 2 middle, 3 thin, under the same vintage rule (COSTS_PER_COIN_V4 group) [tier]
    cost_bp_retro: RETROSPECTIVE, never a decision feature: today's COSTS_PER_COIN_V4 applied to the past (cost sensitivity only; its source time is the table's, after the decision) [bp]
    cost_tier_retro: RETROSPECTIVE tier from the same table, never a decision feature [tier]"""
    tab = c.tables.get('costs', {}); h = [dt.datetime.fromtimestamp(float(t), dt.timezone.utc).hour for t in c.ev['t']]
    vintage = c.tables.get('costs_known_at_us', {}); got, retro = [], []
    for coin, hh, decision in zip(c.ev['coin'], h, c.ev['t']):
        key = (coin, hh) if (coin, hh) in tab else (coin, 'ALL')
        known = vintage.get(key)
        usable = isinstance(known, (int, np.integer)) and 0 <= known <= decision * 1_000_000
        retro.append(tab.get(key, (np.nan, np.nan))); got.append(retro[-1] if usable else (np.nan, np.nan))
    return dict(cost_bp=np.array([g[0] for g in got], float), cost_tier=np.array([g[1] for g in got], float),
                cost_bp_retro=np.array([g[0] for g in retro], float), cost_tier_retro=np.array([g[1] for g in retro], float))


@block('COIN', 'trend')
def cn_trend(c):
    """coin_move_24h / _7d: the coin's move over the last 24 h / 7 days, + = in the push direction (lab C1.S14; 7 d = seven 24 h moves in a row) [pct]
    coin_straight_24h: how straight the coin walked over 24 h, from its 24 hourly moves: 1 = trending, near 0 = ranging (lab C1.S13) [share]
    coin_vol_regime: the coin's last-24 h volatility (std of its hourly moves) over its median at the same minute of the 30 days before (lab C1.S13; NaN with < 10 earlier days) [ratio]"""
    d7 = c.lat('C1.S14', [DAY * k for k in range(7)])
    hourly = lambda lags: c.lat('C1.S13', lags)
    return dict(coin_move_24h=c.push(d7[:, 0]), coin_move_7d=c.push(_compound(d7)), coin_straight_24h=_straight(hourly([H * k for k in range(24)])),
                coin_vol_regime=_vol_regime(hourly))


@block('COIN', 'flush_history')
def cn_flush(c):
    """days_since_bigger_alarm: days from this coin's last alarm with a burst at least as big as this one to this alarm (whole alarm list, t' < alarm; NaN = none, or the list carries no size: A02N lists are UNAVAILABLE here, never filled from another size, P09-02) [days]
    alarms_all_24h: alarms of every coin in the 24 h before this alarm (t' < alarm) [count]"""
    hc = np.asarray(c.hist['coin']); ht = np.asarray(c.hist['t'], float); hS = np.asarray(c.hist['S'], float)
    out = np.full(c.n, np.nan); n24 = np.zeros(c.n)
    for i in range(c.n):
        ta = float(c.ev['t_alarm'][i]); before = ht < ta
        big = before & (hc == c.ev['coin'][i]) & (hS >= float(c.ev['S'][i]))
        if big.any():
            out[i] = (ta - ht[big].max()) / 86400.0
        n24[i] = np.sum(before & (ht >= ta - 86400))
    return dict(days_since_bigger_alarm=out, alarms_all_24h=n24)


@block('COIN', 'type')
def cn_type(c):
    """coin_class: 1 major (BTC, ETH), 2 alt, 3 meme (COIN_TYPES_V1.tsv in this folder, a hand list) [class]"""
    tab = c.tables.get('types', {}); m = {'major': 1.0, 'alt': 2.0, 'meme': 3.0}
    return dict(coin_class=np.array([m.get(tab.get(x, ''), np.nan) for x in c.ev['coin']], float))


# ---------------------------------------------------------------- v2 (the owner 21:30 Berlin; meaning sheet PROPOSED_BLOCKS_V2.md, METRICS_V1)
def _forced(c, up_code, down_code, kind='at'):
    """the forced side's value: the shorts' code when the alarm pushed up (side +1), the longs' when it pushed down"""
    f = c.at if kind == 'at' else c.mkt
    return np.where(c.sd > 0, f(up_code), f(down_code))


@block('EVENT', 'forcing_now')
def ev_forcing_now(c):
    """liq_oi_forced_bp_60s: forced-side liquidation dollars of the last 60 s over open interest x mark (lab X1.LIQX.S04 shorts, S03 longs) [bps]
    liq_seconds_share_60s: share of the last 60 s holding a liquidation print of the coin, either side (lab X1.LIQX.S01) [share]
    oi_moved_since_wave: how much of the coin's open interest left (-) or came in since the market's forced-side wave began (lab A7.S03 squeeze, A7.S01 long wave) [ratio]
    coins_liquidating_1m: seen roster coins with >=0.50 USD observed forced-side liquidations summed over 60 s; excludes positive dust below the threshold (A2.S06 shorts, A2.S05 longs) [count]
    coins_liquidating_z: how many more coins liquidating the forced side in the last 30 s than over 6 h (lab A2.S04 shorts, A2.S03 longs) [std units]"""
    return dict(liq_oi_forced_bp_60s=_forced(c, 'X1.LIQX.S04', 'X1.LIQX.S03'), liq_seconds_share_60s=c.at('X1.LIQX.S01'),
                oi_moved_since_wave=_forced(c, 'A7.S03', 'A7.S01'), coins_liquidating_1m=_forced(c, 'A2.S06', 'A2.S05', 'mkt'),
                coins_liquidating_z=_forced(c, 'A2.S04', 'A2.S03', 'mkt'))


@block('EVENT', 'who_trades')
def ev_who_trades(c):
    """fills_one_sided: how one-sided the coin's last 1,000 fills were, 0 balanced, 1 all one side (lab B2.S02) [share]
    volume_one_sided: one-sided share of the last 50 volume buckets on true taker sides (lab X1.FLOWX.S12) [share]
    whale_net_5m_usd: net taker dollars of the big trades in the last 5 min, + = with the push (lab X1.FLOWX.S01) [usd]"""
    return dict(fills_one_sided=c.at('B2.S02'), volume_one_sided=c.at('X1.FLOWX.S12'), whale_net_5m_usd=c.push(c.at('X1.FLOWX.S01')))


@block('EVENT', 'book_now')
def ev_book_now(c):
    """book_flow_top_60s: which side the top-of-book changes helped over 60 s, + = the push side (lab D1.S04) [share -1..1]
    book_flow_10lv_60s: the same for the first 10 levels (lab D4.S04) [share -1..1]
    book_imbalance_30bp: imbalance of the observed 25 levels lying within 30 bps, + = towards the push side; not the full 30 bp book (D3.S05) [ratio]
    depth_vs_median_coin: how many times the median coin's top-of-book dollars this coin has (lab D3.S15) [ratio]
    spread_vs_usual: the half spread now over its median at this UTC hour over the 14 days before (lab X1.COST.S01 / S02) [ratio]
    impact_10k_vs_usual: the cost of a 10,000 USDT market order (buy and sell averaged) over the average of the two side medians at this hour; medians exclude exhausted books, so read both exhausted shares beside this ratio; NaN if either share is unknown (X1.COST.S04, S05 / S06, S08; S10, S11) [ratio]
    impact_10k_buy_exhausted_share: fraction of eligible historical ask snapshots unable to fill 10,000 USDT; read beside impact_10k_vs_usual (X1.COST.S10) [share]
    impact_10k_sell_exhausted_share: same for bid snapshots (X1.COST.S11) [share]
    min_to_funding: minutes to the coin's next Binance funding payment (lab Z3.S01) [min]"""
    ex_buy, ex_sell = c.at('X1.COST.S10'), c.at('X1.COST.S11')
    exhaustion_known = np.isfinite(ex_buy) & np.isfinite(ex_sell)
    imp = 0.5 * (c.at('X1.COST.S04') + c.at('X1.COST.S05')); imp0 = 0.5 * (c.at('X1.COST.S06') + c.at('X1.COST.S08'))
    return dict(book_flow_top_60s=c.push(c.at('D1.S04')), book_flow_10lv_60s=c.push(c.at('D4.S04')), book_imbalance_30bp=c.push(c.at('D3.S05')),
                depth_vs_median_coin=c.at('D3.S15'), spread_vs_usual=_div(c.at('X1.COST.S01'), c.at('X1.COST.S02')),
                impact_10k_vs_usual=np.where(exhaustion_known, _div(imp, imp0), np.nan),
                impact_10k_buy_exhausted_share=ex_buy, impact_10k_sell_exhausted_share=ex_sell, min_to_funding=c.at('Z3.S01'))


@block('MARKET', 'heat_news')
def mk_heat_news(c):
    """typical_range_15m: how far the typical coin moved over 15 min (lab C7.S04) [pct]
    market_hot_rank_30d: the rank of the typical coin's 2 h range among its values of the last 30 days, 1 = hottest (lab X1.VOLX.S18) [share]
    btc_implied_minus_real: BTC DVOL minus BTC's 30-day realised volatility (lab X1.VOLX.S09) [pct]
    market_funding_dev: the market's funding deviation vs its last 3 weeks in max(1.4826 MAD, 1.2533 MeanAD) units, signed as -push; no positioning or payer claim (the E1.S07 card forbids that reading) (lab E1.S07) [spread units]
    market_whales_with_push: (coins with whale net buying - coins with net selling) over the coins, + = with the push (lab X1.FLOWX.S04) [share -1..1]
    crypto_news_rows: GDELT records tagged bitcoin in the last readable batch (lab Z2.S02) [count]"""
    return dict(typical_range_15m=c.mkt('C7.S04'), market_hot_rank_30d=c.mkt('X1.VOLX.S18'),
                btc_implied_minus_real=c.btc('X1.VOLX.S09'), market_funding_dev=-c.push(c.mkt('E1.S07')),
                market_whales_with_push=c.push(c.mkt('X1.FLOWX.S04')), crypto_news_rows=c.mkt('Z2.S02'))


@block('COIN', 'behaviour')
def cn_behaviour(c):
    """btc_beta_3d: Dimson beta of the coin's 60 s returns on BTC's over the last 3 days (lab X1.RETX.S01) [ratio]
    idio_move_60m: the coin's 60 min return less beta x BTC's, + = in the push direction (lab X1.RETX.S04) [pct]
    quote_rate: bookTicker top updates a second over the last 30 s (lab C12.S02) [per s]
    range_rank_1h_30d: the rank of the coin's 60 min range among its last 30 days, 1 = widest (lab X1.VOLX.S19) [share]
    jump_flag: a Lee-Mykland jump in the last minute: +1 in the push direction, -1 against, 0 none (lab X1.VOLX.S17) [flag]"""
    return dict(btc_beta_3d=c.at('X1.RETX.S01'), idio_move_60m=c.push(c.at('X1.RETX.S04')), quote_rate=c.at('C12.S02'),
                range_rank_1h_30d=c.at('X1.VOLX.S19'), jump_flag=c.push(c.at('X1.VOLX.S17')))


@block('COIN', 'positioning')
def cn_positioning(c):
    """funding_z_30d: -push times robust z of estimated hourly funding against pooled 720 clock hours of D-30..D-1, spread 1.4826 MAD; not actual payments or crowding (X1.POSX.S03) [robust units]
    oi_vs_30d: Binance OI contract coins x trade close over the pooled 720 clock-hour samples of D-30..D-1 (at least 684 valued); fixed daily baseline, not same-hour; price alone can raise it (X1.POSX.S12) [ratio]
    top_traders_ls_chg_1h: 1 h change of Binance's top-trader long/short position ratio from rows known 10 minutes after create_time; + = ratio change aligned with the push, not price direction; source column meaning remains untested (X1.POSX.S13) [ratio]
    taker_buy_sell_5m: log of Binance taker buy/sell volume in the latest available 5-minute metrics row, known 10 minutes after create_time and used up to 900 s after that; its period is older than the decision, not the latest 5 minutes ending now; + = with push (X1.POSX.S14; OX-CODE1 V04, A09-S03) [log ratio]"""
    tb = c.at('X1.POSX.S14')
    return dict(funding_z_30d=-c.push(c.at('X1.POSX.S03')), oi_vs_30d=c.at('X1.POSX.S12'), top_traders_ls_chg_1h=c.push(c.at('X1.POSX.S13')),
                taker_buy_sell_5m=c.push(np.where(tb > 0, np.log(np.where(tb > 0, tb, 1.0)), np.nan)))


def doc_columns(levels=None):
    """[(level, block, column, meaning, unit)] in block order, from the docstrings (the catalog's source)"""
    out = []
    for lv, name, f in BLOCKS:
        if levels is not None and lv not in levels:
            continue
        for l in (f.__doc__ or '').splitlines():
            l = l.strip()
            if ':' not in l:
                continue
            cols, mean = l.split(':', 1); mean = mean.strip(); unit = ''
            if mean.endswith(']') and '[' in mean:
                unit = mean[mean.rindex('[') + 1:-1].strip(); mean = mean[:mean.rindex('[')].strip()
            names = [x.strip() for x in cols.split('/')]; stem = names[0][:names[0].rindex('_')] if '_' in names[0] else names[0]
            for nm in names:
                out.append((lv, name, stem + nm if nm.startswith('_') else nm, mean, unit))
    return out


def run(ctx, levels=('EVENT',)):
    """{column: (n,) float} of every block of the levels, in block order; a column the docstrings do not name is refused"""
    named = [x[2] for x in doc_columns(levels)]; cols = {}
    for lv, name, f in BLOCKS:
        if lv not in levels:
            continue
        with np.errstate(divide='ignore', invalid='ignore'):
            got = f(ctx)
        for k, v in got.items():
            if k not in named:
                raise ValueError('block %s returns %s, not in its docstring: add the catalog line' % (name, k))
            v = np.asarray(v, float)
            if v.shape != (ctx.n,):
                raise ValueError('block %s column %s: shape %s, want (%d,)' % (name, k, v.shape, ctx.n))
            cols[k] = v
    return {k: cols[k] for k in named if k in cols}
