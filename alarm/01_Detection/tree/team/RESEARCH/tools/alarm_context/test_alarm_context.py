"""tests for RESEARCH tools/alarm_context (TOOL_DESIGN_V1 section 6 + SCOUT's review 17:29Z: known-at = the decision time; December
refused). The blocks and build() run on a planted fake source anywhere; the one-format tests (write, read back, generated once,
determinism) run through the real lab3 when LAB3_CODE names its code dir (the Mac job), else they skip."""
import datetime as dt, json, os, resource, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_context as AC
import context_blocks as CB

M = 1440
DAY = '20251015'
D0 = dt.datetime(2025, 10, 15, tzinfo=dt.timezone.utc).timestamp()
L3 = os.environ.get('LAB3_CODE')
ALL = ('EVENT', 'MARKET', 'COIN')


TEST_SEALED = (('20251201', '20251231', 'test seal: December, as sealed until 21 Oct 22:06 Berlin'),
               ('20260310', '99991231', 'the research cutoff'))
REAL_SEALED = None


def setUpModule():
    """the sealing machinery is tested with December sealed again (the owner opened it for research 22:06 Berlin; the machinery stays)"""
    global REAL_SEALED
    REAL_SEALED = AC.SEALED; AC.SEALED = TEST_SEALED


def tearDownModule():
    AC.SEALED = REAL_SEALED


class Policy(unittest.TestCase):
    def test_the_real_policy(self):
        """LAB1 23 Oct (the owner 06:01Z): research reads Sep 2025 to May 2026; from 1 Jun 2026 sealed (BLIND). Was: from 1 Jan 2026 sealed."""
        AC.SEALED = REAL_SEALED
        try:
            self.assertIsNone(AC.sealed('20251215')); self.assertIsNone(AC.sealed_read('20251231')); self.assertIsNone(AC.sealed_read('20251201'))
            self.assertIsNone(AC.sealed('20260101')); self.assertIsNone(AC.sealed('20260531'))
            self.assertTrue(AC.sealed('20260601')); self.assertTrue(AC.sealed('20260706')); self.assertTrue(AC.sealed('20261022'))
        finally:
            AC.SEALED = TEST_SEALED


