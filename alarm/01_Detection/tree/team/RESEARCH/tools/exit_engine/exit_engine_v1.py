"""exit_engine_v1.py (BUILD1, 23 Oct 2026; T03 of LEAD/BUILD_BOARD_V1; owner STRATEGY/LEAD, tester TEST2; README V2.4 f096e1be; tests
tests/test_exit_engine_v1.py de80a82b written first, contract tests/engine_iface_v1.py f7aacbce). PAPER: a library, no data writes.
THE EXIT WALK: for trades entered at a known bar, price and side, where and when each exits under one named exit row, what it books and
which rule closed it. Per 3 s bar after the entry bar, in this order (README sec 2): 1 ADVERSE (the stop, the early stop in its minutes,
or the trail line once armed and past min_hold; a touch books the WORSE of the level and the bar close; a level crossed inside a hole
books the first price after it, gap_len_bars = the hole), 2 TAKE (trade-through only, at its level; a touch is touched_not_filled),
3 ARM (best since the arm bar; the trail line = best moved back by give, acting from the NEXT bar), 4 MONITOR (a reason known at bar k's
close books bar k+1's close), 5 TIME (the bar at entry + time_limit; a grid that ends first is NOPRICE, never cut short).
An empty bar (close, hi or lo NaN) is unknown, never a price. Units: pct, c (the coin's cost), nm (its normal move), each per trade with
its known_at; a missing unit or one known after the entry is REFUSED (the JOIN GUARD).
HOW (speed, the one design choice here): each trade's window is walked as numpy arrays in 'signed' prices (side x price, so a long and a
short share one rule: adverse = the signed low side, favourable = the signed high side); the first exit is the first bar where any
rule fires, by the order above. The oracle (tests/oracle_exit_v1.py, TEST2) is the same rules as plain per-bar Python.
FADE_F1 (TEST2 12:31:23Z reading 5, named here): a row with stop_from = 'extreme' measures its stop from units['extreme_px'] (per trade,
the run extreme read from EPI.<alarm>.giveback_pct at the fire, known_at in units['known_at_us']) instead of the entry price.
SET LIST (labcore, imported, never copied): ids.sha16_file (the registry sha16), costs.cost_c (the one cost c), lookahead.join_guard
(units known after the entry: refused, raised here as ValueError per the contract), prices.PriceCache (the coin-day cache over lab3.bins,
the one reader of the 3 s bins).
SKEPTIC REVIEW 03 (STRATEGY-130408, owner rulings): 03-06 a monitor whose bar k+1 is empty books the FIRST valid bar after it (kind
monitor, gap_len_bars = the hole before it); 03-07 every trade carries hole_bars (empty bars from entry+1 to its exit, or to the window's
end) and path_gap (hole_bars > 0), whatever closed it: an unobserved stretch is never read as a clean path; 03-08 a non-pct unit needs
units['known_at_us'] for every trade (no -1 accepted) and stop_from extreme needs units['extreme_known_at_us'], both under the join guard;
03-14 coverage(o) counts trades, resolved, noprice and with_holes, so a caller reports them and never drops a NOPRICE as a NaN.
INPUT CHECKS (OUTSIDE CODE1 review C1-01..04, refused with ValueError before any walk): side exactly +1 or -1; entry prices finite and
above 0; every availability clock a whole number (a fractional clock is never truncated into the past) and not negative; an observed
bar (close, hi, lo all finite) has positive prices and lo <= close <= hi (a bar missing any of the three is a hole, never a price);
every active level (stop, take, arm, give, early_stop) finite and above 0, arm and give together, time_limit above 0.
EVIDENCE (README V2.5 sec 2b, OX-SKEPTIC A02 rulings): every trade carries booking_status (STOP TRAIL TAKE MONITOR TIME NOPRICE) and
path_evidence_status: CLEAN; PATH_UNCERTAIN when a hole inside its hold could have held a level (any hole while a stop, take or trail
was active: an unobserved stretch can cross any level), even with a finite exit; UNRESOLVED for NOPRICE. census(o) counts every
eligible trade (nothing removed by finiteness) with the PATH_UNCERTAIN and NOPRICE shares and incomplete = non-CLEAN share > 5 pct.
CALL BOUNDARY: simulate(..., frozen={exits_path, exit_row_sha16, cost_table, cost_sha16, module_sha16}) or run_frozen(...) (frozen
required) verifies the registry row's sha16, that the row passed in memory equals that registry row field by field, the cost table's
sha16 and this module's own sha16; any mismatch refuses (a helper's existence is not evidence of its use).
A06 (OX-CODE1, STRATEGY-142032; its patch REVIEW_A06_02 applied, read): the manifest's dependency_sha16 {path: sha16} is checked file by
file at the boundary; run_frozen REQUIRES it and it must name every labcore module this engine imports (costs, ids, lookahead, prices).
OX-CODE2 A06-01..03 (STRATEGY 14:21:50Z; its patches applied, read): a duplicate exit id in the registry is refused; a frozen run carries
exit_row_sha16, cost_sha16 and module_sha16 on every result; every result carries price_model SIMULATED_BINANCE_3S_ADVERSE_FIRST and
price_venue BINANCE (never an attainable Hyperliquid fill).
OX-SKEPTIC A06-01, A06-03 (STRATEGY-155031a; its patches applied, read): a MONITOR exit booked after missing bars (gap_len_bars > 0)
is PATH_UNCERTAIN, never CLEAN; the frozen manifest also pins exits_schema_sha16 (the registry's column header), checked at the boundary.
MODEL PRICE: the booked price is a SIMULATION on Binance 3 s bins with adverse-first booking, never an attainable Hyperliquid fill or
queue quantity (those are measured only by the paper fill record T12 and live reconciliation).
VENUE NOTE (LAB1): the bars are BINANCE 3 s bins; the trading venue is Hyperliquid; the money tool carries the Binance-HL gap.
  simulate(close, hi, lo, entry_bar, entry_px, side, row, units=None, monitor=None, t0_us=0, signal_us=None) -> dict of arrays
  load_exits(path=EXITS, want_sha16=None) -> {id: row}     row_sha16(path, exit_id)     coverage(o)
  unit_c(settings, coins) -> per coin c in pct     bars(root, coin, t0_us, t1_us)"""
