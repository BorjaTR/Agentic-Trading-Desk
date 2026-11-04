#!/usr/bin/env python3
"""test_month_parts_v1_1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): test_month_parts_v1.py f3f2df303f48f5c1 (SCOUT 29 Oct, released) for
the paths-only chain alarm_grade_chain_v2_2_1_to20260430.sh: the same step-1 tests and 19 planted bugs, with LAB_DAYS in the environment
and the --lab-root argument checked; then (K4) the whole chain with every step a stub: the machine only from AL, PY and LAB_DAYS, every
step from the lab tree <AL>/01_Detection/tree, and its own planted bugs. Run from an Alarm package. Its old header follows: tests of
alarm_grade_chain_v2_2_to20260430.sh's step 1, run on the chain's OWN text: the whole step-1 block (status line, PARTS guard, the
loop with its detect call, the merge) is cut out of the file and run in bash with tests/fake_detect.py in place of detect_aw1.py,
on made-up rosters (not in alphabetical order). Then planted bugs: each mutant of the chain text must make a test fail. Seconds.
  python3 -B tests/test_month_parts_v1_1.py      (exit 0: every test passes and every mutant is caught)"""
import os, re, sys, json, subprocess, tempfile, shutil, hashlib
HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = os.path.join(HOME, 'alarm_grade_chain_v2_2_1_to20260430.sh')
LABD = '/k4/lab_days'                                  # a made-up lab days folder: the fake detect never opens it
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
    env = dict(os.environ, PY=sys.executable, DET=FAKE, DEF=os.path.join(tmp, 'def.json'), ROSTER=rp, FIRST='20250910', LAST='20260430', D=D, S=S, LAB_DAYS=LABD)
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
            if ' --workers 3' not in args or ' --lab-root %s ' % LABD not in args or '--research-window 20250901:20260430' not in args or '--first 20250910 --last 20260430' not in args:
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
    global CARD_SHA16
    CARD_SHA16 = hashlib.sha256(open(package_file(*LAB_TREE, *SHA_CHECKED[0].split('/')), 'rb').read()).hexdigest()[:16]
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
    pf = chain_tests(txt)
    print('CHAIN TESTS', 'PASS' if not pf else 'FAIL %s' % pf)
    pm = run_path_mutants(txt)
    return 1 if f or missed or pf or pm else 0


CHAIN_NAME = os.path.basename(CHAIN); CHAIN_AT = ('03_Grading', 'tree', 'tools', 'month_parts')
CARD = 'alarm_card_v1_3_1.py'
SHA_CHECKED = tuple('team/RESEARCH/tools/alarm_process/' + x for x in (CARD, 'detect_aw1.py', 'idea_to_grade_aw1.py', 'I2G_PINS_AW1.json',
                    'event_outcomes_aw1.py', 'RELEASE_event_outcomes_AW1.json', 'WINDOWS_ALARM_V1.tsv'))
STAND_INS = ('team/RESEARCH/tools/alarm_process/make_random_v3_1.py', 'team/RESEARCH/tools/alarm_process/menu_v2_1.py')
EXPECTED_TOOLS = ['alarm_process/detect_aw1.py'] * 26 + ['alarm_process/' + x for x in ('idea_to_grade_aw1.py', 'make_random_v3_1.py',
                  'event_outcomes_aw1.py', 'event_outcomes_aw1.py', 'menu_v2_1.py', CARD)]
CARD_SHA16 = None                                      # set in main: the package's own card
PATH_MUTANTS = [(' --lab-root "$LAB_DAYS" --out ${D}_$h', ' --out ${D}_$h'), (' --lab-root "$LAB_DAYS" --out $W/gradeL', ' --out $W/gradeL'), ('F=$AL/01_Detection/tree;', 'F=$AL/03_Grading/tree;'), ('for k in AL PY LAB_DAYS;', 'for k in AL PY;'), ('[ -n "$v" ] && [ "${v#/}" != "$v" ] ||', '[ -n "$v" ] ||'), ('[ -f "$AL/_tools/settings_v1.py" ] && [ -d "$AL/settings" ] ||', 'true ||'), ('case "$(cd "$(dirname "$0")" && pwd -P)/" in', 'case "$(cd "$AL" && pwd -P)/" in'), ('$F/team/LAB3/code $IN $G', '$R/LAB3/code $IN $G'), ('run 0 "$LAB_DAYS"', 'run 0 "$F/lab_days"'), ('$PY -B $AP/make_random_v3_1.py', '$PY -B $L2/make_random_v3.py'), ('$PY -B $AP/menu_v2_1.py', '$PY -B $L2/menu_v2.py'), ('"$CARD_SHA" "$AP/alarm_card_v1_3_1.py"', '"$CARD_SHA" "$AP/alarm_card_v1_3.py"'), ('CARD_SHA=3c496708f9d44651;', 'CARD_SHA=a616c4378a02852b;')]

