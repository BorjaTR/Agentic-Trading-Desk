"""planted tests for o1_flush_v1 (card alarms/O1_OI_FLUSH_CARD_V1.md b63f9818), from the card's words"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import o1_flush_v2 as O
NAN = float('nan')


class T(unittest.TestCase):
    def test_oi_change_coins_and_carried(self):
        o = np.full(1440, 100.0); car = np.zeros(1440)
        o[20] = 90.0
        f = O.oi_change(o, car, np.full(10, NAN), np.ones(10))
        self.assertTrue(np.isnan(f[5])); self.assertAlmostEqual(f[20], -0.1); self.assertAlmostEqual(f[30], 1 / 9); self.assertEqual(f[35], 0.0)
        car[20] = 1; f = O.oi_change(o, car, np.full(10, NAN), np.ones(10)); self.assertTrue(np.isnan(f[20]))   # a carried row: no value
        car[20] = 0; car[10] = 1; f = O.oi_change(o, car, np.full(10, NAN), np.ones(10)); self.assertTrue(np.isnan(f[20]))
        f = O.oi_change(o, np.zeros(1440), np.full(10, 100.0), np.zeros(10)); self.assertEqual(f[5], 0.0)        # D - 1's last columns

    def test_price_fall_with_contracts_flat_does_not_fire(self):
        o = np.full(1440, 100.0); f = O.oi_change(o, np.zeros(1440), np.full(10, 100.0), np.zeros(10))
        g = np.zeros(1440); g[500] = -0.05                                              # a big price fall, OI in coins unchanged
        both, ok = O.state(f, g, (-0.01, 0.01))
        self.assertFalse(both.any())

    def test_state_strict_and_side(self):
        f = np.array([-0.02, -0.01, -0.02, -0.02, NAN]); g = np.array([0.02, 0.02, 0.01, -0.03, 0.05])
        both, ok = O.state(f, g, (-0.01, 0.01))
        self.assertEqual(list(both), [True, False, False, True, False]); self.assertEqual(list(ok), [True, True, True, True, False])

    def test_entries_refractory_per_side(self):
        both = np.zeros(1440, bool); ok = np.ones(1440, bool); g = np.ones(1440)
        both[[100, 120, 131, 140]] = True; g[120] = -1
        last = {}
        self.assertEqual(O.entries(both, ok, g, False, True, last), [(100, 1), (120, -1), (131, 1)])   # 131 is 31 after 100; 140 is 9 after 131
        ok2 = ok.copy(); ok2[130] = False
        self.assertEqual(O.entries(both, ok2, g, False, True, {}), [(100, 1), (120, -1), (140, 1)])   # 131: j - 1 not valued, no fire; 140 is 40 after 100
        self.assertEqual(O.entries(both, ok, g, False, True, {1: 70}), [(120, -1), (131, 1)])        # 30 after 70: blocked
        b0 = both.copy(); b0[0] = True
        self.assertEqual(O.entries(b0, ok, g, True, True, {})[0], (100, 1))                           # D - 1 last BOTH: 0 no entry

    def test_edges_and_loop(self):
        rng = np.random.default_rng(3)
        h = [(rng.normal(0, 0.01, 1440), rng.normal(0, 0.01, 1440)) for _ in range(3)]
        e = O.edges(h, 1.0, 90.0)
        self.assertAlmostEqual(e[0], np.percentile(np.concatenate([x[0] for x in h]), 1.0))
        self.assertAlmostEqual(e[1], np.percentile(np.abs(np.concatenate([x[1] for x in h])), 90.0))
        bad = (np.full(1440, NAN), h[0][1]); self.assertIsNone(O.edges([h[0], bad], 1.0, 90.0))
        for _ in range(10):
            both = rng.random(1440) < 0.05; ok = rng.random(1440) < 0.97; g = rng.normal(size=1440)
            l0 = {1: int(rng.integers(-40, 0))} if rng.random() < 0.5 else {}
            self.assertEqual(O.entries(both, ok, g, False, True, dict(l0)), O.entries_loop(both, ok, g, False, True, dict(l0)))

    def test_roll10_and_move(self):
        x = np.ones(30); x[15] = NAN; r = O.roll10(x)
        self.assertTrue(np.isnan(r[8])); self.assertEqual(r[9], 10.0); self.assertTrue(np.isnan(r[20])); self.assertEqual(r[25], 10.0)
        tl = np.array([0.0, 600.0]); px = np.array([100.0, 110.0])
        g = O.price_move(tl, px, np.array([600.0, 599.0, 1200.0]))
        self.assertAlmostEqual(g[0], np.log(1.1)); self.assertTrue(np.isnan(g[1]));                  # no bin at or before - 1 self.assertTrue(np.isnan(O.price_move(tl, px, np.array([-1.0]))[0]))


if __name__ == '__main__':
    unittest.main()
