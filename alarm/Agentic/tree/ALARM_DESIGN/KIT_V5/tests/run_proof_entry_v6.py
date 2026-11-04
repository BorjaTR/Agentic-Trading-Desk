#!/usr/bin/env python3
"""run_proof_entry_v6.py (SCOUT, K6, 31 Oct 2026; TEST, NOT REVIEWED): the RUN proof of JOB_ENTRY_V6 on real data, from an Alarm folder,
with a machine's settings file (CLEAN_RELEASE_V1 section 1). New edition by SCOUT for the clean release (the owner 30 Oct 2026 23:07
Berlin: "All alarm tools should work from the release folder only"). Run it under _tools/run_isolated_v2.py --settings <file>, which
watches this process; it then
  1 fills the ENTRY job with this folder's queue_job_v5.py, loaded in memory with the template's sha16 put into its TEMPLATE_SHA (the
    one change; the queue does not queue ENTRY yet), --dry: nothing claimed, written or queued;
  2 checks the filled job: every absolute path lies in this Alarm folder or under the settings keys (PYTHON, LAB_DAYS, SCRATCH,
    RESEARCH_ROOT, FEED_GATE) or is /dev/null (a path and its realpath both compared: on the Mac /tmp is a link to /private/tmp);
  3 runs the job with bash as it is (with --fake-free-mb N, its one read of the scratch disk's free space answers N MB: a small
    machine is under the job's 60 GB floor), every Python process it starts watched by the home kit's start-up hook
    (_vendor/home_kit/isolation): every file opened under FORBID, under --forbid-more folders or in an archive/ folder of this Alarm
    folder is logged, then judged by this folder's _tools/run_isolated_v2.py rule: a data file under a settings data key passes (the
    feed's gate FEED_GATE counts as data), code (.py, .sh, ...) or anything else fails, and every past edition (archive/) fails;
  4 reads the job's receipts: every stage rc 0 and the end line; and the grader's own record (RUN.json of the store run): every file
    it executed (code_sha16) and its pins file lie in this Alarm folder.
The job writes only where it always writes: SCRATCH/work_<RUN>/0_ENTRY_<IDEA>, the store's places under SCRATCH and the receipts under
RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>/receipts/0_ENTRY_<IDEA> (give a sandbox RESEARCH_ROOT: the job is a real one). Nothing is
written inside the Alarm folder (it may be a read-only install).
  python3 -B _tools/run_isolated_v2.py --settings S Agentic/tree/ALARM_DESIGN/KIT_V5/tests/run_proof_entry_v6.py --settings S
      --run RUN --idea IDEA --variant V --from-job GRADE_JOB [--fake-free-mb N] [--forbid-more DIR[:DIR...]]"""
import contextlib, hashlib, importlib.util, io, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
KIT5 = os.path.dirname(HERE)
ALARM = os.path.realpath(os.path.join(KIT5, '..', '..', '..', '..'))
ABS = re.compile(r'(?<![\w.$@)\]/*-])/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*[A-Za-z0-9_-]')


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def under(p, roots):
    return any(p == r or p.startswith(r.rstrip(os.sep) + os.sep) for r in roots)


def both(p):
    """a path and its realpath (on the Mac /tmp is a link to /private/tmp: compare both, never one form against the other)"""
    return {os.path.normpath(p), os.path.realpath(p)}


def args(a):
    o = {'--settings': None, '--run': None, '--idea': None, '--variant': None, '--from-job': None, '--fake-free-mb': None, '--forbid-more': ''}
    while a:
        k = a.pop(0)
        if k not in o or not a:
            raise SystemExit('USAGE: see the docstring of %s' % __file__)
        o[k] = a.pop(0)
    if not all(o[k] for k in ('--settings', '--run', '--idea', '--variant', '--from-job')):
        raise SystemExit('give --settings --run --idea --variant --from-job')
    return o


