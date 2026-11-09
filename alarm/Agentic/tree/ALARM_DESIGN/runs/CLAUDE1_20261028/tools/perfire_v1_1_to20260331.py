# perfire_v1_1_to20260430.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): perfire_v1_to20260430.py 59a865d0127d1482 (CLAUDE1 28 Oct) with
# only its paths changed (CLEAN_RELEASE_V1): F, the lab code it imports (lab3, labcore, event_outcomes), is <Alarm>/01_Detection/tree
# (settings_v1.alarm_root), never the dev tree. Same arguments, same PERFIRE_<V>.tsv.
# perfire_v1_to20260430.py (CLAUDE1_20261028, 28 Oct 2026). TEST, NOT REVIEWED. Runs on the Mac inside a Q_CHAIN job.
# A READER of a finished grade (the alarm grader's stored outcome runs om_<V>_v1 and om_<V>RND_v1, read with the same code as
# alarm_card_v1_2.py: event_outcomes.read, labcore waves 1800 s, random weights from RND_<V>_V1_WEIGHTS.tsv). Its date range is
# HARDCODED: FIRST..LAST below; it refuses any alarm or random row outside it (the owner's tools rule), and its name carries LAST.
# It writes one flat file per variant, PERFIRE_<V>.tsv (refuses an existing file): one row per alarm fire and per random moment:
#   kind (A alarm / R random), coin, t, day, month, hour, side, wave, w (the one-result-per-wave weight, random: its weight),
#   wave_size (fires in the wave), c (the coin round-trip cost), and the races 2c<1c at 5m, 15m, 1h for FADE and FOLLOW (1 win, 0 no, nan).
# Proven on a known result first (L2): in the same job, test_perfire_v1.py checks that the flat file reproduces the card's SUM
# month keys (2c<1c <h> a <m> and r <m>) for the variant to 0.1 point.
#   python3 -B perfire_v1_to20260430.py <W> <V>
import sys, os, collections, datetime as dt, numpy as np
FIRST, LAST = '20250910', '20260331'
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
RACES = [('5m', 'OFFER2C_BEFORE_HEAT1C_5M'), ('15m', 'OFFER2C_BEFORE_HEAT1C_15M'), ('1h', 'OFFER2C_BEFORE_HEAT1C_60M')]
DS = ['FADE', 'FOLLOW']
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
    cols = ['unit__c'] + ['%s__%s' % (lab, D) for _, lab in RACES for D in DS if '%s__%s' % (lab, D) in cat]
    R = EO.read(root, CODE, subj, cols); o = {c: np.asarray(R[c]['value'], float) for c in cols}
    o['coin'] = np.asarray(R[cols[0]]['coin']); o['t'] = (np.asarray(R[cols[0]]['as_of_us']) // 10**6).astype(np.int64)
    for c in cols[1:]:
        assert np.array_equal(np.asarray(R[c]['coin']), o['coin']), 'row order differs in ' + c
    o['d'] = np.array([dt.datetime.utcfromtimestamp(int(x)).strftime('%Y%m%d') for x in o['t']])
    o['side'] = np.array([side_of.get((c, int(t)), 0) for c, t in zip(o['coin'], o['t'])]); o['cols'] = cols; return o
def refuse(o, nm):
    bad = [x for x in o['d'] if not (FIRST <= x <= LAST)]
    if bad:
        raise SystemExit('OUTSIDE_WINDOW %s: %d rows outside %s-%s: refused' % (nm, len(bad), FIRST, LAST))
def main(W, V):
    out = os.path.join(W, 'PERFIRE_%s.tsv' % V)
    if os.path.exists(out): raise SystemExit('EXISTS ' + out)
    A = load('%s/om_%s_v1' % (W, V), 'IDEA2%sMENU' % V, sides('%s/%s_FIRES_V1_LIST.tsv' % (W, V))); refuse(A, 'alarm')
    wv = WV.waves(A['t'].astype(float), 1800); cnt = collections.Counter(wv); A['wave'] = np.asarray(wv); A['w'] = np.array([1.0 / cnt[k] for k in wv])
    A['ws'] = np.array([cnt[k] for k in wv])
    rows = []
    Rn = None
    if os.path.isdir('%s/om_%sRND_v1' % (W, V)):
        Rn = load('%s/om_%sRND_v1' % (W, V), 'IDEA2%sRNDMENU' % V, sides('%s/RND_%s_V1_LIST.tsv' % (W, V))); refuse(Rn, 'random'); wt = {}
        for l in list(open('%s/RND_%s_V1_WEIGHTS.tsv' % (W, V)))[1:]:
            c, t, x = l.rstrip('\n').split('\t'); wt[(c, int(t))] = float(x)
        Rn['w'] = np.array([wt.get((c, int(t)), 0.0) for c, t in zip(Rn['coin'], Rn['t'])]); Rn['wave'] = np.full(len(Rn['t']), -1); Rn['ws'] = np.zeros(len(Rn['t']), int)
    hdr = ['kind', 'coin', 't', 'day', 'month', 'hour', 'side', 'wave', 'w', 'wave_size', 'c'] + ['%s %s' % (D, h) for D in DS for h, _ in RACES]
    with open(out + '.part', 'w') as f:
        f.write('\t'.join(hdr) + '\n')
        for k, o in (('A', A), ('R', Rn)):
            if o is None: continue
            for i in range(len(o['t'])):
                r = [k, o['coin'][i], str(int(o['t'][i])), o['d'][i], o['d'][i][2:6], dt.datetime.utcfromtimestamp(int(o['t'][i])).strftime('%H'), str(int(o['side'][i])),
                     str(int(o['wave'][i])), '%.8g' % o['w'][i], str(int(o['ws'][i])), '%.6g' % o['unit__c'][i]]
                for D in DS:
                    for h, lab in RACES:
                        c = '%s__%s' % (lab, D); x = o[c][i] if c in o else np.nan
                        r.append('nan' if x != x else ('1' if x == 1 else '0'))
                f.write('\t'.join(r) + '\n')
    os.rename(out + '.part', out); print('WROTE', out, len(A['t']), 'alarm rows', 0 if Rn is None else len(Rn['t']), 'random rows')
if __name__ == '__main__':
    if len(sys.argv) != 3: raise SystemExit('USAGE perfire_v1_to20260430.py W V')
    main(sys.argv[1], sys.argv[2])
