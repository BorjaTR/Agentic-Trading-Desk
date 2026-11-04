"""test_i2g_v3_2_rel1.py: test_i2g_v3_2.py (83d675829fea3aeb, never edited) on the rel1 editions. Owner STRATEGY/LEAD (the grader thread).
New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Changed: the modules tested are idea_to_grade_v3_2_rel1 and i2g_engine_v3_2_rel1
(and V2 mode reads idea_to_grade_rel1.py and i2g_engine_rel1.py, the V2.3.1 code of this chain); the argument lists of the two "everything
but X is given" checks carry the new required --lab-root and --research-root, so each still fails on the one argument it names;
test 15 names the research root (the tree's team/RESEARCH) before it asks run_class for GRADED; test 12 scans the rel1 files. Every
assertion is test_i2g_v3_2.py's. It reads the dev layout from the tree root (team/RESEARCH/...): no view of links is needed.
The rest of this text is test_i2g_v3_2.py's.
[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file test_i2g_v3.py 874f628c269d6186 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
test_i2g_v3_2.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026): the V3 grading rules, no lab data read (standard library + numpy).
Tests 13-19 are the V3.1 fixes of REVIEW_IDEA_TO_GRADE_V3_INDEP (F1-F6 and the chain-split sensitivity): each one fails on the V3
candidate (RELEASE_idea_to_grade_V3_CANDIDATE.json) and passes on V3.1.
Each test runs against the implementation chosen by I2G_IMPL:
  I2G_IMPL=v3 python3 -B test_i2g_v3_2.py     the V3 rules (i2g_rules_v1_2, i2g_grade3_v3_2, idea_to_grade_v3_2): must pass
  I2G_IMPL=v2 python3 -B test_i2g_v3_2.py     V2.3.1 as it is (draw_v3.own_flag, labcore.waves per run, coin_t ids, the fixed delay, no
                                            ledger, no exit or resting rule): expected to FAIL or ERROR where V2.3.1 had the fault
The real-data checks (V2 compatibility, a second alarm on other coins and other days, the delay moving the fill) are in test_i2g_v3_2_real.py."""
import argparse, ast, importlib.util, os, re, sys, tempfile, unittest
import numpy as np
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
FO = os.environ.get('I2G_FORENSICS') or os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))   # forensics (mutant runs: env)
TOOLS = os.path.join(FO, 'team', 'RESEARCH', 'tools')
IMPL = os.environ.get('I2G_IMPL', 'v3')
US = 1_000_000


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


class V2:
    """V2.3.1's behaviour, taken from its own code where it exists"""
    D = load(os.path.join(TOOLS, 'alarm_match', 'draw_v3.py'), 'draw_v3_t')
    W = load(os.path.join(TOOLS, 'labcore', 'waves.py'), 'waves_t')
    UNKNOWN = object()

    @staticmethod
    def control_eligible(cand_t, parent_t, busy, horizon_s=14466):
        return V2.D.own_flag(parent_t, cand_t, horizon_s) == ''

    @staticmethod
    def parent_id(coin, t, side):
        return '%s_%d' % (coin, int(t))                       # i2g_engine.coin_job and idea_to_grade.aggregate: coin_t

    @staticmethod
    def slice_weights(alarm_id, fires, subset):
        """V2: the waves are rebuilt by each run on ITS parents (idea_to_grade.aggregate: k.waves(parents, 1800))"""
        t = np.asarray([f[2] for f in subset], float); w = V2.W.wave_weights(V2.W.waves(t, 1800))
        return {V2.parent_id(f[1], f[2], f[3]): float(x) for f, x in zip(subset, w)}

    @staticmethod
    def delay_is_a_setting():
        with open(os.path.join(HERE, 'i2g_engine_rel1.py')) as f:
            return 'S.DELAY_S, S.HOLD_S' not in f.read()

    @staticmethod
    def needs_ledger():
        with open(os.path.join(HERE, 'idea_to_grade_rel1.py')) as f:
            return 'ledger' in f.read()

    barrier_exit = passive_entry = clustered_mean = None


class V3:
    import i2g_rules_v1_2 as RU

    @staticmethod
    def control_eligible(cand_t, parent_t, busy, horizon_s=14466):
        return V3.RU.asof_flag(cand_t, sorted(busy)) == ''

    @staticmethod
    def parent_id(coin, t, side):
        return V3.RU.parent_id(coin, t, side)

    @staticmethod
    def slice_weights(alarm_id, fires, subset):
        U = V3.RU.Universe(V3.RU.build_clusters(fires), 'test')
        got = U.subgroup(alarm_id, [V3.RU.parent_id(c, t, s) for _, c, t, s in subset])
        return {p: w for p, (_, w, _) in got.items()}

    @staticmethod
    def delay_is_a_setting():
        with open(os.path.join(HERE, 'i2g_engine_v3_2_rel1.py')) as f:
            src = f.read()
        return "delay = float(v3['delay_s'])" in src and 'S.DELAY_S, S.HOLD_S' not in src.split('def coin_job')[1]

    @staticmethod
    def needs_ledger():
        import idea_to_grade_v3_2_rel1 as I3
        try:
            I3.parser().parse_args(['--first', '20250101', '--last', '20250101', '--research-window', '20250101:20250101', '--out', 'x',
                                    '--lab-root', 'L', '--research-root', 'R', '--delay-s', '1', '--alarm-id', 'ALM_X'])           # everything but the ask
        except SystemExit:
            return True
        return False

    barrier_exit = staticmethod(RU.barrier_exit); passive_entry = staticmethod(RU.passive_entry)
    clustered_mean = staticmethod(RU.clustered_mean)


