#!/usr/bin/env python3
"""pipe_mac_v1.py (SCO-A162 for SCOUT, 6 Nov 2026; the owner 22:02 Berlin "Can't you run it with remote control?"). TEST, NOT REVIEWED.
The Mac mode of alarm_pipeline_v1_1 (ALARM_PIPELINE_V1_1; pipeline file beside this folder, sha16 pinned, loaded read-only,
never edited) runs its 22 steps INSIDE ONE RUNNER JOB on the Mac, with Mac paths, and no VM bridge:
  - the step logic, the parsers and every STEP_<nn>_<NAME>.json are the pipeline's own (one_move, write_step, parse_kit_receipts,
    parse_rel, parse_card_job, the own steps);
  - only the job layer is replaced (file_job and finish_job): a rel step runs its pinned INSTALL tool directly (the same script, pin,
    --settings and arguments the bridge's rel job runs, in the run folder) and keeps its output beside the logs with the bridge's
    "BRIDGE END rc <n>" line; a kitq step runs queue_job_v16 itself on the Mac (--dry first, then the filing), and the CARD step
    files the pipeline's own card job; a kit job gets the bridge's header (pipe_kitq_v1: '# JOB <file name>', '# TITLE: <kit title>',
    TASK, OP), and a GRADE job filed without it is read through a header view (grade_view); both are polled through their .status files in the runner (every --poll-s seconds, at most
    --budget-s in all); the VM bridge's typed ops ledger (op ids, opdone) is not used: each PENDING says op MAC;
  - the settings are the run folder's SETTINGS.json with every VM path mapped to the Mac (--vm-prefix to --mac-home), python the
    Mac interpreter, settings_env the Alarm folder's SETTINGS_LOCAL.env, mac_map empty, card_job_template the released
    CARD_JOB_TEMPLATE_V3.sh of ALARM_UNDERSTAND_V1_2 (fast CARD) and card_queue a live empty queue of the runner, picked when the card job is filed;
    the result is written beside as MAC_SETTINGS.json (SETTINGS.json is never changed).
  python3 -B pipe_mac_v1.py run <pipe folder> [--retry-stop N] [--budget-s 2700] [--poll-s 5] [--until N]
      --retry-stop N: a STOP_<N>_*.json is moved to filed/ first (as alarm_pipeline_v1 retry); a PENDING_<N>.json left by the VM
      is then finished from its runner status and receipts, never refiled.
      --refile-failed N: a PENDING_<N>.json whose job ENDED with a nonzero exit is moved to filed/ so the step is filed again; a job
      not ended or ended exit 0 refuses (exit 2): a finished job is never refiled.
Prints the pipeline's lines (DONE, WAIT, STOP) and the step table; appends one row per move to <pipe folder>/TIMES.tsv (utc, step, rc,
seconds, line): the per-step seconds are the sum of a step's rows. Exit 0 DONE ALL or --until reached, 10 budget spent while a job
runs (run again: the PENDING file resumes it), 3 a STOP, 2 refused."""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, os, re, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

PIPE = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'alarm_pipeline_v1_1.py')   # the edition's own pipeline
PIPE_PIN = '236b27f51f4b2a10'
INSTALL = '<RELEASE_ROOT>/Alarm/alarm/ALARM_V1_21_16_6'   # Alarm/alarm current from job 20270384
MAC_SETTINGS_ENV = INSTALL + '/settings/SETTINGS_LOCAL.env'
MAC_PY = '<PYTHON>'
CARD_TPL = ('<RELEASE_ROOT>/Alarm/alarm_understand/ALARM_UNDERSTAND_V1_2/tree/team/RESEARCH/PLAYGROUND/tools/PG20261105_alarm_understand/'
            'code/CARD_JOB_TEMPLATE_V3.sh')   # V1_2 carries the draw edition where mech_cards_run_v2 looks by default (job 20270289 exit 7)
