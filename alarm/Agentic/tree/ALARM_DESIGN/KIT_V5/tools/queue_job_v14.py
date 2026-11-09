#!/usr/bin/env python3
# queue_job_v14.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK; TEST, NOT REVIEWED): queue_job_v12.py 7530e9ee597c5bb1 (ALARM_V1_16) plus KIND FIRSTLOOK, nothing else: COUNT, GRADE, ENTRY and MONTH keep their templates, checks and sizes.
#   queue_job_v14.py --settings S <RUN> FIRSTLOOK <IDEA> <V> --from-job <GRADE job> [--month-job <MONTH job>] [--reader v11|v12] [--unsealed-source] [--dry]
# GPT HOLD 1 (09:57:42Z): a look's source is bound to its job, digest and period before anything is copied (fl_source); GRADE and MONTH on V14: V13 plus PERFIRE_SEAL.tsv. Edited by hand since make_editions_v1 (twins beside).
# ALARM_V1_19_1 (GPT HOLD d7f4868861ae2366): one read of the source carries its digest through the job; rows before the look's first day refused; a job that had a seal needs it, whatever the flag; the variant, definition and lean bound to the job's twin; --reader v11|v12, default in the settings, v12's chain builds its BAR tables.
# One variant, one job (JOB_FIRSTLOOK_V1): no --month-job = Sep-Dec only, best label NEEDS MORE MONTHS; with it = Sep-Apr. The reader is 06_First_look/FIRSTLOOK_SETTINGS_V1.json (a setting).
"""queue_job_v14.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md):
queue_job_v11.py plus three things, nothing else (same templates, MEM_MB, checks and job text):
  - NEXT: every refusal it knows (NEXT_HINTS) prints one more line, 'NEXT: <what to do>', after its REFUSED line (stderr).
  - --dry first prints the prerequisites as DRY CHECK lines, all of them, each OK or MISSING with its NEXT: the run folder and its
    registers, the claim file, for ENTRY the card, for MONTH the 4 FORECASTS rows (2601-2604) of each variant; any MISSING ends it with
    exit 2 before the rest. Then, as v11, every check and the filled job (now also without a run folder: it is a DRY CHECK line).
  - ENTRY: JOB_ENTRY_V7 reads ideas/<IDEA>/ALARM_CARD.md. When it is missing and the sealed card ideas/<IDEA>/CARD_<IDEA>.md exists,
    the queue copies the card byte for byte to ALARM_CARD.md (opened 'x') after every check passed and before it claims a number
    (--dry says it would); with neither file it refuses NO ALARM CARD as v11.
The usage line names v12. v11's text follows; where it says queue_job_v11 read queue_job_v14.
queue_job_v11.py (SCOUT, ALARM_V1_12, by make_v1_12_v1.py from queue_job_v10.py def6c938c345899d): the fixes templates JOB_COUNT_V7, JOB_GRADE_V13, JOB_ENTRY_V7, JOB_MONTH_V13 (each ends with its first failed stage's code; a FEED_GATE naming a
missing file stops at once; ENTRY reads its own chain folder) and MONTH's MEM_MB 3813 (job 20265358 m12 tree peak 3177 MB + 20 percent).
Nothing else. queue_job_v10.py (BUILD5, ALARM_V1_10; made by team/BUILD5/proposals/v1_10/jobs/make_jobs_v12.py from queue_job_v9.py 17ecac047554fc2a):
GRADE and MONTH on their V12 templates (chains v2_0_7 / v2_2_7: gm editions, evt1 store); nothing else. The text of queue_job_v9.py follows.
queue_job_v9.py (SCOUT for ALARM_DESIGN KIT_V5, 31 Oct 2026, V2_0 stage 2 D1; TEST, NOT REVIEWED): queue_job_v8.py 970df4adfac333e1 with
only GRADE on JOB_GRADE_V11 (81c9edda5ab18760: chain v2_0_6, ONE process from Outcomes to the reports, perfire and the hand-off from the kept
rows, 3 cores) and MONTH on JOB_MONTH_V11 (d5b2a44b8ed98e75: chain v2_2_6, the same, perfire from the kept rows), and GRADE's MEM_MB 2879 for 1
variant and 3000 for 2 or 3 (job 20265194: the measured tree peaks + 20 percent), MONTH's 3758 (job 20265289: its tree peak 3131 MB + 20
percent; DSK's review M1, team/DSK/notes/reviews/REVIEW_SCOUT_S2_D1_DSK.md 84f086e7ee1bba3b); team/SCOUT/D1_BUILD_PLAN_V1.md. The rest of this text is
queue_job_v8.py's, with its own name in the usage line and the refusals:
queue_job_v8.py (SCOUT for ALARM_DESIGN KIT_V5, 31 Oct 2026, V2_0 stage 1; TEST, NOT REVIEWED): queue_job_v7.py 5f9a50a3c5f525a7 with only GRADE
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

  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v11.py --settings <file> [--job-settings <file>] <RUN> <KIND> <IDEA> <ITEMS> [--queue Q_Vn] [--from-job <JOB>] [--behind] [--forward-only] [--dry]
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
import io
import csv, sys, os, re, json, hashlib, subprocess, datetime, math, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))


def _refused_at_start(msg):
    print('REFUSED: %s' % msg, file=sys.stderr)
    raise SystemExit(2)


def _settings_reader():
    """settings_v1 of the Alarm package that holds this file (this file sits at <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tools), loaded by
    its path, so the reader, its keys and its rule 'data lives outside this Alarm folder' are this package's own"""
    p = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..', '_tools', 'settings_v1.py'))
    if not os.path.isfile(p):
        _refused_at_start('NOT INSIDE AN ALARM PACKAGE: no %s (run queue_job_v11.py from the Alarm folder)' % p)
    spec = importlib.util.spec_from_file_location('settings_v1_of_queue_job_v9', p)
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
TEMPLATE_SHA = {'COUNT': 'ac237070224af425', 'GRADE': '8910f9ec0728be8b', 'MONTH': '09a83bf3ab337c3b',
                'ENTRY': 'aa3101178ff59030', 'FIRSTLOOK': '395f8aaf5a1f432c'}   # the templates (COUNT runs detect_v2 with --gate, 31 Oct; MONTH by SCOUT K4, 30 Oct; ENTRY,
