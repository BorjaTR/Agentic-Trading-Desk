"""test_settings_v1.py (SCOUT, 30 Oct 2026): the settings reader of the Alarm package (KEY=VALUE files, protocol V4.12 H4), smallest first.
  python3 -B _tools/tests/test_settings_v1.py      (from Alarm; no data, no network; temp files only)"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import settings_v1 as S  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='settings_v1_test_')
        self.keys = S.keys()
        self.vals = {}
        for k in self.keys:
            p = os.path.join(self.d, 'data', k.lower())
            os.makedirs(p)
            self.vals[k] = p

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, rows=None, extra=''):
        rows = [(k, self.vals[k]) for k in self.keys] if rows is None else rows
        p = os.path.join(self.d, 'SETTINGS_TEST.env')
        with open(p, 'w') as f:
            f.write('# a comment\n\n' + ''.join('%s=%s\n' % r for r in rows) + extra)
        return p

    def with_first(self, value, i=0):
        return self.write([(k, value if j == i else self.vals[k]) for j, k in enumerate(self.keys)])

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = S.main(list(argv))
        return rc, out.getvalue(), err.getvalue()


class T01Example(Base):
    def test_example_is_a_valid_settings_file(self):
        rows = S.read_env(S.EXAMPLE)
        self.assertGreaterEqual(len(rows), 6)
        for k in rows:
            self.assertRegex(k, r'^[A-Z][A-Z0-9_]*$')
        self.assertEqual(list(S.load(S.EXAMPLE)), self.keys)

    def test_the_owners_mac_file_is_complete(self):
        p = os.path.join(S.ALARM, 'settings', 'SETTINGS_LOCAL.env')
        s = S.load(p)
        self.assertEqual(list(s), self.keys)
        self.assertTrue(all(v.startswith(('/Users/', '/Volumes/')) for v in s.values() if v))


class T02Get(Base):
    def test_get_returns_the_value(self):
        p = self.write()
        for k in self.keys:
            self.assertEqual(S.get(p, k), self.vals[k])

    def test_comments_and_blank_lines_skipped(self):
        p = self.write(extra='\n# trailing comment\n')
        self.assertEqual(S.get(p, self.keys[0]), self.vals[self.keys[0]])

    def test_values_are_normalized(self):
        p = self.with_first(self.vals[self.keys[0]] + '//')
        self.assertEqual(S.get(p, self.keys[0]), self.vals[self.keys[0]])

    def test_empty_value_is_allowed_but_get_refuses_it(self):
        p = self.with_first('')
        self.assertEqual(S.load(p)[self.keys[0]], '')
        with self.assertRaises(S.Refused) as cm:
            S.get(p, self.keys[0])
        self.assertIn('EMPTY %s' % self.keys[0], str(cm.exception))


class T03Refused(Base):
    def assertRefused(self, fn, text):
        with self.assertRaises(S.Refused) as cm:
            fn()
        self.assertIn(text, str(cm.exception))

    def test_no_file(self):
        self.assertRefused(lambda: S.load(os.path.join(self.d, 'nothing.env')), 'NO SETTINGS FILE')

    def test_not_key_value(self):
        p = self.write(extra='LAB_DAYS /x\n')
        self.assertRefused(lambda: S.load(p), 'NOT KEY=VALUE')
        p = self.write(extra='export X=/x\n')
        self.assertRefused(lambda: S.load(p), 'NOT KEY=VALUE')

    def test_missing_key(self):
        p = self.write([(k, self.vals[k]) for k in self.keys[1:]])
        self.assertRefused(lambda: S.load(p), 'KEYS MISSING %s' % self.keys[0])

    def test_unknown_key(self):
        p = self.write(extra='NOT_A_KEY=%s\n' % self.d)
        self.assertRefused(lambda: S.load(p), 'UNKNOWN KEYS NOT_A_KEY')

    def test_key_twice(self):
        p = self.write(extra='%s=%s\n' % (self.keys[0], self.d))
        self.assertRefused(lambda: S.load(p), 'KEY TWICE %s' % self.keys[0])

    def test_lower_case_key(self):
        p = self.write(extra='lab_days=%s\n' % self.d)
        self.assertRefused(lambda: S.load(p), 'NOT KEY=VALUE')

    def test_relative_tilde_variable_quoted_or_spaced(self):
        for bad in ('data/x', '~/x', '$HOME/x', '"/x"', ' /x', '/x '):
            p = self.with_first(bad)
            self.assertRefused(lambda: S.load(p), 'NOT AN ABSOLUTE PATH %s' % self.keys[0])

    def test_data_inside_the_alarm_folder(self):
        for bad in (S.ALARM, os.path.join(S.ALARM, '05_Profile'), os.path.join(S.ALARM, 'x', '..', 'settings')):
            p = self.with_first(bad, 1)
            self.assertRefused(lambda: S.load(p), 'DATA INSIDE ALARM %s' % self.keys[1])

    def test_a_sibling_folder_is_not_inside(self):
        p = self.with_first(S.ALARM + '_data')
        self.assertEqual(S.load(p)[self.keys[0]], S.ALARM + '_data')

    def test_no_such_key(self):
        p = self.write()
        self.assertRefused(lambda: S.get(p, 'NOPE'), 'NO SUCH KEY NOPE')
        self.assertRefused(lambda: S.check(p, ['NOPE']), 'NO SUCH KEY NOPE')


class T04Check(Base):
    def test_all_ok_exit_0(self):
        p = self.write()
        rc, out, _ = self.run_main('check', p)
        self.assertEqual(rc, 0)
        self.assertEqual(out.count('OK '), len(self.keys))
        self.assertIn('0 not OK', out)

    def test_missing_and_empty_exit_3(self):
        os.rmdir(self.vals[self.keys[2]])
        p = self.write([(k, '' if i == 3 else self.vals[k]) for i, k in enumerate(self.keys)])
        rc, out, _ = self.run_main('check', p)
        self.assertEqual(rc, 3)
        self.assertIn('MISSING  %s' % self.keys[2], out)
        self.assertIn('EMPTY    %s' % self.keys[3], out)
        self.assertIn('2 not OK', out)

    def test_named_keys_only(self):
        os.rmdir(self.vals[self.keys[2]])
        p = self.write()
        rc, out, _ = self.run_main('check', p, '%s,%s' % (self.keys[0], self.keys[1]))
        self.assertEqual(rc, 0)
        self.assertNotIn(self.keys[2], out)
        self.assertEqual(self.run_main('check', p, self.keys[2])[0], 3)

    def test_cli_get_and_refusals_exit_2(self):
        p = self.write()
        rc, out, _ = self.run_main('get', p, self.keys[0])
        self.assertEqual((rc, out.strip()), (0, self.vals[self.keys[0]]))
        rc, _, err = self.run_main('get', p, 'NOPE')
        self.assertEqual(rc, 2)
        self.assertIn('REFUSED NO SUCH KEY', err)
        self.assertEqual(self.run_main('check', os.path.join(self.d, 'nothing.env'))[0], 2)

    def test_usage_exit_2(self):
        for argv in ((), ('get',), ('check',), ('nope', 'x'), ('get', 'f'), ('get', 'f', 'A', 'B')):
            self.assertEqual(self.run_main(*argv)[0], 2, argv)


class T05Root(Base):
    def test_alarm_root_from_inside(self):
        self.assertEqual(S.alarm_root(__file__), S.ALARM)
        self.assertEqual(S.alarm_root(os.path.join(S.ALARM, '_tools')), S.ALARM)

    def test_alarm_root_from_outside_refused(self):
        with self.assertRaises(S.Refused):
            S.alarm_root(self.d)


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    print('TESTS %d, failures %d, errors %d' % (r.testsRun, len(r.failures), len(r.errors)))
    sys.exit(0 if r.wasSuccessful() else 1)
