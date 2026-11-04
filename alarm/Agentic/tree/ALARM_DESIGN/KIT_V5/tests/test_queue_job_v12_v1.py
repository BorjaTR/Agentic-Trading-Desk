#!/usr/bin/env python3
"""test_queue_job_v12_v1.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): the three
changes of queue_job_v12.py, on planted runs in temp folders (seconds; no market data; nothing outside the temp folders):
  N1  next_hint: each refusal text of v12 that has a hint gets it; others get none.
  D1  dry_checks with no run folder: run folder, registers and claim MISSING (all three listed, not only the first).
  D2  dry_checks on a full run: all OK; ENTRY with only CARD_<IDEA>.md is OK (copied when queued); with neither card MISSING.
  D3  dry_checks MONTH: a variant with 3 of 4 FORECASTS rows is MISSING and names the month it lacks; 4 rows OK.
  C1  plan ENTRY: ALARM_CARD.md missing, CARD_<IDEA>.md there -> CFG['CARD_COPY'] = (card, ALARM_CARD.md) and the checks go on (the
      next refusal is the hand-off's); neither -> NO ALARM CARD; ALARM_CARD.md there -> no copy planned.
  V1  the v11 suite (test_queue_job_v11_clean_v1.py beside this file) passes on v12 too (its Q1-Q5 hold).
Then planted bugs in copies of queue_job_v12.py (each must fail a test). Run from inside an Alarm folder:
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_queue_job_v12_v1.py"""
import hashlib, importlib.util, os, shutil, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
QFILE = os.path.join(HERE, '..', 'tools', 'queue_job_v12.py')
PKG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
SV = os.path.join(PKG, '_tools', 'settings_v1.py')
RUN = 'AB1_20261101'
IDEA = 'PLANT'
N = [0]
HEAD = {'VARIANTS': 'idea\tV\tlean\tdef_rel\tdef_sha16\tprereg_rel\tprereg_sha16\treason',
        'FORECASTS': 'idea\tV\tscope\tfile_rel\tfile_sha16\tgap15_lo\tgap15_hi\tgap1h_lo\tgap1h_hi',
        'RUNS': 'kind\tidea\tvariants\treceipts_rel', 'DECISIONS': 'idea\tV\tstate\tgrade_job'}


def load(qfile):
    N[0] += 1
    sp = importlib.util.spec_from_file_location('queue_job_v12_test_%d' % N[0], qfile)
    assert sp is not None and sp.loader is not None, qfile
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def w(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(text)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def plant(h, m, card=None, forecasts=4):
    """a run under h/runs/RUN: registers, claim, V1 sealed (definition and card), a finished GRADE receipt; card: 'ALARM', 'SEALED' or None"""
    run = os.path.join(h, 'runs', RUN)
    for n in m.REGISTERS:
        w(os.path.join(run, 'registers', n + '.tsv'), HEAD.get(n, 'x') + '\n')
    w(os.path.join(h, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUN, IDEA)), 'claim\n')
    d = os.path.join(run, 'ideas', IDEA, 'defs', 'V1.json'); w(d, '{"window": {"first": "20250901", "last": "20260430"}}')
    pre = ('CARD_%s.md' if card is not None else 'PREREG_%s.md') % IDEA     # with no card at all, the prereg is another file
    c = os.path.join(run, 'ideas', IDEA, pre); w(c, 'sealed card\n')
    with open(os.path.join(run, 'registers', 'VARIANTS.tsv'), 'a') as f:
        f.write('%s\tV1\tFADE\tideas/%s/defs/V1.json\t%s\tideas/%s/%s\t%s\t-\n' % (IDEA, IDEA, sha16(d), IDEA, pre, sha16(c)))
    if card == 'ALARM':
        w(os.path.join(run, 'ideas', IDEA, 'ALARM_CARD.md'), 'sealed card\n')
    fc = os.path.join(run, 'ideas', IDEA, 'FC.md'); w(fc, 'forecast\n')
    with open(os.path.join(run, 'registers', 'FORECASTS.tsv'), 'a') as f:
        for mth in m.MONTHS[:forecasts]:
            f.write('%s\tV1\t%s\tideas/%s/FC.md\t%s\t1\t2\t3\t4\n' % (IDEA, mth, IDEA, sha16(fc)))
    w(os.path.join(run, 'receipts', '9_GRADE_%s' % IDEA, 'STAGES.tsv'), 'stage\trc\nend\t0\n')
    return run


