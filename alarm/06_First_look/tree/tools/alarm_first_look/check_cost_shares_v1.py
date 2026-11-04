"""check_cost_shares_v1.py (SCOUT 2 Nov 2026; GPT 10:30:53Z: cost_of(1,1,NaN,NaN) returned a known cost): on the real COST cells, over every coin and hour of the days: how many have S06 and S08 valued but S10 or S11 empty, and how many of those a stored BAR moment reads. 0 at the moments = treating them as unknown changes no stored table.
  python3 -B check_cost_shares_v1.py <out.tsv> <lab_days> <lab3 code> <first> <last> <BAR dir>      Exit 0 none at the moments, 3 some."""
import csv, gzip, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bar_v1 as B
csv.field_size_limit(10 ** 7)
out, lab, code, first, last, bdir = sys.argv[1:7]
days = B.day_list(first, last); src = B.LabSource(lab, code, days); t0 = B.day_start(days[0]); want = {}
for fn in sorted(os.listdir(bdir)):
    if fn.startswith('BAR_') and fn.endswith('.tsv.gz'):
        with gzip.open(os.path.join(bdir, fn), 'rt') as f:
            for r in csv.DictReader(f, delimiter='\t'):
                t = int(r['t']); want.setdefault((r['coin'], (t - t0) // 3600), [0, 0]); want[(r['coin'], (t - t0) // 3600)][0 if r['cost_pct'] != '' else 1] += 1
tot = dict(cells=0, both_costs=0, share_empty=0, moments_known_cost=0, cells_at_known_moments=0, share_empty_at_known_moments=0, moments_share_empty=0); rows = []
for k, d in enumerate(days):
    coins = sorted(str(c) for c in src.R.index(d, 'PRICE')['coins'])
    for c, a in src.cost_cells(d, coins).items():
        for h in range(24):
            s06, s08, s10, s11 = a[:, h]; tot['cells'] += 1; w = want.get((c, k * 24 + h))
            if np.isfinite(s06) and np.isfinite(s08):
                tot['both_costs'] += 1; e = not (np.isfinite(s10) and np.isfinite(s11)); tot['share_empty'] += e
                if w and w[0]:
                    tot['cells_at_known_moments'] += 1; tot['moments_known_cost'] += w[0]
                    if e:
                        tot['share_empty_at_known_moments'] += 1; tot['moments_share_empty'] += w[0]; rows.append((d, c, h, s10, s11, w[0]))
with open(out, 'x') as f:
    f.write('\t'.join(tot) + '\n' + '\t'.join(str(v) for v in tot.values()) + '\nday\tcoin\thour\ts10\ts11\tmoments\n')
    for r in rows:
        f.write('\t'.join(str(x) for x in r) + '\n')
print('COST SHARES', tot)
sys.exit(3 if tot['moments_share_empty'] else 0)
