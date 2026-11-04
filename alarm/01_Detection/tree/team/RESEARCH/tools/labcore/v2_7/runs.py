"""labcore.v2_7.runs (labcore V2_7 CANDIDATE, sub-package labcore/v2_7 so the released V2_6 tree and its tests stay unchanged; ctxprof_shared for STRATEGY/LEAD, 25 Oct 2026; A46R REL-01 items K2, K3, C6). NOT RELEASED:
it enters labcore only through a LAB1 release cycle (RELEASE_labcore_V2_7_CANDIDATE.json). A library: it reads and checks run folders a
caller names; it writes only inside the run folder the caller staged (the plan, the manifest) and moves aside, never deletes. It is the
ONE module of the candidate that acts on files (the run-publication protocol); labcore's 'no data writes' contract (README, test L12)
needs LAB1's architecture review for it before promotion: it never writes a value store, only a caller's run folder.

ONE CHECKED WHOLE RUN for tools that write lab3 parts (Profile EPG.<S>, Context CTX.<S>.<LEVEL>, ...). The publication primitives are
NOT copied: stage / commit / abort / load_complete / write_json_atomic / RunRefused are IMPORTED from decisions_fixer's candidate
team/RESEARCH/tools/event_decisions/run_manifest_candidate.py (its owner keeps it; LAB1 moves it into labcore in one step later), and
verify_committed is used when that file provides it (LEAD note 12:2xZ).
What this module adds, for any lab3-part tool:
  check_stage(root, expect, frozen, lab_root)  after every worker exited 0: every expected day-part exists whole (index.json), holds the
        expected coins and the expected row count in every code, one seal per part kind, every fixed source pin (code, lists, settings,
        catalog) the same in every part and equal to the frozen pin, every lab source index the same in every part and unchanged on disk
        since it was read; no partial write (.tmp_), no aside, no unexpected part -> {parts, files, observed, seals, pins}; RunRefused
        (code) otherwise. Nothing is counted from log lines.
  plan_identity(plan)                           sha16 of the run plan (no out_root, no time): the identity a resume and an UP TO DATE
        rerun must match.
  find_resumable(out_root, plan_sha16)          the newest kept attempt (<out_root>.pending_* or .failed_*) of the SAME plan whose owner
        process AND workers (<out_root>.logs/<run id>/WORKERS.json) are gone; None if there is none; RunRefused RUN_ACTIVE otherwise.
  adopt_for_resume(old, out_root, expect, frozen, aside_dir)  renames that attempt to a new staging folder owned by this process, keeps
        every part that passes the part check, moves partial writes, asides and failing parts to aside_dir (kept, never deleted)
        -> (stage, {(day, part) kept}).
  replay_diff(a, b)                             two committed runs of the same plan: every file byte-equal except the named telemetry
        (TELEMETRY: index.json built_utc; RUN_MANIFEST.json committed_utc, run_id, telemetry; of its parts and part_digests, the
        hashes of index.json files are telemetry-derived: their keys are compared) -> [differences]; [] = identical.
  adopt(root, prefix)                           what a consumer calls before reading a run: the COMPLETE manifest with every committed
        file rechecked (load_complete, then verify_committed when available); RunRefused otherwise. Consumers adopt only committed runs.
Times: the run manifest's committed_utc and its 'telemetry' block are telemetry, never part of a result."""
import hashlib, importlib.util, json, os, sys

FORENSICS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', '..', '..'))
RM_PATH = os.path.join(FORENSICS, 'team', 'RESEARCH', 'tools', 'event_decisions', 'run_manifest_candidate.py')
MANIFEST = 'RUN_MANIFEST'
PLAN = 'RUN_PLAN.json'
WORKERS = 'WORKERS.json'                       # <out_root>.logs/<run id>/WORKERS.json: the pids of an attempt's workers (resume safety)
TELEMETRY = {'index.json': ('built_utc',), MANIFEST + '.json': ('committed_utc', 'run_id', 'telemetry')}
# hashes OF a file that holds telemetry (index.json holds built_utc): their keys are compared, their values are telemetry-derived
TELEMETRY_DERIVED = {MANIFEST + '.json': ('parts', 'part_digests')}


