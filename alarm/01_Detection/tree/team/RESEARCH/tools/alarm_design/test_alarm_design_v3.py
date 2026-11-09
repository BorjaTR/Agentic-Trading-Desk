"""test_alarm_design_v3.py: the tests of alarm_design_v3.py (planted, seconds). Owner ALARM. New edition by SCOUT for the clean release
(30 Oct 2026). Old file: test_alarm_design_v2.py bc9c40a838f40329 (the tests of alarm_design_v2.py), never edited. Its tests run here as
written against alarm_design_v3 (only the import changed); class LabDaysFromCaller adds the new path code's tests (no machine default for
the lab days: LabSource and the run command).
Run: cd <this folder> && python3 -B test_alarm_design_v3.py"""
import json, os, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_design_v3 as AD

D1, D2, D3 = '20251014', '20251015', '20251016'
COINS = ['AAA', 'BBB']


class Plant:
    """a planted source: codes[(code, day)] = (ncoins, NB) on the 5 s clock; missing = NaN"""

    def __init__(self, codes=None, events=None, days=(D1, D2, D3)):
        self.c = codes or {}; self.events = events or {}; self.days = set(days)

    def coins(self, d):
        return list(COINS) if d in self.days else []

    def code(self, code, d, coins):
        x = self.c.get((code, d)); return np.full((len(coins), AD.NB), np.nan) if x is None else np.array(x, float)

    def market(self, code, d):
        x = self.c.get((code, d, 'M')); return np.zeros(AD.NB) if x is None else np.array(x, float)

    def price(self, d, coins):
        return np.full((len(coins), AD.NB), 100.0)

    def bins(self, d, coin):
        g = AD.day0(d) + 3 * np.arange(1, 28801); px = 100 + np.sin(np.arange(28800) / 50.0)
        return (g * 1_000_000).astype(np.int64), px


def zeros():
    return np.zeros((len(COINS), AD.NB))


def dfn(**kw):
    d = {'id': 'T', 'version': '1', 'claim': {'one_line': 'test', 'type': 'PREDICT', 'footprint_s': 15}, 'window': {'first': D2, 'last': D2}, 'grid_s': 5,
         'inputs': {'x': {'op': 'raw', 'code': 'X'}, 'y': {'op': 'raw', 'code': 'Y'}, 'liq_s': {'op': 'raw', 'code': 'A1.S02'}},
         'conditions': [{'name': 'sh', 'lhs': 'x', 'cmp': '>=', 'rhs': 1, 'role': 'shared'},
                        {'name': 'cl', 'lhs': 'y', 'cmp': '>=', 'rhs': 1, 'role': 'claim'}],
         'fire': {'onset': True, 'refractory_s': 600, 'side': {'input': 'x', 'sign': 1}},
         'truth': [{'name': 'f', 'kind': 'forced_usd', 'start_s': 0, 'end_s': 60, 'dir': 'same', 'floor_usd': 0}],
         'primary': 'f', 'base': {'match_on': [], 'k': 3, 'scope': 'coin-day', 'seed': 1, 'caliper': 1.0},
         'mirror': {'X': '-', 'Y': 'Y', 'A1.S01': 'A1.S02', 'A1.S02': 'A1.S01'}, 'oi_usd': False}
    d.update(kw); d['_sha16'] = '0' * 16; d['_path'] = 'T.json'
    return d


def setxy(x_rows, y_rows, day=D2, coin=0, codes=None):
    codes = codes if codes is not None else {}
    X = codes.setdefault(('X', day), zeros()); Y = codes.setdefault(('Y', day), zeros())
    for a, b, v in x_rows:
        X[coin, a:b] = v
    for a, b, v in y_rows:
        Y[coin, a:b] = v
    return codes


