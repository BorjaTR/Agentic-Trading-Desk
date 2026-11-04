"""[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file i2g_rules_v1.py 29cd896d5436693a (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
i2g_rules_v1_2.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026; V3.1 = the six fixes of REVIEW_IDEA_TO_GRADE_V3_INDEP): the grading rules moved from the alarm library contract
(team/RESEARCH/LIBRARY/alarm_library/alarm_core_v1.py, 18 tests, 18 mutants) into the grading tool, as pure functions on numbers and arrays.
No file of the lab is read here, and no alarm, coin, day or price level is held in this code: every one of them is the caller's input.
  1 AS-OF CONTROL ELIGIBILITY  a moment is eligible when no alarm or parent of its coin lies in [t - 4 h, t]; a LATER alarm never removes it
  2 EVENT IDENTITY             parent id = coin, emission second and side; two opposite-side fires in one second stay two events
  3 FROZEN CLUSTER UNIVERSE    clusters built ONCE per alarm on its whole fire list (30 min gap, a cluster never spans more than 4 h: the
                               chain is split and flagged), fixed weights 1/size; every slice reads them, none rebuilds them
  4 AS-OF FEATURES             signed 15 min move and 5 min realized volatility at t, from 3 s bins that ended at or before t
  5 TOUGH POOL                 same-coin moments, as-of eligible, with a similar signed move and volatility, drawn by seed
  6 PATHS                      returns at fixed horizons; target / stop / time exits (target and stop inside one bin = the stop); a resting
                               order fills only on a strict trade-through (a touch is not a fill)
  7 COSTS                      per entry type from the cost table: taker leg, resting leg, honest and stress gap
  8 STATISTICS                 wave-clustered weighted mean and 95% interval
  9 TRIES LEDGER               a run needs an open PREREG ask id whose idea and days are the run's; each ask admits ONE complete run (a
                               claim file beside the ledger; the ledger itself is only read)
 10 ALARM REGISTRY             the run's alarm id must be a registry id; an idea must be its registered definition
The as-of rule, the cluster chain, the same-bin rule and the trade-through rule are the ONE shared copy in alarm_contract_v1.py (F6).
Prices across a feed hole are unknown, never the last close (F1: MAX_STALE_S)."""
import csv, hashlib, json, math, os, re, sys, zlib
import numpy as np
_HERE = os.path.dirname(os.path.realpath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import alarm_contract_v1 as C

US = 1_000_000
ASOF_BEFORE_S = C.ASOF_BEFORE_S       # an alarm or parent in the 4 h up to and including the moment makes it busy
WAVE_GAP_S = C.WAVE_GAP_S             # fires closer than 30 min join one cluster
WAVE_MAX_SPAN_S = C.WAVE_MAX_SPAN_S   # a cluster never spans more than 4 h from its first fire (a longer chain is split, flagged)
MAX_STALE_S = 60                      # a price is known at x only when a bin's last trade lies in [x - 60 s, x]; a longer gap is a hole
HORIZONS_S = (10, 60, 300, 900, 3600, 14400)
HORIZON_NAMES = ('10s', '1m', '5m', '15m', '1h', '4h')
# the fixed exit grid, the same for every alarm and every control: (name, kind, target, stop, time limit s)
#   kind 'VOL': target and stop in units of the row's own 5 min realized volatility at its clock; kind 'COST': in units of the coin cost c
EXITS = (('V1_15m', 'VOL', 1.0, 1.0, 900), ('V1_1h', 'VOL', 1.0, 1.0, 3600), ('V1_4h', 'VOL', 1.0, 1.0, 14400),
         ('V2_15m', 'VOL', 2.0, 2.0, 900), ('V2_1h', 'VOL', 2.0, 2.0, 3600), ('V2_4h', 'VOL', 2.0, 2.0, 14400),
         ('C2C1_1h', 'COST', 2.0, 1.0, 3600), ('C4C2_4h', 'COST', 4.0, 2.0, 14400))
EXIT_CODES = {'TARGET': 1.0, 'STOP': 2.0, 'AMBIGUOUS_STOP': 3.0, 'TIME': 4.0, 'PATH_HOLE': 5.0}   # PATH_HOLE: value unknown
RESTING_WAIT_S = 60                   # a resting entry waits at most this long for a trade-through
TOUGH = dict(k=10, grid_s=60, move_tol_c=0.5, move_tol_rel=0.25, rv_lo=0.8, rv_hi=1.25, min_n=3, days=7)


class Refused(ValueError):
    def __init__(self, code, detail=''):
        super().__init__('%s: %s' % (code, detail)); self.code = code


# ---------------------------------------------------------------------------------------------------- 1 as-of control eligibility
def asof_flag(cand_t, busy_sorted, before_s=ASOF_BEFORE_S):
    """'' when no time of busy_sorted (the coin's alarms and parents, seconds, sorted) lies in [cand_t - before_s, cand_t];
    'ASOF_BUSY' otherwise. Only the past and the moment itself count: an alarm after cand_t never changes the answer."""
    return 'ASOF_BUSY' if C.asof_busy(cand_t, busy_sorted, before_s) else ''


def asof_mask(times, busy_sorted, before_s=ASOF_BEFORE_S):
    """vector form of asof_flag (the same rule, for arrays; a test holds it equal to alarm_contract_v1.asof_busy): True = eligible"""
    b = np.asarray(busy_sorted, float); t = np.asarray(times, float)
    i = np.searchsorted(b, t - before_s, 'left')
    hit = np.zeros(len(t), bool); ok = i < len(b)
    hit[ok] = b[i[ok]] <= t[ok]
    return ~hit


# ---------------------------------------------------------------------------------------------------- 2 event identity
def parent_id(coin, t, side):
    """the parent's identity: coin, emission second, side. (coin, t) alone is never a key"""
    if side not in (-1, 1):
        raise Refused('EVENT_SIDE', 'side %r' % (side,))
    return '%s_%d_%+d' % (coin, int(t), int(side))


def moment_id(coin, t):
    """the moment's identity for the matcher's random stream (draw_v3: seed + crc32(id)): two sides of one moment draw the same controls"""
    return '%s_%d' % (coin, int(t))


def event_key(alarm_id, version, coin, t, side):
    return '%s|%s|%s|%d|%+d' % (alarm_id, version, coin, int(t), int(side))


# ---------------------------------------------------------------------------------------------------- 3 frozen cluster universe
UNIVERSE_COLS = ('alarm_id', 'coin', 't', 'side', 'parent_id', 'cluster_id', 'weight', 'cluster_size', 'flag')
UNIVERSE_HEADER = '# I2G_UNIVERSE_V1 gap_s %d max_span_s %d' % (WAVE_GAP_S, WAVE_MAX_SPAN_S)


def build_clusters(fires, gap_s=WAVE_GAP_S, max_span_s=WAVE_MAX_SPAN_S):
    """fires [(alarm_id, coin, t, side)] -> rows (UNIVERSE_COLS), per alarm over ALL its coins in time order: a fire joins the open cluster
    when it is at most gap_s after the previous fire AND at most max_span_s after the cluster's first fire; a fire refused only by the span
    rule opens a new cluster flagged CHAIN_SPLIT. Weight = 1 / cluster size (each cluster counts once). Never reads an outcome."""
    by = {}
    for a, c, t, s in fires:
        by.setdefault(str(a), []).append((int(t), str(c), int(s)))
    rows = []
    for a in sorted(by):
        fs = sorted(set(by[a]))
        if len(fs) != len(by[a]):
            raise Refused('UNIVERSE_DUPLICATE', '%s: a fire is listed twice' % a)
        groups = []
        for f, (n, flag) in zip(fs, C.chain([x[0] for x in fs], gap_s, max_span_s)):
            if n == len(groups):
                groups.append([flag, []])
            groups[-1][1].append(f)
        for flag, g in groups:
            cid = '%s:%d' % (a, g[0][0])
            for t, c, s in g:
                rows.append((a, c, t, s, parent_id(c, t, s), cid, 1.0 / len(g), len(g), flag))
    return rows


def write_universe(path, rows, sources):
    """sources: [(path, sha16)] of the fire lists it was built from; refuses to overwrite"""
    with open(path, 'x') as f:
        f.write(UNIVERSE_HEADER + '\n')
        for p, h in sources:
            f.write('# source %s %s\n' % (p, h))
        f.write('\t'.join(UNIVERSE_COLS) + '\n')
        for r in rows:
            f.write('\t'.join(repr(x) if isinstance(x, float) else str(x) for x in r) + '\n')


class Universe:
    """a frozen universe file: weights and cluster ids by (alarm_id, parent id); subgroup() refuses an event the universe does not hold.
    read() trusts nothing in the file (F2): the header must name this code's gap and span, and every row must equal the row build_clusters
    gives on the file's own fires (cluster id, weight 1 / size, size, flag; no fire twice)."""
    def __init__(self, rows, name, sources=None):
        self.name = name; self.by = {}; self.sources = dict(sources or {}); self.rows = list(rows)
        for r in self.rows:
            if (r[0], r[4]) in self.by:
                raise Refused('UNIVERSE_DUPLICATE', '%s: %s %s is listed twice' % (name, r[0], r[4]))
            self.by[(r[0], r[4])] = (r[5], float(r[6]), r[8])

    @classmethod
    def read(cls, path):
        with open(path) as f:
            lines = f.read().split('\n')
        head = [l for l in lines if l.startswith('#')]
        if not head or head[0] != UNIVERSE_HEADER:
            raise Refused('UNIVERSE_HEADER', '%s: header %r, this code builds %r' % (path, head[:1], UNIVERSE_HEADER))
        sources = {}
        for l in head[1:]:
            if l.startswith('# source '):
                spec, h = l[len('# source '):].rsplit(' ', 1); aid, p = spec.split('=', 1)
                sources[aid] = (p, h)
        rows = list(csv.reader((l for l in lines if l and not l.startswith('#')), delimiter='\t'))
        if not rows or tuple(rows[0]) != UNIVERSE_COLS:
            raise Refused('UNIVERSE_FORMAT', path)
        try:
            got = [(r[0], r[1], int(r[2]), int(r[3]), r[4], r[5], float(r[6]), int(r[7]), r[8]) for r in rows[1:]]
        except (IndexError, ValueError) as e:
            raise Refused('UNIVERSE_FORMAT', '%s: %s' % (path, e))
        want = build_clusters([(r[0], r[1], r[2], r[3]) for r in got])
        if sorted(got) != sorted(want):
            bad = sorted(set(got) - set(want))
            raise Refused('UNIVERSE_INCONSISTENT', '%s: %d rows differ from the clusters of its own fires, e.g. %s' % (path, len(bad), bad[:2]))
        if set(sources) != {r[0] for r in got}:
            raise Refused('UNIVERSE_SOURCES', '%s: sources %s, alarms %s' % (path, sorted(sources), sorted({r[0] for r in got})))
        return cls(got, path, sources)

    def subgroup(self, alarm_id, pids):
        missing = [p for p in pids if (alarm_id, p) not in self.by]
        if missing:
            raise Refused('UNIVERSE_MISSING_EVENT', '%d events of %s are not in the frozen universe %s, e.g. %s'
                          % (len(missing), alarm_id, self.name, missing[:3]))
        return {p: self.by[(alarm_id, p)] for p in pids}

    def merged_clusters(self, alarm_id):
        """chain-split sensitivity: cluster id -> the id of the first cluster of its chain (a CHAIN_SPLIT cluster joins the one before it)"""
        firsts = sorted({(int(r[5].rsplit(':', 1)[1]), r[5], r[8]) for r in self.rows if r[0] == alarm_id})
        out = {}; root = None
        for _, cid, flag in firsts:
            root = root if flag == 'CHAIN_SPLIT' and root is not None else cid
            out[cid] = root
        return out


# ---------------------------------------------------------------------------------------------------- 4 as-of features
def asof_features(te_s, px, times, move_s=900, vol_s=300, max_stale_s=60):
    """te_s: bin end clocks (seconds, sorted), px: closes. For each clock t -> (move_pct, rv_pct):
      move = 100 (p(t) / p(t - move_s) - 1), p(x) = the close of the last bin that ended at or before x (NaN when it ended more than
             max_stale_s before x);
      rv   = 100 sqrt(sum of squared log returns between consecutive bins whose later bin ended in (t - vol_s, t]) (NaN with fewer than
             vol_s / 6 returns: half of the 3 s bins).
    Unsigned: the caller signs the move by the side."""
    te = np.asarray(te_s, float); p = np.asarray(px, float); t = np.atleast_1d(np.asarray(times, float))
    n = len(te); mv = np.full(len(t), np.nan); rv = np.full(len(t), np.nan)
    if n < 2:
        return mv, rv
    lr = np.r_[0.0, np.diff(np.log(p))]; cs = np.cumsum(lr * lr)
    i = np.searchsorted(te, t, 'right') - 1; j = np.searchsorted(te, t - move_s, 'right') - 1
    ok = (i >= 0) & (j >= 0)
    ok[ok] &= (t[ok] - te[i[ok]] <= max_stale_s) & ((t[ok] - move_s) - te[j[ok]] <= max_stale_s)
    mv[ok] = 100.0 * (p[i[ok]] / p[j[ok]] - 1.0)
    k = np.searchsorted(te, t - vol_s, 'right') - 1                      # the last bin at or before t - vol_s: returns after it count
    cnt = i - np.maximum(k, 0); ok2 = (i >= 1) & (cnt >= vol_s / 6.0)
    ok2[ok2] &= t[ok2] - te[i[ok2]] <= max_stale_s
    base = np.where(k >= 0, cs[np.maximum(k, 0)], 0.0)
    rv[ok2] = 100.0 * np.sqrt(np.maximum(cs[i[ok2]] - base[ok2], 0.0))
    return mv, rv


# ---------------------------------------------------------------------------------------------------- 5 the tough pool
def tough_pick(pid, seed, side, move_p, rv_p, c_pct, grid_t, grid_move, grid_rv, eligible, k=TOUGH['k'], move_tol_c=TOUGH['move_tol_c'],
               move_tol_rel=TOUGH['move_tol_rel'], rv_lo=TOUGH['rv_lo'], rv_hi=TOUGH['rv_hi'], min_n=TOUGH['min_n']):
    """the tough baseline of one parent: among the candidate grid moments (same coin, the caller's day domain) that are as-of eligible, the
    ones whose move SIGNED BY THE PARENT'S SIDE is within max(move_tol_c x c, move_tol_rel x |parent move|) of the parent's and whose
    volatility is within [rv_lo, rv_hi] x the parent's; up to k drawn without replacement by (seed, crc32(pid)), sorted by time.
    -> (chosen times, status, pool size). status TOUGH_UNKNOWN (no parent feature), TOUGH_NO_COST (no cost of record), TOUGH_NONE, TOUGH_THIN (< min_n), TOUGH_OK."""
    if not (np.isfinite(move_p) and np.isfinite(rv_p) and rv_p > 0):
        return [], 'TOUGH_UNKNOWN', 0
    if not np.isfinite(c_pct):
        return [], 'TOUGH_NO_COST', 0                 # the move tolerance needs the coin cost: no tough pool without one
    m = side * np.asarray(grid_move, float); r = np.asarray(grid_rv, float); mp = side * move_p
    tol = max(move_tol_c * c_pct, move_tol_rel * abs(mp))
    q = np.asarray(eligible, bool) & np.isfinite(m) & np.isfinite(r) & (np.abs(m - mp) <= tol) & (r >= rv_lo * rv_p) & (r <= rv_hi * rv_p)
    pool = np.flatnonzero(q)
    if len(pool) == 0:
        return [], 'TOUGH_NONE', 0
    rng = np.random.default_rng([int(seed), zlib.crc32(('tough|' + pid).encode())])
    pick = np.sort(rng.choice(pool, size=min(k, len(pool)), replace=False))
    chosen = [float(np.asarray(grid_t, float)[i]) for i in pick]
    return chosen, ('TOUGH_OK' if len(chosen) >= min_n else 'TOUGH_THIN'), int(len(pool))


# ---------------------------------------------------------------------------------------------------- 6 paths
def known_end_us(loaded_days, t_us, day_of, shift, day_start_s):
    """the end of the contiguous run of loaded days holding t_us: 00:00 of the first day after it that is not loaded"""
    d = day_of(t_us // US)
    while d in loaded_days:
        d = shift(d, 1)
    return int(day_start_s(d)) * US


def _last_at_or_before(tl, x, lo):
    j = int(np.searchsorted(tl, x, 'right')) - 1
    return j if j >= lo else -1


def horizon_returns(tl, px, i_fill, t_fill_us, fill_px, side, known_end, horizons_s=HORIZONS_S, max_stale_s=MAX_STALE_S, holes=None):
    """gross return in the traded side (pct) at fill + H: the close of the last bin whose last trade is at or before fill + H; NaN when
    fill + H lies beyond the known path, and NaN when that last trade is more than max_stale_s before fill + H (a feed hole: the price at
    fill + H is not known; holes, a list, gets one entry per such horizon). A hole earlier in the path does not change the price at fill + H."""
    out = []
    for H in horizons_s:
        x = t_fill_us + int(H * US)
        j = _last_at_or_before(tl, x, i_fill) if x <= known_end else -1
        if j >= 0 and x - int(tl[j]) > max_stale_s * US:
            j = -1
            if holes is not None:
                holes.append(H)
        out.append(side * 100.0 * (px[j] / fill_px - 1.0) if j >= 0 else np.nan)
    return out


def barrier_exit(tl, px, hi, lo, i_start, t_from_us, entry_px, side, target_pct, stop_pct, limit_s, known_end, resting_target=False,
                 max_stale_s=MAX_STALE_S):
    """the first exit after the entry over the bins after index i_start whose last trade is in (t_from, t_from + limit]:
      STOP   the bin's adverse extreme reaches the stop; exit at the stop or the bin's close, whichever is worse (a taker stop);
      AMBIGUOUS_STOP  target and stop inside ONE bin: the order inside the bin is unknown, scored as the stop, never the target;
      TARGET the favourable extreme reaches the target (resting_target: only a STRICT trade-through, a touch is not a fill); exit at it;
      TIME   no barrier by the limit: the close of the last bin at or before the limit.
      PATH_HOLE  (F1) before any barrier, two consecutive trades of the walked span (from t_from) are more than max_stale_s apart, or the
             time exit's last trade is more than max_stale_s before the limit: a barrier may have been crossed unseen, the value is unknown
             (-> ('PATH_HOLE', the clock that ends the hole, NaN)).
    -> (code, exit clock us, gross pct in the traded side), or (None, None, NaN) when the limit lies beyond the known path and no barrier
    was hit before the path ends. The same-bin rule is alarm_contract_v1.bin_exit."""
    if not (np.isfinite(target_pct) and np.isfinite(stop_pct) and target_pct > 0 and stop_pct > 0):
        return None, None, np.nan
    tp = entry_px * (1 + side * target_pct / 100.0); sl = entry_px * (1 - side * stop_pct / 100.0)
    end = t_from_us + int(limit_s * US); last = min(end, known_end); stale = int(max_stale_s * US)
    j1 = int(np.searchsorted(tl, last, 'right')); prev = int(t_from_us)
    for j in range(i_start + 1, j1):
        if tl[j] <= t_from_us:
            continue
        if int(tl[j]) - prev > stale:
            return 'PATH_HOLE', int(tl[j]), np.nan
        prev = int(tl[j])
        code = C.bin_exit(side, hi[j], lo[j], tp, sl, resting_target)
        if code is None:
            continue
        if code == 'TARGET':
            return 'TARGET', int(tl[j]), side * 100.0 * (tp / entry_px - 1.0)
        x = min(sl, px[j]) if side > 0 else max(sl, px[j])
        return code, int(tl[j]), side * 100.0 * (x / entry_px - 1.0)
    if end > known_end:
        return None, None, np.nan
    j = _last_at_or_before(tl, end, i_start)
    if j < 0:
        return None, None, np.nan
    if end - int(tl[j]) > stale:
        return 'PATH_HOLE', int(end), np.nan
    return 'TIME', int(tl[j]), side * 100.0 * (px[j] / entry_px - 1.0)


def passive_entry(tl, px, lo, hi, t_dec_us, side, wait_s=RESTING_WAIT_S, max_stale_s=MAX_STALE_S):
    """a resting entry at the decision: limit = the close of the last bin at or before the decision; filled at the limit in the first later
    bin (last trade in (decision, decision + wait]) whose extreme trades THROUGH it (buy: low < limit; sell: high > limit). A touch is not
    a fill. The decision price is known only when that bin's last trade lies in [decision - max_stale_s, decision] (F1); an older price
    is no price (V3.2, external review blocker 2).
    -> ('FILLED', bin index, clock us, limit) | ('UNFILLED', None, None, limit) | ('NO_PRICE', None, None, NaN)"""
    i0 = int(np.searchsorted(tl, t_dec_us, 'right')) - 1
    if i0 < 0 or int(t_dec_us) - int(tl[i0]) > int(max_stale_s * US):
        return 'NO_PRICE', None, None, np.nan
    L = float(px[i0]); end = t_dec_us + int(wait_s * US)
    j1 = int(np.searchsorted(tl, end, 'right'))
    for j in range(i0 + 1, j1):
        if tl[j] <= t_dec_us:
            continue
        if C.trades_through(side, hi[j], lo[j], L):
            return 'FILLED', j, int(tl[j]), L
    return 'UNFILLED', None, None, L


def exit_levels(kind, a, b, rv_pct, c_pct):
    """(target pct, stop pct) of one exit of the grid for a row whose own volatility is rv_pct and whose coin cost is c_pct"""
    unit = rv_pct if kind == 'VOL' else c_pct
    return a * unit, b * unit


def value_names():
    """the V3 measurement columns of every observation row (VALUES3.npy), in order"""
    n = ['move15_pct', 'rv5_pct', 'c_pct', 'tk_filled']
    n += ['ret_%s' % h for h in HORIZON_NAMES]
    for e in EXITS:
        n += ['tk_%s' % e[0], 'tk_%s_code' % e[0]]
    n += ['rs_filled', 'rs_wait_s']
    for e in EXITS:
        n += ['re_%s' % e[0], 'rb_%s' % e[0], 'rb_%s_code' % e[0]]
    n += ['path_holes']                   # how many values of the row are unknown because of a feed hole (F1)
    return n


def path_values(pv_tl, pv_px, pv_hi, pv_lo, taker, t_dec_us, side_traded, known_end, move_pct, rv_pct, c_pct):
    """one observation row of value_names(): taker = (status, bin index, fill clock us, fill px) of the BED taker fill (fill_v2), the
    decision clock = alarm + delay; side_traded = the side of the trade (FADE already flipped)"""
    names = value_names(); v = dict.fromkeys(names, np.nan)
    v['move15_pct'], v['rv5_pct'], v['c_pct'] = move_pct, rv_pct, c_pct
    st, i_f, t_f, p_f = taker
    v['tk_filled'] = 1.0 if st == 'FILLED' else 0.0
    holes = []
    if st == 'FILLED':
        for h, r in zip(HORIZON_NAMES, horizon_returns(pv_tl, pv_px, i_f, t_f, p_f, side_traded, known_end, holes=holes)):
            v['ret_%s' % h] = r
        for name, kind, a, b, lim in EXITS:
            tg, sp = exit_levels(kind, a, b, rv_pct, c_pct)
            code, _, g = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, i_f, t_f, p_f, side_traded, tg, sp, lim, known_end)
            v['tk_%s' % name] = g; v['tk_%s_code' % name] = EXIT_CODES.get(code, np.nan); holes += [name] if code == 'PATH_HOLE' else []
    rs, j, t_r, L = passive_entry(pv_tl, pv_px, pv_lo, pv_hi, t_dec_us, side_traded)
    v['rs_filled'] = 1.0 if rs == 'FILLED' else 0.0 if rs == 'UNFILLED' else np.nan
    if rs == 'FILLED':
        v['rs_wait_s'] = (t_r - t_dec_us) / US
        for name, kind, a, b, lim in EXITS:
            tg, sp = exit_levels(kind, a, b, rv_pct, c_pct)
            c1, _, g = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, j, t_r, L, side_traded, tg, sp, lim, known_end)
            code, _, g2 = barrier_exit(pv_tl, pv_px, pv_hi, pv_lo, j, t_r, L, side_traded, tg, sp, lim, known_end, resting_target=True)
            v['re_%s' % name] = g; v['rb_%s' % name] = g2; v['rb_%s_code' % name] = EXIT_CODES.get(code, np.nan)
            holes += [name] * ((c1 == 'PATH_HOLE') + (code == 'PATH_HOLE'))
    v['path_holes'] = float(len(holes))
    return np.array([v[n] for n in names], float)


