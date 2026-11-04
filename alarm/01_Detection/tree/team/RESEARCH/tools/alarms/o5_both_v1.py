"""QUANT o5_both_v1: O5 DELEVERAGING ON BOTH VENUES exactly as team/RESEARCH/alarms/O5_DELEVERAGE_BOTH_CARD_V1.md 14cc7704 (FROZEN, SCOUT's 3 items
taken). At minute end m_j = D 00:00 + 60 j (j = 0 .. 1439; a 1 min code's column j): b = E2.S04 (Binance 10 min OI change, pct), valued when
finite and E2.S03 = 0 at j and at j - 10 (D - 1's columns for j below 10); h = E2.S06 (Hyperliquid 10 min OI change, pct; stale rows NaN).
Edges of D per coin: the 1st pct (numpy linear) of the valued b, and of the valued h, over the 14 built days before D (a day with 1,000
valued, at least 2 days). HOLD(j) = b(j) < eb(D) and some i in j - 9 .. j with h(i) valued and h(i) < eh(day of i); VALUED(j) = b(j) valued
and some h valued in that window. FIRE at an onset (HOLD after a VALUED j - 1 not HOLD), more than 60 minute ends after the coin's last fire;
one-day chain: D - 1's fires from D - 1 00:00 (j = 0 not an onset). Side = sign(ln p(m) - ln p(m - 600)) from the last bin close at or
before (0 when missing). S = b / eb. M1 (d): roll-10 sum of A1.S08 + A1.S09 (all 10 finite) above the 90th pct of D - 1's roll-10 sums
(1,000 valued), else unvalued. Proofs: entries_loop (a plain loop), and a prefix cut per fire (columns after the cut emptied).
Usage: python3 o5_both_v1.py <lab_days> <lab3 code> <out dir> <first> <last> <coin> ...
Writes O5_EVENTS.tsv, O5_FIRES.tsv (with M1 and D3 fields), O5_PROOF.txt."""
import datetime, os, sys
import numpy as np

HIST, HIST_MIN, DAY_MIN, REFR, W, PCT = 14, 2, 1000, 60, 10, 1.0


def shift(d, k):
    return (datetime.datetime.strptime(d, '%Y%m%d') + datetime.timedelta(days=k)).strftime('%Y%m%d')


