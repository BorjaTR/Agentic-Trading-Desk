"""md_v1.py (SCOUT 30 Oct 2026, tools/money_direction; the owner 30 Oct 07:44, 07:47 and 08:01 Berlin). TEST, NOT REVIEWED.
THE MD TEST (money-direction): does the alarm's lean side get a raw move of a useful size, month after month? Pass rule (the owner 07:47,
"raw move, not money; turning it into money is STRATEGY's job"):
  - unit = wave: the fires of the alarm (any coin), each within 15 min (900 s) of the previous fire; each wave's average counts once;
    a wave belongs to the month and the day of its first fire.
  - trade per fire: the factory entry (taker, first 3 s bar ending at or after the fire + 6 s; event_outcomes_aw1), the lean side,
    a fixed hold H in 15 min, 1 h, 4 h, 1 day; gross = the lean-side return in pct of price (RET_<H>__<lean>), before any cost.
  - H is chosen on the design months (Sep-Dec 2025) only: among the holds that pass every design rule, the largest design per-wave
    gross; when none passes, the largest design per-wave gross (shorter hold on a tie). The forward months (Jan-Apr 2026) are read at
    that same H. May 2026 onward is never read (a time at or after 1 May 2026 is refused).
  - design rules at H: per-wave gross >= 0.5 x median c (c = cost_bp / 100 + 0.032 over the design fires, COSTS_PER_COIN_V1);
    per-wave gross > 0 in at least 3 of the 4 design months; no 2 coins make more than half of the design gross; the best 5 days are at
    most half of it; at least 30 waves in every design month.
  - forward rules at the same H: per-wave gross > 0 in each forward month; at least 30 waves in each.
  - MD PASS = design PASS and forward PASS. No forward fire at all = forward NOT READ (MD not PASS).
  - money after cost is REPORTED, never a pass rule: market (gross - c), waiting (a limit at P0, filled only if WORST_1M > 0;
    gross - (0.031 + cost_bp / 200 + 0.016)), hedged (gross - d x BTC's own return over the same seconds - c - BTC's c; BTC fires out).
  - a fire on a coin without a cost row is left out of every MD number (counted), as STRATEGY's scripts do.
Also reported (the owner 08:01): the best and worst offer after the fire at 1 m to 1 day (largest favourable / adverse excursion, pct and c
units) and the coin's own move before the fire (1, 5, 15, 60, 240 min, from the extreme of the last hour and of the last 4 h).
  python3 -B md_v1.py batch <TARGETS.tsv> <COSTS_PER_COIN_V1.tsv> <out dir (new)> <receipts dir> [<receipts dir> ...]
  python3 -B md_v1.py null <POST_<code>.tsv.gz> <COSTS_PER_COIN_V1.tsv> <seeds> <out.tsv>
"""
import csv, gzip, hashlib, json, os, sys
import numpy as np

VERSION = 'md_v1'
DESIGN = ('202509', '202510', '202511', '202512')
FORWARD = ('202601', '202602', '202603', '202604')
HOLDS = (('15m', 'RET_15M'), ('1h', 'RET_60M'), ('4h', 'RET_240M'), ('1d', 'RET_1440M'))
OFFER_H = (1, 2, 3, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720, 1440)
WAVE_GAP_S = 900
SIZE_X = 0.5
MONTHS_MIN = 3
TOP2_MAX = 0.5
BEST5_MAX = 0.5
WAVES_MIN = 30
GAP_PCT = 0.032
REST_PCT = 0.031
REST_GAP_PCT = 0.016
T1 = 1777593600            # 2026-05-01T00:00:00Z: never read at or after
DAY0 = 1757462400          # 2025-09-10T00:00:00Z: the first day (3-day blocks count from it)
DRAWS = 2000
SEED = 30
PERIODS = tuple((m, (m,)) for m in DESIGN + FORWARD) + (('Sep-Dec', DESIGN), ('Jan-Apr', FORWARD), ('Mar-Apr', ('202603', '202604')))
s16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


class Refused(Exception):
    pass


