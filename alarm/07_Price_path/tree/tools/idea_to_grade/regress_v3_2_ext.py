"""regress_v3_2_ext.py (idea_to_grade V3.2, ALARMLIB seat, 26 Oct 2026): the real-data regression cases of
team/OUTSIDE/DATA/REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1.md, read from two COMPLETE full-population runs of one stored alarm list (no producer,
no detector; both runs read only): the stored V3.1 run and a V3.2 run of the same command (full_population_v3_2.sh).
  B1  net FILL_SHARE without NO_COST parents. Oracle from files (OBSERVATIONS.tsv, VALUES3.npy, WEIGHTS.tsv, NO_COST.tsv) and
      i2g_rules_v1_2.clustered_mean: on the V3.1 values the ALL/FOLLOW/RR/HONEST fill share must be the report's corrected
      0.9415227198170552 over 10,745 parents and 1,428 clusters; on the V3.2 values the oracle must equal every net FILL_SHARE row of the
      V3.2 TABLE.tsv (ALL, both directions, RT and RR, HONEST and STRESS), and no NO_COST parent may be counted there.
  B2  a resting entry whose decision price is older than 60 s is NO_PRICE: observation 147181 (a VVV FADE control) had rs_filled 1 and
      rs_wait_s 8.999 in V3.1 and must be unknown (NaN) in V3.2.
  U   unaffected numbers unchanged: every VALUES3 column outside the resting entry (rs_*, re_*, rb_*, path_holes) is identical bit for
      bit; resting values change only on rows whose V3.2 resting entry is NO_PRICE; every TABLE.tsv row of the taker scheme TT other
      than a net FILL_SHARE row is identical as text; OBSERVATIONS.tsv and WEIGHTS.tsv are identical.
  python3 -B regress_v3_2_ext.py <V3.1 run folder> <V3.2 run folder>      -> one line per check, exit 1 on any FAIL"""
import csv, hashlib, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import i2g_rules_v1_2 as RU

B1_WANT = (0.9415227198170552, 10745, 1428)
B2_OBS = 147181
RESTING = lambda n: n.startswith(('rs_', 're_', 'rb_')) or n == 'path_holes'
bad = []


