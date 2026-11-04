"""test_labcore_v1 (TEST1, 23 Oct 2026, PAPER): the tester's tests of labcore step 1 (ids, settings, gates, waves), from the meaning
written in FUNCTIONS_V1.tsv and TOOL_DESIGN V4.2 section 0d (LAB1 11:36:51Z), not from BUILD2's move proof. Each function: its meaning on
plants, equal to its pinned original on random plants, the registry row true, a SPEED bar. pytest only (the analyst venv). Run:
  cd team/RESEARCH/tools/labcore/tests && TMPDIR=<SCRATCH>/work_TEST1/tmp /usr/sbin/taskpolicy -b nice -n 10 \\
    <PYTHON> -m pytest -q test_labcore_v1.py            (LABCORE_DIR=<copy> to test a planted copy)
Marker 'defect': a test that names a defect found today (by_wave's drop_best is accepted and ignored); left out of the mutant runs."""
import hashlib, importlib, importlib.util, inspect, json, os, re, sys, time
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.environ.get('LABCORE_DIR') or os.path.dirname(TESTS)               # .../tools/labcore (or a planted copy)
sys.path.insert(0, os.path.dirname(PKG_DIR))
for k in [k for k in sys.modules if k == 'labcore' or k.startswith('labcore.')]:
    del sys.modules[k]
labcore = importlib.import_module(os.path.basename(PKG_DIR))
waves = importlib.import_module(labcore.__name__ + '.waves')
gates = importlib.import_module(labcore.__name__ + '.gates')
ids = importlib.import_module(labcore.__name__ + '.ids')
settings = importlib.import_module(labcore.__name__ + '.settings')
F = '<LAB_REPO>/forensics'
LAW = os.path.join(F, 'team', 'LAB3', 'code', 'lab3', 'law.py')
ORIG = {'bucket_proof': (os.path.join(F, 'team/RESEARCH/tools/bucket_proof/bucket_proof.py'), '2b615f53396155d0'),
        'money_v1': (os.path.join(F, 'team/RESEARCH/tools/bucket_proof/money_v1.py'), '3bb9bf378008aed5')}


def the_law():
    """load_law() by its own default path; a planted copy outside the tree is handed the real path"""
    return gates.load_law(LAW) if os.environ.get('LABCORE_DIR') else gates.load_law()


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def original(name):
    p, pin = ORIG[name]
    p_now = p
    if sha(open(p, 'rb').read()) != pin:                                         # the old file moved on: use its pinned twin
        twins = [os.path.join(os.path.dirname(p), f) for f in os.listdir(os.path.dirname(p)) if f.startswith(os.path.basename(p) + '.pre_')]
        hit = [t for t in twins if sha(open(t, 'rb').read()) == pin]
        if not hit:
            pytest.skip('the pinned original %s %s is gone' % (name, pin))
        p_now = hit[0]
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader('orig_' + name, p_now)        # a twin ends in .pre_<stamp>, not .py
    spec = importlib.util.spec_from_loader('orig_' + name, loader)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(p))
    loader.exec_module(m)
    return m


# ---------------------------------------------------------------- ids
def test_L01_sha16_file_and_text(tmp_path):
    """sha16 = the first 16 hex of sha256: of a file's bytes and of a text's utf-8; the same bytes give the same id either way"""
    for b in (b'', b'abc', 'é news ✓'.encode('utf-8'), bytes(range(256)) * 400):
        p = tmp_path / ('f%d' % len(b))
        p.write_bytes(b)
        assert ids.sha16_file(str(p)) == hashlib.sha256(b).hexdigest()[:16]
    assert ids.sha16_text('é news ✓') == hashlib.sha256('é news ✓'.encode('utf-8')).hexdigest()[:16]
    p = tmp_path / 't'
    p.write_text('é news ✓', encoding='utf-8')
    assert ids.sha16_text('é news ✓') == ids.sha16_file(str(p))


