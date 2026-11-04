"""fair_v4.py (SCOUT 30 Oct 2026, tools/alarm_first_look). TEST, NOT REVIEWED. Made by mk_fair_v4.py from fair_v3.py.
fair_v4 = fair_v3 (below) on edition 11 (fl_read_v11.py): the real alarm's fires are in the grade's 30 min waves (labcore's waves;
the owner 30 Oct 2026 21:11 Berlin, "30 minutes"), so side_flip, the plants and the real rows read them; the null by weight is unchanged
(each made-up fire its own wave). FAIR_V4.json; its code part names labcore/waves.py. Run it as fair_v1.py.
fair_v3.py's docstring follows: (SCOUT 30 Oct 2026, tools/alarm_first_look). TEST, NOT REVIEWED. Made by mk_fair_v3.py from fair_v2.py.
fair_v3 = fair_v2 (below) with a null that is no-edge against its own random by construction. Review B (30 Oct 2026 19:08Z,
reviews/REVIEW_B_FAIR2_20261030.md): FAIL on the SIZE fairness claim: fair_v2's made-up alarm leaned against its random (its fires
weighted one each, in waves of their own, while the random is weighted per grade wave; its own pre-fire moments cut from the random).
Review B's fix, each made-up fire in its real fire's wave, still leaned on T23 (SIZE null z +1.13 Sep-Dec, +1.80 Jan-Apr over 10 seeds;
SCOUT's VM check 30 Oct, not a receipt): a fire's candidates mix random moments of other waves, and the tables do not say which fire a
random moment was matched to. So, on edition 10 (fl_read_v10.py):
 - the null by weight: each random moment with a cost and a weight, not a real fire's pre-fire moment, is a made-up fire with
   probability p = min(w, PI_MAX = 0.5) (its weight: each grade wave gives about one), each made-up fire its own wave (Look's wid), and
   the rest is its random, each moment weighted w / (1 - p). In every cell the made-up fires and the random then have the same expected
   weighted mean (the moments over 0.5 carry 0.05 to 1.5 pct of the weight), and they are disjoint, so the random's own error stays in,
   as for a real alarm (a null against the full random read z too narrow, sd 0.4 to 0.8: SCOUT's VM check, 30 Oct);
 - the null is accepted on calibration, not on a pass count: FAIR_CALIB.tsv, for the null and side_flip (plant 0), per bar and period:
   per code its runs' z (mean, sd, shares at or over 1 and 2; LEANS when the mean is over 3 errors from 0) and for ALL the mean z, the
   sd within alarms, the spread of the alarms' means against its noise (the within sd over the root of the runs) and the verdict:
   CALIBRATED when |mean z| <= 0.2, the sd within alarms is 0.8 to 1.25 and the spread is at most 1.3 times its noise (SCOUT's lines,
   set 30 Oct 2026 before the job; TOO FEW ALARMS under 5);
 - FAIR_SUMMARY: every row gets rate_JanApr_given_SepDec (passes both / passes Sep-Dec); the ALL rows a 95 pct interval of the
   both-period rate over alarms (both_lo, both_hi: the codes resampled 2,000 times, seeded); FAIR_RUNS gets the bar's waves; FAIR_V3.json
   (per code the share of the weight on moments over PI_MAX).
fair_v2.py's docstring follows (made by mk_fair_v2.py from fair_v1.py; its null paragraph is fair_v3's):
fair_v2 = fair_v1 (below) on edition 9 (fl_read_v9.py): each period judged at its own z line (PERIODS9: Sep-Dec z >= 2, Jan-Apr
confirms at z >= 1; the owner 30 Oct 2026 19:21 Berlin, "Okay" to testing it on made-up alarms first); every FAIR_RUNS row carries its
z line (z_min); FAIR_SUMMARY gets an EITHER row for the runs that read both bars (real, null): a run passes a period when SIZE or SIDE
passes it, and passes both when one bar passes both periods (an alarm's own pass); FAIR_V2.json. Run it as fair_v1.py.
fair_v1.py's docstring follows:
THE LADDER for edition 8's two bars (fl_read_v8.py: SIZE, SIDE). The owner, the owner, 30 Oct 2026 Berlin: 17:35 "how do we know our bars
are fair?"; 17:40 "maybe we should have more than one bar and a way of proving that we keep the edges and remove what has no edge";
17:44 "okay build it". On each alarm's own fires and random moments (no new data), the bars are run on made-up alarms whose answer is
known, both periods (Sep-Dec, Jan-Apr), to count how often a bar lets a no-edge alarm through and how often it catches a planted edge:
 - null (no edge of any kind; both bars; fair_v3): a made-up alarm of the alarm's own random moments: each random moment with a cost and
   a weight, not a pre-fire moment of a real fire, is a made-up fire with probability min(w, PI_MAX), each its own wave; the moments
   left are its random, each weighted w / (1 - its probability) (a real fire's pre-fire moments stay out). Its fires and its random are
   the same kind of moment, weighted alike: no bar should pass it more often than its z line allows;
 - size_plant +D (SIZE): that null alarm with its misses (no 4c move within 1 h) turned into a 4c move (a random side) with probability
   D / (100 (1 - h)) a period (h: the period's busy made-up fires' hit share, waves weighted as the bar weights them), so it moves D
   points more often than equally busy random moments;
 - side_flip (no side; SIDE): the alarm's own fires (its timing, its waves, its days) with every UTC day's 1 h races flipped by one coin,
   and the random's races flipped by their own day coins: the sides say no more than a coin would;
 - side_plant +D (SIDE): side_flip with each race lost (the other side first) turned won with probability D / (100 s) a period (s: the
   period's decided share, waves weighted), so offer-first minus heat-first (the bar's unit) goes up D points against the random (the
   lean-first share D / 2: fair_v3's wording, review B);
 - real: the alarm itself (verdict8, both bars).
A run passes a period when the bar passes it; it passes when it passes both. Every draw comes from a generator seeded by (the seed, the
code, the kind, the plant); a plant on seed s is built on the null (or the flip) of seed s, so the two differ only by the plant.
  python3 -B fair_v1.py <TARGETS_FL.tsv> <ALARM_DESIGN dir> <COSTS_PER_COIN_V1.tsv> <out dir (new)> <seeds> <plants, e.g. 5,10>
                        [--codes T04,T05] [--plant-seeds N (<= seeds; default seeds)] <receipts dir> [<receipts dir> ...]
  (receipts dirs as fl_read_v10.py takes them: FLOUT, APROF22, and the busyness job's BZ folder)
Writes FAIR_RUNS.tsv (one row per code, kind, plant, seed, bar and period), FAIR_SUMMARY.tsv (for ALL codes and per code, per kind, plant
and bar: runs, passes in Sep-Dec, in Jan-Apr and in both, their rates, the median z and points a period) and FAIR_V1.json (inputs,
settings, code sha16s)."""
import copy, csv, hashlib, json, math, os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fl_read_v11 as F  # noqa: E402  the bars (edition 9's z lines; 10: given wave ids; 11: the grade's waves), tables, busyness join
M = F.M

