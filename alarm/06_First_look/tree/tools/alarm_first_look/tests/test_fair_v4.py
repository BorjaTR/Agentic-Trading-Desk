"""test_fair_v4.py (SCOUT 30 Oct 2026, tools/alarm_first_look): test_fair_v3.py on fair_v4 (edition 11: the grade's 30 min waves; imports,
FAIR_V4.json and its code names changed; a made-up fire is compared with the reader's own waves). test_fair_v3.py's docstring follows:
(SCOUT 30 Oct 2026, tools/alarm_first_look): test_fair_v2.py on fair_v3, with the null's tests rewritten for the null
by weight (T01: probabilities and draws; T02: each made-up fire its own wave, the rest weighted w / (1 - p), a real pre-fire moment never
drawn and still out; T08: a made-up fire's own pre-fire moments stay in), then fair_v3's own: T12 the null against unequal waves (by
weight it reads 0 where drawn alike it reads +50 pts or more; plants sized by wave), T13 the calibration table (the verdict at its lines,
LEANS, what counts), T14 the summary's new columns (Jan-Apr given Sep-Dec, the interval over alarms, the EITHER rates), T15 the files.
test_fair_v2.py's docstring follows: (SCOUT 30 Oct 2026, tools/alarm_first_look): test_fair_v1.py on fair_v2 (imports changed; the summary now holds the EITHER
rows; the real rows equal FL_RULE9), then fair_v2's own (T10): every row's z line, Jan-Apr confirming in the ladder, EITHER needing one bar
both periods. test_fair_v1.py's docstring follows: the ladder on planted worlds with known answers: the made-up alarm's
candidates (same coin, 7 days, 1 h of the hour of day on the circle, only the rows allowed), the draw (one a fire, never twice, seeded),
the made-up alarm's tables (its fires out of its random, a real fire's pre-fire moments still out), the day coins, the plants' sizes
(only lost races and misses change; the null is not changed), no-edge made-up alarms that rarely pass and planted edges that pass (both
bars), the real rows equal to fl_read_v8's own, the summary's counts, the run files and the refusals.
  python3 -B tests/test_fair_v1.py   (from tools/alarm_first_look; imports tests/test_fl_read_v8.py for its table helpers)"""
import contextlib, csv, io, math, os, sys, unittest
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import fair_v4 as FV
import test_fl_read_v11 as T8
F = FV.F; M = F.M; C = T8.C; COSTS = T8.COSTS


def fworld(hitA, hitR, recR=lambda m, kk, coin: 6.0 if kk % 3 == 0 else 1.0, waves=40):
    """fires (T8.fires: coins C0-C9 in turn, 12 h apart) and, for each fire, 3 random moments of ITS coin at its hour of day (+2, +22 and
    +42 min) 1 day before, 1 and 2 days after, kk = 3k + j (j = 0, 1, 2); the FADE 1 h race from hitA(m, k, coin) / hitR(m, kk, coin) (a
    bool: +1 or 0; a number: the race); normal move 2c everywhere, the last hour's range 6 normal moves for the fires and recR for the random
    -> (L, R table, weights, busyness arrays)"""
    A = T8.fires(waves=waves); Rr = []
    for (c, t, s, m, k) in A:
        for j, dd in enumerate((-1, 1, 2)):
            Rr.append((c, t + dd * 86400 + 120 + 1200 * j, s, m, 3 * k + j))
    num = lambda v: (1.0 if v else 0.0) if isinstance(v, (bool, np.bool_)) else float(v)
    ob = lambda f: (lambda m, k, coin, d, h: num(f(m, k, coin)) if d == 'FADE' else -num(f(m, k, coin)))
    TA, TR = T8.table(A, obh=ob(hitA)), T8.table(Rr, obh=ob(hitR))
    w = np.full(len(Rr), 1 / 3.0); L = F.Look(TA, TR, w, COSTS, 'FADE', pre_R=F.pre_fire_mask(TA, TR))
    bzt = lambda rows, rec: {'normal_move_pct': np.full(len(rows), 2 * C), 'range60_pct': np.array([rec(m, k, c) for (c, t, s, m, k) in rows]) * 2 * C,
                             'move15_pct': np.full(len(rows), 2 * C)}
    return L, TR, w, {'A': bzt(A, lambda m, k, c: 6.0), 'R': bzt(Rr, recR)}


ALLHIT = lambda m, k, coin: True
R70 = T8.R70                                   # random: the busiest band (j = 0) 70 pct hit, the rest 10 pct
SIDE3 = T8.SIDE3                               # the lean first in 26 of 40 fires a month, the other side in 14: +30 pts
EVEN = T8.EVEN                                 # the random: as often one side as the other
R0 = {'code': 'T99', 'alarm_ids': 'X1'}


def by(rows):
    return {(x['code'], x['kind'], x['plant'], x['bar']): x for x in FV.summary(rows)}


class T01NullRows(unittest.TestCase):
    # fair_v3: the made-up fires by weight (review B)
    def test_probabilities(self):
        # min(w, 0.5); 0 without a weight, with weight 0, without a cost, and for a real fire's pre-fire moment
        L, R, w, bz = fworld(ALLHIT, R70); n = len(R['t'])
        w2 = w.copy(); w2[0] = 0.8; w2[1] = 0.0; w2[2] = np.nan; w2[3] = 0.5
        R2 = dict(R); R2['coin'] = R['coin'].astype(object).copy(); R2['coin'][4] = 'NOCOST'
        pre = np.zeros(n, bool); pre[5] = True
        p = FV.null_p(F.Look(L.A, R2, w2, COSTS, 'FADE', pre_R=pre))
        self.assertEqual(p[:6].tolist(), [0.5, 0.0, 0.0, 0.5, 0.0, 0.0]); self.assertTrue(np.allclose(p[6:], 1 / 3.0))

    def test_draws(self):
        # each moment drawn with its probability; in order, never twice; the same generator, the same draw
        L, R, w, bz = fworld(ALLHIT, R70); w2 = np.where(np.arange(len(w)) % 2 == 0, 0.1, 0.4)
        L2 = F.Look(L.A, R, w2, COSTS, 'FADE', pre_R=L.preR); cnt = np.zeros(len(w2))
        for s in range(400):
            r = FV.null_rows(L2, np.random.default_rng(s)); cnt[r] += 1
            self.assertEqual(r.tolist(), sorted(set(r.tolist())))
        self.assertAlmostEqual(cnt[::2].mean() / 400, 0.1, delta=0.01); self.assertAlmostEqual(cnt[1::2].mean() / 400, 0.4, delta=0.01)
        self.assertEqual(FV.null_rows(L2, np.random.default_rng(7)).tolist(), FV.null_rows(L2, np.random.default_rng(7)).tolist())


class T02MadeUp(unittest.TestCase):
    def test_tables(self):
        L, R, w, bz = fworld(ALLHIT, R70)
        rows = np.array([3, 10, 50]); L2, bz2 = FV.made_up(L, R, w, COSTS, bz, rows)
        self.assertEqual(L2.A['t'].tolist(), R['t'][rows].tolist()); self.assertEqual(len(L2.R['t']), len(R['t']) - 3)
        self.assertNotIn(int(R['t'][3]), L2.R['t'].tolist())
        self.assertEqual(L2.wid.tolist(), [0, 1, 2])                                           # fair_v3: each made-up fire its own wave
        self.assertTrue(np.allclose(L2.wR, (1 / 3.0) / (1 - 1 / 3.0)))                        # the rest weighted w / (1 - p)
        self.assertEqual(bz2['A']['range60_pct'].tolist(), bz['R']['range60_pct'][rows].tolist())
        self.assertEqual(len(bz2['R']['range60_pct']), len(L2.R['t']))
        self.assertIsNone(FV.made_up(L, R, w, COSTS, None, rows)[1])

    def test_prefire_stays_out(self):
        # a random moment 20 min before a real fire is a pre-fire moment of the real alarm: never a made-up fire (p 0), out of the made-up
        # alarm's random, its weight unchanged
        L, R, w, bz = fworld(ALLHIT, R70)
        t0 = int(L.A['t'][5]); c0 = L.A['coin'][5]; n = len(R['t'])
        R2 = {k: np.append(v, v[0]) for k, v in R.items()}; R2['coin'] = R2['coin'].astype(object); R2['coin'][n] = c0; R2['t'][n] = t0 - 1200
        w2 = np.append(w, 1 / 3.0); L = F.Look(L.A, R2, w2, COSTS, 'FADE', pre_R=F.pre_fire_mask(L.A, R2))
        self.assertTrue(L.preR[n]); self.assertEqual(int(L.preR.sum()), 1); self.assertEqual(FV.null_p(L)[n], 0.0)
        bz = {'A': bz['A'], 'R': {k: np.append(v, v[0]) for k, v in bz['R'].items()}}
        L2, _ = FV.made_up(L, R2, w2, COSTS, bz, np.array([0, 1]))
        self.assertTrue(L2.preR[-1]); self.assertEqual(int(L2.preR.sum()), 1); self.assertAlmostEqual(float(L2.wR[-1]), 1 / 3.0)


