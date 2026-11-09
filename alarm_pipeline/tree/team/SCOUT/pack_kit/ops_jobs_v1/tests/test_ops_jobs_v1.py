#!/usr/bin/env python3
# test_ops_jobs_v1.py (SCO-A137, SCOUT 2026-11-06): smallest cases of ops_jobs_v1.py (nextop: the next free <TASK>-OP<nn> from the typed
# ledger and JOBS.tsv; relq: the first live empty rel queue by the bridge's own rule; add and done: the work/JOBS.tsv rows from the typed
# ledger INTENT row and the bridge's own output; check: JOBS.tsv job rows against the ledger INTENT jobs), written before the tool (red
# first). Planted ledger, bridge outputs and a planted runner folder only; no runner job, no real queue is read.
# Usage: python3 -B test_ops_jobs_v1.py [<tool path>] [<work dir>]; exit 0 when all pass.
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'ops_jobs_v1.py')
W = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'work', 'r_%s_%d' % (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), os.getpid()))
os.makedirs(W)
def run(*a):
    p = subprocess.run([sys.executable, '-B', TOOL] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout
def wr(n, t):
    p = os.path.join(W, n)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f: f.write(t)
    return p
LH = 'id\tstatus\tutc\ttext\n'
def lrow(op, st, job, task='SCO-A9'): return '%s\t%s\t2026-11-06T10:00:00Z\t{"schema":"LOOP_RUNNER_OP_V1","task":"%s","job":"%s"}\n' % (op, st, task, job)
LED2 = LH + lrow('SCO-A9-OP01', 'INTENT', '20270116') + lrow('SCO-A9-OP01', 'DONE', '20270116') + lrow('SCO-A9-OP02', 'INTENT', '20270117')
REL_OUT = ('RELBRIDGE OPS INTENT SCO-A9-OP02 2026-11-06T10:13:50Z task SCO-A9 job 20270117 in /x/TYPED_OPS_SCO-A9.tsv commit OPS:SCO-A9-OP02:INTENT:1:abc\n'
           'RELBRIDGE QUEUED 20270117_judge_RBSCOUT_HCMEM on Q_V16 (rel hc_mem_probe_v3 for SCOUT_20261105); it never waits: relwait 20270117_judge_RBSCOUT_HCMEM\n')
KIT_OUT = ('RELBRIDGE OPS INTENT SCO-A9-OP02 2026-11-06T10:24:51Z task SCO-A9 job 20270117 in /x commit c\n'
           'QUEUED Q_V1 20270117 20270117_judge_SCOUT_GRADE_TESTIDEA.job.sh twin jobs/20270117_judge_SCOUT_GRADE_TESTIDEA.job.sh sha16 6e9e IN 6e9e | RUNS\n')
OPD = ('RELBRIDGE OPS DONE SCO-A9-OP02 2026-11-06T10:14:18Z task SCO-A9 job 20270117 in /x commit c\n'
       'RELBRIDGE OPDONE SCO-A9-OP02 job 20270117 (20270117_judge_RBSCOUT_HCMEM on Q_V16, SUCCEEDED, exit 0) task SCO-A9 commit OPS:SCO-A9-OP02:DONE:2:def; DONE is the runner\'s terminal record only, never a PASS\n')
def jrows(p): return [l.split('\t') for l in open(p).read().split('\n') if l][1:]
CASES = []
def case(f): CASES.append(f); return f
@case
def t01_nextop_empty_ledger_is_op01():
    rc, o = run('nextop', '--ledger', os.path.join(W, 'none.tsv'), '--task', 'SCO-A9')
    assert rc == 0 and o.strip().split('\n')[-1] == 'NEXTOP SCO-A9-OP01', (rc, o)
@case
def t02_nextop_after_two():
    led = wr('L2.tsv', LED2)
    rc, o = run('nextop', '--ledger', led, '--task', 'SCO-A9')
    assert rc == 0 and o.strip().split('\n')[-1] == 'NEXTOP SCO-A9-OP03', (rc, o)
@case
def t03_nextop_counts_jobs_rows_too():
    led = wr('L3.tsv', LED2); j = wr('J3.tsv', 'utc\top_id\tjob\tstep\tpurpose\n2026-11-06T10:00:00Z\tSCO-A9-OP05\t20270120_x\tCOUNT\tp\n')
    rc, o = run('nextop', '--ledger', led, '--task', 'SCO-A9', '--jobs', j)
    assert rc == 0 and o.strip().split('\n')[-1] == 'NEXTOP SCO-A9-OP06', (rc, o)
@case
def t04_nextop_bad_ledger_refused():
    led = wr('L4.tsv', 'a\tb\n')
    rc, o = run('nextop', '--ledger', led, '--task', 'SCO-A9')
    assert rc == 3 and 'REFUSED BAD_LEDGER' in o, (rc, o)
@case
def t05_add_from_rel_output():
    led = wr('L5.tsv', LED2); j = os.path.join(W, 'J5.tsv'); out = wr('REL_HCMEM_V1.txt', REL_OUT)
    rc, o = run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'rel hc_mem_probe_v3: memory', '--out', out)
    assert rc == 0, (rc, o)
    assert open(j).read().split('\n')[0] == 'utc\top_id\tjob\tstep\tpurpose'
    r = jrows(j); assert len(r) == 1 and r[0][1:] == ['SCO-A9-OP02', '20270117_judge_RBSCOUT_HCMEM', 'DEFINE', 'rel hc_mem_probe_v3: memory'], r
