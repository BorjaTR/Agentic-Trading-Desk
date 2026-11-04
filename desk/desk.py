#!/usr/bin/env python3
"""desk.py: the one command of the Crypto Alarm Desk (local mode). Standard Python only; run it with any python3.

  python3 -B desk/desk.py setup  [--settings F]    make the output folders and the alarm package's settings file; check Python
  python3 -B desk/desk.py check  [--settings F]    the settings, the Python packages, the data root's schema check and the
                                                   engine's release check of GRADE and MONTH (desk/release_check_v1.py)
  python3 -B desk/desk.py env    [--settings F]    print PY=... and S=... (the two words every alarm tool takes)
  python3 -B desk/desk.py start  <RUN> [--dry]     start a run folder (alarm/.../start_run_v1.py)
  python3 -B desk/desk.py job    <RUN> <KIND> <IDEA> <ITEMS> [queue options] [--dry]
                                                   one job of any kind (COUNT, GRADE, TRUE, FIRSTLOOK, ENTRY, MONTH): the released
                                                   queue_job_v16.py makes it (same checks, claim, twin, RUNS row, seals), then this
                                                   command runs it here, now, in the foreground; one job at a time
  python3 -B desk/desk.py run    <alarm-relative script> [args]   any alarm tool with PYTHON; a bare argument S becomes --settings <file>
  python3 -B desk/desk.py tests  [--workers N] [--forbid DIR]...   every test of alarm/_tools/TESTS.tsv (each process watched: an open
                                                   under FORBID fails it; FORBID = OUTPUT_ROOT/forbid_canary plus each --forbid),
                                                   then the desk's own tests

Settings (one file, default settings/desk.env): DATA_ROOT, OUTPUT_ROOT, PYTHON. A relative path is relative to the repo folder (the
folder that holds desk/). PYTHON may be a bare name (python3): it is looked up on PATH. Nothing else is configured by hand: the alarm
package's own settings file (alarm/settings/SETTINGS_EXAMPLE.env keys) is generated into OUTPUT_ROOT/settings/SETTINGS_LOCAL.env.
Exit 0 done, 2 refused (nothing run), 3 a job or a test failed."""
import fcntl, os, re, shutil, subprocess, sys, time

DESK = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DESK)
ALARM = os.path.join(REPO, 'alarm')
KEYS = ('DATA_ROOT', 'OUTPUT_ROOT', 'PYTHON')
QUEUE = os.path.join(ALARM, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'queue_job_v16.py')
START = os.path.join(ALARM, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'start_run_v1.py')
LINE = re.compile(r'([A-Z][A-Z0-9_]*)=(.*)')
REGISTRY_COLS = ('alarm_id', 'kind', 'seat', 'run', 'idea', 'V', 'state', 'lean', 'side', 'parent', 'one_line', 'novelty_verdict',
                 'novelty_basis', 'nearest_before', 'nearest_same_fires_pct', 'nearest_same_side_pct', 'nearest_waves_near_pct',
                 'nearest_baseline_pct', 'r1', 'r2', 'lead_15m', 't_15m', 'lead_1h', 't_1h', 'waves', 'months_counted', 'months_passing',
                 'clear', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'forward_months', 'decided_utc', 'claimed_utc',
                 'claimed_src', 'minutes_claim_to_decision', 'variants_tried_for_idea', 'def_rel', 'def_sha16', 'idea_card', 'alarm_card',
                 'prereg', 'findings', 'grade_job', 'entry_job', 'month_job', 'fire_list_rel', 'fire_list_sha16', 'fires', 'fire_list_check',
                 'decision_source', 'do_not', 'page')   # the header of the released registry (registry_build_v2), no rows


class Refused(Exception):
    pass


