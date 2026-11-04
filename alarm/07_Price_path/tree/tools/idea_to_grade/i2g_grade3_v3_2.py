"""[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file i2g_grade3.py 618b6c1829b86310 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
i2g_grade3_v3_2.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026): the V3 grade tables, from the V3 measurement columns of the run
(measurements/VALUES3.npy) and the run's frozen weights. One fixed grid for every alarm, set before any value is read:
  measures   the return at 10 s, 1 min, 5 min, 15 min, 1 h, 4 h after the taker fill, and the eight exits of i2g_rules_v1_2.EXITS;
  schemes    TT taker in / taker out; RT resting in (fills only on a trade-through) / taker out; RR resting in / resting target, taker stop
             and time exit. Costs per leg from the cost table (i2g_rules_v1_2.cost_legs) at the honest and the stress gap, and GROSS;
  baselines  CALM = the parent's matched controls (as-of eligibility, normalized draw weights); TOUGH = the parent's same-move,
             same-volatility moments (equal weights, at least TOUGH min_n known); CALM_V2 = the matched controls under the V2 rule
             (sensitivity only: it drops controls by a LATER alarm);
  statistic  per slice (ALL, each calendar month) the wave-clustered weighted mean and its 95% interval (i2g_rules_v1_2.clustered_mean),
             each parent weighted by its FROZEN cluster weight: a slice never rebuilds a weight.
Describes what the stored paths did after each event against the baselines; not causality, not a strategy, not live parity."""
import math, os
import numpy as np
import i2g_rules_v1_2 as RU

STATS = ('PARENT', 'CALM', 'TOUGH', 'CALM_EDGE', 'TOUGH_EDGE', 'CALM_V2_EDGE', 'FILL_SHARE', 'MISSED_TT')
# MISSED_TT: for a resting scheme, the taker-in / taker-out result of the parents whose resting entry did NOT fill (the trades it missed)
COLS = ('slice', 'direction', 'measure', 'scheme', 'cost', 'stat', 'mean', 'lo', 'hi', 'parents', 'clusters')


def measures():
    """[(measure, scheme, value column, code column or None)]"""
    out = [('ret_' + h, 'TT', 'ret_' + h, None) for h in RU.HORIZON_NAMES]
    for e in RU.EXITS:
        n = e[0]
        out += [(n, 'TT', 'tk_' + n, 'tk_%s_code' % n), (n, 'RT', 're_' + n, None), (n, 'RR', 'rb_' + n, 'rb_%s_code' % n)]
    return out


def net(gross, scheme, code, legs):
    """gross pct -> net pct under one scheme; legs = (taker leg, resting leg) pct per row"""
    tk, rs = legs
    if scheme == 'TT':
        return gross - 2 * tk
    if scheme == 'RT':
        return gross - rs - tk
    exit_leg = np.where(code == RU.EXIT_CODES['TARGET'], rs, tk)
    return gross - rs - exit_leg


def base_means(x, groups):
    """groups: per parent a list of (row, weight); -> per parent the weighted mean of the finite x (NaN when none is finite)"""
    out = np.full(len(groups), np.nan)
    for i, g in enumerate(groups):
        if not g:
            continue
        r = np.fromiter((a for a, _ in g), np.int64, len(g)); w = np.fromiter((b for _, b in g), float, len(g))
        v = x[r]; ok = np.isfinite(v)
        if ok.any():
            out[i] = float((w[ok] * v[ok]).sum() / w[ok].sum())
    return out


def tough_means(x, groups, min_n):
    out = np.full(len(groups), np.nan)
    for i, g in enumerate(groups):
        if not g:
            continue
        v = x[np.asarray(g, np.int64)]; v = v[np.isfinite(v)]
        if len(v) >= min_n:
            out[i] = float(v.mean())
    return out


