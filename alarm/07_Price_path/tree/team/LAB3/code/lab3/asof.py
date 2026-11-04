"""lab3/asof.py (LAB2, builder, 19 Oct 2026). asof(): the value of a code as known at each step end, by C1's rule (LAB3_ARCH_V1 rev 10
section 5.3; TABLES_V2_DESIGN_V1 S1 and S2; TREE's asof_v2 2f13aaf7 and stored_v2 038a92c4 read for the rule). Standard Python only, so
the VM runs it; LAB4 tests that its cells equal lab_v2's (C2) and TREE's core where both exist. Tests first: tests/test_asof_v1.py.

The rule, at a step end t of day D (grid D 00:00:00 + k x step, as lab_v2's ts_end):
  - rows read: those of day(t - 1 h) and day(t), so 00:00 to 00:59 also read D-1; rows with a null as_of_us or known_at_us are never kept;
  - every kept row has an order key (as_of_us, known_at_us, value text, reason text) and its read position last;
  - the answer is the LAST row in that order among the rows with as_of_us <= t and known_at_us <= t; none -> no row known;
  - value text: kind 0 -> '', 1 -> the float's text, 2 -> the integer's text, else value_txt ('' if null);
  - reason text: empty_reason, with ';STALE' (or 'STALE' alone) when stale is 1;
  - age: (t - known_at_us) in whole seconds, rounded half to even, done in integers (no float).
OPINION, to be measured by C2: the float's text here is Python's repr; TREE's is polars' cast; they differ only in how a few floats are
written, which can change the order only between two rows sharing as_of and known_at (Y3 ties)."""
import math, datetime
from bisect import bisect_right
from . import rows as R

US = 1_000_000
HOUR_US = 3600 * US          # C1's first-hour window: 00:00 to 00:59 reads D-1's tail; ONE place (LAYERS 6.12f item 1, rule 32)
STEPS = {'minute': 60, 's30': 30, 's5': 5, 60: 60, 30: 30, 5: 5}
NO_ROW = 'NO_ROW_KNOWN'

def day_start_us(day):
    d = datetime.datetime.strptime(str(day), '%Y%m%d').replace(tzinfo=datetime.timezone.utc)
    return int(d.timestamp()) * US

def grid(day, step):
    s = STEPS[step] * US; d0 = day_start_us(day)
    return [d0 + k * s for k in range(86400 * US // s)]

def value_text(kind, bits, txt):
    if kind == 0:
        return ''
    if kind == 1 and bits is not None:
        return repr(R.as_float(bits))
    if kind == 2 and bits is not None:                 # WHOLE: an integer prints as one; NaN, inf, -0.0 or a fraction by repr (LAB4 15:48:06Z)
        x = R.as_float(bits)
        if math.isfinite(x) and x == int(x) and not (x == 0 and math.copysign(1.0, x) < 0):
            return str(int(x))
        return repr(x)
    return '' if txt is None else txt

def reason_text(empty_reason, stale):
    er = empty_reason or ''
    if stale == 1:
        return er + ';STALE' if er else 'STALE'
    return er

def rint_age(us):
    q, r = divmod(us, US)
    return q + (1 if (r > US // 2 or (r == US // 2 and q % 2 == 1)) else 0)

def _series(r, days_read):
    """the kept rows of the days read: list of (key, pos, row dict)"""
    out = []
    for i, d in enumerate(r['day']):
        if d not in days_read:
            continue
        a = r['as_of_us'][i]; k = r['known_at_us'][i]
        if a is None or k is None:
            continue
        v = value_text(r['value_kind'][i], r['value_bits'][i], r['value_txt'][i])
        why = reason_text(r['empty_reason'][i], r['stale'][i])
        out.append(((a, k, v, why, d, i), i, v, why))
    return out

def answer_grid(kept, ts):
    """kept: list of (key, i, v, why); ts: ascending step ends -> for each t the index into kept of the answer, or None.
    The last row in key order among rows with as_of <= t and known_at <= t: rank the rows by key, sweep them by max(as_of, known_at)."""
    order = sorted(range(len(kept)), key=lambda j: kept[j][0])
    rank = [0] * len(kept)
    for r_, j in enumerate(order):
        rank[j] = r_
    by_t = sorted(range(len(kept)), key=lambda j: (max(kept[j][0][0], kept[j][0][1]), rank[j]))
    tes = [max(kept[j][0][0], kept[j][0][1]) for j in by_t]
    best = []; cur = -1; cur_j = None
    for j in by_t:
        if rank[j] > cur:
            cur = rank[j]; cur_j = j
        best.append(cur_j)
    out = []
    for t in ts:
        p = bisect_right(tes, t)
        out.append(best[p - 1] if p else None)
    return out

def asof(root, code, coins, day0, day1, step='minute'):
    """-> {coin: {'ts_end', 'v' (text), 'value' (float or None), 'age' (int or None), 'reason' (text), 'stale', 'kind', 'not_built'}}.
    A day whose own block or the day before it (for 00:00 to 00:59) is not built is listed in not_built and returns no cells."""
    days = R.days_between(day0, day1)
    first = int((datetime.datetime.strptime(str(days[0]), '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d'))
    out = {}
    for coin in coins:
        rr = R.rows(root, code, [coin], first, days[-1])[coin]
        res = {k: [] for k in ('ts_end', 'v', 'value', 'age', 'reason', 'stale', 'kind')}; res['not_built'] = []
        for d in days:
            prev = int((datetime.datetime.strptime(str(d), '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d'))
            if d in rr['not_built'] or prev in rr['not_built']:
                res['not_built'].append(d); continue
            g = grid(d, step); d0 = day_start_us(d)
            early = [t for t in g if t - HOUR_US < d0]; late = [t for t in g if t - HOUR_US >= d0]
            for ts, days_read in ((early, {prev, d}), (late, {d})):
                if not ts:
                    continue
                kept = _series(rr, days_read)
                ans = answer_grid(kept, ts)
                for t, j in zip(ts, ans):
                    res['ts_end'].append(t)
                    if j is None:
                        res['v'].append(''); res['value'].append(None); res['age'].append(None); res['reason'].append(NO_ROW)
                        res['stale'].append(None); res['kind'].append(None)
                        continue
                    key, i, v, why = kept[j]
                    res['v'].append(v)
                    try:
                        res['value'].append(float(v) if v != '' else None)
                    except ValueError:
                        res['value'].append(None)
                    res['age'].append(rint_age(t - key[1])); res['reason'].append(why)
                    res['stale'].append(rr['stale'][i]); res['kind'].append(rr['value_kind'][i])
        out[coin] = res
    return out
