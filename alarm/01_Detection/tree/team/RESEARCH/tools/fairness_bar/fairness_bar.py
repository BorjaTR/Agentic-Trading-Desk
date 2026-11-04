"""RESEARCH tools/fairness_bar (T02; owner SCOUT, built by BUILD2 23 Oct 2026; tests TEST1; reviewers QUANT, LAB4, LAB1). PAPER ONLY.
Design: README.md ARCHITECTURE V1.3 (this file builds it; names from tests/INTERFACE_FAIRNESS_BAR_V1.md). FAST PATH (STRATEGY 12:11:29Z):
code now, TEST1's tests must pass before the merge, every review MUST fixed before the first real-data run.
QUESTION: for a new result of an idea family, how many tries has the family had (counted and effective), and what bar must the result
clear after all of them: deflated Sharpe on per-wave results (Bailey and Lopez de Prado 2014), wave t >= 3 (Harvey, Liu and Zhu), Holm
across the family, with the waves it would need.
UNIT: one evaluated result (a per-wave receipt by sha16) against its family at the result's own time.
KNOWN AT: the census reads only tries stamped at or before the result's time (as_of); bar() REFUSES a joined try stamped later (the join
guard); a later try never changes an old result's bar.
NOT IN IT: no price, no P&L, no outcome read of its own (it takes the per-wave values a money tool already made), no change to any verdict.
Uses labcore (the ONE wave module, the sha16, the settings loader, the join guard); holds no wave code of its own.
  families(path) / family_of(text, source, fams)   the frozen family map (first matching row wins)
  read_tries(sources)                              the census readers: every row of every named source is one try; a malformed or
                                                   duplicate row is a REFUSAL naming file and line (LAB4 M2), never skipped
  census(tries, fams, as_of_utc)                   family x source counts (UNMAPPED printed, never dropped; a WITHDRAWN try once)
  neff(per_wave, n_without, min_shared)            effective number of tries from pairwise correlations on shared waves
  sr_star, dsr, holm, bhy, waves_needed, evaluate, bar   the bar (README sections 1f, 3)"""
import hashlib, json, math, os, re, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.realpath(os.path.join(HERE, '..'))
TEAM = os.path.realpath(os.path.join(HERE, '..', '..', '..'))
FORENSICS = os.path.dirname(TEAM)                                 # the repo root that release paths and the migration record name
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
from labcore import ids, lookahead, waves        # noqa: E402  (the ONE wave module; never a copy here)

EULER = 0.5772156649015329
DEFAULT_SETTINGS = dict(gap_s=1800, t_bar=3.0, holm_alpha=0.05, min_waves=11, boot=2000, seed=20261023, dsr_bar=0.95,
                        require_wave_sha=True)        # LAB4 M1 (V1.3): a receipt without labcore's wave-module sha16 is refused
WAVE_MODULE = os.path.join(TOOLS, 'labcore', 'waves.py')
SOURCES = {
    'ledger': os.path.join(TEAM, 'RESEARCH', 'TRIES_LEDGER_V1.tsv'),
    'model': os.path.join(TEAM, 'RESEARCH', 'SCOUT', 'receipts', 'SCOUT_LEDGER_MODEL_V1.tsv'),
    'screen': os.path.join(TEAM, 'RESEARCH', 'QUANT', 'SCREEN_LEDGER_V1.tsv'),
    'try': os.path.join(TEAM, 'RESEARCH', 'TRY_LEDGER.tsv'),
    'results': None}                                # every */RESULTS_*_V1.tsv under team (found each run, by sha16)


# ---------------------------------------------------------------- families
def families(path=None):
    """FAMILIES_V1.tsv rows in file order: {pattern, source, family, why, rx}"""
    path = path or os.path.join(HERE, 'FAMILIES_V1.tsv')
    out = []; head = None
    for l in open(path, encoding='utf-8'):
        if l.startswith('#') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if head is None:
            head = f; continue
        r = dict(zip(head, f)); r['rx'] = re.compile(r['pattern']); out.append(r)
    return out


