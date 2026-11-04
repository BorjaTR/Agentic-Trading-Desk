"""mutants_fair_v4.py (SCOUT 30 Oct 2026, tools/alarm_first_look): fair_v4 = fair_v3 on edition 11, so its planted bugs are fair_v3's whole
plan (mutants_fair_v3.py: its own, fair_v1's and fair_v2's, adapted and not here as listed there) on fair_v4, and fair_v4's own (the
reader it imports, labcore's name in FAIR_V4.json; review C's 10 on the ladder's reporting, reviews/REVIEW_C_FL10_FAIR3_20261030.md:
the 9 it found alive on fair_v3 and its C11); every one must make tests/test_fair_v4.py fail. The unchanged copy must pass first;
3 at once.
  TMPDIR=/tmp python3 -B mutants_fair_v4.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py, ../labcore)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mutants_fair_v3 as P3   # noqa: E402  fair_v3's plan, one list

OWN = [
 ("import fl_read_v11 as F  # noqa: E402", "import fl_read_v8 as F  # noqa: E402"),
 ("'labcore/waves.py': F.s16(F.WV.__file__),", ""),
 # review C (30 Oct 2026): the 9 planted bugs it found alive on fair_v3 (the same code here) and its C11; tests T17ReviewC, T18ReviewCFiles
 ("float(np.percentile(r, 2.5))", "float(np.percentile(r, 25))"),                                          # C1 the interval's low end at 25 pct
 ("append((x['runs'], x['pass_both']))", "append((x['runs'], x['pass_SepDec']))"),                         # C2 the interval of the Sep-Dec passes
 ("abs(mu) > 3 * sd / math.sqrt(n) + F.TOL", "abs(mu) > 2 * sd / math.sqrt(n) + F.TOL"),                   # C3 LEANS at 2 errors
 ("x['sd_z'] = math.sqrt(float(var.mean()))", "x['sd_z'] = float(np.sqrt(var).mean())"),                   # C4 the sd within: the mean of the sds
 ("'p_z_ge_2': float((z >= 2 - F.TOL).mean())", "'p_z_ge_2': float((z >= 1 - F.TOL).mean())"),            # C5 an alarm's P(z >= 2) at 1
 ("'p_z_ge_2': float((allz >= 2 - F.TOL).mean())", "'p_z_ge_2': float((allz > 2 + F.TOL).mean())"),       # C6 ALL's P(z >= 2) strict
 ("w = np.where(null_p(L) > 0, L.wR, 0.0)", "w = np.where(np.isfinite(L.wR), L.wR, 0.0)"),                 # C7 the manifest share over every moment
 ("mz = float(allz.mean())", "mz = float(np.mean([np.mean(v) for v in codes.values()]))"),                 # C11 the mean of the alarms' means
 ("pre_R=L.preR[keep], wid=np.arange(len(rows)))",
  "pre_R=L.preR[keep] | F.pre_fire_mask(A2, R2, 600), wid=np.arange(len(rows)))"),                         # C16 a 10 min pre-fire cut of its own
 ("x['rate_JanApr_given_SepDec'] = x['pass_both'] / x['pass_SepDec'] if x['pass_SepDec'] else np.nan",
  "x['rate_JanApr_given_SepDec'] = (x['pass_both'] if x['bar'] != 'EITHER' else x['pass_JanApr']) / x['pass_SepDec'] if x['pass_SepDec'] else np.nan"),  # C17
]
NAME, TEST = 'fair_v4.py', 'test_fair_v4.py'
EXTRA_SRC, EXTRA_TESTS = ('fl_read_v11.py', 'fl_read_v8.py'), ('test_fl_read_v11.py',)


def plan(src):
    return [('v4 own %d' % i, o, n) for i, (o, n) in enumerate(OWN, 1)] + [('v3 ' + lab, o, n) for lab, o, n in P3.plan(src)]


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
    here = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(here, NAME)).read(); M = plan(src)
    for lab, old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', lab, src.count(old), old)
    print('%s %s, tests/%s %s, planted bugs %d (own %d; the plan of fair_v3 %d from mutants_fair_v3.py %s)' % (
        NAME, s16(os.path.join(here, NAME)), TEST, s16(os.path.join(here, 'tests', TEST)), len(M), len(OWN), len(M) - len(OWN), s16(P3.__file__)))
    if '--check' in argv:
        return 0
    md = os.path.join(os.path.dirname(here), 'money_direction', 'md_v1.py')
    if run_one(src, here, md):
        print('THE UNCHANGED CODE FAILS ITS TESTS: no verdict'); return 2
    with ThreadPoolExecutor(3) as ex:
        rcs = list(ex.map(lambda m: run_one(src, here, md, m[1], m[2]), M))
    alive = []
    for i, ((lab, old, new), rc) in enumerate(zip(M, rcs), 1):
        print('%2d %-6s %-20s %s' % (i, 'KILLED' if rc else 'ALIVE', lab, old.strip()[:96].replace('\n', ' | ')), flush=True)
        if not rc:
            alive.append(i)
    print('mutants %d, killed %d, alive %d%s' % (len(M), len(M) - len(alive), len(alive), (': ' + ','.join(map(str, alive))) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
