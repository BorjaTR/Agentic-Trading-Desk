"""event_profile.py: PROFILE V2 (STRATEGY/LEAD, 25 Oct 2026; design team/RESEARCH/LEAD/PROFILE_V2_DESIGN.md). The profile of ANY alarm, built
only from settings: which year-table metrics (any registered CLOCK code, any clock), which operator each gets (flow, level, price, return,
flag), which entity it is read for (the alarm coin, BTC or the MARKET row), the onset rule, the normal window.
Owner the owner 09:08:15Z: "adding it should just be one more setting in the profile command and not more recoding"; 09:11:02Z: "build it in
that way so at any time we can add any metric with any clock".
Edition 2 of the code (VERSION 2, profile_fixer 25 Oct 2026, A46 review team/OUTSIDE/CODE1/ctxprof_review_v1 PR-02, PR-03, MET-01):
- PR-02: every input is checked BEFORE any data is read or anything is written: the settings (registered CLOCK code, built, not REBUILD or
  PARKED, operator against the registered unit and window, entity against the registered scope, numbers in range), the alarm list (coin,
  integral t, side in -1/0/+1, onset <= t), the days (real YYYYMMDD, first <= last; no date limit in this code: the range is the caller's setting and the lab3 reader's data law applies underneath, owner's generic-tools rule) and the trigger codes. Reader
  refusals and integrity errors propagate (clock_series); a NOT_BUILT day is decided from lab3's metadata (edition 3, P-R1).
- PR-03: every native grid point of the event window is kept with its state (OK, HOLE, NOT_LISTED, NOT_BUILT, NOT_KNOWN). Endpoints are
  exact: at_onset is the point in force at the onset, at_alarm the point in force at F; a missing endpoint is empty with its state, never
  the neighbouring point. A summary over the whole window (totals, peaks, max/min, pulses, swing, path) is empty with PARTIAL unless every
  point is OK; steps_expected and steps_observed give the support of every series. Zero denominators are typed (ZERO_TOTAL, ZERO_BASE,
  ZERO_NORMAL, ZERO_PATH). The original onset, the effective onset and the max_event_s truncation flag are written.
- MET-01: entity coin | btc | market, checked against the registered scope (C1.S15 is BTC's own series: entity btc gives every alarm the
  same BTC value at the same time). Operators are checked against units: flow sums only additive units whose registered window is the
  native step (non-overlapping bins); return compounds arithmetic percent returns ((1+r1)(1+r2)...-1, never a sum); price needs a price
  unit; flag (-1/0/+1, 0/1) gets categorical counts, never a percent change; level gets change_pct only on a ratio-scale unit with a
  positive onset value (never on a signed series). The catalog names each column's series, card name, entity, operator and unit, so a
  fitted series (X1.BOOKX.S01, Stoikov's fitted microprice) is labelled as what it is.
Edition 3 of the code (VERSION 3, profile_fix2 25 Oct 2026; OX-CODE1 re-review team/OUTSIDE/CODE1/ctxprof_rereview_v1 P-R1, P-R2 and the
Profile checklist items C3 C4 C5 G4 H2 K1; task team/RESEARCH/LEAD/ctxprof_fix2/TASK_CTXPROF_FIX2_V1.md):
- P-R2: ONE registered-metric admission, admit_metric, for every settings series AND every trigger, before any read or write: registered,
  a CLOCK code, BUILT, card check not REBUILD or PARKED, reading status not STOP (DO NOT USE or WITHDRAWN in LAB4's METRIC_TRAPS_V3, read
  through labcore.briefs, the reading-metrics skill's own call). A trigger then keeps its own checks (the alarm coin's scope, a number).
- P-R1 (clock_series): an absent day is decided from lab3's metadata (no part of the day names the code); a malformed existing part (a
  required field missing) raises lab3's own error, never read as absent.
- K1: every day of the requested range is checked against lab3/law.py (labcore.gates.load_law: THE seal table, never a copy of its dates)
  before anything is read; a refused day stops the run (Refused, DAY_SEALED). Support days before the range (the normal window, an onset on
  the day before) that law.py refuses are SEALED: never read; every reading that needs them is empty SEALED.
- C3/G4: the states are the LEAD source-state words: NOT_BUILT, NOT_IN_SOURCE (edition 2 wrote NOT_LISTED; it never proved the coin was
  unlisted on the venue), HOLE, NOT_KNOWN, SEALED. PRELISTING is never written: no canonical listing source is registered.
- C4: every series gains normal_steps_observed, the normal-window support of each event (of normal_days x 86400 / step grid points).
- C5/C6: optional requested coins (--coins), checked before the empty path; an empty selection is an explicit successful result
  (COMPLETE_EMPTY); build fills a run report (--report) with requested and observed coverage for the run manifest (ctxprof_shared owns it).
- N4: an optional caller window (--window first,last: the permitted days, the caller's setting): the requested range must lie inside it
  and a support day before it is never opened (OUTSIDE_WINDOW). B5: whole numbers of the alarm list are read exactly (decimal, never a
  float). K6: a refusal is one line 'REFUSED <CODE>: <reason>', exit 2.
- H2: every value an event uses is checked known_at <= F by labcore.lookahead.join_guard (LookaheadError otherwise).
- G7 / P-R2-01 (ctxprof_check VERDICT_V1, OX-CODE1 A46R2; FIX_ROUND3 S2): a value is used only when THE one quality rule,
  labcore.v2_7.quality.known(v, e, a, o, k), calls it known; a finite value the lab stores with a reason (e.g. 0.0 with STALE) is typed
  STALE (else NOT_KNOWN or HOLE) in event windows by clock_series and left out of every normal.
RULES: every reading is measured over the EVENT, from its onset to the alarm F (never a clock window ending at F: that is Context), and each
is also given against the entity's normal (the same series over the normal_days before the event day). Only values with as_of and
known_at <= F are used. A value that cannot be computed is empty with a reason word (README: Output). Nothing is guessed.
INPUT: alarms TSV with coin, t (F, unix seconds), side (+1 / -1 / 0); optional onset_t (from the detector) and trigger (the metric code the
alarm fires on). Without onset_t the settings' onset_rule finds it on the trigger metric; without either, event readings are NO_ONSET.
OUTPUT: lab3 one format, part EPG.<SUBJECT>, ROWS, codes EPG.<SUBJECT>.<series>__<summary> (series code with '.' as '_').
  python3 event_profile.py build <lab_root> <lab3 code dir> <alarms.tsv> <settings.json> <SUBJECT> <first day> <last day> <out_root>
                           [--coins A,B,...] [--window <first>,<last>] [--report <run report .json>]
  python3 event_profile.py check <alarms.tsv> <settings.json> <SUBJECT> <first day> <last day> [--coins A,B,...] [--window <first>,<last>]
                           (all input checks, no data read)
  A refusal prints one line 'REFUSED <CODE>: <reason>' and exits 2 (nothing written).
  python3 event_profile.py show  <out_root> <lab3 code dir> <SUBJECT> <first day> <last day>"""
import csv, datetime as dt, decimal, hashlib, importlib, json, math, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import clock_series as CS                                                    # labcore candidate (shared)
from clock_series import ClockSeries as Series, read_day as _read_day        # noqa: F401 (kept names)

