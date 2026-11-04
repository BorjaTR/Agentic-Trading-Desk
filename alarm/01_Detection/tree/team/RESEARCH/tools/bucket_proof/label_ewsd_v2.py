"""LABEL_EWSD_V2 (QUANT, 23 Oct 2026; STRATEGY RULING 13:36:02Z on OUTSIDE S05 52e617c5, all 6 accepted; ASK STRATEGY-133602). V1 992555f9
(bucket_proof.ewsd) stays as written for its receipts; V2 is a new label version, this module is its one home. The label is a
retrospective BINANCE-PATH opportunity description scaled by a frozen cost (rule 4): not fill proof, not HL payoff; money only through
exit_engine + labcore.costs. Per fire and side, from the stored STAMP ladder (alarm_stamp.read: first touches of offer / heat at 0.1 k pct,
k = 1..25, seconds from the fill; NaN = not within the known path), decision minute 0, hold H.
  (1) a target above the ladder's top (2.5 pct) is OUT_OF_RANGE, never capped; a target rounds UP to the next ladder level.
  (2) heat is an INTERVAL [highest rung touched, next rung) (the top rung touched: [2.5, inf)); a heat limit holds only when the whole
      interval satisfies it (the limit, in effect, rounds DOWN); an interval across a limit is UNDECIDED_BOUND. Heat touched in the same
      second as the target counts as before it (adverse first).
  (3) WAIT is a descriptive hindsight annotation: never a decision target (decision_target: ENTER 1; WAIT, SKIP, DEAD 0).
  (5) a missing price interval before the deciding touch makes the row UNDECIDED_GAP unless the class was settled before the gap; DEAD
      needs the whole hold covered; coverage not supplied (NaN) = UNKNOWN_PATH; a path known for less than H and not settled = UNKNOWN_PATH.
  (6) delay, hold, fill step, gap and the cost model are settings carried with their sha16 (required keys below); the outcome is known at
      the fire + delay + fill wait + hold (alarm_stamp's known_at), never earlier.
Classes: ENTER WAIT SKIP DEAD (decided), NA (not filled), OUT_OF_RANGE, UNDECIDED_BOUND, UNDECIDED_GAP, UNKNOWN_PATH (undecided)."""
import numpy as np

VERSION = 'LABEL_EWSD_V2'
LEVELS = np.round(np.arange(1, 26) * 0.1, 10)                                     # the stored rungs, pct
TOP = float(LEVELS[-1])
DECIDED = ('ENTER', 'WAIT', 'SKIP', 'DEAD')
UNDECIDED = ('NA', 'OUT_OF_RANGE', 'UNDECIDED_BOUND', 'UNDECIDED_GAP', 'UNKNOWN_PATH')
REQUIRED = ('version', 'offer_c', 'enter_heat_c', 'wait_heat_c', 'dead_c', 'hold_min', 'delay_s', 'fill_step_s', 'gap_s', 'cost_model', 'cost_sha16')
EPS = 1e-9


def check_settings(lab):
    miss = [k for k in REQUIRED if k not in lab]
    if miss or lab['version'] != VERSION:
        raise ValueError('%s settings: missing %s or version %r: refused (rule 6: every clock and the cost model named)' % (VERSION, miss, lab.get('version')))

    for key in ('offer_c', 'enter_heat_c', 'wait_heat_c', 'dead_c', 'hold_min', 'fill_step_s'):
        value = float(lab[key])
        if not np.isfinite(value) or value <= 0:
            raise ValueError('%s must be finite and positive' % key)
    for key in ('delay_s', 'gap_s'):
        value = float(lab[key])
        if not np.isfinite(value) or value < 0:
            raise ValueError('%s must be finite and nonnegative' % key)
    sha = lab['cost_sha16']
    if not isinstance(sha, str) or len(sha) != 16 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('cost_sha16 must be 16 lowercase hexadecimal characters')
    if not isinstance(lab['cost_model'], str) or not lab['cost_model'].strip():
        raise ValueError('cost_model must name the frozen model')


def up_index(x):
    """the smallest rung >= x -> index, -1 when x is above the top (OUT_OF_RANGE, never capped)"""
    x = np.asarray(x, float); i = np.searchsorted(LEVELS, x - EPS)
    return np.where(x > TOP + EPS, -1, np.minimum(i, len(LEVELS) - 1))


def interval(T, upto):
    """the interval of the largest excursion touched at or before 'upto' seconds: (lo, hi) with lo = the highest rung touched (0 if none)
    and hi = the next rung (inf when the top was touched)"""
    T = np.asarray(T, float); upto = np.asarray(upto, float)[:, None]
    hit = np.isfinite(T) & (T <= upto); k = np.where(hit.any(1), np.argmax(np.where(hit, np.arange(len(LEVELS)), -1), 1), -1)
    lo = np.where(k >= 0, LEVELS[np.maximum(k, 0)], 0.0)
    hi = np.where(k < 0, LEVELS[0], np.where(k >= len(LEVELS) - 1, np.inf, LEVELS[np.minimum(k + 1, len(LEVELS) - 1)]))
    return lo, hi


def first_above(T, x):
    """seconds of the first touch that ESTABLISHES an excursion above x (the smallest rung > x touched), inf if none / x above the top"""
    T = np.asarray(T, float); x = np.asarray(x, float); out = np.full(len(T), np.inf)
    for i in range(len(LEVELS)):                                                   # 25 columns, vectorised over rows
        m = (LEVELS[i] > x + EPS) & np.isfinite(T[:, i])
        out = np.where(m, np.minimum(out, T[:, i]), out)
    return out


