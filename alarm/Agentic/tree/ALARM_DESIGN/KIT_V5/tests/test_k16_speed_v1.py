"""test_k16_speed_v1.py (SCOUT K16, 31 Oct 2026; TEST, NOT REVIEWED): tests of the V1_7 speed editions (K16 T5, T6, T8; SCOUT 31 Oct with
the fixes of the reviews REV1 and REV2): chains v2_0_4 and v2_2_4, JOB_GRADE_V9, JOB_MONTH_V9, queue_job_v7.py and the two V9 job tests.
  C1   k16_speed_contract.py remakes the seven files from their V1_6 parents in this package byte for byte.
  B1   v2_2_4's detection, run from the chain's own text with a planted detector: a definition of any mode but SERIAL_FORCED runs in 2
       parts, merged; the census passes; the fire list is every fire sorted by t then coin in byte order (LC_ALL=C).
  B2   a part refused with WORKER_RSS_CAP is re-split alone (the other part untouched) into new folders; its folder is kept and never
       merged; the fire list is byte-equal to B1's.
  B3   a SERIAL_FORCED definition runs in 26 parts up front; the same fire list.
  B4   a fire of a coin outside its part: the census refuses, exit 3, no fire list.
  B5   a roster that repeats a coin: the census refuses, exit 3.
  B6   any other refusal (GATE_NOT_RUN): exit 3, no re-split.
  B7   a re-split part refused again: exit 3.
  B8   a part refused at the 26-part size: no finer split, exit 3.
  B9   PARTS=4 from the caller: 4 parts; the same fire list.
  B10  the merge sorts with LC_ALL=C (the chain's text).
  B11  the census alone, on planted tables: a coin in no part, a coin not in the roster, a coin in two parts, a part with no COMPLETE run,
       a fire outside its part: each refused; the good table passes.
  B12  v2_0_4 runs Outcomes as run 3 on both lists (T5), nothing else changed (C1).
  B13  JOB_GRADE_V9 and JOB_MONTH_V9 declare # CORES 3 in header lines 1-10 and run du once (T8); JOB_MONTH_V9 sets PARTS empty.
Then planted bugs in v2_2_4's detection text: each must make its tests fail. The detector, the roster and the definitions are planted
(temp folders, removed after); with an en_US UTF-8 locale on the machine, B1-B9 run under it, so a sort without LC_ALL=C would fail.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_k16_speed_v1.py"""
import hashlib, importlib.util, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sp = importlib.util.spec_from_file_location('k16_speed_contract', os.path.join(HERE, 'k16_speed_contract.py'))
assert sp and sp.loader   # V1_13: pyright (an Optional spec)
CT = importlib.util.module_from_spec(sp); sp.loader.exec_module(CT)
PY = sys.executable
HEAD, TAIL = '# 1 detect (K16 T6, v2_2_4)', "grep -v '^#' $D/EVENTS.tsv > $LIST\n"
ROSTER = ['1INCH', 'AAVE', 'A_B', 'Ab', 'B1', 'B_1', 'aZ', 'a_z'] + ['C%02d' % i for i in range(44)]     # 52 coins, as the real roster

FAKE = r'''import argparse, json, os, sys
def load_definition(p):
    return json.load(open(p)), {}
def parallel_mode(d):
    return d.get('mode', 'CHUNKED'), ''
def fires(c):
    h = sum(ord(x) * (i + 7) for i, x in enumerate(c))
    return [(1000, 1), (1060 + 60 * (h % 50), -1 if h % 2 else 1)]
def main():
    p = argparse.ArgumentParser()
    for k in ('--definition', '--roster', '--coins', '--first', '--last', '--research-window', '--lab-root', '--gate', '--out', '--workers'):
        p.add_argument(k)
    a = p.parse_args(); d = json.load(open(a.definition)); coins = a.coins.split(',')
    os.makedirs(a.out)
    open(os.path.join(a.out, 'TRIED.txt'), 'w').write(a.coins + '\n')
    if d.get('refuse') and d['refuse'][1] in coins:
        print('REFUSED %s: planted' % d['refuse'][0], file=sys.stderr); return 2
    if len(coins) > d.get('cap_over', 10 ** 6) and d.get('cap_coin', coins[0]) in coins:
        open(os.path.join(a.out, 'EVENTS.tsv'), 'w').write('coin\tt\tside\n%s\t7\t1\n' % coins[0])   # a partial write a refused run might leave
        print('REFUSED WORKER_RSS_CAP: 2150924288 bytes', file=sys.stderr); return 2
    rows = [(c, t, s) for c in coins for t, s in fires(c)]
    if d.get('foreign') and d['foreign'][0] in coins:
        rows.append((d['foreign'][1], 5, 1))
    with open(os.path.join(a.out, 'EVENTS.tsv'), 'w') as f:
        f.write('# planted detector: coins %s\ncoin\tt\tside\n' % a.coins)
        for c, t, s in rows:
            f.write('%s\t%d\t%d\n' % (c, t, s))
    json.dump({'status': 'COMPLETE', 'memory': {}, 'sources': {}, 'code_sha16': {}}, open(os.path.join(a.out, 'DETECT_RUN.json'), 'w'))
    print(json.dumps({'status': 'COMPLETE'})); return 0
if __name__ == '__main__':
    sys.exit(main())
'''

