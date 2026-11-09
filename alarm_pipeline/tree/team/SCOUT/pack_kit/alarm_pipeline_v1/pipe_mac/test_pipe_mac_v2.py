#!/usr/bin/env python3
"""test_pipe_mac_v2.py (SCO-A162R): test_pipe_mac_v1 on pipe_mac_v2 (M2 checks the rel tool ran in RUN by its cwd word; M3 the pipeline is alarm_pipeline_v1_3; M14 a replay adopts the run's one earlier receipts folder of a kind the input does not name).
test_pipe_mac_v1.py (SCO-A162 for SCOUT, 6 Nov 2026). TEST, NOT REVIEWED. Planted, seconds: the released alarm_pipeline_v1 (pinned)
driven by pipe_mac_v1's job layer on a planted run folder, a planted INSTALL (rel tool, queue_job_v16) and a planted runner.
  M1 settings: every VM path mapped, the Mac keys set, a VM path left refuses
  M2 rel (step 7 true_gate_check): the pinned tool runs in the run folder, STEP_07 holds the pipeline's parse_rel lines, op MAC
  M3 kitq (step 11 GRADE): --dry then the filing; WAIT while no status; after exit=0 STEP_11 = the pipeline's parse_kit_receipts
  M4 a VM-filed PENDING_06 with a STOP_06 (opdone failed): --retry-stop 6 finishes it from status and receipts, nothing refiled
  M5 a job that ends exit 3: STOP JOB_EXIT; a refused --dry: STOP DRY_REFUSED and nothing filed
  M6 budget: a job that never ends returns 10 with the BUDGET line and the PENDING kept for the next run
  M7 the card step picks a live empty queue (fresh heartbeat, no stop, nothing in RUN or IN)
  M8 a rel tool that exits 2: STOP JOB_EXIT with the tool's own output kept
  M9 a kit job filed on the Mac gets the bridge's header (# JOB <file name>, # TITLE: <kit title>, # TASK, # OP MAC)
  M11 --refile-failed: a job ended exit 6 is filed again (new PENDING); a job ended exit 0 refuses, nothing moved
  M2 also: a rel path word reaches the tool absolute from RUN (as the bridge); TIMES.tsv holds a row per move (step, rc, seconds); a rel step's output is logs/S<nn>_relwait.out, the bridge's name (st_classify reads step 16's by it)
  M13 replay: a kit dry refused ALREADY adopts the INPUT's replay job (no filing); write mode stops DRY_REFUSED
  M12 the card template is ALARM_UNDERSTAND_V1_2's V3 at its pin and the draw edition sits at mech_cards_run_v2's default place; the pipeline is the v1_1 beside
  M10 a GRADE job without that header: the card job reads a header view, the runner's own files untouched; with it: no view
Run: python3 -B test_pipe_mac_v1.py [M1 ...]   Env: PIPE_MAC_PIPE (the released pipeline file), MAC_SCRATCH. Exit 0 all passed."""
import sys
sys.dont_write_bytecode = True
import datetime as dt, io, contextlib, json, os, time, traceback

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import pipe_mac_v2 as PM
PIPE = os.environ.get('PIPE_MAC_PIPE') or PM.PIPE
SCR = os.environ.get('MAC_SCRATCH') or os.path.join(HERE, 'scratch')
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
_N = [0]
VMP = '/sessions/vmtest/mnt'
FAKE_QJ = """import os, subprocess, sys
Q = sys.modules[__name__]
CFG = {'ALLOC': [sys.executable, '-c', 'print(777)']}
class Refused(Exception):
    pass
def main(argv):
    open(os.environ['QJ_LOG'], 'a').write(' '.join(argv) + '\\n')
    if os.environ.get('QJ_REFUSE'):
        raise Refused('planted')
    if os.environ.get('QJ_ALREADY'):
        raise Refused("ALREADY GRADED ['V1']: never re-run; a change is a new variant")
    if '--dry' in argv:
        print('DRY RUN OK: planted'); return 0
    r = subprocess.run(CFG['ALLOC'] + ['claim', 'SCOUT', '1'], capture_output=True, text=True)
    n = r.stdout.split()[0]
    jd = os.path.join(os.environ['QJ_RUNDIR'], 'jobs'); os.makedirs(jd, exist_ok=True)
    with open(os.path.join(jd, '%s_judge_SCOUT_GRADE_IDEA.job.sh' % n), 'x') as f:
        f.write('# JOB %s_SCOUT_GRADE_IDEA -- planted kit title\\n# MEM_MB: 1\\nset -u\\necho run\\n' % n)
    print('QUEUED Q_V3 %s %s_judge_SCOUT_GRADE_IDEA.job.sh twin x sha16 y IN z | RUNS r' % (n, n)); return 0
"""


