"""desk.py setup and the commands after it (GPT DESKPKG-V1 items 1, 2): setup never creates or writes the data folders; it makes an empty
registry so the first copy search runs on a fresh desk; every other command refuses before setup and after the settings change."""
import os, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESK = os.path.join(REPO, 'desk', 'desk.py')


def desk(settings, *a):
    return subprocess.run([sys.executable, '-B', DESK, '--settings', settings] + list(a), capture_output=True, text=True, cwd=REPO)


def fresh():
    t = tempfile.mkdtemp(prefix='desk_setup_')
    data, out = os.path.join(t, 'data_ro'), os.path.join(t, 'out')
    os.makedirs(data)
    st = os.path.join(t, 'desk.env')
    open(st, 'w').write('DATA_ROOT=%s\nOUTPUT_ROOT=%s\nPYTHON=%s\n' % (data, out, sys.executable))
    return t, data, out, st


def test_setup_never_writes_the_data_folder_and_makes_an_empty_registry():
    t, data, out, st = fresh()
    r = desk(st, 'setup')
    assert r.returncode == 0, r.stderr
    assert os.listdir(data) == [], os.listdir(data)                      # no lab_days, no research_days created
    assert 'lab_days' in r.stdout and 'absent' in r.stdout
    reg = os.path.join(out, 'research', 'ALARM_DESIGN', 'REGISTRY', 'ALARM_REGISTRY_V1.tsv')
    rows = [l for l in open(reg) if not l.startswith('#')]
    assert len(rows) == 1 and rows[0].startswith('alarm_id\tkind\t')       # header only
    before = open(reg).read()
    assert desk(st, 'setup').returncode == 0 and open(reg).read() == before  # a second setup never overwrites it


def test_first_copy_search_runs_on_a_fresh_desk():
    t, data, out, st = fresh()
    assert desk(st, 'setup').returncode == 0
    r = desk(st, 'run', '08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py', 'S', 'liquidation', 'flush')
    assert r.returncode == 0, r.stdout + r.stderr
    assert 'NO REGISTRY' not in r.stdout + r.stderr


def test_commands_refuse_before_setup_and_after_a_settings_change():
    t, data, out, st = fresh()
    r = desk(st, 'env')
    assert r.returncode == 2 and 'NOT SET UP' in r.stderr
    assert desk(st, 'setup').returncode == 0
    assert desk(st, 'env').returncode == 0
    other = os.path.join(t, 'data_other'); os.makedirs(other)
    text = open(st).read().replace('DATA_ROOT=%s' % data, 'DATA_ROOT=%s' % other)
    open(st, 'w').write(text)
    r = desk(st, 'env')
    assert r.returncode == 2 and 'SETTINGS CHANGED' in r.stderr, r.stderr
    assert os.listdir(data) == [] and os.listdir(other) == []


def test_overlapping_roots_are_refused_before_any_write():
    t = tempfile.mkdtemp(prefix='desk_setup_')
    data = os.path.join(t, 'data'); os.makedirs(data)
    for out in (os.path.join(data, 'output'), data):                     # nested, and the same folder
        st = os.path.join(t, 'nested.env')
        open(st, 'w').write('DATA_ROOT=%s\nOUTPUT_ROOT=%s\nPYTHON=%s\n' % (data, out, sys.executable))
        r = desk(st, 'setup')
        assert r.returncode == 2 and 'overlap' in r.stderr, r.stdout + r.stderr
        assert os.listdir(data) == []
    alias = os.path.join(t, 'alias'); os.symlink(data, alias)                # a symlink alias of the data folder
    st = os.path.join(t, 'alias.env')
    open(st, 'w').write('DATA_ROOT=%s\nOUTPUT_ROOT=%s\nPYTHON=%s\n' % (data, os.path.join(alias, 'out'), sys.executable))
    r = desk(st, 'setup')
    assert r.returncode == 2 and 'overlap' in r.stderr and os.listdir(data) == []