class T(unittest.TestCase):
    def fires(self, d, src, day=D2):
        ctx = AD.Ctx(d, src, day, COINS, {}); f, *_ = AD.find_fires(ctx, {}); return [(i, r - ctx.i0) for i, r in f], ctx

    def test_onset_and_refractory(self):
        c = setxy([(100, 200, 1), (210, 300, 1)], [(100, 300, 1)])
        f, _ = self.fires(dfn(), Plant(c))
        self.assertEqual(f, [(0, 100)])                    # 210 is a new onset but inside 600 s (120 rows) of 100
        c = setxy([(100, 200, 1), (300, 400, 1)], [(0, 1000, 1)])
        f, _ = self.fires(dfn(), Plant(c)); self.assertEqual(f, [(0, 100), (0, 300)])

    def test_refractory_crosses_midnight(self):
        c = setxy([(AD.NB - 10, AD.NB, 1)], [(AD.NB - 10, AD.NB, 1)], day=D1)
        setxy([(5, 50, 1)], [(5, 50, 1)], day=D2, codes=c)
        d = dfn(); d['window'] = {'first': D2, 'last': D2}
        recs, sets = AD.run(d, D2, D2, Plant(c), warm=1, mode='fires', log=lambda x: None)
        self.assertIsNone(recs.get('FIRE'))              # D1 23:59:10 fired; D2 00:00:25 is under 600 s later

    def test_prefix_no_lookahead(self):
        c = setxy([(100, 200, 1)], [(100, 200, 1)])
        X = c[('X', D2)]; X[1, 101:] = 5.0                # coin 1: nothing until row 101
        n, bad = AD.prefix_check(dfn(), Plant(c), D2); self.assertEqual(bad, 0); self.assertGreater(n, 0)

    def test_base_shares_everything_but_the_claim(self):
        c = setxy([(0, AD.NB, 1)], [(5000, 9000, 1)]); c[('X', D2)][1, :] = -1.0   # claim true 5000-9000: one fire, the rest claim-true non-fires
        d = dfn(); ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, sh, cl, kn, side = AD.find_fires(ctx, {})
        rows = AD.base_rows(ctx, sh, cl, kn, side, f, 10 ** 6, np.random.default_rng(1))
        self.assertTrue(rows)
        for i, r in rows:
            self.assertTrue(sh[i, r] and not cl[i, r])      # shared true, claim false: always
        self.assertTrue(all(i == 0 for i, r in rows))        # coin 1 (x = -1, side -1) never meets the shared condition

    def test_label_starts_after_t(self):
        c = setxy([(100, 101, 1)], [(100, 101, 1)])
        L = c.setdefault(('A1.S02', D2), zeros()); L[0, :] = 0; L[0, 100] = 1e6      # the fire's own row: never in its label
        d = dfn(); ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, *_, side = AD.find_fires(ctx, {})
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([side[i, r] for i, r in f]))
        self.assertEqual(lv['value'][0], 0.0); self.assertEqual(lv['pre'][0], 1e6)
        L[0, 101] = 50.0; L[0, 102] = 50.0                  # row 101 covers (t, t + 5]: counted; after +6 s only row 102
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); lv = AD.label_values(ctx, d['truth'][0], f, np.array([1]))
        self.assertEqual(lv['value'][0], 100.0); self.assertAlmostEqual(lv['after6'][0], 0.5)

    def test_label_side(self):
        c = setxy([(100, 101, -1)], [(100, 101, 1)])
        c[('A1.S02', D2)] = zeros(); c[('A1.S01', D2)] = zeros(); c[('A1.S01', D2)][0, 105] = 7.0
        d = dfn(); d['inputs']['ax'] = {'op': 'abs', 'of': 'x'}; d['conditions'][0]['lhs'] = 'ax'
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, *_, side = AD.find_fires(ctx, {})
        self.assertEqual(side[f[0]], -1)                    # a down push: the same-side label reads LONG liquidations (A1.S01)
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([-1])); self.assertEqual(lv['value'][0], 7.0)

    def test_sign_plant(self):
        c = setxy([(100, 200, 1)], [(100, 200, 1)])
        X = c[('X', D2)]; X[1, 300:400] = -1.0; c[('Y', D2)][1, 300:400] = 1
        d = dfn(); d['conditions'][0] = {'name': 'sh', 'lhs': 'ax', 'cmp': '>=', 'rhs': 1, 'role': 'shared'}
        d['inputs']['ax'] = {'op': 'abs', 'of': 'x'}
        n, same, flip = AD.sign_check(d, Plant(c), D2); self.assertEqual((n, same, flip), (2, True, True))
        d['mirror'] = {'Y': 'Y'}                            # a mirror map that forgets X: sides do not flip -> the check must say so
        n, same, flip = AD.sign_check(d, Plant(c), D2); self.assertFalse(flip)

    def test_accel(self):
        c = setxy([(0, AD.NB, 1)], [])
        L = c.setdefault(('A1.S02', D2), zeros()); L[0, 200:204] = [10, 20, 30, 40]
        d = dfn(); d['inputs']['acc'] = {'op': 'accel', 'of': 'liq_s', 'n': 3}
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); a = ctx.get('acc')[0, ctx.i0:]
        self.assertEqual(list(np.flatnonzero(a == 1)), [203])

    def test_own_pct_uses_earlier_days_only(self):
        c = {}
        for k, dd in enumerate(AD.days_between('20251001', D2)):
            X = zeros(); X[:, :] = k; c[('X', dd)] = X
        c[('X', D2)][:, :] = 1e9                              # D itself must never move D's edge
        d = dfn(); d['inputs']['e'] = {'op': 'own_pct', 'of': 'x', 'q': 100}
        src = Plant(c, days=AD.days_between('20251001', D3)); hist = {}
        for dd in AD.days_between('20251001', D2):
            ctx = AD.Ctx(d, src, dd, COINS, hist); e = ctx.get('e'); ctx.push_hist(AD.keep_days(d))
        self.assertTrue(np.all(e[:, ctx.i0:2 * ctx.i0] < 100))

    def test_pick_and_thr_input(self):
        c = setxy([(100, 101, 1)], [(100, 101, 1)]); c[('A1.S02', D2)] = zeros(); c[('A1.S01', D2)] = zeros() + 3.0
        c[('A1.S02', D2)][0, 101:113] = 10.0                       # 120 USD in the next minute on the up side
        d = dfn(); d['inputs']['dom'] = {'op': 'raw', 'code': 'X'}; d['inputs']['liq_l'] = {'op': 'raw', 'code': 'A1.S01'}
        d['inputs']['pk'] = {'op': 'pick', 'if': 'dom', 'pos': 'liq_s', 'neg': 'liq_l'}; d['inputs']['band'] = {'op': 'raw', 'code': 'B'}
        c[('B', D2)] = zeros() + 100.0
        d['truth'][0]['thr_input'] = 'band'
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); pk = ctx.get('pk')[:, ctx.i0:]
        self.assertTrue(np.isnan(pk[0, 0]) and pk[0, 100] == 0.0)  # x = 0 -> no side; x = 1 -> the short-liquidation series
        d['inputs']['pk2'] = {'op': 'pick', 'if': 'dom', 'pos': 'liq_s', 'neg': 'liq_l', 'tie': 'neg'}
        self.assertEqual(ctx.get('pk2')[0, ctx.i0], 3.0)         # tie = 'neg': sign 0 reads the neg series
        f, *_, side = AD.find_fires(ctx, {}); lv = AD.label_values(ctx, d['truth'][0], f, np.array([1]))
        self.assertEqual(lv['value'][0], 120.0); self.assertEqual(lv['hit'][0], 1.0)
        c[('B', D2)][:] = 121.0; ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); lv = AD.label_values(ctx, d['truth'][0], f, np.array([1]))
        self.assertEqual(lv['hit'][0], 0.0)

    def test_event_label_cover(self):
        c = setxy([(100, 101, 1), (5000, 5001, 1)], [(100, 101, 1), (5000, 5001, 1)])
        ev = {'AAA': (np.array([AD.day0(D2) + 600.0]), np.array([1]))}
        d = dfn(); d['truth'] = [{'name': 'e', 'kind': 'event_within', 'events': 'E', 'start_s': 0, 'end_s': 3600, 'dir': 'same'}]; d['primary'] = 'e'
        src = Plant(c, events={'E': ev}); ctx = AD.Ctx(d, src, D2, COINS, {}); f, *_, side = AD.find_fires(ctx, {})
        with self.assertRaises(ValueError):
            AD.label_values(ctx, d['truth'][0], f, np.array([1, 1]))
        d['events_cover'] = {'E': [D2, D2]}; ctx = AD.Ctx(d, src, D2, COINS, {})
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([1, 1]))
        self.assertEqual(lv['hit'][0], 1.0); self.assertEqual(lv['hit'][1], 0.0)
        d['events_cover'] = {'E': [D1, D1]}; ctx = AD.Ctx(d, src, D2, COINS, {})
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([1, 1]))
        self.assertTrue(np.all(np.isnan(lv['hit'])))           # a day the list does not cover is unknown, never 'no event'

    def test_edge_ops(self):
        c = {('P', D2): zeros()}; P = c[('P', D2)]; P[0, :] = 100.0; P[0, 5000] = 105.0; P[0, 6000] = 95.0
        d = dfn(); d['inputs'].update({'px': {'op': 'raw', 'code': 'P'}, 'hi': {'op': 'prior_max', 'of': 'px', 'w_s': 3600},
                                       'lo': {'op': 'prior_min', 'of': 'px', 'w_s': 3600}, 'up': {'op': 'sub', 'a': 'px', 'b': 'hi'},
                                       'u': {'op': 'pospart', 'of': 'up'}, 'dn': {'op': 'sub', 'a': 'px', 'b': 'lo'}, 'dd': {'op': 'negpart', 'of': 'dn'}})
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); i0 = ctx.i0; g = lambda k: ctx.get(k)[0, i0:]
        self.assertEqual(g('hi')[5000], 100.0)             # the prior high excludes the row itself
        self.assertEqual(g('u')[5000], 5.0); self.assertEqual(g('u')[5001], 0.0); self.assertEqual(g('hi')[5001], 105.0)
        self.assertEqual(g('dd')[6000], -5.0); self.assertEqual(g('lo')[6000], 100.0)

    def test_roll_max_vs_loop(self):
        rng = np.random.default_rng(3); x = rng.normal(size=(2, 300)); x[0, 50:60] = np.nan; x[1, 100:200] = np.nan
        for n in (1, 2, 5, 12, 60):
            for prior in (False, True):
                m = AD.roll_max(x, n, prior)
                for i in range(2):
                    for k in range(300):
                        lo, hi = (k - n, k) if prior else (k - n + 1, k + 1)
                        if lo < 0:
                            self.assertTrue(np.isnan(m[i, k])); continue
                        w = x[i, lo:hi]; w = w[np.isfinite(w)]
                        self.assertTrue(np.isnan(m[i, k]) if not len(w) else m[i, k] == w.max(), (n, prior, i, k))

    def test_event_ops(self):
        c = {('P', D2): zeros()}; P = c[('P', D2)]; P[0, :] = 100.0; P[0, 1010:1020] = 90.0; P[0, 1020:] = 95.0
        t_ev = AD.day0(D2) + 5 * 1000
        ev = {'AAA': (np.array([t_ev]), np.array([-1]))}
        d = dfn(); d['events_cover'] = {'E': [D2, D2]}
        d['inputs'].update({'px': {'op': 'raw', 'code': 'P'}, 'since': {'op': 'ev_since', 'events': 'E', 'w_s': 3600},
                            'sd': {'op': 'ev_side', 'events': 'E', 'w_s': 3600}, 'v0': {'op': 'ev_value', 'events': 'E', 'of': 'px', 'w_s': 3600},
                            'ext': {'op': 'ext_since_ev', 'events': 'E', 'of': 'px', 'w_s': 3600}})
        ctx = AD.Ctx(d, Plant(c, events={'E': ev}), D2, COINS, {}); i0 = ctx.i0; g = lambda k: ctx.get(k)[0, i0:]
        self.assertTrue(np.isnan(g('since')[999])); self.assertEqual(g('since')[1000], 0.0); self.assertEqual(g('since')[1100], 500.0)
        self.assertEqual(g('sd')[1100], -1.0); self.assertEqual(g('v0')[1100], 100.0)
        self.assertEqual(g('ext')[1005], 100.0); self.assertEqual(g('ext')[1015], 90.0); self.assertEqual(g('ext')[1500], 90.0)
        self.assertTrue(np.isnan(g('since')[1000 + 721]))   # beyond w_s
        d['inputs']['emax'] = {'op': 'ext_since_ev', 'events': 'E', 'of': 'px', 'w_s': 3600, 'mode': 'max'}
        self.assertEqual(ctx.get('emax')[0, i0 + 1500], 100.0)
        self.assertTrue(np.all(np.isnan(ctx.get('since')[1])))
        d['events_cover'] = {'E': [D1, D1]}; ctx = AD.Ctx(d, Plant(c, events={'E': ev}), D2, COINS, {})
        self.assertTrue(np.all(np.isnan(ctx.get('since')[0, ctx.i0:2 * ctx.i0])))   # outside the cover: unknown

    def test_trail_pct_before_t(self):
        c = setxy([(0, AD.NB, 1)], []); c[('X', D2)][0, 1200:] = 1e9      # from minute 100 on: huge
        d = dfn(); d['inputs']['tp'] = {'op': 'trail_pct', 'of': 'x', 'q': 100, 'w_s': 3600, 'min_n': 1}
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); tp = ctx.get('tp')[0, ctx.i0:]
        self.assertEqual(tp[12 * 100], 1.0)               # at minute 100 only earlier minutes count
        self.assertEqual(tp[12 * 101], 1e9)

    def test_match_exact_and_caliper(self):
        F = {'coin': np.array(['A', 'A'], object), 't': np.array([AD.day0(D2) + 100.0, AD.day0(D2) + 200.0]),
             'hour_block4': np.array([0.0, 0.0]), 'v': np.array([1.0, 9.0])}
        B = {'coin': np.array(['A'] * 4, object), 't': np.array([AD.day0(D2) + x for x in (1e3, 2e3, 3e3, 4e4)]),
             'hour_block4': np.array([0.0, 0.0, 0.0, 2.0]), 'v': np.array([1.1, 8.9, 5.0, 1.0])}
        s = AD.match(F, B, ['v'], 'coin-day', 1, 0.3, np.random.default_rng(0))
        self.assertEqual([list(x) for x in s], [[0], [1]])  # nearest within the caliper; row 3 (other hour block) never used

    def test_match_time30_other_coins(self):
        t0 = AD.day0(D2)
        F = {'coin': np.array(['A'], object), 't': np.array([t0 + 100.0]), 'hour_block4': np.array([0.0]), 'v': np.array([1.0])}
        B = {'coin': np.array(['B', 'C'], object), 't': np.array([t0 + 200.0, t0 + 4000.0]), 'hour_block4': np.array([0.0, 0.0]), 'v': np.array([1.0, 1.0])}
        s = AD.match(F, B, ['v'], 'time30', 2, 1.0, np.random.default_rng(0))
        self.assertEqual(list(s[0]), [0])                    # another coin in the same 30 min; the one an hour later is not

    def test_seal_refused(self):
        with self.assertRaises(PermissionError):
            AD.refuse_sealed(['20260401'], '20260401')
        AD.refuse_sealed(['20260331'], '20260401')
        self.assertEqual(AD.seal_day(), '20260401')        # follows the one setting (lab3.law 0802358832de2b23: research to 20260331, SCO-A179; was 20260601)

    def test_claim_type_required(self):
        p = os.path.join(tempfile.mkdtemp(), 'd.json'); d = dfn(); d.pop('_sha16'); d.pop('_path')
        d['claim'].pop('type'); json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)
        d['claim']['type'] = 'DETECT'; d['claim'].pop('footprint_s'); json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)

    def test_detect_needs_present_label(self):
        p = os.path.join(tempfile.mkdtemp(), 'd.json'); d = dfn(); d.pop('_sha16'); d.pop('_path')
        d['claim']['type'] = 'DETECT'; json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)                                    # a future label cannot grade a DETECT claim
        d['truth'][0]['when'] = 'present'; json.dump(d, open(p, 'w')); AD.load_def(p)
        d['claim']['type'] = 'PREDICT'; json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)

    def test_present_label_window(self):
        c = setxy([(100, 101, 1)], [(100, 101, 1)]); L = c.setdefault(('A1.S02', D2), zeros()); L[0, 95] = 7.0; L[0, 100] = 5.0; L[0, 101] = 99.0
        d = dfn(); d['truth'][0]['when'] = 'present'; d['truth'][0]['end_s'] = 30
        ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, *_, side = AD.find_fires(ctx, {})
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([1])); self.assertEqual(lv['value'][0], 12.0)   # rows 95..100: never row 101 (after t)

    def test_definition_rules(self):
        p = os.path.join(tempfile.mkdtemp(), 'd.json'); d = dfn(); d.pop('_sha16'); d.pop('_path')
        d['truth'][0]['start_s'] = -5; json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)
        d['truth'][0]['start_s'] = 0; d['primary'] = 'nope'; json.dump(d, open(p, 'w'))
        with self.assertRaises(ValueError):
            AD.load_def(p)

    def test_gap_and_verdict(self):
        y = np.array([1.0, 1.0, 0.0, 1.0]); by = np.array([0.0, 0.0, 0.0, 0.0])
        sets = [np.array([0]), np.array([1]), np.array([2]), np.array([3])]
        ws, wm, nu, fs, bs, d = AD.gap_by_wave(y, sets, by, np.array([0, 0, 1, 2]), np.ones(4, bool))
        self.assertEqual(list(wm), [1.0, 0.0, 1.0]); self.assertEqual(nu, 4)
        self.assertEqual(AD.verdict(0.1, 7, 9, 0.05), 'TRUE_FOR_REFERENCE'); self.assertEqual(AD.verdict(0.1, 6, 9, 0.05), 'UNSURE')
        self.assertEqual(AD.verdict(0.1, 7, 9, -0.01), 'UNSURE')
        self.assertEqual(AD.verdict(-0.1, 2, 9, -0.01, pooled_hi=0.3), 'UNSURE')        # wide: never a kill (S07 rule 5)
        self.assertEqual(AD.verdict(-0.1, 2, 9, -0.01, pooled_hi=0.02), 'NOT_SUPPORTED') # precise and under the frozen effect

    def test_card_build_check_split(self):
        t0 = AD.day0('20251015'); t1 = AD.day0('20260315')
        F = {'coin': np.array(['A', 'A'], object), 't': np.array([t0, t1], float), 'side': np.array([1, 1]),
             'lab_f_hit': np.array([1.0, 0.0]), 'lab_f_after6': np.array([1.0, 0.0]), 'lab_f_value': np.array([1.0, 0.0]), 'oi_usd': np.array([1.0, 1.0])}
        B = {'lab_f_hit': np.array([0.0, 1.0]), 'lab_f_after6': np.array([0.0, 1.0]), 'lab_f_value': np.array([0.0, 1.0])}
        d = dfn(); d['window'] = {'first': '20251001', 'last': '20260331'}
        sets = {'FAIR': [np.array([0]), np.array([1])]}
        L, summ = AD.card(d, F, {'FAIR': B}, sets, n_draw=50, windows={'build_months': ['202510'], 'check_months': ['202603'], '_sha16': 'x'})
        line = [l for l in L if 'BUILD' in l and 'NOT read' in l][0]
        self.assertIn('BUILD 202510..202510 pooled gap +1.000', line)
        self.assertFalse(any(l.strip().startswith('202603') for l in L))    # a CHECK month gets no row

    def test_load_events_filter(self):
        p = os.path.join(tempfile.mkdtemp(), 'E.tsv')
        open(p, 'w').write('coin\tt\tside\twarm_up\nA\t10\t1\t0\nA\t20\t-1\t1\n')
        ev, sh = AD.load_events([p + '::warm_up=0']); self.assertEqual(list(ev['A'][0]), [10.0])
        ev, sh = AD.load_events([p]); self.assertEqual(len(ev['A'][0]), 2)

    def test_v2_seal_refusal_propagates(self):
        class Refuse(AD.LabSource):
            def __init__(self):
                self._c = {}; self.events = {}

                class R:
                    def read(self, *a, **k):
                        raise PermissionError('BLIND')

                    def step(self, *a, **k):
                        return 5
                self.R = R()
        with self.assertRaises(PermissionError):
            Refuse().code('A1.S01', D2, COINS)
        with self.assertRaises(PermissionError):
            Refuse().market('A2.S05', D2)

    def test_v2_zero_grid_refused(self):
        p = os.path.join(tempfile.mkdtemp(), 'd.json'); d = dfn(); d.pop('_sha16'); d.pop('_path')
        for g in (0, -5, 7, True, 5.0):
            d['grid_s'] = g; json.dump(d, open(p, 'w'))
            with self.assertRaises(ValueError):
                AD.load_def(p)

    def test_v2_base_excludes_only_after_past_fires(self):
        c = setxy([(0, AD.NB, 1)], [(5000, 9000, 1)]); c[('X', D2)][1, :] = -1.0
        d = dfn(); ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, sh, cl, kn, side = AD.find_fires(ctx, {})
        # plant a fire at row 3000 of coin 0 (claim true for one row only): rows 2000-2999 are BEFORE it and must stay candidates
        c[('Y', D2)][0, 3000] = 1; ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); f, sh, cl, kn, side = AD.find_fires(ctx, {})
        rows = AD.base_rows(ctx, sh, cl, kn, side, f, 10 ** 6, np.random.default_rng(1)); rr = {r - ctx.i0 for i, r in rows if i == 0}
        self.assertIn(2990, rr)                              # 50 s before a fire: a candidate (no future exclusion)
        self.assertNotIn(3010, rr)                           # 50 s after it: excluded
        self.assertIn(3000 + 361, rr)                        # 1805 s after it: a candidate again

    def test_v2_nothing_read_after_last(self):
        c = setxy([(AD.NB - 5, AD.NB - 4, 1)], [(AD.NB - 5, AD.NB - 4, 1)]); c[('A1.S02', D2)] = zeros(); c[('A1.S02', D3)] = zeros() + 1.0
        d = dfn(); ctx = AD.Ctx(d, Plant(c), D2, COINS, {}); ctx.read_last = D2; f, *_, side = AD.find_fires(ctx, {})
        lv = AD.label_values(ctx, d['truth'][0], f, np.array([1]))
        self.assertTrue(np.isnan(lv['value'][0]))           # its 60 s label crosses midnight into a day after the run: NOT KNOWN
        ctx.read_last = None; lv = AD.label_values(ctx, d['truth'][0], f, np.array([1])); self.assertTrue(np.isfinite(lv['value'][0]))

    def test_v2_unmatched_reasons(self):
        t0 = AD.day0(D2)
        F = {'coin': np.array(['A', 'A', 'Z'], object), 't': np.array([t0 + 100.0, t0 + 200.0, t0 + 300.0]), 'hour_block4': np.array([0.0, 1.0, 0.0]),
             'v': np.array([1.0, 1.0, 1.0])}
        B = {'coin': np.array(['A', 'A'], object), 't': np.array([t0 + 1000.0, t0 + 2000.0]), 'hour_block4': np.array([0.0, 0.0]), 'v': np.array([9.0, 1.0])}
        why = {}; s = AD.match(F, B, ['v'], 'coin-day', 1, 0.2, np.random.default_rng(0), why=why)
        self.assertEqual((why[0][0], why[1][0], why[2][0]), (0, 2, 1))

    def test_legacy_try_ledger_never_authorizes_a_read(self):
        # OUTSIDE A35-AD-01 (OX-CODE1's planted six-column retired row): card must refuse BEFORE any read
        tmp = tempfile.mkdtemp(); d = dfn(); d.pop('_sha16'); d.pop('_path'); p = os.path.join(tmp, 'd.json'); json.dump(d, open(p, 'w'))
        sha = AD.load_def(p)['_sha16']; old = os.path.join(tmp, 'TRY_LEDGER.tsv')
        open(old, 'w').write('20251001\tALARM\tT\t1\t%s\ttry\n' % sha)
        called = []
        orig = AD.read_back; AD.read_back = lambda *a, **k: called.append(1) or (_ for _ in ()).throw(RuntimeError('read reached'))
        try:
            with self.assertRaises(SystemExit):
                AD.main(['card', p, tmp, tmp, old, '-', os.path.join(tmp, 'W.json')])
        finally:
            AD.read_back = orig
        self.assertEqual(called, [])

    def test_waves(self):
        t = np.array([0.0, 1000.0, 5000.0, 5100.0]); self.assertEqual(list(AD.waves(t)), [0, 0, 1, 1])

    def test_one_format_twice_same(self):
        c = setxy([(100, 200, 1), (2000, 2100, 1)], [(100, 200, 1), (2000, 2100, 1)])
        c[('X', D2)][0, 1000:1500] = 1; c[('A1.S02', D2)] = zeros(); c[('E2.S02', D2)] = zeros() + 10
        d = dfn(); d['id'] = 'TPLANT'
        recs, sets = AD.run(d, D2, D2, Plant(c), warm=1, log=lambda x: None)
        roots = [tempfile.mkdtemp(), tempfile.mkdtemp()]; shas = []
        for r in roots:
            AD.write_out(d, recs, sets, r, log=lambda x: None, catalog_dir=os.path.join(r, '_cat'))
            ix = json.load(open(os.path.join(r, 'day=%s' % D2, AD.part_name(d), 'index.json')))
            shas.append(json.dumps({k: v['files'] for k, v in ix['readings'].items()}, sort_keys=True))   # every value file's sha16
        self.assertEqual(shas[0], shas[1])
        F, B, S = AD.read_back(d, roots[0])
        self.assertEqual(len(F['t']), len(recs['FIRE']['t'])); self.assertEqual(sorted(F['t'].tolist()), sorted(recs['FIRE']['t'].tolist()))
        n_used = sum(len(x) for x in sets['FAIR']); self.assertEqual(sum(len(x) for x in S['FAIR']), n_used)
        cat = AD.catalog_text(d); self.assertIn('%s.lab_f_hit' % AD.part_name(d, 'FAIR'), cat)


