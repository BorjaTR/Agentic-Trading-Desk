"""TEST2 tests for exit_engine README V2.5 section 2b (OX-SKEPTIC A02 evidence rules, owner rulings; STRATEGY-134431, BUILD1-135345;
23 Oct 2026): path_evidence_status per trade, the census with its shares and the 5 pct line, and the call boundary (run_frozen /
simulate(frozen=)). Engine only (the oracle has no evidence rules). Mutants on patched temp copies: run_teeth_exit_v25.py.
Run: EXIT_ENGINE=<module> (default ../exit_engine_v1.py) pytest -q test_exit_engine_v25.py."""
import os, shutil, sys, tempfile
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import engine_iface_v1 as E
from labcore import ids

COSTS = os.path.join(E.FORENSICS, 'team', 'RESEARCH', 'QUANT', 'receipts', 'COSTS_PER_COIN_V1.tsv')


def eng():
    return E.engine()


def flat(n, p=1.0):
    return np.full(n, p), np.full(n, p), np.full(n, p)


def run(c, h, l, row, e=(0,), **kw):
    return eng().simulate(c, h, l, list(e), [c[x] for x in e], [1] * len(e), row, **kw)


ROW = dict(id='PLANT', kind='B', unit='pct', stop=40, take=50, arm=None, give=None, time_limit_min=3, min_hold_min=None, early_stop=None,
           early_min=None, monitor='none', note='planted by TEST2')


# ---------------------------------------------------------------- path_evidence_status
def test_hole_then_take_is_path_uncertain():
    c, h, l = flat(100); c[3:5] = h[3:5] = l[3:5] = np.nan; h[8] = 1.6
    o = run(c, h, l, ROW)
    assert o['booking_status'][0] == 'TAKE' and o['path_evidence_status'][0] == 'PATH_UNCERTAIN'


def test_no_hole_is_clean_and_time_only_hole_is_clean():
    c, h, l = flat(100); h[8] = 1.6
    assert run(c, h, l, ROW)['path_evidence_status'][0] == 'CLEAN'
    c, h, l = flat(100); c[3:5] = h[3:5] = l[3:5] = np.nan
    o = run(c, h, l, dict(ROW, stop=None, take=None))                                     # no level can be crossed in a hole
    assert o['booking_status'][0] == 'TIME' and o['hole_bars'][0] == 2 and o['path_evidence_status'][0] == 'CLEAN'


def test_noprice_is_unresolved():
    c, h, l = flat(30)
    o = run(c, h, l, ROW)
    assert o['booking_status'][0] == 'NOPRICE' and o['path_evidence_status'][0] == 'UNRESOLVED'


# ---------------------------------------------------------------- census: every trade counted, shares, incomplete > 5 pct
@pytest.mark.parametrize('n_hole, n_nop, incomplete', [(1, 0, False), (2, 0, True), (0, 1, False), (1, 1, True)])
def test_census_counts_every_trade(n_hole, n_nop, incomplete):
    c, h, l = flat(400); c[50:52] = h[50:52] = l[50:52] = np.nan          # a hole inside holds that start at 40..49
    e = [100 + 3 * i for i in range(20 - n_hole - n_nop)] + [40 + i for i in range(n_hole)] + [395 - i for i in range(n_nop)]
    o = run(c, h, l, ROW, e=e)
    cs = eng().census(o)
    assert cs['trades'] == 20 and cs['path_uncertain'] == n_hole and cs['noprice'] == n_nop and cs['clean'] == 20 - n_hole - n_nop
    assert abs(cs['path_uncertain_share'] - n_hole / 20) < 1e-12 and abs(cs['noprice_share'] - n_nop / 20) < 1e-12
    assert cs['incomplete'] is incomplete


# ---------------------------------------------------------------- the call boundary (frozen manifest)
@pytest.fixture
def frozen():
    d = tempfile.mkdtemp(prefix='test2_exit25_')
    ex = os.path.join(d, 'EXITS_V1.tsv'); shutil.copy(os.path.join(E.TOOL, 'EXITS_V1.tsv'), ex)
    ct = os.path.join(d, 'COSTS.tsv'); shutil.copy(COSTS, ct)
    import labcore.costs, labcore.ids, labcore.lookahead, labcore.prices
    deps = {os.path.realpath(m.__file__): ids.sha16_file(os.path.realpath(m.__file__))
            for m in (labcore.costs, labcore.ids, labcore.lookahead, labcore.prices)}
    hdr = next(l.rstrip('\n') for l in open(ex, encoding='utf-8') if not l.startswith('#'))
    return dict(exits_path=ex, exit_row_sha16=eng().row_sha16(ex, 'EXIT_T1'), exits_schema_sha16=ids.sha16_text(hdr), cost_table=ct, cost_sha16=ids.sha16_file(ct),
                module_sha16=ids.sha16_file(E.engine_path()), dependency_sha16=deps)


