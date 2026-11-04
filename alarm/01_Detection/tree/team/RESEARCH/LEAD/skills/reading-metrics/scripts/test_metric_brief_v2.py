#!/usr/bin/env python3
"""test_metric_brief_v2.py: planted tests and planted bugs for metric_brief_v2.py. Temp folders only, seconds.

Owner: LEAD (the reading-metrics skill). New edition by SCOUT for the clean release (K7, 30 Oct 2026). Old file:
team/RESEARCH/LEAD/skills/reading-metrics/scripts/test_metric_brief.py 3470fc1fe711623f. Its 8 checks and 7 planted bugs are kept (the
same checks, the same patterns); only the planting changed: the tables are planted inside a planted Alarm folder, because the new
edition reads no variables. New: 13 checks of the path code (where the tables come from, refusals, settings) and 8 planted bugs in it.
It runs no old edition. Run it from inside an Alarm folder (it copies that folder's _tools/settings_v1.py into each planted one):
  python3 -B test_metric_brief_v2.py      -> TESTS PASS (0 failing), then MUTANTS n of n killed; exit 0 only when both hold"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'metric_brief_v2.py'
TOOL_DIR = 'team/RESEARCH/LEAD/skills/reading-metrics/scripts'
T_METRICS = 'team/LAB3/METRICS_V1.tsv'
T_TRAPS = 'team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv'
T_CTX = 'team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv'
T_EPI = 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv'
CAT_HEAD = 'code\tstore\tclock\texact_k\tscope\tmeaning\tunit\tlevel\tblock\n'
# the old edition's planted tables, unchanged
M = 'code\tcard_name\tmeaning\tunit_text\tscope_text\tstep\twindow\tuse_may\tfirst\tlast\tcard\n' \
    'X.S01\tplain one\tmeans one\tusd\tcoin\t5 s\t5 s\tmay one\t20250910\t20260309\tcards/x.yaml\n' \
    'X.S02\tbroken one\tmeans two\tusd\tcoin\t5 s\t5 s\t\t20250910\t20260309\tcards/x.yaml\n' \
    'X.S03\tmisleading one\tmeans three\tpct\tcoin\t1 min\t15 min\t\t20250910\t20260309\tcards/x.yaml\n'
T = '# METRIC_TRAPS_V1 test\ncode\tname\tlooks_like\tnever_read_as\tread_it_as\tempty_means\tstatus\tproof\tcard\n' \
    'X.S01\tplain one\t\tthe total\tat least\tnot seen, never 0\tPROVEN, READ BY THE RULE\tj1\tc\n' \
    'X.S02\tbroken one\t\t\t\t\tDO NOT USE: NOT BUILT\t\tc\n' \
    'X.S03\tmisleading one\t\tbeyond its own beta\twhose move it is\t\tNAME MISLEADS: READ THE RULE\tj3\tc\n' \
    'X.S04\tuntested one\t\t\t\t\tCOMPUTED RIGHT, MEANING NOT YET TESTED\t\tc\n'
T += 'X.S05\twithdrawn one\t\t\t\t\tWITHDRAWN (A DROPPED MODEL)\t\tc\n' 'X.S06\tblank one\t\t\t\t\t\t\tc\n'
CTX = CAT_HEAD + 'CTX.T.only_ctx\tCTX\t60\t0\tcoin\tthe planted context value\tusd\tA\tB\n'
EPI = CAT_HEAD + 'EPI.T.only_epi\tEPI\t60\t0\tcoin\tthe planted profile value\tpct\tA\tB\n'


def alarm_files():
    """this Alarm folder's settings reader and settings example, copied into every planted Alarm folder"""
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


def plant(root, src, tables, tool_part='01_Detection', tool_dir=TOOL_DIR):
    """a planted Alarm folder at root: the real settings reader, the tables in 01_Detection/tree, the tool -> the tool's path"""
    reader, example = alarm_files()
    os.makedirs(os.path.join(root, '_tools')); os.makedirs(os.path.join(root, 'settings'))
    shutil.copy(reader, os.path.join(root, '_tools')); shutil.copy(example, os.path.join(root, 'settings'))
    for rel, text in tables.items():
        if text is not None:
            write(os.path.join(root, '01_Detection', 'tree', *rel.split('/')), text)
    tool = os.path.join(root, tool_part, 'tree', *tool_dir.split('/'), TOOL)
    os.makedirs(os.path.dirname(tool), exist_ok=True)
    shutil.copy(src, tool)
    return tool