VERSION = 'fair_v4'
PI_MAX = 0.5                                          # fair_v3: a random moment is a made-up fire with probability min(w, PI_MAX)
PERIODS2 = tuple((p, ms) for p, ms, z in F.PERIODS9)
ZMIN = {p: z for p, ms, z in F.PERIODS9}             # fair_v2: each period's z line (edition 9)
CALIB_MEAN_TOL = 0.2                                  # fair_v3: the null is CALIBRATED when |mean z| <= 0.2,
CALIB_SD = (0.8, 1.25)                                #   the sd of z within alarms is 0.8 to 1.25,
CALIB_SPREAD_MAX = 1.3                                #   the spread of the alarms' mean z at most 1.3 times its noise,
CALIB_MIN_ALARMS = 5                                  #   over 5 alarms or more (SCOUT 30 Oct 2026, set before the job)
BOOT_N, BOOT_SEED = 2000, 0                           # the both-period rate's interval over alarms: resamples of the codes, seed
KINDS = {'real': 0, 'null': 1, 'size_plant': 2, 'side_flip': 3, 'side_plant': 4}


def rng_for(seed, code, kind, plant):
    return np.random.default_rng([int(seed), int(hashlib.sha256(code.encode()).hexdigest()[:8], 16), KINDS[kind], int(plant)])


