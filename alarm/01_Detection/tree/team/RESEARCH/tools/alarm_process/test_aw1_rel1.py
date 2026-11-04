#!/usr/bin/env python3
"""test_aw1_rel1.py (SCOUT, K12, 31 Oct 2026; TEST, NOT REVIEWED): tests of the MONTH chain's two clean aw1 editions beside this file:
detect_aw1_rel1.py (detect_v2.py with detect_aw1.py's window classes) and idea_to_grade_aw1_rel1.py (idea_to_grade_rel1.py with
idea_to_grade_aw1.py's changes). No lab data, no settings file: seconds.
  D1, D2 derivation: each file is rebuilt here from its two sources in this tree (the clean edition and the aw1 file) with exactly the aw1
         change and the K12 header, and must be the same bytes;
  F  detect_aw1_rel1: the research window Sep 2025-Apr 2026 is admitted (aw1's BUILD classes) where detect_v2 refuses it (WINDOWS_V1: Mar
     is CHECK); June 2026 is refused; a changed window table is ALARM_WINDOWS_CHANGED; no lab root is LAB_ROOT_REQUIRED before any read;
     the gate: none runs, a PAUSE file stops, a RUN file runs; its engine is alarm_design_v3; no machine path in its text;
  G  idea_to_grade_aw1_rel1: the same window checks through check_window (rel1 refuses Mar 2026); a changed table is refused; no machine
     default (GATE, LAB_ROOT, PINS_FILE are None); the tree root is found from the file; the rel1 kernels come from idea_to_grade/ in this
     tree; load_pins maps I2G_PINS_AW1_REL1.json into the tree and refuses an absolute path; the command refuses without --pins or
     --lab-root.
Then planted bugs in the new lines (each edition's text run in place of the file): each must make an F or G test fail.
  python3 -B test_aw1_rel1.py            (exit 0: every test passed and every planted bug was caught)"""
import contextlib, importlib.util, io, json, os, sys, tempfile, types
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.dirname(HERE); FO = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
I2G_DIR = os.path.join(TOOLS, 'idea_to_grade')
DET, I2G = os.path.join(HERE, 'detect_aw1_rel1.py'), os.path.join(HERE, 'idea_to_grade_aw1_rel1.py')
K12_DET = ('# detect_aw1_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the\n'
           '# release folder only"): a new edition for the clean release. Old file: alarm_process/detect_aw1.py 228630e3d0c30b20, never edited. It is\n'
           '# detect_v2.py 97a822a20e08088d (detect.py with its paths changed: --lab-root required, --gate, alarm_design_v3) with detect_aw1.py\'s\n'
           '# aw1 change and nothing else (the research window CLASSES from alarm_process/WINDOWS_ALARM_V1.tsv, its sha16 checked). detect_aw1.py\'s\n'
           '# header follows, then detect_v2.py\'s text.\n')
K12_I2G = ('# idea_to_grade_aw1_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from\n'
           '# the release folder only"): a new edition for the clean release. Old file: alarm_process/idea_to_grade_aw1.py e35b17019a3d34f6, never\n'
           '# edited. It is idea_to_grade_rel1.py edee6bbe51a2bbde (SCOUT K6: idea_to_grade.py V2.3.1 with its paths changed: the tree root from its\n'
           '# file, --lab-root and --pins required, --gate, the kernels i2g_engine_rel1, i2g_grade_rel1, detect_v2) with idea_to_grade_aw1.py\'s aw1\n'
           '# changes and nothing else: (1) the research window CLASSES from alarm_process/WINDOWS_ALARM_V1.tsv (sha16 checked); (2) the original\n'
           '# folder idea_to_grade/ (its rel1 kernels) first on sys.path; (3) its pins: --pins I2G_PINS_AW1_REL1.json beside it (relative paths;\n'
           '# rel1 has no default pins file). idea_to_grade_aw1.py\'s header follows, then idea_to_grade_rel1.py\'s text.\n')
