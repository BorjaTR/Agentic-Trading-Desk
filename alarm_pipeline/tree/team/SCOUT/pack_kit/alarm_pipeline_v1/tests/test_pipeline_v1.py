#!/usr/bin/env python3
"""test_pipeline_v1.py (SCO-A153): the alarm_pipeline_v1 tests on a planted world with a FAKE runner and FAKE bridge (tests/fake/).
Real tools inside the tests: ops_jobs_v1, classify_line_v2, card_v1, mechanism_v1, alarm_cards_v1.side_hits (read-only import), the real
MECHANISM_MAP_V1.md (copied). Never real data, never the real runner. Scratch: tests/scratch/<test>_<pid>/ (kept, never deleted).
  python3 -B test_pipeline_v1.py [name ...]        env PIPE_UNDER_TEST=<file> runs them on another file (the red run on a stub)
Prints one line per test and 'RESULT <passed> of <n>'; rc 0 when all pass."""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, os, shutil, subprocess, time, traceback

T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
FR_REAL = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
MAP = os.path.join(FR_REAL, 'team', 'RESEARCH', 'LEAD', 'MECHANISM_20261106', 'MECHANISM_MAP_V1.md')
OPS = os.path.join(FR_REAL, 'team', 'SCOUT', 'pack_kit', 'ops_jobs_v1', 'ops_jobs_v1.py')
CLS = os.path.join(FR_REAL, 'team', 'SCOUT', 'pack_kit', 'classify_line_v2', 'classify_line_v2.py')
FK = os.path.join(T, 'fake')
SUT = os.environ.get('PIPE_UNDER_TEST', os.path.join(HERE, 'alarm_pipeline_v1.py'))


