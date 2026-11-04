"""labcore.v2_7.rows (labcore V2_7 CANDIDATE; ctxprof_shared, 25 Oct 2026; context_fix2's request 2). The FIXED canonical row form of the
lookahead guards. labcore/_rows.py (V2_6, pinned: never edited) writes a NaN cell as ('f', 'nan') beside ('f', <int bits>), so canon_rows
raises TypeError when two rows differ by NaN versus a number in one column (met in Context's H2 controls); a None beside a value of the
same column has the same fault. Here a NaN is ('fnan', 0) and a None is ('none', 0): every cell compares, the order of every row without
NaN or None is unchanged (same tags, same values). LAB1 request: the same two lines in labcore/_rows.py _cell, in labcore V3.
  canon_rows(cols, mask=None) -> sorted list of rows with floats by their bits; columns re-exported from labcore._rows (unchanged)."""
import struct
import numpy as np

from .._rows import columns                                             # noqa: F401  unchanged, re-exported


def _cell(x):
    if x is None:
        return ('none', 0)
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return ('fnan', 0) if x != x else ('f', struct.unpack('<Q', struct.pack('<d', x))[0])
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
