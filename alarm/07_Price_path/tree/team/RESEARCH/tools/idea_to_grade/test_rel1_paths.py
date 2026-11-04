#!/usr/bin/env python3
"""test_rel1_paths.py (SCOUT, K6, 31 Oct 2026; TEST, NOT REVIEWED): the new lines of the rel1 editions of the grader V3.2 speed twin S6
(owner STRATEGY/LEAD) and of their clean kernels, one check each, on the files beside this one (the team/ layout of the dev tree: no
machine path, nothing outside the tree root). No lab data, no settings file: seconds. mutants_rel1.py plants a bug in each new line
and runs this file (and the old tests on their new editions) on a copy: every planted bug must make it fail.
New edition by SCOUT for the clean release (the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only").
  python3 -B test_rel1_paths.py            (exit 0: every check passed)"""
import ast, importlib, io, json, os, re, subprocess, sys, tempfile, tokenize, contextlib
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
FO = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))          # the tree root: FO/team/RESEARCH/tools/idea_to_grade
OLD = ('idea_to_grade.py', 'i2g_engine.py', 'i2g_grade.py', 'idea_to_grade_v3_2.py', 'i2g_engine_v3_2.py', 'i2g_engine_v3_2_s2.py',
       'i2g_engine_v3_2_s6.py', 'i2g_patch_s6_v1.py', 'idea_to_grade_v3_2_s2.py', 'idea_to_grade_v3_2_s3.py', 'idea_to_grade_v3_2_s6.py',
       'detect.py', 'alarm_design_v2.py', 'alarm_context.py', 'alarm_stamp.py', 'alarm_stamp_projection_v1.py', 'draw_prepared_v1.py',
       'prepared_activity_v1.py', 'compare.py', 'make_pins_s6.py', 'release_pins_v3_2.py', 'markout_v1_1.py', 'markout_v1.py')
OLD_TABLES = ('STAMP_CATALOG_V1.tsv', 'I2G_PINS_V3_2.json', 'I2G_PINS_V3_2_S6.json', 'I2G_PINS_V2.json', 'JOB_ENTRY_V5.job.sh.txt',
              'run_alarm_store_v10_3_noladder.sh')
ok = fail = 0


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1; print('FAIL', name)


def refused(f, code):
    try:
        f()
    except SystemExit:
        return code == 'SystemExit'
    except Exception as e:
        return code in str(e)
    return False


import idea_to_grade_v3_2_s6_rel1 as S6                    # the store's entry: swaps warm to the rel1 S6 engine
import idea_to_grade_v3_2_rel1 as I3
import idea_to_grade_rel1 as I2
import i2g_engine_rel1 as E
import i2g_grade_rel1 as GR
L0 = (I3.LEDGER, I3.REGISTRY)                                             # as imported, before any test sets them
# 1 the tree root and the folders, found from the files (no machine path)
check('I2.F is the tree root above team/', I2.F == FO and os.path.isdir(os.path.join(FO, 'team', 'RESEARCH', 'tools', 'idea_to_grade')))
check('E.F is the same root; TOOLS, LAB3, B2 inside it', E.F == FO and E.TOOLS == FO + '/team/RESEARCH/tools' and E.LAB3 == FO + '/team/LAB3/code'
      and E.B2 == FO + '/team/OUTSIDE/COORD/development/DEV1/b2_performance_v1')
check('GR.DEV is <team>/OUTSIDE/COORD/development of this tree', GR.DEV == FO + '/team/OUTSIDE/COORD/development')
check('GR pins compare_v2.py at e7f7f91ad15183d7 (fast_compare unchanged)', GR.REF.endswith('/DEV1/opportunity_compare_v1/compare_v2.py') and
      GR.PINS == {GR.FAST: 'eec15093614540d5', GR.REF: 'e7f7f91ad15183d7'})
check('I3.COSTS is the cost table in the tree', I3.COSTS == FO + '/team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv' and os.path.isfile(I3.COSTS))
check('the default pins of V3.2 rel1 are I2G_PINS_V3_2_REL1.json beside it', I3.PINS_FILE == os.path.join(HERE, 'I2G_PINS_V3_2_REL1.json')
      and os.path.isfile(I3.PINS_FILE))