# ---------------------------------------------------------------- settings
def test_L02_load_settings_and_its_sha_refusal(tmp_path):
    """the JSON plus _sha16 and _path; a file whose sha16 differs from want_sha16 is refused; the right one is read"""
    p = tmp_path / 's.json'
    p.write_text(json.dumps({'months': [202510], 'gap_s': 1800}))
    s = settings.load_settings(str(p))
    assert s['gap_s'] == 1800 and s['_sha16'] == ids.sha16_file(str(p)) and s['_path'] == str(p)
    assert settings.load_settings(str(p), want_sha16=s['_sha16'])['gap_s'] == 1800
    with pytest.raises(ValueError):
        settings.load_settings(str(p), want_sha16='0' * 16)


# ---------------------------------------------------------------- gates
def test_L03_load_law_is_THE_law():
    """load_law reads team/LAB3/code/lab3/law.py itself: its answers equal law.py's, and labcore holds no seal date of its own"""
    law = the_law()
    spec = importlib.util.spec_from_file_location('law_direct', LAW)
    direct = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(direct)
    for d in (20250910, 20251231, 20260531, 20260601, 20261023):
        assert law.research_refusal(d) == direct.research_refusal(d)
    assert law.research_refusal(20260601) and not law.research_refusal(20260531)
    for f in os.listdir(PKG_DIR):
        if f.endswith('.py'):
            src = open(os.path.join(PKG_DIR, f)).read()
            assert not re.search(r'2026060[1-9]|RESEARCH_REFUSED\s*=', src), f


def test_L04_month_last_day():
    """the last day of a YYYYMM month (leap years too); months are texts, as in every settings file"""
    assert [int(gates.month_last_day(m)) for m in ('202502', '202402', '202512', '202604', '202601')] == [20250228, 20240229, 20251231, 20260430, 20260131]


def S(**kw):
    s = dict(months=['202510', '202511', '202512', '202601'], outcome_months=['202510', '202511'], fit_months=['202510'], judge_months=['202511'])
    s.update(kw)
    return s


def test_L05_check_window():
    """every settings month readable under law.py (a June 2026 month is refused); outcome, fit and judge months inside months"""
    law = the_law()
    assert gates.check_window(S(), law) is None
    with pytest.raises(ValueError):
        gates.check_window(S(months=['202510', '202511', '202512', '202601', '202606']), law)   # only the June month is wrong
    for k in ('outcome_months', 'fit_months', 'judge_months'):
        with pytest.raises(ValueError):
            gates.check_window(S(**{k: ['202509']}), law)


def ledger(tmp_path, rows):
    p = tmp_path / 'ledger.tsv'
    hdr = 'try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\tresult_sha16\tstatus\n'
    p.write_text('# planted ledger\n' + hdr + ''.join('\t'.join(r) + '\n' for r in rows))
    return str(p)


def test_L06_outcome_allowed(tmp_path):
    """outcomes only for outcome_months; a judge month only with an OLDER PREREG row naming the fit settings sha16"""
    s = S(opens_judge_with=dict(prereg_ask_id='ask-1', fit_sha16='a' * 16))
    with pytest.raises(PermissionError):                                                          # v2: now_utc is required (02-05)
        gates.outcome_allowed(s, ['202510'], ledger=ledger(tmp_path, []))
    assert gates.outcome_allowed(s, ['202510'], ledger=ledger(tmp_path, []), now_utc='20261023T120000Z') is True
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202512'], ledger=ledger(tmp_path, []), now_utc='20261023T120000Z')
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202511'], ledger=ledger(tmp_path, []), now_utc='20261023T120000Z')
    good = ['20261023T100000Z', 'ask-1', 'idea', 'p', 'PREREG', '20251001', '20251130', 'a' * 16, '-', 'OK']
    assert gates.outcome_allowed(s, ['202511'], ledger=ledger(tmp_path, [good]), now_utc='20261023T120000Z') is True
    with pytest.raises(PermissionError):                                                          # the row is not older than now
        gates.outcome_allowed(s, ['202511'], ledger=ledger(tmp_path, [good]), now_utc='20261023T090000Z')
    wrong = list(good); wrong[7] = 'b' * 16
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202511'], ledger=ledger(tmp_path, [wrong]), now_utc='20261023T120000Z')
    run = list(good); run[4] = 'run'
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202511'], ledger=ledger(tmp_path, [run]), now_utc='20261023T120000Z')


