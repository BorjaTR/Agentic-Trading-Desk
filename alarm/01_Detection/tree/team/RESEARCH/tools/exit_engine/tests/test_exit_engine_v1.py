"""TEST2 tests for T03 exit_engine (README V2.4 f096e1bee1928fc0 section 5 + 1c LOOKAHEAD + 6 proof rows), written FIRST (23 Oct 2026).
Planted paths, seconds. Run: EXIT_TARGET=engine (default) or oracle; pytest -q (Framework python 3.11, taskpolicy -b nice 10).
Tests marked engine_only need the engine's registry, cost and reader calls; every other test also runs on the oracle with each mutant
(run_teeth_exit_v1.py). Paper only; no store is read here (the SPEED row is speed_exit_v1.py)."""
import math, os, sys, tempfile
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import engine_iface_v1 as E

engine_only = pytest.mark.engine_only
P0 = 100.0


def flat(n, p=P0):
    return np.full(n, p), np.full(n, p), np.full(n, p)


def walk(n, seed, sd=8e-4, p=P0):
    r = np.random.default_rng(seed)
    c = p * np.exp(np.cumsum(r.normal(0, sd, n)))
    w = np.abs(r.normal(0, sd / 2, n)) * c
    return c, c + w, c - w


def one(c, h, l, row, e=0, side=1, px=None, **kw):
    o = E.simulate(c, h, l, [e], [c[e] if px is None else px], [side], row, **kw)
    return {k: v[0] for k, v in o.items()}


def put(c, h, l, j, close=None, hi=None, lo=None):
    if close is not None:
        c[j] = close
    if hi is not None:
        h[j] = hi
    if lo is not None:
        l[j] = lo


# ---------------------------------------------------------------- oracle (README 5: equals exits_v1.trail_exit)
def test_oracle_equals_exits_v1():
    """stop, arm 0.6, give 0.2, no take, no monitor, pct: the same kind, arm bar and price as exits_v1; the price is the worse of v1's
    level and the exit bar's close (V2.4 books the worse of level and close; v1 books the level: the only intended difference)"""
    sys.path.insert(0, os.path.join(E.TOOLS, 'moves'))
    import exits_v1 as V1
    c, h, l = walk(6000, 1, sd=2.5e-4)
    e = np.arange(0, 4000, 41); kinds = {0: 'stop', 1: 'trail', 2: 'time'}; seen = set(); worse_used = 0
    for side, sname in ((1, 'long'), (-1, 'short')):
        for stop in (1.5, 1.0, 0.5):
            px1, k1, t1, _, _ = V1.trail_exit(c, h, l, e, sname, stop, max_bars=1200)
            o = E.simulate(c, h, l, e, c[e], np.full(len(e), side), E.row(kind='T', stop=stop, arm=0.6, give=0.2, time_limit_min=60))
            assert [kinds[int(k)] for k in k1] == list(o['kind'])
            np.testing.assert_array_equal(t1, o['bars_to_arm'])
            cl = c[o['exit_bar']]
            want = np.where(o['kind'] == 'time', px1, np.minimum(px1, cl) if side > 0 else np.maximum(px1, cl))
            np.testing.assert_allclose(o['exit_px'], want, rtol=0, atol=1e-12)
            worse_used += int(np.sum(want != px1)); seen |= set(o['kind'])
    assert {'stop', 'trail', 'time'} <= seen
    assert worse_used > 0                                    # the plant reaches the worse-of rule, so it is tested


# ---------------------------------------------------------------- sign plants
def test_sign_mirror_bracket():
    """the same path mirrored around the entry with side -1 gives the mirrored result (bracket + time, exact)"""
    n = 0
    for seed in range(20):
        c, h, l = walk(1500, 100 + seed, sd=6e-4)
        k = P0 / c[0]; c, h, l = c * k, h * k, l * k; c[0] = P0
        r = E.row(stop=0.5, take=0.7, time_limit_min=30)
        a = one(c, h, l, r, side=1)
        b = one(2 * P0 - c, 2 * P0 - l, 2 * P0 - h, r, side=-1)
        assert a['kind'] == b['kind'] and a['exit_bar'] == b['exit_bar']
        assert abs((2 * P0 - a['exit_px']) - b['exit_px']) < 1e-9 and abs(a['ret_pct'] - b['ret_pct']) < 1e-9
        n += a['kind'] in ('stop', 'take')
    assert n >= 5


