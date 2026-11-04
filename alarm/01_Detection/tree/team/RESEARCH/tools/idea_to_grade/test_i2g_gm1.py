"""test_i2g_gm1.py (BUILD5, G1 D4 pair 3): planted, seconds. idea_to_grade_gm1.py with windows 'GRADE' must act as idea_to_grade_rel1.py
and with 'MONTH' as idea_to_grade_aw1_rel1.py where they differ (check_window); run() and main() are rel1's text plus exactly the one
changed line each; every other definition is the same text; the pins file is rel1's with this file in place; one kernels folder.

  python3 -B test_i2g_gm1.py <forensics tree holding rel1, aw1_rel1 and the gm1 overlay>"""
import ast, importlib.util, json, os, sys, tempfile, unittest, hashlib

TREE = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['GM1_TREE'])
T = os.path.join(TREE, 'team', 'RESEARCH', 'tools')
P_R = os.path.join(T, 'idea_to_grade', 'idea_to_grade_rel1.py')
P_A = os.path.join(T, 'alarm_process', 'idea_to_grade_aw1_rel1.py')
P_G = os.path.join(T, 'idea_to_grade', 'idea_to_grade_gm1.py')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, path
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m)
    return m


R = load('i2g_rel1', P_R); A = load('i2g_aw1', P_A); G = load('i2g_gm1', P_G)


def defs(path):
    with open(path) as fh:
        src = fh.read()
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                for x in ([t] if isinstance(t, ast.Name) else getattr(t, 'elts', [])):
                    if isinstance(x, ast.Name):
                        out[x.id] = ast.get_source_segment(src, n)
    return out


CHANGED_VS_R = {'WINDOWS', 'WINDOWS_ALARM', 'WINDOWS_ALARM_SHA16', 'check_window', 'run', 'main'}
CHANGED_VS_A = {'WINDOWS', 'WINDOWS_ALARM', 'check_window', 'run', 'main', 'I2G'}
CASES = [(('20250901', '20251231'), '20250910', '20251231'), (('20250901', '20260228'), '20250910', '20260228'),
         (('20250901', '20260430'), '20250910', '20260430'), (('20250901', '20260531'), '20250910', '20260531'),
         (('20250901', '20260630'), '20250910', '20260630'), (('20251001', '20251031'), '20250910', '20251031'),
         (('20251231', '20250901'), '20250910', '20251231'), (('20250901', '20251231'), '20251231', '20250910'),
         (('2025091', '20251231'), '20250910', '20251231')]


def out(fn, *a, **k):
    try:
        return ('OK', fn(*a, **k))
    except SystemExit as e:
        return ('EXIT', e.code)
    except Exception as e:                                        # noqa: BLE001 (the refusal by name is the answer)
        return (getattr(e, 'code', type(e).__name__), str(e))


class Verbatim(unittest.TestCase):
    def test_other_definitions_are_rel1_text(self):
        r, g = defs(P_R), defs(P_G)
        for k in sorted((set(r) | set(g)) - CHANGED_VS_R):
            self.assertEqual(g.get(k), r.get(k), k)

    def test_other_definitions_are_aw1_text(self):
        a, g = defs(P_A), defs(P_G)
        for k in sorted((set(a) | set(g)) - CHANGED_VS_A):
            self.assertEqual(g.get(k), a.get(k), k)

    def test_run_is_rel1_plus_one_line(self):
        g, r = defs(P_G)['run'], defs(P_R)['run']
        self.assertEqual(g.count('    check_window(window, a.first, a.last, a.windows)\n'), 1)
        self.assertEqual(g.replace('check_window(window, a.first, a.last, a.windows)', 'check_window(window, a.first, a.last)'), r)

    def test_main_is_rel1_plus_one_line(self):
        g, r = defs(P_G)['main'], defs(P_R)['main']
        line = "    p.add_argument('--windows', default=None, help='GRADE or MONTH: the window table (gm1); required, no default')\n"
        self.assertEqual(g.count(line), 1)
        self.assertEqual(g.replace(line, ''), r)

    def test_one_kernels_folder(self):                         # rel1 puts its folder first, aw1 puts idea_to_grade/ first: the same
        self.assertEqual(os.path.realpath(G.HERE), os.path.realpath(R.HERE))
        self.assertEqual(os.path.realpath(G.HERE), os.path.realpath(A.I2G))
        self.assertEqual(os.path.realpath(G.WINDOWS_ALARM), os.path.realpath(A.WINDOWS_ALARM))
        self.assertEqual(G.WINDOWS_ALARM, A.WINDOWS_ALARM)        # the refusal text names the same path string
        self.assertEqual(G.WINDOWS_ALARM_SHA16, A.WINDOWS_ALARM_SHA16)


