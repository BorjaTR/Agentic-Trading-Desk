#!/usr/bin/env python3
"""FAKE mac_desk_v48 for the pipeline tests (planted world only): rel, kitq (--dry), opdone, relwait. World: env FAKE_WORLD (FAKE.json)."""
import json, os, sys, time
W = os.environ['FAKE_WORLD']; F = json.load(open(os.path.join(W, 'FAKE.json')))
ROOTQ = os.path.join(W, 'rootq'); RD = os.path.join(W, 'fr', 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs')


def utc():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def claim():
    c = os.path.join(W, 'counter'); n = int(open(c).read()) + 1 if os.path.exists(c) else 30000001
    open(c, 'w').write(str(n)); return n


def intent(op, num):
    led = os.environ['LOOP_OPS_LEDGER']
    rows = [l.split('\t') for l in open(led).read().splitlines()[1:] if l]
    if any(r[0] == op for r in rows):
        print('RELBRIDGE REFUSED OP_USED: %s' % op); sys.exit(2)
    with open(led, 'a') as f:
        f.write('%s\tINTENT\t%s\t{"schema":"LOOP_RUNNER_OP_V1","task":"%s","job":"%d"}\n' % (op, utc(), os.environ['LOOP_TASK_ID'], num))


def job(q, name, body):
    open(os.path.join(ROOTQ, q, 'IN', name + '.job.sh'), 'w').write('# JOB %s\n# CORES 1\nset -u\n%s\n' % (name, body))


a = sys.argv[1:]
mode = a[0]
if mode == 'rel':
    run, tool = a[1], a[2]
    tag = {'hc_defs_v4': 'HCDEFS', 'novelty_v5': 'NOVELTY', 'true_gate_check': 'TGCHECK', 'ledger_add_v7': 'LEDGER'}[tool]
    if tool == 'ledger_add_v7':
        tag = 'LEDGER'
    key = tool + ('_' + a[3] if tool == 'ledger_add_v7' else '')
    if key in F.get('rel_refuse', []):
        print('RELBRIDGE REFUSED PATH_OUTSIDE: planted'); sys.exit(2)
    q = os.environ['MAC_DESK_QUEUE']; op = os.environ['LOOP_OP_ID']; num = claim(); intent(op, num)
    name = '%d_judge_RBSCOUT_%s' % (num, tag)
    out = F['rel_out'].get(key, 'ok\n')
    job(q, name, 'cat <<"XEOF"\n%sXEOF\nexit %d' % (out, F.get('exit', {}).get(key, 0)))
    print('RELBRIDGE OPS INTENT %s task %s job %d' % (op, os.environ['LOOP_TASK_ID'], num))
    print('RELBRIDGE QUEUED %s on %s (rel %s for %s); it never waits' % (name, q, tool, run))
elif mode == 'kitq':
    run, kind, idea = a[1], a[2], a[3]
    if '--dry' in a:
        if kind in F.get('dry_refuse', []):
            print('REFUSED: planted dry refusal'); sys.exit(2)
        if kind in F.get('dry_already', []):
            print("REFUSED: ALREADY GRADED ['V1']: never re-run; a change is a new variant"); sys.exit(2)
        print('DRY RUN OK: %s %s %s %s on Q_V1' % (run, kind, idea, a[4])); sys.exit(0)
    op = os.environ['LOOP_OP_ID']; num = claim(); intent(op, num)
    name = '%d_judge_SCOUT_%s_%s' % (num, kind, idea)
    rec = os.path.join(RD, run, 'receipts', '%d_%s_%s' % (num, kind, idea))
    src = os.path.join(W, 'fix', kind)
    omit = F.get('omit', {}).get(kind, '')
    body = 'mkdir -p %s && for f in %s/*; do b=$(basename "$f"); [ "$b" = "%s" ] || cp -R "$f" %s/; done\nexit %d' % (rec, src, omit or '-', rec, F.get('exit', {}).get(kind, 0))
    job('Q_V1', name, body)
    print('QUEUED Q_V1 %d %s.job.sh twin jobs/%s.job.sh sha16 0 IN 0 | RUNS %s RUNS' % (num, name, name, utc()))
elif mode == 'opdone':
    op, num = a[1], a[2]
    if op in F.get('opdone_fail', []) or ('ALL' in F.get('opdone_fail', [])):
        print('RELBRIDGE REFUSED NOT_TERMINAL: planted'); sys.exit(2)
    for q in os.listdir(ROOTQ):
        lg = os.path.join(ROOTQ, q, 'logs')
        for x in os.listdir(lg) if os.path.isdir(lg) else []:
            if x.startswith(num + '_') and x.endswith('.status'):
                kv = dict(l.split('=', 1) for l in open(os.path.join(lg, x)).read().splitlines() if '=' in l)
                name = x[:-7]
                led = os.environ['LOOP_OPS_LEDGER']
                with open(led, 'a') as f:
                    f.write('%s\tDONE\t%s\t{"schema":"LOOP_RUNNER_OP_V1","task":"T","job":"%s"}\n' % (op, utc(), num))
                print('RELBRIDGE OPDONE %s job %s (%s on %s, SUCCEEDED, exit %s) task T commit X; DONE is the runner\'s terminal record only, never a PASS' % (op, num, name, q, kv['exit']))
                sys.exit(0)
    print('RELBRIDGE REFUSED NOT_TERMINAL'); sys.exit(2)
elif mode == 'relwait':
    name = a[1]
    for q in os.listdir(ROOTQ):
        p = os.path.join(ROOTQ, q, 'logs', name + '.log')
        if os.path.exists(p):
            sys.stdout.write(open(p).read()); print('BRIDGE END rc 0'); sys.exit(0)
    print('no log'); sys.exit(2)
else:
    print('usage'); sys.exit(2)
