"""QUANT o1_flush_v2 (= v1 dae7bfc1 with M1 on the coin codes A1.S08 long, A1.S09 short; the rule untouched). o1_flush_v1 (card alarms/O1_OI_FLUSH_CARD_V1.md b63f9818, part 0 PASS WITH 2 by SCOUT, items taken; DRAFT).
O1 LONG FLUSH / O2 SHORT SQUEEZE: at minute end m_j = D 00:00 + 60 j, o = E2.S02 (Binance OI in coins of the contract, 1 min, row in force
61 s), valued when E2.S03 (carried flag) is 0; f(j) = (o(j) - o(j - 10)) / o(j - 10), both valued (D - 1's last columns before j = 10);
p = the last bin close at or before t (lab bins); g(j) = ln p(m_j) - ln p(m_j - 600). Edges: the 1st pct of f and the 90th pct of |g| over
the minute ends with both finite of the history days among the 14 built days before D (at least 1,000 such minute ends a day; at least
2 days). BOTH = f below its edge and |g| above its edge (strict). FIRE at the first j with BOTH after a valued j - 1 (f and g finite) not
BOTH, more than 30 minute ends after the coin's last fire of that side (across midnight). Side = sign of g: -1 O1 (price fell), +1 O2.
Settings: S (1 pct, 90th), A (0.5 pct, 90th, beside), B (1 pct, 75th, beside). D2 (after the fact): M1 the move's side liquidations
(A1.S08 when the price fell, A1.S09 when it rose) summed over j - 9 .. j above the coin's median 10-minute sum of D - 1; M2 Hyperliquid
OI E2.S05 at j below at j - 10. Usage: python3 o1_flush_v1.py <lab_days> <lab3 code> <out dir> <first> <last> <last readable> <coin> ...
Writes O1_EVENTS.tsv (S), O1a_EVENTS.tsv, O1b_EVENTS.tsv, O1_FIRES.tsv (all settings), O1_PROOF.txt."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v4 as OB

HIST, HIST_MIN, DAY_MIN, REFR, W = 14, 2, 1000, 30, 10
SETTINGS = {'S': (1.0, 90.0, 'O1_EVENTS.tsv'), 'A': (0.5, 90.0, 'O1a_EVENTS.tsv'), 'B': (1.0, 75.0, 'O1b_EVENTS.tsv')}


def oi_change(o, carried, o_prev, c_prev):
    """o, carried (1440,) of D; o_prev, c_prev the last W columns of D - 1 (or NaN) -> f (1440,)"""
    oo = np.concatenate([o_prev, o]); cc = np.concatenate([c_prev, carried])
    ok = np.isfinite(oo) & (cc == 0) & (oo > 0)
    a, b = oo[W:], oo[:-W]; oka, okb = ok[W:], ok[:-W]
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where(oka & okb, (a - b) / b, np.nan)


def price_move(tl, px, t):
    """t: minute ends -> g = ln p(t) - ln p(t - 600), NaN without a bin at or before"""
    def at(u):
        i = np.searchsorted(tl, u, side='right') - 1
        out = np.full(len(u), np.nan); okk = i >= 0; out[okk] = px[i[okk]]; return out
    p1, p0 = at(t), at(t - 600)
    with np.errstate(invalid='ignore', divide='ignore'):
        return np.where((p1 > 0) & (p0 > 0), np.log(p1) - np.log(p0), np.nan)


def edges(hist, qf, qg):
    keep = []
    for f, g in hist[-HIST:]:
        ok = np.isfinite(f) & np.isfinite(g)
        if ok.sum() >= DAY_MIN:
            keep.append((f[ok], np.abs(g[ok])))
    if len(keep) < HIST_MIN:
        return None
    return float(np.percentile(np.concatenate([k[0] for k in keep]), qf)), float(np.percentile(np.concatenate([k[1] for k in keep]), qg))


def state(f, g, e):
    ok = np.isfinite(f) & np.isfinite(g)
    with np.errstate(invalid='ignore'):
        both = ok & (f < e[0]) & (np.abs(g) > e[1])
    return both, ok


def entries(both, ok, g, prev_both, prev_ok, last):
    """last: {side: j of the last fire relative to D (negative for D - 1) or None} -> [(j, side)]; last is updated"""
    pb = np.concatenate([[prev_both], both[:-1]]); po = np.concatenate([[prev_ok], ok[:-1]])
    out = []
    for j in np.flatnonzero(both & po & ~pb):
        s = 1 if g[j] > 0 else -1
        if last.get(s) is None or j - last[s] > REFR:
            out.append((int(j), s)); last[s] = int(j)
    return out


def entries_loop(both, ok, g, prev_both, prev_ok, last):
    out = []
    for j in range(len(both)):
        b0 = prev_both if j == 0 else bool(both[j - 1]); o0 = prev_ok if j == 0 else bool(ok[j - 1])
        if both[j] and o0 and not b0:
            s = 1 if g[j] > 0 else -1
            if last.get(s) is None or j - last[s] > REFR:
                out.append((j, s)); last[s] = j
    return out


def roll10(x):
    """10-minute sums ending at each column (NaN unless all 10 finite)"""
    x = np.asarray(x, float); fin = np.isfinite(x)
    c = np.concatenate([[0.0], np.cumsum(np.where(fin, x, 0.0))]); m = np.concatenate([[0], np.cumsum(fin)])
    out = np.full(len(x), np.nan)
    if len(x) >= W:
        out[W - 1:] = np.where(m[W:] - m[:-W] == W, c[W:] - c[:-W], np.nan)
    return out


def main(root, code_dir, out_dir, first, last_d, last_ok, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); os.makedirs(out_dir, exist_ok=True)
    days = [d for d in OB.day_list(first, last_d, HIST + 1) if d in have and d <= last_ok]
    ev = {k: open(os.path.join(out_dir, v[2]), 'x') for k, v in SETTINGS.items()}
    for f in ev.values():
        f.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, 'O1_FIRES.tsv'), 'x'); fr.write('coin\tt\tday\tj\tsetting\tside\tf\tg\tm1\tm2\n')
    proof = open(os.path.join(out_dir, 'O1_PROOF.txt'), 'x')
    n = len(coins); hist = {c: [] for c in coins}; prevst = {}; last = {(c, k): {} for c in coins for k in SETTINGS}
    prev_day = None; prev_o = np.full((n, 1440), np.nan); prev_c = np.ones((n, 1440)); prev_bins = None; prev_liq = None
    for D in days:
        t0 = OB.day0(D); cons = prev_day is not None and OB.day0(prev_day) + 86400 == t0; write = D >= first
        rd = lambda code, fill: (lambda a: np.full((n, 1440), fill) if a is None else np.asarray(a, float))(OB.read_code(R, code, D, coins))
        o, car = rd('E2.S02', np.nan), rd('E2.S03', 1.0)
        off, b = LB.read_bins(R, D, coins)
        cur = []
        for i in range(n):
            s_, e_ = off[i], off[i + 1]; m = b['n'][s_:e_] > 0
            cur.append((b['tl'][s_:e_][m] / 1e6, np.asarray(b['px'][s_:e_][m], float)))
        liq = (rd('A1.S08', np.nan), rd('A1.S09', np.nan))                  # coin scope (v1 read the MARKET codes S12, S13: J33466)
        h5 = rd('E2.S05', np.nan) if write else None
        tm = t0 + 60.0 * np.arange(1440)
        n_same = n_diff = 0; nf = {k: 0 for k in SETTINGS}
        for i, c in enumerate(coins):
            op, cp = (prev_o[i, -W:], prev_c[i, -W:]) if cons else (np.full(W, np.nan), np.ones(W))
            f = oi_change(o[i], car[i], op, cp)
            tl, px = cur[i]
            if cons and prev_bins is not None:
                tl = np.concatenate([prev_bins[i][0], tl]); px = np.concatenate([prev_bins[i][1], px])
            g = price_move(tl, px, tm)
            for k, (qf, qg, _) in SETTINGS.items():
                lst = {s: (None if v is None else v - 1440) for s, v in last[(c, k)].items()} if cons else {}
                last[(c, k)] = dict(lst)                                  # every day relative to D, also when no edges
                pb, po = prevst.get((c, k), (False, False)) if cons else (False, False)
                e = edges(hist[c], qf, qg)
                if e is None:
                    prevst[(c, k)] = (False, False)
                    continue
                both, ok = state(f, g, e)
                lst2 = dict(lst)
                js = entries(both, ok, g, pb, po, lst)
                if write and i % 4 == 0:
                    same = js == entries_loop(both, ok, g, pb, po, lst2); n_same += same; n_diff += (not same)
                last[(c, k)] = {s: v for s, v in lst.items()}
                prevst[(c, k)] = (bool(both[-1]), bool(ok[-1]))
                if write:
                    for j, s in js:
                        lq = liq[0][i] if s < 0 else liq[1][i]
                        r10 = roll10(lq); ref = np.nan
                        if prev_liq is not None and cons:
                            pq = prev_liq[0][i] if s < 0 else prev_liq[1][i]; rr = roll10(pq); rr = rr[np.isfinite(rr)]
                            ref = float(np.median(rr)) if len(rr) else np.nan
                        lv = r10[j] if j >= W - 1 else np.nan
                        m1 = '' if not (lv == lv and ref == ref) else str(int(lv > ref))
                        m2 = ''
                        if h5 is not None and j >= W and np.isfinite(h5[i][j]) and np.isfinite(h5[i][j - W]) and h5[i][j] != h5[i][j - W]:
                            m2 = str(int(h5[i][j] < h5[i][j - W]))
                        t = t0 + 60 * j
                        ev[k].write('%s\t%d\t%d\t%.4f\tO1%s\n' % (c, t, s, f[j] / e[0], '' if k == 'S' else k.lower()))
                        fr.write('%s\t%d\t%s\t%d\t%s\t%d\t%.6f\t%.6f\t%s\t%s\n' % (c, t, D, j, k, s, f[j], g[j], m1, m2)); nf[k] += 1
            hist[c].append((f, g)); hist[c] = hist[c][-HIST:]
        prev_o, prev_c, prev_bins, prev_liq, prev_day = o, car, cur, liq, D
        if write:
            line = 'DAY %s coins %d D1 same %d differ %d fires S %d A %d B %d' % (D, n, n_same, n_diff, nf['S'], nf['A'], nf['B'])
            proof.write(line + '\n'); print(line, flush=True)
    for f in ev.values():
        f.close()
    fr.close(); proof.close()


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5], a[6:])
