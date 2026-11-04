"""labcore.v2_7.selection (labcore V2_7 CANDIDATE, sub-package labcore/v2_7; ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026; A46R REL-01 items C1, C2, C5, C6). NOT
RELEASED: it enters labcore only through a LAB1 release cycle. THE ONE POPULATION SELECTOR for every event tool (Profile, Context,
Outcomes, Cause, Situations, idea_to_grade): which events of an event list a run describes.

SELECTION (one text, the same in every tool's command):
  list            every row of the list inside the dates (the default: the list is the population)
  coin:BTC        one coin;  coins:BTC,ETH  a set;  all  every coin of the canonical roster (ALL is the same)
  group:NAME      a named group of a group file (--group-file: the shared resolver's dated JSON, or a tsv with columns group (or
                  sector) and coin = one membership for the whole requested range)
  roster          the weekly roster of record (knowledge/roster/ROSTER_<monday>.csv, ROSTER_RULE_V1): a coin is selected on a day only
                  when that day's week lists it; a week with no roster file is GROUP_NOT_EFFECTIVE (typed, never filled), except the
                  aliases its own receipts declare (ROSTER_WEEK_ALIASES_V1.json)
  plus a date range first..last (UTC days, both included), always the caller's: no date constant here; every requested day must pass
  lab3/law.py (labcore.gates.load_law), else SelectionRefused('SEALED_REQUEST') before anything is read.
MEMBERSHIP IS NOT SYNTAX: a coin is valid only when the canonical roster names it. The canonical roster is the historical lab roster
document (ROSTER_BUILD.json: the union of the lab's PRICE indexes, every index pinned by sha256; DEV2's, approved by OX-CODE1) plus the
members of the roster-of-record weeks of the requested range; an unknown coin or group is refused with its code (UNKNOWN_COIN,
UNKNOWN_GROUP, MALFORMED_COINS, MALFORMED_DATE, REVERSED_RANGE ...). The resolver is NOT copied: the shared, reviewed DEV2 resolver
(population.resolve_population) and event_selection.select_events are imported from their pinned files.
EMPTY IS A RESULT: a valid selection with no event is status EMPTY_SELECTED_POPULATION with its full coverage receipt, never an error.
COVERAGE (requested and observed, C6): the request (kind, members, dated intervals, group gaps), the list rows inside / outside the range,
the rows excluded and why (COIN_NOT_SELECTED, NOT_A_MEMBER_THAT_DAY, GROUP_NOT_EFFECTIVE), the selected events by day and coin, and the
source state of every selected event from the canonical roster's pinned PRICE indexes: IN_SOURCE, NOT_IN_SOURCE (the lab part exists
that day, the coin is not in its index), SOURCE_NOT_DECLARED (no pinned index for that day). Never PRELISTING: no listing source here.
  select(events_path, first, last, selection='list', group_file=None, subject='LIST', ...) -> Selection dict (rows kept in file order)
  selected_text(sel) -> the text of a list holding the original '#' lines, its header and the selected rows byte for byte (pure: the
      command writes it; this module writes nothing)
  resolve_selection(ev, coins=None, group=None, group_file=None, first=None, last=None) -> (set of coins or None for every coin, record):
      the interface event_situations already uses (--coins A,B|ALL, --group-file F --group NAME), with roster membership checked.
  roster_unknown(R, coins, last, event_days, law, outside) -> the coins no PRICE index of a readable day up to last names (registered
      here from alarm_context_ed2's rule; Context's own copy stays until LAB1's promotion switches its import)
  parse(text) -> (kind, value); SelectionRefused(code, detail)
WINDOW FIRST (S3, FIX_ROUND3: Outcomes A51R2-01, Cause R2-03; note SHARED_S3_NOTE_V2.md): the caller's window is checked before any file is
opened, and every roster, listing or index scan opens only days inside it, never the day before; what would need that day (the first
step's predecessor, a D-1 warm-up) is unknown, typed, never read.
  check_window(first, last, window) -> (first, last, (win_first, win_last) or None): pure, reads nothing; SELECTION_OUTSIDE_WINDOW, BAD_WINDOW
  in_window(window) -> inside(day) predicate; roster_universe(R, last, window=None, law=None) -> (coins, days read): window days only"""
