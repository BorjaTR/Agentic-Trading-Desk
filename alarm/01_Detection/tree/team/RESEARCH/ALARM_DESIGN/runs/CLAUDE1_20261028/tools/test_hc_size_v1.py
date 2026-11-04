#!/usr/bin/env python3
"""test_hc_size_v1.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): planted tests and
planted bugs for hc_size_v1.py. Temp folders only, seconds; no lab data is read. Each planted Alarm folder holds the real settings
reader, a planted roster (5 coins) and a stand-in hc_defs_v4 that logs its arguments, writes the fires the test plants for its week to
its --out file and holds the memory the test asks for. Run it from inside an Alarm folder:
  python3 -B test_hc_size_v1.py      -> TESTS PASS, then MUTANTS n of n killed; exit 0 only when both hold"""
import importlib.util, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'hc_size_v1.py'
TOOL_DIR = 'team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
FAKE_HC = r'''
import json, os, sys
a = sys.argv[1:]
wk = 'QUIET' if a[5] == '20251110' else 'PROBE'
with open(os.environ['HC_FAKE_LOG'] + '_' + wk, 'w') as f:
    json.dump(a, f)
o = a[a.index('--out') + 1]
with open(o, 'x') as f:
    f.write('coin\tt\tside\n' + ''.join('%s\t%s\t1\n' % tuple(x.split(':')) for x in os.environ.get('HC_FAKE_' + wk, '').split(',') if x))
hold = bytearray(int(os.environ.get('HC_FAKE_MB_' + wk, '1')) * 1024 * 1024)
for i in range(0, len(hold), 4096):
    hold[i] = 1
print('PARSE OK FAKE feedfacefeedface path BASE briefs {}')
print('fires %s per coin {} fires a coin-day 0.00' % wk)
sys.exit(int(os.environ.get('HC_FAKE_RC_' + wk, '0')))
'''
QUIET = 'C1:1000,C2:2800,C1:4601,C3:4602,C1:9000'        # waves [1000,2800] (gap exactly 1800), [4601,4602], [9000]: 3; coins 3
PROBE = ','.join('C%d:%d' % (1 + i % 5, 100000 + 2000 * i) for i in range(40))   # 40 fires 2000 s apart: 40 waves; 5 coins


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
        write(os.path.join(d, 'hc_defs_v4_to20251231.py'), FAKE_HC)
    shutil.copy(src, os.path.join(d, TOOL))
    return os.path.join(d, TOOL)


def settings_file(tmp, name, extra=''):
    _, example = alarm_files()
    keys = [l.split('=', 1)[0] for l in open(example) if '=' in l and not l.lstrip().startswith('#')]
    p = os.path.join(tmp, name)
    write(p, ''.join('%s=\n' % k for k in keys) + extra)
    return p


def run(tool, args, log, quiet=QUIET, probe=PROBE, mbq='90', mbp='5', rcq='0', rcp='0'):
    e = dict(os.environ, HC_FAKE_LOG=log, HC_FAKE_QUIET=quiet, HC_FAKE_PROBE=probe, HC_FAKE_MB_QUIET=mbq, HC_FAKE_MB_PROBE=mbp,
             HC_FAKE_RC_QUIET=rcq, HC_FAKE_RC_PROBE=rcp)
    p = subprocess.run([sys.executable, '-B', tool] + args, capture_output=True, text=True, env=e, cwd=tempfile.gettempdir())
    argv = {w: json.load(open(log + '_' + w)) for w in ('QUIET', 'PROBE') if os.path.isfile(log + '_' + w)}
    return p.returncode, p.stdout, p.stderr, argv


def size_line(out, wk):
    l = [x for x in out.split('\n') if x.startswith('SIZE %s ' % wk)]
    return l[0] if l else ''


