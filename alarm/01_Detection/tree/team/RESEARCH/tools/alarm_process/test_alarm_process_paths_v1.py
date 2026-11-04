#!/usr/bin/env python3
"""test_alarm_process_paths_v1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): tests of the path code of the paths-only editions
alarm_card_v1_2_1.py, alarm_card_v1_3_1.py, make_random_v3_1.py and menu_v2_1.py (CLEAN_RELEASE_V1 section 6): each takes the lab code
(lab3, labcore, event_outcomes) from the Alarm folder that holds it (<Alarm>/01_Detection/tree), never from anywhere else, refuses outside
an Alarm package or without its lab tree, and the menu takes its work folder W only from the environment. Each test copies a tool into a
made-up Alarm package (this package's own settings_v1.py, a settings/ folder, a lab tree of stub modules that write down where they were
loaded from and what they were asked); then planted bugs: every mutant of a tool's path code must make a test fail. Seconds; temp folders
only, removed after.  python3 -B <Alarm>/01_Detection/tree/team/RESEARCH/tools/alarm_process/test_alarm_process_paths_v1.py"""
import os, sys, shutil, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = {'alarm_card_v1_2_1.py': 'event_outcomes', 'alarm_card_v1_3_1.py': 'event_outcomes', 'menu_v2_1.py': 'event_outcomes',
         'make_random_v3_1.py': 'labcore'}
AT = ('01_Detection', 'tree', 'team', 'RESEARCH', 'tools', 'alarm_process')          # where each tool sits in the release
STUB = ("import os, sys\nopen(os.environ['K4_LOG'], 'a').write('LOADED ' + os.path.realpath(__file__) + '\\n')\n"
        "def read(root, code, *a, **k):\n    open(os.environ['K4_LOG'], 'a').write('READ code=' + os.path.realpath(code) + '\\n'); sys.exit(0)\n"  # realpath: on the Mac /tmp is /private/tmp
        "def waves(t, gap):\n    open(os.environ['K4_LOG'], 'a').write('WAVES\\n'); sys.exit(0)\n"
        "if not os.environ.get('K4_GO'):\n    sys.exit(0)\n")


def package_file(*rel):
    """a file of the Alarm package that holds this test (found by settings_v1's own rule)"""
    d = HERE
    while not (os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings'))):
        if os.path.dirname(d) == d:
            raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ above %s' % HERE)
        d = os.path.dirname(d)
    return os.path.join(d, *rel)


def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s)


def fake_package(root, lab=True, lab3=True, settings_dir=True, decoy=False):
    w(os.path.join(root, '_tools', 'settings_v1.py'), open(package_file('_tools', 'settings_v1.py')).read())
    if settings_dir:
        os.makedirs(os.path.join(root, 'settings'))
    if lab:
        t = os.path.join(root, '01_Detection', 'tree', 'team')
        if lab3:
            os.makedirs(os.path.join(t, 'LAB3', 'code'))
        w(os.path.join(t, 'RESEARCH', 'tools', 'labcore', '__init__.py'), '')
        w(os.path.join(t, 'RESEARCH', 'tools', 'labcore', 'waves.py'), STUB)
        w(os.path.join(t, 'RESEARCH', 'tools', 'event_outcomes', 'event_outcomes.py'), STUB)
    return root


def decoy_dir(root):
    """the same module names elsewhere, first on PYTHONPATH: a tool must still load its own lab tree's"""
    w(os.path.join(root, 'labcore', '__init__.py'), '')
    for p in (os.path.join(root, 'labcore', 'waves.py'), os.path.join(root, 'event_outcomes.py')):
        w(p, "import os, sys\nopen(os.environ['K4_LOG'], 'a').write('DECOY ' + os.path.realpath(__file__) + '\\n'); sys.exit(0)\n")
    return root


def run(text, name, where, go=False, env=None, args=(), pythonpath=None):
    """the tool text as <where>/<name>, run in a fresh interpreter; -> (rc, output, log lines)"""
    p = os.path.join(where, name); w(p, text)
    log = os.path.join(tempfile.mkdtemp(dir=os.path.dirname(where.rstrip(os.sep)) or None), 'k4.log'); open(log, 'w').close()
    e = {k: v for k, v in os.environ.items() if k not in ('W', 'PYTHONPATH', 'K4_GO')}
    e.update(K4_LOG=log, PYTHONDONTWRITEBYTECODE='1', **(env or {}))
    if go:
        e['K4_GO'] = '1'
    if pythonpath:
        e['PYTHONPATH'] = pythonpath
    r = subprocess.run([sys.executable, '-B', p] + list(args), capture_output=True, text=True, env=e, cwd=where)
    return r.returncode, r.stdout + r.stderr, [l for l in open(log).read().split('\n') if l]


