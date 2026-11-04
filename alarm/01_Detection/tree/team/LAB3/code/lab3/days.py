"""lab3/days.py (LAB2, 20 Oct 2026; kanban 6.12, ARCH 14 rev 21 896165a7 sections 14.2 to 14.4): THE ONE READER of lab_days, the
one format (edition 3). Made from the door's GridSet (team/LAB3/code/gridbuild_v1.py: Grid, GridSet: sha16 check on read, one part a
code a day, reasons remapped by text, ABSENT for a coin the day does not list, NotBuilt never served as no value).
Tests first: LAB4's team/LAB3/LAB4/code/test_lab3_write_days_v1.py 0d6c7993 (16).

LAYOUT (written only by lab3.write; ARCH rev 21b 14.3): <root>/FORMAT.json; <root>/day=<D>/<PART>/: <code>.<field>.lz4, REASONS.txt and
WORDS/<code>.txt (the part's OWN id lists, one JSON text a line, reason id 0 = none: EDGE1 A1), index.json LAST. A part is a folder
holding index.json whose name has no '.tmp_' and no '.aside_'.

read(code, field, days, coins) -> numpy array (days, coins, steps) of the field's dtype; e and w are the ids of the part holding the code
that day: reasons(code, day) and words(code, day) decode them (LAB4 v2 03c28b78); a coin the day does not list reads ABSENT.
Fields: v, w, a, e, o (t_k - as_of us, an offset: 'has' = o == 0), k (known_at us, only for exact_k codes). has(code, days, coins).
Refused by name, never a value: NotBuilt (no part holds the code that day), Duplicate (two parts do), StaleInput (an input part of
the part changed or went), BlockChanged (a file's sha16 is not its index's).
D2 (BUILD5, 31 Oct 2026; CONDUCTOR RULING 13:08:49Z): a root whose FORMAT.json names layout 'evt1' (lab3/evt.py: one file per
field for every ROWS code of a part) is read by lab3.evt.EvtDays, which Days(root, purpose) returns; the same API and answers. One
layout a root: a part of another layout is refused MixedLayout."""
import json, os, time
import numpy as np
import pyarrow as pa

CODEC = pa.Codec('lz4')
DTYPE = {'v': '<f8', 'w': '<i2', 'a': '<i4', 'e': '|u1', 'o': '<i8', 'k': '<i8', 'off': '<i8', 'u': '<i8', 'x': '|u1'}
ABSENT = {'v': np.nan, 'w': -1, 'a': -2147483648, 'e': 255, 'o': -9223372036854775808, 'k': -9223372036854775808}
US = 1_000_000
EDITION = 3
NO_PREV = 'NO_PREV_DAY'      # the reason of 00:00 to 00:59 on a code-day whose D-1 the source does not hold (LAB1 09:34:26Z (b))


class NotBuilt(LookupError):
    pass


class Duplicate(ValueError):
    pass


class StaleInput(ValueError):
    pass


class BlockChanged(ValueError):
    pass


class WrongKind(ValueError):
    """a CLOCK read of a ROWS code, or a ROWS read of a CLOCK code, named"""


class Refused(PermissionError):
    """a day the caller's purpose may not read (the guard), named"""


class MixedLayout(ValueError):
    """D2: a part whose layout is not its root's (FORMAT.json layout), named: MIXED_LAYOUT"""


# The guard by purpose (ARCH rev 21b 14.4; EDGE2 N2, BED a): the purpose is FIXED BY THE CALLER IN CODE (Days(root, 'research') in the
# engine, the tabs, python3 -m lab3 and the studies; Days(root, 'build') in the makers, the checkers, the live history).
# Research keeps ALLOWED_PERIODS_V4 as lab3.reader holds it today (KEPT_ASIDE 6 Apr to 5 Jul 2026, refused from 6 Jul 2026) and names
# the team's JUL_UNSEEN (6 to 19 Jul) and FINAL_BLOCK (20 Sep to 7 Oct) inside it. OPINION, for the review: the same constants as
# lab3/reader.py (LAW_FIRST_REFUSED, KEPT_ASIDE); lab/guard.py takes over when its periods adapter (BED's periods.py v2) lands.
PURPOSES = ('research', 'build', 'check', 'live', 'proof')
# THE RESEARCH LAW is ONE table, lab3/law.py (LAB4 days_proof v3; LAB1 review 08:46:18Z), shared with lab3/reader.py; its names are kept here.
# PROOF_SEALED (LAB1 08:33:24Z (2); the owner 08:43 Berlin 22 Oct): research refuses 1 Jan to 9 Mar 2026 too. The 'proof' purpose reads
# PROOF_OPEN (1 Jan to 31 Mar 2026) and every day research reads, nothing else; it is for SCOUT's one look only: Days(root, 'proof',
# run=<name>) logs every read to <root>/PROOF_LOG.tsv (fixed here, never the caller's) BEFORE the read, and a second run name in that log
# is refused (the look is spent).
from .law import RESEARCH_REFUSED, PROOF_OPEN, research_refusal, proof_refusal, quarantine_refusal      # noqa: E402,F401 (days_prices.py: DY.research_refusal)
PROOF_LOG = 'PROOF_LOG.tsv'


