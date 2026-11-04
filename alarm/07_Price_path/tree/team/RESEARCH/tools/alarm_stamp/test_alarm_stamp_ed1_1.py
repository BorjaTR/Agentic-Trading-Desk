"""test_alarm_stamp_ed1_1.py: test_alarm_stamp.py (a0c7041f264eb5c5, never edited) on alarm_stamp_ed1_1. Owner QUANT. New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only").
Changed: only the import of the module tested (every test gives its out root, so the required out root changes nothing here). The rest
of this text is test_alarm_stamp.py's.
tests for RESEARCH tools/alarm_stamp (TOOL_DESIGN_V2 section 6). The entry and ladder are BED's real fill_v2 / ladder_v6 on planted 3 s
price paths (BED_EFILL / BED_ELADDER name their folders; default: ../../BED/scripts/... beside RESEARCH, as on the Mac); the one-format tests
(write, read back, generated once, determinism, the join with alarm_context) run when LAB3_CODE names lab3's code dir (the Mac job)."""
import datetime as dt, json, os, sys, tempfile, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_stamp_ed1_1 as S
AC = S.AC
BED = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'BED', 'scripts'))
if not os.path.isdir(BED):
    BED = os.path.normpath(os.path.join(HERE, '..', '..', 'BED', 'scripts'))                 # the VM copy's layout
EF = os.environ.get('BED_EFILL', os.path.join(BED, 'e_fill')); EL = os.environ.get('BED_ELADDER', os.path.join(BED, 'e_ladder'))
sys.path.insert(0, EF); sys.path.insert(0, EL)
import fill_v2 as FV
import ladder_v6 as LD
L3 = os.environ.get('LAB3_CODE')
US = 1_000_000


def ts(y, m, d, H=0, M=0, s=0):
    return dt.datetime(y, m, d, H, M, s, tzinfo=dt.timezone.utc).timestamp()


class Path:
    """planted 3 s bins per coin from t0 to t1: price(t) a step function of [(from_s_after_t_ref, price)]; loads only the days asked"""
    def __init__(self, t0, t1, t_ref, steps, coin='AAA'):
        te = np.arange(int(t0) + 3, int(t1), 3, dtype=np.int64) * US; tl = te - US; rel = (tl / US - t_ref)
        px = np.full(len(te), float(steps[0][1]))
        for a, p in steps:
            px[rel >= a] = p
        self.coin = coin; self.te, self.tl, self.px = te, tl, px; self.asked = []

    def load(self, coin, days):
        self.asked.append(list(days)); keep = np.array([AC.utc_day(t / US) in set(days) for t in self.tl], bool)
        if coin != self.coin or not keep.any():
            return FV.PriceView.empty(coin), set(), {}
        loaded = {d for d in days if any(AC.utc_day(t / US) == d for t in self.tl[keep][::1200])} | {AC.utc_day(self.tl[keep][0] / US), AC.utc_day(self.tl[keep][-1] / US)}
        p = self.px[keep]
        return FV.PriceView(coin, self.te[keep], self.tl[keep], p, p, p), loaded, {'lab:day=%s/BIN' % d: 'abcdef0123456789' for d in sorted(loaded)}


def write_events(path, rows):
    with open(path, 'w') as w:
        w.write('coin\tt\tside\tS\tmode\tforced\n')
        for c, t, s, x in rows:
            w.write('%s\t%.3f\t%d\t%.1f\tCLIMAX\t%s\n' % (c, t, s, x, 'SHORTS' if s > 0 else 'LONGS'))


def build_fake(path, rows, first, last, direction='FADE', decisions=(0,), hold=S.HOLD_S):
    d = tempfile.mkdtemp(); p = os.path.join(d, 'E.tsv'); write_events(p, rows); got = []
    cat = {S.code_name('A02', dr, n): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for dr in S.DIRECTIONS for n in S.NAMES}
    done = S.build('unused', None, EF, EL, p, 'A02', direction, first, last, d, decisions=decisions, hold=hold, load=path.load, FV=FV, LD=LD,
                   write=lambda *a, **k: got.append((a, k)), load_catalog=lambda q: cat, log=lambda s: None)
    return done, got