class LabDaysFromCaller(unittest.TestCase):
    """the new path code: the lab days come from the caller (LabSource(lab_root=...), the run command's last argument)"""

    def test_no_machine_default(self):
        self.assertNotIn('LAB_ROOT', vars(AD))
        for bad in (None, ''):
            with self.assertRaisesRegex(ValueError, 'LAB_ROOT_REQUIRED'):
                AD.LabSource(lab_root=bad)
        with self.assertRaisesRegex(ValueError, 'LAB_ROOT_REQUIRED'):
            AD.LabSource()

    def test_lab_root_given_is_read(self):
        root = tempfile.mkdtemp()
        src = AD.LabSource(lab_root=root)
        self.assertEqual(src.R.root, root)

    def test_run_command_takes_the_lab_days(self):
        d = dfn(); p = os.path.join(tempfile.mkdtemp(), 'd.json'); d.pop('_sha16'); d.pop('_path'); json.dump(d, open(p, 'w'))
        out, rec = tempfile.mkdtemp(), tempfile.mkdtemp(); first = last = d['window']['first']
        for argv in (['run', p, first, last, out, rec], ['run', p, first, last, out, rec, '']):
            with self.assertRaisesRegex(SystemExit, 'lab days'):
                AD.main(argv)
        seen = []

        class Stop(Exception):
            pass

        def fake_source(**kw):
            seen.append(kw); raise Stop()
        real_src, real_quiet = AD.LabSource, AD.quiet_now
        AD.LabSource, AD.quiet_now = fake_source, (lambda now=None: False)
        try:
            with self.assertRaises(Stop):
                AD.main(['run', p, first, last, out, rec, 'LAB_DAYS_DIR'])
        finally:
            AD.LabSource, AD.quiet_now = real_src, real_quiet
        self.assertEqual(seen[0]['lab_root'], 'LAB_DAYS_DIR')


if __name__ == '__main__':
    unittest.main(verbosity=1)
