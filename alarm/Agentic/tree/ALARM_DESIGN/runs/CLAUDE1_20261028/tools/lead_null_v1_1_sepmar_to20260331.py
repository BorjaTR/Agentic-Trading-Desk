# lead_null_v1_1_to20251231.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): lead_null_v1_to20251231.py 63fe4fbdd283a777 (CLAUDE1 29 Oct)
# with only its paths changed (CLEAN_RELEASE_V1): F, the lab code eo_backend() imports (lab3, labcore, event_outcomes), is
# <Alarm>/01_Detection/tree (settings_v1.alarm_root), found only when the real store reader is first needed (never at import: the
# synthetic tests need no Alarm folder), never the dev tree. TOOL and the output labels stay lead_null_v1_to20251231 (the method;
# test_lead_null_v1_1.py checks them); the code sha16 in every output header names this edition.
# lead_null_v1_to20251231.py (CLAUDE1_20261028, 29 Oct 2026; review round 1 applied 29 Oct 2026). TEST, NOT REVIEWED. Runs on the Mac as
# a runner job (<PYTHON>); in the VM only its synthetic tests run (test_lead_null_v1.py).
# THE QUESTION: per wave, does the alarm's declared LEAN beat the OTHER side by more than its matched random does?
#   Per fire f at horizon h (race OFFER2C_BEFORE_HEAT1C at 15m and 1h = 60M), on complete cases only:
#   e_f = (a_l - r_l) - (a_o - r_o) in points (x100), a = the fire's win, r = its random share (sum_k w_k win_k / sum_k w_k over its draws
#   with a finite outcome); d_w = mean e_f over the wave's complete fires. Pooled lead = mean d_w (each wave once); t = lead / SE with a
#   day-clustered SE (UTC day of the wave's first fire): SE^2 = G/(G-1) * sum_g (sum_{w in g} (d_w - lead))^2 / N^2.
#   R1: months counted (30+ waves with a finite lead at a horizon) at either horizon; a counted month passes when its lead at a counted
#   horizon >= +3; pass when passing >= ceil(2/3 counted) and counted >= 3. R2: R1 and t >= 3 at 15m or 1h. R2s: R1 on one horizon's
#   months and t >= 3 at that same horizon. R3: t >= 3 at 15m or 1h. R4: lead >= +3 and t >= 3 at the same horizon.
#   NULL: each version's pooled real lead per horizon is removed from every d_w, then B = 10,000 sign flips (seed 20261029), one sign per
#   block of 1, 3 or 7 consecutive UTC days (grid from 2025-09-10, both horizons, the block of the wave's first fire). POWER: the same
#   flips plus a planted delta (0, 3, 5, 7 points) after the flip. Shapes: flat (deciding), 1h_only and by_month (reported, never
#   deciding). Every pass rate has a 95 pct Wilson interval. The real (unflipped) lead, t and monthly leads go to REAL_SEALED/ only.
# ASSUMPTIONS (stated, checked where code can):
#   A1 waves = labcore waves 1800 s (any coin). The gate uses all in-window alarm store rows (as alarm_card_v1_3.py); the statistics use
#      the analysis fires (in the window and t <= 2025-12-31 22:59:59 UTC, so a 1 h label never reads 2026; the rest dropped, counted).
#      Checked: WV.waves equals this file's wave_ids on both sets, else WAVE_MISMATCH. A2 win = 1 when value == 1, 0 when finite, else NaN.
#   A3 complete cases per fire: e_f only when a_l, a_o, r_l, r_o are all finite at that horizon; a wave with no complete fire is dropped
#      there; fires and waves dropped are counted per horizon.
#   A4 pairing as make_random_v3.py: own edges skipped, first 3 by draw_index per parent, weight / sum of the kept weights; each draw is
#      matched to the RND list row of the same coin and side with t in [int(cand_t), int(cand_t)+3], nearest first (make_random_v3
#      moves a moment +1 s per collision, so +2 and +3 s happen; +4 s stays unmatched). A candidate outside the window, or at or after
#      2025-12-31 23:00:00 UTC (also after the shift), is dropped after the first-3 selection and counted. MATCH_FAIL (no statistics)
#      when (unmatched + matched without a random store row) > 1 pct of the kept draws.
#   A5 a month counts at a horizon when 30+ of its waves (by first fire) have a finite lead there; see R1, R2s above.
#   A6 comparisons use >= threshold - 1e-9; SE = 0 gives t = +inf (lead > 0), NaN (lead = 0); G < 2 gives t = NaN. The t statistic
#      keeps the day-clustered SE at every block length (the block length changes only the null reference, not the statistic).
#   A7 (corrected) the sign flip needs independent blocks (and A11), not interchangeable waves.
#   A8 the equality gate rebuilds the card's month shares (alarm weight 1/wave size, random weight from RND_<V>_V1_WEIGHTS.tsv, random
#      rows by their own month) for 2509..2512 and compares with SUM_<V>.tsv within 0.15 points; a miss or no key checked = GATE_FAIL.
#      Waves here end at Dec 31: a SUM made on a longer store can differ at the last December wave (a GATE_FAIL then says so).
#   A9 manifest sha16 columns, when given, must equal the files (fires, RND list, weights, edges, SUM, INPUTS_<V>.txt, both
#      RUN_MANIFEST.json); a mismatch = INPUT_CHANGED (no statistics).
#   A10 blocks of 1, 3 and 7 consecutive UTC days are assumed independent of each other at the chosen length; the worst null over the
#      three lengths is reported.
#   A11 a no-skill alarm's per-block lead is symmetric around 0 (after the real lead is removed), so a block's sign is exchangeable.
#   A12 the pooled real lead per horizon is removed from every d_w BEFORE flipping, for the null and for the power (planted delta added
#      after the flip). The real lead itself is written only to REAL_SEALED/.
#   A13 planted shapes: flat (deciding); 1h_only (delta at 1 h, 15m gets 0); by_month (delta x0.5 in odd calendar months Sep, Nov,
#      x1.5 in even months Oct, Dec). The last two are reported, never deciding.
#   A14 random moments are shared across days and parents (a draw can sit on another day and serve several parents), so blocks are not
#      fully independent through the random part; a flip moves each wave's whole d_w (alarm and its random) with its first fire's block.
#   Flips: the same seed for each block length; 95 pct Wilson interval per pass rate (z = 1.95996).
# LIMITATIONS: the null is only as good as A10 and A11 (dependence longer than 7 days, or a skewed per-block lead, is not covered);
#   removing the real lead makes the null "no lead" by construction, and the power is for a planted lead of the stated shapes only;
#   random moments shared across days (A14) weaken block independence; the gate checks the lean side and months 2509..2512 only; R1
#   alone has a high false-pass rate (about 6 to 8 pct on the synthetic iid null), so it never decides alone.
# WINDOW: FIRST..LAST below, hardcoded and in the file name; any fire, random, weight or edge row outside is dropped at load and counted;
# a computed row outside (or a fire or draw at or after 23:00 Dec 31) raises WindowError (the job stops).
#   python3 -B lead_null_v1_to20251231.py --manifest <INPUTS_V1.tsv> --out <new dir> [--only V1,V2] [--flips 10000]
import sys, os, json, math, hashlib, argparse, bisect, collections, datetime as dt
import numpy as np