def work_folder(root, v='V1'):
    """the least a card or the menu reads before Outcomes' reader: the fire list, the store catalogs, the random weights"""
    W = os.path.join(root, 'W')
    w(os.path.join(W, '%s_FIRES_V1_LIST.tsv' % v), 'coin\tt\tside\nBTC\t1757900000\t1\n')
    w(os.path.join(W, 'RND_%s_V1_LIST.tsv' % v), 'coin\tt\tside\nBTC\t1757901000\t1\n')
    w(os.path.join(W, 'RND_%s_V1_WEIGHTS.tsv' % v), 'coin\tt\tweight\nBTC\t1757901000\t1.0\n')
    for sub, subj in (('om_%s_v1' % v, 'IDEA2%sMENU' % v), ('om_%sRND_v1' % v, 'IDEA2%sRNDMENU' % v)):
        w(os.path.join(W, sub, 'OUT_CATALOG_%s.tsv' % subj), 'name\tx\n')
    return W


def check_tool(name, text):
    """-> the failures of every test for one tool's text"""
    fails = []
    kind = TOOLS[name]
    with tempfile.TemporaryDirectory() as tmp:
        pkg = fake_package(os.path.join(tmp, 'A1'))
        want = os.path.realpath(os.path.join(pkg, '01_Detection', 'tree', 'team', 'RESEARCH', 'tools'))
        mod = os.path.join(want, 'labcore', 'waves.py') if kind == 'labcore' else os.path.join(want, 'event_outcomes', 'event_outcomes.py')
        rc, out, log = run(text, name, os.path.join(pkg, *AT))                                  # 1 inside: its own lab tree
        if rc != 0 or log != ['LOADED ' + mod]:
            fails.append('inside: rc %d log %s %s' % (rc, log, out[-300:]))
        os.makedirs(os.path.join(pkg, '03_Grading', '_tools'))                                  # 2 elsewhere in the package, past a _tools
        rc, out, log = run(text, name, os.path.join(pkg, '03_Grading', 'tree', 'tools', 'x'))   #   folder without the reader: the same tree
        if rc != 0 or log != ['LOADED ' + mod]:
            fails.append('elsewhere in the package: rc %d log %s' % (rc, log))
        dz = decoy_dir(os.path.join(tmp, 'decoy'))                                               # 3 a decoy first on PYTHONPATH loses
        rc, out, log = run(text, name, os.path.join(pkg, *AT), pythonpath=dz)
        if rc != 0 or log != ['LOADED ' + mod]:
            fails.append('decoy: rc %d log %s' % (rc, log))
        for label, kw, msg in (('no package', None, 'NOT INSIDE AN ALARM PACKAGE'), ('no settings folder', dict(settings_dir=False), 'NOT INSIDE AN ALARM PACKAGE'),
                               ('no lab tree', dict(lab=False), 'NO LAB TREE IN THE ALARM FOLDER'),
                               ('no lab3 code in the lab tree', dict(lab3=False), 'NO LAB TREE IN THE ALARM FOLDER')):   # 4 refusals, nothing loaded
            where = os.path.join(tmp, 'plain', label.replace(' ', '_')) if kw is None else os.path.join(fake_package(os.path.join(tmp, label.replace(' ', '_')), **kw), *AT)
            rc, out, log = run(text, name, where)
            if rc == 0 or msg not in out or log:
                fails.append('%s: rc %d log %s out %s' % (label, rc, log, out[-200:]))
        if kind == 'event_outcomes':                                                            # 5 the lab3 code it hands to Outcomes' reader
            W = work_folder(tmp)
            args = ['V1', 'om'] if name.startswith('menu') else [W, 'V1']
            rc, out, log = run(text, name, os.path.join(pkg, *AT), go=True, env={'W': W}, args=args)
            code = os.path.join(os.path.realpath(pkg), '01_Detection', 'tree', 'team', 'LAB3', 'code')
            wv = os.path.join(want, 'labcore', 'waves.py')
            if rc != 0 or log != ['LOADED ' + mod, 'LOADED ' + wv, 'READ code=' + code]:
                fails.append('lab3 code: rc %d log %s %s' % (rc, log, out[-300:]))
        else:
            W = work_folder(tmp)
            rc, out, log = run(text, name, os.path.join(pkg, *AT), go=True, args=[os.path.join(W, 'g'), os.path.join(W, 'V1_FIRES_V1_LIST.tsv'), os.path.join(W, 'R')])
            if rc != 0 or log != ['LOADED ' + mod, 'WAVES']:
                fails.append('labcore waves: rc %d log %s %s' % (rc, log, out[-300:]))
        if name.startswith('menu'):                                                             # 6 the menu's W: the environment only, absolute
            for label, env in (('W unset', {}), ('W relative', {'W': 'W'})):
                rc, out, log = run(text, name, os.path.join(pkg, *AT), go=True, env=env, args=['V1', 'om'])
                if rc == 0 or 'NO W' not in out:
                    fails.append('menu %s: rc %d %s' % (label, rc, out[-200:]))
        mp = importlib.util.spec_from_file_location('k4_machine_paths', package_file('_tools', 'machine_paths_v2.py'))   # 7 no machine path in code
        M = importlib.util.module_from_spec(mp); mp.loader.exec_module(M)
        code_rows = [r for r in M.py_rows(text) if r[2] == 'CODE']
        if code_rows:
            fails.append('machine paths in code: %s' % code_rows[:3])
    return fails


