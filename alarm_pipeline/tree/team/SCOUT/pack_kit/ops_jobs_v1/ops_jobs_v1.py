#!/usr/bin/env python3
"""ops_jobs_v1.py (SCO-A137 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; built test first, tests/test_ops_jobs_v1.py).
The bridge-row words of ALARM_BUILD and work/JOBS.tsv (gaps GV15-07 and GV15-08), from the run kit's env and the bridge's own records:
  python3 -B ops_jobs_v1.py nextop --ledger $LED --task $RK_TASK [--jobs $RK_WORK/JOBS.tsv]   <op>: the next free <TASK>-OP<nn>
  python3 -B ops_jobs_v1.py relq --runner $ROOTQ --seat $RK_SEAT                                <Q>: the first live empty rel queue
  python3 -B ops_jobs_v1.py add --jobs $RK_WORK/JOBS.tsv --ledger $LED --op <op> --step <STEP> --purpose "<why>" --out <bridge output file>
  python3 -B ops_jobs_v1.py done --jobs $RK_WORK/JOBS.tsv --op <op> --out <the opdone output file>
  python3 -B ops_jobs_v1.py check --jobs $RK_WORK/JOBS.tsv --ledger $LED --task $RK_TASK
$LED, $RK_TASK, $RK_SEAT, $RK_WORK and $ROOTQ are lines of ops/RUN_ENV.sh (run_kit_v2 init through run_kit_v1). nextop: the highest
<TASK>-OP<nn> in the ledger (any status) and in JOBS.tsv, plus 1 (OP01 when none; OP00 is the SMOKE no-intent probe, never a job).
relq: among the Q_* folders of the runner root with an IN folder, by number: NOT_LIVE when runner.heartbeat is 60 s old or more or
absent, BUSY when IN or RUN holds a .job.sh; the first live empty one is printed "RELQ <Q>" (mac_desk_v48 rel_queue's own rule; the
bridge checks again when it files). BUSY_SELF when any queue holds a _judge_RB<SEAT>_ job (one rel job per seat). add: after a rel or
kitq filing, the op's INTENT row in the ledger gives the job number and the bridge output file gives its one job name <num>_judge_...;
it appends "utc op job step purpose" (utc from date -u; header utc op_id job step purpose, made on first use). done: after opdone
passed, the output's "RELBRIDGE OPDONE <op> job <num> (...)" line, for the job of that op's row, is appended as "<op> opdone" with the
bridge's words. check: the JOBS.tsv job rows against the ledger INTENT jobs of the task: SAME (rc 0) or DIFFER (rc 3), the census the
run kit's bind takes (run_kit_v1 jobs_tsv). Refusals write nothing: BAD_LEDGER, BAD_JOBS, BAD_WORD, BAD_FIELD, NO_INTENT, NO_JOBNAME,
DUP_OP, NOT_FILED, NO_OPDONE, DUP_DONE, NO_FILE, NO_QUEUE, BUSY_SELF. rc 0 done, 3 refused, 2 usage. Reads the runner root, files no job."""
import fcntl, json, os, re, subprocess, sys, time
LH = ['id', 'status', 'utc', 'text']; JH = ['utc', 'op_id', 'job', 'step', 'purpose']
LIVE_S = 60
USAGE = 'usage: ops_jobs_v1.py nextop|relq|add|done|check (see the docstring)'
class Refused(Exception):
    def __init__(self, word, why): Exception.__init__(self, word); self.word, self.why = word, why
def utc():
    return subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout.strip()
def ledger(p):
    if not os.path.exists(p): return []
    L = open(p, encoding='utf-8').read().split('\n')
    if L[0].split('\t') != LH: raise Refused('BAD_LEDGER', '%s header is not %s' % (p, ' '.join(LH)))
    return [l.split('\t') for l in L[1:] if l]
def jobs(p):
    if not os.path.exists(p): return []
    L = open(p, encoding='utf-8').read().split('\n')
    if L[0].split('\t') != JH: raise Refused('BAD_JOBS', '%s header is not %s' % (p, ' '.join(JH)))
    return [l.split('\t') for l in L[1:] if l]
def task_word(t):
    if not re.fullmatch(r'[A-Z]{2,5}-A[0-9]+', t): raise Refused('BAD_WORD', 'task %r' % t)
    return t
def intent_job(led, op):
    J = []
    for r in ledger(led):
        if len(r) == 4 and r[0] == op and r[1] == 'INTENT':
            try: J.append(str(json.loads(r[3]).get('job', '')))
            except ValueError: pass
    if len(J) != 1 or not J[0].isdigit(): raise Refused('NO_INTENT', '%d INTENT rows of %s with a job number in %s, expected 1' % (len(J), op, led))
    return J[0]
