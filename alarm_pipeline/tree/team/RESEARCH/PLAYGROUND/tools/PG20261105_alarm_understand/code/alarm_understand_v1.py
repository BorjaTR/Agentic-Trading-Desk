#!/usr/bin/env python3
"""alarm_understand_v1.py (SCO-A9 for SCOUT, 5 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED: never a PASS.
Built to SPEC_ALARM_UNDERSTANDING_V1.md 62d2aa9a779274f5 (team/RESEARCH/LEAD/ALARM_UNDERSTANDING_TOOL_20261105/). A READER: for one alarm
and one month block it joins what released tools already wrote into one ALARM_CARD.md: the 8 questions, each with a one-line answer,
numbers, evidence (path + sha16) and one word of STRONG / WEAK / OPINION / NOT_ANSWERED. No new metric, grade or alarm rule.
REUSED, NEVER REWRITTEN (imported read-only after their sha16 pins are checked; a changed file: REFUSED SOURCE_CHANGED):
  waves             i2g_rules_v1_2.build_clusters (the grade's rule: 30 min gap, 4 h span, any coin; weight 1/size)
  statistics        i2g_rules_v1_2.clustered_mean (wave-clustered weighted mean and 95% interval)
  wave count, top-k grouper_v1_10.size and top_waves (group_and_grade's own wave count and "waves that add most")
  code status       metric_brief_v2.flag on METRIC_TRAPS_V3 (PROVEN, or STOP refused, or capped at WEAK)
  closed days       lab3/law.py research_refusal (June 2026 onward BLIND) and the strategy card (August 2026 onward closed)
NEW here (the spec's list): the joiner, T_IMPACT, T_CONC, T_SINGLE, T_WHERE and the card writer (plus T_WHEN, T_FIRES, T_WAVES,
T_FORCED, T_SOURCES, plain tables of the joined rows).
INPUTS (the JOIN bundle, a folder; see README.md for every column): FIRES.tsv (required), READINGS.tsv, FORCED.tsv, MONEY.tsv; optional
--true-row (true_gate TRUE_ROW.tsv, column verdict), --fl-row (first look FL_RULE9_ROW.tsv, column RULE_9), --family-tags
(FAMILY_TAGS_V1.tsv). The bundle builder that writes them from the released run outputs is NOT in V1 (README: why).
RULES, FIXED BEFORE ANY RUN:
  AFTER      a reading, a liquidation row or a money value known after the moment it describes (known_at > t; money always) is tagged
             AFTER and never feeds Q1 to Q5; AFTER readings are listed under Q6.
  WAVES      built once on the alarm's whole open fire list (fires on closed days are dropped first), then the block's fires kept.
  WHERE      a fire's percentile = its value's place among the matched moments' values of the same month (ties count half).
  WORD       STRONG = every code PROVEN, 30+ waves, the same sign in 3 of 4 months (a block of fewer than 4 months cannot be STRONG),
             and beats matched moments: |z| >= z_crit, z of the mean of (percentile - 50) with a two-sample error: the fire side
             wave-clustered (clustered_mean) plus the matched pool's own sampling error, month by month (U7 kill rule fix, 5 Nov) (Q2-Q5); of the edge vs
             tough moments (Q6), of lone minus wave net (Q8); z_crit = Bonferroni at family-wise ALPHA 0.01 over k tests, k = the
             card's as-of Q2-Q5 readings + 2 (money tests always counted, so no after-fire value moves a Q1-Q5 word).
             WEAK = measured, fails one; OPINION = hand tag or prose only; NOT_ANSWERED = names the missing input.
             Q1 is STRONG only with first look RULE_9 SIZE, SIDE or SIZE+SIDE and true_gate TRUE and every DEF code PROVEN.
             Q7 is never STRONG in V1: no matched-moment comparison of concentration exists.
  IMPACT     retained_h = 1 - FADE gross at h / move in (EPI.<subject>.run_pct, as of the fire); move 0: empty, ZERO_MOVE.
             retained_1h < 0.5: the price comes back (liquidity); >= 0.5: it stays (information). AFTER: shown in Q6.
  FORCED     per fire the larger of long and short liquidations (as of the fire) is the forced side; a down push (side -1) expects
             longs. The card names a side only when it holds 2 of 3 fires (weighted), else mixed; Q4 and Q5 are STRONG only with a side.
  CONC       events = waves; a wave's net = the sum of weight x net of its fires; carried by one event when the net is > 0 and the
             net without the top wave <= 0; by the top 5 when the net without them <= 0.
  SINGLE     wave size 1 / 2-5 / 6+ x breadth (coins in the wave: 1coin / multi) x month; Q8 compares lone fires with waves of 2+.
Commands (a runner job, never by hand on real data):
  python3 -B alarm_understand_v1.py check --alarm <id> --def <DEF json> --def-sha16 <s> --block <YYYYMM|SEPDEC|JANAPR|MAYJUL>
  python3 -B alarm_understand_v1.py card <new out dir> --alarm <id> --def <DEF json> --def-sha16 <s> --block <B> --bundle <dir>
         [--true-row TRUE_ROW.tsv] [--fl-row FL_RULE9_ROW.tsv] [--family-tags FAMILY_TAGS_V1.tsv] [--card-closed-from YYYYMMDD]
  python3 -B alarm_understand_v1.py bundle <new out dir> --from-job <GRADE job id> --runner <runner root> --alarm <id> --block <B> [...]
         (SCO-A136 6 Nov 2026: the JOIN bundle builder, bundle_builder_v1.py beside this file; its docstring has every option and rule)
  check reads no data (the block, the pins, the DEF and its codes' status). Exit 0 done, 2 REFUSED <CODE>, 3 FAILED.
  Refusals: BLOCK_CLOSED (nothing read), SOURCE_CHANGED, STOP_CODE, BAD_BLOCK, BAD_ARGS, BAD_INPUT, OUT_EXISTS, NO_RELEASE."""
import sys
sys.dont_write_bytecode = True        # importing the release code must never write __pycache__ beside it
import argparse, csv, datetime as dt, hashlib, importlib, json, math, os, re, statistics
import numpy as np

EDITION = 'alarm_understand V1 (playground PG20261105_alarm_understand, SCO-A9 5 Nov 2026, TEST, NOT REVIEWED: never a PASS)'
SPEC = 'team/RESEARCH/LEAD/ALARM_UNDERSTANDING_TOOL_20261105/SPEC_ALARM_UNDERSTANDING_V1.md 62d2aa9a779274f5'
WORDS = ('STRONG', 'WEAK', 'OPINION', 'NOT_ANSWERED')
QUESTIONS = ((1, 'what type'), (2, 'when'), (3, 'why'), (4, 'who is forced'), (5, 'who is paying'), (6, 'money from whom'),
             (7, 'carried by events'), (8, 'single events'))
MIN_WAVES = 30
MONTHS_NEED, MONTHS_SAME = 4, 3
ALPHA = 0.01
RETAINED_CUT = 0.5
FORCED_SHARE = 2.0 / 3.0      # a side is named forced only when it holds 2 of 3 fires (weighted); else mixed
HORIZONS = ('15m', '1h', '4h')
CARD_CLOSED_FROM = 20260801
CARD_CLOSED_WHY = 'the strategy card: August onward is closed (team/RESEARCH/STRATEGIES/FDAOI/CARD.md b8bd7b5b1c9acb72 line 10)'
BLOCKS = {'SEPDEC': (20250910, 20251231), 'JANAPR': (20260101, 20260430), 'MAYJUL': (20260501, 20260731)}
RULE9_MEASURED = ('SIZE', 'SIDE', 'SIZE+SIDE')
# the spec's codes column (section "The 8 questions"), by column name; raw lab codes by their full code
QMAP = {}
for _q, _names in ((2, 'hour_utc weekday fires_other_60m alarms_all_24h btc_vol_regime market_hot_rank_30d'),
                   (3, 'run_pct pre_move_pct forced_share hl_lead_s btc_move_15m coin_vs_basket_15m coin_with_market_15m'),
                   (4, 'forced_usd_log size_vs_bar burst_vs_oi_bp other_share hl_forced_usd_log oi_chg_burst_pct liq_oi_forced_bp_60s '
                       'oi_moved_since_wave coins_liquidating_z'),
                   (5, 'fills_one_sided volume_one_sided whale_net_5m_usd funding_forced_pays_bp hl_net_whale_push_usd_60s'),
                   (8, 'coins_liquidating_1m')):
    for _n in _names.split():
        QMAP[_n] = _q
