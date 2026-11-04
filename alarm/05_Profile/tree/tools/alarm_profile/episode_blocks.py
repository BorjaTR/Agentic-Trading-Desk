"""RESEARCH tools/alarm_profile episode_blocks (QUANT, 22 Oct 2026; reviewer SCOUT; built to the research-tool-design skill).
THE EPISODE QUESTIONS asked of every liquidation alarm: what this liquidation looked like UP TO THE ALARM, measured so that one alarm
can be compared with another (the owner 12:52 and 13:03 Berlin: "how much the price has moved before the alarm from where the move of
the coin really started"; "how fast the price moved since the liquidations started to the alarm? how big the liquidations are, how big
they are to the normal liquidations for that coin?"). The owner 13:13 Berlin: "whatever metric we use we prove it means what it says":
every column below has a proof card in PROOFS_V1.tsv, and the profile view shows its status.

A block is a function registered with @block(level, name) that reads an Ep (one alarm's inputs, ALREADY CUT AT THE ALARM) and returns
{column: float}. Its docstring lines 'column: meaning [unit]' are the catalog (EPI_CATALOG_V1.tsv is generated from them; a test keeps
the two equal). Adding a question = adding one block and regenerating the catalog (python3 alarm_profile.py catalog).

WORDS USED BELOW (one definition each, the README says the same):
  push       the alarm's price direction: side +1 = pushed UP (shorts forced), -1 = pushed DOWN (longs forced). x = side x ln(close):
             every price value is in the push direction, + = the way the alarm pushed.
  close(s)   the close of the last 3 s PRICE bin whose end te <= s (te in integer microseconds): known at s.
  rows       the lab's 5 s liquidation rows (A1.S01 longs, A1.S02 shorts): row k is known at T5 + 5 k and covers (T5 + 5 k - 5, T5 + 5 k].
             The FORCED side's rows are A1.S02 when side +1, A1.S01 when side -1; the OTHER side's the opposite. A missing row (NaN)
             is a hole (NO_FILE, THIN_FEED, TRADES_HOLE), never zero.
  onset      the A01 onset of the alarm's episode (the alarm list's onset_t): the first 5 s step whose 60 s forced sum went over the
             coin's bar (a01_onset_v2: max(p99.9 of the 60 s sums of the 6 h before, 20,000 USD)).
  BURST START  the start of the first forced row with a print (> 0) inside the onset's 60 s window (rows k0 - 11 .. k0): the moment the
             liquidations that crossed the bar began. THE BURST = from the burst start to the alarm; every burst value (dollars,
             prices, speed, open interest) covers that same span.
  RUN START  where the move really started (a02_run_start_v1 80db84d8, its eye check 12 of 12, J471127), v2 (22 Oct 12:4xZ): on the
             1 min closes from 24 h before the alarm up to the RUN END (plus the close at the run end), take everything since the price
             last FELL by h = 3 x the coin's normal 15 min move (floor 0.1 pct) from a high; the start is the LAST point of it within
             one normal move of its lowest.
  RUN END    (v2) the price EXTREME since the burst start: the furthest close in the push direction among the close at the burst start
             (the onset window's start, onset - 60 s, when the burst has none) and every 3 s bin ending after it up to the alarm (the
             latest on ties); the alarm itself when the alarm's close is that extreme. Why: A02 fires after the climax; v1 searched up
             to the alarm, so a bounce of h or more between the extreme and the alarm restarted the run AT the alarm (run 0, giveback
             0; OP 3 Nov 15:32, 4.3 pct in the burst, read as no run: QUANT's look at the J471128 eye charts). The bounce now shows in
             the giveback, where it belongs; with no such bounce v2 = v1.
  PAUSE      (v3, the owner 22 Oct ~15:1x Berlin: "no progress, 30 min", chosen on QUANT's chart of 4 rules over SCOUT's 12 eye alarms):
             walking the run grid from the swing start (the v2 start above) to the run end, the price PROGRESSES at a close more than
             one normal move above the close of the last progress (the first reference: the swing start); a PAUSE is 30 min or more
             from one progress to the next (or from the last progress to the run end). When there is a pause, the run start moves to the
             LAST point of the LAST pause within one normal move of that pause's lowest close (the start of the final push); without one
             it stays at the swing start. Why: SCOUT's eye check 7 of 12 (J471128): after hours of sideways the eye puts the start at the
             final push, the swing rule kept the old low (ETH 24 Sep: 373 min, a 5 h flat; the final push 19 min).
  normal move  the median absolute 15 min log move over [alarm - 25 h, alarm - 1 h] (96 moves; at least 48 known).
KNOWN AT: the alarm. Ep cuts every input at the alarm (rows k <= the alarm's step, bins te <= t, open interest minute ends <= t, daily
totals of whole days before the burst's day) before any block runs, so no block can see later data (tests plant 1e12 after the alarm).
Uses SCOUT's tools/alarms (one definition each): a01_onset_v2.sums60 / bar_at (the 60 s sums and the bar), a02_climax_v3.f15."""
import datetime as dt
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'alarms'))
import a01_onset_v2 as A01                                           # noqa: E402  sums60, bar_at: the onset's definition
import a02_climax_v3 as A02                                          # noqa: E402  f15: the climax's 15 s sums

