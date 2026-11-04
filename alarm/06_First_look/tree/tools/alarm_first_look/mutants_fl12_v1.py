"""mutants_fl12_v1.py (SCOUT 2 Nov 2026): planted bugs in edition 12's own three files; every one must make tests/test_fl12_v1.py fail. The unchanged copy passes first; 3 at once.
  TMPDIR=<dir> python3 -B mutants_fl12_v1.py [--check]   (from tools/alarm_first_look; copies what the test needs; the test's moment_v1 cross-check is left out here: planted bugs must die on the planted cases)"""
import hashlib, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

M = [
 # bar_v1
 ('bar_v1.py', "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 303, 168", "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 4.0, 87, 14, 303, 168"),
 ('bar_v1.py', "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 303, 168", "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 80, 14, 303, 168"),
 ('bar_v1.py', "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 303, 168", "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 7, 150, 168"),
 ('bar_v1.py', "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 303, 168", "K_COST, LINE_Q, LINE_DAYS, LINE_MIN_N, LINE_BESIDE_N = 6.0, 87, 14, 168, 168"),
 ('bar_v1.py', "b = int(np.searchsorted(ends, t_min, side='left'))", "b = int(np.searchsorted(ends, t_min, side='right'))"),          # the moment's own minute
 ('bar_v1.py', "b = int(np.searchsorted(ends, t_min, side='left'))", "b = int(np.searchsorted(ends, t_min + 60, side='left'))"),      # an hour of look-ahead
 ('bar_v1.py', "b = int(np.searchsorted(ends, t_min, side='left'))", "b = len(ends)"),                                                # all the future
 ('bar_v1.py', "a = int(np.searchsorted(ends, t_min - LINE_DAYS * 1440, side='left'));", "a = 0;"),                                  # all the past
 ('bar_v1.py', "return J + H, v", "return J, v"),                                                                                     # a window dated at its start
 ('bar_v1.py', "ok = f.mean(1) >= VALUED_MIN", "ok = f.mean(1) >= 0.0"),
 ('bar_v1.py', "ok = f.mean(1) >= VALUED_MIN", "ok = f.mean(1) > VALUED_MIN"),
 ('bar_v1.py', "J = J[np.isfinite(m[J])]", "J = J"),
 ('bar_v1.py', "np.nanmax(np.abs(W / m[J][:, None] - 1), axis=1) * 100.0", "np.nanmax(W / m[J][:, None] - 1, axis=1) * 100.0"),       # up only
 ('bar_v1.py', "np.nanmax(np.abs(W / m[J][:, None] - 1), axis=1) * 100.0", "np.nanmax(np.abs(W / m[J][:, None] - 1), axis=1)"),        # a fraction
 ('bar_v1.py', "J = np.arange(1, len(m) - H, 60)", "J = np.arange(0, len(m) - H, 60)"),
 ('bar_v1.py', "return max(K_COST * cost_pct, line_pct), ''", "return K_COST * cost_pct, ''"),
 ('bar_v1.py', "return max(K_COST * cost_pct, line_pct), ''", "return line_pct, ''"),
 ('bar_v1.py', "return max(K_COST * cost_pct, line_pct), ''", "return min(K_COST * cost_pct, line_pct), ''"),
 ('bar_v1.py', "if why:\n        return np.nan, '+'.join(why)", "if cwhy:\n        return np.nan, '+'.join(why)"),
 ('bar_v1.py', "FEE_BP, GAP_BP = 9.0, 3.2", "FEE_BP, GAP_BP = 0.0, 3.2"),
 ('bar_v1.py', "FEE_BP, GAP_BP = 9.0, 3.2", "FEE_BP, GAP_BP = 9.0, 0.0"),
 ('bar_v1.py', "(FEE_BP + float(s06) + float(s08) + GAP_BP) / 100.0", "(FEE_BP + 2 * float(s06) + GAP_BP) / 100.0"),
 ('bar_v1.py', "(FEE_BP + float(s06) + float(s08) + GAP_BP) / 100.0", "(FEE_BP + float(s06) + float(s08) + GAP_BP) / 10000.0"),
 ('bar_v1.py', "if (np.isfinite(s10) and s10 > EXHAUSTED_MAX) or (np.isfinite(s11) and s11 > EXHAUSTED_MAX):", "if np.isfinite(s10) and s10 > EXHAUSTED_MAX:"),
 ('bar_v1.py', "if (np.isfinite(s10) and s10 > EXHAUSTED_MAX) or (np.isfinite(s11) and s11 > EXHAUSTED_MAX):", "if (np.isfinite(s10) and s10 >= EXHAUSTED_MAX) or (np.isfinite(s11) and s11 > EXHAUSTED_MAX):"),
 ('bar_v1.py', "if not (np.isfinite(s06) and np.isfinite(s08)):", "if not np.isfinite(s06):"),
 ('bar_v1.py', "h = int((t[i] - t0) // 3600); cw = C[c][:, h]", "h = int((t[i] - t0) // 3600); cw = C[c][:, min(h + 1, C[c].shape[1] - 1)]"),   # next hour's cell
 ('bar_v1.py', "h = int((t[i] - t0) // 3600); cw = C[c][:, h]", "h = int((t[i] - t0) // 3600); cw = C[c][:, max(h - 24, 0)]"),                   # yesterday's
 ('bar_v1.py', "(int(t[i]) - t0) / 60.0, memo)", "(int(t[i]) - t0) // 60 + 1, memo)"),
 ('bar_v1.py', "if int(t.min()) < t0 or int(t.max()) >= t_end:", "if int(t.max()) >= t_end:"),
 ('bar_v1.py', "if int(t.min()) < t0 or int(t.max()) >= t_end:", "if int(t.min()) < t0:"),
 ('bar_v1.py', "if a > b or b >= T1:", "if a > b:"),
 ('bar_v1.py', "(nn >= LINE_BESIDE_N) & (nn < LINE_MIN_N)", "(nn < LINE_MIN_N)"),
 # fl_read_v12
 ('fl_read_v12.py', "WIN60 = tuple(h for h in F.WINDOWS if h <= F.HIT_H)", "WIN60 = tuple(F.WINDOWS)"),
 ('fl_read_v12.py', "WIN60 = tuple(h for h in F.WINDOWS if h <= F.HIT_H)", "WIN60 = (F.HIT_H,)"),
 ('fl_read_v12.py', "for d in ('FADE', 'FOLLOW'):\n            v = T", "for d in ('FADE',):\n            v = T"),
 ('fl_read_v12.py', "seen |= known & np.isfinite(v) & (v >= bar - F.TOL)", "seen |= known & np.isfinite(v) & (v > bar + F.TOL)"),
 ('fl_read_v12.py', "hit = np.where(seen, 1.0, np.where(known & full, 0.0, np.nan))", "hit = np.where(seen, 1.0, np.where(full, 0.0, np.nan))"),       # unknown bar a miss
 ('fl_read_v12.py', "hit = np.where(seen, 1.0, np.where(known & full, 0.0, np.nan))", "hit = np.where(seen, 1.0, 0.0)"),                              # unknown path a miss
 ('fl_read_v12.py', "full = np.isfinite(T['BEST_%dM__FADE' % F.HIT_H]) & np.isfinite(T['BEST_%dM__FOLLOW' % F.HIT_H])", "full = np.isfinite(T['BEST_%dM__FADE' % F.HIT_H])"),
 ('fl_read_v12.py', "return hit, known & ~seen & ~full", "return hit, ~seen & ~full"),
 ('fl_read_v12.py', "V.A = dict(L.A); V.R = dict(L.R);", "V.A = L.A; V.R = L.R;"),
 ('fl_read_v12.py', "V.A[oo] = -hitA; V.R[ob] = hitR; V.R[oo] = -hitR", "V.A[oo] = -hitA; V.R[ob] = hitA[:0].sum() + hitR * 0; V.R[oo] = -hitR"),      # the random's own hit lost
 ('fl_read_v12.py', "return F.bar8(V, F.match7(V, bz, months, True), months, counts, 'SIZE', z_min)", "return F.bar8(V, F.match7(V, bz, months, False), months, counts, 'SIZE', z_min)"),
 ('fl_read_v12.py', "if tuple(h) != BV.HEAD:", "if False:"),
 ('fl_read_v12.py', "if set(keys) != set(d) or len(keys) != len(d):", "if not set(keys) <= set(d):"),
 ('fl_read_v12.py', "if e is None or e['list'][1] != r[col] or not os.path.isfile(p):", "if e is None or not os.path.isfile(p):"),
 ('fl_read_v12.py', "res['RULE_12'] = 'NOT RUN' if V is None or bz is None else F.overall8(d, w)", "res['RULE_12'] = F.overall8({'SIZE': d['SIZE11'], 'SIDE': d['SIDE']}, {'SIZE': w['SIZE11'], 'SIDE': w['SIDE']}) if V is None or bz is None else F.overall8(d, w)"),
 ('fl_read_v12.py', "res['RULE_12'] = 'NOT RUN' if V is None or bz is None else F.overall8(d, w)", "res['RULE_12'] = 'NOT RUN' if V is None or bz is None else F.overall8({'SIZE': d['SIZE11'], 'SIDE': d['SIDE']}, {'SIZE': w['SIZE11'], 'SIDE': w['SIDE']})"),
 ('fl_read_v12.py', "c = F.counts8(L, ms); v8 =", "c = F.counts8(V, ms) if V is not None and False else {m: 0 for m in ms}; v8 ="),                     # COUNT lost
 ('fl_read_v12.py', "'NO_COST': sum('NO_COST' in q for q in wy.tolist())", "'NO_COST': 0"),
 ('fl_read_v12.py', "'bar_unknown': cnt(wy),", "'bar_unknown': 0,"),
 ('fl_read_v12.py', "'fires_known': int(np.isfinite(hA[fa]).sum())", "'fires_known': int(fa.sum())"),
 ('fl_read_v12.py', "if not side_same(out):", "if False:"),
 ('fl_read_v12.py', "F.main(targets, H, costs_path, out + '.e11', *rdirs)", "os.makedirs(out + '.e11')"),
 ('fl_read_v12.py', "if not os.path.isfile(os.path.join(bdir, 'BAR_V1.json')):\n        raise M.Refused('NO BAR_V1.json in %s (the build writes it last)' % bdir)", "pass"),
 ('fl_read_v12.py', "int(q['RULE_12'] != q['RULE_9_here'])", "0"),
 ('fl_read_v12.py', "'fires_known': int((X['ok'] & wm).sum())", "'fires_known': int((X['busy'] & wm).sum())"),
 ('fl_read_v12.py', "'fires_matched': int((X['matched'] & wm).sum())", "'fires_matched': int((X['ok'] & wm).sum()) + 1"),
 ('fl_read_v12.py', "'waves_known': wv(X['ok'] & wm)", "'waves_known': wv(wm)"),
 ('fl_read_v12.py', "'random_known': int((rb & np.isfinite(hR) & np.isfinite(rR)).sum())", "'random_known': int(rb.sum())"),
 # the hold: admission
 ('bar_v1.py', "    if not (np.isfinite(s10) and np.isfinite(s11)):\n        return np.nan, 'NO_COST'\n", ""),
 ('bar_v1.py', "    if not (np.isfinite(s10) and np.isfinite(s11)):", "    if not np.isfinite(s10):"),
 ('bar_v1.py', "    if not (np.isfinite(s10) and np.isfinite(s11)):", "    if not np.isfinite(s11):"),
 ('bar_v1.py', "    if np.isfinite(c) == bool(set(w) & {'NO_COST', 'EXHAUSTED_COST'}):", "    if False:"),
 ('bar_v1.py', "    if np.isfinite(l) == ('NO_LINE' in w) or np.isfinite(l) != (nn >= LINE_MIN_N):", "    if np.isfinite(l) != (nn >= LINE_MIN_N):"),
 ('bar_v1.py', "    if np.isfinite(l) == ('NO_LINE' in w) or np.isfinite(l) != (nn >= LINE_MIN_N):", "    if np.isfinite(l) == ('NO_LINE' in w):"),
 ('bar_v1.py', "    if np.isfinite(b) == bool(w):", "    if False:"),
 ('bar_v1.py', "    if np.isfinite(b) and abs(b - max(K_COST * c, l)) > 1e-9 * max(1.0, b):", "    if False:"),
 ('bar_v1.py', "    if any(x != '' and not (np.isfinite(float(x)) and float(x) >= 0) for x in (cost, line, bar)):", "    if False:"),
 ('bar_v1.py', "    if not set(w) <= {'NO_COST', 'EXHAUSTED_COST', 'NO_LINE'}:", "    if False:"),
 ('fl_read_v12.py', "    if hashlib.sha256(raw).hexdigest()[:16] != out[1]:", "    if False:"),
 ('fl_read_v12.py', "or out[0] != os.path.basename(p):", "or False:"),
 ('fl_read_v12.py', "    if man.get('version') != BV.VERSION or man.get('settings') != BV.SETTINGS:", "    if man.get('settings') != BV.SETTINGS:"),
 ('fl_read_v12.py', "    if man.get('version') != BV.VERSION or man.get('settings') != BV.SETTINGS:", "    if man.get('version') != BV.VERSION:"),
 ('fl_read_v12.py', "        bad = BV.row_fault(x[2], x[3], x[4], x[5], x[6]) if len(x) == len(h) else 'COLUMNS'\n", "        bad = None\n"),
 ('fl_read_v12.py', "    if e.get('rows') != len(rows):", "    if False:"),
 ('fl_read_v12.py', "    if e.get('why') != why:", "    if False:"),
 ('fl_read_v12.py', "'labels_read': 'retrospective: RULE_12 beside RULE_9, neither replaces the other', ", ""),
 ('fl_read_v12.py', "x = [aid, r['code'], r['V'], r['lean'], q['RULE_12'], q['RULE_9_here'], int(", "x = [aid, r['code'], r['V'], r['lean'], q['RULE_12'], q['RULE_12'], int("),
 # fair_v5
 ('fair_v5.py', "V2 = E.size_view(L2, hR[rws], hR[keep])", "V2 = E.size_view(L2, hR[rws], np.where(np.isfinite(hR[keep]), hR[keep], 0.0))"),            # unknown random as a miss
 ('fair_v5.py', "V2 = E.size_view(L2, hR[rws], hR[keep])", "V2 = E.size_view(L2, np.where(np.isfinite(hR[rws]), hR[rws], 0.0), hR[keep])"),              # unknown fire as a miss
 ('fair_v5.py', "V2 = E.size_view(L2, hR[rws], hR[keep])", "V2 = L2"),
 ('fair_v5.py', "L3 = P.plant_size(V2, bz2, plant, P.rng_for(s, code, 'size_plant', plant))", "L3 = V2"),
 ('fair_v5.py', "s = base + k\n        rws", "s = k\n        rws"),
 ('fair_v5.py', "s = base + k\n        netA", "s = k\n        netA"),
 ('fair_v5.py', "x = x[0]; lo, hi = clopper(x['pass_both'], x['runs'])", "x = x[0]; lo, hi = clopper(x['pass_SepDec'], x['runs'] * 2)"),
 ('fair_v5.py', "for plant in (plants if bz2 is not None and k < plant_seeds else []):", "for plant in (plants if bz2 is not None and s < plant_seeds else []):"),
 ('fair_v5.py', "{p: {'SIZE': E.size12(V, bz, ms, counts[p], Z[p]), 'SIDE'", "{p: {'SIZE': F.verdict8(L, bz, ms, counts[p], z_min=Z[p])['SIZE'], 'SIDE'"),
 ('fair_v5.py', "low = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k - 1, n, p) < a / 2)", "low = 0.0"),
 ('fair_v5.py', "high = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > a / 2)", "high = 1.0"),
 ('fair_v5.py', "netA, netR = P.side_flip(L, P.rng_for(s, code, 'side_flip', 0))", "netA, netR = P.side_flip(L, P.rng_for(s + 1, code, 'side_flip', 0))"),
]
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)
SRC = ('bar_v1.py', 'fl_read_v12.py', 'fair_v5.py', 'fl_read_v11.py', 'fair_v4.py', 'fl_read_v8.py')
TESTS = ('test_fl12_v1.py', 'test_fl_read_v11.py')


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def run_one(m=None):
    with tempfile.TemporaryDirectory() as d:
        for x in ('fl/tests', 'money_direction', 'labcore'):
            os.makedirs(os.path.join(d, x))
        shutil.copy(os.path.join(TOOLS, 'money_direction', 'md_v1.py'), os.path.join(d, 'money_direction'))
        for x in ('__init__.py', 'waves.py'):
            shutil.copy(os.path.join(TOOLS, 'labcore', x), os.path.join(d, 'labcore'))
        for x in SRC:
            shutil.copy(os.path.join(HERE, x), os.path.join(d, 'fl'))
        for x in TESTS:
            shutil.copy(os.path.join(HERE, 'tests', x), os.path.join(d, 'fl', 'tests'))
        if m:
            p = os.path.join(d, 'fl', m[0]); txt = open(p).read(); assert txt.count(m[1]) == 1, m
            os.chmod(p, 0o644)   # ALARM_V1_19_1: shutil.copy keeps an install's read-only mode (job 20266942: PermissionError)
            open(p, 'w').write(txt.replace(m[1], m[2]))
        return subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(d, 'fl', 'tests', TESTS[0])], capture_output=True, text=True).returncode


def main(argv):
    print('bar_v1 %s fl_read_v12 %s fair_v5 %s test %s planted bugs %d' % (s16(HERE + '/bar_v1.py'), s16(HERE + '/fl_read_v12.py'), s16(HERE + '/fair_v5.py'), s16(HERE + '/tests/test_fl12_v1.py'), len(M)))
    for m in M:
        assert open(os.path.join(HERE, m[0])).read().count(m[1]) == 1, ('NOT ONCE', m)
    if '--check' in argv:
        return 0
    if run_one():
        print('THE UNCHANGED CODE FAILS ITS TESTS: no verdict'); return 2
    with ThreadPoolExecutor(3) as ex:
        rcs = list(ex.map(run_one, M))
    alive = []
    for i, (m, rc) in enumerate(zip(M, rcs), 1):
        print('%2d %-6s %s %s' % (i, 'KILLED' if rc else 'ALIVE', m[0], m[1].strip()[:90].replace('\n', ' | ')), flush=True)
        if not rc:
            alive.append(i)
    print('mutants %d, killed %d, alive %d%s' % (len(M), len(M) - len(alive), len(alive), (': ' + ','.join(map(str, alive))) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