# ---------------------------------------------------------------- the whole chain, every step a stub (K4: the paths-only edition)
STUB_PY = r'''import sys, os, json
a = sys.argv[1:]
if a[:1] == ['-c']:
    os.execv(sys.executable, [sys.executable] + a)
tool, args = a[1], a[2:]
with open(os.environ['STUB_LOG'], 'a') as f:
    f.write(json.dumps({'tool': tool, 'args': args, 'env': {k: os.environ.get(k) for k in ('W', 'METRIC_TRAPS', 'CATALOGS')}}) + '\n')
name = os.path.basename(tool)
def opt(k):
    return args[args.index(k) + 1]
if name.startswith('detect'):
    out = opt('--out'); os.makedirs(out)
    rows = ['%s\t%d\t1\t%d\tstub\tid%s' % (c, 1757900000 + 600 * j, 1757900000 + 600 * j, c) for j, c in enumerate(opt('--coins').split(','))]
    open(os.path.join(out, 'EVENTS.tsv'), 'w').write('# stub\ncoin\tt\tside\tonset_t\ttrigger\tevent_id\n' + ''.join(r + '\n' for r in rows))
elif name.startswith('idea_to_grade'):
    os.makedirs(os.path.join(opt('--out'), 'matches'))
elif name.startswith('make_random'):
    open(args[2] + '_LIST.tsv', 'w').write('coin\tt\tside\nK00\t1757901000\t1\n'); open(args[2] + '_WEIGHTS.tsv', 'w').write('coin\tt\tweight\nK00\t1757901000\t1.0\n')
elif name.startswith('event_outcomes'):
    os.makedirs(args[9])
elif name.startswith('menu'):
    print('stub menu')
elif name.startswith('alarm_card'):
    open(opt('--tsv'), 'x').write('key\tvalue\n'); print('stub card')
'''
LAB_TREE = ('01_Detection', 'tree')
TABLES = ('team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json', 'team/RESEARCH/tools/alarm_process/OUTCOMES_MENU_ALARM_V1.json')