STEP = 5                                                             # seconds per liquidation row
WIN60 = 12                                                           # rows in 60 s
GRID_S, LOOK_S = 60, 86400                                           # the run start's 1 min grid over 24 h
NORM_FROM_S, NORM_TO_S, NORM_STEP_S, NORM_MIN = 25 * 3600, 3600, 900, 48
H_MULT, H_FLOOR = 3.0, 0.001                                         # a turn = a fall of 3 normal moves (at least 0.1 pct)
PAUSE_S = 1800                                                       # v3: a pause = 30 min or more without a normal move of progress
HIGH, QUIET, QUIET_STEPS = 0.5, 0.10, 3                              # flushes: >= half the peak; quiet <= 10 pct of it for 15 s
WEEK_DAYS, WEEK_MIN_DAYS, DAY_COVER = 7, 5, 0.9                      # the coin's normal day: 7 days before, >= 5 with >= 90 pct rows
PRE_S = 3600                                                         # the hour before the burst start
SPEED_MIN_S = 60                                                     # a speed needs at least 60 s
HL_BEFORE_S = 180                                                    # Hyperliquid's first liquidation may come up to 3 min before the burst start
KEEP_ROWS = A01.LOOK + WIN60 + PRE_S // STEP + 64                    # rows an Ep keeps before the onset (bar 6 h, 60 s sums, the hour before)
KEEP_PRICE_S = NORM_FROM_S + 3600                                    # prices an Ep keeps before the alarm (the normal move's 25 h, + 1 h)
MAX_PRICE_AGE_S = 60                                                  # STRATEGY-153335 (LAYERS; QUANT 16:00:47Z: 60 s, the draw V3 / proof_v3 / EWSD rule): older = NaN (STALE_PRICE)
RUN_END = 'burst_extreme'                                            # v2: the run search ends at the price extreme since the burst start
SETTINGS = dict(step_s=STEP, win60_rows=WIN60, grid_s=GRID_S, look_s=LOOK_S, run_end=RUN_END, pause_s=PAUSE_S, norm=[NORM_FROM_S, NORM_TO_S, NORM_STEP_S, NORM_MIN],
                h=[H_MULT, H_FLOOR], flush=[HIGH, QUIET, QUIET_STEPS], week=[WEEK_DAYS, WEEK_MIN_DAYS, DAY_COVER], pre_s=PRE_S,
                speed_min_s=SPEED_MIN_S, hl_before_s=HL_BEFORE_S, keep=[KEEP_ROWS, KEEP_PRICE_S], a01=[A01.W, A01.LOOK, A01.COVER, A01.FLOOR, A01.Q])
BLOCKS = []
NAN = float('nan')


def block(level, name):
    def wrap(f):
        BLOCKS.append((level, name, f)); return f
    return wrap


def lg(v):
    """log10 of USD: 0 when nothing (0 USD), NaN when not known"""
    return NAN if not np.isfinite(v) or v < 0 else (0.0 if v == 0 else float(np.log10(v)))


def div(a, b):
    return float(a) / float(b) if np.isfinite(a) and np.isfinite(b) and b != 0 else NAN


