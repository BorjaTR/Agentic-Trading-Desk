"""SCOUT a01_onset_v2 (= v1 2487519b + QUANT review 17:30:19Z a93bd78c: (1) the 15 min refractory crosses midnight: fires are
found from D-1 (from its first step with a full 6 h bar) and only D's are written; (2) EVENTS side = the PRICE direction (+1 up): longs
forced -> -1, its own column forced = LONGS / SHORTS; (3) outputs never over a file (mode x); (4) refractory = no fire within 180 steps
(15 min) after the last, a fire 181 steps later passes. v1 (20 Oct 2026; the owner 19:12 Berlin: "write a small specification of what each alarm is exactly and then check
that you can find those moments"; "pick one and prove that"). A01 FORCED ONSET exactly as team/RESEARCH/alarms/A01_FORCED_ONSET_SPEC_V1.md.
find() is the vectorised finder; find_loop() is a second computation written apart (plain loops) for proof P2.
Usage (a runner job; lab3 needs pyarrow): python3 a01_onset_v1.py <lab_days root> <lab3 code dir> <out dir> <day> [<day> ...]
Writes A01_FIRES.tsv (coin, t, side, forced, S, mode, day, k, S_k, bar_k, S_prev, bar_prev, cover) and A01_EVENTS.tsv (coin, t, side, S, mode)
for alarm_offer_v1, and A01_PROOF.txt (P2: the two computations compared)."""
import datetime, os, sys
import numpy as np
STEP = 5; W = 12; LOOK = 4320; COVER = 0.9; FLOOR = 20000.0; Q = 99.9; REFR = 180

def sums60(x, clean):
    """x, clean: arrays of 5 s rows -> S (nan where not all 12 rows clean)"""
    xv = np.where(clean, x, 0.0); n = np.concatenate([[0], np.cumsum(clean.astype(int))])
    S = np.full(len(x), np.nan); k = np.arange(W - 1, len(x))
    ok = (n[k + 1] - n[k + 1 - W]) == W
    win = np.lib.stride_tricks.sliding_window_view(xv, W).sum(axis=1)   # each window summed on its own: a running cumsum's
    S[k[ok]] = win[ok]                                                   # rounding put 20,000.0000001 over the floor (test P1)
    return S

def bar_at(S, k):
    """the bar at step k from S[k-LOOK .. k-1]: max(p99.9, FLOOR), or None (cover under 90 pct or not enough history)"""
    if k - LOOK < 0:
        return None, 0.0
    w = S[k - LOOK:k]; v = w[np.isfinite(w)]; cov = len(v) / LOOK
    if cov < COVER:
        return None, cov
    return max(float(np.percentile(v, Q)), FLOOR), cov

def find(x_long, c_long, x_short, c_short, k_from):
    """one coin; arrays over D-1 and D (k_from = D's first step); -> list of (k, side, S_k, bar_k, S_prev, bar_prev, cover)"""
    cand = []
    for side, x, c in ((1, x_long, c_long), (-1, x_short, c_short)):
        S = sums60(np.asarray(x, float), np.asarray(c, bool))
        ks = np.flatnonzero(np.isfinite(S) & (S > FLOOR)); ks = ks[ks >= k_from]
        for k in ks:
            b, cov = bar_at(S, k)
            if b is None or not S[k] > b:
                continue
            bp, _ = bar_at(S, k - 1)
            prev_above = bp is not None and np.isfinite(S[k - 1]) and S[k - 1] > bp
            if not prev_above:
                cand.append((int(k), side, float(S[k]), b, float(S[k - 1]) if np.isfinite(S[k - 1]) else float('nan'), bp, cov))
    out, last = [], None
    for f in sorted(cand, key=lambda r: (r[0], -r[1])):
        if last is None or f[0] - last > REFR:
            out.append(f); last = f[0]
    return out

def find_loop(x_long, c_long, x_short, c_short, k_from):
    """P2: the same rule in plain loops, written apart: -> list of (k, side)"""
    def sums(x, c):
        S = [None] * len(x)
        for k in range(W - 1, len(x)):
            if all(c[j] for j in range(k - W + 1, k + 1)):
                S[k] = sum(float(x[j]) for j in range(k - W + 1, k + 1))
        return S
    def bar(S, k):
        if k < LOOK:
            return None
        v = sorted(s for s in S[k - LOOK:k] if s is not None)
        if len(v) < COVER * LOOK:
            return None
        return max(float(np.percentile(np.array(v), Q)), FLOOR)
    ev = []
    for side, x, c in ((1, x_long, c_long), (-1, x_short, c_short)):
        S = sums(list(x), list(c))
        for k in range(max(k_from, 1), len(S)):
            if S[k] is None or S[k] <= FLOOR:
                continue
            b = bar(S, k)
            if b is None or S[k] <= b:
                continue
            bp = bar(S, k - 1)
            if bp is not None and S[k - 1] is not None and S[k - 1] > bp:
                continue
            ev.append((k, side))
    ev.sort(key=lambda r: (r[0], -r[1])); out = []
    for k, s in ev:
        if not out or k - out[-1][0] > REFR:
            out.append((k, s))
    return out

def prior5(x, clean, k):
    """D2 M1: the coin's forced USD of the fire's side in the 5 min before the fire's 60 s window (rows k-71 .. k-12)"""
    lo = max(0, k - 71); v = np.where(clean[lo:k - 11], x[lo:k - 11], 0.0)
    return float(v.sum())

def last_close(te_us, px, t_s):
    """the last 3 s close with bin end at or before t (s); None when none"""
    i = int(np.searchsorted(te_us, int(t_s * 1e6), side='right')) - 1
    return None if i < 0 else float(px[i])

