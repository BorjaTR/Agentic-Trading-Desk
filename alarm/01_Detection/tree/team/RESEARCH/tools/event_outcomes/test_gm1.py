"""test_gm1.py (BUILD5, G1 D4 pair 1): planted, seconds. event_outcomes_gm1.py with the window GRADE must act as event_outcomes_rel1.py
and with MONTH as event_outcomes_aw1_rel1.py, on every line where the two differ; everything else must be the same text (verbatim gate).
A wrong window (unset, another word, GRADE where MONTH is asked) must fail.

  python3 -B test_gm1.py <forensics tree holding rel1, aw1_rel1 and the gm1 overlay>
Reads code only; writes only in a temporary folder; no data store, no network, no clock."""
import ast, importlib.util, json, os, subprocess, sys, tempfile, unittest

TREE = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['GM1_TREE'])
T = os.path.join(TREE, 'team', 'RESEARCH', 'tools')
P_R = os.path.join(T, 'event_outcomes', 'event_outcomes_rel1.py')
P_A = os.path.join(T, 'alarm_process', 'event_outcomes_aw1_rel1.py')
P_G = os.path.join(T, 'event_outcomes', 'event_outcomes_gm1.py')
P_RPR = os.path.join(T, 'event_profile', 'run_parallel_rel1.py')
P_RPG = os.path.join(T, 'event_profile', 'run_parallel_gm1.py')
os.environ.pop('EO_WINDOWS', None)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


R = load('eo_rel1', P_R); A = load('eo_aw1', P_A); G = load('eo_gm1', P_G)


def defs(path):
    """{top-level name: source text} of every def, class and assignment"""
    src = open(path).read(); tree = ast.parse(src); out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ([t] if isinstance(t, ast.Name) else getattr(t, 'elts', [])):
                    if isinstance(x, ast.Name):
                        out[x.id] = ast.get_source_segment(src, n)
    return out


# the named differences (make_gm1.py); every other definition must be the source's text exactly
CHANGED_VS_R = {'RELEASE', 'RUN_PARALLEL', 'RELEASES', 'WINDOWS_ENV', 'WINDOWS_ALARM', 'WINDOWS_ALARM_SHA16', 'windows', 'use_windows',
                'release_path', '__getattr__', 'alarm_wins', 'authorize', 'config_pins', 'run', 'check_closure', 'preflight', 'main'}
CHANGED_VS_A = CHANGED_VS_R - {'WINDOWS_ALARM_SHA16', 'alarm_wins'}


class Env:
    """set or clear EO_WINDOWS for one block"""
    def __init__(self, w):
        self.w = w
    def __enter__(self):
        self.old = os.environ.pop('EO_WINDOWS', None)
        if self.w is not None:
            os.environ['EO_WINDOWS'] = self.w
    def __exit__(self, *e):
        os.environ.pop('EO_WINDOWS', None)
        if self.old is not None:
            os.environ['EO_WINDOWS'] = self.old


class Patch:
    """set module attributes for one block (the same object for every module that shares it)"""
    def __init__(self, obj, **kw):
        self.obj, self.kw = obj, kw
    def __enter__(self):
        self.old = {k: getattr(self.obj, k) for k in self.kw}
        for k, v in self.kw.items():
            setattr(self.obj, k, v)
    def __exit__(self, *e):
        for k, v in self.old.items():
            setattr(self.obj, k, v)


class Stop(Exception):
    pass


def refusal(fn, *a, **k):
    try:
        fn(*a, **k)
    except Stop:
        return 'PASSED_CHECKS'
    except PermissionError as e:
        return getattr(e, 'code', type(e).__name__) + ' | ' + str(e).split(': ', 1)[-1]
    return 'NO_REFUSAL'


