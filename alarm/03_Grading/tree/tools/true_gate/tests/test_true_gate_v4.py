#!/usr/bin/env python3
"""tests of true_gate_v4 (SCO-A179: test_true_gate_v3.py on v4, the months lines changed: Jan-Mar 2026 admitted, April refused). TG4_CODE points a mutant copy."""
import importlib.util, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CODE = os.environ.get('TG4_CODE', os.path.join(HERE, '..'))
os.environ['TG_V2'] = os.path.join(HERE, '..', 'true_gate_v2.py')
sp = importlib.util.spec_from_file_location('g3', os.path.join(CODE, 'true_gate_v4.py')); G = importlib.util.module_from_spec(sp); sp.loader.exec_module(G)
TG, G2 = G.TG, G.G2; PASS = []; FAIL = []
def ok(n, c): (PASS if c else FAIL).append(n)
V = G.verdict3
ok('TRUE needs all four', V(.06, .01, .1, .06, .01, .1, .9) == 'TRUE')
ok('gap at bar', V(.05, .01, .1, .05, .01, .1, .9) == 'TRUE')
ok('difference under the bar: not TRUE', V(.06, .01, .1, .04, .01, .1, .9) == 'UNSURE')
ok('difference interval touches 0: not TRUE', V(.06, .01, .1, .06, 0.0, .1, .9) == 'UNSURE')
ok('gap under the bar: not TRUE', V(.04, .01, .1, .06, .01, .1, .9) == 'UNSURE')
ok('gap interval touches 0: not TRUE', V(.06, 0.0, .1, .06, .01, .1, .9) == 'UNSURE')
ok('the bias case: gap TRUE, difference precise and negative', V(.07, .04, .1, -.2, -.25, -.15, .9) == 'NOT SUPPORTED')
ok('gap top under .05', V(.01, -.01, .04, .2, .1, .3, .9) == 'NOT SUPPORTED')
ok('top exactly .05 is not under', V(.01, -.01, .05, .01, -.01, .05, .9) == 'UNSURE')
ok('coverage just under a half: UNSURE even when all else is TRUE', V(.2, .1, .3, .2, .1, .3, .499) == 'UNSURE')
ok('coverage under a half: UNSURE even when precise and small', V(.0, -.01, .01, 0, -.01, .01, .3) == 'UNSURE')
ok('coverage exactly a half counts', V(.2, .1, .3, .2, .1, .3, .5) == 'TRUE')
ok('a NaN: UNSURE', V(.2, .1, .3, float('nan'), .1, .3, .9) == 'UNSURE')
# ---- percentile: known before the day
DAY = '20251104'; D0 = TG.day0(DAY)
class Fake:
    def __init__(self, f): self.f = f
class H(G.History):
    def __init__(self, vals): self.d = {}; self.vals = vals
    def day(self, day): return self.vals.get(day, {})