def family_of(text, source, fams):
    for r in fams:
        srcs = r['source'].split('|')
        if ('any' in srcs or source in srcs) and r['rx'].search(text or ''):
            return r['family']
    return 'UNMAPPED'


# ---------------------------------------------------------------- the census readers (README 1c)
STAMP = re.compile(r'^(\d{4})-?(\d{2})-?(\d{2})T(\d{2}):?(\d{2})(?::?(\d{2}))?Z$')


def utc_key(s, where):
    """'2026-10-22T07:08Z', '2026-10-23T06:29:33Z' or '20261020T141538Z' -> '20261020T141538Z'; anything else is a refusal"""
    m = STAMP.match((s or '').strip())
    if not m:
        raise ValueError('%s: bad time stamp %r: census refused' % (where, s))
    y, mo, d, h, mi, se = m.groups()
    return '%s%s%sT%s%s%sZ' % (y, mo, d, h, mi, se or '00')


def _read(path, source, ncols_min):
    """-> [(line_no, {header: value})]; a row with the wrong number of fields is a refusal naming file and line"""
    out = []; head = None
    for i, l in enumerate(open(path, encoding='utf-8'), 1):
        if l.startswith('#') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if head is None:
            head = f
            if len(head) < ncols_min:
                raise ValueError('%s line %d: header has %d columns: census refused' % (path, i, len(head)))
            continue
        if len(f) != len(head):
            raise ValueError('%s line %d: %d fields, the header has %d: census refused (LAB4 M2)' % (path, i, len(f), len(head)))
        out.append((i, dict(zip(head, f))))
    return out


def _results_files():
    """every seat's RESULTS_<SEAT>_V1.tsv one to three folders under team (a seat folder; a walk of the whole team tree is too slow)"""
    import glob
    out = set()
    for depth in ('*', '*/*', '*/*/*'):
        out.update(p for p in glob.glob(os.path.join(TEAM, depth, 'RESULTS_*_V1.tsv'))
                   if re.match(r'^RESULTS_[A-Z0-9]+_V1\.tsv$', os.path.basename(p)) and '_to_delete' not in p)
    return sorted(out)


