#!/usr/bin/env python3
"""queue_job_v8.py (SCOUT for ALARM_DESIGN KIT_V5, 31 Oct 2026, V2_0 stage 1; TEST, NOT REVIEWED): queue_job_v7.py 5f9a50a3c5f525a7 with only GRADE
on JOB_GRADE_V10 (35ff1397e19ab0a9: chain v2_0_5, the Outcomes runs and then the menu and the card at the same time, each perfire beside the next
step, 6 cores declared) and MONTH on JOB_MONTH_V10 (9e4b771485b43cd5: chain v2_2_5, its Outcomes runs and then its menu and card at the same
time); team/SCOUT/SPEED_V2_0_DESIGN_V1.md Q1-Q3; GRADE's MEM_MB 2710 for 1 variant (job 20265150: tree peak 2253 MB + 20 percent) and 2931 for 2 or 3 (job 20265156: tree peak 2442 MB + 20 percent; CONDUCTOR's design review M1). The rest of this text is queue_job_v7.py's:
queue_job_v7.py: queue_job_v6.py d4477631c22b027a with only
GRADE and MONTH on their V9 templates and MONTH's MEM_MB changed: JOB_GRADE_V9 (cf0baab20d828d61: chain v2_0_4, Outcomes in 3 worker
processes, 3 cores declared, one du at the end) and JOB_MONTH_V9 (fe73a394772eb046: chain v2_2_4, the detection parts by the chain's
rule, 3 cores declared, one du at the end), K16 T5, T6 and T8; MONTH's MEM_MB 4030, the measured peak + 20 percent (WORKING_SESSION_V16
section 0.7; job 20264959 x1: a 2-part tree up to 3,355,115,520 bytes, DETECT_RUN_B.json sum_peak_rss_bytes; was 8000). SCOUT, 31 Oct 2026 (the owner 10:51 Berlin, of CLEAN: "remove it"; scratch cleanup is DSK's, on
the owner's word): KIND CLEAN is refused (CLEAN REMOVED) and is in no table; a finished job's scratch counts in the disk budget only while
its folder is on SCRATCH_DISK (DSK's sweep frees it); GRADE's MEM_MB 2710, the measured V9 peak + 20 percent (job 20265002: the detection
part tree 2,255,994,880 bytes, the two parts one after the other; was 6000). The docstring of queue_job_v6.py follows.
queue_job_v6.py (SCOUT K12 for ALARM_DESIGN KIT_V5, 31 Oct 2026; TEST, NOT REVIEWED): queue_job_v5.py d1cf44aeb5487d50 with only
GRADE and MONTH moved to JOB_GRADE_V8 (bde3b7d82e6ce7f7) and JOB_MONTH_V8 (7779de8ad87bffee), whose chains v2_0_3 and v2_2_3 run Outcomes with the feed's
stop gate from FEED_GATE and the research days from RESEARCH_STORE, and the job path placeholder @@RESEARCH_STORE@@ (the settings key
RESEARCH_STORE of the machine that runs the job: now one of the keys --job-settings must have). The rest of this text is
queue_job_v5.py's.
queue_job_v5.py (SCOUT for ALARM_DESIGN KIT_V5, 30 Oct 2026; TEST, NOT REVIEWED). The only way a KIT_V5 agent queues a job, run from the
Alarm package. queue_job_v4.py (3d5abaea8c3cbe33) with only its paths changed (CLEAN_RELEASE_V1 sections 1 and 6; the owner 30 Oct 2026 22:21
Berlin: "Let's make sure everything can run from the release folder"):
  - code only from the Alarm folder that holds this file (settings_v1.alarm_root): the job templates TEMPLATE_NAME (JOB_<KIND>_V6,
    GRADE and MONTH V7: Agentic/tree/ALARM_DESIGN/KIT_V5/jobs, pinned by TEMPLATE_SHA) and the register writer reg_append_v1.py
    (Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools, pinned by REG_SHA);
  - its own data only under the keys of --settings, the file of the machine it runs on (settings_v1's rules): RESEARCH_ROOT
    (ALARM_DESIGN/runs/<RUN>, runs/IDEAS_CLAIMED), RUNNER_QUEUES (Q_V1..Q_V21), RUNNER_ALLOC (the runner's job_alloc.py, run where it is),
    SCRATCH (its free space);
  - the job is filled at queue time with the paths of the machine that runs it (SCOUT 30 Oct: jobs run on the Mac, so a job queued in the
    VM still names the Mac's paths): @@PYTHON@@, @@RESEARCH_ROOT@@, @@SCRATCH@@ (a job's scratch is SCRATCH/work_<RUN>/<JOB>) and
    @@LAB_DAYS@@ and @@FEED_GATE@@ (the feed's stop gate; empty: none) from --job-settings (the runner machine's settings file; default --settings); @@ALARM@@ from RUNNER_RELEASE of --settings
    (the release the runner runs jobs from), or this Alarm folder when RUNNER_RELEASE is empty;
  - only the kinds that have a V6 template are queued (COUNT and CLEAN); GRADE, ENTRY and MONTH are refused (NOT CLEAN YET) until their
    tools are released;
  - the quiet window was removed by the owner 30 Oct 2026 23:32 Berlin ("All jobs can be queued. Please do not stop queueing jobs"): no
    refusal from 23:20Z to 00:15Z or for a job that would run into 23:30Z, and the V6 jobs no longer stop near it.
Reads no market data. Never deletes; never overwrites (twin opened 'x', IN via .part + rename).

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v8.py --settings <file> [--job-settings <file>] <RUN> <KIND> <IDEA> <ITEMS> [--queue Q_Vn] [--from-job <JOB>] [--behind] [--forward-only] [--dry]
    --settings      this machine's settings file (settings/SETTINGS_<MACHINE>.env), always named
    --job-settings  the settings file of the machine that runs the job (the job runner's), when it is another one (default --settings)
    RUN    the run tag, e.g. AD1_20261029 (folder RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>; the seat is the part before _, e.g. AD1)
    KIND   COUNT  ITEMS = V1=ideas/<IDEA>/defs/V1.json[,V2=...]  (up to 3 definitions; detection only, no outcome read)
           CLEAN  REMOVED (the owner 31 Oct 2026 10:51 Berlin): refused; scratch cleanup is DSK's, on the owner's word.
           GRADE, ENTRY, MONTH: NOT CLEAN YET (their checks below are v4's, kept for their V6 templates)
           GRADE  ITEMS = V1[,V2,V3]  (each registered in VARIANTS with one PREREG; Sep-Dec grade + hand-off)
           ENTRY  ITEMS = V1[,...] --from-job <the GRADE job>  (only variants whose hand-off R1 passed)
           MONTH  ITEMS = V1[,...] --from-job <the GRADE job>  (only PASS or NEEDS MORE MONTHS; Jan-Apr forecasts in FORECASTS)
                  --forward-only (the owner 29 Oct 22:02 Berlin): V is the OTHER side of a STOP variant V0 (same definition, other lean,
                  VARIANTS reason 'FORWARD ONLY OF V0', never graded itself); --from-job is V0's GRADE job; only Jan-Apr decides
                  (decide_forward_v1.py: month_read_v3 HELD or STRONGER in 3 or more of 4 months).
    --queue   a Q_V queue (default: the first empty one of Q_V1..Q_V21)
    --behind  allow a queue that holds only your own jobs (your 3rd job then waits there)
    --dry     every check, then print the filled job; claims, writes and queues nothing (bash -n reads the job from its input)

What it checks (KIT_V5 LEARNINGS_V5 rows in brackets): names in capitals and digits (V5-39); the idea's claim file; the try budget, at
most 3 graded variants an idea, each in VARIANTS before its job (V5-07, V5-20); definition and PREREG files unchanged since VARIANTS
(V5-20); for ENTRY the hand-off R1 of each variant, for MONTH the decision and the sealed Jan-Apr forecasts (V5-16); your own jobs
(at most 2, or 3 with --behind) (V5-22); an empty queue (V5-19); SCRATCH_DISK (SCRATCH) free at
least 60,000 MB plus the job's WRITES_MB (V5-21); the template's sha16; no placeholder left; no refused word in the job's own text (the
settings' paths go in after that check: a path such as <install>/Alarm/alarm/<RELEASE> is not a command); each settings path it fills
set and plain (letters, digits, _ . / -); bash -n (V5-29). Then it
claims the number from the live allocator (V5-18), writes the twin to RUN/jobs/, the RUNS row through reg_append_v1.py (all or
nothing: a failed row queues nothing) and copies the twin into the queue's IN. Disk budget (V5-41): a run may hold at most
RUN_BUDGET_MB of its own scratch on SCRATCH_DISK (measured from finished receipts while the job's scratch folder is there, declared for the
rest); scratch cleanup is DSK's (the owner 31 Oct 2026 10:51 Berlin).
"""
import sys, os, re, json, hashlib, subprocess, datetime, math, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))


