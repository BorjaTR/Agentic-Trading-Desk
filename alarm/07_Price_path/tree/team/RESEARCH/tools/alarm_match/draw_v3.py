"""alarm_match draw V3 (QUANT, 23 Oct 2026; OUTSIDE S06 5ad00361, all accepted, ASK STRATEGY-133818b with ALARM; SCOUT review 153096b8:
MUSTs M1-M5 in, SHOULDs S1, S3, S4, S5, S6 in, S2 reported): the matched-moment baseline drawn again under a declared contract. Replaces,
for new work, the V1 draw inside QUANT/proposals/stage2/fire_path_v1.py (draw_matches) and the A02N twin built from it
(match_events_a02n_v1); those lists stay as receipts of what they were.
ESTIMAND (rule 1): CONDITIONAL PREDICTION at alarm time: the alarm's moment against the AVAILABLE-AT-TIME no-alarm risk set of the same
coin (+-7 days, UTC hour +-1, the same split part) with similar PRE-EXPOSURE activity. Not a total causal effect. The covariate is the
activity over (t - 5400 s, t - 1800 s]: it ends where the widest onset window (W30) starts, so no part of a burst that began up to 30 min
before the alarm is matched away. It is anchored at the last close at or before the window start and is EMPTY (NO_COVARIATE) when any
gap between closes, or from the last close to the window end, exceeds gap_s (60 s): a price hole is never read as a quiet window (M5).
ELIGIBILITY (rule 2): a candidate is eligible when NO alarm of the list and NO parent of the run is at or within away_s BEFORE it (past
only: a later alarm never removes a candidate; parent times are merged into the exclusion list, M1); when it and its outcome horizon lie
in the parent's SPLIT PART (FIT / CONFIRM / CHECK, read from WINDOWS_V1's BUILD use text and CHECK row, pinned in the manifest; BLIND
never, M2); and when its covariate is within the frozen caliper [vlo, vhi] x the parent's.
LINKS (rule 3): every draw is an EDGE (parent fire, candidate time, side, weight = 1 / matches of that parent): the target averages
alarms; a candidate shared by several parents stays linked to each; a candidate drawn by parents of opposite sides is two evaluations.
One random stream per parent (seed + crc32(fid), S5): adding a parent never redraws another.
CENSUS and BALANCE (rule 4): every parent appears (MATCHED, NO_ELIGIBLE, NO_COVARIATE, NO_SIDE; parents outside first..last counted in
the manifest, S4). BALANCE per month and ALL (M3): SMD before = every parent with a covariate (matched and NO_ELIGIBLE) vs the
time-eligible pool, each parent's pool weighted 1 / its size (S3); SMD after = matched parents vs their matches weighted 1 / n; the
median covariate of unmatched vs matched parents (the supported population named); the share of matches within 30 min before their own
parent and within its horizon (S1; each edge carries the flag, so a sensitivity can drop them). Calipers never widen after a look.
SIDE (rule 5): each match inherits its parent's side: a conditional directional benchmark, not a trading policy.
SEAL (TOOL_DESIGN 3a, M4): a first, last or parent day that lab3/law.py refuses is refused at start, never turned into a census reason.
OX-CODE2 D13 (REVIEW_D13 308d2d5a): the parent's own outcome horizon stays in its part (else PARENT_OUT_OF_SPLIT, counted); one part's
parents read only that part's price days (and the day before it); constant but disjoint covariates give an infinite SMD, never 0.
V3.1 (q_471223 receipt): the manifest's parents_listed counted the last coin's parents (a loop name shadowed the whole list); fixed.
Pure functions here; the run (main, one process) writes EDGES, MOMENTS, CENSUS, BALANCE and a MANIFEST pinning every setting and source."""
import datetime as dt
import re
import zlib
import numpy as np

S0 = {'k': 10, 'tries': 400, 'days': 7, 'hour_band': 1.0, 'pre_end_s': 1800.0, 'pre_len_s': 3600.0, 'vlo': 0.8, 'vhi': 1.25,
      'away_s': 1800.0, 'horizon_s': 14466.0, 'min_closes': 60, 'gap_s': 60.0}
UTC = dt.timezone.utc


def month_of(t):
    return dt.datetime.fromtimestamp(float(t), UTC).strftime('%Y%m')


def day_of(t):
    return dt.datetime.fromtimestamp(float(t), UTC).strftime('%Y%m%d')


