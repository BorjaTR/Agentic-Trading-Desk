"""mutants_machine_paths_v1.py (SCOUT 30 Oct 2026): planted bugs in _tools/machine_paths_v1.py; every one must make
_tools/tests/test_machine_paths_v1.py fail. The unchanged copy must pass first.
  python3 -B _tools/tests/mutants_machine_paths_v1.py"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
M = [
 ("kind = 'TEXT' if tok.type == tokenize.COMMENT or", "kind = 'TEXT' if False or"),                        # comments counted as code
 ("(tok.type == tokenize.STRING and tok.start[0] in doc)", "(False)"),                                       # docstrings counted as code
 ("        return sh_rows(src, True)\n    if name.endswith('.py'):", "        return sh_rows(src, False)\n    if name.endswith('.py'):"),  # template header as text
 ("        out += [(i, p, 'CODE') for p in hits(l)]\n    return out\n\n\ndef file_rows", "        out += [(i, p, 'TEXT') for p in hits(l)]\n    return out\n\n\ndef file_rows"),  # JSON as text
 ("PAT = re.compile(r'(?:/Users/|", "PAT = re.compile(r'(?:/tmp/|/Users/|"),                                 # /tmp counted
 ("    if every:\n", "    if False:\n"),                                                                         # --all ignored
 ("    return 1 if code else 0\n", "    return 0\n"),                                                           # exit 0 when not clean
 ("    if miss:\n", "    if False:\n"),                                                                           # a missing file not refused
 ("|~/|", "|"),                                                                                                   # ~/ not seen
 ("|/Volumes/|", "|"),                                                                                            # /Volumes/ not seen
 ("        kind = 'CODE' if template or not l.lstrip().startswith('#') else 'TEXT'", "        kind = 'CODE' if template else 'TEXT'"),  # shell commands as text
 ("        if out and os.path.exists(out):\n", "        if False:\n"),                                         # OUT overwritten
 ("    if name.endswith('.json') and name.startswith('RELEASE_'):", "    if False:"),                              # a release record as code
]


def run(src):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'tests'))
        with open(os.path.join(d, 'machine_paths_v1.py'), 'w') as f:
            f.write(src)
        shutil.copy(os.path.join(HERE, 'test_machine_paths_v1.py'), os.path.join(d, 'tests'))
        return subprocess.run([sys.executable, '-B', os.path.join(d, 'tests', 'test_machine_paths_v1.py')], capture_output=True).returncode


def main():
    src = open(os.path.join(TOOLS, 'machine_paths_v1.py')).read()
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
