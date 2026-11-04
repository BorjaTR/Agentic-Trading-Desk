"""mutants_fl_read_v10.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in edition 10's own code (Look takes the fires' wave
ids; review B 30 Oct 2026), then edition 9's 23 (mutants_fl_read_v9.py, unchanged texts) on edition 10; every one must make
tests/test_fl_read_v10.py fail. The unchanged copy must pass first; 3 at once.
  TMPDIR=/tmp python3 -B mutants_fl_read_v10.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mutants_fl_read_v9 as P9   # noqa: E402  edition 9's planted bugs, one list

OWN = [
 ("        self.wid = M.wave_ids(A['t']) if wid is None else np.asarray(wid, int)     # edition 10: the fires' wave ids may be given\n",
  "        self.wid = M.wave_ids(A['t'])\n"),
 ("        if self.wid.shape != (n,) or (n and int(self.wid.min()) < 0):\n",
  "        if len(self.wid) < n:\n"),
 ("        if self.wid.shape != (n,) or (n and int(self.wid.min()) < 0):\n",
  "        if self.wid.shape != (n,):\n"),
 ("            raise M.Refused('WAVE IDS NOT ALIGNED TO THE FIRES')\n",
  "            pass\n"),
]
M = OWN + list(P9.M)
NAME, TEST = 'fl_read_v10.py', 'test_fl_read_v10.py'
EXTRA_SRC, EXTRA_TESTS = ('fl_read_v8.py',), ()


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def run_one(src, here, md, old=None, new=None):
    """the tests on a temp copy with one planted text (none: the unchanged code) -> the tests' exit code"""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'fl', 'tests')); os.makedirs(os.path.join(d, 'money_direction'))
        shutil.copy(md, os.path.join(d, 'money_direction'))
        with open(os.path.join(d, 'fl', NAME), 'w') as f:
            f.write(src if old is None else src.replace(old, new))
        for x in EXTRA_SRC:
            shutil.copy(os.path.join(here, x), os.path.join(d, 'fl'))
        for x in (TEST,) + EXTRA_TESTS:
            shutil.copy(os.path.join(here, 'tests', x), os.path.join(d, 'fl', 'tests'))
        r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(d, 'fl', 'tests', TEST)], capture_output=True, text=True)
        return r.returncode


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(here, NAME)).read()
    for old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', src.count(old), old)
    print('%s %s, tests/%s %s, planted bugs %d (own %d, edition 9 %d from mutants_fl_read_v9.py %s)' % (
        NAME, s16(os.path.join(here, NAME)), TEST, s16(os.path.join(here, 'tests', TEST)), len(M), len(OWN), len(P9.M), s16(P9.__file__)))
    if '--check' in argv:
        return 0
    md = os.path.join(os.path.dirname(here), 'money_direction', 'md_v1.py')
    if run_one(src, here, md):
        print('THE UNCHANGED CODE FAILS ITS TESTS: no verdict'); return 2
    with ThreadPoolExecutor(3) as ex:
        rcs = list(ex.map(lambda on: run_one(src, here, md, on[0], on[1]), M))
    alive = []
    for i, ((old, new), rc) in enumerate(zip(M, rcs), 1):
        print('%2d %-6s %s' % (i, 'KILLED' if rc else 'ALIVE', old.strip()[:110].replace('\n', ' | ')), flush=True)
        if not rc:
            alive.append(i)
    print('mutants %d, killed %d, alive %d%s' % (len(M), len(M) - len(alive), len(alive), (': ' + ','.join(map(str, alive))) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
