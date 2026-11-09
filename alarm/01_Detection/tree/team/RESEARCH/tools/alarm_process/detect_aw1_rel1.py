#!/usr/bin/env python3
# detect_aw1_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
# release folder only"): a new edition for the clean release. Old file: alarm_process/detect_aw1.py f03254fd5420e56b, never edited. It is
# detect_v2.py 97a822a20e08088d (detect.py with its paths changed: --lab-root required, --gate, alarm_design_v3) with detect_aw1.py's
# aw1 change and nothing else (the research window CLASSES from alarm_process/WINDOWS_ALARM_V1.tsv, its sha16 checked). detect_aw1.py's
# header follows, then detect_v2.py's text.
# detect_aw1.py, aw1 (STRATEGY 28 Oct 2026, ALARM_DESIGN kit; TEST, NOT REVIEWED; the owner 28 Oct 2026: Mar-May for the alarm agents only): detect.py 5ced7c1a40356a7f copied unchanged except the research window CLASSES, read from
# alarm_process/WINDOWS_ALARM_V1.tsv (BUILD 1 Sep 2025-31 May 2026, BLIND from 1 Jun 2026; its sha16 checked) instead of freeze_judge WINDOWS_V1.
"""idea_to_grade/detect_v2.py: THE DETECTION STAGE of idea_to_grade, edition 2 (new edition by SCOUT for the clean release, 30 Oct 2026).
Owner STRATEGY/LEAD. Old file: idea_to_grade/detect.py 5ced7c1a40356a7f (DETECT_V1, release idea_to_grade V2_3_1), never edited.
the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only" (CLEAN_RELEASE_V1 section 6). Edition 2
changes only where things are; the detection, its outputs and its refusals are detect.py's, and VERSION stays 'DETECT_V1', so the same
inputs give the same EVENTS.tsv byte for byte:
  --lab-root  required: no machine default (the settings key LAB_DAYS). run(lab_root=) likewise: no lab_root and no test reader is
              REFUSED LAB_ROOT_REQUIRED before anything is read or written.
  --gate      the feed's stop gate file (the settings key FEED_GATE). Given, it is read exactly as detect.py read the team's gate through
              labcore.jobgate.state (first line RUN, else REFUSED GATE_NOT_RUN; a missing or unreadable file reads PAUSE), at the start,
              in every worker and before the commit. Empty or not given: no gate (a machine without the feed). run(gate=) likewise.
              From a job, pass it as one word even when empty: --gate=<FEED_GATE> or --gate "<FEED_GATE>".
  The engine: alarm_design_v3.py, the new edition of alarm_design_v2.py (the same rules; no machine default), never the old file.
  Unchanged on purpose: VERSION, the EVENTS.tsv and COVERAGE.tsv headers and the manifest's tool and version fields are detect.py's, so
  readers and byte comparisons see one format; the edition that ran is named in the manifest's code_sha16 (its path and sha16).
The rest of this text is detect.py's (i2g_detector for STRATEGY/LEAD, 25 Oct 2026; owner 11:59Z "finish the tool and launch it as soon
as possible"). One generic function and one command: a registered idea definition (alarm_design format: any
metric, any clock, its conditions, onset, refractory, side), a roster, a selector (all coins, a set, a named group) and first/last days in,
ONE committed detector run out (INTERFACE_V1.md, section DETECT).

  python3 detect_v2.py --definition D.json --roster ROSTER --first YYYYMMDD --last YYYYMMDD --research-window FIRST:LAST --out OUT_DIR
                    --lab-root LAB_DAYS [--gate FEED_GATE] [--coins ALL|A,B,C | --group-file F.tsv --group NAME] [--workers 8]
  python:  detect_v2.run(definition, first, last, out_dir, roster, coins='ALL', group=None, group_file=None, workers=8, lab_root=LAB_DAYS,
                         research_window=(FIRST, LAST) or 'FIRST:LAST', gate=None or FEED_GATE)
           -> absolute path of OUT_DIR/DETECT_RUN.json (the worker pool is joined before it returns; workers die with their parent)
  Exit 0 = COMPLETE (one JSON line); exit 2 = REFUSED <CODE>: detail (nothing committed); exit 3 = FAILED (an unexpected error).
RESEARCH WINDOW (required, no default, no date in the code): every month of FIRST..LAST must be a BUILD month of labcore.gates' window
table (freeze_judge WINDOWS_V1) and pass lab3/law.py, and first..last must lie inside it; else REFUSED before any read. NO day outside the
window is ever opened, support days included: the 00:00 step of the window's first day has an UNKNOWN predecessor (D-1 23:59 is outside),
so an onset at the window's first 00:00 cannot fire, and warm-up days before the window are not read (history starts at the window).

SEMANTICS are the outside detector's (DEV2 detector_vector_v1 run_speed_v11 + source_runtime_speed_v11 + native_raw_clock_v6), which are
the lab engine's (team/RESEARCH/tools/alarm_design/alarm_design_v2.py, imported, never copied):
- every input value comes through the ONE lab3 reader, Days(root, 'research'); a value is KNOWN only when it is finite AND e == 0, a >= 0,
  o >= 0 and k (when the part lists k) is set and <= the column time (the outside strict source's quality rule); else it is UNKNOWN (NaN).
  lab3's documented absence (NotBuilt) reads as a whole UNKNOWN code-day; every other reader error stops the run (nothing swallowed).
- a CLOCK column j of day D is the value as known at D0 + j x step (lab3 as-of); the alarm is checked on its grid (grid_s) at D0 + k x grid,
  which takes native column floor(k x grid / step) (the engine's to_base, then its grid rows).
- conditions: the engine's cond_mask; shared/claim masks and KNOWN = every shared condition known AND the claim decided (all claim
  conditions known, or one known false) (engine masks); side = the engine's side_of (sign of the side input x sign; 0 = no fire).
- a fire at grid step k of D: shared AND claim hold, side != 0, and (onset rule) the step before (k-1; for D's first step the last step of
  D-1, read from D-1's data) is KNOWN and not all true; refractory: a fire within refractory_s after the coin's last ACCEPTED fire is dropped
  (engine find_fires; the chain starts warm-up days before first, as the engine's run does). Nothing after day D is read for day D.
- per day only the coins the day's PRICE part lists are evaluated (the engine's src.coins and the outside roster availability rule).
TWO EXECUTION PATHS, ONE SEMANTICS: GRID (every input op pointwise: raw, market and pointwise transforms; evaluated on the grid only, the
outside's native fast path generalised) and BASE (any other op: window, percentile, event, price, hour ops; the engine's own Ctx and
find_fires on its 5 s clock, a day with D-1 beside it). test_detect.py checks GRID == BASE on real data.
SPEED (the lab's fast pattern, event_profile clock_series/run_parallel): each code-day is read ONCE for all the run's coins, the rule is
evaluated vectorised over coins x steps, days are split into contiguous chunks over at most 8 processes (nice 10, one numeric thread);
refractory and the warm-up seeds are applied after the merge, in time order (the engine's rule; candidate fires do not depend on it);
percentile history is rebuilt per chunk by ENTRIES (each coin's last keep_days listed days), never calendar days, so every coin's answer
equals the serial run's; a rule whose history source depends on history runs in one process (DETECT_RUN.json parallel.mode says which).
NO DATE CONSTANT: the days are the caller's; lab3/law.py inside the reader is the only seal (a refused requested day is a REFUSED cell).
The definition's own declared window bounds first/last (the outside DEFINITION_WINDOW rule).
OUTPUTS (INTERFACE_V1.md): OUT_DIR/EVENTS.tsv, COVERAGE.tsv, then DETECT_RUN.json LAST with status COMPLETE. OUT_DIR must not exist."""
import argparse, csv, datetime as dt, hashlib, importlib.util, io, json, os, re, resource, sys, time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent                                                    # team/RESEARCH/tools
F_ROOT = TOOLS.parents[2]                                              # forensics
ENGINE_PATH = TOOLS / 'alarm_design' / 'alarm_design_v3.py'
WINDOWS_ALARM = TOOLS / 'alarm_process' / 'WINDOWS_ALARM_V1.tsv'; WINDOWS_ALARM_SHA16 = '69c3327ebf4e15a1'   # aw1: the alarm kit's window classes
CODE_DIR = F_ROOT / 'team' / 'LAB3' / 'code'
# no LAB_ROOT: the lab days are the caller's (--lab-root, the settings key LAB_DAYS); edition 2 names no machine path
VERSION = 'DETECT_V1'
MAX_WORKERS = 8                                                        # the team process budget
WORKER_RSS_CAP = 2 * 1024 ** 3                                         # 16 GiB / 8 workers
INT64_MIN = np.iinfo(np.int64).min
US = 1_000_000
THREAD_VARS = ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS',
               'NUMBA_NUM_THREADS')
