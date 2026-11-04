# split_v1.py (CLAUDE1_20261028, 28 Oct 2026). TEST, NOT REVIEWED. Reads only a PERFIRE_<V>.tsv written by perfire_v1_to20260131.py
# (no lab data; it reads only what that file holds, whose range the writer enforced). Pure numpy, runs in the VM or on the Mac.
# For a lean and a horizon, it splits the alarm and its matched random by a grouping and prints, per group: waves (alarm), the alarm race
# (one result per wave: weight w), the random race (weight w), the gap, and the other side's gap. Groups: month, day, side (up/down),
# hour block (6 h), wave_size (1, 2-5, 6-20, 21+ coins in the wave), coin. Optional --month to keep one month.
#   python3 -B split_v1.py <PERFIRE.tsv> <LEAN> <H 5m|15m|1h> <GROUP month|day|side|hour6|wsize|coin> [--month YYMM] [--min 20]
import sys, numpy as np
def read(p):
    L = open(p).read().split('\n'); h = L[0].split('\t'); rows = [x.split('\t') for x in L[1:] if x]
    return h, rows
def gkey(r, H, g):
    if g == 'month': return r[H['month']]
    if g == 'day': return r[H['day']]
    if g == 'side': return 'up' if r[H['side']] == '1' else ('down' if r[H['side']] == '-1' else '0')
    if g == 'hour6': return '%02d-%02d' % ((int(r[H['hour']]) // 6) * 6, (int(r[H['hour']]) // 6) * 6 + 6)
    if g == 'coin': return r[H['coin']]
    if g == 'wsize': return None
    raise SystemExit('BAD GROUP ' + g)
def wsize_bucket(n):
    return '1' if n <= 1 else ('2-5' if n <= 5 else ('6-20' if n <= 20 else '21+'))
def race(rows, H, col):
    w = np.array([float(r[H['w']]) for r in rows]); x = np.array([float(r[H[col]]) for r in rows]); ok = np.isfinite(x) & (w > 0)
    return (np.sum(w[ok] * x[ok]) / np.sum(w[ok])) if np.sum(w[ok]) > 0 else np.nan
def split(h, rows, lean, hz, g, month=None):
    H = {k: i for i, k in enumerate(h)}; other = 'FOLLOW' if lean == 'FADE' else 'FADE'
    if month: rows = [r for r in rows if r[H['month']] == month]
    A = [r for r in rows if r[H['kind']] == 'A']; Rr = [r for r in rows if r[H['kind']] == 'R']
    if g == 'wsize':
        # random moments carry no wave: they are matched to fires (3 per fire); a random row takes the bucket of the alarm wave nearest in
        # time on the same coin is not stored, so wsize groups the alarm only and reads random over all rows of the same month set
        ka = {}
        for r in A: ka.setdefault(wsize_bucket(int(r[H['wave_size']])), []).append(r)
        kr = {k: Rr for k in ka}
    else:
        ka, kr = {}, {}
        for r in A: ka.setdefault(gkey(r, H, g), []).append(r)
        for r in Rr: kr.setdefault(gkey(r, H, g), []).append(r)
    out = []
    for k in sorted(ka):
        a = ka[k]; rr = kr.get(k, []); nw = len(set(r[H['wave']] for r in a))
        la, lr = race(a, H, '%s %s' % (lean, hz)), (race(rr, H, '%s %s' % (lean, hz)) if rr else np.nan)
        oa, orr = race(a, H, '%s %s' % (other, hz)), (race(rr, H, '%s %s' % (other, hz)) if rr else np.nan)
        out.append((k, nw, len(a), la, lr, la - lr, oa - orr))
    return out
def main(a):
    if len(a) < 4: raise SystemExit('USAGE split_v1.py PERFIRE LEAN H GROUP [--month YYMM] [--min N]')
    p, lean, hz, g = a[:4]; month = a[a.index('--month') + 1] if '--month' in a else None; mn = int(a[a.index('--min') + 1]) if '--min' in a else 1
    if lean not in ('FADE', 'FOLLOW') or hz not in ('5m', '15m', '1h'): raise SystemExit('BAD LEAN OR H')
    h, rows = read(p); res = split(h, rows, lean, hz, g, month)
    print('%-10s %6s %6s | %6s %6s %6s | %s' % (g, 'waves', 'fires', 'alarm', 'random', 'gap', 'other side gap'))
    for k, nw, nf, la, lr, gp, og in res:
        if nw < mn: continue
        f = lambda x: '   na' if x != x else '%5.1f' % (100 * x)
        print('%-10s %6d %6d | %6s %6s %6s | %s' % (k, nw, nf, f(la), f(lr), '   na' if gp != gp else '%+5.1f' % (100 * gp), '   na' if og != og else '%+5.1f' % (100 * og)))
    return res
if __name__ == '__main__':
    main(sys.argv[1:])