QMAP_FULL = {'A1.S08': 4, 'E2.S06': 4}
SG = 'Strategy/group_and_grade_tool/current/tree/team/RESEARCH/tools'
AL = 'Alarm/alarm/current'
PINS = ((SG + '/idea_to_grade/i2g_rules_v1_2.py', '2fd143d066355df8'),
        (SG + '/idea_to_grade/alarm_contract_v1.py', '65c37dbff4cb3ef4'),
        (SG + '/group_and_grade/grouper_v1_10.py', 'e3df62cb4fd5438c'),
        (AL + '/01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief_v2.py', '0ca9f04bd2181f04'),
        (AL + '/_tools/settings_v1.py', '6b25623d1943524e'),
        (AL + '/_vendor/LAB3_code/lab3/__init__.py', 'e3b0c44298fc1c14'),
        (AL + '/_vendor/LAB3_code/lab3/law.py', 'c54e24bdd9b0debe'),
        (AL + '/01_Detection/tree/team/LAB3/METRICS_V1.tsv', 'c2335f86987c5045'),
        (AL + '/01_Detection/tree/team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv', 'f71f02f3a8af3e76'),
        (AL + '/01_Detection/tree/team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'f413906feb40c0b4'),
        (AL + '/01_Detection/tree/team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv', 'd133fea9c7935857'))
_REL = None


class Refused(Exception):
    def __init__(self, code, detail=''):
        super().__init__('%s: %s' % (code, detail)); self.code = code; self.detail = detail


class NS:
    def __init__(self, **k):
        self.__dict__.update(k)


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


# ---------------------------------------------------------------------------------------------------- release code, pinned
def release_root():
    """AU_RELEASE, else <RELEASE_ROOT> (the Mac), else ~/mnt/volat_release (a Cowork VM)"""
    env = os.environ.get('AU_RELEASE')
    cands = [env] if env else [os.path.expanduser('<RELEASE_ROOT>'), os.path.expanduser('~/mnt/volat_release')]
    for c in cands:
        if c and os.path.isdir(os.path.join(c, 'Alarm')) and os.path.isdir(os.path.join(c, 'Strategy')):
            return os.path.realpath(c)
    raise Refused('NO_RELEASE', 'no release folder at %s' % ' or '.join(c for c in cands if c))


def verify_pins(root, pins=PINS):
    """every pinned file's sha16 -> [(rel, sha16)]; one missing or changed: REFUSED SOURCE_CHANGED"""
    bad, got = [], []
    for relp, want in pins:
        p = os.path.join(root, relp)
        if not os.path.isfile(p):
            bad.append('%s missing' % relp)
            continue
        s = sha16_file(p)
        got.append((relp, s))
        if s != want:
            bad.append('%s is %s, pinned %s' % (relp, s, want))
    if bad:
        raise Refused('SOURCE_CHANGED', '; '.join(bad))
    return got


def _import(name, folder, relfile):
    sys.path.insert(0, folder)
    try:
        mod = importlib.import_module(name)
    finally:
        if folder in sys.path:
            sys.path.remove(folder)
    if os.path.realpath(mod.__file__) != os.path.realpath(os.path.join(folder, relfile)):
        raise Refused('SOURCE_CHANGED', '%s was imported from %s, not the pinned %s' % (name, mod.__file__, os.path.join(folder, relfile)))
    return mod


def release(pins=PINS):
    """the pins checked, then the reused release modules imported read-only (cached once a process)"""
    global _REL
    if _REL is not None and pins is PINS:
        return _REL
    root = release_root()
    got = verify_pins(root, pins)
    j = lambda *p: os.path.join(root, *p)
    RU = _import('i2g_rules_v1_2', j(SG, 'idea_to_grade'), 'i2g_rules_v1_2.py')
    GG = _import('grouper_v1_10', j(SG, 'group_and_grade'), 'grouper_v1_10.py')
    MB = _import('metric_brief_v2', j(AL, '01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts'), 'metric_brief_v2.py')
    LAW = _import('lab3.law', j(AL, '_vendor/LAB3_code'), 'lab3/law.py')
    R = NS(root=root, pins=got, RU=RU, GG=GG, MB=MB, LAW=LAW)
    if pins is PINS:
        _REL = R
    return R


def release_tables(R):
    """(traps {code: row}, cards {code: row}) from metric_brief_v2's own four tables, found by its own functions"""
    S = R.MB.settings_module(R.MB.__file__)
    M, T, C = R.MB.tables(R.MB.detection_tree(R.MB.__file__, S))
    cards = {r['code']: r for r in R.MB.rows(M)}
    for p in C:
        for r in R.MB.rows(p):
            cards.setdefault(r['code'], r)
    return {r['code']: r for r in R.MB.rows(T)}, cards


def code_status(codes, traps, R=None):
    """{code: PROVEN | UNPROVEN} by metric_brief_v2.flag; a STOP code: REFUSED STOP_CODE (never read into a card)"""
    R = R or release()
    out, stop = {}, []
    for c in codes:
        tr = traps.get(c)
        if not tr:
            out[c] = 'UNPROVEN'
            continue
        f = R.MB.flag(tr.get('status'))
        if f.startswith('STOP'):
            stop.append('%s (%s)' % (c, tr.get('status')))
        out[c] = 'PROVEN' if f == '' else 'UNPROVEN'
    if stop:
        raise Refused('STOP_CODE', '; '.join(stop))
    return out


# ---------------------------------------------------------------------------------------------------- days and blocks
def utc(t):
    return dt.datetime.fromtimestamp(int(t), dt.timezone.utc)


def day_of(t):
    return int(utc(t).strftime('%Y%m%d'))


def month_of(t):
    return utc(t).strftime('%Y%m')


def block_span(block):
    """-> (first day, last day, [months YYYYMM])"""
    b = str(block)
    if b in BLOCKS:
        first, last = BLOCKS[b]
    elif re.fullmatch(r'20\d\d(0[1-9]|1[0-2])', b):
        y, m = int(b[:4]), int(b[4:])
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)
        first, last = y * 10000 + m * 100 + 1, int(nxt.strftime('%Y%m%d'))
    else:
        raise Refused('BAD_BLOCK', '%r: YYYYMM, SEPDEC, JANAPR or MAYJUL' % b)
    months, d = [], dt.datetime.strptime(str(first), '%Y%m%d').date()
    while int(d.strftime('%Y%m%d')) <= last:
        if d.strftime('%Y%m') not in months:
            months.append(d.strftime('%Y%m'))
        d += dt.timedelta(days=1)
    return first, last, months


def closed_reason(day, law_refusal, closed_from=CARD_CLOSED_FROM):
    why = law_refusal(int(day))
    if why:
        return 'lab3 law.py: %s' % why
    if int(day) >= closed_from:
        return CARD_CLOSED_WHY if closed_from == CARD_CLOSED_FROM else 'closed from %d (--card-closed-from)' % closed_from
    return None


def check_block(block, law_refusal, closed_from=CARD_CLOSED_FROM):
    """a block touching a closed day: REFUSED BLOCK_CLOSED, before any input is read"""
    first, last, months = block_span(block)
    d = dt.datetime.strptime(str(first), '%Y%m%d').date()
    while int(d.strftime('%Y%m%d')) <= last:
        why = closed_reason(int(d.strftime('%Y%m%d')), law_refusal, closed_from)
        if why:
            raise Refused('BLOCK_CLOSED', '%s touches %s: %s' % (block, d.strftime('%Y%m%d'), why))
        d += dt.timedelta(days=1)
    return first, last, months


