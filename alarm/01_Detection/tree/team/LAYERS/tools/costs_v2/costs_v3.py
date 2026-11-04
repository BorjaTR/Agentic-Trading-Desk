"""costs_v3: the cost of record, labcore.costs V3 landed in its tool folder (BUILD2, 23 Oct 2026; it moves into labcore.costs at labcore's
next release cycle so RELEASE_labcore_V2_1 and every release on it stay valid; T04, design team/LAYERS/tools/costs_v2/README.md 236897024fefcf39, STRATEGY-143903 and review
14:41:52Z M1-M3): ONE cost of record for every tool, in bp of the ENTRY notional, every part positive when the trader PAYS.
  make_record(v1_path, v4_path) -> (rows, header): rows {(coin, hour 0-23): (book_bp, 'V1'|'V4')}, book_bp = the DEARER of V1 and V4
      (cost_bp - fee, STRATEGY Q1); a coin in one table only has no row and is named in the header (refused, never a median, Q4)
  Costs(settings, record, funding, xcost=None, recorder=None, lab_root=LAB_DAYS): one instance per process (one table read, one funding
      month read per coin-month); xcost None = X1.COST read through lab3.days with the CALLER's purpose (README 639c5323 LAB1 MUST 1)
    cost_at(coin, t_us, purpose) -> fee_bp, book_bp, gap_bp, total_bp, total_x1_5_bp, total_x2_bp, reason
        the record row of (coin, UTC hour of t); unknown coin or hour: NaN + NO_COST. purpose is REQUIRED: 'charge'; the record has no
        known_at, so 'select' (or anything else) raises ValueError (LAB1 MUST 2); gates and skips use cost_fire.
    cost_fire(coin, t_us, purpose) -> the same keys + known_at_us: fee + (X1.COST.S04 + S05 at the last point u <= t KNOWN by t) + gap,
        the Binance round trip at 10k at the fire (SCOUT MUST); purpose = the caller's lab3.days purpose (the seal and quarantine apply);
        an empty cell keeps its EMPTY reason (never filled)
    funding_paid(coin, side, t_in_us, t_out_us, source='stored') -> funding_bp, hours, missing, reason, source, known_at_us: the sum over
        settled hour ends h with
        t_in < h <= t_out of rate x 1e4 x side (+1 long, -1 short): a long pays a positive rate, a short pays a negative one; a missing
        hour: NaN + FUNDING_MISSING (never filled); known_at = t_out. APPROXIMATION (M3): charged on the ENTRY notional, not the hourly mark.
        source 'recorder' = the HL recorder's live rates (paper and live, LIVE4 T12), the same rule, named in every row (LAB1 MUST 3).
    trade_cost(coin, side, t_in_us, t_out_us, size_usd, source='stored') -> cost_at's parts at t_in + funding_bp (+ funding_source);
        total = fee + book + gap + funding;
        size above settings size_usd: NaN + SIZE_REFUSED
    gap_bp(priced_on) -> 2 x gap_leg when fills are priced on Binance, 0 on HL trades (a setting, never a constant in a tool)
  settings: fee_side_pct, gap_leg_pct, size_usd, stress [k...], priced_on (+ table paths and sha16 in the settings file)
load_cost / cost_c (V1 table + gap, median fallback) stay importable, SUPERSEDED: receipts made with them stay under their own settings;
new work calls Costs. All arrays are numpy and vectorised over trades; nothing here writes a file."""
import datetime as dt, os, sys
import numpy as np

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', 'RESEARCH', 'tools')))
from labcore.lookahead import join_guard  # noqa: E402

HERE = os.path.dirname(os.path.realpath(__file__))
TEAM = os.path.realpath(os.path.join(HERE, '..', '..', '..'))
US, H_US = 1_000_000, 3_600_000_000
LAB_DAYS = '<DATA_ROOT>/lab_days'
LAB3_CODE = os.environ.get('LAB3_CODE') or os.path.realpath(os.path.join(HERE, '..', '..', '..', 'LAB3', 'code'))   # env: the jobs' LAB3_CODE