def go(fz, row=None, **kw):
    row = row if row is not None else eng().load_exits(fz['exits_path'])['EXIT_T1']
    c, h, l = flat(4000, 100.0)
    return eng().run_frozen(c, h, l, [0], [100.0], [1], row, fz, units={'nm': np.array([0.5]), 'known_at_us': np.array([0])}, **kw)


def test_run_frozen_accepts_the_frozen_release(frozen):
    assert go(frozen)['booking_status'][0] == 'TIME'


def test_run_frozen_refuses_a_row_edited_in_memory(frozen):
    row = dict(eng().load_exits(frozen['exits_path'])['EXIT_T1'], stop=2.0)
    with pytest.raises(ValueError):
        go(frozen, row=row)


def test_run_frozen_refuses_a_row_edited_in_the_registry(frozen):
    t = open(frozen['exits_path']).read().replace('EXIT_T1\tT\tnm\t3\t', 'EXIT_T1\tT\tnm\t4\t'); open(frozen['exits_path'], 'w').write(t)
    with pytest.raises(ValueError):
        go(frozen)


@pytest.mark.parametrize('key', ['module_sha16', 'cost_sha16'])
def test_run_frozen_refuses_a_wrong_sha16(frozen, key):
    with pytest.raises(ValueError):
        go(dict(frozen, **{key: '0123456789abcdef'}))


def test_run_frozen_refuses_a_missing_manifest_or_inventory(frozen):
    with pytest.raises(ValueError):
        go(None, row=eng().load_exits(frozen['exits_path'])['EXIT_T1'])
    with pytest.raises(ValueError):
        go({k: v for k, v in frozen.items() if k != 'dependency_sha16'})
    with pytest.raises(ValueError):
        go(dict(frozen, dependency_sha16=dict(list(frozen['dependency_sha16'].items())[1:])))      # one labcore module left out


def test_run_frozen_refuses_a_changed_dependency(frozen):
    p = next(iter(frozen['dependency_sha16']))
    with pytest.raises(ValueError):
        go(dict(frozen, dependency_sha16=dict(frozen['dependency_sha16'], **{p: '0123456789abcdef'})))


# ---------------------------------------------------------------- OX-SKEPTIC A06 (STRATEGY-155031a)
def test_a06_01_monitor_exit_after_missing_bars_is_uncertain():
    """a monitor-only row (no level) whose k+1 bar is missing books later: delayed by an unobserved fill bar, never CLEAN"""
    c, h, l = flat(100); c[26:29] = h[26:29] = l[26:29] = np.nan
    r = dict(ROW, stop=None, take=None, monitor='caller')
    o = eng().simulate(c, h, l, [0], [1.0], [1], r, monitor=[25])
    assert o['booking_status'][0] == 'MONITOR' and o['gap_len_bars'][0] == 3 and o['path_evidence_status'][0] == 'PATH_UNCERTAIN'
    c, h, l = flat(100)
    o = eng().simulate(c, h, l, [0], [1.0], [1], r, monitor=[25])                      # no hole: CLEAN
    assert o['booking_status'][0] == 'MONITOR' and o['path_evidence_status'][0] == 'CLEAN'


def test_a06_03_registry_header_is_pinned(frozen):
    """a column added to the registry header only (EXIT_T1's row text and parsed values unchanged) refuses at the boundary"""
    lines = open(frozen['exits_path']).read().split('\n')
    k = next(i for i, l in enumerate(lines) if l and not l.startswith('#'))
    lines[k] += '\textra_col'; open(frozen['exits_path'], 'w').write('\n'.join(lines))
    assert eng().row_sha16(frozen['exits_path'], 'EXIT_T1') == frozen['exit_row_sha16']
    with pytest.raises(ValueError):
        go(frozen, row=dict(eng().load_exits(os.path.join(E.TOOL, 'EXITS_V1.tsv'))['EXIT_T1']))
