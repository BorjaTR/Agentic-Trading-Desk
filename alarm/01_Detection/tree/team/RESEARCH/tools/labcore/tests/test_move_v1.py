"""test_move_v1 (BUILD2, 23 Oct 2026): the MOVE PROOF of labcore step 1 (TOOL_DESIGN V4.2 0d b: a helper moves with its tests). It is not
TEST1's test of labcore (TEST1 writes those); it proves the moved functions are the originals:
  M1 SOURCE: each moved function's code is the original's, line for line (ast dump), read from the pinned source files;
  M2 SAME OUTPUT: on planted inputs labcore gives what bucket_proof / money_v1 give (waves, weights, by_wave with one seed, gates,
     the settings loader), including the refusals (a month law.py refuses, an outcome month not opened, a judge month with no PREREG row);
  M3 the new want_sha16 check refuses a settings file whose sha16 differs, and loads it when it matches.
Run: TMPDIR=<SCRATCH>/work_BUILD2/tmp /usr/sbin/taskpolicy -b nice -n 10 python3 -B -m pytest -q test_move_v1.py"""
import ast, inspect, json, os, sys
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.realpath(os.path.join(HERE, '..', '..'))
BP_DIR = os.path.join(TOOLS, 'bucket_proof')
PINS = {'oracle/bucket_proof_oracle.py': '2b615f53396155d0', 'money_v1.py.pre_BUILD2_20261023T131752Z': '3bb9bf378008aed5'}
# money_v1.py moved on (BUILD2 13:17Z, the labcore gate); the version by_wave was moved from is its twin .pre_BUILD2_20261023T131752Z
# bucket_proof.py moved on (QUANT f6c5f994, 12:31:40Z); the version labcore moved is kept by QUANT as oracle/bucket_proof_oracle.py
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.join(BP_DIR, 'oracle')); sys.path.insert(0, BP_DIR)
from labcore import costs, gates, ids, settings, waves   # noqa: E402
import bucket_proof_oracle as BP                          # noqa: E402
import importlib.machinery as _ILM                        # noqa: E402
MV = _ILM.SourceFileLoader('money_v1_moved', os.path.join(BP_DIR, 'money_v1.py.pre_BUILD2_20261023T131752Z')).load_module()   # noqa: E402

MOVED = [(ids.sha16_file, 'oracle/bucket_proof_oracle.py', 'sha16_file'), (gates.month_last_day, 'oracle/bucket_proof_oracle.py', 'month_last_day'),
         (gates.check_window, 'oracle/bucket_proof_oracle.py', 'check_window'), (gates.ledger_rows, 'oracle/bucket_proof_oracle.py', 'ledger_rows'),
         (waves.waves, 'oracle/bucket_proof_oracle.py', 'waves'),
         (waves.wave_weights, 'oracle/bucket_proof_oracle.py', 'wave_weights'), (costs.load_cost, 'oracle/bucket_proof_oracle.py', 'load_cost')]
# outcome_allowed left M1 at v2 (SKEPTIC 02-04/05: law, WINDOWS, now_utc required, one look; tests/test_skeptic02_v1.py); M2 still
# checks it agrees with the original on the BUILD months the original opened
# by_wave left M1 at v2 (it now refuses drop_best != 0, TEST1 L09b); M2 still proves it gives the original's answer with drop_best=0


def test_M0_pins():
    for f, want in PINS.items():
        assert ids.sha16_file(os.path.join(BP_DIR, f)) == want, f


def _fn_ast(path, name):
    tree = ast.parse(open(path).read())
    node = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name][0]
    return ast.dump(node, include_attributes=False)


@pytest.mark.parametrize('fn,src,name', MOVED, ids=[m[2] for m in MOVED])
def test_M1_source_is_the_original(fn, src, name):
    mine = ast.dump([n for n in ast.parse(open(inspect.getsourcefile(fn)).read()).body
                     if isinstance(n, ast.FunctionDef) and n.name == name][0], include_attributes=False)
    assert mine == _fn_ast(os.path.join(BP_DIR, src), name)


def test_M2_waves_same_output():
    rng = np.random.default_rng(7); t = np.sort(rng.uniform(0, 86400, 400)); t = rng.permutation(t)
    for gap in (60, 1800, 7200):
        assert np.array_equal(waves.waves(t, gap), BP.waves(t, gap))
        w = waves.waves(t, gap)
        assert np.array_equal(waves.wave_weights(w), BP.wave_weights(w))
    v = rng.normal(0, 1, 400); v[::17] = np.nan; w = waves.waves(t, 1800)
    a = waves.by_wave(v, w, None, np.random.default_rng(3), B=200); b = MV.by_wave(v, w, None, np.random.default_rng(3), B=200)
    assert a == b
    with pytest.raises(TypeError):
        waves.by_wave(v, w, None, np.random.default_rng(3), B=10, drop_best=5)


