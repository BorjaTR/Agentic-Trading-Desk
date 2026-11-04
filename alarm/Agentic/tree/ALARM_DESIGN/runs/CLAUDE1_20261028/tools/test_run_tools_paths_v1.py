#!/usr/bin/env python3
"""test_run_tools_paths_v1.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): tests of the path code of the paths-only editions
perfire_v1_1_to20260430.py and lead_null_v1_1_to20251231.py (CLEAN_RELEASE_V1 section 6): each takes the lab code (lab3, labcore,
event_outcomes) from the Alarm folder that holds it (<Alarm>/01_Detection/tree), never from anywhere else, and refuses outside an Alarm
package or without its lab tree; lead_null finds it only when its real store reader is first needed (importing it needs no package: its
synthetic tests, test_lead_null_v1_1.py, run anywhere). Each test copies a tool into a made-up Alarm package (this package's settings_v1.py,
a settings/ folder, a lab tree of stub modules that write down where they were loaded from and the lab3 code they were handed); then
planted bugs: every mutant of the path code must make a test fail. Seconds; temp folders only, removed after.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/test_run_tools_paths_v1.py"""
import os, sys, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ('perfire_v1_1_to20260430.py', 'lead_null_v1_1_to20251231.py')
AT = ('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools')          # where both sit in the release
STUB = ("import os, sys\nopen(os.environ['K4_LOG'], 'a').write('LOADED ' + os.path.realpath(__file__) + '\\n')\n"
        "def read(root, code, *a, **k):\n    open(os.environ['K4_LOG'], 'a').write('READ code=' + os.path.realpath(code) + '\\n'); sys.exit(0)\n"  # realpath: on the Mac /tmp is /private/tmp
        "if not os.environ.get('K4_GO'):\n    sys.exit(0)\n")
# lead_null: a driver loads the tool by its path (as its synthetic tests do), checks the import touched no lab code, then asks for the backend
DRIVER = ("import importlib.util, sys, os, json\nsp = importlib.util.spec_from_file_location('k4ln', sys.argv[1]); m = importlib.util.module_from_spec(sp)\n"
          "sp.loader.exec_module(m)\nopen(os.environ['K4_LOG'], 'a').write('IMPORTED %s\\n' % ('event_outcomes' in sys.modules or 'labcore' in sys.modules))\n"
          "if len(sys.argv) > 2:\n    rs, wf = m.eo_backend(); rs(sys.argv[2], 'IDEA2V1MENU', ['unit__c'])\n")


def package_file(*rel):
    d = HERE
    while not (os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings'))):
        if os.path.dirname(d) == d:
            raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ above %s' % HERE)
        d = os.path.dirname(d)
    return os.path.join(d, *rel)


def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s)


def fake_package(root, lab=True, lab3=True, settings_dir=True):
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
    w(os.path.join(root, 'labcore', '__init__.py'), '')
    for p in (os.path.join(root, 'labcore', 'waves.py'), os.path.join(root, 'event_outcomes.py')):
        w(p, "import os, sys\nopen(os.environ['K4_LOG'], 'a').write('DECOY ' + os.path.realpath(__file__) + '\\n'); sys.exit(0)\n")
    return root


def work_folder(root):
    W = os.path.join(root, 'W')
    w(os.path.join(W, 'V1_FIRES_V1_LIST.tsv'), 'coin\tt\tside\nBTC\t1757900000\t1\n')
    w(os.path.join(W, 'om_V1_v1', 'OUT_CATALOG_IDEA2V1MENU.tsv'), 'OUT.IDEA2V1MENU.unit__c\tx\n')
    return W


def run(text, name, where, go=False, args=(), pythonpath=None, tmp=None):
    p = os.path.join(where, name); w(p, text)
    log = os.path.join(tempfile.mkdtemp(dir=tmp), 'k4.log'); open(log, 'w').close()
    e = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'K4_GO')}
    e.update(K4_LOG=log, PYTHONDONTWRITEBYTECODE='1')
    if go:
        e['K4_GO'] = '1'
    if pythonpath:
        e['PYTHONPATH'] = pythonpath
    if name.startswith('lead_null'):
        d = os.path.join(tmp, 'driver.py'); w(d, DRIVER); cmd = [sys.executable, '-B', d, p] + list(args)
    else:
        cmd = [sys.executable, '-B', p] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=where)
    return r.returncode, r.stdout + r.stderr, [l for l in open(log).read().split('\n') if l]


