# make_random_v3_1.py (SCOUT 30 Oct 2026, K4, home team/RESEARCH/tools/alarm_process: the grade chains' own copy; TEST, NOT REVIEWED):
# LEAD loop2 make_random_v3.py d5881d3b95e4dff3 with only its path changed (CLEAN_RELEASE_V1): labcore comes from
# <Alarm>/01_Detection/tree/team/RESEARCH/tools (settings_v1.alarm_root), never the dev tree. Same arguments, same outputs.
# random moments for Outcomes from a grading run's matched EDGES: one row per (coin, whole second, side); weight = edge weight (1/n of its
# parent) x 1/(size of the parent's wave, 30 min gap any coin), so random counts once per wave like the alarm
import sys, collections, os
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
sys.path.insert(0, os.path.join(_lab_tree(), 'team', 'RESEARCH', 'tools'))   # K4: was the dev tree's absolute path
import numpy as np
from labcore import waves as WV
run, fires, out = sys.argv[1:4]
F = [l.rstrip('\n').split('\t') for l in open(fires)][1:]
t = np.array([float(x[1]) for x in F]); wv = WV.waves(t, 1800); cnt = collections.Counter(wv)
pw = {'%s_%d' % (x[0], int(x[1])): 1.0 / cnt[k] for x, k in zip(F, wv)}
KMAX = int(sys.argv[4]) if len(sys.argv) > 4 else 0      # 0 = every matched moment; k = the first k draws of each parent (weight 1/k)
E = collections.defaultdict(list)
for l in list(open(run + '/matches/EDGES.tsv'))[1:]:
    fid, coin, pt, ct, side, w, di, own = l.rstrip('\n').split('\t')[:8]
    if own: continue                                   # a moment flagged own (another alarm of the coin before 30 min or within the horizon) is not eligible
    E[fid].append((int(di), coin, int(float(ct)), int(side), float(w)))
W = collections.defaultdict(float)
for fid, rows in E.items():
    rows = sorted(rows)[:KMAX] if KMAX else rows; tot = sum(r[4] for r in rows)
    for di, coin, ct, side, w in rows:
        W[(coin, ct, side)] += (w / tot) * pw.get(fid, 0.0)
# Outcomes refuses two rows with the same (coin, second): a moment drawn for parents of both sides moves the later side by +1 s
seen = set(); W2 = {}
for (c, tt, s_), w in sorted(W.items()):
    while (c, tt) in seen: tt += 1
    seen.add((c, tt)); W2[(c, tt, s_)] = w
W = W2
with open(out + '_LIST.tsv', 'w') as a, open(out + '_WEIGHTS.tsv', 'w') as b:
    a.write('coin\tt\tside\n'); b.write('coin\tt\tweight\n')
    for (c, tt, s), w in sorted(W.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        a.write('%s\t%d\t%d\n' % (c, tt, s)); b.write('%s\t%d\t%.6f\n' % (c, tt, w))
print(out, len(W), 'random moments; parents with a wave weight', len(pw))
