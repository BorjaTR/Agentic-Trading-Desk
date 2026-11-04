"""RESEARCH tools/bucket_proof (QUANT, 23 Oct 2026; TOOL_DESIGN_V3; reviewer SCOUT; LAB1 reviews before the scale run). Design note: README.md.
QUESTION: does a frozen bucket file tell the fire's four-class outcome apart better than no buckets, random buckets (whole waves moved within
the month, fires shuffled beside it), one-value splits cut on the fit months, and a small tree fitted on the fit months, month by month?
UNIT: one alarm fire (coin, t_alarm) of the subject that passes the filter. Every count is by WAVE: fires of any coin within wave_gap_s of the
previous one share a wave; a fire weighs 1 / (scored fires of its wave), so every wave counts once in total.
KNOWN AT: placement reads the stored EPI / CTX values of decision 0 (known at the alarm, so by fire + 6 s); the outcome reads STAMP decision 0
(fill at fire + 6 s) and only for the settings' outcome_months (refused otherwise: Feb-May stays closed until the fit settings are frozen).
BLOCKS (pure functions, each with a planted test): place, ewsd, outcome4, waves, info_gain, shares_boot, random_fire, random_wave, split_cuts /
split_labels, tree_labels, rank_stability, predictions. main() reads the stores, writes the per-fire values through lab3.write (part
BPROOF.<SUBJECT>.<settings name>) and the scores as a receipt named by the settings sha16 (LAB1 07:00:14Z).
  python3 -B bucket_proof.py describe <settings json> <out dir>      placement shares per month, no outcome read
  python3 -B bucket_proof.py score <settings json> <out dir> [--write] scores on the outcome months (+ the per-fire part with --write)
  python3 -B bucket_proof.py catalog                                  regenerate CATALOG_V1.tsv from the settings files"""
import glob, hashlib, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.join(HERE, '..')
TEAM = os.path.realpath(os.path.join(HERE, '..', '..', '..'))
CATALOG = os.path.join(HERE, 'CATALOG_V1.tsv')
CLASSES = ('RIDE_GOOD', 'FADE_GOOD', 'DEAD', 'BOTH_BAD')
FILL_WAIT_MAX_S = 60                                                         # = alarm_stamp MAX_WAIT_S (BED fill_v2's longest wait): the embargo horizon
EWSD = ('ENTER', 'WAIT', 'SKIP', 'DEAD', 'NA')
LEVELS = np.round(np.arange(1, 26) * 0.1, 1)
OPS = {'>=': np.greater_equal, '>': np.greater, '<=': np.less_equal, '<': np.less}
FIELDS = [('bucket', 'index of the bucket in the settings rules order (0 = the first rule)', 'index'),
          ('by_default', '1 = an earlier rule needed a missing input, so the fire passed to this bucket by default', 'flag'),
          ('ride', 'LABEL_EWSD_V1 class of the RIDE side (STAMP FOLLOW decision 0): 0 ENTER, 1 WAIT, 2 SKIP, 3 DEAD; empty NOT_OPENED / NA', 'class'),
          ('fade', 'LABEL_EWSD_V1 class of the FADE side (STAMP FADE decision 0): 0 ENTER, 1 WAIT, 2 SKIP, 3 DEAD; empty NOT_OPENED / NA', 'class'),
          ('outcome', 'four-class outcome (METHOD_BUCKETS_A02P_V1 s1): 0 RIDE_GOOD, 1 FADE_GOOD, 2 DEAD, 3 BOTH_BAD; empty NOT_OPENED / NA', 'class')]


def sha16_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def load_settings(path):
    s = json.load(open(path)); s['_sha16'] = sha16_file(path); s['_path'] = path
    return s


def month_last_day(m):
    y, mo = int(m[:4]), int(m[4:])
    nxt = (y + (mo == 12), 1 if mo == 12 else mo + 1)
    return '%04d%02d%02d' % (y, mo, (np.datetime64('%04d-%02d-01' % nxt) - np.timedelta64(1, 'D')).astype(object).day)


def check_window(s, law):
    """every settings month must be readable under lab3/law.py (its last day not refused); outcome, fit and judge months inside months"""
    for m in s['months']:
        why = law.research_refusal(month_last_day(m))
        if why:
            raise ValueError('month %s refused by lab3/law.py: %s' % (m, why))
    for k in ('outcome_months', 'fit_months', 'judge_months'):
        bad = [m for m in s[k] if m not in s['months']]
        if bad:
            raise ValueError('%s %s not in months' % (k, bad))


def ledger_rows(path):
    out = []
    for l in open(path):
        if l.startswith('#') or l.startswith('try_utc') or '\t' not in l:
            continue
        f = l.rstrip('\n').split('\t'); out.append(f)
    return out


# outcome_allowed: THE labcore gate (STRATEGY 13:14:41Z ruling; SKEPTIC REVIEW 02-04/05): law.py on every month, WINDOWS_V1 class (CHECK
# needs an older PREREG, BLIND refused), now_utc required, one look. The copy that stood here (= oracle 2b615f53) is retired.
sys.path.insert(0, TOOLS)
from labcore.gates import outcome_allowed  # noqa: E402


# ---------------------------------------------------------------- place
def cond_value(cond, X, derived):
    """-> (true, known) arrays for one condition; X: {input name: float array}"""
    if len(cond) == 1:
        a, op, k, b = derived[cond[0]]
        va, vb = np.asarray(X[a], float), np.asarray(X[b], float); kn = np.isfinite(va) & np.isfinite(vb)
        with np.errstate(invalid='ignore'):
            return OPS[op](va, k * vb) & kn, kn
    name, op, thr = cond[:3]; v = np.asarray(X[name], float); kn = np.isfinite(v)
    with np.errstate(invalid='ignore'):
        tr = OPS[op](v, thr) & kn
    if len(cond) > 3 and cond[3] == 'or_missing':
        return tr | ~kn, np.ones(len(v), bool)
    return tr, kn


