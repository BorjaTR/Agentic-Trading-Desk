"""tests for alarm_view_v1: values, and the LOOKAHEAD PROOF made once on the layer: every causal tool gives the same values up to a cut when
everything after the cut is replaced by garbage (planted future), at many random cuts."""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import alarm_view_v1 as V
NAN = float('nan')
M = V.M


def garbage(x, cut, rng):
    y = np.array(x, float, copy=True); n = y.shape[-1] - cut - 1
    if n > 0:
        y[..., cut + 1:] = rng.normal(0, 1e6, y[..., cut + 1:].shape); y[..., cut + 1::7] = NAN
    return y


class Values(unittest.TestCase):
    def test_to_minutes(self):
        v5 = np.arange(17280.0)[None, :]; self.assertEqual(list(V.to_minutes(v5)[0, :3]), [0.0, 12.0, 24.0])   # 5 s: column 12 j
        v30 = np.arange(2880.0)[None, :]; self.assertEqual(list(V.to_minutes(v30)[0, :3]), [0.0, 2.0, 4.0])    # 30 s: column 2 j
        v1 = np.arange(1440.0)[None, :]; self.assertEqual(list(V.to_minutes(v1)[0, :3]), [0.0, 1.0, 2.0])
        self.assertRaises(ValueError, V.to_minutes, np.zeros((1, 1000)))

    def test_lag(self):
        x = np.arange(10.0); self.assertTrue(np.isnan(V.lag(x, 3)[2])); self.assertEqual(V.lag(x, 3)[5], 2.0)
        self.assertRaises(ValueError, V.lag, x, -1)

    def test_roll(self):
        x = np.arange(10.0); x[4] = NAN
        self.assertEqual(V.roll(x, 3, 'sum')[6], 5.0 + 6.0)                    # x[4..6], NaN skipped
        self.assertEqual(V.roll(x, 3, 'sum', prior=True)[6], 5.0 + 3.0)       # x[3..5]
        self.assertEqual(V.roll(x, 3, 'count')[6], 2.0)
        self.assertTrue(np.isnan(V.roll(x, 3, 'mean', min_count=3)[6]))
        self.assertEqual(V.roll(x, 3, 'median')[8], 7.0); self.assertEqual(V.roll(x, 3, 'median', prior=True)[8], 6.0)
        self.assertAlmostEqual(V.roll(x, 4, 'pct', q=90)[9], np.percentile([6, 7, 8, 9], 90))
        self.assertAlmostEqual(V.roll(x, 3, 'std', ddof=1)[2], np.std([0, 1, 2], ddof=1))
        self.assertEqual(V.roll(x, 3, 'sum')[0], 0.0)                          # a partial window counts its finite values
        self.assertTrue(np.isnan(V.roll(x, 3, 'sum', min_count=3)[1]))
        r = np.random.default_rng(1).normal(size=5000)
        self.assertTrue(np.allclose(V.roll(r, 360, 'pct', q=10, prior=True)[4000], np.percentile(r[3640:4000], 10)))

    def test_engines_equal(self):
        r = np.random.default_rng(3).normal(size=3000); r[::11] = NAN
        for how, kw in (('median', {}), ('pct', {'q': 10}), ('pct', {'q': 99}), ('std', {'ddof': 1}), ('std', {'ddof': 0}), ('max', {}), ('min', {})):
            for prior in (False, True):
                a = V.roll(r, 60, how, prior=prior, min_count=50, engine='pandas', **kw); b = V.roll(r, 60, how, prior=prior, min_count=50, engine='numpy', **kw)
                np.testing.assert_allclose(a, b, rtol=1e-12, atol=1e-12, equal_nan=True, err_msg=how)

    def test_minute_counts(self):
        c = V.minute_counts(np.array([1000.0, 1001.0, 1060.0, 1060.5, 87400.0]), np.array([1, 2, 3, 4, 5]), 1000.0)
        self.assertEqual((c[0], c[1], c[2], c[1440]), (1.0, 5.0, 4.0, 5.0))       # te in (t - 60, t]; the next day's first minute end

    def test_fresh_move(self):
        p = np.array([1.0, 2.0, 4.0, 8.0]); a = np.array([0.0, 10.0, 70.0, 5.0])
        m = V.fresh_move(p, a, 1)
        self.assertAlmostEqual(m[1], np.log(2)); self.assertTrue(np.isnan(m[2])); self.assertTrue(np.isnan(m[3]))   # stale now / stale back

    def test_day_edge(self):
        x = np.tile(np.arange(M, dtype=float), (1, 4)); built = np.array([True, True, True, True])
        e = V.day_edge(x, built, 90.0, hist=14, day_min=1000, min_days=2)
        self.assertTrue(np.isnan(e[0, 0]) and np.isnan(e[0, M]))                      # days 0 and 1: under 2 days before
        self.assertAlmostEqual(e[0, 2 * M], np.percentile(np.arange(M), 90))          # day 2 from days 0 and 1 only
        x2 = x.copy(); x2[0, 2 * M:] = 1e9
        self.assertAlmostEqual(V.day_edge(x2, built, 90.0)[0, 2 * M], e[0, 2 * M])   # the day itself never enters
        b2 = np.array([True, False, True, True]); self.assertTrue(np.isnan(V.day_edge(x, b2, 90.0)[0, 2 * M]))   # a day not built
        self.assertEqual(V.day_edge(x, built, 'max')[0, 3 * M], M - 1.0)

    def test_day_edge_window(self):
        x = np.tile(np.arange(M, dtype=float), (1, 5)); x[0, :M] += 2e6; x[0, M:2 * M] += 1e6; built = np.array([True, True, False, True, True])
        self.assertEqual(V.day_edge(x, built, 'max', hist=2)[0, 4 * M], 1e6 + M - 1)                         # built: the last 2 built, days 1, 3
        self.assertTrue(np.isnan(V.day_edge(x, built, 'max', hist=2, window='calendar')[0, 4 * M]))          # calendar: days 2, 3, one built
        self.assertEqual(V.day_edge(x, built, 'max', hist=3, window='calendar')[0, 4 * M], 1e6 + M - 1)      # calendar: days 1 .. 3, never day 0
        self.assertRaises(ValueError, V.day_edge, x, built, 'max', 14, 1000, 2, 'weeks')

    def test_sums_plain(self):
        x = np.random.default_rng(1).lognormal(16, 1, 20000); x[::7] = NAN
        s = V.roll(x, 10, 'sum', min_count=1); plain = np.array([np.nansum(x[max(0, i - 9):i + 1]) for i in range(len(x))])
        self.assertTrue((s[9:] == plain[9:]).mean() > 0.999)                                 # the rebuild's arithmetic (pairwise order aside)
        s3 = V.roll(x, 360, 'sum'); p3 = np.array([np.nansum(x[i - 359:i + 1]) for i in range(359, len(x))])
        np.testing.assert_allclose(s3[359:], p3, rtol=1e-9)
        sp = np.r_[np.full(100, 1e-3), 1e6, np.full(3000, 1e-3)] * np.random.default_rng(2).uniform(0.5, 1.5, 3101)   # 10 Oct: a spike, then calm
        for dd in (0, 1):
            np.testing.assert_allclose(V.roll(sp, 60, 'std', ddof=dd, min_count=50), V.roll(sp, 60, 'std', ddof=dd, min_count=50, engine='numpy'), rtol=1e-9, equal_nan=True)

    def test_onset(self):
        N = 3 * M; h = np.zeros((1, N), bool); ok = np.ones((1, N), bool)
        h[0, [M + 100, M + 101, M + 160, M + 161, 2 * M + 0]] = True
        self.assertEqual(V.onset(h, ok, 60, first_day=1)[0], [M + 100, 2 * M])   # 101 not onset; 160 is 60 after; 161 follows a hold
        h2 = np.zeros((1, N), bool); h2[0, [2 * M - 10, 2 * M + 50]] = True
        self.assertEqual(V.onset(h2, ok, 60, first_day=2)[0], [])                     # d - 1's fire 60 before
        h2[0, 2 * M + 50] = False; h2[0, 2 * M + 51] = True
        self.assertEqual(V.onset(h2, ok, 60, first_day=2)[0], [2 * M + 51])
        h3 = np.zeros((1, N), bool); h3[0, M] = True; h3[0, M + 30] = True; h3[0, M + 29] = False
        self.assertEqual(V.onset(h3, ok, 60, first_day=2)[0], [])                     # nothing on day 2
        self.assertEqual(V.onset(h3, ok, 20, first_day=1)[0], [M, M + 30])
        ok2 = ok.copy(); ok2[0, M + 99] = False; self.assertEqual(V.onset(h, ok2, 60, first_day=1)[0], [M + 160, 2 * M])   # 100 after an unvalued minute


