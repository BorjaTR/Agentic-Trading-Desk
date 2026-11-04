"""fl_read_v12.py (SCOUT 2 Nov 2026, tools/alarm_first_look). TEST, NOT REVIEWED. why: team/RESEARCH/plans/PLAN_FL12_PERCOIN_BAR_20261102.md.
First look edition 12 = edition 11 (fl_read_v11.py, imported and run UNCHANGED, every table it writes stays byte for byte) + one more
reading of the SIZE bar: price moves either way within 1 h by at least the moment's own B (bar_v1.py: the larger of 6 dated costs and the
coin's own top 13 pct 1 h move over the previous 14 days, known at the moment). the owner, from STRATEGY's plan, 2 Nov 2026. SIDE is edition
11's; edition 11's SIZE on the fixed table is printed beside; RULE_12 = overall8(SIZE at B, SIDE).
The hit comes from the first look's own stored path values (hit_b): BEST_<h>M__FADE and __FOLLOW at the windows up to 60 min, pct of the
price from the entry close, 3 s closes of Binance's model price: HIT when one reaches B (a crossing seen before a later gap counts); MISS
when BEST_60M has both values under B; else unknown. A moment with an unknown bar or an unknown path is left out of SIZE on its own side
(fire or random), never a miss. match7 and bar8 are edition 11's, unchanged: size_view puts the hit where they read it. COUNT is edition
11's (a wave with a 1 h value, whatever the bar). A month under 10 judged waves is THIN and cannot hold, as always; so a THIN Sep means
Oct, Nov and Dec must all hold.
  python3 -B fl_read_v12.py <TARGETS_FL.tsv> <ALARM_DESIGN dir> <COSTS_PER_COIN_V1.tsv> <out (new)> --bar <BAR dir> <receipts dirs as fl_read_v11.py>
HOLD (GPT 10:30:53Z): a threshold table is read only from bytes equal to its manifest's output digest, from the expected producer and settings, each row consistent: anything else is REFUSED before a verdict, for reader and ladder alike.
RULE_12 and edition 11's RULE_9 stay side by side: both retrospective; a RULE_12 label replaces no earlier label and is no reason an alarm was chosen.
Writes everything edition 11 writes, then FL_RULE12.tsv, FL_<code>_RULE12.tsv, FL_RULE12_UNKNOWN.tsv, FL_RULE12_SUPPORT.tsv and FL12.json."""
import copy, csv, gzip, hashlib, io, json, os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fl_read_v11 as F   # noqa: E402  edition 11: Look, match7, bar8, verdict8, overall8; never edited
import bar_v1 as BV       # noqa: E402  the bar's columns
M = F.M

VERSION = 'fl_read_v12'
WIN60 = tuple(h for h in F.WINDOWS if h <= F.HIT_H)


def load_bar(p, T, e):
    """BAR_<list>.tsv.gz whose bytes are those of its manifest entry e -> (bar_pct, why) aligned to T by (coin, t), or None when it does not join one to one. Refused: other bytes, an inconsistent row, other counts than the manifest's"""
    out = e.get('out') if isinstance(e, dict) else None
    if not isinstance(out, list) or len(out) != 2 or out[0] != os.path.basename(p):
        raise M.Refused('BAR MANIFEST NAMES NO OUTPUT %s FOR %s' % (out, p))
    with open(p, 'rb') as f:
        raw = f.read()              # the digest and the rows come from the same read
    if hashlib.sha256(raw).hexdigest()[:16] != out[1]:
        raise M.Refused('BAR DIGEST %s IS %s; ITS MANIFEST RECORDS %s' % (p, hashlib.sha256(raw).hexdigest()[:16], out[1]))
    rd = csv.reader(io.StringIO(gzip.decompress(raw).decode()), delimiter='\t'); h = next(rd); rows = list(rd)
    if tuple(h) != BV.HEAD:
        raise M.Refused('BAR HEADER %s' % p)
    if e.get('rows') != len(rows):
        raise M.Refused('BAR ROWS %s: %d, ITS MANIFEST %s' % (p, len(rows), e.get('rows')))
    ib, iw = h.index('bar_pct'), h.index('why'); d = {}; why = {}
    for x in rows:
        bad = BV.row_fault(x[2], x[3], x[4], x[5], x[6]) if len(x) == len(h) else 'COLUMNS'
        if bad:
            raise M.Refused('BAR ROW %s %s %s: %s' % (p, x[0], x[1], bad))
        why[x[iw] or 'KNOWN'] = why.get(x[iw] or 'KNOWN', 0) + 1
        k = (x[0], int(x[1]))
        if k in d:
            return None
        d[k] = (float(x[ib]) if x[ib] != '' else np.nan, x[iw])
    if e.get('why') != why:
        raise M.Refused('BAR REASONS %s: %s, ITS MANIFEST %s' % (p, why, e.get('why')))
    keys = list(zip([str(c) for c in T['coin']], [int(t) for t in T['t']]))
    if set(keys) != set(d) or len(keys) != len(d):
        return None
    return np.array([d[k][0] for k in keys], float), np.array([d[k][1] for k in keys], dtype=object)


