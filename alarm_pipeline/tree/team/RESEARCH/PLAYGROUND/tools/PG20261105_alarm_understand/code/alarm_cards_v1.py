#!/usr/bin/env python3
"""alarm_cards_v1.py (SCO-A150 for SCOUT, 6 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED: never a PASS.
The mechanism card writer asked by REQUEST_ALARM_CARD_TOOL_V1.md (STR-TOOLREQ-AU1): one command per mechanism with an alarm-list
config writes ALARM_CARDS_<MECHANISM>.tsv (alarm, q, answer, number, source, sha16, strength) and ALARM_CARDS_<MECHANISM>.md
(Part A: one 8-line card per alarm, a GRADE line and an 'after the fire (description)' line; Part B: exactly 4 knowledge lines,
nothing about stage 2: PACK_V3/PART_ALARM_CARDS_TEMPLATE_V1.md, the owner 14:16Z). The TSV holds q = Q1..Q8 and GRADE (the template).
Knowledge only: answers describe the event; no answer names a trade side (checked on the written text: REFUSED SIDE_WORD).
  python3 -B alarm_cards_v1.py <new out dir> --mechanism <NAME> --config <ALARMS_<NAME>.tsv> [--grades GRADES.tsv]
CONFIG (tab separated, '#' comments): alarm, block (SEPDEC 20250910..20251231 or JANMAR 20260101..20260331), bundle (FIRES.tsv and
MONEY.tsv, bundle_builder --from-gg), def, def_sha16 (checked), readings (READINGS.tsv, FORCED.tsv, MATCH_PARENT.tsv, readings_builder_v1), grade_key (the
GRADES.tsv alarm column, or '-'). A missing input never stops the card: its questions read UNKNOWN and name the input.
REUSED (pinned by alarm_understand_v1.release(), never rewritten): i2g_rules_v1_2.build_clusters (events = waves: 30 min gap, 4 h span,
any coin, weight 1/size), i2g_rules_v1_2.clustered_mean (event-clustered mean and error), lab3 law.py research_refusal (closed days).
RULES, FIXED BEFORE ANY RUN (6 Nov 2026 14:20Z, before any real card of this tool):
  WINDOW    blocks lie in 20250901..20260331 (Sep 2025 to Mar 2026 only; BLOCK_CLOSED otherwise); a fire on a law-closed day is dropped.
  AS OF     a reading is used only when known_at <= t (the fire second); a later one is counted as AFTER and never used in Q1-Q5.
            MONEY is always after the fire: it feeds only Q7, Q8 and the 'after the fire (description)' line.
  VS MATCH  a fire's percentile = its value's place among the matched moments of the same month (the parent's month; ties half);
            score = event-clustered mean of (percentile - 50); error = clustered error plus the matched side's 100^2/12/n; z = score/error.
  WORDS     SOLID = measured, 30+ events, |z| >= z_crit (Bonferroni, family-wise 0.01 over the card's tests) where a comparison
            exists, and the same sign in every month of the block (every month with 5+ events); WEAK = measured, thin or mixed;
            UNKNOWN = no data, the missing input is named.
  Q1        the event: the forced side (longs on a down push, shorts on an up push) holds the larger 15 min liquidations (FORCED.tsv);
            SOLID when that holds for 2 of 3 fires (event-weighted) overall and in every month.
  Q3 RULE   per fire, against the same month's matched moments: BTC-led when BTC's 15 min move the same way (btc_move_15m) is in the
            top 10 pct of the matched moments; else market when the typical coin's 15 min move (basket_move_15m) is; else one venue
            when the Binance mark premium over spot (|basis_push_bp|) is; else coin alone. Matched moments are classed by the same rule
            against their own pool. The class with the largest fire-minus-matched share is the answer.
  Q4        the forced side as Q1 plus forced_log_usd_15m vs matched moments.
  Q2, Q5    the reading with the largest |z| among the question's readings.
  AFTER     impact retained 1 h = 1 - (price give-back over 1 h, MONEY fade_gross_1h) / (move in, CTX move_15m); temporary when
            retained < 0.5, permanent otherwise. Description only, never in Q1-Q5.
  Q6        UNKNOWN on every card: needs an absorber reading after the fire (X1.FLOWX / X1.HLFLOWX absorber side), built with LAYERS.
  Q7        event result = sum of weight x MONEY net (the store's 1 h honest-cost column) over the event's fires; top 1 and top 5
            shares of the total, total without the best event; SOLID when the month-by-month reading agrees in every month.
  Q8        events split by size (1, 2-5, 6+ fires) and breadth (1 coin, more coins); single-coin minus multi-coin mean result, z.
Exit 0 written, 2 REFUSED <CODE>, 3 FAILED."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, datetime as dt, hashlib, importlib.util, math, os, re, statistics, time
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
EDITION = 'alarm_cards V1 (playground PG20261105_alarm_understand, SCO-A150 6 Nov 2026, TEST, NOT REVIEWED: never a PASS)'
BLOCKS = {'SEPDEC': ('20250910', '20251231'), 'JANMAR': ('20260101', '20260331')}
WINDOW = ('20250901', '20260331')
SIDE_WORDS = ('fade', 'follow', 'buy', 'sell', 'long entry', 'short entry')
ALPHA, MIN_EVENTS, MIN_MONTH_EVENTS, CUT = 0.01, 30, 5, 90.0
QV = {2: ('hour_utc', 'weekday', 'fires_other_60m', 'alarms_all_24h', 'btc_vol_regime', 'market_hot_rank_30d'),
      4: ('forced_log_usd_15m',),
      5: ('fills_one_sided', 'volume_one_sided', 'whale_net_5m_usd', 'funding_forced_pays_bp', 'forced_over_taker_15m')}
MEAN = {'hour_utc': 'the hour of day (UTC)', 'weekday': 'the weekday', 'fires_other_60m': 'other coins firing in the hour before',
        'alarms_all_24h': 'fires of all coins in the 24 h before', 'btc_vol_regime': 'BTC volatility against its usual',
        'market_hot_rank_30d': 'the market heat rank of 30 days', 'forced_log_usd_15m': 'forced-side liquidations over 15 min',
        'fills_one_sided': 'how one-sided the last 1,000 fills were', 'volume_one_sided': 'the one-sided share of the last 50 volume buckets',
        'whale_net_5m_usd': 'big trades with the push over 5 min', 'funding_forced_pays_bp': 'the funding paid by the forced side',
        'forced_over_taker_15m': 'forced dollars over aggressive dollars in the push'}
CLASSES = ('coin alone', 'market', 'BTC-led', 'one venue')
TSV_COLS = ('alarm', 'q', 'answer', 'number', 'source', 'sha16', 'strength')
QNAME = {'GRADE': 'versus random moments (kit GRADE)', 1: 'what type', 2: 'when', 3: 'why', 4: 'who is forced', 5: 'who is paying', 6: 'money from whom', 7: 'carried by events',
         8: 'single events'}


class Refused(Exception):
    def __init__(self, code, detail=''):
        super().__init__('%s %s' % (code, detail)); self.code = code; self.detail = detail


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def day_of(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def read_tsv(p):
    with open(p) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return float('nan')
    return v


def fmt(x, d=2, sign=False):
    if x is None or not np.isfinite(x):
        return 'nan'
    return ('%+.*f' if sign else '%.*f') % (d, x)


_REL = None


def release():
    """the pinned release modules through alarm_understand_v1 (its pins checked there): RU (build_clusters, clustered_mean), LAW"""
    global _REL
    if _REL is None:
        sp = importlib.util.spec_from_file_location('alarm_understand_for_cards', os.path.join(HERE, 'alarm_understand_v1.py'))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _REL = m.release()
    return _REL


def cmean(RU, x, w, cl):
    x = np.asarray(x, float); w = np.asarray(w, float); ok = np.isfinite(x)
    if not ok.any():
        return dict(mean=float('nan'), se=float('nan'))
    r = RU.clustered_mean(x[ok], w[ok], np.asarray(cl, dtype=object)[ok])
    return dict(mean=float(r['mean']), se=float(r['se']))


def wmedian(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float); ok = np.isfinite(x) & (w > 0)
    if not ok.any():
        return float('nan')
    o = np.argsort(x[ok], kind='stable'); xs, ws = x[ok][o], w[ok][o]; c = np.cumsum(ws)
    return float(xs[int(np.searchsorted(c, 0.5 * c[-1]))])


def z_crit(k):
    return statistics.NormalDist().inv_cdf(1.0 - ALPHA / (2.0 * max(k, 1)))


# ------------------------------------------------------------------------------------------------ one alarm
def load_alarm(cfg, RU, law):
    first, last = BLOCKS[cfg['block']]
    srcs = {}
    out = dict(alarm=cfg['alarm'], block=cfg['block'], first=first, last=last, missing=[], srcs=srcs)
    fp = os.path.join(cfg['bundle'], 'FIRES.tsv')
    if not os.path.exists(fp):
        raise Refused('NO_INPUT', fp)
    srcs['FIRES'] = (fp, sha16_file(fp))
    allf = []
    for r in read_tsv(fp):
        t = int(num(r['t']))
        if law(int(day_of(t))) is None:
            allf.append((cfg['alarm'], r['coin'], t, int(num(r['side']))))
    U = RU.build_clusters(allf)
    wc, wt = {}, {}
    for r in U:
        wc.setdefault(r[5], set()).add(r[1]); wt.setdefault(r[5], []).append(r[2])
    F = [dict(coin=c, t=t, side=s, wave=cid, w=float(w), size=int(size), breadth=len(wc[cid]), month=day_of(t)[:6],
              span=(min(wt[cid]), max(wt[cid])))
         for (a, c, t, s, pid, cid, w, size, flag) in U if first <= day_of(t) <= last]
    F.sort(key=lambda x: (x['t'], x['coin']))
    out['F'] = F; out['months'] = sorted(set(x['month'] for x in F))
    out['events'] = sorted(set(x['wave'] for x in F)); out['spans'] = {x['wave']: x['span'] for x in F}
    out['side'] = int(np.sign(sum(x['side'] for x in F))) if F else 0
    mp = os.path.join(cfg['bundle'], 'MONEY.tsv')
    out['money'] = {}
    if os.path.exists(mp):
        srcs['MONEY'] = (mp, sha16_file(mp))
        for r in read_tsv(mp):
            out['money'][(r['coin'], int(num(r['t'])))] = (num(r['net']), num(r['fade_gross_1h']))
    else:
        out['missing'].append('MONEY.tsv (bundle --from-gg)')
    rd = cfg.get('readings', '-')
    out['fire_r'], out['match_r'], out['after_n'] = {}, {}, 0
    out['forced'] = {}
    rp = os.path.join(rd, 'READINGS.tsv')
    if rd != '-' and os.path.exists(rp):
        srcs['READINGS'] = (rp, sha16_file(rp))
        par = {}
        pp = os.path.join(rd, 'MATCH_PARENT.tsv')
        if os.path.exists(pp):
            for r in read_tsv(pp):
                par[(r['coin'], num(r['t']))] = day_of(num(r['parent_t']))[:6]
        fk = {(x['coin'], x['t']) for x in F}
        with open(rp) as fh:                                   # plain split: the file is ours (readings_builder), header checked
            hdr = None
            for line in fh:
                if line.startswith('#'):
                    continue
                p_ = line.rstrip('\n').split('\t')
                if hdr is None:
                    hdr = p_
                    if hdr != ['who', 'coin', 't', 'code', 'value', 'known_at']:
                        raise Refused('BAD_INPUT', '%s header %s' % (rp, hdr))
                    continue
                who, coin, t, code, v, ka = p_[0], p_[1], float(p_[2]), p_[3], float(p_[4]), float(p_[5])
                if code.startswith('CTX.'):
                    code = code[4:]
                r = {'who': who, 'coin': coin}
                load_one(out, r, code, t, ka, v, fk, par)
    else:
        out['missing'].append('READINGS.tsv (readings_builder_v1: alarm_context at the fire and at matched moments)')
    _forced(out, rd)
    return out


def load_one(out, r, code, t, ka, v, fk, par):
    """one READINGS row: FIRE rows of the block's fires and MATCH rows, as of their own second only (known_at <= t)"""
    if ka > t:
        out['after_n'] += 1
        return
    if r['who'] == 'FIRE':
        k = (r['coin'], int(t))
        if k in fk:
            out['fire_r'].setdefault(code, {})[k] = v
    else:
        m = par.get((r['coin'], t)) or day_of(t)[:6]
        out['match_r'].setdefault(code, {})[(r['coin'], t)] = (m, v)


