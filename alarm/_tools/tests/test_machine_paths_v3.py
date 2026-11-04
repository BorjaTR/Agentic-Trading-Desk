"""test_machine_paths_v3.py (SCOUT 31 Oct 2026): test_machine_paths_v2.py 89a42bf667305dda (all its tests, run on machine_paths_v3) plus
class V3: Python imports from the syntax tree (`from pkg.old import x`, `import pkg.old`, `import os, old`, `from . import old` and a
multi-line import call old.py, on the statement's first line; `a, old = f()` and `[1, old]` do not), and a MACHINE_PATHS_KNOWN.tsv row
holding a reference to an archived file (a label, a test's name): KNOWN while the file is unchanged, CALLS_ARCHIVE and STALE once it
changes or when the line is wrong; the verdict CLEAN EXCEPT KNOWN.
v2's text: test_machine_paths_v2.py (SCOUT 30 Oct 2026): the STATIC proof on planted parts with known answers: a machine path in Python code
is CODE, in a docstring or comment TEXT; in a shell command CODE, in a shell comment TEXT; in a job template CODE on every line (the
runner reads its header); in JSON CODE; in a document TEXT; /tmp is no machine path; the MANIFEST rows decide what is scanned (--all:
every file); refusals; the exit codes (all as v1). New in v2: MARKED (a Python comment `machine-path-ok: <reason>` on the string's
first or last line; no reason, a marker inside a string, the wrong line, shell and job templates: still CODE) and KNOWN (a row of
MACHINE_PATHS_KNOWN.tsv while the file's sha16 is unchanged; a changed file or a wrong line: CODE, the row STALE); the verdicts
CLEAN, CLEAN EXCEPT KNOWN and NOT CLEAN; the known table's refusals; the archive (ARCHIVE: a machine path inside archive/, never CODE;
CALLS_ARCHIVE: a current file's code names an archived file, in this part or another part of the Alarm folder, by its name in a
string, a template line or JSON, or a Python import; NAMES_ARCHIVE: the same in a test; docstrings, comments, a name shared with a
current file and a longer name that only contains it are no reference).
  python3 -B _tools/tests/test_machine_paths_v3.py"""
import contextlib, io, os, shutil, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import machine_paths_v3 as MP

U = '/Use' + 'rs/owner/dev'                     # split so this test file names no machine path itself
V = '/Vol' + 'umes/SCRATCH_DISK'