class FakeDays:
    """lab3.days.Days stand-in: days d0, d0 + 1 (NOT built), d0 + 2; code 'X5' (5 s) with value = column index, its part lacks coin C;
    code 'Y1' (1 min) has no part on the last day"""
    def __init__(self, d0):
        self.purpose = 'research'; self.d = [d0, V.shift(d0, 2)]

    def days(self):
        return list(self.d)

    def part_of(self, name, d):
        if name == 'Y1' and d == self.d[1]:
            raise KeyError('no part for Y1')
        return 'P_' + name

    def index(self, d, part):
        return {'coins': ['A', 'B']}

    def read(self, name, what, days, coins):
        ncol = 17280 if name == 'X5' else 1440
        return [np.tile(np.arange(ncol, dtype=float), (len(coins), 1)) + 1e6 * np.array([['AB'.index(c)] for c in coins])]


class FakeBins:
    """lab3.bins stand-in: read_bins(R, d, coins) -> (off, arrays) in the order asked, an absent coin with 0 rows (lab3's contract)"""
    def __init__(self, trades):
        self.trades = trades                                    # {(day, coin): [(tl_us, px, n), ...]}

    def read_bins(self, R, d, coins):
        rows = [self.trades.get((d, c), []) for c in coins]; off = np.concatenate([[0], np.cumsum([len(r) for r in rows])]).astype(np.int64)
        allr = [x for r in rows for x in r]
        tl = np.array([x[0] for x in allr], np.int64); px = np.array([x[1] for x in allr], float); n = np.array([x[2] for x in allr], np.int64)
        return off, {'tl': tl, 'te': tl, 'px': px, 'n': n}