import csv, datetime as dt, hashlib, importlib.util, io, json, os, re, sys

HERE = os.path.dirname(os.path.realpath(__file__))
FORENSICS = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
DEV = os.path.join(FORENSICS, 'team', 'OUTSIDE', 'COORD', 'development')
RESOLVER_PATH = os.path.join(DEV, 'DEV2', 'shared_population_v2', 'population.py')
EVSEL_PATH = os.path.join(DEV, 'performance_v2', 'labcore_candidate', 'event_selection.py')
ROSTER_DOC = os.path.join(DEV, 'DEV2', 'a02p_chain_v1', 'full_population', 'ROSTER_BUILD.json')
ROSTER_DOC_SHA256 = 'b93de33b2a73a56eae854b85fcb0dd30fac93472686af17eb63da2b2957da11b'
WEEKLY_DIR = '<RUNNER_TREE>/forensics/knowledge/roster'
ALIASES = os.path.join(HERE, 'ROSTER_WEEK_ALIASES_V1.json')
WEEKLY_GROUP = 'ROSTER_RULE_V1'
KINDS = ('list', 'coins', 'all', 'group', 'roster')
US = 1_000_000


class SelectionRefused(ValueError):
    """a selection that cannot be made, named by its code (the resolver's codes, or BAD_SELECTION, SEALED_REQUEST, ROSTER_* ...)"""
    def __init__(self, code, detail=''):
        super().__init__('%s: %s' % (code, detail) if detail else code); self.code = code; self.detail = detail


def _load(path, name):
    m = sys.modules.get(name)
    if m is not None and os.path.realpath(getattr(m, '__file__', '')) == os.path.realpath(path):
        return m
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    sys.modules[name] = m
    return m


P = _load(RESOLVER_PATH, 'labcore_ext_population_v2')                 # DEV2 shared_population_v2/population.py (pinned by sha16)
ES = _load(EVSEL_PATH, 'labcore_ext_event_selection')                 # performance_v2/labcore_candidate/event_selection.py (pinned)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    with open(p, 'rb') as f:
        return sha256_bytes(f.read())


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def _day(s):
    return dt.datetime.strptime(s, '%Y%m%d').date()


def _ymd(d):
    return d.strftime('%Y%m%d')


def utc_day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def parse(text):
    """'list' | 'all' | 'coin:X' | 'coins:A,B' | 'group:NAME' | 'roster' -> (kind, value)"""
    t = (text or 'list').strip()
    low = t.lower()
    if low in ('list', 'all', 'roster'):
        return low, None
    if ':' in t:
        k, v = t.split(':', 1); k = k.strip().lower(); v = v.strip()
        if k in ('coin', 'coins') and v:
            return ('all', None) if v.upper() == 'ALL' else ('coins', v)
        if k == 'group' and v:
            return 'group', v
    raise SelectionRefused('BAD_SELECTION', '%r: write list, all, coin:X, coins:A,B, group:NAME or roster' % (text,))


def read_list(path):
    """the event list as written: '#' lines, header, and every row with its line number (ordinal), coin, t and UTC day"""
    raw = open(path, 'rb').read(); text = raw.decode('utf-8')
    head, rows, hdr = [], [], None
    for line in text.splitlines(keepends=True):
        if line.startswith('#'):
            head.append(line); continue
        if hdr is None:
            hdr = next(csv.reader([line.rstrip('\r\n')], delimiter='\t')); hline = line
            if 'coin' not in hdr or 't' not in hdr:
                raise SelectionRefused('BAD_LIST', '%s: columns coin and t are required (got %s)' % (path, hdr))
            ci, ti = hdr.index('coin'), hdr.index('t'); continue
        if not line.strip():
            continue
        r = next(csv.reader([line.rstrip('\r\n')], delimiter='\t'))
        try:
            t = float(r[ti])
        except (IndexError, ValueError):
            raise SelectionRefused('BAD_LIST', '%s: row %d has no number t' % (path, len(rows) + 1))
        rows.append((len(rows), line, r[ci].strip(), t, utc_day(t)))
    if hdr is None:
        raise SelectionRefused('BAD_LIST', '%s: no header' % path)
    return dict(path=os.path.abspath(path), sha256=sha256_bytes(raw), head=head, header=hline, rows=rows)