def as_x(got):
    """the fake writer's codes -> the read() shape"""
    acc = {'coin': [], 't_alarm': [], 't_decision': []}; acc.update({n: [] for n in S.NAMES})
    for a, k in got:
        off = json.loads(k['seal'])['known_at_offset_s']; codes = a[3]; base = None; dr = json.loads(k['seal'])['direction']
        for n in S.NAMES:
            rr = codes[S.code_name('A02', dr, n)]['rows']; keys = []; vals = []
            for c in a[4]:
                for b, ao, ka in zip(rr[c]['value_bits'], rr[c]['as_of_us'], rr[c]['known_at_us']):
                    keys.append((c, ao, ka)); vals.append(np.array([b], '<u8').view('<f8')[0] if b is not None else np.nan)
            if base is None:
                base = keys; acc['coin'] += [x[0] for x in keys]; acc['t_alarm'] += [x[1] / 1e6 for x in keys]; acc['t_decision'] += [x[2] / 1e6 - off for x in keys]
            acc[n] += vals
    return {k: np.array(v) for k, v in acc.items()}


T0 = ts(2025, 10, 15, 10)                                  # the alarm
TEST_SEALED = (('20251201', '20251231', 'test seal: December'), ('20260310', '99991231', 'the research cutoff'))
REAL_SEALED = None


def setUpModule():
    """the sealing machinery is tested with December sealed again (the owner opened December 22:06 Berlin; the machinery stays)"""
    global REAL_SEALED
    REAL_SEALED = AC.SEALED; AC.SEALED = TEST_SEALED


def tearDownModule():
    AC.SEALED = REAL_SEALED


