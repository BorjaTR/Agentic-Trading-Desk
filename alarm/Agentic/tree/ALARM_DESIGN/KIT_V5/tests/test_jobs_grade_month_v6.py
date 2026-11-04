#!/usr/bin/env python3
"""test_jobs_grade_month_v6.py (SCOUT 30 Oct 2026, K4; TEST, NOT REVIEWED): tests of JOB_GRADE_V6 and JOB_MONTH_V6, the V5 jobs with their
paths changed (CLEAN_RELEASE_V1) and the quiet window removed (the owner 30 Oct 2026 23:32 Berlin). queue_job_v5.py does not queue GRADE or
MONTH yet (its TEMPLATE_SHA has COUNT and CLEAN only): this test loads a copy of it in a sandbox and puts the two templates' sha16s into
that copy's TEMPLATE_SHA, nothing else. The sandbox: an Alarm package laid out like the install (this package's settings reader and
example, the queue, the two templates, the register writer; stubs for every file a job pins and runs), and outside it the data its
settings file names. A filled job runs with bash as it is, except the scratch disk's free space (df), the pins of the stubs (their sha16
for the real one) and the clock (a planted `date` saying 23:30Z, inside the old quiet window). Then planted bugs in the templates: each
must make a test fail. Seconds; temp folders only, removed after.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_jobs_grade_month_v6.py"""
import contextlib, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT5 = os.path.dirname(HERE)
PKG = os.path.normpath(os.path.join(KIT5, '..', '..', '..', '..'))
KIT = ('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5'); CT = ('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools')
REGS = os.path.join(KIT5, 'runs', 'TEMPLATE_V3', 'registers')
RUNTAG, IDEA = 'AD1_20261029', 'GMX'
STUB_CHAIN = r'''#!/bin/bash
# stub chain: what it was given, and the files the job reads after it
V=$1; DEF=$2; W=$3; mkdir -p $W
printf '{"AL": "%s", "PY": "%s", "LAB_DAYS": "%s", "LEAN": "%s", "PARTS": "%s", "cwd": "%s", "def": "%s", "w": "%s"}\n' "${AL:-}" "${PY:-}" "${LAB_DAYS:-}" "${LEAN:-}" "${PARTS:-}" "$(pwd -P)" "$DEF" "$W" > $W/CHAIN_SAW_$V.json
printf 'coin\tt\tside\nBTC\t1757900000\t1\n' > $W/${V}_FIRES_V1_LIST.tsv
for x in CARD_$V.txt INPUTS_$V.txt MENU_${V}_om.txt; do echo stub > $W/$x; done; printf 'key\tvalue\n' > $W/SUM_$V.tsv
printf 'step\trc\tseconds\tout\tutc\ndone\t0\t0\t%s\tnow\n' "$W" > $W/STATUS_$V.tsv
'''
STUB_PY = r'''import sys, os, json
me = os.path.basename(__file__); a = sys.argv[1:]
open(os.path.join(os.environ.get('K4_SAW', '/dev/null')), 'a').write(json.dumps({'tool': me, 'python': sys.executable, 'argv': a}) + '\n') if os.environ.get('K4_SAW') else None
if me.startswith('perfire'):
    open(os.path.join(a[0], 'PERFIRE_%s.tsv' % a[1]), 'w').write('kind\n')
elif me.startswith('test_perfire'):
    print('PERFIRE TEST %s: PASS 1 FAIL 0' % a[1])
elif me.startswith('lead_null'):
    out = a[a.index('--out') + 1]; os.makedirs(os.path.join(out, 'REAL_SEALED'))
    open(os.path.join(out, 'SUMMARY.tsv'), 'w').write('V\n'); open(os.path.join(out, 'REAL_SEALED', 'REAL_RULES_V1.tsv'), 'w').write('key\tvalue\nR1\tno\n')
elif me.startswith('month_read'):
    print('VERDICT HELD')
elif me.startswith('conditions'):
    print('descriptive')
'''


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def w(p, s, mode=0o644):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s); os.chmod(p, mode)


def pins_of(tpl_text):
    """{path relative to the package: sha16} of every `ck $X/... sha16` line naming a file in the package"""
    var = {'CH': ('03_Grading', 'tree', 'tools', 'alarm_process'), 'MP': ('03_Grading', 'tree', 'tools', 'month_parts'),
           'AP': ('01_Detection', 'tree', 'team', 'RESEARCH', 'tools', 'alarm_process'), 'T': CT}
    out = {}
    for v, rel, h in re.findall(r'ck \$(CH|MP|AP|T)/(\S+) ([0-9a-f]{16})', tpl_text):
        out[os.path.join(*var[v], rel)] = h
    return out


