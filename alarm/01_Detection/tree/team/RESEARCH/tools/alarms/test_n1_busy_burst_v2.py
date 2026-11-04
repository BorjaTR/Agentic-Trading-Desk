"""planted tests for n1_busy_burst_v2 (v1 tests kept: no bar of the hour) (seconds; card alarms/N1_BUSY_BURST_CARD_V1.md D1)"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import n1_busy_burst_v2 as N

NAN = float('nan')


def day(v=10.0):
    return np.full(N.DAY_STEPS, v)


class TestEdges(unittest.TestCase):
    def test_minute_ends_only(self):
        a = day(10.0); a[1::12] = 1e6                     # huge values off the minute ends must not move the edge
        e = N.edges([N.minute_ends(a[None, :]), N.minute_ends(a[None, :])])
        self.assertAlmostEqual(e[0], 10.0)

    def test_needs_two_days_and_uses_last_14(self):
        self.assertIsNone(N.edges([N.minute_ends(day()[None, :])]))
        old = [N.minute_ends(day(1000.0)[None, :])] * 3; new = [N.minute_ends(day(5.0)[None, :])] * 14
        self.assertAlmostEqual(N.edges(old + new)[0], 5.0)

    def test_history_day_needs_1000_clean(self):
        good = N.minute_ends(day(5.0)[None, :]); thin = N.minute_ends(day(500.0)[None, :]).copy(); thin[0, 999:] = NAN   # 999 clean
        self.assertTrue(np.isnan(N.edges([thin, good])[0]))               # one history day only
        self.assertAlmostEqual(N.edges([thin, good, good])[0], 5.0)       # the thin day is not used
        ok = N.minute_ends(day(500.0)[None, :]).copy(); ok[0, 1000:] = NAN                                            # 1,000 clean
        self.assertGreater(N.edges([ok, good, good])[0], 5.0)

    def test_percentile_and_clean(self):
        a = np.arange(1440, dtype=float)[None, :]; b = a.copy(); b[0, :100] = -1.0; b[0, 100:200] = NAN   # 1,240 clean: a history day
        e = N.edges([a, a])[0]
        self.assertAlmostEqual(e, np.percentile(np.tile(np.arange(1440.0), 2), 99))
        e2 = N.edges([b, b])[0]
        self.assertAlmostEqual(e2, np.percentile(np.tile(np.arange(200.0, 1440.0), 2), 99))


class TestFires(unittest.TestCase):
    def test_cross_fires_first_step(self):
        x = day(); x[1000:1010] = 50.0
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [1000])

    def test_equal_edge_does_not_fire(self):
        x = day(); x[1000] = 20.0; x[1001] = 20.5
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [1001])
        x2 = day(); x2[1000] = 20.0
        self.assertEqual(N.fires_vec(x2, 10.0, 20.0, None), [])

    def test_after_hole_no_fire(self):
        x = day(); x[999] = NAN; x[1000:1005] = 50.0
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [])
        x[999] = -1.0                                      # negative is not clean either
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [])

    def test_refractory_15_min(self):
        x = day(); x[1000] = 50.0; x[1180] = 50.0; x[1361] = 50.0
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [1000, 1361])   # 1180 is 180 steps after: not more than 15 min

    def test_refractory_across_midnight_and_k0(self):
        x = day(); x[0] = 50.0; x[200] = 50.0
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, -10), [200])          # a fire 10 steps before midnight blocks k = 0
        self.assertEqual(N.fires_vec(x, 10.0, 20.0, None), [0, 200])
        self.assertEqual(N.fires_vec(x, NAN, 20.0, None), [200])          # D-1 not read: no crossing at k = 0

    def test_no_edge_no_fire(self):
        x = day(); x[5] = 1e9
        self.assertEqual(N.fires_vec(x, 10.0, None, None), [])
        self.assertEqual(N.fires_vec(x, 10.0, NAN, None), [])

    def test_vec_equals_loop(self):
        rng = np.random.default_rng(7)
        for _ in range(20):
            x = rng.gamma(2.0, 10.0, N.DAY_STEPS); x[rng.integers(0, N.DAY_STEPS, 300)] = NAN
            x[rng.integers(0, N.DAY_STEPS, 50)] = -1.0
            e = float(np.nanpercentile(x, 97)); lf = int(rng.integers(-400, 0)); pl = float(rng.choice([NAN, 5.0, 500.0]))
            self.assertEqual(N.fires_vec(x, pl, e, lf), N.fires_loop(x, pl, e, lf))


class TestMeaning(unittest.TestCase):
    def bins(self, t0, seed=3):
        rng = np.random.default_rng(seed)
        tl = np.sort(t0 + rng.uniform(0, 86400, 20000)); px = 100 * np.exp(np.cumsum(rng.normal(0, 1e-4, len(tl))))
        hi = px * (1 + rng.uniform(0, 2e-4, len(tl))); lo = px * (1 - rng.uniform(0, 2e-4, len(tl)))
        return tl, rng.integers(1, 5, len(tl)).astype(float), px, hi, lo

    def test_day_median_range_equals_loop(self):
        t0 = 1757635200.0
        tl, n, px, hi, lo = self.bins(t0)
        self.assertAlmostEqual(N.day_median_range(tl, px, hi, lo, t0), N.day_median_range_loop(tl, px, hi, lo, t0), places=9)
        k = (tl > t0 + 3600) & (tl < t0 + 7200)            # an empty hour
        self.assertAlmostEqual(N.day_median_range(tl[~k], px[~k], hi[~k], lo[~k], t0),
                               N.day_median_range_loop(tl[~k], px[~k], hi[~k], lo[~k], t0), places=9)

    def test_side_ratio_range(self):
        t = 10000.0
        tl = np.concatenate([t - 3600 + 60.0 * np.arange(59) + 1, [t - 60.0, t - 30.0, t - 20.0, t - 1.0]])
        n = np.concatenate([np.ones(59), [1.0, 4.0, 4.0, 4.0]])
        px = np.concatenate([np.full(59, 100.0), [100.0, 100.5, 101.0, 101.0]]); hi = px + 0.2; lo = px - 0.2
        side, ratio, rng_bp, ref = N.meaning(tl, n, px, hi, lo, t, 7.0)
        self.assertEqual(side, 1)
        self.assertAlmostEqual(ratio, 12.0)                # 12 trades in (t - 60, t] over a median of 1 a minute
        self.assertAlmostEqual(rng_bp, (101.2 - 100.3) / 100.0 * 1e4)
        self.assertEqual(ref, 7.0)


class TestHourBar(unittest.TestCase):
    def test_mapping_strictly_before(self):
        prev = np.full(1440, 10.0); day_ = np.full(1440, 10.0); day_[0] = 1000.0     # D's first minute end (k = 0) is not in its own bar
        hb = N.hour_bar(prev, day_)
        self.assertEqual(hb[0], 20.0)                 # D-1's last 60: median 10
        self.assertEqual(hb[1], 20.0)                 # k = 1: minute ends 1381 (D-1) .. 0 (D): median still 10
        p3 = np.full(1440, 10.0); p3[-30:] = 30.0; d3 = np.full(1440, 10.0); d3[0] = 1000.0
        self.assertEqual(N.hour_bar(p3, d3)[0], 40.0)  # median 20 of D-1's last 60; with k = 0's own minute end it would be 30
        prev2 = np.full(1440, NAN); prev2[-29:] = 10.0
        self.assertTrue(np.isnan(N.hour_bar(prev2, np.full(1440, NAN))[0]))   # 29 clean: no bar
        prev2[-30:] = 10.0
        self.assertEqual(N.hour_bar(prev2, np.full(1440, NAN))[0], 20.0)

    def test_busy_all_day_does_not_refire(self):
        x = np.full(N.DAY_STEPS, 100.0); x[::7] = 40.0                                 # busy all day, dips below the 2-week edge
        me_prev = np.full(1440, 100.0)
        v1 = N.fires_vec(x, 100.0, 50.0, None)
        hb = N.hour_bar(me_prev, N.minute_ends(x[None, :])[0])
        v2 = N.fires_vec(x, 100.0, 50.0, None, hb)
        self.assertGreater(len(v1), 50); self.assertEqual(v2, [])

    def test_burst_over_the_hour_fires_and_loop_equal(self):
        x = np.full(N.DAY_STEPS, 10.0); x[5000:5010] = 100.0
        hb = N.hour_bar(np.full(1440, 10.0), N.minute_ends(x[None, :])[0])
        self.assertEqual(N.fires_vec(x, 10.0, 50.0, None, hb), [5000])
        rng = np.random.default_rng(5)
        for _ in range(6):
            y = rng.gamma(2.0, 10.0, N.DAY_STEPS); y[rng.integers(0, N.DAY_STEPS, 200)] = NAN
            mp = rng.gamma(2.0, 10.0, 1440); md = N.minute_ends(y[None, :])[0]; hb = N.hour_bar(mp, md)
            e = float(np.nanpercentile(y, 95))
            self.assertEqual(N.fires_vec(y, 5.0, e, -30, hb), N.fires_loop(y, 5.0, e, -30, mp, md))


if __name__ == '__main__':
    unittest.main()
