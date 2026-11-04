"""labcore._rows (BUILD2, 23 Oct 2026): rows in either shape a tool hands over (a dict of equal-length columns, or a list of dicts) as
one form for the guards: columns() -> {name: np.ndarray}; canon_rows() -> sorted list of rows with floats by their bits (NaN = NaN)."""
import struct
import numpy as np


def columns(rows):
    """a COPY of every column (SKEPTIC 02-03: a guard's baseline is frozen the moment it is taken, a reused buffer cannot change it)"""
    if isinstance(rows, dict):
        cols = {k: np.array(v, copy=True) for k, v in rows.items()}
    else:
        rows = list(rows)
        keys = sorted({k for r in rows for k in r})
        cols = {k: np.asarray([r.get(k) for r in rows]) for k in keys}
    n = {len(v) for v in cols.values()}
    if len(n) > 1:
        raise ValueError('columns of different lengths: %s' % {k: len(v) for k, v in cols.items()})
    return cols


def _cell(x):
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return ('f', 'nan') if x != x else ('f', struct.unpack('<Q', struct.pack('<d', x))[0])
    if isinstance(x, (np.integer,)):
        return ('i', int(x))
    if isinstance(x, (np.bool_,)):
        return ('b', bool(x))
    return ('o', x)


def canon_rows(cols, mask=None):
    names = sorted(cols)
    n = len(cols[names[0]]) if names else 0
    idx = np.arange(n) if mask is None else np.nonzero(mask)[0]
    return sorted(tuple((k, _cell(cols[k][i])) for k in names) for i in idx)
