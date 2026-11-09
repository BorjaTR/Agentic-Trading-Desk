#!/usr/bin/env python3
"""agreement_v1.py (SCOUT 2026-11-08; why: team/RESEARCH/plans/PLAN_PROCESS_QUALITY_SYSTEM_20261108.md, fairness rule
"agreement is measured and must reach 0.80"). Agreement of 2 or more scorers on the same items.
Input: scorer TSVs with columns <unit cols...> and a points column (default: run, item, points). Rows whose item is TOTAL or
MESSY, or whose points are not numbers, are skipped. Units = the join of the unit columns.
Prints per scorer pair and overall: units, exact agreement, within-1 agreement, Krippendorff alpha (ordinal and interval),
and the units where scorers differ by more than --adjudicate points (they go to a third scorer).
Reading (content-analysis convention): alpha >= 0.80 reliable; 0.667-0.80 tentative; below 0.667 fix the scale first.
  python3 -B agreement_v1.py A.tsv B.tsv [--units run,item] [--points points] [--adjudicate 1] [--self-test]"""
import argparse, csv, itertools, sys
from collections import defaultdict

def alpha(units, level='ordinal'):
    """Krippendorff alpha; units = list of lists of numeric values (one list per unit, missing left out)."""
    units = [u for u in units if len(u) >= 2]
    vals = sorted({v for u in units for v in u})
    if len(vals) < 2: return float('nan')   # C218: one value only, alpha is undefined (was 1.0, printed RELIABLE)
    o = defaultdict(float)
    for u in units:
        m = len(u)
        for i, j in itertools.permutations(range(m), 2): o[(u[i], u[j])] += 1.0 / (m - 1)
    n_c = {c: sum(o[(c, k)] for k in vals) for c in vals}; n = sum(n_c.values())
    def d2(c, k):
        if level == 'interval': return (c - k) ** 2
        lo, hi = min(c, k), max(c, k)
        return (sum(n_c[g] for g in vals if lo <= g <= hi) - (n_c[c] + n_c[k]) / 2.0) ** 2
    Do = sum(o[(c, k)] * d2(c, k) for c in vals for k in vals) / n
    De = sum(n_c[c] * n_c[k] * d2(c, k) for c in vals for k in vals) / (n * (n - 1))
    return 1.0 - Do / De if De > 0 else 1.0

def load(path, ucols, pcol):
    out = {}
    for r in csv.DictReader(open(path), delimiter='\t'):
        if r.get('item', '') in ('TOTAL', 'MESSY') or r.get('run', '') == 'ALL': continue
        try: out[tuple(r[c] for c in ucols)] = float(r[pcol])
        except (TypeError, ValueError, KeyError): continue
    return out

def report(names, tables, adj):
    keys = sorted(set.intersection(*[set(t) for t in tables]))
    rows = [[t[k] for t in tables] for k in keys]
    if not rows: print('NO COMMON UNITS'); return 2
    ex = sum(1 for r in rows if max(r) == min(r)) / len(rows); w1 = sum(1 for r in rows if max(r) - min(r) <= 1) / len(rows)
    ao, ai = alpha(rows, 'ordinal'), alpha(rows, 'interval')
    word = 'NOT_COMPUTABLE' if ao != ao else ('RELIABLE' if ao >= 0.80 else ('TENTATIVE' if ao >= 0.667 else 'FIX_THE_SCALE'))   # C218: nan = one value
    fa = lambda x: 'n/a (one value)' if x != x else '%.3f' % x
    print('SCORERS %s | units %d | exact %.2f | within-1 %.2f | alpha ordinal %s | alpha interval %s | %s' % (','.join(names), len(rows), ex, w1, fa(ao), fa(ai), word))
    for k, r in zip(keys, rows):
        if max(r) - min(r) > adj: print('ADJUDICATE', '|'.join(k), r)
    by = defaultdict(list)
    for k, r in zip(keys, rows): by[k[-1]].append(r)
    for item, rr in sorted(by.items()):
        print('ITEM %s | units %d | exact %.2f | alpha ordinal %s' % (item, len(rr), sum(1 for r in rr if max(r) == min(r)) / len(rr),
              ('%.3f' % alpha(rr)) if len({v for r in rr for v in r}) > 1 else 'n/a (one value)'))
    return 0

def self_test():
    same = [[0, 0], [1, 1], [2, 2], [1, 1], [0, 0], [2, 2]]
    assert abs(alpha(same) - 1.0) < 1e-9, alpha(same)
    import random; rnd = random.Random(7)
    noise = [[rnd.choice([0, 1, 2]), rnd.choice([0, 1, 2])] for _ in range(400)]
    assert abs(alpha(noise)) < 0.15, alpha(noise)
    off = [[0, 1], [1, 1], [2, 2], [1, 2], [0, 0], [2, 2], [1, 1], [0, 0]]
    a = alpha(off); assert 0.3 < a < 0.95, a
    # published example (Krippendorff 2011, 'Computing Krippendorff's Alpha-Reliability', 4 observers x 12 units): ordinal 0.815, interval 0.849
    N = None; A = [1,2,3,3,2,1,4,1,2,N,N,N]; B = [1,2,3,3,2,2,4,1,2,5,N,3]; C = [N,3,3,3,2,3,4,2,2,5,1,N]; D = [1,2,3,3,2,4,4,1,2,5,1,N]
    k = [[x for x in col if x is not None] for col in zip(A, B, C, D)]
    assert abs(alpha(k, 'ordinal') - 0.815) < 0.0005 and abs(alpha(k, 'interval') - 0.849) < 0.0005, (alpha(k), alpha(k, 'interval'))
    print('SELF_TEST PASS same %.3f noise %.3f one-off %.3f' % (alpha(same), alpha(noise), a)); return 0

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='*'); ap.add_argument('--units', default='run,item')
    ap.add_argument('--points', default='points'); ap.add_argument('--adjudicate', type=float, default=1); ap.add_argument('--self-test', action='store_true')
    a = ap.parse_args(argv)
    if a.self_test: return self_test()
    if len(a.files) < 2: sys.exit('need 2 or more scorer files')
    uc = a.units.split(','); tabs = [load(f, uc, a.points) for f in a.files]
    return report([f.rsplit('/', 1)[-1] for f in a.files], tabs, a.adjudicate)

if __name__ == '__main__':
    sys.exit(main())
