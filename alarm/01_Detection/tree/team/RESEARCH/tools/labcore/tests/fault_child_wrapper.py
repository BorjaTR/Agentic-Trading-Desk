"""fault_child_wrapper.py (TESTS ONLY; ctxprof_shared, 25 Oct 2026): run_parallel's Profile/Context worker behind a planted fault.
run_parallel runs `python3 -B fault_child_wrapper.py <the real worker command ...>` when RUN_PARALLEL_CHILD_WRAP names this file (its
sha16 then enters the run plan, so a wrapped run never stands for a real one). FAULT (environment) chooses the fault; the worker command's
arguments are ... <first> <last> <out root> [tail]: the wrapper finds first/last/out by position (the 6th, 7th and 8th after 'build').
  (unset)              run the real worker unchanged
  crash_after_first    run the real worker for its FIRST day only, then exit 3 (a worker that died after writing some days)
  partial              leave a half-written part folder (<part>.tmp_planted with one block, no index) for the first day, exit 9
  skip_last_ok         run the real worker without its LAST day and exit 0 (a worker that says success but did not write a day)
  commit_then_fail     run the real worker, plant RUN_MANIFEST.json (status COMPLETE) in the stage, exit 1
  only_day=<D>         fail (exit 4) unless the chunk is exactly day D..D (to check which days a resume reruns)
  tamper_receipt       Context only: run the real worker, then change every day receipt's keys_sha16 (the run must refuse)
NICE_LOG (environment): append this worker's nice value to that file first (the absolute-nice-10 test)."""
import os, subprocess, sys

cmd = sys.argv[1:]
fault = os.environ.get('FAULT', '')
if os.environ.get('NICE_LOG'):                                      # the worker's own nice, as the dispatcher set it (absolute nice 10)
    with open(os.environ['NICE_LOG'], 'a') as f:
        f.write('%d\n' % os.getpriority(os.PRIO_PROCESS, 0))
tool = 'context' if os.path.basename(cmd[2]).startswith('alarm_context') else 'profile'
fi = cmd.index('build') + 6        # profile: build lab code list settings subj FIRST LAST OUT [--window ..]; context: build lab code list subj level FIRST ...
first, last, out = cmd[fi], cmd[fi + 1], cmd[fi + 2]


def days(a, b):
    import datetime as dt
    d = dt.datetime.strptime(a, '%Y%m%d'); e = dt.datetime.strptime(b, '%Y%m%d'); out = []
    while d <= e:
        out.append(d.strftime('%Y%m%d')); d += dt.timedelta(days=1)
    return out


def with_range(a, b):
    c = list(cmd); c[fi], c[fi + 1] = a, b
    return c


if fault == '':
    sys.exit(subprocess.call(cmd))
if fault == 'crash_after_first':
    subprocess.call(with_range(first, first)); sys.exit(3)
if fault == 'partial':
    part = 'EPG.%s' % cmd[fi - 1] if tool == 'profile' else 'CTX.%s.%s' % (cmd[fi - 2], cmd[fi - 1])
    d = os.path.join(out, 'day=%s' % first, '%s.tmp_planted' % part); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'X.v.lz4'), 'wb').write(b'half')
    sys.exit(9)
if fault == 'skip_last_ok':
    ds = days(first, last)
    if len(ds) > 1:
        rc = subprocess.call(with_range(first, ds[-2]))
    else:
        rc = 0
    sys.exit(rc)
if fault == 'commit_then_fail':
    subprocess.call(cmd)
    open(os.path.join(out, 'RUN_MANIFEST.json'), 'w').write('{"schema": "RUN_MANIFEST_V1", "status": "COMPLETE", "exit_status": 0, "parts": {}}')
    sys.exit(1)
if fault == 'tamper_receipt':                                       # Context: the worker writes, then its day receipt is altered
    rc = subprocess.call(cmd)
    import glob, json as _j
    for rp in glob.glob(os.path.join(out, 'CTX_RECEIPTS_ED2', '*', 'day=*.json')):
        x = _j.load(open(rp)); x['keys_sha16'] = '0' * 16; open(rp, 'w').write(_j.dumps(x, indent=1, sort_keys=True) + '\n')
    sys.exit(rc)
if fault.startswith('only_day='):
    want = fault.split('=', 1)[1]
    if (first, last) != (want, want):
        sys.stderr.write('only_day=%s but the chunk is %s..%s\n' % (want, first, last)); sys.exit(4)
    sys.exit(subprocess.call(cmd))
sys.exit('unknown FAULT %r' % fault)
