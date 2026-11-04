#!/usr/bin/env python3
"""C53 planted tests for run_all_tests_v4.py (seconds; planted data only). Each SCOUT C49 MUST has a case that failed on v3.
Run: test_run_all_tests_v4.py <run_all_tests_v4.py> <hook dir with sitecustomize.py V1.1> <an Alarm install or the dev alarm_package>"""
import datetime, os, shutil, subprocess, sys, tempfile, time
V4, HOOK, INST = sys.argv[1:4]
NAME = os.path.basename(V4)
root = tempfile.mkdtemp(prefix='c53_')
FB, STORE = os.path.join(root, 'forbidden'), os.path.join(root, 'store')
os.makedirs(FB); os.makedirs(STORE)
keys = [l.split('=', 1)[0].strip() for l in open(os.path.join(INST, 'settings', 'SETTINGS_EXAMPLE.env')) if '=' in l and not l.lstrip().startswith('#')]
assert 'RESEARCH_STORE' in keys and 'FORBID' in keys, keys
st = os.path.join(root, 'settings.env')
open(st, 'w').write(''.join('%s=%s\n' % (k, FB if k == 'FORBID' else STORE if k == 'RESEARCH_STORE' else '') for k in keys))
open(os.path.join(STORE, 'x.txt'), 'w').write('store one\n')
W = "import time,sys,os\nt=time.time()\nwhile time.time()-t<%s: pass\n"
TESTS = ('part\ttest\targs\tenv\tview\tnote\tknown\n'
         'p1\tt_a.py\t\t\t\tp\t\n'                      # reads p1/d.txt
         'p1\tt_b.py\t\t\t\tp\t\n'                      # starts ls: NONPY
         'p1\tt_c.py\t\t\t\tp\t\n'                      # fails
         'p1\tt_k.py\t\t\t\tp\tplanted known\n'         # known failure
         'p1\tt_v.py\t@VIEW/x.txt\t\tx.txt=@RESEARCH_STORE/x.txt\tp\t\n'   # reads a view COPY of store data (M2)
         'p1\tt_m.py\t\t\t\tp\t\n'                      # tries p1/m.txt, absent (I2)
         'p1\tt_e.py\t\t\t\tp\t\n')                     # prints whether the hook logs (M7)


def cp(src, folder):
    """the bytes only, never the mode (SCOUT ALARM_V1_11_1, J20265396): a copy from a read-only install must stay writable"""
    shutil.copyfile(src, os.path.join(folder, os.path.basename(src)))


def make_alarm(name):
    AL = os.path.join(root, name); T = os.path.join(AL, '_tools'); P1 = os.path.join(AL, 'p1')
    os.makedirs(T); os.makedirs(P1); os.makedirs(os.path.join(AL, 'settings'))
    for f in ('settings_v1.py', 'run_isolated_v1.py'):
        cp(os.path.join(INST, '_tools', f), T)
    os.makedirs(os.path.join(AL, '_vendor', 'home_kit', 'isolation'))
    cp(os.path.join(HOOK, 'sitecustomize.py'), os.path.join(AL, '_vendor', 'home_kit', 'isolation'))
    cp(V4, T); cp(os.path.join(INST, 'settings', 'SETTINGS_EXAMPLE.env'), os.path.join(AL, 'settings'))
    open(os.path.join(P1, 'd.txt'), 'w').write('one\n')
    here = "os.path.dirname(os.path.abspath(__file__))"
    open(os.path.join(P1, 't_a.py'), 'w').write(W % 0.3 + "open(os.path.join(%s,'d.txt')).read()\nprint('a ok')\n" % here)
    open(os.path.join(P1, 't_b.py'), 'w').write(W % 0.1 + "import subprocess\nsubprocess.run(['ls'], stdout=subprocess.DEVNULL)\nprint('b ok')\n")
    open(os.path.join(P1, 't_c.py'), 'w').write(W % 0.1 + "sys.exit(1)\n")
    open(os.path.join(P1, 't_k.py'), 'w').write(W % 0.1 + "sys.exit(1)\n")
    open(os.path.join(P1, 't_v.py'), 'w').write("import sys\nprint('v ' + open(sys.argv[1]).read().strip())\n")
    open(os.path.join(P1, 't_m.py'), 'w').write("import os\ntry:\n    open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'m.txt')).read(); print('m present')\nexcept OSError:\n    print('m absent')\n")
    open(os.path.join(P1, 't_e.py'), 'w').write("import os\nprint('log ' + ('yes' if os.environ.get('CTXG_OPEN_LOG') else 'no'))\n")
    open(os.path.join(T, 'TESTS.tsv'), 'w').write(TESTS)
    return AL


