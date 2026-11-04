"""SCOUT a02_climax_v3 (20 Oct 2026; the owner 19:53 and 19:56 Berlin: "a real card ... with proper settings and how to detect it. With
clear no lookahead"; "Prove first that you can detect it properly"). A02 FORCED CLIMAX version 3 exactly as
team/RESEARCH/alarms/A02_FORCED_CLIMAX_CARD_V1.md: inside each A01 episode (a01_onset_v2.find, imported: one definition of the onset),
FIRE at the first 5 s step k with grown(k) (the largest f60 since the onset >= G x f60 at the onset) and quiet(k) (the last Q/5 steps
all clean, after the episode's 15 s peak, each f15 <= D x that peak). One fire per episode; the episode ends 720 steps after the onset or
at the next onset of the same coin and side. find_episode() vectorised-by-run, find_episode_loop() written apart (proof D1).
Usage (a runner job): python3 a02_climax_v3.py <lab_days root> <lab3 code dir> <out dir> <day> [<day> ...]"""
import datetime, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import a01_onset_v2 as A01
STEP = 5; G = 2.0; D = 0.10; QSTEPS = 6; CAP = 720; HOLD = 360

def f15(x, clean):
    """the forced USD of the last 15 s (3 rows), nan unless all 3 clean; known at k"""
    xv = np.where(clean, x, 0.0); n = np.concatenate([[0], np.cumsum(clean.astype(int))])
    out = np.full(len(x), np.nan); k = np.arange(2, len(x))
    ok = (n[k + 1] - n[k - 2]) == 3
    out[k[ok]] = np.lib.stride_tricks.sliding_window_view(xv, 3).sum(axis=1)[ok]
    return out

def find_episode(F15, F60, k0, k_end, g=G, d=D, q=QSTEPS):
    """one episode [k0, k_end): -> (k_fire, peak15, kP) or None; reads only rows k0 .. k at step k"""
    start = F60[k0]
    if not np.isfinite(start) or start <= 0:
        return None
    peak, kP, run, maxf60 = -1.0, -1, 0, -np.inf
    for k in range(k0, k_end):
        v = F15[k]
        if np.isfinite(F60[k]):
            maxf60 = max(maxf60, F60[k])
        if np.isfinite(v) and v >= peak:                       # a new peak (the latest on ties): the quiet run restarts
            peak, kP, run = float(v), k, 0
            continue
        if kP >= 0 and np.isfinite(v) and v <= d * peak:
            run += 1
        else:
            run = 0
        if run >= q and maxf60 >= g * start:
            return k, peak, kP
    return None

def find_episode_loop(F15, F60, k0, k_end, g=G, d=D, q=QSTEPS):
    """D1: the card's words read literally at every step, with no running state"""
    start = F60[k0]
    if not (start == start) or start <= 0:
        return None
    for k in range(k0, k_end):
        vals = [(F15[j], j) for j in range(k0, k + 1) if F15[j] == F15[j]]
        if not vals:
            continue
        peak = max(v for v, _ in vals); kP = max(j for v, j in vals if v == peak)
        grown = max([F60[j] for j in range(k0, k + 1) if F60[j] == F60[j]] or [-1.0]) >= g * start
        last = list(range(k - q + 1, k + 1))
        quiet = last[0] > kP and all(F15[j] == F15[j] and F15[j] <= d * peak for j in last)
        if grown and quiet:
            return k, float(peak), kP
    return None

def climaxes(x, clean, onsets, side):
    """onsets: A01 fires [(k, forced, ...)] of this coin (both sides); -> [(k0, k_fire, peak15, kP, start_f60, max_f60)] for one side"""
    F15 = f15(x, clean); F60 = A01.sums60(x, clean)
    ks = sorted(o[0] for o in onsets if o[1] == side); out = []
    for i, k0 in enumerate(ks):
        k_end = min(k0 + CAP, ks[i + 1] if i + 1 < len(ks) else len(x), len(x))
        r = find_episode(F15, F60, k0, k_end)
        if r:
            out.append((k0, r[0], r[1], r[2], float(F60[k0]), float(np.nanmax(F60[k0:r[0] + 1]))))
    return out, F15, F60

def held(F15, k, peak, n=HOLD):
    """M1 (after the fact, never in the rule): no f15 above the peak in the next n steps; None when the window is cut"""
    if k + n >= len(F15):
        return None
    w = F15[k + 1:k + n + 1]
    return bool(not np.any(w[np.isfinite(w)] > peak))

