"""i2g_v3_4_vectors.py (idea_to_grade V3.4, grader thread, 26 Oct 2026): Step A of SCOPE_ARCH_I2G_V3_4_V1.md section 4.
Once per store: the per-parent values that V3.2.1's grade (i2g_grade3_v3_2_1.grade, imported, never copied) builds before it slices, for
every direction, measure, scheme and cost. None of them depends on the grouping: a parent's calm and tough lists are its own. The calm and
tough means follow base_means and tough_means exactly, as array sums (bincount) instead of a loop per parent; the sums add in another
order, so they equal V3.2's to the release tolerance (1e-12 relative), not bit for bit (the owner's ruling 2, 26 Oct 11:46Z).
No alarm, coin, field, state or date is held here."""
import numpy as np
import i2g_grade3_v3_2_1 as G3
import i2g_rules_v1_2 as RU

DIRECTIONS = ('FOLLOW', 'FADE')


def _flat(groups, weighted):
    """per parent lists -> (parent index, row[, weight]) arrays"""
    p, r, w = [], [], []
    for i, g in enumerate(groups):
        for e in g:
            p.append(i)
            if weighted:
                r.append(e[0]); w.append(e[1])
            else:
                r.append(e)
    p = np.asarray(p, np.int64); r = np.asarray(r, np.int64)
    return (p, r, np.asarray(w, float)) if weighted else (p, r)


def base_means(x, flat, n):
    """= G3.base_means(x, groups): per parent the weighted mean of the finite x over its (row, weight) list, NaN when none is finite"""
    p, r, w = flat
    v = x[r]; ok = np.isfinite(v)
    num = np.bincount(p[ok], w[ok] * v[ok], minlength=n); den = np.bincount(p[ok], w[ok], minlength=n)
    has = np.bincount(p[ok], minlength=n) > 0
    out = np.full(n, np.nan)
    with np.errstate(divide='ignore', invalid='ignore'):
        out[has] = num[has] / den[has]
    return out


def tough_means(x, flat, n, min_n):
    """= G3.tough_means(x, groups, min_n): the plain mean of the finite x over the parent's tough rows, when at least min_n are finite"""
    p, r = flat
    v = x[r]; ok = np.isfinite(v)
    s = np.bincount(p[ok], v[ok], minlength=n); k = np.bincount(p[ok], minlength=n)
    out = np.full(n, np.nan)
    good = k >= min_n
    out[good] = s[good] / k[good]
    return out


def parent_vectors(parents, names3, V3, row_coin, calm, calm_v2, tough, legs_by_coin):
    """-> [(direction, measure, scheme, cost, {stat: per-parent vector})] in V3.2's row order (direction, measure and scheme of
    G3.measures(), cost GROSS then the sorted cost names); the stat vectors are V3.2's vals before a slice index is applied"""
    col = {n: i for i, n in enumerate(names3)}
    n = len(parents)
    legs = {cn: (np.asarray([L[c][0] for c in row_coin], float), np.asarray([L[c][1] for c in row_coin], float))
            for cn, L in legs_by_coin.items()}
    out = []
    for d in DIRECTIONS:
        prow = np.asarray([p['row_ids'][d] for p in parents], np.int64)
        fc, fc2, ft = _flat(calm[d], True), _flat(calm_v2[d], True), _flat(tough[d], False)
        for meas, scheme, vcol, ccol in G3.measures():
            g = np.asarray(V3[:, col[vcol]], float); code = np.asarray(V3[:, col[ccol]], float) if ccol else None
            fill = np.asarray(V3[:, col['rs_filled'] if scheme in ('RT', 'RR') else col['tk_filled']], float)
            for cname in ['GROSS'] + sorted(legs):
                x = g if cname == 'GROSS' else G3.net(g, scheme, code, legs[cname])
                if cname != 'GROSS':      # V3.2.1: NO_COST rows (taker leg NaN) are unknown in every net row
                    x = np.where(np.isfinite(legs[cname][0]), x, np.nan)
                if scheme == 'TT':
                    XT = np.full(n, np.nan)
                else:
                    gt = np.asarray(V3[:, col['tk_' + meas]], float)
                    XT = (gt if cname == 'GROSS' else G3.net(gt, 'TT', None, legs[cname]))[prow]
                X = x[prow]; C = base_means(x, fc, n); T = tough_means(x, ft, n, RU.TOUGH['min_n']); C2 = base_means(x, fc2, n)
                F = fill[prow] if cname == 'GROSS' else np.where(np.isfinite(legs[cname][0][prow]), fill[prow], np.nan)
                known = np.isfinite(X)
                vals = {'PARENT': X, 'CALM': np.where(known, C, np.nan), 'TOUGH': np.where(known, T, np.nan), 'CALM_EDGE': X - C,
                        'TOUGH_EDGE': X - T, 'CALM_V2_EDGE': X - C2, 'FILL_SHARE': F, 'MISSED_TT': np.where(F == 0, XT, np.nan)}
                out.append((d, meas, scheme, cname, vals))
    return out