TOOL = 'lead_null_v1_to20251231'
FIRST, LAST = '20250910', '20260331'
SEED = 20261029
FLIPS = 10000
DELTAS = (0, 3, 5, 7)
BLOCKS = (1, 3, 7)
SHAPES = ('flat', '1h_only', 'by_month')
DECIDING = 'flat'
GAP_S = 1800
KMAX = 3
SHIFT_MAX = 3
MIN_WAVES = 30
LEAD_MIN = 3.0
T_MIN = 3.0
EPS = 1e-9
GATE_TOL = 0.15
MATCH_MAX_PCT = 1.0
Z95 = 1.959963984540054
GATE_MONTHS = ('2509', '2510', '2511', '2512', '2601', '2602', '2603')
DIRS = ('FADE', 'FOLLOW')
HORIZONS = (('15m', 'OFFER2C_BEFORE_HEAT1C_15M', '2c<1c 15m'), ('1h', 'OFFER2C_BEFORE_HEAT1C_60M', '2c<1c 1h'))
COLS = ['%s__%s' % (lab, D) for _, lab, _ in HORIZONS for D in DIRS]
RULES = ('R1', 'R2', 'R2s', 'R3', 'R4')
def _lab_tree():
    """K4 (SCOUT 30 Oct 2026; CLEAN_RELEASE_V1 section 6): the lab code inside the Alarm folder that holds this file, in the dev layout
    (<Alarm>/01_Detection/tree: team/LAB3/code and team/RESEARCH/tools), never the dev tree. The Alarm folder is settings_v1.alarm_root
    (the nearest parent with _tools/settings_v1.py and settings/), read with the package's own settings_v1; outside one: refused."""
    import importlib.util
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s (run it from the Alarm folder)' % os.path.abspath(__file__))
        d = os.path.dirname(d)
    sp = importlib.util.spec_from_file_location('settings_v1', os.path.join(d, '_tools', 'settings_v1.py'))
    sv = importlib.util.module_from_spec(sp); sp.loader.exec_module(sv)
    try:
        f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')
    except sv.Refused as e:
        raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s' % e)
    if not (os.path.isdir(os.path.join(f, 'team', 'LAB3', 'code')) and os.path.isdir(os.path.join(f, 'team', 'RESEARCH', 'tools'))):
        raise SystemExit('NO LAB TREE IN THE ALARM FOLDER: %s (01_Detection/tree with team/LAB3/code and team/RESEARCH/tools)' % f)
    return f
SHA_COLS = collections.OrderedDict([('sha16_fires', 'fires'), ('sha16_rnd_list', 'rnd_list'), ('sha16_rnd_weights', 'rnd_weights'),
                                    ('sha16_edges', 'edges'), ('sha16_sum', 'sum'), ('sha16_inputs', 'inputs'),
                                    ('sha16_manifest_alarm', 'manifest_alarm'), ('sha16_manifest_rnd', 'manifest_rnd')])


def _epoch(day):
    return int(dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())


T_FIRST = _epoch(FIRST); T_END = _epoch(LAST) + 86400   # a row is in the window when T_FIRST <= t < T_END (UTC)
T_CUT = T_END - 3600                                     # analysis fires and draws need t < T_CUT (t <= 2025-12-31 22:59:59 UTC)
GRID0 = T_FIRST // 86400                                 # block grid day 0 = 2025-09-10
N_GRID_DAYS = (T_END - T_FIRST) // 86400


def sha16_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


CODE_SHA16 = sha16_file(os.path.abspath(__file__))


class WindowError(AssertionError):
    pass


class VersionError(Exception):
    def __init__(self, status, msg):
        Exception.__init__(self, '%s: %s' % (status, msg)); self.status = status


# ---------------------------------------------------------------- pure helpers (no EO, no labcore)
def in_window(t, end=T_END):
    t = np.asarray(t, dtype=np.int64); return (t >= T_FIRST) & (t < end)


def utc_day(t):
    t = np.asarray(t, dtype=np.int64).reshape(-1)
    u, inv = np.unique(t // 86400, return_inverse=True)
    lab = np.array([int(dt.datetime.fromtimestamp(int(x) * 86400, dt.timezone.utc).strftime('%Y%m%d')) for x in u], dtype=np.int64)
    return lab[inv.reshape(-1)] if len(t) else np.zeros(0, np.int64)


def utc_month(t):
    return np.array([str(x)[2:6] for x in utc_day(t)], dtype='<U4')


def assert_window(t, what, end=T_END):
    t = np.asarray(t, dtype=np.int64).reshape(-1); bad = ~in_window(t, end)
    if bad.any():
        raise WindowError('OUTSIDE_WINDOW %s: %d computed rows outside %s 00:00:00 - %s UTC (first bad day %d)' % (
            what, int(bad.sum()), FIRST, dt.datetime.fromtimestamp(end - 1, dt.timezone.utc).strftime('%Y%m%d %H:%M:%S'), utc_day(t[bad][:1])[0]))


def wave_ids(t, gap_s=GAP_S):
    """labcore.waves.waves, same rule: a fire more than gap_s after the previous fire (any coin) starts a new wave; ids in time order"""
    t = np.asarray(t, float)
    if len(t) == 0:
        return np.zeros(0, int)
    o = np.argsort(t, kind='mergesort'); ts = t[o]
    wid = np.cumsum(np.r_[1, np.diff(ts) > gap_s]) - 1; out = np.empty(len(t), int); out[o] = wid
    return out


def win(x):
    x = np.asarray(x, float); return np.where(np.isfinite(x), (x == 1).astype(float), np.nan)


def group_nanmean(idx, x, n):
    idx = np.asarray(idx, int); x = np.asarray(x, float); f = np.isfinite(x)
    s = np.bincount(idx[f], weights=x[f], minlength=n); k = np.bincount(idx[f], minlength=n)
    return np.where(k > 0, s / np.maximum(k, 1), np.nan)


def fire_random_share(draw_fire, draw_w, draw_x, n_fires):
    """per fire: sum_k w_k x_k / sum_k w_k over its draws with a finite outcome (NaN when none)"""
    df = np.asarray(draw_fire, int); w = np.asarray(draw_w, float); x = np.asarray(draw_x, float)
    ok = np.isfinite(x) & (w > 0)
    num = np.bincount(df[ok], weights=w[ok] * x[ok], minlength=n_fires); den = np.bincount(df[ok], weights=w[ok], minlength=n_fires)
    return np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)


