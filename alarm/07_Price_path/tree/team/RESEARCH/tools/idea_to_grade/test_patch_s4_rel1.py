"""test_patch_s4_rel1.py: test_patch_s4_v1.py (0bb36a9b269a72d6, never edited) on the rel1 chain: the kernels of idea_to_grade_v3_2_rel1
(i2g_patch_s4_v1 itself is unchanged). Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only").
Changed: only the import of idea_to_grade_v3_2. The rest of this text is test_patch_s4_v1.py's.
test_patch_s4_v1.py: i2g_patch_s4_v1 gives the same values as the modules' own functions (fixed seed):
  calendar  day_of, month_of, part_of, same_window on random times and on every day edge of the window +- 0, 1e-7, 5e-7, 1e-6, 0.5 s
            (int, float, numpy float); _day_start and days_for on every day text; NaN raises the same error
  ladder    ladder_stamp's offer_t, heat_t, end, offer0_t, heat0_t equal LD.ladder's (values and dtype) on random paths with gaps, NaN
            bins, both sides, fills near the end of the data and holds of 0 s to 4 h
    cd <idea_to_grade folder> && nice -n 10 python3 -B test_patch_s4_v1.py [N]"""
import os, sys, types
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import idea_to_grade_v3_2_rel1 as G
import i2g_patch_s4_v1 as P4


def outcome(f, *a):
    try:
        return ('ok', f(*a))
    except Exception as e:                                          # noqa: BLE001
        return ('err', type(e).__name__, str(e))


def main(N):
    E = G.warm(); k = E.K.load()
    mods = {id(k.D): k.D, id(k.DP): k.DP}.values()
    orig = {id(m): (m.day_of, m.month_of, m._day_start, m.part_of, m.same_window, m.days_for) for m in mods}
    split = k.D.split_from(k.gates.WINDOWS)
    rng = np.random.default_rng(20261026)
    t0 = 1735689600.0                                               # 2025-01-01, a range around the window
    ts = list(t0 + rng.uniform(-400, 800, N) * 86400)
    for d in range(-400, 800):
        e = t0 + d * 86400
        for off in (0, 1e-7, 5e-7, 1e-6, 0.5, 0.9999994, 0.9999995, 0.9999996, 0.999999, 0.9999999):
            ts += [e + off, e - off]
        ts += [int(e), int(e) - 1, np.float64(e) - 1e-6]
    days = sorted({k.D.day_of(t) for t in ts})
    want = {}
    for m in mods:
        o = orig[id(m)]
        want[id(m)] = ([outcome(o[0], t) for t in ts], [outcome(o[1], t) for t in ts], [outcome(o[2], d) for d in days],
                       [outcome(o[3], t, split) for t in ts[:20000]], [outcome(o[4], t, t - 3 * 86400, 14466.0, split) for t in ts[:20000]])
    want_nan = [outcome(orig[id(m)][0], float('nan')) for m in mods]
    P4.patch(k, ladder=False)
    bad = 0
    for m in mods:
        got = ([outcome(m.day_of, t) for t in ts], [outcome(m.month_of, t) for t in ts], [outcome(m._day_start, d) for d in days],
               [outcome(m.part_of, t, split) for t in ts[:20000]], [outcome(m.same_window, t, t - 3 * 86400, 14466.0, split) for t in ts[:20000]])
        for name, a, b in zip(('day_of', 'month_of', '_day_start', 'part_of', 'same_window'), want[id(m)], got):
            nb = sum(x != y for x, y in zip(a, b)); bad += nb
            print('calendar %s %s: %d values, %d differ' % (m.__name__, name, len(a), nb))
    got_nan = [outcome(m.day_of, float('nan')) for m in mods]
    print('NaN same error:', got_nan == want_nan); bad += got_nan != want_nan
    # ladder
    LD = k.LD; full = LD.ladder; lite = P4.ladder_stamp(LD); US = LD.US; badl = 0; n_end = 0
    for case in range(N // 20):
        n = int(rng.integers(2, 9000))
        gaps = rng.choice([3, 3, 3, 3, 6, 9, 61, 120, 3], n) * US
        tl = (np.cumsum(gaps) + 1_760_000_000 * US).astype(np.int64); te = tl.copy()
        px = 100 * np.exp(np.cumsum(rng.normal(0, 0.002, n)))
        hi = px * (1 + np.abs(rng.normal(0, 0.001, n))); lo = px * (1 - np.abs(rng.normal(0, 0.001, n)))
        nan = rng.random(n) < 0.01; hi[nan] = np.nan; lo[nan] = np.nan
        pv = types.SimpleNamespace(tl=tl, te=te, px=px, hi=hi, lo=lo)
        i = int(rng.integers(0, n)); f = types.SimpleNamespace(t_us=int(tl[i]), i=i, px=float(px[i]), status='FILLED')
        side = int(rng.choice([1, -1])); hold = int(rng.choice([0, 60, 900, 3600, 14400]))
        a = full(pv, f, side, hold); b = lite(pv, f, side, hold); n_end += a['end']
        for key in ('offer_t', 'heat_t'):
            if not (np.array_equal(a[key], b[key]) and a[key].dtype == b[key].dtype):
                badl += 1
        for key in ('end', 'offer0_t', 'heat0_t', 'n', 't_fill', 't_end', 'edge'):
            if a[key] != b[key] or type(a[key]) != type(b[key]):
                badl += 1
    print('ladder_stamp: %d paths (%d past the data end), %d differ' % (N // 20, n_end, badl))
    return bad + badl


if __name__ == '__main__':
    sys.exit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 200000) else 0)