def suite(qfile):
    f = []
    def ck(name, ok):
        if not ok:
            f.append(name)
    m = load(qfile)
    msgs = {'NO RUN FOLDER /x': 'TEMPLATE_V4', 'NO REGISTER /x/registers/RUNS.tsv': 'TEMPLATE_V4',
            'IDEA NOT CLAIMED: no /x': 'IDEAS_CLAIMED', 'NO ALARM CARD /x (the store registers it)': 'CARD_<IDEA>.md',
            'V1: NO SEALED FORECAST FOR 2603 IN FORECASTS (seal all of Jan-Apr first)': 'scope 2601, 2602, 2603, 2604',
            'VARIANT V1 OF X NOT IN VARIANTS: register it before its job (SKILL step E)': 'VARIANTS row',
            'DISK BUDGET: your run holds 1 MB': 'DSK', 'DISK: SCRATCH_DISK free 1 MB': 'DSK'}
    for k, want in msgs.items():
        h = m.next_hint(k)
        ck('N1 hint for %s' % k[:20], h is not None and want in h)
    ck('N1 no hint for an unknown refusal', m.next_hint('BAD RUN TAG x') is None)
    with tempfile.TemporaryDirectory() as t:
        m.CFG['H'] = t
        r = {n: ok for n, ok, _ in m.dry_checks(RUN, 'COUNT', IDEA, 'V1=x')}
        ck('D1 all three missing listed', r == {'run folder': False, 'registers': False, 'claim': False})
        ck('D1 run folder has its NEXT', [m.next_hint(d) is not None for n, ok, d in m.dry_checks(RUN, 'COUNT', IDEA, 'V1=x')] == [True, True, True])
        plant(t, m, card='SEALED')
        r = m.dry_checks(RUN, 'ENTRY', IDEA, 'V1')
        ck('D2 full run OK', all(ok for _, ok, _ in r) and [n for n, _, _ in r] == ['run folder', 'registers', 'claim', 'card'])
        ck('D2 sealed card named', 'copied to ALARM_CARD.md when queued' in r[-1][2])
        os.rename(os.path.join(t, 'runs', RUN, 'ideas', IDEA, 'CARD_%s.md' % IDEA), os.path.join(t, 'cardaway'))
        r = m.dry_checks(RUN, 'ENTRY', IDEA, 'V1')
        ck('D2 no card MISSING', r[-1][0] == 'card' and not r[-1][1] and 'NO ALARM CARD' in r[-1][2])
        r = m.dry_checks(RUN, 'MONTH', IDEA, 'V1')
        ck('D3 4 rows OK', r[-1] == ('forecasts V1', True, '4 rows 2601,2602,2603,2604'))
    with tempfile.TemporaryDirectory() as t:
        m.CFG['H'] = t
        plant(t, m, card='SEALED', forecasts=3)
        r = m.dry_checks(RUN, 'MONTH', IDEA, 'V1')
        ck('D3 3 rows MISSING names 2604', r[-1][0] == 'forecasts V1' and not r[-1][1] and 'rows needed: 2604' in r[-1][2])
    for card, want in (('SEALED', 'copy'), (None, 'NO ALARM CARD'), ('ALARM', 'none')):
        with tempfile.TemporaryDirectory() as t:
            m.CFG['H'] = t; m.CFG['JOB_SCRATCH'] = t; m.CFG.pop('CARD_COPY', None)
            run = plant(t, m, card=card)
            try:
                m.plan(run, 'ENTRY', IDEA, 'V1', '9_GRADE_%s' % IDEA)
                got = 'no refusal'
            except m.Refused as e:
                got = str(e)
            cc = m.CFG.get('CARD_COPY')
            if want == 'copy':
                ck('C1 copy planned', cc == (os.path.join(run, 'ideas', IDEA, 'CARD_%s.md' % IDEA), os.path.join(run, 'ideas', IDEA, 'ALARM_CARD.md')))
                ck('C1 checks go on to the hand-off', got.startswith('NO HAND-OFF RULES'))
                ck('C1 nothing copied at plan time', not os.path.exists(os.path.join(run, 'ideas', IDEA, 'ALARM_CARD.md')))
            elif want == 'NO ALARM CARD':
                ck('C1 neither card refused', got.startswith('NO ALARM CARD') and cc is None)
            else:
                ck('C1 ALARM_CARD.md there: no copy', cc is None and got.startswith('NO HAND-OFF RULES'))
    src = open(qfile).read()
    ck('C1 copy opened x and checked', "open(dst_card, 'xb')" in src and "raise Refused('CARD COPY DIFFERS" in src)
    ck('C1 copy after fill, before the claim', src.index("    if CFG.get('CARD_COPY'):                     # v12") > src.index("    fill('0')                                    # all checks pass")
       and src.index("    if CFG.get('CARD_COPY'):                     # v12") < src.index("r = subprocess.run(CFG['ALLOC'] + ['claim', seat, '1']"))
    return f