TOOL = 'event_profile'; VERSION = 3
US = 1_000_000
HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, '..'))                           # team/RESEARCH/tools (labcore lives here)
REGISTRY = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'LAB3', 'METRICS_V1.tsv'))   # team/LAB3/METRICS_V1.tsv (the writer's catalog)
NAN = np.nan                   # one NaN object for every empty value (dict equality of outputs stays exact)
SIDES = (-1, 0, 1)
ENTITIES = ('coin', 'btc', 'market')
ENTITY_ROW = {'btc': 'BTC', 'market': 'MARKET'}
SCOPE_OF_ENTITY = {'coin': ('coin', 'coin+market'), 'btc': ('BTC',), 'market': ('market', 'coin+market')}
SUMMARIES = {
    'flow': ('total', 'peak', 'peak_s', 'pulses', 'last60_share', 'vs_normal'),
    'level': ('at_onset', 'at_alarm', 'change', 'change_pct', 'max', 'min', 'vs_normal'),
    'price': ('move_pct', 'swing_pct', 'giveback_pct', 'straightness', 'vs_normal'),
    'return': ('move_pct', 'swing_pct', 'giveback_pct', 'straightness', 'vs_normal'),
    'flag': ('at_onset', 'at_alarm', 'n_pos', 'n_neg', 'share_nonzero'),
}
SUPPORT = ('steps_expected', 'steps_observed', 'normal_steps_observed')
TRIGGER = ('value_at_alarm', 'peak', 'pct_vs_normal', 'onset_to_alarm_s', 'onset_source', 'onset_t', 'onset_original_t', 'onset_truncated')
# operator <- registered unit (METRICS_V1 'unit'); flow and return also need the registered window to be the native step (non-overlapping)
FLOW_UNITS = ('usd', 'count', 'coins_qty')
NOT_LEVEL_UNITS = ('flag', 'side_pm1', 'word', 'timestamp_us', 'metric_unit')
KIND_UNITS = {'flow': FLOW_UNITS, 'price': ('price',), 'return': ('pct',), 'flag': ('flag', 'side_pm1')}
RATIO_SCALE = ('usd', 'coins_qty', 'price', 'count', 'per_second')   # units where a percent change of a positive value has a meaning
REFUSED_CARDS = ('REBUILD', 'PARKED')                                  # METRICS CARD_CHECK: do not use / parked by the owner
SERIES_KEYS = ('code', 'kind', 'entity', 'scope', 'signed', 'why', 'label')
SETTINGS_KEYS = ('name', 'series', 'normal_days', 'max_event_s', 'onset_rule', 'design', 'list', 'version', 'changes', 'proposals', 'why', 'note')
ONSET_KINDS = ('first_beyond_normal', 'rise_start')
MEANING = {
    'total': 'sum of the native bins ending in (onset - one step, F]; empty PARTIAL unless every bin is OK',
    'peak': 'largest bin in the event (complete window only)', 'peak_s': 'seconds from the onset to the end of the peak bin (complete window only)',
    'pulses': 'runs of bins above the normal p90 inside the event (complete window only)',
    'last60_share': 'share of the event total in the bins ending in its last 60 s (complete window; ZERO_TOTAL when the total is 0)',
    'vs_normal': 'the event value over the normal for the same number of native steps (normal_days before the event day)',
    'at_onset': 'value in force at the onset (the grid point at or just before it), exact; empty with its state when missing',
    'at_alarm': 'value in force at the alarm F (the grid point at or just before F), exact; empty with its state when missing',
    'change': 'at_alarm minus at_onset', 'change_pct': 'change in percent of a positive at_onset, ratio-scale units only (ZERO_BASE, '
    'NEGATIVE_BASE, NOT_RATIO_SCALE otherwise)', 'max': 'largest value in the event (complete window only)',
    'min': 'smallest value in the event (complete window only)',
    'move_pct': 'move from the onset to the alarm in the alarm direction (raw when side 0), percent; price: at_alarm/at_onset - 1; '
    'return: the compounded bins (1+r1)(1+r2)...-1 (complete window only)',
    'swing_pct': 'highest minus lowest price of the event path, percent of the start (complete window only)',
    'giveback_pct': 'best point in the alarm direction minus the move at the alarm, percent (complete window; NO_DIRECTION when side 0)',
    'straightness': 'net move over the path length, 0 chop to 1 straight (complete window; ZERO_PATH when the path never moved)',
    'n_pos': 'flag steps above 0 in the event (complete window only)', 'n_neg': 'flag steps below 0 in the event (complete window only)',
    'share_nonzero': 'share of the event steps with a nonzero flag (complete window only)',
    'steps_expected': 'native grid points of the event window (onset - one step, F] for this series and entity',
    'steps_observed': 'of those, the points with a value known at F (the rest are HOLE, NOT_IN_SOURCE, NOT_BUILT, NOT_KNOWN, SEALED, '
    'OUTSIDE_WINDOW or STALE)',
    'normal_steps_observed': 'the finite values known at F in the normal window (the normal_days before the event day) that vs_normal, '
    'pulses and the onset rules use, only values the quality rule calls known (never a STALE value); under 100: NO_NORMAL; a never-read normal '
    'day: SEALED or OUTSIDE_WINDOW',
    'value_at_alarm': 'trigger metric in force at the alarm (exact grid point)', 'pct_vs_normal': 'share of the normal window values below '
    'the value at the alarm', 'onset_to_alarm_s': 'seconds from the effective onset to the alarm',
    'onset_source': '0 none, 1 run beyond the coin normal, 2 start of the build-up, 3 given by the alarm list',
    'onset_t': 'effective onset, unix seconds (the original one moved to F - max_event_s when longer)',
    'onset_original_t': 'onset before the max_event_s cut, unix seconds', 'onset_truncated': '1 when the onset was moved to F - max_event_s, else 0'}
SUMMARY_UNIT = {'peak_s': 'seconds', 'pulses': 'count', 'last60_share': 'share_0_1', 'vs_normal': 'ratio', 'change_pct': 'pct',
                'move_pct': 'pct', 'swing_pct': 'pct', 'giveback_pct': 'pct', 'straightness': 'share_0_1', 'n_pos': 'count', 'n_neg': 'count',
                'share_nonzero': 'share_0_1', 'steps_expected': 'count', 'steps_observed': 'count', 'normal_steps_observed': 'count',
                'pct_vs_normal': 'share_0_1',
                'onset_to_alarm_s': 'seconds', 'onset_source': 'word_number', 'onset_t': 'unix_seconds', 'onset_original_t': 'unix_seconds',
                'onset_truncated': 'flag'}
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')


class Refused(PermissionError):
    """a run outside the admitted research window, named before any data is read"""


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def _lc(name):
    """a module of labcore, THE shared package (team/RESEARCH/tools/labcore), imported on first use: the tools that import this module only
    for load_alarms (cause, situations, decisions, outcomes) do not load it"""
    if TOOLS not in sys.path:
        sys.path.append(TOOLS)
    return importlib.import_module('labcore.' + name)


_LAW = []


def research_law(law=None):
    """lab3/law.py through labcore.gates.load_law (THE seal table; never a copy of its dates), loaded once; a caller (a test fixture) may
    pass its own object with research_refusal(day) -> reason or None"""
    if law is not None:
        return law
    if not _LAW:
        _LAW.append(_lc('gates').load_law())
    return _LAW[0]


def admission_sources(law=None):
    """{name: sha16} of what admission and the seal read besides the settings and the registry: law.py, LAB4's trap table and the
    reading-metrics script (through labcore.briefs), the labcore modules this tool calls"""
    out = {}
    lp = getattr(research_law(law), '__file__', None)
    if lp and os.path.isfile(lp):
        out['law:law.py'] = sha16_file(lp)
    B = _lc('briefs')
    out['code:metric_brief.py'] = sha16_file(B.MB_PATH)
    tp = getattr(B._tables()['MB'], 'TRAPS', None)                 # the trap table the brief read (its path, set by the skill script)
    if tp and os.path.isfile(tp):
        out['brief:%s' % os.path.basename(tp)] = sha16_file(tp)
    for m in ('briefs', 'gates', 'lookahead', '_rows'):
        out['code:labcore/%s.py' % m] = sha16_file(os.path.join(TOOLS, 'labcore', '%s.py' % m))
    return out


_JG = []


def join_guard(known_at_us, decision_us, what):
    """H2 (labcore.lookahead.join_guard): every value used at an event was known at or before its decision time F; refused otherwise"""
    if not _JG:
        _JG.append(_lc('lookahead').join_guard)
    return _JG[0](known_at_us, decision_us, what)


_REG = {}


def load_registry(path=None):
    """{code: registered row (code, card_name, unit, unit_text, scope, store, clock, window, build, card_check, meaning)} from METRICS_V1"""
    path = path or REGISTRY
    if path not in _REG:
        csv.field_size_limit(10 ** 9)
        with open(path, newline='') as f:
            rows = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
            need = ('code', 'unit', 'scope', 'store', 'clock', 'window', 'build', 'card_check')
            miss = [c for c in need if c not in (rows.fieldnames or [])]
            if miss:
                raise ValueError('%s lacks the columns %s: refused' % (path, miss))
            keep = need + ('card_name', 'unit_text', 'meaning')
            _REG[path] = ({r['code']: {k: (r.get(k) or '').strip() for k in keep} for r in rows}, sha16_file(path))
    return _REG[path][0]


