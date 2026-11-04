"""lab3/evt.py (BUILD5 for SCOUT, D2 of G1, 31 Oct 2026; CONDUCTOR RULING 13:08:49Z: "lab3/evt.py, a separate module, Days dispatching on
FORMAT.json (absent = old layout)"; ADR team/SCOUT/ADR_D2_COMPACT_OUTCOMES_STORE_V1.md d1c16fa85ff8a802; TEST, NOT REVIEWED): the COMPACT
layout of a lab_days root for ROWS parts (event outputs: OUT.<subject>), edition 3, layout 'evt1'.

WHY: an Outcomes run wrote, per event day, one lz4 file per code and field (169 codes x about 7 fields = about 1,355 files a day); the time
was the file count, not the values (PB3: write 24.1 s + commit 15.5 s of a 51 s run, job 20264959). Here a day's part is about 10 files.

LAYOUT (only this module writes it; lab3.days reads it through EvtDays, which Days(root, purpose) returns for a root whose FORMAT.json says
layout 'evt1'): <root>/FORMAT.json (write.py's FORMAT + layout evt1); <root>/day=<D>/<PART>/: ALL.<field>.lz4 for each ROWS field (off, u,
k, v, w, e, x), every code's array stacked in code order (sorted names), REASONS.txt (the part's reason ids, as write.py), WORDS.json
({code: [word texts]}), index.json LAST. The index keeps write.py's readings for each code (kind, value_kind, step, exact_k,
coins_with_rows, fields, dtypes, shape, shapes, rows_null, no_prev) with files = {field: sha16 of the code's raw slice bytes} and slices =
{field: [first, end)} into the stacked array, plus blocks = {field: {sha16 of the lz4 file, n}} and layout 'evt1'.
SAME ANSWERS: the arrays are lab3.write.rows_arrays' (imported, never re-made), so Days.rows, Days.at, words, reasons, step and
coins_with_rows answer exactly as for write.py's layout (tests: test_evt_v1.py).
ONE LAYOUT A ROOT: write.py refuses an evt1 root (its FORMAT differs), this writer refuses a root of write.py's FORMAT, and a reader
refuses a part whose layout is not its root's (MixedLayout).
COMMIT as write.py: one writer a (day, part) by flock; written in <PART>.tmp_<UTC>; read back whole through EvtDays (every code and
field: the file's sha16, the decode, the slice's sha16); the old part renamed <PART>.aside_<UTC>, the new one renamed in. A killed write
leaves a .tmp_ folder that no reader serves (lab3.days.is_part).
write_part(root, day, part, codes, coins, inputs=None, catalog=None, sources=None, seal=None) -> the part's index: write.write_part's
arguments and checks; ROWS codes only (a CLOCK code is refused EVT_ROWS_ONLY)."""
import datetime, errno, fcntl, json, os, re
import numpy as np
from . import days as DY, write as LW

LAYOUT = 'evt1'
FORMAT = dict(json.loads(json.dumps(LW.FORMAT)), layout=LAYOUT,
              block='ROWS parts: one lz4 file per field holding every code of the part, stacked in code order (index slices)')
FIELDS = LW.ROW_FIELDS
WORDS = 'WORDS.json'


def _code_shas():
    here = os.path.dirname(os.path.abspath(__file__))
    return dict(LW.CODE_SHAS, **{'lab3/evt.py': DY.sha16_file(os.path.join(here, 'evt.py'))})


CODE_SHAS = _code_shas()     # at import, as write.py: the code this process runs