ok = fail = 0
CHK = [0]                                                                # the F and G checks run (each c() call)


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1; print('FAIL', name)


def rep(t, a, b):
    assert t.count(a) == 1, ('not once', a[:80]); return t.replace(a, b)


def derive_detect():
    t = open(os.path.join(I2G_DIR, 'detect_v2.py')).read(); aw = open(os.path.join(HERE, 'detect_aw1.py')).read().split('\n')
    t = rep(t, '#!/usr/bin/env python3\n', '#!/usr/bin/env python3\n' + K12_DET + aw[1] + '\n' + aw[2] + '\n')
    t = rep(t, "ENGINE_PATH = TOOLS / 'alarm_design' / 'alarm_design_v3.py'\n", "ENGINE_PATH = TOOLS / 'alarm_design' / 'alarm_design_v3.py'\n"
            "WINDOWS_ALARM = TOOLS / 'alarm_process' / 'WINDOWS_ALARM_V1.tsv'; WINDOWS_ALARM_SHA16 = '37decf0075649f69'   # aw1: the alarm kit's window classes\n")
    i = [k for k, l in enumerate(aw) if 'if hashlib.sha256(WINDOWS_ALARM.read_bytes()).hexdigest()[:16] != WINDOWS_ALARM_SHA16:' in l][0]
    return rep(t, '    wins = gates.windows(); m = lo[:6]\n', '\n'.join(aw[i:i + 3]) + '\n')


def derive_grade():
    t = open(os.path.join(I2G_DIR, 'idea_to_grade_rel1.py')).read(); aw = open(os.path.join(HERE, 'idea_to_grade_aw1.py')).read().split('\n')
    t = K12_I2G + '\n'.join(aw[0:3]) + '\n' + t
    t = rep(t, 'if HERE not in sys.path:\n    sys.path.insert(0, HERE)\n', '\n'.join(aw[26:29]) + '\n')
    t = rep(t, "PINS_FILE = None                                                    # V2.3.1's released pins name past editions: its command here needs --pins\n",
            aw[43] + '\n' + "PINS_FILE = None                                                    # rel1: no default; aw1's run gives --pins I2G_PINS_AW1_REL1.json beside this file\n")
    t = rep(t, '    k = E.K.load(); wins = k.gates.windows(); law = k.gates.load_law()\n', '\n'.join(aw[264:268]) + '\n')
    return rep(t, "'month %s is in the %s window of %s' % (m, cls, k.gates.WINDOWS))", "'month %s is in the %s window of %s' % (m, cls, WINDOWS_ALARM))")


def machine_strings(text):
    """the string constants of a module's code (docstrings aside) that name a machine path"""
    import ast
    tree = ast.parse(text); docs = set()
    for n in [tree] + [x for x in ast.walk(tree) if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]:
        if n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], 'value', None), ast.Constant):
            docs.add(id(n.body[0].value))
    return [x.value for x in ast.walk(tree) if isinstance(x, ast.Constant) and isinstance(x.value, str) and id(x) not in docs
            and any(r in x.value for r in ('/Users/', '/Volumes/', '/home/'))]  # machine-path-ok: the test's own pattern of a machine path (test data)


def load(path, text=None, name=None):
    """a module from its file, or the given text run as that file (a planted bug)"""
    m = types.ModuleType(name or os.path.basename(path)[:-3] + '_t'); m.__file__ = path
    exec(compile(text if text is not None else open(path).read(), path, 'exec'), m.__dict__)
    return m


def refused(f, code):
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            f()
    except SystemExit as e:
        return code == 'SystemExit'
    except Exception as e:
        return code in str(e) or code == getattr(e, 'code', None)
    return False


def needs(G, argv, opt):
    """the command stops at its argument check, naming the missing option (argparse: exit 2, 'the following arguments are required')"""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            G.main(argv)
    except SystemExit as e:
        return e.code == 2 and 'required' in err.getvalue() and opt in err.getvalue()
    except Exception:
        return False
    return False


