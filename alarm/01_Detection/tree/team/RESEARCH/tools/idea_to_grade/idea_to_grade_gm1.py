# idea_to_grade_gm1.py (BUILD5 for SCOUT, G1 D4, 31 Oct 2026; TEST, NOT REVIEWED; the owner 31 Oct 13:28 Berlin: "Their tools need to be fast and
# refactored properly"): ONE edition for GRADE and MONTH, made by team/BUILD5/proposals/idea_to_grade_gm1/make_i2g_gm1.py from
# idea_to_grade_rel1.py edee6bbe51a2bbde (GRADE) and idea_to_grade_aw1_rel1.py 64d3fbb8006a8261 (MONTH), both never edited. Changed, nothing
# else: the window choice is an argument (--windows GRADE|MONTH, check_window(..., windows); missing or another word refused NO_WINDOWS):
# GRADE reads labcore.gates' WINDOWS_V1 classes (rel1), MONTH the alarm kit's alarm_process/WINDOWS_ALARM_V1.tsv (its sha16 checked; aw1);
# its pins file is I2G_PINS_GM1.json (rel1's pins with this file in place of idea_to_grade_rel1.py: the same for both windows). The fresh
# detection still imports detect_v2 under both windows, as both editions do. idea_to_grade_rel1.py's text follows.
"""idea_to_grade_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: idea_to_grade.py (V2.3.1) 43215be173cb148d, never edited. Changed: F (the tree root) is found from this file; no machine
default for the lab days (--lab-root required: the settings key LAB_DAYS) nor for the feed's stop gate (--gate: the settings key
FEED_GATE, read exactly as before: its first line RUN; empty or not given: no gate; set_gate() for an importer); the pins file names
paths relative to F (load_pins refuses an absolute one) and V2.3.1's own command needs --pins (its released pins name past editions);
the detector is detect_v2 (97a822a20e08088d: detect.py with its paths changed, the same EVENTS), the engine i2g_engine_rel1, the
grading i2g_grade_rel1. VERSION and every output's format are idea_to_grade.py's.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is idea_to_grade.py's.
idea_to_grade.py — THE ONE PUBLIC COMMAND: a registered idea -> fresh detection -> matched controls -> opportunity measurements -> grading
-> one downstream-ready run, published all-or-nothing with RUN.json written last (STRATEGY/LEAD; owner 25 Oct 2026 11:59Z: "finish the tool and
launch it as soon as possible"). Paper research only: it reads stored lab data, never trades, never writes a store.

  PY=<PYTHON>; T=<forensics>/team/RESEARCH/tools/idea_to_grade
  nice -n 10 $PY -B $T/idea_to_grade.py --idea <definition.json> --roster <ROSTER_BUILD.json> --coins ALL|A,B,C | --group NAME --group-file F
        --first YYYYMMDD --last YYYYMMDD --research-window FIRST:LAST --out <new folder> [--workers 8] [--max-rss-gb 16]

STAGES (one process tree; README.md is the manual, ARCHITECTURE.md the design):
  1 DETECT   i2g_detector's detect.run (fresh, every run; its committed run lands in <out>/detect/).
  2 MATCH    per coin, alarm_match/draw_v3 (imported): up to 10 matched control moments per parent (same coin, +-7 days, UTC hour +-1,
             same split part, no alarm in the 30 min before, pre-activity within the caliper); whole-parent abstention when the detector
             did not fully know a candidate day.
  3 MEASURE  per coin, the 55 STAMP fields (alarm_stamp, BED fill + ladder) for every parent and eligible control, FOLLOW and FADE.
  4 GRADE    190 cohorts x (ALL + each month): reach, heat before the offer, timing, paired comparison with the matched controls (the outside
             grading kernel, imported). Opportunity, not profit.
  5 PUBLISH  staged folder, verified, one rename, RUN.json last (event_decisions/run_manifest_candidate.py). A failure leaves
             <out>.failed_<stamp> with FAILED.json; nothing half-written is ever served as a run.
No date is held in this code: the dates and the research window are the caller's; lab3/law.py (inside the reader) is the only seal; every
research-window month must be a BUILD month of the window table (labcore.gates.WINDOWS) or the run is refused before any read."""
import argparse, csv, datetime as dt, hashlib, json, math, os, pickle, resource, subprocess, sys, threading, time, traceback
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np

F = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))             # the tree root: <F>/team/RESEARCH/tools/idea_to_grade holds this file
TOOLS = F + '/team/RESEARCH/tools'
GATE = None                     # the feed's stop gate file: set_gate(--gate, the settings key FEED_GATE); None or '': no gate
LAB_ROOT = None                 # no machine default: --lab-root (the settings key LAB_DAYS)
MANIFEST_HELPER = TOOLS + '/event_decisions/run_manifest_candidate.py'
VERSION = 'I2G_V1'
THREADS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMBA_NUM_THREADS')
MAX_WORKERS = 8
US = 1_000_000
DIRECTIONS = ('FOLLOW', 'FADE')


WINDOWS_ALARM = os.path.join(os.path.dirname(HERE), 'alarm_process', 'WINDOWS_ALARM_V1.tsv'); WINDOWS_ALARM_SHA16 = '37decf0075649f69'   # aw1: the alarm kit's window classes
WINDOWS = ('GRADE', 'MONTH')                                        # gm1: the window choice (an argument)
PINS_FILE = None                                                    # V2.3.1's released pins name past editions: its command here needs --pins
RUN_SCHEMA = 'I2G_RUN_V2'
# the exact file inventory of a published run (A54-F3): verify_run refuses a manifest that names more or fewer files than this
REQUIRED_FILES = ('matches/CENSUS.tsv', 'matches/EDGES.tsv', 'matches/BALANCE.tsv', 'matches/COMPARISON_COVERAGE.json', 'matches/UNAVAILABLE.json',
                  'measurements/OBSERVATIONS.tsv', 'measurements/VALUES.npy', 'measurements/NAMES.json', 'measurements/REASONS.json',
                  'grading/COHORTS.json', 'grading/PARENT_DETAIL.npz', 'grading/PARENTS.tsv', 'grading/GRADED_EDGES.tsv', 'grading/REPORT.md',
                  'grading/GRADING_INPUT.pkl')
DETECT_FILES = ('detect/EVENTS.tsv', 'detect/COVERAGE.tsv', 'detect/DETECT_RUN.json')
HELPER_KEYS = ('schema', 'status', 'exit_status', 'committed_utc', 'part_digests',  # keys run_manifest_candidate adds at commit
               'run_check', 'run_check_seal')                                      # (S1 V3: its own sealed run check)


class Refused(ValueError):
    def __init__(self, code, detail=''):
        super().__init__('%s: %s' % (code, detail)); self.code = code


def strict_day(d, what):
    """a real calendar day written YYYYMMDD (8 digits) -> d; Refused BAD_DAY otherwise (2025091 or 20260230 are refused)"""
    import re
    try:
        ok = isinstance(d, str) and re.fullmatch(r'\d{8}', d) is not None and dt.datetime.strptime(d, '%Y%m%d').strftime('%Y%m%d') == d
    except ValueError:
        ok = False
    if not ok:
        raise Refused('BAD_DAY', '%s %r is not a real day written YYYYMMDD' % (what, d))
    return d


