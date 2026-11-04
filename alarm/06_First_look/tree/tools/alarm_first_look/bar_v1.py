"""bar_v1.py (SCOUT 2 Nov 2026, tools/alarm_first_look). TEST, NOT REVIEWED. why: team/RESEARCH/plans/PLAN_FL12_PERCOIN_BAR_20261102.md.
The per-coin SIZE bar of first look edition 12, for any moment (coin, t), known at the moment. the owner: price moves either way within 1 h by
at least B, B = the larger of 6 costs and the coin's own top 13 percent 1 h move over the previous 14 days. Definitions reused from the
stopped moment tool (team/RESEARCH/PLAYGROUND/tool_tests/moment_tool/code/moment_v1.py hourly_peaks and own_line, moment_run_v1.py's
"known" cost), with three named differences: the line is in percent of price (not cost multiples); a window must have ended strictly
before t (not at or before the clock column); at least LINE_MIN_N = 303 peaks, 90 pct of 336 (not 168, which is 7 days).
 - cost_pct = (FEE_BP + X1.COST.S06 + X1.COST.S08 + GAP_BP) / 100, the cell of t's UTC hour on t's day (each cell is a median over the 14
   days before the day: known before the moment; a Binance 10k walk proxy, never Hyperliquid's cost). Unknown when max(S10, S11) > 0.5, and when S10 or S11 is empty (GPT 10:30:53Z; job 20266523 COST_SHARES: no real cell has that, so no stored table moves).
 - line_pct = np.percentile(peaks, 87) over the coin's hourly peaks: a window starts at each whole hour + 1 minute column, runs 60 columns,
   at least 90 pct valued, peak = the largest |mid / start - 1| in pct on C13.S05.
 - bar_pct = max(K_COST x cost_pct, line_pct). Either unknown: unknown, with its reason in why (NO_COST, EXHAUSTED_COST, NO_LINE, joined by +).
Reads only days first..last (the caller's window); a moment outside it is refused.
  python3 -B bar_v1.py build <lab_days> <lab3 code dir> <first YYYYMMDD> <last YYYYMMDD> <out dir (new)> <list.tsv>=<name> [...]
      one BAR_<name>.tsv.gz per list (coin, t, cost_pct, line_pct, line_n, bar_pct, why; the list's order) and BAR_V1.json last.
Exit 0 done, 2 refused."""
import calendar, csv, gzip, hashlib, json, os, shutil, sys
import numpy as np

VERSION = 'bar_v1'
K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 303, 168
H_MIN, VALUED_MIN = 60, 0.9
FEE_BP, GAP_BP = 9.0, 3.2
EXHAUSTED_MAX = 0.5
T1 = 1777593600                    # 2026-05-01T00:00:00Z: never read at or after (= md_v1.T1)
SETTINGS = {'k_cost': K_COST, 'line_q': LINE_Q, 'line_days': LINE_DAYS, 'line_min_n': LINE_MIN_N, 'h_min': H_MIN, 'valued_min': VALUED_MIN, 'fee_bp': FEE_BP, 'gap_bp': GAP_BP, 'exhausted_max': EXHAUSTED_MAX}
COLS = ('cost_pct', 'line_pct', 'line_n', 'bar_pct', 'why')
HEAD = ('coin', 't') + COLS


class Refused(Exception):
    pass


def s16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def day_start(d):
    return calendar.timegm((int(d[:4]), int(d[4:6]), int(d[6:]), 0, 0, 0))


def day_list(first, last):
    for d in (first, last):
        if len(d) != 8 or not d.isdigit():
            raise Refused('DATE %s' % d)
    a, b = day_start(first), day_start(last)
    if a > b or b >= T1:
        raise Refused('WINDOW %s %s' % (first, last))
    return [''.join(str(np.datetime64(x, 's').astype('datetime64[D]')).split('-')) for x in range(a, b + 1, 86400)]


def hourly_peaks(m, H=H_MIN):
    """m: one coin's minute mids from the first day's midnight (column j in force at t0 + 60 j). -> (end columns, peak in pct): one window
    per whole hour + 1 column, its H later columns, at least VALUED_MIN valued; a missing start or short window gives none"""
    J = np.arange(1, len(m) - H, 60)
    if not len(J):
        return np.zeros(0, int), np.zeros(0)
    J = J[np.isfinite(m[J])]
    W = m[J[:, None] + np.arange(1, H + 1)]; f = np.isfinite(W); ok = f.mean(1) >= VALUED_MIN
    J, W = J[ok], W[ok]
    with np.errstate(invalid='ignore', divide='ignore'):
        v = np.nanmax(np.abs(W / m[J][:, None] - 1), axis=1) * 100.0 if len(J) else np.zeros(0)
    return J + H, v


