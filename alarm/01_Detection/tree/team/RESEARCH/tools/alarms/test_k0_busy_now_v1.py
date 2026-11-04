"""planted tests for k0_busy_now_v1 (card alarms/K0_BUSY_NOW_CONTROL_CARD_V1.md e94f9227, s4 D1): one per rule line; seconds"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import k0_busy_now_v1 as K
import onset_band_v4 as OB

NAN = float('nan')
T0 = 1_760_000_400.0 - (1_760_000_400 % 86400)   # a UTC midnight


def bins(ts, ps, spread=0.0):
    tl = np.asarray(ts, float); px = np.asarray(ps, float)
    return tl, px, px + spread, px - spread


class TestRange(unittest.TestCase):
    def test_two_computations_equal(self):
        rng = np.random.default_rng(7)
        slots = np.sort(rng.choice(np.arange(-2000, 28800), 9000, replace=False))      # irregular 3 s bins, D - 1's tail too
        tl = T0 + 3.0 * slots + rng.uniform(0, 2.999, len(slots))
        px = 100 * np.exp(np.cumsum(rng.normal(0, 1e-4, len(slots))))
        hi = px * (1 + rng.uniform(0, 3e-4, len(slots))); lo = px * (1 - rng.uniform(0, 3e-4, len(slots)))
        x = K.range_series(tl, px, hi, lo, T0)
        self.assertEqual(len(x), K.STEPS)
        for k in range(0, K.STEPS, 7):
            a = OB.range_bp(tl, px, hi, lo, T0 + 5.0 * k)
            if a != a:
                self.assertTrue(np.isnan(x[k]), k)
            else:
                self.assertAlmostEqual(x[k], a, places=9)
        self.assertTrue(np.isnan(x).any() and np.isfinite(x).any())

    def test_window_is_open_left_closed_right(self):
        t = T0 + 5.0 * 100
        tl, px, hi, lo = bins([t - 120, t - 60, t - 30, t], [100.0, 200.0, 101.0, 102.0])
        x = K.range_series(tl, px, hi, lo, T0)
        # bins in (t - 60, t]: 101 and 102 (the 200 at t - 60 exactly is out); the price at or before t - 60 is 200
        self.assertAlmostEqual(x[100], (102.0 - 101.0) / 200.0 * 1e4)
        tl2, px2, hi2, lo2 = bins([t - 120, t - 59.999, t + 0.001], [100.0, 200.0, 50.0])
        x2 = K.range_series(tl2, px2, hi2, lo2, T0)
        self.assertAlmostEqual(x2[100], 0.0)                                         # only the 200; the 50 after t is not used

    def test_missing(self):
        t = T0 + 5.0 * 100
        tl, px, hi, lo = bins([t - 200, t - 61], [100.0, 100.0])
        self.assertTrue(np.isnan(K.range_series(tl, px, hi, lo, T0)[100]))           # no bin in the window
        tl, px, hi, lo = bins([t - 30], [100.0])
        self.assertTrue(np.isnan(K.range_series(tl, px, hi, lo, T0)[100]))           # no price at or before t - 60
        e = np.array([])
        self.assertTrue(np.isnan(K.range_series(e, e, e, e, T0)).all())


class TestFires(unittest.TestCase):
    def test_level_edges(self):
        hist = [np.tile(np.arange(1000, dtype=float), (2, 1)) for _ in range(3)]
        hist[0][1, :400] = NAN                                                        # coin 1, day 0 under 70 pct clean
        E = K.level_edges(hist, (99.0, 99.9))
        self.assertAlmostEqual(E[99.0][0], np.percentile(np.arange(1000.0), 99.0))
        self.assertAlmostEqual(E[99.9][1], np.percentile(np.arange(1000.0), 99.9))  # two clean days left: an edge
        hist[1][1, :400] = NAN
        self.assertTrue(np.isnan(K.level_edges(hist, (99.0,))[99.0][1]))             # one history day: no edge
        self.assertIsNone(K.level_edges(hist[:1], (99.0,)))

    def test_onset_and_refractory_across_midnight(self):
        x = np.zeros(K.STEPS); x[10] = 5.0; x[100] = 5.0; x[200] = 5.0
        self.assertEqual(K.coin_day_fires(x, 0.0, 1.0, None), [10, 200])            # 100: 90 steps after 10, blocked; 200: 190 after
        self.assertEqual(K.coin_day_fires(x, 0.0, 1.0, -171), [10, 200])            # D - 1 fire 171 steps before 00:00: 10 is 181 after
        self.assertEqual(K.coin_day_fires(x, 0.0, 1.0, -170), [100])                # 10 is 180 after: blocked; 100 is 270 after; 200 is 100 after 100
        y = np.zeros(K.STEPS); y[10] = 1.0; y[20] = 2.0
        self.assertEqual(K.coin_day_fires(y, 0.0, 1.0, None), [20])                  # equal to the edge is not past it
        z = np.zeros(K.STEPS); z[9] = NAN; z[10] = 5.0; z[30] = 0.5; z[31] = 5.0
        self.assertEqual(K.coin_day_fires(z, 0.0, 1.0, None), [31])                  # no fire on a step after a missing one
        w = np.zeros(K.STEPS); w[0] = 5.0
        self.assertEqual(K.coin_day_fires(w, 5.0, 1.0, None), [])                    # D - 1's last step already past: not a crossing
        self.assertEqual(K.coin_day_fires(w, NAN, 1.0, None), [])                    # D - 1's last step missing
        self.assertEqual(K.coin_day_fires(w, 0.5, 1.0, None), [0])
        self.assertEqual(K.coin_day_fires(w, 0.5, NAN, None), [])                    # no edge, no fire

    def test_loop_equals_vec(self):
        rng = np.random.default_rng(3)
        for _ in range(20):
            x = rng.exponential(1.0, K.STEPS); x[rng.random(K.STEPS) < 0.05] = NAN
            lk = int(rng.integers(-400, 0)) if rng.random() < 0.5 else None
            pl = float(rng.exponential(1.0))
            a = K.coin_day_fires(x, pl, 4.0, lk)
            self.assertEqual(a, K.coin_day_fires_loop(x, pl, 4.0, lk))
            self.assertTrue(len(a) > 0)


class TestMeaning(unittest.TestCase):
    def test_m1_column_and_reference(self):
        prev = np.zeros((1, 1440)); prev[0, :] = np.linspace(-1, 1, 1440)
        cur = np.zeros((1, 1440)); cur[0, 3] = 0.95; cur[0, 4] = -0.2
        ref = K.m1_ref(prev[0])
        self.assertAlmostEqual(ref, np.percentile(np.abs(prev[0]), 90))
        self.assertEqual(K.m1(cur[0], None, T0, T0 + 125.0, ref), 1)                 # minute end at or after t = column 3 (180 s)
        self.assertEqual(K.m1(cur[0], None, T0, T0 + 185.0, ref), 0)                 # column 4
        self.assertEqual(K.m1(cur[0], None, T0, T0 + 180.0, ref), 1)                 # exactly at a minute end: that column
        self.assertIsNone(K.m1(cur[0], None, T0, T0 + 86395.0, ref))                 # column 1440 = D + 1's column 0, not read
        nxt = np.full(1440, 0.99)
        self.assertEqual(K.m1(cur[0], nxt, T0, T0 + 86395.0, ref), 1)
        self.assertIsNone(K.m1(cur[0], None, T0, T0 + 125.0, NAN))

    def test_m2_cut_at_the_read_end(self):
        t = T0 + 5.0 * 100
        tl, px, hi, lo = bins([t - 120, t - 20, t + 20], [100.0, 100.0, 103.0])              # window (t - 30, t + 30] at t + 30
        self.assertEqual(K.m2(tl, px, hi, lo, t, 1.0, T0 + 86400), 1)               # range at t + 30: 100 .. 103 = 300 bp > 1
        self.assertEqual(K.m2(tl, px, hi, lo, t, 400.0, T0 + 86400), 0)
        self.assertIsNone(K.m2(tl, px, hi, lo, t, 1.0, t + 29))                      # t + 30 beyond what was read
        self.assertIsNone(K.m2(tl, px, hi, lo, t, NAN, T0 + 86400))

    def test_tick(self):
        p = np.array([100.00, 100.05, 100.10, 100.05, 100.20])
        self.assertAlmostEqual(K.tick(p), 0.05)
        self.assertTrue(np.isnan(K.tick(np.array([5.0, 5.0]))))


if __name__ == '__main__':
    unittest.main()
