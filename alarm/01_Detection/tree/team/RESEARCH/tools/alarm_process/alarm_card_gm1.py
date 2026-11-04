# alarm_card_gm1.py (BUILD5 for SCOUT, G1 D4, 31 Oct 2026; TEST, NOT REVIEWED; the owner 31 Oct 13:28 Berlin: "Their tools need to be fast and
# refactored properly"): ONE card for GRADE and MONTH, made by team/BUILD5/proposals/alarm_card_gm1/make_card_gm1.py from alarm_card_v1_2_1.py
# 121304e1471d7e41 (GRADE) and alarm_card_v1_3_1.py 3c496708f9d44651 (MONTH), both never edited. Changed, nothing else: --windows GRADE|MONTH
# (missing or another word: REFUSED NO_WINDOWS, exit 2) picks WINDOW and the card name the outputs print (CARDS below), so the outputs are
# byte-equal to v1_2_1's (GRADE) and v1_3_1's (MONTH). alarm_card_v1_2_1.py's text follows.
# alarm_card_v1_2_1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): alarm_card_v1_2.py c3172f94e389cadb (STRATEGY 28 Oct) with only its paths changed
# (CLEAN_RELEASE_V1; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the release folder only"): F, the lab code it
# imports (lab3, labcore, event_outcomes), is <Alarm>/01_Detection/tree (settings_v1.alarm_root), never the dev tree. Its labels still say
# v1_2 (the CARD line, SUM row card), so its outputs are byte-equal to v1_2 on the same inputs; the chain's INPUTS_<V>.txt names this file.
# alarm_card_v1_2.py (STRATEGY 28 Oct 2026; v1_2 = v1_1 + a HARDCODED date range, WINDOW below: it refuses any alarm or random row outside
# it, so its sha16 says which months it can read (ALARM_DESIGN TOOLS_REGISTRY.tsv); months from the data (YYMM labels, any count);
# checks at 5 min too; the other side at 5 min / 15 min / 1 h; per-month numbers in SUM (forward reads); TEST, NOT REVIEWED).
# alarm_card_v1_1.py (STRATEGY 27 Oct 2026; v1_1 = v1 + --screen (no matched random: the alarm's own levels and the reads against the base
# only, for screening parts fast) + took / skipped / all-base in SUM), team/RESEARCH/tools/alarm_process; TEST, NOT REVIEWED): the ALARM CARD of one variant from the
# alarm grader's stored runs (reads only, no new run). Races (offer before heat: the share of moments where the offer level is touched
# before the heat level; heat first or neither = no), alarm vs matched random, all and by month; reach and the heat before it; checks
# without the top 5 coins and the best 5 days; with --base B: the PAIRED read (each fire against the base alarm's latest fire of the same
# coin and side within the hour before: the same move entered at the base's moment = timing), the base fires the alarm skipped, and the
# alarm against random sets of the base's fires of the same size (selection + timing). One result per wave, like LEAD's menu_v2.py
# (alarm weight 1/wave size, 30 min gap any coin; random weight from RND_<V>_V1_WEIGHTS<sfx>.tsv).
#   python3 alarm_card_v1.py <W> <V> [--base B] [--lean FADE|FOLLOW] [--wsfx _OWNFREE] [--tsv SUM_<V>.tsv (key, value; refuses an existing file)] [--draws 1000]
import sys, os, collections, argparse, datetime as dt, numpy as np
def _lab_tree():
    """K4 (SCOUT 30 Oct 2026; CLEAN_RELEASE_V1 section 6): the lab code inside the Alarm folder that holds this file, in the dev layout
    (<Alarm>/01_Detection/tree: team/LAB3/code and team/RESEARCH/tools), never the dev tree. The Alarm folder is settings_v1.alarm_root
    (the nearest parent with _tools/settings_v1.py and settings/), read with the package's own settings_v1; outside one: refused."""
    import importlib.util
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s (run it from the Alarm folder)' % os.path.abspath(__file__))
        d = os.path.dirname(d)
    sp = importlib.util.spec_from_file_location('settings_v1', os.path.join(d, '_tools', 'settings_v1.py'))
    sv = importlib.util.module_from_spec(sp); sp.loader.exec_module(sv)
    try:
        f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')
    except sv.Refused as e:
        raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s' % e)
    if not (os.path.isdir(os.path.join(f, 'team', 'LAB3', 'code')) and os.path.isdir(os.path.join(f, 'team', 'RESEARCH', 'tools'))):
        raise SystemExit('NO LAB TREE IN THE ALARM FOLDER: %s (01_Detection/tree with team/LAB3/code and team/RESEARCH/tools)' % f)
    return f
