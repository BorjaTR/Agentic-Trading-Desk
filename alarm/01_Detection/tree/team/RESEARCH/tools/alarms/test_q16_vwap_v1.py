"""tests for q16_vwap_v1, planted from the card's words (Q16 d6ddf4a2 section 4) and a second plain computation of the VWAP gap"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import q16_vwap_v1 as P, alarm_view_v1 as V
M = V.M


def minute(bins):
    """bins: list of (buy, sell, px) of one minute -> the dict bin_minutes gives for that minute (1 coin, 1 minute)"""
    b = {'buy': np.array([x[0] for x in bins], float), 'sell': np.array([x[1] for x in bins], float), 'px': np.array([x[2] for x in bins], float)}
    pb = P.per_bin(b, 0, len(bins)); return {k: np.array([[v.sum()]]) for k, v in pb.items()}


class T(unittest.TestCase):
    def test_vwap(self):
        m = minute([(500.0, 0, 100.0), (500.0, 0, 101.0), (1000.0, 0, 102.0)])
        vb, vs = P.vwaps(m); exp = 2000.0 / (500 / 100 + 500 / 101 + 1000 / 102)
        self.assertAlmostEqual(vb[0, 0], exp); self.assertTrue(np.isnan(vs[0, 0]))                      # dollar-weighted; no sells
        self.assertTrue(np.isnan(P.vwaps(minute([(499.0, 0, 100.0), (500.0, 0, 100.0), (0.5, 0, 100.0)]))[0][0, 0]))   # 1,000 USD floor
        self.assertTrue(np.isnan(P.vwaps(minute([(800.0, 0, 100.0), (800.0, 0, 100.0)]))[0][0, 0]))   # 2 bins not valued
        self.assertAlmostEqual(P.vwaps(minute([(499.0, 0, 100.0), (500.0, 0, 100.0), (1.0, 0, 100.0)]))[0][0, 0], 100.0)   # 1,000 exactly: valued
        gb, gs = P.gaps(vb, vs, np.array([[100.0]])); self.assertAlmostEqual(gb[0, 0], 1e4 * (exp / 100 - 1))
        self.assertTrue(np.isnan(P.gaps(vb, vs, np.array([[np.nan]]))[0][0, 0]))                         # a stale mid: no value

    def test_state(self):
        r = np.random.default_rng(3); N = 4 * M; built = np.ones(4, bool)
        gb = r.normal(0, 1, (1, N)); gs = r.normal(0, 1, (1, N))
        eb = np.percentile(np.concatenate([gb[0, :M], gb[0, M:2 * M]]), 99.5); es = np.percentile(np.concatenate([gs[0, :M], gs[0, M:2 * M]]), 99.5)
        t = 2 * M + 100; gb[0, t] = eb; gs[0, t] = -9                                                    # at the edge: strict, no hold
        t2 = 2 * M + 200; gb[0, t2] = 2 * eb; gs[0, t2] = 3 * es                                        # both: the larger ratio, sells
        hold, ok, side, g, e = P.state(gb, gs, built)
        self.assertAlmostEqual(e[0, t2], es); self.assertFalse(hold[0, t]); self.assertEqual(side[0, t2], -1)
        self.assertTrue(ok[0, t]); self.assertFalse(ok[0, 10])                                          # day 0: no edges yet

    def test_mid_before(self):
        """the main gap uses the mid of m - 60 (lag 1), the beside the mean of m - 60 and m"""
        mid = np.array([[100.0, 100.0, 110.0]]); vb = np.full((1, 3), 110.0); vs = np.full((1, 3), np.nan)
        g_main = P.gaps(vb, vs, V.lag(mid, 1))[0]; g_bes = P.gaps(vb, vs, (V.lag(mid, 1) + mid) / 2)[0]
        self.assertAlmostEqual(g_main[0, 2], 1000.0); self.assertAlmostEqual(g_bes[0, 2], 1e4 * (110 / 105 - 1))

    def test_loop_equal(self):
        """a plain loop over bins and minutes gives the same VWAP gap as minute_sums + vwaps"""
        r = np.random.default_rng(5); t0 = 1000.0; te = np.sort(r.uniform(t0 - 30, t0 + 600, 400)); buy = r.choice([0.0, 300.0, 900.0], 400)
        px = 100 + r.normal(0, 1, 400); b = {'buy': buy, 'sell': np.zeros(400), 'px': px, 'te': te * 1e6}
        pb = P.per_bin(b, 0, 400); ms = V.minute_sums(te, np.array([pb[k] for k in pb]), t0); m = {k: ms[i][None, :M] for i, k in enumerate(pb)}
        vb, _ = P.vwaps(m)
        for j in range(0, 11):
            sel = (te > t0 + 60 * (j - 1)) & (te <= t0 + 60 * j) & (buy > 0)
            B = buy[sel].sum(); exp = B / (buy[sel] / px[sel]).sum() if (B >= 1000 and sel.sum() >= 3) else np.nan
            np.testing.assert_allclose(vb[0, j], exp, rtol=1e-12, equal_nan=True)


if __name__ == '__main__':
    unittest.main()