A = V3 if IMPL == 'v3' else V2


def path(prices, t0=1_000_000_000, step=3):
    """synthetic 3 s bins: [(close, high, low)] -> tl, px, hi, lo (last trade = bin end)"""
    tl = np.asarray([(t0 + step * (i + 1)) * US for i in range(len(prices))], np.int64)
    px, hi, lo = (np.asarray([p[j] for p in prices], float) for j in range(3))
    return tl, px, hi, lo


class T(unittest.TestCase):
    # ------------------------------------------------------------------ 1 as-of control eligibility
    def test_01_a_later_alarm_does_not_drop_a_control(self):
        ct = 50_000.0
        self.assertTrue(A.control_eligible(ct, parent_t=ct + 600, busy=[ct + 600]))        # V2: BEFORE_30M of its own parent: dropped
        self.assertTrue(A.control_eligible(ct, parent_t=ct + 7200, busy=[ct + 7200]))      # V2: WITHIN_H: dropped
        self.assertFalse(A.control_eligible(ct, parent_t=ct - 600, busy=[ct - 600]))       # an alarm 10 min BEFORE: busy in both

    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_01b_asof_window_is_closed_at_the_moment_and_4h_long(self):
        RU = V3.RU
        self.assertEqual(RU.asof_flag(100.0, [100.0]), 'ASOF_BUSY')                         # the alarm moment itself is never a control
        self.assertEqual(RU.asof_flag(20000.0, [20000.0 - 14400]), 'ASOF_BUSY')
        self.assertEqual(RU.asof_flag(20000.0, [20000.0 - 14401]), '')
        m = RU.asof_mask([100.0, 20000.0, 30000.0], [100.0, 20000.0 - 14401, 30500.0])          # 30500: after the moment
        self.assertEqual(list(m), [False, True, True])

    # ------------------------------------------------------------------ 2 frozen weights
    def _fires(self):
        f = [('X', 'AAA' if i % 2 else 'BBB', 1000 + 600 * i, 1) for i in range(5)]           # one wave over two coins
        f += [('X', 'CCC', 100_000 + 1200 * i, -1) for i in range(16)]                        # a 5 h chain, gaps 20 min
        return f

    def test_02_a_slice_keeps_the_full_weights(self):
        fires = self._fires()
        full = A.slice_weights('X', fires, fires)
        for part in ([f for f in fires if f[1] == 'AAA'], [f for f in fires if f[1] == 'BBB'], fires[5:8]):
            got = A.slice_weights('X', fires, part)
            self.assertEqual(got, {k: full[k] for k in got})                                  # V2: rebuilt per selection -> differ

    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_02b_span_rule_and_universe_refusal(self):
        RU = V3.RU; rows = RU.build_clusters(self._fires())
        self.assertIn('CHAIN_SPLIT', {r[8] for r in rows})
        self.assertTrue(all(r[2] - int(r[5].split(':')[1]) <= RU.WAVE_MAX_SPAN_S for r in rows))
        sums = {}
        for r in rows:
            sums[r[5]] = sums.get(r[5], 0) + r[6]
        self.assertTrue(all(abs(v - 1) < 1e-12 for v in sums.values()))                        # each cluster counts once
        U = RU.Universe(rows, 'u')
        with self.assertRaises(RU.Refused):
            U.subgroup('X', ['ZZZ_1_+1'])
        with self.assertRaises(RU.Refused):
            U.subgroup('OTHER', [rows[0][4]])                                                  # clusters never mix alarms
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'U.tsv'); RU.write_universe(p, rows, [('X=x', '0' * 16)])
            self.assertEqual(RU.Universe.read(p).by, U.by)
            with self.assertRaises(FileExistsError):
                RU.write_universe(p, rows, [])

    # ------------------------------------------------------------------ 3 identity
    def test_03_opposite_sides_in_one_second_are_two_events(self):
        self.assertNotEqual(A.parent_id('AAA', 1_760_000_000, 1), A.parent_id('AAA', 1_760_000_000, -1))

    # ------------------------------------------------------------------ 4 exits
    def test_04_target_and_stop_inside_one_bin_is_the_stop(self):
        tl, px, hi, lo = path([(100, 100, 100), (100, 101.5, 98.5), (101, 101, 101)])
        code, t, g = A.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, 1, 1.0, 1.0, 900, int(tl[-1]) + 3600 * US)
        self.assertEqual(code, 'AMBIGUOUS_STOP'); self.assertAlmostEqual(g, -1.0)
        code, t, g = A.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, -1, 1.0, 1.0, 900, int(tl[-1]) + 3600 * US)
        self.assertEqual(code, 'AMBIGUOUS_STOP'); self.assertAlmostEqual(g, -1.0)                # the short side too

    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_04b_exit_kinds_and_unknown_path(self):
        RU = V3.RU
        tl, px, hi, lo = path([(100, 100, 100), (100.5, 100.6, 100.4), (99.3, 100.5, 98.9), (102, 102, 102)])
        self.assertEqual(RU.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, 1, 2.0, 1.0, 900, int(tl[-1]) + 3600 * US)[:1], ('STOP',))
        g = RU.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, 1, 2.0, 1.0, 900, int(tl[-1]) + 3600 * US)[2]
        self.assertAlmostEqual(g, -1.0)                                                        # stop level (close 99.3 is better)
        tl2, px2, hi2, lo2 = path([(100, 100, 100), (98.5, 99.6, 98.0)])
        self.assertAlmostEqual(RU.barrier_exit(tl2, px2, hi2, lo2, 0, int(tl2[0]), 100.0, 1, 2.0, 1.0, 900, int(tl2[-1]) + 3600 * US)[2], -1.5)                       # a gap through the stop: the worse close
        # target with a touch only: TARGET for a taker trigger, nothing for a resting target
        tl3, px3, hi3, lo3 = path([(100, 100, 100), (100.5, 101.0, 100.2), (100.4, 100.6, 100.3)])
        self.assertEqual(RU.barrier_exit(tl3, px3, hi3, lo3, 0, int(tl3[0]), 100.0, 1, 1.0, 1.0, 6, int(tl3[-1]) + 3600 * US)[0], 'TARGET')
        self.assertEqual(RU.barrier_exit(tl3, px3, hi3, lo3, 0, int(tl3[0]), 100.0, 1, 1.0, 1.0, 6, int(tl3[-1]) + 3600 * US,
                                         resting_target=True)[0], 'TIME')
        # the limit beyond the known path and no barrier before: unknown, never a time exit
        self.assertEqual(RU.barrier_exit(tl3, px3, hi3, lo3, 0, int(tl3[0]), 100.0, 1, 5.0, 5.0, 900, int(tl3[-1]))[0], None)
        r = RU.horizon_returns(tl3, px3, 0, int(tl3[0]), 100.0, 1, int(tl3[0]) + 10 * US, horizons_s=(3, 6, 60))
        self.assertAlmostEqual(r[0], 0.5); self.assertAlmostEqual(r[1], 0.4); self.assertTrue(np.isnan(r[2]))

    # ------------------------------------------------------------------ 5 resting orders
    def test_05_a_touch_is_not_a_fill(self):
        tl, px, hi, lo = path([(100, 100, 100), (100.2, 100.4, 100.0), (100.1, 100.3, 99.9)])
        st, j, t, L = A.passive_entry(tl, px, lo, hi, int(tl[0]), 1, wait_s=3)
        self.assertEqual(st, 'UNFILLED')                                                       # low 100.0 = the limit: a touch
        st, j, t, L = A.passive_entry(tl, px, lo, hi, int(tl[0]), 1, wait_s=60)
        self.assertEqual((st, j, L), ('FILLED', 2, 100.0))                                     # low 99.9 trades through
        st, j, t, L = A.passive_entry(tl, px, lo, hi, int(tl[0]), -1, wait_s=60)
        self.assertEqual((st, j), ('FILLED', 1))                                               # sell limit: high 100.4 > 100

    # ------------------------------------------------------------------ 6 ledger
    def test_06_a_run_without_a_ledger_ask_is_refused(self):
        self.assertTrue(A.needs_ledger())
        if IMPL == 'v3':
            RU = V3.RU
            with tempfile.TemporaryDirectory() as d:
                p = os.path.join(d, 'L.tsv')
                with open(p, 'w') as f:
                    f.write('# ledger\ntry_utc\task_id\tidea\tkind\n1\tPREREG_A_1\tA\tPREREG\n2\tPREREG_B_2\tB\tPREREG\n3\tPREREG_B_2_R\tB\tRESULT\n')
                self.assertEqual(RU.ledger_check(p, 'PREREG_A_1')['idea'], 'A')
                for ask, code in (('', 'LEDGER_ASK_MISSING'), ('PREREG_Z', 'LEDGER_ASK_UNKNOWN'), ('PREREG_B_2', 'LEDGER_ASK_CLOSED')):
                    with self.assertRaises(RU.Refused) as e:
                        RU.ledger_check(p, ask)
                    self.assertEqual(e.exception.code, code)

    # ------------------------------------------------------------------ 7 delay
    def test_07_the_delay_is_a_setting(self):
        self.assertTrue(A.delay_is_a_setting())

    # ------------------------------------------------------------------ 8 features and the tough pool
    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_08_features_read_only_the_past(self):
        RU = V3.RU
        te = np.arange(0, 3600, 3, dtype=float); px = 100 * np.exp(0.0001 * np.arange(len(te)))
        mv, rv = RU.asof_features(te, px, [1800.0])
        self.assertAlmostEqual(mv[0], 100 * (np.exp(0.0001 * 300) - 1), places=9)              # 900 s = 300 bins
        self.assertAlmostEqual(rv[0], 100 * np.sqrt(100 * 0.0001 ** 2), places=9)              # 300 s = 100 returns
        px2 = px.copy(); px2[te > 1800] *= 3                                                   # the future changes, the reading does not
        self.assertEqual(list(RU.asof_features(te, px2, [1800.0])[0]), list(mv))
        self.assertTrue(np.isnan(RU.asof_features(te, px, [600.0])[0][0]))                    # no bin 900 s back
        self.assertTrue(np.isnan(RU.asof_features(te, px, [5000.0])[0][0]))                   # stale: the last bin is 1.4 ks old

    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_08b_tough_pool(self):
        RU = V3.RU
        g = np.arange(100) * 60.0; mv = np.linspace(-2, 2, 100); rv = np.full(100, 0.3); ok = np.ones(100, bool)
        ch, st, n = RU.tough_pick('P_1_+1', 7, 1, 1.0, 0.3, 0.2, g, mv, rv, ok)
        sel = [int(x / 60) for x in ch]
        self.assertEqual(st, 'TOUGH_OK'); self.assertEqual(len(ch), 10)
        self.assertTrue(all(abs(mv[i] - 1.0) <= max(0.1, 0.25) + 1e-12 for i in sel))
        self.assertEqual(ch, RU.tough_pick('P_1_+1', 7, 1, 1.0, 0.3, 0.2, g, mv, rv, ok)[0])  # seeded
        import zlib                                                                            # the stated stream: (seed, crc32('tough|' + id))
        pool = np.flatnonzero((np.abs(mv - 1.0) <= 0.25) & ok)
        want = np.sort(np.random.default_rng([7, zlib.crc32(b'tough|P_1_+1')]).choice(pool, size=10, replace=False))
        self.assertEqual(sel, [int(i) for i in want])
        ch2 = RU.tough_pick('P_1_-1', 7, -1, -1.0, 0.3, 0.2, g, mv, rv, ok)[0]                 # signed by the side: the mirror cell
        self.assertTrue(all(mv[int(x / 60)] < 0 for x in ch2))
        ok2 = ok.copy(); ok2[sel] = False                                                       # busy moments never enter
        self.assertFalse(set(RU.tough_pick('P_1_+1', 7, 1, 1.0, 0.3, 0.2, g, mv, rv, ok2)[0]) & set(ch))
        self.assertEqual(RU.tough_pick('P', 7, 1, np.nan, 0.3, 0.2, g, mv, rv, ok)[1], 'TOUGH_UNKNOWN')
        self.assertEqual(RU.tough_pick('P', 7, 1, 1.0, 9.0, 0.2, g, mv, rv, ok)[1], 'TOUGH_NONE')

    # ------------------------------------------------------------------ 9 costs and statistics
    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_09_cost_legs(self):
        RU = V3.RU
        tk, rs = RU.cost_legs(14.735, 0.032, 1.5)
        self.assertAlmostEqual(2 * tk, RU.coin_cost_pct(14.735, 0.032))                        # taker round trip = c
        self.assertAlmostEqual(rs, 0.015 + 0.016)
        import i2g_grade3_v3_2 as G3
        g = np.array([1.0, 1.0]); code = np.array([1.0, 2.0])
        self.assertEqual(list(G3.net(g, 'RR', code, (np.full(2, tk), np.full(2, rs)))), [1 - 2 * rs, 1 - rs - tk])

    def test_10_wave_clustered_interval(self):
        r = A.clustered_mean([1.0, 3.0, 5.0, 7.0], [1, 1, 1, 1], ['a', 'b', 'c', 'd'])
        se = np.std([1, 3, 5, 7], ddof=1) / 2
        self.assertAlmostEqual(r['mean'], 4.0); self.assertAlmostEqual(r['se'], se)
        r2 = A.clustered_mean([1.0, 1.0, 7.0, 7.0], [0.5, 0.5, 0.5, 0.5], ['a', 'a', 'b', 'b'])
        self.assertEqual(r2['clusters'], 2); self.assertAlmostEqual(r2['se'], 3.0)               # two waves: two draws, not four

    @unittest.skipIf(IMPL == 'v2', 'V3-only rule check (V2.3.1 has no such rule)')
    def test_11_grade3_slices_read_frozen_weights(self):
        import i2g_grade3_v3_2 as G3, i2g_rules_v1_2 as RU
        names = RU.value_names(); n_rows = 8; V3m = np.full((n_rows, len(names)), np.nan)
        col = {c: i for i, c in enumerate(names)}
        V3m[:, col['ret_10s']] = np.arange(n_rows, dtype=float); V3m[:, col['tk_filled']] = 1
        parents = [{'coin': 'AAA', 'day': d, 'row_ids': {'FOLLOW': 2 * i, 'FADE': 2 * i + 1}} for i, d in
                   enumerate(['20990101', '20990102', '20990201', '20990202'])]
        empty = {d: [[] for _ in parents] for d in ('FOLLOW', 'FADE')}
        w = [0.5, 0.5, 1.0, 1.0]; cl = ['a', 'a', 'b', 'c']
        rows = G3.grade(parents, names, V3m, ['AAA'] * n_rows, empty, empty, empty, w, cl, {'HONEST': {'AAA': (0.0, 0.0)}})
        get = {(r[0], r[1], r[2], r[4], r[5]): r for r in rows}
        self.assertAlmostEqual(get[('ALL', 'FOLLOW', 'ret_10s', 'GROSS', 'PARENT')][6], (0.5 * 0 + 0.5 * 2 + 4 + 6) / 3)
        self.assertAlmostEqual(get[('209902', 'FOLLOW', 'ret_10s', 'GROSS', 'PARENT')][6], 5.0)
        self.assertEqual(get[('209901', 'FOLLOW', 'ret_10s', 'GROSS', 'PARENT')][10], 1)        # one wave in January

    # ------------------------------------------------------------------ 12 generic: no alarm, coin or date in the code
    def test_12_no_alarm_coin_or_date_in_the_code(self):
        """an AST scan (review paperwork, N3): every string and number constant of the code, docstrings included"""
        files = ['i2g_rules_v1_2.py', 'i2g_engine_v3_2_rel1.py', 'i2g_grade3_v3_2.py', 'idea_to_grade_v3_2_rel1.py', 'i2g_universe_v1.py', 'alarm_contract_v1.py'] \
            if IMPL == 'v3' else ['i2g_engine_rel1.py', 'i2g_grade_rel1.py', 'idea_to_grade_rel1.py']
        cost = os.path.join(FO, 'team', 'RESEARCH', 'QUANT', 'receipts', 'COSTS_PER_COIN_V1.tsv')
        with open(cost) as f:
            coins = {line.split('\t')[0] for line in f if not line.startswith(('#', 'coin\t'))}
        alarms = {'H0', 'S1', 'S2', 'S3', 'S3W', 'A02', 'A02P', 'B0', 'R1', 'C3', 'M1'}
        allowed_numbers = {'20261023'}                                                           # the matcher's seed (V2.3.1's default)
        bad = []
        for fn in files:
            with open(os.path.join(HERE, fn)) as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if not isinstance(node, ast.Constant):
                    continue
                v = node.value
                if isinstance(v, bool):
                    continue
                if isinstance(v, int) and 20000101 <= v <= 20991231 and str(v) not in allowed_numbers:
                    bad.append((fn, node.lineno, v))
                if isinstance(v, str):
                    bad += [(fn, node.lineno, m) for m in re.findall(r'(?<!\d)20\d{6}(?!\d)', v) if m not in allowed_numbers]
                    bad += [(fn, node.lineno, w) for w in re.findall(r'[A-Z0-9]{2,10}', v) if w == v.strip() and (w in coins or w in alarms)]
        self.assertEqual(bad, [])

    # ------------------------------------------------------------------ 13 F1: a feed hole is unknown, never the last close
    @staticmethod
    def _hole_path(hole_s):
        t0 = 1_000_000_000; tl = []; t = t0
        for i in range(40):
            t += 3 + (hole_s if i == 20 else 0)
            tl.append(t * US)
        px = np.asarray([100.0] * 20 + [105.0] * 20)
        return np.asarray(tl, np.int64), px, px.copy(), px.copy()

    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_13_a_feed_hole_gives_unknown(self):
        RU = V3.RU
        tl, px, hi, lo = self._hole_path(7200)                                                   # review CE1: a 2 h hole after 60 s
        far = int(tl[-1]) + 10 * 3600 * US
        r = RU.horizon_returns(tl, px, 0, int(tl[0]), 100.0, 1, far)
        self.assertEqual(r[:2], [0.0, 0.0])                                                      # 10 s, 1 min: fresh prices
        self.assertTrue(all(np.isnan(x) for x in r[2:]), r)                                      # 5 min .. 4 h fall in or after the hole
        self.assertEqual(RU.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, 1, 50.0, 50.0, 3600, far)[0], 'PATH_HOLE')   # the TIME exit
        self.assertEqual(RU.barrier_exit(tl, px, hi, lo, 0, int(tl[0]), 100.0, 1, 2.0, 50.0, 14400, far)[0], 'PATH_HOLE')  # a target after the hole
        row = RU.path_values(tl, px, hi, lo, ('FILLED', 0, int(tl[0]), 100.0), int(tl[0]) - 3 * US, 1, far, 0.0, 1.0, 0.2)
        names = RU.value_names()
        self.assertGreater(row[names.index('path_holes')], 0)
        self.assertEqual(row[names.index('tk_V1_1h_code')], RU.EXIT_CODES['PATH_HOLE']); self.assertTrue(np.isnan(row[names.index('tk_V1_1h')]))
        tl2, px2, hi2, lo2 = self._hole_path(0)                                                  # the same path without the hole: unchanged
        end2 = int(tl2[-1]) + 3600 * US
        r2 = RU.horizon_returns(tl2, px2, 0, int(tl2[0]), 100.0, 1, end2, horizons_s=(10, 57, 90))
        self.assertEqual(r2[:2], [0.0, 0.0]); self.assertAlmostEqual(r2[2], 5.0)
        self.assertEqual(RU.barrier_exit(tl2, px2, hi2, lo2, 0, int(tl2[0]), 100.0, 1, 2.0, 50.0, 900, end2 + 900 * US)[:2],
                         ('TARGET', int(tl2[20])))
        r3 = RU.horizon_returns(tl, px, 0, int(tl[0]), 100.0, 1, far, horizons_s=(7262,))     # after the hole, a fresh price is known again
        self.assertAlmostEqual(r3[0], 5.0)

    # ------------------------------------------------------------------ 14 F2: the universe is checked, its sha16 frozen at admission
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_14_universe_checked_and_frozen(self):
        RU = V3.RU
        import idea_to_grade_v3_2_rel1 as I3
        rows = RU.build_clusters([('X', 'AAA', 1000 + 60 * i, 1) for i in range(4)] + [('X', 'BBB', 90000, -1)])
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'U.tsv'); RU.write_universe(p, rows, [('X=/fires.tsv', 'f' * 16)])
            U = RU.Universe.read(p)
            self.assertEqual(U.sources, {'X': ('/fires.tsv', 'f' * 16)})
            good = open(p).read()
            for name, txt, code in (('weight', good.replace('\t0.25\t4\t', '\t1.0\t4\t'), 'UNIVERSE_INCONSISTENT'),
                                    ('size', good.replace('\t0.25\t4\t', '\t0.25\t3\t'), 'UNIVERSE_INCONSISTENT'),
                                    ('cluster', good.replace('X:90000', 'X:1000'), 'UNIVERSE_INCONSISTENT'),
                                    ('header', good.replace('gap_s 1800', 'gap_s 99999'), 'UNIVERSE_HEADER'),
                                    ('twice', good + good.split('\n')[-2] + '\n', 'UNIVERSE_DUPLICATE')):
                q = os.path.join(d, name + '.tsv')
                with open(q, 'w') as f:
                    f.write(txt)
                with self.assertRaises(RU.Refused) as e:
                    RU.Universe.read(q)
                self.assertEqual(e.exception.code, code, name)
            frozen = {'universe': (p, I3.sha16(p))}
            I3.recheck_frozen(frozen)
            with open(p, 'a') as f:
                f.write('# a line added during the run\n')
            with self.assertRaises(Exception) as e:
                I3.recheck_frozen(frozen)
            self.assertIn('UNIVERSE_CHANGED', str(e.exception))

    # ------------------------------------------------------------------ 15 F3: the ledger counts tries
    @staticmethod
    def _args(**kw):
        a = dict(ledger='L.tsv', registry='R.tsv', universe='U.tsv', compat_v2=False, detect_run=None)
        a.update(kw); return argparse.Namespace(**a)

    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_15_one_ask_one_run_of_its_idea_and_days(self):
        RU = V3.RU
        import idea_to_grade_v3_2_rel1 as I3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'L.tsv')
            with open(p, 'w') as f:
                f.write('try_utc\task_id\tidea\tkind\tdays_from\tdays_to\n1\tPREREG_A\tALM_X\tPREREG\t20990101\t20990131\n'
                        '2\tPREREG_B\tALM_X\tPREREG\t\t\n')
            self.assertEqual(RU.ledger_check(p, 'PREREG_A', idea='ALM_X', first='20990101', last='20990131')['idea'], 'ALM_X')
            for kw in (dict(idea='ALM_Y', first='20990101', last='20990131'), dict(idea='ALM_X', first='20990101', last='20990228')):
                with self.assertRaises(RU.Refused) as e:
                    RU.ledger_check(p, 'PREREG_A', **kw)
                self.assertEqual(e.exception.code, 'LEDGER_ASK_MISMATCH')
            with self.assertRaises(RU.Refused) as e:                                               # blank days are not "any days"
                RU.ledger_check(p, 'PREREG_B', idea='ALM_X', first='20990101', last='20990131')
            self.assertEqual(e.exception.code, 'LEDGER_ASK_MISMATCH')
            RU.ledger_claim(p, 'PREREG_A', {'out': 'run1'})
            for f_ in (lambda: RU.ledger_check(p, 'PREREG_A', idea='ALM_X', first='20990101', last='20990131'),
                       lambda: RU.ledger_claim(p, 'PREREG_A', {'out': 'run2'})):
                with self.assertRaises(RU.Refused) as e:
                    f_()
                self.assertEqual(e.exception.code, 'LEDGER_ASK_USED')
        I3.set_research_root(os.path.join(FO, 'team', 'RESEARCH'))                         # rel1: the canonical ledger and registry
        self.assertEqual(I3.run_class(self._args(ledger=I3.LEDGER, registry=I3.REGISTRY)), 'GRADED')
        for kw in (dict(), dict(ledger=I3.LEDGER), dict(registry=I3.REGISTRY), dict(ledger=I3.LEDGER, registry=I3.REGISTRY, universe=None),
                   dict(ledger=I3.LEDGER, registry=I3.REGISTRY, compat_v2=True)):
            self.assertEqual(I3.run_class(self._args(**kw)), 'TEST', kw)

    # ------------------------------------------------------------------ 16 F4: the 15 min move is signed per row
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_16_opposite_parents_in_one_second_keep_their_own_move_sign(self):
        RU = V3.RU
        import i2g_engine_v3_2_rel1 as E3
        names = RU.value_names(); m15 = names.index('move15_pct'); T_ = 1_760_000_000 * US
        obs = [('parent', T_, 1, 'FOLLOW'), ('parent', T_, 1, 'FADE'), ('parent', T_, -1, 'FOLLOW'), ('parent', T_, -1, 'FADE')]
        values = np.full((4, 2), np.nan); values3 = np.full((4, len(names)), np.nan); calls = []
        def measure(t_us, side, d, traded):
            calls.append(traded); return np.zeros(2), {}, np.zeros(len(names)), 0.8          # the unsigned move at T_ is +0.8
        E3.fill_rows(range(4), obs, values, values3, {}, {}, measure, m15)
        self.assertEqual(sorted(calls), [-1, 1])                                                 # +1 FADE and -1 FOLLOW share one memo
        self.assertEqual(list(values3[:, m15]), [0.8, 0.8, -0.8, -0.8])                          # each row signed by its parent side

    # ------------------------------------------------------------------ 17 F5: the alarm id is a registry id bound to its events
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_17_alarm_id_must_be_registered_and_bound(self):
        RU = V3.RU
        import idea_to_grade_v3_2_rel1 as I3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'R.tsv')
            with open(p, 'w') as f:
                f.write('# registry\nregistry_id\tcard\tversion\tdefinition\tdefinition_sha16\tfamily\nALM_X\tc\t1\tdef.json\t' + 'a' * 16 + '\tf\n')
            reg = RU.read_registry(p)
            U = RU.Universe(RU.build_clusters([('ALM_X', 'AAA', 1000, 1)]), 'u', {'ALM_X': ('/fires.tsv', 'e' * 16)})
            self.assertEqual(RU.alarm_check(reg, 'ALM_X', definition_sha16='a' * 16)[1], 'NO_UNIVERSE')
            self.assertEqual(RU.alarm_check(reg, 'ALM_X', events_sha16='e' * 16, universe=U)[1], 'SOURCE_LIST')
            self.assertEqual(RU.alarm_check(reg, 'ALM_X', events_sha16='0' * 16, universe=U, events_subset=True)[1], 'DECLARED_SUBSET')
            U2 = RU.Universe(RU.build_clusters([('ALM_Y', 'AAA', 1000, 1)]), 'u2', {'ALM_Y': ('/y.tsv', 'e' * 16)})
            for kw, code in ((dict(alarm_id='ALM_Z'), 'ALARM_ID_UNKNOWN'),
                             (dict(alarm_id='ALM_X', definition_sha16='b' * 16), 'ALARM_DEFINITION_MISMATCH'),
                             (dict(alarm_id='ALM_X', events_sha16='0' * 16, universe=U), 'ALARM_EVENTS_MISMATCH'),
                             (dict(alarm_id='ALM_X', events_sha16='e' * 16, universe=U2), 'UNIVERSE_ALARM_ABSENT')):
                with self.assertRaises(RU.Refused) as e:
                    RU.alarm_check(reg, **kw)
                self.assertEqual(e.exception.code, code)
        with self.assertRaises(SystemExit):                                                      # --alarm-id is required
            I3.parser().parse_args(['--first', '20990101', '--last', '20990101', '--research-window', '20990101:20990101', '--out', 'x',
                                    '--lab-root', 'L', '--research-root', 'R', '--delay-s', '1', '--ledger-ask', 'PREREG_A'])
        real = RU.read_registry(os.path.join(FO, 'team', 'RESEARCH', 'LIBRARY', 'alarm_library', 'ALARM_REGISTRY_V1.tsv'))   # the real one reads
        self.assertTrue(real and all(k.startswith('ALM_') for k in real))

    # ------------------------------------------------------------------ 18 F6: one copy of the shared rules
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_18_one_shared_contract(self):
        RU = V3.RU
        import alarm_contract_v1 as C
        lib = os.path.join(FO, 'team', 'RESEARCH', 'LIBRARY', 'alarm_library')
        AC2 = load(os.path.join(lib, 'alarm_core_v1_2.py'), 'alarm_core_v1_2_t'); AC1 = load(os.path.join(lib, 'alarm_core_v1_1.py'), 'alarm_core_v1_1_t')
        self.assertIs(RU.C, C); self.assertIs(AC2.C, C)                                          # both users import the one module
        src = open(os.path.join(HERE, 'i2g_rules_v1_2.py')).read()
        for dup in ('busy_sorted[i] <= cand_t', 'hit_s = lo[j] <= sl', 'lo[j] < L', 't - prev <= gap_s'):
            self.assertNotIn(dup, src)                                                           # no second copy left in the grading rules
        rng = np.random.default_rng(5)
        for _ in range(300):                                                                     # the three agree on planted cases
            fires = sorted(set(int(x) for x in rng.integers(0, 40000, 6))); t = int(rng.integers(0, 40000))
            want = not C.asof_busy(t, fires)
            self.assertEqual(AC1.control_eligible(t, fires), want); self.assertEqual(AC2.control_eligible(t, fires), want)
            self.assertEqual(RU.asof_flag(t, fires) == '', want); self.assertEqual(bool(RU.asof_mask([t], fires)[0]), want)
            side = int(rng.choice([-1, 1])); tg, sp = (102.0, 98.0) if side > 0 else (98.0, 102.0)
            bins = [(i, float(x), float(x) - float(y)) for i, (x, y) in enumerate(zip(rng.uniform(99, 103, 4), rng.uniform(0, 4, 4)))]
            r1 = AC1.first_touch(bins, side, tg, sp); r2 = AC2.first_touch(bins, side, tg, sp)
            self.assertEqual(r1, r2)
            lim = float(rng.uniform(99, 101))
            self.assertEqual(AC1.passive_fill(bins, side, lim, -1), AC2.passive_fill(bins, side, lim, -1))
            ts = sorted(int(x) for x in rng.integers(0, 30000, 12))
            c1 = AC1.Clusters([(str(i), 'A', x) for i, x in enumerate(ts)], 'u'); c2 = AC2.Clusters([(str(i), 'A', x) for i, x in enumerate(ts)], 'u')
            self.assertEqual((c1.cid, c1.flags, c1.weight), (c2.cid, c2.flags, c2.weight))

    # ------------------------------------------------------------------ 19 chain-split sensitivity (OX-DATA point 7)
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_19_split_chains_merge_back_for_the_sensitivity(self):
        RU = V3.RU
        U = RU.Universe(RU.build_clusters(self._fires()), 'u')
        m = U.merged_clusters('X')
        split = sorted({r[5] for r in U.rows if r[2] >= 100_000})
        self.assertEqual(len(split), 2)
        self.assertEqual({m[c] for c in split}, {min(split, key=lambda c: int(c.split(':')[1]))})
        self.assertEqual(m['X:1000'], 'X:1000')


    # ------------------------------------------------------------------ 20 the event list reader keeps both sides of one second
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_20_event_list_reader_keeps_a_buy_and_a_sell_in_one_second(self):
        import idea_to_grade_v3_2_rel1 as I3
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'E.tsv')
            with open(p, 'w') as f:
                f.write('coin\tt\tside\nAAA\t1760000000\t1\nAAA\t1760000000\t-1\nBBB\t1760000000\t1\n')
            ev = I3.load_events_v3(p)
            self.assertEqual(sorted(zip(ev['coin'], ev['t'].tolist(), ev['side'].tolist())),
                             [('AAA', 1760000000, -1), ('AAA', 1760000000, 1), ('BBB', 1760000000, 1)])
            with open(p, 'a') as f:
                f.write('aaa\t1760000000\t1\n')                                                # same coin (case), second and side
            with self.assertRaises(ValueError):
                I3.load_events_v3(p)
            for bad in ('AAA\t1760000000.5\t1\n', 'AAA\t1760000001\t2\n', 'A-A\t1760000001\t1\n'):   # the V2 row checks still hold
                with open(p, 'w') as f:
                    f.write('coin\tt\tside\n' + bad)
                with self.assertRaises(ValueError):
                    I3.load_events_v3(p)

    # ------------------------------------------------------------------ 21 a coin without a cost of record is graded before cost only
    @unittest.skipIf(IMPL == 'v2', 'V3.1 rule check')
    def test_21_no_cost_coin_graded_gross_only(self):
        import idea_to_grade_v3_2_rel1 as I3, i2g_grade3_v3_2 as G3
        RU = V3.RU
        nc, bp = I3.cost_split(['AAA', 'ZZZ'], {'AAA': (10.0, 9.0)})
        self.assertEqual(nc, ['ZZZ']); self.assertEqual(bp['AAA'], 10.0); self.assertTrue(np.isnan(bp['ZZZ']))
        names = RU.value_names(); col = {c: i for i, c in enumerate(names)}; V = np.full((4, len(names)), np.nan)
        V[:, col['ret_10s']] = [1.0, 1.0, 3.0, 3.0]; V[:, col['tk_filled']] = 1
        parents = [{'coin': c, 'day': '20990101', 'row_ids': {'FOLLOW': 2 * i, 'FADE': 2 * i + 1}} for i, c in enumerate(['AAA', 'ZZZ'])]
        empty = {d: [[] for _ in parents] for d in ('FOLLOW', 'FADE')}
        legs = {'HONEST': {c: RU.cost_legs(bp[c], 0.032, 1.5) for c in ('AAA', 'ZZZ')}}
        rows = G3.grade(parents, names, V, ['AAA', 'AAA', 'ZZZ', 'ZZZ'], empty, empty, empty, [1.0, 1.0], ['a', 'b'], legs)
        get = {(r[0], r[1], r[2], r[4], r[5]): r for r in rows}
        self.assertEqual(get[('ALL', 'FOLLOW', 'ret_10s', 'GROSS', 'PARENT')][9], 2)            # both parents before cost
        net = get[('ALL', 'FOLLOW', 'ret_10s', 'HONEST', 'PARENT')]
        self.assertEqual(net[9], 1); self.assertAlmostEqual(net[6], 1.0 - 2 * RU.cost_legs(10.0, 0.032, 1.5)[0])   # the NO_COST parent is out
        g = np.arange(10) * 60.0
        self.assertEqual(RU.tough_pick('P', 7, 1, 1.0, 0.3, float('nan'), g, np.ones(10), np.full(10, 0.3), np.ones(10, bool))[1], 'TOUGH_NO_COST')
        V[:, col['rs_filled']] = [1.0, 1.0, 0.0, 0.0]                                          # the NO_COST parent's resting entry missed
        rows = G3.grade(parents, names, V, ['AAA', 'AAA', 'ZZZ', 'ZZZ'], empty, empty, empty, [1.0, 1.0], ['a', 'b'], legs)
        get = {(r[0], r[1], r[2], r[3], r[4], r[5]): r for r in rows}
        rt = [k for k in get if k[0] == 'ALL' and k[1] == 'FOLLOW' and k[3] == 'RT' and k[5] == 'FILL_SHARE']
        self.assertTrue(rt)
        for k in rt:                                                                            # V3.2 blocker 1: net fill share
            r = get[k]
            if k[4] == 'GROSS':
                self.assertEqual((r[9], r[6]), (2, 0.5))                                         # both parents before cost
            else:
                self.assertEqual((r[9], r[6]), (1, 1.0))                                         # the NO_COST parent is out

    def test_22_a_stale_decision_price_is_no_price(self):
        RU = V3.RU
        t0 = 1_762_097_500
        tl = np.asarray([(t0 + 67) * US + 693000, (t0 + 152) * US + 219000], np.int64)        # 75.527 s before the decision, then 9 s after
        px = np.asarray([1.547, 1.540]); hi = np.asarray([1.547, 1.548]); lo = np.asarray([1.547, 1.530])
        dec = (t0 + 143) * US + 220000
        self.assertEqual(RU.passive_entry(tl, px, lo, hi, dec, 1)[0], 'NO_PRICE')               # V3.2 blocker 2 (was FILLED)
        self.assertEqual(RU.passive_entry(tl, px, lo, hi, dec, -1)[0], 'NO_PRICE')
        st, j, t, L = RU.passive_entry(tl, px, lo, hi, int(tl[0]) + 60 * US, 1)                   # exactly 60 s old: still known
        self.assertEqual((st, L), ('FILLED', 1.547))                                            # the next bin trades through
        st, j, t, L = RU.passive_entry(tl, px, lo, hi, int(tl[0]) + 60 * US + 1, 1)               # one microsecond more: unknown
        self.assertEqual(st, 'NO_PRICE'); self.assertTrue(np.isnan(L))
        names = RU.value_names(); col = {c: i for i, c in enumerate(names)}
        v = RU.path_values(tl, px, hi, lo, ('NO_FILL', None, None, None), dec, 1, int(tl[-1]), 1.0, 0.3, 0.2)
        self.assertTrue(np.isnan(v[col['rs_filled']])); self.assertTrue(np.isnan(v[col['rs_wait_s']]))   # out of the fill share

if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=2).result
    sys.exit(0 if r.wasSuccessful() else 1)
