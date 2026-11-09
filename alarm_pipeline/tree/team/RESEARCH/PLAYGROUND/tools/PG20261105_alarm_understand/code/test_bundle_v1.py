#!/usr/bin/env python3
"""test_bundle_v1.py (SCO-A136 for SCOUT, 6 Nov 2026, playground PG20261105_alarm_understand). TEST, NOT REVIEWED.
Unit tests B1 to B9 of the bundle builder (bundle_builder_v1.py, `alarm_understand_v1.py bundle`), written BEFORE the builder, on
planted synthetic data only (a planted runner tree, GRADE receipts, fire list and PERFIRE file; planted reader outputs). No market
data, no lab day, no store is read. The smallest test per piece, with its edge cases.
Run:  python3 -B test_bundle_v1.py [B1 B2 ...]      (all when none named)
Env:  BB_TOOL = the builder file to test (default bundle_builder_v1.py beside this file; a mutant copy for the mutant runs)
      AU_SCRATCH = where planted inputs go (default ../scratch, kept, never removed)
Exit 0 all passed, 1 a test failed."""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, importlib.util, os, subprocess, traceback
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.environ.get('BB_TOOL') or os.path.join(HERE, 'bundle_builder_v1.py')
AUT = os.path.join(HERE, 'alarm_understand_v1.py')
SCRATCH = os.environ.get('AU_SCRATCH') or os.path.join(os.path.dirname(HERE), 'scratch')
_spec = importlib.util.spec_from_file_location('bundle_builder_under_test', TOOL)
BB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BB)
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
JOBID = '90000001'
JNAME = '90000001_judge_SCOUT_GRADE_PLANT'
J = '90000001_GRADE_PLANT'
ALARM = 'PLANT/V1'
_N = [0]


def T(day, sec=0):
    d = dt.datetime.strptime(str(day), '%Y%m%d').replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp()) + int(sec)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'x') as f:
        f.write(text)
    return p


FIRES0 = [('AAA', T(20250915, 3600), -1), ('BBB', T(20250915, 3900), -1), ('CCC', T(20251002, 100), 1),
          ('AAA', T(20251110, 7200), -1), ('DDD', T(20251205, 50), 1)]


def plant(name, fires=FIRES0, perfire_fires=None, status='exit=0', title='JOB_GRADE_V14', end_rc='0', seal_j=J,
          list_header='coin\tt\tside\tS', extra_job=False, dv_line='W=$ROOT/w/$J; DV=$RD/receipts/$J', list_n=None,
          true_row=None):
    """a planted runner tree + GRADE receipts + W; -> dict(root, runner, dv, list, perfire)"""
    _N[0] += 1
    root = os.path.join(SCRATCH, 'bb_%s_%02d_%s' % (STAMP, _N[0], name))
    runner = os.path.join(root, 'runner'); rd = os.path.join(root, 'rd'); dv = os.path.join(rd, 'receipts', J)
    w = os.path.join(root, 'w', J)
    write(os.path.join(runner, 'Q_V1', 'DONE', JNAME + '.job.sh'),
          '# JOB %s -- planted (test_bundle_v1)\n# TITLE: %s -- SCOUT (ALARM_DESIGN KIT_V5 %s; planted)\nset -u\n'
          'ROOT=%s; RD=%s; T=x; J=%s\n%s\n' % (JNAME, J, title, root, rd, J, dv_line))
    if extra_job:
        write(os.path.join(runner, 'Q_V2', 'DONE', JOBID + '_judge_OTHER.job.sh'), '# JOB other\n')
    if status is not None:
        write(os.path.join(runner, 'Q_V1', 'logs', JNAME + '.status'), 'job=%s\n%s\nstarted=1\nended=2\n' % (JNAME, status))
    lst = os.path.join(w, 'V1_FIRES_V1_LIST.tsv')
    write(lst, list_header + '\n' + ''.join('%s\t%d\t%d\t9.9\n' % f for f in fires))
    pf = perfire_fires if perfire_fires is not None else fires
    rows = ['kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc']
    for c, t, s in pf:
        rows.append('A\t%s\t%d\t0\t0\t0\t%d\t0\t1\t1\t0.2' % (c, t, s))
    rnd = [('RRR', t + 77, s) for c, t, s in pf]
    for c, t, s in rnd:
        rows.append('R\t%s\t%d\t0\t0\t0\t%d\t0\t1\t1\t0.2' % (c, t, s))
    perf = write(os.path.join(w, 'PERFIRE_V1.tsv'), '\n'.join(rows) + '\n')
    write(os.path.join(dv, 'STAGES.tsv'), 'stage\trc\tseconds\tutc\tnote\nstart\t0\t0\tx\t\nend\t%s\t0\tx\t\n' % end_rc)
    write(os.path.join(dv, 'FIRES.tsv'), 'V1\t%d\t%s\t%s\n' % (list_n if list_n is not None else len(fires), sha16(lst), lst))
    allt = [t for c, t, s in pf] + [t for c, t, s in rnd]
    write(os.path.join(dv, 'PERFIRE_SEAL.tsv'), 'V1\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n' % (
        sha16(perf), len(pf), len(rnd), min(allt), max(allt), len(pf) + len(rnd), seal_j))
    tr = None
    if true_row is not None:
        tr = write(os.path.join(root, 'TRUE_ROW.tsv'), 'id\tverdict\tdef_sha16\tperfire_sha16\nX\tNOT SUPPORTED\t%s\t%s\n' % (
            true_row.get('def', 'dddddddddddddddd'), true_row.get('perfire', sha16(perf))))
    return dict(root=root, runner=runner, dv=dv, list=lst, perfire=perf, true_row=tr)


