"""test_fl12_v1.py (SCOUT 2 Nov 2026): planted bars for edition 12: bar_v1, hit_b, the reader on Look worlds, the ladder, the files. Tests first. why: plans/PLAN_FL12_PERCOIN_BAR_20261102.md.
  python3 -B tests/test_fl12_v1.py   (from tools/alarm_first_look; needs ../money_direction, ../labcore; moment_v1 cross-check runs when ../../PLAYGROUND/tool_tests/moment_tool/code is there)"""
import copy, gzip, json, os, shutil, sys, tempfile, unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import bar_v1 as B
import fl_read_v12 as E
import fair_v5 as V
import fair_v4 as P
import test_fl_read_v11 as T8
F = E.F; M = F.M
C = T8.C
T0 = 1757462400           # 2025-09-10 00:00:00Z
DAY = 86400
MT = os.path.join(ROOT, '..', '..', 'PLAYGROUND', 'tool_tests', 'moment_tool', 'code')


class Src:
    """planted days: one coin X, mids from a function of the column; cost cells by a function of (day index, hour)"""
    def __init__(self, ndays, price=None, cell=None):
        self.days = [''.join(str(np.datetime64(T0 + k * DAY, 's').astype('datetime64[D]')).split('-')) for k in range(ndays)]
        self.price = price or (lambda j: 100.0); self.cell = cell or (lambda k, h: (5.0, 5.0, 0.0, 0.0))

    def minutes(self, d, coins):
        k = self.days.index(d); return {'X': np.array([self.price(k * 1440 + j) for j in range(1440)], float)}

    def cost_cells(self, d, coins):
        k = self.days.index(d); return {'X': np.array([[self.cell(k, h)[i] for h in range(24)] for i in range(4)], float)}


def one(src, t):
    x = B.compute(src, np.array(['X'], dtype=object), np.array([t], np.int64)); return {k: x[k][0] for k in x}


def wobble(j):
    """every hour's window peaks at a size that grows with the hour number mod 100: peaks known, line known"""
    h = (j - 1) // 60; a = 1.0 + (h % 337) / 337.0            # peak a pct in hour h, distinct over any 14 days
    return 100.0 * (1 + a / 100.0) if (j - 1) % 60 == 30 else 100.0


def line_by_hand(hours):
    return float(np.percentile(np.array([1.0 + (h % 337) / 337.0 for h in hours]), 87))


class T01Bar(unittest.TestCase):
    def test_cost_units_and_fee(self):
        self.assertAlmostEqual(B.cost_of(5.0, 7.0, 0, 0)[0], (9 + 5 + 7 + 3.2) / 100.0)

    def test_bar_is_the_larger(self):
        self.assertEqual(B.bar_of(0.1, '', 1.0), (1.0, ''))
        self.assertAlmostEqual(B.bar_of(0.3, '', 1.0)[0], 1.8)

    def test_exhausted_unknown(self):
        self.assertEqual(B.cost_of(5, 5, 0.6, 0)[1], 'EXHAUSTED_COST'); self.assertEqual(B.cost_of(5, 5, 0, 0.6)[1], 'EXHAUSTED_COST')
        self.assertEqual(B.cost_of(5, 5, 0.5, 0.5)[1], ''); self.assertEqual(B.cost_of(np.nan, 5, 0, 0)[1], 'NO_COST'); self.assertEqual(B.cost_of(5, np.nan, 0, 0)[1], 'NO_COST')

    def test_empty_share_is_unknown(self):
        # GPT 10:30:53Z: cost_of(1, 1, NaN, NaN) was known
        for a in ((1, 1, np.nan, np.nan), (1, 1, 0, np.nan), (1, 1, np.nan, 0)):
            c, w = B.cost_of(*a); self.assertTrue(np.isnan(c), a); self.assertEqual(w, 'NO_COST', a)

    def test_unknown_either_part(self):
        self.assertEqual(B.bar_of(0.2, '', np.nan)[1], 'NO_LINE'); self.assertTrue(np.isnan(B.bar_of(0.2, '', np.nan)[0]))
        self.assertEqual(B.bar_of(np.nan, 'NO_COST', 1.0)[1], 'NO_COST'); self.assertEqual(B.bar_of(np.nan, 'NO_COST', np.nan)[1], 'NO_COST+NO_LINE')

    def test_peaks_definition(self):
        m = np.full(400, 100.0); m[1 + 30] = 102.0; m[61 + 10] = 99.0
        e, v = B.hourly_peaks(m)
        self.assertEqual(e[:2].tolist(), [61, 121]); self.assertAlmostEqual(v[0], 2.0); self.assertAlmostEqual(v[1], 1.0)

    def test_peaks_under_90_pct_valued_none(self):
        m = np.full(200, 100.0); m[2:9] = np.nan
        self.assertEqual(B.hourly_peaks(m)[0][0], 121)        # 7 of 60 empty: over 10 pct: first window out
        m2 = np.full(200, 100.0); m2[1] = np.nan
        self.assertEqual(B.hourly_peaks(m2)[0][0], 121)       # no start value

    def test_peaks_exactly_90_kept(self):
        m = np.full(200, 100.0); m[2:8] = np.nan; m[30] = 105.0
        e, v = B.hourly_peaks(m); self.assertEqual(int(e[0]), 61); self.assertAlmostEqual(v[0], 5.0)
        m[2:9] = np.nan
        self.assertNotEqual(int(B.hourly_peaks(m)[0][0]), 61)

    def test_quantile_87_and_window_14_days(self):
        ends = np.arange(1, 501) * 60 + 1; vals = np.arange(500.0)
        t = 500 * 60 + 2.0; x, n = B.line_at(ends, vals, t)                        # the last 14 days: 336 peaks
        self.assertEqual(n, 336); self.assertAlmostEqual(x, float(np.percentile(vals[-336:], 87)))

    def test_min_history(self):
        ends = np.arange(1, 303) * 60 + 1; vals = np.ones(302); self.assertTrue(np.isnan(B.line_at(ends, vals, 302 * 60 + 2.0)[0]))
        ends = np.arange(1, 304) * 60 + 1; vals = np.ones(303); self.assertAlmostEqual(B.line_at(ends, vals, 303 * 60 + 2.0)[0], 1.0)

    def test_moment_tool_agrees(self):
        # definitions reused: moment_v1's hourly_peaks with cost 1 and own_line give the same line, in fractions, at a clock column just before t
        if not os.path.isdir(MT):
            self.skipTest('moment tool not here')
        sys.path.insert(0, MT); import moment_v1 as MV
        rng = np.random.default_rng(3); m = 100 * np.exp(np.cumsum(rng.normal(0, 1e-3, 20 * 1440)))
        e1, v1 = B.hourly_peaks(m); e2, v2 = MV.hourly_peaks(m, 1.0, 60)
        self.assertEqual(e1.tolist(), e2.tolist()); self.assertTrue(np.allclose(v1, v2 * 100))
        for tmin in (16 * 1440 + 17.5, 18 * 1440 + 3.25):
            self.assertAlmostEqual(B.line_at(e1, v1, tmin)[0], MV.own_line(e2, v2, int(np.ceil(tmin)) - 1, 87, 14, 303) * 100, places=10)