def _forced(out, rd):
    srcs = out['srcs']
    fo = os.path.join(rd, 'FORCED.tsv')
    if rd != '-' and os.path.exists(fo):
        srcs['FORCED'] = (fo, sha16_file(fo))
        for r in read_tsv(fo):
            if num(r['known_at']) <= num(r['t']):
                out['forced'][(r['coin'], int(num(r['t'])))] = (num(r['long_usd']), num(r['short_usd']))
    else:
        out['missing'].append('FORCED.tsv (readings_builder_v1, CTX forced_log_usd_15m)')


def vs_match(A, RU, code, transform=None):
    """percentiles of the fires among the same month's matched values -> dict(score, z, per month, n events, fire median, match median)"""
    F = A['F']; fr = A['fire_r'].get(code, {}); mr = A['match_r'].get(code, {})
    tf = transform or (lambda v: v)
    pools = {}
    for (m, v) in mr.values():
        if np.isfinite(v):
            pools.setdefault(m, []).append(tf(v))
    pools = {m: np.sort(np.array(v)) for m, v in pools.items()}
    pct = np.full(len(F), np.nan); fv = np.full(len(F), np.nan)
    for i, x in enumerate(F):
        v = fr.get((x['coin'], x['t']), np.nan)
        if np.isfinite(v):
            fv[i] = tf(v)
            p = pools.get(x['month'])
            if p is not None and len(p) > 1:
                lo = np.searchsorted(p, fv[i], 'left'); hi = np.searchsorted(p, fv[i], 'right'); pct[i] = 100.0 * (lo + 0.5 * (hi - lo)) / len(p)
    return summarize(A, RU, pct - 50.0, pools, fv, extra_var=lambda m: (100.0 ** 2 / 12.0) / len(pools[m]) if m in pools else np.nan)


