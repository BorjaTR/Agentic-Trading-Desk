#!/usr/bin/env python3
"""test_log_tried_v1_1.py (SCO-A162, SCOUT, 6 Nov 2026): step 20 LOG_TRIED against the REAL released add_row (ADD_ROW_V1), not the fake.
Drill K STOP_20 (job 20270382): alarm_pipeline_v1's row was refused (missing columns, blank fail_layer, thought_file not a file); the
v1 suite passed because tests/fake/add_row.py accepts any row. Scratch: tests/scratch/log_tried_<pid>/ (kept).
  python3 -B test_log_tried_v1_1.py        env PIPE_UNDER_TEST=<file> (default ../alarm_pipeline_v1_1.py), ADD_ROW=<add_row.py>
L1 NOT_MEASURABLE row written (fail_layer MEASURE, thought_file the card path, closest_existing the step 16 nearest line, 16 learning
columns filled); L2 WORKED row written (fail_layer NONE); L3 the v1 file on the same world STOPs TOOL_RC (the red run)."""
import sys
sys.dont_write_bytecode = True
import importlib.util, os, shutil, traceback
T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
SUT = os.environ.get('PIPE_UNDER_TEST', os.path.join(HERE, 'alarm_pipeline_v1_1.py'))
REL = '<RELEASE_ROOT>' if os.path.isdir('<RELEASE_ROOT>') else os.path.expanduser('~/mnt/volat_release')
AR = os.environ.get('ADD_ROW', os.path.join(REL, 'Learning_Loop/add_row/current/tree/team/RESEARCH/PLAYGROUND/tools/PG20261105_add_row_vm_fix/code/add_row.py'))
import time
SCR = os.path.join(os.environ.get('LT_SCRATCH', os.path.join(T, 'scratch')), 'log_tried_%d_%d' % (os.getpid(), time.time() * 1000))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def world(tag, M, word):
    w = os.path.join(SCR, tag); rd = os.path.join(w, 'run'); f = os.path.join(w, 'pipe')
    for d in (os.path.join(rd, 'ideas', 'X'), os.path.join(f, 'logs'), os.path.join(w, 'reg')):
        os.makedirs(d)
    open(os.path.join(rd, 'ideas', 'X', 'CARD_X.md'), 'w').write('# CARD X\nthe claim, written before the run\n')
    C = load(os.path.join(os.path.dirname(AR), 'common.py'), 'ar_common_%s' % tag)
    reg = os.path.join(w, 'reg', 'TRIED_ALARMS_V1.tsv'); open(reg, 'w').write('\t'.join(C.TRIED_COLS) + '\n')
    stg = os.path.join(os.path.dirname(AR), 'STAGES.tsv')
    src = stg if os.path.isfile(stg) else None
    for cand in [src, os.path.join(REL, '..', 'dev/TradingPlatform_repo/volat-agent/forensics/team/RESEARCH/PROCESS/2_ALARMS/STAGES.tsv')]:
        if cand and os.path.isfile(cand):
            shutil.copy(cand, os.path.join(w, 'reg', 'STAGES.tsv')); break
    dec = {'PASS': 'PASS', 'NOT_MEASURABLE': 'INSUFFICIENT'}[word]
    D = {6: dict(numbers=dict(job='6_COUNT')), 10: dict(numbers=dict(prereg_id='PREREG_X_1')), 11: dict(numbers=dict(job='11_GRADE')),
         13: dict(numbers=dict(job='13_TRUE', verdict_line='TRUE ok')), 14: dict(numbers=dict(word=dec, line='DECIDE %s' % dec)),
         16: dict(numbers=dict(job='MACREL_16', verdict='VERDICT NEW: x', nearest=['nearest 1: AD7_X (OWN, STOP, lean FOLLOW): same fires 6.4 pct'])),
         18: dict(numbers=dict(mechanism='NONE', share='0'))}
    class FP:
        pass
    p = FP(); p.f = f; p.rd = rd; p.fr = w
    p.S = dict(python=sys.executable, add_row=AR, tried_file=reg)
    p.I = dict(run='RUNT', idea='X', v='V1', seat='SCOUT', registry_mode='write', words='w', claim_text='claim', card='ideas/X/CARD_X.md',
               card_sha16='0' * 16, window='202509-202512', task='T')
    p.done = lambda n: D.get(n); p.p = lambda *a: os.path.join(f, *a)
    p.log = lambda n, tag: os.path.join(f, 'logs', 'S%02d_%s.out' % (n, tag))
    p.sh = lambda n, tag, argv, env=None, timeout=50, cwd=None: M.P.sh(p, n, tag, argv, env=env, timeout=timeout, cwd=cwd)
    p.py = lambda key: M.P.py(p, key)
    return p, reg


def row(reg):
    L = open(reg).read().splitlines(); h = L[0].split('\t'); assert len(L) == 2, L; return dict(zip(h, L[1].split('\t')))


def L1():
    M = load(SUT, 'sut1'); p, reg = world('L1', M, 'NOT_MEASURABLE')
    out = M.st_log_tried(p, 20); r = row(reg)
    assert out['numbers']['verdict'] == 'NOT_MEASURABLE' and r['fail_layer'] == 'MEASURE', r
    assert r['thought_file'] == os.path.join(p.rd, 'ideas/X/CARD_X.md') and r['closest_existing'].startswith('nearest 1: AD7_X'), r
    assert all(r[k] in ('unknown', 'none') for k in M.LOOP_COLS), r


def L2():
    M = load(SUT, 'sut2'); p, reg = world('L2', M, 'PASS')
    M.st_log_tried(p, 20); r = row(reg)
    assert r['verdict'] == 'WORKED' and r['fail_layer'] == 'NONE', r


def L3():
    v1 = os.path.join(HERE, 'alarm_pipeline_v1.py'); M = load(v1, 'v1'); p, reg = world('L3', M, 'NOT_MEASURABLE')
    try:
        M.st_log_tried(p, 20); raise AssertionError('v1 row accepted')
    except M.Stop as e:
        assert 'TOOL_RC' in str(e.args), e.args


TESTS = ['L1', 'L2', 'L3']
if __name__ == '__main__':
    ok = 0; names = sys.argv[1:] or TESTS
    for n in names:
        try:
            globals()[n](); print('PASS', n); ok += 1
        except Exception:
            print('FAIL', n); traceback.print_exc(limit=3)
    print('RESULT %d of %d passed (log_tried v1_1, add_row %s)' % (ok, len(names), AR)); sys.exit(0 if ok == len(names) else 1)
