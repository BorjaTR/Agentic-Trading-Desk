"""test_read_outcome_v2 (BUILD2, 23 Oct 2026; QUANT 13:59:25Z FOR BUILD2, STRATEGY-133602): read_outcome uses LABEL_EWSD_V2
(label_ewsd_v2.ewsd_v2 + outcome4_v2) when s['label']['version'] is LABEL_EWSD_V2, with each path's coverage read from the lab PRICE bins
from the FILL time (t_decision + delay_s + fill_wait_s, alarm_stamp's rule); V1 settings keep V1 (no coverage read). The stamp store and
the price cache are planted; the authorization gates are tested elsewhere (test_authorized_v1, labcore tests) and stubbed here.
Mutants killed: coverage from the decision time (no delay or fill wait); V1 label on V2 settings.  Run: python3 -B -m pytest -q test_read_outcome_v2.py"""
import os, sys, types
import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bucket_proof as BP   # noqa: E402

LAB2 = {'version': 'LABEL_EWSD_V2', 'offer_c': 4.0, 'enter_heat_c': 1.0, 'wait_heat_c': 3.0, 'dead_c': 1.5, 'hold_min': 240, 'delay_s': 6,
        'fill_step_s': 3, 'gap_s': 60, 'cost_model': 'T04 table of record (dearer of V1 and V4)', 'cost_sha16': '0' * 16}
LAB1 = {'offer_c': 4.0, 'enter_heat_c': 1.0, 'wait_heat_c': 3.0, 'dead_c': 1.5, 'hold_min': 240}
TA = np.array([1000.0, 2000.0]); WAIT = np.array([2.0, 4.0])                     # the fill waits of the two fires
F = {'month': np.array(['202511', '202511']), 't': TA, 'coin': np.array(['X', 'X']), 'COST:c': np.array([0.1, 0.1])}


def stamp_read(root, code, subject, d, first, last):
    """ride (FOLLOW): offer rungs up to 0.5 pct touched at 100 s, no heat; fade (FADE): nothing touched over the whole hold"""
    OT = np.full((2, 25), np.nan); HT = np.full((2, 25), np.nan)
    if d == 'FOLLOW':
        OT[:, :5] = 100.0
    x = {'coin': F['coin'], 't_alarm': TA, 't_decision': TA.copy(), 'filled': np.ones(2), 'known_s': np.full(2, 14400.0), 'fill_wait_s': WAIT}
    x.update({'ot_%02d' % (k + 1): OT[:, k] for k in range(25)}); x.update({'ht_%02d' % (k + 1): HT[:, k] for k in range(25)})
    return x


class Cache:
    """3 s bars over the whole hold, except the path filled from the first fire stops after 50 s (a hole)"""
    def __init__(self):
        self.t0 = []

    def path(self, coin, t0, t1):
        self.t0.append(t0); stop = t0 + 50_000_000 if t0 < 1_500_000_000 else t1
        te = np.arange(t0 + 3_000_000, stop + 1, 3_000_000, dtype=np.int64); one = np.ones(len(te))
        return {'te_us': te, 'px': one, 'hi': one, 'lo': one}


@pytest.fixture
def bp(monkeypatch):
    monkeypatch.setitem(sys.modules, 'alarm_stamp', types.SimpleNamespace(read=stamp_read))
    monkeypatch.setattr(BP, 'check_authorized', lambda s: True)
    monkeypatch.setattr(BP, 'outcome_allowed', lambda *a, **k: True)
    return BP


def test_v2_label_gap_and_fill_time(bp):
    c = Cache(); s = {'outcome_months': ['202511'], 'subject': 'A02', 'label': dict(LAB2)}
    ride, fade, y, _ = bp.read_outcome(s, F, '/r', '/c', cache=c)
    assert list(ride) == ['UNDECIDED_GAP', 'ENTER']                              # the hole at 50 s comes before the offer at 100 s
    assert list(fade) == ['UNDECIDED_GAP', 'DEAD']                               # DEAD needs the whole hold covered
    assert list(y) == ['UNDECIDED', 'RIDE_GOOD']
    fill = np.round((TA + 6 + WAIT) * 1e6).astype(np.int64)                     # the fill: decision + delay + fill wait
    assert sorted(set(c.t0)) == sorted(fill.tolist())


