"""test_patch_s6_rel1.py: test_patch_s6_v1.py (33c67d5d206b3101, never edited) on i2g_patch_s6_rel1 and i2g_engine_rel1. Owner
STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Changed: only the two imports. The rest of
this text is test_patch_s6_v1.py's.
test_patch_s6_v1.py (speed twin S6, grader thread, 26 Oct 2026): i2g_patch_s6_v1 gives the same values as the modules' own functions.
Builds the store's modules (K.load()), keeps the originals, applies the patch to a stand-in engine module, then compares on random and edge
inputs: shift (day texts over 2024-2026, k in -3..3), day_of / utc_day (whole seconds, fractions, the last microsecond of a second, day
edges), and known_end_us (random loaded sets of 0-4 days around t, t at day edges and inside).
    python3 -B test_patch_s6_v1.py [N]"""
import os, sys, types
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import i2g_engine_rel1 as E2
import i2g_patch_s6_rel1 as P6


def main(N):
    k = E2.K.load(); S = k.S; AS = S.PROJECTION_BASE; AC = AS.AC
    o_shift, o_day, o_acshift, o_utc, o_ke = E2.shift, E2.day_of, AC.shift, AC.utc_day, S.known_end_us
    eng = types.ModuleType('eng'); eng.shift = E2.shift; eng.day_of = E2.day_of
    P6.patch(k, eng)
    assert E2.shift is not o_shift and AC.shift is not o_acshift and S.known_end_us is not o_ke and eng.shift is E2.shift
    rng = np.random.default_rng(20261026); bad = 0
    days = [o_shift('20240101', i) for i in range(0, 1100)]
    for _ in range(N):
        d = days[int(rng.integers(0, len(days)))]; kk = int(rng.integers(-3, 4))
        bad += E2.shift(d, kk) != o_shift(d, kk); bad += AC.shift(d, kk) != o_acshift(d, kk)
    t0 = 1704067200
    ts = []
    for _ in range(N):
        base = t0 + int(rng.integers(0, 1100)) * 86400
        r = rng.random()
        t = base + (0 if r < 0.2 else -1 if r < 0.3 else int(rng.integers(0, 86400)))
        f = rng.random()
        t = t + (0.0 if f < 0.3 else 0.9999995 if f < 0.35 else 0.999999 if f < 0.4 else 0.9999999 if f < 0.45 else float(rng.random()))
        ts.append(t)
    for t in ts:
        bad += E2.day_of(t) != o_day(t); bad += AC.utc_day(t) != o_utc(t)
    for t in ts:
        tu = int(round(t * 1e6))
        d0 = o_utc(tu / 1e6)
        loaded = {o_acshift(d0, j) for j in range(-1, int(rng.integers(-1, 4)))} if rng.random() < 0.9 else set()
        bad += S.known_end_us(loaded, tu) != o_ke(loaded, tu)
    print('patch_s6 vs own functions: %d shift, %d day, %d known_end cases, %d differ' % (2 * N, 2 * N, N, bad))
    return bad


if __name__ == '__main__':
    sys.exit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 50000) else 0)
