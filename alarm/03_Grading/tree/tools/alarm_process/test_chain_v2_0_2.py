#!/usr/bin/env python3
"""test_chain_v2_0_2.py (SCOUT 31 Oct 2026, K12; TEST, NOT REVIEWED): tests of the GRADE chain alarm_grade_chain_v2_0_2_to20251231.sh, the
edition of v2_0_1 that runs the clean grader idea_to_grade_rel1 with its relative pins I2G_PINS_V2_REL1.json and detect_v2 (CLEAN_RELEASE_V1;
v2_0_1 was refused UNPINNED_MODULE from the install, GRADE job 20264797). test_chain_v2_0_1.py's tests on the new edition, every step a stub
(a stub interpreter answers each tool with the files the next step reads), plus the new lines: FEED_GATE must be set (empty: no gate) and
absolute, and goes to detection and the grade as one word (--gate=<file or empty>); the grade gets --pins <lab tree>/.../I2G_PINS_V2_REL1.json;
detect_v2, idea_to_grade_rel1 and the pins are checked by sha16 before any step (a changed one is refused, nothing runs); METRICS_V1 is
exported beside METRIC_TRAPS and CATALOGS (the lab tree's team/LAB3/METRICS_V1.tsv); INPUTS_<V>.txt keeps v2_0_1's lines and appends detect,
grade, pins and gate. Then planted bugs in the chain's lines: each must make a test fail. Seconds; temp folders only, removed after.
Run from an Alarm package:
  python3 -B <Alarm>/03_Grading/tree/tools/alarm_process/test_chain_v2_0_2.py"""
import os, re, sys, json, subprocess, tempfile, shutil, hashlib

HOME = os.path.dirname(os.path.abspath(__file__))
CHAIN = os.path.join(HOME, 'alarm_grade_chain_v2_0_2_to20251231.sh')
CHAIN_NAME = os.path.basename(CHAIN); CHAIN_AT = ('03_Grading', 'tree', 'tools', 'alarm_process')
CARD = 'alarm_card_v1_2_1.py'
DET = 'team/RESEARCH/tools/idea_to_grade/detect_v2.py'; I2G = 'team/RESEARCH/tools/idea_to_grade/idea_to_grade_rel1.py'
PINS = 'team/RESEARCH/tools/idea_to_grade/I2G_PINS_V2_REL1.json'
SHA_CHECKED = ('team/RESEARCH/tools/alarm_process/' + CARD, DET, I2G, PINS)
STAND_INS = ('team/RESEARCH/tools/event_outcomes/event_outcomes.py', 'team/RESEARCH/tools/alarm_process/make_random_v3_1.py',
             'team/RESEARCH/tools/alarm_process/menu_v2_1.py')
EXPECTED_TOOLS = ['idea_to_grade/detect_v2.py', 'idea_to_grade/detect_v2.py', 'idea_to_grade/idea_to_grade_rel1.py', 'alarm_process/make_random_v3_1.py',
                  'event_outcomes/event_outcomes.py', 'event_outcomes/event_outcomes.py', 'alarm_process/menu_v2_1.py', 'alarm_process/' + CARD]