@case
def t06_add_from_kitq_output():
    led = wr('L6.tsv', LED2); j = os.path.join(W, 'J6.tsv'); out = wr('KITQ_GRADE_V1.txt', KIT_OUT)
    rc, o = run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'GRADE', '--purpose', 'kitq GRADE', '--out', out)
    assert rc == 0 and jrows(j)[0][2] == '20270117_judge_SCOUT_GRADE_TESTIDEA', (rc, o)
@case
def t07_add_no_intent_refused():
    led = wr('L7.tsv', LH + lrow('SCO-A9-OP01', 'INTENT', '20270116')); j = os.path.join(W, 'J7.tsv'); out = wr('o7.txt', REL_OUT)
    rc, o = run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)
    assert rc == 3 and 'REFUSED NO_INTENT' in o and not os.path.exists(j), (rc, o)
@case
def t08_add_output_of_another_job_refused():
    led = wr('L8.tsv', LED2); j = os.path.join(W, 'J8.tsv'); out = wr('o8.txt', REL_OUT.replace('20270117', '20270199'))
    rc, o = run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)
    assert rc == 3 and 'REFUSED NO_JOBNAME' in o, (rc, o)
@case
def t09_add_twice_refused():
    led = wr('L9.tsv', LED2); j = os.path.join(W, 'J9.tsv'); out = wr('o9.txt', REL_OUT)
    assert run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)[0] == 0
    rc, o = run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)
    assert rc == 3 and 'REFUSED DUP_OP' in o and len(jrows(j)) == 1, (rc, o)
@case
def t10_done_appends_the_bridge_words():
    led = wr('L10.tsv', LED2); j = os.path.join(W, 'J10.tsv'); out = wr('o10.txt', REL_OUT); d = wr('OPDONE_SCO-A9-OP02.txt', OPD)
    assert run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)[0] == 0
    rc, o = run('done', '--jobs', j, '--op', 'SCO-A9-OP02', '--out', d)
    assert rc == 0, (rc, o)
    r = jrows(j); assert len(r) == 2 and r[1][1] == 'SCO-A9-OP02 opdone' and r[1][2].startswith('RELBRIDGE OPDONE SCO-A9-OP02 job 20270117 ('), r
@case
def t11_done_without_job_row_refused():
    j = wr('J11.tsv', 'utc\top_id\tjob\tstep\tpurpose\n'); d = wr('o11.txt', OPD)
    rc, o = run('done', '--jobs', j, '--op', 'SCO-A9-OP02', '--out', d)
    assert rc == 3 and 'REFUSED NOT_FILED' in o, (rc, o)
