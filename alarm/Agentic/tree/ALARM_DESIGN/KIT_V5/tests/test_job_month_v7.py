#!/usr/bin/env python3
"""test_job_month_v7.py (SCOUT 31 Oct 2026, K12; TEST, NOT REVIEWED): tests of JOB_MONTH_V7, JOB_MONTH_V6 with only its chain changed: it
pins and runs alarm_grade_chain_v2_2_2_to20260430.sh (the clean aw1 grader idea_to_grade_aw1_rel1 with its relative pins and the clean
aw1 detector) and gives the chain the feed gate FEED_GATE (filled by the queue from the settings; empty: no gate). Built on
test_jobs_grade_month_v6.py (K4), whose sandbox it imports from this folder: a copy of queue_job_v5.py fills the template (the queue names
its templates JOB_<KIND>_V6, so the sandbox puts V7's text under that name and V7's sha16 into the copy's TEMPLATE_SHA; nothing else
changes); a filled job runs with bash with a stub chain that records what it was given. Checks: the template pins the package's own chain
v2_2_2 by its sha16; a filled job names no path outside the package and the settings keys (the gate file included); the chain sees AL, PY,
LAB_DAYS, PARTS=26 and FEED_GATE (set and empty when the settings leave it empty; the gate file when they name one), runs in the package,
and every month read and condition stage runs. Then planted bugs in the template: each must make a test fail. Seconds; temp folders only.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_job_month_v7.py"""
import hashlib, importlib.util, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT5 = os.path.dirname(HERE)
sp = importlib.util.spec_from_file_location('test_jobs_grade_month_v6_k4', os.path.join(HERE, 'test_jobs_grade_month_v6.py'))
K4 = importlib.util.module_from_spec(sp); sp.loader.exec_module(K4)
CHAIN_REL = os.path.join('03_Grading', 'tree', 'tools', 'month_parts', 'alarm_grade_chain_v2_2_2_to20260430.sh')
K4.STUB_CHAIN = K4.STUB_CHAIN.replace('"PARTS": "%s", ', '"PARTS": "%s", "FEED_GATE": "%s", ').replace(
    '"${PARTS:-}" ', '"${PARTS:-}" "${FEED_GATE-UNSET}" ')                     # the stub chain also records FEED_GATE (UNSET when not given)
assert '"FEED_GATE": "%s"' in K4.STUB_CHAIN and '"${FEED_GATE-UNSET}"' in K4.STUB_CHAIN


def check_body(sb, body, gate):
    """K4's check of a filled job (no placeholder, no quiet window, paths only in the package and the settings keys), the gate file
    allowed as the settings key FEED_GATE, and the chain line giving FEED_GATE"""
    roots = [sb.P, sb.v['RESEARCH_ROOT'], sb.v['SCRATCH'], sb.v['LAB_DAYS']] + ([gate] if gate else [])
    f = []
    if '@@' in body: f.append('placeholder left')
    if 'quiet window was removed by the owner 30 Oct 2026 23:32 Berlin' not in body: f.append('header lacks the removal note')
    if re.search(r'\bst quiet\b|\$h -ge 2320', body): f.append('still checks the quiet window')
    stray = [p for p in K4.ABS.findall(body) if p not in ('/dev/null',) and p != sb.v['PYTHON'] and not any(p == r or p.startswith(r + os.sep) for r in roots)]
    if stray: f.append('paths outside the package and the keys: %s' % stray[:5])
    if not re.search(r'FEED_GATE=%s PARTS=26 LEAN=\$L bash \$MP/alarm_grade_chain_v2_2_2_to20260430\.sh ' % re.escape(gate), body):
        f.append('the chain line does not give FEED_GATE=%s' % (gate or '(empty)'))
    return f


def one_month(sb, v, gj, gate):
    """queue a MONTH of variant v from grade job gj (dry, then real), run it; -> failures"""
    fails = []
    if gate:
        os.makedirs(os.path.dirname(gate), exist_ok=True); open(gate, 'w').write('RUN\n')
    s = open(sb.settings).read(); s = re.sub(r'^FEED_GATE=.*$', 'FEED_GATE=%s' % gate, s, flags=re.M); open(sb.settings, 'w').write(s)
    sb.variant(v); sb.month_ready(gj, v)
    out = sb.queue(K4.RUNTAG, 'MONTH', K4.IDEA, v, '--from-job', gj, '--dry')
    fails += ['%s dry: %s' % (v, x) for x in check_body(sb, out, gate)]
    out = sb.queue(K4.RUNTAG, 'MONTH', K4.IDEA, v, '--from-job', gj)
    twin = os.path.join(sb.run, re.search(r' twin (\S+) ', out).group(1)); j = re.search(r'(\d+)_judge_', twin).group(1)
    fails += ['%s twin: %s' % (v, x) for x in check_body(sb, open(twin).read(), gate)]
    r, saw = sb.run_job(twin)
    rec = os.path.join(sb.run, 'receipts', '%s_MONTH_%s' % (j, K4.IDEA)); st = open(os.path.join(rec, 'STAGES.tsv')).read() if os.path.isdir(rec) else ''
    W = os.path.join(sb.v['SCRATCH'], 'work_' + K4.RUNTAG, '%s_MONTH_%s' % (j, K4.IDEA))
    for x in ['grade_%s\t0' % v, 'perfire_%s\t0' % v] + ['month_%s_%s\t0' % (v, m) for m in ('2601', '2602', '2603', '2604')] + \
             ['conditions_%s_15m\t0' % v, 'conditions_%s_1h\t0' % v, 'end\t0']:
        if x not in st: fails.append('%s stage %s missing: rc %d %s %s' % (v, x, r.returncode, st[-300:], r.stderr[-200:]))
    if 'chain v2_2_2 Sep-Apr in 26 coin parts' not in st: fails.append('%s the grade stage does not name the chain v2_2_2' % v)
    cs = json.load(open(os.path.join(W, 'CHAIN_SAW_%s.json' % v))) if os.path.exists(os.path.join(W, 'CHAIN_SAW_%s.json' % v)) else {}
    if (cs.get('AL') != sb.P or cs.get('PY') != sb.v['PYTHON'] or cs.get('LAB_DAYS') != sb.v['LAB_DAYS'] or cs.get('cwd') != sb.P
            or cs.get('PARTS') != '26' or cs.get('w') != W or cs.get('FEED_GATE') != gate):
        fails.append('%s chain saw %s' % (v, cs))
    if not saw or any(x['python'] != sb.v['PYTHON'] for x in saw): fails.append('%s tools ran on %s' % (v, sorted({x['python'] for x in saw})))
    for d in os.listdir(sb.v['RUNNER_QUEUES']):                                       # the fake runner takes the job
        for f in os.listdir(os.path.join(sb.v['RUNNER_QUEUES'], d, 'IN')):
            os.rename(os.path.join(sb.v['RUNNER_QUEUES'], d, 'IN', f), os.path.join(sb.root, f + '.done'))
    return fails


