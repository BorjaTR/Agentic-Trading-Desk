"""mutants_fl_read_v9.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in edition 9's own code (the z line in bar8 and verdict8,
CONFIRM_Z_MIN, PERIODS9, RULE_9, the one writer of FL_RULE8 and FL_RULE9; the owner 30 Oct 2026 19:21 Berlin); every one must make
tests/test_fl_read_v9.py fail. Edition 8's code is unchanged (mutants_fl_read_v8.py). The unchanged copy must pass first; 3 at once.
  TMPDIR=/tmp python3 -B mutants_fl_read_v9.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

M = [
 ("S['z'] >= z_min - TOL",
  "S['z'] >= NET_Z_MIN - TOL"),
 ("'fail': why, 'z_min': z_min, 'months_holding': nh,",
  "'fail': why, 'z_min': NET_Z_MIN, 'months_holding': nh,"),
 ("counts, 'SIZE', z_min) if bz is not None",
  "counts, 'SIZE') if bz is not None"),
 ("months, counts, 'SIDE', z_min)}",
  "months, counts, 'SIDE')}"),
 ('CONFIRM_Z_MIN = 1.0',
  'CONFIRM_Z_MIN = 2.0'),
 ("PERIODS9 = (('Sep-Dec', M.DESIGN, NET_Z_MIN),",
  "PERIODS9 = (('Sep-Dec', M.DESIGN, CONFIRM_Z_MIN),"),
 ('    R9 = {p: verdict8(L, bz, ms, z_min=zm) for p, ms, zm in PERIODS9}',
  '    R9 = {p: verdict8(L, bz, ms) for p, ms, zm in PERIODS9}'),
 ("    R9['RULE_9'] = overall8(R9['Sep-Dec'], R9['Jan-Apr'])",
  "    R9['RULE_9'] = overall8(R8['Sep-Dec'], R8['Jan-Apr'])"),
 ("(('rule_8', 'rule_7'), ('rule_9', 'rule_8')):",
  "(('rule_8', 'rule_7'), ('rule_9', 'rule_7')):"),
 ("q = res[key]; vals = [aid, r['code'], r['V'], r['lean'], q[lab]]",
  "q = res['rule_8']; vals = [aid, r['code'], r['V'], r['lean'], q['RULE_8']]"),
 ("'rule_8': R8, 'rule_9': R9,",
  "'rule_8': R8, 'rule_9': dict(R9, **{'Jan-Apr': R8['Jan-Apr']}),"),
 ('def bar8(L, X, months, counts, label, z_min=NET_Z_MIN):',
  'def bar8(L, X, months, counts, label, z_min=CONFIRM_Z_MIN):'),
 ('net_R=None, z_min=NET_Z_MIN):',
  'net_R=None, z_min=CONFIRM_Z_MIN):'),
 # review A (30 Oct 2026): Jan-Apr keeps every rule but the z line; the exact limits; a FOLLOW lean
 ("    if nh < MONTHS_MIN or not (np.isfinite(S['z']) and S['z'] >= z_min - TOL):",
  "    if (nh < MONTHS_MIN and z_min >= NET_Z_MIN) or not (np.isfinite(S['z']) and S['z'] >= z_min - TOL):"),
 ("        thin = t['waves'] < BUSY_WAVES_MIN",
  "        thin = t['waves'] < BUSY_WAVES_MIN and z_min >= NET_Z_MIN"),
 ("(label, nh, fnum(S['z'])))\n    if not (np.isfinite(Sc['mean_pts']) and Sc['mean_pts'] > PTS_TOL):",
  "(label, nh, fnum(S['z'])))\n    if z_min >= NET_Z_MIN and not (np.isfinite(Sc['mean_pts']) and Sc['mean_pts'] > PTS_TOL):"),
 ("    if not (np.isfinite(Sd['mean_pts']) and Sd['mean_pts'] > PTS_TOL):\n        why.append('DAYS (without the best 5: %s pts)' % fnum(Sd['mean_pts']))\n    if min(counts",
  "    if z_min >= NET_Z_MIN and not (np.isfinite(Sd['mean_pts']) and Sd['mean_pts'] > PTS_TOL):\n        why.append('DAYS (without the best 5: %s pts)' % fnum(Sd['mean_pts']))\n    if min(counts"),
 ('    if min(counts[m] for m in months) < WAVES_MIN:',
  '    if z_min >= NET_Z_MIN and min(counts[m] for m in months) < WAVES_MIN:'),
 ("S['z'] >= z_min - TOL",
  "S['z'] > z_min + 1e-9"),
 ("        thin = t['waves'] < BUSY_WAVES_MIN",
  "        thin = t['waves'] <= BUSY_WAVES_MIN"),
 ('    if min(counts[m] for m in months) < WAVES_MIN:',
  '    if min(counts[m] for m in months) <= WAVES_MIN:'),
 ("    ob = 'OBH4_60M__%s' % L.lean; xr = L.net(L.R, ob) if net_R",
  "    ob = 'OBH4_60M__FADE'; xr = L.net(L.R, ob) if net_R"),
 ("    off = L.series(60, L.lean)['A']['offer']\n",
  "    off = L.series(60, 'FADE')['A']['offer']\n"),
]
NAME, TEST = 'fl_read_v9.py', 'test_fl_read_v9.py'
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
