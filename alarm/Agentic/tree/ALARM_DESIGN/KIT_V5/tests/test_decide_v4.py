#!/usr/bin/env python3
"""test_decide_v4.py (SCOUT, 2 Nov 2026, V1_18_FIXES; RESULTS_R5 item 7, RESULTS_R6): the refusal and the run budget name the newest queue
beside the tool, by number, whichever it is. A copy of the tool in a temp folder with planted queues; a planted run. No data.
TOOL_UNDER_TEST names the tool file."""
import importlib.util, os, shutil, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.environ.get('TOOL_UNDER_TEST') or os.path.join(HERE, '..', 'tools', 'decide_v4.py')
N = 0


def load(d):
    global N
    N += 1
    p = os.path.join(d, 'decide_v4.py'); shutil.copy(SRC, p)
    spec = importlib.util.spec_from_file_location('decide_t%d' % N, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def plant_run(r):
    g = os.path.join(r, 'receipts', '1_GRADE_IDEA'); os.makedirs(os.path.join(g, 'HANDOFF', 'REAL_SEALED')); os.makedirs(os.path.join(r, 'registers'))
    w = lambda p, t: open(os.path.join(r, p), 'w').write(t)
    w('registers/VARIANTS.tsv', 'idea\tV\tlean\nIDEA\tV1\tFADE\n')
    w('receipts/1_GRADE_IDEA/STAGES.tsv', 'stage\trc\ngrade_V1\t0\nhandoff\t0\nend\t0\n')
    w('receipts/1_GRADE_IDEA/HANDOFF/SUMMARY.tsv', 'V\tstatus\tgate\twaves\nV1\tOK\tPASS\t100\n')
    w('receipts/1_GRADE_IDEA/HANDOFF/REAL_SEALED/REAL_RULES_V1.tsv', 'key\tvalue\nR1\tPASS\nR2\tno\ncounted\t4\npassing\t3\nneed\t3\n')
    w('receipts/1_GRADE_IDEA/HANDOFF/REAL_SEALED/REAL_V1.tsv', 'horizon\tlead\tt\n15m\t4\t1.8\n1h\t3\t1.5\n')
    w('receipts/1_GRADE_IDEA/FIRES.tsv', 'V1\t3000\tabc\t/x/list.tsv\n')


class Queue(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); self.t = self.d.name; self.run_dir = os.path.join(self.t, 'run'); plant_run(self.run_dir)

    def tearDown(self):
        self.d.cleanup()

    def q(self, name, mb):
        with open(os.path.join(self.t, name), 'w') as f:
            f.write("'RUN_BUDGET_MB': %d,\n" % mb)

    def test_refusal_names_newest_by_number(self):
        for n, mb in (('queue_job_v9.py', 1), ('queue_job_v11.py', 2), ('queue_job_v13.py', 3)):
            self.q(n, mb)
        m = load(self.t)
        with self.assertRaises(m.Refused) as c:
            m.decide(self.run_dir, 'IDEA', 'V1', '1_GRADE_IDEA', None)
        self.assertIn('queue_job_v13.py', str(c.exception)); self.assertNotIn('queue_job_v11', str(c.exception))

    def test_budget_read_from_that_queue(self):
        self.q('queue_job_v11.py', 111); self.q('queue_job_v13.py', 333)
        self.assertEqual(load(self.t).run_budget_mb(), 333)

    def test_works_when_v11_is_gone(self):
        self.q('queue_job_v12.py', 700)
        m = load(self.t); self.assertEqual(m.run_budget_mb(), 700); self.assertEqual(m.current_queue(), 'queue_job_v12.py')

    def test_look_alikes_not_taken(self):
        self.q('queue_job_v12.py', 700); self.q('queue_job_v99_old.py', 1); self.q('queue_job_v99.py.pre_SCOUT', 1)
        self.assertEqual(load(self.t).current_queue(), 'queue_job_v12.py')

    def test_no_queue_refused_by_name(self):
        m = load(self.t)
        with self.assertRaises(m.Refused) as c:
            m.decide(self.run_dir, 'IDEA', 'V1', '1_GRADE_IDEA', None)
        self.assertIn('NO queue_job', str(c.exception))

    def test_no_queue_name_typed_in_the_code(self):
        import re
        code = [l for l in open(SRC).read().split('"""', 2)[2].split('\n')]
        self.assertEqual([l for l in code if re.search(r'queue_job_v[0-9]', l)], [])

    def test_entry_size_message_uses_the_budget(self):
        self.q('queue_job_v13.py', 100)
        m = load(self.t)
        d = m.decide(self.run_dir, 'IDEA', 'V1', '1_GRADE_IDEA', None, too_big=True)
        self.assertEqual(d['state'], 'NO ENTRY'); self.assertIn('100 MB run budget', d['note'])


if __name__ == '__main__':
    unittest.main()