def registry_sha16(path=None):
    load_registry(path)
    return _REG[path or REGISTRY][1]


def _window_s(text):
    """seconds of a registered window that starts with '<n> s' or '<n> min', else None"""
    m = re.match(r'^\s*(\d[\d,]*)\s*(s|min)\b', text or '')
    if not m:
        return None
    n = int(m.group(1).replace(',', ''))
    return n * 60 if m.group(2) == 'min' else n


def _int_in(x, lo, hi, what):
    if isinstance(x, bool) or not isinstance(x, int) or not lo <= x <= hi:
        raise ValueError('settings: %s must be a whole number from %d to %d, got %r' % (what, lo, hi, x))
    return x


def admit_metric(code, reg, what):
    """THE registered-metric admission (A46R-P P-R2): one function for every settings series (what 'settings') and every trigger (what
    'trigger'), run by preflight before any data is read or anything written -> the registry row. Refused with a stable code word:
    METRIC_NOT_REGISTERED (not in METRICS_V1), METRIC_NOT_CLOCK (not a CLOCK code whose clock divides a day), METRIC_NOT_BUILT,
    CARD_REFUSED (card check REBUILD or PARKED, REFUSED_CARDS), METRIC_STOP (reading status DO NOT USE or WITHDRAWN: the reading-metrics
    brief through labcore.briefs says STOP). Reads the registry and the brief tables only, never a value."""
    r = reg.get(code)
    if r is None:
        raise ValueError('METRIC_NOT_REGISTERED: %s: %s is not a registered metric (METRICS_V1): refused' % (what, code))
    if r['store'] != 'CLOCK' or not r['clock'].isdigit() or int(r['clock']) <= 0 or 86400 % int(r['clock']):
        raise ValueError('METRIC_NOT_CLOCK: %s: %s is a %s code at clock %r; the profile reads CLOCK codes only: refused'
                         % (what, code, r['store'], r['clock']))
    if r['build'] != 'BUILT':
        raise ValueError('METRIC_NOT_BUILT: %s: %s is %s in METRICS_V1, not BUILT: refused' % (what, code, r['build'] or 'not built'))
    if r['card_check'] in REFUSED_CARDS:
        raise ValueError('CARD_REFUSED: %s: %s card check is %s (do not use / parked): refused' % (what, code, r['card_check']))
    b = _lc('briefs').brief(code)
    if b['flag'] == 'STOP':
        raise ValueError('METRIC_STOP: %s: %s reading status %r (metric brief STOP: never use it): refused' % (what, code, b['status']))
    return r


def series_spec(x, reg):
    """one checked settings line -> {code, kind, entity, row, unit, clock, signed, label}; ValueError naming the line otherwise"""
    if not isinstance(x, dict):
        raise ValueError('settings: a series line must be an object: %r' % (x,))
    bad = sorted(set(x) - set(SERIES_KEYS))
    if bad:
        raise ValueError('settings: unknown keys %s in %r (allowed %s)' % (bad, x, ', '.join(SERIES_KEYS)))
    code, kind = x.get('code'), x.get('kind')
    if not isinstance(code, str) or not code or kind not in SUMMARIES:
        raise ValueError('settings: every series needs a code and a kind in %s: %r' % (sorted(SUMMARIES), x))
    r = admit_metric(code, reg, 'settings')                          # the same admission as a trigger (P-R2)
    scope = x.get('scope')
    if scope is not None and scope not in ('coin', 'market'):
        raise ValueError('settings: %s scope %r: use entity coin | btc | market' % (code, scope))
    ent = x.get('entity', scope or 'coin')
    if ent not in ENTITIES:
        raise ValueError('settings: %s entity %r not in %s' % (code, ent, ENTITIES))
    if scope is not None and scope != ent:
        raise ValueError('settings: %s scope %r and entity %r disagree' % (code, scope, ent))
    if r['scope'] not in SCOPE_OF_ENTITY[ent]:
        raise ValueError('settings: %s is registered with scope %r; entity %r reads a row it does not have (use entity %s): refused'
                         % (code, r['scope'], ent, {'BTC': 'btc', 'market': 'market'}.get(r['scope'], 'coin')))
    unit, clock = r['unit'], int(r['clock'])
    if kind == 'level':
        if unit in NOT_LEVEL_UNITS:
            raise ValueError('settings: %s unit %r cannot take the level operator (a flag is a flag, never a percent change)' % (code, unit))
    elif unit not in KIND_UNITS[kind]:
        raise ValueError('settings: %s unit %r cannot take the %s operator (needs %s)' % (code, unit, kind, ', '.join(KIND_UNITS[kind])))
    if kind in ('flow', 'return'):
        w = _window_s(r['window'])
        if w != clock:
            raise ValueError('settings: %s registered window %r is not its %d s step: %s needs non-overlapping native bins: refused'
                             % (code, r['window'], clock, kind))
        if kind == 'flow' and re.search(r'\b(a|per) second\b', r['unit_text']):
            raise ValueError('settings: %s is a rate (%s): never summed as a flow' % (code, r['unit_text']))
    signed = x.get('signed', False)
    if not isinstance(signed, bool) or (signed and kind != 'level'):
        raise ValueError('settings: %s signed must be true or false, and only for the level operator' % code)
    return dict(code=code, kind=kind, entity=ent, row=ENTITY_ROW.get(ent), unit=unit, clock=clock, signed=signed,
                label=str(x.get('label') or ''), card_name=r['card_name'])


def load_settings(path, registry=None):
    """the settings, every line checked against the registry before any data is read; s['_spec'] holds the checked lines"""
    with open(path) as f:
        s = json.load(f)
    if not isinstance(s, dict):
        raise ValueError('settings: a JSON object, got %s' % type(s).__name__)
    for k in ('name', 'series', 'normal_days', 'max_event_s'):
        if k not in s:
            raise ValueError('settings: %s missing' % k)
    bad = sorted(k for k in s if k not in SETTINGS_KEYS)
    if bad:
        raise ValueError('settings: unknown keys %s' % bad)
    if not isinstance(s['name'], str) or not s['name']:
        raise ValueError('settings: name must be a text')
    _int_in(s['normal_days'], 1, 30, 'normal_days'); _int_in(s['max_event_s'], 1, 86400, 'max_event_s')
    rule = s.get('onset_rule', {})
    if not isinstance(rule, dict) or sorted(set(rule) - {'kinds', 'kind', 'pct', 'lookback_s'}):
        raise ValueError('settings: onset_rule takes kinds, pct, lookback_s: %r' % (rule,))
    kinds = rule.get('kinds', [rule.get('kind', 'first_beyond_normal')])
    if not isinstance(kinds, list) or not kinds or any(k not in ONSET_KINDS for k in kinds):
        raise ValueError('settings: onset_rule kinds must be a list from %s: %r' % (ONSET_KINDS, kinds))
    pct = rule.get('pct', 90)
    if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not 0 < pct < 100:
        raise ValueError('settings: onset_rule pct must be a number between 0 and 100: %r' % (pct,))
    _int_in(rule.get('lookback_s', 3600), 1, 86400, 'onset_rule lookback_s')
    if not isinstance(s['series'], list) or not s['series']:
        raise ValueError('settings: series must be a non-empty list')
    reg = load_registry(registry)
    spec, seen = [], set()
    for x in s['series']:
        sp = series_spec(x, reg)
        if sp['code'] in seen:
            raise ValueError('settings: series listed twice: %s' % sp['code'])
        seen.add(sp['code']); spec.append(sp)
    s['_spec'] = spec; s['_registry_sha16'] = registry_sha16(registry)
    return s


def _whole(text, what, path, line):
    """the exact whole number a text writes (edition 3, checklist B5: read exactly as a decimal, never through a float, so a fraction
    a float would round away, e.g. 1760529600.0000001, is refused); NaN, infinity and fractions are refused"""
    try:
        x = decimal.Decimal(str(text).strip())
    except (TypeError, ValueError, decimal.InvalidOperation):
        raise ValueError('%s line %d: %s %r is not a number: refused' % (path, line, what, text))
    if not x.is_finite() or x != x.to_integral_value():
        raise ValueError('%s line %d: %s %r is not a whole number: refused' % (path, line, what, text))
    return int(x)


