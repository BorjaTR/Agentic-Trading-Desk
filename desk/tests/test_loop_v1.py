"""The learning loop (loop/, LEARNING_LOOP_V1_1: loop/generic and loop/packs/alarm): its own test suites (loop/TEST.md rows 1 to 13b)
and two smoke checks, each run from a copy of loop/ in a new temp folder (TMPDIR), so nothing is written into the repo.
Rows that cannot pass in this repo are KNOWN (xfail, with the reason), never skipped."""
import os, shutil, subprocess, sys, tempfile
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOOP = os.path.join(REPO, 'loop')
KNOWN = {
    'knowledge_v2': 'KNOWN: test_v0_as_filed_names_from_file_and_todo_bars_refused reads packs/strategy_draft, not shipped (the strategy pack comes later)',
    'queue_job_v15_scout': 'KNOWN: the alarm pack playground queue copy refuses outside the lab install (NOT INSIDE AN ALARM PACKAGE)',
    'bar_check_v2': 'KNOWN: test_08_host_path_old_rows expects the lab VM session path, which the build scrub replaced by <VM_SESSION>',
}
ROWS = [
    ('knowledge_v2', 'generic/tools/knowledge_v2', ['-m', 'unittest', 'test_build_knowledge_v2']),
    ('knowledge_v2_c218', 'generic/tools/knowledge_v2', ['-m', 'unittest', 'test_knowledge_v2_c218']),
    ('reg_audit', 'generic/tools/registers', ['test_reg_audit.py']),
    ('reg_report', 'generic/tools/registers', ['test_reg_report.py']),
    ('reg_baseline', 'generic/tools/registers', ['test_reg_baseline.py']),
    ('messy_triage_v1', 'generic/tools/registers', ['test_messy_triage_v1.py']),
    ('blind_kit_v1', 'generic/tools/drills', ['test_blind_kit_v1.py']),
    ('leak_scan_v1', 'generic/tools/drills', ['test_leak_scan_v1.py']),
    ('agreement_v1', 'generic/tools/drills', ['test_agreement_v1.py']),
    ('agreement_self_test', 'generic/tools/drills', ['agreement_v1.py', '--self-test']),
    ('queue_job_v15_scout', 'packs/alarm/playground', ['test_queue_job_v15_scout.py']),
    ('bar_check_v2', 'packs/alarm/tools', ['test_bar_check_v2.py']),
    ('forecast_score', 'packs/alarm/tools', ['test_forecast_score.py']),
    ('check_round_v1', 'packs/alarm/tools', ['test_check_round_v1.py']),
    ('pool_splits_v1', 'packs/alarm/tools', ['test_pool_splits_v1.py']),
    ('speed_report_v1', 'packs/alarm/tools', ['test_speed_report_v1.py']),
]


@pytest.fixture(scope='module')
def copy():
    top = tempfile.mkdtemp(prefix='desk_loop_')
    d = os.path.join(top, 'loop'); tmp = os.path.join(top, 'tmp'); os.makedirs(tmp)
    shutil.copytree(LOOP, d)
    env = dict(os.environ, LL_TEST_TMP=tmp, KNOW_V2_TMP=tmp, TMPDIR=tmp, PYTHONDONTWRITEBYTECODE='1')
    yield d, env
    shutil.rmtree(top)


def run(cwd, args, env):
    return subprocess.run([sys.executable, '-B'] + args, cwd=cwd, env=env, capture_output=True, text=True, timeout=300)


@pytest.mark.parametrize('name,folder,args', ROWS, ids=[r[0] for r in ROWS])
def test_loop_suite(copy, name, folder, args):
    d, env = copy
    r = run(os.path.join(d, folder), args, env)
    if r.returncode != 0 and name in KNOWN:
        pytest.xfail(KNOWN[name])
    assert r.returncode == 0, (r.stdout + r.stderr)[-2000:]


def test_new_alarm_store_checks_clean(copy):
    d, env = copy
    k = os.path.join(d, 'generic', 'tools', 'knowledge_v2', 'build_knowledge_v2.py')
    store = os.path.join(env['LL_TEST_TMP'], 'store_alarm')
    pack = os.path.join(d, 'packs', 'alarm', 'alarm.json')
    assert run(d, [k, 'init', '--pack', pack, '--dir', store], env).returncode == 0
    r = run(d, [k, 'check', '--pack', pack, '--dir', store], env)
    assert r.returncode == 0 and 'CHECK PASS' in r.stdout, r.stdout + r.stderr


def test_leak_scan_refuses_without_a_pattern(copy):
    d, env = copy
    e = dict(env); e.pop('LEAK_SCAN_PATTERN_FILE', None)
    r = run(d, [os.path.join(d, 'generic', 'tools', 'drills', 'leak_scan_v1.py'), '--secrets', os.path.join(d, 'generic', 'LOOP.md'),
                '--targets', os.path.join(d, 'generic', 'prompts')], e)
    assert r.returncode == 2 and 'REFUSED NO_PATTERN' in (r.stdout + r.stderr), r.stdout + r.stderr


def test_no_held_out_file_ships():
    bad = [os.path.join(p, f) for p, _, fs in os.walk(LOOP) for f in fs if 'heldout' in f.lower() or 'held_out' in f.lower()]
    assert not bad, bad
