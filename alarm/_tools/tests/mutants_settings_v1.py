"""mutants_settings_v1.py (SCOUT, 30 Oct 2026): planted bugs in settings_v1.py; each must make test_settings_v1.py fail.
  python3 -B _tools/tests/mutants_settings_v1.py      (from Alarm)"""
import os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ALARM = os.path.dirname(TOOLS)
M = [
 ("            if m.group(1) in rows:\n", "            if False:\n"),
 ("    if miss:\n", "    if False:\n"),
 ("    if extra:\n", "    if False:\n"),
 ("        if v and (v != v.strip() or not os.path.isabs(v)):", "        if v and not os.path.isabs(v.strip()):"),
 ("        if v and inside(v, ALARM):", "        if False:"),
 ("    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)", "    return path == root or path.startswith(root)"),
 ("    return 3 if any(r[1] != 'OK' for r in rows) else 0", "    return 0"),
 ("'EMPTY' if not s[k] else ('OK' if os.path.exists(s[k]) else 'MISSING')", "'EMPTY' if not s[k] else 'OK'"),
 ("    if not s[key]:\n", "    if False:\n"),
 ("LINE_RE = re.compile(r'([A-Z][A-Z0-9_]*)=(.*)')", "LINE_RE = re.compile(r'(?:export )?([A-Za-z][A-Za-z0-9_]*)=(.*)')"),
 ("    names = list(s) if not names else names", "    names = list(s)"),
 ("            if not line.strip() or line.lstrip().startswith('#'):", "            if not line.strip():"),
 ("        out[k] = os.path.normpath(v) if v else ''", "        out[k] = v"),
 ("        print(__doc__)\n        return 2", "        print(__doc__)\n        return 0"),
 ("        print('REFUSED %s' % e, file=sys.stderr)\n        return 2", "        print('REFUSED %s' % e, file=sys.stderr)\n        return 1"),
 ("    bad = [k for k in names if k not in s]", "    bad = []"),
 ("            if not m:\n", "            if False:\n"),
]
src = open(os.path.join(TOOLS, 'settings_v1.py')).read(); alive = []
for old, new in M:
    assert src.count(old) == 1, ('NOT ONCE', src.count(old), old)
    d = tempfile.mkdtemp(prefix='settings_v1_mut_')
    try:
        a = os.path.join(d, 'Alarm'); os.makedirs(os.path.join(a, '_tools', 'tests')); os.makedirs(os.path.join(a, 'settings'))
        for fn in ('SETTINGS_EXAMPLE.env', 'SETTINGS_LOCAL.env'):
            shutil.copy(os.path.join(ALARM, 'settings', fn), os.path.join(a, 'settings'))
        shutil.copy(os.path.join(HERE, 'test_settings_v1.py'), os.path.join(a, '_tools', 'tests'))
        open(os.path.join(a, '_tools', 'settings_v1.py'), 'w').write(src.replace(old, new))
        r = subprocess.run([sys.executable, '-B', os.path.join(a, '_tools', 'tests', 'test_settings_v1.py')], capture_output=True, text=True, timeout=120)
        print('%-8s %s' % ('KILLED' if r.returncode else 'ALIVE', old.strip()[:90].replace('\n', ' ')))
        if not r.returncode:
            alive.append(old)
    finally:
        shutil.rmtree(d)
print('mutants %d, killed %d, alive %d' % (len(M), len(M) - len(alive), len(alive)))
sys.exit(1 if alive else 0)
