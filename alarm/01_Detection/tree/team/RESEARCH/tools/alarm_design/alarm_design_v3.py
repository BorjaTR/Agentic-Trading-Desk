"""alarm_design_v3.py: the lab engine alarm_design_v2.py with the lab days from the caller. Owner ALARM. New edition by SCOUT for the clean
release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release folder only"). Old file: alarm_design_v2.py
ac3e78f84e3ff58c (release alarm_design V3_8_1), never edited. Changed: no machine default for the lab days. LabSource(lab_root=...) is
required (none: ValueError LAB_ROOT_REQUIRED) and the run command takes them as its last argument (the settings key LAB_DAYS). Code stays
relative to this file (HOME/../alarms, ../model_v1, <forensics>/team/LAB3/code: a part must keep the dev layout). Every rule, value and
output is alarm_design_v2.py's. The rest of this text is alarm_design_v2.py's.
ALARM alarm_design v2 (23 Oct 2026) = v1 + OUTSIDE D05 (seal refusals stop the run; grid_s must be a positive multiple of 5) +
OUTSIDE S06 rules 1-5 (estimand named: alarm-time conditional prediction; base exclusion from PAST fires only; nothing read past the run's
last day, labels crossing it are NOT KNOWN; balance, common support and unmatched reasons on the card; the busy base is a named
retrospective reference, never the verdict). v1 (23 Oct 2026; design README 7907291d + LEAD 06:04:23Z changes 1-6 + LAB1 06:04:40Z MUSTs 1-6).
One tool for every alarm: a JSON DEFINITION in, on the find window (to the seal LAB1 sets in lab3.law), out:
  the fire list, the FAIR comparison moments (same coin and scope, every 'shared' condition true, the 'claim' condition false, matched on
  the definition's inputs + market forcing + hour block + the primary label's own value just before t), the no-price truth labels
  (start after t; the share after t + 6 s beside), counts by wave / episode / day, and the truth card (cmd 'card').
Nothing here reads a price after t except the OI dollar value at t; no money, no costs (AHEAD = alarm_stamp + offer_ladder_v1).
  python3 alarm_design_v3.py run  <def.json> <first YYYYMMDD> <last YYYYMMDD> <out_root> <receipt dir> <lab_days>
  python3 alarm_design.py try  <def.json> <team/RESEARCH/TRY_LEDGER.tsv> [what is tried]     (BEFORE the card; frozen before read)
  python3 alarm_design.py card <def.json> <out_root> <receipt dir> <team/RESEARCH/TRIES_LEDGER_V1.tsv> <REGIMES.tsv or -> <WINDOWS.json> <RUN settings.json>
      (the ONE tries ledger, ledger_add_v5: a PREREG row on the run settings file must exist; TRY_LEDGER.tsv is history only)
Internal clock: every input is laid on a 5 s clock by the lab3 as-of rule (column k = value known at D0 + step x k); the alarm is checked
on its own grid (grid_s, a multiple of 5). A day is processed with D-1 and D+1 beside it (D+1 only for labels)."""
import datetime, hashlib, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
HOME = os.environ.get('AD_HOME', HERE)             # the tool's real folder (a mutant copy runs elsewhere and points back here)
sys.path.insert(0, os.path.join(HOME, '..', 'alarms')); sys.path.insert(0, os.path.join(HOME, '..', 'model_v1'))
import onset_band_v6 as OB                         # REUSED: the 14-day own band (edges) of the lab's alarm finders
import matched_controls_v1 as MC                   # REUSED: the lab's busy base (range-matched moments, SCOUT)
F_ROOT = os.path.realpath(os.path.join(HOME, '..', '..', '..', '..'))
CODE_DIR = os.path.join(F_ROOT, 'team', 'LAB3', 'code')
# no LAB_ROOT: the lab days are the caller's (LabSource(lab_root=...), the run command's <lab_days>: the settings key LAB_DAYS)
BASE_S = 5
NB = 86400 // BASE_S
NAN = float('nan')
SIDE_LIQ = {1: 'A1.S02', -1: 'A1.S01'}          # liquidations that push price that way: up = shorts forced (A1.S02), down = longs (A1.S01)
MONTHS_FIRST = '20250901'
QUIET = ((23 * 60 + 30), (24 * 60 + 15))           # LAB1 MUST 5: never 23:30-00:15Z


# ---------------------------------------------------------------- small helpers
def sha16_bytes(b):
    return hashlib.sha256(b).hexdigest()[:16]


def sha16_file(p):
    return sha16_bytes(open(p, 'rb').read())