def args(P, out_name='BUNDLE', block='SEPDEC', extra=()):
    out = os.path.join(P['root'], out_name)
    return BB.parse(['bundle', out, '--from-job', JOBID, '--runner', P['runner'], '--alarm', ALARM, '--block', block] + list(extra)), out


def refused(fn, code):
    try:
        fn()
    except Exception as e:
        got = getattr(e, 'code', None)
        assert got == code, 'expected REFUSED %s, got %s: %s' % (code, got, e)
        return str(e)
    raise AssertionError('expected REFUSED %s, nothing refused' % code)


def rows(p):
    L = [l.rstrip('\n').split('\t') for l in open(p) if not l.startswith('#')]
    return [dict(zip(L[0], r)) for r in L[1:]]


def no_reader(*a, **k):
    raise AssertionError('a reader was called')


# ---------------------------------------------------------------------------------------------------- B1 the GRADE join, happy path
def test_B1():
    P = plant('b1')
    a, out = args(P)
    res = BB.build(a, readers=dict(ctx=no_reader, epi=no_reader, gg=no_reader))
    F = rows(os.path.join(out, 'FIRES.tsv'))
    assert [(r['alarm_id'], r['coin'], int(r['t']), int(r['side'])) for r in F] == [(ALARM, c, t, s) for c, t, s in FIRES0], F
    for nm in ('READINGS.tsv', 'FORCED.tsv', 'MONEY.tsv'):
        assert not os.path.exists(os.path.join(out, nm)), nm + ' written without a source'
    src = rows(os.path.join(out, 'BUNDLE_SOURCES.tsv'))
    roles = {r['role']: r for r in src}
    assert roles['FIRE_LIST']['sha16'] == sha16(P['list']) and roles['PERFIRE']['sha16'] == sha16(P['perfire']), roles
    assert roles['MONEY']['rows'] == '0' and 'race grade' in roles['MONEY']['note'], roles['MONEY']
    notes = open(os.path.join(out, 'BUNDLE_NOTES.md')).read()
    assert 'DIMS_V2' in notes and 'NOT BUILT' in notes, notes
    assert res['fires'] == 5 and res['closed_dropped'] == 0, res


