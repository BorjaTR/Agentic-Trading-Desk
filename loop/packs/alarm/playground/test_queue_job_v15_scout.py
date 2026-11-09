#!/usr/bin/env python3
"""test_queue_job_v15_scout.py (SCOUT playground C202, 8 Nov 2026): seconds-fast checks of the one changed rule of queue_job_v15_scout.py
(the TRY BUDGET exempts a held-out re-grade) on a synthetic run folder in a temporary folder on SCRATCH_DISK (else the system temp), removed at
the end. Nothing is filed, claimed or queued: only plan() is called. The days below are synthetic test data, not tool constants.
  python3 -B test_queue_job_v15_scout.py"""
import hashlib, importlib.util, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


Q = load('queue_job_v15_scout', os.path.join(HERE, 'queue_job_v15_scout.py'))
IDEA, RUNTAG = 'TIDEA', 'SCOUTT_20990101'
DESIGN_END, HELDOUT_END = '20990131', '20990331'      # synthetic blocks: the design grade and the held-out grade
TPL = '# JOB @@JOBNUM@@\nbash $MP/alarm_grade_chain_vX_to%s.sh $V $D $W < /dev/null > $W/x.out 2>&1\n'
HDR = {'VARIANTS': 'idea\tV\tlean\tdef_rel\tdef_sha16\tprereg_rel\tprereg_sha16\treason',
       'RUNS': 'job\tjob_sha16\tkind\tidea\tvariants\tqueue\treceipts_rel\ttemplate_sha16\tfrom_job'}


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


class Fixture:
    def __init__(self, root):
        self.root = root
        self.h = os.path.join(root, 'ALARM_DESIGN'); self.run = os.path.join(self.h, 'runs', RUNTAG)
        self.kit = os.path.join(root, 'KIT'); os.makedirs(os.path.join(self.kit, 'jobs'))
        for n, end in (('T_HELDOUT.job.sh.txt', HELDOUT_END), ('T_DESIGN.job.sh.txt', DESIGN_END)):
            open(os.path.join(self.kit, 'jobs', n), 'w').write(TPL % end)
        os.makedirs(os.path.join(self.run, 'registers')); os.makedirs(os.path.join(self.run, 'ideas', IDEA, 'defs'))
        os.makedirs(os.path.join(self.run, 'jobs')); os.makedirs(os.path.join(self.h, 'runs', 'IDEAS_CLAIMED'))
        open(os.path.join(self.h, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUNTAG, IDEA)), 'w').write('claimed\n')
        for n in Q.REGISTERS:
            open(os.path.join(self.run, 'registers', n + '.tsv'), 'w').write(HDR.get(n, 'a\tb') + '\n')
        self.card = 'ideas/%s/CARD.md' % IDEA
        open(os.path.join(self.run, self.card), 'w').write('card\n')
        self.job_n = 100

    def defn(self, name, k):
        rel = 'ideas/%s/defs/%s.json' % (IDEA, name)
        json.dump({'window': {'first': '20250901', 'last': '20260331'}, 'k': k}, open(os.path.join(self.run, rel), 'w'))
        return rel

    def variant(self, v, def_rel, reason='try'):
        row = [IDEA, v, 'FADE', def_rel, sha16(os.path.join(self.run, def_rel)), self.card, sha16(os.path.join(self.run, self.card)), reason]
        open(os.path.join(self.run, 'registers', 'VARIANTS.tsv'), 'a').write('\t'.join(row) + '\n')

    def graded(self, v, end):
        """a finished GRADE job of v (rc 0), its filed twin grading to <end>"""
        self.job_n += 1
        job = 'jobs/%d_judge_SCOUTT_GRADE_%s.job.sh' % (self.job_n, IDEA)
        open(os.path.join(self.run, job), 'w').write(TPL % end)
        rec = 'receipts/%d_GRADE_%s' % (self.job_n, IDEA)
        os.makedirs(os.path.join(self.run, rec))
        open(os.path.join(self.run, rec, 'STAGES.tsv'), 'w').write('stage\trc\ngrade_%s\t0\nend\t0\n' % v)
        row = [job, sha16(os.path.join(self.run, job)), 'GRADE', IDEA, v, 'Q_V1', rec, '-', '-']
        open(os.path.join(self.run, 'registers', 'RUNS.tsv'), 'a').write('\t'.join(row) + '\n')