class T02LookAhead(unittest.TestCase):
    def plant(self, col):
        return lambda j: 200.0 if j == col else wobble(j)

    def setUp(self):
        self.src = Src(16, wobble); self.t = T0 + 15 * DAY + 3 * 3600 + 600
        self.base = one(self.src, self.t)
        self.col = (self.t - T0) // 60

    def test_hand_value(self):
        # windows start at 60 h + 1; end at 60 h + 61 strictly before the moment
        last = (self.col - 61) // 60; hours = range(last - 335, last + 1)
        self.assertEqual(self.base['line_n'], 336); self.assertAlmostEqual(self.base['line_pct'], line_by_hand(list(hours)), places=8)
        self.assertAlmostEqual(self.base['bar_pct'], max(6 * 0.222, self.base['line_pct']))

    def test_moment_own_minute_not_used(self):
        self.assertEqual(one(Src(16, self.plant(self.col)), self.t)['line_pct'], self.base['line_pct'])

    def test_later_minute_not_used(self):
        for c in (self.col + 1, self.col + 40, self.col + 2000):
            self.assertEqual(one(Src(16, self.plant(c)), self.t)['line_pct'], self.base['line_pct'])

    def test_window_ending_exactly_at_the_moment_out(self):
        t = T0 + (60 * 360 + 61) * 60; s = Src(16, wobble); x = one(s, t); y = one(Src(16, self.plant(60 * 360 + 40)), t)
        self.assertTrue(np.isfinite(x['line_pct'])); self.assertEqual(x['line_pct'], y['line_pct'])
        z = one(Src(16, self.plant(60 * 360 + 40)), t + 1)        # one second later that window has ended
        self.assertNotEqual(x['line_pct'], z['line_pct'])

    def test_a_past_window_does_count(self):
        h = (self.col - 61) // 60 - 5
        while h % 337 > 150:
            h -= 1                                                # a window under the line, so raising it moves the line
        col = h * 60 + 31
        self.assertNotEqual(one(Src(16, self.plant(col)), self.t)['line_pct'], self.base['line_pct'])

    def test_older_than_14_days_out(self):
        s = Src(30, wobble); t = T0 + 25 * DAY; a = one(s, t)['line_pct']
        self.assertEqual(one(Src(30, self.plant(1 + 60 * 5 + 30)), t)['line_pct'], a)      # 25 days back

    def test_cost_hour_cell_of_the_moment(self):
        s = Src(16, wobble, lambda k, h: (50.0, 50.0, 0, 0) if h == 3 and k == 15 else (1.0, 1.0, 0, 0))
        x = one(s, T0 + 15 * DAY + 3 * 3600 + 5); self.assertAlmostEqual(x['cost_pct'], (9 + 100 + 3.2) / 100)
        y = one(s, T0 + 15 * DAY + 3 * 3600 - 5); self.assertAlmostEqual(y['cost_pct'], (9 + 2 + 3.2) / 100)
        z = one(s, T0 + 14 * DAY + 3 * 3600 + 5); self.assertAlmostEqual(z['cost_pct'], (9 + 2 + 3.2) / 100)

    def test_early_moment_no_line(self):
        s = Src(20, wobble); x = one(s, T0 + 2 * DAY); self.assertEqual(x['why'], 'NO_LINE'); self.assertTrue(np.isnan(x['bar_pct']))

    def test_no_cost_no_bar(self):
        s = Src(20, wobble, lambda k, h: (np.nan,) * 4); x = one(s, T0 + 17 * DAY); self.assertEqual(x['why'], 'NO_COST'); self.assertTrue(np.isnan(x['bar_pct']))

    def test_window_refused(self):
        with self.assertRaises(B.Refused):
            one(Src(2), T0 + 3 * DAY)
        with self.assertRaises(B.Refused):
            one(Src(2), T0 - 1)
        with self.assertRaises(B.Refused):
            B.day_list('20260430', '20260501')
        self.assertEqual(B.day_list('20250910', '20250912'), ['20250910', '20250911', '20250912'])


def tbl(best, worst=None):
    """one row per entry; best: (fade at each window) dict h -> (fade, follow) values, others carried"""
    n = len(best); T = {}
    for h in F.WINDOWS:
        T['BEST_%dM__FADE' % h] = np.array([b[0].get(h, np.nan) for b in best], float); T['BEST_%dM__FOLLOW' % h] = np.array([b[1].get(h, np.nan) for b in best], float)
    return T


W = (1, 2, 3, 5, 10, 15, 20, 30, 60)


class T03Hit(unittest.TestCase):
    def full(self, v1, v2):
        return ({h: v1 for h in W}, {h: v2 for h in W})

    def test_over_and_under_its_dated_bar(self):
        T = tbl([self.full(1.2, 0.1), self.full(0.1, 1.2), self.full(1.1999, 0.1)])
        h, p = E.hit_b(T, np.array([1.2, 1.2, 1.2])); self.assertEqual(h.tolist(), [1.0, 1.0, 0.0]); self.assertFalse(p.any())

    def test_two_bars_same_move(self):
        # the same move: over a calm month's bar, under a dear month's
        T = tbl([self.full(1.0, 0.1), self.full(1.0, 0.1)]); h, _ = E.hit_b(T, np.array([0.9, 1.5])); self.assertEqual(h.tolist(), [1.0, 0.0])

    def test_unknown_bar_stays_unknown(self):
        T = tbl([self.full(50.0, 50.0)]); h, p = E.hit_b(T, np.array([np.nan])); self.assertTrue(np.isnan(h[0])); self.assertFalse(p[0])

    def test_gap_before_crossing_unknown(self):
        a = ({1: 0.2, 2: 0.2}, {1: 0.1, 2: 0.1}); T = tbl([a]); h, p = E.hit_b(T, np.array([1.0])); self.assertTrue(np.isnan(h[0])); self.assertTrue(p[0])

    def test_crossing_seen_before_gap_counts(self):
        a = ({1: 0.2, 2: 1.5}, {1: 0.1, 2: 0.1}); T = tbl([a]); h, p = E.hit_b(T, np.array([1.0])); self.assertEqual(h[0], 1.0); self.assertFalse(p[0])

    def test_one_direction_empty_at_60(self):
        a = ({h: 0.2 for h in W}, {h: 0.1 for h in W if h != 60}); T = tbl([a]); h, p = E.hit_b(T, np.array([1.0])); self.assertTrue(np.isnan(h[0]))

    def test_window_over_60_not_read(self):
        a = self.full(0.1, 0.1); a[0][90] = 9.0; a[0][120] = 9.0; a[0][180] = 9.0; T = tbl([a]); self.assertEqual(E.hit_b(T, np.array([1.0]))[0][0], 0.0)

    def test_path_unknown_only_when_the_bar_is_known(self):
        a = ({1: 0.2}, {1: 0.1}); T = tbl([a, a]); h, p = E.hit_b(T, np.array([1.0, np.nan])); self.assertEqual(p.tolist(), [True, False])

    def test_win60_lists(self):
        self.assertEqual(E.WIN60, W)


