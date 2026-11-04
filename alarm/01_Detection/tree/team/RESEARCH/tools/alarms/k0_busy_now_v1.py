"""QUANT k0_busy_now_v1 (research desk, 20 Oct 2026; DRAFT; reviewer and rebuilder SCOUT). THE CONTROL K0 BUSY RIGHT NOW, card
alarms/K0_BUSY_NOW_CONTROL_CARD_V1.md e94f9227 (part 0 PASS, SCOUT 19:46:32Z): x(k) at the 5 s step t = D 00:00 + 5 k is the coin's price
range over the last 60 s (our 3 s bins with trades whose last trade time is in (t - 60, t]: highest high minus lowest low) over the last
price at or before t - 60 s, in bp; MISSING when no bin is in the window or no price is at or before t - 60. The own-band onset of
alarms/ONSET_RULE_QUANT_V1.txt 6851e4e6 (helpers imported from onset_band_v4 af9b49e6, never re-written): edge(D) at level q = the q-th
percentile of x over the coin's history days among the 14 built days before D (at least 70 pct of the steps clean, at least 2); FIRE at the
first step past the edge after a clean step not past it, more than 180 steps after the coin's last fire, across midnight (from D - 1 on).
Side = the price direction over the 60 s ending at t (D - 1's last bin allowed, as N5). Five levels, read in one pass (card s3).
D2 after the fact, never in the rule: M1 |C1.S10| at the minute end at or after t above the coin's 90th percentile of |C1.S10| over D - 1;
M2 the 60 s range ending at t + 30 above the coin's median 60 s range of D - 1 (cut when t + 30 is past what was read). ticks = the fire's
range in price steps (the step: the smallest gap between distinct prices of D - 1 and D). Usage (runner job):
python3 k0_busy_now_v1.py <lab_days> <lab3 code dir> <out dir> <first day> <last day> <last readable day> <coin> ...
Writes K0_<q>_EVENTS.tsv (coin t side S mode: the desk bench's input, one a level), K0_FIRES.tsv (every level, with D2), K0_PROOF.txt."""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v4 as OB

LEVELS = (99.0, 99.5, 99.8, 99.9, 99.95)
STEPS, CLOCK, W, REFR = 17280, 5, 60.0, 180
M2_LAG = 30.0


def range_series(tl, px, hi, lo, t0, steps=STEPS, clock=CLOCK, w=W):
    """(steps,) x in bp from bins sorted by tl (seconds); the window (t - w, t] by last trade time; NaN when missing"""
    x = np.full(steps, np.nan)
    if len(tl) == 0:
        return x
    t = t0 + clock * np.arange(steps, dtype=float)
    a = np.searchsorted(tl, t - w, 'right'); b = np.searchsorted(tl, t, 'right'); n = b - a
    mx = np.full(steps, -np.inf); mn = np.full(steps, np.inf); last = len(hi) - 1
    for j in range(int(n.max()) if n.max() > 0 else 0):
        idx = a + j; ok = idx < b; ii = np.minimum(idx, last)
        mx = np.where(ok, np.maximum(mx, hi[ii]), mx); mn = np.where(ok, np.minimum(mn, lo[ii]), mn)
    p0 = np.where(a >= 1, px[np.maximum(a - 1, 0)], np.nan)
    good = (n > 0) & np.isfinite(p0) & (p0 > 0)
    x[good] = (mx[good] - mn[good]) / p0[good] * 1e4
    return x


def level_edges(hist, levels=LEVELS):
    """{q: (coins,) edge} from the history arrays (oldest first); None when under 2 days were read (OB.edges' rule)"""
    out = {}
    for q in levels:
        e = OB.edges(hist, q, None)
        if e is None:
            return None
        out[q] = e
    return out


def coin_day_fires(x, prev_last, edge, last_k):
    """fire steps of one coin-day at one level; last_k = the coin's last fire in steps from D 00:00 (negative: D - 1), None = none"""
    return OB.fires_vec(x, prev_last, edge, 'top', last_k, REFR)


