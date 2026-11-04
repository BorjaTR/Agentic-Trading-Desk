#!/usr/bin/env python3
"""true_gate_v2.py (SCOUT, 2 Nov 2026; TEST, NOT REVIEWED; print-only) (released edition: made by make_true_gate_home_v1.py from the playground; only paths and pins differ). A library of true_gate_v3.py: run that one. V1 stays as it is and is imported, with its sha16 checked.
New in V2:
 1 strata: true_gate_v1's busy match run unchanged inside groups of a second value known at t (fl_read_v11.match7 per group, merged by fire).
   activity = the label metric's own recent activity: the mean of |10 min change| over 6 steps of 600 s ENDING WHERE THE LABEL STARTS, so it never
   reads the label's own window. flow = similar Binance long liquidations: the sum over 15 steps of 60 s of X1.LIQX.S03, bp of the coin's open
   interest, ending at t. Groups: the random pool's weighted quantiles CUTS; every value known at t.
 2 false positives: sets of random moments from the comparison pool, by rows or whole waves, treated as fires against the moments left.
   The verdict rule is V1's. Primary gap: ACTIVITY. The busy-only gap is printed beside.
  python3 -B true_gate_v2.py run <claim.json> <out dir (new)>
  python3 -B true_gate_v2.py fp <claim.json> <out.tsv (new)> <sets> <rows|waves>"""
import hashlib, importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
V1_PATH = os.environ.get('TG_V1', os.path.join(HERE, 'true_gate_v1.py'))
V1_SHA = '9cef10e960700d6b'
if hashlib.sha256(open(V1_PATH, 'rb').read()).hexdigest()[:16] != V1_SHA:
    raise SystemExit('V1 CHANGED: ' + V1_PATH)
_s = importlib.util.spec_from_file_location('true_gate_v1', V1_PATH); TG = importlib.util.module_from_spec(_s); _s.loader.exec_module(TG)
FL, AD = TG.FL, TG.AD
VERSION = 'true_gate_v2'
NAN = float('nan')
CUTS = (0.5, 0.8, 0.95)
ACT_STEP, ACT_N, ACT_MIN = 600, 6, 4
FLOW = {'code': 'X1.LIQX.S03', 'step_s': 60, 'n': 15, 'max_age_s': 300}
SEED = 20261102


def activity(src, lab, coin, t, spec):
    """mean |10 min change| over ACT_N steps ending at the label's start (present: t - end_s; window: t). mode level: pct change of a level; mode change:
    |the stored change| at each step end. Under ACT_MIN known steps: NaN. Nothing later than the anchor is read."""
    anchor = t - lab['end_s'] if lab['when'] == 'present' else t
    code, ma = spec['code'], spec['max_age_s']; xs = []
    for k in range(ACT_N):
        e = anchor - k * ACT_STEP
        if spec['mode'] == 'level':
            a, b = TG.cell(src, code, coin, e - ACT_STEP, ma, t), TG.cell(src, code, coin, e, ma, t)
            if math.isfinite(a) and math.isfinite(b) and a != 0:
                xs.append(abs(100.0 * (b - a) / a))
        else:
            b = TG.cell(src, code, coin, e, ma, t)
            if math.isfinite(b):
                xs.append(abs(b))
    return sum(xs) / len(xs) if len(xs) >= ACT_MIN else NAN


def flow_sum(src, coin, t, spec=FLOW):
    """the sum of stored 60 s values ending at t; a missing step makes it NaN"""
    tot = 0.0
    for k in range(spec['n']):
        v = TG.cell(src, spec['code'], coin, t - k * spec['step_s'], spec['max_age_s'], t)
        if not math.isfinite(v):
            return NAN
        tot += v
    return tot


def group_of(x, cuts):
    """-1 not known, else the group: 0 is at or under the first cut"""
    g = np.searchsorted(cuts, x, side='left').astype(int)
    return np.where(np.isfinite(x), g, -1)