def tests(src):
    ok = []
    spec = importlib.util.spec_from_file_location('hc_size_under_test', src); M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    ok.append(('t_waves_gap_rule', M.waves([1000, 2800, 4601, 4602, 9000]) == 3 and M.waves([]) == 0 and M.waves([5, 1, 1802]) == 1))
    ok.append(('t_a_month', M.a_month(8) == 30.0 and M.a_month(3) == 11.25))
    ok.append(('t_weeks', M.WEEKS == (('QUIET', '20251110', '20251117'), ('PROBE', '20251009', '20251016'))))
    ok.append(('t_units', M.peak_mb(1048576, 'darwin') == 1.0 and M.peak_mb(1024, 'linux') == 1.0))
    with tempfile.TemporaryDirectory() as tmp:
        tool = plant(os.path.join(tmp, 'A', 'Alarm'), src)
        S = settings_file(tmp, 'S.env'); dfn = os.path.join(tmp, 'D.json'); write(dfn, '{"id": "X"}')
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l1'))
        q, p = argv.get('QUIET'), argv.get('PROBE')
        ok.append(('t_args_full_roster', q is not None and p is not None and q[:3] == ['--settings', S, '--out']
                   and q[4:] == [dfn, '20251110', '20251117', 'C1,C2,C3,C4,C5', '0', 'NONE']
                   and p[4:] == [dfn, '20251009', '20251016', 'C1,C2,C3,C4,C5', '0', 'NONE']))
        fq = q[3] if q else ''
        lq = size_line(out, 'QUIET')
        ok.append(('t_quiet_line', lq.startswith('SIZE QUIET 20251110..20251117: 5 fires, 3 waves, 3 coins with a fire; 11.2 waves a month (w x 30 / 8); peak ')
                   and lq.endswith('; fire list %s' % fq)))
        lp = size_line(out, 'PROBE')
        ok.append(('t_probe_line', lp.startswith('SIZE PROBE 20251009..20251016: 40 fires, 40 waves, 5 coins with a fire; 150.0 waves a month')))
        pq = int(re.search(r'peak (\d+) MB', lq).group(1)) if 'peak' in lq else -1
        pp = int(re.search(r'peak (\d+) MB', lp).group(1)) if 'peak' in lp else -1
        ok.append(('t_peak_per_child', pq >= 90 and 0 <= pp < 60))   # the second child's own peak, not the running max
        ok.append(('t_quiet_first', 0 <= out.find('SIZE QUIET') < out.find('SIZE PROBE')))
        ok.append(('t_hint_under_30', 'HINT UNDER 30 WAVES A MONTH ON THE QUIET WEEK (11.2)' in out and 'HINT the bar' in out))
        ok.append(('t_fire_lists_kept', os.path.isfile(fq) and open(fq).read().count('\n') == 6 and os.path.isfile(fq.replace('QUIET', 'PROBE'))))
        ok.append(('t_hand_check_last_line', 'QUIET: fires QUIET per coin' in out and 'PROBE: fires PROBE per coin' in out))
        busy = ','.join('C1:%d' % (10 ** 6 + 2000 * i) for i in range(9))       # 9 waves: 33.75 a month: no UNDER hint
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l2'), quiet=busy)
        ok.append(('t_no_under_hint_at_33', rc == 0 and 'HINT UNDER' not in out and '33.8 waves a month' in out and 'HINT the bar' in out))
        eight = ','.join('C1:%d' % (10 ** 6 + 2000 * i) for i in range(8))      # 8 waves: exactly 30 a month: not under
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l2b'), quiet=eight)
        ok.append(('t_30_is_not_under', rc == 0 and 'HINT UNDER' not in out and '30.0 waves a month' in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l3'), rcp='1')
        ok.append(('t_hand_check_failure_refused', rc == 2 and 'HAND CHECK FAILED ON PROBE rc 1' in err and 'HINT' not in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l3b'), quiet='')
        ok.append(('t_zero_fires', rc == 0 and 'SIZE QUIET 20251110..20251117: 0 fires, 0 waves, 0 coins with a fire; 0.0 waves a month' in out))
        bad = settings_file(tmp, 'S_BAD.env', 'NOT_A_KEY=\n')
        rc, out, err, argv = run(tool, ['--settings', bad, dfn], os.path.join(tmp, 'l4'))
        ok.append(('t_bad_settings_refused_before_the_run', rc == 2 and not argv))
        rc, out, err, argv = run(tool, [dfn], os.path.join(tmp, 'l5'))
        ok.append(('t_settings_required', rc == 2 and 'USAGE' in err and not argv))
        nj = os.path.join(tmp, 'N.json'); write(nj, 'not json')
        rc, out, err, argv = run(tool, ['--settings', S, nj], os.path.join(tmp, 'l6'))
        ok.append(('t_bad_definition_refused', rc == 2 and 'DEFINITION UNREADABLE' in err and not argv))
        t2 = plant(os.path.join(tmp, 'B', 'Alarm'), src, roster=False)
        rc, out, err, argv = run(t2, ['--settings', S, dfn], os.path.join(tmp, 'l7'))
        ok.append(('t_no_roster_refused', rc == 2 and 'NO ROSTER' in err and not argv))
        lone = os.path.join(tmp, 'lone'); os.makedirs(lone); shutil.copy(src, os.path.join(lone, TOOL))
        rc, out, err, argv = run(os.path.join(lone, TOOL), ['--settings', S, dfn], os.path.join(tmp, 'l8'))
        ok.append(('t_outside_alarm_refused', rc == 2 and 'NOT INSIDE AN ALARM FOLDER' in err))
    return ok


MUTANTS = [
    ("        if prev is None or t - prev > GAP:", "        if prev is None or t - prev >= GAP:"),
    ("    return w * 30.0 / DAYS_A_WEEK", "    return w * 30.0 / 7"),
    ("WEEKS = (('QUIET', '20251110', '20251117'),", "WEEKS = (('QUIET', '20251110', '20251116'),"),
    ("    if quiet_month < UNDER:", "    if quiet_month <= UNDER:"),
    ("    if quiet_month < UNDER:", "    if False:"),
    ("        if name == 'QUIET':\n            quiet = a_month(w)", "        quiet = a_month(w)"),
    ("','.join(coins), '0', 'NONE']", "','.join(coins[len(coins) // 2:]), '0', 'NONE']"),
    ("int(round(peak_mb(ru.ru_maxrss)))", "int(round(peak_mb(__import__('resource').getrusage(__import__('resource').RUSAGE_CHILDREN).ru_maxrss)))"),
    ("        if rc != 0:\n", "        if False:\n"),
    ("len({c for c, _ in fires})", "len(fires)"),
    ("        S.load(settings)\n", "        pass\n"),
    ("            json.load(open(defn))\n", "            pass\n"),
    ("'--settings', settings, '--out', fl, defn,", "'--settings', settings, '--out', fl + '.x', defn,"),
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
            try:
                k = not all(v for _, v in tests(p))
            except Exception:
                k = True
            killed += k
            print('MUTANT %d: %s' % (i, 'KILLED' if k else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(MUTANTS)))
    sys.exit(0 if not fails and killed == len(MUTANTS) else 1)


if __name__ == '__main__':
    main()
