#!/usr/bin/env python3
"""test_bundle_gg_v1.py (SCO-A146 for SCOUT, 6 Nov 2026, playground PG20261105_alarm_understand). TEST, NOT REVIEWED.
Unit tests B10 to B15 of `bundle --from-gg <results store run folder>` (bundle_builder_v1.py), written BEFORE the code, on planted
synthetic data only: a planted idea_to_grade V3.2 store (RUN.json, grading/PARENTS.tsv), a planted event list, a planted grouper Data.
No market data, no lab day, no real store is read. The smallest test per piece, with its edge cases.
Run:  python3 -B test_bundle_gg_v1.py [B10 B11 ...]      (all when none named)
Env:  BB_TOOL (the builder under test, a mutant copy for the mutant runs), AU_SCRATCH (planted inputs; kept, never removed)
Exit 0 all passed, 1 a test failed."""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, importlib.util, json, math, os, subprocess, traceback
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.environ.get('BB_TOOL') or os.path.join(HERE, 'bundle_builder_v1.py')
AUT = os.path.join(HERE, 'alarm_understand_v1.py')
SCRATCH = os.environ.get('AU_SCRATCH') or os.path.join(os.path.dirname(HERE), 'scratch')
_spec = importlib.util.spec_from_file_location('bundle_builder_gg_under_test', TOOL)
BB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BB)
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
ALARM = 'PG_PLANT'
AID = 'ALM_PG_PLANT_SD'
DEFS = 'dddddddddddddddd'
_N = [0]
PH = ['parent_id', 'event_id', 'coin', 't', 'side', 'day', 'wave_id', 'census_status', 'original_draw_edges', 'eligible_edges',
      'rule_excluded_edges', 'row_follow', 'row_fade', 'known_at_us']
OFF = 8 + 60 + 14400


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


def eid(esha, c, t, s):
    return hashlib.sha256(('%s|%s|%d|%d' % (esha, c, int(t), int(s))).encode()).hexdigest()[:16]


