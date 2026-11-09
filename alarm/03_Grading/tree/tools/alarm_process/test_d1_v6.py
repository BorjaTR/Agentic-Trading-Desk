#!/usr/bin/env python3
"""test_d1_v6.py (SCO-A162 for SCOUT, 6 Nov 2026; GPT SCO-A162-REV2). TEST, NOT REVIEWED. test_d1_v5.py with D8 counting a 0 list as 1 and D7 against v5.
Unit tests D1 to D9 of d1_reports_v6.py's Outcomes workers (D1_EO_WORKERS), planted data only, seconds: a planted lab3.evt writer,
a planted Outcomes edition (its run(n) writes one part file per event day through the writer it is given and records n beside the
root) and a planted card; no data store, no network.
  D1 eo_workers: absent and missing keys 0; 'ALARM=3,RND=5'; 0 and 8 kept; 9 and -1 exit 2
  D2 outcomes(NW=0) is v3: run(0) with the capture, <root>.mem.pkl written; outcomes(NW=3): run(3), no .mem.pkl; part files equal
  D3 a failing Outcomes run gives rc 1, its traceback in <root>.log, and no .mem.pkl
  D4 mem_of keeps only roots that have a .mem.pkl (a run(n) root is read from its store)
  D5 chain with D1_EO_WORKERS=ALARM=2,RND=4: each list's run gets its own count (2 and 4), steps outcomes_alarm, outcomesRND, card
     all rc 0, the card gets --windows GRADE; without D1_EO_WORKERS both runs are run(0) with .mem.pkl (v3); both chains' parts equal
  D6 chain refuses a bad count before any run: exit 2, no steps file, no Outcomes root
  D7 the text is d1_reports_v5's except eo_budget (skipped under D1_MUTANT=1)
  D8 the budget (a 0 list counts 1): ALARM=3,RND=5, ALARM=8 with one list, ALARM=0,RND=7 and both 0 run; ALARM=8,RND=8, ALARM=5,RND=4, ALARM=0,RND=8 and ALARM=8,RND=0 exit 2 before any run (no steps file, no root)
  D9 a non-integer value (ALARM=x, ALARM=-1, ALARM=) exits 2 with a message, never a traceback
Run:  python3 -B test_d1_v4.py [D1 D2 ...]
Env:  D1_TOOL = the file under test (default d1_reports_v6.py beside this file; a mutant copy for the mutant runs; d1_mem_v2.py
      must sit beside it); D1_V5 = d1_reports_v5.py for D7 (default beside the tool); D1_SCRATCH = planted inputs (default
      ../scratch; kept, never removed)
Exit 0 all passed, 1 a test failed. The planted modules are dropped from sys.modules after each test (run_isolated, job 20270365)."""
import sys
sys.dont_write_bytecode = True
import ast, contextlib, datetime as dt, filecmp, importlib, io, os, pickle, traceback

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.realpath(os.environ.get('D1_TOOL') or os.path.join(HERE, 'd1_reports_v6.py'))
V5 = os.environ.get('D1_V5') or os.path.join(os.path.dirname(TOOL), 'd1_reports_v5.py')
SCRATCH = os.environ.get('D1_SCRATCH') or os.path.join(os.path.dirname(HERE), 'scratch')
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
sys.path.insert(0, os.path.dirname(TOOL))
D1 = importlib.import_module(os.path.basename(TOOL)[:-3])      # by name: the spawned Outcomes processes import it the same way
_N = [0]
DAY0 = int(dt.datetime(2025, 10, 1, tzinfo=dt.timezone.utc).timestamp())

