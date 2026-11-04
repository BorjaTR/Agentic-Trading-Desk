"""LABEL_EWSD_V2 planted tests (STRATEGY-133602: out-of-range, rounding both ways, gap before the touch, WAIT never a target) plus
coverage unknown, truncated path, settled-before-gap SKIP, the path coverage reader, and one mutant per guard that must fail."""
import os, sys, types, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import label_ewsd_v2 as E

LAB = {'version': 'LABEL_EWSD_V2', 'offer_c': 4.0, 'enter_heat_c': 1.0, 'wait_heat_c': 3.0, 'dead_c': 1.5, 'hold_min': 240, 'delay_s': 6,
       'fill_step_s': 3, 'gap_s': 60, 'cost_model': 'T04 table of record (dearer of V1 and V4)', 'cost_sha16': '0' * 16}
H = 14400.0


def path(offer_up_to=0.0, offer_t=100.0, heat_up_to=0.0, heat_t=50.0):
    """one row: every offer rung up to offer_up_to touched at offer_t + k, every heat rung up to heat_up_to touched at heat_t + k"""
    OT = np.full((1, 25), np.nan); HT = np.full((1, 25), np.nan)
    for i, L in enumerate(E.LEVELS):
        if L <= offer_up_to + 1e-9:
            OT[0, i] = offer_t + i
        if L <= heat_up_to + 1e-9:
            HT[0, i] = heat_t + i
    return OT, HT


def run(OT, HT, c, gap=np.inf, known=H, mod=E):
    return mod.ewsd_v2(OT, HT, [1], [known], [c], LAB, [gap])[0][0]


def bars(te):
    """a planted PRICE path: valid prices on every bar (C12-01 counts only bars with a valid observed price)"""
    te = np.asarray(te, np.int64); one = np.ones(len(te)); return {'te_us': te, 'px': one, 'hi': one, 'lo': one}