def split_from(path):
    """the frozen split from THE window table (WINDOWS_V1): BUILD's use text 'fit A-B, confirm C-D' and the CHECK row ->
    (('FIT', A, B), ('CONFIRM', C, D), ('CHECK', first, last)); refuses a table without them or parts outside their window"""
    rows = {}
    with open(path) as fh:
        lines = fh.read().splitlines()
    for l in lines:
        f = l.split('\t')
        if not l.startswith('#') and len(f) >= 4 and f[0] != 'window':
            rows[f[0]] = f
    m = re.search(r'fit (\d{8})-(\d{8}), confirm (\d{8})-(\d{8})', rows.get('BUILD', ['', '', '', ''])[3])
    if not m or 'CHECK' not in rows:
        raise ValueError('WINDOWS table %s has no BUILD fit/confirm split or no CHECK row: refused' % path)
    b, c = rows['BUILD'], rows['CHECK']; fa, fb, ca, cb = m.groups()
    if not (b[1] <= fa <= fb < ca <= cb <= b[2]):
        raise ValueError('split %s outside BUILD %s-%s: refused' % (m.groups(), b[1], b[2]))
    return (('FIT', fa, fb), ('CONFIRM', ca, cb), ('CHECK', c[1], c[2]))


def part_of(t, split):
    """the split part holding the UTC day of t; None outside every part (BLIND, or before the research window)"""
    d = day_of(t)
    for name, a, b in split:
        if a <= d <= b:
            return name
    return None


def pre_activity(ts, px, t, s=S0):
    """the pre-exposure covariate: sum of squared log returns of consecutive closes over (t - pre_end - pre_len, t - pre_end], anchored at
    the last close at or before the window start; NaN without an anchor, with fewer than min_closes closes, or when any gap (anchor to the
    first close, between closes, last close to the window end) exceeds gap_s: a hole is never a quiet window"""
    hi = t - s['pre_end_s']; lo = hi - s['pre_len_s']
    a, b = int(np.searchsorted(ts, lo, 'right')) - 1, int(np.searchsorted(ts, hi, 'right'))
    if a < 0 or b - a - 1 < s['min_closes']:
        return np.nan
    if np.max(np.diff(np.r_[ts[a:b], hi])) > s['gap_s']:
        return np.nan
    r = np.diff(np.log(px[a:b])); return float(np.sum(r * r))


def past_clear(t, alarms_sorted, away_s):
    """available-at-time eligibility: no alarm at a time in [t - away_s, t] (a LATER alarm never matters)"""
    j = int(np.searchsorted(alarms_sorted, t, 'right'))
    return not (j > 0 and t - alarms_sorted[j - 1] <= away_s)


def exclusion_times(alarms, parent_times):
    """M1: the alarm list's times merged with the run's parent times (one coin), sorted: a parent missing from the alarm list still
    excludes the candidates just after it"""
    return np.unique(np.r_[np.asarray(alarms, float), np.asarray(parent_times, float)])


def same_window(t, parent_t, horizon_s, split):
    """M2, OX-CODE2 D13-01: the parent, ITS outcome horizon, the candidate and its horizon lie in ONE split part (FIT / CONFIRM / CHECK);
    outside every part never"""
    p = part_of(parent_t, split)
    return p is not None and part_of(parent_t + horizon_s, split) == p and part_of(t, split) == p and part_of(t + horizon_s, split) == p


def days_for(have, parent_times, part, split, s):
    """OX-CODE2 D13-02: the price days one part's parents may read: inside that part (plus the day before it starts, the earlier
    candidates' covariate) and within days + 1 of a parent; a later part's day is never read"""
    a, b = {n: (x, y) for n, x, y in split}[part]; a0 = (dt.datetime.strptime(a, '%Y%m%d') - dt.timedelta(days=1)).strftime('%Y%m%d')
    lo = min(parent_times) - (s['days'] + 1) * 86400; hi = max(parent_times) + (s['days'] + 1) * 86400
    return [d for d in have if a0 <= str(d) <= b and lo - 86400 <= _day_start(d) <= hi]


