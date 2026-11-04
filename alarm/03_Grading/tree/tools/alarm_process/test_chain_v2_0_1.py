#!/usr/bin/env python3
"""test_chain_v2_0_1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): tests of the paths-only GRADE chain alarm_grade_chain_v2_0_1_to20251231.sh
(CLEAN_RELEASE_V1): the whole chain with every step a stub (a stub interpreter answers each tool with the files the next step reads): the
machine comes only from AL, PY and LAB_DAYS (absolute; AL an Alarm package holding this chain), else it is refused before any step; every
step comes from the lab tree <AL>/01_Detection/tree; the lab days go to detection, the grade and Outcomes; the lab3 code and the metric tables
come from the lab tree; no other root appears in any argument; INPUTS names this chain and its card. Then planted bugs in the chain's path
code: each must make a test fail. Seconds; temp folders only, removed after. Run from an Alarm package:
  python3 -B <Alarm>/03_Grading/tree/tools/alarm_process/test_chain_v2_0_1.py"""
import os, re, sys, json, subprocess, tempfile, shutil, hashlib

HOME = os.path.dirname(os.path.abspath(__file__))
CHAIN = os.path.join(HOME, 'alarm_grade_chain_v2_0_1_to20251231.sh')
CHAIN_NAME = os.path.basename(CHAIN); CHAIN_AT = ('03_Grading', 'tree', 'tools', 'alarm_process')
CARD = 'alarm_card_v1_2_1.py'
SHA_CHECKED = ('team/RESEARCH/tools/alarm_process/' + CARD,)
STAND_INS = ('team/RESEARCH/tools/idea_to_grade/detect.py', 'team/RESEARCH/tools/idea_to_grade/idea_to_grade.py', 'team/RESEARCH/tools/event_outcomes/event_outcomes.py',
             'team/RESEARCH/tools/alarm_process/make_random_v3_1.py', 'team/RESEARCH/tools/alarm_process/menu_v2_1.py')
EXPECTED_TOOLS = ['idea_to_grade/detect.py', 'idea_to_grade/detect.py', 'idea_to_grade/idea_to_grade.py', 'alarm_process/make_random_v3_1.py',
                  'event_outcomes/event_outcomes.py', 'event_outcomes/event_outcomes.py', 'alarm_process/menu_v2_1.py', 'alarm_process/' + CARD]
CARD_SHA16 = None                                      # set in main: the package's own card
PATH_MUTANTS = [(' --lab-root "$LAB_DAYS" --out ${D}_$h', ' --out ${D}_$h'), (' --lab-root "$LAB_DAYS" --out $W/gradeL', ' --out $W/gradeL'), ('F=$AL/01_Detection/tree;', 'F=$AL/03_Grading/tree;'), ('for k in AL PY LAB_DAYS;', 'for k in AL PY;'), ('[ -n "$v" ] && [ "${v#/}" != "$v" ] ||', '[ -n "$v" ] ||'), ('[ -f "$AL/_tools/settings_v1.py" ] && [ -d "$AL/settings" ] ||', 'true ||'), ('case "$(cd "$(dirname "$0")" && pwd -P)/" in', 'case "$(cd "$AL" && pwd -P)/" in'), ('$F/team/LAB3/code $IN $G', '$R/LAB3/code $IN $G'), ('run 1 "$LAB_DAYS"', 'run 1 "$F/lab_days"'), ('$PY -B $T/alarm_process/make_random_v3_1.py', '$PY -B $L2/make_random_v3.py'), ('$PY -B $T/alarm_process/menu_v2_1.py', '$PY -B $L2/menu_v2.py'), ('"$CARD_SHA" "$T/alarm_process/alarm_card_v1_2_1.py"', '"$CARD_SHA" "$T/alarm_process/alarm_card_v1_2.py"'), ('CARD_SHA=121304e1471d7e41', 'CARD_SHA=c3172f94e389cadb')]

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


def main():
    global CARD_SHA16
    CARD_SHA16 = hashlib.sha256(open(package_file(*LAB_TREE, *SHA_CHECKED[0].split('/')), 'rb').read()).hexdigest()[:16]
    txt = open(CHAIN).read()
    f = chain_tests(txt)
    print('CHAIN TESTS', 'PASS' if not f else 'FAIL %s' % f)
    pm = run_path_mutants(txt)
    return 1 if f or pm else 0


if __name__ == '__main__':
    sys.exit(main())