# ---------------------------------------------------------------------------------------------------- 7 costs
def read_costs(path):
    """the cost table (coin, cost_bp = taker fee round trip + book walk round trip, fee_bp) -> {coin: (cost_bp, fee_bp)}"""
    with open(path) as f:
        rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    out = {}
    for r in rows:
        out[r['coin']] = (float(r['cost_bp']), float(r['fee_bp']))
    if not out:
        raise Refused('COSTS_FILE', path)
    return out


def cost_legs(cost_bp, gap_pct, maker_fee_bp):
    """-> (taker leg pct, resting leg pct): a taker leg pays half of the round-trip cost of record (fee + book walk) plus half the gap; a
    resting leg pays the resting fee plus half the gap (no book walk)"""
    return cost_bp / 200.0 + gap_pct / 2.0, maker_fee_bp / 100.0 + gap_pct / 2.0


def coin_cost_pct(cost_bp, gap_pct):
    """c: the round-trip taker cost of record, pct"""
    return cost_bp / 100.0 + gap_pct


# ---------------------------------------------------------------------------------------------------- 8 statistics
def clustered_mean(x, w, clusters):
    """weighted mean of the finite x with weights w, and its 95% interval with the CLUSTER as the unit (linearised ratio estimator: each
    cluster's weighted sum is one draw). -> dict(mean, lo, hi, se, parents, clusters)"""
    x = np.asarray(x, float); w = np.asarray(w, float); cl = np.asarray(clusters, dtype=object)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w, cl = x[ok], w[ok], cl[ok]
    if len(x) == 0:
        return dict(mean=np.nan, lo=np.nan, hi=np.nan, se=np.nan, parents=0, clusters=0)
    W = w.sum(); m = float((w * x).sum() / W)
    keys = {}
    for i, c in enumerate(cl):
        keys.setdefault(c, []).append(i)
    G = len(keys)
    if G < 2:
        return dict(mean=m, lo=np.nan, hi=np.nan, se=np.nan, parents=int(len(x)), clusters=G)
    u = np.array([float((w[ix] * (x[ix] - m)).sum()) for ix in keys.values()])
    se = math.sqrt(G / (G - 1) * float((u * u).sum())) / W
    return dict(mean=m, lo=m - 1.96 * se, hi=m + 1.96 * se, se=se, parents=int(len(x)), clusters=G)


