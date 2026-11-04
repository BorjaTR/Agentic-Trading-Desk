"""mutants_machine_paths_v3.py (SCOUT 31 Oct 2026): planted bugs in _tools/machine_paths_v3.py; every one must make
_tools/tests/test_machine_paths_v3.py fail. The unchanged copy must pass first. mutants_machine_paths_v2.py 4a053295cb4cc530's bugs (less its
token import bug: v3 reads imports from the syntax tree) plus 7 for v3's two changes.
  python3 -B _tools/tests/mutants_machine_paths_v3.py"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
M = [
 ("kind = 'TEXT' if tok.type == tokenize.COMMENT or", "kind = 'TEXT' if False or"),                        # comments counted as code
 ("(tok.type == tokenize.STRING and tok.start[0] in doc)", "(False)"),                                       # docstrings counted as code
 ("        return sh_rows(src, True)\n    if name.endswith('.py'):", "        return sh_rows(src, False)\n    if name.endswith('.py'):"),  # template header as text
 ("        out += [(i, p, 'CODE') for p in hits(l)]\n    return out\n\n\ndef file_rows", "        out += [(i, p, 'TEXT') for p in hits(l)]\n    return out\n\n\ndef file_rows"),  # JSON as text
 ("PAT = re.compile(r'(?:/Users/|", "PAT = re.compile(r'(?:/tmp/|/Users/|"),                                 # /tmp counted; machine-path-ok: a planted bug's text
 ("    if every:\n", "    if False:\n"),                                                                         # --all ignored
 ("    return 1 if bad else 0\n", "    return 0\n"),                                                            # exit 0 when not clean
 ("    if miss:\n", "    if False:\n"),                                                                           # a missing file not refused
 ("|~/|", "|"),                                                                                                   # ~/ not seen; machine-path-ok: a planted bug's text
 ("|/Volumes/|", "|"),                                                                                            # /Volumes/ not seen; machine-path-ok: a planted bug's text
 ("        kind = 'CODE' if template or not l.lstrip().startswith('#') else 'TEXT'", "        kind = 'CODE' if template else 'TEXT'"),  # shell commands as text
 ("        if out and os.path.exists(out):\n", "        if False:\n"),                                         # OUT overwritten
 ("    if name.endswith('.json') and name.startswith('RELEASE_'):", "    if False:"),                              # a release record as code
 ("            kind = 'MARKED'\n", "            kind = 'CODE'\n"),                                                  # marks ignored
 ("MARK = re.compile(r'machine-path-ok:\\s*\\S')", "MARK = re.compile(r'machine-path-ok:')"),                         # no reason needed
 ("t.type == tokenize.COMMENT and MARK.search(t.string)", "MARK.search(t.string)"),                              # a marker inside a string
 ("(tok.start[0] in marked or tok.end[0] in marked)", "(tok.start[0] in marked)"),                               # a string's last line ignored
 ("(tok.start[0] in marked or tok.end[0] in marked)", "marked"),                                                 # one mark marks the file
 ("                if shas[rel] == known[key][0]:", "                if True:"),                                    # a changed file stays KNOWN
 ("out[(r['file'].strip(), int(r['line']), r['path'].strip())]", "out[(r['file'].strip(), 1, r['path'].strip())]"),  # the line not read
 ("        if any(not (r.get(c) or '').strip() for c in KNOWN_COLS) or not r['line'].strip().isdigit():", "        if False:"),  # no refusal
 ("('CLEAN EXCEPT KNOWN' if n['KNOWN'] else 'CLEAN')", "'CLEAN'"),                                               # KNOWN hidden in CLEAN
 ("        elif r[3] in ('CODE', 'CALLS_ARCHIVE', 'MARKED', 'NAMES_ARCHIVE'):", "        elif r[3] in ('CODE', 'CALLS_ARCHIVE', 'NAMES_ARCHIVE'):"),                                # MARKED not printed
 ("            print('KNOWN\\t%s:%d\\t%s\\t(%s)'", "            print('\\t%s:%d\\t%s\\t(%s)'"),                     # KNOWN not printed
 ("    for f, i, p in stale:\n", "    for f, i, p in []:\n"),                                                       # STALE not printed
 ("    return 'archive' in rel.replace(os.sep, '/').split('/')[:-1]", "    return False"),                       # archive files read as current
 ("    return 'tests' in p[:-1] or p[-1].startswith(TEST_PREFIX)", "    return False"),                          # tests fail the part
 ("    return arch - cur\n", "    return arch\n"),                                                                # a name shared with a current file
 ("(?<![\\w.-])(%s)(?![\\w.-])", "(%s)"),                                                                         # names inside longer names
 ("(tok.type == tokenize.STRING and tok.start[0] not in doc)", "(tok.type == tokenize.STRING)"),                 # docstrings as references
 ("    names = archive_names(alarm_of(part))", "    names = archive_names(part)"),                                # other parts' archives missed
 ("    bad = n['CODE'] + n['CALLS_ARCHIVE']", "    bad = n['CODE']"),                                             # archive calls pass
 ("    if name.endswith('.job.sh.txt') or (name.endswith('.json') and not name.startswith('RELEASE_')):", "    if False:"),  # templates, JSON
 ("'NAMES_ARCHIVE' if is_test(rel) and how == 'name' else 'CALLS_ARCHIVE'", "'NAMES_ARCHIVE' if is_test(rel) else 'CALLS_ARCHIVE'"),  # a test's import passes
 ("'.log', '.yaml', '.yml')", "'.log')"),                                                                          # cards as code
 ("TEXT_SUFFIX = ('.md',", "TEXT_SUFFIX = ('.cfg', '.md',"),                                                       # an unknown ending as text
 ("            rows += [(rel, i, p, 'ARCHIVE') for i, p, k in file_rows(os.path.join(part, rel)) if k != 'TEXT']\n            continue\n",
  "            rows += [(rel, i, p, 'ARCHIVE') for i, p, k in file_rows(os.path.join(part, rel)) if k != 'TEXT']\n"),   # archive files also scanned as current
 ("            if isinstance(node, (ast.Import, ast.ImportFrom)):", "            if isinstance(node, ast.Import):"),        # v3: from-imports missed
 ("(node.module or '').split('.') + [a.name for a in node.names]", "[a.name for a in node.names]"),                  # v3: from pkg.old import x missed
 ("[x for a in node.names for x in a.name.split('.')]", "[a.name for a in node.names]"),                              # v3: import pkg.old missed
 ("out += [(node.lineno, m + '.py', 'import')", "out += [(node.end_lineno, m + '.py', 'import')"),                     # v3: an import's last line
 ("            if (rel, i, n) in known:", "            if False:"),                                                       # v3: archive names never KNOWN
 ("                if shas[rel] == known[(rel, i, n)][0]:", "                if True:"),                                     # v3: a changed file stays KNOWN
 ("k = 'KNOWN'; used.add((rel, i, n))", "k = 'KNOWN'"),                                                                  # v3: a used row reported STALE
]


def run(src):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'tests'))
        with open(os.path.join(d, 'machine_paths_v3.py'), 'w') as f:
            f.write(src)
        shutil.copy(os.path.join(HERE, 'test_machine_paths_v3.py'), os.path.join(d, 'tests'))
        return subprocess.run([sys.executable, '-B', os.path.join(d, 'tests', 'test_machine_paths_v3.py')], capture_output=True).returncode


def main():
    src = open(os.path.join(TOOLS, 'machine_paths_v3.py')).read()
    for old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', old)
    if run(src):
        print('THE UNCHANGED CODE FAILS ITS TESTS'); return 2
    alive = [i for i, (o, n) in enumerate(M, 1) if not run(src.replace(o, n))]
    for i, (o, n) in enumerate(M, 1):
        print('%2d %s %s' % (i, 'ALIVE ' if i in alive else 'KILLED', o.strip().split('\n')[0][:90]))
    print('mutants %d, killed %d, alive %d' % (len(M), len(M) - len(alive), len(alive)))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main())