def hworld(hitA, hitR, barA=lambda m, k, c: 3 * C, barR=lambda m, kk, c: 3 * C, waves=40):
    """T8.world's moments with BEST = 4 c on a hit, 0.5 c on a miss, OBH4 all 0; a bar of each moment"""
    L, bz = T8.world(lambda m, k, c: False, lambda m, k, c: False, waves=waves)
    # T8.world's own order: rows rebuilt with the same generator
    A = T8.fires(waves=waves); Rr = []
    for (c, t, s, m, k) in list(A):
        for j in range(3):
            Rr.append(('C%d' % ((int(c[1:]) + j + 1) % 10), t + 420 + 60 * j, s, m, 3 * k + j))
    best = lambda f: (lambda m, k, c, d, h: (4 * C if f(m, k, c) else 0.5 * C) if d == 'FADE' else 0.1 * C)
    TA, TR = T8.table(A, best=best(hitA)), T8.table(Rr, best=best(hitR))
    bA = np.array([barA(r[3], r[4], r[0]) for r in A], float); bR = np.array([barR(r[3], r[4], r[0]) for r in Rr], float)
    return L, bz, TA, TR, bA, bR


def view(hitA, hitR, **kw):
    L, bz, TA, TR, bA, bR = hworld(hitA, hitR, **kw); hA, _ = E.hit_b(TA, bA); hR, _ = E.hit_b(TR, bR)
    return L, bz, E.size_view(L, hA, hR), hA, hR


P70, R70 = T8.P70, T8.R70
ALLM = M.DESIGN + M.FORWARD