vals = {AD_d: {'AAA': np.arange(10.0)} for AD_d in [G.AD.shift(DAY, -k) for k in range(1, 9)]}; vals[DAY] = {'AAA': np.full(24, 1e9)}
h = H(vals)
ok('mid-rank by hand: x=4.5 among 8 x 0..9: half', h.pct('AAA', D0 + 60, 4.5) == 0.5)
ok('ties take half: x=4: 32 under, 8 equal of 80', h.pct('AAA', D0 + 60, 4.0) == (32 + 4) / 80)
vals2 = {G.AD.shift(DAY, -k): {'AAA': np.arange(10.0)} for k in (1, 14, 15, 16, 17, 18, 19, 20, 21)}
ok('only 14 days back: 20 samples under 72, NaN', math.isnan(H(vals2).pct('AAA', D0, 4.5)))
vals3 = {G.AD.shift(DAY, -k): {'AAA': np.arange(10.0)} for k in range(1, 15)}; vals3[G.AD.shift(DAY, -15)] = {'AAA': np.full(10, -5.0)}
ok('day 15 back is left out', H(vals3).pct('AAA', D0, 4.5) == 0.5)
ok('the day itself is left out', h.pct('AAA', D0 + 60, 1e8) == 1.0)
ok('NaN value: NaN', math.isnan(h.pct('AAA', D0, float('nan'))))
ok('another coin: NaN', math.isnan(h.pct('BBB', D0, 1.0)))
# ---- a world by hand: every moment in the same band. Pool: half top group, half low.
def world(hit_c, hit_m, nw=60, r_top=(.3, .3), r_low=(.1, .1), top=True):
    t0 = TG.day0('20251104'); nA = 2 * nw; At = np.array([t0 + w * 3600 + k * 60 for w in range(nw) for k in range(2)], np.int64)
    A = {'coin': np.array(['AAA', 'BBB'] * nw, object), 't': At, 'side': -np.ones(nA), 'w': np.ones(nA), 'c': np.full(nA, .2)}
    nr = 2000; R = {'coin': np.array(['C%d' % (i % 500) for i in range(nr)], object), 't': (t0 + 1801 + 7 * np.arange(nr)).astype(np.int64), 'side': -np.ones(nr), 'w': np.ones(nr), 'c': np.full(nr, .2)}
    sR = np.r_[np.full(1000, .2), np.full(1000, .99)]; sA = np.full(nA, .99 if top else .2)
    def fill(a, b):
        x = np.zeros(nr); x[:int(a * 1000)] = 1; x[1000:1000 + int(b * 1000)] = 1; return x
    hR = fill(r_low[0], r_top[0]); mR = fill(r_low[1], r_top[1])
    one = lambda n: {k: np.ones(n) for k in ('normal_move_pct', 'range60_pct', 'move15_pct')}
    def fh(x):
        h = np.zeros(nA); h[:int(round(x * nA))] = 1; return h
    return A, R, fh(hit_c), hR, fh(hit_m), mR, {'A': one(nA), 'R': one(nr)}, sA, sR
