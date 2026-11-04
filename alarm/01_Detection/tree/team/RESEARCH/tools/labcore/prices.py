"""labcore.prices (BUILD2, 23 Oct 2026): the coin-day price cache (spec LEAD/LABCORE_STEP2_SPEC_V1.md b75998c5 sec 1). Wraps
lab3.bins.read_bins (the ONE reader of lab_days PRICE 3 s bins); nothing written, nothing re-coded.
  PriceCache(root, purpose='research', code=None)  one run's cache; reads a (coin, day) from disk ONCE (.reads counts disk reads)
  .day(coin, day) -> {te_us, px, hi, lo, reason}   te sorted (stable); a coin absent that day: empty arrays, reason 'NO_COIN'; a day lab3
                                                   refuses for the purpose: lab3's refusal is raised, never hidden
  v2 (SKEPTIC 02-11, 02-12): cached arrays are read-only; close_at(..., with_time=True) gives the matched bar time; close_at_many
  refuses unequal lengths and non-integer times.
  .close_at(coin, t_us) -> float                   the last close with te <= t on t's UTC day (money_v1.lab_close_at's rule); NaN if none
  .close_at_many(coins, t_us) -> float64[]         the same for many asks, each coin-day touched once (np.searchsorted)
  .path(coin, t0_us, t1_us) -> {te_us, px, hi, lo} the bars with te in (t0, t1], across midnight (each day read once)
  .drop(day)                                       frees a day (a run walking days in order keeps memory bounded)"""
import datetime, os, sys
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
LAB3_CODE = os.path.realpath(os.path.join(HERE, '..', '..', '..', 'LAB3', 'code'))
US = 1_000_000
DAY_US = 86_400 * US
UTC = datetime.timezone.utc
EMPTY = {'te_us': np.zeros(0, np.int64), 'px': np.zeros(0), 'hi': np.zeros(0), 'lo': np.zeros(0)}


def day_of(t_us):
    return datetime.datetime.fromtimestamp(int(t_us) // US, UTC).strftime('%Y%m%d')


class PriceCache:
    def __init__(self, root, purpose='research', code=None):
        code = code or LAB3_CODE
        if code not in sys.path:
            sys.path.insert(0, code)
        from lab3 import days as LD, bins as LB
        self.LB = LB; self.R = LD.Days(root, purpose); self.mem = {}; self.reads = 0; self.coins_of = {}

    def _coins(self, day):
        if day not in self.coins_of:
            self.coins_of[day] = set(self.R.index(day, 'PRICE')['coins'])
        return self.coins_of[day]

    def day(self, coin, day):
        """a SNAPSHOT of the cached coin-day (OUTSIDE C2-05): fresh read-only copies; replacing or rewriting it never reaches the cache"""
        d = self._day(coin, day); out = {k: np.array(d[k], copy=True) for k in ('te_us', 'px', 'hi', 'lo')}
        for k in out:
            out[k].setflags(write=False)
        out['reason'] = d['reason']
        return out

    def _src(self, coin, day):
        """the lookups' reader: .day is the documented reader boundary (a subclass that overrides it is used); the base class reads its
        own cache directly (no snapshot copy per lookup)"""
        return self.day(coin, day) if type(self).day is not PriceCache.day else self._day(coin, day)

    def _day(self, coin, day):
        day = str(day); key = (coin, day)
        if key not in self.mem:
            if coin not in self._coins(day):
                self.mem[key] = dict(EMPTY, reason='NO_COIN')
            else:
                off, b = self.LB.read_bins(self.R, day, [coin]); self.reads += 1
                te = np.asarray(b['te'][off[0]:off[1]], np.int64); o = np.argsort(te, kind='mergesort')
                self.mem[key] = {'te_us': te[o], 'px': np.asarray(b['px'][off[0]:off[1]], float)[o],
                                 'hi': np.asarray(b['hi'][off[0]:off[1]], float)[o], 'lo': np.asarray(b['lo'][off[0]:off[1]], float)[o],
                                 'reason': ''}
            for k in ('te_us', 'px', 'hi', 'lo'):
                self.mem[key][k].setflags(write=False)                 # SKEPTIC 02-11: the cache cannot be changed by a caller
        return self.mem[key]

    def close_at(self, coin, t_us, with_time=False):
        """the last close with te <= t that day; with_time=True -> (px, te_us of that bar or -1): the caller measures its age (a hole)"""
        d = self._src(coin, day_of(t_us)); q = np.searchsorted(d['te_us'], int(t_us), side='right') - 1
        px = float(d['px'][q]) if q >= 0 else float('nan')
        return (px, int(d['te_us'][q]) if q >= 0 else -1) if with_time else px

    def close_at_many(self, coins, t_us):
        coins = list(coins); t_raw = np.asarray(t_us)
        if len(coins) != len(t_raw):
            raise ValueError('close_at_many: %d coins and %d times: refused (SKEPTIC 02-12)' % (len(coins), len(t_raw)))
        if t_raw.dtype.kind not in 'iu':
            raise ValueError('close_at_many: times must be integer microseconds, got %s' % t_raw.dtype)
        t_us = t_raw.astype(np.int64); out = np.full(len(t_us), np.nan); groups = {}
        for i, (c, t) in enumerate(zip(coins, t_us)):
            groups.setdefault((c, day_of(t)), []).append(i)
        for (c, day), idx in sorted(groups.items()):
            d = self._src(c, day); idx = np.asarray(idx)
            q = np.searchsorted(d['te_us'], t_us[idx], side='right') - 1; ok = q >= 0
            out[idx[ok]] = d['px'][q[ok]]
        return out

    def path(self, coin, t0_us, t1_us):
        parts = []; t = int(t0_us) - int(t0_us) % DAY_US
        while t <= int(t1_us):
            d = self._src(coin, day_of(t)); m = (d['te_us'] > t0_us) & (d['te_us'] <= t1_us)
            parts.append({k: d[k][m] for k in ('te_us', 'px', 'hi', 'lo')}); t += DAY_US
        return {k: np.concatenate([p[k] for p in parts]) if parts else EMPTY[k] for k in ('te_us', 'px', 'hi', 'lo')}

    def drop(self, day):
        day = str(day)
        for k in [k for k in self.mem if k[1] == day]:
            del self.mem[k]