def _read_tries_unchecked(sources=None):
    """every row of every named source -> in exactly one try {try_utc, source, text, status, ask_id, file, line, rows}; a RESULT or WITHDRAWN
    row is merged into its try (rows lists them all); refusals (ValueError) name file and line for a malformed row, a bad stamp, a
    missing id or a duplicate (a second row of the same kind for one try)"""
    src = dict(SOURCES) if sources is None else dict(sources)
    tries = []
    for name in ('ledger', 'model', 'screen', 'try', 'results'):
        if name not in src:
            continue
        paths = _results_files() if (name == 'results' and src[name] is None) else ([src[name]] if isinstance(src[name], str) else list(src[name]))
        for p in paths:
            if not os.path.exists(p):
                raise ValueError('census source %s: %s missing: census refused' % (name, p))
            for i, r in _read(p, name, 3):
                where = '%s line %d' % (p, i)
                if name == 'ledger':
                    t = dict(try_utc=utc_key(r.get('try_utc'), where), ask_id=r.get('ask_id', ''), status=r.get('status', ''),
                             text=' '.join(r.get(k, '') for k in ('idea', 'purpose', 'kind', 'ask_id')))
                elif name == 'model':
                    t = dict(try_utc=utc_key(r.get('utc'), where), ask_id=r.get('try', ''), text=' '.join(r.get(k, '') for k in ('what', 'data')),
                             status='WITHDRAWN' if 'WITHDRAWN' in r.get('verdict', '').upper() else 'OK')
                elif name == 'screen':
                    t = dict(try_utc=utc_key(r.get('utc'), where), ask_id='%s:%d' % (os.path.basename(p), i), status='OK',
                             text=' '.join(r.get(k, '') for k in ('question', 'value', 'subject', 'group', 'direction')))
                elif name == 'try':
                    t = dict(try_utc=utc_key(r.get('utc'), where), ask_id='%s:%s' % (r.get('sha16', ''), r.get('version', '')), status='OK',
                             text=' '.join(r.get(k, '') for k in ('subject', 'what is tried')), _has_result=bool(r.get('result', '').strip()))
                else:
                    t = dict(try_utc=utc_key(r.get('utc'), where), ask_id='%s:%s' % (r.get('seat', ''), r.get('id', '')), status='OK',
                             text=' '.join(r.get(k, '') for k in ('scheme', 'window', 'ledger_row')))
                if not t['ask_id']:
                    raise ValueError('%s: no id: census refused (LAB4 M2)' % where)
                t.update(source=name, file=p, line=i); tries.append(t)
    # ONE TRY = its PREREG (or first) row plus the rows that close it: a ledger RESULT row (<ask_id>_R) or WITHDRAWN row (<ask_id>_W),
    # a TRY_LEDGER result row (the same sha16 and version, result filled) (ledger README v4: count = PREREG rows + door rows). Those rows
    # are merged into their try (listed in its 'rows'), never counted twice and never dropped; a second row of the same kind for one try
    # is a duplicate: REFUSED naming file and line (LAB4 M2).
    merged = {}; order = []
    for t in tries:
        kind = 'open'
        base = t['ask_id']
        if t['source'] == 'ledger':
            m = re.match(r'^(.*)_(R|W)$', base)
            if m:
                base, kind = m.group(1), {'R': 'result', 'W': 'withdrawn'}[m.group(2)]
        elif t['source'] == 'try':
            kind = 'result' if t.get('_has_result') else 'open'
        key = (t['source'], base)
        if key not in merged:
            merged[key] = dict(t, ask_id=base, rows=[(t['file'], t['line'], kind)], kinds={kind})
            if kind == 'withdrawn':
                merged[key]['status'] = 'WITHDRAWN'
            order.append(key); continue
        m0 = merged[key]
        if kind in m0['kinds']:
            f0, l0, _ = [r for r in m0['rows'] if r[2] == kind][0]
            raise ValueError('%s line %d: id %s already at line %d of %s: a duplicate row, census refused (LAB4 M2)' % (
                t['file'], t['line'], base, l0, f0))
        m0['kinds'].add(kind); m0['rows'].append((t['file'], t['line'], kind))
        if kind == 'withdrawn':
            m0['status'] = 'WITHDRAWN'
        if t['try_utc'] < m0['try_utc']:
            m0['try_utc'] = t['try_utc']
    tries = []
    for k in order:
        t = merged[k]; t.pop('kinds'); t.pop('_has_result', None); tries.append(t)
    # OUTSIDE A30-F02 (Rule 2): typed purpose / family / parent belong to ledger ask_ids, not to the legacy description text
    typed_path = src.get('types')
    if typed_path is None and isinstance(src.get('ledger'), str):
        adjacent = os.path.join(os.path.dirname(src['ledger']), 'TRIES_TYPES_V1.tsv')
        typed_path = adjacent if os.path.isfile(adjacent) else None
    if typed_path is not None:
        import csv
        with open(typed_path, encoding='utf-8') as stream:
            reader = csv.DictReader(stream, delimiter='\t')
            if reader.fieldnames not in (TYPED_COLS, TYPED_COLS + ['try_utc']):       # ledger_add_v6 writes the 5-column form
                raise ValueError('typed census schema differs: refused')
            typed = {}
            ledger = {t['ask_id']: t for t in tries if t['source'] == 'ledger'}
            for row in reader:
                key = row['ask_id']
                if key in typed or key not in ledger or row['type'] not in TYPED_TYPES or not (row['family'] or '').strip():
                    raise ValueError('duplicate, orphan or invalid typed census row: refused')
                typed[key] = row

        def lineage(key, seen):
            """-> (typed families of key and its typed ancestors, the untyped LEGACY ledger parent ending the chain or None)"""
            if key in seen or key not in typed:
                raise ValueError('cyclic or unresolved typed ancestry: refused')
            row = typed[key]; parent = row['parent_ask_id']
            if not parent:
                return [row['family']], None
            if parent not in typed:
                if parent in ledger:                                            # ledger_add_v6 accepts a legacy parent: its history is
                    return [row['family']], parent                             # inherited through its own name families (never erased)
                raise ValueError('cyclic or unresolved typed ancestry: refused')
            fams, legacy = lineage(parent, seen | {key})
            return [row['family']] + fams, legacy
        sha = ids.sha16_file(typed_path)
        for t in tries:
            if t['source'] == 'ledger' and t['ask_id'] in typed:
                fams, legacy = lineage(t['ask_id'], set())
                t['_typed_families'] = list(dict.fromkeys(fams)); t['_typed_type'] = typed[t['ask_id']]['type']; t['_typed_source_sha16'] = sha
                if legacy:
                    t['_typed_legacy_parent'] = (legacy, ledger[legacy].get('text', ''))
    return tries