def main(root, lab3_code, out, days):
    sys.path.insert(0, lab3_code)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); os.makedirs(out, exist_ok=True)
    rows, proof = [], []
    for Dd in days:
        d0 = datetime.datetime.strptime(Dd, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)
        P = (d0 - datetime.timedelta(days=1)).strftime('%Y%m%d'); N = (d0 + datetime.timedelta(days=1)).strftime('%Y%m%d'); t0 = int(d0.timestamp())
        coins = list(R.index(Dd, 'PRICE')['coins'])
        arr = {}
        for code in ('A1.S01', 'A1.S02'):
            a = [R.read(code, 'v', [d], coins)[0] for d in (P, Dd, N)]
            arr[code] = np.concatenate(a, axis=1); kd = a[0].shape[1]; kn = kd + a[1].shape[1]
        px = {}
        for d in (P, Dd, N):
            off, b = LB.read_bins(R, d, coins)
            for i, c in enumerate(coins):
                px.setdefault(c, []).append((np.asarray(b['te'][off[i]:off[i + 1]], np.int64), np.asarray(b['px'][off[i]:off[i + 1]], float)))
        n_same = n_diff = n_on = 0
        for i, c in enumerate(coins):
            xl, xs = arr['A1.S01'][i], arr['A1.S02'][i]; cl, cs = np.isfinite(xl), np.isfinite(xs)
            ons = A01.find(xl[:kn], cl[:kn], xs[:kn], cs[:kn], A01.LOOK)          # onsets known up to D's end (D+1 only for the checks)
            te = np.concatenate([p[0] for p in px[c]]); pp = np.concatenate([p[1] for p in px[c]])
            for forced, x, cc in ((1, xl, cl), (-1, xs, cs)):
                cx, F15, F60 = climaxes(x, cc, ons, forced)
                for k0, k, pk, kP, st, mx in cx:
                    if not (kd <= k < kn):
                        continue
                    t = t0 + STEP * (k - kd); tP = t0 + STEP * (kP - kd); tk0 = t0 + STEP * (k0 - kd)
                    sgn = -1 if forced == 1 else 1                      # the forced push's price direction
                    a_ = A01.ret_bp(te, pp, t, t + 60); b_ = A01.ret_bp(te, pp, tP - 60, tP)
                    trap = k0 + 12; pk_trap = np.nanmax(F15[k0:trap + 1]) if np.isfinite(F15[k0:trap + 1]).any() else np.nan
                    rows.append(dict(coin=c, t=t, side=sgn, forced='LONGS' if forced == 1 else 'SHORTS', day=Dd, k=k - kd, onset_t=tk0, peak_t=tP,
                                     secs_from_onset=STEP * (k - k0), secs_from_peak=STEP * (k - kP), peak15=pk, start_f60=st, max_f60=mx,
                                     held=held(F15, k, pk), held_trap=held(F15, trap, pk_trap) if pk_trap == pk_trap else None,
                                     push_after=None if a_ is None else sgn * a_, push_before_peak=None if b_ is None else sgn * b_))
                n_on += sum(1 for o in ons if o[1] == forced and kd <= o[0] < kn)
                if i % 4 == 0:                                          # D1 on every 4th coin
                    F15l = F15.tolist(); F60l = F60.tolist(); ks = sorted(o[0] for o in ons if o[1] == forced)
                    lv = []
                    for j, k0 in enumerate(ks):
                        k_end = min(k0 + CAP, ks[j + 1] if j + 1 < len(ks) else len(x), len(x))
                        r = find_episode_loop([v if v == v else float('nan') for v in F15l], F60l, k0, k_end)
                        if r: lv.append((k0, r[0]))
                    same = [(a[0], a[1]) for a in cx] == lv; n_same += same; n_diff += (not same)
        proof.append('DAY %s coins %d onsets %d climaxes %d D1 same %d differ %d' % (Dd, len(coins), n_on, sum(r['day'] == Dd for r in rows), n_same, n_diff))
        print(proof[-1], flush=True)
    cols = ['coin', 't', 'side', 'forced', 'day', 'k', 'onset_t', 'peak_t', 'secs_from_onset', 'secs_from_peak', 'peak15', 'start_f60', 'max_f60',
            'held', 'held_trap', 'push_after', 'push_before_peak']
    f = lambda v: '' if v is None or (isinstance(v, float) and v != v) else (('%.2f' % v) if isinstance(v, float) else str(v))
    with open(os.path.join(out, 'A02_FIRES.tsv'), 'x') as fh:
        fh.write('\t'.join(cols) + '\n')
        for r in rows: fh.write('\t'.join(f(r[c]) for c in cols) + '\n')
    with open(os.path.join(out, 'A02_EVENTS.tsv'), 'x') as fh:
        fh.write('coin\tt\tside\tS\tmode\tforced\n')
        for r in rows: fh.write('%s\t%d\t%d\t%.1f\tCLIMAX\t%s\n' % (r['coin'], r['t'], r['side'], r['peak15'], r['forced']))
    m = meaning(rows)
    with open(os.path.join(out, 'A02_PROOF.txt'), 'x') as fh: fh.write('\n'.join(proof) + '\n')
    with open(os.path.join(out, 'A02_MEANING.txt'), 'x') as fh: fh.write('\n'.join('%s\t%s' % kv for kv in m.items()) + '\n')
    print('MEANING', m)

def meaning(rows):
    """the card's D2 lines: M1 held >= 80 pct and above the trap moment's share; M2 no 5 s bucket of secs_from_onset over 10 pct;
    M3 push_after < push_before_peak in >= 65 pct"""
    h = [r['held'] for r in rows if r['held'] is not None]; ht = [r['held_trap'] for r in rows if r['held_trap'] is not None]
    b = {}
    for r in rows: b[r['secs_from_onset']] = b.get(r['secs_from_onset'], 0) + 1
    top = max(b.values()) / len(rows) if rows else float('nan')
    p = [r['push_after'] < r['push_before_peak'] for r in rows if r['push_after'] is not None and r['push_before_peak'] is not None]
    M1 = float(np.mean(h)) if h else float('nan'); M1t = float(np.mean(ht)) if ht else float('nan'); M3 = float(np.mean(p)) if p else float('nan')
    return dict(n=len(rows), M1_held=M1, M1_trap=M1t, M1_pass=bool(h) and M1 >= 0.80 and M1 > M1t, M2_top_bucket=top,
                M2_pass=bool(rows) and top <= 0.10, M3_share=M3, M3_n=len(p), M3_pass=bool(p) and M3 >= 0.65,
                median_secs_from_onset=float(np.median([r['secs_from_onset'] for r in rows])) if rows else float('nan'),
                median_secs_from_peak=float(np.median([r['secs_from_peak'] for r in rows])) if rows else float('nan'))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
