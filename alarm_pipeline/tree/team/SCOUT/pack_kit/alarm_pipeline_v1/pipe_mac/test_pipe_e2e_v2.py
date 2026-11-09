#!/usr/bin/env python3
"""test_pipe_e2e_v2.py (SCO-A162R for SCOUT, 6 Nov 2026). TEST. Seconds, planted: the E2E verdict rule of pipe_e2e_v2 (V1_3):
E1 22 of 22 and no refusal asked = PASS; E2 the refusal asked, exactly (step, name, code) = PASS, another refusal or 22 of 22 = FAIL;
E3 a pipe_mac rc other than 0, 3, 10 = CRASH (even at 22 of 22); E4 21 of 22, or a compare not equal = FAIL; E5 an existing out root is
refused (exit 2, nothing written). python3 -B test_pipe_e2e_v1.py; exit 0 all passed."""
import sys
sys.dont_write_bytecode = True
import os, tempfile, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import pipe_e2e_v2 as E


def r(**k):
    d = dict(case='C', steps=22, stop='-', cmp='-', total=1.0, per={}, expect='', prc=0, code='')
    d.update(k); return d


def E1():
    assert E.verdict(r()) == 'PASS'
    assert E.verdict(r(cmp=0)) == 'PASS'


def E2():
    x = '01 INPUT BLOCK_NOT_GRADED'
    assert E.verdict(r(steps=0, prc=3, expect=x, code=x)) == 'PASS'
    assert E.verdict(r(steps=0, prc=3, expect=x, code='01 INPUT WINDOW_OUTSIDE_BLOCK')) == 'FAIL'
    assert E.verdict(r(expect=x)) == 'FAIL'          # asked a refusal, ran 22 of 22: the refusal is missing


def E3():
    assert E.verdict(r(prc=1)) == 'CRASH'
    assert E.verdict(r(prc=1, expect='x', code='x')) == 'CRASH'


def E4():
    assert E.verdict(r(steps=21, prc=3, code='17 CARD JOB_EXIT')) == 'FAIL'
    assert E.verdict(r(cmp=1)) == 'FAIL'


def E5():
    sd = os.environ.get('MAC_SCRATCH') or None
    if sd:
        os.makedirs(sd, exist_ok=True)   # job 20270422: MAC_SCRATCH named a folder not made yet (E5 FileNotFoundError)
    d = tempfile.mkdtemp(prefix='e2e_t5_', dir=sd)
    o = io.StringIO()
    with contextlib.redirect_stdout(o):
        rc = E.main([d, 'X=y.json', '--template', 't', '--home', 'h'])
    assert rc == 2 and 'REFUSED OUT_EXISTS' in o.getvalue() and os.listdir(d) == [], (rc, o.getvalue())


if __name__ == '__main__':
    bad = 0; T = ['E1', 'E2', 'E3', 'E4', 'E5']
    for n in T:
        try:
            globals()[n](); print('PASS', n)
        except Exception as e:
            bad += 1; print('FAIL', n, repr(e)[:300])
    print('RESULT %d of %d passed (pipe_e2e_v2)' % (len(T) - bad, len(T)))
    sys.exit(1 if bad else 0)