def day0(d):
    return int(datetime.datetime.strptime(str(d), '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp())


def utc_day(t):
    return datetime.datetime.fromtimestamp(int(t), datetime.timezone.utc).strftime('%Y%m%d')


def shift(d, n):
    return (datetime.datetime.strptime(str(d), '%Y%m%d') + datetime.timedelta(days=n)).strftime('%Y%m%d')


def days_between(a, b):
    out = []; d = a
    while d <= b:
        out.append(d); d = shift(d, 1)
    return out


def seal_day(code_dir=CODE_DIR):
    """the first day research may not read, from LAB1's one setting (lab3.law.RESEARCH_REFUSED, LEAD change 1)"""
    sys.path.insert(0, code_dir)
    from lab3 import law
    return str(min(lo for lo, hi, why in law.RESEARCH_REFUSED))


def refuse_sealed(days, seal):
    bad = [d for d in days if str(d) >= str(seal)]
    if bad:
        raise PermissionError('days %s..%s on or after the seal %s: refused' % (bad[0], bad[-1], seal))


def quiet_now(now=None):
    m = (now or datetime.datetime.now(datetime.timezone.utc)); mm = m.hour * 60 + m.minute
    return mm >= QUIET[0] or mm < QUIET[1] - 24 * 60


# ---------------------------------------------------------------- the definition
REQ = ('id', 'version', 'claim', 'window', 'grid_s', 'inputs', 'conditions', 'fire', 'truth', 'primary', 'base')
CMPS = ('>=', '<=', '>', '<', 'samesign', 'oppsign')


def load_def(path):
    raw = open(path, 'rb').read(); d = json.loads(raw)
    miss = [k for k in REQ if k not in d]
    if miss:
        raise ValueError('definition %s lacks %s' % (path, miss))
    if not isinstance(d['grid_s'], int) or isinstance(d['grid_s'], bool) or d['grid_s'] <= 0 or d['grid_s'] % BASE_S:
        raise ValueError('grid_s must be a positive multiple of 5 (OUTSIDE D05-02)')
    roles = [c['role'] for c in d['conditions']]
    if roles.count('claim') < 1 or any(r not in ('shared', 'claim') for r in roles):
        raise ValueError('every condition is shared or claim, at least one claim (the base is built on it)')
    names = {t['name'] for t in d['truth']}
    if d['claim'].get('type') not in ('DETECT', 'PREDICT', 'CONTINUATION'):
        raise ValueError('claim.type must be DETECT, PREDICT or CONTINUATION, frozen before data (OUTSIDE S07-02)')
    if not isinstance(d['claim'].get('footprint_s'), int) or d['claim']['footprint_s'] < 0:
        raise ValueError('claim.footprint_s: the trigger event footprint in seconds (OUTSIDE S07-03)')
    prim = [t for t in d['truth'] if t['name'] == d['primary']]
    if prim and d['claim'].get('type') == 'DETECT' and prim[0].get('when') != 'present':
        raise ValueError('a DETECT claim needs a CONTEMPORANEOUS primary label (when = present: (t - end_s, t]) (OUTSIDE P02-06)')
    if prim and d['claim'].get('type') in ('PREDICT', 'CONTINUATION') and prim[0].get('when') == 'present':
        raise ValueError('a PREDICT or CONTINUATION claim needs a label after t (OUTSIDE P02-06)')
    if d['primary'] not in names:
        raise ValueError('primary %r is not a truth label (LAB1 MUST 3: one primary, named before data)' % d['primary'])
    for t in d['truth']:
        if t.get('start_s', 0) < 0:
            raise ValueError('label %s: start_s < 0 (LEAD change 2: every label starts after t)' % t['name'])
    for c in d['conditions']:
        if c['cmp'] not in CMPS:
            raise ValueError('condition %s: cmp %r' % (c['name'], c['cmp']))
    d['_sha16'] = sha16_bytes(raw); d['_path'] = path
    return d


# ---------------------------------------------------------------- the data source (lab3 for real; tests plant their own)
class LabSource:
    """values as lab3 knows them; everything through Days(root, 'research')"""

    def __init__(self, lab_root=None, code_dir=CODE_DIR, events=None):
        if not lab_root:
            raise ValueError('LAB_ROOT_REQUIRED: give lab_root (the lab days, the settings key LAB_DAYS); no machine default')
        sys.path.insert(0, code_dir)
        from lab3 import days as LD, bins as LB
        self.R = LD.Days(lab_root, 'research'); self.LB = LB; self._c = {}; self.events = events or {}
        self.used = {}

    def coins(self, day):
        """the day's coins; [] for a day lab_days has not built (the warm-up before 10 Sep 2025) - a refused (sealed) day still raises"""
        try:
            return list(self.R.index(day, 'PRICE')['coins'])
        except Exception as e:                                 # lab3 says NotBuilt (or FileNotFoundError before 23 Oct) for an unbuilt day
            if type(e).__name__ in ('NotBuilt', 'FileNotFoundError') and str(day) < '20250910':
                return []                                      # only the warm-up days before the first built day; anything else stops the run
            raise

    def code(self, code, day, coins):
        """(ncoins, NB) on the 5 s clock by the as-of rule; NaN when the day or code is not built"""
        key = (code, day, tuple(coins))
        if key not in self._c:
            if len(self._c) > 64:
                self._c.pop(next(iter(self._c)))
            try:
                v = self.R.read(code, 'v', [day], coins)[0]; st = self.R.step(code, day)
                self._c[key] = to_base(v, st)
            except PermissionError:
                raise                                          # a refused (sealed) day stops the run, named (OUTSIDE D05-01)
            except Exception:
                self._c[key] = np.full((len(coins), NB), np.nan)
        return self._c[key]

    def market(self, code, day):
        key = (code, day, 'MARKET')
        if key not in self._c:
            try:
                v = self.R.read(code, 'v', [day], ['MARKET'])[0]; st = self.R.step(code, day)
                self._c[key] = to_base(v, st)[0]
            except PermissionError:
                raise
            except Exception:
                self._c[key] = np.full(NB, np.nan)
        return self._c[key]

    def bins(self, day, coin):
        """(te_us, px) of the coin's 3 s bins of the day (lab3.bins), for matched_controls_v1"""
        key = ('BINS', day)
        if key not in self._c:
            try:
                cs = self.coins(day); boff, b = self.LB.read_bins(self.R, day, cs)
                self._c[key] = {c: (np.asarray(b['te'][boff[i]:boff[i + 1]], np.int64), np.asarray(b['px'][boff[i]:boff[i + 1]], float)) for i, c in enumerate(cs)}
            except Exception:
                self._c[key] = {}
        return self._c[key].get(coin, (np.zeros(0, np.int64), np.zeros(0)))

    def price(self, day, coins):
        """(ncoins, NB) last 3 s close known at each 5 s step"""
        key = ('PRICE', day, tuple(coins))
        if key not in self._c:
            out = np.full((len(coins), NB), np.nan)
            try:
                boff, b = self.LB.read_bins(self.R, day, coins)
                g = (day0(day) + BASE_S * np.arange(NB)) * 1_000_000
                for i in range(len(coins)):
                    te = np.asarray(b['te'][boff[i]:boff[i + 1]], np.int64); px = np.asarray(b['px'][boff[i]:boff[i + 1]], float)
                    j = np.searchsorted(te, g, side='right') - 1
                    out[i] = np.where(j >= 0, px[np.maximum(j, 0)] if len(px) else np.nan, np.nan)
            except Exception:
                pass
            self._c[key] = out
        return self._c[key]


def to_base(v, step):
    """lab3 columns (k = known at D0 + step x k) to the 5 s clock by as-of: base index j takes column floor(j x 5 / step)"""
    v = np.asarray(v, float)
    if step == BASE_S:
        return v
    if step < BASE_S or step % BASE_S:
        raise ValueError('step %s not on the 5 s clock' % step)
    j = (np.arange(NB) * BASE_S) // step
    return v[:, j]


def load_events(paths):
    """{coin: (t sorted float, side int)} from EVENTS tsv files (coin, t, side, ...); several files = one list (one source each, by sha)"""
    out = {}; shas = {}
    for p in paths:
        p, _, flt = p.partition('::')                       # 'path::column=value' keeps only rows with that value (e.g. warm_up=0)
        shas[os.path.basename(p) + ('::' + flt if flt else '')] = sha16_file(p)
        with open(p) as f:
            h = f.readline().rstrip('\n').split('\t'); ic, it, isd = h.index('coin'), h.index('t'), h.index('side')
            fc, fv = (h.index(flt.split('=')[0]), flt.split('=')[1]) if flt else (None, None)
            for l in f:
                r = l.rstrip('\n').split('\t')
                if fc is not None and r[fc] != fv:
                    continue
                out.setdefault(r[ic], ([], []))[0].append(float(r[it])); out[r[ic]][1].append(int(float(r[isd])))
    ev = {}
    for c, (t, s) in out.items():
        o = np.argsort(t, kind='mergesort'); ev[c] = (np.asarray(t)[o], np.asarray(s, int)[o])
    return ev, shas


# ---------------------------------------------------------------- the op registry (LEAD-approved: fixed, tested once, reused)
def roll_sum(x, n):
    """sum of the last n 5 s rows (NaN when any is NaN)"""
    out = np.full_like(x, np.nan)
    if n <= 0 or x.shape[-1] < n:
        return out
    w = np.lib.stride_tricks.sliding_window_view(x, n, axis=-1).sum(axis=-1)
    out[..., n - 1:] = w
    return out


def roll_max(x, n, prior=False):
    """max of the last n 5 s rows ignoring NaN (NaN when all n are NaN or the window starts before the data); prior=True: the n rows
    BEFORE this one. scipy's maximum_filter1d, then shifted so the window ends at the row (checked against a plain loop in the tests)"""
    from scipy.ndimage import maximum_filter1d
    x = np.asarray(x, float); out = np.full_like(x, np.nan); L = x.shape[-1]
    if n <= 0 or L < n + (1 if prior else 0):
        return out
    fin = np.isfinite(x); xf = np.where(fin, x, -np.inf)
    m = maximum_filter1d(xf, size=n, axis=-1, mode='constant', cval=-np.inf, origin=(n - 1) // 2)   # m[k] = max(x[k - n + 1 .. k])
    cnt = np.concatenate([np.zeros(x.shape[:-1] + (1,)), np.cumsum(fin, axis=-1)], axis=-1)
    k = np.arange(n - 1, L); have = cnt[..., k + 1] - cnt[..., k + 1 - n]
    val = np.where(have > 0, m[..., k], np.nan)
    if prior:
        out[..., n:] = val[..., :-1]
    else:
        out[..., n - 1:] = val
    return out


def lag(x, n):
    out = np.full_like(x, np.nan)
    if n < x.shape[-1]:
        out[..., n:] = x[..., :-n] if n else x
    return out


class Ctx:
    """one day's evaluation: ext arrays span D-1, D, D+1 on the 5 s clock (3 x NB); i0 = D's first row"""

    def __init__(self, dfn, src, day, coins, hist):
        self.d = dfn; self.src = src; self.day = day; self.coins = coins; self.hist = hist; self.memo = {}
        self.i0 = NB; self.days = (shift(day, -1), day, shift(day, 1)); self.mirror = False
        self.t = day0(shift(day, -1)) + BASE_S * np.arange(3 * NB)
        self.need = None                                   # (coins, 1440) minutes where a slow percentile is needed (None = all)
        self.read_last = None                              # S06 rule 2: no value of a day after this is read (labels crossing it: NOT KNOWN)

    def code(self, code):
        m = self.d.get('mirror', {}) if self.mirror else {}
        neg = False
        if code in m:
            if m[code] == '-':
                neg = True
            else:
                code = m[code]
        x = np.concatenate([self.src.code(code, dd, self.coins) if self.ok_day(dd) else np.full((len(self.coins), NB), np.nan)
                            for dd in self.days], axis=1)
        return -x if neg else x

    def ok_day(self, dd):
        return self.read_last is None or dd <= self.read_last

    def market(self, code):
        x = np.concatenate([self.src.market(code, dd) if self.ok_day(dd) else np.full(NB, np.nan) for dd in self.days])
        return np.broadcast_to(x, (len(self.coins), len(x))).copy()

    def price(self):
        x = np.concatenate([self.src.price(dd, self.coins) if self.ok_day(dd) else np.full((len(self.coins), NB), np.nan)
                            for dd in self.days], axis=1)
        return -x if self.mirror and self.d.get('mirror', {}).get('PRICE') == '-' else x   # the sign plant of a price alarm: price mirrored

    def get(self, name):
        if name not in self.memo:
            self.memo[name] = self.op(self.d['inputs'][name])
        return self.memo[name]

    def val(self, ref):
        return self.get(ref) if isinstance(ref, str) else np.full((len(self.coins), 3 * NB), float(ref))

    def op(self, s):
        o = s['op']; n = lambda w: int(w) // BASE_S
        if o == 'raw':
            return self.code(s['code'])
        if o == 'market':
            return self.market(s['code'])
        if o == 'price':
            return self.price()
        if o == 'sum':
            return roll_sum(self.val(s['of']), n(s['w_s']))
        if o == 'max':
            return roll_max(self.val(s['of']), n(s['w_s']))
        if o == 'prior_max':
            return roll_max(self.val(s['of']), n(s['w_s']), prior=True)
        if o == 'prior_min':
            return -roll_max(-self.val(s['of']), n(s['w_s']), prior=True)
        if o == 'known':
            x = self.val(s['of']); return np.isfinite(x).astype(float)       # 1 where the input has a value (e.g. a running wave), else 0
        if o == 'pospart':
            x = self.val(s['of']); return np.where(np.isfinite(x), np.maximum(x, 0.0), np.nan)
        if o == 'negpart':
            x = self.val(s['of']); return np.where(np.isfinite(x), np.minimum(x, 0.0), np.nan)
        if o == 'change':
            x = self.val(s['of']); return x - lag(x, n(s['w_s']))
        if o == 'lag':
            return lag(self.val(s['of']), n(s['w_s']))
        if o == 'ratio':
            a, b = self.val(s['a']), self.val(s['b'])
            with np.errstate(divide='ignore', invalid='ignore'):
                return np.where(b != 0, a / b, np.nan)
        if o == 'mul':
            return self.val(s['a']) * self.val(s['b'])
        if o == 'add':
            return self.val(s['a']) + self.val(s['b'])
        if o == 'sub':
            return self.val(s['a']) - self.val(s['b'])
        if o == 'abs':
            return np.abs(self.val(s['of']))
        if o == 'pick':
            # pos where sign(if) > 0, neg where < 0, NaN where 0 or unknown (e.g. the dominant forced side's own series)
            c = self.val(s['if']); a, b = self.val(s['pos']), self.val(s['neg'])
            tie = {'pos': a, 'neg': b}.get(s.get('tie'), np.full_like(a, np.nan))   # tie: what sign 0 reads ('pos', 'neg', default NaN)
            return np.where(c > 0, a, np.where(c < 0, b, np.where(c == 0, tie, np.nan)))
        if o == 'maxof':
            return np.maximum(self.val(s['a']), self.val(s['b']))
        if o == 'neg':
            return -self.val(s['of'])
        if o == 'sign':
            x = self.val(s['of']); return np.where(np.isfinite(x), np.sign(x), np.nan)
        if o == 'accel':
            # n rising 5 s rows in a row: x[k] > x[k-1] > ... > x[k-n], and x[k-n] > 0 (the first print is real)
            x = self.val(s['of']); k = int(s['n']); ok = np.isfinite(x) & (lag(x, k) > 0)
            for j in range(k):
                ok &= lag(x, j) > lag(x, j + 1)
            return np.where(np.isfinite(x) & np.isfinite(lag(x, k)), ok.astype(float), np.nan)
        if o == 'hour_block':
            h = ((self.t % 86400) // 3600) // int(s['h'])
            return np.broadcast_to(h.astype(float), (len(self.coins), 3 * NB)).copy()
        if o in ('trail_pct', 'own_pct'):
            return self.pct(s)
        if o in ('ev_since', 'ev_side', 'ev_value', 'ext_since_ev'):
            return self.event_op(s)
        raise ValueError('op %r is not in the registry' % o)

    def event_op(self, s):
        """the coin's most recent event of an event list at or before each row, within w_s (else NaN), inside the list's cover:
        ev_since = seconds since it; ev_side = its side; ev_value = input `of` at the event row; ext_since_ev = the extreme of `of`
        from the event row to this row (the min after a down event, the max after an up event)"""
        ev = self.src.events[s['events']]; cov = self.d.get('events_cover', {}).get(s['events'])
        if cov is None:
            raise ValueError('events %r: events_cover is required' % s['events'])
        lo_t, hi_t = day0(cov[0]), day0(shift(cov[1], 1)); w = float(s.get('w_s', 86400))
        x = self.val(s['of']) if 'of' in s else None; out = np.full((len(self.coins), 3 * NB), np.nan)
        for i, c in enumerate(self.coins):
            if c not in ev:
                continue
            te, sd = ev[c]; j = np.searchsorted(te, self.t, side='right') - 1; ok = j >= 0
            jj = np.maximum(j, 0); age = self.t - te[jj]; ok &= (age <= w) & (te[jj] >= lo_t) & (self.t < hi_t)
            if s['op'] == 'ev_since':
                out[i] = np.where(ok, age, np.nan)
            elif s['op'] == 'ev_side':
                out[i] = np.where(ok, sd[jj], np.nan)
            else:
                er = np.clip(((te[jj] - self.t[0]) // BASE_S).astype(int), 0, 3 * NB - 1)   # the event's row (5 s clock)
                if s['op'] == 'ev_value':
                    out[i] = np.where(ok & (te[jj] >= self.t[0]), x[i, er], np.nan)
                else:
                    for k in np.unique(j[ok]):
                        rows = np.flatnonzero(ok & (j == k)); r0 = int(er[rows[0]])
                        if te[k] < self.t[0]:
                            continue                                   # the event is before the 3-day span: its extreme is not known here
                        seg = x[i, r0:rows[-1] + 1]
                        mode = s.get('mode', 'side')                # 'side' (min after a down event), 'min' or 'max'
                        use_min = mode == 'min' or (mode == 'side' and sd[k] < 0)
                        acc = np.fmin.accumulate(seg) if use_min else np.fmax.accumulate(seg)
                        out[i, rows] = acc[rows - r0]
        return out

    def pct(self, s):
        """walk-forward percentiles from minute samples of an input BEFORE t (state kept across days in self.hist):
        own_pct: the coin's prior `days` whole days (constant over D); trail_pct: the w_s seconds before t (D's earlier minutes too)"""
        name = s['of']; x = self.val(name); q = float(s['q']); out = np.full_like(x, np.nan)
        H = self.hist.setdefault(name, {})
        if s['op'] == 'own_pct':
            # onset_band_v6.edges on the coin's minute samples of the 14 built days before D (its HIST_MIN / DAY_SHARE rules)
            nd = max([len(H.get(c, [])) for c in self.coins] + [0]); hh = []
            for k in range(nd, 0, -1):
                a = np.full((len(self.coins), 1440), np.nan)
                for i, c in enumerate(self.coins):
                    if len(H.get(c, [])) >= k:
                        a[i] = H[c][-k][1]
                hh.append(a)
            e = OB.edges(hh, q, s.get('floor'))
            if e is not None:
                out[:, self.i0:2 * self.i0] = e[:, None]
            return out
        for i, c in enumerate(self.coins):
            past = H.get(c, [])                                      # [(day, minute samples of that day)] before D
            if s['op'] == 'own_pct':
                continue
            else:
                w = int(s['w_s']) // 60; mn = int(s.get('min_n', 1))
                prev = np.concatenate([v for dd, v in past]) if past else np.zeros(0)
                today = x[i, self.i0:2 * self.i0:12]                  # D's minute samples (index 12k = D0 + 60k)
                allm = np.concatenate([prev, today]); base = len(prev)
                for k in range(1440):
                    if self.need is not None and not self.need[i, k]:
                        continue
                    lo = max(0, base + k - w); seg = allm[lo:base + k]; seg = seg[np.isfinite(seg)]
                    if len(seg) >= mn:
                        out[i, self.i0 + 12 * k:self.i0 + 12 * (k + 1)] = np.percentile(seg, q)
        return out

    def push_hist(self, keep_days):
        """after D is done: remember D's minute samples of every percentile source"""
        for name in self.pct_sources():
            x = self.get(name); H = self.hist.setdefault(name, {})
            for i, c in enumerate(self.coins):
                H.setdefault(c, []).append((self.day, x[i, self.i0:2 * self.i0:12].copy()))
                H[c] = H[c][-keep_days:]

    def pct_sources(self):
        return sorted({s['of'] for s in self.d['inputs'].values() if s['op'] in ('trail_pct', 'own_pct')})


def keep_days(dfn):
    k = 1
    for s in dfn['inputs'].values():
        if s['op'] == 'own_pct':
            k = max(k, OB.HIST_MAX)
        if s['op'] == 'trail_pct':
            k = max(k, int(np.ceil(int(s['w_s']) / 86400.0)) + 1)
    return k


# ---------------------------------------------------------------- conditions, fires, base candidates
def cond_mask(ctx, c):
    a = ctx.val(c['lhs']); b = ctx.val(c['rhs']); ok = np.isfinite(a) & np.isfinite(b)
    m = {'>=': a >= b, '<=': a <= b, '>': a > b, '<': a < b, 'samesign': np.sign(a) * np.sign(b) > 0, 'oppsign': np.sign(a) * np.sign(b) < 0}[c['cmp']]
    return np.where(ok, m, False), ok


def slow(dfn, ref, seen=None):
    """does an input depend on a trailing percentile (the one slow op)?"""
    if not isinstance(ref, str):
        return False
    s = dfn['inputs'][ref]
    if s['op'] == 'trail_pct':
        return True
    return any(slow(dfn, s[k]) for k in ('of', 'a', 'b') if k in s)


def conditions_known(shared_known, shared_false, claim_known, claim_false):
    """Knownness shared by BASE and GRID: a known-false shared filter decides OFF without evaluating its claim."""
    return shared_false | (shared_known & (claim_known | claim_false))


def masks(ctx):
    """(shared all true, claim all true, known) over ext rows. A known-false shared condition decides the row OFF. Otherwise known =
    every shared condition known AND the claim decided (every claim condition known, or one known false). The cheap conditions go first;
    the slow percentile is then computed only in the
    minutes where every cheap condition holds or the claim is still open (ctx.need), which never changes a decided row."""
    n = len(ctx.coins); sh = np.ones((n, 3 * NB), bool); cl = sh.copy(); shk = sh.copy(); clk = sh.copy(); clf = np.zeros_like(sh)
    shf = np.zeros_like(sh)                                         # a false prefilter stays decided even if its claim is not evaluated
    conds = ctx.d['conditions']; fast = [c for c in conds if not (slow(ctx.d, c['lhs']) or slow(ctx.d, c['rhs']))]
    late = [c for c in conds if c not in fast]
    for group in (fast, late):
        if group is late and late:
            cand = sh & shk & ~clf                              # rows still open after the cheap conditions
            ctx.need = cand[:, ctx.i0:2 * ctx.i0].reshape(n, 1440, 12).any(axis=2)
        for c in group:
            m, ok = cond_mask(ctx, c)
            if c['role'] == 'shared':
                sh &= m; shk &= ok; shf |= ok & ~m
            else:
                cl &= m; clk &= ok; clf |= ok & ~m
    ctx.need = None
    return sh, cl, conditions_known(shk, shf, clk, clf)


def side_of(ctx):
    s = ctx.d['fire']['side']; x = ctx.val(s['input']); return np.where(np.isfinite(x), np.sign(x) * int(s.get('sign', 1)), 0).astype(int)


def find_fires(ctx, last_fire):
    """D's fires: grid steps where shared and claim all hold (onset: the grid step before did not), side != 0, refractory from the
    coin's last fire (carried across midnight in last_fire). -> list of (coin index, ext row)"""
    sh, cl, kn = masks(ctx); allm = sh & cl; side = side_of(ctx)
    gs = ctx.d['grid_s'] // BASE_S; f = ctx.d['fire']; refr = int(f.get('refractory_s', 0))
    rows = np.arange(ctx.i0, 2 * ctx.i0, gs); out = []
    for i, c in enumerate(ctx.coins):
        hit = rows[allm[i, rows] & (side[i, rows] != 0)]
        if f.get('onset', True):
            hit = hit[~allm[i, hit - gs] & kn[i, hit - gs]]          # onset: the grid step before is KNOWN and not all true
        for r in hit:
            t = float(ctx.t[r])
            if t - last_fire.get(c, -1e18) < refr:
                continue
            last_fire[c] = t; out.append((i, int(r)))
    return out, sh, cl, kn, side


def base_rows(ctx, sh, cl, kn, side, fires, cap, rng, loose=False, prev_last=None):
    """candidate comparison rows of D per coin: fair = every shared condition true AND the claim false (LEAD/LAB1: same in every way but
    the claim), known inputs, side != 0, not within the refractory (or 1800 s) AFTER one of the coin's PAST fires (S06 rule 2: a later
    fire never removes a candidate; prev_last = the coin's last fire before D); loose = any known grid row.
    At most `cap` per coin-day, drawn with the seeded rng."""
    gs = ctx.d['grid_s'] // BASE_S; rows = np.arange(ctx.i0, 2 * ctx.i0, gs)
    away = max(int(ctx.d['fire'].get('refractory_s', 0)), 1800); out = []
    fr = {}
    for i, r in fires:
        fr.setdefault(i, []).append(ctx.t[r])
    for i, c in enumerate(ctx.coins):
        m = (kn[i, rows] if loose else (sh[i, rows] & ~cl[i, rows] & kn[i, rows])) & (side[i, rows] != 0)
        rr = rows[m]
        past = sorted(fr.get(i, []) + ([prev_last[c]] if prev_last and c in prev_last else []))
        if past and len(rr):
            ft = np.array(past); tt = ctx.t[rr]; j = np.searchsorted(ft, tt, side='right') - 1     # the last fire AT or BEFORE t
            near = (j >= 0) & ((tt - ft[np.maximum(j, 0)]) < away)
            rr = rr[~near]
        if len(rr) > cap:
            rr = np.sort(rng.choice(rr, cap, replace=False))
        out += [(i, int(r)) for r in rr]
    return out


# ---------------------------------------------------------------- the label registry (no price in any label)
def label_values(ctx, lab, pts, sides):
    """for points (coin index, ext row) and their sides -> dict of arrays: value (primary measure), hit (0/1), after6 (the share of the
    value landing after t + 6 s, or hit counted from t + 6 s), pre (the same measure over the window just BEFORE t: LAB1 MUST 2)"""
    k = lab['kind']; st, en = int(lab.get('start_s', 0)), int(lab['end_s']); w = en - st
    n = len(pts); val = np.full(n, np.nan); hit = np.full(n, np.nan); a6 = np.full(n, np.nan); pre = np.full(n, np.nan)
    if not n:
        return dict(value=val, hit=hit, after6=a6, pre=pre)
    if k == 'forced_usd':
        L = {s: np.concatenate([ctx.src.code(SIDE_LIQ[s], dd, ctx.coins) if ctx.ok_day(dd) else np.full((len(ctx.coins), NB), np.nan)
                                for dd in ctx.days], axis=1) for s in (1, -1)}
        cs = {s: np.concatenate([np.zeros((len(ctx.coins), 1)), np.cumsum(np.nan_to_num(L[s]), axis=1)], axis=1) for s in L}
        nan_cs = {s: np.concatenate([np.zeros((len(ctx.coins), 1)), np.cumsum(~np.isfinite(L[s]), axis=1)], axis=1) for s in L}
        thr = lab.get('thr_usd', None); mult = lab.get('thr_mult_pre', None)
        ti = ctx.get(lab['thr_input']) if lab.get('thr_input') else None      # a threshold known at t (e.g. the coin's own 14-day band)
        for j, ((i, r), s) in enumerate(zip(pts, sides)):
            ss = s if lab.get('dir', 'same') == 'same' else -s
            # A1 row r covers (t_r - 5, t_r]: the window (t + st, t + en] is rows r + st/5 + 1 .. r + en/5
            a, b = r + st // BASE_S + 1, r + en // BASE_S + 1
            if lab.get('when') == 'present':                   # P02-06: a DETECT reference, (t - en, t], the event AT the fire
                a, b = r - en // BASE_S + 1, r + 1
                if a < 0 or nan_cs[ss][i, b] - nan_cs[ss][i, a] > 0:
                    continue
                val[j] = cs[ss][i, b] - cs[ss][i, a]
                hit[j] = float(val[j] >= ti[i, r]) if ti is not None and np.isfinite(ti[i, r]) else (float(val[j] >= float(thr)) if thr is not None else float(val[j] > float(lab.get('floor_usd', 0))))
                continue
            if b > cs[ss].shape[1] - 1 or nan_cs[ss][i, b] - nan_cs[ss][i, a] > 0:
                continue
            val[j] = cs[ss][i, b] - cs[ss][i, a]
            a2 = r + max(st, 6) // BASE_S + 1                           # 5 s rows: 'after +6 s' = the rows after t + 5 s (row r + 2 on)
            v6 = cs[ss][i, b] - cs[ss][i, min(a2, b)]; a6[j] = v6 / val[j] if val[j] > 0 else np.nan
            p0 = r - w // BASE_S + 1
            if p0 >= 0 and nan_cs[ss][i, r + 1] - nan_cs[ss][i, p0] == 0:
                pre[j] = cs[ss][i, r + 1] - cs[ss][i, p0]
            if ti is not None:
                hit[j] = float(val[j] >= ti[i, r]) if np.isfinite(ti[i, r]) else np.nan
            elif thr is not None:
                hit[j] = float(val[j] >= float(thr))
            elif mult is not None and np.isfinite(pre[j]):
                hit[j] = float(val[j] >= float(mult) * max(pre[j], float(lab.get('floor_usd', 0))))
            else:
                hit[j] = float(val[j] > float(lab.get('floor_usd', 0)))
    elif k == 'event_within':
        ev = ctx.src.events[lab['events']]
        cov = ctx.d.get('events_cover', {}).get(lab['events'])            # the list's own days: outside them the label is NOT KNOWN, never 0
        if cov is None:
            raise ValueError('events %r: events_cover [first, last] is required (a missing day must never read as no event)' % lab['events'])
        lo_t, hi_t = day0(cov[0]), day0(shift(cov[1], 1))
        if ctx.read_last is not None:
            hi_t = min(hi_t, day0(shift(ctx.read_last, 1)))                # S06 rule 2: an event after the run's last day is never read
        for j, ((i, r), s) in enumerate(zip(pts, sides)):
            c = ctx.coins[i]; t = float(ctx.t[r]); ss = s if lab.get('dir', 'same') == 'same' else -s
            pre_ok = t - w >= lo_t and t <= hi_t
            if t + st < lo_t or t + en > hi_t:
                if pre_ok and c in ev:
                    pre[j] = float(np.any((ev[c][1] == ss) & (ev[c][0] > t - w) & (ev[c][0] <= t)))
                continue
            if c not in ev:
                val[j] = np.nan; hit[j] = 0.0; a6[j] = 0.0; pre[j] = 0.0 if pre_ok else np.nan; continue
            te, sd = ev[c]; m = sd == ss
            x = te[m & (te > t + st) & (te <= t + en)]
            hit[j] = float(len(x) > 0); val[j] = float(x[0] - t) if len(x) else np.nan
            a6[j] = float(len(te[m & (te > t + max(st, 6)) & (te <= t + en)]) > 0)
            pre[j] = float(np.any(m & (te > t - w) & (te <= t))) if pre_ok else np.nan
    else:
        raise ValueError('label kind %r is not in the registry' % k)
    return dict(value=val, hit=hit, after6=a6, pre=pre)


# ---------------------------------------------------------------- one day -> records
AUTO_MATCH = ('mkt_forced', 'hour_block4', 'pre_primary')
BUSY_K = 5


def busy_points(ctx, fires, rng):
    """the lab's busy base, REUSED: matched_controls_v1.draw (same coin and day, within 6 h, range-matched 0.75-1.33 x, 1800 s away from
    the coin's fires and the definition's busy_avoid events, side = the moment's own 30 min push) -> (points, sides, sets per fire)"""
    pts, sds, sets = [], [], []; d0 = day0(ctx.day)
    av_ev = [ctx.src.events[n] for n in ctx.d['base'].get('busy_avoid', []) if n in ctx.src.events]
    allf = {}
    for i, r in fires:
        allf.setdefault(i, []).append(float(ctx.t[r]))
    for i, r in fires:
        c = ctx.coins[i]; te, px = ctx.src.bins(ctx.day, c)
        avoid = list(allf[i]) + [x for ev in av_ev if c in ev for x in ev[c][0].tolist()]
        ct, cs = MC.draw(te, px, int(ctx.t[r]), d0, avoid, BUSY_K, rng); idx = []
        for tc, sc in zip(ct, cs):
            rr = ctx.i0 + (int(tc) - d0) // BASE_S
            if ctx.i0 <= rr < 2 * ctx.i0:
                pts.append((i, int(rr))); sds.append(int(sc)); idx.append(len(pts) - 1)
        sets.append(np.array(idx, int))
    return pts, sds, sets


def day_records(ctx, last_fire, rng, cap, mode='all'):
    """D's fire records and candidate base records (fair and loose); each a dict of arrays"""
    prev_last = dict(last_fire)
    fires, sh, cl, kn, side = find_fires(ctx, last_fire)
    out = {'FIRE': fires}; over = {}; bsets = []
    if mode == 'all':
        out['FAIR'] = base_rows(ctx, sh, cl, kn, side, fires, cap, rng, prev_last=prev_last)
        out['BUSY'], over['BUSY'], bsets = busy_points(ctx, fires, rng)
    mk = ctx.market('A2.S05') + ctx.market('A2.S06')               # LEAD change 3: the market's forcing at t (coins forced in the minute)
    hb = ((ctx.t % 86400) // 3600) // 4
    oi = ctx.code('E2.S02'); px = ctx.price() if ctx.d.get('oi_usd', True) else None
    recs = {}
    for kind, pts in out.items():
        sd = np.array(over[kind], int) if kind in over else np.array([side[i, r] for i, r in pts], int)
        R = {'coin': np.array([ctx.coins[i] for i, r in pts], object), 't': np.array([ctx.t[r] for i, r in pts], float), 'side': sd}
        for nm in ctx.d['inputs']:
            x = ctx.get(nm); R['in_' + nm] = np.array([x[i, r] for i, r in pts], float)
        R['mkt_forced'] = np.array([mk[i, r] for i, r in pts], float); R['hour_block4'] = np.array([hb[r] for i, r in pts], float)
        R['oi_usd'] = np.array([oi[i, r] * px[i, r] if px is not None else np.nan for i, r in pts], float)
        for lab in ctx.d['truth']:
            lv = label_values(ctx, lab, pts, sd)
            for f, v in lv.items():
                R['lab_%s_%s' % (lab['name'], f)] = v
        R['pre_primary'] = R['lab_%s_pre' % ctx.d['primary']]
        recs[kind] = R
    recs['_busy_sets'] = bsets
    return recs


def cat_recs(lst):
    lst = [x for x in lst if len(x['t'])]
    if not lst:
        return None
    return {k: np.concatenate([x[k] for x in lst]) for k in lst[0]}


# ---------------------------------------------------------------- matching (fair, fair without the persistence term, loose)
def match(F, B, keys, scope, k, caliper, rng, exact=('hour_block4',), why=None):
    """for each fire: up to k comparison rows of the same coin and scope (month or day), the same exact keys, every other key within
    `caliper` in percentile rank (ranks taken over fires + candidates of that coin-scope), nearest first; a comparison row serves one
    fire at most. -> list (per fire) of index arrays into B. why (a dict, S06 rule 4): per fire 'code' (0 matched, 1 no candidate in its
    scope, 2 none with its exact keys, 3 none within the caliper, 4 all taken by other fires) and 'pool' (candidates in its scope)"""
    if scope == 'time30':                                   # any coin, the same 30 min of the clock (e.g. the same market wave)
        fk = [(None, int(t // 1800)) for t in F['t']]; bk = [(None, int(t // 1800)) for t in B['t']] if B is not None else []
    else:
        sc = (lambda t: utc_day(t)[:6]) if scope == 'coin-month' else utc_day
        fk = [(c, sc(t)) for c, t in zip(F['coin'], F['t'])]; bk = [(c, sc(t)) for c, t in zip(B['coin'], B['t'])] if B is not None else []
    groups = {}
    for j, g in enumerate(bk):
        groups.setdefault(g, []).append(j)
    cont = [x for x in keys if x not in exact]; used = set(); out = [None] * len(F['t'])
    for g in sorted(set(fk)):
        fi = [i for i, x in enumerate(fk) if x == g]; bj = np.array(groups.get(g, []), int)
        if not len(bj):
            for i in fi:
                out[i] = np.zeros(0, int)
                if why is not None:
                    why[i] = (1, 0)
            continue
        R = {}
        for x in cont:
            allv = np.concatenate([F[x][fi], B[x][bj]]); ok = np.isfinite(allv)
            r = np.full(len(allv), np.nan)
            if ok.any():
                o = allv[ok]; srt = np.sort(o)
                lo = np.searchsorted(srt, o, 'left'); hi = np.searchsorted(srt, o, 'right')
                r[ok] = ((lo + hi) / 2.0) / len(o)                    # tie-aware rank (average ranks; the AUC lesson)
            R[x] = (r[:len(fi)], r[len(fi):])
        for a, i in enumerate(fi):
            m = np.ones(len(bj), bool)
            for x in exact:
                m &= B[x][bj] == F[x][i]
            dist = np.zeros(len(bj))
            for x in cont:
                fr, br = R[x]
                if not np.isfinite(fr[a]):
                    m &= ~np.isfinite(br)
                    continue
                dd = np.abs(br - fr[a]); m &= np.isfinite(dd) & (dd <= caliper); dist += np.nan_to_num(dd) ** 2
            cand = [j for j in np.argsort(dist + rng.random(len(dist)) * 1e-9) if m[j] and bj[j] not in used][:k]
            out[i] = bj[cand]; used.update(bj[cand].tolist())
            if why is not None:
                mx = np.ones(len(bj), bool)
                for x in exact:
                    mx &= B[x][bj] == F[x][i]
                why[i] = (0 if cand else (2 if not mx.any() else (3 if not m.any() else 4)), len(bj))
    return out


def balance_lines(F, B, S, keys):
    """S06 rule 4: per match key, the fires' mean vs the whole candidate pool (before) and vs their matched rows (after), as a
    standardised difference (mean gap over the pooled sd); and the common support (share of fires with any candidate in scope)"""
    L = []
    if B is None or not len(B['t']):
        return ['balance: no candidate pool']
    used = np.array(sorted({int(j) for s_ in S for j in s_}), int); mf = np.array([len(s_) > 0 for s_ in S])
    for x in keys:
        f = F[x][np.isfinite(F[x])]; b = B[x][np.isfinite(B[x])]; u = B[x][used] if len(used) else np.zeros(0); u = u[np.isfinite(u)]
        fm = F[x][mf]; fm = fm[np.isfinite(fm)]
        sd = np.std(np.concatenate([f, b])) if len(f) and len(b) else np.nan
        smd = lambda a, c: (np.mean(a) - np.mean(c)) / sd if len(a) and len(c) and sd > 0 else np.nan
        L.append('balance %-14s before %+.2f (fires %d vs pool %d) after %+.2f (matched fires %d vs used %d)' % (x, smd(f, b), len(f), len(b), smd(fm, u), len(fm), len(u)))
    L.append('common support: %d of %d fires matched; unmatched by reason (1 no pool, 2 no exact key, 3 outside caliper, 4 taken): %s' % (
        int(mf.sum()), len(S), ', '.join('%d:%d' % (c, int(np.sum(F['match_code'] == c))) for c in (1, 2, 3, 4))))
    return L


# ---------------------------------------------------------------- run one window (a month job)
def run(dfn, first, last, src, cap=300, log=print, warm=None, mode='all'):
    """-> (records by kind, matched sets by base name, settings); warm-up days before `first` fill the percentile history and the
    refractory chain, nothing from them is kept"""
    rng = np.random.default_rng(int(dfn['base'].get('seed', 23102026)))
    kd = keep_days(dfn); warm = kd + 1 if warm is None else warm
    hist = {}; last_fire = {}; acc = {}; bsets = []; nbusy = 0
    for d in days_between(shift(first, -warm), last):
        coins = src.coins(d)
        if not coins:
            continue
        ctx = Ctx(dfn, src, d, coins, hist); ctx.read_last = last
        if d < first:
            find_fires(ctx, last_fire); ctx.push_hist(kd); continue
        rec = day_records(ctx, last_fire, rng, cap, mode)
        bs = rec.pop('_busy_sets')
        bsets += [x + nbusy for x in bs]; nbusy += len(rec['BUSY']['t']) if 'BUSY' in rec else 0
        for kind, R in rec.items():
            acc.setdefault(kind, []).append(R)
        ctx.push_hist(kd)
        log('[alarm_design] %s %s fires %d fair %d busy %d' % (dfn['id'], d, len(rec['FIRE']['t']),
                                                              len(rec.get('FAIR', {'t': []})['t']), len(rec.get('BUSY', {'t': []})['t'])))
    recs = {k: cat_recs(v) for k, v in acc.items()}
    sets = {}
    F = recs.get('FIRE')
    if F is not None and mode == 'all':
        b = dfn['base']; k = int(b.get('k', 5)); cal = float(b.get('caliper', 0.10)); scope = b.get('scope', 'coin-month')
        own = ['in_' + x for x in b.get('match_on', [])]
        mrng = np.random.default_rng(int(b.get('seed', 23102026)) + 1)
        why = {}
        sets['FAIR'] = match(F, recs.get('FAIR'), own + list(AUTO_MATCH), scope, k, cal, mrng, why=why)
        F['match_code'] = np.array([why.get(i, (1, 0))[0] for i in range(len(F['t']))], float)
        F['pool_n'] = np.array([why.get(i, (1, 0))[1] for i in range(len(F['t']))], float)
        recs['_balance'] = balance_lines(F, recs.get('FAIR'), sets['FAIR'], own + list(AUTO_MATCH))
        sets['FAIR_NOPRE'] = match(F, recs.get('FAIR'), own + ['mkt_forced', 'hour_block4'], scope, k, cal, mrng)
        sets['BUSY'] = bsets
    return recs, sets


# ---------------------------------------------------------------- waves, statistics, the verdict
def waves(t, gap=1800):
    o = np.argsort(t, kind='mergesort'); w = np.zeros(len(t), int); cur = 0
    for a, b in zip(o[:-1], o[1:]):
        if t[b] - t[a] > gap:
            cur += 1
        w[b] = cur
    return w


def episodes(coin, t, gap=1800):
    e = np.zeros(len(t), int); nxt = 0
    for c in sorted(set(coin.tolist())):
        ix = np.flatnonzero(coin == c); ix = ix[np.argsort(t[ix], kind='mergesort')]; last = -1e18
        for i in ix:
            if t[i] - last > gap:
                nxt += 1
            e[i] = nxt; last = t[i]
    return e


def gap_by_wave(y, base_sets, by, w, sel):
    """per fire: d = y - mean(base y over its set); per wave: mean d; -> (wave ids, wave means, n fires used, fire share, base share)"""
    d = np.full(len(y), np.nan); bm = np.full(len(y), np.nan)
    for i in np.flatnonzero(sel):
        s = base_sets[i]
        if s is None or not len(s) or not np.isfinite(y[i]):
            continue
        v = by[s]; v = v[np.isfinite(v)]
        if len(v):
            bm[i] = v.mean(); d[i] = y[i] - bm[i]
    ok = np.isfinite(d)
    ws = np.unique(w[ok]); wm = np.array([d[ok & (w == x)].mean() for x in ws])
    return ws, wm, int(ok.sum()), (float(np.nanmean(y[ok])) if ok.any() else NAN), (float(np.nanmean(bm[ok])) if ok.any() else NAN), d


def boot_ci(wm, rng, n=2000):
    if len(wm) < 2:
        return (NAN, NAN)
    b = rng.integers(0, len(wm), (n, len(wm))); m = wm[b].mean(axis=1)
    return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)))


def flip_p(wm, rng, n=2000):
    if not len(wm):
        return NAN
    s = rng.choice((-1.0, 1.0), (n, len(wm))); m = (s * wm).mean(axis=1)
    return float((np.sum(m >= wm.mean()) + 1) / (n + 1))


def verdict(pooled_lo, months_pos, months_n, ex5, pooled_hi=np.nan, min_effect=0.05):
    """one order (OUTSIDE S07 rule 5; LAB1 MUST 4): TRUE_FOR_REFERENCE = pooled wave interval above 0 AND the same sign in >= 7 of 9
    months (scaled) AND positive without the 5 best days; NOT_SUPPORTED only when PRECISE: the interval's top is under the frozen
    min_effect; anything else UNSURE (gather more, never a kill)"""
    need = 7 if months_n >= 9 else int(np.ceil(months_n * 7 / 9.0))
    if np.isfinite(pooled_lo) and pooled_lo > 0 and months_pos >= need and np.isfinite(ex5) and ex5 > 0:
        return 'TRUE_FOR_REFERENCE'
    if np.isfinite(pooled_hi) and pooled_hi < min_effect:
        return 'NOT_SUPPORTED'
    return 'UNSURE'


def best_days_out(d, F, w, ndays=5):
    """the per-wave gap after removing the 5 days whose fires add the most gap"""
    day = np.array([utc_day(t) for t in F['t']]); ok = np.isfinite(d)
    tot = {}
    for dd, x in zip(day[ok], d[ok]):
        tot[dd] = tot.get(dd, 0.0) + x
    drop = set(sorted(tot, key=lambda x: -tot[x])[:ndays])
    keep = ok & ~np.isin(day, list(drop))
    ws = np.unique(w[keep]); return float(np.mean([d[keep & (w == x)].mean() for x in ws])) if len(ws) else NAN


def months_list(first, last):
    m = []; d = first[:6]
    while d <= last[:6]:
        m.append(d); y, mo = int(d[:4]), int(d[4:]); d = '%04d%02d' % (y + (mo == 12), 1 if mo == 12 else mo + 1)
    return m


def card(dfn, F, B, sets, regimes=None, tries=1, n_draw=2000, windows=None):
    """the truth card text + a JSON summary"""
    rng = np.random.default_rng(7)
    P = dfn['primary']; y = F['lab_%s_hit' % P]; w = waves(F['t']); ep = episodes(F['coin'], F['t'])
    day = np.array([utc_day(t) for t in F['t']]); mon = np.array([x[:6] for x in day]); crash = np.isin(day, ['20251010', '20251011'])
    first, last = dfn['window']['first'], dfn['window']['last']; months = months_list(first, last)
    if windows is not None:
        months = [m for m in months if m in windows['build_months']]          # CHECK months get no row at all
    L = ['TRUTH CARD %s v%s (definition sha16 %s; tool alarm_design.py %s)' % (dfn['id'], dfn['version'], dfn['_sha16'], sha16_file(os.path.realpath(__file__))),
         'claim: %s' % dfn['claim'].get('one_line', ''),
         'primary label: %s; window %s..%s; tries in this family: %d (each scored version is one try)' % (P, first, last, tries),
         'claim type %s; trigger footprint %d s before t; decision t, arrival t + 6 s; primary label (t + %s, t + %s] s; policy CHECK_WINDOW_RULE_V3 + RUN_GATE_V1 (S07 rules 1-3); '
         'verdict names: TRUE_FOR_REFERENCE (the label only; mechanism needs attribution), NOT_SUPPORTED (precise), UNSURE' % (
             dfn['claim']['type'], dfn['claim']['footprint_s'], [t for t in dfn['truth'] if t['name'] == P][0].get('start_s', 0),
             [t for t in dfn['truth'] if t['name'] == P][0]['end_s']),
         'estimand (S06 rule 1): ALARM-TIME CONDITIONAL PREDICTION, not a causal effect: at the decision time t, among moments that share every '
         'shared condition and the matched readings known at t, do fires see the claimed forced event more often? Base sides come from the '
         'same side rule at the base moment (not borrowed from the fire, S06 rule 5); a base moment is excluded only after a PAST fire.',
         'counts: fires %d, coins %d, days %d, fires per coin-day %.2f, waves (any coin within 30 min) %d, same-coin episodes %d' % (
             len(y), len(set(F['coin'].tolist())), len(set(day.tolist())), len(y) / max(1, len(set(zip(F['coin'].tolist(), day.tolist())))),
             len(set(w.tolist())), len(set(ep.tolist()))), '']
    summ = {'id': dfn['id'], 'version': dfn['version'], 'sha16': dfn['_sha16'], 'fires': int(len(y)), 'waves': int(len(set(w.tolist()))), 'months': {}}
    for bname in ('FAIR', 'FAIR_NOPRE', 'BUSY'):
        if bname not in sets:
            continue
        Bk = B.get(bname); S = sets[bname]
        if Bk is None:
            continue
        by = Bk['lab_%s_hit' % P]
        unmatched = sum(1 for s in S if s is None or not len(s))
        L.append('BASE %s (%s): unmatched fires %d of %d (%.1f pct)' % (bname, {'FAIR': 'shared true, claim false, matched on own inputs + market forcing + hour + the label just before t',
                 'FAIR_NOPRE': 'as FAIR without the label-just-before term (LAB1 MUST 2: the gap with and without it)', 'BUSY': 'RETROSPECTIVE QUIET REFERENCE (S06 rule 2): matched_controls_v1 excludes moments near alarms on both sides, so it is never the verdict, reading only'}[bname],
                 unmatched, len(S), 100.0 * unmatched / max(1, len(S))))
        L.append('  %-8s %6s %6s %5s %8s %8s %8s %18s %7s %s' % ('month', 'fires', 'used', 'waves', 'fire', 'base', 'gap', 'wave 95 pct', 'p', 'regime'))
        res = {}
        for m in ['ALL', 'EX_CRASH'] + months:
            sel = np.ones(len(y), bool) if m == 'ALL' else (~crash if m == 'EX_CRASH' else mon == m)
            ws, wm, nu, fs, bs, d = gap_by_wave(y, S, by, w, sel)
            lo, hi = boot_ci(wm, rng, n_draw); p = flip_p(wm, rng, n_draw); g = float(wm.mean()) if len(wm) else NAN
            res[m] = dict(fires=int(sel.sum()), used=nu, waves=int(len(ws)), fire=fs, base=bs, gap=g, lo=lo, hi=hi, p=p)
            L.append('  %-8s %6d %6d %5d %8.3f %8.3f %+8.3f [%+7.3f %+7.3f] %7.4f %s' % (m, sel.sum(), nu, len(ws), fs, bs, g, lo, hi, p,
                     (regimes or {}).get(m, '-')))
        # the verdict is judged on the BUILD months of the windows settings (LAB1 11:21:59Z); CHECK months are judged apart, after
        bm = [m for m in months if windows is None or m in windows['build_months']]; cm = [m for m in months if windows is not None and m in windows['check_months']]
        selb = np.isin(mon, bm) if windows is not None else np.ones(len(y), bool)
        ws, wm, nu, fs, bs, d = gap_by_wave(y, S, by, w, selb)
        lob, hib = boot_ci(wm, rng, n_draw); ex5 = best_days_out(d, F, w)
        mp = sum(1 for m in bm if np.isfinite(res[m]['gap']) and res[m]['gap'] > 0); mn = sum(1 for m in bm if res[m]['used'] > 0)
        v = verdict(lob, mp, mn, ex5, hib, float(dfn['base'].get('min_effect', 0.05)))
        if windows is not None:
            L.append('  BUILD %s..%s pooled gap %+.3f [%+.3f %+.3f] (the verdict reads BUILD only; CHECK %s is NOT read here: freeze_judge only) settings %s' % (
                bm[0] if bm else '-', bm[-1] if bm else '-', float(wm.mean()) if len(wm) else NAN, lob, hib, ','.join(windows['check_months']), windows.get('_sha16', '-')))
        L.append('  ex the 5 best days: gap %+.3f | months positive %d of %d with fires | method v3 size line +0.05: %s | VERDICT (%s): %s' % (
            ex5, mp, mn, 'met' if np.isfinite(res['ALL']['gap']) and res['ALL']['gap'] >= 0.05 else 'not met', bname, v))
        if regimes:
            rg = {}
            for m in months:
                if np.isfinite(res[m]['gap']):
                    rg.setdefault(regimes.get(m, 'untagged'), []).append(res[m]['gap'])
            L.append('  by regime: ' + '; '.join('%s %d months, %d positive' % (k, len(v_), sum(1 for x in v_ if x > 0)) for k, v_ in sorted(rg.items())))
        if bname == 'FAIR':
            # latency (LEAD change 2) and the size of the effect (LEAD change 5)
            a6 = F['lab_%s_after6' % P]; ba6 = Bk['lab_%s_after6' % P]
            ws6, wm6, *_ = gap_by_wave(a6, S, ba6, w, np.ones(len(y), bool))
            L.append('  after t + 6 s (our latency): %s' % ('gap %+.3f by wave' % wm6.mean() if len(wm6) and dfn_kind(dfn, P) == 'event_within'
                     else 'median share of the fire label landing after +6 s %.2f' % np.nanmedian(a6) if np.isfinite(np.nanmedian(a6) if len(a6) else NAN) else 'n/a'))
            for lab in dfn['truth']:
                if lab['kind'] != 'forced_usd':
                    continue
                fv = F['lab_%s_value' % lab['name']]; bv = Bk['lab_%s_value' % lab['name']]; ex = np.full(len(fv), np.nan)
                for i, s in enumerate(S):
                    if s is not None and len(s):
                        vv = bv[s]; vv = vv[np.isfinite(vv)]
                        if len(vv) and np.isfinite(fv[i]):
                            ex[i] = fv[i] - vv.mean()
                with np.errstate(invalid='ignore', divide='ignore'):
                    bp = ex / F['oi_usd'] * 1e4
                L.append('  size %s: extra forced USD per fire over the fair base median %s mean %s; as OI bp median %.2f (USD %s, coin OI from E2.S02 x price at t)' % (
                    lab['name'], fmt(np.nanmedian(ex)), fmt(np.nanmean(ex)), np.nanmedian(bp) if np.isfinite(bp).any() else NAN, 'per fire'))
        summ['months'][bname] = res; summ.setdefault('verdict', {})[bname] = v
        L.append('')
    return L, summ


def dfn_kind(dfn, name):
    return [t['kind'] for t in dfn['truth'] if t['name'] == name][0]


def fmt(x):
    return 'nan' if not np.isfinite(x) else '{:,.0f}'.format(x)


def lead_lines(F, ev, window=300):
    """seconds the fire comes before the reference event (same coin, same side) within `window`; the share that leads by > 6 s"""
    lead = []; after = 0
    for c, t, s in zip(F['coin'], F['t'], F['side']):
        if c not in ev:
            continue
        te, sd = ev[c]; m = sd == s
        if np.any(m & (te <= t) & (te > t - window)):
            after += 1; continue
        x = te[m & (te > t) & (te <= t + window)]
        if len(x):
            lead.append(x[0] - t)
    lead = np.array(lead)
    if not len(lead):
        return 'lead: no reference event within %d s of any fire; %d fires came after one' % (window, after)
    return 'lead over the reference: %d fires lead (median %.0f s, quartiles %.0f / %.0f s, share leading by > 6 s %.2f); %d fires came AFTER one (late)' % (
        len(lead), np.median(lead), np.percentile(lead, 25), np.percentile(lead, 75), float(np.mean(lead > 6)), after)


def overlap_lines(F, lists, window=300):
    out = []
    for nm, ev in lists.items():
        n = 0
        for c, t in zip(F['coin'], F['t']):
            if c in ev and np.any(np.abs(ev[c][0] - t) <= window):
                n += 1
        out.append('%s %.2f' % (nm, n / max(1, len(F['t']))))
    return 'overlap (share of fires within %d s of another alarm, same coin): %s' % (window, ', '.join(out))


# ---------------------------------------------------------------- real-data checks on every first run (LAB1 MUST 6)
def warm_state(dfn, src, day, mirror=False):
    """the percentile history and refractory chain as they stand at D 00:00 (the warm-up days of run(), replayed)"""
    import copy
    kd = keep_days(dfn); hist = {}; lf = {}
    for d in days_between(shift(day, -(kd + 1)), shift(day, -1)):
        cs = src.coins(d)
        if not cs:
            continue
        ctx = Ctx(dfn, src, d, cs, hist); ctx.mirror = mirror; find_fires(ctx, lf); ctx.push_hist(kd)
    return hist, lf


def prefix_check(dfn, src, day, n=20, log=print):
    """cut every input after t to NaN (so nothing after t can be read) and re-find, with the real history before D: each sampled fire
    at t must still fire, same side. -> (fires checked, differ); 0 checked = NOT CHECKED, never a pass"""
    import copy
    hist, lf = warm_state(dfn, src, day)
    ctx = Ctx(dfn, src, day, src.coins(day), copy.deepcopy(hist)); fires, *_, side = find_fires(ctx, dict(lf))
    rng = np.random.default_rng(1); pick = [fires[i] for i in sorted(rng.choice(len(fires), min(n, len(fires)), replace=False))] if fires else []
    bad = 0
    for i, r in pick:
        c2 = Ctx(dfn, CutSource(src, ctx.t[r]), day, ctx.coins, copy.deepcopy(hist)); f2, *_, s2 = find_fires(c2, dict(lf))
        if (i, r) not in f2 or s2[i, r] != side[i, r]:
            bad += 1
    return len(pick), bad


class CutSource:
    """a source whose every value known after `t_cut` is NaN (the prefix test)"""

    def __init__(self, src, t_cut):
        self.s = src; self.t = t_cut; self.events = src.events

    def coins(self, d):
        return self.s.coins(d)

    def _cut(self, x, d):
        x = np.array(x, float, copy=True); g = day0(d) + BASE_S * np.arange(NB); x[..., g > self.t] = np.nan; return x

    def code(self, code, d, coins):
        return self._cut(self.s.code(code, d, coins), d)

    def market(self, code, d):
        return self._cut(self.s.market(code, d), d)

    def price(self, d, coins):
        return self._cut(self.s.price(d, coins), d)


def sign_check(dfn, src, day):
    """mirror every signed input (definition 'mirror': code -> its mirror or '-' for a sign flip), history included: the same fire
    times, opposite sides. -> (fires, same times, flipped) or None without a mirror map"""
    if not dfn.get('mirror'):
        return None
    out = []
    for m in (False, True):
        hist, lf = warm_state(dfn, src, day, mirror=m)
        c = Ctx(dfn, src, day, src.coins(day), hist); c.mirror = m; f, *_, s = find_fires(c, lf); out.append((f, s))
    (f1, s1), (f2, s2) = out
    same = set(f1) == set(f2); flip = all(s1[i, r] == -s2[i, r] for i, r in f1 if (i, r) in set(f2))
    return len(f1), same, flip


# ---------------------------------------------------------------- the one-format output (research_days ADES.<ID>V<n>[_MATCH])
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')


BASES = ('FAIR', 'FAIR_NOPRE', 'BUSY')
POOL = {'FAIR': 'FAIR', 'FAIR_NOPRE': 'FAIR', 'BUSY': 'BUSY'}


def part_name(dfn, base=None):
    """ADES.<ID>V<n> (fires) and ADES.<ID>V<n>_MATCH_<BASE> (the rows each base set used: FAIR, FAIR_NOPRE, BUSY)"""
    return 'ADES.%sV%s%s' % (dfn['id'], dfn['version'], '' if base is None else '_MATCH_' + base)


def columns(dfn):
    cols = ['side', 'wave', 'set_of', 'mkt_forced', 'hour_block4', 'oi_usd', 'pre_primary', 'match_code', 'pool_n'] + ['in_' + x for x in dfn['inputs']]
    for lab in dfn['truth']:
        cols += ['lab_%s_%s' % (lab['name'], f) for f in ('value', 'hit', 'after6', 'pre')]
    return cols


def catalog_text(dfn):
    L = ['# ADES catalog of %s v%s (generated by alarm_design.py from the definition %s)' % (dfn['id'], dfn['version'], dfn['_sha16']), '\t'.join(CAT_COLS)]
    for base in (None,) + BASES:
        for c in columns(dfn):
            L.append('\t'.join(['%s.%s' % (part_name(dfn, base), c), 'ROWS', 'event', '0', 'coin', c.replace('_', ' '), '-', 'EVENT', 'alarm_design']))
    return '\n'.join(L) + '\n'


def items_of(dfn, recs, sets):
    """{part: [(records, row index, wave, set_of t)]}: the fires, then each base's used rows (set_of = the fire's t, same coin)"""
    F = recs['FIRE']; w = waves(F['t']); out = {part_name(dfn): [(F, i, w[i], -1.0) for i in range(len(F['t']))]}
    for b in BASES:
        if b in sets and recs.get(POOL[b]) is not None:
            out[part_name(dfn, b)] = [(recs[POOL[b]], int(j), w[fi], float(F['t'][fi])) for fi, s in enumerate(sets[b]) for j in (s if s is not None else [])]
    return out


def write_out(dfn, recs, sets, out_root, code_dir=CODE_DIR, sources=None, log=print, writer=None, catalog_dir=None):
    """the one format: lab3.write.write_part per day and part; as_of = the moment t, known_at = t + the primary label's end (an outcome
    row); a moment used by two fires of one base gets known_at + 1 us per repeat (rows stay unique, values unchanged)"""
    sys.path.insert(0, code_dir)
    from lab3 import write as LW
    write = writer or LW.write_part
    catp = os.path.join(catalog_dir or os.path.join(HERE, 'catalogs'), 'ADES_%sV%s_CATALOG.tsv' % (dfn['id'], dfn['version']))
    os.makedirs(os.path.dirname(catp), exist_ok=True); txt = catalog_text(dfn)
    if os.path.exists(catp) and open(catp).read() != txt:
        raise ValueError('%s differs from the definition: a changed definition is a new version' % catp)
    if not os.path.exists(catp):
        open(catp, 'x').write(txt)
    cat = LW.load_catalog(catp); end = int([t['end_s'] for t in dfn['truth'] if t['name'] == dfn['primary']][0])
    seal = json.dumps({k: v for k, v in dfn.items() if not k.startswith('_')}, sort_keys=True)
    srcs = dict(sources or {}); srcs['definition:%s' % os.path.basename(dfn['_path'])] = dfn['_sha16']
    srcs['code:alarm_design.py'] = sha16_file(os.path.realpath(__file__)); srcs['catalog:%s' % os.path.basename(catp)] = sha16_file(catp)
    done = {}
    for part, its in items_of(dfn, recs, sets).items():
        byday = {}
        for R, i, wv, so in its:
            byday.setdefault(utc_day(R['t'][i]), []).append((R, i, wv, so))
        for d, rows_ in sorted(byday.items()):
            ixp = os.path.join(out_root, 'day=%s' % d, part, 'index.json')
            if os.path.exists(ixp):
                old = json.load(open(ixp))
                if old.get('seal') == seal and old.get('sources') == srcs:
                    done[(part, d)] = 'UP TO DATE'; continue
            coins = sorted(set(R['coin'][i] for R, i, *_ in rows_)); codes = {}
            rows_ = sorted(rows_, key=lambda x: (x[0]['coin'][x[1]], x[0]['t'][x[1]], x[3]))
            seen = {}; ka = []
            for R, i, wv, so in rows_:
                a = int(round(R['t'][i] * 1e6)); key = (R['coin'][i], a); n = seen.get(key, 0); seen[key] = n + 1
                ka.append((a, a + end * 1_000_000 + n))
            for col in columns(dfn):
                rws = {c: {k: [] for k in ROWCOLS} for c in coins}
                for (R, i, wv, so), (a, k) in zip(rows_, ka):
                    v = {'wave': wv, 'set_of': so}.get(col, None)
                    v = (float(R[col][i]) if col in R else np.nan) if v is None else float(v)
                    ok = np.isfinite(v); r = rws[R['coin'][i]]
                    r['day'].append(int(d)); r['as_of_us'].append(a); r['known_at_us'].append(k); r['value_kind'].append(1)
                    r['value_bits'].append(int(np.array([v], '<f8').view('<u8')[0]) if ok else None)
                    r['value_txt'].append(None); r['empty_reason'].append('' if ok else 'NOT_KNOWN'); r['stale'].append(0)
                codes['%s.%s' % (part, col)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rws}
            write(out_root, int(d), part, codes, coins, catalog=cat, sources=srcs, seal=seal); done[(part, d)] = 'WRITTEN'
        log('[alarm_design] %s rows %d' % (part, len(its)))
    return done


def read_back(dfn, out_root, code_dir=CODE_DIR, months=None):
    """-> (F, {base: records}, {base: sets}) from research_days through lab3.days (purpose research); months: only these YYYYMM are
    read at all (RUN_GATE G4: outcomes on BUILD months only; a CHECK day is never opened here)"""
    sys.path.insert(0, code_dir)
    from lab3 import days as LD
    R = LD.Days(out_root, 'research'); cols = columns(dfn); got = {}
    first, last = dfn['window']['first'], dfn['window']['last']
    for d in R.days():
        if not first <= str(d) <= last or (months is not None and str(d)[:6] not in months):
            continue
        for base in (None,) + BASES:
            p = part_name(dfn, base)
            if p not in R.parts(d):
                continue
            coins = R.index(d, p)['coins']; G = got.setdefault(base, {c: [] for c in ['coin', 't'] + cols})
            per = {col: R.rows('%s.%s' % (p, col), d, coins) for col in cols}
            for c in coins:
                n = len(per[cols[0]][c]['as_of_us'])
                G['coin'] += [c] * n; G['t'] += [a / 1e6 for a in per[cols[0]][c]['as_of_us']]
                for col in cols:
                    G[col] += [np.array([b], '<u8').view('<f8')[0] if b is not None else np.nan for b in per[col][c]['value_bits']]
    conv = {b: {k: np.array(v, object if k == 'coin' else float) for k, v in G.items()} for b, G in got.items()}
    F = conv.get(None)
    if F is None:
        raise ValueError('no fires of %s in %s' % (part_name(dfn), out_root))
    o = np.lexsort((F['coin'].astype(str), F['t'])); F = {k: v[o] for k, v in F.items()}
    F['side'] = F['side'].astype(int); key = {(c, round(t, 3)): i for i, (c, t) in enumerate(zip(F['coin'], F['t']))}
    Bs, Ss = {}, {}
    for b in BASES:
        if b not in conv:
            Ss[b] = [np.zeros(0, int) for _ in F['t']]; Bs[b] = None
            continue
        B = conv[b]; B['side'] = B['side'].astype(int); s = [[] for _ in F['t']]
        for j, (c, so) in enumerate(zip(B['coin'], B['set_of'])):
            i = key.get((c, round(so, 3)))
            if i is not None:
                s[i].append(j)
        Bs[b] = B; Ss[b] = [np.array(x, int) for x in s]
    return F, Bs, Ss


def write_events(recs, path, kind='FIRE'):
    """the hand-over EVENTS tsv (coin, t, side, S, mode, forced), written whole (tmp, fsync, replace) and never over an existing file"""
    if os.path.exists(path):
        raise FileExistsError(path)
    R = recs[kind]; tmp = path + '.tmp'
    with open(tmp, 'x') as f:
        f.write('coin\tt\tside\tS\tmode\tforced\n')
        for c, t, s in sorted(zip(R['coin'], R['t'], R['side']), key=lambda x: (x[1], x[0])):
            f.write('%s\t%.0f\t%d\t\t%s\t%s\n' % (c, t, s, kind, 'SHORTS' if s > 0 else 'LONGS'))
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


# ---------------------------------------------------------------- the try ledger (LEAD change 4; research-tool-design V3 section 10)
LEDGER_HEAD = 'utc\tseat\tsubject\tversion\tsha16\twhat is tried\tprimary horizon\tpass line\tresult'
PASS_LINE = 'TRUE = pooled wave 95 pct interval above 0 AND same sign in >= 7 of 9 months AND positive without the 5 best days (LAB1 MUST 4)'


def ledger_rows(ledger):
    if not os.path.exists(ledger):
        return []
    return [l.rstrip('\n').split('\t') for l in open(ledger) if l.strip() and not l.startswith('#') and not l.startswith('utc\t')]


def tries(dfn, ledger):
    """the subject family's scored tries: distinct sha16 rows of the family (a RESULT row does not count again)"""
    fam = dfn.get('family', dfn['id'])
    return len({r[4] for r in ledger_rows(ledger) if len(r) > 4 and r[2] == fam})


def has_try(dfn, ledger):
    return any(len(r) > 4 and r[4] == dfn['_sha16'] for r in ledger_rows(ledger))


def append_line(path, line):
    """append one line; the file is re-read to prove it landed (another seat may append too)"""
    with open(path, 'a') as f:
        f.write(line + '\n'); f.flush(); os.fsync(f.fileno())
    if line not in open(path).read():
        raise RuntimeError('the ledger line did not land in %s' % path)


def log_try(dfn, ledger, what, result=''):
    if not os.path.exists(ledger):
        append_line(ledger, '# TRY_LEDGER (research-tool-design V3 s10): one row per scored definition BEFORE its result is read; the result is a later row with the same sha16')
        append_line(ledger, LEDGER_HEAD)
    end = [t for t in dfn['truth'] if t['name'] == dfn['primary']][0]
    append_line(ledger, '\t'.join([datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'ALARM', dfn.get('family', dfn['id']),
                                    str(dfn['version']), dfn['_sha16'], what, '%s %s (%s..%s s)' % (dfn['primary'], end['kind'], end.get('start_s', 0), end['end_s']),
                                    PASS_LINE, result]))


def sources_of(dfn):
    ev_all = {}; shas = {}
    for nm, paths in dfn.get('events', {}).items():
        ev_all[nm], sh = load_events(paths); shas.update({'events:' + k: v for k, v in sh.items()})
    return ev_all, shas


def main(argv):
    """run: one window (a month job) -> research_days + EVENTS + RUN receipt (with the prefix and sign checks on its first fire day);
    card: every built month -> TRUTH_CARD receipt"""
    cmd = argv[0]
    if cmd == 'run':
        if len(argv) < 7 or not argv[6]:
            raise SystemExit('run <def.json> <first> <last> <out_root> <receipt dir> <lab_days>: the lab days (LAB_DAYS) are required')
        dfn = load_def(argv[1]); first, last, out_root, rec_dir, lab_root = argv[2], argv[3], argv[4], argv[5], argv[6]
        seal = seal_day(); refuse_sealed([first, last, dfn['window']['last']], seal)
        if not (dfn['window']['first'] <= first <= last <= dfn['window']['last']):
            raise SystemExit('%s..%s is outside the definition window' % (first, last))
        if quiet_now():
            raise SystemExit('23:30-00:15Z: no runs (LAB1 MUST 5)')
        catp = os.path.join(HERE, 'catalogs', 'ADES_%sV%s_CATALOG.tsv' % (dfn['id'], dfn['version']))
        if os.path.exists(catp) and open(catp).read() != catalog_text(dfn):   # refuse BEFORE computing, not after (23 Oct, 30 min lost)
            raise SystemExit('%s differs from the definition: a changed definition is a new version' % catp)
        ev_all, shas = sources_of(dfn); src = LabSource(lab_root=lab_root, events=ev_all)
        t0 = time.time(); recs, sets = run(dfn, first, last, src)
        os.makedirs(rec_dir, exist_ok=True); L = ['RUN %s %s..%s def %s code %s seal %s' % (part_name(dfn), first, last, dfn['_sha16'], sha16_file(os.path.realpath(__file__)), seal)]
        L += ['source %s %s' % kv for kv in sorted(shas.items())]
        F = recs.get('FIRE')
        if F is None or not len(F['t']):
            L.append('no fires in %s..%s' % (first, last))
        else:
            dd_, cnt_ = np.unique([utc_day(t) for t in F['t']], return_counts=True); fd = str(dd_[np.argmax(cnt_)])   # the busiest fire day
            n, bad = prefix_check(dfn, src, fd); sg = sign_check(dfn, src, fd)
            L.append('PREFIX (LAB1 MUST 6) day %s: %d fires re-found with every value after t cut: %d differ -> %s' % (
                fd, n, bad, 'NOT CHECKED (no fire)' if n == 0 else ('PASS' if bad == 0 else 'FAIL')))
            L.append('SIGN PLANT (LAB1 MUST 6) day %s: %s' % (fd, 'no mirror map in the definition' if sg is None else '%d fires, same times %s, sides flipped %s -> %s' % (
                sg[0], sg[1], sg[2], 'NOT CHECKED (no fire)' if sg[0] == 0 else ('PASS' if sg[1] and sg[2] else 'FAIL'))))
            L += recs.pop('_balance', [])
            write_out(dfn, recs, sets, out_root, sources=shas, log=lambda x: L.append(x))
            for kind, nm in (('FIRE', '%s_EVENTS_%s_%s.tsv'), ('FAIR', '%s_FAIR_EVENTS_%s_%s.tsv')):
                if kind == 'FIRE':
                    write_events(recs, os.path.join(rec_dir, nm % (part_name(dfn), first, last)), kind)
                else:
                    used = sorted({int(j) for s_ in sets['FAIR'] for j in s_})
                    sub = {k: v[used] for k, v in recs['FAIR'].items()}
                    write_events({'MATCH': sub}, os.path.join(rec_dir, nm % (part_name(dfn), first, last)), 'MATCH')
        L.append('seconds %.0f' % (time.time() - t0))
        open(os.path.join(rec_dir, 'RUN_%s_%s_%s.txt' % (part_name(dfn), first, last)), 'x').write('\n'.join(L) + '\n')
        print('\n'.join(L))
    elif cmd == 'card':
        dfn = load_def(argv[1]); out_root, rec_dir, ledger = argv[2], argv[3], argv[4]
        regimes = {}
        if len(argv) > 5 and os.path.exists(argv[5]):
            for l in open(argv[5]):
                if l.strip() and not l.startswith('#'):
                    m, tag = l.rstrip('\n').split('\t')[:2]; regimes[m] = tag
        if os.path.basename(ledger).startswith('TRIES_LEDGER'):
            # the ONE tries ledger (ledger_add_v5): a PREREG row whose setting file names this definition's sha16 (argv 7 = that file)
            if len(argv) < 8:
                raise SystemExit('card on TRIES_LEDGER needs the run settings file (argv 7) whose sha16 is in a PREREG row')
            st = json.load(open(argv[7])); ssha = sha16_file(argv[7])
            if st.get('definition_sha16') != dfn['_sha16']:
                raise SystemExit('the run settings name definition %s, not %s' % (st.get('definition_sha16'), dfn['_sha16']))
            pre = [l.split('\t') for l in open(ledger) if '\tPREREG\t' in l and ssha in l]
            if not pre:
                raise SystemExit('no PREREG row with setting sha16 %s in %s: ledger_add_v5 prereg first (frozen before read)' % (ssha, ledger))
        else:                                                            # OUTSIDE A35-AD-01: the legacy TRY_LEDGER is history only, it
            raise SystemExit('card needs the ONE tries ledger TRIES_LEDGER_V1 (ledger_add_v5); %s is history only and authorizes no read' % ledger)
        windows = None
        if len(argv) > 6:
            windows = json.load(open(argv[6])); windows['_sha16'] = sha16_file(argv[6])
        F, B, S = read_back(dfn, out_root, months=set(windows['build_months']) if windows else None)
        ntry = (sum(1 for l in open(ledger) if '\tPREREG\t' in l and ('\tALARM_%s\t' % dfn.get('family', dfn['id'])) in l)
                if os.path.basename(ledger).startswith('TRIES_LEDGER') else tries(dfn, ledger))
        L, summ = card(dfn, F, B, S, regimes=regimes, tries=ntry, windows=windows)
        ev_all, shas = sources_of(dfn)
        if dfn.get('lead_vs') in ev_all:
            L.append(lead_lines(F, ev_all[dfn['lead_vs']]))
        ov = {k: v for k, v in ev_all.items() if k in dfn.get('overlap_with', [])}
        if ov:
            L.append(overlap_lines(F, ov))
        os.makedirs(rec_dir, exist_ok=True)
        nm = 'TRUTH_CARD_%s' % part_name(dfn)
        open(os.path.join(rec_dir, nm + '.txt'), 'x').write('\n'.join(L) + '\n')
        open(os.path.join(rec_dir, nm + '.json'), 'x').write(json.dumps(summ, sort_keys=True, default=float, indent=1))
        print('\n'.join(L))
        if not os.path.basename(ledger).startswith('TRIES_LEDGER'):      # the ONE ledger takes its RESULT row via ledger_add_v5 result
            log_try(dfn, ledger, 'RESULT of the card above', result='; '.join('%s %s' % kv for kv in sorted(summ.get('verdict', {}).items())))
    elif cmd == 'try':
        dfn = load_def(argv[1]); ledger = argv[2]
        if has_try(dfn, ledger):
            raise SystemExit('%s already has a try row' % dfn['_sha16'])
        log_try(dfn, ledger, ' '.join(argv[3:]) or 'truth card %s..%s' % (dfn['window']['first'], dfn['window']['last']))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