# ---------------------------------------------------------------------------------------------------- context
def def_codes(defn):
    out = set()
    for v in (defn.get('inputs') or {}).values():
        if isinstance(v, dict) and v.get('code'):
            out.add(str(v['code']))
    return sorted(out)


def make_context(R, alarm, block, defn, traps=None, cards=None, closed_from=CARD_CLOSED_FROM, def_path='', def_sha16=''):
    first, last, months = check_block(block, R.LAW.research_refusal, closed_from)
    planted = traps is not None
    if traps is None or cards is None:
        t2, c2 = release_tables(R)
        traps = t2 if traps is None else traps
        cards = c2 if cards is None else cards
    status = code_status(def_codes(defn), traps, R)
    return NS(R=R, alarm=str(alarm), block=str(block), first=first, last=last, months=months, defn=defn, traps=traps,
              cards=cards, status=status, planted=planted, closed_from=closed_from, def_path=def_path, def_sha16=def_sha16,
              closed=lambda day: closed_reason(day, R.LAW.research_refusal, closed_from))


def parent_key(f):
    return release().RU.parent_id(f[1], int(f[2]), int(f[3]))


# ---------------------------------------------------------------------------------------------------- small statistics
def num(x):
    if x is None:
        return float('nan')
    if isinstance(x, (int, float, np.floating, np.integer)):
        return float(x)
    s = str(x).strip()
    if s in ('', 'nan', 'NaN', 'NA', 'None'):
        return float('nan')
    return float(s)