class T04Reader(unittest.TestCase):
    def counts(self, L, ms):
        return F.counts8(L, ms)

    def test_edge_at_b_passes(self):
        L, bz, V_, _, _ = view(lambda m, k, c: True, R70)
        for p, ms, z in F.PERIODS9:
            self.assertEqual(E.size12(V_, bz, ms, self.counts(L, ms), z)['PASS'], 'PASS')

    def test_equal_hits_no_edge(self):
        L, bz, V_, _, _ = view(R70, R70)
        d = E.size12(V_, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0); self.assertEqual(d['PASS'], 'NOT PASS')

    def test_band_pair_used(self):
        # the last hour explains everything in this world (T8): matched on the band pair the excess is 0, on the normal move alone it is not
        L, bz, V_, _, _ = view(P70, R70); d = E.size12(V_, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0); self.assertAlmostEqual(d['excess_pts'], 0.0, places=6)

    def test_view_leaves_look_alone(self):
        L, bz, V_, hA, _ = view(P70, R70); ob = 'OBH4_60M__FADE'
        self.assertTrue((L.A[ob] == 0).all()); self.assertEqual(V_.A[ob].tolist(), hA.tolist()); self.assertEqual(V_.A['OBH4_60M__FOLLOW'].tolist(), (-hA).tolist())
        self.assertEqual(V_.R['OBH4_60M__FOLLOW'].tolist(), (-V_.R[ob]).tolist())

    def test_unknown_fire_never_a_miss(self):
        # fires of even k unknown: the same hit share among the rest, the excess keeps its sign and the alarm share counts the known only
        allhit = lambda m, k, c: True; L, bz, Va, hA, hR = view(allhit, R70)
        d0 = E.size12(Va, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        unk = lambda m, k, c: np.nan if k % 2 == 0 else 3 * C; L, bz, Vb, hA2, _ = view(allhit, R70, barA=unk)
        d1 = E.size12(Vb, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        self.assertTrue(np.isnan(hA2).any()); self.assertEqual(d1['months'][M.DESIGN[0]]['alarm'], 1.0); self.assertAlmostEqual(d1['excess_pts'], d0['excess_pts'], delta=1.0)
        self.assertLess(d1['waves'], d0['waves'])

    def test_unknown_random_out_of_the_pool(self):
        # the random's misses unknown: the pool has only hits, expected 1, so an all-hit alarm has no edge; never counted as misses
        allhit = lambda m, k, c: True; hr = lambda m, kk, c: kk % 2 == 0
        unkr = lambda m, kk, c: 3 * C if kk % 2 == 0 else np.nan
        L, bz, Vb, _, _ = view(allhit, hr, barR=unkr)
        d = E.size12(Vb, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0); self.assertAlmostEqual(d['months'][M.DESIGN[0]]['expected'], 1.0, places=9)

    def test_thin_month_cannot_hold_and_needs_the_rest(self):
        # the first month's bars unknown: thin, not failed; three others holding: 3 of 4, PASS; one of them failing: not
        unk = lambda m, k, c: np.nan if m == M.DESIGN[0] else 3 * C
        hr = lambda m, kk, c: False
        unkr = lambda m, kk, c: np.nan if m == M.DESIGN[0] else 3 * C
        Pp = lambda m, k, c: True
        L, bz, V1, _, _ = view(Pp, R70, barA=unk, barR=unkr); d = E.size12(V1, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        self.assertTrue(d['months'][M.DESIGN[0]]['thin']); self.assertEqual(d['months_holding'], 3); self.assertEqual(d['PASS'], 'PASS'); self.assertNotIn('COUNT', d['fail'])
        Pq = lambda m, k, c: m != M.DESIGN[1]
        L, bz, V2, _, _ = view(Pq, R70, barA=unk, barR=unkr); d = E.size12(V2, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        self.assertEqual(d['PASS'], 'NOT PASS')

    def test_random_own_bar(self):
        # the same move: the random's own high bar makes it a miss, so the fire's hit has an edge; with the fire's bar for the random, none
        allhit = lambda m, k, c: True
        L, bz, V1, _, _ = view(allhit, allhit, barR=lambda m, kk, c: 9 * C); d = E.size12(V1, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        self.assertAlmostEqual(d['months'][M.DESIGN[0]]['expected'], 0.0)
        L, bz, V2, _, _ = view(allhit, allhit); d = E.size12(V2, bz, M.DESIGN, self.counts(L, M.DESIGN), 2.0)
        self.assertAlmostEqual(d['months'][M.DESIGN[0]]['expected'], 1.0)

    def test_no_bz_not_run(self):
        L, bz, V_, _, _ = view(P70, R70); self.assertEqual(E.size12(V_, None, M.DESIGN, self.counts(L, M.DESIGN), 2.0)['PASS'], 'NOT RUN')

    def test_side_not_touched_by_view(self):
        # SIDE reads the real Look: same numbers with or without a bar reading
        L, bz = T8.world(T8.P70, T8.R70); A = copy.deepcopy(L.A['OBH4_60M__FADE']); a = F.verdict8(L, bz, M.DESIGN)['SIDE']
        E.size_view(L, np.zeros(len(L.A['t'])), np.zeros(len(L.R['t']))); b = F.verdict8(L, bz, M.DESIGN)['SIDE']
        self.assertEqual(a['z'], b['z']); self.assertEqual(a['excess_pts'], b['excess_pts']); self.assertTrue((L.A['OBH4_60M__FADE'] == A).all())


class T05Files(unittest.TestCase):
    """the whole reader on files"""
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, self.d, True)
        A = T8.fires(); Rr = []
        for (c, t, s, m, k) in list(A):
            for j in range(3):
                Rr.append(('C%d' % ((int(c[1:]) + j + 1) % 10), t + 420 + 60 * j, s, m, 3 * k + j))
        best = lambda f: (lambda m, k, c, d, h: (4 * C if f(m, k, c) else 0.5 * C) if d == 'FADE' else 0.1 * C)
        race = lambda m, k, c, d, h: 0.0
        TA, TR = T8.table(A, best=best(lambda m, k, c: True), obh=race), T8.table(Rr, best=best(R70), obh=race)
        self.idir = os.path.join(self.d, 'in'); self.rc = os.path.join(self.d, 'rc'); self.bz = os.path.join(self.d, 'bzjob', 'BZ'); self.bar = os.path.join(self.d, 'bar')
        for x in (self.idir, self.rc, self.bz, self.bar):
            os.makedirs(x)
        for jd in (self.rc, os.path.dirname(self.bz)):
            open(os.path.join(jd, 'STAGES.tsv'), 'w').write('t\tend\t0\tdone\n')
        T8.gz(os.path.join(self.rc, 'AT1.tsv.gz'), TA); T8.gz(os.path.join(self.rc, 'RT1.tsv.gz'), TR)
        def lst(p, rows):
            with open(p, 'w') as f:
                f.write('coin\tt\tside\ttrigger\n')
                for r in rows:
                    f.write('%s\t%d\t%d\tX\n' % (r[0], r[1], r[2]))
        la, lr = os.path.join(self.idir, 'A_T1_EVENTS.tsv'), os.path.join(self.idir, 'R_T1_EVENTS.tsv'); lst(la, A); lst(lr, Rr)
        with open(os.path.join(self.idir, 'R_T1_W.tsv'), 'w') as f:
            f.write('coin\tt\tw\n')
            for r in Rr:
                f.write('%s\t%d\t0.333333\n' % (r[0], r[1]))
        def bzf(name, rows, rec):
            with gzip.open(os.path.join(self.bz, 'BZ_%s_T1.tsv.gz' % name), 'wt') as f:
                f.write('coin\tt\tnormal_move_pct\trange60_pct\tmove15_pct\n')
                for r in rows:
                    n = 2 * C; f.write('%s\t%d\t%.12g\t%.12g\t%.12g\n' % (r[0], r[1], n, rec(r) * n, n))
        bzf('A', A, lambda r: 6.0); bzf('R', Rr, lambda r: 6.0 if r[4] % 3 == 0 else 1.0)
        json.dump({'version': 'busy_v1', 'lists': {'A_T1': {'list': [la, F.s16(la)]}, 'R_T1': {'list': [lr, F.s16(lr)]}}}, open(os.path.join(self.bz, 'BUSY_V1.json'), 'w'))
        def barf(name, rows, unk=lambda r: False):
            with gzip.open(os.path.join(self.bar, 'BAR_%s_T1.tsv.gz' % name), 'wt') as f:
                f.write('\t'.join(B.HEAD) + '\n')
                for r in rows:
                    f.write('%s\t%d\t\t\t0\t\tNO_COST+NO_LINE\n' % (r[0], r[1]) if unk(r) else '%s\t%d\t%.12g\t%.12g\t336\t%.12g\t\n' % (r[0], r[1], 3 * C / 6, 3 * C / 2, 3 * C))
            self.reman(name)
        self.barf = barf; self.A, self.Rr = A, Rr
        barf('A', A); barf('R', Rr)
        json.dump({'version': 'bar_v1', 'settings': B.SETTINGS, 'lists': {'A_T1': {'list': [la, F.s16(la)]}, 'R_T1': {'list': [lr, F.s16(lr)]}}}, open(os.path.join(self.bar, 'BAR_V1.json'), 'w')); self.reman('A'); self.reman('R')
        self.tg = os.path.join(self.idir, 'TARGETS_FL.tsv')
        with open(self.tg, 'w') as f:
            f.write('code\talarm_ids\tV\tlean\tperfire\tperfire_sha16\tA_sha16\tR_sha16\tW_sha16\n')
            f.write('T1\tX1,X2\tV1\tFADE\tnone.tsv\t\t%s\t%s\t%s\n' % (F.s16(la), F.s16(lr), F.s16(os.path.join(self.idir, 'R_T1_W.tsv'))))
        self.cost = os.path.join(self.d, 'costs.tsv')
        with open(self.cost, 'w') as f:
            f.write('coin\tcost_bp\tgroup\n')
            for c in T8.COSTS:
                f.write('%s\t%s\tx\n' % (c, T8.COSTS[c]))

    def reman(self, name):
        """the build's own manifest entry for a table it wrote"""
        j = os.path.join(self.bar, 'BAR_V1.json'); p = os.path.join(self.bar, 'BAR_%s_T1.tsv.gz' % name)
        if not os.path.isfile(j):
            return
        x = json.load(open(j)); e = x['lists']['%s_T1' % name]; rows = [l.split('\t') for l in gzip.open(p, 'rt').read().split('\n')[1:] if l]; why = {}
        for r in rows:
            why[r[-1] or 'KNOWN'] = why.get(r[-1] or 'KNOWN', 0) + 1
        e.update(rows=len(rows), why=why, out=[os.path.basename(p), F.s16(p)]); json.dump(x, open(j, 'w'))

    def run_it(self, out='o'):
        out = os.path.join(self.d, out)
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            E.main(self.tg, self.d, self.cost, out, self.rc, self.bz, '--bar', self.bar)
        return out

    def test_files_and_rule9_table_same_as_edition_11(self):
        o = self.run_it(); o11 = os.path.join(self.d, 'e11')
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            F.main(self.tg, self.d, self.cost, o11, self.rc, self.bz)
        for fn in sorted(os.listdir(o11)):
            if fn.endswith('.tsv'):
                self.assertEqual(F.s16(os.path.join(o, fn)), F.s16(os.path.join(o11, fn)), fn)
        for fn in ('FL_RULE12.tsv', 'FL_T1_RULE12.tsv', 'FL_RULE12_UNKNOWN.tsv', 'FL12.json'):
            self.assertTrue(os.path.isfile(os.path.join(o, fn)), fn)
        rows = list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12.tsv')), delimiter='\t')); self.assertEqual([r['alarm_id'] for r in rows], ['X1', 'X2'])
        self.assertEqual(rows[0]['SIZE_SepDec'], 'PASS'); self.assertEqual(rows[0]['SIZE11_SepDec'], 'NOT PASS')      # no 4c race planted, a hit at B planted
        self.assertTrue(E.side_same(o)); self.assertEqual(rows[0]['RULE_12'], 'SIZE'); self.assertEqual(rows[0]['changed'], '1')

    def test_unknown_table_counts(self):
        # the fires' bars rebuilt with the first month's unknown
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); os.rename(p, p + '.old'); self.barf('A', self.A, lambda r: r[3] == M.DESIGN[0])
        o = self.run_it(); u = list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12_UNKNOWN.tsv')), delimiter='\t'))
        x = {r['month']: r for r in u}; a = x[M.DESIGN[0]]
        self.assertEqual(int(a['bar_unknown']), int(a['fires'])); self.assertEqual(int(a['NO_COST']), int(a['fires'])); self.assertEqual(int(a['fires_known']), 0)
        self.assertEqual(int(x[M.DESIGN[1]]['bar_unknown']), 0); self.assertAlmostEqual(float(x[M.DESIGN[1]]['alarm_hit_share_all']), 1.0, places=2)
        m = {r['month']: r for r in T8.csv.DictReader(open(os.path.join(o, 'FL_T1_RULE12.tsv')), delimiter='\t')}
        self.assertEqual(m[M.DESIGN[0]]['thin'], '1'); self.assertEqual(m[M.DESIGN[0]]['holds'], '0'); self.assertEqual(int(m[M.DESIGN[0]]['waves_1h']), 40)

    def test_support_funnel(self):
        # the first month's fires unknown: all and busy stay, known and matched fall to 0, whole waves go; the other months keep all; the funnel only narrows
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); os.rename(p, p + '.old'); self.barf('A', self.A, lambda r: r[3] == M.DESIGN[0])
        o = self.run_it('o5'); x = {r['month']: r for r in T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12_SUPPORT.tsv')), delimiter='\t')}
        a, b = x[M.DESIGN[0]], x[M.DESIGN[1]]
        self.assertEqual((a['fires_all'], a['fires_busy'], a['fires_known'], a['fires_matched']), ('40', '40', '0', '0'))
        self.assertEqual((a['waves_all'], a['waves_known'], a['waves_matched']), ('40', '0', '0')); self.assertEqual(len(x), 8)
        self.assertEqual((b['fires_all'], b['fires_known'], b['fires_matched'], b['waves_matched']), ('40', '40', '40', '40'))
        self.assertEqual(int(b['random_all']), 120); self.assertEqual(int(b['random_busy']), 120); self.assertEqual(int(b['random_known']), 120)

    def test_support_random_known(self):
        p = os.path.join(self.bar, 'BAR_R_T1.tsv.gz'); os.rename(p, p + '.old'); self.barf('R', self.Rr, lambda r: r[4] % 3 == 0)
        o = self.run_it('o6'); x = {r['month']: r for r in T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12_SUPPORT.tsv')), delimiter='\t')}
        self.assertEqual(int(x[M.DESIGN[1]]['random_busy']), 120); self.assertEqual(int(x[M.DESIGN[1]]['random_known']), 80)

    def test_side_guard(self):
        o = self.run_it(); self.assertTrue(E.side_same(o))
        p = os.path.join(o, 'FL_RULE12.tsv'); txt = open(p).read().split('\n'); h = txt[0].split('\t'); i = h.index('SIDE_SepDec_pts'); x = txt[1].split('\t'); x[i] = '999'; txt[1] = '\t'.join(x)
        open(p, 'w').write('\n'.join(txt)); self.assertFalse(E.side_same(o))
        old = E.side_same; E.side_same = lambda out: False
        try:
            with self.assertRaises(M.Refused):
                self.run_it('o2')
        finally:
            E.side_same = old
        self.assertFalse(os.path.exists(os.path.join(self.d, 'o2'))); self.assertFalse(os.path.exists(os.path.join(self.d, 'o2.e11')))

    def test_bad_bar_header_refused(self):
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); os.rename(p, p + '.old')
        with gzip.open(p, 'wt') as f:
            f.write('coin\tt\tbar_pct\nX\t1\t1\n')
        x = json.load(open(os.path.join(self.bar, 'BAR_V1.json'))); x['lists']['A_T1']['out'][1] = F.s16(p); json.dump(x, open(os.path.join(self.bar, 'BAR_V1.json'), 'w'))
        with self.assertRaises(M.Refused) as c:
            self.run_it('o3')
        self.assertIn('BAR HEADER', str(c.exception))

    def test_extra_bar_row_not_run(self):
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); os.rename(p, p + '.old'); self.barf('A', self.A + [('C1', 1757500000, 1, M.DESIGN[0], 0)])
        o = self.run_it('o4'); self.assertEqual(list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12.tsv')), delimiter='\t'))[0]['RULE_12'], 'NOT RUN')

    def test_refused(self):
        with self.assertRaises(M.Refused):
            E.main(self.tg, self.d, self.cost, os.path.join(self.d, 'x'), self.rc, self.bz)
        with self.assertRaises(M.Refused):
            E.main(self.tg, self.d, self.cost, os.path.join(self.d, 'x'), self.rc, self.bz, '--bar', self.d)
        self.assertFalse(os.path.exists(os.path.join(self.d, 'x')))

    def test_bar_from_another_list_not_run(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); x['lists']['A_T1']['list'][1] = 'bad'; json.dump(x, open(j, 'w'))
        o = self.run_it(); r = list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12.tsv')), delimiter='\t'))[0]; self.assertEqual(r['RULE_12'], 'NOT RUN'); self.assertEqual(r['SIZE_SepDec'], 'NOT RUN')

    def test_join_not_one_to_one(self):
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); os.rename(p, p + '.old'); self.barf('A', self.A[:-1])
        o = self.run_it(); self.assertEqual(list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12.tsv')), delimiter='\t'))[0]['RULE_12'], 'NOT RUN')

    def test_ladder_on_files(self):
        o = os.path.join(self.d, 'f')
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            rc = V.main([self.tg, self.d, self.cost, o, '2', '10', '--bar', self.bar, '--plant-seeds', '1', '--seed-base', '7', self.rc, self.bz])
        self.assertEqual(rc, 0); rows = list(T8.csv.DictReader(open(os.path.join(o, 'FAIR_RUNS.tsv')), delimiter='\t'))
        self.assertEqual(sorted({r['seed'] for r in rows if r['kind'] == 'null'}), ['7', '8'])
        self.assertEqual({r['bar'] for r in rows if r['kind'] == 'size_plant'}, {'SIZE'}); man = json.load(open(os.path.join(o, 'FAIR_V5.json'))); self.assertEqual(man['settings']['seed_base'], 7); self.assertIn('null_SIZE_both', man)


class T08Admit(T05Files):
    """GPT HOLD 2 (10:30:53Z): the threshold table a reader or ladder consumes is the one its manifest records; refused before a verdict"""
    def plant(self, fix, name='A', man=True):
        """rewrite one bar table's rows; man: the manifest follows (bytes agree, so the row checks must speak), else unchanged"""
        p = os.path.join(self.bar, 'BAR_%s_T1.tsv.gz' % name); h, *rows = gzip.open(p, 'rt').read().split('\n'); rows = [r for r in rows if r]; rows = fix(rows)
        with gzip.open(p, 'wt') as f:
            f.write('\n'.join([h] + rows) + '\n')
        if man:
            self.reman(name)

    def row0(self, f):
        return lambda rows: ['\t'.join(f(rows[0].split('\t')))] + rows[1:]

    def refused(self, want):
        with self.assertRaises(M.Refused) as c:
            self.run_it('oz')
        self.assertIn(want, str(c.exception)); self.assertFalse(os.path.exists(os.path.join(self.d, 'oz'))); self.assertFalse(os.path.exists(os.path.join(self.d, 'oz.e11')))

    def ladder(self):
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            return V.main([self.tg, self.d, self.cost, os.path.join(self.d, 'lz'), '1', '10', '--bar', self.bar, '--plant-seeds', '1', self.rc, self.bz])

    def set_bar(self, v):
        def f(x):
            x[5] = v; return x
        return self.row0(f)

    def test_hold_reader_refuses_changed_threshold_manifest_unchanged(self):
        self.plant(self.set_bar('9.0'), man=False); self.refused('BAR DIGEST')

    def test_hold_ladder_refuses_it_and_leaves_nothing(self):
        self.plant(self.set_bar('9.0'), man=False)
        with self.assertRaises(M.Refused):
            self.ladder()
        self.assertFalse(os.path.exists(os.path.join(self.d, 'lz'))); self.assertFalse(os.path.exists(os.path.join(self.d, 'lz.part')))

    def test_random_side_too(self):
        self.plant(self.set_bar('9.0'), 'R', man=False); self.refused('BAR DIGEST')

    def test_same_values_other_bytes_refused(self):
        p = os.path.join(self.bar, 'BAR_A_T1.tsv.gz'); b = gzip.decompress(open(p, 'rb').read())
        with open(p, 'wb') as f:
            f.write(gzip.compress(b, 1) + b'')
        x = json.load(open(os.path.join(self.bar, 'BAR_V1.json')))['lists']['A_T1']['out'][1]
        if F.s16(p) != x:
            self.refused('BAR DIGEST')

    def test_manifest_without_output(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); del x['lists']['A_T1']['out']; json.dump(x, open(j, 'w')); self.refused('NAMES NO OUTPUT')

    def test_manifest_names_another_file(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); x['lists']['A_T1']['out'][0] = 'BAR_R_T1.tsv.gz'; json.dump(x, open(j, 'w')); self.refused('NAMES NO OUTPUT')

    def test_another_edition(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); x['version'] = 'bar_v0'; json.dump(x, open(j, 'w')); self.refused('BAR PRODUCER')

    def test_other_settings(self):
        for k in sorted(B.SETTINGS):
            j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); keep = x['settings'][k]; x['settings'][k] = keep + 1; json.dump(x, open(j, 'w')); self.refused('BAR PRODUCER'); x['settings'][k] = keep; json.dump(x, open(j, 'w'))

    def test_no_settings(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); del x['settings']; json.dump(x, open(j, 'w')); self.refused('BAR PRODUCER')

    def test_table_and_manifest_changed_together_threshold(self):
        self.plant(self.set_bar('9.0')); self.refused('BAR ROW')

    def test_known_threshold_with_a_reason(self):
        def f(x):
            x[6] = 'NO_COST'; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_unknown_threshold_without_a_reason(self):
        self.plant(self.set_bar('')); self.refused('BAR ROW')

    def test_a_count_short_of_the_line(self):
        def f(x):
            x[4] = '302'; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_empty_line_marked_known(self):
        def f(x):
            x[3] = ''; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_empty_cost_marked_known(self):
        def f(x):
            x[2] = ''; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_inf_and_nan_text(self):
        for v in ('inf', 'nan', '-1', 'x'):
            self.plant(self.set_bar(v)); self.refused('BAR ROW')
            self.plant(self.set_bar('%.12g' % (3 * C)))

    def test_unknown_reason_word(self):
        def f(x):
            x[2:6] = ['', '', '0', '']; x[6] = 'NO_COST+NO_LINE+WHO'; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_line_valued_but_marked_no_line(self):
        def f(x):
            x[5] = ''; x[2] = ''; x[6] = 'NO_COST+NO_LINE'; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_negative_cost_under_a_true_max(self):
        def f(x):
            x[2] = '-0.01'; x[5] = x[3]; return x
        self.plant(self.row0(f)); self.refused('BAR ROW')

    def test_rows_differ_from_manifest(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); x['lists']['A_T1']['rows'] += 1; json.dump(x, open(j, 'w')); self.refused('BAR ROWS')

    def test_reasons_differ_from_manifest(self):
        j = os.path.join(self.bar, 'BAR_V1.json'); x = json.load(open(j)); x['lists']['A_T1']['why'] = {'KNOWN': 1}; json.dump(x, open(j, 'w')); self.refused('BAR REASONS')

    def test_genuine_reads_and_v11_label_stays_beside(self):
        o = self.run_it(); r = list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE12.tsv')), delimiter='\t'))[0]; r9 = list(T8.csv.DictReader(open(os.path.join(o, 'FL_RULE9.tsv')), delimiter='\t'))[0]
        self.assertEqual(r['RULE_9'], r9['RULE_9']); self.assertNotEqual(r['RULE_12'], r['RULE_9']); self.assertIn('retrospective', json.load(open(os.path.join(o, 'FL12.json')))['labels_read'])

    def test_the_build_writes_what_the_reader_admits(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True); src = Src(18, wobble); p = os.path.join(d, 'l.tsv')
        with open(p, 'w') as f:
            f.write('coin\tt\tside\nX\t%d\t1\nX\t%d\t1\n' % (T0 + DAY, T0 + 17 * DAY))
        o = os.path.join(d, 'B')
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            B.build(src, o, [(p, 'A_T1'), (p, 'R_T1')])
        T = {'coin': np.array(['X', 'X']), 't': np.array([T0 + DAY, T0 + 17 * DAY])}; x, _ = E.bars_of('T1', {'A_sha16': F.s16(p), 'R_sha16': F.s16(p)}, o, T, T); self.assertEqual(x['A'][1].tolist(), ['NO_LINE', ''])


class T06Ladder(unittest.TestCase):
    def setUp(self):
        L, TR, w, bz = T8FW()
        self.L, self.R, self.w, self.bz = L, TR, w, bz; n = len(TR['t'])
        self.bars = {'A': (np.full(len(L.A['t']), 3 * C), np.full(len(L.A['t']), '', dtype=object)), 'R': (np.full(n, 3 * C), np.full(n, '', dtype=object))}
        self.r0 = {'code': 'T99', 'alarm_ids': 'X1'}

    def go(self, seeds=2, plants=(10,), ps=1, base=0):
        return V.ladder(self.r0, self.L, self.R, self.w, T8.COSTS, self.bz, self.bars, seeds, list(plants), ps, base)

    def test_side_rows_equal_fair_v4(self):
        a = [x for x in self.go() if x['bar'] == 'SIDE']; b = [x for x in P.ladder(self.r0, self.L, self.R, self.w, T8.COSTS, self.bz, 2, [10], 1) if x['bar'] == 'SIDE']
        key = lambda x: (x['kind'], x['plant'], x['seed'], x['period'])
        self.assertEqual(len(a), len(b))
        for x, y in zip(sorted(a, key=key), sorted(b, key=key)):
            self.assertEqual((x['PASS'], x['z'] if np.isfinite(x['z']) else 0, x['excess_pts'] if np.isfinite(x['excess_pts']) else 0), (y['PASS'], y['z'] if np.isfinite(y['z']) else 0, y['excess_pts'] if np.isfinite(y['excess_pts']) else 0))

    def test_seed_base_moves_draws(self):
        s = lambda rows: [x['z'] for x in rows if x['kind'] == 'null' and x['bar'] == 'SIZE']
        self.assertNotEqual(s(self.go(base=0)), s(self.go(base=500)))
        self.assertEqual({x['seed'] for x in self.go(base=500) if x['kind'] == 'null'}, {500, 501})

    def test_real_row_is_the_readers(self):
        b = np.full(len(self.L.A['t']), 3 * C); b[::3] = 9 * C; self.bars['A'] = (b, self.bars['A'][1])    # a dear bar on a third of the fires
        hA, _ = E.hit_b(self.L.A, self.bars['A'][0]); hR, _ = E.hit_b(self.R, self.bars['R'][0]); Vw = E.size_view(self.L, hA, hR); ms = M.DESIGN
        d = E.size12(Vw, self.bz, ms, F.counts8(self.L, ms), 2.0)
        r = [x for x in self.go(0, (), 0) if x['kind'] == 'real' and x['bar'] == 'SIZE' and x['period'] == 'Sep-Dec'][0]; self.assertEqual(r['PASS'], d['PASS'])
        self.assertEqual(r['excess_pts'], d['excess_pts']); self.assertEqual(r['z'], d['z'])
        o = F.verdict8(self.L, self.bz, ms)['SIZE']; self.assertNotEqual(o['excess_pts'], d['excess_pts'])    # edition 11's fixed reading differs in this world

    def test_unknown_stays_unknown_in_the_null(self):
        # every moment hits; half the random's bars unknown: the made-up fires and their random both hit all, excess 0; an unknown read as a miss on either side moves it
        L, R, w, bz = T8FW(lambda m, k, c, d, h: 4 * C if d == 'FADE' else 0.1 * C); n = len(R['t']); b = np.full(n, 3 * C); b[::2] = np.nan
        bars = {'A': (np.full(len(L.A['t']), 3 * C), np.full(len(L.A['t']), '', dtype=object)), 'R': (b, np.full(n, '', dtype=object))}
        rows = V.ladder(self.r0, L, R, w, T8.COSTS, bz, bars, 3, [], 0)
        x = [q['excess_pts'] for q in rows if q['kind'] == 'null' and q['bar'] == 'SIZE' and np.isfinite(q['excess_pts'])]
        self.assertTrue(x); self.assertTrue(all(abs(q) < 1e-6 for q in x), x)

    def test_side_flip_seed_base(self):
        z = lambda rows: [q['z'] for q in rows if q['kind'] == 'side_flip']
        self.assertNotEqual(z(self.go(base=0)), z(self.go(base=500)))
        self.assertEqual({q['seed'] for q in self.go(base=500) if q['kind'] == 'side_flip'}, {500, 501})

    def test_null_line_numbers(self):
        s = [{'code': 'ALL', 'kind': 'null', 'bar': 'SIZE', 'runs': 200, 'pass_both': 1, 'pass_SepDec': 9, 'pass_JanApr': 30}]
        x = V.null_line(s); self.assertEqual(x['pass_both'], 1); self.assertAlmostEqual(x['exact_hi'], 0.0275, places=3); self.assertEqual(x['pass_SepDec'], 9)

    def test_made_up_fires_keep_their_own_bar(self):
        # a dear bar on half the random moments: its fires then hit less; the null's pooled hit share falls with them
        n = len(self.R['t']); b = np.full(n, 3 * C); b[::2] = np.nan; self.bars['R'] = (b, np.full(n, '', dtype=object))
        rows = self.go(1, (), 0); self.assertTrue(any(x['kind'] == 'null' for x in rows))
        rws = P.null_rows(self.L, P.rng_for(0, 'T99', 'null', 0)); hR, _ = E.hit_b(self.R, b); self.assertTrue(np.isnan(hR[rws]).any())

    def test_plant_rises_excess(self):
        s = lambda k: float(np.nanmean([x['excess_pts'] for x in self.go(4, (25,), 4) if x['kind'] == k and x['bar'] == 'SIZE']))
        self.assertGreater(s('size_plant'), s('null') + 5)

    def test_clopper(self):
        lo, hi = V.clopper(0, 200); self.assertEqual(lo, 0.0); self.assertAlmostEqual(hi, 0.0183, places=3)
        lo, hi = V.clopper(5, 200); self.assertAlmostEqual(lo, 0.0082, places=3); self.assertAlmostEqual(hi, 0.0574, places=3)
        self.assertTrue(np.isnan(V.clopper(0, 0)[0])); self.assertEqual(V.clopper(10, 10)[1], 1.0)

    def test_binom(self):
        self.assertAlmostEqual(V.binom_cdf(1, 2, 0.5), 0.75); self.assertEqual(V.binom_cdf(-1, 2, 0.5), 0.0); self.assertEqual(V.binom_cdf(0, 2, 0.0), 1.0); self.assertEqual(V.binom_cdf(1, 2, 1.0), 0.0)

    def test_null_line(self):
        rows = self.go(2, (), 0); s = P.summary(rows); x = V.null_line(s); self.assertEqual(x['runs'], 2)
        self.assertIsNone(V.null_line([]))


def T8FW(H=None):
    # fair tests' world: T8.table has BEST values; bars 3c: 5c is a hit by default
    A = T8.fires(); Rr = []
    for (c, t, s, m, k) in A:
        for j, dd in enumerate((-1, 1, 2)):
            Rr.append((c, t + dd * 86400 + 120 + 1200 * j, s, m, 3 * k + j))
    H = H or (lambda m, k, c, d, h: (4 * C if k % 2 == 0 else 0.5 * C) if d == 'FADE' else 0.1 * C)
    O = lambda m, k, c, d, h: (1.0 if k % 10 < 7 else -1.0) if d == 'FADE' else (-1.0 if k % 10 < 7 else 1.0)
    TA, TR = T8.table(A, best=H, obh=O), T8.table(Rr, best=H, obh=O); w = np.full(len(Rr), 1 / 3.0)
    L = F.Look(TA, TR, w, T8.COSTS, 'FADE', pre_R=F.pre_fire_mask(TA, TR))
    bzt = lambda rows, rec: {'normal_move_pct': np.full(len(rows), 2 * C), 'range60_pct': np.array([rec(r) for r in rows]) * 2 * C, 'move15_pct': np.full(len(rows), 2 * C)}
    return L, TR, w, {'A': bzt(A, lambda r: 6.0), 'R': bzt(Rr, lambda r: 6.0 if r[4] % 3 == 0 else 1.0)}


class T07Build(unittest.TestCase):
    def test_build_table_and_manifest(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True); src = Src(18, wobble); p = os.path.join(d, 'l.tsv')
        with open(p, 'w') as f:
            f.write('coin\tt\tside\nX\t%d\t1\nX\t%d\t1\n' % (T0 + DAY, T0 + 17 * DAY))
        o = os.path.join(d, 'B')
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            man = B.build(src, o, [(p, 'A_T1')])
        self.assertEqual(man['lists']['A_T1']['why'], {'NO_LINE': 1, 'KNOWN': 1}); self.assertEqual(man['moments'], 2); self.assertTrue(os.path.isfile(os.path.join(o, 'BAR_V1.json')))
        rows = gzip.open(os.path.join(o, 'BAR_A_T1.tsv.gz'), 'rt').read().splitlines(); self.assertEqual(rows[0].split('\t'), list(B.HEAD)); self.assertEqual(rows[1].split('\t')[5:], ['', 'NO_LINE'])
        self.assertTrue(float(rows[2].split('\t')[5]) > 0)
        with self.assertRaises(B.Refused):
            B.build(src, o, [(p, 'A_T1')])

    def test_list_twice_refused(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True); p = os.path.join(d, 'l.tsv')
        with open(p, 'w') as f:
            f.write('coin\tt\nX\t5\nX\t5\n')
        with self.assertRaises(B.Refused):
            B.load_list(p)

    def test_beside_count(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True); p = os.path.join(d, 'l.tsv')
        with open(p, 'w') as f:
            f.write('coin\tt\nX\t%d\n' % (T0 + 8 * DAY + 3700))      # about 193 peaks: 168 to 302
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            man = B.build(Src(10, wobble), os.path.join(d, 'B'), [(p, 'N')])
        self.assertEqual(man['lists']['N']['no_line_with_168_or_more'], 1)
        with open(p, 'w') as f:
            f.write('coin\tt\nX\t%d\n' % (T0 + 2 * DAY))       # under 168: not counted beside
        with T8.contextlib.redirect_stdout(T8.io.StringIO()):
            man = B.build(Src(10, wobble), os.path.join(d, 'B2'), [(p, 'N')])
        self.assertEqual(man['lists']['N']['no_line_with_168_or_more'], 0)

    def test_compute_keeps_order_and_two_coins_apart(self):
        class S2(Src):
            def minutes(self, d, coins):
                k = self.days.index(d); return {'X': np.array([wobble(k * 1440 + j) for j in range(1440)], float), 'Y': np.full(1440, 50.0)}
            def cost_cells(self, d, coins):
                k = self.days.index(d); return {c: np.array([[1.0] * 24, [1.0] * 24, [0.0] * 24, [0.0] * 24]) for c in ('X', 'Y')}
        t = T0 + 17 * DAY; x = B.compute(S2(18), np.array(['Y', 'X', 'Y'], dtype=object), np.array([t, t, t + 60], np.int64))
        self.assertEqual(x['line_pct'][0], 0.0); self.assertGreater(x['line_pct'][1], 1.0); self.assertEqual(x['line_pct'][2], 0.0)


if __name__ == '__main__':
    unittest.main(verbosity=0)
