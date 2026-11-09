#!/usr/bin/env python3
"""check_run1_v1.py (SCO-A150, 6 Nov 2026): the tool's FDAOI, FDAOIV, FDONLY numbers beside run 1's hand numbers
(STAGE1_LAYOUT_RECEIPT.md 4c1b5a60491e30bb: events FDAOI 689 / 710, FDAOIV 382 / 400, FDONLY 1,024 Sep-Dec; overlap FDAOIV->FDAOI
0.987, FDAOI->FDONLY 0.997; TRUE card OI closing 66.0 vs 50.5 pct matched). Reads the final config of a mech_cards_run; writes CHECK_RUN1.md.
  python3 -B check_run1_v1.py <CONFIG_FINAL_FORCED_OUT.tsv> <out md>"""
import sys
sys.dont_write_bytecode = True
import csv, importlib.util, os
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
sp = importlib.util.spec_from_file_location('ac_chk', os.path.join(HERE, 'alarm_cards_v1.py')); AC = importlib.util.module_from_spec(sp); sp.loader.exec_module(AC)
HAND = {('PG_FDAOI', 'SEPDEC'): 689, ('PG_FDAOI', 'JANMAR'): 710, ('PG_FDAOIV', 'SEPDEC'): 382, ('PG_FDONLY', 'SEPDEC'): 1024}
cfg, out = sys.argv[1], sys.argv[2]
R = AC.release(); law = R.LAW.research_refusal
A = {}
for c in csv.DictReader(open(cfg), delimiter='\t'):
    A[(c['alarm'], c['block'])] = AC.load_alarm(c, R.RU, law)
L = ['# CHECK_RUN1: alarm_cards numbers beside run 1 hand numbers (STAGE1_LAYOUT_RECEIPT.md 4c1b5a60491e30bb)', '',
     '| item | tool | run 1 | same |', '|---|---|---|---|']
for k, h in HAND.items():
    if k in A:
        n = len(A[k]['events']); L.append('| events %s %s | %d (fires %d) | %d | %s |' % (k[0], k[1], n, len(A[k]['F']), h, 'yes' if n == h else 'NO'))
    else:
        L.append('| events %s %s | not run | %d | UNKNOWN |' % (k[0], k[1], h))
for x, y, h in (('PG_FDAOIV', 'PG_FDAOI', 0.987), ('PG_FDAOI', 'PG_FDONLY', 0.997), ('PG_FDONLY', 'PG_FDAOI', 0.641)):
    if (x, 'SEPDEC') in A and (y, 'SEPDEC') in A:
        v = AC.overlap(A[(x, 'SEPDEC')], A[(y, 'SEPDEC')])
        L.append('| %s events touching %s (Sep-Dec) | %.3f | %.3f | %s |' % (x, y, v, h, 'yes' if abs(v - h) < 0.0005 else 'NO'))
k = ('PG_FDAOI', 'SEPDEC')
if k in A and A[k]['fire_r'].get('oi_chg_10m'):
    F = A[k]['F']; W = np.array([f['w'] for f in F]); fr = A[k]['fire_r']['oi_chg_10m']
    v = np.array([fr.get((f['coin'], f['t']), np.nan) for f in F]); ok = np.isfinite(v)
    fs = float(((v[ok] < 0) * W[ok]).sum() / W[ok].sum()); ms = [m[1] for m in A[k]['match_r'].get('oi_chg_10m', {}).values() if np.isfinite(m[1])]
    L.append('| FDAOI Sep-Dec open interest closing (oi_chg_10m < 0, Binance, event-weighted) | %.1f pct of fires vs %.1f pct matched | 66.0 vs 50.5 (TRUE card) | %s |'
             % (100 * fs, 100 * np.mean(np.array(ms) < 0) if ms else float('nan'), 'see note'))
L += ['', 'Notes on differences (written by the job from the rows above; why per row is in the README):']
open(out, 'w').write('\n'.join(L) + '\n'); print('\n'.join(L))
