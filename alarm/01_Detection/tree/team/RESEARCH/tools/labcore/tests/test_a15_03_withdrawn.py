"""test_a15_03_withdrawn (LAB1, 23 Oct 2026; OUTSIDE OX-SKEPTIC A15-03): a withdrawn registration never authorizes a read, even with its
grant. Lands in labcore/tests with RELEASE_labcore_V2_2 (staged gates.py beside it). Uses test_a04_v1's planted ledger and grant.
Mutant killed: the gate without the WITHDRAWN check (the A3 grant read returns True)."""
import os, sys
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE))); sys.path.insert(0, HERE)
from labcore import gates  # noqa: E402
from test_a04_v1 import X, _ledger, _pre, _opens, _read, _s  # noqa: E402


def test_withdrawn_with_grant_refused(tmp_path):
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X), ['20261023T093000Z', 'P1_W', 'FAM', 'stopped', 'WITHDRAWN', '20260301', '20260331', X]])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    with pytest.raises(PermissionError, match='WITHDRAWN'):
        _read(_s('P1', X, 'O1'), L, op)


def test_same_grant_without_withdrawal_still_reads(tmp_path):
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X)])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    assert _read(_s('P1', X, 'O1'), L, op)


def test_another_tries_withdrawal_does_not_block(tmp_path):
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X), ['20261023T093000Z', 'P9_W', 'FAM', 'stopped', 'WITHDRAWN', '20260301', '20260331', X]])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    assert _read(_s('P1', X, 'O1'), L, op)
