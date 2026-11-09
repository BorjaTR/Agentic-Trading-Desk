#!/usr/bin/env python3
"""combine_readings_v1.py (SCOUT 2026-11-08; drill H05: both agents asked for a two-reading split; the owner 3 Nov: never test one reading alone).
Adds ONE combined reading to a copy of a card's READINGS file, for state_split --readings:
  CTX.combo_<A>__<B> = z(A) + sign * z(B) over the FIRE rows (z = (x - median) / MAD-based scale, robust), known_at = the later of the two.
Two readings become one score, split into halves at its wave first-fire median by state_split (--cuts), so every wave stays in the test
(a 2 x 2 grid would quarter the waves and lose power). sign (+1 or -1) is the hunter's stated hypothesis, written BEFORE the split.
Writes a new file (never edits the card's READINGS). Rows missing either reading get no combined value (state_split: no_reading).
  python3 -B combine_readings_v1.py <READINGS.tsv> <out.tsv> --a CTX.basis_push_bp --b CTX.oi_chg_10m --sign 1"""
import argparse, statistics, sys

def robust_z(vals):
    m = statistics.median(vals); mad = statistics.median(abs(v - m) for v in vals) or 1e-12
    return m, 1.4826 * mad

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--a', required=True); ap.add_argument('--b', required=True); ap.add_argument('--sign', type=int, choices=(1, -1), required=True)
    a = ap.parse_args(argv)
    A, B = {}, {}
    for line in open(a.src):
        if line.startswith('#') or line.startswith('who\t'): continue
        p = line.rstrip('\n').split('\t')
        if len(p) < 6 or p[0] != 'FIRE' or p[3] not in (a.a, a.b): continue
        try: v = float(p[4]); k = float(p[5])
        except ValueError: continue
        (A if p[3] == a.a else B)[(p[1], p[2])] = (v, k)
    keys = sorted(set(A) & set(B))
    if len(keys) < 100: sys.exit('REFUSED TOO_FEW_BOTH: %d fires have both readings' % len(keys))
    ma, sa = robust_z([A[k][0] for k in keys]); mb, sb = robust_z([B[k][0] for k in keys])
    code = 'CTX.combo_%s__%s%s' % (a.a.split('.', 1)[1], a.b.split('.', 1)[1], '' if a.sign == 1 else '_neg')
    with open(a.dst, 'w') as out:
        for line in open(a.src): out.write(line)
        for k in keys:
            z = (A[k][0] - ma) / sa + a.sign * (B[k][0] - mb) / sb
            out.write('FIRE\t%s\t%s\t%s\t%.6f\t%.1f\n' % (k[0], k[1], code, z, max(A[k][1], B[k][1])))
    vals = sorted((A[k][0] - ma) / sa + a.sign * (B[k][0] - mb) / sb for k in keys)
    print('WROTE %s code %s fires %d (A only %d, B only %d) fire median %.4f' % (a.dst, code, len(keys), len(set(A) - set(B)), len(set(B) - set(A)), vals[len(vals) // 2]))
    return 0

if __name__ == '__main__':
    sys.exit(main())