def bars_of(code, r, bdir, A, R):
    """({'A': (bar, why), 'R': (bar, why)} or None, note): NOT RUN without BAR_V1.json, for another list's sha16, or without a one to one join; REFUSED for another producer or settings, or a table that is not the manifest's (load_bar)"""
    mp = os.path.join(bdir, 'BAR_V1.json') if bdir else ''
    if not bdir or not os.path.isfile(mp):
        return None, 'NOT RUN: no BAR_V1.json'
    with open(mp) as f:
        man = json.load(f)
    if man.get('version') != BV.VERSION or man.get('settings') != BV.SETTINGS:
        raise M.Refused('BAR PRODUCER %s: edition %s, settings %s; expected %s, %s' % (mp, man.get('version'), man.get('settings'), BV.VERSION, BV.SETTINGS))
    out = {}; note = {'manifest': [mp, F.s16(mp)], 'version': man.get('version')}
    for k, col, T in (('A', 'A_sha16', A), ('R', 'R_sha16', R)):
        e = (man.get('lists') or {}).get('%s_%s' % (k, code)); p = os.path.join(bdir, 'BAR_%s_%s.tsv.gz' % (k, code))
        if e is None or e['list'][1] != r[col] or not os.path.isfile(p):
            return None, 'NOT RUN: BAR_%s_%s missing or built from another list' % (k, code)
        x = load_bar(p, T, e)
        if x is None:
            return None, 'NOT RUN: BAR_%s_%s does not join the %s rows one to one' % (k, code, k)
        out[k] = x
    return out, note


def hit_b(T, bar):
    """1 when the price moved at least the moment's bar either way within 1 h, seen in the stored path values; 0 when BEST_60M has both values
    under the bar; NaN when the bar or the path is unknown. -> (hit, path_unknown: the bar known, the path not, no crossing seen)"""
    bar = np.asarray(bar, float); n = len(bar); seen = np.zeros(n, bool); known = np.isfinite(bar)
    for h in WIN60:
        for d in ('FADE', 'FOLLOW'):
            v = T['BEST_%dM__%s' % (h, d)]
            with np.errstate(invalid='ignore'):
                seen |= known & np.isfinite(v) & (v >= bar - F.TOL)
    full = np.isfinite(T['BEST_%dM__FADE' % F.HIT_H]) & np.isfinite(T['BEST_%dM__FOLLOW' % F.HIT_H])
    hit = np.where(seen, 1.0, np.where(known & full, 0.0, np.nan))
    return hit, known & ~seen & ~full


def size_view(L, hitA, hitR):
    """a copy of Look L where edition 11's hit4 reads the hit at B: match7 and bar8 stay edition 11's. L's own tables are not changed"""
    V = copy.copy(L); ob = 'OBH4_%dM__%s' % (F.HIT_H, L.lean); oo = 'OBH4_%dM__%s' % (F.HIT_H, F.other(L.lean))
    V.A = dict(L.A); V.R = dict(L.R); V.A[ob] = hitA; V.A[oo] = -hitA; V.R[ob] = hitR; V.R[oo] = -hitR
    return V


def size12(V, bz, months, counts, z_min):
    """the SIZE bar at B over `months`; counts are edition 11's (counts8 on the real Look)"""
    if bz is None:
        return {'PASS': 'NOT RUN', 'fail': ['NOT RUN (no BZ tables)']}
    return F.bar8(V, F.match7(V, bz, months, True), months, counts, 'SIZE', z_min)