def check_tool(name, text):
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        pkg = fake_package(os.path.join(tmp, 'A1'))
        want = os.path.realpath(os.path.join(pkg, '01_Detection', 'tree', 'team', 'RESEARCH', 'tools'))
        eo, wv = os.path.join(want, 'event_outcomes', 'event_outcomes.py'), os.path.join(want, 'labcore', 'waves.py')
        code = os.path.join(os.path.realpath(pkg), '01_Detection', 'tree', 'team', 'LAB3', 'code')
        W = work_folder(tmp); om = os.path.join(W, 'om_V1_v1')
        ln = name.startswith('lead_null')
        args, go_want = ([om], ['IMPORTED False', 'LOADED ' + eo, 'LOADED ' + wv, 'READ code=' + code]) if ln else ([W, 'V1'], ['LOADED ' + eo, 'LOADED ' + wv, 'READ code=' + code])
        rc, out, log = run(text, name, os.path.join(pkg, *AT), go=True, args=args, tmp=tmp)          # 1 inside: its own lab tree, its lab3 code
        if rc != 0 or log != go_want:
            fails.append('inside: rc %d log %s %s' % (rc, log, out[-300:]))
        os.makedirs(os.path.join(pkg, '03_Grading', '_tools'))                                      # 2 elsewhere, past a _tools without the reader
        rc, out, log = run(text, name, os.path.join(pkg, '03_Grading', 'tree', 'x'), go=True, args=args, tmp=tmp)
        if rc != 0 or log != go_want:
            fails.append('elsewhere in the package: rc %d log %s' % (rc, log))
        rc, out, log = run(text, name, os.path.join(pkg, *AT), go=True, args=args, pythonpath=decoy_dir(os.path.join(tmp, 'decoy')), tmp=tmp)
        if rc != 0 or log != go_want:                                                               # 3 a decoy first on PYTHONPATH loses
            fails.append('decoy: rc %d log %s' % (rc, log))
        for label, kw, msg in (('no package', None, 'NOT INSIDE AN ALARM PACKAGE'), ('no settings folder', dict(settings_dir=False), 'NOT INSIDE AN ALARM PACKAGE'),
                               ('no lab tree', dict(lab=False), 'NO LAB TREE IN THE ALARM FOLDER'),
                               ('no lab3 code in the lab tree', dict(lab3=False), 'NO LAB TREE IN THE ALARM FOLDER')):   # 4 refusals, nothing loaded
            where = os.path.join(tmp, 'plain', label.replace(' ', '_')) if kw is None else os.path.join(fake_package(os.path.join(tmp, label.replace(' ', '_')), **kw), *AT)
            rc, out, log = run(text, name, where, go=True, args=args, tmp=tmp)
            if rc == 0 or msg not in out or [l for l in log if not l.startswith('IMPORTED False')]:
                fails.append('%s: rc %d log %s out %s' % (label, rc, log, out[-200:]))
        if ln:                                                                                      # 5 lead_null imports anywhere, touching no lab code
            rc, out, log = run(text, name, os.path.join(tmp, 'plain', 'import_only'), tmp=tmp)
            if rc != 0 or log != ['IMPORTED False']:
                fails.append('import outside a package: rc %d log %s %s' % (rc, log, out[-200:]))
        mp = importlib.util.spec_from_file_location('k4_machine_paths', package_file('_tools', 'machine_paths_v2.py'))   # 6 no machine path in code
        M = importlib.util.module_from_spec(mp); mp.loader.exec_module(M)
        rows = [r for r in M.py_rows(text) if r[2] == 'CODE']
        if rows:
            fails.append('machine paths in code: %s' % rows[:3])
    return fails


MUTANTS = [
    (TOOLS, "f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')", "f = os.path.join(sv.alarm_root(__file__), '03_Grading', 'tree')"),
    (TOOLS, "f = os.path.join(sv.alarm_root(__file__), '01_Detection', 'tree')", "f = os.path.join(d, '01_Detection', 'tree')"),
    (TOOLS, "    if not (os.path.isdir(os.path.join(f, 'team', 'LAB3', 'code')) and os.path.isdir(os.path.join(f, 'team', 'RESEARCH', 'tools'))):",
     "    if not os.path.isdir(f):"),
    (TOOLS, "    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):", "    while not os.path.isdir(os.path.join(d, '_tools')):"),
    (TOOLS, "        raise SystemExit('NOT INSIDE AN ALARM PACKAGE: %s' % e)", "        f = os.path.join(d, '01_Detection', 'tree')"),
    (('perfire_v1_1_to20260430.py',), "F = _lab_tree(); CODE = F + '/team/LAB3/code'", "F = _lab_tree(); CODE = F + '/team/LAB3'"),
    (('perfire_v1_1_to20260430.py',), "sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')",
     "sys.path.append(F + '/team/RESEARCH/tools'); sys.path.append(F + '/team/RESEARCH/tools/event_outcomes')"),
    (('lead_null_v1_1_to20251231.py',), "    F = _lab_tree(); CODE = F + '/team/LAB3/code'", "    F = _lab_tree(); CODE = F + '/team/LAB3'"),
    (('lead_null_v1_1_to20251231.py',), "\ndef eo_backend():\n", "\n_EAGER = _lab_tree()\n\n\ndef eo_backend():\n"),
    (('lead_null_v1_1_to20251231.py',), "    sys.path.insert(0, F + '/team/RESEARCH/tools'); sys.path.insert(0, F + '/team/RESEARCH/tools/event_outcomes')",
     "    sys.path.append(F + '/team/RESEARCH/tools'); sys.path.append(F + '/team/RESEARCH/tools/event_outcomes')"),
]


def main():
    texts = {n: open(os.path.join(HERE, n)).read() for n in TOOLS}
    bad = 0
    for n, t in texts.items():
        f = check_tool(n, t)
        print('TESTS %-30s %s' % (n, 'PASS' if not f else 'FAIL %s' % f)); bad += bool(f)
    killed = total = 0
    for tools, a, b in MUTANTS:
        for n in tools:
            assert texts[n].count(a) == 1, ('mutant target not found once', n, a)
            total += 1; caught = bool(check_tool(n, texts[n].replace(a, b, 1))); killed += caught
            print('MUTANT %-30s %-64s %s' % (n, b.strip()[:64], 'KILLED' if caught else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, total))
    return 1 if bad or killed != total else 0


if __name__ == '__main__':
    sys.exit(main())