def test_v2_unfilled_with_empty_length_is_na(bp, monkeypatch):
    """QUANT 14:47:21Z: one unfilled stamp (filled 0, known_s NaN) is NA and never refuses the batch (C12 refuses a NaN length)"""
    def read3(root, code, subject, d, first, last):
        x = stamp_read(root, code, subject, d, first, last); x = dict(x); x['filled'] = np.array([0.0, 1.0]); x['known_s'] = np.array([np.nan, 14400.0])
        return x
    monkeypatch.setitem(sys.modules, 'alarm_stamp', types.SimpleNamespace(read=read3))
    ride, fade, y, _ = bp.read_outcome({'outcome_months': ['202511'], 'subject': 'A02', 'label': dict(LAB2)}, F, '/r', '/c', cache=Cache())
    assert ride[0] == 'NA' and ride[1] == 'ENTER'


def test_v1_settings_keep_v1(bp):
    c = Cache(); s = {'outcome_months': ['202511'], 'subject': 'A02', 'label': dict(LAB1)}
    ride, fade, y, _ = bp.read_outcome(s, F, '/r', '/c', cache=c)
    assert c.t0 == [] and set(ride) <= set(BP.EWSD) and 'UNDECIDED' not in set(y)


def test_v2_settings_incomplete_refused(bp):
    s = {'outcome_months': ['202511'], 'subject': 'A02', 'label': {k: v for k, v in LAB2.items() if k != 'cost_sha16'}}
    with pytest.raises(ValueError):
        bp.read_outcome(s, F, '/r', '/c', cache=Cache())


WINS = [('BUILD', '20250901', '20260228'), ('CHECK', '20260301', '20260531'), ('BLIND', '20260601', None)]


@pytest.mark.parametrize('lab', [LAB2, LAB1])
def test_embargo_horizon_into_another_window(bp, monkeypatch, lab):
    """STRATEGY RULING 14:11:07Z (QUANT MUST, CHECK_WINDOW_RULE_V3 item 8): a fire whose outcome horizon (t + 4 h + 66 s) ends in another
    window is EMBARGO (both sides and the outcome), never scored, counted. 28 Feb 22:00 reaches 1 Mar; 28 Feb 10:00 does not; a fire whose
    horizon ends 1 s before midnight stays. Mutant killed: no embargo."""
    ta = np.array([1772316000.0, 1772272800.0, 1772323200.0 - 14400 - 66 - 1])     # 28 Feb 22:00, 28 Feb 10:00, ends 28 Feb 23:59:59
    f2 = {'month': np.array(['202602'] * 3), 't': ta, 'coin': np.array(['X'] * 3), 'COST:c': np.array([0.1] * 3)}

    def read2(root, code, subject, d, first, last):
        OT = np.full((3, 25), np.nan); HT = np.full((3, 25), np.nan); OT[:, :5] = 100.0 if d == 'FOLLOW' else np.nan
        x = {'coin': f2['coin'], 't_alarm': ta, 't_decision': ta.copy(), 'filled': np.ones(3), 'known_s': np.full(3, 14400.0),
             'fill_wait_s': np.zeros(3)}
        x.update({'ot_%02d' % (k + 1): OT[:, k] for k in range(25)}); x.update({'ht_%02d' % (k + 1): HT[:, k] for k in range(25)})
        return x
    monkeypatch.setitem(sys.modules, 'alarm_stamp', types.SimpleNamespace(read=read2))

    class Full:
        def path(self, coin, t0, t1):
            te = np.arange(t0 + 3_000_000, t1 + 1, 3_000_000, dtype=np.int64); one = np.ones(len(te))
            return {'te_us': te, 'px': one, 'hi': one, 'lo': one}
    s = {'outcome_months': ['202602'], 'subject': 'A02', 'label': dict(lab)}
    ride, fade, y, _ = bp.read_outcome(s, f2, '/r', '/c', cache=Full(), wins=WINS)
    assert list(y) == ['EMBARGO', 'RIDE_GOOD', 'RIDE_GOOD'] and ride[0] == fade[0] == 'EMBARGO'
