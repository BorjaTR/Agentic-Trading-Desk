"""QUANT o5_both_v2: O5 DELEVERAGING ON BOTH VENUES (alarms/O5_DELEVERAGE_BOTH_CARD_V1.md 14cc7704, FROZEN) on alarm_view_v1 (AV1): the
whole run at once on the minute-end timeline; the same rule and output lines as o5_both_v1 d1a1c9b0 (its DEV outputs are the equality check).
  b = E2.S04 where E2.S03 = 0 at t and t - 10 (a missing S03 counts as carried); h = E2.S06; eb, eh = 1st pct over the 14 built days before
  (1,000 valued a day, 2 days); HOLD = b < eb and some h(i) < eh(day of i) for i in t - 9 .. t; VALUED = b and eb valued and some h valued
  with its edge in that window; onset, refractory 60, one-day chain. Side = sign(ln p(t) - ln p(t - 10)) from the last bin close at or
  before (0 when missing); S = b / eb. M1 = the 10-minute sum of A1.S08 + A1.S09 (all 10 finite) above the 90th pct of the day before's
  sums (that day's own minutes 9 on, 1,000 valued; that day built). carried10 = some S03 not 0 in t - 9 .. t; funding15 = within 15 min
  after 00, 08, 16 UTC.
Usage: python3 o5_both_v2.py <lab_days> <lab3 code> <out dir> <first> <last> <coin> ...  Writes O5_EVENTS.tsv, O5_FIRES.tsv, O5_TIMES.txt."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import alarm_view_v1 as V

M, W, REFR = V.M, 10, 60


def carried(s03):
    """S03 with a missing value counted as carried (1)"""
    return np.where(np.isfinite(s03), s03, 1.0)


def b_valued(s04, s03c):
    with np.errstate(invalid='ignore'):
        return np.where(np.isfinite(s04) & (s03c == 0) & (V.lag(s03c, W) == 0), s04, np.nan)


def states(b, h, built):
    E = lambda x: V.day_edge(x, built, 1.0, hist=14, day_min=1000, min_days=2)
    eb, eh = E(b), E(h)
    with np.errstate(invalid='ignore'):
        hv = np.isfinite(h) & np.isfinite(eh); hl = hv & (h < eh)
        anyv = V.roll(hv.astype(float), W, 'sum') > 0; anyl = V.roll(hl.astype(float), W, 'sum') > 0
        bv = np.isfinite(b) & np.isfinite(eb); hold = bv & (b < eb) & anyl
    return hold, bv & anyv, eb, eh


def m1_of(liq, built):
    r10 = V.roll(liq, W, 'sum', min_count=W)
    j = np.tile(np.arange(M), r10.shape[1] // M)[None, :]
    own = np.where(j >= W - 1, r10, np.nan)                                      # the day's own sums (its minutes 9 on)
    ref = V.day_edge(own, built, 90.0, hist=1, day_min=1000, min_days=1)
    prev_built = np.repeat(np.concatenate([[False], built[:-1]]), M)[None, :]
    ref = np.where(prev_built, ref, np.nan)
    with np.errstate(invalid='ignore'):
        return np.where(np.isfinite(r10) & np.isfinite(ref), (r10 > ref).astype(float), np.nan)


def main(root, code_dir, out_dir, first, last, coins):
    T = [time.time()]; os.makedirs(out_dir, exist_ok=True)
    v = V.View(root, code_dir, first, last, coins, before=20)
    s03c = carried(v.code('E2.S03')); b = b_valued(v.code('E2.S04'), s03c); h = v.code('E2.S06'); liq = v.code('A1.S08') + v.code('A1.S09')
    T.append(time.time()); p, age = v.prices(); T.append(time.time())
    hold, ok, eb, eh = states(b, h, v.built); m1 = m1_of(liq, v.built)
    p0 = V.lag(p, W)
    with np.errstate(invalid='ignore', divide='ignore'):
        side = np.where((p > 0) & (p0 > 0), np.sign(np.log(p) - np.log(p0)), 0).astype(int)
    hmin = V.roll(h, W, 'min'); car = V.roll((s03c != 0).astype(float), W, 'sum') > 0
    fires = V.onset(hold, ok, REFR, first_day=v.first_day); T.append(time.time()); n = 0
    with open(os.path.join(out_dir, 'O5_EVENTS.tsv'), 'x') as fe, open(os.path.join(out_dir, 'O5_FIRES.tsv'), 'x') as fr:
        fe.write('coin\tt\tside\tS\tmode\n'); fr.write('coin\tt\tday\tj\tside\tb\teb\th_min\teh\tm1\tcarried10\tfunding15\n')
        for i, c in enumerate(coins):
            for t in fires[i]:
                d, j = v.day_of(t); m = int(v.t[t]); ms = '' if not np.isfinite(m1[i, t]) else str(int(m1[i, t]))
                fe.write('%s\t%d\t%d\t%.4f\tO5\n' % (c, m, side[i, t], b[i, t] / eb[i, t]))
                fr.write('%s\t%d\t%s\t%d\t%d\t%.5f\t%.5f\t%.5f\t%.5f\t%s\t%d\t%d\n' % (c, m, d, j, side[i, t], b[i, t], eb[i, t], hmin[i, t], eh[i, t], ms,
                                                                                    int(car[i, t]), int((m - V.day0(d)) % 28800 < 900))); n += 1
    T.append(time.time())
    with open(os.path.join(out_dir, 'O5_TIMES.txt'), 'x') as f:
        f.write('days %d coins %d fires O5 %d; seconds: codes %.1f prices %.1f rule %.1f write %.1f\n' % (len(v.days), len(coins), n, *np.diff(T)))
    with open(os.path.join(out_dir, 'SKIPPED.tsv'), 'x') as f:
        f.write('day\tcode\treason\n'); f.writelines('%s\t%s\t%s\n' % k for k in v.skipped)
    print('skipped day-codes', len(v.skipped), flush=True)
    print(open(os.path.join(out_dir, 'O5_TIMES.txt')).read(), flush=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], a[1], a[2], a[3], a[4], a[5:])