def ret_bp(te_us, px, a_s, b_s):
    pa, pb = last_close(te_us, px, a_s), last_close(te_us, px, b_s)
    return None if pa is None or pb is None or pa <= 0 else 1e4 * (pb / pa - 1)

def meaning(rows):
    """D2 lines named before the read: M1 >= 70 pct of fires with the 5 min before under 25 pct of the fire's 60 s sum;
    M2 >= 60 pct of fires with the price moving the forced way (longs forced: down) over the 60 s ending at the fire"""
    m1 = [r['prior5'] < 0.25 * r['S_k'] for r in rows]
    m2 = [(r['ret60'] < 0) if r['forced'] == 'LONGS' else (r['ret60'] > 0) for r in rows if r['ret60'] is not None and r['ret60'] != 0]
    m2a = [(r['ret60a'] < 0) if r['forced'] == 'LONGS' else (r['ret60a'] > 0) for r in rows if r['ret60a'] is not None and r['ret60a'] != 0]
    med = lambda v: float(np.median(v)) if v else float('nan')
    return dict(n=len(rows), M1_share=float(np.mean(m1)) if m1 else float('nan'), M1_pass=bool(m1) and np.mean(m1) >= 0.70,
                M1_median_ratio=med([r['prior5'] / r['S_k'] for r in rows]),
                M2_n=len(m2), M2_share=float(np.mean(m2)) if m2 else float('nan'), M2_pass=bool(m2) and np.mean(m2) >= 0.60,
                M2_after_share=float(np.mean(m2a)) if m2a else float('nan'),
                M2_median_forced_way_bp=med([(-r['ret60'] if r['forced'] == 'LONGS' else r['ret60']) for r in rows if r['ret60'] is not None]))

def main(root, lab3_code, out, days):
    sys.path.insert(0, lab3_code)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); os.makedirs(out, exist_ok=True); prof = []
    rows, proof = [], []
    for D in days:
        d0 = datetime.datetime.strptime(D, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)
        P = (d0 - datetime.timedelta(days=1)).strftime('%Y%m%d'); t0 = int(d0.timestamp())
        coins = list(R.index(D, 'PRICE')['coins'])
        arr = {}
        for code in ('A1.S01', 'A1.S02'):
            a = [R.read(code, 'v', [d], coins)[0] for d in (P, D)]
            arr[code] = np.concatenate(a, axis=1); kd = a[0].shape[1]
        n_same = n_diff = 0
        boff, barr = LB.read_bins(R, D, coins)
        for i, c in enumerate(coins):
            te_c = np.asarray(barr['te'][boff[i]:boff[i + 1]], np.int64); px_c = np.asarray(barr['px'][boff[i]:boff[i + 1]], float)
            xl = arr['A1.S01'][i]; xs = arr['A1.S02'][i]; cl = np.isfinite(xl); cs = np.isfinite(xs)
            fs = find(xl, cl, xs, cs, LOOK)              # from D-1's first full bar: the refractory crosses midnight
            for k, forced, Sk, bk, Sp, bp, cov in fs:
                if k < kd:
                    continue
                t = t0 + STEP * (k - kd)
                fz = 'LONGS' if forced == 1 else 'SHORTS'
                p5 = prior5(xl if forced == 1 else xs, cl if forced == 1 else cs, k)
                r60 = ret_bp(te_c, px_c, t - 60, t); r60a = ret_bp(te_c, px_c, t, t + 60)
                rows.append((c, t, -forced, fz, Sk, 'ONSET', D, k - kd, Sk, bk, Sp, bp, cov, p5, r60, r60a))
                prof.append(dict(forced=fz, S_k=Sk, prior5=p5, ret60=r60, ret60a=r60a))
            if i % 4 == 0:                       # P2 on every 4th coin (the loop is slow)
                fl = find_loop(xl, cl, xs, cs, LOOK)
                same = [(f[0], f[1]) for f in fs] == fl
                n_same += same; n_diff += (not same)
                proof.append('%s %s vector %d loop %d %s' % (D, c, len(fs), len(fl), 'SAME' if same else 'DIFFER'))
        proof.append('DAY %s coins %d fires %d P2 same %d differ %d' % (D, len(coins), sum(r[6] == D for r in rows), n_same, n_diff))
        print(proof[-1], flush=True)
    f = lambda v: '' if v is None or (isinstance(v, float) and v != v) else (('%.1f' % v) if isinstance(v, float) else str(v))
    with open(os.path.join(out, 'A01_FIRES.tsv'), 'x') as fh:
        fh.write('coin\tt\tside\tforced\tS\tmode\tday\tk\tS_k\tbar_k\tS_prev\tbar_prev\tcover\tprior5\tret60_bp\tret60_after_bp\n')
        for r in rows: fh.write('\t'.join(f(x) for x in r) + '\n')
    with open(os.path.join(out, 'A01_EVENTS.tsv'), 'x') as fh:
        fh.write('coin\tt\tside\tS\tmode\tforced\n')
        for r in rows: fh.write('%s\t%d\t%d\t%.1f\t%s\t%s\n' % (r[0], r[1], r[2], r[4], r[5], r[3]))
    with open(os.path.join(out, 'A01_PROOF.txt'), 'x') as fh:
        fh.write('\n'.join(proof) + '\n')
    mm = meaning(prof)
    with open(os.path.join(out, 'A01_MEANING.txt'), 'x') as fh:
        fh.write('\n'.join('%s\t%s' % (k, v) for k, v in mm.items()) + '\n')
    print('MEANING', mm)
    print('WROTE', len(rows), 'fires')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
