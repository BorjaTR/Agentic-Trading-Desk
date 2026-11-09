#!/usr/bin/env python3
"""test_speed_report_v1.py (SCOUT C230, L11 K41): synthetic series folder; the tool must not crash on a drill with no numeric minutes
(L11: StatisticsError no median for empty data), must print 'no data' for it, and must give per-round step minutes from FORECASTS seals."""
import csv, os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); TOOL = os.path.join(HERE, 'speed_report_v1.py'); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
def w(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(text)
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE); t = self.t
        reg = os.path.join(t, 'drills_v2', 'registers')
        w(os.path.join(reg, 'DRILL_RUNS.tsv'), 'run_id\tdrill_id\tminutes\nr1\tDA\t3\nr2\tDA\t5\nr3\tDEMPTY\t-\nr4\tDEMPTY\t\n')
        w(os.path.join(reg, 'PARTS.tsv'), 'part_id\tname\tdrills\nP01\tone\tDA\nP02\ttwo\tDEMPTY\nP03\tthree\t\n')
        run = os.path.join(t, 'runs_v2', 'L99')
        w(os.path.join(run, 'ops', 'LAUNCH_UTC.txt'), '2026-01-01T00:00:00Z\n')
        w(os.path.join(run, 'work', 'RESULT_L99.md'), 'DONE 2026-01-01T00:40:00Z. text\n')
        w(os.path.join(run, 'work', 'FORECASTS.tsv'), 'round\tutc\tp\n# note row\nR1\t2026-01-01T00:04:00Z\t0.5\nR2\t2026-01-01T00:10:00Z\t\nR2\t2026-01-01T00:10:00Z\t\nR3\t2026-01-01T00:22:00Z\t0.4\nR3P\t2026-01-01T00:22:00Z\t0.3\n')
        w(os.path.join(t, 'runs_v2', 'L98', 'ops', 'LAUNCH_UTC.txt'), '2026-01-01T00:00:00Z\n')   # no FORECASTS, no RESULT
        self.out = os.path.join(t, 'speed.tsv')
    def tearDown(self): shutil.rmtree(self.t, ignore_errors=True)
    def run_tool(self, runs):
        return subprocess.run([sys.executable, '-B', TOOL, '--root', self.t, '--runs', runs, '--out', self.out], capture_output=True, text=True)
    def rows(self): return {(r['kind'], r['id']): r for r in csv.DictReader(open(self.out), delimiter='\t')}
    def test_empty_drill_no_crash(self):
        p = self.run_tool('L99'); self.assertEqual(p.returncode, 0, p.stderr); r = self.rows()
        self.assertEqual(r[('drill', 'DEMPTY')]['median_min'], 'no data'); self.assertEqual(r[('drill', 'DEMPTY')]['n'], '0')
        self.assertEqual(r[('part', 'P02')]['median_min'], 'no data'); self.assertEqual(r[('drill', 'DA')]['median_min'], '4.0')
        self.assertNotIn(('part', 'P03'), r); self.assertIn('NO DATA', p.stdout)
    def test_step_minutes(self):
        p = self.run_tool('L99'); self.assertEqual(p.returncode, 0, p.stderr); r = self.rows()
        self.assertEqual(r[('run', 'L99')]['median_min'], '40.0')
        got = {k[1]: (v['median_min'], v['within']) for k, v in r.items() if k[0] == 'step'}
        self.assertEqual(got, {'L99:R0 (launch to R1 seal)': ('4.0', 'yes'), 'L99:R1': ('6.0', 'yes'), 'L99:R2': ('12.0', 'no'), 'L99:R3/R3P': ('18.0', 'no')})
    def test_run_without_receipts_is_no_data(self):
        p = self.run_tool('L98'); self.assertEqual(p.returncode, 0, p.stderr); r = self.rows()
        self.assertEqual(r[('step', 'L98:rounds')]['median_min'], 'no data'); self.assertNotIn(('run', 'L98'), r)
if __name__ == '__main__':
    unittest.main()