def load_alarms(path):
    """the alarm list -> dict(coin, t, side, onset_t (-1 none), trigger) arrays; every row checked: coin, whole t > 0, side -1/0/+1 (blank
    = 0), onset_t blank or a whole time <= t, and no event identity twice (coin and second; coins compared without case); a bad row is
    refused by line, never skipped"""
    with open(path) as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        R = list(rd); fields = rd.fieldnames or []
    if R and not {'coin', 't'} <= set(fields):
        raise ValueError('%s: the columns coin and t are required (got %s): refused' % (path, fields))
    coin, t, side, onset, trig = [], [], [], [], []; seen = {}
    for n, r in enumerate(R, start=2):
        c = (r.get('coin') or '').strip()
        if not c or not re.fullmatch(r'[A-Za-z0-9_]+', c):
            raise ValueError('%s line %d: coin %r: refused' % (path, n, r.get('coin')))
        tt = _whole(r.get('t'), 't', path, n)
        if tt <= 0 or tt * US >= 2 ** 63:                            # a time in microseconds must fit int64 (B5: never an overflow later)
            raise ValueError('%s line %d: t %d: refused' % (path, n, tt))
        key = (c.upper(), tt)                                         # the event identity every consumer joins on (A50 F02)
        if key in seen:
            raise ValueError('%s line %d: duplicate event identity (coin %s, t %d), first on line %d (the same coin and second, or a coin '
                             'spelled differently only by case): refused' % (path, n, c, tt, seen[key]))
        seen[key] = n
        sd = 0 if (r.get('side') or '').strip() == '' else _whole(r.get('side'), 'side', path, n)
        if sd not in SIDES:
            raise ValueError('%s line %d: side %r must be -1, 0 or +1: refused' % (path, n, r.get('side')))
        given = (r.get('onset_t') or '').strip() != ''
        ot = _whole(r.get('onset_t'), 'onset_t', path, n) if given else -1
        if given and not 0 < ot <= tt:
            raise ValueError('%s: an onset after its alarm (line %d): refused' % (path, n))
        coin.append(c); t.append(tt); side.append(sd); onset.append(ot); trig.append((r.get('trigger') or '').strip())
    return dict(coin=np.array(coin), t=np.array(t, np.int64), side=np.array(side, int), onset_t=np.array(onset, np.int64),
                trigger=np.array(trig))


def valid_day(d):
    """a real calendar day YYYYMMDD -> the same text; ValueError otherwise (20260230 refused)"""
    text = str(d)
    if len(text) != 8 or not text.isdigit():
        raise ValueError('day %r: must be YYYYMMDD' % (d,))
    dt.date(int(text[:4]), int(text[4:6]), int(text[6:]))
    return text


def check_days(first, last):
    first, last = valid_day(first), valid_day(last)
    if first > last:
        raise ValueError('first day %s is after last day %s: refused' % (first, last))
    return first, last


def check_coins(coins):
    """C5: the requested coins -> None (every coin of the alarm list) or a sorted tuple of upper-case names. A list (or 'A,B' text) of
    names of letters, digits and _, each once (compared without case); an empty list, a bad name or a name twice is refused
    (COINS_INVALID). A requested coin with no alarm in the range is valid: it has no row. Whether a coin is in a source is read per day
    from the part index (NOT_IN_SOURCE); roster membership belongs to the shared population selector (REL-01, ctxprof_shared)."""
    if coins is None:
        return None
    if isinstance(coins, str):
        coins = coins.split(',')
    if not isinstance(coins, (list, tuple)) or not coins:
        raise ValueError('COINS_INVALID: the requested coins must be a non-empty list: %r: refused' % (coins,))
    out = []
    for c in coins:
        if not isinstance(c, str) or not re.fullmatch(r'[A-Za-z0-9_]+', c.strip()):
            raise ValueError('COINS_INVALID: requested coin %r: refused' % (c,))
        out.append(c.strip().upper())
    if len(set(out)) != len(out):
        raise ValueError('COINS_INVALID: a coin requested twice (compared without case) in %r: refused' % (coins,))
    return tuple(sorted(out))


def col(code, summ):
    return '%s__%s' % (code.replace('.', '_'), summ)


def columns(settings):
    out = [(col('TRIGGER', s), s) for s in TRIGGER]
    for x in settings['series']:
        out += [(col(x['code'], s), s) for s in SUMMARIES[x['kind']] + SUPPORT]
    return out


def _clean(text):
    return re.sub(r'\s+', ' ', str(text or '')).strip()


def catalog_text(subject, settings):
    lines = ['# EPG catalog for %s from settings %s (event_profile.py VERSION %d)' % (subject, settings['name'], VERSION), '\t'.join(CAT_COLS)]
    spec = {x['code']: x for x in settings.get('_spec', [])}
    for c, s in columns(settings):
        if c.startswith('TRIGGER__'):
            meaning, unit = MEANING[s], SUMMARY_UNIT.get(s, 'unit of the trigger metric')
        else:
            x = next(y for y in settings['series'] if col(y['code'], s) == c); sp = spec.get(x['code'], {})
            m0 = MEANING[s]
            if s == 'normal_steps_observed' and sp.get('clock'):
                m0 += ' (of %d grid points: normal_days %d x 86400 / %d s)' % (int(settings['normal_days']) * 86400 // sp['clock'],
                                                                              int(settings['normal_days']), sp['clock'])
            meaning = '%s | series %s (%s%s) entity %s, operator %s, registered unit %s' % (
                m0, x['code'], sp.get('card_name', ''), ('; ' + sp['label']) if sp.get('label') else '', sp.get('entity', 'coin'),
                x['kind'], sp.get('unit', '?'))
            unit = SUMMARY_UNIT.get(s, sp.get('unit', 'per series'))
        lines.append('\t'.join(['EPG.%s.%s' % (subject, c), 'ROWS', 'event', '0', 'coin', _clean(meaning), unit, 'EVENT', 'EPG']))
    return '\n'.join(lines) + '\n'


def utc_day(t):
    return dt.datetime.fromtimestamp(int(t), dt.timezone.utc).strftime('%Y%m%d')


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def _state_reason(st):
    """the reason word of a set of missing states: the one state when they agree, else PARTIAL"""
    u = np.unique(st[st != CS.OK])
    return CS.STATE_WORD[int(u[0])] if len(u) == 1 else 'PARTIAL'


def _normal_why(ns):
    """'' when the normal can be used; SEALED (or OUTSIDE_WINDOW) when a never-read day holds part of its window (never computed from
    what is left); NO_NORMAL when fewer than 100 values are known"""
    w = ns.get('sealed')
    if w:
        return w if isinstance(w, str) else 'SEALED'
    return 'NO_NORMAL' if ns['n'] < 100 else ''