def draw(rng, parent_t, ts, px, alarms_sorted, day_starts, s):
    """-> (matches [(t, cov)], cov0, reason, pool_covs): up to k eligible candidates; pool_covs = covariates of every candidate that passed
    the time rules (for the balance-before table)"""
    if part_of(parent_t + s['horizon_s'], s['split']) != part_of(parent_t, s['split']):
        return [], np.nan, 'PARENT_OUT_OF_SPLIT', []                          # D13-01: its own outcome leaves the part
    cov0 = pre_activity(ts, px, parent_t, s)
    if not np.isfinite(cov0) or cov0 <= 0:
        return [], cov0, 'NO_COVARIATE', []
    d0 = parent_t - parent_t % 86400; hr = (parent_t - d0) / 3600.0
    days = [d for d in day_starts if abs(d - d0) <= s['days'] * 86400]; out, pool = [], []
    for _ in range(int(s['tries'])):
        if len(out) >= s['k'] or not days:
            break
        d = days[int(rng.integers(len(days)))]; t = d + ((hr + rng.uniform(-s['hour_band'], s['hour_band'])) % 24.0) * 3600.0
        if not past_clear(t, alarms_sorted, s['away_s']) or not same_window(t, parent_t, s['horizon_s'], s['split']):
            continue
        v = pre_activity(ts, px, t, s)
        if not np.isfinite(v):
            continue
        pool.append(v)
        if s['vlo'] * cov0 <= v <= s['vhi'] * cov0:
            out.append((float(t), v))
    return out, cov0, ('' if out else 'NO_ELIGIBLE'), pool


def edges_for(parent, matches):
    """parent = (coin, t, side, fid) -> edge rows (fid, coin, parent_t, cand_t, side, weight 1/n, draw_index)"""
    coin, t, side, fid = parent; n = len(matches)
    return [(fid, coin, float(t), float(m[0]), int(side), 1.0 / n, i) for i, m in enumerate(matches)]


def own_flag(parent_t, cand_t, horizon_s):
    """S1: BEFORE_30M (the candidate lies in the 30 min before its own parent), WITHIN_H (its horizon and the parent's overlap), '' else"""
    if 0 < parent_t - cand_t <= 1800.0:
        return 'BEFORE_30M'
    return 'WITHIN_H' if abs(cand_t - parent_t) < horizon_s else ''


def moments(edges):
    """unique (coin, cand_t, side) evaluations with their multiplicity (parents linked); opposite sides stay two rows"""
    cnt = {}
    for fid, coin, pt, ct, side, w, i in edges:
        k = (coin, round(ct, 3), side); cnt.setdefault(k, []).append(fid)
    return sorted(((c, t, sd, len(f), '|'.join(sorted(set(f)))) for (c, t, sd), f in cnt.items()), key=lambda r: (r[1], r[0], r[2]))


def smd_w(a, wa, b, wb):
    """weighted standardized mean difference of log covariates (balance): (mean a - mean b) / pooled sd, weights normalised per side"""
    a, wa, b, wb = (np.asarray(x, float) for x in (a, wa, b, wb))
    ka, kb = (a > 0) & (wa > 0), (b > 0) & (wb > 0)
    if ka.sum() < 2 or kb.sum() < 2:
        return np.nan
    la, lb = np.log(a[ka]), np.log(b[kb]); wa, wb = wa[ka] / wa[ka].sum(), wb[kb] / wb[kb].sum()
    ma, mb = np.sum(wa * la), np.sum(wb * lb); sd = np.sqrt((np.sum(wa * (la - ma) ** 2) + np.sum(wb * (lb - mb) ** 2)) / 2.0)
    if sd > 0:
        return float((ma - mb) / sd)
    return 0.0 if ma == mb else float(np.sign(ma - mb) * np.inf)            # D13-03: constant but disjoint groups are not balanced


def balance(rows):
    """rows (month, kind, cov, weight, own) with kind PARENT_MATCHED / PARENT_UNMATCHED / POOL / MATCH -> one row per month and ALL:
    (month, parents with a covariate, matched, unmatched, SMD before, SMD after, median cov unmatched, median cov matched, matches,
    share BEFORE_30M, share within the parent's horizon)"""
    out = []
    for m in sorted({r[0] for r in rows}) + ['ALL']:
        sel = [r for r in rows if m == 'ALL' or r[0] == m]

        def pick(kinds):
            return [r[2] for r in sel if r[1] in kinds], [r[3] for r in sel if r[1] in kinds]
        par, wp = pick(('PARENT_MATCHED', 'PARENT_UNMATCHED')); pool, wpool = pick(('POOL',))
        mp, wmp = pick(('PARENT_MATCHED',)); mt, wmt = pick(('MATCH',)); um, _ = pick(('PARENT_UNMATCHED',))
        own = [r[4] for r in sel if r[1] == 'MATCH']; n = len(own)
        out.append((m, len(par), len(mp), len(um), smd_w(par, wp, pool, wpool), smd_w(mp, wmp, mt, wmt),
                    float(np.median(um)) if um else np.nan, float(np.median(mp)) if mp else np.nan, n,
                    own.count('BEFORE_30M') / n if n else np.nan, (n - own.count('')) / n if n else np.nan))
    return out