POINTWISE = {'raw', 'market', 'known', 'pospart', 'negpart', 'ratio', 'mul', 'add', 'sub', 'abs', 'pick', 'maxof', 'neg', 'sign'}
OTHER_OPS = {'price', 'sum', 'max', 'prior_max', 'prior_min', 'change', 'lag', 'accel', 'hour_block', 'trail_pct', 'own_pct',
             'ev_since', 'ev_side', 'ev_value', 'ext_since_ev'}
HIST_OPS = {'trail_pct', 'own_pct'}
OP_FIELDS = {'raw': ('code',), 'market': ('code',), 'price': (), 'known': ('of',), 'pospart': ('of',), 'negpart': ('of',),
             'abs': ('of',), 'neg': ('of',), 'sign': ('of',), 'ratio': ('a', 'b'), 'mul': ('a', 'b'), 'add': ('a', 'b'),
             'sub': ('a', 'b'), 'maxof': ('a', 'b'), 'pick': ('if', 'pos', 'neg'), 'sum': ('of', 'w_s'), 'max': ('of', 'w_s'),
             'prior_max': ('of', 'w_s'), 'prior_min': ('of', 'w_s'), 'change': ('of', 'w_s'), 'lag': ('of', 'w_s'),
             'accel': ('of', 'n'), 'hour_block': ('h',), 'trail_pct': ('of', 'w_s', 'q'), 'own_pct': ('of', 'q'),
             'ev_since': ('events',), 'ev_side': ('events',), 'ev_value': ('events', 'of'), 'ext_since_ev': ('events', 'of')}
REQUIRED_FILES = ('COVERAGE.tsv', 'EVENTS.tsv')
EVENT_OPS = {'ev_since', 'ev_side', 'ev_value', 'ext_since_ev'}
COIN_RE = re.compile(r'^[A-Za-z0-9_]+$')
STATUSES = ('PRESENT', 'NOT_LISTED', 'NOT_BUILT', 'HOLE', 'REFUSED')
TEST_HOLD_ENV = 'I2G_DETECT_TEST_HOLD'                                 # tests only: '<seconds>:<folder>' holds each worker (hard-kill test)

for _p in (str(CODE_DIR), str(TOOLS), str(TOOLS / 'event_profile')):
    if _p not in sys.path:
        sys.path.insert(0, _p)


class Refusal(ValueError):
    """a typed refusal of the run (CODE: detail); nothing is committed"""
    def __init__(self, code, detail=''):
        self.code = code; self.detail = detail; super().__init__('%s: %s' % (code, detail) if detail else code)

    def __reduce__(self):                                              # a worker's refusal keeps its code across the process boundary
        return (Refusal, (self.code, self.detail))


_ENGINE = {}


def engine():
    """the lab engine alarm_design_v2, imported once by path (never copied, never an AD_HOME mutant)"""
    if 'A' not in _ENGINE:
        if os.environ.get('AD_HOME'):
            raise Refusal('AD_HOME_OVERRIDE_REFUSED', 'the engine must be the released one')
        sp = importlib.util.spec_from_file_location('i2g_alarm_design_v2', str(ENGINE_PATH))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _ENGINE['A'] = m
    return _ENGINE['A']


def sha16_file(p):
    from labcore import ids
    return ids.sha16_file(str(p))


def sha16_text(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def rss_bytes():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(r if sys.platform == 'darwin' else r * 1024)


def gate_is_run(gate):
    """the feed's stop gate. gate None or '': no gate, RUN (a machine without the feed). A gate file: labcore.jobgate.state(gate) == 'RUN',
    exactly detect.py's read of the team's gate (its first line; a missing or unreadable file reads PAUSE)"""
    if not gate:
        return True
    from labcore import jobgate
    return jobgate.state(gate) == 'RUN'


# ---------------------------------------------------------------- the definition
def ops_of(d):
    return {s['op'] for s in d['inputs'].values()}


def load_definition(path):
    """the engine's parser (A.load_def) plus this stage's admission: known ops, operands bound, fire rule typed, metric briefs (labcore:
    STOP, CAUTION and UNPROVEN inputs refused, as the outside's metric reading refusal). -> (d, info)"""
    A = engine()
    p = Path(path).resolve()
    if not p.is_file():
        raise Refusal('DEFINITION_MISSING', str(p))
    try:
        d = A.load_def(str(p))
    except (ValueError, KeyError, TypeError) as e:
        raise Refusal('DEFINITION_INVALID', str(e))
    if d['grid_s'] > 86400:
        raise Refusal('GRID_RANGE', 'grid_s %d is longer than a day' % d['grid_s'])
    names = set(d['inputs'])
    for nm, s in d['inputs'].items():
        if not isinstance(s, dict) or s.get('op') not in POINTWISE | OTHER_OPS:
            raise Refusal('UNSUPPORTED_OP', '%s: %r' % (nm, s))
        if s['op'] in ('raw', 'market') and not isinstance(s.get('code'), str):
            raise Refusal('DEFINITION_INVALID', 'input %s needs a code' % nm)
        if s['op'] in EVENT_OPS and not (d.get('events', {}).get(s.get('events')) and d.get('events_cover', {}).get(s.get('events'))):
            raise Refusal('EVENT_BINDING', 'input %s needs events and events_cover for %r' % (nm, s.get('events')))

    def operand(v, where):
        if isinstance(v, str):
            if v not in names:
                raise Refusal('UNKNOWN_INPUT', '%s: %r' % (where, v))
        elif isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v):
            raise Refusal('FINITE_CONSTANT_REQUIRED', '%s: %r' % (where, v))
    for nm, s in d['inputs'].items():                                 # every operand and op field inside the input expressions
        for k in OP_FIELDS[s['op']]:
            if k not in s:
                raise Refusal('OP_FIELD_MISSING', 'input %s (%s) needs %s' % (nm, s['op'], k))
        for k in ('of', 'a', 'b', 'if', 'pos', 'neg'):
            if k in s:
                operand(s[k], '%s.%s' % (nm, k))
        for k in ('w_s', 'n', 'h', 'q'):
            if k in s and (isinstance(s[k], bool) or not isinstance(s[k], (int, float)) or not np.isfinite(s[k]) or s[k] < 0
                           or (k != 'q' and s[k] <= 0) or (k == 'q' and s[k] > 100)):
                raise Refusal('OP_FIELD_INVALID', 'input %s: %s = %r' % (nm, k, s[k]))
    state = {}

    def visit(nm, path):                                              # an input that depends on itself never terminates
        if state.get(nm) == 2:
            return
        if state.get(nm) == 1:
            raise Refusal('INPUT_CYCLE', ' -> '.join(path + [nm]))
        state[nm] = 1
        for k in ('of', 'a', 'b', 'if', 'pos', 'neg'):
            v = d['inputs'][nm].get(k)
            if isinstance(v, str):
                visit(v, path + [nm])
        state[nm] = 2
    for nm in d['inputs']:
        visit(nm, [])
    for c in d['conditions']:
        operand(c['lhs'], c['name']); operand(c['rhs'], c['name'])
    f = d['fire']
    if not isinstance(f.get('onset', True), bool):
        raise Refusal('FIRE_RULE', 'onset must be true or false')
    r = f.get('refractory_s', 0)
    if isinstance(r, bool) or not isinstance(r, int) or r < 0:
        raise Refusal('FIRE_RULE', 'refractory_s must be a whole number of seconds >= 0')
    s = f.get('side')
    if not isinstance(s, dict) or 'input' not in s or s.get('sign', 1) not in (-1, 1) or isinstance(s.get('sign', 1), bool):
        raise Refusal('FIRE_RULE', 'side must be {input, sign -1 or 1}')
    operand(s['input'], 'fire.side')
    win = d.get('window') or {}
    if not isinstance(win, dict):
        raise Refusal('DEFINITION_INVALID', 'window must be {first, last}')
    check_days(win.get('first'), win.get('last'), 'DEFINITION_INVALID')     # 8-digit real days, first <= last ('2025091' refused)
    event_pins = {}
    if ops_of(d) & EVENT_OPS:
        try:
            event_pins = A.sources_of(d)[1]
        except (OSError, ValueError, KeyError, IndexError) as e:
            raise Refusal('EVENT_LIST_INVALID', str(e))
    codes = list(dict.fromkeys(s['code'] for s in d['inputs'].values() if s['op'] in ('raw', 'market')))
    from labcore import briefs
    try:
        br = briefs.refuse_inputs(codes, decision_codes=codes)
    except ValueError as e:
        raise Refusal('METRIC_READING_REFUSAL', str(e))
    path = 'GRID' if ops_of(d) <= POINTWISE else 'BASE'
    info = {'path': str(p), 'sha16': d['_sha16'], 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'id': d['id'],
            'version': d.get('version'), 'grid_s': d['grid_s'], 'execution_path': path,
            'raw_codes': [s['code'] for s in d['inputs'].values() if s['op'] == 'raw'],
            'market_codes': [s['code'] for s in d['inputs'].values() if s['op'] == 'market'],
            'fire': {'onset': f.get('onset', True), 'refractory_s': r, 'side': {'input': s['input'], 'sign': s.get('sign', 1)}},
            'conditions': d['conditions'], 'window': {'first': win['first'], 'last': win['last']},
            'briefs': {c: {'flag': b['flag'], 'status': b['status']} for c, b in br.items()}, 'event_lists': event_pins}
    return d, info