def unknown_rows(code, L, bars, hA, hR, pA, pR, X, months):
    """per month: fires, by reason; the random's weight unknown; the judged waves and the random's hit share (a meaning check)"""
    out = []
    for m in months:
        fa = L.useA & (L.fmonth == m); ra = L.useR & (L.rmonth == m); wy = bars['A'][1][fa]; w = L.wR[ra]; wyr = bars['R'][1][ra]; kn = np.isfinite(hR[ra])
        w = np.where(np.isfinite(w), w, 0.0); W = float(w.sum())
        cnt = lambda x: sum(1 for q in x.tolist() if q)
        out.append({'code': code, 'month': m, 'fires': int(fa.sum()), 'bar_unknown': cnt(wy), 'path_unknown': int(pA[fa].sum()), 'fires_known': int(np.isfinite(hA[fa]).sum()),
                    'NO_COST': sum('NO_COST' in q for q in wy.tolist()), 'EXHAUSTED_COST': sum('EXHAUSTED_COST' in q for q in wy.tolist()), 'NO_LINE': sum('NO_LINE' in q for q in wy.tolist()),
                    'random': int(ra.sum()), 'random_bar_unknown': cnt(wyr), 'random_path_unknown': int(pR[ra].sum()),
                    'random_weight_unknown_share': float(w[~kn].sum() / W) if W > 0 else np.nan,
                    'random_hit_share': float((w[kn] * hR[ra][kn]).sum() / w[kn].sum()) if w[kn].sum() > 0 else np.nan,
                    'alarm_hit_share_all': float(hA[fa][np.isfinite(hA[fa])].mean()) if np.isfinite(hA[fa]).any() else np.nan})
    return out


U_COLS = ['code', 'month', 'fires', 'bar_unknown', 'path_unknown', 'fires_known', 'NO_COST', 'EXHAUSTED_COST', 'NO_LINE', 'random', 'random_bar_unknown', 'random_path_unknown',
          'random_weight_unknown_share', 'random_hit_share', 'alarm_hit_share_all']


def support_rows(code, L, V, bz, months):
    """GPT's check 09:45:02Z: all -> busy -> known -> matched, per month of a period, fires and waves (a wave's month: its first fire's) and the
    random. The busy population is edition 11's (table c), retrospective; matched reads SIZE at B"""
    X = F.match7(V, bz, months, True); hR = F.hit4(V.R, V.lean); nR = bz['R']['normal_move_pct'] / L.cR; out = []
    wv = lambda k: len(np.unique(L.wid[k]))
    with np.errstate(divide='ignore', invalid='ignore'):
        rR = bz['R']['range60_pct'] / bz['R']['normal_move_pct']
    busyR = L.useR & np.isfinite(nR) & (nR >= F.BUSY_MIN_C - F.TOL) & ~L.preR & (L.wR > 0)
    for m in months:
        wm = L.useA & (L.wmonth == m); ra = L.useR & (L.rmonth == m); rb = ra & busyR
        out.append({'code': code, 'month': m, 'fires_all': int(wm.sum()), 'fires_busy': int((X['busy'] & wm).sum()), 'fires_known': int((X['ok'] & wm).sum()), 'fires_matched': int((X['matched'] & wm).sum()),
                    'waves_all': wv(wm), 'waves_busy': wv(X['busy'] & wm), 'waves_known': wv(X['ok'] & wm), 'waves_matched': wv(X['matched'] & wm),
                    'random_all': int(ra.sum()), 'random_busy': int(rb.sum()), 'random_known': int((rb & np.isfinite(hR) & np.isfinite(rR)).sum())})
    return out


S_COLS = ['code', 'month', 'fires_all', 'fires_busy', 'fires_known', 'fires_matched', 'waves_all', 'waves_busy', 'waves_known', 'waves_matched', 'random_all', 'random_busy', 'random_known']