@case
def t12_done_output_without_opdone_refused():
    led = wr('L12.tsv', LED2); j = os.path.join(W, 'J12.tsv'); out = wr('o12.txt', REL_OUT); d = wr('o12d.txt', 'RELBRIDGE REFUSED NOT_TERMINAL wait\n')
    assert run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)[0] == 0
    rc, o = run('done', '--jobs', j, '--op', 'SCO-A9-OP02', '--out', d)
    assert rc == 3 and 'REFUSED NO_OPDONE' in o and len(jrows(j)) == 1, (rc, o)
@case
def t13_done_twice_refused():
    led = wr('L13.tsv', LED2); j = os.path.join(W, 'J13.tsv'); out = wr('o13.txt', REL_OUT); d = wr('o13d.txt', OPD)
    run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)
    assert run('done', '--jobs', j, '--op', 'SCO-A9-OP02', '--out', d)[0] == 0
    rc, o = run('done', '--jobs', j, '--op', 'SCO-A9-OP02', '--out', d)
    assert rc == 3 and 'REFUSED DUP_DONE' in o, (rc, o)
@case
def t14_check_same_and_differ():
    led = wr('L14.tsv', LED2); j = os.path.join(W, 'J14.tsv'); out = wr('o14.txt', REL_OUT)
    run('add', '--jobs', j, '--ledger', led, '--op', 'SCO-A9-OP02', '--step', 'DEFINE', '--purpose', 'p', '--out', out)
    rc, o = run('check', '--jobs', j, '--ledger', led, '--task', 'SCO-A9')
    assert rc == 3 and 'DIFFER' in o, (rc, o)
    with open(j, 'a') as f: f.write('2026-11-06T10:00:00Z\tSCO-A9-OP01\t20270116_judge_RBSCOUT_HCDEFS\tDEFINE\tp\n')
    rc, o = run('check', '--jobs', j, '--ledger', led, '--task', 'SCO-A9')
    assert rc == 0 and 'SAME' in o, (rc, o)
def queue(root, q, age=5, files=()):
    d = os.path.join(root, q); os.makedirs(os.path.join(d, 'IN')); os.makedirs(os.path.join(d, 'RUN'))
    hb = os.path.join(d, 'runner.heartbeat'); open(hb, 'w').write('x'); t = time.time() - age; os.utime(hb, (t, t))
    for sub, f in files: open(os.path.join(d, sub, f), 'w').write('#')
@case
def t15_relq_first_live_empty():
    root = os.path.join(W, 'runner15'); queue(root, 'Q_V1', age=300); queue(root, 'Q_V2', files=[('IN', '1_judge_OTHER_x.job.sh')]); queue(root, 'Q_V16'); queue(root, 'Q_V19')
    rc, o = run('relq', '--runner', root, '--seat', 'SCOUT')
    assert rc == 0 and o.strip().split('\n')[-1] == 'RELQ Q_V16', (rc, o)
    assert 'Q_V1 NOT_LIVE' in o and 'Q_V2 BUSY' in o, o
@case
def t16_relq_busy_self_refused():
    root = os.path.join(W, 'runner16'); queue(root, 'Q_V2', files=[('RUN', '5_judge_RBSCOUT_HCDEFS.job.sh')]); queue(root, 'Q_V16')
    rc, o = run('relq', '--runner', root, '--seat', 'SCOUT')
    assert rc == 3 and 'REFUSED BUSY_SELF' in o, (rc, o)
@case
def t17_relq_none_live_refused():
    root = os.path.join(W, 'runner17'); queue(root, 'Q_V1', age=120)
    rc, o = run('relq', '--runner', root, '--seat', 'SCOUT')
    assert rc == 3 and 'REFUSED NO_QUEUE' in o, (rc, o)
@case
def t18_usage():
    rc, o = run()
    assert rc == 2 and 'usage' in o.lower(), (rc, o)
def main():
    ok = 0
    for f in CASES:
        try: f(); ok += 1; print('OK %s' % f.__name__)
        except Exception as e: print('FAIL %s: %r' % (f.__name__, e))
    print('TESTS %d of %d (tool %s)' % (ok, len(CASES), TOOL)); return 0 if ok == len(CASES) else 1
if __name__ == '__main__': sys.exit(main())