def test_sign_down_push_flips():
    """a down push of 2 pct: the long loses at its stop, the short wins at its take"""
    c, h, l = flat(200); c[10:] = 98.0; h[10:] = 98.0; l[10:] = 98.0
    r = E.row(stop=1.0, take=1.0, time_limit_min=5)
    lo_, sh = one(c, h, l, r, side=1), one(c, h, l, r, side=-1)
    assert lo_['kind'] == 'stop' and lo_['ret_pct'] < 0
    assert sh['kind'] == 'take' and sh['ret_pct'] > 0 and abs(sh['exit_px'] - 99.0) < 1e-9


# ---------------------------------------------------------------- order plants
def test_order_stop_beats_take_in_one_bar():
    c, h, l = flat(100); put(c, h, l, 5, hi=101.0, lo=99.0)
    o = one(c, h, l, E.row(stop=0.5, take=0.6, time_limit_min=2))
    assert o['kind'] == 'stop' and o['exit_bar'] == 5


def test_order_trail_line_from_previous_bar():
    """bar 1 arms (best 100.6, trail 100.6 x 0.998); bar 2 makes a new best AND touches that line: books the line of bar 1"""
    c, h, l = flat(100); put(c, h, l, 1, close=100.5, hi=100.6, lo=100.45); put(c, h, l, 2, close=100.5, hi=101.0, lo=100.39)
    o = one(c, h, l, E.row(kind='T', stop=1.0, arm=0.5, give=0.2, time_limit_min=2))
    assert o['kind'] == 'trail' and o['exit_bar'] == 2 and o['bars_to_arm'] == 1
    assert abs(o['exit_px'] - 100.6 * (1 - 0.002)) < 1e-9


# ---------------------------------------------------------------- booking
def test_stop_books_worse_of_level_and_close():
    c, h, l = flat(100); put(c, h, l, 5, close=99.2, lo=99.0)
    o = one(c, h, l, E.row(stop=0.5, time_limit_min=2))
    assert o['kind'] == 'stop' and abs(o['exit_px'] - 99.2) < 1e-9 and abs(o['gap_bp'] - 30.0) < 1e-6
    c, h, l = flat(100); put(c, h, l, 5, close=99.8, lo=99.0)
    o = one(c, h, l, E.row(stop=0.5, time_limit_min=2))
    assert o['kind'] == 'stop' and abs(o['exit_px'] - 99.5) < 1e-9 and abs(o['gap_bp']) < 1e-6


def test_stop_never_better_than_level_on_walks():
    c, h, l = walk(5000, 7, sd=1e-3)
    e = np.arange(0, 3000, 13)
    for side in (1, -1):
        o = E.simulate(c, h, l, e, c[e], np.full(len(e), side), E.row(stop=0.4, time_limit_min=60))
        st = o['kind'] == 'stop'; lvl = c[e] * (1 - side * 0.004)
        assert st.sum() > 10 and np.all(side * (o['exit_px'][st] - lvl[st]) <= 1e-12)


def test_take_fills_only_on_trade_through():
    c, h, l = flat(100, 1.0); h[5] = 1.5                       # touches the take (+50 pct of 1.0), never through
    o = one(c, h, l, E.row(stop=40, take=50, time_limit_min=3))
    assert o['kind'] == 'time' and o['touched_not_filled'] >= 1
    h[8] = 1.51                                                # through: books the level
    o = one(c, h, l, E.row(stop=40, take=50, time_limit_min=3))
    assert o['kind'] == 'take' and o['exit_bar'] == 8 and o['exit_px'] == 1.5


