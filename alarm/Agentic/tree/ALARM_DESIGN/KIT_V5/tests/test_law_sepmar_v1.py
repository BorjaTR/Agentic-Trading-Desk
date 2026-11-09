"""test_law_sepmar.py (SCO-A176): the law edition on planted dates, every boundary, armed and not. python3 -B test_law_sepmar.py [law.py]"""
import importlib.util, os, sys, tempfile, unittest
LAW = sys.argv.pop(1) if len(sys.argv) > 1 and sys.argv[1].endswith('.py') else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'law.py')


def load():
    s = importlib.util.spec_from_file_location('law_t', LAW); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


COLS = 'utc\tevent\trun\tidea\tV\tdef_rel\tdef_sha16\tpipe\tjob\tstate\tedition\n'


def reg(rows):
    f = tempfile.NamedTemporaryFile('w', suffix='.tsv', delete=False); f.write(COLS)
    for ev, job, st in rows:
        f.write('t\t%s\tR\tI\tV1\td\ts\tp\t%s\t%s\tE\n' % (ev, job, st))
    f.close(); return f.name


class T(unittest.TestCase):
    def setUp(self):
        os.environ.pop('VOLAT_HOLDOUT_OPEN', None); self.L = load()

    def arm(self, v):
        os.environ['VOLAT_HOLDOUT_OPEN'] = v; self.L._ARMED.clear()

    def tearDown(self):
        os.environ.pop('VOLAT_HOLDOUT_OPEN', None)

    def test_l01_in_sample_open(self):
        for d in (20250901, 20250910, 20251231, 20260101, 20260331):
            self.assertIsNone(self.L.research_refusal(d), d)

    def test_l02_out_of_sample_refused(self):
        for d in (20260401, 20260515, 20260731):
            self.assertTrue(self.L.research_refusal(d).startswith('OUT_OF_SAMPLE'), d)

    def test_l03_never_seen_by_name(self):
        for d in (20260801, 20261015, 20261130):
            self.assertTrue(self.L.research_refusal(d).startswith('NEVER_SEEN'), d)

    def test_l04_after_blind(self):
        for d in (20261201, 20270115):
            self.assertTrue(self.L.research_refusal(d).startswith('BLIND'), d)

    def test_l05_armed_opens_only_apr_jul(self):
        self.arm(reg([('OPEN', 'J1', 'OPENED')]) + '|J1')
        for d in (20260401, 20260731, 20260331):
            self.assertIsNone(self.L.research_refusal(d), d)
        self.assertTrue(self.L.research_refusal(20260801).startswith('NEVER_SEEN'))
        self.assertTrue(self.L.research_refusal(20261201).startswith('BLIND'))

    def test_l06_spent_look_refused(self):
        self.arm(reg([('OPEN', 'J1', 'OPENED'), ('RESULT', 'J1', 'PASS')]) + '|J1')
        self.assertTrue(self.L.research_refusal(20260401).startswith('OUT_OF_SAMPLE'))

    def test_l07_wrong_job_missing_register_bad_value(self):
        for v in (reg([('OPEN', 'J1', 'OPENED')]) + '|J2', '/no/such.tsv|J1', 'J1', '', reg([('OPEN', 'J1', 'OPENED')]) + '|'):
            self.arm(v); self.assertTrue(self.L.research_refusal(20260401).startswith('OUT_OF_SAMPLE'), v)

    def test_l08_open_row_not_opened_state(self):
        self.arm(reg([('OPEN', 'J1', 'PENDING')]) + '|J1')
        self.assertTrue(self.L.research_refusal(20260601).startswith('OUT_OF_SAMPLE'))

    def test_l09_proof_never_opens_never_seen(self):
        self.L.PROOF_OPEN = (20260101, 20261231)
        self.assertTrue(self.L.proof_refusal(20260901).startswith('NEVER_SEEN'))
        self.assertIsNone(self.L.proof_refusal(20260501))
        self.L.PROOF_OPEN = (0, 0)
        self.assertTrue(self.L.proof_refusal(20260501).startswith('OUT_OF_SAMPLE'))
        self.assertIsNone(self.L.proof_refusal(20260215))

    def test_l10_store_refusal_research(self):
        self.assertTrue(self.L.store_refusal('candidate_days', 20260410, 'research').startswith('OUT_OF_SAMPLE'))
        self.assertTrue(self.L.store_refusal('candidate_days', 20260810, 'research').startswith('NEVER_SEEN'))
        self.assertIsNone(self.L.store_refusal('candidate_days', 20260810, 'build'))

    def test_l11_quarantine_and_bad_day_unchanged(self):
        self.assertTrue(self.L.quarantine_refusal('ADES.N2V1', 20260315).startswith('QUARANTINE'))
        self.assertIsNone(self.L.quarantine_refusal('PRICE', 20260315))
        for bad in (20260230, '2026040', 'x'):
            self.assertRaises(ValueError, self.L.research_refusal, bad)

    def test_l12_tables(self):
        self.assertEqual(self.L.OUT_OF_SAMPLE, (20260401, 20260731)); self.assertEqual(self.L.NEVER_SEEN, (20260801, 20261130))
        self.assertEqual([r[:2] for r in self.L.RESEARCH_REFUSED], [(20260401, 20260731), (20260801, 20261130), (20261201, 99999999)])


if __name__ == '__main__':
    unittest.main(verbosity=1)