def draw_coin(coin, parents, alarms, ts, px, day_starts, seed, s):
    """parents [(t, side, fid)] of one coin, sorted -> (edges, census rows, balance rows); the exclusion list merges the parents (M1); one
    random stream per parent (S5); each parent's pool weighted 1 / its size (S3)"""
    excl = exclusion_times(alarms, [p[0] for p in parents]); edges, census, bal = [], [], []
    for t, side, fid in parents:
        rng = np.random.default_rng(seed + zlib.crc32(str(fid).encode()) % 1000000007)
        out, cov0, why, pool = draw(rng, t, ts, px, excl, day_starts, s)
        census.append((fid, coin, t, side, len(out), why or 'MATCHED', cov0)); m = month_of(t)
        if np.isfinite(cov0) and cov0 > 0:
            bal.append((m, 'PARENT_MATCHED' if out else 'PARENT_UNMATCHED', cov0, 1.0, ''))
        bal += [(m, 'POOL', v, 1.0 / len(pool), '') for v in pool]
        if out:
            e = edges_for((coin, t, side, fid), out); edges += e
            bal += [(m, 'MATCH', v, 1.0 / len(out), own_flag(t, ct, s['horizon_s'])) for ct, v in out]
    return edges, census, bal


# ---------------------------------------------------------------- the run (waits for the backfill gate RUN; one process)
def coin_arrays(cache, coin, days):
    """the coin's 3 s closes over the given days, through labcore.prices (one read per coin-day), seconds and prices; a NaN or
    non-positive close is dropped, so it reads as a gap"""
    te, px = [], []
    for d in days:
        x = cache.day(coin, d); te.append(np.asarray(x['te_us'], np.int64)); px.append(np.asarray(x['px'], float))
    te = np.concatenate(te) if te else np.zeros(0, np.int64); px = np.concatenate(px) if px else np.zeros(0)
    ok = np.isfinite(px) & (px > 0); return te[ok] / 1e6, px[ok]


def _day_start(d):
    d = str(d); return dt.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), tzinfo=UTC).timestamp()


def select_parents(rows, first, last):
    """S4: -> (parents with a side inside first..last, NO_SIDE rows inside, count outside first..last): nothing dropped silently"""
    inside = [r for r in rows if first <= day_of(float(r['t'])) <= last]
    return [r for r in inside if int(float(r['side'])) != 0], [r for r in inside if int(float(r['side'])) == 0], len(rows) - len(inside)


def fid_of(r):
    return r.get('fid') or '%s_%d' % (r['coin'], int(float(r['t'])))