def sha16_bytes(b):
    import hashlib
    return hashlib.sha256(b).hexdigest()[:16]


def sha16_file(p):
    with open(p, 'rb') as f:
        return sha16_bytes(f.read())


def load_list(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _day_start_us(day):
    import datetime
    return int(datetime.datetime.strptime(str(day), '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp()) * US


def _prev(day):
    import datetime
    return (datetime.datetime.strptime(str(day), '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d')


def is_part(day_dir, name):
    return '.tmp_' not in name and '.aside_' not in name and os.path.isfile(os.path.join(day_dir, name, 'index.json'))


class Days:
    """the one reader of a lab_days root"""
    LAYOUT = None                                                    # D2: the part layout read here (None: one file a code and field)

    def __new__(cls, root=None, purpose=None, run=None):
        """D2: a root whose FORMAT.json names layout evt1 is read by lab3.evt.EvtDays; a root without a layout by Days (no root:
        pickle's call, the class as asked)"""
        if cls is Days and root is not None:
            p = os.path.join(root, 'FORMAT.json')
            if os.path.exists(p):
                with open(p) as f:
                    lay = json.load(f).get('layout')
                if lay is not None:
                    from . import evt
                    if lay != evt.LAYOUT:
                        raise ValueError('%s: FORMAT layout %r, this reader reads %r or none' % (root, lay, evt.LAYOUT))
                    return object.__new__(evt.EvtDays)
        return object.__new__(cls)

    def __init__(self, root, purpose, run=None):                     # no default: a caller names its purpose (LAB4 6.12 item 1)
        if purpose not in PURPOSES:
            raise ValueError('purpose %r: one of %s, fixed by the caller in code' % (purpose, ', '.join(PURPOSES)))
        if purpose == 'proof' and not (run and isinstance(run, str) and '\t' not in run and '\n' not in run):
            raise ValueError("purpose 'proof' needs run=<name> (one line, no tab): every proof read is logged to <root>/%s" % PROOF_LOG)
        if purpose != 'proof' and run is not None:
            raise ValueError('run is for the proof purpose only')
        self.root = root; self.purpose = purpose; self.run = run
        p = os.path.join(root, 'FORMAT.json')
        if os.path.exists(p):
            with open(p) as f:
                fm = json.load(f)
            if fm.get('edition') != EDITION:
                raise ValueError('%s: FORMAT edition %r, this reader reads %d' % (root, fm.get('edition'), EDITION))
        self._ix = {}; self._cp = {}; self._pc = {}                     # D2.1: _pc day -> (day folder mtime_ns, parts)

    def days(self):
        return sorted(d[4:] for d in os.listdir(self.root) if d.startswith('day='))

    _PC = 'D2.1'                                                         # the parts() cache is in this edition
    SETTLE_NS = 2 * 10**9                                                # D2.1: a day folder mtime younger than this is never trusted

    def parts(self, day):
        """D2.1 (BUILD5): the day's parts, kept while the day folder's mtime_ns is unchanged and settled (SETTLE_NS old). RELIES ON
        the commit renaming <PART>.tmp_ into the day folder (write.py and evt.py both do), which moves the folder's mtime: a part
        whose index.json were written in place would be missed (test_parts_cache_v1 pins both writers' rename; CONDUCTOR 14:31:14Z)"""
        dd = os.path.join(self.root, 'day=%s' % day)
        try:
            mt = os.stat(dd).st_mtime_ns
        except FileNotFoundError:
            return []
        pc = self.__dict__.setdefault('_pc', {}); hit = pc.get(day)
        if hit is not None and hit[0] == mt:
            return list(hit[1])
        out = sorted(n for n in os.listdir(dd) if is_part(dd, n))
        if time.time_ns() - mt >= self.SETTLE_NS:
            pc[day] = (mt, tuple(out))
        else:
            pc.pop(day, None)
        return out

    def _seal(self, part, day):
        """the seal before any index IO, every purpose (OUTSIDE D04-01, LAB1 23 Oct): refuse only, never logs (reads log in _guard)"""
        why = proof_refusal(day) if self.purpose == 'proof' else research_refusal(day) if self.purpose == 'research' else None
        if why is None and self.purpose != 'proof':
            why = quarantine_refusal(part, day)                             # STRATEGY-134049: CHECK-month outcome parts
        if why:
            raise Refused('%s %s: refused for %s: %s (the seal at the index)' % (part, day, self.purpose, why))

    def index(self, day, part):
        self._seal(part, str(day))
        key = (str(day), part)
        p = os.path.join(self.root, 'day=%s' % day, part, 'index.json')
        try:                                                                 # LAB1 V2_7: the cache is keyed by the index FILE too (a rebuilt
            st = os.stat(p); sig = (st.st_ino, st.st_size, st.st_mtime_ns)   # or newly built part is read again, never served stale)
        except FileNotFoundError as exc:                                     # OUTSIDE D04-02: a missing index is NotBuilt, by name
            self._ix.pop(key, None)
            raise NotBuilt('%s %s: no part index in %s: refused, never served as no value' % (part, day, self.root)) from exc
        got = self._ix.get(key)
        if got is None or got[0] != sig:
            with open(p, 'rb') as f:
                raw = f.read()
            ix = json.loads(raw)
            ix['_sha16'] = sha16_bytes(raw)
            if ix.get('layout') != self.LAYOUT:                              # D2: one layout a root
                raise MixedLayout('%s %s: part layout %r in a reader of layout %r (%s): MIXED_LAYOUT, refused'
                                  % (part, day, ix.get('layout'), self.LAYOUT, self.root))
            self._ix[key] = got = (sig, ix)
        return got[1]

    def code_parts(self, day):
        """{code: [parts holding it]} of a day, built once from the part indexes and rebuilt when any index changes (LAB1 V2_7: part_of no
        longer parses every part index of the day for every code)"""
        day = str(day); pts = self.parts(day)
        sig = tuple((pt, self.index(day, pt)['_sha16']) for pt in pts)
        got = self._cp.get(day)
        if got is None or got[0] != sig:
            m = {}
            for pt in pts:
                for code in self.index(day, pt)['readings']:
                    m.setdefault(code, []).append(pt)
            self._cp[day] = got = (sig, m)
        return got[1]

    def part_of(self, code, day):
        """the ONE part of day holding code: NotBuilt (none), Duplicate (two), StaleInput (an input part changed)"""
        hold = list(self.code_parts(day).get(code, ()))
        if not hold:
            raise NotBuilt('%s %s: no part of %s holds this code that day: refused, never served as no value' % (code, day, self.root))
        if len(hold) > 1:
            raise Duplicate('%s %s: held by parts %s: refused' % (code, day, ', '.join(hold)))
        pt = hold[0]
        for src, sha in sorted(self.index(day, pt).get('inputs', {}).items()):
            now = None
            if src in self.parts(day):
                p = os.path.join(self.root, 'day=%s' % day, src, 'index.json')
                now = sha16_file(p)
            if now != sha:
                raise StaleInput('%s %s: part %s was made from %s %s, now %s: STALE_INPUT, refused' % (code, day, pt, src, sha, now))
        return pt

    def reasons(self, code, day):
        """the reason texts of the part holding code that day (id = index, 0 = none)"""
        pt = self.part_of(code, str(day))
        return load_list(os.path.join(self.root, 'day=%s' % day, pt, 'REASONS.txt'))

    def _word_list(self, day, pt, code):
        """D2: the word texts of code in part pt of day, read in this one place (lab3.evt.EvtDays reads its WORDS.json)"""
        return load_list(os.path.join(self.root, 'day=%s' % day, pt, 'WORDS', '%s.txt' % code))

    def words(self, code, day):
        """the word texts of code in the part holding it that day (id = index)"""
        pt = self.part_of(code, str(day))
        return self._word_list(day, pt, code)

    def block(self, day, part, code, field):
        r = self.index(day, part)['readings'][code]
        if field not in r['files']:
            raise NotBuilt('%s %s: part %s has no field %s' % (code, day, part, field))
        p = os.path.join(self.root, 'day=%s' % day, part, '%s.%s.lz4' % (code, field))
        with open(p, 'rb') as f:
            data = f.read()
        if sha16_bytes(data) != r['files'][field]:
            raise BlockChanged('%s is %s, its index names %s: refused' % (p, sha16_bytes(data), r['files'][field]))
        shape = tuple(r.get('shapes', {}).get(field) or r['shape']); dt = np.dtype(DTYPE[field])
        raw = CODEC.decompress(data, decompressed_size=int(np.prod(shape)) * dt.itemsize, asbytes=True)
        return np.frombuffer(raw, dtype=dt).reshape(shape)

    def _proof_guard(self, code, days):
        import datetime
        for D in days:
            why = proof_refusal(D)
            if why:
                raise Refused('%s %s: refused for proof: %s (the guard)' % (code, D, why))
        log = os.path.join(self.root, PROOF_LOG); runs = set()
        if os.path.exists(log):
            with open(log) as f:
                runs = {ln.split('\t')[1] for ln in f if ln.count('\t') >= 3}
        if runs - {self.run}:
            raise Refused('%s: the one look is spent: %s holds run %s, this is run %s'
                          % (code, log, ', '.join(sorted(runs - {self.run})), self.run))
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(log, 'a') as f:
            f.write('%s\t%s\t%s\t%s\n' % (stamp, self.run, code, ','.join(days)))

    def _guard(self, code, days):
        if self.purpose == 'proof':
            return self._proof_guard(code, days)
        if self.purpose == 'research':
            for D in days:
                why = research_refusal(D)
                if why:
                    raise Refused('%s %s: refused for research: %s (the guard; build, check and live read it)' % (code, D, why))

    def _kind(self, code, day, want):
        pt = self.part_of(code, str(day)); r = self.index(str(day), pt)['readings'][code]
        if r.get('kind', 'CLOCK') != want:
            raise WrongKind('%s %s: a %s code; %s' % (code, day, r.get('kind', 'CLOCK'),
                            'read() reads CLOCK codes' if want == 'CLOCK' else 'rows() and at() read ROWS codes'))
        return pt, r

    def read(self, code, field, days, coins):
        days = [str(d) for d in days]; coins = list(coins)
        out = None
        self._guard(code, days)
        for di, D in enumerate(days):
            pt, r = self._kind(code, D, 'CLOCK')
            ix = self.index(D, pt)
            b = self.block(D, pt, code, field)
            if out is None:
                out = np.full((len(days), len(coins), b.shape[1]), ABSENT[field], DTYPE[field])
            elif b.shape[1] != out.shape[2]:
                raise ValueError('%s: %d steps on %s, %d before: one call reads one clock' % (code, b.shape[1], D, out.shape[2]))
            pos = {c: i for i, c in enumerate(ix['coins'])}
            ci = [i for i, c in enumerate(coins) if c in pos]
            if ci:
                out[di, ci] = b[[pos[coins[i]] for i in ci]]
        return out

    def _rows(self, code, day, coins):
        """no guard: rows() and at() guard first"""
        D = str(day); pt, r = self._kind(code, D, 'ROWS')
        b = {f: self.block(D, pt, code, f) for f in r['fields']}
        rs = load_list(os.path.join(self.root, 'day=%s' % D, pt, 'REASONS.txt'))
        ws = self._word_list(D, pt, code)
        d0 = _day_start_us(D); listed = {c: i for i, c in enumerate(self.index(D, pt)['coins'])}
        out = {}
        for coin in coins:
            if coin not in listed:
                out[coin] = None; continue
            i = listed[coin]; lo, hi = int(b['off'][i]), int(b['off'][i + 1])
            col = {f: [] for f in ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')}
            for j in range(lo, hi):
                x = int(b['x'][j]); kind = x & 7; w = int(b['w'][j])
                col['day'].append(int(D)); col['as_of_us'].append(d0 + int(b['u'][j])); col['known_at_us'].append(int(b['k'][j]))
                col['value_kind'].append(kind)
                col['value_bits'].append(None if x & 16 else int(np.asarray(b['v'][j], '<f8').view('<u8')))
                col['value_txt'].append(ws[w] if w >= 0 else None)
                col['empty_reason'].append(rs[int(b['e'][j])]); col['stale'].append(1 if x & 8 else 0)
            out[coin] = col
        return out

    def rows(self, code, day, coins):
        """ROWS kind: {coin: day's rows in lab3.rows' columns, in the rule's key order}; None for a coin the day does not list"""
        self._guard(code, [str(day)])
        return self._rows(code, day, list(coins))

    def at(self, code, days, coins, step):
        """ROWS kind: the value as known at t_k = D 00:00 + step x k by C1's rule through lab3/asof.py (rows of day(t - 1 h) and
        day(t): D-1's part is read for 00:00 to 00:59, NotBuilt when it is not built). -> {'v' f8, 'text' obj, 'a' i4, 'reason' obj,
        'o' i8 (t_k - as_of), 'k' i8 (known_at)}, each (days, coins, steps); none: text '', reason NO_ROW_KNOWN; an unlisted coin: ABSENT,
        text and reason None. The texts are decoded, so a D-1 row keeps D-1's reason text."""
        from . import asof as AS
        days = [str(d) for d in days]; coins = list(coins)
        self._guard(code, days)
        n = 86400 // int(step)
        out = {'v': np.full((len(days), len(coins), n), np.nan, '<f8'), 'text': np.full((len(days), len(coins), n), None, object),
               'a': np.full((len(days), len(coins), n), ABSENT['a'], '<i4'), 'reason': np.full((len(days), len(coins), n), None, object),
               'o': np.full((len(days), len(coins), n), ABSENT['o'], '<i8'), 'k': np.full((len(days), len(coins), n), ABSENT['k'], '<i8')}
        for di, D in enumerate(days):
            P = _prev(D)
            now = self._rows(code, D, coins)
            no_prev = bool(self.index(D, self.part_of(code, D))['readings'][code].get('no_prev'))
            if no_prev:                                             # FIRST_DAYS: D-1 does not exist: the first hour is NO_PREV_DAY, never read
                before = {c: None for c in coins}
            elif not self.parts(P):
                raise NotBuilt('%s %s: 00:00 to 00:59 read day %s, not built: refused' % (code, D, P))
            else:
                try:
                    before = self._rows(code, P, coins)
                except NotBuilt:                                    # D-1 built without this code: no rows of it (LAB4 6.12b item 1)
                    before = {c: None for c in coins}
            number = self.index(D, self.part_of(code, D))['readings'][code].get('value_kind') != 'WORD'
            d0 = _day_start_us(D); ts = [d0 + kk * int(step) * US for kk in range(n)]
            early = [t for t in ts if t - AS.HOUR_US < d0]; late = ts[len(early):]
            for ci, coin in enumerate(coins):
                if now[coin] is None:
                    continue
                r = {f: (before[coin][f] if before[coin] is not None else []) + now[coin][f] for f in now[coin]}
                res = []
                for tt, dset in ((early, {int(P), int(D)}), (late, {int(D)})):
                    if not tt:
                        continue
                    kept = AS._series(r, dset)
                    res += [(t, None if j is None else kept[j]) for t, j in zip(tt, AS.answer_grid(kept, tt))]
                for kk, (t, hit) in enumerate(res):
                    if no_prev and kk < len(early):
                        out['text'][di, ci, kk] = ''; out['reason'][di, ci, kk] = NO_PREV; continue
                    if hit is None:
                        out['text'][di, ci, kk] = ''; out['reason'][di, ci, kk] = AS.NO_ROW; continue
                    key, i, v, why = hit
                    out['text'][di, ci, kk] = v; out['reason'][di, ci, kk] = why
                    if number:                                           # a word is not a number (LAB4 6.12b item 2)
                        try:
                            out['v'][di, ci, kk] = float(v) if v != '' else np.nan
                        except ValueError:
                            pass
                    out['a'][di, ci, kk] = AS.rint_age(t - key[1]); out['o'][di, ci, kk] = t - key[0]; out['k'][di, ci, kk] = key[1]
        return out

    def step(self, code, day):
        """the code's clock that day from its part's index: 5, 30, 60 (CLOCK) or 'event' (ROWS); NotBuilt when no part holds it"""
        pt = self.part_of(code, str(day))
        return self.index(str(day), pt)['readings'][code]['step']

    def coins_with_rows(self, code, day):
        """the coins with at least one kept row of the day itself (not D-1) for code: the old 'the group file holds a row of the
        coin' (meaning_core b_coin_days; LAB4 6.21 item 2), where the part's coins list is the whole roster"""
        pt = self.part_of(code, str(day))
        return list(self.index(day, pt)['readings'][code]['coins_with_rows'])

    def has(self, code, days, coins):
        """True where a point sits exactly at the step end (o == 0): 'has a new point at t_k' at any clock (rev 21b, EDGE1 S2)"""
        return self.read(code, 'o', days, coins) == 0