CARD_TPL_PIN = 'f856dc3c6667d6ce'
QJ16 = 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/queue_job_v16.py'
KITQ_CHILD = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pipe_kitq_v1.py')
HC = '01_Detection/tree/team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/'
TOOLS = {   # mac_desk_v49 TOOLS (MAC_DESK_V49_1), the same scripts and pins
    'hc_defs_v4': (HC + 'hc_defs_v4_to20251231.py', 'ca8fb06e38940270', True),
    'true_gate_check': ('03_Grading/tree/tools/true_gate/true_gate_v3.py', 'd8d7fc77b9abf87a', False),
    'novelty_v5': ('08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v5.py', '4ac3b0b1a0a46e9f', True),
    'ledger_add_v7': ('Agentic/tree/ALARM_DESIGN/KIT_V5/tools/ledger_add_v7.py', '95ab96bb2c66b59a', True)}


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def load_pipe(path=None, pin=None):
    path = path or os.environ.get('PIPE_MAC_PIPE') or PIPE
    want = pin if pin is not None else os.environ.get('PIPE_MAC_PIPE_PIN', PIPE_PIN)
    if want and sha16(path) != want:
        raise SystemExit('REFUSED PIN_CHANGED %s is %s, pinned %s' % (path, sha16(path), want))
    sp = importlib.util.spec_from_file_location('alarm_pipeline_v1_mac', path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def mac_settings(S, vm_prefix, mac_home, extra):
    """every string (and list item) starting with vm_prefix mapped to mac_home; then the Mac keys"""
    def mp(v):
        if isinstance(v, str):
            return mac_home + v[len(vm_prefix):] if v.startswith(vm_prefix) else v
        if isinstance(v, list):
            return [mp(x) for x in v]
        return v
    M = {k: mp(v) for k, v in S.items() if not k.startswith('note')}
    M.update(extra)
    left = [k for k, v in M.items() if vm_prefix in json.dumps(v)]
    if left:
        raise SystemExit('REFUSED VM_PATH_LEFT %s' % left)
    return M


def live_queue(root, now=None, fresh_s=180):
    """a live, empty queue of the runner root: a heartbeat younger than fresh_s, no runner.stop, nothing in RUN, no job in IN"""
    now = now or time.time()
    for q in sorted(os.listdir(root), key=lambda x: (len(x), x)):
        d = os.path.join(root, q)
        if not re.fullmatch(r'Q_V\d+', q) or not os.path.isdir(d):
            continue
        hb = os.path.join(d, 'runner.heartbeat')
        if os.path.exists(os.path.join(d, 'runner.stop')) or not os.path.isfile(hb) or now - os.path.getmtime(hb) > fresh_s:
            continue
        busy = [x for x in os.listdir(os.path.join(d, 'RUN'))] if os.path.isdir(os.path.join(d, 'RUN')) else ['?']
        inq = [x for x in os.listdir(os.path.join(d, 'IN')) if x.endswith('.job.sh')] if os.path.isdir(os.path.join(d, 'IN')) else ['?']
        if not busy and not inq:
            return q
    return None


def grade_view(p, A):
    """a GRADE job filed without the bridge's header (no '# TITLE:'; drill K job 20270282, filed by pipe_mac_v1 before pipe_kitq_v1):
    the card job's bundle reads a view: <pipe>/grade_view/<Q>/DONE/<name>.job.sh = the DONE text with the bridge's header (kit_text, the
    same lines, nothing else) and logs/<name>.status a copy; the runner's own files are never touched. None when the job has the header."""
    g = p.done(11)['numbers']; num = g['job_tag'].split('_')[0]
    hits = []
    for q in sorted(os.listdir(p.S['rootq'])):
        d = os.path.join(p.S['rootq'], q, 'DONE')
        if q.startswith('Q_') and os.path.isdir(d):
            hits += [(q, x[:-len('.job.sh')]) for x in os.listdir(d) if x.startswith(num + '_') and x.endswith('.job.sh')]
    if len(hits) != 1:
        raise A.Stop('NO_GRADE_JOB', '%d DONE files of GRADE job %s in %s' % (len(hits), num, p.S['rootq']))
    q, name = hits[0]
    text = open(os.path.join(p.S['rootq'], q, 'DONE', name + '.job.sh')).read()
    if '\n# TITLE: ' in text:
        return None
    import pipe_kitq_v1 as K
    seat = re.match(r'^([A-Z][A-Z0-9]{0,11})_', p.I['run']).group(1)
    new = K.kit_text(text, name, num, seat, 'GRADE', p.I['idea'], p.I['task'], 'MAC')
    v = p.p('grade_view')
    for sub in ('DONE', 'logs'):
        os.makedirs(os.path.join(v, q, sub), exist_ok=True)
    jp = os.path.join(v, q, 'DONE', name + '.job.sh')
    if not os.path.exists(jp):
        open(jp, 'x').write(new)
        open(os.path.join(v, q, 'logs', name + '.status'), 'x').write(open(os.path.join(p.S['rootq'], q, 'logs', name + '.status')).read())
    return v


def install(A, cfg):
    """the job layer of the released pipeline replaced for the Mac; everything else is the pipeline's"""
    Stop, Wait = A.Stop, A.Wait

    def pending(p, n, **kw):
        pend = dict(step=n, filed=A.utc(), op='MAC', mode='pipe_mac_v1', **kw)
        A.jwrite(p.p('PENDING_%02d.json' % n), pend)
        return pend

    def file_job(p, n, name, kind):
        if kind == 'rel':
            a = A.rel_args(p, n); tool, args = a[0], a[1:]
            # as the bridge (mac_desk_v49): every path word reaches the tool as an absolute Mac path, a relative one from RUN
            # (novelty_v5 reads a relative list under ALARM_DESIGN, not the working folder: E2E job 20270397 STOP 05)
            args = [x if (x.startswith('-') or os.path.isabs(x) or '/' not in x) else os.path.join(p.rd, x) for x in args]
            if tool not in TOOLS:
                raise Stop('NOT_ALLOWED', 'rel tool %s' % tool)
            rel, pin, st = TOOLS[tool]
            script = os.path.join(cfg['install'], rel)
            if cfg.get('pins', True) and sha16(script) != pin:
                raise Stop('PIN_CHANGED', '%s is %s, pinned %s' % (script, sha16(script), pin))
            argv = [p.S['python'], '-B', script] + (['--settings', p.S['settings_env']] if st else []) + args
            lg = p.log(n, 'relwait')   # the bridge's log name: st_classify reads step 16's output ending relwait.out (job 20270380)
            with open(lg, 'w') as f:
                f.write('# CMD (cwd %s) %s\n' % (p.rd, ' '.join(argv))); f.flush()
                rc = subprocess.run(argv, stdout=f, stderr=subprocess.STDOUT, cwd=p.rd, stdin=subprocess.DEVNULL,
                                    timeout=cfg.get('rel_timeout', 1800)).returncode
                f.write('BRIDGE END rc %d\n' % rc)
            return pending(p, n, name=name, kind='rel', job='MACREL_%02d_%s' % (n, tool), num='-', queue='-', rc=rc, out=lg)
        if kind == 'kitq':
            a = A.kitq_args(p, n)
            qj = [p.S['python'], '-B', cfg.get('kitq_child', KITQ_CHILD), os.path.join(cfg['install'], QJ16), '--settings', p.S['settings_env'],
                  p.I['run']] + a
            env = {'PIPE_TASK': p.I['task'], 'PIPE_OP': 'MAC'}
            rc, t = p.sh(n, 'macdry', qj + ['--dry'], timeout=120, env=env)
            if rc != 0 or 'DRY RUN OK' not in t:
                old = (p.I.get('replay_jobs') or {}).get(a[0])     # the pipeline's own replay rule: the kit refuses a re-run, the
                if p.I['registry_mode'] == 'replay' and old and re.search(r'REFUSED: ALREADY', t):   # earlier job is adopted, read back
                    pend = A.adopt_old(p, n, name, a[0], str(old), A.lines_with(t, r'REFUSED: ALREADY')[0])
                    pend['mode'] = 'pipe_mac_v1'; A.jwrite(p.p('PENDING_%02d.json' % n), pend); return pend
                raise Stop('DRY_REFUSED', 'queue_job_v16 --dry rc %d (%s)' % (rc, p.log(n, 'macdry')))
            rc, t = p.sh(n, 'macfile', qj, timeout=120, env=env)
            m = re.search(r'QUEUED (Q_\w+) (\d+) (\S+)\.job\.sh', t)
            if rc != 0 or not m:
                raise Stop('FILE_REFUSED', 'queue_job_v16 rc %d, no QUEUED line (%s)' % (rc, p.log(n, 'macfile')))
            return pending(p, n, name=name, kind='kitq', job=m.group(3), num=m.group(2), queue=m.group(1), file_log=p.log(n, 'macfile'))
        q = cfg['pick'](p.S['rootq'])
        if not q:
            raise Wait('no live empty queue in %s for the card job' % p.S['rootq'])
        p.S['card_queue'] = q
        view = grade_view(p, A)
        tpl0 = p.S['card_job_template']
        if view:
            p.S['card_job_template'] = tpl0.replace('--from-job {GRADE_NUM} --runner {RN}', '--from-job {GRADE_NUM} --runner %s' % view, 1)
            if p.S['card_job_template'] == tpl0:
                raise Stop('TEMPLATE', 'the card template has no "--from-job {GRADE_NUM} --runner {RN}" for the GRADE view')
        try:
            rc, t = A.file_own_job(p, n, 'MAC')
        finally:
            p.S['card_job_template'] = tpl0
        m = re.search(r'OWNJOB QUEUED (Q_\w+) (\d+) (\S+)\.job\.sh', t)
        if rc != 0 or not m:
            raise Stop('FILE_REFUSED', 'card job rc %d, no OWNJOB QUEUED line' % rc)
        return pending(p, n, name=name, kind='job', job=m.group(3), num=m.group(2), queue=m.group(1), grade_view=view or '-')

    def finish_job(p, n, name, kind, pend):
        if kind == 'rel' and pend.get('mode') == 'pipe_mac_v1':
            t = open(pend['out']).read()
            N = dict(job=pend['job'], job_num='-', queue='-', op='MAC', exit=str(pend['rc']), mode='pipe_mac_v1')
            if pend['rc'] != 0:
                raise Stop('JOB_EXIT', 'rel %s rc %d (%s)' % (pend['job'], pend['rc'], pend['out']))
            N.update(A.parse_rel(p, n, t))
            return dict(numbers=N, outputs=A.outs([pend['out']]))
        kv, sp = A.status_of(p, pend)
        if kv is None:
            raise Wait('job %s on %s not ended (%s)' % (pend['job'], pend['queue'], sp))
        N = dict(job=pend['job'], job_num=pend['num'], queue=pend['queue'], op=pend.get('op', 'MAC'), exit=kv['exit'], status_file=sp,
                 seconds=kv.get('seconds', ''), mode='pipe_mac_v1')
        if pend.get('grade_view', '-') != '-':
            N['grade_view'] = pend['grade_view']
        if pend.get('mode') != 'pipe_mac_v1':
            N['filed_by'] = 'the VM bridge (op %s); finished on the Mac without opdone' % pend.get('op')
        if kv['exit'].strip() != '0':
            raise Stop('JOB_EXIT', 'job %s exit=%s (%s)' % (pend['job'], kv['exit'], sp))
        files = [sp]
        if kind == 'kitq':
            K, fs = A.parse_kit_receipts(p, n, pend['num'], pend['job'])
        else:
            K, fs = A.parse_card_job(p, n, pend)
        N.update(K); files += fs
        return dict(numbers=N, outputs=A.outs(files))

    A.file_job = file_job
    A.finish_job = finish_job


def run(argv, A=None, cfg=None, sleep=time.sleep, clock=time.time):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['run']); ap.add_argument('folder')
    ap.add_argument('--refile-failed', type=int, default=0)
    ap.add_argument('--retry-stop', type=int, default=0); ap.add_argument('--budget-s', type=float, default=2700)
    ap.add_argument('--poll-s', type=float, default=5); ap.add_argument('--until', type=int, default=22)
    ap.add_argument('--vm-prefix', default='<VM_SESSION>/mnt'); ap.add_argument('--mac-home', default='<HOME>')
    a = ap.parse_args(argv)
    A = A or load_pipe()
    cfg = dict(dict(install=INSTALL, pick=live_queue, pins=True), **(cfg or {}))
    f = os.path.abspath(a.folder)
    S = A.jload(os.path.join(f, 'SETTINGS.json'))
    tpl = cfg.get('card_tpl', CARD_TPL)
    if cfg.get('pins', True) and sha16(tpl) != CARD_TPL_PIN:
        print('REFUSED PIN_CHANGED %s' % tpl); return 2
    extra = dict(python=cfg.get('python', MAC_PY), mac_python=cfg.get('python', MAC_PY), settings_env=cfg.get('settings_env', MAC_SETTINGS_ENV),
                 mac_map=[], card_job_template=open(tpl).read(), card_queue='(picked when filed)')
    M = mac_settings(S, a.vm_prefix, a.mac_home, extra)
    ms = os.path.join(f, 'MAC_SETTINGS.json')
    if os.path.exists(ms) and A.jload(ms) != M:
        os.replace(ms, os.path.join(f, 'filed', 'MAC_SETTINGS.json.' + A.stamp()))
    A.jwrite(ms, M)
    install(A, cfg)
    p = A.P(f)
    p.S = M; p.fr = M['forensics_root']; p.rd = os.path.join(p.fr, 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', p.I['run'])
    if a.retry_stop:
        for x in sorted(os.listdir(f)):
            if x.startswith('STOP_%02d_' % a.retry_stop) and x.endswith('.json'):
                os.makedirs(os.path.join(f, 'filed'), exist_ok=True)
                os.replace(os.path.join(f, x), os.path.join(f, 'filed', x + '.retried_mac_' + A.stamp())); print('RETRY moved %s aside' % x)
    if a.refile_failed:
        pq = p.p('PENDING_%02d.json' % a.refile_failed)
        if os.path.exists(pq):
            pend = A.jload(pq); kv, sp = A.status_of(p, pend)
            if kv is None or kv['exit'].strip() == '0':
                print('REFUSED REFILE: job %s has not ended or ended exit 0: it is finished, never refiled' % pend['job']); return 2
            os.makedirs(os.path.join(f, 'filed'), exist_ok=True)
            os.replace(pq, os.path.join(f, 'filed', 'PENDING_%02d.json.failed_exit%s_%s' % (a.refile_failed, kv['exit'].strip(), A.stamp())))
            print('REFILE: job %s ended exit %s; its PENDING moved to filed/, the step is filed again' % (pend['job'], kv['exit'].strip()))
    t0 = clock(); rc = 0; tl = os.path.join(f, 'TIMES.tsv'); last = clock()
    if not os.path.exists(tl):
        open(tl, 'w').write('utc\tstep\trc\tseconds\tline\n')
    while True:
        nxt = next((n for n, _, _ in getattr(A, 'ORDER', A.STEPS) if not p.done(n)), None)   # v1_1 runs 21 before 20
        if nxt is None or nxt > a.until:
            print('DONE ALL' if nxt is None else 'DONE UNTIL %02d' % a.until); rc = 0; break
        rc, line = A.one_move(p); print(line); sys.stdout.flush()
        now = clock()   # TIMES.tsv: one row per move, seconds since the previous move ended (the poll sleep counts to the step it waits on)
        with open(tl, 'a') as w:
            w.write('%s\t%02d\t%d\t%.1f\t%s\n' % (A.utc(), nxt, rc, now - last, line.replace('\t', ' ')[:160]))
        last = now
        if rc == 3:
            break
        if rc == 10:
            if clock() - t0 > a.budget_s:
                print('BUDGET %.0f s spent while a job runs: run again to resume' % a.budget_s); break
            if 'job MACREL_' not in line:      # a rel step already ran inside file_job: finish it at once, no poll sleep
                sleep(a.poll_s)
    print(A.table(p))
    return rc


if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