def utc_day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def run_start_index(x, h, eps=0.0):
    """x: push-signed log prices in time order (the last one at the alarm) -> (index of the run start, found a turn). The segment is
    everything after the price last FELL by h or more from a high (a turn; with no such fall, the whole window); the move started at the
    LAST point of that segment within eps of its lowest price (a flat, choppy bottom is not the start). (a02_run_start_v1, unchanged.)"""
    last_turn = -1; m = -np.inf; i_m = -1
    for i in range(len(x)):
        v = x[i]
        if not np.isfinite(v):
            continue
        if v > m:
            m, i_m = v, i
        elif v <= m - h:                                             # a fall of h from the high at i_m: a turn
            last_turn = i_m; m, i_m = v, i                           # track the next high from here
    seg = x[last_turn + 1:]
    near = np.flatnonzero(np.isfinite(seg) & (seg <= np.nanmin(seg) + eps))
    return int(near[-1]) + last_turn + 1, last_turn >= 0


def pause_start(ts, x, i0, eps, min_s=PAUSE_S):
    """v3 PAUSE: ts, x = the run grid's times (s) and push-signed log closes (the last one at the run end), i0 = the swing start ->
    (index of the run start, found a pause). Walking from i0, the price PROGRESSES at a close more than eps above the close of the
    last progress (the first: x[i0]); a pause is min_s or more from one progress to the next (or from the last one to the end); the
    start is the LAST point of the LAST pause within eps of its lowest close; with no pause, i0."""
    ref = x[i0]; iref = i0; last = None
    for i in range(i0 + 1, len(x)):
        v = x[i]
        if not np.isfinite(v):
            continue
        if v > ref + eps:
            if ts[i] - ts[iref] >= min_s:
                last = (iref, i - 1)
            ref, iref = v, i
    if ts[len(x) - 1] - ts[iref] >= min_s:
        last = (iref, len(x) - 1)
    if last is None:
        return i0, False
    a, b = last; seg = x[a:b + 1]
    near = np.flatnonzero(np.isfinite(seg) & (seg <= np.nanmin(seg) + eps))
    return a + int(near[-1]), True


