"""mutants_v6.py (SCOUT, 30 Oct 2026; TEST, NOT REVIEWED): planted bugs in queue_job_v5.py, JOB_COUNT_V6, JOB_CLEAN_V6 and
clean_scratch_v2.py; test_kit5_v6.py must fail on every one. Each mutant runs in its own small copy of the Alarm package (only the files
the tests read), in a new temporary folder that is removed after it (mutants_v1.py kept one whole kit per mutant and filled the VM's disk
on 30 Oct). A mutated file is re-pinned where the kit pins it (a template in queue_job_v5's TEMPLATE_SHA, clean_scratch_v2 in
JOB_CLEAN_V6), so a mutant is caught by what the code does, never by a changed sha16. The unmutated copy must pass first.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/mutants_v6.py [FIRST LAST]      (mutants FIRST..LAST, 1-based; default all)
Exit 0: every mutant run was killed; 1: one or more alive; 2: refused (the unmutated copy fails, or a mutant's text is not in its file as
often as the list says)."""
import hashlib, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT5 = os.path.dirname(HERE)
PKG = os.path.normpath(os.path.join(KIT5, '..', '..', '..', '..'))
KIT = os.path.join('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5')
COPY = [os.path.join('_tools', 'settings_v1.py'), os.path.join('_tools', 'machine_paths_v2.py'), os.path.join('settings', 'SETTINGS_EXAMPLE.env'),
        os.path.join('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py')] + [
        os.path.join(KIT, *x.split('/')) for x in ('tools/queue_job_v5.py', 'tools/clean_scratch_v2.py', 'jobs/JOB_COUNT_V6.job.sh.txt',
                                                    'jobs/JOB_CLEAN_V6.job.sh.txt', 'jobs/JOB_GRADE_V6.job.sh.txt', 'jobs/JOB_GRADE_V7.job.sh.txt', 'jobs/JOB_MONTH_V6.job.sh.txt', 'jobs/JOB_MONTH_V7.job.sh.txt', 'jobs/JOB_ENTRY_V6.job.sh.txt', 'tests/test_kit5_v6.py',
                                                    'tests/mutants_v6.py')] + [
        os.path.join(KIT, 'runs', 'TEMPLATE_V3', 'registers', n + '.tsv') for n in ('DECISIONS', 'FORECASTS', 'LEARNINGS_PROPOSED', 'POSTMORTEMS',
                                                                              'PROBLEMS', 'RUNS', 'TOOLS_BUILT', 'VARIANTS')]   # the register headers
PINNED_BY = {'jobs/JOB_COUNT_V6.job.sh.txt': ['tools/queue_job_v5.py'], 'jobs/JOB_CLEAN_V6.job.sh.txt': ['tools/queue_job_v5.py'],
             'tools/clean_scratch_v2.py': ['jobs/JOB_CLEAN_V6.job.sh.txt']}
