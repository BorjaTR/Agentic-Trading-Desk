#!/usr/bin/env python3
"""test_bar_check_v2.py (SCO-A182): planted SERIES_V2 rows and ASSESS files for bar_check_v2.py; seconds, no market data. Each run writes
a new folder dry_test_v2/bars_<utc>/ only.   python3 -B test_bar_check_v2.py"""
import json, os, shutil, subprocess, sys, unittest, importlib.util
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
LS = os.path.expanduser('~/mnt/dev/TradingPlatform_repo/volat-agent/forensics/team/SCOUT/loop_day_20261105/learning_series')
if not os.path.isdir(LS): LS = HERE if os.path.isfile(os.path.join(HERE, 'SERIES_V2_CONFIG.json')) else os.path.dirname(HERE)   # C218: Mac host or a pack copy
LS = os.environ.get('ALARM_SERIES_DIR', LS)   # C218 (from RC2 copy): the series folder (SERIES_V2_CONFIG.json)
BC = os.environ.get('BC_UNDER_TEST', os.path.join(HERE, 'bar_check_v2.py'))
TT = (os.environ['LL_TEST_TMP'] if os.environ.get('LL_TEST_TMP') else LS + '/dry_test_v2') + '/bars_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')   # C218: temp root env LL_TEST_TMP
spec = importlib.util.spec_from_file_location('bc', BC); bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
YARD = 5.88
HDR = 'section\titem\tvalue\treceipt\thow\n'


def assess(runf, arm, n, r1, best, best_round, err, match, m1, hand=0, stops=0, blind=0, overlap=20.0, red='no', repro=True, repro_change=False,
           bad_math=False):
    os.makedirs(runf)
    rid = '%s%02d' % (arm, n); task = 'SCT-A%d' % ((300 if arm == 'L' else 400) + n)
    launch = '2026-11-%02dT%02d:00:00Z' % (10 + n, 1 if arm == 'L' else 2)
    margin = round(best - YARD, 4)
    rows = [('V1', 'M1', '%d of %d' % (m1, m1 + 2)),
            ('V2', 'M7_R1', 'lead15 %s lead1h 1 waves 600 t15 4 months_pass 5 months 7 word PASS' % r1),
            ('V2', 'M8_YARD', 'yard15 %s best_round %d best_lead15 %s margin %s best_months_pass 5 best_t15 4.1 better yes' % (YARD, best_round, best, margin)),
            ('V2', 'M9_WITHIN', 'r1_lead15 %s best_lead15 %s diff %s best_beats_r1 yes r3_beats_r1 NA' % (r1, best, round(best - r1, 4))),
            ('V2', 'M11_FORECAST_R1', 'pred_lead15 %s actual_lead15 %s abs_err %s pred_months 5 actual_months 5 pred_better CTX.A:high tool_better CTX.A:high state_match %s sealed_before_job yes' % (r1 + err, r1, (err + 1) if bad_math else err, match)),
            ('V2', 'M11_FORECAST', 'mean_abs_err %s n_rounds 1 best_round_state_match %s' % (err, match)),
            ('V2', 'M12_NOVELTY', 'max_overlap_pct %s with OTHER source card rediscovery %s' % (overlap, red)),
            ('V2', 'M13_ARM', 'arm %s run_id %s task %s launch_utc %s' % (arm, rid, task, launch)),
            ('V2', 'B1_CLEAN', 'hand %d tool_stops %d blindfold %d' % (hand, stops, blind)),
            ('V1', 'ASSESSOR', 'planted first'), ('V1', 'TIME', 'planted')]
    open(runf + '/ASSESS.tsv', 'w').write(HDR + ''.join('%s\t%s\t%s\tplanted\tplanted\n' % r for r in rows))
    if repro:
        rr = [(s, i, (v.replace('mean_abs_err %s' % err, 'mean_abs_err %s' % (err + 0.5)) if (repro_change and i == 'M11_FORECAST') else v)) for s, i, v in rows]
        rr = [(s, i, 'planted second' if i == 'ASSESSOR' else v) for s, i, v in rr]
        open(runf + '/ASSESS_REPRO.tsv', 'w').write(HDR + ''.join('%s\t%s\t%s\tplanted\tplanted\n' % r for r in rr))
    os.makedirs(runf + '/pipe_r2' if best_round == 2 else runf + '/pipe')
    open((runf + '/pipe_r2' if best_round == 2 else runf + '/pipe') + '/INPUT.json', 'w').write(json.dumps({'idea': 'PLANT%s' % rid}))