# ---------------------------------------------------------------------------------------------------- 9 tries ledger
ASK_RE = re.compile(r'^[A-Za-z0-9_.-]{1,200}$')


def ledger_check(path, ask_id, idea=None, first=None, last=None):
    """the run's ask id must be a PREREG row of the tries ledger with no RESULT and no WITHDRAWN row (read only), whose idea is the run's
    alarm id and whose days_from / days_to are the run's --first / --last (F3; a blank day is refused), and that no complete run has
    claimed yet (ledger_claim) -> the PREREG row"""
    if not ask_id:
        raise Refused('LEDGER_ASK_MISSING', 'a run needs --ledger-ask <PREREG ask id> registered in the tries ledger first')
    if not ASK_RE.match(ask_id):
        raise Refused('LEDGER_ASK_MALFORMED', repr(ask_id))
    try:
        with open(path) as f:
            rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    except OSError as e:
        raise Refused('LEDGER_UNREADABLE', str(e))
    pre = [r for r in rows if r.get('ask_id') == ask_id and r.get('kind') == 'PREREG']
    if not pre:
        raise Refused('LEDGER_ASK_UNKNOWN', '%s has no PREREG row in %s' % (ask_id, path))
    closed = [r['ask_id'] for r in rows if r.get('ask_id') in (ask_id + '_R', ask_id + '_W')]
    if closed:
        raise Refused('LEDGER_ASK_CLOSED', '%s already has %s: register a new try' % (ask_id, closed))
    row = pre[0]
    if idea is not None and row.get('idea') != idea:
        raise Refused('LEDGER_ASK_MISMATCH', '%s registers idea %r, the run grades %r' % (ask_id, row.get('idea'), idea))
    if first is not None and (row.get('days_from'), row.get('days_to')) != (first, last):
        raise Refused('LEDGER_ASK_MISMATCH', '%s registers days %s..%s, the run asks %s..%s'
                      % (ask_id, row.get('days_from'), row.get('days_to'), first, last))
    if ledger_used(path, ask_id):
        raise Refused('LEDGER_ASK_USED', '%s already admitted a complete run (%s): register a new try'
                      % (ask_id, _claim_path(path, ask_id)))
    return row