def line_at(ends, vals, t_min, memo=None):
    """the coin's own line at a moment t_min (real minutes after t0): the LINE_Q percentile of the peaks whose window ended strictly before
    the moment and within LINE_DAYS -> (line_pct or NaN when under LINE_MIN_N, the peaks counted)"""
    a = int(np.searchsorted(ends, t_min - LINE_DAYS * 1440, side='left')); b = int(np.searchsorted(ends, t_min, side='left'))
    n = max(0, b - a)
    if n < LINE_MIN_N:
        return np.nan, n
    if memo is not None and (a, b) in memo:
        return memo[(a, b)], n
    x = float(np.percentile(vals[a:b], LINE_Q))
    if memo is not None:
        memo[(a, b)] = x
    return x, n


def cost_of(s06, s08, s10, s11):
    """one cell -> (cost_pct or NaN, why ('' known, NO_COST, EXHAUSTED_COST))"""
    if not (np.isfinite(s06) and np.isfinite(s08)):
        return np.nan, 'NO_COST'
    if not (np.isfinite(s10) and np.isfinite(s11)):
        return np.nan, 'NO_COST'
    if (np.isfinite(s10) and s10 > EXHAUSTED_MAX) or (np.isfinite(s11) and s11 > EXHAUSTED_MAX):
        return np.nan, 'EXHAUSTED_COST'
    return (FEE_BP + float(s06) + float(s08) + GAP_BP) / 100.0, ''


def bar_of(cost_pct, cwhy, line_pct):
    """-> (bar_pct or NaN, why)"""
    why = [x for x in (cwhy, '' if np.isfinite(line_pct) else 'NO_LINE') if x]
    if why:
        return np.nan, '+'.join(why)
    return max(K_COST * cost_pct, line_pct), ''


def row_fault(cost, line, n, bar, why):
    """one row's text fields -> what is wrong with them, or None: known and unknown must agree with why, and a known bar must be max(K_COST x cost, line)"""
    try:
        c, l, b = [float(x) if x != '' else np.nan for x in (cost, line, bar)]; nn = int(n)
    except ValueError:
        return 'NOT A NUMBER'
    if any(x != '' and not (np.isfinite(float(x)) and float(x) >= 0) for x in (cost, line, bar)):
        return 'NOT A FINITE VALUE'
    w = why.split('+') if why else []
    if not set(w) <= {'NO_COST', 'EXHAUSTED_COST', 'NO_LINE'}:
        return 'WHY %s' % why
    if np.isfinite(c) == bool(set(w) & {'NO_COST', 'EXHAUSTED_COST'}):
        return 'COST AND WHY DISAGREE'
    if np.isfinite(l) == ('NO_LINE' in w) or np.isfinite(l) != (nn >= LINE_MIN_N):
        return 'LINE, COUNT AND WHY DISAGREE'
    if np.isfinite(b) == bool(w):
        return 'BAR AND WHY DISAGREE'
    if np.isfinite(b) and abs(b - max(K_COST * c, l)) > 1e-9 * max(1.0, b):
        return 'BAR %s IS NOT THE LARGER OF %s COSTS AND THE LINE' % (bar, K_COST)
    return None


class LabSource:
    """the lab's one reader (lab3.days, research purpose), only the caller's days"""
    def __init__(self, lab_root, code_dir, days):
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        self.LD = LD; self.R = LD.Days(lab_root, 'research'); self.days = list(days)

    def _coins(self, d, want):
        have = {str(c) for c in self.R.index(d, 'PRICE')['coins']}
        return sorted(have & set(want))

    def minutes(self, d, coins):
        cs = self._coins(d, coins)
        if not cs:
            return {}
        v = self.R.read('C13.S05', 'v', [d], cs)[0].astype(float)
        return {c: v[i] for i, c in enumerate(cs)}

    def cost_cells(self, d, coins):
        """{coin: 4 x 24 array: S06, S08, S10, S11 at each hour's first 5 s column; the column equals the hour's cell, moment_run_v1's read}"""
        cs = self._coins(d, coins); out = {}
        if not cs:
            return out
        try:
            a = [self.R.read('X1.COST.S%02d' % k, 'v', [d], cs)[0].astype(float) for k in (6, 8, 10, 11)]
        except self.LD.NotBuilt:
            return out
        st = a[0].shape[1] // 24
        for i, c in enumerate(cs):
            out[c] = np.array([x[i, ::st] for x in a])
        return out


