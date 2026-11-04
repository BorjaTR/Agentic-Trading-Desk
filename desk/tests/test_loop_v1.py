"""The generic learning loop (loop/): loop_check passes on an empty loop and on a planted one, and fails on a hand-written row."""
import os, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SC = os.path.join(REPO, 'loop', 'scripts')


def run(*a):
    return subprocess.run([sys.executable, '-B'] + list(a), capture_output=True, text=True)


def new_loop():
    d = os.path.join(tempfile.mkdtemp(prefix='desk_loop_'), 'loop')
    r = run(os.path.join(SC, 'loop_init.py'), d, '--roster', '1_IDEA,5_COUNT', '--tools-process', '9_TOOLS')
    assert r.returncode == 0, r.stderr
    open(os.path.join(d, '5_COUNT', 'STAGES.tsv'), 'w').write('stage\tquestion\ncount\twaves a month\n')
    return d


def check(d):
    return run(os.path.join(SC, 'loop_check.py'), d, '--accept')


ROW = dict(id='T1', process='5_COUNT', seat='desk', run='DESK_20251001', what_tried='a planted COUNT try', thought_file='thoughts/T1.md',
           expected='30 waves a month', actual='12 waves in Oct', verdict='FAILED', failed_stage='count', fail_layer='RULE', why='the rule is rare',
           went_well='none', failed='too few waves', slowed='none', gaps='none', improve='widen the moment, not the line', faster_next='size first',
           not_waste='none', minutes_active='3', minutes_waiting='0', minutes_blocked='0', closest_existing='none', tools_used='queue_job_v16',
           playground_ref='none', receipts='none', ledger_row='none', months_read='none', prompt_id='none', prompt_fix='none', model='none',
           next_action='another idea', lesson_id='none', reviewed_by='none')


def test_empty_loop_passes():
    d = new_loop()
    r = check(d)
    assert r.returncode == 0 and 'VERDICT\tFULL_PASS' in r.stdout and 'tried 0' in r.stdout, r.stdout
    shutil.rmtree(os.path.dirname(d))


def test_planted_loop_passes_and_hand_row_fails():
    d = new_loop()
    os.makedirs(os.path.join(d, '5_COUNT', 'thoughts'), exist_ok=True)
    open(os.path.join(d, '5_COUNT', 'thoughts', 'T1.md'), 'w').write('why this, what I doubted\n')
    t = os.path.join(d, '5_COUNT', 'TRIED_COUNT_V1.tsv')
    r = run(os.path.join(SC, 'add_row.py'), t, *['%s=%s' % kv for kv in ROW.items()])
    assert r.returncode == 0, r.stdout + r.stderr
    r = check(d)
    assert r.returncode == 0 and 'VERDICT\tFULL_PASS' in r.stdout and 'tried 1' in r.stdout, r.stdout
    bad = dict(ROW, id='T2', verdict='PLAN_ONLY')
    head = open(t).readline().rstrip('\n').split('\t')
    open(t, 'a').write('\t'.join(bad.get(c, '2026-01-01T00:00:00Z') for c in head) + '\n')   # a row by hand, past add_row
    r = check(d)
    assert r.returncode == 1 and 'VERDICT\tFAIL' in r.stdout and 'T2' in r.stdout, r.stdout
    shutil.rmtree(os.path.dirname(d))


def test_add_row_refuses_a_bad_verdict():
    d = new_loop()
    open(os.path.join(d, '5_COUNT', 'thoughts', 'T1.md'), 'w').write('x\n')
    r = run(os.path.join(SC, 'add_row.py'), os.path.join(d, '5_COUNT', 'TRIED_COUNT_V1.tsv'), *['%s=%s' % kv for kv in dict(ROW, verdict='GREAT').items()])
    assert r.returncode != 0 and 'verdict must be one of' in (r.stdout + r.stderr)
    shutil.rmtree(os.path.dirname(d))


def test_shipped_loop_passes():
    r = check(os.path.join(REPO, 'loop'))
    assert r.returncode == 0 and 'VERDICT\tFULL_PASS' in r.stdout, r.stdout