def day0(d):
    return int(datetime.datetime.strptime(d, '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp())


def b_valued(s04, s03, s03_prev):
    """s04, s03 (1440,) of D; s03_prev the last 10 columns of D - 1 (1 = carried, missing -> 1) -> b (1440,), NaN unless fresh both ends"""
    cc = np.concatenate([s03_prev, s03])
    fresh = (cc[W:] == 0) & (cc[:-W] == 0)
    return np.where(np.isfinite(s04) & fresh, s04, np.nan)


def edge(hist):
    """hist: valued arrays of the history days -> the 1st pct pooled, NaN without 2 days of 1,000"""
    keep = [h[np.isfinite(h)] for h in hist[-HIST:]]; keep = [k for k in keep if len(k) >= DAY_MIN]
    return float(np.percentile(np.concatenate(keep), PCT)) if len(keep) >= HIST_MIN else np.nan


def state(b, eb, h2, eh2):
    """b (1440,) and eb of D; h2 (1449,) = D - 1's last 9 then D's h; eh2 (1449,) the edge of each h's own day -> HOLD, VALUED (1440,)"""
    with np.errstate(invalid='ignore'):
        hv = np.isfinite(h2) & np.isfinite(eh2); hl = hv & (h2 < eh2)
    win = lambda x: np.array([x[j:j + W].any() for j in range(1440)])
    anyv, anyl = win(hv), win(hl)
    bv = np.isfinite(b) & (eb == eb)
    with np.errstate(invalid='ignore'):
        hold = bv & (b < eb) & anyl
    return hold, bv & anyv


def entries(hold, ok, prev_hold, prev_ok, last, first_onset=True):
    """onset entries; last: index of the coin's last fire relative to this day (negative for the day before) or None"""
    ph = np.concatenate([[prev_hold], hold[:-1]]); po = np.concatenate([[prev_ok], ok[:-1]])
    out = []
    for j in np.flatnonzero(hold & po & ~ph):
        if j == 0 and not first_onset:
            continue
        if last is None or j - last > REFR:
            out.append(int(j)); last = int(j)
    return out, last


def entries_loop(hold, ok, prev_hold, prev_ok, last, first_onset=True):
    out = []
    for j in range(len(hold)):
        h0 = prev_hold if j == 0 else bool(hold[j - 1]); o0 = prev_ok if j == 0 else bool(ok[j - 1])
        if hold[j] and o0 and not h0 and (j > 0 or first_onset) and (last is None or j - last > REFR):
            out.append(j); last = j
    return out, last


def roll10(x):
    x = np.asarray(x, float); fin = np.isfinite(x)
    c = np.concatenate([[0.0], np.cumsum(np.where(fin, x, 0.0))]); m = np.concatenate([[0], np.cumsum(fin)])
    out = np.full(len(x), np.nan)
    if len(x) >= W:
        out[W - 1:] = np.where(m[W:] - m[:-W] == W, c[W:] - c[:-W], np.nan)
    return out


def price_at(tl, px, u):
    i = np.searchsorted(tl, u, side='right') - 1
    out = np.full(len(u), np.nan); ok = i >= 0; out[ok] = px[i[ok]]; return out


def read_code(R, code, D, coins):
    try:
        zc = list(R.index(D, R.part_of(code, D))['coins'])
    except Exception:
        return None
    got = [c for c in coins if c in zc]
    if not got:
        return None
    v = np.asarray(R.read(code, 'v', [D], got)[0], float)
    a = np.full((len(coins), v.shape[1]), np.nan)
    for i, c in enumerate(coins):
        if c in got:
            a[i] = v[got.index(c)]
    return a


def main(root, code_dir, out_dir, first, last_d, coins):
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    R = LD.Days(root, 'research'); have = set(R.days()); built = sorted(have); os.makedirs(out_dir, exist_ok=True)
    fe = open(os.path.join(out_dir, 'O5_EVENTS.tsv'), 'x'); fe.write('coin\tt\tside\tS\tmode\n')
    fr = open(os.path.join(out_dir, 'O5_FIRES.tsv'), 'x')
    fr.write('coin\tt\tday\tj\tside\tb\teb\th_min\teh\tm1\tcarried10\tfunding15\n')
    proof = open(os.path.join(out_dir, 'O5_PROOF.txt'), 'x')
    n = len(coins); arr = {}
    def day_arrays(x):
        """x -> dict(b, h, s03, liq) (n, 1440), cached; missing day -> None"""
        if x not in arr:
            if x not in have:
                arr[x] = None
            else:
                rd = lambda code, fill: (lambda a: np.full((n, 1440), fill) if a is None else a)(read_code(R, code, x, coins))
                s03, s04, s06 = rd('E2.S03', 1.0), rd('E2.S04', np.nan), rd('E2.S06', np.nan)
                s03 = np.where(np.isfinite(s03), s03, 1.0)
                px = arr.get(shift(x, -1)); sp = px['s03'][:, -W:] if px is not None else np.ones((n, W))
                b = np.array([b_valued(s04[i], s03[i], sp[i]) for i in range(n)])
                liq = rd('A1.S08', np.nan) + rd('A1.S09', np.nan)
                arr[x] = dict(b=b, h=s06, s03=s03, liq=liq)
        return arr[x]
    ecache = {}
    def edges_of(x):
        if x not in ecache:
            hd = [y for y in built if y < x][-HIST:]
            hs = [day_arrays(y) for y in hd]; hs = [a for a in hs if a is not None]
            ecache[x] = (np.array([edge([a['b'][i] for a in hs]) for i in range(n)]), np.array([edge([a['h'][i] for a in hs]) for i in range(n)]))
        return ecache[x]
    def day_state(x, i):
        a = day_arrays(x); eb, eh = edges_of(x); p = shift(x, -1); ap = day_arrays(p) if p in have else None
        hp = ap['h'][i, -(W - 1):] if ap is not None else np.full(W - 1, np.nan)
        ehp = edges_of(p)[1][i] if ap is not None else np.nan
        h2 = np.concatenate([hp, a['h'][i]]); eh2 = np.concatenate([np.full(W - 1, ehp), np.full(1440, eh[i])])
        return state(a['b'][i], eb[i], h2, eh2), (a['b'][i], eb[i], h2, eh2)
    days = [d for d in built if shift(first, -HIST - 3) <= d <= last_d]
    for D in days:
        day_arrays(D)
        if D < first:
            continue
        dm1 = shift(D, -1); t0 = day0(D); a = day_arrays(D); n_same = n_diff = pre_same = pre_diff = 0; nfire = 0
        bins_cur = LB.read_bins(R, D, coins); bins_prev = LB.read_bins(R, dm1, coins) if dm1 in have else None
        ap = day_arrays(dm1) if dm1 in have else None
        for i, c in enumerate(coins):
            (hold, ok), parts = day_state(D, i)
            last, ph, po = None, False, False
            if ap is not None:
                (hm, om), _ = day_state(dm1, i)
                _, lm = entries(hm, om, False, False, None, first_onset=False)
                last = None if lm is None else lm - 1440; ph, po = bool(hm[-1]), bool(om[-1])
            js, _ = entries(hold, ok, ph, po, last)
            jl, _ = entries_loop(hold, ok, ph, po, last)
            same = js == jl; n_same += same; n_diff += (not same)
            if not js:
                continue
            tls, pxs = [], []
            for bb in ([bins_prev] if bins_prev is not None else []) + [bins_cur]:
                off, b = bb; s_, e_ = off[i], off[i + 1]; m = b['n'][s_:e_] > 0
                tls.append(b['tl'][s_:e_][m] / 1e6); pxs.append(np.asarray(b['px'][s_:e_][m], float))
            tl = np.concatenate(tls); px = np.concatenate(pxs); o = np.argsort(tl, kind='stable'); tl, px = tl[o], px[o]
            liq2 = np.concatenate([ap['liq'][i, -(W - 1):] if ap is not None else np.full(W - 1, np.nan), a['liq'][i]])
            r10 = roll10(liq2)[W - 1:]
            ref = np.nan
            if ap is not None:
                rp = roll10(ap['liq'][i]); rp = rp[np.isfinite(rp)]
                ref = float(np.percentile(rp, 90)) if len(rp) >= DAY_MIN else np.nan
            car2 = np.concatenate([ap['s03'][i, -(W - 1):] if ap is not None else np.ones(W - 1), a['s03'][i]])
            for j in js:
                m = t0 + 60.0 * j; p1, p0 = price_at(tl, px, np.array([m, m - 600]))
                side = int(np.sign(np.log(p1) - np.log(p0))) if p1 > 0 and p0 > 0 else 0
                b, eb, h2, eh2 = parts; hw = h2[j:j + W]
                m1 = '' if not (r10[j] == r10[j] and ref == ref) else str(int(r10[j] > ref))
                carried = int((car2[j:j + W] != 0).any()); fund = int((m - t0) % 28800 < 900)        # within 15 min after 00, 08, 16 UTC
                fe.write('%s\t%d\t%d\t%.4f\tO5\n' % (c, int(m), side, b[j] / eb))
                fr.write('%s\t%d\t%s\t%d\t%d\t%.5f\t%.5f\t%.5f\t%.5f\t%s\t%d\t%d\n' % (c, int(m), D, j, side, b[j], eb, np.nanmin(hw) if np.isfinite(hw).any() else np.nan, eh2[j + W - 1], m1, carried, fund)); nfire += 1
                # prefix: empty D's columns after j and re-run the day for this coin
                bc = b.copy(); bc[j + 1:] = np.nan; hc = h2.copy(); hc[W - 1 + j + 1:] = np.nan
                hh, oo = state(bc, eb, hc, eh2); jc, _ = entries(hh, oo, ph, po, last)
                ok_ = [x for x in jc if x <= j] == [x for x in js if x <= j]; pre_same += ok_; pre_diff += (not ok_)
        line = 'DAY %s coins %d fires %d D1 loop same %d differ %d prefix same %d differ %d' % (D, n, nfire, n_same, n_diff, pre_same, pre_diff)
        proof.write(line + '\n'); print(line, flush=True)
        for k in [k for k in arr if k < shift(D, -HIST - 3)]:
            del arr[k]
        for k in [k for k in ecache if k < shift(D, -2)]:
            del ecache[k]
    fe.close(); fr.close(); proof.close()


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5:])