def plant(name, fires=FIRES0, events=None, first='20250910', last='20251231', alarm_id=AID, defs=DEFS, parents=None,
          bad_eid=None, ka_off=OFF, run_json=None, ph=PH, gg_out=False, side_txt=None):
    """a planted store <root>/store/run (RUN.json, grading/PARENTS.tsv) and its event list <root>/EVENTS.tsv -> dict"""
    _N[0] += 1
    root = os.path.join(SCRATCH, 'bbgg_%s_%02d_%s' % (STAMP, _N[0], name))
    ev_rows = events if events is not None else fires
    ev = write(os.path.join(root, 'EVENTS.tsv'), 'coin\tt\tside\tonset_t\ttrigger\tevent_id\n' + ''.join(
        '%s\t%d\t%d\t%d\tLIQ\tdet%d\n' % (c, t, s, t - 30, i) for i, (c, t, s) in enumerate(ev_rows)))
    es = sha16(ev)
    run = os.path.join(root, 'store', 'run')
    pr = parents if parents is not None else fires
    lines = ['\t'.join(ph)]
    for i, (c, t, s) in enumerate(pr):
        e = eid(es, c, t, s) if bad_eid != i else 'ffffffffffffffff'
        d = dict(parent_id='%s_%d_%+d' % (c, t, s), event_id=e, coin=c, t=str(t), side=side_txt[i] if side_txt and i in side_txt else str(s),
                 day=dt.datetime.fromtimestamp(int(float(t)), dt.timezone.utc).strftime('%Y%m%d'), wave_id='W%d' % (i // 2),
                 census_status='MATCHED', original_draw_edges='3', eligible_edges='3', rule_excluded_edges='0', row_follow=str(2 * i),
                 row_fade=str(2 * i + 1), known_at_us=str(int((float(t) + ka_off) * 1000000)))
        lines.append('\t'.join(d.get(k, '') for k in ph))
    write(os.path.join(run, 'grading', 'PARENTS.tsv'), '\n'.join(lines) + '\n')
    body = dict(tool='idea_to_grade', version='3.2', event_list=dict(path=ev, sha16=es), alarm_id=alarm_id,
                alarm=dict(definition_sha16=defs), selection=dict(first=first, last=last),
                settings=dict(measure=dict(execution_delay_s=8.0)), counts=dict(parents=len(pr)))
    if run_json is not None:
        body = run_json(body)
    if body is not None:
        write(os.path.join(run, 'RUN.json'), body if isinstance(body, str) else json.dumps(body))
    if gg_out:
        write(os.path.join(root, 'ggout', 'RUN_ARGS.tsv'), 'store\t%s\n' % run)
    return dict(root=root, run=run, ev=ev, ev_sha16=es, ggout=os.path.join(root, 'ggout'))


MONEY_ARGS = ['--gg-tools', '/t', '--gg-costs', '/c', '--money-exit', 'HOLD_1h', '--lean', 'FADE']


def args(P, block='SEPDEC', extra=None, run=None, out_name='BUNDLE'):
    out = os.path.join(P['root'], out_name)
    ex = MONEY_ARGS + ['--def-sha16', DEFS, '--gg-alarm-id', AID] if extra is None else extra
    return BB.parse(['bundle', out, '--from-gg', run or P['run'], '--alarm', ALARM, '--block', block] + list(ex)), out


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


class FakeData:
    """grouper_v1_10.Data's face: keys (coin, t, side) as strings in PARENTS order, P[(exit, lean, cost)] = (X, T)"""
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


def gg(keys, flip=None):
    return dict(ctx=no_reader, epi=no_reader, gg=lambda run, tools, costs: FakeData(keys, flip))


# ---------------------------------------------------------------------------------------------------- B10 the store join, happy path
def test_B10():
    extra_ev = FIRES0 + [('EEE', T(20251020, 10), 1)]          # one listed fire the store did not grade: counted, never copied
    P = plant('b10', events=extra_ev)
    a, out = args(P)
    res = BB.build(a, readers=gg(FIRES0))
    F = rows(os.path.join(out, 'FIRES.tsv'))
    assert [(r['alarm_id'], r['coin'], int(r['t']), int(r['side'])) for r in F] == [(ALARM, c, t, s) for c, t, s in FIRES0], F
    M = {(r['coin'], int(r['t'])): r for r in rows(os.path.join(out, 'MONEY.tsv'))}
    assert len(M) == 5, M
    r = M[(FIRES0[2][0], FIRES0[2][1])]
    assert (float(r['fade_gross_15m']), float(r['fade_gross_1h']), float(r['fade_gross_4h'])) == (12.0, 22.0, 32.0), r
    assert float(r['net']) == 1.0 and float(r['edge_tough']) == 2.0 and r['exit'] == 'HOLD_1h' and int(r['side']) == 1, r
    assert int(r['known_at']) == FIRES0[2][1] + OFF and r['after'] == '1', r          # known_at kept from PARENTS, AFTER marked
    C = rows(os.path.join(out, 'CONTEXT.tsv'))
    got = {(x['coin'], int(x['t']), x['column']): x for x in C}
    o = got[(FIRES0[0][0], FIRES0[0][1], 'onset_t')]
    assert o['source'] == 'EVENT_LIST' and int(o['value']) == FIRES0[0][1] - 30 and int(o['known_at']) == FIRES0[0][1] and o['after'] == '0', o
    tr = got[(FIRES0[0][0], FIRES0[0][1], 'trigger')]
    assert tr['value'] == 'LIQ' and tr['after'] == '0', tr
    wv = got[(FIRES0[0][0], FIRES0[0][1], 'wave_id')]
    assert wv['source'] == 'PARENTS' and wv['after'] == '1' and int(wv['known_at']) == FIRES0[0][1] + OFF, wv
    assert not any(x['column'] in ('coin', 't', 'side', 'event_id', 'known_at_us', 'parent_id') for x in C), C[:3]
    assert not any(x['coin'] == 'EEE' for x in C) and not any(r['coin'] == 'EEE' for r in F), 'an ungraded listed fire was copied'
    for nm in ('READINGS.tsv', 'FORCED.tsv'):
        assert not os.path.exists(os.path.join(out, nm)), nm
    roles = {x['role']: x for x in rows(os.path.join(out, 'BUNDLE_SOURCES.tsv'))}
    assert roles['STORE_RUN']['sha16'] == sha16(os.path.join(P['run'], 'RUN.json')), roles
    assert roles['STORE_PARENTS']['rows'] == '5' and roles['EVENT_LIST']['sha16'] == P['ev_sha16'], roles
    assert roles['MONEY']['rows'] == '5', roles['MONEY']
    notes = open(os.path.join(out, 'BUNDLE_NOTES.md')).read()
    assert '1 listed fires not graded' in notes, notes
    assert res['fires'] == 5 and res['money'] == 5 and res['closed_dropped'] == 0, res


# ---------------------------------------------------------------------------------------------------- B11 the store: refusals
def test_B11():
    P = plant('b11a', run_json=lambda b: None); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'NO_INPUT')
    P = plant('b11b', run_json=lambda b: '{not json'); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')
    P = plant('b11c'); os.rename(P['ev'], P['ev'] + '.moved')
    refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'NO_INPUT')
    P = plant('b11d'); open(P['ev'], 'a').write('ZZZ\t%d\t1\t0\tX\tx\n' % T(20251201))
    refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'SOURCE_CHANGED')
    P = plant('b11e', defs='eeeeeeeeeeeeeeee'); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'SOURCE_CHANGED')
    P = plant('b11f', alarm_id='ALM_OTHER'); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'JOIN_MISMATCH')
    P = plant('b11g', run_json=lambda b: dict(b, counts=dict(parents=4))); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'JOIN_MISMATCH')
    P = plant('b11h', run_json=lambda b: dict(b, event_list=None)); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')
    P = plant('b11i'); os.rename(os.path.join(P['run'], 'grading', 'PARENTS.tsv'), os.path.join(P['run'], 'grading', 'P.moved'))
    refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'NO_INPUT')