class Ep:
    """ONE alarm's inputs, cut at the alarm. coin, t (the alarm, whole seconds on the 5 s grid), t0 (its A01 onset), side (+1 up / -1
    down); T5 = the time of row 0 of xf / xo (forced / other side 5 s rows, NaN = hole); te_us, px = 3 s PRICE bins (end time in us,
    close); daily = {day: (forced-side USD of the whole day, share of its rows known)} of whole UTC days; oi_t, oi_v, oi_c = open interest
    minute ends (s), coins, carried flag (lab E2.S02, E2.S03); hl = None (no Hyperliquid file) or {'days': set of UTC days whose file has
    trades (the coin traded on Hyperliquid), 'lt': liquidation fill times (s), 'usd': price x size, 'side': the liquidated account's fill
    side (+1 a buy: a short closed; -1 a sell: a long closed)}, the liquidated accounts' own rows only (SCOUT's HLF lself = 1).
    Nothing after t is kept (the known-at rule, in one place)."""
    def __init__(self, coin, t, t0, side, T5, xf, xo, te_us, px, daily, oi_t, oi_v, oi_c, hl=None):
        if any(not np.isfinite(v) or float(v) != int(v) for v in (t, t0, T5)):
            raise ValueError('episode clocks must be whole seconds, never silently truncated')
        self.coin = coin; self.t = int(t); self.t0 = int(t0); self.sgn = int(side)
        if (self.t - int(T5)) % STEP or (self.t0 - int(T5)) % STEP:
            raise ValueError('%s %d: the alarm and its onset must sit on the 5 s rows' % (coin, t))
        kt = (self.t - int(T5)) // STEP; k0 = (self.t0 - int(T5)) // STEP
        if self.sgn not in (-1, 1) or kt < 0 or k0 < 0 or k0 > kt:
            raise ValueError('invalid episode side or onset/alarm ordering')
        if np.asarray(xf).ndim != 1 or np.asarray(xo).ndim != 1 or len(xf) != len(xo) or len(xf) <= kt:
            raise ValueError('forced row arrays must cover the full onset-to-alarm clock')
        lo = max(0, k0 - KEEP_ROWS)                                  # only the rows a block may read: the bar's 6 h and the hour before
        self.T5 = int(T5) + STEP * lo; self.kt = kt - lo; self.k0 = k0 - lo
        self.xf = np.asarray(xf, float)[lo:kt + 1].copy(); self.xo = np.asarray(xo, float)[lo:kt + 1].copy()   # nothing after the alarm
        te_us = np.asarray(te_us, np.int64); px = np.asarray(px, float)
        hi = int(np.searchsorted(te_us, self.t * 1_000_000, side='right'))
        first = max(0, int(np.searchsorted(te_us, (self.t - KEEP_PRICE_S) * 1_000_000, side='left')) - 1)   # + the last bin before
        self.te_us = te_us[first:hi].copy(); self.px = px[first:hi].copy()
        oi_t = np.asarray(oi_t, float); k = oi_t <= self.t
        self.oi_t = oi_t[k]; self.oi_v = np.asarray(oi_v, float)[k]; self.oi_c = np.asarray(oi_c, float)[k]
        self.daily = dict(daily); self._c = {}; self.hl = None; self.stale_n = 0
        if hl is not None:
            lt = np.asarray(hl['lt'], float); k = lt <= self.t
            self.hl = dict(days=set(hl['days']), lt=lt[k], usd=np.asarray(hl['usd'], float)[k], side=np.asarray(hl['side'], float)[k])

    # ---- prices
    def close(self, s):
        """the close of the last bin with te <= s; NaN when none, or when that bin ended more than MAX_PRICE_AGE_S before s (STALE_PRICE)"""
        u = int(round(s * 1_000_000)); i = int(np.searchsorted(self.te_us, u, side='right')) - 1
        if i >= 0 and u - int(self.te_us[i]) > MAX_PRICE_AGE_S * 1_000_000:
            self.stale_n += 1; return NAN                                               # STALE_PRICE: a feed gap never reads as a flat price
        return float(self.px[i]) if i >= 0 and self.px[i] > 0 else NAN

    def closes(self, ss):
        ss = np.asarray(ss, float); u = np.round(ss * 1_000_000).astype(np.int64)
        i = np.searchsorted(self.te_us, u, side='right') - 1
        v = np.where(i >= 0, self.px[np.maximum(i, 0)] if len(self.px) else NAN, NAN)
        if len(self.te_us):
            st = (i >= 0) & (u - self.te_us[np.maximum(i, 0)] > MAX_PRICE_AGE_S * 1_000_000)
            self.stale_n += int(st.sum()); v = np.where(st, NAN, v)                     # STALE_PRICE
        return np.where(v > 0, v, NAN)

    def x(self, s):
        c = self.close(s); return self.sgn * float(np.log(c)) if np.isfinite(c) else NAN

    # ---- shared episode facts (computed once)
    def normal(self):
        if 'nm' not in self._c:
            g = self.closes(np.arange(self.t - NORM_FROM_S, self.t - NORM_TO_S + 1, NORM_STEP_S))
            m = np.abs(np.diff(np.log(g))); m = m[np.isfinite(m)]
            self._c['nm'] = float(np.median(m)) if len(m) >= NORM_MIN else NAN
        return self._c['nm']

    def run_end(self):
        """(time, push-signed log close) where the run search ends (v2, RUN END): the price extreme since the burst start (the onset
        window's start when the burst has none), the latest on ties; the alarm itself when the alarm's close is that extreme"""
        if 'end' not in self._c:
            _, tb = self.burst_rows()
            w0 = tb if np.isfinite(tb) else float(self.t0 - 60)
            k = (self.te_us > int(round(w0 * 1_000_000))) & (self.px > 0)
            ts = np.concatenate(([w0], self.te_us[k] / 1e6)); xs = np.concatenate(([self.x(w0)], self.sgn * np.log(self.px[k])))
            ok = np.isfinite(xs); xt = self.x(self.t); out = (float(self.t), xt)
            if ok.any():
                m = float(np.max(xs[ok])); i = int(np.flatnonzero(ok & (xs == m))[-1])
                if not (np.isfinite(xt) and xt >= m):
                    out = (float(ts[i]), m)
            self._c['end'] = out
        return self._c['end']

    def run(self):
        """(start time, turned) of the move's real start, or (NaN, False); the search runs from 24 h before the alarm to the run end"""
        if 'run' not in self._c:
            nm = self.normal(); out = (NAN, False)
            if np.isfinite(nm):
                h = max(H_MULT * nm, H_FLOOR); te = self.run_end()[0]
                grid = np.append(np.arange(self.t - LOOK_S, te, float(GRID_S)), float(te))
                c = self.closes(grid)
                if np.isfinite(c[-1]) and np.isfinite(c).sum() > 60:
                    xg = self.sgn * np.log(c)
                    i0, turned = run_start_index(xg, h, nm)
                    i1, paused = pause_start(grid, xg, i0, nm)               # v3: the start of the final push after the last pause
                    out = (float(grid[i1]), bool(turned or paused))
            self._c['run'] = out
        return self._c['run']

    def burst_rows(self):
        """(first row of the burst, its start time) or (None, NaN): the first forced row with a print in the onset's 60 s window"""
        if 'br' not in self._c:
            lo = self.k0 - WIN60 + 1; out = (None, NAN)
            if lo >= 0 and self.k0 <= self.kt:
                w = self.xf[lo:self.k0 + 1]; hit = np.flatnonzero(np.isfinite(w) & (w > 0))
                if len(hit):
                    k1 = lo + int(hit[0]); out = (k1, float(self.T5 + STEP * k1 - STEP))
            self._c['br'] = out
        return self._c['br']

    def series(self):
        """(f15, S60) of the forced rows (a02 / a01 definitions; NaN unless all their rows are known)"""
        if 'ser' not in self._c:
            clean = np.isfinite(self.xf)
            self._c['ser'] = (A02.f15(self.xf, clean), A01.sums60(self.xf, clean))
        return self._c['ser']

    def peak(self):
        """(peak15, step of it (the latest on ties), peak60) over the steps from the onset to the alarm"""
        if 'pk' not in self._c:
            F15, S60 = self.series(); a = F15[self.k0:self.kt + 1]; b = S60[self.k0:self.kt + 1]; out = (NAN, None, NAN)
            if np.isfinite(a).any():
                p = float(np.nanmax(a)); kp = self.k0 + int(np.flatnonzero(a == p)[-1])
                out = (p, kp, float(np.nanmax(b)) if np.isfinite(b).any() else NAN)
            self._c['pk'] = out
        return self._c['pk']

    def burst_sum(self, x):
        """sum of rows k1 .. kt of x (the burst), NaN with a hole"""
        k1, _ = self.burst_rows()
        if k1 is None:
            return NAN
        w = x[k1:self.kt + 1]
        return float(w.sum()) if np.isfinite(w).all() else NAN