def place(s, X):
    """exclusive, first rule that holds wins; a rule not known false but needing a missing input fails and the fire passes on, counted as
    placed by default -> (bucket index array, by_default bool array)"""
    n = len(next(iter(X.values()))); out = np.full(n, -1); dflt = np.zeros(n, bool); open_ = np.ones(n, bool); skipped = np.zeros(n, bool)
    for i, rule in enumerate(s['rules']):
        if 'any' in rule:                                                  # true if one condition is true; known false if all are known false
            t = np.zeros(n, bool); allf = np.ones(n, bool)
            for c in rule['any']:
                tr, kn = cond_value(c, X, s['derived']); t |= tr; allf &= kn & ~tr
            f = allf & ~t
        else:
            t = np.ones(n, bool); f = np.zeros(n, bool)
            for c in rule['all']:
                tr, kn = cond_value(c, X, s['derived']); f |= kn & ~tr; t &= tr
        hit = open_ & t; out[hit] = i; dflt[hit] = skipped[hit]; open_ &= ~hit
        skipped |= open_ & ~f & ~t
    if (out < 0).any():
        raise ValueError('%d fires in no bucket: the last rule must be the catch-all' % int((out < 0).sum()))
    return out, dflt


def rule_text(s, rule):
    """the rule in the bucket md's words (for the transcription test)"""
    conds = rule.get('all', rule.get('any', []))
    if not conds:
        return 'everything else'
    parts = []
    for c in conds:
        if len(c) == 1:
            parts.append(c[0].replace('_', '-'))
        elif len(c) > 3 and c[3] == 'or_missing':
            parts.append('(%s %s %s OR %s missing)' % (c[0], c[1], fmt(c[2]), c[0]))
        else:
            parts.append('%s %s %s' % (c[0], c[1], fmt(c[2])))
    return (' OR ' if 'any' in rule else ' AND ').join(parts)


def fmt(x):
    return ('%d' % x) if float(x).is_integer() else ('%g' % x)


# ---------------------------------------------------------------- outcome
def lvl_index(x):
    """the smallest stored level >= x (pct), capped at 2.5 -> index 0..24"""
    return np.minimum(np.searchsorted(LEVELS, np.minimum(np.asarray(x, float), 2.5) - 1e-9), 24)


def ewsd(OT, HT, filled, known_s, c, lab):
    """LABEL_EWSD_V1 per row. OT, HT: (n, 25) seconds from the fill to the first touch of offer / heat level 0.1 k pct (NaN = not reached);
    c: full cost pct per row. -> array of names (EWSD)"""
    OT = np.asarray(OT, float); HT = np.asarray(HT, float); n = len(OT); r = np.arange(n); hold = 60.0 * lab['hold_min']
    c = np.asarray(c, float); io = lvl_index(lab['offer_c'] * c); to = OT[r, io]; reached = np.isfinite(to) & (to <= hold)
    tlim = np.where(reached, to, -1.0)[:, None]
    before = np.isfinite(HT) & (HT <= tlim)                                   # heat touched at or before the offer (same second = before)
    hb = np.where(before.any(1), LEVELS[np.argmax(np.where(before, np.arange(25), -1), 1)], 0.0)
    inH = np.isfinite(HT) & (HT <= hold); hmax = np.where(inH.any(1), LEVELS[np.argmax(np.where(inH, np.arange(25), -1), 1)], 0.0)
    inO = np.isfinite(OT) & (OT <= hold); omax = np.where(inO.any(1), LEVELS[np.argmax(np.where(inO, np.arange(25), -1), 1)], 0.0)
    # every threshold, offer and heat alike, is the smallest stored level >= x c (LABEL_EWSD_V1 text; STRATEGY ruling 07:31:22Z)
    l_enter = LEVELS[lvl_index(lab['enter_heat_c'] * c)]; l_wait = LEVELS[lvl_index(lab['wait_heat_c'] * c)]; l_dead = LEVELS[lvl_index(lab['dead_c'] * c)]
    cls = np.where(reached, np.where(hb <= l_enter, 'ENTER', np.where(hb <= l_wait, 'WAIT', 'SKIP')),
                   np.where(np.asarray(known_s, float) < hold, 'NA',
                            np.where((hmax <= l_dead) & (omax <= l_dead), 'DEAD', 'SKIP')))
    return np.where(np.asarray(filled) == 1, cls, 'NA').astype(object)


def outcome4(ride, fade):
    """-> four-class outcome per fire (CLASSES) or 'NA' when a side is NA"""
    ride = np.asarray(ride, object); fade = np.asarray(fade, object)
    rg = np.isin(ride, ('ENTER', 'WAIT')); fg = np.isin(fade, ('ENTER', 'WAIT'))
    out = np.where(rg & ~fg, 'RIDE_GOOD', np.where(fg & ~rg, 'FADE_GOOD', np.where((ride == 'DEAD') & (fade == 'DEAD'), 'DEAD', 'BOTH_BAD')))
    return np.where((ride == 'NA') | (fade == 'NA'), 'NA', out).astype(object)


# ---------------------------------------------------------------- waves and scores
def waves(t, gap_s):
    """wave id per fire (in the input order): a fire more than gap_s after the previous fire (any coin) starts a new wave"""
    t = np.asarray(t, float); o = np.argsort(t, kind='mergesort'); ts = t[o]
    wid = np.cumsum(np.r_[1, np.diff(ts) > gap_s]) - 1; out = np.empty(len(t), int); out[o] = wid
    return out


def wave_weights(wave):
    """1 / (fires of the wave): every wave counts once in total"""
    u, inv, cnt = np.unique(wave, return_inverse=True, return_counts=True)
    return 1.0 / cnt[inv]


def entropy(p):
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def info_gain(lab, y, w):
    """H(Y) - sum_b W_b H(Y | b), weighted, bits"""
    lab = np.asarray(lab); y = np.asarray(y); w = np.asarray(w, float); W = w.sum()
    if W <= 0:
        return np.nan
    if lab.dtype.kind in 'iu' and y.dtype.kind in 'iu':                   # fast path (integer codes): one bincount
        nc = int(y.max()) + 1 if len(y) else 1; m = np.bincount(lab * nc + y, weights=w).reshape(-1, nc) if len(lab) else np.zeros((1, nc))
        rows = m.sum(1); py = m.sum(0) / W; h = entropy(py)
        for r in np.flatnonzero(rows > 0):
            h -= rows[r] / W * entropy(m[r] / rows[r])
        return h
    cl = np.unique(y); py = np.array([w[y == k].sum() for k in cl]) / W; h = entropy(py)
    for b in np.unique(lab):
        m = lab == b; wb = w[m].sum()
        if wb > 0:
            h -= wb / W * entropy(np.array([w[m & (y == k)].sum() for k in cl]) / wb)
    return h