def _load_rm():
    """decisions_fixer's run_manifest_candidate, imported (one module object per process, whoever imported it first)"""
    m = sys.modules.get('run_manifest_candidate')
    if m is not None and os.path.realpath(getattr(m, '__file__', '')) == os.path.realpath(RM_PATH):
        return m
    spec = importlib.util.spec_from_file_location('run_manifest_candidate', RM_PATH)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    sys.modules.setdefault('run_manifest_candidate', m)
    return m


RM = _load_rm()
RunRefused = RM.RunRefused
stage = RM.stage
commit = RM.commit
abort = RM.abort
load_complete = RM.load_complete
write_json_atomic = RM.write_json_atomic
utc_now = RM.utc_now
verify_committed = getattr(RM, 'verify_committed', None)


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def sha16_bytes(b):
    return hashlib.sha256(b).hexdigest()[:16]


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def plan_identity(plan):
    """sha16 of the plan's canonical JSON; the plan never holds out_root or a clock time"""
    if 'out_root' in plan:
        raise ValueError('a run plan holds no out_root (it is the identity of the run, wherever it is published)')
    return sha16_bytes(canonical(plan).encode())


def _load_list(p):
    """lab3's id list file (one JSON text a line)"""
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def part_problems(ix, exp):
    """what is wrong with one written part against its expectation {'coins': [...], 'rows': n}; [] = fine"""
    bad = []
    if sorted(ix.get('coins') or []) != sorted(exp['coins']):
        bad.append('coins %s, the plan expects %s' % (sorted(ix.get('coins') or [])[:6], sorted(exp['coins'])[:6]))
    rd = ix.get('readings') or {}
    if not rd:
        bad.append('no reading')
    for code, r in sorted(rd.items()):
        shape = r.get('shape') or [None]
        if r.get('kind') == 'ROWS' and shape[0] != exp['rows']:
            bad.append('%s holds %s rows, the plan expects %d' % (code, shape[0], exp['rows'])); break
    return bad


def _scan(root, prefixes):
    """{(day, part): index path} of the run's parts, and the problems of the folder (partial writes, asides, unexpected entries)"""
    found, junk = {}, []
    for d in sorted(x for x in os.listdir(root) if x.startswith('day=')):
        dd = os.path.join(root, d)
        if not os.path.isdir(dd):
            continue
        for p in sorted(os.listdir(dd)):
            if p.startswith('.lock_'):
                continue                                                      # lab3's per-(day, part) writer lock: never a part
            if not any(p.startswith(x) for x in prefixes):
                junk.append(('UNEXPECTED_PART', '%s/%s' % (d, p))); continue
            if '.tmp_' in p:
                junk.append(('PARTIAL_WRITE', '%s/%s' % (d, p))); continue
            if '.aside_' in p:
                junk.append(('ASIDE_IN_RUN', '%s/%s' % (d, p))); continue
            ixp = os.path.join(dd, p, 'index.json')
            if not os.path.isfile(ixp):
                junk.append(('PARTIAL_WRITE', '%s/%s has no index.json' % (d, p))); continue
            found[(d[4:], p)] = ixp
    return found, junk


