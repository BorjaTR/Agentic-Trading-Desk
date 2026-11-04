"""lab3/bins.py v5 (BED, 20 Oct 09:1xZ: = v4 9b7e982e + LAB4 09:04:54Z narrowed item: coins_missing is DISJOINT from coins (prices_rec's rule,
B10) + LAB4 09:06:46Z item: the reader refuses an index whose recorded dtype of a field is not DTYPE (BlockChanged, named; B11)). v4 text:
lab3/bins.py v4 (BED, 20 Oct 08:5xZ: = v3 53ff25aa + write_bins refuses a coins_missing coin that has bins, or one named
twice (a missing coin outside coins is the prices_rec rule: kept): LAB4 6.12d item 1, TREE note; test B9). v3 text: lab3/bins.py (BED, 20 Oct 2026; kanban 6.12d with 6.17; ARCH 14 rev 21c 14.3 'BIN: prices. Present 3 s bins only, by coin (off),
te, tl, px, hi, lo, n, buy, sell: the arrays prices_rec holds today, so P3 is array for array'). THE BIN KIND of the one format: the
writer's and the reader's PRICE half, on LAB2's layout and helpers (lab3.write: FORMAT.json, the (day, part) flock, <PART>.tmp_<UTC>
read back whole, the old part moved to <PART>.aside_<UTC> and named in the new index; lab3.days: the lz4 codec, sha16 on read,
NotBuilt, BlockChanged, Refused by purpose). Tests first: team/BED/proposals/prices_6_17/tests/test_prices_bin_v2.py 295ecacb.

write_bins(root, day, coins, bins, sources=None, part='PRICE', missing=None) -> the part's index (missing: coins with no source, named)
  coins = the day's coin list (the part's row order); bins = {coin: {te, tl, px, hi, lo, n, buy, sell: 1-d, one length}}; a listed coin
  without bins has 0 rows; bins of a coin not listed: refused. sources = {coin: sha16 of the raw it came from}, kept in the index.
  Refused BEFORE anything is written (BadBins, the rule named): every rule today's reader lab/prices.read_px3s2 refuses.
read_bins(days, day, coins) -> (off int64 (len(coins) + 1), {field: array}): coins in the order ASKED, a coin the part lacks 0 rows.
  The guard first (a research read of a refused day: Refused, nothing opened). Wired as Days.bins (one line in lab3/days.py, LAB2's).
LAYOUT (v3): <root>/day=<D>/<PART>/BIN.<field>.lz4 = one lz4 frame A COIN back to back (index: [pos, bytes, sha16, rows] a coin), so a
  coin-day is read alone (pread, sha16 checked; prices_ed9's coin-day load, E5 memory), BIN.off.lz4, index.json
LAST with 'kind': 'BIN', 'bins' (dtype, rows, sha16 per file), 'readings': {} (so lab3.days' CLOCK reads never see a BIN part)."""
import datetime, fcntl, json, os
import numpy as np
from . import days as DY, write as W

US = 1_000_000
BIN_US = 3 * US
DAY_US = 86_400 * US
FIELDS = ('te', 'tl', 'px', 'hi', 'lo', 'n', 'buy', 'sell')
DTYPE = {'te': '<i8', 'tl': '<i8', 'px': '<f8', 'hi': '<f8', 'lo': '<f8', 'n': '<i4', 'buy': '<f8', 'sell': '<f8', 'off': '<i8'}
PART = 'PRICE'


class BadBins(ValueError):
    """bins today's reader (lab/prices.read_px3s2) would refuse, the rule named; nothing written"""


def day_start_us(day):
    return int(datetime.datetime.strptime(str(day), '%Y%m%d').replace(tzinfo=datetime.timezone.utc).timestamp()) * US


def _whole(x, what, coin):
    a = np.asarray(x)
    if a.dtype.kind in 'iu':
        return a.astype(np.int64)
    if a.dtype.kind != 'f' or not np.isfinite(a).all() or np.any(a != np.round(a)):
        raise BadBins('%s: %s not whole numbers' % (coin, what))
    return a.astype(np.int64)


