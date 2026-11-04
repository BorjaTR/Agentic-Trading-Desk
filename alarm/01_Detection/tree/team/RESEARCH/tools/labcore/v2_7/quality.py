"""labcore.v2_7.quality (LAB1, 25 Oct 2026; LAB1_REQUESTS_V1 item 7): THE one rule that says whether a lab3 clock cell is KNOWN. Before it,
idea_to_grade.detect (e == 0) and event_cause (e not 0 and not 255) disagreed on a finite value whose reason byte is ABSENT (255).
  known(v, e=None, a=None, o=None, k=None, col_us=None) -> bool array, the shape of v. A cell is KNOWN when ALL hold:
    v finite;
    e == 0                        (a reason id, or the ABSENT byte 255 beside a finite value, is not known: strict, one rule);
    a >= 0, o >= 0                (ABSENT ages and offsets are negative);
    k set (not INT64_MIN) and k <= col_us   (known_at no later than the column's own time; col_us broadcasts over rows).
  A field passed as None is not checked: the part did not list it (a part that lists it must pass it).
  counts(v, ...) -> {'cells', 'known', 'nonfinite', 'reason', 'age', 'offset', 'late'}: why cells are not known, each cell counted once by
  the FIRST failing rule in the order above. Reads nothing, writes nothing."""
import numpy as np

INT64_MIN = np.iinfo(np.int64).min
ORDER = ('nonfinite', 'reason', 'age', 'offset', 'late')


def _fails(v, e=None, a=None, o=None, k=None, col_us=None):
    v = np.asarray(v, float)
    f = {'nonfinite': ~np.isfinite(v)}
    f['reason'] = (np.asarray(e) != 0) if e is not None else np.zeros(v.shape, bool)
    f['age'] = (np.asarray(a) < 0) if a is not None else np.zeros(v.shape, bool)
    f['offset'] = (np.asarray(o) < 0) if o is not None else np.zeros(v.shape, bool)
    if k is not None:
        if col_us is None:
            raise ValueError('quality.known: k given without the column times col_us: refused')
        kk = np.asarray(k, np.int64)
        f['late'] = (kk == INT64_MIN) | (kk > np.broadcast_to(np.asarray(col_us, np.int64), kk.shape))
    else:
        f['late'] = np.zeros(v.shape, bool)
    for n in ORDER:
        if f[n].shape != v.shape:
            raise ValueError('quality.known: field %s shape %s, v %s: refused' % (n, f[n].shape, v.shape))
    return v, f


def known(v, e=None, a=None, o=None, k=None, col_us=None):
    v, f = _fails(v, e, a, o, k, col_us)
    bad = np.zeros(v.shape, bool)
    for n in ORDER:
        bad |= f[n]
    return ~bad


def counts(v, e=None, a=None, o=None, k=None, col_us=None):
    v, f = _fails(v, e, a, o, k, col_us)
    out = {'cells': int(v.size)}; seen = np.zeros(v.shape, bool)
    for n in ORDER:
        hit = f[n] & ~seen; out[n] = int(hit.sum()); seen |= f[n]
    out['known'] = int((~seen).sum())
    return out