import csv, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
TEAM = os.path.dirname(os.path.dirname(TOOLS))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
from labcore import costs, ids, lookahead, prices                            # noqa: E402  the set list

EXITS = os.path.join(HERE, 'EXITS_V1.tsv')
BAR_US = 3_000_000
KINDS = ('stop', 'trail', 'take', 'monitor', 'time', 'noprice')
NUM = ('stop', 'take', 'arm', 'give', 'time_limit_min', 'min_hold_min', 'early_stop', 'early_min')
OUT = ('exit_bar', 'exit_px', 'kind', 'ret_pct', 'heat_pct', 'best_pct', 'bars_to_arm', 'gap_bp', 'gap_len_bars', 'touched_not_filled',
       'hole_bars')


def bars_of(minutes):
    """minutes -> 3 s bars (None stays None)"""
    return None if minutes is None or minutes == '' else int(round(float(minutes) * 20))


def _num(x):
    return None if x is None or x == '' else float(x)


def _clock(x, m, what):
    """C1-01: a clock array as given (never cast first): whole, finite, not negative, one per trade"""
    a = np.asarray(x)
    if a.shape != (m,):
        raise ValueError('%s: %s values for %d trades: refused' % (what, a.shape, m))
    if a.dtype.kind not in 'iuf' or (a.dtype.kind == 'f' and (not np.all(np.isfinite(a)) or np.any(a != np.floor(a)))):
        raise ValueError('%s: a clock that is not a whole number of microseconds: refused (never truncated)' % what)
    return a.astype(np.int64)


