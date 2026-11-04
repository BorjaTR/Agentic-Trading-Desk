#!/usr/bin/env python3
"""true_gate_v1.py (SCOUT, 2 Nov 2026; TEST, NOT REVIEWED; print-only) (released edition: made by make_true_gate_home_v1.py from the playground; only paths and pins differ). A library of true_gate_v3.py: run that one.
Is the claim of an alarm true on a stored no-price metric, against equally busy moments? Reuses by import, from the release:
 alarm_design_v3 (LabSource, boot_ci, flip_p, label_values for its own kinds), fl_read_v11 (match7, stats7, load_bz, pre_fire_mask),
 labcore.waves. Nothing here computes busy-ness, bands or waves on its own.

  python3 -B true_gate_v1.py run <claim.json> <out dir (new)>     exit 0 printed a verdict, 2 refused
  python3 -B true_gate_v1.py check <claim.json>                   refusal check only; reads no data

THE LABEL (kind metric_test), on the code's own lab clock (column k holds the value known at D0 + k x step):
  code | code_by_side {"1": .., "-1": ..}   the stored metric; code_by_side picks by side (with dir same/opposite)
  when: window (t + start_s, t + end_s] | present (t - end_s, t]
  agg: sum | mean | max | min | last        for >= and <=; a row counts only when its whole step lies inside the interval
  test: >= | <= | falling | rising          falling/rising read the level as of each end of the interval: end - start
  change: abs | pct                         falling/rising only
  thr | thr_code {code, scale} | thr_input  fixed; or read as of t (known_at <= t) from a code; or (engine only) an input of the definition
  sign: none | same | opposite              the value times the alarm's side, or minus it
  max_age_s: required.                      A value older than this, missing, with a reason, or known after t in a present label is
                                            NOT KNOWN (NaN), never false. One such row in a sum/mean/max/min interval makes the label NOT KNOWN.
VERDICT, frozen: TRUE if gap >= +0.05 and interval above 0; NOT SUPPORTED if the interval's top is under +0.05; else UNSURE.
The luck line (flip p) is printed for information, uncalibrated, and never enters the verdict."""
import csv, datetime, hashlib, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
REL = os.environ.get('TG_REL') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))   # the Alarm folder: <Alarm>/03_Grading/tree/tools/true_gate; TG_REL only for a mutant copy
sys.path.insert(0, os.path.join(REL, '06_First_look/tree/tools/alarm_first_look'))
sys.path.insert(0, os.path.join(REL, '01_Detection/tree/team/RESEARCH/tools/alarm_design'))
import fl_read_v11 as FL                                      # noqa: E402
import alarm_design_v3 as AD                                  # noqa: E402
from labcore import waves as WV                               # noqa: E402

VERSION = 'true_gate_v1'
MIN_EFFECT = 0.05
WAVE_S = 1800
NAN = float('nan')
FAMILIES = os.path.join(HERE, 'SOURCE_FAMILIES_V1.tsv')
TESTS = ('>=', '<=', 'falling', 'rising')
AGGS = ('sum', 'mean', 'max', 'min', 'last')
CRASH_DAYS = ('20251010', '20251011')
# opinion printed on the card, never a refusal: closing a position through a liquidation lowers open interest by itself
MECHANICAL = {('LIQ_BN', 'OI_BN'): 'Binance liquidations close positions, so they lower Binance open interest by themselves: part of this label is the trigger\'s own flow'}
# every op of alarm_design_v3's registry; a definition with another op cannot be read, so it is refused
KNOWN_OPS = {'raw', 'market', 'price', 'sum', 'max', 'prior_max', 'prior_min', 'known', 'pospart', 'negpart', 'change', 'lag', 'ratio', 'mul', 'add',
             'sub', 'abs', 'pick', 'maxof', 'neg', 'sign', 'accel', 'hour_block', 'trail_pct', 'own_pct', 'ev_since', 'ev_side', 'ev_value', 'ext_since_ev'}


class Refused(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, '%s: %s' % (code, why)); self.code = code; self.why = why


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def day0(d):
    return AD.day0(str(d))


# ---------------------------------------------------------------- circular refusal
def load_families(path=FAMILIES):
    out = {}
    for r in csv.DictReader(open(path), delimiter='\t'):
        out[r['code']] = {'fam': set(r['families'].split('|')), 'px': r['price_derived'] == '1', 'status': r['status']}
    return out