# the store runner v11 and the grader rel1, by SCOUT K6, 31 Oct; GRADE V7: chain v2_0_2 with the grader rel1 and its relative pins, and
# MONTH V7: chain v2_2_2 with the aw1 rel1 editions and their relative pins, by SCOUT K12, 31 Oct, after round 7 found every V6 GRADE
# refused UNPINNED_MODULE; GRADE V8 and MONTH V8: chains v2_0_3 and v2_2_3, Outcomes with the gate from FEED_GATE and the research
# days from RESEARCH_STORE, SCOUT K12, 31 Oct; GRADE V9 and MONTH V9: chains v2_0_4 (Outcomes in 3 worker processes) and v2_2_4 (the
# detection parts by the chain's rule), 3 cores declared, one du at the end, SCOUT K16, 31 Oct); a KIND without one is NOT CLEAN YET
TEMPLATE_NAME = {'COUNT': 'JOB_COUNT_V7.job.sh.txt', 'GRADE': 'JOB_GRADE_V14.job.sh.txt',
                 'MONTH': 'JOB_MONTH_V14.job.sh.txt', 'ENTRY': 'JOB_ENTRY_V7.job.sh.txt', 'FIRSTLOOK': 'JOB_FIRSTLOOK_V1.job.sh.txt'}   # each KIND's template file in KIT_V5/jobs
KINDS = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'FIRSTLOOK')
CLEAN_REMOVED = "CLEAN REMOVED: the owner 31 Oct 2026 10:51 Berlin; scratch cleanup is DSK's, on the owner's word"   # SCOUT, 31 Oct 2026: KIND CLEAN is refused by name
WORK = ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'FIRSTLOOK')
JOBNAME = re.compile(r'^[0-9]+_(COUNT|GRADE|ENTRY|MONTH|FIRSTLOOK)_[A-Z][A-Z0-9]{0,23}$')
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
    need = ['store_' + v, 'markout_' + v] if kind == 'ENTRY' else ['receipt'] if kind == 'FIRSTLOOK' else ['grade_' + v]
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
        sub.update({'@@WMB@@': str(1800 * n), '@@MMB@@': '2879' if n == 1 else '3000', '@@MINUTES@@': str(30 * n + 10)})   # SCOUT: MEM_MB = the measured peak + 20 percent (V11, job 20265194); V10's: 1 variant 2253 MB (job 20265150), 2 or 3 variants 2442 MB (job 20265156)
        return seat, vs, block, sub, row
    if not from_job or not re.match(r'^[0-9]+_GRADE_%s$' % idea, from_job):
        raise Refused('%s NEEDS --from-job <the GRADE job of %s, e.g. 20263700_GRADE_%s>' % (kind, idea, idea))
    gd, bad = receipts_done(run, from_job)
    if kind == 'FIRSTLOOK':
        if len(vs) != 1:
            raise Refused('FIRSTLOOK TAKES ONE VARIANT, ONE JOB: %s' % vs)
        return plan_firstlook(run, idea, vs[0], var[vs[0]], from_job, runs, seat, row)
    if kind == 'ENTRY':
        again = sorted(set(vs) & done_kind('ENTRY'))
        if again:
            raise Refused('ALREADY ENTERED %s: never re-run' % again)
        card = os.path.join(run, 'ideas', idea, 'ALARM_CARD.md')
        if not os.path.isfile(card):
            sealed = os.path.join(run, 'ideas', idea, 'CARD_%s.md' % idea)
            if not os.path.isfile(sealed):
                raise Refused('NO ALARM CARD %s (the store registers it)' % card)
            CFG['CARD_COPY'] = (sealed, card)          # v12: copied after every check, before the number is claimed
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
        sub.update({'@@WMB@@': str(3000 * n), '@@MMB@@': '3813', '@@MINUTES@@': str(60 * n)})   # D1 (DSK M1): MEM_MB = the measured tree peak + 20 percent (job 20265205 m11: 3102 MB, PEAK_m11.txt); V10's 4030 (job 20264959)
        return seat, vs, block, sub, row
    raise Refused('KIND %s' % kind)


FL_SETTINGS_REL = os.path.join('06_First_look', 'FIRSTLOOK_SETTINGS_V1.json')
FL_TOOLS = ('lists', 'outcomes', 'export', 'extract', 'profile', 'busy', 'receipt', 'outcome_settings', 'costs')   # what the chain runs; the reader is apart so an edition can swap in
FL_V_MAX = 20                # G_<V>, H_<V> and FLR<V> must stay subject names of the tools (at most 24 characters)
FL_MEM_MB = 2448        # job 20266489: tree peak 2040 MB (profile, 47962 fires) + 20 percent
FL_LABEL = re.compile(r'^[A-Z][A-Z0-9_]*$'); FL_FILE = re.compile(r'^[A-Za-z0-9_]+\.tsv$'); FL_ARG = re.compile(r'^[A-Za-z0-9_.=-]+$')