def coin_day_fires_loop(x, prev_last, edge, last_k):
    return OB.fires_loop(x, prev_last, edge, 'top', last_k, REFR)


def m1_ref(prev_row):
    v = np.abs(np.asarray(prev_row, float)); v = v[np.isfinite(v)]
    return float(np.percentile(v, 90)) if len(v) else float('nan')


def m1(cur_row, next_row, t0, t, ref):
    """1 / 0 / None: |C1.S10| at the minute end at or after t (column k is the minute ending at t0 + 60 k) above ref"""
    if not ref == ref:
        return None
    c = int(math.ceil((t - t0) / 60.0 - 1e-9))
    if c < len(cur_row):
        v = cur_row[c]
    elif next_row is not None and c - len(cur_row) < len(next_row):
        v = next_row[c - len(cur_row)]
    else:
        return None
    return None if not np.isfinite(v) else int(abs(float(v)) > ref)


def m2(tl, px, hi, lo, t, ref, read_end):
    """1 / 0 / None: the 60 s range ending at t + 30 above ref; None when t + 30 is past what was read or ref is missing"""
    if t + M2_LAG > read_end or not ref == ref:
        return None
    r = OB.range_bp(tl, px, hi, lo, t + M2_LAG)
    return None if not r == r else int(r > ref)


def tick(px):
    u = np.unique(np.asarray(px, float)[np.isfinite(px)])
    d = np.diff(u)
    return float(d.min()) if len(d) else float('nan')