def check_stage(root, expect, frozen, lab_root=None, prefixes=None):
    """the whole-run check after every worker exited 0. expect: {(day, part): {'coins', 'rows'}}; frozen: {source key: sha16} pins the
    run froze before any worker started (code files, lists, settings); lab_root: the store the 'lab:day=<D>/<part>' pins name (rehashed).
    -> dict(parts {rel index path: sha16}, observed {...}, seals {part kind: sha16}, pins {...}); RunRefused(code) on any problem."""
    prefixes = tuple(prefixes or sorted({p for _, p in expect}))
    found, junk = _scan(root, prefixes) if prefixes else ({}, [])
    if junk:
        raise RunRefused(junk[0][0], '%s: %s' % (root, '; '.join('%s %s' % j for j in junk[:5])))
    missing = sorted(set(expect) - set(found)); extra = sorted(set(found) - set(expect))
    if missing:
        raise RunRefused('PART_MISSING', '%d expected day-parts are not written, e.g. %s' % (len(missing), missing[:5]))
    if extra:
        raise RunRefused('UNEXPECTED_PART', '%d day-parts the plan does not name, e.g. %s' % (len(extra), extra[:5]))
    parts, seals, fixed, lab, reasons, rows = {}, {}, {}, {}, {}, {}
    for (day, part), ixp in sorted(found.items()):
        with open(ixp, 'rb') as f:
            raw = f.read()
        try:
            ix = json.loads(raw)
        except ValueError as e:
            raise RunRefused('PART_UNREADABLE', '%s: %s' % (ixp, e))
        bad = part_problems(ix, expect[(day, part)])
        if bad:
            raise RunRefused('PART_CONTENT', 'day=%s/%s: %s' % (day, part, '; '.join(bad)))
        kind = part                                                           # a part kind: the part name (one per day)
        s = ix.get('seal')
        seals.setdefault(kind, set()).add(s)
        for k, v in (ix.get('sources') or {}).items():
            (lab if k.startswith('lab:') else fixed).setdefault(k, set()).add(v)
        rp = os.path.join(os.path.dirname(ixp), 'REASONS.txt')
        if os.path.isfile(rp):
            reasons.setdefault(kind, set()).update(x for x in _load_list(rp) if x)
        rows[kind] = rows.get(kind, 0) + expect[(day, part)]['rows']
        parts['day=%s/%s/index.json' % (day, part)] = sha16_bytes(raw)
    for kind, ss in seals.items():
        if len(ss) != 1:
            raise RunRefused('SEALS_DISAGREE', '%s: %d different seals in one run' % (kind, len(ss)))
    for k, vs in sorted(fixed.items()):
        if len(vs) != 1:
            raise RunRefused('SOURCE_PINS_DISAGREE', '%s: %s in one run' % (k, sorted(vs)))
        if k in frozen and frozen[k] not in vs:
            raise RunRefused('SOURCE_PIN_NOT_FROZEN', '%s: parts name %s, the run froze %s' % (k, sorted(vs), frozen[k]))
    absent = sorted(k for k in frozen if k not in fixed)
    if found and absent:
        raise RunRefused('FROZEN_PIN_NOT_IN_PARTS', 'no part names %s' % absent[:5])
    changed = []
    for k, vs in sorted(lab.items()):
        if len(vs) != 1:
            raise RunRefused('SOURCE_PINS_DISAGREE', '%s: %s in one run' % (k, sorted(vs)))
        if lab_root is not None:
            p = os.path.join(lab_root, k[4:], 'index.json')
            now = sha16_file(p) if os.path.isfile(p) else None
            if now not in vs:
                changed.append('%s now %s, read as %s' % (k, now, sorted(vs)[0]))
    if changed:
        raise RunRefused('SOURCE_CHANGED_DURING_RUN', '%d lab indexes changed since they were read: %s' % (len(changed), changed[:5]))
    labpins = {k: next(iter(v)) for k, v in lab.items()}
    return dict(parts=parts,
                seals={k: sha16_bytes((next(iter(v)) or '').encode()) for k, v in sorted(seals.items())},
                pins=dict(fixed={k: next(iter(v)) for k, v in sorted(fixed.items())}, lab_indexes=len(labpins),
                          lab_indexes_sha16=sha16_bytes(canonical(labpins).encode()), lab_rehashed=lab_root is not None),
                observed=dict(day_parts=len(found), days=len({d for d, _ in found}), rows=rows,
                              reasons={k: sorted(v) for k, v in sorted(reasons.items())}))


def top_files(root, skip=()):
    """{relative path: sha16} of EVERY file of the run folder outside its day parts (catalogs, FORMAT.json, the plan, _selection/, a
    tool's side folders such as receipts), the manifest itself excepted: every published byte is pinned (checklist K4)"""
    out = {}
    for dp, dns, fs in os.walk(root):
        rel = os.path.relpath(dp, root)
        if rel == '.':
            dns[:] = [d for d in dns if not d.startswith('day=')]
        for f in fs:
            r = f if rel == '.' else os.path.join(rel, f)
            if r in skip or f.startswith(MANIFEST + '.json') or '.tmp' in f or f.startswith('.lock_'):
                continue
            out[r] = sha16_file(os.path.join(dp, f))
    return dict(sorted(out.items()))


