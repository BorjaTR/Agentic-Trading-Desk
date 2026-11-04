# test_ctx_output_proofs_ed1_1.py: new edition by SCOUT for the clean release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release
# folder only"). Owner QUANT (with LEAD/LAYERS). Old file: test_ctx_output_proofs.py 142b792f95aef839, never edited. Changed: only its imports (alarm_context_ed1_1 and test_alarm_context_ed1_1).
"""OUTPUT PROOFS of 26 context readings (ASK STRATEGY-144018; OUTSIDE A09 rule: a context output is PROVEN only with its OWN version-bound
proof, never inherited from valid inputs). One planted check per reading (known input -> known output) plus its EMPTY rule, on the real
context_blocks code through the planted FakeSrc of test_alarm_context (no store read). The cards these tests prove are
CTX_OUTPUT_PROOFS_V1.tsv (definition, clock, EMPTY rule); a test here names the card row it proves (proof O1_PLANT)."""
import csv, datetime as dt, os, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import test_alarm_context_ed1_1 as TA
import alarm_context_ed1_1 as AC

D0, M = TA.D0, TA.M
CARDS = os.path.join(HERE, 'CTX_OUTPUT_PROOFS_V1.tsv')


def utc(y, mo, d, h, mi=0):
    return dt.datetime(y, mo, d, h, mi, tzinfo=dt.timezone.utc).timestamp()


def hist_of(rows):
    H = TA.events(rows); return {'coin': H['coin'], 't': H['t'], 'S': H['S']}


class Identity(unittest.TestCase):
    def test_hour_weekday_forced_shorts(self):
        t = D0 + 10 * 3600 + 1800                                                     # Wed 15 Oct 2025 10:30 UTC
        x = TA.run(TA.events([('AAA', t, 1, 1e6), ('BBB', t, -1, 1e6)]), TA.FakeSrc(['AAA', 'BBB']), ('EVENT',))
        self.assertEqual(x['hour_utc'].tolist(), [10.0, 10.0]); self.assertEqual(x['weekday'].tolist(), [2.0, 2.0])
        self.assertEqual(x['forced_shorts'].tolist(), [1.0, 0.0])

    def test_decision_hour_and_weekend(self):
        t = D0 + 23 * 3600 + 45 * 60                                                  # alarm Wed 23:45, decision 30 min later: Thu 00:15
        x = TA.run(TA.events([('AAA', t, 1, 1e6)], 30.0), TA.FakeSrc(['AAA'], last='20251016'), ('MARKET',))
        self.assertEqual(x['decision_hour_utc'][0], 0.0); self.assertEqual(x['weekend'][0], 0.0)
        sat = utc(2025, 10, 18, 9)
        y = TA.run(TA.events([('AAA', sat, 1, 1e6)]), TA.FakeSrc(['AAA'], first='20251018', last='20251018'), ('MARKET',))
        self.assertEqual(y['weekend'][0], 1.0); self.assertEqual(y['decision_hour_utc'][0], 9.0)


class History(unittest.TestCase):
    T = D0 + 600 * 60

    def runh(self, rows, decision=0.0, levels=('EVENT', 'COIN')):
        H = hist_of(rows)
        return TA.run(TA.events([('AAA', self.T, 1, 4.0)], decision), TA.FakeSrc(['AAA', 'BBB']), levels, hist=H)

    def test_counts(self):
        t = self.T
        rows = [('AAA', t - 8 * 86400, 1, 1.0), ('AAA', t - 2 * 86400, 1, 1.0), ('AAA', t - 5 * 3600, 1, 1.0), ('AAA', t - 2 * 3600, 1, 1.0),
                ('AAA', t - 1800, 1, 1.0), ('BBB', t - 200, 1, 1.0), ('BBB', t - 3000, 1, 1.0), ('BBB', t - 23 * 3600, 1, 1.0),
                ('AAA', t, 1, 4.0), ('AAA', t + 60, 1, 1.0), ('BBB', t + 120, 1, 1.0)]
        x = self.runh(rows)
        self.assertEqual([x['fires_coin_%s' % k][0] for k in ('1h', '4h', '24h', '7d')], [1, 2, 3, 4])
        self.assertEqual((x['fires_other_5m'][0], x['fires_other_60m'][0]), (1, 2))
        self.assertAlmostEqual(x['min_since_prev_fire'][0], 30.0); self.assertEqual(x['alarms_all_24h'][0], 6)
        self.assertEqual((x['fires_coin_since'][0], x['fires_other_since'][0]), (0, 0))   # decision 0: nothing after the alarm counts
        y = self.runh(rows, decision=5.0)
        self.assertEqual((y['fires_coin_since'][0], y['fires_other_since'][0]), (1, 1))   # alarm < t' < decision

    def test_empty(self):
        x = self.runh([('AAA', self.T, 1, 4.0)])
        self.assertTrue(np.isnan(x['min_since_prev_fire'][0]))                        # no earlier alarm: NaN, never 0
        self.assertEqual(x['fires_coin_7d'][0], 0); self.assertEqual(x['alarms_all_24h'][0], 0)