def summarize(A, RU, x, pools, fv, extra_var):
    F = A['F']; W = np.array([f['w'] for f in F]); CL = np.array([f['wave'] for f in F], dtype=object)
    MO = np.array([f['month'] for f in F], dtype=object); ok = np.isfinite(x)
    res = dict(n_fires=int(ok.sum()), n_events=len(set(CL[ok].tolist())), per={}, fire_median=wmedian(fv, W) if fv is not None else np.nan,
               match_n=int(sum(len(p) for p in pools.values())) if pools else 0)
    if not ok.any():
        res.update(score=np.nan, z=np.nan); return res
    c = cmean(RU, x[ok], W[ok], CL[ok])
    wsum = {m: W[ok & (MO == m)].sum() for m in A['months']}; tot = sum(wsum.values())
    vm = sum((wsum[m] / tot) ** 2 * extra_var(m) for m in A['months'] if wsum[m] > 0 and np.isfinite(extra_var(m))) if tot > 0 else np.nan
    se = math.sqrt(c['se'] ** 2 + (vm if np.isfinite(vm) else 0.0)) if np.isfinite(c['se']) else np.nan
    res.update(score=c['mean'], z=c['mean'] / se if se and np.isfinite(se) and se > 0 else np.nan)
    for m in A['months']:
        k = ok & (MO == m)
        res['per'][m] = (cmean(RU, x[k], W[k], CL[k])['mean'] if k.any() else np.nan, len(set(CL[k].tolist())))
    return res


def word(res, zc, months, need_z=True):
    if res is None or res.get('n_fires', 0) == 0 or not np.isfinite(res.get('score', np.nan)):
        return 'UNKNOWN'
    s = np.sign(res['score'])
    same = all(np.isfinite(res['per'].get(m, (np.nan, 0))[0]) and res['per'][m][1] >= MIN_MONTH_EVENTS and np.sign(res['per'][m][0]) == s
               for m in months) and s != 0
    zok = (not need_z) or (np.isfinite(res['z']) and abs(res['z']) >= zc)
    return 'SOLID' if (res['n_events'] >= MIN_EVENTS and same and zok) else 'WEAK'


def months_txt(res, d=1):
    return ' '.join('%s:%s' % (m, fmt(v, d, True)) for m, (v, n) in sorted(res['per'].items()))


