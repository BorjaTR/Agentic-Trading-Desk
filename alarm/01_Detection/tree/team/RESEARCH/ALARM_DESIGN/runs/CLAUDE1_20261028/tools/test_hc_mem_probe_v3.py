#!/usr/bin/env python3
"""test_hc_mem_probe_v3.py (SCOUT, 2 Nov 2026, V1_18_FIXES): every test of v2 on hc_mem_probe_v3 with the limit from the code cap, plus the cap read from planted detectors, the real pairs of run SCOUT_20261101, and refusals.
test_hc_mem_probe_v2.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): every
test of test_hc_mem_probe_v1.py on hc_mem_probe_v2 (the stand-in is now hc_defs_v4_to20251231.py and writes the fires of
HC_FAKE_FIRES to its --out file; the definition has 4 inputs), plus WAVES (the gap rule, a gap of exactly 1800 s stays in the wave),
MB PER INPUT, the fire list kept, and a definition with no inputs refused. v1's text follows.
test_hc_mem_probe_v1.py: planted tests and planted bugs for hc_mem_probe_v1.py. Temp folders only, seconds; no lab data is read.

Owner: SCOUT (the alarm kit). New by SCOUT for the clean release (K7, 30 Oct 2026); it replaces no file. Each planted Alarm folder holds
the real settings reader, a planted roster (5 coins) and a stand-in hand check beside the probe that logs its arguments, holds the
memory the test asks for (HC_FAKE_MB) and exits with HC_FAKE_RC. It runs no old edition. Run it from inside an Alarm folder:
  python3 -B test_hc_mem_probe_v1.py      -> TESTS PASS, then MUTANTS n of n killed; exit 0 only when both hold"""
