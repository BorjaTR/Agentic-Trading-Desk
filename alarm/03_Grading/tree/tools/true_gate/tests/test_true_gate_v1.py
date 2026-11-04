#!/usr/bin/env python3
"""tests of true_gate_v1: expected answers are written by hand beside each case, never from the code under test. No lab data read, except that
the family table is read from the file. Run: python3 -B test_true_gate_v1.py [code dir]"""
import copy, importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.environ.get('TG_CODE', os.path.join(HERE, '..'))
sp = importlib.util.spec_from_file_location('tg', os.path.join(CODE, 'true_gate_v1.py')); TG = importlib.util.module_from_spec(sp); sp.loader.exec_module(TG)
FAM = TG.load_families(os.path.join(HERE, '..', 'SOURCE_FAMILIES_V1.tsv'))
D = 1762214400            # 2025-11-04 00:00 UTC
DAY = '20251104'
PASS = []; FAIL = []


def ok(name, cond):
    (PASS if cond else FAIL).append(name)


class Plant:
    """a planted source: {code: (step, {coin: {tau offset s: value}}, age, reason, known lag)}"""

    def __init__(self):
        self.d = {}

    def put(self, code, step, coin, vals, age=None, e=None, k=None, day=DAY):
        n = 86400 // step
        if (code, day) not in self.d:
            self.d[(code, day)] = {'coins': {'AAA': 0, 'BBB': 1}, 'step': step, 'v': np.full((2, n), np.nan), 'a': np.full((2, n), -2147483648, np.int32),
                                   'e': np.zeros((2, n), np.uint8), 'k': None}
        x = self.d[(code, day)]; i = x['coins'][coin]
        for off, v in vals.items():
            j = off // step; x['v'][i, j] = v; x['a'][i, j] = 0
        if age:
            for off, a in age.items():
                x['a'][i, off // step] = a
        if e:
            for off, c in e.items():
                x['e'][i, off // step] = c
        if k is not None:
            if x['k'] is None:
                x['k'] = (TG.day0(day) + step * np.arange(n))[None, :].repeat(2, axis=0).astype(np.int64) * 1_000_000
            for off, s in k.items():
                x['k'][i, off // step] = (TG.day0(day) + s) * 1_000_000

    def native(self, code, day):
        return self.d.get((code, str(day)))


def lab(**k):
    b = {'kind': 'metric_test', 'code': 'E2.S04', 'when': 'present', 'end_s': 600, 'test': '<=', 'agg': 'last', 'thr': 0, 'max_age_s': 120}
    b.update(k); return b


T = D + 3600    # a moment on the clock
OFF = 3600

# ---- 1 planted label cases, answers by hand
p = Plant(); p.put('E2.S04', 60, 'AAA', {OFF: -1.5, OFF + 60: 9.0})
ok('last <= thr: -1.5 <= 0 is a hit', TG.hit_of(lab(), TG.metric_value(p, lab(), 'AAA', T, -1), 0.0) == 1.0)
ok('last as of t, off the clock: t + 59 s still reads column at t', TG.metric_value(p, lab(), 'AAA', T + 59, -1) == -1.5)
ok('last as of t: t + 60 reads the next column', TG.metric_value(p, lab(), 'AAA', T + 60, -1) == 9.0)

p = Plant(); p.put('A1.S01', 5, 'AAA', {OFF + 5: 100.0, OFF + 10: 50.0, OFF + 15: 25.0, OFF + 20: 7.0, OFF: 1000.0, OFF - 5: 3000.0})
L = lab(code='A1.S01', when='window', start_s=0, end_s=15, agg='sum', test='>=', thr=175)
ok('window sum (t, t+15] = 100+50+25, the row at t left out', TG.metric_value(p, L, 'AAA', T, -1) == 175.0)
ok('window sum meets >= 175', TG.hit_of(L, 175.0, 175.0) == 1.0)
L2 = dict(L, start_s=5)
ok('window (t+5, t+15] = 50+25', TG.metric_value(p, L2, 'AAA', T, -1) == 75.0)
L3 = lab(code='A1.S01', when='present', end_s=10, agg='sum', test='>=', thr=1)
ok('present sum (t-10, t] = 3000+1000, nothing after t', TG.metric_value(p, L3, 'AAA', T, -1) == 4000.0)
ok('off-clock moment: rows whose whole step is inside (t, t+15]: t=+2: 50+25 (the row ending t+5 starts before t+2)', TG.metric_value(p, L, 'AAA', T + 2, -1) == 75.0)
L4 = dict(L, agg='mean'); ok('mean 175/3', abs(TG.metric_value(p, L4, 'AAA', T, -1) - 175 / 3.0) < 1e-12)
L5 = dict(L, agg='max'); ok('max', TG.metric_value(p, L5, 'AAA', T, -1) == 100.0)
L6 = dict(L, agg='min'); ok('min', TG.metric_value(p, L6, 'AAA', T, -1) == 25.0)

p = Plant(); p.put('E2.S02', 60, 'AAA', {OFF - 600: 100.0, OFF: 90.0, OFF - 60: 500.0})
F = lab(code='E2.S02', test='falling', agg=None, change='pct')
ok('falling reads the two ends only: 100 to 90 = -10 pct', abs(TG.metric_value(p, F, 'AAA', T, 1) + 10.0) < 1e-12)
ok('falling hit', TG.hit_of(F, -10.0, 0.0) == 1.0)
ok('not falling on 0', TG.hit_of(F, 0.0, 0.0) == 0.0)
ok('falling with threshold 12: -10 is no hit', TG.hit_of(F, -10.0, 12.0) == 0.0)
ok('rising on -10 is no hit', TG.hit_of(dict(F, test='rising'), -10.0, 0.0) == 0.0)
ok('rising on +3 is a hit', TG.hit_of(dict(F, test='rising'), 3.0, 0.0) == 1.0)

# sign and side
p = Plant(); p.put('B1.S01', 60, 'AAA', {OFF: 7.0})
S = lab(code='B1.S01', sign='same', test='>=', thr=0)
ok('sign same, side -1: -7', TG.metric_value(p, S, 'AAA', T, -1) == -7.0)
ok('sign opposite, side -1: +7', TG.metric_value(p, dict(S, sign='opposite'), 'AAA', T, -1) == 7.0)
ok('sign with side 0 is NOT KNOWN', math.isnan(TG.metric_value(p, S, 'AAA', T, 0)))
p = Plant(); p.put('A1.S01', 5, 'AAA', {OFF: 11.0}); p.put('A1.S02', 5, 'AAA', {OFF: 22.0})
B = lab(code=None, code_by_side={'-1': 'A1.S01', '1': 'A1.S02'}, when='present', end_s=5, agg='last')
ok('code_by_side, side -1 reads the long code', TG.metric_value(p, B, 'AAA', T, -1) == 11.0)
ok('code_by_side, opposite', TG.metric_value(p, dict(B, dir='opposite'), 'AAA', T, -1) == 22.0)

# threshold known at t
p = Plant(); p.put('E2.S04', 60, 'AAA', {OFF: 5.0}); p.put('E1.S01', 60, 'AAA', {OFF: 4.0, OFF + 60: 99.0}, k={OFF: OFF})
TC = lab(thr=None, thr_code={'code': 'E1.S01', 'scale': 1.0}, test='>=')
ok('threshold read as of t: 4, not the 99 after it', TG.threshold(p, TC, 'AAA', T) == 4.0)
p2 = Plant(); p2.put('E1.S01', 60, 'AAA', {OFF: 4.0}, k={OFF: OFF + 30})
ok('threshold known after t is NOT KNOWN', math.isnan(TG.threshold(p2, TC, 'AAA', T)))
ok('a NaN threshold gives NOT KNOWN, not false', math.isnan(TG.hit_of(TC, 5.0, float('nan'))))

# ---- 2 stale and missing
p = Plant(); p.put('E2.S04', 60, 'AAA', {OFF: -1.0}, age={OFF: 900})
ok('age 900 over max_age 120: NOT KNOWN', math.isnan(TG.metric_value(p, lab(), 'AAA', T, 1)))
ok('age 900 under max_age 1000: known', TG.metric_value(p, lab(max_age_s=1000), 'AAA', T, 1) == -1.0)
ok('age equal to max_age is known', TG.metric_value(p, lab(max_age_s=900), 'AAA', T, 1) == -1.0)
p = Plant(); p.put('E2.S04', 60, 'AAA', {OFF: -1.0}, e={OFF: 3})
ok('a value with a reason is NOT KNOWN', math.isnan(TG.metric_value(p, lab(), 'AAA', T, 1)))
p = Plant(); p.put('E2.S04', 60, 'BBB', {OFF: -1.0})
ok('missing value: NOT KNOWN, never false', math.isnan(TG.metric_value(p, lab(), 'AAA', T, 1)))
ok('missing hit is NaN', math.isnan(TG.hit_of(lab(), TG.metric_value(p, lab(), 'AAA', T, 1), 0.0)))
ok('a coin the day does not list: NOT KNOWN', math.isnan(TG.metric_value(p, lab(), 'ZZZ', T, 1)))
ok('a code not built: NOT KNOWN', math.isnan(TG.metric_value(Plant(), lab(), 'AAA', T, 1)))
p = Plant(); p.put('A1.S01', 5, 'AAA', {OFF + 5: 1.0, OFF + 15: 1.0})
ok('a hole inside a sum makes the sum NOT KNOWN', math.isnan(TG.metric_value(p, L, 'AAA', T, 1)))
p = Plant(); p.put('E2.S02', 60, 'AAA', {OFF: 90.0})
ok('falling with the start missing: NOT KNOWN', math.isnan(TG.metric_value(p, F, 'AAA', T, 1)))
p = Plant(); p.put('E2.S02', 60, 'AAA', {OFF - 600: 0.0, OFF: 90.0})
ok('pct change on a zero base: NOT KNOWN', math.isnan(TG.metric_value(p, F, 'AAA', T, 1)))

# ---- 3 no look-ahead: a prefix test and a future plant
p1 = Plant(); p2 = Plant()
base = {OFF + 60 * i: float(i) for i in range(-30, 1)}
fut = {OFF + 60 * i: 1e9 for i in range(1, 60)}
p1.put('E2.S02', 60, 'AAA', base); p2.put('E2.S02', 60, 'AAA', {**base, **fut})
for nm, l in (('falling present', F), ('last present', lab(code='E2.S02', test='>=', thr=-1e12)), ('sum present', lab(code='E2.S02', agg='sum', test='>=', thr=-1e12)), ('max present', lab(code='E2.S02', agg='max', test='>=', thr=-1e12))):
    ok('prefix: %s equal with the future cut or planted' % nm, TG.metric_value(p1, l, 'AAA', T, 1) == TG.metric_value(p2, l, 'AAA', T, 1))
pK = Plant(); pK.put('E2.S02', 60, 'AAA', {OFF - 600: 100.0, OFF: 90.0}, k={OFF: OFF + 30})
ok('present label: a value known after t is NOT KNOWN', math.isnan(TG.metric_value(pK, F, 'AAA', T, 1)))
pW = Plant(); pW.put('A1.S01', 5, 'AAA', {OFF + 5: 1.0, OFF + 10: 1.0, OFF + 15: 1.0})
pW2 = copy.deepcopy(pW); pW2.d[('A1.S01', DAY)]['v'][0, OFF // 5] = 1e9; pW2.d[('A1.S01', DAY)]['v'][0, (OFF + 20) // 5] = 1e9; pW2.d[('A1.S01', DAY)]['a'][0, (OFF + 20) // 5] = 0
ok('window label: the footprint row at t and rows past the end do not count', TG.metric_value(pW, L, 'AAA', T, 1) == TG.metric_value(pW2, L, 'AAA', T, 1))
ok('window label: the prefix cut at the window end is NaN when cut before it', math.isnan(TG.metric_value(Plant(), L, 'AAA', T, 1)))


class Cut(Plant):
    def __init__(self, inner, last):
        self.inner = inner; self.last = last

    def native(self, code, day):
        return None if str(day) > self.last else self.inner.native(code, day)


pD = Plant(); pD.put('E2.S04', 60, 'AAA', {0: -1.0}, day='20251105')
Lw = lab(when='window', start_s=0, end_s=60, agg='last')
ok('a label crossing the last day is NOT KNOWN', math.isnan(TG.metric_value(Cut(pD, DAY), Lw, 'AAA', TG.day0('20251105') - 30, 1)))
ok('the same inside the day is known', TG.metric_value(Cut(pD, '20251105'), Lw, 'AAA', TG.day0('20251105') - 30, 1) == -1.0)


# ---- 4 circular refusal: planted
def ref(dfn, l):
    try:
        TG.check_circular(dfn, l, FAM); return None
    except TG.Refused as e:
        return e.code


def df(*codes, price=False):
    inp = {'i%d' % j: {'op': 'raw', 'code': c} for j, c in enumerate(codes)}
    if price:
        inp['px'] = {'op': 'price'}
    return {'inputs': inp, 'conditions': [], 'fire': {}}


ok('same code refused', ref(df('E2.S04'), lab()) == 'SAME_CODE')
ok('E2.S02 and E2.S04 are one family', ref(df('E2.S02'), lab()) == 'SAME_FAMILY')
ok('A1 and X1.LIQX are one family', ref(df('A1.S01'), lab(code='X1.LIQX.S03')) == 'SAME_FAMILY')
ok('A7 reads open interest', ref(df('A7.S01'), lab()) == 'SAME_FAMILY')
ok('X1.POSX.S09 reads open interest', ref(df('X1.POSX.S09'), lab()) == 'SAME_FAMILY')
ok('HL closing and HL open interest are one family', ref(df('X1.HLFLOWX.S09'), lab(code='E2.S06')) == 'SAME_FAMILY')
ok('price op with a price label', ref(df('A1.S01', price=True), lab(code='C2.S06')) == 'PRICE_DERIVED')
ok('price-derived label C4 refused', ref(df('A1.S01'), lab(code='C4.S04')) == 'PRICE_DERIVED')
ok('mark premium E3 refused', ref(df('A1.S01'), lab(code='E3.S01')) == 'PRICE_DERIVED')
ok('an unknown label code refused', ref(df('A1.S01'), lab(code='NO.SUCH')) == 'UNKNOWN_SOURCE')
ok('an unknown trigger code refused', ref(df('NO.SUCH'), lab()) == 'UNKNOWN_SOURCE')
ok('a card-less family refused', ref(df('A1.S01'), lab(code='A6.S01')) == 'UNKNOWN_SOURCE')
ok('an event list of unknown source refused', ref({'inputs': {'e': {'op': 'ev_since', 'events': 'L', 'w_s': 60}}}, lab()) == 'UNKNOWN_SOURCE')
ok('an event list with its source stated: refused on that family', ref({'inputs': {'e': {'op': 'ev_since', 'events': 'L', 'w_s': 60}}, 'events_family': {'L': 'OI_BN'}}, lab()) == 'SAME_FAMILY')
ok('an unknown op refused', ref({'inputs': {'a': {'op': 'new_op'}}}, lab()) == 'UNKNOWN_OP')
ok('a code in the fire side is seen', ref({'inputs': {}, 'fire': {'side': {'op': 'raw', 'code': 'E2.S02'}}}, lab()) == 'SAME_FAMILY')
ok('a code nested inside an op is seen', ref({'inputs': {'a': {'op': 'sum', 'of': {'op': 'raw', 'code': 'E2.S02'}, 'w_s': 60}}}, lab()) == 'SAME_FAMILY')
ok('a mirror code is seen', ref({'inputs': {}, 'mirror': {'E2.S02': '-'}}, lab()) == 'SAME_FAMILY')
ok('a threshold code is read too', ref(df('A1.S01'), lab(thr=None, thr_code={'code': 'A1.S02'}, test='>=')) == 'SAME_FAMILY')
ok('a price-derived threshold refused', ref(df('A1.S01'), lab(thr=None, thr_code={'code': 'C4.S04'}, test='>=')) == 'PRICE_DERIVED')
ok('a side-picked code is read', ref(df('A1.S01'), lab(code=None, code_by_side={'1': 'A1.S02', '-1': 'A1.S01'})) == 'SAME_CODE')
ok('the FDA2APR rule may be tested on Binance open interest', ref(df('A1.S08', 'C2.S06', 'X1.HLFLOWX.S08', 'X1.HLFLOWX.S09', price=True), lab()) is None)
ok('a truth label inside the definition is not the trigger', ref(dict(df('A1.S08'), truth=[{'code': 'E2.S04'}]), lab()) is None)
for bad in (dict(max_age_s=None), dict(max_age_s=0), dict(test='!='), dict(when='later'), dict(agg='median'), dict(start_s=-5, when='window'), dict(end_s=0), dict(thr=None), dict(thr=float('nan'))):
    ok('bad label refused: %s' % bad, ref(df('A1.S08'), lab(**bad)) == 'BAD_LABEL')
ok('two thresholds refused', ref(df('A1.S08'), lab(thr=1, thr_code={'code': 'E1.S01'})) == 'BAD_LABEL')

# ---- 5 the verdict order, by hand
ok('TRUE at the bar', TG.verdict(0.05, 0.01, 0.09) == 'TRUE')
ok('just under the gap bar with its interval above 0: UNSURE (top over .05)', TG.verdict(0.049, 0.01, 0.09) == 'UNSURE')
ok('gap over the bar, interval touches 0: UNSURE', TG.verdict(0.06, 0.0, 0.12) == 'UNSURE')
ok('wide around 0: UNSURE', TG.verdict(0.0, -0.2, 0.2) == 'UNSURE')
ok('precise and small: NOT SUPPORTED', TG.verdict(0.01, -0.01, 0.03) == 'NOT SUPPORTED')
ok('top exactly .05 is not under .05: UNSURE', TG.verdict(0.01, -0.01, 0.05) == 'UNSURE')
ok('precise and negative: NOT SUPPORTED', TG.verdict(-0.1, -0.15, -0.05) == 'NOT SUPPORTED')
ok('NaN: UNSURE', TG.verdict(float('nan'), 0.1, 0.2) == 'UNSURE')

# ---- 6 the comparison: a tiny world worked by hand
def world(hit_f, n_w=40, hit_r=0.2, seed=1):
    t0 = TG.day0('20251104'); Ac, At = [], []
    for w in range(n_w):                     # waves 1 h apart, two fires each
        At += [t0 + w * 3600, t0 + w * 3600 + 60]; Ac += ['AAA', 'BBB']
    A = {'coin': np.array(Ac, object), 't': np.array(At, np.int64), 'side': -np.ones(len(At)), 'w': np.ones(len(At)), 'c': np.full(len(At), 0.2)}
    nr = 400; Rt = t0 + 7 * np.arange(nr) * 60 + 1800          # away from the fires' hour starts by more than nothing: pre-fire moments handled below
    R = {'coin': np.array(['CCC'] * nr, object), 't': Rt.astype(np.int64), 'side': -np.ones(nr), 'w': np.ones(nr) * 0.5, 'c': np.full(nr, 0.2)}
    hA = np.full(len(At), float(hit_f)); hR = np.zeros(nr); hR[:int(round(nr * hit_r))] = 1.0
    bz = {'A': {'normal_move_pct': np.full(len(At), 1.0), 'range60_pct': np.full(len(At), 1.0), 'move15_pct': np.full(len(At), 1.0)},
          'R': {'normal_move_pct': np.full(nr, 1.0), 'range60_pct': np.full(nr, 1.0), 'move15_pct': np.full(nr, 1.0)}}
    return A, R, hA, hR, bz


A, R, hA, hR, bz = world(1.0)
res = TG.compare(A, R, hA, hR, bz, 'FADE', ['2511'], 0.0)
ok('hand world: all fires hit, random .2 in one cell: gap .8', abs(res['all']['gap'] - 0.8) < 1e-9)
ok('hand world: 40 waves', res['all']['waves'] == 40)
ok('hand world: 80 fires', res['all']['fires'] == 80)
ok('hand world: released stats7 agrees (points)', abs(res['stats7_mean'] - 80.0) < 1e-6)
ok('hand world: verdict TRUE', TG.verdict(res['all']['gap'], res['all']['lo'], res['all']['hi']) == 'TRUE')
hB = hA.copy(); hB[1::2] = 0.0                  # every wave's second fire misses: wave value 0.5 - 0.2 = 0.3, by wave, not by anything else
res = TG.compare(A, R, hB, hR, bz, 'FADE', ['2511'], 0.0)
ok('one value per wave: .3', abs(res['all']['gap'] - 0.3) < 1e-9)
hC = hA.copy(); hC[1:] = np.nan                  # one wave known only
res = TG.compare(A, R, hC, hR, bz, 'FADE', ['2511'], 0.0)
ok('NOT KNOWN fires leave the count, never read as no hit', res['all']['fires'] == 1 and res['all']['waves'] == 1 and abs(res['all']['gap'] - 0.8) < 1e-9)
ok('one wave: no interval, UNSURE', TG.verdict(res['all']['gap'], res['all']['lo'], res['all']['hi']) == 'UNSURE')
hR2 = hR.copy(); hR2[50:] = np.nan              # known random: 50 of 50 hit, share 1: gap 0
res = TG.compare(A, R, hA, hR2, bz, 'FADE', ['2511'], 0.0)
ok('NOT KNOWN random leave the base, never read as no hit: expected 1, gap 0', abs(res['all']['gap']) < 1e-9)
A2, R2, hA2, hR3, bz2 = world(0.0, hit_r=0.0)
A2 = dict(A2); bz2['A']['normal_move_pct'] = np.full(80, 0.1)
res = TG.compare(A2, R2, np.ones(80), hR3, bz2, 'FADE', ['2511'], 1.12)
ok('busy filter 1.12c: calm fires out', res['all']['fires'] == 0)

# ---- 7 engine wiring: released kinds pass through unchanged; metric_test works in the engine's shape
class Ctx:
    coins = ['AAA', 'BBB']; t = D + 5 * np.arange(3 * 17280)

    def __init__(self, src):
        self.src = src

    def get(self, n):
        return np.full((2, 3 * 17280), -0.5)


p = Plant(); p.put('E2.S04', 60, 'AAA', {OFF: -1.0})
r = OFF // 5
v = TG.label_values_v2(Ctx(p), lab(thr=None, thr_input='x'), [(0, r)], [-1])
ok('engine: thr_input read at the row: -1 <= -.5', v['hit'][0] == 1.0 and v['value'][0] == -1.0)
try:
    TG.label_values_v2(Ctx(p), {'kind': 'no_such', 'end_s': 5}, [(0, r)], [-1]); ok('released kinds go to the released function', False)
except ValueError as e:
    ok('released kinds go to the released function', 'not in the registry' in str(e))

# ---- 8 end to end on planted files: the PERFIRE's rows outside the window and its race columns are not read
import gzip, tempfile
tmp = tempfile.mkdtemp(dir=os.environ.get('TMPDIR') or None)
A, R, hA, hR, bz = world(1.0)
pf = os.path.join(tmp, 'PERFIRE.tsv')
with open(pf, 'w') as f:
    f.write('kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc\tFADE 1h\n')
    for c, t in zip(A['coin'], A['t']):
        f.write('A\t%s\t%d\t\t\t\t-1\t0\t1\t1\t0.2\tNOT_A_NUMBER\n' % (c, t))
    for c, t in zip(R['coin'], R['t']):
        f.write('R\t%s\t%d\t\t\t\t-1\t0\t0.5\t1\t0.2\tNOT_A_NUMBER\n' % (c, t))
    f.write('A\tAAA\t%d\t\t\t\t-1\t0\t1\t1\t0.2\tNOT_A_NUMBER\n' % TG.day0('20260115'))
for nm, T_ in (('a', A), ('r', R)):
    with gzip.open(os.path.join(tmp, 'BZ_%s.tsv.gz' % nm), 'wt') as f:
        f.write('coin\tt\tnormal_move_pct\trange60_pct\tmove15_pct\n')
        for c, t in zip(T_['coin'], T_['t']):
            f.write('%s\t%d\t1\t1\t1\n' % (c, t))
AA, RR, drop = TG.load_perfire(pf, '20251101', '20251130')
ok('load_perfire: the January row is left unread', drop == 1 and len(AA['t']) == 80 and int(AA['t'].max()) < TG.day0('20251201'))
class Src(Plant):
    pass
ps = Src(); ps.d = {}
for code in ('E2.S04',):
    for day in ('20251104', '20251105', '20251106', '20251107'):
        n = 1440; d0 = TG.day0(day)
        v = np.full((3, n), -1.0); v[2] = 1.0     # AAA and BBB always closing, CCC (the random) never
        ps.d[(code, day)] = {'coins': {'AAA': 0, 'BBB': 1, 'CCC': 2}, 'step': 60, 'v': v, 'a': np.zeros((3, n), np.int32), 'e': np.zeros((3, n), np.uint8), 'k': None}
cl = {'id': 'E2E', 'alarm_id': 'P', 'inputs': {'x': {'op': 'raw', 'code': 'A1.S08'}}, 'label': lab(), 'perfire': pf, 'perfire_sha16': TG.sha16(pf),
      'bz_a': os.path.join(tmp, 'BZ_a.tsv.gz'), 'bz_r': os.path.join(tmp, 'BZ_r.tsv.gz'), 'first': '20251101', 'last': '20251130', 'lab_days': '-', 'lean': 'FADE'}
cp = os.path.join(tmp, 'c.json'); json.dump(cl, open(cp, 'w'))
row = TG.run(cp, os.path.join(tmp, 'out'), src=ps)
ok('e2e: gap 1.0, TRUE, 40 waves', row['gap'] == 1.0 and row['verdict'] == 'TRUE' and row['waves'] == 40)
cl2 = dict(cl, label=lab(code='A1.S08')); json.dump(cl2, open(cp, 'w'))
try:
    TG.run(cp, os.path.join(tmp, 'out2'), src=ps); ok('e2e: a circular claim refused before any data', False)
except TG.Refused as e:
    ok('e2e: a circular claim refused before any data', e.code == 'SAME_CODE' and not os.path.exists(os.path.join(tmp, 'out2')))
cl3 = dict(cl, perfire_sha16='0' * 16); json.dump(cl3, open(cp, 'w'))
try:
    TG.run(cp, os.path.join(tmp, 'out3'), src=ps); ok('e2e: a changed PERFIRE refused', False)
except TG.Refused as e:
    ok('e2e: a changed PERFIRE refused', e.code == 'PERFIRE_CHANGED')
json.dump(cl, open(cp, 'w'))
try:
    TG.run(cp, os.path.join(tmp, 'out'), src=ps); ok('e2e: a second run on the same folder refused', False)
except TG.Refused as e:
    ok('e2e: a second run on the same folder refused', e.code == 'OUT_EXISTS')

# ---- 9 cases added for mutants that survived the first run (failing-before receipt: receipts/MUTANTS_FIRST_RUN.txt)
ok('rising on 0 is no hit', TG.hit_of(dict(F, test='rising'), 0.0, 0.0) == 0.0)
ok('<= at equality is a hit', TG.hit_of(lab(thr=-1), -1.0, -1.0) == 1.0)
FX = dict(FAM); FX['PX.ONLY'] = {'fam': {'PRICE'}, 'px': False, 'status': 'CARD'}
try:
    TG.check_circular(df('A1.S01'), lab(code='PX.ONLY'), FX); ok('a code of the PRICE family is refused, whatever its flag', False)
except TG.Refused as e:
    ok('a code of the PRICE family is refused, whatever its flag', e.code == 'PRICE_DERIVED')
t0 = TG.day0('20251104')
Au = {'coin': np.array(['AAA', 'BBB', 'AAA', 'BBB'] * 10, object), 't': np.concatenate([[t0 + 3600 * 2 * w, t0 + 3600 * 2 * w + 3600, t0 + 3600 * 2 * w + 3660, t0 + 3600 * 2 * w + 3720] for w in range(10)]).astype(np.int64)}
Au.update(side=-np.ones(40), w=np.ones(40), c=np.full(40, 0.2))
hU = np.tile([1.0, 0.0, 0.0, 0.0], 10)          # one fire in a wave of its own hits, a wave of three misses: by wave .5, by fire .25
_, Ru, _, hRu, _ = world(1.0, hit_r=0.0)
bzu = {'A': {'normal_move_pct': np.ones(40), 'range60_pct': np.ones(40), 'move15_pct': np.ones(40)}, 'R': {'normal_move_pct': np.ones(400), 'range60_pct': np.ones(400), 'move15_pct': np.ones(400)}}
res = TG.compare(Au, Ru, hU, hRu, bzu, 'FADE', ['2511'], 0.0)
ok('waves of different sizes: one value per wave, .5, not .25 by fire', res['all']['waves'] == 20 and abs(res['all']['gap'] - 0.5) < 1e-9)
A3, R3, _, hR3b, bz3 = world(1.0, hit_r=0.0)
bz3['A']['normal_move_pct'] = np.full(80, 0.1)        # .5c: under the busy line
bz3['R']['normal_move_pct'] = np.r_[np.full(200, 0.1), np.full(200, 1.0)]
res = TG.compare(A3, R3, np.ones(80), hR3b, bz3, 'FADE', ['2511'], 1.12)
ok('busy line 1.12c: fires at .5c leave, though random moments stand at .5c', res['all']['fires'] == 0)
res = TG.compare(A3, R3, np.ones(80), hR3b, bz3, 'FADE', ['2511'], 0.0)
ok('no busy line: the same fires count', res['all']['fires'] == 80)
ns = TG.NativeSource.__new__(TG.NativeSource); ns.last = '20251231'; ns._c = {}; opened = []
ns._read = lambda code, day: opened.append(day)
ok('NativeSource: a day after the last is not opened', ns.native('E2.S04', '20260101') is None and not opened)
ns.native('E2.S04', '20251231'); ok('NativeSource: the last day is', opened == ['20251231'])

print('PASS %d FAIL %d' % (len(PASS), len(FAIL)))
for n in FAIL:
    print('FAIL', n)
sys.exit(1 if FAIL else 0)
