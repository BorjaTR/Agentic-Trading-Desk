"""test_skeptic02_v1 (BUILD2, 23 Oct 2026; STRATEGY ask 125528): one regression test per SKEPTIC REVIEW 02 finding fixed in labcore
(team/RESEARCH/SKEPTIC/REVIEW_02_SHARED_PACKAGE.md 6da3a6fa), each the reviewer's synthetic scenario, with the mutant it kills named in
the docstring. It is not TEST1's suite (TEST1 adds its own and the mutant runs); it pins the fixes so they cannot slip back.
02-06 (tick_stores value_at, QUANT's module) is QUANT's to fix and is not tested here.
Run: cd tests; python3 -B -m pytest -q test_skeptic02_v1.py"""
import json, os, sys
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(TESTS)))
from labcore import briefs, gates, lookahead as LA, times  # noqa: E402

I64 = np.int64


def test_S01_default_cut_by_availability_not_event_time():
    """02-01: an event at 5 available at 20 must not survive a cut at 10; a backstamped value fails the prefix check.
    Mutant killed: cut on t_us (event time)."""
    data = {'t_us': np.array([1, 5], I64), 'known_at_us': np.array([1, 20], I64), 'x': np.array([1.0, 7.0])}
    cut = LA.default_cut(data, 10)
    assert list(cut['known_at_us']) == [1]

    def backstamp(d):                                       # reports the late value as known at its event time
        return {'as_of_us': d['t_us'], 'known_at_us': d['t_us'], 'v': d['x']}
    assert LA.prefix_check(backstamp, data, 10)
    with pytest.raises(LA.LookaheadError):
        LA.default_cut({'t_us': np.array([1], I64), 'x': np.array([1.0])}, 10)


def test_S02_invalid_times_never_pass():
    """02-02: NaN known_at in output, NaN decision, -inf known_at, the int64 minimum: each refused. Mutant killed: skip NaN."""
    def nan_out(d):
        return {'known_at_us': np.array([np.nan, 1.0]), 'v': d['x']}
    data = {'known_at_us': np.array([1, 2], I64), 'x': np.array([1.0, 2.0])}
    with pytest.raises(LA.LookaheadError):
        LA.prefix_check(nan_out, data, 5)
    with pytest.raises(LA.LookaheadError):
        LA.join_guard(np.array([1], I64), np.array([np.nan]), 'f')
    with pytest.raises(LA.LookaheadError):
        LA.join_guard(np.array([-np.inf]), np.array([5], I64), 'f')
    with pytest.raises(LA.LookaheadError):
        LA.join_guard(np.array([np.iinfo(I64).min], I64), np.array([5], I64), 'f')
    assert LA.join_guard(np.array([1, 2], I64), np.array([2, 2], I64), 'f')


def test_S03_baseline_frozen_against_reused_buffers():
    """02-03: a function reusing one output buffer; the planted future value changes it 99 -> 999; the plant check must see it.
    Mutant killed: columns() without a copy."""
    buf = np.zeros(2)

    def reuse(d):
        buf[:] = d['x']
        return {'known_at_us': d['known_at_us'], 'v': buf}

    def plant(d, t):
        d = dict(d); x = d['x'].copy(); x[0] = 999.0; d['x'] = x
        return d
    data = {'known_at_us': np.array([1, 2], I64), 'x': np.array([99.0, 1.0])}
    assert LA.future_plant_check(reuse, data, plant, 5)


def _settings(**kw):
    s = dict(months=['202511', '202603'], outcome_months=['202511'], fit_months=['202511'], judge_months=[])
    s.update(kw)
    return s


def _ledger(tmp, rows):
    p = os.path.join(str(tmp), 'L.tsv')
    open(p, 'w').write('try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\n' + ''.join('\t'.join(r) + '\n' for r in rows))
    return p