def null_p(L):
    """fair_v3: each random moment's probability of being a made-up fire: min(its weight, PI_MAX); 0 for a moment without a cost or a
    weight and for a real fire's pre-fire moment"""
    ok = L.useR & ~L.preR & np.isfinite(L.wR) & (L.wR > 0)
    return np.where(ok, np.minimum(np.where(ok, L.wR, 0.0), PI_MAX), 0.0)


def null_rows(L, rng):
    """fair_v3: the made-up fires of one seed: each random moment with probability null_p -> row indices, in order"""
    return np.flatnonzero(rng.random(len(L.wR)) < null_p(L))


def sub(T, m):
    n = len(T['t'])
    return {k: (v[m] if isinstance(v, np.ndarray) and v.shape[:1] == (n,) else v) for k, v in T.items()}


def made_up(L, R, wR, costs, bz, rows):
    """the made-up alarm of random rows `rows` (null_rows): its fires are those rows, each its own wave (fair_v3: weighted as the random
    weights one grade wave's moment); its random is the rest, each moment weighted w / (1 - null_p), so it still estimates the alarm's
    weighted random; a real fire's pre-fire moments stay out of it (no pre-fire cut of its own) -> (Look, busyness arrays or None)"""
    keep = np.ones(len(R['t']), bool); keep[rows] = False
    A2 = sub(R, rows); R2 = sub(R, keep); v = np.asarray(wR, float) / (1.0 - null_p(L))
    L2 = F.Look(A2, R2, v[keep], costs, L.lean, pre_R=L.preR[keep], wid=np.arange(len(rows)))
    bz2 = None if bz is None else {'A': {k: bz['R'][k][rows] for k in F.BZ_COLS}, 'R': {k: bz['R'][k][keep] for k in F.BZ_COLS}}
    return L2, bz2


def wave_share(L, x, sel):
    """the mean of x over the fires in sel, waves weighted as stats7 weights them (a wave 1, its fires 1 / its size)"""
    if not sel.any():
        return np.nan
    u, inv = np.unique(L.wid[sel], return_inverse=True); nw = np.bincount(inv)
    return float((np.bincount(inv, weights=x[sel]) / nw).mean())


def day_signs(t, rng):
    """one coin a UTC day: -1 or +1 for every row of that day"""
    d = np.asarray(t, np.int64) // 86400
    if not len(d):
        return np.zeros(0)
    u, inv = np.unique(d, return_inverse=True)
    return np.where(rng.random(len(u)) < 0.5, -1.0, 1.0)[inv]


def side_flip(L, rng):
    """the alarm's 1 h races (+1 lean first, -1 other first, 0 neither) with each UTC day flipped by a coin, the fires' days and the
    random's days by coins apart -> (fires' races, random's races)"""
    ob = 'OBH4_60M__%s' % L.lean
    return L.net(L.A, ob) * day_signs(L.A['t'], rng), L.net(L.R, ob) * day_signs(L.R['t'], rng)


def plant_side(L, net, plant, rng):
    """each lost race (-1) of the fires turned won (+1) with probability plant / (100 s) a period, s the period's decided share (waves
    weighted): the waves' mean race goes up plant / 100"""
    net = np.array(net, float)
    for _, ms in PERIODS2:
        inp = L.useA & np.isin(L.wmonth, ms) & np.isfinite(net)
        s = wave_share(L, (net != 0).astype(float), inp)
        if not (np.isfinite(s) and s > 0):
            continue
        p = min(1.0, plant / (100.0 * s)); lose = np.flatnonzero(inp & (net < 0))
        net[lose[rng.random(len(lose)) < p]] = 1.0
    return net


