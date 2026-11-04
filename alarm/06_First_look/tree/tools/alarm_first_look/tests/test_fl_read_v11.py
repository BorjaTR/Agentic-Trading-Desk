"""test_fl_read_v11.py (SCOUT 30 Oct 2026, tools/alarm_first_look). Edition 10's 127 tests on edition 11 (test_fl_read_v10.py, import
changed), then edition 11's own (T28): the fires' waves are the grade's (labcore's waves, a 30 min gap; owner 30 Oct 2026 21:11 Berlin):
fires 20 min apart share a wave, a gap of exactly 30 min keeps the wave, 30 min and 1 s starts a new one; the reader uses labcore's
function, not a copy; given ids still replace them. test_fl_read_v10.py's docstring follows:
(SCOUT 30 Oct 2026, tools/alarm_first_look). Edition 9's 123 tests on edition 10 (test_fl_read_v9.py, import changed),
then edition 10's own (T27): Look takes the fires' wave ids (review B, 30 Oct 2026: the ladder's made-up fires keep their real waves): the
default is md_v1's waves, given ids are the bars' unit, a wave's month and day are its first fire's, misaligned or negative ids are refused.
test_fl_read_v9.py's docstring follows: (SCOUT 30 Oct 2026, tools/alarm_first_look). Edition 8's 112 tests on edition 9 (test_fl_read_v8.py, import changed), then
edition 9's own (T24, T25): the z lines (PERIODS9), Jan-Apr confirms at z 1, the z line reaches both bars, RULE_9 against RULE_8, the
FL_RULE9 table and FL_RULE8 byte for byte equal to edition 8's. test_fl_read_v8.py's docstring follows: Edition 7's 87 tests on edition 8, then edition 8's own: the
SIZE bar equals edition 7's MOVES verdict; the SIDE bar equals Look.net_test (mean and z) and passes a planted side, fails no side
and the wrong side; BROAD and COUNT for SIDE; a made-up net replaces the fires'; RULE_8's labels; the tables on files.
test_fl_read_v7.py's docstring follows: (SCOUT 30 Oct 2026, tools/alarm_first_look). Edition 6's 66 tests on edition 7, then edition 7's own: MOVES matched on
the busy random in the same band pair (a world where the last hour explains everything fails; normal-only matching would pass it), the
busy filter on both sides, thin months, unmatched band pairs, 3 of 4 months and z, the random's error in z, the pre-fire random out,
BROAD (coins, days), COUNT, NOT RUN, the overall RULE_7, the weighted quantiles, and runs on files (the BZ folder inside a finished
job, the manifest's list sha16, the one-to-one join, the tables).
test_fl_read_v6.py's docstring follows: (SCOUT 30 Oct 2026, tools/alarm_first_look). Edition 4's tests (edition 3's 48 with the PUSH test rewritten for
the new PUSH; the busy-filter run with the 1.12c cut; the 5-point leg tests replaced by the test across waves), then edition 5's: the
leg's error clustered by day and the random without the pre-fire moments; unfinished jobs refused; a refused run leaves no output;
and the rules reviewer F's planted bugs showed untested (heat side, a wave's day, the R-side refusals, the 'without' results by month,
the windows, the summary columns, the weighted random median, the pre-fire share, the random speed, the May guards).
Edition 4's docstring follows: test_fl_read_v4.py (SCOUT 30 Oct 2026). Edition 3's 48 tests, then edition 4's (the 5-point leg, now
replaced; the busy filter beside each alarm). Edition 3's docstring follows.
v2's tests (smallest first: weighted random, waves and months, the month
test at its boundaries, concentration, the PASS rule, exclusions, race LEAD, speed, money, May refused, the move spent, the AP join), then
edition 3: the rule pinned where reviewer C's planted bugs lived (waves of several fires, unequal weights, rule 1 AND rule 2, the forward
months outside the 30-waves rule, the edge a mean, the excluded coins out of the random too, the race weights, speed per wave, a coin's
share split across its wave), NO PUSH, the random's coverage, the moments before a fire, the dropped counts, the input refusals, and one
end-to-end run with lists, weights, a PERFIRE and both AP kinds.
  python3 -B tests/test_fl_read_v6.py   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)"""
import calendar, contextlib, csv, gzip, io, json, math, os, shutil, sys, tempfile, unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import fl_read_v11 as F
M = F.M

COSTS = dict({'C%d' % i: 10.0 for i in range(10)}, DASH=10.0, VVV=10.0, ZEC=10.0, A=10.0, B=10.0, C=10.0, D=10.0, E=20.0)
C = 10.0 / 100 + 0.032
ALL = M.DESIGN + M.FORWARD


def start(m):
    return calendar.timegm((int(m[:4]), int(m[4:]), 10 if m == '202509' else 1, 0, 0, 0))


def table(rows, best=None, worst=None, obh=None, reach_t=None, ret=None):
    """rows: (coin, t, side, m, k); best/worst/obh(m, k, coin, side_name, h) -> value (pct for best/worst, sign for obh)"""
    T = {'coin': np.array([r[0] for r in rows], dtype=object), 't': np.array([r[1] for r in rows], np.int64),
         'side': np.array([r[2] for r in rows], int), 'unit__c': np.full(len(rows), C)}
    for h in F.WINDOWS:
        for d in ('FADE', 'FOLLOW'):
            T['BEST_%dM__%s' % (h, d)] = np.array([best(r[3], r[4], r[0], d, h) if best else 5 * C for r in rows], float)
            T['WORST_%dM__%s' % (h, d)] = np.array([worst(r[3], r[4], r[0], d, h) if worst else 1 * C for r in rows], float)
            T['OBH4_%dM__%s' % (h, d)] = np.array([obh(r[3], r[4], r[0], d, h) if obh else 0.0 for r in rows], float)
            T['OBH4_%dM__%s__t' % (h, d)] = np.full(len(rows), np.nan)
    for d in ('FADE', 'FOLLOW'):
        T['REACH4_180M__%s' % d] = np.ones(len(rows)); T['REACH4_180M__%s__t' % d] = np.array([reach_t(d) if reach_t else 600.0 for r in rows], float)
        for h in (15, 60, 180):
            T['RET_%dM__%s' % (h, d)] = np.array([ret(d) if ret else 0.5 for r in rows], float)
        T['WORST_1M__%s' % d] = T['WORST_1M__%s' % d] if 'WORST_1M__%s' % d in T else np.full(len(rows), 0.05)
    return T


def fires(months=ALL, waves=40, coins=None, gap_h=12, extra=None):
    coins = coins or ['C%d' % i for i in range(10)]
    if isinstance(waves, int):
        waves = {m: waves for m in months}
    R = [(coins[k % len(coins)], start(m) + k * gap_h * 3600, -1, m, k) for m in months for k in range(waves.get(m, 0))]
    return R + (extra or [])


def randoms(A_rows):
    """3 random moments per fire, 7 minutes after it, other coins; weight 1/3"""
    R = []
    for (c, t, s, m, k) in A_rows:
        for j in range(3):
            R.append(('C%d' % ((int(c[1:]) if c[1:].isdigit() else 0) + j + 1) if c.startswith('C') else c, t + 420 + 60 * j, s, m, k))
    return R


def look(A_rows, R_rows, Akw=None, Rkw=None, lean='FADE', w=None, **kw):
    A = table(A_rows, **(Akw or {})); R = table(R_rows, **(Rkw or {}))
    return F.Look(A, R, np.full(len(R_rows), 1 / 3.0) if w is None else np.asarray(w, float), COSTS, lean, **kw)


class T01Basics(unittest.TestCase):
    def test_weighted(self):
        self.assertEqual(F.wmean(np.array([1.0, 3.0, np.nan]), np.array([1.0, 3.0, 5.0])), 2.5)
        self.assertEqual(F.wmedian(np.array([1.0, 2.0, 10.0]), np.array([1.0, 1.0, 1.0])), 2.0)
        self.assertEqual(F.other('FADE'), 'FOLLOW')

    def test_may_refused(self):
        A = fires(months=('202510',), waves=2) + [('C0', M.T1, -1, '202605', 0)]
        with self.assertRaises(M.Refused):
            look(A, randoms(A[:2]))