def collect_reads(dfn):
    """everything the definition reads: every code under inputs, conditions, fire (side), base and mirror, price, events. The truth labels are
    not the trigger and are left out. An unknown op is refused: its reads cannot be known."""
    codes, events = set(), set(); price = [False]

    def walk(x):
        if isinstance(x, dict):
            if 'op' in x:
                if x['op'] not in KNOWN_OPS:
                    raise Refused('UNKNOWN_OP', 'op %r: its reads cannot be known' % x['op'])
                if x['op'] == 'price':
                    price[0] = True
            for k, v in x.items():
                if k == 'code' and isinstance(v, str):
                    codes.add(v)
                if k == 'events' and isinstance(v, str):
                    events.add(v)
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for k in ('inputs', 'conditions', 'fire', 'base'):
        walk(dfn.get(k, {}))
    for k, v in (dfn.get('mirror') or {}).items():
        if k == 'PRICE':
            price[0] = True
        else:
            codes.add(k)
            if isinstance(v, str) and v != '-':
                codes.add(v)
    for n in (dfn.get('base') or {}).get('busy_avoid', []):
        events.add(n)
    return {'codes': codes, 'price': price[0], 'events': events}


def label_codes(lab):
    out = set()
    if lab.get('code'):
        out.add(lab['code'])
    for c in (lab.get('code_by_side') or {}).values():
        out.add(c)
    if isinstance(lab.get('thr_code'), dict) and lab['thr_code'].get('code'):
        out.add(lab['thr_code']['code'])
    return out


def check_label_shape(lab):
    if lab.get('kind') != 'metric_test':
        raise Refused('BAD_LABEL', 'kind %r' % lab.get('kind'))
    if bool(lab.get('code')) == bool(lab.get('code_by_side')):
        raise Refused('BAD_LABEL', 'give code or code_by_side, one of them')
    if lab.get('code_by_side') and set(lab['code_by_side']) != {'1', '-1'}:
        raise Refused('BAD_LABEL', 'code_by_side needs the keys 1 and -1')
    if lab.get('when') not in ('window', 'present'):
        raise Refused('BAD_LABEL', 'when must be window or present')
    if lab.get('test') not in TESTS:
        raise Refused('BAD_LABEL', 'test %r' % lab.get('test'))
    if lab['test'] in ('>=', '<=') and lab.get('agg') not in AGGS:
        raise Refused('BAD_LABEL', 'agg %r' % lab.get('agg'))
    if lab.get('sign', 'none') not in ('none', 'same', 'opposite'):
        raise Refused('BAD_LABEL', 'sign %r' % lab.get('sign'))
    if lab.get('change', 'abs') not in ('abs', 'pct'):
        raise Refused('BAD_LABEL', 'change %r' % lab.get('change'))
    ma = lab.get('max_age_s')
    if isinstance(ma, bool) or not isinstance(ma, (int, float)) or not math.isfinite(ma) or ma <= 0:
        raise Refused('BAD_LABEL', 'max_age_s is required and positive')
    st, en = lab.get('start_s', 0), lab.get('end_s')
    for x in (st, en):
        if isinstance(x, bool) or not isinstance(x, int):
            raise Refused('BAD_LABEL', 'start_s and end_s are whole seconds')
    if st < 0 or en <= st:
        raise Refused('BAD_LABEL', 'needs 0 <= start_s < end_s (a window starts after t)')
    if lab['when'] == 'present' and st != 0:
        raise Refused('BAD_LABEL', 'a present label has no start_s')
    has = [k for k in ('thr', 'thr_code', 'thr_input') if lab.get(k) is not None]
    if len(has) > 1:
        raise Refused('BAD_LABEL', 'one threshold: %s' % has)
    if lab['test'] in ('>=', '<=') and not has:
        raise Refused('BAD_LABEL', '%s needs a threshold' % lab['test'])
    if lab.get('thr') is not None and (isinstance(lab['thr'], bool) or not isinstance(lab['thr'], (int, float)) or not math.isfinite(lab['thr'])):
        raise Refused('BAD_LABEL', 'thr must be a finite number')
    if lab['test'] in ('falling', 'rising') and lab.get('thr', 0) < 0:
        raise Refused('BAD_LABEL', 'falling and rising take a threshold of 0 or more')