check('I2 has no machine default: GATE, LAB_ROOT and PINS_FILE are None', I2.GATE is None and I2.LAB_ROOT is None and I2.PINS_FILE is None)
check('V3.2 rel1 has no machine default for the ledger and the registry', L0 == (None, None))
# 2 the gate (the settings key FEED_GATE): none = RUN; a file = its first line
with tempfile.TemporaryDirectory() as d:
    g = os.path.join(d, 'GATE.txt'); open(g, 'w').write('PAUSE\n')
    I2.set_gate(None); a = I2.gate_ok(); I2.set_gate(''); b = I2.gate_ok() and I2.GATE is None
    I2.set_gate(g); c = I2.gate_ok(); open(g, 'w').write('RUN\n'); e = I2.gate_ok()
    I2.set_gate(os.path.join(d, 'missing')); m = refused(I2.gate_ok, 'No such file')
    I2.set_gate(None)
check('no gate: RUN; a gate file: PAUSE refused, RUN passes; a missing gate file stops the run', a and b and not c and e and m)
# 3 the research root (the settings key RESEARCH_ROOT): the canonical ledger and registry; GRADED only on them
I3.LEDGER = I3.REGISTRY = None
import argparse
ns = lambda **k: argparse.Namespace(**dict(dict(ledger='L.tsv', registry='R.tsv', universe='U.tsv', compat_v2=False, detect_run=None), **k))
check('without a research root every run is TEST', I3.run_class(ns()) == 'TEST')
I3.set_research_root('/r')
check('set_research_root: RESEARCH_ROOT/TRIES_LEDGER_V1.tsv and LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv', I3.LEDGER == '/r/TRIES_LEDGER_V1.tsv'
      and I3.REGISTRY == '/r/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv')
check('GRADED on the canonical pair, TEST otherwise', I3.run_class(ns(ledger=I3.LEDGER, registry=I3.REGISTRY)) == 'GRADED' and I3.run_class(ns(ledger=I3.LEDGER)) == 'TEST')
base = ['--first', '20250910', '--last', '20250910', '--research-window', '20250910:20250910', '--out', 'x', '--delay-s', '2', '--ledger-ask', 'A',
        '--alarm-id', 'ALM_X']
with contextlib.redirect_stderr(io.StringIO()):
    check('V3.2 rel1: --lab-root is required', refused(lambda: I3.parser().parse_args(base + ['--research-root', '/r']), 'SystemExit'))
    check('V3.2 rel1: --research-root is required', refused(lambda: I3.parser().parse_args(base + ['--lab-root', '/l']), 'SystemExit'))
    p = I3.parser().parse_args(base + ['--lab-root', '/l', '--research-root', '/r', '--gate=/g'])
    check('V3.2 rel1: --gate, --ledger and --registry: None defaults', p.gate == '/g' and p.ledger is None and p.registry is None and p.lab_root == '/l')
    check('I2 rel1 (V2.3.1 command): --lab-root and --pins required', refused(lambda: I2.main(['--first', '20250910', '--last', '20250910',
          '--research-window', '20250910:20250910', '--out', 'x', '--roster', 'r', '--events', 'e', '--events-sha16', 'x']), 'SystemExit'))
seen = []; run0 = I3.run; I3.run = lambda a: seen.append((a.ledger, a.registry, a.lab_root, I2.GATE))
try:
    I3.main(base + ['--lab-root', '/l', '--research-root', '/r', '--gate=/g', '--events', 'e', '--events-sha16', 'x', '--roster', 'ro'])
finally:
    I3.run = run0
check('V3.2 rel1 main: ledger and registry under the research root, the gate set', seen == [('/r/TRIES_LEDGER_V1.tsv', '/r/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv', '/l', '/g')])
I2.set_gate(None); I3.LEDGER = I3.REGISTRY = None
seen2 = []; run2 = I2.run; I2.run = lambda a: seen2.append((a.lab_root, a.pins, I2.GATE))
try:
    with contextlib.redirect_stderr(io.StringIO()):
        I2.main(['--first', '20250910', '--last', '20250910', '--research-window', '20250910:20250910', '--out', 'x', '--roster', 'ro', '--events', 'e',
                 '--events-sha16', 'x', '--lab-root', '/l', '--pins', 'P.json', '--gate=/g2'])
except SystemExit:
    pass
finally:
    I2.run = run2