def shares(lab, y, w, buckets, classes=CLASSES):
    """{bucket: (waves, {class: share})}"""
    out = {}
    for b in buckets:
        m = lab == b; wb = w[m].sum()
        out[b] = (wb, {k: (w[m & (y == k)].sum() / wb if wb > 0 else np.nan) for k in classes})
    return out


def shares_boot(lab, y, w, wave, buckets, rng, B, classes=CLASSES):
    """90 pct intervals of each bucket's class shares and of the info gain, resampling WHOLE waves jointly for all buckets"""
    u, inv = np.unique(wave, return_inverse=True); sh = {b: {k: [] for k in classes} for b in buckets}; ig = []
    for _ in range(B):
        cnt = np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u)); wb = w * cnt[inv]
        ig.append(info_gain(lab, y, wb))
        for b, (n_, d) in shares(lab, y, wb, buckets, classes).items():
            for k in classes:
                sh[b][k].append(d[k])
    q = lambda v: (float(np.nanpercentile(v, 5)), float(np.nanpercentile(v, 95))) if np.isfinite(v).any() else (np.nan, np.nan)
    return {b: {k: q(np.array(sh[b][k], float)) for k in classes} for b in buckets}, q(np.array(ig, float))


def random_fire(lab, month, rng):
    """labels shuffled across fires inside each month (exact bucket sizes per month kept)"""
    out = np.array(lab, copy=True)
    for m in np.unique(month):
        i = np.where(month == m)[0]; out[i] = out[rng.permutation(i)]
    return out


def wave_plan(wave, month, t, bins):
    """the label-free part of random_wave, computed once: per month and wave-size bin, each wave's fire indices in time order"""
    edges = list(bins) + [10 ** 9]; plan = []
    for m in np.unique(month):
        im = np.where(month == m)[0]; ws = {}
        for i in im[np.argsort(t[im], kind='mergesort')]:
            ws.setdefault(wave[i], []).append(i)
        ids = list(ws); size = np.array([len(ws[k]) for k in ids]); b_of = size   # C06-04: exact wave-size strata keep each month's bucket sizes
        for b in np.unique(b_of):
            grp = [np.array(ws[ids[j]]) for j in np.where(b_of == b)[0]]
            plan.append(grp)
    return plan


def random_wave(lab, wave, month, t, rng, bins, plan=None):
    """whole waves move: inside each month and wave-size bin, waves swap their bucket PATTERNS (the labels of their fires in time order);
    a pattern given to a wave of another size inside the bin is laid on its fires proportionally"""
    lab = np.asarray(lab); out = lab.copy()
    for grp in (plan if plan is not None else wave_plan(wave, month, t, bins)):
        perm = rng.permutation(len(grp))
        for rec, j in zip(grp, perm):
            p = lab[grp[j]]; k = len(p); mm = len(rec)
            out[rec] = p[(np.arange(mm) * k) // mm]
    return out


def split_cuts(x_fit, K):
    """quantile cut points of the finite fit values into at most K groups (ties merge groups)"""
    x = np.asarray(x_fit, float); x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.array([])
    return np.unique(np.quantile(x, np.arange(1, K) / K))


def split_labels(x, cuts):
    """group index per value; a missing value is its own group 'NA'"""
    x = np.asarray(x, float); g = np.searchsorted(cuts, x, side='right').astype(object)
    g[~np.isfinite(x)] = 'NA'
    return np.array(['Q%s' % v if v != 'NA' else 'NA' for v in g], object)


def tree_labels(X_fit, y_fit, w_fit, X_all, cfg, seed):
    """depth-limited tree fitted on the fit months only -> leaf label per fire of X_all (missing values go the learned way)"""
    from sklearn.tree import DecisionTreeClassifier
    frac = cfg['min_weight_leaf_waves'] / max(float(np.sum(w_fit)), 1e-9)
    t = DecisionTreeClassifier(max_depth=cfg['max_depth'], max_leaf_nodes=cfg['max_leaf_nodes'], min_weight_fraction_leaf=min(frac, 0.5),
                               random_state=seed).fit(X_fit, y_fit, sample_weight=w_fit)
    return np.array(['L%d' % v for v in t.apply(X_all)], object), t


def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float); ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 3:
        return np.nan
    ra = np.argsort(np.argsort(a[ok])).astype(float); rb = np.argsort(np.argsort(b[ok])).astype(float)
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def rank_stability(lab, y, w, month, months, cls):
    """mean Spearman correlation, over every pair of months, of the buckets' share of class cls (buckets with weight in both months)"""
    per = {}
    for m in months:
        i = month == m
        per[m] = {b: d[cls] for b, (wb, d) in shares(lab[i], y[i], w[i], np.unique(lab[i]), (cls,)).items() if wb > 0}
    rs = []
    for a in range(len(months)):
        for b in range(a + 1, len(months)):
            ka = per[months[a]]; kb = per[months[b]]; common = sorted(set(ka) & set(kb))
            rs.append(spearman([ka[k] for k in common], [kb[k] for k in common]))
    return float(np.nanmean(rs)) if np.isfinite(rs).any() else np.nan


PRED_RIDE_RANK = {'S1': 1, 'S4': 2, 'S0': 3.5, 'S3': 3.5, 'S6': 5.5, 'S2': 5.5, 'S5': 7}


def predictions(d, base=None):
    """SCOUT BUCKETS_A02P_V1's testable claims on one month's shares d = {bucket: (waves, {class: share})}; base = the month's own
    share of each class (all buckets together)"""
    sh = {b: v[1] for b, v in d.items() if v[0] > 0}
    common = [b for b in PRED_RIDE_RANK if b in sh]
    rho = spearman([-PRED_RIDE_RANK[b] for b in common], [sh[b]['RIDE_GOOD'] for b in common])
    fg = {b: sh[b]['FADE_GOOD'] for b in sh}
    c1b = ('S3' in fg) and fg['S3'] == min(fg.values())
    c2 = (('S1' in sh) and sh['S1']['RIDE_GOOD'] - sh['S1']['FADE_GOOD'] > 0, ('S2' in sh) and sh['S2']['RIDE_GOOD'] - sh['S2']['FADE_GOOD'] < 0)
    gap = {b: abs(sh[b]['RIDE_GOOD'] - sh[b]['FADE_GOOD']) for b in sh}
    c3 = ('S5' in gap) and gap['S5'] == min(gap.values())
    hi = {b: (b in sh and base is not None and sh[b]['FADE_GOOD'] > base['FADE_GOOD']) for b in ('S2', 'S6')}
    return dict(ride_rank_rho=rho, s3_lowest_fade=bool(c1b), s1_ride_side=bool(c2[0]), s2_fade_side=bool(c2[1]), s5_smallest_gap=bool(c3),
                s2_fade_above_base=bool(hi['S2']), s6_fade_above_base=bool(hi['S6']))