# ---------------------------------------------------------------- MOVE: the price move from where it really started
@block('MOVE', 'run')
def mv_run(e):
    """normal_move_pct: the coin's normal 15 min move: the median absolute 15 min move over the 24 h ending 1 h before the alarm [log-pct]
    run_pct: how far the price moved in the push direction from the run start (where the move really started) to the alarm [log-pct]
    run_norm: run_pct in the coin's normal 15 min moves [normal moves]
    run_age_min: minutes from the run start to the alarm [min]
    run_capped: 1 = no turn (a fall of 3 normal moves) and no pause between 24 h before the alarm and the run end, so the move may be older than its start [flag]"""
    nm = e.normal(); st, turned = e.run(); out = dict(normal_move_pct=nm * 100 if np.isfinite(nm) else NAN, run_pct=NAN, run_norm=NAN,
                                                     run_age_min=NAN, run_capped=NAN)
    if np.isfinite(st):
        r = (e.x(e.t) - e.x(st)) * 100.0
        out.update(run_pct=r, run_norm=div(r, nm * 100), run_age_min=(e.t - st) / 60.0, run_capped=float(not turned))
    return out


@block('MOVE', 'split')
def mv_split(e):
    """pre_move_pct: the part of the run before the liquidations began: from the run start to the burst start, push direction (negative when the move started inside the burst) [log-pct]
    burst_move_pct: the part since the liquidations began: from the burst start to the alarm, push direction [log-pct]
    forced_share: burst_move_pct over run_pct (when run_pct > 0): the share of the move made since the liquidations began; above 1 when the move started inside the burst [share]
    giveback_pct: how far the price came back from the run's extreme (the furthest 3 s close in the push direction since the run start) by the alarm [log-pct]
    giveback_share: giveback_pct over the move from the run start to that extreme [share]"""
    st, _ = e.run(); _, tb = e.burst_rows(); out = dict(pre_move_pct=NAN, burst_move_pct=NAN, forced_share=NAN, giveback_pct=NAN, giveback_share=NAN)
    xt = e.x(e.t)
    if np.isfinite(tb):
        out['burst_move_pct'] = (xt - e.x(tb)) * 100.0
    if np.isfinite(st):
        xs = e.x(st); run = (xt - xs) * 100.0
        if np.isfinite(tb):
            out['pre_move_pct'] = (e.x(tb) - xs) * 100.0
            if run > 0:
                out['forced_share'] = out['burst_move_pct'] / run
        k = (e.te_us >= int(round(st * 1_000_000))) & (e.px > 0)
        if k.any() and np.isfinite(xt):
            ext = float(np.max(e.sgn * np.log(e.px[k])))
            out['giveback_pct'] = (ext - xt) * 100.0
            if ext > xs:
                out['giveback_share'] = (ext - xt) / (ext - xs)
    return out


