#!/usr/bin/env python3
"""test_where_v3.py: planted tests and planted bugs for where_v3.py. Temp folders only, seconds.

Owner: LAB1 (the map's owner). New edition by SCOUT for the clean release (K7, 30 Oct 2026). Old file:
team/LAB3/LAB1/tools/where_v2/test_where_v2.py 66623f0511a7b2d2. Kept from it: the checks of the finder's metric and code search
(t_metric_card, t_not_found, t_same_output: same planted rows, same assertions). Not kept: its 13 checks of the team map (seat files,
tool owners, producers, skills, the --check gap list, VM paths), which test where_v2's map functions; where_v3 does not carry them (the
team's folders are not in the release), so those stay where_v2's. New: 17 checks of the new edition and 10 planted bugs.
It runs no old edition. Run it from inside an Alarm folder (it copies that folder's _tools/settings_v1.py into each planted one):
  python3 -B test_where_v3.py      -> TESTS PASS (0 failing), then MUTANTS n of n killed; exit 0 only when both hold"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'where_v3.py'
TOOL_DIR = 'team/LAB3/LAB1/tools/where_v2'
CAT_HEAD = 'code\tstore\tclock\texact_k\tscope\tmeaning\tunit\tlevel\tblock\n'
V1_HEAD = 'code\tshort\tunit\tcard\tmeaning\tstore\tread_as\n'
TABLES = {   # the same planted metric row as test_where_v2 (X1.FOOX.S01), plus one row per new table
    'team/LAB3/METRICS_V1.tsv': '# head\n' + V1_HEAD +
        'X1.FOOX.S01\tfoo_5s\tusd\tteam/RAWCHECK/notes/BUILD/FOOX/F1_V1.yaml\tthe planted foo\tCLOCK\tas is\n'
        'Q9.S01\tgone_card\tusd\tteam/RAWCHECK/notes/NOWHERE/GONE_V1.yaml\tthe planted card that is not here\tCLOCK\tas is\n'
        'Q8.S01\tdrop_me\tusd\tNO_CARD\tthe planted dropped one\tCLOCK\tdo not\n',
    'team/LAB3/METRICS_HL_CANDIDATE_V2.tsv': 'code\tcard\tmeaning\tunit\tstore\tread_as\n'
        'X1.HLZZ.Q01\tteam/RAWCHECK/notes/BUILD/HLZZ/HZ1_V1.yaml\tthe planted candidate\tusd\tX1.HLZZ\tread it carefully\n',
    'team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv': CAT_HEAD + 'CTX.T.zebra\tCTX\t60\t0\tcoin\tthe planted zebra context\tusd\tA\tB\n',
    'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv': CAT_HEAD + 'EPI.T.giraffe\tEPI\t60\t0\tcoin\tthe planted giraffe profile\tpct\tA\tB\n',
    'team/RESEARCH/tools/alarm_stamp/STAMP_CATALOG_V1.tsv': 'part\tcolumn\tmeaning\nSTAMPX\tlabel_kiwi\tthe planted kiwi label\n',
    'team/FEED/CATALOG_V1.tsv': 'code\tmeaning\naggTrade.zz\tthe planted feed column\n',
    'team/LIVELAYER/CATALOG_V1.tsv': 'code\tmeaning\nLIVE.zz\tthe planted live value\n',
    'team/LAB3/METRICS_V2.tsv': '# head\n' + V1_HEAD.rstrip('\n') + '\tregister_status\n' +
        'X1.FOOX.S01\tfoo_5s\tusd\tteam/RAWCHECK/notes/BUILD/FOOX/F1_V1.yaml\tthe planted foo\tCLOCK\tas is\tIN_FORCE\n'
        'Q8.S01\tdrop_me\tusd\tNO_CARD\tthe planted dropped one\tCLOCK\tdo not\tDROPPED\n'
        'X1.HLNEW.Q01\thl_new\tusd\tteam/RAWCHECK/notes/BUILD/HLNEW/HN1_V1.yaml\tthe planted register only reading\tCLOCK\tread it\tIN_FORCE\n',
    'team/RAWCHECK/notes/BUILD/FOOX/F1_V1.yaml': 'x\n',
    'team/RAWCHECK/notes/BUILD/HLZZ/HZ1_V1.yaml': 'x\n',
    'team/RAWCHECK/notes/BUILD/HLNEW/HN1_V1.yaml': 'x\n',
}
NEEDED = [t for t in TABLES if t.endswith('.tsv')]


def alarm_files():
    d = HERE
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('REFUSED: run this test inside an Alarm folder (no _tools/settings_v1.py above %s)' % HERE)
        d = os.path.dirname(d)
    return os.path.join(d, '_tools', 'settings_v1.py'), os.path.join(d, 'settings', 'SETTINGS_EXAMPLE.env')


def write(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(text)


def plant(root, src, skip=()):
    reader, example = alarm_files()
    os.makedirs(os.path.join(root, '_tools')); os.makedirs(os.path.join(root, 'settings'))
    shutil.copy(reader, os.path.join(root, '_tools')); shutil.copy(example, os.path.join(root, 'settings'))
    for rel, text in TABLES.items():
        if rel not in skip:
            write(os.path.join(root, '01_Detection', 'tree', *rel.split('/')), text)
    tool = os.path.join(root, '01_Detection', 'tree', *TOOL_DIR.split('/'), TOOL)
    os.makedirs(os.path.dirname(tool), exist_ok=True)
    shutil.copy(src, tool)
    return tool


def run(tool, *args, env=None):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run([sys.executable, '-B', tool, *args], capture_output=True, text=True, env=e, cwd=tempfile.gettempdir())
    return p.returncode, p.stdout + p.stderr


def tests(src):
    ok = []
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, 'A', 'Alarm'); tool = plant(root, src)
        tree = os.path.join(root, '01_Detection', 'tree')
        # kept from test_where_v2 (the finder's metric and code search)
        rc, o = run(tool, 'X1.FOOX.S01', '--kind', 'metric')
        ok.append(('t_metric_card', 'F1_V1.yaml' in o and 'the planted foo' in o))
        rc, o = run(tool, 'no_such_thing_anywhere')
        ok.append(('t_not_found', rc == 1 and 'NOT FOUND' in o))
        ok.append(('t_same_output', run(tool, 'planted', '--n', '20') == run(tool, 'planted', '--n', '20')))
        # new
        rc, o = run(tool, 'X1.FOOX.S01', '--kind', 'metric')
        ok.append(('t_metric_header', rc == 0 and o.startswith('[metric] X1.FOOX.S01  | owner LAB1 (METRICS_V1); proof LAB4 | from team/LAB3/METRICS_V1.tsv\n')))
        ok.append(('t_path_under_tree', ('\n   %s\n' % os.path.join(tree, 'team/RAWCHECK/notes/BUILD/FOOX/F1_V1.yaml')) in o))
        ok.append(('t_card_here_not_gone', 'GONE TODAY' not in o))
        rc, o = run(tool, 'Q9.S01', '--kind', 'metric')
        ok.append(('t_card_missing_gone', '[metric] Q9.S01   GONE TODAY' in o))
        rc, o = run(tool, 'X1.HLZZ.Q01')
        ok.append(('t_candidate', '[metric] X1.HLZZ.Q01' in o and 'UNSIGNED CANDIDATE | the planted candidate' in o))
        rc, o = run(tool, 'X1.HLNEW.Q01')
        ok.append(('t_register_only_row', '[metric] X1.HLNEW.Q01  | owner LAYERS (METRICS_V2 register) | from team/LAB3/METRICS_V2.tsv' in o))
        rc, o = run(tool, 'Q8.S01')
        ok.append(('t_dropped', 'DROPPED (register METRICS_V2: not in force)' in o.split('\n')[0]))
        rc, o = run(tool, 'X1.FOOX.S01')
        ok.append(('t_in_force_not_dropped', 'DROPPED' not in o))
        rc, o = run(tool, 'zebra', '--kind', 'code')
        ok.append(('t_code_ctx', '[code] CTX.T.zebra' in o and os.path.join(tree, 'team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv') in o))
        found = all('[code] %s' % c in run(tool, w, '--kind', 'code')[1] for c, w in
                    (('EPI.T.giraffe', 'giraffe'), ('STAMPX.label_kiwi', 'kiwi'), ('aggTrade.zz', 'feed column'), ('LIVE.zz', 'live value')))
        ok.append(('t_code_every_catalogue', found))
        rc, o = run(tool, 'planted', 'foo', '--kind', 'metric')
        ok.append(('t_words', rc == 0 and o.startswith('[metric] X1.FOOX.S01')))
        rc, o = run(tool, 'X1.FOOX.S01', '--kind', 'metric', env={'WHERE_V2_REPO': os.path.join(tmp, 'elsewhere'),
                                                                   'METRICS_V1': os.path.join(tmp, 'elsewhere.tsv')})
        ok.append(('t_env_ignored', rc == 0 and 'the planted foo' in o))
        rc, o = run(tool, '--check')
        ok.append(('t_check_refused', rc == 2 and 'REFUSED --check is where_v2' in o))
        miss = []
        for t in NEEDED:
            r2 = plant(os.path.join(tmp, 'M_' + t.replace('/', '_'), 'Alarm'), src, skip=(t,))
            rc, o = run(r2, 'X1.FOOX.S01')
            miss.append(rc == 2 and 'MISSING TABLE ' + t in o)
        ok.append(('t_missing_table_refused_each_of_8', len(miss) == 8 and all(miss)))
        lone = os.path.join(tmp, 'lone'); os.makedirs(lone); shutil.copy(src, os.path.join(lone, TOOL))
        rc, o = run(os.path.join(lone, TOOL), 'X1.FOOX.S01')
        ok.append(('t_outside_alarm_refused', rc == 2 and 'NOT INSIDE AN ALARM FOLDER' in o))
        _, example = alarm_files()
        keys = [l.split('=', 1)[0] for l in open(example) if '=' in l and not l.lstrip().startswith('#')]
        good = os.path.join(tmp, 'S_GOOD.env'); write(good, ''.join('%s=\n' % k for k in keys))
        bad = os.path.join(tmp, 'S_BAD.env'); write(bad, ''.join('%s=\n' % k for k in keys) + 'NOT_A_KEY=\n')
        ok.append(('t_settings_good', run(tool, 'X1.FOOX.S01', '--settings', good) == run(tool, 'X1.FOOX.S01')))
        rc, o = run(tool, 'X1.FOOX.S01', '--settings', bad)
        ok.append(('t_settings_bad_refused', rc == 2 and 'REFUSED' in o and '[metric]' not in o))
    return ok


MUTANTS = [
    ("    if miss:\n        raise Refused", "    if False:\n        raise Refused"),
    ("TABLES = (METRICS, CANDIDATES) + CATALOGS[1:] + (REGISTER,)", "TABLES = (METRICS, CANDIDATES) + CATALOGS[1:]"),
    ("drop = '   DROPPED (register METRICS_V2: not in force)' if r[0] == 'metric' and r[1] in dropped else ''", "drop = ''"),
    ("        if r[0] in known:\n            continue", "        if True:\n            continue"),
    ("return os.path.exists(r if r.startswith('/') else os.path.join(tree, r))", "return os.path.exists(r)"),
    ("return os.path.join(S.alarm_root(start), *DETECTION_TREE)", "return os.environ.get('WHERE_V2_REPO') or os.path.join(S.alarm_root(start), *DETECTION_TREE)"),
    ("    if '--check' in a:\n", "    if False:\n"),
    ("        if settings: S.load(settings)", "        pass"),
    ("full = p if (not p or p.startswith('/')) else os.path.join(tree, p)", "full = p"),
    ("    for c in CATALOGS[1:]:\n", "    for c in CATALOGS[1:3]:\n"),
]


def main():
    src = os.path.join(HERE, TOOL)
    res = tests(src)
    for n, v in res:
        print('%s %s' % ('PASS' if v else 'FAIL', n))
    fails = [n for n, v in res if not v]
    print('TESTS %s (%d of %d pass)' % ('PASS' if not fails else 'FAIL', len(res) - len(fails), len(res)))
    killed = 0
    for i, (old, new) in enumerate(MUTANTS, 1):
        with tempfile.TemporaryDirectory() as md:
            s = open(src).read()
            if old not in s:
                print('MUTANT %d: pattern not found' % i); continue
            p = os.path.join(md, TOOL)
            with open(p, 'w') as f:
                f.write(s.replace(old, new, 1))
            k = not all(v for _, v in tests(p))
            killed += k
            print('MUTANT %d: %s' % (i, 'KILLED' if k else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(MUTANTS)))
    sys.exit(0 if not fails and killed == len(MUTANTS) else 1)


if __name__ == '__main__':
    main()