def plant_size(L2, bz2, plant, rng):
    """the made-up alarm's misses (0) turned into 4c moves (a random side) with probability plant / (100 (1 - h)) a period, h the period's
    busy fires' hit share (waves weighted) -> a new Look (the null's own is not changed)"""
    ob = 'OBH4_60M__%s' % L2.lean; oo = 'OBH4_60M__%s' % F.other(L2.lean)
    v = np.array(L2.A[ob], float); w = np.array(L2.A[oo], float)
    nA = bz2['A']['normal_move_pct'] / L2.cA; busy = L2.useA & np.isfinite(nA) & (nA >= F.BUSY_MIN_C - F.TOL)
    for _, ms in PERIODS2:
        inp = L2.useA & np.isin(L2.wmonth, ms) & np.isfinite(v)
        h = wave_share(L2, (np.abs(v) == 1).astype(float), inp & busy)
        if not (np.isfinite(h) and h < 1):
            continue
        f = min(1.0, plant / (100.0 * (1.0 - h))); miss = np.flatnonzero(inp & (v == 0))
        turn = rng.random(len(miss)) < f; vals = np.where(rng.random(len(miss)) < 0.5, 1.0, -1.0)
        v[miss[turn]] = vals[turn]; w[miss[turn]] = -vals[turn]
    L3 = copy.copy(L2); L3.A = dict(L2.A); L3.A[ob] = v; L3.A[oo] = w
    return L3


def runs_of(code, aid, kind, plant, seed, V, fires):
    """rows for FAIR_RUNS from {period: {bar: verdict}}"""
    out = []
    for p, _ in PERIODS2:
        for bar, d in V[p].items():
            out.append({'code': code, 'alarm_ids': aid, 'kind': kind, 'plant': plant, 'seed': seed, 'bar': bar, 'period': p, 'PASS': d['PASS'],
                        'z': d.get('z', np.nan), 'excess_pts': d.get('excess_pts', np.nan), 'months_holding': d.get('months_holding', ''),
                        'fail': '; '.join(d.get('fail', [])) or '-', 'fires': fires, 'z_min': d.get('z_min', np.nan),
                        'waves': d.get('waves', '')})
    return out


def ladder(r, L, R, wR, costs, bz, seeds, plants, plant_seeds, log=None):
    """every run of one code -> FAIR_RUNS rows"""
    code, aid = r['code'], r['alarm_ids']; rows = []; nf = int(L.useA.sum())
    counts = {p: F.counts8(L, ms) for p, ms in PERIODS2}
    rows += runs_of(code, aid, 'real', 0, 0, {p: F.verdict8(L, bz, ms, counts[p], z_min=ZMIN[p]) for p, ms in PERIODS2}, nf)
    for s in range(seeds):                                    # the alarm's own timing, made-up sides
        netA, netR = side_flip(L, rng_for(s, code, 'side_flip', 0))
        V = {p: {'SIDE': F.bar8(L, F.side8(L, ms, netA, netR), ms, counts[p], 'SIDE', ZMIN[p])} for p, ms in PERIODS2}
        rows += runs_of(code, aid, 'side_flip', 0, s, V, nf)
        for plant in (plants if s < plant_seeds else []):
            net = plant_side(L, netA, plant, rng_for(s, code, 'side_plant', plant))
            V = {p: {'SIDE': F.bar8(L, F.side8(L, ms, net, netR), ms, counts[p], 'SIDE', ZMIN[p])} for p, ms in PERIODS2}
            rows += runs_of(code, aid, 'side_plant', plant, s, V, nf)
    for s in range(seeds):                                    # fair_v3: made-up alarms of the alarm's own random moments, by weight
        rws = null_rows(L, rng_for(s, code, 'null', 0)); L2, bz2 = made_up(L, R, wR, costs, bz, rws)
        c2 = {p: F.counts8(L2, ms) for p, ms in PERIODS2}
        rows += runs_of(code, aid, 'null', 0, s, {p: F.verdict8(L2, bz2, ms, c2[p], z_min=ZMIN[p]) for p, ms in PERIODS2}, len(rws))
        for plant in (plants if bz2 is not None and s < plant_seeds else []):
            L3 = plant_size(L2, bz2, plant, rng_for(s, code, 'size_plant', plant))
            V = {p: {'SIZE': F.bar8(L3, F.match7(L3, bz2, ms, True), ms, c2[p], 'SIZE', ZMIN[p])} for p, ms in PERIODS2}
            rows += runs_of(code, aid, 'size_plant', plant, s, V, len(rws))
    if log:
        log('LADDER %s: %d rows' % (code, len(rows)))
    return rows