class T(unittest.TestCase):
    def test_out_of_range(self):
        """S05-01: c 0.8 -> target 3.2 pct is above the top: OUT_OF_RANGE even when the top rung was touched (never capped)"""
        OT, HT = path(offer_up_to=2.5)
        self.assertEqual(run(OT, HT, 0.8), 'OUT_OF_RANGE')
        self.assertEqual(run(OT, HT, 0.625), 'ENTER')                              # target exactly at the top: supported

    def test_rounding_both_ways(self):
        """target rounds UP; heat is an interval: [0.1, 0.2) with c 0.14 is neither ENTER nor WAIT; with c 0.2 it is ENTER"""
        OT, HT = path(offer_up_to=1.0, heat_up_to=0.1)
        self.assertEqual(run(OT, HT, 0.14), 'UNDECIDED_BOUND')                     # heat in [0.1, 0.2): may exceed c = 0.14
        self.assertEqual(run(OT, HT, 0.2), 'ENTER')                                # heat < 0.2 <= c: ENTER for the whole interval
        OT5, HT5 = path(offer_up_to=0.5)
        self.assertNotEqual(run(OT5, HT5, 0.14), 'ENTER')                          # target 0.56 rounds UP to 0.6: 0.5 is not enough

    def test_gap_before_touch(self):
        """S05-05: a gap before the deciding touch: UNDECIDED_GAP; after it: decided; heat > 3c before the gap: SKIP settled"""
        OT, HT = path(offer_up_to=1.0, offer_t=200.0)
        self.assertEqual(run(OT, HT, 0.2, gap=100.0), 'UNDECIDED_GAP')
        self.assertEqual(run(OT, HT, 0.2, gap=300.0), 'ENTER')
        OTs, HTs = path(offer_up_to=1.0, offer_t=200.0, heat_up_to=0.8, heat_t=20.0)
        self.assertEqual(run(OTs, HTs, 0.2, gap=100.0), 'SKIP')                     # heat 0.7 > 3c = 0.6 at 26 s, before the gap
        quiet = path()
        self.assertEqual(run(*quiet, 0.2, gap=9000.0), 'UNDECIDED_GAP')             # DEAD needs the whole hold covered
        self.assertEqual(run(*quiet, 0.2), 'DEAD')
        self.assertEqual(run(*quiet, 0.2, gap=np.nan), 'UNKNOWN_PATH')
        self.assertEqual(run(*quiet, 0.2, known=3600.0), 'UNKNOWN_PATH')

    def test_wait_never_a_target(self):
        """S05-03: WAIT is annotation only: target 0 like SKIP; a WAIT side is never GOOD"""
        OT, HT = path(offer_up_to=1.0, offer_t=200.0, heat_up_to=0.4, heat_t=20.0)
        self.assertEqual(run(OT, HT, 0.2), 'WAIT')                                 # heat [0.4, 0.5) within (0.2, 0.6]
        self.assertEqual(E.decision_target(['WAIT', 'ENTER', 'SKIP', 'DEAD', 'UNDECIDED_GAP']).tolist()[:4], [0.0, 1.0, 0.0, 0.0])
        self.assertTrue(np.isnan(E.decision_target(['UNDECIDED_GAP'])[0]))
        self.assertEqual(E.outcome4_v2(['WAIT'], ['SKIP'])[0], 'BOTH_BAD'); self.assertEqual(E.outcome4_v2(['ENTER'], ['WAIT'])[0], 'RIDE_GOOD')
        self.assertEqual(E.outcome4_v2(['ENTER'], ['OUT_OF_RANGE'])[0], 'UNDECIDED')

    def test_settings_required(self):
        with self.assertRaises(ValueError):
            E.ewsd_v2(*path(), [1], [H], [0.2], {k: v for k, v in LAB.items() if k != 'cost_sha16'}, [np.inf])

    def test_path_first_gap(self):
        class Cache:
            def path(self, coin, t0, t1):
                te = np.arange(t0 + 3_000_000, t1 + 1, 3_000_000, dtype=np.int64); return bars(te[(te < t0 + 600_000_000) | (te > t0 + 700_000_000)])
        self.assertAlmostEqual(E.path_first_gap(Cache(), 'BTC', 1000.0, H, 60.0), 600.0, delta=3.0)
        class Full:
            def path(self, coin, t0, t1):
                return bars(np.arange(t0 + 3_000_000, t1 + 1, 3_000_000, dtype=np.int64))
        self.assertEqual(E.path_first_gap(Full(), 'BTC', 1000.0, H, 60.0), np.inf)
        class NaNGrid:                                                  # OX-CODE1 C12-01: a full grid of NaN prices is no coverage
            def path(self, coin, t0, t1):
                p = bars(np.arange(t0 + 3_000_000, t1 + 1, 3_000_000, dtype=np.int64)); p['px'] = np.full(len(p['te_us']), np.nan); return p
        self.assertEqual(E.path_first_gap(NaNGrid(), 'BTC', 1000.0, H, 60.0), 0.0)

    def test_mutants(self):
        src = open(E.__file__).read()
        muts = [("return np.where(x > TOP + EPS, -1, np.minimum(i, len(LEVELS) - 1))", "return np.minimum(i, len(LEVELS) - 1)", 'test_out_of_range'),
                ("cls_r = np.where(hi <= e + EPS, 'ENTER'", "cls_r = np.where(lo <= e + EPS, 'ENTER'", 'test_rounding_both_ways'),
                ("np.where(gap < settle, 'UNDECIDED_GAP', cls)", "np.where(gap < -1, 'UNDECIDED_GAP', cls)", 'test_gap_before_touch'),
                ("rg = ride == 'ENTER'; fg = fade == 'ENTER'", "rg = np.isin(ride, ('ENTER', 'WAIT')); fg = np.isin(fade, ('ENTER', 'WAIT'))", 'test_wait_never_a_target')]
        for old, new, name in muts:
            self.assertEqual(src.count(old), 1, old)
            m = types.ModuleType('ewsd_mut'); exec(compile(src.replace(old, new), 'ewsd_mut', 'exec'), m.__dict__)
            saved = E.__dict__.copy()
            try:
                for k in ('ewsd_v2', 'up_index', 'outcome4_v2', 'decision_target', 'interval', 'first_above'):
                    setattr(E, k, getattr(m, k))
                r = unittest.TextTestRunner(stream=open(os.devnull, 'w')).run(T(name)); self.assertFalse(r.wasSuccessful(), 'mutant not caught: ' + new)
            finally:
                for k in ('ewsd_v2', 'up_index', 'outcome4_v2', 'decision_target', 'interval', 'first_above'):
                    setattr(E, k, saved[k])


if __name__ == '__main__':
    unittest.main()