def grade(parents, names3, V3, row_coin, calm, calm_v2, tough, weights, clusters, legs_by_coin, slices=None):
    """parents: [{coin, day, row_ids {FOLLOW, FADE}}]; row_coin: the coin of every observation row; calm / calm_v2: {direction: per parent
    [(row, weight)]}; tough: {direction: per parent [row]}; weights, clusters: per parent (frozen); legs_by_coin: {cost name: {coin:
    (taker leg, resting leg)}}; slices: None = ALL and every month, or the names to keep -> table rows (COLS)"""
    col = {n: i for i, n in enumerate(names3)}
    months = sorted({p['day'][:6] for p in parents})
    keep = None if slices is None else set(slices)
    slices = [('ALL', np.arange(len(parents)))] + [(m, np.asarray([i for i, p in enumerate(parents) if p['day'][:6] == m], np.int64))
                                                    for m in months]
    if keep is not None:
        slices = [x for x in slices if x[0] in keep]
    w = np.asarray(weights, float); cl = np.asarray(clusters, dtype=object)
    legs = {cn: (np.asarray([L[c][0] for c in row_coin], float), np.asarray([L[c][1] for c in row_coin], float))
            for cn, L in legs_by_coin.items()}
    rows = []
    for d in ('FOLLOW', 'FADE'):
        prow = np.asarray([p['row_ids'][d] for p in parents], np.int64)
        for meas, scheme, vcol, ccol in measures():
            g = np.asarray(V3[:, col[vcol]], float); code = np.asarray(V3[:, col[ccol]], float) if ccol else None
            fill = np.asarray(V3[:, col['rs_filled'] if scheme in ('RT', 'RR') else col['tk_filled']], float)
            for cname in ['GROSS'] + sorted(legs):
                x = g if cname == 'GROSS' else net(g, scheme, code, legs[cname])
                if scheme == 'TT':
                    XT = np.full(len(prow), np.nan)
                else:
                    gt = np.asarray(V3[:, col['tk_' + meas]], float)
                    XT = (gt if cname == 'GROSS' else net(gt, 'TT', None, legs[cname]))[prow]
                X = x[prow]; C = base_means(x, calm[d]); T = tough_means(x, tough[d], RU.TOUGH['min_n']); C2 = base_means(x, calm_v2[d])
                # a parent with no cost of record (NO_COST) is absent from every net row, its fill share included (V3.2, review blocker 1)
                F = fill[prow] if cname == 'GROSS' else np.where(np.isfinite(legs[cname][0][prow]), fill[prow], np.nan)
                for sname, ix in slices:
                    known = np.isfinite(X[ix])
                    vals = {'PARENT': X[ix], 'CALM': np.where(known, C[ix], np.nan), 'TOUGH': np.where(known, T[ix], np.nan),
                            'CALM_EDGE': X[ix] - C[ix], 'TOUGH_EDGE': X[ix] - T[ix], 'CALM_V2_EDGE': X[ix] - C2[ix], 'FILL_SHARE': F[ix],
                            'MISSED_TT': np.where(F[ix] == 0, XT[ix], np.nan)}
                    for st in STATS:
                        r = RU.clustered_mean(vals[st], w[ix], cl[ix])
                        rows.append((sname, d, meas, scheme, cname, st, r['mean'], r['lo'], r['hi'], r['parents'], r['clusters']))
    return rows


def fmt(x):
    return '' if x is None or (isinstance(x, float) and not math.isfinite(x)) else ('%.6g' % x if isinstance(x, float) else str(x))


def write(out_dir, rows, weights_rows, header_lines):
    os.makedirs(out_dir)
    with open(os.path.join(out_dir, 'TABLE.tsv'), 'x') as f:
        f.write('\t'.join(COLS) + '\n')
        for r in rows:
            f.write('\t'.join(fmt(x) for x in r) + '\n')
    with open(os.path.join(out_dir, 'WEIGHTS.tsv'), 'x') as f:
        f.write('parent_id\tcluster_id\tweight\tflag\n')
        for r in weights_rows:   # the frozen weights at full precision (repr), so the file equals the universe
            f.write('\t'.join(repr(x) if isinstance(x, float) else fmt(x) for x in r) + '\n')
    by = {(r[0], r[1], r[2], r[3], r[4], r[5]): r for r in rows}
    L = list(header_lines) + ['']
    for d in ('FOLLOW', 'FADE'):
        L += ['## %s, all parents, honest cost (net pct per trade; interval = 95%%, waves as the unit)' % d, '',
              '|measure|scheme|parents|waves|parent net|vs CALM|vs TOUGH|vs CALM (V2 rule, sensitivity)|fill share|missed (TT net)|',
              '|---|---|---:|---:|---:|---|---|---|---:|---:|']
        for meas, scheme, _, _ in measures():
            p = by.get(('ALL', d, meas, scheme, 'HONEST', 'PARENT'))
            if p is None:
                continue
            ce = by[('ALL', d, meas, scheme, 'HONEST', 'CALM_EDGE')]; te = by[('ALL', d, meas, scheme, 'HONEST', 'TOUGH_EDGE')]
            c2 = by[('ALL', d, meas, scheme, 'HONEST', 'CALM_V2_EDGE')]; fs = by[('ALL', d, meas, scheme, 'HONEST', 'FILL_SHARE')]
            ms = by[('ALL', d, meas, scheme, 'HONEST', 'MISSED_TT')]
            ci = lambda r: '%s [%s, %s] (%d)' % (fmt(r[6]), fmt(r[7]), fmt(r[8]), r[9])
            L.append('|%s|%s|%d|%d|%s|%s|%s|%s|%s|%s|' % (meas, scheme, p[9], p[10], fmt(p[6]), ci(ce), ci(te), ci(c2), fmt(fs[6]),
                                                     '' if scheme == 'TT' else '%s (%d)' % (fmt(ms[6]), ms[9])))
        L.append('')
    with open(os.path.join(out_dir, 'REPORT3.md'), 'x') as f:
        f.write('\n'.join(L) + '\n')