def _claim_path(ledger, ask_id):
    return os.path.join(os.path.dirname(os.path.abspath(ledger)), 'I2G_RUN_CLAIMS', ask_id + '.json')


def ledger_used(ledger, ask_id):
    return os.path.exists(_claim_path(ledger, ask_id))


def ledger_claim(ledger, ask_id, record):
    """consume the ask: create I2G_RUN_CLAIMS/<ask>.json beside the ledger, exclusively (a second claim of one ask is refused)"""
    p = _claim_path(ledger, ask_id); os.makedirs(os.path.dirname(p), exist_ok=True)
    try:
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    except FileExistsError:
        raise Refused('LEDGER_ASK_USED', '%s already admitted a complete run (%s)' % (ask_id, p))
    with os.fdopen(fd, 'w') as f:
        json.dump(record, f, sort_keys=True); f.write('\n')
    return p


# ---------------------------------------------------------------------------------------------------- 10 alarm registry
REGISTRY_COLS = ('registry_id', 'card', 'version', 'definition', 'definition_sha16', 'family')


def read_registry(path):
    """ALARM_REGISTRY_V1 -> {registry_id: row}"""
    try:
        with open(path) as f:
            rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    except OSError as e:
        raise Refused('REGISTRY_UNREADABLE', str(e))
    if not rows or not set(REGISTRY_COLS) <= set(rows[0]):
        raise Refused('REGISTRY_FORMAT', path)
    out = {}
    for r in rows:
        if r['registry_id'] in out:
            raise Refused('REGISTRY_FORMAT', '%s: %s twice' % (path, r['registry_id']))
        out[r['registry_id']] = r
    return out


