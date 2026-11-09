#!/usr/bin/env python3
"""mutants_d1_v6.py (SCO-A162 for SCOUT, 6 Nov 2026). TEST, NOT REVIEWED. mutants_d1_v5.py with the v6 budget line and its faults.
Planted faults on the changed lines of d1_reports_v5.py (v4's and v5's) (eo_workers, the run(n) branch of outcomes, mem_of's skip, the count
passed by chain); each mutant is a copy (with d1_mem_v2.py beside it) in <out>/<name>/, run under test_d1_v6.py (D1_TOOL=<copy>,
D1_MUTANT=1); every mutant must be caught and the unpatched copy must pass.
  python3 -B mutants_d1_v4.py <new out dir>       exit 0 all caught and the clean copy green, 1 otherwise"""
import sys
sys.dont_write_bytecode = True
import os, shutil, subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
SRC = os.environ.get('D1_SRC') or os.path.join(HERE, 'd1_reports_v6.py')
MEM = os.path.join(os.path.dirname(SRC), 'd1_mem_v2.py')
TEST = os.path.join(HERE, 'test_d1_v6.py')
M = [
    ('upper_9', "if not 0 <= n <= 8:", "if not 0 <= n <= 9:"),
    # lower_neg of v4 dropped: in v5 a negative never reaches the range check (isdigit refuses it first; D9), an equivalent mutant
    ('upper_7', "if not 0 <= n <= 8:", "if not 0 <= n <= 7:"),
    ('exit_1', "want 0 to 8\\n' % (y, n)); sys.exit(2)", "want 0 to 8\\n' % (y, n)); sys.exit(1)"),
    ('default_3', "v = kv.get(y, '0').strip()", "v = kv.get(y, '3').strip()"),
    ('key_ignored', "v = kv.get(y, '0').strip()", "v = (list(kv.values())[0] if kv else '0').strip()"),
    ('digit_check_off', "    if not v.isdigit():\n", "    if False:\n"),
    ('budget_9', "EO_BUDGET = 8   #", "EO_BUDGET = 9   #"),
    ('budget_7', "EO_BUDGET = 8   #", "EO_BUDGET = 7   #"),
    ('budget_ge', "    if need > EO_BUDGET:", "    if need >= EO_BUDGET:"),
    ('budget_max', "    need = sum(max(n, 1) for n in counts)", "    need = max(max(n, 1) for n in counts)"),
    ('zero_counts_0', "    need = sum(max(n, 1) for n in counts)", "    need = sum(counts)"),
    ('zero_counts_2', "    need = sum(max(n, 1) for n in counts)", "    need = sum(max(n, 2) for n in counts)"),
    ('budget_call_off', "    eo_budget([a[10] for _, a in jobs])", "    pass"),
    ('budget_exit_1', "% (os.environ.get('D1_EO_WORKERS', ''), need, EO_BUDGET)); sys.exit(2)", "% (os.environ.get('D1_EO_WORKERS', ''), need, EO_BUDGET)); sys.exit(1)"),
    ('nw_ge0', "if NW > 0:", "if NW >= 0:"),
    ('nw_never', "if NW > 0:", "if NW > 99:"),
    ('nw_as_1', "EOR.run(NW, LAB, CODE", "EOR.run(1, LAB, CODE"),
    ('nw_rc1', "            return 0, int(time.time() - t0)\n        cap = d1.Capture", "            return 1, int(time.time() - t0)\n        cap = d1.Capture"),
    ('mem_no_skip', "        if not os.path.isfile(root + '.mem.pkl'):                     # v4: a run(n) root: the real read answers from its store\n            continue\n", ""),
    ('chain_count_swap', "LAB, EO, eo_workers(y))))", "LAB, EO, eo_workers('RND' if y == 'ALARM' else 'ALARM'))))"),
    ('chain_count_zero', "LAB, EO, eo_workers(y))))", "LAB, EO, 0)))"),
]


def main(out):
    os.makedirs(out)
    src = open(SRC).read(); bad = 0
    env = dict(os.environ, D1_MUTANT='1', D1_SCRATCH=os.path.join(out, 'scratch'))

    def one(name, text):
        dd = os.path.join(out, name); os.makedirs(dd)
        p = os.path.join(dd, 'mut_%s.py' % name); open(p, 'w').write(text); shutil.copyfile(MEM, os.path.join(dd, 'd1_mem_v2.py'))
        return subprocess.run([sys.executable, '-B', TEST], env=dict(env, D1_TOOL=p), capture_output=True, text=True)
    r = one('clean', src)
    print('CLEAN rc %d %s' % (r.returncode, 'GREEN' if r.returncode == 0 else 'RED')); bad += r.returncode != 0
    if r.returncode:
        print(r.stdout[-800:])
    for name, a, b in M:
        if src.count(a) != 1:
            print('MUTANT %s NOT_APPLIED (%d matches)' % (name, src.count(a))); bad += 1; continue
        r = one(name, src.replace(a, b))
        fails = [l.split()[1] for l in r.stdout.splitlines() if l.startswith('FAIL ')]
        print('MUTANT %s %s %s' % (name, 'CAUGHT' if r.returncode != 0 else 'SURVIVED', ','.join(fails)))
        bad += r.returncode == 0
    print('RESULT %d mutants, %s' % (len(M), 'all caught, clean green' if not bad else '%d problems' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(2)
    sys.exit(main(sys.argv[1]))