def summary(rows):
    """for ALL codes and per code, per (kind, plant, bar): runs (code x seed; NOT RUN left out), passes in Sep-Dec, in Jan-Apr, in both,
    their rates, the median z and points a period"""
    g = {}
    for x in rows:
        if x['PASS'] == 'NOT RUN':
            continue
        for c in ('ALL', x['code']):
            g.setdefault((c, x['kind'], x['plant'], x['bar']), {}).setdefault((x['code'], x['seed']), {})[x['period']] = x
    ok = lambda v, p: v.get(p, {}).get('PASS') == 'PASS'

    def med(runs, p, k):
        a = [float(v[p][k]) for v in runs.values() if p in v and np.isfinite(float(v[p][k]))]
        return float(np.median(a)) if a else np.nan
    out = []
    for (code, kind, plant, bar), runs in sorted(g.items(), key=lambda kv: (kv[0][0] != 'ALL', kv[0][0], KINDS[kv[0][1]], kv[0][2], kv[0][3])):
        n = len(runs); sd = sum(ok(v, 'Sep-Dec') for v in runs.values()); ja = sum(ok(v, 'Jan-Apr') for v in runs.values())
        both = sum(ok(v, 'Sep-Dec') and ok(v, 'Jan-Apr') for v in runs.values())
        out.append({'code': code, 'kind': kind, 'plant': plant, 'bar': bar, 'runs': n, 'pass_SepDec': sd, 'pass_JanApr': ja, 'pass_both': both,
                    'rate_SepDec': sd / n, 'rate_JanApr': ja / n, 'rate_both': both / n,
                    'median_z_SepDec': med(runs, 'Sep-Dec', 'z'), 'median_z_JanApr': med(runs, 'Jan-Apr', 'z'),
                    'median_pts_SepDec': med(runs, 'Sep-Dec', 'excess_pts'), 'median_pts_JanApr': med(runs, 'Jan-Apr', 'excess_pts')})
    ev = {}                                                   # fair_v2: EITHER, for the runs that read both bars
    for (code, kind, plant, bar), runs in g.items():
        if kind in ('real', 'null'):
            for key, v in runs.items():
                ev.setdefault((code, kind, plant), {}).setdefault(key, []).append(v)
    for (code, kind, plant), runs in ev.items():
        n = len(runs); sd = sum(any(ok(v, 'Sep-Dec') for v in vs) for vs in runs.values()); ja = sum(any(ok(v, 'Jan-Apr') for v in vs) for vs in runs.values())
        both = sum(any(ok(v, 'Sep-Dec') and ok(v, 'Jan-Apr') for v in vs) for vs in runs.values())
        out.append({'code': code, 'kind': kind, 'plant': plant, 'bar': 'EITHER', 'runs': n, 'pass_SepDec': sd, 'pass_JanApr': ja, 'pass_both': both,
                    'rate_SepDec': sd / n, 'rate_JanApr': ja / n, 'rate_both': both / n, 'median_z_SepDec': np.nan, 'median_z_JanApr': np.nan,
                    'median_pts_SepDec': np.nan, 'median_pts_JanApr': np.nan})
    out.sort(key=lambda x: (x['code'] != 'ALL', x['code'], KINDS[x['kind']], x['plant'], x['bar']))
    per = {}                                                  # fair_v3: each code's (runs, passes both) for the interval over alarms
    for x in out:
        if x['code'] != 'ALL':
            per.setdefault((x['kind'], x['plant'], x['bar']), []).append((x['runs'], x['pass_both']))
    for x in out:
        x['rate_JanApr_given_SepDec'] = x['pass_both'] / x['pass_SepDec'] if x['pass_SepDec'] else np.nan
        x['both_lo'], x['both_hi'] = both_interval(per.get((x['kind'], x['plant'], x['bar']), [])) if x['code'] == 'ALL' else (np.nan, np.nan)
    return out