# ---------------------------------------------------------------------------------------------------- B2 the job: refusals
def test_B2():
    P = plant('b2a')
    refused(lambda: BB.build(BB.parse(['bundle', os.path.join(P['root'], 'O'), '--from-job', '90000002', '--runner', P['runner'],
                                       '--alarm', ALARM, '--block', 'SEPDEC'])), 'NO_JOB')
    refused(lambda: BB.build(BB.parse(['bundle', os.path.join(P['root'], 'O'), '--from-job', '9000x', '--runner', P['runner'],
                                       '--alarm', ALARM, '--block', 'SEPDEC'])), 'BAD_ARGS')
    P = plant('b2b', extra_job=True); refused(lambda: BB.build(args(P)[0]), 'JOB_AMBIGUOUS')
    P = plant('b2c', status='exit=3'); refused(lambda: BB.build(args(P)[0]), 'JOB_NOT_OK')
    P = plant('b2d', status=None); refused(lambda: BB.build(args(P)[0]), 'NO_STATUS')
    P = plant('b2e', title='JOB_TRUE_V1'); refused(lambda: BB.build(args(P)[0]), 'NOT_A_GRADE_JOB')
    P = plant('b2f', dv_line='DV=$RD/other/$J'); refused(lambda: BB.build(args(P)[0]), 'NOT_A_GRADE_JOB')
    P = plant('b2g', end_rc='7'); refused(lambda: BB.build(args(P)[0]), 'GRADE_NOT_DONE')


# ---------------------------------------------------------------------------------------------------- B3 the receipts: refusals
def test_B3():
    P = plant('b3a'); open(P['list'], 'a').write('EEE\t%d\t1\t1\n' % T(20251201)); refused(lambda: BB.build(args(P)[0]), 'SOURCE_CHANGED')
    P = plant('b3b'); open(P['perfire'], 'a').write('R\tZZZ\t1\t0\t0\t0\t1\t0\t1\t1\t0.2\n'); refused(lambda: BB.build(args(P)[0]), 'SOURCE_CHANGED')
    P = plant('b3c', seal_j='90000009_GRADE_OTHER'); refused(lambda: BB.build(args(P)[0]), 'JOIN_MISMATCH')
    moved = [FIRES0[0]] + [('BBB', FIRES0[1][1] + 60, -1)] + FIRES0[2:]
    P = plant('b3d', perfire_fires=moved); refused(lambda: BB.build(args(P)[0]), 'JOIN_MISMATCH')
    flipped = FIRES0[:2] + [('CCC', FIRES0[2][1], -1)] + FIRES0[3:]
    P = plant('b3e', perfire_fires=flipped); refused(lambda: BB.build(args(P)[0]), 'JOIN_MISMATCH')
    P = plant('b3f', list_n=4); refused(lambda: BB.build(args(P)[0]), 'JOIN_MISMATCH')
    P = plant('b3g', list_header='t\tcoin\tside\tS'); refused(lambda: BB.build(args(P)[0]), 'BAD_INPUT')
    P = plant('b3h', fires=FIRES0 + [('AAA', FIRES0[0][1], -1)]); refused(lambda: BB.build(args(P)[0]), 'BAD_INPUT')
    P = plant('b3i', fires=FIRES0 + [('EEE', T(20251201), 0)]); refused(lambda: BB.build(args(P)[0]), 'BAD_INPUT')
    P = plant('b3j'); os.rename(P['list'], P['list'] + '.moved'); refused(lambda: BB.build(args(P)[0]), 'NO_INPUT')
    P = plant('b3k'); a, out = args(P); os.makedirs(out); refused(lambda: BB.build(a), 'OUT_EXISTS')


# ---------------------------------------------------------------------------------------------------- B4 alarm_context readings
def ctx_out(keys, vals, decision_s=0):
    n = len(keys)
    o = {'coin': np.array([k[0] for k in keys]), 't_alarm': np.array([float(k[1]) for k in keys]),
         't_decision': np.array([float(k[1] + decision_s) for k in keys])}
    for v, arr in vals.items():
        o[v] = np.asarray(arr, float)
    return o