def fl_settings():
    """the package's first look table: which reader (a setting, so an edition 12 swaps in here alone), the tools and pins with their sha16s, the months; every file checked here"""
    p = os.path.join(ALARM, FL_SETTINGS_REL)
    bad = lambda why: Refused('FIRSTLOOK SETTINGS %s: %s' % (p, why))
    try:
        s = json.load(open(p))
    except (OSError, ValueError) as e:
        raise bad(e)
    for k in ('tools', 'readers', 'default_reader', 'pins', 'labels', 'months'):
        if k not in s:
            raise bad('no %s' % k)
    name = CFG.get('READER') or s['default_reader']
    if name not in s['readers']:
        raise Refused('READER %r: one of %s' % (name, ', '.join(sorted(s['readers']))))
    if set(s['tools']) != set(FL_TOOLS):
        raise bad('tools must be exactly %s' % ', '.join(FL_TOOLS))

    def file_ok(e, under=None):
        rel, sha = e.get('rel', ''), e.get('sha16', '')
        if not SAFE.match(rel) or '..' in rel or rel.startswith('/') or (under and not rel.startswith(under)):
            raise bad('bad path %r' % rel)
        f = os.path.join(ALARM, rel)
        if not os.path.isfile(f) or sha16(f) != sha:
            raise bad('%s is not %s' % (rel, sha))
    for e in list(s['tools'].values()) + list(s['pins']):
        file_ok(e)
    for r in s['readers'].values():
        file_ok(r, os.path.join('06_First_look', ''))
        for e in r.get('pins', []) + ([r['bar_tool']] if r.get('bar_tool') else []):
            file_ok(e)
        if not FL_FILE.match(r.get('rule_file', '')) or not FL_LABEL.match(r.get('label_column', '')):
            raise bad('reader rule_file or label_column')
        if not isinstance(r.get('extra_args', []), list) or not all(FL_ARG.match(str(a)) for a in r.get('extra_args', [])):
            raise bad('reader extra_args')
    s['reader'] = dict(s['readers'][name], name=name)
    m = s['months']
    if not all(re.fullmatch(r'[0-9]{8}', m.get(k, '')) for k in ('run_first', 'first', 'design_last', 'full_last')) or m['full_last'] > '20260430' or m['design_last'] > m['full_last']:
        raise bad('months: Sep 2025 to Apr 2026 only')
    if not all(re.fullmatch(r'[A-Z0-9_]+', x) for x in s['labels']):
        raise bad('labels')
    return s


def fl_stages_ok(run, job, v, months=False):
    """the job's own stages for v each ended rc 0; for a MONTH job each sealed month too"""
    p = os.path.join(run, 'receipts', job, 'STAGES.tsv')
    rows = [l.rstrip('\n').split('\t') for l in open(p) if l.strip()][1:]
    need = ['grade_' + v, 'perfire_' + v, 'perfire_test_' + v] + (['month_%s_%s' % (v, m) for m in MONTHS] if months else [])
    return all(any(x[0] == n and len(x) > 1 and x[1] == '0' for x in rows) for n in need)


def fl_failed_stages(run, job, v, others):
    """a failed stage of the job counts unless it names another variant of the same job; an end with a failed code and no stage of another variant behind it counts too"""
    p = os.path.join(run, 'receipts', job, 'STAGES.tsv')
    rows = [l.rstrip('\n').split('\t') for l in open(p) if l.strip()][1:]
    bad = [x for x in rows if len(x) > 1 and x[1] != '0']; fails = [x for x in bad if x[0] != 'end']
    theirs = lambda n: any(re.search(r'_%s(_|$)' % re.escape(o), n) for o in others)
    mine = [x[0] for x in fails if not theirs(x[0])]
    if mine:
        raise Refused('FAILED STAGE %s IN %s: a look reads only a job whose stages for %s all ended 0' % (','.join(mine), job, v))
    if len(fails) < len(bad) and not fails:
        raise Refused('FAILED STAGE end IN %s: the job ended with a failed code and no stage says why' % job)


def fl_run_row(runs, run, kind, idea, v, job, var):
    """the source job's one RUNS row, its twin's bytes and its sealed variant: the job the queue itself launched for this variant -> the row"""
    rows = [r for r in runs if r.get('kind') == kind and r.get('idea') == idea and r.get('receipts_rel') == 'receipts/' + job]
    if len(rows) != 1:
        raise Refused('SOURCE NOT IN RUNS: %d %s rows of %s with receipts/%s; one expected' % (len(rows), kind, idea, job))
    r = rows[0]; twin = os.path.join(run, r.get('job', ''))
    if v not in r.get('variants', '').split(','):
        raise Refused('SOURCE JOB %s DID NOT RUN %s: variants %s' % (job, v, r.get('variants')))
    if r.get('prereg_sha16') != var.get('prereg_sha16') or r.get('prereg_rel') != var.get('prereg_rel'):
        raise Refused('SOURCE JOB %s: ANOTHER CARD THAN THE SEALED VARIANT %s' % (job, v))
    if not os.path.isfile(twin) or sha16(twin) != r.get('job_sha16'):
        raise Refused('SOURCE JOB %s: ITS TWIN %s IS NOT THE ONE QUEUED (%s)' % (job, r.get('job'), r.get('job_sha16')))
    with open(twin) as f:
        tw = f.read()
    arr = {}
    for n in ('VS', 'DEFS', 'DSHAS', 'LEANS'):
        m = re.search(r'^%s=\((.*)\)$' % n, tw, re.M); arr[n] = m.group(1).split() if m else None
    if not arr['VS'] or v not in arr['VS'] or arr['DSHAS'] is None or len(arr['DSHAS']) != len(arr['VS']):
        raise Refused('SOURCE JOB %s: ITS TWIN DOES NOT PIN THE SEALED DEFINITION OF %s (%s)' % (job, v, var.get('def_sha16')))
    i = arr['VS'].index(v)
    if arr['DSHAS'][i] != var.get('def_sha16') or arr['DEFS'] is None or len(arr['DEFS']) != len(arr['VS']) or arr['DEFS'][i] != var.get('def_rel'):
        raise Refused('SOURCE JOB %s: ITS TWIN DOES NOT PIN THE SEALED DEFINITION OF %s (%s)' % (job, v, var.get('def_sha16')))
    if arr['LEANS'] is None or len(arr['LEANS']) != len(arr['VS']) or arr['LEANS'][i] != var.get('lean'):
        raise Refused('SOURCE LEAN: JOB %s RAN %s WITH LEAN %s, ITS VARIANTS ROW SAYS %s: a grade supports the side it ran' % (job, v, arr['LEANS'][i] if arr['LEANS'] and len(arr['LEANS']) == len(arr['VS']) else 'NOT RECORDED', var.get('lean')))
    return r


