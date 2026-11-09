#!/usr/bin/env python3
"""pool_splits_v1.py (SCOUT 2026-11-08, the owner 08:08Z "yes, let's do the pooling and see if that improves").
Why: 0 of 26 round 2 splits reached t 2.5 alone (drills_v2/R2_POWER_CHECK_20261108.md): each sharpened alarm leaves 50-300 waves a state.
What: for each CTX reading, the gap (highest-reading state minus lowest-reading state, lead at 15 min) from every memory run's state_split
receipt (runs_v2/L*/split*/STATE_SPLIT_*.tsv; one split per run and reading: the one with most waves), pooled by inverse variance:
  gap_pooled = sum(g_i / v_i) / sum(1 / v_i), v_i = se_hi^2 + se_lo^2, se_pooled = sqrt(1 / sum(1 / v_i)), t = gap_pooled / se_pooled;
plus sign agreement, Cochran Q and I^2 (do the runs disagree?), and a dependence-adjusted t: runs share market days, so their gaps are
not independent; t_adj = t / sqrt(1 + (k - 1) * RHO) with RHO = 0.5 (assumed correlation between runs; written down, not fitted).
Reads design-month receipts only (Sep-Jan); arm C (control) runs are never read. Writes one TSV (stdout or --out).
  python3 -B pool_splits_v1.py [--runs runs_v2] [--out FILE] [--rho 0.5] [--horizon 15m]"""
import argparse, collections, csv, glob, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def read_split(path, horizon):
    rows = list(csv.DictReader([l for l in open(path) if not l.startswith('#')], delimiter='\t'))
    s = [r for r in rows if r['horizon'] == horizon and r['state'] not in ('ALL', 'no_reading') and r['status'] == 'OK']  # curator L08: the warm-up row is not a state
    if len(s) < 2: return None
    lo, hi = s[0], s[-1]      # states are ordered by the reading (S1 lowest cut range ... last highest)
    try:
        return dict(gap=float(hi['lead']) - float(lo['lead']), v=float(hi['se']) ** 2 + float(lo['se']) ** 2,
                    waves=int(lo['waves']) + int(hi['waves']), lo=lo['rule'], hi=hi['rule'])
    except (ValueError, KeyError):
        return None

def collect(runs_dir, horizon):
    by = collections.defaultdict(dict)    # reading -> run -> split
    for p in sorted(glob.glob(os.path.join(runs_dir, 'L*', 'split*', 'STATE_SPLIT_*.tsv'))):
        run = os.path.relpath(p, runs_dir).split(os.sep)[0]
        if not re.fullmatch(r'L\d\d', run): continue
        m = re.search(r'CTX\.([A-Za-z0-9_]+)\.tsv$', p)
        if not m: continue
        sp = read_split(p, horizon)
        if sp is None: continue
        sp['file'] = os.path.relpath(p, runs_dir)
        old = by[m.group(1)].get(run)
        if old is None or sp['waves'] > old['waves']: by[m.group(1)][run] = sp
    return by

def pool(splits, rho):
    k = len(splits); w = [1 / s['v'] for s in splits]
    g = sum(s['gap'] * wi for s, wi in zip(splits, w)) / sum(w); se = math.sqrt(1 / sum(w)); t = g / se
    q = sum(wi * (s['gap'] - g) ** 2 for s, wi in zip(splits, w)); i2 = max(0.0, (q - (k - 1)) / q) if q > 0 and k > 1 else 0.0
    same = sum(1 for s in splits if (s['gap'] > 0) == (g > 0))
    return dict(k=k, gap=g, se=se, t=t, t_adj=t / math.sqrt(1 + (k - 1) * rho), same=same, i2=i2)

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--runs', default=os.environ.get('ALARM_RUNS_DIR', os.path.join(os.path.dirname(HERE), 'runs_v2')))
    ap.add_argument('--out'); ap.add_argument('--rho', type=float, default=0.5); ap.add_argument('--horizon', default='15m')
    a = ap.parse_args(argv)
    by = collect(a.runs, a.horizon)
    cols = ['reading', 'horizon', 'runs', 'k', 'pooled_gap_hi_minus_lo', 'pooled_se', 'pooled_t', 't_dependence_adjusted', 'sign_agree', 'I2', 'per_run_gap_t', 'files']
    lines = ['\t'.join(cols)]
    for rd in sorted(by):
        sp = [by[rd][r] for r in sorted(by[rd])]
        p = pool(sp, a.rho)
        per = '; '.join('%s %+.2f (t %+.2f)' % (r, by[rd][r]['gap'], by[rd][r]['gap'] / math.sqrt(by[rd][r]['v'])) for r in sorted(by[rd]))
        lines.append('\t'.join([rd, a.horizon, ','.join(sorted(by[rd])), str(p['k']), '%+.2f' % p['gap'], '%.2f' % p['se'], '%+.2f' % p['t'],
                                '%+.2f' % p['t_adj'], '%d/%d' % (p['same'], p['k']), '%.2f' % p['i2'], per, ','.join(by[rd][r]['file'] for r in sorted(by[rd]))]))
    out = '\n'.join(lines) + '\n'
    if a.out:
        open(a.out, 'w').write(out)
    sys.stdout.write(out)
    return 0

if __name__ == '__main__':
    sys.exit(main())
