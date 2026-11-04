"""lab3/write.py (LAB2, 20 Oct 2026; kanban 6.12, ARCH 14 rev 21 896165a7 sections 14.2 to 14.4): THE ONE WRITER of lab_days, the
one format (edition 3). Made from gridbuild_v1.py's write half (write_block: lz4 frame of a C-order array, never over a file;
append-only REASONS and WORDS; the day's index written last; a partial part moved aside, never deleted; one writer a root by flock).
The cells are C1's as-of rule (lab3/asof.py: the key, value_text, reason_text, rint_age, the D-1 hour), imported, never re-made: the
sweep here is numpy, its key order and texts are lab3.asof's. Tests first: LAB4's test_lab3_write_days_v1.py 0d6c7993 (16).

write_part(root, day, part, codes, coins, inputs=None) -> the part's index
  codes  = {code: {'step': 5 | 30 | 60, 'kind': 'NUMBER' | 'WORD', 'rows': {coin: ROWS}}}, ROWS = lab3.rows' columns (day D-1 or D,
           as_of_us, known_at_us, value_kind, value_bits, value_txt, empty_reason, stale) of one length;
           optional 'no_prev': True when the source holds no D-1 for this code (team/LAB3 FIRST_DAYS list, LAB1 09:34:26Z): 00:00 to
           00:59 is unknown with reason NO_PREV_DAY (C1 needs D-1 there), 01:00 on is C1 from D's rows; the index keeps 'no_prev';
  coins  = the day's row order (a coin without rows is a row of NO_ROW_KNOWN);
  inputs = the parts of the same day this part is made from (their index sha16 kept: the reader says STALE_INPUT when one changes).
CLOCK kind (ARCH rev 21b 14.3), fields (coins, 86,400 / step): v f8 (NaN unknown; WORD codes NaN), w i2 (WORD codes: word id, -1
unknown), a i4 (age s, half to even; INT32_MIN unknown), e u1 (reason id, 0 none), o i8 (t_k - the answering point's as_of in us, an
OFFSET; INT64_MIN unknown), k i8 (its known_at in us) ONLY for a code given 'exact_k': True (METRICS exact_k). Each part has its OWN
REASONS.txt and WORDS/<code>.txt (EDGE1 A1). One writer a (day, part) at a time: flock <root>/day=<D>/.lock_<PART>.
Commit: written in <PART>.tmp_<UTC>, read back whole through lab3.days, then the old part (if any) renamed <PART>.aside_<UTC> (named in
the new index) and the new one renamed in. ROWS kind: rows_arrays (6.12b): a part keeps day D's own rows as they are, by coin (off), with
u, k, v, w, e, x; Days.rows and Days.at read them. TABLE and BAND parts: lab3/tb.py (6.12c). NOT HERE yet: BIN (PRICE, 6.12d bins.py)."""
import datetime, errno, fcntl, json, os, re
import numpy as np
from . import asof as AS, days as DY

US = 1_000_000
I32MIN = -2147483648
I64MIN = -9223372036854775808
STEPS = (5, 30, 60)
KINDS = ('NUMBER', 'WORD')
FORMAT = {'store': 'lab_days', 'edition': DY.EDITION, 'codec': 'pyarrow lz4 frame', 'block': '(coins, steps) C order',
          'steps': [3, 5, 30, 60], 'dtype': DY.DTYPE, 'absent': {'v': 'NaN', 'w': -1, 'a': I32MIN, 'e': 255, 'o': I64MIN, 'k': I64MIN},
          'clock': 'column k = the value as known at t_k = D 00:00 UTC + step x k (edition 2 rule)',
          'rule': 'C1 as-of (lab3/asof.py)'}
FIELDS = {'NUMBER': ('v', 'a', 'e', 'o'), 'WORD': ('w', 'a', 'e', 'o')}
NO_ROW = AS.NO_ROW
COLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')


def _prev(day):
    return int((datetime.datetime.strptime(str(day), '%Y%m%d') - datetime.timedelta(days=1)).strftime('%Y%m%d'))


