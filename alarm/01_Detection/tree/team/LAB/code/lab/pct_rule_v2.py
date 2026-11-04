"""pct_rule_v2.py (EDGE1, 16 Oct 2026, DRAFT; tests test_pct_rule_v2.py PR1 to PR9, written first) = pct_rule_v1.py d68bd40a (its text below)
with BED's review of 17:50:42Z (EDGE2 seconded 17:57:58Z):
  REACH (BED's SMALL, overclaim on small bases): an edge is offered only when n x its tail share >= 1 (0.1 and 99.9 need n >= 1000 sizes,
         1 and 99 need 100, 5 and 95 need 20); a band without its edge merges with the next band toward the middle, which keeps its number:
         under 1,000 sizes a value above every size is band 23 'top 1%', never band 24; band 24 'top 0.1%' exists only from 1,000 sizes.
         edges_for(n); the cuts carry the edges they were made on (Cuts.edges); label(k, n) names a merged band ('top 1%', 'bottom 1%').
  FLOAT (BED's GAP 2): a float v is read as the card reads it, its shortest decimal form, so a raw float at a cut lands where the card puts it.
  GRID empty() (GAP 1): the bands of the cuts with no size; the TYPE stays the card's (type_of re-exported): it measures the metric on its
         fifths, and the daily checks that use it stay on the fifths grid.
pct_rule_v1's text:
THE LAB'S GRADE: THE FIFTHS CARD'S RULE ON THE OWNER'S GRID. Every rule is CARD_FIFTHS_V11's (code fifths_rule_v2.py 1057542b, imported):
the none value apart (rule 9), the sizes |v| (10), the floor (11), one value (12), equal sizes never split and a run placed by the middle
of its share (12b), each sign its own cuts with the pooled fallback (12c), a value graded by the smallest base size at or above it, above
every size the top, the minus kept (16). ONE CHANGE: the grid. A run whose middle of share is p percent takes the band of the first edge at
or above p. EDGES = 0.1, 1, 5, 10 .. 95, 99, 99.9, 100: 24 bands (1 = bottom 0.1%, 24 = top 0.1%, 0 = none, minus kept).
On the edges (20, 40, 60, 80, 100) every function answers exactly as fifths_rule_v2 (PR1)."""
from decimal import Decimal
from fractions import Fraction

import numpy as np

import fifths_rule_v2 as FR

EDGES = (Fraction(1, 10), 1, 5) + tuple(5 * k for k in range(2, 20)) + (99, Fraction(999, 10), 100)
type_of = FR.type_of


def _edges(edges):
    return tuple(e if isinstance(e, Fraction) else Fraction(e).limit_denominator(1000) for e in edges)


class Cuts(tuple):
    """the cuts (a tuple, equal to fifths_rule_v2's on its grid) and the edges they were made on, and the full grid they map to"""
    edges = None
    full = None


def edges_for(n, edges=EDGES):
    """REACH: the edges a base of n sizes can offer: an edge e < 50 needs n x e/100 >= 1, an edge e > 50 needs n x (100 - e)/100 >= 1"""
    E = _edges(edges)
    out = []
    for e in E:
        if e == 100:
            out.append(e)
        elif e < 50 and n * e / 100 < 1:
            continue
        elif e > 50 and n * (100 - e) / 100 < 1:
            continue
        else:
            out.append(e)
    return tuple(out)


def _bands(st, ln, n, edges):
    E = _edges(edges)
    assert all((10 * e).denominator == 1 for e in E), 'edges in tenths of a percent'
    T = np.array([2 * n * int(10 * e) for e in E], np.int64)
    x = 1000 * (2 * np.asarray(st, np.int64) + np.asarray(ln, np.int64))
    return np.searchsorted(T, x, side='left') + 1


def _to_full(k, used, full):
    """a band k of the used edges -> the band of the full grid: toward the middle (its upper edge below 50, its lower edge from 50)"""
    U, F = _edges(used), _edges(full)
    lo = U[k - 2] if k >= 2 else Fraction(0)
    hi = U[k - 1]
    if hi <= 50:
        return F.index(hi) + 1
    return F.index(lo) + 2 if lo > 0 else 1


def positions(sizes, edges=EDGES):
    n = len(sizes)
    st, ln = FR._runs(sizes)
    b = _bands(st, ln, n, edges)
    out = []
    for k in range(1, len(edges)):
        i = np.flatnonzero(b == k)
        out.append(FR.num(sizes[int(st[i[-1]])]) if len(i) else None)
    return tuple(out)