def test_B4():
    keys = [(c, t) for c, t, s in FIRES0]
    calls = []

    def reader(root, code_dir, subject, first, last, values):
        calls.append((subject, first, last, tuple(values)))
        if subject == 'SUBJ':
            o0 = ctx_out(keys, {'hour_utc': [1, 2, 3, 4, 5]})
            o1 = ctx_out(keys, {'hour_utc': [11, 12, 13, 14, 15]}, decision_s=3600)
            return {k: np.concatenate([o0[k], o1[k]]) for k in o0}
        return ctx_out([('MMM', T(20250920)), ('NNN', T(20251020))], {'hour_utc': [7, np.nan]})
    P = plant('b4a')
    a, out = args(P, extra=['--ctx', '/planted/root', 'SUBJ', '--ctx-match', 'SUBJ_MATCH', '--lab3', '/planted/lab3', '--ctx-values', 'hour_utc'])
    BB.build(a, readers=dict(ctx=reader, epi=no_reader, gg=no_reader))
    R = rows(os.path.join(out, 'READINGS.tsv'))
    fire = [r for r in R if r['who'] == 'FIRE']; match = [r for r in R if r['who'] == 'MATCH']
    assert len(fire) == 10 and len(match) == 1, (len(fire), len(match))          # a NaN matched value is not a reading
    assert all(r['code'] == 'CTX.SUBJ.hour_utc' for r in R), R                    # MATCH rows under the fire subject's code name
    after = [r for r in fire if r['after'] == '1']
    assert len(after) == 5 and all(int(r['known_at']) == int(r['t']) + 3600 for r in after), after
    asof = {(r['coin'], int(r['t'])): float(r['value']) for r in fire if r['after'] == '0'}
    assert asof[keys[2]] == 3.0, asof
    assert calls[0][1] == 20250910 and calls[0][2] == 20251231, calls             # the block's days only
    # a fire the context lacks, and a context row with no fire: refused, never joined by guess
    def miss(root, code_dir, subject, first, last, values):
        return ctx_out(keys[:4], {'hour_utc': [1, 2, 3, 4]}) if subject == 'SUBJ' else ctx_out([], {'hour_utc': []})
    P = plant('b4b'); a, _ = args(P, extra=['--ctx', '/r', 'SUBJ', '--lab3', '/l', '--ctx-values', 'hour_utc'])
    refused(lambda: BB.build(a, readers=dict(ctx=miss)), 'JOIN_MISSING')
    def extra(root, code_dir, subject, first, last, values):
        return ctx_out(keys + [('ZZZ', T(20251003))], {'hour_utc': [1, 2, 3, 4, 5, 6]})
    P = plant('b4c'); a, _ = args(P, extra=['--ctx', '/r', 'SUBJ', '--lab3', '/l', '--ctx-values', 'hour_utc'])
    refused(lambda: BB.build(a, readers=dict(ctx=extra)), 'JOIN_EXTRA')
    def frac(root, code_dir, subject, first, last, values):
        o = ctx_out(keys, {'hour_utc': [1, 2, 3, 4, 5]}); o['t_alarm'] = o['t_alarm'] + 0.5; return o
    P = plant('b4d'); a, _ = args(P, extra=['--ctx', '/r', 'SUBJ', '--lab3', '/l', '--ctx-values', 'hour_utc'])
    refused(lambda: BB.build(a, readers=dict(ctx=frac)), 'BAD_INPUT')
    P = plant('b4e'); a, _ = args(P, extra=['--ctx', '/r', 'SUBJ', '--ctx-values', 'hour_utc'])
    refused(lambda: BB.build(a, readers=dict(ctx=reader)), 'BAD_ARGS')         # --ctx needs --lab3