# ---------------------------------------------------------------- waves
def test_L07_waves_gap_rule_any_coin_input_order():
    """a fire MORE than gap_s after the previous fire (any coin) starts a new wave; exactly gap_s stays; ids follow the input order"""
    t = np.array([0, 100, 1900, 1901, 3702, 5502.5])          # gaps 100, 1800 (stays), 1, 1801 (new), 1800.5 (new)
    assert list(waves.waves(t, 1800)) == [0, 0, 0, 0, 1, 2]
    rng = np.random.default_rng(7)
    o = rng.permutation(len(t))
    w = waves.waves(t[o], 1800)
    assert list(w) == list(np.array([0, 0, 0, 0, 1, 2])[o])


def test_L08_wave_weights_one_per_wave():
    """1 / (fires of the wave): each wave weighs 1 in total"""
    w = np.array([0, 0, 0, 1, 2, 2])
    ww = waves.wave_weights(w)
    assert np.allclose(ww, [1 / 3, 1 / 3, 1 / 3, 1, 0.5, 0.5])
    assert abs(ww.sum() - 3) < 1e-12


def test_L09_by_wave_mean_of_wave_means():
    """the mean of WAVE means (a wave of 3 fires counts once), NaN rows out, an empty input gives n 0; the 90 pct interval holds the
    mean; the same seed gives the same answer"""
    v = np.array([1.0, 1.0, 1.0, 3.0, np.nan])
    w = np.array([0, 0, 0, 1, 1])
    r = waves.by_wave(v, w, 202510, np.random.default_rng(1), B=500)
    assert (r['n'], r['waves']) == (4, 2) and abs(r['mean'] - 2.0) < 1e-12
    assert r['lo'] <= r['mean'] <= r['hi']
    r2 = waves.by_wave(v, w, 202510, np.random.default_rng(1), B=500)
    assert r == r2
    e = waves.by_wave(np.array([np.nan]), np.array([0]), 202510, np.random.default_rng(1))
    assert e['n'] == 0 and e['waves'] == 0


@pytest.mark.defect
def test_L09b_by_wave_drop_best_is_applied_or_refused():
    """the registry and the docstring say drop_best 'removes the trades of the best days first'; the function takes no day input and
    ignores drop_best (inherited verbatim from money_v1 3bb9bf37). A parameter that is silently ignored is a defect: it must act or
    refuse"""
    v = np.array([5.0, 0.0, 0.0, 0.0]); w = np.array([0, 1, 2, 3])
    a = waves.by_wave(v, w, 202510, np.random.default_rng(1), B=200, drop_best=0)
    try:
        b = waves.by_wave(v, w, 202510, np.random.default_rng(1), B=200, drop_best=1)
    except (ValueError, NotImplementedError, TypeError):
        return
    assert a != b, 'drop_best=1 changed nothing'


# ---------------------------------------------------------------- the move: equal to the pinned originals
def test_L10_equal_to_pinned_originals():
    """each moved function gives the same answer as its pinned original (bucket_proof 2b615f53, money_v1 3bb9bf37) on 200 random plants"""
    bp, mv = original('bucket_proof'), original('money_v1')
    rng = np.random.default_rng(20261023)
    for _ in range(200):
        n = int(rng.integers(1, 60))
        t = np.sort(rng.integers(0, 20000, n)).astype(float)
        rng.shuffle(t)
        g = float(rng.choice([0, 60, 1800, 1800.5]))
        assert list(waves.waves(t, g)) == list(bp.waves(t, g))
        w = waves.waves(t, g)
        assert np.allclose(waves.wave_weights(w), bp.wave_weights(w))
        v = rng.normal(0, 1, n); v[rng.random(n) < 0.1] = np.nan
        a = waves.by_wave(v, w, 202510, np.random.default_rng(5), B=50)
        b = mv.by_wave(v, w, 202510, np.random.default_rng(5), B=50)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    for m in ('202501', '202502', '202402', '202512'):
        assert gates.month_last_day(m) == bp.month_last_day(m)


