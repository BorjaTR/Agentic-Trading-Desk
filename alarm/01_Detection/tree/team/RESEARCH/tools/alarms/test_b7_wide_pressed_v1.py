"""planted tests for b7_wide_pressed_v1 (card alarms/B7_WIDE_AND_PRESSED_CARD_V1.md 897ade9b), from the card's words"""
import os, sys, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import b7_wide_pressed_v1 as B

NAN = float('nan')


def day(n=17280):
    v = np.arange(n, dtype=float) % 100
    return v.copy(), v.copy()


class TestEdges(unittest.TestCase):
    def test_percentiles_and_clean_days(self):
        h = [day() for _ in range(3)]
        e = B.edges(h, 95)
        self.assertAlmostEqual(e[0], np.percentile(np.concatenate([x[0] for x in h]), 95))
        self.assertAlmostEqual(e[1], np.percentile(np.abs(np.concatenate([x[1] for x in h])), 95))
        neg = (day()[0], -day()[1]); self.assertAlmostEqual(B.edges([neg, neg], 95)[1], e[1])        # |i|, not i
        bad = list(day()); bad[0] = bad[0].copy(); bad[0][:5200] = NAN                                # 69.9 pct clean: not a day
        self.assertIsNone(B.edges([day(), tuple(bad)], 95))
        ok = list(day()); ok[0] = ok[0].copy(); ok[0][:5184] = NAN                                    # 70.0 pct clean: a day
        self.assertIsNotNone(B.edges([day(), tuple(ok)], 95))
        self.assertIsNone(B.edges([], 95))


class TestRule(unittest.TestCase):
    def test_both_strict(self):
        e = (10.0, 3.0)
        s = np.array([11, 11, 10, 11, NAN, 11]); i = np.array([4, -4, 4, 3, 4, NAN])
        st, ok = B.state(s, i, e)
        self.assertEqual(list(st), [True, True, False, False, False, False])                 # edges themselves not past; sell side counts
        self.assertEqual(list(ok), [True, True, True, True, False, False])

    def test_entry_and_refractory(self):
        st = np.zeros(17280, bool); ok = np.ones(17280, bool)
        st[100:103] = True; st[280] = True; st[281] = True; st[400] = True
        self.assertEqual(B.entries(st, ok, False, True, None), [100, 400])        # 280 is 180 after 100: blocked; 281 not an entry
        st2 = st.copy(); st2[280] = False
        self.assertEqual(B.entries(st2, ok, False, True, None), [100, 281])                  # 181 after: fires
        ok2 = ok.copy(); ok2[399] = False
        self.assertEqual(B.entries(st, ok2, False, True, None), [100])                       # step before not clean: no fire
        st0 = st.copy(); st0[0] = True
        self.assertEqual(B.entries(st0, ok, True, True, None)[:1], [100])                    # D - 1 last step BOTH: 0 not an entry
        self.assertEqual(B.entries(st0, ok, False, True, -181)[:1], [0])
        self.assertEqual(B.entries(st0, ok, False, True, -180)[:1], [100])

    def test_m1(self):
        fl = np.array([5.0, -2.0, NAN, 1.0])
        self.assertEqual(B.m1_sign(fl, 1, NAN, 1), '1')                                      # 5 - 2 > 0, side buy
        self.assertEqual(B.m1_sign(fl, 1, NAN, -1), '0')
        self.assertEqual(B.m1_sign(fl, 0, -9.0, -1), '1')                                    # k = 0 uses D - 1's last step
        self.assertEqual(B.m1_sign(fl, 0, NAN, 1), '')
        self.assertEqual(B.m1_sign(fl, 3, NAN, 1), '')                                       # a missing row: no reading
        self.assertEqual(B.m1_sign(fl, 1, NAN, 0), '')

    def test_loop_equals_vec(self):
        rng = np.random.default_rng(7)
        for _ in range(10):
            st = rng.random(17280) < 0.05; ok = rng.random(17280) < 0.97; lk = int(rng.integers(-400, 0)) if rng.random() < 0.5 else None
            pst, pok = bool(rng.random() < 0.5), bool(rng.random() < 0.9)
            self.assertEqual(B.entries(st, ok, pst, pok, lk), B.entries_loop(st, ok, pst, pok, lk))


if __name__ == '__main__':
    unittest.main()
