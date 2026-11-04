"""test_machine_paths_v1.py (SCOUT 30 Oct 2026): the STATIC proof on planted parts with known answers: a machine path in Python code
is CODE, in a docstring or comment TEXT; in a shell command CODE, in a shell comment TEXT; in a job template CODE on every line (the
runner reads its header); in JSON CODE; in a document TEXT; /tmp is no machine path; the MANIFEST rows decide what is scanned (--all:
every file); refusals; the exit codes.
  python3 -B _tools/tests/test_machine_paths_v1.py"""
import contextlib, io, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import machine_paths_v1 as MP

U = '/Use' + 'rs/owner/dev'                     # split so this test file names no machine path itself
V = '/Vol' + 'umes/SCRATCH_DISK'

PY = ('"""a tool: reads %s/x.tsv by default (a docstring: TEXT)"""\n'
      'import os\n'
      'F = "%s/forensics"   # the dev root (the string is CODE)\n'
      '# %s/old (a comment: TEXT)\n'
      'def f():\n'
      '    """%s/doc (a function docstring: TEXT)"""\n'
      '    return os.path.expanduser("~/mnt/dev")\n'
      'T = "/tmp/x"\n') % (U, U, U, U)
SH = '#!/bin/bash\n# %s/notes (TEXT)\ncd %s && python3 x.py\nW=%s/judge_scratch\n' % (U, U, V)
JOB = '# QUEUE: Q_V1\n# WRITES %s/judge_scratch/work_X\ncd @@ALARM@@\n' % V
JS = '{"pins": {"a.py": "%s/forensics/a.py"}}\n' % U
MD = '# A doc\nThe data lives in %s/x (TEXT).\n' % U


class Part(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for name, body in (('tool.py', PY), ('run.sh', SH), ('JOB_X_V1.job.sh.txt', JOB), ('PINS.json', JS), ('README.md', MD),
                           ('clean.py', 'import os\nX = "/tmp/a"\n')):
            with open(os.path.join(self.d, name), 'w') as f:
                f.write(body)
        with open(os.path.join(self.d, 'MANIFEST.tsv'), 'w') as f:
            f.write('# a part\nrepo_path\tdev_path\trole\n' + ''.join('%s\tx\ty\n' % n for n in
                                                                   ('tool.py', 'run.sh', 'JOB_X_V1.job.sh.txt', 'PINS.json', 'README.md', 'clean.py')))

    def tearDown(self):
        shutil.rmtree(self.d)

    def kinds(self, name):
        rows, _ = MP.scan(self.d)
        return [(r[1], r[3]) for r in rows if r[0] == name]

    def test_python(self):
        self.assertEqual(self.kinds('tool.py'), [(1, 'TEXT'), (3, 'CODE'), (4, 'TEXT'), (6, 'TEXT'), (7, 'CODE')])

    def test_shell(self):
        self.assertEqual(self.kinds('run.sh'), [(2, 'TEXT'), (3, 'CODE'), (4, 'CODE')])

    def test_job_template_header_counts(self):
        self.assertEqual(self.kinds('JOB_X_V1.job.sh.txt'), [(2, 'CODE')])

    def test_json_and_docs(self):
        self.assertEqual(self.kinds('PINS.json'), [(1, 'CODE')]); self.assertEqual(self.kinds('README.md'), [(2, 'TEXT')])

    def test_release_record_is_text(self):
        with open(os.path.join(self.d, 'RELEASE_X_V1.json'), 'w') as f:
            f.write('{"python": "%s/venvs/analyst/bin/python3"}\n' % U)
        self.assertEqual([(r[1], r[3]) for r in MP.scan(self.d, every=True)[0] if r[0] == 'RELEASE_X_V1.json'], [(1, 'TEXT')])

    def test_tmp_is_no_machine_path(self):
        self.assertEqual(self.kinds('clean.py'), [])

    def test_paths_found(self):
        rows, n = MP.scan(self.d)
        self.assertEqual(n, 6)
        self.assertIn('~/mnt/dev', [r[2] for r in rows]); self.assertIn(V + '/judge_scratch', [r[2] for r in rows])
        self.assertIn(U + '/forensics', [r[2] for r in rows])

    def test_manifest_decides(self):
        with open(os.path.join(self.d, 'extra.py'), 'w') as f:
            f.write('X = "%s/a"\n' % U)
        self.assertNotIn('extra.py', [r[0] for r in MP.scan(self.d)[0]])
        self.assertIn('extra.py', [r[0] for r in MP.scan(self.d, every=True)[0]])

    def test_exit_codes_and_out(self):
        out = os.path.join(self.d, 'rows.tsv')
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.d, '--tsv', out]), 1)
        self.assertIn('NOT CLEAN', s.getvalue()); self.assertTrue(os.path.isfile(out))
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.d, '--tsv', out]), 2)                          # OUT exists
        self.assertIn('REFUSED', s.getvalue())
        c = tempfile.mkdtemp()
        try:
            with open(os.path.join(c, 'MANIFEST.tsv'), 'w') as f:
                f.write('repo_path\tdev_path\trole\nok.py\tx\ty\n')
            with open(os.path.join(c, 'ok.py'), 'w') as f:
                f.write('"""no machine path"""\nimport os\n')
            with contextlib.redirect_stdout(io.StringIO()) as s:
                self.assertEqual(MP.main([c]), 0)
            self.assertIn('CLEAN', s.getvalue())
        finally:
            shutil.rmtree(c)

    def test_refusals(self):
        os.remove(os.path.join(self.d, 'run.sh'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(MP.main([self.d]), 2)                                           # a listed file missing
        os.remove(os.path.join(self.d, 'MANIFEST.tsv'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(MP.main([self.d]), 2)                                           # no MANIFEST without --all
            self.assertEqual(MP.main([self.d, '--all']), 1)

    def test_broken_python_still_scanned(self):
        with open(os.path.join(self.d, 'tool.py'), 'w') as f:
            f.write('def f(:\n    X = "%s/a"\n' % U)
        self.assertEqual(self.kinds('tool.py'), [(2, 'CODE')])


if __name__ == '__main__':
    unittest.main(verbosity=1)