class Ladder(unittest.TestCase):
    def setUp(self):
        # alarm side -1 (pushed down), FADE = buy. Flat 100; at +60 s 99.85 (heat 0.15); at +200 s 100.55 (offer 0.5); at +900 s 99.0 (heat 1.0)
        self.path = Path(T0 - 86400, T0 + 86400, T0, [(-1e9, 100.0), (60, 99.85), (200, 100.55), (900, 99.0)])

    def test_heat_before_offer_by_hand(self):
        done, got = build_fake(self.path, [('AAA', T0, -1, 1e6)], '20251015', '20251015')
        self.assertEqual(done, {'20251015': 'WRITTEN'}); x = as_x(got); st = S.stamps(x)
        self.assertEqual(x['filled'][0], 1.0); self.assertEqual(x['known_s'][0], S.HOLD_S)
        t_fill = T0 + S.DELAY_S + x['fill_wait_s'][0]
        for L in (1, 2, 3, 4, 5):
            self.assertTrue(abs(x['ot_%02d' % L][0] - (T0 + 200 - t_fill)) <= 3, L)          # offers 0.1 .. 0.5 at +200 s (3 s bins)
        self.assertTrue(np.isnan(x['ot_06'][0]))                                                 # never +0.6
        self.assertTrue(abs(x['ht_01'][0] - (T0 + 60 - t_fill)) <= 3)                           # heat 0.1 at +60 s
        self.assertTrue(abs(x['ht_10'][0] - (T0 + 900 - t_fill)) <= 3); self.assertTrue(np.isnan(x['ht_11'][0]))
        self.assertEqual(st['hb_0.5_15m'][0], 0.1); self.assertEqual(st['reach_0.5_15m'][0], 1.0)
        self.assertEqual(st['reach_0.6_240m'][0], 0.0); self.assertTrue(np.isnan(st['hb_0.6_240m'][0]))
        self.assertEqual(st['hw_15m'][0], 1.0)                                                   # heat 1.0 at alarm +900 s = fill + ~888 s
        self.assertEqual(st['hb_0.2_15m'][0], 0.1)                                               # the 0.1 heat (+60 s) came before every offer
        self.assertEqual(x['t_alarm'][0], round(T0, 3)); self.assertEqual(x['t_decision'][0], round(T0, 3))

    def test_fade_and_follow_are_mirrors(self):
        up = Path(T0 - 86400, T0 + 86400, T0, [(-1e9, 100.0), (60, 100.3), (300, 99.6)])
        fa = as_x(build_fake(up, [('AAA', T0, -1, 1e6)], '20251015', '20251015', 'FADE')[1])     # buy: offer at +60 s, heat 0.4 at +300 s
        fo = as_x(build_fake(up, [('AAA', T0, -1, 1e6)], '20251015', '20251015', 'FOLLOW')[1])   # sell: heat at +60 s, offer 0.4 at +300 s
        self.assertTrue(np.isfinite(fa['ot_03'][0]) and np.isnan(fa['ot_04'][0]) and np.isfinite(fa['ht_04'][0]))
        self.assertTrue(np.isfinite(fo['ht_03'][0]) and np.isnan(fo['ht_04'][0]) and np.isfinite(fo['ot_04'][0]))
        self.assertEqual(S.stamps(fa)['hb_0.3_15m'][0], 0.0); self.assertEqual(S.stamps(fo)['hb_0.4_15m'][0], 0.3)

    def test_same_second_is_heat_first(self):
        x = {'coin': np.array(['A']), 'filled': np.array([1.0]), 'known_s': np.array([14400.0])}
        for L in range(1, 26):
            x['ot_%02d' % L] = np.array([np.nan]); x['ht_%02d' % L] = np.array([np.nan])
        x['ot_02'] = np.array([50.0]); x['ht_01'] = np.array([50.0]); x['ht_02'] = np.array([51.0])
        st = S.stamps(x); self.assertEqual(st['hb_0.2_15m'][0], 0.1)

    def test_decisions_and_exact_keys(self):
        t = T0 + 0.123; done, got = build_fake(self.path, [('AAA', t, -1, 1e6)], '20251015', '20251015', decisions=(0, 15))
        x = as_x(got); self.assertEqual(len(x['coin']), 2)
        np.testing.assert_allclose(x['t_alarm'], [t, t], atol=1e-6); np.testing.assert_allclose(x['t_decision'], [t, t + 900], atol=1e-6)
        a, k = got[0]; rr = a[3]['STAMP.A02.FADE.filled']['rows']['AAA']
        self.assertEqual(rr['as_of_us'], [int(round(t * US))] * 2)
        self.assertEqual(S.offset_s(), 6 + 60 + 14400)                                         # SCOUT MUST 1: pinned, not only round-tripped
        self.assertEqual(rr['known_at_us'], [int(round(t * US)) + (w + 14466) * US for w in (0, 900)])   # known only after the whole hold
        for q in range(2):                                                                     # and never before the fill + the hold
            t_fill = x['t_decision'][q] + S.DELAY_S + x['fill_wait_s'][q]
            self.assertGreaterEqual(rr['known_at_us'][q], int(round((t_fill + S.HOLD_S) * US)))
        self.assertAlmostEqual(x['fill_px'][0], 100.0)

    def test_the_path_stops_at_an_unbuilt_day(self):
        """a path whose next day is not loaded is known only to 00:00: later horizons NaN, never 'not reached'"""
        t = ts(2025, 10, 15, 23, 0); p = Path(t - 86400, ts(2025, 10, 16), t, [(-1e9, 100.0), (60, 100.25)])
        x = as_x(build_fake(p, [('AAA', t, -1, 1e6)], '20251015', '20251015')[1]); st = S.stamps(x)
        self.assertTrue(3500 < x['known_s'][0] < 3600)
        self.assertEqual(st['reach_0.2_15m'][0], 1.0); self.assertEqual(st['reach_0.5_30m'][0], 0.0)
        self.assertTrue(np.isnan(st['reach_0.5_120m'][0])); self.assertTrue(np.isnan(st['hw_240m'][0]))
        self.assertEqual(st['reach_0.2_240m'][0], 1.0)                                          # reached early: known whatever came after