def fl_seal_expected(run, job, v, row):
    """what says this job had a PERFIRE_SEAL: its registered template, its twin, its stages, its digest list -> the reasons; none for a job from before the seal"""
    d = os.path.join(run, 'receipts', job); why = []
    if row.get('template_sha16') in (TEMPLATE_SHA['GRADE'], TEMPLATE_SHA['MONTH']):
        why.append('its template %s writes one' % row.get('template_sha16'))
    twin = os.path.join(run, row.get('job', ''))
    if os.path.isfile(twin) and 'PERFIRE_SEAL' in open(twin).read():
        why.append('its twin writes one')
    with open(os.path.join(d, 'STAGES.tsv')) as f:
        if any(l.split('\t')[0] == 'perfire_seal_' + v for l in f):
            why.append('its stages name perfire_seal_' + v)
    if fl_sha_line(d, 'PERFIRE_SEAL.tsv'):
        why.append('its SHA16.txt lists one')
    return why


def fl_sha_line(d, name):
    """the sha16 SHA16.txt of a finished job records for a file, or None"""
    p = os.path.join(d, 'SHA16.txt')
    if not os.path.isfile(p):
        return None
    for l in open(p):
        x = l.split()
        if len(x) == 2 and x[1] == name:
            return x[0][:16]
    return None


def fl_scan(data, path):
    """the PERFIRE's identity and date columns only, of the bytes the digest came from, never an outcome -> {'A': set of (coin, t, side), 'nA', 'nR', 'first', 'last', 'rows'}"""
    with io.StringIO(data.decode()) as f:
        h = f.readline().rstrip('\n').split('\t')
        if not all(k in h for k in ('kind', 'coin', 't', 'side')):
            raise Refused('PERFIRE HAS NO kind, coin, t AND side COLUMNS %s' % path)
        ik, ic, it, iS = h.index('kind'), h.index('coin'), h.index('t'), h.index('side'); s = {'A': set(), 'nA': 0, 'nR': 0, 'first': None, 'last': None, 'rows': 0}
        for l in f:
            x = l.rstrip('\n').split('\t')
            if len(x) != len(h) or x[ik] not in ('A', 'R'):
                raise Refused('SOURCE KIND: a row of %s is neither A nor R (%r)' % (path, x[ik] if len(x) > ik else l[:40]))
            try:
                t = int(x[it])
            except ValueError:
                raise Refused('SOURCE TIME %r IN %s' % (x[it], path))
            s['rows'] += 1; s['n' + x[ik]] += 1; s['first'] = t if s['first'] is None else min(s['first'], t); s['last'] = t if s['last'] is None else max(s['last'], t)
            if x[ik] == 'A':
                s['A'].add((x[ic], t, x[iS]))
    return s