class Loaders(unittest.TestCase):
    def setUp(self):
        self.d0 = '20250101'; t0 = V.day0(self.d0) * 1000000; us = 1000000
        tr = {(self.d0, 'A'): [(t0 + 300 * us + 1, 10.0, 1), (t0 + 600 * us, 20.0, 1), (t0 + 86000 * us, 30.0, 2)],
              (self.d0, 'B'): [(t0 + 60 * us, 99.0, 1), (t0 + 120 * us, 98.0, 0)]}
        self.v = V.View(None, None, V.shift(self.d0, 2), V.shift(self.d0, 2), ['B', 'A', 'C'], before=2, R=FakeDays(self.d0), LB=FakeBins(tr))

    def test_code_columns(self):
        x = self.v.code('X5')
        self.assertEqual(x[1, 7], 12 * 7.0); self.assertEqual(x[0, 7], 1e6 + 12 * 7.0)     # 5 s column 12 j at j; B is B, A is A
        self.assertTrue(np.isnan(x[2]).all())                                               # coin C absent from the part
        self.assertTrue(np.isnan(x[:, M:2 * M]).all())                                       # day 1 not built
        y = self.v.code('Y1'); self.assertTrue(np.isnan(y[:, 2 * M:]).all())
        self.assertEqual([(d, c) for d, c, _ in self.v.skipped], [(V.shift(self.d0, 2), 'Y1')])   # said, not silent

    def test_prices(self):
        p, age = self.v.prices()
        self.assertTrue(np.isnan(p[1, 5])); self.assertEqual(p[1, 6], np.nan if False else 10.0)   # a trade at t + 1 us is not used at t
        self.assertEqual((p[1, 10], age[1, 10]), (20.0, 0.0))                                # a trade at t exactly is used, age 0
        self.assertEqual(p[0, 1], 99.0); self.assertEqual(p[0, 2], 99.0)                     # B's own prices; a bin with no trades skipped
        self.assertTrue(np.isnan(p[2]).all() and np.isinf(age[2]).all())                     # coin C: no prices
        self.assertEqual(p[1, 2 * M], 30.0); self.assertEqual(age[1, 2 * M], 2 * 86400 - 86000.0)   # carried over the unbuilt day, age grows

    def test_bin_minutes(self):
        m = self.v.bin_minutes(lambda b, s, e: {'px': np.asarray(b['px'][s:e], float), 'one': np.ones(e - s)})
        self.assertEqual(m['one'][1, 6], 1.0); self.assertEqual(m['px'][1, 6], 10.0)          # te = t0 + 300 s + 1 us: minute end j = 6
        self.assertEqual(m['px'][1, 10], 20.0); self.assertEqual(m['one'][1, 5], 0.0)        # te = t exactly: in (t - 60, t]
        self.assertEqual((m['px'][0, 1], m['px'][0, 2]), (99.0, 98.0)); self.assertEqual(m['one'][2].sum(), 0.0)   # B's own; C none
        np.testing.assert_array_equal(V.minute_sums(np.array([1000.0, 1059.0, 1061.0]), np.array([[1.0, 2.0, 4.0]]), 1000.0)[0, :3], [1.0, 2.0, 4.0])

    def test_card_t(self):
        self.assertEqual(V.card_t(2, 5, 'j'), 2 * M + 5); self.assertEqual(V.card_t(2, 5, 'j+1'), 2 * M + 6)
        self.assertRaises(ValueError, V.card_t, 2, 5, 'j-1')


