#!/usr/bin/env python3
"""pipe_e2e_v2.py, V1_3 (SCO-A162R, 6 Nov 2026 23:xxZ): the pipeline alarm_pipeline_v1_3; a case passes on 22 of 22, or on the named
refusal its INPUT asks for (key e2e_expect, e.g. "01 INPUT BLOCK_NOT_GRADED": the STOP step, name and code must be exactly that); a
pipe_mac call that ends with an rc other than 0, 3 or 10 is a CRASH and fails the case; E2E_RESULT.tsv gains columns expect, verdict, pipe_rc.
Was: pipe_e2e_v1.py (SCO-A162, SCOUT, 6 Nov 2026; the owner 22:52 Berlin "We need tools that work", 22:53 "any date and any alarm"). TEST.
The pipeline's end-to-end acceptance: one command, no agent; each case is one INPUT.json run through all 22 steps by pipe_mac_v1 (the
released pipeline, Mac mode) in a NEW pipe folder; the INPUT is copied with task E2E-<case>-<HHMMSS> (the tools name their outputs by task, so each run is a new try identity);
per case: steps DONE, the STOP if any (code and why, read from STOP_<nn>_*.json),
per-step seconds (TIMES.tsv) and total seconds; an optional compare command per case (e.g. the WIDEBLOCKS replay against trial I).
  python3 -B pipe_e2e_v1.py <out root (new)> --template PIPE_SETTINGS_V3_TEMPLATE.json --home <@HOME@> --seat <SEAT>
        [--cards-root DIR] [--budget-s 3600] [--poll-s 5] CASE=INPUT.json[,COMPARE_CMD] ...
  COMPARE_CMD is run with {pipe} replaced by the pipe folder (rc 0 = equal; spaces split the words). --cards-root (default <out>/cards) keeps step 22's card hand-off out
  of the team's card tree. Writes <out>/E2E_RESULT.tsv (case, steps_done, stop, compare_rc, total_s, per_step_s) and prints one line per
  case: E2E PASS|FAIL <case> <steps> <seconds>. Exit 0 when every case reached 22 of 22 (and its compare is equal), else 1."""
import sys
sys.dont_write_bytecode = True
import json, os, subprocess, time
HERE = os.path.dirname(os.path.realpath(__file__))
PIPE = os.path.join(os.path.dirname(HERE), 'alarm_pipeline_v1_3.py'); PM = os.path.join(HERE, 'pipe_mac_v2.py')


def per_step(f):
    S = {}
    tl = os.path.join(f, 'TIMES.tsv')
    if os.path.exists(tl):
        for l in open(tl).read().splitlines()[1:]:
            x = l.split('\t'); S[int(x[1])] = round(S.get(int(x[1]), 0) + float(x[3]), 1)
    return S


def one(out, case, inp, cmp, a, py):
    f = os.path.join(out, case); cr = os.path.join(out, 'cards', case); os.makedirs(cr)
    t = open(a.template).read().replace('@HOME@', a.home).replace('@SEAT@', a.seat); S = json.loads(t)
    S['cards_root'] = cr if not a.cards_root else a.cards_root
    for k, v in (a.set or []):
        S[k] = v
    sp = os.path.join(out, case + '_SETTINGS.json'); json.dump(S, open(sp, 'w'), indent=1)
    I = json.load(open(inp)); I['task'] = 'E2E-%s-%s' % (case, a.stamp); expect = I.get('e2e_expect', '')   # a run's own identity: the tools name their outputs by task
    ip = os.path.join(out, case + '_INPUT.json'); json.dump(I, open(ip, 'w'), indent=1)
    t0 = time.time()
    rc = subprocess.run([py, '-B', PIPE, 'init', f, '--input', ip, '--settings', sp]).returncode
    if rc != 0:
        return dict(case=case, steps=0, stop='INIT rc %d' % rc, cmp='-', total=0, per={}, expect=expect, prc=rc, code='')
    rc = 10; prc = []
    while rc == 10 and time.time() - t0 < a.budget_s:
        rc = subprocess.run([py, '-B', PM, 'run', f, '--vm-prefix', a.home + '/mnt', '--budget-s', str(a.budget_s), '--poll-s', str(a.poll_s)]).returncode; prc.append(rc)
    done = sum(1 for n in range(1, 23) if any(x.startswith('STEP_%02d_' % n) for x in os.listdir(f)))
    st = [x for x in sorted(os.listdir(f)) if x.startswith('STOP_')]
    stop = '-'; code = ''
    if st:
        j = json.load(open(os.path.join(f, st[0]))); stop = '%s %s %s: %s' % (st[0][5:7], j.get('name'), j.get('code'), str(j.get('why'))[:200])
        code = '%s %s %s' % (st[0][5:7], j.get('name'), j.get('code'))
    c = '-'
    if cmp and done == 22:
        c = subprocess.run(cmp.replace('{pipe}', f).split()).returncode
    return dict(case=case, steps=done, stop=stop, cmp=c, total=round(time.time() - t0, 1), per=per_step(f), expect=expect, prc=rc, code=code)


def verdict(r):
    """PASS: 22 of 22 (compare equal) with no refusal asked, or exactly the refusal asked; CRASH: a pipe_mac rc other than 0, 3, 10"""
    if r['prc'] not in (0, 3, 10):
        return 'CRASH'
    if r['expect']:
        return 'PASS' if r['code'] == r['expect'] else 'FAIL'
    return 'PASS' if r['steps'] == 22 and r['cmp'] in ('-', 0) else 'FAIL'


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('cases', nargs='+')
    ap.add_argument('--template', required=True); ap.add_argument('--home', required=True); ap.add_argument('--seat', default='SCOUT')
    ap.add_argument('--cards-root', default=''); ap.add_argument('--budget-s', type=float, default=3600); ap.add_argument('--poll-s', type=float, default=5)
    ap.add_argument('--set', nargs=2, action='append', metavar=('KEY', 'VALUE'), help='a settings key for every case (e.g. tried_file <copy>)')
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        print('REFUSED OUT_EXISTS %s' % a.out); return 2
    os.makedirs(a.out); py = sys.executable; R = []; a.stamp = time.strftime('%H%M%S', time.gmtime())
    for c in a.cases:
        name, rest = c.split('=', 1); inp, _, cmp = rest.partition(',')
        r = one(a.out, name, inp, cmp, a, py); R.append(r)
        v = verdict(r)
        print('E2E %s %s %d %.0f %s' % (v, name, r['steps'], r['total'], ('refusal as asked: ' + r['stop']) if (v == 'PASS' and r['expect']) else ('' if v == 'PASS' else r['stop']))); sys.stdout.flush()
    with open(os.path.join(a.out, 'E2E_RESULT.tsv'), 'w') as w:
        w.write('case\tsteps_done\tstop\tcompare_rc\ttotal_s\tper_step_s\texpect\tverdict\tpipe_rc\n')
        for r in R:
            w.write('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (r['case'], r['steps'], r['stop'], r['cmp'], r['total'], json.dumps(r['per'], sort_keys=True), r['expect'] or '-', verdict(r), r['prc']))
    return 0 if all(verdict(r) == 'PASS' for r in R) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