class Verbatim(unittest.TestCase):
    def test_every_other_definition_is_rel1_text(self):
        r, g = defs(P_R), defs(P_G)
        for k in sorted((set(r) | set(g)) - CHANGED_VS_R):
            self.assertEqual(g.get(k), r.get(k), k)

    def test_every_other_definition_is_aw1_text(self):
        a, g = defs(P_A), defs(P_G)
        for k in sorted((set(a) | set(g)) - CHANGED_VS_A):
            self.assertEqual(g.get(k), a.get(k), k)

    def test_alarm_lines_are_aw1_text(self):
        a, g = defs(P_A), defs(P_G)
        for k in ('alarm_wins', 'WINDOWS_ALARM_SHA16'):
            self.assertEqual(g[k].replace('WINDOWS_ALARM = os.path.join(TOOLS, \'alarm_process\', ', 'WINDOWS_ALARM = os.path.join(HERE, ').split('#')[0].strip(),
                             a[k].split('#')[0].strip(), k)

    def test_same_window_file_and_release_folder_as_aw1(self):
        self.assertEqual(os.path.realpath(G.WINDOWS_ALARM), os.path.realpath(A.WINDOWS_ALARM))
        self.assertEqual(G.WINDOWS_ALARM_SHA16, A.WINDOWS_ALARM_SHA16)
        self.assertEqual(os.path.dirname(G.RELEASES['MONTH']), os.path.dirname(A.RELEASE))
        self.assertEqual(os.path.dirname(G.RELEASES['GRADE']), os.path.dirname(R.RELEASE))

    def test_run_parallel_gm1_is_rel1_but_EO(self):
        r, g = defs(P_RPR), defs(P_RPG)
        for k in sorted(set(r) | set(g)):
            if k != 'EO':
                self.assertEqual(g.get(k), r.get(k), k)
        rp = load('rp_gm1', P_RPG)
        self.assertEqual(os.path.realpath(rp.EO), os.path.realpath(P_G))
        self.assertEqual(os.path.realpath(G.RUN_PARALLEL), os.path.realpath(P_RPG))


class Choice(unittest.TestCase):
    def test_unset_refused_everywhere(self):
        with Env(None):
            self.assertTrue(refusal(G.windows).startswith('NO_WINDOWS'))
            self.assertTrue(refusal(G.release_path).startswith('NO_WINDOWS'))
            self.assertTrue(refusal(lambda: G.RELEASE).startswith('NO_WINDOWS'))
            r = refusal(G.authorize, ('20250901', '20251231'), ['202509'], '2026-10-31T00:00:00Z')   # authorize names every refusal OUTCOME_REFUSED
            self.assertTrue(r.startswith('OUTCOME_REFUSED') and 'NO_WINDOWS' in r, r)
            self.assertTrue(refusal(G.run, 0, *['x'] * 8).startswith('NO_WINDOWS'))
            for cmd in ('run', 'check', 'build'):
                self.assertTrue(refusal(G.main, [cmd, '0'] + ['x'] * 8).startswith('NO_WINDOWS'), cmd)

    def test_other_word_refused(self):
        for w in ('DAY', 'grade', '', 'GRADE '):
            with Env(w):
                self.assertTrue(refusal(G.windows).startswith('NO_WINDOWS'), w)
            self.assertTrue(refusal(G.use_windows, w).startswith('NO_WINDOWS'), w)

    def test_use_windows_and_cli_set_the_environment_children_inherit(self):
        with Env(None):
            G.use_windows('MONTH')
            out = subprocess.check_output([sys.executable, '-c', 'import os; print(os.environ.get("EO_WINDOWS"))']).decode().strip()
            self.assertEqual(out, 'MONTH')
            with Patch(G, gate_wait=lambda log=print: (_ for _ in ()).throw(Stop())):
                self.assertEqual(refusal(G.main, ['run', '3', '--windows', 'GRADE'] + ['x'] * 8), 'PASSED_CHECKS')
            self.assertEqual(os.environ['EO_WINDOWS'], 'GRADE')

    def test_release_record_per_window(self):
        with Env('GRADE'):
            self.assertEqual(G.release_path(), os.path.join(T, 'event_outcomes', 'RELEASE_event_outcomes_GM1.json'))
            self.assertEqual(G.RELEASE, G.release_path())
        with Env('MONTH'):
            self.assertEqual(G.release_path(), os.path.join(T, 'alarm_process', 'RELEASE_event_outcomes_GM1_MONTH.json'))
            self.assertEqual(G.RELEASE, G.release_path())
        self.assertRaises(AttributeError, lambda: G.NOT_A_NAME)


