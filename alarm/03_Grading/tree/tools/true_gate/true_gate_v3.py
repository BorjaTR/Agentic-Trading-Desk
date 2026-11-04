#!/usr/bin/env python3
"""true_gate_v3.py (SCOUT, 2 Nov 2026; TEST, NOT REVIEWED; PRINT-ONLY, the word changes no decide_v4 state; SEP-DEC ONLY; its calibration is NOT BLIND; X1 source families are guesses).
The one command of the TRUE step (AGENTS.md step 5c). Added to the playground's V3: check, the months guard, the busy tables built when a claim names none.
New: a directional claim must beat its mirror on the same matched fires; strata = the coin's own activity percentile, known at t; coverage by group;
under half of the known fires matched prints UNSURE; the trigger's flow removed, printed as information only. The rule: under half of the known fires matched prints UNSURE; TRUE = gap >= +0.05, its interval above 0, claim minus mirror >= +0.05, its interval above 0; NOT SUPPORTED = the top of either interval under +0.05; else UNSURE.
Inside a group: V2's two-value band pairs first, and a fire with no such cell is priced on the normal move band alone (counted as coarse).
  python3 -B true_gate_v3.py check <claim.json>                 no data read; REFUSED <CODE> or OK
  python3 -B true_gate_v3.py run <claim.json> <out dir (new)>   exit 0 a word printed, 2 refused
  python3 -B true_gate_v3.py fp <claim.json> <out.tsv (new)> <sets> <rows|waves>"""
import hashlib, importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
V2_PATH = os.environ.get('TG_V2', os.path.join(HERE, 'true_gate_v2.py'))
if hashlib.sha256(open(V2_PATH, 'rb').read()).hexdigest()[:16] != '08323a3835d4d265':
    raise SystemExit('V2 CHANGED')
_s = importlib.util.spec_from_file_location('true_gate_v2', V2_PATH); G2 = importlib.util.module_from_spec(_s); _s.loader.exec_module(G2)
TG, FL, AD = G2.TG, G2.FL, G2.AD
NAN = float('nan'); MIN = TG.MIN_EFFECT; MIN_COVER = 0.5; SEED = 20261102
CUTS = np.array([0.5, 0.8, 0.95]); HIST_DAYS = 14; HIST_STEP = 3600; HIST_MIN = 72
FLOW_L, FLOW_S = 'X1.LIQX.S03', 'X1.LIQX.S04'
FIRST_ALLOWED, LAST_ALLOWED = '20250910', '20251231'     # this edition: events Sep-Dec 2025 only. Jan-Feb 2026 gets one look, on the owner's word, in a new edition. The activity history alone reads up to 14 days before an event, known before its day
SAME_FIELDS = ('code', 'code_by_side', 'dir', 'when', 'start_s', 'end_s', 'agg', 'change', 'sign', 'max_age_s', 'kind')
import datetime as _dt                                    # noqa: E402


class History:
    """each coin's own activity, sampled every HIST_STEP, by day, for the days before a moment's day; every sample is known at its own time"""

    def __init__(self, src, lab, spec, coins_of):
        self.src, self.lab, self.spec, self.coins_of = src, lab, spec, coins_of; self.d = {}

    def day(self, day):
        if day not in self.d:
            d0 = TG.day0(day); out = {}
            for c in self.coins_of(day):
                x = [G2.activity(self.src, self.lab, c, d0 + k * HIST_STEP, self.spec) for k in range(24)]
                out[c] = np.array([v for v in x if math.isfinite(v)], float)
            self.d[day] = out
        return self.d[day]

    def pct(self, coin, t, x):
        """the mid-rank of x among the coin's samples of the HIST_DAYS days before t's day; NaN under HIST_MIN samples"""
        if not math.isfinite(x):
            return NAN
        day = TG._day(t); v = []
        for k in range(1, HIST_DAYS + 1):
            e = self.day(AD.shift(day, -k)).get(coin)
            if e is not None and len(e):
                v.append(e)
        if not v:
            return NAN
        v = np.concatenate(v)
        if len(v) < HIST_MIN:
            return NAN
        return float(((v < x).sum() + 0.5 * (v == x).sum()) / len(v))


def coin_pct(src, lab, spec, coin, t, H):
    out = np.full(len(t), NAN)
    for j in range(len(t)):
        out[j] = H.pct(str(coin[j]), int(t[j]), G2.activity(src, lab, str(coin[j]), int(t[j]), spec))
    return out


