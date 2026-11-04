#!/usr/bin/env python3
"""mutants_inputs_read_v1.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED): planted bugs in tools/inputs_read_v1.py; every one must make
tests/test_inputs_read_v1.py fail. The unchanged copy must pass first. Each run copies the three registry tools and the test into a
temp REGISTRY layout (bytes only: the source may be a read-only install) and plants one bug in inputs_read_v1.py.

  python3 -B <REGISTRY>/tests/mutants_inputs_read_v1.py [--alarm <Alarm package>]   (--alarm as in the test file)
Exit 0: every planted bug killed; 1: one lived; 2: the unchanged code fails its tests."""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.dirname(HERE), 'tools')
M = [
    ("    return f.split(':', 1)[0].strip() if f else 'OK'", "    return 'OK'"),                                    # every flag OK
    ("        return 'NO ROW'", "        return 'OK'"),                                                                 # no LAB4 row read as OK
    ("        if want not in ('', '-') and sha16(p) != want:", "        if False:"),                                  # a changed definition read
    ("            skip['missing'].append(a)", "            skip['none'].append(a)"),                                    # missing counted as none
    ("        if i and re.fullmatch(r'S[0-9]+', p):", "        if False:"),                                           # settings grouped apart
    ("        if r['flag'] == 'OK' and r['alarms_n'] == 0 and", "        if r['alarms_n'] == 0 and"),                 # CAUTION offered as unread
    ("    return SB.state_of(r) or cell(r.get('state') or '-')", "    return cell(r.get('state') or '-')"),          # not the scoreboard's words
    ("                    'found': sum(1 for r in rs if SB.verdict(r) == 'FOUND'),", "                    'found': 0,"),  # FOUND not counted
    ("NV.outside(p['--page'], alarm, S)", "p['--page']"),                                                               # page inside the package
    ("NV.outside(p['--out'], alarm, S)", "p['--out']"),                                                                 # table inside the package
    ("    if os.path.exists(path):", "    if False:"),                                                                  # no twin
    ("isinstance(v, dict) and isinstance(v.get('code'), str)", "isinstance(v, dict) and v.get('op') == 'raw' and isinstance(v.get('code'), str)"),  # market inputs missed
    ("'flag': flag_word(MB, trap) if (c in cards or c in traps) else 'NOT IN TABLES',", "'flag': flag_word(MB, trap),"),  # unknown code as NO ROW
    ("            cards.setdefault(r['code'], r)", "            pass"),                                                 # catalogues ignored
    ("        found = sum(1 for r in rs if SB.verdict(r) == 'FOUND')", "        found = 0"),                            # family FOUND not counted
    ("    p = {k: NV.under(v, design) for k, v in o.items()}", "    p = {k: v for k, v in o.items()}"),                 # paths under the working folder
]


def run(src, alarm):
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, 'tools')); os.makedirs(os.path.join(d, 'tests'))
        for n in ('novelty_v2.py', 'scoreboard_v2.py'):
            shutil.copyfile(os.path.join(TOOLS, n), os.path.join(d, 'tools', n))
        with open(os.path.join(d, 'tools', 'inputs_read_v1.py'), 'w') as f:
            f.write(src)
        shutil.copyfile(os.path.join(HERE, 'test_inputs_read_v1.py'), os.path.join(d, 'tests', 'test_inputs_read_v1.py'))
        return subprocess.run([sys.executable, '-B', os.path.join(d, 'tests', 'test_inputs_read_v1.py'), '--alarm', alarm],
                              capture_output=True, text=True, timeout=600).returncode


def find_alarm(start):
    d = os.path.dirname(os.path.abspath(start))
    while True:
        if os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings')):
            return d
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)


def main(a):
    alarm = os.path.abspath(a[a.index('--alarm') + 1]) if '--alarm' in a else find_alarm(__file__)
    if not alarm:
        print('NO ALARM PACKAGE: run this file inside an Alarm package, or name one with --alarm'); return 2
    with open(os.path.join(TOOLS, 'inputs_read_v1.py')) as f:
        src = f.read()
    for old, new in M:
        assert src.count(old) == 1, ('NOT ONCE', old)
    if run(src, alarm):
        print('THE UNCHANGED CODE FAILS ITS TESTS'); return 2
    alive = [i for i, (o, n) in enumerate(M, 1) if not run(src.replace(o, n), alarm)]
    for i, (o, n) in enumerate(M, 1):
        print('%2d %s %s' % (i, 'ALIVE ' if i in alive else 'KILLED', o.strip()[:90]))
    print('mutants %d, killed %d, alive %d' % (len(M), len(M) - len(alive), len(alive)))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