def load():
    spec = importlib.util.spec_from_file_location('pipe_under_test', SUT)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def w(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w').write(t)


DECIDE_STOP = ('DECISION IDEA V1: STOP | R1 no R2 no | LEAD 15m +3.15 (t +1.70) 1h +6.14 (t +2.90) | waves 720, months counted 4 passing 2 '
               '| CLEAR - - | price gate - | R1 missed: passing 2 of 4 counted (need 3)')
DECIDE_PASS = DECIDE_STOP.replace(': STOP | R1 no R2 no', ': PASS | R1 yes R2 yes')


def world(name, fake=None, inp=None, sett=None, mech_hold=38):
    W = os.path.join(T, 'scratch', '%s_%d_%d' % (name, os.getpid(), int(time.time() * 1000) % 100000))
    fr = os.path.join(W, 'fr'); rd = os.path.join(fr, 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'RUNX')
    w(os.path.join(rd, 'ideas', 'IDEA', 'defs', 'V1.json'), '{"def": 1}\n')
    w(os.path.join(rd, 'ideas', 'IDEA', 'CARD_IDEA.md'), 'sealed card\n')
    w(os.path.join(rd, 'ideas', 'IDEA', 'TRUE_V1_LAB.json'), '{"perfire_sha16": "%s"}\n' % ('9999999999999999' if name == 't17' else 'abcdefabcdefabcd'))
    ds, cs = sha16(os.path.join(rd, 'ideas', 'IDEA', 'defs', 'V1.json')), sha16(os.path.join(rd, 'ideas', 'IDEA', 'CARD_IDEA.md'))
    vrow = 'now\tIDEA\tV1\tFADE\tideas/IDEA/defs/V1.json\t%s\tideas/IDEA/CARD_IDEA.md\t%s' % (ds, cs)
    w(os.path.join(rd, 'registers', 'VARIANTS.tsv'), 'utc\tidea\tV\tlean\tdef\tdef_sha16\tcard\tprereg_sha16\n' + vrow + '\n')
    os.makedirs(os.path.join(rd, 'receipts'))
    for q in ('Q_V1', 'Q_V16', 'Q_V19'):
        for d in ('IN', 'RUN', 'DONE', 'logs'):
            os.makedirs(os.path.join(W, 'rootq', q, d))
        w(os.path.join(W, 'rootq', q, 'runner.heartbeat'), 'hb\n')
    w(os.path.join(W, 'TRIES.tsv'), 'id\tstatus\tidea\nPREREG_IDEA_20261106T000000Z\tPREREG\tIDEA\nPREREG_IDEA_20261106T000000Z_R\tFAIL\tIDEA\n')
    w(os.path.join(W, 'TRIED.tsv'), 'id\tutc\tverdict\twhat_tried\tactual\nRUNX_IDEA\tnow\tFAILED\tx\ty\n')
    fx = os.path.join(W, 'fix')
    w(os.path.join(fx, 'COUNT', 'COUNT_V1.tsv'), '# COUNT V1 planted\nmonth\tfires\twaves\tcoins\tmax_fires_in_a_wave\tfires_on_BTC\n2509\t10\t5\t3\t4\t1\n'
      '2510\t30\t6\t3\t9\t0\nALL\t40\t11\t3\t9\t1\n# months with 30 or more waves: 0 of 2; rows outside the window: 0\n')
    w(os.path.join(fx, 'GRADE', 'HANDOFF', 'SUMMARY.tsv'), '# planted\nV\tlean\tstatus\nV1\tFADE\tOK\n')
    w(os.path.join(fx, 'GRADE', 'HANDOFF', 'REAL_SEALED', 'REAL_V1.tsv'), '# planted\nhorizon\twaves\tlead\tt\n15m\t720\t3.1517\t1.6965\n1h\t720\t6.1381\t2.8955\n')
    w(os.path.join(fx, 'GRADE', 'PERFIRE_SEAL.tsv'), 'V1\tabcdefabcdefabcd\t40\t100\t1\t2\t3\tX\n')
    w(os.path.join(fx, 'GRADE', 'CARD_V1.txt'), 'CARD V1 | planted | 40 fires, 11 waves\nFADE   2c<1c 5m    14 / 13  +1.6 | 2509  +3.4 2510  +5.3 | 2/2\n'
      'FOLLOW 2c<1c 5m    15 / 13  +2.3 | 2509  +4.9 2510  -0.5 | 1/2\n')
    w(os.path.join(fx, 'TRUE', 'TRUE_V1_LAB', 'TRUE_ROW.tsv'), 'id\tverdict\tfires\twaves\tidea\tV\nIDEA_V1_LAB\tNOT SUPPORTED\t40\t11\tIDEA\tV1\n')
    w(os.path.join(fx, 'TRUE', 'TRUE_V1_LAB', 'TRUE_CARD.txt'), 'VERDICT NOT SUPPORTED: gap +0.028 on 11 waves\n')
    w(os.path.join(fx, 'FIRSTLOOK', 'FIRST_LOOK.md'), '# First look of IDEA_V1: RULE_9 = SIDE\n')
    fires = ['alarm_id\tcoin\tt\tside'] + ['IDEA_V1\tC%d\t%d\t-1' % (i % 3, 1757600000 + 3600 * i) for i in range(40)]
    w(os.path.join(fx, 'CARD', 'FIRES.tsv'), '# planted bundle\n' + '\n'.join(fires) + '\n')
    R = ['who\tcoin\tt\tcode\tvalue\tknown_at']
    for i in range(40):
        t = 1757600000 + 3600 * i; c = 'C%d' % (i % 3); hold = i < mech_hold
        R.append('FIRE\t%s\t%d\tCTX.forced_log_usd_15m\t%s\t%d' % (c, t, '7.0' if hold else '1.0', t))
        R.append('FIRE\t%s\t%d\tCTX.oi_chg_10m\t%s\t%d' % (c, t, '-0.3' if hold else '0.2', t))
    for c in ('C0', 'C1', 'C2'):
        for j in range(25):
            R.append('MATCH\t%s\t%d\tCTX.forced_log_usd_15m\t%.2f\t%d' % (c, 1757000000 + j, 3.0 + j * 0.05, 1757000000 + j))
    w(os.path.join(fx, 'CARD', 'RD', 'READINGS.tsv'), '\n'.join(R) + '\n')
    qs = ['alarm\tq\tanswer\tnumber\tsource\tsha16\tstrength']
    for q in ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'GRADE'):
        qs.append('@ALARM@\t%s\tplanted answer %s about the event\t1\tREADINGS.tsv\t0000000000000000\t%s' % (q, q, 'UNKNOWN' if q == 'Q6' else 'WEAK'))
    w(os.path.join(fx, 'CARD', 'CARDS.tsv'), '\n'.join(qs) + '\n')
    w(os.path.join(fx, 'CARD', 'CARDS.md'), '# ALARM_CARDS_@ALARM@\n\n## Part A: cards\n\n### @ALARM@ (definition V1.json x): 40 fires, 11 events\n\n| Q |\n\n'
      '- after the fire (description): planted retained line\n\n## Part B: conclusions (4 lines, knowledge only)\n\n1. planted one\n2. planted two\n')
    mp = os.path.join(W, 'MAP.md'); shutil.copyfile(MAP, mp)
    py = sys.executable
    S = dict(forensics_root=fr, python=py, rootq=os.path.join(W, 'rootq'), bridge=os.path.join(FK, 'fake_bridge.py'),
             close_lib=os.path.join(W, 'close_lib'), settings_env=os.path.join(W, 'SETTINGS.env'), tried_search=os.path.join(FK, 'tried_search_v1.py'),
             ops_jobs=OPS, classify=CLS, claim_fill=os.path.join(FK, 'claim_fill_v1.py'), add_row=os.path.join(FK, 'add_row.py'),
             menu_gate=os.path.join(FK, 'menu_gate_v1.py'), reg_append=os.path.join(FK, 'reg_append_v1.py'), decide=os.path.join(FK, 'decide_v6.py'),
             card_v1=os.path.join(os.path.dirname(SUT), 'card_v1.py'), alloc=[py, '-B', os.path.join(FK, 'job_alloc.py')], card_queue='Q_V19', mac_map=[],
             mac_python=py, au_code=FK, mechanism_map=mp, mechanism_map_sha16=sha16(mp), cards_root=os.path.join(W, 'cards'),
             tries_ledger=os.path.join(W, 'TRIES.tsv'), tried_file=os.path.join(W, 'TRIED.tsv'), scratch_mac='<DISK>')
    S.update(sett or {})
    I = dict(task='SCO-A999', seat='SCOUT', run='RUNX', idea='IDEA', v='V1', lean='FADE', claim_kind='SIDE', **{'def': 'ideas/IDEA/defs/V1.json'},
             def_sha16=ds, card='ideas/IDEA/CARD_IDEA.md', card_sha16=cs, claim='ideas/IDEA/TRUE_V1_LAB.json', label='LAB',
             window='20250910:20251231', block='SEPDEC', words='large fill', hc=dict(first='20251001', last='20251031', coins='BTC,ETH', n=2, inputs='a,b'),
             mechanism_hypothesis='FORCED_OUT', registry_mode='replay', open='why the late months fail', replay_prereg_id='PREREG_IDEA_20261106T000000Z')
    I.update(inp or {})
    F = dict(rel_out={'hc_defs_v4': 'HC planted 12 fires\n', 'novelty_v5': 'nearest 1: X (OWN): same fires 1.0 pct\nVERDICT NEW: every overlap under 40 pct\n',
                      'true_gate_check': 'OK trigger reads A; label B\n', 'ledger_add_v7_prereg': 'PREREG_IDEA_20261106T010203Z tries for IDEA: 2\n',
                      'ledger_add_v7_result': 'PREREG_IDEA_20261106T010203Z_R\n'},
             decide=DECIDE_STOP, variants_row=vrow)
    F.update(fake or {})
    json.dump(F, open(os.path.join(W, 'FAKE.json'), 'w'))
    json.dump(S, open(os.path.join(W, 'S.json'), 'w')); json.dump(I, open(os.path.join(W, 'I.json'), 'w'))
    os.environ['FAKE_WORLD'] = W
    os.environ['CARD_V1_ALARM_CARDS'] = os.path.join(FR_REAL, 'team', 'RESEARCH', 'PLAYGROUND', 'tools', 'PG20261105_alarm_understand', 'code', 'alarm_cards_v1.py')
    m = load()
    run = os.path.join(W, 'run')
    with open(os.devnull, 'w') as dn:
        so = sys.stdout; sys.stdout = dn
        try:
            m.init(run, os.path.join(W, 'I.json'), os.path.join(W, 'S.json'))
        finally:
            sys.stdout = so
    return W, run, m


