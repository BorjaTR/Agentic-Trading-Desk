#!/usr/bin/env python3
"""test_month_parts_v1_2.py (SCOUT 31 Oct 2026, K12; TEST, NOT REVIEWED): tests of the MONTH chain alarm_grade_chain_v2_2_2_to20260430.sh,
the edition of v2_2_1 that runs the clean aw1 grader idea_to_grade_aw1_rel1 with its relative pins I2G_PINS_AW1_REL1.json and the clean
aw1 detector detect_aw1_rel1 (CLEAN_RELEASE_V1). Built on test_month_parts_v1_1.py (K4), whose tests it imports from this folder and runs
on the new chain: the step-1 tests and their 19 planted bugs (with fake_detect_v2.py, which takes the new --gate= word), then the whole
chain with every step a stub and K4's planted bugs on the lines v2_2_2 keeps. Then the new lines: FEED_GATE must be set (empty: no gate)
and absolute, and goes to detection and the grade as one word; the grade gets --pins <lab tree>/.../alarm_process/I2G_PINS_AW1_REL1.json;
detect_aw1_rel1, idea_to_grade_aw1_rel1 and the pins are checked by sha16 before any step (a changed one is refused, nothing runs);
METRICS_V1 is exported beside METRIC_TRAPS and CATALOGS; INPUTS_<V>.txt holds v2_2_1's 12 lines with the new files named, then a gate
line. Then planted bugs in those lines: each must make a test fail. Seconds; temp folders only, removed after.
  python3 -B <Alarm>/03_Grading/tree/tools/month_parts/tests/test_month_parts_v1_2.py      (exit 0: every test passes, every bug caught)
  [--only step1|chain]   one half only (step1: the step-1 tests and their 19 planted bugs; chain: the rest), for a short session"""
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('test_month_parts_v1_1_k4', os.path.join(HERE, 'test_month_parts_v1_1.py'))
K4 = importlib.util.module_from_spec(sp); sp.loader.exec_module(K4)
K4.CHAIN = os.path.join(K4.HOME, 'alarm_grade_chain_v2_2_2_to20260430.sh'); K4.CHAIN_NAME = os.path.basename(K4.CHAIN)
K4.FAKE = os.path.join(HERE, 'fake_detect_v2.py')
AP = 'team/RESEARCH/tools/alarm_process/'
DET, I2G, PINS = AP + 'detect_aw1_rel1.py', AP + 'idea_to_grade_aw1_rel1.py', AP + 'I2G_PINS_AW1_REL1.json'
K4.SHA_CHECKED = tuple(AP + x for x in (K4.CARD, 'detect_aw1_rel1.py', 'idea_to_grade_aw1_rel1.py', 'I2G_PINS_AW1_REL1.json',
                                        'event_outcomes_aw1.py', 'RELEASE_event_outcomes_AW1.json', 'WINDOWS_ALARM_V1.tsv'))
K4.EXPECTED_TOOLS = ['alarm_process/detect_aw1_rel1.py'] * 26 + ['alarm_process/' + x for x in ('idea_to_grade_aw1_rel1.py', 'make_random_v3_1.py',
                     'event_outcomes_aw1.py', 'event_outcomes_aw1.py', 'menu_v2_1.py', K4.CARD)]
assert "('W', 'METRIC_TRAPS', 'CATALOGS')" in K4.STUB_PY
K4.STUB_PY = K4.STUB_PY.replace("('W', 'METRIC_TRAPS', 'CATALOGS')", "('W', 'METRIC_TRAPS', 'CATALOGS', 'METRICS_V1')")
UNSET = object()


def run_chain(tmp, chain, env, DEF):
    """K4's run_chain with FEED_GATE: given (set and empty unless the case names one), or left out when the case says UNSET; a fresh W"""
    W = os.path.join(tmp, 'W'); log = os.path.join(tmp, 'stub.log'); open(log, 'w').close()
    if os.path.exists(W):
        os.rename(W, W + '.%d' % len(os.listdir(tmp)))
    e = {k: v for k, v in os.environ.items() if k not in ('AL', 'PY', 'LAB_DAYS', 'PARTS', 'BASE', 'SCREEN', 'LEAN', 'FEED_GATE', 'METRICS_V1')}
    env = dict(env); g = env.pop('FEED_GATE', '')
    e.update(STUB_LOG=log, LEAN='FADE', **env)
    if g is not UNSET:
        e['FEED_GATE'] = g
    p = subprocess.run(['bash', chain, 'V1', DEF, W], env=e, capture_output=True, text=True, cwd=tmp)
    return p.returncode, p.stdout + p.stderr, [json.loads(l) for l in open(log) if l.strip()], W


