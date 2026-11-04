"""test_run_isolated_v2.py (SCOUT 30 Oct 2026): the RUN proof on planted folders with known answers. A sandbox Alarm package (its
_tools/settings_v1.py and run_isolated_v2.py copied from this package, a settings example with the data keys) and a forbidden 'dev'
folder outside it holding research data, a dev tool, a job template and other files. A script inside the package that opens a data
file under RESEARCH_ROOT passes; one that opens dev code, a job template or a file under no key fails; a module imported from the dev
folder fails; refusals (no settings, a bad settings file, a script outside the package); the script's own exit code passes through.
  python3 -B _tools/tests/test_run_isolated_v2.py"""
import os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
KEYS = ('PYTHON', 'LAB_DAYS', 'RESEARCH_STORE', 'HL_FILLS', 'SCRATCH', 'RESEARCH_ROOT', 'RUNNER_QUEUES', 'FORBID', 'BOARD', 'FEED_GATE')


class Run(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); d = self.d
        self.alarm = os.path.join(d, 'Alarm'); os.makedirs(os.path.join(self.alarm, '_tools')); os.makedirs(os.path.join(self.alarm, 'settings'))
        for f in ('settings_v1.py', 'run_isolated_v2.py'):
            shutil.copy(os.path.join(TOOLS, f), os.path.join(self.alarm, '_tools', f))
        with open(os.path.join(self.alarm, 'settings', 'SETTINGS_EXAMPLE.env'), 'w') as f:
            f.write('# example\n' + ''.join('%s=\n' % k for k in KEYS))
        self.dev = os.path.join(d, 'dev'); self.res = os.path.join(self.dev, 'research')
        os.makedirs(os.path.join(self.res, 'tools')); os.makedirs(os.path.join(self.dev, 'other'))
        for rel, body in (('research/runs.tsv', 'a\tb\n'), ('research/tools/devtool.py', 'X = 1\n'), ('research/JOB_X_V1.job.sh.txt', 'echo\n'),
                          ('other/y.tsv', 'c\n')):
            with open(os.path.join(self.dev, rel), 'w') as f:
                f.write(body)
        self.settings = os.path.join(d, 'SETTINGS_T.env')
        with open(self.settings, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, {'RESEARCH_ROOT': self.res, 'FORBID': self.dev}.get(k, '')) for k in KEYS))

    def tearDown(self):
        shutil.rmtree(self.d)

    def script(self, body, name='s.py'):
        p = os.path.join(self.alarm, name)
        with open(p, 'w') as f:
            f.write('import sys\n' + body + '\n')
        return p

    def run_it(self, script, settings=True, extra=()):
        a = [sys.executable, '-B', os.path.join(self.alarm, '_tools', 'run_isolated_v2.py')] + (['--settings', self.settings] if settings else [])
        a += ['--forbid', self.dev] + list(extra) + [script]
        r = subprocess.run(a, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_data_under_a_key_passes(self):
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(self.res, 'runs.tsv')))
        self.assertEqual(rc, 0, out); self.assertIn('RUN ISOLATION OK', out); self.assertIn('1 data files', out)

    def test_dev_code_fails(self):
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(self.res, 'tools', 'devtool.py')))
        self.assertEqual(rc, 3, out); self.assertIn('devtool.py', out)

    def test_job_template_fails(self):
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(self.res, 'JOB_X_V1.job.sh.txt')))
        self.assertEqual(rc, 3, out)

    def test_file_under_no_key_fails(self):
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(self.dev, 'other', 'y.tsv')))
        self.assertEqual(rc, 3, out); self.assertIn('y.tsv', out)

    def test_module_from_dev_fails(self):
        rc, out = self.run_it(self.script('sys.path.insert(0, %r)\nimport devtool' % os.path.join(self.res, 'tools')))
        self.assertEqual(rc, 3, out); self.assertIn('modules from outside', out)

    def test_exit_code_passes_through(self):
        rc, out = self.run_it(self.script('open(%r).read()\nsys.exit(5)' % os.path.join(self.res, 'runs.tsv')))
        self.assertEqual(rc, 5, out); self.assertIn('script exit 5', out)

    def test_refusals(self):
        s = self.script('pass')
        rc, out = self.run_it(s, settings=False)                                            # no settings file named: the usage
        self.assertEqual(rc, 2); self.assertIn('--settings <settings file>', out); self.assertNotIn('REFUSED SETTINGS', out)
        with open(self.settings, 'w') as f:
            f.write('PYTHON=\n')                                                             # keys missing
        rc, out = self.run_it(s); self.assertEqual(rc, 2, out); self.assertIn('REFUSED SETTINGS', out)
        outside = os.path.join(self.d, 'outside.py')
        with open(outside, 'w') as f:
            f.write('pass\n')
        with open(self.settings, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, {'RESEARCH_ROOT': self.res}.get(k, '')) for k in KEYS))
        self.assertEqual(self.run_it(outside)[0], 2)                                       # a script outside the package

    def test_files_outside_forbid_are_free(self):
        p = os.path.join(self.d, 'free.tsv')
        with open(p, 'w') as f:
            f.write('x\n')
        rc, out = self.run_it(self.script('open(%r).read()' % p))
        self.assertEqual(rc, 0, out); self.assertIn('0 data files', out)

    def test_interpreter_files_do_not_count(self):
        # the Mac's Python lives inside the dev tree: its own files, opened by an import, are no breach even under a forbidden root
        a = [sys.executable, '-B', os.path.join(self.alarm, '_tools', 'run_isolated_v2.py'), '--settings', self.settings,
             '--forbid', self.dev, '--forbid', os.path.realpath(sys.base_prefix),
             self.script('import json, csv, decimal\nopen(%r).read()' % os.path.join(self.res, 'runs.tsv'))]
        r = subprocess.run(a, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_module_from_anywhere_else_fails(self):
        # a module from a folder that is neither the package, the interpreter nor a forbidden root: still a breach of (1)
        lib = os.path.join(self.d, 'lib'); os.makedirs(lib)
        with open(os.path.join(lib, 'elsewhere_mod.py'), 'w') as f:
            f.write('Y = 2\n')
        rc, out = self.run_it(self.script('sys.path.insert(0, %r)\nimport elsewhere_mod' % lib))
        self.assertEqual(rc, 3, out); self.assertIn('elsewhere_mod.py', out)

    def test_forbid_comes_from_the_settings(self):
        # no --forbid: the settings' FORBID is the forbidden root, so dev code still fails and data under a key still passes
        a = lambda body: subprocess.run([sys.executable, '-B', os.path.join(self.alarm, '_tools', 'run_isolated_v2.py'), '--settings',
                                         self.settings, self.script(body)], capture_output=True, text=True)
        self.assertEqual(a('open(%r).read()' % os.path.join(self.res, 'tools', 'devtool.py')).returncode, 3)
        self.assertEqual(a('open(%r).read()' % os.path.join(self.res, 'runs.tsv')).returncode, 0)

    def test_forbid_folders_split_on_colons(self):
        # FORBID names two folders, as run_all_tests_v1 reads it: the dev folder is still forbidden
        with open(self.settings, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, {'RESEARCH_ROOT': self.res, 'FORBID': os.path.join(self.d, 'elsewhere') + ':' + self.dev}.get(k, ''))
                            for k in KEYS))
        r = subprocess.run([sys.executable, '-B', os.path.join(self.alarm, '_tools', 'run_isolated_v2.py'), '--settings', self.settings,
                            self.script('open(%r).read()' % os.path.join(self.res, 'tools', 'devtool.py'))], capture_output=True, text=True)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)

    def test_no_forbidden_folder_refused(self):
        # no --forbid and an empty FORBID: refused, never a proof that checked nothing
        with open(self.settings, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, {'RESEARCH_ROOT': self.res}.get(k, '')) for k in KEYS))
        r = subprocess.run([sys.executable, '-B', os.path.join(self.alarm, '_tools', 'run_isolated_v2.py'), '--settings', self.settings,
                            self.script('pass')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn('NO FORBIDDEN FOLDER', r.stdout)

    def test_past_editions_are_never_run(self):
        # a file or module in an archive/ folder of the package fails; an archive/ folder in the data is data
        arch = os.path.join(self.alarm, 'P', 'tools', 'archive'); os.makedirs(arch)
        with open(os.path.join(arch, 'old_v1.py'), 'w') as f:
            f.write('Z = 1\n')
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(arch, 'old_v1.py')))
        self.assertEqual(rc, 3, out); self.assertIn('old_v1.py', out); self.assertIn('archive', out)
        rc, out = self.run_it(self.script('sys.path.insert(0, %r)\nimport old_v1' % arch))
        self.assertEqual(rc, 3, out); self.assertIn('old_v1.py', out)
        # a module whose file lies in archive/ but was loaded without an open (as an extension module is): still caught
        rc, out = self.run_it(self.script('import types\nm = types.ModuleType("ext_v1")\nm.__file__ = %r\nsys.modules["ext_v1"] = m'
                                          % os.path.join(arch, 'ext_v1.so')))
        self.assertEqual(rc, 3, out); self.assertIn('ext_v1.so', out)
        os.makedirs(os.path.join(self.res, 'archive'))
        with open(os.path.join(self.res, 'archive', 'r.tsv'), 'w') as f:
            f.write('r\n')
        rc, out = self.run_it(self.script('open(%r).read()' % os.path.join(self.res, 'archive', 'r.tsv')))
        self.assertEqual(rc, 0, out); self.assertIn('no past edition', out)

    def test_the_feed_gate_file_is_data(self):
        # FEED_GATE names one file inside the dev tree (the feed's stop gate): reading it is data, reading its folder's other files is not
        gate = os.path.join(self.dev, 'other', 'BACKFILL_GATE.txt')
        with open(gate, 'w') as f:
            f.write('RUN\n')
        with open(self.settings, 'w') as f:
            f.write(''.join('%s=%s\n' % (k, {'RESEARCH_ROOT': self.res, 'FORBID': self.dev, 'FEED_GATE': gate}.get(k, '')) for k in KEYS))
        self.assertEqual(self.run_it(self.script('open(%r).read()' % gate))[0], 0)
        self.assertEqual(self.run_it(self.script('open(%r).read()' % os.path.join(self.dev, 'other', 'y.tsv')))[0], 3)

    def test_a_key_prefix_is_not_its_root(self):
        # research2 starts with the characters of research but is another folder: under no key
        os.makedirs(os.path.join(self.dev, 'research2'))
        p = os.path.join(self.dev, 'research2', 'z.tsv')
        with open(p, 'w') as f:
            f.write('z\n')
        self.assertEqual(self.run_it(self.script('open(%r).read()' % p))[0], 3)


if __name__ == '__main__':
    unittest.main(verbosity=1)
