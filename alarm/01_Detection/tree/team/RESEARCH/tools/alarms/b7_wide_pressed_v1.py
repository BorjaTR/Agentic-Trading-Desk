"""QUANT b7_wide_pressed_v1 (card alarms/B7_WIDE_AND_PRESSED_CARD_V1.md 897ade9b, part 0 PASS WITH 2 by SCOUT, items taken; DRAFT).
B7 WIDE AND PRESSED: at 5 s step k (known at D 00:00 + 5 k), s = X1.COST.S01 (half spread, bps), i = X1.BOOKX.S04 (10 s OFI over the event
mean top depth). Edges: the 95th pct of s and of |i| (beside: the 99th) over the clean steps (both finite) of the history days among the 14
built days before D (a history day has at least 70 pct clean steps; at least 2). BOTH = s above its edge and |i| above its edge (strict).
FIRE at the first step k with BOTH after a clean step not BOTH (D - 1's last step before k = 0), more than 180 steps (15 min) after the
coin's last fire (across midnight). Side = sign of i. D2 (after the fact): M1 the net taker dollars B1.S09 over the same 10 s (steps k - 1,
k) has the side's sign; M2 our bins' 60 s range at the fire above the coin's median 60 s range of D - 1.
Usage: python3 b7_wide_pressed_v1.py <lab_days> <lab3 code> <out dir> <first day> <last day> <last readable day> <coin> ...
Writes B7_EVENTS.tsv (top 5), B7x1_EVENTS.tsv (top 1, beside), B7_FIRES.tsv (both, setting column), B7_PROOF.txt."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v4 as OB

HIST, HIST_MIN, CLEAN, REFR, NSTEP = 14, 2, 0.70, 180, 17280
CODES = ('X1.COST.S01', 'X1.BOOKX.S04', 'B1.S09')
LEVELS = {95: 'B7_EVENTS.tsv', 99: 'B7x1_EVENTS.tsv'}


def edges(hist, q):
    """hist: list of (s, i) arrays (NSTEP,) of history days -> (s_hi, i_hi) or None"""
    keep = []
    for s, i in hist[-HIST:]:
        ok = np.isfinite(s) & np.isfinite(i)
        if ok.mean() >= CLEAN:
            keep.append((s[ok], np.abs(i[ok])))
    if len(keep) < HIST_MIN:
        return None
    return (float(np.percentile(np.concatenate([k[0] for k in keep]), q)),
            float(np.percentile(np.concatenate([k[1] for k in keep]), q)))


def state(s, i, e):
    s, i = np.asarray(s, float), np.asarray(i, float)
    ok = np.isfinite(s) & np.isfinite(i)
    with np.errstate(invalid='ignore'):
        both = ok & (s > e[0]) & (np.abs(i) > e[1])
    return both, ok


def entries(st, ok, prev_st, prev_ok, last_k):
    st = np.asarray(st, bool); ok = np.asarray(ok, bool)
    pst = np.concatenate([[prev_st], st[:-1]]); pok = np.concatenate([[prev_ok], ok[:-1]])
    out, last = [], last_k
    for j in np.flatnonzero(st & pok & ~pst):
        if last is None or j - last > REFR:
            out.append(int(j)); last = int(j)
    return out


def entries_loop(st, ok, prev_st, prev_ok, last_k):
    out, last = [], last_k
    for j in range(len(st)):
        b_st = prev_st if j == 0 else bool(st[j - 1]); b_ok = prev_ok if j == 0 else bool(ok[j - 1])
        if bool(st[j]) and b_ok and not b_st and (last is None or j - last > REFR):
            out.append(j); last = j
    return out


def m1_sign(flow, k, prev_last, side):
    """net taker dollars over steps k - 1 and k (k - 1 of D - 1 when k = 0) -> '1', '0' or '' (missing or side 0)"""
    a = flow[k]; b = prev_last if k == 0 else flow[k - 1]
    if side == 0 or not (np.isfinite(a) and np.isfinite(b)):
        return ''
    return str(int(np.sign(a + b) == side))


def main(root, code_dir, out_dir, first, last, last_ok, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); os.makedirs(out_dir, exist_ok=True)
    days = [d for d in OB.day_list(first, last, HIST + 1) if d in have and d <= last_ok]
    ev = {q: open(os.path.join(out_dir, f), 'x') for q, f in LEVELS.items()}
    for f in ev.values():
        f.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, 'B7_FIRES.tsv'), 'x'); fr.write('coin\tt\tday\tk\tsetting\tside\ts\ti\tm1\tm2\n')
    proof = open(os.path.join(out_dir, 'B7_PROOF.txt'), 'x')
    hist = {c: [] for c in coins}; prev = {}; last = {(c, q): None for c in coins for q in LEVELS}; prev_day = None; prev_flow = {}
    for D in days:
        t0 = OB.day0(D); consecutive = prev_day is not None and OB.day0(prev_day) + 86400 == t0; write = D >= first
        raw = []
        for code in CODES:
            a = OB.read_code(R, code, D, coins)
            raw.append(np.full((len(coins), NSTEP), np.nan) if a is None else np.array([np.asarray(x, float)[:NSTEP] for x in a]))
        px = None
        if write:
            px = {}
            for d in (OB.shift(D, -1), D, OB.shift(D, 1)):
                if d in have and d <= last_ok:
                    off, b = LB.read_bins(R, d, coins)
                    for k, c in enumerate(coins):
                        s_, e_ = off[k], off[k + 1]; m = b['n'][s_:e_] > 0
                        px.setdefault(c, []).append((b['tl'][s_:e_][m] / 1e6, np.asarray(b['px'][s_:e_][m], float),
                                                     np.asarray(b['hi'][s_:e_][m], float), np.asarray(b['lo'][s_:e_][m], float)))
        n_same = n_diff = 0; nf = {q: 0 for q in LEVELS}
        for k, c in enumerate(coins):
            s, ii, fl = raw[0][k], raw[1][k], raw[2][k]
            pfl = prev_flow.get(c, np.nan) if consecutive else np.nan
            if px is not None and c in px:
                tl = np.concatenate([p[0] for p in px[c]]); o = np.argsort(tl, kind='stable')
                tl, pp, hh, ll = tl[o], np.concatenate([p[1] for p in px[c]])[o], np.concatenate([p[2] for p in px[c]])[o], np.concatenate([p[3] for p in px[c]])[o]
            else:
                tl = pp = hh = ll = np.array([])
            ref = None
            for q in LEVELS:
                e = edges(hist[c], q)
                if e is None:
                    continue
                st, ok = state(s, ii, e)
                pst, pok = prev.get((c, q), (False, False)) if consecutive else (False, False)
                lk = None if last[(c, q)] is None else int(round((last[(c, q)] - t0) / 5))
                js = entries(st, ok, pst, pok, lk)
                if write and k % 4 == 0:
                    same = js == entries_loop(st, ok, pst, pok, lk); n_same += same; n_diff += (not same)
                if write:
                    if ref is None:
                        sel = (tl > t0 - 86400) & (tl <= t0)
                        ref = OB.day_median_range(tl[sel], pp[sel], hh[sel], ll[sel], t0 - 86400) if len(tl) else np.nan
                    for j in js:
                        t = t0 + 5 * j; side = int(np.sign(ii[j]))
                        r = OB.range_bp(tl, pp, hh, ll, t) if len(tl) else np.nan
                        m2 = '' if not (r == r and ref == ref) else str(int(r > ref))
                        m1 = m1_sign(fl, j, pfl, side)
                        ev[q].write('%s\t%d\t%d\t%d\tB7\n' % (c, t, side, q))
                        fr.write('%s\t%d\t%s\t%d\t%d\t%d\t%.4f\t%.4f\t%s\t%s\n' % (c, t, D, j, q, side, s[j], ii[j], m1, m2))
                        nf[q] += 1
                if js:
                    last[(c, q)] = t0 + 5 * js[-1]
                prev[(c, q)] = (bool(st[-1]), bool(ok[-1]))
            hist[c].append((s, ii)); hist[c] = hist[c][-HIST:]; prev_flow[c] = fl[-1]
        prev_day = D
        if write:
            line = 'DAY %s coins %d D1 same %d differ %d fires top5 %d top1 %d' % (D, len(coins), n_same, n_diff, nf[95], nf[99])
            proof.write(line + '\n'); print(line, flush=True)
    for f in ev.values():
        f.close()
    fr.close(); proof.close()


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5], a[6:])