def trigger_of(d):
    """the definition's metric code(s) for the trigger column: its raw and market codes in input order ('+' joined)"""
    codes = list(dict.fromkeys(s['code'] for s in d['inputs'].values() if s['op'] in ('raw', 'market')))
    return '+'.join(codes) if codes else d['id']


# ---------------------------------------------------------------- the population
def load_roster(path):
    """a roster: JSON with a 'coins' list (e.g. ROSTER_BUILD.json) or a TSV with a 'coin' column -> (coins in order, sha16)"""
    p = Path(path).resolve()
    if not p.is_file():
        raise Refusal('ROSTER_MISSING', str(p))
    try:
        if p.suffix == '.json':
            doc = json.loads(p.read_text())
            coins = doc.get('coins') if isinstance(doc, dict) else None
        else:
            with p.open() as f:
                rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
            coins = [(r.get('coin') or '').strip() for r in rows] if rows and 'coin' in rows[0] else None
    except (OSError, ValueError, UnicodeDecodeError) as e:
        raise Refusal('ROSTER_INVALID', '%s: %s' % (p, e))
    if not isinstance(coins, list) or not coins or any(not isinstance(c, str) or not COIN_RE.match(c) or c == 'MARKET' for c in coins) \
            or len(set(coins)) != len(coins):
        raise Refusal('ROSTER_INVALID', '%s: needs a non-empty list of distinct coin names' % p)
    return list(coins), sha16_file(p)


def select_coins(roster, coins='ALL', group=None, group_file=None):
    """the selector: all roster coins ('ALL' / None), an explicit set ('A,B' or a list), or a named group of a group file (TSV with a
    group or sector column and a coin column, the lab's convention, e.g. team/RESEARCH/tools/cause_label/SECTORS_V1.tsv). Unknown coins,
    unknown groups and a group with no roster member refuse; group members outside the roster are listed in the record, never silent.
    -> (coins in roster order, record)"""
    if group is not None or group_file is not None:
        if coins not in (None, 'ALL'):
            raise Refusal('BAD_SELECTION', 'give coins or a group, not both')
        if not group or not group_file or not Path(group_file).is_file():
            raise Refusal('BAD_SELECTION', 'a group needs group and an existing group_file')
        try:
            with open(group_file) as f:
                rows = list(csv.reader((l for l in f if not l.startswith('#')), delimiter='\t'))
        except (OSError, UnicodeDecodeError) as e:
            raise Refusal('BAD_SELECTION', '%s: %s' % (group_file, e))
        h = [x.strip() for x in rows[0]] if rows else []
        gcol = 'group' if 'group' in h else 'sector' if 'sector' in h else None
        if gcol is None or 'coin' not in h:
            raise Refusal('BAD_SELECTION', '%s: needs columns group (or sector) and coin' % group_file)
        gi, ci = h.index(gcol), h.index('coin')
        members = sorted({r[ci].strip() for r in rows[1:] if len(r) > max(gi, ci) and r[gi].strip() == group})
        if not members:
            raise Refusal('UNKNOWN_GROUP', 'group %s is not in %s' % (group, group_file))
        chosen = [c for c in roster if c in set(members)]
        if not chosen:
            raise Refusal('EMPTY_GROUP', 'group %s has no member in the roster' % group)
        return chosen, {'kind': 'group', 'group': group, 'group_file': str(Path(group_file).resolve()),
                        'group_file_sha16': sha16_file(group_file), 'members': members, 'selected': chosen,
                        'members_not_in_roster': sorted(set(members) - set(roster))}
    if coins is None or (isinstance(coins, str) and coins.strip().upper() == 'ALL'):
        return list(roster), {'kind': 'all', 'selected': list(roster)}
    want = [c.strip() for c in coins.split(',')] if isinstance(coins, str) else [str(c).strip() for c in coins]
    if not want or any(not c or not COIN_RE.match(c) for c in want) or len(set(want)) != len(want):
        raise Refusal('INVALID_COIN', 'coins %r' % (coins,))
    unknown = sorted(set(want) - set(roster))
    if unknown:
        raise Refusal('UNKNOWN_COIN', 'not in the roster: %s' % ','.join(unknown))
    chosen = [c for c in roster if c in set(want)]
    return chosen, {'kind': 'coins', 'selected': chosen}


def check_days(first, last, code='BAD_DAYS'):
    import event_profile as EP                                         # the shared day check of the event_* tools
    try:
        return EP.check_days(first, last)
    except (ValueError, TypeError) as e:
        raise Refusal(code, str(e))


