"""check_fl12_v1.py (SCOUT 2 Nov 2026): the real-data checks of edition 12, inside its job. why: plans/PLAN_FL12_PERCOIN_BAR_20261102.md.
 bars <out.tsv> <lab_days> <lab3 code> <moment code dir> <first> <last> <BAR dir> <n> : n moments, seeded, recomputed apart from bar_v1: lab3 reads here, moment_v1's hourly_peaks and own_line, the
   cost at the moment's own 5 s column (bar_v1 reads the hour's first); every one must equal bar_v1's table. Exit 3 on a difference.
 path <out.tsv> <receipts dir> [...] : on every A and R table: BEST_60M either way >= 4 unit__c against |OBH4_60M| = 1, rows with both values. Exit 3 on a difference.
 same <out.tsv> <old dir> <new dir> : every .tsv of the old folder byte equal in the new one. Exit 3 on a difference.
 side <out.tsv> <old FAIR_RUNS> <new FAIR_RUNS> : SIDE rows equal, text by text. Exit 3 on a difference.
 labels <out.tsv> <FL_RULE9.tsv> <FL_RULE12.tsv> : every label against FL_RULE9, changes marked."""
import csv, gzip, hashlib, os, sys
import numpy as np

csv.field_size_limit(10 ** 7)


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def bars(a):
    out, lab, code, mdir, first, last, bdir, n = a[0], a[1], a[2], a[3], a[4], a[5], a[6], int(a[7])
    sys.path.insert(0, code); sys.path.insert(0, mdir)
    from lab3 import days as LD
    import moment_v1 as MV, calendar
    R = LD.Days(lab, 'research'); st = lambda d: calendar.timegm((int(d[:4]), int(d[4:6]), int(d[6:]), 0, 0, 0)); t0 = st(first); nd = (st(last) - t0) // 86400 + 1
    days = [''.join(str(np.datetime64(t0 + k * 86400, 's').astype('datetime64[D]')).split('-')) for k in range(nd)]
    rows = []
    for fn in sorted(os.listdir(bdir)):
        if fn.startswith('BAR_') and fn.endswith('.tsv.gz'):
            with gzip.open(os.path.join(bdir, fn), 'rt') as f:
                rd = csv.DictReader(f, delimiter='\t')
                rows += [dict(r, file=fn) for r in rd]
    rng = np.random.default_rng(12); pick = [rows[i] for i in rng.choice(len(rows), min(n, len(rows)), replace=False)]
    coins = sorted({r['coin'] for r in pick}); M = {c: np.full(nd * 1440, np.nan) for c in coins}
    for k, d in enumerate(days):
        have = {str(c) for c in R.index(d, 'PRICE')['coins']}; cs = [c for c in coins if c in have]
        if cs:
            v = R.read('C13.S05', 'v', [d], cs)[0].astype(float)
            for i, c in enumerate(cs):
                M[c][k * 1440:(k + 1) * 1440] = v[i]
    hp = {c: MV.hourly_peaks(M[c], 1.0, 60) for c in coins}; bad = 0
    with open(out, 'x') as f:
        f.write('file\tcoin\tt\tbar_table\tbar_check\tline_table\tline_check\tcost_table\tcost_check\twhy\tok\n')
        for r in pick:
            c = r['coin']; t = int(r['t']); tmin = (t - t0) / 60.0; clock = int(np.ceil(tmin)) - 1
            ln = MV.own_line(hp[c][0], hp[c][1], clock, 87, 14, 303) * 100.0; d = days[(t - t0) // 86400]; col = (t - st(d)) // 5
            try:
                x = [R.read('X1.COST.S%02d' % q, 'v', [d], [c])[0].astype(float)[0, col] for q in (6, 8, 10, 11)]
            except (LD.NotBuilt, KeyError, ValueError):
                x = [np.nan] * 4
            cost = (9 + x[0] + x[1] + 3.2) / 100.0 if np.isfinite(x[0]) and np.isfinite(x[1]) and not (x[2] > 0.5 or x[3] > 0.5) else np.nan
            b = max(6 * cost, ln) if np.isfinite(cost) and np.isfinite(ln) else np.nan
            num = lambda s: float(s) if s != '' else np.nan
            eq = lambda u, w: (np.isnan(u) and np.isnan(w)) or abs(u - w) <= 1e-9 * max(1.0, abs(w))
            ok = eq(num(r['bar_pct']), b) and eq(num(r['line_pct']), ln) and eq(num(r['cost_pct']), cost); bad += not ok
            f.write('%s\t%s\t%d\t%s\t%.12g\t%s\t%.12g\t%s\t%.12g\t%s\t%d\n' % (r['file'], c, t, r['bar_pct'], b, r['line_pct'], ln, r['cost_pct'], cost, r['why'], ok))
    print('BARS checked %d, different %d' % (len(pick), bad))
    return 3 if bad else 0


def path(a):
    out = a[0]; tot = {'both': 0, 'diff': 0, 'best_only': 0, 'obh_only': 0, 'tables': 0}
    with open(out, 'x') as o:
        o.write('table\trows\tboth\tdifferent\tbest_only\tobh_only\n')
        for d in a[1:]:
            for fn in sorted(os.listdir(d)):
                if not (fn.endswith('.tsv.gz') and fn[0] in 'AR' and fn[1] == 'T'):
                    continue
                with gzip.open(os.path.join(d, fn), 'rt') as f:
                    rd = csv.DictReader(f, delimiter='\t'); n = b = x = bo = oo = 0
                    for r in rd:
                        n += 1; u, v, c, q = r['BEST_60M__FADE'], r['BEST_60M__FOLLOW'], r['unit__c'], r['OBH4_60M__FADE']
                        hv = u != '' and v != '' and c != ''; hq = q != ''
                        if hv and hq:
                            b += 1; x += (max(float(u), float(v)) >= 4 * float(c) - 1e-12) != (abs(float(q)) == 1)
                        elif hv:
                            bo += 1
                        elif hq:
                            oo += 1
                o.write('%s\t%d\t%d\t%d\t%d\t%d\n' % (fn, n, b, x, bo, oo)); tot['both'] += b; tot['diff'] += x; tot['best_only'] += bo; tot['obh_only'] += oo; tot['tables'] += 1
    print('PATH %s' % tot)
    return 3 if tot['diff'] else 0


def same(a):
    out, old, new = a; bad = n = 0
    with open(out, 'x') as o:
        o.write('file\told\tnew\tsame\n')
        for fn in sorted(os.listdir(old)):
            if fn.endswith('.tsv'):
                p = os.path.join(new, fn); x, y = s16(os.path.join(old, fn)), s16(p) if os.path.isfile(p) else 'MISSING'; n += 1; bad += x != y
                o.write('%s\t%s\t%s\t%d\n' % (fn, x, y, x == y))
    print('SAME %s: %d tables, different %d' % (new, n, bad))
    return 3 if bad or not n else 0


def side(a):
    out, old, new = a
    rd = lambda p: {(r['code'], r['kind'], r['plant'], r['seed'], r['period']): r for r in csv.DictReader(open(p), delimiter='\t') if r['bar'] == 'SIDE'}
    x, y = rd(old), rd(new); bad = [k for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k)]
    with open(out, 'x') as o:
        o.write('SIDE rows old %d new %d different %d\n' % (len(x), len(y), len(bad)))
        for k in bad[:50]:
            o.write('%s\n' % (k,))
    print('SIDE rows old %d new %d different %d' % (len(x), len(y), len(bad)))
    return 3 if bad or not x else 0