def test_S04_outcome_gate_uses_law_and_windows(tmp_path):
    """02-04: June listed in outcome_months is refused by law.py inside the gate; March (CHECK) needs a PREREG even when the settings do
    not call it a judge month; a month both fit and judge is refused. Mutant killed: trust the settings' judge_months."""
    now = '20261023T130000Z'
    assert gates.outcome_allowed(_settings(), ['202511'], None, now)
    with pytest.raises(PermissionError):
        gates.outcome_allowed(_settings(months=['202606'], outcome_months=['202606'], fit_months=[]), ['202606'], None, now)
    with pytest.raises(PermissionError):
        gates.outcome_allowed(_settings(outcome_months=['202511', '202603']), ['202603'], None, now)
    with pytest.raises(PermissionError):
        gates.outcome_allowed(_settings(judge_months=['202511']), ['202511'], None, now)


def test_S05_one_look_and_now_required(tmp_path):
    """02-05: now_utc is required; a PREREG that already has its RESULT row cannot open the CHECK months again. Mutant killed: no
    single-look check."""
    s = _settings(outcome_months=['202603'], opens_judge_with={'prereg_ask_id': 'P1', 'fit_sha16': 'abcdabcdabcdabcd'})
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202603'], None, None)
    s['opens_judge_with']['open_id'] = 'O1'
    pre = ['20261023T090000Z', 'P1', 'A02P', 'y', 'PREREG', '20260301', '20260331', 'abcdabcdabcdabcd']   # idea = the open's family (D01b-02)
    op = os.path.join(str(tmp_path), 'OPENS_V1.tsv'); open(op, 'w').write('20261023T100000Z\tabcdabcdabcdabcd\tCHECK\tA02P\tO1\n')
    L = _ledger(tmp_path, [pre])
    assert gates.outcome_allowed(s, ['202603'], L, '20261023T130000Z', opens=op)
    L2 = _ledger(tmp_path, [pre, ['20261023T100000Z', 'P1_R', 'x', 'y', 'RESULT', '', '', 'abcdabcdabcdabcd']])
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202603'], L2, '20261023T130000Z', opens=op)


def test_C2_01_check_read_needs_the_consuming_open(tmp_path):
    """OUTSIDE C2-01: a CHECK read without a freeze_judge open (the consuming grant) is refused, even with a valid PREREG and no RESULT;
    an open for another card or granted after now is refused. Mutant killed: authorize on the PREREG alone."""
    s = _settings(outcome_months=['202603'], opens_judge_with={'prereg_ask_id': 'P1', 'fit_sha16': 'abcdabcdabcdabcd', 'open_id': 'O1'})
    L = _ledger(tmp_path, [['20261023T090000Z', 'P1', 'x', 'y', 'PREREG', '20260301', '20260331', 'abcdabcdabcdabcd']])
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202603'], L, '20261023T130000Z')
    for row in ('20261023T100000Z\teeeeeeeeeeeeeeee\tCHECK\tA02P\tO1\n', '20261023T140000Z\tabcdabcdabcdabcd\tCHECK\tA02P\tO1\n'):
        op = os.path.join(str(tmp_path), 'OPENS_V1.tsv'); open(op, 'w').write(row)
        with pytest.raises(PermissionError):
            gates.outcome_allowed(s, ['202603'], L, '20261023T130000Z', opens=op)


def test_C2_02_prereg_bound_to_its_months(tmp_path):
    """OUTSIDE C2-02: a March PREREG cannot open April by changing outcome_months. Mutant killed: ignore days_from/days_to."""
    s = _settings(months=['202511', '202603', '202604'], outcome_months=['202604'],
                  opens_judge_with={'prereg_ask_id': 'P1', 'fit_sha16': 'abcdabcdabcdabcd', 'open_id': 'O1'})
    L = _ledger(tmp_path, [['20261023T090000Z', 'P1', 'x', 'y', 'PREREG', '20260301', '20260331', 'abcdabcdabcdabcd']])
    op = os.path.join(str(tmp_path), 'OPENS_V1.tsv'); open(op, 'w').write('20261023T100000Z\tabcdabcdabcdabcd\tCHECK\tA02P\tO1\n')
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202604'], L, '20261023T130000Z', opens=op)