def package_file(*rel):
    """a file of the Alarm package that holds this test (settings_v1's rule: the nearest parent with _tools/settings_v1.py and settings/)"""
    d = os.path.dirname(os.path.abspath(__file__))
    while not (os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings'))):
        if os.path.dirname(d) == d:
            raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ above %s' % __file__)
        d = os.path.dirname(d)
    return os.path.join(d, *rel)


def sandbox(tmp, txt):
    """a made-up Alarm package with this chain text at its release place and, in its lab tree, the files the chain checks by sha16 (the
    package's own bytes) and stand-ins for the rest; a stub interpreter outside it; -> (AL, chain, PY, LAB, DEF)"""
    AL = os.path.join(tmp, 'Alarm'); os.makedirs(os.path.join(AL, 'settings'))
    shutil.copyfile(package_file('_tools', 'settings_v1.py'), os.path.join(os.makedirs(os.path.join(AL, '_tools')) or AL, '_tools', 'settings_v1.py'))
    for rel in SHA_CHECKED:
        p = os.path.join(AL, *LAB_TREE, *rel.split('/')); os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copyfile(package_file(*LAB_TREE, *rel.split('/')), p)
    for rel in TABLES + STAND_INS:
        p = os.path.join(AL, *LAB_TREE, *rel.split('/')); os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w').write(json.dumps({'coins': ['K%02d' % i for i in range(52)]}) if rel.endswith('ROSTER_BUILD.json') else '# stand-in\n')
    chain = os.path.join(AL, *CHAIN_AT, CHAIN_NAME); os.makedirs(os.path.dirname(chain), exist_ok=True); open(chain, 'w').write(txt)
    PY = os.path.join(tmp, 'bin', 'python'); os.makedirs(os.path.dirname(PY))
    open(PY + '.py', 'w').write(STUB_PY); open(PY, 'w').write('#!/bin/bash\nexec "%s" -B "%s.py" "$@"\n' % (sys.executable, PY)); os.chmod(PY, 0o755)
    LAB = os.path.join(tmp, 'lab_days'); os.makedirs(LAB)
    DEF = os.path.join(tmp, 'run', 'V1.json'); os.makedirs(os.path.dirname(DEF)); open(DEF, 'w').write('{"id": "V1"}\n')
    return AL, chain, PY, LAB, DEF


def run_chain(tmp, chain, env, DEF):
    W = os.path.join(tmp, 'W'); log = os.path.join(tmp, 'stub.log'); open(log, 'w').close()
    e = {k: v for k, v in os.environ.items() if k not in ('AL', 'PY', 'LAB_DAYS', 'PARTS', 'BASE', 'SCREEN', 'LEAN')}
    e.update(STUB_LOG=log, LEAN='FADE', **env)
    p = subprocess.run(['bash', chain, 'V1', DEF, W], env=e, capture_output=True, text=True, cwd=tmp)
    return p.returncode, p.stdout + p.stderr, [json.loads(l) for l in open(log) if l.strip()], W


def chain_tests(txt):
    """P1 the machine comes only from AL, PY, LAB_DAYS (absolute; AL an Alarm package holding this chain), else refused before any step;
    P2 a whole run: every step from the lab tree <AL>/01_Detection/tree, the lab days handed to detection, the grade and Outcomes, the lab3
    code and the metric tables from the lab tree, no other root in any argument, INPUTS naming this chain and its card"""
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        AL, chain, PY, LAB, DEF = sandbox(tmp, txt)
        good = {'AL': AL, 'PY': PY, 'LAB_DAYS': LAB}
        cases = [('AL unset', {k: v for k, v in good.items() if k != 'AL'}, 'NO_AL'), ('PY relative', dict(good, PY='python3'), 'NO_PY'),
                 ('LAB_DAYS unset', {k: v for k, v in good.items() if k != 'LAB_DAYS'}, 'NO_LAB_DAYS'),
                 ('LAB_DAYS relative', dict(good, LAB_DAYS='lab_days'), 'NO_LAB_DAYS'),
                 ('AL not a package', dict(good, AL=os.path.join(tmp, 'run')), 'NOT_AN_ALARM_FOLDER')]
        for label, env, msg in cases:
            rc, out, calls, W = run_chain(tmp, chain, env, DEF)
            if rc != 2 or msg not in out or calls or os.path.exists(W):
                fails.append('P1 %s: rc %d calls %d out %s' % (label, rc, len(calls), out.strip()[-160:]))
        other = os.path.join(tmp, 'elsewhere', CHAIN_NAME); os.makedirs(os.path.dirname(other)); shutil.copyfile(chain, other)
        rc, out, calls, W = run_chain(tmp, other, good, DEF)
        if rc != 2 or 'CHAIN_OUTSIDE_ALARM' not in out or calls or os.path.exists(W):
            fails.append('P1 chain outside AL: rc %d calls %d out %s' % (rc, len(calls), out.strip()[-160:]))
        rc, out, calls, W = run_chain(tmp, chain, good, DEF)
        TR = os.path.join(AL, *LAB_TREE); T = os.path.join(TR, 'team', 'RESEARCH', 'tools')
        st = open(os.path.join(W, 'STATUS_V1.tsv')).read() if os.path.exists(os.path.join(W, 'STATUS_V1.tsv')) else ''
        if rc != 0 or not re.search(r'^done\t0\t', st, re.M):
            fails.append('P2 run: rc %d %s' % (rc, (out + st).strip()[-300:]))
        names = [os.path.relpath(c['tool'], T) for c in calls]
        if names != EXPECTED_TOOLS:
            fails.append('P2 tools %s' % names)
        for c in calls:
            n = os.path.basename(c['tool']); a = c['args']
            if n.startswith(('detect', 'idea_to_grade')) and not (a.count('--lab-root') == 1 and a[a.index('--lab-root') + 1] == LAB):
                fails.append('P2 %s lab root %s' % (n, a)); break
            if n.startswith('event_outcomes') and a[2:4] != [LAB, os.path.join(TR, 'team', 'LAB3', 'code')]:
                fails.append('P2 %s lab days, lab3 code %s' % (n, a[2:4])); break
            roots = (AL, LAB, W, os.path.dirname(DEF))
            stray = [x for x in a if x.startswith('/') and not any(x == r or x.startswith(r + os.sep) for r in roots)]
            if stray:
                fails.append('P2 %s paths outside AL, LAB_DAYS, W and the run: %s' % (n, stray)); break
            L2 = os.path.join(TR, 'team', 'RESEARCH', 'LEAD', 'loop2', 'defs')
            if c['env']['METRIC_TRAPS'] != os.path.join(L2, 'METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv') or c['env']['CATALOGS'] != ':'.join(
                    [os.path.join(T, 'alarm_context', 'CTX_CATALOG_V1.tsv'), os.path.join(T, 'alarm_profile', 'EPI_CATALOG_V1.tsv'),
                     os.path.join(TR, 'team', 'LAB3', 'METRICS_HL_ADD_V1.tsv'), os.path.join(L2, 'METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv')]):
                fails.append('P2 metric tables %s' % c['env']); break
        inp = open(os.path.join(W, 'INPUTS_V1.txt')).read() if os.path.exists(os.path.join(W, 'INPUTS_V1.txt')) else ''
        card = os.path.join(T, 'alarm_process', CARD)
        if 'chain\t%s\t%s\n' % (hashlib.sha256(txt.encode()).hexdigest()[:16], chain) not in inp or 'card\t%s\t%s\n' % (CARD_SHA16, card) not in inp:
            fails.append('P2 INPUTS %s' % inp.strip()[:300])
    return fails


def run_path_mutants(txt):
    """every planted bug in the chain's path code must make chain_tests fail (4 at a time)"""
    import concurrent.futures as cf
    for a, b in PATH_MUTANTS:
        assert txt.count(a) == 1, ('path mutant target not found once', a)
    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda ab: bool(chain_tests(txt.replace(ab[0], ab[1], 1))), PATH_MUTANTS))
    for (a, b), caught in zip(PATH_MUTANTS, res):
        print('PATH MUTANT %-60s %s' % (b.strip()[:60], 'KILLED' if caught else 'SURVIVED'))
    print('PATH MUTANTS %d of %d killed' % (sum(res), len(res)))
    return len(res) - sum(res)


if __name__ == '__main__':
    sys.exit(main())