TYPING_CUT = os.path.join(HERE, 'TYPING_CUT_V1.json')


def read_tries(sources=None):
    """the census rows (see _read_tries_unchecked) after OUTSIDE A36-F01 (STRATEGY-202600): an untyped ledger row is LEGACY only when the
    explicit migration record (sources['typing_cut'], default TYPING_CUT_V1.json) covers that ledger, its ledger stamp predates the record's
    cut, and the record's legacy set is exactly the untyped set found; anything else refuses (a missing record never makes a row legacy)"""
    src = dict(SOURCES) if sources is None else dict(sources)
    tries = _read_tries_unchecked(sources)
    untyped = [t for t in tries if t['source'] == 'ledger' and '_typed_families' not in t]
    if untyped:
        cut = typing_cut(src.get('typing_cut', TYPING_CUT))
        led = os.path.realpath(src['ledger']) if isinstance(src.get('ledger'), str) else None
        if cut is None or led != cut['ledger_path']:
            raise ValueError('untyped ledger rows %s and no migration record covers %s: refused (A36-F01)' % (','.join(t['ask_id'] for t in untyped[:5]), led))
        late = [t['ask_id'] for t in untyped if t['try_utc'] >= cut['cut_utc']]
        if late:
            raise ValueError('untyped ledger rows at or after the typing cut %s: %s: refused (A36-F01; register with ledger_add_v6 --type --family)' % (
                cut['cut_utc'], ','.join(late[:5])))
        found = sorted(t['ask_id'] for t in untyped)
        if len(found) != cut['legacy_ids'] or legacy_sha16(found) != cut['legacy_ids_sha16']:
            raise ValueError('the untyped rows before the cut (%d) are not the migration record\'s legacy set (%d): refused (A36-F01)' % (
                len(found), cut['legacy_ids']))
        for t in untyped:
            t['_legacy_by_cut'] = cut['sha16']
    return tries


def legacy_sha16(ask_ids):
    return hashlib.sha256('\n'.join(sorted(ask_ids)).encode('utf-8')).hexdigest()[:16]


def typing_cut(path):
    """the migration record (A36-F01) -> dict + ledger_path (real path) + sha16; None when no path or no file"""
    if not path or not os.path.exists(path):
        return None
    rec = json.load(open(path)); rec['ledger_path'] = os.path.realpath(os.path.join(FORENSICS, rec['ledger'])); rec['sha16'] = ids.sha16_file(path)
    utc_key(rec['cut_utc'], path)
    return rec


def make_typing_cut(ledger, out, cut_utc, recorded_by, why):
    """write the migration record ONCE (never over a file): every untyped base ask_id of the ledger stamped before cut_utc is legacy"""
    if os.path.exists(out):
        raise ValueError('%s exists: a migration record is written once (a new cut is a new version)' % out)
    utc_key(cut_utc, 'cut')
    base = sorted(t['ask_id'] for t in _read_tries_unchecked({'ledger': ledger}) if '_typed_families' not in t and t['try_utc'] < cut_utc)
    rec = dict(ledger=os.path.relpath(os.path.realpath(ledger), FORENSICS), cut_utc=cut_utc, legacy_ids=len(base), legacy_ids_sha16=legacy_sha16(base),
               recorded_by=recorded_by, why=why)
    with open(out + '.tmp', 'w') as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    os.replace(out + '.tmp', out); return rec


