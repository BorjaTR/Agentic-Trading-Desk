#!/usr/bin/env python3
"""test_job_entry_v6.py (SCOUT, K6, 31 Oct 2026; TEST, NOT REVIEWED): tests of JOB_ENTRY_V6 and of the store runner it runs,
run_alarm_store_v11_noladder.sh: the V5 job and the v10_3 runner with only where things are changed (CLEAN_RELEASE_V1; the owner 30 Oct 2026
23:07 Berlin: "All alarm tools should work from the release folder only") and the quiet window removed (23:32 Berlin). New edition by
SCOUT for the clean release. queue_job_v5.py does not queue ENTRY yet (its TEMPLATE_SHA has no ENTRY): this test loads a copy of it in
a sandbox and puts the template's sha16 into that copy's TEMPLATE_SHA, nothing else (as test_jobs_grade_month_v6.py does for GRADE and
MONTH). The sandbox: an Alarm package laid out like the install (this package's settings reader and example, the queue, the template,
the register writer, the REAL store runner and the real bytes of every file the job and the runner pin), and outside it the data its
settings file names. The interpreter of the settings is a stand-in: it records every call (script, arguments, folder) and answers for
the grader, the universe writer and the markout and its units; every other call (python -c) runs on the real interpreter. A filled
job runs with bash as it is, except the scratch disk's free space (df). The runner also runs on its own: its refusals and what it
gives the grader. Then planted bugs in the template and in the runner: each must make a test fail. Seconds; temp folders only.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_job_entry_v6.py"""
import contextlib, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
KIT5 = os.path.dirname(HERE)
PKG = os.path.normpath(os.path.join(KIT5, '..', '..', '..', '..'))
KIT = ('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5'); CT = ('Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools')
P7 = ('07_Price_path', 'tree', 'team'); I2G = P7 + ('RESEARCH', 'tools', 'idea_to_grade'); MO = P7 + ('RESEARCH', 'tools', 'markout')
ROSTER = P7 + ('OUTSIDE', 'COORD', 'development', 'DEV2', 'a02p_chain_v1', 'full_population', 'ROSTER_BUILD.json')
REGS = os.path.join(KIT5, 'runs', 'TEMPLATE_V3', 'registers')
RUNTAG, IDEA, SEAT = 'AD1_20261029', 'ENX', 'AD1'
RUNNER = 'run_alarm_store_v11_noladder.sh'
PINNED = [I2G + ('idea_to_grade_v3_2_s6_rel1.py',), I2G + ('I2G_PINS_V3_2_S6_REL1.json',), MO + ('markout_v1_2.py',), MO + ('test_markout_v1_2.py',),
          MO + ('test_markout_v1_2_base.py',), MO + ('settings', 'SETTINGS_V1.json')]
STUB = r'''import json, os, sys
a = sys.argv[1:]; log = os.environ.get('K6_SAW')
script = next((x for x in a if x.endswith('.py')), '')
if log:
    open(log, 'a').write(json.dumps({'script': script, 'argv': a, 'cwd': os.getcwd()}) + '\n')
name = os.path.basename(script)
def opt(k):
    for i, x in enumerate(a):
        if x == k: return a[i + 1]
        if x.startswith(k + '='): return x[len(k) + 1:]
    return None
if name == 'idea_to_grade_v3_2_s6_rel1.py':
    out = opt('--out'); os.makedirs(out); json.dump({'tool': 'stub grader', 'argv': a}, open(os.path.join(out, 'RUN.json'), 'w'))
    print(json.dumps({'status': 'COMPLETE', 'out': out}))
elif name == 'i2g_universe_v1.py':
    open(a[a.index(script) + 1], 'w').write('# stub universe\n')
elif name == 'test_markout_v1_2.py':
    print('UNITS 1 PASS 0 FAIL')
elif name == 'markout_v1_2.py':
    out = opt('--out'); os.makedirs(out)
    for f in ('GATES.json', 'CURVE.tsv', 'HALVES_W0.tsv', 'HALVES_W60.tsv', 'HALVES_W300.tsv', 'TABLE_W0.tsv', 'RECEIPT.json'):
        open(os.path.join(out, f), 'w').write('{}' if f.endswith('.json') else 'x\n')
    print('DONE gates stub -> ' + out)
else:
    os.execv(sys.executable, [sys.executable] + a)
'''


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def w(p, s, mode=0o644):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s); os.chmod(p, mode)


