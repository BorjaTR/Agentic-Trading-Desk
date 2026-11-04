"""clock_series.py: CANDIDATE for the shared library labcore (STRATEGY/LEAD, 25 Oct 2026; owner the owner 09:23:38Z: "those improvements if they
can be made generic should be included into the libraries so every other tool reuses them"). Owner of labcore: LAB1; enters labcore by
review (old owner + LAB1) with its tests, in a release cycle. Until then tools import it from here.
What it gives any tool that reads a year-table CLOCK metric (any clock: 3 s, 5 s, 60 s ...) around events:
- parts_holding(R, code, day): lab3 METADATA only (no value read): the parts of the day whose index names the code.
- read_day_typed(R, code, day, coins, step=None): one code-day through the ONE lab3 reader -> {v, k or None, sources, pos, listed, built,
  part, flag}; flag: the points whose FINITE value the one quality rule (labcore.v2_7.quality.known) does not call known, typed STALE,
  NOT_KNOWN or HOLE, their value removed.
- read_day(R, code, day, coins): the same as the older 4-tuple (v, k or None, {source: sha16}, {coin: row}).
- ClockSeries(R, code, days, coins, cache=None, all_coins=None, step=None, sealed=None): consecutive days of one code for some coins; with a
  shared cache each day is read once for all the run's coins (a rolling window: the caller deletes days it no longer needs); days named in
  sealed are never read (state SEALED, or OUTSIDE_WINDOW for a day the caller's window excludes).
- ClockSeries.window(coin, lo, hi, cut): the values with lo < t <= hi and known_at <= cut, found by bisection (t sorted). Known values only.
- ClockSeries.event_window(coin, lo, hi, cut, with_k=False): EVERY native grid point lo < t <= hi with its value and its state (OK, HOLE,
  NOT_IN_SOURCE, NOT_BUILT, NOT_KNOWN, SEALED); a missing point is kept and typed, never dropped (A46 PR-03); with_k adds known_at.
- ClockSeries.normal(coin, lo, hi, cut): the finite values of a normal window and their stats (n, p90, mean, mean |step|,
  mean |log step|, sealed: the word of a never-read day in the window or ''), computed once per coin and window and reused while nothing
  in it is known late. unavailable_between(lo, hi): that word for any window.
Times are microseconds; column j of a day is the value as known at D0 + j x step (lab3/asof.py; checked 25 Oct on E2.S02 and D3.S01: every
stored known_at <= D0 + j x step; the first version put it one step later, D0 + (j+1) x step, so values were read one step stale);
known_at = the stored k when the part's index lists a k field, else the grid time.
ABSENCE AND ERRORS (A46R-P P-R1, profile_fix2 25 Oct 2026). Edition 2 read a day as absent whenever the reader raised an exception whose
class was NAMED NotBuilt; lab3 raises that same class when an EXISTING part lacks a required field (block(): 'part P has no field v'), so a
malformed part read as an absent day. Now absence is decided from lab3's own metadata BEFORE any value is read and no exception is caught
in this module: parts_holding lists the day's parts (R.parts: none when the day folder does not exist) and keeps those whose index names the
code (R.index(day, part)['readings']). No part names it: the day is NOT_BUILT, typed, nothing read. A part names it: the values are read and
EVERY reader error propagates unchanged: lab3's NotBuilt for a missing required field (the part exists: an integrity failure, never an
absence), Refused (the law, the seal, a quarantine), StaleInput, BlockChanged, Duplicate, WrongKind, a clock that is not the registered
one, OSError. A reader that cannot list a day's parts cannot prove an absence: its read decides and every error raises.
STATES (the LEAD source-state vocabulary of the ctxprof_fix2 task): OK; HOLE (the coin is in the part, its value at that time is empty);
NOT_IN_SOURCE (the part exists that day but the coin is not in its index; edition 2 wrote NOT_LISTED, which never proved the coin was
unlisted on the venue: the constant NOT_LISTED stays as an alias of the same state 2, its word is now NOT_IN_SOURCE); NOT_BUILT (no part
names the code that day, from metadata); NOT_KNOWN (a value known only after the cut); SEALED (a day the caller names as sealed: law.py
refuses it for the caller's purpose and the caller did not request it; it is never read); OUTSIDE_WINDOW (a support day outside the
caller's permitted window: never read, checklist N4); STALE (the lab stored a finite value WITH the reason STALE: the value is carried, not
new, and is never used as a value; G7); a finite value the quality rule rejects for another cause is HOLE (or NOT_KNOWN: known_at later than
its column). PRELISTING is not a state here: no canonical listing source is registered, so a coin missing from a
part's index is NOT_IN_SOURCE, never PRELISTING.
QUALITY (G7 = OX-CODE1 A46R2 P-R2-01, ctxprof_check VERDICT_V1; FIX_ROUND3 S2; profile_fix2 25 Oct 2026): lab3 stores beside each value its
reason id (field e; 0 = none, 255 = absent), its age (a), its offset (o) and, for exact_k codes, its known_at (k). Edition 3 (5b5a331c) read
v and k only, so a FINITE value the lab marks bad was used as a value (real case: 0.0 with STALE for 52 coins on A1.S01/A1.S02 at 26 Dec
11:13-11:17Z and 8 Jan 23:23-23:26Z, inside the 7-day normal of 585 A02P events). Now every field among e, a, o, k that the part's index
lists is read through the one reader and THE one quality rule decides, labcore.v2_7.quality.known(v, e, a, o, k, col_us) (LAB1; never a
private copy): a cell is a value only when it is known. A finite value that is not known is removed (NaN) and typed: STALE when its stored
reason text names STALE (alone or in a compound such as TRADES_HOLE;STALE), NOT_KNOWN when its known_at is later than its own column time,
else HOLE (another stored reason, the absent reason byte, a negative age or offset). It is never an OK point of an event window and never a
normal value (normal_steps_observed does not count it). The reason texts are read only when such a point exists (Days.reasons)."""
import datetime as dt, os, sys
import numpy as np

