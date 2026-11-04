#!/usr/bin/env python3
"""test_wave_gap_v1.py (SCOUT, 2 Nov 2026, V1_18_FIXES; RESULTS_R5 item 5): a planted GRADE work folder. TOOL_UNDER_TEST names the tool."""
import importlib.util, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ.get('TOOL_UNDER_TEST') or os.path.join(HERE, 'wave_gap_v1.py')
HEAD = 'kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc\tFADE 15m\tFADE 1h\tFOLLOW 15m\tFOLLOW 1h\n'


def a(coin, t, day, wave, o='1'):
    return '\t'.join(['A', coin, str(t), day, day[2:6], '00', '1', str(wave), '1', '1', '0', o, o, o, o]) + '\n'


class Gap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); w = self.w = self.d.name; os.makedirs(os.path.join(w, 'gradeL_V1_v1', 'matches'))
        F = [('K', 1000, '20250912', 0, 'MATCHED', 'e', '1'), ('U', 9000, '20250912', 1, 'COMPARISON_UNAVAILABLE', '', '1'),
             ('O', 90000, '20251001', 2, 'MATCHED', 'o', '1'), ('N', 190000, '20251002', 3, 'NO_ELIGIBLE', '', '1'),
             ('Q', 290000, '20251003', 4, 'MATCHED', 'e', 'nan'), ('M', 390000, '20251004', 5, 'COMPARISON_UNAVAILABLE', '', '1'),
             ('M2', 390010, '20251004', 5, 'MATCHED', 'e', '1')]
        with open(os.path.join(w, 'PERFIRE_V1.tsv'), 'w') as f:
            f.write(HEAD + 'R\tX\t1\t20250912\t2509\t00\t1\t-1\t1\t1\t0\t1\t1\t1\t1\n' + ''.join(a(c, t, d, wv, o) for c, t, d, wv, st, e, o in F))
        with open(os.path.join(w, 'gradeL_V1_v1', 'matches', 'CENSUS.tsv'), 'w') as f:
            f.write('fid\tcoin\tt\tside\tmatches\tstatus\tcov0\n' + ''.join('%s_%d\t%s\t%d.0\t1\t0\t%s\tnan\n' % (c, t, c, t, st) for c, t, d, wv, st, e, o in F))
        with open(os.path.join(w, 'gradeL_V1_v1', 'matches', 'EDGES.tsv'), 'w') as f:
            f.write('fid\tcoin\tparent_t\tcand_t\tside\tweight\tdraw_index\town\n')
            for c, t, d, wv, st, e, o in F:
                if e:
                    f.write('%s_%d\t%s\t%d.0\t5.0\t1\t1\t0\t%s\n' % (c, t, c, t, '1' if e == 'o' else ''))
        self.real = os.path.join(w, 'REAL_V1.tsv')
        self.wr('1')

    def wr(self, w2510):
        with open(self.real, 'w') as f:
            f.write('# c\nhorizon\twaves\tlead_2509\twaves_2509\tcounted_2509\tlead_2510\twaves_2510\tcounted_2510\n15m\t3\t1\t1\tyes\t1\t%s\tyes\n' % w2510)

    def tearDown(self):
        self.d.cleanup()

    def run_(self, *x):
        p = subprocess.run([sys.executable, '-B', TOOL, self.w, 'V1', '--real', self.real] + list(x), capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def line(self, out, k):
        return [l for l in out.split('\n') if l.startswith(k)][0]

    def test_counts_by_hand(self):
        rc, out, err = self.run_()
        self.assertEqual(rc, 0, err + out)
        self.assertIn('WAVES count 6 lead 2 dropped 4', self.line(out, 'WAVES'))
        self.assertIn('2509 count 2 lead 1', out); self.assertIn('2510 count 4 lead 1', out)

    def test_reasons_by_hand(self):
        rc, out, err = self.run_()
        r = self.line(out, 'REASONS')
        for t in ('COMPARISON_UNAVAILABLE 1', 'ONLY_OWN_EDGES 1', 'NO_ELIGIBLE 1', 'NO_OUTCOME 1'):
            self.assertIn(t, r)

    def test_mismatch_with_real_exits_3(self):
        self.wr('9')
        rc, out, err = self.run_()
        self.assertEqual(rc, 3); self.assertIn('NOT EQUAL', out)

    def test_equal_said_when_equal(self):
        self.wr('1')
        rc, out, err = self.run_()
        self.assertEqual(rc, 0, out); self.assertIn('EQUAL', self.line(out, 'REAL'))

    def test_missing_file_refused(self):
        p = subprocess.run([sys.executable, '-B', TOOL, self.w, 'V9', '--real', self.real], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == '__main__':
    unittest.main()