def strat(L, hA, hR, bz, months, sA, sR):
    """fl_read_v11.match7 per group of the percentile, the two-value cells first, the normal band for the fires left -> X merged, coverage rows"""
    key = 'OBH4_%dM__%s' % (FL.HIT_H, L.lean); gA, gR = G2.group_of(sA, CUTS), G2.group_of(sR, CUTS); n = len(hA)
    M = {'e': np.full(n, NAN), 'p': np.full(n, NAN), 'hit': np.array(hA, float), 'key': np.full(n, -1, int), 'matched': np.zeros(n, bool), 'keys': [], 'kvar': [], 'coarse': np.zeros(n, bool)}
    keep = FL.BUSY_MIN_C; FL.BUSY_MIN_C = 0.0; cov = []
    inm = np.isin(L.fmonth, list(months)) & L.useA
    try:
        for g in range(len(CUTS) + 1):
            L.A[key] = np.where(gA == g, hA, NAN); L.R[key] = np.where(gR == g, hR, NAN)
            for recent in (True, False):
                X = FL.match7(L, bz, tuple(months), recent=recent)
                j = np.flatnonzero(X['matched'] & (gA == g) & ~M['matched']); off = len(M['keys'])
                M['e'][j] = X['e'][j]; M['p'][j] = X['p'][j]; M['key'][j] = X['key'][j] + off; M['matched'][j] = True; M['coarse'][j] = not recent
                M['keys'] += [(g, recent) + tuple(k) for k in X['keys']]; M['kvar'] += list(X['kvar'])
            k = inm & (gA == g) & np.isfinite(hA)
            cov.append((g, int(k.sum()), int((k & M['matched']).sum()), int((k & M['coarse']).sum())))
    finally:
        FL.BUSY_MIN_C = keep; L.A[key] = hA; L.R[key] = hR
    M['kvar'] = np.array(M['kvar'], float)
    known = int((inm & np.isfinite(hA)).sum()); M['cover'] = (M['matched'] & inm & np.isfinite(hA)).sum() / known if known else 0.0
    return M, cov


def difference(L, Mc, Mm, months, seed):
    """per fire matched on both: claimed e minus mirror e; one value per wave; the wave bootstrap widened by both random errors"""
    both = Mc['matched'] & Mm['matched']
    X = {'matched': both, 'e': Mc['e'] - Mm['e'], 'key': Mc['key'], 'keys': Mc['keys'], 'kvar': Mc['kvar'] * 0, 'hit': Mc['hit'], 'p': Mc['p']}
    d, _ = TG.wave_stats(L, X, months, seed); c, _ = TG.wave_stats(L, dict(Mc, matched=both), months, seed); m, _ = TG.wave_stats(L, dict(Mm, matched=both), months, seed)
    sr = math.hypot(c['rnd_se'], m['rnd_se']) if d['waves'] else NAN
    if d['waves']:
        d['lo'] = d['gap'] - math.hypot(d['gap'] - d['blo'], 1.96 * sr); d['hi'] = d['gap'] + math.hypot(d['bhi'] - d['gap'], 1.96 * sr)
    d['claim_gap'] = c['gap']; d['mirror_gap'] = m['gap']
    return d


def verdict3(gap, lo, hi, dg, dlo, dhi, cover):
    if not cover >= MIN_COVER:
        return 'UNSURE'
    if not all(math.isfinite(x) for x in (gap, lo, hi, dg, dlo, dhi)):
        return 'UNSURE'
    if gap >= MIN and lo > 0 and dg >= MIN and dlo > 0:
        return 'TRUE'
    if hi < MIN or dhi < MIN:
        return 'NOT SUPPORTED'
    return 'UNSURE'


