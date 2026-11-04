"""test_gm2.py (BUILD5, ALARM_V1_10 D2 step 3): planted, seconds. event_outcomes_gm2.py must be event_outcomes_gm1.py's text but in the
named definitions; the store must be written by lab3.evt.write_part (evt1) and never by lab3.write.write_part; every process's imports
must name lab3.evt; the manifest binds WORDS.json; run_parallel_gm2 is gm1 but its EO; the records differ only in the gm2 rows.

  python3 -B test_gm2.py <gm1 overlay tree> <gm2 overlay tree> <lab3 code dir (holds lab3/ with evt.py)>
Reads code only; writes only in a temporary folder; no data store, no network, no clock."""
import ast, importlib.util, json, os, sys, tempfile, unittest

if len(sys.argv) == 2:                                   # run_mutants_v1: one argument, the (mutated) gm2 tree; the rest from the environment
    G1, G2, CODE = os.environ['GM1_TREE'], sys.argv.pop(1), os.environ['LAB3_CODE']
else:
    G1, G2, CODE = sys.argv.pop(1), sys.argv.pop(1), sys.argv.pop(1)
G1, G2, CODE = (os.path.realpath(x) for x in (G1, G2, CODE))
PIN = unittest.skipIf(os.environ.get('GM1_MUTANT') == '1', 'pins bytes (BL55): skipped under planted faults')
T = 'team/RESEARCH/tools/'
P1 = os.path.join(G1, T + 'event_outcomes/event_outcomes_gm1.py'); P2 = os.path.join(G2, T + 'event_outcomes/event_outcomes_gm2.py')
R1 = os.path.join(G1, T + 'event_profile/run_parallel_gm1.py'); R2 = os.path.join(G2, T + 'event_profile/run_parallel_gm2.py')
C1 = os.path.join(G1, T + 'event_outcomes/RELEASE_event_outcomes_GM1.json'); C2 = os.path.join(G2, T + 'event_outcomes/RELEASE_event_outcomes_GM2.json')
M2 = os.path.join(G2, T + 'alarm_process/RELEASE_event_outcomes_GM2_MONTH.json')
CHANGED = {'RELEASES', 'RUN_PARALLEL', 'load_deps', '_write_days', 'run'}   # make_gm2.py's named differences


def defs(path):
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


def sha16(p):
    import hashlib
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def body_of(path, name):
    return defs(path)[name]


@PIN
class Verbatim(unittest.TestCase):
    def test_cases_really_run(self):                     # BL56: a vacuous pass is a failure
        self.assertGreater(len(defs(P1)), 50); self.assertEqual(set(defs(P1)), set(defs(P2)))

    def test_every_other_definition_is_gm1_text(self):
        a, b = defs(P1), defs(P2)
        diff = {k for k in a if a[k] != b[k]}
        self.assertEqual(diff, CHANGED)

    def test_the_text_after_the_head_is_gm1_text_but_the_named_lines(self):
        a = open(P1).read().splitlines(); b = open(P2).read().splitlines()
        self.assertEqual(len(b) - len(a), 5)                                # the 5 head lines, nothing added elsewhere
        changed = [i for i, (x, y) in enumerate(zip(a, b[5:])) if x != y]
        self.assertEqual(len(changed), 8)          # gm1's first line (its quotes now open the head), deps, writer import, writer, bind, RELEASES x2, RUN_PARALLEL
        self.assertEqual(changed[0], 0); self.assertEqual(b[5], a[0][3:])

    def test_run_parallel_gm2_is_gm1_but_EO(self):
        a = open(R1).read().splitlines(); b = open(R2).read().splitlines()
        self.assertEqual(len(b) - len(a), 2); self.assertEqual(b[2], a[0][3:])        # 2 head lines; gm1's quotes open the head
        changed = [i for i, (x, y) in enumerate(zip(a[1:], b[3:])) if x != y]
        self.assertEqual(len(changed), 1)                                                  # the EO line only
        self.assertEqual(defs(R2)['EO'], "EO = os.path.join(HERE, '..', 'event_outcomes', 'event_outcomes_gm2.py')")


