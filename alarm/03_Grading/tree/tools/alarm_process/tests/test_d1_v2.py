#!/usr/bin/env python3
"""test_d1_v2.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED): the tests of V2_0 stage 2 D1 (d1_mem_v2.py, d1_reports_v2.py, chains v2_0_6
and v2_2_6, JOB_GRADE_V11, JOB_MONTH_V11), planted data only, seconds:
  M1  a committed planted Outcomes run (event_outcomes_rel1.run(0) with d1_mem_v2.Capture, the price source planted as in
      event_outcomes/test_outcomes_v3.py): for every column event_outcomes.read == mem_read (each field, dtype, numbers by their bits),
      also with first/last and a column subset; empty cells keep their reasons.
  M2  refusals: another subject (SUBJECT), an unknown column (COLUMN), a capture missing a day (MEM_MISMATCH).
  M3  install: event_outcomes.read answers from memory for the captured root, the real read for another root.
  C1  the chains' D1 block with a fake driver: STATUS lines in the steps file's order, an Outcomes failure exits 6, a driver crash
      writes 'd1' and exits 6, the card's rc is the chain's rc (both chains).
  J1  JOB_GRADE_V11 pins and calls chain v2_0_6, runs perfire and the hand-off through d1_reports_v2.py, # CORES 3; JOB_MONTH_V11 pins
      and calls chain v2_2_6 and runs perfire through d1_reports_v2.py.
  J2  every pin in both templates (`ck <path> <sha16>`, paths resolved from the template's own VAR=$X/... lines, files of this package
      only) and both chains' D1_SHA and MEM_SHA equal the file they name (ALARM_V1_9's proof job 20265254 stopped at a stale pin).
  K1  a killed Outcomes worker (an edition whose run kills its own process): d1_reports_v2.py chain ends in seconds with rc 1 for both
      runs, no menu or card, the reason on stderr, so the chain exits 6 (CONDUCTOR's must M1, REVIEW_SCOUT_D1_CODE_V2.md bcf771a7a532540e).
Then planted bugs in copies of d1_mem_v2.py, of the chain block and of d1_reports_v2.py (the Pool.map it had): each must fail a test.
  python3 -B <Alarm>/03_Grading/tree/tools/alarm_process/tests/test_d1_v2.py"""
import importlib.util, json, os, re, shutil, signal, subprocess, sys, tempfile, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AP3 = os.path.dirname(HERE)
PKG = os.path.abspath(os.path.join(AP3, '..', '..', '..', '..'))
TOOLS = os.path.join(PKG, '01_Detection', 'tree', 'team', 'RESEARCH', 'tools')
CODE = os.path.join(PKG, '01_Detection', 'tree', 'team', 'LAB3', 'code')
MEMPY = os.path.join(AP3, 'd1_mem_v2.py')
GCH = os.path.join(AP3, 'alarm_grade_chain_v2_0_6_to20251231.sh')
MCH = os.path.join(PKG, '03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_6_to20260430.sh')
K5 = os.path.join(PKG, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'jobs')
REP = os.path.join(AP3, 'd1_reports_v2.py')
KF = os.path.abspath(os.path.join(TOOLS, '..', '..', '..'))   # the F of d1_reports_v2.tools(F): F/team/RESEARCH/tools, F/team/LAB3/code
os.environ.setdefault('FEED_GATE', '')
for p in (CODE, os.path.join(TOOLS, 'event_outcomes'), TOOLS):
    sys.path.insert(0, p)
T0 = 1760486400                                   # 2025-10-15 00:00:00 UTC
N = [0]