def admit_research_window(window, first, last):
    """the caller's research window (a run setting; no default, no date constant) -> (lo, hi). REFUSED unless both ends are real days,
    every month lo..hi is a BUILD month of labcore.gates' window table and passes lab3/law.py, and first..last lies inside it"""
    if window is None or window == '':
        raise Refusal('RESEARCH_WINDOW_REQUIRED', 'give research_window FIRST:LAST (the BUILD months this run may read)')
    parts = window.split(':') if isinstance(window, str) else list(window)
    if len(parts) != 2:
        raise Refusal('RESEARCH_WINDOW', 'FIRST:LAST, got %r' % (window,))
    lo, hi = check_days(parts[0], parts[1], 'RESEARCH_WINDOW')
    from labcore import gates
    from lab3 import law
    if hashlib.sha256(WINDOWS_ALARM.read_bytes()).hexdigest()[:16] != WINDOWS_ALARM_SHA16:   # aw1
        raise Refusal('ALARM_WINDOWS_CHANGED', '%s is not sha16 %s' % (WINDOWS_ALARM, WINDOWS_ALARM_SHA16))
    wins = gates.windows(str(WINDOWS_ALARM)); m = lo[:6]   # aw1: the alarm kit's classes (WINDOWS_V1 unchanged)
    while m <= hi[:6]:
        try:
            cls = gates.window_of(m, wins)
        except PermissionError as e:
            raise Refusal('RESEARCH_WINDOW_NOT_BUILD', str(e))
        if cls != 'BUILD':
            raise Refusal('RESEARCH_WINDOW_NOT_BUILD', 'month %s is in the %s window' % (m, cls))
        why = law.research_refusal(gates.month_last_day(m))
        if why:
            raise Refusal('RESEARCH_WINDOW_SEALED', 'month %s: %s' % (m, why))
        m = '%04d%02d' % (int(m[:4]) + (m[4:] == '12'), 1 if m[4:] == '12' else int(m[4:]) + 1)
    if not lo <= first <= last <= hi:
        raise Refusal('SELECTION_OUTSIDE_WINDOW', '%s..%s is not inside the research window %s..%s' % (first, last, lo, hi))
    return lo, hi


