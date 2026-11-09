#!/usr/bin/env python3
"""test_agreement_v1.py (RC2 C215; source since C218): small synthetic scorer files; temp only under LL_TEST_TMP.  python3 -B test_agreement_v1.py"""
import contextlib, importlib.util, io, os, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
sp = importlib.util.spec_from_file_location('ag', os.path.join(HERE, 'agreement_v1.py')); ag = importlib.util.module_from_spec(sp); sp.loader.exec_module(ag)
def tsv(rows): return 'run\titem\tpoints\tevidence\n' + ''.join('%s\t%s\t%s\te\n' % r for r in rows)
class T(unittest.TestCase):
    def setUp(self): os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
    def tearDown(self): shutil.rmtree(self.t)
    def w(self, name, rows):
        p = os.path.join(self.t, name); open(p, 'w').write(tsv(rows)); return p
    def run_main(self, args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = ag.main(args)
        return rc, buf.getvalue()
    def test_self_test(self):
        self.assertEqual(self.run_main(['--self-test'])[0], 0)
    def test_identical_scorers_reliable(self):
        rows = [('I01', 'P1', 2), ('I01', 'P2', 0), ('I02', 'P1', 1), ('I02', 'P2', 2), ('I01', 'TOTAL', 2), ('I02', 'MESSY', 'x')]
        rc, out = self.run_main([self.w('a.tsv', rows), self.w('b.tsv', rows)])
        self.assertEqual(rc, 0); self.assertIn('units 4 | exact 1.00', out); self.assertIn('alpha ordinal 1.000', out); self.assertIn('RELIABLE', out)
    def test_disagreement_goes_to_adjudication(self):
        a = self.w('a.tsv', [('I01', 'P1', 0), ('I01', 'P2', 2), ('I02', 'P1', 1)]); b = self.w('b.tsv', [('I01', 'P1', 2), ('I01', 'P2', 2), ('I02', 'P1', 1)])
        rc, out = self.run_main([a, b]); self.assertEqual(rc, 0); self.assertIn('ADJUDICATE I01|P1', out); self.assertIn('exact 0.67', out)
    def test_no_common_units(self):
        rc, out = self.run_main([self.w('a.tsv', [('I01', 'P1', 1)]), self.w('b.tsv', [('I02', 'P1', 1)])]); self.assertEqual(rc, 2); self.assertIn('NO COMMON UNITS', out)
    def test_one_file_refused(self):
        with self.assertRaises(SystemExit): ag.main([self.w('a.tsv', [('I01', 'P1', 1)])])
    def test_one_value_not_computable(self):   # C218: was alpha 1.000 RELIABLE
        rows = [('I01', 'P1', 2), ('I02', 'P1', 2)]
        rc, out = self.run_main([self.w('a.tsv', rows), self.w('b.tsv', rows)])
        self.assertEqual(rc, 0); self.assertIn('NOT_COMPUTABLE', out); self.assertNotIn('RELIABLE', out); self.assertIn('alpha ordinal n/a (one value)', out)
if __name__ == '__main__':
    unittest.main(verbosity=1)