def read_settings(path):
    if not os.path.isfile(path):
        raise Refused('NO SETTINGS FILE %s (copy settings/desk.env.example to settings/desk.env)' % path)
    got = {}
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\r\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        m = LINE.fullmatch(line)
        if not m or m.group(1) not in KEYS or m.group(1) in got:
            raise Refused('BAD LINE %s line %d (keys %s, each once, KEY=VALUE)' % (path, n, ', '.join(KEYS)))
        got[m.group(1)] = m.group(2).strip()
    miss = [k for k in KEYS if not got.get(k)]
    if miss:
        raise Refused('KEYS MISSING %s in %s' % (', '.join(miss), path))
    out = {}
    for k in ('DATA_ROOT', 'OUTPUT_ROOT'):
        v = got[k]
        out[k] = os.path.normpath(v if os.path.isabs(v) else os.path.join(REPO, v))
        if out[k] == ALARM or out[k].startswith(ALARM + os.sep):
            raise Refused('%s=%s is inside alarm/: data and outputs live outside the package' % (k, out[k]))
    rd, ro = os.path.realpath(out['DATA_ROOT']), os.path.realpath(out['OUTPUT_ROOT'])     # symlink aliases resolved
    if rd == ro or ro.startswith(rd + os.sep) or rd.startswith(ro + os.sep):
        raise Refused('DATA_ROOT %s and OUTPUT_ROOT %s overlap (resolved %s and %s): outputs never go inside the data, nor the data '
                      'inside the outputs' % (out['DATA_ROOT'], out['OUTPUT_ROOT'], rd, ro))
    py = got['PYTHON']
    out['PYTHON'] = py if os.path.isabs(py) else (shutil.which(py) or '')
    if not out['PYTHON'] or not os.path.isfile(out['PYTHON']):
        raise Refused('PYTHON %r not found' % py)
    if not re.fullmatch(r'[A-Za-z0-9_./-]+', out['PYTHON'] + out['DATA_ROOT'] + out['OUTPUT_ROOT']):
        raise Refused('a path holds a space or another sign the job lines refuse: letters, digits and _ . / - only')
    return out


def paths(s):
    o = s['OUTPUT_ROOT']
    return {'alarm_settings': os.path.join(o, 'settings', 'SETTINGS_LOCAL.env'), 'runner': os.path.join(o, 'local_runner'),
            'alloc': os.path.join(o, 'local_runner', 'ALLOC.tsv'), 'logs': os.path.join(o, 'local_runner', 'LOGS'),
            'research': os.path.join(o, 'research'), 'scratch': os.path.join(o, 'scratch'), 'runlog': os.path.join(o, 'runlog'),
            'forbid': os.path.join(o, 'forbid_canary'), 'lab_days': os.path.join(s['DATA_ROOT'], 'lab_days'), 'research_days': os.path.join(s['DATA_ROOT'], 'research_days')}


def alarm_settings_text(s, p):
    rows = [('PYTHON', s['PYTHON']), ('LAB_DAYS', p['lab_days']), ('RESEARCH_STORE', p['research_days']), ('HL_FILLS', ''),
            ('SCRATCH', p['scratch']), ('RESEARCH_ROOT', p['research']), ('BOARD', p['runlog']), ('RUNNER_QUEUES', p['runner']),
            ('RUNNER_ALLOC', os.path.join(DESK, 'local_alloc.py')), ('RUNNER_RELEASE', ''), ('FEED_GATE', ''), ('FORBID', p['forbid'])]
    return ('# generated by desk/desk.py setup from %s: do not edit; edit the desk settings and run setup again\n' % s['_file']
            + ''.join('%s=%s\n' % kv for kv in rows))