def _refused_at_start(msg):
    print('REFUSED: %s' % msg, file=sys.stderr)
    raise SystemExit(2)


def _settings_reader():
    """settings_v1 of the Alarm package that holds this file (this file sits at <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools), loaded by
    its path, so the reader, its keys and its rule 'data lives outside this Alarm folder' are this package's own"""
    p = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..', '_tools', 'settings_v1.py'))
    if not os.path.isfile(p):
        _refused_at_start('NOT INSIDE AN ALARM PACKAGE: no %s (run queue_job_v8.py from the Alarm folder)' % p)
    spec = importlib.util.spec_from_file_location('settings_v1_of_queue_job_v8', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


SV = _settings_reader()
try:
    ALARM = SV.alarm_root(__file__)                              # the code root (CLEAN_RELEASE_V1 section 6)
except SV.Refused as _e:
    _refused_at_start(str(_e))
if os.path.realpath(ALARM) != os.path.realpath(SV.ALARM):
    _refused_at_start('TWO ALARM FOLDERS: %s holds this file, %s holds its settings reader' % (ALARM, SV.ALARM))
AD = os.path.join(ALARM, 'Agentic', 'tree', 'ALARM_DESIGN')      # the kit inside Alarm: Agentic's tree keeps the dev layout
CFG = {
    'H': None,                    # RESEARCH_ROOT/ALARM_DESIGN: the agent runs and their registers (use_settings)
    'KIT': os.path.join(AD, 'KIT_V5'),
    'RUNNER': None,               # RUNNER_QUEUES (use_settings)
    'ALLOC': None,                # python3 -B RUNNER_ALLOC (use_settings)
    'WDB': None,                  # SCRATCH of --settings (use_settings): its free MB, seen from this machine
    'JOB_SCRATCH': None,          # SCRATCH of --job-settings (use_settings): every job's scratch SCRATCH/work_<RUN>/<JOB>, as the runner names it
    'REG': os.path.join(AD, 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py'),
    'REG_SHA': 'c301c5977ecd6860',
    'QUEUES': ['Q_V%d' % i for i in range(1, 22)],
    'MIN_FREE_MB': 60000,
    'RUN_BUDGET_MB': 10000,      # 10,000 from round 3 19:40Z (29 Oct; was 8,000 from round 2): two ideas at once held ENTRY out (AD9 19:29Z); 3 runs x 10,000 plus the 60 GB floor = 90 GB; SCRATCH_DISK 100 GB free 19:36Z
    'now': lambda: datetime.datetime.now(datetime.timezone.utc),     # the clock tests plant; no rule reads it since the quiet window went
    'free_mb': None,          # tests set a function; None = statvfs of CFG['WDB']
}
TEMPLATE_SHA = {'COUNT': 'ff3455fd96087ed7', 'GRADE': '35ff1397e19ab0a9', 'MONTH': '9e4b771485b43cd5',
                'ENTRY': '2d55b4788a059d10'}   # the templates (COUNT runs detect_v2 with --gate, 31 Oct; MONTH by SCOUT K4, 30 Oct; ENTRY,
# the store runner v11 and the grader rel1, by SCOUT K6, 31 Oct; GRADE V7: chain v2_0_2 with the grader rel1 and its relative pins, and
# MONTH V7: chain v2_2_2 with the aw1 rel1 editions and their relative pins, by SCOUT K12, 31 Oct, after round 7 found every V6 GRADE
# refused UNPINNED_MODULE; GRADE V8 and MONTH V8: chains v2_0_3 and v2_2_3, Outcomes with the gate from FEED_GATE and the research
# days from RESEARCH_STORE, SCOUT K12, 31 Oct; GRADE V9 and MONTH V9: chains v2_0_4 (Outcomes in 3 worker processes) and v2_2_4 (the
# detection parts by the chain's rule), 3 cores declared, one du at the end, SCOUT K16, 31 Oct); a KIND without one is NOT CLEAN YET
TEMPLATE_NAME = {'COUNT': 'JOB_COUNT_V6.job.sh.txt', 'GRADE': 'JOB_GRADE_V10.job.sh.txt',
                 'MONTH': 'JOB_MONTH_V10.job.sh.txt', 'ENTRY': 'JOB_ENTRY_V6.job.sh.txt'}   # each KIND's template file in KIT_V5/jobs
KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH')
CLEAN_REMOVED = "CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; scratch cleanup is DSK's, on the owner's word"   # SCOUT, 31 Oct 2026: KIND CLEAN is refused by name
WORK = ('COUNT', 'GRADE', 'ENTRY', 'MONTH')
JOBNAME = re.compile(r'^[0-9]+_(COUNT|GRADE|ENTRY|MONTH)_[A-Z][A-Z0-9]{0,23}$')
NAME = re.compile(r'^[A-Z][A-Z0-9]{0,23}$')
RUNTAG = re.compile(r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$')
SAFE = re.compile(r'^[A-Za-z0-9_./-]+$')
WORDS = re.compile(r'(?<![A-Za-z0-9_])(rm|dd|git|sudo|sleep|timeout|alarm)(?![A-Za-z0-9_])')
TOKEN = re.compile(r'@@[A-Z_]+@@')
MONTHS = ('2601', '2602', '2603', '2604')
NEED = ('RESEARCH_ROOT', 'RUNNER_QUEUES', 'RUNNER_ALLOC', 'SCRATCH')         # the keys of --settings this tool uses (its own paths)
JOB_NEED = ('PYTHON', 'LAB_DAYS', 'SCRATCH', 'RESEARCH_ROOT', 'RESEARCH_STORE')                 # the keys of --job-settings that go into the job
PATHS = ('ALARM', 'PYTHON', 'RESEARCH_ROOT', 'SCRATCH', 'LAB_DAYS', 'FEED_GATE', 'RESEARCH_STORE')               # the job's path placeholders @@<KEY>@@
REGISTERS = ('VARIANTS', 'FORECASTS', 'RUNS', 'DECISIONS', 'POSTMORTEMS', 'LEARNINGS_PROPOSED', 'PROBLEMS', 'TOOLS_BUILT')


class Refused(Exception):
    pass


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def read_reg(run, name):
    p = os.path.join(run, 'registers', name + '.tsv')
    if not os.path.isfile(p):
        raise Refused('NO REGISTER %s' % p)
    with open(p) as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    if not lines:
        raise Refused('EMPTY REGISTER (no header) %s' % p)
    hdr = lines[0].split('\t')
    return [dict(zip(hdr, l.split('\t'))) for l in lines[1:]]


def latest(rows, **kw):
    hit = [r for r in rows if all(r.get(k) == v for k, v in kw.items())]
    return hit[-1] if hit else None


def _load(path, need, which):
    """a settings file read by this package's settings_v1 (every key; values empty or absolute paths outside Alarm), the keys named set"""
    try:
        s = SV.load(path)
    except SV.Refused as e:
        raise Refused('%s: %s' % (which, e))
    for k in need:
        if not s.get(k):
            raise Refused('%s KEY %s IS EMPTY in %s (this tool needs %s)' % (which, k, path, ', '.join(need)))
    return s


def use_settings(path, job_path=None):
    """--settings (this machine: the queue's own paths) and --job-settings (the machine that runs the job; default --settings): the job's
    data paths come from the second, @@ALARM@@ from RUNNER_RELEASE of the first (this Alarm folder when it is empty); every path that goes
    into a job line must be plain (letters, digits, _ . / -). Sets the data places of CFG; returns the job's path placeholders"""
    s = _load(path, NEED + (JOB_NEED if job_path is None else ()), 'SETTINGS')
    j = s if job_path is None else _load(job_path, JOB_NEED, 'JOB SETTINGS')
    vals = dict((k, j[k]) for k in JOB_NEED)
    vals['ALARM'] = s.get('RUNNER_RELEASE') or ALARM
    vals['FEED_GATE'] = j.get('FEED_GATE') or ''           # the feed's stop gate file of the runner machine; empty: no gate (detect_v2 --gate=)
    for k in PATHS:
        if k == 'FEED_GATE' and not vals[k]:
            continue
        if not SAFE.match(vals[k]):
            raise Refused('UNSAFE PATH %s=%r: a job line takes letters, digits and _ . / - only' % (k, vals[k]))
    CFG.update({'H': os.path.join(s['RESEARCH_ROOT'], 'ALARM_DESIGN'), 'RUNNER': s['RUNNER_QUEUES'],
                'ALLOC': ['python3', '-B', s['RUNNER_ALLOC']], 'WDB': s['SCRATCH'], 'JOB_SCRATCH': j['SCRATCH']})
    return {'@@%s@@' % k: vals[k] for k in PATHS}


def free_mb():
    """SCRATCH_DISK (SCRATCH) free MB, or None when this session cannot see it (each job checks the 60 GB floor itself when it starts)"""
    if CFG['free_mb'] is not None:
        return CFG['free_mb']()
    if not os.path.isdir(CFG['WDB']):
        return None
    s = os.statvfs(CFG['WDB'])
    return s.f_bavail * s.f_frsize // 1048576


def jobs_in(q):
    out = []
    for sub in ('IN', 'RUN'):
        d = os.path.join(CFG['RUNNER'], q, sub)
        if os.path.isdir(d):
            out += [(sub, f) for f in os.listdir(d) if f.endswith('.job.sh')]
    return out


def own_jobs(seat):
    pat = '_judge_%s_' % seat
    out = []
    for q in sorted(os.listdir(CFG['RUNNER'])):
        if q.startswith('Q_') and os.path.isdir(os.path.join(CFG['RUNNER'], q)):
            out += [(q, sub, f) for sub, f in jobs_in(q) if pat in f]
    return out


def stage_ok(run, receipts_rel, v, kind):
    """None while r's job has no end line (queued or running); True when v's own stage(s) ended rc 0; False when the job ended
    without them (failed, or stopped before v): such a job gave no result for v (SCOUT 29 Oct)"""
    p = os.path.join(run, receipts_rel or '', 'STAGES.tsv')
    if not receipts_rel or not os.path.isfile(p):
        return None
    rows = [l.rstrip('\n').split('\t') for l in open(p) if l.strip()][1:]
    if not any(x and x[0] == 'end' for x in rows):
        return None
    need = ['store_' + v, 'markout_' + v] if kind == 'ENTRY' else ['grade_' + v]
    return all(any(x[0] == s and len(x) > 1 and x[1] == '0' for x in rows) for s in need)


def receipts_done(run, job):
    d = os.path.join(run, 'receipts', job)
    p = os.path.join(d, 'STAGES.tsv')
    if not os.path.isfile(p):
        raise Refused('JOB %s HAS NO RECEIPTS YET (%s)' % (job, p))
    rows = [l.rstrip('\n').split('\t') for l in open(p) if l.strip()][1:]
    end = [r for r in rows if r and r[0] == 'end']
    if not end:
        raise Refused('JOB %s NOT FINISHED (no end line in STAGES.tsv)' % job)
    bad = [r for r in rows if len(r) > 1 and r[1] != '0']
    return d, bad


def check_window(path, v):
    """one definition serves the Sep-Dec grade and the Sep-Apr MONTH job: its window must cover 20250910 to 20260430"""
    try:
        w = json.load(open(path)).get('window') or {}
    except ValueError as e:
        raise Refused('DEFINITION NOT JSON %s: %s' % (path, e))
    if not (str(w.get('first', '99999999')) <= '20250910' and str(w.get('last', '0')) >= '20260430'):
        raise Refused('DEFINITION WINDOW OF %s IS %s: it must hold 20250910 to 20260430: write first 20250901, last 20260430 (AGENTS.md, the months rule); the chain decides the months read' % (v, w))


def bash_array(name, vals):
    for v in vals:
        if not SAFE.match(v):
            raise Refused('UNSAFE VALUE FOR %s: %r' % (name, v))
    return '%s=(%s)' % (name, ' '.join(vals))


def plan(run, kind, idea, items, from_job, forward_only=False):
    """every check that needs no claim; returns the substitutions and the RUNS row fields"""
    m = RUNTAG.match(os.path.basename(run.rstrip('/')))
    seat = m.group(1)
    regs = {n: read_reg(run, n) for n in REGISTERS}
    claim = os.path.join(CFG['H'], 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (os.path.basename(run), idea))
    if kind != 'CLEAN' and not os.path.isfile(claim):
        raise Refused('IDEA NOT CLAIMED: no %s (claim it first, SKILL step A)' % claim)
    runs = regs['RUNS']
    if forward_only and kind != 'MONTH':
        raise Refused('--forward-only IS ONLY FOR MONTH')
    if kind == 'CLEAN':
        return plan_clean(run, seat, regs, items)
    # a variant counts while its job is queued or running, and when its stage ended rc 0; a failed one may run again (no extra try)
    done_kind = lambda k: {v for r in runs if r.get('kind') == k and r.get('idea') == idea for v in r.get('variants', '').split(',')
                           if v and stage_ok(run, r.get('receipts_rel'), v, k) is not False}
    sub = {'@@FROMJOB@@': from_job or '-', '@@PREREG_REL@@': '-', '@@PREREG_SHA@@': '-'}
    if kind == 'COUNT':
        pairs = [x.split('=', 1) for x in items.split(',') if x]
        if not pairs or any(len(p) != 2 for p in pairs):
            raise Refused('COUNT ITEMS ARE V=ideas/%s/defs/V.json[,V2=...]' % idea)
        if len(pairs) > 3:
            raise Refused('AT MOST 3 DEFINITIONS IN ONE COUNT JOB')
        vs, defs, shas = [], [], []
        for v, rel in pairs:
            if not NAME.match(v):
                raise Refused('BAD NAME %r: capitals and digits only, starting with a letter' % v)
            if not rel.startswith('ideas/%s/' % idea) or not SAFE.match(rel) or '..' in rel or not rel.endswith('.json'):
                raise Refused('DEFINITION MUST BE ideas/%s/...json: %r' % (idea, rel))
            p = os.path.join(run, rel)
            if not os.path.isfile(p):
                raise Refused('NO DEFINITION %s' % p)
            check_window(p, v)
            vs.append(v); defs.append(rel); shas.append(sha16(p))
        block = '\n'.join([bash_array('VS', vs), bash_array('DEFS', defs), bash_array('DSHAS', shas)])
        n = len(vs)
        sub.update({'@@WMB@@': str(300 * n), '@@MMB@@': '6000', '@@MINUTES@@': str(10 * n)})
        row = {'prereg_rel': '-', 'prereg_sha16': '-'}
        return seat, vs, block, sub, row
    vs = [v for v in items.split(',') if v]
    if not vs or len(vs) > 3 or len(set(vs)) != len(vs):
        raise Refused('ITEMS ARE 1 TO 3 DIFFERENT VARIANT NAMES')
    for v in vs:
        if not NAME.match(v):
            raise Refused('BAD NAME %r: capitals and digits only, starting with a letter' % v)
    var = {}
    for v in vs:
        r = latest(regs['VARIANTS'], idea=idea, V=v)
        if r is None:
            raise Refused('VARIANT %s OF %s NOT IN VARIANTS: register it before its job (SKILL step E)' % (v, idea))
        if r.get('lean') not in ('FADE', 'FOLLOW'):
            raise Refused('VARIANT %s LEAN %r: FADE or FOLLOW' % (v, r.get('lean')))
        for k in ('def_rel', 'prereg_rel'):
            if not SAFE.match(r.get(k, '')) or '..' in r.get(k, ''):
                raise Refused('VARIANT %s BAD PATH %s=%r' % (v, k, r.get(k)))
        for k, s in (('def_rel', 'def_sha16'), ('prereg_rel', 'prereg_sha16')):
            p = os.path.join(run, r[k])
            if not os.path.isfile(p):
                raise Refused('VARIANT %s: NO FILE %s' % (v, p))
            if sha16(p) != r.get(s):
                raise Refused('VARIANT %s: %s CHANGED SINCE VARIANTS (%s now %s): a sealed file never changes; a change is a new variant' % (v, r[k], r.get(s), sha16(p)))
        check_window(os.path.join(run, r['def_rel']), v)
        var[v] = r
    pre = {(var[v]['prereg_rel'], var[v]['prereg_sha16']) for v in vs}
    if len(pre) != 1:
        raise Refused('ONE PREREG A JOB: these variants name %s' % sorted(pre))
    prel, psha = pre.pop()
    sub.update({'@@PREREG_REL@@': prel, '@@PREREG_SHA@@': psha})
    row = {'prereg_rel': prel, 'prereg_sha16': psha}
    defs = [var[v]['def_rel'] for v in vs]; dshas = [var[v]['def_sha16'] for v in vs]; leans = [var[v]['lean'] for v in vs]
    if kind == 'GRADE':
        if from_job:
            raise Refused('GRADE TAKES NO --from-job')
        again = sorted(set(vs) & done_kind('GRADE'))
        if again:
            raise Refused('ALREADY GRADED %s: never re-run; a change is a new variant' % again)
        tries = done_kind('GRADE') | set(vs)
        if len(tries) > 3:
            raise Refused('TRY BUDGET: %d graded variants for %s (at most 3): %s' % (len(tries), idea, sorted(tries)))
        block = '\n'.join([bash_array('VS', vs), bash_array('DEFS', defs), bash_array('DSHAS', dshas), bash_array('LEANS', leans)])
        n = len(vs)
        sub.update({'@@WMB@@': str(1800 * n), '@@MMB@@': '2710' if n == 1 else '2931', '@@MINUTES@@': str(30 * n + 10)})   # SCOUT: MEM_MB = the measured peak + 20 percent: 1 variant 2253 MB (job 20265150), 2 or 3 variants 2442 MB (job 20265156: a variant's perfire beside the next variant's chain)
        return seat, vs, block, sub, row
    if not from_job or not re.match(r'^[0-9]+_GRADE_%s$' % idea, from_job):
        raise Refused('%s NEEDS --from-job <the GRADE job of %s, e.g. 20263700_GRADE_%s>' % (kind, idea, idea))
    gd, bad = receipts_done(run, from_job)
    if kind == 'ENTRY':
        again = sorted(set(vs) & done_kind('ENTRY'))
        if again:
            raise Refused('ALREADY ENTERED %s: never re-run' % again)
        card = os.path.join(run, 'ideas', idea, 'ALARM_CARD.md')
        if not os.path.isfile(card):
            raise Refused('NO ALARM CARD %s (the store registers it)' % card)
        fires = {}
        fp = os.path.join(gd, 'FIRES.tsv')
        if os.path.isfile(fp):
            for l in open(fp):
                x = l.rstrip('\n').split('\t')
                if len(x) == 4:
                    fires[x[0]] = x
        srcs, srcshas, total = [], [], 0
        mx = 0
        for v in vs:
            rr = os.path.join(gd, 'HANDOFF', 'REAL_SEALED', 'REAL_RULES_%s.tsv' % v)
            if not os.path.isfile(rr):
                raise Refused('NO HAND-OFF RULES FOR %s IN %s' % (v, from_job))
            rules = dict(l.rstrip('\n').split('\t')[:2] for l in open(rr) if '\t' in l and not l.startswith('#'))
            if rules.get('R1') != 'PASS':
                raise Refused('%s: HAND-OFF R1 IS %r, NOT PASS: no ENTRY job (decide it with decide_v1.py)' % (v, rules.get('R1')))
            if v not in fires:
                raise Refused('NO FIRE LIST FOR %s IN %s/FIRES.tsv' % (v, from_job))
            _, n, s, path = fires[v]
            if not path.startswith(os.path.join(CFG['JOB_SCRATCH'], 'work_%s' % os.path.basename(run), from_job) + os.sep):
                raise Refused('FIRE LIST OUTSIDE THE GRADE JOB: %s' % path)
            srcs.append(path); srcshas.append(s); k = int(n); total += k; mx = max(mx, k)
        block = '\n'.join([bash_array('VS', vs), bash_array('DEFS', defs), bash_array('DSHAS', dshas), bash_array('SRCS', srcs), bash_array('SRCSHAS', srcshas)])
        # measured 29 Oct 2026 (6 ENTRY receipts, W plus store places): 550 MB for 5,042 fires, 839 MB for 8,892; declared about 3 times
        wmb = sum(max(1000, 300 * int(math.ceil(int(fires[v][1]) / 1000.0))) for v in vs)
        mmb = 6000 if mx <= 5000 else 8000 if mx <= 10000 else 10000 if mx <= 17000 else 14000
        sub.update({'@@WMB@@': str(wmb), '@@MMB@@': str(mmb), '@@MINUTES@@': str(sum(5 + int(fires[v][1]) // 1000 for v in vs) + 2)})
        return seat, vs, block, sub, row
    if kind == 'MONTH':
        again = sorted(set(vs) & done_kind('MONTH'))
        if again:
            raise Refused('ALREADY MONTH-GRADED %s: never re-run' % again)
        fcfiles, fcshas, cases = [], [], []
        for v in vs:
            d = latest(regs['DECISIONS'], idea=idea, V=v)
            if forward_only:
                if d is not None:
                    raise Refused('%s: ALREADY DECIDED (%s): --forward-only is for the other side of a STOP, never graded itself' % (v, d.get('state')))
                m0 = re.match(r'^FORWARD ONLY OF ([A-Z][A-Z0-9]{0,23})(?![A-Z0-9])', var[v].get('reason', ''))
                if not m0:
                    raise Refused('%s: ITS VARIANTS REASON MUST START "FORWARD ONLY OF <V0>"' % v)
                v0 = m0.group(1)
                d0 = latest(regs['DECISIONS'], idea=idea, V=v0)
                if d0 is None or d0.get('state') != 'STOP':
                    raise Refused('%s: ITS PARENT %s IS NOT A STOP (latest %r)' % (v, v0, None if d0 is None else d0.get('state')))
                r0 = latest(regs['VARIANTS'], idea=idea, V=v0)
                if r0 is None or r0.get('def_sha16') != var[v].get('def_sha16') or r0.get('def_rel') != var[v].get('def_rel'):
                    raise Refused('%s: NOT THE SAME DEFINITION FILE AS %s' % (v, v0))
                if r0.get('lean') == var[v].get('lean'):
                    raise Refused('%s: SAME LEAN AS %s (%s): --forward-only takes the other side' % (v, v0, var[v].get('lean')))
                if d0.get('grade_job') != from_job:
                    raise Refused('%s: --from-job MUST BE %s (the grade of %s)' % (v, d0.get('grade_job'), v0))
            elif d is None or d.get('state') not in ('PASS', 'NEEDS MORE MONTHS'):
                raise Refused('%s: NO PASS OR NEEDS MORE MONTHS DECISION (latest %r): no forward months' % (v, None if d is None else d.get('state')))
            for mth in MONTHS:
                fr = latest(regs['FORECASTS'], idea=idea, V=v, scope=mth)
                if fr is None:
                    raise Refused('%s: NO SEALED FORECAST FOR %s IN FORECASTS (seal all of Jan-Apr first)' % (v, mth))
                rel = fr.get('file_rel', '')
                if not SAFE.match(rel) or '..' in rel or not os.path.isfile(os.path.join(run, rel)):
                    raise Refused('%s %s: FORECAST FILE MISSING %r' % (v, mth, rel))
                if sha16(os.path.join(run, rel)) != fr.get('file_sha16'):
                    raise Refused('%s %s: FORECAST FILE CHANGED SINCE SEALED (%s)' % (v, mth, rel))
                try:
                    lo1, hi1, lo2, hi2 = [float(fr[k]) for k in ('gap15_lo', 'gap15_hi', 'gap1h_lo', 'gap1h_hi')]
                except (KeyError, ValueError):
                    raise Refused('%s %s: FORECAST RANGES MUST BE NUMBERS (gap15_lo, gap15_hi, gap1h_lo, gap1h_hi)' % (v, mth))
                if not (lo1 <= hi1 and lo2 <= hi2):
                    raise Refused('%s %s: A FORECAST RANGE HAS LO ABOVE HI' % (v, mth))
                if rel not in fcfiles:
                    fcfiles.append(rel); fcshas.append(fr['file_sha16'])
                cases.append('  %s_%s) echo %s:%s,%s:%s;;' % (v, mth, '%g' % lo1, '%g' % hi1, '%g' % lo2, '%g' % hi2))
        rng = 'rng(){ case "$1_$2" in\n%s\n  *) echo NONE;;\nesac; }' % '\n'.join(cases)
        block = '\n'.join([bash_array('VS', vs), bash_array('DEFS', defs), bash_array('DSHAS', dshas), bash_array('LEANS', leans),
                           bash_array('FCFILES', fcfiles), bash_array('FCSHAS', fcshas), rng])
        n = len(vs)
        sub.update({'@@WMB@@': str(3000 * n), '@@MMB@@': '4030', '@@MINUTES@@': str(60 * n)})   # K16: MEM_MB = the measured peak + 20 percent (job 20264959 x1: a 2-part tree 3,355,115,520 bytes); was 8000
        return seat, vs, block, sub, row
    raise Refused('KIND %s' % kind)


def queued_names(seat):
    return {f for _, _, f in own_jobs(seat)}


def plan_clean(run, seat, regs, items):
    jobs = [j for j in items.split(',') if j]
    if not jobs or len(jobs) > 12 or len(set(jobs)) != len(jobs):
        raise Refused('CLEAN ITEMS ARE 1 TO 12 DIFFERENT JOBS (receipts names)')
    runs = regs['RUNS']
    byrec = {r.get('receipts_rel', '').replace('receipts/', '', 1): r for r in runs}
    inq = queued_names(seat)
    pending = {r.get('from_job') for r in runs if os.path.basename(r.get('job', '')) in inq}
    cleaning = {j for r in runs if r.get('kind') == 'CLEAN' and os.path.basename(r.get('job', '')) in inq for j in r.get('variants', '').split(',') if j}
    for j in jobs:
        if not JOBNAME.match(j):
            raise Refused('NOT A JOB OF THIS KIT: %r' % j)
        r = byrec.get(j)
        if r is None:
            raise Refused('%s IS NOT IN YOUR RUNS' % j)
        if j in cleaning:
            raise Refused('%s IS ALREADY IN A QUEUED CLEAN JOB' % j)
        if os.path.basename(r.get('job', '')) in inq:
            raise Refused('%s IS STILL QUEUED OR RUNNING' % j)
        d, bad = receipts_done(run, j)
        if not os.path.isfile(os.path.join(d, 'SHA16.txt')):
            raise Refused('%s HAS NO SHA16.txt: its proof is not complete' % j)
        if os.path.exists(os.path.join(d, 'CLEANED_BY.txt')):
            raise Refused('%s IS ALREADY CLEANED' % j)
        if j in pending:
            raise Refused('%s IS STILL NEEDED: a queued job reads it (--from-job)' % j)
        kind, idea = r.get('kind'), r.get('idea')
        vs = [v for v in r.get('variants', '').split(',') if v]
        if kind == 'GRADE':
            dec = {x.get('V') for x in regs['DECISIONS'] if x.get('idea') == idea and x.get('grade_job') == j}
            miss = [v for v in vs if v not in dec and stage_ok(run, r.get('receipts_rel'), v, 'GRADE') is not False]   # a failed variant gave nothing to decide
            if miss:
                raise Refused('%s: NOT DECIDED YET %s (decide_v1.py --write first)' % (j, miss))
        elif kind == 'ENTRY':
            dec = {x.get('V') for x in regs['DECISIONS'] if x.get('idea') == idea and x.get('entry_job') == j}
            miss = [v for v in vs if v not in dec and stage_ok(run, r.get('receipts_rel'), v, 'ENTRY') is not False]
            if miss:
                raise Refused('%s: NOT DECIDED YET %s (decide_v1.py --entry %s --write first)' % (j, miss, j))
        else:
            if not any(x.get('job') == j for x in regs['POSTMORTEMS']):
                raise Refused('%s: NO POSTMORTEMS ROW NAMES IT (read it first)' % j)
    sub = {'@@FROMJOB@@': '-', '@@PREREG_REL@@': '-', '@@PREREG_SHA@@': '-', '@@WMB@@': '10', '@@MMB@@': '1000', '@@MINUTES@@': '5'}
    return seat, jobs, 'JOBS=%s' % ','.join(jobs), sub, {'prereg_rel': '-', 'prereg_sha16': '-'}


def scratch_gone(run, d):
    """True when this machine sees SCRATCH_DISK (SCRATCH of --settings) and the scratch folder SCRATCH/work_<RUN>/<JOB> of the finished job
    whose receipts folder is d is not on it (a job's scratch W is named by its receipts name)"""
    w = CFG.get('WDB')
    return bool(w) and os.path.isdir(w) and not os.path.isdir(os.path.join(w, 'work_%s' % os.path.basename(run.rstrip('/')),
                                                                       os.path.basename(d.rstrip('/'))))


def scratch_used(run, regs=None):
    """MB of this run's own scratch on SCRATCH_DISK: measured (receipts DISK.tsv and STORE_PLACES.tsv) for finished jobs whose scratch folder
    is still there (none for one DSK swept; counted when SCRATCH_DISK is not visible from here), declared for the others"""
    runs = read_reg(run, 'RUNS') if regs is None else regs['RUNS']
    used = 0
    for r in runs:
        if r.get('kind') not in WORK:
            continue
        d = os.path.join(run, r.get('receipts_rel', ''))
        if os.path.exists(os.path.join(d, 'CLEANED_BY.txt')):
            continue
        dk = os.path.join(d, 'DISK.tsv')
        if os.path.isfile(dk):
            if scratch_gone(run, d):
                continue      # its scratch folder is no longer on SCRATCH_DISK (DSK's sweep; the owner 31 Oct 2026 10:51 Berlin): it holds nothing
            mb = 0
            for l in open(dk):
                x = l.rstrip('\n').split('\t')
                if x[0] == 'du_mb_W' and len(x) > 1 and x[1].isdigit():
                    mb += int(x[1])
            if os.path.isdir(d):
                for v in os.listdir(d):
                    sp = os.path.join(d, v, 'STORE_PLACES.tsv')
                    if os.path.isfile(sp):
                        for l in open(sp):
                            x = l.rstrip('\n').split('\t')
                            if x[0] == 'du_mb' and len(x) > 1 and x[1].isdigit():
                                mb += int(x[1])
            used += mb
        else:
            try:
                used += int(r.get('writes_mb', '0'))
            except ValueError:
                pass
    return used


def pick_queue(seat, q, behind, kind='GRADE'):
    mine = own_jobs(seat)
    limit = 3 if behind else 2
    if kind != 'CLEAN' and len(mine) >= limit:
        raise Refused('JOB BUDGET: you have %d jobs in IN or RUN (%s); at most 2, or a 3rd waiting with --behind' % (len(mine), ', '.join('%s/%s/%s' % x for x in mine)))
    cands = [q] if q else CFG['QUEUES']
    for c in cands:
        if c not in CFG['QUEUES']:
            raise Refused('QUEUE %s: use one of Q_V1..Q_V21' % c)
        if not os.path.isdir(os.path.join(CFG['RUNNER'], c, 'IN')):
            if q:
                raise Refused('NO QUEUE %s' % c)
            continue
        js = jobs_in(c)
        if behind:                                  # --behind waits behind your own job, never in an empty queue (AD2 29 Oct 17:02Z)
            if js and all('_judge_%s_' % seat in f for _, f in js):
                return c
        elif not js:
            return c
        if q:
            raise Refused('%s QUEUE %s: %s' % ('NOT ONLY YOUR JOBS IN' if behind and js else 'NO JOB OF YOURS TO WAIT BEHIND IN' if behind else 'BUSY', c, ', '.join('%s/%s' % x for x in js)))
    raise Refused('NO QUEUE HOLDING ONLY YOUR JOBS FOR --behind' if behind else 'NO EMPTY QUEUE IN Q_V1..Q_V21')


def main(argv):
    a = list(argv)
    flags = {'--behind': False, '--dry': False, '--forward-only': False}
    for k in list(flags):
        if k in a:
            flags[k] = True; a.remove(k)
    opts = {'--queue': None, '--from-job': None, '--settings': None, '--job-settings': None}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % k)
            opts[k] = a[i + 1]; del a[i:i + 2]
    if opts['--settings'] is None:
        raise Refused('--settings <file> IS REQUIRED: the settings file of this machine, e.g. settings/SETTINGS_<MACHINE>.env (CLEAN_RELEASE_V1 section 6)')
    if len(a) != 4:
        raise Refused('USAGE queue_job_v8.py --settings FILE [--job-settings FILE] RUN KIND IDEA ITEMS [--queue Q_Vn] [--from-job JOB] [--behind] [--forward-only] [--dry]')
    runtag, kind, idea, items = a
    if not RUNTAG.match(runtag):
        raise Refused('BAD RUN TAG %r (e.g. AD1_20261029)' % runtag)
    if kind == 'CLEAN':
        raise Refused(CLEAN_REMOVED)
    if kind not in KINDS:
        raise Refused('KIND %r: one of %s' % (kind, ', '.join(KINDS)))
    if kind not in TEMPLATE_SHA:
        raise Refused('NOT CLEAN YET: %s (no V6 template pinned for it in this queue)' % kind)
    if not NAME.match(idea):
        raise Refused('BAD IDEA NAME %r: capitals and digits only, starting with a letter' % idea)
    paths = use_settings(opts['--settings'], opts['--job-settings'])
    run = os.path.join(CFG['H'], 'runs', runtag)
    if not os.path.isdir(run):
        raise Refused('NO RUN FOLDER %s' % run)
    seat, vs, block, sub, row = plan(run, kind, idea, items, opts['--from-job'], flags['--forward-only'])
    tpl = os.path.join(CFG['KIT'], 'jobs', TEMPLATE_NAME[kind])
    if not os.path.isfile(tpl):
        raise Refused('NO TEMPLATE %s' % tpl)
    tsha = sha16(tpl)
    if tsha != TEMPLATE_SHA[kind]:
        raise Refused('TEMPLATE CHANGED %s (%s, kit says %s)' % (tpl, tsha, TEMPLATE_SHA[kind]))
    wmb = int(sub['@@WMB@@'])
    if kind != 'CLEAN':
        fm = free_mb()
        if fm is None:
            print('NOTE: SCRATCH_DISK is not visible here; the job checks the 60 GB floor itself when it starts. Read hb/DSK.txt.')
        elif fm < CFG['MIN_FREE_MB'] + wmb:
            raise Refused('DISK: SCRATCH_DISK free %d MB is under %d + this job\'s %d MB; read hb/DSK.txt and wait' % (fm, CFG['MIN_FREE_MB'], wmb))
        used = scratch_used(run)
        if used + wmb > CFG['RUN_BUDGET_MB']:
            raise Refused('DISK BUDGET: your run holds %d MB of scratch on SCRATCH_DISK; with this job\'s %d MB it would pass %d MB: scratch cleanup is done by DSK (the owner 31 Oct 2026 10:51 Berlin): ask DSK on the board (hb/DSK.txt) and wait for its sweep' % (used, wmb, CFG['RUN_BUDGET_MB']))
    q = pick_queue(seat, opts['--queue'], flags['--behind'], kind)
    if not os.path.isfile(CFG['REG']) or sha16(CFG['REG']) != CFG['REG_SHA']:
        raise Refused('reg_append_v1.py MISSING OR CHANGED %s' % CFG['REG'])
    sub.update({'@@SEAT@@': seat, '@@RUNTAG@@': runtag, '@@IDEA@@': idea, '@@QNAME@@': q, '@@ITEMS_BLOCK@@': block,
                '@@ITEMS_LIST@@': '/'.join(vs), '@@TPLSHA@@': tsha})
    body0 = open(tpl).read()

    def fill(num):
        b = body0.replace('@@JOBNUM@@', num)
        for k, v in sub.items():
            b = b.replace(k, v)
        f = b
        for k, v in paths.items():                   # the settings' paths last: checked plain by use_settings, they are no command
            f = f.replace(k, v)
        left = sorted(set(TOKEN.findall(f)))
        if left:
            raise Refused('PLACEHOLDERS LEFT %s' % left)
        w = WORDS.search(b)
        if w:
            raise Refused('REFUSED WORD %r IN THE FILLED JOB' % w.group(0))
        return f

    if flags['--dry']:
        b = fill('0')
        r = subprocess.run(['bash', '-n'], input=b, capture_output=True, text=True)    # from its input: a dry run writes no file
        if r.returncode:
            raise Refused('BASH -n FAILED %s' % r.stderr.strip())
        print(b)
        print('DRY RUN OK: %s %s %s %s on %s; WRITES_MB %s, MEM_MB %s; nothing claimed or queued' % (runtag, kind, idea, '/'.join(vs), q, sub['@@WMB@@'], sub['@@MMB@@']))
        return 0
    fill('0')                                    # all checks pass before a number is claimed
    r = subprocess.run(CFG['ALLOC'] + ['claim', seat, '1'], capture_output=True, text=True)
    ids = [x for x in r.stdout.split() if x.isdigit()]
    if r.returncode or len(ids) != 1:
        raise Refused('ALLOCATOR FAILED rc %d: %s %s' % (r.returncode, r.stdout.strip(), r.stderr.strip()))
    n = ids[0]
    body = fill(n)
    name = '%s_judge_%s_%s_%s.job.sh' % (n, seat, kind, idea)
    jd = os.path.join(run, 'jobs')
    os.makedirs(jd, exist_ok=True)
    twin = os.path.join(jd, name)
    with open(twin, 'x') as f:
        f.write(body)
    b = subprocess.run(['bash', '-n', twin], capture_output=True, text=True)
    if b.returncode:
        raise Refused('BASH -n FAILED (twin kept, nothing queued, number %s unused): %s' % (n, b.stderr.strip()))
    js = sha16(twin)
    fields = dict(row)
    fields.update({'job': os.path.relpath(twin, run), 'job_sha16': js, 'kind': kind, 'idea': idea, 'variants': ','.join(vs), 'queue': q,
                   'writes_mb': sub['@@WMB@@'], 'mem_mb': sub['@@MMB@@'], 'minutes': sub['@@MINUTES@@'], 'template_sha16': tsha,
                   'from_job': opts['--from-job'] or '-', 'receipts_rel': 'receipts/%s_%s_%s' % (n, kind, idea)})
    rr = subprocess.run([sys.executable, '-B', CFG['REG'], run, 'RUNS', '-'], input=json.dumps(fields), capture_output=True, text=True)
    if rr.returncode != 0 or 'RUNS' not in rr.stdout:
        raise Refused('RUNS ROW FAILED, NOTHING QUEUED (twin kept at %s, number %s unused): rc %d %s %s' % (twin, n, rr.returncode, rr.stdout.strip(), rr.stderr.strip()))
    dst = os.path.join(CFG['RUNNER'], q, 'IN', name)
    if os.path.exists(dst) or os.path.exists(dst + '.part'):
        raise Refused('IN EXISTS %s (RUNS row written; tell the lead)' % dst)
    with open(twin, 'rb') as f, open(dst + '.part', 'xb') as g:
        g.write(f.read())
    os.rename(dst + '.part', dst)
    print('QUEUED %s %s %s twin %s sha16 %s IN %s | RUNS %s' % (q, n, name, os.path.relpath(twin, run), js, sha16(dst), rr.stdout.strip()))
    print('NEXT: check every 5 min: ls %s/%s/RUN %s/%s/IN; done when receipts/%s_%s_%s/STAGES.tsv has its end line' % (CFG['RUNNER'], q, CFG['RUNNER'], q, n, kind, idea))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