# ---------------------------------------------------------------- reading (the one lab3 reader, each code-day once for all coins)
class DayReader:
    """per worker: lab3 Days(root, 'research'); each (code, day) read ONCE for all the run's coins and quality gated; at most the
    current and previous day kept. Records the fingerprint (index sha16) of every part read."""

    def __init__(self, R, coins, window):
        self.R = R; self.coins = list(coins); self.pos = {c: i for i, c in enumerate(self.coins)}
        self.cache = {}; self.sources = {}; self.read_s = 0.0; self.reads = 0
        self.lo, self.hi = window; self.outside = set()

    def inside(self, day):
        """the research window guard: a day outside it is never opened (it reads as UNKNOWN, counted in outside)"""
        if self.lo <= day <= self.hi:
            return True
        self.outside.add(day)
        return False

    def keep(self, days):
        for k in [k for k in self.cache if k[1] not in days]:
            del self.cache[k]

    def note(self, day, part, sha):
        self.sources['day=%s/%s' % (day, part)] = sha

    def price_coins(self, day):
        """the coins the day's PRICE part lists; None when lab3 says NotBuilt (Refused and any other error propagate)"""
        import clock_series as CS
        key = ('PRICE', day)
        if not self.inside(day):
            return None
        if key not in self.cache:
            t0 = time.perf_counter()
            try:
                ix = self.R.index(day, 'PRICE')
                self.cache[key] = set(ix['coins']); self.note(day, 'PRICE', ix['_sha16'])
            except Exception as e:                                     # noqa: BLE001 (re-raised unless the documented absence)
                if not CS.is_absence(e):
                    raise
                self.cache[key] = None
            self.read_s += time.perf_counter() - t0
        return self.cache[key]

    def gated(self, code, day, rows=None):
        """(v (coins, n) float with UNKNOWN = NaN, step s, listed bool (coins), part) of code on day for the run's coins (or rows=['MARKET']);
        None when lab3 says NotBuilt. Known = finite v AND e == 0 AND a >= 0 AND o >= 0 AND k set and <= the column time (fields the
        part lists)."""
        import clock_series as CS
        who = tuple(rows) if rows is not None else None
        key = (code, day, who)
        if not self.inside(day):
            return None
        if key in self.cache:
            return self.cache[key]
        t0 = time.perf_counter(); coins = list(who) if who is not None else self.coins
        try:
            pt = self.R.part_of(code, day)
        except Exception as e:                                         # noqa: BLE001
            if not CS.is_absence(e):
                raise
            self.cache[key] = None; self.read_s += time.perf_counter() - t0
            return None
        ix = self.R.index(day, pt); desc = ix['readings'][code]; self.note(day, pt, ix['_sha16'])
        if desc.get('kind', 'CLOCK') != 'CLOCK':
            raise Refusal('CLOCK_REQUIRED', '%s %s is a %s code' % (code, day, desc.get('kind')))
        step = int(self.R.step(code, day))
        if step < 5 or step % 5 or 86400 % step:
            raise Refusal('NATIVE_CLOCK', '%s %s: step %s is not on the 5 s clock' % (code, day, step))
        v = np.array(self.R.read(code, 'v', [day], coins)[0], dtype=float)
        if v.shape != (len(coins), 86400 // step):
            raise Refusal('CLOCK_SHAPE', '%s %s: block %s for %d coins at step %d' % (code, day, v.shape, len(coins), step))
        valid = np.isfinite(v); files = desc.get('files') or {}
        for fld in ('e', 'a', 'o', 'k'):
            if fld not in files:
                continue
            q = self.R.read(code, fld, [day], coins)[0]
            if fld == 'e':
                valid &= q == 0
            elif fld in ('a', 'o'):
                valid &= q >= 0
            else:
                times = engine().day0(day) * US + np.arange(q.shape[1], dtype=np.int64) * step * US
                valid &= (q != INT64_MIN) & (q <= times[None, :])
        v[~valid] = np.nan
        have = set(ix.get('coins') or [])
        listed = np.array([c in have for c in coins], bool)
        out = (v, step, listed, pt)
        self.cache[key] = out; self.reads += 1; self.read_s += time.perf_counter() - t0
        return out


def day_steps(grid_s):
    """the day's decision offsets: every k x grid_s < 86400 (a grid that does not divide the day keeps its last step, e.g. 70 s ->
    1235 steps, the last at 23:59:40), exactly the engine's find_fires rows arange(i0, 2 i0, grid/5)"""
    return np.arange(0, 86400, grid_s, dtype=np.int64)


def sample_grid(v, step, grid_s):
    """native columns at the grid times D0 + k x grid (column floor(k x grid / step); the engine's to_base then its grid rows)"""
    return v[:, day_steps(grid_s) // step]


def sample_predecessor(v, step, grid_s):
    """D-1's native column at D0 - grid (the engine's onset row i0 - grid/5 on D-1: floor((86400 - grid) / step)), shape (n, 1)"""
    return v[:, [(86400 - grid_s) // step]]


# ---------------------------------------------------------------- evaluation: GRID path (pointwise rules)
def grid_ctx_class(A):
    class GridCtx(A.Ctx):
        """the engine's Ctx on the decision grid only: column 0 = D-1's last grid step (the predecessor), 1..G = D's grid steps; the
        engine's op registry (pointwise ops), cond_mask and side_of run on it unchanged"""
        def __init__(self, dfn, coins, t, values, market):
            self.d = dfn; self.coins = coins; self.t = t; self.memo = {}; self.mirror = False; self.hist = {}
            self.need = None; self.read_last = None; self.i0 = 1; self.shape = (len(coins), len(t))
            self._values = values; self._market = market

        def code(self, code):
            return self._values[code]

        def market(self, code):
            return np.broadcast_to(self._market[code], self.shape).copy()

        def price(self):
            raise Refusal('GRID_PATH_OP', 'price is a BASE path op')

        def val(self, ref):
            return self.get(ref) if isinstance(ref, str) else np.full(self.shape, float(ref))
    return GridCtx


def eval_grid(A, d, rd, day, coins_idx):
    """one day, GRID path -> (t (G+1,), predicate, known, side) arrays (n, G+1) over the coins in coins_idx (rows of rd.coins)"""
    grid = d['grid_s']; G = len(day_steps(grid)); prev = A.shift(day, -1); n = len(coins_idx)
    t = A.day0(day) + np.r_[np.int64(-grid), day_steps(grid)]
    values, market = {}, {}
    for s in d['inputs'].values():
        if s['op'] == 'raw' and s['code'] not in values:
            col = []
            for dd in (prev, day):
                x = rd.gated(s['code'], dd)
                col.append(np.full((n, 1 if dd == prev else G), np.nan) if x is None else
                           (sample_predecessor if dd == prev else sample_grid)(x[0][coins_idx], x[1], grid))
            values[s['code']] = np.concatenate(col, axis=1)
        elif s['op'] == 'market' and s['code'] not in market:
            col = []
            for dd in (prev, day):
                x = rd.gated(s['code'], dd, rows=['MARKET'])
                col.append(np.full((1 if dd == prev else G,), np.nan) if x is None else
                           (sample_predecessor if dd == prev else sample_grid)(x[0], x[1], grid)[0])
            market[s['code']] = np.concatenate(col)
    ctx = grid_ctx_class(A)(d, [rd.coins[i] for i in coins_idx], t, values, market)
    sh = np.ones(ctx.shape, bool); cl = sh.copy(); shk = sh.copy(); clk = sh.copy(); clf = np.zeros_like(sh)
    shf = np.zeros_like(sh)
    for c in d['conditions']:                                         # the engine's masks combination (no slow op on this path)
        m, ok = A.cond_mask(ctx, c)
        if c['role'] == 'shared':
            sh &= m; shk &= ok; shf |= ok & ~m
        else:
            cl &= m; clk &= ok; clf |= ok & ~m
    kn = A.conditions_known(shk, shf, clk, clf); side = A.side_of(ctx)
    return t, sh & cl, kn, side


def fires_grid(d, t, allm, kn, side):
    """candidate fires (row i, column j >= 1) of the engine's find_fires before refractory: all true, side != 0, onset: step before
    KNOWN and not all true"""
    hit = allm[:, 1:] & (side[:, 1:] != 0)
    if d['fire'].get('onset', True):
        hit &= ~allm[:, :-1] & kn[:, :-1]
    i, j = np.nonzero(hit)
    return [(int(a), int(b) + 1) for a, b in zip(i, j)]


# ---------------------------------------------------------------- evaluation: BASE path (the engine's own Ctx and find_fires)
def base_source_class(A):
    class GatedSource(A.LabSource):
        """the engine's LabSource fed by the DayReader: values quality gated, NotBuilt = NaN, every other error propagates"""
        def __init__(self, rd, events):
            self.rd = rd; self.R = rd.R; self._c = {}; self.events = events or {}; self.used = {}
            self.LB = None

        def code(self, code, day, coins):
            x = self.rd.gated(code, day)
            if x is None:
                return np.full((len(coins), A.NB), np.nan)
            return A.to_base(x[0][[self.rd.pos[c] for c in coins]], x[1])

        def market(self, code, day):
            x = self.rd.gated(code, day, rows=['MARKET'])
            return np.full(A.NB, np.nan) if x is None else A.to_base(x[0], x[1])[0]

        def price(self, day, coins):
            """PRICE through the canonical lab3 reader (lab3.bins.read_bins) BEFORE the engine's price: only lab3's NotBuilt (no PRICE
            part that day) reads as UNKNOWN; a corrupt block, a missing frame file, the seal and every other error stop the run (the
            engine's own price swallows every exception: backlog request to ALARM). The engine's as-of math then runs on those bins."""
            if not self.rd.inside(day):
                return np.full((len(coins), A.NB), np.nan)
            from lab3 import bins as LB, days as LD
            key = ('PRICE', day, tuple(coins))
            if key not in self._c:
                try:
                    off, arrays = LB.read_bins(self.R, day, list(coins))
                except LD.NotBuilt:
                    self._c[key] = np.full((len(coins), A.NB), np.nan)
                    return self._c[key]

                class Bound:                                          # serves exactly the bins read above, nothing else
                    @staticmethod
                    def read_bins(R, which, cs):
                        if which != day or list(cs) != list(coins):
                            raise Refusal('PRICE_BINDING', '%s %s' % (which, cs))
                        return off, arrays
                self.LB = Bound
                try:
                    A.LabSource.price(self, day, coins)
                finally:
                    self.LB = None
            return self._c[key]
    return GatedSource


def no_refractory(d):
    x = dict(d); x['fire'] = dict(d['fire'], refractory_s=0)
    return x


# ---------------------------------------------------------------- one chunk of days (one worker)
def work_chunk(job):
    """one contiguous chunk: warm days (evaluated for history / refractory seeds only) then its own days -> candidate fires, cells,
    fingerprints, timings. Runs in a worker process (or in-process for workers=1)."""
    t_start = time.perf_counter()
    try:
        os.setpriority(os.PRIO_PROCESS, 0, max(10, os.getpriority(os.PRIO_PROCESS, 0)))
    except OSError:
        pass
    if not gate_is_run(job['gate']):
        raise Refusal('GATE_NOT_RUN', 'BACKFILL_GATE first line is not RUN')
    A = engine()
    from lab3 import days as LD, law
    d = A.load_def(job['definition'])
    if d['_sha16'] != job['definition_sha16']:
        raise Refusal('DEFINITION_CHANGED', job['definition'])
    hold = os.environ.get(TEST_HOLD_ENV)
    if hold:                                                          # tests only: hold the worker so a test can kill its parent
        secs, folder = hold.split(':', 1)
        Path(folder, 'worker_%d.pid' % os.getpid()).write_text(str(os.getpid())); time.sleep(float(secs))
    R = job.get('reader') or LD.Days(job['lab_root'], 'research')
    coins = job['coins']; rd = DayReader(R, coins, tuple(job['window'])); grid = d['grid_s']; G = len(day_steps(grid))
    path = job['path']; onset_seed = job['seed_days']
    raw_codes = list(dict.fromkeys(s['code'] for s in d['inputs'].values() if s['op'] == 'raw'))
    mkt_codes = list(dict.fromkeys(s['code'] for s in d['inputs'].values() if s['op'] == 'market'))
    d0 = no_refractory(d); keep = A.keep_days(d); hist = {}
    events_src = A.sources_of(d)[0] if ops_of(d) & EVENT_OPS else {}
    src = base_source_class(A)(rd, events_src) if path == 'BASE' else None
    fires, cells = [], []; eval_s = 0.0; cand = 0
    own = set(job['days']); warm_days = list(job['warm_days']); only = {}
    if job.get('warm_mode') == 'ENTRIES':                             # the coin's last keep listed days in [serial start, chunk start)
        want = {c: job['keep'] for c in coins}; dd = A.shift(job['days'][0], -1)
        while dd >= job['serial_start'] and any(want.values()):
            pc = rd.price_coins(dd) or set()
            for c in coins:
                if want[c] and c in pc:
                    only.setdefault(dd, set()).add(c); want[c] -= 1
            dd = A.shift(dd, -1)
        warm_days = sorted(only)
    for day in warm_days + job['days']:
        rd.keep({day, A.shift(day, -1)})
        if src is not None:                                           # the engine source's own cache (price) keeps D-1 and D only
            src._c = {k: v for k, v in src._c.items() if len(k) > 1 and k[1] in (day, A.shift(day, -1))}
        if day in own:
            why = law.research_refusal(day)                               # the reader's seal, asked before any read of the day
            if why:
                cells += [(c, day, 'REFUSED', why, '', '', '', 0) for c in coins]
                continue
        pc = rd.price_coins(day)
        idx = [i for i, c in enumerate(coins) if pc is not None and c in pc and (day not in only or c in only[day])]
        status = {}
        if day in own:
            for i, c in enumerate(coins):
                if pc is None:
                    status[c] = ('NOT_BUILT', 'PRICE')
                elif c not in pc:
                    status[c] = ('NOT_LISTED', 'PRICE')
            for code in raw_codes:
                x = rd.gated(code, day)
                for i in idx:
                    c = coins[i]
                    if c in status:
                        continue
                    if x is None:
                        status[c] = ('NOT_BUILT', code)
                    elif not x[2][i]:
                        status[c] = ('NOT_LISTED', '%s %s' % (x[3], code))
            for code in mkt_codes:
                if rd.gated(code, day, rows=['MARKET']) is None:
                    for i in idx:
                        status.setdefault(coins[i], ('NOT_BUILT', code + ' MARKET'))
        if not idx:
            if day in own:
                cells += [(c, day) + status[c] + ('', '', '', 0) for c in coins]
            continue
        t0 = time.perf_counter()
        if path == 'GRID':
            t, allm, kn, side = eval_grid(A, d, rd, day, idx)
            cand_ij = fires_grid(d, t, allm, kn, side)
            kn_day = kn[:, 1:]; kn_pred = kn[:, 0]
            fl = [(coins[idx[i]], int(t[j]), int(side[i, j])) for i, j in cand_ij]
        else:
            ctx = A.Ctx(d0, src, day, [coins[i] for i in idx], hist); ctx.read_last = day
            fl_raw, sh, cl, kn, side = A.find_fires(ctx, {})
            rows = np.arange(ctx.i0, 2 * ctx.i0, grid // A.BASE_S)
            kn_day = kn[:, rows]; kn_pred = kn[:, ctx.i0 - grid // A.BASE_S]
            fl = [(coins[idx[i]], int(ctx.t[r]), int(side[i, r])) for i, r in fl_raw]
            ctx.push_hist(keep)
            del ctx, sh, cl
        eval_s += time.perf_counter() - t0; cand += len(fl)
        if day in own or day in onset_seed:
            fires += [(c, tt, sd, day) for c, tt, sd in fl]
        if day in own:
            ks = kn_day.sum(axis=1); kp = kn_pred
            row = {coins[i]: k for k, i in enumerate(idx)}
            for c in coins:
                if c not in row:
                    cells.append((c, day) + status[c] + ('', '', '', 0)); continue
                k = row[c]; st = status.get(c) or (('HOLE', 'no known slot') if int(ks[k]) == 0 else ('PRESENT', ''))
                full = int(st[0] == 'PRESENT' and int(ks[k]) == G and bool(kp[k]))
                cells.append((c, day, st[0], st[1], G, int(ks[k]), int(bool(kp[k])), full))
        if rss_bytes() > WORKER_RSS_CAP:
            raise Refusal('WORKER_RSS_CAP', '%d bytes' % rss_bytes())
    t1 = time.perf_counter(); changed = []                             # every part read is unchanged at the end (no producer mid-run)
    for key, sha in rd.sources.items():
        dd, pt = key.split('/', 1)
        p = Path(job['lab_root']) / dd / pt / 'index.json'
        if job.get('reader') is None and sha16_file(p) != sha:
            changed.append(key)
    if changed:
        raise Refusal('SOURCE_CHANGED_DURING_RUN', ', '.join(changed[:5]))
    return {'chunk': job['chunk'], 'fires': fires, 'cells': cells, 'sources': rd.sources, 'candidates': cand,
            'warm': {'mode': job.get('warm_mode'), 'days': len(warm_days), 'coin_days': sum(len(v) for v in only.values()) if only else None},
            'outside_window_days': sorted(rd.outside), 'module_pins': module_pins(),
            'timing': {'read_s': rd.read_s, 'eval_s': eval_s, 'verify_s': time.perf_counter() - t1,
                       'chunk_s': time.perf_counter() - t_start}, 'code_day_reads': rd.reads, 'peak_rss_bytes': rss_bytes(),
            'pid': os.getpid(), 'nice': os.getpriority(os.PRIO_PROCESS, 0)}


# ---------------------------------------------------------------- the run
def depends_on_hist(d, ref):
    """does input ref (or anything it is computed from) use a percentile history op?"""
    if not isinstance(ref, str):
        return False
    s = d['inputs'][ref]
    return s['op'] in HIST_OPS or any(depends_on_hist(d, s[k]) for k in ('of', 'a', 'b', 'if', 'pos', 'neg') if k in s)


def parallel_mode(d):
    """how days may be split over processes with the serial (engine run) answer kept for EVERY coin:
    CHUNKED: no state crosses days (D-1 is read beside D); refractory is merged after the chunks.
    CHUNKED_ENTRY_WARMUP: percentile history (trail_pct / own_pct) keeps the coin's last keep_days EVALUATED days (entries, not calendar
      days; a coin is evaluated on the days its PRICE part lists it) from the serial start (first - keep_days - 1): each later chunk
      rebuilds, coin by coin, exactly those entries (walking back over the PRICE listings, listing gaps included) before its first day.
    SERIAL_FORCED: a history source itself depends on a history op (its stored samples depend on older history): one process."""
    if not ops_of(d) & HIST_OPS:
        return 'CHUNKED', ''
    if any(depends_on_hist(d, s['of']) for s in d['inputs'].values() if s['op'] in HIST_OPS):
        return 'SERIAL_FORCED', 'a percentile history source depends on another percentile history op'
    return 'CHUNKED_ENTRY_WARMUP', ''


def plan_chunks(A, d, info, days, first, workers):
    """contiguous day chunks. The serial start S = first - (keep_days + 1) days (the engine's run warm-up). Chunk 0 evaluates the
    calendar days S..first-1 when the rule keeps history or refractory > 0 (history and refractory seeds, as the engine's run).
    A later chunk of a history rule rebuilds its coins' history entries in the worker (warm_mode ENTRIES, see parallel_mode)."""
    mode, _ = parallel_mode(d)
    n = 1 if mode == 'SERIAL_FORCED' else max(1, min(workers, len(days)))
    k = -(-len(days) // n)
    parts = [days[i:i + k] for i in range(0, len(days), k)]
    keep = A.keep_days(d); start = A.shift(first, -(keep + 1))
    hist = bool(ops_of(d) & HIST_OPS); refr = info['fire']['refractory_s'] > 0
    out = []
    for ci, own in enumerate(parts):
        wd = A.days_between(start, A.shift(own[0], -1)) if ci == 0 and (hist or refr) else []
        out.append({'chunk': ci, 'days': own, 'warm_days': wd, 'seed_days': wd if refr else [],
                    'warm_mode': 'ENTRIES' if (ci > 0 and hist) else 'CALENDAR', 'serial_start': start, 'keep': keep})
    return out


def apply_refractory(fires, refractory_s):
    """the engine's rule over candidate fires in time order per coin: a fire within refractory_s after the coin's last ACCEPTED fire is
    dropped (warm-day seeds included) -> accepted fires"""
    out = []; last = {}
    for c, t, sd, day in sorted(fires, key=lambda x: (x[0], x[1])):
        if t - last.get(c, -1e18) < refractory_s:
            continue
        last[c] = t; out.append((c, t, sd, day))
    return out


def _tsv(columns, rows, head=()):
    f = io.StringIO()
    for h in head:
        f.write('# %s\n' % h)
    w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(columns); w.writerows(rows)
    return f.getvalue()


def _write(path, text):
    tmp = Path(str(path) + '.tmp')
    with open(tmp, 'w') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def module_pins():
    """sha16 of every module file this process loaded from the forensics tree (sys.modules) plus the engine (loaded by path): the code
    identity, taken at admission, in every worker and again before the commit; any difference refuses the run"""
    import clock_series, event_profile                                  # noqa: F401 (loaded before the pins are taken)
    from lab3 import days, law, bins                                     # noqa: F401
    from labcore import briefs, jobgate, ids, gates                      # noqa: F401
    root = str(F_ROOT) + os.sep; out = {str(ENGINE_PATH): sha16_file(ENGINE_PATH), str(Path(__file__).resolve()): sha16_file(__file__)}
    for m in list(sys.modules.values()):
        f = getattr(m, '__file__', None)
        if f and f.endswith('.py'):
            f = os.path.realpath(f)
            if f.startswith(root):
                out[f] = sha16_file(f)
    return dict(sorted(out.items()))


def manifest_sha16(m):
    """sha16 of the manifest body (every key but manifest_sha16), canonical JSON: an edited DETECT_RUN.json is refused by read_run"""
    body = {k: v for k, v in m.items() if k != 'manifest_sha16'}
    return sha16_text(json.dumps(body, sort_keys=True, separators=(',', ':'), allow_nan=False))


def _die_with_parent(parent_pid, poll_s=0.1):
    """a worker (and the CLI process) stops when the process that started it is gone: a hard-killed run leaves nothing running outside
    its slot claim"""
    import threading

    def watch():
        while True:
            if os.getppid() != parent_pid:
                os._exit(70)
            time.sleep(poll_s)
    threading.Thread(target=watch, name='die_with_parent', daemon=True).start()


def run(definition, first, last, out_dir, roster, coins='ALL', group=None, group_file=None, workers=8, lab_root=None,
        research_window=None, gate=None, _reader=None, _path=None, _log=None):
    """THE detection function -> absolute path of out_dir/DETECT_RUN.json (status COMPLETE). Refusals raise Refusal before anything is
    committed. _reader / _path are test hooks (a planted reader object, a forced execution path); a run using them is marked TEST."""
    wall0 = time.perf_counter(); started = dt.datetime.now(dt.timezone.utc).isoformat()
    log = _log or (lambda *a: None)
    if not isinstance(workers, int) or isinstance(workers, bool) or not 1 <= workers <= MAX_WORKERS:
        raise Refusal('WORKERS', '1 to %d workers (the team process budget), got %r' % (MAX_WORKERS, workers))
    if _reader is None and (lab_root is None or str(lab_root) == ''):
        raise Refusal('LAB_ROOT_REQUIRED', 'give lab_root (--lab-root: the settings key LAB_DAYS); edition 2 has no machine default')
    if not gate_is_run(gate):
        raise Refusal('GATE_NOT_RUN', 'BACKFILL_GATE first line is not RUN')
    for k in THREAD_VARS:                                              # one numeric thread in every worker (inherited by spawn)
        os.environ[k] = '1'
    first, last = check_days(first, last)
    window = admit_research_window(research_window, first, last)    # before any read: nothing outside it is ever opened
    A = engine()
    d, info = load_definition(definition)
    if _path is not None:
        if _path not in ('GRID', 'BASE') or (_path == 'GRID' and info['execution_path'] != 'GRID'):
            raise Refusal('PATH', 'forced path %r not possible' % _path)
        info['execution_path'] = _path
    if not (info['window']['first'] <= first <= last <= info['window']['last']):
        raise Refusal('DEFINITION_WINDOW', '%s..%s is outside the definition window %s..%s' % (first, last, info['window']['first'],
                                                                                               info['window']['last']))
    roster_coins, roster_sha = load_roster(roster)
    chosen, selection = select_coins(roster_coins, coins, group, group_file)
    out = Path(out_dir).resolve()
    if out.exists():
        raise Refusal('OUTPUT_EXISTS', '%s: a run folder is never overwritten' % out)
    days = A.days_between(first, last)
    jobs = plan_chunks(A, d, info, days, first, workers)
    pmode, preason = parallel_mode(d)
    for j in jobs:
        j.update(definition=info['path'], definition_sha16=info['sha16'], lab_root=str(lab_root), coins=chosen,
                 path=info['execution_path'], reader=_reader, window=list(window), gate=gate)
    pins0 = module_pins()                                              # code identity at admission
    out.mkdir(parents=True)
    t_plan = time.perf_counter() - wall0
    t0 = time.perf_counter(); results = []
    if workers == 1 or len(jobs) == 1 or _reader is not None:
        for j in jobs:
            results.append(work_chunk(j))
    else:
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=len(jobs), mp_context=mp.get_context('spawn'), initializer=_die_with_parent,
                                 initargs=(os.getpid(),)) as ex:
            futs = [ex.submit(work_chunk, j) for j in jobs]
            try:
                results = [f.result() for f in futs]
            except BaseException:
                for f in futs:
                    f.cancel()
                raise
        # leaving the with-block joins every worker process (ProcessPoolExecutor.shutdown(wait=True))
    t_pool = time.perf_counter() - t0
    t1 = time.perf_counter()
    results.sort(key=lambda r: r['chunk'])
    cand = [x for r in results for x in r['fires']]
    acc = apply_refractory(cand, info['fire']['refractory_s'])
    lo, hi = A.day0(first), A.day0(A.shift(last, 1))
    ev = sorted((x for x in acc if lo <= x[1] < hi and x[3] >= first), key=lambda x: (x[1], x[0]))
    cells = [c for r in results for c in r['cells']]
    want = {(c, dd) for c in chosen for dd in days}
    got = [(c[0], c[1]) for c in cells]
    if len(got) != len(set(got)) or set(got) != want:
        raise Refusal('CENSUS', 'cells %d (distinct %d) vs requested %d' % (len(got), len(set(got)), len(want)))
    evaluated = {(c[0], c[1]) for c in cells if c[4] != ''}
    bad = [e for e in ev if (e[0], e[3]) not in evaluated]
    if bad:
        raise Refusal('EVENT_OUTSIDE_EVALUATED_CELL', repr(bad[:3]))
    trig = trigger_of(d)
    rows = [(c, t, sd, t, trig, sha16_text('%s|%s|%d|%d' % (info['sha16'], c, t, sd))) for c, t, sd, _ in ev]
    head = ['idea_to_grade detect %s' % VERSION, 'definition %s sha16 %s path %s' % (info['id'], info['sha16'], info['path']),
            'roster sha16 %s path %s' % (roster_sha, Path(roster).resolve()), 'first %s last %s' % (first, last),
            'selection %s' % json.dumps(selection, sort_keys=True), 'onset_t: the fire step (the onset rule fires at the onset)']
    _write(out / 'EVENTS.tsv', _tsv(['coin', 't', 'side', 'onset_t', 'trigger', 'event_id'], rows, head))
    cells.sort(key=lambda c: (c[1], chosen.index(c[0])))
    _write(out / 'COVERAGE.tsv', _tsv(['coin', 'day', 'status', 'reason', 'slots', 'known_slots', 'predecessor_known', 'full_known'],
                                      cells, head[:5]))
    import event_profile as EP                                         # the interface promise: the shared loader reads it
    back = EP.load_alarms(str(out / 'EVENTS.tsv'))
    if len(back['t']) != len(rows):
        raise Refusal('EVENTS_UNREADABLE', 'load_alarms read %d of %d' % (len(back['t']), len(rows)))
    t_write = time.perf_counter() - t1
    counts = {s: sum(1 for c in cells if c[2] == s) for s in STATUSES}
    sources = {}
    for r in results:
        sources.update(r['sources'])
    if not gate_is_run(gate):
        raise Refusal('GATE_NOT_RUN', 'the gate left RUN during the run: nothing committed')
    pins = dict(pins0); changed = set()
    for pp in [module_pins()] + [r['module_pins'] for r in results]:    # the parent now and every worker: one identity
        for f, h in pp.items():
            if pins.setdefault(f, h) != h:
                changed.add(f)
    if changed:
        raise Refusal('CODE_CHANGED_DURING_RUN', ', '.join(sorted(changed)[:5]))
    outside = sorted({x for r in results for x in r['outside_window_days']})
    peak_workers = [r['peak_rss_bytes'] for r in results]
    manifest = {
        'status': 'COMPLETE', 'tool': 'idea_to_grade/detect.py', 'version': VERSION,
        'test_hooks': bool(_reader is not None or _path or os.environ.get(TEST_HOLD_ENV)),
        'started_utc': started, 'finished_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'definition': {k: info[k] for k in ('path', 'sha16', 'sha256', 'id', 'version', 'window', 'briefs')},
        'grid_s': info['grid_s'], 'fire': info['fire'], 'side': info['fire']['side'], 'conditions': info['conditions'],
        'trigger': trig, 'execution_path': info['execution_path'],
        'roster': {'path': str(Path(roster).resolve()), 'sha16': roster_sha, 'coins': len(roster_coins)},
        'selection': selection, 'coins': chosen, 'first': first, 'last': last, 'days': len(days), 'lab_root': str(lab_root),
        'cells': {'requested': len(cells), 'present': counts['PRESENT'], 'unavailable': len(cells) - counts['PRESENT'], 'by_status': counts,
                  'full_known': sum(c[7] for c in cells)},
        'events': len(rows), 'candidate_fires': sum(r['candidates'] for r in results),
        'files': {n: sha16_file(out / n) for n in REQUIRED_FILES},
        'code_sha16': pins, 'research_window': {'first': window[0], 'last': window[1], 'days_never_opened': outside},
        'event_lists': info['event_lists'], 'source_parts_read': len(sources), 'source_fingerprint': sha16_text(json.dumps(sources, sort_keys=True)),
        'sources': sources,
        'phase_s': {'plan': t_plan, 'workers_wall': t_pool, 'merge_write': t_write,
                    'read_sum': sum(r['timing']['read_s'] for r in results), 'eval_sum': sum(r['timing']['eval_s'] for r in results),
                    'verify_sum': sum(r['timing']['verify_s'] for r in results), 'chunks': [r['timing'] for r in results]},
        'parallel': {'mode': pmode, 'reason': preason, 'chunks': len(jobs)},
        'workers': {'requested': workers, 'processes': len(jobs) if len(jobs) > 1 and workers > 1 and _reader is None else 0,
                    'chunks': [{'chunk': j['chunk'], 'first': j['days'][0], 'last': j['days'][-1], 'warm': r['warm']}
                               for j, r in zip(jobs, results)],
                    'nice': sorted({r['nice'] for r in results}), 'threads_env': {k: os.environ.get(k) for k in THREAD_VARS}},
        'memory': {'parent_peak_rss_bytes': rss_bytes(), 'worker_peak_rss_bytes': peak_workers,
                   'sum_peak_rss_bytes': rss_bytes() + sum(peak_workers),
                   'meaning': 'ru_maxrss of each process; the sum is an upper bound of the tree at any instant'},
        'wall_s': time.perf_counter() - wall0,
        'semantics': 'outside detector (run_speed_v11/source_runtime_speed_v11/native_raw_clock_v6) = engine alarm_design_v2 '
                     'cond_mask/side_of/find_fires; quality: finite v AND e==0, a>=0, o>=0, k<=column time; NotBuilt = UNKNOWN day',
        'not_asserted': 'detection replays the registered rule on stored values; it does not prove the named phenomenon, causes or profit',
    }
    manifest['manifest_sha16'] = manifest_sha16(manifest)
    tmp = out / 'DETECT_RUN.json.tmp'
    with open(tmp, 'w') as f:
        json.dump(manifest, f, indent=1, sort_keys=True, allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, out / 'DETECT_RUN.json')
    log('DETECT %s events %d cells %d present %d wall %.2f s' % (info['id'], len(rows), len(cells), counts['PRESENT'], manifest['wall_s']))
    return str(out / 'DETECT_RUN.json')


def read_run(out_dir):
    """a consumer's read of a committed run -> the manifest. REFUSED: no folder or no DETECT_RUN.json (NOT_A_RUN), an unreadable manifest
    (MANIFEST_INVALID), a status other than COMPLETE (NOT_COMPLETE), an edited manifest (MANIFEST_CHANGED: its manifest_sha16 is the
    canonical body's), a pinned file missing (FILE_MISSING) or changed (FILE_CHANGED), any file the manifest does not pin (EXTRA_FILE)"""
    out = Path(out_dir)
    p = out / 'DETECT_RUN.json'
    if not out.is_dir() or not p.is_file():
        raise Refusal('NOT_A_RUN', '%s has no DETECT_RUN.json' % out)
    try:
        m = json.loads(p.read_text())
        files = dict(m['files'])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Refusal('MANIFEST_INVALID', '%s: %s' % (p, e))
    if m.get('status') != 'COMPLETE':
        raise Refusal('NOT_COMPLETE', str(m.get('status')))
    if sorted(files) != sorted(REQUIRED_FILES) or any(not isinstance(h, str) or not re.fullmatch('[0-9a-f]{16}', h)
                                                      for h in files.values()):
        raise Refusal('RUN_SCHEMA', '%s: files must pin exactly %s with sha16 hashes' % (p, ', '.join(REQUIRED_FILES)))
    for k in ('events', 'cells', 'coins', 'first', 'last', 'definition', 'grid_s', 'manifest_sha16'):
        if k not in m:
            raise Refusal('RUN_SCHEMA', '%s: no %s' % (p, k))
    if m.get('manifest_sha16') != manifest_sha16(m):
        raise Refusal('MANIFEST_CHANGED', '%s: its body is not the committed one' % p)
    extra = sorted(set(os.listdir(out)) - set(files) - {'DETECT_RUN.json'})
    if extra:
        raise Refusal('EXTRA_FILE', '%s: not pinned by the manifest: %s' % (out, ', '.join(extra[:5])))
    for n, h in files.items():
        if not (out / n).is_file():
            raise Refusal('FILE_MISSING', n)
        if sha16_file(out / n) != h:
            raise Refusal('FILE_CHANGED', n)
    return m


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--definition', required=True); p.add_argument('--roster', required=True)
    p.add_argument('--first', required=True); p.add_argument('--last', required=True); p.add_argument('--out', required=True)
    p.add_argument('--coins', default=None); p.add_argument('--group', default=None); p.add_argument('--group-file', default=None)
    p.add_argument('--workers', type=int, default=8); p.add_argument('--lab-root', required=True, help='the lab days (settings key LAB_DAYS)')
    p.add_argument('--gate', default=None, help="the feed's stop gate file (settings key FEED_GATE); empty or not given: no gate")
    p.add_argument('--research-window', default=None, help='FIRST:LAST, required (BUILD months only); no default')
    a = p.parse_args(argv)
    coins = a.coins if a.coins is not None else (None if a.group else 'ALL')
    if argv is None:                                                   # the command line process stops if its launcher (slot wrapper) dies
        _die_with_parent(os.getppid())
    try:
        path = run(a.definition, a.first, a.last, a.out, a.roster, coins=coins, group=a.group, group_file=a.group_file,
                   workers=a.workers, lab_root=a.lab_root, research_window=a.research_window, gate=a.gate, _log=print)
    except Refusal as e:
        print('REFUSED %s' % e, file=sys.stderr)
        return 2
    except Exception as e:                                             # noqa: BLE001 (an unexpected failure: named, never a COMPLETE run)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print('FAILED %s: %s' % (type(e).__name__, e), file=sys.stderr)
        return 3
    m = json.loads(Path(path).read_text())
    print(json.dumps({'status': m['status'], 'events': m['events'], 'cells': m['cells'], 'wall_s': round(m['wall_s'], 3),
                      'sum_peak_rss_bytes': m['memory']['sum_peak_rss_bytes'], 'run': path}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
