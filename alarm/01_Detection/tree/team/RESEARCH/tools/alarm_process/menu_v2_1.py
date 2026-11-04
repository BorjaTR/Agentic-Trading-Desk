# menu_v2_1.py (SCOUT 30 Oct 2026, K4, home team/RESEARCH/tools/alarm_process: the grade chains' own copy; TEST, NOT REVIEWED): LEAD loop2
# menu_v2.py 945a89b99c30abff with only its paths changed (CLEAN_RELEASE_V1): F, the lab code (lab3, labcore, event_outcomes), is
# <Alarm>/01_Detection/tree (settings_v1.alarm_root), never the dev tree; the work folder W comes only from the environment (an absolute
# path: the grade chains export it), no built-in scratch default. Same arguments, same output.
# LOOP2 Outcomes MENU (skill items 1-6) for one alarm vs its matched random, FADE and FOLLOW side by side; one result per wave
# (alarm fire weight 1/wave size; random weight from RND_<v>_V1_WEIGHTS = 1/n x the parent's wave weight); args: variant tag(om|oms)
import sys, collections, datetime as dt, numpy as np, os
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
F = _lab_tree(); code = F + '/team/LAB3/code'   # K4: was the dev tree's absolute path
sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')
import event_outcomes as EO
from labcore import waves as WV
import os; W = os.environ.get('W', ''); v, tag = sys.argv[1], sys.argv[2]; sfx = 'MENU' if tag == 'om' else 'MENUS'
if not os.path.isabs(W): raise SystemExit('NO W: the work folder is the environment variable W, an absolute path (the grade chains export it)')   # K4: no built-in default
HS = ['5M', '15M', '60M', '240M']; KS = [1, 2, 4, 8]; DS = ['FADE', 'FOLLOW']; MS = ['09', '10', '11', '12']
FIRST = [('2c<-1c 15m', 'OFFER2C_BEFORE_HEAT1C_15M', .667), ('2c<-1c 1h', 'OFFER2C_BEFORE_HEAT1C_60M', .667),
         ('2c<-1c 5h', 'OFFER2C_BEFORE_HEAT1C_5H', .667), ('4c<-2c 5h', 'OFFER4C_BEFORE_HEAT2C_5H', .5)]
cols = ['unit__c'] + ['%s__%s' % (n, D) for D in DS for n in
        ['REACH_%dC_%s' % (k, h) for h in HS for k in KS] + ['REACH_%dC_%s__t' % (k, h) for h in HS for k in KS] +
        ['HEATB_%dC_%s' % (k, h) for h in HS for k in KS] + ['BEST_%s' % h for h in HS] + [f[1] for f in FIRST]]
cols = [c.replace('__t__%s' % D, '__%s__t' % D) for c in cols for D in [c.split('__')[-1]]] if False else cols
cols = [c if '__t__' not in c else c.replace('__t__FADE', '__FADE__t').replace('__t__FOLLOW', '__FOLLOW__t') for c in cols]
def load(root, subj):
    R = EO.read(root, code, subj, cols); o = {c: np.asarray(R[c]['value'], float) for c in cols}
    o['coin'] = np.asarray(R[cols[0]]['coin']); o['t'] = np.asarray(R[cols[0]]['as_of_us']) // 10**6; return o
A = load('%s/%s_%s_v1' % (W, tag, v), 'IDEA2%s%s' % (v, sfx)); Rn = load('%s/%s_%sRND_v1' % (W, tag, v), 'IDEA2%sRND%s' % (v, sfx))
wv = WV.waves(A['t'].astype(float), 1800); cnt = collections.Counter(wv); A['w'] = np.array([1.0 / cnt[k] for k in wv]); A['wave'] = np.asarray(wv)
wt = {}
for l in open('%s/RND_%s_V1_WEIGHTS%s.tsv' % (W, v, sys.argv[3] if len(sys.argv) > 3 else '')).readlines()[1:]:
    c, t, x = l.split('\t'); wt[(c, int(t))] = float(x)
Rn['w'] = np.array([wt.get((c, int(t)), 0.0) for c, t in zip(Rn['coin'], Rn['t'])])
for o in (A, Rn):
    o['m'] = np.array([dt.datetime.utcfromtimestamp(x).strftime('%m') for x in o['t']]); o['d'] = np.array([dt.datetime.utcfromtimestamp(x).strftime('%Y%m%d') for x in o['t']])
def share(o, x, m=None):
    ok = np.isfinite(x) & (m if m is not None else True); return np.sum(o['w'][ok] * x[ok]) / np.sum(o['w'][ok]) if ok.any() and np.sum(o['w'][ok]) > 0 else np.nan
def wq(o, col, qs, m=None):
    x = o[col]; ok = np.isfinite(x) & (m if m is not None else True) & (o['w'] > 0)
    if not ok.any(): return [np.nan] * len(qs)
    vv, w = x[ok], o['w'][ok]; i = np.argsort(vv); vv, w = vv[i], np.cumsum(w[i]); return [vv[min(np.searchsorted(w, q * w[-1]), len(vv) - 1)] for q in qs]