def runner(W, hold=False):
    """the FAKE runner: runs every IN job with bash, writes logs/<name>.status (exit=, started=, ended=) and moves it to DONE"""
    if hold:
        return
    for q in sorted(os.listdir(os.path.join(W, 'rootq'))):
        IN = os.path.join(W, 'rootq', q, 'IN')
        for f in sorted(os.listdir(IN)):
            if not f.endswith('.job.sh'):
                continue
            name = f[:-7]; t0 = int(time.time())
            with open(os.path.join(W, 'rootq', q, 'logs', name + '.log'), 'w') as lg:
                rc = subprocess.run(['bash', os.path.join(IN, f)], stdout=lg, stderr=subprocess.STDOUT).returncode
            w(os.path.join(W, 'rootq', q, 'logs', name + '.status'), 'job=%s\nexit=%d\nstarted=%d\nended=%d\nseconds=0\nkilled=\n' % (name, rc, t0, int(time.time())))
            os.replace(os.path.join(IN, f), os.path.join(W, 'rootq', q, 'DONE', f))
        os.utime(os.path.join(W, 'rootq', q, 'runner.heartbeat'))


def drive(W, run, m, n=90, hold_at=None, cut_at=None):
    lines = []
    for i in range(n):
        p = m.P(run)
        if cut_at is not None and not os.path.exists(os.path.join(run, 'STEP_%02d_%s.json' % (cut_at, dict((a, b) for a, b, c in m.STEPS)[cut_at]))) \
                and not os.path.exists(os.path.join(run, 'PENDING_%02d.json' % cut_at)) and _first_missing(m, p) == cut_at:
            real = m.adopt
            def cut(*a, **k):
                raise KeyboardInterrupt('planted cut after filing')
            m.adopt = cut
            try:
                m.one_move(p)
            except KeyboardInterrupt:
                lines.append('CUT %02d' % cut_at)
            m.adopt = real; cut_at = None
            continue
        rc, line = m.one_move(p); lines.append(line)
        if rc == 3 or line == 'DONE ALL':
            return rc, line, lines
        if rc == 10:
            if hold_at is not None and line.startswith('WAIT %02d' % hold_at):
                return rc, line, lines
            runner(W)
    return 9, 'NO END', lines


