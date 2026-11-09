# event_outcomes_aw1_rel1.py (SCOUT K12, 31 Oct 2026; TEST, NOT REVIEWED): event_outcomes_aw1.py e4a4792db69e71fb, never edited, with
# event_outcomes_rel1.py's changes and nothing else: the feed's stop gate is the environment FEED_GATE (must be set: unset refused
# NO_FEED_GATE; empty = no gate), never labcore.jobgate's built-in dev-tree GATE; the research days are RESEARCH_STORE when set;
# RUN_PARALLEL is run_parallel_rel1.py (only named in the code inventory: aw1 runs Outcomes in its own process, run 0); its release
# record is RELEASE_event_outcomes_AW1_REL1.json. The rest of this file is event_outcomes_aw1.py's.
# event_outcomes_aw1.py, aw1 (STRATEGY 28 Oct 2026, ALARM_DESIGN kit; TEST, NOT REVIEWED; the owner 28 Oct 2026: Mar-May for the alarm agents only): event_outcomes.py 7332c1f005e958ef copied unchanged except
# (1) the outcome window CLASSES from alarm_process/WINDOWS_ALARM_V1.tsv (sha16 checked; frozen as the run's windows pin), (2) its release
# RELEASE_event_outcomes_AW1.json beside it (= V3_CANDIDATE + this file + the table), (3) run 0 only (in this process: workers would run the original).
"""event_outcomes.py: OUTCOMES, code VERSION 3 (STRATEGY/LEAD builder, 25 Oct 2026): successor of 2017ed1cc2e4c6dd (VERSION 2) after the
independent A51 review (team/OUTSIDE/A51/outcomes_review_v1: A51-01..07). Architecture: ARCHITECTURE.md; manual: README.md.
QUESTION: for every event of any list (coin, t, side), what happened after it, measured by every outcome label a settings file names, in
each chosen direction. Owner the owner 25 Oct 10:37:54Z: "we should be able to choose any yardstick, any labels and get the results for the
alarms"; 10:39:49Z: "speed, settings to add any new label we want". Research labels on Binance 3 s model paths; never an order.
WHAT VERSION 3 CHANGED (each with its review id; README 'What changed'):
- A51-01 clocks: entry__px / entry__s are known at the entry bar's end (never at F); a NO_ENTRY is known at the end of the 60 s wait; a
  horizon is a whole number of 3 s bars (the settings refuse any other) and label_path floors defensively, so no bar after the declared
  horizon is ever read; every column carries its own availability clock (README 'Columns').
- A51-02 missing paths: ONE coverage convention, the shared LABEL_EWSD helper bucket_proof/label_ewsd_v2.path_first_gap (imported,
  applied to exactly the bars the label reads); return refuses a path with a hole (PATH_GAP); its last-close fallback is clamped to the
  entry and to gap_s; a label settled before a truncated tail keeps its value; best / worst include the zero excursion of the entry; the
  settings refuse non-finite numbers, horizons that are not whole 3 s bars, repeated directions and colliding column names.
- A51-03 touches: reach / first / offer_before_heat / heat_before compare the bar's high (low) with the PRICE LEVEL
  p0 x (1 +- target x unit / 100), inclusive within TOUCH_RTOL = 1e-9 relative (far below any traded tick), never a recomputed ratio.
- A51-04 authorization: the caller's authorized outcome window (run setting run_window or argument --run-window FIRST:LAST; never a
  date in this code) is enforced before any read: the selected days must lie inside it, and the months of every event and of every
  forward support go through labcore.gates.outcome_allowed (lab3/law.py + WINDOWS_V1). A label whose window could need a bar at or
  after the end of the authorized window is EMBARGO_SUPPORT (the row and its event identity stay; the price is never read).
- A51-05 evidence: exit labels go through exit_engine.run_frozen (frozen registry row, schema, cost table, module and the run's
  transitive inventory); the value is published only for a CLEAN path; PATH_UNCERTAIN keeps its booking in __booked; path evidence and
  hole bars are columns; price model and venue are checked constant and carried in the catalog and manifest; every unresolved value and
  companion shares one reason and one defensible clock.
- A51-06 money: kind money_full is the factory's money of record (factory_v2.costs_of / trade_cost: costs V3_5 fee + book + gap +
  funding on the entry notional). A trade with missing funding is EMPTY (FUNDING_MISSING) and its fee + book + gap stay in
  __cost_prefunding; kind money (static V1 cost + gap, no funding) is retired: it is refused by name, never relabelled.
- A51-07 operation: strict event list (load_events: event_profile.load_alarms' contract, no import) and coverage census; per coin-day listing (NO_COIN, NOT_LISTED,
  NOT_BUILT) and the static cost fallback carried, never conflated; real catalog units; the run is frozen (release + transitive code
  inventory + PRICE / EPI index and funding-file vintages) before work, rechecked by every worker before it reads and again at
  publication; the run is staged in <out_root>.pending_<pid>_<stamp>, verified (every requested event x column exactly once, typed, a reason
  for every empty cell, outcome clocks never before F, sources equal to the frozen ones), then published by ONE atomic rename with the
  terminal manifest RUN_MANIFEST.json committed last (event_decisions/run_manifest_candidate.py stage / commit / abort / load_complete:
  the same pattern event_situations VERSION 2 uses, reused, not copied); a failure is kept as <out_root>.failed_<stamp> with FAILED.json.
  Consumers (read, show, verify) refuse a root without a COMPLETE manifest, a changed file, or an OUT part the manifest does not name.
COMMANDS (analyst python; the public commands check RELEASE_event_outcomes_V3_CANDIDATE.json and the import closure first):
  python3 event_outcomes.py run   <N 1-8> <lab_root> <lab3 code> <events.tsv> <settings.json> <SUBJECT> <first> <last> <out_root>
                                  [--run-window FIRST:LAST] [--ctx R] [--epg R] [--cause R] [--max-rss-gb G]
  python3 event_outcomes.py check <same arguments as run without N>   (every admission check and the input census; reads indexes only)
  python3 event_outcomes.py build <lab_root> <lab3 code> <events.tsv> <settings.json> <SUBJECT> <first> <last> <stage_root>
                                  (a worker: run_parallel's 'outcomes' branch calls it inside the stage that run opened)
  python3 event_outcomes.py verify <out_root> <lab3 code>
  python3 event_outcomes.py show   <out_root> <lab3 code> <SUBJECT> <first> <last>"""
import csv, datetime as dt, decimal, json, math, os, re, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__)); TOOLS = os.path.dirname(HERE)
FORENSICS = os.path.realpath(os.path.join(TOOLS, '..', '..', '..'))
for _d in ('exit_engine', 'bucket_proof', 'event_decisions', ''):
    _p = os.path.join(TOOLS, _d) if _d else TOOLS
    if _p not in sys.path:
        sys.path.insert(0, _p)
from labcore import prices, costs, gates, ids, release, jobgate            # noqa: E402  price cache, static c, outcome gate, sha16
import exit_engine_v1 as XE                                                 # noqa: E402  the exit walk (run_frozen) and the 3 s grid
import label_ewsd_v2 as LV2                                                 # noqa: E402  path_first_gap: THE coverage convention
import run_manifest_candidate as RM                                         # noqa: E402  whole-run manifest (decisions_fixer's candidate)
from labcore.v2_7 import quality as Q                                       # noqa: E402  S2: THE rule that a stored cell is KNOWN (LAB1)
from labcore.v2_7 import selection as S                                     # noqa: E402  S3: window-first selection (ctxprof_shared)

TOOL = 'event_outcomes'; VERSION = 3; US = 1_000_000; BAR_S = 3; BAR_US = XE.BAR_US; DAY_US = 86_400 * US
WAIT_S = 60                       # the factory's entry rule (factory_v2.trade): no priced bar within 60 s of the first grid bar = no entry
TOUCH_RTOL = 1e-9                 # a price level counts as touched within 1e-9 relative (float noise of p0 x (1 + x); far below a tick)
MANIFEST = 'RUN_MANIFEST'
RELEASE = os.path.join(HERE, 'RELEASE_event_outcomes_AW1_REL1.json')   # aw1; K12 rel1: this edition's release record
WINDOWS_ALARM = os.path.join(HERE, 'WINDOWS_ALARM_V1.tsv'); WINDOWS_ALARM_SHA16 = '69c3327ebf4e15a1'   # aw1: the alarm kit's window classes
RUN_PARALLEL = os.path.join(TOOLS, 'event_profile', 'run_parallel_rel1.py')   # K12 rel1 (only in the code inventory: run 0)
KINDS = {'return': ('horizon_min',), 'best': ('horizon_min',), 'worst': ('horizon_min',), 'reach': ('target', 'horizon_min'),
         'first': ('up', 'down', 'horizon_min'), 'offer_before_heat': ('offer', 'heat', 'horizon_min'), 'heat_before': ('target', 'horizon_min'),
         'exit': ('exit_id',), 'money_full': ('exit_id',)}
RETIRED = {'money': 'kind money (V1/V2: the booked exit minus the static V1 cost + gap, without funding) is retired (A51-06): it is not the '
                    'money of record. Use kind money_full (factory_v2 trade_cost: fee + book + gap + funding, costs V3_5)'}
PATH_KINDS = ('exit', 'money_full')
TIMED = ('reach', 'first', 'offer_before_heat', 'exit', 'money_full')
DIRS = ('FADE', 'FOLLOW', 'LONG', 'SHORT')
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')
NAME_RE = re.compile(r'[A-Z0-9](?:[A-Z0-9]|_(?!_))*\Z')                   # capitals, digits, single _ (no '__': column suffixes use it)
DAY_RE = re.compile(r'\d{8}\Z')
REASONS = {                                                                  # the closed set of empty reasons ('<REASON>:<detail>' allowed)
    'EMBARGO_SUPPORT': 'the window could need a bar at or after the end of the authorized outcome window (run_window): never read',
    'NO_COIN': 'the coin is not in the PRICE index of a day the entry needs',
    'NOT_BUILT': 'a PRICE day the event needs is not built (lab3 NotBuilt)',
    'NO_ENTRY': 'no priced 3 s bar within 60 s of the first grid bar (the factory rule)',
    'NOT_LISTED': 'the coin is not in the PRICE index of a later day of the window, and the label was not decided before it',
    'NO_PATH': 'the 3 s grid ends before the window / exit engine UNRESOLVED (no valid bar to book the exit)',
    'PATH_GAP': 'a data hole (a stretch over gap_s without a valid bar, LABEL_EWSD convention) before the label was decided',
    'NO_PRICE': 'no observed bar where the label needs one',
    'NOT_REACHED': 'the target was not reached in the window (heat_before; __t of a reach 0 / first 0)',
    'NO_UNIT': 'the unit (c, nm) is missing, not positive, a cost fallback or known after the decision (detail after the colon)',
    'NO_DIRECTION': 'side 0 without a Cause side_used: no FADE / FOLLOW direction',
    'PATH_UNCERTAIN': 'exit engine PATH_UNCERTAIN: a hole inside the hold could have crossed a level; the booking is in __booked',
    'FUNDING_MISSING': 'money_full: an hour of HL funding is missing; fee + book + gap only (__cost_prefunding): never complete money',
    'NO_COST': 'money_full: no cost-of-record row for the coin (costs V3_5)'}


class Refused(PermissionError):
    """a refusal by name: nothing is read or written after it"""
    def __init__(self, code, text):
        super().__init__('%s: %s' % (code, text)); self.code = code


def feed_gate():
    """K12 rel1: the feed's stop gate is the environment FEED_GATE (the settings key FEED_GATE; the job gives it to the chain, the chain to
    this run and its workers). It must be set: unset is refused NO_FEED_GATE (never the built-in team path of labcore.jobgate); empty =
    no gate (a machine without the feed), the rule of detect_v2's --gate"""
    if 'FEED_GATE' not in os.environ:
        raise Refused('NO_FEED_GATE', 'set FEED_GATE to the feed stop gate file (the settings key FEED_GATE), or to empty for no gate')
    return os.environ['FEED_GATE']


def gate_wait(log=print):
    """K12 rel1: labcore.jobgate.gate_wait on the FEED_GATE file (as before: blocks while its first line is not RUN; a missing file reads
    PAUSE); no gate (FEED_GATE empty): 0 at once, nothing read"""
    g = feed_gate()
    return jobgate.gate_wait(gate=g, log=log) if g else 0


def research_store(lab_root):
    """K12 rel1: the research days are the environment RESEARCH_STORE (the settings key RESEARCH_STORE) when it is set and not empty,
    else (as before) research_days beside the lab days"""
    return os.environ.get('RESEARCH_STORE') or os.path.join(os.path.dirname(os.path.abspath(lab_root)), 'research_days')


class _Lazy:
    """a module imported on first use (event_situations is only needed when a settings file binds CTX / EPG / CAUSE2 inputs)"""
    def __init__(self, name):
        self.__dict__['_name'] = name

    def __getattr__(self, k):
        import importlib
        return getattr(importlib.import_module(self.__dict__['_name']), k)


ES = _Lazy('event_situations')
if os.path.join(TOOLS, 'event_situations') not in sys.path:
    sys.path.insert(1, os.path.join(TOOLS, 'event_situations'))


# ------------------------------------------------------------------ small helpers (dates, files)
def fpath(p):
    """a settings path: absolute, or relative to the forensics folder"""
    return p if os.path.isabs(p) else os.path.join(FORENSICS, p)