def first(o, D, lab, m=None):
    x = o['%s__%s' % (lab, D)]; return share(o, np.where(np.isfinite(x), (x == 1).astype(float), np.nan), m)
def pct(x): return '%3.0f' % (100 * x) if x == x else ' na'
cost = 'honest (gap 0.032 rt; BTC ~0.13%)' if tag == 'om' else 'STRESS (gap 0.144 rt)'
mcount = {m: (int(np.sum(A['m'] == m)), len(set(A['wave'][A['m'] == m]))) for m in MS}
print('IDEA2 %s | Sep 10-Dec 31 2025 | %d fires, %d waves (%s) | random %d moments | cost %s, median c %.3f%%' % (v, len(A['t']), len(cnt),
      ' '.join('%s %d/%d' % (m, *mcount[m]) for m in MS), len(Rn['t']), cost, np.nanmedian(A['unit__c'])))
print('Each cell: alarm / random (%). FADE = bet against the move (the idea); FOLLOW = with the move (the volatility check).')
print('\n6. WHICH COMES FIRST (break-even: 2c<-1c 67%%, 4c<-2c 50%%) ALL and by month')
for D in DS:
    for nm, lab, be in FIRST:
        print('  %-6s %-10s ALL %s/%s | %s' % (D, nm, pct(first(A, D, lab)), pct(first(Rn, D, lab)), ' '.join('%s %s/%s' % (m, pct(first(A, D, lab, A['m'] == m)), pct(first(Rn, D, lab, Rn['m'] == m))) for m in MS)))
print('\n1-3. REACH the offer in the window | heat before it (c) median/p75/p90 alarm [random median] | minutes to reach median alarm [random]')
for D in DS:
    for h in HS:
        for k in KS:
            r = 'REACH_%dC_%s__%s' % (k, h, D); hb = 'HEATB_%dC_%s__%s' % (k, h, D); tt = r + '__t'
            a = wq(A, hb, [.5, .75, .9]); b = wq(Rn, hb, [.5]); ta = wq(A, tt, [.5]); tb = wq(Rn, tt, [.5])
            print('  %-6s %-4s +%dc: %s/%s | heat %.1f/%.1f/%.1f [%.1f] | %5.1f [%5.1f] min' % (D, h, k, pct(share(A, A[r])), pct(share(Rn, Rn[r])), a[0], a[1], a[2], b[0], ta[0] / 60, tb[0] / 60))
print('\n4. SIZE of the best move, c: p25/median/p75/p90 alarm [random median]')
for D in DS:
    for h in HS:
        a = wq(A, 'BEST_%s__%s' % (h, D), [.25, .5, .75, .9]); b = wq(Rn, 'BEST_%s__%s' % (h, D), [.5])
        print('  %-6s %-4s %.1f / %.1f / %.1f / %.1f [%.1f]' % (D, h, a[0], a[1], a[2], a[3], b[0]))
print('\n5. BEST MOVE PAYS MORE THAN THE COST (above 1c), ALL and by month')
for D in DS:
    for h in HS:
        col = 'BEST_%s__%s' % (h, D); pa = np.where(np.isfinite(A[col]), (A[col] > 1).astype(float), np.nan); pr = np.where(np.isfinite(Rn[col]), (Rn[col] > 1).astype(float), np.nan)
        print('  %-6s %-4s ALL %s/%s | %s' % (D, h, pct(share(A, pa)), pct(share(Rn, pr)), ' '.join('%s %s/%s' % (m, pct(share(A, pa, A['m'] == m)), pct(share(Rn, pr, Rn['m'] == m))) for m in MS)))
# boring checks on the main yardstick P = 2c<-1c 1h
lab = 'OFFER2C_BEFORE_HEAT1C_60M'; top3 = [c for c, _ in collections.Counter(A['coin']).most_common(3)]
print('\nBORING CHECKS on P = 2c<-1c 1h, alarm - random (points): FADE / FOLLOW')
def gap(D, ma, mr): return 100 * (first(A, D, lab, ma) - first(Rn, D, lab, mr))
print('  all: %+.1f / %+.1f' % (gap('FADE', None, None), gap('FOLLOW', None, None)))
ma = ~np.isin(A['coin'], top3); mr = ~np.isin(Rn['coin'], top3); print('  without top-3 coins %s: %+.1f / %+.1f' % (','.join(top3), gap('FADE', ma, mr), gap('FOLLOW', ma, mr)))
ma = ~np.isin(A['d'], ['20251010', '20251011']); mr = ~np.isin(Rn['d'], ['20251010', '20251011']); print('  without 10-11 Oct: %+.1f / %+.1f' % (gap('FADE', ma, mr), gap('FOLLOW', ma, mr)))
print('  by month FADE: %s | FOLLOW: %s' % (' '.join('%s %+.1f' % (m, gap('FADE', A['m'] == m, Rn['m'] == m)) for m in MS), ' '.join('%s %+.1f' % (m, gap('FOLLOW', A['m'] == m, Rn['m'] == m)) for m in MS)))