def append(p, row):
    for x in row:
        if '\t' in x or '\n' in x: raise Refused('BAD_FIELD', 'a tab or newline in %r' % x)
    fd = os.open(p, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    with os.fdopen(fd, 'a', encoding='utf-8') as out:
        fcntl.flock(out.fileno(), fcntl.LOCK_EX)
        out.write(('\t'.join(JH) + '\n' if os.path.getsize(p) == 0 else '') + '\t'.join(row) + '\n')
    print('JOBS ROW %s -> %s' % (' | '.join(row), p))
def cmd_nextop(o):
    t = task_word(o['--task']); rx = re.compile(r'^%s-OP([0-9]{2,})$' % re.escape(t))
    ids = [r[0] for r in ledger(o['--ledger'])] + ([r[1] for r in jobs(o['--jobs'])] if '--jobs' in o else [])
    n = max([int(m.group(1)) for m in (rx.match(i) for i in ids) if m] + [0])
    print('NEXTOP %s-OP%02d' % (t, n + 1)); return 0
def cmd_relq(o):
    root, seat = o['--runner'], o['--seat']
    if not re.fullmatch(r'[A-Z][A-Z0-9]{0,11}', seat): raise Refused('BAD_WORD', 'seat %r' % seat)
    qs = sorted((d for d in (os.listdir(root) if os.path.isdir(root) else []) if re.fullmatch(r'Q_[A-Z0-9]{1,16}', d) and os.path.isdir(os.path.join(root, d, 'IN'))),
                key=lambda d: (int(re.sub(r'\D', '', d) or 0), d))
    jf = lambda q: [(s, f) for s in ('IN', 'RUN') if os.path.isdir(os.path.join(root, q, s)) for f in sorted(os.listdir(os.path.join(root, q, s))) if f.endswith('.job.sh')]
    mine = ['%s/%s/%s' % (q, s, f) for q in qs for s, f in jf(q) if ('_judge_RB%s_' % seat) in f]
    if mine: raise Refused('BUSY_SELF', 'one rel job per seat at a time: %s (relwait it first)' % ', '.join(mine))
    pick = None
    for q in qs:
        try: age = time.time() - os.stat(os.path.join(root, q, 'runner.heartbeat')).st_mtime
        except OSError: age = None
        if age is None or age >= LIVE_S: print('%s NOT_LIVE (heartbeat %s)' % (q, 'absent' if age is None else '%d s old' % age)); continue
        if jf(q): print('%s BUSY (%s)' % (q, ', '.join('%s/%s' % x for x in jf(q)))); continue
        print('%s LIVE EMPTY' % q)
        if pick is None: pick = q
    if pick is None: raise Refused('NO_QUEUE', 'no live empty queue under %s' % root)
    print('RELQ %s' % pick); return 0
def cmd_add(o):
    op = o['--op']; J = jobs(o['--jobs'])
    if any(r[1] == op for r in J if len(r) > 1): raise Refused('DUP_OP', '%s already has a job row in %s' % (op, o['--jobs']))
    num = intent_job(o['--ledger'], op)
    if not os.path.isfile(o['--out']): raise Refused('NO_FILE', 'no bridge output %s' % o['--out'])
    names = sorted(set(re.findall(r'(?<![0-9])(%s_judge_[A-Za-z0-9_]+)' % num, open(o['--out'], encoding='utf-8', errors='replace').read())))
    if len(names) != 1: raise Refused('NO_JOBNAME', '%d job names %s_judge_... in %s (%s), expected 1' % (len(names), num, o['--out'], ', '.join(names) or 'none'))
    append(o['--jobs'], [utc(), op, names[0], o['--step'], o['--purpose']]); return 0
def cmd_done(o):
    op = o['--op']; J = jobs(o['--jobs'])
    R = [r for r in J if len(r) > 2 and r[1] == op]
    if len(R) != 1: raise Refused('NOT_FILED', '%d job rows of %s in %s, expected 1 (ops_jobs_v1 add after filing)' % (len(R), op, o['--jobs']))
    if any(r[1] == op + ' opdone' for r in J if len(r) > 1): raise Refused('DUP_DONE', '%s already has its opdone row' % op)
    num = re.match(r'^([0-9]+)', R[0][2]).group(1)
    if not os.path.isfile(o['--out']): raise Refused('NO_FILE', 'no opdone output %s' % o['--out'])
    W = [l for l in open(o['--out'], encoding='utf-8', errors='replace').read().split('\n') if l.startswith('RELBRIDGE OPDONE %s job %s (' % (op, num))]
    if len(W) != 1: raise Refused('NO_OPDONE', '%d lines "RELBRIDGE OPDONE %s job %s (" in %s, expected 1' % (len(W), op, num, o['--out']))
    append(o['--jobs'], [utc(), op + ' opdone', W[0].strip()]); return 0
def cmd_check(o):
    t = task_word(o['--task']); lj = []
    for r in ledger(o['--ledger']):
        if len(r) == 4 and r[1] == 'INTENT':
            try: x = json.loads(r[3])
            except ValueError: continue
            if isinstance(x, dict) and x.get('task') == t and str(x.get('job', '')).isdigit(): lj.append(str(x['job']))
    jt = [re.match(r'^([0-9]+)', r[2]).group(1) for r in jobs(o['--jobs']) if len(r) >= 3 and r[1] and ' ' not in r[1] and re.match(r'^[0-9]+', r[2])]
    same = sorted(lj) == sorted(jt)
    print('census JOBS.tsv %d: %s | ledger INTENT %d: %s | %s' % (len(jt), ' '.join(jt) or 'none', len(lj), ' '.join(lj) or 'none', 'SAME' if same else 'DIFFER'))
    return 0 if same else 3
SPEC = {'nextop': (('--ledger', '--task'), ('--jobs',)), 'relq': (('--runner', '--seat'), ()), 'add': (('--jobs', '--ledger', '--op', '--step', '--purpose', '--out'), ()),
        'done': (('--jobs', '--op', '--out'), ()), 'check': (('--jobs', '--ledger', '--task'), ())}
def main(a):
    if not a or a[0] not in SPEC or len(a[1:]) % 2: print(USAGE); return 2
    need, opt = SPEC[a[0]]; o = dict(zip(a[1::2], a[2::2]))
    if len(o) * 2 != len(a) - 1 or any(k not in o for k in need) or any(k not in need + opt for k in o): print(USAGE); return 2
    try: return {'nextop': cmd_nextop, 'relq': cmd_relq, 'add': cmd_add, 'done': cmd_done, 'check': cmd_check}[a[0]](o)
    except Refused as e: print('REFUSED %s: %s' % (e.word, e.why)); return 3
if __name__ == '__main__': sys.exit(main(sys.argv[1:]))