def setup(s, quiet=False):
    p = paths(s)
    for d in (p['runner'] + '/Q_V1/IN', p['runner'] + '/Q_V1/RUN', p['runner'] + '/Q_V1/DONE', p['logs'],
              p['research'] + '/ALARM_DESIGN/runs/IDEAS_CLAIMED', p['research'] + '/ALARM_DESIGN/REGISTRY', p['scratch'], p['runlog'],
              p['forbid'], os.path.dirname(p['alarm_settings'])):
        os.makedirs(d, exist_ok=True)          # outputs only: the data folders (DATA_ROOT) are read, never created or written
    reg = os.path.join(p['research'], 'ALARM_DESIGN', 'REGISTRY', 'ALARM_REGISTRY_V1.tsv')
    if not os.path.isfile(reg):                # the desk's own registry starts empty (the lab's rows are not shipped)
        with open(reg, 'x') as f:
            f.write('# ALARM_REGISTRY of this desk: empty at setup; copy and novelty checks compare with this desk\'s own alarms only.\n'
                    + '\t'.join(REGISTRY_COLS) + '\n')
    text = alarm_settings_text(s, p)
    if not os.path.isfile(p['alarm_settings']) or open(p['alarm_settings']).read() != text:
        with open(p['alarm_settings'] + '.tmp', 'w') as f:
            f.write(text)
        os.replace(p['alarm_settings'] + '.tmp', p['alarm_settings'])
    if not quiet:
        print('SETUP OK output %s; alarm settings %s' % (s['OUTPUT_ROOT'], p['alarm_settings']))
        for k in ('lab_days', 'research_days'):
            if not os.path.isdir(p[k]):
                print('NOTE: %s %s is absent (setup never creates data folders; tools that read it refuse by themselves)' % (k, p[k]))
    return p


def ready(s):
    """every command but setup: the alarm settings that setup wrote must exist and still match the desk settings; nothing is written"""
    p = paths(s)
    if not os.path.isfile(p['alarm_settings']):
        raise Refused('NOT SET UP: no %s (run desk.py setup first)' % p['alarm_settings'])
    if open(p['alarm_settings']).read() != alarm_settings_text(s, p):
        raise Refused('SETTINGS CHANGED since setup: %s no longer matches %s (run desk.py setup again)' % (p['alarm_settings'], s['_file']))
    return p


def env_for(s, p):
    e = dict(os.environ)
    e['DESK_ALLOC_STATE'] = p['alloc']
    e['PYTHONDONTWRITEBYTECODE'] = '1'
    e['DESK_LAB_DAYS'], e['DESK_PYTHON'], e['DESK_ALARM_SETTINGS'] = p['lab_days'], s['PYTHON'], p['alarm_settings']   # desk/tests read them
    return e


def run_alarm_tool(s, p, script, args):
    full = os.path.join(ALARM, script)
    if not os.path.isfile(full):
        raise Refused('NO SUCH TOOL alarm/%s' % script)
    a = []
    for x in args:
        a += ['--settings', p['alarm_settings']] if x == 'S' else [x]
    return subprocess.run([s['PYTHON'], '-B', full] + a, cwd=ALARM, env=env_for(s, p)).returncode