def _whole(x, what, lo=None):
    """an index array as given: whole numbers only (never truncated), at or above lo when given"""
    a = np.asarray(x)
    if a.dtype.kind not in 'iuf' or (a.dtype.kind == 'f' and (not np.all(np.isfinite(a)) or np.any(a != np.floor(a)))):
        raise ValueError('%s: whole numbers only (a fractional index is never truncated): refused' % what)
    if lo is not None and np.any(a < lo):
        raise ValueError('%s: below %d: refused' % (what, lo))
    return a.astype(np.int64)


def _check_inputs(close, hi, lo, entry_bar, entry_px, side, row, monitor=None):
    """C1-02, C1-03, C1-04 (+ C01b rerun: entry bar and monitor step whole numbers): bad inputs refused before any walk"""
    eb = _whole(entry_bar, 'entry_bar', 0)
    if np.any(eb >= len(close)):
        raise ValueError('entry_bar beyond the grid: refused')
    if monitor is not None:
        mo = _whole(monitor, 'monitor', -1)
        if mo.shape != eb.shape:
            raise ValueError('monitor: one step per trade: refused')
    s = np.asarray(side)
    if s.dtype.kind not in 'iuf' or not np.all(np.isin(s, (1, -1))):
        raise ValueError('side must be exactly +1 or -1 for every trade: refused')
    p = np.asarray(entry_px, float)
    if p.shape != s.shape or p.shape != np.asarray(entry_bar).shape or not np.all(np.isfinite(p)) or np.any(p <= 0):
        raise ValueError('entry prices: one finite price above 0 per trade: refused')
    fin = np.isfinite(close) & np.isfinite(hi) & np.isfinite(lo)              # a bar missing any of the three is a hole (unknown)
    if np.any(fin & ((close <= 0) | (hi <= 0) | (lo <= 0) | (lo > close) | (close > hi))):
        raise ValueError('an observed bar with a price at or below 0 or not lo <= close <= hi: refused')
    for k in ('stop', 'take', 'arm', 'give', 'early_stop'):
        v = _num(row.get(k))
        if v is not None and (not np.isfinite(v) or v <= 0):
            raise ValueError('level %s = %r: finite and above 0, or off: refused' % (k, row.get(k)))
    if (_num(row.get('arm')) is None) != (_num(row.get('give')) is None):
        raise ValueError('arm and give go together: refused')
    tl = _num(row.get('time_limit_min'))
    if tl is None or not np.isfinite(tl) or tl <= 0:
        raise ValueError('time_limit_min %r: finite and above 0: refused' % row.get('time_limit_min'))
    for k in ('min_hold_min', 'early_min'):
        v = _num(row.get(k))
        if v is not None and (not np.isfinite(v) or v < 0):
            raise ValueError('%s %r: finite and not negative: refused' % (k, row.get(k)))


def _guard(known_at_us, entry_us, what):
    if np.any(np.asarray(known_at_us) < 0):                                   # 03-08: a negative clock is a missing-value sentinel
        raise ValueError('%s: a known_at below 0 (a sentinel, not a clock): refused' % what)
    try:
        lookahead.join_guard(known_at_us, entry_us, what)
    except lookahead.LookaheadError as x:
        raise ValueError('JOIN GUARD: %s: refused' % x)


def _unit_values(row, units, m, entry_us):
    """-> (multiplier per trade, units_known_at_us per trade); refuses a missing unit and a unit known after its entry"""
    u = row['unit']
    has = units is not None and units.get('known_at_us') is not None
    if u != 'pct' and not has:
        raise ValueError('unit %s: units known_at_us missing: refused (03-08: never -1, never a default)' % u)
    ukn = _clock(units['known_at_us'], m, 'units known_at_us') if has else np.full(m, -1, np.int64)
    if u == 'pct':
        if has:
            _guard(ukn, entry_us, 'exit_engine units')
        return np.ones(m), ukn
    _guard(ukn, entry_us, 'exit_engine units')
    v = None if units is None or units.get(u) is None else np.asarray(units[u], float)
    if v is None or len(v) != m or not np.all(np.isfinite(v)) or np.any(v <= 0):
        raise ValueError('unit %s missing or not positive for some trade: refused (never a default)' % u)
    return v, ukn