class Bracket(unittest.TestCase):
    def test_target_stop_by_hand(self):
        """4 rows: target first; stop first; same second (stop first); neither within 15 min; plus one not filled"""
        n = 5; x = {'coin': np.array(['A'] * n), 'filled': np.array([1, 1, 1, 1, 0.0]), 'known_s': np.full(n, 14400.0)}
        for L in range(1, 26):
            x['ot_%02d' % L] = np.full(n, np.nan); x['ht_%02d' % L] = np.full(n, np.nan)
        x['ot_05'] = np.array([100.0, 500.0, 300.0, 2000.0, 10.0]); x['ht_03'] = np.array([np.nan, 200.0, 300.0, 1900.0, 5.0])
        b = S.bracket(x, 0.5, 0.3, 15, cost_pct=np.full(n, 0.1))
        self.assertEqual(b['n'], 4); self.assertEqual((b['win'], b['loss'], b['open']), (0.25, 0.5, 0.25))
        self.assertAlmostEqual(b['net_closed'], (0.5 - 0.3 - 0.3) / 3 - 0.1); self.assertAlmostEqual(b['net_open0'], (0.5 - 0.6 + 0.0) / 4 - 0.1)
        b60 = S.bracket(x, 0.5, 0.3, 60); self.assertEqual((b60['win'], b60['loss'], b60['open']), (0.25, 0.75, 0.0))   # row 4: heat at 1900 s
        x['known_s'][3] = 1000.0; x['ot_05'][3] = np.nan; x['ht_03'][3] = np.nan                                         # as stored: no touch past the known path
        self.assertEqual(S.bracket(x, 0.5, 0.3, 60)['n'], 3); self.assertEqual(S.bracket(x, 0.5, 0.3, 15)['n'], 4)       # known to 15 min, not to 60


class FakeDays:
    """a lab3-like reader that lists the days it is given (read() must refuse a sealed one before reading anything)"""
    def __init__(self, days):
        self._d = days

    def days(self):
        return list(self._d)

    def parts(self, day):
        if AC.sealed(day):
            raise AssertionError('a sealed day was read')
        return []


class Horizons(unittest.TestCase):
    def test_read_refuses_sealed_days(self):
        """SCOUT MUST 2: read() raises on a December or after-cutoff day in the range, before reading it"""
        for d in ('20251205', '20260320'):
            with self.assertRaises(PermissionError):
                S.read('unused', None, 'A02', 'FADE', '20251101', '20260331', days_reader=FakeDays(['20251130', d]))

    def test_a_touch_exactly_at_the_horizon_counts(self):
        """SCOUT SHOULD 2: an offer first touched at exactly H x 60 s is reached within H"""
        x = {'coin': np.array(['A']), 'filled': np.array([1.0]), 'known_s': np.array([14400.0])}
        for L in range(1, 26):
            x['ot_%02d' % L] = np.array([np.nan]); x['ht_%02d' % L] = np.array([np.nan])
        x['ot_05'] = np.array([900.0]); x['ht_01'] = np.array([900.0]); x['ht_02'] = np.array([900.5])
        st = S.stamps(x)
        self.assertEqual(st['reach_0.5_15m'][0], 1.0); self.assertEqual(st['hb_0.5_15m'][0], 0.1); self.assertEqual(st['hw_15m'][0], 0.1)

    def test_1_jan_refused_like_alarm_context(self):
        """SCOUT SHOULD 3: an alarm on 1 Jan 2026 has no context row (its lab windows hold December), so no stamp row either"""
        t = ts(2026, 1, 1, 12); p = Path(t - 86400, t + 86400, t, [(-1e9, 100.0)])
        self.assertEqual(build_fake(p, [('AAA', t, 1, 1.0)], '20260101', '20260102')[0], {'20260101': 'REFUSED'})

    def test_each_horizon_sees_only_its_minutes(self):
        p = Path(T0 - 86400, T0 + 86400, T0, [(-1e9, 100.0), (60, 99.8), (1300, 100.6), (2000, 99.0)])
        st = S.stamps(as_x(build_fake(p, [('AAA', T0, -1, 1e6)], '20251015', '20251015')[1]))
        self.assertEqual(st['hw_15m'][0], 0.2); self.assertEqual(st['hw_30m'][0], 0.2); self.assertEqual(st['hw_60m'][0], 1.0)
        self.assertEqual(st['reach_0.5_15m'][0], 0.0); self.assertEqual(st['reach_0.5_30m'][0], 1.0); self.assertEqual(st['hb_0.5_30m'][0], 0.2)
        self.assertTrue(np.isnan(st['hb_0.5_15m'][0]))

    def test_a_touch_after_a_hole_is_not_seen(self):
        """the next day is not built: a touch two days later, inside a long hold, is beyond the known path"""
        t = ts(2025, 10, 15, 23, 0); p = Path(t - 86400, ts(2025, 10, 18), t, [(-1e9, 100.0), (60, 100.15), (90000, 103.0)])
        load = p.load
        p.load = lambda coin, days: load(coin, [d for d in days if d != '20251016'])
        x = as_x(build_fake(p, [('AAA', t, -1, 1e6)], '20251015', '20251015', hold=2 * 86400)[1])
        self.assertTrue(3500 < x['known_s'][0] < 3600); self.assertTrue(np.isfinite(x['ot_01'][0])); self.assertTrue(np.isnan(x['ot_20'][0]))