def job(s, p, argv):
    """queue_job_v16.py unchanged into the local spool, then the job file it wrote runs here (bash), one at a time"""
    dry = '--dry' in argv
    lockp = os.path.join(p['runner'], '.one_job_at_a_time')
    lock = open(lockp, 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        raise Refused('ANOTHER JOB IS RUNNING (local mode runs one job at a time): wait for it')
    try:
        inq = os.path.join(p['runner'], 'Q_V1', 'IN')
        before = set(os.listdir(inq))
        r = subprocess.run([s['PYTHON'], '-B', QUEUE, '--settings', p['alarm_settings']] + argv, cwd=ALARM, env=env_for(s, p))
        if r.returncode != 0 or dry:
            return r.returncode
        new = sorted(f for f in set(os.listdir(inq)) - before if f.endswith('.job.sh'))
        if len(new) != 1:
            raise Refused('the queue wrote %d job files, 1 expected: %s' % (len(new), new))
        name = new[0]
        runf = os.path.join(p['runner'], 'Q_V1', 'RUN', name)
        os.rename(os.path.join(inq, name), runf)
        logf = os.path.join(p['logs'], name + '.log')
        print('LOCAL RUN %s (log %s)' % (name, logf), flush=True)
        t0 = time.time()
        with open(logf, 'x') as lf:
            rc = subprocess.run(['nice', '-n', '10', 'bash', runf], cwd=ALARM, env=env_for(s, p), stdout=lf, stderr=subprocess.STDOUT,
                                stdin=subprocess.DEVNULL).returncode
        os.rename(runf, os.path.join(p['runner'], 'Q_V1', 'DONE', name))
        print('LOCAL END %s rc %d in %.0f s' % (name, rc, time.time() - t0))
        num, kind, idea = name.split('_')[0], name.split('_')[-2], name.split('_')[-1].split('.')[0]
        run = argv[0]
        st = os.path.join(p['research'], 'ALARM_DESIGN', 'runs', run, 'receipts', '%s_%s_%s' % (num, kind, idea), 'STAGES.tsv')
        if os.path.isfile(st):
            print('STAGES %s' % st)
            sys.stdout.write(open(st).read())
        return 0 if rc == 0 else 3
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()


def tests(s, p, argv):
    w = argv[argv.index('--workers') + 1] if '--workers' in argv else '2'
    fb = []
    for i, x in enumerate(argv):
        if x == '--forbid':
            fb += ['--forbid', argv[i + 1]]
    out = os.path.join(s['OUTPUT_ROOT'], 'tests', time.strftime('%Y%m%dT%H%M%S'))
    r1 = subprocess.run([s['PYTHON'], '-B', os.path.join(ALARM, '_tools', 'run_all_tests_v4.py'), p['alarm_settings'], '--workers', w,
                         '--out', out] + fb, cwd=ALARM, env=env_for(s, p)).returncode
    r2 = subprocess.run([s['PYTHON'], '-B', '-m', 'pytest', '-q', '-rxX', '-p', 'no:cacheprovider', os.path.join(DESK, 'tests')],
                        cwd=REPO, env=env_for(s, p)).returncode
    print('TESTS alarm rc %d, desk rc %d' % (r1, r2))
    return 0 if r1 == 0 and r2 == 0 else 3


def main(argv):
    a = list(argv)
    sf = os.path.join(REPO, 'settings', 'desk.env')
    if '--settings' in a:
        i = a.index('--settings'); sf = a[i + 1]; del a[i:i + 2]
    if not a:
        print(__doc__); return 2
    s = read_settings(sf); s['_file'] = os.path.abspath(sf)
    cmd, rest = a[0], a[1:]
    if cmd == 'setup':
        setup(s); return 0
    p = ready(s)
    if cmd == 'env':
        print('PY=%s' % s['PYTHON']); print('S=--settings %s' % p['alarm_settings']); return 0
    if cmd == 'check':
        r = subprocess.run([s['PYTHON'], '-B', os.path.join(ALARM, '_tools', 'settings_v1.py'), 'check', p['alarm_settings']]).returncode
        r2 = subprocess.run(['bash', os.path.join(ALARM, '_tools', 'setup_python_v1.sh'), '--check', '--python', s['PYTHON']]).returncode
        sc = os.path.join(DESK, 'data', 'schema_check.py')
        if os.path.isfile(sc):
            r3 = subprocess.run([s['PYTHON'], '-B', sc, p['lab_days']]).returncode
        else:
            print('DATA CHECK NOT BUILT (V2 ships no converter and no schema check: docs/CONVERT_YOUR_DATA_V2.md step 5 holds the checks): lab_days %s %s'
                  % (p['lab_days'], ('holds %d entries' % len(os.listdir(p['lab_days']))) if os.path.isdir(p['lab_days']) else 'is ABSENT'))
            r3 = 0
        r4 = subprocess.run([s['PYTHON'], '-B', os.path.join(DESK, 'release_check_v1.py')]).returncode   # a desk that cannot GRADE says so here
        print('CHECK settings rc %d (3 = some keys EMPTY, expected for HL_FILLS, RUNNER_RELEASE, FEED_GATE, FORBID), python rc %d, '
              'data rc %d, release rc %d' % (r, r2, r3, r4))
        return 0 if r2 == 0 and r3 == 0 and r4 == 0 else 3
    if cmd == 'start':
        return run_alarm_tool(s, p, os.path.relpath(START, ALARM), ['S'] + rest)
    if cmd == 'job':
        return job(s, p, rest)
    if cmd == 'run':
        if not rest:
            raise Refused('run <alarm-relative script> [args]')
        return run_alarm_tool(s, p, rest[0], rest[1:])
    if cmd == 'tests':
        return tests(s, p, rest)
    print(__doc__); return 2


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr); sys.exit(2)