def profile_one(s, kind, coin, onset_us, f_us, side, normal_lo_us, normal_hi_us, unit=None, signed=False, tally=None):
    """{summary: (value or NaN, reason)} for one series of one alarm, the summaries of kind plus steps_expected, steps_observed and
    normal_steps_observed. unit: the registered unit (None: a library caller without a registry; change_pct then needs only a positive
    onset value). Every value used is checked known_at <= F (join_guard). tally: an optional dict counting the event-window points by
    state word (the run report)."""
    names = SUMMARIES[kind] + SUPPORT
    if onset_us < 0:
        return {n: (NAN, 'NO_ONSET') for n in names}
    t, v, st, kn = s.event_window(coin, onset_us - s.step * US, f_us, f_us, with_k=True)
    n = len(t)
    ns = s.normal(coin, normal_lo_us, normal_hi_us, f_us)
    nwhy = _normal_why(ns)
    if n == 0:                                                        # no native grid point at all (only a sparse test double can do this)
        out = {k: (NAN, 'NO_DATA') for k in SUMMARIES[kind]}
        out['steps_expected'] = (0.0, ''); out['steps_observed'] = (0.0, ''); out['normal_steps_observed'] = (float(ns['n']), '')
        return out
    okm = st == CS.OK; nobs = int(okm.sum()); complete = nobs == n
    if nobs:
        join_guard(kn[okm], f_us, 'EPG %s %s' % (getattr(s, 'code', kind), coin))   # H2: a value known after F is never used
    if tally is not None:
        for w, c in zip(*np.unique(st, return_counts=True)):
            tally[CS.STATE_WORD[int(w)]] = tally.get(CS.STATE_WORD[int(w)], 0) + int(c)
    out = {'steps_expected': (float(n), ''), 'steps_observed': (float(nobs), ''), 'normal_steps_observed': (float(ns['n']), '')}
    whole = '' if complete else ('PARTIAL' if nobs else _state_reason(st))     # the reason of every whole-window summary

    def first_last(name_a, name_b):
        a = (float(v[0]), '') if okm[0] else (NAN, CS.STATE_WORD[int(st[0])])
        b = (float(v[-1]), '') if okm[-1] else (NAN, CS.STATE_WORD[int(st[-1])])
        out[name_a] = a; out[name_b] = b
        return a[0], b[0]

    def need_whole(*keys):
        for k in keys:
            out[k] = (NAN, whole)
    if kind == 'flow':
        if not complete:
            need_whole('total', 'peak', 'peak_s', 'pulses', 'last60_share', 'vs_normal')
            return out
        tot = float(np.sum(v)); j = int(np.argmax(v))
        out['total'] = (tot, ''); out['peak'] = (float(v[j]), ''); out['peak_s'] = ((t[j] - onset_us) / US, '')
        out['last60_share'] = ((float(np.sum(v[t > f_us - 60 * US])) / tot, '') if tot != 0 else (NAN, 'ZERO_TOTAL'))
        if not nwhy:
            p90 = ns['p90']; above = v > p90
            out['pulses'] = (float(np.sum(above[1:] & ~above[:-1]) + (1 if above[0] else 0)), '')
            mean = ns['mean']
            out['vs_normal'] = (tot / (mean * n), '') if mean > 0 else (NAN, 'ZERO_NORMAL')
        else:
            out['pulses'] = (NAN, nwhy); out['vs_normal'] = (NAN, nwhy)
    elif kind == 'level':
        a, b = first_last('at_onset', 'at_alarm')
        if math.isfinite(a) and math.isfinite(b):
            ch = b - a; out['change'] = (ch, '')
            if signed or (unit is not None and unit not in RATIO_SCALE):
                out['change_pct'] = (NAN, 'NOT_RATIO_SCALE')
            elif a > 0:
                out['change_pct'] = (ch / a * 100, '')
            else:
                out['change_pct'] = (NAN, 'ZERO_BASE' if a == 0 else 'NEGATIVE_BASE')
            if nwhy:
                out['vs_normal'] = (NAN, nwhy)
            else:
                sc = ns['absdiff'] * np.sqrt(max(n, 1))
                out['vs_normal'] = (abs(ch) / sc, '') if sc > 0 else (NAN, 'ZERO_NORMAL')
        else:
            why = out['at_onset'][1] or out['at_alarm'][1]
            for k in ('change', 'change_pct', 'vs_normal'):
                out[k] = (NAN, why)
        if complete:
            out['max'] = (float(np.max(v)), ''); out['min'] = (float(np.min(v)), '')
        else:
            need_whole('max', 'min')
    elif kind == 'flag':
        first_last('at_onset', 'at_alarm')
        if complete:
            out['n_pos'] = (float(np.sum(v > 0)), ''); out['n_neg'] = (float(np.sum(v < 0)), '')
            out['share_nonzero'] = (float(np.mean(v != 0)), '')
        else:
            need_whole('n_pos', 'n_neg', 'share_nonzero')
    else:                                                             # price (a price level) or return (arithmetic percent returns)
        sgn = side if side != 0 else 1
        if kind == 'price':
            p0, p1 = (float(v[0]) if okm[0] else NAN), (float(v[-1]) if okm[-1] else NAN)
            if not (math.isfinite(p0) and math.isfinite(p1)):
                why = CS.STATE_WORD[int(st[0])] if not okm[0] else CS.STATE_WORD[int(st[-1])]
                for k in ('move_pct', 'vs_normal'):
                    out[k] = (NAN, why)
                path = None
            elif p0 <= 0 or p1 <= 0:
                for k in ('move_pct', 'vs_normal'):
                    out[k] = (NAN, 'NONPOSITIVE_PRICE')
                path = None
            else:
                move = (p1 / p0 - 1) * 100 * sgn; out['move_pct'] = (move, '')
                path = v / p0 if complete and np.all(v > 0) else None    # the price path relative to the start
                if nwhy:
                    out['vs_normal'] = (NAN, nwhy)
                else:
                    sc = ns['logabsdiff'] * 100 * np.sqrt(max(n, 1))
                    out['vs_normal'] = (abs(move) / sc, '') if sc > 0 else (NAN, 'ZERO_NORMAL')
            if not complete:
                need_whole('swing_pct', 'giveback_pct', 'straightness')
                return out
            if path is None:
                for k in ('swing_pct', 'giveback_pct', 'straightness'):
                    out[k] = (NAN, out['move_pct'][1] or 'NONPOSITIVE_PRICE')
                return out
        else:                                                         # return: compound, never sum
            if not complete:
                need_whole('move_pct', 'swing_pct', 'giveback_pct', 'straightness', 'vs_normal')
                return out
            g = 1 + v / 100.0
            if np.any(g <= 0):
                for k in ('move_pct', 'swing_pct', 'giveback_pct', 'straightness', 'vs_normal'):
                    out[k] = (NAN, 'BAD_RETURN')
                return out
            path = np.concatenate([[1.0], np.cumprod(g)])               # the price path relative to the start, start included
            move = (float(path[-1]) - 1) * 100 * sgn; out['move_pct'] = (move, '')
            if nwhy:
                out['vs_normal'] = (NAN, nwhy)
            else:
                if 'logabsret' not in ns:
                    nv = ns['nv']; nv = nv[nv > -100]
                    ns['logabsret'] = float(np.mean(np.abs(np.log1p(nv / 100.0)))) if len(nv) else 0.0
                sc = ns['logabsret'] * 100 * np.sqrt(max(n, 1))
                out['vs_normal'] = (abs(move) / sc, '') if sc > 0 else (NAN, 'ZERO_NORMAL')
        dpath = (path - 1) * 100 * sgn
        out['swing_pct'] = (float(np.max(path) - np.min(path)) * 100 / float(path[0]), '')
        out['giveback_pct'] = (float(np.max(dpath)) - float(dpath[-1]), '') if side != 0 else (NAN, 'NO_DIRECTION')
        pl = float(np.sum(np.abs(np.diff(path))))
        out['straightness'] = (abs(float(path[-1]) - float(path[0])) / pl, '') if pl > 0 else (NAN, 'ZERO_PATH')
    return out


def find_onset(s, coin, f_us, rule, normal_lo_us, normal_hi_us):
    """(onset_us, source) by the settings' rules, tried in order, on the trigger series; (-1, 0) when none applies (never guessed).
    first_beyond_normal (1): the start of the run of steps above the coin normal p<pct> that reaches the alarm.
    rise_start (2): the start of the trigger metric's build-up: walking back from the alarm while it kept moving toward its value at the
    alarm (steps against it smaller than a quarter of the coin's normal step are ignored). A heuristic on the known values of the trigger
    (holes are stepped over); it never proves a mechanism. A never-read day (SEALED, OUTSIDE_WINDOW) in the normal or lookback window:
    (-1, 0), never an onset found on what is left (onset_sealed names it)."""
    if s is None or not s.ok or coin not in s.coin:
        return -1, 0
    if onset_sealed(s, f_us, rule, normal_lo_us, normal_hi_us):
        return -1, 0
    nt, nv = s.window(coin, normal_lo_us, normal_hi_us, f_us); nv = nv[np.isfinite(nv)]
    t, v = s.window(coin, f_us - int(rule.get('lookback_s', 3600)) * US, f_us, f_us)
    ok = np.isfinite(v); t, v = t[ok], v[ok]
    if len(nv) < 100 or len(v) < 3:
        return -1, 0
    for kind in rule.get('kinds', [rule.get('kind', 'first_beyond_normal')]):
        if kind == 'first_beyond_normal':
            thr = float(np.percentile(nv, rule.get('pct', 90)))
            if v[-1] > thr:
                j = len(v) - 1
                while j > 0 and v[j - 1] > thr:
                    j -= 1
                if j < len(v) - 1:
                    return int(t[j] - s.step * US), 1
        elif kind == 'rise_start':
            d = 1.0 if v[-1] >= np.median(v) else -1.0
            tol = 0.25 * float(np.mean(np.abs(np.diff(nv))))
            j = len(v) - 1
            while j > 0 and d * (v[j] - v[j - 1]) >= -tol:
                j -= 1
            if j < len(v) - 2:
                return int(t[j]), 2
        else:
            raise ValueError('onset rule kind %r unknown' % kind)
    return -1, 0