A, R, hA, hR, mA, mR, bz, sA, sR = world(.8, .3)
g = G.gate(A, R, hA, hR, mA, mR, bz, sA, sR, 'FADE', ['2511'])
ok('strata price the top group: .8 - .3 = +.5', abs(g['s']['gap'] - .5) < 1e-9)
ok('difference .5 - 0 = +.5', abs(g['d']['gap'] - .5) < 1e-9 and abs(g['d']['mirror_gap']) < 1e-9)
ok('word TRUE; coverage 1', g['word'] == 'TRUE' and g['cover'] == 1.0)
ok('coverage rows: the top group holds the 120 fires', g['cov'][-1] == (3, 120, 120, 0))
A, R, hA, hR, mA, mR, bz, sA, sR = world(.5, .5)
g = G.gate(A, R, hA, hR, mA, mR, bz, sA, sR, 'FADE', ['2511'])
ok('both directions up on the same fires: gap +.2, difference 0, NOT SUPPORTED', abs(g['s']['gap'] - .2) < 1e-9 and abs(g['d']['gap']) < 1e-9 and g['word'] == 'NOT SUPPORTED')
A, R, hA, hR, mA, mR, bz, sA, sR = world(1.0, 0.0)
sB = sA.copy(); sB[:80] = np.nan
g = G.gate(A, R, hA, hR, mA, mR, bz, sB, sR, 'FADE', ['2511'])
ok('a fire with no percentile counts against coverage: 40 of 120, UNSURE', abs(g['cover'] - 40 / 120) < 1e-9 and g['word'] == 'UNSURE')
hM = mA.copy(); hM[:60] = np.nan
g = G.gate(A, R, hA, hR, hM, mR, bz, sA, sR, 'FADE', ['2511'])
ok('the difference reads only fires known on both', g['d']['fires'] == 60)
A5, R5, h5, hR5, m5, mR5, bz5, s5, sR5 = world(.5, 0.0); m5 = m5.copy(); m5[:60] = np.nan
g = G.gate(A5, R5, h5, hR5, m5, mR5, bz5, s5, sR5, 'FADE', ['2511'])
ok('the claim gap beside the difference is on the same fires: the 60 with a mirror, all misses, 0 - .3', abs(g['d']['claim_gap'] + .3) < 1e-9)
# a fire in a thin two-value cell falls to the normal band
bz2 = {'A': {k: v.copy() for k, v in bz['A'].items()}, 'R': {k: v.copy() for k, v in bz['R'].items()}}
bz2['A']['range60_pct'][:] = 1.0; bz2['R']['range60_pct'] = np.r_[np.ones(1000), np.ones(1000)]; bz2['R']['range60_pct'][1000:1015] = 2.0; bz2['R']['range60_pct'][1000:1005] = 50.0; bz2['A']['range60_pct'][0] = 50.0
g = G.gate(A, R, hA, hR, mA, mR, bz2, sA, sR, 'FADE', ['2511'])
ok('thin cell: priced on the normal band, counted coarse', g['cov'][-1][3] >= 1 and g['cover'] == 1.0)
# ---- flow removed, by hand
class P:
    def __init__(self): self.d = {}
    def put(self, code, vals):
        n = 17280; self.d[code] = {'coins': {'AAA': 0}, 'step': 5, 'v': np.full((1, n), np.nan), 'a': np.zeros((1, n), np.int32), 'e': np.zeros((1, n), np.uint8), 'k': None}
        for o, v in vals.items(): self.d[code]['v'][0, o // 5] = v
    def native(self, code, day): return self.d.get(code)
p = P(); O = 36000
p.put(G.FLOW_L, {O - 60 * i: 10.0 for i in range(10)}); p.put(G.FLOW_S, {O - 60 * i: 1.0 for i in range(10)})
r = G.flow_removed(p, {'end_s': 600}, np.array(['AAA']), np.array([D0 + O]), np.array([-2.0]))
ok('flow added back: -2 pct + (100 + 10) bp = -0.9 pct', abs(r[0] + 0.9) < 1e-9)
p.d[G.FLOW_L]['v'][0, O // 5] = np.nan
ok('a missing step: NaN', math.isnan(G.flow_removed(p, {'end_s': 600}, np.array(['AAA']), np.array([D0 + O]), np.array([-2.0]))[0]))
# ---- the release's admission (GPT's must-fix, REVIEW_ALARM_V1_20_TRUE_GATE_GPT.md)
import json, tempfile
TMPD = tempfile.mkdtemp(); DEF = os.path.join(TMPD, 'V1.json'); json.dump({'inputs': {'a': {'op': 'raw', 'code': 'A1.S08'}}, 'conditions': [], 'fire': {}}, open(DEF, 'w'))
DEF2 = os.path.join(TMPD, 'V2.json'); json.dump({'inputs': {'a': {'op': 'raw', 'code': 'E2.S04'}}}, open(DEF2, 'w'))
FAM_LAB = {'kind': 'metric_test', 'code': 'E2.S04', 'when': 'present', 'end_s': 600, 'test': '<=', 'agg': 'last', 'thr': -0.5, 'max_age_s': 120}
CL = {'id': 'X', 'idea': 'I', 'V': 'V1', 'def': DEF, 'def_sha16': TG.sha16(DEF), 'label': FAM_LAB, 'mirror': dict(FAM_LAB, test='>=', thr=0.5), 'activity': {'code': 'E2.S04', 'mode': 'change', 'max_age_s': 120}, 'perfire': '/x/PERFIRE_V1.tsv', 'perfire_sha16': 'x', 'first': '20250910', 'last': '20251231', 'lab_days': 'l'}
def adm(drop=(), **k):
    c = dict(CL, **k)
    for d in drop:
        c.pop(d)
    try:
        G.admit(c); return 'OK'
    except TG.Refused as e:
        return e.code
ok('admit: a good claim', adm() == 'OK')
for f in ('def', 'def_sha16', 'idea', 'V', 'mirror', 'perfire_sha16'):
    ok('admit: no %s refused' % f, adm(drop=(f,)) == 'BAD_CLAIM')
ok('admit: a definition of other bytes refused', adm(def_sha16='0' * 16) == 'DEF_CHANGED')
ok('admit: a substituted definition reading E2.S04, its own digest: circular', adm(**{'def': DEF2, 'def_sha16': TG.sha16(DEF2)}) == 'SAME_CODE')
ok('admit: a missing definition refused', adm(**{'def': DEF + '.no'}) == 'DEF_CHANGED')
ok('admit: the PERFIRE of another variant refused', adm(perfire='/x/PERFIRE_V2.tsv') == 'BAD_CLAIM')
ok('admit: Jan 2026 admitted (Sep-Mar)', adm(last='20260101') == 'OK')
ok('admit: the last day 20260331 admitted', adm(last='20260331') == 'OK')
ok('admit: April 2026 refused (out of sample)', adm(last='20260401') == 'MONTHS')
ok('admit: August 2026 refused (never seen)', adm(last='20260801') == 'MONTHS')
ok('admit: August refused', adm(first='20250801') == 'MONTHS')
ok('admit: the first day allowed', adm(first='20250910', last='20250910') == 'OK')
ok('admit: not a date refused', adm(last='20251301') == 'MONTHS')
ok('admit: a date inside the window that is no date refused', adm(last='20251131') == 'MONTHS')
ok('admit: activity on another code refused', adm(activity={'code': 'E2.S02', 'mode': 'level', 'max_age_s': 120}) == 'BAD_CLAIM')
ok('admit: same test with opposite thresholds refused', adm(mirror=dict(FAM_LAB, thr=0.5)) == 'BAD_MIRROR')
ok('admit: first after last refused', adm(first='20251231', last='20251230') == 'MONTHS')
ok('admit: a future 86,400 s mirror with threshold 99 refused', adm(mirror=dict(FAM_LAB, test='>=', thr=99, when='window', end_s=86400)) == 'BAD_MIRROR')
ok('admit: mirror threshold not opposite refused', adm(mirror=dict(FAM_LAB, test='>=', thr=99)) == 'BAD_MIRROR')
for f, v in (('end_s', 300), ('when', 'window'), ('agg', 'max'), ('max_age_s', 60), ('sign', 'same'), ('code', 'E2.S02')):
    ok('admit: mirror %s differing refused' % f, adm(mirror=dict(FAM_LAB, test='>=', thr=0.5, **{f: v})) == 'BAD_MIRROR')
ok('admit: a mirror the same way refused', adm(mirror=FAM_LAB) == 'BAD_MIRROR')
ok('admit: thresholds mixed with falling refused', adm(label=dict(FAM_LAB, test='falling', change='pct', agg=None, thr=None), mirror=dict(FAM_LAB, test='>=', thr=0.5, change='pct', agg=None)) == 'BAD_MIRROR')
F1 = dict(FAM_LAB, code='E2.S02', test='falling', change='pct'); F1.pop('thr'); F1.pop('agg')
ok('admit: falling with rising passes', adm(label=F1, mirror=dict(F1, test='rising'), activity={'code': 'E2.S02', 'mode': 'level', 'max_age_s': 120}) == 'OK')
ok('admit: falling with rising at another threshold refused', adm(label=F1, mirror=dict(F1, test='rising', thr=1.0), activity={'code': 'E2.S02', 'mode': 'level', 'max_age_s': 120}) == 'BAD_MIRROR')
T1 = dict(FAM_LAB, thr=None, thr_code={'code': 'E1.S01', 'scale': 1.0}); T2 = dict(FAM_LAB, test='>=', thr=None, thr_code={'code': 'E1.S01', 'scale': -1.0})
ok('admit: threshold codes opposite pass', adm(label=T1, mirror=T2) == 'OK')
ok('admit: threshold codes the same way refused', adm(label=T1, mirror=dict(T2, thr_code={'code': 'E1.S01', 'scale': 1.0})) == 'BAD_MIRROR')
m2 = dict(FAM_LAB, test='>=', thr=None, thr_code={'code': 'A1.S08'})
ok('admit: a one-sided threshold code refused', adm(mirror=m2) == 'BAD_MIRROR')
# coverage on the paired fires: GPT's witness
A, R, hA, hR, mA, mR, bz, sA, sR = world(1.0, 0.0); mB = mA.copy(); mB[12:] = np.nan
g = G.gate(A, R, hA, hR, mB, mR, bz, sA, sR, 'FADE', ['2511'])
ok('12 of 120 paired: UNSURE, coverage .1, counts printed', g['word'] == 'UNSURE' and abs(g['cover'] - .1) < 1e-9 and g['pair'] == {'claim_known': 120, 'mirror_known': 12, 'joint_known': 12, 'matched_both': 12, 'paired_waves': 6})
g = G.gate(A, R, hA, hR, mA, mR, bz, sA, sR, 'FADE', ['2511'])
ok('fully paired: keeps its word', g['word'] == 'TRUE' and g['cover'] == 1.0)
mC = mA.copy(); mC[60:] = np.nan
g = G.gate(A, R, hA, hR, mC, mR, bz, sA, sR, 'FADE', ['2511'])
ok('half paired counts', g['cover'] == .5)
print('PASS %d FAIL %d' % (len(PASS), len(FAIL)))
for n in FAIL: print('FAIL', n)
sys.exit(1 if FAIL else 0)
