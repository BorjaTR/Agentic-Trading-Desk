# test_lead_null_v1_1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): test_lead_null_v1.py 9fac443c42a83d67 (CLAUDE1 29 Oct) unchanged but
# for the edition it imports: lead_null_v1_1_to20251231.py (the paths-only edition; no current file imports a past edition).
# test_lead_null_v1.py (CLAUDE1_20261028, 29 Oct 2026; review round 1 applied 29 Oct 2026). TEST, NOT REVIEWED. Synthetic tests for
# lead_null_v1_to20251231.py (written before the tool; the owner's rule: the smallest test per issue first, the real run last). Plain python +
# numpy, no event_outcomes, no labcore: the tool is imported from its path with importlib and must not import them at import time.
#   python3 -B test_lead_null_v1.py
# a) planted: 60 days x 10 waves, lean always wins: real lead +100 and all rules pass; with the real lead removed before flipping, power
#    is 1.0 at delta 3/5/7 and 0 at delta 0 for every block length; the 1h_only and by_month shapes give their exact expected rates.
# b) null: iid normal(0, 50) d_w, 1,200 waves over 120 days, 10,000 flips: R3 false pass <= 1 pct at block 1, 3, 7; a shifted real lead
#    (+20 / -15) gives the same null (the lead is removed before flipping); power rises with delta.
# c) window: a 2026-01-02 fire and a 2025-12-31 23:30 fire are dropped and counted; complete-case drops counted; outside rows raise.
# d) blocks: one sign per block (1, 3, 7 days, grid from 2025-09-10), the same at 15m and 1h.
# e) pairing: own skipped, first 3 by draw_index, +1 and +3 s matched, +4 s unmatched, candidate outside or after 22:59:59 dropped.
# f) gate: within 0.15 passes, 0.2 fails, missing keys skipped, nothing checked fails.
# g) cli: RESULTS (180 rows, Wilson bounds), REAL_SEALED/, SUMMARY and stdout and RECEIPT without the real lead, MATCH_FAIL version.
# h) the day-level statistics equal a wave-level reference written here (all shapes, blocks, centred or not).
# i) per-fire complete cases: a wave's lead is the mean over its complete fires only.
# j) months per horizon and R2s: a month counts at a horizon with 30+ finite waves there; R2s needs R1 and t at the same horizon.
# k) Wilson 95 pct bounds on known values.
import importlib.util, os, sys, io, json, tempfile, traceback, contextlib
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('lead_null_v1_1_to20251231', os.path.join(HERE, 'lead_null_v1_1_to20251231.py'))
T = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(T)
assert 'event_outcomes' not in sys.modules and 'labcore' not in sys.modules, 'the tool imported EO or labcore at import time'
DAY = 86400; NAN = float('nan')


def synth_t(n_days, per_day, fires_per_wave=2, start=None):
    start = T.T_FIRST if start is None else start
    return np.array([start + d * DAY + k * 7200 + 60 * j for d in range(n_days) for k in range(per_day) for j in range(fires_per_wave)], np.int64)


def months_of(day_num):
    return T.utc_month(T.T_FIRST + np.asarray(day_num, np.int64) * DAY)