def load_table(path):
    """a gz table of md_extract_v1.py -> dict: coin (str), t (int64), side (int), every value column as float (NaN when empty)"""
    with gzip.open(path, 'rt') as f:
        rd = csv.reader(f, delimiter='\t'); h = next(rd); rows = list(rd)
    if h[:3] != ['coin', 't', 'side']:
        raise Refused('BAD HEADER %s' % path)
    out = {'coin': np.array([r[0] for r in rows], dtype=object), 't': np.array([int(r[1]) for r in rows], np.int64),
           'side': np.array([int(r[2]) for r in rows], int)}
    if len(rows) and int(out['t'].max()) >= T1:
        raise Refused('MAY ROW in %s' % path)
    for i, c in enumerate(h):
        if i < 3 or c.endswith('__why'):
            continue
        out[c] = np.array([float(r[i]) if r[i] != '' else np.nan for r in rows], float)
    return out


def load_costs(path):
    """COSTS_PER_COIN_V1.tsv -> {coin: cost_bp}"""
    o = {}
    for r in csv.DictReader((l for l in open(path) if not l.startswith('#')), delimiter='\t'):
        try:
            o[r['coin']] = float(r['cost_bp'])
        except (KeyError, ValueError):
            pass
    return o


def months_days(t):
    d = t.astype('datetime64[s]')
    mo = np.array([str(x).replace('-', '') for x in d.astype('datetime64[M]')])
    dy = np.array([str(x).replace('-', '') for x in d.astype('datetime64[D]')])
    return mo, dy


def wave_ids(t):
    """fires each within WAVE_GAP_S of the previous one (any coin) share a wave; ids follow time order"""
    t = np.asarray(t, np.int64)
    if len(t) == 0:
        return np.zeros(0, int)
    o = np.argsort(t, kind='stable'); gap = np.diff(t[o]) > WAVE_GAP_S
    w = np.empty(len(t), int); w[o] = np.concatenate([[0], np.cumsum(gap)])
    return w


def per_wave(x, wid, mask):
    """-> (wave ids, wave means, fires per wave) over the fires in mask with a finite x"""
    ok = mask & np.isfinite(x)
    if not ok.any():
        return np.zeros(0, int), np.zeros(0), np.zeros(0, int)
    u, inv = np.unique(wid[ok], return_inverse=True)
    n = np.bincount(inv); return u, np.bincount(inv, weights=x[ok]) / n, n