def wmedian(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not ok.any():
        return float('nan')
    o = np.argsort(x[ok], kind='stable'); xs, ws = x[ok][o], w[ok][o]
    c = np.cumsum(ws)
    return float(xs[int(np.searchsorted(c, 0.5 * c[-1]))])


def cmean(R, x, w, cl):
    r = R.RU.clustered_mean(np.asarray(x, float), np.asarray(w, float), np.asarray(cl, dtype=object))
    se = r['se']
    r['z'] = r['mean'] / se if (np.isfinite(se) and se > 0 and np.isfinite(r['mean'])) else float('nan')
    return r


def z_crit(k):
    return statistics.NormalDist().inv_cdf(1.0 - ALPHA / (2.0 * k)) if k > 0 else float('inf')


def same_months(overall, per_month, n_months):
    """(months with the overall's sign, months_ok)"""
    if not np.isfinite(overall) or overall == 0:
        return 0, False
    s = sum(1 for v in per_month if np.isfinite(v) and v != 0 and np.sign(v) == np.sign(overall))
    return s, n_months >= MONTHS_NEED and s >= MONTHS_SAME


def f2(x, d=2, sign=True):
    if x is None or not np.isfinite(x):
        return 'nan'
    return ('%+.*f' if sign else '%.*f') % (d, x)


def qmap(code):
    if code in QMAP_FULL:
        return QMAP_FULL[code]
    return QMAP.get(code.split('.')[-1], 0)


# ---------------------------------------------------------------------------------------------------- the joiner
def build_card(B, ctx):
    """B: dict(fires [(alarm, coin, t, side)], readings [dict], forced [dict], money [dict], labels {}) -> dict(rows, tables, meta)"""
    R = ctx.R
    fires_all = []
    for f in B.get('fires') or []:
        a, c, t, s = str(f[0]), str(f[1]), int(f[2]), int(f[3])
        if a != ctx.alarm:
            raise Refused('BAD_INPUT', 'a fire of alarm %s in the list of %s' % (a, ctx.alarm))
        fires_all.append((a, c, t, s))
    open_f = [f for f in fires_all if ctx.closed(day_of(f[2])) is None]
    U = R.RU.build_clusters(open_f) if open_f else []
    wcoins, wtimes = {}, {}
    for r in U:
        wcoins.setdefault(r[5], set()).add(r[1]); wtimes.setdefault(r[5], []).append(r[2])
    worder = {cid: i for i, cid in enumerate(sorted(wtimes, key=lambda c: (min(wtimes[c]), c)))}
    F = []
    for (a, c, t, s, pid, cid, w, size, flag) in U:
        d = day_of(t)
        if ctx.first <= d <= ctx.last:
            F.append(dict(pid=pid, coin=c, t=t, side=s, wave=cid, wi=worder[cid], w=float(w), size=int(size), flag=flag,
                          month=str(d)[:6], breadth=len(wcoins[cid])))
    F.sort(key=lambda x: (x['t'], x['coin'], x['side']))
    n = len(F)
    W = np.array([x['w'] for x in F], float); CL = np.array([x['wave'] for x in F], dtype=object)
    WI = np.array([x['wi'] for x in F], dtype=np.int64); MO = np.array([x['month'] for x in F], dtype=object)
    SIZE = np.array([x['size'] for x in F], dtype=np.int64); BR = np.array([x['breadth'] for x in F], dtype=np.int64)
    fkeys = {(x['coin'], x['t']) for x in F}
    meta = dict(fires_listed=len(fires_all), fires_closed_dropped=len(fires_all) - len(open_f), fires_block=n,
                waves_block=len(set(CL.tolist())))
    tables = {}
    # ---- T_FIRES, T_WAVES, T_WHEN
    tables['T_FIRES'] = (['parent_id', 'coin', 't', 'utc', 'side', 'wave', 'wave_size', 'weight', 'flag', 'month'],
                         [[x['pid'], x['coin'], x['t'], utc(x['t']).strftime('%Y-%m-%dT%H:%M:%SZ'), x['side'], x['wave'], x['size'],
                           x['w'], x['flag'], x['month']] for x in F])
    inblock = {}
    for x in F:
        inblock[x['wave']] = inblock.get(x['wave'], 0) + 1
    wflag = {r[5]: r[8] for r in U}
    tables['T_WAVES'] = (['wave', 'first_t', 'first_utc', 'size', 'coins', 'span_s', 'flag', 'fires_in_block'],
                         [[cid, min(wtimes[cid]), utc(min(wtimes[cid])).strftime('%Y-%m-%dT%H:%M:%SZ'), len(wtimes[cid]),
                           len(wcoins[cid]), max(wtimes[cid]) - min(wtimes[cid]), wflag[cid], inblock[cid]]
                          for cid in sorted(inblock, key=lambda c: worder[c])])
    when = []
    for kind, keyf in (('month', lambda t: month_of(t)), ('week', lambda t: '%d-W%02d' % utc(t).isocalendar()[:2]),
                       ('hour', lambda t: '%02d' % utc(t).hour), ('weekday', lambda t: utc(t).strftime('%a'))):
        g = {}
        for x in F:
            g.setdefault(keyf(x['t']), []).append(x['wave'])
        for k in sorted(g):
            when.append([kind, k, len(g[k]), len(set(g[k]))])
    tables['T_WHEN'] = (['kind', 'key', 'fires', 'waves'], when)
    # ---- readings: as of the fire, or AFTER (known_at > t), by code
    asof_f, after_f, asof_m, after_m = {}, {}, {}, {}
    skipped = dict(outside_block=0, fire_not_listed=0)
    for r in B.get('readings') or []:
        who, c, t, k, code, v = str(r['who']), str(r['coin']), int(r['t']), int(r['known_at']), str(r['code']), num(r['value'])
        if who not in ('FIRE', 'MATCH'):
            raise Refused('BAD_INPUT', 'READINGS who %r: FIRE or MATCH' % who)
        if not ctx.first <= day_of(t) <= ctx.last:
            skipped['outside_block'] += 1
            continue
        if who == 'FIRE' and (c, t) not in fkeys:
            skipped['fire_not_listed'] += 1
            continue
        after = k > t
        key = '%s@+%dm' % (code, int(round((k - t) / 60.0))) if after else code
        tgt = (after_f if after else asof_f) if who == 'FIRE' else (after_m if after else asof_m)
        cur = tgt.setdefault(key, {}).get((c, t))
        if cur is None or k >= cur[0]:
            tgt[key][(c, t)] = (k, v)
    meta['readings_skipped'] = skipped
    base_codes = sorted({k.split('@')[0] for d_ in (asof_f, after_f, asof_m, after_m) for k in d_})
    st = code_status(base_codes, ctx.traps, R)
    status = dict(ctx.status); status.update(st)
    # ---- T_WHERE
    wrows, wstat = [], {}
    for key in sorted(set(asof_f) | set(asof_m) | set(after_f) | set(after_m)):
        tag = 'AFTER' if '@' in key else 'ASOF'
        base = key.split('@')[0]
        fd = (after_f if tag == 'AFTER' else asof_f).get(key, {})
        md = (after_m if tag == 'AFTER' else asof_m).get(key, {})
        q = 6 if tag == 'AFTER' else qmap(base)
        fv = np.array([fd.get((x['coin'], x['t']), (0, np.nan))[1] for x in F], float)
        pools = {}
        for (c, t), (k, v) in md.items():
            if np.isfinite(v):
                pools.setdefault(month_of(t), []).append(v)
        pools = {m: np.sort(np.array(v, float)) for m, v in pools.items()}
        pct = np.full(n, np.nan)
        mvar = {}                       # month -> (fire weight, variance of the mean from the matched side)
        for m, arr in pools.items():
            ix = np.flatnonzero((MO == m) & np.isfinite(fv))
            if len(ix):
                lo = np.searchsorted(arr, fv[ix], 'left'); hi = np.searchsorted(arr, fv[ix], 'right')
                pct[ix] = 100.0 * (lo + 0.5 * (hi - lo)) / len(arr)
                # the matched pool is a sample too: each matched value's place among the month's fires (weighted, ties half);
                # its variance / pool size is the matched side's part of the error (two-sample, DeLong-style)
                o = np.argsort(fv[ix], kind='stable'); xs, ws = fv[ix][o], W[ix][o]
                cw = np.concatenate([[0.0], np.cumsum(ws)])
                a_ = np.searchsorted(xs, arr, 'left'); b_ = np.searchsorted(xs, arr, 'right')
                qm = 100.0 * (cw[a_] + 0.5 * (cw[b_] - cw[a_])) / cw[-1]
                mvar[m] = (float(ws.sum()), float(np.var(qm, ddof=1)) / len(arr) if len(arr) > 1 else float('nan'))
        per = {}
        for sl in ['ALL'] + ctx.months:
            mk = np.isfinite(pct) & ((MO == sl) if sl != 'ALL' else True)
            mp = [pools[m] for m in (ctx.months if sl == 'ALL' else [sl]) if m in pools]
            mp = np.concatenate(mp) if mp else np.array([])
            cm = cmean(R, pct[mk] - 50.0, W[mk], CL[mk]) if mk.any() else dict(mean=np.nan, se=np.nan, z=np.nan, clusters=0)
            ms = [mvar[m] for m in (ctx.months if sl == 'ALL' else [sl]) if m in mvar]
            wt = sum(v[0] for v in ms)
            vm = sum((v[0] / wt) ** 2 * v[1] for v in ms) if wt > 0 else float('nan')
            se2 = math.sqrt(cm['se'] ** 2 + vm) if (np.isfinite(cm['se']) and np.isfinite(vm)) else float('nan')
            cm['z'] = cm['mean'] / se2 if (np.isfinite(se2) and se2 > 0 and np.isfinite(cm['mean'])) else float('nan')
            per[sl] = cm
            wrows.append(dict(reading=key, q=q, tag=tag, slice=sl, status=status.get(base, 'UNPROVEN'), fires=int(mk.sum()),
                              waves=len(set(CL[mk].tolist())), fire_median=wmedian(fv[mk], W[mk]), matched_n=int(len(mp)),
                              matched_median=float(np.median(mp)) if len(mp) else float('nan'), fire_pct=wmedian(pct[mk], W[mk]),
                              pct_mean=cm['mean'] + 50.0, z=cm['z'], word=''))
        same, mok = same_months(per['ALL']['mean'], [per[m]['mean'] for m in ctx.months], len(ctx.months))
        wstat[key] = dict(tag=tag, q=q, base=base, all=[r for r in wrows if r['reading'] == key and r['slice'] == 'ALL'][0],
                          same=same, months_ok=mok, per=per)
    # the card's tests: its as-of Q2-Q5 readings + 2 (money tests, always counted: no after-fire value moves z_crit)
    tests = [k for k, s in wstat.items() if s['tag'] == 'ASOF' and 2 <= s['q'] <= 5 and np.isfinite(s['all']['z'])]
    k_tests = len(tests) + 2
    zc = z_crit(k_tests)
    meta.update(k_tests=k_tests, z_crit=zc)
    for key, s in wstat.items():
        a = s['all']
        if s['tag'] == 'ASOF' and 2 <= s['q'] <= 5 and a['fires'] > 0:
            strong = (a['status'] == 'PROVEN' and a['waves'] >= MIN_WAVES and s['months_ok'] and np.isfinite(a['z'])
                      and abs(a['z']) >= zc)
            a['word'] = 'STRONG' if strong else 'WEAK'
    tables['T_WHERE'] = (['reading', 'q', 'tag', 'slice', 'status', 'fires', 'waves', 'fire_median', 'matched_n', 'matched_median',
                          'fire_pct', 'pct_mean', 'z', 'word'],
                         [[r[c] for c in ('reading', 'q', 'tag', 'slice', 'status', 'fires', 'waves', 'fire_median', 'matched_n',
                                          'matched_median', 'fire_pct', 'pct_mean', 'z', 'word')] for r in wrows])

    def best(q):
        c = [s for s in wstat.values() if s['tag'] == 'ASOF' and s['q'] == q and s['all']['fires'] > 0]
        if not c:
            return None, []
        c.sort(key=lambda s: (-(abs(s['all']['z']) if np.isfinite(s['all']['z']) else -1), s['all']['reading']))
        return c[0], c

    # ---- T_FORCED (as of the fire only)
    fz, after_forced = {}, 0
    for r in B.get('forced') or []:
        c, t, k = str(r['coin']), int(r['t']), int(r['known_at'])
        if (c, t) not in fkeys:
            continue
        if k > t:
            after_forced += 1
            continue
        cur = fz.get((c, t))
        if cur is None or k >= cur[0]:
            fz[(c, t)] = (k, num(r['long_usd']), num(r['short_usd']))
    meta['forced_after_ignored'] = after_forced
    frows, FS = [], []
    for x in F:
        _, lg, sh = fz.get((x['coin'], x['t']), (0, np.nan, np.nan))
        if np.isfinite(lg) and np.isfinite(sh):
            side = 'longs' if lg > sh else 'shorts' if sh > lg else ('none' if lg == 0 else 'tie')
        else:
            side = ''
        exp = 'longs' if x['side'] < 0 else 'shorts'
        agree = '' if side == '' else ('yes' if side == exp else 'no')
        FS.append(side)
        frows.append([x['pid'], x['month'], x['side'], lg, sh, side, exp, agree, '', '', 1])
    FS = np.array(FS, dtype=object)
    fsum = {}
    for sl in ['ALL'] + ctx.months:
        mk = (FS != '') & ((MO == sl) if sl != 'ALL' else True)
        tw = W[mk].sum() if mk.any() else 0.0
        sl_ = W[mk & (FS == 'longs')].sum() / tw if tw > 0 else float('nan')
        ss_ = W[mk & (FS == 'shorts')].sum() / tw if tw > 0 else float('nan')
        side = '' if tw == 0 else 'longs' if sl_ >= FORCED_SHARE else 'shorts' if ss_ >= FORCED_SHARE else 'mixed'
        fsum[sl] = dict(side=side, longs=sl_, shorts=ss_, fires=int(mk.sum()), waves=len(set(CL[mk].tolist())))
        frows.append([sl, sl if sl != 'ALL' else '', '', '', '', side, '', '', sl_, ss_, int(mk.sum())])
    tables['T_FORCED'] = (['row', 'month', 'side', 'long_usd', 'short_usd', 'forced', 'expected', 'agree', 'share_longs',
                           'share_shorts', 'fires'], frows)
    # ---- money (AFTER by nature): T_IMPACT, T_CONC, T_SINGLE, Q6
    mo, exits = {}, set()
    for r in B.get('money') or []:
        pid = R.RU.parent_id(str(r['coin']), int(r['t']), int(r['side']))
        mo[pid] = r; exits.add(str(r.get('exit', '')))
    exit_name = ','.join(sorted(exits)) if exits else ''
    NET = np.array([num(mo[x['pid']]['net']) if x['pid'] in mo else np.nan for x in F], float)
    EDGE = np.array([num(mo[x['pid']].get('edge_tough')) if x['pid'] in mo else np.nan for x in F], float)
    BACK = {h: np.array([num(mo[x['pid']].get('fade_gross_' + h)) if x['pid'] in mo else np.nan for x in F], float) for h in HORIZONS}
    mkeys = sorted(k for k in asof_f if k.startswith('EPI.') and k.split('.')[-1] == 'run_pct')
    mcode = mkeys[0] if mkeys else ''
    MOVE = np.array([asof_f[mcode].get((x['coin'], x['t']), (0, np.nan))[1] if mcode else np.nan for x in F], float)
    irows = []
    for i, x in enumerate(F):
        mv = MOVE[i]
        flag = ('NO_MOVE' if not np.isfinite(mv) else 'ZERO_MOVE' if mv == 0 else 'NEG_MOVE' if mv < 0 else
                'NO_MONEY' if not np.isfinite(BACK['1h'][i]) else '')
        ret = [1.0 - BACK[h][i] / mv if (np.isfinite(mv) and mv > 0 and np.isfinite(BACK[h][i])) else float('nan') for h in HORIZONS]
        irows.append([x['pid'], x['month'], mv] + [BACK[h][i] for h in HORIZONS] + ret + [flag, 1])
    isum = {}
    for sl in ['ALL'] + ctx.months:
        base_m = np.isfinite(MOVE) & (MOVE > 0) & ((MO == sl) if sl != 'ALL' else True)
        ret = []
        for h in HORIZONS:
            mk = base_m & np.isfinite(BACK[h])
            ret.append(1.0 - (W[mk] * BACK[h][mk]).sum() / (W[mk] * MOVE[mk]).sum() if mk.any() else float('nan'))
        isum[sl] = dict(zip(HORIZONS, ret))
        zero = int((np.isfinite(MOVE) & (MOVE == 0) & ((MO == sl) if sl != 'ALL' else True)).sum())
        irows.append([sl, sl if sl != 'ALL' else '', float('nan'), float('nan'), float('nan'), float('nan')] + ret
                     + ['ZERO_MOVE %d' % zero if zero else '', int(base_m.sum())])
    tables['T_IMPACT'] = (['row', 'month', 'move_in', 'back_15m', 'back_1h', 'back_4h', 'retained_15m', 'retained_1h', 'retained_4h',
                           'flag', 'fires'], irows)
    ok = np.isfinite(NET)
    crows, csum = [], {}
    for sl in ['ALL'] + ctx.months:
        mk = ok & ((MO == sl) if sl != 'ALL' else True)
        if mk.any():
            x, w, c = NET[mk], W[mk], WI[mk]
            sums = {}
            for ci, v in zip(c.tolist(), (w * x).tolist()):
                sums[ci] = sums.get(ci, 0.0) + v
            total = float(sum(sums.values()))
            t1 = R.GG.top_waves(x, w, c, 1); t5 = R.GG.top_waves(x, w, c, 5)
            top1 = float(sum(sums[int(i)] for i in t1)); top5 = float(sum(sums[int(i)] for i in t5))
            ex1, ex5 = total - top1, total - top5
            sh1 = top1 / total if total > 0 else float('nan'); sh5 = top5 / total if total > 0 else float('nan')
            ans = ('no net to carry (net %s <= 0)' % f2(total) if total <= 0 else 'carried by one event' if ex1 <= 0 else
                   'carried by the top 5 events' if ex5 <= 0 else 'not carried by a few events')
            nw = len(sums)
        else:
            total = top1 = top5 = ex1 = ex5 = sh1 = sh5 = float('nan'); ans = 'no money'; nw = 0
        csum[sl] = dict(answer=ans, total=total, ex1=ex1, ex5=ex5, sh1=sh1, sh5=sh5, waves=nw)
        crows.append([sl, nw, total, top1, top5, sh1, sh5, ex1, ex5, ans])
    tables['T_CONC'] = (['slice', 'waves', 'net_sum', 'top1', 'top5', 'top1_share', 'top5_share', 'net_ex_top1', 'net_ex_top5',
                         'answer'], crows)
    SB = np.array(['1' if s == 1 else '2-5' if s <= 5 else '6+' for s in SIZE], dtype=object)
    BB = np.array(['1coin' if b == 1 else 'multi' for b in BR], dtype=object)
    srows = []
    for sb in ('1', '2-5', '6+'):
        for br in ('1coin', 'multi'):
            for sl in ['ALL'] + ctx.months:
                mk = ok & (SB == sb) & (BB == br) & ((MO == sl) if sl != 'ALL' else True)
                cm = cmean(R, NET[mk], W[mk], CL[mk]) if mk.any() else dict(mean=np.nan, lo=np.nan, hi=np.nan)
                srows.append([sb, br, sl, len(set(CL[mk].tolist())), int(mk.sum()), cm['mean'], cm['lo'], cm['hi']])
    tables['T_SINGLE'] = (['size_bucket', 'breadth', 'slice', 'waves', 'fires', 'net', 'lo', 'hi'], srows)
    # ---- the card rows
    labels = B.get('labels') or {}
    claim = ctx.defn.get('claim') or {}
    conds = '; '.join(str(c.get('name')) for c in (ctx.defn.get('conditions') or []) if c.get('name'))
    primary = ctx.defn.get('primary') or ''
    rows = []

    def add(q, answer, numbers, evidence, word):
        assert word in WORDS
        rows.append(dict(q=q, question=dict(QUESTIONS)[q], answer=' '.join(str(answer).split()), numbers=' '.join(str(numbers).split()),
                         evidence=list(evidence), word=word))

    def rtext(s):
        a = s['all']
        return '%s fire pct %.0f among matched (fire median %.4g vs matched %.4g)' % (a['reading'], a['fire_pct'], a['fire_median'],
                                                                                     a['matched_median'])

    def rnum(s):
        a = s['all']
        pm = ' '.join('%s:%s' % (m, f2(s['per'][m]['mean'] + 50.0, 0, False) if np.isfinite(s['per'][m]['mean']) else '%s:nan' % m)
                      for m in ctx.months)
        return ('%s: fires %d, waves %d, pct mean %s, z %s (z_crit %.2f), same sign %d of %d months, %s; pct by month %s'
                % (a['reading'], a['fires'], a['waves'], f2(a['pct_mean'], 1, False), f2(a['z'], 2), zc, s['same'], len(ctx.months),
                   a['status'], pm))

    def qword(cands, fallback):
        if any(s['all']['word'] == 'STRONG' for s in cands):
            return 'STRONG'
        return fallback

    # Q1
    t1, r9, tv, fam = claim.get('type'), labels.get('rule9'), labels.get('true_verdict'), labels.get('family_tag')
    parts = []
    if t1:
        parts.append('%s (DEF claim type): %s' % (t1, claim.get('one_line', '')))
    if fam:
        parts.append('family %s (SCOUT opinion)' % fam)
    if r9:
        parts.append('first look RULE_9 %s' % r9)
    if tv:
        parts.append('true_gate %s' % tv)
    allproven = all(ctx.status.get(c) == 'PROVEN' for c in def_codes(ctx.defn))
    if r9 or tv:
        w1 = 'STRONG' if (r9 in RULE9_MEASURED and tv == 'TRUE' and allproven) else 'WEAK'
    elif t1 or fam:
        w1 = 'OPINION'
    else:
        w1 = 'NOT_ANSWERED'
    a1 = '; '.join(parts) + '; liquidity vs information: measured after the fire, in Q6 (AFTER)' if parts else \
        'NOT_ANSWERED: no DEF claim type, no FAMILY_TAGS row, no FL_RULE9_ROW.tsv, no TRUE_ROW.tsv'
    add(1, a1, 'RULE_9 %s; true_gate %s; DEF codes %s' % (r9 or 'none', tv or 'none',
                                                          ', '.join('%s %s' % (c, ctx.status.get(c)) for c in def_codes(ctx.defn)) or 'none'),
        ['DEF', 'FL_ROW', 'TRUE_ROW', 'FAMILY_TAGS'], w1)
    # Q2
    b2, c2 = best(2)
    if n == 0:
        add(2, 'NOT_ANSWERED: no fires in the block (FIRES.tsv)', 'fires 0', ['FIRES'], 'NOT_ANSWERED')
    else:
        bym = {r[1]: (r[2], r[3]) for r in when if r[0] == 'month'}
        byh = sorted(((r[2], r[1]) for r in when if r[0] == 'hour'), key=lambda v: (-v[0], v[1]))
        top_m = sorted(bym.items(), key=lambda kv: (-kv[1][0], kv[0]))[0]
        a2 = 'most fires in %s (%d of %d); peak hour %s UTC (%d fires)' % (top_m[0], top_m[1][0], n, byh[0][1], byh[0][0])
        if b2:
            a2 += '; ' + rtext(b2)
        n2 = 'fires %d, waves %d; by month %s' % (n, meta['waves_block'], ' '.join('%s:%d/%d' % (m, bym.get(m, (0, 0))[0],
                                                                                              bym.get(m, (0, 0))[1]) for m in ctx.months))
        if b2:
            n2 += '; ' + rnum(b2)
        add(2, a2, n2, ['T_WHEN', 'T_WHERE', 'FIRES', 'READINGS'], qword(c2, 'WEAK'))
    # Q3
    b3, c3 = best(3)
    if b3:
        add(3, rtext(b3) + ('; DEF conditions: ' + conds if conds else ''), rnum(b3), ['T_WHERE', 'READINGS', 'DEF'], qword(c3, 'WEAK'))
    elif conds:
        add(3, 'DEF conditions (prose, not measured here): ' + conds, 'no Q3 reading measured', ['DEF'], 'OPINION')
    else:
        add(3, 'NOT_ANSWERED: no Q3 reading (READINGS.tsv EPI/CTX run_pct, btc_move_15m ...) and no DEF conditions', 'none', [],
            'NOT_ANSWERED')
    # Q4
    b4, c4 = best(4)
    fa = fsum['ALL']
    if fa['fires'] > 0:
        a4 = '%s forced: share longs %s, shorts %s of %d fires (liquidations only, AT LEAST: stops and ADL unseen)' % (
            fa['side'] if fa['side'] in ('longs', 'shorts') else 'no side (mixed, none in 2 of 3 fires)', f2(fa['longs'], 2, False),
            f2(fa['shorts'], 2, False), fa['fires'])
        if b4:
            a4 += '; ' + rtext(b4)
        n4 = 'forced by month %s' % ' '.join('%s:%s' % (m, fsum[m]['side'] or '-') for m in ctx.months)
        if b4:
            n4 += '; ' + rnum(b4)
        w4 = qword(c4, 'WEAK') if fa['side'] in ('longs', 'shorts') else 'WEAK'        # STRONG needs a named side
        add(4, a4, n4, ['T_FORCED', 'T_WHERE', 'FORCED', 'READINGS'], w4)
    elif b4:
        add(4, 'forced side not measured (no FORCED.tsv row as of the fires); ' + rtext(b4), rnum(b4), ['T_WHERE', 'READINGS'],
            qword(c4, 'WEAK'))
    elif conds and 'liquidation' in conds.lower():
        add(4, 'DEF conditions (prose, not measured here): ' + conds, 'no FORCED.tsv row, no Q4 reading', ['DEF'], 'OPINION')
    else:
        add(4, 'NOT_ANSWERED: no FORCED.tsv row and no Q4 reading (A1.S08, E2.S06, EPI forced_usd_log ...)', 'none', [], 'NOT_ANSWERED')
    # Q5
    b5, c5 = best(5)
    if fa['side'] in ('longs', 'shorts'):
        a5 = 'the forced %s pay the price concession at entry (the forced side is the payer, Coval-Stafford 2007)' % fa['side']
        if primary:
            a5 += '; DEF truth label %s' % primary
        if b5:
            a5 += '; ' + rtext(b5)
        n5 = 'forced share %s of %d fires; temporary vs permanent split: Q6 (AFTER)' % (
            f2(fa['longs'] if fa['side'] == 'longs' else fa['shorts'], 2, False), fa['fires'])
        if b5:
            n5 += '; ' + rnum(b5)
        add(5, a5, n5, ['T_FORCED', 'T_WHERE', 'READINGS', 'DEF'], qword(c5, 'WEAK'))
    elif b5:
        add(5, 'payer side not measured (forced side %s); ' % (fa['side'] or 'none') + rtext(b5), rnum(b5), ['T_WHERE', 'READINGS'],
            qword(c5, 'WEAK'))
    elif primary:
        add(5, 'DEF truth label %s (prose: the payer is not measured here)' % primary, 'no forced side, no Q5 reading', ['DEF'], 'OPINION')
    else:
        add(5, 'NOT_ANSWERED: no forced side (FORCED.tsv) and no Q5 reading (CTX fills_one_sided ...)', 'none', [], 'NOT_ANSWERED')
    # Q6 (money and AFTER)
    if ok.any():
        cn = cmean(R, NET[ok], W[ok], CL[ok])
        ek = np.isfinite(EDGE)
        ce = cmean(R, EDGE[ek], W[ek], CL[ek]) if ek.any() else dict(mean=np.nan, lo=np.nan, hi=np.nan, z=np.nan, clusters=0)
        pm_e = []
        for m in ctx.months:
            mk = ek & (MO == m)
            pm_e.append(cmean(R, EDGE[mk], W[mk], CL[mk])['mean'] if mk.any() else float('nan'))
        pm_n = []
        for m in ctx.months:
            mk = ok & (MO == m)
            pm_n.append(cmean(R, NET[mk], W[mk], CL[mk])['mean'] if mk.any() else float('nan'))
        same6, mok6 = same_months(ce['mean'], pm_e, len(ctx.months))
        r1h = isum['ALL']['1h']
        typ = ('' if not np.isfinite(r1h) else 'comes back: later trades return the price (liquidity), they pay our exit'
               if r1h < RETAINED_CUT else 'stays: nobody returns the price (information), nobody pays our exit')
        a6 = 'net %s %s pct a fire (95%% %s..%s, %d waves); vs tough moments %s (z %s)' % (
            exit_name or '?', f2(cn['mean']), f2(cn['lo']), f2(cn['hi']), cn['clusters'], f2(ce['mean']), f2(ce['z']))
        a6 += ('; price %s, retained at 1h %s (AFTER)' % (typ, f2(r1h, 2, False))) if typ else '; impact split not measured (no move in)'
        aft = [s for s in wstat.values() if s['tag'] == 'AFTER' and s['all']['fires'] > 0]
        n6 = 'net by month %s; edge by month %s, same sign %d of %d; retained 15m/1h/4h %s/%s/%s; AFTER readings %d (T_WHERE tag AFTER)' % (
            ' '.join('%s:%s' % (m, f2(v)) for m, v in zip(ctx.months, pm_n)), ' '.join('%s:%s' % (m, f2(v)) for m, v in zip(ctx.months, pm_e)),
            same6, len(ctx.months), f2(isum['ALL']['15m'], 2, False), f2(r1h, 2, False), f2(isum['ALL']['4h'], 2, False), len(aft))
        w6 = 'STRONG' if (cn['clusters'] >= MIN_WAVES and mok6 and np.isfinite(ce['z']) and abs(ce['z']) >= zc) else 'WEAK'
        add(6, a6, n6, ['T_IMPACT', 'T_WHERE', 'MONEY'], w6)
    else:
        add(6, 'NOT_ANSWERED: no MONEY.tsv net for the block fires (the GRADE nets)', 'none', [], 'NOT_ANSWERED')
    # Q7
    ca = csum['ALL']
    if ca['waves'] > 0:
        a7 = '%s (net sum %s over %d waves; top 1 share %s, net without the top wave %s)' % (
            ca['answer'], f2(ca['total']), ca['waves'], f2(ca['sh1'], 2, False), f2(ca['ex1']))
        n7 = 'top5 share %s, net without top 5 %s; by month %s; never STRONG in V1 (no matched comparison of concentration)' % (
            f2(ca['sh5'], 2, False), f2(ca['ex5']), ' '.join('%s:%s' % (m, csum[m]['answer']) for m in ctx.months))
        add(7, a7, n7, ['T_CONC', 'MONEY'], 'WEAK')
    else:
        add(7, 'NOT_ANSWERED: no MONEY.tsv net for the block fires', 'none', [], 'NOT_ANSWERED')
    # Q8
    lone, multi = ok & (SIZE == 1), ok & (SIZE >= 2)
    if lone.any() and multi.any():
        cl_, cm_ = cmean(R, NET[lone], W[lone], CL[lone]), cmean(R, NET[multi], W[multi], CL[multi])
        diff = cl_['mean'] - cm_['mean']
        se = math.sqrt(cl_['se'] ** 2 + cm_['se'] ** 2) if (np.isfinite(cl_['se']) and np.isfinite(cm_['se'])) else float('nan')
        z8 = diff / se if (np.isfinite(se) and se > 0) else float('nan')
        pmd = []
        for m in ctx.months:
            a_, b_ = lone & (MO == m), multi & (MO == m)
            pmd.append(cmean(R, NET[a_], W[a_], CL[a_])['mean'] - cmean(R, NET[b_], W[b_], CL[b_])['mean']
                       if (a_.any() and b_.any()) else float('nan'))
        same8, mok8 = same_months(diff, pmd, len(ctx.months))
        verb = 'pay less than' if diff < 0 else 'pay more than' if diff > 0 else 'pay the same as'
        a8 = 'lone fires %s waves of 2+: net %s (%d waves) vs %s (%d waves)' % (verb, f2(cl_['mean']), cl_['clusters'], f2(cm_['mean']),
                                                                              cm_['clusters'])
        n8 = 'lone minus waves %s, z %s (z_crit %.2f); by month %s, same sign %d of %d; T_SINGLE by size x breadth x month' % (
            f2(diff), f2(z8), zc, ' '.join('%s:%s' % (m, f2(v)) for m, v in zip(ctx.months, pmd)), same8, len(ctx.months))
        w8 = 'STRONG' if (cl_['clusters'] >= MIN_WAVES and cm_['clusters'] >= MIN_WAVES and mok8 and np.isfinite(z8) and abs(z8) >= zc) \
            else 'WEAK'
        add(8, a8, n8, ['T_SINGLE', 'MONEY'], w8)
    elif ok.any():
        add(8, 'NOT_ANSWERED: only %s in the block (needs both lone fires and waves of 2+)' % ('lone fires' if lone.any() else 'waves'),
            'lone %d fires, waves %d fires' % (int(lone.sum()), int(multi.sum())), ['T_SINGLE', 'MONEY'], 'NOT_ANSWERED')
    else:
        add(8, 'NOT_ANSWERED: no MONEY.tsv net for the block fires', 'none', [], 'NOT_ANSWERED')
    meta['exit'] = exit_name
    meta['move_code'] = mcode
    return dict(rows=rows, tables=tables, meta=meta, status=status)


# ---------------------------------------------------------------------------------------------------- inputs
COLS = {'FIRES': ('alarm_id', 'coin', 't', 'side'), 'READINGS': ('who', 'coin', 't', 'code', 'value', 'known_at'),
        'FORCED': ('coin', 't', 'long_usd', 'short_usd', 'known_at'),
        'MONEY': ('coin', 't', 'side', 'exit', 'fade_gross_15m', 'fade_gross_1h', 'fade_gross_4h', 'net', 'edge_tough')}


def read_tsv(path, need=()):
    with open(path, newline='') as f:
        rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
        cols = rows[0].keys() if rows else None
    if cols is None:
        with open(path) as f:
            head = [l for l in f if not l.startswith('#')][:1]
        cols = head[0].rstrip('\n').split('\t') if head else []
    miss = [c for c in need if c not in cols]
    if miss:
        raise Refused('BAD_INPUT', '%s lacks columns %s' % (path, miss))
    return rows


def read_def(path, want):
    if not os.path.isfile(path):
        raise Refused('BAD_INPUT', 'no DEF %s' % path)
    got = sha16_file(path)
    if got != want:
        raise Refused('SOURCE_CHANGED', 'DEF %s is %s, expected %s' % (path, got, want))
    return json.load(open(path)), got


def load_bundle(folder, alarm, def_sha16, true_row=None, fl_row=None, family_tags=None):
    """the JOIN bundle -> (B, sources [(role, path, sha16, rows, note)])"""
    if not os.path.isdir(folder) or not os.path.isfile(os.path.join(folder, 'FIRES.tsv')):
        raise Refused('BAD_INPUT', 'no FIRES.tsv in %s' % folder)
    B = dict(fires=[], readings=[], forced=[], money=[], labels={})
    src = []
    for role in ('FIRES', 'READINGS', 'FORCED', 'MONEY'):
        p = os.path.join(folder, role + '.tsv')
        if not os.path.isfile(p):
            src.append((role, p, '', 0, 'absent'))
            continue
        rows = read_tsv(p, COLS[role])
        if role == 'FIRES':
            B['fires'] = [(r['alarm_id'], r['coin'], int(r['t']), int(r['side'])) for r in rows]
        else:
            B[role.lower()] = rows
        src.append((role, p, sha16_file(p), len(rows), ''))
    if true_row:
        rows = read_tsv(true_row, ('verdict',))
        if len(rows) != 1:
            raise Refused('BAD_INPUT', '%s: one row expected' % true_row)
        if rows[0].get('def_sha16') and rows[0]['def_sha16'] != def_sha16:
            raise Refused('SOURCE_CHANGED', 'TRUE_ROW %s binds def %s, not %s' % (true_row, rows[0]['def_sha16'], def_sha16))
        B['labels']['true_verdict'] = rows[0]['verdict']
        src.append(('TRUE_ROW', true_row, sha16_file(true_row), 1, 'true_gate verdict'))
    if fl_row:
        rows = read_tsv(fl_row, ('RULE_9',))
        if len(rows) != 1:
            raise Refused('BAD_INPUT', '%s: one row expected' % fl_row)
        B['labels']['rule9'] = rows[0]['RULE_9']
        src.append(('FL_ROW', fl_row, sha16_file(fl_row), 1, 'first look RULE_9'))
    if family_tags:
        rows = [r for r in read_tsv(family_tags, ('alarm_id', 'family')) if r['alarm_id'] == alarm]
        if rows:
            B['labels']['family_tag'] = rows[0]['family']
        src.append(('FAMILY_TAGS', family_tags, sha16_file(family_tags), len(rows), 'SCOUT opinion'))
    return B, src


# ---------------------------------------------------------------------------------------------------- the card writer
def cell(v):
    if isinstance(v, (float, np.floating)):
        return '' if not np.isfinite(v) else '%.6g' % v
    return str(v)


def write_out(out, card, ctx, sources, tool_path=None):
    os.makedirs(out)
    tool_path = tool_path or os.path.realpath(__file__)
    shas = {}
    for name in ('T_FIRES', 'T_WAVES', 'T_WHEN', 'T_WHERE', 'T_FORCED', 'T_IMPACT', 'T_CONC', 'T_SINGLE'):
        cols, rows = card['tables'][name]
        p = os.path.join(out, name + '.tsv')
        with open(p, 'x') as f:
            f.write('\t'.join(cols) + '\n')
            for r in rows:
                f.write('\t'.join(cell(v).replace('\t', ' ').replace('\n', ' ') for v in r) + '\n')
        shas[name] = sha16_file(p)
    srcs = [('DEF', ctx.def_path, ctx.def_sha16, 1, 'checked')] + list(sources)
    srcs += [('release pin', os.path.join(ctx.R.root, r), s, '', 'checked') for r, s in ctx.R.pins]
    srcs += [('tool', tool_path, sha16_file(tool_path), '', EDITION)]
    p = os.path.join(out, 'T_SOURCES.tsv')
    with open(p, 'x') as f:
        f.write('role\tpath\tsha16\trows\tnote\n')
        for r in srcs:
            f.write('\t'.join(cell(v) for v in r) + '\n')
    shas['T_SOURCES'] = sha16_file(p)
    inp = {r[0]: r for r in srcs}

    def ev(names):
        out_ = []
        for nm in names:
            if nm in shas:
                out_.append('%s.tsv %s' % (nm, shas[nm]))
            elif nm in inp and inp[nm][2]:
                out_.append('%s %s' % (os.path.basename(inp[nm][1]), inp[nm][2]))      # the full path: T_SOURCES.tsv
        return '; '.join(out_) or 'none'

    m = card['meta']
    lines = ['# ALARM_CARD %s, block %s' % (ctx.alarm, ctx.block), '',
             '- edition: %s; tool sha16 %s; spec %s' % (EDITION, sha16_file(tool_path), SPEC),
             '- alarm: %s; DEF %s sha16 %s (checked)' % (ctx.alarm, ctx.def_path, ctx.def_sha16),
             '- block: %s = %d..%d (months %s); no closed day inside (lab3 law.py research_refusal; card closed from %d)' % (
                 ctx.block, ctx.first, ctx.last, ' '.join(ctx.months), ctx.closed_from),
             '- fires: %d listed, %d on closed days dropped before the waves, %d in the block in %d waves; money exit %s' % (
                 m['fires_listed'], m['fires_closed_dropped'], m['fires_block'], m['waves_block'], m.get('exit') or 'none'),
             '- sources: T_SOURCES.tsv %s (every input, release pin and the tool, each with its sha16)' % shas['T_SOURCES'],
             '- words: STRONG = PROVEN codes, %d+ waves, same sign in %d of %d months, beats matched moments (|z| >= z_crit %.2f, '
             'Bonferroni over k %d tests at family-wise alpha %.2f); WEAK = measured, fails one; OPINION = hand tag or prose; '
             'NOT_ANSWERED = names the missing input. A code not PROVEN in metric_brief_v2 caps at WEAK; a STOP code is refused.' % (
                 MIN_WAVES, MONTHS_SAME, MONTHS_NEED, m['z_crit'], m['k_tests'], ALPHA),
             '- AFTER: readings, liquidations and money known after the fire are tagged AFTER and never feed Q1-Q5 '
             '(%d AFTER liquidation rows ignored; AFTER readings in T_WHERE, shown in Q6).' % m.get('forced_after_ignored', 0),
             '- status: playground result, TEST, not reviewed: never a PASS; describes, never selects.']
    win_last = int(str((ctx.defn.get('window') or {}).get('last') or 0) or 0)
    for c in def_codes(ctx.defn):
        last = str((ctx.cards.get(c) or {}).get('last') or '').strip()
        if last.isdigit() and (int(last) < ctx.last or (win_last and int(last) < win_last)):
            lines.append('- caveat: code %s card LAST DAY %s; block ends %d, DEF window ends %s: the card does not cover the days after %s.'
                         % (c, last, ctx.last, win_last or '?', last))
    if ctx.planted:
        lines.append('- PLANTED: code status from a planted table (a test), not metric_brief_v2.')
    lines += ['', '| Q | question | answer | numbers | evidence | word |', '|---|---|---|---|---|---|']
    for r in card['rows']:
        lines.append('| Q%d | %s | %s | %s | %s | %s |' % (r['q'], r['question'], r['answer'].replace('|', '/'), r['numbers'].replace('|', '/'),
                                                          ev(r['evidence']), r['word']))
    lines += ['', '## Tables', '']
    for name in ('T_FIRES', 'T_WAVES', 'T_WHEN', 'T_WHERE', 'T_FORCED', 'T_IMPACT', 'T_CONC', 'T_SINGLE', 'T_SOURCES'):
        lines.append('- %s.tsv %s' % (name, shas[name]))
    p = os.path.join(out, 'ALARM_CARD.md')
    with open(p, 'x') as f:
        f.write('\n'.join(lines) + '\n')
    return p, sha16_file(p)


# ---------------------------------------------------------------------------------------------------- command line
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == 'bundle':                 # SCO-A136 6 Nov: the bundle builder (bundle_builder_v1.py beside this file)
        import importlib.util
        bp = os.environ.get('AU_BUILDER') or os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bundle_builder_v1.py')
        sp = importlib.util.spec_from_file_location('bundle_builder_v1', bp)
        BB = importlib.util.module_from_spec(sp); sp.loader.exec_module(BB)
        return BB.main(argv)
    ap = argparse.ArgumentParser(description='alarm_understand V1: one ALARM_CARD for one alarm and one month block (a reader)')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('check', 'card'):
        p = sub.add_parser(name)
        if name == 'card':
            p.add_argument('out')
        p.add_argument('--alarm', required=True)
        p.add_argument('--def', dest='def_path', required=True)
        p.add_argument('--def-sha16', required=True)
        p.add_argument('--block', required=True)
        p.add_argument('--card-closed-from', type=int, default=CARD_CLOSED_FROM)
        if name == 'card':
            p.add_argument('--bundle', required=True)
            p.add_argument('--true-row')
            p.add_argument('--fl-row')
            p.add_argument('--family-tags')
    a = ap.parse_args(argv)
    try:
        if a.card_closed_from > CARD_CLOSED_FROM:
            raise Refused('BAD_ARGS', '--card-closed-from may only move earlier than %d' % CARD_CLOSED_FROM)
        R = release()                                                          # pins first: SOURCE_CHANGED
        check_block(a.block, R.LAW.research_refusal, a.card_closed_from)       # then the block, before any input is read
        if a.cmd == 'card' and os.path.exists(a.out):
            raise Refused('OUT_EXISTS', a.out)
        defn, dsha = read_def(a.def_path, a.def_sha16)
        ctx = make_context(R, a.alarm, a.block, defn, closed_from=a.card_closed_from, def_path=os.path.realpath(a.def_path),
                           def_sha16=dsha)
        if a.cmd == 'check':
            print('CHECK OK alarm %s block %s (%d..%d) def %s; pins %d checked; DEF codes %s; nothing else read' % (
                a.alarm, a.block, ctx.first, ctx.last, dsha, len(R.pins), ', '.join('%s %s' % kv for kv in sorted(ctx.status.items())) or 'none'))
            return 0
        B, sources = load_bundle(a.bundle, a.alarm, dsha, a.true_row, a.fl_row, a.family_tags)
        card = build_card(B, ctx)
        p, s = write_out(a.out, card, ctx, sources)
        print('CARD %s sha16 %s; words %s' % (p, s, ' '.join('Q%d:%s' % (r['q'], r['word']) for r in card['rows'])))
        return 0
    except Refused as e:
        print('REFUSED %s: %s' % (e.code, e.detail))
        return 2
    except Exception as e:
        print('FAILED %s: %s' % (type(e).__name__, e))
        return 3


if __name__ == '__main__':
    sys.exit(main())