def check_bins(coin, b, day):
    """one coin-day's bins -> the 8 arrays in their dtypes, or BadBins naming read_px3s2's rule (its order kept)"""
    miss = [f for f in FIELDS if f not in b]
    if miss:
        raise BadBins('%s: fields %s missing' % (coin, miss))
    L = {f: len(b[f]) for f in FIELDS}
    if len(set(L.values())) != 1:
        raise BadBins('%s: the fields are not of one length %s' % (coin, L))
    n = np.asarray(b['n'])
    if n.dtype.kind not in 'iuf' or (n.dtype.kind == 'f' and not np.isfinite(n).all()) or np.any(n != np.round(n)) or np.any(n < 1):
        raise BadBins('%s: refused, a trade count that is not a whole number >= 1' % coin)
    te = _whole(b['te'], 'bin ends (us)', coin); tl = _whole(b['tl'], 'last trades (us)', coin)
    if np.any(te % US != 0) or np.any(tl % 1000 != 0):
        raise BadBins('%s: a time that is not a whole second (te) or millisecond (tl)' % coin)
    out = {'te': te, 'tl': tl, 'n': n.astype(np.int32)}
    for f in ('px', 'hi', 'lo', 'buy', 'sell'):
        out[f] = np.asarray(b[f], dtype=np.float64)
    px, hi, lo = out['px'], out['hi'], out['lo']
    D0 = day_start_us(day)
    checks = [
        (not all(np.isfinite(out[k]).all() for k in ('px', 'hi', 'lo', 'buy', 'sell')), 'a value that is not a finite number'),
        (np.any(px <= 0), 'a close <= 0'),
        (np.any(hi < px), 'hi below its close'),
        (np.any(lo > px), 'lo above its close'),
        (len(te) > 1 and np.any(np.diff(te) <= 0), 'bin ends not rising'),
        (np.any((te - D0) % BIN_US != 0), 'a bin end off the 3 s grid'),
        (np.any((tl < te - BIN_US) | (tl >= te)), 'a last trade outside [t_end - 3 s, t_end)'),
        (np.any((te <= D0) | (te > D0 + DAY_US)), 'a bin end outside its day %s (D, D + 1 day]' % day),
    ]
    for bad, rule in checks:
        if bad:
            raise BadBins('%s %s: refused, %s' % (coin, day, rule))
    return {f: np.ascontiguousarray(out[f], dtype=DTYPE[f]) for f in FIELDS}


def _frame(path, fr, dtype):
    """one coin's frame of a BIN file: [pos, nbytes, sha16, rows]; sha16 checked (BlockChanged), never a value from a changed frame"""
    pos, nb, sha, rows = fr
    dt = np.dtype(dtype)
    if rows == 0:
        return np.zeros(0, dt)
    fd = os.open(path, os.O_RDONLY)
    try:
        data = os.pread(fd, nb, pos)
    finally:
        os.close(fd)
    if len(data) != nb or DY.sha16_bytes(data) != sha:
        raise DY.BlockChanged('%s bytes %d..%d are %s, its index names %s: refused' % (path, pos, pos + nb, DY.sha16_bytes(data), sha))
    return np.frombuffer(DY.CODEC.decompress(data, decompressed_size=int(rows) * dt.itemsize, asbytes=True), dtype=dt)


def _index(dd, part):
    ix = json.load(open(os.path.join(dd, part, 'index.json')))
    if ix.get('kind') != 'BIN':
        raise DY.NotBuilt('%s/%s: kind %r, not BIN' % (dd, part, ix.get('kind')))
    for f in ('off',) + FIELDS:                                                  # v5 (LAB4 09:06:46Z): a narrowed write is named
        if np.dtype(ix['bins'][f]['dtype']) != np.dtype(DTYPE[f]):
            raise DY.BlockChanged('%s/%s: field %s dtype %s in its index, the BIN kind is %s: refused' % (dd, part, f, ix['bins'][f]['dtype'], DTYPE[f]))
    return ix


def _off(dd, part, ix):
    return _frame(os.path.join(dd, part, 'BIN.off.lz4'), ix['bins']['off']['frames'][0], DTYPE['off'])


def coin_arrays(dd, part, ix, i, fields=FIELDS):
    """the i-th coin of the part (ix['coins'][i]): its arrays, one frame a field (pread, sha16 checked)"""
    return {f: _frame(os.path.join(dd, part, 'BIN.%s.lz4' % f), ix['bins'][f]['frames'][i], DTYPE[f]) for f in fields}


def _load(dd, part):
    ix = _index(dd, part)
    off = _off(dd, part, ix)
    per = [coin_arrays(dd, part, ix, i) for i in range(len(ix['coins']))]
    return ix, off, {f: np.concatenate([p[f] for p in per] or [np.zeros(0, DTYPE[f])]).astype(DTYPE[f]) for f in FIELDS}


def _write_frames(path, segs):
    """segs: arrays in coin order -> [[pos, nbytes, sha16, rows]] (one lz4 frame a coin, back to back; never over a file)"""
    out, pos = [], 0
    with open(path, 'xb') as f:
        for a in segs:
            data = DY.CODEC.compress(np.ascontiguousarray(a).tobytes(), asbytes=True) if len(a) else b''
            f.write(data)
            out.append([pos, len(data), DY.sha16_bytes(data), int(len(a))])
            pos += len(data)
    return out


