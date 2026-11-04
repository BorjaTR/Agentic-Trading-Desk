"""mutants_fl_read_v11.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in edition 11's own code (the grade's 30 min waves from
labcore; owner 30 Oct 2026 21:11 Berlin), then edition 10's (mutants_fl_read_v10.py: its 4, the first adapted to edition 11's line, and
edition 9's 23); every one must make tests/test_fl_read_v11.py fail. The unchanged copy must pass first; 3 at once.
  TMPDIR=/tmp python3 -B mutants_fl_read_v11.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py, ../labcore)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mutants_fl_read_v10 as P10   # noqa: E402  edition 10's and edition 9's planted bugs, one list each

LINE = "        self.wid = WV.waves(A['t'], GRADE_WAVE_S) if wid is None else np.asarray(wid, int)   # edition 11: the grade's waves; edition 10: ids given\n"
OWN = [
 ("GRADE_WAVE_S = 1800        # edition 11", "GRADE_WAVE_S = 900         # edition 11"),
 (LINE, "        self.wid = M.wave_ids(A['t']) if wid is None else np.asarray(wid, int)\n"),        # md_v1's 15 min waves again
 (LINE, "        self.wid = WV.waves(A['t'], GRADE_WAVE_S)\n"),                                     # edition 10's #1 on edition 11: ids ignored
]
M = OWN + list(P10.OWN[1:]) + list(P10.P9.M)
NAME, TEST = 'fl_read_v11.py', 'test_fl_read_v11.py'
EXTRA_SRC, EXTRA_TESTS = ('fl_read_v8.py',), ()


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def run_one(src, here, md, old=None, new=None):
    """the tests on a temp copy with one planted text (none: the unchanged code) -> the tests' exit code"""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'fl', 'tests')); os.makedirs(os.path.join(d, 'money_direction')); os.makedirs(os.path.join(d, 'labcore'))
        shutil.copy(md, os.path.join(d, 'money_direction'))
        for x in ('__init__.py', 'waves.py'):
            shutil.copy(os.path.join(os.path.dirname(here), 'labcore', x), os.path.join(d, 'labcore'))
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
    print('%s %s, tests/%s %s, planted bugs %d (own %d, edition 10 %d, edition 9 %d; labcore/waves.py %s)' % (
        NAME, s16(os.path.join(here, NAME)), TEST, s16(os.path.join(here, 'tests', TEST)), len(M), len(OWN), len(P10.OWN) - 1, len(P10.P9.M),
        s16(os.path.join(os.path.dirname(here), 'labcore', 'waves.py'))))
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
