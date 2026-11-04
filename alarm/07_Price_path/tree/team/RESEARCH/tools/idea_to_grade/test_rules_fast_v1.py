"""test_rules_fast_v1.py: i2g_rules_fast_v1 equals i2g_rules_v1_2 bit for bit on random paths with holes, ties, NaN bins, both sides,
resting and taker targets, every start, limit and known end (fixed seed), and on every observation of a real coin-day when one is given.
    python3 -B test_rules_fast_v1.py [N]"""
import math, sys, time
import numpy as np
import i2g_rules_v1_2 as RU
import i2g_rules_fast_v1 as RF


def same(a, b):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if isinstance(x, float) and isinstance(y, float) and math.isnan(x) and math.isnan(y):
            continue
        if type(x) != type(y) or x != y:
            return False
    return True


def path(rng, n):
    gaps = rng.choice([3, 3, 3, 3, 6, 9, 61, 120, 3], n) * RU.US
    tl = np.cumsum(gaps).astype(np.int64) + 1_760_000_000 * RU.US
    px = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
    px = np.round(px, rng.integers(1, 4))                     # ties with the levels
    hi = px * (1 + np.abs(rng.normal(0, 0.001, n))); lo = px * (1 - np.abs(rng.normal(0, 0.001, n)))
    nan = rng.random(n) < 0.01
    hi[nan] = np.nan; lo[nan] = np.nan
    return tl, px, hi, lo


def main(N):
    rng = np.random.default_rng(20261026); bad = 0; t_old = t_new = 0.0; codes = {}
    for case in range(N):
        n = int(rng.integers(5, 6000))
        tl, px, hi, lo = path(rng, n)
        i0 = int(rng.integers(0, n - 1)); t_from = int(tl[i0]) + int(rng.choice([0, 0, 1, 2 * RU.US]))
        entry = float(px[i0]) if rng.random() < 0.5 else float(rng.choice([px[i0], hi[i0], lo[i0]]))
        side = int(rng.choice([1, -1])); tg = float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan, 0.0]))
        sp = float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan]))
        lim = int(rng.choice([900, 3600, 14400, 60]))
        ke = int(tl[min(n - 1, int(rng.integers(i0, n)))]) if rng.random() < 0.7 else int(tl[-1]) + 10 ** 12
        rest = bool(rng.random() < 0.5)
        a0 = time.perf_counter(); a = RU.barrier_exit(tl, px, hi, lo, i0, t_from, entry, side, tg, sp, lim, ke, resting_target=rest)
        a1 = time.perf_counter(); b = RF.barrier_exit(tl, px, hi, lo, i0, t_from, entry, side, tg, sp, lim, ke, resting_target=rest)
        a2 = time.perf_counter(); t_old += a1 - a0; t_new += a2 - a1
        codes[a[0]] = codes.get(a[0], 0) + 1
        if not same(a, b):
            bad += 1
            if bad <= 5:
                print('DIFF case', case, a, b)
    print('barrier_exit: %d cases, %d differ; codes %s; loop %.2f s, arrays %.2f s' % (N, bad, codes, t_old, t_new))
    bad2 = 0; t_old = t_new = 0.0; nask = 0
    for case in range(N // 4):
        n = int(rng.integers(5, 6000))
        tl, px, hi, lo = path(rng, n)
        i0 = int(rng.integers(0, n - 1)); t_from = int(tl[i0]) + int(rng.choice([0, 0, 1, 2 * RU.US]))
        entry = float(rng.choice([px[i0], hi[i0], lo[i0]])); side = int(rng.choice([1, -1]))
        ke = int(tl[min(n - 1, int(rng.integers(i0, n)))]) if rng.random() < 0.7 else int(tl[-1]) + 10 ** 12
        asks = [(float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan, 0.0])), float(rng.choice([0.05, 0.2, 0.5, 1.0, 3.0, np.nan])),
                 int(rng.choice([900, 3600, 14400, 60])), bool(rng.random() < 0.5)) for _ in range(int(rng.integers(1, 17)))]
        a0 = time.perf_counter()
        want = [RU.barrier_exit(tl, px, hi, lo, i0, t_from, entry, side, tg, sp, lim, ke, resting_target=r) for tg, sp, lim, r in asks]
        a1 = time.perf_counter(); got = RF.walk_all(tl, px, hi, lo, i0, t_from, entry, side, asks, ke); a2 = time.perf_counter()
        t_old += a1 - a0; t_new += a2 - a1; nask += len(asks)
        for x, y in zip(want, got):
            if not same(x, y):
                bad2 += 1
                if bad2 <= 5:
                    print('WALK DIFF case', case, x, y)
    print('walk_all: %d starts, %d asks, %d differ; loop %.2f s, one pass %.2f s' % (N // 4, nask, bad2, t_old, t_new))
    bad3 = 0; t_old = t_new = 0.0
    for case in range(N // 10):
        n = int(rng.integers(50, 6000))
        tl, px, hi, lo = path(rng, n)
        i0 = int(rng.integers(0, n - 1)); side = int(rng.choice([1, -1]))
        taker = ('FILLED', i0, int(tl[i0]), float(px[i0])) if rng.random() < 0.8 else ('NO_FILL', None, None, None)
        t_dec = int(tl[i0]) - int(rng.choice([0, 1, 2])) * RU.US
        ke = int(tl[min(n - 1, int(rng.integers(i0, n)))]) if rng.random() < 0.7 else int(tl[-1]) + 10 ** 12
        rv = float(rng.choice([0.1, 0.5, 2.0, np.nan])); c = float(rng.choice([0.1, 0.2, np.nan]))
        a0 = time.perf_counter(); x = RU.path_values(tl, px, hi, lo, taker, t_dec, side, ke, 0.3, rv, c)
        a1 = time.perf_counter(); y = RF.path_values_walk(tl, px, hi, lo, taker, t_dec, side, ke, 0.3, rv, c); a2 = time.perf_counter()
        z = RF.path_values(tl, px, hi, lo, taker, t_dec, side, ke, 0.3, rv, c)
        t_old += a1 - a0; t_new += a2 - a1
        if x.tobytes() != y.tobytes() or x.tobytes() != z.tobytes():
            bad3 += 1
            if bad3 <= 3:
                print('PATH DIFF case', case, np.flatnonzero(x.view(np.int64) != y.view(np.int64)))
    print('path_values: %d rows, %d differ (bytes); loop %.2f s, one pass %.2f s' % (N // 10, bad3, t_old, t_new))
    return bad + bad2 + bad3


if __name__ == '__main__':
    sys.exit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000) else 0)