HARNESS = r'''set -uo pipefail
PY=@PY@; DET=@DET@; DEF=@DEF@; ROSTER=@ROSTER@; FIRST=20250910; LAST=20260430; LAB_DAYS=@W@/lab; FEED_GATE=
V=T; W=@W@; D=$W/det_${V}_v1; LIST=$W/${V}_FIRES_V1_LIST.tsv
S=$W/STATUS_${V}.tsv; printf 'step\trc\tseconds\tout\tutc\n' > "$S"; st(){ printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$(date -u +%FT%TZ)" >> "$S"; }
'''


def fake_fires(c):
    h = sum(ord(x) * (i + 7) for i, x in enumerate(c))
    return [(1000, 1), (1060 + 60 * (h % 50), -1 if h % 2 else 1)]


def expected(roster):
    rows = sorted(((c, t, s) for c in roster for t, s in fake_fires(c)), key=lambda r: (r[1], r[0].encode()))
    return 'coin\tt\tside\n' + ''.join('%s\t%d\t%d\n' % r for r in rows)


def block_of(text):
    a = text.index(HEAD); b = text.index(TAIL, a) + len(TAIL)
    return text[a:b]


def locale_env():
    env = {k: v for k, v in os.environ.items() if k not in ('PARTS', 'LC_ALL', 'LC_COLLATE', 'LANG')}
    try:
        have = subprocess.run(['locale', '-a'], capture_output=True, text=True).stdout.split()
    except OSError:
        have = []
    for loc in ('en_US.UTF-8', 'en_US.utf8'):
        if loc in have:
            env['LC_ALL'] = loc; return env, loc
    return env, None


ENV, LOC = locale_env()