SHA16 = {}                                             # set in main: the package's own files the chain checks
PATH_MUTANTS = [
    # v2_0_1's planted bugs, on the lines v2_0_2 keeps
    (' --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$h', ' --gate="$FEED_GATE" --out ${D}_$h'),
    (' --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins', ' --gate="$FEED_GATE" --pins'),
    ('F=$AL/01_Detection/tree;', 'F=$AL/03_Grading/tree;'), ('for k in AL PY LAB_DAYS;', 'for k in AL PY;'),
    ('[ -n "$v" ] && [ "${v#/}" != "$v" ] ||', '[ -n "$v" ] ||'), ('[ -f "$AL/_tools/settings_v1.py" ] && [ -d "$AL/settings" ] ||', 'true ||'),
    ('case "$(cd "$(dirname "$0")" && pwd -P)/" in', 'case "$(cd "$AL" && pwd -P)/" in'), ('$F/team/LAB3/code $IN $G', '$R/LAB3/code $IN $G'),
    ('run 1 "$LAB_DAYS"', 'run 1 "$F/lab_days"'), ('$PY -B $T/alarm_process/make_random_v3_1.py', '$PY -B $L2/make_random_v3.py'),
    ('$PY -B $T/alarm_process/menu_v2_1.py', '$PY -B $L2/menu_v2.py'),
    ('"$CARD_SHA" "$T/alarm_process/alarm_card_v1_2_1.py"', '"$CARD_SHA" "$T/alarm_process/alarm_card_v1_2.py"'),
    ('CARD_SHA=121304e1471d7e41', 'CARD_SHA=c3172f94e389cadb'),
    # v2_0_2's new lines
    ('--research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$h', '--research-window 20250901:$LAST --lab-root "$LAB_DAYS" --out ${D}_$h'),
    ('--lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins $PINS', '--lab-root "$LAB_DAYS" --pins $PINS'),
    ('--gate="$FEED_GATE" --pins $PINS --out', '--gate="$FEED_GATE" --out'),
    ('--gate="$FEED_GATE" --out ${D}_$h', '--gate "$FEED_GATE" --out ${D}_$h'),
    ('PINS=$T/idea_to_grade/I2G_PINS_V2_REL1.json', 'PINS=$T/idea_to_grade/I2G_PINS_V2.json'),
    ('I2G=$T/idea_to_grade/idea_to_grade_rel1.py;', 'I2G=$T/idea_to_grade/idea_to_grade.py;'),
    ('DET=$T/idea_to_grade/detect_v2.py;', 'DET=$T/idea_to_grade/detect.py;'),
    ('nice -n 10 $PY -B $DET ', 'nice -n 10 $PY -B $T/idea_to_grade/detect.py '),
    ('nice -n 10 $PY -B $I2G ', 'nice -n 10 $PY -B $T/idea_to_grade/idea_to_grade.py '),
    ('[ "${FEED_GATE+set}" = set ] ||', 'true ||'),
    ('[ -z "$FEED_GATE" ] || [ "${FEED_GATE#/}" != "$FEED_GATE" ] ||', 'true ||'),
    ('ckf $DET $DET_SHA; ', ''), ('ckf $I2G $I2G_SHA; ', ''), ('ckf $DET $DET_SHA; ckf $I2G $I2G_SHA; ckf $PINS $PINS_SHA', 'ckf $DET $DET_SHA; ckf $I2G $I2G_SHA'),
    ('DET_SHA=97a822a20e08088d;', 'DET_SHA=5ced7c1a40356a7f;'), ('PINS_SHA=17f89bef42400d38', 'PINS_SHA=7be3186f7957dde7'),
    ('export METRICS_V1=$F/team/LAB3/METRICS_V1.tsv ', 'export '),
    ('"$PINS_SHA" "$PINS" "${FEED_GATE:-none}" >>', '"$PINS_SHA" "$PINS" "${FEED_GATE:-none}" >/dev/null; : >>'),
    ('"$DET_SHA" "$DET" "$I2G_SHA" "$I2G"', '"$DET_SHA" "$DET" "$I2G_SHA" "$DET"'),
]