TYPED_COLS = ['ask_id', 'type', 'family', 'parent_ask_id']                        # = ledger_add_v6.TYPES_COLS[:4] (a test keeps them equal)
TYPED_TYPES = ('GROUPING', 'LABEL_SCHEME', 'UNIVERSE', 'SETTING_CHOICE', 'ALARM_TRUTH', 'STRATEGY_MONEY', 'CHART_READ', 'DESCRIBE_ONLY',
               'ABANDONED')                                                     # = ledger_add_v6.TYPES (a test keeps them equal)


def census(tries, fams, as_of_utc):
    """family x source counts of the tries stamped at or before as_of_utc; UNMAPPED tries are a family of their own AND listed; a WITHDRAWN
    try counts once (its source and ask_id once)"""
    counts = {}; unmapped = []; withdrawn = set(); last = ''
    for t in tries:
        if t['try_utc'] > as_of_utc:
            continue
        if t.get('status') == 'WITHDRAWN':
            k = (t['source'], t.get('ask_id'))
            if k in withdrawn:
                continue
            withdrawn.add(k)
        fam = t.get('family') or family_of(t.get('text', ''), t['source'], fams)
        counts.setdefault(fam, {}); counts[fam][t['source']] = counts[fam].get(t['source'], 0) + 1
        if fam == 'UNMAPPED':
            unmapped.append(t)
        last = max(last, t['try_utc'])
    return dict(counts=counts, unmapped=unmapped, census_as_of=last or None)


# ---------------------------------------------------------------- N_eff (README 1f)
def _nearest_psd_corr(C):
    w, V = np.linalg.eigh(C)
    fixed = float(-w[w < 0].sum())
    if fixed <= 0:
        return C, 0.0
    w = np.clip(w, 0, None); X = V @ np.diag(w) @ V.T
    d = np.sqrt(np.clip(np.diag(X), 1e-12, None)); X = X / np.outer(d, d)
    return X, fixed


def neff(per_wave, n_without=0, min_shared=11):
    """per_wave = {try_id: {wave_id: value}}; pairwise correlation on shared waves (fewer than min_shared: the pair is left out, counted,
    and taken as independent), nearest PSD when needed (logged in psd_fixed = the negative eigenvalue mass clipped);
    N_eff = (sum lambda)^2 / sum lambda^2 + n_without (tries with no per-wave receipt count 1 each)"""
    keys = sorted(per_wave, key=str); n = len(keys); left = 0
    if n == 0:
        return dict(n_eff=float(n_without), method='ALL_INDEPENDENT', pairs_left_out=0, psd_fixed=0.0)
    C = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = per_wave[keys[i]], per_wave[keys[j]]
            sh = sorted(set(a) & set(b), key=str)
            if len(sh) < min_shared:
                left += 1; continue
            x = np.array([a[w] for w in sh], float); y = np.array([b[w] for w in sh], float)
            if x.std() == 0 or y.std() == 0:
                left += 1; continue
            C[i, j] = C[j, i] = float(np.corrcoef(x, y)[0, 1])
    C, fixed = _nearest_psd_corr(C)
    lam = np.clip(np.linalg.eigvalsh(C), 0, None)
    ne = float(lam.sum() ** 2 / (lam ** 2).sum()) if (lam ** 2).sum() > 0 else float(n)
    return dict(n_eff=ne + n_without, method='EIGEN' if n >= 2 else 'ALL_INDEPENDENT', pairs_left_out=left, psd_fixed=fixed)


# ---------------------------------------------------------------- DSR, Holm, BH-Y, power
def sr_star(n_eff, V):
    """expected best per-wave Sharpe of n_eff null tries of variance V (Bailey and Lopez de Prado 2014, eq. for SR0)"""
    n = max(float(n_eff), 1.0)
    if n <= 1.0:
        return 0.0
    return math.sqrt(V) * ((1 - EULER) * stats.norm.ppf(1 - 1.0 / n) + EULER * stats.norm.ppf(1 - 1.0 / (n * math.e)))


def dsr(sr, T, skew, kurt_pearson, n_eff, V):
    """-> (sr_star, dsr_p): the probabilistic Sharpe of sr against sr_star over T periods (sr per period, kurtosis Pearson)"""
    s0 = sr_star(n_eff, V)
    den = 1.0 - skew * sr + (kurt_pearson - 1.0) / 4.0 * sr * sr
    den = math.sqrt(den) if den > 1e-12 else 1e-6
    return s0, float(stats.norm.cdf((sr - s0) * math.sqrt(max(T - 1, 0)) / den))


