"""i2g_engine_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: i2g_engine.py 22a029e9b74311a0, never edited. Changed: F (the tree root) is found from this file, no longer one machine's
path; the kernels are the clean editions: alarm_stamp_projection_v2 on alarm_stamp_ed1_1 and alarm_context_ed1_1, draw_prepared_v2 on
prepared_activity_v2 (no machine path); PINS name them.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is i2g_engine.py's.
i2g_engine.py (i2g_grader for STRATEGY/LEAD, 25 Oct 2026): the per-coin work of idea_to_grade after detection, in ONE process per coin:
each needed PRICE coin-day is read ONCE (lab3.bins frames, five fields, through lab3.days: law.py inside it is the only seal) and serves both
  1. MATCHED CONTROLS: the matcher of record alarm_match/draw_v3.py, imported unchanged (draw_coin, days_for, part_of, split_from, own_flag,
     exclusion_times), driven exactly as the outside chain drove it (OUTSIDE DEV1/b2_performance_v1/match_prepared_activity_v1._run_coin):
     one random stream per parent (seed + crc32(fid)), one split part at a time, whole-parent abstention (COMPARISON_UNAVAILABLE) when any
     candidate day (+-7 d in the part, and each one's previous day) is not FULLY known to the detector or has no PRICE part;
  2. OPPORTUNITY MEASUREMENTS: alarm_stamp's 55 STAMP fields per (alarm or control) x direction, through the outside chain's STAMP projection
     (alarm_stamp_projection_v1.one_entry, imported unchanged: alarm_stamp + heat_offer_v2.entry_row without the unused trail columns),
     BED fill_v2 taker fill after the 6 s execution delay and ladder_v6 first touches over the 4 h hold, on the PriceView of the
     observation's day D-1, D, D+1 (days inside the run's research window only), exactly as prepare_measurements_parallel_v3.load_prices.
No date is held here: the research window and the split come from the caller (the split from labcore.gates.WINDOWS through draw_v3)."""
import datetime as dt, hashlib, importlib.util, os, sys, time, zlib
sys.dont_write_bytecode = True
import numpy as np

F = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', '..'))   # the tree root (<F>/team/RESEARCH/tools/idea_to_grade holds this file)
TOOLS = F + '/team/RESEARCH/tools'
LAB3 = F + '/team/LAB3/code'
B2 = F + '/team/OUTSIDE/COORD/development/DEV1/b2_performance_v1'
US = 1_000_000
# every imported kernel, pinned (sha256 prefix 16); a change refuses the run (KERNEL_DRIFT)
PINS = {
    TOOLS + '/alarm_match/draw_v3.py': '91279359fb4a0815',
    TOOLS + '/alarm_stamp/alarm_stamp_ed1_1.py': '486e6fbf6880b892',
    TOOLS + '/entry_card/heat_offer_v2.py': 'c14e05a3975186be',
    TOOLS + '/alarm_context/alarm_context_ed1_1.py': 'ab5d915138cb1f01',
    F + '/team/BED/scripts/e_fill/fill_v2.py': '8d166ddc23fee167',
    F + '/team/BED/scripts/e_ladder/ladder_v6.py': 'ab45f22b9b9af87c',
    B2 + '/alarm_stamp_projection_v2.py': '914ec6f23260940e',
    B2 + '/heat_offer_projection_v1.py': '6bef437137369208',
    B2 + '/draw_prepared_v2.py': 'ef46ca7be926f96a',
    B2 + '/prepared_activity_v2.py': '2878fb0d5ae9d4f5',
    TOOLS + '/labcore/waves.py': None,
    TOOLS + '/labcore/gates.py': None,
    LAB3 + '/lab3/bins.py': None,
    LAB3 + '/lab3/days.py': None,
    LAB3 + '/lab3/law.py': None,
}


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


_MODS = None


def process_modules(refresh=False):
    """-> {path: sha16} of every Python file of the forensics tree this process has executed: imported modules (sys.modules) and files
    loaded by path (LOADED_BY_PATH); hashed once per process (the run re-hashes every pinned file again before publication)"""
    global _MODS
    if _MODS is None or refresh:
        paths = set(LOADED_BY_PATH)
        for m in list(sys.modules.values()):
            f = getattr(m, '__file__', None)
            if f and f.endswith('.py'):
                q = os.path.realpath(f)
                if q.startswith(F + '/'):
                    paths.add(q)
        _MODS = {q: sha16(q) for q in sorted(paths)}
    return dict(_MODS)