def check_frozen(row, frozen):
    """the call boundary: the row, the registry, the cost table and this module are those the caller's card froze; else refused"""
    for k in ('exits_path', 'exit_row_sha16', 'exits_schema_sha16', 'cost_table', 'cost_sha16', 'module_sha16'):
        if not frozen.get(k):
            raise ValueError('frozen manifest lacks %s: refused' % k)
    with open(frozen['exits_path'], encoding='utf-8') as schema_file:
        header = next((line.rstrip('\n') for line in schema_file if not line.startswith('#')), '')
    if ids.sha16_text(header) != frozen['exits_schema_sha16']:
        raise ValueError('exit registry schema differs from frozen schema: refused')
    if row_sha16(frozen['exits_path'], row.get('id')) != frozen['exit_row_sha16']:
        raise ValueError('exit row %s sha16 is not the frozen %s: refused' % (row.get('id'), frozen['exit_row_sha16']))
    reg = load_exits(frozen['exits_path'])[row['id']]
    bad = sorted(k for k in set(reg) | set(row) if reg.get(k) != row.get(k))
    if bad:
        raise ValueError('the row passed differs from the frozen registry row in %s: refused' % bad)
    if ids.sha16_file(frozen['cost_table']) != frozen['cost_sha16']:
        raise ValueError('cost table %s sha16 is not the frozen %s: refused' % (frozen['cost_table'], frozen['cost_sha16']))
    # The release builder supplies its complete transitive code inventory.
    # Never ignore extra dependency hashes supplied by that release.
    for path, want in frozen.get('dependency_sha16', {}).items():
        if not os.path.isfile(path) or ids.sha16_file(path) != want:
            raise ValueError('dependency %s differs from the frozen release: refused' % path)
    if ids.sha16_file(os.path.abspath(__file__)) != frozen['module_sha16']:
        raise ValueError('exit_engine module sha16 %s is not the frozen %s: refused' % (ids.sha16_file(os.path.abspath(__file__)), frozen['module_sha16']))


def run_frozen(close, hi, lo, entry_bar, entry_px, side, row, frozen, **kw):
    """the money and judge tools' entry: simulate with the frozen manifest REQUIRED"""
    if not frozen:
        raise ValueError('run_frozen needs the frozen manifest: refused')
    deps = frozen.get('dependency_sha16')
    if not isinstance(deps, dict) or not deps:
        raise ValueError('dependency inventory required by run_frozen: refused')
    for module in (costs, ids, lookahead, prices):
        path = os.path.realpath(module.__file__)
        if path not in deps:
            raise ValueError('dependency inventory lacks %s: refused' % path)
    return simulate(close, hi, lo, entry_bar, entry_px, side, row, frozen=frozen, **kw)


