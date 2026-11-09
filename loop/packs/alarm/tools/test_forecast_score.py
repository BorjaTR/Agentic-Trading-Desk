#!/usr/bin/env python3
"""test_forecast_score.py (SCOUT 2026-11-08; part P23; plan wave 1). Planted forecasts with known answers (temp folder on SCRATCH_DISK):
a run whose R1 passes the rule (+2 over the yardstick, t >= 3, 3 of 5 months), one that beats the yardstick by less than +2, and an R3P
round that must be scored as its own round. Expected Brier values are computed by hand below.  python3 -B test_forecast_score.py"""
import importlib.util, os, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
spec = importlib.util.spec_from_file_location('fs', os.path.join(HERE, 'forecast_score.py')); fs = importlib.util.module_from_spec(spec); spec.loader.exec_module(fs)

CARD = """# CARD {run}
Yardstick FDONLY.
| round | question | change | lead 15 min | lead minus FDONLY | t | months up | waves | job |
|---|---|---|---|---|---|---|---|---|
| R1 | q | c | +{r1} | x | {t1} | {m1} of 5 | 400 | j |
| R3 | q | c | +{r3} | x | 4.0 | 4 of 5 | 350 | j |
| R3P | q | c | +{r3p} | x | 3.5 | 4 of 5 | 340 | j |
"""
FC = "round\tutc\tp_beat_yardstick\tforecast_net15\tlow80_net15\thigh80_net15\tforecast_t\tforecast_months_up\n" \
     "R1\tu\t{p1}\t12.0\t9.0\t15.0\t4\t4\nR3\tu\t0.5\t13.0\t10.0\t16.0\t4\t4\nR3P\tu\t0.2\t9.0\t7.0\t11.0\t3\t3\n"

class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
        self.old = (fs.RUNS, fs.HERE); fs.RUNS = self.t; fs.HERE = self.t
    def tearDown(self):
        fs.RUNS, fs.HERE = self.old; shutil.rmtree(self.t)
    def plant(self, run, r1, t1, m1, r3, r3p, p1):
        d = os.path.join(self.t, run); os.makedirs(os.path.join(d, 'work'))
        open(os.path.join(d, 'CARD.md'), 'w').write(CARD.format(run=run, r1=r1, t1=t1, m1=m1, r3=r3, r3p=r3p))
        open(os.path.join(d, 'work', 'FORECASTS.tsv'), 'w').write(FC.format(p1=p1))
    def rows(self):
        import csv
        return {(r['run'], r['round']): r for r in csv.DictReader(open(os.path.join(self.t, 'FORECAST_SCORES.tsv')), delimiter='\t')}
    def test_pass_rule_and_placebo(self):
        fd = fs.yardsticks()[0]                                   # FDONLY Sep-Jan from the real store (8.09)
        self.plant('LA', r1=round(fd + 3.0, 2), t1=5.0, m1=4, r3=round(fd + 1.0, 2), r3p=round(fd + 5.0, 2), p1=0.8)   # R1 passes; R3 beats by +1 only
        self.plant('LB', r1=round(fd + 3.0, 2), t1=2.5, m1=4, r3=round(fd - 1.0, 2), r3p=round(fd - 2.0, 2), p1=0.8)   # R1 fails on t
        fs.main(['LA', 'LB']); r = self.rows()
        self.assertEqual(r[('LA', 'R1')]['beat'], '1'); self.assertAlmostEqual(float(r[('LA', 'R1')]['brier']), 0.04, places=4)   # (0.8-1)^2
        self.assertEqual(r[('LA', 'R3')]['beat'], '0')                                                                          # +1 < +2
        self.assertEqual(r[('LA', 'R3P')]['beat'], '1'); self.assertAlmostEqual(float(r[('LA', 'R3P')]['brier']), 0.64, places=4)  # (0.2-1)^2
        self.assertEqual(r[('LB', 'R1')]['beat'], '0'); self.assertAlmostEqual(float(r[('LB', 'R1')]['brier']), 0.64, places=4)   # t 2.5 < 3
        self.assertEqual(r[('LA', 'R3P')]['forecast_row'], 'R3P')                                                               # never paired with R3

    def test_months_column_any_name(self):                   # C101 (M071): L10 card header 'months above +10.99'
        fd = fs.yardsticks()[0]
        d = os.path.join(self.t, 'LC'); os.makedirs(os.path.join(d, 'work'))
        open(os.path.join(d, 'CARD.md'), 'w').write(CARD.format(run='LC', r1=round(fd + 3.0, 2), t1=5.0, m1=2, r3=1, r3p=1).replace('| months up |', '| months above +8.09 |'))
        open(os.path.join(d, 'work', 'FORECASTS.tsv'), 'w').write(FC.format(p1=0.8))
        up, lead, tt, mo = fs.card('LC'); self.assertEqual(mo['R1'], 2)
        fs.main(['LC']); self.assertEqual(self.rows()[('LC', 'R1')]['beat'], '0')       # 2 of 5 months: the pass rule fails

    def test_print_writes_nothing(self):                       # C98 (M066)
        fd = fs.yardsticks()[0]
        self.plant('LA', r1=round(fd + 3.0, 2), t1=5.0, m1=4, r3=round(fd + 1.0, 2), r3p=round(fd + 5.0, 2), p1=0.8)
        fs.main(['LA', '--print']); self.assertFalse(os.path.exists(os.path.join(self.t, 'FORECAST_SCORES.tsv')))

    def test_receipt_wins_over_card_cell(self):                # C145 (K2 packet): a wrong card cell must not reach the error
        import json
        fd = fs.yardsticks()[0]
        self.plant('LD', r1=round(fd + 3.5, 2), t1=5.0, m1=4, r3=round(fd + 1.0, 2), r3p=round(fd + 5.0, 2), p1=0.8)
        cp = os.path.join(self.t, 'LD', 'CARD.md'); txt = open(cp).read()
        txt = txt.replace('| R1 | q | c |', '| R1 | q | c V1 |').replace('| R3 | q | c |', '| R3 | q | c V3 |')
        open(cp, 'w').write(txt)
        for pipe, alarm, lead in (('pipe_r1', 'X_V1', fd + 3.0), ('pipe_r3', 'X_V2', fd + 9.0)):
            os.makedirs(os.path.join(self.t, 'LD', pipe))
            json.dump({'alarm': alarm, 'numbers': {'real': [{'horizon': '15m', 'lead': '%.4f' % lead, 't': '5.0'}]}},
                      open(os.path.join(self.t, 'LD', pipe, 'STEP_11_GRADE.json'), 'w'))
        fs.main(['LD']); r = self.rows()
        self.assertAlmostEqual(float(r[('LD', 'R1')]['actual15']), round(fd + 3.0, 4), places=3)       # receipt, not card's +3.5
        self.assertTrue(r[('LD', 'R1')]['actual_from'].startswith('STEP_11 (card said'))
        self.assertAlmostEqual(float(r[('LD', 'R3')]['actual15']), round(fd + 1.0, 2), places=2)       # V2 receipt vs card V3: card kept
        self.assertTrue(r[('LD', 'R3')]['actual_from'].startswith('card (receipt variant 2'))

if __name__ == '__main__':
    unittest.main(verbosity=1)