class EvtDays(DY.Days):
    """lab3.days.Days for an evt1 root: the same API; block() slices the day's stacked field file, words come from WORDS.json"""
    LAYOUT = LAYOUT

    def __init__(self, root, purpose, run=None):
        super().__init__(root, purpose, run)
        self._stk = {}; self._wd = {}

    def _stack(self, day, part, field, ix):
        key = (str(day), part, field); got = self._stk.get(key)
        if got is not None and got[0] == ix['_sha16']:
            return got[1]
        b = ix['blocks'][field]
        p = os.path.join(self.root, 'day=%s' % day, part, 'ALL.%s.lz4' % field)
        with open(p, 'rb') as f:
            data = f.read()
        if DY.sha16_bytes(data) != b['sha16']:
            raise DY.BlockChanged('%s is %s, its index names %s: refused' % (p, DY.sha16_bytes(data), b['sha16']))
        dt = np.dtype(DY.DTYPE[field])
        raw = DY.CODEC.decompress(data, decompressed_size=int(b['n']) * dt.itemsize, asbytes=True)
        arr = np.frombuffer(raw, dtype=dt)
        self._stk[key] = (ix['_sha16'], arr)
        return arr

    def block(self, day, part, code, field):
        ix = self.index(day, part); r = ix['readings'][code]
        if field not in r['files']:
            raise DY.NotBuilt('%s %s: part %s has no field %s' % (code, day, part, field))
        lo, hi = r['slices'][field]
        seg = self._stack(day, part, field, ix)[int(lo):int(hi)]
        if DY.sha16_bytes(seg.tobytes()) != r['files'][field]:
            raise DY.BlockChanged('%s %s %s.%s: the slice is %s, its index names %s: refused'
                                  % (day, part, code, field, DY.sha16_bytes(seg.tobytes()), r['files'][field]))
        return seg.reshape(tuple(r['shapes'][field]))

    def _word_list(self, day, pt, code):
        ix = self.index(str(day), pt); key = (str(day), pt); got = self._wd.get(key)
        if got is None or got[0] != ix['_sha16']:
            p = os.path.join(self.root, 'day=%s' % day, pt, WORDS)
            with open(p) as f:
                got = (ix['_sha16'], json.load(f))
            self._wd[key] = got
        return list(got[1].get(code, []))


def _format(root):
    """write.py's _format for the evt1 FORMAT: a root of another FORMAT is refused (one layout a root)"""
    p = os.path.join(root, 'FORMAT.json')
    want = json.loads(json.dumps(FORMAT))
    if os.path.exists(p):
        with open(p) as f:
            got = json.load(f)
        if got != want:
            raise ValueError('%s: FORMAT %r, this writer writes %r: refused (one layout a root)' % (root, got, want))
        return
    tmp = '%s.tmp.%d.%s' % (p, os.getpid(), os.urandom(4).hex())
    with open(tmp, 'x') as f:
        json.dump(want, f, sort_keys=True)
    os.replace(tmp, p)
    with open(p) as f:
        if json.load(f) != want:
            raise ValueError('%s: FORMAT changed while written: refused' % root)


def _write_stack(path, arr):
    if os.path.exists(path):
        raise FileExistsError('%s exists: a block is never written over' % path)
    data = DY.CODEC.compress(np.ascontiguousarray(arr).tobytes(), asbytes=True)
    with open(path, 'xb') as f:
        f.write(data)
    return DY.sha16_bytes(data)