# ---------------------------------------------------------------------------------------------------- B12 the parents: refusals
def test_B12():
    P = plant('b12a', parents=FIRES0 + [('ZZZ', T(20251203), 1)]); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'JOIN_EXTRA')
    P = plant('b12b', bad_eid=3); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'JOIN_MISMATCH')
    P = plant('b12c', side_txt={1: '0'}); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')
    P = plant('b12d', parents=FIRES0 + [FIRES0[0]], events=FIRES0); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')
    P = plant('b12e', parents=[(c, t + 0.5 if i == 2 else t, s) for i, (c, t, s) in enumerate(FIRES0)], events=FIRES0)
    refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')
    P = plant('b12f', ka_off=0); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')       # money known at the fire
    P = plant('b12g', ph=PH[:-1]); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0)), 'BAD_INPUT')     # no known_at_us column
    P = plant('b12h'); a, out = args(P)
    refused(lambda: BB.build(a, readers=gg(FIRES0[:4])), 'JOIN_MISMATCH')                                       # Data is not PARENTS
    assert not os.path.exists(out), 'written before a refusal'
    P = plant('b12i'); refused(lambda: BB.build(args(P)[0], readers=gg(FIRES0, flip=2)), 'JOIN_MISMATCH')
    P = plant('b12j'); refused(lambda: BB.build(args(P)[0], readers=gg(list(reversed(FIRES0)))), 'JOIN_MISMATCH')  # order kept


# ---------------------------------------------------------------------------------------------------- B13 the arguments
def test_B13():
    P = plant('b13')
    out = os.path.join(P['root'], 'O')
    base = ['bundle', out, '--alarm', ALARM, '--block', 'SEPDEC']
    refused(lambda: BB.build(BB.parse(base + ['--from-gg', P['run'], '--from-job', '9001', '--runner', '/r'] + MONEY_ARGS +
                                      ['--def-sha16', DEFS, '--gg-alarm-id', AID]), readers=gg(FIRES0)), 'BAD_ARGS')
    refused(lambda: BB.build(BB.parse(base + MONEY_ARGS), readers=gg(FIRES0)), 'BAD_ARGS')                    # neither source
    refused(lambda: BB.build(args(P, extra=['--def-sha16', DEFS, '--gg-alarm-id', AID])[0], readers=gg(FIRES0)), 'BAD_ARGS')  # no money args
    refused(lambda: BB.build(args(P, extra=['--gg-tools', '/t', '--money-exit', 'HOLD_1h', '--lean', 'FADE', '--def-sha16', DEFS,
                                          '--gg-alarm-id', AID])[0], readers=gg(FIRES0)), 'BAD_ARGS')   # no --gg-costs
    refused(lambda: BB.build(args(P, extra=MONEY_ARGS + ['--gg-alarm-id', AID])[0], readers=gg(FIRES0)), 'BAD_ARGS')         # no def
    refused(lambda: BB.build(args(P, extra=MONEY_ARGS + ['--def-sha16', DEFS])[0], readers=gg(FIRES0)), 'BAD_ARGS')          # no alarm id
    refused(lambda: BB.build(args(P, extra=MONEY_ARGS + ['--def-sha16', DEFS, '--gg-alarm-id', AID, '--gg-run', '/x'])[0],
                             readers=gg(FIRES0)), 'BAD_ARGS')
    refused(lambda: BB.build(args(P, block='JANAPR')[0], readers=gg(FIRES0)), 'BAD_ARGS')                    # block outside the store
    refused(lambda: BB.build(args(P, extra=MONEY_ARGS + ['--def-sha16', DEFS, '--gg-alarm-id', AID, '--true-row', '/x'])[0],
                             readers=gg(FIRES0)), 'NOT_BUILT')
    refused(lambda: BB.build(args(P, extra=MONEY_ARGS + ['--def-sha16', DEFS, '--gg-alarm-id', AID, '--ctx', '/r', 'A02',
                                                          '--ctx-values', 'x', '--lab3', '/l'])[0], readers=gg(FIRES0)), 'NOT_BUILT')
    P2 = plant('b13g', gg_out=True)
    e = refused(lambda: BB.build(args(P2, run=P2['ggout'])[0], readers=gg(FIRES0)), 'NOT_BUILT')            # a gg output folder
    assert P2['run'] in e, e
    refused(lambda: BB.build(BB.parse(base + ['--from-job', '9001'])), 'BAD_ARGS')                            # from-job needs --runner