def onset_sealed(s, f_us, rule, normal_lo_us, normal_hi_us):
    """the word (SEALED, OUTSIDE_WINDOW) of a never-read day holding part of the onset rule's normal or lookback window, else '': the
    onset is then unavailable, never found on what is left"""
    ub = getattr(s, 'unavailable_between', None)
    if ub is None:
        return ''
    return ub(normal_lo_us, normal_hi_us) or ub(f_us - int(rule.get('lookback_s', 3600)) * US, f_us)


def trigger_readings(ts, coin, on, f, nlo, nhi, on_why='NO_ONSET'):
    """TRIGGER value_at_alarm, peak, pct_vs_normal of one alarm on its trigger series (exact grid point at F; peak over a complete window);
    every value used is checked known_at <= F (join_guard); on_why: the reason of a missing onset (NO_ONSET, SEALED or OUTSIDE_WINDOW)"""
    out = {}
    if ts is None or not ts.ok or coin not in ts.coin:
        return {k: (NAN, 'NO_TRIGGER') for k in ('value_at_alarm', 'peak', 'pct_vs_normal')}
    t1, v1, s1, k1 = ts.event_window(coin, f - ts.step * US, f, f, with_k=True)
    if len(v1) and s1[-1] == CS.OK:
        join_guard(k1[-1:], f, 'EPG TRIGGER %s %s' % (ts.code, coin))
        out['value_at_alarm'] = (float(v1[-1]), '')
    else:
        out['value_at_alarm'] = (NAN, CS.STATE_WORD[int(s1[-1])] if len(s1) else 'NO_DATA')
    if on < 0:
        out['peak'] = (NAN, on_why)
    else:
        tw, tv, tst, tk = ts.event_window(coin, on - ts.step * US, f, f, with_k=True)
        if len(tv) and np.all(tst == CS.OK):
            join_guard(tk, f, 'EPG TRIGGER %s %s' % (ts.code, coin))
            out['peak'] = (float(np.max(tv)), '')
        else:
            out['peak'] = (NAN, ('PARTIAL' if np.any(tst == CS.OK) else _state_reason(tst)) if len(tst) else 'NO_DATA')
    nt, nv = ts.window(coin, nlo, nhi, f); nv = nv[np.isfinite(nv)]
    va = out['value_at_alarm'][0]
    if not math.isfinite(va):
        out['pct_vs_normal'] = (NAN, out['value_at_alarm'][1])
    elif ts.unavailable_between(nlo, nhi):
        out['pct_vs_normal'] = (NAN, ts.unavailable_between(nlo, nhi))
    elif len(nv) < 100:
        out['pct_vs_normal'] = (NAN, 'NO_NORMAL')
    else:
        out['pct_vs_normal'] = (float(np.mean(nv < va)), '')
    return out


def check_window(window, first, last):
    """N4: the caller's permitted window (first day, last day) -> the two days or None; the requested range must lie inside it (refused
    OUTSIDE_WINDOW otherwise). A support day before the window is never opened (OUTSIDE_WINDOW). The window is the caller's setting
    (e.g. the team's research months), never a constant here; law.py still seals underneath."""
    if window is None:
        return None
    if isinstance(window, str):
        window = window.split(',')
    if not isinstance(window, (list, tuple)) or len(window) != 2:
        raise ValueError('WINDOW_INVALID: the window is two days first,last: %r: refused' % (window,))
    w0, w1 = check_days(*window)
    if not (w0 <= first and last <= w1):
        raise Refused('OUTSIDE_WINDOW: the requested range %s..%s is not inside the caller window %s..%s: refused before any read'
                      % (first, last, w0, w1))
    return w0, w1


def preflight(alarms_path, settings_path, subject, first, last, registry=None, coins=None, law=None, window=None):
    """every input check, before any data is read or anything written -> (settings, alarms, first, last, trigger specs). In order: the
    subject; the days (real calendar days, first <= last); the requested coins (C5, check_coins); lab3/law.py on EVERY day of the requested
    range (K1: a refused day stops the run, Refused DAY_SEALED); the settings (every series through admit_metric); the alarm list; every
    trigger of the selected alarms through the SAME admit_metric, then its own scope and unit checks (P-R2). The settings dict also carries
    the checked selection: _sel (the selected alarm rows: in the range and, when coins are requested, of those coins), _coins (the requested
    coins or None), _sealed ({support day: law.py reason}: days before the range that a normal window or an onset on the day before needs
    and law.py refuses: never read, SEALED), _outside ({support day: the caller window}: support days before the caller's window, N4:
    never opened, OUTSIDE_WINDOW), _window (the caller window or None)."""
    if not (isinstance(subject, str) and subject and subject.replace('_', '').isalnum() and subject.upper() == subject):
        raise ValueError('subject: capital letters, digits and _')
    first, last = check_days(first, last)
    win = check_window(window, first, last)
    want = check_coins(coins)
    L = research_law(law)
    d = first
    while d <= last:                                                  # the caller's range, checked by THE seal table (never a constant)
        why = L.research_refusal(d)
        if why:
            raise Refused('DAY_SEALED: day %s of the requested range %s..%s: lab3/law.py refuses it for research (%s): refused before any '
                          'read' % (d, first, last, why))
        d = shift(d, 1)
    st = load_settings(settings_path, registry); ev = load_alarms(alarms_path)
    reg = load_registry(registry); trig = {}
    days = [utc_day(t) for t in ev['t'].tolist()]
    sel = np.array([i for i, dd in enumerate(days) if first <= dd <= last and (want is None or ev['coin'][i].upper() in want)], int)
    for tc in sorted(set(ev['trigger'][sel].tolist()) - {''}):        # duplicates: refused by load_alarms
        r = admit_metric(tc, reg, 'trigger')                            # P-R2: the same admission as every settings series
        if r['scope'] not in SCOPE_OF_ENTITY['coin'] or r['unit'] in NOT_LEVEL_UNITS:
            raise ValueError('TRIGGER_SCOPE_UNIT: trigger %s scope %r unit %r: a trigger is read on the alarm coin as a number: refused'
                             % (tc, r['scope'], r['unit']))
        trig[tc] = int(r['clock'])
    sealed, outside = {}, {}
    for dd in sorted(set(days[i] for i in sel.tolist())):            # support days before the range: the normal window (and D-1)
        for k in range(int(st['normal_days']), 0, -1):
            sd = shift(dd, -k)
            if sd < first and sd not in sealed and sd not in outside:
                if win is not None and sd < win[0]:
                    outside[sd] = 'outside the caller window %s..%s' % win
                    continue
                why = L.research_refusal(sd)
                if why:
                    sealed[sd] = why
    st['_sel'] = sel; st['_coins'] = want; st['_sealed'] = sealed; st['_outside'] = outside; st['_window'] = win
    return st, ev, first, last, trig


def _report_series(rep, code, sp, normal_days):
    x = rep['series'].get(code)
    if x is None:
        x = rep['series'][code] = dict(entity=sp.get('entity', 'coin'), clock=sp['clock'], normal_steps_expected=normal_days * 86400 // sp['clock'],
                                       points={}, not_built_days=set(), never_read_days=set())
    return x