def load_cost(s, coins):
    """full cost c per fire in pct = coin HL cost of record (cost table) + the gap; a coin not in the table takes the median (counted)"""
    cost = {}
    for l in open(os.path.join(os.path.dirname(TEAM), s['cost']['table'])):
        if l.startswith('#') or l.startswith('coin\t'):
            continue
        f = l.rstrip('\n').split('\t'); cost[f[0]] = float(f[4]) / 100.0
    cmed = float(np.median(list(cost.values())))
    return np.array([cost.get(x, cmed) for x in coins]) + s['cost']['gap_pct'], int(sum(1 for x in coins if x not in cost))


cost_c = load_cost                                    # the spec's name; the body is bucket_proof's, line for line (SUPERSEDED by Costs)


def _tsv(path):
    rows = []; head = None
    for l in open(path):
        if l.startswith('#') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if head is None:
            head = f; continue
        rows.append(dict(zip(head, f)))
    return rows


def make_record(v1_path, v4_path, fee_bp=9.0):
    """-> ({(coin, hour): (book_bp, source)}, header text): the dearer of V1 (per coin, every hour) and V4 (per coin and hour)"""
    v1 = {r['coin']: float(r['cost_bp']) - fee_bp for r in _tsv(v1_path)}
    v4 = {(r['coin'], int(r['hour_utc'])): float(r['cost_bp']) - fee_bp for r in _tsv(v4_path) if r['hour_utc'].isdigit()}
    rows = {}
    for (coin, h), b4 in sorted(v4.items()):
        if coin in v1:
            rows[(coin, h)] = (b4, 'V4') if b4 >= v1[coin] else (v1[coin], 'V1')
    only = sorted(set(v1) ^ {c for c, _ in v4})
    return rows, 'coins in one table only (no row, refused): %s' % (' '.join(only) or 'none')


def _arr(*xs):
    xs = [np.atleast_1d(np.asarray(x)) for x in xs]; n = max(len(x) for x in xs)
    return [np.broadcast_to(x, (n,)) for x in xs]


