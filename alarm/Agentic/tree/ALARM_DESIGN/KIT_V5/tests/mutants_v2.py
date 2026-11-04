"""mutants_v2.py (SCOUT helper K2, 30 Oct 2026; TEST, NOT REVIEWED): planted bugs in the clean editions decide_v2.py, decide_forward_v2.py,
audit_run_v3.py, board_line_v2.py and idea_time_v2.py; each must make test_kit5_tools_v2.py fail. For each bug: a new temporary copy of
only the package files those tests read (about 20 small files, never the whole kit), the bug planted in the copy, the copy's own tests
run, the copy removed at once (mutants_v1.py left a whole kit per bug behind and filled the VM's disk on 30 Oct). The unchanged copy
must pass first; a bug whose text is not in its file exactly once, or that breaks the file's syntax, stops the run.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/mutants_v2.py [N-M]      (from an Alarm package; N-M: only those bugs)
Exit 0: every bug caught; 1: a bug missed (listed); 2: refused (the unchanged copy fails, or a bug's text is wrong)."""
import ast
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.dirname(os.path.dirname(HERE))
TREE = ('Agentic', 'tree', 'ALARM_DESIGN')
NEEDED = ['KIT_V5/tools/decide_v2.py', 'KIT_V5/tools/decide_forward_v2.py', 'KIT_V5/tools/audit_run_v3.py', 'KIT_V5/tools/board_line_v2.py',
          'KIT_V6/tools/idea_time_v2.py', 'KIT_V5/tools/queue_job_v5.py', 'KIT_V5/tests/test_kit5_tools_v2.py',
          'runs/CLAUDE1_20261028/tools/reg_append_v1.py', 'runs/CLAUDE1_20261028/tools/read_stratentry_v1.py']
EDITION1 = ['KIT_V5/tools/decide_v1.py', 'KIT_V5/tools/decide_forward_v1.py', 'KIT_V5/tools/audit_run_v2.py', 'KIT_V5/tools/board_line_v1.py',
            'KIT_V6/tools/idea_time_v1.py',
            'KIT_V5/tools/queue_job_v4.py']          # copied when present: the tests compare edition 2 with them (decide_v1 reads its
                                                     # run budget from queue_job_v4.py next to it; edition 2 reads queue_job_v5.py)
D, F, A, B, I = ('KIT_V5/tools/decide_v2.py', 'KIT_V5/tools/decide_forward_v2.py', 'KIT_V5/tools/audit_run_v3.py', 'KIT_V5/tools/board_line_v2.py',
                 'KIT_V6/tools/idea_time_v2.py')
M = [
 # decide_v2.py: where things are
 (D, "    CFG.update({'H': os.path.join(research, 'ALARM_DESIGN'), 'REG': os.path.join(t1, 'reg_append_v1.py'),",
     "    CFG.update({'H': research, 'REG': os.path.join(t1, 'reg_append_v1.py'),"),
 (D, "    t1 = os.path.join(alarm, *RUN_TOOLS)", "    t1 = os.path.join(os.path.dirname(alarm), *RUN_TOOLS)"),
 (D, "    if not opts['--settings']:\n", "    if False:\n"),
 (D, "        research = S.get(settings, 'RESEARCH_ROOT')\n    except S.Refused as e:",
     "        research = S.get(settings, 'RESEARCH_ROOT')\n    except KeyError as e:"),
 (D, "        research = S.get(settings, 'RESEARCH_ROOT')\n    except S.Refused as e:",
     "        research = S.load(settings)['RESEARCH_ROOT']\n    except S.Refused as e:"),
 (D, "    d = os.path.dirname(os.path.abspath(__file__))\n    while not", "    d = os.getcwd()\n    while not"),
 (D, "    qp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue_job_v5.py')",
     "    qp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queue_job_v4.py')"),          # the past edition read
 # decide_v2.py: the checks kept from edition 1
 (D, "    if sha16(CFG['RSE']) != CFG['RSE_SHA']:", "    if False:"),
 (D, "        if sha16(CFG['REG']) != CFG['REG_SHA']:", "        if False:"),
 (D, "    elif rules.get('R1') != 'PASS':", "    elif rules.get('R2') != 'PASS':"),
 (D, "        if srow.get('gate') != 'PASS':", "        if False:"),
 # decide_forward_v2.py
 (F, "    CFG.update({'H': os.path.join(research, 'ALARM_DESIGN'), 'REG': os.path.join(alarm, *RUN_TOOLS, 'reg_append_v1.py')})",
     "    CFG.update({'H': research, 'REG': os.path.join(alarm, *RUN_TOOLS, 'reg_append_v1.py')})"),
 (F, "'REG': os.path.join(alarm, *RUN_TOOLS, 'reg_append_v1.py')})", "'REG': os.path.join(alarm, 'reg_append_v1.py')})"),
 (F, "    if not settings:\n        raise Refused(", "    if False:\n        raise Refused("),
 (F, "        if sha16(CFG['REG']) != CFG['REG_SHA']:", "        if False:"),
 (F, "    elif len(holds) >= 3:", "    elif len(holds) >= 2:"),
 # audit_run_v3.py
 (A, "'HB': board, 'RUNNER': runner,", "'HB': os.path.join(research, 'hb'), 'RUNNER': runner,"),
 (A, "        runner = S.load(settings).get('RUNNER_QUEUES', '')", "        runner = ''"),
 (A, "'RUNNER': runner, 'SETTINGS': os.path.abspath(settings)})", "'RUNNER': runner, 'SETTINGS': None})"),
 (A, "                if CFG['SETTINGS']:\n                    D.configure(CFG['SETTINGS'])", "                if False:\n                    D.configure(CFG['SETTINGS'])"),
 (A, "'decide_v2.py'), 'DECIDE_CFG': {},", "'decide_v1.py'), 'DECIDE_CFG': {},"),
 (A, "        lines = ['AUDIT %s (audit_run_v3.py, %s).", "        lines = ['AUDIT %s (audit_run_v2.py, %s)."),
 (A, "'months_counted', 'waves'):\n                    if str(d.get(k, '')) != r.get(k, ''):", "'months_counted', 'waves'):\n                    if False:"),
 (A, "'months_passing'):\n                        if str(d.get(k, '')) != r.get(k, ''):", "'months_passing'):\n                        if False:"),
 (A, "                if lag > 20:", "                if lag > 2000:"),
 (A, "                if not (prob and stuck):", "                if False:"),
 # board_line_v2.py
 (B, "        CFG['HB'] = S.get(settings, 'BOARD')", "        CFG['HB'] = S.get(settings, 'RESEARCH_ROOT')"),
 (B, "    configure(settings)\n    p = os.path.join(CFG['HB'], seat + '.txt')", "    p = os.path.join(CFG['HB'] or '.', seat + '.txt')"),
 (B, "    if len(line) >= LIMIT:", "    if False:"),
 (B, "            except FileExistsError:\n                k += 1", "            except ZeroDivisionError:\n                k += 1"),
 # idea_time_v2.py
 (I, "    p = os.path.join(HB, seat + '.txt')", "    p = os.path.join(H, seat + '.txt')"),
 (I, "    H, HB = os.path.join(research, 'ALARM_DESIGN'), board", "    H, HB = research, board"),
 (I, "        if a == '--settings':", "        if a == '--settingz':"),
 (I, "        if not settings:\n            raise Refused(", "        if False:\n            raise Refused("),
]


