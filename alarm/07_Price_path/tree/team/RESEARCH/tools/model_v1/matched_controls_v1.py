"""SCOUT matched_controls_v1 (22 Oct 2026; the controls for A02 strategy reads, QUANT's strategy-build skill v0.5 read rule 1).
For one fire: K matched random MOMENTS on the same coin, judged FORWARD from their own time like the fire:
  - near in time: the same UTC day and within NEAR_S of the fire;
  - away from alarms: at least AWAY_S from every A01 onset and every A02 fire of that coin;
  - similar recent range: the log range (max - min of the 3 s closes) over the RANGE_S before the moment within LO..HI x the fire's;
  - on the fire's 5 s grid; a fixed seed. The SIDE of a control = the sign of its own move over the RANGE_S before it (the push it had),
    so a fade or a ride is judged the same way as at a fire.
Nothing after a moment is read here (the money is read later by the caller, forward from the moment)."""
import numpy as np

NEAR_S, AWAY_S, RANGE_S, LO, HI, STEP = 6 * 3600, 1800, 1800, 0.75, 1.33, 5
NAN = float('nan')


def closes(te_us, px, ts):
    """the close of the last bin with te <= t, NaN when none (episode_blocks.Ep.close's rule)"""
    i = np.searchsorted(te_us, np.round(np.asarray(ts, float) * 1_000_000).astype(np.int64), side='right') - 1
    v = np.where(i >= 0, px[np.maximum(i, 0)] if len(px) else NAN, NAN)
    return np.where(v > 0, v, NAN)


def recent(te_us, px, t):
    """(log range, signed log move) of the closes over (t - RANGE_S, t]: the bins ending in the window plus the close at its start"""
    a = int(np.searchsorted(te_us, int(round((t - RANGE_S) * 1_000_000)), side='right'))
    b = int(np.searchsorted(te_us, int(round(t * 1_000_000)), side='right'))
    c0 = closes(te_us, px, [t - RANGE_S])[0]; seg = px[a:b]; seg = seg[seg > 0]
    if not np.isfinite(c0) or len(seg) == 0:
        return NAN, NAN
    lg = np.log(np.concatenate(([c0], seg)))
    return float(lg.max() - lg.min()), float(lg[-1] - lg[0])


def candidates(t_fire, d0, avoid):
    """moments on the fire's 5 s grid, inside the UTC day starting d0, within NEAR_S of the fire, AWAY_S from every time in avoid"""
    c = t_fire + STEP * np.arange(-(NEAR_S // STEP), NEAR_S // STEP + 1)
    c = c[(c >= d0) & (c < d0 + 86400)]
    av = np.sort(np.asarray(avoid, float))
    if len(av):
        i = np.searchsorted(av, c - AWAY_S, side='right'); j = np.searchsorted(av, c + AWAY_S, side='left')
        c = c[i == j]                                                # nothing in (c - AWAY_S, c + AWAY_S)
    return c.astype(np.int64)


def draw(te_us, px, t_fire, d0, avoid, K, rng):
    """-> (times, sides) of up to K range-matched moments, sorted; none when the fire's own range is unknown or 0"""
    r0, _ = recent(te_us, px, t_fire)
    if not (np.isfinite(r0) and r0 > 0):
        return np.zeros(0, np.int64), np.zeros(0, int)
    c = candidates(t_fire, d0, avoid)
    if len(c) == 0:
        return np.zeros(0, np.int64), np.zeros(0, int)
    rm = np.array([recent(te_us, px, t) for t in c])
    ok = np.isfinite(rm[:, 0]) & (rm[:, 0] >= LO * r0) & (rm[:, 0] <= HI * r0) & np.isfinite(rm[:, 1]) & (rm[:, 1] != 0)
    k = np.flatnonzero(ok)
    if len(k) > K:
        k = np.sort(rng.choice(k, K, replace=False))
    return c[k], np.sign(rm[k, 1]).astype(int)
