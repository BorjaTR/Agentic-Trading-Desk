#!/usr/bin/env python3
"""test_reg_baseline.py (SCOUT 2026-11-08, C218, review B6): a new seat reaches reg.py ledger-check PASS. The alarm seat's PARTS.tsv
flags every file in a new seat; the seat's own PARTS.tsv plus `reg.py baseline` gives PASS; a missing file refuses and writes nothing;
{NAME} cells resolve from env LL_<NAME>. Temp only under LL_TEST_TMP.  python3 -B test_reg_baseline.py"""
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); REG = os.path.join(HERE, 'reg.py')
BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/tmp_SCOUT')
HDR = 'part_id\tname\tcategory\tkind\tfiles\tmeasure\tdrills\tpass_bar\n'
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(prefix='regbase_', dir=BASE)
        self.reg = os.path.join(self.t, 'registers'); self.pack = os.path.join(self.t, 'pack'); os.makedirs(self.reg); os.makedirs(self.pack)
        open(os.path.join(self.pack, 'RULES.md'), 'w').write('rules\n'); open(os.path.join(self.t, 'NOW.md'), 'w').write('now\n')
        self.env = dict(os.environ, LL_REGISTERS=self.reg, LL_SEAT_ROOT=self.t, LL_PACK=self.pack)
    def tearDown(self):
        shutil.rmtree(self.t)
    def parts(self, files):
        open(os.path.join(self.reg, 'PARTS.tsv'), 'w').write(HDR + ''.join('P%02d\tn\tc\tk\t%s\tm\tnone\tb\n' % (i + 1, f) for i, f in enumerate(files)))
    def run_reg(self, *a):
        p = subprocess.run([sys.executable, '-B', REG] + list(a), env=self.env, capture_output=True, text=True); return p.returncode, p.stdout + p.stderr
    def test_alarm_layout_flags_in_new_seat(self):
        self.parts(['lean_v1/HUNTER_RULES_V2.md,build/blind_kit_v1.py'])
        rc, out = self.run_reg('ledger-check'); self.assertEqual(rc, 1, out); self.assertIn('LEDGER_CHECK FLAG files 2 flags 2', out)
    def test_baseline_then_pass(self):
        self.parts(['NOW.md,{PACK}/RULES.md', '{PACK}/RULES.md'])
        rc, out = self.run_reg('baseline', 'who=TEST'); self.assertEqual(rc, 0, out); self.assertIn('BASELINE rows 2', out)
        rc, out = self.run_reg('ledger-check'); self.assertEqual(rc, 0, out); self.assertIn('LEDGER_CHECK PASS files 3 flags 0', out)
        rc, out = self.run_reg('baseline'); self.assertEqual(rc, 0, out); self.assertIn('BASELINE rows 0', out)
        open(os.path.join(self.pack, 'RULES.md'), 'a').write('x\n')
        rc, out = self.run_reg('ledger-check'); self.assertEqual(rc, 1, out); self.assertIn('CHANGED_WITHOUT_LEDGER_ROW', out)
    def test_missing_file_refused_nothing_written(self):
        self.parts(['NOW.md', 'lean_v1/HUNTER_RULES_V2.md'])
        rc, out = self.run_reg('baseline'); self.assertEqual(rc, 2, out); self.assertIn('REFUSED BASELINE_MISSING files 1', out)
        self.assertFalse(os.path.exists(os.path.join(self.reg, 'LEDGER.tsv')))
    def test_unset_placeholder_stays_missing(self):
        self.env.pop('LL_PACK'); self.parts(['{PACK}/RULES.md'])
        rc, out = self.run_reg('baseline'); self.assertEqual(rc, 2, out); self.assertIn('MISSING P01 {PACK}/RULES.md', out)
if __name__ == '__main__':
    unittest.main(verbosity=1)
