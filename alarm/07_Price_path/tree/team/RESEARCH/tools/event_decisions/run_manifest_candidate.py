# run_manifest_candidate_evt1.py: a NEW edition of the shared run check (owner STRATEGY; BUILD5 builds it, CONDUCTOR RULING 13:33:04Z;
# TEST, NOT REVIEWED), made by team/BUILD5/proposals/d2_lab3/rm_fix1/make_rm_d2.py from run_manifest_candidate.py 1a99409b69d6644a,
# never edited: _index_blocks reads an evt1 part (lab3/evt.py) by its ALL.<field>.lz4 files; nothing else changes. The text follows.
"""run_manifest_candidate_next.py: the shared run check V3 with S1 (decisions_fixer, owner of S1; FIX_ROUND3_V1, 25 Oct 2026). STAGED: it
becomes run_manifest_candidate.py in the LEAD's re-cut round with labcore V2_7. API note: team/RESEARCH/LEAD/SHARED_S1_NOTE_V2.md.
S1 closes the integrity faults the outside round-2 reviews found in six tools (Cause R2-01 / R2-02, Context C-R2-02, Situations A49R2-01,
Decisions R1, alarm tool A54-F2 residual, Outcomes A51R2-04), once, here:
- every file of every part inventoried and verified: names exact (an added or removed file refuses), text bytes (index.json, REASONS.txt,
  WORDS/*.txt) hashed, payload blocks checked against the index sha16 and decoded through lab3 (Days.block);
- the run's metadata bound: the manifest carries a seal over its whole content (coverage, selection, identity, inputs, digests), the
  files outside the parts (catalog, plan, receipts) are inventoried, and the coverage (window and days) is sealed: a requested day
  outside it refuses RANGE_NOT_COVERED, so nobody widens a run by editing a field;
- ONE verify (verify_committed) for admit, read, UP TO DATE and resume; commit itself rechecks every staged part (against the receipt
  taken when the part was written) and decodes every block before anything is published;
- values are returned only after a recheck AFTER the read (recheck_after_read / read_verified);
- freeze_inputs / recheck_inputs: settings, event lists, configured files, transitive code and upstream parts INCLUDING ABSENCE, frozen at
  admission and rechecked before commit (commit(frozen=...)) and before consumption (verify_committed(inputs=True));
- old V2 runs still verify (no seal, no coverage: covered days are the days with parts; ALL_FILES_V2 digests); every V2 name works.
Digest kinds (A51R2-04): INDEX_AND_TEXT_V3 does not hash payload bytes into the digest (the index pins them). load_complete therefore
hashes every block of a V3 part against its index, and verify_committed decodes every block, so no caller is opened to a flipped block
by the faster kind. A receipt carries its kind; part_digest / verify_part default to ALL_FILES_V2 for old callers, and a V3 digest
checked as ALL_FILES never matches (refused, never accepted). The seal is a sha16, not a signature: it stops edits, not a forger who
recomputes it on purpose (there is no key in this lab). S1 fields live under manifest['run_check'] (format, coverage, root_files,
inputs), sealed by manifest['run_check_seal'] over the WHOLE manifest; a manifest carrying either key without a matching seal refuses.
Errors: RunRefused(code): BAD_OUT_ROOT, OUTPUT_EXISTS, RUN_NOT_PUBLISHED, RUN_INCOMPLETE, RUN_CHANGED_AFTER_COMMIT, CORRUPT_RUN,
RANGE_NOT_COVERED, SELECTION_NOT_COVERED, PART_CHANGED_BEFORE_COMMIT, SEALED_FILE_CHANGED, INPUTS_CHANGED, RUN_CHANGED_DURING_READ. Only data faults become
codes: a fault of the checker itself propagates as it is (tester N6), a lab3 law refusal (PermissionError) propagates.
  stage(out_root) -> pending                        commit(pending, out_root, name, body, receipts=None, frozen=None, window=None)
  abort(pending, out_root, error)                   part_receipt(root, part_dir, kind=DIGEST_KIND) -> {'digest', 'files', 'kind'}
  load_complete(root, name, prefix=None, days=None) verify_committed(root, name, prefix=None, code_dir=None, purpose='research',
  verify_part(root, part_dir, digest_or_receipt, ...)                                    days=None, inputs=True)
  recheck_after_read(root, name, m, prefix=None, days=None)    read_verified(root, name, read, prefix=None, code_dir=None, ...)
  freeze_inputs(files=None, sources=None, code='loaded', code_roots=None)    recheck_inputs(frozen, strict_code=True)
  seal_of(obj)   write_sealed_json(path, obj)   load_sealed_json(path)   part_digest(root, part_dir, kind=ALL_FILES)
History: V1 whole-run publication (A50 K2: stage, check, rename, manifest last); V2 part digests of every file (tester N2); V3 digest
kinds (ctxprof K4 speed) and named catches (tester N6); S1 above.
  python3 run_manifest_candidate_next.py verify <root> <manifest name> [<part prefix>] [--code-dir <lab3 code>] [--days D1,D2] [--no-inputs]"""