def _cols(rows):
    """the row columns as numpy: as_of, known_at (0 where null), day, and the kept mask (both present)"""
    n = len(rows['day'])
    DD = np.array(rows['day'], np.int64) if n else np.zeros(0, np.int64)
    try:
        A_ = np.array(rows['as_of_us'], np.int64) if n else np.zeros(0, np.int64)
        K_ = np.array(rows['known_at_us'], np.int64) if n else np.zeros(0, np.int64)
        ok = np.ones(n, bool)
    except TypeError:                                                 # a null as_of or known_at: never kept (C1)
        ok = np.array([x is not None and y is not None for x, y in zip(rows['as_of_us'], rows['known_at_us'])], bool)
        A_ = np.array([x if x is not None else 0 for x in rows['as_of_us']], np.int64)
        K_ = np.array([x if x is not None else 0 for x in rows['known_at_us']], np.int64)
    return A_, K_, DD, ok


def _rank(rows, sel, cols=None):
    """sel: the kept row positions -> their order by lab3.asof's key (as_of, known_at, value text, reason text, day, position);
    numpy on (as_of, known_at, day, position), the texts only inside ties of (as_of, known_at)"""
    sel = np.asarray(sel, np.int64)
    A_, K_, DD, _ = cols if cols is not None else _cols(rows)
    a = A_[sel]; k = K_[sel]; dd = DD[sel]; ps = sel
    order = np.lexsort((ps, dd, k, a))
    if len(order) > 1:
        sa, sk = a[order], k[order]
        tie = np.flatnonzero((sa[1:] == sa[:-1]) & (sk[1:] == sk[:-1]))
        if len(tie):
            order = order.copy(); j = 0; T = set(tie.tolist()); n = len(order)
            while j < n - 1:
                if j in T:
                    s_ = j
                    while j in T:
                        j += 1
                    grp = order[s_:j + 1].tolist()
                    def key(g):
                        i = int(sel[g])
                        return (AS.value_text(rows['value_kind'][i], rows['value_bits'][i], rows['value_txt'][i]),
                                AS.reason_text(rows['empty_reason'][i], rows['stale'][i]), rows['day'][i], i)
                    order[s_:j + 1] = sorted(grp, key=key)
                j += 1
    return a, k, order


def _answers(rows, sel, ts, cols=None):
    """the answering kept row (a position into rows) at each t of ts, or -1: the last row in key order with as_of <= t, known_at <= t"""
    out = np.full(len(ts), -1, np.int64)
    sel = np.asarray(sel, np.int64)
    if not len(sel):
        return out
    a, k, order = _rank(rows, sel, cols)
    n = len(sel); rank = np.empty(n, np.int64); rank[order] = np.arange(n)
    te = np.maximum(a, k); by_t = np.lexsort((rank, te))
    tes = te[by_t]; cum = np.maximum.accumulate(rank[by_t])
    p = np.searchsorted(tes, ts, side='right')
    hit = p > 0
    out[hit] = sel[order[cum[p[hit] - 1]]]
    return out