class Branches(unittest.TestCase):
    def capture_auth(self, mod, wins):
        got = {}
        def fake(s, months, **k):
            got.update(k, months=months, s=s)
        with Patch(G.gates, outcome_allowed=fake):
            mod.authorize(('20250901', '20251231'), ['202509', '202510'], '2026-10-31T00:00:00Z', law='L', wins=wins)
        return got

    def test_authorize_grade_is_rel1(self):
        for wins in (None, [('BUILD', '20250901', '20260228')]):
            with Env('GRADE'):
                self.assertEqual(self.capture_auth(G, wins), self.capture_auth(R, wins))

    def test_authorize_month_is_aw1(self):
        for wins in (None, [('BUILD', '20250901', '20260228')]):
            with Env('MONTH'):
                g, a = self.capture_auth(G, wins), self.capture_auth(A, wins)
            self.assertEqual(g, a)
        with Env('MONTH'):
            self.assertIsNotNone(self.capture_auth(G, None)['wins'])          # MONTH never falls back to WINDOWS_V1

    def test_wrong_window_fails(self):
        with Env('GRADE'):
            g = self.capture_auth(G, None)
        with Env('MONTH'):
            a = self.capture_auth(A, None)
        self.assertNotEqual(g, a)                                             # GRADE where MONTH is asked is caught

    def test_authorize_refusal_named_the_same(self):
        def no(s, months, **k):
            raise PermissionError('planted refusal')
        for w, mod in (('GRADE', R), ('MONTH', A)):
            with Env(w), Patch(G.gates, outcome_allowed=no):
                self.assertEqual(refusal(G.authorize, ('20250901', '20251231'), ['202509'], 'n'),
                                 refusal(mod.authorize, ('20250901', '20251231'), ['202509'], 'n'))

    def test_alarm_table_changed_refused_like_aw1(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'WINDOWS_ALARM_V1.tsv'); open(p, 'w').write(open(G.WINDOWS_ALARM).read() + '# planted\n')
            with Env('MONTH'), Patch(G, WINDOWS_ALARM=p), Patch(A, WINDOWS_ALARM=p):
                g = refusal(G.authorize, ('20250901', '20251231'), ['202509'], 'n')
                a = refusal(A.authorize, ('20250901', '20251231'), ['202509'], 'n')
        self.assertTrue(g.startswith('OUTCOME_REFUSED') and 'ALARM_WINDOWS_CHANGED' in g, g)   # aw1 wraps it the same way
        self.assertEqual(g, a)

    def test_config_pins(self):
        with tempfile.TemporaryDirectory() as d:
            st = os.path.join(d, 's.json'); ev = os.path.join(d, 'e.tsv'); law = os.path.join(d, 'law.py')
            for p in (st, ev, law):
                open(p, 'w').write(p)
            s = {'_path': st, 'labels': [{'kind': 'return'}]}
            with Patch(G.gates, LAW=law if not os.path.isfile(G.gates.LAW) else G.gates.LAW):
                with Env('GRADE'):
                    self.assertEqual(G.config_pins(s, ev), R.config_pins(s, ev))
                with Env('MONTH'):
                    self.assertEqual(G.config_pins(s, ev), A.config_pins(s, ev))
                    self.assertEqual(G.config_pins(s, ev)['windows']['path'], os.path.realpath(A.WINDOWS_ALARM))
                with Env('GRADE'):
                    self.assertEqual(G.config_pins(s, ev)['windows']['path'], os.path.realpath(G.gates.WINDOWS))

    def test_workers(self):
        stop = lambda log=print: (_ for _ in ()).throw(Stop())
        with Patch(G, gate_wait=stop), Patch(R, gate_wait=stop), Patch(A, gate_wait=stop):
            for n in (0, 1, 3, 8, 9, -1):
                with Env('GRADE'):
                    self.assertEqual(refusal(G.run, n, *['x'] * 8), refusal(R.run, n, *['x'] * 8), n)
                with Env('MONTH'):
                    self.assertEqual(refusal(G.run, n, *['x'] * 8), refusal(A.run, n, *['x'] * 8), n)
            with Env('MONTH'):
                self.assertTrue(refusal(G.run, 3, *['x'] * 8).startswith('WORKERS_AW1'))
            with Env('GRADE'):
                self.assertEqual(refusal(G.run, 3, *['x'] * 8), 'PASSED_CHECKS')


