"""test_costs_v3 (BUILD2, 23 Oct 2026; T04, STRATEGY-143903 and review 14:41:52Z; design tools/costs_v2/README.md 236897024fefcf39 sec 6):
the tests of labcore.costs V3, written BEFORE the code. Planted inputs only (seconds); C9 (the funding tie with q_471169 on the real
download) is the build job's real-data test and skips here when the store is absent. README 069a8e993ea449cb adds C11 and C12.
Interface the build must offer (builder's choice, named here so the tests can run; module functions delegate to one default instance):
  costs.make_record(v1_path, v4_path) -> (rows, header): rows {(coin, hour): (book_bp, source)} = the DEARER of V1 and V4 (cost_bp - fee)
  costs.Costs(settings, record=rows, funding=read(coin, 'YYYYMM') -> [(time_ms, rate, premium)], xcost=read(coin, t_us, purpose) -> dict
              (default: lab3.days with the CALLER's purpose, lab_root=), recorder=read(coin, 'YYYYMM') for source='recorder')
    .cost_at(coin, t_us, purpose)  .cost_fire(coin, t_us, purpose)  .funding_paid(coin, side, t_in_us, t_out_us, source='stored')
    .trade_cost(coin, side, t_in_us, t_out_us, size_usd)  .gap_bp(priced_on)
Every cost part is positive when the trader PAYS (STRATEGY M1). Values in bp of the entry notional.
Run: python3 -B -m pytest -q test_costs_v3.py"""
import os, sys
import numpy as np
import pytest

TOOLS = '<LAB_REPO>/forensics/team/RESEARCH/tools'
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import costs_v3 as costs  # noqa: E402  (the landed tool: tools/costs_v2/costs_v3.py)
from labcore import lookahead  # noqa: E402

S = {'fee_side_pct': 0.045, 'gap_leg_pct': 0.072, 'size_usd': 10000, 'stress': [1.5, 2], 'priced_on': 'binance'}
US, H_US = 1_000_000, 3_600_000_000
T0 = 1760313600 * US                                            # 2025-10-13 00:00:00 UTC


def tables(tmp, v1, v4):
    a = tmp / 'V1.tsv'; a.write_text('# planted V1\ncoin\tbinance_walk10k_rt_bp\thl_walk10k_rt_bp\tfee_bp\tcost_bp\tsource\tgroup\n'
                                     + ''.join('%s\t0\t0\t9.000\t%.3f\tHL\tmiddle\n' % r for r in v1))
    b = tmp / 'V4.tsv'; b.write_text('# planted V4\ncoin\thour_utc\tcost_bp\tgroup\tratio\tfilled\n'
                                     + ''.join('%s\t%d\t%.3f\tcheap\t1\t0\n' % r for r in v4))
    return str(a), str(b)


def record(tmp):
    """AAA: V1 20 bp, V4 25 bp at hour 0 and 15 bp at hour 23 (the dearer: 16 at 0, 11 at 23); BBB in V4 only (refused)"""
    v1, v4 = tables(tmp, [('AAA', 20.0)], [('AAA', 0, 25.0), ('AAA', 23, 15.0), ('BBB', 0, 30.0)])
    return costs.make_record(v1, v4)[0]