class Window(unittest.TestCase):
    def test_cases_really_run(self):                              # an import failure must never make 'equal' pass (it did once)
        for mod, kw in ((R, {}), (A, {}), (G, {'windows': 'GRADE'}), (G, {'windows': 'MONTH'})):
            got = [out(mod.check_window, *c, **kw)[0] for c in CASES]
            self.assertIn('OK', got, (mod.__name__, kw, got))
            self.assertFalse({'ModuleNotFoundError', 'ImportError', 'AttributeError', 'NameError', 'TypeError'} & set(got), got)

    def test_grade_is_rel1(self):
        for c in CASES:
            self.assertEqual(out(G.check_window, *c, windows='GRADE'), out(R.check_window, *c), c)

    def test_month_is_aw1(self):
        for c in CASES:
            self.assertEqual(out(G.check_window, *c, windows='MONTH'), out(A.check_window, *c), c)

    def test_the_two_differ_somewhere(self):
        self.assertTrue(any(out(R.check_window, *c) != out(A.check_window, *c) for c in CASES))

    def test_missing_or_other_word_refused(self):
        for w in (None, '', 'grade', 'DAY', 'MONTH '):
            self.assertEqual(out(G.check_window, *CASES[0], windows=w)[0], 'NO_WINDOWS', w)

    def test_changed_alarm_table_refused_like_aw1(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'WINDOWS_ALARM_V1.tsv')
            with open(G.WINDOWS_ALARM) as src, open(p, 'w') as dst:
                dst.write(src.read() + '# planted\n')
            og, oa = G.WINDOWS_ALARM, A.WINDOWS_ALARM; G.WINDOWS_ALARM = A.WINDOWS_ALARM = p
            try:
                g = out(G.check_window, *CASES[0], windows='MONTH'); a = out(A.check_window, *CASES[0])
                gg = out(G.check_window, *CASES[0], windows='GRADE')
            finally:
                G.WINDOWS_ALARM, A.WINDOWS_ALARM = og, oa
        self.assertEqual(g[0], 'ALARM_WINDOWS_CHANGED'); self.assertEqual(g[0], a[0]); self.assertEqual(g[1].replace(p, 'P'), a[1].replace(p, 'P'))
        self.assertEqual(gg, out(R.check_window, *CASES[0]))


class CommandLine(unittest.TestCase):
    def test_windows_reaches_run(self):
        got = []
        def spy(a):
            got.append(a.windows); raise G.Refused('PLANTED', 'stop')
        old = G.run; G.run = spy
        try:
            base = ['--events', 'e', '--events-sha16', '0' * 16, '--roster', 'r', '--first', '20250910', '--last', '20251231',
                    '--research-window', '20250901:20251231', '--out', 'o', '--lab-root', 'l', '--pins', 'p']
            for w in ('GRADE', 'MONTH'):
                self.assertEqual(out(G.main, base + ['--windows', w]), ('EXIT', 2))
            self.assertEqual(out(G.main, base), ('EXIT', 2))
        finally:
            G.run = old
        self.assertEqual(got, ['GRADE', 'MONTH', None])


class Pins(unittest.TestCase):
    @unittest.skipIf(os.environ.get('GM1_MUTANT') == '1', 'every edit breaks the pin: mutants must be caught by behaviour tests')
    def test_pins_name_this_file(self):
        p = json.load(open(os.path.join(T, 'idea_to_grade', 'I2G_PINS_GM1.json')))['pins']
        with open(P_G, 'rb') as fh:
            self.assertEqual(p['team/RESEARCH/tools/idea_to_grade/idea_to_grade_gm1.py'], hashlib.sha256(fh.read()).hexdigest()[:16])

    def test_pins_are_rel1s_and_aw1s_but_the_grader(self):
        p = json.load(open(os.path.join(T, 'idea_to_grade', 'I2G_PINS_GM1.json')))['pins']
        r = json.load(open(os.path.join(T, 'idea_to_grade', 'I2G_PINS_V2_REL1.json')))['pins']
        a = json.load(open(os.path.join(T, 'alarm_process', 'I2G_PINS_AW1_REL1.json')))['pins']
        g = dict(p); del g['team/RESEARCH/tools/idea_to_grade/idea_to_grade_gm1.py']
        del r['team/RESEARCH/tools/idea_to_grade/idea_to_grade_rel1.py']; del a['team/RESEARCH/tools/alarm_process/idea_to_grade_aw1_rel1.py']
        self.assertEqual(g, r); self.assertEqual(g, a)


if __name__ == '__main__':
    unittest.main(verbosity=1)