def load(path, name=None):
    N[0] += 1
    sp = importlib.util.spec_from_file_location(name or 'm%d' % N[0], path)
    if sp is None or sp.loader is None:
        raise ImportError(path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


import event_outcomes as EO  # noqa: E402  pyright: ignore[reportMissingImports]
EOR = load(os.path.join(TOOLS, 'event_outcomes', 'event_outcomes_rel1.py'), 'event_outcomes_rel1')
from lab3 import write as LW  # noqa: E402  pyright: ignore[reportMissingImports]


class FakeSrc:
    """test_outcomes_v3.py's planted price source: flat 100, one coin's bars rising"""
    def __init__(self, lab_root, code_dir, pins=None):
        self.pins = pins; self.pc = type('PC', (), {'reads': 0, 'mem': {}})()

    def state(self, coin, day):
        return 'NO_COIN' if coin == 'XRP' else 'LISTED'

    def bars(self, coin, t0, t1):
        te = np.arange(t0, t1 + 1, EOR.BAR_US, dtype=np.int64); c = np.full(len(te), 100.0)
        if coin == 'ETH':
            c = c + np.arange(len(te)) * 0.01
        return te, c, c.copy(), c.copy()

    def drop_before(self, day):
        pass


def planted_runs(tmp):
    EOR.PriceSource = FakeSrc
    EOR.ES.read_inputs = lambda s, *a, **k: {u: np.full(len(a[4]), 1.0) for u in s['inputs']}
    st = os.path.join(tmp, 's.json')
    json.dump(dict(name='T3', entry={'delay_s': 6, 'gap_s': 60}, directions=['LONG', 'SHORT'],
                   labels=[dict(name='RET5', kind='return', horizon_min=5, unit='pct'), dict(name='REACH1', kind='reach', target=1, horizon_min=5, unit='pct')]), open(st, 'w'))
    ev = os.path.join(tmp, 'e.tsv')
    open(ev, 'w').write('coin\tt\tside\n' + ''.join('%s\t%s\t%s\n' % r for r in [('BTC', T0, 1), ('ETH', T0 + 60, -1), ('XRP', T0 + 120, 1),
                                                                                     ('BTC', T0 + 86400, -1), ('ETH', T0 + 86460, 1)]))
    os.makedirs(os.path.join(tmp, 'lab'), exist_ok=True)
    d1 = load(MEMPY); cap = d1.Capture(LW.write_part); outs = []
    for i, w in enumerate((cap, None)):
        out = os.path.join(tmp, 'run%d' % i)
        EOR.run(0, os.path.join(tmp, 'lab'), CODE, ev, st, 'T3', '20251015', '20251016', out, run_window=('20251015', '20251016'),
                check_release=False, log=lambda *a: None, inprocess_write=w)
        outs.append(out)
    return cap, outs


def same(a, b):
    if set(a) != set(b):
        return 'keys'
    for k in a:
        x, y = a[k], b[k]
        if isinstance(x, str) or isinstance(y, str):
            if x != y:
                return k
            continue
        if x.dtype != y.dtype or x.shape != y.shape:
            return k + ' dtype/shape'
        if x.dtype == float:
            if not np.array_equal(x.view('<u8'), y.view('<u8')):
                return k + ' bits'
        elif x.size and not (x == y).all():
            return k
    return ''


def suite(mempy, cap, outs):
    f = []
    def ck(name, ok):
        if not ok:
            f.append(name)
    d1 = load(mempy); c = d1.Capture(None); c.part = cap.part; c.days = cap.days
    real = EO.read(outs[0], CODE, 'T3'); mem = d1.mem_read(EO, c, outs[0], CODE, 'T3')
    ck('M1 the columns', list(real) == list(mem) and len(real) > 3)
    ck('M1 every column equal', all(same(real[k], mem.get(k, {})) == '' for k in real))
    ck('M1 empty cells keep reasons', any(((r['reason'] != '') & (r['kind'] == 'number')).any() if r['kind'] == 'number' else False for r in mem.values()))
    r1 = EO.read(outs[0], CODE, 'T3', ['RET5__LONG'], first='20251016'); m1 = d1.mem_read(EO, c, outs[0], CODE, 'T3', ['RET5__LONG'], first='20251016')
    ck('M1 first and a subset', list(r1) == list(m1) == ['RET5__LONG'] and same(r1['RET5__LONG'], m1['RET5__LONG']) == '' and len(m1['RET5__LONG']['coin']) == 2)
    for name, fn, exc, word in (('M2 subject', lambda: d1.mem_read(EO, c, outs[0], CODE, 'T4'), EO.Refused, 'SUBJECT'),
                                ('M2 column', lambda: d1.mem_read(EO, c, outs[0], CODE, 'T3', ['NOPE']), EO.Refused, 'COLUMN')):
        try:
            fn(); ck(name, False)
        except exc as e:
            ck(name, word in str(e))
        except Exception:
            ck(name, False)
    c2 = d1.Capture(None); c2.part = cap.part; c2.days = {k: v for k, v in cap.days.items() if k != max(cap.days)}
    try:
        d1.mem_read(EO, c2, outs[0], CODE, 'T3'); ck('M2 a missing day', False)
    except ValueError as e:
        ck('M2 a missing day', 'MEM_MISMATCH' in str(e))
    except Exception:
        ck('M2 a missing day', False)
    real_read = EO.read
    try:
        d1.install(EO, {os.path.realpath(outs[0]): (c, 'T3')})
        calls = []
        old = d1.mem_read
        d1.mem_read = lambda *a, **k: (calls.append(1), old(*a, **k))[1]
        x = EO.read(outs[0], CODE, 'T3'); y = EO.read(outs[1], CODE, 'T3')
        ck('M3 memory for the captured root', calls == [1] and all(same(x[k], real[k]) == '' for k in real))
        ck('M3 the real read for another', all(same(y[k], real[k]) == '' for k in real))
    finally:
        EO.read = real_read
    return f


def block(chain):
    t = open(chain).read(); i = t.index('# 5-7 (V2_0 stage 2 D1)'); j = t.index('[ $rc -eq 0 ] && rc=$rc2; st done $rc 0 "$W"; exit $rc')
    return t[i:j + len('[ $rc -eq 0 ] && rc=$rc2; st done $rc 0 "$W"; exit $rc')]


def chain_case(text, steps, drv_rc, tmp):
    W = os.path.join(tmp, 'W%d' % N[0]); N[0] += 1; os.makedirs(W)
    fake = os.path.join(tmp, 'fakedrv.py')
    open(fake, 'w').write('import sys, os\nW, V = sys.argv[3], sys.argv[4]\nopen(os.path.join(W, "d1_%s_steps.tsv" % V), "w").write(os.environ["STEPS"])\nsys.exit(int(os.environ["DRC"]))\n')
    h = ('set -u; W=%s; V=PB3; F=/x; LAB_DAYS=/x; G=/x; FIRST=1; LAST=2; XS="ALARM RND"; EO=/x; T=/x; AP=/x; PY=%s; H=%s\n'
         'S=$W/STATUS.tsv; st(){ printf "%%s\\t%%s\\t%%s\\t%%s\\n" "$1" "$2" "$3" "$4" >> "$S"; }\n'
         'nice(){ shift 2; "$@"; }\n' % (W, sys.executable, tmp))
    text = text.replace('$H/d1_reports_v2.py', fake)
    p = subprocess.run(['bash', '-c', h + text], env=dict(os.environ, STEPS=steps, DRC=str(drv_rc)), capture_output=True, text=True)
    s = open(os.path.join(W, 'STATUS.tsv')).read() if os.path.exists(os.path.join(W, 'STATUS.tsv')) else ''
    return p.returncode, [l.split('\t')[0] + ':' + l.split('\t')[1] for l in s.splitlines()]


def chain_suite(text, tmp):
    f = []
    ok4 = 'outcomes_alarm\t0\t1\ta\noutcomesRND\t0\t1\tb\nmenu\t0\t1\tc\ncard\t0\t1\td\n'
    rc, s = chain_case(text, ok4, 0, tmp)
    if not (rc == 0 and s == ['outcomes_alarm:0', 'outcomesRND:0', 'menu:0', 'card:0', 'done:0']):
        f.append('C1 order and rc 0')
    rc, s = chain_case(text, 'outcomes_alarm\t0\t1\ta\noutcomesRND\t1\t1\tb\n', 0, tmp)
    if not (rc == 6 and s == ['outcomes_alarm:0', 'outcomesRND:1']):
        f.append('C1 an Outcomes failure exits 6')
    rc, s = chain_case(text, '', 1, tmp)
    if not (rc == 6 and s == ['d1:1']):
        f.append('C1 a driver crash')
    rc, s = chain_case(text, ok4.replace('card\t0', 'card\t2').replace('menu\t0', 'menu\t5'), 0, tmp)
    if not (rc == 2 and s[-1] == 'done:2'):
        f.append("C1 the card's rc")
    return f


def job_checks():
    f = []; g = open(os.path.join(K5, 'JOB_GRADE_V11.job.sh.txt')).read(); m = open(os.path.join(K5, 'JOB_MONTH_V11.job.sh.txt')).read()
    sha = lambda p: __import__('hashlib').sha256(open(p, 'rb').read()).hexdigest()[:16]
    if not ('ck $CH/alarm_grade_chain_v2_0_6_to20251231.sh %s;' % sha(GCH) in g and 'bash $CH/alarm_grade_chain_v2_0_6_to20251231.sh $V $D $W' in g):
        f.append('J1 GRADE chain pinned and called')
    if not ('$CH/d1_reports_v2.py perfire $F $T/perfire_v1_1_to20260430.py $W $V' in g and '$CH/d1_reports_v2.py handoff $F $T/lead_null_v1_1_to20251231.py' in g and '# CORES 3\n' in g):
        f.append('J1 GRADE perfire, hand-off, cores')
    if not ('ck $MP/alarm_grade_chain_v2_2_6_to20260430.sh %s;' % sha(MCH) in m and '$CH/d1_reports_v2.py perfire $F $T/perfire_v1_1_to20260430.py $W $V' in m):
        f.append('J1 MONTH chain and perfire')
    return f


def pin_checks(texts=None):
    """J2: the pins of both templates and both chains equal the files of this package; texts: {template name: text} (planted bugs)"""
    f = []; sha = lambda p: __import__('hashlib').sha256(open(p, 'rb').read()).hexdigest()[:16]
    for ch in (GCH, MCH):
        t = open(ch).read()
        for var, path in (('D1_SHA', REP), ('MEM_SHA', MEMPY)):
            m = re.search(r'\b%s=([0-9a-f]{16})\b' % var, t)
            if not m or m.group(1) != sha(path):
                f.append('J2 %s: %s %s, the file is %s' % (os.path.basename(ch), var, m.group(1) if m else 'none', sha(path)))
    sub_ = lambda s, env: re.sub(r'\$([A-Z][A-Z0-9_]*)', lambda mm: env.get(mm.group(1), '$' + mm.group(1)), s)
    for name in ('JOB_GRADE_V11.job.sh.txt', 'JOB_MONTH_V11.job.sh.txt'):
        t = (texts or {}).get(name) or open(os.path.join(K5, name)).read(); env = {'AL': PKG}; n = 0
        for m in re.finditer(r'(?:^|;|\s)([A-Z][A-Z0-9_]*)=(\$[A-Z][A-Z0-9_]*(?:/[^\s;]*)?)', t):
            env[m.group(1)] = sub_(m.group(2), env)
        for m in re.finditer(r'\bck (\$[A-Z][A-Z0-9_]*/[^\s;]+) ([0-9a-f]{16})\b', t):
            p = sub_(m.group(1), env)
            if '$' in p or not os.path.isfile(p):
                continue
            n += 1
            if sha(p) != m.group(2):
                f.append('J2 %s pins %s %s, the file is %s' % (name, os.path.relpath(p, PKG), m.group(2), sha(p)))
        if n == 0:
            f.append('J2 %s: no pin checked' % name)
    return f


def kill_suite(rep, tmp, limit=20):
    """K1: an Outcomes edition whose run kills its own process; the driver must end within limit seconds"""
    W = os.path.join(tmp, 'K%d' % N[0]); N[0] += 1; os.makedirs(W)
    for n in ('PB3_FIRES_V1_LIST.tsv', 'RND_PB3_V1_LIST.tsv'):
        open(os.path.join(W, n), 'w').write('coin\tt\tside\n')
    eo = os.path.join(tmp, 'eo_selfkill.py')
    open(eo, 'w').write('import os, signal\ndef _window_arg(d):\n    return None\ndef run(*a, **k):\n    open(a[8] + ".reached", "w").close()\n'
                        '    os.kill(os.getpid(), signal.SIGKILL)\n')   # a[8]: the run's root; the marker shows the kill came from run
    cmd = [sys.executable, '-B', rep, 'chain', KF, W, 'PB3', os.path.join(tmp, 'lab'), os.path.join(tmp, 's.json'), '20251015', '20251016',
           '20250901:20251016', 'FADE', '0', '', 'ALARM RND', eo, os.path.join(tmp, 'card_unused.py')]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True); t0 = time.time()
    try:
        out, err = p.communicate(timeout=limit)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL); p.communicate()
        return ['K1 a killed Outcomes worker ends the driver in seconds (still running after %d s)' % limit]
    f = []; sp = os.path.join(W, 'd1_PB3_steps.tsv')
    s = [l.split('\t')[:2] for l in open(sp).read().splitlines()] if os.path.exists(sp) else []
    if not (p.returncode == 0 and s == [['outcomes_alarm', '1'], ['outcomesRND', '1']]):
        f.append('K1 both runs rc 1, no menu or card (rc %s, steps %s)' % (p.returncode, s))
    if 'BrokenProcessPool' not in err:
        f.append('K1 the reason on stderr')
    if not any(os.path.exists(os.path.join(W, 'om_PB3%s_v1.reached' % x)) for x in ('', 'RND')):
        f.append('K1 a run reached its kill')
    print('K1 %.1f s' % (time.time() - t0))
    return f


