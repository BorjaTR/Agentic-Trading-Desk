"""test_labcore_review02_v1 (TEST1, 23 Oct 2026, PAPER; ASK STRATEGY-125528): one planted case per MUST of SKEPTIC REVIEW 02
(team/RESEARCH/SKEPTIC/REVIEW_02_SHARED_PACKAGE.md 6da3a6fa), written from the review's failure scenarios, black box through labcore's
public calls (briefs._tables is read only to PICK a plant code). Mutants: run_teeth_review02_v1.py (each fix undone on a copy).
  cd team/RESEARCH/tools/labcore/tests && TMPDIR=<SCRATCH>/work_TEST1/tmp /usr/sbin/taskpolicy -b nice -n 10 \\
    <PYTHON> -m pytest -q test_labcore_review02_v1.py         (LABCORE_DIR=<copy> for a planted copy)"""
import importlib, os, sys
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.environ.get('LABCORE_DIR') or os.path.dirname(TESTS)
sys.path.insert(0, os.path.dirname(PKG_DIR))
for k in [k for k in sys.modules if k == 'labcore' or k.startswith('labcore.')]:
    del sys.modules[k]
P = os.path.basename(PKG_DIR)
LA = importlib.import_module(P + '.lookahead')
G = importlib.import_module(P + '.gates')
BR = importlib.import_module(P + '.briefs')
TM = importlib.import_module(P + '.times')
TS = importlib.import_module(P + '.tick_stores')
F = '<LAB_REPO>/forensics'
LAW = os.path.join(F, 'team', 'LAB3', 'code', 'lab3', 'law.py')
I64 = np.int64
REFUSED = (LA.LookaheadError, ValueError, TypeError, PermissionError)
if os.environ.get('LABCORE_DIR'):            # a planted copy lives outside the tree: hand it the tree's own tables (the package's paths)
    _T = os.path.join(F, 'team', 'RESEARCH')
    G.LAW = LAW
    G.WINDOWS = os.path.join(_T, 'tools', 'freeze_judge', 'WINDOWS_V1.tsv')
    BR.MB_PATH = os.path.join(_T, 'LEAD', 'skills', 'reading-metrics', 'scripts', 'metric_brief.py')


def law():
    return G.load_law(LAW)


# ---------------------------------------------------------------- 02-01 cut by availability, not event time
def test_R01_default_cut_by_known_at_and_backstamp_caught():
    """02-01: an event at 5 available at 20 is cut at 10; a function that backstamps its value to the event time is CAUGHT by the prefix
    guard; an input without known_at is refused"""
    data = {'t_us': np.array([5], I64), 'known_at_us': np.array([20], I64), 'v': np.array([1.0])}
    cut = LA.default_cut(data, I64(10))
    assert len(cut['v']) == 0
    backstamp = lambda d: {'known_at_us': np.asarray(d['t_us'], I64), 'v': np.asarray(d['v'], float)}
    assert LA.prefix_check(backstamp, data, I64(10)), 'a backstamped value passed the prefix guard'
    with pytest.raises(REFUSED):
        LA.default_cut({'t_us': np.array([5], I64), 'v': np.array([1.0])}, I64(10))


# ---------------------------------------------------------------- 02-02 invalid times never pass
@pytest.mark.parametrize('k,d', [(np.array([5], I64), np.array([np.nan])), (np.array([-np.inf]), np.array([10], I64)),
                                 (np.array([np.iinfo(np.int64).min], I64), np.array([10], I64)), (np.array([5], np.int32), np.array([10], I64))])
def test_R02_join_guard_refuses_invalid_times(k, d):
    """02-02: NaN decision, -inf known_at, the int64 missing sentinel and a non-int64 clock are refused by the join guard"""
    with pytest.raises(REFUSED):
        LA.join_guard(k, d, 'plant')


def test_R02b_output_nan_known_at_refused_not_dropped():
    """02-02: output rows with NaN known_at must not vanish from both sides of a guard (they are refused)"""
    data = {'known_at_us': np.array([1, 2], I64), 'v': np.array([1.0, 2.0])}
    fn = lambda d: {'known_at_us': np.array([np.nan, 1.0]), 'v': np.array([9.0, 1.0])}
    with pytest.raises(REFUSED):
        LA.prefix_check(fn, data, I64(5))


# ---------------------------------------------------------------- 02-03 frozen baselines
def test_R03_reused_output_buffer_cannot_hide_a_plant():
    """02-03: a function that reuses one output buffer: the planted future value changes it from 99 to 999 and the guard must see it"""
    buf = {'known_at_us': np.array([1], I64), 'v': np.array([99.0])}

    def fn(d):
        buf['v'][0] = 999.0 if (np.asarray(d['known_at_us']) > 100).any() else 99.0
        return buf

    data = {'known_at_us': np.array([1], I64), 'v': np.array([0.0])}
    plant = lambda d, t: {'known_at_us': np.array([1, 200], I64), 'v': np.array([0.0, 5.0])}
    assert LA.future_plant_check(fn, data, plant, I64(50)), 'a reused buffer hid the planted future value'


# ---------------------------------------------------------------- 02-04 one outcome gate, central classes
def S(**kw):
    s = dict(months=['202510', '202511', '202603', '202606'], outcome_months=['202510'], fit_months=['202510'], judge_months=[],
             opens_judge_with={})
    s.update(kw)
    return s