# ---------------------------------------------------------------- catalog and per-fire part
def code_name(subject, name, field):
    return 'BPROOF.%s.%s.%s' % (subject, name, field)


def part_name(subject, name):
    return 'BPROOF.%s.%s' % (subject, name)


def catalog_text(settings_paths=None):
    paths = sorted(settings_paths if settings_paths is not None else glob.glob(os.path.join(HERE, 'settings', '*.json')))
    lines = ['# BPROOF CATALOG_V1: generated by bucket_proof.py catalog from the settings files; METRICS_V1 columns + meaning, unit, level, block',
             'code\tstore\tclock\texact_k\tscope\tmeaning\tunit\tlevel\tblock']
    for p in paths:
        s = json.load(open(p))
        if 'rules' not in s:                                               # a money settings file writes no per-fire part
            continue
        for f, mean, unit in FIELDS:
            lines.append('\t'.join([code_name(s['subject'], s['name'], f), 'ROWS', 'event', '0', 'coin', mean, unit,
                                    'DESCRIPTION' if f in ('bucket', 'by_default') else 'OUTCOME', 'place' if f in ('bucket', 'by_default') else 'outcome']))
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------- reading the stores
def utc_month(t):
    return np.array([str(np.datetime64(int(x), 's'))[:7].replace('-', '') for x in t])


def utc_day(t):
    return np.array([str(np.datetime64(int(x), 's'))[:10].replace('-', '') for x in t])


def load_cost(s, coins):
    """full cost c per fire in pct = coin HL cost of record (cost table) + the gap; a coin not in the table takes the median (counted)"""
    cost = {}
    for l in open(os.path.join(os.path.dirname(TEAM), s['cost']['table'])):
        if l.startswith('#') or l.startswith('coin\t'):
            continue
        f = l.rstrip('\n').split('\t'); cost[f[0]] = float(f[4]) / 100.0
    cmed = float(np.median(list(cost.values())))
    return np.array([cost.get(x, cmed) for x in coins]) + s['cost']['gap_pct'], int(sum(1 for x in coins if x not in cost))


def read_cause(s, root, code, coins, ts, fields):
    """'CAUSE:<field>' inputs through T01's own reader (cause_label.read, one reader per store), joined on (coin, alarm second);
    a fire with no label row reads EMPTY (NaN / '')"""
    sys.path.insert(0, os.path.join(TOOLS, 'cause_label')); import cause_label as CL
    if not fields:
        return {}
    days = utc_day(ts); r = CL.read(root, code, s['subject'], s['cause_part'], min(days), max(days), list(fields))
    pos = {(c, int(t)): i for i, (c, t) in enumerate(zip(r['coin'], r['t']))}; j = np.array([pos.get((c, int(t)), -1) for c, t in zip(coins, ts)])
    out = {}
    for f in fields:
        word = r[f].dtype == object; v = r[f][np.maximum(j, 0)] if len(r[f]) else np.full(len(j), '' if word else np.nan, object if word else float)
        out['CAUSE:' + f] = np.where(j >= 0, v, '' if word else np.nan)
    return out


def read_inputs(s, root, code):
    """fires of the subject in the settings months that pass the filter, with every input / split value at decision 0;
    the fires the filter cannot judge (a filter value missing) are counted per month in s['_filter_missing']"""
    sys.path.insert(0, os.path.join(TOOLS, 'alarm_profile')); sys.path.insert(0, os.path.join(TOOLS, 'alarm_context'))
    import alarm_profile as AP, alarm_context as AC
    first = s['months'][0] + '01'; last = month_last_day(s['months'][-1])
    names = sorted(set(list(s['inputs'].values()) + s['rivals']['splits'] + [c['value'] for c in s.get('claims', [])]))
    epi_v = sorted({v.split(':')[1] for v in names if v.startswith('EPI:')} | {s['filter']['value'], s['filter']['ge_value']})
    ctx_v = sorted({v.split(':')[1] for v in names if v.startswith('CTX:')})
    E = AP.read(root, code, s['subject'], first, last, values=epi_v)
    C = AC.read(root, code, s['subject'], first, last, values=ctx_v)
    dec0 = np.abs(C['t_decision'] - C['t_alarm']) < 0.5                         # decision 0 only (known at the alarm)
    ck = {(c, int(round(t))): i for i, (c, t) in enumerate(zip(C['coin'], C['t_alarm'])) if dec0[i]}
    fv, gv = E[s['filter']['value']], E[s['filter']['ge_value']]; nanf = ~(np.isfinite(fv) & np.isfinite(gv))
    em = utc_month(np.round(E['t_alarm'])); s['_filter_missing'] = {m: int((nanf & (em == m)).sum()) for m in s['months']}
    with np.errstate(invalid='ignore'):
        keep = fv >= gv
    idx = np.where(keep)[0]; ci = np.array([ck.get((E['coin'][i], int(round(E['t_alarm'][i]))), -1) for i in idx])
    F = {'coin': E['coin'][idx], 't': np.round(E['t_alarm'][idx]).astype(np.int64), 'ctx_found': ci >= 0}
    for v in names:
        src, nm = v.split(':')
        if src in ('COST', 'CAUSE'):
            continue
        F[v] = E[nm][idx] if src == 'EPI' else np.where(ci >= 0, C[nm][np.maximum(ci, 0)], np.nan)
    F['COST:c'], s['_cost_fallback'] = load_cost(s, F['coin'])
    F.update(read_cause(s, root, code, F['coin'], F['t'], sorted({v.split(':', 1)[1] for v in names if v.startswith('CAUSE:')})))
    F['month'] = utc_month(F['t']); F['day'] = utc_day(F['t'])
    o = np.lexsort((F['coin'], F['t']))
    return {k: v[o] for k, v in F.items()}


