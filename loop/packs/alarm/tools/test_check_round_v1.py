#!/usr/bin/env python3
"""test_check_round_v1.py (SCOUT 2026-11-08; part P20; plan doc 'Re-score and improve every part', wave 1). Planted run folders with
known answers on SCRATCH_DISK (no test output on the internal disk): a clean run passes; each planted defect is flagged; a good card with
a CAUSES block gives 0 card flags.  python3 -B test_check_round_v1.py"""
import os, shutil, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); TOOL = os.path.join(HERE, 'check_round_v1.py'); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
CLAIMS = """## R0 step 0
pro-practice: value of information ... stuck check: A1 ...
R1 | 2026-11-08T10:00:00Z | change ... builds on F0001
R2 | 2026-11-08T10:20:00Z | split plan ... power line: gap needed 14.9 for t 2.5
R3 | 2026-11-08T10:40:00Z | gate ...
R3P | 2026-11-08T10:40:00Z | placebo ...
"""
FC = "round\tutc\tp\n" + "R1\t2026-11-08T10:00:01Z\t0.5\nR2\t2026-11-08T10:20:01Z\t0.5\nR3\t2026-11-08T10:40:01Z\t0.4\nR3P\t2026-11-08T10:40:01Z\t0.3\n"
JOBS = "utc\tjob\tqueue\tround\n" + "2026-11-08T10:01:00Z\t1\tQ\tR1 pipe_r1\n2026-11-08T10:21:00Z\t2\tQ\tR2 split\n2026-11-08T10:41:00Z\t3\tQ\tR3 pipe_r3\n2026-11-08T10:41:30Z\t4\tQ\tR3P pipe_r3p\n"
GOOD_CARD = """# CARD L99
| round | question |
Works when: hot market +21.40 vs +14.13 (see CAUSES).
Held-out Feb-Mar: orchestrator only (never written in a card).
## CAUSES
- QUESTION hot pays more | receipt=x.tsv 0123 number=+7.26 t=1.14 differs_in=heat
- heat state pays more | receipt=x.tsv 0123 number=+7.26 t=2.60 differs_in=heat
## NEXT TESTS
1. F0023; split; moves it to SUPPORTED if gap t >= 2.5
"""

def mk(d, claims=CLAIMS, fc=FC, jobs=JOBS, card=None):
    os.makedirs(os.path.join(d, 'work'))
    open(os.path.join(d, 'work', 'CLAIMS.md'), 'w').write(claims); open(os.path.join(d, 'work', 'FORECASTS.tsv'), 'w').write(fc)
    open(os.path.join(d, 'work', 'MAC_JOBS.tsv'), 'w').write(jobs)
    if card is not None: open(os.path.join(d, 'CARD.md'), 'w').write(card)

def run(d):
    p = subprocess.run([sys.executable, '-B', TOOL, d, '--run-number', '10'], capture_output=True, text=True); return p.returncode, p.stdout

