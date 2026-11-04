"""lab3/rows.py (LAB2, builder, 19 Oct 2026). rows(): the binary's rows of one code for coins and days, every field, from the lab v3's
lossless layer (LAB3_ARCH_V1 rev 7 729f0767, section 5.3). Standard Python only (runs in the VM). One file open at a time.
Names: this layer takes the CODE (GROUP.NAME, X1.GROUP.NAME); the catalog and aliases come in phase 4 after phase 3's PASS."""
import os, struct, datetime
from . import binfmt, labgroups

FIELDS = ('as_of_us', 'known_at_us', 'value_bits', 'value_kind', 'stale', 'value_txt', 'empty_reason', 'flags')

def days_between(day0, day1):
    d0 = datetime.datetime.strptime(str(day0), '%Y%m%d').date(); d1 = datetime.datetime.strptime(str(day1), '%Y%m%d').date()
    if d1 < d0:
        raise ValueError('day1 %s before day0 %s' % (day1, day0))
    out = []
    while d0 <= d1:
        out.append(int(d0.strftime('%Y%m%d'))); d0 += datetime.timedelta(days=1)
    return out

def as_float(b):
    return None if b is None else struct.unpack('<d', struct.pack('<Q', b))[0]

_MAN = {}

def manifest_keys(root, code, day):
    """the (code, coin) keys the day's manifest of this code's group lists, or None when the group's day is not built (no manifest).
    A manifest is written last, after every block of the group (build_day), so its presence means the group's day is built."""
    parts = code.split('.')
    if parts[0] == 'LAB':
        kind, group = 'lab', labgroups.lab_group(code)   # kanban 4.8: days/<D>/lab_LAB.tsv; 4.41: the split codes lab_LABTOP.tsv
    else:
        kind, group = ('x1', parts[1]) if parts[0] == 'X1' and len(parts) > 2 else ('l0bin', parts[0])
    p = os.path.join(root, 'days', str(day), '%s_%s.tsv' % (kind, group))
    if p in _MAN:
        return _MAN[p]
    if not os.path.exists(p):
        return None                      # not cached: a later build may write it
    keys = set()
    with open(p) as fh:
        for line in fh:
            if line.startswith('#') or line.startswith('code\t') or not line.strip():
                continue
            c, coin = line.split('\t', 2)[:2]
            keys.add((c, coin))
    _MAN[p] = keys
    return keys

def rows(root, code, coins, day0, day1, path_of=None):
    """-> {coin: {'day': [...], <every field>: [...], 'not_built': [days]}}. value_bits are the float64's raw bits (as_float gives the
    float). A day is NOT BUILT when its group's manifest is missing, or the manifest lists this code and coin but the block fails
    (torn, cut); a built day whose manifest does not list the code and coin had NO ROWS for it (C2, J19854: lab_v2 says NO_ROW_KNOWN)."""
    out = {}
    for coin in coins:
        r = {k: [] for k in ('day',) + FIELDS}; r['not_built'] = []
        for d in days_between(day0, day1):
            p = (path_of or _path)(root, code, coin, d)
            b = binfmt.read_day(p, d)
            if b is binfmt.NOT_BUILT:
                keys = manifest_keys(root, code, d)
                if keys is None or (code, coin) in keys:
                    r['not_built'].append(d)
                continue
            c = binfmt.decode_block(b)
            n = binfmt.block_rows(b)
            r['day'].extend([d] * n)
            for k in FIELDS:
                r[k].extend(c[k])
        out[coin] = r
    return out

def columns(root, code, coins, day0, day1, fields=('as_of_us', 'value_f64')):
    """The fast path of rows(): numeric columns as array objects (binfmt.decode_arrays), concatenated over the days, with null lists
    (None when a field has no null). -> {coin: {'day': array('i') a row, field: array, 'nulls': {field: list or None}, 'not_built'}}"""
    from array import array
    out = {}
    for coin in coins:
        r = {'day': array('i'), 'not_built': [], 'nulls': {f: None for f in fields}}
        for f in fields:
            r[f] = None
        for d in days_between(day0, day1):
            b = binfmt.read_day((_path)(root, code, coin, d), d)
            if b is binfmt.NOT_BUILT:
                keys = manifest_keys(root, code, d)
                if keys is None or (code, coin) in keys:
                    r['not_built'].append(d)
                continue
            a, nl = binfmt.decode_arrays(b, fields)
            n = binfmt.block_rows(b); before = len(r['day'])
            r['day'].extend(array('i', [d]) * n)
            for f in fields:
                if r[f] is None:
                    r[f] = a[f]
                else:
                    r[f].extend(a[f])
                if nl[f] is not None or r['nulls'][f] is not None:
                    cur = r['nulls'][f] if r['nulls'][f] is not None else [False] * before
                    cur.extend(nl[f] if nl[f] is not None else [False] * n); r['nulls'][f] = cur
        out[coin] = r
    return out

def columns_np(root, code, coins, day0, day1, fields=('as_of_us', 'value_f64')):
    """The numpy path of columns() (fastdecode.decode_np, LAB1 f8e55ef3; LAB4 R3): numpy arrays concatenated over the days.
    -> {coin: {'day': int32 array a row, field: array, 'nulls': {field: bool array or None}, 'not_built': [days]}}; equal to columns()."""
    import numpy as np
    from . import fastdecode as FD
    mask_of = {'as_of_us': 'as_of_us_null', 'known_at_us': 'known_at_us_null', 'value_f64': 'value_null', 'value_bits': 'value_null',
               'value_kind': 'value_kind_null', 'stale': 'stale_null'}
    out = {}
    for coin in coins:
        parts = {f: [] for f in fields}; masks = {f: [] for f in fields}; dayp = []; nb = []; any_null = {f: False for f in fields}
        for d in days_between(day0, day1):
            b = binfmt.read_day(_path(root, code, coin, d), d)
            if b is binfmt.NOT_BUILT:
                keys = manifest_keys(root, code, d)
                if keys is None or (code, coin) in keys:
                    nb.append(d)
                continue
            x = FD.decode_np(b, fields); n = x['rows']
            dayp.append(np.full(n, d, dtype=np.int32))
            for f in fields:
                parts[f].append(x[f]); m = x.get(mask_of[f])
                if m is not None:
                    any_null[f] = True
                masks[f].append(m if m is not None else np.zeros(n, dtype=bool))
        r = {'day': np.concatenate(dayp) if dayp else np.zeros(0, np.int32), 'not_built': nb, 'nulls': {}}
        for f in fields:
            r[f] = np.concatenate(parts[f]) if parts[f] else None
            r['nulls'][f] = np.concatenate(masks[f]) if any_null[f] else None
        out[coin] = r
    return out

def _path(root, code, coin, day):
    # the same rule as build_day.series_path (tested equal); kept here so the VM needs no pyarrow
    for part in (code, coin):
        if not part or '/' in part or part.startswith('.'):
            raise ValueError('cannot be a path part: %r' % part)
    return os.path.join(root, 'series', code, coin, '%s.bin' % str(day)[:4])
