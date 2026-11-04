"""planted tests for event_outcomes (STRATEGY/LEAD, 25 Oct 2026). python3 -m pytest -q test_event_outcomes.py
VERSION 3 (A51 successor): the nine original tests, unchanged except that the two which load a settings file load OUTCOMES_CORE_V3.json
(V1 is refused by VERSION 3: its MONEY_T1 is the retired static-cost kind 'money'; the assertions are the original ones)."""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import event_outcomes as EO


def path(n=2000, p0=100.0):
    c = np.full(n, p0); return c, c.copy(), c.copy()


def lab(kind, **k):
    return dict(name='X', kind=kind, unit='pct', **k)


def test_return_best_worst_exact():
    c, h, l = path()
    h[10] = 102.0; l[30] = 99.0; c[200] = 101.0          # bar e+10 high +2 pct, e+30 low -1 pct, close at 10 min (200 bars) +1 pct
    e = 0
    assert abs(EO.label_path(lab('return', horizon_min=10), c, h, l, e, 100.0, 1, 1.0)[0] - 1.0) < 1e-12
    assert abs(EO.label_path(lab('return', horizon_min=10), c, h, l, e, 100.0, -1, 1.0)[0] + 1.0) < 1e-12    # short: the mirror
    assert abs(EO.label_path(lab('best', horizon_min=10), c, h, l, e, 100.0, 1, 1.0)[0] - 2.0) < 1e-12
    assert abs(EO.label_path(lab('worst', horizon_min=10), c, h, l, e, 100.0, 1, 1.0)[0] - 1.0) < 1e-12
    assert abs(EO.label_path(lab('best', horizon_min=10), c, h, l, e, 100.0, -1, 1.0)[0] - 1.0) < 1e-12     # short: low -1 is +1
    assert abs(EO.label_path(lab('return', horizon_min=10), c, h, l, e, 100.0, 1, 0.5)[0] - 2.0) < 1e-12    # unit c = 0.5 pct: 2 c


def test_reach_first_heat_before_and_time():
    c, h, l = path()
    l[5] = 99.4; h[20] = 101.0; l[25] = 98.0
    v, t, _ = EO.label_path(lab('reach', target=1.0, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)
    assert v == 1.0 and t == 60                                       # bar e+20 = 20 x 3 s
    assert EO.label_path(lab('reach', target=1.5, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[0] == 0.0
    v, t, _ = EO.label_path(lab('heat_before', target=1.0, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)
    assert abs(v - 0.6) < 1e-9 and t == 60                            # the -0.6 pct at e+5 came before the +1 pct
    assert EO.label_path(lab('first', up=1.0, down=0.5, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[0] == -1.0   # -0.6 first
    assert EO.label_path(lab('first', up=1.0, down=0.7, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[0] == 1.0
    h2 = h.copy(); l2 = l.copy(); h2[3] = 101.0; l2[3] = 99.0          # one bar touching both: adverse first
    assert EO.label_path(lab('first', up=1.0, down=1.0, horizon_min=5), c, h2, l2, 0, 100.0, 1, 1.0)[0] == -1.0


def test_no_trade_bars_are_not_holes_but_long_gaps_are():
    c, h, l = path()
    for a in (c, h, l):
        a[40:50] = np.nan                                             # 30 s without a trade: fine
    assert np.isfinite(EO.label_path(lab('best', horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[0])
    for a in (c, h, l):
        a[40:70] = np.nan                                             # 90 s missing: a hole
    v, _, why = EO.label_path(lab('best', horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)
    assert np.isnan(v) and why == 'PATH_GAP'
    h[10] = 102.0                                                     # reached BEFORE the hole: still decided
    assert EO.label_path(lab('reach', target=1.0, horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[0] == 1.0


def test_nothing_after_the_window_counts():
    c, h, l = path()
    a = EO.label_path(lab('best', horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)
    h[101:] = 1e6; l[101:] = 1e-6; c[101:] = 5.0                       # everything after 5 min (100 bars) planted huge
    b = EO.label_path(lab('best', horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)
    assert a == b


def test_short_path_is_no_path():
    c, h, l = path(50)
    assert EO.label_path(lab('return', horizon_min=5), c, h, l, 0, 100.0, 1, 1.0)[2] == 'NO_PATH'


def test_exit_label_is_the_exit_engine(tmp_path):
    """the exit label calls exit_engine.simulate unchanged: a planted trail exit books what the engine books"""
    s = EO.load_settings(os.path.join(HERE, 'OUTCOMES_CORE_V3.json')); row = s['_exits']['EXIT_T1']
    c, h, l = path(4000); c[100:] = 103.0; h[100:] = 103.0; l[100:] = 103.0; c[300:] = 101.0; h[300:] = 101.0; l[300:] = 101.0
    o = EO.XE.simulate(c, h, l, [0], [100.0], [1], row, units={'known_at_us': np.array([0], np.int64), 'nm': np.array([1.0])}, t0_us=0)
    assert str(o['kind'][0]) == 'trail' and abs(float(o['ret_pct'][0]) - 1.0) < 1e-9


def test_settings_add_a_label_is_one_line(tmp_path):
    s = json.load(open(os.path.join(HERE, 'OUTCOMES_CORE_V3.json')))
    s['labels'].append({'name': 'RET_2M', 'kind': 'return', 'horizon_min': 2, 'unit': 'pct'})
    p = tmp_path / 's.json'; p.write_text(json.dumps(s)); t = EO.load_settings(str(p))
    assert 'RET_2M__FADE' in [c for c, _, _ in EO.columns(t)]
    s['labels'].append({'name': 'BAD', 'kind': 'reach', 'horizon_min': 5})           # a reach without its target: refused
    p.write_text(json.dumps(s))
    import pytest
    with pytest.raises(ValueError):
        EO.load_settings(str(p))


def test_offer_before_heat_any_numbers():
    """the owner's label: any offer, any heat, any time; equal to the triple barrier with up = offer, down = heat"""
    c, h, l = path(6100)
    l[50] = 99.5; h[80] = 101.0; h[5000] = 103.0
    for H, want in ((2, 0.0), (5, 1.0)):                               # within 2 min nothing; within 5 min the +1 offer came before -1 heat
        a = EO.label_path(dict(name='X', kind='offer_before_heat', offer=1.0, heat=1.0, horizon_min=H, unit='pct'), c, h, l, 0, 100.0, 1, 1.0)
        b = EO.label_path(dict(name='X', kind='first', up=1.0, down=1.0, horizon_min=H, unit='pct'), c, h, l, 0, 100.0, 1, 1.0)
        assert a == b and a[0] == want
    assert EO.label_path(dict(name='X', kind='offer_before_heat', offer=1.0, heat=0.4, horizon_min=5, unit='pct'), c, h, l, 0, 100.0, 1, 1.0)[0] == -1.0
    assert EO.label_path(dict(name='X', kind='offer_before_heat', offer=3.0, heat=2.0, horizon_min=300, unit='pct'), c, h, l, 0, 100.0, 1, 1.0)[0] == 1.0


def test_any_date_range_accepted():
    """no date guard in the tool: the range is the caller's (the lab3 reader's law applies underneath)"""
    assert not hasattr(EO, 'outcome_months_ok')
