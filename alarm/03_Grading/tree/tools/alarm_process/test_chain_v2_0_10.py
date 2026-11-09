#!/usr/bin/env python3
"""test_chain_v2_0_10.py (SCO-A162 for SCOUT, 6 Nov 2026). TEST, NOT REVIEWED. test_chain_v2_0_9.py on v2_0_10 (d1_reports_v6 pinned). Planted, seconds: the release lines of
alarm_grade_chain_v2_0_10_to20251231.sh, run with bash on a planted Alarm folder (no data, no tool runs past the checks):
  C1 a copy outside the Alarm folder refuses CHAIN_OUTSIDE_ALARM, exit 2, before any STATUS file
  C2 FEED_GATE set to a missing file: STATUS gate 8 'MISSING <file>', exit 8, nothing after it
  C3 FEED_GATE a file reading RUN: STATUS gate 0 'FOUND <file> RUN', then the chain goes on (here: CARD_SHA_MISMATCH, exit 2)
  C4 FEED_GATE empty: STATUS gate 0 'NONE (FEED_GATE empty ...)'
  C5 the grade workers and the Outcomes workers: GRADE_WORKERS default 8, D1_EO_WORKERS default ALARM=3,RND=5, d1_reports_v6 pinned
  C6 GRADE_WORKERS 9, 0, x refused exit 2 BAD_GRADE_WORKERS before any STATUS file; unset, 1 and 8 pass the check
Run:  python3 -B test_chain_v2_0_8.py [C1 ...]      Env: CHAIN = the file under test (default beside this file); CH_SCRATCH
Exit 0 all passed, 1 a test failed."""
import sys
sys.dont_write_bytecode = True
import datetime as dt, os, shutil, subprocess, traceback

HERE = os.path.dirname(os.path.realpath(__file__))
CHAIN = os.environ.get('CHAIN') or os.path.join(HERE, 'alarm_grade_chain_v2_0_10_to20251231.sh')
SCRATCH = os.environ.get('CH_SCRATCH') or os.path.join(os.path.dirname(HERE), 'scratch')
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
_N = [0]
import hashlib
D6 = hashlib.sha256(open(os.path.join(os.path.dirname(os.path.realpath(CHAIN)), 'd1_reports_v6.py'), 'rb').read()).hexdigest()[:16] if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(CHAIN)), 'd1_reports_v6.py')) else 'NO_D1_V6'


def plant(tag):
    _N[0] += 1
    d = os.path.join(SCRATCH, 'ch208_%s_%s_%d' % (STAMP, tag, _N[0]))
    AL = os.path.join(d, 'ALARM_PLANT')
    os.makedirs(os.path.join(AL, '_tools')); os.makedirs(os.path.join(AL, 'settings'))
    open(os.path.join(AL, '_tools', 'settings_v1.py'), 'w').write('# planted\n')
    ap = os.path.join(AL, '01_Detection', 'tree', 'team', 'RESEARCH', 'tools', 'alarm_process'); os.makedirs(ap)
    open(os.path.join(ap, 'OUTCOMES_MENU_ALARM_V1.json'), 'w').write('{}\n')
    open(os.path.join(ap, 'alarm_card_gm1.py'), 'w').write('# planted card, wrong bytes on purpose\n')
    ch = os.path.join(AL, '03_Grading', 'tree', 'tools', 'alarm_process'); os.makedirs(ch)
    c = os.path.join(ch, os.path.basename(CHAIN)); shutil.copyfile(CHAIN, c)
    df = os.path.join(d, 'DEF.json'); open(df, 'w').write('{}\n')
    return d, AL, c, df


def run(c, AL, df, W, gate, **extra):
    env = dict(os.environ, AL=AL, PY=sys.executable, LAB_DAYS='/planted/lab_days', FEED_GATE=gate, RESEARCH_STORE='/planted/research', **extra)
    env.pop('GRADE_WORKERS', None) if 'GRADE_WORKERS' not in extra else None
    r = subprocess.run(['bash', c, 'V1', df, W], env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    st = os.path.join(W, 'STATUS_V1.tsv')
    rows = [l.rstrip('\n').split('\t') for l in open(st)][1:] if os.path.exists(st) else None
    return r.returncode, r.stdout + r.stderr, rows


def C1():
    d, AL, c, df = plant('C1'); out = os.path.join(d, 'outside.sh'); shutil.copyfile(CHAIN, out)
    rc, o, rows = run(out, AL, df, os.path.join(d, 'W'), '')
    assert rc == 2 and 'CHAIN_OUTSIDE_ALARM' in o and rows is None, (rc, o, rows)


def C2():
    d, AL, c, df = plant('C2'); g = os.path.join(d, 'no_such_gate.txt')
    rc, o, rows = run(c, AL, df, os.path.join(d, 'W'), g)
    assert rc == 8 and rows is not None, (rc, o)
    assert rows == [['gate', '8', '0', 'MISSING ' + g, rows[0][4]]], rows


def C3():
    d, AL, c, df = plant('C3'); g = os.path.join(d, 'BACKFILL_GATE.txt'); open(g, 'w').write('RUN\n# planted\n')
    rc, o, rows = run(c, AL, df, os.path.join(d, 'W'), g)
    assert rows is not None, (rc, o)
    assert rows[0][:4] == ['gate', '0', '0', 'FOUND %s RUN' % g], rows
    assert rc == 2 and 'CARD_SHA_MISMATCH' in o, (rc, o)


def C4():
    d, AL, c, df = plant('C4')
    rc, o, rows = run(c, AL, df, os.path.join(d, 'W'), '')
    assert rows is not None, (rc, o)
    assert rows[0][:4] == ['gate', '0', '0', 'NONE (FEED_GATE empty: no gate, a machine without the feed)'], rows
    assert rc == 2 and 'CARD_SHA_MISMATCH' in o, (rc, o)


def C5():
    s = open(CHAIN).read()
    assert 'GRADE_WORKERS=${GRADE_WORKERS:-8};' in s and '--workers $GRADE_WORKERS' in s and 'export D1_EO_WORKERS=${D1_EO_WORKERS:-ALARM=3,RND=5}' in s
    assert 'd1_reports_v6.py chain' in s and 'D1_SHA=%s' % D6 in s


def C6():
    for gw, ok in (('9', 0), ('0', 0), ('x', 0), ('', 1), ('1', 1), ('8', 1)):
        d, AL, c, df = plant('C6'); g = os.path.join(d, 'BACKFILL_GATE.txt'); open(g, 'w').write('RUN\n')
        ex = {'GRADE_WORKERS': gw} if gw else {}
        rc, o, rows = run(c, AL, df, os.path.join(d, 'W'), g, **ex)
        if ok:
            assert 'BAD_GRADE_WORKERS' not in o and rows is not None, (gw, rc, o)
        else:
            assert rc == 2 and 'BAD_GRADE_WORKERS' in o and rows is None, (gw, rc, o)


TESTS = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
if __name__ == '__main__':
    os.makedirs(SCRATCH, exist_ok=True)
    want = sys.argv[1:] or TESTS; bad = 0
    for n in want:
        try:
            globals()[n](); print('PASS', n)
        except (Exception, SystemExit):
            bad += 1; print('FAIL', n); traceback.print_exc(limit=3)
    print('RESULT %d of %d passed (%s)' % (len(want) - bad, len(want), os.path.basename(CHAIN)))
    sys.exit(1 if bad else 0)