class Writer(unittest.TestCase):
    @PIN
    def test_write_days_resolves_evt_write_part(self):
        src = body_of(P2, '_write_days')
        self.assertIn('from lab3 import write as LW, evt as LE', src)
        self.assertIn('write = LE.write_part', src); self.assertNotIn('write = LW.write_part', src)

    def test_write_days_calls_evt_and_never_write(self):
        """run _write_days on no day (P['days'] empty) with the real lab3: the resolved writer is never called, so plant a day:
        both writers replaced by recorders; the evt one must be the one called"""
        sys.path.insert(0, CODE); sys.path.insert(0, os.path.dirname(P2))
        from lab3 import write as LW, evt as LE
        spec = importlib.util.spec_from_file_location('eo_gm2_src', P2); src = open(P2).read()
        node = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == '_write_days'][0]
        g = {}; exec(compile(ast.Module([node], []), P2, 'exec'), g)
        import numpy as np
        calls = []
        old_e, old_w = LE.write_part, LW.write_part
        LE.write_part = lambda *a, **k: calls.append('evt'); LW.write_part = lambda *a, **k: calls.append('write')
        g.update(os=os, sys=sys, np=np, ROWCOLS=('day', 'as_of_us', 'known_at_us', 'stale', 'value_kind', 'value_bits', 'value_txt', 'empty_reason'),
                 US=1000000, VERIFIED='VERIFIED', FAULT_ENV='EVENT_OUTCOMES_FAULT', catalog_text=lambda subject, s: 'code\tkind\tclock\texact_k\tscope\tmeaning\n',
                 column_specs=lambda s: [{'col': 'r1', 'kind': 'number'}], time=None)
        LWc = LW.load_catalog
        LW.load_catalog = lambda p: {}
        try:
            with tempfile.TemporaryDirectory() as d:
                P = {'days': np.array([20251001]), 'keys': [('BTC', 1759312800)]}
                g['_write_days'](d, CODE, 'S', {}, P, {'r1': [1.5]}, {'r1': ['']}, {'r1': [1759312800000000]}, {}, None, log=lambda *a: None)
        finally:
            LE.write_part, LW.write_part, LW.load_catalog = old_e, old_w, LWc
        self.assertEqual(calls, ['evt'])

    @PIN
    def test_load_deps_imports_evt(self):
        self.assertIn('evt as _e', body_of(P2, 'load_deps'))

    @PIN
    def test_manifest_binds_words_json(self):
        self.assertIn("f in ('index.json', 'REASONS.txt', 'WORDS.json')", body_of(P2, 'run'))

    @PIN
    def test_releases_and_run_parallel_are_gm2(self):
        self.assertIn('RELEASE_event_outcomes_GM2.json', defs(P2)['RELEASES']); self.assertIn('RELEASE_event_outcomes_GM2_MONTH.json', defs(P2)['RELEASES'])
        self.assertIn('run_parallel_gm2.py', defs(P2)['RUN_PARALLEL'])


@PIN
class Records(unittest.TestCase):
    def test_grade_record_differs_only_in_gm2_rows(self):
        a = json.load(open(C1)); b = json.load(open(C2))
        self.assertEqual(set(a) , set(b))
        for k in a:
            if k not in ('files', 'by', 'reason', 'release', 'replaces', 'status'):
                self.assertEqual(a[k], b[k], k)
        fa = {k: v for k, v in a['files'].items() if not k.endswith(('event_outcomes_gm1.py', 'run_parallel_gm1.py'))}
        fb = {k: v for k, v in b['files'].items() if not k.endswith(('event_outcomes_gm2.py', 'run_parallel_gm2.py'))}
        self.assertEqual(fa, fb)

    def test_records_pin_the_gm2_bytes(self):
        b = json.load(open(C2))['files']
        self.assertEqual(b[T + 'event_outcomes/event_outcomes_gm2.py']['sha16'], sha16(P2))
        self.assertEqual(b[T + 'event_profile/run_parallel_gm2.py']['sha16'], sha16(R2))
        m = json.load(open(M2))['releases']
        self.assertEqual(m, {T + 'event_outcomes/RELEASE_event_outcomes_GM2.json': sha16(C2)})


if __name__ == '__main__':
    unittest.main(verbosity=1)