# ---------------------------------------------------------------- SPEED: how fast it moved
@block('SPEED', 'speed')
def sp_speed(e):
    """burst_s: seconds from the burst start (the first liquidation of the burst) to the alarm [s]
    onset_to_alarm_s: seconds from the A01 onset to the alarm [s]
    burst_speed_pct_min: burst_move_pct per minute of the burst (NaN under 60 s) [log-pct per min]
    pre_speed_pct_min: pre_move_pct per minute from the run start to the burst start (NaN under 60 s) [log-pct per min]
    speed_ratio: burst_speed_pct_min over pre_speed_pct_min (when the move before was in the push direction): how many times faster the price moved once the liquidations began [ratio]
    burst_speed_vs_normal: burst_speed_pct_min over the coin's normal pace (its normal 15 min move per 15 min): 1 = the usual pace [ratio]
    max_move_60s_pct: the biggest 60 s move in the push direction inside the burst (60 s windows ending on the alarm's 5 s grid) [log-pct]"""
    st, _ = e.run(); _, tb = e.burst_rows(); nm = e.normal()
    out = dict(burst_s=NAN, onset_to_alarm_s=float(e.t - e.t0), burst_speed_pct_min=NAN, pre_speed_pct_min=NAN, speed_ratio=NAN,
               burst_speed_vs_normal=NAN, max_move_60s_pct=NAN)
    if not np.isfinite(tb):
        return out
    bs = e.t - tb; out['burst_s'] = bs; xt = e.x(e.t); xb = e.x(tb)
    if bs >= SPEED_MIN_S:
        out['burst_speed_pct_min'] = (xt - xb) * 100.0 / (bs / 60.0)
        if np.isfinite(nm):
            out['burst_speed_vs_normal'] = div(out['burst_speed_pct_min'], nm * 100.0 / 15.0)
        ends = np.arange(e.t, tb + 60 - 0.5, -STEP, dtype=float)
        if len(ends):
            mv = (e.sgn * (np.log(e.closes(ends)) - np.log(e.closes(ends - 60)))) * 100.0
            if np.isfinite(mv).any():
                out['max_move_60s_pct'] = float(np.nanmax(mv))
    if np.isfinite(st) and tb - st >= SPEED_MIN_S:
        out['pre_speed_pct_min'] = (xb - e.x(st)) * 100.0 / ((tb - st) / 60.0)
        if out['pre_speed_pct_min'] > 0:
            out['speed_ratio'] = div(out['burst_speed_pct_min'], out['pre_speed_pct_min'])
    return out