class Sandbox:
    def __init__(self, tmp, template, runner):
        self.root = tmp; self.P = os.path.join(tmp, 'volat_release', 'Alarm', 'alarm', 'R1'); D = os.path.join(tmp, 'data')
        cp = lambda src, *dst: (os.makedirs(os.path.dirname(os.path.join(self.P, *dst)), exist_ok=True), shutil.copyfile(src, os.path.join(self.P, *dst)))
        cp(os.path.join(PKG, '_tools', 'settings_v1.py'), '_tools', 'settings_v1.py')
        cp(os.path.join(PKG, 'settings', 'SETTINGS_EXAMPLE.env'), 'settings', 'SETTINGS_EXAMPLE.env')
        cp(os.path.join(KIT5, 'tools', 'queue_job_v5.py'), *KIT, 'tools', 'queue_job_v5.py')
        cp(os.path.join(PKG, *CT, 'reg_append_v1.py'), *CT, 'reg_append_v1.py')
        for rel in PINNED:
            cp(os.path.join(PKG, *rel), *rel)                                       # the real bytes: the job and the runner check their sha16
        w(os.path.join(self.P, *ROSTER), json.dumps({'coins': ['BTC', 'ETH']}))
        w(os.path.join(self.P, *I2G, 'i2g_universe_v1.py'), '# the stand-in interpreter answers for it\n')
        self.runner = os.path.join(self.P, *CT, RUNNER); w(self.runner, runner, 0o755)
        self.tpl = os.path.join(self.P, *KIT, 'jobs', 'JOB_ENTRY_V6.job.sh.txt'); w(self.tpl, template)
        real = re.search(r'ck \$CH ([0-9a-f]{16})', template)
        self.shamap = {real.group(1): sha16(self.runner)} if real else {}
        self.v = v = {'PYTHON': os.path.join(D, 'venv', 'bin', 'python3'), 'LAB_DAYS': os.path.join(D, 'lab_days'), 'SCRATCH': os.path.join(D, 'scratch'),
                      'RESEARCH_ROOT': os.path.join(D, 'research'), 'RUNNER_QUEUES': os.path.join(D, 'runner'), 'RUNNER_ALLOC': os.path.join(D, 'alloc', 'job_alloc.py'),
                      'FEED_GATE': os.path.join(D, 'feed', 'BACKFILL_GATE.txt')}
        for k in ('LAB_DAYS', 'SCRATCH'):
            os.makedirs(v[k])
        w(v['FEED_GATE'], 'RUN\n')
        for i in range(1, 22):
            for s in ('IN', 'RUN'):
                os.makedirs(os.path.join(v['RUNNER_QUEUES'], 'Q_V%d' % i, s))
        w(v['RUNNER_ALLOC'], 'import os\np = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n")\nn = int(open(p).read()) + 1 if os.path.exists(p) else 20269001\nopen(p, "w").write(str(n)); print(n)\n')
        self.saw = os.path.join(tmp, 'saw.jsonl')
        w(os.path.join(D, 'stub.py'), STUB); w(v['PYTHON'], '#!/bin/bash\nexec %s -B %s "$@"\n' % (sys.executable, os.path.join(D, 'stub.py')), 0o755)
        sp = importlib.util.spec_from_file_location('settings_v1_k6', os.path.join(self.P, '_tools', 'settings_v1.py')); S = importlib.util.module_from_spec(sp); sp.loader.exec_module(S)
        self.settings = os.path.join(tmp, 'SETTINGS_SIM.env'); w(self.settings, ''.join('%s=%s\n' % (k, v.get(k, '')) for k in S.keys()))
        R = v['RESEARCH_ROOT']; self.run = os.path.join(R, 'ALARM_DESIGN', 'runs', RUNTAG)
        for f in sorted(os.listdir(REGS)):
            if f.endswith('.tsv'):
                w(os.path.join(self.run, 'registers', f), open(os.path.join(REGS, f)).readline())
        w(os.path.join(R, 'ALARM_DESIGN', 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUNTAG, IDEA)), 'claimed\n')
        w(os.path.join(R, 'LIBRARY', 'UNIVERSE_ALARMS_V1.tsv'), '# source ALM_OTHER=/x 0\n'); w(os.path.join(R, 'LIBRARY', 'UNIVERSE_ALARMS_V3.tsv'), '# source ALM_OTHER=/x 0\n')
        w(os.path.join(R, 'LIBRARY', 'alarm_library', 'ALARM_REGISTRY_V1_1.tsv'), 'registry_id\tcard\tversion\tdefinition\tdefinition_sha16\tfamily\n')
        w(os.path.join(self.run, 'ideas', IDEA, 'ALARM_CARD.md'), 'card\n')
        self.Q = self.load_queue({'ENTRY': sha16(self.tpl)})

    def load_queue(self, extra):
        sp = importlib.util.spec_from_file_location('queue_job_v5_k6', os.path.join(self.P, *KIT, 'tools', 'queue_job_v5.py'))
        Q = importlib.util.module_from_spec(sp); sp.loader.exec_module(Q)
        Q.TEMPLATE_SHA.update(extra)                       # the only change to the queue: the template's sha16
        Q.CFG.update({'free_mb': lambda: 200000})
        return Q

    def reg(self, name, row):
        r = subprocess.run([sys.executable, '-B', os.path.join(self.P, *CT, 'reg_append_v1.py'), self.run, name, '-'], input=json.dumps(row), capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr

    def entry_ready(self, v='V1'):
        """a variant, its GRADE job done with a passed hand-off R1 and its fire list on the scratch disk (one fire after 31 Dec)"""
        d = 'ideas/%s/defs/%s.json' % (IDEA, v); pr = 'ideas/%s/CARD_%s.md' % (IDEA, IDEA)
        w(os.path.join(self.run, d), json.dumps({'id': v, 'window': {'first': '20250901', 'last': '20260531'}})); w(os.path.join(self.run, pr), 'prereg\n')
        self.reg('VARIANTS', {'idea': IDEA, 'V': v, 'lean': 'FADE', 'def_rel': d, 'def_sha16': sha16(os.path.join(self.run, d)),
                              'prereg_rel': pr, 'prereg_sha16': sha16(os.path.join(self.run, pr)), 'reason': 'test'})
        gj = '20269000_GRADE_%s' % IDEA; g = os.path.join(self.run, 'receipts', gj)
        fl = os.path.join(self.v['SCRATCH'], 'work_' + RUNTAG, gj, '%s_FIRES_V1_LIST.tsv' % v)
        w(fl, 'coin\tt\tside\nBTC\t1757900000\t1\nETH\t1760000000\t-1\nBTC\t1768000000\t1\n')
        w(os.path.join(g, 'STAGES.tsv'), 'stage\trc\nend\t0\n')
        w(os.path.join(g, 'FIRES.tsv'), '%s\t3\t%s\t%s\n' % (v, sha16(fl), fl))
        w(os.path.join(g, 'HANDOFF', 'REAL_SEALED', 'REAL_RULES_%s.tsv' % v), 'key\tvalue\nR1\tPASS\n')
        self.d, self.pr, self.gj, self.fl = d, pr, gj, fl
        return gj

    def queue(self, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.Q.main(['--settings', self.settings] + list(a))
        return buf.getvalue()

    def run_job(self, twin):
        s = open(twin).read(); df = 'df -m %s |' % self.v['SCRATCH']
        assert s.count(df) == 1, 'the job reads the free space of SCRATCH, once'
        s = s.replace(df, "printf 'Filesystem\\nx x x 200000\\n' |")
        for real, mine in self.shamap.items():
            s = s.replace(' ' + real, ' ' + mine)
        p = os.path.join(self.root, 'sim', os.path.basename(twin)); w(p, s)
        r = subprocess.run(['bash', p], capture_output=True, text=True, cwd=self.root, stdin=subprocess.DEVNULL, env=dict(os.environ, K6_SAW=self.saw))
        return r, [json.loads(l) for l in open(self.saw)] if os.path.exists(self.saw) else []

    def store(self, *a, gate=None):
        """the runner on its own, as the job calls it: the settings keys as options, then AID FIRST LAST EVENTS SHA16 DEF CARD FAMILY"""
        g = self.v['FEED_GATE'] if gate is None else gate
        self.n = getattr(self, 'n', 0) + 1                          # one alarm id per call: a store folder is named by its second
        a = [x.replace('ALM_AD1_V1_SD', 'ALM_AD1_V%d_SD' % self.n) for x in a]
        opts = ['--python', self.v['PYTHON'], '--lab-days', self.v['LAB_DAYS'], '--scratch', self.v['SCRATCH'], '--research-root', self.v['RESEARCH_ROOT'], '--gate=' + g]
        if os.path.exists(self.saw):
            os.remove(self.saw)
        r = subprocess.run(['bash', self.runner] + (opts if not a or not a[0].startswith('-') else []) + list(a), capture_output=True, text=True, cwd=self.root,
                           stdin=subprocess.DEVNULL, env=dict(os.environ, K6_SAW=self.saw))
        return r, [json.loads(l) for l in open(self.saw)] if os.path.exists(self.saw) else []


ABS = re.compile(r'(?<![\w.$@)\]/*-])/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*[A-Za-z0-9_-]')


def check_body(sb, body):
    f = []
    if '@@' in body: f.append('placeholder left')
    if 'quiet window was removed by the owner 30 Oct 2026 23:32 Berlin' not in body: f.append('header lacks the removal note')
    if re.search(r'\bst quiet\b|\$h -ge 2320', body): f.append('still checks the quiet window')
    roots = [sb.P, sb.v['RESEARCH_ROOT'], sb.v['SCRATCH'], sb.v['LAB_DAYS'], sb.v['FEED_GATE']]
    stray = [p for p in ABS.findall(body) if p not in ('/dev/null',) and p != sb.v['PYTHON'] and not any(p == r or p.startswith(r + os.sep) for r in roots)]
    if stray: f.append('paths outside the package and the keys: %s' % stray[:5])
    for path in re.findall(r'^ck (\S+) [0-9a-f]{16}', body, re.M):
        if not path.startswith('$'): f.append('a pin by a literal path %s' % path)
    if '--gate=%s ' % sb.v['FEED_GATE'] not in body: f.append('the gate is not FEED_GATE as one word')
    return f


def grader_call(saw):
    return next((x for x in saw if os.path.basename(x['script']) == 'idea_to_grade_v3_2_s6_rel1.py'), None)


def opt(argv, k):
    for i, x in enumerate(argv):
        if x == k: return argv[i + 1]
        if x.startswith(k + '='): return x[len(k) + 1:]
    return None


def runner_tests(template, runner):
    """the runner on its own"""
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        sb = Sandbox(os.path.realpath(tmp), template, runner); sb.entry_ready()
        R = sb.v['RESEARCH_ROOT']; ev = sb.fl; es = sha16(ev); defrel = 'ALARM_DESIGN/runs/%s/%s' % (RUNTAG, sb.d); card = 'ALARM_DESIGN/runs/%s/ideas/%s/ALARM_CARD.md' % (RUNTAG, IDEA)
        base = ['ALM_AD1_V1_SD', '20250910', '20251231', ev, es, defrel, card, IDEA]
        r, saw = sb.store(*base); aid = 'ALM_AD1_V%d_SD' % sb.n
        g = grader_call(saw)
        if r.returncode != 0 or g is None: fails.append('runner: no grader run rc %d %s' % (r.returncode, (r.stderr + r.stdout)[-300:])); return fails
        a = g['argv']; T = os.path.join(sb.P, *I2G)
        want = {'--lab-root': sb.v['LAB_DAYS'], '--research-root': R, '--gate': sb.v['FEED_GATE'], '--roster': os.path.join(sb.P, *ROSTER),
                '--pins': os.path.join(T, 'I2G_PINS_V3_2_S6_REL1.json'), '--workers': '3', '--first': '20250910', '--last': '20251231', '--alarm-id': aid}
        for k, v in want.items():
            if opt(a, k) != v: fails.append('runner: grader %s %r, want %r' % (k, opt(a, k), v))
        if g['script'] != os.path.join(T, 'idea_to_grade_v3_2_s6_rel1.py'): fails.append('runner: grader script %s' % g['script'])
        out = opt(a, '--out') or ''
        if not out.startswith(os.path.join(sb.v['SCRATCH'], 'work_ALARMLIB', 'i2g_v3_2', 'full_%s_20250910_20251231_' % aid)) or g['cwd'] != os.path.dirname(out):
            fails.append('runner: store folder %s cwd %s' % (out, g['cwd']))
        D = os.path.dirname(out)
        if opt(a, '--events-subset') is None and '--events-subset' not in a: fails.append('runner: a fire after 31 Dec did not make the list a declared slice')
        reg = open(os.path.join(D, 'REGISTRY_SCRATCH.tsv')).read().split('\n')[2].split('\t') if os.path.isfile(os.path.join(D, 'REGISTRY_SCRATCH.tsv')) else []
        if reg != [aid, card, '1', defrel, sha16(os.path.join(R, defrel)), IDEA]: fails.append('runner: scratch registry row %s' % reg)
        if opt(a, '--registry') != os.path.join(D, 'REGISTRY_SCRATCH.tsv') or opt(a, '--ledger') != os.path.join(D, 'LEDGER_FULL.tsv'): fails.append('runner: registry or ledger %s' % a)
        ch = [x for x in os.listdir(os.path.join(sb.v['SCRATCH'], 'work_TOOLTRIAL', 'chain')) if x.startswith(aid + '_')] if os.path.isdir(os.path.join(sb.v['SCRATCH'], 'work_TOOLTRIAL', 'chain')) else []
        st = open(os.path.join(sb.v['SCRATCH'], 'work_TOOLTRIAL', 'chain', ch[0], 'STATUS.tsv')).read() if len(ch) == 1 else ''
        for s in ('events\t0', 'universe\t0', 'registry\t0', 'grader_store\t0', 'done\t0'):
            if s not in st: fails.append('runner: status %s missing (%s)' % (s, ch))
        chain = os.path.join(sb.v['SCRATCH'], 'work_TOOLTRIAL', 'chain'); before = sorted(os.listdir(chain))
        r2, saw2 = sb.store(*base[:2])
        if r2.returncode != 2 or saw2 or sorted(os.listdir(chain)) != before:
            fails.append('runner: fewer than 3 positional arguments not refused before writing (rc %d)' % r2.returncode)
        uni = [x for x in saw if os.path.basename(x['script']) == 'i2g_universe_v1.py']
        if not uni or uni[0]['script'] != os.path.join(T, 'i2g_universe_v1.py'): fails.append('runner: universe writer %s' % uni)
        r, saw = sb.store(*base, gate='')                                                         # FEED_GATE empty: one word, no gate
        g = grader_call(saw)
        if r.returncode or g is None or '--gate=' not in g['argv']: fails.append('runner: an empty gate is not --gate= (%s)' % (g and g['argv']))
        r, saw = sb.store(*(base[:4] + ['0' * 16] + base[5:]))
        if r.returncode != 2 or grader_call(saw): fails.append('runner: an events sha16 that differs ran (rc %d)' % r.returncode)
        r, saw = sb.store(*(base[:5] + ['ALARM_DESIGN/runs/%s/ideas/%s/defs/NO.json' % (RUNTAG, IDEA)] + base[6:]))
        if r.returncode != 2 or grader_call(saw): fails.append('runner: a definition missing under RESEARCH_ROOT ran (rc %d)' % r.returncode)
        r, saw = sb.store(*(base[:5] + ['team/RESEARCH/' + defrel] + base[6:]))
        if r.returncode != 2 or grader_call(saw): fails.append('runner: a DEF_REL of the old form (from the forensics root) ran (rc %d)' % r.returncode)
        w(os.path.join(sb.P, 'ALARM_DESIGN', 'runs', RUNTAG, 'ideas', IDEA, 'defs', 'ONLYAL.json'), '{}')          # a definition in the package only
        r, saw = sb.store(*(base[:5] + ['ALARM_DESIGN/runs/%s/ideas/%s/defs/ONLYAL.json' % (RUNTAG, IDEA)] + base[6:]))
        if r.returncode != 2 or grader_call(saw): fails.append('runner: a definition found in the Alarm folder, not under RESEARCH_ROOT, ran (rc %d)' % r.returncode)
        o = ['--python', sb.v['PYTHON'], '--lab-days', sb.v['LAB_DAYS'], '--scratch', sb.v['SCRATCH'], '--research-root', R, '--gate=' + sb.v['FEED_GATE']]
        for k in ('--python', '--lab-days', '--scratch', '--research-root'):
            i = o.index(k)
            for bad in (o[:i] + o[i + 2:], o[:i + 1] + ['relative/path'] + o[i + 2:]):
                r, saw = sb.store(*(bad + base))
                if r.returncode != 2 or saw: fails.append('runner: %s missing or relative not refused (rc %d)' % (k, r.returncode))
        for bad in (o[:-1], o[:-1] + ['--gate=relative'], o + ['--workers', '0'], o + ['--lab-root', '/x']):
            r, saw = sb.store(*(bad + base))
            if r.returncode != 2 or saw: fails.append('runner: %s not refused (rc %d)' % (bad[len(o) - 1:], r.returncode))
        r, saw = sb.store(*(o + ['--lab-root', '/x'] + base))
        if 'REFUSED: unknown option --lab-root' not in r.stderr: fails.append('runner: an unknown option not named in its refusal (%s)' % r.stderr[-200:])
        r, saw = sb.store(*(o + ['--workers', '1'] + base)); g = grader_call(saw)
        if r.returncode or not g or opt(g['argv'], '--workers') != '1': fails.append('runner: --workers 1 not passed')
        pins = os.path.join(sb.P, *I2G, 'I2G_PINS_V3_2_S6_REL1.json'); open(pins, 'a').write(' ')
        r, saw = sb.store(*base)
        if r.returncode != 4 or grader_call(saw): fails.append('runner: a changed pins file ran (rc %d)' % r.returncode)
        out = os.path.join(sb.root, 'lone'); os.makedirs(out); lone = os.path.join(out, RUNNER); shutil.copyfile(sb.runner, lone)
        r = subprocess.run(['bash', lone] + o + base, capture_output=True, text=True, cwd=sb.root)
        if r.returncode != 2 or 'NOT INSIDE AN ALARM PACKAGE' not in r.stderr: fails.append('runner: outside an Alarm package not refused (rc %d)' % r.returncode)
    return fails


def job_tests(template, runner):
    fails = []
    with tempfile.TemporaryDirectory() as tmp:
        sb = Sandbox(os.path.realpath(tmp), template, runner); gj = sb.entry_ready()
        out = sb.queue(RUNTAG, 'ENTRY', IDEA, 'V1', '--from-job', gj, '--dry')                     # 1 ENTRY filled, nothing queued
        fails += check_body(sb, out)
        out = sb.queue(RUNTAG, 'ENTRY', IDEA, 'V1', '--from-job', gj)                              # 2 ENTRY queued and run
        twin = os.path.join(sb.run, re.search(r' twin (\S+) ', out).group(1)); j = re.search(r'(\d+)_judge_', twin).group(1)
        r, saw = sb.run_job(twin)
        rec = os.path.join(sb.run, 'receipts', '%s_ENTRY_%s' % (j, IDEA)); st = open(os.path.join(rec, 'STAGES.tsv')).read() if os.path.isdir(rec) else ''
        for s in ('markout_units\t0', 'events_V1\t0', 'store_V1\t0', 'markout_V1\t0', 'end\t0'):
            if s not in st: fails.append('ENTRY stage %s missing: rc %d %s %s' % (s, r.returncode, st[-400:], r.stderr[-300:]))
        if '2 fires Sep 10-Dec 31' not in st: fails.append('ENTRY events: the fire after 31 Dec kept (%s)' % st[-200:])
        W = os.path.join(sb.v['SCRATCH'], 'work_' + RUNTAG, '%s_ENTRY_%s' % (j, IDEA)); g = grader_call(saw)
        if not g: fails.append('ENTRY: no grader call'); return fails
        a = g['argv']; R = sb.v['RESEARCH_ROOT']
        for k, v in {'--lab-root': sb.v['LAB_DAYS'], '--research-root': R, '--gate': sb.v['FEED_GATE'], '--alarm-id': 'ALM_%s_V1_SD' % SEAT,
                     '--first': '20250910', '--last': '20251231'}.items():
            if opt(a, k) != v: fails.append('ENTRY: grader %s %r, want %r' % (k, opt(a, k), v))
        ev = opt(a, '--events') or ''
        if not ev.startswith(os.path.join(sb.v['SCRATCH'], 'work_ALARMLIB', 'i2g_v3_2') + os.sep) and not ev.startswith(W + os.sep):
            fails.append('ENTRY: events %s' % ev)
        D = os.path.dirname(opt(a, '--out') or '/x/y')
        reg = open(os.path.join(D, 'REGISTRY_SCRATCH.tsv')).read().split('\n')[2].split('\t') if os.path.isfile(os.path.join(D, 'REGISTRY_SCRATCH.tsv')) else []
        if reg[:4] != ['ALM_%s_V1_SD' % SEAT, 'ALARM_DESIGN/runs/%s/ideas/%s/ALARM_CARD.md' % (RUNTAG, IDEA), '1', 'ALARM_DESIGN/runs/%s/%s' % (RUNTAG, sb.d)]:
            fails.append('ENTRY: scratch registry row %s' % reg)
        mk = [x for x in saw if os.path.basename(x['script']) == 'markout_v1_2.py']
        if not mk or mk[0]['cwd'] != os.path.join(sb.P, *MO) or opt(mk[0]['argv'], '--run') != opt(a, '--out') or opt(mk[0]['argv'], '--settings') != 'settings/SETTINGS_V1.json':
            fails.append('ENTRY: markout call %s' % mk)
        un = [x for x in saw if os.path.basename(x['script']) == 'test_markout_v1_2.py']
        if not un or un[0]['cwd'] != os.path.join(sb.P, *MO): fails.append('ENTRY: markout units call %s' % un)
        uw = [x for x in saw if os.path.basename(x['script']) == 'i2g_universe_v1.py']
        if not uw or uw[0]['cwd'] != sb.P: fails.append('ENTRY: the store did not start in the Alarm folder (universe writer %s)' % uw)
        places = open(os.path.join(rec, 'V1', 'STORE_PLACES.tsv')).read() if os.path.isfile(os.path.join(rec, 'V1', 'STORE_PLACES.tsv')) else ''
        if os.path.join(sb.v['SCRATCH'], 'work_TOOLTRIAL', 'chain') not in places or D not in places: fails.append('ENTRY: store places %s' % places)
        for x in ('STORE_STATUS.tsv', 'MARKOUT/GATES.json', 'MARKOUT/CURVE.tsv'):
            if not os.path.isfile(os.path.join(rec, 'V1', x)): fails.append('ENTRY: receipt %s not kept' % x)
        stok = sb.Q.stage_ok(sb.run, 'receipts/%s_ENTRY_%s' % (j, IDEA), 'V1', 'ENTRY')
        if stok is not True: fails.append('ENTRY: the queue does not read the job as done for V1 (%r)' % stok)
    return fails


def all_tests(template, runner):
    return job_tests(template, runner) + runner_tests(template, runner)


QUIET = 'h=$((10#$(date -u +%H%M))); if [ $h -ge 2320 ] || [ $h -lt 15 ]; then st quiet 0 0 "QUIET WINDOW NEAR: not started"; st end 0 0 "not started"; exit 0; fi\n'
MUTANTS = [   # (file, the text, the bug planted)
    ('JOB', 'f=$(fmb); st start 0 0', QUIET + 'f=$(fmb); st start 0 0'),
    ('JOB', 'AL=@@ALARM@@; PY=@@PYTHON@@; RR=@@RESEARCH_ROOT@@', 'AL=@@ALARM@@; PY=python3; RR=@@RESEARCH_ROOT@@'),
    ('JOB', 'PY=@@PYTHON@@; RR=@@RESEARCH_ROOT@@', 'PY=@@PYTHON@@; RR=@@SCRATCH@@'),
    ('JOB', 'RDREL=ALARM_DESIGN/runs/@@RUNTAG@@', 'RDREL=team/RESEARCH/ALARM_DESIGN/runs/@@RUNTAG@@'),
    ('JOB', 'X=$AL/07_Price_path/tree/team/RESEARCH/tools/markout', 'X=$AL/07_Price_path/tree/tools/markout'),
    ('JOB', 'CH=$AL/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/run_alarm_store_v11_noladder.sh', 'CH=$AL/Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/run_alarm_store_v10_3_noladder.sh'),
    ('JOB', 'W=@@SCRATCH@@/work_@@RUNTAG@@/$J', 'W=@@SCRATCH@@/$J'),
    ('JOB', 'fmb(){ df -m @@SCRATCH@@', 'fmb(){ df -m @@RESEARCH_ROOT@@'),
    ('JOB', '[ -f $RR/$CARDREL ]', '[ -f $AL/$CARDREL ]'),
    ('JOB', 'bash $CH --python $PY ', 'bash $CH --python python3 '),
    ('JOB', '--lab-days @@LAB_DAYS@@ ', '--lab-days @@SCRATCH@@ '),
    ('JOB', '--scratch @@SCRATCH@@ --research-root', '--scratch @@RESEARCH_ROOT@@ --research-root'),
    ('JOB', '--research-root $RR --gate', '--research-root $RD --gate'),
    ('JOB', '--gate=@@FEED_GATE@@ $AID', '--gate= $AID'),
    ('JOB', 'CD=$(ls -dt @@SCRATCH@@/work_TOOLTRIAL/chain/', 'CD=$(ls -dt @@SCRATCH@@/chain/'),
    ('JOB', '\n  cd $AL\n', '\n  cd /\n'),
    ('JOB', 'ck $X/markout_v1_2.py ', 'ck $X/markout_v1_1.py '),
    ('JOB', '$PY -B markout_v1_2.py run', '$PY -B markout_v1_1.py run'),
    ('JOB', '$PY -B test_markout_v1_2.py $W/units', '$PY -B test_markout_v1_1.py $W/units'),
    ('JOB', ' The quiet window was removed by the owner 30 Oct 2026 23:32 Berlin', ' Stops before the quiet window'),
    ('JOB', '# WRITES @@SCRATCH@@/work_@@RUNTAG@@/@@JOBNUM@@_ENTRY_@@IDEA@@/,', '# WRITES /data/scratch/work_@@RUNTAG@@/@@JOBNUM@@_ENTRY_@@IDEA@@/,'),
    ('RUN', 'R=$RR\n', 'R=$SCR\n'),
    ('RUN', '--python) PY=${2:-};', '--python) PY=python3;'),
    ('RUN', '--lab-days) LABD=${2:-};', '--lab-days) LABD=/x;'),
    ('RUN', '--scratch) SCR=${2:-};', '--scratch) SCR=${2:-}/x;'),
    ('RUN', '--research-root) RR=${2:-};', '--research-root) RR=${2:-}/x;'),
    ('RUN', '--workers) NW=${2:-};', '--workers) NW=3;'),
    ('RUN', '--gate=*) GATE=${1#--gate=}; GSET=1; shift;;', '--gate=*) GATE=; GSET=1; shift;;'),
    ('RUN', '    *) break;;\n', '    *) shift;;\n'),
    ('RUN', '[ $# -ge 3 ] ||', '[ $# -ge 0 ] ||'),
    ('RUN', 'HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P); AL=$HERE', 'HERE=$(pwd -P); AL=$HERE'),
    ('RUN', 'while [ "$AL" != / ] && ! {', 'while false && ! {'),
    ('RUN', '$PY -B $T/idea_to_grade_v3_2_s6_rel1.py --events', '$PY -B $T/idea_to_grade_v3_2_s6.py --events'),
    ('RUN', '    --roster $ROSTER \\', '    --roster $P7/ROSTER_BUILD.json \\'),
    ('RUN', 'C=$SCR/work_TOOLTRIAL/chain/', 'C=$RR/work_TOOLTRIAL/chain/'),
    ('RUN', 'D=$SCR/work_ALARMLIB/i2g_v3_2/', 'D=$RR/work_ALARMLIB/i2g_v3_2/'),
    ('RUN', 'T=$P7/team/RESEARCH/tools/idea_to_grade', 'T=$P7/tools/idea_to_grade'),
    ('RUN', 'P7=$AL/07_Price_path/tree;', 'P7=$AL/01_Detection/tree;'),
    ('RUN', 'ROSTER=$P7/team/OUTSIDE/COORD', 'ROSTER=$P7/_team/OUTSIDE/COORD'),
    ('RUN', '    --lab-root "$LABD" --research-root "$R" --gate="$GATE" )', '    --research-root "$R" --gate="$GATE" )'),
    ('RUN', '    --lab-root "$LABD" --research-root "$R" --gate="$GATE" )', '    --lab-root "$LABD" --gate="$GATE" )'),
    ('RUN', '    --lab-root "$LABD" --research-root "$R" --gate="$GATE" )', '    --lab-root "$LABD" --research-root "$R" )'),
    ('RUN', '[ -f "$R/$RDEF" ]', '[ -f "$AL/$RDEF" ] || [ -f "$R/$RDEF" ]'),
    ('RUN', 'DSHA=$(shasum -a 256 "$R/$RDEF"', 'DSHA=$(shasum -a 256 "$EV"'),
    ('RUN', 'for v in "$PY" "$LABD" "$SCR" "$RR"; do', 'for v in "$PY" "$LABD" "$SCR"; do'),
    ('RUN', '[ $GSET = 1 ] ||', 'true ||'),
    ('RUN', "case \"$GATE\" in ''|/*) ;;", "case \"$GATE\" in *) ;;"),
    ('RUN', "case \"$NW\" in [1-8]) ;;", "case \"$NW\" in *) ;;"),
    ('RUN', 'NW=3\n', 'NW=1\n'),
    ('RUN', '--workers $NW --pins', '--workers 3 --pins'),
    ('RUN', '--pins $T/I2G_PINS_V3_2_S6_REL1.json \\', '--pins $T/I2G_PINS_V3_2_S6.json \\'),
    ('RUN', '[ "$AL" != / ] || { echo "REFUSED: NOT INSIDE', 'AL=$HERE; [ "$AL" != / ] || { echo "REFUSED: NOT INSIDE'),
    ('RUN', '    --*) echo "REFUSED: unknown option $1" >&2; exit 2;;\n', ''),
    ('RUN', '= a1ec98395a62de77 ]', '= 75aee82e3ab5f99d ]'),
]


def main():
    if not (os.path.isfile(os.path.join(PKG, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(PKG, 'settings'))):
        raise SystemExit('run this test from an Alarm package: no _tools/settings_v1.py and settings/ at %s' % PKG)
    tpl = open(os.path.join(KIT5, 'jobs', 'JOB_ENTRY_V6.job.sh.txt')).read(); run = open(os.path.join(PKG, *CT, RUNNER)).read()
    f = all_tests(tpl, run)
    print('TESTS', 'PASS' if not f else 'FAIL %s' % f)
    killed = 0
    for which, a, b in MUTANTS:
        src = tpl if which == 'JOB' else run
        assert src.count(a) >= 1, ('mutant target not found', which, a)
        t2, r2 = (src.replace(a, b, 1), run) if which == 'JOB' else (tpl, src.replace(a, b, 1))
        try:
            caught = bool(all_tests(t2, r2))
        except Exception:                                                           # a refused queue or a missing receipt also catches it
            caught = True
        killed += caught
        print('MUTANT %-3s %-74s %s' % (which, b.strip().split('\n')[-1][:74], 'KILLED' if caught else 'SURVIVED'))
    print('MUTANTS %d of %d killed' % (killed, len(MUTANTS)))
    return 1 if f or killed != len(MUTANTS) else 0


if __name__ == '__main__':
    sys.exit(main())
