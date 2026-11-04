#!/usr/bin/env python3
"""run_all_tests_v2.py = run_all_tests_v1.py eddfa06bdbaff7cd + --workers N (CONDUCTOR 31 Oct 2026, C41; SCOUT 13:12:29Z: 96 tests one
at a time, 1885 s of a 1895 s install job; rule book 0.20 (3): tests 3 at a time). N tests run at once, each in its own new temporary
folder as before; the result lines and ALL_TESTS.tsv keep TESTS.tsv order; --workers 1 (the default) runs as v1. Landed in ALARM_V1_9 by
SCOUT with review item 1 (team/SCOUT/reviews/REVIEW_C41_RUN_ALL_TESTS_V2_SCOUT.md 573249c88d46d849): each result line is printed as
soon as its test and every test before it are done (v1 printed each line as its test ended). v1's text follows.
run_all_tests_v1.py (SCOUT 30 Oct 2026; the owner, the owner, 13:07 Berlin: "TEST THAT BOTH WORK CORRECTLY"; 10:46: "if now I clone
the repository in another machine. That machine should be able to execute everything as well with a settings file").
Runs every test listed in _tools/TESTS.tsv from this Alarm folder, each through _tools/run_isolated_v1.py, with the forbidden folders
of the settings file (FORBID) and the home kit's start-up hook in every Python process (so a worker process that opens a forbidden file
is caught too). No data is needed: the tests plant their own.
  python3 -B _tools/run_all_tests_v2.py <settings file> [--workers N] [--copy] [--part <part>]... [--forbid <dir>]... [--out <new folder outside Alarm>]
--copy first copies this whole Alarm folder into a new temporary folder and runs the copy's own tests there, with this Alarm folder
forbidden too (proof that nothing depends on where the folder sits); the copy is removed at the end. Each test gets its own new
temporary folder (TMPDIR, its working folder), removed after the test: tests never write into the Alarm folder.
A test passes when it exits 0, run_isolated_v1 prints ISOLATION OK, and the start-up hook logged no forbidden open. A row whose
"known" column (7th, optional) names a reason is a KNOWN failure when it fails: it is printed as KNOWN with that reason and does not
fail the run (for a released file that cannot be changed here, e.g. one with the Mac's dev tree built into its import path).
TESTS.tsv columns: part, test (path in the part), args, env (KEY=VALUE ...; both split like a shell line, so quotes work), view,
note. In args and env: @LAB3 = _vendor/LAB3_code, @ALARM = this Alarm folder, @PART = the part folder, @WORK = the test's own new
temporary folder, @VIEW = a temporary folder built from the view column ("path=target;..."): a link to target (relative to @ALARM),
or, when target starts with @<SETTINGS KEY>, a COPY of that data file (a test that reads a small table of the team's data; a copy,
because a link would resolve into the forbidden dev tree). For a tool that reads the dev tree's layout from one root.
Exit 0 all passed, 3 a test failed, 2 refused (nothing run)."""
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