import datetime, hashlib, json, os, sys

SCHEMA = 'RUN_MANIFEST_V1'                                                   # unchanged: consumers compare it (event_situations)
FORMAT = 3                                                                   # S1 manifests: sealed, coverage, root files, inputs
ALL_FILES = 'ALL_FILES_V2'                                                   # every file's bytes (V2, the default of part_digest / verify_part)
DIGEST_KIND = 'INDEX_AND_TEXT_V3'                                            # text files' bytes + block file names (blocks pinned by the index)
KINDS = (ALL_FILES, DIGEST_KIND)
RC, RC_SEAL = 'run_check', 'run_check_seal'                                  # S1 fields live under one key (no clash with a tool's own
# manifest fields, e.g. Decisions' 'inputs' counts); a manifest carrying run_check must carry its seal
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
LAB3_CODE = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), 'LAB3', 'code')
ABSENT = 'ABSENT'


class RunRefused(ValueError):
    """a run that may not be consumed or published, named by its code"""
    def __init__(self, code, msg):
        super().__init__('%s: %s' % (code, msg)); self.code = code


def sha16_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def _stamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')


def write_json_atomic(path, obj):
    """tmp + fsync + os.replace: the file is either absent or whole"""
    tmp = '%s.tmp_%d' % (path, os.getpid())
    with open(tmp, 'x') as f:
        json.dump(obj, f, sort_keys=True, indent=1, allow_nan=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def _fsync_dir(d):
    fd = os.open(d, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


# ---------------------------------------------------------------- seals
def _plain(obj):
    return json.loads(json.dumps(obj, sort_keys=True, allow_nan=False))      # the object exactly as it reads back from disk


def seal_of(obj, key='seal'):
    """sha16 of the canonical JSON of obj without its seal key"""
    o = {k: v for k, v in _plain(obj).items() if k != key}
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()[:16]


def write_sealed_json(path, obj):
    o = _plain(obj); o['seal'] = seal_of(o)
    write_json_atomic(path, o)
    return o


def load_sealed_json(path, code='SEALED_FILE_CHANGED'):
    try:
        with open(path) as f:
            o = json.load(f)
    except (OSError, ValueError) as e:
        raise RunRefused(code, '%s: unreadable: %s' % (path, e))
    if not isinstance(o, dict) or o.get('seal') != seal_of(o):
        raise RunRefused(code, '%s: its content does not match its seal (edited after it was written)' % path)
    return o


# ---------------------------------------------------------------- parts
def stage(out_root):
    if not out_root or out_root.endswith('/') or os.path.basename(out_root).startswith('.'):
        raise RunRefused('BAD_OUT_ROOT', 'out_root %r' % (out_root,))
    parent = os.path.dirname(os.path.abspath(out_root))
    if not os.path.isdir(parent):
        raise RunRefused('BAD_OUT_ROOT', '%s: its folder does not exist' % out_root)
    if os.path.lexists(out_root):
        raise RunRefused('OUTPUT_EXISTS', '%s exists: a run is published into a new root only' % out_root)
    pending = '%s.pending_%d_%s' % (out_root, os.getpid(), _stamp())
    os.makedirs(pending)
    return pending


def _part_dirs(parts):
    """the committed part folders 'day=D/PART' named by the manifest's parts keys (index.json or any file of the part)"""
    return sorted({'/'.join(rel.split('/')[:2]) for rel in parts if rel.startswith('day=') and rel.count('/') >= 2})


def _day(pd):
    return pd.split('/')[0][4:]


def part_digest(root, part_dir, kind=ALL_FILES):
    """(sha16, n_files) of the files under <root>/<part_dir>, recursive, relative paths sorted. ALL_FILES_V2: every file's bytes.
    INDEX_AND_TEXT_V3: every file's bytes except the *.lz4 blocks, which enter by NAME only (their bytes are pinned in index.json).
    A changed text file, a changed index, an added or removed file changes either digest."""
    if kind not in KINDS:
        raise RunRefused('CORRUPT_RUN', '%s/%s: unknown digest kind %r' % (root, part_dir, kind))
    base = os.path.join(root, part_dir); lines = []
    for r, _, files in os.walk(base):
        for f in files:
            q = os.path.join(r, f); rel = os.path.relpath(q, base)
            lines.append('%s\t%s' % (rel, 'BLOCK' if (kind == DIGEST_KIND and f.endswith('.lz4')) else sha16_file(q)))
    lines.sort()
    return hashlib.sha256(('%s\n' % kind if kind != ALL_FILES else '').encode() + '\n'.join(lines).encode()).hexdigest()[:16], len(lines)


def part_receipt(root, part_dir, kind=DIGEST_KIND):
    """the receipt of a part just written: keep it (in memory or a sealed plan) and pass it to commit / verify_part at resume"""
    d, n = part_digest(root, part_dir, kind)
    return {'digest': d, 'files': n, 'kind': kind}


def _index_blocks(root, part_dir, code):
    """[(block path, sha16 the index names)] of a part, from its index.json (whose bytes the digest pins); D2: an evt1 part's blocks are
    its ALL.<field>.lz4 files (index blocks)"""
    p = os.path.join(root, part_dir, 'index.json')
    try:
        with open(p) as f:
            ix = json.load(f)
        out = []
        if ix.get('layout') == 'evt1':                                   # D2 (BUILD5): lab3/evt.py's stacked field files
            for field, b in sorted(ix['blocks'].items()):
                out.append((os.path.join(root, part_dir, 'ALL.%s.lz4' % field), b['sha16']))
            return out
        for c, r in sorted(ix['readings'].items()):
            for field, sha in sorted(r['files'].items()):
                out.append((os.path.join(root, part_dir, '%s.%s.lz4' % (c, field)), sha))
        return out
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise RunRefused(code, '%s: unreadable part index: %s: %s' % (p, type(e).__name__, e))


def _hash_blocks(root, part_dir, code):
    """every payload block of the part against the sha16 its index names (no decode)"""
    for q, sha in _index_blocks(root, part_dir, code):
        if not os.path.isfile(q) or sha16_file(q) != sha:
            raise RunRefused(code, '%s: payload block missing or changed (its index names %s)' % (q, sha))


def _lab3_days(code_dir):
    code_dir = code_dir or LAB3_CODE
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
    from lab3 import days as LD
    return LD


def _decode_part(root, part_dir, code_dir, purpose):
    """every payload block of every reading through lab3 Days.block (bytes vs index sha16, lz4, shape) -> n blocks; CORRUPT_RUN"""
    LD = _lab3_days(code_dir)
    day, part = _day(part_dir), part_dir.split('/')[1]
    R = LD.Days(root, purpose); blocks = 0                                   # a fresh reader: no cached index
    try:
        ix = R.index(day, part)
        for code, r in sorted(ix['readings'].items()):
            for field in sorted(r['files']):
                R.block(day, part, code, field); blocks += 1
    except PermissionError:
        raise
    except (LD.BlockChanged, LD.NotBuilt, OSError, ValueError, KeyError) as e:   # tester N6: only an integrity failure of the DATA is
        raise RunRefused('CORRUPT_RUN', '%s/%s: %s: %s' % (root, part_dir, type(e).__name__, str(e)[:300]))   # CORRUPT_RUN; a fault of
    return blocks                                                            # the checker itself (NameError, TypeError, ...) propagates


def _check_part(root, part_dir, digest, kind, changed, code_dir=None, purpose='research', decode=True):
    if not os.path.isdir(os.path.join(root, part_dir)):
        raise RunRefused(changed, '%s/%s missing' % (root, part_dir))
    d, n = part_digest(root, part_dir, kind)
    if d != digest:
        raise RunRefused(changed, '%s/%s: its files changed (%d files now)' % (root, part_dir, n))
    if decode:
        return _decode_part(root, part_dir, code_dir, purpose)
    if kind == DIGEST_KIND:
        _hash_blocks(root, part_dir, changed)
    return 0


def verify_part(root, part_dir, digest, code_dir=None, purpose='research', kind=ALL_FILES, decode=True):
    """one committed lab3 part: its file digest equals the committed one (a receipt dict carries its own kind) -> RUN_CHANGED_AFTER_COMMIT;
    then every payload block through lab3 (CORRUPT_RUN) -> the number of blocks checked (decode=False: blocks hashed against the index)"""
    if isinstance(digest, dict):
        digest, kind = digest['digest'], digest.get('kind', ALL_FILES)
    return _check_part(root, part_dir, digest, kind, 'RUN_CHANGED_AFTER_COMMIT', code_dir, purpose, decode)


# ---------------------------------------------------------------- inputs: freeze at admission, recheck before commit and consumption
def _under(path, roots):
    a, r = os.path.abspath(path), os.path.realpath(path)
    for x in roots:
        xa, xr = os.path.abspath(x) + os.sep, os.path.realpath(x) + os.sep
        if a.startswith(xa) or r.startswith(xr):
            return True
    return False


def _loaded_code(roots):
    out = {}
    for mod in list(sys.modules.values()):
        f = getattr(mod, '__file__', None)
        if f and f.endswith('.py') and _under(f, roots):
            out[os.path.abspath(f)] = f
    return out


def _file_state(p):
    return sha16_file(p) if p and os.path.isfile(p) else ABSENT


def _source_state(spec):
    """the state of an upstream lab3 root as a consumer will read it: per part, the index sha16 and the text-and-names digest, or ABSENT
    (no folder or no index.json); per day of a prefix, the set of its parts; the root's top-level files (manifests, catalogs)"""
    root = spec['root']
    if not os.path.isdir(root):
        return {'root': ABSENT}
    st = {'top': {f: sha16_file(os.path.join(root, f)) for f in sorted(os.listdir(root))
                  if os.path.isfile(os.path.join(root, f)) and '.tmp_' not in f}}
    pds = list(spec.get('parts') or [])
    if spec.get('prefix'):
        pre = spec['prefix']
        for d in sorted(str(x) for x in spec.get('days') or []):
            dd = os.path.join(root, 'day=%s' % d)
            found = sorted(p for p in os.listdir(dd) if (p == pre or p.startswith(pre + '.')) and '.tmp_' not in p and '.aside_' not in p) \
                if os.path.isdir(dd) else []
            pds += ['day=%s/%s' % (d, p) for p in found] or ['day=%s/%s' % (d, pre)]
    parts = {}
    for pd in sorted(set(pds)):
        ix = os.path.join(root, pd, 'index.json')
        parts[pd] = ABSENT if not os.path.isfile(ix) else {'index': sha16_file(ix), 'digest': part_digest(root, pd, DIGEST_KIND)[0]}
    st['parts'] = parts
    return st


def freeze_inputs(files=None, sources=None, code='loaded', code_roots=None):
    """the input identity of a run, taken at admission (after preflight and its lazy imports):
    files {label: path}: sha16 or ABSENT; sources {label: {'root', 'parts': [...]} or {'root', 'prefix', 'days'}}: see _source_state;
    code 'loaded' (every module under code_roots, default team/RESEARCH/tools and team/LAB3/code) or a list of paths -> sha16.
    -> {'schema', 'files', 'sources', 'code', 'code_roots', 'frozen_utc', 'sha16'}; sha16 is the identity (put it in the run_id)"""
    roots = [os.path.abspath(x) for x in (code_roots or (TOOLS, LAB3_CODE))]
    fz = {'schema': 'INPUT_FREEZE_V1', 'code_roots': roots,
          'files': {k: {'path': os.path.abspath(p), 'sha16': _file_state(p)} for k, p in sorted((files or {}).items()) if p is not None},
          'sources': {k: {'spec': {kk: (sorted(str(x) for x in vv) if isinstance(vv, (list, tuple, set)) else vv) for kk, vv in spec.items()},
                          'state': _source_state(spec)} for k, spec in sorted((sources or {}).items())}}
    loaded = sorted(_loaded_code(roots))
    paths = loaded if code == 'loaded' else sorted(os.path.abspath(p) for p in (code or []))
    fz['code'] = {p: _file_state(p) for p in paths}
    fz['loaded_at_freeze'] = loaded                                          # the late-import check compares with this set
    fz = _plain(fz)
    fz['sha16'] = seal_of({k: v for k, v in fz.items() if k != 'frozen_utc'}); fz['frozen_utc'] = utc_now()
    return fz


def recheck_inputs(frozen, strict_code=True, what=('files', 'sources', 'code')):
    """every frozen input as it is now; any change, disappearance or APPEARANCE (absent at the freeze, present now) -> INPUTS_CHANGED.
    strict_code: a team module loaded after the freeze (its bytes are not in the identity) refuses too."""
    if not frozen:
        return
    diff = []
    if 'files' in what:
        for k, x in sorted(frozen.get('files', {}).items()):
            now = _file_state(x['path'])
            if now != x['sha16']:
                diff.append('%s %s: %s at the freeze, %s now' % (k, x['path'], x['sha16'], now))
    if 'sources' in what:
        for k, x in sorted(frozen.get('sources', {}).items()):
            now = _plain(_source_state(x['spec']))
            if now != x['state']:
                was, cur = x['state'], now
                keys = sorted(set((was.get('parts') or {})) | set((cur.get('parts') or {})))
                bits = ['%s %s -> %s' % (pd, 'ABSENT' if (was.get('parts') or {}).get(pd) == ABSENT else 'built',
                                         'ABSENT' if (cur.get('parts') or {}).get(pd) == ABSENT else 'built')
                        for pd in keys if (was.get('parts') or {}).get(pd) != (cur.get('parts') or {}).get(pd)]
                if was.get('top') != cur.get('top') or was.get('root') != cur.get('root'):
                    bits.append('root files or the root itself changed')
                diff.append('source %s %s: %s' % (k, x['spec'].get('root'), '; '.join(bits[:4]) or 'changed'))
    if 'code' in what:
        for p, sha in sorted(frozen.get('code', {}).items()):
            now = _file_state(p)
            if now != sha:
                diff.append('code %s: %s at the freeze, %s now' % (p, sha, now))
        if strict_code:
            late = sorted(set(_loaded_code(frozen.get('code_roots') or [TOOLS, LAB3_CODE])) - set(frozen.get('code', {}))
                          - set(frozen.get('loaded_at_freeze') or []))
            if late:
                diff.append('code loaded after the freeze (not in the identity): %s' % ', '.join(late[:4]))
    if diff:
        raise RunRefused('INPUTS_CHANGED', '%d input(s) changed since the freeze: %s' % (len(diff), ' | '.join(diff[:6])))


# ---------------------------------------------------------------- commit
def _root_files(root, skip):
    """every file of the run outside the day=D/PART folders (catalogs, plans, receipts, any side file) -> {relative path: sha16}"""
    out = {}
    for r, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(r, root)
        top = rel_dir.split(os.sep)[0]
        if top.startswith('day='):
            dirs[:] = []; continue                                           # a day folder: its parts have digests, lab3 locks are not
            # run content, and a day-scoped verify must never open another day (N4, C-R2-02)
        for f in files:
            rel = os.path.normpath(os.path.join(rel_dir, f)) if rel_dir != '.' else f
            if rel in skip or '.tmp_' in f:
                continue
            out[rel.replace(os.sep, '/')] = sha16_file(os.path.join(r, f))
    return out


def commit(pending, out_root, name, body, receipts=None, frozen=None, window=None, code_dir=None, purpose='research', coins=None):
    """publish a staged run, after checking it: every part against its receipt (PART_CHANGED_BEFORE_COMMIT) and through lab3 (CORRUPT_RUN);
    the frozen inputs rechecked (INPUTS_CHANGED); root files inventoried; coverage from window=(first, last) (+ the days with parts);
    coins: the coins the run covers (its resolved selection), sealed: a consumer asking for another coin refuses SELECTION_NOT_COVERED;
    the manifest sealed; folder renamed to out_root; the manifest renamed last (the terminal commit)"""
    for k in ('parts', 'selection', 'run_id'):
        if k not in body:
            raise ValueError('a COMPLETE manifest names %s' % k)
    pds = _part_dirs(body['parts']); digests = {}
    for pd in pds:
        if receipts is not None:
            rc = receipts.get(pd)
            if not isinstance(rc, dict) or 'digest' not in rc:
                raise RunRefused('PART_CHANGED_BEFORE_COMMIT', '%s/%s has no receipt from when it was written' % (pending, pd))
            _check_part(pending, pd, rc['digest'], rc.get('kind', ALL_FILES), 'PART_CHANGED_BEFORE_COMMIT', code_dir, purpose)
            kind = rc.get('kind', ALL_FILES); d, n = rc['digest'], rc.get('files') or part_digest(pending, pd, kind)[1]
        else:
            kind = DIGEST_KIND; d, n = part_digest(pending, pd, kind)
            _decode_part(pending, pd, code_dir, purpose)
        digests[pd] = {'digest': d, 'files': n, 'kind': kind}
    for rel, sha in sorted(body['parts'].items()):                           # the caller's own part pins still hold
        q = os.path.join(pending, rel)
        if not os.path.isfile(q) or sha16_file(q) != sha:
            raise RunRefused('PART_CHANGED_BEFORE_COMMIT', '%s changed after the caller pinned it' % rel)
    if frozen:
        recheck_inputs(frozen, strict_code=False)                             # before anything is published (no late-import check: the
    days = sorted({_day(pd) for pd in pds})                                   # caller may import after its freeze inside its own build)
    if window is not None:
        first, last = str(window[0]), str(window[1])
        if first > last or any(not (first <= d <= last) for d in days):
            raise RunRefused('RANGE_NOT_COVERED', 'window %s..%s does not hold the committed days %s' % (first, last, days[:3]))
        cov = {'first': first, 'last': last, 'days': days}
    else:
        cov = {'first': None, 'last': None, 'days': days}
    cov['coins'] = sorted({str(c) for c in coins}) if coins is not None else None
    staged = '%s.json.staged' % name
    rc = {'format': FORMAT, 'coverage': cov, 'root_files': _root_files(pending, {staged, '%s.json' % name})}
    if frozen:
        rc['inputs'] = _plain(frozen)
    m = dict(_plain(body), schema=SCHEMA, status='COMPLETE', exit_status=0, committed_utc=utc_now(), part_digests=digests)
    m[RC] = rc
    m[RC_SEAL] = seal_of(m, RC_SEAL)
    write_json_atomic(os.path.join(pending, staged), m)
    if os.path.lexists(out_root):
        raise RunRefused('OUTPUT_EXISTS', '%s appeared during the run: nothing published' % out_root)
    os.rename(pending, out_root)                                             # the whole run appears at once
    _fsync_dir(os.path.dirname(os.path.abspath(out_root)))
    os.rename(os.path.join(out_root, staged), os.path.join(out_root, '%s.json' % name))   # the terminal commit
    _fsync_dir(out_root)
    return m


def abort(pending, out_root, error):
    if not os.path.isdir(pending):
        return None
    failed = '%s.failed_%s' % (out_root, _stamp())
    try:
        write_json_atomic(os.path.join(pending, 'FAILED.json'), {'schema': SCHEMA, 'status': 'FAILED', 'error': str(error)[:4000],
                                                                 'failed_utc': utc_now()})
    finally:
        os.rename(pending, failed)
    return failed


# ---------------------------------------------------------------- admission and reading
def _load(root, name, prefix, days, block_hash, changed='RUN_CHANGED_AFTER_COMMIT', coins=None):
    """the manifest, every committed byte and name of the checked days rechecked (no decode) -> (manifest, checked part dirs, days)"""
    p = os.path.join(root, '%s.json' % name)
    if not os.path.isdir(root) or not os.path.isfile(p):
        raise RunRefused('RUN_NOT_PUBLISHED', '%s has no %s.json (no run, an interrupted run, a staging folder or an older version): refused'
                         % (root, name))
    try:
        with open(p, 'rb') as f:
            raw = f.read()
        m = json.loads(raw)
    except (OSError, ValueError) as e:
        raise RunRefused(changed, '%s: unreadable manifest: %s' % (p, e))
    if not isinstance(m, dict) or m.get('schema') != SCHEMA or m.get('status') != 'COMPLETE' or m.get('exit_status') != 0:
        raise RunRefused('RUN_INCOMPLETE', '%s: schema %r status %r: refused' % (p, m.get('schema') if isinstance(m, dict) else None,
                                                                                 m.get('status') if isinstance(m, dict) else None))
    if RC in m or RC_SEAL in m:
        if m.get(RC_SEAL) != seal_of(m, RC_SEAL) or not isinstance(m.get(RC), dict):
            raise RunRefused(changed, '%s: the manifest does not match its seal (edited after the commit)' % p)
    pds_all = _part_dirs(m.get('parts') or {})
    rc = m.get(RC) or {}
    cov = rc.get('coverage')
    if days is None:
        want = None; pds = pds_all
    else:
        want = sorted({str(d) for d in days})
        if cov and cov.get('first') is not None:
            out = [d for d in want if not (cov['first'] <= d <= cov['last'])]
        else:
            have = set(cov['days']) if cov else {_day(pd) for pd in pds_all}
            out = [d for d in want if d not in have]
        if out:
            raise RunRefused('RANGE_NOT_COVERED', '%s: days %s are outside the run\'s committed coverage %s' % (
                root, out[:4], ('%s..%s' % (cov['first'], cov['last'])) if cov and cov.get('first') else 'days with parts'))
        pds = [pd for pd in pds_all if _day(pd) in set(want)]
    if coins is not None:                                                    # the requested selection must be covered (finish line)
        have = (cov or {}).get('coins')
        miss = sorted({str(c) for c in coins} - set(have or ()))
        if have is None or miss:
            raise RunRefused('SELECTION_NOT_COVERED', '%s: coins %s are not in the run\'s committed coverage%s' % (
                root, miss[:5], '' if have is not None else ' (the run records no coin coverage)'))
    bad = []
    for rel, sha in sorted((m.get('parts') or {}).items()):
        if want is not None and rel.startswith('day=') and rel.split('/')[0][4:] not in set(want):
            continue                                                         # another day: never opened (N4, C-R2-02)
        q = os.path.join(root, rel)
        if not os.path.isfile(q):
            bad.append('%s missing' % rel)
        elif sha16_file(q) != sha:
            bad.append('%s is %s, committed %s' % (rel, sha16_file(q), sha))
    for rel, sha in sorted(list((m.get('files') or {}).items()) + list((rc.get('root_files') or {}).items())):
        q = os.path.join(root, rel)
        if not os.path.isfile(q) or sha16_file(q) != sha:
            bad.append('%s changed or missing' % rel)
    dig = m.get('part_digests') or {}
    for pd in pds:
        x = dig.get(pd)
        if not isinstance(x, dict) or 'digest' not in x:
            continue                                                         # verify_committed refuses parts without a digest
        if not os.path.isdir(os.path.join(root, pd)):
            bad.append('%s missing' % pd); continue
        d, n = part_digest(root, pd, x.get('kind', ALL_FILES))
        if d != x['digest']:
            bad.append('%s: its files changed since the commit (%d files now, %d committed)' % (pd, n, x.get('files', -1)))
        elif block_hash and x.get('kind', ALL_FILES) == DIGEST_KIND:
            try:
                _hash_blocks(root, pd, changed)
            except RunRefused as e:
                bad.append(str(e))
    if prefix:
        named = set(pds_all)
        dds = ['day=%s' % d for d in want] if want is not None else sorted(x for x in os.listdir(root) if x.startswith('day='))
        for d in dds:
            if not os.path.isdir(os.path.join(root, d)):
                continue
            for prt in os.listdir(os.path.join(root, d)):
                if prt.startswith(prefix) and '.tmp_' not in prt and '.aside_' not in prt and '%s/%s' % (d, prt) not in named:
                    bad.append('%s/%s is not in the manifest' % (d, prt))
    if bad:
        raise RunRefused(changed, '%s: %s: refused' % (p, '; '.join(bad[:5])))
    m['_manifest_sha16'] = hashlib.sha256(raw).hexdigest()[:16]
    return m, pds, want


def load_complete(root, name, prefix=None, days=None, coins=None):
    """the COMPLETE manifest of a published run, every committed file rechecked (bytes; V3 parts: every block against its index sha16)
    -> manifest; RunRefused otherwise. No decode and no input recheck: consumers use verify_committed."""
    return _load(root, name, prefix, days, block_hash=True, coins=coins)[0]


def verify_committed(root, name, prefix=None, code_dir=None, purpose='research', days=None, inputs=True, coins=None):
    """THE check before any value is returned, VERIFY PASS printed, UP TO DATE reported or a committed run resumed: _load (seal, coverage,
    root files, indexes, part digests, unnamed parts, on the checked days only), every payload block of the checked parts through lab3,
    and (inputs=True: everything frozen; 'data': files and sources only; False: skip) the input identity frozen at commit
    -> the manifest with m['_verified']"""
    m, pds, want = _load(root, name, prefix, days, block_hash=False, coins=coins)
    dig = m.get('part_digests') or {}
    if pds and not all(isinstance(dig.get(pd), dict) and 'digest' in dig[pd] for pd in pds):
        raise RunRefused('CORRUPT_RUN', '%s: parts without a committed fingerprint (a run committed before verify_committed): rebuild' % root)
    blocks = sum(_decode_part(root, pd, code_dir, purpose) for pd in pds)
    if inputs and (m.get(RC) or {}).get('inputs'):
        recheck_inputs(m[RC]['inputs'], strict_code=False, what=('files', 'sources') if inputs == 'data' else ('files', 'sources', 'code'))
    m['_verified'] = {'parts': len(pds), 'files': sum(dig[pd].get('files', 0) for pd in pds), 'payload_blocks': blocks,
                      'days': want, 'manifest_sha16': m.pop('_manifest_sha16')}
    return m


def recheck_after_read(root, name, m, prefix=None, days=None):
    """after the values were read and before they are returned: the manifest file has the bytes that were verified, and every committed
    byte and name of the checked days is unchanged (no second decode: the blocks read were checked by lab3 against the index, whose bytes
    are rechecked here) -> RUN_CHANGED_DURING_READ"""
    v = m.get('_verified') or {}
    days = v.get('days') if days is None else days
    try:
        m2, _, _ = _load(root, name, prefix, days, block_hash=False, changed='RUN_CHANGED_DURING_READ')
    except RunRefused as e:
        raise RunRefused('RUN_CHANGED_DURING_READ', str(e)) if e.code != 'RUN_CHANGED_DURING_READ' else e
    if v.get('manifest_sha16') and m2['_manifest_sha16'] != v['manifest_sha16']:
        raise RunRefused('RUN_CHANGED_DURING_READ', '%s/%s.json: the manifest changed while the run was read' % (root, name))


def read_verified(root, name, read, prefix=None, code_dir=None, purpose='research', days=None, inputs=True, coins=None):
    """verify_committed -> values = read(manifest) -> recheck_after_read -> (manifest, values)"""
    m = verify_committed(root, name, prefix, code_dir, purpose, days, inputs, coins)
    values = read(m)
    recheck_after_read(root, name, m, prefix, days)
    return m, values


if __name__ == '__main__':
    a = sys.argv[1:]; cd = None; dy = None; inp = True
    if '--code-dir' in a:
        i = a.index('--code-dir'); cd = a[i + 1]; a = a[:i] + a[i + 2:]
    if '--days' in a:
        i = a.index('--days'); dy = [x for x in a[i + 1].split(',') if x]; a = a[:i] + a[i + 2:]
    if '--no-inputs' in a:
        a.remove('--no-inputs'); inp = False
    if len(a) not in (3, 4) or a[0] != 'verify':
        raise SystemExit(__doc__)
    try:
        m = verify_committed(a[1], a[2], a[3] if len(a) == 4 else None, cd, days=dy, inputs=inp)
    except (RunRefused, PermissionError) as e:
        print('REFUSED %s' % e, file=sys.stderr); sys.exit(2)
    v = m['_verified']
    print('VERIFY PASS %s %s run %s: %d parts, %d files, %d payload blocks' % (a[1], a[2], m.get('run_id'), v['parts'], v['files'], v['payload_blocks']))
