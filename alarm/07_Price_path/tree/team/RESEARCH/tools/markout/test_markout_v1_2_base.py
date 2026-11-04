"""test_markout_v1_2_base.py: test_markout_v1.py (dd91de15f8e5e824, never edited) on markout_v1_2. Owner STRATEGY. New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only").
Changed: only the import of the module tested. The rest of this text is test_markout_v1.py's.
test_markout_v1.py: hand answers for markout_v1's own logic on planted files (no lab data, no grader import: the grader's functions are
exercised by the tool's gates A and B on a real run).  python3 test_markout_v1.py WORKDIR"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import markout_v1_2 as M

W = sys.argv[1]; os.makedirs(W, exist_ok=True); ok = fail = 0
US = M.US


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1; print('FAIL', name)


def put(path, head, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('\t'.join(head) + '\n')
        for r in rows:
            f.write('\t'.join(str(x) for x in r) + '\n')


# 1) the grader's inputs rebuilt from a planted run: P2 (A, 500 s, -1) comes before P1 (A, 1000 s, +1)
R = os.path.join(W, 'run')
obs = [(0, 'parent', 'A', 1000 * US, 1, 'FOLLOW'), (1, 'parent', 'A', 1000 * US, 1, 'FADE'), (2, 'parent', 'A', 500 * US, -1, 'FOLLOW'),
       (3, 'parent', 'A', 500 * US, -1, 'FADE'), (4, 'control', 'A', 1100 * US, 1, 'FOLLOW'), (5, 'control', 'A', 1100 * US, 1, 'FADE'),
       (6, 'control', 'A', 1300 * US + 250000, 1, 'FOLLOW'), (7, 'control', 'A', 1300 * US + 250000, 1, 'FADE'),
       (8, 'tough', 'A', 1200 * US, 1, 'FOLLOW'), (9, 'tough', 'A', 1200 * US, 1, 'FADE')]
put(os.path.join(R, 'measurements', 'OBSERVATIONS.tsv'), ['row', 'kind', 'coin', 'as_of_us', 'side', 'direction', 'day', 'known_at_us'],
    [list(o) + ['19700101', 0] for o in obs])
put(os.path.join(R, 'matches', 'EDGES.tsv'), ['fid', 'coin', 'parent_t', 'cand_t', 'side', 'weight', 'draw_index', 'own', 'own_v2', 'asof'],
    [['A_1000_+1', 'A', '1000.0', '1100.0004', 1, '0.5', 0, '', '', ''],
     ['A_1000_+1', 'A', '1000.0', '1300.2496', 1, '0.3', 1, 'WITHIN_H', '', 'BUSY'],
     ['A_1000_+1', 'A', '1000.0', '1400.0', 1, '0.2', 2, 'X', 'X', 'X']])
put(os.path.join(R, 'matches', 'TOUGH.tsv'), ['parent_id', 'tough_t'], [['A_1000_+1', '1200']])
put(os.path.join(R, 'grade3', 'WEIGHTS.tsv'), ['parent_id', 'cluster_id', 'weight', 'flag'],
    [['A_1000_+1', 'K:1000', '0.5', ''], ['A_500_-1', 'K:500', '1.0', '']])
I = M.rebuild_inputs(R)
check('parents sorted by clock: P2 then P1', [p['id'] for p in I['parents']] == ['A_500_-1', 'A_1000_+1'])
check('row ids', I['parents'][1]['row_ids'] == {'FOLLOW': 0, 'FADE': 1} and I['parents'][0]['row_ids'] == {'FOLLOW': 2, 'FADE': 3})
check('calm = the graded flag empty only (control at 1100.0004 -> 1100.000 s, ms rounding)', I['calm']['FADE'] == [[], [(5, 0.5)]])
check('calm_v2 = the V2 flag empty (both controls)', I['calm_v2']['FADE'] == [[], [(5, 0.5), (7, 0.3)]] and I['calm_v2']['FOLLOW'][1] == [(4, 0.5), (6, 0.3)])
check('a control flagged by every rule is never measured or graded', all(q not in (8, 9) for d in I['calm_v2'] for g in I['calm_v2'][d] for q, _ in g))
check('tough rows', I['tough']['FADE'] == [[], [9]] and I['tough']['FOLLOW'] == [[], [8]])
check('weights and clusters per parent, in parent order', I['weights'] == [1.0, 0.5] and I['clusters'] == ['K:500', 'K:1000'])
check('row coins', I['row_coin'] == ['A'] * 10)
check('parent day', I['parents'][0]['day'] == '19700101')
put(os.path.join(R, 'matches', 'TOUGH.tsv'), ['parent_id', 'tough_t'], [['A_1000_+1', '1999']])
try:
    M.rebuild_inputs(R); check('a tough clock without its row refused', False)
except M.Refused as e:
    check('a tough clock without its row refused', e.code == 'NO_TOUGH_ROW')
put(os.path.join(R, 'matches', 'TOUGH.tsv'), ['parent_id', 'tough_t'], [['A_1000_+1', '1200']])
put(os.path.join(R, 'grade3', 'WEIGHTS.tsv'), ['parent_id', 'cluster_id', 'weight', 'flag'], [['A_1000_+1', 'K:1000', '0.5', '']])
try:
    M.rebuild_inputs(R); check('a parent without a weight refused', False)
except M.Refused as e:
    check('a parent without a weight refused', e.code == 'NO_WEIGHT')
put(os.path.join(R, 'grade3', 'WEIGHTS.tsv'), ['parent_id', 'cluster_id', 'weight', 'flag'],
    [['A_1000_+1', 'K:1000', '0.5', ''], ['A_500_-1', 'K:500', '1.0', '']])

# 2) the schedule: entry = moment + wait + delay; one measurement per (clock, traded side) and wait; FADE flips; move signed by side
calls = []


def fake(t_clock, t_dec, traded):
    calls.append((t_clock, t_dec, traded))
    return np.array([t_clock / US, t_dec / US, traded, 0.0]), 0.7


rows = [(0, 'parent', 1000 * US, 1, 'FOLLOW'), (1, 'parent', 1000 * US, 1, 'FADE'), (4, 'control', 1000 * US, -1, 'FOLLOW')]
got = M.measure_rows(rows, [0, 60], 2.0, fake, 4, 3)
check('two measurements a wait (+1 and -1 traded; the control at -1 FOLLOW shares the FADE one)', len(calls) == 4)
check('clocks: decision = moment + wait, entry = decision + 2 s', sorted(set((c[0], c[1]) for c in calls)) == [(1000 * US, 1002 * US), (1060 * US, 1062 * US)])
ids, V = got[60]
check('row ids kept', list(ids) == [0, 1, 4])
check('traded side: FOLLOW +1, FADE of a +1 parent -1, FOLLOW of a -1 parent -1', list(V[:, 2]) == [1, -1, -1])
check('move15 signed by each row\'s own parent side', list(V[:, 3]) == [0.7, 0.7, -0.7])
check('wait 60 rows read from moment + 60', all(V[:, 0] == 1060) and all(got[0][1][:, 0] == 1000))

# 3) gates
a = np.array([[1.0, np.nan], [0.5, 2.0]]); b = a.copy()
check('equal values with NaN: 0', M.values_diff(a, b) == 0)
b[1, 1] = np.nextafter(2.0, 3.0)
check('one bit: 1', M.values_diff(a, b) == 1)
b = a.copy(); b[0, 1] = 0.0
check('NaN against a number: 1', M.values_diff(a, b) == 1)
check('shape: -1', M.values_diff(a, a[:1]) == -1)
tp = os.path.join(W, 'T.tsv'); open(tp, 'w').write('h\nx\t1\ny\t2\n')
check('table text equal: 0', M.table_diff(['x\t1', 'y\t2'], tp) == 0)
check('one row differs: 1', M.table_diff(['x\t1', 'y\t3'], tp) == 1)
check('a row missing counts', M.table_diff(['x\t1'], tp) == 1)
fmt = lambda x: '' if x is None else (('%.6g' % x) if isinstance(x, float) else str(x))
check('table_text formats like the grader', M.table_text([('ALL', 0.1234567, 3)], fmt) == ['ALL\t0.123457\t3'])

# 4) the curve keeps the six horizon returns, TT, three stats
tab = [('ALL', 'FADE', 'ret_1h', 'TT', 'STRESS', 'PARENT', -0.1, -0.2, 0.0, 600, 340), ('ALL', 'FADE', 'ret_1h', 'RT', 'STRESS', 'PARENT', 0, 0, 0, 1, 1),
       ('ALL', 'FADE', 'V1_1h', 'TT', 'STRESS', 'PARENT', 0, 0, 0, 1, 1), ('ALL', 'FADE', 'ret_1h', 'TT', 'STRESS', 'CALM', 0, 0, 0, 1, 1),
       ('202509', 'FADE', 'ret_5m', 'TT', 'GROSS', 'TOUGH_EDGE', 0.1, 0, 0.2, 100, 50)]
C = M.curve_rows(60, 'H1', tab)
check('curve rows: 2 kept', len(C) == 2 and C[0][:4] == (60, 'H1', 'ALL', 'FADE') and C[1][2] == '202509')

# 5) checks and refusals
f1 = os.path.join(W, 'code.py'); open(f1, 'w').write('x = 1\n')
check('code unchanged', M.check_code({f1: M.sha16(f1)}) == [])
check('code changed or missing', len(M.check_code({f1: '0' * 16, os.path.join(W, 'nope.py'): '1' * 16})) == 2)
check('waits sorted', M.parse_waits('60,0,300', 900) == [0, 60, 300])
for bad in ('-1', '901', '0,0', '', 'a'):
    try:
        M.parse_waits(bad, 900); check('bad waits %r refused' % bad, False)
    except M.Refused:
        check('bad waits %r refused' % bad, True)
S = os.path.join(W, 'S.json'); json.dump(dict(waits_s=[0, 60], max_wait_s=900, max_workers=3, allowed_last='20260228', split_day='20251101'), open(S, 'w'))
args = lambda out, **k: ['run', '--run', k.get('run', R), '--settings', k.get('settings', S), '--out', out] + k.get('more', [])
os.makedirs(os.path.join(W, 'exists'), exist_ok=True)
check('out exists refused', M.main(args(os.path.join(W, 'exists'))) == 2)
Sb = os.path.join(W, 'Sb.json'); json.dump(dict(waits_s=[0]), open(Sb, 'w'))
check('bad settings refused', M.main(args(os.path.join(W, 'o1'), settings=Sb)) == 2)
check('too many workers refused', M.main(args(os.path.join(W, 'o2'), more=['--workers', '4'])) == 2)
check('an incomplete run refused', M.main(args(os.path.join(W, 'o3'))) == 2)
for n in ('measurements/VALUES3.npy', 'measurements/NAMES3.json', 'grade3/TABLE.tsv'):
    open(os.path.join(R, n), 'w').write('x')
costs = os.path.join(W, 'COSTS.tsv'); open(costs, 'w').write('coin\tcost_bp\tfee_bp\nA\t10\t4\n')
run_json = dict(selection=dict(research_window=['20250910', '20260331'], coins=['A']), code_sha16={f1: M.sha16(f1)},
                settings=dict(costs=dict(path=costs, sha16=M.sha16(costs), gaps_pct=dict(HONEST=0.032, STRESS=0.144), maker_fee_bp=1.5),
                              measure=dict(execution_delay_s=2.0)), sources=dict(lab_root='/nope'))
json.dump(run_json, open(os.path.join(R, 'RUN.json'), 'w'))
check('a run reaching past Feb 2026 refused (Mar-May never)', M.main(args(os.path.join(W, 'o4'))) == 2)
run_json['selection']['research_window'] = ['20250910', '20251231']; run_json['code_sha16'] = {f1: 'f' * 16}
json.dump(run_json, open(os.path.join(R, 'RUN.json'), 'w'))
check('changed grader code refused', M.main(args(os.path.join(W, 'o5'))) == 2)
run_json['code_sha16'] = {f1: M.sha16(f1)}; run_json['settings']['costs']['sha16'] = 'e' * 16
json.dump(run_json, open(os.path.join(R, 'RUN.json'), 'w'))
check('changed cost table refused', M.main(args(os.path.join(W, 'o6'))) == 2)
check('nothing made on a refusal', not any(os.path.exists(os.path.join(W, 'o%d' % i)) for i in range(1, 7)))
# mutant: a schedule that forgets the delay must fail the clock answer
orig = M.measure_rows
calls.clear(); orig(rows, [0], 0.0, fake, 4, 3)
check('mutant caught (no delay gives other entry clocks)', sorted(set(c[1] for c in calls)) != [1002 * US])
print('UNITS %d PASS %d FAIL' % (ok, fail)); sys.exit(1 if fail else 0)