def write_part(root, day, part, codes, coins, inputs=None, catalog=None, sources=None, seal=None):
    """one ROWS part of one day in the evt1 layout, committed whole or not at all; -> its index (write.write_part's contract)"""
    sources = dict(sources or {})
    for nm, sh in sorted(sources.items(), key=lambda x: str(x[0])):
        if not nm or not isinstance(sh, str) or not re.fullmatch('[0-9a-f]{16}', sh):
            raise ValueError('source %r: sha16 %r: a source needs its 16-hex sha16: refused' % (nm, sh))
    if seal is not None and not isinstance(seal, str):
        raise ValueError('seal %r: a text or None' % (seal,))
    if catalog is None:
        catalog = LW.load_catalog()
    LW.check_catalog(codes, catalog)
    clock = sorted(c for c in codes if catalog[c]['kind'] != 'ROWS')
    if clock:
        raise ValueError('EVT_ROWS_ONLY: %s are not ROWS codes; the evt1 layout holds ROWS parts only (write.py writes CLOCK parts)' % clock[:3])
    codes = {c: dict(x, exact_k=bool(catalog[c].get('exact_k'))) for c, x in codes.items()}
    if not part or '/' in part or part.startswith('.') or '.tmp_' in part or '.aside_' in part:
        raise ValueError('part name %r refused' % (part,))
    day = int(day); coins = list(coins)
    if len(set(coins)) != len(coins):
        raise ValueError('coins named twice')
    os.makedirs(root, exist_ok=True)
    _format(root)
    ddir = os.path.join(root, 'day=%d' % day); os.makedirs(ddir, exist_ok=True)
    lockf = open(os.path.join(ddir, '.lock_%s' % part), 'a')
    try:
        fcntl.flock(lockf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        lockf.close()
        if e.errno in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EACCES):
            raise RuntimeError('%s %d %s: another writer holds this (day, part): one writer at a time' % (root, day, part))
        raise RuntimeError('%s %d %s: the lock failed (errno %s %s), not held by a writer: refused' % (root, day, part, e.errno, e.strerror))
    try:
        rd = DY.Days(root, 'build')
        if not isinstance(rd, EvtDays):
            raise ValueError('%s: Days did not dispatch this root to EvtDays: refused' % root)
        ins = {}
        for src in sorted(inputs or []):
            if not DY.is_part(ddir, src):
                raise DY.NotBuilt('%s %d: input part %s is not built: refused' % (part, day, src))
            ins[src] = DY.sha16_file(os.path.join(ddir, src, 'index.json'))
        stamp = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S%fZ')
        tmp = os.path.join(ddir, '%s.tmp_%s' % (part, stamp)); os.mkdir(tmp)
        reasons = ['']; readings = {}; words_of = {}; stack = {f: [] for f in FIELDS}; pos = {f: 0 for f in FIELDS}
        for code in sorted(codes):
            c = codes[code]; words = []; held = []
            try:
                arr, nnull = LW.rows_arrays(c, coins, day, reasons, words, held)
            except ValueError as ex:
                raise ValueError('%s %d: %s' % (code, day, ex)) from ex
            flds = list(arr); files = {}; slices = {}
            for f in flds:
                a = np.ascontiguousarray(arr[f]); files[f] = DY.sha16_bytes(a.tobytes())
                slices[f] = [pos[f], pos[f] + int(a.shape[0])]; pos[f] += int(a.shape[0]); stack[f].append(a)
            readings[code] = {'kind': 'ROWS', 'value_kind': c['kind'], 'step': c['step'], 'exact_k': bool(c.get('exact_k')),
                              'coins_with_rows': held, 'fields': flds, 'dtypes': {f: DY.DTYPE[f] for f in flds}, 'files': files,
                              'slices': slices, 'shape': [int(arr['u'].shape[0])], 'shapes': {f: list(arr[f].shape) for f in flds},
                              'rows_null': nnull}
            if c.get('no_prev'):
                readings[code]['no_prev'] = True
            words_of[code] = words
        blocks = {}
        for f in FIELDS:
            a = np.concatenate(stack[f]) if stack[f] else np.zeros(0, DY.DTYPE[f])
            blocks[f] = {'sha16': _write_stack(os.path.join(tmp, 'ALL.%s.lz4' % f), a.astype(DY.DTYPE[f], copy=False)), 'n': int(a.shape[0])}
        with open(os.path.join(tmp, WORDS), 'x') as fh:
            json.dump(words_of, fh, sort_keys=True)
        LW._write_list(os.path.join(tmp, 'REASONS.txt'), reasons)
        final = os.path.join(ddir, part)
        aside = None
        if os.path.exists(final):
            aside = '%s.aside_%s' % (part, stamp)
            if os.path.exists(os.path.join(ddir, aside)):
                raise FileExistsError(aside)
        ix = {'day': day, 'part': part, 'coins': coins, 'coins_missing': [], 'readings': readings, 'inputs': ins, 'aside': aside,
              'sources': sources, 'seal': seal, 'format': FORMAT, 'layout': LAYOUT, 'blocks': blocks, 'code_sha16': dict(CODE_SHAS),
              'built_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
        with open(os.path.join(tmp, 'index.json'), 'x') as f:
            json.dump(ix, f, sort_keys=True)
        name = os.path.basename(tmp)
        for code, r in readings.items():
            for f in r['fields']:
                rd.block(day, name, code, f)                              # the file's sha16, the decode and the slice's sha16: all reads back
        if aside:
            os.rename(final, os.path.join(ddir, aside))
        os.rename(tmp, final)
        return ix
    finally:
        fcntl.flock(lockf, fcntl.LOCK_UN); lockf.close()