def test_heat_and_best_include_the_exit_bar():
    c, h, l = flat(100); put(c, h, l, 3, hi=100.4, lo=99.8); put(c, h, l, 6, close=99.3, lo=99.1)
    o = one(c, h, l, E.row(stop=0.5, time_limit_min=2))
    assert o['exit_bar'] == 6 and abs(o['heat_pct'] - (-0.9)) < 1e-9 and abs(o['best_pct'] - 0.4) < 1e-9
    s = one(c, h, l, E.row(stop=0.5, time_limit_min=2), side=-1)        # the short: heat from the highs
    assert s['kind'] == 'time' and abs(s['heat_pct'] - (-0.4)) < 1e-9 and abs(s['best_pct'] - 0.9) < 1e-9


# ---------------------------------------------------------------- units (pct, c, nm)
def test_units_c_and_nm_equal_pct_times_unit():
    c, h, l = walk(4000, 3); e = np.arange(0, 2500, 11); m = len(e); sd = np.ones(m, int)
    a = E.simulate(c, h, l, e, c[e], sd, E.row(kind='BT', stop=0.6, take=1.0, arm=0.4, give=0.2, time_limit_min=30))
    b = E.simulate(c, h, l, e, c[e], sd, E.row(kind='BT', unit='c', stop=1.2, take=2.0, arm=0.8, give=0.4, time_limit_min=30),
                   units={'c': np.full(m, 0.5), 'known_at_us': np.zeros(m, np.int64)})
    d = E.simulate(c, h, l, e, c[e], sd, E.row(kind='BT', unit='nm', stop=2.4, take=4.0, arm=1.6, give=0.8, time_limit_min=30),
                   units={'nm': np.full(m, 0.25), 'known_at_us': np.zeros(m, np.int64)})
    for x in (b, d):
        assert list(a['kind']) == list(x['kind'])
        np.testing.assert_array_equal(a['exit_bar'], x['exit_bar']); np.testing.assert_array_equal(a['exit_px'], x['exit_px'])
    assert len(set(a['kind'])) >= 3


@pytest.mark.parametrize('units', [None, {'c': np.array([np.nan]), 'known_at_us': np.array([0])}, {'nm': np.array([0.3])}])
def test_missing_unit_refuses(units):
    c, h, l = flat(100)
    with pytest.raises(ValueError):
        E.simulate(c, h, l, [0], [P0], [1], E.row(unit='c', stop=1, time_limit_min=2), units=units)


# ---------------------------------------------------------------- monitor
def test_monitor_books_next_bar_close():
    c, h, l = flat(100); c[20:] = h[20:] = l[20:] = 100.3; c[26:] = h[26:] = l[26:] = 100.4
    o = E.simulate(c, h, l, [0, 0], [P0, P0], [1, 1], E.row(stop=0.5, time_limit_min=4, monitor='caller'), monitor=[25, -1])
    assert list(o['kind']) == ['monitor', 'time'] and o['exit_bar'][0] == 26 and abs(o['exit_px'][0] - 100.4) < 1e-9


def _caller(c, peek):
    """a caller's monitor: the first bar whose close (good) or whose close 3 bars LATER (bad: lookahead) is above 100.3"""
    v = c[3:] if peek else c
    k = np.nonzero(v > 100.3)[0]
    return int(k[0]) if len(k) else -1


def test_monitor_prefix_catches_a_caller_lookahead():
    c, h, l = flat(80); c[30:] = h[30:] = l[30:] = 100.5
    r = E.row(stop=0.5, time_limit_min=3, monitor='caller')
    for peek, same in ((False, True), (True, False)):
        full = one(c, h, l, r, monitor=[_caller(c, peek)])
        b = full['exit_bar']; cc, hh, ll = c[:b + 1], h[:b + 1], l[:b + 1]
        cut = one(cc, hh, ll, r, monitor=[_caller(cc, peek)])
        assert ((cut['kind'], cut['exit_bar']) == (full['kind'], full['exit_bar'])) == same