def _first_missing(m, p):
    for a, b, c in m.STEPS:
        if not p.done(a):
            return a


def J(run, n, name):
    return json.load(open(os.path.join(run, 'STEP_%02d_%s.json' % (n, name))))


# ------------------------------------------------------------------ tests
def t01_happy_replay():
    W, run, m = world('t01')
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', (line, L[-3:])
    assert len([x for x in os.listdir(run) if x.startswith('STEP_')]) == 22
    assert J(run, 15, 'FIRSTLOOK')['numbers']['ran'] == 'no'
    assert J(run, 18, 'MECHANISM')['numbers']['mechanism'] == 'FORCED_OUT'
    assert abs(J(run, 18, 'MECHANISM')['numbers']['share'] - 0.95) < 1e-9
    h = J(run, 22, 'HANDOFF')['numbers']
    idx = open(os.path.join(W, 'cards', 'INDEX.tsv')).read().splitlines()
    assert len(idx) == 2 and idx[1].startswith('IDEA_V1\tFORCED_OUT\t' + h['card_sha16']), idx
    assert os.path.exists(os.path.join(W, 'cards', 'FORCED_OUT', 'IDEA_V1', 'HANDOFF.json'))
    assert J(run, 11, 'GRADE')['numbers']['exit'] == '0' and J(run, 11, 'GRADE')['numbers']['perfire_sha16'] == 'abcdefabcdefabcd'
    assert 'race STOP' in open(h['card']).read()
    assert J(run, 10, 'SEAL_PREREG')['numbers']['mode'] == 'replay'


