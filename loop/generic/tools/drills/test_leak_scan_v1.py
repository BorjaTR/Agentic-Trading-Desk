#!/usr/bin/env python3
"""test_leak_scan_v1.py (SCOUT 2026-11-08, C104): planted secrets and targets; temp files on SCRATCH_DISK only.  python3 -B test_leak_scan_v1.py"""
import importlib.util, json, os, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/scout_keep/test_tmp')
sp = importlib.util.spec_from_file_location('ls1', os.path.join(HERE, 'leak_scan_v1.py')); ls = importlib.util.module_from_spec(sp); sp.loader.exec_module(ls)
PACKS = os.path.join(HERE, '..', '..', '..', 'packs')
ALARM_PAT = os.environ.get('LEAK_SCAN_PATTERN_FILE', os.path.join(PACKS, 'alarm', 'HELDOUT_PATTERN.txt'))
BUILDER = os.path.join(PACKS, 'alarm', 'tools', 'build_run_v2.py')
if not os.path.isfile(BUILDER): BUILDER = os.path.join(HERE, 'build_run_v2.py')   # C218: the alarm seat source sits beside its builder
def builder_rx():
    s = importlib.util.spec_from_file_location('brv2t', BUILDER); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.HELDOUT_RX
class T(unittest.TestCase):
    def setUp(self):
        os.makedirs(BASE, exist_ok=True); self.t = tempfile.mkdtemp(dir=BASE)
        self.pat = ALARM_PAT if os.path.isfile(ALARM_PAT) else self.w('pack/HELDOUT_PATTERN.txt', builder_rx().pattern + '\n')   # C218: the source has no pattern file: today's builder pattern
        ls.load_pattern(self.pat)   # RC2: the alarm pack's pattern
    def tearDown(self):
        shutil.rmtree(self.t)
    def w(self, rel, txt):
        p = os.path.join(self.t, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(txt); return p
    def test_plants(self):
        s1 = self.w('sec/RESULT.md', 'L03 R3: +23.17, margin +21.33 on 412 waves\n')
        s2 = self.w('sec/Y.json', json.dumps({'yardstick_heldout_febmar': {'lead15': 3.1415, 'waves': 777}}))
        sec = ls.secrets([s1, s2])
        self.assertTrue({'+23.17', '+21.33', '412 waves', '+3.14', '777 waves'} <= sec)
        self.w('read/CARD.md', 'R1 lead +12.30 on 500 waves\n')                     # clean
        self.w('read/BRIEF.md', 'a line\nthe held-out lead was +23.17\n')            # number leak, line 2
        self.w('read/ASSESS.tsv', 'x\tlead_2602 0.5\n')                              # marker
        self.w('read/pipe_r1/GRADES.tsv', '+23.17\n')                                # tool output folder: skipped
        self.w('read/note.md', 'value 123.17 and +23.171 are not the secret\n')      # boundaries
        hits = ls.scan([os.path.join(self.t, 'read')], sec)
        got = sorted((os.path.basename(f), i, k) for f, i, k in hits)
        self.assertEqual(got, [('ASSESS.tsv', 1, 'MARKER'), ('BRIEF.md', 2, 'NUMBER')])
    def test_allow_drops_design_numbers(self):
        s1 = self.w('sec/RESULT.md', 'FDONLY Sep-Jan +8.09; Feb-Mar lead +23.17\n'); a1 = self.w('allow/EVIDENCE.tsv', 'E1\t8.09\t1235 waves\n')
        sec = ls.secrets([s1]) - ls.allowed([a1]); self.assertIn('+23.17', sec); self.assertNotIn('+8.09', sec)
    def test_marker_and_number_both_reported(self):
        s1 = self.w('sec/R.md', 'Feb-Mar +23.17\n'); self.w('read2/H.md', 'yardstick_heldout_febmar is +23.17\n')
        hits = ls.scan([os.path.join(self.t, 'read2')], ls.secrets([s1])); self.assertEqual([k for _, _, k in hits], ['NUMBER+MARKER'])
    @unittest.skipUnless(os.path.isfile(BUILDER), 'alarm builder absent: pattern equality is an alarm pack check')
    def test_alarm_pattern_file_equals_builder(self):   # RC2 C215: the pack file is today's builder pattern
        self.assertEqual(ls.load_pattern(self.pat).pattern, builder_rx().pattern)
    def test_other_pack_pattern(self):   # RC2 C215: a second pack's pattern replaces the alarm one
        p = self.w('pack/PAT.txt', '# planted strategy pack pattern\nstrategy_heldout|HOLDOUT_2604\n'); ls.load_pattern(p)
        self.w('read3/A.md', 'x strategy_heldout y\n'); self.w('read3/B.md', 'lead_2602 is an alarm marker only\n')
        hits = ls.scan([os.path.join(self.t, 'read3')], set()); self.assertEqual([(os.path.basename(f), k) for f, _, k in hits], [('A.md', 'MARKER')])
    def test_main_refuses_without_pattern(self):
        old = os.environ.pop('LEAK_SCAN_PATTERN_FILE', None); rx = ls.MARKER_RX; ls.MARKER_RX = None   # C218: as in a copy with no builder beside it
        try:
            s = self.w('s/R.md', '+1.11\n'); self.assertEqual(ls.main(['--secrets', s, '--targets', s]), 2)
        finally:
            ls.MARKER_RX = rx
            if old is not None: os.environ['LEAK_SCAN_PATTERN_FILE'] = old
    def test_main_with_pattern_file(self):
        s = self.w('s/R.md', 'held-out +7.77\n'); t = self.w('t/C.md', 'lead_2602\n')
        self.assertEqual(ls.main(['--pattern-file', self.pat, '--secrets', s, '--targets', t]), 3)
if __name__ == '__main__':
    unittest.main(verbosity=1)