# ---------------------------------------------------------------- time, NOPRICE, holes, min hold, early stop
def test_time_and_noprice_never_cut_short():
    c, h, l = flat(100)
    o = E.simulate(c, h, l, [0, 60, 59], [P0] * 3, [1] * 3, E.row(stop=0.5, time_limit_min=2))
    assert list(o['kind']) == ['time', 'noprice', 'time'] and list(o['exit_bar']) == [40, -1, 99] and math.isnan(o['exit_px'][1])


def test_hole_across_a_stop_books_first_price_after_with_gap():
    c, h, l = flat(100); c[10:20] = h[10:20] = l[10:20] = np.nan; c[20:] = h[20:] = l[20:] = 98.0
    o = one(c, h, l, E.row(stop=1.0, time_limit_min=3))
    assert o['kind'] == 'stop' and o['exit_bar'] == 20 and o['exit_px'] == 98.0 and o['gap_len_bars'] == 10
    c, h, l = flat(100); put(c, h, l, 20, close=98.0, lo=98.0)        # the same stop without a hole: no GAP
    assert one(c, h, l, E.row(stop=1.0, time_limit_min=3))['gap_len_bars'] == 0


def test_empty_bar_is_never_a_price():
    c, h, l = flat(100); c[15:26] = h[15:26] = l[15:26] = np.nan
    o = one(c, h, l, E.row(stop=1.0, time_limit_min=1))                 # the time bar (20) is empty
    assert o['kind'] == 'noprice' and math.isnan(o['exit_px'])
    c2, h2, l2 = walk(3000, 11); c2[::17] = np.nan; h2[::17] = np.nan; l2[::17] = np.nan
    e = np.arange(1, 2000, 10); e = e[np.isfinite(c2[e])]
    o = E.simulate(c2, h2, l2, e, c2[e], np.ones(len(e), int), E.row(kind='T', stop=0.5, arm=0.3, give=0.15, time_limit_min=20))
    ok = o['kind'] != 'noprice'
    assert np.all(np.isfinite(o['exit_px'][ok])) and np.all(np.isfinite(c2[o['exit_bar'][ok]]))


def test_min_hold_blocks_take_keeps_stop():
    c, h, l = flat(100, 1.0); h[5] = 1.6; l[10] = 0.5
    o = one(c, h, l, E.row(stop=40, take=50, time_limit_min=3, min_hold_min=1))
    assert o['kind'] == 'stop' and o['exit_bar'] == 10


def test_early_stop_only_in_its_minutes():
    c, h, l = flat(100, 1.0); l[5] = 0.85
    o = one(c, h, l, E.row(stop=40, early_stop=10, early_min=1, time_limit_min=3))
    assert o['kind'] == 'stop' and o['exit_bar'] == 5 and abs(o['exit_px'] - 0.9) < 1e-12
    c, h, l = flat(100, 1.0); l[30] = 0.85
    assert one(c, h, l, E.row(stop=40, early_stop=10, early_min=1, time_limit_min=3))['kind'] == 'time'


# ---------------------------------------------------------------- times on every trade row (1c)
def test_times_on_rows():
    c, h, l = flat(100); put(c, h, l, 7, lo=99.0)
    t0 = 1_760_000_000_000_000
    o = E.simulate(c, h, l, [2, 50], [P0, P0], [1, 1], E.row(unit='nm', stop=1.0, time_limit_min=1),
                   units={'nm': np.array([0.5, 0.5]), 'known_at_us': np.array([t0, t0 + 50 * 3_000_000])}, t0_us=t0,
                   signal_us=[t0 + 3_000_000, t0 + 48 * 3_000_000])
    np.testing.assert_array_equal(o['entry_us'], [t0 + 6_000_000, t0 + 150_000_000])
    np.testing.assert_array_equal(o['exit_us'], [t0 + 21_000_000, t0 + 210_000_000])
    np.testing.assert_array_equal(o['known_at_us'], o['exit_us'])
    assert np.all(o['units_known_at_us'] <= o['entry_us']) and np.all(o['signal_us'] <= o['entry_us'])


# ---------------------------------------------------------------- LOOKAHEAD (1c): prefix, future plant, join guard
TRAIL_ROW = dict(kind='BT', stop=0.5, take=1.2, arm=0.3, give=0.15, time_limit_min=20)