class T03Coins(unittest.TestCase):
    def test_day_signs(self):
        t = np.array([0, 100, 86399, 86400, 200000, 200001], np.int64)
        for s in range(10):
            x = FV.day_signs(t, np.random.default_rng(s))
            self.assertEqual(len(set(x[:3].tolist())), 1); self.assertEqual(x[4], x[5]); self.assertTrue(set(x.tolist()) <= {-1.0, 1.0})
        seen = {tuple(FV.day_signs(t, np.random.default_rng(s)).tolist()) for s in range(40)}
        self.assertGreater(len(seen), 4)                                                   # the days get coins apart

    def test_side_flip(self):
        L, R, w, bz = fworld(SIDE3, EVEN)
        a, r = FV.side_flip(L, np.random.default_rng(2)); a0 = L.net(L.A, 'OBH4_60M__FADE'); r0 = L.net(L.R, 'OBH4_60M__FADE')
        self.assertTrue(np.array_equal(np.abs(a), np.abs(a0))); self.assertTrue(np.array_equal(np.abs(r), np.abs(r0)))
        fl = (a != a0); d = L.A['t'] // 86400
        for day in np.unique(d):
            self.assertEqual(len(set(fl[d == day].tolist())), 1)                            # a day flipped whole
        self.assertTrue(0 < fl.mean() < 1)


class T04Plants(unittest.TestCase):
    def test_side_plant(self):
        L, R, w, bz = fworld(SIDE3, EVEN); n = len(L.A['t'])
        net = -np.ones(n); net[::7] = 0.0; net[3] = np.nan
        out = FV.plant_side(L, net, 20, np.random.default_rng(3))
        self.assertTrue(np.array_equal(out[::7], net[::7])); self.assertTrue(np.isnan(out[3]))    # 0 and NaN never change
        ch = np.isfinite(net) & (out != net); self.assertTrue(np.all(net[ch] == -1) and np.all(out[ch] == 1))
        dec = np.isfinite(net) & (net != 0); s = dec.sum() / np.isfinite(net).sum()
        self.assertAlmostEqual(ch.sum() / dec.sum(), 0.20 / s, delta=0.07)                # lost races turned with probability D / (100 s)
        self.assertTrue(np.array_equal(net[::7], np.zeros(len(net[::7]))))                # the input is not changed

    def test_size_plant(self):
        L, R, w, bz = fworld(ALLHIT, R70); g = np.random.default_rng(5)
        rws = FV.null_rows(L, g); L2, bz2 = FV.made_up(L, R, w, COSTS, bz, rws)
        v0 = L2.A['OBH4_60M__FADE'].copy(); before = float((np.abs(v0) == 1).mean())
        L3 = FV.plant_size(L2, bz2, 10, g); v = L3.A['OBH4_60M__FADE']; after = float((np.abs(v) == 1).mean())
        self.assertAlmostEqual(after - before, 0.10, delta=0.05)
        self.assertTrue(np.array_equal(L2.A['OBH4_60M__FADE'], v0))                       # the null's own table is not changed
        self.assertTrue(np.all(v[v0 != 0] == v0[v0 != 0]))                                 # hits stay as they were
        self.assertTrue(np.array_equal(L3.A['OBH4_60M__FOLLOW'], -v)); self.assertTrue(set(v[v != v0].tolist()) <= {-1.0, 1.0})


class T05Ladder(unittest.TestCase):
    def test_side(self):
        # the real side +30 pts; day-flipped sides and made-up alarms rarely pass a period; a planted +40 always passes both
        L, R, w, bz = fworld(SIDE3, EVEN)
        rows = FV.ladder(R0, L, R, w, COSTS, None, 100, [40], 5); S = by(rows)     # fair_v3: 100 runs, at most 10 pass
        self.assertEqual(S[('T99', 'real', 0, 'SIDE')]['pass_both'], 1); self.assertNotIn(('T99', 'real', 0, 'SIZE'), S)   # SIZE NOT RUN
        for k in ('side_flip', 'null'):
            self.assertEqual(S[('ALL', k, 0, 'SIDE')]['runs'], 100); self.assertLessEqual(S[('ALL', k, 0, 'SIDE')]['pass_SepDec'], 10)
        self.assertEqual(S[('ALL', 'side_plant', 40, 'SIDE')]['pass_both'], 5)
        self.assertAlmostEqual(S[('ALL', 'side_plant', 40, 'SIDE')]['median_pts_SepDec'], 40, delta=12)
        self.assertNotIn(('ALL', 'size_plant', 40, 'SIZE'), S)                                 # no busyness: no size plant

    def test_size(self):
        # random moments that hit 4c as often as their band says; a made-up alarm of them rarely passes; a planted +25 always does
        L, R, w, bz = fworld(ALLHIT, R70, waves=56)    # fair_v3: 56 fires a month (the null by weight counts about one a fire)
        rows = FV.ladder(R0, L, R, w, COSTS, bz, 10, [25], 3); S = by(rows)
        self.assertEqual(S[('ALL', 'null', 0, 'SIZE')]['runs'], 10); self.assertLessEqual(S[('ALL', 'null', 0, 'SIZE')]['pass_SepDec'], 1)
        self.assertLessEqual(S[('ALL', 'null', 0, 'SIDE')]['pass_SepDec'], 1)
        self.assertEqual(S[('ALL', 'size_plant', 25, 'SIZE')]['pass_both'], 3)
        self.assertAlmostEqual(S[('ALL', 'size_plant', 25, 'SIZE')]['median_pts_SepDec'], 25, delta=8)
        self.assertTrue(all(370 <= x['fires'] <= 530 for x in rows if x['kind'] == 'null'))     # fair_v3: by weight, 448 expected

    def test_seeds_and_plants_share_their_null(self):
        L, R, w, bz = fworld(SIDE3, R70)
        a = FV.ladder(R0, L, R, w, COSTS, bz, 2, [10], 1); b = FV.ladder(R0, L, R, w, COSTS, bz, 2, [10], 1)
        key = lambda xs: [(x['kind'], x['seed'], x['bar'], x['period'], x['PASS'], F.fnum(x['z']), F.fnum(x['excess_pts'])) for x in xs]
        self.assertEqual(key(a), key(b))                                                      # seeded: the same rows
        c = FV.ladder(R0, L, R, w, COSTS, bz, 2, [10, 20], 1)
        self.assertEqual(key([x for x in c if x['plant'] != 20]), key(a))                    # another plant changes no other run
        self.assertEqual(len([x for x in c if x['kind'] == 'size_plant']), 4)                 # 2 plants x 1 seed x 2 periods
        self.assertNotEqual(key([x for x in a if x['kind'] == 'null' and x['seed'] == 0]), key([x for x in a if x['kind'] == 'null' and x['seed'] == 1]))