# ---------------------------------------------------------------------------------------------------- B5 alarm_profile_v2_3: forced side and EPI readings
def test_B5():
    keys = [(c, t) for c, t, s in FIRES0]

    def epi(root, code_dir, subject, first, last, values):
        o = {'coin': np.array([k[0] for k in keys]), 't_alarm': np.array([float(k[1]) for k in keys]),
             'known_at_us': np.array([k[1] * 1000000 for k in keys], dtype=np.int64)}
        o['forced_usd_log'] = np.array([5.0, 4.0, 3.0, np.nan, 6.0]); o['other_usd_log'] = np.array([3.0, 0.0, 4.0, 2.0, 0.0])
        o['run_pct'] = np.array([4.0, 2.0, 1.0, 0.0, 3.0])
        return {k: v for k, v in o.items() if k in ('coin', 't_alarm', 'known_at_us') or k in values}
    P = plant('b5a')
    a, out = args(P, extra=['--epi', '/planted/root', 'ESUB', '--lab3', '/l', '--epi-values', 'run_pct'])
    BB.build(a, readers=dict(ctx=no_reader, epi=epi, gg=no_reader))
    Fo = {(r['coin'], int(r['t'])): r for r in rows(os.path.join(out, 'FORCED.tsv'))}
    r0 = Fo[keys[0]]; r2 = Fo[keys[2]]; r1 = Fo[keys[1]]; r3 = Fo[keys[3]]
    assert float(r0['long_usd']) == 1e5 and float(r0['short_usd']) == 1e3, r0          # side -1: the forced side is the longs (A1.S01)
    assert float(r2['short_usd']) == 1e3 and float(r2['long_usd']) == 1e4, r2          # side +1: the forced side is the shorts (A1.S02)
    assert float(r1['short_usd']) == 0.0, r1                                             # other_usd_log 0 = none (the catalog's unit)
    assert r3['long_usd'] == '' and float(r3['short_usd']) == 100.0, r3                 # unknown forced side stays empty, never 0
    R = rows(os.path.join(out, 'READINGS.tsv'))
    assert sorted({r['code'] for r in R}) == ['EPI.ESUB.run_pct'] and len(R) == 5, R
    assert all(r['after'] == '0' and r['who'] == 'FIRE' for r in R), R
    def short(root, code_dir, subject, first, last, values):
        o = epi(root, code_dir, subject, first, last, values); return {k: v[1:] for k, v in o.items()}
    P = plant('b5b'); a, _ = args(P, extra=['--epi', '/r', 'ESUB', '--lab3', '/l'])
    refused(lambda: BB.build(a, readers=dict(epi=short)), 'JOIN_MISSING')


# ---------------------------------------------------------------------------------------------------- B6 group_and_grade money (grouper_v1_10.Data)
class FakeData:
    def __init__(self, keys, flip=None):
        self.keys = [(c, str(t), str(s)) for c, t, s in keys]
        if flip is not None:
            c, t, s = self.keys[flip]; self.keys[flip] = (c, t, str(-int(s)))
        n = len(keys); ar = np.arange(n, dtype=float)
        self.P = {}
        for h, base in (('15m', 10.0), ('1h', 20.0), ('4h', 30.0)):
            self.P[('HOLD_%s' % h, 'FADE', 'GROSS')] = (base + ar, np.full(n, np.nan))
        self.P[('HOLD_1h', 'FADE', 'HONEST')] = (ar - 1.0, ar - 3.0)
        self.P[('HOLD_1h', 'FOLLOW', 'HONEST')] = (1.0 - ar, np.full(n, 0.5))