def both_interval(per_code, n=BOOT_N, seed=BOOT_SEED):
    """fair_v3: a 95 pct interval of the both-period pass rate over alarms: the codes resampled n times (seeded), each resample's
    passes over its runs -> (low, high); NaN without codes"""
    if not per_code:
        return np.nan, np.nan
    a = np.array(per_code, float); k = np.random.default_rng(seed).integers(0, len(a), size=(n, len(a)))
    r = a[k, 1].sum(1) / np.maximum(a[k, 0].sum(1), 1.0)
    return float(np.percentile(r, 2.5)), float(np.percentile(r, 97.5))


def calib(rows):
    """fair_v3: is the no-edge reference centred? For the null (plant 0) and side_flip, per bar and period, from the runs' finite z: per
    code its runs, mean, sd, shares at or over 1 and 2 (LEANS when |mean| is over 3 errors, sd / root of runs); for ALL the alarms with
    2 runs or more, the runs, the mean z, the sd within alarms (root of their mean variance), the spread of their means (sd) against its
    noise (root of the mean of variance / runs) and the verdict: CALIBRATED when |mean z| <= CALIB_MEAN_TOL, the sd within alarms in
    CALIB_SD and the spread at most CALIB_SPREAD_MAX times its noise; NOT CALIBRATED; TOO FEW ALARMS under CALIB_MIN_ALARMS"""
    g = {}
    for x in rows:
        if x['kind'] in ('null', 'side_flip') and x['plant'] == 0 and x['PASS'] != 'NOT RUN' and np.isfinite(float(x['z'])):
            g.setdefault((x['kind'], x['bar'], x['period']), {}).setdefault(x['code'], []).append(float(x['z']))
    head, body = [], []
    for (kind, bar, period), codes in sorted(g.items(), key=lambda kv: (KINDS[kv[0][0]], kv[0][1], kv[0][2] != 'Sep-Dec')):
        ok = []
        for code, zs in sorted(codes.items()):
            z = np.array(zs); n = len(z); mu = float(z.mean()); sd = float(z.std(ddof=1)) if n > 1 else np.nan
            lean = bool(n > 1 and abs(mu) > 3 * sd / math.sqrt(n) + F.TOL)
            body.append({'code': code, 'kind': kind, 'bar': bar, 'period': period, 'alarms': 1, 'runs': n, 'mean_z': mu, 'sd_z': sd,
                         'p_z_ge_1': float((z >= 1 - F.TOL).mean()), 'p_z_ge_2': float((z >= 2 - F.TOL).mean()), 'spread': np.nan, 'noise': np.nan,
                         'spread_ratio': np.nan, 'verdict': 'LEANS' if lean else '-'})
            if n > 1:
                ok.append((mu, sd ** 2, n))
        allz = np.concatenate([np.array(v) for v in codes.values()]); mz = float(allz.mean())
        x = {'code': 'ALL', 'kind': kind, 'bar': bar, 'period': period, 'alarms': len(ok), 'runs': len(allz), 'mean_z': mz, 'sd_z': np.nan,
             'p_z_ge_1': float((allz >= 1 - F.TOL).mean()), 'p_z_ge_2': float((allz >= 2 - F.TOL).mean()), 'spread': np.nan, 'noise': np.nan,
             'spread_ratio': np.nan, 'verdict': 'TOO FEW ALARMS'}
        if len(ok) >= CALIB_MIN_ALARMS:
            mu, var, n = (np.array(c, float) for c in zip(*ok))
            x['sd_z'] = math.sqrt(float(var.mean())); x['spread'] = float(mu.std(ddof=1)); x['noise'] = math.sqrt(float((var / n).mean()))
            x['spread_ratio'] = x['spread'] / x['noise'] if x['noise'] > 0 else np.nan
            good = (abs(mz) <= CALIB_MEAN_TOL + F.TOL and CALIB_SD[0] - F.TOL <= x['sd_z'] <= CALIB_SD[1] + F.TOL
                    and np.isfinite(x['spread_ratio']) and x['spread_ratio'] <= CALIB_SPREAD_MAX + F.TOL)
            x['verdict'] = 'CALIBRATED' if good else 'NOT CALIBRATED'
        head.append(x)
    return head + body