def f_tests(D, tag):
    """F: detect_aw1_rel1 (D: the module) -> failures"""
    out = []
    def c(name, cond):
        CHK[0] += 1
        if not cond: out.append('%s %s' % (tag, name))
    try:
        c('F1 Sep-Apr admitted', D.admit_research_window('20250901:20260430', '20250910', '20260430') == ('20250901', '20260430'))
    except Exception as e:
        c('F1 Sep-Apr admitted (%s)' % str(e)[:80], False)
    c('F3 June 2026 refused', refused(lambda: D.admit_research_window('20250901:20260630', '20250910', '20260630'), 'RESEARCH_WINDOW_NOT_BUILD'))
    keep = D.WINDOWS_ALARM_SHA16; D.WINDOWS_ALARM_SHA16 = '0' * 16
    c('F4 a changed table refused', refused(lambda: D.admit_research_window('20250901:20251231', '20250910', '20251231'), 'ALARM_WINDOWS_CHANGED'))
    D.WINDOWS_ALARM_SHA16 = keep
    with tempfile.TemporaryDirectory() as tmp:
        c('F5 no lab root refused', refused(lambda: D.run(os.path.join(tmp, 'd.json'), '20250910', '20251231', os.path.join(tmp, 'out'), os.path.join(tmp, 'r.json')), 'LAB_ROOT_REQUIRED')
          and not os.path.exists(os.path.join(tmp, 'out')))
        p = os.path.join(tmp, 'GATE.txt'); open(p, 'w').write('PAUSE\n'); a = D.gate_is_run(p); open(p, 'w').write('RUN\n'); b = D.gate_is_run(p)
        c('F6 the gate (none runs, PAUSE stops, RUN runs)', D.gate_is_run('') is True and D.gate_is_run(None) is True and a is False and b is True)
    c('F7 the engine is alarm_design_v3', str(D.ENGINE_PATH).endswith('/alarm_design/alarm_design_v3.py') and os.path.isfile(str(D.ENGINE_PATH)))
    c('F8 the window table is the alarm kit\'s', str(D.WINDOWS_ALARM) == os.path.join(HERE, 'WINDOWS_ALARM_V1.tsv'))
    return out


def g_tests(G, tag):
    """G: idea_to_grade_aw1_rel1 (G: the module) -> failures"""
    out = []
    def c(name, cond):
        CHK[0] += 1
        if not cond: out.append('%s %s' % (tag, name))
    try:
        G.check_window(('20250901', '20260430'), '20250910', '20260430'); c('G1 Sep-Apr admitted', True)
    except Exception as e:
        c('G1 Sep-Apr admitted (%s)' % str(e)[:80], False)
    c('G3 June 2026 refused', refused(lambda: G.check_window(('20250901', '20260630'), '20250910', '20260630'), 'RESEARCH_WINDOW_NOT_BUILD'))
    keep = G.WINDOWS_ALARM_SHA16; G.WINDOWS_ALARM_SHA16 = '0' * 16
    c('G4 a changed table refused', refused(lambda: G.check_window(('20250901', '20251231'), '20250910', '20251231'), 'ALARM_WINDOWS_CHANGED'))
    G.WINDOWS_ALARM_SHA16 = keep
    c('G5 no machine default', G.GATE is None and G.LAB_ROOT is None and G.PINS_FILE is None and G.F == FO and G.TOOLS == FO + '/team/RESEARCH/tools')
    c('G5 the window table is the alarm kit\'s', G.WINDOWS_ALARM == os.path.join(HERE, 'WINDOWS_ALARM_V1.tsv'))
    c('G9 the kernels\' folder first on sys.path is idea_to_grade/ of this tree', getattr(G, 'I2G', None) == I2G_DIR and I2G_DIR in sys.path)
    try:
        real = G.load_pins(os.path.join(HERE, 'I2G_PINS_AW1_REL1.json'))
        c('G6 the pins map into the tree', len(real) == 39 and all(q.startswith(FO + os.sep) and os.path.isfile(q) for q in real)
          and os.path.join(HERE, 'idea_to_grade_aw1_rel1.py') in real)
    except Exception as e:
        c('G6 the pins map into the tree (%s)' % str(e)[:80], False)
    with tempfile.TemporaryDirectory() as tmp:
        q = os.path.join(tmp, 'P.json'); json.dump({'pins': {'/abs/x.py': '0' * 16}}, open(q, 'w'))
        c('G6 an absolute pin refused', refused(lambda: G.load_pins(q), 'PINS_FILE'))
    base = ['--events', 'x.tsv', '--events-sha16', '0' * 16, '--roster', 'r.json', '--first', '20250910', '--last', '20251231',
            '--research-window', '20250901:20251231', '--out', 'o']
    c('G7 the command needs --pins', needs(G, base + ['--lab-root', '/x'], '--pins'))
    c('G7 the command needs --lab-root', needs(G, base + ['--pins', 'p.json'], '--lab-root'))
    try:
        G.warm(); import importlib
        mods = {n: getattr(sys.modules.get(n), '__file__', None) for n in ('i2g_engine_rel1', 'i2g_grade_rel1', 'detect_v2')}
        c('G8 the rel1 kernels from idea_to_grade/ in this tree', all(f and os.path.realpath(f) == os.path.join(I2G_DIR, n + '.py') for n, f in mods.items()))
    except Exception as e:
        c('G8 the rel1 kernels from idea_to_grade/ in this tree (%s)' % str(e)[:80], False)
    return out