def build(lab_root, code_dir, alarms_path, settings_path, subject, first, last, out_root, R=None, write=None, log=print, registry=None,
          coins=None, law=None, report=None, window=None):
    """the profile of every selected alarm -> {day: 'WRITTEN'}. Every check (preflight) runs before anything is read; every read before
    anything is written. An empty selection reads and writes nothing and is an explicit success (report status COMPLETE_EMPTY).
    report: an optional dict filled in place with the run report (requested and observed coverage, see README: Run report)."""
    st, ev, first, last, trig = preflight(alarms_path, settings_path, subject, first, last, registry, coins, law, window)   # no read, no write before this
    spec = st['_spec']; selected = st['_sel']
    sealed = dict({d: 'SEALED' for d in st['_sealed']}, **{d: 'OUTSIDE_WINDOW' for d in st['_outside']})   # never-read support days
    rep = report if report is not None else {}
    seal = json.dumps({'tool': TOOL, 'version': VERSION, 'settings': {k: v for k, v in st.items() if not k.startswith('_')},
                       'registry_sha16': st['_registry_sha16'], 'subject': subject}, sort_keys=True)
    fixed = {'alarms:%s' % os.path.basename(alarms_path): sha16_file(alarms_path),
             'settings:%s' % os.path.basename(settings_path): sha16_file(settings_path),
             'registry:%s' % os.path.basename(registry or REGISTRY): st['_registry_sha16'],
             'code:event_profile.py': sha16_file(os.path.realpath(__file__)),
             'code:clock_series.py': sha16_file(os.path.realpath(CS.__file__))}
    fixed.update(admission_sources(law))
    days = np.array([utc_day(t) for t in ev['t'].tolist()], dtype=object)
    in_range = int(sum(1 for d in days.tolist() if first <= d <= last))
    want = st['_coins']; sel_coins = sorted(set(c.upper() for c in ev['coin'][selected].tolist()))
    part = 'EPG.%s' % subject; cols = columns(st); done = {}
    rep.update(tool=TOOL, version=VERSION, subject=subject, part=part, first=first, last=last, out_root=os.path.realpath(out_root),
               requested_coins=list(want) if want is not None else None, settings_name=st['name'], seal_sha16=hashlib.sha256(seal.encode()).hexdigest()[:16],
               sources=dict(sorted(fixed.items())), sealed_support_days=dict(sorted(st['_sealed'].items())),
               window=list(st['_window']) if st['_window'] else None, outside_window_support_days=dict(sorted(st['_outside'].items())),
               events=dict(in_list=int(len(ev['t'])), in_range=in_range, selected=int(len(selected)), written=0),
               requested_coins_without_events=sorted(set(want) - set(sel_coins)) if want is not None else [],
               days={}, coins={}, series={}, status='RUNNING')
    if not len(selected):                                        # C5: a valid empty selection is an explicit success, nothing read
        rep['status'] = 'COMPLETE_EMPTY'
        log('BUILD %s COMPLETE_EMPTY: no alarm selected in %s..%s%s: nothing read, nothing written'
            % (part, first, last, '' if want is None else ' for coins %s' % ','.join(want)))
        return done
    sys.path.insert(0, code_dir)
    if R is None:
        from lab3 import days as LD
        R = LD.Days(lab_root, 'research')
    load_catalog = None
    if write is None:
        from lab3 import write as LW
        write = LW.write_part; load_catalog = LW.load_catalog
    plan = {}
    sdays = days[selected]
    for day in sorted(set(sdays.tolist())):
        sel = selected[sdays == day]
        z = int(dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()) * US
        plan[day] = dict(sel=sel, coins=sorted(set(ev['coin'][sel].tolist())),
                         rd=[shift(day, -k) for k in range(int(st['normal_days']), -1, -1)],       # normal days + the event day
                         nlo=z - int(st['normal_days']) * 86400 * US, nhi=z, sources=dict(fixed), ons=np.full(len(sel), -1, np.int64),
                         owhy=[''] * len(sel), vals={c: np.full(len(sel), NAN) for c, _ in cols}, why={c: [''] * len(sel) for c, _ in cols})
    run_coins = sorted(set(c for p in plan.values() for c in p['coins']))
    maxs = int(st['max_event_s']) * US; rule = st.get('onset_rule', {})
    for day, p in plan.items():                                  # pass 1: onsets and the trigger, per day, one trigger series at a time
        sel, coins, nlo, nhi, vals, why, ons, owhy = (p[k] for k in ('sel', 'coins', 'nlo', 'nhi', 'vals', 'why', 'ons', 'owhy'))
        for tc in sorted(set(c for c in ev['trigger'][sel].tolist() if c)) + ['']:
            idx = [r for r, i in enumerate(sel) if ev['trigger'][i] == tc]
            if not idx:
                continue
            ts = Series(R, tc, p['rd'], coins, step=trig[tc], sealed=sealed) if tc else None
            p['sources'].update(getattr(ts, 'sources', {}))
            if ts is not None:
                tr = _report_series(rep, 'TRIGGER:' + tc, dict(clock=trig[tc]), int(st['normal_days']))
                tr['not_built_days'].update(ts.not_built_days); tr['never_read_days'].update(ts.sealed_days)
            for r in idx:
                i = sel[r]; coin, f = ev['coin'][i], int(ev['t'][i]) * US
                if ev['onset_t'][i] >= 0:
                    on0, osrc = int(ev['onset_t'][i]) * US, 3
                else:
                    on0, osrc = find_onset(ts, coin, f, rule, nlo, nhi)
                    if on0 < 0 and ts is not None and ts.ok:
                        owhy[r] = onset_sealed(ts, f, rule, nlo, nhi)   # the onset support was never read: unavailable, never guessed
                cut = on0 >= 0 and f - on0 > maxs
                on = f - maxs if cut else on0
                ons[r] = on
                ow = owhy[r] or 'NO_ONSET'
                tv = {'onset_to_alarm_s': ((f - on) / US, '') if on >= 0 else (NAN, ow), 'onset_source': (float(osrc), ''),
                      'onset_t': (on / US, '') if on >= 0 else (NAN, ow),
                      'onset_original_t': (on0 / US, '') if on0 >= 0 else (NAN, ow),
                      'onset_truncated': (1.0 if cut else 0.0, '') if on0 >= 0 else (NAN, ow)}
                tv.update(trigger_readings(ts, coin, on, f, nlo, nhi, on_why=ow))
                for k in TRIGGER:
                    vals[col('TRIGGER', k)][r], why[col('TRIGGER', k)][r] = tv[k]
            del ts
    for x, sp in zip(st['series'], spec):                        # pass 2: one series at a time over all days; each day read once
        row = sp['row']; allc = [row] if row else run_coins; cache = {}
        sr = _report_series(rep, x['code'], sp, int(st['normal_days'])); tally = sr['points']
        for day, p in plan.items():
            sel, coins, nlo, nhi, vals, why, ons, owhy = (p[k] for k in ('sel', 'coins', 'nlo', 'nhi', 'vals', 'why', 'ons', 'owhy'))
            for d in [d for d in cache if d < p['rd'][0]]:
                del cache[d]                                      # memory: only this window's days stay
            s = Series(R, x['code'], p['rd'], [row] if row else coins, cache=cache, all_coins=allc, step=sp['clock'], sealed=sealed)
            p['sources'].update(getattr(s, 'sources', {}))
            sr['not_built_days'].update(s.not_built_days); sr['never_read_days'].update(s.sealed_days)
            for r, i in enumerate(sel):
                coin, f = ev['coin'][i], int(ev['t'][i]) * US; side = int(ev['side'][i])
                who = row or coin                                 # btc / market series: the BTC / MARKET row, the same for every alarm
                if not s.ok:
                    for k in SUMMARIES[x['kind']] + SUPPORT:
                        why[col(x['code'], k)][r] = (owhy[r] or 'NO_ONSET') if ons[r] < 0 else 'NOT_BUILT'
                    continue
                for k, (val, rs) in profile_one(s, x['kind'], who, int(ons[r]), f, side, nlo, nhi, unit=sp['unit'], signed=sp['signed'],
                                                tally=tally).items():
                    if rs == 'NO_ONSET' and owhy[r]:
                        rs = owhy[r]                              # the onset was unavailable because its support is sealed
                    vals[col(x['code'], k)][r] = val; why[col(x['code'], k)][r] = rs if not np.isfinite(val) else ''
            del s
        del cache
    os.makedirs(out_root, exist_ok=True)                         # nothing is written before every read above has succeeded
    cat_path = os.path.join(out_root, 'EPG_CATALOG_%s.tsv' % subject)
    tmp = '%s.tmp%d' % (cat_path, os.getpid())
    with open(tmp, 'w') as fh:
        fh.write(catalog_text(subject, st))
    os.replace(tmp, cat_path)                                    # per-process temp: parallel runs share the root
    cat = load_catalog(cat_path) if load_catalog else None
    for day, p in plan.items():                                  # pass 3: write each day (rows grouped by coin once, bits per column)
        sel, coins, vals, why = p['sel'], p['coins'], p['vals'], p['why']
        fs = [int(ev['t'][i]) * US for i in sel]; iday = int(day)
        idx_of = {coin: [r for r, i in enumerate(sel) if ev['coin'][i] == coin] for coin in coins}
        codes = {}
        for c, _ in cols:
            vc = vals[c]; wc = why[c]; fin = np.isfinite(vc); bits = vc.astype('<f8', copy=False).view('<u8')
            rows = {}
            for coin in coins:
                ix = idx_of[coin]; m = len(ix)
                rows[coin] = {'day': [iday] * m, 'as_of_us': [fs[r] for r in ix], 'known_at_us': [fs[r] for r in ix], 'value_kind': [1] * m,
                              'value_bits': [int(bits[r]) if fin[r] else None for r in ix], 'value_txt': [None] * m,
                              'empty_reason': ['' if fin[r] else (wc[r] or 'NO_DATA') for r in ix], 'stale': [0] * m}
            codes['EPG.%s.%s' % (subject, c)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rows}
        write(out_root, iday, part, codes, coins, catalog=cat, sources=p['sources'], seal=seal)
        fin = float(np.mean([np.isfinite(vals[c]).mean() for c, _ in cols]))
        done[day] = 'WRITTEN'; log('DAY %s %s alarms %d coins %d codes %d finite %.3f WRITTEN' % (day, part, len(sel), len(coins), len(cols), fin))
        rep['days'][day] = dict(events=int(len(sel)), coins=list(coins), written=True, sources=dict(sorted(p['sources'].items())))
        rep['events']['written'] += int(len(sel))
        for i in sel.tolist():
            rep['coins'][ev['coin'][i]] = rep['coins'].get(ev['coin'][i], 0) + 1
    _finish_report(rep, st, plan)
    return done


