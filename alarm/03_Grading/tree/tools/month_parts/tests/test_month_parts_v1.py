#!/usr/bin/env python3
"""test_month_parts_v1.py (SCOUT 29 Oct 2026, revised after reviews 1 and 2; TEST, NOT REVIEWED): tests of
alarm_grade_chain_v2_2_to20260430.sh's step 1, run on the chain's OWN text: the whole step-1 block (status line, PARTS guard, the
loop with its detect call, the merge) is cut out of the file and run in bash with tests/fake_detect.py in place of detect_aw1.py,
on made-up rosters (not in alphabetical order). Then planted bugs: each mutant of the chain text must make a test fail. Seconds.
  python3 -B tests/test_month_parts_v1.py        (exit 0: every test passes and every mutant is caught)"""
import os, re, sys, json, subprocess, tempfile
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = os.path.join(HOME, 'alarm_grade_chain_v2_2_to20260430.sh')
FAKE = os.path.join(HOME, 'tests', 'fake_detect.py')
R12 = ['ZEC', 'ADA', 'BTC', 'XRP', 'ETH', 'SOL', 'DOGE', 'LTC', 'BNB', 'AVAX', 'DOT', 'LINK']
R52 = ['Z%02d' % (51 - i) for i in range(52)]           # 52 coins, reverse order (as many as the real roster)


def part_code(txt):
    m = re.search(r'C=\$\(\$PY -c "(.*?)" \$ROSTER \$NP \$i\)', txt)
    assert m, 'no partition line'
    return m.group(1)


def parts(txt, coins, n, tmp):
    p = os.path.join(tmp, 'roster_p.json'); json.dump({'coins': coins}, open(p, 'w'))
    return [subprocess.run([sys.executable, '-c', part_code(txt), p, str(n), str(i)], capture_output=True, text=True, check=True).stdout.strip()
            for i in range(n)]


def block(txt):
    L = txt.split('\n')
    s = [l for l in L if l.startswith("printf 'step\\trc") and 'st(){' in l]
    i = [k for k, l in enumerate(L) if l.startswith('# 1 detect in PARTS parts')]
    assert len(s) == 1 and len(i) == 1, 'status line or step 1 not found'
    j = [k for k in range(i[0], len(L)) if L[k].rstrip().endswith('> $D/EVENTS.tsv')][0]
    return s[0] + '\n' + '\n'.join(L[i[0]:j + 1]) + '\n'


def run(txt, roster, tmp, parts_env, fail=None):
    """run the chain's step 1 on a made-up roster with the fake detector; return (rc, list rows, status text, merged text, part A args)"""
    os.makedirs(tmp)
    rp = os.path.join(tmp, 'roster.json'); json.dump({'coins': roster}, open(rp, 'w'))
    D = os.path.join(tmp, 'det_X_v1'); S = os.path.join(tmp, 'STATUS_X.tsv')
    env = dict(os.environ, PY=sys.executable, DET=FAKE, DEF=os.path.join(tmp, 'def.json'), ROSTER=rp, FIRST='20250910', LAST='20260430', D=D, S=S)
    env.pop('PARTS', None); env.pop('FAKE_FAIL_COIN', None)
    if fail:
        env['FAKE_FAIL_COIN'] = fail
    if parts_env is not None:
        env['PARTS'] = parts_env
    p = subprocess.run(['bash', '-c', 'set -uo pipefail\n' + block(txt) + 'exit 0\n'], env=env, capture_output=True, text=True)
    st = open(S).read() if os.path.exists(S) else ''
    merged = open(D + '/EVENTS.tsv').read() if os.path.exists(D + '/EVENTS.tsv') else ''
    args = open(D + '_A/ARGS.txt').read() if os.path.exists(D + '_A/ARGS.txt') else ''
    return p.returncode, [l for l in merged.split('\n') if l and not l.startswith('#')], st, merged, args


def expected(roster):
    rows = []
    for j, c in enumerate(roster):
        for t in (900 + 100 * (j % 3), 2000 + 50 * (j % 2)):
            rows.append((t, c, '%s\t%d\t%d\t%d\tfake\tid%s%d' % (c, t, 1 if j % 2 == 0 else -1, t, c, t)))
    return ['coin\tt\tside\tt0\ttrigger\tevent_id'] + [r[2] for r in sorted(rows)]