US = 1_000_000
OK, HOLE, NOT_IN_SOURCE, NOT_BUILT, NOT_KNOWN, SEALED, OUTSIDE_WINDOW, STALE = 0, 1, 2, 3, 4, 5, 6, 7
NOT_LISTED = NOT_IN_SOURCE                    # edition 2 name of state 2 (kept for callers); its word is NOT_IN_SOURCE
STATE_WORD = {OK: 'OK', HOLE: 'HOLE', NOT_IN_SOURCE: 'NOT_IN_SOURCE', NOT_BUILT: 'NOT_BUILT', NOT_KNOWN: 'NOT_KNOWN', SEALED: 'SEALED',
              OUTSIDE_WINDOW: 'OUTSIDE_WINDOW', STALE: 'STALE'}
UNREAD = {'SEALED': SEALED, 'OUTSIDE_WINDOW': OUTSIDE_WINDOW}   # the two never-read day words a caller may name


def is_absence(exc):
    """kept name (edition 2 API). True only for an instance of lab3's canonical NotBuilt class (lab3.days.NotBuilt, by class, never by
    name). It is NOT how this module decides an absence: read_day_typed decides it from lab3 metadata (parts_holding) before any read."""
    from lab3 import days as LD                                       # the caller's lab3 (the one reader's own exception classes)
    return isinstance(exc, LD.NotBuilt)


def parts_holding(R, code, d):
    """lab3 METADATA ONLY, no value read: the parts of day d whose index names code (R.parts(d): the day's parts, none when the day folder
    does not exist; R.index(d, part)['readings']: the codes a part holds). The index's own seal (Refused) and its errors propagate.
    None when the reader cannot list a day's parts: then an absence cannot be proven and the read decides (every error raises)."""
    lister = getattr(R, 'parts', None)
    if lister is None:
        return None
    return [pt for pt in lister(d) if code in ((R.index(d, pt) or {}).get('readings') or {})]


def _absent(coins, sealed=0):
    """a day with no value: NOT_BUILT (sealed 0) or never read (sealed = the state SEALED or OUTSIDE_WINDOW)"""
    pos = {c: i for i, c in enumerate(coins)}
    return dict(v=None, k=None, sources=None, pos=pos, listed=None, built=False, part=None, sealed=sealed, flag=None)


_Q = []


def quality():
    """labcore.v2_7.quality (LAB1): THE one rule of a known lab3 cell, imported on first use (team/RESEARCH/tools on the path if needed)"""
    if not _Q:
        tools = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
        if tools not in sys.path:
            sys.path.append(tools)
        from labcore.v2_7 import quality as Q
        _Q.append(Q)
    return _Q[0]