def _mondays(first, last):
    m = first - dt.timedelta(days=first.weekday())
    while m <= last:
        yield m; m += dt.timedelta(days=7)


def weekly_roster(first, last, weekly_dir=WEEKLY_DIR, aliases=ALIASES, window=None):
    """the roster-of-record weeks touching first..last as the resolver's dated group document, and what was read. With a caller window
    (S3) a week whose file is stamped outside it (its Monday, or an alias's Monday) is NOT opened: its days are GROUP_NOT_EFFECTIVE and the
    week is listed in info['weeks_outside_window']"""
    al = json.load(open(aliases))['aliases'] if aliases else {}
    inside = in_window(window)
    files, segs, missing, used, outside = {}, [], [], {}, []
    for m in _mondays(_day(first), _day(last)):
        w = _ymd(m); src = w
        p = os.path.join(weekly_dir, 'ROSTER_%s.csv' % w)
        if not inside(w):
            outside.append(w); continue
        if not os.path.isfile(p) and w in al:
            src = al[w]['uses']; p = os.path.join(weekly_dir, 'ROSTER_%s.csv' % src); used[w] = src
            if not inside(src):
                outside.append(w); continue
        if not os.path.isfile(p):
            missing.append(w); continue
        raw = open(p, 'rb').read(); files[os.path.basename(p)] = sha256_bytes(raw)
        coins = sorted({r['coin'].strip().upper() for r in csv.DictReader(io.StringIO(
            ''.join(l for l in raw.decode('utf-8').splitlines(keepends=True) if not l.startswith('#')))) if r.get('coin', '').strip()})
        segs.append({'first': w, 'last': _ymd(m + dt.timedelta(days=6)), 'coins': coins})
    ident = sha256_bytes(canonical({'files': files, 'aliases': sha256_file(aliases) if aliases else None}).encode())
    doc = {'data': {'schema_version': 1, 'version': 'ROSTER_RULE_V1_WEEKS_' + ident[:16], 'timezone': 'UTC',
                    'groups': {WEEKLY_GROUP: segs}}, 'source_sha256': ident}
    return doc, dict(files=files, weeks_missing=missing, aliases_used=used, weeks=len(segs), weeks_outside_window=outside)


def group_document(path, first, last):
    """a group file as the resolver's document: the dated JSON (schema 1) as it is, or a tsv (group or sector, coin) = one membership for
    the requested range"""
    raw = open(path, 'rb').read(); sha = sha256_bytes(raw)
    if raw.lstrip()[:1] == b'{':
        return {'data': json.loads(raw), 'source_sha256': sha}
    rows = list(csv.reader((l for l in raw.decode('utf-8').splitlines() if l and not l.startswith('#')), delimiter='\t'))
    h = rows[0] if rows else []
    g = 'group' if 'group' in h else 'sector' if 'sector' in h else None
    if g is None or 'coin' not in h:
        raise SelectionRefused('BAD_SELECTION', '%s: needs columns group (or sector) and coin' % path)
    gi, ci = h.index(g), h.index('coin'); mem = {}
    for r in rows[1:]:
        if len(r) > max(gi, ci) and r[gi].strip() and r[ci].strip():
            mem.setdefault(r[gi].strip(), set()).add(r[ci].strip().upper())
    return {'data': {'schema_version': 1, 'version': 'TSV_' + sha[:16], 'timezone': 'UTC',
                     'groups': {k: [{'first': first, 'last': last, 'coins': sorted(v)}] for k, v in mem.items()}}, 'source_sha256': sha}