def main(parents_tsv, alarms_tsv, lab_days, out_dir, first, last, seed=20261023, law=None, windows_path=None):
    """parents: an EVENTS list (coin, t, side[, fid]); alarms: the alarm list whose past times exclude candidates (same coin; the parents
    are merged in); writes EDGES_V3.tsv, MOMENTS_V3.tsv (an EVENTS list for alarm_context / alarm_stamp), CENSUS_V3.tsv, BALANCE_V3.tsv,
    MANIFEST_V3.json"""
    import csv, hashlib, json, os, sys
    tools = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')); sys.path.insert(0, tools)
    from labcore import gates
    law = law or gates.load_law(); seed = int(seed)
    for d in (first, last):                                                    # M4: refused at start, never a wrong census reason
        if law.research_refusal(str(d)):
            raise PermissionError('day %s refused by lab3/law.py: %s' % (d, law.research_refusal(str(d))))
    wpath = windows_path or gates.WINDOWS; s = dict(S0, split=split_from(wpath))
    sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    allp = list(csv.DictReader(open(parents_tsv), delimiter='\t'))
    P, noside, n_out = select_parents(allp, first, last)
    bad = sorted({day_of(float(r['t'])) for r in P + noside if law.research_refusal(day_of(float(r['t'])))})
    if bad:
        raise PermissionError('parents on days lab3/law.py refuses: %s' % bad[:5])
    outside = sorted({day_of(float(r['t'])) for r in P if part_of(float(r['t']), s['split']) is None})
    if outside:
        raise PermissionError('parents outside every split part (FIT / CONFIRM / CHECK): %s' % outside[:5])
    A = {}
    for r in csv.DictReader(open(alarms_tsv), delimiter='\t'):
        A.setdefault(r['coin'], []).append(float(r['t']))
    for r in noside:                                                           # SCOUT 15:09:23Z: side-0 parents are alarms too
        A.setdefault(r['coin'], []).append(float(r['t']))
    by = {}
    for r in P:
        by.setdefault(r['coin'], []).append((float(r['t']), int(float(r['side'])), fid_of(r)))
    from labcore.prices import PriceCache
    cache = PriceCache(lab_days); have = sorted(d for d in cache.R.days() if not law.research_refusal(str(d)))
    E, C, BAL = [], [], []
    for coin in sorted(by):
        cps = sorted(by[coin]); excl = A.get(coin, []) + [p[0] for p in cps]   # cps: this coin's parents (allp stays the whole list)
        for part in sorted({part_of(p[0], s['split']) for p in cps}):          # D13-02: one part's parents read only that part's days
            pts = [p for p in cps if part_of(p[0], s['split']) == part]; days = days_for(have, [p[0] for p in pts], part, s['split'], s)
            ts, px = coin_arrays(cache, coin, days)
            e, c, b = draw_coin(coin, pts, excl, ts, px, [_day_start(d) for d in days], seed, s)
            E += e; C += c; BAL += b
            for k in [k for k in cache.mem if k[0] == coin]:                   # memory: one coin-part's days at a time
                cache.mem.pop(k, None)
    C += [(fid_of(r), r['coin'], float(r['t']), 0, 0, 'NO_SIDE', np.nan) for r in noside]
    os.makedirs(out_dir, exist_ok=True)

    def put(name, hdr, rows):
        p = os.path.join(out_dir, name)
        if os.path.exists(p):
            raise FileExistsError(p)
        open(p + '.tmp', 'w').write('\t'.join(hdr) + '\n' + ''.join('\t'.join(str(x) for x in r) + '\n' for r in rows)); os.replace(p + '.tmp', p)
        return sha(p)
    bal = balance(BAL); H = s['horizon_s']
    out = {'EDGES_V3.tsv': put('EDGES_V3.tsv', ('fid', 'coin', 'parent_t', 'cand_t', 'side', 'weight', 'draw_index', 'own'),
                               [x + (own_flag(x[2], x[3], H),) for x in E]),
           'MOMENTS_V3.tsv': put('MOMENTS_V3.tsv', ('coin', 't', 'side', 'S', 'mode', 'forced', 'parents', 'fids'),
                                  [(c, '%.3f' % t, sd, '', 'MATCH', 'SHORTS' if sd > 0 else 'LONGS', n, f) for c, t, sd, n, f in moments(E)]),
           'CENSUS_V3.tsv': put('CENSUS_V3.tsv', ('fid', 'coin', 't', 'side', 'matches', 'status', 'cov0'), C),
           'BALANCE_V3.tsv': put('BALANCE_V3.tsv', ('month', 'parents_with_cov', 'matched', 'unmatched', 'smd_before', 'smd_after',
                                                    'median_cov_unmatched', 'median_cov_matched', 'matches', 'share_before_30m',
                                                    'share_within_h'), [tuple('%.4f' % x if isinstance(x, float) else x for x in r) for r in bal])}
    n_m = [c[4] for c in C if c[5] == 'MATCHED']
    man = {'tool': 'alarm_match/draw_v3.py', 'code_sha16': sha(__file__), 'settings': s, 'seed': seed, 'first': first, 'last': last,
           'estimand': 'conditional prediction at alarm time vs the available-at-time no-alarm risk set (S06 rule 1); not a total causal effect',
           'side_rule': 'inherited from the parent: a conditional directional benchmark (S06 rule 5)',
           'census': {'parents_listed': len(allp), 'outside_first_last': n_out, 'no_side': len(noside), 'drawn': len(P),
                      'status': {k: sum(1 for c in C if c[5] == k) for k in ('MATCHED', 'NO_ELIGIBLE', 'NO_COVARIATE', 'PARENT_OUT_OF_SPLIT', 'NO_SIDE')},
                      'matches_per_matched_parent': {'min': min(n_m, default=0), 'median': float(np.median(n_m)) if n_m else 0.0,
                                                     'max': max(n_m, default=0), 'below_k': sum(1 for n in n_m if n < s['k'])}},
           'sources': {'parents': sha(parents_tsv), 'alarms': sha(alarms_tsv), 'windows': sha(wpath), 'law': sha(gates.LAW)}, 'outputs': out}
    p = os.path.join(out_dir, 'MANIFEST_V3.json'); open(p + '.tmp', 'w').write(json.dumps(man, indent=1, sort_keys=True)); os.replace(p + '.tmp', p)
    a = bal[-1]
    print('DRAW V3 parents %d matched %d edges %d moments %d SMD before %.3f after %.3f own before_30m %.3f within_h %.3f' % (
        len(C), man['census']['status']['MATCHED'], len(E), len(moments(E)), a[4], a[5], a[9], a[10]))


if __name__ == '__main__':
    import sys
    main(*sys.argv[1:7])