F = _lab_tree(); CODE = F + '/team/LAB3/code'   # K4: was the dev tree's absolute path
sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')
import event_outcomes as EO
from labcore import waves as WV
ap = argparse.ArgumentParser(); ap.add_argument('W'); ap.add_argument('V'); ap.add_argument('--base'); ap.add_argument('--lean', default='FADE')
ap.add_argument('--wsfx', default=''); ap.add_argument('--screen', action='store_true'); ap.add_argument('--tsv'); ap.add_argument('--draws', type=int, default=1000)
ap.add_argument('--windows', default=None); a = ap.parse_args()   # gm1: GRADE or MONTH, required, no default
W, V, L = a.W, a.V, a.lean; DS = ['FADE', 'FOLLOW']
CARDS = {'GRADE': (('20250910', '20260228'), 'v1_2'), 'MONTH': (('20250910', '20260531'), 'v1_3')}   # gm1: each card's date range and its printed name
if a.windows not in CARDS:
    sys.stderr.write('REFUSED NO_WINDOWS: --windows GRADE or MONTH, got %r\n' % (a.windows,)); sys.exit(2)
WINDOW, CV = CARDS[a.windows]   # gm1: rows outside WINDOW are refused (the card's hardcoded date range, as before)
RACES = [('1c<1c 5m', 'OFFER1C_BEFORE_HEAT1C_5M'), ('1c<1c 15m', 'OFFER1C_BEFORE_HEAT1C_15M'), ('1c<1c 1h', 'OFFER1C_BEFORE_HEAT1C_60M'),
         ('2c<1c 5m', 'OFFER2C_BEFORE_HEAT1C_5M'), ('2c<1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M'), ('2c<1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M'),
         ('3c<1c 15m', 'OFFER3C_BEFORE_HEAT1C_15M'), ('3c<1c 1h', 'OFFER3C_BEFORE_HEAT1C_60M'), ('4c<1c 1h', 'OFFER4C_BEFORE_HEAT1C_60M'),
         ('2c<2c 1h', 'OFFER2C_BEFORE_HEAT2C_60M'), ('4c<2c 1h', 'OFFER4C_BEFORE_HEAT2C_60M'), ('4c<2c 5h', 'OFFER4C_BEFORE_HEAT2C_5H')]
KEY = [('1c<1c 15m', 'OFFER1C_BEFORE_HEAT1C_15M'), ('2c<1c 5m', 'OFFER2C_BEFORE_HEAT1C_5M'), ('2c<1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M'),
       ('2c<1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M'), ('3c<1c 1h', 'OFFER3C_BEFORE_HEAT1C_60M'), ('4c<1c 1h', 'OFFER4C_BEFORE_HEAT1C_60M')]
REACH = [(k, h) for h in ['5M', '15M', '60M'] for k in [1, 2, 4]]

def sides(path):
    m = {}
    for l in list(open(path))[1:]:
        f = l.rstrip('\n').split('\t'); m[(f[0], int(float(f[1])))] = int(float(f[2]))
    return m