import importlib.util, json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'hc_mem_probe_v3.py'
TOOL_DIR = 'team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
FAKE_HC = r'''
import json, os, sys
with open(os.environ['HC_FAKE_LOG'], 'w') as f:
    json.dump(sys.argv[1:], f)
a = sys.argv[1:]
o = a[a.index('--out') + 1]
with open(o, 'x') as f:
    f.write('coin\tt\tside\n' + ''.join('C3\t%s\t1\n' % t for t in os.environ.get('HC_FAKE_FIRES', '').split(',') if t))
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


CAP_RELS = ('team/RESEARCH/tools/alarm_process/detect_aw1.py', 'team/RESEARCH/tools/idea_to_grade/detect_v2.py', 'team/RESEARCH/tools/idea_to_grade/detect_gm1.py')
CAP2G = 'import os\nWORKER_RSS_CAP = 2 * 1024 ** 3   # 16 GiB / 8 workers\n'


def plant(root, src, roster=True, hand_check=True, caps=(CAP2G, CAP2G, CAP2G)):
    reader, example = alarm_files()
    os.makedirs(os.path.join(root, '_tools')); os.makedirs(os.path.join(root, 'settings'))
    shutil.copy(reader, os.path.join(root, '_tools')); shutil.copy(example, os.path.join(root, 'settings'))
    tree = os.path.join(root, '01_Detection', 'tree')
    for rel, text in zip(CAP_RELS, caps):
        if text is not None:
            write(os.path.join(tree, *rel.split('/')), text)
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


FIRES = '1000,2800,4601,4602,9000'   # waves: [1000, 2800] (gap exactly 1800), [4601, 4602], [9000] -> 3


def run(tool, args, log, mb='1', rc='0', fires=FIRES):
    e = dict(os.environ, HC_FAKE_LOG=log, HC_FAKE_MB=mb, HC_FAKE_RC=rc, HC_FAKE_FIRES=fires)
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
    ok.append(('t_verdict_at_limit_passes', M.verdict(1272, 1272) == 'PASS' and M.verdict(1273, 1272) == 'OVER'))
    ok.append(('t_limit_from_the_cap', M.limit_from_cap(2 * 1024 ** 3) == 1272 and M.limit_from_cap(1024 ** 3) == 636))
    ok.append(('t_stale_line_gone', '7' + '32' not in open(src).read()))
    L = M.limit_from_cap(2 * 1024 ** 3)
    ok.append(('t_real_passes_pass', all(M.verdict(x, L) == 'PASS' for x in (826, 981, 1000, 1053, 1121, 1200, 1229, 1233))))
    ok.append(('t_real_cap_death_over', M.verdict(1283, L) == 'OVER'))
    ok.append(('t_death_bytes_in_mb_above_cap', int(round(M.peak_mb(2166620160, 'darwin'))) == 2066 and 2166620160 > 2 * 1024 ** 3))
    ok.append(('t_worker_estimate', M.worker_estimate(1283) == 2066 and M.worker_estimate(1000) == 1610))
    with tempfile.TemporaryDirectory() as tmp:
        tool = plant(os.path.join(tmp, 'A', 'Alarm'), src)
        S = settings_file(tmp, 'S.env'); dfn = os.path.join(tmp, 'D.json'); write(dfn, json.dumps({'inputs': {'a': {}, 'b': {}, 'c': {}, 'd': {}}}))
        rc, out, err, argv = run(tool, ['--settings', S, dfn, '--limit-mb', '2000'], os.path.join(tmp, 'l1'), mb='40')
        ok.append(('t_hand_check_args', argv is not None and argv[:3] == ['--settings', S, '--out'] and argv[4:] == [dfn, '20251009', '20251016', 'C3,C4,C5', '0', 'NONE']))
        fl = argv[3] if argv else ''
        ok.append(('t_waves_line', ('WAVES 3 on half B, 20251009..20251016 (5 fires; fire list %s)' % fl) in out))
        ok.append(('t_fire_list_kept', os.path.isfile(fl) and open(fl).read().count('\n') == 6 and os.path.basename(fl) == 'FIRES.tsv'))
        pk = peak_of(out)
        ok.append(('t_mb_per_input', ('MB PER INPUT %.1f (peak %d MB / 4 inputs of the definition)' % (pk / 4.0, pk)) in out))
        ok.append(('t_peak_line_last', out.rstrip().split('\n')[-1].startswith('PEAK ')))
        ok.append(('t_pass', rc == 0 and out.rstrip().endswith(': PASS') and 'limit 2000 MB' in out and peak_of(out) >= 40))
        ok.append(('t_prints_hand_check_lines', 'PARSE OK FAKE' in out and 'fires 0 per coin' in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn, '--limit-mb', '30'], os.path.join(tmp, 'l2'), mb='60')
        ok.append(('t_over', rc == 1 and out.rstrip().endswith(': OVER') and peak_of(out) >= 60))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l3'))
        ok.append(('t_default_limit_printed', 'limit 1272 MB' in out and 'WORKER_RSS_CAP 2048 MB' in out and 'worker estimate' in out and 'half B 3 coins, 20251009..20251016' in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l4'), rc='1')
        ok.append(('t_hand_check_failure_refused', rc == 2 and 'HAND CHECK FAILED rc 1' in err and 'PEAK' not in out))
        rc, out, err, argv = run(tool, ['--settings', S, dfn], os.path.join(tmp, 'l9'), fires='')
        ok.append(('t_no_fires_zero_waves', rc == 0 and 'WAVES 0 on half B' in out and '(0 fires;' in out))
        nod = os.path.join(tmp, 'N.json'); write(nod, '{}')
        rc, out, err, argv = run(tool, ['--settings', S, nod], os.path.join(tmp, 'l10'))
        ok.append(('t_no_inputs_refused', rc == 2 and 'NO "inputs" OBJECT' in err and argv is None))
        rc, out, err, argv = run(tool, ['--settings', S, dfn, '--limit-mb', '2049'], os.path.join(tmp, 'l11'))
        ok.append(('t_limit_above_cap_refused', rc == 2 and 'ABOVE' in err and argv is None))
        CAP1G = 'WORKER_RSS_CAP = 1024 ** 3\n'
        t3 = plant(os.path.join(tmp, 'C', 'Alarm'), src, caps=(CAP1G, CAP1G, CAP1G))
        rc, out, err, argv = run(t3, ['--settings', S, dfn], os.path.join(tmp, 'l12'))
        ok.append(('t_cap_read_from_the_code', 'limit 636 MB' in out and 'WORKER_RSS_CAP 1024 MB' in out))
        t4 = plant(os.path.join(tmp, 'D', 'Alarm'), src, caps=(CAP2G, CAP1G, CAP2G))
        rc, out, err, argv = run(t4, ['--settings', S, dfn], os.path.join(tmp, 'l13'))
        ok.append(('t_caps_disagree_refused', rc == 2 and 'DISAGREE' in err and argv is None))
        t5 = plant(os.path.join(tmp, 'E', 'Alarm'), src, caps=(CAP2G, None, CAP2G))
        rc, out, err, argv = run(t5, ['--settings', S, dfn], os.path.join(tmp, 'l14'))
        ok.append(('t_cap_file_missing_refused', rc == 2 and 'NO DETECTOR' in err and argv is None))
        t6 = plant(os.path.join(tmp, 'G', 'Alarm'), src, caps=('X = 1\n', CAP2G, CAP2G))
        rc, out, err, argv = run(t6, ['--settings', S, dfn], os.path.join(tmp, 'l15'))
        ok.append(('t_no_cap_constant_refused', rc == 2 and 'NO WORKER_RSS_CAP' in err and argv is None))
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
    ("WORKER_PER_PROBE = 1.61", "WORKER_PER_PROBE = 1.0"),
    ("WORKER_PER_PROBE = 1.61", "WORKER_PER_PROBE = 2.8"),
    ("    return int(cap_bytes / (1024.0 * 1024.0) / WORKER_PER_PROBE)", "    return int(2048 / WORKER_PER_PROBE)"),
    ("    return int(cap_bytes / (1024.0 * 1024.0) / WORKER_PER_PROBE)", "    return int(cap_bytes / 1e6 / WORKER_PER_PROBE)"),
    ("    return int(round(mb * WORKER_PER_PROBE))", "    return mb"),
    ("    if len(set(caps.values())) != 1:", "    if False:"),
    ("        if not os.path.isfile(p):\n            raise Refused('NO DETECTOR", "        if False:\n            raise Refused('NO DETECTOR"),
    ("        if limit is not None and limit > cap_mb:", "        if False:"),
    ("        limit = limit_from_cap(cap) if limit is None else limit", "        limit = 1272 if limit is None else limit"),
    ("','.join(coins), '0', 'NONE']", "','.join(coins), '5', 'NONE']"),
    ("        S.load(settings)\n", "        pass\n"),
    ("    return 0 if v == 'PASS' else 1", "    return 0"),
    ("        if prev is None or t - prev > GAP:", "        if prev is None or t - prev >= GAP:"),
    ("    for t in sorted(times):", "    for t in times[::-1]:"),
    ("mb / float(k), mb, k", "mb / float(k + 1), mb, k"),
    ("        k = n_inputs(defn)\n", "        k = 4\n"),
    ("'--settings', settings, '--out', fl, defn,", "'--settings', settings, defn,"),
    ("    if not isinstance(d, dict) or not isinstance(d.get('inputs'), dict) or not d['inputs']:", "    if not isinstance(d, dict):"),
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