def q3_classes(A, RU):
    """the Q3 rule on fires and on matched moments; -> table rows and the headline"""
    F = A['F']
    need = ('btc_move_15m', 'basket_move_15m', 'basis_push_bp')
    if any(not A['match_r'].get(c) for c in need):
        return None
    pools = {}
    for c in need:
        tf = abs if c == 'basis_push_bp' else (lambda v: v)
        for (m, v) in A['match_r'][c].values():
            if np.isfinite(v):
                pools.setdefault((c, m), []).append(tf(v))
    pools = {k: np.sort(np.array(v)) for k, v in pools.items()}

    def pc(c, m, v):
        p = pools.get((c, m))
        if p is None or len(p) < 2 or not np.isfinite(v):
            return np.nan
        v = abs(v) if c == 'basis_push_bp' else v
        lo = np.searchsorted(p, v, 'left'); hi = np.searchsorted(p, v, 'right'); return 100.0 * (lo + 0.5 * (hi - lo)) / len(p)

    def cls(m, b, k, s):
        pb, pk, ps = pc('btc_move_15m', m, b), pc('basket_move_15m', m, k), pc('basis_push_bp', m, s)
        if not (np.isfinite(pb) and np.isfinite(pk)):
            return None
        if pb >= CUT:
            return 'BTC-led'
        if pk >= CUT:
            return 'market'
        if np.isfinite(ps) and ps >= CUT:
            return 'one venue'
        return 'coin alone'
    fc = []
    for x in F:
        k = (x['coin'], x['t'])
        fc.append(cls(x['month'], *(A['fire_r'].get(c, {}).get(k, np.nan) for c in need)))
    mc = {}
    for key, (m, b) in A['match_r']['btc_move_15m'].items():
        kk = A['match_r']['basket_move_15m'].get(key, (m, np.nan))[1]; ss = A['match_r']['basis_push_bp'].get(key, (m, np.nan))[1]
        c = cls(m, b, kk, ss)
        if c:
            mc.setdefault(m, []).append(c)
    W = np.array([f['w'] for f in F]); rows = []; best = None
    for c in CLASSES:
        ind = np.array([np.nan if v is None else float(v == c) for v in fc])
        p0 = {m: (np.mean([v == c for v in mc[m]]) if mc.get(m) else np.nan) for m in A['months']}
        x = np.array([ind[i] - p0.get(F[i]['month'], np.nan) for i in range(len(F))])
        res = summarize(A, RU, x, {m: mc[m] for m in mc}, None,
                        extra_var=lambda m: (p0[m] * (1 - p0[m]) / len(mc[m])) if mc.get(m) and np.isfinite(p0.get(m, np.nan)) else np.nan)
        ok = np.isfinite(ind)
        fs = float((ind[ok] * W[ok]).sum() / W[ok].sum()) if ok.any() else np.nan
        allm = [v for m in mc for v in mc[m]]
        ms = float(np.mean([v == c for v in allm])) if allm else np.nan
        rows.append(dict(cls=c, fire_share=fs, match_share=ms, res=res))
        if np.isfinite(res['score']) and (best is None or res['score'] > best['res']['score']):
            best = rows[-1]
    unk = sum(1 for v in fc if v is None)
    return dict(rows=rows, best=best, unknown=unk)