def test_a():
    t = synth_t(60, 10); n = len(t); wave = T.wave_ids(t)
    assert wave.max() + 1 == 600, wave.max()
    df = np.repeat(np.arange(n), 2); dw = np.full(2 * n, 0.5)
    rl = T.fire_random_share(df, dw, np.tile([1.0, 0.0], n), n); ro = T.fire_random_share(df, dw, np.tile([0.0, 1.0], n), n)
    WT = T.wave_table(t, wave, {h: (np.ones(n), np.zeros(n), rl, ro) for h in ('15m', '1h')})
    assert np.all(WT['d']['15m'] == 100.0) and np.all(WT['d']['1h'] == 100.0)
    P = T.prepare(WT['day_num'], WT['month'], WT['d']['15m'], WT['d']['1h'])
    R = T.real_stats(P)
    for h in ('15m', '1h'):
        assert R['st'][h]['lead'][0] == 100.0 and R['st'][h]['t'][0] == np.inf, (h, R['st'][h])
    assert R['rules']['counted'] == 3 and R['rules']['counted_15m'] == 3 and R['rules']['counted_1h'] == 3 and int(R['rules']['passing'][0]) == 3
    for r in T.RULES:
        assert bool(R['rules'][r][0]), r
    rates = T.null_power(P, 1000, T.SEED)
    want = {'flat': {0: 0.0, 3: 1.0, 5: 1.0, 7: 1.0}, '1h_only': {0: 0.0, 3: 1.0, 5: 1.0, 7: 1.0}}
    for L in T.BLOCKS:
        for shape, exp in want.items():
            for r in T.RULES:
                for d, e in exp.items():
                    assert rates[(shape, L, r, d)][1] == e, (shape, L, r, d, rates[(shape, L, r, d)])
        # by_month x0.5 Sep, x1.5 Oct, x0.5 Nov: delta 3 and 5 pass only October (R1 fails), delta 7 passes all three months
        for r in T.RULES:
            for d, e in ((0, 0.0), (3, 0.0 if r in ('R1', 'R2', 'R2s') else 1.0), (5, 0.0 if r in ('R1', 'R2', 'R2s') else 1.0), (7, 1.0)):
                assert rates[('by_month', L, r, d)][1] == e, ('by_month', L, r, d, rates[('by_month', L, r, d)])
    print('   a) real lead +100, t inf, R1 R2 R2s R3 R4 pass; centred null: power 0 at delta 0, 1.0 at 3/5/7 (flat, 1h_only), by_month as expected, blocks 1/3/7')


