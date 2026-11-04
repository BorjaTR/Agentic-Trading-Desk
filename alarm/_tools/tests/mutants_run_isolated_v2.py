"""mutants_run_isolated_v2.py (SCOUT 30 Oct 2026): planted bugs in _tools/run_isolated_v2.py; every one must make
_tools/tests/test_run_isolated_v2.py fail. The unchanged copy must pass first.
  python3 -B _tools/tests/mutants_run_isolated_v2.py"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
M = [
 ("CODE_SUFFIX = ('.py', '.pyc',", "CODE_SUFFIX = ('.pyc',"),                                                  # dev .py read as data
 (", '.job.sh.txt')", ")"),                                                                                     # templates read as data
 ("        if under(p, data) and not p.endswith(CODE_SUFFIX):", "        if under(p, data):"),                  # code under a key passes
 ("    return any(p == r or p.startswith(r + os.sep) for r in roots)", "    return any(p.startswith(r) for r in roots)"),  # prefix match
 ("        if not under(p, forbid) or under(p, interp):", "        if not under(p, forbid):"),                    # interpreter files counted
 ("    if outside or bad or arch:", "    if bad or arch:"),                                                                     # imports not judged
 ("    return code\n", "    return 0\n"),                                                                      # the script's exit lost
 ("    if not a or settings is None:", "    if not a:"),                                                     # no settings accepted
 ("    if not script.startswith(ALARM + os.sep):", "    if False:"),                                           # a script outside runs
 ("        return 3\n", "        return 0\n"),                                                                  # failure exits 0
 ("    forbid = forbid or fb ", "    forbid = forbid or [] "),                                                    # the settings' FORBID ignored
 ("    if not forbid:\n", "    if False:\n"),                                                                       # no forbidden folder: not refused
 ("(s.get('FORBID') or '').split(':') if x]", "[s.get('FORBID') or ''] if x]"),                                  # FORBID not split on ':'
 ("    return p.startswith(ALARM + os.sep) and 'archive' in", "    return 'archive' in"),                       # data's archive/ refused
 ("    if outside or bad or arch:", "    if outside or bad:"),                                                       # past editions run
 ("    arch = sorted(p for p in set(opened) | mods if in_archive(p))", "    arch = sorted(p for p in set(opened) if in_archive(p))"),  # imports missed
 (", 'BOARD', 'FEED_GATE')", ", 'BOARD')"),                                                                     # the gate file flagged
]


def run(src):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'tests'))
        with open(os.path.join(d, 'run_isolated_v2.py'), 'w') as f:
            f.write(src)
        shutil.copy(os.path.join(TOOLS, 'settings_v1.py'), d)
        shutil.copy(os.path.join(HERE, 'test_run_isolated_v2.py'), os.path.join(d, 'tests'))
        return subprocess.run([sys.executable, '-B', os.path.join(d, 'tests', 'test_run_isolated_v2.py')], capture_output=True).returncode


def main():
    src = open(os.path.join(TOOLS, 'run_isolated_v2.py')).read()
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
