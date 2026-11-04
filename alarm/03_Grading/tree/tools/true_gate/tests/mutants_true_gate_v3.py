#!/usr/bin/env python3
import os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); CODE = os.path.join(HERE, '..', 'true_gate_v3.py'); TEST = os.path.join(HERE, 'test_true_gate_v3.py')
# left out as equivalent: Mc's own cover no longer decides; check_mirror makes the mirror read what the label reads, so its circular check repeats the label's
M = [('coverage rule off', "    if not cover >= MIN_COVER:\n        return 'UNSURE'\n", ""),
 ('coverage strict', "if not cover >= MIN_COVER:", "if not cover > MIN_COVER:"),
 ('difference bar off', "and dg >= MIN and dlo > 0:", "and dlo > 0:"),
 ('difference interval off', "and dg >= MIN and dlo > 0:", "and dg >= MIN:"),
 ('no difference at all', "if gap >= MIN and lo > 0 and dg >= MIN and dlo > 0:", "if gap >= MIN and lo > 0:"),
 ('not supported on the gap only', "if hi < MIN or dhi < MIN:", "if hi < MIN:"),
 ('not supported on the difference only', "if hi < MIN or dhi < MIN:", "if dhi < MIN:"),
 ('not supported at the bar', "if hi < MIN or dhi < MIN:", "if hi <= MIN or dhi <= MIN:"),
 ('history reads the day itself', "for k in range(1, HIST_DAYS + 1):", "for k in range(0, HIST_DAYS + 1):"),
 ('history one day too long', "for k in range(1, HIST_DAYS + 1):", "for k in range(1, HIST_DAYS + 2):"),
 ('history minimum off', "        if len(v) < HIST_MIN:\n            return NAN\n", ""),
 ('ties not halved', "0.5 * (v == x).sum()", "(v == x).sum()"),
 ('groups ignored for random', "L.R[key] = np.where(gR == g, hR, NAN)", "L.R[key] = hR"),
 ('coarse step off', "for recent in (True, False):", "for recent in (True,):"),
 ('coarse overwrites a fine price', "& ~M['matched']); off", "); off"),
 ('mirror fires not required', "both = Mc['matched'] & Mm['matched']", "both = Mc['matched']"),
 ('difference is the sum', "'e': Mc['e'] - Mm['e']", "'e': Mc['e'] + Mm['e']"),
 ('mirror same as claim', "Mm, _ = strat(L, mA, mR, bz, months, sA, sR)", "Mm, _ = strat(L, hA, hR, bz, months, sA, sR)"),
 ('flow subtracted', "out[j] = val[j] + (a + b) / 100.0", "out[j] = val[j] - (a + b) / 100.0"),
 ('flow in pct wrong', "out[j] = val[j] + (a + b) / 100.0", "out[j] = val[j] + (a + b)"),
 ('months guard off', "if str(cl['first']) < FIRST_ALLOWED or str(cl['last']) > LAST_ALLOWED or str(cl['first']) > str(cl['last']):", "if str(cl['first']) < FIRST_ALLOWED or str(cl['first']) > str(cl['last']):"),
 ('first after last passes', "if str(cl['first']) < FIRST_ALLOWED or str(cl['last']) > LAST_ALLOWED or str(cl['first']) > str(cl['last']):", "if str(cl['first']) < FIRST_ALLOWED or str(cl['last']) > LAST_ALLOWED:"),
 ('August passes', "if str(cl['first']) < FIRST_ALLOWED or str(cl['last']) > LAST_ALLOWED or", "if str(cl['last']) > LAST_ALLOWED or"),
 ('calendar not checked', "_dt.datetime.strptime(str(cl[k]), '%Y%m%d')", "str(cl[k])"),
 ('another variant PERFIRE passes', "if os.path.basename(cl['perfire']) != 'PERFIRE_%s.tsv' % cl['V']:", "if False:"),
 ('def digest not checked', "if TG.sha16(cl['def']) != cl['def_sha16']:", "if False:"),
 ('a missing def passes the fields', "('id', 'idea', 'V', 'def', 'def_sha16',", "('id', 'idea', 'V',"),
 ('coverage is the claim alone', "cover = both.sum() / kc.sum() if kc.any() else 0.0", "cover = Mc['cover']"),
 ('a mirror field not compared', "SAME_FIELDS = ('code', 'code_by_side', 'dir', 'when', 'start_s', 'end_s',", "SAME_FIELDS = ('code', 'code_by_side', 'dir', 'when', 'start_s',"),
 ('threshold sign not compared', "float(x) != -float(y)", "float(x) != float(y)"),
 ('falling threshold not compared', "elif float(x or 0) != float(y or 0):", "elif False:"),
 ('mirror may be the claim', "if {t, u} != {'falling', 'rising'} and {t, u} != {'>=', '<='}:", "if False:"),
 ('activity may read another code', "if a.get('code') != code or a.get('mode')", "if a.get('mode')"),
 ('short flow left out', "out[j] = val[j] + (a + b) / 100.0", "out[j] = val[j] + a / 100.0"),
]
src = open(CODE).read(); kill, sv, nf = [], [], []; tmp = tempfile.mkdtemp()
b = os.path.join(tmp, 'base'); os.makedirs(b); open(os.path.join(b, 'true_gate_v3.py'), 'w').write(src)
if subprocess.run([sys.executable, '-B', TEST], env=dict(os.environ, TG3_CODE=b), capture_output=True).returncode:
    print('BASELINE FAILS: the unchanged copy does not pass, no mutant can be judged'); sys.exit(1)
for i, (nm, a, b) in enumerate(M):
    if a not in src: nf.append(nm); continue
    d = os.path.join(tmp, 'm%d' % i); os.makedirs(d); open(os.path.join(d, 'true_gate_v3.py'), 'w').write(src.replace(a, b, 1))
    r = subprocess.run([sys.executable, '-B', TEST], env=dict(os.environ, TG3_CODE=d), capture_output=True, text=True)
    (kill if r.returncode else sv).append(nm)
print('MUTANTS killed %d survived %d not found %d' % (len(kill), len(sv), len(nf)))
for n in sv: print('SURVIVED', n)
for n in nf: print('NOT FOUND', n)
sys.exit(1 if nf or sv else 0)