def gate(A, R, hA, hR, mA, mR, bz, sA, sR, lean, months, seed=SEED, extra=False):
    L = TG.Shim(A, R, hA, hR, lean)
    Mc, cov = strat(L, hA, hR, bz, months, sA, sR); Mm, _ = strat(L, mA, mR, bz, months, sA, sR)
    s, _ = TG.wave_stats(L, Mc, months, seed); d = difference(L, Mc, Mm, months, seed + 1)
    inm = np.isin(L.fmonth, list(months)) & L.useA; kc, km = inm & np.isfinite(hA), inm & np.isfinite(mA)
    both = kc & np.isfinite(mA) & Mc['matched'] & Mm['matched']
    pair = {'claim_known': int(kc.sum()), 'mirror_known': int(km.sum()), 'joint_known': int((kc & km).sum()), 'matched_both': int(both.sum()), 'paired_waves': int(d['waves'])}
    cover = both.sum() / kc.sum() if kc.any() else 0.0        # fires matched on both over the claim's known fires: the word rests on the paired fires
    v = verdict3(s['gap'], s['lo'], s['hi'], d['gap'], d['lo'], d['hi'], cover)
    out = {'s': s, 'd': d, 'word': v, 'cover': float(cover), 'pair': pair, 'cov': cov, 'L': L, 'Mc': Mc}
    if extra:
        out['ex'], _ = TG.wave_stats(L, Mc, months, seed, drop_days=TG.CRASH_DAYS)
        out['months'] = {m: TG.wave_stats(L, Mc, (m,), seed)[0] for m in months}
        keep = FL.BUSY_MIN_C; FL.BUSY_MIN_C = 0.0
        try:
            X0 = FL.match7(TG.Shim(A, R, hA, hR, lean), bz, tuple(months))
        finally:
            FL.BUSY_MIN_C = keep
        out['busy'], _ = TG.wave_stats(L, X0, months, seed)
    return out


def flow_removed(src, lab, coin, t, val):
    """information only: the label's pct value with the coin's Binance liquidations of the window added back (bp of open interest / 100). A lower bound of the
    forced closes: Binance prints one liquidation a second. NaN when a step is missing."""
    n = lab['end_s'] // 60; out = np.full(len(t), NAN)
    sp = {'step_s': 60, 'n': n, 'max_age_s': 300}
    for j in range(len(t)):
        a = G2.flow_sum(src, str(coin[j]), int(t[j]), dict(sp, code=FLOW_L)); b = G2.flow_sum(src, str(coin[j]), int(t[j]), dict(sp, code=FLOW_S))
        out[j] = val[j] + (a + b) / 100.0
    return out


def check_mirror(l, m):
    """the mirror is the label's exact opposite: every field the same; falling with rising at the same threshold, <= with >= at the opposite threshold"""
    for k in SAME_FIELDS:
        if l.get(k) != m.get(k):
            raise TG.Refused('BAD_MIRROR', '%s: %r against %r' % (k, l.get(k), m.get(k)))
    t, u = l.get('test'), m.get('test')
    if {t, u} != {'falling', 'rising'} and {t, u} != {'>=', '<='}:
        raise TG.Refused('BAD_MIRROR', 'test %s against %s' % (t, u))
    if l.get('thr_input') is not None or m.get('thr_input') is not None:
        raise TG.Refused('BAD_MIRROR', 'an engine input cannot be mirrored here')
    a, b = l.get('thr_code'), m.get('thr_code')
    if a or b:
        if not (a and b) or a.get('code') != b.get('code') or float(a.get('scale', 1.0)) != -float(b.get('scale', 1.0)) * (1 if t in ('>=', '<=') else -1):
            raise TG.Refused('BAD_MIRROR', 'threshold codes %r against %r' % (a, b))
        if l.get('thr') is not None or m.get('thr') is not None:
            raise TG.Refused('BAD_MIRROR', 'two thresholds')
        return
    x, y = l.get('thr'), m.get('thr')
    if t in ('>=', '<='):
        if x is None or y is None or float(x) != -float(y):
            raise TG.Refused('BAD_MIRROR', 'thresholds %r against %r' % (x, y))
    elif float(x or 0) != float(y or 0):
        raise TG.Refused('BAD_MIRROR', 'thresholds %r against %r' % (x, y))