class Releases(unittest.TestCase):
    @unittest.skipUnless(json.load(open(os.path.join(T, 'event_outcomes', 'RELEASE_event_outcomes_GM1.json')))['runtime'].get('interpreter', sys.executable)
                         == sys.executable, 'release.check pins another interpreter here')
    def test_release_graph_checks(self):
        from labcore import release
        for w in ('GRADE', 'MONTH'):
            with Env(w):
                release.check(G.release_path())

    @unittest.skipIf(os.environ.get('GM1_MUTANT') == '1', 'every edit breaks the pin: mutants must be caught by behaviour tests')
    def test_files_are_the_pinned_bytes(self):
        g = json.load(open(os.path.join(T, 'event_outcomes', 'RELEASE_event_outcomes_GM1.json')))['files']
        for p in (P_G, P_RPG):
            self.assertEqual(G.ids.sha16_file(p), g[os.path.relpath(os.path.realpath(p), G.FORENSICS)]['sha16'], p)

    def test_release_graph_closes(self):
        g = json.load(open(os.path.join(T, 'event_outcomes', 'RELEASE_event_outcomes_GM1.json')))['files']
        inv = {k: g[k]['sha16'] for k in ('team/RESEARCH/tools/event_outcomes/event_outcomes_gm1.py', 'team/RESEARCH/tools/event_profile/run_parallel_gm1.py')}
        for w in ('GRADE', 'MONTH'):
            with Env(w):
                G.check_closure(inv)
                bad = dict(inv); bad[next(iter(bad))] = '0' * 16
                self.assertTrue(refusal(G.check_closure, bad).startswith('CLOSURE'), w)

    def test_month_closure_walks_the_month_record(self):
        inv = {'team/RESEARCH/tools/alarm_process/WINDOWS_ALARM_V1.tsv': '37decf0075649f69'}   # pinned only by the MONTH record
        with Env('MONTH'):
            G.check_closure(inv)
        with Env('GRADE'):
            self.assertTrue(refusal(G.check_closure, inv).startswith('CLOSURE'))

    def test_month_record_pins_the_table_and_grade_record(self):
        m = json.load(open(os.path.join(T, 'alarm_process', 'RELEASE_event_outcomes_GM1_MONTH.json')))
        self.assertEqual(m['files']['team/RESEARCH/tools/alarm_process/WINDOWS_ALARM_V1.tsv']['sha16'], '37decf0075649f69')
        self.assertEqual(list(m['releases']), ['team/RESEARCH/tools/event_outcomes/RELEASE_event_outcomes_GM1.json'])
        g = json.load(open(os.path.join(T, 'event_outcomes', 'RELEASE_event_outcomes_GM1.json')))
        self.assertNotIn('team/RESEARCH/tools/event_outcomes/event_outcomes_rel1.py', g['files'])
        self.assertIn('team/RESEARCH/tools/event_outcomes/event_outcomes_gm1.py', g['files'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
