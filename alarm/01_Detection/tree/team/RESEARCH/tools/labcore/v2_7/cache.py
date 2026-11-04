"""labcore.v2_7.cache (labcore V2_7 CANDIDATE, sub-package labcore/v2_7; ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026; A46R REL-01 item F3). NOT RELEASED.
IN-MEMORY CACHES WITH AN EXPLICIT IDENTITY, for any tool that reads the same partition more than once in one process (Profile's per-code
day cache, Context's views and index hashes, Cause's coin-day reads). A library: no data writes.

Two different things, kept apart:
  DISK OUTPUT SEAL   what a tool WROTE: a part's index 'seal' (settings, declarations) and 'sources' (sha16 of every input it read).
                     It answers "is this stored output still the output of these inputs?" (UP TO DATE, resume, run check).
  IN-MEMORY IDENTITY what a process HOLDS: the key of one cached read. It answers "may this held value be served for this request?"
                     It never reads or trusts an output seal, and an output seal never names an in-memory key.
IDENTITY = every field below, all required (None only where it is the truth, e.g. no settings for a raw read):
  kind            what the cached thing is (e.g. 'clock_day', 'ctx_view', 'index_sha16')
  code            the registered metric code or part name read
  entity          the coins / rows the value holds, in order (a value read for [BTC, ETH] is not served for [ETH])
  dates           the days (or the first..last span) it covers
  clock_s         the clock it was read on (a 5 s day is never served as a 60 s day)
  settings_sha16  the settings (or None) that shaped the read
  source_vintage  the identity of the stored source at READ time: vintage(paths) = (path, size, mtime_ns, inode) of every file the read
                  depends on (e.g. the day's part indexes). A rewritten part changes it, so the old value is never served (a miss).
  IdentityCache(max_items=None)       .get(identity, load) -> value (load() on a miss); .stats() -> hits, misses, evictions, items
  vintage(paths) -> tuple             (cheap: os.stat, no hashing; a missing file is part of the identity as 'MISSING')
  key(identity) -> sha16              (canonical JSON of the complete identity; a missing or unknown field raises ValueError)"""
import collections, hashlib, json, os

FIELDS = ('kind', 'code', 'entity', 'dates', 'clock_s', 'settings_sha16', 'source_vintage')


def vintage(paths):
    out = []
    for p in sorted(paths):
        try:
            st = os.stat(p)
            out.append((p, st.st_size, st.st_mtime_ns, st.st_ino))
        except FileNotFoundError:
            out.append((p, 'MISSING'))
    return tuple(out)


def key(identity):
    miss = [f for f in FIELDS if f not in identity]; extra = sorted(set(identity) - set(FIELDS))
    if miss or extra:
        raise ValueError('cache identity: missing %s, unknown %s' % (miss, extra))
    text = json.dumps({f: identity[f] for f in FIELDS}, sort_keys=True, separators=(',', ':'), default=list)
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class IdentityCache:
    """a bounded mapping identity -> value; a request is served only for the exact same identity (source vintage included)"""
    def __init__(self, max_items=None):
        self.max_items = max_items; self._d = collections.OrderedDict(); self.hits = self.misses = self.evictions = 0

    def get(self, identity, load):
        k = key(identity)
        if k in self._d:
            self.hits += 1; self._d.move_to_end(k)
            return self._d[k][1]
        self.misses += 1; v = load(); self._d[k] = (dict(identity), v)
        while self.max_items is not None and len(self._d) > self.max_items:
            self._d.popitem(last=False); self.evictions += 1
        return v

    def drop(self, keep):
        """release held values whose identity the caller no longer needs (keep(identity) False): the memory bound of a rolling window"""
        for k in [k for k, (ident, _) in self._d.items() if not keep(ident)]:
            del self._d[k]

    def stats(self):
        return dict(hits=self.hits, misses=self.misses, evictions=self.evictions, items=len(self._d))