def all_tests(text):
    fails = []
    pins = K4.pins_of(text); real = os.path.join(K4.PKG, CHAIN_REL)
    want = hashlib.sha256(open(real, 'rb').read()).hexdigest()[:16] if os.path.isfile(real) else 'NO CHAIN IN THE PACKAGE'
    if pins.get(CHAIN_REL) != want or any('alarm_grade_chain' in k and k != CHAIN_REL for k in pins):
        fails.append('the template pins %s, the package chain v2_2_2 is %s' % ({k: v for k, v in pins.items() if 'chain' in k}, want))
    with tempfile.TemporaryDirectory() as tmp:
        sb = K4.Sandbox(os.path.realpath(tmp), {'MONTH': text})
        fails += one_month(sb, 'V1', '20269001_GRADE_%s' % K4.IDEA, '')                                     # no gate
        fails += one_month(sb, 'V2', '20269002_GRADE_%s' % K4.IDEA, os.path.join(sb.root, 'data', 'feed', 'BACKFILL_GATE.txt'))   # a gate
    return fails


MUTANTS = [   # (the text, the bug planted)
    ('FEED_GATE=@@FEED_GATE@@ ', ''), ('FEED_GATE=@@FEED_GATE@@ ', 'FEED_GATE= '), ('FEED_GATE=@@FEED_GATE@@ ', 'FEED_GATE=@@LAB_DAYS@@ '),
    ('ck $MP/alarm_grade_chain_v2_2_2_to20260430.sh d2bc556e5adaa1a4', 'ck $MP/alarm_grade_chain_v2_2_1_to20260430.sh 093be8f399d1b0d4'),
    ('alarm_grade_chain_v2_2_2_to20260430.sh d2bc556e5adaa1a4', 'alarm_grade_chain_v2_2_2_to20260430.sh 0000000000000000'),
    ('bash $MP/alarm_grade_chain_v2_2_2_to20260430.sh $V', 'bash $MP/alarm_grade_chain_v2_2_1_to20260430.sh $V'),
    ('"chain v2_2_2 Sep-Apr in 26 coin parts, lean $L"', '"chain v2_2_1 Sep-Apr in 26 coin parts, lean $L"'),
    ('PARTS=26 LEAN=$L', 'PARTS=8 LEAN=$L'), ('\ncd $AL\n', '\ncd /\n'), ('AL=$AL PY=$PY LAB_DAYS=@@LAB_DAYS@@ FEED_GATE', 'AL=$AL PY=$PY FEED_GATE'),
    ('AL=$AL PY=$PY LAB_DAYS', 'AL=$AL LAB_DAYS'), ('W=@@SCRATCH@@/work_@@RUNTAG@@/$J', 'W=@@SCRATCH@@/$J'),
    ('RD=@@RESEARCH_ROOT@@/ALARM_DESIGN', 'RD=@@SCRATCH@@/ALARM_DESIGN'), ('fmb(){ df -m @@SCRATCH@@', 'fmb(){ df -m @@LAB_DAYS@@'),
    ('PY=@@PYTHON@@', 'PY=python3'), ('MP=$AL/03_Grading/tree/tools/month_parts', 'MP=$AL/01_Detection/tree/tools/month_parts'),
    ('F=$AL/01_Detection/tree', 'F=$AL/03_Grading/tree'),
]


def main():
    if not (os.path.isfile(os.path.join(K4.PKG, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(K4.PKG, 'settings'))):
        raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ at %s' % K4.PKG)
    text = open(os.path.join(KIT5, 'jobs', 'JOB_MONTH_V7.job.sh.txt')).read()
    f = all_tests(text)
    print('TESTS', 'PASS' if not f else 'FAIL %s' % f)
    killed = 0
    for a, b in MUTANTS:
        assert text.count(a) == 1, ('planted bug target not found once', a)
        try:
            caught = bool(all_tests(text.replace(a, b, 1)))
        except Exception:                                                             # a refused queue or a missing receipt also catches it
            caught = True
        killed += caught
        print('PLANTED BUG %-66s %s' % ((b.strip().split('\n')[-1] or '(removed)')[:66], 'KILLED' if caught else 'SURVIVED'))
    print('PLANTED BUGS %d of %d killed' % (killed, len(MUTANTS)))
    return 1 if f or killed != len(MUTANTS) else 0


if __name__ == '__main__':
    sys.exit(main())