def admit(cl):
    """everything that needs no data: the fields, the months, the definition's pin, the circular rule on the label and its mirror -> notes, reads, families"""
    for k in ('id', 'idea', 'V', 'def', 'def_sha16', 'label', 'mirror', 'activity', 'perfire', 'perfire_sha16', 'first', 'last', 'lab_days'):
        if not cl.get(k):
            raise TG.Refused('BAD_CLAIM', 'the claim has no %s' % k)
    for k in ('first', 'last'):
        try:
            _dt.datetime.strptime(str(cl[k]), '%Y%m%d')
        except ValueError:
            raise TG.Refused('MONTHS', '%s %s is not a calendar date' % (k, cl[k]))
    if str(cl['first']) < FIRST_ALLOWED or str(cl['last']) > LAST_ALLOWED or str(cl['first']) > str(cl['last']):
        raise TG.Refused('MONTHS', 'first %s, last %s: this edition reads events %s to %s only' % (cl['first'], cl['last'], FIRST_ALLOWED, LAST_ALLOWED))
    if os.path.basename(cl['perfire']) != 'PERFIRE_%s.tsv' % cl['V']:
        raise TG.Refused('BAD_CLAIM', 'the PERFIRE %s is not variant %s' % (os.path.basename(cl['perfire']), cl['V']))
    code = cl['label'].get('code'); a = cl['activity']
    if a.get('code') != code or a.get('mode') not in ('level', 'change') or not isinstance(a.get('max_age_s'), (int, float)):
        raise TG.Refused('BAD_CLAIM', 'activity needs the label code, mode level or change, and max_age_s')
    check_mirror(cl['label'], cl['mirror']); m = cl['mirror']
    if not os.path.isfile(cl['def']):
        raise TG.Refused('DEF_CHANGED', 'no definition at %s' % cl['def'])
    if TG.sha16(cl['def']) != cl['def_sha16']:
        raise TG.Refused('DEF_CHANGED', cl['def'])
    dfn = json.load(open(cl['def']))
    notes, reads, fams = TG.check_circular(dfn, cl['label']); TG.check_circular(dfn, m)
    return notes, reads, fams


def busy_tables(cl, A, R, out):
    """the released busy_v2 on this claim's moments, when the claim names no tables; values known at each moment"""
    sys.path.insert(0, os.path.join(TG.REL, '06_First_look/tree/tools/alarm_first_look'))
    import busy_v2 as BZ
    d = os.path.join(out, 'BZ_LISTS'); os.makedirs(d)
    spec = []
    for nm, T in (('A', A), ('R', R)):
        p = os.path.join(d, nm + '.tsv')
        with open(p, 'w') as f:
            f.write('coin\tt\n')
            for k in sorted(set(zip([str(c) for c in T['coin']], [int(t) for t in T['t']]))):
                f.write('%s\t%d\n' % k)
        spec.append((p, nm + '_' + cl['id']))
    BZ.build(cl['lab_days'], os.path.join(TG.REL, '01_Detection/tree/team/LAB3/code'), os.path.join(out, 'BZ'), spec)
    return tuple(os.path.join(out, 'BZ', 'BZ_%s_%s.tsv.gz' % (nm, cl['id'])) for nm in 'AR')


def load(cl, src=None, out=None):
    lab, mir = cl['label'], cl['mirror']; notes, reads, fams = admit(cl)
    if TG.sha16(cl['perfire']) != cl['perfire_sha16']:
        raise TG.Refused('PERFIRE_CHANGED', cl['perfire'])
    A, R, drop = TG.load_perfire(cl['perfire'], cl['first'], cl['last'])
    if cl.get('bz_a'):
        pa, pr = cl['bz_a'], cl['bz_r']
    else:
        if out is None:
            raise TG.Refused('BAD_CLAIM', 'no busy tables and nowhere to build them')
        pa, pr = busy_tables(cl, A, R, out)
    bzA, _ = FL.load_bz(pa, A); bzR, _ = FL.load_bz(pr, R)
    src = src or TG.NativeSource(cl['lab_days'], cl['last'])
    vA, hA = TG.eval_moments(src, lab, A['coin'], A['t'], A['side']); vR, hR = TG.eval_moments(src, lab, R['coin'], R['t'], R['side'])
    _, mA = TG.eval_moments(src, mir, A['coin'], A['t'], A['side']); _, mR = TG.eval_moments(src, mir, R['coin'], R['t'], R['side'])
    coins_of = (lambda day: list(src.lab.coins(day))) if hasattr(src, 'lab') else (lambda day: sorted({str(c) for c in A['coin']} | {str(c) for c in R['coin']}))
    H = History(src, lab, cl['activity'], coins_of)
    sA = coin_pct(src, lab, cl['activity'], A['coin'], A['t'], H); sR = coin_pct(src, lab, cl['activity'], R['coin'], R['t'], H)
    return dict(lab=lab, notes=notes, A=A, R=R, drop=drop, bz={'A': bzA, 'R': bzR}, src=src, vA=vA, vR=vR, hA=hA, hR=hR, mA=mA, mR=mR, sA=sA, sR=sR, fams=fams, months=TG.months_of(cl['first'], cl['last']), lean=cl.get('lean', 'FADE'))