class LookaheadProof(unittest.TestCase):
    """the layer's causality, once: values at or before a cut never change when everything after the cut is garbage"""
    def setUp(self):
        self.rng = np.random.default_rng(7); N = 4 * M
        self.x = self.rng.normal(size=(3, N)); self.x[:, ::13] = NAN
        self.p = np.exp(np.cumsum(self.rng.normal(0, 1e-3, (3, N)), 1)); self.a = self.rng.uniform(0, 90, (3, N))
        self.cuts = list(self.rng.integers(0, N - 1, 6)) + [0, M - 1, M, 2 * M - 1, N - 2]

    def same(self, f, *arrays):
        full = f(*arrays)
        for cut in self.cuts:
            g = f(*[garbage(a, cut, self.rng) for a in arrays])
            np.testing.assert_array_equal(np.asarray(full)[..., :cut + 1], np.asarray(g)[..., :cut + 1], err_msg='cut %d' % cut)

    def test_lag(self):
        for k in (0, 1, 10, 600):
            self.same(lambda x: V.lag(x, k), self.x)

    def test_roll(self):
        for how, kw in (('sum', {}), ('mean', {}), ('count', {}), ('median', {}), ('pct', {'q': 10}), ('std', {'ddof': 1}), ('max', {})):
            for prior in (False, True):
                self.same(lambda x: V.roll(x, 60, how, prior=prior, **kw), self.x)       # numpy engine = pandas engine (test_engines_equal)

    def test_fresh_move(self):
        self.same(lambda p, a: V.fresh_move(p, a, 10), self.p, self.a)

    def test_day_edge(self):
        built = np.array([True] * 4)
        self.same(lambda x: V.day_edge(x, built, 10.0, day_min=500), self.x)

    def test_onset(self):
        hold = self.rng.random((3, 4 * M)) < 0.01; ok = self.rng.random((3, 4 * M)) < 0.95
        full = V.onset(hold, ok, 30, first_day=1)
        for cut in self.cuts:
            h2 = hold.copy(); o2 = ok.copy(); h2[:, cut + 1:] = self.rng.random(h2[:, cut + 1:].shape) < 0.5; o2[:, cut + 1:] = True
            g = V.onset(h2, o2, 30, first_day=1)
            for c in range(3):
                self.assertEqual([t for t in full[c] if t <= cut], [t for t in g[c] if t <= cut])


if __name__ == '__main__':
    unittest.main()
