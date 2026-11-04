# conditions_v1.py (CLAUDE1_20261028, 28 Oct 2026). TEST, NOT REVIEWED. Reads only PERFIRE_<V>.tsv files (no lab data and no date range of
# its own; it reads only what the files hold, whose range their writer enforced). Pure numpy, split_v1.py's reader and races.
# The CONDITIONS diagnostic of PROCESS_V5 section 5: how busy each DAY was, and the alarm's result by busy-ness bucket.
#   activity of a day = the matched random race of the ACTIVITY file (normally M) on that day at horizon H, the mean of its FADE and
#   FOLLOW races (how often an ordinary moment paid +2c before -1c either way). OUTCOME-SIDE: a diagnostic, never a trigger input.
#   buckets: quiet / mid / busy by the terciles of day activity over the CUT months only (frozen from seen months).
#   per month and bucket: the alarm's waves, lean gap, other-side gap and direction (lean gap minus other-side gap).
#   python3 -B conditions_v1.py <ACTIVITY PERFIRE> <ALARM PERFIRE> <LEAN> <H> <CUT YYMM,YYMM,...> [--side up|down]
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import split_v1 as S
def day_activity(h, rows, hz):
    H = {k: i for i, k in enumerate(h)}; acc = {}
    for r in rows:
        if r[H['kind']] != 'R': continue
        w = float(r[H['w']]); a, b = float(r[H['FADE %s' % hz]]), float(r[H['FOLLOW %s' % hz]])
        if w <= 0 or a != a or b != b: continue
        s = acc.setdefault(r[H['day']], [0.0, 0.0]); s[0] += w * (a + b) / 2; s[1] += w
    return {d: s[0] / s[1] for d, s in acc.items() if s[1] > 0}
def cuts(act, months):
    v = np.array([x for d, x in act.items() if d[2:6] in months])
    if len(v) < 3: raise SystemExit('TOO FEW CUT DAYS %d' % len(v))
    return float(np.quantile(v, 1 / 3.0)), float(np.quantile(v, 2 / 3.0))
def bucket(x, c):
    return 'quiet' if x <= c[0] else ('mid' if x <= c[1] else 'busy')
def run(ap, alp, lean, hz, cut_months, side=None):
    ha, ra = S.read(ap); act = day_activity(ha, ra, hz); c = cuts(act, cut_months)
    h, rows = S.read(alp); H = {k: i for i, k in enumerate(h)}
    if side: rows = [r for r in rows if r[H['side']] == ('1' if side == 'up' else '-1')]
    out = []
    for m in sorted({r[H['month']] for r in rows}):
        for b in ('quiet', 'mid', 'busy'):
            keep = [r for r in rows if r[H['month']] == m and r[H['day']] in act and bucket(act[r[H['day']]], c) == b]
            res = S.split(h, keep, lean, hz, 'month', m) if keep else []
            if res:
                k, nw, nf, la, lr, gp, og = res[0]; out.append((m, b, nw, gp, og, gp - og))
            else: out.append((m, b, 0, np.nan, np.nan, np.nan))
    days = {}
    for d, x in act.items(): days.setdefault(d[2:6], []).append(bucket(x, c))
    return c, out, {m: (v.count('quiet'), v.count('mid'), v.count('busy')) for m, v in days.items()}
def main(a):
    if len(a) not in (5, 7): raise SystemExit('USAGE conditions_v1.py ACTIVITY ALARM LEAN H CUT_MONTHS [--side up|down]')
    ap, alp, lean, hz, cm = a[:5]; side = a[6] if len(a) == 7 and a[5] == '--side' else None
    c, out, dc = run(ap, alp, lean, hz, cm.split(','), side)
    f = lambda x: '   na' if x != x else '%+5.1f' % (100 * x)
    print('cut points (activity at %s, cut months %s): quiet <= %.1f pct < mid <= %.1f pct < busy' % (hz, cm, 100 * c[0], 100 * c[1]))
    print('month  bucket  days  waves | lean gap  other  direction')
    for m, b, nw, gp, og, dr in out:
        print('%s   %-6s %4d  %5d | %s  %s  %s' % (m, b, dc.get(m, (0, 0, 0))[('quiet', 'mid', 'busy').index(b)], nw, f(gp), f(og), f(dr)))
    return c, out
if __name__ == '__main__':
    main(sys.argv[1:])