def test_B6():
    P = plant('b6a')
    a, out = args(P, extra=['--gg-run', '/planted/run', '--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'HOLD_1h', '--lean', 'FADE'])
    BB.build(a, readers=dict(ctx=no_reader, epi=no_reader, gg=lambda run, tools, costs: FakeData(FIRES0)))
    M = {(r['coin'], int(r['t'])): r for r in rows(os.path.join(out, 'MONEY.tsv'))}
    r = M[(FIRES0[2][0], FIRES0[2][1])]
    assert (float(r['fade_gross_15m']), float(r['fade_gross_1h']), float(r['fade_gross_4h'])) == (12.0, 22.0, 32.0), r
    assert float(r['net']) == 1.0 and float(r['edge_tough']) == 2.0 and r['exit'] == 'HOLD_1h' and r['after'] == '1', r
    assert int(r['side']) == 1, r
    P = plant('b6b'); a, _ = args(P, extra=['--gg-run', '/r', '--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'HOLD_1h', '--lean', 'FADE'])
    refused(lambda: BB.build(a, readers=dict(gg=lambda run, tools, costs: FakeData(FIRES0, flip=1))), 'JOIN_SIDE')
    P = plant('b6c'); a, _ = args(P, extra=['--gg-run', '/r', '--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'HOLD_1h', '--lean', 'FADE'])
    refused(lambda: BB.build(a, readers=dict(gg=lambda run, tools, costs: FakeData(FIRES0[:4]))), 'JOIN_MISSING')
    P = plant('b6d'); a, _ = args(P, extra=['--gg-run', '/r', '--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'FIXED_V1_4h', '--lean', 'FADE'])
    refused(lambda: BB.build(a, readers=dict(gg=lambda run, tools, costs: FakeData(FIRES0))), 'BAD_ARGS')
    P = plant('b6e'); a, out = args(P, extra=['--gg-run', '/r', '--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'HOLD_1h', '--lean', 'FOLLOW'])
    BB.build(a, readers=dict(gg=lambda run, tools, costs: FakeData(FIRES0)))
    r = {(x['coin'], int(x['t'])): x for x in rows(os.path.join(out, 'MONEY.tsv'))}[(FIRES0[0][0], FIRES0[0][1])]
    assert float(r['net']) == 1.0 and float(r['edge_tough']) == 0.5 and float(r['fade_gross_1h']) == 20.0, r   # FOLLOW net, FADE gross kept


# ---------------------------------------------------------------------------------------------------- B7 closed days and blocks
def test_B7():
    late = FIRES0 + [('EEE', T(20270102, 10), -1)]                  # a fire on a day lab3 law.py refuses
    P = plant('b7a', fires=late)
    a, out = args(P, extra=['--ctx', '/r', 'SUBJ', '--lab3', '/l', '--ctx-values', 'hour_utc'])
    keys = [(c, t) for c, t, s in FIRES0]
    res = BB.build(a, readers=dict(ctx=lambda root, code_dir, subject, first, last, values: ctx_out(keys, {'hour_utc': [1, 2, 3, 4, 5]})))
    F = rows(os.path.join(out, 'FIRES.tsv'))
    assert len(F) == 5 and res['closed_dropped'] == 1 and 'EEE' not in {r['coin'] for r in F}, (F, res)
    P = plant('b7b')
    a, _ = BB.parse(['bundle', os.path.join(P['root'], 'O'), '--from-job', JOBID, '--runner', P['runner'], '--alarm', ALARM,
                     '--block', '202701']), None
    refused(lambda: BB.build(a, readers=dict(ctx=no_reader, epi=no_reader, gg=no_reader)), 'BLOCK_CLOSED')
    assert not os.path.exists(os.path.join(P['root'], 'O'))
    a, _ = BB.parse(['bundle', os.path.join(P['root'], 'O2'), '--from-job', JOBID, '--runner', P['runner'], '--alarm', ALARM,
                     '--block', 'SEPX']), None
    refused(lambda: BB.build(a), 'BAD_BLOCK')


# ---------------------------------------------------------------------------------------------------- B8 TRUE_ROW binding and DIMS_V2
def test_B8():
    P = plant('b8a', true_row={})
    a, out = args(P, extra=['--true-row', P['true_row'], '--def-sha16', 'dddddddddddddddd'])
    BB.build(a, readers=dict(ctx=no_reader, epi=no_reader, gg=no_reader))
    assert rows(os.path.join(out, 'TRUE_ROW.tsv'))[0]['verdict'] == 'NOT SUPPORTED'
    P = plant('b8b', true_row={'perfire': '0123456789abcdef'})
    a, _ = args(P, extra=['--true-row', P['true_row'], '--def-sha16', 'dddddddddddddddd'])
    refused(lambda: BB.build(a), 'JOIN_MISMATCH')
    P = plant('b8c', true_row={'def': 'eeeeeeeeeeeeeeee'})
    a, _ = args(P, extra=['--true-row', P['true_row'], '--def-sha16', 'dddddddddddddddd'])
    refused(lambda: BB.build(a), 'SOURCE_CHANGED')
    P = plant('b8d', true_row={})
    a, _ = args(P, extra=['--true-row', P['true_row']])
    refused(lambda: BB.build(a), 'BAD_ARGS')                          # a TRUE_ROW needs the DEF sha16 it must bind
    P = plant('b8e')
    a, _ = args(P, extra=['--dims', '/planted/DIMENSIONS.tsv'])
    refused(lambda: BB.build(a), 'NOT_BUILT')


# ---------------------------------------------------------------------------------------------------- B9 end to end: bundle then card, by the command line
def test_B9():
    P = plant('b9a', true_row={})
    defp = write(os.path.join(P['root'], 'DEF.json'), '{"id": "PLANT", "claim": {"type": "PREDICT", "one_line": "planted"}, "inputs": {}}\n')
    ds = sha16(defp)
    tr = write(os.path.join(P['root'], 'TRUE_ROW_B9.tsv'), 'id\tverdict\tdef_sha16\tperfire_sha16\nX\tNOT SUPPORTED\t%s\t%s\n' % (ds, sha16(P['perfire'])))
    out = os.path.join(P['root'], 'BUNDLE'); card = os.path.join(P['root'], 'CARD')
    env = dict(os.environ, AU_BUILDER=TOOL)
    r = subprocess.run([sys.executable, '-B', AUT, 'bundle', out, '--from-job', JOBID, '--runner', P['runner'], '--alarm', ALARM,
                        '--block', 'SEPDEC', '--true-row', tr, '--def-sha16', ds], capture_output=True, text=True, timeout=120, env=env)
    assert r.returncode == 0 and r.stdout.startswith('BUNDLE '), (r.returncode, r.stdout, r.stderr)
    r2 = subprocess.run([sys.executable, '-B', AUT, 'card', card, '--alarm', ALARM, '--def', defp, '--def-sha16', ds, '--block', 'SEPDEC',
                         '--bundle', out, '--true-row', os.path.join(out, 'TRUE_ROW.tsv')], capture_output=True, text=True, timeout=120)
    assert r2.returncode == 0 and 'Q6:NOT_ANSWERED' in r2.stdout, (r2.returncode, r2.stdout, r2.stderr)
    r3 = subprocess.run([sys.executable, '-B', AUT, 'bundle', out, '--from-job', JOBID, '--runner', P['runner'], '--alarm', ALARM,
                         '--block', 'SEPDEC'], capture_output=True, text=True, timeout=120, env=env)
    assert r3.returncode == 2 and r3.stdout.startswith('REFUSED OUT_EXISTS'), (r3.returncode, r3.stdout)


TESTS = [('B%d' % i, globals()['test_B%d' % i]) for i in range(1, 10)]


def main(argv):
    want = set(argv) or {n for n, _ in TESTS}
    print('test_bundle_v1 %s; builder %s sha16 %s' % (STAMP, TOOL, sha16(TOOL)))
    bad = 0
    for name, fn in TESTS:
        if name not in want:
            continue
        try:
            fn(); print('PASS %s' % name)
        except Exception as e:
            bad += 1
            print('FAIL %s: %s: %s' % (name, type(e).__name__, str(e)[:600]))
            traceback.print_exc(limit=2, file=sys.stdout)
    n = len([1 for x, _ in TESTS if x in want])
    print('RESULT %d of %d passed' % (n - bad, n))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
