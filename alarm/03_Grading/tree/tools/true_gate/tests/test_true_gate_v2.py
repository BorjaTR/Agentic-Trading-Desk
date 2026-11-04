#!/usr/bin/env python3
"""tests of true_gate_v2, answers by hand, no lab data. TG2_CODE points a mutant copy."""
import importlib.util, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CODE = os.environ.get('TG2_CODE', os.path.join(HERE, '..'))
os.environ.setdefault('TG_V1', os.path.join(HERE, '..', 'true_gate_v1.py'))
sp = importlib.util.spec_from_file_location('g2', os.path.join(CODE, 'true_gate_v2.py')); G = importlib.util.module_from_spec(sp); sp.loader.exec_module(G)
TG = G.TG; PASS = []; FAIL = []
def ok(n, c): (PASS if c else FAIL).append(n)
DAY = '20251104'; D = TG.day0(DAY); OFF = 36000; T = D + OFF
class P:
    def __init__(self): self.d = {}
    def put(self, code, step, coin, vals, age=None):
        if (code, DAY) not in self.d:
            n = 86400 // step
            self.d[(code, DAY)] = {'coins': {'AAA': 0}, 'step': step, 'v': np.full((1, n), np.nan), 'a': np.full((1, n), -2147483648, np.int32), 'e': np.zeros((1, n), np.uint8), 'k': None}
        x = self.d[(code, DAY)]
        for o, v in vals.items():
            x['v'][0, o // step] = v; x['a'][0, o // step] = (age or {}).get(o, 0)
    def native(self, code, day): return self.d.get((code, str(day)))
LAB = {'when': 'present', 'end_s': 600}; LV = {'code': 'E2.S02', 'mode': 'level', 'max_age_s': 120}; CH = {'code': 'E2.S04', 'mode': 'change', 'max_age_s': 120}
# levels at anchor t-600 going back: 100, 110, 110, 99, 99, 99, 99: changes |100-110|/110 ...
p = P(); lv = [100, 110, 110, 99, 99, 99, 99]
p.put('E2.S02', 60, 'AAA', {OFF - 600 - 600 * i: float(x) for i, x in enumerate(lv)})
exp = (abs(100 - 110) / 110 * 100 + 0 + abs(110 - 99) / 99 * 100 + 0 + 0 + 0) / 6
ok('level activity by hand', abs(G.activity(p, LAB, 'AAA', T, LV) - exp) < 1e-9)
p2 = P(); p2.d = {k: {**v, 'v': v['v'].copy(), 'a': v['a'].copy()} for k, v in p.d.items()}
p2.put('E2.S02', 60, 'AAA', {OFF - 300: 1e9, OFF: 1e9, OFF + 600: 1e9})
ok('activity reads nothing inside the label window or after t', G.activity(p2, LAB, 'AAA', T, LV) == G.activity(p, LAB, 'AAA', T, LV))
pc = P(); pc.put('E2.S04', 60, 'AAA', {OFF - 600 * (i + 1): float(x) for i, x in enumerate([-1, 2, -3, 4, -5, 6])}); pc.put('E2.S04', 60, 'AAA', {OFF: 99.0})
ok('change activity: mean |x|, the column at t left out', G.activity(pc, LAB, 'AAA', T, CH) == 3.5)
pw = P(); pw.put('E2.S04', 60, 'AAA', {OFF - 600 * i: 2.0 for i in range(6)}); pw.put('E2.S04', 60, 'AAA', {OFF + 60: 99.0})
ok('window label: activity ends at t', G.activity(pw, {'when': 'window', 'end_s': 60}, 'AAA', T, CH) == 2.0)
ps = P(); ps.put('E2.S04', 60, 'AAA', {OFF - 600 * (i + 1): 1.0 for i in range(3)})
ok('under 4 known steps: NaN', math.isnan(G.activity(ps, LAB, 'AAA', T, CH)))
ps.put('E2.S04', 60, 'AAA', {OFF - 2400: 5.0})
ok('4 known steps are enough', G.activity(ps, LAB, 'AAA', T, CH) == 2.0)
pa = P(); pa.put('E2.S04', 60, 'AAA', {OFF - 600 * (i + 1): 1.0 for i in range(6)}, age={OFF - 600 * (i + 1): 900 for i in range(6)})
ok('stale steps are not known', math.isnan(G.activity(pa, LAB, 'AAA', T, CH)))
pf = P(); pf.put('X1.LIQX.S03', 5, 'AAA', {OFF - 60 * i: 1.0 for i in range(15)}); pf.put('X1.LIQX.S03', 5, 'AAA', {OFF + 60: 500.0, OFF - 900: 500.0})
ok('flow: 15 steps ending at t', G.flow_sum(pf, 'AAA', T) == 15.0)
pg = P(); pg.put('X1.LIQX.S03', 5, 'AAA', {OFF - 60 * i: 1.0 for i in range(14)})
ok('flow with a hole: NaN, not a smaller sum', math.isnan(G.flow_sum(pg, 'AAA', T)))
ok('groups: at a cut is the lower group', list(G.group_of(np.array([0.0, 1.0, 1.5, 2.0, 3.0, np.nan]), np.array([1.0, 2.0]))) == [0, 0, 1, 1, 2, -1])
# ---- a confounded world by hand: quiet moments hit .1, active .5, whoever they are. Fires all active, hit .5: V1's match sees a gap, V2 none.
def world(fire_hit=0.5, nw=60):
    t0 = TG.day0('20251104'); nA = 2 * nw; At = np.array([t0 + w * 3600 + k * 60 for w in range(nw) for k in range(2)], np.int64)
    A = {'coin': np.array(['AAA', 'BBB'] * nw, object), 't': At, 'side': -np.ones(nA), 'w': np.ones(nA), 'c': np.full(nA, 0.2)}
    nr = 2000; Rt = t0 + 1801 + 7 * np.arange(nr).astype(np.int64)
    R = {'coin': np.array(['CCC'] * nr, object), 't': Rt, 'side': -np.ones(nr), 'w': np.ones(nr), 'c': np.full(nr, 0.2)}
    sR = np.r_[np.zeros(1000) + 1, np.zeros(1000) + 10]; hR = np.zeros(nr); hR[:100] = 1; hR[1000:1500] = 1      # quiet .1 (100 of 1000), active .5 (500 of 1000)
    sA = np.full(nA, 10.0); hA = np.tile([1.0, 0.0], nw) if fire_hit == 0.5 else np.ones(nA)
    one = lambda n: {k: np.ones(n) for k in ('normal_move_pct', 'range60_pct', 'move15_pct')}
    return A, R, hA, hR, {'A': one(nA), 'R': one(nr)}, sA, sR
A, R, hA, hR, bz, sA, sR = world()
g = G.gate(A, R, hA, hR, bz, sA, sR, 'FADE', ['2511'])
ok('busy only sees the confound: .5 - .3 = +.2', abs(g['busy']['gap'] - 0.2) < 1e-9)
ok('activity match takes it out: .5 - .5 = 0', abs(g['strat']['gap']) < 1e-9)
ok('all fires matched', g['strat']['fires'] == 120 and g['strat']['waves'] == 60)
A, R, hA, hR, bz, sA, sR = world(1.0)
g = G.gate(A, R, hA, hR, bz, sA, sR, 'FADE', ['2511'])
ok('a real effect survives: 1 - .5', abs(g['strat']['gap'] - 0.5) < 1e-9 and G.word(g['strat']) == 'TRUE')
sB = sA.copy(); sB[:2] = np.nan
g = G.gate(A, R, hA, hR, bz, sB, sR, 'FADE', ['2511'])
ok('a fire with its second value not known leaves, never joins a group', g['strat']['fires'] == 118)
key = 'OBH4_60M__FADE'; L = g['L']
ok('the shim holds the label again after the groups', np.array_equal(L.A[key], hA, equal_nan=True) and np.array_equal(L.R[key], hR, equal_nan=True))
# ---- draws
A, R, hA, hR, bz, sA, sR = world(); rng = np.random.default_rng(1)
ix = G.draw(R, 500, 'rows', rng); ok('rows: n distinct', len(ix) == 500 and len(set(ix.tolist())) == 500)
R2 = dict(R); R2['w'] = np.r_[np.zeros(1000), np.ones(1000)]
ix = G.draw(R2, 200, 'rows', np.random.default_rng(1)); ok('rows follow the weights', ix.min() >= 1000)
Rw = dict(R); t0 = TG.day0('20251104'); Rw['t'] = np.r_[t0 + np.arange(1000), t0 + 86400 + np.arange(1000)].astype(np.int64)
ix = G.draw(Rw, 10, 'waves', np.random.default_rng(1)); ok('waves: whole waves', len(ix) == 1000)
ix = G.draw(Rw, 1001, 'waves', np.random.default_rng(1)); ok('waves: until n is reached', len(ix) == 2000)
Rf = dict(R); Rf['coin'] = np.array(['C%d' % (i % 500) for i in range(2000)], object); Rf['t'] = (TG.day0('20251102') + 1000 * np.arange(2000)).astype(np.int64)
hF = np.random.default_rng(5).integers(0, 2, 2000).astype(float); sF = np.random.default_rng(6).random(2000)
rows = G.fp_sets(Rf, hF, sF, bz['R'], 500, 4, 'rows', 'FADE', ['2511'])
rows2 = G.fp_sets(Rf, hF, sF, bz['R'], 500, 4, 'rows', 'FADE', ['2511'])
ok('sets carry numbers', all(math.isfinite(r[3]) and math.isfinite(r[8]) for r in rows))
ok('sets are seeded', [r[3] for r in rows] == [r[3] for r in rows2])
ok('sets differ', len({r[3] for r in rows}) == 4)
s = G.fp_summary([(0, 1, 1, .1, .01, .2, 'TRUE', 1, .1, .01, .2, 'UNSURE'), (1, 1, 1, 0, -.1, .1, 'UNSURE', 1, 0, -.01, .01, 'NOT SUPPORTED')])
ok('summary shares', s['busy']['true'] == .5 and s['activity']['true'] == 0 and s['activity']['not_supported'] == .5 and s['busy']['lo_above_0'] == .5)
seen = []; real_gate = G.gate
def fake(A_, R_, *a, **k):
    seen.append((set(A_['t'].tolist()), set(R_['t'].tolist()))); x = {'gap': 0.0, 'lo': 0.0, 'hi': 0.0, 'waves': 1}
    return {'busy': x, 'strat': x}
G.gate = fake; G.fp_sets(Rf, hF, sF, bz['R'], 500, 1, 'rows', 'FADE', ['2511']); G.gate = real_gate
ok('pseudo fires leave the base: disjoint, 500 and 1500', not (seen[0][0] & seen[0][1]) and len(seen[0][0]) == 500 and len(seen[0][1]) == 1500)
print('PASS %d FAIL %d' % (len(PASS), len(FAIL)))
for n in FAIL: print('FAIL', n)
sys.exit(1 if FAIL else 0)