class T02Month(unittest.TestCase):
    def setUp(self):
        self.A = fires(); self.R = randoms(self.A)

    def test_base_passes(self):
        # alarm: offer 5c, heat 1c; random: offer 2c, heat 2c -> edge 4 vs 0: beats by 4c
        V = look(self.A, self.R, Rkw={'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}).verdict()
        self.assertEqual(V['PASS'], 'PASS'); self.assertEqual(V['months_held_design'], 4)

    def test_offer_boundary(self):
        L = look(self.A, self.R, Akw={'best': lambda *a: 4 * C}, Rkw={'best': lambda *a: 0.5 * C, 'worst': lambda *a: 2 * C})
        self.assertTrue(L.month_test(('202510',))['offer_ok'])
        L = look(self.A, self.R, Akw={'best': lambda *a: 3.99 * C}, Rkw={'best': lambda *a: 0.5 * C, 'worst': lambda *a: 2 * C})
        self.assertFalse(L.month_test(('202510',))['offer_ok'])

    def test_edge_boundary_and_first(self):
        # alarm edge 5-1 = 4; random edge set so the difference is exactly 2, then just under 2 with offer-first equal to random
        L = look(self.A, self.R, Rkw={'best': lambda *a: 3 * C, 'worst': lambda *a: 1 * C})
        t = L.month_test(('202510',)); self.assertAlmostEqual(t['edge_1h_vs_random_c'], 2.0, places=9); self.assertTrue(t['beats_random'])
        L = look(self.A, self.R, Rkw={'best': lambda *a: 3.01 * C, 'worst': lambda *a: 1 * C})
        self.assertFalse(L.month_test(('202510',))['beats_random'])           # 1.99c, and offer-first 0 = random 0
        L = look(self.A, self.R, Akw={'obh': lambda m, k, coin, d, h: 1.0 if (d == 'FADE' and k % 2 == 0) else 0.0},
                 Rkw={'best': lambda *a: 3.01 * C, 'worst': lambda *a: 1 * C, 'obh': lambda m, k, coin, d, h: 1.0 if (d == 'FADE' and k % 4 == 0) else 0.0})
        t = L.month_test(('202510',)); self.assertGreater(t['first_1h_share'], t['random_first_1h_share']); self.assertTrue(t['beats_random'])

    def test_three_of_four(self):
        bad = lambda m, k, coin, d, h: (2 * C if m in ('202510',) else 5 * C)
        V = look(self.A, self.R, Akw={'best': bad}, Rkw={'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}).verdict()
        self.assertEqual(V['months_held_design'], 3); self.assertEqual(V['PASS'], 'PASS')
        bad2 = lambda m, k, coin, d, h: (2 * C if m in ('202510', '202511') else 5 * C)
        V = look(self.A, self.R, Akw={'best': bad2}, Rkw={'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}).verdict()
        self.assertEqual(V['PASS'], 'NOT PASS'); self.assertIn('MONTHS (2 of 4)', V['fail'])

    def test_thirty_waves(self):
        w = dict({m: 40 for m in ALL}, **{'202511': 29}); A = fires(waves=w)
        V = look(A, randoms(A), Rkw={'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}).verdict()
        self.assertIn('COUNT', V['fail'])
        w['202511'] = 30; A = fires(waves=w)
        V = look(A, randoms(A), Rkw={'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}).verdict()
        self.assertNotIn('COUNT', V['fail'])

    def test_lean_follow_reads_follow(self):
        A = self.A
        L = look(A, self.R, Akw={'best': lambda m, k, coin, d, h: (5 * C if d == 'FOLLOW' else 1 * C)}, lean='FOLLOW')
        self.assertAlmostEqual(L.month_test(('202510',))['offer_1h_median_c'], 5.0, places=9)


    def test_one_hour_window_and_own_cost(self):
        one_h = lambda m, k, coin, d, h: (5 * C if h == 60 else 1 * C)
        L = look(self.A, self.R, Akw={'best': one_h})
        self.assertAlmostEqual(L.month_test(('202510',))['offer_1h_median_c'], 5.0, places=9)
        CE = 20.0 / 100 + 0.032
        A = fires(coins=['E']); L = look(A, randoms(A), Akw={'best': lambda *a: 5 * CE})
        self.assertAlmostEqual(L.month_test(('202510',))['offer_1h_median_c'], 5.0, places=9)

    def test_wave_month_is_its_first_fire(self):
        t0 = calendar.timegm((2025, 10, 31, 23, 55, 0))
        A = fires(months=()) + [('C0', t0, -1, '202510', 0), ('C1', t0 + 600, -1, '202511', 0)]
        L = look(A, randoms(A))
        self.assertEqual(list(L.wmonth), ['202510', '202510'])


class T03Concentration(unittest.TestCase):
    def rk(self):
        return {'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}

    def test_edge_is_above_the_months_random(self):
        A = fires()
        rk = {'best': lambda m, k, coin, d, h: (5 * C if m == '202510' else 2 * C), 'worst': lambda *a: 2 * C}
        V = look(A, randoms(A), Akw={'best': lambda *a: 5 * C, 'worst': lambda *a: 1 * C}, Rkw=rk).verdict()
        self.assertAlmostEqual(V['edge_design']['total'], 40 * 1.0 + 120 * 4.0, places=6)   # Oct: 4 - 3; other months: 4 - 0

    def test_two_coins_under_half(self):
        four = ['A', 'B', 'C', 'D']; A = fires(coins=four); R = randoms(A)
        V = look(A, R, Rkw=self.rk()).verdict()
        self.assertAlmostEqual(V['edge_design']['top2_coins_share'], 0.5, places=9); self.assertIn('COINS', V['fail'])   # exactly half: not under
        ten = fires(); V = look(ten, randoms(ten), Rkw=self.rk()).verdict()
        self.assertNotIn('COINS', V['fail'])

    def test_top5_waves_and_days(self):
        A = fires()
        big = lambda m, k, coin, d, h: (500 * C if (m == '202510' and k < 5) else 5 * C)
        V = look(A, randoms(A), Akw={'best': big}, Rkw=self.rk()).verdict()
        self.assertIn('WAVES5', V['fail']); self.assertIn('DAYS', V['fail'])
        self.assertEqual(len(V['edge_design']['top5_waves']), 5)

    def test_exact_half_is_not_under_half(self):
        # one wave a day, 20 a month: 5 waves of edge 15 and 75 of edge 1 -> top 5 waves and best 5 days are exactly half
        A = fires(gap_h=24, waves=20)
        big = lambda m, k, coin, d, h: (16 * C if (m == '202510' and k < 5) else 2 * C)
        V = look(A, randoms(A), Akw={'best': big}, Rkw=self.rk()).verdict()
        self.assertEqual(V['edge_design']['top5_waves_share'], 0.5); self.assertEqual(V['edge_design']['best5_days_share'], 0.5)
        self.assertIn('WAVES5', V['fail']); self.assertIn('DAYS', V['fail'])

    def test_without_top5_and_excluded_coins(self):
        A = fires(coins=['C0', 'C1', 'C2', 'DASH'])
        L = look(A, randoms(A), Rkw=self.rk(), drop_coins=F.EXCLUDE)
        self.assertFalse(L.useA[np.array([c == 'DASH' for c in L.A['coin']])].any())
        V = look(A, randoms(A), Rkw=self.rk()).verdict()
        L5 = look(A, randoms(A), Rkw=self.rk(), drop_waves=V['edge_design']['top5_waves'])
        self.assertEqual(int((~L5.useA).sum()), 5)


class T04Race(unittest.TestCase):
    def test_lead(self):
        P = {'kind': np.array(['A', 'A', 'R', 'R']), 'month': np.array(['2510'] * 4), 'w': np.array([1.0, 1.0, 1.0, 1.0])}
        for h in F.RACE:
            P['FADE %s' % h] = np.array([1.0, 1.0, 0.0, 1.0]); P['FOLLOW %s' % h] = np.array([0.0, 0.0, 0.0, 1.0])
        A = fires(months=('202510',), waves=2)
        L = look(A, randoms(A), perfire=P)
        r = L.race('202510')['15m']
        self.assertEqual(r['lean_a'], 100.0); self.assertEqual(r['lean_r'], 50.0); self.assertEqual(r['other_a'], 0.0); self.assertEqual(r['other_r'], 50.0)
        self.assertEqual(r['LEAD'], 100.0)


class T05Reported(unittest.TestCase):
    def test_speed_sides(self):
        A = fires(); R = randoms(A)
        L = look(A, R, Akw={'reach_t': lambda d: 300.0 if d == 'FADE' else 900.0})
        sp = L.speed(M.DESIGN)
        self.assertEqual(sp['FADE offer']['median_s'], 300.0); self.assertEqual(sp['FADE heat']['median_s'], 900.0)
        self.assertEqual(sp['FOLLOW offer']['median_s'], 900.0)

    def test_money_and_counts(self):
        A = fires(months=('202510',), waves=30); L = look(A, randoms(A))
        mo = L.money(('202510',)); self.assertAlmostEqual(mo['60m market_pct'], 0.5 - C, places=9)
        self.assertAlmostEqual(mo['60m waiting_pct'], 0.5 - (0.031 + 10.0 / 200 + 0.016), places=9)
        c = L.counts('202510'); self.assertEqual(c['fires'], 30); self.assertEqual(c['waves_all'], 30); self.assertEqual(c['days_with_fires'], 15)
        L0 = look(A, randoms(A), Akw={'worst': lambda m, k, coin, d, h: (0.0 if h == 1 else 1 * C)})
        self.assertTrue(np.isnan(L0.money(('202510',))['60m waiting_pct']))     # WORST_1M 0: never filled


# ---------------- edition 2
def ap_for(A_rows, run=None, age=None, back=None, capped=None, normal=None, norm=None):
    """move spent arrays aligned to A_rows; each argument (m, k, coin) -> value (pct for run, back and normal; run_norm in normal moves)"""
    f = lambda g, d: np.array([g(r[3], r[4], r[0]) if g else d for r in A_rows], float)
    return {'run_pct': f(run, 6 * C), 'run_age_min': f(age, 30.0), 'run_capped': f(capped, 0.0), 'giveback_pct': f(back, 1 * C),
            'normal_move_pct': f(normal, 0.5 * C), 'run_norm': f(norm, 12.0)}


class T06Move(unittest.TestCase):
    def test_in_c_and_median_over_waves(self):
        A = fires()                                                          # one fire a wave, 40 waves a month
        ap = ap_for(A, run=lambda m, k, coin: (10 * C if k < 21 else 2 * C), age=lambda m, k, coin: float(k), back=lambda *a: 3 * C)
        mv = look(A, randoms(A), ap=ap).move(('202510',))
        self.assertEqual((mv['fires'], mv['fires_known'], mv['waves_known']), (40, 40, 40))
        self.assertAlmostEqual(mv['run_c_median'], 10.0, places=9)          # 21 waves at 10c, 19 at 2c
        self.assertAlmostEqual(mv['run_age_min_median'], 19.5, places=9); self.assertAlmostEqual(mv['giveback_c_median'], 3.0, places=9)
        self.assertEqual(mv['capped_share'], 0.0); self.assertAlmostEqual(mv['normal_15m_c_median'], 0.5, places=9)

    def test_each_wave_once(self):
        # two fires 5 min apart (one wave) at 2c and 6c count once at 4c; a lone wave at 10c: median of (4, 10) = 7
        t0 = start('202510')
        A = [('C0', t0, -1, '202510', 0), ('C1', t0 + 300, -1, '202510', 1), ('C2', t0 + 86400, -1, '202510', 2)]
        mv = look(A, randoms(A), ap=ap_for(A, run=lambda m, k, coin: {0: 2 * C, 1: 6 * C, 2: 10 * C}[k])).move(('202510',))
        self.assertEqual(mv['waves_known'], 2); self.assertAlmostEqual(mv['run_c_median'], 7.0, places=9)

    def test_own_cost(self):
        CE = 20.0 / 100 + 0.032
        A = fires(coins=['E']); ap = ap_for(A, run=lambda *a: 5 * CE, back=lambda *a: 1 * CE)
        mv = look(A, randoms(A), ap=ap).move(('202511',))
        self.assertAlmostEqual(mv['run_c_median'], 5.0, places=9); self.assertAlmostEqual(mv['giveback_c_median'], 1.0, places=9)

    def test_not_known_and_capped(self):
        A = fires(months=('202512',), waves=10)
        ap = ap_for(A, run=lambda m, k, coin: (np.nan if k < 4 else 3 * C), capped=lambda m, k, coin: (1.0 if k >= 8 else 0.0))
        mv = look(A, randoms(A), ap=ap).move(('202512',))
        self.assertEqual((mv['fires'], mv['fires_known'], mv['waves_known']), (10, 6, 6)); self.assertAlmostEqual(mv['capped_share'], 0.2, places=9)

    def test_periods_apart_and_no_ap(self):
        A = fires(); L = look(A, randoms(A), ap=ap_for(A, run=lambda m, k, coin: (8 * C if m in M.FORWARD else 4 * C)))
        self.assertAlmostEqual(L.move(M.DESIGN)['run_c_median'], 4.0, places=9); self.assertAlmostEqual(L.move(M.FORWARD)['run_c_median'], 8.0, places=9)
        self.assertIsNone(look(A, randoms(A)).move(M.DESIGN))

    def test_misaligned_refused(self):
        A = fires(months=('202510',), waves=3)
        with self.assertRaises(M.Refused):
            look(A, randoms(A), ap=ap_for(A[:2]))

    def test_random_offer_beside_rule_1(self):
        A = fires(); L = look(A, randoms(A), Rkw={'best': lambda *a: 3 * C, 'worst': lambda *a: 2 * C})
        t = L.month_test(('202510',))
        self.assertAlmostEqual(t['random_offer_1h_median_c'], 3.0, places=9); self.assertAlmostEqual(t['offer_1h_median_c'], 5.0, places=9)


class T07Join(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def ap_file(self, rows, cols=('coin', 't', 'onset_rule') + F.AP_COLS):
        p = os.path.join(self.d, 'AP_T99.tsv')
        with open(p, 'w') as f:
            f.write('\t'.join(cols) + '\n')
            for r in rows:
                f.write('\t'.join(str(x) for x in r) + '\n')
        return p

    def test_by_coin_and_t_not_by_order(self):
        A = table([('C0', 100, -1, '202510', 0), ('C1', 200, -1, '202510', 1)])
        ap, j = F.load_ap(self.ap_file([('C1', 200, 't', 2.0, 5, 0, 0.1, 0.2, 3), ('C0', 100, 't', 1.0, '', 1, '', 0.2, 3)]), A)
        self.assertEqual(list(ap['run_pct']), [1.0, 2.0]); self.assertTrue(np.isnan(ap['run_age_min'][0])); self.assertEqual(ap['run_capped'][0], 1.0)
        self.assertTrue(np.isnan(ap['giveback_pct'][0])); self.assertEqual(ap['giveback_pct'][1], 0.1)
        self.assertEqual(j, {'fires': 2, 'ap_rows': 2, 'fires_without_row': 0, 'rows_without_fire': 0, 'rows_twice': 0})

    def test_missing_extra_twice_and_columns(self):
        A = table([('C0', 100, -1, '202510', 0), ('C1', 200, -1, '202510', 1)])
        _, j = F.load_ap(self.ap_file([('C0', 100, 't', 1, 1, 0, 0, 0.2, 2), ('C9', 300, 't', 1, 1, 0, 0, 0.2, 2)]), A)
        self.assertEqual((j['fires_without_row'], j['rows_without_fire']), (1, 1))
        _, j2 = F.load_ap(self.ap_file([('C0', 100, 't', 1, 1, 0, 0, 0.2, 2), ('C0', 100, 't', 1, 1, 0, 0, 0.2, 2), ('C1', 200, 't', 1, 1, 0, 0, 0.2, 2)]), A)
        self.assertEqual(j2['rows_twice'], 1)                                       # counted, so the move is NOT RUN (never silently kept)
        with self.assertRaises(M.Refused):
            F.load_ap(self.ap_file([('C0', 100, 't', 1, 1, 0, 0)], cols=('coin', 't', 'onset_rule', 'run_pct', 'run_age_min', 'run_capped', 'giveback_pct')), A)


class T09RulePinned(unittest.TestCase):
    """reviewer C's planted bugs that v2's tests let live: each test here kills one"""
    def rk(self):
        return {'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}

    def test_rule1_median_over_waves_not_fires(self):
        # 20 waves of 1 fire at offer 3c, 21 waves of 3 fires (offers 1c, 5c, 6c: wave mean 4c): wave median 4c, fire median 5c
        t0 = start('202510'); A = []
        for k in range(20):
            A.append(('C%d' % (k % 10), t0 + k * 7200, -1, '202510', k))
        for k in range(21):
            base = t0 + 200000 + k * 7200
            A += [('C%d' % ((k + j) % 10), base + 60 * j, -1, '202510', 100 + 3 * k + j) for j in range(3)]
        off = lambda m, k, coin, d, h: (3 * C if k < 100 else {0: 1 * C, 1: 5 * C, 2: 6 * C}[(k - 100) % 3])
        t = look(A, randoms(A), Akw={'best': off}).month_test(('202510',))
        self.assertAlmostEqual(t['offer_1h_median_c'], 4.0, places=9); self.assertEqual(t['waves_1h'], 41)

    def test_weighted_mean_and_median_with_unequal_weights(self):
        A = fires(months=('202510',), waves=30); R = randoms(A)
        w = [1 / 3.0 if i % 2 == 0 else 1 / 9.0 for i in range(len(R))]
        L = look(A, R, Rkw={'best': lambda *a: 0 * C}, w=w)
        x = np.array([4.0 if i % 2 == 0 else 1.0 for i in range(len(R))]); ww = np.array(w)
        self.assertAlmostEqual(F.wmean(x, ww), (4 / 3.0 * 45 + 1 / 9.0 * 45) / (45 / 3.0 + 45 / 9.0), places=9)
        self.assertEqual(F.wmedian(x, ww), 4.0)                                   # weighted: 3/4 of the weight sits at 4
        self.assertEqual(F.wmedian(x, np.ones(len(x))), 1.0)                     # unweighted: half and half, the lower middle
        self.assertNotAlmostEqual(F.wmean(x, ww), float(x.mean()), places=3)
        self.assertIsNotNone(L)

    def test_weights_change_the_random(self):
        A = fires(months=('202510',), waves=30, coins=['C%d' % i for i in range(7)]); R = randoms(A)   # every random coin has a cost
        rb = lambda m, k, coin, d, h: 2 * C
        Rt = table(R, best=rb, worst=lambda *a: 1 * C); At = table(A)
        Rt['BEST_60M__FADE'] = np.array([6 * C if i % 3 == 0 else 1 * C for i in range(len(R))])
        L1 = F.Look(At, Rt, np.full(len(R), 1 / 3.0), COSTS, 'FADE'); L2 = F.Look(At, Rt, np.array([1.0 if i % 3 == 0 else 1 / 9.0 for i in range(len(R))]), COSTS, 'FADE')
        e1 = L1.month_test(('202510',))['random_edge_1h_c']; e2 = L2.month_test(('202510',))['random_edge_1h_c']
        self.assertAlmostEqual(e1, (6 + 1 + 1) / 3.0 - 1, places=9); self.assertAlmostEqual(e2, (6 * 1 + 1 / 9.0 + 1 / 9.0) / (1 + 2 / 9.0) - 1, places=9)

    def test_month_needs_both_rules(self):
        # offer 5c (rule 1 true), random edge equal to the alarm's and offer-first equal: rule 2 false -> the month does not hold
        A = fires(); L = look(A, randoms(A), Rkw={'best': lambda *a: 5 * C, 'worst': lambda *a: 1 * C})
        t = L.month_test(('202510',))
        self.assertTrue(t['offer_ok']); self.assertFalse(t['beats_random']); self.assertFalse(t['holds'])

    def test_forward_months_outside_the_count(self):
        w = dict({m: 40 for m in ALL}, **{'202602': 5}); A = fires(waves=w)
        V = look(A, randoms(A), Rkw=self.rk()).verdict()
        self.assertNotIn('COUNT', V['fail'])

    def test_edge_is_a_mean_over_waves(self):
        A = fires(months=('202510',), waves=31)
        best = lambda m, k, coin, d, h: (40 * C if k == 0 else 5 * C)     # one big wave: mean above median
        t = look(A, randoms(A), Akw={'best': best}, Rkw=self.rk()).month_test(('202510',))
        self.assertAlmostEqual(t['edge_1h_c'], (39 + 30 * 4) / 31.0, places=9)
        self.assertAlmostEqual(t['edge_1h_vs_random_c'], (39 + 30 * 4) / 31.0, places=9)   # the random edge is 0 here: the rule uses the mean

    def test_excluded_coins_leave_the_random_too(self):
        A = fires(coins=['C0', 'C1']); R = [(('DASH' if i % 2 == 0 else c), t, s, m, k) for i, (c, t, s, m, k) in enumerate(randoms(A))]
        L = look(A, R, Rkw=self.rk(), drop_coins=F.EXCLUDE)
        self.assertFalse(L.useR[np.array([c == 'DASH' for c in L.R['coin']])].any())

    def test_race_uses_its_weights(self):
        P = {'kind': np.array(['A', 'A', 'R', 'R']), 'month': np.array(['2510'] * 4), 'w': np.array([1.0, 1.0, 3.0, 1.0])}
        for h in F.RACE:
            P['FADE %s' % h] = np.array([1.0, 1.0, 0.0, 1.0]); P['FOLLOW %s' % h] = np.array([0.0, 0.0, 0.0, 0.0])
        A = fires(months=('202510',), waves=2)
        r = look(A, randoms(A), perfire=P).race('202510')['1h']
        self.assertEqual(r['lean_r'], 25.0)                                       # (0 x 3 + 1 x 1) / 4

    def test_speed_per_wave(self):
        t0 = start('202510'); A = [('C0', t0, -1, '202510', 0), ('C1', t0 + 60, -1, '202510', 1), ('C2', t0 + 120, -1, '202510', 2),
                                   ('C3', t0 + 90000, -1, '202510', 3)]
        L = look(A, randoms(A), Akw={'reach_t': lambda d: 100.0})
        L.A['REACH4_180M__FADE__t'] = np.array([100.0, 200.0, 600.0, 1000.0])
        self.assertEqual(L.speed(('202510',))['FADE offer']['median_s'], 650.0)   # waves: 300 and 1000; fires would give 400

    def test_coin_share_split_across_its_wave(self):
        t0 = start('202510'); A = []
        for k in range(40):
            A.append(('C%d' % (k % 8 + 2), t0 + k * 7200, -1, '202510', k))
        A += [('C0', t0 + 400000, -1, '202510', 100), ('C1', t0 + 400060, -1, '202510', 101)]
        big = lambda m, k, coin, d, h: (60 * C if k >= 100 else 5 * C)
        ep = look(A, randoms(A), Akw={'best': big}, Rkw=self.rk()).edge_parts(('202510',))
        tot = 40 * 4.0 + 59.0                                                     # 40 waves of 5c - 1c, one wave of 60c - 1c
        self.assertAlmostEqual(ep['total'], tot, places=6)
        self.assertAlmostEqual(ep['top2_coins_share'], 59.0 / tot, places=6)       # C0 and C1 share their wave's 59c: 29.5 each


class T10Beside(unittest.TestCase):
    def test_push_flag(self):
        # edition 5: the share of design waves whose run went the side's way; 26 of 40 a month (0.65) is NO PUSH
        A = fires(); L = look(A, randoms(A), ap=ap_for(A, run=lambda m, k, coin: (-1 * C if k % 3 == 0 else 6 * C)))
        self.assertAlmostEqual(L.push_share(), 26 / 40.0, places=9); self.assertEqual(L.push(), 'NO PUSH')
        # 32 of 40 (0.8, the bar) is PUSH; the forward months do not count (all negative there)
        L = look(A, randoms(A), ap=ap_for(A, run=lambda m, k, coin: (-1 * C if (k % 5 == 0 or m in M.FORWARD) else 6 * C)))
        self.assertAlmostEqual(L.push_share(), 0.8, places=9); self.assertEqual(L.push(), 'PUSH')
        L = look(A, randoms(A), ap=ap_for(A, run=lambda m, k, coin: (np.nan if k % 2 else 6 * C)))
        self.assertEqual(L.push_share(), 1.0)                                     # a run not known leaves its fire out
        self.assertEqual(look(A, randoms(A)).push(), 'NOT RUN')

    def test_two_ap_kinds(self):
        A = fires(); L = look(A, randoms(A), ap=ap_for(A, run=lambda *a: 2 * C), aph=ap_for(A, run=lambda *a: 7 * C, back=lambda *a: 3 * C))
        self.assertAlmostEqual(L.move(M.DESIGN, 'AP')['run_c_median'], 2.0, places=9)
        mh = L.move(M.DESIGN, 'APH'); self.assertAlmostEqual(mh['run_c_median'], 7.0, places=9); self.assertAlmostEqual(mh['giveback_c_median'], 3.0, places=9)

    def test_drop_R_leaves_the_random(self):
        A = fires(months=('202510',), waves=30, coins=['C%d' % i for i in range(7)]); R = randoms(A)
        Rt = table(R, best=lambda *a: 2 * C, worst=lambda *a: 1 * C); Rt['BEST_60M__FADE'] = np.array([6 * C if i % 3 == 0 else 1 * C for i in range(len(R))])
        drop = np.array([i % 3 == 0 for i in range(len(R))])
        L = F.Look(table(A), Rt, np.full(len(R), 1 / 3.0), COSTS, 'FADE', drop_R=drop)
        self.assertAlmostEqual(L.month_test(('202510',))['random_edge_1h_c'], 0.0, places=9)   # only the 1c - 1c moments are left

    def test_prefire_mask(self):
        A = {'coin': np.array(['C0', 'C0', 'C1'], dtype=object), 't': np.array([1000, 9000, 5000], np.int64)}
        R = {'coin': np.array(['C0', 'C0', 'C1', 'C2'], dtype=object), 't': np.array([500, 1000, 1400, 4999], np.int64)}
        self.assertEqual(list(F.pre_fire_mask(A, R)), [True, False, True, False])   # 500: C0 fires at 1000; 1000: next C0 at 9000 > 1 h

    def test_coverage_and_counts(self):
        A = fires(months=('202510',), waves=30, coins=['C%d' % i for i in range(7)])
        P = {'kind': np.array(['A'] * 30), 'month': np.array(['2510'] * 30), 'w': np.ones(30), 'wave': np.array([str(i // 2) for i in range(30)])}
        for h in F.RACE:
            for s in ('FADE', 'FOLLOW'):
                P['%s %s' % (s, h)] = np.zeros(30)
        L = look(A, randoms(A), perfire=P)
        self.assertAlmostEqual(L.coverage('202510'), 30.0 / 15, places=9)         # weight 90 x 1/3 = 30 over 15 grade waves
        A2 = A + [('LIT', start('202510') + 999, -1, '202510', 99)]
        c = look(A2, randoms(A), Akw={'best': lambda m, k, coin, d, h: (np.nan if (k == 3 and h == 60) else 5 * C)}).counts('202510')
        self.assertEqual((c['fires_no_cost'], c['fires_no_cost_coins'], c['fires_no_1h']), (1, ['LIT'], 1))


class T11Inputs(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_weights_join_one_to_one(self):
        R = table([('C1', 100, -1, '202510', 0), ('C2', 200, -1, '202510', 1)]); p = os.path.join(self.d, 'W.tsv')
        open(p, 'w').write('coin\tt\tw\nC1\t100\t0.5\nC2\t200\t0.25\n'); self.assertEqual(list(F.load_w(p, R)), [0.5, 0.25])
        for txt in ('coin\tt\tw\nC1\t100\t0.5\n', 'coin\tt\tw\nC1\t100\t0.5\nC2\t200\t0.25\nC3\t300\t1\n', 'coin\tt\tw\nC1\t100\t0.5\nC1\t100\t0.5\nC2\t200\t1\n'):
            open(p, 'w').write(txt)
            with self.assertRaises(M.Refused):
                F.load_w(p, R)


def gz(p, T):
    cols = [k for k in T if k not in ('coin', 't', 'side')]
    with gzip.open(p, 'wt') as f:
        f.write('\t'.join(['coin', 't', 'side'] + cols) + '\n')
        for i in range(len(T['t'])):
            f.write('\t'.join([str(T['coin'][i]), str(int(T['t'][i])), str(int(T['side'][i]))] +
                              ['' if not np.isfinite(T[c][i]) else repr(float(T[c][i])) for c in cols]) + '\n')


class T12EndToEnd(unittest.TestCase):
    """main on files: lists, weights, targets with their sha16s, a PERFIRE, the outcome tables, both AP kinds"""
    def setUp(self):
        d = self.d = tempfile.mkdtemp()
        self.A_rows = fires(); self.R_rows = randoms(self.A_rows)
        self.A = table(self.A_rows); self.R = table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C)
        self.rc, self.apd, self.inp, self.H = (os.path.join(d, x) for x in ('rc', 'ap', 'in', 'H'))
        for x in (self.rc, self.apd, self.inp, os.path.join(self.H, 'runs')):
            os.makedirs(x)
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), self.A); gz(os.path.join(self.rc, 'RT99.tsv.gz'), self.R)
        for x in (self.rc, self.apd):
            with open(os.path.join(x, 'STAGES.tsv'), 'w') as f:
                f.write('2026-10-30T09:00:00Z\tstart\t0\tx\n2026-10-30T09:01:00Z\tend\t0\tdone\n')
        for name, rows in (('A_T99_EVENTS.tsv', self.A_rows), ('R_T99_EVENTS.tsv', self.R_rows)):
            with open(os.path.join(self.inp, name), 'w') as f:
                f.write('coin\tt\tside\ttrigger\n' + ''.join('%s\t%d\t%d\tX\n' % (c, t, s) for (c, t, s, m, k) in rows))
        with open(os.path.join(self.inp, 'R_T99_W.tsv'), 'w') as f:
            f.write('coin\tt\tw\n' + ''.join('%s\t%d\t%r\n' % (c, t, 1 / 3.0) for (c, t, s, m, k) in self.R_rows))
        for kind, run, age in (('AP', 6 * C, 30.0), ('APH', 9 * C, 50.0)):
            with open(os.path.join(self.apd, '%s_T99.tsv' % kind), 'w') as f:
                f.write('\t'.join(('coin', 't', 'onset_rule') + F.AP_COLS) + '\n')
                for (c, t, s, m, k) in reversed(self.A_rows):
                    f.write('%s\t%d\tt\t%r\t%r\t0.0\t%r\t%r\t%r\n' % (c, t, run, age if m in M.DESIGN else age + 15, 1 * C, 0.5 * C, 12.0))
        pf = os.path.join(self.H, 'runs', 'PERFIRE_V9.tsv')
        with open(pf, 'w') as f:
            f.write('kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc\tFADE 5m\tFADE 15m\tFADE 1h\tFOLLOW 5m\tFOLLOW 15m\tFOLLOW 1h\n')
            for i, (c, t, s, m, k) in enumerate(self.A_rows):
                f.write('A\t%s\t%d\t\t%s\t\t%d\t%d\t1\t\t\t1\t1\t1\t0\t0\t0\n' % (c, t, m[2:], s, i))
            for (c, t, s, m, k) in self.R_rows:
                f.write('R\t%s\t%d\t\t%s\t\t%d\t-1\t%r\t\t\t0\t0\t1\t0\t0\t0\n' % (c, t, m[2:], s, 1 / 3.0))
        self.pf = pf
        self.costs = os.path.join(d, 'costs.tsv')
        with open(self.costs, 'w') as f:
            f.write('coin\tcost_bp\n' + ''.join('%s\t%r\n' % kv for kv in COSTS.items()))

    def tearDown(self):
        shutil.rmtree(self.d)

    def targets(self, **over):
        s16 = F.s16; r = {'code': 'T99', 'alarm_ids': 'X1,X2', 'V': 'V9', 'lean': 'FADE', 'perfire': 'runs/PERFIRE_V9.tsv',
                          'perfire_sha16': s16(self.pf), 'A_sha16': s16(os.path.join(self.inp, 'A_T99_EVENTS.tsv')),
                          'R_sha16': s16(os.path.join(self.inp, 'R_T99_EVENTS.tsv')), 'W_sha16': s16(os.path.join(self.inp, 'R_T99_W.tsv'))}
        r.update(over); tg = os.path.join(self.inp, 'TARGETS_FL.tsv')
        with open(tg, 'w') as f:
            f.write('\t'.join(r) + '\n' + '\t'.join(r.values()) + '\n')
        return tg

    def run_main(self, name, *dirs, **over):
        out = os.path.join(self.d, name)
        with contextlib.redirect_stdout(io.StringIO()):
            F.main(self.targets(**over), self.H, self.costs, out, *(dirs or (self.rc, self.apd)))
        return out

    def test_full_run(self):
        out = self.run_main('o1')
        S = list(csv.DictReader(open(os.path.join(out, 'FL_SUMMARY.tsv')), delimiter='\t'))
        self.assertEqual([r['alarm_id'] for r in S], ['X1', 'X2']); s = S[0]
        self.assertEqual((s['FIRST_LOOK'], s['PUSH'], s['race']), ('PASS', 'PUSH', 'OK'))
        self.assertEqual((s['move_SepDec_run_c'], s['move_SepDec_age_min'], s['move_JanApr_age_min'], s['hour_SepDec_run_c']), ('6.00', '30', '45', '9.00'))
        self.assertEqual((s['2510_waves_1h'], s['2510_offer1h_c'], s['2510_rnd_offer1h_c']), ('40', '5.00', '2.00'))
        Mo = {r['month']: r for r in csv.DictReader(open(os.path.join(out, 'FL_T99_MONTHS.tsv')), delimiter='\t')}
        self.assertEqual((Mo['202510']['race_1h_lean_a'], Mo['202510']['race_1h_lean_r'], Mo['202510']['hour_giveback_c']), ('100.0', '100.0', '1.00'))
        self.assertEqual(Mo['202602']['top5_waves_share'], '0.12')                  # shares by month, forward too
        W = list(csv.DictReader(open(os.path.join(out, 'FL_T99_WINDOWS.tsv')), delimiter='\t'))
        self.assertEqual(sorted({r['period'] for r in W}), sorted(list(ALL) + ['Jan-Apr', 'Sep-Dec']))   # every month and both periods
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertIn('202512', J['speed']); self.assertIn('202601', J['shares']); self.assertEqual(J['push'], 'PUSH')

    def test_race_not_run_says_why(self):
        out = self.run_main('o2', perfire_sha16='0000000000000000')
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertTrue(J['race'].startswith('RACE NOT RUN: PERFIRE changed'))
        Mo = list(csv.DictReader(open(os.path.join(out, 'FL_T99_MONTHS.tsv')), delimiter='\t'))
        self.assertEqual(Mo[0]['race_1h_LEAD'], 'NOT RUN')

    def test_refusals(self):
        with self.assertRaises(M.Refused):
            self.run_main('o3', A_sha16='0000000000000000')                         # a list changed
        with self.assertRaises(M.Refused):
            self.run_main('o4', W_sha16='0000000000000000')
        A2 = dict(self.A); A2['side'] = -A2['side']; gz(os.path.join(self.rc, 'AT99.tsv.gz'), A2)
        with self.assertRaises(M.Refused):
            self.run_main('o5')                                                      # the table is not the list (sides)
        A3 = dict(self.A); A3['unit__c'] = A3['unit__c'] * 1.01; gz(os.path.join(self.rc, 'AT99.tsv.gz'), A3)
        with self.assertRaises(M.Refused):
            self.run_main('o6')                                                      # c is not the outcome tool's

    def test_an_ap_row_twice_stops_the_move(self):
        lines = open(os.path.join(self.apd, 'AP_T99.tsv')).read().splitlines()
        with open(os.path.join(self.apd, 'AP_T99.tsv'), 'a') as f:
            f.write(lines[1] + '\n')                                                # one fire twice, no fire missing, none extra
        out = self.run_main('o8')
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertTrue(J['move_spent_push_at_fire'].startswith('NOT RUN')); self.assertIn('"rows_twice": 1', J['move_spent_push_at_fire'])

    def test_a_bad_ap_file_stops_only_the_move(self):
        with open(os.path.join(self.apd, 'AP_T99.tsv'), 'a') as f:
            f.write('C0\t1\tt\t1\t1\t0\t0\t0.2\t2\n')
        out = self.run_main('o7')
        S = list(csv.DictReader(open(os.path.join(out, 'FL_SUMMARY.tsv')), delimiter='\t'))
        self.assertEqual((S[0]['move_SepDec_run_c'], S[0]['PUSH'], S[0]['FIRST_LOOK'], S[0]['hour_SepDec_run_c']), ('NOT RUN', 'NOT RUN', 'PASS', '9.00'))

# ---------------- edition 4
class T14Busy(unittest.TestCase):
    """the busy filter beside each alarm (the owner 30 Oct 11:51): the same rule on the fires whose coin's normal 15 min move >= 1.17c"""
    def test_keep_mask(self):
        A = fires(); keep = np.array([k % 2 == 0 for (c, t, s, m, k) in A])
        self.assertEqual(look(A, randoms(A), keep_A=keep).month_test(('202510',))['waves_1h'], 20)
        with self.assertRaises(M.Refused):
            look(A, randoms(A), keep_A=keep[:-1])

    def test_random_is_the_months_whole_random(self):
        A = fires(); keep = np.array([k % 2 == 0 for (c, t, s, m, k) in A])
        rk = {'best': lambda m, k, coin, d, h: (4 * C if k % 2 else 2 * C), 'worst': lambda *a: 1 * C}
        t0 = look(A, randoms(A), Rkw=rk).month_test(('202510',)); t1 = look(A, randoms(A), Rkw=rk, keep_A=keep).month_test(('202510',))
        self.assertAlmostEqual(t0['random_edge_1h_c'], t1['random_edge_1h_c'], places=12)


class T15BusyRun(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main

    def write_ap(self, normal):
        with open(os.path.join(self.apd, 'AP_T99.tsv'), 'w') as f:
            f.write('\t'.join(('coin', 't', 'onset_rule') + F.AP_COLS) + '\n')
            for (c, t, s, m, k) in self.A_rows:
                f.write('%s\t%d\tt\t%r\t30.0\t0.0\t%r\t%s\t12.0\n' % (c, t, 6 * C, 1 * C, normal(m, k)))

    def test_busy_columns_and_counts(self):
        # kept: k < 20 in design months, k < 10 in forward months (2c), and k = 20 at exactly 1.12c; out: k = 21 at 1.1c, the rest at
        # 0.5c, and one October fire with no normal move
        nm = lambda m, k: ('' if (m == '202510' and k == 39) else
                           repr((2.0 if k < (20 if m in M.DESIGN else 10) else {20: 1.12, 21: 1.1}.get(k, 0.5)) * C))
        self.write_ap(nm)
        ob = lambda m, k, coin, d, h: ((1.0 if k < 4 else (-1.0 if k < 8 else 0.0)) if d == 'FADE' else 0.0)   # first 10 pct, net 0
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=ob))
        out = self.run_main('b1'); s = list(csv.DictReader(open(os.path.join(out, 'FL_SUMMARY.tsv')), delimiter='\t'))[0]
        J = json.load(open(os.path.join(out, 'FL_T99.json'))); bf = J['busy_filter']
        self.assertEqual((bf['fires'], bf['fires_kept'], bf['fires_without_normal_move'], bf['min_c']), (320, 21 * 4 + 11 * 4, 1, 1.12))
        self.assertEqual((s['busy_waves_kept_SepDec'], s['busy_waves_kept_JanApr']), ('0.525', '0.275'))
        self.assertEqual(s['busy_FIRST_LOOK'], 'NOT PASS'); self.assertIn('COUNT', s['busy_fail'])    # 21 waves a design month < 30
        self.assertEqual(s['FIRST_LOOK'], 'PASS')                                                   # the plain result is unchanged
        self.assertEqual((s['2510_net_vs_rnd_pts'], s['2510_first']), ('0.0', '0.100')); self.assertIn('busy_only', J['variants'])

    def test_busy_not_run_without_ap(self):
        out = self.run_main('b2', self.rc)                                                          # no AP folder given
        s = list(csv.DictReader(open(os.path.join(out, 'FL_SUMMARY.tsv')), delimiter='\t'))[0]
        self.assertEqual(s['busy_FIRST_LOOK'], 'NOT RUN'); self.assertTrue(s['busy_fail'].startswith('NOT RUN: no AP_T99.tsv'))
        self.assertNotIn('busy_only', json.load(open(os.path.join(out, 'FL_T99.json')))['variants'])

# ---------------- edition 6: the owner's rule of 30 Oct 14:58 Berlin ("direction every month, money only when busy")
def obf(f):
    """obh on the FADE side from f(m, k); FOLLOW 0"""
    return lambda m, k, coin, d, h: (f(m, k) if d == 'FADE' else 0.0)


FLAT = {'best': lambda *a: 2 * C, 'worst': lambda *a: 2 * C}               # the random: offer 2c, heat 2c, edge 0, neither first


class T16Rule30(unittest.TestCase):
    def two(self, A, Akw=None, keep=None):
        """(all fires, busy fires) Looks on the same fires and random"""
        R = randoms(A); keep = np.ones(len(A), bool) if keep is None else np.asarray(keep, bool)
        return look(A, R, Akw=Akw, Rkw=FLAT), look(A, R, Akw=Akw, Rkw=FLAT, keep_A=keep)

    def test_pass(self):
        # offer first in every third wave, never heat first; offer 5c, heat 1c; every fire busy
        A = fires(); L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0)})
        v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual((v['PASS'], v['fail'], v['direction_months'], v['money_months'], v['loss_months']), ('PASS', [], 4, 4, []))
        self.assertGreater(v['z'], 2); self.assertEqual(v['months']['202510']['busy_waves'], 40)

    def test_zero_edge_fails_direction(self):
        A = fires(); L, B = self.two(A)                                          # neither level first: no direction
        v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual(v['PASS'], 'NOT PASS'); self.assertTrue(v['fail'][0].startswith('DIRECTION (0 of 4'))
        self.assertEqual(v['money_months'], 4)                                   # big moves alone are not a PASS

    def test_direction_needs_three_months_and_z(self):
        # offer first only in October and November: 2 of 4 months
        A = fires(); L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if (m in ('202510', '202511') and k % 3 == 0) else 0.0)})
        v = F.verdict6(L, B, M.DESIGN); self.assertIn('DIRECTION (2 of 4', v['fail'][0])

    def test_direction_needs_z_two(self):
        # one offer-first wave in each of Sep, Oct, Nov: 3 months above random, but over 160 waves z is about 1.77
        A = fires(); L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if (m in ('202509', '202510', '202511') and k == 0) else 0.0)})
        v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual(v['direction_months'], 3); self.assertLess(v['z'], 2); self.assertIn('DIRECTION (3 of 4, z 1.77)', v['fail'])

    def test_spread_is_the_busy_fires(self):
        # only coins C0-C2 busy (12 waves a month): their edge is all the busy edge, so 2 coins hold 2/3 of it (all fires: 1/5)
        A = fires(); keep = [c in ('C0', 'C1', 'C2') for (c, t, s, m, k) in A]
        L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0)}, keep)
        v = F.verdict6(L, B, M.DESIGN)
        self.assertAlmostEqual(v['spread_busy']['top2_coins_share'], 2 / 3.0, places=9); self.assertIn('COINS', v['fail'])

    def test_money_on_busy_fires_only(self):
        # every even wave busy with offer 5c, every odd wave quiet with offer 1c: the busy median is 5c, the all-fires median 3c
        A = fires(); keep = [k % 2 == 0 for (c, t, s, m, k) in A]
        ak = {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0), 'best': lambda m, k, coin, d, h: (5 * C if k % 2 == 0 else 1 * C)}
        L, B = self.two(A, ak, keep)
        v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual(v['money_months'], 4); self.assertAlmostEqual(v['months']['202510']['busy_offer_1h_c'], 5.0, places=9)
        self.assertLess(L.month_test(('202510',))['offer_1h_median_c'], 4)

    def test_money_three_of_four(self):
        ak = {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0), 'best': lambda m, k, coin, d, h: (3.99 * C if m in ('202510', '202511') else 5 * C)}
        A = fires(); L, B = self.two(A, ak)
        v = F.verdict6(L, B, M.DESIGN); self.assertEqual(v['money_months'], 2); self.assertIn('MONEY (2 of 4)', v['fail'])
        ak['best'] = lambda m, k, coin, d, h: (3.99 * C if m == '202510' else 5 * C)
        L, B = self.two(A, ak); v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual((v['money_months'], v['PASS']), (3, 'PASS'))
        ak['best'] = lambda m, k, coin, d, h: (4 * C if m == '202510' else 5 * C)                      # exactly 4c is money
        L, B = self.two(A, ak); self.assertEqual(F.verdict6(L, B, M.DESIGN)['money_months'], 4)

    def test_loss_month(self):
        # November's busy fires: offer 1c, heat 3c (edge -2c) against the random's 0: a LOSS, even with 3 money months
        ak = {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0), 'best': lambda m, k, coin, d, h: (1 * C if m == '202511' else 5 * C),
              'worst': lambda m, k, coin, d, h: (3 * C if m == '202511' else 1 * C)}
        A = fires(); L, B = self.two(A, ak)
        v = F.verdict6(L, B, M.DESIGN)
        self.assertEqual((v['loss_months'], v['money_months'], v['PASS']), (['202511'], 3, 'NOT PASS')); self.assertIn('LOSS (2511)', v['fail'])

    def test_thin_month_is_not_judged(self):
        # October keeps only 9 busy waves (thin): no money and no loss there, whatever its numbers
        A = fires(); keep = [not (m == '202510' and k >= 9) for (c, t, s, m, k) in A]
        ak = {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0), 'best': lambda m, k, coin, d, h: (1 * C if m == '202510' else 5 * C),
              'worst': lambda m, k, coin, d, h: (3 * C if m == '202510' else 1 * C)}
        L, B = self.two(A, ak, keep)
        v = F.verdict6(L, B, M.DESIGN); t = v['months']['202510']
        self.assertEqual((t['busy_waves'], t['thin'], t['money'], t['loss']), (9, True, False, False))
        self.assertEqual((v['thin_months'], v['loss_months'], v['money_months'], v['PASS']), (['202510'], [], 3, 'PASS'))
        keep = [not (m == '202510' and k >= 10) for (c, t, s, m, k) in A]                               # 10 busy waves: judged
        L, B = self.two(A, ak, keep); self.assertEqual(F.verdict6(L, B, M.DESIGN)['loss_months'], ['202510'])

    def test_spread_on_busy_edge(self):
        # all the busy edge from coin C0 (offer 25c there, 1c elsewhere, heat 1c): COINS fails
        ak = {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0), 'best': lambda m, k, coin, d, h: (25 * C if coin == 'C0' else 1 * C)}
        A = fires(); L, B = self.two(A, ak)
        self.assertIn('COINS', F.verdict6(L, B, M.DESIGN)['fail'])

    def test_count_and_no_ap(self):
        w = dict({m: 40 for m in ALL}, **{'202511': 29}); A = fires(waves=w)
        L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0)})
        self.assertIn('COUNT', F.verdict6(L, B, M.DESIGN)['fail'])
        v = F.verdict6(L, None, M.DESIGN)
        self.assertEqual(v['PASS'], 'NOT RUN'); self.assertTrue(v['fail'][0].startswith('NOT RUN (no AP file'))

    def test_forward_months_beside(self):
        # direction only in Jan-Apr: the design verdict fails, the same rule on the forward months passes
        A = fires(); L, B = self.two(A, {'obh': obf(lambda m, k: 1.0 if (m in M.FORWARD and k % 3 == 0) else 0.0)})
        self.assertEqual(F.verdict6(L, B, M.DESIGN)['PASS'], 'NOT PASS'); self.assertEqual(F.verdict6(L, B, M.FORWARD)['PASS'], 'PASS')