# ---------------------------------------------------------------- FORCED: the liquidations themselves
@block('FORCED', 'size')
def fo_size(e):
    """forced_usd_log: log10 of the forced side's liquidation USD from the burst start to the alarm (Binance publishes one print per coin per second: at least this much) [log10 usd]
    peak15_usd_log: log10 of the biggest 15 s forced sum from the onset to the alarm [log10 usd]
    peak60_usd_log: log10 of the biggest 60 s forced sum from the onset to the alarm [log10 usd]
    size_vs_bar: the biggest 60 s forced sum over the coin's A01 bar at the onset (its 6 h p99.9 of 60 s sums, at least 20,000 USD) [ratio]
    size_vs_week: the burst's forced USD over the coin's normal day: the median forced-side USD of the 7 whole UTC days before the burst's day (days with >= 90 pct of rows known, at least 5) [ratio]
    growth: the biggest 60 s forced sum over the 60 s sum at the onset: how much the burst grew after it was first seen [ratio]
    pre_forced_usd_log: log10 of the forced side's liquidation USD in the hour before the burst start [log10 usd, 0 = none]"""
    F15, S60 = e.series(); p15, _, p60 = e.peak(); usd = e.burst_sum(e.xf)
    bar = A01.bar_at(S60, e.k0)[0] if e.k0 <= e.kt else None
    k1, tb = e.burst_rows(); pre = NAN
    if k1 is not None and k1 - PRE_S // STEP >= 0:
        w = e.xf[k1 - PRE_S // STEP:k1]; pre = float(w.sum()) if np.isfinite(w).all() else NAN
    wk = NAN
    if np.isfinite(tb):
        b = utc_day(tb); v = [e.daily[d][0] for d in (shift(b, -j) for j in range(1, WEEK_DAYS + 1))
                             if d in e.daily and e.daily[d][1] >= DAY_COVER and np.isfinite(e.daily[d][0])]
        if len(v) >= WEEK_MIN_DAYS:
            wk = div(usd, float(np.median(v)))
    s0 = S60[e.k0] if e.k0 <= e.kt else NAN
    return dict(forced_usd_log=lg(usd), peak15_usd_log=lg(p15), peak60_usd_log=lg(p60), size_vs_bar=div(p60, bar) if bar else NAN,
                size_vs_week=wk, growth=div(p60, s0), pre_forced_usd_log=lg(pre))


@block('FORCED', 'shape')
def fo_shape(e):
    """peak_s: seconds from the burst start to the end of the biggest 15 s of forced liquidations (the latest on ties) [s]
    peak_to_alarm_s: seconds from the end of the biggest 15 s to the alarm [s]
    n_flushes: BIG waves of forced liquidations from the onset row to the alarm row: a wave starts at a 15 s sum at or above half the biggest; a new wave needs 3 consecutive known 15 s sums at or under 10 pct of the biggest since the last (an unknown sum or one in between resets that count) [count]
    active_share: share of the burst's 5 s rows holding a forced print [share]
    top5s_share: the biggest single 5 s row's share of the burst's forced USD (1 = one row made it all) [share]"""
    F15, _ = e.series(); p15, kp, _ = e.peak(); k1, tb = e.burst_rows(); usd = e.burst_sum(e.xf)
    out = dict(peak_s=NAN, peak_to_alarm_s=NAN, n_flushes=NAN, active_share=NAN, top5s_share=NAN)
    if kp is not None:
        tp = e.T5 + STEP * kp; out['peak_to_alarm_s'] = float(e.t - tp)
        if np.isfinite(tb):
            out['peak_s'] = float(tp - tb)
        if p15 > 0:
            n = 0; quiet = 0; armed = False
            for k in range(e.k0, e.kt + 1):
                v = F15[k]
                if not np.isfinite(v):
                    quiet = 0; continue
                if v >= HIGH * p15:
                    if n == 0:
                        n = 1
                    elif armed:
                        n += 1; armed = False
                    quiet = 0
                elif v <= QUIET * p15:
                    quiet += 1
                    if n > 0 and quiet >= QUIET_STEPS:
                        armed = True
                else:
                    quiet = 0
            out['n_flushes'] = float(n)
    if k1 is not None and np.isfinite(usd):
        w = e.xf[k1:e.kt + 1]; out['active_share'] = float(np.mean(w > 0))
        if usd > 0:
            out['top5s_share'] = float(np.max(w)) / usd
    return out


@block('FORCED', 'other')
def fo_other(e):
    """other_usd_log: log10 of the OTHER side's liquidation USD over the burst (from the burst start to the alarm) [log10 usd, 0 = none]
    other_share: the other side's USD over both sides' USD over the burst [share]"""
    f = e.burst_sum(e.xf); o = e.burst_sum(e.xo)
    return dict(other_usd_log=lg(o), other_share=div(o, f + o))


# ---------------------------------------------------------------- POSITIONS: what the open positions did in the burst
@block('POSITIONS', 'oi')
def po_oi(e):
    """oi_chg_burst_pct: Binance open interest (in coins) at the last minute end at or before the alarm over the one at the last minute end at or before the burst start, minus 1 (- = positions closed; NaN when both are the same minute end or the later one is carried from an older row) [pct]
    burst_vs_oi_bp: the burst's forced USD over the open interest in USD at the burst start (coins x the close there) [bp]"""
    _, tb = e.burst_rows(); out = dict(oi_chg_burst_pct=NAN, burst_vs_oi_bp=NAN)
    if not np.isfinite(tb) or not len(e.oi_t):
        return out
    ib = int(np.searchsorted(e.oi_t, tb, side='right')) - 1; ia = len(e.oi_t) - 1
    if ib < 0:
        return out
    vb = e.oi_v[ib]
    if np.isfinite(vb) and vb > 0:
        out['burst_vs_oi_bp'] = div(e.burst_sum(e.xf), vb * e.close(tb)) * 1e4
        va = e.oi_v[ia]
        if ia > ib and np.isfinite(va) and va > 0 and e.oi_c[ia] == 0:
            out['oi_chg_burst_pct'] = (va / vb - 1.0) * 100.0
    return out


# ---------------------------------------------------------------- HL: the same burst seen on another exchange (Hyperliquid, every liquidation)
@block('HL', 'hyperliquid')
def hl_liq(e):
    """hl_forced_usd_log: log10 of Hyperliquid's liquidations on the FORCED side (the liquidated accounts' fills, price x size; Hyperliquid's record holds every liquidation) from the burst start to the alarm (NaN when our Hyperliquid files miss the day or the coin had no Hyperliquid trades that day) [log10 usd, 0 = none]
    hl_other_usd_log: the same for the OTHER side [log10 usd, 0 = none]
    hl_lead_s: seconds by which Hyperliquid's first forced-side liquidation, from 3 min before the burst start to the alarm, came BEFORE the burst start (+ = Hyperliquid liquidated first; NaN = none in that window or not covered) [s]"""
    out = dict(hl_forced_usd_log=NAN, hl_other_usd_log=NAN, hl_lead_s=NAN)
    _, tb = e.burst_rows()
    if e.hl is None or not np.isfinite(tb) or utc_day(tb - HL_BEFORE_S) not in e.hl['days'] or utc_day(e.t) not in e.hl['days']:
        return out
    day = utc_day(tb - HL_BEFORE_S)
    while day <= utc_day(e.t):
        if day not in e.hl['days']:
            return out
        day = shift(day, 1)
    lt, usd, sd = e.hl['lt'], e.hl['usd'], e.hl['side']; w = lt > tb
    out['hl_forced_usd_log'] = lg(float(usd[w & (sd == e.sgn)].sum())); out['hl_other_usd_log'] = lg(float(usd[w & (sd == -e.sgn)].sum()))
    f = (lt > tb - HL_BEFORE_S) & (sd == e.sgn)
    if f.any():
        out['hl_lead_s'] = float(tb - lt[f].min())
    return out


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
            col, mean = l.split(':', 1); mean = mean.strip(); unit = ''
            if mean.endswith(']') and '[' in mean:
                unit = mean[mean.rindex('[') + 1:-1].strip(); mean = mean[:mean.rindex('[')].strip()
            out.append((lv, name, col.strip(), mean, unit))
    return out


def run_one(e):
    """{column: float} of every block for one Ep, in block order; a column the docstrings do not name is refused"""
    named = [c[2] for c in doc_columns()]; out = {k: NAN for k in named}
    for lv, name, f in BLOCKS:
        with np.errstate(divide='ignore', invalid='ignore'):
            got = f(e)
        for k, v in got.items():
            if k not in out:
                raise ValueError('block %s returns %s, not in its docstring: add the catalog line' % (name, k))
            out[k] = float(v)
    return out


def run(eps):
    """{column: (n,) float} of every block over the alarms eps (any iterable of Ep, used one at a time)"""
    rows = [run_one(e) for e in eps]; named = [c[2] for c in doc_columns()]
    return {k: np.array([r[k] for r in rows], float) for k in named}