PY = ('"""a tool: reads %s/x.tsv by default (a docstring: TEXT)"""\n'
      'import os\n'
      'F = "%s/forensics"   # the dev root (the string is CODE)\n'
      '# %s/old (a comment: TEXT)\n'
      'def f():\n'
      '    """%s/doc (a function docstring: TEXT)"""\n'
      '    return os.path.expanduser("~/mnt/dev")\n'   # machine-path-ok: test data (a planted tool)
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
        rows = MP.scan(self.d)[0]
        return [(r[1], r[3]) for r in rows if r[0] == name]

    def test_python(self):
        self.assertEqual(self.kinds('tool.py'), [(1, 'TEXT'), (3, 'CODE'), (4, 'TEXT'), (6, 'TEXT'), (7, 'CODE')])

    def test_shell(self):
        self.assertEqual(self.kinds('run.sh'), [(2, 'TEXT'), (3, 'CODE'), (4, 'CODE')])

    def test_job_template_header_counts(self):
        self.assertEqual(self.kinds('JOB_X_V1.job.sh.txt'), [(2, 'CODE')])

    def test_json_and_docs(self):
        self.assertEqual(self.kinds('PINS.json'), [(1, 'CODE')]); self.assertEqual(self.kinds('README.md'), [(2, 'TEXT')])

    def test_metric_cards_are_text(self):
        # a card (.yaml, .yml) says where a source lives, for people; an unknown ending stays CODE
        for name in ('CARD_A1_V2.yaml', 'CARD_B1_V1.yml', 'odd.cfg'):
            with open(os.path.join(self.d, name), 'w') as f:
                f.write('year_output: %s/volat_store/x.parquet\n' % U)
        kinds = {r[0]: r[3] for r in MP.scan(self.d, every=True)[0] if r[0] in ('CARD_A1_V2.yaml', 'CARD_B1_V1.yml', 'odd.cfg')}
        self.assertEqual(kinds, {'CARD_A1_V2.yaml': 'TEXT', 'CARD_B1_V1.yml': 'TEXT', 'odd.cfg': 'CODE'})

    def test_release_record_is_text(self):
        with open(os.path.join(self.d, 'RELEASE_X_V1.json'), 'w') as f:
            f.write('{"python": "%s/venvs/analyst/bin/python3"}\n' % U)
        self.assertEqual([(r[1], r[3]) for r in MP.scan(self.d, every=True)[0] if r[0] == 'RELEASE_X_V1.json'], [(1, 'TEXT')])

    def test_tmp_is_no_machine_path(self):
        self.assertEqual(self.kinds('clean.py'), [])

    def test_paths_found(self):
        rows, n, _ = MP.scan(self.d)
        self.assertEqual(n, 6)
        self.assertIn('~/mnt/dev', [r[2] for r in rows]); self.assertIn(V + '/judge_scratch', [r[2] for r in rows])  # machine-path-ok: test data
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


MARKS = ('X = "%s/a"   # machine-path-ok: test data\n'                 # 1 MARKED
         'Y = "%s/b"   # machine-path-ok:\n'                           # 2 no reason: CODE
         'Z = "%s/c # machine-path-ok: inside a string"\n'             # 3 the marker inside a string: CODE
         'W = ("%s/d"\n'                                                # 4 the marker on another line than the string: CODE
         '     )  # machine-path-ok: another line\n'
         'Q = """%s/e\n'                                                # 6 a string that ends on a marked line: MARKED
         'more"""  # machine-path-ok: test data\n') % (U, U, U, U, U)


class V2(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for name, body in (('m.py', MARKS), ('run.sh', 'cd %s/x  # machine-path-ok: a shell line\n' % U),
                           ('JOB_M_V1.job.sh.txt', 'cd %s/x  # machine-path-ok: a template line\n' % U),
                           ('old.py', 'F = "%s/dev"\nG = "%s/two"\n' % (U, U)), ('ok.py', 'X = "%s/a"  # machine-path-ok: test data\n' % U)):
            with open(os.path.join(self.d, name), 'w') as f:
                f.write(body)
        self.manifest(('m.py', 'run.sh', 'JOB_M_V1.job.sh.txt', 'old.py'))

    def tearDown(self):
        shutil.rmtree(self.d)

    def manifest(self, names):
        with open(os.path.join(self.d, 'MANIFEST.tsv'), 'w') as f:
            f.write('repo_path\tdev_path\trole\n' + ''.join('%s\tx\ty\n' % n for n in names))

    def known(self, *rows):
        with open(os.path.join(self.d, MP.KNOWN_FILE), 'w') as f:
            f.write('# kept released files\nfile\tline\tpath\tsha16\treason\n' + ''.join('\t'.join(map(str, r)) + '\n' for r in rows))

    def kinds(self, name):
        return [(r[1], r[3]) for r in MP.scan(self.d)[0] if r[0] == name]

    def main(self):
        with contextlib.redirect_stdout(io.StringIO()) as s:
            rc = MP.main([self.d])
        return rc, s.getvalue()

    def test_marks(self):
        self.assertEqual(self.kinds('m.py'), [(1, 'MARKED'), (2, 'CODE'), (3, 'CODE'), (4, 'CODE'), (6, 'MARKED')])

    def test_shell_and_templates_cannot_be_marked(self):
        self.assertEqual(self.kinds('run.sh'), [(1, 'CODE')]); self.assertEqual(self.kinds('JOB_M_V1.job.sh.txt'), [(1, 'CODE')])

    def test_known_while_unchanged(self):
        self.known(('old.py', 1, U + '/dev', MP.sha16(os.path.join(self.d, 'old.py')), 'released, kept for its callers'))
        self.assertEqual(self.kinds('old.py'), [(1, 'KNOWN'), (2, 'CODE')])
        self.assertEqual(MP.scan(self.d)[2], [])
        with open(os.path.join(self.d, 'old.py'), 'a') as f:
            f.write('# changed\n')
        self.assertEqual(self.kinds('old.py'), [(1, 'CODE'), (2, 'CODE')])                  # a changed file: CODE again
        self.assertEqual(MP.scan(self.d)[2], [('old.py', 1, U + '/dev')])                   # its row matches nothing

    def test_known_wrong_line(self):
        self.known(('old.py', 2, U + '/dev', MP.sha16(os.path.join(self.d, 'old.py')), 'the wrong line'))
        self.assertEqual(self.kinds('old.py'), [(1, 'CODE'), (2, 'CODE')])
        rc, out = self.main()
        self.assertIn('STALE\told.py:2\t' + U + '/dev', out)

    def test_verdicts(self):
        self.manifest(('ok.py',))
        rc, out = self.main()
        self.assertEqual(rc, 0, out); self.assertTrue(out.strip().endswith('-> CLEAN'), out); self.assertIn('MARKED\tok.py:1\t', out)
        self.manifest(('ok.py', 'old.py'))
        self.known(('old.py', 1, U + '/dev', MP.sha16(os.path.join(self.d, 'old.py')), 'released, kept for its callers'),
                   ('old.py', 2, U + '/two', MP.sha16(os.path.join(self.d, 'old.py')), 'released too'))
        rc, out = self.main()
        self.assertEqual(rc, 0, out); self.assertTrue(out.strip().endswith('-> CLEAN EXCEPT KNOWN'), out)
        self.assertIn('KNOWN\told.py:1\t' + U + '/dev\t(released, kept for its callers)', out)
        self.assertIn('CODE 0, CALLS_ARCHIVE 0, KNOWN 2, MARKED 1', out)
        self.manifest(('ok.py', 'old.py', 'm.py'))
        rc, out = self.main()
        self.assertEqual(rc, 1, out); self.assertTrue(out.strip().endswith('-> NOT CLEAN'), out)

    def test_known_refusals(self):
        self.known(('old.py', 1, U + '/dev', MP.sha16(os.path.join(self.d, 'old.py')), ' '))      # no reason
        self.assertEqual(self.main()[0], 2)
        self.known(('old.py', 'x', U + '/dev', MP.sha16(os.path.join(self.d, 'old.py')), 'a reason'))  # a line that is no number
        rc, out = self.main(); self.assertEqual(rc, 2, out); self.assertIn('ROW INCOMPLETE', out)


class Archive(unittest.TestCase):
    """an Alarm folder (with _tools/settings_v1.py) holding two parts; past editions in archive/ folders"""
    def setUp(self):
        self.d = tempfile.mkdtemp(); A = self.d
        files = {
            '_tools/settings_v1.py': 'X = 1\n',
            'P/tools/new_v2.py': '"""the current edition (new_v1.py was the past one: a docstring, no reference)"""\nX = 2\n',
            'P/tools/archive/new_v1.py': 'F = "%s/forensics"\n' % U,
            'P/tools/archive/README.md': 'past editions\n',
            'P/tools/README.md': 'current\n',
            'P/tools/caller.py': 'import os\nQ = os.path.join(os.path.dirname(__file__), "new_v1.py")   # reads the past edition\n',
            'P/tools/imp.py': 'import os, new_v1\n',
            'P/tools/fine.py': '# new_v1.py was replaced by new_v2.py (a comment)\nR = "old_new_v1.py renew_v1.pyc README.md"\n',
            'P/tests/test_new.py': 'OLD = "tools/new_v1.py"   # compared when present\n',
            'P/tests/mutants_new_v2.py': 'import os\nimport new_v1 as P1   # an import is never optional\n',
            'P/JOB_N_V2.job.sh.txt': '# QUEUE: Q_V1\ncd @@ALARM@@ && python3 P/tools/new_v1.py\n',
            'P/PINS.json': '{"tools/new_v1.py": "abcd"}\n',
            'Q/tools/archive/other_v1.py': 'Y = 1\n',
            'Q/tools/other_v2.py': 'Y = 2\n',
            'P/tools/cross.py': 'C = "other_v1.py"\n',
        }
        for rel, body in files.items():
            p = os.path.join(A, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w') as f:
                f.write(body)
        self.part = os.path.join(A, 'P')

    def tearDown(self):
        shutil.rmtree(self.d)

    def rows(self):
        return [(r[0], r[1], r[2], r[3]) for r in MP.scan(self.part, every=True)[0]]

    def test_kinds(self):
        rows = self.rows()
        self.assertEqual([r for r in rows if r[0] == 'tools/archive/new_v1.py'], [('tools/archive/new_v1.py', 1, U + '/forensics', 'ARCHIVE')])
        self.assertIn(('tools/caller.py', 2, 'new_v1.py', 'CALLS_ARCHIVE'), rows)
        self.assertIn(('tools/imp.py', 1, 'new_v1.py', 'CALLS_ARCHIVE'), rows)
        self.assertIn(('JOB_N_V2.job.sh.txt', 2, 'new_v1.py', 'CALLS_ARCHIVE'), rows)
        self.assertIn(('PINS.json', 1, 'new_v1.py', 'CALLS_ARCHIVE'), rows)
        self.assertIn(('tools/cross.py', 1, 'other_v1.py', 'CALLS_ARCHIVE'), rows)          # another part's archive
        self.assertIn(('tests/test_new.py', 1, 'new_v1.py', 'NAMES_ARCHIVE'), rows)
        self.assertIn(('tests/mutants_new_v2.py', 2, 'new_v1.py', 'CALLS_ARCHIVE'), rows)            # a test's import is a call
        for f in ('tools/new_v2.py', 'tools/fine.py', 'tools/README.md', 'tools/archive/README.md'):
            self.assertEqual([r for r in rows if r[0] == f], [], f)                         # docstring, comment, longer names, shared name

    def test_verdict(self):
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.part, '--all']), 1)
        out = s.getvalue()
        self.assertIn('CALLS_ARCHIVE\ttools/caller.py:2\tnew_v1.py', out); self.assertIn('NAMES_ARCHIVE\ttests/test_new.py:1', out)
        self.assertNotIn('\ttools/archive/new_v1.py:1', out)                                 # ARCHIVE rows are counted, not listed
        self.assertIn('CODE 0, CALLS_ARCHIVE 6,', out); self.assertIn('NAMES_ARCHIVE 1, ARCHIVE 1,', out)
        for f in ('tools/caller.py', 'tools/imp.py', 'JOB_N_V2.job.sh.txt', 'PINS.json', 'tools/cross.py', 'tests/mutants_new_v2.py'):
            os.remove(os.path.join(self.part, f))
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.part, '--all']), 0)
        self.assertTrue(s.getvalue().strip().endswith('-> CLEAN'), s.getvalue())          # an archived machine path and a test's name pass