def test_lookahead_prefix():
    c, h, l = walk(2500, 21, sd=1.5e-4); e = np.arange(0, 1800, 45)
    o = E.simulate(c, h, l, e, c[e], np.where(np.arange(len(e)) % 2, 1, -1), E.row(**TRAIL_ROW))
    seen = 0
    for i in np.nonzero(o['kind'] != 'noprice')[0]:
        b = o['exit_bar'][i]
        x = one(c[:b + 1], h[:b + 1], l[:b + 1], E.row(**TRAIL_ROW), e=e[i], side=(1 if i % 2 else -1))
        assert (x['kind'], x['exit_bar'], x['exit_px']) == (o['kind'][i], b, o['exit_px'][i]); seen += 1
    assert seen > 20 and len(set(o['kind'])) >= 3


def test_lookahead_future_plant():
    c, h, l = walk(2500, 22, sd=1.5e-4); e = np.arange(0, 1800, 45)
    o = E.simulate(c, h, l, e, c[e], np.ones(len(e), int), E.row(**TRAIL_ROW))
    for i in np.nonzero(o['kind'] != 'noprice')[0]:
        b = o['exit_bar'][i]; cc, hh, ll = c.copy(), h.copy(), l.copy()
        cc[b + 1] *= 10; hh[b + 1] *= 10; ll[b + 1] /= 10
        x = one(cc, hh, ll, E.row(**TRAIL_ROW), e=e[i])
        assert (x['kind'], x['exit_bar'], x['exit_px']) == (o['kind'][i], b, o['exit_px'][i])
    assert 'time' in set(o['kind'])


def test_lookahead_join_guard_refuses_unit_known_after_entry():
    """mutant of the README: nm from the fire's own 15 min window ending after the entry (known_at = entry + 1 us) is refused"""
    c, h, l = flat(100); t0 = 1_760_000_000_000_000; entry_us = t0 + 3 * 3_000_000
    E.simulate(c, h, l, [3], [P0], [1], E.row(unit='nm', stop=1, time_limit_min=1),
               units={'nm': np.array([0.4]), 'known_at_us': np.array([entry_us])}, t0_us=t0)          # at the entry: allowed
    with pytest.raises(ValueError):
        E.simulate(c, h, l, [3], [P0], [1], E.row(unit='nm', stop=1, time_limit_min=1),
                   units={'nm': np.array([0.4]), 'known_at_us': np.array([entry_us + 1])}, t0_us=t0)


# ---------------------------------------------------------------- engine only: registry, one c, reader, reuse
EXITS = os.path.join(E.TOOL, 'EXITS_V1.tsv')


@engine_only
def test_registry_exit_t1_and_fade_f1():
    """EXIT_T1 = hb/STRATEGY.txt 2026-10-22T20:00:00Z S3: first stop 3 nm, trail from +2 nm, width 1.5 nm, max hold 3 h"""
    X = E.engine().load_exits(EXITS)
    t = X['EXIT_T1']
    assert (t['unit'], float(t['stop']), float(t['arm']), float(t['give']), float(t['time_limit_min'])) == ('nm', 3.0, 2.0, 1.5, 180.0)
    assert 'T' in t['kind'] and t['take'] in (None, '') and '2026-10-22T20:00:00Z' in t['note']
    f = X['FADE_F1']
    assert f['kind'] == 'B' and f['unit'] == 'nm' and float(f['take']) == 1.0 and float(f['time_limit_min']) == 45.0
    assert 'F1' not in X                                     # STRATEGY 12:06:51Z: FADE_F1, never F1


@engine_only
def test_registry_refuses_wrong_sha16():
    from labcore import ids
    E.engine().load_exits(EXITS, want_sha16=ids.sha16_file(EXITS))
    with pytest.raises(ValueError):
        E.engine().load_exits(EXITS, want_sha16='0' * 16)