K4.run_chain = run_chain                                   # K4's chain tests run with FEED_GATE set and empty


def new_tests(txt):
    """the new lines: FEED_GATE, the three pinned files, --gate= and --pins, METRICS_V1, INPUTS"""
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        AL, chain, PY, LAB, DEF = K4.sandbox(tmp, txt)
        GATE = os.path.join(tmp, 'feed', 'BACKFILL_GATE.txt'); os.makedirs(os.path.dirname(GATE)); open(GATE, 'w').write('RUN\n')
        good = {'AL': AL, 'PY': PY, 'LAB_DAYS': LAB, 'FEED_GATE': ''}
        for label, env, msg in (('FEED_GATE unset', dict(good, FEED_GATE=UNSET), 'NO_FEED_GATE'),
                                ('FEED_GATE relative', dict(good, FEED_GATE='feed/BACKFILL_GATE.txt'), 'NO_FEED_GATE')):
            rc, out, calls, W = run_chain(tmp, chain, env, DEF)
            if rc != 2 or msg not in out or calls:
                fails.append('N1 %s: rc %d calls %d out %s' % (label, rc, len(calls), out.strip()[-160:]))
        for rel in (DET, I2G, PINS):
            p = os.path.join(AL, *K4.LAB_TREE, *rel.split('/')); keep = open(p, 'rb').read()
            open(p, 'ab').write(b'\n# changed\n')
            rc, out, calls, W = run_chain(tmp, chain, good, DEF)
            open(p, 'wb').write(keep)
            if rc != 2 or 'SHA_MISMATCH' not in out or calls:
                fails.append('N1 changed %s: rc %d calls %d out %s' % (os.path.basename(rel), rc, len(calls), out.strip()[-160:]))
        TR = os.path.join(AL, *K4.LAB_TREE); T = os.path.join(TR, 'team', 'RESEARCH', 'tools'); A = os.path.join(T, 'alarm_process')
        for gate in ('', GATE):
            rc, out, calls, W = run_chain(tmp, chain, dict(good, FEED_GATE=gate), DEF)
            tag = 'N2 gate %s' % (gate or '(empty)')
            st = open(os.path.join(W, 'STATUS_V1.tsv')).read() if os.path.exists(os.path.join(W, 'STATUS_V1.tsv')) else ''
            if rc != 0 or not re.search(r'^done\t0\t', st, re.M):
                fails.append('%s run: rc %d %s' % (tag, rc, (out + st).strip()[-200:])); continue
            for c in calls:
                n = os.path.basename(c['tool']); a = c['args']
                if n.startswith(('detect', 'idea_to_grade')) and [x for x in a if x.startswith('--gate')] != ['--gate=' + gate]:
                    fails.append('%s %s gate words %s' % (tag, n, [x for x in a if x.startswith('--gate')])); break
                if n.startswith('idea_to_grade') and not (a.count('--pins') == 1 and a[a.index('--pins') + 1] == os.path.join(TR, *PINS.split('/'))):
                    fails.append('%s %s pins %s' % (tag, n, a)); break
                if n.startswith(('detect', 'make_random', 'event_outcomes', 'menu', 'alarm_card')) and '--pins' in a:
                    fails.append('%s %s got --pins' % (tag, n)); break
                if c['env'].get('METRICS_V1') != os.path.join(TR, 'team', 'LAB3', 'METRICS_V1.tsv'):
                    fails.append('%s METRICS_V1 %s' % (tag, c['env'].get('METRICS_V1'))); break
            sha = lambda rel: hashlib.sha256(open(os.path.join(TR, *rel.split('/')), 'rb').read()).hexdigest()[:16]
            inp = open(os.path.join(W, 'INPUTS_V1.txt')).read().split('\n') if os.path.exists(os.path.join(W, 'INPUTS_V1.txt')) else []
            want = {6: 'windows\t%s\t%s' % (sha(AP + 'WINDOWS_ALARM_V1.tsv'), os.path.join(A, 'WINDOWS_ALARM_V1.tsv')),
                    7: 'detect\t%s\t%s' % (sha(DET), os.path.join(TR, *DET.split('/'))), 8: 'grade\t%s\t%s' % (sha(I2G), os.path.join(TR, *I2G.split('/'))),
                    9: 'pins\t%s\t%s' % (sha(PINS), os.path.join(TR, *PINS.split('/'))),
                    10: 'outcomes\t%s\t%s' % (sha(AP + 'event_outcomes_aw1.py'), os.path.join(A, 'event_outcomes_aw1.py')),
                    11: 'release\t%s\t%s' % (sha(AP + 'RELEASE_event_outcomes_AW1.json'), os.path.join(A, 'RELEASE_event_outcomes_AW1.json')),
                    12: 'gate\t%s' % (gate or 'none')}
            if len(inp) != 14 or inp[-1] != '' or any(inp[i] != w for i, w in want.items()) or [l.split('\t')[0] for l in inp[:6]] != ['chain', 'window', 'card', 'input', 'menu', 'base']:
                fails.append('%s INPUTS %s' % (tag, inp))
    return fails