def funding_of(rates):
    """rates {(coin, hour index from T0): rate}; a missing hour is absent from the month"""
    def read(coin, month):
        return sorted(((T0 // 1000 + h * 3_600_000), r, None) for (c, h), r in rates.items() if c == coin)
    return read


def no_x(coin, t_us, purpose):
    return {'u_us': np.zeros(0, np.int64), 'known_at_us': np.zeros(0, np.int64), 'S04': np.zeros(0), 'S05': np.zeros(0), 'reason': np.zeros(0, object)}


def C(tmp, rates=None, xcost=no_x, recorder=None, lab_root=None):
    return costs.Costs(S, record=record(tmp), funding=funding_of(rates or {}), xcost=xcost, recorder=recorder, lab_root=lab_root)


def test_C1_record_is_the_dearer_and_one_table_coins_refused(tmp_path):
    r = record(tmp_path)
    assert r[('AAA', 0)] == (16.0, 'V4') and r[('AAA', 23)] == (11.0, 'V1')
    assert not any(k[0] == 'BBB' for k in r)                    # in V4 only: no row (named in the header)
    assert 'BBB' in costs.make_record(*tables(tmp_path, [('AAA', 20.0)], [('AAA', 0, 25.0), ('BBB', 0, 30.0)]))[1]


def test_C2_hour_lookup_parts_and_stress(tmp_path):
    c = C(tmp_path); t = np.array([T0 + 23 * H_US + 3_599 * US, T0 + 24 * H_US], np.int64)   # 23:59:59 and the next 00:00:00
    x = c.cost_at(np.array(['AAA', 'AAA']), t, 'charge')
    np.testing.assert_allclose(x['book_bp'], [11.0, 16.0]); np.testing.assert_allclose(x['fee_bp'], [9.0, 9.0])
    np.testing.assert_allclose(x['gap_bp'], [14.4, 14.4]); np.testing.assert_allclose(x['total_bp'], [9 + 11 + 14.4, 9 + 16 + 14.4])
    np.testing.assert_allclose(x['total_x1_5_bp'], [9 + 1.5 * (11 + 14.4), 9 + 1.5 * (16 + 14.4)])
    np.testing.assert_allclose(x['total_x2_bp'], [9 + 2 * (11 + 14.4), 9 + 2 * (16 + 14.4)])
    assert c.gap_bp('binance') == pytest.approx(14.4) and c.gap_bp('hl') == 0.0


def test_C3_unknown_coin_or_hour_refused_never_a_median(tmp_path):
    x = C(tmp_path).cost_at(np.array(['ZZZ', 'AAA']), np.array([T0, T0 + 5 * H_US], np.int64), 'charge')   # AAA hour 5 has no row
    assert np.isnan(x['total_bp']).all() and list(x['reason']) == ['NO_COST', 'NO_COST']


def test_C3b_record_never_selects(tmp_path):
    """README sec 5: the record carries no known_at; asking it for a selection is refused (gates and skips use cost_fire)"""
    with pytest.raises(ValueError):
        C(tmp_path).cost_at(np.array(['AAA']), np.array([T0], np.int64), 'select')


def test_C4_funding_sign_both_ways_and_hours_counted(tmp_path):
    c = C(tmp_path, {('AAA', 1): 0.0001, ('AAA', 2): 0.0001, ('AAA', 3): -0.0002})
    t_in, t_out = np.array([T0 + H_US] * 2, np.int64), np.array([T0 + 3 * H_US] * 2, np.int64)      # (01:00, 03:00]: hours 2 and 3
    f = c.funding_paid(np.array(['AAA', 'AAA']), np.array([1, -1]), t_in, t_out)
    np.testing.assert_allclose(f['funding_bp'], [(0.0001 - 0.0002) * 1e4, -(0.0001 - 0.0002) * 1e4])   # net negative: the SHORT pays
    np.testing.assert_array_equal(f['hours'], [2, 2])                            # entry exactly at 01:00 does not pay 01:00
    g = c.funding_paid(np.array(['AAA', 'AAA']), np.array([1, -1]), np.array([T0] * 2, np.int64), np.array([T0 + H_US] * 2, np.int64))
    np.testing.assert_allclose(g['funding_bp'], [1.0, -1.0])                     # a positive rate: the long pays, the short receives


def test_C5_missing_hour_is_unknown_never_zero(tmp_path):
    c = C(tmp_path, {('AAA', 1): 0.0001, ('AAA', 3): 0.0001})                    # hour 2 missing
    f = c.funding_paid(np.array(['AAA']), np.array([1]), np.array([T0], np.int64), np.array([T0 + 3 * H_US], np.int64))
    assert np.isnan(f['funding_bp'][0]) and f['reason'][0] == 'FUNDING_MISSING' and f['missing'][0] == 1


def test_C6_cost_fire_known_at(tmp_path):
    """the round trip at the fire from X1.COST S04 + S05 at the last 5 s point u <= t KNOWN by t; a huge value planted 1 s after t changes
    nothing; an empty cell keeps its reason; the prefix check holds"""
    t = T0 + 600 * US

    def x(coin, t_us, purpose):
        return {'u_us': np.array([t - 5 * US, t, t + US], np.int64), 'known_at_us': np.array([t - 5 * US, t + 2 * US, t + US], np.int64),
                'S04': np.array([3.0, 1e9, 1e9]), 'S05': np.array([4.0, 1e9, 1e9]), 'reason': np.array(['', '', ''], object)}
    y = C(tmp_path, xcost=x).cost_fire(np.array(['AAA']), np.array([t], np.int64), 'research')
    assert y['book_bp'][0] == 7.0 and y['total_bp'][0] == pytest.approx(9 + 7 + 14.4) and y['known_at_us'][0] <= t

    def hole(coin, t_us, purpose):
        return {'u_us': np.array([t], np.int64), 'known_at_us': np.array([t], np.int64), 'S04': np.array([np.nan]), 'S05': np.array([4.0]),
                'reason': np.array(['BOOK_HOLE'], object)}
    z = C(tmp_path, xcost=hole).cost_fire(np.array(['AAA']), np.array([t], np.int64), 'research')
    assert np.isnan(z['total_bp'][0]) and z['reason'][0] == 'BOOK_HOLE'


def test_C6b_funding_joined_to_an_entry_trips_the_guard(tmp_path):
    f = C(tmp_path, {('AAA', 1): 0.0001}).funding_paid(np.array(['AAA']), np.array([1]), np.array([T0], np.int64), np.array([T0 + H_US], np.int64))
    assert f['known_at_us'][0] == T0 + H_US
    with pytest.raises(lookahead.LookaheadError):
        lookahead.join_guard(f['known_at_us'], np.array([T0], np.int64), 'funding at entry')   # (known_at, decision)


def test_C7_size_above_10k_refused(tmp_path):
    x = C(tmp_path).trade_cost(np.array(['AAA']), np.array([1]), np.array([T0], np.int64), np.array([T0 + H_US], np.int64), np.array([20000.0]))
    assert np.isnan(x['total_bp'][0]) and x['reason'][0] == 'SIZE_REFUSED'


def test_C8_one_c_through_trade_cost(tmp_path):
    """trade_cost = cost_at at entry + funding_paid: the same fee, book, gap the label, the gate and the exit read (QUANT T03 M2)"""
    c = C(tmp_path, {('AAA', 1): 0.0001}); args = (np.array(['AAA']), np.array([-1]), np.array([T0], np.int64), np.array([T0 + H_US], np.int64))
    tc = c.trade_cost(*args, np.array([100.0])); at = c.cost_at(args[0], args[2], 'charge'); f = c.funding_paid(*args)
    for k in ('fee_bp', 'book_bp', 'gap_bp'):
        assert tc[k][0] == at[k][0]
    assert tc['funding_bp'][0] == f['funding_bp'][0] == -1.0 and tc['total_bp'][0] == pytest.approx(at['total_bp'][0] - 1.0)


def test_C9_funding_tie_with_the_old_receipt():
    """real data (the build job): the downloaded Sep-Dec 2025 hourly rates equal q_471169's per (coin, hour), named differences only"""
    store = '<DATA_ROOT>/hl_funding_hourly'
    if not os.path.isdir(store) or not hasattr(costs, 'funding_tie'):
        pytest.skip('real-data tie runs in the build job (store or costs.funding_tie absent here)')
    r = costs.funding_tie(store, '<LAB_REPO>/forensics/team/RESEARCH/QUANT/receipts/q_471169_HL_FUNDING_HOURLY.tsv')
    assert r['differ'] == 0, r


def test_C10_determinism(tmp_path):
    a = record(tmp_path); b = record(tmp_path); assert a == b
    t = np.array([T0, T0 + 23 * H_US], np.int64); x = C(tmp_path).cost_at(np.array(['AAA', 'AAA']), t, 'charge'); y = C(tmp_path).cost_at(np.array(['AAA', 'AAA']), t, 'charge')
    for k in x:
        np.testing.assert_array_equal(x[k], y[k])


def test_C11_purpose_required_select_refused_sealed_day_refused(tmp_path):
    """LAB1 MUSTs 1-2: purpose is required on cost_at and cost_fire; 'select' always raises; cost_fire reads X1.COST through lab3.days
    with the caller's purpose, so a sealed (BLIND) day is refused for research exactly as lab3.days refuses it"""
    c = C(tmp_path); a = (np.array(['AAA']), np.array([T0], np.int64))
    with pytest.raises(TypeError):
        c.cost_at(*a)
    with pytest.raises(TypeError):
        c.cost_fire(*a)
    for bad in ('select', 'other'):
        with pytest.raises(ValueError):
            c.cost_at(*a, bad)
    sealed = int(1781481600) * US                                    # 2026-06-15: BLIND (lab3/law.py)
    d = C(tmp_path, xcost=None, lab_root=str(tmp_path))                 # the default reader: lab3.days on a (planted, empty) root
    with pytest.raises(PermissionError):
        d.cost_fire(np.array(['AAA']), np.array([sealed], np.int64), 'research')


def test_C12_recorder_funding_equals_stored_and_names_its_source(tmp_path):
    """LAB1 MUST 3: paper and live take funding from the HL recorder's live rates through the same rule; on an hour both hold the two agree;
    the source is named in every row"""
    rates = {('AAA', 1): 0.0001, ('AAA', 2): -0.00005}
    c = C(tmp_path, rates, recorder=funding_of(rates)); args = (np.array(['AAA', 'AAA']), np.array([1, -1]), np.array([T0] * 2, np.int64),
                                                              np.array([T0 + 2 * H_US] * 2, np.int64))
    st, rc = c.funding_paid(*args), c.funding_paid(*args, source='recorder')
    np.testing.assert_allclose(st['funding_bp'], rc['funding_bp']); assert list(st['source']) == ['stored'] * 2 and list(rc['source']) == ['recorder'] * 2
    with pytest.raises(ValueError):
        c.funding_paid(*args, source='guess')


class FakeDays:
    """a lab3.days stand-in for the DEFAULT X1.COST reader: per day, 5 s points; S04 = 1 + index/1000, S05 = 2; known_at = the point's time,
    except planted late points (known 10 s after their time)"""
    def __init__(self, late=()):
        self.late = set(late); self.calls = []

    def at(self, code, days, coins, step, record=True):
        D = days[0]; self.calls.append((code, D)) if record else None; n = 86400 // step
        d0 = int(__import__('datetime').datetime.strptime(D, '%Y%m%d').replace(tzinfo=__import__('datetime').timezone.utc).timestamp()) * US
        u = d0 + np.arange(n, dtype=np.int64) * step * US; k = u.copy()
        for x in self.late:
            if d0 <= x < d0 + 86400 * US:
                k[(x - d0) // (step * US)] = x + 10 * US
        v = (1 + np.arange(n) / 1000.0) if code.endswith('S04') else np.full(n, 2.0)
        return {'v': v.reshape(1, 1, n), 'k': k.reshape(1, 1, n), 'reason': np.full((1, 1, n), None, object)}

    # D12C-02 (OX-CODE2): costs_v3 reads X1.COST through the CLOCK API (read / step / reasons), as lab3.days serves a CLOCK part
    def read(self, code, field, days, coins):
        g = self.at(code, days, coins, 5, record=field == 'v')         # one decode a (code, day): counted on its value field
        if field == 'e':
            return np.full(g['v'].shape, -1, np.int64)                   # no reason index: every point valued
        return g[field]

    def step(self, code, day):
        return 5

    def reasons(self, code, day):
        return []


def test_C13_cost_fire_steps_back_to_the_last_known_point(tmp_path):
    """SCOUT + LAB1 MUST (15:38Z, 15:39Z): when the 5 s point holding t is known AFTER t, cost_fire uses the last point known by t, also
    across midnight (D-1's last point); plant at t = u + 1 s. The day arrays are read once per (code, day). Mutant killed: only the point at t."""
    fd = FakeDays(late=[T0 + 600 * US, T0]); c = costs.Costs(S, record=record(tmp_path), funding=funding_of({}), days=lambda purpose: fd)
    y = c.cost_fire(np.array(['AAA', 'AAA']), np.array([T0 + 601 * US, T0 + 600 * US + 2 * US], np.int64), 'research')
    assert y['book_bp'][0] == pytest.approx(1 + 119 / 1000.0 + 2) and y['known_at_us'][0] == T0 + 595 * US     # point 120 late: point 119
    z = c.cost_fire(np.array(['AAA']), np.array([T0 + US], np.int64), 'research')                             # 00:00:01, 00:00 point late
    assert z['book_bp'][0] == pytest.approx(1 + 17279 / 1000.0 + 2) and z['known_at_us'][0] == T0 - 5 * US     # D-1's last point
    assert len(fd.calls) == len(set(fd.calls))                                                                 # each day read once


class NotBuilt(Exception):
    pass


def test_C15_prev_day_not_built_gives_no_earlier_points(tmp_path):
    """LAB1 17:11:46Z MUST 2: at 00:00:01 of the first lab day (D-1 NotBuilt) the late 00:00 point gives NO_COST_AT_FIRE, no raise; counted"""
    fd = FakeDays(late=[T0]); real = fd.at
    def at(code, days, coins, step, record=True):
        if days[0] != '20251013':
            raise NotBuilt(days[0])
        return real(code, days, coins, step, record)
    fd.at = at; c = costs.Costs(S, record=record(tmp_path), funding=funding_of({}), days=lambda purpose: fd)
    z = c.cost_fire(np.array(['AAA']), np.array([T0 + US], np.int64), 'research')
    assert np.isnan(z["book_bp"][0]) and c.prev_not_built == 1                         # the one D-1 grid read refused, counted


def test_C14_trade_cost_passes_the_funding_source(tmp_path):
    """LAB1 MUST (15:39Z): paper and live call trade_cost with source='recorder'; it reaches funding_paid and is named"""
    rates = {('AAA', 1): 0.0001}; c = C(tmp_path, rates, recorder=funding_of({('AAA', 1): 0.0003}))
    a = (np.array(['AAA']), np.array([1]), np.array([T0], np.int64), np.array([T0 + H_US], np.int64), np.array([100.0]))
    assert c.trade_cost(*a)['funding_bp'][0] == pytest.approx(1.0) and c.trade_cost(*a, source='recorder')['funding_bp'][0] == pytest.approx(3.0)
    assert c.trade_cost(*a, source='recorder')['funding_source'][0] == 'recorder'
