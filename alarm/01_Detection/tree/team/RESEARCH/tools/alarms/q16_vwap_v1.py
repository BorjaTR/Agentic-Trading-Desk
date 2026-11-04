"""QUANT q16_vwap_v1: Q16 TAKER VWAP PRESSURE (alarms/Q16_VWAP_PRESSURE_CARD_V1.md d6ddf4a2; SCOUT PASS WITH 2: the drift-free beside and
M1 read on it) on alarm_view_v1.
  Per minute end t, the bins with te in (t - 60, t]: B = buy dollars, VB = B / sum(buy / px) over bins with buy > 0, valued with B >= 1,000
  and 3 bins with buys; S, VS the same for sells. mid0 = C13.S05 at t - 1, mid1 = C13.S05 at t.
  MAIN: gb = 1e4 (VB / mid0 - 1), gs = 1e4 (1 - VS / mid0); BESIDE (drift out): the same against (mid0 + mid1) / 2.
  Edges eb, es = 99.5th pct over the 14 built days before (1,000 valued a day, 2 days); HOLD gb > eb (+1) or gs > es (-1), both: the larger
  ratio; VALUED = a side valued with its edge; onset, refractory 30, one-day chain. S = g / e.
  M1: sign(mid1 - mid0) = side. D3 flags: move = |1e4 ln(mid1 / mid0)| >= the fire's gap; block = |B1.S04| above half the side's dollars.
Usage: python3 q16_vwap_v1.py <lab_days> <lab3 code> <out dir> <first> <last> <coin> ...  Writes Q16_EVENTS.tsv (main), Q16B_EVENTS.tsv
(beside), Q16_FIRES.tsv, Q16_READ.txt (D2 and D3 for both), Q16_TIMES.txt, SKIPPED.tsv."""
import collections, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import alarm_view_v1 as V

M, REFR, Q, FLOOR, NB = V.M, 30, 99.5, 1000.0, 3


def per_bin(b, s, e):
    buy = np.asarray(b['buy'][s:e], float); sell = np.asarray(b['sell'][s:e], float); px = np.asarray(b['px'][s:e], float)
    with np.errstate(invalid='ignore', divide='ignore'):
        ub = np.where((buy > 0) & (px > 0), buy / px, 0.0); us = np.where((sell > 0) & (px > 0), sell / px, 0.0)
    return {'B': buy, 'S': sell, 'UB': ub, 'US': us, 'NB': (buy > 0).astype(float), 'NS': (sell > 0).astype(float)}


def vwaps(m):
    with np.errstate(invalid='ignore', divide='ignore'):
        vb = np.where((m['B'] >= FLOOR) & (m['NB'] >= NB) & (m['UB'] > 0), m['B'] / m['UB'], np.nan)
        vs = np.where((m['S'] >= FLOOR) & (m['NS'] >= NB) & (m['US'] > 0), m['S'] / m['US'], np.nan)
    return vb, vs


def gaps(vb, vs, ref):
    with np.errstate(invalid='ignore', divide='ignore'):
        ok = np.isfinite(ref) & (ref > 0)
        return np.where(ok, 1e4 * (vb / ref - 1), np.nan), np.where(ok, 1e4 * (1 - vs / ref), np.nan)


def state(gb, gs, built):
    E = lambda x: V.day_edge(x, built, Q, hist=14, day_min=1000, min_days=2)
    eb, es = E(gb), E(gs)
    with np.errstate(invalid='ignore', divide='ignore'):
        okb = np.isfinite(gb) & np.isfinite(eb); oks = np.isfinite(gs) & np.isfinite(es)
        hb = okb & (gb > eb); hs = oks & (gs > es); rb = gb / eb; rs = gs / es
        side = np.where(hb & hs, np.where(rb >= rs, 1, -1), np.where(hb, 1, np.where(hs, -1, 0)))
        g = np.where(side > 0, gb, gs); e = np.where(side > 0, eb, es)
    return hb | hs, okb | oks, side, g, e