MUTANTS = [   # (tools, the text of the new path code, the bug planted)
    (list(TOOLS), "f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')", "f = os.path.join(sv.alarm_root(__file__), '03_Grading', 'tree')"),
    (list(TOOLS), "f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')", "f = os.path.join(d, '01_Detection', 'tree')"),
    (list(TOOLS), "    if not (os.path.isdir(os.path.join(f, 'team', 'LAB3', 'code')) and os.path.isdir(os.path.join(f, 'team', 'RESEARCH', 'tools'))):",
     "    if not os.path.isdir(f):"),
    (list(TOOLS), "    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):", "    while not os.path.isdir(os.path.join(d, '_tools')):"),
    (list(TOOLS), "        raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s' % e)", "        f = os.path.join(d, '01_Detection', 'tree')"),
    (['alarm_card_v1_2_1.py', 'alarm_card_v1_3_1.py'], "F = _lab_tree(); CODE = F + '/team/LAB3/code'", "F = _lab_tree(); CODE = F + '/team/LAB3'"),
    (['alarm_card_v1_2_1.py', 'alarm_card_v1_3_1.py'], "sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')",
     "sys.path.append(F + '/team/RESEARCH/tools'); sys.path.append(F + '/team/RESEARCH/tools/event_outcomes')"),
    (['menu_v2_1.py'], "F = _lab_tree(); code = F + '/team/LAB3/code'", "F = _lab_tree(); code = F + '/team/LAB3/code/lab3'"),
    (['menu_v2_1.py'], "W = os.environ.get('W', '')", "W = os.environ.get('W', '/tmp')"),
    (['menu_v2_1.py'], "if not os.path.isabs(W): raise SystemExit", "if not W: raise SystemExit"),
    (['make_random_v3_1.py'], "sys.path.insert(0, os.path.join(_lab_tree(), 'team', 'RESEARCH', 'tools'))", "sys.path.append(os.path.join(_lab_tree(), 'team', 'RESEARCH', 'tools'))"),
    (['make_random_v3_1.py'], "sys.path.insert(0, os.path.join(_lab_tree(), 'team', 'RESEARCH', 'tools'))", "sys.path.insert(0, os.path.join(_lab_tree(), 'team', 'RESEARCH'))"),
]


def main():
    texts = {n: open(os.path.join(HERE, n)).read() for n in TOOLS}
    bad = 0
    for n, t in texts.items():
        f = check_tool(n, t)
        print('TESTS %-22s %s' % (n, 'PASS' if not f else 'FAIL %s' % f)); bad += bool(f)
    killed = total = 0
    for tools, a, b in MUTANTS:
        for n in tools:
            assert texts[n].count(a) == 1, ('mutant target not found once', n, a)
            total += 1
            caught = bool(check_tool(n, texts[n].replace(a, b, 1)))
            killed += caught
            print('MUTANT %-22s %-70s %s' % (n, b.strip()[:70], 'KILLED' if caught else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, total))
    return 1 if bad or killed != total else 0


if __name__ == '__main__':
    sys.exit(main())