def check(name, ok, detail):
    print('%s %s: %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        bad.append(name)


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def tsv(p):
    with open(p) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def load(run):
    names = json.load(open(os.path.join(run, 'measurements', 'NAMES3.json')))
    V = np.load(os.path.join(run, 'measurements', 'VALUES3.npy'))
    obs = tsv(os.path.join(run, 'measurements', 'OBSERVATIONS.tsv'))
    W = tsv(os.path.join(run, 'grade3', 'WEIGHTS.tsv'))
    nc = {r['parent_id'] for r in tsv(os.path.join(run, 'grade3', 'NO_COST.tsv'))}
    with open(os.path.join(run, 'grade3', 'TABLE.tsv')) as f:
        lines = f.read().split('\n')
    cols = lines[0].split('\t')
    table = {tuple(l.split('\t')[:6]): l for l in lines[1:] if l}
    return dict(names=names, V=V, obs=obs, W=W, nc=nc, cols=cols, table=table)


def parent_rows(R, direction):
    """the observation row of every parent (WEIGHTS.tsv order = the grading order) for one direction: kind parent, the parent's coin,
    second and side (a parent row keeps the parent's side in both directions)"""
    by = {}
    for o in R['obs']:
        if o['kind'] == 'parent' and o['direction'] == direction:
            by.setdefault((o['coin'], int(o['as_of_us']) // RU.US, int(o['side'])), []).append(int(o['row']))
    rows = []
    for w in R['W']:
        coin, t, side = w['parent_id'].rsplit('_', 2)
        got = by.get((coin, int(t), int(side)), [])
        if len(got) != 1:
            raise SystemExit('parent %s %s: %d observation rows' % (w['parent_id'], direction, len(got)))
        rows.append(got[0])
    return np.asarray(rows, np.int64)


def oracle_fill(R, direction):
    rows = parent_rows(R, direction)
    F = R['V'][rows, R['names'].index('rs_filled')].astype(float)
    F = np.where([w['parent_id'] in R['nc'] for w in R['W']], np.nan, F)
    w = np.asarray([float(x['weight']) for x in R['W']]); cl = np.asarray([x['cluster_id'] for x in R['W']], dtype=object)
    return RU.clustered_mean(F, w, cl)


def main(r1, r2):
    A, B = load(r1), load(r2)
    print('V3.1 run %s\nV3.2 run %s' % (r1, r2))
    check('U same observations', sha16(os.path.join(r1, 'measurements', 'OBSERVATIONS.tsv')) == sha16(os.path.join(r2, 'measurements', 'OBSERVATIONS.tsv')),
          'OBSERVATIONS.tsv %d rows' % len(A['obs']))
    check('U same weights', sha16(os.path.join(r1, 'grade3', 'WEIGHTS.tsv')) == sha16(os.path.join(r2, 'grade3', 'WEIGHTS.tsv')),
          'WEIGHTS.tsv %d parents' % len(A['W']))
    check('U same columns', A['names'] == B['names'] and A['V'].shape == B['V'].shape, 'VALUES3 %s' % (B['V'].shape,))
    # B1 the report's corrected number on the V3.1 values (the fix-1 rule alone), then the V3.2 table against the oracle
    o = oracle_fill(A, 'FOLLOW')
    check('B1 report case on V3.1 values', abs(o['mean'] - B1_WANT[0]) < 1e-12 and (o['parents'], o['clusters']) == B1_WANT[1:],
          'ALL/FOLLOW/RR/HONEST FILL_SHARE %r over %d parents, %d clusters (report: %r, %d, %d)' % ((o['mean'], o['parents'], o['clusters']) + B1_WANT))
    old = A['table'].get(('ALL', 'FOLLOW', 'V1_15m', 'RR', 'HONEST', 'FILL_SHARE'))
    print('     V3.1 stored row (wrong): %s' % old)
    for d in ('FOLLOW', 'FADE'):
        o2 = oracle_fill(B, d); n = 0; worst = 0.0
        for k, l in B['table'].items():
            if k[0] == 'ALL' and k[1] == d and k[3] in ('RT', 'RR') and k[4] in ('HONEST', 'STRESS') and k[5] == 'FILL_SHARE':
                v = l.split('\t'); n += 1
                worst = max(worst, abs(float(v[6]) - o2['mean']))
                if (int(v[9]), int(v[10])) != (o2['parents'], o2['clusters']):
                    worst = float('inf')
        check('B1 V3.2 table equals the oracle %s' % d, n > 0 and worst < 5e-6,
              '%d net resting FILL_SHARE rows; oracle %r over %d parents (table is printed to 6 digits; largest gap %.2g)'
              % (n, o2['mean'], o2['parents'], worst))
    print('     NO_COST parents: %d' % len(B['nc']))
    # B2
    nm = B['names']; ob = B['obs'][B2_OBS]
    a = A['V'][B2_OBS, nm.index('rs_filled')], A['V'][B2_OBS, nm.index('rs_wait_s')]
    b = B['V'][B2_OBS, nm.index('rs_filled')], B['V'][B2_OBS, nm.index('rs_wait_s')]
    check('B2 report case', ob['coin'] == 'VVV' and ob['kind'] == 'control' and ob['direction'] == 'FADE' and a[0] == 1.0
          and abs(a[1] - 8.999) < 1e-3 and np.isnan(b[0]) and np.isnan(b[1]),
          'observation %d %s %s %s as_of %s: V3.1 rs_filled %r wait %r -> V3.2 %r wait %r'
          % (B2_OBS, ob['coin'], ob['kind'], ob['direction'], ob['as_of_us'], a[0], a[1], b[0], b[1]))
    # U values
    same = lambda x, y: (x == y) | (np.isnan(x) & np.isnan(y))
    outside = [i for i, n in enumerate(nm) if not RESTING(n)]
    eq = same(A['V'][:, outside], B['V'][:, outside])
    check('U values outside the resting entry identical', bool(eq.all()), '%d columns x %d rows, %d cells differ'
          % (len(outside), len(B['V']), int((~eq).sum())))
    inside = [i for i, n in enumerate(nm) if RESTING(n)]
    rowdiff = ~same(A['V'][:, inside], B['V'][:, inside]).all(axis=1)
    nop = np.isnan(B['V'][:, nm.index('rs_filled')]) & ~np.isnan(A['V'][:, nm.index('rs_filled')])
    was = A['V'][nop, nm.index('rs_filled')]
    check('U resting values change only on the new NO_PRICE rows', bool(np.array_equal(rowdiff, nop)) and bool(np.isnan(A['V'][:, nm.index('rs_filled')][~np.isnan(B['V'][:, nm.index('rs_filled')])]).sum() == 0),
          '%d rows changed, %d now NO_PRICE (V3.1 had %d of them FILLED, %d UNFILLED); no row gained a price'
          % (int(rowdiff.sum()), int(nop.sum()), int((was == 1).sum()), int((was == 0).sum())))
    # U table
    tt = [k for k in A['table'] if k[3] == 'TT' and not (k[5] == 'FILL_SHARE' and k[4] != 'GROSS')]
    diff = [k for k in tt if A['table'][k] != B['table'].get(k)]
    check('U taker rows identical', not diff and set(A['table']) == set(B['table']), '%d TT rows compared as text, %d differ%s'
          % (len(tt), len(diff), (': ' + ' '.join('/'.join(k) for k in diff[:5])) if diff else ''))
    ch = [k for k in A['table'] if A['table'][k] != B['table'].get(k)]
    kinds = {}
    for k in ch:
        key = 'net FILL_SHARE' if k[5] == 'FILL_SHARE' and k[4] != 'GROSS' else 'resting %s' % k[3]
        kinds[key] = kinds.get(key, 0) + 1
    print('INFO table rows changed: %d of %d (%s)' % (len(ch), len(A['table']), ', '.join('%s %d' % kv for kv in sorted(kinds.items()))))
    print('%s: %d checks failed' % ('REGRESSION FAILED' if bad else 'REGRESSION PASSED', len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
