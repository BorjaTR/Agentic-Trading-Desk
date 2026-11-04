"""tests of labcore.v2_7.quality (LAB1, 25 Oct 2026, item 7): each rule alone makes a cell unknown; the ABSENT reason byte beside a
finite value is unknown (the detect/Cause disagreement settled strict); counts names the first failing rule once; shapes must agree."""
import os, sys
import numpy as np
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from labcore.v2_7 import quality as Q

M = np.iinfo(np.int64).min


def base():
    v = np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]])
    e = np.zeros((1, 6), np.uint8); a = np.zeros((1, 6), np.int32); o = np.zeros((1, 6), np.int64)
    k = np.array([[0, 5, 10, 15, 20, 25]], np.int64); col = np.array([0, 5, 10, 15, 20, 25], np.int64)
    return v, e, a, o, k, col


def test_Q1_all_known():
    v, e, a, o, k, col = base()
    assert Q.known(v, e, a, o, k, col).all()


def test_Q2_each_rule_alone():
    v, e, a, o, k, col = base()
    v[0, 0] = np.nan; e[0, 1] = 3; a[0, 2] = -1; o[0, 3] = -1; k[0, 4] = M; k[0, 5] = 26
    assert Q.known(v, e, a, o, k, col).tolist() == [[False] * 6]
    c = Q.counts(v, e, a, o, k, col)
    assert c == {'cells': 6, 'nonfinite': 1, 'reason': 1, 'age': 1, 'offset': 1, 'late': 2, 'known': 0}


def test_Q3_absent_reason_beside_a_value_is_unknown():
    v, e, a, o, k, col = base(); e[0, 2] = 255
    assert Q.known(v, e)[0].tolist() == [True, True, False, True, True, True]


def test_Q4_fields_not_listed_are_not_checked():
    v = np.array([1.0, np.inf, 2.0])
    assert Q.known(v).tolist() == [True, False, True]


def test_Q5_first_rule_counted_once():
    v, e, a, o, k, col = base(); v[0, 0] = np.nan; e[0, 0] = 7; a[0, 0] = -1
    c = Q.counts(v, e, a, o, k, col)
    assert c['nonfinite'] == 1 and c['reason'] == 0 and c['age'] == 0 and c['known'] == 5


def test_Q6_refusals():
    v, e, a, o, k, col = base()
    with pytest.raises(ValueError):
        Q.known(v, k=k)
    with pytest.raises(ValueError):
        Q.known(v, e=e[:, :3])