def plant(tag):
    _N[0] += 1
    d = os.path.join(SCR, 'pm_%s_%s_%d' % (STAMP, tag, _N[0])); home = os.path.join(d, 'home')
    fr = os.path.join(home, 'dev', 'F'); rd = os.path.join(fr, 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'SCOUT_20261105')
    os.makedirs(os.path.join(rd, 'ideas', 'IDEA', 'defs')); os.makedirs(os.path.join(rd, 'receipts'))
    open(os.path.join(rd, 'ideas', 'IDEA', 'TRUE_V1_LAB.json'), 'w').write('{}')
    inst = os.path.join(d, 'INSTALL'); tg = os.path.join(inst, '03_Grading/tree/tools/true_gate'); os.makedirs(tg)
    open(os.path.join(tg, 'true_gate_v3.py'), 'w').write("import sys, os\nprint('OK claim', sys.argv[1:], os.getcwd())\nprint('FOR THE CARD x')\n")
    kit = os.path.join(inst, 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools'); os.makedirs(kit)
    open(os.path.join(kit, 'queue_job_v16.py'), 'w').write(FAKE_QJ)
    rq = os.path.join(home, 'dev', 'TP', 'runner')
    for q in ('Q_V3', 'Q_V7'):
        for s in ('IN', 'RUN', 'logs'):
            os.makedirs(os.path.join(rq, q, s))
        open(os.path.join(rq, q, 'runner.heartbeat'), 'w').write('x')
    pf = os.path.join(rd, 'pipe'); os.makedirs(os.path.join(pf, 'filed')); os.makedirs(os.path.join(pf, 'logs'))
    I = dict(task='T-1', seat='SCOUT', run='SCOUT_20261105', idea='IDEA', v='V1', lean='FOLLOW', claim_kind='SIDE', label='LAB',
             **{'def': 'ideas/IDEA/defs/V1.json'}, def_sha16='x', card='c', card_sha16='y', claim='ideas/IDEA/TRUE_V1_LAB.json', window='20250910:20251231',
             block='SEPDEC', words='w', hc={}, mechanism_hypothesis='m', registry_mode='write', open='o')
    json.dump(I, open(os.path.join(pf, 'INPUT.json'), 'w'))
    vm = lambda x: x.replace(home, VMP)
    S = dict(forensics_root=vm(fr), rootq=vm(rq), python='/usr/bin/python3', mac_map=[[VMP + '/dev', '<DEV>']],
             settings_env=VMP + '/SETTINGS_SCOUT.env', scratch_mac='<SCRATCH>', note_v2='n',
             alloc=['/usr/bin/python3', '-B', vm(os.path.join(home, 'dev', 'TP', 'job_alloc.py'))])
    json.dump(S, open(os.path.join(pf, 'SETTINGS.json'), 'w'))
    tpl = os.path.join(d, 'TPL.sh'); open(tpl, 'w').write('# JOB {NAME}\n')
    return dict(d=d, home=home, rd=rd, pf=pf, inst=inst, rq=rq, tpl=tpl)


def done_until(w, n):
    A = PM.load_pipe(PIPE)
    for k, name, kind in A.STEPS:
        if k <= n:
            json.dump(dict(step=k, name=name, numbers={}), open(os.path.join(w['pf'], 'STEP_%02d_%s.json' % (k, name)), 'w'))


class Clock:
    def __init__(self): self.t = 0.0
    def __call__(self): return self.t
    def sleep(self, s): self.t += s


def go(w, argv, hook=None, pick=None):
    A = PM.load_pipe(PIPE)
    os.environ['QJ_LOG'] = os.path.join(w['d'], 'qj.log'); os.environ['QJ_RUNDIR'] = w['rd']
    cfg = dict(install=w['inst'], pins=False, card_tpl=w['tpl'], python=sys.executable, settings_env=os.path.join(w['d'], 'S.env'))
    if pick:
        cfg['pick'] = pick
    c = Clock(); out = io.StringIO()
    def sl(s):
        c.sleep(s)
        if hook: hook(c.t)
    with contextlib.redirect_stdout(out):
        rc = PM.run(['run', w['pf'], '--vm-prefix', VMP, '--mac-home', w['home']] + argv, A=A, cfg=cfg, sleep=sl, clock=c)
    return rc, out.getvalue()


def receipts_grade(w, num):
    r = os.path.join(w['rd'], 'receipts', '%s_GRADE_IDEA' % num); os.makedirs(os.path.join(r, 'HANDOFF', 'REAL_SEALED'))
    open(os.path.join(r, 'HANDOFF', 'SUMMARY.tsv'), 'w').write('a\n1\n')
    open(os.path.join(r, 'HANDOFF', 'REAL_SEALED', 'REAL_V1.tsv'), 'w').write('h\tlead\n15m\t0.3\n')
    open(os.path.join(r, 'PERFIRE_SEAL.tsv'), 'w').write('V1 abcd 10 1 2 3 J\n')
    open(os.path.join(r, 'CARD_V1.txt'), 'w').write('HEADER\nFOLLOW  2c<1c 5m x | 4/4\nFADE  2c<1c 5m y | 3/4\n')


def status(w, q, job, ex):
    open(os.path.join(w['rq'], q, 'logs', job + '.status'), 'w').write('job=%s\nexit=%d\nstarted=1\nended=2\nseconds=1\n' % (job, ex))


def M1():
    M = PM.mac_settings({'a': VMP + '/dev/x', 'b': [VMP + '/v', 'z'], 'note': 'skip', 'c': 1}, VMP, '<HOME>', {'python': 'P'})
    assert M == {'a': '<DEV>/x', 'b': ['<HOME>/v', 'z'], 'c': 1, 'python': 'P'}, M
    try:
        PM.mac_settings({'a': 'x' + VMP}, VMP, '/H', {}); raise AssertionError('no refusal')
    except SystemExit as e:
        assert 'VM_PATH_LEFT' in str(e)


def M2():
    w = plant('M2'); done_until(w, 6)
    rc, o = go(w, ['--until', '7'])
    assert rc == 0 and 'DONE 07 SEAL_TG' in o, o[-600:]
    s = json.load(open(os.path.join(w['pf'], 'STEP_07_SEAL_TG.json')))
    assert s['numbers']['op'] == 'MAC' and s['numbers']['exit'] == '0' and s['numbers']['lines'][0].startswith('OK claim'), s
    assert s['numbers']['lines'][0].split()[-1] in (os.path.realpath(w['rd']), w['rd']), (s['numbers']['lines'][0], w['rd'])   # the tool ran in RUN (its last word is its cwd)
    cmd = open(os.path.join(w['pf'], 'logs', 'S07_relwait.out')).readline().split()
    assert cmd[-1] == os.path.join(w['rd'], 'ideas', cmd[-1].split('/ideas/')[-1]) and os.path.isabs(cmd[-1]), cmd   # path words absolute from RUN
    assert [k for k in s['outputs'] if k.endswith('relwait.out')], s['outputs']      # st_classify finds a rel output by this name
    T = [l.split('\t') for l in open(os.path.join(w['pf'], 'TIMES.tsv')).read().splitlines()]
    assert T[0] == ['utc', 'step', 'rc', 'seconds', 'line'] and T[-1][1] == '07' and float(T[-1][3]) >= 0, T     # per-step seconds recorded
    ms = json.load(open(os.path.join(w['pf'], 'MAC_SETTINGS.json')))
    assert ms['forensics_root'] == os.path.join(w['home'], 'dev', 'F') and ms['mac_map'] == [] and VMP not in json.dumps(ms)


def M3():
    w = plant('M3'); done_until(w, 10)
    def hook(t):
        if t >= 15 and not os.path.exists(os.path.join(w['rq'], 'Q_V3', 'logs', '777_judge_SCOUT_GRADE_IDEA.status')):
            receipts_grade(w, '777'); status(w, 'Q_V3', '777_judge_SCOUT_GRADE_IDEA', 0)
    rc, o = go(w, ['--until', '11'], hook=hook)
    assert rc == 0 and 'DONE 11 GRADE job 777_judge_SCOUT_GRADE_IDEA exit 0' in o, o[-800:]
    assert o.count('WAIT 11') >= 2, o
    q = open(os.path.join(w['d'], 'qj.log')).read().splitlines()
    assert len(q) == 2 and q[0].endswith('--dry') and 'SCOUT_20261105 GRADE IDEA V1' in q[1], q
    A = PM.load_pipe(PIPE); p = A.P(w['pf']); p.rd = w['rd']; p.S['scratch_mac'] = '<SCRATCH>'
    K, _ = A.parse_kit_receipts(p, 11, '777', 'x')
    s = json.load(open(os.path.join(w['pf'], 'STEP_11_GRADE.json')))['numbers']
    for k, v in K.items():
        assert s[k] == v, (k, s[k], v)
    assert s['both_sides_5m_every_month'] is False and s['perfire_sha16'] == 'abcd'


def M4():
    w = plant('M4'); done_until(w, 5)
    r = os.path.join(w['rd'], 'receipts', '555_COUNT_IDEA'); os.makedirs(r)
    open(os.path.join(r, 'COUNT_V1.tsv'), 'w').write('v\tn\nV1\t12\n# months with 3\n')
    status(w, 'Q_V7', '555_judge_SCOUT_COUNT_IDEA', 0)
    json.dump(dict(step=6, name='COUNT', kind='kitq', op='T-1-OP03', job='555_judge_SCOUT_COUNT_IDEA', num='555', queue='Q_V7', filed='x'),
              open(os.path.join(w['pf'], 'PENDING_06.json'), 'w'))
    json.dump(dict(step=6, name='COUNT', code='OPDONE', why='x'), open(os.path.join(w['pf'], 'STOP_06_COUNT.json'), 'w'))
    rc, o = go(w, ['--until', '6'])
    assert rc == 3 and 'STOP 06 COUNT OPDONE' in o, 'without --retry-stop the STOP stands'
    rc, o = go(w, ['--until', '6', '--retry-stop', '6'])
    assert rc == 0 and 'DONE 06 COUNT' in o, o[-500:]
    s = json.load(open(os.path.join(w['pf'], 'STEP_06_COUNT.json')))['numbers']
    assert s['count_rows'] == [{'v': 'V1', 'n': '12'}] and 'the VM bridge' in s['filed_by'] and s['exit'] == '0', s
    assert not os.path.exists(os.path.join(w['d'], 'qj.log')), 'nothing refiled'


def M5():
    w = plant('M5'); done_until(w, 10)
    def hook(t):
        status(w, 'Q_V3', '777_judge_SCOUT_GRADE_IDEA', 3)
    rc, o = go(w, ['--until', '11'], hook=hook)
    assert rc == 3 and 'STOP 11 GRADE JOB_EXIT' in o, o[-500:]
    w = plant('M5b'); done_until(w, 10); os.environ['QJ_REFUSE'] = '1'
    try:
        rc, o = go(w, ['--until', '11'])
    finally:
        del os.environ['QJ_REFUSE']
    assert rc == 3 and 'STOP 11 GRADE DRY_REFUSED' in o, o[-500:]
    assert len(open(os.path.join(w['d'], 'qj.log')).read().splitlines()) == 1, 'only the dry run'


def M6():
    w = plant('M6'); done_until(w, 10)
    rc, o = go(w, ['--until', '11', '--budget-s', '20', '--poll-s', '5'])
    assert rc == 10 and 'BUDGET' in o and os.path.exists(os.path.join(w['pf'], 'PENDING_11.json')), o[-400:]
    receipts_grade(w, '777'); status(w, 'Q_V3', '777_judge_SCOUT_GRADE_IDEA', 0)
    rc, o = go(w, ['--until', '11'])
    assert rc == 0 and 'DONE 11 GRADE' in o and len(open(os.path.join(w['d'], 'qj.log')).read().splitlines()) == 2, 'resumed, not refiled'


def M7():
    w = plant('M7'); rq = w['rq']
    assert PM.live_queue(rq) == 'Q_V3'
    open(os.path.join(rq, 'Q_V3', 'RUN', '9_y.job.sh'), 'w').write('')
    assert PM.live_queue(rq) == 'Q_V7', 'a running job makes the queue busy'
    os.replace(os.path.join(rq, 'Q_V3', 'RUN', '9_y.job.sh'), os.path.join(rq, 'Q_V3', 'logs', '9_y.job.sh'))
    assert PM.live_queue(rq) == 'Q_V3'
    open(os.path.join(rq, 'Q_V3', 'IN', '1_x.job.sh'), 'w').write('')
    assert PM.live_queue(rq) == 'Q_V7'
    open(os.path.join(rq, 'Q_V7', 'runner.stop'), 'w').write('')
    assert PM.live_queue(rq) is None
    os.replace(os.path.join(rq, 'Q_V7', 'runner.stop'), os.path.join(rq, 'Q_V7', 'runner.stop.taken'))
    os.utime(os.path.join(rq, 'Q_V7', 'runner.heartbeat'), (time.time() - 999, time.time() - 999))
    assert PM.live_queue(rq) is None


def M8():
    w = plant('M8'); done_until(w, 6)
    open(os.path.join(w['inst'], '03_Grading/tree/tools/true_gate/true_gate_v3.py'), 'w').write("import sys\nprint('REFUSED planted')\nsys.exit(2)\n")
    rc, o = go(w, ['--until', '7'])
    assert rc == 3 and 'STOP 07 SEAL_TG JOB_EXIT' in o, o[-500:]
    assert 'REFUSED planted' in open(os.path.join(w['pf'], 'logs', 'S07_relwait.out')).read()


def M9():
    w = plant('M9'); done_until(w, 10)
    rc, o = go(w, ['--until', '11', '--budget-s', '6', '--poll-s', '5'])
    tw = open(os.path.join(w['rd'], 'jobs', '777_judge_SCOUT_GRADE_IDEA.job.sh')).read().split('\n')
    assert tw[0] == "# JOB 777_judge_SCOUT_GRADE_IDEA -- the runner's file name (mac_desk_v43 kitq); the kit title is the TITLE line", tw[:5]
    assert tw[1:5] == ['# MEM_MB: 1', '# TITLE: 777_SCOUT_GRADE_IDEA -- planted kit title', '# TASK: T-1', '# OP: MAC'], tw[:6]
    assert tw[5:7] == ['set -u', 'echo run'], tw


def M10():
    w = plant('M10'); A = PM.load_pipe(PIPE)
    json.dump(dict(step=11, name='GRADE', numbers=dict(job_tag='888_GRADE_IDEA')), open(os.path.join(w['pf'], 'STEP_11_GRADE.json'), 'w'))
    for q in ('Q_V3',):
        os.makedirs(os.path.join(w['rq'], q, 'DONE'), exist_ok=True)
    body = '# JOB 888_SCOUT_GRADE_IDEA -- planted title\n# CORES 3\nRD=/x; J=888_GRADE_IDEA\nDV=$RD/receipts/$J\n'
    jf = os.path.join(w['rq'], 'Q_V3', 'DONE', '888_judge_SCOUT_GRADE_IDEA.job.sh'); open(jf, 'w').write(body)
    status(w, 'Q_V3', '888_judge_SCOUT_GRADE_IDEA', 0)
    p = A.P(w['pf']); p.S = dict(p.S, rootq=w['rq'])
    v = PM.grade_view(p, A)
    assert v == p.p('grade_view'), v
    vt = open(os.path.join(v, 'Q_V3', 'DONE', '888_judge_SCOUT_GRADE_IDEA.job.sh')).read()
    import pipe_kitq_v1 as K
    assert vt == K.kit_text(body, '888_judge_SCOUT_GRADE_IDEA', '888', 'SCOUT', 'GRADE', 'IDEA', 'T-1', 'MAC') and '\n# TITLE: 888_SCOUT_GRADE_IDEA -- planted title' in vt
    assert open(jf).read() == body, 'the runner file untouched'
    assert os.path.isfile(os.path.join(v, 'Q_V3', 'logs', '888_judge_SCOUT_GRADE_IDEA.status'))
    w2 = plant('M10b')
    json.dump(dict(step=11, name='GRADE', numbers=dict(job_tag='889_GRADE_IDEA')), open(os.path.join(w2['pf'], 'STEP_11_GRADE.json'), 'w'))
    os.makedirs(os.path.join(w2['rq'], 'Q_V3', 'DONE'), exist_ok=True)
    open(os.path.join(w2['rq'], 'Q_V3', 'DONE', '889_judge_SCOUT_GRADE_IDEA.job.sh'), 'w').write("# JOB 889_judge -- x\n# TITLE: 889_SCOUT_GRADE_IDEA -- t\nset -u\n")
    p2 = A.P(w2['pf']); p2.S = dict(p2.S, rootq=w2['rq'])
    assert PM.grade_view(p2, A) is None


def M11():
    w = plant('M11'); done_until(w, 10)
    json.dump(dict(step=11, name='GRADE', kind='kitq', op='MAC', mode='pipe_mac_v1', job='700_judge_SCOUT_GRADE_IDEA', num='700', queue='Q_V3', filed='x'),
              open(os.path.join(w['pf'], 'PENDING_11.json'), 'w'))
    status(w, 'Q_V3', '700_judge_SCOUT_GRADE_IDEA', 0)
    rc, o = go(w, ['--until', '11', '--refile-failed', '11'])
    assert rc == 2 and 'REFUSED REFILE' in o and os.path.exists(os.path.join(w['pf'], 'PENDING_11.json')), o[-300:]
    status(w, 'Q_V3', '700_judge_SCOUT_GRADE_IDEA', 6)
    json.dump(dict(step=11, name='GRADE', code='JOB_EXIT', why='x'), open(os.path.join(w['pf'], 'STOP_11_GRADE.json'), 'w'))
    rc, o = go(w, ['--until', '11', '--refile-failed', '11', '--retry-stop', '11', '--budget-s', '6', '--poll-s', '5'])
    assert 'REFILE: job 700_judge_SCOUT_GRADE_IDEA ended exit 6' in o and json.load(open(os.path.join(w['pf'], 'PENDING_11.json')))['num'] == '777', o[-400:]


def M12():
    assert PM.CARD_TPL.endswith('ALARM_UNDERSTAND_V1_2/tree/team/RESEARCH/PLAYGROUND/tools/PG20261105_alarm_understand/code/CARD_JOB_TEMPLATE_V3.sh'), PM.CARD_TPL
    here = lambda x: x if os.path.isdir('<HOME>') else x.replace('<HOME>', os.path.expanduser('~/mnt'), 1)
    assert PM.sha16(here(PM.CARD_TPL)) == PM.CARD_TPL_PIN
    code = os.path.dirname(here(PM.CARD_TPL))
    ed = os.path.join(code, '..', '..', 'PG20261106_alarm_match_lawpath', 'edition', '07_Price_path')   # mech_cards_run_v2's default
    assert os.path.isfile(os.path.join(ed, 'tree', 'tools', 'alarm_match', 'draw_v3.py')), ed
    assert PM.PIPE.endswith('/alarm_pipeline_v1_3.py') and PM.sha16(PM.PIPE) == PM.PIPE_PIN, PM.PIPE


def M13():
    w = plant('M13'); I = json.load(open(os.path.join(w['pf'], 'INPUT.json')))
    I.update(registry_mode='replay', replay_jobs={'GRADE': '700'}); json.dump(I, open(os.path.join(w['pf'], 'INPUT.json'), 'w'))
    done_until(w, 10); status(w, 'Q_V7', '700_judge_SCOUT_GRADE_IDEA', 0); os.environ['QJ_ALREADY'] = '1'
    try:
        rc, o = go(w, ['--until', '11'])
    finally:
        del os.environ['QJ_ALREADY']
    pend = [x for x in os.listdir(w['pf']) if x.startswith('PENDING_11')] + [x for x in os.listdir(w['pf']) if x.startswith('STEP_11')]
    assert 'DRY_REFUSED' not in o and pend, o[-600:]
    assert len(open(os.path.join(w['d'], 'qj.log')).read().splitlines()) == 1, 'replay: only the dry run, never a filing'
    # write mode: the same refusal stops (the pipeline's rule: only a replay adopts)
    w2 = plant('M13w'); done_until(w2, 10); os.environ['QJ_ALREADY'] = '1'
    try:
        rc, o = go(w2, ['--until', '11'])
    finally:
        del os.environ['QJ_ALREADY']
    assert rc == 3 and 'STOP 11 GRADE DRY_REFUSED' in o, o[-400:]



def M14():
    """v1_3 replay_old: the input names no earlier job of the kind; the run's one receipts folder <num>_<KIND>_<IDEA> is adopted"""
    w = plant('M14'); I = json.load(open(os.path.join(w['pf'], 'INPUT.json')))
    I.update(registry_mode='replay'); I.pop('replay_jobs', None); json.dump(I, open(os.path.join(w['pf'], 'INPUT.json'), 'w'))
    os.makedirs(os.path.join(w['rd'], 'receipts', '700_GRADE_IDEA'))
    done_until(w, 10); status(w, 'Q_V7', '700_judge_SCOUT_GRADE_IDEA', 0); os.environ['QJ_ALREADY'] = '1'
    try:
        rc, o = go(w, ['--until', '11'])
    finally:
        del os.environ['QJ_ALREADY']
    pend = [x for x in os.listdir(w['pf']) if x.startswith('PENDING_11')] + [x for x in os.listdir(w['pf']) if x.startswith('STEP_11')]
    assert 'DRY_REFUSED' not in o and pend, o[-600:]
    assert len(open(os.path.join(w['d'], 'qj.log')).read().splitlines()) == 1, 'replay: only the dry run, never a filing'


TESTS = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9', 'M10', 'M11', 'M12', 'M13', 'M14']
if __name__ == '__main__':
    os.makedirs(SCR, exist_ok=True)
    want = sys.argv[1:] or TESTS; bad = 0
    for n in want:
        try:
            globals()[n](); print('PASS', n)
        except (Exception, SystemExit):
            bad += 1; print('FAIL', n); traceback.print_exc(limit=5)
    print('RESULT %d of %d passed (pipe_mac_v2)' % (len(want) - bad, len(want)))
    sys.exit(1 if bad else 0)