def fire_leads(al, ao, rl, ro):
    """per fire (a_l - r_l) - (a_o - r_o) in points, NaN unless all four are finite (complete cases)"""
    al, ao, rl, ro = [np.asarray(x, float) for x in (al, ao, rl, ro)]
    ok = np.isfinite(al) & np.isfinite(ao) & np.isfinite(rl) & np.isfinite(ro)
    e = np.full(len(al), np.nan); e[ok] = 100.0 * ((al[ok] - rl[ok]) - (ao[ok] - ro[ok])); return e


def wave_table(t, wave, comp):
    """comp: {horizon: (a_l, a_o, r_l, r_o) per fire} -> per wave first_t, day, day_num (grid day), month, size, d[h] = mean of the
    wave's complete-case fire leads (NaN = dropped), fires_dropped[h]"""
    t = np.asarray(t, dtype=np.int64); wave = np.asarray(wave, int)
    assert_window(t, 'fire', T_CUT)
    n = int(wave.max()) + 1 if len(wave) else 0
    size = np.bincount(wave, minlength=n)
    if (size == 0).any():
        raise ValueError('wave ids are not contiguous')
    first_t = np.full(n, np.iinfo(np.int64).max, np.int64); np.minimum.at(first_t, wave, t)
    assert_window(first_t, 'wave first fire', T_CUT)
    out = {'first_t': first_t, 'day': utc_day(first_t), 'day_num': first_t // 86400 - GRID0, 'month': utc_month(first_t), 'size': size,
           'd': collections.OrderedDict(), 'fire_lead': {}, 'fires_dropped': collections.OrderedDict()}
    for h, xs in comp.items():
        e = fire_leads(*xs); out['fire_lead'][h] = e; out['fires_dropped'][h] = int((~np.isfinite(e)).sum())
        out['d'][h] = group_nanmean(wave, e, n)
    return out


def _onehot(idx, k):
    m = np.zeros((len(idx), k)); m[np.arange(len(idx)), idx] = 1.0; return m


def month_mult(months):
    """by_month shape: x0.5 in odd calendar months (Sep, Nov), x1.5 in even ones (Oct, Dec); NaN for a label that is not YYMM"""
    out = []
    for m in months:
        s = str(m)
        out.append((0.5 if int(s[2:4]) % 2 == 1 else 1.5) if (len(s) == 4 and s.isdigit()) else np.nan)
    return np.array(out, float)