def code_pins():
    """-> {path: sha16} of every kernel this engine imports; refuses a pinned kernel that changed"""
    out = {}
    for p, want in PINS.items():
        got = sha16(p)
        if want is not None and got != want:
            raise ValueError('KERNEL_DRIFT %s is %s, pinned %s' % (p, got, want))
        out[p] = got
    out[os.path.realpath(__file__)] = sha16(os.path.realpath(__file__))
    return out


LOADED_BY_PATH = []                                                     # files this process executed through importlib (not in sys.modules)


def load_path(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    LOADED_BY_PATH.append(os.path.realpath(path))
    return m


class K:
    """the imported kernels (one import per process)"""
    loaded = False

    @classmethod
    def load(cls):
        if cls.loaded:
            return cls
        for p in (LAB3, TOOLS, TOOLS + '/alarm_match', TOOLS + '/alarm_stamp', TOOLS + '/entry_card', F + '/team/BED/scripts/e_fill',
                  F + '/team/BED/scripts/e_ladder'):
            if p not in sys.path:
                sys.path.insert(0, p)
        if B2 not in sys.path:
            sys.path.append(B2)                                   # appended: only the two projection modules are taken from it
        import draw_v3 as D
        import fill_v2 as FV
        import ladder_v6 as LD
        from lab3.days import Days, NotBuilt
        from lab3 import bins as LB
        from labcore import gates
        from labcore.waves import waves
        S = load_path(B2 + '/alarm_stamp_projection_v2.py', 'alarm_stamp_projection_v2')
        # the outside chain's draw: draw_v3's functions with the bit-audited prepared pre-activity (prepared_activity_v2 refuses to load
        # unless alarm_match/draw_v3.py is the reference it was audited against)
        DP = load_path(B2 + '/draw_prepared_v2.py', 'draw_prepared_v2')
        cls.DP = DP
        for m, p in ((D, TOOLS + '/alarm_match/draw_v3.py'), (FV, F + '/team/BED/scripts/e_fill/fill_v2.py'),
                     (LD, F + '/team/BED/scripts/e_ladder/ladder_v6.py')):
            if os.path.realpath(m.__file__) != os.path.realpath(p):
                raise ValueError('KERNEL_PATH %s loaded from %s' % (p, m.__file__))
        cls.D, cls.FV, cls.LD, cls.Days, cls.NotBuilt, cls.LB, cls.gates, cls.waves, cls.S = D, FV, LD, Days, NotBuilt, LB, gates, waves, S
        cls.loaded = True
        return cls


def ms_us(cand_t):
    """the control clock: the draw time rounded to the millisecond, as integer microseconds (outside: C.us(format(float(cand_t), '.3f')))"""
    s = format(float(cand_t), '.3f'); a, b = s.split('.')
    if a.startswith('-'):
        raise ValueError('NEGATIVE_CLOCK')
    return int(a) * US + int(b) * 1000


def day_of(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def calendar(first, last):
    out, d = [], first
    while d <= last:
        out.append(d); d = shift(d, 1)
    return out


FIELDS5 = ('te', 'tl', 'px', 'hi', 'lo')
_INDEX = {}                                                             # per process: (root, day) -> the PRICE index as of its sha16


class SourceChanged(RuntimeError):
    """a PRICE part changed while this process was using it (A54-F2): never served stale, never mixed into one run"""
    code = 'SOURCE_CHANGED'


def index_sha16(root, day):
    return sha16(os.path.join(root, 'day=%s' % day, 'PRICE', 'index.json'))


ABSENT = 'ABSENT'


def price_state(root, day):
    """the source state of one PRICE day (A54-F2 residual): ABSENT when lab3 would say NotBuilt (no part), else the sha16 of its index;
    every state a task consults (present AND absent) is part of the run's frozen source identity"""
    DY = sys.modules[K.LB.__name__.rsplit('.', 1)[0] + '.days']
    dd = os.path.join(root, 'day=%s' % day)
    if not os.path.isdir(dd) or not DY.is_part(dd, K.LB.PART):
        return ABSENT
    return index_sha16(root, day)


def price_index(root, day):
    """the day's PRICE index, offsets and coin positions, REVALIDATED on every call by the sha16 of index.json (A54-F2): a cached entry
    whose file changed is re-read (the old one is never served); NotBuilt when lab3 says the day has no PRICE part -> (entry, sha16)"""
    LB = K.LB; DY = sys.modules[LB.__name__.rsplit('.', 1)[0] + '.days']
    dd = os.path.join(root, 'day=%s' % day)
    if not os.path.isdir(dd) or not DY.is_part(dd, LB.PART):
        _INDEX.pop((root, day), None)
        raise K.NotBuilt('%s %s: no %s part in %s' % (LB.PART, day, LB.PART, root))
    h = index_sha16(root, day); ent = _INDEX.get((root, day))
    if ent is None or ent[4] != h:
        ix = LB._index(dd, LB.PART); off = LB._off(dd, LB.PART, ix)
        if index_sha16(root, day) != h:                                  # the bytes read must be the bytes hashed
            raise SourceChanged('%s %s: PRICE index changed while it was read' % (root, day))
        ent = _INDEX[(root, day)] = (dd, ix, off, {c: i for i, c in enumerate(ix['coins'])}, h)
    return ent, h


def read_coin_day(R, root, day, coin):
    """lab3.bins.read_bins for ONE coin and the five fields the kernels use (te, tl, px, hi, lo): the same guard first (lab3/law.py through
    Days._guard, before any IO), the same index and frame readers (sha16 checked per frame against an index revalidated by its own sha16),
    the same row check against BIN.off; the unused n, buy and sell frames are not read.
    -> ({field: array} (0 rows when the coin is not in the day's PRICE part), index sha16)"""
    LB = K.LB; DY = sys.modules[LB.__name__.rsplit('.', 1)[0] + '.days']
    R._guard(LB.PART, [str(day)])
    (dd, ix, off, pos, h), _ = price_index(root, day)
    if coin not in pos:
        return {f: np.zeros(0, LB.DTYPE[f]) for f in FIELDS5}, h
    i = pos[coin]; a = LB.coin_arrays(dd, LB.PART, ix, i, fields=FIELDS5)
    if len(a['te']) != int(off[i + 1]) - int(off[i]):
        raise DY.BlockChanged('%s %s %s: frame rows %d, off says %d: refused' % (LB.PART, day, coin, len(a['te']), int(off[i + 1]) - int(off[i])))
    return {f: np.asarray(a[f]).astype(LB.DTYPE[f]) for f in FIELDS5}, h


class CoinPrices:
    """one coin's PRICE days, each read once (the lab3.bins frames through lab3.days.Days purpose 'research': law.py is the seal)"""
    def __init__(self, lab_root, coin, window):
        k = K.load(); self.R = k.Days(lab_root, 'research'); self.root = lab_root; self.coin = coin; self.window = window; self.mem = {}
        self.reads = 0; self.read_s = 0.0; self.vintage = {}

    def _record(self, day, state):
        if self.vintage.setdefault(day, state) != state:
            raise SourceChanged('%s %s: PRICE %s was %s, now %s within one task' % (self.root, self.coin, day, self.vintage[day], state))

    def present(self, day):
        """the coverage shortcut: does the day have a PRICE part? The answer (present with its index sha16, or ABSENT) is recorded in the
        task's source identity like a read, so a part that appears or changes later refuses the task"""
        if day not in self.vintage:
            self._record(day, price_state(self.root, day))
        return self.vintage[day] != ABSENT

    def recheck(self):
        """every PRICE day this object consulted (read OR found absent), its state taken again now: a part that changed, appeared or
        disappeared during the task refuses it (SOURCE_CHANGED)"""
        bad = [(d, h) for d, h in sorted(self.vintage.items()) if price_state(self.root, d) != h]
        if bad:
            raise SourceChanged('%s %s: PRICE changed during the task on %s' % (self.root, self.coin, ['%s was %s' % x for x in bad[:5]]))
        return dict(self.vintage)

    def raw(self, day):
        """-> {te, tl, px, hi, lo} or None (no PRICE part that day: lab3 NotBuilt); outside the research window: None, never read"""
        if not self.window[0] <= day <= self.window[1]:
            return None
        if day not in self.mem:
            t0 = time.perf_counter()
            try:
                self.mem[day], h = read_coin_day(self.R, self.root, day, self.coin); self.reads += 1
                self._record(day, h)
            except K.NotBuilt:                                      # no PRICE part that day (lab3: no index.json); a missing or changed
                self.mem[day] = None                                # frame INSIDE an existing part raises (integrity error, never 'no prices')
                self._record(day, ABSENT)                           # the absence is part of the task's source identity
            self.read_s += time.perf_counter() - t0
        return self.mem[day]

    def match_arrays(self, days):
        """draw_v3.coin_arrays over labcore.prices.PriceCache.day: per day te sorted (stable) with its px; a NaN or non-positive close
        dropped; seconds and prices"""
        te, px = [], []
        for d in days:
            x = self.raw(d)
            if x is None:
                raise ValueError('MATCH_DAY_WITHOUT_PRICE %s %s' % (self.coin, d))
            t = np.asarray(x['te'], np.int64); o = np.argsort(t, kind='mergesort')
            te.append(t[o]); px.append(np.asarray(x['px'], float)[o])
        te = np.concatenate(te) if te else np.zeros(0, np.int64); px = np.concatenate(px) if px else np.zeros(0)
        ok = np.isfinite(px) & (px > 0)
        return te[ok] / 1e6, px[ok]

    def view(self, day):
        """prepare_measurements_parallel_v3.load_prices: the PriceView of D-1, D, D+1 (inside the window, PRICE present) and the loaded days"""
        parts = {k: [] for k in ('te', 'tl', 'px', 'hi', 'lo')}; loaded = set()
        for k in (-1, 0, 1):
            d = shift(day, k); x = self.raw(d)
            if x is None:
                continue
            loaded.add(d)
            for f in parts:
                parts[f].append(x[f])
        if not parts['tl']:
            return K.FV.PriceView.empty(self.coin), loaded
        return K.FV.PriceView(self.coin, *[np.concatenate(parts[f]) for f in ('te', 'tl', 'px', 'hi', 'lo')]), loaded


def coin_job(task):
    """task: coin, parents [(t s int, side)], alarms [t s] (the coin's whole event list: exclusions), known_days [YYYYMMDD fully known to
    the detector], lab_root, window (first, last of the research window), split [(name, a, b)], settings (draw_v3.S0 + split), seed,
    measure (bool) -> dict(census, edges, balance, unavailable, obs (t_us, side, direction, kind) rows with values, reasons, timings)"""
    t_start = time.perf_counter()
    k = K.load(); D = k.D; S = k.S
    coin = task['coin']; seed = int(task['seed']); s = dict(task['settings']); split = tuple(tuple(x) for x in task['split'])
    s['split'] = split
    prices = CoinPrices(task['lab_root'], coin, tuple(task['window']))
    known_days = set(task['known_days'])
    have = calendar(*task['window'])                                       # every calendar day of the research window
    tuples = sorted((float(t), int(sd), '%s_%d' % (coin, int(t))) for t, sd in task['parents'])
    exclusions = D.exclusion_times(task['alarms'], [p[0] for p in tuples])
    edges, census, balance, unavailable = [], [], [], []
    missing_price = {}
    def no_price(d):                                                # bound to the task's source identity (prices.present records it)
        if d not in missing_price:
            missing_price[d] = not prices.present(d)
        return missing_price[d]
    t_match = time.perf_counter()
    for part in sorted({D.part_of(t, split) for t, _, _ in tuples}, key=lambda x: (x is None, x)):
        if part is None:
            raise ValueError('PARENT_OUTSIDE_SPLIT %s' % coin)
        pts = [p for p in tuples if D.part_of(p[0], split) == part]
        days = D.days_for(have, [p[0] for p in pts], part, split, s)
        ts, px = prices.match_arrays([d for d in days if not no_price(d)])
        ts.setflags(write=False); px.setflags(write=False)
        act = k.DP.PreparedPreActivity(ts, px)
        starts = [D._day_start(d) for d in days]
        lo, hi = {n: (x, y) for n, x, y in split}[part]
        for parent in pts:
            t, side, fid = parent
            if D.part_of(t + s['horizon_s'], split) != part:
                e, c, b = k.DP.draw_coin(coin, [parent], exclusions, ts, px, starts, seed, s, activity=act)
            else:
                domain = [d for d in days if lo <= d <= hi and abs(D._day_start(d) - (t - t % 86400)) <= s['days'] * 86400]
                needed = set(domain) | {shift(d, -1) for d in domain}
                missing = ['PRICE:' + d for d in D.days_for(have, [t], part, split, s) if no_price(d)]
                missing += [d for d in sorted(needed) if d not in known_days]
                if missing:
                    e, c, b = [], [(fid, coin, t, side, 0, 'COMPARISON_UNAVAILABLE', float('nan'))], []
                    # known_at: the abstention reads the coverage of every candidate day, so it is known at 00:00 after the latest one
                    last_day = max(list(needed) + [d for d in D.days_for(have, [t], part, split, s)] + [day_of(t)])
                    unavailable.append({'fid': fid, 'reason': 'CONSERVATIVE_FULL_DAY_SUPPORT_OR_PRICE_COVERAGE_UNAVAILABLE', 'days': missing,
                                        'known_at_us': int(D._day_start(shift(last_day, 1))) * US})
                else:
                    e, c, b = k.DP.draw_coin(coin, [parent], exclusions, ts, px, starts, seed, s, activity=act)
            edges += [x + (D.own_flag(x[2], x[3], s['horizon_s']),) for x in e]; census += c; balance += b
        del act
    t_measure = time.perf_counter()
    obs = []; values = None; reasons = {}
    if task.get('measure', True):
        # observations: every parent and every ELIGIBLE control (own flag empty) x FOLLOW, FADE; the control clock is its draw time
        # rounded to the millisecond (prepare_measurements_parallel_v3: C.us(format(float(cand_t), '.3f')))
        seen = {}
        for fid, c_, t, side, n, status, cov0 in census:
            for d in ('FOLLOW', 'FADE'):
                key = ('parent', int(round(t)) * US, int(side), d)
                if key not in seen:
                    seen[key] = len(obs); obs.append(key)
        for e in edges:
            if e[7] != '':
                continue
            ct = ms_us(e[3])
            for d in ('FOLLOW', 'FADE'):
                key = ('control', ct, int(e[4]), d)
                if key not in seen:
                    seen[key] = len(obs); obs.append(key)
        names = S.NAMES; values = np.full((len(obs), len(names)), np.nan)
        by_day = {}
        for i, (kind, t_us, side, d) in enumerate(obs):
            by_day.setdefault(day_of(t_us // US), []).append(i)
        memo = {}                                                       # the same clock and traded side -> the same measurement
        for day in sorted(by_day):
            pv, loaded = prices.view(day)
            for i in by_day[day]:
                kind, t_us, side, d = obs[i]
                eff = (t_us, -side if d == 'FADE' else side)
                if eff not in memo:
                    r = S.one_entry(pv, k.FV, k.LD, loaded, t_us / US, side, d, 0, S.DELAY_S, S.HOLD_S, entry_projection='stamp')
                    row = np.array([np.nan if r[nm][0] is None else r[nm][0] for nm in names], float)
                    why = {nm: r[nm][1] for nm in names if r[nm][1]}
                    memo[eff] = (row, why)
                row, why = memo[eff]; values[i] = row
                if why:
                    reasons[i] = dict(why)
            del pv
    vintages = prices.recheck()
    t_end = time.perf_counter()
    return {'coin': coin, 'price_vintages': vintages, 'census': census, 'edges': edges, 'balance': balance, 'unavailable': unavailable, 'obs': obs, 'values': values,
            'reasons': reasons, 'price_reads': prices.reads, 'price_read_s': prices.read_s,
            'missing_price_days': sorted(d for d, v in missing_price.items() if v),
            'seconds': {'match': t_measure - t_match, 'measure': t_end - t_measure, 'total': t_end - t_start}, 'pid': os.getpid(),
            'ru_maxrss': __import__('resource').getrusage(__import__('resource').RUSAGE_SELF).ru_maxrss, 'modules': process_modules()}
