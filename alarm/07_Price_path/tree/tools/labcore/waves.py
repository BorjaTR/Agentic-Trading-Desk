"""labcore.waves (BUILD2, 23 Oct 2026): THE ONE wave module (LAB1 11:13:30Z). MOVED verbatim: waves, wave_weights from
team/RESEARCH/tools/bucket_proof/bucket_proof.py 2b615f53396155d0; by_wave (the by-wave bootstrap) from money_v1.py 3bb9bf378008aed5.
v2 (BUILD2 23 Oct, LEAD's step 2 spec sec 7, TEST1 L09b): by_wave's dead parameter drop_best is removed (any value but 0 is a TypeError);
without it the answer is the original's (move proof M2).
One event = one WAVE (fires of any coin within gap_s of the previous one); counts, shares and intervals by wave, never by fire row."""
import numpy as np


def waves(t, gap_s):
    """wave id per fire (in the input order): a fire more than gap_s after the previous fire (any coin) starts a new wave"""
    t = np.asarray(t, float); o = np.argsort(t, kind='mergesort'); ts = t[o]
    wid = np.cumsum(np.r_[1, np.diff(ts) > gap_s]) - 1; out = np.empty(len(t), int); out[o] = wid
    return out


def wave_weights(wave):
    """1 / (fires of the wave): every wave counts once in total"""
    u, inv, cnt = np.unique(wave, return_inverse=True, return_counts=True)
    return 1.0 / cnt[inv]


def by_wave(v, wave, month, rng, B=1000, drop_best=0):
    """mean of wave means, its 90 pct whole-wave interval, the waves and trades. v2 (LEAD/LABCORE_STEP2_SPEC_V1 b75998c5 sec 7, TEST1
    L09b): the dead parameter drop_best is REMOVED (the moved original took it and ignored it); a caller passing it gets a TypeError and
    drops the best days itself by setting their values to NaN (as money_v1 does). month is unused, kept for the callers' signature.
    drop_best=0 is still accepted (TEST1 L09b calls it so); any other value raises the TypeError the spec names."""
    if drop_best:
        raise TypeError('by_wave: drop_best was removed (it was never applied); set the best days to NaN before the call')
    ok = np.isfinite(v)
    if not ok.any():
        return dict(n=0, waves=0, mean=np.nan, lo=np.nan, hi=np.nan)
    v, wave = v[ok], wave[ok]; u, inv = np.unique(wave, return_inverse=True)
    wm = np.bincount(inv, weights=v) / np.bincount(inv); bs = [wm[rng.integers(0, len(u), len(u))].mean() for _ in range(B)]
    return dict(n=int(ok.sum()), waves=len(u), mean=float(wm.mean()), lo=float(np.percentile(bs, 5)), hi=float(np.percentile(bs, 95)))