def day_start_us(d):
    return int(dt.datetime.strptime(str(d), '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp()) * US


def quality_flags(R, code, d, coins, v, k, rd):
    """S2/G7: the points whose value is FINITE but not known by the one quality rule -> (coins, n) uint8 states (STALE, NOT_KNOWN or HOLE;
    0 where the value stands), or None when every finite value is known. The fields among e, a, o that the part's index lists are read
    through the one reader (its guard and block checks apply; k is read by the caller); labcore.v2_7.quality.known(v, e, a, o, k, col_us)
    decides, col_us = D0 + j x step (the column's own time). The word only names why: STALE (stored reason text names STALE), NOT_KNOWN
    (the known_at rule alone), else HOLE."""
    files = (rd or {}).get('files') or {}
    Q = quality()
    got = {f: np.asarray(R.read(code, f, [d], coins)[0]) for f in ('e', 'a', 'o') if f in files}
    col = None
    if k is not None:
        col = (day_start_us(d) + np.arange(v.shape[1], dtype=np.int64) * (86400 // v.shape[1]) * US)[None, :]
    bad = np.isfinite(v) & ~Q.known(v, e=got.get('e'), a=got.get('a'), o=got.get('o'), k=k, col_us=col)
    if not bad.any():
        return None
    out = np.zeros(v.shape, np.uint8); out[bad] = HOLE
    if k is not None:                                                  # the known_at rule alone (the same function, one field)
        out[bad & ~Q.known(np.zeros(v.shape), k=k, col_us=col)] = NOT_KNOWN
    if 'e' in got:
        why = bad & ~Q.known(np.zeros(v.shape), e=got['e'])            # the reason rule (the same function, one field)
        if why.any():
            words = R.reasons(code, d) if hasattr(R, 'reasons') else []   # a reader without reason texts: no word, HOLE
            stale_ids = [i for i, w in enumerate(words) if 'STALE' in str(w).split(';')]
            out[why & np.isin(got['e'], stale_ids)] = STALE
    return out


def read_day_typed(R, code, d, coins, step=None):
    """one code-day through the one lab3 reader -> dict(v (coins, n) float or None, k (coins, n) int64 or None, sources {name: sha16} or
    None, pos {coin: row}, listed bool array over coins or None (index names no coins), built bool, part, flag (quality_flags: the finite
    points the one quality rule does not call known, removed from v, or None)). built False ONLY when lab3's metadata shows no part of the
    day names the code (parts_holding); once a part names it every reader error propagates."""
    hold = parts_holding(R, code, d)
    if hold is not None and not hold:                                 # the true absence, from metadata: nothing is read
        return _absent(coins)
    pos = {c: i for i, c in enumerate(coins)}
    v = np.asarray(R.read(code, 'v', [d], coins)[0], float)          # a part names the code: NotBuilt (no field v), Refused ... raise
    if v.ndim != 2 or v.shape[0] != len(coins) or v.shape[1] < 1 or 86400 % v.shape[1]:
        raise ValueError('%s %s: v block of shape %s for %d coins is not a CLOCK day: refused' % (code, d, v.shape, len(coins)))
    n = v.shape[1]
    if step is not None and 86400 // n != int(step):
        raise ValueError('%s %s: %d steps a day = a %d s clock, the registered clock is %s s: refused, never re-gridded'
                         % (code, d, n, 86400 // n, step))
    pt = R.part_of(code, d)
    ix = R.index(d, pt)
    rd = (ix.get('readings') or {}).get(code)
    k = None
    if rd is not None:
        if 'step' in rd and str(rd['step']) != str(86400 // n):
            raise ValueError('%s %s: the part index names step %r, the block holds %d steps: refused' % (code, d, rd['step'], n))
        if 'k' in (rd.get('files') or {}):                          # the index names the field: read it, any error propagates
            k = np.asarray(R.read(code, 'k', [d], coins)[0], np.int64)
    flag = quality_flags(R, code, d, coins, v, k, rd)                  # S2/G7: a value the one quality rule does not know is never used
    if flag is not None:
        v = np.where(flag != 0, np.nan, v)
    listed = None
    if 'coins' in ix:
        have = set(ix['coins'])
        listed = np.array([c in have for c in coins], bool)
    return dict(v=v, k=k, sources={'lab:day=%s/%s' % (d, pt): ix.get('_sha16', '')}, pos=pos, listed=listed, built=True, part=pt,
                sealed=0, flag=flag)


def read_day(R, code, d, coins):
    """(v, k or None, {source: sha16} or None, {coin: row}) of one code-day; (None, None, None, pos) only when lab3's metadata shows no
    part of the day names the code"""
    x = read_day_typed(R, code, d, coins)
    return x['v'], x['k'], x['sources'], x['pos']


class ClockSeries:
    """one CLOCK code for some coins over consecutive days, read once through lab3 (any clock): t (the column's as-of time, us), v, k
    (known_at, us), state_day (coins, days): OK, NOT_IN_SOURCE, NOT_BUILT or SEALED. step: the registered clock in seconds (every built
    day must hold it); without it the clock is inferred from the first built day and must not change. sealed: days never read, a set of
    YYYYMMDD (state SEALED) or a mapping {day: 'SEALED' | 'OUTSIDE_WINDOW'}; the caller decides them (law.py, its own window).
    not_built_days, sealed_days (every never-read day), unread {day: state}: the days of each kind."""
    def __init__(self, R, code, days, coins, cache=None, all_coins=None, step=None, sealed=None):
        self.ok = False; self.code = code; self.days = list(days); vs, ks, built, listed, seal, fls = [], [], [], [], [], []
        self.sources = {}
        sealed = sealed or ()
        unread = {d: UNREAD[sealed[d]] for d in sealed} if isinstance(sealed, dict) else {d: SEALED for d in sealed}
        want = int(step) if step is not None else None
        for d in self.days:
            if cache is not None:                                  # speed (25 Oct): each day read once for all the run's coins
                if d not in cache:
                    cache[d] = _absent(all_coins, unread[d]) if d in unread else read_day_typed(R, code, d, all_coins, want)
                x = cache[d]
                ix = [x['pos'][c] for c in coins]
                v = x['v'][ix] if x['v'] is not None else None
                k = x['k'][ix] if x['k'] is not None else None
                lst = x['listed'][ix] if x['listed'] is not None else None
                fl = x['flag'][ix] if x.get('flag') is not None else None
            else:
                x = _absent(coins, unread[d]) if d in unread else read_day_typed(R, code, d, coins, want)
                v, k, lst, fl = x['v'], x['k'], x['listed'], x.get('flag')
            if x['sources'] is not None:
                self.sources.update(x['sources'])
            if v is not None:
                n = v.shape[1]
                if want is None:
                    want = 86400 // n
                if 86400 // n != want:
                    raise ValueError('%s: clock changed between days' % code)
            vs.append(v); ks.append(k); built.append(v is not None); listed.append(lst); seal.append(int(x.get('sealed') or 0)); fls.append(fl)
        self.sealed_days = [d for d, s in zip(self.days, seal) if s]
        self.unread = {d: s for d, s in zip(self.days, seal) if s}
        self.not_built_days = [d for d, b, s in zip(self.days, built, seal) if not b and not s]
        if want is None:                                           # nothing built and no registered clock: nothing to grid
            return
        step = want; n = 86400 // step; self._n = n
        z0 = int(dt.datetime.strptime(self.days[0], '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())
        self.step = step
        self.t = (z0 + step * np.arange(0, n * len(self.days), dtype=np.int64)) * US          # column j = the value as known at D0 + j x step (lab3 asof rule)
        self.v = np.concatenate([x if x is not None else np.full((len(coins), n), np.nan) for x in vs], axis=1)
        kk = []
        for x, d in zip(ks, range(len(self.days))):
            kk.append(x if x is not None else np.broadcast_to(self.t[d * n:(d + 1) * n], (len(coins), n)))
        self.k = np.concatenate(kk, axis=1)
        self.k = np.where(self.k == np.iinfo(np.int64).min, np.iinfo(np.int64).max, self.k)    # no known_at = never known
        self.flag = None                                                   # S2/G7: STALE, NOT_KNOWN or HOLE of the finite points not known
        if any(f is not None for f in fls):
            self.flag = np.concatenate([f if f is not None else np.zeros((len(coins), n), np.uint8) for f in fls], axis=1)
        self.state_day = np.zeros((len(coins), len(self.days)), np.uint8)
        for di, (b, lst, s) in enumerate(zip(built, listed, seal)):
            if s:
                self.state_day[:, di] = s
            elif not b:
                self.state_day[:, di] = NOT_BUILT
            elif lst is not None:
                self.state_day[~lst, di] = NOT_IN_SOURCE
        self.coin = {c: i for i, c in enumerate(coins)}; self.ok = True

    def unavailable_between(self, lo_us, hi_us):
        """the word of a never-read day (SEALED before OUTSIDE_WINDOW) holding a grid point lo < t <= hi, else ''"""
        un = getattr(self, 'unread', None)
        if not un or not getattr(self, 'ok', False):
            return ''
        a = int(np.searchsorted(self.t, lo_us, 'right')); b = int(np.searchsorted(self.t, hi_us, 'right'))
        hit = {un[self.days[j]] for j in range(a // self._n, (b - 1) // self._n + 1) if self.days[j] in un} if b > a else set()
        return STATE_WORD[SEALED] if SEALED in hit else (STATE_WORD[OUTSIDE_WINDOW] if hit else '')

    def sealed_between(self, lo_us, hi_us):
        """True when a never-read day (SEALED or OUTSIDE_WINDOW) holds a grid point lo < t <= hi"""
        return bool(self.unavailable_between(lo_us, hi_us))

    def window(self, coin, lo_us, hi_us, cut_us):
        """(t, v) with lo < t <= hi and known_at <= cut; t is sorted, so the window is found by bisection (speed, 25 Oct). Known points
        only (a hole stays a NaN value, a point known after cut is left out): for normals and onset rules, never for event summaries."""
        i = self.coin[coin]; a = int(np.searchsorted(self.t, lo_us, 'right')); b = int(np.searchsorted(self.t, hi_us, 'right'))
        t, v, k = self.t[a:b], self.v[i][a:b], self.k[i][a:b]
        if not len(k) or k.max() <= cut_us:
            return t, v
        m = k <= cut_us
        return t[m], v[m]

    def event_window(self, coin, lo_us, hi_us, cut_us, with_k=False):
        """(t, v, state) of EVERY native grid point lo < t <= hi: state OK (finite, known_at <= cut), HOLE (the store holds an empty
        value), NOT_IN_SOURCE (the day's part does not list the entity), NOT_BUILT (no part holds the code that day), NOT_KNOWN (known only
        after cut), SEALED or OUTSIDE_WINDOW (a day never read), STALE (a finite value the lab stored with the reason STALE: never used;
        any other finite value the quality rule rejects is HOLE or NOT_KNOWN); v is NaN wherever state is not OK. with_k: (t, v, state,
        known_at)"""
        i = self.coin[coin]; a = int(np.searchsorted(self.t, lo_us, 'right')); b = int(np.searchsorted(self.t, hi_us, 'right'))
        t, v, k = self.t[a:b], self.v[i][a:b], self.k[i][a:b]
        fin = np.isfinite(v)
        st = np.where(fin, np.where(k <= cut_us, OK, NOT_KNOWN), HOLE).astype(np.uint8)
        fl = getattr(self, 'flag', None)
        if fl is not None and len(t):
            fs = fl[i][a:b]
            st = np.where(fs != 0, fs, st).astype(np.uint8)
        sd = getattr(self, 'state_day', None)
        if sd is not None and len(t):
            ds = sd[i][np.arange(a, b) // self._n]
            st = np.where(ds != OK, ds, st).astype(np.uint8)
        if (st != OK).any():
            v = np.where(st == OK, v, np.nan)
        return (t, v, st, k) if with_k else (t, v, st)

    def normal(self, coin, lo_us, hi_us, cut_us):
        """the coin's normal window values (finite) and their stats, computed once per coin and window when nothing in it is known late;
        sealed: the word (SEALED, OUTSIDE_WINDOW) of a never-read day holding part of the window, else ''"""
        key = (coin, lo_us, hi_us); c = getattr(self, '_norm', None)
        if c is None:
            c = self._norm = {}
        if key in c and c[key]['kmax'] <= cut_us:
            return c[key]
        i = self.coin[coin]; a = int(np.searchsorted(self.t, lo_us, 'right')); b = int(np.searchsorted(self.t, hi_us, 'right'))
        k = self.k[i][a:b]; kmax = int(k.max()) if len(k) else -1
        nv = self.v[i][a:b]                                        # = window(): the values known at cut (one max of k, not two)
        if kmax > cut_us:
            nv = nv[k <= cut_us]
        nv = nv[np.isfinite(nv)]
        ub = getattr(self, 'unavailable_between', None)            # a test double without it has no never-read day
        st = {'nv': nv, 'kmax': kmax, 'n': len(nv), 'sealed': ub(lo_us, hi_us) if ub is not None else ''}
        if len(nv) >= 100:
            st['p90'] = float(np.percentile(nv, 90)); st['mean'] = float(np.mean(nv)); st['absdiff'] = float(np.mean(np.abs(np.diff(nv))))
            pos = nv[nv > 0]
            st['logabsdiff'] = float(np.mean(np.abs(np.diff(np.log(pos))))) if len(pos) >= 2 else 0.0
        if kmax <= cut_us:
            c[key] = st
        return st
