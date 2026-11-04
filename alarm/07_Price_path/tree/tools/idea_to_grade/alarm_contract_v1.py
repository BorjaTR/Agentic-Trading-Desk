"""alarm_contract_v1.py (ALARMLIB seat, 25 Oct 2026): the ONE copy of the four rules the alarm contract and the grading tool share (review
F6: "one module both import"). Pure Python, standard library only; no file, alarm, coin, day or price level is held here.
  ASOF      a moment t is busy when a fire lies in [t - before_s, t] (closed at t: the fire moment itself is never a control)
  CHAIN     fires in time order chain into one cluster when the gap to the previous fire is <= gap_s, and a cluster never spans more than
            max_span_s from its first fire (the chain is split, the new cluster is flagged CHAIN_SPLIT)
  SAME BIN  target and stop inside one price bin: the order inside the bin is unknown, scored as the stop (AMBIGUOUS_STOP)
  THROUGH   a resting order fills only when a bin trades STRICTLY through its price (a touch is not a fill)
Users: team/RESEARCH/tools/idea_to_grade/i2g_rules_v1.py and team/RESEARCH/LIBRARY/alarm_library/alarm_core_v1_2.py."""
import bisect

ASOF_BEFORE_S = 14400
WAVE_GAP_S = 1800
WAVE_MAX_SPAN_S = 14400


def asof_busy(t, fires_sorted, before_s=ASOF_BEFORE_S):
    """True when a time of fires_sorted (ascending) lies in [t - before_s, t]; a fire after t never counts"""
    i = bisect.bisect_left(fires_sorted, t - before_s)
    return i < len(fires_sorted) and fires_sorted[i] <= t


def chain(times_sorted, gap_s=WAVE_GAP_S, max_span_s=WAVE_MAX_SPAN_S):
    """times in ascending order -> per time (cluster number from 0, flag): the flag is 'CHAIN_SPLIT' on every member of a cluster that was
    opened only by the span rule (its first fire is within gap_s of the previous fire), '' otherwise"""
    out = []; n = -1; first = prev = None; flag = ''
    for t in times_sorted:
        if first is not None and t - prev <= gap_s and t - first <= max_span_s:
            pass
        else:
            flag = 'CHAIN_SPLIT' if first is not None and t - prev <= gap_s else ''
            n += 1; first = t
        prev = t
        out.append((n, flag))
    return out


def bin_exit(side, hi, lo, target, stop, strict_target=False):
    """one price bin after the entry -> 'AMBIGUOUS_STOP' (both levels inside the bin), 'STOP', 'TARGET' or None. side +1 long / -1 short;
    target and stop are prices; strict_target: a resting target needs a strict trade-through (a touch is not a fill)"""
    if side > 0:
        hit_s = lo <= stop; hit_t = hi > target if strict_target else hi >= target
    else:
        hit_s = hi >= stop; hit_t = lo < target if strict_target else lo <= target
    if hit_s:
        return 'AMBIGUOUS_STOP' if hit_t else 'STOP'
    return 'TARGET' if hit_t else None


def trades_through(side, hi, lo, limit):
    """a resting buy (side +1) fills when the bin trades strictly below its limit, a resting sell strictly above"""
    return lo < limit if side > 0 else hi > limit