def mark(twin):
    return 'HOLDOUT re-grade of %s %s, same definition, orchestrator, not a new try' % (IDEA, twin)


class TestHeldoutBudget(unittest.TestCase):
    def setUp(self):
        base = '<SCRATCH_DISK>/tmp_SCOUT' if os.path.isdir('<SCRATCH_DISK>/tmp_SCOUT') else None
        self.tmp = tempfile.TemporaryDirectory(prefix='qj_scout_test_', dir=base)
        f = self.f = Fixture(self.tmp.name)
        Q.CFG['H'] = f.h; Q.CFG['KIT'] = f.kit
        self.tpl0 = Q.TEMPLATE_NAME['GRADE']
        Q.TEMPLATE_NAME['GRADE'] = 'T_HELDOUT.job.sh.txt'          # the job being filed grades the held-out block
        self.da = f.defn('A', 1)
        for v, k in (('A', 1), ('B', 2), ('C', 3)):                 # three graded tries on the design block: the budget is spent
            f.variant(v, self.da if v == 'A' else f.defn(v, k)); f.graded(v, DESIGN_END)

    def tearDown(self):
        Q.TEMPLATE_NAME['GRADE'] = self.tpl0
        self.tmp.cleanup()

    def plan(self, v):
        return Q.plan(self.f.run, 'GRADE', IDEA, v, None)

    def test_a_fourth_normal_variant_refused(self):
        self.f.variant('D', self.f.defn('D', 4))
        with self.assertRaisesRegex(Q.Refused, 'TRY BUDGET: 4 graded variants'):
            self.plan('D')

    def test_b_heldout_same_def_allowed(self):
        self.f.variant('AH', self.da, mark('A'))
        self.assertEqual(self.plan('AH')[1], ['AH'])

    def test_b2_byte_identical_copy_allowed_and_later_ones_too(self):
        """HELDOUT.md seals a byte-identical copy under its own name; after it is graded, a second held-out re-grade still files,
        and a normal 4th try is still refused"""
        cp = 'ideas/%s/defs/AH.json' % IDEA
        open(os.path.join(self.f.run, cp), 'wb').write(open(os.path.join(self.f.run, self.da), 'rb').read())
        self.f.variant('AH', cp, mark('A')); self.f.graded('AH', HELDOUT_END)
        self.f.variant('BH', 'ideas/%s/defs/B.json' % IDEA, mark('B'))
        self.assertEqual(self.plan('BH')[1], ['BH'])
        self.f.variant('D', self.f.defn('D', 4))
        with self.assertRaisesRegex(Q.Refused, 'TRY BUDGET'):
            self.plan('D')

    def test_c_heldout_different_def_refused(self):
        self.f.variant('AX', self.f.defn('AX', 9), mark('A'))
        with self.assertRaisesRegex(Q.Refused, 'HOLDOUT RE-GRADE AX .*def_sha16 .* differs'):
            self.plan('AX')

    def test_d_heldout_mark_on_non_heldout_block_refused(self):
        Q.TEMPLATE_NAME['GRADE'] = 'T_DESIGN.job.sh.txt'            # the job would grade the same block as the twin
        self.f.variant('AH', self.da, mark('A'))
        with self.assertRaisesRegex(Q.Refused, 'NON-HELD-OUT BLOCK'):
            self.plan('AH')

    def test_e_mark_naming_ungraded_twin_refused(self):
        self.f.variant('ZH', self.da, mark('Z'))
        with self.assertRaisesRegex(Q.Refused, 'twin Z is not a graded variant'):
            self.plan('ZH')

    def test_f_v16_scout_and_launcher_load_pinned(self):
        q16 = load('queue_job_v16_scout', os.path.join(HERE, 'queue_job_v16_scout.py'))
        self.assertTrue(q16.V15.endswith('queue_job_v15_scout.py'))
        pm = load('pipe_mac_v3_heldout', os.path.join(HERE, 'pipe_mac_v3_heldout.py'))
        self.assertEqual(pm.M.QJ16, os.path.join(HERE, 'queue_job_v16_scout.py'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
