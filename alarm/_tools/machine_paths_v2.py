#!/usr/bin/env python3
"""machine_paths_v2.py (SCOUT 30 Oct 2026; the owner 22:21 Berlin: "Let's make sure everything can run from the release folder.
Everything needs to be clean first"). The STATIC proof of a clean part: no machine path written into its code. v1 plus two kinds,
so test data and released files no longer read as code that calls a machine's folders:
  MARKED  a Python line whose own comment says `machine-path-ok: <reason>` (a comment, never text inside a string; the reason
          is required): for test data and the scanner's own pattern. Shell, job templates and JSON cannot be marked.
  KNOWN   a CODE row listed in the part's MACHINE_PATHS_KNOWN.tsv (columns file, line, path, sha16, reason) while the file's
          sha16 (first 16 hex of its sha256) is still the one listed: a released file kept for its callers, that cannot change
          here. Any change to the file makes its rows CODE again. A row that matches nothing is printed as STALE.

A machine path is a string that names one machine's folders: /Users/, /Volumes/, /home/, /mnt/, /sessions/, /private/var/,
~/ and $HOME (the release's own `/tmp` use is not one). Where it sits decides its kind:
  CODE  Python: in a string or a line of code (not a docstring, not a comment); shell (.sh): a line that is not a comment;
        a job template (.job.sh.txt): every line, its header too (the runner reads it); JSON: any value (pins name files);
  TEXT  a Python docstring or comment, a shell comment, a document or table (.md, .tsv, .txt, .csv, .env, ...), a metric card
        (.yaml, .yml: notes for people on where a source lives; where_v3 and metric_brief_v2 read the cards as text and open no path
        written in them; the RUN proof catches any tool that would), a release record (RELEASE_*.json: what a past release ran).
Past editions live in archive/ folders (the owner 30 Oct 23:51-23:54 Berlin: "move the past editions to an Archive folder"): read
only, never run, never called. So:
  ARCHIVE        a machine path in a file inside an archive/ folder: counted, not listed (the --tsv file has them), never CODE;
  CALLS_ARCHIVE  a current file whose code names a file of any archive/ folder of the Alarm folder (its file name in a string, a
                 shell or template line or JSON; for Python also `import <its module>`), unless a current file has the same name:
                 like CODE, it fails the part;
  NAMES_ARCHIVE  the same in a test (a tests/ folder, or a file named test_*, mutants_* or edges_*): listed, does not fail (a
                 test may compare with a past edition when it is present; the archive's files are not, so such a test skips).
                 An import is never optional: `import <an archived module>` is CALLS_ARCHIVE in a test too.
The Alarm folder is the nearest folder above the part (or the part) with _tools/settings_v1.py.
A part is CLEAN when no CODE and no KNOWN row is left (settings keys and arguments carry every path instead); CLEAN EXCEPT KNOWN
when only KNOWN rows are left (each printed with its reason). MARKED and KNOWN rows are always printed, so a reader sees each one.

  python3 -B _tools/machine_paths_v2.py <part folder> [--all] [--tsv OUT]
    <part folder>  e.g. Alarm/Agentic: the files its MANIFEST.tsv lists (repo_path); --all: every file under the folder
    --tsv OUT      also write the rows (file, line, path, kind) to OUT (refused if OUT exists)
Exit 0: no CODE and no CALLS_ARCHIVE row; 1: such rows (listed); 2: refused (no MANIFEST.tsv without --all, OUT exists, a listed file missing, a
MACHINE_PATHS_KNOWN.tsv row with an empty column or a line that is no number).
Reads files only; writes nothing but OUT."""
import ast, csv, hashlib, io, json, os, re, sys, tokenize

PAT = re.compile(r'(?:/Users/|/Volumes/|/home/|/mnt/|/sessions/|/private/var/|~/|\$HOME\b|\$\{HOME\})[^\s\'"`,;:)\]}]*')  # machine-path-ok: the scanner's own pattern
MARK = re.compile(r'machine-path-ok:\s*\S')
KNOWN_FILE = 'MACHINE_PATHS_KNOWN.tsv'
KNOWN_COLS = ('file', 'line', 'path', 'sha16', 'reason')
TEST_PREFIX = ('test_', 'mutants_', 'edges_')
FAIL_KINDS = ('CODE', 'CALLS_ARCHIVE')
TEXT_SUFFIX = ('.md', '.tsv', '.txt', '.csv', '.env', '.rst', '.html', '.log', '.yaml', '.yml')
BINARY_SUFFIX = ('.gz', '.npz', '.npy', '.parquet', '.pyc', '.png', '.jpg', '.pdf', '.zip', '.so', '.dylib')


class Refused(Exception):
    pass


def hits(text):
    return [m.group(0) for m in PAT.finditer(text)]


def doc_lines(tree):
    doc = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            b = node.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, 'value', None), ast.Constant) and isinstance(b.value.value, str):
                doc.update(range(b.lineno, (b.end_lineno or b.lineno) + 1))
    return doc