def series(d):
    os.makedirs(d, exist_ok=True); p = d + '/SERIES_V2.tsv'
    open(p, 'w').write(open(os.environ.get('ALARM_SERIES_HEADER') or (LS + '/SERIES_V2.tsv' if os.path.isfile(LS + '/SERIES_V2.tsv') else os.path.join(HERE, 'SERIES_V2_HEADER.tsv'))).readline())   # C71: header only (the live series now holds real L01-L09 rows: ROW_EXISTS)
    return p


def cfg(d, look=(1.0, 1.0, 1.0, 1.0)):
    c = json.load(open(LS + '/SERIES_V2_CONFIG.json')); c.pop('yardstick', None)   # C225: a planted look in a temp Sep-Mar file, never the real one
    yp = d + '/SEPMAR_PLANT.json'; open(yp, 'w').write(json.dumps({'yardstick': {'look_lead15_by_month': list(look) if look else None}}))
    c['yardstick_sepmar_file'] = {'path': yp}
    p = d + '/CFG.json'; open(p, 'w').write(json.dumps(c)); return p


def run(*args):
    r = subprocess.run([sys.executable, '-B', BC] + list(args), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr


def block(d, good=True, repro_break=None):
    s = series(d)
    for n in range(1, 11):
        if good:
            Lr1, Lbest = 6.0, round(YARD + n * 0.8 - 2 + 2, 4)
            Lerr, Lmatch, Lm1 = (3.0 if n <= 5 else 1.0), ('yes' if n >= 4 else 'no'), 1
            Cbest, Cm1 = YARD - 1 + (n % 2) * 0.1, 3
        else:
            Lr1, Lbest, Lerr, Lmatch, Lm1 = 6.0, YARD + 1, 2.0, 'no', 3
            Cbest, Cm1 = YARD + 1, 3
        assess(d + '/runs_v2/L%02d' % n, 'L', n, Lr1, Lbest, 2, Lerr, Lmatch, Lm1, repro=(n <= 6), repro_change=(repro_break == n))
        assess(d + '/runs_v2/C%02d' % n, 'C', n, 6.0, Cbest, 1, 2.0, 'no', Cm1, repro=(n <= 6), repro_change=False)
        for x in ('L', 'C'):
            rc, out = run('row', '--runf', d + '/runs_v2/%s%02d' % (x, n), '--series', s, '--write')
            assert rc == 0, out
    return s


class T(unittest.TestCase):
    def test_01_perm_exact(self):
        p, how = bc.perm_p([1, 2, 3], [0, 0, 0]); self.assertAlmostEqual(p, 1 / 20); self.assertIn('exact 20', how)

    def test_02_good_block_passes(self):
        d = TT + '/good'; s = block(d)
        for x in ('L01', 'L02', 'L03'):     # three LOOK rows that beat the planted yardstick look figure 1.0 in 4 of 4 months
            rc, out = run('look', '--run-id', x, '--series', s, '--by-month', '2,2,2,0.5', '--t-pooled', '2.5', '--receipt', 'planted', '--write'); self.assertEqual(rc, 0, out)
        rc, out = run('bars', '--series', s, '--config', cfg(d)); print(out)
        self.assertEqual(rc, 0, out)
        for k in ('B1 PASS', 'B2 PASS', 'B2a PASS', 'B2b PASS', 'B2c PASS', 'B3 PASS', 'B4 PASS', 'KILL_RULE no', 'BAR PASS'):
            self.assertIn(k, out)

    def test_03_no_learning_kills(self):
        d = TT + '/flat'; s = block(d, good=False)
        rc, out = run('bars', '--series', s, '--config', cfg(d, look=None))
        self.assertIn('B2b FAIL', out); self.assertIn('B3 FAIL', out); self.assertIn('KILL_RULE TRIGGER', out); self.assertIn('B4 PENDING NO_YARDSTICK_LOOK', out)

    def test_04_repro_break_cuts_streak(self):
        d = TT + '/repro'; s = block(d, repro_break=3)
        rc, out = run('bars', '--series', s, '--config', cfg(d))
        b1 = [l for l in out.split('\n') if l.startswith('B1')][0]; self.assertIn('B1 PASS', b1)    # C01..L06 by launch: streak after L03
        self.assertIn('L03(hand 0 stops 0 blind 0 repro no)', b1)

    def test_05_mismatch_detected(self):
        d = TT + '/mism'; s = block(d)
        t = open(s).read().split('\n'); f = t[1].split('\t'); i = bc.COLS.index('best_margin'); f[i] = '9.99'; t[1] = '\t'.join(f)
        open(s, 'w').write('\n'.join(t))
        rc, out = run('bars', '--series', s, '--config', cfg(d)); self.assertEqual(rc, 3); self.assertIn('MISMATCH', out)

    def test_06_bad_forecast_math_refused(self):
        d = TT + '/math'; s = series(d); assess(d + '/runs_v2/L01', 'L', 1, 6.0, 8.0, 2, 1.0, 'yes', 0, bad_math=True)
        rc, out = run('row', '--runf', d + '/runs_v2/L01', '--series', s); self.assertEqual(rc, 2); self.assertIn('REFUSED ASSESS_MATH', out)

    def test_09_kv_free_text_and_R_round(self):         # C99: free text inside a value; best_round 'R1'
        self.assertEqual(bc.kv('max_overlap_pct 100 (by DEF nesting, not a tool) with X source DEF rediscovery yes (one)')['rediscovery'], 'yes')
        self.assertEqual(bc.kv('lead15 12.36 waves 633 word PASS')['waves'], '633')

    def test_10_replace_keeps_old_row(self):            # C99: --replace needs a reason and keeps the old row
        d = TT + '/t10'; s = series(d)
        assess(d + '/runs_v2/L01', 'L', 1, 6.0, 9.0, 2, 1.0, 'yes', 1)
        self.assertEqual(run('row', '--runf', d + '/runs_v2/L01', '--series', s, '--write')[0], 0)
        rc, out = run('row', '--runf', d + '/runs_v2/L01', '--series', s, '--write', '--replace'); self.assertIn('NO_REASON', out)
        rc, out = run('row', '--runf', d + '/runs_v2/L01', '--series', s, '--write', '--replace', '--reason', 'test'); self.assertEqual(rc, 0, out)
        self.assertEqual(sum(1 for l in open(s) if l.startswith('RUN\tL01\t')), 1)
        self.assertIn('\ttest\tRUN\tL01', open(d + '/SERIES_V2_REPLACED.tsv').read())

    def test_08_host_path_old_rows(self):               # C90 (M043): VM paths and series-relative paths of the live series rows
        self.assertEqual(bc.host_path('<VM_SESSION>/mnt/dev/a/runs_v2/L01'), os.path.join(os.path.expanduser('~'), 'dev/a/runs_v2/L01'))
        self.assertEqual(bc.host_path('runs_v2/L06', '/x/y/SERIES_V2.tsv'), '/x/y/runs_v2/L06')
        self.assertEqual(bc.host_path('/abs/runs_v2/L09', '/x/y/SERIES_V2.tsv'), '/abs/runs_v2/L09')

    def test_07_one_look_only_and_row_once(self):
        d = TT + '/look'; s = series(d); assess(d + '/runs_v2/L01', 'L', 1, 6.0, 8.0, 2, 1.0, 'yes', 0)
        self.assertEqual(run('row', '--runf', d + '/runs_v2/L01', '--series', s, '--write')[0], 0)
        rc, out = run('row', '--runf', d + '/runs_v2/L01', '--series', s, '--write'); self.assertIn('REFUSED ROW_EXISTS', out)
        self.assertEqual(run('look', '--run-id', 'L01', '--series', s, '--by-month', '1,2,3,4', '--t-pooled', '2', '--write')[0], 0)
        rc, out = run('look', '--run-id', 'L01', '--series', s, '--by-month', '1,2,3,4', '--t-pooled', '2', '--write'); self.assertIn('LOOK_EXISTS', out)
        row = [l for l in open(s).read().split('\n') if l.startswith('RUN\t')][0].split('\t')
        self.assertEqual(row[bc.COLS.index('idea_best')], 'PLANTL01'); self.assertEqual(row[bc.COLS.index('best_margin')], '2.12')


if __name__ == '__main__':
    os.makedirs(TT)
    unittest.main(verbosity=1)