def t02_write_mode():
    W, run, m = world('t02', inp=dict(registry_mode='write', variants_fields='ideas/IDEA/V.json'))
    rows0 = open(os.path.join(W, 'TRIED.tsv')).read()
    w(os.path.join(W, 'TRIED.tsv'), rows0.splitlines()[0] + '\n')
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', (line, L[-3:])
    assert J(run, 10, 'SEAL_PREREG')['numbers']['prereg_id'] == 'PREREG_IDEA_20261106T010203Z'
    assert J(run, 21, 'LOG_LEDGER')['numbers']['result_id'] == 'PREREG_IDEA_20261106T010203Z_R'
    assert 'RUNX_IDEA' in open(os.path.join(W, 'TRIED.tsv')).read()
    assert 'EXISTS' in J(run, 9, 'SEAL_VARIANTS')['numbers'].get('note', '')


def t03_job_exit_nonzero():
    W, run, m = world('t03', fake=dict(exit={'GRADE': 1}))
    rc, line, L = drive(W, run, m)
    assert rc == 3 and line.startswith('STOP 11 GRADE JOB_EXIT'), line


def t04_missing_output():
    W, run, m = world('t04', fake=dict(omit={'COUNT': 'COUNT_V1.tsv'}))
    rc, line, L = drive(W, run, m)
    assert rc == 3 and line.startswith('STOP 06 COUNT NO_OUTPUT'), line


def t05_refused_then_retry():
    W, run, m = world('t05', fake=dict(dry_refuse=['COUNT']))
    rc, line, L = drive(W, run, m)
    assert rc == 3 and line.startswith('STOP 06 COUNT DRY_REFUSED'), line
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 06'), 'a STOP holds until retry'
    F = json.load(open(os.path.join(W, 'FAKE.json'))); F['dry_refuse'] = []; json.dump(F, open(os.path.join(W, 'FAKE.json'), 'w'))
    with open(os.devnull, 'w') as dn:
        so = sys.stdout; sys.stdout = dn
        try:
            m.main(['retry', run])
        finally:
            sys.stdout = so
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', line
    assert [x for x in os.listdir(os.path.join(run, 'filed')) if x.startswith('STOP_06')], 'the STOP is kept aside'


def t06_resume_after_cut():
    W, run, m = world('t06')
    rc, line, L = drive(W, run, m, cut_at=11)
    assert line == 'DONE ALL', (line, L)
    assert 'CUT 11' in L and any('adopted after a cut' in x for x in L), L
    led = open(os.path.join(run, 'ops', 'TYPED_OPS_SCO-A999.tsv')).read()
    assert led.count('SCO-A999-OP') == led.count('\tINTENT\t') * 2, 'every INTENT has its DONE row'
    assert J(run, 11, 'GRADE')['numbers']['exit'] == '0'


def t07_firstlook_rule():
    W, run, m = world('t07', fake=dict(decide=DECIDE_PASS))
    w(os.path.join(W, 'TRIED.tsv'), 'id\tutc\tverdict\twhat_tried\tactual\nRUNX_IDEA\tnow\tWORKED\tx\ty\n')
    w(os.path.join(W, 'TRIES.tsv'), 'id\tstatus\tidea\nPREREG_IDEA_20261106T000000Z\tPREREG\tIDEA\nPREREG_IDEA_20261106T000000Z_R\tPASS\tIDEA\n')
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', line
    assert J(run, 15, 'FIRSTLOOK')['numbers']['ran'] == 'yes' and 'RULE_9 = SIDE' in J(run, 15, 'FIRSTLOOK')['numbers']['rule9']


