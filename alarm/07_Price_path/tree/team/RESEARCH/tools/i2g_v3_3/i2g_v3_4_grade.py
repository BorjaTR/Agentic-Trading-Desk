"""i2g_v3_4_grade.py (idea_to_grade V3.4, grader thread, 26 Oct 2026): Step B of SCOPE_ARCH_I2G_V3_4_V1.md section 4.
Per label set: every group's rows of V3.2's table, from the Step A vectors, in ONE pass. A group is a subset of the parents with their
FROZEN weights and clusters, sliced as V3.2 slices (ALL, then each calendar month present among the group's parents). The statistic is
V3.2's i2g_rules_v1_2.clustered_mean (weighted mean, 95% interval with the cluster as the unit, G / (G - 1) correction, 1.96), computed
for all groups and slices at once with np.bincount. The row order inside a group is V3.2's (direction, measure, scheme, cost, slice,
stat). Equal to V3.2's grade within |a - b| <= 1e-12 x max(1, |b|); grade_exact is the reference path (V3.2's grade per group).
No alarm, coin, field, state or date is held here."""
import math
import numpy as np
import i2g_grade3_v3_2_1 as G3

TOL = 1e-12


def _cells(gid, n_groups, month_of, n_months):
    """membership of every parent in its group's ALL cell and its group's month cell -> (parent index, cell) arrays"""
    ix = np.flatnonzero(gid >= 0)
    g = gid[ix]
    return np.concatenate([ix, ix]), np.concatenate([g, n_groups + g * n_months + month_of[ix]])


def clustered_means(v, w, cc, ip, cell, kinv, key_cell, n_cells, n_keys):
    """clustered_mean of v for every cell at once -> (mean, lo, hi, parents, clusters) arrays over the cells"""
    vv = v[ip]; ww = w[ip]
    ok = np.isfinite(vv) & np.isfinite(ww) & (ww > 0)
    c = cell[ok]; vv = vv[ok]; ww = ww[ok]; kk = kinv[ok]
    W = np.bincount(c, ww, minlength=n_cells)
    S = np.bincount(c, ww * vv, minlength=n_cells)
    npar = np.bincount(c, minlength=n_cells)
    m = np.full(n_cells, np.nan)
    has = npar > 0
    m[has] = S[has] / W[has]
    u = np.bincount(kk, ww * (vv - m[c]), minlength=n_keys)
    nk = np.bincount(kk, minlength=n_keys)
    G = np.bincount(key_cell[nk > 0], minlength=n_cells)
    U2 = np.bincount(key_cell, u * u, minlength=n_cells)
    lo = np.full(n_cells, np.nan); hi = np.full(n_cells, np.nan)
    two = G >= 2
    se = np.sqrt(G[two] / (G[two] - 1.0) * U2[two]) / W[two]
    lo[two] = m[two] - 1.96 * se; hi[two] = m[two] + 1.96 * se
    return m, lo, hi, npar, G


def grade_groups(blocks, gid, n_groups, days, weights, clusters, slices=None):
    """blocks: Step A output; gid: per parent its group number (0 .. n_groups - 1, or -1 for none); days: per parent YYYYMMDD;
    weights, clusters: per parent (frozen); slices: None = ALL and every month, or the slice names to keep
    -> per group the list of V3.2 table rows (G3.COLS order)"""
    gid = np.asarray(gid, np.int64)
    months = sorted({d[:6] for d in days})
    mpos = {m: i for i, m in enumerate(months)}
    month_of = np.asarray([mpos[d[:6]] for d in days], np.int64)
    nm = max(len(months), 1)
    n_cells = n_groups + n_groups * nm
    ip, cell = _cells(gid, n_groups, month_of, nm)
    cl_code = {c: i for i, c in enumerate(sorted(set(clusters)))}
    cc = np.asarray([cl_code[c] for c in clusters], np.int64)
    key = cell * len(cl_code) + cc[ip]
    ukey, kinv = np.unique(key, return_inverse=True)
    key_cell = ukey // len(cl_code)
    w = np.asarray(weights, float)
    keep = None if slices is None else set(slices)
    present = {}                                      # the months a group has parents in (V3.2 builds its slices from them)
    for g, mo in set(zip(gid[gid >= 0].tolist(), month_of[gid >= 0].tolist())):
        present.setdefault(g, set()).add(mo)
    plan = []
    for g in range(n_groups):
        sl = [('ALL', g)] + [(months[mo], n_groups + g * nm + mo) for mo in sorted(present.get(g, ()))]
        plan.append([x for x in sl if keep is None or x[0] in keep])
    rows = [[] for _ in range(n_groups)]
    for d, meas, scheme, cname, vals in blocks:
        res = {st: clustered_means(vals[st], w, cc, ip, cell, kinv, key_cell, n_cells, len(ukey)) for st in G3.STATS}
        for g in range(n_groups):
            out = rows[g]
            for sname, ci in plan[g]:
                for st in G3.STATS:
                    m, lo, hi, npar, G = res[st]
                    if npar[ci] == 0:
                        out.append((sname, d, meas, scheme, cname, st, np.nan, np.nan, np.nan, 0, 0))
                    else:
                        out.append((sname, d, meas, scheme, cname, st, float(m[ci]), float(lo[ci]), float(hi[ci]), int(npar[ci]),
                                    int(G[ci])))
    return rows


def grade_exact(parents, names3, V3, row_coin, calm, calm_v2, tough, weights, clusters, legs, ix, slices=None):
    """the reference path: V3.2's own grade on the parents ix (as V3.3.2 grades a group)"""
    pick = lambda xs: [xs[i] for i in ix]
    return G3.grade(pick(parents), names3, V3, row_coin, {d: pick(calm[d]) for d in calm}, {d: pick(calm_v2[d]) for d in calm_v2},
                    {d: pick(tough[d]) for d in tough}, pick(weights), pick(clusters), legs, slices=slices)


def same_rows(a, b, tol=TOL):
    """the release rule: the same keys in the same order, parents and clusters equal, mean, lo and hi within tol x max(1, |b|)
    (NaN equal to NaN) -> [first difference] or []"""
    if len(a) != len(b):
        return ['row count %d vs %d' % (len(a), len(b))]
    for i, (x, y) in enumerate(zip(a, b)):
        if x[:6] != y[:6] or x[9:] != y[9:]:
            return ['row %d: %s vs %s' % (i, x, y)]
        for j in (6, 7, 8):
            p, q = x[j], y[j]
            if math.isnan(p) and math.isnan(q):
                continue
            if math.isnan(p) != math.isnan(q) or abs(p - q) > tol * max(1.0, abs(q)):
                return ['row %d col %d: %r vs %r' % (i, j, p, q)]
    return []