class T06Summary(unittest.TestCase):
    def test_counts(self):
        mk = lambda code, kind, seed, period, ok, z=1.0, bar='SIDE': {'code': code, 'kind': kind, 'plant': 0, 'seed': seed, 'bar': bar, 'period': period,
                                                                       'PASS': ok, 'z': z, 'excess_pts': 2 * z}
        rows = [mk('T1', 'null', 0, 'Sep-Dec', 'PASS', 3.0), mk('T1', 'null', 0, 'Jan-Apr', 'PASS', 2.5),
                mk('T1', 'null', 1, 'Sep-Dec', 'PASS', 2.2), mk('T1', 'null', 1, 'Jan-Apr', 'NOT PASS', 0.1),
                mk('T2', 'null', 0, 'Sep-Dec', 'NOT PASS', np.nan), mk('T2', 'null', 0, 'Jan-Apr', 'NOT PASS', -1.0),
                mk('T2', 'null', 0, 'Sep-Dec', 'NOT RUN', np.nan, 'SIZE'), mk('T2', 'null', 0, 'Jan-Apr', 'NOT RUN', np.nan, 'SIZE')]
        S = by(rows)
        a = S[('ALL', 'null', 0, 'SIDE')]
        self.assertEqual((a['runs'], a['pass_SepDec'], a['pass_JanApr'], a['pass_both']), (3, 2, 1, 1))
        self.assertAlmostEqual(a['rate_both'], 1 / 3); self.assertAlmostEqual(a['median_z_SepDec'], 2.6)   # NaN left out
        self.assertEqual(S[('T1', 'null', 0, 'SIDE')]['runs'], 2); self.assertEqual(S[('T2', 'null', 0, 'SIDE')]['pass_SepDec'], 0)
        self.assertNotIn(('ALL', 'null', 0, 'SIZE'), S)                                        # NOT RUN is no run
        self.assertEqual([(x['code'], x['bar']) for x in FV.summary(rows)], [('ALL', 'EITHER'), ('ALL', 'SIDE'), ('T1', 'EITHER'), ('T1', 'SIDE'), ('T2', 'EITHER'), ('T2', 'SIDE')])


