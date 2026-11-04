"""test_d1_v3.py (BUILD5, ALARM_V1_10): planted, seconds. d1_reports_v3.py must be d1_reports_v2.py's text but the named lines (make_d1_v3.py):
the Outcomes run's in-process writer is Capture(lab3.evt.write_part) (the store in evt1), and chain() refuses NO_WINDOWS (exit 2) unless
EO_WINDOWS is GRADE or MONTH, and gives the card --windows <EO_WINDOWS>.
  python3 -B test_d1_v3.py <folder holding d1_reports_v2.py and d1_reports_v3.py (the Alarm's 03_Grading/tree/tools/alarm_process)>
Reads code only; no data store, no network."""
import ast, os, subprocess, sys, unittest

D = os.path.realpath(sys.argv.pop(1) if len(sys.argv) > 1 else os.environ['D1_DIR'])
P2, P3 = os.path.join(D, 'd1_reports_v2.py'), os.path.join(D, 'd1_reports_v3.py')
PIN = unittest.skipIf(os.environ.get('GM1_MUTANT') == '1', 'pins bytes (BL55): skipped under planted faults')


def defs(path):
    src = open(path).read(); out = {}
    for n in ast.parse(src).body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
    return out


class Verbatim(unittest.TestCase):
    @PIN
    def test_only_outcomes_and_chain_differ(self):
        a, b = defs(P2), defs(P3)
        self.assertGreater(len(a), 5); self.assertEqual(set(a), set(b))
        self.assertEqual({k for k in a if a[k] != b[k]}, {'outcomes', 'chain'})

    @PIN
    def test_changed_lines_are_the_named_ones(self):
        a = open(P2).read().splitlines(); b = open(P3).read().splitlines()
        self.assertEqual(len(b) - len(a), 3 + 3)                                  # 3 head lines, 3 window-check lines
        self.assertIn('        cap = d1.Capture(LE.write_part)', b); self.assertNotIn('        cap = d1.Capture(LW.write_part)', b)


class Behaviour(unittest.TestCase):
    def run_chain(self, windows):
        env = dict(os.environ); env.pop('EO_WINDOWS', None)
        if windows is not None:
            env['EO_WINDOWS'] = windows
        code = ('import importlib.util as u, sys; s = u.spec_from_file_location("d1v3", %r); m = u.module_from_spec(s); s.loader.exec_module(m); '
                'm.tools = lambda F: (_ for _ in ()).throw(SystemExit(7)); m.chain(*["x"] * 14)') % P3
        return subprocess.run([sys.executable, '-B', '-c', code], env=env, capture_output=True, text=True)

    def test_no_windows_refused(self):
        for w in (None, '', 'grade', 'BOTH'):
            p = self.run_chain(w)
            self.assertEqual(p.returncode, 2, (w, p.stderr[-300:])); self.assertIn('NO_WINDOWS', p.stderr)

    def test_a_window_passes_the_check(self):
        for w in ('GRADE', 'MONTH'):
            self.assertEqual(self.run_chain(w).returncode, 7, w)                  # reached tools(): past the window check

    def test_card_gets_the_window(self):
        src = defs(P3)['chain']
        self.assertIn("+ ['--windows', WINDOWS]", src)

    def test_outcomes_writer_is_evt(self):
        src = defs(P3)['outcomes']
        self.assertIn('from lab3 import evt as LE', src); self.assertIn('d1.Capture(LE.write_part)', src)


if __name__ == '__main__':
    unittest.main(verbosity=1)