def holm(pvals):
    p = np.asarray(pvals, float); m = len(p); o = np.argsort(p, kind='mergesort')
    adj = np.minimum(1.0, np.maximum.accumulate((m - np.arange(m)) * p[o]))
    out = np.empty(m); out[o] = adj
    return list(out)


def bhy(pvals):
    p = np.asarray(pvals, float); m = len(p); o = np.argsort(p, kind='mergesort')
    c = float(np.sum(1.0 / np.arange(1, m + 1)))
    adj = np.minimum(1.0, np.minimum.accumulate((m * c / np.arange(1, m + 1) * p[o])[::-1])[::-1])
    out = np.empty(m); out[o] = adj
    return list(out)


def waves_needed(sr, n_eff, V, skew, kurt_pearson, target=0.95):
    """the fewest waves at this Sharpe that reach dsr_p >= target at this N_eff and V; None when sr <= 0 or never reachable"""
    if sr <= 0 or sr <= sr_star(n_eff, V):
        return None
    hi = 2
    while dsr(sr, hi, skew, kurt_pearson, n_eff, V)[1] < target:
        hi *= 2
        if hi > 10 ** 9:
            return None
    lo = max(hi // 2, 1)
    while lo < hi:
        mid = (lo + hi) // 2
        if dsr(sr, mid, skew, kurt_pearson, n_eff, V)[1] >= target:
            hi = mid
        else:
            lo = mid + 1
    return int(lo)


def _moments(v):
    T = len(v)
    if T < 4:
        return 0.0, 3.0
    m = v.mean(); d = v - m; s2 = (d ** 2).mean()
    if s2 <= 0:
        return 0.0, 3.0
    return float((d ** 3).mean() / s2 ** 1.5), float((d ** 4).mean() / s2 ** 2)


def evaluate(values, n_eff, V=None, family_pvals=None, settings=None, family='?', tries_counted=None, neff_method=''):
    """the result's per-wave values (wave order) -> README section 3 fields + 'line'; under min_waves the full line prints, UNRELIABLE"""
    s = dict(DEFAULT_SETTINGS, **(settings or {}))
    v = np.asarray(values, float); v = v[np.isfinite(v)]; T = len(v)
    sd = float(v.std(ddof=1)) if T > 1 else 0.0
    sr = float(v.mean() / sd) if sd > 0 else 0.0
    skew, kurt = _moments(v)
    V_used = '1/T' if V is None else 'given %.6g' % V
    Vx = (1.0 / T if T else 1.0) if V is None else float(V)
    s0, p_dsr = dsr(sr, T, skew, kurt, n_eff, Vx)
    t = sr * math.sqrt(T)
    p_raw = float(stats.t.sf(t, T - 1)) if T > 1 else 1.0
    ps = list(family_pvals or []) + [p_raw]
    hp = float(holm(ps)[-1])
    need = waves_needed(sr, n_eff, Vx, skew, kurt, s['dsr_bar'])
    block = float(np.corrcoef(v[:-1], v[1:])[0, 1]) if T >= 11 and v[:-1].std() > 0 and v[1:].std() > 0 else None
    if T < s['min_waves']:
        verdict = 'UNRELIABLE'
    else:
        verdict = 'PASS' if (p_dsr >= s['dsr_bar'] and t >= s['t_bar'] and hp < s['holm_alpha']) else 'FAIL'
    r = dict(family=family, tries_counted=tries_counted, tries_effective=float(n_eff), neff_method=neff_method, waves=T, sr_wave=sr,
             skew=skew, kurt_pearson=kurt, sr_star=float(s0), dsr_p=p_dsr, t_wave=t, p_raw=p_raw, holm_p=hp, waves_needed=need,
             block_check=block, verdict=verdict, reliability='UNRELIABLE' if T < s['min_waves'] else 'OK', V_used=V_used)
    r['line'] = ('FAIR BAR %s: tries %s (eff %.1f, %s), waves %d, SR/wave %.3f, SR* %.3f, DSR %.3f, t %.2f (bar %.1f), Holm %.4f, '
                 'needs %s waves, block %s, V %s, %s' % (family, tries_counted if tries_counted is not None else '-', float(n_eff),
                                                          neff_method or '-', T, sr, s0, p_dsr, t, s['t_bar'], hp,
                                                          need if need is not None else '-',
                                                          '%.2f' % block if block is not None else '-', V_used, verdict))
    return r


# ---------------------------------------------------------------- one result's bar
def read_waves(path, require_wave_sha=True):
    """the money tool's per-wave receipt (wave_id, value, month, day, n_fires) + '# wave_module_sha16=<sha16>' (README 2, LAB4 M1): a
    receipt without it, or naming another wave module than labcore's current one, is REFUSED"""
    sha = None; rows = []
    for i, l in enumerate(open(path, encoding='utf-8'), 1):
        if l.startswith('#'):
            m = re.search(r'wave_module_sha16=([0-9a-f]{16})', l)
            if m:
                sha = m.group(1)
            continue
        if l.strip():
            rows.append(l.rstrip('\n').split('\t'))
    head, body = rows[0], rows[1:]
    need = ('wave_id', 'value', 'month', 'day', 'n_fires')
    if [h for h in need if h not in head]:
        raise ValueError('%s: columns %s needed: refused' % (path, need))
    if require_wave_sha:
        cur = ids.sha16_file(WAVE_MODULE)
        if sha is None:
            raise ValueError('%s: no wave_module_sha16 line: the waves are not known to come from labcore.waves: refused (LAB4 M1)' % path)
        if sha != cur:
            raise ValueError('%s: waves made by wave module %s, labcore.waves is %s now: refused, recount with it (LAB4 M1)' % (path, sha, cur))
    ix = {h: head.index(h) for h in need}
    return [dict(wave_id=r[ix['wave_id']], value=float(r[ix['value']]), month=r[ix['month']], day=r[ix['day']],
                 n_fires=int(r[ix['n_fires']])) for r in body], sha


def bar(result_receipt_path, family, as_of_utc, tries, settings=None, per_wave=None, family_pvals=None, V=None):
    """evaluate() on the receipt with the family's census at as_of_utc. The JOIN GUARD: every try joined here must be stamped at or before
    as_of_utc, else ValueError (a later try never changes an old result's bar). per_wave = the tries' per-wave receipts {try_id: {wave:
    value}} where they exist; the others count 1 each (the conservative side)."""
    s = dict(DEFAULT_SETTINGS, **(settings or {}))
    fam_tries = [t for t in tries if (t.get('family') or family) == family]
    try:
        lookahead.join_guard(np.array([int(t['try_utc'][:8] + t['try_utc'][9:15]) for t in fam_tries], np.int64),
                             np.int64(int(as_of_utc[:8] + as_of_utc[9:15])), 'fairness_bar.bar tries joined to %s' % family)
    except lookahead.LookaheadError as e:
        raise ValueError(str(e))
    rows, sha = read_waves(result_receipt_path, require_wave_sha=s['require_wave_sha'])
    counted = len({(t['source'], t.get('ask_id')) if t.get('status') == 'WITHDRAWN' else (t['source'], t.get('ask_id'), id(t))
                   for t in fam_tries})
    pw = per_wave or {}
    ne = neff(pw, n_without=max(counted - len(pw), 0)) if (pw or counted) else dict(n_eff=1.0, method='ALL_INDEPENDENT')
    r = evaluate([x['value'] for x in rows], max(ne['n_eff'], 1.0), V=V, family_pvals=family_pvals, settings=s, family=family,
                 tries_counted=counted, neff_method=ne['method'])
    r.update(result_sha16=ids.sha16_file(result_receipt_path), wave_module_sha16=sha, as_of_utc=as_of_utc, known_at_utc=as_of_utc,
             census_as_of=max([t['try_utc'] for t in fam_tries] or [None], key=lambda x: x or ''),
             fires=sum(x['n_fires'] for x in rows), days=len({x['day'] for x in rows}))
    return r