def ewsd_v2(OT, HT, filled, known_s, c, lab, first_gap_s):
    """-> (classes, heat_lo, heat_hi): heat before the target as an interval (NaN when the target was not reached). first_gap_s: seconds
    from the fill to the first missing price interval (inf = the whole hold verified covered, NaN = coverage unknown)"""
    check_settings(lab)
    OT = np.asarray(OT, float); HT = np.asarray(HT, float); n = len(OT); r = np.arange(n); hold = 60.0 * float(lab['hold_min'])
    c = np.asarray(c, float); known = np.asarray(known_s, float); gap = np.asarray(first_gap_s, float)
    if OT.shape != (n, len(LEVELS)) or HT.shape != OT.shape:
        raise ValueError('touch ladders must have exactly 25 rungs per row')
    if c.shape != (n,) or not np.all(np.isfinite(c)) or np.any(c <= 0):
        raise ValueError('cost must be finite and positive for every row')
    if known.shape != (n,) or not np.all(np.isfinite(known)) or np.any(known < 0):
        raise ValueError('known path length must be finite and nonnegative')
    if gap.shape != (n,) or np.any(gap < 0):
        raise ValueError('first gap must be nonnegative, infinity or unknown')
    tgt = float(lab['offer_c']) * c; io = up_index(tgt); oor = io < 0
    to = np.where(oor, np.nan, OT[r, np.maximum(io, 0)]); reached = np.isfinite(to) & (to <= hold)
    lo, hi = interval(HT, np.where(reached, to, -1.0))
    e, w, d = float(lab['enter_heat_c']) * c, float(lab['wait_heat_c']) * c, float(lab['dead_c']) * c
    cls_r = np.where(hi <= e + EPS, 'ENTER', np.where((lo > e + EPS) & (hi <= w + EPS), 'WAIT', np.where(lo > w + EPS, 'SKIP', 'UNDECIDED_BOUND')))
    t_skip = first_above(HT, w)                                                     # heat > 3c established: SKIP whatever comes later
    olo, ohi = interval(OT, np.full(n, hold)); hlo, hhi = interval(HT, np.full(n, hold))
    cls_u = np.where((olo > d + EPS) | (hlo > d + EPS), 'SKIP', np.where((ohi <= d + EPS) & (hhi <= d + EPS), 'DEAD', 'UNDECIDED_BOUND'))
    settle = np.where(reached, np.where(cls_r == 'SKIP', np.minimum(to, t_skip), to),                 # when the class could no longer change
                      np.where(np.isfinite(t_skip) & (t_skip <= hold), t_skip, hold))
    cls = np.where(reached, cls_r, np.where(np.isfinite(t_skip) & (t_skip <= hold), 'SKIP', cls_u))
    cls = np.where(~reached & ~(np.isfinite(t_skip) & (t_skip <= hold)) & (known < hold), 'UNKNOWN_PATH', cls)
    cls = np.where(np.isnan(gap), 'UNKNOWN_PATH', np.where(gap < settle, 'UNDECIDED_GAP', cls))
    cls = np.where(oor, 'OUT_OF_RANGE', cls)
    cls = np.where(np.asarray(filled) == 1, cls, 'NA').astype(object)
    return cls, np.where(reached, lo, np.nan), np.where(reached, hi, np.nan)


def outcome4_v2(ride, fade):
    """four-class outcome: GOOD means ENTER only (rule 3: WAIT is never a target); UNDECIDED when either side is not decided"""
    ride = np.asarray(ride, object); fade = np.asarray(fade, object); rg = ride == 'ENTER'; fg = fade == 'ENTER'
    out = np.where(rg & ~fg, 'RIDE_GOOD', np.where(fg & ~rg, 'FADE_GOOD', np.where((ride == 'DEAD') & (fade == 'DEAD'), 'DEAD', 'BOTH_BAD')))
    return np.where(np.isin(ride, DECIDED) & np.isin(fade, DECIDED), out, 'UNDECIDED').astype(object)


def decision_target(cls):
    """what a decision learns: ENTER 1, WAIT / SKIP / DEAD 0 (WAIT stays a hindsight annotation), NaN when undecided"""
    cls = np.asarray(cls, object)
    return np.where(cls == 'ENTER', 1.0, np.where(np.isin(cls, ('WAIT', 'SKIP', 'DEAD')), 0.0, np.nan))


def path_first_gap(cache, coin, t_fill_s, hold_s, gap_s):
    """coverage of one path from the lab PRICE 3 s bins (labcore.prices.PriceCache.path): seconds from the fill to the start of the first
    stretch longer than gap_s without a bar (also before the first and after the last bar up to the hold); inf when the hold is covered"""
    us = 1_000_000; t0 = int(round(t_fill_s * us)); p = cache.path(coin, t0, t0 + int(hold_s * us))
    px, hi, lo = (np.asarray(p[k], float) for k in ('px', 'hi', 'lo'))
    valid = np.isfinite(px) & np.isfinite(hi) & np.isfinite(lo)
    valid &= (lo > 0) & (lo <= px) & (px <= hi)
    te = np.r_[t0, np.asarray(p['te_us'], np.int64)[valid], t0 + int(hold_s * us)]; d = np.diff(te) / us
    k = np.flatnonzero(d > gap_s)
    return float((te[k[0]] - t0) / us) if len(k) else np.inf