def simulate(close, hi, lo, entry_bar, entry_px, side, row, units=None, monitor=None, t0_us=0, signal_us=None, frozen=None):
    if frozen is not None:
        check_frozen(row, frozen)
    close, hi, lo = (np.asarray(x, float) for x in (close, hi, lo))
    _check_inputs(close, hi, lo, entry_bar, entry_px, side, row, monitor)
    e_all = np.asarray(entry_bar, np.int64); m = len(e_all); n = len(close)
    p0_all = np.asarray(entry_px, float); s_all = np.asarray(side, np.int64)
    entry_us = int(t0_us) + e_all * BAR_US
    mult, ukn = _unit_values(row, units, m, entry_us)
    ref = None
    if row.get('stop_from') == 'extreme':
        ref = None if units is None or units.get('extreme_px') is None else np.asarray(units['extreme_px'], float)
        if ref is None or len(ref) != m or not np.all(np.isfinite(ref)) or np.any(ref <= 0):
            raise ValueError('stop_from extreme: units extreme_px missing or not above 0: refused')
        if units.get('extreme_known_at_us') is None:
            raise ValueError('stop_from extreme: units extreme_known_at_us missing: refused (03-08)')
        ek = _clock(units['extreme_known_at_us'], m, 'units extreme_known_at_us')
        _guard(ek, entry_us, 'exit_engine extreme_px')
    stop, take, arm, give = (_num(row.get(k)) for k in ('stop', 'take', 'arm', 'give'))
    early = _num(row.get('early_stop'))
    tl, mh, em = bars_of(row['time_limit_min']), bars_of(row.get('min_hold_min')) or 0, bars_of(row.get('early_min'))
    valid = np.isfinite(close) & np.isfinite(hi) & np.isfinite(lo)
    mon_all = None if monitor is None else np.asarray(monitor, np.int64)
    out = {k: np.zeros(m, float) for k in OUT}
    out['exit_bar'] = np.full(m, -1, np.int64); out['bars_to_arm'] = np.full(m, -1, np.int64)
    out['gap_len_bars'] = np.zeros(m, np.int64); out['touched_not_filled'] = np.zeros(m, np.int64)
    kind = np.empty(m, dtype=object)
    for i in range(m):
        e, p0, s, k_ = int(e_all[i]), float(p0_all[i]), int(s_all[i]), float(mult[i])
        end = e + tl
        j1 = min(end, n - 1)
        j = np.arange(e + 1, j1 + 1)
        k = j - e
        ok = valid[j] if len(j) else np.zeros(0, bool)
        A = np.where(s > 0, lo[j], -hi[j]) if len(j) else np.zeros(0)        # signed adverse side (lower is worse)
        F = np.where(s > 0, hi[j], -lo[j]) if len(j) else np.zeros(0)        # signed favourable side (higher is better)
        C = s * close[j] if len(j) else np.zeros(0)
        lv = lambda x, sg, base=p0: None if x is None else s * base * (1 + sg * s * x * k_ / 100.0)   # a level, signed
        stop_s = lv(stop, -1, p0 if ref is None else float(ref[i]))
        early_s, take_s, arm_s = lv(early, -1), lv(take, +1), lv(arm, +1)
        hold = k < mh
        # 3 ARM: the first valid bar whose favourable side reaches arm; best and the trail line from there (valid bars only)
        armed_after = np.zeros(len(j), bool); trail_prev = np.full(len(j), np.nan); ia = -1
        if arm_s is not None and give is not None:
            hit = np.nonzero(ok & (F >= arm_s))[0]
            if len(hit):
                ia = int(hit[0])
                Fv = np.where(ok, F, -np.inf); Fv[:ia] = -np.inf
                best = np.maximum(np.maximum.accumulate(Fv), s * p0)
                trail = best * (1 - s * give * k_ / 100.0)                    # price nt = best_px x (1 - s g k/100), signed: the same factor
                tr = np.where(np.arange(len(j)) >= ia, trail, np.nan)
                trail_prev[1:] = tr[:-1]; armed_after[1:] = np.arange(len(j) - 1) >= ia
        # 1 ADVERSE level per bar
        lvl = np.full(len(j), np.nan if stop_s is None else stop_s)
        if early_s is not None and em is not None:
            lvl = np.where(k <= em, early_s, lvl)
        use_trail = armed_after & ~hold
        lvl = np.where(use_trail, trail_prev, lvl)
        kind_adv = np.where(use_trail, 1, 0)                                  # 1 trail, 0 stop
        hitA = ok & np.isfinite(lvl) & (A <= lvl)
        # 2 TAKE: trade-through only, outside min_hold
        hitT = ok & ~hold & (F > take_s) if take_s is not None else np.zeros(len(j), bool)
        # 4 MONITOR: the next bar after the caller's step; 5 TIME: the bar at entry + time_limit
        mon = -1 if mon_all is None else int(mon_all[i])
        hitM = ok & (j >= mon + 1) if mon >= e else np.zeros(len(j), bool)    # 03-06: the first VALID bar from k+1 on
        hitE = ok & (j == end)
        anyx = hitA | hitT | hitM | hitE
        if anyx.any():
            x = int(np.argmax(anyx))
            if hitA[x]:
                L = float(lvl[x]); px = s * min(L, float(C[x])); kk = 'trail' if kind_adv[x] else 'stop'
                gbp = s * (s * L - px) / p0 * 1e4
                g = 0
                while x - 1 - g >= 0 and not ok[x - 1 - g]:
                    g += 1
            elif hitT[x]:
                px, kk, gbp, g = s * take_s, 'take', 0.0, 0
            elif hitM[x]:
                px, kk, gbp, g = float(close[j[x]]), 'monitor', 0.0, 0
                while x - 1 - g >= 0 and not ok[x - 1 - g] and j[x - 1 - g] > mon:
                    g += 1
            else:
                px, kk, gbp, g = float(close[j[x]]), 'time', 0.0, 0
            last = x
        else:
            x, last, kk = -1, len(j) - 1, 'noprice'; px, gbp, g = float('nan'), 0.0, 0
        upto = ok[:last + 1] if last >= 0 else np.zeros(0, bool)
        late_steps = kk in ('monitor', 'time', 'noprice')                    # the bar's take touch and arm step ran before its exit
        if take_s is not None and last >= 0:
            t = upto & ~hold[:last + 1] & (F[:last + 1] == take_s)
            if not late_steps and x >= 0:
                t[x] = False
            out['touched_not_filled'][i] = int(t.sum())
        if ia >= 0 and (ia < last or (ia == last and late_steps)) and (x < 0 or ia <= x):
            out['bars_to_arm'][i] = int(k[ia])
        if kk == 'noprice' or not upto.any():
            heat = best_ = float('nan')
        else:
            heat = s * (s * float(A[:last + 1][upto].min()) / p0 - 1) * 100
            best_ = s * (s * float(F[:last + 1][upto].max()) / p0 - 1) * 100
        out['exit_bar'][i] = -1 if x < 0 else int(j[x]); out['exit_px'][i] = px; kind[i] = kk
        out['ret_pct'][i] = s * (px / p0 - 1) * 100 if kk != 'noprice' else float('nan')
        out['heat_pct'][i] = heat; out['best_pct'][i] = best_; out['gap_bp'][i] = gbp; out['gap_len_bars'][i] = g
        out['hole_bars'][i] = int((~ok[:last + 1]).sum()) if last >= 0 else 0  # 03-07: every unobserved bar of the hold, any kind
    out['hole_bars'] = out['hole_bars'].astype(np.int64); out['path_gap'] = out['hole_bars'] > 0
    out['kind'] = kind.astype(str); out['booking_status'] = np.char.upper(out['kind'])
    levels = any(_num(row.get(k)) is not None for k in ('stop', 'take', 'arm', 'early_stop'))
    monitor_fill_gap = (out['kind'] == 'monitor') & (out['gap_len_bars'] > 0)
    uncertain = (out['path_gap'] & levels) | monitor_fill_gap
    out['path_evidence_status'] = np.where(out['kind'] == 'noprice', 'UNRESOLVED',
                                           np.where(uncertain, 'PATH_UNCERTAIN', 'CLEAN')).astype(str)
    out['price_model'] = np.repeat(np.asarray(['SIMULATED_BINANCE_3S_ADVERSE_FIRST']), m)
    out['price_venue'] = np.repeat(np.asarray(['BINANCE']), m)
    out['signal_us'] = entry_us.copy() if signal_us is None else np.asarray(signal_us, np.int64)
    out['entry_us'] = entry_us
    out['exit_us'] = np.where(out['exit_bar'] >= 0, int(t0_us) + out['exit_bar'] * BAR_US, -1)
    out['known_at_us'] = out['exit_us'].copy()
    out['units_known_at_us'] = ukn
    if frozen is not None:
        for key in ('exit_row_sha16', 'cost_sha16', 'module_sha16'):
            out[key] = np.repeat(np.asarray([str(frozen[key])]), m)
    return out


