#!/usr/bin/env python3
"""wave_gap_v1.py (SCOUT, 2 Nov 2026, V1_18_FIXES; why: RESULTS_R5 item 5): why COUNT's waves exceed the graded (LEAD) waves, from a GRADE's own files.
A COUNT wave is kept by lead_null only when one of its fires has a non-own matched edge (a random moment) and a finite outcome. Reads <W>/PERFIRE_<V>.tsv,
<W>/gradeL_<V>_v1/matches/{EDGES,CENSUS}.tsv and REAL_<V>.tsv; writes nothing; market files none. Exit 0 equal to REAL, 3 not equal, 2 refused.
  $PY -B wave_gap_v1.py <W> <V> --real <RUN>/receipts/<GRADE>/HANDOFF/REAL_SEALED/REAL_<V>.tsv"""
import argparse, collections, csv, os, sys


def table(p):
    if not os.path.isfile(p):
        print('REFUSED: NO FILE %s' % p, file=sys.stderr); sys.exit(2)
    with open(p, newline='') as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def fin(r):
    ok = lambda x: x not in ('', 'nan', 'NaN')
    return any(ok(r['FADE ' + h]) and ok(r['FOLLOW ' + h]) for h in ('15m', '1h'))


def kept(keyed, edges):
    return any(k in edges and fin(x) for x, k in keyed)


def reason(keyed, edges, own, census):
    """why a dropped wave is dropped: the first cause, in the order of the chain"""
    st = [census.get(k, '-') for _, k in keyed]
    if any(k in edges for _, k in keyed):
        return 'NO_OUTCOME'
    if any(k in own for _, k in keyed):
        return 'ONLY_OWN_EDGES'
    return collections.Counter(st).most_common(1)[0][0]


def main(a=None):
    ap = argparse.ArgumentParser(); ap.add_argument('W'); ap.add_argument('V'); ap.add_argument('--real', required=True)
    o = ap.parse_args(a); m = os.path.join(o.W, 'gradeL_%s_v1' % o.V, 'matches')
    rows = sorted((r for r in table(os.path.join(o.W, 'PERFIRE_%s.tsv' % o.V)) if r['kind'] == 'A'), key=lambda r: int(r['t']))
    edges, own = set(), set()
    for r in table(os.path.join(m, 'EDGES.tsv')):
        if not r['own']:
            edges.add(r['fid'])
        else:
            own.add(r['fid'])
    census = {r['fid']: r['status'] for r in table(os.path.join(m, 'CENSUS.tsv'))}
    real = [r for r in table(o.real) if r.get('horizon') == '15m']
    if not real:
        print('REFUSED: NO 15m ROW IN %s' % o.real, file=sys.stderr); return 2
    wv = collections.OrderedDict()
    for r in rows:
        wv.setdefault(r['wave'], []).append((r, r['coin'] + '_' + r['t']))
    cnt, lead, drop, why = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for keyed in wv.values():
        mth = keyed[0][0]['month']
        cnt[mth] += 1
        if kept(keyed, edges):
            lead[mth] += 1
        else:
            drop[mth] += 1; why[reason(keyed, edges, own, census)] += 1
    fires = collections.Counter(census.get(k, '-') for keyed in wv.values() for _, k in keyed)
    print('WAVES count %d lead %d dropped %d (%.1f pct of count); fires %d' % (sum(cnt.values()), sum(lead.values()), sum(drop.values()), 100.0 * sum(drop.values()) / max(sum(cnt.values()), 1), len(rows)))
    for x in sorted(cnt):
        print('MONTH %s count %d lead %d dropped %d' % (x, cnt[x], lead[x], drop[x]))
    print('REASONS ' + ' '.join('%s %d' % kv for kv in why.most_common()))
    print('FIRES CENSUS ' + ' '.join('%s %d' % kv for kv in fires.most_common()))
    mon = sorted(c[6:] for c in real[0] if c.startswith('waves_'))
    bad = [x for x in mon if str(lead[x]) != real[0]['waves_' + x]]
    print('REAL %s months %s' % ('NOT EQUAL at ' + ','.join(bad) if bad else 'EQUAL', ','.join(mon)))
    return 3 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
