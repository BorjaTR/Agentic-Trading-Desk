"""mutants_fair_v2.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in fair_v2's own code (each period's z line at the five calls,
ZMIN, the z_min column, the EITHER row; the owner 30 Oct 2026 19:21 Berlin); every one must make tests/test_fair_v2.py fail. fair_v1's
code is unchanged (mutants_fair_v1.py). The unchanged copy must pass first; 3 at once.
  TMPDIR=/tmp python3 -B mutants_fair_v2.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

M = [
 ('{p: F.verdict8(L, bz, ms, counts[p], z_min=ZMIN[p]) for p, ms in PERIODS2}',
  '{p: F.verdict8(L, bz, ms, counts[p]) for p, ms in PERIODS2}'),
 ("netA, netR), ms, counts[p], 'SIDE', ZMIN[p])}",
  "netA, netR), ms, counts[p], 'SIDE')}"),
 ("net, netR), ms, counts[p], 'SIDE', ZMIN[p])}",
  "net, netR), ms, counts[p], 'SIDE')}"),
 ('{p: F.verdict8(L2, bz2, ms, c2[p], z_min=ZMIN[p]) for p, ms in PERIODS2}',
  '{p: F.verdict8(L2, bz2, ms, c2[p]) for p, ms in PERIODS2}'),
 ("ms, c2[p], 'SIZE', ZMIN[p])}",
  "ms, c2[p], 'SIZE')}"),
 ('ZMIN = {p: z for p, ms, z in F.PERIODS9}',
  'ZMIN = {p: 2.0 for p, ms, z in F.PERIODS9}'),
 ("'fires': fires, 'z_min': d.get('z_min', np.nan)})",
  "'fires': fires, 'z_min': np.nan})"),
 ("both = sum(any(ok(v, 'Sep-Dec') and ok(v, 'Jan-Apr') for v in vs) for vs in runs.values())",
  "both = sum(any(ok(v, 'Sep-Dec') for v in vs) and any(ok(v, 'Jan-Apr') for v in vs) for vs in runs.values())"),
 ("        if kind in ('real', 'null'):\n            for key, v in runs.items():",
  '        if True:\n            for key, v in runs.items():'),
 ("    out.sort(key=lambda x: (x['code'] != 'ALL', x['code'], KINDS[x['kind']], x['plant'], x['bar']))\n",
  ''),
 ("'rate_both': both / n, 'median_z_SepDec': np.nan,",
  "'rate_both': sd / n, 'median_z_SepDec': np.nan,"),
 ("F.fnum(x[c]) if c in ('z', 'excess_pts', 'z_min') else str(x[c])",
  "F.fnum(x[c]) if c in ('z', 'excess_pts') else str(x[c])"),
]
NAME, TEST = 'fair_v2.py', 'test_fair_v2.py'
EXTRA_SRC, EXTRA_TESTS = ('fl_read_v9.py', 'fl_read_v8.py'), ('test_fl_read_v9.py',)


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
    print('%s %s, tests/%s %s, planted bugs %d' % (NAME, s16(os.path.join(here, NAME)), TEST, s16(os.path.join(here, 'tests', TEST)), len(M)))
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