def roster_document(first, last, extra_coins=(), roster_doc=ROSTER_DOC, roster_sha256=ROSTER_DOC_SHA256, verify_sources=True):
    """the canonical roster as the resolver's document; its pinned PRICE indexes of the requested days are rechecked on disk"""
    raw = open(roster_doc, 'rb').read()
    if sha256_bytes(raw) != roster_sha256:
        raise SelectionRefused('ROSTER_DOC_CHANGED', '%s is %s, the selection pins %s' % (roster_doc, sha256_bytes(raw)[:16], roster_sha256[:16]))
    data = json.loads(raw); checked = 0
    if verify_sources:
        for p, sha in sorted(data.get('source_sha256', {}).items()):
            d = p.split('day=', 1)[1][:8] if 'day=' in p else None
            if d is None or not first <= d <= last:
                continue
            if not os.path.isfile(p):
                raise SelectionRefused('ROSTER_SOURCE_MISSING', p)
            if sha256_file(p) != sha:
                raise SelectionRefused('ROSTER_SOURCE_CHANGED', '%s changed since the roster was made' % p)
            checked += 1
    extra = sorted(set(extra_coins) - set(data['coins']))
    if extra:
        data = dict(data, coins=list(data['coins']) + extra, availability=dict(data.get('availability', {}), **{c: {'days': []} for c in extra}))
        src = sha256_bytes(canonical({'roster': roster_sha256, 'roster_of_record_members': extra}).encode())
    else:
        src = roster_sha256
    return {'data': data, 'source_sha256': src}, dict(path=roster_doc, sha256=roster_sha256, added_members=extra, sources_rechecked=checked)


class _Population:
    """the list's rows as the population event_selection.select_events reads (subject, source_sha256, select)"""
    def __init__(self, rows, subject, sha256):
        self.subject = subject; self.source_sha256 = sha256
        self._ev = [dict(coin=c.upper(), alarm_us=int(round(t * US)), source_ordinal=o) for o, _, c, t, _ in rows]

    def select(self, *, coins, first_us, end_us):
        cs = frozenset(coins)
        return tuple(e for e in self._ev if e['coin'] in cs and first_us <= e['alarm_us'] < end_us)


def _check_law(first, last, law):
    if law is None:
        from ..gates import load_law
        law = load_law()
    d = _day(first); bad = []
    while d <= _day(last):
        why = law.research_refusal(_ymd(d))
        if why:
            bad.append('%s (%s)' % (_ymd(d), why))
        d += dt.timedelta(days=1)
    if bad:
        raise SelectionRefused('SEALED_REQUEST', 'lab3/law.py refuses %d requested day(s), e.g. %s' % (len(bad), bad[0]))


def _norm_dates(first, last):
    """YYYYMMDD or YYYY-MM-DD, a real calendar day (the resolver's own rule, checked again inside it) -> two YYYYMMDD texts"""
    out = []
    for x in (first, last):
        x = str(x)
        try:
            out.append(_ymd(dt.datetime.strptime(x, '%Y%m%d' if len(x) == 8 and x.isdigit() else '%Y-%m-%d').date()))
        except ValueError:
            raise SelectionRefused('MALFORMED_DATE', x)
    if out[0] > out[1]:
        raise SelectionRefused('REVERSED_RANGE', '%s..%s' % tuple(out))
    return out


def _window(window):
    """None, a (FIRST, LAST) pair or 'FIRST..LAST' / 'FIRST,LAST' text -> (first, last) YYYYMMDD or None; BAD_WINDOW otherwise"""
    if window is None:
        return None
    parts = re.split(r'\.\.|,', window.strip()) if isinstance(window, str) else list(window)
    if len(parts) != 2:
        raise SelectionRefused('BAD_WINDOW', 'window %r: two days FIRST..LAST' % (window,))
    try:
        a, b = _norm_dates(parts[0], parts[1])
    except SelectionRefused as e:
        raise SelectionRefused('BAD_WINDOW', 'window %r: %s' % (window, e))
    return a, b


def check_window(first, last, window):
    """THE first check of every entry path (S3), before any file is opened: first..last real days, first <= last, and inside the caller's
    window -> (first, last, window pair or None); SELECTION_OUTSIDE_WINDOW / BAD_WINDOW / MALFORMED_DATE / REVERSED_RANGE. Reads nothing."""
    w = _window(window)
    first, last = _norm_dates(first, last)
    if w is not None and not (w[0] <= first <= last <= w[1]):
        raise SelectionRefused('SELECTION_OUTSIDE_WINDOW', 'the requested %s..%s is not inside the caller window %s..%s' % (first, last, w[0], w[1]))
    return first, last, w


def in_window(window):
    """inside(day) -> True for a day of the caller's window (every day when window is None)"""
    w = _window(window)
    return (lambda d: True) if w is None else (lambda d: w[0] <= str(d) <= w[1])