def check_authorized(s):
    """OUTSIDE S02 rule 4 (SCOUT-133139): the scorer checks authorization BEFORE touching any outcome: the settings' status must be
    SCORING (T06 make_settings writes DRAFT_UNPROVEN while a needed cause is unproven) and evidence_manifest must equal the sha16 of the
    proof table the settings name in evidence_path (relative to the forensics folder); anything else is refused (PermissionError)"""
    if s.get('status') != 'SCORING':
        raise PermissionError('settings %s: status %r, not SCORING: no outcome is read (S02 rule 4)' % (s.get('_path'), s.get('status')))
    ev, man = s.get('evidence_path'), s.get('evidence_manifest')
    if not ev or not man:
        raise PermissionError('settings %s: evidence_path and evidence_manifest are both required to score (S02 rule 4)' % s.get('_path'))
    p = os.path.join(os.path.dirname(TEAM), ev)
    if not os.path.exists(p) or sha16_file(p) != man:
        raise PermissionError('settings %s: evidence %s is %s, the settings name %s: refused (S02 rule 4)' % (
            s.get('_path'), ev, sha16_file(p) if os.path.exists(p) else 'missing', man))
    return True


def read_outcome(s, F, root, code, cache=None, wins=None):
    """EWSD per side and the four-class outcome, for the fires of the opened outcome months only. s['label']['version'] LABEL_EWSD_V2
    (QUANT 13:59:25Z): label_ewsd_v2.ewsd_v2 + outcome4_v2, each filled path's coverage read from the lab PRICE bins from its FILL time
    (t_decision + delay_s + fill_wait_s, alarm_stamp's rule) through labcore PriceCache (lab root: s['lab_root'], else BPROOF_LAB, else
    lab_days); any other label keeps V1 (ewsd + outcome4) for its receipts.
    EMBARGO (STRATEGY RULING 14:11:07Z on QUANT's MUST, CHECK_WINDOW_RULE_V3 item 8): a fire whose outcome horizon (t + hold + delay_s +
    the 60 s fill wait; 4 h + 66 s) ends in another window of WINDOWS_V1 than it starts in reads that window's prices: both sides and the
    outcome are EMBARGO, never scored, counted in the receipt (any label version)"""
    import datetime
    check_authorized(s)                                                     # S02 rule 4: before any outcome
    outcome_allowed(s, sorted(set(F['month'][np.isin(F['month'], s['outcome_months'])])), os.path.join(TEAM, 'RESEARCH', 'TRIES_LEDGER_V1.tsv'),
                    datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    sys.path.insert(0, os.path.join(TOOLS, 'alarm_stamp')); import alarm_stamp as ST
    ms = s['outcome_months']; c = F['COST:c']
    v2 = s['label'].get('version') == 'LABEL_EWSD_V2'
    if v2:
        import label_ewsd_v2 as LV2
        LV2.check_settings(s['label'])
        if cache is None:
            from labcore.prices import PriceCache
            cache = PriceCache(s.get('lab_root') or os.environ.get('BPROOF_LAB', '<DATA_ROOT>/lab_days'))
    res = {}
    for side, d in (('ride', 'FOLLOW'), ('fade', 'FADE')):
        parts = [ST.read(root, code, s['subject'], d, m + '01', month_last_day(m)) for m in ms]     # month by month: no closed month read
        x = {k: np.concatenate([p_[k] for p_ in parts]) for k in parts[0]}; dec0 = np.abs(x['t_decision'] - x['t_alarm']) < 0.5
        key = {(cn, int(round(t))): i for i, (cn, t) in enumerate(zip(x['coin'], x['t_alarm'])) if dec0[i]}
        j = np.array([key.get((cn, int(t)), -1) for cn, t in zip(F['coin'], F['t'])]); ok = j >= 0; jj = np.maximum(j, 0)
        OT = np.stack([x['ot_%02d' % k][jj] for k in range(1, 26)], 1); HT = np.stack([x['ht_%02d' % k][jj] for k in range(1, 26)], 1)
        filled = np.where(ok, x['filled'][jj], 0)
        if v2:
            lab = s['label']; hold = 60.0 * float(lab['hold_min']); gap = np.full(len(filled), np.nan)
            t_fill = x['t_decision'][jj] + float(lab['delay_s']) + x['fill_wait_s'][jj]
            for i in np.flatnonzero(filled == 1):
                gap[i] = LV2.path_first_gap(cache, F['coin'][i], float(t_fill[i]), hold, float(lab['gap_s']))
            known = np.where(filled == 1, x['known_s'][jj], 0.0)            # QUANT 14:47:21Z: an unfilled stamp's EMPTY length never refuses the batch
            cls = LV2.ewsd_v2(OT, HT, filled, known, c, lab, gap)[0]
        else:
            cls = ewsd(OT, HT, filled, x['known_s'][jj], c, s['label'])
        opened = np.isin(F['month'], ms)
        res[side] = np.where(opened, cls, 'NOT_OPENED').astype(object)
    out = (LV2.outcome4_v2 if v2 else outcome4)(res['ride'], res['fade']); out = np.where(np.isin(F['month'], ms), out, 'NOT_OPENED').astype(object)
    from labcore.gates import windows
    wins = wins or windows(); pad = 60.0 * float(s['label']['hold_min']) + float(s['label'].get('delay_s', 6)) + FILL_WAIT_MAX_S
    win = lambda d: [w for w, lo, hi in wins if lo <= d and (hi is None or d <= hi)]
    t_ = np.asarray(F['t'], float)
    emb = np.array([win(a) != win(b) for a, b in zip(utc_day(t_), utc_day(t_ + pad))], bool) & np.isin(F['month'], ms)
    for k in ('ride', 'fade'):
        res[k] = np.where(emb, 'EMBARGO', res[k]).astype(object)
    out = np.where(emb, 'EMBARGO', out).astype(object)
    return res['ride'], res['fade'], out, s.get('_cost_fallback', 0)


# ---------------------------------------------------------------- the run
def score_run(s, F, y, write_lines):
    """all scores on fires with an outcome (not NA, not NOT_OPENED, not crash days); -> receipt lines"""
    rng = np.random.default_rng(s['seed']); K = len(s['rules']); names = [r['bucket'] for r in s['rules']]
    X = {k: F[v] for k, v in s['inputs'].items()}; b, dflt = place(s, X); lab = np.array([names[i] for i in b], object)
    wave_all = waves(F['t'], s['wave_gap_s'])
    use = np.isin(y, CLASSES) & ~np.isin(F['day'], s['crash_days'])
    if s.get('subset'):                                                    # score only where a gate holds (T06: SIDE groups behind G)
        tr = np.ones(len(b), bool)
        for c in s['subset']:
            t_, k_ = cond_value(c, X, s['derived']); tr &= t_ & k_
        use &= tr
    view = s.get('outcome_view', 'FOUR_CLASS'); cls = CLASSES
    if view == 'SIDE':                                                     # which side, not how big: only fires where exactly one side is good
        use &= np.isin(y, ('RIDE_GOOD', 'FADE_GOOD'))
    elif view == 'ROOM':                                                   # is there room: one side good vs DEAD or BOTH_BAD (STRATEGY 09:39:35Z)
        y = np.where(np.isin(y, ('RIDE_GOOD', 'FADE_GOOD')), 'ROOM', np.where(np.isin(y, CLASSES), 'NO_ROOM', y)).astype(object); cls = ('ROOM', 'NO_ROOM')
    L = lab[use]; Y = y[use]; M = F['month'][use]; WV = wave_all[use]; T = F['t'][use].astype(float); W = wave_weights(WV)
    months = [m for m in s['outcome_months'] if (M == m).any()]
    out = ['SETTINGS %s sha16 %s | view %s | fires scored %d (outcome known, crash days %s out) | waves %d' % (s['name'], s['_sha16'],
           s.get('outcome_view', 'FOUR_CLASS'), int(use.sum()), ','.join(s['crash_days']), len(np.unique(WV)))]
    # the scheme and its rivals
    schemes = {'BUCKETS': L, 'NONE': np.array(['ALL'] * len(L), object)}
    fit = np.isin(M, s['fit_months'])
    for v in s['rivals']['splits']:
        cuts = split_cuts(F[v][use][fit], K); schemes['SPLIT_' + v] = split_labels(F[v][use], cuts)
    Xs = np.column_stack([F[v][use] for v in s['rivals']['splits']])
    if fit.sum() > 0:
        schemes['TREE'], _ = tree_labels(Xs[fit], Y[fit], W[fit], Xs, s['rivals']['tree'], s['seed'])
    # luck bars per month and pooled over the opened months (integer codes and one wave plan: same draws, faster)
    ig_rw = {m: [] for m in months + ['POOLED']}; ig_rf = {m: [] for m in months + ['POOLED']}
    Lc = np.unique(L, return_inverse=True)[1].astype(np.int64); Yc = np.unique(Y, return_inverse=True)[1].astype(np.int64)
    plan = wave_plan(WV, M, T, s['rivals']['wave_size_bins'])
    out.append('WAVE STRATA: %d strata (month x exact wave size), %d with a single wave (it draws itself every time, QUANT 14:28:50Z)' % (
        len(plan), sum(len(g) == 1 for g in plan)))
    L_obj, Y_obj = L, Y; L, Y = Lc, Yc
    for _ in range(s['rivals']['random_wave_draws']):
        r = random_wave(L, WV, M, T, rng, s['rivals']['wave_size_bins'], plan)
        for m in months:
            i = M == m; ig_rw[m].append(info_gain(r[i], Y[i], W[i]))
        ig_rw['POOLED'].append(info_gain(r, Y, W))
    for _ in range(s['rivals']['random_fire_draws']):
        r = random_fire(L, M, rng)
        for m in months:
            i = M == m; ig_rf[m].append(info_gain(r[i], Y[i], W[i]))
        ig_rf['POOLED'].append(info_gain(r, Y, W))
    L, Y = L_obj, Y_obj
    out.append('INFO GAIN (bits, by wave) per scheme: month columns %s + POOLED; luck bars = 95th pct of 1000 random draws' % ' '.join(months))
    out.append('scheme\t' + '\t'.join(months + ['POOLED']))
    for nm, sc in schemes.items():
        out.append(nm + '\t' + '\t'.join('%.4f' % info_gain(sc[M == m], Y[M == m], W[M == m]) for m in months) + '\t%.4f' % info_gain(sc, Y, W))
    out.append('LUCK_WAVE_95\t' + '\t'.join('%.4f' % np.percentile(ig_rw[m], 95) for m in months + ['POOLED']))
    out.append('LUCK_FIRE_95\t' + '\t'.join('%.4f' % np.percentile(ig_rf[m], 95) for m in months + ['POOLED']))
    out.append('BUCKETS_P_WAVE\t' + '\t'.join('%.3f' % np.mean(np.array(ig_rw[m]) >= info_gain(L[M == m] if m != 'POOLED' else L, Y[M == m] if m != 'POOLED' else Y,
                                                                                             W[M == m] if m != 'POOLED' else W)) for m in months + ['POOLED']))
    # by regime (QUANT REGIME_V1 tags in the settings): the opened months of each regime pooled, beside a 200-draw whole-wave bar
    reg = s.get('regimes', {})
    for g in sorted(set(reg[m] for m in months if m in reg)):
        rm = [m for m in months if reg.get(m) == g]; i = np.isin(M, rm)
        Li = np.unique(L[i], return_inverse=True)[1].astype(np.int64); Yi = np.unique(Y[i], return_inverse=True)[1].astype(np.int64)
        pl = wave_plan(WV[i], M[i], T[i], s['rivals']['wave_size_bins'])
        bars = [info_gain(random_wave(Li, WV[i], M[i], T[i], rng, s['rivals']['wave_size_bins'], pl), Yi, W[i]) for _ in range(200)]
        out.append('REGIME %s (%s): BUCKETS IG %.4f | LUCK_WAVE_95 %.4f | TREE %s | waves %.0f' % (g, ' '.join(rm), info_gain(L[i], Y[i], W[i]),
                   np.percentile(bars, 95), ('%.4f' % info_gain(schemes['TREE'][i], Y[i], W[i])) if 'TREE' in schemes else '-', W[i].sum()))
    # per bucket shares with joint whole-wave intervals, per month and pooled
    out.append('SHARES by wave (90 pct interval, whole waves resampled jointly); THIN = interval width over %.2f' % s['thin_width'])
    out.append('month\tbucket\twaves\tfires\t' + '\t'.join(cls) + '\tTHIN')
    for m in months + ['POOLED']:
        i = (M == m) if m != 'POOLED' else np.ones(len(M), bool)
        d = shares(L[i], Y[i], W[i], names, cls); ci, _ = shares_boot(L[i], Y[i], W[i], WV[i], names, rng, s['rivals']['bootstrap'], cls)
        for bk in names:
            wb, sh = d[bk]; nf = int((L[i] == bk).sum())
            thin = any((ci[bk][k][1] - ci[bk][k][0]) > s['thin_width'] for k in cls if np.isfinite(ci[bk][k][0]))
            out.append('%s\t%s\t%.1f\t%d\t' % (m, bk, wb, nf) + '\t'.join('%.3f [%.3f %.3f]' % (sh[k], ci[bk][k][0], ci[bk][k][1]) for k in cls)
                       + '\t%s' % ('THIN' if thin or nf == 0 else ''))
        if m != 'POOLED' and s.get('predictions') == 'BUCKETS_A02P_V1' and view != 'ROOM':
            base = shares(np.array(['ALL'] * int(i.sum()), object), Y[i], W[i], ['ALL'])['ALL'][1]; p = predictions(d, base)
            out.append('PREDICTIONS %s: ride rank rho %.2f | S3 lowest FADE_GOOD %s | S1 RIDE side %s | S2 FADE side %s | S5 smallest gap %s | '
                       'S2 FADE above base %s | S6 FADE above base %s' % (m, p['ride_rank_rho'], p['s3_lowest_fade'], p['s1_ride_side'],
                                                                         p['s2_fade_side'], p['s5_smallest_gap'], p['s2_fade_above_base'], p['s6_fade_above_base']))
    # stability of every scheme over the opened months
    if set(months) <= set(s['fit_months']):
        out.append('NOTE in-sample: the SPLIT cuts and the TREE above are fitted AND scored on the same months (optimistic for them); the fair '
                   'in-sample comparison is the WALK-FORWARD block below (SCOUT SHOULD 3)')
    out += walk_forward(s, F, use, L, Y, M, W, WV, T, months, K, rng)
    out.append('STABILITY (mean Spearman of bucket shares over every pair of opened months): scheme\t%s\t%s' % cls[:2])
    for nm, sc in schemes.items():
        if nm != 'NONE':
            out.append('%s\t%.3f\t%.3f' % (nm, rank_stability(sc, Y, W, M, months, cls[0]), rank_stability(sc, Y, W, M, months, cls[1])))
    out += claims_block(s, F, lab, use, Y, M, WV, rng)
    write_lines(out)
    return out


def walk_forward(s, F, use, L, Y, M, W, WV, T, months, K, rng):
    """inside the opened months: each month from the third on is scored by SPLIT cuts and a TREE fitted on the earlier opened fit months
    only (expanding window), beside the fixed buckets and that month's whole-wave luck bar (200 draws)"""
    out = ['WALK-FORWARD (fit on the earlier opened fit months, score the month): month\tfit\tBUCKETS\tLUCK_WAVE_95\tTREE\tbest SPLIT (of %d)\tits IG'
           % len(s['rivals']['splits'])]
    Xs = np.column_stack([F[v][use] for v in s['rivals']['splits']])
    for m in months:
        prior = [x for x in months if x < m and x in s['fit_months']]
        if len(prior) < 2:
            continue
        fi = np.isin(M, prior); sc = M == m
        Ls = np.unique(L[sc], return_inverse=True)[1].astype(np.int64); Ys = np.unique(Y[sc], return_inverse=True)[1].astype(np.int64)
        pl = wave_plan(WV[sc], M[sc], T[sc], s['rivals']['wave_size_bins'])
        bars = [info_gain(random_wave(Ls, WV[sc], M[sc], T[sc], rng, s['rivals']['wave_size_bins'], pl), Ys, W[sc]) for _ in range(200)]
        tl, _ = tree_labels(Xs[fi], Y[fi], W[fi], Xs[sc], s['rivals']['tree'], s['seed'])
        best = max(((info_gain(split_labels(F[v][use][sc], split_cuts(F[v][use][fi], K)), Y[sc], W[sc]), v) for v in s['rivals']['splits']),
                   key=lambda z: (np.nan_to_num(z[0], nan=-1), z[1]))
        out.append('%s\t%s..%s\t%.4f\t%.4f\t%.4f\t%s\t%.4f' % (m, prior[0], prior[-1], info_gain(L[sc], Y[sc], W[sc]), np.percentile(bars, 95),
                                                        info_gain(tl, Y[sc], W[sc]), best[1], best[0]))
    return out


def claims_block(s, F, lab, use, Y, M, WV, rng):
    """declared claims inside groups (SCOUT CLAIM_*): share of the claim's class in SPLIT A vs B by wave, per window, the difference with
    its 90 pct whole-wave interval (A and B resampled jointly); fires with the reading missing are counted, not judged"""
    out = []
    for c in s.get('claims', []):
        g = np.isin(lab, c['groups']); x = np.asarray(F[c['value']], float)
        if c['split']['kind'] == 'eq0':
            A = x == 0; cut = 0.0
        else:
            cm = g & np.isin(F['month'], c['split']['cut_months']) & np.isfinite(x)
            cut = float(np.quantile(x[cm], 1 - c['split']['frac'])) if cm.any() else np.nan; A = x >= cut
        miss = g & ~np.isfinite(x)
        out.append('CLAIM %s (ledger %s): groups %s, A = %s %s (cut %.4g), class %s; missing reading %d fires' % (
            c['name'], c['ledger'], '+'.join(c['groups']), c['value'], c['split']['kind'], cut, c['cls'], int(miss.sum())))
        for wn, wm in c['windows'].items():
            sel = (g & np.isfinite(x))[use] & np.isin(M, wm)
            if not sel.any():
                out.append('  %s %s: no fires' % (wn, '+'.join(wm))); continue
            a = A[use][sel]; yy = Y[sel] == c['cls']; wv = WV[sel]; w = wave_weights(wv)
            def diff(ww):
                pa = (ww[a] * yy[a]).sum() / ww[a].sum() if ww[a].sum() > 0 else np.nan
                pb = (ww[~a] * yy[~a]).sum() / ww[~a].sum() if ww[~a].sum() > 0 else np.nan
                return pa, pb
            pa, pb = diff(w); u, inv = np.unique(wv, return_inverse=True); bs = []
            for _ in range(s['rivals']['bootstrap']):
                cnt = np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u)); q = diff(w * cnt[inv]); bs.append(q[0] - q[1])
            lo, hi = np.nanpercentile(bs, 5), np.nanpercentile(bs, 95)
            out.append('  %s %s: A %d fires %.1f waves share %.3f | B %d fires %.1f waves share %.3f | A-B %+.3f [%+.3f %+.3f]' % (
                wn, '+'.join(wm), int(a.sum()), w[a].sum(), pa, int((~a).sum()), w[~a].sum(), pb, pa - pb, lo, hi))
    return out