def card(A, RU, grades, zc_k=None):
    """-> list of (q, answer, number, source, sha16, strength), after line, grading line, extras"""
    F, months, srcs = A['F'], A['months'], A['srcs']
    ev = len(A['events']); side = A['side']
    push = 'falling' if side < 0 else 'rising'; fside = 'longs' if side < 0 else 'shorts'
    has_r = 'READINGS' in srcs
    S = lambda k: (os.path.basename(srcs[k][0]), srcs[k][1]) if k in srcs else ('-', '-')
    tests = {}
    if has_r:
        for q in (2, 4, 5):
            for c in QV[q]:
                if A['fire_r'].get(c) and A['match_r'].get(c):
                    tests[(q, c)] = vs_match(A, RU, c)
    q3 = q3_classes(A, RU) if has_r else None
    k = len([r for r in tests.values() if np.isfinite(r['z'])]) + (1 if q3 else 0) + 2
    zc = z_crit(k)
    rows = []
    W = np.array([f['w'] for f in F])
    # ---- Q1 and Q4: the forced side
    fres = None
    if A['forced']:
        ind = []
        for f in F:
            lo, sh = A['forced'].get((f['coin'], f['t']), (np.nan, np.nan))
            a, b = (lo, sh) if side < 0 else (sh, lo)
            ind.append(np.nan if not (np.isfinite(a) and np.isfinite(b)) or (a + b) <= 0 else float(a > b))
        ind = np.array(ind)
        fres = summarize(A, RU, ind - 2.0 / 3.0, {}, None, extra_var=lambda m: np.nan)
        ok = np.isfinite(ind); share = float((ind[ok] * W[ok]).sum() / W[ok].sum()) if ok.any() else np.nan
        fres['share'] = share
    mv = A['fire_r'].get('move_15m', {})
    mvm = wmedian([mv.get((f['coin'], f['t']), np.nan) for f in F], W) if mv else np.nan
    oi = A['fire_r'].get('oi_chg_10m', {})
    oim = wmedian([oi.get((f['coin'], f['t']), np.nan) for f in F], W) if oi else np.nan
    if fres is not None and np.isfinite(fres.get('share', np.nan)):
        w1 = word(fres, zc, months, need_z=False)
        rows.append((1, '%s forced out of a %s coin: the coin moved a median %s pct over 15 min in the push, the %s side held the larger '
                     '15 min liquidations in %s pct of fires, open interest changed a median %s pct over 10 min'
                     % (fside.capitalize(), push, fmt(mvm), fside, fmt(100 * fres['share'], 0), fmt(oim)),
                     'forced-side share %.3f; events %d; by month (share minus 2/3) %s' % (fres['share'], ev, months_txt(fres, 2)),
                     S('FORCED')[0], S('FORCED')[1], w1))
    else:
        rows.append((1, 'UNKNOWN: the event type needs FORCED.tsv (15 min liquidations by side at the fire)', 'events %d' % ev, '-', '-', 'UNKNOWN'))
    # ---- Q2: when
    bym = {m: (sum(1 for f in F if f['month'] == m), len(set(f['wave'] for f in F if f['month'] == m))) for m in months}
    hours = {}
    for f in F:
        h = dt.datetime.fromtimestamp(f['t'], dt.timezone.utc).hour; hours[h] = hours.get(h, 0) + 1
    ph = max(hours, key=hours.get) if hours else -1
    cand = [(c, r) for (q, c), r in tests.items() if q == 2 and np.isfinite(r['z'])]
    whentxt = 'in events by month %s; most fires at %02d UTC (%d)' % (' '.join('%s:%d' % (m, bym[m][1]) for m in months), ph, hours.get(ph, 0))
    if cand:
        c, r = max(cand, key=lambda x: abs(x[1]['z']))
        rows.append((2, 'Fires come %s; %s is %s than at matched moments' % (whentxt, MEAN[c], 'higher' if r['score'] > 0 else 'lower'),
                     '%s fire percentile %s (z %s, z_crit %.2f, %d events); by month %s' % (c, fmt(50 + r['score'], 1), fmt(r['z'], 2, True), zc,
                                                                                           r['n_events'], months_txt(r)),
                     S('READINGS')[0], S('READINGS')[1], word(r, zc, months)))
    else:
        rows.append((2, 'Fires come %s; no reading against matched moments' % whentxt, 'fires %d, events %d' % (len(F), ev),
                     S('FIRES')[0], S('FIRES')[1], 'WEAK' if F else 'UNKNOWN'))
    # ---- Q3: why (the table)
    if q3 and q3['best']:
        b = q3['best']; tab = ', '.join('%s %s (matched %s)' % (r['cls'], fmt(100 * r['fire_share'], 0), fmt(100 * r['match_share'], 0)) for r in q3['rows'])
        rows.append((3, 'The move is mostly %s; shares of fires %s; rule: BTC-led if BTC 15 min move in the matched top 10 pct, else market '
                     'if the typical coin move is, else one venue if the mark premium over spot is, else coin alone' % (b['cls'], tab),
                     '%s fire minus matched share %s (z %s); by month %s; unclassed fires %d' % (b['cls'], fmt(100 * b['res']['score'], 1, True),
                                                                                                 fmt(b['res']['z'], 2, True), months_txt(b['res'], 2), q3['unknown']),
                     S('READINGS')[0], S('READINGS')[1], word(b['res'], zc, months)))
    else:
        rows.append((3, 'UNKNOWN: the coin alone / market / BTC-led / one venue table needs READINGS.tsv with btc_move_15m, basket_move_15m and '
                     'basis_push_bp at fires and matched moments', '-', '-', '-', 'UNKNOWN'))
    # ---- Q4: who is forced
    r4 = tests.get((4, 'forced_log_usd_15m'))
    if fres is not None and r4 is not None:
        named = fres['share'] >= 2.0 / 3.0
        w4 = word(r4, zc, months) if named else 'WEAK'
        rows.append((4, '%s: the %s side held the larger 15 min liquidations in %s pct of fires; %s are %s than at matched moments'
                     % (fside.capitalize() if named else 'Mixed', fside, fmt(100 * fres['share'], 0), MEAN['forced_log_usd_15m'],
                        'higher' if r4['score'] > 0 else 'lower'),
                     'forced_log_usd_15m fire percentile %s (z %s); by month %s' % (fmt(50 + r4['score'], 1), fmt(r4['z'], 2, True), months_txt(r4)),
                     S('FORCED')[0], S('FORCED')[1], w4))
    else:
        rows.append((4, 'UNKNOWN: who is forced needs FORCED.tsv and READINGS.tsv forced_log_usd_15m at fires and matched moments', '-', '-', '-', 'UNKNOWN'))
    # ---- Q5: who is paying
    cand = [(c, r) for (q, c), r in tests.items() if q == 5 and np.isfinite(r['z'])]
    if cand:
        c, r = max(cand, key=lambda x: abs(x[1]['z']))
        rows.append((5, 'The forced %s pay into the push; %s is %s than at matched moments' % (fside, MEAN[c], 'higher' if r['score'] > 0 else 'lower'),
                     '%s fire percentile %s (z %s); by month %s; others: %s' % (c, fmt(50 + r['score'], 1), fmt(r['z'], 2, True), months_txt(r),
                                                                                ', '.join('%s %s' % (cc, fmt(50 + rr['score'], 1)) for cc, rr in cand if cc != c)),
                     S('READINGS')[0], S('READINGS')[1], word(r, zc, months)))
    else:
        rows.append((5, 'UNKNOWN: who is paying needs READINGS.tsv flow readings (fills_one_sided, volume_one_sided, forced_over_taker_15m) '
                     'at fires and matched moments', '-', '-', '-', 'UNKNOWN'))
    # ---- Q6
    rows.append((6, 'UNKNOWN: needs an absorber reading after the fire (X1.FLOWX / X1.HLFLOWX absorber side), built with LAYERS through producer-design',
                 '-', '-', '-', 'UNKNOWN'))
    # ---- Q7, Q8: the store's 1 h result per event
    money = A['money']
    evr = {}; evm = {}; evsz = {}; evbr = {}
    for f in F:
        n = money.get((f['coin'], f['t']), (np.nan, np.nan))[0]
        if np.isfinite(n):
            evr[f['wave']] = evr.get(f['wave'], 0.0) + f['w'] * n; evm[f['wave']] = f['month']; evsz[f['wave']] = f['size']; evbr[f['wave']] = f['breadth']
    if len(evr) >= 2:
        v = np.array(sorted(evr.values(), reverse=True)); tot = float(v.sum())
        def carry(vals):
            vals = np.sort(np.array(vals))[::-1]; t_ = vals.sum()
            if t_ <= 0:
                return 'no positive total'
            if vals[1:].sum() <= 0:
                return 'carried by one event'
            if vals[5:].sum() <= 0:
                return 'carried by the top 5 events'
            return 'spread over events'
        allc = carry(v); perc = {m: carry([evr[e] for e in evr if evm[e] == m]) for m in months if sum(1 for e in evr if evm[e] == m) >= 2}
        w7 = 'SOLID' if (len(evr) >= MIN_EVENTS and len(perc) == len(months) and all(p == allc for p in perc.values())) else 'WEAK'
        rows.append((7, 'The 1 h result of the store (honest cost) is %s: top event %s pct and top 5 events %s pct of the total; without the best event %s'
                     % (allc, fmt(100 * v[0] / tot, 0) if tot > 0 else 'nan', fmt(100 * v[:5].sum() / tot, 0) if tot > 0 else 'nan', fmt(tot - v[0], 2, True)),
                     'total %s over %d events; by month %s' % (fmt(tot, 2, True), len(evr), '; '.join('%s:%s' % kv for kv in sorted(perc.items()))),
                     S('MONEY')[0], S('MONEY')[1], w7))
        one = np.array([evr[e] for e in evr if evbr[e] == 1]); many = np.array([evr[e] for e in evr if evbr[e] > 1])
        def mse(a):
            return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(len(a)))) if len(a) > 1 else (np.nan, np.nan)
        (m1, s1), (m2, s2) = mse(one), mse(many)
        d = m1 - m2; zz = d / math.sqrt(s1 ** 2 + s2 ** 2) if np.isfinite(s1) and np.isfinite(s2) and (s1 + s2) > 0 else np.nan
        perm = {}
        for m in months:
            a = [evr[e] for e in evr if evm[e] == m and evbr[e] == 1]; b = [evr[e] for e in evr if evm[e] == m and evbr[e] > 1]
            perm[m] = (np.mean(a) - np.mean(b), len(a) + len(b)) if a and b else (np.nan, len(a) + len(b))
        r8 = dict(score=d, z=zz, n_fires=len(F), n_events=len(evr), per=perm)
        sz = {}
        for e in evr:
            key = '1' if evsz[e] == 1 else ('2-5' if evsz[e] <= 5 else '6+')
            sz.setdefault(key, []).append(evr[e])
        rows.append((8, 'Single-coin events average %s and multi-coin events %s (1 h result per event, pct); by event size 1 / 2-5 / 6+ fires: %s'
                     % (fmt(m1, 3, True), fmt(m2, 3, True), ' / '.join('%s (%d)' % (fmt(np.mean(sz[k]), 3, True), len(sz[k])) if k in sz else 'none'
                                                                     for k in ('1', '2-5', '6+'))),
                     'single minus multi %s (z %s, z_crit %.2f); events %d single, %d multi; by month %s' % (fmt(d, 3, True), fmt(zz, 2, True), zc, len(one),
                                                                                                         len(many), months_txt(r8, 3)),
                     S('MONEY')[0], S('MONEY')[1], word(r8, zc, months)))
    else:
        for q in (7, 8):
            rows.append((q, 'UNKNOWN: needs MONEY.tsv (the store 1 h result per fire)', '-', '-', '-', 'UNKNOWN'))
    # ---- after the fire (description)
    ret = []
    for f in F:
        gb = money.get((f['coin'], f['t']), (np.nan, np.nan))[1]; mi = mv.get((f['coin'], f['t']), np.nan)
        ret.append(1.0 - gb / mi if np.isfinite(gb) and np.isfinite(mi) and mi > 0 else np.nan)
    ret = np.array(ret); ok = np.isfinite(ret)
    if ok.any():
        rm = wmedian(ret, W); tmp = float(((ret[ok] < 0.5) * W[ok]).sum() / W[ok].sum())
        after = ('Impact retained after 1 h: median %s of the 15 min move in (%s); temporary in %s pct of fires (retained under 0.5), permanent in %s pct'
                 % (fmt(rm), 'the price mostly comes back' if rm < 0.5 else 'the price mostly stays', fmt(100 * tmp, 0), fmt(100 * (1 - tmp), 0)),
                 'MONEY.tsv %s + READINGS.tsv %s' % (S('MONEY')[1], S('READINGS')[1]))
    else:
        after = ('UNKNOWN: impact retained needs MONEY.tsv and READINGS.tsv move_15m', '-')
    # ---- grading
    g = grades.get(A.get('grade_key') or '-')
    if g:
        gsrc = ('%s %s' % (g.get('grade_job', '-'), os.path.basename(g.get('result_file', '-'))), g.get('result_sha16', '-'))
        gword = 'SOLID' if g.get('state') == 'PASS' and g.get('months_passing') == g.get('months_counted') else 'WEAK'
        grading = ('lead over matched random moments %s pts at 15 min (t %s) and %s at 1 h (t %s), %s waves, %s of %s months passing; state %s (job %s)'
                   % (g['lead_15m'], g['t_15m'], g['lead_1h'], g['t_1h'], g['waves'], g['months_passing'], g['months_counted'], g['state'], g['grade_job']))
    else:
        grading = 'UNKNOWN: no GRADES_FORCED_FAMILY row for this alarm and block (the kit GRADE, STRATEGY)'
        gsrc, gword = ('-', '-'), 'UNKNOWN'
    rows.append(('GRADE', grading, g.get('waves', '-') + ' waves' if g else '-', gsrc[0], gsrc[1], gword))
    return rows, after, grading, dict(q3=q3, zc=zc, k=k, events=ev, fires=len(F))