def _listing(R):
    return R.all_days() if hasattr(R, 'all_days') else R.days()


def roster_universe(R, last, window=None, law=None):
    """event_cause's roster rule, window first (S3, Cause R2-03): every coin of the PRICE index of each built, research-readable day up to
    last, opening ONLY days inside the caller's window (never the day before it) -> (set of coins, [days read]). A day law.py refuses is
    not opened either. R: lab3 Days-like (days() or all_days(), parts(day) when it has it, index(day, part))."""
    inside = in_window(window); out = set(); read = []
    for d in _listing(R):
        if d > last or not inside(d) or (law is not None and law.research_refusal(str(d))):
            continue
        if hasattr(R, 'parts'):
            if 'PRICE' not in R.parts(d):
                continue
            ix = R.index(d, 'PRICE')
        else:
            try:
                ix = R.index(d, 'PRICE')
            except LookupError:                                          # lab3 NotBuilt: no PRICE part that day
                continue
        out.update(ix['coins']); read.append(d)
    return out, read


def select(events_path, first, last, selection='list', group_file=None, subject='LIST', roster_doc=ROSTER_DOC,
           roster_sha256=ROSTER_DOC_SHA256, weekly_dir=WEEKLY_DIR, aliases=ALIASES, verify_sources=True, law=None, window=None):
    """-> Selection: dict(status SELECTED | EMPTY_SELECTED_POPULATION, request, identity, cache_key, coverage, rows [(ordinal, line,
    coin, t, day)] in file order, head, header, resolver). Refuses (SelectionRefused) before any tool runs; the caller's window (S3) is
    checked before anything is read, and no day outside it is opened."""
    kind, value = parse(selection)
    first, last, win = check_window(first, last, window)
    _check_law(first, last, law)
    L = read_list(events_path)
    wdoc, winfo = weekly_roster(first, last, weekly_dir, aliases, win)
    wcoins = sorted({c for s in wdoc['data']['groups'][WEEKLY_GROUP] for c in s['coins']})
    rdoc, rinfo = roster_document(first, last, wcoins, roster_doc, roster_sha256, verify_sources)
    req = {'start': first, 'end': last, 'timezone': 'UTC', 'endpoints': 'date_inclusive'}; gdoc = None
    if kind in ('list', 'all'):
        req['coins'] = 'all'
    elif kind == 'coins':
        req['coins'] = value
    elif kind == 'group':
        if not group_file:
            raise SelectionRefused('BAD_SELECTION', 'group:%s needs a group file' % value)
        gdoc = group_document(group_file, first, last); req['group'] = value
    else:
        gdoc = wdoc; req['group'] = WEEKLY_GROUP
    policy = {'version': 'CALLER_RANGE_UNDER_LAB3_LAW', 'timezone': 'UTC', 'allowed_first': first, 'allowed_last': last, 'protected': []}
    ref = {'subject': subject, 'source_sha256': L['sha256']}
    try:
        man = P.resolve_population(req, rdoc, policy=policy, groups_document=gdoc, population_reference=ref)
    except P.PopulationError as e:
        raise SelectionRefused(e.code, e.detail)
    inr = [r for r in L['rows'] if first <= r[4] <= last]
    if kind == 'list':
        rows = inr
    else:
        keep = {e['source_ordinal'] for e in ES.select_events(_Population(L['rows'], subject, L['sha256']), man)}
        rows = [r for r in L['rows'] if r[0] in keep]
    # excluded rows (inside the range) and why
    gaps = [(i['first'], i['last']) for i in man['resolved']['intervals'] if i['membership_status'] == 'GROUP_NOT_EFFECTIVE']
    chosen = {r[0] for r in rows}; excluded = {}
    for r in inr:
        if r[0] in chosen:
            continue
        why = ('COIN_NOT_SELECTED' if kind == 'coins' else
               'GROUP_NOT_EFFECTIVE' if any(a <= r[4] <= b for a, b in gaps) else
               'NOT_IN_CANONICAL_ROSTER' if r[2].upper() not in set(rdoc['data']['coins']) else 'NOT_A_MEMBER_THAT_DAY')
        excluded[why] = excluded.get(why, 0) + 1
    # source state of every selected event, from the canonical roster's pinned PRICE indexes
    av = {c: set(v.get('days', [])) for c, v in rdoc['data'].get('availability', {}).items()}
    sdays = {p.split('day=', 1)[1][:8] for p in rdoc['data'].get('source_sha256', {}) if 'day=' in p}
    states, notin = {}, {}
    for _, _, c, _, d in rows:
        s = 'IN_SOURCE' if d in av.get(c.upper(), ()) else 'NOT_IN_SOURCE' if d in sdays else 'SOURCE_NOT_DECLARED'
        states[s] = states.get(s, 0) + 1
        if s != 'IN_SOURCE':
            notin.setdefault(s, set()).add('%s %s' % (c, d))
    by_day, by_coin = {}, {}
    for _, _, c, _, d in rows:
        by_day[d] = by_day.get(d, 0) + 1; by_coin[c] = by_coin.get(c, 0) + 1
    not_canon = sorted({r[2] for r in rows if r[2].upper() not in set(rdoc['data']['coins'])})
    cov = dict(
        requested=dict(kind=kind, value=value, first=first, last=last, calendar_days=(_day(last) - _day(first)).days + 1,
                       members=man['resolved']['members'], intervals=man['resolved']['intervals'], group_gaps=gaps,
                       roster_of_record=winfo, canonical_roster=rinfo),
        list=dict(rows=len(L['rows']), rows_in_range=len(inr), rows_outside_range=len(L['rows']) - len(inr)),
        observed=dict(events=len(rows), coins=sorted(by_coin), days=sorted(by_day), events_by_day=by_day, events_by_coin=by_coin),
        excluded_in_range=excluded,
        source_states=dict(counts=states, cells={k: sorted(v) for k, v in notin.items()}, event_coins_not_in_canonical_roster=not_canon,
                           meaning='the lab PRICE index of the event day (canonical roster sources); not a listing date, never PRELISTING'),
        member_coverage=man['coverage']['canonical_roster'])
    ident = dict(list_sha256=L['sha256'], selection=selection, resolver_cache_key=man['cache_key'], roster_doc=rinfo['sha256'],
                 roster_of_record=winfo['files'], group_file=(gdoc or {}).get('source_sha256') if kind == 'group' else None,
                 selected_sha256=sha256_bytes(canonical([r[0] for r in rows]).encode()),
                 resolver_file=sha256_file(RESOLVER_PATH)[:16], event_selection_file=sha256_file(EVSEL_PATH)[:16],
                 selection_file=sha256_file(os.path.realpath(__file__))[:16])
    return dict(status='SELECTED' if rows else 'EMPTY_SELECTED_POPULATION', request=dict(kind=kind, value=value, first=first, last=last,
                subject=subject, list=L['path'], group_file=os.path.abspath(group_file) if group_file else None,
                window=list(win) if win else None),
                identity=ident, cache_key=sha256_bytes(canonical(ident).encode()), coverage=cov, rows=rows, head=L['head'],
                header=L['header'], resolver={k: man[k] for k in ('status', 'requested', 'identity', 'cache_key')})