def describe_lines(s, F):
    """placement shares and placed-by-default counts per month: no outcome read"""
    names = [r['bucket'] for r in s['rules']]; X = {k: F[v] for k, v in s['inputs'].items()}; b, dflt = place(s, X)
    wv = waves(F['t'], s['wave_gap_s']); out = ['DESCRIBE %s sha16 %s: fires %d, ctx found %d' % (s['name'], s['_sha16'], len(b), int(F['ctx_found'].sum())),
                                                'month\tfires\twaves\t' + '\t'.join('%s share|by_default' % n for n in names)]
    for m in s['months']:
        i = F['month'] == m; n = int(i.sum())
        out.append('%s\t%d\t%d\t' % (m, n, len(np.unique(wv[i]))) + '\t'.join('%.3f|%d' % ((b[i] == k).mean() if n else np.nan, int((dflt[i] & (b[i] == k)).sum()))
                                                                         for k in range(len(names))))
    miss = {k: [float(np.mean(~np.isfinite(F[v][F['month'] == m]))) for m in s['months']] for k, v in s['inputs'].items()}
    out.append('missing share per input per month: ' + ' | '.join('%s %s' % (k, ' '.join('%.2f' % x for x in v)) for k, v in miss.items()))
    out.append('filter not judged (a filter value missing) per month: ' + ' '.join('%s %d' % kv for kv in s.get('_filter_missing', {}).items()))
    return out