def side_hits(text):
    """trade-side words in the text, after the sha16 tokens (16 hex digits, e.g. b10252c8fade7ae8 in job 20270165) are taken out"""
    low = re.sub(r'(?<![0-9a-z])[0-9a-f]{16}(?![0-9a-z])', ' ', text.lower())
    return [w for w in SIDE_WORDS if w in low]


def overlap(A, B, gap=1800):
    """share of A's events whose span lies within gap seconds of some B event span (any coin)"""
    bs = sorted(B['spans'].values())
    if not A['spans'] or not bs:
        return np.nan
    starts = np.array([s[0] for s in bs]); ends = np.array([s[1] for s in bs]); emax = np.maximum.accumulate(ends)
    hit = 0
    for a0, a1 in A['spans'].values():
        i = np.searchsorted(starts, a1 + gap, 'right')         # B events starting before a1 + gap
        if i and emax[i - 1] >= a0 - gap:
            hit += 1
    return hit / len(A['spans'])


def run(a):
    t0 = time.time()
    R = release(); RU = R.RU
    law = R.LAW.research_refusal
    cfg = read_tsv(a.config)
    for c in cfg:
        if c['block'] not in BLOCKS:
            raise Refused('BAD_BLOCK', c['block'])
        f, l = BLOCKS[c['block']]
        if not (WINDOW[0] <= f and l <= WINDOW[1]):
            raise Refused('BLOCK_CLOSED', c['block'])
    grades = {}
    if a.grades and os.path.exists(a.grades):
        for r in read_tsv(a.grades):
            grades[r['alarm']] = r
    os.makedirs(a.out, exist_ok=True)
    pt, pm = os.path.join(a.out, 'ALARM_CARDS_%s.tsv' % a.mechanism), os.path.join(a.out, 'ALARM_CARDS_%s.md' % a.mechanism)
    if os.path.exists(pt) or os.path.exists(pm):
        raise Refused('OUT_EXISTS', pt)
    cards = []
    for c in cfg:
        A = load_alarm(c, RU, law); A['grade_key'] = c.get('grade_key', '-')
        if c.get('def', '-') != '-':
            if not os.path.exists(c['def']):
                raise Refused('NO_INPUT', c['def'])
            if sha16_file(c['def']) != c.get('def_sha16'):
                raise Refused('SOURCE_CHANGED', '%s is %s, config says %s' % (c['def'], sha16_file(c['def']), c.get('def_sha16')))
        A['def_sha16'] = c.get('def_sha16', '-')
        rows, after, grading, ex = card(A, RU, grades)
        cards.append((c, A, rows, after, grading, ex))
    # ---- Part B
    main = [x for x in cards if x[0]['block'] == 'SEPDEC']
    ov = []
    for i, x in enumerate(main):
        for y in main[i + 1:]:
            ov.append('%s events touching %s %s, %s touching %s %s' % (x[0]['alarm'], y[0]['alarm'], fmt(overlap(x[1], y[1]), 3),
                                                                       y[0]['alarm'], x[0]['alarm'], fmt(overlap(y[1], x[1]), 3)))
    q1 = [x for x in main if x[2][0][5] != 'UNKNOWN']
    sides = sorted(set('longs' if x[1]['side'] < 0 else 'shorts' for x in main))
    pushes = sorted(set('falling' if x[1]['side'] < 0 else 'rising' for x in main))
    shares = ', '.join('%s %s' % (x[0]['alarm'], x[2][0][2].split(';')[0].split()[-1]) for x in q1)
    unk = {}
    for x in cards:
        for r in x[2]:
            if r[5] == 'UNKNOWN':
                unk.setdefault(r[0] if r[0] == 'GRADE' else 'Q%d' % r[0], []).append(x[0]['alarm'] + ('' if x[0]['block'] == 'SEPDEC' else ' ' + x[0]['block']))
    who = {'GRADE': 'STRATEGY (kit GRADE; ASK in GRADES_FORCED_FAMILY)', 'Q6': 'LAYERS (absorber reading X1.FLOWX / X1.HLFLOWX, producer-design; ASK SCOUT-2)', 'Q1': 'SCOUT (readings_builder)', 'Q3': 'SCOUT (readings_builder)',
           'Q4': 'SCOUT (readings_builder)', 'Q5': 'SCOUT (readings_builder)', 'Q7': 'STRATEGY (store)', 'Q8': 'STRATEGY (store)', 'Q2': 'SCOUT'}
    gr = [(x[0]['alarm'], num(grades[x[0]['grade_key']]['t_1h'])) for x in main if x[0].get('grade_key', '-') in grades
          and np.isfinite(num(grades[x[0]['grade_key']]['t_1h']))]
    q8 = [(x[0]['alarm'], x[2][7]) for x in main]
    partb = []
    allov = [overlap(x[1], y[1]) for x in main for y in main if x is not y]
    one = bool(allov) and min(allov) >= 0.9
    inside = []
    for x in main:
        for y in main:
            if x is not y and overlap(x[1], y[1]) >= 0.9 and overlap(y[1], x[1]) < 0.9:
                inside.append('%s sits inside %s' % (x[0]['alarm'], y[0]['alarm']))
    partb.append('1. Overlap by event (spans within 30 min, any coin): ' + ('; '.join(ov) if ov else 'one alarm only') +
                 ('; every pair at 0.9 or more: one stream of events, they enter stage 2 together as ONE mechanism' if one else
                  ('; nested, not one stream: %s' % ', '.join(inside) if inside else ('; not one stream' if ov else ''))))
    partb.append('2. Cause: %s forced out of %s coins, the liquidations on that side lead in the 15 min before the fire (forced-side share %s).'
                 % ('/'.join(sides), '/'.join(pushes), shares or 'UNKNOWN'))
    nojm = [x[0]['alarm'] for x in main if not any(y[0]['alarm'] == x[0]['alarm'] and y[0]['block'] == 'JANMAR' for y in cards)]
    if nojm:
        unk.setdefault('Jan-Mar 2026 card', []).extend(nojm); who['Jan-Mar 2026 card'] = 'STRATEGY (no Jan-Mar results store for these alarms)'
    partb.append('3. UNKNOWN: ' + ('; '.join('%s on %s, owner %s' % (q, ', '.join(v), who.get(q, '?')) for q, v in sorted(unk.items())) or 'none'))
    if gr:
        partb.append('4. By grading t at 1 h: strongest %s (t %s), weakest %s (t %s)%s.' % (max(gr, key=lambda x: x[1])[0], fmt(max(gr, key=lambda x: x[1])[1], 2, True),
                     min(gr, key=lambda x: x[1])[0], fmt(min(gr, key=lambda x: x[1])[1], 2, True),
                     '' if len(gr) == len(main) else '; not graded: ' + ', '.join(x[0]['alarm'] for x in main if x[0]['alarm'] not in [g[0] for g in gr])))
    else:
        partb.append('4. Strongest and weakest: UNKNOWN (no GRADES_FORCED_FAMILY rows)')
    # ---- write
    def clean(s):
        return str(s).replace('\t', ' ').replace('\n', ' ')
    tsv = ['\t'.join(TSV_COLS)]
    md = ['# ALARM_CARDS_%s' % a.mechanism, '',
          '- edition: %s; tool sha16 %s; config %s %s' % (EDITION, sha16_file(os.path.realpath(__file__)), os.path.basename(a.config), sha16_file(a.config)),
          '- words: SOLID = measured, 30+ events, beats matched moments (|z| >= z_crit, Bonferroni at 0.01 over the card\'s tests) and the same sign in every month; '
          'WEAK = measured, thin or mixed; UNKNOWN = no data, the missing input named. Knowledge only: no rule, no money test, no trade side.',
          '- events = waves of the grade rule (30 min gap, 4 h span, any coin); readings as of the fire second only (known_at <= t); '
          'money only after the fire (Q7, Q8, the after-the-fire line). Window Sep 2025 to Mar 2026.', '', '## Part A: cards', '']
    for c, A, rows, after, grading, ex in cards:
        name = c['alarm'] + ('' if c['block'] == 'SEPDEC' else '_' + c['block'])
        md.append('### %s (definition %s %s; months %s..%s; block %s): %d fires, %d events%s' % (c['alarm'], os.path.basename(c.get('def', '-')), A.get('def_sha16', '-'),
                                                                     A['first'], A['last'], c['block'], ex['fires'], ex['events'],
                                                                     '; missing: ' + ', '.join(A['missing']) if A['missing'] else ''))
        md.append('')
        md.append('| Q | question | answer | number | source sha16 | strength |')
        md.append('|---|---|---|---|---|---|')
        for q, ans, nb, src, sh, st in rows:
            qq = q if q == 'GRADE' else 'Q%d' % q
            md.append('| %s | %s | %s | %s | %s %s | %s |' % (qq, QNAME[q], clean(ans), clean(nb), src, sh, st))
            tsv.append('\t'.join(clean(v) for v in (name, qq, ans, nb, src, sh, st)))
        md.append('')
        md.append('- after the fire (description): %s (%s)' % after)
        if ex['q3']:
            md.append('')
            md.append('| Q3 class | fire share | matched share | fire minus matched (z) |')
            md.append('|---|---|---|---|')
            for r in ex['q3']['rows']:
                md.append('| %s | %s | %s | %s (z %s) |' % (r['cls'], fmt(r['fire_share'], 3), fmt(r['match_share'], 3), fmt(r['res']['score'], 3, True),
                                                              fmt(r['res']['z'], 2, True)))
        md.append('- sources: ' + '; '.join('%s %s %s' % (k, v[0], v[1]) for k, v in sorted(A['srcs'].items())) + '; readings known after the fire, not used: %d' % A['after_n'])
        md.append('')
    md += ['## Part B: conclusions (4 lines, knowledge only)', ''] + partb + ['', 'Wall time %.1f s.' % (time.time() - t0)]
    text_md = '\n'.join(md) + '\n'; text_tsv = '\n'.join(tsv) + '\n'
    hit = side_hits(text_md + '\n' + text_tsv)
    if hit:
        bad = [l for l in (text_md.splitlines() + tsv[1:]) if side_hits(l)]
        with open(pm + '.REFUSED_SIDE_WORD', 'w') as f:                       # a receipt of the refusal, never the card
            f.write('\n'.join(bad) + '\n')
        for l in bad[:5]:
            print('SIDE_WORD at: ...%s...' % l[:300])
        raise Refused('SIDE_WORD', 'the written text names a trade side: %s' % ', '.join(hit))
    open(pt, 'x').write(text_tsv); open(pm, 'x').write(text_md)
    print('WROTE %s %s' % (pt, sha16_file(pt))); print('WROTE %s %s' % (pm, sha16_file(pm))); print('WALL %.1f s' % (time.time() - t0))
    return pt, pm


def main(argv=None):
    ap = argparse.ArgumentParser(prog='alarm_cards_v1.py')
    ap.add_argument('out'); ap.add_argument('--mechanism', required=True); ap.add_argument('--config', required=True)
    ap.add_argument('--grades', default='')
    a = ap.parse_args(argv)
    if not re.fullmatch(r'[A-Z0-9_]+', a.mechanism):
        print('REFUSED BAD_ARGS mechanism'); return 2
    try:
        run(a); return 0
    except Refused as e:
        print('REFUSED', e.code, e.detail); return 2
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAILED', repr(e)); return 3


if __name__ == '__main__':
    sys.exit(main())