class Alarm:
    """one fire table (POST) with its costs, waves and lean; the MD numbers come from here"""

    def __init__(self, post, costs, lean, btc=None, pre60=None, pre240=None):
        if lean not in ('FADE', 'FOLLOW'):
            raise Refused('LEAN %s' % lean)
        self.P, self.lean = post, lean
        t = post['t']; self.n = len(t)
        if self.n and int(t.max()) >= T1:
            raise Refused('MAY FIRE')
        key = list(zip(post['coin'], t.tolist()))
        if len(set(key)) != len(key):
            raise Refused('REPEATED FIRE')
        bp = np.array([costs.get(c, np.nan) for c in post['coin']], float)
        self.bp = bp; self.c = bp / 100 + GAP_PCT; self.c_rt = REST_PCT + bp / 200 + REST_GAP_PCT
        self.usable = np.isfinite(self.c)
        self.d = -post['side'] if lean == 'FADE' else post['side'].copy()
        self.wid = wave_ids(t)
        first = np.full(self.wid.max() + 1 if self.n else 0, np.iinfo(np.int64).max, np.int64)
        np.minimum.at(first, self.wid, t)
        mo, dy = months_days(first); self.wmonth, self.wday = mo[self.wid], dy[self.wid]
        self.wfirst = first[self.wid]
        self.cb = costs.get('BTC', np.nan) / 100 + GAP_PCT
        self.btc = {}
        if btc is not None:
            ix = {int(a): i for i, a in enumerate(btc['t'])}
            j = np.array([ix.get(int(a), -1) for a in t])
            for _, L in HOLDS:
                col = btc[L + '__FOLLOW']
                self.btc[L] = np.where(j >= 0, col[np.maximum(j, 0)], np.nan) if len(col) else np.full(self.n, np.nan)
        self.pre = {}
        for tab, labs in ((pre60, ('RET_45M', 'RET_55M', 'RET_59M', 'RET_60M', 'BEST_60M', 'WORST_60M')),
                          (pre240, ('RET_240M', 'BEST_240M', 'WORST_240M'))):
            if tab is None:
                continue
            ix = {(c, int(a)): i for i, (c, a) in enumerate(zip(tab['coin'], tab['t']))}
            j = np.array([ix.get(k, -1) for k in key], int)
            if len(j) and ((j >= 0) & (tab['side'][np.maximum(j, 0)] != post['side'])).any():
                raise Refused('PRE SIDE DIFFERS')
            for L in labs:
                col = tab[L + '__FOLLOW']
                self.pre[L] = np.where(j >= 0, col[np.maximum(j, 0)], np.nan) if len(col) else np.full(self.n, np.nan)

    def gross(self, L):
        return self.P[L + '__' + self.lean]

    def in_months(self, months):
        return np.isin(self.wmonth, months)

    def wave_stats(self, x, months):
        u, v, n = per_wave(x, self.wid, self.usable & self.in_months(months))
        return len(u), (float(v.mean()) if len(u) else np.nan), v, u

    def median_c(self):
        m = self.usable & self.in_months(DESIGN)
        return float(np.median(self.c[m])) if m.any() else np.nan

    def design(self, g):
        """the design rules at one hold, gross g per fire -> dict"""
        mc = self.median_c(); mon = {m: self.wave_stats(g, (m,))[:2] for m in DESIGN}
        nw, pooled, v, u = self.wave_stats(g, DESIGN)
        ok = self.usable & self.in_months(DESIGN) & np.isfinite(g)
        total = float(v.sum()) if nw else 0.0
        top2 = best5 = np.nan; top_coins = []
        if ok.any():
            uw, inv = np.unique(self.wid[ok], return_inverse=True); nf = np.bincount(inv)
            contrib = g[ok] / nf[inv]
            cu, cinv = np.unique(self.P['coin'][ok].astype(str), return_inverse=True); cs = np.bincount(cinv, weights=contrib)
            o = np.argsort(-cs, kind='stable'); top2 = float(cs[o[:2]].sum()); top_coins = [str(cu[i]) for i in o[:2]]
            wd = self.wday[self._first_index(u)]
            du, dinv = np.unique(wd, return_inverse=True); ds = np.bincount(dinv, weights=v)
            best5 = float(np.sort(ds)[::-1][:5].sum())
        r = {'median_c': mc, 'threshold': SIZE_X * mc, 'waves': nw, 'per_wave_gross': pooled,
             'months': {m: [mon[m][0], mon[m][1]] for m in DESIGN}, 'total': total, 'top2': top2, 'top2_coins': top_coins,
             'best5_days': best5}
        r['top2_share'] = top2 / total if total > 0 else np.nan
        r['best5_share'] = best5 / total if total > 0 else np.nan
        why = []
        if not (np.isfinite(pooled) and np.isfinite(mc) and pooled >= SIZE_X * mc):
            why.append('SIZE')
        if sum(1 for m in DESIGN if mon[m][0] > 0 and mon[m][1] > 0) < MONTHS_MIN:
            why.append('MONTHS')
        if not (total > 0 and top2 <= TOP2_MAX * total):
            why.append('COINS')
        if not (total > 0 and best5 <= BEST5_MAX * total):
            why.append('DAYS')
        if min(mon[m][0] for m in DESIGN) < WAVES_MIN:
            why.append('WAVES')
        r['months_positive'] = sum(1 for m in DESIGN if mon[m][0] > 0 and mon[m][1] > 0)
        r['min_waves'] = min(mon[m][0] for m in DESIGN)
        r['fail'] = why; r['pass'] = not why
        return r

    def _first_index(self, waves):
        """the index of one fire of each wave id in waves (all fires of a wave share its day)"""
        if not hasattr(self, '_fi'):
            fi = np.full(self.wid.max() + 1 if self.n else 0, -1, int)
            fi[self.wid[::-1]] = np.arange(self.n)[::-1]
            self._fi = fi
        return self._fi[waves]

    def forward(self, g):
        if not self.in_months(FORWARD).any():
            return {'state': 'NOT READ', 'months': {}, 'fail': ['NO FORWARD FIRES']}
        mon = {m: self.wave_stats(g, (m,))[:2] for m in FORWARD}
        why = []
        if not all(mon[m][0] > 0 and mon[m][1] > 0 for m in FORWARD):
            why.append('MONTHS')
        if min(mon[m][0] for m in FORWARD) < WAVES_MIN:
            why.append('WAVES')
        return {'state': 'FAIL' if why else 'PASS', 'months': {m: [mon[m][0], mon[m][1]] for m in FORWARD}, 'fail': why}

    def choose(self):
        """H on the design months only"""
        D = {h: self.design(self.gross(L)) for h, L in HOLDS}
        fin = lambda h: D[h]['per_wave_gross'] if np.isfinite(D[h]['per_wave_gross']) else -np.inf
        passing = [h for h, _ in HOLDS if D[h]['pass']]
        pool = passing if passing else [h for h, _ in HOLDS]
        best = pool[0]
        for h in pool[1:]:
            if fin(h) > fin(best):
                best = h
        return best, D, bool(passing)

    def money(self, L, months):
        """reported only: per wave and per fire, gross and money after cost (market, waiting, hedged)"""
        g = self.gross(L); w1 = self.P['WORST_1M__' + self.lean]
        mk = g - self.c
        wt = np.where(np.isfinite(w1) & (w1 > 0), g - self.c_rt, np.nan)
        b = self.btc.get(L)
        if b is None:
            hd = np.full(self.n, np.nan)
        else:
            hd = np.where(self.P['coin'] == 'BTC', np.nan, g - self.d * b - self.c - self.cb)
        m = self.usable & self.in_months(months); out = {}
        for k, x in (('gross', g), ('market', mk), ('waiting', wt), ('hedged', hd)):
            nw, pw, _, _ = self.wave_stats(x, months); okf = m & np.isfinite(x)
            out[k] = {'waves': nw, 'per_wave': pw, 'fires': int(okf.sum()), 'per_fire': float(x[okf].mean()) if okf.any() else np.nan}
        return out

    def boot(self, g, block_days):
        """day-block bootstrap of the design per-wave gross (information only, the owner 07:47 dropped it from the rule)"""
        nw, pooled, v, u = self.wave_stats(g, DESIGN)
        if nw < 2:
            return [np.nan, np.nan]
        ft = self.wfirst[self._first_index(u)]
        blk = (ft - DAY0) // (86400 * block_days)
        bu, binv = np.unique(blk, return_inverse=True); bs = np.bincount(binv, weights=v); bn = np.bincount(binv)
        rng = np.random.default_rng(SEED); k = len(bu)
        pick = rng.integers(0, k, size=(DRAWS, k))
        means = bs[pick].sum(1) / bn[pick].sum(1)
        return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]

    def offers(self, months):
        rows = []
        for h in OFFER_H:
            for kind in ('BEST', 'WORST'):
                x = self.P['%s_%dM__%s' % (kind, h, self.lean)]
                nw, pw, v, _ = self.wave_stats(x, months); _, pwc, vc, _ = self.wave_stats(x / self.c, months)
                rows.append((h, kind, nw, pw, float(np.median(v)) if nw else np.nan, pwc, float(np.median(vc)) if nw else np.nan))
        return rows

    def pre_moves(self):
        """the coin's own move before the fire, side-signed (positive = in the direction of the fire's move), pct"""
        s = self.P['side'].astype(float); P = self.pre; out = {}
        if 'RET_60M' in P:
            q = lambda R: 1 + s * R / 100
            out['move_60m'] = P['RET_60M']
            out['move_15m'] = s * (q(P['RET_60M']) / q(P['RET_45M']) - 1) * 100
            out['move_5m'] = s * (q(P['RET_60M']) / q(P['RET_55M']) - 1) * 100
            out['move_1m'] = s * (q(P['RET_60M']) / q(P['RET_59M']) - 1) * 100
            out['from_extreme_60m'] = s * (q(P['RET_60M']) / (1 - s * P['WORST_60M'] / 100) - 1) * 100
            out['peak_60m'] = P['BEST_60M']
        if 'RET_240M' in P:
            q = lambda R: 1 + s * R / 100
            out['move_240m'] = P['RET_240M']
            out['from_extreme_240m'] = s * (q(P['RET_240M']) / (1 - s * P['WORST_240M'] / 100) - 1) * 100
            out['peak_240m'] = P['BEST_240M']
        return out

    def verdict(self):
        h, D, any_pass = self.choose(); L = dict(HOLDS)[h]; g = self.gross(L)
        F = self.forward(g) if D[h]['pass'] else dict(self.forward(g), note='read at H for information; design FAIL')
        if not D[h]['pass']:
            md = 'FAIL'
        elif F['state'] == 'PASS':
            md = 'PASS'
        elif F['state'] == 'NOT READ':
            md = 'DESIGN PASS, FORWARD NOT READ'
        else:
            md = 'FAIL'
        return {'H': h, 'design_by_H': D, 'design': D[h], 'MD_DESIGN': 'PASS' if D[h]['pass'] else 'FAIL', 'forward': F,
                'MD_FORWARD': F['state'] if D[h]['pass'] else ('NOT READ' if F['state'] == 'NOT READ' else F['state'] + ' (info)'),
                'MD_PASS': md, 'boot_day': self.boot(g, 1), 'boot_3day': self.boot(g, 3)}