def selected_text(sel):
    """the selected rows as a list file's text (pure; the command writes it): every '#' line of the original (declarations included),
    its header, the chosen rows byte-equal"""
    return ''.join(sel['head']) + sel['header'] + ''.join(r[1] for r in sel['rows'])


def roster_unknown(R, coins, last, event_days, law, outside=lambda d: False, window=None):
    """REGISTERED from alarm_context_ed2.py 0d70516ee7b5ea5a (context_fix2; event_cause.roster_universe's rule), unchanged in behaviour
    (Context keeps its own frozen copy until LAB1's promotion switches its import; F1 stays open until then): the
    selected coins that are never in the canonical roster read from the store itself = the PRICE index of a built, research-readable day
    up to last, inside the caller's window (outside(day) True = never opened; window (S3): only days inside it, never the day before; an
    event day or last outside it refuses SELECTION_OUTSIDE_WINDOW before any open). The event days are read first, then earlier days only
    for a coin not found yet. R: a lab3 Days-like reader with all_days() (or days()), parts(day), index(day, part); law: lab3/law.py (or a
    planted law with research_refusal). -> sorted unknown coins"""
    w = _window(window)
    if w is not None and (last > w[1] or any(not w[0] <= str(d) <= w[1] for d in event_days)):
        raise SelectionRefused('SELECTION_OUTSIDE_WINDOW', 'last %s or an event day of %s is not inside the caller window %s..%s'
                               % (last, sorted(set(event_days))[:3], w[0], w[1]))
    inside = in_window(w)
    want = set(coins); seen = set(); part = 'PRICE'
    days = [d for d in _listing(R) if d <= last and inside(d) and not outside(d) and not law.research_refusal(str(d))]
    first = [d for d in sorted(set(event_days)) if d in set(days)]
    for d in first + [d for d in reversed(days) if d not in set(first)]:
        if want <= seen:
            break
        if part not in R.parts(d):
            continue
        seen |= want & set(R.index(d, part)['coins'])
    return sorted(want - seen)


