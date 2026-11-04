"""planted tests for b8_roll_v1 (card alarms/B8_ROLL_SPREAD_CARD_V1.md 5b863b48), from the card's words"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import b8_roll_v1 as B
NAN = float('nan')


class T(unittest.TestCase):
    def test_bounce_gives_the_spread(self):
        mid, s = 100.0, 0.02                                          # bid 99.99, ask 100.01: spread 2 bp of the mid
        rng = np.random.default_rng(0); side = rng.choice([-1, 1], 4000)
        px = mid + side * s / 2
        self.assertAlmostEqual(B.roll_one(px), 2.0, delta=0.1)
        self.assertEqual(B.roll_one(np.linspace(100, 101, 300)), 0.0)        # a trend: c >= 0, Roll 0
        drift = px * np.exp(5e-5 * np.arange(4000))                           # the mean move is removed before the covariance
        self.assertAlmostEqual(B.roll_one(drift), B.roll_one(px), delta=0.02)
        self.assertTrue(np.isnan(B.roll_one([100.0, 100.1])))

    def test_series_window_and_count(self):
        tl = np.arange(0, 1800, 3.0); px = 100 + 0.01 * (np.arange(len(tl)) % 2)
        x = B.roll_series(tl, px, np.array([297.0, 294.0, 1200.0]), 900, 100)
        self.assertTrue(np.isfinite(x[0])); self.assertTrue(np.isnan(x[1])); self.assertTrue(np.isfinite(x[2]))   # 100 bins valued, 99 not
        y = B.roll_series(tl, px, np.array([1200.0]), 300, 40)
        self.assertTrue(np.isfinite(y[0]))
        tl3 = np.array([0.0, 900.0, 903.0, 906.0]); self.assertTrue(np.isnan(B.roll_series(tl3, np.ones(4), np.array([900.0]), 900, 2)[0]))  # (0, 900]: 1 bin

    def test_fires(self):
        x = np.zeros(1440); x[[100, 101, 110, 116, 300]] = 5.0; x[299] = NAN
        self.assertEqual(B.fires(x, 1.0, 0.0, None)[0], [100, 116])           # 110: 10 after; 116: 16 after; 300 after a NaN
        self.assertEqual(B.fires(x, 1.0, 0.0, 85)[0], [110])                 # 100 is 15 after 85: blocked
        self.assertEqual(B.fires(x, 5.0, 0.0, None)[0], [])                  # strict
        x0 = x.copy(); x0[0] = 5.0
        self.assertEqual(B.fires(x0, 1.0, 5.0, None)[0][0], 100)
        rng = np.random.default_rng(3)
        for _ in range(10):
            y = rng.random(1440) * 3; y[rng.random(1440) < 0.05] = NAN
            self.assertEqual(B.fires(y, 2.9, 0.5, -5)[0], B.fires_loop(y, 2.9, 0.5, -5)[0])

    def test_edge_range(self):
        h = [np.linspace(0, 1, 1440)] * 3
        self.assertAlmostEqual(B.edge(h, 99.0), np.percentile(np.concatenate(h), 99.0))
        bad = np.full(1440, NAN); bad[:999] = 1.0; self.assertTrue(np.isnan(B.edge([h[0], bad], 99.0)))
        tl = np.array([0.0, 3.0, 6.0]); px = np.array([100.0, 101.0, 100.0]); hi = np.array([100.5, 102.0, 100.0]); lo = np.array([99.0, 101.0, 99.5])
        self.assertAlmostEqual(B.wrange(tl, px, hi, lo, 6.0, 900), 0.03)


if __name__ == '__main__':
    unittest.main()