Q5, C2, JC, JL = 'tools/queue_job_v5.py', 'tools/clean_scratch_v2.py', 'jobs/JOB_COUNT_V6.job.sh.txt', 'jobs/JOB_CLEAN_V6.job.sh.txt'
M = [   # (file in KIT_V5, text, planted text, how many times the text is in the file)
 (Q5, "    if opts['--settings'] is None:\n", "    if False:\n", 1),
 (Q5, "    if kind not in TEMPLATE_SHA:\n", "    if False:\n", 1),
 (Q5, "    vals['FEED_GATE'] = j.get('FEED_GATE') or ''", "    vals['FEED_GATE'] = ''", 1),
 (Q5, "        if k == 'FEED_GATE' and not vals[k]:\n            continue\n", "", 1),
 (JC, "--gate=@@FEED_GATE@@ ", "", 1),
 (Q5, "        w = WORDS.search(b)\n", "        w = WORDS.search(f)\n", 1),
 (Q5, "        if not SAFE.match(vals[k]):\n", "        if False:\n", 1),
 (Q5, "    'KIT': os.path.join(AD, 'KIT_V5'),\n", "    'KIT': os.path.join(ALARM, 'KIT_V5'),\n", 1),
 (Q5, "    return {'@@%s@@' % k: vals[k] for k in PATHS}\n", "    return dict({'@@%s@@' % k: vals[k] for k in PATHS}, **{'@@SCRATCH@@': vals['LAB_DAYS']})\n", 1),
 (Q5, "    return {'@@%s@@' % k: vals[k] for k in PATHS}\n", "    return dict({'@@%s@@' % k: vals[k] for k in PATHS}, **{'@@LAB_DAYS@@': vals['RESEARCH_ROOT']})\n", 1),
 (Q5, "    vals['ALARM'] = s.get('RUNNER_RELEASE') or ALARM\n", "    vals['ALARM'] = s.get('RUNNER_RELEASE') or os.path.dirname(ALARM)\n", 1),
 (Q5, "        r = subprocess.run(['bash', '-n'], input=b, capture_output=True, text=True)",
      "        open(os.path.join(CFG['H'], 'dry.sh'), 'w').write(b); r = subprocess.run(['bash', '-n', os.path.join(CFG['H'], 'dry.sh')], capture_output=True, text=True)", 1),
 (Q5, "    if flags['--dry']:\n", "    if flags['--dry'] and False:\n", 1),
 (Q5, "'ALLOC': ['python3', '-B', s['RUNNER_ALLOC']]", "'ALLOC': ['python3', '-B', os.path.join(s['RUNNER_QUEUES'], 'job_alloc.py')]", 1),
 (Q5, "    'REG': os.path.join(AD, 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py'),\n", "    'REG': os.path.join(AD, 'KIT_V5', 'tools', 'reg_append_v1.py'),\n", 1),
 (Q5, "os.path.join(CFG['JOB_SCRATCH'], 'work_%s' % os.path.basename(run), from_job) + os.sep", "os.path.join(CFG['H'], 'work_%s' % os.path.basename(run), from_job) + os.sep", 1),
 (Q5, "os.path.join(CFG['JOB_SCRATCH'], 'work_%s' % os.path.basename(run), from_job) + os.sep", "os.path.join(CFG['JOB_SCRATCH'], 'work_%s' % os.path.basename(run), from_job)", 1),
 (Q5, "    if not os.path.isdir(CFG['WDB']):\n", "    if not os.path.isdir(CFG['H']):\n", 1),
 (Q5, "'H': os.path.join(s['RESEARCH_ROOT'], 'ALARM_DESIGN')", "'H': os.path.join(s['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs')", 1),
 (Q5, "    if kind != 'CLEAN' and len(mine) >= limit:\n", "    if False:\n", 1),
 (Q5, "            if not any(x.get('job') == j for x in regs['POSTMORTEMS']):\n", "            if False:\n", 1),
 (JC, "--lab-root @@LAB_DAYS@@ ", "", 1),
 (JC, "export METRICS_V1=$F/team/LAB3/METRICS_V1.tsv METRIC_TRAPS=", "export METRIC_TRAPS=", 1),
 (JC, "\ncd $AL\n", "\ncd @@SCRATCH@@\n", 1),
 (JC, "W=@@SCRATCH@@/work_@@RUNTAG@@/$J", "W=@@RESEARCH_ROOT@@/work_@@RUNTAG@@/$J", 1),
 (JC, "fmb(){ df -m @@SCRATCH@@ |", "fmb(){ df -m @@LAB_DAYS@@ |", 1),
 (JC, "ck $ROSTER b93de33b2a73a56e; ", "", 1),
 (JC, "R=$F/team/RESEARCH; PY=@@PYTHON@@", "R=$F/team/RESEARCH; PY=python3", 1),
 (JC, "t-prev>1800", "t-prev>18000", 1),
 (JL, " --scratch @@SCRATCH@@ --", " --scratch @@LAB_DAYS@@ --", 2),
 (JL, "K5=$AL/Agentic/tree/ALARM_DESIGN/KIT_V5;", "K5=@@RESEARCH_ROOT@@/ALARM_DESIGN/KIT_V5;", 1),
 (C2, "def plan_job(run, seat, j, scratch):\n", "def plan_job(run, seat, j, scratch):\n    scratch = os.path.join(scratch, 'judge_scratch')\n", 1),
 (C2, "                if not (ok_chain or ok_run):\n", "                if False:\n", 1),
 (C2, "        if os.path.islink(w) or not os.path.realpath(w).startswith(os.path.realpath(scratch) + os.sep):\n", "        if False:\n", 1),
 # --job-settings and RUNNER_RELEASE (SCOUT 30 Oct 22:2xZ): the job takes the runner's paths, the queue keeps its own
 (Q5, "    j = s if job_path is None else _load(job_path, JOB_NEED, 'JOB SETTINGS')\n", "    j = s\n", 1),
 (Q5, "    paths = use_settings(opts['--settings'], opts['--job-settings'])\n", "    paths = use_settings(opts['--settings'])\n", 1),
 (Q5, "    vals['ALARM'] = s.get('RUNNER_RELEASE') or ALARM\n", "    vals['ALARM'] = ALARM\n", 1),
 (Q5, "    vals['ALARM'] = s.get('RUNNER_RELEASE') or ALARM\n", "    vals['ALARM'] = j.get('RUNNER_RELEASE') or ALARM\n", 1),
 (Q5, "    vals['ALARM'] = s.get('RUNNER_RELEASE') or ALARM\n", "    vals['ALARM'] = s.get('RUNNER_RELEASE', ALARM)\n", 1),
 (Q5, "'H': os.path.join(s['RESEARCH_ROOT'], 'ALARM_DESIGN')", "'H': os.path.join(j['RESEARCH_ROOT'], 'ALARM_DESIGN')", 1),
 (Q5, "'RUNNER': s['RUNNER_QUEUES']", "'RUNNER': j['RUNNER_QUEUES']", 1),
 (Q5, "'ALLOC': ['python3', '-B', s['RUNNER_ALLOC']]", "'ALLOC': ['python3', '-B', j['RUNNER_ALLOC']]", 1),
 (Q5, "'WDB': s['SCRATCH']", "'WDB': j['SCRATCH']", 1),
 (Q5, "'JOB_SCRATCH': j['SCRATCH']", "'JOB_SCRATCH': s['SCRATCH']", 1),
 (Q5, "    s = _load(path, NEED + (JOB_NEED if job_path is None else ()), 'SETTINGS')\n", "    s = _load(path, NEED + JOB_NEED, 'SETTINGS')\n", 1),
 (Q5, "    s = _load(path, NEED + (JOB_NEED if job_path is None else ()), 'SETTINGS')\n", "    s = _load(path, NEED, 'SETTINGS')\n", 1),
 (Q5, "_load(job_path, JOB_NEED, 'JOB SETTINGS')", "_load(job_path, (), 'JOB SETTINGS')", 1),
 # the quiet window, removed by the owner 30 Oct 2026 23:32 Berlin: each way of putting it back must be caught
 (Q5, "    seat, vs, block, sub, row = plan(run, kind, idea, items, opts['--from-job'], flags['--forward-only'])\n",
      "    now = CFG['now']()\n    if now.hour * 100 + now.minute >= 2320 or now.hour * 100 + now.minute < 15:\n"
      "        raise Refused('QUIET WINDOW: nothing is queued from 23:20Z to 00:15Z')\n"
      "    seat, vs, block, sub, row = plan(run, kind, idea, items, opts['--from-job'], flags['--forward-only'])\n", 1),
 (Q5, "    seat, vs, block, sub, row = plan(run, kind, idea, items, opts['--from-job'], flags['--forward-only'])\n",
      "    seat, vs, block, sub, row = plan(run, kind, idea, items, opts['--from-job'], flags['--forward-only'])\n    now = CFG['now']()\n"
      "    if now.hour * 60 + now.minute + int(sub['@@MINUTES@@']) > 23 * 60 + 30 and now.hour * 100 + now.minute >= 15:\n"
      "        raise Refused('QUIET WINDOW: this job would run into 23:30Z')\n", 1),
 (JC, 'f=$(fmb); st start 0 0 "SCRATCH_DISK free ${f} MB"\n',
      'h=$((10#$(date -u +%H%M))); if [ $h -ge 2320 ] || [ $h -lt 15 ]; then st quiet 0 0 "QUIET WINDOW NEAR: not started"; st end 0 0 "not started"; exit 0; fi\n'
      'f=$(fmb); st start 0 0 "SCRATCH_DISK free ${f} MB"\n', 1),
 (JL, 'f0=$(fmb); st start 0 0 "SCRATCH_DISK free ${f0} MB"\n',
      'h=$((10#$(date -u +%H%M))); if [ $h -ge 2320 ] || [ $h -lt 15 ]; then st quiet 0 0 "QUIET WINDOW NEAR: not started"; st end 0 0 "not started"; exit 0; fi\n'
      'f0=$(fmb); st start 0 0 "SCRATCH_DISK free ${f0} MB"\n', 1),
]


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def build(base):
    for rel in COPY:
        d = os.path.join(base, 'Alarm', rel)
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(os.path.join(PKG, rel), d)
    return os.path.join(base, 'Alarm', KIT)


