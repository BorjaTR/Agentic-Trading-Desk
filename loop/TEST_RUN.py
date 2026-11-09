#!/usr/bin/env python3
"""TEST_RUN.py (LEARNING_LOOP_V1, built as RC5, SCOUT 2026-11-08, C218; C223 rows 5 and 12; C230 row 13b): every TEST.md row, run from a copy of this release as a NEW seat,
with the seat variables of SETTINGS_TEMPLATE.md SET (install report U1). Nothing outside <seat> and <tmp> is written.
  python3 -B TEST_RUN.py --release <copy of this folder> --seat <new empty seat folder> --tmp <temp folder off the internal disk>
       [--watch <folder no test may open, e.g. the alarm seat>]
Prints one line per row: ROW <n> <PASS|FAIL> <seconds> <summary>; and SEAT_REGISTERS_UNCHANGED yes|no; exit 0 when every row passes."""
import argparse, csv, hashlib, os, shutil, subprocess, sys, time
ap = argparse.ArgumentParser(); ap.add_argument('--release', required=True); ap.add_argument('--seat', required=True); ap.add_argument('--tmp', required=True)
ap.add_argument('--watch', default=''); a = ap.parse_args()
R, SEAT, TMP = (os.path.abspath(x) for x in (a.release, a.seat, a.tmp)); G = os.path.join(R, 'generic')
for d in ('registers', 'pack_strategy', 'hook'): os.makedirs(os.path.join(SEAT, d), exist_ok=True)
os.makedirs(TMP, exist_ok=True)
for f in os.listdir(os.path.join(G, 'registers_template')): shutil.copy2(os.path.join(G, 'registers_template', f), os.path.join(SEAT, 'registers', f))
shutil.copytree(os.path.join(R, 'packs', 'strategy_draft'), os.path.join(SEAT, 'pack_strategy'), dirs_exist_ok=True)
shutil.copy2(os.path.join(G, 'RULES_TEMPLATE.md'), os.path.join(SEAT, 'pack_strategy', 'RULES.md'))   # stands for the seat's merged rules page
LOG = os.path.join(SEAT, 'hook', 'watch.log')
if a.watch:   # audit hook: any open, listing or subprocess naming the watched folder is logged
    open(os.path.join(SEAT, 'hook', 'sitecustomize.py'), 'w').write(
        'import sys\nW = %r; L = %r\n' % (os.path.abspath(a.watch), LOG) +
        'def h(ev, args):\n    if ev in ("open", "os.listdir", "os.scandir", "shutil.copyfile", "subprocess.Popen") and args and W in str(args[0]):\n'
        '        with open(L, "a") as fh: fh.write(ev + " " + str(args[0]) + "\\n")\nsys.addaudithook(h)\n')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', LL_SEAT_ROOT=SEAT, LL_REGISTERS=os.path.join(SEAT, 'registers'), LL_SEAT_ROOT_NAME=os.path.basename(SEAT),
           LL_REPORT_TEMPLATE=os.path.join(G, 'REPORT_TEMPLATE_V1.md'), LEAK_SCAN_PATTERN_FILE=os.path.join(R, 'packs', 'alarm', 'HELDOUT_PATTERN.txt'),
           LL_TEST_TMP=TMP, KNOW_V2_TMP=TMP, LL_GENERIC=G, LL_PACK=os.path.join(SEAT, 'pack_strategy'), LL_SKILLS=os.path.join(SEAT, 'skills'))
if a.watch: ENV['PYTHONPATH'] = os.path.join(SEAT, 'hook')
for k in ('KNOW_V2_SERIES', 'ALARM_SERIES_DIR', 'ALARM_SERIES_HEADER', 'ALARM_RUNS_DIR'): ENV.pop(k, None)
def tree_sha(d):
    h = hashlib.sha256()
    for f in sorted(os.listdir(d)): h.update(f.encode()); h.update(open(os.path.join(d, f), 'rb').read())
    return h.hexdigest()[:16]
REG = os.path.join(SEAT, 'registers'); before = tree_sha(REG); fails = 0
PY = [sys.executable, '-B']; K = PY + [os.path.join(G, 'tools/knowledge_v2/build_knowledge_v2.py')]; RG = PY + [os.path.join(G, 'tools/registers/reg.py')]
LS = PY + [os.path.join(G, 'tools/drills/leak_scan_v1.py')]
ALARM = os.path.join(R, 'packs/alarm/alarm.json'); STRAT = os.path.join(SEAT, 'pack_strategy', 'strategy_v0.json')
def row(n, cmd, cwd, want_rc=0, want=(), env=None, note=''):
    global fails
    t0 = time.time(); p = subprocess.run(cmd, cwd=cwd, env=env or ENV, capture_output=True, text=True); dt = time.time() - t0
    out = p.stdout + p.stderr; ok = p.returncode == want_rc and all(w in out for w in want)
    summ = [l for l in out.splitlines() if l.strip() and not l.startswith(('.', '-', '='))][-1:] or ['']
    fails += 0 if ok else 1
    print('ROW %s %s %.2f s rc %d | %s%s' % (n, 'PASS' if ok else 'FAIL', dt, p.returncode, summ[0][:150], (' | ' + note) if note else ''))
    if not ok: print(out[-1500:])
    return out
