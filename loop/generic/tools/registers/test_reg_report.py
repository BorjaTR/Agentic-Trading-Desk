#!/usr/bin/env python3
"""test_reg_report.py (SCOUT 2026-11-08, C130): the REPORT block of drills_v2/REPORT_TEMPLATE_V1.md is parsed and loaded with none lost;
bad lines are refused and named; nothing is written on a refusal. Temp registers on SCRATCH_DISK only.  python3 -B test_reg_report.py"""
import importlib.util, os, shutil, tempfile, unittest, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
sp = importlib.util.spec_from_file_location('reg', os.path.join(HERE, 'reg.py')); reg = importlib.util.module_from_spec(sp); sp.loader.exec_module(reg)
GOOD = '''some answer text
## REPORT
```
MESSY | two_readings | lean_v1/HUNTER_RULES_V2.md | "R1 under 334 graded waves" | cut 10 pct of 334 | cut 10 pct of R1's waves
MESSY | stale | ASSESSOR_STEP_V3.md | "pipe_r2" | the old folder | pipe_p2
WASTE | 4 | a COUNT stopped NO FIRE ROWS | the data-trap line
PROPOSE | P10 | lean_v1/HUNTER_RULES_V2.md | count fires removed beside waves | R3 gain +2 | H06 round 4 | L10 STEP_06 7fab93c521b76d43
```
'''
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE); self.old = reg.HERE; reg.HERE = self.t
        self.env = {k: os.environ.get(k) for k in ('LL_REGISTERS', 'LL_SEAT_ROOT')}; os.environ['LL_REGISTERS'] = self.t; os.environ['LL_SEAT_ROOT'] = self.t   # C218: own temp registers, never the seat's live ones
    def tearDown(self):
        reg.HERE = self.old; shutil.rmtree(self.t)
        for k, v in self.env.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
    def run_import(self, text, src):
        p = os.path.join(self.t, 'r.md'); open(p, 'w').write(text); buf = io.StringIO()
        with contextlib.redirect_stdout(buf): rc = reg.import_report(p, src)
        return rc, buf.getvalue()
    def test_good_report_loads_every_line(self):
        rc, out = self.run_import(GOOD, 'AG1'); self.assertEqual(rc, 0, out); self.assertIn('messy 2, waste 1, propose 1', out)
        m = reg.rows('mess'); self.assertEqual([r['kind'] for r in m], ['two_readings', 'stale', 'waste'])
        self.assertEqual(m[0]['line_quoted'], 'R1 under 334 graded waves'); self.assertEqual(m[2]['line_quoted'], '4 min: a COUNT stopped NO FIRE ROWS')
        p = reg.rows('proposal'); self.assertEqual(len(p), 1); self.assertEqual(p[0]['part_id'], 'P10'); self.assertEqual(p[0]['status'], 'PROPOSED')
        rc, out = self.run_import(GOOD, 'AG1'); self.assertEqual(rc, 2); self.assertIn('ALREADY_IMPORTED', out)
    def test_tab_inside_a_field_loads_whole(self):        # C137
        rc, out = self.run_import('## REPORT\nMESSY | stale | f.tsv | "a\tb" | x | y\nNONE | WASTE\nNONE | PROPOSE\n', 'AG7'); self.assertEqual(rc, 0, out)
        self.assertEqual(reg.rows('mess')[0]['line_quoted'], 'a b')
    def test_none_lines(self):
        rc, out = self.run_import('## REPORT\nNONE | MESSY\nNONE | WASTE\nNONE | PROPOSE\n', 'AG2'); self.assertEqual(rc, 0, out); self.assertEqual(reg.rows('mess'), [])
    def test_refusals_write_nothing(self):
        bad = GOOD.replace('WASTE | 4 |', 'WASTE | four |').replace('| stale |', '| oops |')
        rc, out = self.run_import(bad, 'AG3'); self.assertEqual(rc, 2); self.assertIn('minutes', out); self.assertIn("kind 'oops'", out); self.assertEqual(reg.rows('mess'), [])
        rc, out = self.run_import('## REPORT\nNONE | MESSY\nNONE | WASTE\n', 'AG4'); self.assertIn('list PROPOSE missing', out)
        rc, out = self.run_import('no block here', 'AG5'); self.assertIn('NO_REPORT_BLOCK', out)
        rc, out = self.run_import('## REPORT\nMESSY | stale | f | "q" | a\nNONE | WASTE\nNONE | PROPOSE\n', 'AG6'); self.assertIn('needs 6 fields, has 5', out)
if __name__ == '__main__':
    unittest.main(verbosity=1)