def repin(kit, rel, old):
    """the files that pin <rel> by its sha16 take its new one (and so on up: clean_scratch_v2 -> JOB_CLEAN_V6 -> queue_job_v5)"""
    new = sha16(os.path.join(kit, rel))
    for g in PINNED_BY.get(rel, ()):
        p = os.path.join(kit, g)
        s, g_old = open(p).read(), sha16(p)
        if s.count(old) != 1:
            raise SystemExit('REFUSED: %s pins %s %d times, not once' % (g, old, s.count(old)))
        with open(p, 'w') as f:
            f.write(s.replace(old, new))
        repin(kit, g, g_old)


def tests_fail(kit):
    r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(kit, 'tests', 'test_kit5_v6.py')], capture_output=True, text=True,
                       timeout=600, stdin=subprocess.DEVNULL)
    last = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith('TESTS ')]
    return r.returncode != 0, (last[-1] if last else 'no summary line')


def main(a):
    first, last = (int(a[0]), int(a[1])) if len(a) == 2 else (1, len(M))
    for i, (rel, old, new, n) in enumerate(M, 1):
        c = open(os.path.join(KIT5, *rel.split('/'))).read().count(old)
        if c != n:
            print('REFUSED: mutant %d: %r is in %s %d times, not %d' % (i, old, rel, c, n))
            return 2
    base = tempfile.mkdtemp(prefix='k6mut_')
    try:
        failed, line = tests_fail(build(base))
    finally:
        shutil.rmtree(base, ignore_errors=True)
    if failed:
        print('REFUSED: the unmutated copy fails its tests (%s)' % line)
        return 2
    print('baseline: the unmutated copy passes (%s)' % line, flush=True)
    alive = []
    for i in range(first, last + 1):
        rel, old, new, n = M[i - 1]
        base = tempfile.mkdtemp(prefix='k6mut_')
        try:
            kit = build(base)
            p = os.path.join(kit, *rel.split('/'))
            s, before = open(p).read(), sha16(p)
            with open(p, 'w') as f:
                f.write(s.replace(old, new))
            repin(kit, rel, before)
            failed, line = tests_fail(kit)
        finally:
            shutil.rmtree(base, ignore_errors=True)
        print('mutant %2d %-30s %s  %s' % (i, rel, 'KILLED' if failed else 'ALIVE <-- ' + old.strip()[:70], line), flush=True)
        if not failed:
            alive.append(i)
    print('mutants %d..%d of %d: killed %d, alive %d %s' % (first, last, len(M), last - first + 1 - len(alive), len(alive), alive or ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