# ---------------------------------------------------------------- the whole chain, every step a stub
STUB_PY = r'''import sys, os, json
a = sys.argv[1:]
if a[:1] == ['-c']:
    os.execv(sys.executable, [sys.executable] + a)
tool, args = a[1], a[2:]
with open(os.environ['STUB_LOG'], 'a') as f:
    f.write(json.dumps({'tool': tool, 'args': args, 'env': {k: os.environ.get(k) for k in ('W', 'METRIC_TRAPS', 'CATALOGS', 'METRICS_V1')}}) + '\n')
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
    package's own bytes) and stand-ins for the rest; a stub interpreter outside it; a gate file; -> (AL, chain, PY, LAB, DEF, GATE)"""
    AL = os.path.join(tmp, 'Alarm'); os.makedirs(os.path.join(AL, 'settings')); os.makedirs(os.path.join(AL, '_tools'))
    shutil.copyfile(package_file('_tools', 'settings_v1.py'), os.path.join(AL, '_tools', 'settings_v1.py'))
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
    GATE = os.path.join(tmp, 'feed', 'BACKFILL_GATE.txt'); os.makedirs(os.path.dirname(GATE)); open(GATE, 'w').write('RUN\n')
    return AL, chain, PY, LAB, DEF, GATE


def run_chain(tmp, chain, env, DEF):
    W = os.path.join(tmp, 'W'); log = os.path.join(tmp, 'stub.log'); open(log, 'w').close()
    if os.path.exists(W):
        os.rename(W, W + '.%d' % len(os.listdir(tmp)))                    # a fresh W for every case (never deleted: the temp folder goes)
    e = {k: v for k, v in os.environ.items() if k not in ('AL', 'PY', 'LAB_DAYS', 'FEED_GATE', 'PARTS', 'BASE', 'SCREEN', 'LEAN', 'METRICS_V1')}
    e.update(STUB_LOG=log, LEAN='FADE', **env)
    p = subprocess.run(['bash', chain, 'V1', DEF, W], env=e, capture_output=True, text=True, cwd=tmp)
    return p.returncode, p.stdout + p.stderr, [json.loads(l) for l in open(log) if l.strip()], W


def whole_run(tmp, AL, chain, env, LAB, DEF, gate_word, txt):
    """P2/P3: one run with every step a stub; -> list of failures"""
    fails = []
    rc, out, calls, W = run_chain(tmp, chain, env, DEF)
    TR = os.path.join(AL, *LAB_TREE); T = os.path.join(TR, 'team', 'RESEARCH', 'tools')
    st = open(os.path.join(W, 'STATUS_V1.tsv')).read() if os.path.exists(os.path.join(W, 'STATUS_V1.tsv')) else ''
    tag = 'P2' if gate_word == '--gate=' else 'P3'
    if rc != 0 or not re.search(r'^done\t0\t', st, re.M):
        fails.append('%s run: rc %d %s' % (tag, rc, (out + st).strip()[-300:]))
    names = [os.path.relpath(c['tool'], T) for c in calls]
    if names != EXPECTED_TOOLS:
        fails.append('%s tools %s' % (tag, names))
    pins = os.path.join(TR, *PINS.split('/'))
    for c in calls:
        n = os.path.basename(c['tool']); a = c['args']
        if n.startswith(('detect', 'idea_to_grade')):
            if not (a.count('--lab-root') == 1 and a[a.index('--lab-root') + 1] == LAB):
                fails.append('%s %s lab root %s' % (tag, n, a)); break
            if [x for x in a if x.startswith('--gate')] != [gate_word]:
                fails.append('%s %s gate %s' % (tag, n, [x for x in a if x.startswith('--gate')])); break
        if n.startswith('idea_to_grade') and not (a.count('--pins') == 1 and a[a.index('--pins') + 1] == pins):
            fails.append('%s %s pins %s' % (tag, n, a)); break
        if n.startswith('detect') and '--pins' in a:
            fails.append('%s %s got --pins' % (tag, n)); break
        if n.startswith('event_outcomes') and a[2:4] != [LAB, os.path.join(TR, 'team', 'LAB3', 'code')]:
            fails.append('%s %s lab days, lab3 code %s' % (tag, n, a[2:4])); break
        roots = (AL, LAB, W, os.path.dirname(DEF))
        stray = [x for x in a if x.startswith('/') and not any(x == r or x.startswith(r + os.sep) for r in roots)]
        gw = [x[len('--gate='):] for x in a if x.startswith('--gate=') and x != '--gate=']
        stray += [x for x in gw if x != env.get('FEED_GATE')]
        if stray:
            fails.append('%s %s paths outside AL, LAB_DAYS, W, the run and the gate: %s' % (tag, n, stray)); break
        L2 = os.path.join(TR, 'team', 'RESEARCH', 'LEAD', 'loop2', 'defs')
        if c['env']['METRIC_TRAPS'] != os.path.join(L2, 'METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv') or c['env']['CATALOGS'] != ':'.join(
                [os.path.join(T, 'alarm_context', 'CTX_CATALOG_V1.tsv'), os.path.join(T, 'alarm_profile', 'EPI_CATALOG_V1.tsv'),
                 os.path.join(TR, 'team', 'LAB3', 'METRICS_HL_ADD_V1.tsv'), os.path.join(L2, 'METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv')]):
            fails.append('%s metric tables %s' % (tag, c['env'])); break
        if c['env']['METRICS_V1'] != os.path.join(TR, 'team', 'LAB3', 'METRICS_V1.tsv'):
            fails.append('%s METRICS_V1 %s' % (tag, c['env']['METRICS_V1'])); break
    inp = open(os.path.join(W, 'INPUTS_V1.txt')).read() if os.path.exists(os.path.join(W, 'INPUTS_V1.txt')) else ''
    card = os.path.join(T, 'alarm_process', CARD); det = os.path.join(TR, *DET.split('/')); i2g = os.path.join(TR, *I2G.split('/'))
    want = ['chain\t%s\t%s' % (hashlib.sha256(txt.encode()).hexdigest()[:16], chain), 'window\t20250910\t20251231',
            'card\t%s\t%s' % (SHA16[SHA_CHECKED[0]], card), 'input\t%s\t%s' % (hashlib.sha256(open(DEF, 'rb').read()).hexdigest()[:16], DEF),
            None, 'base\tnone lean FADE screen 0', 'detect\t%s\t%s' % (SHA16[DET], det), 'grade\t%s\t%s' % (SHA16[I2G], i2g),
            'pins\t%s\t%s' % (SHA16[PINS], pins), 'gate\t%s' % (env.get('FEED_GATE') or 'none')]
    got = inp.split('\n')
    if len(got) != len(want) + 1 or got[-1] != '' or any(w is not None and g != w for g, w in zip(got, want)) or not got[4].startswith('menu\t'):
        fails.append('%s INPUTS %s' % (tag, inp.strip()[:500]))
    return fails


def chain_tests(txt):
    """P1 the machine comes only from AL, PY, LAB_DAYS (absolute; AL an Alarm package holding this chain) and FEED_GATE (set; empty or
    absolute), and the three new files must be the package's bytes, else refused before any step; P2 a whole run, no gate (FEED_GATE
    set and empty); P3 a whole run with a gate file"""
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        AL, chain, PY, LAB, DEF, GATE = sandbox(tmp, txt)
        good = {'AL': AL, 'PY': PY, 'LAB_DAYS': LAB, 'FEED_GATE': ''}
        cases = [('AL unset', {k: v for k, v in good.items() if k != 'AL'}, 'NO_AL'), ('PY relative', dict(good, PY='python3'), 'NO_PY'),
                 ('LAB_DAYS unset', {k: v for k, v in good.items() if k != 'LAB_DAYS'}, 'NO_LAB_DAYS'),
                 ('LAB_DAYS relative', dict(good, LAB_DAYS='lab_days'), 'NO_LAB_DAYS'),
                 ('AL not a package', dict(good, AL=os.path.join(tmp, 'run')), 'NOT_AN_ALARM_FOLDER'),
                 ('FEED_GATE unset', {k: v for k, v in good.items() if k != 'FEED_GATE'}, 'NO_FEED_GATE'),
                 ('FEED_GATE relative', dict(good, FEED_GATE='feed/BACKFILL_GATE.txt'), 'NO_FEED_GATE')]
        for label, env, msg in cases:
            rc, out, calls, W = run_chain(tmp, chain, env, DEF)
            if rc != 2 or msg not in out or calls:
                fails.append('P1 %s: rc %d calls %d out %s' % (label, rc, len(calls), out.strip()[-160:]))
        other = os.path.join(tmp, 'elsewhere', CHAIN_NAME); os.makedirs(os.path.dirname(other)); shutil.copyfile(chain, other)
        rc, out, calls, W = run_chain(tmp, other, good, DEF)
        if rc != 2 or 'CHAIN_OUTSIDE_ALARM' not in out or calls:
            fails.append('P1 chain outside AL: rc %d calls %d out %s' % (rc, len(calls), out.strip()[-160:]))
        for rel in (DET, I2G, PINS):                                           # a changed file the chain pins: refused, nothing runs
            p = os.path.join(AL, *LAB_TREE, *rel.split('/')); keep = open(p, 'rb').read()
            open(p, 'ab').write(b'\n# changed\n')
            rc, out, calls, W = run_chain(tmp, chain, good, DEF)
            open(p, 'wb').write(keep)
            if rc != 2 or 'SHA_MISMATCH' not in out or calls:
                fails.append('P1 changed %s: rc %d calls %d out %s' % (os.path.basename(rel), rc, len(calls), out.strip()[-160:]))
        fails += whole_run(tmp, AL, chain, good, LAB, DEF, '--gate=', txt)
        fails += whole_run(tmp, AL, chain, dict(good, FEED_GATE=GATE), LAB, DEF, '--gate=' + GATE, txt)
    return fails


def run_path_mutants(txt):
    """every planted bug in the chain's lines must make chain_tests fail (4 at a time)"""
    import concurrent.futures as cf
    for a, b in PATH_MUTANTS:
        assert txt.count(a) == 1, ('planted bug target not found once', a)
    with cf.ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda ab: bool(chain_tests(txt.replace(ab[0], ab[1], 1))), PATH_MUTANTS))
    for (a, b), caught in zip(PATH_MUTANTS, res):
        print('PLANTED BUG %-70s %s' % ((b.strip() or '(line removed)')[:70], 'KILLED' if caught else 'SURVIVED'))
    print('PLANTED BUGS %d of %d killed' % (sum(res), len(res)))
    return len(res) - sum(res)


def main():
    for rel in SHA_CHECKED:
        SHA16[rel] = hashlib.sha256(open(package_file(*LAB_TREE, *rel.split('/')), 'rb').read()).hexdigest()[:16]
    txt = open(CHAIN).read()
    f = chain_tests(txt)
    print('CHAIN TESTS', 'PASS' if not f else 'FAIL %s' % f)
    pm = run_path_mutants(txt)
    return 1 if f or pm else 0


if __name__ == '__main__':
    sys.exit(main())