check('I2 rel1 main (V2.3.1 command): --lab-root, --pins and the gate reach the run', seen2 == [('/l', 'P.json', '/g2')])
I2.set_gate(None)
REL1 = sorted(f for f in os.listdir(HERE) if f.endswith('_rel1.py'))
bad = []
for f in REL1 + [os.path.join('..', 'alarm_stamp', 'alarm_stamp_ed1_1.py'), os.path.join('..', 'markout', 'markout_v1_2.py'),
                 os.path.join('..', '..', '..', 'OUTSIDE', 'COORD', 'development', 'DEV1', 'b2_performance_v1', 'alarm_stamp_projection_v2.py')]:
    for node in ast.walk(ast.parse(open(os.path.join(HERE, f)).read())):
        names = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) else []
        bad += ['%s: %s' % (f, n) for n in names if n and n + '.py' in OLD]
check('no new edition imports a past edition (%d files)' % (len(REL1) + 3), not bad and len(REL1) >= 13)
def strings_naming(path, names):
    """the places a string of the file's code (not a docstring) names one of names (a file name, whole)"""
    src = open(path).read(); doc = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            b = node.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, 'value', None), ast.Constant) and isinstance(b.value.value, str):
                doc.update(range(b.lineno, (b.end_lineno or b.lineno) + 1))
    rx = re.compile(r'(?<![\w.-])(%s)(?![\w.-])' % '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True)))
    return ['%s:%d %s' % (os.path.basename(path), tok.start[0], m.group(1)) for tok in tokenize.generate_tokens(io.StringIO(src).readline)
            if tok.type == tokenize.STRING and tok.start[0] not in doc for m in rx.finditer(tok.string)]
EDITIONS = [os.path.join(HERE, f) for f in REL1 if not f.startswith(('test_', 'mutants_'))] + [os.path.join(HERE, '..', 'alarm_stamp', 'alarm_stamp_ed1_1.py'),
            os.path.join(HERE, '..', 'markout', 'markout_v1_2.py'), os.path.join(FO, 'team', 'OUTSIDE', 'COORD', 'development', 'DEV1', 'b2_performance_v1',
            'alarm_stamp_projection_v2.py')]
named = [x for e in EDITIONS for x in strings_naming(e, OLD + OLD_TABLES)]
check('no string of the code of the new editions names a past edition (%d files) %s' % (len(EDITIONS), named[:3]), not named and len(EDITIONS) >= 15)
check('the gate goes to the detector: I2 and I3 pass gate= to detect_v2.run', 'research_window=window, gate=GATE)' in open(I2.__file__).read() and
      'research_window=window, gate=I2.GATE)' in open(I3.__file__).read())
I3.LEDGER = I3.REGISTRY = None
# 4 the pins: relative to the tree root, an absolute path refused; the census of the store's process is pinned, with no past edition
with tempfile.TemporaryDirectory() as d:
    pa = os.path.join(d, 'P.json'); json.dump({'pins': {'/Users/x/team/a.py': '0' * 16}}, open(pa, 'w'))   # machine-path-ok: test data, an absolute path load_pins must refuse
    check('load_pins refuses an absolute path', refused(lambda: I2.load_pins(pa), 'PINS_FILE'))
    json.dump({'pins': {'team/../../a.py': '0' * 16}}, open(pa, 'w'))
    check('load_pins refuses a path that leaves the tree', refused(lambda: I2.load_pins(pa), 'PINS_FILE'))
for name in ('I2G_PINS_V3_2_S6_REL1.json', 'I2G_PINS_V3_2_REL1.json'):
    doc = json.load(open(os.path.join(HERE, name)))
    check('%s: every path relative, inside the tree, present' % name, all(not os.path.isabs(q) and os.path.isfile(os.path.join(FO, q)) for q in doc['pins']))
    check('%s: no past edition pinned' % name, not any(os.path.basename(q) in OLD for q in doc['pins']))
pins = I2.load_pins(os.path.join(HERE, 'I2G_PINS_V3_2_S6_REL1.json'))
check('load_pins resolves to the files here', all(q.startswith(FO + os.sep) for q in pins))
I2.recheck_pins(pins)
eng = S6.G.warm(); census = I2.census_modules(); census.pop(os.path.realpath(__file__), None)      # this test is not the store's code
check('the S6 rel1 warm returns the rel1 S6 engine', eng.__name__ == 'i2g_engine_v3_2_s6_rel1')
check('the census of the store process is pinned, unchanged', not set(census) - set(pins) and all(census[q] == pins[q] for q in census))
check('no past edition executed (census)', not any(os.path.basename(q) in OLD for q in census))
import idea_to_grade_v3_2_s2_rel1 as S2W
check('the S2 rel1 warm returns the rel1 S2 engine', S2W.warm().__name__ == 'i2g_engine_v3_2_s2_rel1')
check('the detector is detect_v2 with alarm_design_v3', any(q.endswith('/idea_to_grade/detect_v2.py') for q in census) and
      any(q.endswith('/alarm_design/alarm_design_v3.py') for q in census))
# 5 the clean kernels the engine loads
k = E.K.load(); AS = k.S.PROJECTION_BASE
check('the STAMP projection is alarm_stamp_projection_v2 on alarm_stamp_ed1_1 on alarm_context_ed1_1',
      os.path.basename(k.S.__file__) == 'alarm_stamp_projection_v2.py' and AS.__name__ == 'alarm_stamp_ed1_1' and os.path.basename(AS.AC.__file__) == 'alarm_context_ed1_1.py')
check('the prepared draw is draw_prepared_v2 on prepared_activity_v2', os.path.basename(k.DP.__file__) == 'draw_prepared_v2.py' and
      os.path.basename(k.DP.ACTIVITY.__file__) == 'prepared_activity_v2.py')
cp = E.code_pins()
check('E.code_pins: every pinned kernel is the clean edition, at its sha16', any(q.endswith('/alarm_stamp/alarm_stamp_ed1_1.py') for q in cp) and
      any(q.endswith('/alarm_context/alarm_context_ed1_1.py') for q in cp) and not any(os.path.basename(q) in OLD for q in cp))
g = GR.G.load()
check('the grading kernel is compare_v2', os.path.basename(g.ref.__file__) == 'i2g_existing_full_compare.py' or g.ref.__file__.endswith('compare_v2.py'))
check('alarm_stamp_ed1_1: no machine default for the out root', AS.OUT_ROOT is None and refused(lambda: AS.build('l', None, 'e', 'l', 'ev', 'A02', 'FADE',
      '20250910', '20250910'), 'OUT_ROOT_REQUIRED'))
src = open(AS.__file__).read()
check("alarm_stamp_ed1_1: a part's code identity names this file and alarm_context_ed1_1.py", "os.path.join(HERE, 'alarm_stamp_ed1_1.py')" in src and
      "os.path.join(TOOLS, 'alarm_context', 'alarm_context_ed1_1.py')" in src and 'alarm_stamp_ed1_1.py catalog' in src)
# 6 the pins makers write paths relative to the tree root (each in its own process: their census spawns a worker)
with tempfile.TemporaryDirectory() as d:
    for maker, ship in (('release_pins_v3_2_rel1.py', 'I2G_PINS_V3_2_REL1.json'), ('make_pins_s6_rel1.py', 'I2G_PINS_V3_2_S6_REL1.json')):
        out = os.path.join(d, ship)
        r = subprocess.run([sys.executable, '-B', os.path.join(HERE, maker), out], capture_output=True, text=True, cwd=d)
        doc = json.load(open(out)) if os.path.isfile(out) else {'pins': {}}
        want = json.load(open(os.path.join(HERE, ship)))
        check('%s writes %s again: the same pins, paths relative to the tree root' % (maker, ship), r.returncode == 0 and doc['pins'] == want['pins']
              and doc.get('paths') == 'relative to the tree root (the folder above team/)' and doc.get('by') == maker)
    code = ('import sys; sys.path.insert(0, %r); import release_pins_v3_2_rel1 as RP, idea_to_grade_rel1 as I2; c0 = I2.census_modules; '
            "I2.census_modules = lambda: dict(c0(), **{'/outside_the_tree/x.py': '0' * 16}); RP.main(sys.argv[1])") % HERE
    r = subprocess.run([sys.executable, '-B', '-c', code, os.path.join(d, 'OUT.json')], capture_output=True, text=True, cwd=d)
    check('release_pins_v3_2_rel1 refuses an executed file outside the tree root', r.returncode != 0 and 'REFUSED: executed files outside the tree root'
          in r.stderr + r.stdout and not os.path.exists(os.path.join(d, 'OUT.json')))
print('REL1 PATHS %d PASS %d FAIL' % (ok, fail))
sys.exit(1 if fail else 0)