def check_circular(dfn, lab, fams=None):
    """raises Refused, or returns the notes printed on the card. Order: price, unknown, same code, same family (a price-reading trigger may
    still be tested on a no-price label)."""
    fams = fams if fams is not None else load_families()
    check_label_shape(lab)
    reads = collect_reads(dfn); lcodes = label_codes(lab); notes = []
    tf = set()
    for c in sorted(reads['codes']):
        e = fams.get(c)
        if e is None or e['status'] == 'UNKNOWN':
            raise Refused('UNKNOWN_SOURCE', 'the trigger reads %s: its source is not determined' % c)
        tf |= e['fam']
        if e['status'] == 'GUESS':
            notes.append('family of trigger code %s is a guess: %s' % (c, '|'.join(sorted(e['fam']))))
    for n in sorted(reads['events']):
        ef = (dfn.get('events_family') or {}).get(n)
        if not ef:
            raise Refused('UNKNOWN_SOURCE', 'the trigger reads the event list %s: state its source in events_family' % n)
        tf |= set(ef.split('|'))
    if reads['price']:
        tf.add('PRICE')
    for c in sorted(lcodes):
        e = fams.get(c)
        if e is None or e['status'] == 'UNKNOWN':
            raise Refused('UNKNOWN_SOURCE', 'the label reads %s: its source is not determined' % c)
        if e['px'] or 'PRICE' in e['fam']:
            raise Refused('PRICE_DERIVED', 'the label reads %s, price-derived' % c)
        if c in reads['codes']:
            raise Refused('SAME_CODE', 'the label reads %s and so does the trigger' % c)
        hit = e['fam'] & tf
        if hit:
            raise Refused('SAME_FAMILY', 'the label reads %s (%s), the trigger reads that family' % (c, '|'.join(sorted(hit))))
        if e['status'] == 'GUESS':
            notes.append('family of label code %s is a guess: %s' % (c, '|'.join(sorted(e['fam']))))
        for t in sorted(tf):
            for f in sorted(e['fam']):
                if (t, f) in MECHANICAL:
                    notes.append('MECHANICAL LINK: ' + MECHANICAL[(t, f)])
    return sorted(set(notes)), sorted(reads['codes']) + (['price'] if reads['price'] else []), sorted(tf)


# ---------------------------------------------------------------- the data
class NativeSource:
    """the lab source's own Days reader on each code's own clock. Nothing after `last` is opened (NOT KNOWN). A code or day not built: NaN."""

    def __init__(self, lab_root, last):
        self.lab = AD.LabSource(lab_root=lab_root)
        self.R = self.lab.R; self.last = str(last); self._c = {}

    def native(self, code, day):
        day = str(day)
        if day > self.last:
            return None
        key = (code, day)
        if key not in self._c:
            if len(self._c) > 16:
                self._c.pop(next(iter(self._c)))
            self._c[key] = self._read(code, day)
        return self._c[key]

    def _read(self, code, day):
        from lab3 import days as LD
        try:
            coins = list(self.lab.coins(day))
            if not coins:
                return None
            d = {'coins': {c: i for i, c in enumerate(coins)}, 'step': self.R.step(code, day), 'v': self.R.read(code, 'v', [day], coins)[0],
                 'a': self.R.read(code, 'a', [day], coins)[0], 'e': self.R.read(code, 'e', [day], coins)[0], 'k': None}
        except LD.NotBuilt:
            return None
        try:
            d['k'] = self.R.read(code, 'k', [day], coins)[0]
        except LD.NotBuilt:                                    # a code with no k: known at its step end by the as-of rule
            pass
        return d