def valid_day(d):
    t = str(d)
    if not DAY_RE.fullmatch(t):
        raise ValueError('day %r: YYYYMMDD' % (d,))
    dt.date(int(t[:4]), int(t[4:6]), int(t[6:]))
    return t


def day_of(t_us):
    return prices.day_of(int(t_us))


def day_start_us(day):
    return int(dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()) * US


def days_between(a, b):
    out = []; d = dt.datetime.strptime(a, '%Y%m%d')
    while d.strftime('%Y%m%d') <= b:
        out.append(d.strftime('%Y%m%d')); d += dt.timedelta(days=1)
    return out


def months_between(a, b):
    return sorted({d[:6] for d in days_between(a, b)})


def utc_now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def finite(x, what):
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise ValueError('settings: %s %r is not a number' % (what, x))
    if isinstance(x, bool) or not math.isfinite(v):
        raise ValueError('settings: %s %r must be a finite number' % (what, x))
    return v


def horizon_us(x):
    """a label window in whole microseconds (refused unless a whole number of 3 s bars by load_settings)"""
    return int(round(float(x['horizon_min']) * 60 * US))


# ------------------------------------------------------------------ settings
def load_settings(path, want_sha16=None):
    """the settings, every refusal before any read: kinds and their numbers (finite, > 0), horizons a whole number of 3 s bars, units,
    unique directions and column names, the exits registry (sha16), the static cost table (sha16) for c, the cost settings of record
    (sha16) for money_full, the unit bindings, the optional run_window"""
    sha = ids.sha16_file(path)
    if want_sha16 is not None and sha != want_sha16:
        raise ValueError('settings %s sha16 %s, wanted %s: refused' % (path, sha, want_sha16))
    s = json.load(open(path)); s['_sha16'] = sha; s['_path'] = os.path.realpath(path)
    for k in ('name', 'entry', 'directions', 'labels'):
        if k not in s:
            raise ValueError('settings: %s missing' % k)
    delay = finite(s['entry'].get('delay_s'), 'entry delay_s')
    if delay < 0 or delay * US != int(delay * US):
        raise ValueError('settings: entry delay_s >= 0, whole microseconds')
    gap = finite(s['entry'].get('gap_s', 60), 'entry gap_s')
    if gap < BAR_S:
        raise ValueError('settings: entry gap_s >= one 3 s bar')
    s['entry']['gap_s'] = gap
    d = s['directions']
    if not isinstance(d, list) or not d or len(set(d)) != len(d) or any(x not in DIRS for x in d):
        raise ValueError('settings: directions: a list of distinct names from %s' % (DIRS,))
    if not isinstance(s['labels'], list) or not s['labels']:
        raise ValueError('settings: labels: a non-empty list')
    names = [x.get('name') for x in s['labels']]
    if len(set(names)) != len(names) or not all(isinstance(n, str) and NAME_RE.fullmatch(n) for n in names):
        raise ValueError('settings: label names must be unique, capitals, digits and single _ (no "__")')
    s.setdefault('units', {})
    for x in s['labels']:
        k = x.get('kind')
        if k in RETIRED:
            raise ValueError('settings: label %s: %s' % (x['name'], RETIRED[k]))
        if k not in KINDS or any(f not in x for f in KINDS[k]):
            raise ValueError('settings: label %s needs a kind in %s and its numbers %s' % (x['name'], sorted(KINDS), KINDS.get(k)))
        if k in PATH_KINDS:
            if 'exits' not in s:
                raise ValueError('settings: exit / money_full labels need the exits file (path, sha16)')
            continue
        h = finite(x['horizon_min'], 'label %s horizon_min' % x['name'])
        hus = h * 60 * US
        if h <= 0 or abs(hus - round(hus)) > 1e-3 or int(round(hus)) % BAR_US:
            raise ValueError('settings: label %s: horizon_min > 0 and a whole number of 3 s bars (%r min is not): refused (A51-01)'
                             % (x['name'], x['horizon_min']))
        if x.get('unit', 'pct') not in ('pct', 'c', 'nm'):
            raise ValueError('settings: label %s: unit pct | c | nm' % x['name'])
        for f in ('target', 'up', 'down', 'offer', 'heat'):
            if f in x and finite(x[f], 'label %s %s' % (x['name'], f)) <= 0:
                raise ValueError('settings: label %s: %s must be > 0' % (x['name'], f))
    if 'exits' in s:
        ep = fpath(s['exits']['path'])
        rows = XE.load_exits(ep, want_sha16=s['exits']['sha16']); s['_exits'] = rows; s['_exits_path'] = ep
        for x in s['labels']:
            if x['kind'] in PATH_KINDS:
                if x['exit_id'] not in rows:
                    raise ValueError('settings: exit row %s not in the exits file' % x['exit_id'])
                r = rows[x['exit_id']]
                if r.get('stop_from') == 'extreme' or (r.get('monitor') not in (None, '', 'none')):
                    raise ValueError('settings: exit row %s needs monitor / extreme bindings (stop_from %s, monitor %s) this tool does not '
                                     'supply: refused before any price read (A51 acceptance 8)' % (x['exit_id'], r.get('stop_from'), r.get('monitor')))
    need = {x.get('unit', 'pct') for x in s['labels'] if x['kind'] not in PATH_KINDS} | \
           {s['_exits'][x['exit_id']]['unit'] for x in s['labels'] if x['kind'] in PATH_KINDS}
    if 'c' in need or any(x['kind'] in PATH_KINDS for x in s['labels']):
        c = s.get('cost')
        if not c or not all(k in c for k in ('table', 'sha16', 'gap_pct')):
            raise ValueError('settings: unit c and the frozen exit boundary need the cost block {table, sha16, gap_pct} (labcore.costs)')
        if ids.sha16_file(fpath(c['table'])) != c['sha16']:
            raise ValueError('settings: cost table %s is not sha16 %s: refused' % (c['table'], c['sha16']))
        finite(c['gap_pct'], 'cost gap_pct')
        if c.get('fallback', 'unknown') not in ('unknown', 'median_flagged'):
            raise ValueError('settings: cost fallback unknown | median_flagged')
    if any(x['kind'] == 'money_full' for x in s['labels']):
        m = s.get('money') or {}
        cs = m.get('cost_settings') or {}
        if not cs.get('path') or not cs.get('sha16') or 'size_usd' not in m:
            raise ValueError('settings: money_full needs money {cost_settings {path, sha16}, size_usd}')
        if ids.sha16_file(fpath(cs['path'])) != cs['sha16']:
            raise ValueError('settings: cost settings %s is not sha16 %s: refused' % (cs['path'], cs['sha16']))
        cap = json.load(open(fpath(cs['path']))).get('size_usd')
        if not 0 < finite(m['size_usd'], 'money size_usd') <= float(cap):
            raise ValueError('settings: money size_usd must be > 0 and <= the cost settings size_usd %s' % cap)
    for u in need - {'pct', 'c'}:
        if u not in s['units']:
            raise ValueError('settings: unit %s needs units.%s bound to an input (SOURCE:column)' % (u, u))
    for u, b in s['units'].items():
        if u in ('pct', 'c') or not re.fullmatch(r'[a-z][a-z0-9_]*', u):
            raise ValueError('settings: units.%s: a lower-case name other than pct and c' % u)
        if not isinstance(b, str) or ':' not in b or b.split(':', 1)[0] not in ('CTX', 'EPG', 'CAUSE2', 'EPI'):
            raise ValueError('settings: units.%s must be SOURCE:column with SOURCE CTX | EPG | CAUSE2 | EPI' % u)
    if 'run_window' in s:
        check_window(s['run_window'])
    cols = [c['col'] for c in column_specs(s)]
    if len(set(cols)) != len(cols):
        raise ValueError('settings: generated column names collide: %s' % sorted({c for c in cols if cols.count(c) > 1}))
    return s


def check_window(w):
    if not isinstance(w, dict) or 'first' not in w or 'last' not in w:
        raise ValueError('run_window: {first, last} days')
    a, b = valid_day(w['first']), valid_day(w['last'])
    if a > b:
        raise ValueError('run_window: first %s after last %s' % (a, b))
    return a, b