PLANTS = [
    ("    ('IDEA NOT CLAIMED', ", "    ('IDEA NOT CLAIMEDX', "),
    ("        if start in msg:\n            return what\n", "        if msg.startswith(start):\n            return what\n"),
    ("    out = [('run folder', os.path.isdir(run), run if", "    out = [('run folder', True, run if"),
    ("    out.append(('registers', not miss,", "    out.append(('registers', True,"),
    ("            lack = [m for m in MONTHS if m not in have]", "            lack = [m for m in MONTHS[:3] if m not in have]"),
    ("            CFG['CARD_COPY'] = (sealed, card)", "            raise Refused('NO ALARM CARD %s (the store registers it)' % card)"),
    ("        ok = os.path.isfile(a) or os.path.isfile(c)", "        ok = os.path.isfile(a)"),
    ("open(dst_card, 'xb')", "open(dst_card, 'wb')"),
    ("    ('DISK BUDGET', ", "    ('DISK BUDGETX', "),
]


def planted_package(t, text):
    a = os.path.join(t, 'Alarm')
    os.makedirs(os.path.join(a, '_tools')); os.makedirs(os.path.join(a, 'settings'))
    shutil.copyfile(SV, os.path.join(a, '_tools', 'settings_v1.py'))
    q = os.path.join(a, 'Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5', 'tools', 'queue_job_v12.py')
    os.makedirs(os.path.dirname(q))
    open(q, 'w').write(text)
    return q


def v11_suite_on_v12():
    """V1: test_queue_job_v11_clean_v1's suite() on v12 (its Q1-Q5)"""
    p = os.path.join(HERE, 'test_queue_job_v11_clean_v1.py')
    sp = importlib.util.spec_from_file_location('t_v11_on_v12', p); t = importlib.util.module_from_spec(sp); sp.loader.exec_module(t)
    return t.suite(QFILE)


if __name__ == '__main__':
    fails = suite(QFILE)
    v1 = v11_suite_on_v12()
    print('TESTS %s %s' % ('PASS' if not fails else 'FAIL', ' | '.join(fails)))
    print('V1 the v11 suite on v12: %s %s' % ('PASS' if not v1 else 'FAIL', ' | '.join(v1)))
    src = open(QFILE).read()
    killed = 0
    with tempfile.TemporaryDirectory() as t:
        ctl = suite(planted_package(os.path.join(t, 'control'), src))
        print('CONTROL (the real text in a planted package) %s' % ('PASS' if not ctl else 'FAIL ' + ' | '.join(ctl)))
    for i, (a, b) in enumerate(PLANTS, 1):
        if src.count(a) != 1:
            print('PLANT %d: its text is found %d times, want 1' % (i, src.count(a))); continue
        with tempfile.TemporaryDirectory() as t:
            try:
                g = suite(planted_package(t, src.replace(a, b)))
            except Exception as ex:
                g = ['a crash (%s)' % type(ex).__name__]
        killed += bool(g)
        print('PLANT %d %s' % (i, ('killed by ' + g[0]) if g else 'ALIVE'))
    print('PLANTED BUGS %d of %d killed' % (killed, len(PLANTS)))
    sys.exit(0 if not fails and not v1 and not ctl and killed == len(PLANTS) else 1)
