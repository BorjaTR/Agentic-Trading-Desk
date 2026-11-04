"""mutants_fair_v3.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in fair_v3's own code (the null by weight: its
probabilities, draws, waves and reweighted random; no own pre-fire cut; the calibration table; the summary's new columns; the waves
column; review B's two survivors on fair_v2: the made-up alarm's random losing its weights, plants sized by fire), then every planted bug
of fair_v1 and fair_v2 (mutants_fair_v1.py, mutants_fair_v2.py, one list each) on fair_v3: those whose text fair_v3 changed are ADAPTED
here; those on code fair_v3 no longer has are NOT HERE, each with its reason; the script refuses any other text that does not occur once.
Every one must make tests/test_fair_v3.py fail. The unchanged copy must pass first; 3 at once.
  TMPDIR=/tmp python3 -B mutants_fair_v3.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mutants_fair_v1 as P1   # noqa: E402
import mutants_fair_v2 as P2   # noqa: E402

OWN = [
 ("np.minimum(np.where(ok, L.wR, 0.0), PI_MAX)", "np.where(ok, L.wR, 0.0)"),                              # no cap at PI_MAX
 ("    ok = L.useR & ~L.preR & np.isfinite(L.wR) & (L.wR > 0)\n", "    ok = L.useR & np.isfinite(L.wR) & (L.wR > 0)\n"),   # pre-fire drawn
 ("    ok = L.useR & ~L.preR & np.isfinite(L.wR) & (L.wR > 0)\n", "    ok = ~L.preR & np.isfinite(L.wR) & (L.wR > 0)\n"),  # no cost drawn
 ("rng.random(len(L.wR)) < null_p(L)", "rng.random(len(L.wR)) < 2 * null_p(L)"),
 ("v = np.asarray(wR, float) / (1.0 - null_p(L))", "v = np.asarray(wR, float)"),                        # the rest not reweighted
 ("L2 = F.Look(A2, R2, v[keep], costs,", "L2 = F.Look(A2, R2, np.ones(int(keep.sum())), costs,"),         # review B survivor 1
 ("    return float((np.bincount(inv, weights=x[sel]) / nw).mean())\n", "    return float(x[sel].mean())\n"),   # review B survivor 2
 ("pre_R=L.preR[keep], wid=np.arange(len(rows)))", "pre_R=L.preR[keep], wid=None)"),                   # md_v1 waves again
 ("pre_R=L.preR[keep], wid=np.arange(len(rows)))", "pre_R=F.pre_fire_mask(A2, R2) | L.preR[keep], wid=np.arange(len(rows)))"),
 ("rws = null_rows(L, rng_for(s, code, 'null', 0))", "rws = null_rows(L, rng_for(0, code, 'null', 0))"),
 ("'waves': d.get('waves', '')})", "'waves': '')})"),
 ("x['pass_both'] / x['pass_SepDec'] if x['pass_SepDec'] else np.nan", "x['pass_JanApr'] / x['pass_SepDec'] if x['pass_SepDec'] else np.nan"),
 ("if x['code'] == 'ALL' else (np.nan, np.nan)", "if True else (np.nan, np.nan)"),
 ("float(np.percentile(r, 97.5))", "float(np.percentile(r, 75))"),
 ("    r = a[k, 1].sum(1) / np.maximum(a[k, 0].sum(1), 1.0)\n", "    r = (a[k, 1] / np.maximum(a[k, 0], 1.0)).max(1)\n"),
 ("lean = bool(n > 1 and abs(mu) > 3 * sd / math.sqrt(n) + F.TOL)", "lean = bool(n > 1 and abs(mu) > 3 * sd + F.TOL)"),
 ("'p_z_ge_1': float((allz >= 1 - F.TOL).mean())", "'p_z_ge_1': float((allz > 1 + F.TOL).mean())"),
 ("        if len(ok) >= CALIB_MIN_ALARMS:\n", "        if len(ok) >= 2:\n"),
 ("x['spread'] = float(mu.std(ddof=1));", "x['spread'] = float(mu.std());"),
 ("x['noise'] = math.sqrt(float((var / n).mean()))", "x['noise'] = math.sqrt(float(var.mean()))"),
 ("good = (abs(mz) <= CALIB_MEAN_TOL + F.TOL and", "good = (abs(mz) <= 2 * CALIB_MEAN_TOL + F.TOL and"),
 ("CALIB_SD[0] - F.TOL <= x['sd_z'] <= CALIB_SD[1] + F.TOL\n", "True\n"),
 ("                    and np.isfinite(x['spread_ratio']) and x['spread_ratio'] <= CALIB_SPREAD_MAX + F.TOL)\n", "                    and True)\n"),
 ("    return head + body\n", "    return body + head\n"),
 ("if x['kind'] in ('null', 'side_flip') and x['plant'] == 0 and x['PASS'] != 'NOT RUN'",
  "if x['kind'] in ('null', 'side_flip', 'side_plant') and x['PASS'] != 'NOT RUN'"),
]
GONE = "fair_v3 has no candidates and no draw: the null is drawn by weight (null_p, null_rows)"
NOT_HERE = {('v1', i): GONE for i in (1, 2, 3, 4, 5, 6, 7, 9, 10, 11)}
NOT_HERE[('v1', 8)] = "real pre-fire moments drawn as made-up fires: OWN 2 plants it on null_p"
NOT_HERE[('v1', 14)] = "fair_v1's made-up alarm without its own pre-fire cut: fair_v3's rule (review B); OWN 9 plants the cut back"
ADAPTED = {                     # fair_v1 / fair_v2 planted bugs whose text fair_v3 changed: the same bug on fair_v3's text
 ('v1', 13): ("pre_R=L.preR[keep], wid=np.arange(len(rows)))", "pre_R=np.zeros(int(keep.sum()), bool), wid=np.arange(len(rows)))"),
 ('v1', 37): ("'rate_SepDec': sd / n, 'rate_JanApr': ja / n, 'rate_both': both / n,\n", "'rate_SepDec': ja / n, 'rate_JanApr': sd / n, 'rate_both': both / n,\n"),
 ('v2', 7): ("'fires': fires, 'z_min': d.get('z_min', np.nan),\n", "'fires': fires, 'z_min': np.nan,\n"),
}
EXTRA = [("'rate_SepDec': sd / n, 'rate_JanApr': ja / n, 'rate_both': both / n, 'median_z_SepDec': np.nan,",   # #37 on the EITHER rows
          "'rate_SepDec': ja / n, 'rate_JanApr': sd / n, 'rate_both': both / n, 'median_z_SepDec': np.nan,")]
NAME, TEST = 'fair_v3.py', 'test_fair_v3.py'
EXTRA_SRC, EXTRA_TESTS = ('fl_read_v10.py', 'fl_read_v8.py'), ('test_fl_read_v10.py',)


def plan(src):
    """OWN, then fair_v1's and fair_v2's lists (each text once in fair_v3, or ADAPTED, or NOT HERE), then EXTRA -> [(label, old, new)]"""
    out = [('own %d' % i, o, n) for i, (o, n) in enumerate(OWN, 1)]
    for tag, P in (('v1', P1), ('v2', P2)):
        for i, (o, n) in enumerate(P.M, 1):
            if (tag, i) in NOT_HERE:
                continue
            if (tag, i) in ADAPTED:
                out.append(('%s #%d adapted' % (tag, i),) + ADAPTED[(tag, i)])
            elif src.count(o) == 1:
                out.append(('%s #%d' % (tag, i), o, n))
            else:
                raise SystemExit('NOT ONCE AND NOT LISTED: %s #%d (%d times): %s' % (tag, i, src.count(o), o[:80]))
    return out + [('extra %d' % i, o, n) for i, (o, n) in enumerate(EXTRA, 1)]


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
    here = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(here, NAME)).read(); M = plan(src)
    for lab, old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', lab, src.count(old), old)
    print('%s %s, tests/%s %s, planted bugs %d (own %d; from fair_v1 %d and fair_v2 %d: adapted %d, not here %d; extra %d)' % (
        NAME, s16(os.path.join(here, NAME)), TEST, s16(os.path.join(here, 'tests', TEST)), len(M), len(OWN), len(P1.M), len(P2.M),
        len(ADAPTED), len(NOT_HERE), len(EXTRA)))
    for k, v in sorted(NOT_HERE.items()):
        print('  not here: %s #%d: %s' % (k[0], k[1], v))
    if '--check' in argv:
        return 0
    md = os.path.join(os.path.dirname(here), 'money_direction', 'md_v1.py')
    if run_one(src, here, md):
        print('THE UNCHANGED CODE FAILS ITS TESTS: no verdict'); return 2
    with ThreadPoolExecutor(3) as ex:
        rcs = list(ex.map(lambda m: run_one(src, here, md, m[1], m[2]), M))
    alive = []
    for i, ((lab, old, new), rc) in enumerate(zip(M, rcs), 1):
        print('%2d %-6s %-16s %s' % (i, 'KILLED' if rc else 'ALIVE', lab, old.strip()[:100].replace('\n', ' | ')), flush=True)
        if not rc:
            alive.append(i)
    print('mutants %d, killed %d, alive %d%s' % (len(M), len(M) - len(alive), len(alive), (': ' + ','.join(map(str, alive))) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