class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
    def tearDown(self):
        shutil.rmtree(self.t)
    def test_clean_run_passes(self):
        d = os.path.join(self.t, 'ok'); mk(d, card=GOOD_CARD); rc, out = run(d)
        self.assertEqual(rc, 0, out); self.assertIn('ROUND_CHECK PASS', out)
    def test_forecast_after_job_flagged(self):
        d = os.path.join(self.t, 'late'); mk(d, fc=FC.replace('R3\t2026-11-08T10:40:01Z', 'R3\t2026-11-08T10:59:00Z')); rc, out = run(d)
        self.assertEqual(rc, 3); self.assertIn('R3 FORECASTS row 2026-11-08T10:59:00Z is after its first job', out)
    def test_no_step0_no_power_no_placebo(self):
        c = CLAIMS.replace('## R0 step 0\n', '').replace('power line: gap needed 14.9 for t 2.5', 'split plan').replace('R3P | 2026-11-08T10:40:00Z | placebo ...\n', '')
        d = os.path.join(self.t, 'miss'); mk(d, claims=c, fc=FC.replace('R3P\t2026-11-08T10:40:01Z\t0.3\n', ''), jobs=JOBS.replace('2026-11-08T10:41:30Z\t4\tQ\tR3P pipe_r3p\n', ''))
        rc, out = run(d)
        for k in ('MISSING R0 step 0', 'MISSING R2 power line', 'MISSING R3P placebo claim'): self.assertIn(k, out)
    def test_card_overclaims_flagged(self):
        bad = GOOD_CARD.replace('Works when: hot market +21.40 vs +14.13 (see CAUSES).', 'Works when a hot market pays more because leverage is cut.') \
                       .replace('t=2.60', 'no t')
        d = os.path.join(self.t, 'card'); mk(d, card=bad); rc, out = run(d)
        self.assertIn('card cause sentence outside the CAUSES block, lines [3]', out)
        self.assertIn('card CAUSES line without t= (and not a QUESTION), lines [7]', out)
    def test_heldout_month_on_card_flagged(self):
        d = os.path.join(self.t, 'ho'); mk(d, card=GOOD_CARD + 'lead_2602 +1.2\n'); rc, out = run(d)
        self.assertIn('card names a held-out month column', out)

    def test_card_cell_and_quoted_sha16(self):                 # C152 (K2 packet plants)
        import json, hashlib
        card = GOOD_CARD.replace('| round | question |', '| round | question | change | lead 15 min |\n| R1 | q | X V1 | +14.84 (1 h +15.40) | x |')
        d = os.path.join(self.t, 'cell'); mk(d, card=card)
        os.makedirs(os.path.join(d, 'pipe_r1'))
        json.dump({'alarm': 'X_V1', 'numbers': {'real': [{'horizon': '15m', 'lead': '14.3429', 't': '4.7'}]}}, open(os.path.join(d, 'pipe_r1', 'STEP_11_GRADE.json'), 'w'))
        open(os.path.join(d, 'work', 'RESULT_L99.md'), 'w').write('DONE\ncard sha16 0123456789abcdef\n')
        fh = hashlib.sha256(open(os.path.join(d, 'work', 'FORECASTS.tsv'), 'rb').read()).hexdigest()[:16]
        open(os.path.join(d, 'work', 'MAC_JOBS.tsv'), 'a').write('2026-11-08T10:42:00Z\t5\tQ\tR3 x\tFORECASTS.tsv R3 row (file %s)\n' % fh)
        rc, out = run(d)
        self.assertIn('card lead15 differs from its receipt: R1 +14.84 vs STEP_11 14.34', out)
        self.assertIn('the card changed after RESULT', out)
        self.assertIn('OK FORECASTS.tsv equals the sha16 the last job quotes', out)
        open(os.path.join(d, 'work', 'FORECASTS.tsv'), 'a').write('R9\tu\t0.1\n'); rc, out = run(d)
        self.assertIn('FORECASTS.tsv is', out)

    def test_row_quotes_per_job(self):                        # C219 (L11 assessors): JOB_SHEET quotes the round's own sealed row(s)
        import hashlib
        def rh(fc, r): return hashlib.sha256(''.join(l + '\n' for l in fc.splitlines() if l.startswith(r + '\t')).encode()).hexdigest()[:16]
        jobs = JOBS.replace('\tR1 pipe_r1\n', '\tR1 pipe_r1\tFORECASTS.tsv R1 row %s\n' % rh(FC, 'R1')) \
                   .replace('\tR2 split\n', '\tR2 split\tFORECASTS.tsv R2 row %s\n' % rh(FC, 'R2')) \
                   .replace('\tR3 pipe_r3\n', '\tR3 pipe_r3\tFORECASTS.tsv R3 row %s\n' % rh(FC, 'R3')) \
                   .replace('\tR3P pipe_r3p\n', '\tR3P pipe_r3p\tFORECASTS.tsv R3P row %s\n' % rh(FC, 'R3P'))
        d = os.path.join(self.t, 'rows'); mk(d, fc=FC + 'R4\t2026-11-08T11:00:00Z\t0.2\n', jobs=jobs); rc, out = run(d)   # a later row: fine
        self.assertEqual(rc, 0, out); self.assertIn('OK FORECASTS row(s) equal the sha16 each of 4 jobs quotes', out)
        d = os.path.join(self.t, 'rows_edit'); mk(d, fc=FC.replace('R1\t2026-11-08T10:00:01Z\t0.5', 'R1\t2026-11-08T10:00:01Z\t0.6'), jobs=jobs); rc, out = run(d)
        self.assertEqual(rc, 3, out); self.assertIn('MISSING FORECASTS R1 row(s) are', out); self.assertNotIn('R2 row(s) are', out)
    def test_file_quotes_prefix(self):                        # C219: old '(file X)' quotes (L10): an earlier quote must be a prefix of the file
        import hashlib
        h = lambda t: hashlib.sha256(t.encode()).hexdigest()[:16]; part = FC.split('R3\t')[0]
        jobs = JOBS.replace('\tR1 pipe_r1\n', '\tR1 pipe_r1\tFORECASTS.tsv R1 row (file %s)\n' % h(part)) \
                   .replace('\tR3 pipe_r3\n', '\tR3 pipe_r3\tFORECASTS.tsv R3 row (file %s)\n' % h(FC))
        d = os.path.join(self.t, 'pre'); mk(d, jobs=jobs); rc, out = run(d)
        self.assertEqual(rc, 0, out); self.assertIn('OK FORECASTS.tsv equals the sha16 the last job quotes', out)
        d = os.path.join(self.t, 'pre_bad'); mk(d, jobs=jobs.replace(h(part), '0123456789abcdef')); rc, out = run(d)
        self.assertEqual(rc, 3, out); self.assertIn('no start of FORECASTS.tsv hashes to 0123456789abcdef', out)

if __name__ == '__main__':
    unittest.main(verbosity=1)