def test_b():
    rng = np.random.default_rng(7); n = 1200
    day = np.repeat(np.arange(120), 10); month = np.array(['2509', '2510', '2511', '2512'])[day // 30]
    d15, d60 = rng.normal(0, 50, n), rng.normal(0, 50, n)
    P = T.prepare(day, month, d15, d60); rates = T.null_power(P, 10000, T.SEED, shapes=('flat',))
    for L in T.BLOCKS:
        x = rates[('flat', L, 'R3', 0)]
        print('   b) block %d: false pass at delta 0: %s | R3 power d3/5/7 %s' % (L, ' '.join('%s %.4f [hi95 %.4f]' % (r, rates[('flat', L, r, 0)][1], rates[('flat', L, r, 0)][3]) for r in T.RULES),
                                                                             '/'.join('%.3f' % rates[('flat', L, 'R3', d)][1] for d in T.DELTAS[1:])))
        assert x[1] <= 0.01, (L, x)
        for r in ('R3', 'R4'):
            v = [rates[('flat', L, r, d)][1] for d in T.DELTAS]; assert v == sorted(v), (L, r, v)
    P2 = T.prepare(day, month, d15 + 20.0, d60 - 15.0); r2 = T.null_power(P2, 10000, T.SEED, shapes=('flat',))
    for k in rates:
        assert abs(rates[k][1] - r2[k][1]) <= 0.0005, (k, rates[k], r2[k])
    print('   b) shifting the real lead (+20 at 15m, -15 at 1h) leaves every null and power rate unchanged (within 0.0005)')


def make_world(V='X', drop_list=0):
    """a tiny W: 6 fires (Sep 10-12 2025, 2 per day, 2 h apart = 6 waves), a fire at 2025-12-31 23:30 and one on 2026-01-02; 4 edges
    per fire (first 3 kept); alarm lean FADE always wins (fire 0 has no 15m outcome); random draw k=0 FADE wins, k=1,2 FOLLOW wins
    -> e_f = +133.33 points. drop_list removes that many RND list rows (store and weights kept) to force unmatched draws."""
    W = tempfile.mkdtemp(prefix='lead_null_test_')
    fires = [('AAA' if i % 2 == 0 else 'BBB', T.T_FIRST + (i // 2) * DAY + (i % 2) * 7200 + 3600, 1 if i % 2 == 0 else -1) for i in range(6)]
    last_hour = ('AAA', T.T_CUT + 1800, 1); late = ('AAA', T._epoch('20260102') + 3600, 1); allf = fires + [last_hour, late]
    with open(os.path.join(W, '%s_FIRES_V1_LIST.tsv' % V), 'w') as f:
        f.write('coin\tt\tside\tonset_t\n' + ''.join('%s\t%d\t%d\t%d\n' % (c, t, s, t) for c, t, s in allf))
    E = ['fid\tcoin\tparent_t\tcand_t\tside\tweight\tdraw_index\town\n']; L = []; Wt = []; rs = []
    for c, t, s in allf:
        for k in range(4):
            ct = t + DAY + 600 * k + 0.5
            E.append('%s_%d\t%s\t%d.0\t%.4f\t%d\t0.25\t%d\t\n' % (c, t, c, t, ct, s, k))
            if k < 3 and (c, t, s) in fires:
                L.append((c, int(ct), s)); Wt.append((c, int(ct), 1.0 / 3)); rs.append((c, int(ct), k))
    os.makedirs(os.path.join(W, 'gradeL_%s_v1' % V, 'matches'))
    open(os.path.join(W, 'gradeL_%s_v1' % V, 'matches', 'EDGES.tsv'), 'w').write(''.join(E))
    open(os.path.join(W, 'RND_%s_V1_LIST.tsv' % V), 'w').write('coin\tt\tside\n' + ''.join('%s\t%d\t%d\n' % x for x in L[drop_list:]))
    open(os.path.join(W, 'RND_%s_V1_WEIGHTS.tsv' % V), 'w').write('coin\tt\tweight\n' + ''.join('%s\t%d\t%.6f\n' % x for x in Wt))
    open(os.path.join(W, 'SUM_%s.tsv' % V), 'w').write('key\tvalue\n2c<1c 15m a 2509\t100.0\n2c<1c 15m r 2509\t33.3\n2c<1c 1h a 2509\t100.0\n2c<1c 1h r 2509\t33.3\n')
    A = {'coin': np.array([c for c, _, _ in allf]), 't': np.array([t for _, t, _ in allf], np.int64)}   # the fake store ignores the window
    for h, lab, _ in T.HORIZONS:
        A['%s__FADE' % lab] = np.ones(len(allf)); A['%s__FOLLOW' % lab] = np.zeros(len(allf))
    A['OFFER2C_BEFORE_HEAT1C_15M__FADE'][0] = NAN
    R = {'coin': np.array([c for c, _, _ in rs]), 't': np.array([t for _, t, _ in rs], np.int64)}
    for h, lab, _ in T.HORIZONS:
        R['%s__FADE' % lab] = np.array([1.0 if k == 0 else 0.0 for _, _, k in rs]); R['%s__FOLLOW' % lab] = np.array([0.0 if k == 0 else 1.0 for _, _, k in rs])
    stores = {os.path.join(W, 'om_%s_v1' % V): A, os.path.join(W, 'om_%sRND_v1' % V): R}

    def read_store(root, subj, cols):
        o = stores[root]; return {k: np.array(v) for k, v in o.items() if k in ('coin', 't') or k in cols}
    row = {'V': V, 'lean': 'FADE', 'W': W, 'subj_alarm': 'IDEA2%sMENU' % V, 'subj_rnd': 'IDEA2%sRNDMENU' % V}
    return W, row, read_store


def test_c():
    W, row, rs = make_world()
    res = T.run_version(row, rs, T.wave_ids, 50, T.SEED, log=lambda *a: None)
    c = res['counts']
    assert res['status'] == 'OK', res.get('error', res['status'])
    exp = {'fires_list_outside': 1, 'alarm_store_outside': 1, 'fires_last_hour_dropped': 1, 'edges_parent_outside': 4, 'edges_parent_last_hour': 4,
           'fires': 6, 'fires_dropped_15m': 1, 'fires_dropped_1h': 0, 'waves_15m': 5, 'waves_1h': 6, 'draws_kept': 18, 'draws_unmatched': 0}
    for k, v in exp.items():
        assert c[k] == v, (k, c[k], v)
    assert abs(res['real']['st']['15m']['lead'] - 400.0 / 3) < 1e-9, res['real']['st']['15m']
    for bad_t in (T._epoch('20260102'), T.T_CUT + 1800, T.T_FIRST - 1):
        try:
            T.wave_table(np.array([bad_t], np.int64), np.array([0]), {})
            raise AssertionError('a fire at %d did not raise' % bad_t)
        except T.WindowError:
            pass
    T.assert_window(np.array([T.T_FIRST, T.T_CUT - 1], np.int64), 'test', T.T_CUT)   # 00:00:00 Sep 10 and 22:59:59 Dec 31 are inside
    print('   c) dropped and counted: Jan 2 fire (list 1, store 1, edges 4), Dec 31 23:30 fire (1, edges 4), 15m complete-case drop 1; outside rows raise')


def test_d():
    WT = T.wave_table(np.array([T.T_FIRST + 5, T.T_FIRST + 3 * DAY + 5], np.int64), np.array([0, 1]), {})
    assert list(WT['day_num']) == [0, 3], WT['day_num']                       # grid day 0 = 2025-09-10
    day = np.repeat([0, 1, 2, 3, 6, 7, 13, 14, 20, 21], 2); month = months_of(day)
    d15 = np.ones(len(day)); d60 = np.ones(len(day)); d60[0] = NAN; d15[5] = NAN   # different finite sets per horizon
    P = T.prepare(day, month, d15, d60)
    for L in T.BLOCKS:
        S = T.flip_signs(T.n_blocks(P, L), 300, T.SEED)
        assert np.array_equal(S, T.flip_signs(T.n_blocks(P, L), 300, T.SEED)), 'seed not fixed'
        sign = {}
        for h in ('15m', '1h'):
            Hh = P['H'][h]; D = T.flip_matrix(Hh, S, L, np.zeros(Hh['N']), centered=False); blk = Hh['dn'] // L
            for b in np.unique(blk):
                col = np.sign(D[:, blk == b]); assert np.all(col == col[:, :1]), (L, h, b); sign[(h, int(b))] = col[:, 0]
            for x, y, same in ((0, L - 1, True), (L - 1, L, False)):
                if x in Hh['dn'] and y in Hh['dn']:
                    sx = np.sign(D[:, Hh['dn'] == x][:, 0]); sy = np.sign(D[:, Hh['dn'] == y][:, 0])
                    assert np.array_equal(sx, sy) if same else not np.array_equal(sx, sy), (L, h, x, y)
        for (h, b), s in sign.items():
            if ('1h', b) in sign:
                assert np.array_equal(s, sign[('1h', b)]), (L, b)
        assert 0.35 < (S > 0).mean() < 0.65
    print('   d) blocks 1/3/7 from 2025-09-10: one sign per block, the same at 15m and 1h; block edges where expected; seed fixed')


def test_e():
    W = tempfile.mkdtemp(prefix='lead_null_pair_'); t0 = T.T_FIRST + 5 * DAY; t1 = t0 + 7200; t2 = t0 + 4 * 7200; t3 = t0 + 6 * 7200
    rows = [('AAA', t0, t0 + 1000.7, 1, 0, ''), ('AAA', t0, t0 + 1500.0, 1, 1, 'OWN'), ('AAA', t0, t0 + 2000.2, 1, 2, ''),
            ('AAA', t0, t0 + 3000.0, 1, 3, ''), ('AAA', t0, t0 + 4000.0, 1, 4, ''), ('BBB', t1, T.T_END + 100.0, -1, 0, ''), ('BBB', t1, t1 + 500.0, -1, 1, ''),
            ('CCC', t2, t2 + 700.0, 1, 0, ''), ('CCC', t2, t2 + 800.0, 1, 1, ''), ('DDD', t3, T.T_CUT + 60.0, 1, 0, ''), ('DDD', t3, T.T_CUT - 2.0, 1, 1, '')]
    with open(os.path.join(W, 'EDGES.tsv'), 'w') as f:
        f.write('fid\tcoin\tparent_t\tcand_t\tside\tweight\tdraw_index\town\n')
        for c, p, ct, s, di, own in rows:
            f.write('%s_%d\t%s\t%d.0\t%r\t%d\t0.1\t%d\t%s\n' % (c, p, c, p, ct, s, di, own))
    lst = [('AAA', t0 + 1000, 1), ('AAA', t0 + 2000, -1), ('AAA', t0 + 2001, 1), ('BBB', t1 + 500, -1), ('CCC', t2 + 704, 1), ('CCC', t2 + 803, 1), ('DDD', T.T_CUT + 1, 1)]
    open(os.path.join(W, 'LIST.tsv'), 'w').write('coin\tt\tside\n' + ''.join('%s\t%d\t%d\n' % x for x in lst))
    E, ce = T.read_edges(os.path.join(W, 'EDGES.tsv')); idx, cl = T.read_rnd_list(os.path.join(W, 'LIST.tsv'))
    assert ce['edges_own_skipped'] == 1 and ce['edges_parent_outside'] == 0 and cl['rnd_list_outside'] == 0, (dict(ce), dict(cl))
    df, dc, dt_, dw, cp = T.pair_draws(np.array(['AAA', 'BBB', 'CCC', 'DDD']), np.array([t0, t1, t2, t3], np.int64), np.array([1, -1, 1, 1]), E, idx)
    assert list(df) == [0, 0, 1, 2] and list(dt_) == [t0 + 1000, t0 + 2001, t1 + 500, t2 + 803], (list(df), list(dt_))
    assert np.allclose(dw, [1 / 3, 1 / 3, 0.5, 0.5]), dw
    exp = {'draws_kept': 9, 'draws_unmatched': 2, 'draws_cand_outside': 1, 'draws_cand_last_hour': 2, 'edges_beyond_first3': 1}
    for k, v in exp.items():
        assert cp[k] == v, (k, cp[k], v)
    print('   e) +1 s and +3 s matched, +4 s unmatched (2 unmatched in all), own skipped, beyond first 3: 1, outside 1, after 22:59:59: 2 (one by the shift)')


def test_f():
    month = np.array(['2509', '2509', '2509', '2510']); w = np.array([0.5, 0.5, 1.0, 1.0]); x = np.array([1.0, 0.0, NAN, 1.0])
    s = T.month_share(month, w, x, ('2509', '2510', '2511'))
    assert s['2509'] == 50.0 and s['2510'] == 100.0 and s['2511'] != s['2511'], s
    ours = {'k a 2509': 50.0, 'k a 2510': 100.0, 'k a 2511': NAN}
    ok, rows = T.gate_check(ours, {'k a 2509': '50.1', 'k a 2510': '99.9'}); assert ok, rows
    ok, rows = T.gate_check(ours, {'k a 2509': '50.2', 'k a 2510': '100.0'}); assert not ok and [r[4] for r in rows][:2] == ['MISS', 'OK'], rows
    ok, rows = T.gate_check(ours, {}); assert not ok and all(r[4] == 'SKIP' for r in rows), rows
    ok, rows = T.gate_check(ours, {'k a 2509': '50.0', 'k a 2511': 'na'}); assert ok, rows
    print('   f) gate: within 0.15 passes, 0.2 fails, missing skipped, nothing checked fails, nan equals nan')


def test_g():
    Wy, ry, sy = make_world('Y'); Wz, rz, sz = make_world('Z', drop_list=1); stores = {'Y': sy, 'Z': sz}
    def rs(root, subj, cols):
        return stores['Y' if root.startswith(Wy) else 'Z'](root, subj, cols)
    out = os.path.join(tempfile.mkdtemp(prefix='lead_null_cli_'), 'OUT'); man = os.path.join(Wy, 'INPUTS_TEST.tsv')
    open(man, 'w').write('# test manifest\nV\tlean\tW\tsubj_alarm\tsubj_rnd\tw2509\nY\tFADE\t%s\tIDEA2YMENU\tIDEA2YRNDMENU\t6\nZ\tFADE\t%s\tIDEA2ZMENU\tIDEA2ZRNDMENU\t6\n' % (Wy, Wz))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = T.main(['--manifest', man, '--out', out, '--flips', '200'], backend=(rs, T.wave_ids))
    so = buf.getvalue(); assert rc == 0, (rc, so)
    for fn in ('RESULTS_Y.tsv', 'GATE_Y.tsv', 'SUMMARY.tsv', 'RECEIPT.json', 'REAL_SEALED/REAL_Y.tsv', 'REAL_SEALED/REAL_RULES_Y.tsv'):
        p = os.path.join(out, fn); assert os.path.exists(p), fn
        if fn.endswith('.tsv'):
            l0 = open(p).readline(); assert l0.startswith('# lead_null_v1_to20251231') and 'TEST, NOT REVIEWED' in l0, (fn, l0)
    assert not os.path.exists(os.path.join(out, 'REAL_Y.tsv')) and not os.path.exists(os.path.join(out, 'RESULTS_Z.tsv'))
    sealed = '133.3'
    assert sealed in open(os.path.join(out, 'REAL_SEALED', 'REAL_Y.tsv')).read()
    for txt, nm in ((so, 'stdout'), (open(os.path.join(out, 'SUMMARY.tsv')).read(), 'SUMMARY'), (open(os.path.join(out, 'RECEIPT.json')).read(), 'RECEIPT'),
                    (open(os.path.join(out, 'RESULTS_Y.tsv')).read(), 'RESULTS')):
        assert sealed not in txt, 'the real lead leaked into %s' % nm
    res = [l.rstrip('\n').split('\t') for l in open(os.path.join(out, 'RESULTS_Y.tsv')) if not l.startswith('#')]
    assert res[0] == ['shape', 'deciding', 'block_days', 'rule', 'delta', 'passes', 'pass_rate', 'lo95', 'hi95', 'flips'] and len(res) == 1 + 3 * 3 * 5 * 4, len(res)
    assert all(float(r[7]) <= float(r[6]) <= float(r[8]) for r in res[1:])
    sm = [l.rstrip('\n').split('\t') for l in open(os.path.join(out, 'SUMMARY.tsv')) if not l.startswith('#')]; hd = sm[0]
    assert not any(h.startswith('lead') or h.startswith('t_') or h.startswith('real') for h in hd), hd
    rows = {r[0]: dict(zip(hd, r)) for r in sm[1:]}
    assert rows['Y']['status'] == 'OK' and rows['Y']['waves_2509'] == '6' and rows['Y']['manifest_w2509'] == '6' and rows['Y']['waves15_2509'] == '5', rows['Y']
    assert rows['Z']['status'] == 'MATCH_FAIL' and rows['Z']['match_fail_pct'] == '5.556', rows['Z']
    assert 'MATCH_FAIL' in so
    rec = json.load(open(os.path.join(out, 'RECEIPT.json')))
    assert rec['seed'] == 20261029 and rec['flips'] == 200 and rec['blocks'] == [1, 3, 7] and rec['versions']['Y']['counts']['fires_last_hour_dropped'] == 1, rec
    for argv in (['--manifest', man, '--out', out], ['--manifest', man, '--out', out + '2', '--only', 'NOPE']):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                T.main(argv, backend=(rs, T.wave_ids))
            raise AssertionError('not refused: %s' % argv)
        except SystemExit:
            pass
    assert T.main.__defaults__ is not None and '--flips' in open(T.__file__).read() and T.FLIPS == 10000
    print('   g) cli: RESULTS 180 rows with Wilson bounds, REAL_SEALED/ only place with the real lead, Z MATCH_FAIL (5.556 pct), refusals ok')


def ref_stats(P, h, S, L, delta, shape, centered):
    """wave-level reference, written independently of the tool's day-level code"""
    Hh = P['H'][h]; d = Hh['d'] - (Hh['center'] if centered else 0.0); labs = P['months'][Hh['mi']]
    if shape == 'flat':
        dw = np.full(len(d), float(delta))
    elif shape == '1h_only':
        dw = np.full(len(d), float(delta) if h == '1h' else 0.0)
    else:
        dw = np.array([delta * (0.5 if int(str(m)[2:]) % 2 else 1.5) for m in labs])
    D = d[None, :] * S[:, Hh['dn'] // L] + dw[None, :]
    lead = D.mean(axis=1); N = len(d); days = np.unique(Hh['dn']); G = len(days)
    C = np.stack([(D[:, Hh['dn'] == g] - lead[:, None]).sum(axis=1) for g in days], 1)
    se = np.sqrt(G / (G - 1.0) * (C ** 2).sum(axis=1)) / N
    ml = np.stack([D[:, Hh['mi'] == k].mean(axis=1) if np.any(Hh['mi'] == k) else np.full(len(S), NAN) for k in range(len(P['months']))], 1)
    return D, dw, {'lead': lead, 'se': se, 't': lead / se, 'mlead': ml}


def test_h():
    rng = np.random.default_rng(11); n = 400; day = np.sort(rng.integers(0, 113, n)); month = months_of(day)
    d15 = rng.normal(2, 40, n); d60 = rng.normal(-1, 40, n); d15[rng.random(n) < 0.1] = NAN; d60[rng.random(n) < 0.1] = NAN
    P = T.prepare(day, month, d15, d60); k = 0
    for L in T.BLOCKS:
        S = T.flip_signs(T.n_blocks(P, L), 50, 5)
        for shape in T.SHAPES:
            for delta in (0.0, 3.0, 5.5):
                for centered in (True, False):
                    ev = T.evaluate(P, S, L, delta, shape, centered)
                    for h in ('15m', '1h'):
                        D, dw, ref = ref_stats(P, h, S, L, delta, shape, centered)
                        assert np.allclose(T.delta_waves(P, h, delta, shape), dw)
                        assert np.allclose(T.flip_matrix(P['H'][h], S, L, dw, centered), D)
                        for key in ('lead', 'se', 't', 'mlead'):
                            assert np.allclose(ev['st'][h][key], ref[key], rtol=1e-9, atol=1e-9, equal_nan=True), (L, shape, delta, centered, h, key)
                        k += 1
    print('   h) day-level statistics = wave-level reference in %d cases (3 blocks x 3 shapes x 3 deltas x centred or not x 2 horizons)' % k)


def test_i():
    t = np.array([T.T_FIRST + 3600, T.T_FIRST + 3660, T.T_FIRST + 3 * 3600], np.int64); wave = T.wave_ids(t)
    assert list(wave) == [0, 0, 1]
    al, ao = np.array([1.0, 0.0, 1.0]), np.zeros(3)
    WT = T.wave_table(t, wave, {'15m': (al, ao, np.array([0.5, 0.25, NAN]), np.array([NAN, 0.5, 0.5])), '1h': (al, ao, np.full(3, 0.5), np.full(3, 0.5))})
    assert WT['d']['15m'][0] == 25.0 and np.isnan(WT['d']['15m'][1]) and WT['fires_dropped']['15m'] == 2, (WT['d'], WT['fires_dropped'])
    assert list(WT['d']['1h']) == [50.0, 100.0] and WT['fires_dropped']['1h'] == 0, WT['d']['1h']
    print('   i) complete cases: wave 1 lead 25.0 from its one complete fire (a wave-level mean would give 62.5); wave 2 dropped; 2 fires dropped')


def test_j():
    day, month, d15, d60 = [], [], [], []
    for lab, day0, m15, m60, k15, k60 in (('2509', 0, 5.0, 10.0, 2, 1), ('2510', 21, 0.0, 10.0, 2, 2), ('2511', 52, 5.0, 0.0, 2, 2), ('2512', 82, 10.0, 0.0, 1, 2)):
        for i in range(20):
            s = 100.0 if i % 2 == 0 else -100.0
            for j in range(2):
                day.append(day0 + i); month.append(lab); d15.append(m15 + s if j < k15 else NAN); d60.append(m60 if j < k60 else NAN)
    P = T.prepare(np.array(day), np.array(month), np.array(d15), np.array(d60)); R = T.real_stats(P); r = R['rules']
    assert r['counted_15m'] == 3 and r['counted_1h'] == 3 and r['counted'] == 4 and int(r['passing'][0]) == 3, r
    t15, t60 = R['st']['15m']['t'][0], R['st']['1h']['t'][0]
    assert t15 < 3 <= t60, (t15, t60)
    assert bool(r['R1'][0]) and bool(r['R2'][0]) and not bool(r['R2s'][0]) and bool(r['R3'][0]) and bool(r['R4'][0]), r
    print('   j) months: 15m counts Sep-Nov, 1h counts Oct-Dec, 4 counted, 3 pass (Dec 15m lead 10 not counted); t15 %.2f, t1h %.2f: R2 passes, R2s does not' % (t15, t60))


def test_k():
    lo, hi = T.wilson(0, 10000); assert lo == 0.0 and abs(hi - 0.000384) < 2e-6, (lo, hi)
    lo, hi = T.wilson(5000, 10000); assert abs(lo - 0.4902) < 1e-4 and abs(hi - 0.5098) < 1e-4, (lo, hi)
    lo, hi = T.wilson(10000, 10000); assert hi == 1.0 and abs(lo - (1 - 0.000384)) < 2e-6, (lo, hi)
    print('   k) Wilson 95 pct: 0/10000 -> [0, 0.000384], 5000/10000 -> [0.4902, 0.5098], 10000/10000 -> [0.999616, 1]')


if __name__ == '__main__':
    bad = 0
    TESTS = (('a planted', test_a), ('b null', test_b), ('c window', test_c), ('d blocks', test_d), ('e pairing', test_e), ('f gate', test_f),
             ('g cli', test_g), ('h fast = reference', test_h), ('i complete cases', test_i), ('j months and R2s', test_j), ('k wilson', test_k))
    for name, fn in TESTS:
        try:
            fn(); print('PASS', name)
        except Exception:
            bad += 1; print('FAIL', name); traceback.print_exc()
    print('%d of %d passed' % (len(TESTS) - bad, len(TESTS)))
    sys.exit(1 if bad else 0)