STEP1_MUTANTS = [('(i+1)*k//n]', '(i+1)*k//n-1]'), ('seq 0 $((NP-1))', 'seq 1 $((NP-1))'), ('seq 0 $((NP-1))', 'seq 0 3'),
                 ("-k2,2n -k1,1", "-k2,2 -k1,1"), ("sort -t$'\\t' -k2,2n -k1,1", "sort -s -t$'\\t' -k2,2n"), ('tail -n +2; done', 'tail -n +3; done'),
                 ('${PARTS:-26}', '${PARTS:-8}'), ('^([2-9]|1[0-9]|2[0-6])$', '^([1-9]|1[0-9]|2[0-6])$'), ('^([2-9]|1[0-9]|2[0-6])$', '^([2-9]|[1-2][0-9])$'),
                 ('(2 to 26)"; exit 2; }', '(2 to 26)"; NP=4; }'), ("c[i*k//n:", "c[i*k//n+1:"),
                 ('for h in $PL; do', 'for h in A B; do'), ('PL="$PL $h"', 'PL="$h"'), ('LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Z)', 'LET=(A B C D E F G H I J K L M N O P Q R S T U V W X Y Y)'),
                 ("grep '^#' ${D}_A/EVENTS.tsv; echo", "grep '^#' ${D}_B/EVENTS.tsv; echo"),
                 ('  [ -n "$C" ] || { st detect_$h 2 0 "EMPTY_PART $i of $NP"; exit 3; }\n', ''), ('--coins $C', '--coins ALL'),
                 ('--workers 3', '--workers 8'), ('[ $rc -eq 0 ] && [ -f ${D}_$h/EVENTS.tsv ] || exit 3', '[ -f ${D}_$h/EVENTS.tsv ] || exit 3')]
K4.PATH_MUTANTS = [(' --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$h', ' --gate="$FEED_GATE" --out ${D}_$h'),
                   (' --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins', ' --gate="$FEED_GATE" --pins'),
                   ('F=$AL/01_Detection/tree;', 'F=$AL/03_Grading/tree;'), ('for k in AL PY LAB_DAYS;', 'for k in AL PY;'),
                   ('[ -n "$v" ] && [ "${v#/}" != "$v" ] ||', '[ -n "$v" ] ||'), ('[ -f "$AL/_tools/settings_v1.py" ] && [ -d "$AL/settings" ] ||', 'true ||'),
                   ('case "$(cd "$(dirname "$0")" && pwd -P)/" in', 'case "$(cd "$AL" && pwd -P)/" in'), ('$F/team/LAB3/code $IN $G', '$R/LAB3/code $IN $G'),
                   ('run 0 "$LAB_DAYS"', 'run 0 "$F/lab_days"'), ('$PY -B $AP/make_random_v3_1.py', '$PY -B $L2/make_random_v3.py'),
                   ('$PY -B $AP/menu_v2_1.py', '$PY -B $L2/menu_v2.py'), ('"$CARD_SHA" "$AP/alarm_card_v1_3_1.py"', '"$CARD_SHA" "$AP/alarm_card_v1_3.py"'),
                   ('CARD_SHA=3c496708f9d44651', 'CARD_SHA=a616c4378a02852b')]