DET_BUGS = [("WINDOWS_ALARM = TOOLS / 'alarm_process' / 'WINDOWS_ALARM_V1.tsv'", "WINDOWS_ALARM = TOOLS / 'freeze_judge' / 'WINDOWS_V1.tsv'"),
            ("wins = gates.windows(str(WINDOWS_ALARM)); m = lo[:6]", "wins = gates.windows(); m = lo[:6]"),
            ("    if hashlib.sha256(WINDOWS_ALARM.read_bytes()).hexdigest()[:16] != WINDOWS_ALARM_SHA16:   # aw1\n        raise Refusal('ALARM_WINDOWS_CHANGED',",
             "    if False:\n        raise Refusal('ALARM_WINDOWS_CHANGED',"),
            ("WINDOWS_ALARM_SHA16 = '37decf0075649f69'", "WINDOWS_ALARM_SHA16 = 'd9c5c1a21ceea8f4'"),
            ("ENGINE_PATH = TOOLS / 'alarm_design' / 'alarm_design_v3.py'", "ENGINE_PATH = TOOLS / 'alarm_design' / 'alarm_design_v2.py'"),
            ("    if _reader is None and (lab_root is None or str(lab_root) == ''):\n        raise Refusal('LAB_ROOT_REQUIRED'",
             "    if False:\n        raise Refusal('LAB_ROOT_REQUIRED'"),
            ("    if not gate:\n        return True\n    from labcore import jobgate", "    if True:\n        return True\n    from labcore import jobgate")]
I2G_BUGS = [("I2G = os.path.join(os.path.dirname(HERE), 'idea_to_grade')", "I2G = HERE"),
            ("    wins = k.gates.windows(WINDOWS_ALARM)   # aw1", "    wins = k.gates.windows()   # aw1"),
            ("    if hashlib.sha256(open(WINDOWS_ALARM, 'rb').read()).hexdigest()[:16] != WINDOWS_ALARM_SHA16:   # aw1\n        raise Refused('ALARM_WINDOWS_CHANGED',",
             "    if False:\n        raise Refused('ALARM_WINDOWS_CHANGED',"),
            ("WINDOWS_ALARM = os.path.join(HERE, 'WINDOWS_ALARM_V1.tsv')", "WINDOWS_ALARM = os.path.join(TOOLS, 'freeze_judge', 'WINDOWS_V1.tsv') if 0 else os.path.join(HERE, '..', 'freeze_judge', 'WINDOWS_V1.tsv')"),
            ("PINS_FILE = None                                                    # rel1: no default", "PINS_FILE = os.path.join(HERE, 'I2G_PINS_AW1.json')  # rel1: no default"),
            ("        if os.path.isabs(q) or '/../' in '/%s/' % q:", "        if False:"),
            ("GATE = None                     # the feed's stop gate file", "GATE = '<LAB_REPO>/forensics/team/FEED/stops/BACKFILL_GATE.txt'  # machine-path-ok: a planted bug (test data)\n_X = None                     # the feed's stop gate file"),  # machine-path-ok: a planted bug (test data)
            ("    p.add_argument('--pins', required=True,", "    p.add_argument('--pins', required=False,")]