def _labcore_cost_c():
    import importlib, pkgutil, labcore
    for mi in pkgutil.iter_modules(labcore.__path__):
        m = importlib.import_module('labcore.' + mi.name)
        if hasattr(m, 'cost_c'):
            return m.cost_c
    raise AssertionError('labcore has no cost_c yet (BUILD2, STRATEGY 12:08:08Z)')


@engine_only
def test_one_c_label_gate_exit_are_the_same_number():
    sys.path.insert(0, os.path.join(E.TOOLS, 'bucket_proof'))
    import bucket_proof as BP
    tab = 'team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv'
    s = {'cost': {'table': tab, 'column': 'cost_bp', 'gap_pct': 0.144, 'stress_gap_pct': 0.288}}
    lab = {}
    for ln in open(os.path.join(E.FORENSICS, tab)):                      # LABEL_EWSD_V1 line 3: c = coin HL cost of record + 0.144
        f = ln.rstrip('\n').split('\t')
        if not ln.startswith('#') and f[0] != 'coin':
            lab[f[0]] = float(f[4]) / 100.0 + 0.144
    coins = ['AAVE', 'ADA', sorted(lab)[-1]]
    label = np.array([lab[x] for x in coins])
    gate = BP.load_cost(s, coins)[0]
    exit_ = np.asarray(E.engine().unit_c(s, coins), float)
    r = _labcore_cost_c()(s, coins); lc = np.asarray(r[0] if isinstance(r, tuple) else r, float)
    np.testing.assert_array_equal(gate, label); np.testing.assert_array_equal(exit_, gate); np.testing.assert_array_equal(lc, gate)
    miss = ['AAVE', 'NOT_A_COIN']                                         # the median fallback is the same in gate and exit
    np.testing.assert_array_equal(np.asarray(E.engine().unit_c(s, miss), float), BP.load_cost(s, miss)[0])
    c, h, l = flat(100); put(c, h, l, 5, close=P0, lo=90.0)               # a stop of 1 c books at P0 x (1 - c / 100)
    o = one(c, h, l, E.row(unit='c', stop=1, time_limit_min=2), units={'c': exit_[:1], 'known_at_us': np.array([0])})
    assert o['kind'] == 'stop' and abs(o['exit_px'] - P0 * (1 - exit_[0] / 100)) < 1e-12


@engine_only
def test_bars_reader_holes_and_midnight():
    """bars() through lab3.bins on a planted root: a missing bin is NaN, a hold across midnight reads the next day"""
    sys.path.insert(0, os.path.join(E.FORENSICS, 'team', 'LAB3', 'code'))
    from lab3 import bins as B
    root = tempfile.mkdtemp(prefix='test2_exit_')
    D1 = B.day_start_us('20251016'); D0 = B.day_start_us('20251015')
    te0 = D1 - np.array([4, 3, 1, 0]) * B.BIN_US                         # 15 Oct: the bin ending D1 - 6 s is missing
    te1 = D1 + np.array([1, 2, 3]) * B.BIN_US
    for day, te, p in (('20251015', te0, np.array([100., 101, 103, 104])), ('20251016', te1, np.array([105., 106, 107]))):
        B.write_bins(root, day, ['AAA'], {'AAA': dict(te=te, tl=te - 1000, px=p, hi=p + 0.5, lo=p - 0.5, n=np.ones(len(te), int),
                                                     buy=0 * p, sell=0 * p)})
    t, c, h, l = E.engine().bars(root, 'AAA', int(te0[0]), int(te1[-1]))
    np.testing.assert_array_equal(t, np.arange(te0[0], te1[-1] + 1, B.BIN_US))
    assert np.isnan(c[2]) and np.isnan(h[2]) and np.isnan(l[2])
    np.testing.assert_array_equal(c[np.isfinite(c)], [100., 101, 103, 104, 105, 106, 107])
    assert D0 < te0[0]


@engine_only
def test_engine_imports_labcore_never_copies():
    src = open(E.engine_path()).read()
    assert 'labcore' in src
    for f in ('def load_cost', 'def cost_c', 'def sha16_file', 'def load_settings', 'def waves', 'def by_wave'):
        assert f not in src, '%s copied into the engine' % f