class T17Rule30Run(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main

    def test_tables(self):
        # every fire busy (normal move 2c), offer first in every third wave, nothing else changed from T12's fixture
        with open(os.path.join(self.apd, 'AP_T99.tsv'), 'w') as f:
            f.write('\t'.join(('coin', 't', 'onset_rule') + F.AP_COLS) + '\n')
            for (c, t, s, m, k) in self.A_rows:
                f.write('%s\t%d\tt\t%r\t30.0\t0.0\t%r\t%r\t12.0\n' % (c, t, 6 * C, 1 * C, 2 * C))
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(lambda m, k: 1.0 if k % 3 == 0 else 0.0)))
        out = self.run_main('r1')
        S = list(csv.DictReader(open(os.path.join(out, 'FL_RULE30.tsv')), delimiter='\t'))
        self.assertEqual([r['alarm_id'] for r in S], ['X1', 'X2']); s = S[0]
        self.assertEqual((s['RULE_30OCT'], s['fail'], s['direction_months'], s['money_months'], s['loss_months'], s['thin_months']),
                         ('PASS', '-', '4', '4', '-', '-'))
        self.assertEqual((s['FIRST_LOOK_v5'], s['fwd_RULE_30OCT'], s['2510_dir'], s['2510_money'], s['2510_loss']), ('PASS', 'PASS', '1', '1', '0'))
        Mo = list(csv.DictReader(open(os.path.join(out, 'FL_T99_RULE30.tsv')), delimiter='\t'))
        self.assertEqual([r['month'] for r in Mo], list(ALL)); self.assertEqual(Mo[1]['busy_waves'], '40'); self.assertEqual(Mo[1]['busy_offer_1h_c'], '5.00')
        J = json.load(open(os.path.join(out, 'FL_T99.json'))); self.assertEqual(J['rule_30oct']['Sep-Dec']['PASS'], 'PASS')

    def test_not_run_without_ap(self):
        out = self.run_main('r2', self.rc)
        s = list(csv.DictReader(open(os.path.join(out, 'FL_RULE30.tsv')), delimiter='\t'))[0]
        self.assertEqual(s['RULE_30OCT'], 'NOT RUN'); self.assertTrue(s['fail'].startswith('NOT RUN (no AP file'))