def py_rows(src):
    """(line, path, kind) for a Python source: docstrings and comments are TEXT, every other string or code line CODE, or MARKED
    when a comment on the string's first or last line says machine-path-ok: <reason>"""
    out = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [(i, p, 'CODE') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]
    doc = doc_lines(tree)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return [(i, p, 'CODE') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]
    marked = {t.start[0] for t in toks if t.type == tokenize.COMMENT and MARK.search(t.string)}
    for tok in toks:
        kind = 'TEXT' if tok.type == tokenize.COMMENT or (tok.type == tokenize.STRING and tok.start[0] in doc) else 'CODE'
        if kind == 'CODE' and (tok.start[0] in marked or tok.end[0] in marked):
            kind = 'MARKED'
        if tok.type in (tokenize.COMMENT, tokenize.STRING) or getattr(tokenize, 'FSTRING_MIDDLE', -1) == tok.type:
            for p in hits(tok.string):
                out.append((tok.start[0], p, kind))
    return out


def sh_rows(src, template):
    out = []
    for i, l in enumerate(src.split('\n'), 1):
        kind = 'CODE' if template or not l.lstrip().startswith('#') else 'TEXT'
        out += [(i, p, kind) for p in hits(l)]
    return out


def json_rows(src):
    out = []
    try:
        json.loads(src)
    except ValueError:
        pass
    for i, l in enumerate(src.split('\n'), 1):
        out += [(i, p, 'CODE') for p in hits(l)]
    return out


def file_rows(path):
    name = os.path.basename(path)
    if name.endswith(BINARY_SUFFIX):
        return []
    with open(path, encoding='utf-8', errors='replace') as f:
        src = f.read()
    if name.endswith('.job.sh.txt'):
        return sh_rows(src, True)
    if name.endswith('.py'):
        return py_rows(src)
    if name.endswith('.sh') or src.startswith('#!/bin/') or src.startswith('#!/usr/bin/env bash'):
        return sh_rows(src, False)
    if name.endswith('.json') and name.startswith('RELEASE_'):
        return [(i, p, 'TEXT') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]   # a release record: what was run, once
    if name.endswith('.json'):
        return json_rows(src)
    if name.endswith(TEXT_SUFFIX) or '.' not in name:
        return [(i, p, 'TEXT') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]
    return [(i, p, 'CODE') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]


def is_archive(rel):
    return 'archive' in rel.replace(os.sep, '/').split('/')[:-1]


def is_test(rel):
    p = rel.replace(os.sep, '/').split('/')
    return 'tests' in p[:-1] or p[-1].startswith(TEST_PREFIX)


def alarm_of(part):
    """the Alarm folder: the nearest folder above the part (or the part) holding _tools/settings_v1.py; else the part"""
    d = part
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            return part
        d = os.path.dirname(d)
    return d


def archive_names(root):
    """the file names inside any archive/ folder under root that no current file under root shares"""
    arch, cur = set(), set()
    for d, ds, fs in os.walk(root):
        ds[:] = [x for x in ds if x not in ('__pycache__', '.git')]
        inside = 'archive' in os.path.relpath(d, root).replace(os.sep, '/').split('/')
        (arch if inside else cur).update(f for f in fs if f != '.DS_Store')
    return arch - cur


