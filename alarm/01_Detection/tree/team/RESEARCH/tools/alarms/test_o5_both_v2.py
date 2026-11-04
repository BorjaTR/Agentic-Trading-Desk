"""tests for o5_both_v2: the rule on alarm_view equals o5_both_v1's tested functions (b_valued, edge, state, roll10) on planted days"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import o5_both_v2 as P, o5_both_v1 as OLD, alarm_view_v1 as V
M = V.M


class T(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(9); nd = 5; N = nd * M; C = 2
        self.built = np.array([True, True, False, True, True])
        s04 = r.normal(0, 0.3, (C, N)); s03 = (r.random((C, N)) < 0.02).astype(float); h = r.normal(0, 0.4, (C, N)); liq = r.lognormal(8, 2, (C, N))
        s03[:, ::97] = np.nan; h[:, ::31] = np.nan; liq[:, ::53] = np.nan
        for x in (s04, s03, h, liq):
            x[:, 2 * M:3 * M] = np.nan
        s04[0, 3 * M + 400] = -9.0; h[0, 3 * M + 395] = -9.0; s03[0, 3 * M + 390:3 * M + 401] = 0.0
        h[1, 3 * M + 600:3 * M + 620] = np.nan                                  # a window with no h: not VALUED
        self.s04, self.s03, self.h, self.liq = s04, s03, h, liq

    def test_equal_v1(self):
        s03c = P.carried(self.s03); b = P.b_valued(self.s04, s03c); hold, ok, eb, eh = P.states(b, self.h, self.built)
        days = np.flatnonzero(self.built)
        for d in (3, 4):
            for i in range(2):
                sl = slice(d * M, (d + 1) * M)
                sp = s03c[i, d * M - 10:d * M] if self.built[d - 1] else np.ones(10)
                bd = OLD.b_valued(self.s04[i, sl], s03c[i, sl], sp)
                np.testing.assert_array_equal(np.isnan(b[i, sl]), np.isnan(bd)); np.testing.assert_array_equal(b[i, sl][np.isfinite(bd)], bd[np.isfinite(bd)])
                hist = [e for e in days if e < d]
                bh = lambda e: P.b_valued(self.s04, s03c)[i, e * M:(e + 1) * M]
                e_b = OLD.edge([bh(e) for e in hist]); e_h = OLD.edge([self.h[i, e * M:(e + 1) * M] for e in hist])
                ehp = OLD.edge([self.h[i, e * M:(e + 1) * M] for e in days if e < d - 1]) if self.built[d - 1] else np.nan
                hp = self.h[i, d * M - 9:d * M] if self.built[d - 1] else np.full(9, np.nan)
                h2 = np.concatenate([hp, self.h[i, sl]]); eh2 = np.concatenate([np.full(9, ehp), np.full(M, e_h)])
                ho, oo = OLD.state(bd, e_b, h2, eh2)
                np.testing.assert_array_equal(hold[i, sl], ho); np.testing.assert_array_equal(ok[i, sl], oo)
        self.assertTrue(hold[0, 3 * M + 400]); self.assertFalse(ok[1, 3 * M + 615])

    def test_m1(self):
        m = P.m1_of(self.liq, self.built); i, d = 1, 4
        rp = OLD.roll10(self.liq[i, (d - 1) * M:d * M]); rp = rp[np.isfinite(rp)]; ref = np.percentile(rp, 90)
        l2 = np.concatenate([self.liq[i, d * M - 9:d * M], self.liq[i, d * M:(d + 1) * M]]); r10 = OLD.roll10(l2)[9:]
        exp = np.where(np.isfinite(r10), (r10 > ref).astype(float), np.nan)
        np.testing.assert_array_equal(m[i, d * M:(d + 1) * M], exp)
        self.assertTrue(np.isnan(m[i, 3 * M:4 * M]).all())                     # day 2 not built: no M1 on day 3

    def test_m1_own_minutes(self):
        liq = np.random.default_rng(4).lognormal(8, 1, (1, 3 * M)); liq[0, M - 9:M] = 1e12          # day 0's tail: day 1's first sums only
        m = P.m1_of(liq, np.ones(3, bool))
        rp = OLD.roll10(liq[0, M:2 * M]); ref = np.percentile(rp[np.isfinite(rp)], 90)
        r10 = OLD.roll10(liq[0, 2 * M - 9:3 * M])[9:]
        np.testing.assert_array_equal(m[0, 2 * M:], (r10 > ref).astype(float))

    def test_carried(self):
        s = np.array([[0.0, np.nan, 0.0]]); self.assertEqual(list(P.carried(s)[0]), [0.0, 1.0, 0.0])


if __name__ == '__main__':
    unittest.main()