def coverage(o):
    """03-14: what a caller reports beside any result: trades, resolved (an exit booked), noprice, with_holes (path_gap)"""
    k = np.asarray(o['kind']).astype(str)
    return {'trades': int(len(k)), 'resolved': int((k != 'noprice').sum()), 'noprice': int((k == 'noprice').sum()),
            'with_holes': int(np.asarray(o['path_gap']).sum())}


def census(o, incomplete_share=0.05):
    """V2.5 2b: every eligible trade counted; CLEAN, PATH_UNCERTAIN, NOPRICE and their shares; incomplete when non-CLEAN > 5 pct"""
    e = np.asarray(o['path_evidence_status']).astype(str); n = int(len(e))
    c = {'trades': n, 'clean': int((e == 'CLEAN').sum()), 'path_uncertain': int((e == 'PATH_UNCERTAIN').sum()), 'noprice': int((e == 'UNRESOLVED').sum())}
    c['path_uncertain_share'] = c['path_uncertain'] / n if n else 0.0; c['noprice_share'] = c['noprice'] / n if n else 0.0
    c['incomplete'] = bool(n and (n - c['clean']) / n > incomplete_share)
    return c


def load_exits(path=EXITS, want_sha16=None):
    """{id: row} of the EXITS registry (TSV, '#' lines are notes); refuses a file whose sha16 is not the one wanted"""
    sha = ids.sha16_file(path)
    if want_sha16 is not None and sha != want_sha16:
        raise ValueError('%s sha16 %s, wanted %s: refused' % (path, sha, want_sha16))
    out = {}
    with open(path, encoding='utf-8') as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            row = {k: (None if v == '' else v) for k, v in r.items()}
            for c in NUM:
                if row.get(c) is not None:
                    row[c] = float(row[c])
            if row['id'] in out:
                raise ValueError('duplicate exit id %s: refused (one frozen row per id)' % row['id'])
            out[row['id']] = row
    return out


