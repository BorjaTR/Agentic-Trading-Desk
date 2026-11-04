#!/usr/bin/env python3
"""test_hc_defs_v4.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): test_hc_defs_v3.py
for hc_defs_v4: every v3 test on v4 (the stand-in engine now keeps a memo of computed inputs and the definition names three inputs, x
computed, y computed and all empty, z never computed), plus the 0-fire HINT lines (HC_FAKE_ZERO=1: the stand-in finds no fire) and
their planted bugs. v3's text follows.
test_hc_defs_v3.py (SCOUT, 31 Oct 2026): test_hc_defs_v2.py 84ac79ce7aee66f5 for hc_defs_v3: the FIRE lines with seconds, plus --out (every
fire written as coin, t, side; an existing file refused) and their planted bugs. v2's text follows.
test_hc_defs_v2.py: planted tests and planted bugs for hc_defs_v2_to20251231.py. Temp folders only, seconds; no lab data is read.

Owner: SCOUT (the alarm kit). New by SCOUT for the clean release (K7, 30 Oct 2026). Edition 1 (hc_defs_v1_to20251231.py
edc444f943ea155c) had no tests. Each planted Alarm folder holds the real settings reader, a stand-in detect.py (a fake engine with known
coins, times, values and fires, that logs how it was called) and the gate tables; the hand check runs on it as on the real one. The
expected lines are written here from edition 1's print statements, so the output format is checked without running edition 1.
It runs no old edition. Run it from inside an Alarm folder:
  python3 -B test_hc_defs_v2.py      -> TESTS PASS, then MUTANTS n of n killed; exit 0 only when both hold"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = 'hc_defs_v4_to20251231.py'
TOOL_DIR = 'team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'
GATE = {'METRICS_V1': ['team/LAB3/METRICS_V1.tsv'],
        'METRIC_TRAPS': ['team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv'],
        'CATALOGS': ['team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv',
                     'team/LAB3/METRICS_HL_ADD_V1.tsv', 'team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv']}
FAKE_DETECT = r'''
import datetime as dt, json, os
import numpy as np
def _log(**k):
    with open(os.environ['HC_FAKE_LOG'], 'a') as f:
        f.write(json.dumps(k) + '\n')
class _A:
    @staticmethod
    def shift(d, n):
        return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=n)).strftime('%Y%m%d')
    @staticmethod
    def keep_days(d):
        return 2
    class LabSource:
        def __init__(self, lab_root, code_dir):
            _log(lab_root=lab_root, code_dir=code_dir)
        def coins(self, day):
            _log(day=day)
            return ['AAA', 'BBB']
    class Ctx:
        def __init__(self, d, src, day, cs, hist):
            b = int(dt.datetime.strptime(day, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())
            self.t = np.array([b + 600, b + 660, b + 720], float); self.read_last = None
            self.v = {'x': np.array([[1.5, np.nan, 2.25], [3.0, 4.0, 5.1234567]])}
            self.memo = {'x': self.v['x'], 'y': np.full((2, 3), np.nan) if day >= '20251001' else np.zeros((2, 3)), 'other': np.zeros((2, 3))}
        def get(self, k):
            return self.v[k]
        def push_hist(self, keep):
            pass
    @staticmethod
    def find_fires(ctx, last_fire):
        if os.environ.get('HC_FAKE_ZERO'):
            return [], None, None, None, np.zeros((2, 3))
        return [(0, 0), (1, 2)], None, None, None, np.array([[1, 1, 1], [-1, -1, -1]])
def engine():
    return _A
def load_definition(path):
    _log(env={k: os.environ.get(k) for k in ('METRICS_V1', 'METRIC_TRAPS', 'CATALOGS')}, definition=path)
    d = json.load(open(path))
    return d, {'id': d['id'], 'sha16': 'feedfacefeedface', 'execution_path': 'BASE', 'briefs': {}}
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


def plant(root, src, skip=()):
    reader, example = alarm_files()
    os.makedirs(os.path.join(root, '_tools')); os.makedirs(os.path.join(root, 'settings'))
    shutil.copy(reader, os.path.join(root, '_tools')); shutil.copy(example, os.path.join(root, 'settings'))
    tree = os.path.join(root, '01_Detection', 'tree')
    write(os.path.join(tree, 'team', 'RESEARCH', 'tools', 'idea_to_grade', 'detect.py'), FAKE_DETECT)
    for rels in GATE.values():
        for r in rels:
            if r not in skip:
                write(os.path.join(tree, *r.split('/')), 'code\n')
    tool = os.path.join(tree, *TOOL_DIR.split('/'), TOOL)
    os.makedirs(os.path.dirname(tool), exist_ok=True); shutil.copy(src, tool)
    return tool, tree


def settings_file(tmp, name, lab):
    """every key of the example; LAB_DAYS = lab, RESEARCH_STORE = another real folder (a wrong key must show), the rest empty"""
    _, example = alarm_files()
    keys = [l.split('=', 1)[0] for l in open(example) if '=' in l and not l.lstrip().startswith('#')]
    other = os.path.join(tmp, 'research_days'); os.makedirs(other, exist_ok=True)
    val = {'LAB_DAYS': lab, 'RESEARCH_STORE': other}
    p = os.path.join(tmp, name)
    write(p, ''.join('%s=%s\n' % (k, val.get(k, '')) for k in keys))
    return p


def run(tool, args, log, env=None):
    e = dict(os.environ); e['HC_FAKE_LOG'] = log; e.update(env or {})
    p = subprocess.run([sys.executable, '-B', tool] + args, capture_output=True, text=True, env=e, cwd=tempfile.gettempdir())
    rows = [json.loads(l) for l in open(log)] if os.path.isfile(log) else []
    return p.returncode, p.stdout, p.stderr, rows


INPUTS = {'x': {'op': 'raw', 'code': 'X1.A'}, 'y': {'op': 'raw', 'code': 'X1.B'}, 'z': {'op': 'abs', 'of': 'x'}}
EXPECT_ZERO = ("PARSE OK PLANTED feedfacefeedface path BASE briefs {}\n"
               "fires 0 per coin {} fires a coin-day 0.00\n"
               "HINT 0 fires: the share of each input that is a number on these days and coins (EMPTY: none; check its first day and coins)\n"
               "HINT input x (X1.A): 83.3 pct numbers\n"
               "HINT input y (X1.B): EMPTY\n"
               "HINT input z (abs): not computed\n")
EXPECT = ("PARSE OK PLANTED feedfacefeedface path BASE briefs {}\n"
          "FIRE AAA 2025-10-01 00:10:00 side 1 {'x': 1.5}\n"
          "FIRE BBB 2025-10-01 00:12:00 side -1 {'x': 5.123457}\n"
          "FIRE AAA 2025-10-02 00:10:00 side 1 {'x': 1.5}\n"
          "fires 4 per coin {'AAA': 2, 'BBB': 2} fires a coin-day 1.00\n")


def tests(src):
    ok = []
    with tempfile.TemporaryDirectory() as tmp:
        lab = os.path.join(tmp, 'lab_days'); os.makedirs(lab)
        tool, tree = plant(os.path.join(tmp, 'A', 'Alarm'), src)
        S = settings_file(tmp, 'S.env', lab)
        dfn = os.path.join(tmp, 'D.json'); write(dfn, json.dumps({'id': 'PLANTED', 'inputs': INPUTS}))
        args = ['--settings', S, dfn, '20251001', '20251002', 'AAA,BBB', '3', 'x']
        log = os.path.join(tmp, 'log1.jsonl')
        rc, out, err, rows = run(tool, args, log, env={'METRICS_V1': os.path.join(tmp, 'elsewhere.tsv')})
        ok.append(('t_runs_and_prints_edition_1_lines', rc == 0 and out == EXPECT))
        src_row = [r for r in rows if 'lab_root' in r]
        ok.append(('t_lab_days_from_settings', len(src_row) == 1 and os.path.realpath(src_row[0]['lab_root']) == os.path.realpath(lab)))
        ok.append(('t_lab3_code_inside', len(src_row) == 1 and src_row[0]['code_dir'] == os.path.join(tree, 'team', 'LAB3', 'code')))
        envrow = [r for r in rows if 'env' in r]
        want = {k: ':'.join(os.path.join(tree, *r.split('/')) for r in v) for k, v in GATE.items()}
        ok.append(('t_gate_tables_inside_the_tree', len(envrow) == 1 and envrow[0]['env'] == want))
        ok.append(('t_definition_as_given', len(envrow) == 1 and envrow[0]['definition'] == dfn))
        ok.append(('t_days_with_warm_up', [r['day'] for r in rows if 'day' in r] == ['20250928', '20250929', '20250930', '20251001', '20251002']))
        for k, v in GATE.items():
            for r in v:
                t2, _ = plant(os.path.join(tmp, 'M_' + r.replace('/', '_'), 'Alarm'), src, skip=(r,))
                rc, out, err, rows = run(t2, args, os.path.join(tmp, 'log_' + r.replace('/', '_')))
                ok.append(('t_missing_%s_refused' % r.split('/')[-1], rc == 2 and 'MISSING TABLE' in err and not rows and not out))
        rc, out, err, rows = run(tool, args[2:], os.path.join(tmp, 'log3'))
        ok.append(('t_settings_required', rc != 0 and 'USAGE' in err and not rows))
        rc, out, err, rows = run(tool, args[2:] + [lab, tree], os.path.join(tmp, 'log4'))
        ok.append(('t_edition_1_roots_refused', rc != 0 and 'USAGE' in err and not rows))
        empty = settings_file(tmp, 'S_EMPTY.env', '')
        rc, out, err, rows = run(tool, ['--settings', empty] + args[2:], os.path.join(tmp, 'log5'))
        ok.append(('t_empty_lab_days_refused', rc == 2 and 'EMPTY LAB_DAYS' in err and not rows))
        rc, out, err, rows = run(tool, args[:3] + ['20250901', '20251002'] + args[5:], os.path.join(tmp, 'log6'))
        ok.append(('t_outside_window_refused', rc != 0 and 'OUTSIDE_WINDOW' in err and not rows))
        fo = os.path.join(tmp, 'F.tsv')
        rc, out, err, rows = run(tool, args[:2] + ['--out', fo] + args[2:], os.path.join(tmp, 'log8'))
        want = 'coin\tt\tside\nAAA\t1759277400\t1\nBBB\t1759277520\t-1\nAAA\t1759363800\t1\nBBB\t1759363920\t-1\n'
        ok.append(('t_out_every_fire', rc == 0 and os.path.isfile(fo) and open(fo).read() == want and ('WROTE %s 4 fires\n' % fo) in out))
        ok.append(('t_out_keeps_lines', rc == 0 and out.replace('WROTE %s 4 fires\n' % fo, '') == EXPECT))
        rc, out, err, rows = run(tool, args[:2] + ['--out', fo] + args[2:], os.path.join(tmp, 'log9'))
        ok.append(('t_out_exists_refused', rc == 2 and 'OUT EXISTS' in err and not rows and not out and open(fo).read() == want))
        rc, out, err, rows = run(tool, args, os.path.join(tmp, 'log10'), env={'HC_FAKE_ZERO': '1'})
        ok.append(('t_zero_fires_hints', rc == 0 and out == EXPECT_ZERO))
        fz = os.path.join(tmp, 'FZ.tsv')
        rc, out, err, rows = run(tool, args[:2] + ['--out', fz] + args[2:], os.path.join(tmp, 'log11'), env={'HC_FAKE_ZERO': '1'})
        ok.append(('t_zero_fires_out_header_only', rc == 0 and os.path.isfile(fz) and open(fz).read() == 'coin\tt\tside\n'
                   and out.replace('WROTE %s 0 fires\n' % fz, '') == EXPECT_ZERO))
        lone = os.path.join(tmp, 'lone'); os.makedirs(lone); shutil.copy(src, os.path.join(lone, TOOL))
        rc, out, err, rows = run(os.path.join(lone, TOOL), args, os.path.join(tmp, 'log7'))
        ok.append(('t_outside_alarm_refused', rc == 2 and 'NOT INSIDE AN ALARM FOLDER' in err and not rows))
    return ok


MUTANTS = [
    ("lab = S.get(settings, 'LAB_DAYS')", "lab = S.get(settings, 'RESEARCH_STORE')"),
    ("code_dir=os.path.join(F, 'team', 'LAB3', 'code')", "code_dir=os.path.join(F, 'team', 'LAB3')"),
    ("'team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv',)", "'team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv',)"),
    ("'team/LAB3/METRICS_HL_ADD_V1.tsv', ", ""),
    ("    if miss:\n        raise Refused", "    if False:\n        raise Refused"),
    ("    os.environ.update(env)\n", "    [os.environ.setdefault(k, v) for k, v in env.items()]\n"),
    ("    if settings is None or len(a) != 6: raise SystemExit(USAGE)", "    if len(a) != 6: raise SystemExit(USAGE)"),
    ("    if not (FIRST <= first <= last <= LAST): raise SystemExit", "    if False: raise SystemExit"),
    ("day = max(A.shift(first, -(keep + 1)), SUPPORT_FIRST)", "day = max(A.shift(first, -keep), SUPPORT_FIRST)"),
    ("return os.path.join(S.alarm_root(start), *DETECTION_TREE)", "return os.path.join(S.alarm_root(os.getcwd()), *DETECTION_TREE)"),
    ("strftime('%Y-%m-%d %H:%M:%S')", "strftime('%Y-%m-%d %H:%M')"),
    ("                    rows.append((cs[i], int(ctx.t[r]), int(side[i, r])))\n", "                    if n <= int(nmax): rows.append((cs[i], int(ctx.t[r]), int(side[i, r])))\n"),
    ("    if out is not None and os.path.exists(out):", "    if False:"),
    ("'%s\\t%d\\t%d\\n' % r", "'%s\\t%d\\t%d\\n' % (r[0], r[1], -r[2])"),
    ("        out, a = a[1], a[2:]\n", "        out, a = None, a[2:]\n"),
    ("    if n == 0:\n        print('\\n'.join(hint_lines(fin, inputs)))", "    if n >= 0:\n        print('\\n'.join(hint_lines(fin, inputs)))"),
    ("    if n == 0:\n        print('\\n'.join(hint_lines(fin, inputs)))", "    if n < 0:\n        print('\\n'.join(hint_lines(fin, inputs)))"),
    ("            if day >= first:\n                note_inputs(fin, inputs, ctx.memo)\n", "            note_inputs(fin, inputs, ctx.memo)\n"),
    ("'EMPTY' if num == 0 else", "'EMPTY' if num < 0 else"),
    ("f[0] += int(np.isfinite(v).sum()); f[1] += int(v.size)", "f[0] += int(np.isfinite(v).sum()); f[1] += int(v.size) // 2"),
    ("    for k in names:", "    for k in list(names)[:1]:"),
    ("inputs[k].get('code', inputs[k].get('op')),\n                                                   'EMPTY'", "inputs[k].get('op'),\n                                                   'EMPTY'"),
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
