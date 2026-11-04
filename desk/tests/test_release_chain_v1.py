"""the release chain a GRADE needs (trial CLEANT01_20261104: job 1002_GRADE_WINDFALL refused RELEASE, rc 6): no release pins an
interpreter path, the found-alarms table ships empty, and the engine's own release check of the GRADE and MONTH records passes when run
with the desk's PYTHON (DESK_PYTHON, set by desk.py tests; this interpreter when run alone)."""
import glob, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALARM = os.path.join(REPO, 'alarm')


def test_no_release_pins_an_interpreter_path():
    bad = []
    for p in glob.glob(os.path.join(ALARM, '**', 'RELEASE_*.json'), recursive=True):
        rt = json.load(open(p)).get('runtime') or {}
        if 'interpreter' in rt:
            bad.append((os.path.relpath(p, ALARM), rt['interpreter']))
    assert not bad, bad[:5]


def test_found_alarms_table_ships_empty():
    p = os.path.join(ALARM, '01_Detection', 'tree', 'team', 'RESEARCH', 'alarms', 'ALARMS_V1.tsv')
    rows = [l for l in open(p) if not l.startswith('#')]
    assert len(rows) == 1 and rows[0].startswith('utc\talarm\tname\t'), rows[:2]


def test_grade_and_month_release_check_pass_with_the_desk_python():
    py = os.environ.get('DESK_PYTHON') or sys.executable
    r = subprocess.run([py, '-B', os.path.join(REPO, 'desk', 'release_check_v1.py')], capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, (r.stdout + r.stderr)[-2000:]
    assert 'RELEASE GRADE OK' in r.stdout and 'RELEASE MONTH OK' in r.stdout, r.stdout
    assert not glob.glob(os.path.join(ALARM, '**', '__pycache__'), recursive=True)