def read(rows, label):
    n = len(rows)
    if not n:
        return '%s fires 0\n' % label
    v = [r[4] for r in rows if r[4] == r[4]]; m1 = np.mean(v) if v else float('nan')
    days = collections.Counter(r[1] for r in rows); coins = collections.Counter(r[0] for r in rows)
    bd = [(d, c) for d, c in days.most_common() if c > 0.03 * n]; bc = [(d, c) for d, c in coins.most_common() if c > 0.05 * n]
    mv = np.mean([r[5] for r in rows]); bl = np.mean([r[6] for r in rows]); sd = collections.Counter(r[2] for r in rows)
    return ('%s fires %d M1 %.3f of %d valued (line 60) move share %.3f block share %.3f sides %s days over 3 pct %s coins over 5 pct %s\n'
            % (label, n, m1, len(v), mv, bl, dict(sd), bd, bc))


def main(root, code_dir, out_dir, first, last, coins):
    T = [time.time()]; os.makedirs(out_dir, exist_ok=True)
    v = V.View(root, code_dir, first, last, coins, before=20)
    mid1 = v.code('C13.S05'); s04 = v.code('B1.S04'); mid0 = V.lag(mid1, 1); T.append(time.time())
    m = v.bin_minutes(per_bin); vb, vs = vwaps(m); T.append(time.time())
    out = {}
    for mode, ref in (('Q16', mid0), ('Q16B', (mid0 + mid1) / 2)):
        gb, gs = gaps(vb, vs, ref); hold, ok, side, g, e = state(gb, gs, v.built)
        out[mode] = (V.onset(hold, ok, REFR, first_day=v.first_day), side, g, e)
    with np.errstate(invalid='ignore', divide='ignore'):
        dmid = np.sign(mid1 - mid0); mv_bp = np.abs(1e4 * np.log(mid1 / mid0))
    T.append(time.time()); nd = len(v.days) - v.first_day
    with open(os.path.join(out_dir, 'Q16_FIRES.tsv'), 'x') as fr, open(os.path.join(out_dir, 'Q16_READ.txt'), 'x') as rd:
        fr.write('mode\tcoin\tt\tday\tj\tside\tg\te\tm1\tmove\tblock\n')
        for mode in ('Q16', 'Q16B'):
            fires, side, g, e = out[mode]; rows = []
            with open(os.path.join(out_dir, '%s_EVENTS.tsv' % mode), 'x') as fe:
                fe.write('coin\tt\tside\tS\tmode\n')
                for i, cn in enumerate(coins):
                    for t in fires[i]:
                        d, j = v.day_of(t); sd = int(side[i, t]); m1 = float(dmid[i, t] == sd) if np.isfinite(dmid[i, t]) else float('nan')
                        mvf = int(np.isfinite(mv_bp[i, t]) and mv_bp[i, t] >= g[i, t]); dol = m['B'][i, t] if sd > 0 else m['S'][i, t]
                        blk = int(np.isfinite(s04[i, t]) and abs(s04[i, t]) > 0.5 * dol)
                        fe.write('%s\t%d\t%d\t%.4f\t%s\n' % (cn, int(v.t[t]), sd, g[i, t] / e[i, t], mode))
                        fr.write('%s\t%s\t%d\t%s\t%d\t%d\t%.4f\t%.4f\t%s\t%d\t%d\n' % (mode, cn, int(v.t[t]), d, j, sd, g[i, t], e[i, t],
                                                                                    '' if m1 != m1 else int(m1), mvf, blk))
                        rows.append((cn, d, sd, j, m1, mvf, blk))
            rd.write(read(rows, mode))
            rd.write('%s per coin-day %.2f over %d days x %d coins\n' % (mode, len(rows) / max(nd * len(coins), 1), nd, len(coins)))
    T.append(time.time())
    with open(os.path.join(out_dir, 'SKIPPED.tsv'), 'x') as f:
        f.write('day\tcode\treason\n'); f.writelines('%s\t%s\t%s\n' % k for k in v.skipped)
    with open(os.path.join(out_dir, 'Q16_TIMES.txt'), 'x') as f:
        f.write('days %d coins %d; seconds: codes %.1f bins %.1f rule %.1f write %.1f; skipped %d\n' % (len(v.days), len(coins), *np.diff(T), len(v.skipped)))
    print(open(os.path.join(out_dir, 'Q16_READ.txt')).read() + open(os.path.join(out_dir, 'Q16_TIMES.txt')).read(), flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5:])