def test_C2_04_06_cutoffs_and_float_clocks():
    """OUTSIDE C2-04, C2-06: NaN and -inf cutoffs refused; an integral float clock refused by join_guard"""
    data = {'known_at_us': np.array([1, 2], I64), 'x': np.array([1.0, 2.0])}
    f = lambda d: {'known_at_us': d['known_at_us'], 'v': d['x']}
    for bad in (float('nan'), float('-inf'), 5.0):
        with pytest.raises(LA.LookaheadError):
            LA.prefix_check(f, data, bad)
        with pytest.raises(LA.LookaheadError):
            LA.future_plant_check(f, data, lambda d, t: d, bad)
    with pytest.raises(LA.LookaheadError):
        LA.join_guard(np.array([5.0]), np.array([6], I64), 'f')


def test_S07_unproven_metric_refused_in_a_decision():
    """02-07: a status that is neither flagged nor PROVEN reads UNPROVEN and is refused in a decision line. Mutant killed: empty flag = OK."""
    T = briefs._tables()
    code = next((c for c, r in T['traps'].items() if not T['MB'].flag(r.get('status')) and not (r.get('status') or '').upper().startswith('PROVEN')), None)
    if code is None:
        code = next(c for c in T['cards'] if c not in T['traps'])
    assert briefs.brief(code)['flag'] == 'UNPROVEN'
    with pytest.raises(briefs.MetricRefused):
        briefs.refuse_inputs([], [code])
    assert briefs.brief('A1.S01')['flag'] == 'OK'


def test_S08_generator_decision_codes():
    """02-08: a generator of CAUTION codes is still checked. Mutant killed: list() taken twice."""
    with pytest.raises(briefs.MetricRefused):
        briefs.refuse_inputs(['A1.S01'], (c for c in ['X1.FLOWX.S01']))


def test_S10_times_int64_only():
    """02-10 (SHOULD): int32 and the int64 sentinel are refused"""
    t = np.arange(3, dtype=I64)
    assert times.check_times({'as_of_us': t, 'known_at_us': t})
    with pytest.raises(ValueError):
        times.check_times({'as_of_us': t.astype(np.int32), 'known_at_us': t})
    with pytest.raises(ValueError):
        times.check_times({'as_of_us': t, 'known_at_us': np.array([0, 1, np.iinfo(I64).min], I64)})


def test_D01b_02_grant_bound_to_the_prereg_family(tmp_path):
    """OUTSIDE D01b-02: a FAMILY_B open with the same card hash never authorizes a FAMILY_A PREREG. Mutant killed: drop the family match."""
    s = _settings(outcome_months=['202603'], opens_judge_with={'prereg_ask_id': 'P1', 'fit_sha16': 'abcdabcdabcdabcd', 'open_id': 'O1'})
    L = _ledger(tmp_path, [['20261023T090000Z', 'P1', 'FAMILY_A', 'y', 'PREREG', '20260301', '20260331', 'abcdabcdabcdabcd']])
    op = os.path.join(str(tmp_path), 'OPENS_V1.tsv'); open(op, 'w').write('20261023T100000Z\tabcdabcdabcdabcd\tCHECK\tFAMILY_B\tO1\n')
    with pytest.raises(PermissionError):
        gates.outcome_allowed(s, ['202603'], L, '20261023T130000Z', opens=op)
    open(op, 'w').write('20261023T100000Z\tabcdabcdabcdabcd\tCHECK\tFAMILY_A\tO1\n')
    assert gates.outcome_allowed(s, ['202603'], L, '20261023T130000Z', opens=op)


def test_D01b_03_cutoff_inside_int64():
    """OUTSIDE D01b-03: 2**64 and -2**63 are refused as cutoffs"""
    data = {'known_at_us': np.array([1, 2], I64), 'x': np.array([1.0, 2.0])}
    f = lambda d: {'known_at_us': d['known_at_us'], 'v': d['x']}
    for bad in (2 ** 64, -2 ** 63, 2 ** 63):
        with pytest.raises(LA.LookaheadError):
            LA.prefix_check(f, data, bad)