def antisym(post, L):
    """share of fires whose FADE and FOLLOW returns are exact opposites (both finite)"""
    a, b = post[L + '__FADE'], post[L + '__FOLLOW']; ok = np.isfinite(a) & np.isfinite(b)
    return int(ok.sum()), int((np.abs(a[ok] + b[ok]) <= 1e-9).sum())


def fmt(x, nd=3):
    return '' if x is None or (isinstance(x, float) and not np.isfinite(x)) else ('%+.*f' % (nd, x) if isinstance(x, float) else str(x))


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else round(float(o), 6)
    if isinstance(o, np.integer):
        return int(o)
    return o


def run_code(code, files, costs, lean, out, ids):
    post = load_table(files['POST'])
    btc = load_table(files['BTC']) if files.get('BTC') else None
    pre60 = load_table(files['PRE60']) if files.get('PRE60') else None
    pre240 = load_table(files['PRE240']) if files.get('PRE240') else None
    A = Alarm(post, costs, lean, btc, pre60, pre240); V = A.verdict()
    res = {'version': VERSION, 'code': code, 'alarm_ids': ids, 'lean': lean, 'inputs': {k: [os.path.basename(p), s16(p)] for k, p in files.items() if p},
           'fires': A.n, 'fires_no_cost': int((~A.usable).sum()), 'coins_no_cost': sorted(set(str(c) for c in post['coin'][~A.usable])),
           'design_fires': int((A.usable & A.in_months(DESIGN)).sum()), 'forward_fires': int((A.usable & A.in_months(FORWARD)).sum()),
           'antisym_RET_60M': antisym(post, 'RET_60M')}
    res.update(V)
    with open(os.path.join(out, 'MD_%s.json' % code), 'x') as f:
        json.dump(clean(res), f, indent=1, sort_keys=True)
    with open(os.path.join(out, 'MD_%s.tsv' % code), 'x') as f:
        f.write('period\tH\tkind\twaves\tper_wave\tfires\tper_fire\n')
        for pn, ms in PERIODS:
            for h, L in HOLDS:
                for k, d in A.money(L, ms).items():
                    f.write('%s\t%s\t%s\t%d\t%s\t%d\t%s\n' % (pn, h, k, d['waves'], fmt(d['per_wave'], 4), d['fires'], fmt(d['per_fire'], 4)))
    with open(os.path.join(out, 'OFFERS_%s.tsv' % code), 'x') as f:
        f.write('period\thorizon_min\tkind\twaves\tper_wave_mean_pct\tper_wave_median_pct\tper_wave_mean_c\tper_wave_median_c\n')
        for pn, ms in (('Sep-Dec', DESIGN), ('Jan-Apr', FORWARD)):
            for h, kind, nw, pw, md, pwc, mdc in A.offers(ms):
                f.write('%s\t%d\t%s\t%d\t%s\t%s\t%s\t%s\n' % (pn, h, kind, nw, fmt(pw, 4), fmt(md, 4), fmt(pwc, 3), fmt(mdc, 3)))
    pm = A.pre_moves()
    with open(os.path.join(out, 'PRE_%s.tsv' % code), 'x') as f:
        f.write('period\tmetric\twaves\tper_wave_mean_pct\tper_wave_median_pct\tper_wave_mean_c\n')
        for pn, ms in (('Sep-Dec', DESIGN), ('Jan-Apr', FORWARD)):
            for k, x in pm.items():
                nw, pw, v, _ = A.wave_stats(x, ms); _, pwc, _, _ = A.wave_stats(x / A.c, ms)
                f.write('%s\t%s\t%d\t%s\t%s\t%s\n' % (pn, k, nw, fmt(pw, 4), fmt(float(np.median(v)) if nw else np.nan, 4), fmt(pwc, 3)))
    return res, A