A1 = make_alarm('Alarm1')


def run(AL, *extra):
    p = subprocess.run([sys.executable, '-B', os.path.join(AL, '_tools', NAME), st] + list(extra), capture_output=True, text=True)
    res = {}
    for l in p.stdout.splitlines():
        if l[:4] in ('PASS', 'FAIL', 'KNOW', 'SAME'):
            res[l.split()[2].split('/')[-1].rstrip(':')] = (l.split()[0], l)
    return p.returncode, {k: v[0] for k, v in res.items()}, p.stdout, {k: v[1] for k, v in res.items()}


ok = n = 0


def t(c, what):
    global ok, n
    n += 1; ok += bool(c); print(('PASS ' if c else 'FAIL ') + what)


cf = lambda i: os.path.join(root, 'c%d.tsv' % i)
rc, r, o, L = run(A1, '--workers', '2')
t(r == {'t_a.py': 'PASS', 't_b.py': 'PASS', 't_c.py': 'FAIL', 't_k.py': 'KNOWN', 't_v.py': 'PASS', 't_m.py': 'PASS', 't_e.py': 'PASS'} and rc == 3,
  'without a cache: every test runs (as v2)')
t('log no' in L.get('t_e.py', ''), 'M7: without --cache-out the hook does not log')
rc, r, o, L = run(A1, '--cache-out', cf(1), '--workers', '3')
t('log yes' in L.get('t_e.py', ''), 'M7: with --cache-out the hook logs')
rows = open(cf(1)).read().splitlines()
t(len(rows) == 1 + 4, 'cache-out keeps the clean PASS rows a, v, m, e (b NONPY, c FAIL, k KNOWN never cached): %d rows' % (len(rows) - 1))
t(all('"@ALARM/' in x or '"/' not in x.split('\t')[3].replace(STORE, '') for x in rows[1:]) and '/Alarm1/' not in ''.join(rows[1:]),
  'M1: files under the Alarm folder are kept as @ALARM/<rel>, never the absolute install path')
rc, r, o, L = run(A1, '--cache-in', cf(1), '--cache-out', cf(2))
t(r.get('t_a.py') == 'SAME' and r.get('t_v.py') == 'SAME' and r.get('t_m.py') == 'SAME' and r.get('t_b.py') == 'PASS' and r.get('t_c.py') == 'FAIL',
  'second run: a, v, m SAME; b runs (NONPY); c still FAIL')