def run(tool, *args, env=None):
    e = dict(os.environ)
    for k in ('METRICS_V1', 'METRIC_TRAPS', 'CATALOGS'):
        e.pop(k, None)
    e.update(env or {})
    p = subprocess.run([sys.executable, '-B', tool, *args], capture_output=True, text=True, env=e, cwd=tempfile.gettempdir())
    return p.returncode, p.stdout, p.stderr


def settings_file(tmp, name, extra=''):
    """a settings file with every key of the example, all empty (this tool reads none), plus `extra` lines"""
    _, example = alarm_files()
    keys = [l.split('=', 1)[0] for l in open(example) if '=' in l and not l.lstrip().startswith('#')]
    p = os.path.join(tmp, name)
    write(p, ''.join('%s=\n' % k for k in keys) + extra)
    return p


def base_tables():
    return {T_METRICS: M, T_TRAPS: T, T_CTX: CTX, T_EPI: EPI}


def tests(src):
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        tool = plant(os.path.join(tmp, 'A1', 'Alarm'), src, base_tables())
        o = lambda *a: run(tool, *a)[1]
        # the old edition's 8 checks
        if 'STOP' not in o('X.S02'):
            fails.append('DO NOT USE must print STOP')
        if 'NOT FOUND' not in o('NOPE.S9'):
            fails.append('an unknown code must print NOT FOUND')
        x = o('X.S03')
        if 'RULE: NAME MISLEADS' not in x or 'whose move it is' not in x or 'beyond its own beta' not in x:
            fails.append('NAME MISLEADS must print RULE with its read-it-as and never-read-as lines')
        x = o('X.S04')
        if 'CAUTION' not in x or 'never the basis of a claim' not in x:
            fails.append('MEANING NOT YET TESTED must print CAUTION')
        if 'STOP' not in o('X.S05'):
            fails.append('WITHDRAWN must print STOP (OUTSIDE X01-01)')
        if 'CAUTION' not in o('X.S06'):
            fails.append('a blank or unknown status must print CAUTION, never pass as proven (OUTSIDE 02-07)')
        x = o('X.S01')
        if 'never 0' not in x or 'the total' not in x or 'means one' not in x or 'STOP' in x or 'CAUTION' in x:
            fails.append('a proven metric prints its card and trap lines, with no STOP or CAUTION')
        if o('--family', 'X').count('== X.S0') != 6:
            fails.append('--family must list every code of the family from both files')
        # new: the path code
        rc, out, err = run(tool, 'X.S01')
        if rc != 0 or '== X.S01  plain one' not in out:
            fails.append('a planted Alarm folder: exit 0 and the brief from its own tables')
        if 'the planted context value' not in o('CTX.T.only_ctx') or 'the planted profile value' not in o('EPI.T.only_epi'):
            fails.append('both catalogues (CTX and EPI) are read from the detection tree')
        if 'find it with where_v3 (01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py) before using it' not in o('NOPE.S9'):
            fails.append('NOT FOUND points to where_v3 and its path in the release (where_v2 is not in the release)')
        other = os.path.join(tmp, 'other')
        write(os.path.join(other, 'M.tsv'), M.replace('X.S01\tplain one', 'ENV.S01\tenv one'))
        write(os.path.join(other, 'T.tsv'), T.replace('X.S01\tplain one', 'ENV.S01\tenv one'))
        rc, out, err = run(tool, 'X.S01', 'ENV.S01', env={'METRICS_V1': os.path.join(other, 'M.tsv'),
                                                            'METRIC_TRAPS': os.path.join(other, 'T.tsv'), 'CATALOGS': ''})
        if '== X.S01  plain one' not in out or 'ENV.S01: NOT FOUND' not in out:
            fails.append('the variables METRICS_V1, METRIC_TRAPS and CATALOGS are never read')
        for rel in (T_METRICS, T_TRAPS, T_CTX, T_EPI):
            t2 = base_tables(); t2[rel] = None
            tool2 = plant(os.path.join(tmp, 'miss_' + rel.split('/')[-1], 'Alarm'), src, t2)
            rc, out, err = run(tool2, 'X.S01')
            if rc != 2 or 'MISSING TABLE' not in err or out.strip():
                fails.append('a missing %s must be refused (exit 2, MISSING TABLE, nothing printed)' % rel.split('/')[-1])
        lone = os.path.join(tmp, 'lone'); os.makedirs(lone); shutil.copy(src, os.path.join(lone, TOOL))
        rc, out, err = run(os.path.join(lone, TOOL), 'X.S01')
        if rc != 2 or 'NOT INSIDE AN ALARM FOLDER' not in err:
            fails.append('outside an Alarm folder it refuses (exit 2)')
        tool3 = plant(os.path.join(tmp, 'A3', 'Alarm'), src, base_tables(), tool_part='Agentic', tool_dir='tree_tools')
        if '== X.S01  plain one' not in run(tool3, 'X.S01')[1]:
            fails.append('the tables come from 01_Detection/tree wherever the tool sits in the Alarm folder')
        good = settings_file(tmp, 'S_GOOD.env')
        rc, out, err = run(tool, '--settings', good, 'X.S01')
        if rc != 0 or out != o('X.S01'):
            fails.append('a good settings file changes nothing')
        bad = settings_file(tmp, 'S_BAD.env', 'NOT_A_KEY=\n')
        rc, out, err = run(tool, '--settings', bad, 'X.S01')
        if rc != 2 or 'REFUSED' not in err or out.strip():
            fails.append('a bad settings file is refused (exit 2) before anything is printed')
        rc, out, err = run(tool, '--settings', os.path.join(tmp, 'NO_SUCH.env'), 'X.S01')
        if rc != 2 or 'NO SETTINGS FILE' not in err:
            fails.append('a settings file that does not exist is refused (exit 2)')
    return fails