def row_sha16(path, exit_id):
    """03-05: the sha16 of ONE exit row's exact text (the line in the registry), so a card freezes the row, not its name"""
    with open(path, encoding='utf-8') as f:
        for l in f:
            if not l.startswith('#') and l.split('\t', 1)[0] == exit_id:
                return ids.sha16_text(l.rstrip('\n'))
    raise ValueError('exit id %s not in %s: refused' % (exit_id, path))


def unit_c(settings, coins):
    """per coin c in pct: THE one cost of record (labcore costs.cost_c: coin HL cost + the gap; a coin not in the table: the median)"""
    r = costs.cost_c(settings, coins)
    return np.asarray(r[0] if isinstance(r, tuple) else r, float)


def bars(root, coin, t0_us, t1_us, purpose='research', cache=None):
    """(te_us, close, hi, lo) on the 3 s grid t0..t1 inclusive, NaN where no bin, through labcore's PriceCache (pass one cache to reuse
    coin-days across many trades)"""
    pc = cache or prices.PriceCache(root, purpose)
    t0_us, t1_us = int(t0_us), int(t1_us)
    te = np.arange(t0_us, t1_us + 1, BAR_US, dtype=np.int64)
    c, h, l = (np.full(len(te), np.nan) for _ in range(3))
    p = pc.path(coin, t0_us - 1, t1_us)
    idx = (p['te_us'] - t0_us) // BAR_US
    on = ((p['te_us'] - t0_us) % BAR_US == 0) & (idx >= 0) & (idx < len(te))
    c[idx[on]] = p['px'][on]; h[idx[on]] = p['hi'][on]; l[idx[on]] = p['lo'][on]
    return te, c, h, l