def _day(t):
    return datetime.datetime.fromtimestamp(int(t) // 86400 * 86400, datetime.timezone.utc).strftime('%Y%m%d')


def cell(src, code, coin, x, max_age, need_known_by=None):
    """the value of the column as of second x, or NaN (missing, stale, a reason, or known after need_known_by)"""
    x = int(math.floor(x)); d = src.native(code, _day(x))
    if d is None or coin not in d['coins']:
        return NAN
    i = d['coins'][coin]; st = d['step']; j = (x - day0(_day(x))) // st
    v = float(d['v'][i, j])
    if not math.isfinite(v) or int(d['e'][i, j]) != 0:
        return NAN
    a = int(d['a'][i, j])
    if a < 0 or a > max_age:
        return NAN
    if need_known_by is not None and d['k'] is not None and int(d['k'][i, j]) > int(need_known_by) * 1_000_000:
        return NAN
    return v


def interval_rows(lo, hi, step):
    """the column ends tau in (lo, hi] whose whole step (tau - step, tau] lies inside (lo, hi]"""
    first = (math.ceil(lo / step) + 1) * step
    last = math.floor(hi / step) * step
    return range(first, last + 1, step)


def _code_of(lab, side):
    if lab.get('code'):
        return lab['code']
    if side not in (1, -1):
        return None
    s = side if lab.get('dir', 'same') == 'same' else -side
    return lab['code_by_side'][str(s)]


def _bounds(lab, t):
    if lab['when'] == 'present':
        return t - lab['end_s'], t
    return t + lab.get('start_s', 0), t + lab['end_s']


def threshold(src, lab, coin, t, thr_input=None):
    """known at t: fixed, or as of t from a code (known_at <= t), or the engine's input; NaN = NOT KNOWN"""
    if lab.get('thr') is not None:
        return float(lab['thr'])
    if lab.get('thr_code') is not None:
        v = cell(src, lab['thr_code']['code'], coin, t, lab['max_age_s'], need_known_by=t)
        return v * float(lab['thr_code'].get('scale', 1.0))
    if lab.get('thr_input') is not None:
        return float(thr_input) if thr_input is not None else NAN
    return 0.0


def metric_value(src, lab, coin, t, side):
    """the measure of one moment; NaN = NOT KNOWN. The present mode reads nothing after t and nothing known after t."""
    code = _code_of(lab, side)
    if code is None:
        return NAN
    lo, hi = _bounds(lab, t); ma = lab['max_age_s']; kb = t if lab['when'] == 'present' else None
    if lab['test'] in ('falling', 'rising'):
        a, b = cell(src, code, coin, lo, ma, kb), cell(src, code, coin, hi, ma, kb)
        if not (math.isfinite(a) and math.isfinite(b)):
            return NAN
        if lab.get('change', 'abs') == 'pct':
            if a == 0:
                return NAN
            val = 100.0 * (b - a) / abs(a)
        else:
            val = b - a
    elif lab['agg'] == 'last':
        val = cell(src, code, coin, hi, ma, kb)
    else:
        d = src.native(code, _day(hi)) or src.native(code, _day(lo))
        if d is None:
            return NAN
        rows = interval_rows(lo, hi, d['step'])
        vals = [cell(src, code, coin, tau, ma, kb) for tau in rows]
        if not vals or not all(math.isfinite(x) for x in vals):
            return NAN
        val = {'sum': sum, 'mean': lambda z: sum(z) / len(z), 'max': max, 'min': min}[lab['agg']](vals)
    if not math.isfinite(val):
        return NAN
    sg = lab.get('sign', 'none')
    if sg != 'none':
        if side not in (1, -1):
            return NAN
        val *= side if sg == 'same' else -side
    return val


def hit_of(lab, val, thr):
    if not (math.isfinite(val) and math.isfinite(thr)):
        return NAN
    tst = lab['test']
    if tst == '>=':
        return float(val >= thr)
    if tst == '<=':
        return float(val <= thr)
    if tst == 'falling':
        return float(val < -abs(thr))
    return float(val > abs(thr))


def eval_moments(src, lab, coin, t, side):
    n = len(t); val = np.full(n, NAN); hit = np.full(n, NAN)
    for j in range(n):
        s = int(side[j]) if np.isfinite(side[j]) else 0
        val[j] = metric_value(src, lab, str(coin[j]), int(t[j]), s)
        hit[j] = hit_of(lab, val[j], threshold(src, lab, str(coin[j]), int(t[j])))
    return val, hit


def label_values_v2(ctx, lab, pts, sides):
    """alarm_design_v3.label_values with the new kind: its own kinds go to the released code unchanged. The engine's rows and thr_input are used;
    value, hit and pre as there (after6 has no meaning here: NaN)."""
    if lab['kind'] != 'metric_test':
        return AD.label_values(ctx, lab, pts, sides)
    check_label_shape(lab)
    n = len(pts); out = dict(value=np.full(n, NAN), hit=np.full(n, NAN), after6=np.full(n, NAN), pre=np.full(n, NAN))
    src = ctx.src if hasattr(ctx.src, 'native') else None
    if src is None:
        raise Refused('BAD_SOURCE', 'metric_test needs a source with native()')
    ti = ctx.get(lab['thr_input']) if lab.get('thr_input') else None
    w = lab['end_s'] - lab.get('start_s', 0)
    for j, ((i, r), s) in enumerate(zip(pts, sides)):
        c = ctx.coins[i]; t = int(ctx.t[r]); side = int(s)
        v = metric_value(src, lab, c, t, side); out['value'][j] = v
        out['hit'][j] = hit_of(lab, v, threshold(src, lab, c, t, ti[i, r] if ti is not None else None))
        if lab['when'] == 'window':
            pre = dict(lab); pre['when'] = 'present'; pre['end_s'] = w; pre['start_s'] = 0
            out['pre'][j] = metric_value(src, pre, c, t, side)
    return out


# ---------------------------------------------------------------- the comparison (the released first look's band pairs)
class Shim:
    """what fl_read_v11.match7 and stats7 read of a Look: its rows and masks. The 4c race column carries the label: 1 hit, 0 no hit, NaN not known."""

    def __init__(self, A, R, hitA, hitR, lean):
        self.A = {'coin': A['coin'], 't': A['t'], 'OBH4_%dM__%s' % (FL.HIT_H, lean): hitA}
        self.R = {'coin': R['coin'], 't': R['t'], 'OBH4_%dM__%s' % (FL.HIT_H, lean): hitR}
        self.lean = lean; self.cA = A['c']; self.cR = R['c']; self.wR = R['w']
        self.useA = ~np.isin(A['coin'].astype(str), FL.EXCLUDE); self.useR = ~np.isin(R['coin'].astype(str), FL.EXCLUDE)
        self.fmonth = np.array([_day(x)[2:6] for x in A['t']], object); self.rmonth = np.array([_day(x)[2:6] for x in R['t']], object)
        self.preR = FL.pre_fire_mask(A, R)
        self.wid = WV.waves(A['t'], WAVE_S)
        fi = np.full(self.wid.max() + 1 if len(self.wid) else 0, -1, int); fi[self.wid[::-1]] = np.arange(len(self.wid))[::-1]; self._fi = fi
        self.wmonth = self.fmonth[fi[self.wid]] if len(self.wid) else self.fmonth
        fd = np.array([_day(x) for x in A['t']], object)
        self.wday = fd[fi[self.wid]] if len(self.wid) else fd

    def first_index(self, waves):
        return self._fi[np.asarray(waves, int)]


def verdict(gap, lo, hi):
    """the frozen order; NaN anywhere is UNSURE"""
    if not (math.isfinite(gap) and math.isfinite(lo) and math.isfinite(hi)):
        return 'UNSURE'
    if gap >= MIN_EFFECT and lo > 0:
        return 'TRUE'
    if hi < MIN_EFFECT:
        return 'NOT SUPPORTED'
    return 'UNSURE'


def wave_stats(L, X, months, seed, drop_days=()):
    """one value per wave, the wave bootstrap, and the interval widened by the random's own error (cell shares are estimated too)"""
    sel = X['matched'] & np.isin(L.wmonth, list(months)) & np.isfinite(X['e'])
    if drop_days:
        sel &= ~np.isin(L.wday, list(drop_days))
    out = {'fires': int(sel.sum()), 'waves': 0, 'gap': NAN, 'lo': NAN, 'hi': NAN, 'blo': NAN, 'bhi': NAN, 'flip_p': NAN, 'share': NAN, 'expected': NAN, 'rnd_se': NAN}
    if not sel.any():
        return out, np.zeros(0)
    u, inv = np.unique(L.wid[sel], return_inverse=True); nw = np.bincount(inv)
    wm = np.bincount(inv, weights=X['e'][sel]) / nw
    rng = np.random.default_rng(seed)
    blo, bhi = AD.boot_ci(wm, rng); gap = float(wm.mean())
    ak = np.bincount(X['key'][sel], weights=1.0 / nw[inv], minlength=len(X['keys'])) / len(u)
    sr = math.sqrt(float((ak ** 2 * X['kvar']).sum())) if len(X['keys']) else 0.0
    lo = gap - math.hypot(gap - blo, 1.96 * sr) if math.isfinite(blo) else NAN
    hi = gap + math.hypot(bhi - gap, 1.96 * sr) if math.isfinite(bhi) else NAN
    out.update(waves=len(u), gap=gap, lo=lo, hi=hi, blo=blo, bhi=bhi, flip_p=AD.flip_p(wm, rng), rnd_se=sr,
               share=float((np.bincount(inv, weights=X['hit'][sel]) / nw).mean()), expected=float((np.bincount(inv, weights=X['p'][sel]) / nw).mean()))
    return out, wm


def compare(A, R, hitA, hitR, bz, lean, months, busy_min_c, seed=20261102):
    """fires against equally busy random moments: fl_read_v11.match7 on the label. busy_min_c 0: every fire; 1.12: the first look's busy fires."""
    L = Shim(A, R, hitA, hitR, lean); keep = FL.BUSY_MIN_C
    FL.BUSY_MIN_C = busy_min_c
    try:
        X = FL.match7(L, bz, tuple(months))
    finally:
        FL.BUSY_MIN_C = keep
    main, _ = wave_stats(L, X, months, seed)
    ex, _ = wave_stats(L, X, months, seed, drop_days=CRASH_DAYS)
    per = {}
    for m in months:
        per[m], _ = wave_stats(L, X, (m,), seed)
    st = FL.stats7(L, X, tuple(months))
    return {'all': main, 'ex': ex, 'months': per, 'z_stats7': st['z'], 'stats7_mean': st['mean_pts'],
            'unmatched': int((X['ok'] & ~X['matched'] & np.isin(L.fmonth, list(months))).sum()), 'outside': int(X['outside'].sum()), 'fallback': int(X['fallback'].sum()),
            'L': L, 'X': X}


# ---------------------------------------------------------------- the lists
def load_perfire(path, first, last):
    """only kind, coin, t, side, w, c of the PERFIRE (its race columns are outcomes: never read) and only rows inside the window"""
    lo, hi = day0(first), day0(AD.shift(str(last), 1))
    rows = {'A': [], 'R': []}; drop = 0
    with open(path) as f:
        rd = csv.reader(f, delimiter='\t'); h = next(rd); ix = [h.index(x) for x in ('kind', 'coin', 't', 'side', 'w', 'c')]
        for r in rd:
            k, coin, t, sd, w, c = (r[i] for i in ix); t = int(float(t))
            if lo <= t < hi:
                rows[k].append((coin, t, float(sd), float(w), float(c)))
            else:
                drop += 1

    def arr(x):
        return {'coin': np.array([y[0] for y in x], object), 't': np.array([y[1] for y in x], np.int64), 'side': np.array([y[2] for y in x], float),
                'w': np.array([y[3] for y in x], float), 'c': np.array([y[4] for y in x], float)}
    return arr(rows['A']), arr(rows['R']), drop


def months_of(first, last):
    return [m[2:] for m in AD.months_list(str(first), str(last))]


def run(claim_path, out, src=None):
    cl = json.load(open(claim_path)); lab = cl['label']
    dfn = json.load(open(cl['def'])) if cl.get('def') else {'inputs': cl.get('inputs', {})}
    if cl.get('def_sha16') and sha16(cl['def']) != cl['def_sha16']:
        raise Refused('DEF_CHANGED', cl['def'])
    notes, reads, fams = check_circular(dfn, lab)
    if sha16(cl['perfire']) != cl['perfire_sha16']:
        raise Refused('PERFIRE_CHANGED', cl['perfire'])
    if os.path.exists(out):
        raise Refused('OUT_EXISTS', out)
    A, R, dropped = load_perfire(cl['perfire'], cl['first'], cl['last'])
    bzA, jA = FL.load_bz(cl['bz_a'], A); bzR, jR = FL.load_bz(cl['bz_r'], R)
    src = src or NativeSource(cl['lab_days'], cl['last'])
    vA, hA = eval_moments(src, lab, A['coin'], A['t'], A['side'])
    vR, hR = eval_moments(src, lab, R['coin'], R['t'], R['side'])
    months = months_of(cl['first'], cl['last'])
    res = compare(A, R, hA, hR, {'A': bzA, 'R': bzR}, cl.get('lean', 'FADE'), months, 0.0)
    busy = compare(A, R, hA, hR, {'A': bzA, 'R': bzR}, cl.get('lean', 'FADE'), months, FL.BUSY_MIN_C)
    a = res['all']; v = verdict(a['gap'], a['lo'], a['hi'])
    os.makedirs(out)
    L = []
    w = L.append
    w('# TRUE GATE %s %s (print-only; TEST, NOT REVIEWED; playground)' % (cl['id'], VERSION))
    w('alarm %s; claim: %s' % (cl.get('alarm_id'), cl.get('claim', '')))
    w('label: %s' % json.dumps(lab, sort_keys=True))
    w('trigger reads: %s; families: %s' % (','.join(reads), ','.join(fams)))
    for n in notes:
        w('NOTE ' + n)
    w('fires %d, random %d, rows outside %s..%s left unread %d; label known: fires %.1f pct, random %.1f pct' % (
        len(A['t']), len(R['t']), cl['first'], cl['last'], dropped, 100 * np.isfinite(hA).mean() if len(hA) else NAN, 100 * np.isfinite(hR).mean() if len(hR) else NAN))
    w('busy join: fires without busy values %d, random %d; unmatched fires %d, outside the bands %d, priced by the period %d' % (jA['rows_without_bz'], jR['rows_without_bz'], res['unmatched'], res['outside'], res['fallback']))
    w('VERDICT %s: gap %+.3f on %d waves (%d fires), interval %+.3f..%+.3f (wave bootstrap %+.3f..%+.3f, widened by the random\'s error %.4f)' % (v, a['gap'], a['waves'], a['fires'], a['lo'], a['hi'], a['blo'], a['bhi'], a['rnd_se']))
    w('fires hit %.3f, equally busy random %.3f' % (a['share'], a['expected']))
    e = res['ex']; w('ex 10-11 Oct: gap %+.3f on %d waves, interval %+.3f..%+.3f' % (e['gap'], e['waves'], e['lo'], e['hi']))
    b = busy['all']; w('first look busy fires only (information): gap %+.3f on %d waves, interval %+.3f..%+.3f' % (b['gap'], b['waves'], b['lo'], b['hi']))
    w('luck (information only, uncalibrated, never in the verdict): flip p %.4f' % a['flip_p'])
    w('month\twaves\tfires\thit\trandom\tgap\tlo\thi')
    for m in months:
        x = res['months'][m]
        w('%s\t%d\t%d\t%.3f\t%.3f\t%+.3f\t%+.3f\t%+.3f' % (m, x['waves'], x['fires'], x['share'], x['expected'], x['gap'], x['lo'], x['hi']))
    txt = '\n'.join(L) + '\n'
    open(os.path.join(out, 'TRUE_CARD.txt'), 'w').write(txt)
    print(txt)
    row = {'id': cl['id'], 'alarm': cl.get('alarm_id'), 'code': ','.join(sorted(label_codes(lab))), 'fires': a['fires'], 'waves': a['waves'], 'gap': round(a['gap'], 4), 'lo': round(a['lo'], 4), 'hi': round(a['hi'], 4),
           'verdict': v, 'ex_gap': round(e['gap'], 4), 'ex_lo': round(e['lo'], 4), 'ex_hi': round(e['hi'], 4), 'known_fires': round(float(np.isfinite(hA).mean()), 4), 'known_random': round(float(np.isfinite(hR).mean()), 4), 'flip_p_uncalibrated': round(a['flip_p'], 4)}
    with open(os.path.join(out, 'TRUE_ROW.tsv'), 'w') as f:
        f.write('\t'.join(row) + '\n' + '\t'.join(str(x) for x in row.values()) + '\n')
    return row


def main(argv):
    try:
        if argv[1] == 'check':
            cl = json.load(open(argv[2])); dfn = json.load(open(cl['def']))
            print('OK', check_circular(dfn, cl['label'])); return 0
        if argv[1] == 'run':
            run(argv[2], argv[3]); return 0
    except Refused as e:
        print('REFUSED %s' % e); return 2
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