def strat_match(L, hA, hR, bz, months, busy_min_c, sA, sR, cuts=CUTS):
    """fl_read_v11.match7 inside each group of the second value; the groups' cuts are the pool's own. -> X merged by fire, the cuts, balance rows"""
    key = 'OBH4_%dM__%s' % (FL.HIT_H, L.lean)
    use = L.useR & np.isin(L.rmonth, list(months)) & ~L.preR & np.isfinite(hR) & np.isfinite(sR) & (L.wR > 0)
    cu = np.unique(FL.wquantiles(sR[use], L.wR[use], cuts)) if use.any() else np.zeros(0)
    gA, gR = group_of(sA, cu), group_of(sR, cu)
    n = len(hA)
    M = {'e': np.full(n, NAN), 'p': np.full(n, NAN), 'hit': np.array(hA, float), 'key': np.full(n, -1, int), 'matched': np.zeros(n, bool), 'keys': [], 'kvar': [], 'kneff': [], 'ok': np.zeros(n, bool), 'outside': np.zeros(n, bool), 'fallback': np.zeros(n, bool)}
    keep = FL.BUSY_MIN_C; FL.BUSY_MIN_C = busy_min_c; bal = []
    try:
        for g in range(len(cu) + 1):
            L.A[key] = np.where(gA == g, hA, NAN); L.R[key] = np.where(gR == g, hR, NAN)
            X = FL.match7(L, bz, tuple(months))
            j = np.flatnonzero(X['matched'] & (gA == g)); off = len(M['keys'])
            M['e'][j] = X['e'][j]; M['p'][j] = X['p'][j]; M['key'][j] = X['key'][j] + off; M['matched'][j] = True
            M['keys'] += [(g,) + tuple(k) for k in X['keys']]; M['kvar'] += list(X['kvar']); M['kneff'] += list(X['kneff'])
            M['ok'] |= X['ok']; M['outside'] |= X['outside'] & (gA == g); M['fallback'] |= X['fallback'] & (gA == g)
            r = (gR == g) & use; a = (gA == g) & np.isfinite(hA)
            bal.append((g, int(a.sum()), int(j.size), float(sA[a].mean()) if a.any() else NAN, float(np.average(sR[r], weights=L.wR[r])) if r.any() else NAN))
    finally:
        FL.BUSY_MIN_C = keep; L.A[key] = hA; L.R[key] = hR
    M['kvar'] = np.array(M['kvar'], float); M['kneff'] = np.array(M['kneff'], float)
    return M, cu, bal


def gate(A, R, hA, hR, bz, sA, sR, lean, months, seed=SEED, ex=False):
    """-> busy-only stats (V1's) and strata stats on the same rows"""
    L = TG.Shim(A, R, hA, hR, lean); keep = FL.BUSY_MIN_C; FL.BUSY_MIN_C = 0.0
    try:
        X0 = FL.match7(L, bz, tuple(months))
    finally:
        FL.BUSY_MIN_C = keep
    b, _ = TG.wave_stats(L, X0, months, seed)
    M, cu, bal = strat_match(L, hA, hR, bz, months, 0.0, sA, sR)
    s, _ = TG.wave_stats(L, M, months, seed)
    out = {'busy': b, 'strat': s, 'cuts': cu.tolist(), 'balance': bal, 'L': L, 'X0': X0, 'M': M}
    if ex:
        out['strat_ex'], _ = TG.wave_stats(L, M, months, seed, drop_days=TG.CRASH_DAYS)
        out['months'] = {m: TG.wave_stats(L, M, (m,), seed)[0] for m in months}
    return out


def word(x):
    return TG.verdict(x['gap'], x['lo'], x['hi'])


def take(T, ix):
    return {k: v[ix] for k, v in T.items()}


def draw(R, n, mode, rng):
    """indices of a set of pseudo fires, weighted as the pool. rows: n rows by weight. waves: whole pool waves (1800 s) in random order, until n"""
    N = len(R['t'])
    if mode == 'rows':
        p = R['w'] / R['w'].sum()
        return np.sort(rng.choice(N, min(n, N), replace=False, p=p))
    w = TG.WV.waves(R['t'], TG.WAVE_S); ids = rng.permutation(np.unique(w)); cnt = np.bincount(w)
    k = int(np.searchsorted(np.cumsum(cnt[ids]), n)) + 1
    return np.flatnonzero(np.isin(w, ids[:k]))


