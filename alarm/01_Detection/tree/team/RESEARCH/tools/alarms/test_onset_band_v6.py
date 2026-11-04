"""planted tests for onset_band_v6: all of v5 (bc41aaa8) kept, plus Q4 (card Q4_BASIS_JUMP_CARD_V1 eb124211 s0 d, s2 and items)"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import onset_band_v6 as O
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



class TestQ1(unittest.TestCase):
    def test_config(self):
        a = O.ALARMS['Q1']
        self.assertEqual((a['code'], a['band'], a['q'], a['xform'], a['sign']), ('X1.BOOKX.S04', 'top', 99.9, 'abs', 'book'))
        self.assertEqual(O.ALARMS['Q1b']['q'], 99.5)
        x, s, ok = O.transform(np.array([-3.0, 2.0]), 'abs'); self.assertEqual(list(x), [3.0, 2.0]); self.assertEqual(list(s), [-3.0, 2.0])

    def test_d2(self):
        st = 4; s09 = np.full((1, 12), NAN); s03 = np.full((1, 12), NAN)
        s09[0, st + 1], s09[0, st + 2] = 30.0, -10.0              # net 5 x 20 = 100 dollars, buying
        s03[0, st + 2] = 5.0                                       # OFI 5 coins x price 100 = 500 dollars
        extra = {'B1.S09': (s09, st), 'X1.BOOKX.S03': (s03, st)}
        tl = np.array([0.0, 85.0, 100.0]); pp = np.array([100.0, 99.0, 100.0])   # 10 s ending at 100: 99 (at 90) -> 100, up
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, 1), (1, 1, 1))     # 100 under half of 500: the book moved without trades
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, -1), (0, 0, 1))
        s03[0, st + 2] = 1.5                                       # OFI 150 dollars: 100 is not under half (75)
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, 1)[2], 0)
        s03[0, st + 2] = 1.0                                       # OFI 100 dollars: trades not under half
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, 1)[2], 0)
        s09[0, st + 1] = NAN
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, 1)[:1], (None,))   # a missing row: no reading
        self.assertEqual(O.q1_d2(extra, 0, 2, 100.0, 0, tl, pp, 0), (None, None, None))
        tl2 = np.array([0.0, 95.0]); pp2 = np.array([100.0, 100.0])
        self.assertIsNone(O.q1_d2(extra, 0, 2, 100.0, 0, tl2, pp2, 1)[1])          # no move: no reading


class TestQ4(unittest.TestCase):
    def test_config(self):
        a = O.ALARMS['Q4']
        self.assertEqual((a['code'], a['band'], a['q'], a['xform'], a['sign'], a['lag']), ('E3.S01', 'top', 99.9, 'diff1abs', 'book', 1))
        self.assertEqual((O.ALARMS['Q4b']['q'], O.ALARMS['Q4c']['lag']), (99.5, 5))

    def test_d2(self):
        t0 = 86400.0 * 10
        tl = np.arange(t0 - 86400, t0 + 3600, 30.0); pp = np.full(len(tl), 100.0)
        pp[::4] = 100.01                                                  # D - 1: up and down 1 bp at every minute end (median |r| 1 bp)
        t = t0 + 1800; j = int(np.searchsorted(tl, t))
        pp[tl > t0] = 100.0; pp[j] = 101.0                                # at t the perp moved up 1 pct: no move 1 to 5 min before
        st = 3; c1 = np.full((1, 2000), NAN); k = 30; c1[0, st + k] = 0.5
        extra = {'C1.S10': (c1, st)}
        self.assertEqual(O.q4_d2(extra, 0, k, t, t0, tl, pp, 1), (1, 1, '0|0'))
        self.assertEqual(O.q4_d2(extra, 0, k, t, t0, tl, pp, -1), (0, 0, '0|0'))
        pp[j] = 100.0; pp[j - 6] = 101.0                                  # the move came 3 min before, the perp flat at t: lag 1, flat 1
        m = O.q4_d2(extra, 0, k, t, t0, tl, pp, 1); self.assertEqual(m[2], '1|1'); self.assertIsNone(m[0])
        self.assertEqual(O.q4_d2(extra, 0, k, t, t0, tl, pp, 0), (None, None, None))
        c1[0, st + k] = NAN; self.assertIsNone(O.q4_d2(extra, 0, k, t, t0, tl, pp, 1)[1])
        pp[j - 6] = 100.0; pp[j - 1] = 101.0; pp[j] = 101.0               # up from 60 s before, flat over the last 30 s: M1 reads the 60 s
        self.assertEqual(O.q4_d2(extra, 0, k, t, t0, tl, pp, 1)[0], 1)

if __name__ == '__main__':
    unittest.main()