TOOLS = os.path.dirname(os.path.abspath(__file__))
ALARM = os.path.realpath(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
import settings_v1  # noqa: E402

HOOK = os.path.join(ALARM, '_vendor', 'home_kit', 'isolation')
TIME_LIMIT_S = 1800


class Refused(Exception):
    pass


def rows(path):
    out = []
    with open(path) as f:
        head = None
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln.strip() or ln.startswith('#'):
                continue
            c = ln.split('\t')
            if head is None:
                head = c
                if head[:6] != ['part', 'test', 'args', 'env', 'view', 'note']:
                    raise Refused('TESTS.tsv HEADER %s' % head)
                continue
            r = dict(zip(head, c + [''] * (len(head) - len(c))))
            r.setdefault('known', '')
            out.append(r)
    return out


def subst(s, part, view, work):
    return (s.replace('@LAB3', os.path.join(ALARM, '_vendor', 'LAB3_code')).replace('@ALARM', ALARM)
            .replace('@PART', os.path.join(ALARM, part)).replace('@VIEW', view or '@VIEW').replace('@WORK', work))


def build_view(spec, root, vals):
    for pair in [p for p in spec.split(';') if p.strip()]:
        link, target = [x.strip() for x in pair.split('=', 1)]
        lp = os.path.join(root, link)
        os.makedirs(os.path.dirname(lp), exist_ok=True)
        if target.startswith('@'):
            key, rest = (target[1:].split('/', 1) + [''])[:2]
            if not vals.get(key):
                raise Refused('VIEW NEEDS SETTINGS KEY %s (empty or missing)' % key)
            src = os.path.join(vals[key], rest)
            if not os.path.isfile(src):
                raise Refused('VIEW DATA FILE MISSING %s' % src)
            shutil.copyfile(src, lp)
        else:
            tp = os.path.join(ALARM, target)
            if not os.path.exists(tp):
                raise Refused('VIEW TARGET MISSING %s' % tp)
            os.symlink(tp, lp)


def run_one(r, forbid, out, vals, k=0):
    part, test = r['part'], r['test']
    script = os.path.join(ALARM, part, test)
    if not os.path.isfile(script):
        return 'FAIL', 0.0, 'NO SUCH TEST %s' % script, ''
    work = tempfile.mkdtemp(prefix='alarm_test_')
    try:
        view = os.path.join(work, 'view') if r['view'].strip() else None
        if view:
            os.makedirs(view)
            build_view(r['view'], view, vals)
        tmp = os.path.join(work, 'tmp'); os.makedirs(tmp)
        log = os.path.join(work, 'hook.log')
        env = dict(os.environ)
        env.update({'TMPDIR': tmp, 'CTXG_ISOLATE': '1', 'CTXG_FORBID': ':'.join(forbid),
                    'CTXG_ALLOW': ':'.join([ALARM, os.path.realpath(work)]), 'CTXG_ISOLATION_LOG': log,
                    'PYTHONPATH': HOOK + ((os.pathsep + env['PYTHONPATH']) if env.get('PYTHONPATH') else '')})
        for kv in shlex.split(subst(r['env'], part, view, work)):
            ek, ev = kv.split('=', 1); env[ek] = ev
        cmd = [sys.executable, '-B', '-W', 'ignore', os.path.join(TOOLS, 'run_isolated_v1.py')]
        for f in forbid:
            cmd += ['--forbid', f]
        cmd += [script] + shlex.split(subst(r['args'], part, view, work))
        t0 = time.time()
        try:
            p = subprocess.run(cmd, cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                               text=True, timeout=TIME_LIMIT_S)
            text, rc = p.stdout, p.returncode
        except subprocess.TimeoutExpired as e:
            text, rc = (e.stdout or '') if isinstance(e.stdout, str) else '', 124
        secs = time.time() - t0
        hook = open(log).read() if os.path.exists(log) else ''
        iso = [l for l in text.splitlines() if l.startswith('ISOLATION ')]
        ok = rc == 0 and iso and iso[-1].startswith('ISOLATION OK') and not hook.strip()
        lines = [l for l in text.splitlines() if l.strip() and not l.startswith('ISOLATION ')]
        why = '' if ok else ('exit %d' % rc if rc else ('hook saw: %s' % hook.strip().splitlines()[0][:150] if hook.strip() else 'no ISOLATION OK'))
        if out:
            name = '%02d_%s__%s.log' % (k, part, test.replace('/', '__'))   # numbered: one script may serve several rows
            with open(os.path.join(out, name), 'x') as f:
                f.write('$ %s\n(cwd %s)\n%s\n--- hook log ---\n%s' % (' '.join(cmd), work, text, hook))
        return ('PASS' if ok else 'FAIL'), secs, (lines[-1][:160] if lines else '') + ('' if ok else '  [%s]' % why), (iso[-1] if iso else '')
    finally:
        for d, _, _ in os.walk(work):
            try:
                os.chmod(d, os.stat(d).st_mode | 0o700)      # a test may leave a folder without write permission
            except OSError:
                pass
        shutil.rmtree(work, ignore_errors=True)


def from_copy(settings, rest):
    """copy this Alarm folder into a new temporary folder, run the copy's own run_all_tests_v1.py with this folder forbidden"""
    base = tempfile.mkdtemp(prefix='alarm_copy_')
    try:
        dst = os.path.join(base, 'Alarm')
        shutil.copytree(ALARM, dst, symlinks=True, ignore=shutil.ignore_patterns('__pycache__', '.DS_Store'))
        for d, _, _ in os.walk(dst):
            os.chmod(d, os.stat(d).st_mode | 0o200)          # a copy of a read-only release must be removable
        s = os.path.realpath(settings)
        if s.startswith(ALARM + os.sep):
            s = os.path.join(dst, os.path.relpath(s, ALARM))       # the copy's own settings file
        print('COPY %s -> %s' % (ALARM, dst), flush=True)
        return subprocess.call([sys.executable, '-B', os.path.join(dst, '_tools', 'run_all_tests_v2.py'), s] + rest + ['--forbid', ALARM],
                               stdin=subprocess.DEVNULL)
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main(a):
    if not a:
        print(__doc__); return 2
    settings, a = a[0], a[1:]
    if '--copy' in a:
        return from_copy(settings, [x for x in a if x != '--copy'])
    parts, extra, out, workers = [], [], None, 1
    while a:
        if a[0] == '--workers' and len(a) > 1:
            if not a[1].isdigit() or not 1 <= int(a[1]) <= 8:
                raise Refused('WORKERS %s (1 to 8)' % a[1])
            workers = int(a[1]); a = a[2:]; continue
        if a[0] == '--part' and len(a) > 1:
            parts.append(a[1]); a = a[2:]
        elif a[0] == '--forbid' and len(a) > 1:
            extra.append(os.path.realpath(a[1])); a = a[2:]
        elif a[0] == '--out' and len(a) > 1:
            out = os.path.realpath(a[1]); a = a[2:]
        else:
            raise Refused('ARGUMENT %s' % a[0])
    vals = settings_v1.load(settings)
    forbid = [os.path.realpath(p) for p in (vals.get('FORBID') or '').split(':') if p] + extra
    forbid = [f for f in forbid if not (ALARM == f or ALARM.startswith(f + os.sep))]
    if not forbid:
        raise Refused('NO FORBIDDEN FOLDER: set FORBID in %s (the dev tree) or give --forbid' % settings)
    if out:
        if out == ALARM or out.startswith(ALARM + os.sep):
            raise Refused('OUT INSIDE THE ALARM FOLDER %s' % out)
        if os.path.exists(out):
            raise Refused('OUT EXISTS %s' % out)
    if not os.path.isfile(os.path.join(HOOK, 'sitecustomize.py')):
        raise Refused('NO START-UP HOOK %s' % HOOK)
    R = [r for r in rows(os.path.join(TOOLS, 'TESTS.tsv')) if not parts or r['part'] in parts]
    if not R:
        raise Refused('NO TESTS for %s' % (parts or 'any part'))
    if out:
        os.makedirs(out)
    print('ALARM %s; python %s; forbidden %s; %d tests; workers %d' % (ALARM, sys.executable, forbid, len(R), workers), flush=True)
    res = []
    with ThreadPoolExecutor(max_workers=workers) as ex:      # each run_one is a subprocess; map yields in TESTS.tsv order
        got = ex.map(lambda kr: run_one(kr[1], forbid, out, vals, kr[0]), list(enumerate(R, 1)))
        for r, (st, secs, last, iso) in zip(R, got):          # a line as soon as it and every line before it are done
            if st == 'FAIL' and r['known'].strip():
                st, last = 'KNOWN', '%s  (known: %s)' % (last, r['known'].strip())
            res.append((r['part'], r['test'], st, secs, last, iso))
            print('%s %6.1fs %s/%s: %s' % (st, secs, r['part'], r['test'], last), flush=True)
    n_ok = sum(1 for x in res if x[2] == 'PASS'); n_known = sum(1 for x in res if x[2] == 'KNOWN')
    if out:
        with open(os.path.join(out, 'ALL_TESTS.tsv'), 'x') as f:
            f.write('part\ttest\tresult\tseconds\tlast_line\tisolation\n')
            for x in res:
                f.write('%s\t%s\t%s\t%.1f\t%s\t%s\n' % (x[0], x[1], x[2], x[3], x[4].replace('\t', ' '), x[5].replace('\t', ' ')))
    print('ALL TESTS: %d of %d passed%s' % (n_ok, len(res), ', %d known failures (KNOWN lines above)' % n_known if n_known else ''))
    return 0 if n_ok + n_known == len(res) else 3


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except (Refused, settings_v1.Refused) as e:
        print('REFUSED %s' % e)
        sys.exit(2)