def batch(targets, costs_path, out, *rdirs):
    if os.path.exists(out):
        raise Refused('OUT EXISTS %s' % out)
    T = [r for r in csv.DictReader(open(targets), delimiter='\t')]
    costs = load_costs(costs_path)
    found = {}
    for d in rdirs:
        for fn in os.listdir(d):
            if fn.endswith('.tsv.gz'):
                k, c = fn[:-7].split('_', 1)
                if (k, c) in found:
                    raise Refused('TWO FILES FOR %s %s' % (k, c))
                found[(k, c)] = os.path.join(d, fn)
    os.makedirs(out)
    codes = {}
    for r in T:
        codes.setdefault(r['code'], []).append(r)
    rows = []
    for code, rs in sorted(codes.items()):
        leans = set(r['lean'] for r in rs)
        if len(leans) != 1:
            raise Refused('LEANS DIFFER %s' % code)
        files = {'POST': found.get(('POST', code)), 'PRE60': found.get(('PRE60', code)), 'PRE240': found.get(('PRE240', code)),
                 'BTC': found.get(('POST', 'BTCREF'))}
        if not files['POST']:
            rows.append((code, rs, None)); continue
        res, A = run_code(code, files, costs, leans.pop(), out, [r['alarm_id'] for r in rs])
        rows.append((code, rs, res))
    cols = ['alarm_id', 'code', 'V', 'kind', 'state', 'lean', 'MD_H', 'MD_PASS', 'MD_DESIGN', 'MD_FORWARD', 'design_fail', 'forward_fail',
            'median_c', 'threshold', 'design_per_wave_gross', 'design_months_positive', 'design_min_waves', 'top2_share', 'top2_coins',
            'best5_share', 'boot_day', 'boot_3day'] + ['gross_%s' % m for m in DESIGN + FORWARD] + ['waves_%s' % m for m in DESIGN + FORWARD] + \
           ['gross_by_H_SepDec', 'fires', 'fires_no_cost']
    with open(os.path.join(out, 'MD_SUMMARY.tsv'), 'x') as f:
        f.write('\t'.join(cols) + '\n')
        for code, rs, res in rows:
            for r in rs:
                if res is None:
                    f.write('\t'.join([r['alarm_id'], code, r['V'], r['kind_row'], r['state'], r['lean'], '', 'NOT RUN'] + [''] * (len(cols) - 8)) + '\n')
                    continue
                D, F = res['design'], res['forward']; mon = dict(D['months']); mon.update(F.get('months', {}))
                vals = [r['alarm_id'], code, r['V'], r['kind_row'], r['state'], r['lean'], res['H'], res['MD_PASS'], res['MD_DESIGN'],
                        res['MD_FORWARD'], ','.join(D['fail']) or '-', ','.join(F.get('fail', [])) or '-', fmt(D['median_c'], 4),
                        fmt(D['threshold'], 4), fmt(D['per_wave_gross'], 4), str(D['months_positive']), str(D['min_waves']),
                        fmt(D['top2_share'], 2), ','.join(D['top2_coins']), fmt(D['best5_share'], 2),
                        '%s:%s' % (fmt(res['boot_day'][0], 3), fmt(res['boot_day'][1], 3)),
                        '%s:%s' % (fmt(res['boot_3day'][0], 3), fmt(res['boot_3day'][1], 3))]
                vals += [fmt(mon[m][1], 4) if m in mon else '' for m in DESIGN + FORWARD]
                vals += [str(mon[m][0]) if m in mon else '' for m in DESIGN + FORWARD]
                vals += [' '.join('%s:%s' % (h, fmt(res['design_by_H'][h]['per_wave_gross'], 3)) for h, _ in HOLDS), str(res['fires']), str(res['fires_no_cost'])]
                f.write('\t'.join(vals) + '\n')
    print('MD_SUMMARY %s (%d codes)' % (s16(os.path.join(out, 'MD_SUMMARY.tsv')), len(rows)))