class Sealed(unittest.TestCase):
    def test_30_nov_path_never_reads_december(self):
        t = ts(2025, 11, 30, 22, 30)
        calm = Path(t - 86400, ts(2025, 12, 2), t, [(-1e9, 100.0), (600, 100.2)])
        wild = Path(t - 86400, ts(2025, 12, 2), t, [(-1e9, 100.0), (600, 100.2), (5400, 150.0), (5500, 50.0)])   # December: +50 pct, -50 pct
        a = build_fake(calm, [('AAA', t, -1, 1e6)], '20251130', '20251130', decisions=(0, 120))
        b = build_fake(wild, [('AAA', t, -1, 1e6)], '20251130', '20251130', decisions=(0, 120))
        self.assertEqual(a[0], {'20251130': 'WRITTEN'})
        self.assertEqual(a[1][0][0][3], b[1][0][0][3])                                          # every value the same
        self.assertTrue(all('20251201' not in d for asked in wild.asked for d in asked))         # December never asked for
        x = as_x(b[1]); self.assertEqual(len(x['coin']), 1)                                     # the +120 min decision (1 Dec 00:30) not written
        self.assertTrue(x['known_s'][0] < 5400)

    def test_sealed_alarm_days_refused(self):
        p = Path(ts(2025, 12, 4), ts(2025, 12, 6), ts(2025, 12, 5), [(-1e9, 100.0)])
        self.assertEqual(build_fake(p, [('AAA', ts(2025, 12, 5, 12), 1, 1.0)], '20251201', '20251231')[0], {'20251205': 'REFUSED'})
        q = Path(ts(2026, 3, 19), ts(2026, 3, 21), ts(2026, 3, 20), [(-1e9, 100.0)])
        self.assertEqual(build_fake(q, [('AAA', ts(2026, 3, 20, 12), 1, 1.0)], '20260301', '20260331')[0], {'20260320': 'REFUSED'})


class Catalog(unittest.TestCase):
    def test_catalog_file_is_generated(self):
        self.assertEqual(open(S.CATALOG).read(), S.catalog_text())
        self.assertEqual(len(S.NAMES), 5 + 50); self.assertEqual(len(set(S.NAMES)), len(S.NAMES))
        codes = [l.split('\t')[0] for l in open(S.CATALOG) if not l.startswith('#')][1:]
        self.assertEqual(len(codes), 55 * len(S.DIRECTIONS) * len(S.SUBJECTS)); self.assertEqual(len(set(codes)), len(codes))   # no code in two parts

    def test_not_filled_rows_say_why(self):
        p = Path(T0 + 3600, T0 + 7200, T0, [(-1e9, 100.0)])                                      # no price near the alarm: STALE
        done, got = build_fake(p, [('AAA', T0, -1, 1e6)], '20251015', '20251015')
        rr = got[0][0][3]['STAMP.A02.FADE.ot_01']['rows']['AAA']; self.assertEqual(rr['empty_reason'], ['STALE'])
        self.assertEqual(got[0][0][3]['STAMP.A02.FADE.filled']['rows']['AAA']['value_bits'], [0])