def refs_of(path, names):
    """(line, name, how) for each place the file's code names one of names (CODE context as for machine paths: how 'name'; for
    Python also the module of an archived .py in `import`/`from`: how 'import')"""
    if not names:
        return []
    rx = re.compile(r'(?<![\w.-])(%s)(?![\w.-])' % '|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True)))
    mods = {n[:-3] for n in names if n.endswith('.py')}
    name = os.path.basename(path)
    if name.endswith(BINARY_SUFFIX):
        return []
    with open(path, encoding='utf-8', errors='replace') as f:
        src = f.read()
    lines = src.split('\n')
    if name.endswith('.py'):
        try:
            tree = ast.parse(src); toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
        except (SyntaxError, tokenize.TokenError, IndentationError):
            return [(i, m.group(1), 'name') for i, l in enumerate(lines, 1) for m in rx.finditer(l)]
        doc = doc_lines(tree); out = []; prev = ''
        for tok in toks:
            if (tok.type == tokenize.STRING and tok.start[0] not in doc) or getattr(tokenize, 'FSTRING_MIDDLE', -1) == tok.type:
                out += [(tok.start[0], m.group(1), 'name') for m in rx.finditer(tok.string)]
            elif tok.type == tokenize.NAME and tok.string in mods and prev in ('import', 'from', ','):
                out.append((tok.start[0], tok.string + '.py', 'import'))
            if tok.type not in (tokenize.NL, tokenize.COMMENT):
                prev = tok.string
        return out
    if name.endswith('.job.sh.txt') or (name.endswith('.json') and not name.startswith('RELEASE_')):
        return [(i, m.group(1), 'name') for i, l in enumerate(lines, 1) for m in rx.finditer(l)]
    if name.endswith('.sh') or src.startswith('#!/bin/') or src.startswith('#!/usr/bin/env bash'):
        return [(i, m.group(1), 'name') for i, l in enumerate(lines, 1) if not l.lstrip().startswith('#') for m in rx.finditer(l)]
    return []


def files_of(part, every):
    if every:
        out = []
        for d, ds, fs in os.walk(part):
            ds[:] = sorted(x for x in ds if x not in ('__pycache__', '.git'))
            out += [os.path.relpath(os.path.join(d, f), part) for f in sorted(fs) if f != '.DS_Store']
        return out
    m = os.path.join(part, 'MANIFEST.tsv')
    if not os.path.isfile(m):
        raise Refused('NO MANIFEST.tsv in %s (use --all)' % part)
    with open(m) as f:
        rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    out = [r['repo_path'] for r in rows]
    miss = [x for x in out if not os.path.isfile(os.path.join(part, x))]
    if miss:
        raise Refused('LISTED FILES MISSING: %s' % ', '.join(miss[:5]))
    return out


def sha16(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def known_of(part):
    """the part's MACHINE_PATHS_KNOWN.tsv: {(file, line, path): (sha16, reason)}; {} when the part has none"""
    p = os.path.join(part, KNOWN_FILE)
    if not os.path.isfile(p):
        return {}
    with open(p) as f:
        rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    out = {}
    for r in rows:
        if any(not (r.get(c) or '').strip() for c in KNOWN_COLS) or not r['line'].strip().isdigit():
            raise Refused('%s ROW INCOMPLETE: %s' % (KNOWN_FILE, '\t'.join(str(r.get(c)) for c in KNOWN_COLS)))
        out[(r['file'].strip(), int(r['line']), r['path'].strip())] = (r['sha16'].strip(), r['reason'].strip())
    return out


def scan(part, every=False):
    """-> (rows (file, line, path, kind) for the part's files, in file and line order; the number of files scanned; the known
    table's rows that matched nothing). A CODE row the known table lists, for the file's current sha16, is KNOWN."""
    rows, fs = [], files_of(part, every)
    known, used, shas = known_of(part), set(), {}
    names = archive_names(alarm_of(part))
    for rel in fs:
        if is_archive(rel):
            rows += [(rel, i, p, 'ARCHIVE') for i, p, k in file_rows(os.path.join(part, rel)) if k != 'TEXT']
            continue
        rows += [(rel, i, n, 'NAMES_ARCHIVE' if is_test(rel) and how == 'name' else 'CALLS_ARCHIVE')
                 for i, n, how in refs_of(os.path.join(part, rel), names)]
        for i, p, k in file_rows(os.path.join(part, rel)):
            key = (rel, i, p)
            if k == 'CODE' and key in known:
                if rel not in shas:
                    shas[rel] = sha16(os.path.join(part, rel))
                if shas[rel] == known[key][0]:
                    k = 'KNOWN'; used.add(key)
            rows.append((rel, i, p, k))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows, len(fs), sorted(set(known) - used)


def main(a):
    every = '--all' in a; a = [x for x in a if x != '--all']; out = None
    if '--tsv' in a:
        i = a.index('--tsv'); out = a[i + 1]; a = a[:i] + a[i + 2:]
    if len(a) != 1:
        print(__doc__.strip().split('\n\n')[-1]); return 2
    part = os.path.abspath(a[0])
    try:
        if out and os.path.exists(out):
            raise Refused('OUT EXISTS %s' % out)
        rows, nf, stale = scan(part, every)
        known = known_of(part)
    except Refused as e:
        print('REFUSED %s' % e); return 2
    n = {k: sum(1 for r in rows if r[3] == k) for k in ('CODE', 'CALLS_ARCHIVE', 'KNOWN', 'MARKED', 'NAMES_ARCHIVE', 'ARCHIVE', 'TEXT')}
    for r in rows:
        if r[3] == 'KNOWN':
            print('KNOWN\t%s:%d\t%s\t(%s)' % (r[0], r[1], r[2], known[(r[0], r[1], r[2])][1]))
        elif r[3] in ('CODE', 'CALLS_ARCHIVE', 'MARKED', 'NAMES_ARCHIVE'):
            print('%s\t%s:%d\t%s' % (r[3], r[0], r[1], r[2]))
    for f, i, p in stale:
        print('STALE\t%s:%d\t%s\t(a %s row that matches nothing)' % (f, i, p, KNOWN_FILE))
    if out:
        with open(out, 'x') as f:
            f.write('file\tline\tpath\tkind\n' + ''.join('%s\t%d\t%s\t%s\n' % r for r in rows))
    bad = n['CODE'] + n['CALLS_ARCHIVE']
    verdict = 'NOT CLEAN' if bad else ('CLEAN EXCEPT KNOWN' if n['KNOWN'] else 'CLEAN')
    print('%s: %d files, CODE %d, CALLS_ARCHIVE %d, KNOWN %d, MARKED %d, NAMES_ARCHIVE %d, ARCHIVE %d, TEXT %d -> %s'
          % (os.path.basename(part), nf, n['CODE'], n['CALLS_ARCHIVE'], n['KNOWN'], n['MARKED'], n['NAMES_ARCHIVE'], n['ARCHIVE'], n['TEXT'],
             verdict))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