def fp_sets(R, hR, sR, bzR, n, sets, mode, lean, months, seed=SEED, log=None):
    """each set: pseudo fires against the moments left, the whole comparison and verdict -> one row per set"""
    rows = []
    for s in range(sets):
        rng = np.random.default_rng([seed, s, 0 if mode == 'rows' else 1])
        ix = draw(R, n, mode, rng); left = np.setdiff1d(np.arange(len(R['t'])), ix)
        A2, R2 = take(R, ix), take(R, left)
        bz = {'A': take(bzR, ix), 'R': take(bzR, left)}
        g = gate(A2, R2, hR[ix], hR[left], bz, sR[ix], sR[left], lean, months, seed=seed + s + 1)
        rows.append((s, len(ix), g['busy']['waves'], g['busy']['gap'], g['busy']['lo'], g['busy']['hi'], word(g['busy']), g['strat']['waves'], g['strat']['gap'], g['strat']['lo'], g['strat']['hi'], word(g['strat'])))
    return rows


def fp_summary(rows):
    n = len(rows); out = {}
    for nm, gi, li, wi in (('busy', 3, 4, 6), ('activity', 8, 9, 11)):
        out[nm] = {'sets': n, 'true': sum(r[wi] == 'TRUE' for r in rows) / n, 'not_supported': sum(r[wi] == 'NOT SUPPORTED' for r in rows) / n, 'unsure': sum(r[wi] == 'UNSURE' for r in rows) / n,
                   'lo_above_0': sum(r[li] > 0 for r in rows) / n, 'gap_mean': float(np.nanmean([r[gi] for r in rows])), 'gap_sd': float(np.nanstd([r[gi] for r in rows]))}
    return out


def load(cl, src=None):
    lab = cl['label']; dfn = json.load(open(cl['def'])) if cl.get('def') else {'inputs': cl.get('inputs', {})}
    if cl.get('def_sha16') and TG.sha16(cl['def']) != cl['def_sha16']:
        raise TG.Refused('DEF_CHANGED', cl['def'])
    notes, reads, fams = TG.check_circular(dfn, lab)
    if TG.sha16(cl['perfire']) != cl['perfire_sha16']:
        raise TG.Refused('PERFIRE_CHANGED', cl['perfire'])
    A, R, drop = TG.load_perfire(cl['perfire'], cl['first'], cl['last'])
    bzA, jA = FL.load_bz(cl['bz_a'], A); bzR, jR = FL.load_bz(cl['bz_r'], R)
    src = src or TG.NativeSource(cl['lab_days'], cl['last'])
    _, hA = TG.eval_moments(src, lab, A['coin'], A['t'], A['side']); _, hR = TG.eval_moments(src, lab, R['coin'], R['t'], R['side'])
    return dict(lab=lab, notes=notes, reads=reads, fams=fams, A=A, R=R, drop=drop, bzA=bzA, bzR=bzR, jA=jA, jR=jR, src=src, hA=hA, hR=hR, months=TG.months_of(cl['first'], cl['last']), lean=cl.get('lean', 'FADE'))


def second(cl, d):
    src, lab = d['src'], d['lab']
    if cl.get('strata', 'activity') == 'flow':
        f = lambda c, t: flow_sum(src, c, t)
    else:
        f = lambda c, t: activity(src, lab, c, t, cl['activity'])
    return (np.array([f(str(c), int(t)) for c, t in zip(d['A']['coin'], d['A']['t'])], float),
            np.array([f(str(c), int(t)) for c, t in zip(d['R']['coin'], d['R']['t'])], float))