def write_bins(root, day, coins, bins, sources=None, part=PART, missing=None):
    day = int(day); coins = list(coins)
    if len(set(coins)) != len(coins):
        raise BadBins('coins named twice')
    extra = sorted(set(bins) - set(coins))
    if extra:
        raise BadBins('bins of coins %s not in the day\'s coins: refused, never dropped' % extra[:5])
    if not part or '/' in part or part.startswith('.') or '.tmp_' in part or '.aside_' in part:
        raise ValueError('part name %r refused' % (part,))
    miss = list(missing or [])                                                   # v4 (LAB4 6.12d item 1, TREE note): one thing said a coin
    both = sorted(set(miss) & (set(coins) | set(bins)))                          # v5: missing = no source, DISJOINT from coins (prices_rec)
    if both or len(set(miss)) != len(miss):
        raise BadBins('coins_missing %s: %s' % (miss[:5], 'also listed in coins: %s' % both[:5] if both else 'a coin named twice'))
    good = {c: check_bins(c, bins[c], day) for c in coins if c in bins}          # every rule, every coin, BEFORE any file
    lens = [len(good[c]['te']) if c in good else 0 for c in coins]
    off = np.concatenate([[0], np.cumsum(lens)]).astype(DTYPE['off'])
    os.makedirs(root, exist_ok=True)
    W._format(root)
    dd = os.path.join(root, 'day=%d' % day); os.makedirs(dd, exist_ok=True)
    lockf = open(os.path.join(dd, '.lock_%s' % part), 'a')
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        lockf.close()
        raise RuntimeError('%s %d %s: another writer holds this (day, part): one writer at a time' % (root, day, part))
    try:
        stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S%fZ')
        tmp = os.path.join(dd, '%s.tmp_%s' % (part, stamp)); os.mkdir(tmp)
        files = {'off': {'dtype': DTYPE['off'], 'rows': len(off), 'frames': _write_frames(os.path.join(tmp, 'BIN.off.lz4'), [off])}}
        for f in FIELDS:
            segs = [good[c][f] if c in good else np.zeros(0, DTYPE[f]) for c in coins]
            files[f] = {'dtype': DTYPE[f], 'rows': int(sum(len(x) for x in segs)), 'frames': _write_frames(os.path.join(tmp, 'BIN.%s.lz4' % f), segs)}
        final = os.path.join(dd, part)
        aside = '%s.aside_%s' % (part, stamp) if os.path.exists(final) else None
        if aside and os.path.exists(os.path.join(dd, aside)):
            raise FileExistsError(aside)
        here = os.path.dirname(os.path.abspath(__file__))
        ix = {'day': day, 'part': part, 'kind': 'BIN', 'coins': coins, 'rows': int(off[-1]),
              'coins_with_rows': [c for c, n in zip(coins, lens) if n], 'coins_missing': sorted(missing or []), 'sources': dict(sorted((sources or {}).items())),
              'bins': files, 'readings': {}, 'inputs': {}, 'aside': aside, 'format': W.FORMAT,
              'code_sha16': {'lab3/' + m: DY.sha16_file(os.path.join(here, m)) for m in ('bins.py', 'write.py', 'days.py')},
              'built_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
        with open(os.path.join(tmp, 'index.json'), 'x') as fh:
            json.dump(ix, fh, sort_keys=True)
        _, off2, back = _load(dd, os.path.basename(tmp))                        # the whole part reads back before it is named
        if off2.tobytes() != off.tobytes() or any(back[f].tobytes() != np.concatenate(
                [good[c][f] for c in coins if c in good] or [np.zeros(0, DTYPE[f])]).astype(DTYPE[f]).tobytes() for f in FIELDS):
            raise AssertionError('%s: the part does not read back as written' % tmp)
        if aside:
            os.rename(final, os.path.join(dd, aside))
        os.rename(tmp, final)
        return ix
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN); lockf.close()


def read_bins(days, day, coins, part=PART, fields=FIELDS):
    """days: a lab3.days.Days (its purpose decides); -> (off, arrays) for coins in the order asked; fields = the subset of FIELDS to read
    (LAB1 V2_7: only those frames are decoded; an unknown field refuses)"""
    fields = tuple(fields)
    if not fields or any(f not in FIELDS for f in fields):
        raise ValueError('read_bins fields %r: a non-empty subset of %s only: refused' % (fields, FIELDS))
    days._guard(part, [str(day)])                                   # every purpose, before any IO (OUTSIDE D04-04; proof reads logged)
    dd = os.path.join(days.root, 'day=%s' % day)
    if not os.path.isdir(dd) or not DY.is_part(dd, part):
        raise DY.NotBuilt('%s %s: no %s part in %s: refused, never served as no prices' % (part, day, part, days.root))
    ix = _index(dd, part)
    off = _off(dd, part, ix)
    pos = {c: i for i, c in enumerate(ix['coins'])}
    per = [coin_arrays(dd, part, ix, pos[c], fields) for c in coins if c in pos]       # only the asked coins' and fields' frames are read
    for p, c in zip(per, [c for c in coins if c in pos]):
        for f in fields:
            if len(p[f]) != int(off[pos[c] + 1]) - int(off[pos[c]]):
                raise DY.BlockChanged('%s %s %s: frame %s rows %d, off says %d: refused' % (part, day, c, f, len(p[f]), int(off[pos[c] + 1]) - int(off[pos[c]])))
    lens =[int(off[pos[c] + 1]) - int(off[pos[c]]) if c in pos else 0 for c in coins]
    out_off = np.concatenate([[0], np.cumsum(lens)]).astype(np.int64)
    return out_off, {f: np.concatenate([p[f] for p in per] or [np.zeros(0, DTYPE[f])]).astype(DTYPE[f]) for f in fields}