def rplant(tmp, i, src):
    """a copy of d1_reports_v2.py with the Pool.map it had (and d1_mem_v2.py beside it)"""
    a = src.index("    t0 = time.time(); res = []\n    with cf.ProcessPoolExecutor(")
    b = src.index("res.append((1, int(time.time() - t0)))\n", a) + len("res.append((1, int(time.time() - t0)))\n")
    d = os.path.join(tmp, 'rp%d' % i); os.makedirs(d); shutil.copy(MEMPY, os.path.join(d, 'd1_mem_v2.py'))
    open(os.path.join(d, 'd1_reports_v2.py'), 'w').write(src[:a] + "    with mp.get_context('spawn').Pool(len(jobs)) as pool:\n"
                                                         "        res = pool.map(outcomes, [a for _, a in jobs])\n" + src[b:])
    return os.path.join(d, 'd1_reports_v2.py')


PLANTS = [("np.lexsort((np.array(acc['coin'], str), np.array(acc['as_of_us'], np.int64)))", "np.lexsort((np.array(acc['as_of_us'], np.int64), np.array(acc['coin'], str)))"),
          ("float(np.array([b], '<u8').view('<f8')[0])", "float(np.float32(np.array([b], '<u8').view('<f8')[0]))"),
          ("    if cap.part != part:\n", "    if False:\n"),
          ("        if int(d) not in cap.days or cap.days[int(d)][1] != coins:\n", "        if False:\n"),
          ("acc['reason'].append(er or '')", "acc['reason'].append(er or None)"),
          ("        if k in mem:\n", "        if False:\n")]
