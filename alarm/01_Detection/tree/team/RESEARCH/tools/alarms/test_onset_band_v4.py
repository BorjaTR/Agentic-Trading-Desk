"""planted tests for onset_band_v4 (v2 tests kept, the N2 M3 test in USD as v3) (cards N2, N3, N4, N5, N9 s2; seconds)"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v4 as O
NAN = float('nan')


class TestTransform(unittest.TestCase):
    def test_sum6_needs_all_six(self):
        v = np.ones(20); v[10] = NAN
        x, s, ok = O.transform(v, 'sum6abs')
        self.assertTrue(np.isnan(x[4])); self.assertEqual(x[5], 6.0); self.assertTrue(all(np.isnan(x[10:16]))); self.assertEqual(x[16], 6.0)
        v2 = -np.ones(8); x2, s2, _ = O.transform(v2, 'sum6abs'); self.assertEqual(x2[7], 6.0); self.assertEqual(s2[7], -6.0)

    def test_pos_nonneg_abs(self):
        v = np.array([-1.0, 0.0, 2.0, NAN])
        self.assertTrue(np.array_equal(np.isnan(O.transform(v, 'pos')[0]), [True, True, False, True]))
        self.assertTrue(np.array_equal(np.isnan(O.transform(v, 'nonneg')[0]), [True, False, False, True]))
        self.assertEqual(list(O.transform(v, 'abs')[0][:3]), [1.0, 0.0, 2.0])


class TestEdges(unittest.TestCase):
    def test_history_day_70pct_and_two_days(self):
        good = np.full((1, 100), 5.0); thin = np.full((1, 100), 500.0); thin[0, 69:] = NAN      # 69 pct clean: not a history day
        self.assertTrue(np.isnan(O.edges([thin, good], 99, None)[0]))
        self.assertAlmostEqual(O.edges([thin, good, good], 99, None)[0], 5.0)
        ok = np.full((1, 100), 500.0); ok[0, 70:] = NAN                                         # 70 pct: a history day
        self.assertGreater(O.edges([ok, good, good], 99, None)[0], 5.0)
        self.assertIsNone(O.edges([good], 99, None))

    def test_floor_and_last_14(self):
        a = np.full((1, 100), 10.0)
        self.assertEqual(O.edges([a, a], 99, 25000.0)[0], 25000.0)
        old = [np.full((1, 100), 1e6)] * 3; new = [np.full((1, 100), 3.0)] * 14
        self.assertAlmostEqual(O.edges(old + new, 99, None)[0], 3.0)


class TestFires(unittest.TestCase):
    def test_top_first_step_strict_and_hole(self):
        x = np.full(500, 1.0); x[100:105] = 9.0; x[200] = 5.0; x[300] = NAN; x[301] = 9.0
        self.assertEqual(O.fires_vec(x, 1.0, 5.0, 'top', None, 180), [100])            # 5.0 = edge: no; after a hole: no

    def test_bottom_band(self):
        x = np.full(500, 10.0); x[50] = 0.5; x[51] = 0.4; x[400] = 0.9
        self.assertEqual(O.fires_vec(x, 10.0, 1.0, 'bottom', None, 180), [50, 400])
        y = np.full(500, 10.0); y[50] = 1.0; y[51] = 0.9                                 # equal to the edge is not past it
        self.assertEqual(O.fires_vec(y, 10.0, 1.0, 'bottom', None, 180), [51])

    def test_refractory_more_than(self):
        x = np.full(1000, 1.0); x[10] = 9.0; x[190] = 9.0; x[371] = 9.0
        self.assertEqual(O.fires_vec(x, 1.0, 5.0, 'top', None, 180), [10, 371])
        x2 = np.full(1000, 1.0); x2[0] = 9.0
        self.assertEqual(O.fires_vec(x2, 1.0, 5.0, 'top', -5, 180), [])                # D-1's fire 5 steps before midnight
        self.assertEqual(O.fires_vec(x2, NAN, 5.0, 'top', None, 180), [])              # D-1 not read: no crossing at k = 0
        self.assertEqual(O.fires_vec(x2, 1.0, 5.0, 'top', None, 180), [0])

    def test_vec_equals_loop(self):
        rng = np.random.default_rng(11)
        for band in ('top', 'bottom'):
            for _ in range(15):
                x = rng.gamma(2.0, 10.0, 3000); x[rng.integers(0, 3000, 100)] = NAN
                e = float(np.nanpercentile(x, 97 if band == 'top' else 3)); lk = int(rng.integers(-300, 0)); pl = float(rng.choice([NAN, 1.0, 900.0]))
                self.assertEqual(O.fires_vec(x, pl, e, band, lk, 180), O.fires_loop(x, pl, e, band, lk, 180))


class TestPrices(unittest.TestCase):
    def test_move_sign_and_range(self):
        tl = np.array([0.0, 30.0, 59.0, 61.0, 90.0]); px = np.array([100.0, 101.0, 99.0, 102.0, 103.0])
        self.assertEqual(O.move_sign(tl, px, 90.0, 60), 1)                               # 101 (at 30) -> 103
        self.assertEqual(O.move_sign(tl, px, 59.0, 30), -1)                              # 100 (at 0, last at or before 29) -> 99
        self.assertEqual(O.move_sign(tl, px, 5.0, 60), 0)                                # no price at -55
        hi = px + 1; lo = px - 1
        self.assertAlmostEqual(O.range_bp(tl, px, hi, lo, 90.0), (104.0 - 98.0) / 101.0 * 1e4)


class TestStep(unittest.TestCase):
    def test_price_step(self):
        self.assertEqual(O.price_step([np.array([0.0, 0.3, 0.6, NAN]), np.array([0.9, 0.15])]), 0.15)
        self.assertTrue(np.isnan(O.price_step([np.array([0.0, NAN])])))


class TestD2v2(unittest.TestCase):
    D = '20250924'

    def test_n2_m3_new_block_in_bins(self):
        t0 = O.day0(self.D); t = t0 + 3600
        tl = np.array([t - 90, t - 30, t - 10]); pp = np.array([100.0, 100.0, 100.0])
        bb = np.array([100000.0, 1000.0, 26000.0]); ss = np.array([0.0, 0.0, 0.0])    # 26,000 USD in the minute (v3: the field is USD)
        m = O.d2('N2', {}, 0, 60, 1440, 60, t, tl, pp, pp, pp, 1, np.nan, np.zeros(1440), np.zeros(1440), '20251231', self.D, bb, ss, None)
        self.assertEqual(m[2], 1)
        bb2 = np.array([100000.0, 1000.0, 24000.0])                                       # 24,000: no; the 100,000 at t - 90 is outside
        m = O.d2('N2', {}, 0, 60, 1440, 60, t, tl, pp, pp, pp, 1, np.nan, np.zeros(1440), np.zeros(1440), '20251231', self.D, bb2, ss, None)
        self.assertEqual(m[2], 0)

    def test_n3_m3_stayed_thin(self):
        raw = np.full(1440, 100.0); raw[200] = 1.0; raw[201] = 50.0                     # next minute end 50 < median 100
        rawc = np.concatenate([np.full(1440, 100.0), raw])
        m = O.d2('N3', {}, 0, 200, 1440, 60, O.day0(self.D) + 12000, np.array([0.0]), np.array([1.0]), np.array([1.0]), np.array([1.0]),
                 0, np.nan, raw, raw, '20251231', self.D, None, None, rawc)
        self.assertEqual(m[2], 1)
        raw[201] = 150.0; rawc = np.concatenate([np.full(1440, 100.0), raw])
        m = O.d2('N3', {}, 0, 200, 1440, 60, O.day0(self.D) + 12000, np.array([0.0]), np.array([1.0]), np.array([1.0]), np.array([1.0]),
                 0, np.nan, raw, raw, '20251231', self.D, None, None, rawc)
        self.assertEqual(m[2], 0)

    def test_n9_m3_depth_clean_at_the_minute(self):
        d3 = np.full((1, 3 * 1440), 5.0); d3[0, 1440 + 10] = NAN
        ex = {'D3.S01': (d3, 1440)}; t0 = O.day0(self.D)
        f = lambda t: O.d2('N9', ex, 0, 0, 17280, 5, t, np.array([0.0]), np.array([1.0]), np.array([1.0]), np.array([1.0]), 0, np.nan,
                           np.zeros(17280), np.zeros(17280), '20251231', self.D, None, None, None)[2]
        self.assertEqual(f(t0 + 10 * 60 + 30), 0); self.assertEqual(f(t0 + 11 * 60), 1)


class TestRunRule(unittest.TestCase):
    def test_pair_rule_n3(self):
        x = np.full(300, 10.0); x[50] = 0.5                                              # one snapshot below: no fire
        self.assertEqual(O.fires_run(x, None, 1.0, 'bottom', None, 15, 2), [])
        x[100] = 0.5; x[101] = 0.4                                                       # two in a row: fire at the second
        self.assertEqual(O.fires_run(x, None, 1.0, 'bottom', None, 15, 2), [101])
        y = np.full(300, 10.0); y[100] = 0.5; y[101] = NAN; y[102] = 0.4                 # a hole between: no fire
        self.assertEqual(O.fires_run(y, None, 1.0, 'bottom', None, 15, 2), [])

    def test_six_steps_n9_and_midnight(self):
        x = np.full(500, 1.0); x[100:105] = 9.0                                          # five steps: no fire
        self.assertEqual(O.fires_run(x, None, 5.0, 'top', None, 180, 6), [])
        x[200:206] = 9.0                                                                 # six: fire at the sixth
        self.assertEqual(O.fires_run(x, None, 5.0, 'top', None, 180, 6), [205])
        z = np.full(500, 1.0); z[0:3] = 9.0; prev = np.array([1.0, 1.0, 1.0, 9.0, 9.0, 9.0])
        self.assertEqual(O.fires_run(z, prev, 5.0, 'top', None, 180, 6), [2])           # three from D-1 and three of D

    def test_two_venues_n4(self):
        x = np.full(300, 0.1); x[50] = 5.0; cond = np.zeros(300, bool)
        self.assertEqual(O.fires_run(x, None, 1.0, 'top', None, 15, 1, cond, None), [])   # Binance alone
        cond[50] = True
        self.assertEqual(O.fires_run(x, None, 1.0, 'top', None, 15, 1, cond, None), [50])
        x2 = x.copy(); x2[49] = NAN
        self.assertEqual(O.fires_run(x2, None, 1.0, 'top', None, 15, 1, cond, None), [])  # the step before missing

    def test_run_equals_loop_and_v1(self):
        rng = np.random.default_rng(3)
        for r in (1, 2, 6):
            for _ in range(8):
                x = rng.gamma(2.0, 10.0, 2000); x[rng.integers(0, 2000, 60)] = NAN
                e = float(np.nanpercentile(x, 90)); cond = rng.random(2000) > 0.3; prev = rng.gamma(2.0, 10.0, 7)
                pc = rng.random(7) > 0.3
                for c, p in ((None, None), (cond, pc)):
                    self.assertEqual(O.fires_run(x, prev, e, 'top', -40, 180, r, c, p), O.fires_run_loop(x, prev, e, 'top', -40, 180, r, c, p))
        x = rng.gamma(2.0, 10.0, 3000); e = float(np.nanpercentile(x, 97))
        self.assertEqual(O.fires_run(x, np.array([5.0]), e, 'top', None, 180, 1), O.fires_vec(x, 5.0, e, 'top', None, 180))


if __name__ == '__main__':
    unittest.main()