def _settings(tmp, **kw):
    s = dict(months=['202511', '202512'], outcome_months=['202511'], fit_months=['202511'], judge_months=['202512'])
    s.update(kw); p = os.path.join(str(tmp), 'set.json'); json.dump(s, open(p, 'w')); return p


def test_M2_gates_same_output(tmp_path):
    law = gates.load_law()
    for m in ('202509', '202602', '202605', '202606', '202610'):
        assert gates.month_last_day(m) == BP.month_last_day(m)
    s = json.load(open(_settings(tmp_path)))
    assert gates.check_window(s, law) is None and BP.check_window(s, law) is None
    for bad in (dict(months=['202607']), dict(judge_months=['202603'])):
        s2 = json.load(open(_settings(tmp_path, **bad)))
        with pytest.raises(ValueError):
            gates.check_window(s2, law)
        with pytest.raises(ValueError):
            BP.check_window(s2, law)
    now = '20261023T130000Z'
    assert gates.outcome_allowed(s, ['202511'], None, now) is True and BP.outcome_allowed(s, ['202511']) is True
    for months in (['202512'], ['202601']):
        with pytest.raises(PermissionError):
            gates.outcome_allowed(s, months, None, now)
        with pytest.raises(PermissionError):
            BP.outcome_allowed(s, months)


def test_M2_M3_settings_loader(tmp_path):
    p = _settings(tmp_path)
    a = settings.load_settings(p); b = BP.load_settings(p)
    assert a == b and a['_sha16'] == ids.sha16_file(p)
    assert settings.load_settings(p, want_sha16=a['_sha16'])['_sha16'] == a['_sha16']
    with pytest.raises(ValueError):
        settings.load_settings(p, want_sha16='0' * 16)


# ---------------------------------------------------------------- jobgate (BUILD1-132312): moved verbatim from gate_wait_v1 3dc74609; gate_wait as BUILD1's fix e2fe77ff (BUILD1-135033)
def test_M4_jobgate_moved_verbatim_and_same_behaviour(tmp_path):
    from labcore import jobgate
    src = os.path.realpath(os.path.join(TOOLS, '..', '..', 'FEED', 'code', 'gate_wait_v1.py'))
    assert ids.sha16_file(src) == 'e2fe77ffd73b53f9'
    for name in ('state',):                                                  # gate_wait grew the resume jitter (LIVE4 14:30:31Z): M5 tests it
        mine = [n for n in ast.parse(open(jobgate.__file__).read()).body if isinstance(n, ast.FunctionDef) and n.name == name][0]
        assert ast.dump(mine) == _fn_ast(src, name), name
    g = tmp_path / 'GATE.txt'
    assert jobgate.state(str(g)) == 'PAUSE'                       # missing gate = PAUSE
    g.write_text('RUN\n'); assert jobgate.gate_wait(str(g), sleep=lambda s: None) == 0
    g.write_text('PAUSE\n'); t = [0.0]
    with pytest.raises(TimeoutError):
        jobgate.gate_wait(str(g), poll_s=10, max_wait_s=30, log=lambda s: None, sleep=lambda s: t.__setitem__(0, t[0] + s))
    assert t[0] == 30                                              # a planted sleep times out after exactly the polls slept
    n = []
    with pytest.raises(TimeoutError):                              # a sleep that takes no time still times out (the bug: wall clock read 0)
        jobgate.gate_wait(str(g), poll_s=10, max_wait_s=30, log=lambda s: None, sleep=lambda s: n.append(s))
    assert len(n) == 3


def test_M5_jobgate_resume_jitter(tmp_path):
    """LIVE4 14:30:31Z: after a PAUSE, a job with a job_id waits 0-300 s more, fixed by its id (sha256, never builtin hash()), so
    jobs resume one at a time; no wait, no jitter; the gate is read again after the jitter. Mutant killed: jitter at a plain start."""
    from labcore import jobgate
    g = tmp_path / 'GATE.txt'; g.write_text('RUN\n'); slept = []
    assert jobgate.gate_wait(str(g), sleep=slept.append, job_id='J1') == 0 and slept == []          # no PAUSE seen: starts at once
    ids = ['478024', '471219', '471220', '471221']; js = [jobgate.jitter_s(i) for i in ids]
    assert all(0 <= j <= 300 for j in js) and len(set(js)) > 1 and js == [jobgate.jitter_s(i) for i in ids]
    state = iter(['PAUSE', 'RUN', 'RUN'])
    g.write_text('PAUSE\n'); slept = []

    def sl(s):
        slept.append(s); g.write_text(next(state) + '\n')
    w = jobgate.gate_wait(str(g), poll_s=10, log=lambda s: None, sleep=sl, job_id='478024')
    assert slept == [10, 10, jobgate.jitter_s('478024')] and w == 20 + jobgate.jitter_s('478024')
