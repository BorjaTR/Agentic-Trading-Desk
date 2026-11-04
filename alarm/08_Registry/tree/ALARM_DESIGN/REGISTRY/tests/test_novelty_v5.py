#!/usr/bin/env python3
"""test_novelty_v5.py (SCOUT, 3 Nov 2026, ALARM_V1_21_10): test_novelty_v4.py on novelty_v5.py, with its one changed rule: --show-lean with
a registry id is accepted (it was refused) and --show-lean without --show is refused with what to add. test_novelty_v4.py (SCOUT, 2 Nov
2026, V1_18_FIXES; RESULTS_R5 item 4): --show by a fire list path, through the command, on a planted registry and settings. Needs an Alarm folder above. TOOL_UNDER_TEST names the tool file."""
import os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ.get('TOOL_UNDER_TEST') or os.path.join(HERE, '..', 'tools', 'novelty_v5.py')
T0 = 1757500000


def fires(ts, coin='BTC', side=1):
    return 'coin\tt\tside\n' + ''.join('%s\t%d\t%d\n' % (coin, t, side) for t in ts)


class Show(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory(); r = self.d.name; self.h = os.path.join(r, 'ALARM_DESIGN'); os.makedirs(os.path.join(self.h, 'REGISTRY'))
        d = HERE
        while not os.path.isfile(os.path.join(d, 'settings', 'SETTINGS_EXAMPLE.env')):
            d = os.path.dirname(d)
        keys = [l.split('=', 1)[0] for l in open(os.path.join(d, 'settings', 'SETTINGS_EXAMPLE.env')) if '=' in l and not l.lstrip().startswith('#')]
        self.S = os.path.join(r, 'S.env')
        with open(self.S, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, r if k == 'RESEARCH_ROOT' else '') for k in keys))
        self.new = self.w('NEW.tsv', fires([T0 + i * 86400 for i in range(10)]))
        self.w('REG_LIST.tsv', fires([T0 + 50 * 86400 + i * 86400 for i in range(10)], 'ETH'))
        with open(os.path.join(self.h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), 'w') as f:
            f.write('alarm_id\tseat\tidea\tkind\tstate\tlean\tfire_list_rel\nREG1\tX\tR\tOWN\tSTOP\tFADE\tREG_LIST.tsv\n')

    def tearDown(self):
        self.d.cleanup()

    def w(self, n, t):
        p = os.path.join(self.h, n)
        with open(p, 'w') as f:
            f.write(t)
        return p

    def run_(self, *a):
        p = subprocess.run([sys.executable, '-B', TOOL, '--settings', self.S] + list(a), capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def show(self, out):
        return [l for l in out.split('\n') if l.startswith('show:')]

    def test_school_alarm_by_absolute_path(self):
        p = self.w('SCHOOL.tsv', fires([T0 + i * 86400 for i in range(10)]))
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', p)
        self.assertEqual(rc, 0, err); s = self.show(out); self.assertEqual(len(s), 1)
        self.assertIn(p, s[0]); self.assertIn('same fires 100.0 pct', s[0]); self.assertIn('same side 100.0 pct', s[0])

    def test_relative_path_reads_under_design_root(self):
        self.w('SCHOOL.tsv', fires([T0]))
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'SCHOOL.tsv')
        self.assertEqual(rc, 0, err); self.assertIn('same fires 10.0 pct', self.show(out)[0])

    def test_show_lean_flips_to_other_side(self):
        p = self.w('SCHOOL.tsv', fires([T0 + i * 86400 for i in range(10)]))
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', p, '--show-lean', 'FOLLOW')
        self.assertEqual(rc, 0, err); self.assertIn('other side 100.0 pct', self.show(out)[0])

    def test_shown_list_never_moves_the_verdict(self):
        base = self.run_(self.new, '--lean', 'FADE')[1]
        p = self.w('SCHOOL.tsv', fires([T0 + i * 86400 for i in range(10)]))
        out = self.run_(self.new, '--lean', 'FADE', '--show', p)[1]
        v = lambda o: [l for l in o.split('\n') if l.startswith('VERDICT')]
        self.assertEqual(v(base), v(out)); self.assertIn('VERDICT NEW', out)
        self.assertIn('against 1 registry alarms', out)

    def test_registry_id_still_works_and_unknown_refused(self):
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'REG1')
        self.assertEqual(rc, 0, err); self.assertIn('show: REG1', out)
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'SCOUT_SIDEDHOUR')
        self.assertEqual(rc, 2); self.assertIn('fire list path', err)

    def test_pointer_or_missing_path_refused(self):
        p = self.w('FIRES.tsv', 'V1\t3108\t600fed79bbebf800\t/x/V1_FIRES_V1_LIST.tsv\n')
        self.assertEqual(self.run_(self.new, '--lean', 'FADE', '--show', p)[0], 2)
        self.assertEqual(self.run_(self.new, '--lean', 'FADE', '--show', os.path.join(self.h, 'none.tsv'))[0], 2)

    def test_show_lean_rules(self):
        p = self.w('SCHOOL.tsv', fires([T0]))
        self.assertEqual(self.run_(self.new, '--lean', 'FADE', '--show', p, '--show-lean', 'BOTH')[0], 2)
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show-lean', 'FADE')
        self.assertEqual(rc, 2); self.assertIn('NEEDS --show <ALARM_ID or fire list path>', err)

    def test_show_lean_with_a_registry_id(self):
        self.w('REG2_LIST.tsv', fires([T0 + i * 86400 for i in range(10)]))
        with open(os.path.join(self.h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), 'a') as f:
            f.write('REG2\tX\tR2\tOWN\tSTOP\tFADE\tREG2_LIST.tsv\n')
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'REG2')
        self.assertEqual(rc, 0, err); self.assertIn('same side 100.0 pct', self.show(out)[0])
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'REG2', '--show-lean', 'FOLLOW')
        self.assertEqual(rc, 0, err); s = self.show(out)[0]
        self.assertIn('REG2 with lean FOLLOW (registry lean FADE)', s); self.assertIn('other side 100.0 pct', s)
        v = lambda o: [l for l in o.split('\n') if l.startswith('VERDICT') or l.startswith('nearest')]
        self.assertEqual(v(out), v(self.run_(self.new, '--lean', 'FADE')[1]))   # a shown alarm never moves the verdict
        rc, out, err = self.run_(self.new, '--lean', 'FADE', '--show', 'NOSUCH', '--show-lean', 'FOLLOW')
        self.assertEqual(rc, 2); self.assertIn('fire list path', err)


if __name__ == '__main__':
    unittest.main()
