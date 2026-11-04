#!/usr/bin/env python3
"""test_t_by_month_v1.py (SCOUT, 2 Nov 2026, V1_18_FIXES; RESULTS_R5 item 6): planted files for t_by_month_v1. Temp files only.
Expected numbers are worked by hand below, never by the tool. TOOL_UNDER_TEST names the tool file."""
import importlib.util, math, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ.get('TOOL_UNDER_TEST') or os.path.join(HERE, '..', 'tools', 't_by_month_v1.py')
spec = importlib.util.spec_from_file_location('tbm', TOOL); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
HEAD = 'kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc\tFADE 15m\tFADE 1h\tFOLLOW 15m\tFOLLOW 1h\n'


def pf(kind, coin, t, day, month, wave, w, a15, o15, a1='0', o1='0'):
    return '\t'.join([kind, coin, str(t), day, month, '00', '1', str(wave), str(w), '1', '0', a15, a1, o15, o1]) + '\n'


def run(*a):
    p = subprocess.run([sys.executable, '-B', TOOL] + list(a), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def rows(out):
    L = [l.split('\t') for l in out.split('\n') if l and not l.startswith('#')]
    return [dict(zip(L[0], x)) for x in L[1:]]


class Hand(unittest.TestCase):
    def test_month_t_day_clustered_by_hand(self):
        # 3 waves, 2 days: 1, 3 on day a, 5 on day b. lead 3; SE^2 = 2/1 * ((-2+0)^2 + 2^2) / 9 = 16/9
        lead, se, t, days = M.month_stats([(1.0, 'a'), (3.0, 'a'), (5.0, 'b')])
        self.assertAlmostEqual(lead, 3.0); self.assertAlmostEqual(se, 4.0 / 3); self.assertAlmostEqual(t, 2.25); self.assertEqual(days, 2)

    def test_zero_spread_has_no_t(self):
        self.assertTrue(math.isnan(M.month_stats([(1.0, 'a'), (1.0, 'b')])[2]))

    def test_one_day_has_no_t(self):
        lead, se, t, days = M.month_stats([(1.0, 'a'), (3.0, 'a')])
        self.assertAlmostEqual(lead, 2.0); self.assertTrue(math.isnan(t))


class Files(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.p = lambda n: os.path.join(self.d.name, n)

    def tearDown(self):
        self.d.cleanup()

    def w(self, n, text):
        with open(self.p(n), 'w') as f:
            f.write(text)
        return self.p(n)

    def test_wave_leads_split_by_month(self):
        f = self.w('wl.tsv', 'wave\tday\tlead\n0\t20250912\t1\n1\t20250912\t3\n2\t20250913\t5\n3\t20251001\t10\n4\t20251002\t-10\n')
        rc, out, err = run('--wave-leads', f)
        self.assertEqual(rc, 0, err); r = {x['month']: x for x in rows(out)}
        self.assertAlmostEqual(float(r['2509']['t']), 2.25, places=2); self.assertEqual(r['2509']['waves'], '3')
        self.assertAlmostEqual(float(r['2510']['lead']), 0.0); self.assertEqual(r['2510']['days'], '2')
        self.assertEqual(r['ALL']['waves'], '5')

    def test_day_after_last_dropped_and_counted(self):
        f = self.w('wl.tsv', 'wave\tday\tlead\n0\t20251231\t1\n1\t20251230\t3\n2\t20260101\t99\n')
        rc, out, err = run('--wave-leads', f)
        self.assertEqual(rc, 0, err); self.assertNotIn('2601', out); self.assertIn('dropped after 20251231: 1', out)
        self.assertEqual({x['month']: x for x in rows(out)}['2512']['waves'], '2')

    def test_perfire_lead_by_hand_and_lean(self):
        t = HEAD + pf('R', 'X', 1, '20250912', '2509', -1, 1, '1', '0') + pf('R', 'X', 2, '20250912', '2509', -1, 3, '0', '1')
        t += pf('A', 'A', 10, '20250912', '2509', 0, 1, '1', '0') + pf('A', 'B', 11, '20250912', '2509', 0, 1, '0', 'nan') + pf('A', 'A', 20, '20250913', '2509', 1, 1, '0', '1')
        f = self.w('p.tsv', t)
        rc, out, err = run('--perfire', f, '--lean', 'FADE', '--horizon', '15m')
        self.assertEqual(rc, 0, err); r = {x['month']: x for x in rows(out)}['2509']
        self.assertAlmostEqual(float(r['lead']), 50.0); self.assertEqual(r['waves'], '2')   # +150 and -50, month random -0.5
        rc, out, err = run('--perfire', f, '--lean', 'FOLLOW', '--horizon', '15m')
        self.assertAlmostEqual(float({x['month']: x for x in rows(out)}['2509']['lead']), -50.0)
        self.assertIn('approx', out)

    def test_edges_keep_only_fires_with_a_drawn_moment(self):
        t = HEAD + pf('R', 'X', 1, '20250912', '2509', -1, 1, '1', '0')
        t += pf('A', 'A', 10, '20250912', '2509', 0, 1, '1', '0') + pf('A', 'B', 5000, '20250913', '2509', 1, 1, '1', '0') + pf('A', 'C', 9000, '20250914', '2509', 2, 1, '1', '0')
        f = self.w('p.tsv', t)
        e = self.w('e.tsv', 'fid\tcoin\tparent_t\tcand_t\tside\tweight\tdraw_index\town\nA_10\tA\t10\t99\t1\t1\t0\t\nC_9000\tC\t9000\t99\t1\t1\t0\t1\n')
        rc, out, err = run('--perfire', f, '--lean', 'FADE', '--horizon', '15m', '--edges', e)
        self.assertEqual(rc, 0, err); self.assertEqual({x['month']: x for x in rows(out)}['2509']['waves'], '1')   # no edge, own edge: out

    def test_real_shown_beside_and_alone_gives_no_t(self):
        r = self.w('REAL.tsv', '# c\nhorizon\twaves\tdays\tlead\tse\tt\tlead_2509\twaves_2509\tcounted_2509\tlead_2601\twaves_2601\tcounted_2601\n15m\t9\t5\t1.5\t1\t1.5\t8.8\t124\tyes\t7\t40\tyes\n')
        f = self.w('wl.tsv', 'wave\tday\thorizon\tlead\n0\t20250912\t15m\t1\n1\t20250913\t15m\t3\n2\t20250913\t1h\t500\n')
        rc, out, err = run('--wave-leads', f, '--real', r)
        self.assertEqual(rc, 0, err); x = {y['month']: y for y in rows(out) if y['horizon'] == '15m'}
        self.assertEqual(x['2509']['real_lead'], '8.8'); self.assertEqual(x['2509']['real_waves'], '124'); self.assertEqual(x['2509']['waves'], '2')
        self.assertAlmostEqual(float(x['2509']['lead']), 2.0)
        self.assertNotIn('2601', out)   # a month after --last is never shown
        self.assertIn('15m pooled t here', out); self.assertIn('REAL 1.5:', out)
        rc, out, err = run('--real', r)
        self.assertEqual(rc, 0, err); y = rows(out)[0]
        self.assertEqual((y['month'], y['t'], y['real_lead']), ('2509', '-', '8.8')); self.assertIn('no t', out)

    def test_refusals(self):
        self.assertEqual(run()[0], 2)
        f = self.w('bad.tsv', 'wave\tlead\n0\t1\n')
        self.assertEqual(run('--wave-leads', f)[0], 2)
        g = self.w('nan.tsv', 'wave\tday\tlead\n0\t20250912\tx\n')
        self.assertEqual(run('--wave-leads', g)[0], 2)
        h = self.w('p.tsv', HEAD)
        self.assertEqual(run('--perfire', h)[0], 2)   # no lean
        self.assertEqual(run('--perfire', h, '--lean', 'BOTH')[0], 2)
        self.assertEqual(run('--wave-leads', self.p('none.tsv'))[0], 2)


if __name__ == '__main__':
    unittest.main()