# ---------------------------------------------------------------------------------------------------- B14 closed days and the window
def test_B14():
    fires = FIRES0 + [('EEE', T(20270102, 60), 1)]                     # a planted fire on a day the card's law closes
    P = plant('b14a', fires=fires, last='20270131')
    a, out = args(P)
    res = BB.build(a, readers=gg(fires))
    F = rows(os.path.join(out, 'FIRES.tsv')); M = rows(os.path.join(out, 'MONEY.tsv')); C = rows(os.path.join(out, 'CONTEXT.tsv'))
    assert res['closed_dropped'] == 1 and len(F) == 5 and len(M) == 5, res
    assert not any(r['coin'] == 'EEE' for r in F + M + C), 'a closed-day fire was copied'
    P = plant('b14b', first='20250901', last='20260430', fires=FIRES0 + [('FFF', T(20260210, 5), -1)])
    a, out = args(P, block='JANAPR')
    res = BB.build(a, readers=gg(FIRES0 + [('FFF', T(20260210, 5), -1)]))
    assert res['block_fires'] == 1 and res['fires'] == 6, res
    P = plant('b14c'); refused(lambda: BB.build(args(P, block='MAYJUL')[0], readers=gg(FIRES0)), 'BLOCK_CLOSED')


# ---------------------------------------------------------------------------------------------------- B15 the card reads the bundle
def test_B15():
    P = plant('b15')
    a, out = args(P)
    BB.build(a, readers=gg(FIRES0))
    defp = write(os.path.join(P['root'], 'DEF.json'), '{"id": "PLANT", "claim": {"type": "PREDICT", "one_line": "planted"}, "inputs": {}}\n')
    card = os.path.join(P['root'], 'CARD')
    r = subprocess.run([sys.executable, '-B', AUT, 'card', card, '--alarm', ALARM, '--def', defp, '--def-sha16', sha16(defp),
                        '--block', 'SEPDEC', '--bundle', out], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and r.stdout.startswith('CARD '), (r.returncode, r.stdout, r.stderr)
    assert 'Q6:NOT_ANSWERED' not in r.stdout, r.stdout                   # MONEY was read
    r3 = subprocess.run([sys.executable, '-B', AUT, 'bundle', out, '--from-gg', P['run'], '--alarm', ALARM, '--block', 'SEPDEC']
                        + MONEY_ARGS + ['--def-sha16', DEFS, '--gg-alarm-id', AID], capture_output=True, text=True, timeout=120,
                        env=dict(os.environ, AU_BUILDER=TOOL))
    assert r3.returncode == 2 and r3.stdout.startswith('REFUSED OUT_EXISTS'), (r3.returncode, r3.stdout)


TESTS = [('B%d' % i, globals()['test_B%d' % i]) for i in range(10, 16)]


def main(argv):
    want = set(argv) or {n for n, _ in TESTS}
    print('test_bundle_gg_v1 %s; builder %s sha16 %s' % (STAMP, TOOL, sha16(TOOL)))
    bad = 0
    for name, fn in TESTS:
        if name not in want:
            continue
        try:
            fn(); print('PASS %s' % name)
        except (Exception, SystemExit) as e:                      # an unknown argument on the red run exits argparse
            bad += 1
            print('FAIL %s: %s: %s' % (name, type(e).__name__, str(e)[:600]))
            traceback.print_exc(limit=2, file=sys.stdout)
    n = len([1 for x, _ in TESTS if x in want])
    print('RESULT %d of %d passed' % (n - bad, n))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
