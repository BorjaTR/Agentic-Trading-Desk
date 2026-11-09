#!/usr/bin/env python3
"""test_blind_kit_v1.py (SCOUT 2026-11-08, C97): the scorer task names the key's element ids, so two scorers write the same rows.
C218 (B1) gold rows need a total from every scorer; C223 (N1) no gold row fails score, make refuses no or bad --gold.
Temp files on SCRATCH_DISK only.  python3 -B test_blind_kit_v1.py"""
import contextlib, csv, importlib.util, io, os, shutil, tempfile, unittest, types
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
sp = importlib.util.spec_from_file_location('bk', os.path.join(HERE, 'blind_kit_v1.py')); bk = importlib.util.module_from_spec(sp); sp.loader.exec_module(bk)
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
    def tearDown(self):
        shutil.rmtree(self.t)
    def w(self, n, txt):
        p = os.path.join(self.t, n); open(p, 'w').write(txt); return p
    def test_elements_from_key(self):
        k = self.w('KEY.md', '# KEY\nMOVE (1): a\nSPAN (2): b\nnot an element (3)\nMOVE (1): repeated\n')
        self.assertEqual(bk.key_elements(k), ['MOVE', 'SPAN'])
    def test_task_names_elements(self):
        k = self.w('KEY.md', '# KEY\nI1 trap: x\n'); i = self.w('a.md', '# t\nanswer\n'); g = self.w('g.md', '# g\ngold\n')
        kit = os.path.join(self.t, 'KIT')
        bk.make(types.SimpleNamespace(kit=kit, key=k, rubric=None, item=[i], gold=[g + '=3'], elements='I1,I2,I3'))
        task = open(os.path.join(kit, 'SCORER_TASK.md')).read()
        self.assertIn('Use exactly these element ids, one row each: I1, I2, I3.', task)
        self.assertIn('REPORT_TEMPLATE_V1.md', task)   # C130
    def kit(self):   # C218 B1: one item, one gold known 5
        k = self.w('KEY.md', '# KEY\nI1 trap: x\n'); i = self.w('a.md', '# t\nanswer\n'); g = self.w('g.md', '# g\ngold\n')
        kit = os.path.join(self.t, 'KIT'); bk.make(types.SimpleNamespace(kit=kit, key=k, rubric=None, item=[i], gold=[g + '=5'], elements='I1'))
        return kit, list(csv.DictReader(open(kit + '_MAP.tsv'), delimiter='\t'))
    def score(self, kit, scorers):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = bk.score(types.SimpleNamespace(kit=kit, scorers=scorers, gold_tol=1))
        return rc, buf.getvalue()
    def tsv(self, name, m, totals):
        return self.w(name, 'run\titem\tpoints\n' + ''.join('%s\tI1\t1\n' % r['blind_id'] + ('%s\tTOTAL\t%s\n' % (r['blind_id'], '5' if r['kind'] == 'gold' else '2') if r['kind'] in totals else '') for r in m))
    def test_no_totals_fail_gold_check(self):   # C218 B1: was GOLD ... scored {} -> OK and GOLD_CHECK PASS, exit 0
        kit, m = self.kit(); rc, out = self.score(kit, [self.tsv('A.tsv', m, ()), self.tsv('B.tsv', m, ())])
        self.assertEqual(rc, 3, out); self.assertIn('NO_SCORES', out); self.assertIn('GOLD_CHECK FAIL', out)
    def test_one_scorer_without_gold_total_fails(self):
        kit, m = self.kit(); kinds = {r['kind'] for r in m}
        rc, out = self.score(kit, [self.tsv('A.tsv', m, kinds), self.tsv('B.tsv', m, kinds - {'gold'})])
        self.assertEqual(rc, 3, out); self.assertIn('NO_SCORES 1 of 2 scorers', out)
    def test_all_totals_pass(self):
        kit, m = self.kit(); kinds = {r['kind'] for r in m}
        rc, out = self.score(kit, [self.tsv('A.tsv', m, kinds), self.tsv('B.tsv', m, kinds)])
        self.assertEqual(rc, 0, out); self.assertIn('GOLD_CHECK PASS', out)
    def test_no_gold_row_fails(self):   # C223 N1 (review RC3): a map with one item and no gold, two scorers I01 TOTAL 2: was GOLD_CHECK PASS, exit 0
        d = os.path.join(self.t, 'KIT'); os.makedirs(d)
        open(d + '_MAP.tsv', 'w').write('blind_id\tsource\tkind\tknown_total\nI01\tout1.md\titem\t\n')
        sc = [self.w(n, 'run\titem\tpoints\nI01\tI1\t2\nI01\tTOTAL\t2\n') for n in ('A.tsv', 'B.tsv')]
        rc, out = self.score(d, sc)
        self.assertEqual(rc, 3, out); self.assertIn('GOLD NONE', out); self.assertIn('GOLD_CHECK FAIL 1', out)
    def mk(self, gold):
        k = self.w('KEY.md', '# KEY\nI1 trap: x\n'); i = self.w('a.md', '# t\nanswer\n'); kit = os.path.join(self.t, 'KIT')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = bk.make(types.SimpleNamespace(kit=kit, key=k, rubric=None, item=[i], gold=gold, elements='I1'))
        return rc, buf.getvalue(), os.path.exists(kit + '_MAP.tsv')
    def test_make_refuses_no_gold(self):   # C223 N1: make accepted no --gold and wrote a kit
        rc, out, made = self.mk([])
        self.assertEqual(rc, 2, out); self.assertIn('REFUSED NO_GOLD', out); self.assertFalse(made)
    def test_make_refuses_bad_gold(self):   # C223 N1: a --gold without =<known total> gave an IndexError traceback
        g = self.w('g.md', '# g\ngold\n')
        for bad in (g, g + '=', g + '=x'):
            rc, out, made = self.mk([bad])
            self.assertEqual(rc, 2, out); self.assertIn('REFUSED BAD_GOLD', out); self.assertFalse(made)
if __name__ == '__main__':
    unittest.main(verbosity=1)
