"""fair_v5.py (SCOUT 2 Nov 2026, tools/alarm_first_look). TEST, NOT REVIEWED. why: team/RESEARCH/plans/PLAN_FL12_PERCOIN_BAR_20261102.md.
The ladder for edition 12's SIZE at B. fair_v4 (imported, unchanged) gives the draws: the null by weight, side_flip, the plants, summary, calib.
SIDE runs read as in fair_v4, so its rows equal fair_v4's on the same seeds. SIZE reads hit_b: a made-up fire keeps its own bar and path, a
random moment its own. size_plant turns misses at B into hits (an unknown stays unknown). --seed-base S runs seeds S..S+seeds-1 (fresh draws).
  python3 -B fair_v5.py <TARGETS_FL.tsv> <H> <COSTS> <out (new)> <seeds> <plants> --bar <BAR dir> [--codes T04] [--plant-seeds N] [--seed-base S] <receipts dirs>
Writes FAIR_RUNS.tsv, FAIR_SUMMARY.tsv, FAIR_CALIB.tsv (fair_v4's columns) and FAIR_V5.json (settings, code, the SIZE null with its exact 95 pct bounds)."""
import csv, json, math, os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fair_v4 as P      # noqa: E402
import fl_read_v12 as E  # noqa: E402
F = E.F; M = F.M
VERSION = 'fair_v5'


def binom_cdf(k, n, p):
    if k < 0:
        return 0.0
    if p <= 0:
        return 1.0
    if p >= 1:
        return 1.0 if k >= n else 0.0
    s = 0.0
    for i in range(0, k + 1):
        s += math.exp(math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * math.log(p) + (n - i) * math.log(1 - p))
    return min(1.0, s)


def clopper(k, n, a=0.05):
    """exact two-sided 1 - a interval of k of n, by bisection"""
    if not n:
        return np.nan, np.nan

    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    low = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < a / 2)
    high = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > a / 2)
    return low, high


def ladder(r, L, R, wR, costs, bz, bars, seeds, plants, plant_seeds, base=0, log=None):
    """every run of one code -> FAIR_RUNS rows (SIZE at B; SIDE as fair_v4)"""
    code, aid = r['code'], r['alarm_ids']; rows = []; nf = int(L.useA.sum()); PS = P.PERIODS2; Z = P.ZMIN
    hA, _ = E.hit_b(L.A, bars['A'][0]); hR, _ = E.hit_b(R, bars['R'][0]); V = E.size_view(L, hA, hR)
    counts = {p: F.counts8(L, ms) for p, ms in PS}
    rows += P.runs_of(code, aid, 'real', 0, 0, {p: {'SIZE': E.size12(V, bz, ms, counts[p], Z[p]), 'SIDE': F.verdict8(L, None, ms, counts[p], z_min=Z[p])['SIDE']} for p, ms in PS}, nf)
    for k in range(seeds):
        s = base + k
        netA, netR = P.side_flip(L, P.rng_for(s, code, 'side_flip', 0))
        rows += P.runs_of(code, aid, 'side_flip', 0, s, {p: {'SIDE': F.bar8(L, F.side8(L, ms, netA, netR), ms, counts[p], 'SIDE', Z[p])} for p, ms in PS}, nf)
        for plant in (plants if k < plant_seeds else []):
            net = P.plant_side(L, netA, plant, P.rng_for(s, code, 'side_plant', plant))
            rows += P.runs_of(code, aid, 'side_plant', plant, s, {p: {'SIDE': F.bar8(L, F.side8(L, ms, net, netR), ms, counts[p], 'SIDE', Z[p])} for p, ms in PS}, nf)
    for k in range(seeds):
        s = base + k
        rws = P.null_rows(L, P.rng_for(s, code, 'null', 0)); L2, bz2 = P.made_up(L, R, wR, costs, bz, rws)
        keep = np.ones(len(R['t']), bool); keep[rws] = False; V2 = E.size_view(L2, hR[rws], hR[keep])
        c2 = {p: F.counts8(L2, ms) for p, ms in PS}
        rows += P.runs_of(code, aid, 'null', 0, s, {p: {'SIZE': E.size12(V2, bz2, ms, c2[p], Z[p]), 'SIDE': F.verdict8(L2, None, ms, c2[p], z_min=Z[p])['SIDE']} for p, ms in PS}, len(rws))
        for plant in (plants if bz2 is not None and k < plant_seeds else []):
            L3 = P.plant_size(V2, bz2, plant, P.rng_for(s, code, 'size_plant', plant))
            rows += P.runs_of(code, aid, 'size_plant', plant, s, {p: {'SIZE': E.size12(L3, bz2, ms, c2[p], Z[p])} for p, ms in PS}, len(rws))
    if log:
        log('LADDER %s: %d rows' % (code, len(rows)))
    return rows


def null_line(summ):
    x = [s for s in summ if s['code'] == 'ALL' and s['kind'] == 'null' and s['bar'] == 'SIZE']
    if not x:
        return None
    x = x[0]; lo, hi = clopper(x['pass_both'], x['runs'])
    return {'runs': x['runs'], 'pass_both': x['pass_both'], 'exact_lo': lo, 'exact_hi': hi, 'pass_SepDec': x['pass_SepDec'], 'pass_JanApr': x['pass_JanApr']}