def read_code(r, costs, files, lists, bdir):
    """one code -> {'rule_12', periods: {SIZE12, SIZE11, SIDE}, 'unknown' rows} or None"""
    A = M.load_table(files['A']); R = M.load_table(files['R']); F.check_inputs(r, A, R, lists, files); wR = F.load_w(files['W'], R)
    L = F.Look(A, R, wR, costs, r['lean'], pre_R=F.pre_fire_mask(A, R)); bz, _ = F.busy_of(r['code'], r, files, A, R)
    bars, note = bars_of(r['code'], r, bdir, A, R); res = {'note': note, 'periods': {}}
    V = None
    if bars is not None:
        hA, pA = hit_b(A, bars['A'][0]); hR, pR = hit_b(R, bars['R'][0]); V = size_view(L, hA, hR)
    for p, ms, z in F.PERIODS9:
        c = F.counts8(L, ms); v8 = F.verdict8(L, bz, ms, c, z_min=z)
        res['periods'][p] = {'SIZE11': v8['SIZE'], 'SIDE': v8['SIDE'],
                             'SIZE': size12(V, bz, ms, c, z) if V is not None else {'PASS': 'NOT RUN', 'fail': [str(note)]}}
    d, w = res['periods']['Sep-Dec'], res['periods']['Jan-Apr']
    res['RULE_12'] = 'NOT RUN' if V is None or bz is None else F.overall8(d, w)
    res['RULE_9_here'] = F.overall8({'SIZE': d['SIZE11'], 'SIDE': d['SIDE']}, {'SIZE': w['SIZE11'], 'SIDE': w['SIDE']})
    res['unknown'] = unknown_rows(r['code'], L, bars, hA, hR, pA, pR, None, M.DESIGN + M.FORWARD) if V is not None else []
    res['support'] = [x for _, ms, _ in F.PERIODS9 for x in support_rows(r['code'], L, V, bz, ms)] if V is not None and bz is not None else []
    return res


def write_tables(out, T, res):
    cols = ['alarm_id', 'code', 'V', 'lean', 'RULE_12', 'RULE_9', 'changed']
    for p in ('SepDec', 'JanApr'):
        for b in ('SIZE', 'SIZE11', 'SIDE'):
            cols += ['%s_%s' % (b, p), '%s_%s_fail' % (b, p), '%s_%s_months' % (b, p), '%s_%s_z' % (b, p), '%s_%s_pts' % (b, p), '%s_%s_waves' % (b, p)]
    with open(os.path.join(out, 'FL_RULE12.tsv'), 'x') as f:
        f.write('\t'.join(cols) + '\n')
        for r in T:
            q = res.get(r['code'])
            for aid in r['alarm_ids'].split(','):
                if q is None:
                    f.write('\t'.join([aid, r['code'], r['V'], r['lean'], 'NOT RUN'] + [''] * (len(cols) - 5)) + '\n'); continue
                x = [aid, r['code'], r['V'], r['lean'], q['RULE_12'], q['RULE_9_here'], int(q['RULE_12'] != q['RULE_9_here'])]
                for p in ('Sep-Dec', 'Jan-Apr'):
                    for b in ('SIZE', 'SIZE11', 'SIDE'):
                        d = q['periods'][p][b]
                        x += [d['PASS'], '; '.join(d['fail']) or '-', d.get('months_holding', ''), F.fnum(d.get('z')), F.fnum(d.get('excess_pts'), 1), d.get('waves', '')]
                f.write('\t'.join(str(v) for v in x) + '\n')
    for r in T:
        q = res.get(r['code'])
        if q is None:
            continue
        with open(os.path.join(out, 'FL_%s_RULE12.tsv' % r['code']), 'x') as f:
            f.write('period\tmonth\twaves\tthin\talarm\texpected\texcess_pts\tholds\twaves_1h\tsize11_excess_pts\tsize11_waves\n')
            for p, ms, _ in F.PERIODS9:
                d, o = q['periods'][p]['SIZE'], q['periods'][p]['SIZE11']
                if 'months' not in d:
                    continue
                for m in ms:
                    t = d['months'][m]; u = (o.get('months') or {}).get(m, {})
                    f.write('%s\t%s\t%d\t%d\t%s\t%s\t%s\t%d\t%d\t%s\t%s\n' % (p, m, t['waves'], t['thin'], F.fnum(t['alarm'], 3), F.fnum(t['expected'], 3), F.fnum(t['excess_pts'], 1),
                                                                         t['holds'], t['waves_1h'], F.fnum(u.get('excess_pts'), 1), u.get('waves', '')))
    with open(os.path.join(out, 'FL_RULE12_UNKNOWN.tsv'), 'x') as f:
        f.write('\t'.join(U_COLS) + '\n')
        for r in T:
            for x in (res.get(r['code']) or {}).get('unknown', []):
                f.write('\t'.join(F.fnum(x[c], 3) if isinstance(x[c], float) else str(x[c]) for c in U_COLS) + '\n')