D = lambda *x: os.path.join(R, *x)
row('1', PY + ['-m', 'unittest', 'test_build_knowledge_v2'], D('generic/tools/knowledge_v2'), want=('Ran 33', 'OK (skipped=2)'))
row('1b', PY + ['-m', 'unittest', 'test_knowledge_v2_c218'], D('generic/tools/knowledge_v2'), want=('Ran 5', 'OK'))
row('2', PY + ['test_reg_audit.py'], D('generic/tools/registers'), want=('Ran 6', 'OK'))
row('3', PY + ['test_reg_report.py'], D('generic/tools/registers'), want=('Ran 4', 'OK'), note='seat LL_REGISTERS set')
row('3b', PY + ['test_reg_baseline.py'], D('generic/tools/registers'), want=('Ran 4', 'OK'))
row('4', PY + ['test_messy_triage_v1.py'], D('generic/tools/registers'), want=('PASS 8 planted lines',))
row('5', PY + ['test_blind_kit_v1.py'], D('generic/tools/drills'), want=('Ran 8', 'OK'))
row('6', PY + ['test_leak_scan_v1.py'], D('generic/tools/drills'), want=('Ran 7', 'OK'))
row('7', PY + ['test_agreement_v1.py'], D('generic/tools/drills'), want=('Ran 6', 'OK'))
row('8', PY + ['agreement_v1.py', '--self-test'], D('generic/tools/drills'), want=('SELF_TEST PASS',))
row('9', PY + ['test_queue_job_v15_scout.py'], D('packs/alarm/playground'), want=('Ran 7', 'OK'))
row('10', PY + ['test_bar_check_v2.py'], D('packs/alarm/tools'), want=('Ran 10', 'OK'))
row('11', PY + ['test_forecast_score.py'], D('packs/alarm/tools'), want=('Ran 4', 'OK'))
row('12', PY + ['test_check_round_v1.py'], D('packs/alarm/tools'), want=('Ran 8', 'OK'))
row('13', PY + ['test_pool_splits_v1.py'], D('packs/alarm/tools'), want=('Ran 2', 'OK'))
row('13b', PY + ['test_speed_report_v1.py'], D('packs/alarm/tools'), want=('Ran 3', 'OK'))
unchanged = tree_sha(REG) == before
row('14', RG + ['check'], SEAT, want=('CHECK PASS drill runs 0 improvements 0',))
row('14b.1', RG + ['ledger-check'], SEAT, want_rc=1, want=('LEDGER_CHECK FLAG',), note='template PARTS.tsv (alarm seat files): flags, as the review found')
# 14b: the seat points PARTS.tsv files cells at its own copies (README step 3a): keep each cell that resolves in this seat, P01 gets its RULES.md
P = os.path.join(REG, 'PARTS.tsv'); rows = list(csv.DictReader(open(P), delimiter='\t')); hdr = list(rows[0].keys()); kept = 0
def resolves(f):
    import re
    g = re.sub(r'\{([A-Z_]+)\}', lambda m: ENV.get('LL_' + m.group(1), m.group(0)), f); g = g if os.path.isabs(g) else os.path.join(SEAT, g)
    return os.path.isfile(g)
for r in rows:
    fs = [f for f in r['files'].split(',') if f and resolves(f)]
    if r['part_id'] == 'P01': fs = ['{PACK}/RULES.md'] + fs
    kept += len(fs); r['files'] = ','.join(fs)
with open(P, 'w', newline='') as fh:
    w = csv.DictWriter(fh, hdr, delimiter='\t', lineterminator='\n'); w.writeheader(); w.writerows(rows)
row('14b.2', RG + ['baseline', 'who=TEST_SEAT'], SEAT, want=('BASELINE rows',), note='PARTS.tsv rewritten to the seat: %d files kept' % kept)
row('14b.3', RG + ['ledger-check'], SEAT, want=('LEDGER_CHECK PASS',))
row('15', K + ['init', '--pack', STRAT, '--dir', os.path.join(SEAT, 'store_new', 'store')], SEAT, note='store folder not made first; strategy pack with TODO bars')
row('15b', K + ['init', '--pack', ALARM, '--dir', os.path.join(SEAT, 'store_alarm')], SEAT)
row('16', K + ['check', '--pack', ALARM, '--dir', os.path.join(SEAT, 'store_alarm')], SEAT, want=('CHECK PASS errors 0',))
row('16b', K + ['check', '--pack', STRAT, '--dir', os.path.join(SEAT, 'store_new', 'store')], SEAT, want_rc=1, want=('REFUSED', 'TODO'), note='TODO bars refused by design')
e2 = dict(ENV); e2.pop('LEAK_SCAN_PATTERN_FILE')
row('17', LS + ['--secrets', D('generic/LOOP.md'), '--targets', D('generic/prompts')], SEAT, want_rc=2, want=('REFUSED NO_PATTERN',), env=e2)
row('18', LS + ['--pattern-file', D('packs/alarm/HELDOUT_PATTERN.txt'), '--secrets', D('generic/LOOP.md'), '--targets', D('generic/prompts')], SEAT, want=('LEAK_SCAN PASS',))
print('SEAT_REGISTERS_UNCHANGED_BY_TESTS_1_TO_13', 'yes' if unchanged else 'no'); fails += 0 if unchanged else 1
if a.watch: print('WATCH_LOG_LINES', sum(1 for _ in open(LOG)) if os.path.exists(LOG) else 0)
pyc = [os.path.join(dp, d) for base in (R, SEAT) for dp, dn, _ in os.walk(base) for d in dn if d == '__pycache__']
print('PYCACHE', len(pyc)); print('TEST_RUN', 'PASS' if not fails else 'FAIL %d' % fails); sys.exit(1 if fails else 0)