def run(path, out, src=None):
    cl = json.load(open(path)); admit(cl)
    if os.path.exists(out):
        raise TG.Refused('OUT_EXISTS', out)
    os.makedirs(out)
    d = load(cl, src, out)
    g = gate(d['A'], d['R'], d['hA'], d['hR'], d['mA'], d['mR'], d['bz'], d['sA'], d['sR'], d['lean'], d['months'], extra=True)
    s, x, b, e = g['s'], g['d'], g['busy'], g['ex']; L = []; w = L.append
    w('# TRUE GATE V3 %s (print-only: changes no decide_v4 state; TEST, NOT REVIEWED; Sep-Dec only; rule NOT BLIND; X1 families guessed)' % cl['id'])
    w('alarm %s; claim: %s' % (cl.get('alarm_id'), cl.get('claim', '')))
    w('label: %s' % json.dumps(d['lab'], sort_keys=True)); w('mirror: %s' % json.dumps(cl['mirror'], sort_keys=True))
    for n in d['notes']:
        w('NOTE ' + n)
    w('VERDICT %s: gap %+.3f on %d waves (%d fires), interval %+.3f..%+.3f; fires hit %.3f, matched random %.3f' % (g['word'], s['gap'], s['waves'], s['fires'], s['lo'], s['hi'], s['share'], s['expected']))
    w('DIFFERENCE claim minus mirror %+.3f on %d waves, interval %+.3f..%+.3f (claim %+.3f, mirror %+.3f, same fires)' % (x['gap'], x['waves'], x['lo'], x['hi'], x['claim_gap'], x['mirror_gap']))
    w('COVERAGE %.3f = matched on claim and mirror over the claim\'s known fires; rule: under 0.5 prints UNSURE; %s' % (g['cover'], json.dumps(g['pair'], sort_keys=True)))
    w('group\tfires_known\tmatched\tof_them_normal_band_only  (group 3 = the top: at or over the coin\'s own 95th activity percentile)')
    for r in g['cov']:
        w('%d\t%d\t%d\t%d' % r)
    w('busy match only (information): gap %+.3f on %d waves, interval %+.3f..%+.3f' % (b['gap'], b['waves'], b['lo'], b['hi']))
    w('ex 10-11 Oct: gap %+.3f on %d waves, interval %+.3f..%+.3f' % (e['gap'], e['waves'], e['lo'], e['hi']))
    fr = ''
    if 'LIQ_BN' in d['fams'] and d['lab']['code'] in ('E2.S02', 'E2.S04'):
        fA = flow_removed(d['src'], d['lab'], d['A']['coin'], d['A']['t'], d['vA']); fR = flow_removed(d['src'], d['lab'], d['R']['coin'], d['R']['t'], d['vR'])
        hfA = np.array([TG.hit_of(d['lab'], v, TG.threshold(d['src'], d['lab'], 'X', 0)) for v in fA]); hfR = np.array([TG.hit_of(d['lab'], v, TG.threshold(d['src'], d['lab'], 'X', 0)) for v in fR])
        q = gate(d['A'], d['R'], hfA, hfR, d['mA'], d['mR'], d['bz'], d['sA'], d['sR'], d['lean'], d['months'])['s']
        fr = round(q['gap'], 4)
        w('trigger flow removed (information only, never in the verdict; added back Binance liquidations, a lower bound): gap %+.3f on %d waves, interval %+.3f..%+.3f; known fires %.3f' % (q['gap'], q['waves'], q['lo'], q['hi'], float(np.isfinite(hfA).mean())))
    w('luck (information only, uncalibrated, never in the verdict): flip p %.4f' % s['flip_p'])
    w('month\twaves\tfires\thit\trandom\tgap\tlo\thi')
    for m in d['months']:
        y = g['months'][m]; w('%s\t%d\t%d\t%.3f\t%.3f\t%+.3f\t%+.3f\t%+.3f' % (m, y['waves'], y['fires'], y['share'], y['expected'], y['gap'], y['lo'], y['hi']))
    txt = '\n'.join(L) + '\n'; open(os.path.join(out, 'TRUE_CARD.txt'), 'w').write(txt); print(txt)
    r = lambda z: round(z, 4)
    row = {'id': cl['id'], 'verdict': g['word'], 'fires': s['fires'], 'waves': s['waves'], 'gap': r(s['gap']), 'lo': r(s['lo']), 'hi': r(s['hi']), 'diff': r(x['gap']), 'diff_lo': r(x['lo']), 'diff_hi': r(x['hi']), 'mirror': r(x['mirror_gap']), 'cover': r(g['cover']), 'top_known': g['cov'][-1][1], 'top_matched': g['cov'][-1][2], 'busy_gap': r(b['gap']), 'ex_gap': r(e['gap']), 'flow_removed_gap': fr}
    row.update(g['pair'])
    h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]
    with open(os.path.join(out, 'TRUE_CARD.txt'), 'rb') as f:
        card = hashlib.sha256(f.read()).hexdigest()[:16]
    row.update(idea=cl['idea'], V=cl['V'], def_sha16=cl['def_sha16'], perfire_sha16=cl['perfire_sha16'], label_sha16=h(cl['label']), mirror_sha16=h(cl['mirror']), card_sha16=card)
    txt = '\t'.join(row) + '\n' + '\t'.join(str(x) for x in row.values()) + '\n'
    with open(os.path.join(out, 'TRUE_ROW.tsv'), 'w') as f:
        f.write(txt)
    with open(os.path.join(out, 'TRUE_ROW.sha16'), 'w') as f:
        f.write(hashlib.sha256(txt.encode()).hexdigest()[:16] + '\n')
    return row


