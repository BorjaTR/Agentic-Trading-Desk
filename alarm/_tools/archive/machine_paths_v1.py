#!/usr/bin/env python3
"""machine_paths_v1.py (SCOUT 30 Oct 2026; the owner 22:21 Berlin: "Let's make sure everything can run from the release folder.
Everything needs to be clean first"). The STATIC proof of a clean part: no machine path written into its code.

A machine path is a string that names one machine's folders: /Users/, /Volumes/, /home/, /mnt/, /sessions/, /private/var/,
~/ and $HOME (the release's own `/tmp` use is not one). Where it sits decides its kind:
  CODE  Python: in a string or a line of code (not a docstring, not a comment); shell (.sh): a line that is not a comment;
        a job template (.job.sh.txt): every line, its header too (the runner reads it); JSON: any value (pins name files);
  TEXT  a Python docstring or comment, a shell comment, a document or table (.md, .tsv, .txt, .csv, .env, ...), a release record
        (RELEASE_*.json: what a past release ran, never read to run).
A part is clean when no CODE row is left (settings keys and arguments carry every path instead).

  python3 -B _tools/machine_paths_v1.py <part folder> [--all] [--tsv OUT]
    <part folder>  e.g. Alarm/Agentic: the files its MANIFEST.tsv lists (repo_path); --all: every file under the folder
    --tsv OUT      also write the rows (file, line, path, kind) to OUT (refused if OUT exists)
Exit 0: no CODE row; 1: CODE rows (listed); 2: refused (no MANIFEST.tsv without --all, OUT exists, a listed file missing).
Reads files only; writes nothing but OUT."""
import ast, csv, io, json, os, re, sys, tokenize

PAT = re.compile(r'(?:/Users/|/Volumes/|/home/|/mnt/|/sessions/|/private/var/|~/|\$HOME\b|\$\{HOME\})[^\s\'"`,;:)\]}]*')
TEXT_SUFFIX = ('.md', '.tsv', '.txt', '.csv', '.env', '.rst', '.html', '.log')
BINARY_SUFFIX = ('.gz', '.npz', '.npy', '.parquet', '.pyc', '.png', '.jpg', '.pdf', '.zip', '.so', '.dylib')


class Refused(Exception):
    pass


def hits(text):
    return [m.group(0) for m in PAT.finditer(text)]


def py_rows(src):
    """(line, path, kind) for a Python source: docstrings and comments are TEXT, every other string or code line CODE"""
    out = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [(i, p, 'CODE') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]
    doc = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            b = node.body[0]
            if isinstance(b, ast.Expr) and isinstance(getattr(b, 'value', None), ast.Constant) and isinstance(b.value.value, str):
                doc.update(range(b.lineno, (b.end_lineno or b.lineno) + 1))
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return [(i, p, 'CODE') for i, l in enumerate(src.split('\n'), 1) for p in hits(l)]
    for tok in toks:
        kind = 'TEXT' if tok.type == tokenize.COMMENT or (tok.type == tokenize.STRING and tok.start[0] in doc) else 'CODE'
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


def scan(part, every=False):
    """-> (rows (file, line, path, kind) for the part's files, in file and line order; the number of files scanned)"""
    rows, fs = [], files_of(part, every)
    for rel in fs:
        rows += [(rel, i, p, k) for i, p, k in file_rows(os.path.join(part, rel))]
    return rows, len(fs)


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
        rows, nf = scan(part, every)
    except Refused as e:
        print('REFUSED %s' % e); return 2
    code = [r for r in rows if r[3] == 'CODE']
    for r in code:
        print('CODE\t%s:%d\t%s' % (r[0], r[1], r[2]))
    if out:
        with open(out, 'x') as f:
            f.write('file\tline\tpath\tkind\n' + ''.join('%s\t%d\t%s\t%s\n' % r for r in rows))
    print('%s: %d files, CODE %d, TEXT %d -> %s' % (os.path.basename(part), nf, len(code), len(rows) - len(code), 'CLEAN' if not code else 'NOT CLEAN'))
    return 1 if code else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
