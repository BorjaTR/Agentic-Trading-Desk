"""labcore.release (BUILD2, 23 Oct 2026; OX-SKEPTIC A04-02, STRATEGY-143459): the release identity is checked at run start, from the same
manifest the judges sign (never a parallel list). A manifest pins every file labcore loads or reads (its modules, the tables and policy files
they read, the re-exported readers and what they import) by sha16 relative to the forensics folder, each table's schema by the sha16 of its
header row, and the python and numpy versions. External data (stores, ledgers, settings of a run) is the run's own input manifest, not this.
  check(manifest, root=FORENSICS) -> the manifest; raises ReleaseRefused on a missing file, a sha16 or schema that differs, or another
  python / numpy version, or (STRATEGY-144233) a release it names in 'releases' {manifest path: sha16} whose own file differs or whose
  own check fails (checked recursively; a tool release pins only its OWN files and tables, another tool by its release)
  schema_sha16(path) -> sha16 of the first row that is not a '#' note (the column header); runtime() -> {'python', 'numpy', 'interpreter'}
V2_3 (BUILD1 for LAB1, 23 Oct 2026; LAB1 19:01:05Z design, OX-SKEPTIC FROZEN_1): (1) a TABLE may be pinned by its VALUE columns: a pin
  {schema_sha16, value_columns [names], value_sha16} checks the header and value_sha16(path, value_columns) (those columns of every row, in
  file order) instead of the whole file, so only editor annotations outside the operative semantic fields may change without refusing a run; the release lists
  such edits in its 'text_changes'. Code files stay pinned whole (sha16). (2) declared closure: a ROOT check refuses while a file named in
  any 'unpinned_other_tools' of its graph is pinned nowhere in that graph (a declared dependency is bound or removed, never left floating).
  value_sha16(path, columns) -> sha16 of the named columns of every data row (tab-joined, one row a line); a missing column refuses."""
import hashlib, json, os, sys

import numpy as np

from .ids import sha16_file

FORENSICS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', '..'))


class ReleaseRefused(RuntimeError):
    pass


def schema_sha16(path):
    with open(path) as f:
        for line in f:
            if not line.startswith('#'):
                return hashlib.sha256(line.rstrip('\n').encode()).hexdigest()[:16]
    return hashlib.sha256(b'').hexdigest()[:16]


def value_sha16(path, columns):
    rows = [l.rstrip('\n').split('\t') for l in open(path, encoding='utf-8') if not l.startswith('#')]
    if not rows:
        raise ReleaseRefused('%s: no header: refused' % path)
    hdr = rows[0]; miss = [c for c in columns if c not in hdr]
    if miss or not columns:
        raise ReleaseRefused('%s: value columns %s not in its header: refused' % (path, miss or columns))
    ix = [hdr.index(c) for c in columns]
    text = '\n'.join('\t'.join(r[i] if i < len(r) else '' for i in ix) for r in rows[1:] if any(x for x in r))
    return hashlib.sha256(text.encode()).hexdigest()[:16]


SEMANTIC_COLUMNS = frozenset(('meaning', 'unit_text', 'scope_text', 'use_may',
                              'empty_means', 'never_read_as', 'read_it_as',
                              'read_as', 'use_never', 'empty_when'))           # METRICS_V1's own names (LAB1 20:22:01Z MUST)


def unpinned_semantics(path, columns):
    """Operational interpretation is part of a frozen table's identity.
    Display-only editor notes can remain outside this minimum set.
    """
    with open(path, encoding='utf-8') as stream:
        header = next((line.rstrip('\n').split('\t') for line in stream if not line.startswith('#')), [])
    return sorted((set(header) & SEMANTIC_COLUMNS) - set(columns))


def runtime():
    """the running python, numpy and interpreter path (V2_2, LAB1 17:21:57Z: research = the analyst venv; a manifest without the key is not
    checked on it)"""
    return {'python': sys.version.split()[0], 'numpy': np.__version__, 'interpreter': sys.executable}


def _unbound_closure(manifest, root):
    """Declared executable dependencies must be pinned somewhere in this root graph.
    This is conservative: a narrow approved capability needs a separate verifier.
    It is not discovery of undeclared imports or operative policy dependencies.
    """
    seen, pins, deferred = set(), set(), set()
    def walk(path):
        path = os.path.realpath(path)
        if path in seen:
            return
        seen.add(path)
        with open(path) as stream:
            item = json.load(stream)
        pins.update(item['files'])
        deferred.update(item.get('unpinned_other_tools', {}))
        for child in item.get('releases', {}):
            walk(os.path.join(root, child))
    walk(manifest)
    return sorted(deferred - pins)


def check(manifest, root=FORENSICS, _seen=None):
    man = json.load(open(manifest)); bad = []; seen = set() if _seen is None else _seen
    seen.add(os.path.realpath(manifest))
    for rel, sha in sorted(man.get('releases', {}).items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append('release %s: missing' % rel); continue
        if sha16_file(p) != sha:
            bad.append('release %s: sha16 %s, this release names %s' % (rel, sha16_file(p), sha)); continue
        if os.path.realpath(p) in seen:
            continue
        try:
            check(p, root, seen)
        except ReleaseRefused as e:
            bad.append('release %s: %s' % (rel, e))
    for rel, pin in sorted(man['files'].items()):
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            bad.append('%s: missing' % rel); continue
        if 'value_sha16' in pin:                                              # V2_3: a table by its value columns
            missing_semantics = unpinned_semantics(p, pin.get('value_columns', []))
            if missing_semantics:
                bad.append('%s: operative semantic columns are unpinned: %s' % (rel, missing_semantics))
            if 'schema_sha16' not in pin or not pin.get('value_columns'):
                bad.append('%s: a value pin needs schema_sha16 and value_columns' % rel)
            else:
                try:
                    v = value_sha16(p, pin['value_columns'])
                except ReleaseRefused as e:
                    bad.append(str(e)); v = None
                if v is not None and v != pin['value_sha16']:
                    bad.append('%s: value columns sha16 %s, release pins %s' % (rel, v, pin['value_sha16']))
        elif sha16_file(p) != pin['sha16']:
            bad.append('%s: sha16 %s, release pins %s' % (rel, sha16_file(p), pin['sha16']))
        if 'schema_sha16' in pin and schema_sha16(p) != pin['schema_sha16']:
            bad.append('%s: schema (header) %s, release pins %s' % (rel, schema_sha16(p), pin['schema_sha16']))
    now = runtime()
    for k, v in sorted(man.get('runtime', {}).items()):
        if now.get(k) != v:
            bad.append('%s %s, release pins %s' % (k, now.get(k), v))
    if not bad and _seen is None:
        bad.extend('declared executable dependency unbound: ' + rel for rel in _unbound_closure(manifest, root))
    if bad:
        raise ReleaseRefused('release %s refused (%d): %s' % (man.get('release'), len(bad), '; '.join(bad)))
    return man