@unittest.skipUnless(L3, 'LAB3_CODE not set: the one-format tests run in the Mac job')
class OneFormat(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.ev = os.path.join(self.d, 'EVENTS.tsv')
        self.path = Path(T0 - 86400, T0 + 2 * 86400, T0, [(-1e9, 100.0), (60, 99.85), (200, 100.55), (900, 99.0)])
        write_events(self.ev, [('AAA', T0, -1, 1e6), ('AAA', T0 + 86400, 1, 2e6)])

    def build(self, root, first='20251015', direction='FADE'):
        return S.build('unused', L3, EF, EL, self.ev, 'A02', direction, first, '20251016', root, load=self.path.load, FV=FV, LD=LD, log=lambda s: None)

    def files(self, root, day):
        ix = json.load(open(os.path.join(root, 'day=%s' % day, 'STAMP.A02.FADE', 'index.json')))
        return {c: r['files'] for c, r in ix['readings'].items()}, ix

    def test_write_read_back(self):
        root = os.path.join(self.d, 'r1'); self.assertEqual(set(self.build(root).values()), {'WRITTEN'})
        x = S.read(root, L3, 'A02', 'FADE', '20251015', '20251016'); self.assertEqual(len(x['coin']), 2)
        self.assertEqual(x['filled'].tolist(), [1.0, 1.0]); self.assertEqual(S.stamps(x)['hb_0.5_15m'][0], 0.1)
        np.testing.assert_allclose(x['t_decision'], [T0, T0 + 86400], atol=1e-6)

    def test_both_directions_in_one_root_read_back(self):
        """J36476: FADE and FOLLOW in the same root and day must both read (no code held by two parts)"""
        root = os.path.join(self.d, 'r2'); self.build(root, direction='FADE'); self.build(root, direction='FOLLOW')
        fa = S.read(root, L3, 'A02', 'FADE', '20251015', '20251016'); fo = S.read(root, L3, 'A02', 'FOLLOW', '20251015', '20251016')
        self.assertEqual(len(fa['coin']), 2); self.assertEqual(len(fo['coin']), 2)
        self.assertNotEqual(np.nan_to_num(fa['ot_05']).tolist(), np.nan_to_num(fo['ot_05']).tolist())

    def test_generated_once_and_determinism(self):
        a, b = os.path.join(self.d, 'ra'), os.path.join(self.d, 'rb'); self.build(a); self.build(b)
        self.assertEqual(set(self.build(a).values()), {'UP TO DATE'})
        for day in ('20251015', '20251016'):
            fa, ia = self.files(a, day); fb, ib = self.files(b, day)
            self.assertEqual(fa, fb); self.assertEqual((ia['seal'], ia['sources']), (ib['seal'], ib['sources']))

    def test_range_does_not_change_a_day(self):
        a, b = os.path.join(self.d, 'rc'), os.path.join(self.d, 'rd'); self.build(a); self.build(b, first='20251016')
        self.assertEqual(self.files(a, '20251016')[0], self.files(b, '20251016')[0])

    def test_join_with_alarm_context(self):
        root = os.path.join(self.d, 'rj'); self.build(root)
        x = S.read(root, L3, 'A02', 'FADE', '20251015', '20251016')
        ctx = {'coin': np.array(['AAA', 'AAA', 'BBB']), 't_alarm': np.array([T0 + 86400, T0, T0]), 't_decision': np.array([T0 + 86400, T0, T0])}
        i, j = S.join(ctx, x); self.assertEqual(i.tolist(), [0, 1]); self.assertEqual(j.tolist(), [1, 0])


if __name__ == '__main__':
    unittest.main()