def span_us(s, x):
    """the label's window after the entry bar: its horizon, or the exit row's time limit, in whole 3 s bars"""
    if x['kind'] in PATH_KINDS:
        return XE.bars_of(s['_exits'][x['exit_id']]['time_limit_min']) * BAR_US
    return (horizon_us(x) // BAR_US) * BAR_US


# ------------------------------------------------------------------ columns and catalog
def _unit_names(s):
    us = []
    labs = [x for x in s['labels']]
    if any((x['kind'] not in PATH_KINDS and x.get('unit', 'pct') == 'c') or (x['kind'] in PATH_KINDS and s['_exits'][x['exit_id']]['unit'] == 'c')
           for x in labs):
        us.append('c')
    for u in sorted(s['units']):
        us.append(u)
    return us


def column_specs(s):
    """every output column: {col, kind number | word, unit, role, label, dir}"""
    out = [dict(col='entry__px', kind='number', unit='price', role='entry_px', label=None, dir=None),
           dict(col='entry__s', kind='number', unit='seconds', role='entry_s', label=None, dir=None)]
    for u in _unit_names(s):
        out.append(dict(col='unit__%s' % u, kind='number', unit='pct', role='unit', label=None, dir=None, unit_name=u))
        if u == 'c':
            out.append(dict(col='unit__c_fallback', kind='number', unit='flag', role='unit_fallback', label=None, dir=None, unit_name=u))
    for x in s['labels']:
        k = x['kind']
        vu = {'reach': 'flag', 'first': 'sign', 'offer_before_heat': 'sign', 'exit': 'pct', 'money_full': 'pct'}.get(k, x.get('unit', 'pct'))
        for d in s['directions']:
            b = '%s__%s' % (x['name'], d)
            out.append(dict(col=b, kind='number', unit=vu, role='value', label=x, dir=d))
            if k in TIMED:
                out.append(dict(col=b + '__t', kind='number', unit='seconds', role='t', label=x, dir=d))
            if k in PATH_KINDS:
                out += [dict(col=b + '__how', kind='word', unit='word', role='how', label=x, dir=d),
                        dict(col=b + '__path_evidence_status', kind='word', unit='word', role='evidence', label=x, dir=d),
                        dict(col=b + '__hole_bars', kind='number', unit='count', role='holes', label=x, dir=d),
                        dict(col=b + '__booked', kind='number', unit='pct', role='booked', label=x, dir=d)]
            if k == 'money_full':
                out += [dict(col=b + '__fee', kind='number', unit='pct', role='fee', label=x, dir=d),
                        dict(col=b + '__book', kind='number', unit='pct', role='book', label=x, dir=d),
                        dict(col=b + '__gap', kind='number', unit='pct', role='gap', label=x, dir=d),
                        dict(col=b + '__cost_prefunding', kind='number', unit='pct', role='cost_prefunding', label=x, dir=d),
                        dict(col=b + '__funding', kind='number', unit='pct', role='funding', label=x, dir=d),
                        dict(col=b + '__funding_ok', kind='number', unit='flag', role='funding_ok', label=x, dir=d)]
    return out


def columns(s):
    """the VERSION 2 view kept for callers: [(column, 'number' | 'word', label line or None)]"""
    return [(c['col'], c['kind'], c['label']) for c in column_specs(s)]


def _meaning(s, c):
    x = c['label']; r = c['role']
    if r == 'entry_px':
        return 'entry price: the close of the entry bar (first priced 3 s bar within 60 s of the first bar ending at or after F + delay + one bar; Binance model price). known_at = entry bar end; NO_ENTRY known at first bar + 60 s'
    if r == 'entry_s':
        return 'seconds from F to the entry bar end. known_at = entry bar end'
    if r == 'unit':
        if c['unit_name'] == 'c':
            return 'c in pct: static cost of record (labcore.costs cost_c: %s + gap %s); fallback %s; known_at = F (a static table)' % (
                s['cost']['table'], s['cost']['gap_pct'], s['cost'].get('fallback', 'unknown'))
        return 'unit %s in pct (log-pct) bound to %s; known_at = its stored known_at (never after the decision)' % (c['unit_name'], s['units'][c['unit_name']])
    if r == 'unit_fallback':
        return '1 = the coin is not in the static cost table (labcore median fallback), 0 = in the table; known_at = F'
    spec = {k: v for k, v in x.items() if k not in ('name', 'why')}
    base = '%s %s direction %s' % (x['kind'], json.dumps(spec, sort_keys=True), c['dir'])
    if x['kind'] in PATH_KINDS:
        row = s['_exits'][x['exit_id']]
        eng = 'exit_engine.run_frozen row %s (time limit %s min); price model SIMULATED_BINANCE_3S_ADVERSE_FIRST, venue BINANCE' % (
            x['exit_id'], row['time_limit_min'])
        txt = {'value': ('booked return pct, CLEAN path only' if x['kind'] == 'exit' else
                         'money of record pct = booked - (fee + book + gap + funding) of costs V3_5 (factory_v2.trade_cost, size %s USD); CLEAN, funding complete only' % s['money']['size_usd']),
               't': 'seconds held (exit bar end - entry bar end)', 'how': 'what closed it (stop trail take time monitor)',
               'evidence': 'exit_engine path_evidence_status (CLEAN PATH_UNCERTAIN)', 'holes': 'exit_engine hole_bars (empty 3 s bars of the hold)',
               'booked': 'the engine booking (gross pct), whatever the evidence',
               'fee': 'fee_bp / 100 of costs V3_5 (both legs)', 'book': 'book_bp / 100 of costs V3_5 at the entry hour (the dearer of tables V1 and V4)',
               'gap': 'gap_bp / 100 of costs V3_5 (the Binance-HL gap, both legs)',
               'cost_prefunding': '(fee + book + gap) / 100 of costs V3_5 at the entry', 'funding': 'HL funding paid over the hold, pct of the entry notional',
               'funding_ok': '1 every funding hour priced, 0 FUNDING_MISSING'}[r]
        return '%s; %s; %s. known_at = exit bar end; unresolved: entry + time limit' % (base, txt, eng)
    txt = {'value': {'return': 'side-signed move from the entry close to the close at entry + H', 'best': 'largest favourable excursion (>= 0)',
                     'worst': 'largest adverse excursion (>= 0)', 'reach': '1 favourable price level touched within H, 0 not',
                     'first': '+1 up level first, -1 down level first (a bar touching both: -1), 0 neither',
                     'offer_before_heat': '+1 offer first, -1 heat first (a bar touching both: -1), 0 neither',
                     'heat_before': 'largest adverse excursion before the target level was first touched'}[x['kind']],
           't': 'seconds from the entry bar end to the deciding bar end'}[r]
    return '%s; %s; window %d s of 3 s bars from the entry bar. known_at = entry bar end + window' % (base, txt, span_us(s, x) // US)


def catalog_text(subject, s):
    lines = ['# OUT catalog for %s from settings %s (%s VERSION %d); empty reasons: %s' % (subject, s['name'], TOOL, VERSION, ' '.join(sorted(REASONS))),
             '\t'.join(CAT_COLS)]
    for c in column_specs(s):
        lines.append('\t'.join(['OUT.%s.%s' % (subject, c['col']), 'ROWS', 'event', '0', 'coin', _meaning(s, c).replace('\t', ' '),
                                c['unit'], 'OUTCOME', 'OUT']))
    return '\n'.join(lines) + '\n'


# ------------------------------------------------------------------ prices: the one reader, listing state and vintage pins
class PriceSource:
    """labcore.prices.PriceCache (lab3.bins, the one reader of the 3 s bins) for one process, with the listing state of each (coin, day)
    from the PRICE index and that index's sha16 (the partition vintage), checked against the frozen pins before any bin of the day is read"""
    def __init__(self, lab_root, code_dir, pins=None):
        self.lab_root = lab_root; self.pc = prices.PriceCache(lab_root, 'research', code_dir); self.pins = pins; self.seen = {}; self.listed = {}

    def index_sha16(self, day):
        if day not in self.seen:
            try:
                ix = self.pc.R.index(day, 'PRICE')
            except LookupError:                                               # lab3 NotBuilt (a LookupError); refusals propagate
                self.seen[day] = 'NOT_BUILT'; self.listed[day] = set()
            else:
                self.seen[day] = ix['_sha16']; self.listed[day] = set(ix['coins'])
            if self.pins is not None and self.pins.get(day) != self.seen[day]:
                raise Refused('INPUT_CHANGED', 'PRICE %s index is %s, the run froze %s: refused (never repinned)' % (day, self.seen[day], self.pins.get(day)))
        return self.seen[day]

    def state(self, coin, day):
        if self.index_sha16(day) == 'NOT_BUILT':
            return 'NOT_BUILT'
        return 'LISTED' if coin in self.listed[day] else 'NO_COIN'

    def bars(self, coin, t0_us, t1_us):
        for d in days_between(day_of(t0_us - 1), day_of(t1_us)):
            self.index_sha16(d)
        return XE.bars(self.lab_root, coin, t0_us, t1_us, cache=self.pc)

    def drop_before(self, day):
        for k in [k for k in self.pc.mem if k[1] < day]:
            del self.pc.mem[k]


# ------------------------------------------------------------------ one path: entry and the non-exit labels
def entry_of(te, c, h, l, t_dec_us=None):
    """the factory's entry (factory_v2.trade): the first priced bar of the grid (which starts at the first bar ending at or after the
    decision + one bar) within 60 s -> index or -1"""
    ok = np.nonzero(np.isfinite(c) & np.isfinite(h) & np.isfinite(l))[0]
    ok = ok[ok * BAR_S <= WAIT_S]
    return int(ok[0]) if len(ok) else -1


class GridPath:
    """one event's 3 s grid in labcore.prices.PriceCache.path's shape, so the shared coverage rule reads exactly the bars a label reads"""
    def __init__(self, te, c, h, l):
        self.te, self.c, self.h, self.l = te, c, h, l

    def path(self, coin, t0_us, t1_us):
        m = (self.te > t0_us) & (self.te <= t1_us)
        return {'te_us': self.te[m], 'px': self.c[m], 'hi': self.h[m], 'lo': self.l[m]}


def first_gap_s(te, c, h, l, e, hold_s, gap_s):
    """seconds from the entry bar end to the start of the first hole of the hold (inf = none): label_ewsd_v2.path_first_gap, unchanged"""
    return LV2.path_first_gap(GridPath(te, c, h, l), '', int(te[e]) / US, hold_s, gap_s)


def label_path(x, c, h, l, e, p0, s, mult, gap_s=60, te=None, gaps=None):
    """one non-exit label on one priced path from entry bar e (price p0, side s, unit multiplier mult in pct) -> (value, t_s, reason).
    The window is floor(H / 3 s) bars after the entry bar (never a bar after it). A hole is LABEL_EWSD's: a stretch longer than gap_s
    without a valid bar (path_first_gap). A label decided before the first hole keeps its value, even on a truncated path; otherwise
    PATH_GAP (an interior hole) or NO_PATH (the path ends before the window). Touches compare the bar extreme with the price level."""
    hb = horizon_us(x) // BAR_US; n = len(c); kind = x['kind']
    if te is None:
        te = np.arange(n, dtype=np.int64) * BAR_US
    stop = min(e + hb, n - 1); complete = e + hb <= n - 1
    if not complete and kind in ('return', 'best', 'worst'):
        return np.nan, np.nan, 'NO_PATH'
    j = np.arange(e + 1, stop + 1); ok = np.isfinite(c[j]) & np.isfinite(h[j]) & np.isfinite(l[j])
    hold = (stop - e) * BAR_S
    if gaps is None or hold not in gaps:                                   # one coverage answer per hold (a caller's cache per path)
        g = first_gap_s(te, c, h, l, e, hold, gap_s)
        if gaps is not None:
            gaps[hold] = g
    else:
        g = gaps[hold]
    before = np.arange(1, len(j) + 1) * BAR_S <= g                         # bars ending at or before the start of the first hole
    hole = math.isfinite(g)
    tail = hole and not complete and not (ok & ~before).any()              # the only hole runs into the truncated end: a short path
    with np.errstate(invalid='ignore', divide='ignore'):
        fav = (np.where(s > 0, h[j] / p0 - 1, 1 - l[j] / p0) * 100.0) / mult
        adv = (np.where(s > 0, 1 - l[j] / p0, h[j] / p0 - 1) * 100.0) / mult

    def fav_hit(target):
        lv = p0 * (1 + s * float(target) * mult / 100.0)
        return (h[j] >= lv * (1 - TOUCH_RTOL)) if s > 0 else (l[j] <= lv * (1 + TOUCH_RTOL))

    def adv_hit(limit):
        lv = p0 * (1 - s * float(limit) * mult / 100.0)
        return (l[j] <= lv * (1 + TOUCH_RTOL)) if s > 0 else (h[j] >= lv * (1 - TOUCH_RTOL))

    def undecided(settled_zero):
        if hole and not tail:
            return np.nan, np.nan, 'PATH_GAP'
        if not complete:
            return np.nan, np.nan, 'NO_PATH'
        return settled_zero
    if kind == 'return':
        if hole:
            return np.nan, np.nan, 'PATH_GAP'
        last = c[e + hb]
        if not np.isfinite(last):                                           # the last close within gap_s of the end, never before the entry
            lo = max(e, e + hb - int(gap_s // BAR_S)); k = np.nonzero(np.isfinite(c[lo:e + hb + 1]))[0]
            last = c[lo + k[-1]] if len(k) else np.nan
        return (s * (last / p0 - 1) * 100.0 / mult, np.nan, '') if np.isfinite(last) else (np.nan, np.nan, 'NO_PRICE')
    if kind in ('best', 'worst'):
        if hole:
            return np.nan, np.nan, 'PATH_GAP'
        if not ok.any():
            return np.nan, np.nan, 'NO_PRICE'
        return max(0.0, float(np.max((fav if kind == 'best' else adv)[ok]))), np.nan, ''
    if kind in ('reach', 'heat_before'):
        hit = np.nonzero(ok & fav_hit(x['target']))[0]; i = int(hit[0]) if len(hit) else -1
        if i >= 0 and before[i]:
            if kind == 'reach':
                return 1.0, (i + 1) * BAR_S, ''
            return max(0.0, float(np.max(adv[:i + 1][ok[:i + 1]]))), (i + 1) * BAR_S, ''
        return undecided((0.0, np.nan, '') if kind == 'reach' else (np.nan, np.nan, 'NOT_REACHED'))
    if kind in ('first', 'offer_before_heat'):
        u_, d_ = (x['up'], x['down']) if kind == 'first' else (x['offer'], x['heat'])
        up = ok & fav_hit(u_); dn = ok & adv_hit(d_); any_ = np.nonzero(up | dn)[0]
        i = int(any_[0]) if len(any_) else -1
        if i >= 0 and before[i]:
            return (-1.0 if dn[i] else 1.0), (i + 1) * BAR_S, ''               # a bar touching both: adverse first
        return undecided((0.0, np.nan, ''))
    raise ValueError(kind)


# ------------------------------------------------------------------ the plan: selection, authorization, embargo (no price read)
def _whole(text, what, path, line):
    """the exact whole number a text writes (read as a decimal, never through a float); NaN, infinity and fractions are refused"""
    try:
        x = decimal.Decimal(str(text).strip())
    except (TypeError, ValueError, decimal.InvalidOperation):
        raise Refused('INVALID_EVENT_LIST', '%s line %d: %s %r is not a number' % (path, line, what, text))
    if not x.is_finite() or x != x.to_integral_value():
        raise Refused('INVALID_EVENT_LIST', '%s line %d: %s %r is not a whole number' % (path, line, what, text))
    return int(x)


def load_events(path):
    """the event list, strictly -> dict(coin, t, side, onset_t, trigger): columns coin and t required; coin [A-Za-z0-9_]+; t a whole unix
    second > 0; side -1, 0 or +1 (blank = 0); onset_t blank or whole with 0 < onset_t <= t; one identity per coin and second (coins compared
    without case); a bad row refuses the whole list by line (INVALID_EVENT_LIST), never skipped. The contract of event_profile.load_alarms
    (591f0e13341ade16, exact-decimal _whole) kept here so Outcomes no longer pins event_profile.py, which changes with Profile's own work
    (A51R fix check 3; Cause did the same); test_outcomes_v3 proves it equal to event_profile.load_alarms on the A02P list and refusals.
    The one shared event-list loader is a labcore candidate for LAB1."""
    with open(path) as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        R = list(rd); fields = rd.fieldnames or []
    if R and not {'coin', 't'} <= set(fields):
        raise Refused('INVALID_EVENT_LIST', '%s: the columns coin and t are required (got %s)' % (path, fields))
    coin, t, side, onset, trig = [], [], [], [], []; seen = {}
    for n, r in enumerate(R, start=2):
        c = (r.get('coin') or '').strip()
        if not c or not COIN_RE.fullmatch(c):
            raise Refused('INVALID_EVENT_LIST', '%s line %d: coin %r' % (path, n, r.get('coin')))
        tt = _whole(r.get('t'), 't', path, n)
        if tt <= 0:
            raise Refused('INVALID_EVENT_LIST', '%s line %d: t %d' % (path, n, tt))
        key = (c.upper(), tt)
        if key in seen:
            raise Refused('INVALID_EVENT_LIST', '%s line %d: duplicate event identity (coin %s, t %d), first on line %d' % (path, n, c, tt, seen[key]))
        seen[key] = n
        sd = 0 if (r.get('side') or '').strip() == '' else _whole(r.get('side'), 'side', path, n)
        if sd not in (-1, 0, 1):
            raise Refused('INVALID_EVENT_LIST', '%s line %d: side %r must be -1, 0 or +1' % (path, n, r.get('side')))
        given = (r.get('onset_t') or '').strip() != ''
        ot = _whole(r.get('onset_t'), 'onset_t', path, n) if given else -1
        if given and not 0 < ot <= tt:
            raise Refused('INVALID_EVENT_LIST', '%s: an onset after its event (line %d)' % (path, n))
        coin.append(c); t.append(tt); side.append(sd); onset.append(ot); trig.append((r.get('trigger') or '').strip())
    return dict(coin=np.array(coin), t=np.array(t, np.int64), side=np.array(side, int), onset_t=np.array(onset, np.int64), trigger=np.array(trig))


def alarm_wins():
    """aw1: the alarm kit's window classes (WINDOWS_ALARM_V1.tsv, its sha16 checked); WINDOWS_V1 is unchanged"""
    if ids.sha16_file(WINDOWS_ALARM) != WINDOWS_ALARM_SHA16:
        raise Refused('ALARM_WINDOWS_CHANGED', '%s is not sha16 %s' % (WINDOWS_ALARM, WINDOWS_ALARM_SHA16))
    return gates.windows(WINDOWS_ALARM)


def authorize(window, months, now_utc, law=None, wins=None):
    """THE canonical outcome authorization (labcore.gates.outcome_allowed: lab3/law.py seal + WINDOWS_V1 classes) of the months the run
    reads, under the caller's window; a refusal is OUTCOME_REFUSED by name"""
    a, b = window
    try:
        gates.outcome_allowed({'outcome_months': months_between(a, b)}, sorted(months), now_utc=now_utc, law=law, wins=wins or alarm_wins())   # aw1
    except PermissionError as e:
        raise Refused('OUTCOME_REFUSED', str(e))


COIN_RE = re.compile(r'[A-Za-z0-9_]+\Z')


def admit(first, last, window):
    """A51R2-01 (S3): THE first check of every entry path, before any file is opened: first..last real days, in order, inside the caller's
    authorized window (labcore.v2_7.selection.check_window, pure) -> (first, last, (win_first, win_last))"""
    if window is None:
        raise Refused('NO_RUN_WINDOW', 'the caller names its authorized outcome window (run setting run_window or --run-window): none given')
    try:
        f, l, w = S.check_window(first, last, tuple(window))
    except S.SelectionRefused as e:
        code = {'MALFORMED_DATE': 'BAD_DATES', 'REVERSED_RANGE': 'BAD_DATES', 'BAD_WINDOW': 'NO_RUN_WINDOW'}.get(e.code, e.code)
        raise Refused(code, str(e))
    return f, l, w


def roster_of(lab_root, code_dir, first, last, window=None):
    """the date-effective coin roster of the lab: every coin listed in the lab_days PRICE index of a day first..last (the canonical
    reader, research seal) -> (set of coins, {day: index sha16 or NOT_BUILT})"""
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as LD
    R = LD.Days(lab_root, 'research'); coins = set(); seen = {}; inside = S.in_window(window)
    for d in days_between(first, last):
        if not inside(d):                                                     # S3: a roster scan opens window days only
            continue
        try:
            ix = R.index(d, 'PRICE')
        except LD.NotBuilt:
            seen[d] = 'NOT_BUILT'; continue
        coins |= set(ix['coins']); seen[d] = ix['_sha16']
    return coins, seen


def selection_of(coins=None, group=None, group_file=None, roster=None):
    """C1 (LEAD ruling 25 Oct): --coins A,B | ALL filters the given event list; every named coin must be on the lab's date-effective
    roster (roster_of); a coin with no event in the list and dates is an explicit empty selection, never an error. --group refuses
    SELECTOR_NOT_RELEASED until the ONE shared selector (labcore/selection.py, ctxprof_shared's labcore V2_7 candidate, then LAB1) lands.
    -> (set of coins or None for all, the record the manifest keeps)"""
    if group or group_file:
        raise Refused('SELECTOR_NOT_RELEASED', 'named groups need the shared selector labcore/selection.py (ctxprof_shared, labcore V2_7 '
                                               'candidate, then LAB1): not released, so --group is refused')
    if coins is None or str(coins).upper() == 'ALL':
        return None, {'kind': 'all'}
    want = sorted({c.strip() for c in str(coins).split(',') if c.strip()})
    bad = [c for c in want if not COIN_RE.fullmatch(c)]
    if not want or bad:
        raise Refused('INVALID_COIN', 'coins %r' % (bad or coins,))
    off = sorted(set(want) - set(roster or ()))
    if off:
        raise Refused('UNKNOWN_COIN', 'coins %s are on no lab_days PRICE roster day of the selection' % off)
    return set(want), {'kind': 'coins', 'coins': want}


def plan(events_path, s, subject, first, last, window, now_utc=None, law=None, wins=None, only=None):
    """every admission check before any data read -> the plan: selected events (sorted by t, coin), per-event first grid bar, end of the
    entry wait, the labels each may compute and the latest bar its window could need; the authorization of every month read"""
    if not (isinstance(subject, str) and NAME_RE.fullmatch(subject)):
        raise Refused('BAD_SUBJECT', 'subject %r: capitals, digits and single _' % (subject,))
    try:
        first, last = valid_day(first), valid_day(last)
    except ValueError as e:
        raise Refused('BAD_DATES', str(e))
    if first > last:
        raise Refused('BAD_DATES', 'first %s after last %s' % (first, last))
    if window is None:
        raise Refused('NO_RUN_WINDOW', 'the caller names its authorized outcome window (run setting run_window or --run-window): none given')
    wf, wl = check_window(window) if isinstance(window, dict) else window
    if not (wf <= first and last <= wl):
        raise Refused('SELECTION_OUTSIDE_WINDOW', 'selection %s-%s is not inside the authorized outcome window %s-%s' % (first, last, wf, wl))
    ev = load_events(events_path)
    days = np.array([day_of(int(t) * US) for t in ev['t']]) if len(ev['t']) else np.array([], str)
    sel = np.flatnonzero((days >= first) & (days <= last)) if len(days) else np.zeros(0, int)
    if only is not None:                                                     # a coin selection (selection_of) filters the list
        sel = sel[np.isin(ev['coin'][sel], sorted(only))]
    sel = sel[np.lexsort((ev['coin'][sel], ev['t'][sel]))]
    keys = [(str(ev['coin'][i]), int(ev['t'][i])) for i in sel]
    win_end = day_start_us(wl) + DAY_US                                    # the first microsecond after the authorized window
    delay_us = int(round(float(s['entry']['delay_s']) * US))
    spans = {x['name']: span_us(s, x) for x in s['labels']}
    E = []
    for coin, F in keys:
        t_dec = F * US + delay_us; g0 = ((t_dec + BAR_US - 1) // BAR_US) * BAR_US + BAR_US; w_end = g0 + WAIT_S * US
        ok = {n: (w_end + sp < win_end) for n, sp in spans.items()}           # the latest bar the window could need, strictly inside
        E.append(dict(coin=coin, F=F, t_dec=t_dec, g0=g0, wait_end=w_end, entry_ok=w_end < win_end, label_ok=ok,
                      read_end=max([w_end] + [w_end + spans[n] for n, v in ok.items() if v])))
    need = {d[:6] for d in set(days[sel].tolist())} | {day_of(e['read_end'])[:6] for e in E if e['entry_ok']}
    if E:
        authorize((wf, wl), need, now_utc or utc_now(), law=law, wins=wins)
    return dict(first=first, last=last, window=(wf, wl), win_end=win_end, keys=keys, side=ev['side'][sel].astype(int), days=days[sel],
                events=E, spans=spans, months=sorted(need))


def price_days(P):
    """every PRICE day the plan may read (first grid bar - 1 us to the latest eligible bar)"""
    out = set()
    for e in P['events']:
        if e['entry_ok']:
            out.update(days_between(day_of(e['g0'] - 1), day_of(e['read_end'])))
    return sorted(out)


def funding_keys(P, s):
    """(coin, month) of every funding month a money_full label may read (hours ending in (entry, exit] within the eligible window)"""
    if not any(x['kind'] == 'money_full' for x in s['labels']):
        return []
    out = set()
    for e in P['events']:
        if e['entry_ok']:
            for m in months_between(day_of(e['g0']), day_of(e['read_end'])):
                out.add((e['coin'], m))
    return sorted(out)


def funding_store(s):
    return json.load(open(fpath(s['money']['cost_settings']['path'])))['funding_store']


# ------------------------------------------------------------------ dependencies, inventory and input pins
def load_deps(s, roots, code_dir):
    """import every module the run needs, in every process alike (so the inventory is the run's full transitive code)"""
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as _d, bins as _b, write as _w                    # noqa: F401  the reader, the bins, the writer
    mods = {}
    if any(x['kind'] == 'money_full' for x in s['labels']):
        import factory_v2 as FX2                                            # noqa: F401  (sys.path: tools/factory)
        mods['FX2'] = FX2
    if any(b.startswith('EPI:') for b in s['units'].values()):
        import alarm_profile as AP
        mods['AP'] = AP
    if any(not b.startswith('EPI:') for b in s['units'].values()) or roots.get('CAUSE2'):
        mods['ES'] = __import__('event_situations')
    return mods


if os.path.join(TOOLS, 'factory') not in sys.path:
    sys.path.insert(1, os.path.join(TOOLS, 'factory'))
if os.path.join(TOOLS, 'alarm_profile') not in sys.path:
    sys.path.insert(1, os.path.join(TOOLS, 'alarm_profile'))


def inventory(extra=()):
    """{path relative to forensics: sha16} of every loaded module file under the forensics folder (the transitive code this process
    runs), this file and the executed launcher"""
    files = set()
    for name, m in list(sys.modules.items()):
        f = getattr(m, '__file__', None)
        if name == '__main__':
            continue                                                         # a calling script is not the run's code (this file is added)
        if f and f.endswith('.py'):
            p = os.path.realpath(f)
            if p.startswith(FORENSICS + os.sep) and os.sep + 'tests' + os.sep not in p and not os.path.basename(p).startswith('test_'):
                files.add(p)
    files.add(os.path.realpath(__file__)); files.update(os.path.realpath(x) for x in extra)
    return {os.path.relpath(p, FORENSICS): ids.sha16_file(p) for p in sorted(files)}


def fresh_inventory(settings_path, code_dir, roots):
    """the inventory a worker process computes (a fresh python: load_settings + load_deps), whatever the caller imported"""
    out = subprocess.check_output([sys.executable, '-B', os.path.realpath(__file__), 'inventory', settings_path, code_dir, json.dumps(roots)],
                                  env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    return json.loads(out.decode().strip().splitlines()[-1])


def check_closure(inv, man_path=RELEASE):
    """every code file this process loaded is pinned, with the same sha16, somewhere in the release graph; else refused"""
    pins = {}
    def walk(p, seen=set()):
        p = os.path.realpath(p)
        if p in seen:
            return
        seen.add(p); m = json.load(open(p))
        for f, pin in m['files'].items():
            pins[f] = pin.get('sha16')
        for r in m.get('releases', {}):
            walk(os.path.join(FORENSICS, r))
    walk(man_path, set())
    bad = ['%s (%s)' % (f, 'unpinned' if f not in pins else 'pinned %s, now %s' % (pins[f], sha)) for f, sha in sorted(inv.items()) if pins.get(f) != sha]
    if bad:
        raise Refused('CLOSURE', 'loaded code not pinned by the release graph: %s' % '; '.join(bad))


def epi_binds(s):
    return {u: b.split(':', 1)[1] for u, b in s['units'].items() if b.startswith('EPI:')}


def input_pins(P, s, lab_root, code_dir, research_root):
    """the vintage of every input partition and file the run reads: PRICE index per day, EPI index per event day, funding month files"""
    sys.path.insert(0, code_dir)
    from lab3 import days as LD
    R = LD.Days(lab_root, 'research'); out = {'PRICE': {}, 'EPI': {}, 'FUNDING': {}}
    for d in price_days(P):
        try:
            out['PRICE'][d] = R.index(d, 'PRICE')['_sha16']
        except LD.NotBuilt:
            out['PRICE'][d] = 'NOT_BUILT'
    if epi_binds(s):
        RR = LD.Days(research_root, 'research')
        for u, b in sorted(epi_binds(s).items()):
            part = 'EPI.%s' % b.split('.', 1)[0]
            for d in sorted(set(P['days'].tolist())):
                k = '%s/%s' % (part, d)
                out['EPI'][k] = RR.index(d, part)['_sha16'] if part in RR.parts(d) else 'NOT_BUILT'
    if any(x['kind'] == 'money_full' for x in s['labels']):
        st = funding_store(s)
        for coin, m in funding_keys(P, s):
            p = os.path.join(st, coin, '%s.tsv' % m)
            out['FUNDING']['%s/%s' % (coin, m)] = ids.sha16_file(p) if os.path.exists(p) else 'MISSING'
    return out


def config_pins(s, events_path, extra=None):
    """A51R-01: {name: {path, sha16}} of EVERY configured non-code file the run reads, whether or not a release pins it: the settings, the
    event list, the static cost table, the exits registry, the money cost settings and every table it names, the authorization tables
    (lab3/law.py, freeze_judge WINDOWS_V1), a selection's group file. Frozen at admission, rechecked by every worker before it reads and
    before it writes, and by run before the commit; a changed file is INPUT_CHANGED (never re-pinned)."""
    files = {'settings': s['_path'], 'events': os.path.abspath(events_path), 'law': gates.LAW, 'windows': WINDOWS_ALARM}   # aw1: the table that classed the months
    if 'cost' in s:
        files['cost_table'] = fpath(s['cost']['table'])
    if 'exits' in s:
        files['exits'] = s['_exits_path']
    if any(x['kind'] == 'money_full' for x in s['labels']):
        cs = fpath(s['money']['cost_settings']['path']); files['cost_settings'] = cs
        S = json.load(open(cs))
        for k, v in sorted(S.items()):
            if isinstance(v, dict) and v.get('path'):
                files['cost_settings:%s' % k] = fpath(v['path'])
                if v.get('sha16') and ids.sha16_file(fpath(v['path'])) != v['sha16']:
                    raise Refused('INPUT_CHANGED', 'cost settings %s names %s sha16 %s, the file is %s' % (cs, k, v['sha16'], ids.sha16_file(fpath(v['path']))))
    files.update(extra or {})
    out = {}
    for k, p in sorted(files.items()):
        if not os.path.isfile(p):
            raise Refused('INPUT_MISSING', 'configured file %s (%s) is missing' % (k, p))
        out[k] = {'path': os.path.realpath(p), 'sha16': ids.sha16_file(p)}
    return out


def check_config(frozen_config, when):
    """every frozen configured file still has its frozen sha16 (A51R-01)"""
    bad = []
    for k, x in sorted(frozen_config.items()):
        now = ids.sha16_file(x['path']) if os.path.isfile(x['path']) else 'MISSING'
        if now != x['sha16']:
            bad.append('%s %s is %s, frozen %s' % (k, x['path'], now, x['sha16']))
    if bad:
        raise Refused('INPUT_CHANGED', 'configured file changed %s: %s (never re-pinned)' % (when, '; '.join(bad)))


def part_days(LD, root, part):
    """the canonical lab3 reader (Days, research purpose: the seal, block sha16 and shape checks, stale-input checks unchanged) that lists
    only one part and the parts its index names as inputs, so finding a code does not parse every other part's index of the day (about
    170 parts a research day). The code names of a part (EPI.<subject>.<column>) live only in that part."""
    class OnePart(LD.Days):
        def parts(self, day):
            allp = LD.Days.parts(self, day)
            if part not in allp:
                return []
            keep = {part} | set(self.index(day, part).get('inputs', {}))
            return [p for p in allp if p in keep]
    return OnePart(root, 'research')


# ------------------------------------------------------------------ units read at F
def read_units(P, s, mods, code_dir, research_root, roots, subject, frozen_inputs=None):
    """-> {unit: (value[], known_at_us[], reason[])} over the selected events: c from the static cost of record (fallback by the
    settings), EPI units through alarm_profile.read (its stored known_at, never after the decision), CTX / EPG / CAUSE2 units (and Cause's
    side_used) through event_situations.read_inputs; a missing or late unit is EMPTY with its reason"""
    keys = P['keys']; n = len(keys); t_dec = np.array([e['t_dec'] for e in P['events']], np.int64); out = {}
    if 'c' in _unit_names(s):
        v = np.asarray(costs.cost_c(s, [k[0] for k in keys])[0], float) if n else np.zeros(0)
        fbc = {c: costs.cost_c(s, [c])[1] for c in sorted({k[0] for k in keys})}
        fb = np.array([fbc[k[0]] for k in keys], float) if n else np.zeros(0)
        why = np.array(['' if not f else ('NO_UNIT:COST_FALLBACK' if s['cost'].get('fallback', 'unknown') == 'unknown' else '') for f in fb], object)
        out['c'] = (np.where(why == '', v, np.nan), np.array([k[1] * US for k in keys], np.int64), why)
        out['_c_fallback'] = fb
    for u, b in sorted(epi_binds(s).items()):
        subj, col = b.split('.', 1); part = 'EPI.%s' % subj
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        RR = part_days(LD, research_root, part)
        for d in sorted(set(P['days'].tolist())):
            k = '%s/%s' % (part, d); now = RR.index(d, part)['_sha16'] if part in RR.parts(d) else 'NOT_BUILT'
            if frozen_inputs is not None and frozen_inputs['EPI'].get(k) != now:
                raise Refused('INPUT_CHANGED', 'EPI %s index is %s, the run froze %s: refused' % (k, now, frozen_inputs['EPI'].get(k)))
        code = mods['AP'].code_name(subj, col)                              # alarm_profile's own naming of the stored EPI code
        m = {}                                                                # (coin, F) -> (v, e, k): value, reason byte, stored known_at
        for d in sorted({x for x in set(P['days'].tolist()) if part in RR.parts(x)}):
            want = sorted({c for (c, F), dd in zip(keys, P['days']) if dd == d})
            rows = RR.rows(code, d, want)                                     # the canonical lab3 reader: value, kind, reason, stale, clock
            for coin, x in rows.items():
                if x is None:
                    continue
                for vk, b, er, st, ka, a in zip(x['value_kind'], x['value_bits'], x['empty_reason'], x['stale'], x['known_at_us'], x['as_of_us']):
                    key = (coin, int(a) // US)
                    if key in m:
                        raise Refused('DUPLICATE_SOURCE_ROW', '%s %s: two rows for (%s, %d)' % (code, d, coin, key[1]))
                    v = float(np.array([b], '<u8').view('<f8')[0]) if (vk == 1 and b is not None) else np.nan
                    m[key] = (v, er or ('STALE' if st else ''), int(ka))
        built = {d for d in set(P['days'].tolist()) if part in RR.parts(d)}
        vals = np.full(n, np.nan); kat = np.full(n, -1, np.int64); why = np.full(n, '', object)
        for i, (coin, F) in enumerate(keys):
            if P['days'][i] not in built:
                why[i] = 'NO_UNIT:NOT_BUILT'; continue
            if (coin, F) not in m:
                why[i] = 'NO_UNIT:NO_ROW'; continue
            v, er, k = m[(coin, F)]
            if k != Q.INT64_MIN and k >= 0:
                kat[i] = k                                                    # A51R2-03: the source's own clock, kept even when refused
            ok = bool(Q.known(np.array([v]), e=np.array([0 if not er else 1]), k=np.array([k], np.int64), col_us=np.array([t_dec[i]], np.int64))[0])
            if ok and v > 0:
                vals[i] = v                                                   # A51R2-02 (S2): only a KNOWN cell (labcore v2_7 quality.known)
            elif er:
                why[i] = 'NO_UNIT:SOURCE_%s' % re.sub(r'[^A-Za-z0-9_]', '_', er)[:40]
            elif not math.isfinite(v):
                why[i] = 'NO_UNIT:EMPTY'
            elif k == Q.INT64_MIN or k < 0:
                why[i] = 'NO_UNIT:NO_KNOWN_AT'
            elif k > t_dec[i]:
                why[i] = 'NO_UNIT:KNOWN_AFTER_DECISION'
            else:
                why[i] = 'NO_UNIT:NOT_POSITIVE'
        out[u] = (vals, kat, why)
    rest = {u: b for u, b in s['units'].items() if not b.startswith('EPI:')}
    if roots.get('CAUSE2'):
        rest['_side'] = 'CAUSE2:side_used'
    if rest and n:
        W = {}
        X = ES.read_inputs(dict(inputs=rest), code_dir, subject, P['first'], P['last'], keys, {k: roots.get(k) for k in ('CTX', 'EPG', 'CAUSE2')},
                           why=W)
        for u in rest:
            v = np.asarray(X[u], float); w = np.asarray(W.get(u, np.full(n, '', object)), object)
            w = np.array([('NO_UNIT:%s' % x) if x else ('' if math.isfinite(y) else 'NO_UNIT:EMPTY') for x, y in zip(w, v)], object)
            if u != '_side':
                w = np.array([x or ('NO_UNIT:NOT_POSITIVE' if not y > 0 else '') for x, y in zip(w, v)], object)
            out[u] = (np.where(w == '', v, np.nan), np.array([k[1] * US for k in keys], np.int64), w)
    return out


# ------------------------------------------------------------------ the labels of one selection
def frozen_exit(s, inv):
    """exit_engine's frozen call boundary: the registry, its schema and row sha16, the cost table of record, the engine module and the
    run's transitive inventory (absolute paths: the engine checks them file by file)"""
    ep = s['_exits_path']
    with open(ep, encoding='utf-8') as f:
        header = next((l.rstrip('\n') for l in f if not l.startswith('#')), '')
    eng = {os.path.realpath(XE.__file__)} | {os.path.realpath(sys.modules[m].__file__) for m in ('labcore', 'labcore.costs', 'labcore.ids',
                                                                                                   'labcore.lookahead', 'labcore._rows', 'labcore.prices')}
    deps = {os.path.join(FORENSICS, p): sha for p, sha in inv.items() if os.path.join(FORENSICS, p) in eng}   # the engine's own code, from the frozen inventory
    if len(deps) != len(eng):
        raise Refused('CODE_CHANGED', 'the exit engine\'s code is not all in the frozen inventory: %s' % sorted(eng - set(deps)))
    out = {}
    for x in s['labels']:
        if x['kind'] in PATH_KINDS:
            out[x['exit_id']] = dict(exits_path=ep, exit_row_sha16=XE.row_sha16(ep, x['exit_id']), exits_schema_sha16=ids.sha16_text(header),
                                     cost_table=fpath(s['cost']['table']), cost_sha16=s['cost']['sha16'],
                                     module_sha16=ids.sha16_file(os.path.realpath(XE.__file__)), dependency_sha16=deps)
    return out


def compute(P, s, src, U, mods, frozen, log=print, frozen_inputs=None, gate=True):
    """-> vals, why, kat {column: array over the selected events}"""
    keys = P['keys']; n = len(keys); cols = column_specs(s)
    vals = {c['col']: (np.full(n, np.nan) if c['kind'] == 'number' else np.full(n, '', object)) for c in cols}
    why = {c['col']: np.full(n, '', object) for c in cols}; kat = {c['col']: np.zeros(n, np.int64) for c in cols}
    push = P['side'].astype(float).copy()
    if '_side' in U:
        sv = U['_side'][0]; push = np.where((push == 0) & np.isfinite(sv), np.sign(np.nan_to_num(sv)), push)
    dsign = {'FADE': -1, 'FOLLOW': 1}
    gap_s = float(s['entry']['gap_s']); C = None; size = None; fund_ok = {}
    if any(x['kind'] == 'money_full' for x in s['labels']):
        C = mods['FX2'].costs_of({'cost_settings': s['money']['cost_settings']['path']}, {}); size = float(s['money']['size_usd'])
    by_label = {}
    for c in cols:
        if c['label'] is not None:
            by_label.setdefault((c['label']['name'], c['dir']), []).append(c)
    unit_cols = [c for c in cols if c['role'] in ('unit', 'unit_fallback')]
    cur = None; t_read = 0.0; census = {'trades': 0, 'path_uncertain': 0, 'noprice': 0, 'funding_missing': 0, 'no_cost': 0}
    for r, (coin, F) in enumerate(keys):
        E = P['events'][r]; d = P['days'][r]
        if d != cur:
            if gate:
                gate_wait(log=log)                                    # the recorder gate between days (never kills a running day)
            if src is not None:
                src.drop_before(day_of(day_start_us(d) - DAY_US))
            cur = d
        for c in unit_cols:                                                   # units are inputs at F: published for every event
            u = c['unit_name']
            if c['role'] == 'unit_fallback':
                vals[c['col']][r] = U['_c_fallback'][r]; kat[c['col']][r] = F * US; continue
            v, k, w = U[u]; vals[c['col']][r] = v[r]; why[c['col']][r] = w[r]; kat[c['col']][r] = k[r] if k[r] >= 0 else E['t_dec']

        def put(col, v, reason, clock):
            if isinstance(v, str):
                vals[col][r] = v
            elif v is not None:
                vals[col][r] = v
            why[col][r] = reason; kat[col][r] = int(clock)

        def fill(reason, clock_of):
            for c in cols:
                if c['role'] in ('unit', 'unit_fallback'):
                    continue
                put(c['col'], None, reason, clock_of(c))
        span_of = lambda c: P['spans'][c['label']['name']] if c['label'] is not None else 0
        if not E['entry_ok']:
            fill('EMBARGO_SUPPORT', lambda c: E['wait_end'] + span_of(c)); continue
        dd = days_between(day_of(E['g0'] - 1), day_of(E['read_end'])); avail_end = None; bad = ''
        for day in dd:
            st = src.state(coin, day)
            if st != 'LISTED':
                avail_end = day_start_us(day); bad = st; break
        t1 = E['read_end'] if avail_end is None else min(E['read_end'], avail_end - 1)
        if t1 < E['g0']:
            fill(bad if bad else 'NO_PATH', lambda c: E['wait_end'] + span_of(c)); continue
        a = time.time(); te, c_, h, l = src.bars(coin, E['g0'], t1); t_read += time.time() - a
        e = entry_of(te, c_, h, l, E['t_dec'])
        if e < 0:
            rs = bad if (avail_end is not None and avail_end <= E['wait_end']) else 'NO_ENTRY'
            fill(rs, lambda c: E['wait_end'] + span_of(c)); continue
        p0 = float(c_[e]); ent = int(te[e])
        put('entry__px', p0, '', ent); put('entry__s', (ent - F * US) / US, '', ent)
        short = 'NOT_LISTED' if bad == 'NO_COIN' else (bad or 'NO_PATH')     # the reason of a window cut by a later unavailable day
        sides = {dn: ((1 if dn == 'LONG' else -1) if dn in ('LONG', 'SHORT') else int(dsign[dn] * push[r])) for dn in s['directions']}
        trades = {}; gaps = {}

        def trade(exit_id, row, u, side):
            """one frozen exit-engine call per event and exit row, every traded side at once -> the side's result"""
            if exit_id not in trades:
                sd = sorted({v for v in sides.values() if v != 0}); m = len(sd)
                units = {'known_at_us': np.array([U[u][1][r] if u != 'pct' else F * US] * m, np.int64)}
                if u != 'pct':
                    units[u] = np.array([U[u][0][r]] * m, float)
                o = XE.run_frozen(c_, h, l, [e] * m, [p0] * m, sd, row, frozen[exit_id], units=units, t0_us=int(te[0]), signal_us=[E['t_dec']] * m)
                if set(np.asarray(o['price_model']).tolist()) != {'SIMULATED_BINANCE_3S_ADVERSE_FIRST'} or set(np.asarray(o['price_venue']).tolist()) != {'BINANCE'}:
                    raise Refused('PRICE_MODEL', 'exit engine price model / venue is not the one this catalog names')
                trades[exit_id] = {v: {k: (o[k][i] if hasattr(o[k], '__len__') and not isinstance(o[k], str) else o[k]) for k in o} for i, v in enumerate(sd)}
                census['trades'] += m; census['noprice'] += int((np.asarray(o['kind']) == 'noprice').sum())
                census['path_uncertain'] += int((np.asarray(o['path_evidence_status']) == 'PATH_UNCERTAIN').sum())
            return trades[exit_id][side]
        for dname in s['directions']:
            side = sides[dname]
            for x in s['labels']:
                cs = by_label[(x['name'], dname)]; end = ent + P['spans'][x['name']]
                if side == 0:
                    for cc in cs:
                        put(cc['col'], None, 'NO_DIRECTION', E['t_dec'])
                    continue
                if not E['label_ok'][x['name']]:
                    for cc in cs:
                        put(cc['col'], None, 'EMBARGO_SUPPORT', end)
                    continue
                if x['kind'] in PATH_KINDS:
                    row = s['_exits'][x['exit_id']]; u = row['unit']
                    if u != 'pct' and (u not in U or not math.isfinite(U[u][0][r])):
                        w = U[u][2][r] if u in U and U[u][2][r] else 'NO_UNIT'
                        for cc in cs:
                            put(cc['col'], None, w, E['t_dec'])
                        continue
                    o = trade(x['exit_id'], row, u, side); kind = str(o['kind']); col = {cc['role']: cc['col'] for cc in cs}
                    if kind == 'noprice':
                        rs = short if len(te) - 1 < e + XE.bars_of(row['time_limit_min']) else 'NO_PATH'
                        for cc in cs:
                            put(cc['col'], None, rs, end)
                        continue
                    xu = int(o['exit_us']); ev = str(o['path_evidence_status']); booked = float(o['ret_pct'])
                    put(col['t'], (xu - ent) / US, '', xu); put(col['how'], kind, '', xu); put(col['evidence'], ev, '', xu)
                    put(col['holes'], float(o['hole_bars']), '', xu); put(col['booked'], booked, '', xu)
                    if x['kind'] == 'exit':
                        put(col['value'], booked if ev == 'CLEAN' else None, '' if ev == 'CLEAN' else 'PATH_UNCERTAIN', xu)
                        continue
                    cpct, fok = mods['FX2'].trade_cost(C, coin, side, ent, xu, size)          # the factory's money of record, unchanged
                    parts = C.trade_cost([coin], [int(side)], [ent], [xu], [size])
                    pre = (float(parts['fee_bp'][0]) + float(parts['book_bp'][0]) + float(parts['gap_bp'][0])) / 100.0
                    fund = float(parts['funding_bp'][0]) / 100.0
                    nocost = not math.isfinite(pre)
                    for k_ in ('fee', 'book', 'gap'):                         # A51-06 acceptance 2: the three parts persisted, not only their sum
                        v_ = float(parts['%s_bp' % k_][0]) / 100.0
                        put(col[k_], v_ if math.isfinite(v_) else None, '' if math.isfinite(v_) else 'NO_COST', xu)
                    put(col['cost_prefunding'], pre if not nocost else None, 'NO_COST' if nocost else '', xu)
                    put(col['funding'], fund if math.isfinite(fund) else None, '' if math.isfinite(fund) else 'FUNDING_MISSING', xu)
                    put(col['funding_ok'], 1.0 if math.isfinite(fund) else 0.0, '', xu)
                    census['funding_missing'] += (not math.isfinite(fund)); census['no_cost'] += nocost
                    rs = 'NO_COST' if nocost or not math.isfinite(cpct) else ('PATH_UNCERTAIN' if ev != 'CLEAN' else ('FUNDING_MISSING' if fok != 1 or not math.isfinite(fund) else ''))
                    put(col['value'], booked - cpct if not rs else None, rs, xu)
                    continue
                cv = {cc['role']: cc['col'] for cc in cs}; un = x.get('unit', 'pct')
                if un == 'pct':
                    mv = 1.0; uw = ''
                else:
                    mv = U[un][0][r] if un in U else np.nan; uw = (U[un][2][r] if un in U else '') or ('NO_UNIT' if not math.isfinite(mv) else '')
                if uw:
                    for cc in cs:
                        put(cc['col'], None, uw, E['t_dec'])
                    continue
                v, ts, rs = label_path(x, c_, h, l, e, p0, side, mv, gap_s, te=te, gaps=gaps)
                if rs == 'NO_PATH':
                    rs = short
                put(cv['value'], v if not rs else None, rs, end)
                if 't' in cv:
                    tr = rs or ('' if np.isfinite(ts) else 'NOT_REACHED')
                    put(cv['t'], ts if not tr else None, tr, end)
    return vals, why, kat, dict(census, t_read_s=t_read)


# ------------------------------------------------------------------ writing one selection (a worker)
def _write_days(out_root, code_dir, subject, s, P, vals, why, kat, srcs, seal, write=None, log=print):
    sys.path.insert(0, code_dir)
    from lab3 import write as LW
    if write is None:
        write = LW.write_part
    os.makedirs(os.path.join(out_root, VERIFIED), exist_ok=True)
    cat_path = os.path.join(out_root, 'OUT_CATALOG_%s.tsv' % subject)
    tmp = '%s.tmp%d' % (cat_path, os.getpid()); open(tmp, 'w').write(catalog_text(subject, s)); os.replace(tmp, cat_path)
    cat = LW.load_catalog(cat_path); cols = column_specs(s); keys = P['keys']; done = 0
    for day in sorted(set(P['days'].tolist())):
        idx = np.flatnonzero(P['days'] == day); coins = sorted({keys[j][0] for j in idx}); codes = {}
        for c in cols:
            col = c['col']; rr = {}
            for coin in coins:
                cc = {k: [] for k in ROWCOLS}
                for j in idx:
                    if keys[j][0] != coin:
                        continue
                    cc['day'].append(int(day)); cc['as_of_us'].append(keys[j][1] * US); cc['known_at_us'].append(int(kat[col][j])); cc['stale'].append(0)
                    v = vals[col][j]; w = why[col][j]
                    if c['kind'] == 'word':
                        ok = v != '' and not w; cc['value_kind'].append(3 if ok else 0); cc['value_bits'].append(None)
                        cc['value_txt'].append(str(v) if ok else None); cc['empty_reason'].append('' if ok else w)
                    else:
                        ok = bool(np.isfinite(v)) and not w; cc['value_kind'].append(1 if ok else 0)
                        cc['value_bits'].append(int(np.array([float(v)], '<f8').view('<u8')[0]) if ok else None)
                        cc['value_txt'].append(None); cc['empty_reason'].append('' if ok else w)
                    if not ok and not cc['empty_reason'][-1]:
                        raise RuntimeError('%s %s %s: an empty cell without its reason (a defect, never written)' % (col, coin, keys[j][1]))
                rr[coin] = cc
            codes['OUT.%s.%s' % (subject, col)] = {'step': 'event', 'kind': 'WORD' if c['kind'] == 'word' else 'NUMBER', 'rows': rr}
        write(out_root, int(day), 'OUT.%s' % subject, codes, coins, catalog=cat, sources=srcs, seal=seal); done += 1
        if os.path.exists(os.path.join(out_root, 'day=%s' % day, 'OUT.%s' % subject, 'index.json')):   # read the written day back, keep the receipt
                                                                             # (a planted writer writes nothing; run refuses a day without one)
            want = {}
            for j in idx:
                want.setdefault(keys[j][0], []).append(keys[j][1] * US)
            rc = verify_day(out_root, code_dir, s, subject, day, want, {k: srcs[k] for k in ('inventory', 'window')})
            RM.write_json_atomic(os.path.join(out_root, VERIFIED, '%s.json' % day), rc)
        log('DAY %s OUT.%s events %d WRITTEN' % (day, subject, len(idx)))
        if os.environ.get(FAULT_ENV) == 'fail_after:%s' % day:            # fault injection (acceptance only): this worker dies here
            raise RuntimeError('FAULT INJECTED after day %s (%s)' % (day, FAULT_ENV))
        if os.environ.get(FAULT_ENV) == 'hold_after:%s' % day:            # fault injection: this worker waits here, so an interrupt
            time.sleep(120)                                                   # always lands mid-run (deterministic, A51R2 K2)
    return done


FROZEN = 'RUN_FROZEN.json'
FAULT_ENV = 'EVENT_OUTCOMES_FAULT'     # acceptance fault injection only: 'fail_after:<day>' / 'hold_after:<day>': the worker that wrote <day>


def _stage_header(out_root):
    """the frozen identity of the run whose staging folder out_root is (None: not a stage); a committed or failed root is refused"""
    if os.path.exists(os.path.join(out_root, '%s.json' % MANIFEST)) or os.path.exists(os.path.join(out_root, 'FAILED.json')):
        raise Refused('NOT_A_STAGE', '%s is a committed or failed run: a worker writes only into an open staging folder' % out_root)
    p = os.path.join(out_root, FROZEN)
    if not os.path.exists(p):
        return None
    h = json.load(open(p))
    if h.get('tool') != TOOL or '.pending_' not in os.path.basename(os.path.abspath(out_root)):
        raise Refused('NOT_A_STAGE', '%s: %s of %s outside a .pending_ staging folder' % (out_root, FROZEN, h.get('tool')))
    return h


def build(lab_root, code_dir, events_path, settings_path, subject, first, last, out_root, ctx_root=None, epg_root=None, cause_root=None,
          write=None, log=print, run_window=None, research_root=None, law=None, wins=None, gate=True, coins=None, group=None, group_file=None):
    """one selection (a worker): plan, read, label, write the days into out_root. In a stage opened by run, every frozen pin (settings,
    events, code inventory, window, roots, input vintages) is checked before any read; outside one the parts are written but no
    consumer reads them (no COMPLETE manifest)."""
    t0 = time.time()
    H = _stage_header(out_root); fz = (H or {}).get('frozen')
    if fz:
        check_config(fz['config'], 'before the worker read')               # every configured file, before even the settings are parsed
    s = load_settings(settings_path)
    roots = {'CTX': ctx_root, 'EPG': epg_root, 'CAUSE2': cause_root}
    if fz:
        if s['_sha16'] != fz['settings']['sha16'] or ids.sha16_file(events_path) != fz['events']['sha16']:
            raise Refused('INPUT_CHANGED', 'settings or event list differ from the frozen run: refused')
        for k, v in roots.items():
            if v is not None and v != fz['roots'].get(k):
                raise Refused('ROOTS', '%s root %s differs from the frozen %s' % (k, v, fz['roots'].get(k)))
        roots = {k: fz['roots'].get(k) for k in roots}; research_root = fz['roots']['research']
        if run_window is not None and tuple(run_window) != tuple(fz['run_window']):
            raise Refused('NO_RUN_WINDOW', 'run window differs from the frozen run')
        run_window = tuple(fz['run_window'])
        if not (fz['first'] <= first and last <= fz['last']) or subject != fz['subject']:
            raise Refused('SELECTION', 'worker selection %s %s-%s is outside the frozen run %s %s-%s' % (subject, first, last, fz['subject'], fz['first'], fz['last']))
    window = run_window if run_window is not None else s.get('run_window')
    if isinstance(window, dict):
        window = check_window(window)
    elif window is not None and s.get('run_window') is not None and tuple(window) != check_window(s['run_window']):
        raise Refused('NO_RUN_WINDOW', 'the --run-window %s differs from the settings run_window %s' % (window, s['run_window']))
    first, last, window = admit(first, last, window)                        # A51R2-01: before any roster or index read
    if gate:
        gate_wait(log=log)
    conf = fz['config'] if fz else config_pins(s, events_path)              # a standalone build checks its own admission pins
    if fz:
        if coins is not None or group is not None:
            raise Refused('SELECTION', 'a worker takes the frozen selection, never its own')
        rec = fz['selection']['selector']; only = set(rec['coins']) if rec['kind'] == 'coins' else None
    else:
        only, rec = selection_of(coins, group, group_file, roster_of(lab_root, code_dir, first, last, window)[0] if coins and str(coins).upper() != 'ALL' else None)
    P = plan(events_path, s, subject, first, last, window, law=law, wins=wins, only=only)
    research_root = research_root or research_store(lab_root)
    mods = load_deps(s, roots, code_dir)
    inv = inventory([RUN_PARALLEL])
    if fz and inv != fz['inventory']:
        diff = sorted(set(inv.items()) ^ set(fz['inventory'].items()))
        raise Refused('CODE_CHANGED', 'the code this worker runs differs from the frozen inventory: %s' % diff[:6])
    pins_in = fz['inputs'] if fz else None
    n = len(P['keys'])
    U = read_units(P, s, mods, code_dir, research_root, roots, subject, frozen_inputs=pins_in) if n else {}
    if mods.get('FX2') and fz:
        st = funding_store(s)
        for k in funding_keys(P, s):
            p = os.path.join(st, k[0], '%s.tsv' % k[1]); now = ids.sha16_file(p) if os.path.exists(p) else 'MISSING'
            if fz['inputs']['FUNDING'].get('%s/%s' % k) != now:
                raise Refused('INPUT_CHANGED', 'funding %s/%s is %s, the run froze %s' % (k[0], k[1], now, fz['inputs']['FUNDING'].get('%s/%s' % k)))
    frozen = frozen_exit(s, inv) if any(x['kind'] in PATH_KINDS for x in s['labels']) else {}
    src = PriceSource(lab_root, code_dir, pins=(pins_in or {}).get('PRICE')) if any(e['entry_ok'] for e in P['events']) else None
    vals, why, kat, cen = compute(P, s, src, U, mods, frozen, log=log, gate=gate) if n else ({}, {}, {}, {'t_read_s': 0.0})
    t1 = time.time()
    check_config(conf, 'before the worker wrote')
    srcs, seal = part_sources(s, events_path, inv, P['window'], subject)
    done = _write_days(out_root, code_dir, subject, s, P, vals, why, kat, srcs, seal, write=write, log=log) if n else 0
    reads = src.pc.reads if src is not None and hasattr(src.pc, 'reads') else 0
    log('BUILD OUT.%s events %d days %d labels %d directions %d: prices %.1f s, labels %.1f s, write %.1f s, disk reads %d' % (
        subject, n, done, len(s['labels']), len(s['directions']), cen['t_read_s'], t1 - t0 - cen['t_read_s'], time.time() - t1, reads))
    return vals, why


def part_sources(s, events_path, inv, window, subject):
    """the sources and seal each part keeps (deterministic: no run id, no clock)"""
    srcs = {'events:%s' % os.path.basename(events_path): ids.sha16_file(events_path), 'settings:%s' % os.path.basename(s['_path']): s['_sha16'],
            'code:event_outcomes.py': ids.sha16_file(os.path.realpath(__file__)),
            'inventory': ids.sha16_text(json.dumps(inv, sort_keys=True)),
            'window': ids.sha16_text('%s-%s' % tuple(window))}
    if 'exits' in s:
        srcs['exits'] = s['exits']['sha16']
    seal = json.dumps({'tool': TOOL, 'version': VERSION, 'subject': subject, 'run_window': list(window),
                       'settings': {k: v for k, v in s.items() if not k.startswith('_')}}, sort_keys=True)
    return srcs, seal


# ------------------------------------------------------------------ run: freeze, stage, workers, verify, commit
def preflight(lab_root, code_dir, events_path, settings_path, subject, first, last, run_window=None, roots=None, research_root=None,
              law=None, wins=None, check_release=True, fresh=False, coins=None, group=None, group_file=None):
    """every admission check and the frozen identity of a run (code, settings, events, window, roots, input vintages); reads indexes only"""
    s = load_settings(settings_path)
    window = run_window if run_window is not None else s.get('run_window')
    window = check_window(window) if isinstance(window, dict) else (tuple(window) if window is not None else None)
    if run_window is not None and s.get('run_window') is not None and tuple(window) != check_window(s['run_window']):
        raise Refused('NO_RUN_WINDOW', 'the --run-window %s differs from the settings run_window %s' % (window, s['run_window']))
    first, last, window = admit(first, last, window)                        # A51R2-01 (S3): before any roster or index read
    only, rec = selection_of(coins, group, group_file, roster_of(lab_root, code_dir, first, last, window)[0] if coins and str(coins).upper() != 'ALL' else None)
    P = plan(events_path, s, subject, first, last, window, law=law, wins=wins, only=only)
    roots = dict(roots or {}); research_root = research_root or research_store(lab_root)
    for k, v in roots.items():
        if v is not None and not os.path.isdir(v):
            raise Refused('ROOTS', '%s root %s is not a folder' % (k, v))
    load_deps(s, roots, code_dir)
    inv = fresh_inventory(settings_path, code_dir, roots) if fresh else inventory([RUN_PARALLEL])
    rel = None
    if check_release:
        try:
            release.check(RELEASE)
        except release.ReleaseRefused as e:
            raise Refused('RELEASE', str(e))
        check_closure(inv); rel = {'path': os.path.relpath(RELEASE, FORENSICS), 'sha16': ids.sha16_file(RELEASE)}
    pins = input_pins(P, s, lab_root, code_dir, research_root)
    conf = config_pins(s, events_path)
    sel = dict(selector=rec, requested=len(P['keys']), days=len(set(P['days'].tolist())), coins=len({k[0] for k in P['keys']}),
               entry_embargoed=int(sum(not e['entry_ok'] for e in P['events'])),
               labels_embargoed={x['name']: int(sum(not e['label_ok'][x['name']] for e in P['events'])) for x in s['labels']},
               events_with_any_embargo=[{'coin': e['coin'], 't': e['F'], 'embargoed': sorted(n for n, v in e['label_ok'].items() if not v)}
                                        for e in P['events'] if not all(e['label_ok'].values())],
               months=P['months'])
    frozen = dict(tool=TOOL, version=VERSION, subject=subject, first=P['first'], last=P['last'], run_window=list(P['window']),
                  roots=dict(lab=os.path.abspath(lab_root), code=os.path.abspath(code_dir), research=research_root,
                             CTX=roots.get('CTX'), EPG=roots.get('EPG'), CAUSE2=roots.get('CAUSE2')),
                  events=dict(path=os.path.abspath(events_path), sha16=ids.sha16_file(events_path)),
                  settings=dict(path=os.path.abspath(settings_path), sha16=s['_sha16']), inventory=inv,
                  inventory_sha16=ids.sha16_text(json.dumps(inv, sort_keys=True)), release=rel, inputs=pins, config=conf,
                  columns=[c['col'] for c in column_specs(s)], selection=sel)
    return s, P, frozen


def _tree_rss_bytes(pid):
    try:
        rows = [list(map(int, r.split())) for r in subprocess.check_output(['ps', '-axo', 'pid,ppid,rss'], text=True).splitlines()[1:]]
    except (OSError, subprocess.CalledProcessError):
        return 0
    want = {pid}
    for _ in range(5):
        want |= {p for p, pp, _ in rows if pp in want}
    return sum(rss * 1024 for p, _, rss in rows if p in want)


def run(n, lab_root, code_dir, events_path, settings_path, subject, first, last, out_root, run_window=None, roots=None, research_root=None,
        max_rss_gb=48.0, log=print, check_release=True, law=None, wins=None, inprocess_write=None, fail_after_day=None, hooks=None,
        coins=None, group=None, group_file=None):
    """hooks (acceptance fault injection only): {'after_freeze': fn(stage), 'before_commit': fn(stage)}.
    the public run: gate, release, preflight and freeze; a unique staging folder (run_manifest_candidate.stage); N workers (run_parallel 'outcomes', each nice 10, one numeric
    thread; N = 0 runs the worker in this process, for planted tests); verify; COMPLETE manifest; one atomic rename to out_root"""
    if not 0 <= int(n) <= 8:
        raise Refused('WORKERS', '0 to 8 workers (the team process budget), got %s' % n)
    if int(n) != 0:                                                                              # aw1
        raise Refused('WORKERS_AW1', 'event_outcomes_aw1 runs in this process only (run 0): its workers would run the original, got %s' % n)
    t0 = time.time(); gate_wait(log=log)
    out_root = os.path.abspath(out_root)
    s, P, fz = preflight(lab_root, code_dir, events_path, settings_path, subject, first, last, run_window, roots, research_root, law, wins,
                         check_release, fresh=int(n) > 0, coins=coins, group=group, group_file=group_file)
    ph = {'preflight_s': round(time.time() - t0, 3)}
    if os.path.lexists(out_root):
        try:
            m = RM.verify_committed(out_root, MANIFEST, 'OUT.', code_dir)      # A51R2-04: UP TO DATE only after the full verify
        except (RM.RunRefused, ValueError, OSError) as e:
            raise Refused('OUTPUT_EXISTS', '%s exists and is not a complete run (%s): never overwritten' % (out_root, e))
        if m.get('frozen_sha16') == ids.sha16_text(json.dumps(fz, sort_keys=True)):
            log('UP TO DATE %s (frozen %s)' % (out_root, m['frozen_sha16'])); return m
        raise Refused('OUTPUT_EXISTS', '%s holds another complete run: never overwritten (choose a new out_root)' % out_root)
    stage = RM.stage(out_root); run_id = os.path.basename(stage).split('.pending_', 1)[1]
    head = dict(tool=TOOL, version=VERSION, run_id=run_id, out_root=out_root, workers=int(n), frozen=fz,
                frozen_sha16=ids.sha16_text(json.dumps(fz, sort_keys=True)))
    peak = 0; rc = None
    try:
        RM.write_json_atomic(os.path.join(stage, FROZEN), head)
        if hooks and hooks.get('after_freeze'):
            hooks['after_freeze'](stage)
        if int(n) == 0:
            build(lab_root, code_dir, events_path, settings_path, subject, P['first'], P['last'], stage, write=inprocess_write, log=log,
                  law=law, wins=wins)
        else:
            env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
                       NUMEXPR_NUM_THREADS='1', PYTHONDONTWRITEBYTECODE='1')
            cmd = [sys.executable, '-B', RUN_PARALLEL, str(int(n)), 'outcomes', lab_root, code_dir, events_path, settings_path, subject,
                   P['first'], P['last'], stage]
            with open(os.path.join(stage, 'launcher.log'), 'w') as lg:
                p = subprocess.Popen(cmd, stdout=lg, stderr=subprocess.STDOUT, env=env, start_new_session=True)
                while True:
                    peak = max(peak, _tree_rss_bytes(p.pid))                 # sampled every 0.25 s (the first at once)
                    try:
                        rc = p.wait(timeout=0.25); break
                    except subprocess.TimeoutExpired:
                        if fail_after_day is not None and _written_days(stage) >= fail_after_day:
                            os.killpg(p.pid, 15); p.wait(); raise Refused('INTERRUPTED', 'fault injection: stopped after %d day(s)' % fail_after_day)
                        if peak > max_rss_gb * 1e9:                                       # GB = 10^9 bytes
                            os.killpg(p.pid, 15); p.wait(); raise Refused('RSS_CAP', 'process tree %.1f GB over the cap %.1f GB (10^9 bytes)' % (peak / 1e9, max_rss_gb))
            if rc != 0:
                raise Refused('WORKER_FAILED', 'launcher rc %d (%s)' % (rc, open(os.path.join(stage, 'launcher.log')).read()[-600:]))
        t_work = time.time() - t0; ph['workers_s'] = round(t_work - ph['preflight_s'], 3); t2 = time.time()
        if hooks and hooks.get('before_commit'):
            hooks['before_commit'](stage)
        V = verify_stage(stage, code_dir, s, P, fz); ph['verify_s'] = round(time.time() - t2, 3); t2 = time.time()
        recheck(fz, s, P, lab_root, code_dir); ph['recheck_s'] = round(time.time() - t2, 3); t2 = time.time()
        parts = {}
        for root, _, files in os.walk(stage):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), stage)
                if rel.startswith('day=') and (f in ('index.json', 'REASONS.txt') or rel.split(os.sep)[-2] == 'WORDS'):
                    parts[rel] = ids.sha16_file(os.path.join(root, f))
        files = {f: ids.sha16_file(os.path.join(stage, f)) for f in ('OUT_CATALOG_%s.tsv' % subject, 'FORMAT.json', FROZEN) if os.path.exists(os.path.join(stage, f))}
        files.update({os.path.join(VERIFIED, f): ids.sha16_file(os.path.join(stage, VERIFIED, f)) for f in sorted(os.listdir(os.path.join(stage, VERIFIED)))}
                     if os.path.isdir(os.path.join(stage, VERIFIED)) else {})
        me = __import__('resource').getrusage(__import__('resource').RUSAGE_SELF).ru_maxrss
        ch = __import__('resource').getrusage(__import__('resource').RUSAGE_CHILDREN).ru_maxrss
        if os.path.lexists(out_root):
            raise Refused('OUTPUT_EXISTS', '%s appeared during the run: nothing published' % out_root)
        m = RM.commit(stage, out_root, MANIFEST, dict(head, parts=parts, files=files, selection=fz['selection'], coverage=V['coverage'], verification=V['checks'],
                                terminal=dict(exit_status=0, wall_s=round(time.time() - t0, 3), work_wall_s=round(t_work, 3),
                                              tree_peak_rss_bytes=int(peak), self_max_rss_bytes=int(me), child_max_rss_bytes=int(ch),
                                              phases=dict(ph, hash_and_commit_s=round(time.time() - t2, 3)),
                                              workers=int(n), nice='10 per worker (run_parallel)', numeric_threads=1,
                                              telemetry=sorted(f for f in os.listdir(stage) if f.endswith('.log')))))
        log('COMMITTED %s: events %d, columns %d, wall %.1f s, tree peak %.2f GB (10^9 bytes)' % (out_root, fz['selection']['requested'],
                                                                                              len(fz['columns']), time.time() - t0, peak / 1e9))
        return m
    except BaseException as e:
        kept = RM.abort(stage, out_root, '%s: %s' % (type(e).__name__, e)) if os.path.isdir(stage) else None
        log('FAILED %s: %s (kept as %s, never consumable)' % (out_root, e, kept))
        raise


def _written_days(stage):
    """days whose OUT part is committed in the stage (lab3 writes a part whole or not at all)"""
    n = 0
    for d in os.listdir(stage):
        dd = os.path.join(stage, d)
        if d.startswith('day=') and os.path.isdir(dd):
            n += any(p.startswith('OUT.') and '.tmp_' not in p and '.aside_' not in p for p in os.listdir(dd))
    return n


def recheck(fz, s, P, lab_root, code_dir):
    """at publication: code, settings, events, every configured file and every input vintage still equal the frozen ones (never repinned)"""
    check_config(fz['config'], 'before the commit')
    if ids.sha16_file(fz['settings']['path']) != fz['settings']['sha16'] or ids.sha16_file(fz['events']['path']) != fz['events']['sha16']:
        raise Refused('INPUT_CHANGED', 'settings or event list changed during the run')
    now = {p: ids.sha16_file(os.path.join(FORENSICS, p)) for p in fz['inventory']}
    if now != fz['inventory']:
        raise Refused('CODE_CHANGED', 'code changed during the run: %s' % sorted(k for k in now if now[k] != fz['inventory'][k]))
    pins = input_pins(P, s, lab_root, code_dir, fz['roots']['research'])
    if pins != fz['inputs']:
        bad = [(k, d) for k in pins for d in set(pins[k]) | set(fz['inputs'][k]) if pins[k].get(d) != fz['inputs'][k].get(d)]
        raise Refused('INPUT_CHANGED', 'input vintages changed during the run: %s' % bad[:6])


VERIFIED = 'VERIFIED'


def verify_day(root, code_dir, s, subject, day, want, srcs):
    """one written day read back through the canonical lab3 reader: every requested event x column exactly once, typed as the catalog,
    every empty cell with a reason of the closed set, outcome clocks never before F, input clocks never after the decision, the part's
    sources the run's -> the receipt {day, index_sha16, cells, by_column} (run by each worker right after it writes the day)"""
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as LD
    R = LD.Days(root, 'research'); cols = column_specs(s); part = 'OUT.%s' % subject
    delay = int(round(float(s['entry']['delay_s']) * US)); cov = {}; cells = 0
    ix = R.index(day, part)
    if any(ix['sources'].get(k) != v for k, v in srcs.items()):
        raise Refused('MIXED_RUN', 'day %s part sources %s are not the run\'s %s' % (day, ix['sources'], srcs))
    if sorted(ix['coins']) != sorted(want):
        raise Refused('COVERAGE', 'day %s coins %s, requested %s' % (day, ix['coins'], sorted(want)))
    d0 = day_start_us(day); pos = {c: k for k, c in enumerate(ix['coins'])}
    reasons = np.array(LD.load_list(os.path.join(root, 'day=%s' % day, part, 'REASONS.txt')), object)
    for c in cols:                                                           # the canonical block reader (sha16 + shape checked), vectorised
        code = '%s.%s' % (part, c['col']); unit = c['role'] in ('unit', 'unit_fallback'); n = {}
        if code not in ix['readings'] or ix['readings'][code].get('kind') != 'ROWS':
            raise Refused('COVERAGE', 'day %s lacks the ROWS code %s' % (day, code))
        off, u, k, x, e = (np.asarray(R.block(day, part, code, f)) for f in ('off', 'u', 'k', 'x', 'e'))
        a = d0 + u.astype(np.int64); kind = x.astype(np.int64) & 7; er = reasons[e.astype(np.int64)]
        for coin, ts in want.items():
            lo, hi = int(off[pos[coin]]), int(off[pos[coin] + 1])
            if sorted(a[lo:hi].tolist()) != sorted(ts):
                raise Refused('COVERAGE', '%s %s %s: rows %s, requested %s' % (code, day, coin, a[lo:hi].tolist(), ts))
        if len(a) != sum(len(v) for v in want.values()):
            raise Refused('COVERAGE', '%s %s: %d rows, %d requested' % (code, day, len(a), sum(len(v) for v in want.values())))
        empty = kind == 0; okr = np.array([bool(w) and w.split(':', 1)[0] in REASONS for w in er], bool) if len(er) else np.zeros(0, bool)
        if (empty & ~okr).any():
            raise Refused('REASON', '%s %s: an empty cell with reason %r' % (code, day, er[empty & ~okr][0]))
        bad = ~empty & ((kind != (3 if c['kind'] == 'word' else 1)) | (er != ''))
        if bad.any():
            raise Refused('TYPE', '%s %s: value kind %s / reason %r against catalog %s' % (code, day, kind[bad][0], er[bad][0], c['kind']))
        late = ((k > a + delay) & ~empty) if unit else (k < a)              # an unavailable input may keep its own (late) source clock
        if late.any():
            raise Refused('CLOCK', '%s %s: known_at %s (an outcome before F, or an input after the decision)' % (code, day, k[late][0]))
        for w in er[empty]:
            n[w] = n.get(w, 0) + 1
        if (~empty).any():
            n['VALUE'] = int((~empty).sum())
        cells += len(a); cov[c['col']] = n
    p = os.path.join(root, 'day=%s' % day, part, 'index.json')
    return dict(day=day, index_sha16=ids.sha16_file(p), cells=cells, events=sum(len(v) for v in want.values()), by_column=cov, sources=srcs)


def verify_stage(root, code_dir, s, P, fz):
    """the run's check before publication: exactly the requested days written; for each, the worker's read-back receipt (verify_day)
    exists, is bound to the part's current index sha16 and the frozen sources, and counts every requested event x column -> {coverage,
    checks}"""
    subject = fz['subject']; cols = column_specs(s); part = 'OUT.%s' % subject
    want = {}
    for (coin, F), d in zip(P['keys'], P['days']):
        want.setdefault(d, {}).setdefault(coin, []).append(F * US)
    built = sorted(d[4:] for d in os.listdir(root) if d.startswith('day=') and os.path.isdir(os.path.join(root, d, part)))
    if built != sorted(want):
        raise Refused('COVERAGE', 'days written %s differ from the days requested %s' % (sorted(set(built) ^ set(want))[:5], len(want)))
    srcs = {'inventory': fz['inventory_sha16'], 'window': ids.sha16_text('%s-%s' % tuple(fz['run_window']))}
    cov = {c['col']: {} for c in cols}; cells = 0
    for d in sorted(want):
        rp = os.path.join(root, VERIFIED, '%s.json' % d)
        if not os.path.exists(rp):
            raise Refused('COVERAGE', 'day %s has no read-back receipt %s' % (d, rp))
        r = json.load(open(rp)); ip = os.path.join(root, 'day=%s' % d, part, 'index.json')
        if r['index_sha16'] != ids.sha16_file(ip) or any(r['sources'].get(k) != v for k, v in srcs.items()):
            raise Refused('MIXED_RUN', 'day %s receipt is not bound to the committed part / frozen run' % d)
        n = sum(len(v) for v in want[d].values())
        if r['events'] != n or r['cells'] != n * len(cols) or set(r['by_column']) != set(cov):
            raise Refused('COVERAGE', 'day %s receipt counts %s events / %s cells, requested %d x %d' % (d, r['events'], r['cells'], n, len(cols)))
        for c, x in r['by_column'].items():
            for k, v in x.items():
                cov[c][k] = cov[c].get(k, 0) + v
        cells += r['cells']
    return dict(coverage=dict(events=len(P['keys']), columns=len(cols), cells=cells, by_column=cov),
                checks=dict(identities=len(P['keys']), columns=len(cols), cells=cells, typed=True, reasons_closed=True, clocks_not_before_F=True,
                            sources_frozen=True, clock_rule='outcome known_at >= F; input (unit) known_at <= decision',
                            readback='per day by its worker (verify_day, canonical lab3 rows), receipts bound to each part index sha16'))


# ------------------------------------------------------------------ consumers: only a committed run
def open_run(out_root, code_dir=None):
    """the COMPLETE manifest of a committed run (every committed file rechecked); refuses an interrupted, failed, staged or mixed root"""
    try:
        m = RM.verify_committed(out_root, MANIFEST, 'OUT.', code_dir)     # A51R2-04: every consumer gets THE full verify (every payload
    except RM.RunRefused as e:                                                # block decoded), never the faster digest alone
        raise Refused('RUN_NOT_COMMITTED', str(e))
    if m.get('tool') != TOOL or m.get('version') != VERSION:
        raise Refused('RUN_NOT_COMMITTED', '%s: a manifest of %s version %s, not %s %s' % (out_root, m.get('tool'), m.get('version'), TOOL, VERSION))
    return m


def read(out_root, code_dir, subject, cols=None, first=None, last=None):
    """the consumer reader: {column: {'coin', 'as_of_us', 'known_at_us', 'value', 'reason', 'unit', 'kind'}} over the committed run's
    events (sorted by t, coin): a number column's value is float (NaN when empty), a word column's text ('' when empty); every empty cell
    keeps its reason. Refuses an uncommitted, failed, staged or changed root."""
    m = open_run(out_root, code_dir)
    if m['frozen']['subject'] != subject:
        raise Refused('SUBJECT', 'run is %s, not %s' % (m['frozen']['subject'], subject))
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as LD
    cat = {}
    for l in open(os.path.join(out_root, 'OUT_CATALOG_%s.tsv' % subject)):
        if l.startswith('OUT.'):
            f = l.rstrip('\n').split('\t'); cat[f[0].split('.', 2)[2]] = f
    cols = cols or list(cat)
    R = LD.Days(out_root, 'research'); part = 'OUT.%s' % subject; out = {}
    days = [d for d in R.days() if (first is None or d >= first) and (last is None or d <= last) and part in R.parts(d)]
    for c in cols:
        if c not in cat:
            raise Refused('COLUMN', '%s not in the catalog' % c)
        word = cat[c][6] == 'word'; acc = {k: [] for k in ('coin', 'as_of_us', 'known_at_us', 'value', 'reason')}
        for d in days:
            coins = R.index(d, part)['coins']; rr = R.rows('%s.%s' % (part, c), d, coins)
            for coin in coins:
                x = rr[coin]
                for vk, b, tx, er, ka, a in zip(x['value_kind'], x['value_bits'], x['value_txt'], x['empty_reason'], x['known_at_us'], x['as_of_us']):
                    acc['coin'].append(coin); acc['as_of_us'].append(int(a)); acc['known_at_us'].append(int(ka)); acc['reason'].append(er)
                    acc['value'].append((tx if vk == 3 else '') if word else (float(np.array([b], '<u8').view('<f8')[0]) if vk == 1 else np.nan))
        o = np.lexsort((np.array(acc['coin'], str), np.array(acc['as_of_us'], np.int64))) if acc['coin'] else np.zeros(0, int)
        out[c] = dict(coin=np.array(acc['coin'], object)[o], as_of_us=np.array(acc['as_of_us'], np.int64)[o],
                      known_at_us=np.array(acc['known_at_us'], np.int64)[o], reason=np.array(acc['reason'], object)[o],
                      value=(np.array(acc['value'], object) if word else np.array(acc['value'], float))[o], unit=cat[c][6],
                      kind='word' if word else 'number')
    return out


def show(out_root, code_dir, subject, first, last, log=print):
    r = read(out_root, code_dir, subject, None, first, last)
    log('rows %d' % (len(next(iter(r.values()))['coin']) if r else 0))
    for c, x in r.items():
        if x['kind'] == 'word':
            u, k = np.unique([v if v else '(%s)' % (w or 'none') for v, w in zip(x['value'], x['reason'])], return_counts=True)
            log('%-44s %-7s %s' % (c, x['unit'], ' '.join('%s:%d' % z for z in zip(u, k))))
        else:
            v = np.asarray(x['value'], float); rs = {}
            for w in x['reason']:
                if w:
                    rs[w] = rs.get(w, 0) + 1
            log('%-44s %-7s known %.3f mean %.4g median %.4g %s' % (c, x['unit'], np.isfinite(v).mean() if len(v) else 0,
                                                                     np.nanmean(v) if np.isfinite(v).any() else np.nan,
                                                                     np.nanmedian(v) if np.isfinite(v).any() else np.nan,
                                                                     ' '.join('%s:%d' % z for z in sorted(rs.items()))))


# ------------------------------------------------------------------ the command line
def _opts(a):
    pos, o = [], {}
    i = 0
    while i < len(a):
        if a[i].startswith('--'):
            o[a[i][2:]] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, o


def _window_arg(o):
    if 'run-window' not in o:
        return None
    a, b = o['run-window'].split(':')
    return check_window({'first': a, 'last': b})


def main(a):
    if not a:
        raise SystemExit(__doc__)
    cmd = a[0]; pos, o = _opts(a[1:])
    roots = {'CTX': o.get('ctx'), 'EPG': o.get('epg'), 'CAUSE2': o.get('cause')}
    if cmd == 'run':
        run(int(pos[0]), *pos[1:9], run_window=_window_arg(o), roots=roots, max_rss_gb=float(o.get('max-rss-gb', 48)), coins=o.get('coins'),
            group=o.get('group'), group_file=o.get('group-file'))
    elif cmd == 'check':
        s, P, fz = preflight(*pos[0:7], run_window=_window_arg(o), roots=roots, coins=o.get('coins'), group=o.get('group'), group_file=o.get('group-file'))
        print(json.dumps(dict(selection=fz['selection'], inputs={k: len(v) for k, v in fz['inputs'].items()}, release=fz['release'],
                              inventory_sha16=fz['inventory_sha16']), indent=1, sort_keys=True))
    elif cmd == 'build':
        build(*pos[0:8], *(pos[8:11] if len(pos) > 8 else ()), run_window=_window_arg(o), coins=o.get('coins'), group=o.get('group'),
              group_file=o.get('group-file'))
    elif cmd == 'inventory':                                                 # the worker-equal inventory (fresh_inventory)
        r = json.loads(pos[2]); s = load_settings(pos[0]); load_deps(s, r, pos[1]); print(json.dumps(inventory([RUN_PARALLEL]), sort_keys=True))
    elif cmd == 'verify':                                                    # THE shared run check (run_manifest_candidate V2)
        m = open_run(pos[0], pos[1])
        print('VERIFY PASS %s: %s %s' % (pos[0], json.dumps(m['_verified'], sort_keys=True), json.dumps(m['verification'], sort_keys=True)))
    elif cmd == 'show':
        show(pos[0], pos[1], pos[2], pos[3], pos[4])
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