def alarm_check(registry, alarm_id, definition_sha16=None, events_sha16=None, universe=None, events_subset=False):
    """F5: the alarm id must be a registry id; an idea's definition must be the registered one; an event list graded with a universe must
    be that alarm's source list in the universe (same sha16), or be declared a subset of it (events_subset; subgroup() then refuses any
    event the alarm's universe does not hold) -> (registry row, binding)"""
    if alarm_id not in registry:
        raise Refused('ALARM_ID_UNKNOWN', '%r is not a registry id (%s)' % (alarm_id, sorted(registry)[:8]))
    row = registry[alarm_id]
    if definition_sha16 is not None and row['definition_sha16'] != definition_sha16:
        raise Refused('ALARM_DEFINITION_MISMATCH', '%s registers definition %s, the run gives %s' % (alarm_id, row['definition_sha16'],
                                                                                                    definition_sha16))
    binding = 'NO_UNIVERSE'
    if universe is not None:
        src = universe.sources.get(alarm_id)
        if src is None:
            raise Refused('UNIVERSE_ALARM_ABSENT', '%s is not an alarm of the universe %s' % (alarm_id, universe.name))
        if events_sha16 is None:
            binding = 'DEFINITION'
        elif src[1] == events_sha16:
            binding = 'SOURCE_LIST'
        elif events_subset:
            binding = 'DECLARED_SUBSET'
        else:
            raise Refused('ALARM_EVENTS_MISMATCH', 'the event list %s is not the universe source of %s (%s); a slice of it needs --events-subset'
                          % (events_sha16, alarm_id, src[1]))
    return row, binding


def sha16_bytes(b):
    return hashlib.sha256(b).hexdigest()[:16]