def load(root, subj, side_of):
    cat = set()
    for l in open(os.path.join(root, 'OUT_CATALOG_%s.tsv' % subj)):
        if l.startswith('OUT.'):
            cat.add(l.split('\t')[0].split('.', 2)[2])
    cols = ['unit__c'] + [c for _, lab in RACES for D in DS for c in ['%s__%s' % (lab, D)] if c in cat]
    cols += [c for D in DS for k, h in REACH for c in ('REACH_%dC_%s__%s' % (k, h, D), 'REACH_%dC_%s__%s__t' % (k, h, D), 'HEATB_%dC_%s__%s' % (k, h, D)) if c in cat]
    R = EO.read(root, CODE, subj, cols); o = {c: np.asarray(R[c]['value'], float) for c in cols}
    o['coin'] = np.asarray(R[cols[0]]['coin']); o['t'] = (np.asarray(R[cols[0]]['as_of_us']) // 10**6).astype(np.int64)
    for c in cols[1:]:
        assert np.array_equal(np.asarray(R[c]['coin']), o['coin']), 'row order differs in ' + c
    o['m'] = np.array([dt.datetime.utcfromtimestamp(int(x)).strftime('%y%m') for x in o['t']])
    o['d'] = np.array([dt.datetime.utcfromtimestamp(int(x)).strftime('%Y%m%d') for x in o['t']])
    o['side'] = np.array([side_of.get((c, int(t)), 0) for c, t in zip(o['coin'], o['t'])]); o['cols'] = set(cols); return o

def wave_w(o):
    wv = WV.waves(o['t'].astype(float), 1800); cnt = collections.Counter(wv)
    o['wave'] = np.asarray(wv); o['w'] = np.array([1.0 / cnt[k] for k in wv]); return len(cnt)

def share(o, x, m=None):
    ok = np.isfinite(x) & (o['w'] > 0)
    if m is not None:
        ok &= m
    s = np.sum(o['w'][ok]); return np.sum(o['w'][ok] * x[ok]) / s if s > 0 else np.nan

def win(o, col):
    x = o[col]; return np.where(np.isfinite(x), (x == 1).astype(float), np.nan)

def wq(o, col, q, m=None):
    if col not in o['cols']:
        return np.nan
    x = o[col]; ok = np.isfinite(x) & (o['w'] > 0)
    if m is not None:
        ok &= m
    if not ok.any():
        return np.nan
    v, w = x[ok], o['w'][ok]; i = np.argsort(v, kind='mergesort'); v, w = v[i], np.cumsum(w[i]); return v[min(np.searchsorted(w, q * w[-1]), len(v) - 1)]

def sub(o, idx, w=None):
    s = {k: (v[idx] if isinstance(v, np.ndarray) else v) for k, v in o.items()}
    if w is not None:
        s['w'] = w
    return s

def p(x): return ' na' if x != x else '%3.0f' % (100 * x)
def d(x, y): return '   na' if x != x or y != y else '%+5.1f' % (100 * (x - y))

A_side = sides('%s/%s_FIRES_V1_LIST.tsv' % (W, V)); A = load('%s/om_%s_v1' % (W, V), 'IDEA2%sMENU' % V, A_side); nw = wave_w(A)
if a.screen:
    Rn = {k: (v[:0] if isinstance(v, np.ndarray) else v) for k, v in A.items()}; Rn['w'] = np.zeros(0); Rn['cols'] = set()   # no random: every random number reads na
else:
    Rn = load('%s/om_%sRND_v1' % (W, V), 'IDEA2%sRNDMENU' % V, sides('%s/RND_%s_V1_LIST.tsv' % (W, V))); wt = {}
    for l in list(open('%s/RND_%s_V1_WEIGHTS%s.tsv' % (W, V, a.wsfx)))[1:]:
        c, t, x = l.rstrip('\n').split('\t'); wt[(c, int(t))] = float(x)
    Rn['w'] = np.array([wt.get((c, int(t)), 0.0) for c, t in zip(Rn['coin'], Rn['t'])])
for o_, nm_ in ((A, 'alarm'), (Rn, 'random')):
    bad = [x for x in o_['d'] if not (WINDOW[0] <= x <= WINDOW[1])]
    if bad:
        raise SystemExit('OUTSIDE_WINDOW %s: %d rows outside %s-%s (first %s, last %s): refused' % (nm_, len(bad), WINDOW[0], WINDOW[1], min(bad), max(bad)))
MS = sorted(set(A['m'])); NM = len(MS)
out = []; P = out.append
mc = {m: (int(np.sum(A['m'] == m)), len(set(A['wave'][A['m'] == m]))) for m in MS}
P('CARD %s | data %s-%s, card %s window %s-%s | %d fires, %d waves (%s) | random %d moments (%d with weight) | median c %.3f%% | lean %s'
  % (V, min(A['d']), max(A['d']), CV, WINDOW[0], WINDOW[1], len(A['t']), nw, ' '.join('%s %d/%d' % (m, *mc[m]) for m in MS), len(Rn['t']), int(np.sum(Rn['w'] > 0)), np.nanmedian(A['unit__c']), L))
P('One result per wave. c = the coin round-trip cost. Race "2c<1c 15m" = the price touches +2c (the side) before -1c within 15 min.')
P('\nRACES: alarm / random (%), alarm minus random (points) | by month (points) | months above random')
def race(o, D, lab, m=None): return share(o, win(o, '%s__%s' % (lab, D)), m)
for D in DS:
    for nm, lab in RACES:
        c = '%s__%s' % (lab, D)
        if c not in A['cols'] or (c not in Rn['cols'] and not a.screen):
            continue
        x, y = race(A, D, lab), (race(Rn, D, lab) if not a.screen else np.nan)
        md = [(race(A, D, lab, A['m'] == m), race(Rn, D, lab, Rn['m'] == m) if not a.screen else np.nan) for m in MS]
        P('  %-6s %-10s %s /%s %s | %s | %d/%d' % (D, nm, p(x), p(y), d(x, y), ' '.join('%s %s' % (m, d(*z)) for m, z in zip(MS, md)), sum(1 for z in md if z[0] == z[0] and z[1] == z[1] and z[0] > z[1]), NM))
P('\nREACH +kc within the window: alarm / random (%) diff | heat before it (c), only moments that reach: median, p75 alarm [random] | minutes to reach, median alarm [random]')
for D in DS:
    for k, h in REACH:
        r = 'REACH_%dC_%s__%s' % (k, h, D); hb = 'HEATB_%dC_%s__%s' % (k, h, D); tt = r + '__t'
        if r not in A['cols']:
            continue
        x, y = share(A, A[r]), (share(Rn, Rn[r]) if not a.screen else np.nan)
        P('  %-6s %-3s +%dc: %s /%s %s | heat %.2f, %.2f [%.2f, %.2f] | %5.1f [%5.1f] min' % (D, h, k, p(x), p(y), d(x, y), wq(A, hb, .5), wq(A, hb, .75), wq(Rn, hb, .5), wq(Rn, hb, .75), wq(A, tt, .5) / 60, wq(Rn, tt, .5) / 60))
P('\nCHECKS on the lean (%s), alarm minus random (points)' % L)
top5 = [c for c, _ in collections.Counter(A['coin']).most_common(5)]; chk = {}
for nm, lab in [('2c<1c 5m', 'OFFER2C_BEFORE_HEAT1C_5M'), ('2c<1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M'), ('2c<1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M')]:
    c = '%s__%s' % (lab, L); wd = collections.defaultdict(float)
    for dd, w, x in zip(A['d'], A['w'], win(A, c)):
        if x == x:
            wd[dd] += w * x
    best5 = [k for k, _ in sorted(wd.items(), key=lambda kv: -kv[1])[:5]]
    g = lambda ma, mr: 100 * (race(A, L, lab, ma) - race(Rn, L, lab, mr))
    nc_a, nc_r = ~np.isin(A['coin'], top5), ~np.isin(Rn['coin'], top5); nd_a, nd_r = ~np.isin(A['d'], best5), ~np.isin(Rn['d'], best5)
    chk[nm] = (g(None, None), g(nc_a, nc_r), g(nd_a, nd_r), g(nc_a & nd_a, nc_r & nd_r))
    P('  %-10s all %+5.1f | without top-5 coins (%s) %+5.1f | without best 5 days (%s) %+5.1f | without both %+5.1f' % (nm, chk[nm][0], ','.join(top5), chk[nm][1], ','.join(best5), chk[nm][2], chk[nm][3]))
row = collections.OrderedDict([('variant', V), ('base', a.base or ''), ('fires', len(A['t'])), ('waves', nw)])
for nm, lab in KEY:
    c = '%s__%s' % (lab, L)
    if c in A['cols'] and (c in Rn['cols'] or a.screen):
        x = race(A, L, lab); y = race(Rn, L, lab) if not a.screen else np.nan
        md = [(race(A, L, lab, A['m'] == m), race(Rn, L, lab, Rn['m'] == m) if not a.screen else np.nan) for m in MS]
        row[nm + ' a'] = '%.1f' % (100 * x); row[nm + ' r'] = '%.1f' % (100 * y); row[nm + ' months+'] = sum(1 for z in md if z[0] > z[1])
        row[nm + ' months'] = NM
        for m, z in zip(MS, md):
            row['%s a %s' % (nm, m)] = '%.1f' % (100 * z[0]); row['%s r %s' % (nm, m)] = '%.1f' % (100 * z[1])
for nm, lab in [('2c<1c 5m', 'OFFER2C_BEFORE_HEAT1C_5M'), ('2c<1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M'), ('2c<1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M')]:
    c = '%s__%s' % (lab, 'FOLLOW' if L == 'FADE' else 'FADE')
    if c in A['cols']:
        row['other side %s a-r' % nm] = '%.1f' % (100 * (share(A, win(A, c)) - share(Rn, win(Rn, c))))
for k, h in [(2, '15M'), (4, '60M')]:
    r = 'REACH_%dC_%s__%s' % (k, h, L)
    row['reach %dc %s a' % (k, h)] = '%.1f' % (100 * share(A, A[r])); row['reach %dc %s r' % (k, h)] = '%.1f' % (100 * share(Rn, Rn[r]))
    row['heat %dc %s a' % (k, h)] = '%.2f' % wq(A, 'HEATB_%dC_%s__%s' % (k, h, L), .5); row['heat %dc %s r' % (k, h)] = '%.2f' % wq(Rn, 'HEATB_%dC_%s__%s' % (k, h, L), .5)
for nm in ('2c<1c 5m', '2c<1c 15m', '2c<1c 1h'):
    row['no top5 coins %s' % nm] = '%.1f' % chk[nm][1]; row['no best5 days %s' % nm] = '%.1f' % chk[nm][2]; row['no both %s' % nm] = '%.1f' % chk[nm][3]
mw = collections.Counter(A['m']); row['window'] = '%s-%s' % WINDOW; row['card'] = 'alarm_card_%s.py' % CV
for m in MS:
    row['fires %s' % m] = int(mw[m]); row['waves %s' % m] = len(set(A['wave'][A['m'] == m]))

if a.base:
    B = a.base; Bo = load('%s/om_%s_v1' % (W, B), 'IDEA2%sMENU' % B, sides('%s/%s_FIRES_V1_LIST.tsv' % (W, B))); nbw = wave_w(Bo)
    idx = collections.defaultdict(list)
    for i, (c, s, t) in enumerate(zip(Bo['coin'], Bo['side'], Bo['t'])):
        idx[(c, int(s))].append((int(t), i))
    pair = np.full(len(A['t']), -1); dl = np.full(len(A['t']), np.nan)
    for j, (c, s, t) in enumerate(zip(A['coin'], A['side'], A['t'])):
        for tb, i in idx.get((c, int(s)), []):
            if t - 3600 <= tb <= t:
                pair[j] = i; dl[j] = (t - tb) / 60.0
    ok = pair >= 0; Ap = sub(A, ok); Bp = sub(Bo, pair[ok], w=A['w'][ok]); Bp['m'] = Ap['m']
    P('\nPAIRED with base %s (%d fires, %d waves): %d of %d fires have a base fire of the same coin and side in the hour before (%.0f%% of the wave weight)'
      % (B, len(Bo['t']), nbw, int(ok.sum()), len(ok), 100 * np.sum(A['w'][ok]) / np.sum(A['w'])))
    if ok.any():
        q = np.percentile(dl[ok], [10, 50, 75, 90]); P('  delay after the base fire, minutes: p10 %.1f, median %.1f, p75 %.1f, p90 %.1f' % tuple(q))
        P('  SAME MOVES, alarm at its moment / base at its moment (%%) diff | by month (points) [timing: a + diff = waiting for this alarm helped]')
        for nm, lab in KEY:
            c = '%s__%s' % (lab, L)
            if c not in A['cols'] or c not in Bo['cols']:
                continue
            x, y = race(Ap, L, lab), race(Bp, L, lab); md = [(race(Ap, L, lab, Ap['m'] == m), race(Bp, L, lab, Bp['m'] == m)) for m in MS]
            P('    %-10s %s /%s %s | %s' % (nm, p(x), p(y), d(x, y), ' '.join('%s %s' % (m, d(*z)) for m, z in zip(MS, md))))
            row['paired %s a-b' % nm] = '%.1f' % (100 * (x - y))
        for k, h in [(2, '15M'), (4, '60M')]:
            r = 'REACH_%dC_%s__%s' % (k, h, L); hb = 'HEATB_%dC_%s__%s' % (k, h, L)
            P('    reach +%dc %-3s %s /%s %s | heat median %.2f [%.2f]' % (k, h, p(share(Ap, Ap[r])), p(share(Bp, Bp[r])), d(share(Ap, Ap[r]), share(Bp, Bp[r])), wq(Ap, hb, .5), wq(Bp, hb, .5)))
        row['paired fires'] = int(ok.sum()); row['delay median min'] = '%.1f' % q[1]
    used = np.zeros(len(Bo['t']), bool); used[pair[ok]] = True
    Bu, Bs = sub(Bo, used), sub(Bo, ~used)
    P('  BASE FIRES the alarm took / skipped (base weights, base at its moment): %d / %d' % (int(used.sum()), int((~used).sum())))
    for nm, lab in KEY:
        c = '%s__%s' % (lab, L)
        if c in Bo['cols']:
            P('    %-10s took %s | skipped %s | all base %s' % (nm, p(race(Bu, L, lab)), p(race(Bs, L, lab)), p(race(Bo, L, lab))))
            if nm in ('2c<1c 15m', '2c<1c 1h'):
                row['took %s' % nm] = '%.1f' % (100 * race(Bu, L, lab)); row['all base %s' % nm] = '%.1f' % (100 * race(Bo, L, lab))
    rng = np.random.default_rng(20261027); n = len(A['t'])
    if n < len(Bo['t']):
        P('  RANDOM SETS of %d base fires (%d draws, waves recomputed in each set): alarm vs the draws (share of draws at or above the alarm)' % (n, a.draws))
        for nm, lab in [('2c<1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M'), ('2c<1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M'), ('3c<1c 1h', 'OFFER3C_BEFORE_HEAT1C_60M')]:
            c = '%s__%s' % (lab, L)
            if c not in Bo['cols'] or c not in A['cols']:
                continue
            xb = win(Bo, c); vals = []
            for _ in range(a.draws):
                ii = np.sort(rng.choice(len(Bo['t']), n, replace=False)); tt = Bo['t'][ii].astype(float); wv = WV.waves(tt, 1800)
                cnt = collections.Counter(wv); ww = np.array([1.0 / cnt[k] for k in wv]); xx = xb[ii]; f = np.isfinite(xx)
                vals.append(np.sum(ww[f] * xx[f]) / np.sum(ww[f]))
            vals = np.array(vals); x = race(A, L, lab); pv = float(np.mean(vals >= x))
            P('    %-10s alarm %s | draws p50 %s p95 %s | share of draws >= alarm %.3f' % (nm, p(x), p(np.percentile(vals, 50)), p(np.percentile(vals, 95)), pv))
            row['sets p %s' % nm] = '%.3f' % pv
print('\n'.join(out))
if a.tsv:
    if os.path.exists(a.tsv):
        raise SystemExit('SUM_EXISTS %s' % a.tsv)
    with open(a.tsv, 'w') as f:
        f.write('key\tvalue\n' + ''.join('%s\t%s\n' % kv for kv in row.items()))