def _cells(rows, day, step):
    d0 = AS.day_start_us(day); P = _prev(day); D = int(day)
    ts = d0 + step * US * np.arange(86400 // step, dtype=np.int64)
    cols = _cols(rows); A_, K_, DD, ok = cols
    early = ts - AS.HOUR_US < d0
    pos = np.full(len(ts), -1, np.int64)
    sel_e = np.flatnonzero(ok & ((DD == P) | (DD == D))); sel_l = np.flatnonzero(ok & (DD == D))
    if early.any():
        pos[early] = _answers(rows, sel_e, ts[early], cols)
    if (~early).any():
        pos[~early] = _answers(rows, sel_l, ts[~early], cols)
    return pos, ts, cols


def cells(rows, day, step):
    """-> (pos, ts): for each step end of day (t_k = D 00:00 + step x k, k = 0 .. 86,400 / step - 1) the answering row position or -1.
    Rows read: day(t - 1 h) and day(t) (lab3.asof); rows with a null as_of or known_at never kept."""
    pos, ts, _ = _cells(rows, day, step)
    return pos, ts


def _age(t, kn):
    d = t - kn; q = d // US; r = d % US
    return (q + ((r > US // 2) | ((r == US // 2) & (q % 2 == 1)))).astype(np.int64)


def _float(kind, b, txt):
    if kind in (1, 2) and b is not None:
        return np.frombuffer(int(b).to_bytes(8, 'little'), '<f8')[0]
    t = AS.value_text(kind, b, txt)
    try:
        return float(t) if t != '' else np.nan
    except ValueError:
        return np.nan


class WordNumber(ValueError):
    """a WORD code's answering row holds a number: lab_days has no v for WORD codes, so it would vanish; refused (LAB1 09:08:43Z)"""


def _word_of(kind, bits, txt):
    """the word a WORD code's row holds, or None (w -1) for an empty row (kind 0 or an empty text), as the served grid (u1_view_v2.py
    lines 119 to 133). A number (kind 1 or 2 with bits, or a text float() takes: the grid put it in v) raises WordNumber: the catalog must
    then give the code a number unit (LAB1 09:08:43Z; C11.S08 was this case)."""
    if kind == 0:
        return None
    if kind in (1, 2) and bits is not None:
        raise WordNumber('kind %d with bits' % kind)
    t = '' if txt is None else txt
    if t == '':
        return None
    try:
        float(t)
    except ValueError:
        return t
    raise WordNumber('text %r is a number' % t)


def _has_row_of(rows, day):
    """the ONE rule of coins_with_rows: the coin has a row of day D with an as_of and a known_at (LAB4 6.21 item 2)"""
    return any(int(dd) == day and a_ is not None and k_ is not None
               for dd, a_, k_ in zip(rows['day'], rows['as_of_us'], rows['known_at_us']))


def code_arrays(c, coins, day, reasons, words, held=None):
    """one code's arrays (coins, steps) by its kind; reasons, words: the part's lists (appended to)"""
    step, kind = c['step'], c['kind']
    if step not in STEPS or kind not in KINDS:
        raise ValueError('step %r, kind %r: CLOCK codes take step %s and kind %s' % (step, kind, STEPS, KINDS))
    extra = set(c['rows']) - set(coins)
    if extra:
        raise ValueError('rows of coins %s not in the day\'s coins: refused, never dropped' % sorted(extra))
    n = 86400 // step; rix = {t: i for i, t in enumerate(reasons)}
    wix = {t: i for i, t in enumerate(words)}
    flds = FIELDS[kind] + (('k',) if c.get('exact_k') else ())
    arr = {f: np.full((len(coins), n), DY.ABSENT[f], DY.DTYPE[f]) for f in flds}
    pv = _prev(day)
    for ci, coin in enumerate(coins):
        rows = c['rows'].get(coin) or {k: [] for k in ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')}
        if held is not None and _has_row_of(rows, int(day)):
            held.append(coin)                                          # from the rows in hand: each coin's rows fetched ONCE (BED 08:54:56Z)
        L = len(rows['day'])
        if any(len(rows[f]) != L for f in ('as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')):
            raise ValueError('%s: the row columns are not of one length' % coin)
        no_prev = bool(c.get('no_prev'))
        if no_prev and L and bool((np.asarray(rows['day'], dtype=np.int64) == pv).any()):     # LAB1 25 Oct (BUILD4-031658): D-1 once, not per row
            raise ValueError('%s: no_prev (the source holds no D-1) but rows of D-1 %d were handed: refused, never dropped (BED 6.12f item 1)'
                             % (coin, pv))
        pos, ts, cols = _cells(rows, day, step)
        if no_prev:                                                  # FIRST_DAYS (LAB1 09:34:26Z (b)): C1 needs D-1's tail in 00:00 to 00:59
            early_np = ts < AS.day_start_us(day) + AS.HOUR_US         # and D-1 does not exist: no cell of that hour is guessed
            pos = np.where(early_np, -1, pos)
        hit = pos >= 0
        if NO_ROW not in rix:
            rix[NO_ROW] = len(reasons); reasons.append(NO_ROW)
        e = np.full(n, rix[NO_ROW], np.uint8); a = np.full(n, I32MIN, np.int64)
        o = np.full(n, I64MIN, np.int64); kk = np.full(n, I64MIN, np.int64)
        hj = np.flatnonzero(hit)
        if len(hj):
            hp = pos[hj]
            u, first, inv = np.unique(hp, return_index=True, return_inverse=True)
            by_first = np.argsort(first, kind='stable')               # the rows in first-hit order: the lists grow as before
            ul = u.tolist(); m = len(ul)
            eid = np.empty(m, np.int64); val = np.empty(m, np.float64 if kind == 'NUMBER' else np.int64)
            ER, ST, VK, VB, VT = rows['empty_reason'], rows['stale'], rows['value_kind'], rows['value_bits'], rows['value_txt']
            rcache = {}
            for q in by_first.tolist():
                i = ul[q]
                key = (ER[i], ST[i])
                r = rcache.get(key)
                if r is None:
                    why = AS.reason_text(*key)
                    if why not in rix:
                        rix[why] = len(reasons); reasons.append(why)
                    r = rcache[key] = rix[why]
                eid[q] = r
                if kind == 'WORD':
                    t = _word_of(VK[i], VB[i], VT[i])                 # None: w -1; a number: WordNumber (v5c rule, unchanged)
                    if t is None:
                        val[q] = -1
                    else:
                        if t not in wix:
                            wix[t] = len(words); words.append(t)
                        val[q] = wix[t]
            if kind == 'NUMBER':
                vk = np.array([VK[i] for i in ul], np.int64); vb = [VB[i] for i in ul]
                fast = ((vk == 1) | (vk == 2)) & np.array([x is not None for x in vb], bool)
                fq = np.flatnonzero(fast)
                if len(fq):
                    val[fq] = np.array([vb[q] for q in fq.tolist()], np.uint64).view('<f8')
                for q in np.flatnonzero(~fast).tolist():
                    val[q] = _float(VK[ul[q]], VB[ul[q]], VT[ul[q]])
            if len(reasons) > 255:
                raise OverflowError('more than 255 reason texts in a part (255 is ABSENT)')
            if len(words) > 32767:
                raise OverflowError('more than 32,767 words')
            e[hj] = eid[inv]
            o[hj] = cols[0][u][inv]
            kk[hj] = cols[1][u][inv]
            a[hj] = _age(ts[hj], kk[hj])
            if (a[hj] < 0).any():
                raise AssertionError('a cell uses a row known after its step end')
            if kind == 'WORD':
                arr['w'][ci, hj] = val[inv]
            else:
                arr['v'][ci, hj] = val[inv]
        if no_prev:
            if DY.NO_PREV not in rix:
                rix[DY.NO_PREV] = len(reasons); reasons.append(DY.NO_PREV)
                if len(reasons) > 255:
                    raise OverflowError('more than 255 reason texts in a part (255 is ABSENT)')
            e[early_np] = rix[DY.NO_PREV]
        off = np.full(n, I64MIN, np.int64); off[hj] = ts[hj] - o[hj]
        arr['a'][ci] = a.astype('<i4'); arr['e'][ci] = e; arr['o'][ci] = off
        if 'k' in arr:
            arr['k'][ci] = kk
    return arr


ROW_FIELDS = ('off', 'u', 'k', 'v', 'w', 'e', 'x')


def rows_arrays(c, coins, day, reasons, words, held=None):
    """ROWS kind (ARCH rev 21b 14.3): day D's own rows with an as_of and a known_at, as they are, by coin in the day's order, each
    coin's rows in lab3.asof's key order (as_of, known_at, value text, reason text, day, position). -> (arrays, null rows of D).
    off i8 (coins + 1): coin i's rows are [off[i], off[i+1]); u i8 as_of - D 00:00 in us (not CLOCK's o); k i8 known_at in us; v f8 the float of a
    row's bits, ANY kind with bits (NaN when bits is None: x bit 4); w i2 a word id for a text value (else -1); e u1 the empty_reason id (STALE is in x, not here);
    x u1 = value_kind 0 to 7 (bits 0 to 2; l0bin's 4 OTHER kept) | stale (bit 3) | bits null (bit 4). D-1's rows are D-1's part's: the reader reads that part."""
    if c['step'] != 'event' or c['kind'] not in KINDS:
        raise ValueError('step %r, kind %r: ROWS codes take step event and kind %s' % (c['step'], c['kind'], KINDS))
    extra = set(c['rows']) - set(coins)
    if extra:
        raise ValueError('rows of coins %s not in the day\'s coins: refused, never dropped' % sorted(extra))
    D = int(day); d0 = AS.day_start_us(day)
    rix = {t: i for i, t in enumerate(reasons)}; wix = {t: i for i, t in enumerate(words)}
    off = [0]; cols = {f: [] for f in ROW_FIELDS[1:]}; nnull = 0
    for coin in coins:
        rows = c['rows'].get(coin) or {k: [] for k in COLS}
        if c.get('no_prev') and any(int(dd) == _prev(day) for dd in rows['day']):
            raise ValueError('%s: no_prev (the source holds no D-1) but rows of D-1 %d were handed: refused, never dropped (BED 6.12f item 1)'
                             % (coin, _prev(day)))
        if held is not None and _has_row_of(rows, int(day)):
            held.append(coin)
        L = len(rows['day'])
        if any(len(rows[f]) != L for f in COLS):
            raise ValueError('%s: the row columns are not of one length' % coin)
        mine = [i for i in range(L) if int(rows['day'][i]) == D]
        sel = [i for i in mine if rows['as_of_us'][i] is not None and rows['known_at_us'][i] is not None]
        nnull += len(mine) - len(sel)
        if sel:
            _, _, order = _rank(rows, sel)
            for j in order.tolist():
                i = sel[j]; kind = int(rows['value_kind'][i]); bits = rows['value_bits'][i]; txt = rows['value_txt'][i]
                er = rows['empty_reason'][i] or ''
                if er not in rix:
                    rix[er] = len(reasons); reasons.append(er)
                text_word = kind >= 3 or (kind in (1, 2) and bits is None)
                if text_word and txt is not None:
                    if txt not in wix:
                        wix[txt] = len(words); words.append(txt)
                    w = wix[txt]
                else:
                    w = -1
                v = np.frombuffer(int(bits).to_bytes(8, 'little'), '<f8')[0] if bits is not None else np.nan   # any kind: rows as they are (LAB1 item 1, J27070)
                cols['u'].append(rows['as_of_us'][i] - d0); cols['k'].append(rows['known_at_us'][i]); cols['v'].append(v)
                cols['w'].append(w); cols['e'].append(rix[er])
                if not 0 <= kind <= 7:
                    raise ValueError('%s: value_kind %r outside 0 to 7' % (coin, kind))
                cols['x'].append(kind | (8 if rows['stale'][i] == 1 else 0) | (16 if bits is None else 0))
        off.append(off[-1] + len(sel))
    if len(reasons) > 255:
        raise OverflowError('more than 255 reason texts in a part (255 is ABSENT)')
    if len(words) > 32767:
        raise OverflowError('more than 32,767 words')
    arr = {'off': np.array(off, DY.DTYPE['off'])}
    for f in ROW_FIELDS[1:]:
        arr[f] = np.array(cols[f], DY.DTYPE[f]) if cols[f] else np.zeros(0, DY.DTYPE[f])
    return arr, nnull


def _write_list(path, items):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'x') as f:
        for x in items:
            f.write(json.dumps(x) + '\n')


def _write_block(path, arr):
    if os.path.exists(path):
        raise FileExistsError('%s exists: a block is never written over' % path)
    data = DY.CODEC.compress(np.ascontiguousarray(arr).tobytes(), asbytes=True)
    with open(path, 'xb') as f:
        f.write(data)
    return DY.sha16_bytes(data)


def _code_shas():
    here = os.path.dirname(os.path.abspath(__file__))
    return {'lab3/' + m: DY.sha16_file(os.path.join(here, m)) for m in ('write.py', 'days.py', 'asof.py')}


CODE_SHAS = _code_shas()     # at import: the code this process RUNS (a file changed later never relabels its parts; LAB2 09:14:44Z, rule 29)


def _format(root):
    p = os.path.join(root, 'FORMAT.json')
    want = json.loads(json.dumps(FORMAT))
    if os.path.exists(p):
        with open(p) as f:
            got = json.load(f)
        if got != want:
            raise ValueError('%s: FORMAT %r, this writer writes %r: refused' % (root, got, want))
        return
    tmp = '%s.tmp.%d.%s' % (p, os.getpid(), os.urandom(4).hex())           # LAB1 V2_7: one tmp per writer (two writers on a fresh root raced on .tmp)
    with open(tmp, 'x') as f:
        json.dump(want, f, sort_keys=True)
    os.replace(tmp, p)                                                         # both writers write the same bytes; the last replace wins
    with open(p) as f:
        if json.load(f) != want:
            raise ValueError('%s: FORMAT changed while written: refused' % root)


METRICS = os.environ.get('LAB3_METRICS') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'METRICS_V1.tsv'))


def load_catalog(path=None):
    """{code: {'kind', 'clock', 'exact_k', 'scope'}} from METRICS_V1 (rev 21b: one catalog). The store kind is read from the column
    'store' (CLOCK, ROWS, TABLE): METRICS' own column 'kind' already names something else (VALUE, TWIN, ADDON, ...; rev q, LAB2
    07:5xZ). A METRICS without store, clock, exact_k or scope is refused by name (the writer never guesses a clock)"""
    import csv
    csv.field_size_limit(10 ** 9)
    with open(path or METRICS, newline='') as f:
        rows = csv.reader((l for l in f if not l.startswith('#')), delimiter='\t')
        h = next(rows); need = ('code', 'store', 'clock', 'exact_k', 'scope')
        miss = [c for c in need if c not in h]
        if miss:
            raise ValueError('%s lacks the columns %s (ARCH rev 21b 14.3): the writer refuses to guess' % (path or METRICS, miss))
        ix = {c: h.index(c) for c in need}
        out = {}
        for r in rows:
            ck = r[ix['clock']].strip()
            out[r[ix['code']]] = {'kind': r[ix['store']].strip(), 'clock': int(ck) if ck.isdigit() else ck,
                                  'exact_k': r[ix['exact_k']].strip().lower() in ('1', 'true', 'yes'), 'scope': r[ix['scope']].strip()}
        return out


WRITES = ('CLOCK', 'ROWS')                                            # TABLE, BAND: 6.12c (EDGE2); PRICE BIN: 6.12d (BED)


def check_catalog(codes, catalog):
    """the rows handed must agree with the catalog: every code listed, kind CLOCK or ROWS, clock = step ('event' for ROWS), exact_k the same, market codes one
    row MARKET, coin+market codes their coins plus one MARKET row (METRICS rev s, X1.VOLX.S01; LAB1 08:46:52Z), every other scope no
    MARKET row; else ValueError naming the code (FINDING 2: market codes once built empty with no error)"""
    bad = []
    for code in sorted(codes):
        c = codes[code]; cat = catalog.get(code)
        if cat is None:
            bad.append('%s: not in the catalog' % code); continue
        if cat.get('kind') not in WRITES:
            bad.append('%s: catalog kind %r, this writer writes %s' % (code, cat.get('kind'), ', '.join(WRITES)))
        if cat.get('clock') != c['step']:
            bad.append('%s: rows at %r s, catalog clock %r' % (code, c['step'], cat.get('clock')))
        if 'exact_k' in c and bool(c['exact_k']) != bool(cat.get('exact_k')):
            bad.append('%s: exact_k %r, catalog %r' % (code, c['exact_k'], cat.get('exact_k')))
        scope = cat.get('scope', 'coin')
        keys = set(c['rows'])
        if scope == 'market' and keys - {'MARKET'}:
            bad.append('%s: catalog scope market, rows by coin %s' % (code, sorted(keys - {'MARKET'})[:3]))
        if scope not in ('market', 'coin+market') and 'MARKET' in keys:
            bad.append('%s: catalog scope %r, rows of MARKET' % (code, scope))
    if bad:
        raise ValueError('refused by the catalog: ' + '; '.join(bad))


def write_part(root, day, part, codes, coins, inputs=None, catalog=None, sources=None, seal=None):
    """one part of one day, committed whole or not at all; -> its index. catalog: {code: {kind, clock, exact_k, scope}}, default
    METRICS_V1 (load_catalog); the rows are checked against it before anything is written. sources: {raw file name: sha16} the part
    is made from and seal: its SEAL text, both kept in the index (ARCH 14.3; EDGE1 6.12a item 1); a name without a 16-hex sha16 refused."""
    sources = dict(sources or {})
    for nm, sh in sorted(sources.items(), key=lambda x: str(x[0])):
        if not nm or not isinstance(sh, str) or not re.fullmatch('[0-9a-f]{16}', sh):
            raise ValueError('source %r: sha16 %r: a source needs its 16-hex sha16: refused' % (nm, sh))
    if seal is not None and not isinstance(seal, str):
        raise ValueError('seal %r: a text or None' % (seal,))
    if catalog is None:
        catalog = load_catalog()
    check_catalog(codes, catalog)
    codes = {c: dict(x, exact_k=bool(catalog[c].get('exact_k'))) for c, x in codes.items()}
    if not part or '/' in part or part.startswith('.') or '.tmp_' in part or '.aside_' in part:
        raise ValueError('part name %r refused' % (part,))
    day = int(day); coins = list(coins)
    if len(set(coins)) != len(coins):
        raise ValueError('coins named twice')
    os.makedirs(root, exist_ok=True)
    _format(root)
    ddir = os.path.join(root, 'day=%d' % day); os.makedirs(ddir, exist_ok=True)
    lockf = open(os.path.join(ddir, '.lock_%s' % part), 'a')         # a dot name: never a part, never an aside (J26953: X1.lock was)
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        lockf.close()
        if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EACCES):
            raise RuntimeError('%s %d %s: another writer holds this (day, part): one writer at a time' % (root, day, part))
        raise RuntimeError('%s %d %s: the lock failed (errno %s %s), not held by a writer: refused' % (root, day, part, e.errno, e.strerror))
    try:
        rd = DY.Days(root, 'build')
        ins = {}
        for src in sorted(inputs or []):
            if not DY.is_part(ddir, src):
                raise DY.NotBuilt('%s %d: input part %s is not built: refused' % (part, day, src))
            ins[src] = DY.sha16_file(os.path.join(ddir, src, 'index.json'))
        stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S%fZ')
        tmp = os.path.join(ddir, '%s.tmp_%s' % (part, stamp)); os.mkdir(tmp)
        reasons = ['']; readings = {}
        for code in sorted(codes):
            c = codes[code]; words = []; store = catalog[code]['kind']
            if store == 'ROWS':
                held = []
                try:
                    arr, nnull = rows_arrays(c, coins, day, reasons, words, held)
                except ValueError as ex:
                    raise ValueError('%s %d: %s' % (code, day, ex)) from ex
            else:
                held = []
                try:
                    arr = code_arrays(c, coins, day, reasons, words, held)
                except WordNumber as ex:
                    raise WordNumber('%s %d: a WORD code row answers a cell with a number (%s): refused, give it a number unit in METRICS' % (code, day, ex))
                except ValueError as ex:
                    raise ValueError('%s %d: %s' % (code, day, ex)) from ex
            flds = list(arr)
            files = {f: _write_block(os.path.join(tmp, '%s.%s.lz4' % (code, f)), arr[f]) for f in flds}
            readings[code] = {'kind': store, 'value_kind': c['kind'], 'step': c['step'], 'exact_k': bool(c.get('exact_k')),
                              'coins_with_rows': held,
                              'fields': flds, 'dtypes': {f: DY.DTYPE[f] for f in flds}, 'files': files}
            if c.get('no_prev'):
                readings[code]['no_prev'] = True                     # the reader's at() answers 00:00 to 00:59 NO_PREV_DAY, never reads D-1
            if store == 'ROWS':
                readings[code].update(shape=[int(arr['u'].shape[0])], shapes={f: list(arr[f].shape) for f in flds}, rows_null=nnull)
            else:
                readings[code]['shape'] = [len(coins), 86400 // c['step']]
            if c['kind'] == 'WORD' or store == 'ROWS':
                _write_list(os.path.join(tmp, 'WORDS', '%s.txt' % code), words)
            del arr
        _write_list(os.path.join(tmp, 'REASONS.txt'), reasons)
        final = os.path.join(ddir, part)
        aside = None
        if os.path.exists(final):
            aside = '%s.aside_%s' % (part, stamp)
            if os.path.exists(os.path.join(ddir, aside)):
                raise FileExistsError(aside)
        ix = {'day': day, 'part': part, 'coins': coins, 'coins_missing': [], 'readings': readings, 'inputs': ins,
              'aside': aside, 'sources': sources, 'seal': seal, 'format': FORMAT, 'code_sha16': dict(CODE_SHAS),
              'built_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
        with open(os.path.join(tmp, 'index.json'), 'x') as f:
            json.dump(ix, f, sort_keys=True)
        name = os.path.basename(tmp)
        for code, r in readings.items():
            for f in r['fields']:
                rd.block(day, name, code, f)                              # sha16 and shape: the whole part reads back
        if aside:
            os.rename(final, os.path.join(ddir, aside))
        os.rename(tmp, final)
        return ix
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN); lockf.close()