def write_part(s, F, b, dflt, ride, fade, y, root, code):
    """per-fire values through lab3.write, one part per day: BPROOF.<SUBJECT>.<name>"""
    sys.path.insert(0, code); from lab3 import write as LW
    if open(CATALOG).read() != catalog_text():
        raise ValueError('CATALOG_V1.tsv differs from the settings files: run "bucket_proof.py catalog" first')
    cat = LW.load_catalog(CATALOG); part = part_name(s['subject'], s['name']); idx = {k: i for i, k in enumerate(EWSD[:4])}
    cidx = {k: i for i, k in enumerate(CLASSES)}; seal = json.dumps({k: v for k, v in s.items() if not k.startswith('_')}, sort_keys=True)
    done = 0
    for day in sorted(set(F['day'])):
        sel = np.where(F['day'] == day)[0]; coins = sorted(set(F['coin'][sel])); codes = {}
        vals = {'bucket': (b, None), 'by_default': (dflt.astype(int), None), 'ride': (ride, idx), 'fade': (fade, idx), 'outcome': (y, cidx)}
        for f, (arr, mp) in vals.items():
            rows = {}
            for c in coins:
                col = {k: [] for k in ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')}
                for i in sel[F['coin'][sel] == c]:
                    v = arr[i]; ok = True
                    if mp is not None:
                        ok = v in mp; reason = '' if ok else str(v); v = mp.get(v, np.nan)
                    col['day'].append(int(day)); col['as_of_us'].append(int(F['t'][i]) * 1000000); col['known_at_us'].append((int(F['t'][i]) + 6) * 1000000)
                    col['value_kind'].append(1); col['value_bits'].append(int(np.array([float(v)], '<f8').view('<u8')[0]) if ok else None)
                    col['value_txt'].append(None); col['empty_reason'].append('' if ok else reason); col['stale'].append(0)
                rows[c] = col
            codes[code_name(s['subject'], s['name'], f)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rows}
        LW.write_part(root, int(day), part, codes, coins, catalog=cat, sources={'settings:%s' % os.path.basename(s['_path']): s['_sha16'],
                      'code:bucket_proof.py': sha16_file(__file__)}, seal=seal)
        done += 1
    return done


def write_whole(path, text):
    if os.path.exists(path):
        raise FileExistsError(path)
    with open(path + '.tmp', 'w') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(path + '.tmp', path)


def main(a):
    if a and a[0] == 'catalog':
        t = catalog_text(); write_tmp = CATALOG + '.tmp'; open(write_tmp, 'w').write(t); os.replace(write_tmp, CATALOG); print('CATALOG', sha16_file(CATALOG)); return
    mode, sp, out_dir = a[0], a[1], a[2]
    root = os.environ.get('BPROOF_ROOT', '<DATA_ROOT>/research_days'); code = os.path.join(TEAM, 'LAB3', 'code')
    sys.path.insert(0, code); from lab3 import law
    s = load_settings(sp); check_window(s, law); os.makedirs(out_dir, exist_ok=True)
    print('bucket_proof %s settings %s %s | code %s' % (mode, s['name'], s['_sha16'], sha16_file(__file__)), flush=True)
    F = read_inputs(s, root, code)
    if mode == 'describe':
        txt = '\n'.join(describe_lines(s, F)) + '\n'; write_whole(os.path.join(out_dir, 'DESCRIBE_%s_%s.txt' % (s['name'], s['_sha16'])), txt); print(txt); return
    ride, fade, y, nfall = read_outcome(s, F, root, code)
    lines = describe_lines(s, F) + ['cost fallback (coin not in the cost table, median used): %d fires' % nfall]
    lines += ['outcome counts (all opened fires incl. crash days): ' + ' '.join('%s %d' % (k, int((y == k).sum())) for k in CLASSES + ('NA', 'UNDECIDED', 'EMBARGO', 'NOT_OPENED'))]
    score_run(s, F, y, lines.extend)
    p = os.path.join(out_dir, 'SCORES_%s_%s.txt' % (s['name'], s['_sha16'])); write_whole(p, '\n'.join(lines) + '\n')
    print('\n'.join(lines)); print('WROTE', p, sha16_file(p))
    if '--write' in a:
        names = [r['bucket'] for r in s['rules']]; b, dflt = place(s, {k: F[v] for k, v in s['inputs'].items()})
        print('PART days written', write_part(s, F, b, dflt, ride, fade, y, root, code))


if __name__ == '__main__':
    main(sys.argv[1:])
