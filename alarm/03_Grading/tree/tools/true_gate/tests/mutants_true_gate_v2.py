#!/usr/bin/env python3
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); CODE = os.path.join(HERE, '..', 'true_gate_v2.py'); TEST = os.path.join(HERE, 'test_true_gate_v2.py')
M = [('activity anchored at t', "anchor = t - lab['end_s'] if lab['when'] == 'present' else t", "anchor = t"),
 ('a window label anchored early', "anchor = t - lab['end_s'] if lab['when'] == 'present' else t", "anchor = t - lab['end_s']"),
 ('change takes the sign', "xs.append(abs(b))", "xs.append(b)"),
 ('level takes the sign', "xs.append(abs(100.0 * (b - a) / a))", "xs.append(100.0 * (b - a) / a)"),
 ('min steps off', "if len(xs) >= ACT_MIN else NAN", "if xs else NAN"),
 ('flow skips a hole', "        if not math.isfinite(v):\n            return NAN\n        tot += v", "        if not math.isfinite(v):\n            continue\n        tot += v"),
 ('flow one step early', "t - k * spec['step_s']", "t - (k + 1) * spec['step_s']"),
 ('group at cut goes up', "side='left').astype(int)", "side='right').astype(int)"),
 ('unknown joins a group', "return np.where(np.isfinite(x), g, -1)", "return g"),
 ('groups ignored for fires', "L.A[key] = np.where(gA == g, hA, NAN);", "L.A[key] = hA;"),
 ('groups ignored for random', "L.R[key] = np.where(gR == g, hR, NAN)", "L.R[key] = hR"),
 ('shim not restored', "FL.BUSY_MIN_C = keep; L.A[key] = hA; L.R[key] = hR", "FL.BUSY_MIN_C = keep"),
 ('rows ignore weights', "rng.choice(N, min(n, N), replace=False, p=p)", "rng.choice(N, min(n, N), replace=False)"),
 ('waves stop one short', "n)) + 1", "n))"),
 ('set seed fixed', "np.random.default_rng([seed, s, 0 if mode == 'rows' else 1])", "np.random.default_rng([seed, 0, 0 if mode == 'rows' else 1])"),
 ('pseudo fires kept in the base', "left = np.setdiff1d(np.arange(len(R['t'])), ix)", "left = np.arange(len(R['t']))"),
]
src = open(CODE).read(); kill, sv, nf = [], [], []
tmp = tempfile.mkdtemp()
V1P = os.path.join(HERE, '..', 'true_gate_v1.py')
b = os.path.join(tmp, 'base'); os.makedirs(b); open(os.path.join(b, 'true_gate_v2.py'), 'w').write(src)
if subprocess.run([sys.executable, '-B', TEST], env=dict(os.environ, TG2_CODE=b, TG_V1=V1P), capture_output=True).returncode:
    print('BASELINE FAILS: the unchanged copy does not pass, no mutant can be judged'); sys.exit(1)
EQUIVALENT = {'groups ignored for fires'}   # the fires are filtered by group again right after the match
for i, (nm, a, b) in enumerate(M):
    if a not in src: nf.append(nm); continue
    d = os.path.join(tmp, 'm%d' % i); os.makedirs(d); open(os.path.join(d, 'true_gate_v2.py'), 'w').write(src.replace(a, b, 1))
    r = subprocess.run([sys.executable, '-B', TEST], env=dict(os.environ, TG2_CODE=d, TG_V1=os.path.join(HERE, '..', 'true_gate_v1.py')), capture_output=True, text=True)
    (kill if r.returncode else sv).append(nm)
print('MUTANTS killed %d survived %d not found %d' % (len(kill), len(sv), len(nf)))
for n in sv: print('SURVIVED', n)
for n in nf: print('NOT FOUND', n)
sys.exit(1 if nf or set(sv) - EQUIVALENT else 0)