class Move(unittest.TestCase):
    T = D0 + 600 * 60

    def test_moves_and_sudden(self):
        x = TA.run(TA.events([('AAA', self.T, 1, 1e6), ('BBB', self.T, -1, 1e6)]), TA.FakeSrc(['AAA', 'BBB']), ('EVENT',))
        for k in (5, 15, 60, 240):                                                    # prices rise 0.01 pct a minute
            self.assertAlmostEqual(x['move_%dm' % k][0], 100 * (1.0001 ** k - 1), 9); self.assertAlmostEqual(x['move_%dm' % k][1], -100 * (1.0001 ** k - 1), 9)
        self.assertAlmostEqual(x['sudden_share'][0], (1.0001 ** 5 - 1) / (1.0001 ** 60 - 1), 9)

    def test_empty_price(self):
        src = TA.FakeSrc(['AAA']); j = int(np.searchsorted(src.t, self.T, 'right')) - 1; src.price[0, j - 15] = 0.0
        x = TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))
        self.assertTrue(np.isnan(x['move_15m'][0])); self.assertFalse(np.isnan(x['move_5m'][0]))

    def test_donchian(self):
        src = TA.FakeSrc(['AAA', 'BBB']); n = len(src.t); j = int(np.searchsorted(src.t, self.T, 'right')) - 1; p = src.price[0, j]
        up = np.zeros((2, n)); dn = np.zeros((2, n)); up[:, j - 1] = p / 1.02; dn[:, j - 1] = p * 1.25
        src.plant.update({'NAUTILUS.S79': up, 'NAUTILUS.S81': dn, 'NAUTILUS.S82': up.copy(), 'NAUTILUS.S84': dn.copy()})
        x = TA.run(TA.events([('AAA', self.T, 1, 1e6), ('BBB', self.T, -1, 1e6)]), src, ('EVENT',))
        self.assertAlmostEqual(x['beyond_dc240'][0], 2.0, 9); self.assertAlmostEqual(x['beyond_dc1440'][0], 2.0, 9)   # 2 pct above the upper edge
        self.assertAlmostEqual(x['beyond_dc240'][1], 25.0, 9)                         # down push: 100 x (lower / p - 1), the reciprocal form
        src.plant['NAUTILUS.S79'] = np.zeros((2, n))
        self.assertTrue(np.isnan(TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))['beyond_dc240'][0]))  # an edge <= 0 is no edge


class Forcing(unittest.TestCase):
    T = D0 + 600 * 60

    def test_shares_and_other_side(self):
        src = TA.FakeSrc(['AAA', 'BBB']); n = len(src.t); j = int(np.searchsorted(src.t, self.T, 'right')) - 1
        s9 = np.zeros((2, n)); s8 = np.zeros((2, n)); s9[:, j - 3] = 3000.0; s8[:, j - 10] = 1000.0; s8[:, j - 20] = 5e6   # the last is outside 15 min
        src.plant.update({'A1.S09': s9, 'A1.S08': s8})
        x = TA.run(TA.events([('AAA', self.T, 1, 1e6), ('BBB', self.T, -1, 1e6)]), src, ('EVENT',))
        self.assertAlmostEqual(x['forced_share_15m'][0], 0.75); self.assertAlmostEqual(x['other_log_usd_15m'][0], 3.0)
        self.assertAlmostEqual(x['forced_share_15m'][1], 0.25); self.assertAlmostEqual(x['other_log_usd_15m'][1], np.log10(3000.0))

    def test_empty_and_nothing(self):
        src = TA.FakeSrc(['AAA']); x = TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))
        self.assertTrue(np.isnan(x['forced_share_15m'][0])); self.assertEqual(x['other_log_usd_15m'][0], 0.0)   # 0/0 no share; nothing = 0
        hole = np.zeros((1, len(src.t))); hole[0, int(np.searchsorted(src.t, self.T, 'right')) - 4] = np.nan; src.plant['A1.S08'] = hole
        y = TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))
        self.assertTrue(np.isnan(y['other_log_usd_15m'][0]) and np.isnan(y['forced_share_15m'][0]))            # a hole is unknown, never 0


class CoinAndBook(unittest.TestCase):
    T = D0 + 600 * 60

    def test_coin_class(self):
        c, ty = TA.write_tables(tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))); tab = AC.load_tables(c, ty)
        x = TA.run(TA.events([('AAA', self.T, 1, 1.0), ('BBB', self.T, 1, 1.0), ('CCC', self.T, 1, 1.0)]), TA.FakeSrc(['AAA', 'BBB', 'CCC']), ('COIN',), tables=tab)
        self.assertEqual(x['coin_class'][:2].tolist(), [1.0, 3.0]); self.assertTrue(np.isnan(x['coin_class'][2]))   # not in the hand list

    def test_spread_vs_usual(self):
        src = TA.FakeSrc(['AAA']); n = len(src.t)
        src.plant.update({'X1.COST.S01': np.full((1, n), 3.0), 'X1.COST.S02': np.full((1, n), 1.5)})
        self.assertAlmostEqual(TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))['spread_vs_usual'][0], 2.0)
        src.plant['X1.COST.S02'] = np.zeros((1, n))
        self.assertTrue(np.isnan(TA.run(TA.events([('AAA', self.T, 1, 1e6)]), src, ('EVENT',))['spread_vs_usual'][0]))   # no usual: NaN


class Cards(unittest.TestCase):
    def test_every_card_has_its_test_and_a_catalog_row(self):
        rows = list(csv.DictReader((l for l in open(CARDS) if not l.startswith('#')), delimiter='\t'))
        names = [c[2] for c in AC.columns()]; tests = {n for n in dir(sys.modules[__name__]) if isinstance(getattr(sys.modules[__name__], n), type)}
        self.assertEqual(len(rows), 26)
        for r in rows:
            self.assertIn(r['value'], names, r['value']); cls, meth = r['test'].split('.')
            self.assertIn(cls, tests); self.assertTrue(hasattr(getattr(sys.modules[__name__], cls), meth), r['test'])
            for k in ('definition', 'known_at', 'empty_rule'):
                self.assertTrue(r[k].strip(), (r['value'], k))


if __name__ == '__main__':
    unittest.main()