RUN_COLS = ['code', 'alarm_ids', 'kind', 'plant', 'seed', 'bar', 'period', 'PASS', 'z', 'excess_pts', 'months_holding', 'fail', 'fires', 'z_min', 'waves']
SUM_COLS = ['code', 'kind', 'plant', 'bar', 'runs', 'pass_SepDec', 'pass_JanApr', 'pass_both', 'rate_SepDec', 'rate_JanApr', 'rate_both',
            'median_z_SepDec', 'median_z_JanApr', 'median_pts_SepDec', 'median_pts_JanApr', 'rate_JanApr_given_SepDec', 'both_lo', 'both_hi']
CALIB_COLS = ['code', 'kind', 'bar', 'period', 'alarms', 'runs', 'mean_z', 'sd_z', 'p_z_ge_1', 'p_z_ge_2', 'spread', 'noise', 'spread_ratio', 'verdict']


def write(out, rows, summ, man, cal):
    with open(os.path.join(out, 'FAIR_RUNS.tsv'), 'x') as f:
        f.write('\t'.join(RUN_COLS) + '\n')
        for x in rows:
            f.write('\t'.join(F.fnum(x[c]) if c in ('z', 'excess_pts', 'z_min') else str(x[c]) for c in RUN_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_SUMMARY.tsv'), 'x') as f:
        f.write('\t'.join(SUM_COLS) + '\n')
        for x in summ:
            f.write('\t'.join(F.fnum(x[c], 3) if c.startswith(('rate', 'both_')) else (F.fnum(x[c]) if c.startswith('median') else str(x[c])) for c in SUM_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_CALIB.tsv'), 'x') as f:
        f.write('\t'.join(CALIB_COLS) + '\n')
        for x in cal:
            f.write('\t'.join(F.fnum(x[c], 3) if isinstance(x[c], float) else str(x[c]) for c in CALIB_COLS) + '\n')
    with open(os.path.join(out, 'FAIR_V4.json'), 'x') as f:
        json.dump(man, f, indent=1, sort_keys=True)


def main(a):
    codes = None; plant_seeds = None; rest = []; i = 0
    while i < len(a):
        if a[i] == '--codes' and i + 1 < len(a):
            codes = set(a[i + 1].split(',')); i += 2
        elif a[i] == '--plant-seeds' and i + 1 < len(a):
            plant_seeds = int(a[i + 1]); i += 2
        else:
            rest.append(a[i]); i += 1
    if len(rest) < 7:
        print(__doc__); return 2
    targets, H, costs_path, out, seeds, plants = rest[:6]; rdirs = rest[6:]
    seeds = int(seeds); plants = [int(x) for x in plants.split(',') if x]; plant_seeds = seeds if plant_seeds is None else plant_seeds
    if seeds < 0 or not 0 <= plant_seeds <= seeds or any(p <= 0 or p >= 100 for p in plants):
        raise M.Refused('SETTINGS (seeds %d, plant seeds %d, plants %s): 0 <= plant seeds <= seeds, 0 < plant < 100' % (seeds, plant_seeds, plants))
    if os.path.exists(out) or os.path.exists(out + '.part'):
        raise M.Refused('OUT EXISTS %s' % out)
    for d in rdirs:
        if not (F.job_finished(d) or (os.path.basename(os.path.normpath(d)) == 'BZ' and F.job_finished(os.path.dirname(os.path.normpath(d))))):
            raise M.Refused('JOB NOT FINISHED %s (its STAGES.tsv has no "end 0" line)' % d)
    costs = M.load_costs(costs_path); T = list(csv.DictReader(open(targets), delimiter='\t')); idir = os.path.dirname(targets)
    if codes is not None and not codes <= {r['code'] for r in T}:
        raise M.Refused('CODES NOT IN TARGETS %s' % ','.join(sorted(codes - {r['code'] for r in T})))
    found = {}
    for d in rdirs:
        for fn in os.listdir(d):
            ma = F.AP_RE.match(fn)
            k = fn[:-7] if fn.endswith('.tsv.gz') else ('%s_%s' % (ma.group(1), ma.group(2)) if ma else None)
            if k is None:
                continue
            if k in found:
                raise M.Refused('TWO FILES FOR %s' % k)
            found[k] = os.path.join(d, fn)
    part = out + '.part'; os.makedirs(part); rows = []
    man = {'version': VERSION, 'code': {'fair_v4.py': F.s16(os.path.abspath(__file__)), 'fl_read_v11.py': F.s16(F.__file__), 'labcore/waves.py': F.s16(F.WV.__file__), 'md_v1.py': F.s16(M.__file__)},
           'settings': {'seeds': seeds, 'plant_seeds': plant_seeds, 'plants': plants, 'null': {'pi_max': PI_MAX}, 'z_lines': dict(ZMIN),
                        'calib': {'mean_tol': CALIB_MEAN_TOL, 'sd': list(CALIB_SD), 'spread_max': CALIB_SPREAD_MAX, 'min_alarms': CALIB_MIN_ALARMS},
                        'boot': {'n': BOOT_N, 'seed': BOOT_SEED}},
           'targets': [targets, F.s16(targets)], 'receipts': rdirs, 'codes': {}}
    try:
        for r in T:
            c = r['code']
            if codes is not None and c not in codes:
                continue
            files = {'A': found.get('A' + c), 'R': found.get('R' + c), 'W': os.path.join(idir, 'R_%s_W.tsv' % c),
                     'BZA': found.get('BZ_A_' + c), 'BZR': found.get('BZ_R_' + c)}
            lists = {'A': os.path.join(idir, 'A_%s_EVENTS.tsv' % c), 'R': os.path.join(idir, 'R_%s_EVENTS.tsv' % c)}
            if not files['A'] or not files['R']:
                man['codes'][c] = 'NOT RUN: no A or R table'; continue
            A = M.load_table(files['A']); R = M.load_table(files['R']); F.check_inputs(r, A, R, lists, files)
            wR = F.load_w(files['W'], R)
            L = F.Look(A, R, wR, costs, r['lean'], pre_R=F.pre_fire_mask(A, R))
            bz, note = F.busy_of(c, r, files, A, R)
            w = np.where(null_p(L) > 0, L.wR, 0.0)
            man['codes'][c] = {'inputs': {k: [os.path.basename(p), F.s16(p)] for k, p in files.items() if p}, 'busy_v1': note,
                               'null_weight_over_pi_max': float(w[w > PI_MAX].sum() / w.sum()) if w.sum() > 0 else None}
            rows += ladder(r, L, R, wR, costs, bz, seeds, plants, plant_seeds, log=print)
        summ = summary(rows); write(part, rows, summ, man, calib(rows))
    except BaseException:
        shutil.rmtree(part, ignore_errors=True); raise
    os.rename(part, out)
    print('FAIR_RUNS %s FAIR_SUMMARY %s FAIR_CALIB %s (%d rows)' % (F.s16(os.path.join(out, 'FAIR_RUNS.tsv')), F.s16(os.path.join(out, 'FAIR_SUMMARY.tsv')),
                                                                 F.s16(os.path.join(out, 'FAIR_CALIB.tsv')), len(rows)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except M.Refused as e:
        print('REFUSED %s' % e)
        sys.exit(2)
