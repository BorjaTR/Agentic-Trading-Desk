#!/usr/bin/env python3
"""test_run_all_tests_v2.py (CONDUCTOR's C41 test eb15af23d16dc738, landed by SCOUT in ALARM_V1_9 with a streaming check and planted
bugs; review team/SCOUT/reviews/REVIEW_C41_RUN_ALL_TESTS_V2_SCOUT.md 573249c88d46d849; TEST, NOT REVIEWED), planted data only, seconds:
a fake Alarm folder with 6 tests; --workers 1 and 3 give the same result lines in TESTS.tsv order and the same rc; 3 workers take less
wall time than 1; a bad --workers is refused; S1 the first result line arrives before the run ends (lines stream, as v1's did).
Then planted bugs in copies of run_all_tests_v2.py (--workers not used; rows paired with the wrong results; every line held to the
end): each must fail a check. Needs the Alarm folder for the 3 helper files it copies (settings_v1.py, run_isolated_v1.py, the hook).
  python3 -B <Alarm>/_tools/tests/test_run_all_tests_v2.py <Alarm>/_tools/run_all_tests_v2.py <Alarm>"""
import os, shutil, subprocess, sys, tempfile, time
V2, INST = sys.argv[1], sys.argv[2]
root = tempfile.mkdtemp(prefix='c41_'); AL = os.path.join(root, 'Alarm'); T = os.path.join(AL, '_tools')
os.makedirs(T); os.makedirs(os.path.join(AL, 'p1')); os.makedirs(os.path.join(root, 'forbidden'))
for f in ('settings_v1.py', 'run_isolated_v1.py'):
    shutil.copy(os.path.join(INST, '_tools', f), T)
shutil.copytree(os.path.join(INST, '_vendor', 'home_kit', 'isolation'), os.path.join(AL, '_vendor', 'home_kit', 'isolation'))
RUN = os.path.join(T, 'run_all_tests_v2.py')
BUSY = "import time,sys\nt=time.time()\nwhile time.time()-t<%s: pass\nprint('%s done')\nsys.exit(%d)\n"
tests = [('a', 1.0, 0, ''), ('b', 1.0, 0, ''), ('c', 1.0, 0, ''), ('d', 0.1, 1, ''), ('e', 0.1, 1, 'planted known'), ('f', 1.0, 0, '')]
rows = ['part\ttest\targs\tenv\tview\tnote\tknown']
for n, s, rc, kn in tests:
    open(os.path.join(AL, 'p1', 't_%s.py' % n), 'w').write(BUSY % (s, n, rc)); rows.append('p1\tt_%s.py\t\t\t\tplanted\t%s' % (n, kn))
open(os.path.join(T, 'TESTS.tsv'), 'w').write('\n'.join(rows) + '\n')
os.makedirs(os.path.join(AL, 'settings')); shutil.copy(os.path.join(INST, 'settings', 'SETTINGS_EXAMPLE.env'), os.path.join(AL, 'settings'))
keys = [l.split('=', 1)[0].strip() for l in open(os.path.join(INST, 'settings', 'SETTINGS_EXAMPLE.env')) if '=' in l and not l.lstrip().startswith('#')]
st = os.path.join(root, 'settings.env')
open(st, 'w').write(''.join('%s=%s\n' % (k, os.path.join(root, 'forbidden') if k == 'FORBID' else '') for k in keys))


def run(w):
    t0 = time.time(); p = subprocess.run([sys.executable, '-B', RUN, st, '--workers', str(w)], capture_output=True, text=True)
    lines = [l.split(None, 2)[0] + ' ' + l.split(None, 2)[2] for l in p.stdout.splitlines() if l[:4] in ('PASS', 'FAIL', 'KNOW')]
    return p.returncode, lines, time.time() - t0, p.stdout


def first_line_gap():
    """seconds between the first result line and the end of a --workers 1 run"""
    p = subprocess.Popen([sys.executable, '-B', RUN, st, '--workers', '1'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    assert p.stdout is not None   # stdout=PIPE (pyright: Popen.stdout is Optional)
    first = None
    for l in p.stdout:
        if first is None and l[:4] in ('PASS', 'FAIL', 'KNOW'):
            first = time.time()
    p.wait()
    return (time.time() - first) if first else 0.0


def suite(src):
    with open(RUN, 'w') as fh:
        fh.write(src)
    f = []

    def t(c, what):
        if not c:
            f.append(what)
    r1, l1, s1, o1 = run(1); r3, l3, s3, o3 = run(3)
    t(len(l1) == 6, 'workers 1: 6 result lines'); t(l1 == l3, 'workers 3: the same result lines in the same (TESTS.tsv) order')
    t(r1 == 3 and r3 == 3, 'both rc 3 (one real failure, d)')
    t([x.split()[0] for x in l1] == ['PASS', 'PASS', 'PASS', 'FAIL', 'KNOWN', 'PASS'], 'PASS, FAIL and KNOWN as planted')
    t(s3 < s1 - 1.0, 'workers 3 faster than 1 (%.1f s vs %.1f s)' % (s3, s1)); t('workers 3' in o3, 'the header names the workers')
    p = subprocess.run([sys.executable, '-B', RUN, st, '--workers', '0'], capture_output=True, text=True)
    t(p.returncode == 2 and 'WORKERS' in p.stdout, '--workers 0 refused (rc 2)')
    g = first_line_gap(); t(g > 1.0, 'S1 the first result line arrives before the run ends (%.1f s before)' % g)
    return f


MAP = "        got = ex.map(lambda kr: run_one(kr[1], forbid, out, vals, kr[0]), list(enumerate(R, 1)))\n"
PLANTS = [("ThreadPoolExecutor(max_workers=workers)", "ThreadPoolExecutor(max_workers=1)"),
          (MAP, MAP.replace("list(enumerate(R, 1)))", "list(enumerate(R, 1))[::-1])")),
          (MAP, MAP.replace("got = ex.map(", "got = list(ex.map(").replace("list(enumerate(R, 1)))", "list(enumerate(R, 1))))"))]

if __name__ == '__main__':
    src = open(V2).read()
    fails = suite(src)
    print('TESTS %s %s' % ('PASS' if not fails else 'FAIL', ' | '.join(fails)))
    killed = 0
    for i, (a, b) in enumerate(PLANTS, 1):
        if src.count(a) != 1:
            print('PLANT %d: found %d times' % (i, src.count(a))); continue
        g = suite(src.replace(a, b)); killed += bool(g); print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'))
    print('PLANTED BUGS %d of %d killed' % (killed, len(PLANTS)))
    sys.exit(0 if not fails and killed == len(PLANTS) else 1)
