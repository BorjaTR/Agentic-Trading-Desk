"""QUANT b8_roll_v1 (card alarms/B8_ROLL_SPREAD_CARD_V1.md 5b863b48, part 0 PASS WITH 2 by SCOUT, items taken; DRAFT).
B8 ROLL SPREAD SPIKE: Roll's spread of the 3 s bin closes. At minute end m_j = D 00:00 + 60 j (j = 0 .. 1439), the bins with trades and tl
in (m_j - W, m_j] in time order; d_i = ln px_i - ln px_(i-1) over consecutive window bins; c = mean over i >= 1 of (d_i - dbar)(d_(i-1) -
dbar), dbar the mean of d; Roll = 2 sqrt(-c) x 10,000 when c < 0, else 0; valued with at least N bins (W 900 s and N 100; beside W 300 s
and N 40). Edge = the q-th pct (99, beside 99.5) of Roll over the valued minute ends of the history days among the 14 built days before D
(at least 1,000 valued a day, at least 2). FIRE at the first j with Roll > edge after a valued j - 1 with Roll <= edge, more than 15 minute
ends after the coin's last fire (across midnight). Bench side = the 60 s price direction. D2: M1 the mean quoted half spread X1.COST.S01
over the 5 s steps in (m - W, m] above the coin's median X1.COST.S01 of D - 1; M2 the window's range (max hi - min lo over the last close)
above the coin's median window range over D - 1's minute ends. D3 in PROOF: the share of valued minute ends at 0.
Usage: python3 b8_roll_v1.py <lab_days> <lab3 code> <out dir> <first> <last> <last readable> <coin> ...
Writes B8_EVENTS.tsv (S), B8a_EVENTS.tsv (99.5), B8b_EVENTS.tsv (5 min), B8_FIRES.tsv, B8_PROOF.txt."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v4 as OB

HIST, HIST_MIN, DAY_MIN, REFR = 14, 2, 1000, 15
SETTINGS = {'S': (99.0, 900, 100, 'B8_EVENTS.tsv'), 'A': (99.5, 900, 100, 'B8a_EVENTS.tsv'), 'B': (99.0, 300, 40, 'B8b_EVENTS.tsv')}


def roll_one(px):
    """px: closes of the window in time order -> Roll in bp (0 when c >= 0); NaN with fewer than 3 closes"""
    if len(px) < 3:
        return np.nan
    d = np.diff(np.log(np.asarray(px, float))); d = d - d.mean()
    c = float(np.mean(d[1:] * d[:-1]))
    return 2.0 * np.sqrt(-c) * 1e4 if c < 0 else 0.0


def roll_series(tl, px, t, w, nmin):
    """t: minute ends -> Roll (NaN where fewer than nmin bins in (t - w, t])"""
    a = np.searchsorted(tl, t - w, side='right'); b = np.searchsorted(tl, t, side='right')
    out = np.full(len(t), np.nan)
    for j in range(len(t)):
        if b[j] - a[j] >= nmin:
            out[j] = roll_one(px[a[j]:b[j]])
    return out


def edge(hist, q):
    days = [h for h in hist[-HIST:] if np.isfinite(h).sum() >= DAY_MIN]
    if len(days) < HIST_MIN:
        return np.nan
    return float(np.percentile(np.concatenate([h[np.isfinite(h)] for h in days]), q))


def fires(x, e, prev, last):
    if not np.isfinite(e):
        return [], last
    p = np.concatenate([[prev], x[:-1]])
    with np.errstate(invalid='ignore'):
        cand = np.flatnonzero((x > e) & np.isfinite(p) & (p <= e))
    out = []
    for j in cand:
        if last is None or j - last > REFR:
            out.append(int(j)); last = int(j)
    return out, last


def fires_loop(x, e, prev, last):
    out = []
    if not np.isfinite(e):
        return out, last
    for j in range(len(x)):
        p = prev if j == 0 else x[j - 1]
        if x[j] > e and p == p and p <= e and (last is None or j - last > REFR):
            out.append(j); last = j
    return out, last


def wrange(tl, px, hi, lo, t, w):
    a, b = np.searchsorted(tl, t - w, side='right'), np.searchsorted(tl, t, side='right')
    if b <= a:
        return np.nan
    return float((hi[a:b].max() - lo[a:b].min()) / px[b - 1])


def main(root, code_dir, out_dir, first, last_d, last_ok, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); os.makedirs(out_dir, exist_ok=True)
    days = [d for d in OB.day_list(first, last_d, HIST + 1) if d in have and d <= last_ok]
    ev = {k: open(os.path.join(out_dir, v[3]), 'x') for k, v in SETTINGS.items()}
    for f in ev.values():
        f.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, 'B8_FIRES.tsv'), 'x'); fr.write('coin\tt\tday\tj\tsetting\tside\troll\tedge\tm1\tm2\n')
    proof = open(os.path.join(out_dir, 'B8_PROOF.txt'), 'x')
    n = len(coins); hist = {(c, k): [] for c in coins for k in SETTINGS}; st = {(c, k): (np.nan, None) for c in coins for k in SETTINGS}
    prev_day = None; prev_bins = None; prev_s01 = None
    for D in days:
        t0 = OB.day0(D); cons = prev_day is not None and OB.day0(prev_day) + 86400 == t0; write = D >= first
        off, b = LB.read_bins(R, D, coins); cur = []
        for i in range(n):
            s_, e_ = off[i], off[i + 1]; m = b['n'][s_:e_] > 0
            cur.append(tuple(np.asarray(b[f][s_:e_][m], float) / (1e6 if f == 'tl' else 1) for f in ('tl', 'px', 'hi', 'lo')))
        s01 = OB.read_code(R, 'X1.COST.S01', D, coins)                     # D - 1's is M1's reference
        tm = t0 + 60.0 * np.arange(1440)
        n_same = n_diff = 0; nf = {k: 0 for k in SETTINGS}; zero = [0, 0]
        for i, c in enumerate(coins):
            tl, px, hi, lo = cur[i]
            if cons and prev_bins is not None:
                tl, px, hi, lo = (np.concatenate([prev_bins[i][q], cur[i][q]]) for q in range(4))
            rolls = {}
            for k, (qq, w, nmin, _) in SETTINGS.items():
                if (w, nmin) not in rolls:
                    rolls[(w, nmin)] = roll_series(tl, px, tm, w, nmin)
                x = rolls[(w, nmin)]
                if k == 'S':
                    v = x[np.isfinite(x)]; zero[0] += int((v == 0).sum()); zero[1] += len(v)
                e = edge(hist[(c, k)], qq); pr, lk = st[(c, k)]
                if not cons:
                    pr, lk = np.nan, None
                lk = None if lk is None else lk - 1440
                js, lk2 = fires(x, e, pr, lk)
                if write and k == 'S' and i % 4 == 0:
                    same = js == fires_loop(x, e, pr, lk)[0]; n_same += same; n_diff += (not same)
                st[(c, k)] = (x[-1], lk2)
                if write and js:
                    ref1 = np.nan
                    if prev_s01 is not None and cons:
                        pv = prev_s01[i][np.isfinite(prev_s01[i])]; ref1 = float(np.median(pv)) if len(pv) else np.nan
                    ref2 = np.nan
                    if cons and prev_bins is not None:
                        rr = [wrange(tl, px, hi, lo, t0 - 86400 + 60.0 * q, w) for q in range(int(w // 60), 1440)]
                        rr = [r for r in rr if r == r]; ref2 = float(np.median(rr)) if rr else np.nan
                    for j in js:
                        t = t0 + 60 * j; side = OB.move_sign(tl, px, t, 60)
                        m1 = ''
                        if s01 is not None and ref1 == ref1:
                            u1 = j * 12; u0 = max(u1 - int(w // 5) + 1, 0); v = np.asarray(s01[i][u0:u1 + 1], float); v = v[np.isfinite(v)]
                            m1 = str(int(v.mean() > ref1)) if len(v) else ''
                        r2 = wrange(tl, px, hi, lo, t, w); m2 = '' if not (r2 == r2 and ref2 == ref2) else str(int(r2 > ref2))
                        ev[k].write('%s\t%d\t%d\t%.4f\tB8%s\n' % (c, t, side, x[j] / e, '' if k == 'S' else k.lower()))
                        fr.write('%s\t%d\t%s\t%d\t%s\t%d\t%.4f\t%.4f\t%s\t%s\n' % (c, t, D, j, k, side, x[j], e, m1, m2)); nf[k] += 1
                hist[(c, k)].append(x); hist[(c, k)] = hist[(c, k)][-HIST:]
        prev_day, prev_bins, prev_s01 = D, cur, s01
        if write:
            line = 'DAY %s coins %d D1 same %d differ %d fires S %d A %d B %d zero_share %.3f' % (D, n, n_same, n_diff, nf['S'], nf['A'], nf['B'],
                                                                                              zero[0] / zero[1] if zero[1] else float('nan'))
            proof.write(line + '\n'); print(line, flush=True)
    for f in ev.values():
        f.close()
    fr.close(); proof.close()


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5], a[6:])