def _hour(t_us):
    return np.asarray([dt.datetime.fromtimestamp(int(t) // US, dt.timezone.utc).hour for t in t_us], int)


class Costs:
    def __init__(self, settings, record, funding, xcost=None, recorder=None, lab_root=LAB_DAYS, days=None):
        self.s = dict(settings); self.rec = dict(record); self.src = {'stored': funding, 'recorder': recorder}; self._months = {}
        self.xcost = xcost or self._lab3_xcost; self.lab_root = lab_root; self._days = {}; self._grid = {}; self.prev_not_built = 0   # D-1 grids refused as NotBuilt (LAB1 MUST 2)
        self._mk_days = days                                         # tests: purpose -> a lab3.days-like reader; None = lab3.days.Days
        self.fee = 2 * 100.0 * float(self.s['fee_side_pct']); self.stress = [float(k) for k in self.s.get('stress', [1.5, 2])]

    def gap_bp(self, priced_on=None):
        return 2 * 100.0 * float(self.s['gap_leg_pct']) if (priced_on or self.s.get('priced_on', 'binance')) == 'binance' else 0.0

    def _parts(self, book, reason):
        n = len(book); fee = np.where(np.isnan(book), np.nan, self.fee); gap = np.where(np.isnan(book), np.nan, self.gap_bp())
        out = dict(fee_bp=fee, book_bp=book, gap_bp=gap, total_bp=fee + book + gap, reason=np.asarray(reason, object).reshape(n))
        for k in self.stress:
            out['total_x%s_bp' % ('%g' % k).replace('.', '_')] = fee + k * (book + gap)
        return out

    def _reader(self, purpose):
        if purpose not in self._days:
            if self._mk_days is not None:
                self._days[purpose] = self._mk_days(purpose)
            else:
                import sys
                if LAB3_CODE not in sys.path:
                    sys.path.insert(0, LAB3_CODE)
                from lab3 import days as LD
                self._days[purpose] = LD.Days(self.lab_root, purpose)
        return self._days[purpose]

    def _day_grid(self, coin, day, purpose):
        """(S04, S05) day arrays of one coin, read ONCE per (purpose, coin, day) (LAB1 / SCOUT SHOULD: no whole-day decode per call)"""
        key = (purpose, coin, day)
        if key not in self._grid:
            R = self._reader(purpose)
            def clock(code):
                # X1.COST is CLOCK with exact k; Days.at is ROWS-only.
                # read() applies the caller's seal before any part lookup.
                value = R.read(code, 'v', [day], [coin])
                if R.step(code, day) != 5:
                    raise ValueError('%s: expected a 5-second cost clock' % code)
                known = R.read(code, 'k', [day], [coin])
                reason_ids = R.read(code, 'e', [day], [coin])
                texts = R.reasons(code, day)
                why = np.full(reason_ids.shape, 'ABSENT', object)
                for i, text in enumerate(texts):
                    why[reason_ids == i] = text
                return dict(v=value, k=known, reason=why)
            self._grid[key] = (clock('X1.COST.S04'), clock('X1.COST.S05'))
        return self._grid[key]

    def _lab3_xcost(self, coin, t_us, purpose, back=24):
        """X1.COST.S04 / S05 at the 5 s point holding t AND the `back` points before it (stepping into D-1 after midnight), each with its
        known_at, through lab3.days with the caller's purpose (its seal refuses); cost_fire keeps the last point KNOWN by t (SCOUT + LAB1
        MUST 15:38Z / 15:39Z: a late point at t never hides an earlier known one)"""
        day = dt.datetime.fromtimestamp(t_us // US, dt.timezone.utc).strftime('%Y%m%d')
        d0 = int(dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()) * US; k = int((t_us - d0) // (5 * US))
        # Validate/read the requested day before any predecessor I/O.
        today = self._day_grid(coin, day, purpose)
        parts = []
        if k < back:                                                     # the points before 00:00 are D-1's last ones
            prev = (dt.datetime.strptime(day, '%Y%m%d') - dt.timedelta(days=1)).strftime('%Y%m%d'); p0 = d0 - 86400 * US
            try:
                g4, g5 = self._day_grid(coin, prev, purpose)
            except Exception as e:                                       # LAB1 17:11:46Z MUST 2: a D-1 not built (the first lab day) gives no
                if type(e).__name__ != 'NotBuilt':                       # earlier points, counted; any other error still raises
                    raise
                self.prev_not_built += 1; g4 = None
            if g4 is not None:
                n = g4['v'].shape[2]; idx = np.arange(max(0, n - (back - k)), n); parts.append((p0, idx, g4, g5))
        g4, g5 = today; parts.append((d0, np.arange(max(0, k - back), k + 1), g4, g5))
        u, kn, s4, s5, why = [], [], [], [], []
        for base, idx, g4, g5 in parts:
            u.append(base + idx.astype(np.int64) * 5 * US); kn.append(np.maximum(g4['k'][0, 0, idx], g5['k'][0, 0, idx]).astype(np.int64))
            s4.append(g4['v'][0, 0, idx]); s5.append(g5['v'][0, 0, idx])
            why.append(np.array([g4['reason'][0, 0, i] or g5['reason'][0, 0, i] or '' for i in idx], object))
        return {'u_us': np.concatenate(u), 'known_at_us': np.concatenate(kn), 'S04': np.concatenate(s4), 'S05': np.concatenate(s5),
                'reason': np.concatenate(why)}

    def cost_at(self, coin, t_us, purpose):
        if purpose != 'charge':
            raise ValueError('cost_at purpose %r: only \'charge\'; the record has no known_at, a gate or skip uses cost_fire (costs_v2 README sec 5)' % (purpose,))
        coin, t_us = _arr(coin, t_us); t_us = np.asarray(t_us, np.int64)
        got = [self.rec.get((c, h)) for c, h in zip(coin, _hour(t_us))]
        book = np.array([g[0] if g else np.nan for g in got], float)
        return self._parts(book, ['' if g else 'NO_COST' for g in got])

    def cost_fire(self, coin, t_us, purpose):
        coin, t_us = _arr(coin, t_us); t_us = np.asarray(t_us, np.int64); book = np.full(len(t_us), np.nan); why = []; known = np.full(len(t_us), -1, np.int64)
        for i, (c, t) in enumerate(zip(coin, t_us)):
            x = self.xcost(c, int(t), purpose); ok = (np.asarray(x['u_us'], np.int64) <= t) & (np.asarray(x['known_at_us'], np.int64) <= t)
            if not ok.any():
                why.append('NO_COST_AT_FIRE'); continue
            j = np.flatnonzero(ok)[-1]; v = float(x['S04'][j]) + float(x['S05'][j])
            if np.isfinite(v):
                # Missing cells have no usable value or source timestamp. Preserve
                # their reason; only a finite value is offered to the join guard.
                join_guard(np.array([int(x['known_at_us'][j])], np.int64), np.array([t], np.int64), 'cost_fire X1.COST')
                known[i] = int(x['known_at_us'][j])
                book[i] = v; why.append('')
            else:
                why.append(str(x['reason'][j]) or 'EMPTY')
        out = self._parts(book, why); out['known_at_us'] = known
        return out

    def _rates(self, coin, month, source):
        k = (source, coin, month)
        if k not in self._months:
            self._months[k] = {int(t) * 1000: float(r) for t, r, _ in self.src[source](coin, month)}
        return self._months[k]

    def funding_paid(self, coin, side, t_in_us, t_out_us, source='stored'):
        if source not in self.src or self.src[source] is None:
            raise ValueError('funding source %r: stored or recorder (and the recorder reader given)' % (source,))
        coin, side, t_in_us, t_out_us = _arr(coin, side, t_in_us, t_out_us); n = len(coin)
        out = dict(funding_bp=np.full(n, np.nan), hours=np.zeros(n, int), missing=np.zeros(n, int), reason=np.array([''] * n, object),
                   source=np.array([source] * n, object), known_at_us=np.asarray(t_out_us, np.int64).copy())
        for i in range(n):
            a, b = int(t_in_us[i]), int(t_out_us[i]); h = (a // H_US + 1) * H_US; tot = 0.0; miss = 0; hrs = 0
            while h <= b:
                m = dt.datetime.fromtimestamp(h // US, dt.timezone.utc).strftime('%Y%m'); r = self._rates(coin[i], m, source).get(h)
                hrs += 1
                if r is None or not np.isfinite(r):
                    miss += 1
                else:
                    tot += r
                h += H_US
            out['hours'][i] = hrs; out['missing'][i] = miss
            if miss:
                out['reason'][i] = 'FUNDING_MISSING'
            else:
                out['funding_bp'][i] = tot * 1e4 * float(side[i])
        return out

    def trade_cost(self, coin, side, t_in_us, t_out_us, size_usd, source='stored'):
        coin, side, t_in_us, t_out_us, size_usd = _arr(coin, side, t_in_us, t_out_us, size_usd)
        at = self.cost_at(coin, t_in_us, 'charge'); f = self.funding_paid(coin, side, t_in_us, t_out_us, source=source)   # LAB1 MUST 15:39Z
        out = dict(at); out['funding_bp'] = f['funding_bp']; out['funding_hours'] = f['hours']; out['funding_source'] = f['source']
        big = np.asarray(size_usd, float) > float(self.s['size_usd'])
        out['total_bp'] = np.where(big, np.nan, at['total_bp'] + f['funding_bp'])
        why = np.where(big, 'SIZE_REFUSED', np.where(at['reason'] != '', at['reason'], f['reason'])).astype(object)
        out['reason'] = why
        for k in self.stress:
            key = 'total_x%s_bp' % ('%g' % k).replace('.', '_'); out[key] = np.where(big, np.nan, at[key] + f['funding_bp'])
        return out
