"""labcore.lookahead (BUILD2, 23 Oct 2026): THE THREE LOOKAHEAD GUARDS (TOOL_DESIGN V4.2 0d (g); spec LEAD/LABCORE_STEP2_SPEC_V1.md
b75998c5 sec 3). Each runs in a tool's tests AND on its first real run; a tool without a passing LOOKAHEAD row is not used.
  prefix_check(fn, data, t_cut_us)        the tool on data cut at t_cut gives, for every row with known_at_us <= t_cut, the same row
                                          (values AND times) as on the full data; -> the differing rows ([] = pass)
  future_plant_check(fn, data, plant_fn, t_us)  a huge value planted just after t_us changes no row with known_at_us <= t_us
  join_guard(known_at_us, decision_us, what)    refuses (LookaheadError) any value known after its decision time, and a missing known_at
fn(data) returns rows (a dict of columns or a list of dicts) carrying known_at_us. Rows are compared as multisets: floats by their bits
(NaN equal NaN), every column. cut(data, t_cut_us) defaults to keeping the input rows whose known_at_us (AVAILABILITY, never event
time) is <= t_cut; input without known_at_us is refused: pass cut=. v2 (SKEPTIC REVIEW 02-01, 02-02, 02-03): times validated as finite
int64 on both sides of every comparison; v3 (OUTSIDE C2-04, C2-06): cutoffs validated, float clocks refused; every run gets its own deep copy of the input and its output is copied at once."""
import numpy as np
from ._rows import canon_rows, columns


class LookaheadError(Exception):
    pass


def valid_times(a, what):
    """SKEPTIC 02-02: times are finite signed int64 microseconds; NaN, inf, floats, other widths and the int64 minimum (a missing-time
    sentinel) are refused"""
    a = np.asarray(a)
    if a.dtype != np.int64:                                             # C2-06: no float clock, not even an integral one
        raise LookaheadError('%s: times must be int64 microseconds, got %s' % (what, a.dtype))
    if a.size and (a == np.iinfo(np.int64).min).any():
        raise LookaheadError('%s: a missing-time sentinel (int64 minimum) is refused' % what)
    return a


def default_cut(data, t_cut_us):
    """SKEPTIC 02-01: cuts by AVAILABILITY: keeps the rows of every column-dict whose known_at_us <= t_cut. Data without a known_at_us
    column is refused: pass cut= (an adapter that says when each input became available, delayed arrivals included)"""
    def one(tbl):
        c = columns(tbl)
        if 'known_at_us' not in c:
            raise LookaheadError('default_cut: input without known_at_us: pass cut= with the availability rule (never event time)')
        keep = valid_times(c['known_at_us'], 'input known_at_us') <= t_cut_us
        return {k: v[keep] for k, v in c.items()}
    if data and all(isinstance(v, dict) for v in data.values()):
        return {k: one(v) for k, v in data.items()}
    return one(data)


def _known(cols):
    if 'known_at_us' not in cols:
        raise LookaheadError('rows carry no known_at_us column: a value without its known_at is not used')
    return valid_times(cols['known_at_us'], 'output known_at_us')


def _diff(a_cols, b_cols, t_us):
    ka, kb = _known(a_cols), _known(b_cols)
    ra = canon_rows(a_cols, ka <= t_us); rb = canon_rows(b_cols, kb <= t_us)
    if ra == rb:
        return []
    sa, sb = {}, {}
    for r in ra:
        sa[r] = sa.get(r, 0) + 1
    for r in rb:
        sb[r] = sb.get(r, 0) + 1
    out = [('only_full', dict(r)) for r, n in sa.items() if n > sb.get(r, 0)]
    out += [('only_other', dict(r)) for r, n in sb.items() if n > sa.get(r, 0)]
    return sorted(out, key=lambda x: repr(x))


def _isolated(data):
    """a deep copy of the input for each run (SKEPTIC 02-03: a function that changes its input cannot change the other run's)"""
    import copy
    return copy.deepcopy(data)


def _cutoff(t, what):
    """C2-04: a cutoff is one int64 microsecond time (a Python int or numpy integer); NaN, inf, floats and the sentinel are refused"""
    if isinstance(t, (bool, np.bool_)) or not isinstance(t, (int, np.integer)):
        raise LookaheadError('%s: cutoff must be an int64 microsecond time, got %r' % (what, t))
    if not (np.iinfo(np.int64).min < int(t) <= np.iinfo(np.int64).max):     # D01b-03: inside signed int64, sentinel excluded
        raise LookaheadError('%s: cutoff %r is outside signed int64 or the missing-time sentinel' % (what, t))
    return int(t)


def prefix_check(fn, data, t_cut_us, cut=None):
    t_cut_us = _cutoff(t_cut_us, 'prefix_check')
    full = columns(fn(_isolated(data)))
    part = columns(fn((cut or default_cut)(_isolated(data), t_cut_us)))
    return _diff(full, part, t_cut_us)


def future_plant_check(fn, data, plant_fn, t_us):
    t_us = _cutoff(t_us, 'future_plant_check')
    full = columns(fn(_isolated(data)))
    planted = columns(fn(plant_fn(_isolated(data), t_us)))
    return _diff(full, planted, t_us)


def join_guard(known_at_us, decision_us, what=''):
    """refuses any value known after its decision time; both sides must be finite int64 microseconds (SKEPTIC 02-02: NaN decision,
    -inf known_at and missing-time sentinels never pass)"""
    k = valid_times(np.atleast_1d(known_at_us), '%s known_at_us' % (what or 'join'))
    d = valid_times(np.atleast_1d(decision_us), '%s decision_us' % (what or 'join'))
    k, d = np.broadcast_arrays(k, d)
    bad = k > d
    if bad.any():
        i = int(np.nonzero(bad)[0][0])
        raise LookaheadError('%s: row %d: known_at %d > decision %d (%d rows refused)' % (what or 'join', i, int(k[i]), int(d[i]),
                                                                                       int(bad.sum())))
    return True
