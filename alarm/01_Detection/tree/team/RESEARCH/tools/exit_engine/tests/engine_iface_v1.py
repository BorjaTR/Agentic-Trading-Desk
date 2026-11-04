"""TEST2 engine_iface_v1 (23 Oct 2026): the ONE place where the T03 tests meet the code under test. Target by env EXIT_TARGET:
'oracle' (tests/oracle_exit_v1.py, for the mutant runs) or 'engine' (default; the module at env EXIT_ENGINE, default
tools/exit_engine/exit_engine_v1.py). If BUILD1's names differ from the CONTRACT below, only this file changes (posted with its sha16).

CONTRACT asked of the engine module (README V2.4 sections 1c, 2, 3, 4):
  simulate(close, hi, lo, entry_bar, entry_px, side, row, units=None, monitor=None, t0_us=0, signal_us=None) -> dict of arrays, one per
    trade: exit_bar (-1 when noprice), exit_px, kind (str: stop trail take monitor time noprice), ret_pct (side x (exit/entry - 1) x 100),
    heat_pct and best_pct (side x (worst / best bar extreme / entry - 1) x 100 over bars entry+1 .. exit inclusive), bars_to_arm (-1 never),
    gap_bp (side x (level - booked) / entry x 1e4 for stop and trail, else 0), gap_len_bars (empty bars just before a stop booked after
    a hole, else 0), touched_not_filled (bars where the take was touched, never traded through), signal_us, entry_us, exit_us,
    known_at_us (= exit_us), units_known_at_us.
    row = a dict with the EXITS_V1.tsv columns (None = off); units = {'c': per trade pct, 'nm': per trade pct, 'known_at_us': per trade}.
    Refuses (ValueError) a missing unit and a unit known after its entry (JOIN GUARD).
  load_exits(path, want_sha16=None) -> {id: row}; refuses a file whose sha16 differs.
  unit_c(settings, coins) -> per coin c in pct: THE one cost of record (labcore cost_c = bucket_proof.load_cost moved).
  bars(root, coin, t0_us, t1_us) -> (te_us, close, hi, lo) on the 3 s grid t0..t1 inclusive, NaN where no bin, through lab3.bins.
"""
import importlib.util, os, sys

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.dirname(HERE)
TOOLS = os.path.dirname(TOOL)
FORENSICS = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.path.insert(0, TOOLS)


def _load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def target():
    return os.environ.get('EXIT_TARGET', 'engine')


def engine_path():
    return os.environ.get('EXIT_ENGINE', os.path.join(TOOL, 'exit_engine_v1.py'))


_cache = {}


def module():
    key = (target(), engine_path())
    if key not in _cache:
        _cache[key] = _load(os.path.join(HERE, 'oracle_exit_v1.py'), 'oracle_exit_v1') if target() == 'oracle' \
            else _load(engine_path(), 'exit_engine_under_test')
    return _cache[key]


def simulate(close, hi, lo, entry_bar, entry_px, side, row, units=None, monitor=None, t0_us=0, signal_us=None):
    return module().simulate(close, hi, lo, entry_bar, entry_px, side, row, units=units, monitor=monitor, t0_us=t0_us, signal_us=signal_us)


def engine():
    """engine-only calls (registry, cost, reader): the oracle has none of them"""
    return _load(engine_path(), 'exit_engine_under_test_2') if target() == 'oracle' else module()


def row(**kw):
    r = dict(id='PLANT', kind='B', unit='pct', stop=None, take=None, arm=None, give=None, time_limit_min=60, min_hold_min=None,
             early_stop=None, early_min=None, monitor='none', note='planted by TEST2')
    r.update(kw)
    return r