def run(path, out, src=None):
    cl = json.load(open(path)); d = load(cl, src)
    if os.path.exists(out):
        raise TG.Refused('OUT_EXISTS', out)
    sA, sR = second(cl, d)
    g = gate(d['A'], d['R'], d['hA'], d['hR'], {'A': d['bzA'], 'R': d['bzR']}, sA, sR, d['lean'], d['months'], ex=True)
    s, b, e = g['strat'], g['busy'], g['strat_ex']; v = word(s)
    os.makedirs(out); L = []; w = L.append
    w('# TRUE GATE V2 %s (print-only; TEST, NOT REVIEWED; playground)' % cl['id'])
    w('alarm %s; claim: %s' % (cl.get('alarm_id'), cl.get('claim', '')))
    w('label: %s' % json.dumps(d['lab'], sort_keys=True))
    w('second match: %s; %s' % (cl.get('strata', 'activity'), json.dumps(cl.get('activity', FLOW), sort_keys=True)))
    for n in d['notes']:
        w('NOTE ' + n)
    w('fires %d, random %d; label known: fires %.1f pct, random %.1f pct; second value known: fires %.1f pct, random %.1f pct' % (len(d['hA']), len(d['hR']), 100 * np.isfinite(d['hA']).mean(), 100 * np.isfinite(d['hR']).mean(), 100 * np.isfinite(sA).mean(), 100 * np.isfinite(sR).mean()))
    w('VERDICT %s: gap %+.3f on %d waves (%d fires), interval %+.3f..%+.3f; fires hit %.3f, matched random %.3f' % (v, s['gap'], s['waves'], s['fires'], s['lo'], s['hi'], s['share'], s['expected']))
    w('BUSY MATCH ONLY: %s: gap %+.3f on %d waves (%d fires), interval %+.3f..%+.3f; fires hit %.3f, random %.3f' % (word(b), b['gap'], b['waves'], b['fires'], b['lo'], b['hi'], b['share'], b['expected']))
    w('ex 10-11 Oct: gap %+.3f on %d waves, interval %+.3f..%+.3f' % (e['gap'], e['waves'], e['lo'], e['hi']))
    w('luck (information only, uncalibrated, never in the verdict): flip p %.4f' % s['flip_p'])
    w('cuts %s' % json.dumps(g['cuts']))
    w('group\tfires_known\tfires_matched\tfires_mean_value\trandom_mean_value')
    for r in g['balance']:
        w('%d\t%d\t%d\t%.4f\t%.4f' % r)
    w('month\twaves\tfires\thit\trandom\tgap\tlo\thi')
    for m in d['months']:
        x = g['months'][m]; w('%s\t%d\t%d\t%.3f\t%.3f\t%+.3f\t%+.3f\t%+.3f' % (m, x['waves'], x['fires'], x['share'], x['expected'], x['gap'], x['lo'], x['hi']))
    txt = '\n'.join(L) + '\n'; open(os.path.join(out, 'TRUE_CARD.txt'), 'w').write(txt); print(txt)
    return {'id': cl['id'], 'verdict': v, 'fires': s['fires'], 'waves': s['waves'], 'gap': round(s['gap'], 4), 'lo': round(s['lo'], 4), 'hi': round(s['hi'], 4), 'busy_word': word(b), 'busy_gap': round(b['gap'], 4), 'busy_lo': round(b['lo'], 4), 'busy_hi': round(b['hi'], 4), 'ex_gap': round(e['gap'], 4), 'ex_lo': round(e['lo'], 4), 'ex_hi': round(e['hi'], 4), 'known_fires': round(float(np.isfinite(d['hA']).mean()), 4), 'known_second': round(float(np.isfinite(sA).mean()), 4)}


def run_fp(path, out, sets, mode):
    cl = json.load(open(path)); d = load(cl)
    if os.path.exists(out):
        raise TG.Refused('OUT_EXISTS', out)
    _, sR = second(cl, d)
    n = min(len(d['A']['t']), int(0.4 * len(d['R']['t'])))
    rows = fp_sets(d['R'], d['hR'], sR, d['bzR'], n, sets, mode, d['lean'], d['months'])
    with open(out + '.part', 'w') as f:
        f.write('set\tn\tbusy_waves\tbusy_gap\tbusy_lo\tbusy_hi\tbusy_word\tact_waves\tact_gap\tact_lo\tact_hi\tact_word\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')
    os.replace(out + '.part', out)
    su = fp_summary(rows); print('FP', cl['id'], mode, 'n', n, json.dumps(su, sort_keys=True), flush=True)
    return su


def main(argv):
    try:
        if argv[1] == 'run':
            run(argv[2], argv[3]); return 0
        if argv[1] == 'fp':
            run_fp(argv[2], argv[3], int(argv[4]), argv[5]); return 0
    except TG.Refused as e:
        print('REFUSED %s' % e); return 2
    print(__doc__); return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