def compute(src, coin, t, log=None):
    """the bar of every moment (coin[i], t[i]); src: .days, .minutes(day, coins), .cost_cells(day, coins) -> dict of arrays"""
    coin = np.asarray(coin, dtype=object); t = np.asarray(t, np.int64); n = len(t)
    out = {'cost_pct': np.full(n, np.nan), 'line_pct': np.full(n, np.nan), 'line_n': np.zeros(n, int), 'bar_pct': np.full(n, np.nan), 'why': np.full(n, '', dtype=object)}
    if not n:
        return out
    t0 = day_start(src.days[0]); t_end = t0 + 86400 * len(src.days)
    if int(t.min()) < t0 or int(t.max()) >= t_end:
        raise Refused('A MOMENT OUTSIDE THE WINDOW %s %s' % (src.days[0], src.days[-1]))
    coins = sorted(set(coin.tolist())); M = {c: np.full(len(src.days) * 1440, np.nan) for c in coins}
    C = {c: np.full((4, len(src.days) * 24), np.nan) for c in coins}
    for k, d in enumerate(src.days):
        for c, v in src.minutes(d, coins).items():
            M[c][k * 1440:(k + 1) * 1440] = v
        for c, v in src.cost_cells(d, coins).items():
            C[c][:, k * 24:(k + 1) * 24] = v
    for c in coins:
        idx = np.flatnonzero(coin == c); ends, vals = hourly_peaks(M[c]); memo = {}
        for i in idx:
            h = int((t[i] - t0) // 3600); cw = C[c][:, h]
            cp, cwhy = cost_of(*cw); lp, nn = line_at(ends, vals, (int(t[i]) - t0) / 60.0, memo)
            b, why = bar_of(cp, cwhy, lp)
            out['cost_pct'][i], out['line_pct'][i], out['line_n'][i], out['bar_pct'][i], out['why'][i] = cp, lp, nn, b, why
        del M[c]
        if log:
            log('COIN %s moments %d peaks %d' % (c, len(idx), len(ends)))
    return out


def load_list(path):
    with open(path) as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'); rows = list(rd); h = rd.fieldnames or []
    if 'coin' not in h or 't' not in h:
        raise Refused('LIST COLUMNS %s' % path)
    coin = np.array([r['coin'] for r in rows], dtype=object); t = np.array([int(float(r['t'])) for r in rows], np.int64)
    if len(set(zip(coin.tolist(), t.tolist()))) != len(t):
        raise Refused('A (coin, t) TWICE in %s' % path)
    return coin, t


def fmt(x):
    return '' if not np.isfinite(x) else '%.12g' % x


def build(src, out, specs, inputs=None, log=print):
    """specs: [(list path, name)] -> BAR_<name>.tsv.gz per list, BAR_V1.json last, into out (new); the union of moments computed once"""
    if os.path.exists(out) or os.path.exists(out + '.part'):
        raise Refused('OUT EXISTS %s' % out)
    names = [n for _, n in specs]
    if len(set(names)) != len(names) or any(not n or '/' in n for n in names):
        raise Refused('LIST NAMES %s' % names)
    L = [(p, n) + load_list(p) for p, n in specs]; keys = {}
    for _, _, coin, t in L:
        for k in zip(coin.tolist(), t.tolist()):
            keys.setdefault(k, len(keys))
    U = list(keys); uc = np.array([k[0] for k in U], dtype=object); ut = np.array([k[1] for k in U], np.int64)
    V = compute(src, uc, ut, log=log); part = out + '.part'; os.makedirs(part)
    try:
        man = {'version': VERSION, 'code': {'bar_v1.py': s16(os.path.abspath(__file__))}, 'inputs': inputs or {}, 'moments': len(U), 'first': src.days[0], 'last': src.days[-1],
               'settings': SETTINGS, 'lists': {}}
        for p, n, coin, t in L:
            ix = np.array([keys[k] for k in zip(coin.tolist(), t.tolist())], int); fp = os.path.join(part, 'BAR_%s.tsv.gz' % n)
            with gzip.open(fp, 'wt') as f:
                f.write('\t'.join(HEAD) + '\n')
                for j, i in enumerate(ix):
                    f.write('%s\t%d\t%s\t%s\t%d\t%s\t%s\n' % (coin[j], t[j], fmt(V['cost_pct'][i]), fmt(V['line_pct'][i]), V['line_n'][i], fmt(V['bar_pct'][i]), V['why'][i]))
            why = {}
            for w in V['why'][ix].tolist():
                why[w or 'KNOWN'] = why.get(w or 'KNOWN', 0) + 1
            nn = V['line_n'][ix]
            man['lists'][n] = {'list': [os.path.abspath(p), s16(p)], 'rows': len(t), 'out': ['BAR_%s.tsv.gz' % n, s16(fp)], 'why': why,
                               'no_line_with_168_or_more': int(((nn >= LINE_BESIDE_N) & (nn < LINE_MIN_N)).sum())}
        with open(os.path.join(part, 'BAR_V1.json'), 'x') as f:
            json.dump(man, f, indent=1, sort_keys=True)
    except BaseException:
        shutil.rmtree(part, ignore_errors=True); raise
    os.rename(part, out)
    return man


def main(a):
    if len(a) >= 7 and a[0] == 'build':
        specs = []
        for x in a[6:]:
            if '=' not in x:
                raise Refused('LIST SPEC %s (path=name)' % x)
            p, n = x.rsplit('=', 1); specs.append((p, n))
        man = build(LabSource(a[1], a[2], day_list(a[3], a[4])), a[5], specs, inputs={'lab_root': a[1]})
        print('BAR %s: %d moments, %d lists; BAR_V1.json %s' % (a[5], man['moments'], len(man['lists']), s16(os.path.join(a[5], 'BAR_V1.json'))))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED %s' % e)
        sys.exit(2)