def _finish_report(rep, st, plan):
    """per series: the normal-window support of the events (normal_steps_observed: min, median, max over the events with an onset), the
    events whose normal was NO_NORMAL or SEALED, the events whose window was complete; sets kept as sorted lists; status COMPLETE"""
    for x in st['series']:
        sr = rep['series'][x['code']]
        nso = np.concatenate([p['vals'][col(x['code'], 'normal_steps_observed')] for p in plan.values()])
        exp = np.concatenate([p['vals'][col(x['code'], 'steps_expected')] for p in plan.values()])
        obs = np.concatenate([p['vals'][col(x['code'], 'steps_observed')] for p in plan.values()])
        vsn = [w for p in plan.values() for w in p['why'][col(x['code'], 'vs_normal')]] if 'vs_normal' in SUMMARIES[x['kind']] else []
        f = nso[np.isfinite(nso)]
        sr['events_with_window'] = int(np.isfinite(exp).sum())
        sr['events_complete_window'] = int((np.isfinite(exp) & (exp == obs) & (exp > 0)).sum())
        sr['normal_steps_observed'] = dict(min=int(f.min()), median=float(np.median(f)), max=int(f.max())) if len(f) else None
        sr['normal_unavailable_events'] = {w: vsn.count(w) for w in ('NO_NORMAL', 'SEALED', 'OUTSIDE_WINDOW') if vsn.count(w)}
    for sr in rep['series'].values():
        sr['not_built_days'] = sorted(sr['not_built_days']); sr['never_read_days'] = sorted(sr['never_read_days'])
        sr['points'] = dict(sorted(sr['points'].items()))
    rep['status'] = 'COMPLETE'


def _opts(a, allowed):
    """(positional arguments, {option: value}) of a command line; an option is --name value, each at most once, from allowed"""
    pos, opt, i = [], {}, 0
    while i < len(a):
        if a[i].startswith('--'):
            k = a[i][2:]
            if k not in allowed or i + 1 >= len(a) or k in opt:
                raise SystemExit('option %s: the options are %s, each once and with a value' % (a[i], ', '.join('--' + x for x in allowed)))
            opt[k] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, opt


def write_report(path, rep):
    """the run report as one JSON file, written whole (tmp + fsync + replace)"""
    tmp = '%s.tmp%d' % (path, os.getpid())
    with open(tmp, 'w') as fh:
        fh.write(json.dumps(rep, indent=1, sort_keys=True) + '\n'); fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


REFUSAL_CODE = re.compile(r'^([A-Z][A-Z0-9_]{2,}): ')


def refusal_line(exc):
    """K6: 'REFUSED <CODE>: <reason>' of a refusal: the stable code word a message starts with, else the exception's class name (lab3's
    NotBuilt, Refused, StaleInput, BlockChanged ...; ValueError for an input check without its own code)"""
    msg = str(exc).replace('\n', ' ')
    m = REFUSAL_CODE.match(msg)
    return 'REFUSED %s: %s' % (m.group(1), msg[m.end():]) if m else 'REFUSED %s: %s' % (type(exc).__name__, msg)


def main(a):
    """the command line; a refusal (an input check, a law or reader refusal, an integrity error, a look-ahead refusal) prints one line
    'REFUSED <CODE>: <reason>' and exits 2 (K6), never a traceback; nothing is written"""
    try:
        return _main(a)
    except (ValueError, PermissionError, LookupError) as exc:
        print(refusal_line(exc)); sys.exit(2)
    except Exception as exc:                                          # labcore's LookaheadError is a refusal too; anything else is a bug
        if type(exc).__name__ == 'LookaheadError' and type(exc).__module__.endswith('lookahead'):
            print(refusal_line(exc)); sys.exit(2)
        raise


def _main(a):
    pos, opt = _opts(a, ('coins', 'report', 'window') if a and a[0] == 'build' else ('coins', 'window') if a and a[0] == 'check' else ())
    if pos and pos[0] == 'build' and len(pos) == 9:
        lab, code_dir, alarms, settings, subj, first, last, out = pos[1:9]
        rep = {}
        got = build(lab, code_dir, alarms, settings, subj, first, last, out, coins=opt.get('coins'), report=rep, window=opt.get('window'))
        if 'report' in opt:
            write_report(opt['report'], rep)
        print('BUILD %s days %d written %d status %s' % (subj, len(got), sum(v == 'WRITTEN' for v in got.values()), rep.get('status')))
    elif pos and pos[0] == 'check' and len(pos) == 6:
        st, ev, first, last, trig = preflight(*pos[1:6], coins=opt.get('coins'), window=opt.get('window'))
        print('CHECK OK settings %s series %d columns %d alarms in range %d selected %d coins %s triggers %s sealed support days %s '
              'support days outside the window %s' % (st['name'], len(st['series']), len(columns(st)),
                                                     int(sum(first <= utc_day(t) <= last for t in ev['t'].tolist())), len(st['_sel']),
                                                     ','.join(st['_coins']) if st['_coins'] else 'all', sorted(trig),
                                                     sorted(st['_sealed']) or 'none', sorted(st['_outside']) or 'none'))
    elif pos and pos[0] == 'show' and len(pos) == 6 and not opt:
        out, code_dir, subj, first, last = pos[1:6]
        first, last = valid_day(first), valid_day(last)
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        R = LD.Days(out, 'check'); d = first; vals = {}
        while d <= last:
            if 'EPG.%s' % subj in R.parts(d):                     # a day without the part is skipped by name; any read error propagates
                ix = R.index(d, 'EPG.%s' % subj)
                for code in ix['readings']:
                    rows = R.rows(code, d, ix['coins'])
                    for coin, rr in rows.items():
                        for b in rr['value_bits']:
                            vals.setdefault(code, []).append(np.nan if b is None else float(np.array([b], '<u8').view('<f8')[0]))
            d = shift(d, 1)
        for code, v in vals.items():
            v = np.array(v); print('%-58s finite %.3f median %.4g' % (code.split('.', 2)[2], np.isfinite(v).mean(), np.nanmedian(v) if np.isfinite(v).any() else np.nan))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