def _pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def find_resumable(out_root, plan_sha16):
    """the newest kept attempt of the same plan (a staging folder whose process is gone, or a failed run), or None"""
    parent = os.path.dirname(os.path.abspath(out_root)); base = os.path.basename(os.path.abspath(out_root)); got = []
    for f in os.listdir(parent):
        for tag in ('.pending_', '.failed_'):
            if f.startswith(base + tag):
                p = os.path.join(parent, f); pp = os.path.join(p, PLAN)
                if not os.path.isfile(pp):
                    continue
                try:
                    plan = json.load(open(pp))
                except ValueError:
                    continue
                if plan_identity(plan) != plan_sha16:
                    continue
                if tag == '.pending_':
                    pid = f[len(base + tag):].split('_', 1)[0]
                    if pid.isdigit() and _pid_alive(int(pid)) and int(pid) != os.getpid():
                        raise RunRefused('RUN_ACTIVE', '%s: its process %s is still running: refused (never two writers)' % (p, pid))
                    wk = os.path.join(os.path.abspath(out_root) + '.logs', f[len(base + tag):], WORKERS)
                    live = [w for w in (json.load(open(wk)) if os.path.isfile(wk) else []) if _pid_alive(int(w))]
                    if live:                                              # the parent was killed, its workers still write
                        raise RunRefused('RUN_ACTIVE', '%s: worker processes %s of that attempt still run: refused (never two writers)'
                                         % (p, live[:5]))
                got.append((os.path.getmtime(pp), p))
    return sorted(got)[-1][1] if got else None


def adopt_for_resume(old, out_root, expect, frozen, aside_dir):
    """take over a kept attempt: rename it to a new staging folder of this process, keep the parts that pass, move the rest aside"""
    new = RM.stage(out_root)                                               # a fresh, empty name owned by this process ...
    os.rmdir(new)                                                          # ... (empty: created a moment ago by stage)
    os.rename(old, new)
    os.makedirs(aside_dir, exist_ok=True); kept = set(); moved = []
    if os.path.exists(os.path.join(new, 'FAILED.json')):
        os.rename(os.path.join(new, 'FAILED.json'), os.path.join(aside_dir, 'FAILED.json'))
    prefixes = tuple(sorted({p for _, p in expect}))
    for d in sorted(x for x in os.listdir(new) if x.startswith('day=')):
        dd = os.path.join(new, d)
        for p in sorted(os.listdir(dd)):
            if p.startswith('.lock_'):
                continue
            src = os.path.join(dd, p); key = (d[4:], p)
            ok = key in expect and '.tmp_' not in p and '.aside_' not in p and os.path.isfile(os.path.join(src, 'index.json'))
            if ok:
                try:
                    ix = json.load(open(os.path.join(src, 'index.json')))
                except ValueError:
                    ix = None
                ok = ix is not None and not part_problems(ix, expect[key]) and all(
                    (ix.get('sources') or {}).get(k, v) == v for k, v in frozen.items())
            if ok:
                kept.add(key)
            elif any(p.startswith(x) for x in prefixes) or '.tmp_' in p or '.aside_' in p:
                dst = os.path.join(aside_dir, '%s__%s' % (d, p)); os.rename(src, dst); moved.append(dst)
    return new, kept, moved


def _strip(rel, raw):
    name = os.path.basename(rel)
    if name in TELEMETRY:
        x = json.loads(raw)
        for k in TELEMETRY[name]:
            x.pop(k, None)
        for k in TELEMETRY_DERIVED.get(name, ()):
            if isinstance(x.get(k), dict):
                x[k] = sorted(x[k])
        return canonical(x).encode()
    return raw


def replay_diff(a, b):
    """every file of two run folders compared byte for byte, the named TELEMETRY fields excepted -> [differences]"""
    def files(r):
        out = {}
        for dp, _, fs in os.walk(r):
            for f in fs:
                if f.startswith('.lock_'):
                    continue
                p = os.path.join(dp, f); out[os.path.relpath(p, r)] = p
        return out
    fa, fb = files(a), files(b); diff = []
    for rel in sorted(set(fa) | set(fb)):
        if rel not in fa or rel not in fb:
            diff.append('%s only in %s' % (rel, 'b' if rel not in fa else 'a')); continue
        xa, xb = open(fa[rel], 'rb').read(), open(fb[rel], 'rb').read()
        if xa != xb and _strip(rel, xa) != _strip(rel, xb):
            diff.append('%s differs' % rel)
    return diff


def adopt(root, prefix=None, code_dir=None):
    """the consumer's door: a run is read only when its COMPLETE manifest checks: run_manifest_candidate.verify_committed (status,
    committed files, part digests, no unnamed part of the prefix, every payload block through lab3) -> the manifest; RunRefused otherwise.
    Without verify_committed (an older run_manifest_candidate) load_complete only."""
    if verify_committed is None:
        return load_complete(root, MANIFEST, prefix=prefix)
    return verify_committed(root, MANIFEST, prefix, code_dir)