def run_tests(txt):
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        c10 = ['C%d' % i for i in range(10)]
        exp = {2: ['C0,C1,C2,C3,C4', 'C5,C6,C7,C8,C9'], 3: ['C0,C1,C2', 'C3,C4,C5', 'C6,C7,C8,C9'], 4: ['C0,C1', 'C2,C3,C4', 'C5,C6', 'C7,C8,C9']}
        for n, e in exp.items():                                   # 1 hand-checked partitions
            got = parts(txt, c10, n, tmp)
            if got != e: fails.append('parts n=%d %s' % (n, got))
        c52 = ['K%02d' % i for i in range(52)]
        if parts(txt, c52, 2, tmp) != [','.join(c52[:26]), ','.join(c52[26:])]: fails.append('n=2 is not v2_1 halves')
        for n in range(2, 27):
            g = parts(txt, c52, n, tmp); flat = [x for p in g for x in p.split(',')]
            if flat != c52 or any(not p for p in g): fails.append('cover n=%d' % n)
        lists = {}
        for n, ros in (('2', R12), ('3', R12), ('4', R12), ('8', R12), ('13', R52), ('26', R52), (None, R52)):   # 2 the whole step 1
            want = expected(ros)
            rc, rows, st, merged, args = run(txt, ros, os.path.join(tmp, 'r%s' % n), n)
            lists[n] = rows
            if rc != 0: fails.append('PARTS=%s rc %d' % (n, rc))
            if rows != want: fails.append('PARTS=%s list differs (%d rows, want %d)' % (n, len(rows), len(want)))
            k = int(n or 26)
            nst = sum(1 for l in st.split('\n') if re.match(r'detect_[A-Z]\t0\t', l))
            if nst != k: fails.append('PARTS=%s status rows %d' % (n, nst))
            if not merged.startswith('# fake detect part starting %s\n' % ros[0]): fails.append('PARTS=%s header not from part A' % n)
            if ' --workers 3' not in args or '--research-window 20250901:20260430' not in args or '--first 20250910 --last 20260430' not in args:
                fails.append('PARTS=%s detect args %s' % (n, args.strip()))
        for bad in ('1', '27', '30', 'x', '0', '9x'):                             # 3 the guard runs and stops
            rc, rows, st, merged, args = run(txt, R12, os.path.join(tmp, 'bad%s' % bad), bad)
            if rc != 2 or 'BAD_PARTS' not in st or merged: fails.append('PARTS=%s not stopped (rc %d)' % (bad, rc))
        rc, rows, st, merged, args = run(txt, R12[:5], os.path.join(tmp, 'empty'), '8')   # 4 an empty part stops
        if rc != 3 or 'EMPTY_PART' not in st: fails.append('EMPTY_PART not stopped (rc %d)' % rc)
        rc, rows, st, merged, args = run(txt, R12, os.path.join(tmp, 'empty26'), None)   # 26 parts of 12 coins
        if rc != 3 or 'EMPTY_PART' not in st: fails.append('EMPTY_PART not stopped (rc %d)' % rc)
        rc, rows, st, merged, args = run(txt, R12, os.path.join(tmp, 'fail'), '4', fail='ETH')   # 5 a refused part stops (ETH in part B)
        if rc != 3 or not re.search(r'^detect_B\t2\t', st, re.M) or merged: fails.append('a refused detect not stopped (rc %d)' % rc)
    return fails


def main():
    txt = open(CHAIN).read()
    f = run_tests(txt)
    print('TESTS', 'PASS' if not f else 'FAIL %s' % f)
    muts = [('(i+1)*k//n]', '(i+1)*k//n-1]'), ('seq 0 $((NP-1))', 'seq 1 $((NP-1))'), ('seq 0 $((NP-1))', 'seq 0 3'),
            ("-k2,2n -k1,1", "-k2,2 -k1,1"), ("sort -t$'\\t' -k2,2n -k1,1", "sort -s -t$'\\t' -k2,2n"), ('tail -n +2; done', 'tail -n +3; done'),
            ('${PARTS:-26}', '${PARTS:-8}'), ('^([2-9]|1[0-9]|2[0-6])$', '^([1-9]|1[0-9]|2[0-6])$'), ('^([2-9]|1[0-9]|2[0-6])$', '^([2-9]|[1-2][0-9])$'), ('(2 to 26)"; exit 2; }', '(2 to 26)"; NP=4; }'), ("c[i*k//n:", "c[i*k//n+1:"),
            ('for h in $PL; do', 'for h in A B; do'), ('PL="$PL $h"', 'PL="$h"'), ('LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z)', 'LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Y)'),
            ("grep '^#' ${D}_A/EVENTS.tsv; echo", "grep '^#' ${D}_B/EVENTS.tsv; echo"),
            ('  [ -n "$C" ] || { st detect_$h 2 0 "EMPTY_PART $i of $NP"; exit 3; }\n', ''), ('--coins $C', '--coins ALL'),
            ('--workers 3', '--workers 8'), ('[ $rc -eq 0 ] && [ -f ${D}_$h/EVENTS.tsv ] || exit 3', '[ -f ${D}_$h/EVENTS.tsv ] || exit 3')]
    missed = []
    for a, b in muts:
        assert txt.count(a) >= 1, ('mutant target missing', a)
        try:
            caught = bool(run_tests(txt.replace(a, b, 1)))
        except Exception:
            caught = True
        print('MUTANT %-48s %s' % (a.strip()[:48], 'KILLED' if caught else 'SURVIVED'))
        if not caught: missed.append(a)
    print('MUTANTS %d of %d killed' % (len(muts) - len(missed), len(muts)))
    return 1 if f or missed else 0


if __name__ == '__main__':
    sys.exit(main())