def run_block(block, tmp, name, definition, roster=ROSTER, parts=None):
    """the chain's detection text in a harness with the planted detector -> (rc, W)"""
    w = os.path.join(tmp, name); os.makedirs(os.path.join(w, 'lab'))
    det = os.path.join(tmp, 'fake_detect.py')
    if not os.path.exists(det):
        open(det, 'w').write(FAKE)
    dp = os.path.join(w, 'DEF.json'); json.dump(definition, open(dp, 'w'))
    rp = os.path.join(w, 'ROSTER.json'); json.dump({'coins': roster}, open(rp, 'w'))
    sh = HARNESS.replace('@PY@', PY).replace('@DET@', det).replace('@DEF@', dp).replace('@ROSTER@', rp).replace('@W@', w) + block
    open(os.path.join(w, 'harness.sh'), 'w').write(sh)
    env = dict(ENV)
    if parts:
        env['PARTS'] = str(parts)
    r = subprocess.run(['bash', os.path.join(w, 'harness.sh')], capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
    return r.returncode, w


def table(w):
    p = os.path.join(w, 'DETECT_PARTS_T.tsv')
    if not os.path.isfile(p):
        return []
    lines = open(p).read().splitlines()
    return [dict(zip(lines[0].split('\t'), l.split('\t'))) for l in lines[1:]]


def status(w):
    p = os.path.join(w, 'STATUS_T.tsv')
    return [l.split('\t') for l in open(p).read().splitlines()[1:]] if os.path.isfile(p) else []


def step_rc(w, step):
    return [s[1] for s in status(w) if s[0] == step]


def listed(w):
    p = os.path.join(w, 'T_FIRES_V1_LIST.tsv')
    return open(p).read() if os.path.isfile(p) else None


def t_b1(block, tmp):
    f = []; rc, w = run_block(block, tmp, 'b1', {'mode': 'CHUNKED'})
    rows = table(w); plan = [s[3] for s in status(w) if s[0] == 'detect_plan']
    if rc != 0: f.append('B1 rc %d' % rc)
    if plan != ['2 parts: parallel_mode CHUNKED']: f.append('B1 plan %s' % plan)
    if [(r['part'], r['use']) for r in rows] != [('A', 'merged'), ('B', 'merged')]: f.append('B1 parts %s' % [(r['part'], r['use']) for r in rows])
    if step_rc(w, 'census') != ['0']: f.append('B1 census %s' % step_rc(w, 'census'))
    if listed(w) != expected(ROSTER): f.append('B1 the fire list is not every fire sorted by t then coin (bytes)')
    return f


def t_b2(block, tmp):
    f = []; rc, w = run_block(block, tmp, 'b2', {'mode': 'CHUNKED', 'cap_over': 20, 'cap_coin': ROSTER[0]})
    rows = table(w); uses = [(r['part'], r['use']) for r in rows]
    want = [('A', 'refused_kept_unmerged')] + [('A%d' % j, 'merged') for j in range(1, 14)] + [('B', 'merged')]
    if rc != 0: f.append('B2 rc %d' % rc)
    if uses != want: f.append('B2 parts %s' % uses)
    if step_rc(w, 'resplit_A') != ['0']: f.append('B2 resplit_A %s' % step_rc(w, 'resplit_A'))
    if any(s[0].startswith('resplit_') and s[0] != 'resplit_A' for s in status(w)): f.append('B2 another part was re-split')
    if not os.path.isfile(os.path.join(w, 'det_T_v1_A', 'TRIED.txt')) or not os.path.isfile(os.path.join(w, 'det_T_v1_A.log')):
        f.append('B2 the refused folder or its log is not kept')
    if os.path.exists(os.path.join(w, 'det_T_v1_B1')): f.append('B2 the part not refused was re-split')
    if listed(w) != expected(ROSTER): f.append('B2 the fire list is not byte-equal to B1')
    return f


def t_b3(block, tmp):
    f = []; rc, w = run_block(block, tmp, 'b3', {'mode': 'SERIAL_FORCED'})
    rows = table(w); plan = [s[3] for s in status(w) if s[0] == 'detect_plan']
    if rc != 0: f.append('B3 rc %d' % rc)
    if not plan or not plan[0].startswith('26 parts: SERIAL_FORCED'): f.append('B3 plan %s' % plan)
    if len(rows) != 26 or any(r['use'] != 'merged' for r in rows): f.append('B3 %d parts' % len(rows))
    if listed(w) != expected(ROSTER): f.append('B3 the fire list differs')
    return f


def t_b4(block, tmp):
    rc, w = run_block(block, tmp, 'b4', {'mode': 'CHUNKED', 'foreign': [ROSTER[30], ROSTER[0]]})
    ok = rc == 3 and step_rc(w, 'census') == ['1'] and listed(w) is None
    return [] if ok else ['B4 a fire outside its part: rc %d census %s list %s' % (rc, step_rc(w, 'census'), listed(w) is not None)]


def t_b5(block, tmp):
    rc, w = run_block(block, tmp, 'b5', {'mode': 'CHUNKED'}, roster=ROSTER + [ROSTER[0]])
    ok = rc == 3 and step_rc(w, 'census') == ['1'] and listed(w) is None
    return [] if ok else ['B5 a roster that repeats a coin: rc %d census %s' % (rc, step_rc(w, 'census'))]


def t_b6(block, tmp):
    rc, w = run_block(block, tmp, 'b6', {'mode': 'CHUNKED', 'refuse': ['GATE_NOT_RUN', ROSTER[0]]})
    resp = [s for s in status(w) if s[0].startswith('resplit_')]
    ok = rc == 3 and not resp and [(r['part'], r['use']) for r in table(w)] == [('A', 'failed')]
    return [] if ok else ['B6 another refusal: rc %d re-split rows %s parts %s' % (rc, resp, [(r['part'], r['use']) for r in table(w)])]


def t_b7(block, tmp):
    rc, w = run_block(block, tmp, 'b7', {'mode': 'CHUNKED', 'cap_over': 1, 'cap_coin': ROSTER[0]})
    uses = [(r['part'], r['use']) for r in table(w)]
    ok = rc == 3 and uses == [('A', 'refused_kept_unmerged'), ('A1', 'failed')] and listed(w) is None
    return [] if ok else ['B7 a re-split part refused again: rc %d parts %s' % (rc, uses)]


def t_b8(block, tmp):
    rc, w = run_block(block, tmp, 'b8', {'mode': 'CHUNKED', 'cap_over': 1, 'cap_coin': ROSTER[0]}, parts=26)
    ok = rc == 3 and step_rc(w, 'resplit_A') == ['2'] and [(r['part'], r['use']) for r in table(w)] == [('A', 'failed')]
    return [] if ok else ['B8 refused at the 26-part size: rc %d resplit_A %s' % (rc, step_rc(w, 'resplit_A'))]


def t_b9(block, tmp):
    rc, w = run_block(block, tmp, 'b9', {'mode': 'CHUNKED'}, parts=4)
    ok = rc == 0 and [r['part'] for r in table(w)] == ['A', 'B', 'C', 'D'] and listed(w) == expected(ROSTER)
    return [] if ok else ['B9 PARTS=4: rc %d parts %s' % (rc, [r['part'] for r in table(w)])]


def t_b10(block, tmp):
    return [] if "| LC_ALL=C sort -t$'\\t' -k2,2n -k1,1; } > $D/EVENTS.tsv" in block else ['B10 the merge does not sort with LC_ALL=C']


def census_of(block):
    a = block.index("<<'CENSUS'\n") + len("<<'CENSUS'\n"); b = block.index('\nCENSUS\n', a)
    return block[a:b + 1]


def t_b11(block, tmp):
    f = []; code = census_of(block); d = os.path.join(tmp, 'b11'); os.makedirs(d)
    open(os.path.join(d, 'census.py'), 'w').write(code)

    def part(name, coins, fires=None, complete=True):
        p = os.path.join(d, name); os.makedirs(p, exist_ok=True)
        open(os.path.join(p, 'EVENTS.tsv'), 'w').write('# x\ncoin\tt\tside\n' + ''.join('%s\t1\t1\n' % c for c in (fires or coins)))
        if complete:
            json.dump({'status': 'COMPLETE'}, open(os.path.join(p, 'DETECT_RUN.json'), 'w'))
        return p

    def case(label, parts, roster, want):
        pt = os.path.join(d, label + '.tsv')
        with open(pt, 'w') as o:
            o.write('part\tfolder\trc\tn_coins\tuse\tcoins\n')
            for nm, folder, coins, use in parts:
                o.write('%s\t%s\t0\t%d\t%s\t%s\n' % (nm, folder, len(coins), use, ','.join(coins)))
        r = subprocess.run([PY, '-B', os.path.join(d, 'census.py'), pt, ','.join(roster)], capture_output=True, text=True)
        if (r.returncode == 0) != want:
            f.append('B11 %s: rc %d %s' % (label, r.returncode, r.stdout.strip()[-120:]))

    a, b = part('a', ['X1', 'X2']), part('b', ['X3', 'X4'])
    case('good', [('A', a, ['X1', 'X2'], 'merged'), ('B', b, ['X3', 'X4'], 'merged')], ['X1', 'X2', 'X3', 'X4'], True)
    case('kept_unmerged', [('A', part('r', ['X1', 'X2'], complete=False), ['X1', 'X2'], 'refused_kept_unmerged'),
                           ('A1', a, ['X1', 'X2'], 'merged'), ('B', b, ['X3', 'X4'], 'merged')], ['X1', 'X2', 'X3', 'X4'], True)
    case('missing', [('A', a, ['X1', 'X2'], 'merged')], ['X1', 'X2', 'X3', 'X4'], False)
    case('extra', [('A', a, ['X1', 'X2'], 'merged'), ('B', b, ['X3', 'X4'], 'merged')], ['X1', 'X2', 'X3'], False)
    case('twice', [('A', a, ['X1', 'X2'], 'merged'), ('B', part('b2', ['X2', 'X3', 'X4']), ['X2', 'X3', 'X4'], 'merged')], ['X1', 'X2', 'X3', 'X4'], False)
    case('not_complete', [('A', part('n', ['X1', 'X2'], complete=False), ['X1', 'X2'], 'merged'), ('B', b, ['X3', 'X4'], 'merged')], ['X1', 'X2', 'X3', 'X4'], False)
    case('foreign', [('A', part('o', ['X1', 'X2'], fires=['X1', 'X3']), ['X1', 'X2'], 'merged'), ('B', b, ['X3', 'X4'], 'merged')], ['X1', 'X2', 'X3', 'X4'], False)
    return f


B_TESTS = {'B1': t_b1, 'B2': t_b2, 'B3': t_b3, 'B4': t_b4, 'B5': t_b5, 'B6': t_b6, 'B7': t_b7, 'B8': t_b8, 'B9': t_b9, 'B10': t_b10, 'B11': t_b11}


def static_tests(files):
    f = []
    ch4 = files[CT.CH4].decode()
    if ch4.count('nice -n 10 $PY -B $EO run 3 "$LAB_DAYS"') != 1 or '$EO run 1 ' in ch4: f.append('B12 v2_0_4 does not run Outcomes as run 3')
    for rel in (CT.JG9, CT.JM9):
        t = files[rel].decode(); head = t.split('\n')[:10]
        if '# CORES 3' not in head: f.append('B13 %s does not declare # CORES 3 in lines 1-10' % rel)
        if len(re.findall(r'\bdu -sm\b', t)) != 1: f.append('B13 %s runs du %d times' % (rel, len(re.findall(r'\bdu -sm\b', t))))
    if 'PARTS= LEAN=$L bash $MP/alarm_grade_chain_v2_2_4_to20260430.sh ' not in files[CT.JM9].decode(): f.append('B13 JOB_MONTH_V9 sets a part count')
    return f


def all_tests(block, names=None):
    f = []
    with tempfile.TemporaryDirectory() as tmp:
        for n, t in B_TESTS.items():
            if names is None or n in names:
                try:
                    f += t(block, os.path.realpath(tmp))
                except Exception as e:                                           # noqa: BLE001 (a crash of a test is a failure)
                    f.append('%s crashed: %s: %s' % (n, type(e).__name__, e))
    return f


MUTANTS = [   # (the text in v2_2_4, the bug planted, the tests that must fail)
    ('elif [ "$MODE" = SERIAL_FORCED ]; then NP=$NF;', 'elif false; then NP=$NF;', ('B3',)),
    ('else NP=2; WHY=', 'else NP=26; WHY=', ('B1',)),
    ('  cap $h || { row $h $TRC failed $C; exit 3; }', '  { row $h $TRC failed $C; exit 3; }', ('B2',)),
    ('  row $h $TRC refused_kept_unmerged $C\n', '  row $h $TRC merged $C\n', ('B2',)),
    ("cap(){ [ $TRC -eq 2 ] && grep -q '^REFUSED WORKER_RSS_CAP:'", "cap(){ [ $TRC -eq 2 ] && grep -q '^REFUSED'", ('B6',)),
    ('[ $k -ge 2 ] ||', '[ $k -ge 1 ] ||', ('B8',)),
    ('rc=$?; st census $rc 0', 'rc=0; st census $rc 0', ('B4', 'B5')),
    ('        if c in seen:\n', '        if False:\n', ('B5', 'B11')),
    ('if miss:\n', 'if False:\n', ('B11',)),
    ("    if not os.path.isfile(run) or json.load(open(run)).get('status') != 'COMPLETE':\n", '    if False:\n', ('B11',)),
    ('        if f[ci] not in own:\n', '        if False:\n', ('B4', 'B11')),
    ('| LC_ALL=C sort -t', '| sort -t', ('B10', 'B1')),
    ("ML=$(tail -n +2 $PT | awk -F'\\t' '$5==\"merged\"{printf \"%s \", $1}')", "ML=$(tail -n +2 $PT | awk -F'\\t' '{printf \"%s \", $1}')", ('B2',)),
    ('C=$(slice "$ALLC" $NP $i)', 'C=$(slice "$ALLC" $NP 0)', ('B1',)),
]


def main():
    if not (os.path.isfile(os.path.join(PKG, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(PKG, 'settings'))):
        raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ at %s' % PKG)
    fails = []
    built = CT.build(PKG)
    for rel, b in built.items():
        p = os.path.join(PKG, rel)
        if not os.path.isfile(p) or open(p, 'rb').read() != b:
            fails.append('C1 %s is not its contract remake (%s; the package has %s)' % (
                rel, CT.sha16b(b), CT.sha16b(open(p, 'rb').read()) if os.path.isfile(p) else 'nothing'))
    files = {rel: open(os.path.join(PKG, rel), 'rb').read() for rel in built if os.path.isfile(os.path.join(PKG, rel))}
    if len(files) == len(built):
        fails += static_tests(files)
    text = files.get(CT.CM4, b'').decode(); block = block_of(text)
    fails += all_tests(block)
    print('LOCALE %s' % (LOC or 'none of en_US.UTF-8 here: B10 checks the text'))
    print('TESTS', 'PASS' if not fails else 'FAIL %s' % fails)
    killed = 0
    for a, b, names in MUTANTS:
        assert block.count(a) == 1, ('planted bug target not found once', a)
        caught = bool(all_tests(block.replace(a, b, 1), names))
        killed += caught
        print('PLANTED BUG %-70s %s' % (b.strip().split('\n')[-1][:70] or '(removed)', 'KILLED' if caught else 'SURVIVED'))
    print('PLANTED BUGS %d of %d killed' % (killed, len(MUTANTS)))
    return 1 if fails or killed != len(MUTANTS) else 0


if __name__ == '__main__':
    sys.exit(main())
