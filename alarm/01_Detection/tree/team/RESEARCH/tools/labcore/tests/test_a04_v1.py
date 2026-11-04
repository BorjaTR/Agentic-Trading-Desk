"""test_a04_v1 (BUILD2, 23 Oct 2026; STRATEGY ask 135523): OX-SKEPTIC A04-01 (team/OUTSIDE/SKEPTIC/APPROVAL_labcore_36029bb9.md):
ONE authorization path for a CHECK read. A CHECK read needs the family's one CHECK grant (freeze_judge open, OPENS_V1); a PREREG name or a
local marker never supplies a new family allowance. Each test is one of the reviewer's acceptance cases, with the mutant it kills named.
Run: cd tests; python3 -B -m pytest -q test_a04_v1.py"""
import os, sys
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(TESTS)))
from labcore import gates  # noqa: E402

X, Y = 'abcdabcdabcdabcd', 'eeeeeeeeeeeeeeee'
NOW = '20261023T130000Z'
WINS = [('BUILD', '20250901', '20260228'), ('CHECK', '20260301', '20260531'), ('BLIND', '20260601', None)]


class OpenLaw:
    def research_refusal(self, day):
        return None


def _s(pr, card, oid=None):
    o = {'prereg_ask_id': pr, 'fit_sha16': card}
    if oid:
        o['open_id'] = oid
    return dict(months=['202603'], outcome_months=['202603'], fit_months=[], judge_months=[], opens_judge_with=o)


def _ledger(tmp, rows):
    p = os.path.join(str(tmp), 'L.tsv')
    open(p, 'w').write('try_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\n' + ''.join('\t'.join(r) + '\n' for r in rows))
    return p


def _pre(pr, fam, card):
    return ['20261023T090000Z', pr, fam, 'y', 'PREREG', '20260301', '20260331', card]


def _opens(tmp, rows):
    p = os.path.join(str(tmp), 'OPENS_V1.tsv'); open(p, 'w').write(''.join('\t'.join(r) + '\n' for r in rows))
    return p


def _read(s, L, op=None):
    return gates.outcome_allowed(s, ['202603'], L, NOW, OpenLaw(), WINS, opens=op)


def test_A1_no_grant_refused_and_nothing_written(tmp_path):
    """a valid PREREG with no open_id is refused, and no look marker is created (the PREREG-name fallback is gone).
    Mutant killed: the no-open_id fallback through consume_look."""
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X)])
    with pytest.raises(PermissionError):
        _read(_s('P1', X), L)
    with pytest.raises(PermissionError):
        _read(_s('P1', X), L)
    assert not os.path.exists(os.path.join(str(tmp_path), 'LOOKS_V1'))


def test_A2_two_prereg_names_same_family_no_grant_both_refused(tmp_path):
    """two valid PREREGs of one family, older and with matching hashes, no grant: both refused (a new name is no new allowance)"""
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X), _pre('P2', 'FAM', Y)])
    for pr, card in (('P1', X), ('P2', Y)):
        with pytest.raises(PermissionError):
            _read(_s(pr, card), L)


def test_A3_second_judge_reproduces_under_the_one_grant(tmp_path):
    """the two judges read the same frozen card under the same grant: both allowed (before the RESULT row)"""
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X)])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    assert _read(_s('P1', X, 'O1'), L, op)
    assert _read(_s('P1', X, 'O1'), L, op)


def test_A4_changed_hash_under_the_grant_refused(tmp_path):
    """a renamed or new-version PREREG of the same family with a changed card hash cannot use the family's grant"""
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X), _pre('P2', 'FAM', Y)])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    with pytest.raises(PermissionError):
        _read(_s('P2', Y, 'O1'), L, op)


def test_A5_family_opened_once_a_second_grant_never_authorizes(tmp_path):
    """the family's FIRST CHECK grant is its one allowance: a later CHECK grant for the same family (another card) refuses, whatever its
    PREREG name. Mutant killed: accept any grant row whose open_id matches."""
    L = _ledger(tmp_path, [_pre('P1', 'FAM', X), _pre('P2', 'FAM', Y)])
    op = _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM', 'O1'], ['20261023T110000Z', Y, 'CHECK', 'FAM', 'O2']])
    with pytest.raises(PermissionError):
        _read(_s('P2', Y, 'O2'), L, op)
    assert _read(_s('P1', X, 'O1'), L, op)
    op2 = _opens(tmp_path, [['20261023T110000Z', Y, 'CHECK', 'FAM', 'O2'], ['20261023T100000Z', X, 'CHECK', 'FAM', 'O1']])
    with pytest.raises(PermissionError):                                  # file order never decides: the earliest grant does
        _read(_s('P2', Y, 'O2'), L, op2)


def test_A6_another_familys_grant_and_a_future_grant_refused(tmp_path):
    """a grant of family B never opens family A; a grant stamped after now is no grant"""
    L = _ledger(tmp_path, [_pre('P1', 'FAM_A', X)])
    with pytest.raises(PermissionError):
        _read(_s('P1', X, 'O1'), L, _opens(tmp_path, [['20261023T100000Z', X, 'CHECK', 'FAM_B', 'O1']]))
    with pytest.raises(PermissionError):
        _read(_s('P1', X, 'O1'), L, _opens(tmp_path, [['20261023T140000Z', X, 'CHECK', 'FAM_A', 'O1']]))