def manifest_view(sel):
    """the selection as a run plan / manifest records it (rows by count and digest; the selected list file holds them)"""
    return {k: sel[k] for k in ('status', 'request', 'identity', 'cache_key', 'coverage', 'resolver')}


def resolve_selection(ev, coins=None, group=None, group_file=None, first=None, last=None, roster_doc=ROSTER_DOC,
                      roster_sha256=ROSTER_DOC_SHA256, weekly_dir=WEEKLY_DIR, aliases=ALIASES, law=None, window=None):
    """event_situations' interface: ev {'coin', 't' arrays}; --coins A,B | ALL, or --group-file F --group NAME -> (set of coins, or None
    for every coin, record). Coins and group members are checked against the canonical roster (not the list); a coin with no event is a
    valid empty selection; a dated group whose membership changes inside the range needs select() (DATED_GROUP: refused here)."""
    if coins and group:
        raise SelectionRefused('BAD_SELECTION', 'give coins or a group, not both')
    if group and not group_file:
        raise SelectionRefused('BAD_SELECTION', 'a group needs its group file')
    days = sorted({utc_day(t) for t in list(ev['t'])})
    first = first or (days[0] if days else None); last = last or (days[-1] if days else None)
    if first is None:
        raise SelectionRefused('BAD_SELECTION', 'an empty list needs explicit first and last days')
    first, last, win = check_window(first, last, window)
    _check_law(first, last, law)
    wdoc, winfo = weekly_roster(first, last, weekly_dir, aliases, win)
    wcoins = sorted({c for s in wdoc['data']['groups'][WEEKLY_GROUP] for c in s['coins']})
    rdoc, rinfo = roster_document(first, last, wcoins, roster_doc, roster_sha256, True)
    listed = sorted({str(c).upper() for c in list(ev['coin'])})
    req = {'start': first, 'end': last, 'timezone': 'UTC', 'endpoints': 'date_inclusive'}; gdoc = None
    if group:
        gdoc = group_document(group_file, first, last); req['group'] = group
    else:
        req['coins'] = coins if coins else 'all'
    policy = {'version': 'CALLER_RANGE_UNDER_LAB3_LAW', 'timezone': 'UTC', 'allowed_first': first, 'allowed_last': last, 'protected': []}
    try:
        man = P.resolve_population(req, rdoc, policy=policy, groups_document=gdoc, population_reference=None)
    except P.PopulationError as e:
        raise SelectionRefused(e.code, e.detail)
    ivs = man['resolved']['intervals']
    if group and len({tuple(i['coins']) for i in ivs}) > 1:
        raise SelectionRefused('DATED_GROUP', 'group %s changes membership inside %s..%s: use labcore.selection.select' % (group, first, last))
    mem = man['resolved']['members']
    rec = dict(kind='group' if group else 'coins' if coins and coins.upper() != 'ALL' else 'all', first=first, last=last, members=mem,
               members_in_list=sorted(set(mem) & set(listed)), resolver_cache_key=man['cache_key'], canonical_roster=rinfo['sha256'],
               roster_of_record=winfo['files'], status='SELECTED' if set(mem) & set(listed) else 'EMPTY_SELECTED_POPULATION')
    if group:
        rec.update(group=group, group_file=os.path.abspath(group_file), group_file_sha256=gdoc['source_sha256'])
    return (None if rec['kind'] == 'all' else set(mem)), rec