def write(out, rows, summ, man, cal):
    with open(os.path.join(out, 'FAIR_RUNS.tsv'), 'x') as f:
        f.write('\t'.join(P.RUN_COLS) + '\n')
        for x in rows:
            f.write('\t'.join(F.fnum(x[c]) if c in ('z', 'excess_pts', 'z_min') else str(x[c]) for c in P.RUN_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_SUMMARY.tsv'), 'x') as f:
        f.write('\t'.join(P.SUM_COLS) + '\n')
        for x in summ:
            f.write('\t'.join(F.fnum(x[c], 3) if c.startswith(('rate', 'both_')) else (F.fnum(x[c]) if c.startswith('median') else str(x[c])) for c in P.SUM_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_CALIB.tsv'), 'x') as f:
        f.write('\t'.join(P.CALIB_COLS) + '\n')
        for x in cal:
            f.write('\t'.join(F.fnum(x[c], 3) if isinstance(x[c], float) else str(x[c]) for c in P.CALIB_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_V5.json'), 'x') as f:
        json.dump(man, f, indent=1, sort_keys=True, default=str)


def take(a, name, default=None):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return default


def main(a):
    a = list(a); bdir = take(a, '--bar'); codes = take(a, '--codes'); ps = take(a, '--plant-seeds'); base = int(take(a, '--seed-base', '0'))
    codes = set(codes.split(',')) if codes else None
    if len(a) < 7 or not bdir:
        print(__doc__); return 2
    targets, H, costs_path, out, seeds, plants = a[:6]; rdirs = a[6:]
    seeds = int(seeds); plants = [int(x) for x in plants.split(',') if x]; ps = seeds if ps is None else int(ps)
    if seeds < 0 or base < 0 or not 0 <= ps <= seeds or any(p <= 0 or p >= 100 for p in plants):
        raise M.Refused('SETTINGS (seeds %d, plant seeds %d, plants %s, base %d)' % (seeds, ps, plants, base))
    if os.path.exists(out) or os.path.exists(out + '.part'):
        raise M.Refused('OUT EXISTS %s' % out)
    if not os.path.isfile(os.path.join(bdir, 'BAR_V1.json')):
        raise M.Refused('NO BAR_V1.json in %s' % bdir)
    for d in rdirs:
        if not (F.job_finished(d) or (os.path.basename(os.path.normpath(d)) == 'BZ' and F.job_finished(os.path.dirname(os.path.normpath(d))))):
            raise M.Refused('JOB NOT FINISHED %s' % d)
    costs = M.load_costs(costs_path); T = list(csv.DictReader(open(targets), delimiter='\t')); idir = os.path.dirname(targets)
    found = {}
    for d in rdirs:
        for fn in os.listdir(d):
            if fn.endswith('.tsv.gz'):
                found[fn[:-7]] = os.path.join(d, fn)
    part = out + '.part'; os.makedirs(part); rows = []
    man = {'version': VERSION, 'code': {'fair_v5.py': F.s16(os.path.abspath(__file__)), 'fair_v4.py': F.s16(P.__file__), 'fl_read_v12.py': F.s16(E.__file__), 'fl_read_v11.py': F.s16(F.__file__), 'bar_v1.py': F.s16(E.BV.__file__)},
           'settings': {'seeds': seeds, 'seed_base': base, 'plant_seeds': ps, 'plants': plants}, 'bar': [bdir, F.s16(os.path.join(bdir, 'BAR_V1.json'))], 'targets': [targets, F.s16(targets)], 'not_run': {}}
    try:
        for r in T:
            c = r['code']
            if codes is not None and c not in codes:
                continue
            files = {'A': found.get('A' + c), 'R': found.get('R' + c), 'W': os.path.join(idir, 'R_%s_W.tsv' % c), 'BZA': found.get('BZ_A_' + c), 'BZR': found.get('BZ_R_' + c)}
            lists = {'A': os.path.join(idir, 'A_%s_EVENTS.tsv' % c), 'R': os.path.join(idir, 'R_%s_EVENTS.tsv' % c)}
            if not files['A'] or not files['R']:
                man['not_run'][c] = 'no A or R table'; continue
            A = M.load_table(files['A']); R = M.load_table(files['R']); F.check_inputs(r, A, R, lists, files); wR = F.load_w(files['W'], R)
            L = F.Look(A, R, wR, costs, r['lean'], pre_R=F.pre_fire_mask(A, R)); bz, _ = F.busy_of(c, r, files, A, R); bars, note = E.bars_of(c, r, bdir, A, R)
            if bars is None or bz is None:
                man['not_run'][c] = str(note); continue
            rows += ladder(r, L, R, wR, costs, bz, bars, seeds, plants, ps, base, log=print)
        summ = P.summary(rows); man['null_SIZE_both'] = null_line(summ); write(part, rows, summ, man, P.calib(rows))
    except BaseException:
        shutil.rmtree(part, ignore_errors=True); raise
    os.rename(part, out)
    print('FAIR_RUNS %s FAIR_SUMMARY %s FAIR_CALIB %s (%d rows); null SIZE both %s' % (F.s16(os.path.join(out, 'FAIR_RUNS.tsv')), F.s16(os.path.join(out, 'FAIR_SUMMARY.tsv')), F.s16(os.path.join(out, 'FAIR_CALIB.tsv')), len(rows), man['null_SIZE_both']))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except M.Refused as e:
        print('REFUSED %s' % e); sys.exit(2)
