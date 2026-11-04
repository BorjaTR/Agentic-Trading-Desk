"""lab3/binfmt.py (LAB2, builder, 19 Oct 2026). The name-free layer of the lab v3: the .bin year file (one code, one coin, one year) and the
day block. LAB3_ARCH_V1 rev 4 7c837a78 sections 5.2 and 5.4 (steps 1, 2). Tests first: tests/test_binfmt_v1.py. Standard Python only.

FILE  = head + day blocks appended in build order.
HEAD  = magic 'LAB3', version u16, year u16, 8 reserved bytes, then 366 slots of (offset u64, length u32, rows u32, crc32 u32).
        A slot with length 0, or whose block fails its length or crc32, is NOT BUILT (never an empty value).
BLOCK = 'B1', rows u32, then zlib level 1 of the columns, in the binary's row order (nothing sorted, merged or dropped):
        as_of_us     int64: first value then steps (null bitmap if any null; a null counts as 0 for the steps)
        known_at_us  int64: known_at_us - as_of_us (null bitmap if any null)
        value_bits   uint64: the float64's 64 raw bits (every NaN payload, -0.0, subnormal kept; null bitmap if any null)
        value_kind   int8 (null bitmap if any null)
        stale        int8 (null bitmap if any null)
        value_txt, empty_reason, flags: uint32 codes into the block's own word list (0 = null; '' is a word, kept apart from null)
COMMIT = append the block at the end, write its slot, then one fsync: the slot is the commit and its crc32 covers the block."""
import os, sys, struct, zlib, datetime
from array import array
from itertools import accumulate
from operator import add

MAGIC = b'LAB3'; VERSION = 1; NSLOTS = 366
HEAD = struct.Struct('<4sHH8x'); SLOT = struct.Struct('<QIII')
SLOTS_AT = HEAD.size; SLOT_BYTES = SLOT.size; HEAD_BYTES = HEAD.size + NSLOTS * SLOT.size
BMAGIC = b'B1'; BHEAD = struct.Struct('<2sI')
TMAGIC = b'T1'                      # a whole-day table block (lab3/tables.py, kanban 4.17): same head, same commit; never a series block
T2MAGIC = b'T2'                     # the same, its groups with schemas that differ, one table a group (J23216 20250924)
INT_COLS = ('as_of_us', 'known_at_us'); I8_COLS = ('value_kind', 'stale'); TXT_COLS = ('value_txt', 'empty_reason', 'flags')
COLS = INT_COLS + ('value_bits',) + I8_COLS + TXT_COLS
LITTLE = sys.byteorder == 'little'
NOT_BUILT = type('NotBuilt', (), {'__repr__': lambda s: 'NOT_BUILT', '__bool__': lambda s: False})()

class Head:
    __slots__ = ('version', 'year', 'slots')
    def __init__(self, version, year, slots):
        self.version, self.year, self.slots = version, year, slots

def new_head(year):
    return HEAD.pack(MAGIC, VERSION, int(year)) + bytes(NSLOTS * SLOT.size)

def read_head(b):
    if len(b) < HEAD_BYTES:
        raise ValueError('head too short: %d bytes' % len(b))
    magic, version, year = HEAD.unpack_from(b, 0)
    if magic != MAGIC:
        raise ValueError('not a lab3 file (magic %r)' % magic)
    if version != VERSION:
        raise ValueError('format version %d, this reader knows %d' % (version, VERSION))
    return Head(version, year, [SLOT.unpack_from(b, SLOTS_AT + i * SLOT.size) for i in range(NSLOTS)])

def day_slot(yyyymmdd):
    s = str(int(yyyymmdd))
    try:
        d = datetime.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except ValueError as e:
        raise ValueError('not a day: %s (%s)' % (yyyymmdd, e))
    return d.timetuple().tm_yday - 1

# ---- block codec
def _arr(code, xs):
    a = array(code, xs)
    if not LITTLE: a.byteswap()
    return a.tobytes()

def _unarr(code, b, n, at):
    a = array(code); size = a.itemsize * n
    a.frombytes(b[at:at + size])
    if not LITTLE: a.byteswap()
    return a, at + size