def n_blocks(P, L):
    return -(-P['n_grid'] // int(L))


def prepare(day_num, month, d15, d60):
    """per-wave arrays (grid day of the first fire, month label, d at 15m and 1h) -> day-level structures for the statistics"""
    day_num = np.asarray(day_num, dtype=np.int64).reshape(-1); month = np.asarray(month).reshape(-1)
    if len(day_num) and day_num.min() < 0:
        raise ValueError('a wave before the block grid start %s' % FIRST)
    months = np.unique(month); mi = np.searchsorted(months, month); K = len(months)
    P = {'months': months, 'mult': month_mult(months), 'n_grid': max(N_GRID_DAYS, int(day_num.max()) + 1 if len(day_num) else 0),
         'H': collections.OrderedDict(), 'counted': collections.OrderedDict()}
    fin_any = np.zeros(len(day_num), bool)
    for h, d in (('15m', d15), ('1h', d60)):
        d = np.asarray(d, float).reshape(-1); f = np.isfinite(d); fin_any |= f
        dd, dn, mm = d[f], day_num[f], mi[f]; N = len(dd)
        gday, gi = np.unique(dn, return_inverse=True); gi = gi.reshape(-1); G = len(gday)
        gm = np.zeros(G, int); gm[gi] = mm
        if not np.array_equal(gm[gi], mm):
            raise ValueError('a day lies in two months')
        center = float(dd.mean()) if N else float('nan')
        P['H'][h] = {'d': dd, 'dn': dn, 'mi': mm, 'N': N, 'G': G, 'center': center, 'gday': gday, 'gm': gm,
                     'ng': np.bincount(gi, minlength=G).astype(float), 'ds_raw': np.bincount(gi, weights=dd, minlength=G),
                     'ds_c': np.bincount(gi, weights=dd - center, minlength=G) if N else np.zeros(0),
                     'DM': _onehot(gm, K), 'mcount': np.bincount(mm, minlength=K)}
        P['counted'][h] = P['H'][h]['mcount'] >= MIN_WAVES
    P['mwaves_any'] = np.bincount(mi[fin_any], minlength=K)
    return P


def flip_signs(nblocks, B, seed=SEED):
    """B x nblocks signs: one sign per block of the grid, fixed seed"""
    rng = np.random.default_rng(seed); return np.where(rng.random((B, nblocks)) < 0.5, -1.0, 1.0)


def _per_wave_delta(P, h, delta, shape, month_idx):
    if shape == 'flat':
        return np.full(len(month_idx), float(delta))
    if shape == '1h_only':
        return np.full(len(month_idx), float(delta) if h == '1h' else 0.0)
    if shape == 'by_month':
        m = P['mult'][month_idx]
        if np.isnan(m).any():
            raise ValueError('by_month needs YYMM month labels')
        return float(delta) * m
    raise ValueError('unknown shape %s' % shape)


def delta_waves(P, h, delta, shape):
    return _per_wave_delta(P, h, delta, shape, P['H'][h]['mi'])


def delta_days(P, h, delta, shape):
    Hh = P['H'][h]; return Hh['ng'] * _per_wave_delta(P, h, delta, shape, Hh['gm'])


def flip_matrix(Hh, S, L, delta_w, centered=True):
    """wave level, the definition: B x N = (d_w - real lead if centered) x the sign of the wave's block + planted delta"""
    base = Hh['d'] - Hh['center'] if centered else Hh['d']
    return base[None, :] * np.asarray(S, float)[:, Hh['dn'] // int(L)] + np.asarray(delta_w, float)[None, :]


def horizon_stats(Hh, S, L, dday, centered=True):
    """the same as flip_matrix + mean + day-clustered SE + monthly means, computed exactly on day sums (a day lies in one block)"""
    S = np.asarray(S, float); B = S.shape[0]; K = Hh['DM'].shape[1]; N, G = Hh['N'], Hh['G']
    if N == 0:
        nan = np.full(B, np.nan); return {'lead': nan, 'se': nan.copy(), 't': nan.copy(), 'mlead': np.full((B, K), np.nan)}
    X = S[:, Hh['gday'] // int(L)] * (Hh['ds_c'] if centered else Hh['ds_raw'])[None, :] + np.asarray(dday, float)[None, :]
    lead = X.sum(axis=1) / N
    C = X - Hh['ng'][None, :] * lead[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        se = np.sqrt(G / (G - 1.0) * np.sum(C * C, axis=1)) / N if G >= 2 else np.full(B, np.nan)
        t = lead / se
        mlead = np.where(Hh['mcount'][None, :] > 0, (X @ Hh['DM']) / np.maximum(Hh['mcount'], 1)[None, :], np.nan)
    return {'lead': lead, 'se': se, 't': t, 'mlead': mlead}


def _ge(x, thr):
    x = np.asarray(x, float); return np.where(np.isnan(x), False, x >= thr - EPS)


def _r1(mpass, counted):
    n = int(counted.sum()); return (n >= 3) & (mpass.sum(axis=1) >= (2 * n + 2) // 3)   # ceil(2/3 n) in integers


def rules(P, st):
    a, b = st['15m'], st['1h']; c15, c60 = P['counted']['15m'], P['counted']['1h']
    t15, t60 = _ge(a['t'], T_MIN), _ge(b['t'], T_MIN)
    m15 = _ge(a['mlead'], LEAD_MIN) & c15[None, :]; m60 = _ge(b['mlead'], LEAD_MIN) & c60[None, :]
    cany = c15 | c60; nc = int(cany.sum()); passing = (m15 | m60).sum(axis=1)
    R1 = (nc >= 3) & (passing >= (2 * nc + 2) // 3)
    return {'R1': R1, 'R2': R1 & (t15 | t60), 'R2s': (_r1(m15, c15) & t15) | (_r1(m60, c60) & t60), 'R3': t15 | t60,
            'R4': (_ge(a['lead'], LEAD_MIN) & t15) | (_ge(b['lead'], LEAD_MIN) & t60), 'passing': passing, 'counted': nc,
            'need': (2 * nc + 2) // 3, 'counted_15m': int(c15.sum()), 'counted_1h': int(c60.sum())}


def evaluate(P, S, L, delta=0.0, shape='flat', centered=True):
    st = collections.OrderedDict((h, horizon_stats(Hh, S, L, delta_days(P, h, delta, shape), centered)) for h, Hh in P['H'].items())
    return {'st': st, 'rules': rules(P, st)}


def real_stats(P):
    """the real lead: unflipped, not centred, no delta"""
    return evaluate(P, np.ones((1, P['n_grid'])), 1, 0.0, 'flat', centered=False)


def wilson(k, n, z=Z95):
    if n <= 0:
        return float('nan'), float('nan')
    p = k / float(n); den = 1.0 + z * z / n; c = (p + z * z / (2.0 * n)) / den
    hw = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / den
    return max(0.0, c - hw), min(1.0, c + hw)


def null_power(P, B, seed=SEED, blocks=BLOCKS, deltas=DELTAS, shapes=SHAPES):
    """{(shape, block_days, rule, delta): (passes, rate, lo95, hi95)}: centred d_w, block sign flips, + planted delta after the flip"""
    out = collections.OrderedDict()
    for L in blocks:
        S = flip_signs(n_blocks(P, L), B, seed)
        for shape in shapes:
            for d in deltas:
                ev = evaluate(P, S, L, d, shape, True)
                for r in RULES:
                    k = int(np.sum(ev['rules'][r])); lo, hi = wilson(k, B); out[(shape, L, r, d)] = (k, k / float(B), lo, hi)
    return out


def summarize_rates(rates, blocks=BLOCKS):
    """per rule, deciding shape: worst (max) false pass at delta 0 and lowest power at delta 3, 5, 7 over the block lengths"""
    out = collections.OrderedDict()
    for r in RULES:
        L0 = max(blocks, key=lambda L: rates[(DECIDING, L, r, 0)][1]); x = rates[(DECIDING, L0, r, 0)]
        out[r] = {'null_max': (x[1], x[3], L0)}
        for d in DELTAS[1:]:
            Lp = min(blocks, key=lambda L: rates[(DECIDING, L, r, d)][1]); y = rates[(DECIDING, Lp, r, d)]
            out[r]['pow%d_min' % d] = (y[1], y[2], Lp)
    return out


def scalarize(P, ev):
    out = {'st': collections.OrderedDict(), 'rules': collections.OrderedDict()}; months = [str(m) for m in P['months']]
    for h, Hh in P['H'].items():
        s = ev['st'][h]
        out['st'][h] = {'N': Hh['N'], 'G': Hh['G'], 'lead': float(s['lead'][0]), 'se': float(s['se'][0]), 't': float(s['t'][0]),
                        'mlead': collections.OrderedDict((m, float(s['mlead'][0, k])) for k, m in enumerate(months)),
                        'mwaves': collections.OrderedDict((m, int(Hh['mcount'][k])) for k, m in enumerate(months)),
                        'mcounted': collections.OrderedDict((m, bool(P['counted'][h][k])) for k, m in enumerate(months))}
    r = ev['rules']
    for R in RULES:
        out['rules'][R] = bool(r[R][0])
    out['rules'].update(counted=r['counted'], need=r['need'], passing=int(r['passing'][0]), counted_15m=r['counted_15m'], counted_1h=r['counted_1h'])
    out['months'] = months
    return out


# ---------------------------------------------------------------- equality gate (pure)
def month_share(month, w, x, months):
    month = np.asarray(month); w = np.asarray(w, float); x = np.asarray(x, float); out = collections.OrderedDict()
    for m in months:
        ok = (month == m) & np.isfinite(x) & (w > 0); s = float(np.sum(w[ok]))
        out[m] = 100.0 * float(np.sum(w[ok] * x[ok])) / s if s > 0 else float('nan')
    return out


def _num(v):
    s = str(v).strip().lower()
    return float('nan') if s in ('', 'na', 'nan', 'none') else float(s)


def gate_check(ours, sumv, tol=GATE_TOL):
    """ours {key: pct}; sumv {key: text}. A key missing from SUM is skipped; pass = at least one key checked and no miss"""
    rows = []; n_ok = n_miss = 0
    for k, x in ours.items():
        if k not in sumv:
            rows.append((k, x, None, None, 'SKIP')); continue
        x = float(x); y = _num(sumv[k])
        if x != x and y != y:
            diff, v = 0.0, 'OK'
        elif x != x or y != y:
            diff, v = float('nan'), 'MISS'
        else:
            diff = x - y; v = 'OK' if abs(diff) <= tol + EPS else 'MISS'
        n_ok += v == 'OK'; n_miss += v == 'MISS'; rows.append((k, x, y, diff, v))
    return (n_ok > 0 and n_miss == 0), rows


# ---------------------------------------------------------------- input files (plain python, window drops counted)
def read_table(path):
    with open(path) as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    hdr = lines[0].split('\t'); rows = [l.split('\t') for l in lines[1:]]
    return hdr, [r + [''] * (len(hdr) - len(r)) for r in rows]


def read_manifest(path):
    hdr, rows = read_table(path)
    for k in ('V', 'lean', 'W', 'subj_alarm', 'subj_rnd'):
        if k not in hdr:
            raise SystemExit('MANIFEST_COLUMN %s missing in %s' % (k, path))
    return [collections.OrderedDict(zip(hdr, r)) for r in rows]


def read_sum(path):
    out = {}
    for l in open(path):
        f = l.rstrip('\n').split('\t')
        if len(f) >= 2 and f[0] != 'key':
            out[f[0]] = f[1]
    return out


def read_fires(path):
    hdr, rows = read_table(path); ic, it, isd = hdr.index('coin'), hdr.index('t'), hdr.index('side')
    side = {}; c = collections.Counter(fires_list_rows=len(rows), fires_list_outside=0, fires_list_dup=0)
    for r in rows:
        t = int(float(r[it]))
        if not (T_FIRST <= t < T_END):
            c['fires_list_outside'] += 1; continue
        if (r[ic], t) in side:
            c['fires_list_dup'] += 1
        side[(r[ic], t)] = int(float(r[isd]))
    return side, c


def read_rnd_list(path):
    hdr, rows = read_table(path); ic, it, isd = hdr.index('coin'), hdr.index('t'), hdr.index('side')
    idx = collections.defaultdict(list); seen = set(); c = collections.Counter(rnd_list_rows=len(rows), rnd_list_outside=0, rnd_list_dup=0)
    for r in rows:
        t = int(float(r[it]))
        if not (T_FIRST <= t < T_END):
            c['rnd_list_outside'] += 1; continue
        if (r[ic], t) in seen:
            c['rnd_list_dup'] += 1
        seen.add((r[ic], t)); idx[(r[ic], int(float(r[isd])))].append(t)
    return {k: sorted(v) for k, v in idx.items()}, c


def read_weights(path):
    hdr, rows = read_table(path); ic, it, iw = hdr.index('coin'), hdr.index('t'), hdr.index('weight')
    wt = {}; c = collections.Counter(weights_rows=len(rows), weights_outside=0)
    for r in rows:
        t = int(float(r[it]))
        if not (T_FIRST <= t < T_END):
            c['weights_outside'] += 1; continue
        wt[(r[ic], t)] = float(r[iw])
    return wt, c


def read_edges(path):
    """fid -> [(draw_index, coin, int(cand_t), side, weight)]; a parent outside the window or at/after 23:00 Dec 31 is dropped, own
    edges skipped (all counted)"""
    hdr, rows = read_table(path); ix = {k: hdr.index(k) for k in ('fid', 'coin', 'parent_t', 'cand_t', 'side', 'weight', 'draw_index', 'own')}
    E = collections.defaultdict(list)
    c = collections.Counter(edges_rows=len(rows), edges_parent_outside=0, edges_parent_last_hour=0, edges_own_skipped=0)
    for r in rows:
        pt = int(float(r[ix['parent_t']]))
        if not (T_FIRST <= pt < T_END):
            c['edges_parent_outside'] += 1; continue
        if pt >= T_CUT:
            c['edges_parent_last_hour'] += 1; continue
        if r[ix['own']]:
            c['edges_own_skipped'] += 1; continue
        E[r[ix['fid']]].append((int(float(r[ix['draw_index']])), r[ix['coin']], int(float(r[ix['cand_t']])), int(float(r[ix['side']])), float(r[ix['weight']])))
    return E, c


def pair_draws(coin, t, side, E, rnd_index):
    """per fire (coin, t, side): its first KMAX edges by draw_index, weight / kept sum, matched to the RND list row of the same coin and
    side with t in [ct, ct + SHIFT_MAX], nearest first -> draw_fire, draw_coin, draw_t, draw_w, counts"""
    c = collections.Counter(draws_kept=0, edges_beyond_first3=0, draws_cand_outside=0, draws_cand_last_hour=0, draws_unmatched=0,
                            draws_ambiguous=0, draws_side_differs=0, draws_coin_differs=0, fires_without_edges=0)
    df, dc, dtm, dw = [], [], [], []
    for i, (cn, tt, sd) in enumerate(zip(coin, t, side)):
        rows = E.get('%s_%d' % (cn, int(tt)))
        if not rows:
            c['fires_without_edges'] += 1; continue
        rows = sorted(rows); c['edges_beyond_first3'] += max(0, len(rows) - KMAX); rows = rows[:KMAX]
        tot = sum(r[4] for r in rows)
        for di, ecoin, ct, es, w in rows:
            c['draws_kept'] += 1
            c['draws_side_differs'] += int(es != int(sd)); c['draws_coin_differs'] += int(ecoin != cn)
            if not (T_FIRST <= ct < T_END):
                c['draws_cand_outside'] += 1; continue
            if ct >= T_CUT:
                c['draws_cand_last_hour'] += 1; continue
            lst = rnd_index.get((ecoin, es), [])
            j = bisect.bisect_left(lst, ct); cand = [x for x in lst[j:j + SHIFT_MAX + 1] if x <= ct + SHIFT_MAX]
            if not cand:
                c['draws_unmatched'] += 1; continue
            if cand[0] >= T_CUT:                       # the shifted stored moment crosses 23:00 Dec 31
                c['draws_cand_last_hour'] += 1; continue
            c['draws_ambiguous'] += int(len(cand) > 1)
            df.append(i); dc.append(ecoin); dtm.append(cand[0]); dw.append(w / tot if tot > 0 else 0.0)
    return np.array(df, int), np.array(dc, dtype=object), np.array(dtm, np.int64), np.array(dw, float), c


def _window_rows(o, c, name):
    keep = in_window(o['t']); c[name + '_rows'] = int(len(keep)); c[name + '_outside'] = int((~keep).sum())
    return {k: np.asarray(v)[keep] for k, v in o.items()}


def version_paths(row):
    W, V = row['W'], row['V']; a = '%s/om_%s_v1' % (W, V); r = '%s/om_%sRND_v1' % (W, V)
    return collections.OrderedDict([('fires', '%s/%s_FIRES_V1_LIST.tsv' % (W, V)), ('alarm_root', a), ('rnd_root', r),
                                    ('rnd_list', '%s/RND_%s_V1_LIST.tsv' % (W, V)), ('rnd_weights', '%s/RND_%s_V1_WEIGHTS.tsv' % (W, V)),
                                    ('edges', '%s/gradeL_%s_v1/matches/EDGES.tsv' % (W, V)), ('sum', '%s/SUM_%s.tsv' % (W, V)),
                                    ('inputs', '%s/INPUTS_%s.txt' % (W, V)), ('manifest_alarm', a + '/RUN_MANIFEST.json'), ('manifest_rnd', r + '/RUN_MANIFEST.json')])


# ---------------------------------------------------------------- one version
def run_version(row, read_store, wave_fn, flips, seed=SEED, log=print):
    V = row['V']; lean = row['lean'].strip().upper()
    if lean not in DIRS:
        raise VersionError('BAD_LEAN', '%s lean %r' % (V, row['lean']))
    other = DIRS[1 - DIRS.index(lean)]; p = version_paths(row); c = collections.Counter()
    res = {'V': V, 'lean': lean, 'status': None, 'counts': c, 'paths': p, 'sha16': collections.OrderedDict(), 'sha_check': collections.OrderedDict(),
           'gate': None, 'gate_rows': [], 'manifest_row': row}
    for k, path in p.items():
        if os.path.isfile(path):
            res['sha16'][k] = sha16_file(path)
    changed = []
    for col, k in SHA_COLS.items():
        exp = (row.get(col) or '').strip()
        if exp:
            got = res['sha16'].get(k); res['sha_check'][k] = 'OK' if got == exp else 'CHANGED manifest %s now %s' % (exp, got)
            if got != exp:
                changed.append(k)
    if changed:
        res['status'] = 'INPUT_CHANGED'; log('%s INPUT_CHANGED %s: no statistics' % (V, ','.join(changed))); return res
    side_of, c1 = read_fires(p['fires']); c.update(c1)
    A = _window_rows(read_store(p['alarm_root'], row['subj_alarm'], COLS), c, 'alarm_store')
    Rn = _window_rows(read_store(p['rnd_root'], row['subj_rnd'], COLS), c, 'rnd_store')
    if len(A['t']) == 0:
        raise VersionError('NO_FIRES', '%s: no alarm store row in %s-%s' % (V, FIRST, LAST))
    akeys = list(zip(A['coin'].tolist(), A['t'].tolist()))
    c['alarm_rows_not_in_list'] = sum(1 for k in akeys if k not in side_of); c['list_fires_without_store_row'] = len(set(side_of) - set(akeys))
    # 1) the equality gate, card style: every in-window alarm row, waves on all of them
    wave_g = np.asarray(wave_fn(A['t']), int)
    if not np.array_equal(wave_g, wave_ids(A['t'])):
        raise VersionError('WAVE_MISMATCH', '%s: labcore waves differ from wave_ids (gate set)' % V)
    wg = 1.0 / np.bincount(wave_g)[wave_g]
    wt, cw = read_weights(p['rnd_weights']); c.update(cw)
    w_rnd = np.array([wt.get((cn, int(t)), 0.0) for cn, t in zip(Rn['coin'].tolist(), Rn['t'].tolist())], float)
    am, rmo = utc_month(A['t']), utc_month(Rn['t']); ours = collections.OrderedDict()
    for h, lab, key in HORIZONS:
        sa = month_share(am, wg, win(A['%s__%s' % (lab, lean)]), GATE_MONTHS); sr = month_share(rmo, w_rnd, win(Rn['%s__%s' % (lab, lean)]), GATE_MONTHS)
        for m in GATE_MONTHS:
            ours['%s a %s' % (key, m)] = sa[m]; ours['%s r %s' % (key, m)] = sr[m]
    ok, res['gate_rows'] = gate_check(ours, read_sum(p['sum']) if os.path.isfile(p['sum']) else {})
    res['gate'] = 'PASS' if ok else 'FAIL'; nv = collections.Counter(r[4] for r in res['gate_rows'])
    for k, x, y, d, v in res['gate_rows']:
        if v == 'MISS':
            log('%s GATE MISS %s ours %.2f SUM %.1f' % (V, k, x, y))
    log('%s GATE %s: %d OK, %d SKIP (not in SUM), %d MISS' % (V, res['gate'], nv['OK'], nv['SKIP'], nv['MISS']))
    if not ok:
        res['status'] = 'GATE_FAIL'; log('%s GATE_FAIL: no statistics' % V); return res
    # 2) the analysis fires: t <= 2025-12-31 22:59:59 UTC
    keep = A['t'] < T_CUT; c['fires_last_hour_dropped'] = int((~keep).sum())
    A = {k: v[keep] for k, v in A.items()}; n = len(A['t'])
    if n == 0:
        raise VersionError('NO_FIRES', '%s: no alarm fire before the 23:00 Dec 31 cutoff' % V)
    akeys = list(zip(A['coin'].tolist(), A['t'].tolist())); side = np.array([side_of.get(k, 0) for k in akeys], int)
    wave = np.asarray(wave_fn(A['t']), int)
    if not np.array_equal(wave, wave_ids(A['t'])):
        raise VersionError('WAVE_MISMATCH', '%s: labcore waves differ from wave_ids (analysis set)' % V)
    w_alarm = 1.0 / np.bincount(wave)[wave]
    idx, cl = read_rnd_list(p['rnd_list']); c.update(cl)
    E, ce = read_edges(p['edges']); c.update(ce)
    fids = set('%s_%d' % k for k in akeys); c['edges_parent_not_a_fire'] = sum(len(v) for k, v in E.items() if k not in fids)
    df, dc, dtm, dw, cp = pair_draws(A['coin'], A['t'], side, E, idx); c.update(cp)
    assert_window(dtm, 'random draw', T_CUT)
    ridx = {k: i for i, k in enumerate(zip(Rn['coin'].tolist(), Rn['t'].tolist()))}
    ri = np.array([ridx.get((cn, int(t)), -1) for cn, t in zip(dc, dtm)], int)
    c['draws_used'] = int(len(ri)); c['draws_without_store_row'] = int((ri < 0).sum())
    # 3) the match gate: unmatched draws (no list row within +3 s, or no random store row) over the kept draws
    bad = c['draws_unmatched'] + c['draws_without_store_row']; kept = c['draws_kept']
    res['match_pct'] = 100.0 * bad / kept if kept else 100.0
    if kept == 0 or res['match_pct'] > MATCH_MAX_PCT + EPS:
        res['status'] = 'MATCH_FAIL'; log('%s MATCH_FAIL: %d of %d kept draws unmatched (%.2f pct > %.1f): no statistics' % (V, bad, kept, res['match_pct'], MATCH_MAX_PCT)); return res
    implied = collections.defaultdict(float)
    for i, cn, tm, w in zip(df, dc, dtm, dw):
        implied[(cn, int(tm))] += w * w_alarm[i]
    chk = [k for k in implied if k in wt]
    c['pair_weight_rows_checked'] = len(chk); c['pair_weight_rows_differ'] = sum(1 for k in chk if abs(implied[k] - wt[k]) > 1e-5)
    c['weights_rows_without_draw'] = sum(1 for k in wt if k not in implied); c['draw_rows_without_weight'] = sum(1 for k in implied if k not in wt)
    # 4) per fire complete cases, per wave means, statistics
    comp = collections.OrderedDict()
    for h, lab, key in HORIZONS:
        def rshare(D):
            x = np.full(len(ri), np.nan); okr = ri >= 0; x[okr] = win(Rn['%s__%s' % (lab, D)][ri[okr]]); return fire_random_share(df, dw, x, n)
        comp[h] = (win(A['%s__%s' % (lab, lean)]), win(A['%s__%s' % (lab, other)]), rshare(lean), rshare(other))
    WT = wave_table(A['t'], wave, comp)
    P = prepare(WT['day_num'], WT['month'], WT['d']['15m'], WT['d']['1h'])
    c['fires'] = n; c['waves_all'] = int(len(WT['size'])); c['waves'] = int(P['mwaves_any'].sum())
    for h in P['H']:
        c['fires_dropped_%s' % h] = WT['fires_dropped'][h]; c['waves_%s' % h] = P['H'][h]['N']
        c['waves_dropped_%s' % h] = int(len(WT['size']) - P['H'][h]['N']); c['months_counted_%s' % h] = int(P['counted'][h].sum())
    c['months_counted_any'] = int((P['counted']['15m'] | P['counted']['1h']).sum())
    res['real'] = scalarize(P, real_stats(P))            # SEALED: written to REAL_SEALED/ only
    res['rates'] = null_power(P, flips, seed); res['best'] = summarize_rates(res['rates']); res['status'] = 'OK'
    ms = [str(m) for m in P['months']]
    res['wave_months'] = collections.OrderedDict((m, {'any': int(P['mwaves_any'][k]), '15m': int(P['H']['15m']['mcount'][k]),
                                                      '1h': int(P['H']['1h']['mcount'][k])}) for k, m in enumerate(ms))
    mc = collections.OrderedDict()
    for col, ours_v in [('fires_sepdec', n), ('waves_sepdec', c['waves'])] + [('w' + m, res['wave_months'].get(m, {}).get('any', 0)) for m in GATE_MONTHS]:
        if (row.get(col) or '').strip():
            mc[col] = [row[col], ours_v]
    res['manifest_counts'] = mc
    return res


# ---------------------------------------------------------------- writers and CLI
def _f(x, fmt='%.4f'):
    x = float(x); return 'nan' if x != x else ('inf' if x == np.inf else ('-inf' if x == -np.inf else fmt % x))


def _hdr(kind, V, lean, flips):
    return '# %s %s %s lean %s | window %s-%s (fires and draws to 22:59:59 Dec 31) | seed %d flips %d blocks %s | code %s; TEST, NOT REVIEWED\n' % (
        TOOL, kind, V, lean, FIRST, LAST, SEED, flips, '/'.join(str(L) for L in BLOCKS), CODE_SHA16)


def write_version(out, res, flips):
    V, L = res['V'], res.get('lean', '')
    if res.get('gate_rows'):
        with open(os.path.join(out, 'GATE_%s.tsv' % V), 'x') as f:
            f.write(_hdr('GATE', V, L, flips) + 'key\tours\tsum\tdiff\tverdict\n')
            for k, x, y, d, v in res['gate_rows']:
                f.write('%s\t%s\t%s\t%s\t%s\n' % (k, _f(x, '%.2f'), 'missing' if y is None else _f(y, '%.1f'), 'na' if d is None else _f(d, '%+.2f'), v))
    if res.get('status') != 'OK':
        return
    with open(os.path.join(out, 'RESULTS_%s.tsv' % V), 'x') as f:
        f.write(_hdr('RESULTS (null and power; real lead removed before flipping)', V, L, flips))
        f.write('shape\tdeciding\tblock_days\trule\tdelta\tpasses\tpass_rate\tlo95\thi95\tflips\n')
        for (shape, Lb, r, d), (k, rate, lo, hi) in res['rates'].items():
            f.write('%s\t%s\t%d\t%s\t%d\t%d\t%.4f\t%.4f\t%.4f\t%d\n' % (shape, 'yes' if shape == DECIDING else 'no (reported only)', Lb, r, d, k, rate, lo, hi, flips))
    R = res['real']; ms = R['months']; sd = os.path.join(out, 'REAL_SEALED')
    with open(os.path.join(sd, 'REAL_%s.tsv' % V), 'x') as f:
        f.write(_hdr('REAL SEALED (unflipped, descriptive)', V, L, flips))
        f.write('\t'.join(['horizon', 'waves', 'days', 'lead', 'se', 't'] + [x for m in ms for x in ('lead_%s' % m, 'waves_%s' % m, 'counted_%s' % m)]) + '\n')
        for h, s in R['st'].items():
            f.write('\t'.join([h, str(s['N']), str(s['G']), _f(s['lead']), _f(s['se']), _f(s['t'])]
                              + [x for m in ms for x in (_f(s['mlead'][m]), str(s['mwaves'][m]), 'yes' if s['mcounted'][m] else 'no')]) + '\n')
    with open(os.path.join(sd, 'REAL_RULES_%s.tsv' % V), 'x') as f:
        f.write(_hdr('REAL SEALED rules', V, L, flips) + 'key\tvalue\n')
        for k, v in R['rules'].items():
            f.write('%s\t%s\n' % (k, ('PASS' if v else 'no') if isinstance(v, bool) else v))


SUMMARY_COLS = (['V', 'lean', 'status', 'gate', 'match_fail_pct', 'fires', 'fires_dropped_15m', 'fires_dropped_1h', 'waves', 'waves_15m', 'waves_1h',
                 'months_counted_15m', 'months_counted_1h', 'months_counted_any']
                + [x for m in GATE_MONTHS for x in ('waves_%s' % m, 'waves15_%s' % m, 'waves1h_%s' % m, 'manifest_w%s' % m)]
                + [x for r in RULES for x in (['%s_null_max' % r, '%s_null_max_hi95' % r, '%s_null_max_block' % r]
                                              + [y for d in DELTAS[1:] for y in ('%s_pow%d_min' % (r, d), '%s_pow%d_min_lo95' % (r, d), '%s_pow%d_min_block' % (r, d))])])


def summary_row(res):
    v = collections.OrderedDict((k, '') for k in SUMMARY_COLS); row = res.get('manifest_row') or {}
    v.update(V=res['V'], lean=res.get('lean', ''), status=res.get('status') or '', gate=res.get('gate') or '')
    if res.get('match_pct') is not None:
        v['match_fail_pct'] = '%.3f' % res['match_pct']
    for m in GATE_MONTHS:
        v['manifest_w%s' % m] = (row.get('w' + m) or '').strip()
    if res.get('status') == 'OK':
        c = res['counts']
        for k in ('fires', 'fires_dropped_15m', 'fires_dropped_1h', 'waves', 'waves_15m', 'waves_1h', 'months_counted_15m', 'months_counted_1h', 'months_counted_any'):
            v[k] = c[k]
        for m in GATE_MONTHS:
            wm = res['wave_months'].get(m, {'any': 0, '15m': 0, '1h': 0})
            v['waves_%s' % m] = wm['any']; v['waves15_%s' % m] = wm['15m']; v['waves1h_%s' % m] = wm['1h']
        for r, b in res['best'].items():
            v['%s_null_max' % r] = '%.4f' % b['null_max'][0]; v['%s_null_max_hi95' % r] = '%.4f' % b['null_max'][1]; v['%s_null_max_block' % r] = b['null_max'][2]
            for d in DELTAS[1:]:
                x = b['pow%d_min' % d]
                v['%s_pow%d_min' % (r, d)] = '%.4f' % x[0]; v['%s_pow%d_min_lo95' % (r, d)] = '%.4f' % x[1]; v['%s_pow%d_min_block' % (r, d)] = x[2]
    return v


def _jsonable(x):
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    if isinstance(x, np.ndarray):
        return x.tolist()
    return str(x)


def eo_backend():
    """the real store reader (event_outcomes) and labcore waves, imported only here"""
    F = _lab_tree(); CODE = F + '/team/LAB3/code'   # K4: the lab code inside the Alarm folder (was the dev tree's absolute path)
    sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')
    import event_outcomes as EO
    from labcore import waves as WV

    def read_store(root, subj, cols):
        cat = set()
        for l in open(os.path.join(root, 'OUT_CATALOG_%s.tsv' % subj)):
            if l.startswith('OUT.'):
                cat.add(l.split('\t')[0].split('.', 2)[2])
        miss = [x for x in cols if x not in cat]
        if miss:
            raise VersionError('MISSING_COLUMN', '%s: %s not in OUT_CATALOG_%s.tsv' % (root, ','.join(miss), subj))
        R = EO.read(root, CODE, subj, list(cols), first=FIRST, last=LAST)
        o = {'coin': np.asarray(R[cols[0]]['coin']), 't': np.asarray(R[cols[0]]['as_of_us'], dtype=np.int64) // 10 ** 6}
        for x in cols:
            if not (np.array_equal(np.asarray(R[x]['coin']), o['coin']) and np.array_equal(np.asarray(R[x]['as_of_us'], dtype=np.int64) // 10 ** 6, o['t'])):
                raise VersionError('ROW_ORDER', '%s: row order differs in %s' % (root, x))
            o[x] = np.asarray(R[x]['value'], float)
        return o

    def wave_fn(t):
        return np.asarray(WV.waves(np.asarray(t, float), GAP_S))
    return read_store, wave_fn


def main(argv=None, backend=None):
    ap = argparse.ArgumentParser(prog=TOOL + '.py', description='lean vs other side, against matched random, centred block-flip null (TEST, NOT REVIEWED)')
    ap.add_argument('--manifest', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--only', default=''); ap.add_argument('--flips', type=int, default=FLIPS)
    a = ap.parse_args(argv)
    if a.flips < 1:
        raise SystemExit('FLIPS must be >= 1')
    if os.path.exists(a.out):
        raise SystemExit('OUT_EXISTS %s: refused (give a new directory)' % a.out)
    rows = read_manifest(a.manifest)
    if a.only:
        want = [x.strip() for x in a.only.split(',') if x.strip()]; have = [r['V'] for r in rows]
        miss = [x for x in want if x not in have]
        if miss:
            raise SystemExit('ONLY_UNKNOWN %s not in %s' % (','.join(miss), a.manifest))
        rows = [r for r in rows if r['V'] in want]
    read_store, wave_fn = backend if backend is not None else eo_backend()
    os.makedirs(a.out); os.makedirs(os.path.join(a.out, 'REAL_SEALED'))
    print('# %s | window %s-%s (fires and draws to 22:59:59 Dec 31) | seed %d flips %d blocks %s | code %s | manifest %s; TEST, NOT REVIEWED' % (
        TOOL, FIRST, LAST, SEED, a.flips, '/'.join(str(L) for L in BLOCKS), CODE_SHA16, a.manifest))
    out = []
    for row in rows:
        try:
            res = run_version(row, read_store, wave_fn, a.flips, SEED, log=print)
        except WindowError:
            raise
        except VersionError as e:
            res = {'V': row['V'], 'lean': row.get('lean', ''), 'status': e.status, 'error': str(e), 'counts': {}, 'manifest_row': row}
        except Exception as e:
            res = {'V': row['V'], 'lean': row.get('lean', ''), 'status': 'ERROR', 'error': '%s: %s' % (type(e).__name__, e), 'counts': {}, 'manifest_row': row}
        write_version(a.out, res, a.flips); out.append(res)
        if res['status'] == 'OK':           # null and power only: the real lead stays sealed in REAL_SEALED/
            c, b = res['counts'], res['best']
            print('%s OK lean %s | waves %d (15m %d, 1h %d) | months counted 15m %d, 1h %d | worst null d0 %s | lowest power d3 %s' % (
                res['V'], res['lean'], c['waves'], c['waves_15m'], c['waves_1h'], c['months_counted_15m'], c['months_counted_1h'],
                ' '.join('%s %.4f' % (r, b[r]['null_max'][0]) for r in RULES), ' '.join('%s %.4f' % (r, b[r]['pow3_min'][0]) for r in RULES)))
        else:
            print('%s %s %s' % (res['V'], res['status'], res.get('error', '')))
    with open(os.path.join(a.out, 'SUMMARY.tsv'), 'x') as f:
        f.write('# %s SUMMARY (null and power, waves, gate; no real lead) | window %s-%s | seed %d flips %d blocks %s | code %s; TEST, NOT REVIEWED\n' % (
            TOOL, FIRST, LAST, SEED, a.flips, '/'.join(str(L) for L in BLOCKS), CODE_SHA16))
        f.write('\t'.join(SUMMARY_COLS) + '\n')
        for res in out:
            f.write('\t'.join(str(x) for x in summary_row(res).values()) + '\n')
    rec = collections.OrderedDict([('tool', TOOL), ('code_sha16', CODE_SHA16), ('utc', dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')),
                                   ('argv', sys.argv if argv is None else list(argv)), ('manifest', a.manifest), ('manifest_sha16', sha16_file(a.manifest)),
                                   ('seed', SEED), ('flips', a.flips), ('blocks', list(BLOCKS)), ('shapes', list(SHAPES)), ('deciding_shape', DECIDING),
                                   ('deltas', list(DELTAS)), ('window', [FIRST, LAST]), ('last_moment_utc', '2025-12-31T22:59:59Z'), ('gap_s', GAP_S),
                                   ('kmax', KMAX), ('shift_max', SHIFT_MAX), ('min_waves', MIN_WAVES), ('gate_tol', GATE_TOL), ('match_max_pct', MATCH_MAX_PCT),
                                   ('python', sys.version.split()[0]), ('numpy', np.__version__), ('versions', collections.OrderedDict())])
    for res in out:
        rec['versions'][res['V']] = collections.OrderedDict([(k, res.get(k)) for k in ('status', 'error', 'gate', 'match_pct', 'paths', 'sha16', 'sha_check',
                                                                                      'manifest_counts', 'wave_months')] + [('counts', dict(res.get('counts', {})))])
    with open(os.path.join(a.out, 'RECEIPT.json'), 'x') as f:
        json.dump(rec, f, indent=1, default=_jsonable)
    print('WROTE %s (%d versions: %s)' % (a.out, len(out), ' '.join('%s=%s' % (r['V'], r['status']) for r in out)))
    return 2 if any(r['status'] not in ('OK', 'GATE_FAIL', 'INPUT_CHANGED', 'MATCH_FAIL') for r in out) else 0


if __name__ == '__main__':
    sys.exit(main())