MUTANTS = [   # the old edition's 7, the same patterns
    ("or s.startswith('WITHDRAWN')", "or False"),
    ("return f'CAUTION: {status or \"NO STATUS\"}: not a known proven status, treat as unproven'", "return ''"),
    ("if s.startswith('DO NOT USE') or s.startswith('WITHDRAWN'):", "if s.startswith('WITHDRAWN'):"),
    ("out.append(f'== {c}: NOT FOUND", "pass  # out.append(f'== {c}: NOT FOUND"),
    ("if s.startswith('NAME MISLEADS'):", "if False:"),
    ("if 'MEANING NOT YET TESTED' in s:", "if False:"),
    ("('never_read_as', 'NEVER READ AS'), ", ""),
    # new: the path code
    ("for k, p in paths if not os.path.isfile(p)]", "for k, p in paths[:1] if not os.path.isfile(p)]"),
    ("    if miss:\n        raise Refused", "    if False:\n        raise Refused"),
    ("return paths[0][1], paths[1][1], [p for k, p in paths[2:]]", "return paths[0][1], paths[1][1], [p for k, p in paths[2:3]]"),
    ("METRICS, TRAPS, CATALOGS = tables(detection_tree(__file__, S))",
     "METRICS, TRAPS, CATALOGS = tables(detection_tree(__file__, S)); METRICS = os.environ.get('METRICS_V1', METRICS)"),
    ("            S.load(a.settings)", "            pass"),
    ("return os.path.join(S.alarm_root(start), *DETECTION_TREE)", "return os.path.join(S.alarm_root(os.getcwd()), *DETECTION_TREE)"),
    ("        print('REFUSED %s' % e, file=sys.stderr)\n        return 2\n    cards", "        print('REFUSED %s' % e, file=sys.stderr)\n        return 0\n    cards"),
    ("FINDER = '01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py'", "FINDER = 'where_v2'"),
]


def main():
    src = os.path.join(HERE, TOOL)
    fails = tests(src)
    for f in fails:
        print('FAIL', f)
    print(f'TESTS {"PASS" if not fails else "FAIL"} ({len(fails)} failing)')
    killed = 0
    for i, (old, new) in enumerate(MUTANTS, 1):
        with tempfile.TemporaryDirectory() as md:
            s = open(src).read()
            if old not in s:
                print(f'MUTANT {i}: pattern not found')
                continue
            p = os.path.join(md, TOOL)
            with open(p, 'w') as f:
                f.write(s.replace(old, new, 1))
            ok = bool(tests(p))
            killed += ok
            print(f'MUTANT {i}: {"KILLED" if ok else "SURVIVED"}')
    print(f'MUTANTS {killed} of {len(MUTANTS)} killed')
    sys.exit(0 if not fails and killed == len(MUTANTS) else 1)


if __name__ == '__main__':
    main()