EVT = '''import json, os
def write_part(root, day, part, codes, coins, **kw):
    d = os.path.join(root, part); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'day=%s.json' % day), 'x') as f:
        json.dump({'codes': codes, 'coins': coins}, f, sort_keys=True)
'''
FAKE_EO = '''import os
def _window_arg(d):
    return d['run-window']
def run(n, LAB, CODE, IN, G, SUBJ, FIRST, LAST, OUT, run_window=None, roots=None, log=None, inprocess_write=None):
    from lab3 import evt
    if os.path.basename(IN).startswith('FAIL'):
        raise RuntimeError('planted Outcomes failure')
    with open(OUT + '.n', 'x') as f:
        f.write('%d %s' % (n, 'capture' if inprocess_write is not None else 'store'))
    w = inprocess_write or evt.write_part
    rows = [l.rstrip('\\n').split('\\t') for l in open(IN)][1:]
    by = {}
    for c, t, s in rows:
        by.setdefault(int(t) // 86400, []).append((c, int(t), int(s)))
    for day in sorted(by):
        coins = sorted(set(r[0] for r in by[day]))
        codes = {'E.RET': {'kind': 'f', 'rows': {c: {'t': [r[1] for r in by[day] if r[0] == c], 'v': [r[2] * 0.5 for r in by[day] if r[0] == c]} for c in coins}}}
        w(OUT, day, 'OUT.' + SUBJ, codes, coins)
    log('planted run(%d) %d days' % (n, len(by)))
'''
FAKE_READ = '''class Refused(Exception):
    pass
def read(out_root, code_dir, subject, cols=None, first=None, last=None):
    return {'root': out_root}
'''
CARD = '''import sys
print('CARD', ' '.join(sys.argv[1:]))
'''


def new_dir(tag):
    _N[0] += 1
    d = os.path.join(SCRATCH, 'd1v6_%s_%s_%d' % (STAMP, tag, _N[0])); os.makedirs(d); return d


def plant(d):
    F = os.path.join(d, 'F'); code = os.path.join(F, 'team', 'LAB3', 'code', 'lab3'); os.makedirs(code)
    open(os.path.join(code, '__init__.py'), 'w').close(); open(os.path.join(code, 'evt.py'), 'w').write(EVT)
    eo = os.path.join(F, 'team', 'RESEARCH', 'tools', 'event_outcomes'); os.makedirs(eo)
    open(os.path.join(eo, 'event_outcomes.py'), 'w').write(FAKE_READ)
    EO = os.path.join(d, 'event_outcomes_planted.py'); open(EO, 'w').write(FAKE_EO)
    CD = os.path.join(d, 'card_planted.py'); open(CD, 'w').write(CARD)
    W = os.path.join(d, 'W'); os.makedirs(W)
    for name, k in (('V1_FIRES_V1_LIST.tsv', 0), ('RND_V1_V1_LIST.tsv', 1)):
        with open(os.path.join(W, name), 'w') as f:
            f.write('coin\tt\tside\n')
            for day in (0, 1, 3):
                for j, c in enumerate(('AAA', 'BBB', 'CCC')[:2 + k]):
                    f.write('%s\t%d\t%d\n' % (c, DAY0 + day * 86400 + 600 * (j + 1) + k, 1 if j % 2 else -1))
    return F, EO, CD, W


def files(root):
    out = []
    for dp, dns, fns in os.walk(root):
        dns.sort(); out += [os.path.relpath(os.path.join(dp, f), root) for f in sorted(fns)]
    return out


def same_tree(a, b):
    fa, fb = files(a), files(b)
    assert fa == fb and fa, (fa, fb)
    for r in fa:
        assert filecmp.cmp(os.path.join(a, r), os.path.join(b, r), shallow=False), r


@contextlib.contextmanager
def env(**kw):
    old = {k: os.environ.get(k) for k in kw}
    for k, v in kw.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    try:
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def oc_args(F, W, EO, x, nw, lst=None):
    IN = lst or os.path.join(W, 'V1_FIRES_V1_LIST.tsv' if not x else 'RND_V1_V1_LIST.tsv')
    return (F, IN, 'G.json', 'IDEA2V1%sMENU' % x, '20250910', '20251231', '20250901:20251231', os.path.join(W, 'om_V1%s_v1_%d' % (x, nw)),
            '/planted/lab', EO, nw)


def D1_():
    with env(D1_EO_WORKERS=None):
        assert D1.eo_workers('ALARM') == 0 and D1.eo_workers('RND') == 0
    with env(D1_EO_WORKERS='ALARM=3,RND=5'):
        assert (D1.eo_workers('ALARM'), D1.eo_workers('RND')) == (3, 5)
    with env(D1_EO_WORKERS='RND=8'):
        assert (D1.eo_workers('ALARM'), D1.eo_workers('RND')) == (0, 8)
    with env(D1_EO_WORKERS='ALARM=0,RND=1'):
        assert (D1.eo_workers('ALARM'), D1.eo_workers('RND')) == (0, 1)
    for bad in ('ALARM=9', 'ALARM=-1'):
        with env(D1_EO_WORKERS=bad), contextlib.redirect_stderr(io.StringIO()):
            try:
                D1.eo_workers('ALARM'); raise AssertionError('no exit for %s' % bad)
            except SystemExit as e:
                assert e.code == 2, (bad, e.code)