NEW_MUTANTS = [('--research-window 20250901:$LAST --lab-root "$LAB_DAYS" --gate="$FEED_GATE" --out ${D}_$h', '--research-window 20250901:$LAST --lab-root "$LAB_DAYS" --out ${D}_$h'),
               ('--lab-root "$LAB_DAYS" --gate="$FEED_GATE" --pins $PINS', '--lab-root "$LAB_DAYS" --pins $PINS'),
               ('--gate="$FEED_GATE" --pins $PINS --out', '--gate="$FEED_GATE" --out'), ('--gate="$FEED_GATE" --out ${D}_$h', '--gate "$FEED_GATE" --out ${D}_$h'),
               ('PINS=$AP/I2G_PINS_AW1_REL1.json', 'PINS=$AP/I2G_PINS_AW1.json'), ('DET=$AP/detect_aw1_rel1.py;', 'DET=$AP/detect_aw1.py;'),
               ('I2G=$AP/idea_to_grade_aw1_rel1.py;', 'I2G=$AP/idea_to_grade_aw1.py;'), ('[ "${FEED_GATE+set}" = set ] ||', 'true ||'),
               ('[ -z "$FEED_GATE" ] || [ "${FEED_GATE#/}" != "$FEED_GATE" ] ||', 'true ||'),
               ('ckf detect_aw1_rel1.py $DET_SHA; ', ''), ('ckf idea_to_grade_aw1_rel1.py $I2G_SHA; ', ''), ('; ckf I2G_PINS_AW1_REL1.json $PINS_SHA', ''),
               ('DET_SHA=932bd2957cd3592d;', 'DET_SHA=482a4a1eaf1faff5;'), ('I2G_SHA=d50d277f44aad95f;', 'I2G_SHA=a98936da5aaf93b4;'),
               ('PINS_SHA=82a0d10372bbe744;', 'PINS_SHA=c0c523ed00403f58;'), ('export METRICS_V1=$F/team/LAB3/METRICS_V1.tsv ', 'export '),
               ("printf 'gate\\t%s\\n' \"${FEED_GATE:-none}\" >> \"$W/INPUTS_${V}.txt\"\n", ''), ('"$PINS_SHA" "$PINS" "$EO_SHA"', '"$PINS_SHA" "$AP/I2G_PINS_AW1.json" "$EO_SHA"')]


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    K4.CARD_SHA16 = hashlib.sha256(open(K4.package_file(*K4.LAB_TREE, *K4.SHA_CHECKED[0].split('/')), 'rb').read()).hexdigest()[:16]
    txt = open(K4.CHAIN).read()
    f, missed, pf, nf, pm, n_missed = [], [], [], [], 0, 0
    if only in (None, 'step1'):
        f, missed = step1(txt)
    if only in (None, 'chain'):
        pf, nf, pm, n_missed = chain_part(txt)
    if only is None:
        total = len(STEP1_MUTANTS) + len(K4.PATH_MUTANTS) + len(NEW_MUTANTS)
        print('PLANTED BUGS %d of %d killed' % (total - len(missed) - pm - n_missed, total))
    return 1 if f or missed or pf or nf or pm or n_missed else 0


def step1(txt):
    os.environ['FEED_GATE'] = ''                                   # the step-1 block reads "$FEED_GATE" (set -u): set and empty
    f = K4.run_tests(txt)
    print('STEP-1 TESTS', 'PASS' if not f else 'FAIL %s' % f)
    missed = []
    for a, b in STEP1_MUTANTS:
        assert txt.count(a) >= 1, ('planted bug target missing', a)
        try:
            caught = bool(K4.run_tests(txt.replace(a, b, 1)))
        except Exception:
            caught = True
        print('STEP-1 PLANTED BUG %-48s %s' % (a.strip()[:48], 'KILLED' if caught else 'SURVIVED'))
        if not caught: missed.append(a)
    del os.environ['FEED_GATE']
    print('STEP-1 PLANTED BUGS %d of %d killed' % (len(STEP1_MUTANTS) - len(missed), len(STEP1_MUTANTS)))
    return f, missed


def chain_part(txt):
    pf = K4.chain_tests(txt)
    print('CHAIN TESTS (K4)', 'PASS' if not pf else 'FAIL %s' % pf)
    nf = new_tests(txt)
    print('CHAIN TESTS (new lines)', 'PASS' if not nf else 'FAIL %s' % nf)
    pm = K4.run_path_mutants(txt)
    n_missed = 0
    for a, b in NEW_MUTANTS:
        assert txt.count(a) == 1, ('planted bug target not found once', a)
        t2 = txt.replace(a, b, 1)
        caught = bool(new_tests(t2) or K4.chain_tests(t2))
        print('NEW PLANTED BUG %-70s %s' % ((b.strip().split('\n')[-1] or '(line removed)')[:70], 'KILLED' if caught else 'SURVIVED'))
        n_missed += not caught
    print('NEW PLANTED BUGS %d of %d killed' % (len(NEW_MUTANTS) - n_missed, len(NEW_MUTANTS)))
    return pf, nf, pm, n_missed


if __name__ == '__main__':
    sys.exit(main())