def t08_window_closed():
    W, run, m = world('t08', inp=dict(window='20250910:20260430'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT WINDOW_CLOSED'), line


def t09_def_changed():
    W, run, m = world('t09', inp=dict(def_sha16='1111111111111111'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT DEF_CHANGED'), line


def t10_mechanism_none():
    W, run, m = world('t10', mech_hold=20)
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', line
    M = J(run, 18, 'MECHANISM')['numbers']
    assert M['mechanism'] == 'NONE' and abs(M['share'] - 0.5) < 1e-9 and M['hypothesis_held'] == 'no', M
    assert os.path.exists(os.path.join(W, 'cards', 'NONE', 'IDEA_V1', 'ALARM_CARD_IDEA_V1.md'))


def t11_wait_not_ended():
    W, run, m = world('t11')
    rc, line, L = drive(W, run, m, hold_at=6)
    assert rc == 10 and 'filed job' in line, line
    rc, line = m.one_move(m.P(run))
    assert rc == 10 and 'not ended' in line, line


def t12_opdone_refused():
    W, run, m = world('t12', fake=dict(opdone_fail=['ALL']))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 04 HC_FIRES OPDONE'), line


def t13_tried_differs():
    W, run, m = world('t13', fake=dict(decide=DECIDE_PASS))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 20 LOG_TRIED TRIED_DIFFERS'), line


def t14_side_word_refused():
    W, run, m = world('t14')
    t = open(os.path.join(W, 'fix', 'CARD', 'CARDS.md')).read().replace('planted two', 'buy the dip')
    w(os.path.join(W, 'fix', 'CARD', 'CARDS.md'), t)
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 22 HANDOFF TOOL_RC'), line
    assert 'REFUSED SIDE_WORD' in open(os.path.join(run, 'logs', 'S22_card.out')).read()
    assert not os.path.exists(os.path.join(W, 'cards', 'INDEX.tsv'))


def t15_map_changed():
    W, run, m = world('t15')
    with open(os.path.join(W, 'MAP.md'), 'a') as f:
        f.write('edited\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 17 CARD JOB_EXIT'), line
    assert 'REFUSED MAP_CHANGED' in open(os.path.join(run, [d for d in os.listdir(run) if d.startswith('card_job_')][0], 'MECHANISM.txt')).read()


def t16_handoff_twice_exists():
    W, run, m = world('t16')
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL'
    a = m.P(run); s = J(run, 22, 'HANDOFF')
    r = subprocess.run([sys.executable, '-B', os.path.join(os.path.dirname(SUT), 'card_v1.py'), '--alarm', 'IDEA_V1', '--cards-tsv', J(run, 17, 'CARD')['numbers']['card_tsv'],
                        '--cards-md', J(run, 17, 'CARD')['numbers']['card_md'], '--mechanism-json', J(run, 17, 'CARD')['numbers']['mechanism_json'],
                        '--meta', os.path.join(run, 'HANDOFF_META.json'), '--root', os.path.join(W, 'cards'), '--out', os.path.join(run, 'ALARM_CARD')],
                       stdout=subprocess.PIPE, universal_newlines=True)
    assert r.returncode == 0 and r.stdout.strip().endswith('EXISTS'), r.stdout
    assert len(open(os.path.join(W, 'cards', 'INDEX.tsv')).read().splitlines()) == 2


def t17_perfire_differs():
    W, run, m = world('t17', fake=dict(fill_sha='9999999999999999'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 12 TRUE_FILL PERFIRE_DIFFERS'), line


def t18_replay_needs_prereg_row():
    W, run, m = world('t18', inp=dict(replay_prereg_id='PREREG_IDEA_20990101T000000Z'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 10 SEAL_PREREG NO_PREREG_ROW'), line


def t19_bad_decision():
    W, run, m = world('t19', fake=dict(decide='DECISION IDEA V1: MAYBE | nothing'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 14 DECIDE BAD_DECISION'), line


def t20_novelty_two_verdicts():
    W, run, m = world('t20')
    F = json.load(open(os.path.join(W, 'FAKE.json'))); F['rel_out']['novelty_v5'] += 'VERDICT NEAR X: planted\n'
    json.dump(F, open(os.path.join(W, 'FAKE.json'), 'w'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 05 NOVELTY_HC NO_VERDICT'), line


def t21_menu_refused():
    W, run, m = world('t21', fake=dict(menu='MENU GATE V1.json: REFUSED code C1.S99 not PROVEN'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 08 SEAL_MENU MENU_REFUSED'), line


def t22_tg_refused():
    W, run, m = world('t22')
    F = json.load(open(os.path.join(W, 'FAKE.json'))); F['rel_out']['true_gate_check'] = 'REFUSED label not admitted\n'
    json.dump(F, open(os.path.join(W, 'FAKE.json'), 'w'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 07 SEAL_TG TG_REFUSED'), line


def t23_bad_input():
    W, run, m = world('t23', inp=dict(registry_mode='maybe'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT BAD_INPUT'), line


def t24_card_changed():
    W, run, m = world('t24', inp=dict(card_sha16='2222222222222222'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT CARD_CHANGED'), line


def t25_rel_refused():
    W, run, m = world('t25', fake=dict(rel_refuse=['hc_defs_v4']))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 04 HC_FIRES FILE_REFUSED'), line


def t26_tool_rc():
    W, run, m = world('t26', fake=dict(rc={'tried_search_v1': 3}))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 02 COPY_SEARCH TOOL_RC'), line


def t27_result_differs():
    W, run, m = world('t27')
    w(os.path.join(W, 'TRIES.tsv'), 'id\tstatus\tidea\nPREREG_IDEA_20261106T000000Z\tPREREG\tIDEA\nPREREG_IDEA_20261106T000000Z_R\tPASS\tIDEA\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 21 LOG_LEDGER RESULT_DIFFERS'), line


def t28_write_tried_exists():
    W, run, m = world('t28', inp=dict(registry_mode='write'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 20 LOG_TRIED TRIED_EXISTS'), line


def t29_no_variants_row():
    W, run, m = world('t29')
    w(os.path.join(W, 'fr', 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'RUNX', 'registers', 'VARIANTS.tsv'), 'utc\tidea\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 09 SEAL_VARIANTS NO_VARIANTS_ROW'), line


def t30_write_needs_fields():
    W, run, m = world('t30', inp=dict(registry_mode='write'))
    w(os.path.join(W, 'fr', 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'RUNX', 'registers', 'VARIANTS.tsv'), 'utc\tidea\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 09 SEAL_VARIANTS NO_FIELDS'), line


def t31_no_tried_row():
    W, run, m = world('t31')
    w(os.path.join(W, 'TRIED.tsv'), 'id\tutc\tverdict\twhat_tried\tactual\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 20 LOG_TRIED NO_TRIED_ROW'), line


def t32_no_result_row():
    W, run, m = world('t32')
    w(os.path.join(W, 'TRIES.tsv'), 'id\tstatus\tidea\nPREREG_IDEA_20261106T000000Z\tPREREG\tIDEA\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 21 LOG_LEDGER NO_RESULT_ROW'), line


def t33_no_decision():
    W, run, m = world('t33', fake=dict(decide='REFUSED: NO_GRADE planted'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 14 DECIDE NO_DECISION'), line


def t34_no_file():
    W, run, m = world('t34', inp=dict(claim='ideas/IDEA/TRUE_V1_MISSING.json'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT NO_FILE'), line


def t35_bad_window():
    W, run, m = world('t35', inp=dict(window='20251231:20250910'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 01 INPUT BAD_WINDOW'), line


def t36_cut_before_file():
    W, run, m = world('t36')
    json.dump(dict(step=2, op='SCO-A999-OP01'), open(os.path.join(run, 'FILING_04.json'), 'w'))
    for n, name in ((1, 'INPUT'), (2, 'COPY_SEARCH'), (3, 'COPY_SEARCH_DEF')):
        rc, line = m.one_move(m.P(run))
    rc, line = m.one_move(m.P(run))
    assert line.startswith('STOP 04 HC_FIRES CUT_BEFORE_FILE'), line


def t37_card_no_rows():
    W, run, m = world('t37')
    w(os.path.join(W, 'fix', 'CARD', 'CARDS.tsv'), 'alarm\tq\tanswer\tnumber\tsource\tsha16\tstrength\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 22 HANDOFF TOOL_RC'), line
    assert 'REFUSED NO_ROWS' in open(os.path.join(run, 'logs', 'S22_card.out')).read()


def t38_pipeline_map_changed():
    W, run, m = world('t38', sett=dict(mechanism_map_sha16='3333333333333333'))
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 18 MECHANISM MAP_CHANGED'), line


def t39_relq_busy_waits():
    W, run, m = world('t39')
    w(os.path.join(W, 'rootq', 'Q_V16', 'IN', '1_judge_RBSCOUT_OTHER.job.sh'), 'exit 0\n')
    for i in range(3):
        rc, line = m.one_move(m.P(run))
    rc, line = m.one_move(m.P(run))
    assert rc == 10 and line.startswith('WAIT 04 HC_FIRES no free rel queue'), line


def t40_replay_adopts_already_graded():
    W, run, m = world('t40', fake=dict(dry_already=['GRADE']), inp=dict(replay_jobs={'GRADE': '29999999'}))
    rd = os.path.join(W, 'fr', 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'RUNX', 'receipts', '29999999_GRADE_IDEA')
    shutil.copytree(os.path.join(W, 'fix', 'GRADE'), rd)
    w(os.path.join(W, 'rootq', 'Q_V1', 'logs', '29999999_judge_SCOUT_GRADE_IDEA.status'), 'job=29999999_judge_SCOUT_GRADE_IDEA\nexit=0\nstarted=1\nended=2\n')
    rc, line, L = drive(W, run, m)
    assert line == 'DONE ALL', (line, L[-3:])
    g = J(run, 11, 'GRADE')['numbers']
    assert g['adopted'] == 'yes' and g['job'] == '29999999_judge_SCOUT_GRADE_IDEA' and 'ALREADY GRADED' in g['refusal'], g
    assert 'opdone' not in g


def t41_write_mode_never_adopts():
    W, run, m = world('t41', fake=dict(dry_already=['GRADE']), inp=dict(registry_mode='write', replay_jobs={'GRADE': '29999999'}))
    w(os.path.join(W, 'TRIED.tsv'), 'id\tutc\tverdict\twhat_tried\tactual\n')
    rc, line, L = drive(W, run, m)
    assert line.startswith('STOP 11 GRADE DRY_REFUSED'), line


TESTS = [v for k, v in sorted(globals().items()) if k.startswith('t') and k[1:3].isdigit()]


def main(names):
    ok = 0; sel = [t for t in TESTS if not names or t.__name__ in names or t.__name__[:3] in names]
    for t in sel:
        t0 = time.time()
        try:
            t(); ok += 1; print('PASS %s %.1f s' % (t.__name__, time.time() - t0))
        except Exception as e:
            print('FAIL %s: %s' % (t.__name__, (repr(e) or traceback.format_exc())[:400]))
        sys.stdout.flush()
    print('RESULT %d of %d' % (ok, len(sel)))
    return 0 if ok == len(sel) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