def package_of(d):
    while not (os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings'))):
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)
    return d


def copy_package(alarm, dst):
    """the files the tests read, content only (a read-only install gives writable copies)"""
    rels = ['_tools/settings_v1.py', 'settings/SETTINGS_EXAMPLE.env'] + ['Agentic/tree/fixtures/kit5_test/DP2_%s' % x for x in ('CURVE.tsv', 'GATES.json', 'TABLE_W0.tsv')]
    rels += ['/'.join(TREE) + '/' + r for r in NEEDED + [e for e in EDITION1 if os.path.isfile(os.path.join(AD, e))]]
    for rel in rels:
        p = os.path.join(dst, *rel.split('/'))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        shutil.copyfile(os.path.join(alarm, *rel.split('/')), p)


def run_copy(alarm, plant=None):
    d = tempfile.mkdtemp(prefix='k2mut_')
    try:
        a = os.path.join(d, 'Alarm')
        copy_package(alarm, a)
        if plant:
            p = os.path.join(a, *(TREE + tuple(plant[0].split('/'))))
            with open(p) as f:
                s = f.read()
            with open(p, 'w') as f:
                f.write(s.replace(plant[1], plant[2]))
        r = subprocess.run([sys.executable, '-B', '-W', 'ignore', os.path.join(a, *(TREE + ('KIT_V5', 'tests', 'test_kit5_tools_v2.py')))],
                           capture_output=True, text=True, cwd=d, timeout=150)
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:]
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main(argv):
    alarm = package_of(HERE)
    if alarm is None:
        print('REFUSED: run from an Alarm package (no _tools/settings_v1.py above %s)' % HERE)
        return 2
    lo, hi = 1, len(M)
    if argv:
        lo, hi = (int(x) for x in argv[0].split('-'))
    for k, (rel, old, new) in enumerate(M, 1):
        with open(os.path.join(AD, rel)) as f:
            s = f.read()
        if s.count(old) != 1:
            print('REFUSED: bug %d: its text is in %s %d times, not once: %r' % (k, rel, s.count(old), old[:70]))
            return 2
        try:
            ast.parse(s.replace(old, new))
        except SyntaxError as e:
            print('REFUSED: bug %d breaks the syntax of %s: %s' % (k, rel, e))
            return 2
    rc, last = run_copy(alarm)
    print('unchanged copy: %s %s' % ('PASS' if rc == 0 else 'FAILS', ' '.join(last)), flush=True)
    if rc:
        return 2
    alive = []
    for k, m in enumerate(M, 1):
        if not lo <= k <= hi:
            continue
        rc, last = run_copy(alarm, m)
        print('bug %2d %-24s %-7s %s' % (k, os.path.basename(m[0]), 'CAUGHT' if rc else 'MISSED', m[1].strip().split('\n')[0][:80]), flush=True)
        if not rc:
            alive.append(k)
    n = hi - lo + 1
    print('bugs %d, caught %d, missed %d%s' % (n, n - len(alive), len(alive), (': ' + ', '.join(map(str, alive))) if alive else ''))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