def write_support(out, T, res):
    with open(os.path.join(out, 'FL_RULE12_SUPPORT.tsv'), 'x') as f:
        f.write('\t'.join(S_COLS) + '\n')
        for r in T:
            for x in (res.get(r['code']) or {}).get('support', []):
                f.write('\t'.join(str(x[c]) for c in S_COLS) + '\n')


def side_same(out):
    """the SIDE columns of FL_RULE12 equal FL_RULE9's, row by row and text by text; False stops the run"""
    a = list(csv.DictReader(open(os.path.join(out, 'FL_RULE9.tsv')), delimiter='\t')); b = list(csv.DictReader(open(os.path.join(out, 'FL_RULE12.tsv')), delimiter='\t'))
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x['alarm_id'] != y['alarm_id'] or x['RULE_9'] != y['RULE_9']:
            return False
        for p in ('SepDec', 'JanApr'):
            for k in ('', '_fail', '_months', '_z', '_pts'):
                if x['SIDE_%s%s' % (p, k)] != y['SIDE_%s%s' % (p, k)]:
                    return False
    return True


def write_all(targets, costs_path, out, bdir, rdirs):
    costs = M.load_costs(costs_path); T = list(csv.DictReader(open(targets), delimiter='\t')); idir = os.path.dirname(targets)
    found = {}
    for d in rdirs:
        for fn in os.listdir(d):
            ma = F.AP_RE.match(fn)
            k = fn[:-7] if fn.endswith('.tsv.gz') else ('%s_%s' % (ma.group(1), ma.group(2)) if ma else None)
            if k is not None:
                found[k] = os.path.join(d, fn)
    res = {}
    for r in T:
        c = r['code']
        files = {'A': found.get('A' + c), 'R': found.get('R' + c), 'W': os.path.join(idir, 'R_%s_W.tsv' % c), 'BZA': found.get('BZ_A_' + c), 'BZR': found.get('BZ_R_' + c)}
        lists = {'A': os.path.join(idir, 'A_%s_EVENTS.tsv' % c), 'R': os.path.join(idir, 'R_%s_EVENTS.tsv' % c)}
        if files['A'] and files['R']:
            res[c] = read_code(r, costs, files, lists, bdir)
    write_tables(out, T, res); write_support(out, T, res)
    if not side_same(out):
        raise M.Refused('SIDE DIFFERS FROM EDITION 11')
    mp = os.path.join(bdir, 'BAR_V1.json') if bdir else None
    with open(os.path.join(out, 'FL12.json'), 'x') as f:
        json.dump({'version': VERSION, 'code': {'fl_read_v12.py': F.s16(os.path.abspath(__file__)), 'bar_v1.py': F.s16(BV.__file__), 'fl_read_v11.py': F.s16(F.__file__)},
                   'bar': [mp, F.s16(mp)] if mp and os.path.isfile(mp) else None, 'targets': [targets, F.s16(targets)], 'labels_read': 'retrospective: RULE_12 beside RULE_9, neither replaces the other', 'notes': {c: q['note'] for c, q in res.items()}}, f, indent=1, sort_keys=True, default=str)
    print('FL_RULE12 %s FL_RULE12_UNKNOWN %s' % (F.s16(os.path.join(out, 'FL_RULE12.tsv')), F.s16(os.path.join(out, 'FL_RULE12_UNKNOWN.tsv'))))


def main(targets, H, costs_path, out, *a):
    a = list(a)
    if '--bar' not in a or a.index('--bar') + 1 >= len(a):
        raise M.Refused('--bar <BAR dir> IS REQUIRED')
    i = a.index('--bar'); bdir = a[i + 1]; rdirs = a[:i] + a[i + 2:]
    if not os.path.isfile(os.path.join(bdir, 'BAR_V1.json')):
        raise M.Refused('NO BAR_V1.json in %s (the build writes it last)' % bdir)
    F.main(targets, H, costs_path, out + '.e11', *rdirs)         # edition 11, unchanged; refuses what it refuses, publishes nothing then
    try:
        write_all(targets, costs_path, out + '.e11', bdir, rdirs)
    except BaseException:
        shutil.rmtree(out + '.e11', ignore_errors=True); raise
    os.rename(out + '.e11', out)


if __name__ == '__main__':
    try:
        main(*sys.argv[1:])
    except M.Refused as e:
        print('REFUSED %s' % e); sys.exit(2)