def null(post_path, costs_path, seeds, outp):
    """random-side controls on one list's moments: a fair coin per fire picks the side (lean FADE); the design rules and the H rule as
    for an alarm; the share of seeds that pass the design half is the design false-pass rate at those moments"""
    if os.path.exists(outp):
        raise Refused('OUT EXISTS %s' % outp)
    post = load_table(post_path); costs = load_costs(costs_path)
    rl = {}
    for _, L in HOLDS:   # the long-side return: FOLLOW of a +1 fire, FADE of a -1 fire
        rl[L] = np.where(post['side'] == 1, post[L + '__FOLLOW'], post[L + '__FADE'])
    rows = []
    for s in range(int(seeds)):
        rng = np.random.default_rng(1000 + s); side = rng.choice(np.array([-1, 1]), size=len(post['t']))
        P = {'coin': post['coin'], 't': post['t'], 'side': side, 'WORST_1M__FADE': post['WORST_1M__FADE'], 'WORST_1M__FOLLOW': post['WORST_1M__FOLLOW']}
        for _, L in HOLDS:
            P[L + '__FADE'] = -side * rl[L]; P[L + '__FOLLOW'] = side * rl[L]
        A = Alarm(P, costs, 'FADE'); h, D, any_pass = A.choose()
        rows.append([s, h, int(D[h]['pass'])] + [int(D[x]['pass']) for x, _ in HOLDS] + [D[x]['per_wave_gross'] for x, _ in HOLDS])
    with open(outp, 'x') as f:
        f.write('seed\tH\tdesign_pass_at_H\t' + '\t'.join('pass_%s' % h for h, _ in HOLDS) + '\t' + '\t'.join('gross_%s' % h for h, _ in HOLDS) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) if not isinstance(x, float) else fmt(x, 4) for x in r) + '\n')
    n = len(rows); k = sum(r[2] for r in rows)
    print('null seeds %d: design pass under the H rule %d (%.1f pct); by hold %s' % (n, k, 100.0 * k / max(n, 1),
          ' '.join('%s %d' % (h, sum(r[3 + i] for r in rows)) for i, (h, _) in enumerate(HOLDS))))


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'batch':
            batch(*sys.argv[2:])
        elif sys.argv[1] == 'null':
            null(*sys.argv[2:6])
        else:
            raise Refused('USAGE')
    except Refused as e:
        print('REFUSED %s' % e); sys.exit(2)