def fl_source(run, runtag, job, v, first, last, unsealed, row):
    """HOLD 1: the bytes a look would pin are the bytes this job wrote, every row inside its period, its fires its own fire list, all before a number is claimed or a byte copied, all from ONE read of the file -> (here, there, how authenticated, digest, bytes):
    SEALED (the job's PERFIRE_SEAL.tsv), RECEIPT_SHA16 (an older job's receipts copy listed in its SHA16.txt) or UNSEALED (a V13 job's scratch file: its counts against its log, only with --unsealed-source, and the page says so)"""
    d = os.path.join(run, 'receipts', job); here, there = fl_perfire(run, runtag, job, v); how = None
    with open(here, 'rb') as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()[:16]; s = fl_scan(data, here)
    sp = os.path.join(d, 'PERFIRE_SEAL.tsv'); name = 'PERFIRE_%s.tsv' % v
    if not os.path.isfile(sp):
        lost = fl_seal_expected(run, job, v, row)
        if lost:
            raise Refused('SOURCE SEAL LOST FOR %s IN %s: %s; --unsealed-source is only for a job that never had one' % (v, job, '; '.join(lost)))
    if os.path.isfile(sp):
        if fl_sha_line(d, 'PERFIRE_SEAL.tsv') != sha16(sp):
            raise Refused('SOURCE SEAL %s IS NOT THE ONE ITS JOB RECORDED IN SHA16.txt' % sp)
        rows = [l.rstrip('\n').split('\t') for l in open(sp) if l.strip()]; mine = [x for x in rows if x[0] == v]
        if len(mine) != 1 or len(mine[0]) != 8 or mine[0][7] != job:
            raise Refused('SOURCE SEAL %s: %d ROWS OF %s FROM THIS JOB; one expected' % (sp, len(mine), v))
        x = mine[0]
        if x[1] != sha:
            raise Refused('SOURCE DIGEST %s IS %s; ITS JOB SEALED %s' % (here, sha, x[1]))
        if x[2:7] != [str(s['nA']), str(s['nR']), str(s['first']), str(s['last']), str(s['rows'])]:
            raise Refused('SOURCE SEAL %s: SCOPE %s DIFFERS FROM THE FILE' % (sp, x[2:7]))
        how = 'SEALED'
    elif fl_sha_line(d, name):
        if fl_sha_line(d, name) != sha:
            raise Refused('SOURCE DIGEST %s IS %s; ITS JOB RECORDED %s' % (here, sha, fl_sha_line(d, name)))
        how = 'RECEIPT_SHA16'
    elif not unsealed:
        raise Refused('NO SOURCE SEAL FOR %s IN %s: a job from before GRADE and MONTH V14 keeps no digest of its PERFIRE' % (v, job))
    else:
        lp = os.path.join(d, 'perfire_%s.log' % v); m0 = None
        if os.path.isfile(lp):
            for l in open(lp):
                m0 = re.match(r'^WROTE (\S+) (\d+) alarm rows (\d+) random rows', l) or m0
        if not m0 or not m0.group(1).endswith(os.path.join(job, name)) or (int(m0.group(2)), int(m0.group(3))) != (s['nA'], s['nR']):
            raise Refused('SOURCE LOG %s DOES NOT NAME THIS FILE WITH %d FIRES AND %d RANDOM ROWS' % (lp, s['nA'], s['nR']))
        how = 'UNSEALED'
    t0 = datetime.datetime.strptime(first, '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp(); t1 = datetime.datetime.strptime(last, '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp() + 86400
    if s['rows'] and (s['first'] < t0 or s['last'] >= t1):
        raise Refused('SOURCE ROW OUTSIDE THE PERIOD %s TO %s: %s holds t %d to %d; nothing copied' % (first, last, here, s['first'], s['last']))
    fn = '%s_FIRES_V1_LIST.tsv' % v; rec = None; fp = os.path.join(d, 'FIRES.tsv')
    if os.path.isfile(fp):
        for l in open(fp):
            x = l.rstrip('\n').split('\t')
            if len(x) == 4 and x[0] == v:
                rec = x[2]
    rec = rec or fl_sha_line(d, fn); here_l = os.path.join(d, fn) if os.path.isfile(os.path.join(d, fn)) else os.path.join(CFG['WDB'], 'work_%s' % runtag, job, fn)
    if how != 'SEALED' and not rec and not os.path.isfile(here_l):        # old MONTH jobs recorded no list and it may be swept: the page already says what is not authenticated
        return here, there, how, sha, data
    if (not rec and how == 'SEALED') or not os.path.isfile(here_l) or (rec and sha16(here_l) != rec):
        raise Refused('SOURCE FIRE LIST %s IS NOT THE ONE ITS JOB RECORDED (%s)' % (here_l, rec))
    with open(here_l) as f:
        want = {(x['coin'], int(x['t']), x['side']) for x in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')}
    if want != s['A']:
        raise Refused('SOURCE FIRE LIST: %d FIRES IN THE PERFIRE, %d IN THE LIST, %d DIFFER' % (len(s['A']), len(want), len(s['A'] ^ want)))
    return here, there, how, sha, data


def fl_perfire(run, runtag, job, v):
    """(path here, path on the runner) of the job's PERFIRE: the receipts' copy (older templates), else the job's scratch: GRADE and MONTH keep it only there, and DSK's sweep removes it"""
    rc = os.path.join(run, 'receipts', job, 'PERFIRE_%s.tsv' % v)
    if os.path.isfile(rc) and os.path.isfile(os.path.join(CFG['WDB'], 'work_%s' % runtag, job, 'PERFIRE_%s.tsv' % v)) and sha16(rc) != sha16(os.path.join(CFG['WDB'], 'work_%s' % runtag, job, 'PERFIRE_%s.tsv' % v)):
        raise Refused('SOURCE TWO COPIES OF PERFIRE_%s OF %s DIFFER: receipts and scratch' % (v, job))
    if os.path.isfile(rc):
        return rc, '@@RESEARCH_ROOT@@/ALARM_DESIGN/runs/%s/receipts/%s/PERFIRE_%s.tsv' % (runtag, job, v)
    sc = os.path.join(CFG['WDB'], 'work_%s' % runtag, job, 'PERFIRE_%s.tsv' % v)
    if os.path.isfile(sc):
        return sc, '@@SCRATCH@@/work_%s/%s/PERFIRE_%s.tsv' % (runtag, job, v)
    raise Refused('NO PERFIRE FOR %s: not in receipts/%s and not in %s' % (v, job, sc))


def fl_fires(run, runtag, job, v):
    """the job's fire list as the runner sees it, or None"""
    d = os.path.join(run, 'receipts', job)
    if os.path.isfile(os.path.join(d, '%s_FIRES_V1_LIST.tsv' % v)):
        return '@@RESEARCH_ROOT@@/ALARM_DESIGN/runs/%s/receipts/%s/%s_FIRES_V1_LIST.tsv' % (runtag, job, v)
    if os.path.isfile(os.path.join(CFG['WDB'], 'work_%s' % runtag, job, '%s_FIRES_V1_LIST.tsv' % v)):
        return '@@SCRATCH@@/work_%s/%s/%s_FIRES_V1_LIST.tsv' % (runtag, job, v)
    return None


def fl_count(data, path, first, last):
    """fires and random rows of the PERFIRE's bytes inside the days first..last"""
    t0 = (datetime.datetime.strptime(first, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)).timestamp()
    t1 = (datetime.datetime.strptime(last, '%Y%m%d').replace(tzinfo=datetime.timezone.utc)).timestamp() + 86400
    with io.StringIO(data.decode()) as f:
        h = f.readline().rstrip('\n').split('\t')
        if not all(k in h for k in ('kind', 't')):
            raise Refused('PERFIRE HAS NO kind AND t COLUMNS %s' % path)
        ik, it = h.index('kind'), h.index('t'); n = {'A': 0, 'R': 0}
        for l in f:
            x = l.split('\t')
            if x[ik] in n and t0 <= int(x[it]) < t1:
                n[x[ik]] += 1
    return n['A'], n['R']


def fl_same_reader(run, r, rel):
    """did this earlier look run this reader? its twin says; edition 12 may run beside edition 11, never itself twice"""
    twin = os.path.join(run, r.get('job', ''))
    return not os.path.isfile(twin) or ('READER=$AL/' + rel) in open(twin).read()


def plan_firstlook(run, idea, v, var, grade, runs, seat, row):
    """KIND FIRSTLOOK: one variant after its GRADE; --month-job adds Jan-Apr. Without it the look stays on Sep-Dec, so no outcome of a sealed month is read"""
    runtag = os.path.basename(run.rstrip('/')); month = CFG.get('MONTH_JOB'); lean = var['lean']
    if len(v) > FL_V_MAX:
        raise Refused('NAME TOO LONG %s: at most %d characters for a first look (its subjects add a prefix)' % (v, FL_V_MAX))
    if not fl_stages_ok(run, grade, v):
        raise Refused('NO GOOD GRADE OF %s IN %s: grade_%s, perfire_%s and perfire_test_%s must each end rc 0' % (v, grade, v, v, v))
    gr = fl_run_row(runs, run, 'GRADE', idea, v, grade, var)
    fl_failed_stages(run, grade, v, [o for o in gr['variants'].split(',') if o != v])
    s = fl_settings(); m = s['months']
    if month:
        if not re.match(r'^[0-9]+_MONTH_%s$' % idea, month):
            raise Refused('--month-job MUST BE <the MONTH job of %s, e.g. 20263700_MONTH_%s>' % (idea, idea))
        receipts_done(run, month)
        if not fl_stages_ok(run, month, v, True):
            raise Refused('NO GOOD MONTH OF %s IN %s: grade_%s, perfire_%s, perfire_test_%s and month_%s_2601 to 2604 must each end rc 0' % (v, month, v, v, v, v))
        mr = fl_run_row(runs, run, 'MONTH', idea, v, month, var)
        if mr.get('from_job') != grade:
            raise Refused('SOURCE MONTH %s CAME FROM %s, NOT FROM %s' % (month, mr.get('from_job'), grade))
        fl_failed_stages(run, month, v, [o for o in mr['variants'].split(',') if o != v])
    srow = mr if month else gr
    src = month or grade; mode = 'FULL' if month else 'SEPDEC'; last = m['full_last'] if month else m['design_last']
    if any(r.get('kind') == 'FIRSTLOOK' and r.get('idea') == idea and v in r.get('variants', '').split(',') and r.get('from_job') == src
           and stage_ok(run, r.get('receipts_rel'), v, 'FIRSTLOOK') is not False and fl_same_reader(run, r, s['reader']['rel']) for r in runs):
        raise Refused('ALREADY LOOKED %s FROM %s WITH READER %s: never re-run' % (v, src, s['reader']['name']))
    here, there, how, pfsha, pfdata = fl_source(run, runtag, src, v, m['first'], last, CFG.get('UNSEALED'), srow)
    nA, nR = fl_count(pfdata, here, m['first'], last)
    if not nA or not nR:
        raise Refused('PERFIRE HAS %d FIRES AND %d RANDOM ROWS IN %s TO %s: %s' % (nA, nR, m['first'], last, here))
    fires = fl_fires(run, runtag, src, v)
    r = s['reader']; bt = r.get('bar_tool')
    pins = ['ck $AL/%s %s' % (e['rel'], e['sha16']) for e in list(s['tools'].values()) + [r] + list(s['pins']) + r.get('pins', []) + ([bt] if bt else [])]
    # measured: outcomes + export 25 ms an event, the profile twice 8.5 ms a fire (jobs 20264242, 20264288)
    mins = 15 + int((nA + nR) * 0.025 / 60) + int(nA * 0.0085 / 60) + (2 if bt else 0)
    sub = {'@@FROMJOB@@': src, '@@PREREG_REL@@': row['prereg_rel'], '@@PREREG_SHA@@': row['prereg_sha16'], '@@WMB@@': str(1000 + (nA + nR) // 15), '@@MMB@@': str(max(FL_MEM_MB, int(r.get('mem_mb', 0)))), '@@MINUTES@@': str(mins),
           '@@LEAN@@': lean, '@@MODE@@': mode, '@@FIRST@@': m['first'], '@@LAST@@': last, '@@RWIN@@': '%s:%s' % (m['run_first'], last),
           '@@PFSRC@@': there, '@@PFSHA@@': pfsha, '@@SRCAUTH@@': how, '@@FIRESARG@@': ('--fires ' + fires) if fires else '', '@@LF@@': ','.join(s['labels']),
           '@@PINS@@': '\n'.join(pins), '@@READER@@': s['reader']['rel'], '@@READER_EXTRA@@': ' '.join([str(a) for a in r.get('extra_args', [])] + (['--bar', '$DV/BAR'] if bt else [])),
           '@@BAR_STAGE@@': ('one bar nice -n 10 $PY -B $AL/%s build $LAB $CODE $FIRST $LAST $DV/BAR $LA=A_$C $LR=R_$C' % bt['rel']) if bt else '',
           '@@RULE_FILE@@': s['reader']['rule_file'], '@@LABEL_COL@@': s['reader']['label_column']}
    for k, e in s['tools'].items():
        sub['@@T_%s@@' % k.upper()] = e['rel']
    if mins >= 60:
        print('NOTE: OVER 60 DECLARED MINUTES (%d): %d fires and %d random rows; one job cannot be split yet: tell SCOUT on the board' % (mins, nA, nR))
    return seat, [v], bash_array('VS', [v]), sub, dict(row, from_job=src)


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


NEXT_HINTS = (    # v12: (the start of a refusal, what to do next)
    ('NO RUN FOLDER', 'start it: cp -R -n <INSTALL>/Agentic/tree/ALARM_DESIGN/KIT_V5/runs/TEMPLATE_V4 <that folder> (AGENTS.md, The folder)'),
    ('NO REGISTER', 'your run folder lacks registers/: start it from KIT_V5/runs/TEMPLATE_V4 (cp -R -n), never by hand'),
    ('IDEA NOT CLAIMED', 'claim it: cp -n a one-line text to RESEARCH_ROOT/ALARM_DESIGN/runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt (AGENTS.md step 2)'),
    ('NO ALARM CARD', 'seal your card first as ideas/<IDEA>/CARD_<IDEA>.md (CARD_V7.md, step 5b); the queue copies it to ALARM_CARD.md'),
    ('NO SEALED FORECAST', 'add 4 FORECASTS rows (scope 2601, 2602, 2603, 2604) per variant with reg_append_v1.py: file_rel, file_sha16 of your forecast file and gap15_lo, gap15_hi, gap1h_lo, gap1h_hi (numbers)'),
    ('FORECAST FILE', 'the forecast file must exist unchanged since its FORECASTS rows; a change is a new row with the new sha16'),
    ('NO PASS OR NEEDS MORE MONTHS', 'decide the variant first: decide_v3.py S <RUN> <IDEA> <V> --grade <GRADE job> --write'),
    ('NOT IN VARIANTS', 'seal the variant: one VARIANTS row with reg_append_v1.py (def_rel, def_sha16, prereg_rel = your card, prereg_sha16)'),
    ('NO HAND-OFF RULES', 'ENTRY needs the GRADE job finished with its hand-off: wait for its STAGES.tsv end line'),
    ('NO PERFIRE', 'GRADE and MONTH keep PERFIRE_<V>.tsv only in the job scratch, and DSK sweeps it: ask DSK on the board (hb/DSK.txt) whether a copy is kept; without it this variant has no first look until SCOUT rebuilds its PERFIRE; never write one by hand'),
    ('NO GOOD GRADE', 'the GRADE job failed for this variant: read its STAGES.tsv; a failed variant may run GRADE again'),
    ('NO GOOD MONTH', 'the MONTH job failed for this variant or a month: read its STAGES.tsv; a look needs all four months'),
    ('FAILED STAGE', 'read the job\'s STAGES.tsv; a look reads only a job that finished clean for this variant'),
    ('SOURCE SEAL LOST', 'this job had a seal and it is gone: --unsealed-source does not apply: never rewrite it; write a PROBLEMS row and tell SCOUT'),
    ('SOURCE LEAN', 'the grade ran another side than the newest VARIANTS row: a side needs its own variant and its own GRADE (cards/first_look.md); an unsigned SIZE idea: playbook/ALARM_GOALS_V1.md'),
    ('READER ', 'name a reader in 06_First_look/FIRSTLOOK_SETTINGS_V1.json, block readers: v11 is the default, v12 prints RULE_12 and RULE_9 side by side'),
    ('NO SOURCE SEAL', 'an old job: add --unsealed-source to accept the file as it is now; its counts are checked against the job\'s log, and FIRST_LOOK.md says the source is not authenticated'),
    ('OUTSIDE THE PERIOD', 'this source holds rows the look may not read: never edit a PERFIRE; tell SCOUT on the board, with the job'),
    ('SOURCE', 'the PERFIRE, its fire list or its job is not what the job left: never edit or rewrite them; write a PROBLEMS row and tell SCOUT on the board'),
    ('NO RECEIPTS', 'name a finished job of this idea: ls RESEARCH_ROOT/ALARM_DESIGN/runs/<RUN>/receipts'),
    ('NOT FINISHED', 'wait for the end line of its STAGES.tsv'),
    ('FIRSTLOOK SETTINGS', 'the release is broken: 06_First_look/FIRSTLOOK_SETTINGS_V1.json names a file that is missing or changed: write a PROBLEMS row and tell SCOUT'),
    ('DISK BUDGET', 'ask DSK on the board (hb/DSK.txt) and wait for its sweep; never delete'),
    ('DISK: SCRATCH_DISK', 'ask DSK on the board (hb/DSK.txt) and wait for its sweep; never delete'),
)


def next_hint(msg):
    """v12: the NEXT line for a refusal message, or None"""
    for start, what in NEXT_HINTS:
        if start in msg:
            return what
    return None


def fl_dry(run, runtag, items):
    """the first look's prerequisites for --dry: the job's receipts, the PERFIRE, the reader"""
    out = []; v = items.split(',')[0]; src = CFG.get('MONTH_JOB') or CFG.get('FROM_JOB') or ''
    p = os.path.join(run, 'receipts', src, 'STAGES.tsv')
    out.append(('grade receipts', bool(src) and os.path.isfile(p), p if src and os.path.isfile(p) else 'JOB %s HAS NO RECEIPTS YET (%s)' % (src or '--from-job', p)))
    try:
        out.append(('perfire', True, fl_perfire(run, runtag, src, v)[0]))
    except Refused as e:
        out.append(('perfire', False, str(e)))
    try:
        s = fl_settings(); out.append(('reader', True, '%s %s' % (s['reader']['rel'], s['reader']['sha16'])))
    except Refused as e:
        out.append(('reader', False, str(e)))
    return out


def dry_checks(runtag, kind, idea, items):
    """v12 --dry: the prerequisites, all of them -> [(check, ok, detail)]; reads only, never refuses"""
    run = os.path.join(CFG['H'], 'runs', runtag)
    out = [('run folder', os.path.isdir(run), run if os.path.isdir(run) else 'NO RUN FOLDER %s' % run)]
    regd = os.path.join(run, 'registers')
    miss = [n for n in REGISTERS if not os.path.isfile(os.path.join(regd, n + '.tsv'))]
    out.append(('registers', not miss, ('NO REGISTER %s' % ', '.join(miss)) if miss else regd))
    claim = os.path.join(CFG['H'], 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (runtag, idea))
    out.append(('claim', os.path.isfile(claim), claim if os.path.isfile(claim) else 'IDEA NOT CLAIMED: no %s' % claim))
    if kind == 'ENTRY':
        a = os.path.join(run, 'ideas', idea, 'ALARM_CARD.md'); c = os.path.join(run, 'ideas', idea, 'CARD_%s.md' % idea)
        ok = os.path.isfile(a) or os.path.isfile(c)
        out.append(('card', ok, a if os.path.isfile(a) else (c + ' (copied to ALARM_CARD.md when queued)') if ok else 'NO ALARM CARD %s nor %s' % (a, c)))
    if kind == 'FIRSTLOOK':
        out += fl_dry(run, runtag, items)
    if kind == 'MONTH':
        try:
            rows = read_reg(run, 'FORECASTS')
        except Refused:
            rows = []
        for v in [x for x in items.split(',') if x]:
            have = [m for m in MONTHS if latest(rows, idea=idea, V=v, scope=m)]
            lack = [m for m in MONTHS if m not in have]
            out.append(('forecasts %s' % v, not lack, ('4 rows %s' % ','.join(have)) if not lack else
                        'NO SEALED FORECAST FOR %s IN FORECASTS (rows needed: %s)' % (v, ','.join(lack))))
    return out


def main(argv):
    a = list(argv)
    flags = {'--behind': False, '--dry': False, '--forward-only': False, '--unsealed-source': False}
    for k in list(flags):
        if k in a:
            flags[k] = True; a.remove(k)
    opts = {'--queue': None, '--from-job': None, '--month-job': None, '--reader': None, '--settings': None, '--job-settings': None}
    for k in list(opts):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % k)
            opts[k] = a[i + 1]; del a[i:i + 2]
    if opts['--settings'] is None:
        raise Refused('--settings <file> IS REQUIRED: the settings file of this machine, e.g. settings/SETTINGS_<MACHINE>.env (CLEAN_RELEASE_V1 section 6)')
    if len(a) != 4:
        raise Refused('USAGE queue_job_v14.py --settings FILE [--job-settings FILE] RUN KIND IDEA ITEMS [--queue Q_Vn] [--from-job JOB] [--month-job JOB] [--reader v11|v12] [--unsealed-source] [--behind] [--forward-only] [--dry]')
    runtag, kind, idea, items = a
    if opts['--month-job'] and kind != 'FIRSTLOOK':
        raise Refused('--month-job IS ONLY FOR FIRSTLOOK')
    if flags['--unsealed-source'] and kind != 'FIRSTLOOK':
        raise Refused('--unsealed-source IS ONLY FOR FIRSTLOOK')
    if opts['--reader'] and kind != 'FIRSTLOOK':
        raise Refused('--reader IS ONLY FOR FIRSTLOOK')
    CFG['READER'] = opts['--reader']
    CFG['MONTH_JOB'] = opts['--month-job']; CFG['FROM_JOB'] = opts['--from-job']; CFG['UNSEALED'] = flags['--unsealed-source']
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
    if flags['--dry']:
        bad = 0
        for name, ok, detail in dry_checks(runtag, kind, idea, items):
            print('DRY CHECK %s: %s %s' % (name, 'OK' if ok else 'MISSING', detail))
            if not ok:
                bad += 1
                h = next_hint(detail)
                if h:
                    print('  NEXT: %s' % h)
        if bad:
            raise Refused('DRY: %d PREREQUISITE%s MISSING (the DRY CHECK lines above)' % (bad, '' if bad == 1 else 'S'))
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
        if CFG.get('CARD_COPY'):
            print('DRY NOTE: queued for real, it would copy %s to %s first' % CFG['CARD_COPY'])
        print('DRY RUN OK: %s %s %s %s on %s; WRITES_MB %s, MEM_MB %s; nothing claimed or queued' % (runtag, kind, idea, '/'.join(vs), q, sub['@@WMB@@'], sub['@@MMB@@']))
        return 0
    fill('0')                                    # all checks pass before a number is claimed
    if CFG.get('CARD_COPY'):                     # v12: the sealed card as ALARM_CARD.md, byte for byte, never over a file
        src_card, dst_card = CFG['CARD_COPY']
        with open(src_card, 'rb') as f, open(dst_card, 'xb') as g:
            g.write(f.read())
        if sha16(src_card) != sha16(dst_card):
            raise Refused('CARD COPY DIFFERS %s %s' % (src_card, dst_card))
        print('CARD COPIED %s -> %s sha16 %s' % (src_card, dst_card, sha16(dst_card)))
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
                   'from_job': row.get('from_job') or opts['--from-job'] or '-', 'receipts_rel': 'receipts/%s_%s_%s' % (n, kind, idea)})
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
        if next_hint(str(e)):
            print('NEXT: %s' % next_hint(str(e)), file=sys.stderr)
        sys.exit(2)
