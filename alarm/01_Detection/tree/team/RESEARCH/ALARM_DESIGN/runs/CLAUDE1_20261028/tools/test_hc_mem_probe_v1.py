#!/usr/bin/env python3
"""test_hc_mem_probe_v1.py: planted tests and planted bugs for hc_mem_probe_v1.py. Temp folders only, seconds; no lab data is read.

Owner: SCOUT (the alarm kit). New by SCOUT for the clean release (K7, 30 Oct 2026); it replaces no file. Each planted Alarm folder holds
the real settings reader, a planted roster (5 coins) and a stand-in hand check beside the probe that logs its arguments, holds the
memory the test asks for (HC_FAKE_MB) and exits with HC_FAKE_RC. It runs no old edition. Run it from inside an Alarm folder:
  python3 -B test_hc_mem_probe_v1.py      -> TESTS PASS, then MUTANTS n of n killed; exit 0 only when both hold"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'hc_mem_probe_v1.py'
TOOL_DIR = 'team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
FAKE_HC = r'''
import json, os, sys
with open(os.environ['HC_FAKE_LOG'], 'w') as f:
    json.dump(sys.argv[1:], f)
hold = bytearray(int(os.environ.get('HC_FAKE_MB', '1')) * 1024 * 1024)
for i in range(0, len(hold), 4096):
    hold[i] = 1
print('PARSE OK FAKE feedfacefeedface path BASE briefs {}')
print('fires 0 per coin {} fires a coin-day 0.00')
sys.exit(int(os.environ.get('HC_FAKE_RC', '0')))
'''


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


def plant(root, src, roster=True, hand_check=True):
    reader, example = alarm_files()
    os.makedirs(os.path.join(root, '_tools')); os.makedirs(os.path.join(root, 'settings'))
    shutil.copy(reader, os.path.join(root, '_tools')); shutil.copy(example, os.path.join(root, 'settings'))
    tree = os.path.join(root, '01_Detection', 'tree')
    if roster:
        write(os.path.join(tree, *ROSTER.split('/')), json.dumps({'coins': ['C1', 'C2', 'C3', 'C4', 'C5']}))
    d = os.path.join(tree, *TOOL_DIR.split('/')); os.makedirs(d, exist_ok=True)
    if hand_check:
        write(os.path.join(d, 'hc_defs_v2_to20251231.py'), FAKE_HC)
    shutil.copy(src, os.path.join(d, TOOL))
    return os.path.join(d, TOOL)


def settings_file(tmp, name, extra=''):
    _, example = alarm_files()
    keys = [l.split('=', 1)[0] for l in open(example) if '=' in l and not l.lstrip().startswith('#')]
    p = os.path.join(tmp, name)
    write(p, ''.join('%s=\n' % k for k in keys) + extra)
    return p


def run(tool, args, log, mb='1', rc='0'):
    e = dict(os.environ, HC_FAKE_LOG=log, HC_FAKE_MB=mb, HC_FAKE_RC=rc)
    p = subprocess.run([sys.executable, '-B', tool] + args, capture_output=True, text=True, env=e, cwd=tempfile.gettempdir())
    argv = json.load(open(log)) if os.path.isfile(log) else None
    return p.returncode, p.stdout, p.stderr, argv


def peak_of(out):
    line = [l for l in out.split('\n') if l.startswith('PEAK ')]
    return int(line[0].split()[1]) if line else -1


def tests(src):
    ok = []
    spec = importlib.util.spec_from_file_location('hc_mem_probe_under_test', src); M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    ok.append(('t_half_b_function', M.half_b(['a', 'b', 'c', 'd', 'e']) == ['c', 'd', 'e'] and M.half_b(['a', 'b', 'c', 'd']) == ['c', 'd']))
    ok.append(('t_units', M.peak_mb(1048576, 'darwin') == 1.0 and M.peak_mb(1024, 'linux') == 1.0))
    ok.append(('t_verdict_at_limit_passes', M.verdict(732, 732) == 'PASS' and M.verdict(733, 732) == 'OVER'))
    ok.append(('t_default_limit_732', M.LIMIT_MB == 732))
    with tempfile.TemporaryDirectory() as tmp:
        tool = plant(os.path.join(tmp, 'A', 'Alarm'), src)
        S = settings_file(tmp, 'S.env'); dfn = os.path.join(tmp, 'D.json'); write(dfn, '{}')
        rc, out, err, argv = run(tool, ['--settings', S, dfn, '--limit-mb', '4000'], os.path.join(tmp, 'l1'), mb='40')
        ok.append(('t_hand_check_args', argv == ['--settings', S, dfn, '20251009', '20251016', 'C3,C4,C5', '0', 'NONE']))
        ok.append(('t_pass', rc == 0 and out.rstrip().endswith(': PASS') and 'limit 4000 MB' in out and peak_of(out) >= 40))
        ok.append(('t_prints_hand_check_lines', 'PARSE OK FAKE' in out and 'fires 0 per coin' in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn, '--limit-mb', '30'], os.path.join(tmp, 'l2'), mb='60')
        ok.append(('t_over', rc == 1 and out.rstrip().endswith(': OVER') and peak_of(out) >= 60))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l3'))
        ok.append(('t_default_limit_printed', 'limit 732 MB' in out and 'half B 3 coins, 20251009..20251016' in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l4'), rc='1')
        ok.append(('t_hand_check_failure_refused', rc == 2 and 'HAND CHECK FAILED rc 1' in err and 'PEAK' not in out))
        bad = settings_file(tmp, 'S_BAD.env', 'NOT_A_KEY=\n')
        rc, out, err, argv = run(tool, ['--settings', bad, dfn], os.path.join(tmp, 'l5'))
        ok.append(('t_bad_settings_refused_before_the_run', rc == 2 and argv is None))
        rc, out, err, argv = run(tool, [dfn], os.path.join(tmp, 'l6'))
        ok.append(('t_settings_required', rc == 2 and 'USAGE' in err and argv is None))
        t2 = plant(os.path.join(tmp, 'B', 'Alarm'), src, roster=False)
        rc, out, err, argv = run(t2, ['--settings', S, dfn], os.path.join(tmp, 'l7'))
        ok.append(('t_no_roster_refused', rc == 2 and 'NO ROSTER' in err and argv is None))
        lone = os.path.join(tmp, 'lone'); os.makedirs(lone); shutil.copy(src, os.path.join(lone, TOOL))
        rc, out, err, argv = run(os.path.join(lone, TOOL), ['--settings', S, dfn], os.path.join(tmp, 'l8'))
        ok.append(('t_outside_alarm_refused', rc == 2 and 'NOT INSIDE AN ALARM FOLDER' in err))
    return ok


MUTANTS = [
    ("return coins[len(coins) // 2:]", "return coins[:len(coins) // 2]"),
    ("DAYS = ('20251009', '20251016')", "DAYS = ('20251009', '20251009')"),
    ("return 'PASS' if mb <= limit else 'OVER'", "return 'PASS' if mb < limit else 'OVER'"),
    ("return ru_maxrss / (1024.0 * 1024.0) if platform == 'darwin' else ru_maxrss / 1024.0",
     "return ru_maxrss / 1024.0 if platform == 'darwin' else ru_maxrss / (1024.0 * 1024.0)"),
    ("    if p.returncode != 0:\n", "    if False:\n"),
    ("LIMIT_MB = 732", "LIMIT_MB = 1024"),
    ("','.join(coins), '0', 'NONE']", "','.join(coins), '5', 'NONE']"),
    ("        S.load(settings)\n", "        pass\n"),
    ("    return 0 if v == 'PASS' else 1", "    return 0"),
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