def main(root, code_dir, out_dir, first, last, last_ok, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); os.makedirs(out_dir, exist_ok=True)
    days = [d for d in OB.day_list(first, last, OB.HIST_MAX + 1) if d in have and d <= last_ok]
    cache = {}

    def coin_bins(d):
        if d not in cache:
            if d not in have or d > last_ok:
                cache[d] = None
            else:
                off, b = LB.read_bins(R, d, coins); per = {}
                for i, c in enumerate(coins):
                    s, e = off[i], off[i + 1]; m = b['n'][s:e] > 0
                    per[c] = (b['tl'][s:e][m] / 1e6, np.asarray(b['px'][s:e][m], float), np.asarray(b['hi'][s:e][m], float),
                              np.asarray(b['lo'][s:e][m], float))
                cache[d] = per
            for k in [k for k in cache if k < OB.shift(d, -2)]:
                del cache[k]
        return cache[d]

    hist = []; prev_x = np.full(len(coins), np.nan); prev_day = None; prev_c1 = None
    last_t = {(c, q): None for c in coins for q in LEVELS}
    ev = {q: open(os.path.join(out_dir, 'K0_%s_EVENTS.tsv' % q), 'x') for q in LEVELS}
    for f in ev.values():
        f.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, 'K0_FIRES.tsv'), 'x')
    fr.write('coin\tt\tday\tk\tlevel\tside\tx\tedge\tticks\tm1\tm2\n')
    proof = open(os.path.join(out_dir, 'K0_PROOF.txt'), 'x')
    for D in days:
        t0 = OB.day0(D); consecutive = prev_day is not None and OB.day0(prev_day) + 86400 == t0
        write = D >= first
        seq = [OB.shift(D, -1), D] + ([OB.shift(D, 1)] if write else [])
        blocks = [(d, coin_bins(d)) for d in seq]
        read_end = max(OB.day0(d) + 86400 for d, b in blocks if b is not None)
        X = np.full((len(coins), STEPS), np.nan); arrs = {}
        for i, c in enumerate(coins):
            parts = [b[c] for d, b in blocks if b is not None]
            tl = np.concatenate([p[0] for p in parts]); o = np.argsort(tl, kind='stable')
            tl, pp, hh, ll = tl[o], np.concatenate([p[1] for p in parts])[o], np.concatenate([p[2] for p in parts])[o], \
                np.concatenate([p[3] for p in parts])[o]
            arrs[c] = (tl, pp, hh, ll); X[i] = range_series(tl, pp, hh, ll, t0)
        if not consecutive:
            prev_x[:] = np.nan
        E = level_edges(hist)
        n_same = n_diff = r_same = r_diff = 0; n_f = {q: 0 for q in LEVELS}; two = {q: [0, 0] for q in LEVELS}
        c1 = OB.read_code(R, 'C1.S10', D, coins) if write else None
        c1n = OB.read_code(R, 'C1.S10', OB.shift(D, 1), coins) if (write and OB.shift(D, 1) in have and OB.shift(D, 1) <= last_ok) else None
        for i, c in enumerate(coins):
            tl, pp, hh, ll = arrs[c]
            if write and i % 4 == 0:
                for k in range(0, STEPS, 12):
                    a = OB.range_bp(tl, pp, hh, ll, t0 + CLOCK * k); v = X[i][k]
                    ok = (np.isnan(v) and a != a) or (a == a and v == v and abs(v - a) <= 1e-9 * max(1.0, abs(a)))
                    r_same += ok; r_diff += (not ok)
            if write:
                ref1 = m1_ref(prev_c1[i]) if (consecutive and prev_c1 is not None) else float('nan')
                sel = (tl > t0 - 86400) & (tl <= t0)
                ref2 = OB.day_median_range(tl[sel], pp[sel], hh[sel], ll[sel], t0 - 86400) if consecutive else float('nan')
                sel2 = (tl > t0 - 86400) & (tl <= t0 + 86400); stp = tick(pp[sel2])
            for q in LEVELS:
                edge = None if E is None else E[q][i]
                lk = None if last_t[(c, q)] is None else int(round((last_t[(c, q)] - t0) / CLOCK))
                ks = coin_day_fires(X[i], prev_x[i], edge, lk)
                if write and i % 4 == 0:
                    same = ks == coin_day_fires_loop(X[i], prev_x[i], edge, lk); n_same += same; n_diff += (not same)
                if write:
                    for k in ks:
                        t = t0 + CLOCK * k; side = OB.move_sign(tl, pp, t, 60)
                        a = np.searchsorted(tl, t - W, 'right'); b = np.searchsorted(tl, t, 'right')
                        rng_px = float(hh[a:b].max() - ll[a:b].min())
                        nt = rng_px / stp if stp == stp and stp > 0 else float('nan')
                        g1 = m1(c1[i], None if c1n is None else c1n[i], t0, t, ref1) if c1 is not None else None
                        g2 = m2(tl, pp, hh, ll, t, ref2, read_end)
                        s = lambda v: '' if v is None else str(v)
                        S = float(X[i][k] / edge) if edge > 0 else float('nan')
                        ev[q].write('%s\t%d\t%d\t%.4f\tBUSY\n' % (c, t, side, S))
                        fr.write('%s\t%d\t%s\t%d\t%s\t%d\t%.4f\t%.4f\t%s\t%s\t%s\n' % (c, t, D, k, q, side, X[i][k], edge,
                                 '' if nt != nt else '%.2f' % nt, s(g1), s(g2)))
                        n_f[q] += 1
                        if nt == nt:
                            two[q][1] += 1; two[q][0] += int(nt <= 2 + 1e-6)
                if ks:
                    last_t[(c, q)] = t0 + CLOCK * ks[-1]
            prev_x[i] = X[i][-1]
        hist.append(X); hist = hist[-OB.HIST_MAX:]; prev_day = D
        prev_c1 = c1 if c1 is not None else OB.read_code(R, 'C1.S10', D, coins)
        if write:
            line = 'DAY %s coins %d edge %s range vec=loop %d differ %d D1 fires same %d differ %d | %s' % (
                D, len(coins), 'none' if E is None else 'yes', r_same, r_diff, n_same, n_diff,
                ' '.join('q%s fires %d at_most_2_steps %d of %d' % (q, n_f[q], two[q][0], two[q][1]) for q in LEVELS))
            proof.write(line + '\n'); print(line, flush=True)
    for f in ev.values():
        f.close()
    fr.close(); proof.close()


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5], a[6:])
