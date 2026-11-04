"""mutants_fair_v1.py (SCOUT 30 Oct 2026, tools/alarm_first_look): planted bugs in the ladder (fair_v1.py; the owner 30 Oct 2026 17:35-17:44
Berlin: "how do we know our bars are fair?"); every one must make tests/test_fair_v1.py fail. Each bug runs the tests on a temp copy
(with fl_read_v8.py and tests/test_fl_read_v8.py unchanged), 3 at once; the unchanged copy must pass first.
  TMPDIR=/tmp python3 -B mutants_fair_v1.py [--check]   (from tools/alarm_first_look; needs ../money_direction/md_v1.py)
  --check: only that each planted text occurs once in fair_v1.py"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

M = [
 # candidates: same coin, +-7 days, hour of day +-1 h on the 24 h circle, only the allowed rows
 ("t - MATCH_DAYS * 86400, side='left')", "t - MATCH_DAYS * 86400, side='right')"),
 ("t + MATCH_DAYS * 86400, side='right')", "t + MATCH_DAYS * 86400, side='left')"),
 ("MATCH_DAYS = 7\n", "MATCH_DAYS = 8\n"),
 ("; d = np.minimum(d, 86400 - d)", ""),
 ("out.append(js[a:b][d <= HOUR_TOL_S])", "out.append(js[a:b][d < HOUR_TOL_S])"),
 ("j = idx[R['coin'][idx] == c];", "j = idx;"),
 ("    idx = np.flatnonzero(ok_R); by = {}", "    idx = np.arange(len(ok_R)); by = {}"),
 ("    cands = candidates(L.A, R, L.useR & ~L.preR & (L.wR > 0))", "    cands = candidates(L.A, R, L.useR & (L.wR > 0))"),
 # draw: one a fire, fires in a random order, never one row twice
 ("            if j not in used:", "            if True:"),
 ("    for i in rng.permutation(len(cands)):", "    for i in range(len(cands)):"),
 ("        for k in rng.permutation(len(c)):", "        for k in range(len(c)):"),
 # made_up: its fires out of its random; pre-fire moments (the real alarm's and its own) out
 ("keep = np.ones(len(R['t']), bool); keep[rows] = False", "keep = np.ones(len(R['t']), bool)"),
 ("pre_R=F.pre_fire_mask(A2, R2) | L.preR[keep])", "pre_R=F.pre_fire_mask(A2, R2))"),
 ("pre_R=F.pre_fire_mask(A2, R2) | L.preR[keep])", "pre_R=L.preR[keep])"),
 # day_signs and side_flip: one coin a UTC day; the fires and the random flipped, by coins apart
 ("    return np.where(rng.random(len(u)) < 0.5, -1.0, 1.0)[inv]", "    return np.where(rng.random(len(d)) < 0.5, -1.0, 1.0)"),
 ("    d = np.asarray(t, np.int64) // 86400", "    d = np.asarray(t, np.int64) // 3600"),
 (", L.net(L.R, ob) * day_signs(L.R['t'], rng)", ", L.net(L.R, ob)"),
 ("    return L.net(L.A, ob) * day_signs(L.A['t'], rng), L.net(L.R, ob) * day_signs(L.R['t'], rng)",
  "    sa = day_signs(np.concatenate([L.A['t'], L.R['t']]), rng); n = len(L.A['t'])\n    return L.net(L.A, ob) * sa[:n], L.net(L.R, ob) * sa[n:]"),
 ("    ob = 'OBH4_60M__%s' % L.lean\n    return L.net(L.A, ob) * day_signs", "    ob = 'OBH4_15M__%s' % L.lean\n    return L.net(L.A, ob) * day_signs"),
 # plant_side: lost races turned won with probability D / (100 s) a period; the input left as it was
 ("p = min(1.0, plant / (100.0 * s));", "p = min(1.0, plant / 100.0);"),
 ("lose = np.flatnonzero(inp & (net < 0))", "lose = np.flatnonzero(inp & (net <= 0))"),
 ("        net[lose[rng.random(len(lose)) < p]] = 1.0", "        net[lose[rng.random(len(lose)) < p]] = 0.0"),
 ("    net = np.array(net, float)\n    for _, ms in PERIODS2:", "    net = np.asarray(net, float)\n    for _, ms in PERIODS2:"),
 ("        inp = L.useA & np.isin(L.wmonth, ms) & np.isfinite(net)", "        inp = L.useA & np.isfinite(net)"),
 # plant_size: misses turned into 4c moves with probability D / (100 (1 - h)) a period, h over the busy fires; the null left as it was
 ("f = min(1.0, plant / (100.0 * (1.0 - h)));", "f = min(1.0, plant / 100.0);"),
 ("miss = np.flatnonzero(inp & (v == 0))", "miss = np.flatnonzero(inp & (v != 1))"),
 ("v[miss[turn]] = vals[turn]; w[miss[turn]] = -vals[turn]", "v[miss[turn]] = vals[turn]"),
 ("    v = np.array(L2.A[ob], float); w = np.array(L2.A[oo], float)", "    v = np.asarray(L2.A[ob], float); w = np.asarray(L2.A[oo], float)"),
 ("h = wave_share(L2, (np.abs(v) == 1).astype(float), inp & busy)", "h = wave_share(L2, (np.abs(v) == 1).astype(float), inp)"),
 ("    L3 = copy.copy(L2); L3.A = dict(L2.A); L3.A[ob] = v", "    L3 = L2; L3.A[ob] = v"),
 # ladder: each run judged against its own reference, a plant on its seed's null or flip, the null's own COUNT
 ("F.side8(L, ms, netA, netR)", "F.side8(L, ms, netA)"),
 ("F.side8(L, ms, net, netR)", "F.side8(L, ms, net)"),
 ("            net = plant_side(L, netA, plant, rng_for(s, code, 'side_plant', plant))",
  "            net = plant_side(L, side_flip(L, rng_for(s, code, 'side_plant', plant))[0], plant, rng_for(s, code, 'side_plant', plant))"),
 ("            L3 = plant_size(L2, bz2, plant, rng_for(s, code, 'size_plant', plant))",
  "            L3 = plant_size(*made_up(L, R, wR, costs, bz, draw(cands, rng_for(s, code, 'size_plant', plant))), plant, rng_for(s, code, 'size_plant', plant))"),
 ("        c2 = {p: F.counts8(L2, ms) for p, ms in PERIODS2}", "        c2 = counts"),
 # summary: NOT RUN is no run; the rates; both periods; medians without NaN
 ("        if x['PASS'] == 'NOT RUN':\n            continue\n", ""),
 ("'rate_SepDec': sd / n, 'rate_JanApr': ja / n,", "'rate_SepDec': ja / n, 'rate_JanApr': sd / n,"),
 ("both = sum(ok(v, 'Sep-Dec') and ok(v, 'Jan-Apr') for v in runs.values())", "both = sum(ok(v, 'Sep-Dec') or ok(v, 'Jan-Apr') for v in runs.values())"),
 ("if p in v and np.isfinite(float(v[p][k]))]", "if p in v]"),
 # main: refusals and no half-written output
 ("if seeds < 0 or not 0 <= plant_seeds <= seeds or any(", "if seeds < 0 or any("),
 ("        shutil.rmtree(part, ignore_errors=True); raise", "        raise"),
]
NAME, TEST = 'fair_v1.py', 'test_fair_v1.py'


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def run_one(src, here, md, old=None, new=None):
    """the tests on a temp copy with one planted text (none: the unchanged code) -> the tests' exit code"""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'fl', 'tests')); os.makedirs(os.path.join(d, 'money_direction'))
        shutil.copy(md, os.path.join(d, 'money_direction'))
        shutil.copy(os.path.join(here, 'fl_read_v8.py'), os.path.join(d, 'fl'))
        with open(os.path.join(d, 'fl', NAME), 'w') as f:
            f.write(src if old is None else src.replace(old, new))
        for t in (TEST, 'test_fl_read_v8.py'):
            shutil.copy(os.path.join(here, 'tests', t), os.path.join(d, 'fl', 'tests'))
        r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(d, 'fl', 'tests', TEST)], capture_output=True, text=True)
        return r.returncode


def main(argv):
    here = os.path.dirname(os.path.abspath(__file__)); src = open(os.path.join(here, NAME)).read()
    for old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', src.count(old), old)
    print('%s %s, fl_read_v8.py %s, tests/%s %s, tests/test_fl_read_v8.py %s, planted bugs %d' % (
        NAME, s16(os.path.join(here, NAME)), s16(os.path.join(here, 'fl_read_v8.py')), TEST, s16(os.path.join(here, 'tests', TEST)),
        s16(os.path.join(here, 'tests', 'test_fl_read_v8.py')), len(M)))
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