CPLANTS = [("  case $k in outcomes*) [ $r -eq 0 ] || exit 6;; card) rc2=$r;; esac", "  case $k in card) rc2=$r;; esac"),
           ("card) rc2=$r;;", "menu) rc2=$r;;"),
           ("[ $rd -eq 0 ] && [ -f $W/d1_${V}_steps.tsv ] || { st d1 $rd 0 $W/d1_${V}.log; exit 6; }", "true")]

if __name__ == '__main__':
    fails = []
    with tempfile.TemporaryDirectory() as t:
        cap, outs = planted_runs(t)
        fails += suite(MEMPY, cap, outs)
        for ch in (GCH, MCH):
            fails += [x + ' (%s)' % os.path.basename(ch) for x in chain_suite(block(ch), t)]
        fails += job_checks()
        fails += pin_checks()
        fails += kill_suite(REP, t)
        print('TESTS %s %s' % ('PASS' if not fails else 'FAIL', ' | '.join(fails)))
        src = open(MEMPY).read(); killed = 0; n = 0
        for i, (a, b) in enumerate(PLANTS, 1):
            n += 1
            if src.count(a) != 1:
                print('PLANT %d: found %d times' % (i, src.count(a))); continue
            p = os.path.join(t, 'mut%d.py' % i); open(p, 'w').write(src.replace(a, b))
            try:
                g = suite(p, cap, outs)
            except Exception as e:
                g = ['a crash (%s)' % type(e).__name__]
            killed += bool(g); print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'))
        btxt = block(GCH)
        for i, (a, b) in enumerate(CPLANTS, len(PLANTS) + 1):
            n += 1
            if btxt.count(a) != 1:
                print('PLANT %d: found %d times' % (i, btxt.count(a))); continue
            g = chain_suite(btxt.replace(a, b), t); killed += bool(g); print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'))
        gt = open(os.path.join(K5, 'JOB_GRADE_V11.job.sh.txt')).read(); good = 'ck $CH/d1_reports_v2.py %s;' % __import__('hashlib').sha256(open(REP, 'rb').read()).hexdigest()[:16]
        n += 1
        if gt.count(good) != 1:
            print('PLANT %d: found %d times' % (n, gt.count(good)))
        else:
            g = pin_checks({'JOB_GRADE_V11.job.sh.txt': gt.replace(good, 'ck $CH/d1_reports_v2.py f050decb59b65fa2;')})
            killed += bool(g); print('PLANT %d %s' % (n, ('killed by ' + g[0]) if g else 'ALIVE'))
        n += 1; g = kill_suite(rplant(t, 1, open(REP).read()), t)
        killed += bool(g); print('PLANT %d %s' % (n, ('killed by ' + g[0]) if g else 'ALIVE'))
        print('PLANTED BUGS %d of %d killed' % (killed, n))
    sys.exit(0 if not fails and killed == n else 1)