# ---------------- edition 7: the alarm's criteria of 30 Oct 16:00-16:06 Berlin
def world(hitA, hitR, nA=lambda m, k, coin: 2.0, nR=lambda m, kk, coin: 2.0, recA=lambda m, k, coin: 6.0, recR=lambda m, kk, coin: 6.0 if kk % 3 == 0 else 1.0,
          waves=40, extraR=(), extraA=()):
    """fires() and 3 random moments per fire (7, 8, 9 min after it, coins C(i+j+1) mod 10, kk = 3k + j); the FADE 1 h race +1 (offer first) where
    hitA(m, k, coin) / hitR(m, kk, coin) is true, else 0 (neither); busy_v1 values: normal move nA/nR in c, last hour's range recA/recR in normal moves.
    -> (L, bz)"""
    A = fires(waves=waves); R = []
    for (c, t, s, m, k) in list(A):
        for j in range(3):
            R.append(('C%d' % ((int(c[1:]) + j + 1) % 10), t + 420 + 60 * j, s, m, 3 * k + j))
    R += list(extraR); A += list(extraA)
    num = lambda v: (1.0 if v else 0.0) if isinstance(v, (bool, np.bool_)) else float(v)       # a bool: hit or not; a number: the FADE race
    ob = lambda f: (lambda m, k, coin, d, h: num(f(m, k, coin)) if d == 'FADE' else -num(f(m, k, coin)))
    TA, TR = table(A, obh=ob(hitA)), table(R, obh=ob(hitR))
    L = F.Look(TA, TR, np.full(len(R), 1 / 3.0), COSTS, 'FADE', pre_R=F.pre_fire_mask(TA, TR))
    def bzt(rows, n, rec):
        nm = np.array([n(m, k, c) * C for (c, t, s, m, k) in rows], float); rg = np.array([rec(m, k, c) for (c, t, s, m, k) in rows], float) * nm
        return {'normal_move_pct': nm, 'range60_pct': rg, 'move15_pct': nm}
    return L, {'A': bzt(A, nA, recA), 'R': bzt(R, nR, recR)}


