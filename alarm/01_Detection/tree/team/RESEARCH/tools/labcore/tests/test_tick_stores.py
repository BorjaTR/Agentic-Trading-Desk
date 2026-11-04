"""labcore.tick_stores: the true names of the two v1 'oi' traps, as-of (last row known by t), missing = NaN, the law refusal read from
law.py, max age; a mutant that reads the next row (lookahead) or returns 0 for a missing file must fail"""
import os, sys, tempfile, types
import numpy as np
import pytest
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, os.path.realpath(os.path.join(HERE, '..', '..')))
from labcore import tick_stores as TS, gates


def planted(root, store, coin, day, t_us, v, key):
    os.makedirs(os.path.join(root, store), exist_ok=True); np.savez(os.path.join(root, store, '%s_%s.npz' % (coin, day)), t_us=np.array(t_us, np.int64), **{key: np.array(v, float)})


def setup():
    r = tempfile.mkdtemp(dir=os.environ.get('TMPDIR')); d0 = 1760000000 - 1760000000 % 86400; day = '20251009'
    planted(r, 'hl_mark_2025', 'BTC', day, [(d0 + 10) * 10**6, (d0 + 20) * 10**6], [100.0, 101.0], 'oi')
    planted(r, 'hl_oi_2025', 'BTC', day, [(d0 + 10) * 10**6], [5.0], 'open_interest')
    return r, d0, day


def test_names_and_asof():
    r, d0, day = setup()
    t, v, name = TS.read_day('hl_mark_2025', 'BTC', day, r); assert name == 'mark_px' and v.tolist() == [100.0, 101.0]
    x = TS.value_at('hl_mark_2025', 'BTC', [d0 + 5, d0 + 10, d0 + 19.9, d0 + 20, d0 + 99], delay_s=0, root=r)
    assert np.isnan(x[0]) and x[1:].tolist() == [100.0, 100.0, 101.0, 101.0]
    assert TS.read_day('hl_oi_2025', 'BTC', day, r)[2] == 'open_interest'


def test_missing_and_age():
    r, d0, day = setup()
    assert np.isnan(TS.value_at('hl_mark_2025', 'ETH', [d0 + 30], delay_s=0, root=r)).all()
    assert np.isnan(TS.value_at('hl_mark_2025', 'BTC', [d0 + 99], delay_s=0, max_age_s=30, root=r)).all()


def test_delay():
    """02-06: a row is known at exchange time + delay_s; no delay stated = refused"""
    r, d0, day = setup()
    x = TS.value_at('hl_mark_2025', 'BTC', [d0 + 11, d0 + 12, d0 + 21, d0 + 22], delay_s=2, root=r)
    assert np.isnan(x[0]) and x[1:].tolist() == [100.0, 100.0, 101.0]
    for bad in (None, -1, float('nan')):
        with pytest.raises(ValueError):
            TS.value_at('hl_mark_2025', 'BTC', [d0 + 30], delay_s=bad, root=r)


def test_availability_kind():
    """A04-03: no receipt clock = MODEL_AVAILABLE_AT; a use needing observed availability is refused; the model must be named; a row later
    than the model's delay is excluded under the late stress"""
    r, d0, day = setup(); m = {'delay_s': 2, 'scope': 'planted', 'breach_policy': 'late rows excluded under stress', 'source': '0' * 16}
    v, meta = TS.value_at_checked('hl_mark_2025', 'BTC', [d0 + 12.5], m, root=r)
    assert meta['availability'] == 'MODEL_AVAILABLE_AT' and v.tolist() == [100.0]
    with pytest.raises(PermissionError):
        TS.value_at_checked('hl_mark_2025', 'BTC', [d0 + 12.5], m, require='OBSERVED', root=r)
    with pytest.raises(ValueError):
        TS.value_at_checked('hl_mark_2025', 'BTC', [d0 + 12.5], {'delay_s': 2}, root=r)
    assert np.isnan(TS.late_stress('hl_mark_2025', 'BTC', [d0 + 12.5], m, 5, root=r)[0])


def test_law_refusal():
    law = gates.load_law(); lo = str(min(x[0] for x in law.RESEARCH_REFUSED))
    with pytest.raises(PermissionError):
        TS.read_day('hl_mark_2025', 'BTC', lo, '/nonexistent')


def test_mutants():
    src = open(TS.__file__).read()
    for old, new in (("j = np.searchsorted(t + dus, tu, side='right') - 1", "j = np.minimum(np.searchsorted(t + dus, tu, side='right'), len(t) - 1)"),
                     ("        return np.zeros(0, np.int64), np.zeros(0, float), name", "        return np.zeros(1, np.int64), np.zeros(1, float), name"),
                     ("j = np.searchsorted(t + dus, tu, side='right') - 1", "j = np.searchsorted(t, tu, side='right') - 1")):
        assert src.count(old) == 1
        m = types.ModuleType('labcore.tick_stores_m'); m.__package__ = 'labcore'; m.__file__ = TS.__file__
        exec(compile(src.replace(old, new), 'tick_stores_m', 'exec'), m.__dict__)
        saved = TS.value_at, TS.read_day
        try:
            TS.value_at, TS.read_day = m.value_at, m.read_day; failed = False
            try:
                test_names_and_asof(); test_missing_and_age(); test_delay()
            except AssertionError:
                failed = True
            assert failed, new
        finally:
            TS.value_at, TS.read_day = saved