class T07Files(unittest.TestCase):
    setUp = T8.T12EndToEnd.setUp; tearDown = T8.T12EndToEnd.tearDown; targets = T8.T12EndToEnd.targets
    bz_files = T8.T19Rule7Run.bz_files

    def run_fair(self, name, *dirs, extra=(), seeds='2', plants='10'):
        out = os.path.join(self.d, name)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = FV.main([self.targets(), self.H, self.costs, out, seeds, plants, *extra, *dirs])
        return rc, out

    def test_files_and_real_rows(self):
        T8.gz(os.path.join(self.rc, 'AT99.tsv.gz'), T8.table(self.A_rows, obh=T8.obf(lambda m, k: 1.0)))
        T8.gz(os.path.join(self.rc, 'RT99.tsv.gz'), T8.table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C,
                                                             obh=T8.obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        bzd = self.bz_files()
        rc, out = self.run_fair('f1', self.rc, self.apd, bzd, extra=('--plant-seeds', '1'))
        self.assertEqual(rc, 0)
        R = list(csv.DictReader(open(os.path.join(out, 'FAIR_RUNS.tsv')), delimiter='\t'))
        self.assertEqual(list(R[0].keys()), FV.RUN_COLS)
        kinds = {}
        for x in R:
            kinds[x['kind']] = kinds.get(x['kind'], 0) + 1
        self.assertEqual(kinds, {'real': 4, 'side_flip': 4, 'side_plant': 2, 'null': 8, 'size_plant': 2})
        S = list(csv.DictReader(open(os.path.join(out, 'FAIR_SUMMARY.tsv')), delimiter='\t'))
        self.assertEqual(list(S[0].keys()), FV.SUM_COLS)
        exp = [('real', '0', 'EITHER', '1'), ('real', '0', 'SIDE', '1'), ('real', '0', 'SIZE', '1'), ('null', '0', 'EITHER', '2'), ('null', '0', 'SIDE', '2'), ('null', '0', 'SIZE', '2'),
               ('size_plant', '10', 'SIZE', '1'), ('side_flip', '0', 'SIDE', '2'), ('side_plant', '10', 'SIDE', '1')]
        self.assertEqual([(x['kind'], x['plant'], x['bar'], x['runs']) for x in S], [e for e in exp] * 2)
        self.assertEqual([x['code'] for x in S], ['ALL'] * 9 + ['T99'] * 9)
        J = __import__('json').load(open(os.path.join(out, 'FAIR_V4.json')))
        self.assertEqual(J['settings']['plant_seeds'], 1); self.assertIn('BZA', J['codes']['T99']['inputs'])
        # the real rows are fl_read_v8's own verdicts
        with contextlib.redirect_stdout(io.StringIO()):
            F.main(self.targets(), self.H, self.costs, os.path.join(self.d, 'fl8'), self.rc, self.apd, bzd)
        q = list(csv.DictReader(open(os.path.join(self.d, 'fl8', 'FL_RULE9.tsv')), delimiter='\t'))[0]
        for x in R:
            if x['kind'] == 'real':
                p = x['period'].replace('-', ''); self.assertEqual(x['PASS'], q['%s_%s' % (x['bar'], p)])
                self.assertEqual(x['z'], q['%s_%s_z' % (x['bar'], p)])

    def test_refusals(self):
        with self.assertRaises(M.Refused):
            self.run_fair('f2', self.rc, self.apd, os.path.join(self.d, 'busy_not_there'))    # not a finished job
        os.makedirs(os.path.join(self.d, 'f3'))
        with self.assertRaises(M.Refused):
            self.run_fair('f3', self.rc, self.apd)                                             # the out folder exists
        with self.assertRaises(M.Refused):
            self.run_fair('f4', self.rc, self.apd, extra=('--plant-seeds', '3'))              # more plant seeds than seeds
        with self.assertRaises(M.Refused):
            self.run_fair('f5', self.rc, self.apd, plants='0')                                 # a plant of 0
        with self.assertRaises(M.Refused):
            self.run_fair('f6', self.rc, self.apd, extra=('--codes', 'T98'))                  # a code not in TARGETS
        for n in ('f2', 'f4', 'f5', 'f6'):
            self.assertFalse(os.path.exists(os.path.join(self.d, n)) or os.path.exists(os.path.join(self.d, n + '.part')))


# ---------------- planted bugs the tests above let through (mutants_fair_v1.py, 30 Oct 2026; each survivor gets a test, R16)
LEANS_HEAT = lambda m, kk, coin: -1                     # the random: heat first every time


def with_prefire(L, R, w, bz):
    """the world plus, for each fire, a random moment of its coin 20 min before it (a copy of the fire's row): pre-fire moments that are
    candidates of that fire (same coin, same day, 20 min away)"""
    A = L.A; n = len(A['t'])
    R2 = {k: np.concatenate([R[k], A[k]]) for k in R}; R2['coin'] = R2['coin'].astype(object); R2['t'][len(R['t']):] = A['t'] - 1200
    w2 = np.append(w, np.full(n, 1 / 3.0)); L2 = F.Look(A, R2, w2, COSTS, 'FADE', pre_R=F.pre_fire_mask(A, R2))
    return L2, R2, w2, {'A': bz['A'], 'R': {k: np.concatenate([bz['R'][k], bz['A'][k]]) for k in bz['R']}}


class T08Planted(unittest.TestCase):
    def test_prefire_moments_are_never_made_up_fires(self):
        L, R, w, bz = with_prefire(*fworld(ALLHIT, R70)); seen = []; om = FV.made_up
        FV.made_up = lambda L_, R_, wR_, costs_, bz_, rows: (seen.append(np.array(rows)), om(L_, R_, wR_, costs_, bz_, rows))[1]
        try:
            FV.ladder(R0, L, R, w, COSTS, bz, 3, [], 0)
        finally:
            FV.made_up = om
        pre = np.flatnonzero(L.preR); self.assertEqual(len(pre), len(L.A['t'])); self.assertEqual(len(seen), 3)
        self.assertFalse(any(np.isin(x, pre).any() for x in seen))

    def test_made_up_fires_own_prefire_moments_stay_in(self):
        # fair_v3 (review B): a random moment 20 min before random row 3 (its coin) is no pre-fire moment of the real alarm, so it stays
        # in the made-up alarm's random (fair_v2 cut it: the made-up fires lost random moments of their own hours)
        L, R, w, bz = fworld(ALLHIT, R70); n = len(R['t'])
        R2 = {k: np.append(v, v[3]) for k, v in R.items()}; R2['coin'] = R2['coin'].astype(object); R2['t'][n] = R['t'][3] - 1200
        w2 = np.append(w, 1 / 3.0); L = F.Look(L.A, R2, w2, COSTS, 'FADE', pre_R=F.pre_fire_mask(L.A, R2))
        bz2 = {'A': bz['A'], 'R': {k: np.append(v, v[3]) for k, v in bz['R'].items()}}
        self.assertFalse(L.preR[n])
        L2, _ = FV.made_up(L, R2, w2, COSTS, bz2, np.array([3]))
        self.assertFalse(L2.preR[-1]); self.assertEqual(int(L2.preR.sum()), 0)

    def test_side_flip_flips_the_random_too(self):
        L, R, w, bz = fworld(SIDE3, EVEN)
        a, r = FV.side_flip(L, np.random.default_rng(2)); r0 = L.net(L.R, 'OBH4_60M__FADE'); fl = r != r0; d = L.R['t'] // 86400
        self.assertTrue(0 < fl.mean() < 1)
        for day in np.unique(d):
            self.assertEqual(len(set(fl[d == day].tolist())), 1)                            # a day flipped whole

    def test_side_flip_coins_apart_for_fires_and_random(self):
        L, R, w, bz = fworld(SIDE3, EVEN)
        a, r = FV.side_flip(L, np.random.default_rng(4)); a0 = L.net(L.A, 'OBH4_60M__FADE'); r0 = L.net(L.R, 'OBH4_60M__FADE')
        fa = {int(t) // 86400: bool(x != y) for t, x, y in zip(L.A['t'], a, a0)}
        fr = {int(t) // 86400: bool(x != y) for t, x, y in zip(L.R['t'], r, r0)}
        both = sorted(set(fa) & set(fr)); same = float(np.mean([fa[k] == fr[k] for k in both]))
        self.assertGreater(len(both), 100); self.assertTrue(0.3 < same < 0.7, same)          # the same coin would give 1.0

    def test_side_flip_reads_the_1h_race(self):
        L, R, w, bz = fworld(SIDE3, EVEN)
        for T in (L.A, L.R):
            for h in F.WINDOWS:
                if h != 60:
                    for d in ('FADE', 'FOLLOW'):
                        T['OBH4_%dM__%s' % (h, d)] = np.zeros(len(T['t']))
        a, r = FV.side_flip(L, np.random.default_rng(2))
        self.assertTrue(np.array_equal(np.abs(a), np.abs(L.net(L.A, 'OBH4_60M__FADE'))))
        self.assertTrue(np.array_equal(np.abs(r), np.abs(L.net(L.R, 'OBH4_60M__FADE'))))

    def test_side_plant_with_many_ties(self):
        # half the races neither (0), half lost: the decided share s is 0.5, so a +20 plant turns 40 pct of the lost races (D / (100 s))
        L, R, w, bz = fworld(SIDE3, EVEN); n = len(L.A['t'])
        net = np.where(np.arange(n) % 2 == 0, 0.0, -1.0); out = FV.plant_side(L, net, 20, np.random.default_rng(3)); lost = net == -1
        self.assertAlmostEqual(float((out[lost] == 1).mean()), 0.40, delta=0.1)

    def test_size_plant_keeps_heat_first_hits(self):
        # the random: offer first, heat first, neither in turn; heat first is a 4c hit too and stays
        L, R, w, bz = fworld(ALLHIT, lambda m, kk, coin: (1.0, -1.0, 0.0)[kk % 3]); g = np.random.default_rng(5)
        rws = FV.null_rows(L, g); L2, bz2 = FV.made_up(L, R, w, COSTS, bz, rws)
        v0 = L2.A['OBH4_60M__FADE'].copy(); self.assertTrue((v0 == -1).any())
        v = FV.plant_size(L2, bz2, 10, g).A['OBH4_60M__FADE']
        self.assertTrue(np.all(v[v0 != 0] == v0[v0 != 0]))

    def test_size_plant_sized_on_busy_fires(self):
        # quiet random moments (normal move 1c) always hit 4c, busy ones (2c) 20 pct: a +10 plant turns 10 / (100 (1 - 0.2)) = 12.5 pct of
        # the misses (h is the busy fires' hit share: the SIZE bar reads busy fires only)
        L, R, w, bz = fworld(ALLHIT, lambda m, kk, coin: True if (kk // 3) % 2 == 1 else (kk // 3) % 10 == 0)
        i = np.arange(len(R['t'])); kk = 3 * ((i // 3) % 40) + i % 3
        bz['R']['normal_move_pct'] = np.where((kk // 3) % 2 == 1, 1 * C, 2 * C); g = np.random.default_rng(6)
        rws = FV.null_rows(L, g); L2, bz2 = FV.made_up(L, R, w, COSTS, bz, rws)
        v0 = L2.A['OBH4_60M__FADE'].copy(); miss = v0 == 0     # fair_v3: 20 plants on one null (its misses vary with the draw)
        turned = [float((FV.plant_size(L2, bz2, 10, np.random.default_rng(100 + s)).A['OBH4_60M__FADE'][miss] != 0).mean()) for s in range(20)]
        self.assertGreater(int(miss.sum()), 100); self.assertAlmostEqual(float(np.mean(turned)), 0.125, delta=0.012)

    def test_flip_and_plant_read_the_flipped_random(self):
        # the random heat first every time: against the flipped random the day-flipped fires rarely pass and a +10 plant reads about +10;
        # against the random as it is, every run would pass by about 100 pts
        L, R, w, bz = fworld(SIDE3, LEANS_HEAT)
        S = by(FV.ladder(R0, L, R, w, COSTS, None, 10, [10], 10))
        self.assertLessEqual(S[('ALL', 'side_flip', 0, 'SIDE')]['pass_both'], 1)
        self.assertLess(abs(S[('ALL', 'side_plant', 10, 'SIDE')]['median_pts_SepDec'] - 10), 30)

    def test_plants_are_built_on_their_seeds_flip_and_null(self):
        L, R, w, bz = fworld(SIDE3, R70); got = {'side': [], 'size': []}; op, oz = FV.plant_side, FV.plant_size
        FV.plant_side = lambda L_, net, plant, rng: (got['side'].append(np.array(net)), op(L_, net, plant, rng))[1]
        FV.plant_size = lambda L2, bz2, plant, rng: (got['size'].append(L2.A['t'].copy()), oz(L2, bz2, plant, rng))[1]
        try:
            FV.ladder(R0, L, R, w, COSTS, bz, 2, [10, 20], 2)
        finally:
            FV.plant_side, FV.plant_size = op, oz
        flips = [FV.side_flip(L, FV.rng_for(s, 'T99', 'side_flip', 0))[0] for s in range(2)]
        nulls = [R['t'][FV.null_rows(L, FV.rng_for(s, 'T99', 'null', 0))] for s in range(2)]
        self.assertEqual((len(got['side']), len(got['size'])), (4, 4))
        for i, x in enumerate(got['side']):
            self.assertTrue(np.array_equal(x, flips[i // 2], equal_nan=True))
        for i, x in enumerate(got['size']):
            self.assertTrue(np.array_equal(x, nulls[i // 2]))

    def test_null_reads_its_own_count(self):
        # half the real fires without a 1 h offer: the real alarm counts 28 waves a month (56 fires a month; COUNT fails); the made-up alarm, drawn from the
        # random moments (all with a 1 h offer), counts its own
        L, R, w, bz = fworld(SIDE3, EVEN, waves=56); n = len(L.A['t'])     # fair_v3: 56 a month, the real alarm keeps 28
        L.A['BEST_60M__FADE'] = np.where(np.arange(n) % 2 == 0, np.nan, L.A['BEST_60M__FADE'])
        rows = FV.ladder(R0, L, R, w, COSTS, bz, 2, [], 0)
        self.assertTrue(all('COUNT' in x['fail'] for x in rows if x['kind'] == 'real'))
        self.assertTrue(all('COUNT' not in x['fail'] for x in rows if x['kind'] == 'null'))

    def test_rates_by_period(self):
        mk = lambda seed, period, ok: {'code': 'T1', 'kind': 'null', 'plant': 0, 'seed': seed, 'bar': 'SIDE', 'period': period, 'PASS': ok,
                                       'z': 1.0, 'excess_pts': 1.0}
        rows = [mk(0, 'Sep-Dec', 'PASS'), mk(0, 'Jan-Apr', 'NOT PASS'), mk(1, 'Sep-Dec', 'PASS'), mk(1, 'Jan-Apr', 'NOT PASS'),
                mk(2, 'Sep-Dec', 'NOT PASS'), mk(2, 'Jan-Apr', 'PASS')]
        a = by(rows)[('ALL', 'null', 0, 'SIDE')]
        self.assertEqual((a['rate_SepDec'], a['rate_JanApr'], a['rate_both']), (2 / 3, 1 / 3, 0.0))


class T09FilesPlanted(unittest.TestCase):
    setUp = T8.T12EndToEnd.setUp; tearDown = T8.T12EndToEnd.tearDown; targets = T8.T12EndToEnd.targets

    def test_a_failed_run_leaves_nothing(self):
        out = os.path.join(self.d, 'f7')
        with self.assertRaises(M.Refused):
            with contextlib.redirect_stdout(io.StringIO()):
                FV.main([self.targets(A_sha16='0' * 16), self.H, self.costs, out, '2', '10', self.rc, self.apd])  # a list changed
        self.assertFalse(os.path.exists(out) or os.path.exists(out + '.part'))


# ---------------- fair_v2: edition 9's z lines and the EITHER row (the owner 30 Oct 2026 19:21 Berlin)
class T10ZLines(unittest.TestCase):
    def test_rows_carry_their_z_line(self):
        L, R, w, bz = fworld(SIDE3, R70); rows = FV.ladder(R0, L, R, w, COSTS, bz, 2, [10], 1)
        self.assertEqual({x['kind'] for x in rows}, {'real', 'null', 'size_plant', 'side_flip', 'side_plant'})
        for x in rows:
            self.assertEqual(x['z_min'], 2.0 if x['period'] == 'Sep-Dec' else 1.0, (x['kind'], x['bar'], x['period']))

    def test_jan_apr_confirms_in_the_ladder(self):
        # Sep-Dec +30 pts; Jan-Apr 20 pts above a random that is heat first 60 pct of the time, each day's fires one way: z between 1 and 2
        L, R, w, bz = fworld(T8.CONF, T8.RCONF); rows = FV.ladder(R0, L, R, w, COSTS, None, 1, [], 0)
        real = {x['period']: x for x in rows if x['kind'] == 'real' and x['bar'] == 'SIDE'}
        self.assertEqual((real['Sep-Dec']['PASS'], real['Jan-Apr']['PASS']), ('PASS', 'PASS')); self.assertTrue(1.0 <= real['Jan-Apr']['z'] < 2.0)
        self.assertEqual(by(rows)[('T99', 'real', 0, 'EITHER')]['pass_both'], 1)

    def test_either_needs_one_bar_both_periods(self):
        mk = lambda seed, bar, period, ok: {'code': 'T1', 'kind': 'null', 'plant': 0, 'seed': seed, 'bar': bar, 'period': period, 'PASS': ok,
                                            'z': 1.0, 'excess_pts': 1.0}
        P, N = 'PASS', 'NOT PASS'
        rows = [mk(0, 'SIZE', 'Sep-Dec', P), mk(0, 'SIZE', 'Jan-Apr', N), mk(0, 'SIDE', 'Sep-Dec', N), mk(0, 'SIDE', 'Jan-Apr', P),
                mk(1, 'SIZE', 'Sep-Dec', N), mk(1, 'SIZE', 'Jan-Apr', N), mk(1, 'SIDE', 'Sep-Dec', P), mk(1, 'SIDE', 'Jan-Apr', P),
                mk(2, 'SIZE', 'Sep-Dec', N), mk(2, 'SIZE', 'Jan-Apr', P), mk(2, 'SIDE', 'Sep-Dec', 'NOT RUN'), mk(2, 'SIDE', 'Jan-Apr', 'NOT RUN')]
        e = by(rows)[('ALL', 'null', 0, 'EITHER')]
        self.assertEqual((e['runs'], e['pass_SepDec'], e['pass_JanApr'], e['pass_both']), (3, 2, 3, 1))
        self.assertAlmostEqual(e['rate_both'], 1 / 3)
        self.assertNotIn(('ALL', 'side_flip', 0, 'EITHER'), by(rows + [dict(mk(0, 'SIDE', 'Sep-Dec', P), kind='side_flip')]))


class T11FilesZ(unittest.TestCase):
    setUp = T8.T12EndToEnd.setUp; tearDown = T8.T12EndToEnd.tearDown; targets = T8.T12EndToEnd.targets
    bz_files = T8.T19Rule7Run.bz_files; run_fair = T07Files.run_fair

    def test_runs_file_carries_the_z_lines(self):
        T8.gz(os.path.join(self.rc, 'AT99.tsv.gz'), T8.table(self.A_rows, obh=T8.obf(lambda m, k: 1.0)))
        T8.gz(os.path.join(self.rc, 'RT99.tsv.gz'), T8.table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C,
                                                             obh=T8.obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        rc, out = self.run_fair('z1', self.rc, self.apd, self.bz_files(), seeds='1', extra=('--plant-seeds', '1'))
        R = list(csv.DictReader(open(os.path.join(out, 'FAIR_RUNS.tsv')), delimiter='\t'))
        self.assertEqual({(x['period'], x['z_min']) for x in R}, {('Sep-Dec', '2.00'), ('Jan-Apr', '1.00')})
        J = __import__('json').load(open(os.path.join(out, 'FAIR_V4.json'))); self.assertEqual(J['settings']['z_lines'], {'Sep-Dec': 2.0, 'Jan-Apr': 1.0})


# ---------------- fair_v3: the null by weight (review B, 30 Oct 2026, reviews/REVIEW_B_FAIR2_20261030.md)
def wworld(months=('202510', '202511', '202601', '202602')):
    """unequal waves: each month 30 lone fires (C0-C4 in turn, 12 h apart from day 3, at 00:00 or 12:00) and 4 waves of 10 fires (C5-C9
    twice, 1 min apart, at 06:00 on days 4, 8, 12 and 16); for each fire 3 random moments of its coin at its hour of day (+2, +22, +42 min)
    1 day before, 1 and 2 days after, weighted per wave (a wave's random sums to 1: 1/3 a lone fire's, 1/30 a big wave's fire's). The 1 h
    race: the lone fires' random -1, the big waves' random +1 (so the random, waves weighted, is (4 - 30) / 34 a month); the fires: lone
    ones +1 and -1 in turn, the big waves 0 -> (L, R table, weights)"""
    A, Rr = [], []
    for m in months:
        b = T8.start(m)
        for i in range(30):
            A.append(('C%d' % (i % 5), b + 2 * 86400 + i * 43200, -1, m, i))
        for q, day in enumerate((3, 7, 11, 15)):
            for j in range(10):
                A.append(('C%d' % (5 + j % 5), b + day * 86400 + 6 * 3600 + 60 * j, -1, m, 100 + 10 * q + j))
    for (c, t, s, m, k) in A:
        for j, dd in enumerate((-1, 1, 2)):
            Rr.append((c, t + dd * 86400 + 120 + 1200 * j, s, m, 3 * k + j))
    sgn = lambda d: 1.0 if d == 'FADE' else -1.0
    fa = lambda m, k, coin, d, h: ((1.0 if k % 2 == 0 else -1.0) if k < 100 else 0.0) * sgn(d)
    fr = lambda m, kk, coin, d, h: (-1.0 if kk < 300 else 1.0) * sgn(d)
    TA, TR = T8.table(A, obh=fa), T8.table(Rr, obh=fr)
    w = np.array([1 / 3.0 if r[4] < 300 else 1 / 30.0 for r in Rr])
    return F.Look(TA, TR, w, COSTS, 'FADE', pre_R=F.pre_fire_mask(TA, TR)), TR, w


class T12NullWeights(unittest.TestCase):
    def test_world(self):
        L, R, w = wworld(); x = L.net(L.R, 'OBH4_60M__FADE')
        self.assertEqual(len(np.unique(L.wid)), 4 * 34); self.assertFalse(L.preR.any())
        for m in ('202510', '202602'):
            self.assertAlmostEqual(F.wmean(np.where(L.rmonth == m, x, np.nan), w), (4 - 30) / 34, places=12)

    def test_null_reads_zero_against_unequal_waves(self):
        # review B: made-up fires by weight read the random on average (0 pts) though the big waves' moments (+1) weigh 1/30 and the lone
        # fires' (-1) 1/3; each made-up fire its own wave (the bar's waves are the made-up fires)
        L, R, w = wworld(); rows = FV.ladder(R0, L, R, w, COSTS, None, 30, [], 0)
        null = [x for x in rows if x['kind'] == 'null' and x['bar'] == 'SIDE']; self.assertEqual(len(null), 60)
        self.assertAlmostEqual(float(np.mean([x['excess_pts'] for x in null])), 0.0, delta=4.0)
        for s in range(30):
            ws = [x['waves'] for x in null if x['seed'] == s]; fs = {x['fires'] for x in null if x['seed'] == s}
            self.assertEqual({sum(ws)}, fs)                                                  # all four months in the two periods

    def test_each_made_up_fire_its_own_wave(self):
        # two made-up fires 10 min apart: md_v1 would join them in one wave; the null keeps each its own (as the random weighs a moment)
        L, R, w, bz = fworld(ALLHIT, R70); n = len(R['t'])
        R2 = {k: np.append(v, [v[0], v[0]]) for k, v in R.items()}; R2['coin'] = R2['coin'].astype(object); R2['t'][n + 1] = R2['t'][n] + 600
        w2 = np.append(w, [1 / 3.0, 1 / 3.0]); L = F.Look(L.A, R2, w2, COSTS, 'FADE', pre_R=F.pre_fire_mask(L.A, R2))
        L2, _ = FV.made_up(L, R2, w2, COSTS, None, np.array([n, n + 1]))
        self.assertEqual(L2.wid.tolist(), [0, 1]); self.assertEqual(F.WV.waves(L2.A['t'], F.GRADE_WAVE_S).tolist(), [0, 0])

    def test_drawn_alike_would_lean(self):
        # the same world with every moment drawn alike (1 in 3): the big waves' moments count as much as the lone fires': +50 pts or more
        L, R, w = wworld(); ex = []
        for s in range(5):
            L0, _ = FV.made_up(L, R, w, COSTS, None, np.flatnonzero(np.random.default_rng(s).random(len(w)) < 1 / 3.0))
            ex.append(F.verdict8(L0, None, M.DESIGN)['SIDE']['excess_pts'])
        self.assertGreater(min(ex), 50.0)

    def test_plants_sized_by_wave(self):
        # lone fires decided (+1 and -1 in turn), big waves undecided: decided in 30 of 34 waves but 30 of 70 fires. A +20 plant lifts
        # the waves' mean race (offer-first minus heat-first) by 0.20; sized per fire it would lift it by 0.41
        L, R, w = wworld(); net = L.net(L.A, 'OBH4_60M__FADE'); inp = L.useA & np.isin(L.wmonth, M.DESIGN) & np.isfinite(net)
        u, inv = np.unique(L.wid[inp], return_inverse=True); nw = np.bincount(inv)
        wm = lambda x: float((np.bincount(inv, weights=x[inp]) / nw).mean())
        lifts = [wm(FV.plant_side(L, net, 20, np.random.default_rng(s))) - wm(net) for s in range(40)]
        self.assertAlmostEqual(float(np.mean(lifts)), 0.20, delta=0.04)


def crow(code, z, seed, kind='null', bar='SIDE', period='Sep-Dec', plant=0, ok='NOT PASS'):
    return {'code': code, 'kind': kind, 'plant': plant, 'seed': seed, 'bar': bar, 'period': period, 'PASS': ok, 'z': z, 'excess_pts': z}


Z10 = [-1.5, -1.0, -0.75, -0.5, 0.0, 0.0, 0.5, 0.75, 1.0, 1.5]          # mean 0, sd (ddof 1) 0.957


def cal(rows):
    return {(x['code'], x['kind'], x['bar'], x['period']): x for x in FV.calib(rows)}


def six(shift=lambda c: 0.0, scale=1.0, n=6, **kw):
    return [crow('T%d' % c, scale * z + shift(c), s, **kw) for c in range(n) for s, z in enumerate(np.roll(Z10, c))]


class T13Calib(unittest.TestCase):
    def test_calibrated(self):
        rows = six() + six(kind='side_flip', period='Jan-Apr'); C = cal(rows); a = C[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        sd = float(np.std(Z10, ddof=1))
        self.assertEqual((a['alarms'], a['runs'], a['verdict']), (6, 60, 'CALIBRATED'))
        self.assertAlmostEqual(a['mean_z'], 0.0, places=12); self.assertAlmostEqual(a['sd_z'], sd, places=12)
        self.assertAlmostEqual(a['spread'], 0.0, places=12); self.assertAlmostEqual(a['noise'], sd / math.sqrt(10), places=12)
        self.assertAlmostEqual(a['p_z_ge_1'], 0.2); self.assertAlmostEqual(a['p_z_ge_2'], 0.0)                  # z = 1 counts
        self.assertEqual(C[('ALL', 'side_flip', 'SIDE', 'Jan-Apr')]['verdict'], 'CALIBRATED')
        out = FV.calib(rows); self.assertEqual([x['code'] for x in out[:2]], ['ALL', 'ALL']); self.assertEqual(len(out), 14)

    def test_leaning_alarms(self):
        C = cal(six(shift=lambda c: 2.0 if c < 3 else 0.0)); a = C[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        self.assertEqual(a['verdict'], 'NOT CALIBRATED'); self.assertAlmostEqual(a['mean_z'], 1.0, places=12)
        self.assertAlmostEqual(a['spread'], math.sqrt(1.2), places=12)                       # means 2, 2, 2, 0, 0, 0: sd (ddof 1)
        self.assertEqual([C[('T%d' % c, 'null', 'SIDE', 'Sep-Dec')]['verdict'] for c in range(6)], ['LEANS'] * 3 + ['-'] * 3)

    def test_lines(self):
        v = lambda rows: cal(rows)[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        self.assertEqual(v(six(shift=lambda c: 0.2))['verdict'], 'CALIBRATED')               # |mean z| 0.2: on the line
        for d in (0.21, -0.21):
            self.assertEqual(v(six(shift=lambda c, d=d: d))['verdict'], 'NOT CALIBRATED')
        for k in (3.0, 0.5):                                                                  # sd within 2.9 or 0.48
            self.assertEqual(v(six(scale=k))['verdict'], 'NOT CALIBRATED')
        a = v(six(shift=lambda c: 0.6 if c % 2 else -0.6))                                     # means +-0.6: spread 0.66, noise 0.30
        self.assertEqual(a['verdict'], 'NOT CALIBRATED'); self.assertAlmostEqual(a['mean_z'], 0.0, places=12)
        self.assertGreater(a['spread_ratio'], 2.0); self.assertEqual(cal(six(shift=lambda c: 0.6 if c % 2 else -0.6))[('T1', 'null', 'SIDE', 'Sep-Dec')]['verdict'], '-')

    def test_too_few_and_what_counts(self):
        rows = six(n=4) + [crow('T9', 5.0, s, kind='side_plant', plant=10) for s in range(10)] + [crow('T9', 5.0, 0, kind='real')]
        rows += [crow('T7', np.nan, s) for s in range(10)] + [crow('T8', 5.0, s, ok='NOT RUN') for s in range(10)]
        C = cal(rows); a = C[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        self.assertEqual((a['alarms'], a['runs'], a['verdict']), (4, 40, 'TOO FEW ALARMS'))
        self.assertEqual({k[1] for k in C}, {'null'}); self.assertEqual({k[0] for k in C}, {'ALL', 'T0', 'T1', 'T2', 'T3'})


class T14SummaryV3(unittest.TestCase):
    def test_given_and_interval(self):
        mk = lambda code, seed, period, ok: {'code': code, 'kind': 'null', 'plant': 0, 'seed': seed, 'bar': 'SIDE', 'period': period, 'PASS': ok,
                                             'z': 1.0, 'excess_pts': 1.0}
        P, N = 'PASS', 'NOT PASS'
        rows = [mk('T1', 0, 'Sep-Dec', P), mk('T1', 0, 'Jan-Apr', P), mk('T1', 1, 'Sep-Dec', P), mk('T1', 1, 'Jan-Apr', P),
                mk('T2', 0, 'Sep-Dec', P), mk('T2', 0, 'Jan-Apr', N), mk('T2', 1, 'Sep-Dec', N), mk('T2', 1, 'Jan-Apr', N),
                mk('T3', 0, 'Sep-Dec', N), mk('T3', 0, 'Jan-Apr', P), mk('T3', 1, 'Sep-Dec', N), mk('T3', 1, 'Jan-Apr', N)]
        S = by(rows); a = S[('ALL', 'null', 0, 'SIDE')]
        self.assertAlmostEqual(a['rate_JanApr_given_SepDec'], 2 / 3)                          # 2 of the 3 Sep-Dec passes pass Jan-Apr too
        self.assertTrue(np.isnan(S[('T3', 'null', 0, 'SIDE')]['rate_JanApr_given_SepDec']))   # no Sep-Dec pass
        self.assertEqual((a['both_lo'], a['both_hi']), (0.0, 1.0))      # T1 2 of 2, T2 and T3 0 of 2: 3 codes resampled
        self.assertTrue(np.isnan(S[('T1', 'null', 0, 'SIDE')]['both_lo']) and np.isnan(S[('T1', 'null', 0, 'SIDE')]['both_hi']))
        self.assertEqual(FV.both_interval([(2, 1), (2, 1)]), (0.5, 0.5)); self.assertTrue(np.isnan(FV.both_interval([])[0]))
        lo, hi = FV.both_interval([(2, 2)] + [(2, 0)] * 9)          # 1 code of 10 passes: the pooled rate of a resample, not its best code
        self.assertEqual(lo, 0.0); self.assertAlmostEqual(hi, 0.3, places=12)

    def test_either_rates(self):
        # planted bug (mutants_fair_v3.py, 30 Oct 2026): the EITHER rows' period rates swapped
        mk = lambda seed, bar, period, ok: {'code': 'T1', 'kind': 'null', 'plant': 0, 'seed': seed, 'bar': bar, 'period': period, 'PASS': ok,
                                            'z': 1.0, 'excess_pts': 1.0}
        P, N = 'PASS', 'NOT PASS'
        rows = [mk(0, 'SIZE', 'Sep-Dec', P), mk(0, 'SIZE', 'Jan-Apr', N), mk(0, 'SIDE', 'Sep-Dec', N), mk(0, 'SIDE', 'Jan-Apr', P),
                mk(1, 'SIZE', 'Sep-Dec', N), mk(1, 'SIZE', 'Jan-Apr', P), mk(1, 'SIDE', 'Sep-Dec', N), mk(1, 'SIDE', 'Jan-Apr', N)]
        e = by(rows)[('ALL', 'null', 0, 'EITHER')]
        self.assertEqual((e['rate_SepDec'], e['rate_JanApr'], e['rate_both']), (0.5, 1.0, 0.0))


class T15FilesV3(unittest.TestCase):
    setUp = T8.T12EndToEnd.setUp; tearDown = T8.T12EndToEnd.tearDown; targets = T8.T12EndToEnd.targets
    bz_files = T8.T19Rule7Run.bz_files; run_fair = T07Files.run_fair

    def test_calib_file_and_waves(self):
        T8.gz(os.path.join(self.rc, 'AT99.tsv.gz'), T8.table(self.A_rows, obh=T8.obf(lambda m, k: 1.0)))
        T8.gz(os.path.join(self.rc, 'RT99.tsv.gz'), T8.table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C,
                                                             obh=T8.obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        rc, out = self.run_fair('v3', self.rc, self.apd, self.bz_files(), seeds='3', extra=('--plant-seeds', '1'))
        self.assertEqual(rc, 0)
        K = list(csv.DictReader(open(os.path.join(out, 'FAIR_CALIB.tsv')), delimiter='\t'))
        self.assertEqual(list(K[0].keys()), FV.CALIB_COLS); self.assertEqual(K[0]['code'], 'ALL')
        self.assertEqual({x['kind'] for x in K}, {'null', 'side_flip'})
        self.assertEqual({x['verdict'] for x in K if x['code'] == 'ALL'}, {'TOO FEW ALARMS'})
        R = list(csv.DictReader(open(os.path.join(out, 'FAIR_RUNS.tsv')), delimiter='\t'))
        ran = [x for x in R if x['PASS'] != 'NOT RUN']
        self.assertTrue(ran and all(x['waves'].isdigit() and int(x['waves']) > 0 for x in ran))
        J = __import__('json').load(open(os.path.join(out, 'FAIR_V4.json')))
        self.assertEqual(J['settings']['calib'], {'mean_tol': 0.2, 'sd': [0.8, 1.25], 'spread_max': 1.3, 'min_alarms': 5})
        self.assertEqual(J['settings']['null'], {'pi_max': 0.5}); self.assertNotIn('match_days', J['settings'])
        self.assertTrue(0 <= J['codes']['T99']['null_weight_over_pi_max'] <= 1)
        self.assertEqual((J['settings']['boot'], J['version']), ({'n': 2000, 'seed': 0}, 'fair_v4'))
        self.assertEqual(set(J['code']), {'fair_v4.py', 'fl_read_v11.py', 'md_v1.py', 'labcore/waves.py'})



# ---------------- fair_v4: on edition 11 (the grade's 30 min waves)
class T16GradeWaves(unittest.TestCase):
    def test_on_edition_11(self):
        self.assertEqual((FV.F.VERSION, FV.F.GRADE_WAVE_S), ('fl_read_v11', 1800))

    def test_real_rows_read_thirty_minute_waves(self):
        # fires in pairs 20 min apart (the pairs 12 h apart): 15 min waves would count each fire, the grade's 30 min waves each pair once
        A = T8.fires(months=M.DESIGN, waves=20); A = A + [(c, t + 1200, s, m, k + 100) for (c, t, s, m, k) in A]
        L = T8.look(A, T8.randoms(A), Akw={'obh': T8.RACE10})
        rows = FV.ladder(R0, L, L.R, L.wR, COSTS, None, 1, [], 0)
        real = [x for x in rows if x['kind'] == 'real' and x['bar'] == 'SIDE' and x['period'] == 'Sep-Dec']
        self.assertEqual(real[0]['waves'], 4 * 20)



# ---------------- review C (30 Oct 2026, reviews/REVIEW_C_FL10_FAIR3_20261030.md, fault 2): the ladder's reporting
class T17ReviewC(unittest.TestCase):
    """the 9 planted bugs review C found alive on fair_v3 (the same code in fair_v4), each with the fixture it asked for, and one more:
    the calibration's mean over all runs, not over the alarms' means"""
    def test_interval_low_end(self):
        # 5 codes pass both periods in 1 of 2 runs, 5 codes in 2 of 2: the resampled rates' 2.5 and 97.5 pct points are 0.6 and 0.9
        # (a 25 pct low end would read 0.7)
        self.assertEqual(FV.both_interval([(2, 1)] * 5 + [(2, 2)] * 5), (0.6, 0.9))

    def test_interval_of_the_both_period_passes(self):
        # every code passes Sep-Dec in both runs, Jan-Apr in 1 of 2 (T0-T4) or 2 of 2 (T5-T9): the ALL row's interval is the one of the
        # both-period passes (0.6 to 0.9), not of the Sep-Dec passes (1.0 to 1.0)
        mk = lambda c, s, period, ok: {'code': 'T%d' % c, 'kind': 'null', 'plant': 0, 'seed': s, 'bar': 'SIDE', 'period': period, 'PASS': ok,
                                       'z': 1.0, 'excess_pts': 1.0}
        rows = [mk(c, s, 'Sep-Dec', 'PASS') for c in range(10) for s in range(2)]
        rows += [mk(c, s, 'Jan-Apr', 'PASS' if (c >= 5 or s == 0) else 'NOT PASS') for c in range(10) for s in range(2)]
        a = by(rows)[('ALL', 'null', 0, 'SIDE')]
        self.assertEqual((a['pass_SepDec'], a['pass_both']), (20, 15)); self.assertEqual((a['both_lo'], a['both_hi']), (0.6, 0.9))

    def test_either_given_rate(self):
        # EITHER passes Sep-Dec in 1 run, Jan-Apr in 2, both in none: Jan-Apr given Sep-Dec is 0 of 1 (the Jan-Apr passes would give 2)
        mk = lambda seed, bar, period, ok: {'code': 'T1', 'kind': 'null', 'plant': 0, 'seed': seed, 'bar': bar, 'period': period, 'PASS': ok,
                                            'z': 1.0, 'excess_pts': 1.0}
        P, N = 'PASS', 'NOT PASS'
        rows = [mk(0, 'SIZE', 'Sep-Dec', P), mk(0, 'SIZE', 'Jan-Apr', N), mk(0, 'SIDE', 'Sep-Dec', N), mk(0, 'SIDE', 'Jan-Apr', P),
                mk(1, 'SIZE', 'Sep-Dec', N), mk(1, 'SIZE', 'Jan-Apr', P), mk(1, 'SIDE', 'Sep-Dec', N), mk(1, 'SIDE', 'Jan-Apr', N)]
        e = by(rows)[('ALL', 'null', 0, 'EITHER')]
        self.assertEqual((e['pass_SepDec'], e['pass_JanApr'], e['pass_both'], e['rate_JanApr_given_SepDec']), (1, 2, 0, 0.0))

    def test_sd_within_is_the_root_of_the_mean_variance(self):
        # 3 alarms at Z10, 3 at 3 x Z10: the sd within alarms is the root of their mean variance (root 5 x Z10's sd), not the mean of
        # their sds (2 x Z10's sd)
        rows = [crow('T%d' % c, (1.0 if c < 3 else 3.0) * z, s) for c in range(6) for s, z in enumerate(np.roll(Z10, c))]
        a = cal(rows)[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        self.assertAlmostEqual(a['sd_z'], math.sqrt(5.0) * float(np.std(Z10, ddof=1)), places=12)

    def test_shares_at_exactly_two(self):
        # each alarm's 10 runs hold one z of exactly 2, one of 1.5 and one of 1: P(z >= 2) is 0.1 for each alarm and for ALL, P(z >= 1) 0.3
        zs = [-1.5, -1.0, -0.75, -0.5, 0.0, 0.0, 0.5, 1.0, 1.5, 2.0]
        C = cal([crow('T%d' % c, z, s) for c in range(6) for s, z in enumerate(np.roll(zs, c))])
        for k in ['ALL'] + ['T%d' % c for c in range(6)]:
            x = C[(k, 'null', 'SIDE', 'Sep-Dec')]
            self.assertAlmostEqual(x['p_z_ge_2'], 0.1, places=12); self.assertAlmostEqual(x['p_z_ge_1'], 0.3, places=12)

    def test_leans_at_three_errors_not_two(self):
        # T0's mean z is 2.5 errors from 0 (an error: the sd over the root of the runs): not LEANS; T1's 3.5 errors: LEANS
        se = float(np.std(Z10, ddof=1)) / math.sqrt(10)
        C = cal(six(shift=lambda c: {0: 2.5 * se, 1: 3.5 * se}.get(c, 0.0)))
        self.assertEqual([C[('T%d' % c, 'null', 'SIDE', 'Sep-Dec')]['verdict'] for c in range(3)], ['-', 'LEANS', '-'])

    def test_mean_over_all_runs(self):
        # 6 alarms of 10 runs at mean 0 and T8 with one run at z 3: ALL's runs and mean z are over the 61 runs (3 / 61), not the mean of
        # the 7 alarms' means (3 / 7); T8 is not one of the alarms of the sd and the spread (one run)
        a = cal(six() + [crow('T8', 3.0, 0)])[('ALL', 'null', 'SIDE', 'Sep-Dec')]
        self.assertEqual((a['alarms'], a['runs']), (6, 61)); self.assertAlmostEqual(a['mean_z'], 3.0 / 61, places=12)

    def test_made_up_fires_moments_5_min_before_stay_in(self):
        # a random moment of row 3's coin 5 min before it (no real fire near) stays in the made-up alarm's random: the made-up alarm has
        # no pre-fire cut of its own, at any distance (T08 checks 20 min)
        L, R, w, bz = fworld(ALLHIT, R70); n = len(R['t'])
        R2 = {k: np.append(v, v[3]) for k, v in R.items()}; R2['coin'] = R2['coin'].astype(object); R2['t'][n] = R['t'][3] - 300
        w2 = np.append(w, 1 / 3.0); L = F.Look(L.A, R2, w2, COSTS, 'FADE', pre_R=F.pre_fire_mask(L.A, R2))
        bz2 = {'A': bz['A'], 'R': {k: np.append(v, v[3]) for k, v in bz['R'].items()}}
        self.assertFalse(L.preR[n])
        L2, _ = FV.made_up(L, R2, w2, COSTS, bz2, np.array([3]))
        self.assertFalse(L2.preR[-1]); self.assertEqual(int(L2.preR.sum()), 0); self.assertTrue(L2.useR[-1])


class T18ReviewCFiles(unittest.TestCase):
    setUp = T8.T12EndToEnd.setUp; tearDown = T8.T12EndToEnd.tearDown; targets = T8.T12EndToEnd.targets
    bz_files = T8.T19Rule7Run.bz_files; run_fair = T07Files.run_fair

    def test_manifest_share_over_the_moments_that_can_be_drawn(self):
        # review C: FAIR_V4.json's share of the null's weight over PI_MAX counts only the moments that can be made-up fires. Here the
        # random moments of every 4th fire and of the coins without a cost (C10-C12: never drawn) weigh 0.9, the rest 1/3
        heavy = lambda c, k: k % 4 == 0 or c not in COSTS
        ws = [0.9 if heavy(c, k) else 1 / 3.0 for (c, t, s, m, k) in self.R_rows]
        with open(os.path.join(self.inp, 'R_T99_W.tsv'), 'w') as f:
            f.write('coin\tt\tw\n' + ''.join('%s\t%d\t%r\n' % (c, t, x) for (c, t, s, m, k), x in zip(self.R_rows, ws)))
        T8.gz(os.path.join(self.rc, 'AT99.tsv.gz'), T8.table(self.A_rows, obh=T8.obf(lambda m, k: 1.0)))
        T8.gz(os.path.join(self.rc, 'RT99.tsv.gz'), T8.table(self.R_rows, best=lambda *a: 2 * C, worst=lambda *a: 2 * C,
                                                             obh=T8.obf(lambda m, k: 1.0 if k % 10 == 0 else 0.0)))
        rc, out = self.run_fair('ms', self.rc, self.apd, self.bz_files(), seeds='1', extra=('--plant-seeds', '1'))
        self.assertEqual(rc, 0)
        J = __import__('json').load(open(os.path.join(out, 'FAIR_V4.json')))
        can = [x for (c, t, s, m, k), x in zip(self.R_rows, ws) if c in COSTS]
        every = sum(x for x in ws if x > 0.5) / sum(ws); share = sum(x for x in can if x > 0.5) / sum(can)
        self.assertLess(len(can), len(ws)); self.assertGreater(abs(share - every), 0.05)
        self.assertAlmostEqual(J['codes']['T99']['null_weight_over_pi_max'], share, places=4)


if __name__ == '__main__':
    unittest.main(verbosity=1)