def main(a):
    o = args(list(a))
    S = load(os.path.join(ALARM, '_tools', 'settings_v1.py'), 'settings_v1_proof'); RI = load(os.path.join(ALARM, '_tools', 'run_isolated_v2.py'), 'run_isolated_v2_proof')
    s = S.load(o['--settings'])
    if s.get('RUNNER_RELEASE') and os.path.realpath(s['RUNNER_RELEASE']) != ALARM:
        print('REFUSED: RUNNER_RELEASE=%s names another Alarm folder: the job would run its code, not this folder\'s' % s['RUNNER_RELEASE']); return 2
    tpl = os.path.join(KIT5, 'jobs', 'JOB_ENTRY_V6.job.sh.txt')
    Q = load(os.path.join(KIT5, 'tools', 'queue_job_v5.py'), 'queue_job_v5_proof')
    Q.TEMPLATE_SHA['ENTRY'] = sha16(tpl)                                       # 1 the one change to the queue
    if o['--fake-free-mb']:
        Q.CFG['free_mb'] = lambda: int(o['--fake-free-mb'])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = Q.main(['--settings', o['--settings'], o['--run'], 'ENTRY', o['--idea'], o['--variant'], '--from-job', o['--from-job'], '--dry'])
    out = buf.getvalue()
    if rc != 0 or '\nDRY RUN OK' not in out:
        print('FILL FAILED rc %s: %s' % (rc, out[-500:])); return 1
    job = out.split('\nDRY RUN OK')[0] + '\n'
    keys = ('LAB_DAYS', 'SCRATCH', 'RESEARCH_ROOT', 'FEED_GATE')
    roots = set().union(*[both(ALARM)] + [both(s[k]) for k in keys if s.get(k)])
    stray = sorted({p for p in ABS.findall(job) if p != '/dev/null' and not both(p) & both(s['PYTHON']) and not any(under(q, roots) for q in both(p))})
    print('2 FILLED JOB: template %s; %d absolute paths, outside the Alarm folder and the settings keys: %s' % (sha16(tpl), len(set(ABS.findall(job))), stray or 'none'))
    if stray:
        return 1
    if o['--fake-free-mb']:
        df = 'df -m %s |' % s['SCRATCH']
        assert job.count(df) == 1, 'the job reads the free space of SCRATCH, once'
        job = job.replace(df, "printf 'Filesystem\\nx x x %d\\n' |" % int(o['--fake-free-mb']))
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()); wd = os.path.join(s['SCRATCH'], 'k6proof_%s' % stamp); os.makedirs(wd)
    jp = os.path.join(wd, '0_judge_ENTRY_%s.job.sh' % o['--idea']); open(jp, 'x').write(job)
    log = os.path.join(wd, 'ISOLATION.log'); open(log, 'x').close()
    arch = sorted(os.path.join(d, x) for d, ds, _ in os.walk(ALARM) for x in ds if x == 'archive')
    forbid = [x for x in (s.get('FORBID') or '').split(':') + o['--forbid-more'].split(':') if x] + arch
    env = dict(os.environ, PYTHONPATH=os.path.join(ALARM, '_vendor', 'home_kit', 'isolation'), CTXG_ISOLATE='1', CTXG_FORBID=':'.join(forbid), CTXG_ALLOW='',
               CTXG_ISOLATION_LOG=log)
    t0 = time.time(); r = subprocess.run(['bash', jp], capture_output=True, text=True, cwd=wd, stdin=subprocess.DEVNULL, env=env)
    rec = os.path.join(s['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', o['--run'], 'receipts', '0_ENTRY_%s' % o['--idea'])
    st = [l.rstrip('\n').split('\t') for l in open(os.path.join(rec, 'STAGES.tsv'))][1:] if os.path.isfile(os.path.join(rec, 'STAGES.tsv')) else []
    for x in st:
        print('  stage %-16s rc %-2s %4s s  %s' % (x[0], x[1], x[2], x[4][:150]))
    bad_st = [x for x in st if x[1] != '0']; end = any(x[0] == 'end' and x[1] == '0' for x in st)
    print('3 JOB: bash exit %d in %.0f s; stages %d, not rc 0: %s; end line: %s' % (r.returncode, time.time() - t0, len(st), [x[0] for x in bad_st] or 'none', 'yes' if end else 'NO'))
    opened = sorted({l.rstrip('\n').split('\t')[3] for l in open(log) if l.count('\t') >= 3})
    data_keys = tuple(RI.DATA_KEYS) + (() if 'FEED_GATE' in RI.DATA_KEYS else ('FEED_GATE',))
    data = [os.path.realpath(s[k]) for k in data_keys if s.get(k)]
    bad = RI.judge(opened, [os.path.realpath(x) for x in forbid], data, [])
    print('4 PYTHON PROCESSES OF THE JOB: %d files opened under %d forbidden roots (FORBID, --forbid-more, %d archive/ folders of this Alarm folder): '
          '%d data files under the settings keys, failing (code, no data or a past edition): %d %s' % (len(opened), len(forbid), len(arch), len(opened) - len(bad), len(bad), bad[:5]))
    runs = [x[4].split(' run ')[-1] for x in st if x[0].startswith('store_') and ' run ' in x[4]]
    code_out = []
    for rd in runs:
        m = json.load(open(os.path.join(rd, 'RUN.json'))) if os.path.isfile(os.path.join(rd, 'RUN.json')) else {'code_sha16': {'<no RUN.json in %s>' % rd: ''}}
        code_out += [q for q in list(m.get('code_sha16', {})) + [m.get('pins_file', {}).get('path', '<no pins file>')] if not under(os.path.realpath(q), [ALARM])]
        print("  the grader's RUN.json (%s): %d executed files, pins %s; outside this Alarm folder: %s" % (rd, len(m.get('code_sha16', {})),
              m.get('pins_file', {}).get('sha16'), code_out or 'none'))
    print('receipts %s; job %s (sha16 %s)' % (rec, jp, sha16(jp)))
    ok = r.returncode == 0 and st and not bad_st and end and not bad and runs and not code_out
    print('RUN PROOF ENTRY_V6:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
