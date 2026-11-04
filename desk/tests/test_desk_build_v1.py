"""Tests of the desk's own build tools (path scan, judge parity, settings reader). Planted files only; no data.
The planted words are built from pieces so this file itself holds none of them."""
import os, shutil, subprocess, sys, tempfile

DESK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(DESK)
SCAN = os.path.join(DESK, 'build', 'path_scan_v1.py')
PARITY = os.path.join(DESK, 'build', 'judge_parity_v1.py')
OWNER = 'bor' + 'ja'


def run(*a):
    return subprocess.run([sys.executable, '-B'] + list(a), capture_output=True, text=True)


def mini_repo(extra=None, allow=''):
    d = tempfile.mkdtemp(prefix='desk_scan_')
    os.makedirs(os.path.join(d, 'desk')); os.makedirs(os.path.join(d, 'alarm'))
    open(os.path.join(d, 'alarm', 'ok.py'), 'w').write("x = 1  # nothing to see\n")
    for rel, text in (extra or {}).items():
        os.makedirs(os.path.dirname(os.path.join(d, rel)), exist_ok=True)
        open(os.path.join(d, rel), 'w').write(text)
    open(os.path.join(d, 'desk', 'PATH_ALLOW.tsv'), 'w').write('file\tkind\ttext\treason\n' + allow)
    return d


def test_clean_mini_repo_passes():
    d = mini_repo()
    r = run(SCAN, d)
    assert r.returncode == 0 and 'PATH SCAN CLEAN' in r.stdout, r.stdout
    shutil.rmtree(d)


def test_each_kind_fails():
    plants = {
        'OWNER': 'name = "%s"\n' % OWNER.capitalize(),
        'USER_PATH': 'p = "/Us' + 'ers/' + OWNER + '/dev"\n',
        'MACHINE': 'host = "Mac ' + 'mini"\n',
        'HOST': 'url = "http://lab-box.lo' + 'cal:8080"\n',
        'SEAT_REQ': 'print("read h' + 'b/DSK.txt and wait")\n',
    }
    for kind, text in plants.items():
        d = mini_repo({'alarm/bad.py': text})
        r = run(SCAN, d)
        assert r.returncode == 3 and kind in r.stdout, (kind, r.stdout)
        shutil.rmtree(d)


def test_allow_row_with_reason_passes_and_unused_row_fails():
    d = mini_repo({'alarm/bad.py': 'print("read h' + 'b/DSK.txt")\n'}, 'alarm/bad.py\tSEAT_REQ\th' + 'b/DSK\ta reason\n')
    assert run(SCAN, d).returncode == 0
    shutil.rmtree(d)
    d = mini_repo({}, 'alarm/none.py\tOWNER\t\ta reason\n')
    r = run(SCAN, d)
    assert r.returncode == 3 and 'UNUSED ALLOW' in r.stdout
    shutil.rmtree(d)


def test_allow_row_without_reason_is_refused():
    d = mini_repo({}, 'alarm/x.py\tOWNER\t\t\n')
    r = run(SCAN, d)
    assert r.returncode != 0 and 'REFUSED' in (r.stdout + r.stderr)
    shutil.rmtree(d)


def test_repo_scan_is_clean():
    r = run(SCAN, REPO)
    assert r.returncode == 0, r.stdout[-2000:]


def test_parity_catches_a_changed_judge():
    rel = tempfile.mkdtemp(prefix='desk_rel_'); al = tempfile.mkdtemp(prefix='desk_al_')
    for root in (rel, al):
        p = os.path.join(root, 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools'); os.makedirs(p)
    body = 'RULE = 0.05\n'
    open(os.path.join(rel, 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py'), 'w').write(body)
    open(os.path.join(al, 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py'), 'w').write(body)
    r = run(PARITY, rel, al)
    assert r.returncode == 3 and 'IDENTICAL' in r.stdout and 'MISSING' in r.stdout   # the other judge files are missing here
    open(os.path.join(al, 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py'), 'w').write('RULE = 0.01\n')
    r = run(PARITY, rel, al)
    assert 'DIFFERENT' in r.stdout
    shutil.rmtree(rel); shutil.rmtree(al)


def test_settings_reader_refuses_unknown_key_and_alarm_inside():
    sys.path.insert(0, DESK)
    import desk
    d = tempfile.mkdtemp(prefix='desk_set_')
    p = os.path.join(d, 'a.env')
    open(p, 'w').write('DATA_ROOT=data\nOUTPUT_ROOT=out\nPYTHON=%s\nSEAT=X\n' % sys.executable)
    try:
        desk.read_settings(p); assert False
    except desk.Refused as e:
        assert 'BAD LINE' in str(e)
    open(p, 'w').write('DATA_ROOT=data\nOUTPUT_ROOT=alarm/out\nPYTHON=%s\n' % sys.executable)
    try:
        desk.read_settings(p); assert False
    except desk.Refused as e:
        assert 'inside alarm/' in str(e)
    shutil.rmtree(d)
