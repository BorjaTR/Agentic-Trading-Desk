"""test_rules_fast_v3.py: i2g_rules_fast_v3.walk_all equals i2g_rules_fast_v2.walk_all (and v1) bit for bit (fixed seed): random paths
with holes, ties, NaN bins, both sides, resting and taker asks, odd starts (a start bin after t_from, a NaN entry, a known end before the
start); and path_values_walk byte-equal to i2g_rules_v1_2.path_values. Reports whether numba compiled the walk.
    python3 -B test_rules_fast_v3.py [N]"""
import sys, time
import numpy as np
import i2g_rules_v1_2 as RU
import i2g_rules_fast_v1 as F1
import i2g_rules_fast_v2 as F2
import i2g_rules_fast_v3 as F3
from test_rules_fast_v1 import same, path


def main(N):
    rng = np.random.default_rng(20261027); bad = 0; nask = 0; t1 = t2 = 0.0; codes = {}
    tl, px, hi, lo = path(rng, 50)
    F2.walk_all(tl, px, hi, lo, 1, int(tl[1]), float(px[1]), 1, [(0.5, 0.5, 900, False)], int(tl[-1]))      # compile once
    for case in range(N):
        n = int(rng.integers(5, 6000))
        tl, px, hi, lo = path(rng, n)
        i0 = int(rng.integers(0, n - 1))
        t_from = int(tl[i0]) + int(rng.choice([0, 0, 1, 2 * RU.US, -5 * RU.US]))
        entry = float(rng.choice([px[i0], hi[i0], lo[i0]])) if rng.random() < 0.97 else np.nan
        side = int(rng.choice([1, -1]))
        r = rng.random()
        ke = int(tl[min(n - 1, int(rng.integers(i0, n)))]) if r < 0.6 else int(tl[-1]) + 10 ** 12 if r < 0.9 \
            else int(tl[max(0, i0 - int(rng.integers(0, 5)))]) - int(rng.integers(0, 3)) * RU.US
        asks = [(float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan, 0.0])), float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan])),
                 int(rng.choice([900, 3600, 14400, 60])), bool(rng.random() < 0.5)) for _ in range(int(rng.integers(1, 17)))]
        a0 = time.perf_counter(); want = F2.walk_all(tl, px, hi, lo, i0, t_from, entry, side, asks, ke)
        a1 = time.perf_counter(); got = F3.walk_all(tl, px, hi, lo, i0, t_from, entry, side, asks, ke); a2 = time.perf_counter()
        t1 += a1 - a0; t2 += a2 - a1; nask += len(asks)
        for x, y in zip(want, got):
            codes[x[0]] = codes.get(x[0], 0) + 1
            if not same(x, y):
                bad += 1
                if bad <= 5:
                    print('WALK DIFF case', case, x, y)
    print('walk_all v3 vs v2: %d starts, %d asks, %d differ; codes %s; v2 %.2f s, v3 %.2f s; compiled %s'
          % (N, nask, bad, codes, t1, t2, F2.numba is not None))
    bad3 = 0
    for case in range(N // 10):
        n = int(rng.integers(50, 6000))
        tl, px, hi, lo = path(rng, n)
        i0 = int(rng.integers(0, n - 1)); side = int(rng.choice([1, -1]))
        taker = ('FILLED', i0, int(tl[i0]), float(px[i0])) if rng.random() < 0.8 else ('NO_FILL', None, None, None)
        t_dec = int(tl[i0]) - int(rng.choice([0, 1, 2])) * RU.US
        ke = int(tl[min(n - 1, int(rng.integers(i0, n)))]) if rng.random() < 0.7 else int(tl[-1]) + 10 ** 12
        rv = float(rng.choice([0.1, 0.5, 2.0, np.nan])); c = float(rng.choice([0.1, 0.2, np.nan]))
        x = RU.path_values(tl, px, hi, lo, taker, t_dec, side, ke, 0.3, rv, c)
        y = F3.path_values_walk(tl, px, hi, lo, taker, t_dec, side, ke, 0.3, rv, c)
        if x.tobytes() != y.tobytes():
            bad3 += 1
            if bad3 <= 3:
                print('PATH DIFF case', case, np.flatnonzero(x.view(np.int64) != y.view(np.int64)))
    print('path_values_walk v3 vs i2g_rules_v1_2.path_values: %d rows, %d differ (bytes)' % (N // 10, bad3))
    return bad + bad3


if __name__ == '__main__':
    sys.exit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000) else 0)
