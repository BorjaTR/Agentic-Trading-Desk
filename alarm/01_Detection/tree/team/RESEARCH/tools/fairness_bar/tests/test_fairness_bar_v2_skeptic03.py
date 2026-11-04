"""test_fairness_bar_v2_skeptic03 (BUILD2, 23 Oct 2026; ASK STRATEGY-130408): one planted test per SKEPTIC REVIEW 03 item fixed in
fairness_bar_v2.py by README V1.5 section 1h, the mutant each kills named in the docstring. TEST1 writes the suite of record; this pins the
fixes. Planted ledgers and receipts only (no real ledger read).
Run: cd tests; python3 -B -m pytest -q test_fairness_bar_v2_skeptic03.py"""
import datetime as dt, os, sys
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__)); HOME = os.path.dirname(TESTS)
sys.path.insert(0, HOME)
import fairness_bar_v2 as F2      # noqa: E402

FAST = dict(flips=300, day_boot=300)


def tr(t, text, ask, source='ledger', status='OK'):
    return dict(try_utc=t, text=text, source=source, status=status, ask_id=ask)


def receipt(tmp, name, values, start=1760000000, gap=4000, days=None, fires_per=1):
    lines = ['# wave_module_sha16=%s' % F2.ids.sha16_file(F2.os.path.join(F2.TOOLS, 'labcore', 'waves.py')), 'wave_id\tvalue\tmonth\tday\tn_fires\tfires']
    on_day = {}
    for i, v in enumerate(values):                           # D11-02: a wave's day and month ARE its first fire's UTC date
        if days is not None:                                 # waves of one day 2000 s apart (over the 1800 s wave gap), in order
            k = on_day[days[i]] = on_day.get(days[i], -1) + 1
            t0 = int(dt.datetime.strptime(days[i], '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()) + 2000 * k
        else:
            t0 = start + i * gap
        f = ';'.join('C%d@%d' % (k, t0 + 10 * k) for k in range(fires_per))
        d = dt.datetime.fromtimestamp(t0, dt.timezone.utc).strftime('%Y%m%d')
        lines.append('w%d\t%s\t%s\t%s\t%d\t%s' % (i, 'nan' if v is None else '%.6f' % v, d[:6], d, fires_per, f))
    p = os.path.join(str(tmp), name); open(p, 'w').write('\n'.join(lines) + '\n'); return p


def ledger(extra=()):
    return [tr('20261023T090000Z', 'PREREG A02P money block', 'P1')] + list(extra)


def test_T10_case_insensitive_and_unmapped_incomplete(tmp_path):
    """03-10: a lower-case 'a02p' try counts in A02P; an UNMAPPED try makes the verdict INCOMPLETE. Mutants killed: case-sensitive
    classifier; UNMAPPED ignored."""
    rng = np.random.default_rng(1); p = receipt(tmp_path, 'r.tsv', rng.normal(1.0, 1, 60))
    r = F2.bar(p, 'P1', FAST, tries=ledger([tr('20261023T080000Z', 'old a02p idea', 'X1')]))
    assert r['tries_counted'] == 2 and r['verdict'] != 'INCOMPLETE'
    r = F2.bar(p, 'P1', FAST, tries=ledger([tr('20261023T080000Z', 'zebra crossing', 'X2')]))
    assert r['verdict'] == 'INCOMPLETE' and r['unmapped'] == 1


def test_T11_waves_recounted_from_fires(tmp_path):
    """03-11: one wave's value pasted under many wave ids (fires 1 s apart) is refused by the recount; a fire in two waves is refused.
    Mutant killed: trust the receipt's wave ids."""
    p = receipt(tmp_path, 'dup.tsv', [0.5] * 20, gap=1)
    with pytest.raises(ValueError):
        F2.bar(p, 'P1', FAST, tries=ledger())
    q = os.path.join(str(tmp_path), 'two.tsv')
    open(q, 'w').write('# wave_module_sha16=%s\n' % F2.ids.sha16_file(F2.os.path.join(F2.TOOLS, 'labcore', 'waves.py')) + 'wave_id\tvalue\tmonth\tday\tn_fires\tfires\nw0\t1\t202510\t20251001\t1\tA@100\nw1\t1\t202510\t20251001\t1\tA@100\n')
    with pytest.raises(ValueError):
        F2.read_receipt(q)


def test_T12_multiplicity_never_optional(tmp_path):
    """03-12: with 50 counted tries and no roster the result's p is Bonferroni x 50, printed. Mutant killed: holm on the result alone."""
    rng = np.random.default_rng(2); p = receipt(tmp_path, 'r.tsv', rng.normal(0.4, 1, 40))
    many = [tr('20261023T08%02d00Z' % i, 'A02P variant %d' % i, 'V%d' % i) for i in range(49)]
    r = F2.bar(p, 'P1', FAST, tries=ledger(many))
    assert r['tries_counted'] == 50 and r['multiplicity'].startswith('BONFERRONI')
    assert abs(r['adj_p'] - min(1.0, r['p_used'] * 50)) < 1e-12


def test_T13_opposites_are_two_choices(tmp_path):
    """03-13: x and -x as two tries give a higher luck bar than x alone (two choices, not one). Mutant killed: eigenvalue N_eff."""
    rng = np.random.default_rng(3); x = rng.normal(0, 1, 60)
    a = receipt(tmp_path, 'x.tsv', x); b = receipt(tmp_path, 'mx.tsv', -x)
    one = F2.bar(a, 'P1', FAST, tries=ledger())
    two = F2.bar(a, 'P1', FAST, tries=ledger([tr('20261023T080000Z', 'A02P short side', 'S1')]), roster={'S1': b})
    assert two['sr_star_flips'] > one['sr_star_flips'] + 0.02


def test_T14_unresolved_counted_never_dropped(tmp_path):
    """03-14: 10 pct of waves without a value -> INCOMPLETE, counted; the worst-case rerun printed. Mutant killed: drop NaN waves."""
    rng = np.random.default_rng(4); v = list(rng.normal(1.0, 1, 50)); v[::10] = [None] * 5
    r = F2.bar(receipt(tmp_path, 'r.tsv', v), 'P1', FAST, tries=ledger())
    assert r['unresolved_waves'] == 5 and r['eligible_waves'] == 50 and r['verdict'] == 'INCOMPLETE' and 'worst-case' in r['line']


def test_T18_modes_from_ledger_not_caller(tmp_path):
    """03-18: tries after the PREREG count in CURRENT, not AT_REGISTRATION; no caller time. Mutant killed: count only up to the PREREG."""
    rng = np.random.default_rng(5); p = receipt(tmp_path, 'r.tsv', rng.normal(0.8, 1, 40))
    r = F2.bar(p, 'P1', FAST, tries=ledger([tr('20261023T100000Z', 'A02P later batch', 'L1')]))
    assert r['tries_counted'] == 2 and r['tries_at_registration'] == 0 and r['mode'] == 'CURRENT'


def test_T19_persistent_waves_use_day_blocks(tmp_path):
    """03-19: many waves on few days with a shared day effect: the day-block t is smaller than the iid t and is used. Mutant killed: iid t."""
    rng = np.random.default_rng(6); days = ['202510%02d' % (1 + i // 10) for i in range(60)]
    eff = {d: rng.normal(0.5, 1.5) for d in set(days)}; v = [eff[d] + rng.normal(0, 0.2) for d in days]
    r = F2.bar(receipt(tmp_path, 'r.tsv', v, days=days), 'P1', FAST, tries=ledger())
    assert r['t_day_block'] < r['t_iid'] and r['t_used'] == min(r['t_iid'], r['t_wave_boot'], r['t_day_block'])