# ---------------------------------------------------------------- the registry
def test_L11_registry_rows_true():
    """FUNCTIONS_V1.tsv: one row per public function of EVERY labcore module (02-09), module and name right, its sha16 = sha16 of the function's source now"""
    rows = [ln.rstrip('\n').split('\t') for ln in open(os.path.join(PKG_DIR, 'FUNCTIONS_V1.tsv'), encoding='utf-8') if ln.strip() and not ln.startswith('#')]
    hdr, rows = rows[0], rows[1:]
    reg = {r[hdr.index('function')]: (r[hdr.index('module')], r[hdr.index('sha16')]) for r in rows}
    have = {}
    mods = [importlib.import_module(labcore.__name__ + '.' + f[:-3]) for f in sorted(os.listdir(PKG_DIR))
            if f.endswith('.py') and not f.startswith('_')]                     # SKEPTIC 02-09: every module, not the four of step 1
    for m in mods:
        for n, f in inspect.getmembers(m, lambda x: inspect.isfunction(x) or inspect.isclass(x)):
            if f.__module__ == m.__name__ and not n.startswith('_'):
                have[n] = ('labcore.' + m.__name__.split('.')[-1], hashlib.sha256(inspect.getsource(f).encode()).hexdigest()[:16])
    missing = sorted(set(have) - set(reg))                       # defined in labcore, no registry row
    for n, (mod, h) in reg.items():                               # a row names a callable that exists in its module (re-exports allowed)
        m = importlib.import_module(labcore.__name__ + '.' + mod.split('.', 1)[1])
        assert hasattr(m, n), 'registry row %s: no %s in %s' % (n, n, mod)
    wrong = [(n, reg[n], have[n]) for n in set(reg) & set(have) if reg[n] != have[n]]
    assert not missing and not wrong, 'no registry row: %s; module or sha16 not true: %s' % (missing, wrong)


def test_L12_library_writes_no_data():
    """a library: no file is opened for writing anywhere in labcore's modules"""
    for f in os.listdir(PKG_DIR):
        if f.endswith('.py'):
            src = open(os.path.join(PKG_DIR, f)).read()
            assert not re.search(r"open\([^)]*['\"][wax]b?\+?['\"]", src), f


# ---------------------------------------------------------------- SPEED bars (V4.2 0d: timed by the tester)
def best_of(fn, k=3):
    """CPU seconds of the best of k runs (the Mac runs other seats' jobs: wall time on a load of 40 would judge the Mac, not the code)"""
    out = []
    for _ in range(k):
        t0 = time.process_time(); fn(); out.append(time.process_time() - t0)
    return min(out)


def test_L13_speed_bars(tmp_path):
    """SPEED: waves() on 1,000,000 fires under 1 s; by_wave B=1000 on 1,000 waves under 0.5 s; wave_weights on 1,000,000 under 0.5 s;
    sha16_file on 20 MB under 0.5 s (bars set by TEST1, 10x BUILD2's measured times, on a busy Mac under taskpolicy -b)"""
    rng = np.random.default_rng(1)
    t = np.sort(rng.integers(0, 10 ** 9, 1_000_000)).astype(float)
    assert best_of(lambda: waves.waves(t, 1800)) < 1.0
    w = waves.waves(t, 1800)
    assert best_of(lambda: waves.wave_weights(w)) < 0.5
    v = rng.normal(0, 1, 5000); ww = np.repeat(np.arange(1000), 5)
    assert best_of(lambda: waves.by_wave(v, ww, 202510, np.random.default_rng(2), B=1000)) < 0.5
    p = tmp_path / 'big'
    p.write_bytes(os.urandom(20 * 1024 * 1024))
    assert best_of(lambda: ids.sha16_file(str(p))) < 0.5