P70 = lambda m, k, coin: k % 10 < 7                    # 70 pct of the fires hit 4c within 1 h (28 of 40 a month)
R70 = lambda m, kk, coin: (kk // 3) % 10 < 7 if kk % 3 == 0 else (kk // 3) % 10 < 1    # random: busiest band 70 pct, the rest 10 pct
Q50 = lambda m, k, coin: (k // 10) % 2 == 0            # 50 pct of the fires, the same for every coin (k // 10 is not the coin: coins follow k % 10)
D50 = lambda m, k, coin: k % 2 == 0                     # 50 pct, one hit and one miss on every day (two fires a day)
R50 = lambda m, kk, coin: ((kk // 3) // 10) % 2 == 0 if kk % 3 == 0 else (kk // 3) % 10 < 1   # random: busiest band 50 pct, the rest 10 pct


class T18Rule7(unittest.TestCase):
    def test_last_hour_explains_all_fails(self):
        # fires sit in the busiest band and hit as often as the random there: no excess; matched on the normal move only it would show +40
        L, bz = world(P70, R70); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual(v['PASS'], 'NOT PASS'); self.assertTrue(v['fail'][0].startswith('MOVES (0 of 4'))
        t = v['months']['202510']
        self.assertAlmostEqual(t['alarm_hit_share'], 0.7, places=9); self.assertAlmostEqual(t['expected_hit_share'], 0.7, places=9)
        self.assertAlmostEqual(t['normal_only_excess_pts'], 40.0, places=9); self.assertGreater(v['normal_only']['z'], 5)

    def test_more_moves_passes(self):
        L, bz = world(lambda m, k, coin: True, R70); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['PASS'], v['fail'], v['moves_months']), ('PASS', [], 4))
        self.assertAlmostEqual(v['excess_pts'], 30.0, places=9); self.assertGreater(v['z'], 2); self.assertEqual(v['matched_share'], 1.0)
        self.assertAlmostEqual(v['recent_ratio'], 1.0, places=9); self.assertAlmostEqual(v['normal_ratio'], 1.0, places=9)
        self.assertEqual(v['months']['202511']['busy_waves'], 40)

    def test_random_error_in_z(self):
        # every fire hits: each wave's excess is 0.3, so the error is the random's alone: 4 months x (1/4)^2 x 0.7 x 0.3 / 40 -> se 3.62 pts
        L, bz = world(lambda m, k, coin: True, R70); v = F.verdict7(L, bz, M.DESIGN)
        self.assertAlmostEqual(v['se_pts'], 100 * math.sqrt(4 * (0.25 ** 2) * 0.21 / 40), places=9)

    def test_busy_fires_only(self):
        # odd waves quiet (normal move 1c) and missing every 4c: they are left out; the busy fires keep the +30
        L, bz = world(lambda m, k, coin: k % 2 == 0, R70, nA=lambda m, k, coin: 2.0 if k % 2 == 0 else 1.0)
        v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['PASS'], v['months']['202510']['busy_fires'], v['months']['202510']['busy_waves']), ('PASS', 20, 20))
        self.assertAlmostEqual(v['excess_pts'], 30.0, places=9)

    def test_quiet_random_out_of_the_pool(self):
        # fires at 1.13c; the random: kk = 3k at 1.13c (70 pct hit), 3k + 1 quiet at 1.11c, 3k + 2 at 3c (both always hit), one recent band.
        # The bands come from the busy random only: 1.13c and 3c fall in different thirds and the fires' expected share is 0.7; with the
        # quiet ones in the pool the thirds move and the fires' band would take in the 3c moments too
        hr = lambda m, kk, coin: (kk // 3) % 10 < 7 if kk % 3 == 0 else True
        L, bz = world(P70, hr, nA=lambda m, k, coin: 1.13, nR=lambda m, kk, coin: (1.13, 1.11, 3.0)[kk % 3], recR=lambda m, kk, coin: 6.0)
        self.assertAlmostEqual(F.verdict7(L, bz, M.DESIGN)['months']['202510']['expected_hit_share'], 0.7, places=9)

    def test_prefire_random_out_of_the_pool(self):
        # a random moment 30 min before a same-coin fire, in the busiest band, always hitting: left out of the expected share
        extra = [(c, t - 1800, s, m, 300000 + 3 * k) for (c, t, s, m, k) in fires()]          # kk % 3 == 0: the busiest band
        L, bz = world(P70, lambda m, kk, coin: True if kk >= 300000 else R70(m, kk, coin), extraR=extra)
        self.assertEqual(int(L.preR.sum()), len(extra))
        self.assertAlmostEqual(F.verdict7(L, bz, M.DESIGN)['months']['202510']['expected_hit_share'], 0.7, places=9)

    def test_thin_month(self):
        # October keeps 9 busy waves (thin: not judged); 3 months still move -> PASS; with 10 busy waves October is judged (and moves)
        hit = lambda m, k, coin: True
        L, bz = world(hit, R70, nA=lambda m, k, coin: 2.0 if (m != '202510' or k < 9) else 1.0); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['thin_months'], v['moves_months'], v['PASS']), (['202510'], 3, 'PASS'))
        L, bz = world(hit, R70, nA=lambda m, k, coin: 2.0 if (m != '202510' or k < 10) else 1.0)
        self.assertEqual(F.verdict7(L, bz, M.DESIGN)['moves_months'], 4)

    def test_thin_band_pair_falls_back_then_unmatched(self):
        # the busiest band holds 15 random moments a month (effective count 15 < 20): the fires there are priced by the four months' 60
        # (12 of each month's 15 hit: k 0-6 and 10-14 -> 0.8); with 4 a month (16 over four months) they are unmatched, every month thin
        hr = lambda m, kk, coin: (kk // 3) % 10 < 7
        L, bz = world(lambda m, k, coin: True, hr, recR=lambda m, kk, coin: 6.0 if (kk % 3 == 0 and kk // 3 < 15) else 1.0)
        v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['busy_fires_matched'], v['matched_share'], v['fallback_share']), (160, 1.0, 1.0))
        self.assertAlmostEqual(v['months']['202510']['expected_hit_share'], 0.8, places=9)
        L, bz = world(lambda m, k, coin: True, hr, recR=lambda m, kk, coin: 6.0 if (kk % 3 == 0 and kk // 3 < 20) else 1.0)
        self.assertEqual(F.verdict7(L, bz, M.DESIGN)['fallback_share'], 0.0)                  # 20 a month: each month prices its own
        L, bz = world(lambda m, k, coin: True, hr, recR=lambda m, kk, coin: 6.0 if (kk % 3 == 0 and kk // 3 < 4) else 1.0)
        v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['busy_fires_matched'], v['matched_share'], v['thin_months']), (0, 0.0, list(M.DESIGN)))
        self.assertTrue(v['fail'][0].startswith('MOVES (0 of 4'))

    def test_three_months_and_z(self):
        two = lambda m, k, coin: True if m in ('202510', '202511') else P70(m, k, coin)
        L, bz = world(two, R70); v = F.verdict7(L, bz, M.DESIGN); self.assertTrue(v['fail'][0].startswith('MOVES (2 of 4'))
        # one extra hit in each of Sep, Oct, Nov: 3 months above 0 but z under 2
        small = lambda m, k, coin: True if (m in ('202509', '202510', '202511') and k == 7) else P70(m, k, coin)
        L, bz = world(small, R70); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual(v['moves_months'], 3); self.assertLess(v['z'], 2); self.assertTrue(v['fail'][0].startswith('MOVES (3 of 4, z'))

    def test_broad_coins(self):
        # the excess comes from C0 and C1 alone (every coin else hits as often as the random): without them the mean is 0 -> COINS
        L, bz = world(lambda m, k, coin: True if coin in ('C0', 'C1') else Q50(m, k, coin), R50); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual(sorted(v['top2_coins']), ['C0', 'C1']); self.assertAlmostEqual(v['without_top2_coins_pts'], 0.0, places=9)
        self.assertEqual(v['moves_months'], 4); self.assertTrue(any(x.startswith('COINS (without C0,C1') for x in v['fail']))
        L, bz = world(lambda m, k, coin: True if coin in ('C0', 'C1', 'C2') else Q50(m, k, coin), R50)
        self.assertFalse(any(x.startswith('COINS') for x in F.verdict7(L, bz, M.DESIGN)['fail']))     # a third coin keeps it above 0

    def test_broad_days(self):
        # every other day nets 0 (one hit, one miss); the first 5 days of a month (fires 0-9) both hit. In every month: without the 5 best days
        # (Sep's) the other months' still lift the mean, DAYS holds; in October only: without its 5 days the mean is 0 -> DAYS
        L, bz = world(lambda m, k, coin: True if k < 10 else D50(m, k, coin), R50); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual(v['best5_days'], ['20250910', '20250911', '20250912', '20250913', '20250914'])
        self.assertGreater(v['without_best5_days_pts'], 0); self.assertFalse(any(x.startswith('DAYS') for x in v['fail']))
        L, bz = world(lambda m, k, coin: True if (m == '202510' and k < 10) else D50(m, k, coin), R50); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual(v['best5_days'], ['20251001', '20251002', '20251003', '20251004', '20251005'])
        self.assertAlmostEqual(v['without_best5_days_pts'], 0.0, places=9); self.assertTrue(any(x.startswith('DAYS') for x in v['fail']))

    def test_count_and_not_run(self):
        L, bz = world(lambda m, k, coin: True, R70, waves=29); v = F.verdict7(L, bz, M.DESIGN)
        self.assertIn('COUNT', v['fail'])
        v = F.verdict7(L, None, M.DESIGN)
        self.assertEqual(v['PASS'], 'NOT RUN'); self.assertTrue(v['fail'][0].startswith('NOT RUN')); self.assertIn('lean', v)

    def test_offer_only_is_not_a_hit(self):
        # heat first counts as a 4c move as much as offer first (valid for both sides)
        L, bz = world(lambda m, k, coin: True, R70)
        A2 = dict(L.A); A2['OBH4_60M__FADE'] = -np.ones(len(A2['t']))
        L2 = F.Look(A2, L.R, L.wR, COSTS, 'FADE', pre_R=L.preR)
        self.assertAlmostEqual(F.verdict7(L2, bz, M.DESIGN)['excess_pts'], 30.0, places=9)

    def test_forward_beside_and_overall(self):
        L, bz = world(lambda m, k, coin: True if m in M.DESIGN else P70(m, k, coin), R70)
        d, w = F.verdict7(L, bz, M.DESIGN), F.verdict7(L, bz, M.FORWARD)
        self.assertEqual((d['PASS'], w['PASS'], F.overall7(d, w)), ('PASS', 'NOT PASS', 'NEEDS MORE MONTHS'))
        self.assertEqual(F.overall7(d, d), 'PASS'); self.assertEqual(F.overall7(w, d), 'NOT PASS')
        self.assertEqual(F.overall7({'PASS': 'NOT RUN'}, d), 'NOT RUN')

    def test_a_wave_counts_once(self):
        # waves k < 20 get a second fire 5 min later that misses: per wave (0.3 - 0.7) / 2 = -0.2 there, +0.3 elsewhere -> +5 pts a month
        # (per fire it would be -3.3); every coin's and every day's part adds up to the sum of the wave means
        extra = [(c, t + 300, s, m, 1000 + k) for (c, t, s, m, k) in fires() if k < 20]
        L, bz = world(lambda m, k, coin: k < 1000, R70, extraA=extra); v = F.verdict7(L, bz, M.DESIGN)
        self.assertAlmostEqual(v['months']['202510']['excess_pts'], 5.0, places=9); self.assertEqual(v['months']['202510']['busy_waves'], 40)
        X = F.match7(L, bz, M.DESIGN); S = F.stats7(L, X, M.DESIGN); tot = S['mean_pts'] / 100 * S['waves']
        self.assertAlmostEqual(sum(S['coin_parts'].values()), tot, places=9); self.assertAlmostEqual(sum(S['day_parts'].values()), tot, places=9)

    def test_busyness_ratios_and_outside(self):
        # the random's last hour: 2/3 at 1 normal move, then 5, 6, 7, 8 (1/12 each); the bands cut at 1, 6, 7, 8: fires at 5 share the band of
        # the 1s -> their random means 13/9, the fires 5: recent_ratio 45/13. Fires at 9 are busier than every random moment: outside
        rec = lambda m, kk, coin: (5.0, 6.0, 7.0, 8.0)[(kk // 3) % 4] if kk % 3 == 0 else 1.0
        L, bz = world(lambda m, k, coin: True, R70, recA=lambda m, k, coin: 5.0, recR=rec); v = F.verdict7(L, bz, M.DESIGN)
        self.assertAlmostEqual(v['recent_ratio'], 45 / 13.0, places=9); self.assertAlmostEqual(v['normal_ratio'], 1.0, places=9)
        self.assertEqual((v['matched_share'], v['outside_share'], v['fallback_share']), (1.0, 0.0, 0.0))
        L, bz = world(lambda m, k, coin: True, R70, recA=lambda m, k, coin: 9.0, recR=rec); v = F.verdict7(L, bz, M.DESIGN)
        self.assertEqual((v['busy_fires_matched'], v['outside_share']), (0, 1.0)); self.assertTrue(v['fail'][0].startswith('MOVES (0 of 4'))

    def test_wquantiles(self):
        x = np.array([1.0, 2.0, 3.0, 4.0]); w = np.array([1.0, 1.0, 1.0, 1.0])
        self.assertEqual(F.wquantiles(x, w, (0.25, 0.5, 0.75, 1.0)).tolist(), [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(F.wquantiles(x, np.array([3.0, 0.0, 0.0, 1.0]), (0.5, 0.8)).tolist(), [1.0, 4.0])


class T19Rule7Run(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main

    def bz_files(self, lists=None, drop_one=False):
        """a finished busyness job: receipts/STAGES.tsv and receipts/BZ/ (BZ_A_T99, BZ_R_T99, BUSY_V1.json); every moment busy (2c), one band"""
        rcp = os.path.join(self.d, 'busy'); bzd = os.path.join(rcp, 'BZ'); os.makedirs(bzd)
        with open(os.path.join(rcp, 'STAGES.tsv'), 'w') as f:
            f.write('2026-10-30T15:00:00Z\tstart\t0\tx\n2026-10-30T15:10:00Z\tend\t0\tdone\n')
        for k, rows in (('A', self.A_rows), ('R', self.R_rows)):
            with gzip.open(os.path.join(bzd, 'BZ_%s_T99.tsv.gz' % k), 'wt') as f:
                f.write('coin\tt\tnormal_move_pct\trange60_pct\tmove15_pct\n')
                for i, (c, t, s, m, kk) in enumerate(rows):
                    if drop_one and k == 'R' and i == 0:
                        continue
                    f.write('%s\t%d\t%r\t%r\t%r\n' % (c, t, 2 * C, 6 * C, 1 * C))
        L = lists or {'A_T99': F.s16(os.path.join(self.inp, 'A_T99_EVENTS.tsv')), 'R_T99': F.s16(os.path.join(self.inp, 'R_T99_EVENTS.tsv'))}
        with open(os.path.join(bzd, 'BUSY_V1.json'), 'w') as f:
            json.dump({'version': 'busy_v1', 'lists': {k: {'list': ['x', v]} for k, v in L.items()}}, f)
        return bzd

    def test_tables(self):
        # every fire offer first within 1 h (a 4c move); the random only after the fires k % 10 == 0 (their coins C1-C3): more moves every
        # month, both periods -> PASS
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(lambda m, k: 1.0)))
        gz(os.path.join(self.rc, 'RT99.tsv.gz'), table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C, obh=obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        out = self.run_main('s1', self.rc, self.apd, self.bz_files())
        S = list(csv.DictReader(open(os.path.join(out, 'FL_RULE7.tsv')), delimiter='\t'))
        self.assertEqual([r['alarm_id'] for r in S], ['X1', 'X2']); s = S[0]
        self.assertEqual((s['RULE_7'], s['SepDec'], s['fail'], s['moves_months'], s['JanApr']), ('PASS', 'PASS', '-', '4', 'PASS'))
        self.assertEqual((s['recent_ratio'], s['normal_ratio'], s['fwd_recent_ratio']), ('1.00', '1.00', '1.00'))
        self.assertIn(s['RULE_30OCT'], ('PASS', 'NOT PASS'))                                 # edition 6's rule stays beside
        # the expected share: the random moments with a cost (coins C0-C9), 1 in 10 of the fires' rows hit, all three of its moments
        Mo = list(csv.DictReader(open(os.path.join(out, 'FL_T99_RULE7.tsv')), delimiter='\t'))
        ex = [x for x in self.R_rows if x[0] in COSTS and x[3] == '202510']; exp = sum(1 for x in ex if x[4] % 10 == 0) / len(ex)
        self.assertEqual([r['month'] for r in Mo], list(ALL))
        self.assertEqual((Mo[1]['busy_waves'], Mo[1]['moves'], Mo[1]['expected_hit_share']), ('40', '1', '%.3f' % exp))
        self.assertEqual(s['2510_excess_pts'], '%.1f' % (100 * (1 - exp)))
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertEqual(J['rule_7']['RULE_7'], 'PASS'); self.assertEqual(J['busy_v1']['join_A']['rows_without_bz'], 0)
        self.assertIn('BZA', J['inputs'])

    def test_not_run_reasons(self):
        out = self.run_main('s2', self.rc, self.apd)                                        # no BZ tables
        s = list(csv.DictReader(open(os.path.join(out, 'FL_RULE7.tsv')), delimiter='\t'))[0]
        self.assertEqual((s['RULE_7'], s['SepDec']), ('NOT RUN', 'NOT RUN'))
        out = self.run_main('s3', self.rc, self.apd, self.bz_files(lists={'A_T99': '0' * 16, 'R_T99': '0' * 16}))
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertEqual(J['rule_7']['RULE_7'], 'NOT RUN'); self.assertTrue(J['busy_v1'].startswith('NOT RUN: busy_v1 built A_T99 from another list'))

    def test_bz_must_join_one_to_one(self):
        os.rename(self.bz_files(drop_one=True), os.path.join(self.d, 'busy', 'BZ'))
        out = self.run_main('s4', self.rc, self.apd, os.path.join(self.d, 'busy', 'BZ'))
        J = json.load(open(os.path.join(out, 'FL_T99.json')))
        self.assertTrue(J['busy_v1'].startswith('NOT RUN: BZ_R_T99 does not join')); self.assertEqual(J['rule_7']['RULE_7'], 'NOT RUN')

    def test_only_a_bz_folder_of_a_finished_job(self):
        bzd = self.bz_files(); other = os.path.join(self.d, 'busy', 'XX'); os.rename(bzd, other)
        with self.assertRaises(M.Refused):
            self.run_main('s5', self.rc, self.apd, other)                                   # not named BZ: needs its own STAGES.tsv
        os.rename(other, bzd)
        with open(os.path.join(self.d, 'busy', 'STAGES.tsv'), 'w') as f:
            f.write('2026-10-30T15:00:00Z\tstart\t0\tx\n')                                 # the job has not ended
        with self.assertRaises(M.Refused):
            self.run_main('s6', self.rc, self.apd, bzd)



# ---------------- edition 8: two bars (the owner 30 Oct 17:40-17:44 Berlin)
SIDE3 = lambda m, k, coin: 1 if k % 3 else -1          # the lean first in 26 of 40 waves a month, the other side in 14: +30 pts
EVEN = lambda m, kk, coin: 1 if kk % 2 == 0 else -1     # the random: as often one side as the other (net 0)


class T20Rule8(unittest.TestCase):
    def test_size_bar_is_edition_7(self):
        for hit in (lambda m, k, coin: True, P70, lambda m, k, coin: True if coin in ('C0', 'C1') else Q50(m, k, coin)):
            L, bz = world(hit, R70 if hit is not Q50 else R50)
            v7 = F.verdict7(L, bz, M.DESIGN); v8 = F.verdict8(L, bz, M.DESIGN)['SIZE']
            self.assertEqual((v8['PASS'], v8['z'], v8['excess_pts']), (v7['PASS'], v7['z'], v7['excess_pts']))
            self.assertEqual([x.replace('SIZE', 'MOVES') for x in v8['fail']], v7['fail'])

    def test_side_bar_is_net_test(self):
        L, bz = world(SIDE3, EVEN)
        S = F.stats7(L, F.side8(L, M.DESIGN), M.DESIGN); nt = L.net_test(M.DESIGN)
        self.assertAlmostEqual(S['mean_pts'], nt['net_vs_random_pts'], places=9); self.assertAlmostEqual(S['z'], nt['z'], places=9)
        for m in M.DESIGN:
            self.assertAlmostEqual(S['months'][m]['excess_pts'], L.month_test((m,))['net_vs_random_nopre_pts'], places=9)

    def test_side_passes_a_side_fails_none_and_the_wrong_one(self):
        L, bz = world(SIDE3, EVEN); v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual((v['PASS'], v['months_holding']), ('PASS', 4)); self.assertAlmostEqual(v['excess_pts'], 30.0, places=9)   # (26 - 14) / 40
        L, bz = world(lambda m, k, coin: 1 if k % 2 else -1, EVEN); v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual(v['PASS'], 'NOT PASS'); self.assertTrue(v['fail'][0].startswith('SIDE (0 of 4'))
        L, bz = world(lambda m, k, coin: -SIDE3(m, k, coin), EVEN)
        self.assertTrue(F.verdict8(L, bz, M.DESIGN)['SIDE']['fail'][0].startswith('SIDE (0 of 4'))

    def test_side_bar_counts_quiet_fires_too(self):
        # every fire quiet (normal move 1c): no SIZE bar to judge (no busy fire), the SIDE bar still reads them all
        L, bz = world(SIDE3, EVEN, nA=lambda m, k, coin: 1.0); v = F.verdict8(L, bz, M.DESIGN)
        self.assertEqual((v['SIDE']['PASS'], v['SIZE']['PASS']), ('PASS', 'NOT PASS')); self.assertEqual(v['SIDE']['waves'], 160)

    def test_side_broad_and_count(self):
        bal = lambda m, k, coin: 1 if (k // 10) % 2 == 0 else -1       # each coin 2 of 4 waves a month each way: net 0
        L, bz = world(lambda m, k, coin: 1 if coin in ('C0', 'C1') else bal(m, k, coin), EVEN); v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual(sorted(v['top2_coins']), ['C0', 'C1']); self.assertAlmostEqual(v['without_top2_coins_pts'], 0.0, places=9)
        self.assertTrue(any(x.startswith('COINS (without C0,C1') for x in v['fail']))
        L, bz = world(SIDE3, EVEN, waves=29); self.assertIn('COUNT', F.verdict8(L, bz, M.DESIGN)['SIDE']['fail'])

    def test_made_up_net(self):
        L, bz = world(lambda m, k, coin: 1 if k % 2 else -1, EVEN)
        net = np.array([1.0 if k % 3 else -1.0 for (c, t, s, m, k) in fires()])
        self.assertEqual(F.verdict8(L, bz, M.DESIGN, net=net)['SIDE']['PASS'], 'PASS')
        self.assertEqual(F.verdict8(L, bz, M.DESIGN)['SIDE']['PASS'], 'NOT PASS')

    def test_made_up_random(self):
        # the random's races replaced (every random moment heat first): each month's random is -1 with no error, each fire's excess its
        # race + 1; the fires' races untouched
        L, bz = world(lambda m, k, coin: 1 if k % 2 else -1, EVEN); nr = -np.ones(len(L.R['t']))
        X0 = F.side8(L, M.DESIGN); X1 = F.side8(L, M.DESIGN, net_R=nr); ok = X0['matched']
        self.assertTrue(ok.any()); self.assertTrue(np.array_equal(ok, X1['matched']))
        self.assertTrue(np.allclose(X1['p'][ok], -1.0)); self.assertTrue(np.allclose(X1['e'][ok], X0['hit'][ok] + 1.0))
        self.assertTrue(np.allclose(X1['kvar'], 0.0)); self.assertFalse(np.allclose(X0['p'][ok], -1.0))
        self.assertTrue(np.allclose(F.side8(L, M.DESIGN, net_R=L.net(L.R, 'OBH4_60M__FADE'))['e'][ok], X0['e'][ok]))

    def test_size_not_run_without_bz(self):
        L, bz = world(SIDE3, EVEN); v = F.verdict8(L, None, M.DESIGN)
        self.assertEqual((v['SIZE']['PASS'], v['SIDE']['PASS']), ('NOT RUN', 'PASS'))

    def test_overall8(self):
        P, N = {'PASS': 'PASS'}, {'PASS': 'NOT PASS'}
        self.assertEqual(F.overall8({'SIZE': P, 'SIDE': P}, {'SIZE': P, 'SIDE': P}), 'SIZE+SIDE')
        self.assertEqual(F.overall8({'SIZE': P, 'SIDE': P}, {'SIZE': N, 'SIDE': P}), 'SIDE')
        self.assertEqual(F.overall8({'SIZE': P, 'SIDE': N}, {'SIZE': P, 'SIDE': P}), 'SIZE')
        self.assertEqual(F.overall8({'SIZE': P, 'SIDE': P}, {'SIZE': N, 'SIDE': N}), 'NEEDS MORE MONTHS (SIZE+SIDE)')
        self.assertEqual(F.overall8({'SIZE': N, 'SIDE': P}, {'SIZE': P, 'SIDE': N}), 'NEEDS MORE MONTHS (SIDE)')
        self.assertEqual(F.overall8({'SIZE': N, 'SIDE': N}, {'SIZE': P, 'SIDE': P}), 'NOT PASS')
        self.assertEqual(F.overall8({'SIZE': {'PASS': 'NOT RUN'}, 'SIDE': N}, {'SIZE': {'PASS': 'NOT RUN'}, 'SIDE': N}), 'NOT PASS')


class T21Rule8Run(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main
    bz_files = T19Rule7Run.bz_files

    def test_tables(self):
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(lambda m, k: 1.0)))
        gz(os.path.join(self.rc, 'RT99.tsv.gz'), table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C, obh=obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        out = self.run_main('t1', self.rc, self.apd, self.bz_files())
        S = list(csv.DictReader(open(os.path.join(out, 'FL_RULE8.tsv')), delimiter='\t'))
        self.assertEqual([r['alarm_id'] for r in S], ['X1', 'X2']); s = S[0]
        self.assertEqual((s['RULE_8'], s['SIZE_SepDec'], s['SIDE_SepDec'], s['SIZE_JanApr'], s['SIDE_JanApr'], s['SIDE_SepDec_months'], s['RULE_7']),
                         ('SIZE+SIDE', 'PASS', 'PASS', 'PASS', 'PASS', '4', 'PASS'))
        Mo = list(csv.DictReader(open(os.path.join(out, 'FL_T99_RULE8.tsv')), delimiter='\t'))
        self.assertEqual(len(Mo), 16); self.assertEqual({r['bar'] for r in Mo}, {'SIZE', 'SIDE'}); self.assertEqual(Mo[0]['waves_1h'], '40')
        J = json.load(open(os.path.join(out, 'FL_T99.json'))); self.assertEqual(J['rule_8']['RULE_8'], 'SIZE+SIDE')

    def test_without_bz_the_side_bar_still_runs(self):
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(lambda m, k: 1.0)))
        gz(os.path.join(self.rc, 'RT99.tsv.gz'), table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C, obh=obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        out = self.run_main('t2', self.rc, self.apd)
        s = list(csv.DictReader(open(os.path.join(out, 'FL_RULE8.tsv')), delimiter='\t'))[0]
        self.assertEqual((s['RULE_8'], s['SIZE_SepDec'], s['SIDE_SepDec']), ('SIDE', 'NOT RUN', 'PASS'))


# ---------------- edition 8: planted bugs the tests above let through (mutants_fl_read_v8.py, 30 Oct 2026; each survivor gets a test, R16)
class T22Rule8Planted(unittest.TestCase):
    def test_count_reads_the_1h_value(self):
        # 11 fires a month without a 1 h offer: COUNT counts 29 waves a month (month_test's waves_1h), not the 40 with a 15 min value
        L, bz = world(SIDE3, EVEN)
        gone = np.array([k < 11 for (c, t, s, m, k) in fires()])
        L.A['BEST_60M__FADE'] = np.where(gone, np.nan, L.A['BEST_60M__FADE'])
        c = F.counts8(L, M.DESIGN)
        self.assertEqual(c, {m: L.month_test((m,))['waves_1h'] for m in M.DESIGN}); self.assertEqual(set(c.values()), {29})
        self.assertIn('COUNT', F.verdict8(L, bz, M.DESIGN)['SIDE']['fail'])

    def test_side_reads_the_1h_race(self):
        # every other window says the other side came first: the SIDE bar reads the 1 h race only
        L, bz = world(SIDE3, EVEN)
        for h in F.WINDOWS:
            if h != 60:
                for d in ('FADE', 'FOLLOW'):
                    L.A['OBH4_%dM__%s' % (h, d)] = -L.A['OBH4_60M__%s' % d]
        v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual(v['PASS'], 'PASS'); self.assertAlmostEqual(v['excess_pts'], 30.0, places=9)

    def test_side_leaves_out_fires_without_a_cost(self):
        # a fire of a coin without a cost (NOC) 6 h after each fire, its lean first every time: out of the SIDE bar
        extra = [('NOC', t + 6 * 3600, s, m, 1000 + k) for (c, t, s, m, k) in fires()]
        L, bz = world(lambda m, k, coin: 1 if coin == 'NOC' or k % 2 else -1, EVEN, extraA=extra)
        v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual((v['waves'], v['PASS']), (160, 'NOT PASS')); self.assertAlmostEqual(v['excess_pts'], 0.0, places=9)

    def test_side_wave_month_is_its_first_fire(self):
        # a fire at 23:55 on 31 October joins November's first fire (00:00) in one wave: both are priced by October's random (heat
        # first), as Look.net_test prices the wave; November's random (offer first) would price the second
        L, bz = world(SIDE3, lambda m, kk, coin: -1 if m == '202510' else 1, extraA=[('C0', start('202511') - 300, -1, '202510', 900)])
        self.assertEqual((L.wmonth[80], L.fmonth[80]), ('202510', '202511'))
        S = F.stats7(L, F.side8(L, M.DESIGN), M.DESIGN); nt = L.net_test(M.DESIGN)
        self.assertAlmostEqual(S['mean_pts'], nt['net_vs_random_pts'], places=9); self.assertAlmostEqual(S['z'], nt['z'], places=9)

    def test_side_random_leaves_prefire_moments_out(self):
        # a random moment of each fire's coin 10 min before it, offer first: a pre-fire moment, out of the month's random
        extra = [(c, t - 600, s, m, 10000 + k) for (c, t, s, m, k) in fires()]
        L, bz = world(SIDE3, lambda m, kk, coin: 1 if kk >= 10000 else EVEN(m, kk, coin), extraR=extra)
        self.assertEqual(int(L.preR.sum()), len(extra))
        self.assertAlmostEqual(F.verdict8(L, bz, M.DESIGN)['SIDE']['excess_pts'], 30.0, places=9)

    def test_side_month_without_a_random(self):
        # no random moment in December: its fires are not priced (no wave that month); the other three months still pass
        L, bz = world(SIDE3, EVEN)
        L2 = F.Look(L.A, L.R, L.wR, COSTS, 'FADE', pre_R=L.preR, drop_R=(L.rmonth == '202512'))
        v = F.verdict8(L2, bz, M.DESIGN)['SIDE']
        self.assertEqual((v['PASS'], v['months_holding'], v['waves'], v['months']['202512']['waves']), ('PASS', 3, 120, 0))

    def test_thin_month_does_not_hold(self):
        # December with 9 waves (under BUSY_WAVES_MIN = 10, lean first in 6): THIN, not judged, so 3 of 4 months hold
        L, bz = world(SIDE3, EVEN, waves=dict({m: 40 for m in ALL}, **{'202512': 9}))
        v = F.verdict8(L, bz, M.DESIGN)['SIDE']; d = v['months']['202512']
        self.assertEqual((d['waves'], d['thin'], d['holds'], v['months_holding']), (9, True, False, 3))

    def test_waves_1h_is_the_count_beside_the_bars_own_waves(self):
        # half the fires quiet (normal move 1c): the SIZE bar reads 20 busy waves a month, the COUNT column 40 waves with a 1 h value
        L, bz = world(lambda m, k, coin: True, R70, nA=lambda m, k, coin: 2.0 if k % 2 == 0 else 1.0)
        v = F.verdict8(L, bz, M.DESIGN)['SIZE']
        self.assertEqual({(x['waves'], x['waves_1h']) for x in v['months'].values()}, {(20, 40)})

    def test_two_months_are_not_enough(self):
        # the lean first in 36 of 40 waves in September and October, as often as not in November and December: z over 2, 2 of 4 months
        L, bz = world(lambda m, k, coin: (1 if k % 10 else -1) if m in ('202509', '202510') else (1 if k % 2 else -1), EVEN)
        v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual((v['months_holding'], v['PASS']), (2, 'NOT PASS')); self.assertGreaterEqual(v['z'], 2.0)
        self.assertEqual(v['fail'], ['SIDE (2 of 4, z %s)' % F.fnum(v['z'])])

    def test_four_months_without_z_are_not_enough(self):
        # every month 10 pts above a random that is offer first 45 pct and heat first 55 pct of the time, but each day's two fires go
        # the same way: 4 of 4 months, z under 2, nothing else fails
        L, bz = world(lambda m, k, coin: 1 if (k // 2) % 2 == 0 else -1, lambda m, kk, coin: 1 if kk % 20 < 9 else -1)
        v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual(v['months_holding'], 4); self.assertLess(v['z'], 2.0)
        self.assertEqual(v['fail'], ['SIDE (4 of 4, z %s)' % F.fnum(v['z'])])

    def test_verdict8_takes_the_made_up_random(self):
        # fires as often one side as the other; a made-up random half heat first, half neither (mean -0.5): SIDE passes only with it
        L, bz = world(lambda m, k, coin: 1 if k % 2 else -1, EVEN)
        nr = np.where(np.arange(len(L.R['t'])) % 2 == 0, -1.0, 0.0)
        self.assertEqual(F.verdict8(L, bz, M.DESIGN)['SIDE']['PASS'], 'NOT PASS')
        v = F.verdict8(L, bz, M.DESIGN, net_R=nr)['SIDE']
        self.assertEqual(v['PASS'], 'PASS'); self.assertAlmostEqual(v['excess_pts'], 50.0, places=9)

    def test_verdict8_uses_the_counts_it_is_given(self):
        L, bz = world(SIDE3, EVEN); v = F.verdict8(L, bz, M.DESIGN, counts={m: 29 for m in M.DESIGN})['SIDE']
        self.assertIn('COUNT', v['fail']); self.assertEqual({x['waves_1h'] for x in v['months'].values()}, {29})


class T23Rule8RunPlanted(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main
    bz_files = T19Rule7Run.bz_files

    def tables(self, fwd=1.0):
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(lambda m, k: 1.0 if m in M.DESIGN else fwd)))
        gz(os.path.join(self.rc, 'RT99.tsv.gz'), table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C, obh=obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))

    def test_jan_apr_decides_the_label(self):
        # the fires offer first in Sep-Dec only (neither in Jan-Apr): both bars pass Sep-Dec and fail Jan-Apr
        self.tables(fwd=0.0); out = self.run_main('t3', self.rc, self.apd, self.bz_files())
        s = list(csv.DictReader(open(os.path.join(out, 'FL_RULE8.tsv')), delimiter='\t'))[0]
        self.assertEqual((s['RULE_8'], s['SIZE_SepDec'], s['SIDE_SepDec'], s['SIZE_JanApr'], s['SIDE_JanApr']),
                         ('NEEDS MORE MONTHS (SIZE+SIDE)', 'PASS', 'PASS', 'NOT PASS', 'NOT PASS'))

    def test_files_hold_the_verdicts(self):
        # every cell of FL_RULE8.tsv and FL_T99_RULE8.tsv is the run's own verdict (FL_T99.json, which rounds to 4 places); a code
        # without its tables gets a NOT RUN row with every column
        self.tables(); tg = self.targets()
        with open(tg) as f:
            row = f.read().splitlines()[1]
        with open(tg, 'a') as f:
            f.write(row.replace('T99', 'T98').replace('X1,X2', 'X3') + '\n')
        out = os.path.join(self.d, 't4')
        with contextlib.redirect_stdout(io.StringIO()):
            F.main(tg, self.H, self.costs, out, self.rc, self.apd, self.bz_files())
        lines = open(os.path.join(out, 'FL_RULE8.tsv')).read().splitlines(); head = lines[0].split('\t')
        self.assertTrue(all(len(x.split('\t')) == len(head) for x in lines[1:]))
        rows = [dict(zip(head, x.split('\t'))) for x in lines[1:]]
        self.assertEqual([(x['alarm_id'], x['RULE_8']) for x in rows], [('X1', 'SIZE+SIDE'), ('X2', 'SIZE+SIDE'), ('X3', 'NOT RUN')])
        self.assertEqual({k for k, v in rows[2].items() if v}, {'alarm_id', 'code', 'V', 'lean', 'RULE_8'})
        J = json.load(open(os.path.join(out, 'FL_T99.json')))['rule_8']; s = rows[0]; near = lambda a, b, tol: abs(float(a) - b) <= tol
        for p in ('Sep-Dec', 'Jan-Apr'):
            for b in ('SIZE', 'SIDE'):
                d = J[p][b]; k = '%s_%s' % (b, p.replace('-', ''))
                self.assertEqual((s[k], s[k + '_fail'], s[k + '_months']), (d['PASS'], '; '.join(d['fail']) or '-', str(d['months_holding'])))
                self.assertTrue(near(s[k + '_z'], d['z'], 0.0051) and near(s[k + '_pts'], d['excess_pts'], 0.051), (k, s[k + '_z'], s[k + '_pts']))
        Mo = list(csv.DictReader(open(os.path.join(out, 'FL_T99_RULE8.tsv')), delimiter='\t')); self.assertEqual(len(Mo), 16)
        for r in Mo:
            t = J[r['period']][r['bar']]['months'][r['month']]
            self.assertEqual((r['waves'], r['thin'], r['holds'], r['waves_1h']), (str(t['waves']), str(int(t['thin'])), str(int(t['holds'])), str(t['waves_1h'])))
            self.assertTrue(near(r['alarm'], t['alarm'], 0.00051) and near(r['expected'], t['expected'], 0.00051)
                            and near(r['excess_pts'], t['excess_pts'], 0.051), r)


# ---------------- edition 9: Jan-Apr confirms what Sep-Dec found (the owner 30 Oct 2026 19:21 Berlin)
CONF = lambda m, k, coin: SIDE3(m, k, coin) if m in M.DESIGN else (1 if (k // 2) % 2 == 0 else -1)   # Sep-Dec +30 pts; Jan-Apr each day one way
RCONF = lambda m, kk, coin: EVEN(m, kk, coin) if m in M.DESIGN else (1 if kk % 10 < 4 else -1)         # the random: Jan-Apr offer first 40 pct


class T24Rule9(unittest.TestCase):
    def test_periods9(self):
        self.assertEqual(F.PERIODS9, (('Sep-Dec', M.DESIGN, 2.0), ('Jan-Apr', M.FORWARD, 1.0)))
        self.assertEqual((F.NET_Z_MIN, F.CONFIRM_Z_MIN), (2.0, 1.0))

    def test_jan_apr_confirms_at_z_1(self):
        # Jan-Apr: 20 pts above a random that is heat first 60 pct of the time, each day's two fires one way: z between 1 and 2
        L, bz = world(CONF, RCONF); v1 = F.verdict8(L, bz, M.FORWARD, z_min=F.CONFIRM_Z_MIN)['SIDE']; v2 = F.verdict8(L, bz, M.FORWARD)['SIDE']
        self.assertTrue(1.0 <= v1['z'] < 2.0, v1['z']); self.assertAlmostEqual(v1['excess_pts'], 20.0, places=9)
        self.assertEqual((v1['PASS'], v1['z_min'], v1['months_holding']), ('PASS', 1.0, 4))
        self.assertEqual((v2['PASS'], v2['z_min'], v2['fail']), ('NOT PASS', 2.0, ['SIDE (4 of 4, z %s)' % F.fnum(v2['z'])]))

    def test_the_z_line_reaches_both_bars(self):
        L, bz = world(CONF, RCONF)
        for zm in (1.0, 2.0, 3.5):
            v = F.verdict8(L, bz, M.FORWARD, z_min=zm); self.assertEqual((v['SIZE']['z_min'], v['SIDE']['z_min']), (zm, zm))
        self.assertEqual(F.bar8(L, F.side8(L, M.FORWARD), M.FORWARD, F.counts8(L, M.FORWARD), 'SIDE')['z_min'], F.NET_Z_MIN)

    def test_rule9_label(self):
        # Sep-Dec passes SIDE at z 2; Jan-Apr only confirms: RULE_8 NEEDS MORE MONTHS (SIDE), RULE_9 SIDE; Sep-Dec reads the same
        L, bz = world(CONF, RCONF)
        R8 = {p: F.verdict8(L, bz, ms) for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD))}
        R9 = {p: F.verdict8(L, bz, ms, z_min=zm) for p, ms, zm in F.PERIODS9}
        self.assertEqual((F.overall8(R8['Sep-Dec'], R8['Jan-Apr']), F.overall8(R9['Sep-Dec'], R9['Jan-Apr'])), ('NEEDS MORE MONTHS (SIDE)', 'SIDE'))
        self.assertEqual((R9['Sep-Dec']['SIDE']['z'], R9['Sep-Dec']['SIDE']['PASS']), (R8['Sep-Dec']['SIDE']['z'], 'PASS'))


class T25Rule9Run(unittest.TestCase):
    setUp = T12EndToEnd.setUp; tearDown = T12EndToEnd.tearDown; targets = T12EndToEnd.targets; run_main = T12EndToEnd.run_main
    bz_files = T19Rule7Run.bz_files

    def test_rule9_table_and_rule8_unchanged(self):
        # Sep-Dec: every fire offer first; Jan-Apr: each day's fires one way, against a random that leans heat first (offer first on the
        # rows of the fires k % 10 in 0, 1, 2, 8): SIDE confirms in Jan-Apr at z between 1 and 2. FL_RULE8.tsv equals edition 8's byte for byte
        import fl_read_v8 as F8
        fa = lambda m, k: 1.0 if m in M.DESIGN else (1.0 if (k // 2) % 2 == 0 else -1.0)
        fr = lambda m, k: (1.0 if k % 10 == 0 else 0.0) if m in M.DESIGN else (1.0 if k % 10 in (0, 1, 2, 8) else -1.0)
        gz(os.path.join(self.rc, 'AT99.tsv.gz'), table(self.A_rows, obh=obf(fa)))
        gz(os.path.join(self.rc, 'RT99.tsv.gz'), table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C, obh=obf(fr)))
        bzd = self.bz_files(); out = self.run_main('u1', self.rc, self.apd, bzd)
        with contextlib.redirect_stdout(io.StringIO()):
            F8.main(self.targets(), self.H, self.costs, os.path.join(self.d, 'u8'), self.rc, self.apd, bzd)
        self.assertEqual(open(os.path.join(out, 'FL_RULE8.tsv'), 'rb').read(), open(os.path.join(self.d, 'u8', 'FL_RULE8.tsv'), 'rb').read())
        head = open(os.path.join(out, 'FL_RULE9.tsv')).readline().rstrip('\n').split('\t'); self.assertEqual((head[4], head[-1]), ('RULE_9', 'RULE_8'))
        J = json.load(open(os.path.join(out, 'FL_T99.json'))); rows = list(csv.DictReader(open(os.path.join(out, 'FL_RULE9.tsv')), delimiter='\t'))
        self.assertEqual([(s['alarm_id'], s['RULE_9'], s['RULE_8']) for s in rows], [('X1', 'SIDE', 'NEEDS MORE MONTHS (SIZE+SIDE)'), ('X2', 'SIDE', 'NEEDS MORE MONTHS (SIZE+SIDE)')])
        self.assertEqual((J['rule_9']['RULE_9'], J['rule_8']['RULE_8']), ('SIDE', 'NEEDS MORE MONTHS (SIZE+SIDE)'))
        self.assertTrue(1.0 <= float(rows[0]['SIDE_JanApr_z']) < 2.0, rows[0]['SIDE_JanApr_z'])
        for s in rows:
            for p in ('Sep-Dec', 'Jan-Apr'):
                for b in ('SIZE', 'SIDE'):
                    d = J['rule_9'][p][b]; k = '%s_%s' % (b, p.replace('-', ''))
                    self.assertEqual((s[k], s[k + '_fail'], s[k + '_months']), (d['PASS'], '; '.join(d['fail']) or '-', str(d['months_holding'])))
                    self.assertEqual(d['z_min'], 2.0 if p == 'Sep-Dec' else 1.0)


# ---------------- review A (30 Oct 2026): Jan-Apr keeps every rule but the z line; the exact limits; a FOLLOW lean
def world_follow(hitF):
    """fires() and 3 random moments each (as world); the FOLLOW 1 h race from hitF (a number), the FADE race 0 everywhere -> a FOLLOW Look"""
    A = fires(); R = []
    for (c, t, s, m, k) in list(A):
        for j in range(3):
            R.append(('C%d' % ((int(c[1:]) + j + 1) % 10), t + 420 + 60 * j, s, m, 3 * k + j))
    ob = lambda f: (lambda m, k, coin, d, h: float(f(m, k, coin)) if d == 'FOLLOW' else 0.0)
    TA, TR = table(A, obh=ob(hitF)), table(R, obh=ob(EVEN))
    return F.Look(TA, TR, np.full(len(R), 1 / 3.0), COSTS, 'FOLLOW', pre_R=F.pre_fire_mask(TA, TR))


class T26Rule9Limits(unittest.TestCase):
    def jan_apr(self, L, bz):
        return F.verdict8(L, bz, M.FORWARD, z_min=F.CONFIRM_Z_MIN)['SIDE']

    def test_jan_apr_keeps_three_of_four_months(self):
        L, bz = world(lambda m, k, coin: (1 if k % 10 else -1) if m in ('202601', '202602') else (1 if k % 2 else -1), EVEN); v = self.jan_apr(L, bz)
        self.assertGreaterEqual(v['z'], 1.0); self.assertEqual((v['months_holding'], v['PASS']), (2, 'NOT PASS'))
        self.assertTrue(v['fail'][0].startswith('SIDE (2 of 4'))

    def test_jan_apr_keeps_thin(self):
        L, bz = world(SIDE3, EVEN, waves=dict({m: 40 for m in ALL}, **{'202604': 9})); v = self.jan_apr(L, bz); d = v['months']['202604']
        self.assertEqual((d['waves'], d['thin'], d['holds'], v['months_holding']), (9, True, False, 3))

    def test_jan_apr_keeps_broad_and_count(self):
        bal = lambda m, k, coin: 1 if (k // 10) % 2 == 0 else -1
        L, bz = world(lambda m, k, coin: 1 if coin in ('C0', 'C1') else bal(m, k, coin), EVEN)
        self.assertTrue(any(x.startswith('COINS (without C0,C1') for x in self.jan_apr(L, bz)['fail']))
        L, bz = world(lambda m, k, coin: 1 if (m == '202602' and k < 10) else (1 if k % 2 == 0 else -1), EVEN)
        self.assertTrue(any(x.startswith('DAYS') for x in self.jan_apr(L, bz)['fail']))
        L, bz = world(SIDE3, EVEN, waves=29); self.assertIn('COUNT', self.jan_apr(L, bz)['fail'])

    def test_z_on_the_line_passes(self):
        L, bz = world(CONF, RCONF); X = F.side8(L, M.FORWARD); c = F.counts8(L, M.FORWARD)
        z = F.bar8(L, X, M.FORWARD, c, 'SIDE', F.CONFIRM_Z_MIN)['z']; self.assertTrue(1.0 < z < 2.0)
        self.assertEqual(F.bar8(L, X, M.FORWARD, c, 'SIDE', z)['PASS'], 'PASS')
        self.assertEqual(F.bar8(L, X, M.FORWARD, c, 'SIDE', z + 1e-6)['PASS'], 'NOT PASS')

    def test_ten_waves_are_not_thin_and_thirty_count(self):
        L, bz = world(SIDE3, EVEN, waves=dict({m: 40 for m in ALL}, **{'202512': 10})); d = F.verdict8(L, bz, M.DESIGN)['SIDE']['months']['202512']
        self.assertEqual((d['waves'], d['thin'], d['holds']), (10, False, True))
        L, bz = world(SIDE3, EVEN, waves=30); v = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertNotIn('COUNT', v['fail']); self.assertEqual(set(F.counts8(L, M.DESIGN).values()), {30})

    def test_follow_lean_reads_follow(self):
        # the FOLLOW race +30 pts, the FADE race 0; half the fires without a FADE 1 h offer: the bar and COUNT read the FOLLOW side
        L = world_follow(SIDE3); L.A['BEST_60M__FADE'] = np.where(np.arange(len(L.A['t'])) % 2 == 0, np.nan, L.A['BEST_60M__FADE'])
        self.assertEqual(set(F.counts8(L, M.DESIGN).values()), {40})
        v = F.verdict8(L, None, M.DESIGN)['SIDE']; self.assertEqual(v['PASS'], 'PASS'); self.assertAlmostEqual(v['excess_pts'], 30.0, places=9)



# ---------------- edition 10: the fires' wave ids may be given (review B, 30 Oct 2026: the ladder's made-up fires keep their real waves)
RACE10 = lambda m, k, coin, d, h: (1.0 if k < 10 else -1.0) * (1.0 if d == 'FADE' else -1.0)   # fires 0-9 of a month lean first, the rest not


class T27WaveIds(unittest.TestCase):
    def test_default_is_md_v1(self):
        A = fires(); R = randoms(A); L = look(A, R, Akw={'obh': RACE10})
        self.assertTrue(np.array_equal(L.wid, M.wave_ids(L.A['t'])))
        L2 = look(A, R, Akw={'obh': RACE10}, wid=M.wave_ids(L.A['t']))
        for k in ('wid', 'wmonth', 'wday', 'useA'):
            self.assertTrue(np.array_equal(getattr(L, k), getattr(L2, k)), k)
        a, b = F.verdict8(L, None, M.DESIGN)['SIDE'], F.verdict8(L2, None, M.DESIGN)['SIDE']
        self.assertEqual((a['PASS'], a['z'], a['excess_pts'], a['waves']), (b['PASS'], b['z'], b['excess_pts'], b['waves']))

    def test_given_waves_are_the_bars_unit(self):
        # 40 fires a month 12 h apart (40 waves by md_v1); given ids put fires 0-9 of each month in one wave: 31 waves a month, that wave
        # weighted once: the SIDE excess goes from (10 - 30) / 40 to (1 - 30) / 31 against a random that never races
        A = fires(); R = randoms(A); n = len(A)
        wid = np.arange(n); k = np.array([r[4] for r in A]); mo = np.array([r[3] for r in A])
        for i, m in enumerate(sorted(set(mo.tolist()))):
            wid[(mo == m) & (k < 10)] = n + i
        L0 = look(A, R, Akw={'obh': RACE10}); L = look(A, R, Akw={'obh': RACE10}, wid=wid)
        a0, a = F.verdict8(L0, None, M.DESIGN)['SIDE'], F.verdict8(L, None, M.DESIGN)['SIDE']
        self.assertEqual((a0['waves'], a['waves']), (160, 124))
        self.assertAlmostEqual(a0['excess_pts'], 100 * (10 - 30) / 40, places=9); self.assertAlmostEqual(a['excess_pts'], 100 * (1 - 30) / 31, places=9)
        self.assertEqual(F.counts8(L, M.DESIGN), {m: 31 for m in M.DESIGN})
        self.assertEqual({m: x['waves'] for m, x in a['months'].items()}, {m: 31 for m in M.DESIGN})

    def test_wave_month_and_day_are_its_first_fires(self):
        # one given wave of a fire on 2 Nov 01:00 (first in the table) and one on 31 Oct 23:00: both read October, 31 Oct
        t1 = calendar.timegm((2025, 10, 31, 23, 0, 0)); t2 = calendar.timegm((2025, 11, 2, 1, 0, 0))
        A = [('C0', t2, -1, '202511', 0), ('C1', t1, -1, '202510', 1)]
        L = look(A, randoms(A), wid=[7, 7])
        self.assertEqual(L.wmonth.tolist(), ['202510', '202510']); self.assertEqual(L.wday.tolist(), ['20251031', '20251031'])
        self.assertEqual(F.counts8(L, ('202510', '202511')), {'202510': 1, '202511': 0})

    def test_refused_when_not_aligned(self):
        A = fires(months=('202510',), waves=3); R = randoms(A)
        for bad in ([0, 1], [0, 1, 2, 3], [0, -1, 2]):
            with self.assertRaises(M.Refused):
                look(A, R, wid=bad)
        L = look(A, R, wid=[5, 5, 9])                                       # gaps in the ids are fine
        self.assertEqual(F.counts8(L, ('202510',)), {'202510': 2}); self.assertEqual(L.first_index([5, 9]).tolist(), [0, 2])



# ---------------- edition 11: the fires' waves are the grade's (labcore, 30 min; owner 30 Oct 2026 21:11 Berlin "30 minutes")
class T28GradeWaves(unittest.TestCase):
    def test_thirty_minutes(self):
        # gaps of 20 min, exactly 30 min, 30 min and 1 s, 1 min: waves 0, 0, 0, 1, 1 (md_v1's 15 min would give 0, 1, 2, 3, 3)
        t0 = start('202510') + 3600
        A = [('C%d' % i, t0 + dt, -1, '202510', i) for i, dt in enumerate((0, 1200, 3000, 4801, 4861))]
        L = look(A, randoms(A))
        self.assertEqual(L.wid.tolist(), [0, 0, 0, 1, 1]); self.assertEqual(M.wave_ids(L.A['t']).tolist(), [0, 1, 2, 3, 3])
        self.assertEqual(F.counts8(L, ('202510',)), {'202510': 2})

    def test_the_one_wave_module(self):
        # the reader calls labcore's waves (THE ONE wave module) with the grade's gap: no copy of its own
        import labcore.waves as LW
        self.assertIs(F.WV, LW); self.assertEqual(F.GRADE_WAVE_S, 1800)
        A = fires(); L = look(A, randoms(A)); self.assertTrue(np.array_equal(L.wid, LW.waves(L.A['t'], 1800)))

    def test_given_ids_still_win(self):
        A = fires(months=('202510',), waves=3); L = look(A, randoms(A), wid=[4, 4, 4]); self.assertEqual(L.wid.tolist(), [4, 4, 4])



# ---------------- review D (30 Oct 2026, reviews/REVIEW_D_FAIR3_20261030.md, F1): the smallest proof that the fires need the random's waves
def unit_world():
    """each design month: 20 grade waves of 3 fires 20 min apart (one coin; the lean side first: +1) and 20 lone fires (the other side
    first: -1), 12 h apart; each fire's 3 random moments (randoms: 7-9 min after it, other coins) race as its fire did and weigh
    1 / (3 x the fires of its grade wave), so every grade wave weighs 1 in the random (make_random_v3). No edge: per grade wave the
    fires race as their random -> (fire rows, random rows, weights)"""
    A = []
    for m in M.DESIGN:
        for k in range(40):
            t = start(m) + k * 12 * 3600
            A += [('C%d' % (k % 10), t + 1200 * j, -1, m, k) for j in range(3 if k < 20 else 1)]
    R = randoms(A); size = {k: (3 if k < 20 else 1) for k in range(40)}
    return A, R, np.array([1.0 / (3 * size[k]) for (c, t, s, m, k) in R])


UNIT_RACE = lambda m, k, coin, d, h: (1.0 if k < 20 else -1.0) * (1.0 if d == 'FADE' else -1.0)


class T29UnitWorld(unittest.TestCase):
    """review D F1 (30 Oct 2026): the random weighs each 30 min grade wave 1. Read on the grade's waves (edition 11) a no-edge alarm whose
    big grade waves win more reads 0; read on md_v1's 15 min waves (editions 3 to 10: each fire 20 min apart its own wave) the same fires
    lean, here +50 pts. SIDE shows it alone; SIZE averages its fires per wave in the same stats7."""
    def test_grade_waves_read_zero(self):
        A, R, w = unit_world(); L = look(A, R, Akw={'obh': UNIT_RACE}, Rkw={'obh': UNIT_RACE}, w=w)
        self.assertAlmostEqual(float(np.sum(w)), 4 * 40, places=9)                              # every grade wave weighs 1
        S = F.stats7(L, F.side8(L, M.DESIGN), M.DESIGN)
        self.assertEqual(S['waves'], 4 * 40); self.assertAlmostEqual(S['mean_pts'], 0.0, places=9)
        for m in M.DESIGN:
            self.assertAlmostEqual(S['months'][m]['excess_pts'], 0.0, places=9)

    def test_fifteen_minute_waves_lean(self):
        A, R, w = unit_world(); t = np.array([x[1] for x in A], np.int64)
        L = look(A, R, Akw={'obh': UNIT_RACE}, Rkw={'obh': UNIT_RACE}, w=w, wid=M.wave_ids(t))
        S = F.stats7(L, F.side8(L, M.DESIGN), M.DESIGN)
        self.assertEqual(S['waves'], 4 * 80); self.assertAlmostEqual(S['mean_pts'], 50.0, places=9)     # (60 - 20) / 80


if __name__ == '__main__':
    unittest.main(verbosity=1)
