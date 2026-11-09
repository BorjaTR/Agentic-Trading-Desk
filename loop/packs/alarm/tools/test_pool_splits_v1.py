#!/usr/bin/env python3
"""test_pool_splits_v1.py (RC2, C215): two planted memory runs, one control, hand-computed pooled numbers; temp only under LL_TEST_TMP."""
import importlib.util, math, os, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
sp = importlib.util.spec_from_file_location('ps', os.path.join(HERE, 'pool_splits_v1.py')); ps = importlib.util.module_from_spec(sp); sp.loader.exec_module(ps)
H = 'horizon\tstate\tstatus\tlead\tse\twaves\trule\n'
def split(lo, hi):
    return (H + '15m\tALL\tOK\t9\t1\t500\tall\n15m\tS1\tOK\t%s\t1\t100\tlow\n15m\tS2\tOK\t%s\t1\t120\thigh\n'
            '1h\tS1\tOK\t0\t1\t100\tlow\n1h\tS2\tOK\t50\t1\t120\thigh\n') % (lo, hi)
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
        for run, lo, hi in (('L01', 1, 5), ('L02', 2, 4), ('C01', 0, 40)):
            d = os.path.join(self.t, run, 'split_a'); os.makedirs(d); open(os.path.join(d, 'STATE_SPLIT_x_CTX.FOO.tsv'), 'w').write(split(lo, hi))
    def tearDown(self): shutil.rmtree(self.t)
    def test_pooled_by_hand(self):
        out = os.path.join(self.t, 'out.tsv'); self.assertEqual(ps.main(['--runs', self.t, '--out', out]), 0)
        rows = [l.rstrip('\n').split('\t') for l in open(out)]; h, r = rows[0], dict(zip(rows[0], rows[1]))
        self.assertEqual(len(rows), 2)
        # gaps 4 and 2, each v = 1 + 1 = 2 -> pooled gap 3, se sqrt(1 / (1/2 + 1/2)) = 1, t 3, t_adj 3 / sqrt(1.5); control C01 never read
        self.assertEqual((r['reading'], r['runs'], r['k']), ('FOO', 'L01,L02', '2'))
        self.assertEqual((r['pooled_gap_hi_minus_lo'], r['pooled_se'], r['pooled_t']), ('+3.00', '1.00', '+3.00'))
        self.assertEqual(r['t_dependence_adjusted'], '%+.2f' % (3 / math.sqrt(1.5))); self.assertEqual(r['sign_agree'], '2/2')
    def test_other_horizon(self):
        out = os.path.join(self.t, 'o1h.tsv'); ps.main(['--runs', self.t, '--out', out, '--horizon', '1h'])
        r = dict(zip(*[l.rstrip('\n').split('\t') for l in open(out)][:2])); self.assertEqual(r['pooled_gap_hi_minus_lo'], '+50.00')
if __name__ == '__main__':
    unittest.main(verbosity=1)
