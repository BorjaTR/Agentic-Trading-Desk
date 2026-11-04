"""The desk on real one-format data: the fixed sample of desk/data/SAMPLE_MANIFEST_V1.tsv (owner decision 3 Nov 2026 21:34Z). desk.py tests
passes DESK_LAB_DAYS, DESK_PYTHON and DESK_ALARM_SETTINGS from the settings file. Without the sample the tests are reported XFAIL with the
reason KNOWN (they need the lab's data): never a silent skip."""
import os, subprocess
import pytest

DESK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(DESK)
LAB = os.environ.get('DESK_LAB_DAYS', '')
PY = os.environ.get('DESK_PYTHON', '')
S = os.environ.get('DESK_ALARM_SETTINGS', '')
HC = os.path.join(REPO, 'alarm', '01_Detection', 'tree', 'team', 'RESEARCH', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools', 'hc_defs_v4_to20251231.py')
DEF = os.path.join(DESK, 'tests', 'data', 'SAMPLE_DEF_V1.json')
COINS = 'BTC,ETH,SOL,XRP,DOGE'


def need_sample():
    if not (LAB and PY and S) or not os.path.isfile(os.path.join(LAB, 'day=20251001', 'PRICE', 'index.json')):
        pytest.xfail('KNOWN: needs the one-format sample of desk/data/SAMPLE_MANIFEST_V1.tsv under DATA_ROOT/lab_days (the lab data, not shipped)')


def test_sample_is_there_and_unchanged():
    need_sample()
    r = subprocess.run([PY, '-B', os.path.join(DESK, 'data', 'sample_check.py'), LAB], capture_output=True, text=True)
    assert r.returncode == 0 and 'SAMPLE OK' in r.stdout, r.stdout


def test_hand_check_on_the_sample_runs_and_repeats():
    need_sample()
    outs = []
    for _ in range(2):
        r = subprocess.run([PY, '-B', HC, '--settings', S, DEF, '20251001', '20251002', COINS, '5', 'px,move'],
                           capture_output=True, text=True, cwd=os.path.join(REPO, 'alarm'))
        assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
        outs.append(r.stdout)
    assert outs[0] == outs[1]
    assert 'FIRE' in outs[0] or 'fires' in outs[0].lower(), outs[0][-1500:]
