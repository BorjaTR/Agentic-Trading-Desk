"""mutants_setup_python_v1.py (SCOUT helper K14, 31 Oct 2026; TEST, NOT REVIEWED): planted bugs in _tools/setup_python_v1.sh; each must make
test_setup_python_v1.py fail. Each runs in a new temporary Alarm folder (the mutated script, the test, settings/PYTHON_PACKAGES.txt);
first the unchanged script must pass there.
  python3 -B _tools/tests/mutants_setup_python_v1.py      (from Alarm; no data, no network; never deletes: its folders stay under TMPDIR)"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ALARM = os.path.dirname(TOOLS)
M = [
    ('      vcmp "$ver" 3.10\n', '      vcmp "$ver" 3.9\n'),                                                   # an old python3 passes
    ("    '==') [ \"$VCMP\" = 0 ] ;;", "    '==') [ \"$VCMP\" = 0 ] || [ \"$VCMP\" = 1 ] ;;"),                    # == read as >=
    ("    '>=') [ \"$VCMP\" = 0 ] || [ \"$VCMP\" = 1 ] ;;", "    '>=') [ \"$VCMP\" = 0 ] || [ \"$VCMP\" = -1 ] ;;"),  # >= turned round
    ('    if [ $((10#$a)) -lt $((10#$b)) ]; then VCMP=-1; return 0; fi\n    if [ $((10#$a)) -gt $((10#$b)) ]; then VCMP=1; return 0; fi',
     '    if [[ $a < $b ]]; then VCMP=-1; return 0; fi\n    if [[ $a > $b ]]; then VCMP=1; return 0; fi'),           # numbers compared as text
    ('  if [ "$p1" -lt "$p2" ]; then VCMP=-1; elif [ "$p1" -gt "$p2" ]; then VCMP=1',
     '  if false; then VCMP=-1; elif false; then VCMP=1'),                                                     # rc, dev and post ignored
    ('  v=${v%%+*}; v=${v#v}', '  v=${v#v}'),                                                                 # a local label (+x) kept
    ('  while [ -n "$r1" ] || [ -n "$r2" ]; do', '  while [ -n "$r1" ] && [ -n "$r2" ]; do'),                 # 2.2 the same as 2.2.6
    ('    line=${line%%#*}\n', ''),                                                                           # comments read as packages
    ("(==|>=)[[:space:]]*([^[:space:]]+)$'", "(==|>=|~=|<=|<|>)[[:space:]]*([^[:space:]]+)$'"),               # other operators taken
    ('  case "$DEST/" in "$ALARM"/*) refuse', '  case "$DEST/" in "$ALARM"/nothing/*) refuse'),               # inside the Alarm folder taken
    ('            if [ -d "$cur" ]; then cur=$(CDPATH= cd -P "$cur" 2>/dev/null && pwd -P) || return 1; fi ;;', '            : ;;'),  # links not resolved
    ('      ..)   cur=${cur%/*}; [ -n "$cur" ] || cur=/ ;;', '      ..)   ;;'),                                  # .. ignored
    ('    [ -d "$DEST" ] || refuse "NOT A FOLDER $DEST"', '    true || refuse "NOT A FOLDER $DEST"'),            # a file taken for a folder
    ('    is_empty_dir "$DEST" || refuse', '    true || refuse'),                                             # a full folder taken
    ('  for f in "$1"/* "$1"/.[!.]* "$1"/..?*; do', '  for f in "$1"/*; do'),                                 # dot names not seen
    ('PIN_SHA256=cba3455e18516fbe8668cff2820c9b6a53447c552d612443c2b2fb60d390a908',
     'PIN_SHA256=cba3455e18516fbe8668cff2820c9b6a53447c552d612443c2b2fb60d390a909'),                         # one sha256 wrong
    ('    Darwin/arm64)              PLATFORM=aarch64-apple-darwin ;;', '    Darwin/arm64)              PLATFORM=x86_64-apple-darwin ;;'),  # Intel build on Apple silicon
    ('    Linux/aarch64|Linux/arm64) PLATFORM', '    Linux/aarch64) PLATFORM'),                               # Linux arm64 unknown
    ('  [ "$CHECK_BAD" -eq 0 ] && exit 0\n  exit 1', '  exit 0'),                                             # --check always exit 0
    ('  exit 2\n}\nrefuse()', '  exit 1\n}\nrefuse()'),                                                       # usage exit 1
    ('  if [ $DRY -eq 1 ]; then echo "DRY RUN: nothing was changed"; exit 0; fi',
     '  mkdir -p "$DEST"; if [ $DRY -eq 1 ]; then echo "DRY RUN: nothing was changed"; exit 0; fi'),         # --dry makes the folder
    ('  [ "$CHECK_BAD" -eq 0 ] || fail "check:', '  [ "$CHECK_BAD" -eq 0 ] || echo "check:'),                 # PYTHON= after a failed check
    ('-m pip install --disable-pip-version-check -r "$PKGS" < /dev/null',
     '-m pip install --disable-pip-version-check -r "$ALARM/requirements.txt" < /dev/null'),                  # pip given another file
    ('  check_python "$venvpy" "the new venv"', '  check_python "$base" "the new venv"'),                     # the base checked, not the venv
    ('      item UNCHECKED "$spec" "no good python3 to ask"; bad=$((bad+1)); names="$names $spec"',
     '      item UNCHECKED "$spec" "no good python3 to ask"'),                                                # UNCHECKED counted as OK
    ('"$PROBE_IMPORT" "${P_NAME[$i]}" <', '"$PROBE_IMPORT" "$spec" <'),                                       # the probe asked the whole line
    ('      out=$(cd / && "$py" -B -c "$PROBE_IMPORT"', '      out=$("$py" -B -c "$PROBE_IMPORT"'),               # the current folder seen
    ('base_ok() { case "$1" in 3.10|3.10.*|3.11|3.11.*) return 0 ;; esac; return 1; }', 'base_ok() { return 0; }'),  # any PATH python3 a base
    ('  if [ $PY_GIVEN -eq 1 ]; then find_python "$PY_ARG";', '  if false; then find_python "$PY_ARG";'),     # --python ignored
    ('      [ "$SHA" = "$PIN_SHA256" ] || fail "sha256:', '      [ -n "$SHA" ] || fail "sha256:'),             # the sha256 not compared
    ('      sha256_of "$file"\n', '      tar -xzf "$file" -C "$DEST"; sha256_of "$file"\n'),                  # unpacked before the check
    ('      elif [ "$3" = NO ]; then', '      elif [ "$3" = NOPE ]; then'),                                     # a missing package not MISSING
    ('else wget -q -O "$file" "$PIN_URL"; fi', 'else wget -q "$PIN_URL"; fi'),                                # wget writes elsewhere
]


def run(src):
    """the test on a new temporary Alarm folder holding `src` as its setup_python_v1.sh: its exit code"""
    a = os.path.join(tempfile.mkdtemp(prefix='setup_python_v1_mut_'), 'Alarm')
    os.makedirs(os.path.join(a, '_tools', 'tests'))
    os.makedirs(os.path.join(a, 'settings'))
    shutil.copyfile(os.path.join(ALARM, 'settings', 'PYTHON_PACKAGES.txt'), os.path.join(a, 'settings', 'PYTHON_PACKAGES.txt'))
    shutil.copyfile(os.path.join(HERE, 'test_setup_python_v1.py'), os.path.join(a, '_tools', 'tests', 'test_setup_python_v1.py'))
    with open(os.path.join(a, '_tools', 'setup_python_v1.sh'), 'w') as f:
        f.write(src)
    r = subprocess.run([sys.executable, '-B', os.path.join(a, '_tools', 'tests', 'test_setup_python_v1.py')], stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True, timeout=600)
    return r.returncode, r.stdout


with open(os.path.join(TOOLS, 'setup_python_v1.sh')) as f:
    SRC = f.read()
rc, out = run(SRC)
if rc:
    print('THE UNCHANGED SCRIPT FAILS ITS TEST (exit %d): no mutant can be read\n%s' % (rc, out[-2000:]))
    sys.exit(1)
print('unchanged script: its test passes')
alive = []
for old, new in M:
    assert SRC.count(old) == 1, ('NOT ONCE', SRC.count(old), old)
    rc, out = run(SRC.replace(old, new))
    print('%-7s %s' % ('KILLED' if rc else 'ALIVE', old.strip()[:100].replace('\n', ' ')), flush=True)
    if not rc:
        alive.append(old)
print('mutants %d, killed %d, alive %d' % (len(M), len(M) - len(alive), len(alive)))
sys.exit(1 if alive else 0)