class Sandbox:
    def __init__(self, tmp, templates):
        self.root = tmp; self.P = os.path.join(tmp, 'volat_release', 'Alarm', 'alarm', 'R1'); D = os.path.join(tmp, 'data')
        cp = lambda src, *dst: (os.makedirs(os.path.dirname(os.path.join(self.P, *dst)), exist_ok=True), shutil.copyfile(src, os.path.join(self.P, *dst)))
        cp(os.path.join(PKG, '_tools', 'settings_v1.py'), '_tools', 'settings_v1.py')
        cp(os.path.join(PKG, 'settings', 'SETTINGS_EXAMPLE.env'), 'settings', 'SETTINGS_EXAMPLE.env')
        cp(os.path.join(KIT5, 'tools', 'queue_job_v5.py'), *KIT, 'tools', 'queue_job_v5.py')
        cp(os.path.join(PKG, *CT, 'reg_append_v1.py'), *CT, 'reg_append_v1.py')
        self.shamap = {}
        for kind, text in templates.items():
            w(os.path.join(self.P, *KIT, 'jobs', 'JOB_%s_V6.job.sh.txt' % kind), text)
            for rel, real in pins_of(text).items():
                p = os.path.join(self.P, rel)
                if not os.path.exists(p):
                    w(p, STUB_CHAIN if rel.endswith('.sh') else STUB_PY if rel.endswith('.py') else 'stub\n', 0o755)
                self.shamap[real] = sha16(p)
        self.v = v = {'PYTHON': os.path.join(D, 'venv', 'bin', 'python3'), 'LAB_DAYS': os.path.join(D, 'lab_days'), 'SCRATCH': os.path.join(D, 'scratch'),
                      'RESEARCH_ROOT': os.path.join(D, 'research'), 'RUNNER_QUEUES': os.path.join(D, 'runner'), 'RUNNER_ALLOC': os.path.join(D, 'alloc', 'job_alloc.py')}
        for k in ('LAB_DAYS', 'SCRATCH'):
            os.makedirs(v[k])
        for i in range(1, 22):
            for s in ('IN', 'RUN'):
                os.makedirs(os.path.join(v['RUNNER_QUEUES'], 'Q_V%d' % i, s))
        w(v['RUNNER_ALLOC'], 'import os\np = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n")\nn = int(open(p).read()) + 1 if os.path.exists(p) else 20269001\nopen(p, "w").write(str(n)); print(n)\n')
        os.makedirs(os.path.dirname(v['PYTHON'])); os.symlink(sys.executable, v['PYTHON'])
        sp = importlib.util.spec_from_file_location('settings_v1_k4', os.path.join(self.P, '_tools', 'settings_v1.py')); S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
        self.settings = os.path.join(tmp, 'SETTINGS_SIM.env'); w(self.settings, ''.join('%s=%s\n' % (k, v.get(k, '')) for k in S.keys()))
        self.run = os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', RUNTAG)
        for f in sorted(os.listdir(REGS)):
            if f.endswith('.tsv'):
                w(os.path.join(self.run, 'registers', f), open(os.path.join(REGS, f)).readline())
        w(os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUNTAG, IDEA)), 'claimed\n')
        self.Q = self.load_queue({k: sha16(os.path.join(self.P, *KIT, 'jobs', 'JOB_%s_V6.job.sh.txt' % k)) for k in templates})

    def load_queue(self, extra):
        sp = importlib.util.spec_from_file_location('queue_job_v5_k4', os.path.join(self.P, *KIT, 'tools', 'queue_job_v5.py'))
        Q = importlib.util.module_from_spec(sp); sp.loader.exec_module(Q)
        Q.TEMPLATE_SHA.update(extra)                       # the only change to the queue: the two templates' sha16s
        for k in extra:                                    # and their names: the sandbox holds each under its V6 name (queue_job_v5
            if hasattr(Q, 'TEMPLATE_NAME'):                # names each KIND's template in TEMPLATE_NAME since 31 Oct: GRADE V7)
                Q.TEMPLATE_NAME[k] = 'JOB_%s_V6.job.sh.txt' % k
        Q.CFG.update({'free_mb': lambda: 200000})
        return Q

    def reg(self, name, row):
        r = subprocess.run([sys.executable, '-B', os.path.join(self.P, *CT, 'reg_append_v1.py'), self.run, name, '-'], input=json.dumps(row), capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr

    def variant(self, v='V1'):
        d = 'ideas/%s/defs/%s.json' % (IDEA, v); pr = 'ideas/%s/CARD_%s.md' % (IDEA, IDEA)
        w(os.path.join(self.run, d), json.dumps({'id': v, 'window': {'first': '20250901', 'last': '20260531'}})); w(os.path.join(self.run, pr), 'prereg\n')
        self.reg('VARIANTS', {'idea': IDEA, 'V': v, 'lean': 'FADE', 'def_rel': d, 'def_sha16': sha16(os.path.join(self.run, d)),
                              'prereg_rel': pr, 'prereg_sha16': sha16(os.path.join(self.run, pr)), 'reason': 'test'})

    def month_ready(self, gj, v='V1'):
        w(os.path.join(self.run, 'receipts', gj, 'STAGES.tsv'), 'stage\trc\nend\t0\n')
        self.reg('DECISIONS', {'idea': IDEA, 'V': v, 'state': 'PASS', 'grade_job': gj})
        fc = 'ideas/%s/FORECAST_%s.md' % (IDEA, v); w(os.path.join(self.run, fc), 'forecast\n')
        for m in ('2601', '2602', '2603', '2604'):
            self.reg('FORECASTS', {'idea': IDEA, 'V': v, 'scope': m, 'gap15_lo': '1', 'gap15_hi': '9', 'gap1h_lo': '1', 'gap1h_hi': '9',
                                   'file_rel': fc, 'file_sha16': sha16(os.path.join(self.run, fc))})

    def queue(self, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.Q.main(['--settings', self.settings] + list(a))
        return buf.getvalue()

    def run_job(self, twin):
        s = open(twin).read(); df = 'df -m %s |' % self.v['SCRATCH']
        assert s.count(df) == 1, 'the job reads the free space of SCRATCH, once'
        s = s.replace(df, "printf 'Filesystem\\nx x x 200000\\n' |")
        for real, stub in self.shamap.items():
            s = s.replace(' ' + real, ' ' + stub)
        p = os.path.join(self.root, 'sim', os.path.basename(twin)); w(p, s)
        b = os.path.join(self.root, 'sim', 'bin'); w(os.path.join(b, 'date'), '#!/bin/bash\nfor a in "$@"; do [ "$a" = "+%%H%%M" ] && { echo 2330; exit 0; }; done\nexec %s "$@"\n' % shutil.which('date'), 0o755)
        saw = os.path.join(self.root, 'saw.jsonl')
        r = subprocess.run(['bash', p], capture_output=True, text=True, cwd=self.root, stdin=subprocess.DEVNULL,
                           env=dict(os.environ, PATH=b + os.pathsep + os.environ.get('PATH', ''), K4_SAW=saw))
        return r, [json.loads(l) for l in open(saw)] if os.path.exists(saw) else []


ABS = re.compile(r'(?<![\w.$@)\]/-])/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*[A-Za-z0-9_-]')


def check_body(sb, body, kind):
    """a filled job: no placeholder left, no quiet window, code only in the package, data only under the settings keys"""
    f = []
    if '@@' in body: f.append('%s placeholder left' % kind)
    if re.search(r'2320|QUIET|quiet window near', body, re.I) and 'quiet window was removed by the owner 30 Oct 2026 23:32 Berlin' not in body: f.append('%s quiet window' % kind)
    if 'quiet window was removed by the owner 30 Oct 2026 23:32 Berlin' not in body: f.append('%s header lacks the removal note' % kind)
    if re.search(r'\bst quiet\b|\$h -ge 2320', body): f.append('%s still checks the quiet window' % kind)
    roots = [sb.P, sb.v['RESEARCH_ROOT'], sb.v['SCRATCH'], sb.v['LAB_DAYS']]
    stray = [p for p in ABS.findall(body) if p not in ('/dev/null',) and p != sb.v['PYTHON'] and not any(p == r or p.startswith(r + os.sep) for r in roots)]
    if stray: f.append('%s paths outside the package and the keys: %s' % (kind, stray[:5]))
    for path in re.findall(r'^ck (\S+) [0-9a-f]{16}', body, re.M):
        if not path.startswith('$') and not path.startswith(sb.P + os.sep) and not path.startswith(sb.run + os.sep):
            f.append('%s pin outside the package %s' % (kind, path))
    return f


def all_tests(templates):
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        sb = Sandbox(os.path.realpath(tmp), templates); sb.variant()
        out = sb.queue(RUNTAG, 'GRADE', IDEA, 'V1', '--dry')                                        # 1 GRADE filled, nothing queued
        fails += check_body(sb, out, 'GRADE')
        out = sb.queue(RUNTAG, 'GRADE', IDEA, 'V1')                                                 # 2 GRADE queued and run at 23:30Z
        twin = os.path.join(sb.run, re.search(r' twin (\S+) ', out).group(1)); j = re.search(r'(\d+)_judge_', twin).group(1)
        r, saw = sb.run_job(twin)
        rec = os.path.join(sb.run, 'receipts', '%s_GRADE_%s' % (j, IDEA)); st = open(os.path.join(rec, 'STAGES.tsv')).read() if os.path.isdir(rec) else ''
        W = os.path.join(sb.v['SCRATCH'], 'work_' + RUNTAG, '%s_GRADE_%s' % (j, IDEA))
        for s in ('grade_V1\t0', 'perfire_V1\t0', 'perfire_test_V1\t0', 'handoff\t0', 'end\t0'):
            if s not in st: fails.append('GRADE stage %s missing: rc %d %s %s' % (s, r.returncode, st[-300:], r.stderr[-200:]))
        if 'quiet' in st: fails.append('GRADE stopped for the quiet window')
        cs = json.load(open(os.path.join(W, 'CHAIN_SAW_V1.json'))) if os.path.exists(os.path.join(W, 'CHAIN_SAW_V1.json')) else {}
        if cs.get('AL') != sb.P or cs.get('PY') != sb.v['PYTHON'] or cs.get('LAB_DAYS') != sb.v['LAB_DAYS'] or cs.get('cwd') != sb.P or cs.get('w') != W:
            fails.append('GRADE chain saw %s' % cs)
        if not saw or any(x['python'] != sb.v['PYTHON'] for x in saw): fails.append('GRADE tools ran on %s' % sorted({x['python'] for x in saw}))
        fr = open(os.path.join(rec, 'FIRES.tsv')).read().split('\t') if os.path.exists(os.path.join(rec, 'FIRES.tsv')) else ['']
        if not fr[-1].strip().startswith(W + os.sep): fails.append('GRADE fire list %s' % fr)
        mf = open(os.path.join(rec, 'HANDOFF', 'HANDOFF_MANIFEST.tsv')).read() if os.path.exists(os.path.join(rec, 'HANDOFF', 'HANDOFF_MANIFEST.tsv')) else ''
        if '\t%s\t' % W not in mf: fails.append('GRADE hand-off manifest %s' % mf)
        gj = '%s_GRADE_%s' % (j, IDEA); sb.month_ready(gj)
        out = sb.queue(RUNTAG, 'MONTH', IDEA, 'V1', '--from-job', gj, '--dry')                      # 3 MONTH filled
        fails += check_body(sb, out, 'MONTH')
        for d in os.listdir(sb.v['RUNNER_QUEUES']):                                                  # the fake runner takes the GRADE job
            for f in os.listdir(os.path.join(sb.v['RUNNER_QUEUES'], d, 'IN')):
                os.rename(os.path.join(sb.v['RUNNER_QUEUES'], d, 'IN', f), os.path.join(sb.root, f + '.done'))
        out = sb.queue(RUNTAG, 'MONTH', IDEA, 'V1', '--from-job', gj)                               # 4 MONTH queued and run at 23:30Z
        twin = os.path.join(sb.run, re.search(r' twin (\S+) ', out).group(1)); j = re.search(r'(\d+)_judge_', twin).group(1)
        r, saw = sb.run_job(twin)
        rec = os.path.join(sb.run, 'receipts', '%s_MONTH_%s' % (j, IDEA)); st = open(os.path.join(rec, 'STAGES.tsv')).read() if os.path.isdir(rec) else ''
        W = os.path.join(sb.v['SCRATCH'], 'work_' + RUNTAG, '%s_MONTH_%s' % (j, IDEA))
        for s in ('grade_V1\t0', 'perfire_V1\t0', 'month_V1_2601\t0', 'month_V1_2604\t0', 'conditions_V1_15m\t0', 'end\t0'):
            if s not in st: fails.append('MONTH stage %s missing: rc %d %s %s' % (s, r.returncode, st[-300:], r.stderr[-200:]))
        if 'quiet' in st: fails.append('MONTH stopped for the quiet window')
        cs = json.load(open(os.path.join(W, 'CHAIN_SAW_V1.json'))) if os.path.exists(os.path.join(W, 'CHAIN_SAW_V1.json')) else {}
        if cs.get('AL') != sb.P or cs.get('PY') != sb.v['PYTHON'] or cs.get('LAB_DAYS') != sb.v['LAB_DAYS'] or cs.get('cwd') != sb.P or cs.get('PARTS') != '26':
            fails.append('MONTH chain saw %s' % cs)
        if not saw or any(x['python'] != sb.v['PYTHON'] for x in saw): fails.append('MONTH tools ran on %s' % sorted({x['python'] for x in saw}))
    return fails


QUIET = 'h=$((10#$(date -u +%H%M))); if [ $h -ge 2320 ] || [ $h -lt 15 ]; then st quiet 0 0 "QUIET WINDOW NEAR: not started"; st end 0 0 "not started"; exit 0; fi\n'
MUTANTS = [   # (template, the text, the bug planted)
    ('GRADE', 'f=$(fmb); st start 0 0', QUIET + 'f=$(fmb); st start 0 0'), ('MONTH', 'f=$(fmb); st start 0 0', QUIET + 'f=$(fmb); st start 0 0'),
    ('GRADE', '\ncd $AL\n', '\ncd /\n'), ('MONTH', '\ncd $AL\n', '\ncd /\n'),
    ('GRADE', 'AL=$AL PY=$PY LAB_DAYS=@@LAB_DAYS@@ LEAN', 'AL=$AL PY=$PY LEAN'), ('MONTH', 'AL=$AL PY=$PY LAB_DAYS=@@LAB_DAYS@@ PARTS', 'AL=$AL PY=$PY PARTS'),
    ('GRADE', 'AL=$AL PY=$PY LAB_DAYS', 'PY=$PY LAB_DAYS'), ('MONTH', 'AL=$AL PY=$PY LAB_DAYS', 'AL=$AL LAB_DAYS'),
    ('GRADE', 'W=@@SCRATCH@@/work_@@RUNTAG@@/$J', 'W=@@SCRATCH@@/$J'), ('MONTH', 'W=@@SCRATCH@@/work_@@RUNTAG@@/$J', 'W=@@SCRATCH@@/$J'),
    ('GRADE', 'RD=@@RESEARCH_ROOT@@/ALARM_DESIGN', 'RD=@@SCRATCH@@/ALARM_DESIGN'), ('MONTH', 'RD=@@RESEARCH_ROOT@@/ALARM_DESIGN', 'RD=@@SCRATCH@@/ALARM_DESIGN'),
    ('GRADE', 'fmb(){ df -m @@SCRATCH@@', 'fmb(){ df -m @@RESEARCH_ROOT@@'), ('MONTH', 'fmb(){ df -m @@SCRATCH@@', 'fmb(){ df -m @@LAB_DAYS@@'),
    ('GRADE', 'PY=@@PYTHON@@', 'PY=python3'), ('MONTH', 'PY=@@PYTHON@@', 'PY=python3'),
    ('GRADE', 'T=$AL/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools', 'T=$AL/Agentic/tree/ALARM_DESIGN/runs/tools'),
    ('MONTH', 'MP=$AL/03_Grading/tree/tools/month_parts', 'MP=$AL/01_Detection/tree/tools/month_parts'),
    ('GRADE', 'CH=$AL/03_Grading/tree/tools/alarm_process', 'CH=$AL/01_Detection/tree/team/RESEARCH/tools/alarm_process'),
    ('GRADE', 'F=$AL/01_Detection/tree', 'F=$AL/03_Grading/tree'), ('MONTH', 'F=$AL/01_Detection/tree', 'F=$AL/03_Grading/tree'),
    ('GRADE', ' The quiet window was removed by the owner 30 Oct 2026 23:32 Berlin', ' Stops before the quiet window'),
]


def main():
    if not (os.path.isfile(os.path.join(PKG, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(PKG, 'settings'))):
        raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ at %s' % PKG)
    tpl = {k: open(os.path.join(KIT5, 'jobs', 'JOB_%s_V6.job.sh.txt' % k)).read() for k in ('GRADE', 'MONTH')}
    f = all_tests(tpl)
    print('TESTS', 'PASS' if not f else 'FAIL %s' % f)
    killed = 0
    for k, a, b in MUTANTS:
        assert tpl[k].count(a) == 1, ('mutant target not found once', k, a)
        t2 = dict(tpl); t2[k] = tpl[k].replace(a, b, 1)
        try:
            caught = bool(all_tests(t2))
        except Exception as e:                                                       # a refused queue or a missing receipt also catches it
            caught = True
        killed += caught
        print('MUTANT %-5s %-66s %s' % (k, b.strip().split('\n')[-1][:66], 'KILLED' if caught else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(MUTANTS)))
    return 1 if f or killed != len(MUTANTS) else 0


if __name__ == '__main__':
    sys.exit(main())