def D2_():
    d = new_dir('D2'); F, EO, CD, W = plant(d)
    r0 = D1.outcomes(oc_args(F, W, EO, '', 0)); r3 = D1.outcomes(oc_args(F, W, EO, '', 3))
    assert r0[0] == 0 and r3[0] == 0, (r0, r3, open(oc_args(F, W, EO, '', 3)[7] + '.log').read()[-300:])
    a, b = oc_args(F, W, EO, '', 0)[7], oc_args(F, W, EO, '', 3)[7]
    assert open(a + '.n').read() == '0 capture' and open(b + '.n').read() == '3 store', (open(a + '.n').read(), open(b + '.n').read())
    assert os.path.isfile(a + '.mem.pkl') and not os.path.exists(b + '.mem.pkl')
    x = pickle.load(open(a + '.mem.pkl', 'rb')); assert x['part'] == 'OUT.IDEA2V1MENU' and len(x['days']) == 3, (x['part'], x['days'].keys())
    same_tree(a, b)


def D3_():
    d = new_dir('D3'); F, EO, CD, W = plant(d)
    bad = os.path.join(W, 'FAIL_LIST.tsv'); open(bad, 'w').write('coin\tt\tside\n')
    for nw in (0, 4):
        a = oc_args(F, W, EO, '', nw, bad); rc, sec = D1.outcomes(a)
        assert rc == 1, (nw, rc)
        assert 'planted Outcomes failure' in open(a[7] + '.log').read()
        assert not os.path.exists(a[7] + '.mem.pkl')


def D4_():
    d = new_dir('D4'); F, EO, CD, W = plant(d)
    a, b = oc_args(F, W, EO, '', 0)[7], oc_args(F, W, EO, 'RND', 5)[7]
    assert D1.outcomes(oc_args(F, W, EO, '', 0))[0] == 0 and D1.outcomes(oc_args(F, W, EO, 'RND', 5))[0] == 0
    d1, mem = D1.mem_of([a, b])
    assert list(mem) == [os.path.realpath(a)], list(mem)
    assert mem[os.path.realpath(a)][1] == 'IDEA2V1MENU'


def chain(F, W, EO, CD, workers):
    with env(D1_EO_WORKERS=workers, EO_WINDOWS='GRADE'):
        return D1.chain(F, W, 'V1', '/planted/lab', 'G.json', '20250910', '20251231', '20250901:20251231', 'FADE', '1', '', 'ALARM RND',
                        EO, CD)


def D5_():
    d = new_dir('D5'); outs = {}
    for tag, wk in (('n', 'ALARM=2,RND=4'), ('v3', None)):
        F, EO, CD, W = plant(os.path.join(d, tag))
        assert chain(F, W, EO, CD, wk) == 0
        st = [l.rstrip('\n').split('\t') for l in open(os.path.join(W, 'd1_V1_steps.tsv'))]
        assert [(s[0], s[1]) for s in st] == [('outcomes_alarm', '0'), ('outcomesRND', '0'), ('card', '0')], st
        n = (open(os.path.join(W, 'om_V1_v1.n')).read(), open(os.path.join(W, 'om_V1RND_v1.n')).read())
        pk = tuple(os.path.isfile(os.path.join(W, r + '.mem.pkl')) for r in ('om_V1_v1', 'om_V1RND_v1'))
        if tag == 'n':
            assert n == ('2 store', '4 store') and pk == (False, False), (n, pk)
        else:
            assert n == ('0 capture', '0 capture') and pk == (True, True), (n, pk)
        assert '--windows GRADE' in open(os.path.join(W, 'CARD_V1.txt')).read()
        outs[tag] = W
    for r in ('om_V1_v1', 'om_V1RND_v1'):
        same_tree(os.path.join(outs['n'], r), os.path.join(outs['v3'], r))
    assert open(os.path.join(outs['n'], 'CARD_V1.txt')).read().replace(outs['n'], 'W') == \
        open(os.path.join(outs['v3'], 'CARD_V1.txt')).read().replace(outs['v3'], 'W')


def D6_():
    d = new_dir('D6'); F, EO, CD, W = plant(d)
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            chain(F, W, EO, CD, 'ALARM=3,RND=12'); raise AssertionError('no exit')
        except SystemExit as e:
            assert e.code == 2, e.code
    assert not os.path.exists(os.path.join(W, 'd1_V1_steps.tsv')) and not os.path.exists(os.path.join(W, 'om_V1_v1'))