def fp_sets(d, n, sets, mode, seed=SEED):
    R, rows = d['R'], []
    for s in range(sets):
        rng = np.random.default_rng([seed, s, 0 if mode == 'rows' else 1])
        ix = G2.draw(R, n, mode, rng); lf = np.setdiff1d(np.arange(len(R['t'])), ix)
        bz = {'A': G2.take(d['bz']['R'], ix), 'R': G2.take(d['bz']['R'], lf)}
        g = gate(G2.take(R, ix), G2.take(R, lf), d['hR'][ix], d['hR'][lf], d['mR'][ix], d['mR'][lf], bz, d['sR'][ix], d['sR'][lf], d['lean'], d['months'], seed=seed + s + 2)
        rows.append((s, len(ix), g['s']['waves'], g['s']['gap'], g['s']['lo'], g['s']['hi'], g['d']['gap'], g['d']['lo'], g['d']['hi'], g['cover'], g['word']))
    return rows


def run_fp(path, out, sets, mode):
    cl = json.load(open(path)); admit(cl)
    if os.path.exists(out):
        raise TG.Refused('OUT_EXISTS', out)
    d = load(cl, None, out + '.work')
    n = min(len(d['A']['t']), int(0.4 * len(d['R']['t']))); rows = fp_sets(d, n, sets, mode)
    with open(out + '.part', 'w') as f:
        f.write('set\tn\twaves\tgap\tlo\thi\tdiff\tdiff_lo\tdiff_hi\tcover\tword\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    os.replace(out + '.part', out)
    print('FP', cl['id'], mode, 'n', n, 'TRUE', sum(r[-1] == 'TRUE' for r in rows) / len(rows), 'NS', sum(r[-1] == 'NOT SUPPORTED' for r in rows) / len(rows), 'lo>0', sum(r[4] > 0 for r in rows) / len(rows), 'diff_lo>0', sum(r[7] > 0 for r in rows) / len(rows), flush=True)


def main(a):
    try:
        if a[1] == 'check':
            notes, reads, fams = admit(json.load(open(a[2])))
            print('OK trigger reads %s; families %s' % (','.join(reads), ','.join(fams)))
            cl = json.load(open(a[2])); dg = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]
            print('FOR THE CARD true_label=%s true_mirror=%s' % (dg(cl['label']), dg(cl['mirror'])))
            for n in notes:
                print('NOTE ' + n)
            return 0
        if a[1] == 'run':
            run(a[2], a[3]); return 0
        if a[1] == 'fp':
            run_fp(a[2], a[3], int(a[4]), a[5]); return 0
    except TG.Refused as e:
        print('REFUSED %s' % e); return 2
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