def labels(a):
    out, oldp, newp = a
    x = {r['alarm_id']: r for r in csv.DictReader(open(oldp), delimiter='\t')}; y = list(csv.DictReader(open(newp), delimiter='\t')); nc = 0
    with open(out, 'x') as o:
        o.write('alarm_id\tcode\tRULE_9\tRULE_12\tchanged\tSIZE_SepDec_z\tSIZE_JanApr_z\tSIZE11_SepDec_z\tSIZE11_JanApr_z\tSIZE_SepDec_months\tSIZE_JanApr_months\tSIZE_SepDec_pts\tSIZE_JanApr_pts\tSIZE_SepDec_fail\tSIZE_JanApr_fail\n')
        for r in y:
            old = x.get(r['alarm_id'], {}).get('RULE_9', '-'); ch = int(old != r['RULE_12']); nc += ch
            o.write('\t'.join([r['alarm_id'], r['code'], old, r['RULE_12'], str(ch)] + [r[k] for k in ('SIZE_SepDec_z', 'SIZE_JanApr_z', 'SIZE11_SepDec_z', 'SIZE11_JanApr_z', 'SIZE_SepDec_months', 'SIZE_JanApr_months', 'SIZE_SepDec_pts', 'SIZE_JanApr_pts', 'SIZE_SepDec_fail', 'SIZE_JanApr_fail')]) + '\n')
    print('LABELS %d rows, %d changed' % (len(y), nc))
    return 0


if __name__ == '__main__':
    sys.exit({'bars': bars, 'path': path, 'same': same, 'side': side, 'labels': labels}[sys.argv[1]](sys.argv[2:]))