def defs(path):
    src = open(path).read(); out = {}
    for n in ast.parse(src).body:
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
    return out


def D7_():
    if os.environ.get('D1_MUTANT') == '1':
        return
    a, b = defs(V5), defs(TOOL)
    assert set(b) == set(a), (set(b) - set(a), set(a) - set(b))
    assert {k for k in a if a[k] != b[k]} == {'eo_budget'}, {k for k in a if a[k] != b[k]}


def chain_xs(F, W, EO, CD, workers, xs, screen):
    with env(D1_EO_WORKERS=workers, EO_WINDOWS='GRADE'):
        return D1.chain(F, W, 'V1', '/planted/lab', 'G.json', '20250910', '20251231', '20250901:20251231', 'FADE', screen, '', xs, EO, CD)


def D8_():
    d = new_dir('D8')
    F, EO, CD, W = plant(os.path.join(d, 'ok'))
    assert chain(F, W, EO, CD, 'ALARM=3,RND=5') == 0
    assert (open(os.path.join(W, 'om_V1_v1.n')).read(), open(os.path.join(W, 'om_V1RND_v1.n')).read()) == ('3 store', '5 store')
    F, EO, CD, W = plant(os.path.join(d, 'one'))
    assert chain_xs(F, W, EO, CD, 'ALARM=8', 'ALARM', '1') == 0
    assert open(os.path.join(W, 'om_V1_v1.n')).read() == '8 store' and not os.path.exists(os.path.join(W, 'om_V1RND_v1'))
    for ok, want in (('ALARM=0,RND=7', ('0 capture', '7 store')), ('ALARM=0,RND=0', ('0 capture', '0 capture'))):
        F, EO, CD, W = plant(os.path.join(d, 'ok_' + ok.replace(',', '_').replace('=', '')))
        assert chain(F, W, EO, CD, ok) == 0, ok
        assert (open(os.path.join(W, 'om_V1_v1.n')).read(), open(os.path.join(W, 'om_V1RND_v1.n')).read()) == want, ok
    for bad in ('ALARM=8,RND=8', 'ALARM=5,RND=4', 'ALARM=0,RND=8', 'ALARM=8,RND=0'):
        F, EO, CD, W = plant(os.path.join(d, 'bad_' + bad.replace(',', '_').replace('=', '')))
        er = io.StringIO()
        with contextlib.redirect_stderr(er):
            try:
                chain(F, W, EO, CD, bad); raise AssertionError('no exit for %s' % bad)
            except SystemExit as e:
                assert e.code == 2, (bad, e.code)
        assert 'D1_EO_WORKERS_BUDGET' in er.getvalue(), er.getvalue()
        assert not os.path.exists(os.path.join(W, 'd1_V1_steps.tsv')) and not os.path.exists(os.path.join(W, 'om_V1_v1')), bad


def D9_():
    for bad in ('ALARM=x', 'ALARM=-1', 'ALARM=', 'ALARM=2.5'):
        er = io.StringIO()
        with env(D1_EO_WORKERS=bad), contextlib.redirect_stderr(er):
            try:
                D1.eo_workers('ALARM'); raise AssertionError('no exit for %s' % bad)
            except SystemExit as e:
                assert e.code == 2, (bad, e.code)
        assert 'D1_EO_WORKERS' in er.getvalue(), bad


def forget_planted():
    """the planted modules (lab3, event_outcomes, the planted Outcomes) leave sys.modules after each test: the package suite's
    run_isolated counts every loaded module outside the Alarm folder (job 20270365)"""
    root = os.path.realpath(SCRATCH) + os.sep
    for k, m in list(sys.modules.items()):
        f = getattr(m, '__file__', None)
        if f and os.path.realpath(f).startswith(root):
            del sys.modules[k]


TESTS = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9']   # v6: D7 against v5, D8 with the 0-counts-1 cases
if __name__ == '__main__':
    os.makedirs(SCRATCH, exist_ok=True)
    want = sys.argv[1:] or TESTS; bad = 0
    for n in want:
        try:
            globals()[n + '_'](); print('PASS', n)
        except (Exception, SystemExit):
            bad += 1; print('FAIL', n); traceback.print_exc(limit=4)
        forget_planted()
    print('RESULT %d of %d passed (%s)' % (len(want) - bad, len(want), os.path.basename(TOOL)))
    sys.exit(1 if bad else 0)
