#!/usr/bin/env python3
"""pipe_kitq_v1.py (SCO-A162 for SCOUT, 6 Nov 2026). TEST, NOT REVIEWED. pipe_mac_v1's kitq child: queue_job_v16 (pinned by its caller)
loaded and run as it is, with the one header the VM bridge (mac_desk_v49 __kitqops, kit_text) gives every kit job: the twin's first line
becomes '# JOB <runner file name> -- the runner's file name (mac_desk_v43 kitq); the kit title is the TITLE line', and the old JOB text
goes on '# TITLE: ', then '# TASK: <task>', '# OP: <op>' close the comment block. The bundle builder and every later kit reader read that
layout (bundle_builder_v1 NOT_A_GRADE_JOB without it, drill K job 20270284). The allocator claim is hooked only to learn the number.
  python3 -B pipe_kitq_v1.py <queue_job_v16.py> --settings S <RUN> <KIND> <IDEA> <ITEMS...> [--dry]     env PIPE_TASK, PIPE_OP"""
import sys
sys.dont_write_bytecode = True
import builtins, importlib.util, os, re


def kit_text(body, name, num, seat, kind, idea, task, op):
    """mac_desk_v49 kit_text, the same lines"""
    lines = body.split('\n')
    k = next((i for i, l in enumerate(lines) if not l.startswith('#')), len(lines))
    head = lines[:k]
    old = '# JOB %s_%s_%s_%s -- ' % (num, seat, kind, idea)
    if not (k >= 1 and head[0].startswith(old) and [l for l in head if l.startswith('# JOB')] == head[:1]):
        raise SystemExit('REFUSED: KIT_HEADER the kit job does not open with one %r line' % old)
    if [l for l in head if re.match(r'#\s*(TASK|OP|TITLE)\b', l)]:
        raise SystemExit('REFUSED: KIT_HEADER the kit job already has a TASK, OP or TITLE line')
    if k + 3 > 10:
        raise SystemExit('REFUSED: KIT_HEADER the comment block has %d lines' % k)
    new = ['# JOB %s -- the runner\'s file name (mac_desk_v43 kitq); the kit title is the TITLE line' % name] + head[1:] + [
        '# TITLE: ' + head[0][len('# JOB '):], '# TASK: ' + task, '# OP: ' + op]
    return '\n'.join(new + lines[k:])


def main(a):
    qj, rest = a[0], a[1:]
    run, kind, idea = rest[2], rest[3], rest[4]
    seat = re.match(r'^([A-Z][A-Z0-9]{0,11})_\d{8}$', run).group(1)
    task, op = os.environ.get('PIPE_TASK', '-'), os.environ.get('PIPE_OP', 'MAC')
    sp = importlib.util.spec_from_file_location('queue_job_v16', qj); m = importlib.util.module_from_spec(sp)
    sys.modules['queue_job_v16'] = m; sp.loader.exec_module(m)
    Q = m.Q
    ctx = {'num': None, 'twins': 0}
    real = Q.subprocess

    class Sub(object):
        def __getattr__(self, k):
            return getattr(real, k)

        def run(self, cmd, *x, **k):
            r = real.run(cmd, *x, **k)
            if Q.CFG.get('ALLOC') and list(cmd) == list(Q.CFG['ALLOC']) + ['claim', seat, '1']:
                ids = [y for y in (r.stdout or '').split() if y.isdigit()]
                if r.returncode == 0 and len(ids) == 1:
                    ctx['num'] = ids[0]
            return r

    class Twin(object):
        def __init__(self, f, path):
            self.f, self.path = f, path

        def __enter__(self):
            return self

        def __exit__(self, *e):
            self.f.close(); return False

        def write(self, body):
            name = os.path.basename(self.path)[:-len('.job.sh')]
            want = '%s_judge_%s_%s_%s' % (ctx['num'], seat, kind, idea)
            if ctx['num'] is None or name != want or ctx['twins']:
                raise SystemExit('REFUSED: KIT_NAME the twin %s is not %s.job.sh (or a second twin)' % (self.path, want))
            ctx['twins'] += 1
            return self.f.write(kit_text(body, name, ctx['num'], seat, kind, idea, task, op))

    def hooked_open(path, mode='r', *x, **k):
        f = builtins.open(path, mode, *x, **k)
        if mode == 'x' and str(path).endswith('.job.sh') and os.path.basename(os.path.dirname(str(path))) == 'jobs':
            return Twin(f, str(path))
        return f
    Q.subprocess = Sub()
    Q.open = hooked_open
    try:
        return Q.main(rest)
    except Q.Refused as e:
        print('REFUSED: %s' % str(e).replace('USAGE queue_job_v15.py', 'USAGE queue_job_v16.py'), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