class V3(unittest.TestCase):
    """v3: imports read from the syntax tree; a known row holds a reference to an archived file"""
    def setUp(self):
        self.d = tempfile.mkdtemp(); A = self.d
        files = {
            '_tools/settings_v1.py': 'X = 1\n',
            'P/tools/archive/old.py': 'Y = 1\n',
            'P/tools/dotted.py': 'from pkg.old import x\n',
            'P/tools/plain.py': 'import pkg.old\n',
            'P/tools/many.py': 'import os, old\n',
            'P/tools/rel.py': 'from . import old\n',
            'P/tools/multi.py': 'from pkg import (\n    x,\n    old)\n',
            'P/tools/tuple.py': 'def f():\n    return 1, 2\na, old = f()\nb = [1, old]\n',
            'P/tools/label.py': 'import os\nL = "# merged by old.py"\n',
            'P/tests/test_label.py': 'OLD = "old.py"\n',
        }
        for rel, body in files.items():
            p = os.path.join(A, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w') as f:
                f.write(body)
        self.part = os.path.join(A, 'P')

    def tearDown(self):
        shutil.rmtree(self.d)

    def rows(self):
        return [(r[0], r[1], r[2], r[3]) for r in MP.scan(self.part, every=True)[0]]

    def known(self, rows):
        with open(os.path.join(self.part, 'MACHINE_PATHS_KNOWN.tsv'), 'w') as f:
            f.write('# planted\nfile\tline\tpath\tsha16\treason\n' + ''.join('%s\t%d\t%s\t%s\t%s\n' % r for r in rows))

    def calls_only_label(self):
        for f in ('dotted', 'plain', 'many', 'rel', 'multi'):
            os.remove(os.path.join(self.part, 'tools', f + '.py'))

    def test_imports(self):
        rows = self.rows()
        for f in ('tools/dotted.py', 'tools/plain.py', 'tools/many.py', 'tools/rel.py', 'tools/multi.py'):
            self.assertIn((f, 1, 'old.py', 'CALLS_ARCHIVE'), rows, f)
        self.assertEqual([r for r in rows if r[0] == 'tools/multi.py'], [('tools/multi.py', 1, 'old.py', 'CALLS_ARCHIVE')])
        self.assertEqual([r for r in rows if r[0] == 'tools/tuple.py'], [])                 # a name after a comma is no import
        self.assertIn(('tools/label.py', 2, 'old.py', 'CALLS_ARCHIVE'), rows)
        self.assertIn(('tests/test_label.py', 1, 'old.py', 'NAMES_ARCHIVE'), rows)

    def test_known_name(self):
        self.calls_only_label()
        lab = MP.sha16(os.path.join(self.part, 'tools', 'label.py')); tst = MP.sha16(os.path.join(self.part, 'tests', 'test_label.py'))
        self.known([('tools/label.py', 2, 'old.py', lab, 'a label it prints'), ('tests/test_label.py', 1, 'old.py', tst, 'compared when present')])
        rows = self.rows()
        self.assertIn(('tools/label.py', 2, 'old.py', 'KNOWN'), rows); self.assertIn(('tests/test_label.py', 1, 'old.py', 'KNOWN'), rows)
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.part, '--all']), 0)
        out = s.getvalue()
        self.assertIn('KNOWN\ttools/label.py:2\told.py\t(a label it prints)', out); self.assertNotIn('STALE', out)
        self.assertTrue(out.strip().endswith('-> CLEAN EXCEPT KNOWN'), out)
        with open(os.path.join(self.part, 'tools', 'label.py'), 'a') as f:
            f.write('Z = 3\n')                                                                   # the file changed: the row no longer holds
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.part, '--all']), 1)
        out = s.getvalue()
        self.assertIn('CALLS_ARCHIVE\ttools/label.py:2\told.py', out); self.assertIn('STALE\ttools/label.py:2\told.py', out)

    def test_known_name_wrong_line(self):
        self.calls_only_label()
        self.known([('tools/label.py', 1, 'old.py', MP.sha16(os.path.join(self.part, 'tools', 'label.py')), 'the wrong line')])
        self.assertIn(('tools/label.py', 2, 'old.py', 'CALLS_ARCHIVE'), self.rows())
        with contextlib.redirect_stdout(io.StringIO()) as s:
            self.assertEqual(MP.main([self.part, '--all']), 1)
        self.assertIn('STALE\ttools/label.py:1\told.py', s.getvalue())


if __name__ == '__main__':
    unittest.main(verbosity=1)
