# test_perfire_v1.py (CLAUDE1_20261028): proves PERFIRE_<V>.tsv on a KNOWN result (L2): its per-month alarm and random races at 5m, 15m,
# 1h on the card's lean equal the card's SUM keys (2c<1c <h> a <m>, r <m>) to 0.1 point. TEST, NOT REVIEWED.
#   python3 -B test_perfire_v1.py <W> <V> <LEAN>
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import split_v1 as S
W, V, L = sys.argv[1:4]
k = dict(l.rstrip('\n').split('\t')[:2] for l in open(os.path.join(W, 'SUM_%s.tsv' % V)) if '\t' in l)
h, rows = S.read(os.path.join(W, 'PERFIRE_%s.tsv' % V)); ok = bad = 0; msg = []
for hz in ('5m', '15m', '1h'):
    for m, nw, nf, la, lr, gp, og in S.split(h, rows, L, hz, 'month'):
        for x, key in ((la, '2c<1c %s a %s' % (hz, m)), (lr, '2c<1c %s r %s' % (hz, m))):
            if key not in k or k[key] in ('', 'na', 'nan'): continue
            if abs(100 * x - float(k[key])) <= 0.1: ok += 1
            else: bad += 1; msg.append('%s: perfire %.2f card %s' % (key, 100 * x, k[key]))
print('PERFIRE TEST %s: PASS %d FAIL %d' % (V, ok, bad)); [print(' ', x) for x in msg]
sys.exit(1 if bad or not ok else 0)