def _bitmap(xs):
    if all(x is not None for x in xs):
        return b'\x00'
    m = bytearray((len(xs) + 7) // 8)
    for i, x in enumerate(xs):
        if x is None: m[i >> 3] |= 1 << (i & 7)
    return b'\x01' + bytes(m)

def _unbitmap(b, n, at):
    if b[at] == 0:
        return None, at + 1
    m = b[at + 1:at + 1 + (n + 7) // 8]
    return [bool(m[i >> 3] >> (i & 7) & 1) for i in range(n)], at + 1 + (n + 7) // 8

def encode_block(cols):
    missing = [c for c in COLS if c not in cols]; extra = [c for c in cols if c not in COLS]
    if missing or extra:
        raise ValueError('columns: missing %s, unknown %s' % (missing, extra))
    n = len(cols['as_of_us'])
    if any(len(cols[c]) != n for c in COLS):
        raise ValueError('columns of unequal length: %s' % {c: len(cols[c]) for c in COLS})
    out = []
    a = cols['as_of_us']; a0 = [0 if x is None else int(x) for x in a]
    out.append(_bitmap(a)); out.append(_arr('q', [a0[0]] + [a0[i] - a0[i - 1] for i in range(1, n)] if n else []))
    k = cols['known_at_us']
    out.append(_bitmap(k)); out.append(_arr('q', [0 if x is None else int(x) - a0[i] for i, x in enumerate(k)]))
    vb = cols['value_bits']
    if any(x is not None and (not isinstance(x, int) or x < 0 or x >= 1 << 64) for x in vb):
        raise ValueError('value_bits must be ints in 0..2**64-1 (the float64 raw bits) or None')
    out.append(_bitmap(vb)); out.append(_arr('Q', [0 if x is None else x for x in vb]))
    for c in I8_COLS:
        xs = cols[c]
        if any(x is not None and not -128 <= x <= 127 for x in xs):
            raise ValueError('%s outside int8' % c)
        out.append(_bitmap(xs)); out.append(_arr('b', [0 if x is None else int(x) for x in xs]))
    for c in TXT_COLS:
        words = {}; codes = []
        for x in cols[c]:
            if x is None:
                codes.append(0)
            else:
                if not isinstance(x, str): raise ValueError('%s holds a non-text value %r' % (c, x))
                codes.append(words.setdefault(x, len(words) + 1))
        wb = [w.encode('utf-8') for w in words]
        out.append(struct.pack('<I', len(wb)))
        out.append(_arr('I', [len(w) for w in wb])); out.append(b''.join(wb)); out.append(_arr('I', codes))
    return BHEAD.pack(BMAGIC, n) + zlib.compress(b''.join(out), 1)

def block_rows(block):
    magic, n = BHEAD.unpack_from(block, 0)
    if magic != BMAGIC: raise ValueError('not a lab3 block')
    return n

def committed_rows(block):
    """the rows a slot records: a series block (B1) or a table block (T1); anything else refused"""
    magic, n = BHEAD.unpack_from(block, 0)
    if magic not in (BMAGIC, TMAGIC, T2MAGIC): raise ValueError('not a lab3 block or table block')
    return n

def _with_nulls(vals, nul):
    if nul is None:
        return vals
    return [None if z else v for v, z in zip(vals, nul)]

def decode_block(block):
    """Fast paths (LAB4 10:51:06Z: R3 5 s codes 546 to 742 ms in the VM): accumulate, map and zip run in C; None only where a bitmap says."""
    n = block_rows(block); b = zlib.decompress(block[BHEAD.size:]); at = 0; cols = {}
    nul, at = _unbitmap(b, n, at); st, at = _unarr('q', b, n, at)
    a0 = list(accumulate(st))
    cols['as_of_us'] = _with_nulls(a0, nul)
    nul, at = _unbitmap(b, n, at); kd, at = _unarr('q', b, n, at)
    cols['known_at_us'] = _with_nulls(list(map(add, kd, a0)), nul)
    nul, at = _unbitmap(b, n, at); vb, at = _unarr('Q', b, n, at)
    cols['value_bits'] = _with_nulls(vb.tolist(), nul)
    for c in I8_COLS:
        nul, at = _unbitmap(b, n, at); xs, at = _unarr('b', b, n, at)
        cols[c] = _with_nulls(xs.tolist(), nul)
    for c in TXT_COLS:
        (nw,) = struct.unpack_from('<I', b, at); at += 4
        lens, at = _unarr('I', b, nw, at); words = [None]
        for ln in lens:
            words.append(b[at:at + ln].decode('utf-8')); at += ln
        codes, at = _unarr('I', b, n, at)
        cols[c] = [None] * n if nw == 0 else list(map(words.__getitem__, codes))
    if at != len(b):
        raise ValueError('block has %d trailing bytes' % (len(b) - at))
    return cols

ARRAY_FIELDS = ('as_of_us', 'known_at_us', 'value_f64', 'value_kind', 'stale')

def decode_arrays(block, fields=ARRAY_FIELDS):
    """The fast column path (LAB4 11:44:04Z: R3 at 5 s 367 to 553 ms with full rows): numeric columns as array objects, no Python object a
    row except the as_of steps summed in C. -> ({field: array}, {field: null list or None}). value_f64 is array('d') filled from the raw
    bytes, so every bit (NaN payloads) is the binary's. Text columns are not given here (rows() gives them)."""
    bad = [f for f in fields if f not in ARRAY_FIELDS]
    if bad:
        raise ValueError('decode_arrays gives %s only, not %s' % (ARRAY_FIELDS, bad))
    n = block_rows(block); b = zlib.decompress(block[BHEAD.size:]); at = 0; out = {}; nulls = {}
    nul, at = _unbitmap(b, n, at); st, at = _unarr('q', b, n, at)
    need_a = 'as_of_us' in fields or 'known_at_us' in fields
    a0 = array('q', accumulate(st)) if need_a else None
    if 'as_of_us' in fields:
        out['as_of_us'] = a0; nulls['as_of_us'] = nul
    nul, at = _unbitmap(b, n, at); kd, at = _unarr('q', b, n, at)
    if 'known_at_us' in fields:
        out['known_at_us'] = array('q', map(add, kd, a0)); nulls['known_at_us'] = nul
    nul, at = _unbitmap(b, n, at)
    if 'value_f64' in fields:
        v = array('d'); v.frombytes(b[at:at + 8 * n])
        if not LITTLE: v.byteswap()
        out['value_f64'] = v; nulls['value_f64'] = nul
    at += 8 * n
    for c in I8_COLS:
        nul, at = _unbitmap(b, n, at)
        if c in fields:
            x = array('b'); x.frombytes(b[at:at + n]); out[c] = x; nulls[c] = nul
        at += n
    return out, nulls

# ---- the year file
def _slot_ok(f, size, s):
    off, ln, rows, crc = s
    if ln == 0 or off < HEAD_BYTES or off + ln > size:
        return None
    f.seek(off); body = f.read(ln)
    return body if len(body) == ln and zlib.crc32(body) == crc else None

def append_day(path, yyyymmdd, block):
    """Append one day's block and commit its slot. Refuses a day already built (its slot passes its crc32);
    a NOT BUILT slot (empty or torn) is written: new bytes at the end, the slot rewritten. Earlier bytes never change."""
    year = int(str(yyyymmdd)[:4]); i = day_slot(yyyymmdd); rows = committed_rows(block)
    if not os.path.exists(path):
        # a new year file appears whole: head written to a temp name, fsynced, then renamed into place (LAB4 11:12:26Z), so a reader
        # never meets a file shorter than its head. The caller holds the root's one-writer lock (build_day.root_lock).
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        tmp = '%s.part.%d' % (path, os.getpid())
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            os.write(fd, new_head(year)); os.fsync(fd)
        finally:
            os.close(fd)
        if os.path.exists(path):
            raise FileExistsError('%s appeared while creating it: is a second writer on this root?' % path)
        os.rename(tmp, path)
    with open(path, 'r+b') as f:
        h = read_head(f.read(HEAD_BYTES))
        if h.year != year:
            raise ValueError('%s is year %d, the day is %s' % (path, h.year, yyyymmdd))
        size = os.fstat(f.fileno()).st_size
        if _slot_ok(f, size, h.slots[i]) is not None:
            raise FileExistsError('%s day %s is built (slot %d passes its crc): rebuild is a separate logged command' % (path, yyyymmdd, i))
        off = size
        f.seek(off); f.write(block); f.flush()
        f.seek(SLOTS_AT + i * SLOT.size); f.write(SLOT.pack(off, len(block), rows, zlib.crc32(block))); f.flush()
        os.fsync(f.fileno())
    return (off, len(block), rows, zlib.crc32(block))

def read_day(path, yyyymmdd):
    i = day_slot(yyyymmdd)
    try:
        f = open(path, 'rb')
    except FileNotFoundError:
        return NOT_BUILT
    with f:
        hb = f.read(HEAD_BYTES)
        if len(hb) < HEAD_BYTES:
            return NOT_BUILT            # a file without its whole head holds no committed day
        h = read_head(hb)
        if h.year != int(str(yyyymmdd)[:4]):
            raise ValueError('%s is year %d, asked %s' % (path, h.year, yyyymmdd))
        body = _slot_ok(f, os.fstat(f.fileno()).st_size, h.slots[i])
    return NOT_BUILT if body is None else body