def test_R04_outcome_gate_central_seal_and_classes(tmp_path):
    """02-04: June listed in outcome_months is refused (the seal, here); March (a CHECK month) with no PREREG is refused even when the
    settings leave it out of judge_months; a month in both fit and judge, or a CHECK month in fit, is refused; a BUILD month opens"""
    led = tmp_path / 'l.tsv'
    led.write_text('try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\n')
    now = '20261023T120000Z'
    assert G.outcome_allowed(S(), ['202510'], ledger=str(led), now_utc=now, law=law()) is True
    for s, m in ((S(outcome_months=['202510', '202606']), ['202606']), (S(outcome_months=['202510', '202603']), ['202603']),
                 (S(judge_months=['202510']), ['202510']), (S(fit_months=['202603'], outcome_months=['202603']), ['202603'])):
        with pytest.raises(PermissionError):
            G.outcome_allowed(s, m, ledger=str(led), now_utc=now, law=law())


# ---------------------------------------------------------------- 02-05 now required, one look
class _Law:
    """a planted seal that refuses October 2025 (the gate must ask THE seal itself, not trust the window table alone)"""
    @staticmethod
    def research_refusal(day):
        return 'PLANTED' if str(day).startswith('202510') else None


def test_R04b_gate_asks_the_seal_itself(tmp_path):
    """02-04: a month the seal refuses is refused by outcome_allowed even when the window table calls it BUILD"""
    led = tmp_path / 'l.tsv'
    led.write_text('try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\n')
    with pytest.raises(PermissionError):
        G.outcome_allowed(S(), ['202510'], ledger=str(led), now_utc='20261023T120000Z', law=_Law())


def test_R05_now_required_and_single_look(tmp_path):
    """02-05: now_utc=None is refused; once the PREREG has its RESULT row the month is refused (one look)"""
    s = S(outcome_months=['202603'], judge_months=['202603'], fit_months=['202510'],
          opens_judge_with=dict(prereg_ask_id='ask-9', fit_sha16='f' * 16))
    hdr = 'try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\n'
    pre = '20261023T100000Z\task-9\tidea\tp\tPREREG\t20260301\t20260331\t' + 'f' * 16 + '\n'
    led = tmp_path / 'l.tsv'
    led.write_text(hdr + pre)
    with pytest.raises(PermissionError):
        G.outcome_allowed(s, ['202603'], ledger=str(led), now_utc=None, law=law())
    # the positive path of a CHECK month now also needs a freeze_judge OPENS row (CHECK_WINDOW_RULE_V2, gates.py after 13:2xZ): not
    # planted here; the claims tested are: no read without now, and no second read after the RESULT row
    led.write_text(hdr + pre + '20261023T110000Z\task-9_R\tidea\tp\tRESULT\t20260301\t20260331\t' + 'f' * 16 + '\n')
    with pytest.raises(PermissionError):
        G.outcome_allowed(s, ['202603'], ledger=str(led), now_utc='20261023T120000Z', law=law())


# ---------------------------------------------------------------- 02-06 no 'known by t' without an arrival clock
def test_R06_value_at_needs_an_availability_rule(monkeypatch):
    """02-06: a record stamped 12:00:00 (exchange time) and received later must not be returned for a 12:00:01 decision as 'known';
    value_at must take an explicit availability delay (or refuse decision use). Planted reader, no store read"""
    t0 = 1760097600 * 10 ** 6                                                          # 2025-10-10 12:00:00
    monkeypatch.setattr(TS, 'read_day', lambda *a, **k: (np.array([t0], I64), np.array([1.5]), 'planted'))
    try:
        v = TS.value_at('planted', 'BTC', [t0 / 1e6 + 1], delay_s=2, law=law())
    except TypeError:
        pytest.fail('value_at has no availability delay: exchange time is read as known time (02-06 open)')
    assert np.isnan(v[0])
    assert TS.value_at('planted', 'BTC', [t0 / 1e6 + 3], delay_s=2, law=law())[0] == 1.5


# ---------------------------------------------------------------- 02-07, 02-08 briefs
def _codes():
    T = BR._tables()
    no_row = [c for c in T['cards'] if c not in T['traps']]
    caution = [c for c in T['traps'] if BR.brief(c)['flag'] == 'CAUTION']
    return no_row, caution


def test_R07_no_proof_row_is_unproven_and_refused_in_a_decision():
    """02-07: a metric with no LAB4 proof row briefs UNPROVEN (never OK) and is refused in a decision line"""
    no_row, _ = _codes()
    assert no_row, 'no plant code with a card and no LAB4 row'
    c = no_row[0]
    assert BR.brief(c)['flag'] == 'UNPROVEN'
    with pytest.raises(BR.MetricRefused):
        BR.refuse_inputs([], decision_codes=[c])


def test_R08_decision_codes_generator_read_once():
    """02-08: decision codes given as a generator are checked like a list"""
    _, caution = _codes()
    assert caution
    with pytest.raises(BR.MetricRefused):
        BR.refuse_inputs([], decision_codes=(c for c in caution[:1]))
    with pytest.raises(BR.MetricRefused):
        BR.refuse_inputs([], decision_codes=tuple(caution[:1]))


# ---------------------------------------------------------------- 02-10 (SHOULD) times
def test_R10_check_times_int64_only_no_sentinel():
    """02-10: check_times refuses an int32 clock and the int64 missing-time sentinel"""
    with pytest.raises(ValueError):
        TM.check_times({'as_of_us': np.array([1], np.int32), 'known_at_us': np.array([1], np.int32)})
    with pytest.raises(ValueError):
        TM.check_times({'as_of_us': np.array([1], I64), 'known_at_us': np.array([np.iinfo(np.int64).min], I64)})
    assert TM.check_times({'as_of_us': np.array([1], I64), 'known_at_us': np.array([2], I64)}) is True