def main():
    d_text, g_text = open(DET).read(), open(I2G).read()
    check('D1 detect_aw1_rel1.py is detect_v2.py with the aw1 change, byte for byte', derive_detect() == d_text)
    check('D2 idea_to_grade_aw1_rel1.py is idea_to_grade_rel1.py with the aw1 changes, byte for byte', derive_grade() == g_text)
    check('D3 no machine path in either edition\'s code (string constants other than docstrings)', not machine_strings(d_text) and not machine_strings(g_text))
    D = load(DET); V2 = load(os.path.join(I2G_DIR, 'detect_v2.py'), name='detect_v2_t')
    for x in f_tests(D, 'detect_aw1_rel1'):
        check(x, False)
    check('F2 detect_v2 refuses Sep-Apr (WINDOWS_V1: Mar is CHECK): the aw1 change is what admits it',
          refused(lambda: V2.admit_research_window('20250901:20260430', '20250910', '20260430'), 'RESEARCH_WINDOW_NOT_BUILD'))
    G = load(I2G)
    for x in g_tests(G, 'idea_to_grade_aw1_rel1'):
        check(x, False)
    R1 = load(os.path.join(I2G_DIR, 'idea_to_grade_rel1.py'), name='idea_to_grade_rel1_t')
    check('G2 idea_to_grade_rel1 refuses Sep-Apr (WINDOWS_V1): the aw1 change is what admits it',
          refused(lambda: R1.check_window(('20250901', '20260430'), '20250910', '20260430'), 'RESEARCH_WINDOW_NOT_BUILD'))
    n = ok + CHK[0] - fail                                                         # the D checks, F2, G2 and every F and G check
    print('AW1 REL1 TESTS', 'PASS (%d checks)' % n if not fail else 'FAIL (%d failed)' % fail)
    killed = 0
    for a, b in DET_BUGS:
        assert d_text.count(a) == 1, ('detect bug target not found once', a)
        try:
            f = f_tests(load(DET, d_text.replace(a, b, 1), name='detect_aw1_rel1_bug'), 'bug')
        except Exception as e:
            f = ['load: %s' % str(e)[:80]]
        killed += bool(f); print('PLANTED BUG detect %-60s %s' % (b.strip().split('\n')[0][:60], 'KILLED (%s)' % f[0][:60] if f else 'SURVIVED'))
    for a, b in I2G_BUGS:
        assert g_text.count(a) == 1, ('grade bug target not found once', a)
        try:
            f = g_tests(load(I2G, g_text.replace(a, b, 1), name='idea_to_grade_aw1_rel1_bug'), 'bug')
        except Exception as e:
            f = ['load: %s' % str(e)[:80]]
        killed += bool(f); print('PLANTED BUG grade  %-60s %s' % (b.strip().split('\n')[0][:60], 'KILLED (%s)' % f[0][:60] if f else 'SURVIVED'))
    n = len(DET_BUGS) + len(I2G_BUGS)
    print('PLANTED BUGS %d of %d killed (by the F and G tests alone; D1 and D2 catch any change of either file)' % (killed, n))
    return 0 if not fail and killed == n else 1


if __name__ == '__main__':
    sys.exit(main())