def cuts(sizes, min_count, n_none=0, signs=1, edges=EDGES):
    n = len(sizes)
    if n == 0 or n < min_count:
        return 'FEW_VALUES'
    if n_none == 0 and signs <= 1 and sizes[0] == sizes[n - 1]:
        return 'ONE_VALUE'
    used = edges_for(n, edges)
    c = Cuts(positions(sizes, used))
    c.edges, c.full = used, _edges(edges)
    return c


def grade(v, c, none, edges=None):
    """rule 16 on the grid: (band of the FULL grid or None, reason or None); a float read by its shortest decimal form"""
    if isinstance(v, float):
        v = Decimal(repr(v))
    if FR.is_none(v, none):
        return 0, None
    if isinstance(c, str):
        return None, c
    s = abs(v)
    g = len(c) + 1
    for k in range(1, len(c) + 1):
        if c[k - 1] is not None and s <= c[k - 1]:
            g = k
            break
    if getattr(c, 'edges', None) is not None:
        g = _to_full(g, c.edges, c.full)
    return (-g if v < 0 else g), None


def counts(sizes, edges=EDGES):
    """the base's sizes per band of the full grid (a merged band's sizes in the band it keeps)"""
    n = len(sizes)
    st, ln = FR._runs(sizes)
    used = edges_for(n, edges)
    b = _bands(st, ln, n, used)
    out = [0] * len(edges)
    for k in range(1, len(used) + 1):
        m = int(ln[b == k].sum())
        if m:
            out[_to_full(k, used, edges) - 1] += m
    return tuple(out)


def empty(c):
    """the bands of the cuts (as numbered in c) that hold no size"""
    if isinstance(c, str):
        return []
    return [k for k in range(1, len(c) + 1) if c[k - 1] is None]


def _side(sizes, min_count, n_none, pooled, edges):
    if len(sizes) < max(min_count, 1) or sizes[0] == sizes[len(sizes) - 1]:
        return pooled, FR.FALLBACK
    used = edges_for(len(sizes), edges)
    c = Cuts(positions(sizes, used))
    c.edges, c.full = used, _edges(edges)
    return c, None


def cuts_signed(neg, pos, min_count, n_none=0, edges=EDGES):
    allz = np.sort(np.concatenate((np.asarray(neg, dtype=np.float64), np.asarray(pos, dtype=np.float64)))) if (len(neg) or len(pos)) else np.zeros(0)
    pooled = cuts(allz, min_count, n_none, 2 if (len(neg) and len(pos)) else 1, edges)
    return pooled, _side(neg, min_count, n_none, pooled, edges), _side(pos, min_count, n_none, pooled, edges)


def grade_signed(v, cs, none):
    if isinstance(v, float):
        v = Decimal(repr(v))
    pooled, (mi, _), (pl, _) = cs
    if FR.is_none(v, none):
        return 0, None
    if v < 0:
        return grade(v, mi, none)
    if v > 0:
        return grade(v, pl, none)
    return grade(v, pooled, none)


def band_of(p, edges=EDGES):
    E = _edges(edges)
    p = Fraction(p).limit_denominator(1000)
    for k, e in enumerate(E):
        if p <= e:
            return k + 1
    return len(E)


def range_of(k, edges=EDGES, n=None):
    """band k's range of percent; with n, a band merged by REACH reports its merged range"""
    F = _edges(edges)
    k = abs(int(k))
    lo, hi = (F[k - 2] if k >= 2 else Fraction(0)), F[k - 1]
    if n is not None:
        U = edges_for(n, edges)
        if hi <= 50:
            lo = max([e for e in U if e < hi], default=Fraction(0))
        else:
            hi = min([e for e in U if e > lo])
    f = lambda x: int(x) if x.denominator == 1 else float(x)
    return f(lo), f(hi)


def label(k, edges=EDGES, n=None):
    if k == 0:
        return 'none'
    lo, hi = range_of(k, edges, n)
    if hi == 100:
        t = 'top %g%%' % (100 - lo)
    elif lo == 0:
        t = 'bottom %g%%' % hi
    else:
        t = '%g to %g%%' % (lo, hi)
    return t + (', minus' if k < 0 else '')