t('in Alarm1' in L.get('t_a.py', ''), 'I6: a SAME line names where and when its PASS was')
t(len(open(cf(2)).read().splitlines()) == 1 + 4, 'SAME rows are carried into the next cache')
# M1: a new install whose test now fails must run, not be SAME on the old install's bytes
A2 = make_alarm('Alarm2')
open(os.path.join(A2, 'p1', 't_a.py'), 'a').write('sys.exit(1)\n')
rc, r, o, L = run(A2, '--cache-in', cf(2))
t(r.get('t_a.py') == 'FAIL' and r.get('t_v.py') == 'SAME' and rc == 3, 'M1: install B with A\'s cache: the changed test runs and FAILS; unchanged rows SAME')
# M2: the store data a view row copies changed
open(os.path.join(STORE, 'x.txt'), 'w').write('store two\n')
rc, r, o, L = run(A1, '--cache-in', cf(2))
t(r.get('t_v.py') == 'PASS' and 'store two' in L.get('t_v.py', ''), 'M2: view-copied data changed: the row runs')
open(os.path.join(STORE, 'x.txt'), 'w').write('store one\n')
# I2: a file absent at the PASS appears
open(os.path.join(A1, 'p1', 'm.txt'), 'w').write('now\n')
rc, r, o, L = run(A1, '--cache-in', cf(2))
t(r.get('t_m.py') == 'PASS' and 'm present' in L.get('t_m.py', ''), 'I2: a file absent at the PASS now exists: the row runs')
os.rename(os.path.join(A1, 'p1', 'm.txt'), os.path.join(root, 'm_aside.txt'))
# M4: the settings file changed: every row runs
rc, r, o, L = run(A1, '--cache-in', cf(2))
t(r.get('t_a.py') == 'SAME', 'control: unchanged settings, a SAME')
open(st, 'a').write('# changed\n')
rc, r, o, L = run(A1, '--cache-in', cf(2))
t(r.get('t_a.py') == 'PASS' and 'SAME' not in r.values(), 'M4: settings changed: no row is SAME')
# M4: the harness changed: the hook file (read before the hook starts, so never in a row's files)
rc, r, o, L = run(A1, '--cache-out', cf(3))
open(os.path.join(A1, '_vendor', 'home_kit', 'isolation', 'sitecustomize.py'), 'a').write('\n# harness edit\n')
rc, r, o, L = run(A1, '--cache-in', cf(3))
t('SAME' not in r.values(), 'M4: the hook (harness) changed: no row is SAME')
# file changes and refusals
rc, r, o, L = run(A1, '--cache-out', cf(4))
open(os.path.join(A1, 'p1', 'd.txt'), 'w').write('two\n'); rc, r, o, L = run(A1, '--cache-in', cf(4))
t(r.get('t_a.py') == 'PASS', 'a file it opened changed: a runs again')
open(os.path.join(A1, 'p1', 't_a.py'), 'a').write('# edited\n'); rc, r, o, L = run(A1, '--cache-in', cf(4))
t(r.get('t_a.py') == 'PASS', 'the test file itself changed: a runs again')
rc, r, o, L = run(A1, '--cache-out', cf(1)); t(rc == 2 and 'CACHE OUT EXISTS' in o, 'an existing cache-out is refused')
rc, r, o, L = run(A1, '--cache-out', os.path.join(A1, 'x.tsv')); t(rc == 2 and 'INSIDE THE ALARM' in o, 'a cache inside the Alarm folder is refused')
bad = os.path.join(root, 'bad.tsv'); open(bad, 'w').write(open(cf(4)).read().splitlines()[0] + '\nnot\ta cache\n')
rc, r, o, L = run(A1, '--cache-in', bad); t(rc == 2 and 'line 2 malformed' in o, 'I7: a malformed cache line is refused with its number')
old = os.path.join(root, 'old.tsv'); open(old, 'w').write('k\t3.10.12\t{}\n')
rc, r, o, L = run(A1, '--cache-in', old); t(rc == 2 and 'not a run_all_tests_v4 cache' in o, 'a v3 cache is refused')
# v4.1: a PASS older than --cache-max-days runs again
open(os.path.join(A1, 'p1', 'd.txt'), 'w').write('one\n')
rc, r, o, L = run(A1, '--cache-out', cf(5))
rows5 = open(cf(5)).read().splitlines()
aged = [rows5[0]] + ['\t'.join([x.split('\t')[0], (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10)).strftime('%Y-%m-%dT%H:%MZ')] + x.split('\t')[2:]) for x in rows5[1:]]
open(cf(6), 'w').write('\n'.join(aged) + '\n')
rc, r, o, L = run(A1, '--cache-in', cf(5)); t(r.get('t_a.py') == 'SAME', 'v4.1 control: a fresh cache row is SAME')
rc, r, o, L = run(A1, '--cache-in', cf(6)); t('SAME' not in r.values(), 'v4.1: rows 10 days old run again (limit 7)')
rc, r, o, L = run(A1, '--cache-in', cf(6), '--cache-max-days', '30'); t(r.get('t_a.py') == 'SAME', 'v4.1: --cache-max-days 30 carries them')
rc, r, o, L = run(A1, '--cache-in', cf(5), '--cache-max-days', '31'); t(rc == 2 and 'CACHE MAX DAYS' in o, 'v4.1: --cache-max-days above 30 refused')
# v4.2: a TESTS.tsv row whose script is missing is a FAIL line (rc 3), never a crash
open(os.path.join(A1, '_tools', 'TESTS.tsv'), 'a').write('p1\tt_missing.py\t\t\t\tp\t\n')
rc, r, o, L = run(A1, '--workers', '2')
t(rc == 3 and r.get('t_missing.py') == 'FAIL' and 'NO SUCH TEST' in o and 'Traceback' not in o, 'v4.2: a missing test script is a FAIL line, rc 3')
rc, r, o, L = run(A1, '--cache-in', cf(5)); t(rc == 3 and r.get('t_missing.py') == 'FAIL' and 'Traceback' not in o, 'v4.2: the same with a cache')
print('%d of %d PASS' % (ok, n)); sys.exit(0 if ok == n else 1)