@engine_only
def test_cross_check_money_v1_and_strategy_book():
    pytest.skip('PENDING: runs when money_v1 and strategy_book call the engine (README 7); TEST2 adds the planted card then')


# ---------------------------------------------------------------- SKEPTIC REVIEW 03 (STRATEGY-130408, BUILD1-130859; 23 Oct 13:3xZ)
def test_03_06_monitor_after_an_empty_bar_books_first_valid_bar_with_gap():
    c, h, l = flat(100); c[20:] = h[20:] = l[20:] = 100.3
    c[26:29] = h[26:29] = l[26:29] = np.nan; c[29:] = h[29:] = l[29:] = 100.4       # k = 25: bars 26-28 empty
    o = one(c, h, l, E.row(stop=0.5, time_limit_min=4, monitor='caller'), monitor=[25])
    assert o['kind'] == 'monitor' and o['exit_bar'] == 29 and abs(o['exit_px'] - 100.4) < 1e-9 and o['gap_len_bars'] == 3


def test_03_07_every_trade_carries_its_holes():
    c, h, l = flat(200); c[5:8] = h[5:8] = l[5:8] = np.nan                            # 3 empty bars, no level crossed
    o = E.simulate(c, h, l, [0, 0, 0, 100], [P0] * 4, [1] * 4,
                   E.row(stop=0.5, time_limit_min=1, monitor='caller'), monitor=[10, -1, -1, -1])
    assert list(o['kind']) == ['monitor', 'time', 'time', 'time']
    assert list(o['hole_bars']) == [3, 3, 3, 0] and list(o['path_gap']) == [True, True, True, False]
    c2, h2, l2 = flat(30); c2[5:8] = h2[5:8] = l2[5:8] = np.nan
    n = one(c2, h2, l2, E.row(stop=0.5, time_limit_min=5))                              # NOPRICE: holes up to the grid's end
    assert n['kind'] == 'noprice' and n['hole_bars'] == 3 and n['path_gap']


@pytest.mark.parametrize('unit', ['c', 'nm'])
def test_03_08_unit_without_known_at_refused(unit):
    c, h, l = flat(100)
    with pytest.raises(ValueError):
        E.simulate(c, h, l, [0], [P0], [1], E.row(unit=unit, stop=1, time_limit_min=2), units={unit: np.array([0.5])})


def test_03_08_stop_from_the_run_extreme_and_its_guard():
    """FADE_F1 shape: a short fading a push; its stop sits 1 nm beyond the run extreme 101, not beyond the entry 100"""
    c, h, l = flat(100); put(c, h, l, 5, hi=101.4); put(c, h, l, 9, close=100.2, hi=101.6)
    r = E.row(unit='nm', stop=1, take=1, time_limit_min=2, stop_from='extreme'); t0 = 1_760_000_000_000_000
    u = {'nm': np.array([0.5]), 'known_at_us': np.array([t0]), 'extreme_px': np.array([101.0]), 'extreme_known_at_us': np.array([t0])}
    o = one(c, h, l, r, side=-1, units=u, t0_us=t0)
    assert o['kind'] == 'stop' and o['exit_bar'] == 9 and abs(o['exit_px'] - 101.0 * 1.005) < 1e-9
    for bad in ({k: v for k, v in u.items() if k != 'extreme_known_at_us'}, dict(u, extreme_known_at_us=np.array([t0 + 1]))):
        with pytest.raises(ValueError):
            one(c, h, l, r, side=-1, units=bad, t0_us=t0)


@engine_only
def test_03_14_coverage_counts_never_drops_noprice():
    c, h, l = flat(100); c[5:7] = h[5:7] = l[5:7] = np.nan
    o = E.simulate(c, h, l, [0, 0, 85, 90], [P0] * 4, [1] * 4, E.row(stop=0.5, time_limit_min=1))
    cov = E.engine().coverage(o)
    assert list(o['kind']) == ['time', 'time', 'noprice', 'noprice']
    assert cov == {'trades': 4, 'resolved': 2, 'noprice': 2, 'with_holes': 2}