def body_digest(body):
    """sha16 of the manifest body as JSON stores it (every key but the helper's own and body_sha16): an edited RUN.json is refused"""
    b = {k: v for k, v in json.loads(json.dumps(body, allow_nan=False)).items() if k not in HELPER_KEYS + ('body_sha16',)}
    return hashlib.sha256(json.dumps(b, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()[:16]


def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def gate_ok():
    """the feed's stop gate: the first line of GATE is RUN; no gate (None or ''): True, a machine without the feed. A missing
    gate file stops the run as before (OSError)"""
    if not GATE:
        return True
    with open(GATE) as f:
        return f.readline().strip() == 'RUN'


def set_gate(path):
    """the caller's gate file (--gate: the settings key FEED_GATE); None or '': no gate"""
    global GATE
    GATE = path or None


def day_of_us(t_us):
    return dt.datetime.fromtimestamp(t_us // US, dt.timezone.utc).strftime('%Y%m%d')


def months_between(first, last):
    out, y, m = [], int(first[:4]), int(first[4:6])
    while '%04d%02d' % (y, m) <= last[:6]:
        out.append('%04d%02d' % (y, m)); m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


_HELPER = []


def load_helper():
    if not _HELPER:
        import i2g_engine_rel1 as E
        _HELPER.append(E.load_path(MANIFEST_HELPER, 'run_manifest_candidate'))
    return _HELPER[0]


# ------------------------------------------------------------------------------------------------------------------ code identity (pins)
def warm():
    """import everything a run executes in this process (kernels, grading kernel, publication helper, the detector and its engine)"""
    import i2g_engine_rel1 as E, i2g_grade_rel1 as GR, detect_v2 as detect
    E.K.load(); GR.G.load(); load_helper(); detect.engine(); detect.module_pins()
    return E


def census_modules():
    """{path: sha16} of every forensics file this process executed, plus the detector's own code list (its engine loads by path)"""
    import i2g_engine_rel1 as E, detect_v2 as detect
    mods = E.process_modules(refresh=True)
    for q, h in detect.module_pins().items():
        mods[os.path.realpath(q)] = E.sha16(q)
    return mods


def load_pins(path):
    try:
        doc = json.load(open(path))
        pins = doc['pins']
    except (OSError, ValueError, KeyError) as e:
        raise Refused('PINS_FILE', '%s: %s' % (path, e))
    out = {}
    for q, h in pins.items():                                        # rel1: paths relative to the tree root F
        if os.path.isabs(q) or '/../' in '/%s/' % q:
            raise Refused('PINS_FILE', '%s names %s: a pins file of this edition names paths relative to the tree root' % (path, q))
        out[os.path.realpath(os.path.join(F, q))] = h
    return out


def check_against_pins(pins, observed, where):
    unpinned = sorted(set(observed) - set(pins))
    if unpinned:
        raise Refused('UNPINNED_MODULE', '%s executed files the release does not pin: %s' % (where, unpinned[:5]))
    drift = sorted(q for q in observed if observed[q] != pins[q])
    if drift:
        raise Refused('KERNEL_DRIFT', '%s: %s' % (where, ['%s is %s, pinned %s' % (q, observed[q], pins[q]) for q in drift[:3]]))


def recheck_pins(pins, code='KERNEL_DRIFT'):
    """every pinned file re-hashed now"""
    bad = [q for q, h in sorted(pins.items()) if not os.path.isfile(q) or sha16(q) != h]
    if bad:
        raise Refused(code, 'changed: %s' % bad[:5])


# ------------------------------------------------------------------------------------------------------------------ the process tree memory
class TreeMemory:
    """samples the RSS of this process and every descendant (ps) every interval; peak = the largest instantaneous sum seen; a sample over
    the limit stops the run (MEMORY_LIMIT). Between-sample spikes can be missed: the per-process ru_maxrss sum is reported beside it as the
    upper bound."""
    def __init__(self, limit_bytes, interval=0.1):
        self.limit = limit_bytes; self.interval = interval; self.peak = 0; self.samples = 0; self.over = None; self.stop = threading.Event()
        self.peak_procs = 0
        self.sample()                                                       # one sample before anything runs
        self.th = threading.Thread(target=self.loop, daemon=True); self.th.start()

    def sample(self):
        out = subprocess.run(['ps', '-axo', 'pid=,ppid=,rss='], capture_output=True, text=True).stdout.split('\n')
        kids = {}; rss = {}
        for line in out:
            f = line.split()
            if len(f) == 3:
                p, pp, r = int(f[0]), int(f[1]), int(f[2]); kids.setdefault(pp, []).append(p); rss[p] = r * 1024
        tot = 0; stack = [os.getpid()]; n = 0
        while stack:
            p = stack.pop(); tot += rss.get(p, 0); n += 1; stack += kids.get(p, [])
        self.samples += 1
        if tot > self.peak:
            self.peak = tot; self.peak_procs = n
        if tot > self.limit and self.over is None:
            self.over = tot
        return tot

    def loop(self):
        while not self.stop.wait(self.interval):
            try:
                self.sample()
            except Exception:
                pass

    def close(self):
        self.stop.set(); self.th.join(timeout=2)
        try:
            self.sample()
        except Exception:
            pass


# ------------------------------------------------------------------------------------------------------------------ worker process setup
def _watch_parent(ppid):
    while True:
        time.sleep(0.2)
        if os.getppid() != ppid:                                   # the run's process died (even by SIGKILL): this worker stops too
            os._exit(70)


def _worker_init():
    """each pool worker: exits when the run's process dies, nice >= 10 (absolute, never lowered), one numeric thread (environment
    inherited), kernels imported once (their files are reported with every task and checked against the release pins)"""
    threading.Thread(target=_watch_parent, args=(os.getppid(),), daemon=True).start()
    try:
        os.setpriority(os.PRIO_PROCESS, 0, max(10, os.getpriority(os.PRIO_PROCESS, 0)))
    except OSError:
        pass
    import i2g_engine_rel1 as E, i2g_grade_rel1 as GR
    E.K.load(); GR.G.load(); E.process_modules(refresh=True)


# ------------------------------------------------------------------------------------------------------------------ inputs
def read_detect(path, allow_fixture):
    """a committed detector run folder -> (manifest, events, coverage): refused (never a traceback) when DETECT_RUN.json is missing, not
    COMPLETE, a listed file changed, a file is missing or added; a fixture needs --allow-fixture (tests); a detector run also passes
    detect.read_run"""
    mp = os.path.join(path, 'DETECT_RUN.json')
    if not os.path.isfile(mp):
        raise Refused('DETECT_RUN_MISSING', '%s has no DETECT_RUN.json' % path)
    try:
        m = json.load(open(mp))
    except ValueError as e:
        raise Refused('DETECT_RUN_INVALID', str(e))
    if m.get('status') != 'COMPLETE':
        raise Refused('DETECT_NOT_COMPLETE', path)
    kind = m.get('kind', 'DETECTOR')
    if kind == 'FIXTURE_FROM_OUTSIDE_VIEW' and not allow_fixture:
        raise Refused('FIXTURE_DETECT_RUN', 'a fixture detector run is accepted only with --allow-fixture (tests)')
    files = m.get('files')
    if not isinstance(files, dict) or not {'EVENTS.tsv', 'COVERAGE.tsv'} <= set(files):
        raise Refused('DETECT_RUN_INVALID', '%s: no file list' % mp)
    extra = sorted(set(os.listdir(path)) - set(files) - {'DETECT_RUN.json'})
    if extra:
        raise Refused('DETECT_RUN_EXTRA_FILE', '%s: %s' % (path, extra[:5]))
    for n, h in files.items():
        q = os.path.join(path, n)
        if not os.path.isfile(q) or sha16(q) != h:
            raise Refused('DETECT_RUN_FILE_CHANGED', '%s/%s' % (path, n))
    if kind not in ('FIXTURE_FROM_OUTSIDE_VIEW', 'EVENT_LIST'):
        import detect_v2 as detect
        try:
            m = detect.read_run(path)
        except detect.Refusal as e:
            raise Refused('DETECT_RUN_' + e.code, str(e))
    with open(os.path.join(path, 'EVENTS.tsv')) as f:
        ev = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    with open(os.path.join(path, 'COVERAGE.tsv')) as f:
        cov = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    return m, ev, cov


def check_window(window, first, last, windows=None):
    """the research window (a run setting) -> its months; refused unless every month is a BUILD month of labcore.gates' window table and
    its last day passes lab3/law.py, and first..last lies inside it"""
    import i2g_engine_rel1 as E
    if windows not in WINDOWS:                                       # gm1: GRADE or MONTH, never a default
        raise Refused('NO_WINDOWS', 'the window table is GRADE or MONTH (--windows), got %r' % (windows,))
    if windows == 'GRADE':                                           # gm1: GRADE = rel1's
        k = E.K.load(); wins = k.gates.windows(); law = k.gates.load_law()
    else:                                                            # gm1: MONTH = aw1's
        k = E.K.load(); law = k.gates.load_law()
        if hashlib.sha256(open(WINDOWS_ALARM, 'rb').read()).hexdigest()[:16] != WINDOWS_ALARM_SHA16:   # aw1
            raise Refused('ALARM_WINDOWS_CHANGED', '%s is not sha16 %s' % (WINDOWS_ALARM, WINDOWS_ALARM_SHA16))
        wins = k.gates.windows(WINDOWS_ALARM)   # aw1: the alarm kit's classes (WINDOWS_V1 unchanged)
    a, b = window
    for d, what in ((a, 'research window first'), (b, 'research window last'), (first, '--first'), (last, '--last')):
        strict_day(d, what)
    if first > last:
        raise Refused('BAD_DAY', '--first %s is after --last %s' % (first, last))
    if not a <= b:
        raise Refused('RESEARCH_WINDOW', '%s > %s' % (a, b))
    for m in months_between(a, b):
        cls = k.gates.window_of(m, wins)
        if cls != 'BUILD':
            raise Refused('RESEARCH_WINDOW_NOT_BUILD', 'month %s is in the %s window of %s' % (m, cls, k.gates.WINDOWS if windows == 'GRADE' else WINDOWS_ALARM))   # gm1
        why = law.research_refusal(k.gates.month_last_day(m))
        if why:
            raise Refused('RESEARCH_WINDOW_SEALED', 'month %s: %s' % (m, why))
    if not a <= first <= last <= b:
        raise Refused('SELECTION_OUTSIDE_WINDOW', '%s..%s is not inside the research window %s..%s' % (first, last, a, b))


def event_list_prepare(a):
    """INPUT MODE 2, an event list (coin, t, side[, onset_t, trigger]) instead of an idea, checked BEFORE anything is staged: its sha16
    pinned by the caller (--events-sha16), read by the shared strict loader (event_profile.load_alarms: whole seconds, side -1/0/+1,
    onset <= t, no duplicate identity), the roster selector of detect.py; side-0 selected events refused -> the selected rows"""
    import detect_v2 as detect
    sys.path.insert(0, TOOLS + '/event_profile')
    import event_profile as EP
    src = os.path.abspath(a.events)
    if not os.path.isfile(src):
        raise Refused('EVENT_LIST_MISSING', src)
    if sha16(src) != a.events_sha16:
        raise Refused('EVENT_LIST_SHA', '%s is %s, pinned %s' % (src, sha16(src), a.events_sha16))
    roster, roster_sha = detect.load_roster(a.roster)
    coins_arg = a.coins if a.coins is not None else (None if a.group else 'ALL')
    chosen, selection = detect.select_coins(roster, coins_arg, a.group, a.group_file)
    try:
        ev = EP.load_alarms(src)
    except ValueError as e:
        raise Refused('EVENT_LIST_INVALID', str(e)[:500])
    rows = []; outside = other = side0 = 0
    for c, t, sd, ot, tr in zip(ev['coin'], ev['t'], ev['side'], ev['onset_t'], ev['trigger']):
        d = day_of_us(int(t) * US)
        if c not in chosen:
            other += 1; continue
        if not a.first <= d <= a.last:
            outside += 1; continue
        if int(sd) == 0:
            side0 += 1; continue
        eid = hashlib.sha256(('%s|%s|%d|%d' % (a.events_sha16, c, int(t), int(sd))).encode()).hexdigest()[:16]
        rows.append((str(c), int(t), int(sd), int(ot) if int(ot) > 0 else '', str(tr), eid))
    if side0:
        raise Refused('EVENT_SIDE', '%d selected events have side 0; this release grades side -1 / +1 events only' % side0)
    rows.sort(key=lambda x: (x[1], x[0]))
    return {'src': src, 'rows': rows, 'chosen': chosen, 'selection': selection, 'roster_sha': roster_sha, 'n': int(len(ev['t'])),
            'other': other, 'outside': outside}


def event_list_write(a, prep, det_dir):
    """the coverage computed HERE from the lab data: a requested coin-day is covered (full_known 1) when the day's PRICE part lists the coin
    (lab3 index through the seal), NOT_LISTED when it does not, NOT_BUILT when lab3 says the day has no PRICE part (any other error, a
    changed or unreadable index, stops the run). The list's own producer coverage is not known to this tool: DETECT_RUN.json says so.
    Writes the same three files as a detector run (EVENTS.tsv, COVERAGE.tsv, DETECT_RUN.json kind EVENT_LIST)."""
    import i2g_engine_rel1 as E
    k = E.K.load(); R = k.Days(a.lab_root, 'research'); rows, chosen = prep['rows'], prep['chosen']
    cov = []; listed = {}; vint = {}
    for d in E.calendar(a.first, a.last):
        try:
            ix = R.index(d, 'PRICE'); listed[d] = set(ix['coins']); vint[d] = E.index_sha16(a.lab_root, d)
        except k.NotBuilt:
            listed[d] = None; vint[d] = E.ABSENT                                  # absence is part of the source identity
        for c in chosen:
            st = 'NOT_BUILT' if listed[d] is None else 'PRESENT' if c in listed[d] else 'NOT_LISTED'
            cov.append((c, d, st, '' if st == 'PRESENT' else 'PRICE ' + st, '', '', '', 1 if st == 'PRESENT' else 0))
    on_absent = sum(1 for r in rows if listed.get(day_of_us(r[1] * US)) is None or r[0] not in listed[day_of_us(r[1] * US)])
    os.makedirs(det_dir)
    with open(os.path.join(det_dir, 'EVENTS.tsv'), 'x') as f:
        f.write('# idea_to_grade event list %s sha16 %s\n# roster sha16 %s\n# first %s last %s\n# selection %s\n'
                % (prep['src'], a.events_sha16, prep['roster_sha'], a.first, a.last, json.dumps(prep['selection'], sort_keys=True)))
        f.write('coin\tt\tside\tonset_t\ttrigger\tevent_id\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    with open(os.path.join(det_dir, 'COVERAGE.tsv'), 'x') as f:
        f.write('coin\tday\tstatus\treason\tslots\tknown_slots\tpredecessor_known\tfull_known\n')
        for r in cov:
            f.write('\t'.join(str(x) for x in r) + '\n')
    m = {'status': 'COMPLETE', 'kind': 'EVENT_LIST', 'tool': 'idea_to_grade.event_list_write',
         'source': {'path': prep['src'], 'sha16': a.events_sha16, 'rows': prep['n'], 'other_coins': prep['other'],
                    'outside_first_last': prep['outside']}, 'events': len(rows), 'events_on_uncovered_cells': on_absent,
         'coins': chosen, 'selection': prep['selection'], 'roster': {'path': os.path.abspath(a.roster), 'sha16': prep['roster_sha']},
         'first': a.first, 'last': a.last, 'cells': {'requested': len(cov), 'present': sum(r[7] for r in cov), 'unavailable': sum(1 - r[7] for r in cov)},
         'coverage_rule': 'EVENT_LIST: a requested coin-day is covered when the PRICE part of that day lists the coin (lab3 index, research '
                          'seal); the producer of the list did not report its own coverage, so candidate control days are trusted as alarm-free '
                          'wherever the coin is listed',
         'price_index_sha16': vint,
         'files': {n: sha16(os.path.join(det_dir, n)) for n in ('EVENTS.tsv', 'COVERAGE.tsv')}}
    with open(os.path.join(det_dir, 'DETECT_RUN.json'), 'x') as f:
        json.dump(m, f, indent=1, sort_keys=True, allow_nan=False)
    return m


# ------------------------------------------------------------------------------------------------------------------ the run
def run(a):
    t_start = time.perf_counter(); phases = {}; started = dt.datetime.now(dt.timezone.utc).isoformat()
    # ---- admission: settings, inputs, gate, window table, law.py, code identity; every input error is refused HERE, before staging
    if not 1 <= a.workers <= MAX_WORKERS:
        raise Refused('WORKERS', '1..%d' % MAX_WORKERS)
    window = tuple(a.research_window.split(':'))
    if len(window) != 2:
        raise Refused('RESEARCH_WINDOW', 'FIRST:LAST, got %r' % a.research_window)
    for d, what in ((window[0], 'research window first'), (window[1], 'research window last'), (a.first, '--first'), (a.last, '--last')):
        strict_day(d, what)
    if not gate_ok():
        raise Refused('GATE_NOT_RUN', GATE)
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise Refused('NICE10_REQUIRED', 'run the command under nice -n 10')
    for kk in THREADS:
        os.environ[kk] = '1'
    out = os.path.abspath(a.out)
    if os.path.lexists(out):
        raise Refused('OUTPUT_EXISTS', '%s exists: a run is published into a new folder only' % out)
    pins = load_pins(a.pins); pins_sha = sha16(a.pins)
    recheck_pins(pins)                                                        # every pinned file as released
    E = warm(); import i2g_grade_rel1 as GR, detect_v2 as detect
    H = load_helper()
    check_against_pins(pins, census_modules(), 'the run process')
    check_window(window, a.first, a.last, a.windows)
    prep = None
    if a.events:
        prep = event_list_prepare(a)
    elif a.detect_run:
        read_detect(os.path.abspath(a.detect_run), a.allow_fixture)
    else:
        _, info = detect.load_definition(a.idea)                              # detect's own admission of the definition, before staging
        for key in ('first', 'last'):
            if key in info.get('window', {}):
                try:
                    strict_day(info['window'][key], 'definition window %s' % key)
                except Refused as e:
                    raise Refused('DEFINITION_WINDOW_MALFORMED', str(e))
        roster, _ = detect.load_roster(a.roster)
        detect.select_coins(roster, a.coins if a.coins is not None else (None if a.group else 'ALL'), a.group, a.group_file)
    mem = TreeMemory(int(a.max_rss_gb * 1024 ** 3))
    try:
        pending = H.stage(out)                                                # a staged folder; out appears only at the commit
    except H.RunRefused as e:
        mem.close(); raise Refused(e.code, str(e))
    pool = None
    try:
        phases['admission'] = time.perf_counter() - t_start
        # ---- 1 DETECT
        t0 = time.perf_counter()
        if a.detect_run:
            det_dir = os.path.abspath(a.detect_run); detection = 'REUSED_FOR_TEST'
        elif a.events:
            det_dir = os.path.join(pending, 'detect'); event_list_write(a, prep, det_dir); detection = 'EVENT_LIST'
        else:
            det_dir = os.path.join(pending, 'detect')
            coins = a.coins if a.coins is not None else (None if a.group else 'ALL')
            try:
                detect.run(a.idea, a.first, a.last, det_dir, a.roster, coins=coins, group=a.group, group_file=a.group_file, workers=a.workers,
                           lab_root=a.lab_root, research_window=window, gate=GATE)
            except detect.Refusal as e:
                raise Refused('DETECT_' + e.code, str(e))
            detection = 'FRESH'
        dm, events, coverage = read_detect(det_dir, a.allow_fixture)
        if dm['first'] != a.first or dm['last'] != a.last:
            raise Refused('DETECT_RANGE', 'detector run %s..%s, asked %s..%s' % (dm['first'], dm['last'], a.first, a.last))
        outside = sorted({x[4:12] for x in dm.get('sources', {}) if x.startswith('day=') and not window[0] <= x[4:12] <= window[1]})
        if outside:
            raise Refused('DETECT_READ_OUTSIDE_WINDOW', 'the detector read days %s outside the research window' % outside[:5])
        if 'code_sha16' in dm and isinstance(dm['code_sha16'], dict):
            check_against_pins(pins, {os.path.realpath(q): h for q, h in dm['code_sha16'].items()}, 'the detector run')
        phases['detect'] = time.perf_counter() - t0
        if mem.over:
            raise Refused('MEMORY_LIMIT', str(mem.over))
        # ---- parents and coin tasks
        t0 = time.perf_counter()
        coins = list(dm['coins']) if 'coins' in dm else list(dm['selection']['coins'])
        k = E.K.load(); split = k.D.split_from(k.gates.WINDOWS)
        by_coin = {}
        for r in events:
            t = int(r['t']); sd = int(r['side'])
            if sd not in (-1, 1):
                raise Refused('EVENT_SIDE', 'side %r (side-0 events are not graded by this release)' % r['side'])
            by_coin.setdefault(r['coin'], []).append((t, sd, r.get('event_id', '')))
        known = {}
        for r in coverage:
            if r['full_known'] == '1':
                known.setdefault(r['coin'], []).append(r['day'])
        # tasks: each coin's parents, per split part (the matcher's part order: sorted names), in contiguous time chunks; a chunk carries the
        # coin's WHOLE event list as its exclusions; outputs re-join in (coin, part, chunk) order = the one-task order
        total = sum(len(v) for v in by_coin.values()); size = max(a.min_chunk, -(-total // (4 * a.workers)))
        if a.chunk:
            size = a.chunk
        tasks = []
        for c in coins:
            ps = sorted(by_coin.get(c, []))
            if not ps:
                continue
            parts = {}
            for t, sd, _ in ps:
                parts.setdefault(k.D.part_of(float(t), split), []).append((t, sd))
            for part in sorted(parts, key=lambda x: (x is None, x)):
                if part is None:
                    raise Refused('PARENT_OUTSIDE_SPLIT', '%s has events outside every split part' % c)
                pp = parts[part]
                for j in range(0, len(pp), size):
                    tasks.append(dict(coin=c, order=(part, j // size), parents=pp[j:j + size], alarms=[t for t, _, _ in ps],
                                      known_days=known.get(c, []), lab_root=a.lab_root, window=list(window), split=[list(x) for x in split],
                                      settings=dict(k.D.S0), seed=a.seed, measure=True))
        run_order = sorted(range(len(tasks)), key=lambda i: -len(tasks[i]['parents']))      # longest first (LPT)
        phases['plan'] = time.perf_counter() - t0
        # ---- 2+3 MATCH and MEASURE: one task per coin, each PRICE coin-day read once
        t0 = time.perf_counter()
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        pool = ProcessPoolExecutor(max_workers=a.workers, mp_context=mp.get_context('spawn'), initializer=_worker_init)
        futs = {i: pool.submit(E.coin_job, tasks[i]) for i in run_order}
        results = {}
        vintages = dict(dm.get('price_index_sha16', {}))                     # PRICE state per day (index sha16 or ABSENT): one per day per run
        for i in run_order:
            try:
                r = futs[i].result()
            except E.SourceChanged as e:
                raise Refused('SOURCE_CHANGED', str(e))
            r['order'] = tasks[i]['order']; results.setdefault(r['coin'], []).append(r)
            for d, h in r['price_vintages'].items():
                if vintages.setdefault(d, h) != h:
                    raise Refused('SOURCE_CHANGED', 'PRICE %s was seen in two states in one run (%s, %s)' % (d, vintages[d], h))
            check_against_pins(pins, r['modules'], 'worker %d' % r['pid'])
            if mem.over:
                raise Refused('MEMORY_LIMIT', str(mem.over))
            if not gate_ok():
                raise Refused('GATE_NOT_RUN', 'the gate left RUN during the run')
        for c in results:
            results[c].sort(key=lambda r: r['order'])
        phases['match_measure'] = time.perf_counter() - t0
        # ---- aggregate (the outside chain's order and identities)
        t0 = time.perf_counter()
        agg = aggregate(coins, events, results, k, split)
        os.makedirs(os.path.join(pending, 'matches')); os.makedirs(os.path.join(pending, 'measurements')); os.makedirs(os.path.join(pending, 'grading'))
        write_matches(pending, agg, k)
        write_measurements(pending, agg)
        inputs = grading_inputs(agg, k)
        inputs_path = os.path.join(pending, 'grading', 'GRADING_INPUT.pkl')
        with open(inputs_path, 'wb') as f:
            pickle.dump(inputs, f, protocol=5)
        phases['aggregate'] = time.perf_counter() - t0
        # ---- 4 GRADE
        t0 = time.perf_counter()
        S = k.S
        offers = list(S.OFFERS); halves = [offers[:len(offers) // 2], offers[len(offers) // 2:]]
        gtasks = [dict(run_key=inputs['run_key'], inputs_path=inputs_path, values_path=os.path.join(pending, 'measurements', 'VALUES.npy'),
                       direction=d, horizon=h, offers=o) for h in S.HORIZONS[::-1] for d in DIRECTIONS for o in halves]
        gres = [f.result() for f in [pool.submit(GR.grade_task, t) for t in gtasks]]
        for g in gres:
            check_against_pins(pins, g['modules'], 'worker %d' % g['pid'])
        peaks = {}
        for r in [x for v in results.values() for x in v] + gres:
            peaks[r['pid']] = max(peaks.get(r['pid'], 0), r['ru_maxrss'])
        pool.shutdown(wait=True); pool = None
        phases['grade'] = time.perf_counter() - t0
        if mem.over:
            raise Refused('MEMORY_LIMIT', str(mem.over))
        # ---- 5 PUBLISH
        t0 = time.perf_counter()
        report = write_grading(pending, agg, inputs, gres, S)
        parts = {}
        for root, _, files in os.walk(pending):
            for n in files:
                p = os.path.join(root, n); parts[os.path.relpath(p, pending)] = sha16(p)
        if not gate_ok():
            raise Refused('GATE_NOT_RUN', 'the gate left RUN before publication')
        if a.events and sha16(a.events) != a.events_sha16:
            raise Refused('EVENT_LIST_CHANGED', 'the event list changed during the run')
        if a.idea and sha16(a.idea) != dm['definition']['sha16']:
            raise Refused('IDEA_CHANGED', 'the definition changed during the run')
        recheck_pins(pins, 'CODE_CHANGED')                                    # every pinned file, again, before anything is published
        changed = [d for d, h in sorted(vintages.items()) if E.price_state(a.lab_root, d) != h]
        if changed:
            raise Refused('SOURCE_CHANGED', 'PRICE changed (or appeared / disappeared) during the run on %s' % changed[:5])
        if sha16(a.pins) != pins_sha:
            raise Refused('CODE_CHANGED', 'the pins file changed during the run')
        phases['publish_write'] = time.perf_counter() - t0
        mem.close()
        body = {
            'tool': 'idea_to_grade', 'version': VERSION, 'run_id': hashlib.sha256(('%s|%s' % (out, started)).encode()).hexdigest()[:16],
            'started_utc': started, 'idea': {'path': os.path.abspath(a.idea), 'sha16': sha16(a.idea)} if a.idea else None,
            'event_list': {'path': os.path.abspath(a.events), 'sha16': a.events_sha16} if a.events else None,
            'detection': detection, 'detect_run': {'path': os.path.relpath(det_dir, pending) if det_dir.startswith(pending) else det_dir,
                                                    'status': dm['status'], 'events': dm['events'], 'wall_s': dm.get('wall_s'),
                                                    'kind': dm.get('kind', 'DETECT_RUN')},
            'selection': {'coins': coins, 'group': a.group, 'group_file': a.group_file,
                          'group_file_sha16': sha16(a.group_file) if a.group_file else None, 'first': a.first, 'last': a.last,
                          'research_window': list(window), 'roster': {'path': a.roster, 'sha16': sha16(a.roster)} if a.roster else None,
                          'requested_coin_days': len(coverage), 'present_coin_days': sum(1 for r in coverage if r['status'] == 'PRESENT'),
                          'unavailable_coin_days': [{'coin': r['coin'], 'day': r['day'], 'status': r['status'], 'reason': r.get('reason', '')}
                                                    for r in coverage if r['status'] != 'PRESENT']},
            'settings': {'match': dict(k.D.S0, split=[list(x) for x in split], seed=a.seed), 'measure': {
                'names': list(S.NAMES), 'execution_delay_s': S.DELAY_S, 'hold_s': S.HOLD_S, 'decision_wait_s': 0, 'directions': list(DIRECTIONS)},
                'grade': {'offers': list(S.OFFERS), 'horizons': list(S.HORIZONS), 'quantiles': list(GR.QUANTILES), 'wave_gap_s': 1800}},
            'counts': report['counts'], 'report': report['headline'],
            'run_schema': RUN_SCHEMA, 'sources': {'price_state_by_day': dict(sorted(vintages.items())), 'lab_root': a.lab_root,
                                                  'meaning': 'every PRICE day the run consulted: the sha16 of its index, or ABSENT (no part); '
                                                             'rechecked at each task end and before publication'},
            'code_sha16': dict(sorted(pins.items())), 'pins_file': {'path': os.path.abspath(a.pins), 'sha16': pins_sha,
                                                                    'files': len(pins)},
            'clocks': {'observation_known_at': 'as_of + %s s (alarm_stamp.offset_s: 6 s delay + 60 s longest fill wait + 4 h hold)'
                       % k.S.offset_s(k.S.DELAY_S, k.S.HOLD_S),
                       'parent_known_at': 'the latest of its own observation and its eligible controls; an abstained parent: 00:00 after the '
                                          'latest candidate day whose coverage decided it; NO_ELIGIBLE: also 00:00 after its last candidate day'},
            'parts': parts,
            'timing_s': dict(phases, wall_to_commit=time.perf_counter() - t_start),
            'memory': {'tree_peak_sampled_bytes': mem.peak, 'tree_peak_processes': mem.peak_procs, 'samples': mem.samples,
                       'limit_bytes': mem.limit, 'parent_ru_maxrss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       'worker_ru_maxrss_bytes': peaks, 'detector_sum_peak_rss_bytes': dm.get('memory', {}).get('sum_peak_rss_bytes'),
                       'meaning': 'tree_peak_sampled = the largest instantaneous RSS sum of this process and all descendants (ps every 0.1 s); '
                                  'ru_maxrss values are per-process peaks (their sum is an upper bound)'},
            'workers': {'processes': a.workers, 'start_method': 'spawn', 'nice': os.getpriority(os.PRIO_PROCESS, 0),
                        'threads_env': {kk: os.environ.get(kk) for kk in THREADS},
                        'chunk_size': size,
                        'coin_jobs': [{'coin': c, 'part': r['order'][0], 'chunk': r['order'][1], 'parents': len(r['census']), 'pid': r['pid'],
                                       'seconds': r['seconds'], 'price_reads': r['price_reads'], 'price_read_s': r['price_read_s']}
                                      for c in coins for r in results.get(c, [])],
                        'grade_jobs': [{'direction': t['direction'], 'horizon': t['horizon'], 'offers': t['offers'], 'pid': g['pid'],
                                        'seconds': g['seconds']}
                                       for t, g in zip(gtasks, gres)]},
            'not_asserted': 'opportunity (reach, heat before the offer, timing) against matched control moments; not profit, not causality, '
                            'not a strategy, research only (no live parity); Binance 3 s model prices, taker fill at the first 3 s close '
                            'traded after alarm + 9 s (6 s delay + fill_v2 3 s)',
        }
        body['body_sha16'] = body_digest(body)
        try:
            m = H.commit(pending, out, 'RUN', body)
        except H.RunRefused as e:
            raise Refused(e.code, str(e))
        wall = time.perf_counter() - t_start
        print(json.dumps({'status': 'COMPLETE', 'out': out, 'wall_s': round(wall, 3), 'timing_s': {k2: round(v, 3) for k2, v in phases.items()},
                          'parents': report['counts']['parents'], 'tree_peak_gb': round(mem.peak / 1024 ** 3, 3)}))
        return m
    except BaseException as e:
        try:
            if pool is not None:
                pool.shutdown(wait=False, cancel_futures=True)
        finally:
            mem.close()
            failed = H.abort(pending, out, '%s\n%s' % (repr(e), traceback.format_exc()))
            sys.stderr.write('FAILED %r -> %s\n' % (e, failed))
        raise


def aggregate(coins, events, results, k, split):
    """the outside chain's population identities: parents sorted by (t, coin, side), id coin_t; wave ids over every parent (1800 s);
    request rows in the outside order (each parent FOLLOW, FADE, then its eligible controls FOLLOW, FADE; one row per distinct
    (kind, coin, clock, side, direction))"""
    import i2g_engine_rel1 as E
    S = k.S
    census, edges, balance, unavailable = [], [], [], []
    for c in coins:
        for r in results.get(c, []):
            census += r['census']; edges += r['edges']; balance += r['balance']; unavailable += r['unavailable']
    ev_id = {('%s_%d' % (r['coin'], int(r['t']))): r.get('event_id', '') for r in events}
    ident = sorted(((int(r['t']) * US, r['coin'], int(r['side'])) for r in events))
    pids = ['%s_%d' % (c, t // US) for t, c, s in ident]
    if len(set(pids)) != len(pids):
        raise Refused('PARENT_ID_COLLISION', '')
    cen = {x[0]: x for x in census}
    if set(cen) != set(pids) or len(cen) != len(census):
        raise Refused('CENSUS_POPULATION', 'census %d parents %d' % (len(census), len(pids)))
    wav = k.waves(np.asarray([t / US for t, c, s in ident]), 1800)
    waves = {p: int(w) for p, w in zip(pids, wav)}
    raw_by = {}
    for e in edges:
        raw_by.setdefault(e[0], []).append(e)
    lookup = {}; requests = []; plan_edges = []; parents = []
    def obs(kind, coin, t, side, d):
        key = (kind, coin, t, side, d)
        if key not in lookup:
            lookup[key] = len(requests); requests.append(key)
        return lookup[key]
    for i, ((t, c, s), pid) in enumerate(zip(ident, pids)):
        original = raw_by.get(pid, []); eligible = [e for e in original if e[7] == '']
        cr = cen[pid]
        if len(original) != int(cr[4]):
            raise Refused('INCOMPLETE_EDGES', pid)
        p = {'id': pid, 'event_id': ev_id.get(pid, ''), 'coin': c, 'as_of_us': t, 'side': s, 'day': day_of_us(t), 'wave_id': waves[pid],
             'census_status': cr[5], 'original_draw_edges': len(original), 'eligible_edges': len(eligible),
             'rule_excluded_edges': len(original) - len(eligible), 'cov0': cr[6], 'row_ids': {}}
        for d in DIRECTIONS:
            p['row_ids'][d] = obs('parent', c, t, s, d)
        parents.append(p)
        for e in eligible:
            ct = E.ms_us(e[3]); w = float(e[5])
            for d in DIRECTIONS:
                plan_edges.append((i, obs('control', c, ct, s, d), w, d, int(e[6])))
    # the measurement matrix in request order, from the coin workers' rows
    names = list(S.NAMES); V = np.full((len(requests), len(names)), np.nan); reasons = {}; done = np.zeros(len(requests), bool)
    for c in coins:
        for r in results.get(c, []):
            for j, (kind, t, s, d) in enumerate(r['obs']):
                q = lookup.get((kind, c, t, s, d))
                if q is None:
                    raise Refused('OBSERVATION_IDENTITY', '%s %s' % (c, (kind, t, s, d)))
                if done[q]:                                   # the same moment drawn in two chunks: the two measurements must be identical
                    if not (np.array_equal(np.isnan(V[q]), np.isnan(r['values'][j])) and
                            np.array_equal(np.nan_to_num(V[q]).view(np.uint64), np.nan_to_num(r['values'][j]).view(np.uint64))) \
                            or reasons.get(str(q), {}) != r['reasons'].get(j, {}):
                        raise Refused('OBSERVATION_CONFLICT', '%s %s' % (c, (kind, t, s, d)))
                    continue
                V[q] = r['values'][j]; done[q] = True
                if j in r['reasons']:
                    reasons[str(q)] = r['reasons'][j]
    if not done.all():
        raise Refused('OBSERVATION_COUNT', '%d of %d requested rows measured' % (int(done.sum()), len(requests)))
    # clocks: an observation is known at as_of + alarm_stamp.offset_s (delay + longest fill wait + hold); a parent's grade inputs at the
    # latest of its own observation, its eligible controls', and the coverage of its candidate days (00:00 after the last one)
    off = int(round(S.offset_s(S.DELAY_S, S.HOLD_S) * US)); unav = {u['fid']: u['known_at_us'] for u in unavailable}
    bounds = {n: (x, y) for n, x, y in split}
    for p in parents:
        t = p['as_of_us']; ka = t + off
        if p['census_status'] == 'COMPARISON_UNAVAILABLE':
            ka = max(ka, unav[p['id']])
        elif p['census_status'] in ('MATCHED', 'NO_ELIGIBLE'):
            part = k.D.part_of(t / US, split); last = min(bounds[part][1], E.shift(p['day'], int(k.D.S0['days'])))
            ka = max(ka, int(k.D._day_start(E.shift(last, 1))) * US)
            ka = max([ka] + [E.ms_us(e[3]) + off for e in raw_by.get(p['id'], []) if e[7] == ''])
        p['known_at_us'] = ka
    months = sorted({p['day'][:6] for p in parents})
    coverage = {}
    for month in ['ALL'] + months:
        sel = [p for p in parents if month == 'ALL' or p['day'][:6] == month]
        counts = {s: sum(p['census_status'] == s for p in sel) for s in sorted({p['census_status'] for p in sel})}
        coverage[month] = {'full_parent_count': len(sel), 'census_status_counts': counts,
                           'comparison_unavailable_parents': counts.get('COMPARISON_UNAVAILABLE', 0), 'matched_parents': counts.get('MATCHED', 0),
                           'interpretation': 'Comparisons describe supported matched parents only; standalone measurements retain every parent.'}
    return dict(parents=parents, pids=pids, waves=waves, requests=requests, edges=plan_edges, raw_edges=edges, census=census,
                balance=balance, unavailable=unavailable, values=V, reasons=reasons, names=names, months=months, coverage=coverage, offset_us=off)


def _tsv(path, head, rows):
    with open(path, 'x') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(head); w.writerows(rows)


def _json(path, obj):
    import orjson
    with open(path, 'xb') as f:
        f.write(orjson.dumps(obj, option=orjson.OPT_SORT_KEYS) + b'\n')


def write_matches(pending, agg, k):
    d = os.path.join(pending, 'matches')
    _tsv(os.path.join(d, 'CENSUS.tsv'), ['fid', 'coin', 't', 'side', 'matches', 'status', 'cov0'], agg['census'])
    _tsv(os.path.join(d, 'EDGES.tsv'), ['fid', 'coin', 'parent_t', 'cand_t', 'side', 'weight', 'draw_index', 'own'], agg['raw_edges'])
    bal = k.D.balance([(m, kd, float(c), float(w), o) for m, kd, c, w, o in agg['balance']])
    _tsv(os.path.join(d, 'BALANCE.tsv'), ['month', 'parents_with_cov', 'matched', 'unmatched', 'smd_before', 'smd_after', 'median_cov_unmatched',
                                          'median_cov_matched', 'matches', 'share_before_30m', 'share_within_h'],
         [tuple('%.4f' % x if isinstance(x, float) else x for x in r) for r in bal])
    _json(os.path.join(d, 'COMPARISON_COVERAGE.json'), agg['coverage'])
    _json(os.path.join(d, 'UNAVAILABLE.json'), agg['unavailable'])


def write_measurements(pending, agg):
    d = os.path.join(pending, 'measurements')
    off = agg['offset_us']
    _tsv(os.path.join(d, 'OBSERVATIONS.tsv'), ['row', 'kind', 'coin', 'as_of_us', 'side', 'direction', 'day', 'known_at_us'],
         [(i, kd, c, t, s, dr, day_of_us(t), t + off) for i, (kd, c, t, s, dr) in enumerate(agg['requests'])])
    np.save(os.path.join(d, 'VALUES.npy'), agg['values'])
    _json(os.path.join(d, 'NAMES.json'), agg['names'])
    _json(os.path.join(d, 'REASONS.json'), agg['reasons'])


def grading_inputs(agg, k):
    req = agg['requests']; n = len(req); pids = agg['pids']; parents = agg['parents']
    dirs = {}
    for d in DIRECTIONS:
        ids = np.asarray([i for i, q in enumerate(req) if q[4] == d], np.int64)
        local = np.full(n, -1, np.int64); local[ids] = np.arange(len(ids))
        es = [e for e in agg['edges'] if e[3] == d]
        dirs[d] = {'ids': ids, 'coins': np.asarray([req[i][1] for i in ids]), 'delay': np.full(len(ids), 0.0 + k.S.DELAY_S),
                   'parents': local[np.asarray([p['row_ids'][d] for p in parents], np.int64)],
                   'edge_parent': np.asarray([e[0] for e in es], np.int64), 'control_ids': ['control:' + str(e[1]) for e in es],
                   'controls': local[np.asarray([e[1] for e in es], np.int64)], 'weights': np.asarray([e[2] for e in es], float)}
    month_ix = [('ALL', np.arange(len(parents), dtype=np.int64))] + \
               [(m, np.asarray([i for i, p in enumerate(parents) if p['day'][:6] == m], np.int64)) for m in agg['months']]
    key = hashlib.sha256(json.dumps([pids, [len(dirs[d]['ids']) for d in DIRECTIONS], [len(dirs[d]['weights']) for d in DIRECTIONS]]).encode()).hexdigest()[:16]
    return {'run_key': key, 'pids': pids, 'waves': agg['waves'], 'directions': dirs, 'month_ix': month_ix, 'names': agg['names']}


def write_grading(pending, agg, inputs, gres, S):
    import i2g_grade_rel1 as GR
    d = os.path.join(pending, 'grading')
    cohorts = sorted((c for g in gres for c in g['cohorts']), key=lambda c: (DIRECTIONS.index(c['direction']), c['offer_pct'], c['horizon_min']))
    names = [c['name'] for c in cohorts]
    if len(names) != len(set(names)) or len(names) != 2 * len(S.OFFERS) * len(S.HORIZONS):
        raise Refused('COHORT_CENSUS', '%d cohorts' % len(names))
    _json(os.path.join(d, 'COHORTS.json'), {'schema': 'I2G_COHORTS_V1', 'population_parents': len(agg['parents']), 'cohorts': cohorts})
    audit = {}
    for g in gres:
        audit.update(g['audit'])
    np.savez(os.path.join(d, 'PARENT_DETAIL.npz'), cohorts=np.asarray(names),
             status=np.stack([audit[n]['status'] for n in names]), parent_reach=np.stack([audit[n]['parent_reach'] for n in names]),
             control_reach=np.stack([audit[n]['control_reach'] for n in names]),
             paired_reach_gap=np.stack([audit[n]['paired_reach_gap'] for n in names]),
             unknown_eligible_mass=np.stack([audit[n]['unknown_eligible_mass'] for n in names]),
             eligible_edges=GR.static_parent_detail(inputs, 'FOLLOW')[0], eligible_mass=GR.static_parent_detail(inputs, 'FOLLOW')[1])
    for dr in DIRECTIONS[1:]:
        c2, m2 = GR.static_parent_detail(inputs, dr); c1, m1 = GR.static_parent_detail(inputs, 'FOLLOW')
        if not (np.array_equal(c1, c2) and np.array_equal(m1, m2)):
            raise Refused('DIRECTION_EDGE_MISMATCH', dr)
    ps = agg['parents']
    _tsv(os.path.join(d, 'PARENTS.tsv'), ['parent_id', 'event_id', 'coin', 't', 'side', 'day', 'wave_id', 'census_status', 'original_draw_edges',
                                         'eligible_edges', 'rule_excluded_edges', 'row_follow', 'row_fade', 'known_at_us'],
         [(p['id'], p['event_id'], p['coin'], p['as_of_us'] // US, p['side'], p['day'], p['wave_id'], p['census_status'], p['original_draw_edges'],
           p['eligible_edges'], p['rule_excluded_edges'], p['row_ids']['FOLLOW'], p['row_ids']['FADE'], p['known_at_us']) for p in ps])
    _tsv(os.path.join(d, 'GRADED_EDGES.tsv'), ['parent_index', 'control_row', 'weight', 'direction', 'draw_index'], agg['edges'])
    # the outside report's table, for every cohort (ALL slice)
    by = {c['name']: c for c in cohorts}
    lines = ['# Opportunity profile: %d parents (%s)' % (len(ps), 'idea_to_grade %s' % VERSION), '',
             'Descriptive BUILD study of opportunity after each alarm against matched control moments; not profitability, not causality.', '',
             '|Direction|Offer %|Minutes|Known parent rows|Parent reach|Paired parents|Paired reach gap|', '|---|---:|---:|---:|---:|---:|---:|']
    head = []
    for dr in DIRECTIONS:
        for o in S.OFFERS:
            for h in S.HORIZONS:
                s = by['%s_%02d_%03d' % (dr, round(o * 10), h)]['profiles'][0]['summary']
                st = s['standalone']; pa = s['paired']
                lines.append('|%s|%s|%s|%s|%s|%s|%s|' % (dr, o, h, st['rows'] - st['unknown_reach_rows'], st['reach_probability'], pa['parents'],
                                                         pa['reach_gap']))
                head.append({'direction': dr, 'offer_pct': o, 'horizon_min': h, 'parent_reach': st['reach_probability'],
                             'paired_parents': pa['parents'], 'paired_reach_gap': pa['reach_gap']})
    lines += ['', 'Comparative coverage (full parent population retained):', json.dumps(agg['coverage'], sort_keys=True), '']
    with open(os.path.join(d, 'REPORT.md'), 'x') as f:
        f.write('\n'.join(lines))
    counts = {'parents': len(ps), 'census': agg['coverage']['ALL']['census_status_counts'], 'raw_edges': len(agg['raw_edges']),
              'eligible_edges': sum(p['eligible_edges'] for p in ps), 'observations': len(agg['requests']), 'cohorts': len(cohorts),
              'profiles': sum(len(c['profiles']) for c in cohorts), 'months': agg['months']}
    return {'counts': counts, 'headline': {'table': 'grading/REPORT.md', 'cohorts': len(head)}}


def verify_run(out):
    """THE check of a published run before any value is used -> the manifest. This tool's own checks run first, on RUN.json as stored:
    status, body digest (body_sha16), run schema, the exact required-file inventory (RUN_INVENTORY), and the files on disk equal to the
    listed ones; then the shared run check (run_manifest_candidate.load_complete: S1's sealed manifest, root-file inventory and every listed
    file's bytes). Refused codes: RUN_NOT_PUBLISHED, RUN_INCOMPLETE, RUN_CHANGED_AFTER_COMMIT, RUN_SCHEMA, RUN_INVENTORY."""
    p = os.path.join(out, 'RUN.json')
    if not os.path.isdir(out) or not os.path.isfile(p):
        raise Refused('RUN_NOT_PUBLISHED', '%s has no RUN.json' % out)
    try:
        disk = json.load(open(p))
    except ValueError as e:
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: RUN.json unreadable: %s' % (out, e))
    if disk.get('status') != 'COMPLETE' or disk.get('exit_status') != 0:
        raise Refused('RUN_INCOMPLETE', '%s: status %r' % (out, disk.get('status')))
    if disk.get('body_sha16') != body_digest(disk):
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: the RUN.json body changed since the commit' % out)
    if disk.get('run_schema') != RUN_SCHEMA:
        raise Refused('RUN_SCHEMA', '%s: run schema %r, this reader reads %s' % (out, disk.get('run_schema'), RUN_SCHEMA))
    parts = disk.get('parts') if isinstance(disk.get('parts'), dict) else {}
    want = set(REQUIRED_FILES) | (set() if disk.get('detection') == 'REUSED_FOR_TEST' else set(DETECT_FILES))
    if set(parts) != want:
        raise Refused('RUN_INVENTORY', '%s: the manifest names %s, the run must hold exactly %s (missing %s, extra %s)'
                      % (out, len(parts), len(want), sorted(want - set(parts))[:5], sorted(set(parts) - want)[:5]))
    on_disk = set()
    for root, _, files in os.walk(out):
        for n in files:
            on_disk.add(os.path.relpath(os.path.join(root, n), out))
    on_disk.discard('RUN.json')
    added, missing = sorted(on_disk - set(parts)), sorted(set(parts) - on_disk)
    if added or missing:
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: files added %s, missing %s' % (out, added[:5], missing[:5]))
    check_consistency(out, disk)
    H = load_helper()
    try:
        m = H.load_complete(out, 'RUN')
    except H.RunRefused as e:
        raise Refused(e.code, str(e))
    return m


def check_consistency(out, m):
    """the published files agree with RUN.json's counts (cohorts, profiles, parents, detail arrays, measured rows): RUN_INCONSISTENT"""
    try:
        doc = json.load(open(os.path.join(out, 'grading', 'COHORTS.json'))); cohorts = doc['cohorts']
        with np.load(os.path.join(out, 'grading', 'PARENT_DETAIL.npz')) as detail:
            shape = detail['status'].shape; names = list(detail['cohorts'])
        with open(os.path.join(out, 'grading', 'PARENTS.tsv')) as f:
            n_rows = sum(1 for _ in f) - 1
        rows = np.load(os.path.join(out, 'measurements', 'VALUES.npy'), mmap_mode='r').shape[0]
        n, c = m['counts']['parents'], m['counts']['cohorts']
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Refused('RUN_INCONSISTENT', '%s: %s' % (out, e))
    bad = [x for x, ok in (('COHORTS population', doc.get('population_parents') == n), ('cohort count', len(cohorts) == c),
                           ('profiles', sum(len(q['profiles']) for q in cohorts) == m['counts'].get('profiles')), ('PARENTS rows', n_rows == n),
                           ('detail shape', shape == (c, n) and names == [q['name'] for q in cohorts]),
                           ('VALUES rows', rows == m['counts'].get('observations'))) if not ok]
    if bad:
        raise Refused('RUN_INCONSISTENT', '%s: %s disagree with RUN.json counts' % (out, bad))


def read_run(out):
    """THE consumer's read: verify_run, then (manifest, cohorts list, parent detail arrays (np.load), parents rows)"""
    m = verify_run(out)
    doc = json.load(open(os.path.join(out, 'grading', 'COHORTS.json'))); cohorts = doc['cohorts']
    detail = np.load(os.path.join(out, 'grading', 'PARENT_DETAIL.npz'))
    with open(os.path.join(out, 'grading', 'PARENTS.tsv')) as f:
        parents = list(csv.DictReader(f, delimiter='\t'))
    check_consistency(out, m)                                               # again on the files as read now (after the shared check)
    return m, cohorts, detail, parents


def main(argv=None):
    p = argparse.ArgumentParser(description='idea_to_grade: idea -> detection -> matched controls -> measurements -> grading -> RUN.json')
    p.add_argument('--idea', help='the registered idea definition (detect_v2.py format, DETECT_V1): fresh detection')
    p.add_argument('--events', help='an event list (coin, t, side[, onset_t, trigger]) instead of an idea; coverage from the PRICE index')
    p.add_argument('--events-sha16', help='the pinned sha16 of --events (refused if the file differs)')
    p.add_argument('--roster'); p.add_argument('--coins'); p.add_argument('--group'); p.add_argument('--group-file')
    p.add_argument('--first', required=True); p.add_argument('--last', required=True)
    p.add_argument('--research-window', required=True, help='FIRST:LAST, the run setting; every month must be BUILD in WINDOWS_V1')
    p.add_argument('--out', required=True); p.add_argument('--workers', type=int, default=8); p.add_argument('--max-rss-gb', type=float, default=16.0)
    p.add_argument('--lab-root', required=True, help='the lab days (the settings key LAB_DAYS)'); p.add_argument('--seed', type=int, default=20261023)
    p.add_argument('--gate', default=None, help="the feed's stop gate file (the settings key FEED_GATE); empty or not given: no gate")
    p.add_argument('--min-chunk', type=int, default=50, help='smallest parent chunk of one coin task (default 50)')
    p.add_argument('--chunk', type=int, default=0, help='TESTS: force this parent chunk size')
    p.add_argument('--detect-run', help='TESTS ONLY: grade an existing committed detector run instead of detecting (RUN.json says so)')
    p.add_argument('--allow-fixture', action='store_true', help='TESTS ONLY: accept a fixture detector run built from an outside view')
    p.add_argument('--pins', required=True, help='a pins file of this edition (paths relative to the tree root)')
    p.add_argument('--windows', default=None, help='GRADE or MONTH: the window table (gm1); required, no default')
    a = p.parse_args(argv)
    if a.events and not a.events_sha16:
        p.error('--events needs --events-sha16 (the list is pinned)')
    if sum(bool(x) for x in (a.idea, a.events, a.detect_run)) != 1:
        p.error('give exactly one input: --idea (fresh detection), --events (an event list) or --detect-run (tests only)')
    if not a.detect_run and not a.roster:
        p.error('--roster is required')
    import detect_v2 as detect
    set_gate(a.gate)
    try:
        run(a)
    except Refused as e:
        sys.stderr.write('REFUSED %s\n' % e); sys.exit(2)
    except detect.Refusal as e:                                           # the detector's own admission (roster, selector, definition)
        sys.stderr.write('REFUSED DETECT_%s\n' % e); sys.exit(2)


if __name__ == '__main__':
    main()
