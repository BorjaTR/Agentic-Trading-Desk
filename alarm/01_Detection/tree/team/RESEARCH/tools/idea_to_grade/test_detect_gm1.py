"""test_detect_gm1.py (BUILD5, G1 D4 pair 2): planted, seconds. detect_gm1.py with windows='GRADE' must act as detect_v2.py and with
'MONTH' as detect_aw1_rel1.py on every line where they differ; every other definition must be the same text. A missing or wrong window fails.

  python3 -B test_detect_gm1.py <forensics tree holding detect_v2, detect_aw1_rel1 and the detect_gm1 overlay>"""
import ast, importlib.util, os, sys, tempfile, unittest
from pathlib import Path

TREE = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['GM1_TREE'])
T = os.path.join(TREE, 'team', 'RESEARCH', 'tools')
P_V = os.path.join(T, 'idea_to_grade', 'detect_v2.py')
P_A = os.path.join(T, 'alarm_process', 'detect_aw1_rel1.py')
P_G = os.path.join(T, 'idea_to_grade', 'detect_gm1.py')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m)
    return m


V = load('det_v2', P_V); A = load('det_aw1', P_A); G = load('det_gm1', P_G)
for _p in (str(G.CODE_DIR), T):                                   # lab3 (law) and labcore, as the tools' callers give them
    if _p not in sys.path:
        sys.path.insert(0, _p)


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


CHANGED_VS_V = {'WINDOWS', 'WINDOWS_ALARM', 'WINDOWS_ALARM_SHA16', 'admit_research_window', 'run', 'main'}
CHANGED_VS_A = {'WINDOWS', 'admit_research_window', 'run', 'main'}
CASES = [('20250901:20251231', '20250910', '20251231'), ('20250901:20260228', '20250910', '20260228'),
         ('20250901:20260430', '20250910', '20260430'), ('20250901:20260531', '20250910', '20260531'),
         ('20250901:20260630', '20250910', '20260630'), ('20251001:20251031', '20250910', '20251031'), (None, '20250910', '20251231'),
         ('20250901', '20250910', '20251231')]


class Stop(Exception):
    pass


def out(fn, *a, **k):
    try:
        return ('OK', fn(*a, **k))
    except Stop:
        return ('PASSED_CHECKS', None)
    except Exception as e:                                        # noqa: BLE001 (the refusal by name is the answer)
        return (getattr(e, 'code', type(e).__name__), str(e))


class Verbatim(unittest.TestCase):
    def test_other_definitions_are_v2_text(self):
        v, g = defs(P_V), defs(P_G)
        for k in sorted((set(v) | set(g)) - CHANGED_VS_V):
            self.assertEqual(g.get(k), v.get(k), k)

    def test_other_definitions_are_aw1_text(self):
        a, g = defs(P_A), defs(P_G)
        for k in sorted((set(a) | set(g)) - CHANGED_VS_A):
            self.assertEqual(g.get(k), a.get(k), k)

    def test_same_table_as_aw1(self):
        self.assertEqual(G.WINDOWS_ALARM.resolve(), A.WINDOWS_ALARM.resolve())
        self.assertEqual(G.WINDOWS_ALARM_SHA16, A.WINDOWS_ALARM_SHA16)


class Admit(unittest.TestCase):
    def test_grade_is_v2(self):
        for c in CASES:
            self.assertEqual(out(G.admit_research_window, *c, 'GRADE'), out(V.admit_research_window, *c), c)

    def test_month_is_aw1(self):
        for c in CASES:
            self.assertEqual(out(G.admit_research_window, *c, 'MONTH'), out(A.admit_research_window, *c), c)

    def test_the_two_windows_differ_somewhere(self):           # a wrong window (GRADE where MONTH is asked) is caught
        self.assertTrue(any(out(V.admit_research_window, *c) != out(A.admit_research_window, *c) for c in CASES))

    def test_missing_or_other_word_refused(self):
        for w in (None, '', 'grade', 'DAY', 'GRADE '):
            self.assertEqual(out(G.admit_research_window, *CASES[0], w)[0], 'NO_WINDOWS', w)

    def test_changed_alarm_table_refused_like_aw1(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'WINDOWS_ALARM_V1.tsv'; p.write_text(G.WINDOWS_ALARM.read_text() + '# planted\n')
            og, oa = G.WINDOWS_ALARM, A.WINDOWS_ALARM
            G.WINDOWS_ALARM = A.WINDOWS_ALARM = p
            try:
                g = out(G.admit_research_window, *CASES[0], 'MONTH'); a = out(A.admit_research_window, *CASES[0])
                gg = out(G.admit_research_window, *CASES[0], 'GRADE')
            finally:
                G.WINDOWS_ALARM, A.WINDOWS_ALARM = og, oa
        self.assertEqual(g[0], 'ALARM_WINDOWS_CHANGED'); self.assertEqual(g, a)
        self.assertEqual(gg, out(V.admit_research_window, *CASES[0]))   # GRADE never reads the alarm table


class Passes(unittest.TestCase):
    def test_run_passes_the_window_to_admit(self):
        got = []
        def spy(window, first, last, windows=None):
            got.append(windows); raise Stop()
        old = G.admit_research_window; G.admit_research_window = spy
        try:
            for w in ('GRADE', 'MONTH', None):
                self.assertEqual(out(G.run, 'd.json', '20250910', '20251231', '/nonexistent/out', 'r.tsv', research_window='20250901:20251231', lab_root='/nonexistent/lab',
                                     windows=w)[0], 'PASSED_CHECKS')
        finally:
            G.admit_research_window = old
        self.assertEqual(got, ['GRADE', 'MONTH', None])

    def test_run_without_window_refused(self):
        r = out(G.run, 'd.json', '20250910', '20251231', '/nonexistent/out', 'r.tsv', research_window='20250901:20251231', lab_root='/nonexistent/lab')
        self.assertEqual(r[0], 'NO_WINDOWS', r)

    def test_command_line_window(self):
        got = []
        def spy(*a, **k):
            got.append(k.get('windows')); raise G.Refusal('PLANTED', 'stop')
        old = G.run; G.run = spy
        try:
            base = ['--definition', 'd', '--roster', 'r', '--first', '20250910', '--last', '20251231', '--out', 'o', '--lab-root', 'l']
            for w in ('GRADE', 'MONTH'):
                self.assertEqual(G.main(base + ['--windows', w]), 2)
            self.assertEqual(G.main(base), 2)
        finally:
            G.run = old
        self.assertEqual(got, ['GRADE', 'MONTH', None])


if __name__ == '__main__':
    unittest.main(verbosity=1)