class FakeSrc:
    """minute ends of first - before .. last; any code is `plant[name]` (coins, N) if planted, else zeros; MARKET / BTC rows from
    plant['MARKET:' + name] / plant['BTC:' + name] (N,); prices rise 0.01 pct a minute; long_* = the same on the long timeline"""
    def __init__(self, coins, first=DAY, last=DAY, before=1, plant=None, price=None, base=None, cut=None):
        f = dt.datetime.strptime(first, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()
        span = 1 + (dt.datetime.strptime(last, '%Y%m%d') - dt.datetime.strptime(first, '%Y%m%d')).days
        self.coins = coins; self.t = f - 86400 + 60.0 * np.arange((1 + span) * M)                 # the short view: the day before .. last
        self.long_t = f - 86400 * before + 60.0 * np.arange((before + span) * M)                 # the long view: `before` days .. last
        self.plant = plant or {}; self.skipped = []; self.base = base; self.cut = cut           # base(name): a value for every unplanted code;
                                                                                                 # cut: from this time on EVERY read is 1e12
        n = len(self.t); self.price = price if price is not None else np.tile(100.0 * 1.0001 ** np.arange(n), (len(coins), 1))

    def _fill(self, name, shape, tl):
        a = np.full(shape, float(self.base(name))) if self.base else np.zeros(shape)
        if self.cut is not None:
            a[..., tl >= self.cut] = 1e12
        return a

    def code(self, name):
        return self.plant[name].copy() if name in self.plant else self._fill(name, (len(self.coins), len(self.t)), self.t)

    def prices(self):
        return self.price.copy(), np.zeros_like(self.price)

    def market(self, name):
        k = 'MARKET:' + name
        return self.plant[k].copy() if k in self.plant else self._fill(k, (len(self.t),), self.t)

    def btc(self, name):
        k = 'BTC:' + name
        return self.plant[k].copy() if k in self.plant else self._fill(k, (len(self.t),), self.t)

    def long(self, name):
        k = 'LONG:' + name
        return self.plant[k].copy() if k in self.plant else self._fill(k, (len(self.coins), len(self.long_t)), self.long_t)

    def long_btc(self, name):
        k = 'LONG_BTC:' + name
        return self.plant[k].copy() if k in self.plant else self._fill(k, (len(self.long_t),), self.long_t)


def events(rows, decision=0.0):
    ev = dict(coin=np.array([r[0] for r in rows]), t=np.array([float(r[1]) for r in rows]), side=np.array([r[2] for r in rows]),
              S=np.array([float(r[3]) for r in rows]))
    return AC.expand(ev, (decision,))


def run(ev, src, levels=ALL, hist=None, tables=None):
    return CB.run(CB.Ctx(ev, src, src.coins, src.t, hist=hist, tables=tables), levels)


def write_events(path, rows):
    with open(path, 'w') as w:
        w.write('coin\tt\tside\tS\tmode\tforced\n')
        for c, t, s, S in rows:
            w.write('%s\t%.3f\t%d\t%.1f\tCLIMAX\t%s\n' % (c, t, s, S, 'SHORTS' if s > 0 else 'LONGS'))


def write_tables(d):
    c = os.path.join(d, 'COSTS.tsv'); t = os.path.join(d, 'TYPES.tsv')
    open(c, 'w').write('# test\ncoin\thour_utc\tcost_bp\tgroup\nAAA\tALL\t12.5\tcheap\nBBB\t10\t30.0\tthin\n')
    open(t, 'w').write('coin\tclass\nAAA\tmajor\nBBB\tmeme\n')
    return c, t


class Blocks(unittest.TestCase):
    def test_known_at_planted_future(self):
        """a huge value from the first minute end AFTER the decision time on changes nothing, in every level and every kind of read"""
        for decision in (0.0, 30.0):
            t = D0 + 600 * 60 + 5; ev = events([('AAA', t, 1, 1e6), ('BBB', t, -1, 2e6)], decision); coins = ['AAA', 'BBB']
            base = FakeSrc(coins, before=31); a = run(ev, base)
            j = int(np.searchsorted(base.t, t + 60 * decision, 'right'))
            names = [x for x in ('A1.S08', 'A1.S09', 'B1.S01', 'B1.S02', 'NAUTILUS.S09', 'C11.S01', 'A6.S01', 'C1.S12', 'C1.S13', 'C1.S14', 'C2.S04',
                                 'C9.S03', 'C10.S10', 'C4.S01', 'E1.S01', 'E2.S02', 'E3.S01')]
            plant = {k: np.zeros((2, len(base.t))) for k in names}
            for k in names:
                plant[k][:, j:] = 1e12
            for k in ('C1.S16', 'C1.S18', 'C6.S05', 'C1.S14'):
                plant['BTC:' + k] = np.zeros(len(base.t)); plant['BTC:' + k][j:] = 1e12
            for k in ('C2.S02', 'C5.S04', 'A4.S05', 'A5.S09', 'D2.S05'):
                plant['MARKET:' + k] = np.zeros(len(base.t)); plant['MARKET:' + k][j:] = 1e12
            jl = int(np.searchsorted(base.long_t, t + 60 * decision, 'right'))
            for k in ('C1.S13', 'C1.S14'):
                plant['LONG:' + k] = np.zeros((2, len(base.long_t))); plant['LONG:' + k][:, jl:] = 1e12
                plant['LONG_BTC:' + k] = np.zeros(len(base.long_t)); plant['LONG_BTC:' + k][jl:] = 1e12
            plant['LONG_BTC:C1.S18'] = np.zeros(len(base.long_t)); plant['LONG_BTC:C1.S18'][jl:] = 1e12
            price = base.price.copy(); price[:, j:] = 1e6
            b = run(ev, FakeSrc(coins, before=31, plant=plant, price=price))
            for k in a:
                np.testing.assert_array_equal(a[k], b[k], err_msg='%s at decision %s' % (k, decision))

    def test_known_at_every_code_read(self):
        """v2: EVERY code any block reads (coin, MARKET, BTC, the 30-day views) set to 1e12 from the first minute end after the decision
        changes nothing: no block can look ahead, whatever code it reads"""
        base = lambda name: 1 + sum(map(ord, name)) % 7
        for decision in (0.0, 30.0):
            t = D0 + 600 * 60 + 5; ev = events([('AAA', t, 1, 1e6), ('BBB', t, -1, 2e6)], decision); coins = ['AAA', 'BBB']
            a = run(ev, FakeSrc(coins, before=31, base=base)); src = FakeSrc(coins, before=31, base=base)
            j = int(np.searchsorted(src.t, t + 60 * decision, 'right')); cut = src.t[j]
            price = src.price.copy(); price[:, j:] = 1e6
            b = run(ev, FakeSrc(coins, before=31, base=base, cut=cut, price=price))
            for k in a:
                np.testing.assert_array_equal(a[k], b[k], err_msg='%s at decision %s' % (k, decision))
            self.assertGreater(np.isfinite(np.stack(list(a.values()))).mean(), 0.6)        # most values are real numbers, not all NaN

    def test_decision_time_is_where_values_are_read(self):
        """a lab value is read at the last minute end <= the decision time, not at the alarm"""
        t = D0 + 600 * 60; src = FakeSrc(['AAA']); ramp = np.arange(len(src.t), dtype=float)[None, :]; src.plant['C1.S12'] = ramp
        for decision in (0.0, 30.0):
            x = run(events([('AAA', t, 1, 1e6)], decision), src, ('COIN',))
            self.assertEqual(x['coin_move_15m'][0], float(np.searchsorted(src.t, t + 60 * decision, 'right') - 1))

    def test_signs(self):
        t = D0 + 600 * 60; src = FakeSrc(['AAA', 'BBB']); n = len(src.t)
        src.plant.update({'BTC:C1.S16': np.full(n, 0.7), 'BTC:C6.S05': np.full(n, 0.8), 'MARKET:C5.S04': np.full(n, 0.9),
                          'E1.S01': np.full((2, n), 0.0001), 'MARKET:A4.S05': np.full(n, 7.0), 'MARKET:A4.S04': np.full(n, 3.0)})
        x = run(events([('AAA', t, 1, 1e6), ('BBB', t, -1, 1e6)]), src)
        self.assertGreater(x['move_5m'][0], 0); self.assertLess(x['move_5m'][1], 0)
        self.assertAlmostEqual(x['move_5m'][0], 100 * (1.0001 ** 5 - 1), 9)
        self.assertEqual(x['forced_shorts'].tolist(), [1.0, 0.0])
        self.assertEqual(x['btc_move_15m'].tolist(), [0.7, -0.7])
        np.testing.assert_allclose(x['btc_pos_6h'], [0.8, 0.2]); np.testing.assert_allclose(x['alts_with_push_15m'], [0.9, np.nan])   # P04-02: no down share exists
        np.testing.assert_allclose(x['funding_forced_pays_bp'], [-1.0, 1.0])     # + funding: longs pay; shorts forced (side +1) were paid
        self.assertEqual(x['mkt_wave_age_min'].tolist(), [7.0, 3.0])              # side +1: the shorts' wave (A4.S05)

    def test_forced_side(self):
        """side +1 reads the shorts' liquidations (A1.S09) as forced, -1 the longs' (A1.S08)"""
        t = D0 + 600 * 60; coins = ['AAA', 'BBB']; src = FakeSrc(coins); j = int(np.searchsorted(src.t, t, 'right')) - 1
        p9 = np.zeros((2, len(src.t))); p8 = np.zeros((2, len(src.t))); p9[:, j] = 1000.0; p8[:, j] = 10.0
        src.plant.update({'A1.S09': p9, 'A1.S08': p8})
        x = run(events([('AAA', t, 1, 1e6), ('BBB', t, -1, 1e6)]), src, ('EVENT',))
        self.assertAlmostEqual(x['forced_log_usd_1m'][0], 3.0); self.assertAlmostEqual(x['forced_log_usd_1m'][1], 1.0)
        self.assertAlmostEqual(x['forced_share_15m'][0], 1000 / 1010)

    def test_history_before_the_alarm_only(self):
        """alarms at the same second or later never count, even when the decision is 30 min later; the whole list counts, not the day"""
        t = D0 + 600 * 60
        H = events([('AAA', t - 2 * 86400, 1, 1.0), ('AAA', t - 3600 + 1, 1, 2.0), ('AAA', t - 60, 1, 3.0), ('AAA', t, 1, 4.0),
                    ('BBB', t, 1, 9.0), ('AAA', t + 10, 1, 50.0), ('BBB', t + 10, 1, 5.0)])
        hist = {'coin': H['coin'], 't': H['t'], 'S': H['S']}
        for decision in (0.0, 30.0):
            x = run(events([('AAA', t, 1, 4.0)], decision), FakeSrc(['AAA']), ('EVENT', 'COIN'), hist=hist)
            self.assertEqual(x['fires_coin_1h'][0], 2); self.assertEqual(x['fires_coin_7d'][0], 3); self.assertEqual(x['fires_other_5m'][0], 0)
            self.assertAlmostEqual(x['min_since_prev_fire'][0], 1.0); self.assertAlmostEqual(x['burst_rel_prior'][0], 4.0 / 2.0)
            self.assertTrue(np.isnan(x['days_since_bigger_alarm'][0])); self.assertEqual(x['alarms_all_24h'][0], 2)
        x = run(events([('AAA', t, 1, 1.5)]), FakeSrc(['AAA']), ('COIN',), hist=hist)
        self.assertAlmostEqual(x['days_since_bigger_alarm'][0], 60 / 86400.0)

    def test_trend_and_regime(self):
        """7 d = seven 24 h moves compounded; straightness 1 for a one-way walk; the volatility regime over 30 earlier days"""
        t = D0 + 600 * 60; src = FakeSrc(['AAA'], before=31); n = len(src.long_t)
        src.plant['LONG:C1.S14'] = np.full((1, n), 1.0)                              # +1 pct every 24 h
        hourly = np.where((np.arange(n) // 60) % 2 == 0, 1.0, 2.0)                    # alternating 1, 2: std 0.5 every day
        hourly[-2 * M:] = np.where((np.arange(2 * M) // 60) % 2 == 0, 1.0, 3.0)       # the last two days: std 1.0
        src.plant['LONG:C1.S13'] = hourly[None, :]
        x = run(events([('AAA', t, 1, 1e6), ]), src, ('COIN',))
        self.assertAlmostEqual(x['coin_move_7d'][0], 100 * (1.01 ** 7 - 1), 9); self.assertAlmostEqual(x['coin_straight_24h'][0], 1.0)
        self.assertAlmostEqual(x['coin_vol_regime'][0], 2.0, 6)
        y = run(events([('AAA', t, -1, 1e6)]), src, ('COIN',)); self.assertAlmostEqual(y['coin_move_7d'][0], -100 * (1.01 ** 7 - 1), 9)
        short = FakeSrc(['AAA'], before=5); short.plant['LONG:C1.S13'] = np.ones((1, len(short.long_t)))
        self.assertTrue(np.isnan(run(events([('AAA', t, 1, 1e6)]), short, ('COIN',))['coin_vol_regime'][0]))   # < 10 earlier days

    def test_tables(self):
        c, ty = write_tables(tempfile.mkdtemp()); tab = AC.load_tables(c, ty); t = D0 + 10 * 3600 + 30
        x = run(events([('AAA', t, 1, 1.0), ('BBB', t, 1, 1.0), ('CCC', t, 1, 1.0)]), FakeSrc(['AAA', 'BBB', 'CCC']), ('COIN',), tables=tab)
        np.testing.assert_array_equal(x['cost_bp_retro'][:2], [12.5, 30.0]); np.testing.assert_array_equal(x['cost_tier_retro'][:2], [1.0, 3.0])
        self.assertTrue(np.isnan(x['cost_bp'][:2]).all() and np.isnan(x['cost_tier'][:2]).all())   # A09-02: no vintage = NOT_KNOWN as a decision feature
        np.testing.assert_array_equal(x['coin_class'][:2], [1.0, 3.0]); self.assertTrue(np.isnan(x['cost_bp'][2]) and np.isnan(x['coin_class'][2]))

    def test_columns_named_unique(self):
        t = D0 + 600 * 60; x = run(events([('AAA', t, 1, 1e6)]), FakeSrc(['AAA'], before=31))
        self.assertEqual(list(x), [c[2] for c in AC.columns()]); self.assertEqual(len(set(x)), len(x))
        self.assertEqual({lv: sum(c[0] == lv for c in AC.columns()) for lv in ALL}, {'EVENT': 56, 'MARKET': 31, 'COIN': 43})   # OX-DATA P04-03: + the two 10k exhausted shares; A09-S03: + mkt_spread_bp

    def test_catalog_file_is_generated(self):
        self.assertEqual(open(AC.CATALOG).read(), AC.catalog_text())
        lines = [l for l in open(AC.CATALOG) if not l.startswith('#')][1:]
        self.assertEqual(len(lines), 130 * len(AC.SUBJECTS))                                   # A09-S03: + mkt_spread_bp
        self.assertTrue(all(l.split('\t')[1:5] == ['ROWS', 'event', '0', 'coin'] for l in lines))

    def test_duplicate_alarm_refused(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, 'E.tsv'); write_events(p, [('AAA', D0 + 60, 1, 1.0), ('AAA', D0 + 60, 1, 2.0)])
        with self.assertRaises(ValueError):
            AC.load_events(p)

    def test_build_with_a_fake_writer(self):
        """build: one row per alarm x decision, as_of = the alarm, known_at = the decision; December REFUSED, never written"""
        d = tempfile.mkdtemp(); p = os.path.join(d, 'E.tsv'); c, ty = write_tables(d); t = D0 + 600 * 60
        dec = dt.datetime(2025, 12, 5, tzinfo=dt.timezone.utc).timestamp()
        write_events(p, [('AAA', t, 1, 1e6), ('BBB', t + 30, -1, 2e6), ('AAA', dec, 1, 1e6)])
        got = []
        cat = {AC.code_name('A02', x[2]): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for x in AC.columns()}
        mk = lambda first, last, coins, before: (FakeSrc(coins, first, last, before), {})
        for level in ALL:
            done = AC.build('unused', p, 'A02', level, '20251001', '20251231', d, decisions=(0, 30), make_view=mk,
                            write=lambda *a, **k: got.append((a, k)), load_catalog=lambda path: cat, costs=c, types=ty, log=lambda s: None)
            self.assertEqual(done, {DAY: 'WRITTEN', '20251205': 'REFUSED'})
        self.assertEqual([a[2] for a, k in got], ['CTX.A02.EVENT', 'CTX.A02.MARKET', 'CTX.A02.COIN'])
        a, k = got[0]; rows = a[3]['CTX.A02.move_5m']['rows']['AAA']
        self.assertEqual(rows['as_of_us'], [int(t * 1e6)] * 2); self.assertEqual(rows['known_at_us'], [int(t * 1e6), int((t + 1800) * 1e6)])
        self.assertTrue(all(len(k['sources'][s]) == 16 for s in k['sources'])); self.assertIn('table:COSTS.tsv', got[2][1]['sources'])
        self.assertNotIn('table:COSTS.tsv', got[0][1]['sources'])                       # EVENT does not depend on the tables
        self.assertEqual(json.loads(k['seal'])['decisions_min'], [0.0, 30.0])

    def test_matched_moments_read_the_alarms_as_history(self):
        """subject A02_MATCH: rows are random moments; their history is the ALARM list (hist_path), never the other moments"""
        d = tempfile.mkdtemp(); m = os.path.join(d, 'M.tsv'); al = os.path.join(d, 'A.tsv'); t = D0 + 600 * 60
        write_events(al, [('AAA', t - 1800, 1, 5.0), ('BBB', t - 120, 1, 5.0)])
        write_events(m, [('AAA', t, 1, float('nan')), ('AAA', t - 60, 1, float('nan'))])
        got = []; cat = {AC.code_name('A02_MATCH', x[2]): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for x in AC.columns()}
        AC.build('unused', m, 'A02_MATCH', 'EVENT', DAY, DAY, d, make_view=lambda f, l, cs, b: (FakeSrc(cs, f, l, b), {}),
                 write=lambda *a, **k: got.append((a, k)), load_catalog=lambda p: cat, log=lambda s: None, hist_path=al)
        rr = got[0][0][3]
        self.assertEqual(rr['CTX.A02_MATCH.fires_coin_1h']['rows']['AAA']['value_bits'][1], int(np.array([1.0], '<f8').view('<u8')[0]))   # the alarm, not the other moment
        self.assertEqual(rr['CTX.A02_MATCH.fires_other_5m']['rows']['AAA']['value_bits'][1], int(np.array([1.0], '<f8').view('<u8')[0]))
        self.assertIn('history:A.tsv', got[0][1]['sources'])

    def test_memory(self):
        """400 alarms on 20 coins, every level, stay far under 300 MB (L47)"""
        coins = ['C%02d' % i for i in range(20)]; rng = np.random.default_rng(0)
        rows = [(coins[i % 20], D0 + float(rng.integers(0, 86400)), 1 if i % 2 else -1, 1e5 + i) for i in range(400)]
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        run(events(rows), FakeSrc(coins, before=31))
        grow = (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss - before) / (1024 * 1024 if sys.platform == 'darwin' else 1024)
        print('MEMORY grow %.0f MB' % grow, file=sys.stderr); self.assertLess(grow, 300)


class Mirror(unittest.TestCase):
    """SCOUT review 17:54Z MUST 3: every directional column, side +1 vs side -1 on asymmetric plants, against hand-written answers;
    bands and channels read at the minute BEFORE (a different value planted at the decision minute); exact window edges"""
    def setUp(self):
        self.t = D0 + 600 * 60 + 5; src = FakeSrc(['AAA']); n = len(src.t); self.J = int(np.searchsorted(src.t, self.t, 'right')) - 1
        J = self.J; P = {}

        def coin(v, now=None):
            a = np.full((1, n), float(v))
            if now is not None:
                a[0, J] = now                                                  # the decision minute differs: a lag-1 read must not see it
            return a
        P.update({'A1.S09': coin(300), 'A1.S08': coin(100), 'B1.S01': coin(1e4), 'B1.S02': coin(2e4),
                  'A6.S01': coin(1e3), 'A6.S09': coin(1e5), 'A6.S03': coin(2e3), 'A6.S11': coin(2e5), 'A6.S05': coin(3e3), 'A6.S13': coin(3e5),
                  'NAUTILUS.S79': coin(110, 999), 'NAUTILUS.S81': coin(90, 1), 'NAUTILUS.S82': coin(120, 999), 'NAUTILUS.S84': coin(80, 1),
                  'NAUTILUS.S09': coin(95), 'NAUTILUS.S73': coin(104, 999), 'NAUTILUS.S74': coin(102, 0), 'NAUTILUS.S70': coin(101, 999),
                  'NAUTILUS.S71': coin(99, 0), 'C11.S01': coin(0.4), 'C11.S02': coin(2.0), 'NAUTILUS.S62': coin(7), 'NAUTILUS.S63': coin(9),
                  'C1.S12': coin(0.5), 'C1.S13': coin(0.8), 'C2.S04': coin(0.25), 'C2.S05': coin(-0.4), 'C9.S03': coin(0.9), 'C9.S17': coin(0.6),
                  'C11.S08': coin(1), 'E1.S01': coin(1e-4), 'E3.S01': coin(5), 'E2.S02': 1000.0 + np.arange(n, dtype=float)[None, :]})
        for k, v in {'C2.S02': 0.3, 'C2.S03': 0.6, 'C2.S08': 0.2, 'C5.S04': 0.7, 'C5.S05': 0.4, 'C5.S06': 0.1, 'A4.S05': 7, 'A4.S04': 3,
                     'A5.S09': 0.8, 'A5.S04': 0.05, 'A5.S03': 0.02}.items():
            P['MARKET:' + k] = np.full(n, float(v))
        for k, v in {'C1.S16': 0.7, 'C6.S05': 0.8, 'C4.S09': 0.3}.items():
            P['BTC:' + k] = np.full(n, float(v))
        src.plant = P; src.price = np.full((1, n), 100.0); self.src = src

    def both(self):
        up = run(events([('AAA', self.t, 1, 1e6)]), self.src); dn = run(events([('AAA', self.t, -1, 1e6)]), self.src); return up, dn

    def test_every_directional_column(self):
        up, dn = self.both(); L = np.log10
        want = {  # column: (side +1, side -1)
            'forced_log_usd_1m': (L(300), L(100)), 'forced_log_usd_15m': (L(4500), L(1500)), 'other_log_usd_15m': (L(1500), L(4500)),
            'forced_share_15m': (0.75, 0.25), 'forced_over_taker_15m': (0.03, 0.005),
            'beyond_dc240': (100 * (100 / 110 - 1), 100 * (90 / 100 - 1)), 'beyond_dc1440': (100 * (100 / 120 - 1), 100 * (80 / 100 - 1)),
            'vwap_dist': (100 * (100 / 95 - 1), -100 * (100 / 95 - 1)), 'boll1440_pos': (-1.0, 1.0), 'boll240_pos': (0.5, -0.5),
            'to_day_extreme': (0.4, 2.0), 'min_since_swing': (7, 9),
            'basket_move_15m': (0.3, -0.3), 'basket_move_1h': (0.6, -0.6), 'alts_vs_btc_1h': (0.2, -0.2),
            'coins_strong_with_push_1h': (0.4, 0.1), 'coins_strong_against_push_1h': (0.1, 0.4), 'mkt_wave_age_min': (7, 3),
            'mkt_forced_share_1m': (0.8, 0.2), 'mkt_forced_per_taker_1m': (0.05, 0.02),
            'btc_move_15m': (0.7, -0.7), 'btc_pos_6h': (0.8, 0.2), 'btc_straight_3h': (0.3, -0.3),
            'coin_move_15m': (0.5, -0.5), 'coin_move_1h': (0.8, -0.8), 'coin_vs_basket_15m': (0.25, -0.25), 'coin_vs_basket_1h': (-0.4, 0.4),
            'range_pos_1h': (0.9, 0.1), 'range_pos_4h': (0.6, 0.4), 'broke_yday_range': (1, -1),
            'funding_forced_pays_bp': (-1.0, 1.0), 'basis_push_bp': (5, -5),
            'oi_chg_1h': (100 * 60 / (1000 + self.J - 60), 100 * 60 / (1000 + self.J - 60)),
            'oi_chg_24h': (100 * 1440 / (1000 + self.J - 1440), 100 * 1440 / (1000 + self.J - 1440))}
        for k, (a, b) in want.items():
            self.assertAlmostEqual(up[k][0], a, 9, msg='%s side +1' % k); self.assertAlmostEqual(dn[k][0], b, 9, msg='%s side -1' % k)
        for k in ('wall_ahead_log_1pct', 'wall_ahead_log_2pct', 'wall_ahead_log_3pct', 'wall_behind_log_1pct', 'wall_behind_log_2pct',
                  'wall_behind_log_3pct'):                         # OX-DATA P04-01: A6 WITHDRAWN, never published, either side
            self.assertTrue(np.isnan(up[k][0]) and np.isnan(dn[k][0]), k)
        self.assertAlmostEqual(up['alts_with_push_15m'][0], 0.7, 9); self.assertTrue(np.isnan(dn['alts_with_push_15m'][0]))   # P04-02

    def test_every_v2_directional_column(self):
        """v2 blocks (PROPOSED_BLOCKS_V2.md): forced-side picks and push signs against hand answers, side +1 vs -1"""
        n = len(self.src.t); C = lambda v: np.full((1, n), float(v)); Mk = lambda v: np.full(n, float(v))
        self.src.plant.update({'X1.LIQX.S04': C(7), 'X1.LIQX.S03': C(3), 'X1.LIQX.S01': C(0.4), 'A7.S03': C(-0.05), 'A7.S01': C(0.02),
                               'B2.S02': C(0.6), 'X1.FLOWX.S12': C(0.3), 'X1.FLOWX.S01': C(5000), 'D1.S04': C(0.4), 'D4.S04': C(-0.2),
                               'D3.S05': C(0.3), 'D3.S15': C(2), 'X1.COST.S01': C(3), 'X1.COST.S02': C(2), 'X1.COST.S04': C(10),
                               'X1.COST.S05': C(20), 'X1.COST.S06': C(5), 'X1.COST.S08': C(10), 'Z3.S01': C(45), 'X1.RETX.S01': C(1.3),
                               'X1.RETX.S04': C(0.7), 'C12.S02': C(12), 'X1.VOLX.S19': C(0.9), 'X1.VOLX.S17': C(1), 'X1.POSX.S03': C(2),
                               'X1.POSX.S12': C(1.1), 'X1.POSX.S13': C(0.05), 'X1.POSX.S14': C(2.0)})
        for k, v in {'A2.S06': 9, 'A2.S05': 4, 'A2.S04': 2.5, 'A2.S03': 1.5, 'C7.S04': 0.8, 'X1.VOLX.S18': 0.95, 'E1.S07': 1.5,
                     'X1.FLOWX.S04': 0.4, 'Z2.S02': 30}.items():
            self.src.plant['MARKET:' + k] = Mk(v)
        self.src.plant.update({'BTC:X1.VOLX.S09': Mk(-5)})
        up, dn = self.both(); L2 = np.log(2.0)
        want = {'liq_oi_forced_bp_60s': (7, 3), 'liq_seconds_share_60s': (0.4, 0.4), 'oi_moved_since_wave': (-0.05, 0.02),
                'coins_liquidating_1m': (9, 4), 'coins_liquidating_z': (2.5, 1.5), 'fills_one_sided': (0.6, 0.6), 'volume_one_sided': (0.3, 0.3),
                'whale_net_5m_usd': (5000, -5000), 'book_flow_top_60s': (0.4, -0.4), 'book_flow_10lv_60s': (-0.2, 0.2),
                'book_imbalance_30bp': (0.3, -0.3), 'depth_vs_median_coin': (2, 2), 'spread_vs_usual': (1.5, 1.5), 'impact_10k_vs_usual': (2, 2),
                'min_to_funding': (45, 45), 'typical_range_15m': (0.8, 0.8), 'market_hot_rank_30d': (0.95, 0.95),
                'btc_implied_minus_real': (-5, -5), 'market_funding_dev': (-1.5, 1.5), 'market_whales_with_push': (0.4, -0.4),
                'crypto_news_rows': (30, 30), 'btc_beta_3d': (1.3, 1.3), 'idio_move_60m': (0.7, -0.7), 'quote_rate': (12, 12),
                'range_rank_1h_30d': (0.9, 0.9), 'jump_flag': (1, -1), 'funding_z_30d': (-2, 2), 'oi_vs_30d': (1.1, 1.1),
                'top_traders_ls_chg_1h': (0.05, -0.05), 'taker_buy_sell_5m': (L2, -L2)}
        for k, (a, b) in want.items():
            self.assertAlmostEqual(up[k][0], a, 9, msg='%s side +1' % k); self.assertAlmostEqual(dn[k][0], b, 9, msg='%s side -1' % k)

    def test_window_edges(self):
        """sum_last over k minutes = minutes J - k + 1 .. J: a value at J - k is outside, one at J - k + 1 inside"""
        n = len(self.src.t); J = self.J; a = np.zeros((1, n)); a[0, J - 15] = 1000.0; a[0, J - 14] = 10.0; a[0, J] = 1.0
        self.src.plant.update({'A1.S09': a, 'A1.S08': np.zeros((1, n))})
        up = run(events([('AAA', self.t, 1, 1e6)]), self.src, ('EVENT',))
        self.assertAlmostEqual(up['forced_log_usd_15m'][0], np.log10(11.0)); self.assertAlmostEqual(up['forced_log_usd_1m'][0], 0.0)

    def test_a_hole_is_not_zero(self):
        """a NaN minute in the window (a lab hole) gives NaN, not a smaller sum (SCOUT SHOULD 2; the lab writes 0 for nothing: J36470)"""
        a = self.src.plant['A1.S09'].copy(); a[0, self.J - 3] = np.nan; self.src.plant['A1.S09'] = a
        up = run(events([('AAA', self.t, 1, 1e6)]), self.src, ('EVENT',))
        self.assertTrue(np.isnan(up['forced_log_usd_15m'][0])); self.assertAlmostEqual(up['forced_log_usd_1m'][0], np.log10(300))

    def test_bigger_alarm_includes_equal(self):
        t = self.t; H = events([('AAA', t - 86400, 1, 5.0), ('AAA', t - 3600, 1, 1.0), ('AAA', t, 1, 5.0)])
        x = run(events([('AAA', t, 1, 5.0)]), FakeSrc(['AAA']), ('COIN',), hist={'coin': H['coin'], 't': H['t'], 'S': H['S']})
        self.assertAlmostEqual(x['days_since_bigger_alarm'][0], 1.0)

    def test_since_the_alarm(self):
        t = self.t; H = events([('AAA', t, 1, 5.0), ('AAA', t + 60, 1, 1.0), ('BBB', t + 120, 1, 1.0), ('BBB', t + 1800, 1, 1.0)])
        h = {'coin': H['coin'], 't': H['t'], 'S': H['S']}
        x = run(events([('AAA', t, 1, 5.0)], 30.0), FakeSrc(['AAA']), ('EVENT',), hist=h)
        self.assertEqual((x['fires_coin_since'][0], x['fires_other_since'][0]), (1, 1))         # t+1800 is at the decision: not before it
        x0 = run(events([('AAA', t, 1, 5.0)], 0.0), FakeSrc(['AAA']), ('EVENT',), hist=h)
        self.assertEqual((x0['fires_coin_since'][0], x0['fires_other_since'][0], x0['fires_coin_1h'][0]), (0, 0, 0))

    def test_vol_regime_excludes_today(self):
        """today's 24 h std 1.0; days 1..15 std 0.5, days 16..30 std 2.0: median 1.25, ratio 0.8 (with today inside it would be 1.33)"""
        src = FakeSrc(['AAA'], before=31); J = int(np.searchsorted(src.long_t, self.t, 'right')) - 1
        i = np.arange(len(src.long_t)); back = J - i; d = back // 1440; k = (back % 1440) // 60
        amp = np.where(d == 0, 1.0, np.where(d <= 15, 0.5, 2.0)); v = np.where(k % 2 == 0, amp, -amp); v[back < 0] = 0.0
        src.plant['LONG:C1.S13'] = v[None, :]; src.plant['LONG:C1.S14'] = np.zeros((1, len(src.long_t)))
        x = run(events([('AAA', self.t, 1, 1e6)]), src, ('COIN',))
        self.assertAlmostEqual(x['coin_vol_regime'][0], 0.8, 9)


class Sealed(unittest.TestCase):
    def test_the_day_after_a_sealed_period_is_sealed_for_reads(self):
        self.assertTrue(AC.sealed_read('20260101')); self.assertTrue(AC.sealed_read('20251215')); self.assertIsNone(AC.sealed_read('20260102'))
        self.assertIsNone(AC.sealed('20260101')); self.assertIsNone(AC.sealed_read('20251130'))

    """SCOUT review 17:54Z MUST 1 and 2: a sealed day (December 2025; from 10 Mar 2026) is never read: not its lab minutes, not its
    alarms as history, not a decision time on it; build and read refuse it"""
    def build_rows(self, rows, first, last, plant_dec, decisions=(0, 30)):
        d = tempfile.mkdtemp(); p = os.path.join(d, 'E.tsv'); c, ty = write_tables(d); write_events(p, rows); got = []
        cat = {AC.code_name('A02', x[2]): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for x in AC.columns()}

        def mk(f, l, coins, before):
            s = FakeSrc(coins, f, l, before)
            if plant_dec:
                for tl, key in ((s.t, ''), (s.long_t, 'LONG:')):
                    dec = np.array([AC.sealed_read(AC.utc_day(x)) is not None for x in tl])   # December and 1 Jan (its lab windows)
                    for code in ('A1.S08', 'A1.S09', 'C1.S12', 'C1.S13', 'C1.S14', 'E2.S02', 'NAUTILUS.S79', 'NAUTILUS.S81'):
                        a = np.zeros((len(coins), len(tl))); a[:, dec] = 1e12; s.plant[key + code] = a
                    for code in ('C1.S14', 'C1.S18', 'C1.S16'):
                        a = np.zeros(len(tl)); a[dec] = 1e12; s.plant[('LONG_BTC:' if key else 'BTC:') + code] = a
                s.price = np.where(np.array([AC.sealed_read(AC.utc_day(x)) is not None for x in s.t])[None, :], 1e9, s.price)
            return s, {}
        out = {}
        for level in ALL:
            AC.build('unused', p, 'A02', level, first, last, d, decisions=decisions, make_view=mk, write=lambda *a, **k: got.append((a, k)),
                     load_catalog=lambda path: cat, costs=c, types=ty, log=lambda s: None)
        for a, k in got:
            for code, cc in a[3].items():
                for coin, r in cc['rows'].items():
                    for ao, ka, b in zip(r['as_of_us'], r['known_at_us'], r['value_bits']):
                        out[(code, coin, ao, ka)] = b
        return out

    def test_january_and_30_nov_do_not_see_december(self):
        jan = dt.datetime(2026, 1, 2, 0, 30, tzinfo=dt.timezone.utc).timestamp(); nov = dt.datetime(2025, 11, 30, 23, 50, tzinfo=dt.timezone.utc).timestamp()
        jan1 = dt.datetime(2026, 1, 1, 12, 0, tzinfo=dt.timezone.utc).timestamp()
        decx = [('AAA', dt.datetime(2025, 12, 31, 20, 0, tzinfo=dt.timezone.utc).timestamp(), 1, 9e9),
                ('BBB', dt.datetime(2025, 12, 31, 23, 0, tzinfo=dt.timezone.utc).timestamp(), -1, 9e9)]
        base = [('AAA', jan, 1, 1e6), ('AAA', nov, -1, 1e6), ('BBB', jan1, 1, 1e6)]
        a = self.build_rows(base, '20251101', '20260131', plant_dec=False)
        b = self.build_rows(base + decx, '20251101', '20260131', plant_dec=True)
        self.assertEqual(a, b)
        known = sorted({k[3] for k in a}); self.assertNotIn(int((nov + 1800) * 1e6), known)   # the 30 Nov decision at 1 Dec 00:20: not written
        self.assertIn(int(nov * 1e6), known); self.assertIn(int((jan + 1800) * 1e6), known)
        self.assertFalse([k for k in a if k[2] == int(jan1 * 1e6)])                                     # 1 Jan: its lab windows hold December: refused

    def test_after_the_cutoff_refused(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, 'E.tsv'); c, ty = write_tables(d)
        write_events(p, [('AAA', dt.datetime(2026, 3, 20, 12, tzinfo=dt.timezone.utc).timestamp(), 1, 1e6),
                         ('AAA', dt.datetime(2026, 3, 9, 23, 50, tzinfo=dt.timezone.utc).timestamp(), 1, 1e6)])
        got = []; cat = {AC.code_name('A02', x[2]): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for x in AC.columns()}
        done = AC.build('unused', p, 'A02', 'EVENT', '20260301', '20260331', d, decisions=(0, 30), make_view=lambda f, l, cs, b: (FakeSrc(cs, f, l, b), {}),
                        write=lambda *a, **k: got.append((a, k)), load_catalog=lambda path: cat, log=lambda s: None)
        self.assertEqual(done, {'20260309': 'WRITTEN', '20260320': 'REFUSED'})
        r = got[0][0][3]['CTX.A02.move_5m']['rows']['AAA']; self.assertEqual(len(r['known_at_us']), 1)     # 23:50 + 30 min = 10 Mar: dropped


def fake_maker(first, last, coins, before):
    return FakeSrc(coins, first, last, before), {'lab:day=%s/X1' % first: '0123456789abcdef'}


@unittest.skipUnless(L3, 'LAB3_CODE not set: the one-format tests run in the Mac job')
class OneFormat(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.ev = os.path.join(self.d, 'EVENTS.tsv'); t = D0 + 600 * 60
        self.costs, self.types = write_tables(self.d)
        write_events(self.ev, [('AAA', t - 86400 * 3, 1, 5e5), ('AAA', t, 1, 1e6), ('BBB', t + 30, -1, 2e6), ('AAA', t + 7200, -1, 3e6),
                               ('BBB', D0 + 86400 + 60, 1, 4e5)])

    def build(self, root, level='EVENT', first=DAY, decisions=(0,)):
        return AC.build('unused', self.ev, 'A02', level, first, AC.shift(DAY, 1), root, decisions=decisions, make_view=fake_maker,
                        code_dir=L3, costs=self.costs, types=self.types, log=lambda s: None)

    def files(self, root, day, level='EVENT'):
        ix = json.load(open(os.path.join(root, 'day=%s' % day, AC.part_name('A02', level), 'index.json')))
        return {c: r['files'] for c, r in ix['readings'].items()}, ix

    def test_write_read_back_and_choose_values(self):
        root = os.path.join(self.d, 'r1')
        for lv in ALL:
            self.assertEqual(self.build(root, lv), {DAY: 'WRITTEN', AC.shift(DAY, 1): 'WRITTEN'})
        x = AC.read(root, L3, 'A02', DAY, AC.shift(DAY, 1), ['move_5m', 'btc_move_1h', 'cost_bp_retro', 'fires_coin_7d'])
        self.assertEqual(list(x), ['coin', 't_alarm', 't_decision', 'move_5m', 'btc_move_1h', 'cost_bp_retro', 'fires_coin_7d'])
        self.assertEqual(x['coin'].tolist(), ['AAA', 'BBB', 'AAA', 'BBB'])
        self.assertAlmostEqual(x['move_5m'][0], 100 * (1.0001 ** 5 - 1), 9); self.assertEqual(x['cost_bp_retro'][0], 12.5)
        self.assertEqual(x['fires_coin_7d'][0], 1.0)                                       # the alarm 3 days before, outside the dates built
        self.assertTrue(np.isnan(AC.read(root, L3, 'A02', DAY, DAY, ['beyond_dc240'])['beyond_dc240']).all())   # NOT_KNOWN reads NaN

    def test_decisions_are_rows(self):
        root = os.path.join(self.d, 'r6'); self.build(root, decisions=(0, 15, 60))
        x = AC.read(root, L3, 'A02', DAY, DAY, ['move_5m'])
        self.assertEqual(len(x['coin']), 9); self.assertEqual(sorted(set(np.round(x['t_decision'] - x['t_alarm']).tolist())), [0.0, 900.0, 3600.0])

    def test_generated_once(self):
        root = os.path.join(self.d, 'r2'); self.build(root); got = self.build(root)
        self.assertEqual(set(got.values()), {'UP TO DATE'})
        self.assertFalse([n for n in os.listdir(os.path.join(root, 'day=%s' % DAY)) if '.aside_' in n])

    def test_determinism(self):
        a, b = os.path.join(self.d, 'ra'), os.path.join(self.d, 'rb')
        for lv in ALL:
            self.build(a, lv); self.build(b, lv)
            for day in (DAY, AC.shift(DAY, 1)):
                fa, ia = self.files(a, day, lv); fb, ib = self.files(b, day, lv)
                self.assertEqual(fa, fb); self.assertEqual((ia['seal'], ia['sources']), (ib['seal'], ib['sources']))

    def test_range_does_not_change_a_day(self):
        a, b = os.path.join(self.d, 'rc'), os.path.join(self.d, 'rd'); self.build(a); self.build(b, first=AC.shift(DAY, 1))
        self.assertEqual(self.files(a, AC.shift(DAY, 1))[0], self.files(b, AC.shift(DAY, 1))[0])

    def test_changed_input_rebuilds_only_what_uses_it(self):
        root = os.path.join(self.d, 're'); self.build(root, 'EVENT'); self.build(root, 'COIN')
        with open(self.types, 'a') as w:
            w.write('CCC\talt\n')                                                           # a table changed: COIN rebuilds, EVENT not
        self.assertEqual(set(self.build(root, 'EVENT').values()), {'UP TO DATE'})
        self.assertEqual(set(self.build(root, 'COIN').values()), {'WRITTEN'})

    def test_the_real_reader_never_lists_a_sealed_day(self):
        """SCOUT SHOULD (18:14Z): the real lab3 reader inside lab_view must list December and 1 Jan as unbuilt, so View never reads or carries them"""
        lab = os.path.join(self.d, 'lab')
        for d in ('20251130', '20251201', '20251231', '20260101', '20260102'):
            os.makedirs(os.path.join(lab, 'day=%s' % d))
        src, used = AC.lab_view(lab, L3)('20260102', '20260102', ['AAA'], 33)          # the long view reaches back to 30 Nov
        lv = src._view('LONG', ['AAA'], 33); self.assertEqual(lv.days[0], '20251130')
        for v in (src._short, lv):
            built = {d for d, b in zip(v.days, v.built) if b}
            self.assertEqual(built & {'20251201', '20251231', '20260101'}, set()); self.assertIn('20260102', built)
        self.assertIn('20251130', {d for d, b in zip(lv.days, lv.built) if b})                # an open day before the seal stays readable

    def test_december_refused_on_read(self):
        root = os.path.join(self.d, 'rf'); self.build(root)
        os.makedirs(os.path.join(root, 'day=20251205'))
        with self.assertRaises(PermissionError):
            AC.read(root, L3, 'A02', '20251201', '20251231', ['move_5m'])


class SignedSize(unittest.TestCase):
    def test_signed_S_becomes_its_size(self):
        """SCOUT 21:49Z MUST: a list with a SIGNED S (P3V2 Lee-Mykland L, N6V3 minute return): S = |S|, so lg(S) and the comparisons
        with earlier alarms never depend on the side"""
        import tempfile
        p = os.path.join(tempfile.mkdtemp(), 'E.tsv')
        open(p, 'w').write('coin\tt\tside\tS\tmode\nAAA\t100\t1\t7.5\tX\nAAA\t200\t-1\t-7.5\tX\nBBB\t300\t-1\t-2\tX\n')
        ev = AC.load_events(p); self.assertEqual(ev['S'].tolist(), [7.5, 7.5, 2.0]); self.assertEqual(ev['side'].tolist(), [1, -1, -1])


if __name__ == '__main__':
    unittest.main()
