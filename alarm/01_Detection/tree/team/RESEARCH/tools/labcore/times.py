"""labcore.times (BUILD2, 23 Oct 2026): EVERY VALUE CARRIES ITS TIMES (TOOL_DESIGN V4.2 0d (f); spec LEAD/LABCORE_STEP2_SPEC_V1.md
b75998c5 sec 4). check_times(rows, required, windows) refuses rows that do not say when they are true and when they could be known:
every required column present, int64 (never float, never NaN); each named window (start_col, end_col) has start <= end; when the rows
carry horizon_end_us (an outcome) known_at_us >= horizon_end_us (an outcome is never known before its horizon ends)."""
import numpy as np
from ._rows import columns


def check_times(rows, required=('as_of_us', 'known_at_us'), windows=()):
    c = columns(rows)
    for k in list(required) + [x for w in windows for x in w] + (['horizon_end_us'] if 'horizon_end_us' in c else []):
        if k not in c:
            raise ValueError('times: column %s missing' % k)
        if c[k].dtype != np.int64:
            raise ValueError('times: column %s is %s, not int64 microseconds (SKEPTIC 02-10)' % (k, c[k].dtype))
        if c[k].size and (c[k] == np.iinfo(np.int64).min).any():
            raise ValueError('times: column %s holds the int64 missing-time sentinel' % k)
    for a, b in windows:
        bad = c[a] > c[b]
        if bad.any():
            i = int(np.nonzero(bad)[0][0])
            raise ValueError('times: row %d window %s %d after %s %d' % (i, a, int(c[a][i]), b, int(c[b][i])))
    if 'horizon_end_us' in c:
        if 'known_at_us' not in c:
            raise ValueError('times: an outcome without known_at_us')
        bad = c['known_at_us'] < c['horizon_end_us']
        if bad.any():
            i = int(np.nonzero(bad)[0][0])
            raise ValueError('times: row %d outcome known_at %d before its horizon end %d' % (i, int(c['known_at_us'][i]),
                                                                                             int(c['horizon_end_us'][i])))
    return True
