#!/usr/bin/env python3
"""test_v1_21_fixes.py (SCOUT, 3 Nov 2026, V1_21 fixes, playground; TEST, NOT REVIEWED): the five snags of run SCOUTR12_20261103, each
with a test that fails on the released code (ALARM_V1_20_3 and ledger_add_v5) and passes on the fix. Seconds; planted worlds in temp
folders; stub true_gate; no market data; the install is only read (its template is copied, never written).

  python3 -B test_v1_21_fixes.py            the fixes (expected: every test passes)
  V121_OLD=1 python3 -B test_v1_21_fixes.py the released code and pages in the same tests (expected: each S<n> test fails)
  V121_FIX=<folder>                         the fixes folder (default: the one holding this file); mutants_v1_21.py sets it to a mutant copy
ALARM_V1_21 (SCOUT 3 Nov 2026): runs from the install: the pages are read at the package's own paths (AGENTS.md, playbook/, cards/), the
install is the package holding this file (ALARM_BASE overrides; V121_OLD=1 needs ALARM_BASE=<ALARM_V1_20_3>), and the real ledger and
ledger_add_v5 with its suites are frozen copies in data_v1_21/ (V121_LEDGER and V121_LEDGER_DIR override), so no dev tree is read.
Classes: S1 the run folder, S2 the run tag, S3 the TRUE kind, S4 decide without ENTRY, S5 the ledger tool; KEEP checks what must stay equal."""
import contextlib, hashlib, importlib.util, io, json, os, re, shutil, stat, subprocess, sys, tempfile, unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
FIX = os.environ.get('V121_FIX') or PKG
OLD = os.environ.get('V121_OLD') == '1'
INSTALL = os.environ.get('ALARM_BASE') or PKG
DATA = os.path.join(HERE, 'data_v1_21')
LEDGER_DIR = os.environ.get('V121_LEDGER_DIR') or os.path.join(DATA, 'ledger_v5')
REAL_LEDGER = os.environ.get('V121_LEDGER') or os.path.join(DATA, 'TRIES_LEDGER_V1.tsv')
KIT = 'Agentic/tree/ALARM_DESIGN/KIT_V5'; RUNT = 'Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'; TGD = '03_Grading/tree/tools/true_gate'
RUN = 'AB1_20261103'; IDEA = 'TESTIDEA'; GRADE = '20269001_GRADE_' + IDEA
s16b = lambda b: hashlib.sha256(b).hexdigest()[:16]
s16 = lambda p: s16b(open(p, 'rb').read())
dg = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]
NEW_TOOLS = {'queue': 'queue_job_v15.py', 'decide': 'decide_v5.py', 'audit': 'audit_run_v5.py', 'ledger': 'ledger_add_v7.py', 'start': 'start_run_v1.py'}
OLD_TOOLS = {'queue': 'queue_job_v14.py', 'decide': 'decide_v4.py', 'audit': 'audit_run_v4.py'}
LABEL = {'kind': 'metric_test', 'code': 'E2.S05', 'when': 'present', 'end_s': 3600, 'test': 'falling', 'change': 'pct', 'thr': 0.5, 'max_age_s': 300}
MIRROR = dict(LABEL, test='rising')


def wr(p, t, mode='w'):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, mode) as f:
        f.write(t)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def page(rel):
    """a page: the fix's draft, or the install's page with V121_OLD"""
    return open(os.path.join(INSTALL, rel) if OLD else os.path.join(FIX, rel)).read()


STUB_TG3 = r'''import hashlib, json, os, sys
a = sys.argv
cl = json.load(open(a[2]))
if a[1] == 'check':
    print('OK trigger reads X; families Y'); sys.exit(0)
if os.environ.get('TG_FAIL'):
    print('REFUSED PERFIRE_CHANGED: planted'); sys.exit(2)
out = a[3]; os.makedirs(out)
open(os.path.join(out, 'TRUE_CARD.txt'), 'w').write('VERDICT UNSURE: planted\n')
card = hashlib.sha256(open(os.path.join(out, 'TRUE_CARD.txt'), 'rb').read()).hexdigest()[:16]
h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]
row = {'id': cl['id'], 'verdict': 'UNSURE', 'idea': cl['idea'], 'V': cl['V'], 'def_sha16': cl['def_sha16'], 'perfire_sha16': cl['perfire_sha16'],
       'label_sha16': h(cl['label']), 'mirror_sha16': h(cl['mirror']), 'card_sha16': card}
t = '\t'.join(row) + '\n' + '\t'.join(str(x) for x in row.values()) + '\n'
open(os.path.join(out, 'TRUE_ROW.tsv'), 'w').write(t); open(os.path.join(out, 'TRUE_ROW.sha16'), 'w').write(hashlib.sha256(t.encode()).hexdigest()[:16] + '\n')
print('VERDICT UNSURE: planted')
'''


class World:
    """a planted Alarm folder (copies of the install's settings reader, register writer, KIT tools; the fixes' tools; a stub true_gate)
    and a planted data root: one run, one sealed variant, one finished GRADE with its sealed PERFIRE"""
    def __init__(self):
        self.t = tempfile.mkdtemp(prefix='v121_'); self.A = os.path.join(self.t, 'Alarm'); self.D = os.path.join(self.t, 'data')
        cp = lambda src, rel: (os.makedirs(os.path.dirname(os.path.join(self.A, rel)), exist_ok=True), shutil.copyfile(src, os.path.join(self.A, rel)))
        for rel in ('_tools/settings_v1.py', 'settings/SETTINGS_EXAMPLE.env', RUNT + '/reg_append_v1.py', RUNT + '/read_stratentry_v1.py'):
            cp(os.path.join(INSTALL, rel), rel)
        for n in ('audit_run_v3.py', 'audit_run_v4.py', 'decide_v2.py', 'decide_v4.py', 'decide_forward_v2.py', 'queue_job_v14.py'):
            cp(os.path.join(INSTALL, KIT, 'tools', n), KIT + '/tools/' + n)
        if not OLD:
            for n in NEW_TOOLS.values():
                cp(os.path.join(FIX, KIT, 'tools', n), KIT + '/tools/' + n)
            cp(os.path.join(FIX, KIT, 'jobs/JOB_TRUE_V1.job.sh.txt'), KIT + '/jobs/JOB_TRUE_V1.job.sh.txt')
            cp(os.path.join(FIX, KIT, 'jobs/JOB_TRUE_V2.job.sh.txt'), KIT + '/jobs/JOB_TRUE_V2.job.sh.txt')   # SCO-A179: the TRUE kind's template
        tpl = os.path.join(INSTALL, KIT, 'runs/TEMPLATE_V4')
        shutil.copytree(tpl, os.path.join(self.A, KIT, 'runs/TEMPLATE_V4'))
        for d, ds, fs in os.walk(os.path.join(self.A, KIT, 'runs/TEMPLATE_V4')):          # the install's modes: read only
            for f in fs:
                os.chmod(os.path.join(d, f), 0o400)
        wr(os.path.join(self.A, TGD, 'true_gate_v3.py'), STUB_TG3)
        wr(os.path.join(self.A, TGD, 'true_gate_v4.py'), STUB_TG3)   # SCO-A179: JOB_TRUE_V2 runs v4
        for n in ('true_gate_v1.py', 'true_gate_v2.py'):
            wr(os.path.join(self.A, TGD, n), '# stub %s\n' % n)
        self.R = os.path.join(self.D, 'research'); self.SC = os.path.join(self.D, 'scratch'); self.QU = os.path.join(self.D, 'q'); self.HB = os.path.join(self.D, 'hb')
        for q in range(1, 22):
            for x in ('IN', 'RUN'):
                os.makedirs(os.path.join(self.QU, 'Q_V%d' % q, x))
        for p in (self.SC, self.HB, os.path.join(self.D, 'lab'), os.path.join(self.D, 'store'), os.path.join(self.R, 'ALARM_DESIGN/runs/IDEAS_CLAIMED')):
            os.makedirs(p, exist_ok=True)
        self.alloc = os.path.join(self.D, 'alloc.py'); wr(self.alloc, 'import os\np=%r\nn=int(open(p).read()) if os.path.exists(p) else 20269100\nopen(p,"w").write(str(n+1))\nprint(n)\n' % (self.alloc + '.n'))
        keys = [l.split('=')[0] for l in open(os.path.join(self.A, 'settings/SETTINGS_EXAMPLE.env')) if re.match(r'[A-Z]', l)]
        self.vals = dict(PYTHON=sys.executable, LAB_DAYS=os.path.join(self.D, 'lab'), RESEARCH_STORE=os.path.join(self.D, 'store'), SCRATCH=self.SC, RESEARCH_ROOT=self.R,
                         RUNNER_QUEUES=self.QU, RUNNER_ALLOC=self.alloc, BOARD=self.HB)
        self.S = os.path.join(self.D, 'S.env'); wr(self.S, ''.join('%s=%s\n' % (k, self.vals.get(k, '')) for k in keys))
        self.Rn = os.path.join(self.R, 'ALARM_DESIGN/runs', RUN)

    def tool(self, k):
        return os.path.join(self.A, KIT, 'tools', (OLD_TOOLS if OLD else NEW_TOOLS)[k])

    def run_tool(self, k, *a, env=None):
        e = dict(os.environ); e.update(env or {})
        return subprocess.run([sys.executable, '-B', self.tool(k)] + list(a), capture_output=True, text=True, env=e)

    def plant_run(self):
        """the run as start_run_v1 would leave it, writable, then the claim, the variant, the GRADE and its seal"""
        shutil.copytree(os.path.join(INSTALL, KIT, 'runs/TEMPLATE_V4'), self.Rn)
        for d, ds, fs in os.walk(self.Rn):
            os.chmod(d, 0o755)
            for f in fs:
                os.chmod(os.path.join(d, f), 0o644)
        wr(os.path.join(self.R, 'ALARM_DESIGN/runs/IDEAS_CLAIMED', '%s_%s.txt' % (RUN, IDEA)), 'claim\n')
        dfp = os.path.join(self.Rn, 'ideas', IDEA, 'defs/V1.json'); wr(dfp, json.dumps({'window': {'first': '20250901', 'last': '20260430'}}))
        card = os.path.join(self.Rn, 'ideas', IDEA, 'CARD_%s.md' % IDEA); wr(card, 'card\n1b `true_label=%s true_mirror=%s`\n' % (dg(LABEL), dg(MIRROR)))
        self.var = dict(utc='2026-11-03T00:01:00Z', idea=IDEA, V='V1', lean='FADE', def_rel='ideas/%s/defs/V1.json' % IDEA, def_sha16=s16(dfp),
                        prereg_rel='ideas/%s/CARD_%s.md' % (IDEA, IDEA), prereg_sha16=s16(card), reason='r')
        self.row('VARIANTS', self.var)
        n = GRADE.split('_')[0]; name = 'jobs/%s_judge_AB1_GRADE_%s.job.sh' % (n, IDEA)
        wr(os.path.join(self.Rn, name), 'VS=(V1)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(FADE)\nPERFIRE_SEAL\n' % (self.var['def_rel'], self.var['def_sha16']))
        self.row('RUNS', dict(utc_queued='2026-11-03T00:02:00Z', job=name, job_sha16=s16(os.path.join(self.Rn, name)), kind='GRADE', idea=IDEA, variants='V1', queue='Q_V1',
                              prereg_rel=self.var['prereg_rel'], prereg_sha16=self.var['prereg_sha16'], writes_mb='1', mem_mb='1', minutes='1', template_sha16='x', from_job='-', receipts_rel='receipts/' + GRADE))
        g = os.path.join(self.Rn, 'receipts', GRADE)
        wr(os.path.join(g, 'STAGES.tsv'), 'stage\trc\tseconds\tutc\tnote\n' + ''.join('%s\t0\t1\t2026-11-03T00:03:00Z\tn\n' % s for s in ('grade_V1', 'perfire_V1', 'perfire_test_V1', 'perfire_seal_V1', 'handoff', 'end')))
        w = os.path.join(self.SC, 'work_' + RUN, GRADE); self.pf = os.path.join(w, 'PERFIRE_V1.tsv')
        wr(self.pf, 'kind\tcoin\tt\tside\tw\tc\nA\tBTC\t1760000000\t1\t1\t0.1\nR\tSOL\t1760000100\t1\t0.5\t0.1\n')
        fl = os.path.join(w, 'V1_FIRES_V1_LIST.tsv'); wr(fl, 'coin\tt\tside\nBTC\t1760000000\t1\n')
        wr(os.path.join(g, 'FIRES.tsv'), 'V1\t1\t%s\t%s\n' % (s16(fl), fl))
        wr(os.path.join(g, 'PERFIRE_SEAL.tsv'), 'V1\t%s\t1\t1\t1760000000\t1760000100\t2\t%s\n' % (s16(self.pf), GRADE))
        self.sha16_txt(g)
        self.claim_rel = 'ideas/%s/TRUE_V1_HLOIFALL.json' % IDEA
        self.claim = {'id': '%s_V1_HLOIFALL' % IDEA, 'alarm_id': 'AB1_%s_V1' % IDEA, 'idea': IDEA, 'V': 'V1', 'claim': 'planted', 'def': dfp, 'def_sha16': self.var['def_sha16'],
                      'perfire': self.pf, 'perfire_sha16': s16(self.pf), 'first': '20250910', 'last': '20251231', 'lab_days': self.vals['LAB_DAYS'], 'lean': 'FADE',
                      'label': LABEL, 'mirror': MIRROR, 'activity': {'code': 'E2.S05', 'mode': 'level', 'max_age_s': 300}}
        self.write_claim()

    def write_claim(self, **k):
        c = dict(self.claim, **k); p = os.path.join(self.Rn, self.claim_rel)
        if os.path.exists(p):
            os.rename(p, p + '.old_%d' % len(os.listdir(os.path.dirname(p))))
        wr(p, json.dumps(c, indent=1))

    def sha16_txt(self, d):
        wr(os.path.join(d, 'SHA16.txt'), ''.join('%s  %s\n' % (hashlib.sha256(open(os.path.join(d, x), 'rb').read()).hexdigest(), x) for x in sorted(os.listdir(d)) if x.endswith('.tsv') and x != 'SHA16.txt'))

    def row(self, reg, d):
        p = os.path.join(self.Rn, 'registers', reg + '.tsv')
        h = [l for l in open(p).read().split('\n') if l and not l.startswith('#')][0].split('\t')
        wr(p, '\t'.join(str(d.get(k, '-')) for k in h) + '\n', 'a')

    def rows(self, reg):
        ls = [l for l in open(os.path.join(self.Rn, 'registers', reg + '.tsv')).read().split('\n') if l and not l.startswith('#')]
        h = ls[0].split('\t'); return [dict(zip(h, l.split('\t'))) for l in ls[1:]]

    def q_true(self, *a, item=None):
        return self.run_tool('queue', '--settings', self.S, RUN, 'TRUE', IDEA, item or 'V1=' + self.claim_rel, '--from-job', GRADE, *a)


# ---------------------------------------------------------------- S1 the run folder
class S1_RunFolder(unittest.TestCase):
    def setUp(self):
        self.w = World(); os.makedirs(os.path.join(self.w.R, 'ALARM_DESIGN/runs'), exist_ok=True)
        tpl = os.path.join(self.w.A, KIT, 'runs/TEMPLATE_V4')
        self.before = {os.path.relpath(os.path.join(d, f), tpl): (os.stat(os.path.join(d, f)).st_mode, os.stat(os.path.join(d, f)).st_mtime_ns, s16(os.path.join(d, f)))
                       for d, ds, fs in os.walk(tpl) for f in fs}

    def start(self, tag=RUN):
        """what the page tells an agent to run: OLD the cp line of AGENTS.md, NEW start_run_v1"""
        if OLD:
            return subprocess.run(['cp', '-R', '-n', os.path.join(self.w.A, KIT, 'runs/TEMPLATE_V4'), os.path.join(self.w.R, 'ALARM_DESIGN/runs', tag)], capture_output=True, text=True)
        return self.w.run_tool('start', '--settings', self.w.S, tag)

    def test_run_folder_is_writable_and_equal(self):
        r = self.start(); self.assertEqual(r.returncode, 0, r.stderr)
        run = self.w.Rn
        os.makedirs(os.path.join(run, 'ideas', IDEA))                                      # the agent's first write (PROBLEMS row 1)
        with open(os.path.join(run, 'registers/PROBLEMS.tsv'), 'a') as f:
            f.write('x\n')
        tpl = os.path.join(self.w.A, KIT, 'runs/TEMPLATE_V4')
        for rel, (_, _, s) in self.before.items():
            if rel != 'registers/PROBLEMS.tsv':
                self.assertEqual(s16(os.path.join(run, rel)), s, rel)
        after = {os.path.relpath(os.path.join(d, f), tpl): (os.stat(os.path.join(d, f)).st_mode, os.stat(os.path.join(d, f)).st_mtime_ns, s16(os.path.join(d, f))) for d, ds, fs in os.walk(tpl) for f in fs}
        self.assertEqual(after, self.before)                                               # the install is never touched

    def test_refuses_an_existing_run_and_never_merges(self):
        self.assertEqual(self.start().returncode, 0)
        wr(os.path.join(self.w.Rn, 'mine.txt'), 'kept\n')
        r = self.start(); self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn('RUN FOLDER EXISTS', r.stderr)
        self.assertEqual(open(os.path.join(self.w.Rn, 'mine.txt')).read(), 'kept\n')

    def test_refuses_a_run_folder_inside_the_install(self):
        if OLD:
            self.fail('no released start-run tool')
        S = load(os.path.join(self.w.A, KIT, 'tools/start_run_v1.py'), 'sr1')
        os.makedirs(os.path.join(self.w.A, 'inner/ALARM_DESIGN/runs'))
        with self.assertRaises(S.Refused) as c:
            S.start(self.w.A, os.path.join(self.w.A, 'inner'), RUN)
        self.assertIn('INSIDE THE ALARM FOLDER', str(c.exception)); self.assertFalse(os.path.exists(os.path.join(self.w.A, 'inner/ALARM_DESIGN/runs', RUN)))

    def test_modes_are_set_whatever_the_umask(self):
        if OLD:
            self.fail('no released start-run tool')
        r = subprocess.run([sys.executable, '-B', self.w.tool('start'), '--settings', self.w.S, RUN], capture_output=True, text=True, preexec_fn=lambda: os.umask(0o077))
        self.assertEqual(r.returncode, 0, r.stderr)
        for d, ds, fs in os.walk(self.w.Rn):
            self.assertEqual(stat.S_IMODE(os.stat(d).st_mode), 0o755, d)
            for f in fs:
                self.assertEqual(stat.S_IMODE(os.stat(os.path.join(d, f)).st_mode), 0o644, f)

    def test_a_copy_that_differs_is_refused(self):
        if OLD:
            self.fail('no released start-run tool')
        S = load(os.path.join(self.w.A, KIT, 'tools/start_run_v1.py'), 'sr2'); real = S.sha16
        S.sha16 = lambda p: 'damaged' if p.startswith(self.w.Rn) else real(p)
        with self.assertRaises(S.Refused) as c:
            S.start(self.w.A, self.w.R, RUN)
        self.assertIn('COPY DIFFERS', str(c.exception))

    def test_page_names_the_tool_not_the_bare_cp(self):
        t = page('AGENTS.md'); f = t[t.index('## The folder'):t.index('## The loop')]
        self.assertIn('start_run_v1.py', f); self.assertNotRegex(f, r'start it with\s+`cp -R -n')


# ---------------------------------------------------------------- S2 the run tag
class S2_RunTag(unittest.TestCase):
    def test_launch_prompt_says_the_seat_rule(self):
        t = page('playbook/LAUNCH_PROMPT_ALARM_V1.md')
        self.assertRegex(t, r'no underscore'); self.assertIn('SCOUTR12', t)

    def test_agents_page_says_the_seat_rule(self):
        t = page('AGENTS.md'); self.assertRegex(t, r'RUN = `<SEAT>_<YYYYMMDD>`[^\n]*no underscore')

    def test_start_names_the_tag_to_use(self):
        if OLD:
            self.fail('no released start-run tool')
        w = World(); os.makedirs(os.path.join(w.R, 'ALARM_DESIGN/runs'), exist_ok=True)
        r = w.run_tool('start', '--settings', w.S, 'SCOUT_R12_20261103')
        self.assertEqual(r.returncode, 2); self.assertIn('write SCOUTR12_20261103', r.stderr)
        self.assertEqual(w.run_tool('start', '--settings', w.S, 'SCOUTR12_20261303').returncode, 2)     # not a calendar day
        self.assertFalse(os.path.exists(os.path.join(w.R, 'ALARM_DESIGN/runs/SCOUT_R12_20261103')))

    def test_queue_refusal_says_why(self):
        w = World(); r = w.run_tool('queue', '--settings', w.S, 'SCOUT_R12_20261103', 'COUNT', IDEA, 'V1=x')
        self.assertEqual(r.returncode, 2); self.assertIn('no underscore', r.stderr)


class KEEP_RunTagOneRule(unittest.TestCase):
    """why the pattern is kept: every tool holds the same RUNTAG, and parsers split the tag at its first underscore (passes old and new)"""
    def test_every_tool_has_the_same_pattern(self):
        pats = set()
        files = [os.path.join(INSTALL, KIT, 'tools', n) for n in ('board_line_v2.py', 'queue_job_v14.py', 'decide_v4.py', 'audit_run_v3.py')]
        files += [os.path.join(FIX, KIT, 'tools', n) for n in ('queue_job_v15.py', 'decide_v5.py', 'start_run_v1.py')]
        for p in files:
            m = re.search(r"RUNTAG = re\.compile\((r'[^']+')\)", open(p).read()); self.assertTrue(m, p); pats.add(m.group(1))
        self.assertEqual(pats, {r"r'^([A-Z][A-Z0-9]{0,11})_([0-9]{8})$'"})

    def test_an_underscore_seat_would_be_read_as_another_seat(self):
        it = open(os.path.join(INSTALL, 'Agentic/tree/ALARM_DESIGN/KIT_V6/tools/idea_time_v2.py')).read()
        self.assertIn("tag.split('_')[0]", it)                                             # idea_time_v2 takes SCOUT from SCOUT_R12_20261103
        self.assertIn('_judge_%s_', open(os.path.join(INSTALL, KIT, 'tools/queue_job_v14.py')).read())
        self.assertIn('_judge_SCOUT_', '20267312_judge_SCOUT_R12_TRUE_X.job.sh')         # seat SCOUT would count SCOUT_R12's jobs as its own


# ---------------------------------------------------------------- S3 the TRUE kind
class S3_TrueKind(unittest.TestCase):
    def setUp(self):
        self.w = World(); self.w.plant_run()

    def test_queue_twin_runs_row_and_audit_a16(self):
        r = self.w.q_true('--dry'); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertIn('DRY RUN OK', r.stdout)
        self.assertNotIn('@@', r.stdout)
        r = self.w.q_true(); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = [x for x in self.w.rows('RUNS') if x['kind'] == 'TRUE']; self.assertEqual(len(rows), 1)
        x = rows[0]; twin = os.path.join(self.w.Rn, x['job'])
        self.assertEqual(s16(twin), x['job_sha16']); self.assertEqual(x['from_job'], GRADE); self.assertEqual(x['variants'], 'V1')
        inq = os.path.join(self.w.QU, x['queue'], 'IN', os.path.basename(twin)); self.assertEqual(s16(inq), s16(twin))
        p = subprocess.run(['bash', inq], capture_output=True, text=True); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        rd = os.path.join(self.w.Rn, x['receipts_rel']); st = open(os.path.join(rd, 'STAGES.tsv')).read()
        self.assertRegex(st, r'\ntrue_V1\t0\t'); self.assertRegex(st, r'\nend\t0\t'); self.assertTrue(os.path.isfile(os.path.join(rd, 'TRUE_V1_HLOIFALL/TRUE_ROW.tsv')))
        os.rename(inq, inq + '.ran')
        a = self.w.run_tool('audit', '--settings', self.w.S, RUN); self.assertIn('A16  JOBS        PASS', a.stdout, a.stdout + a.stderr)
        self.assertEqual(self.w.q_true().returncode, 2)                                     # ALREADY TRUE

    def refused(self, text, **claim):
        if claim:
            self.w.write_claim(**claim)
        r = self.w.q_true('--dry'); self.assertEqual(r.returncode, 2, r.stdout); self.assertIn(text, r.stderr)
        self.assertEqual([x for x in self.w.rows('RUNS') if x['kind'] == 'TRUE'], [])

    def test_refuses_a_label_not_on_the_card(self):
        self.refused('TRUE LABEL NOT SEALED', label=dict(LABEL, thr=1.0), mirror=dict(MIRROR, thr=1.0))

    def test_refuses_another_definition(self):
        self.refused('def_sha16 IS', def_sha16='0000000000000000')

    def test_refuses_another_perfire_digest(self):
        self.refused('perfire_sha16', perfire_sha16='0000000000000000')

    def test_refuses_another_lean(self):
        self.refused('lean IS', lean='FOLLOW')

    def test_refuses_a_swept_or_changed_perfire(self):
        wr(self.w.pf, 'x\n', 'a'); self.refused('SOURCE DIGEST')

    def test_refuses_a_grade_whose_seal_is_gone(self):
        g = os.path.join(self.w.Rn, 'receipts', GRADE); os.rename(os.path.join(g, 'PERFIRE_SEAL.tsv'), os.path.join(g, 'SEAL_AWAY')); self.refused('SEAL LOST')

    def test_refuses_a_claim_named_for_another_variant(self):
        r = self.w.q_true(item='V1=ideas/%s/TRUE_V2_X.json' % IDEA); self.assertEqual(r.returncode, 2); self.assertIn('TRUE CLAIM MUST BE', r.stderr)

    def test_the_job_stops_on_a_claim_or_perfire_changed_after_queueing(self):
        for n, target in enumerate(('claim', 'perfire')):
            w = World(); w.plant_run(); r = w.q_true(); self.assertEqual(r.returncode, 0, r.stderr)
            x = [x for x in w.rows('RUNS') if x['kind'] == 'TRUE'][0]; inq = os.path.join(w.QU, x['queue'], 'IN', os.path.basename(x['job']))
            wr(os.path.join(w.Rn, w.claim_rel) if target == 'claim' else w.pf, '\n', 'a')
            p = subprocess.run(['bash', inq], capture_output=True, text=True); self.assertEqual(p.returncode, 3, (target, p.stdout, p.stderr))
            st = open(os.path.join(w.Rn, x['receipts_rel'], 'STAGES.tsv')).read(); self.assertIn('SHA CHANGED', st); self.assertNotIn('true_V1', st)

    def test_a_failed_true_job_may_run_again(self):
        r = self.w.q_true(); self.assertEqual(r.returncode, 0, r.stderr)
        x = [x for x in self.w.rows('RUNS') if x['kind'] == 'TRUE'][0]; inq = os.path.join(self.w.QU, x['queue'], 'IN', os.path.basename(x['job']))
        p = subprocess.run(['bash', inq], capture_output=True, text=True, env=dict(os.environ, TG_FAIL='1')); self.assertEqual(p.returncode, 2)
        os.rename(inq, inq + '.ran'); r = self.w.q_true('--dry'); self.assertEqual(r.returncode, 0, r.stderr)


# ---------------------------------------------------------------- S4 decide without ENTRY
def plant_decide(r, rules, summary='V1\tOK\tPASS\t100'):
    g = os.path.join(r, 'receipts', '1_GRADE_IDEA')
    wr(os.path.join(r, 'registers/VARIANTS.tsv'), 'idea\tV\tlean\nIDEA\tV1\tFADE\n')
    wr(os.path.join(g, 'STAGES.tsv'), 'stage\trc\ngrade_V1\t0\nhandoff\t0\nend\t0\n')
    wr(os.path.join(g, 'HANDOFF/SUMMARY.tsv'), 'V\tstatus\tgate\twaves\n%s\n' % summary)
    wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_RULES_V1.tsv'), 'key\tvalue\n' + ''.join('%s\t%s\n' % kv for kv in rules.items()))
    wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_V1.tsv'), 'horizon\tlead\tt\n15m\t4\t1.8\n1h\t3\t1.5\n')
    wr(os.path.join(g, 'FIRES.tsv'), 'V1\t3000\tabc\t/x/list.tsv\n')


NMM = {'R1': 'PASS', 'R2': 'no', 'counted': '4', 'passing': '3', 'need': '3'}


class S4_DecideWithoutEntry(unittest.TestCase):
    def mods(self, d):
        """decide (old: v4, new: v5) loaded from a copy beside a planted queue file"""
        shutil.copy(os.path.join(INSTALL if OLD else FIX, KIT, 'tools', 'decide_v4.py' if OLD else 'decide_v5.py'), os.path.join(d, 'decide.py'))
        wr(os.path.join(d, 'queue_job_v15.py'), "'RUN_BUDGET_MB': 10000,\n")
        return load(os.path.join(d, 'decide.py'), 'dec_%d' % id(d))

    def test_r1_is_decided_without_entry_money_left_out(self):
        t = tempfile.mkdtemp(prefix='v121D_')
        r = os.path.join(t, 'run'); plant_decide(r, NMM); D = self.mods(t)
        d = D.decide(r, 'IDEA', 'V1', '1_GRADE_IDEA', None)
        self.assertEqual(d['state'], 'NEEDS MORE MONTHS')
        for k in ('clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr'):
            self.assertEqual(d[k], '-', k)
        self.assertIn('money not read', d['note']); self.assertEqual(d['entry_job'], '-')
        plant_decide(r, dict(NMM, R2='PASS')); self.assertEqual(D.decide(r, 'IDEA', 'V1', '1_GRADE_IDEA', None)['state'], 'PASS')
        with self.assertRaises(D.Refused):
            D.decide(r, 'IDEA', 'V1', '1_GRADE_IDEA', '7_GRADE_IDEA')                       # a wrong --entry is still refused

    def test_audit_a6_recomputes_a_row_without_entry(self):
        w = World(); w.plant_run(); g = os.path.join(w.Rn, 'receipts', GRADE)
        wr(os.path.join(g, 'HANDOFF/SUMMARY.tsv'), 'V\tstatus\tgate\twaves\nV1\tOK\tPASS\t100\n')
        wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_RULES_V1.tsv'), 'key\tvalue\n' + ''.join('%s\t%s\n' % kv for kv in NMM.items()))
        wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_V1.tsv'), 'horizon\tlead\tt\n15m\t4\t1.8\n1h\t3\t1.5\n')
        r = w.run_tool('decide', '--settings', w.S, RUN, IDEA, 'V1', '--grade', GRADE, '--write')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertIn('NEEDS MORE MONTHS', r.stdout)
        a = w.run_tool('audit', '--settings', w.S, RUN); self.assertIn('A6   SOURCED     PASS', a.stdout, a.stdout + a.stderr)

    def test_pages_say_entry_is_information_only(self):
        t = page('AGENTS.md'); self.assertNotIn('R1 passed: it asks for the ENTRY job', t); self.assertIn('decide_v5', t)


class KEEP_PassRules(unittest.TestCase):
    """every state that does not need ENTRY is v4's, case by case (passes old and new)"""
    def test_states_equal_v4(self):
        ok = 'V1\tOK\tPASS\t100'
        cases = [(NMM, ok), (dict(NMM, R2='PASS'), ok), (dict(NMM, R1='FAIL'), ok), (dict(NMM, counted='2'), ok), (NMM, 'V1\tOK\tFAIL\t100'), (NMM, 'V1\tBAD\tPASS\t100'),
                 (dict(NMM, R1='FAIL', R2='PASS'), ok)]
        t = tempfile.mkdtemp(prefix='v121K_'); seen = 0
        for n, (rules, summ) in enumerate(cases):
            r = os.path.join(t, 'run%d' % n); plant_decide(r, rules, summ)
            for big in (False, True):
                out = []
                for tool in (os.path.join(INSTALL, KIT, 'tools/decide_v4.py'), os.path.join(FIX, KIT, 'tools/decide_v5.py')):
                    d = tempfile.mkdtemp(dir=t); shutil.copy(tool, os.path.join(d, 'decide.py')); wr(os.path.join(d, 'queue_job_v15.py'), "'RUN_BUDGET_MB': 100,\n")
                    D = load(os.path.join(d, 'decide.py'), 'k_%s' % os.path.basename(d))
                    try:
                        x = D.decide(r, 'IDEA', 'V1', '1_GRADE_IDEA', None, too_big=big); out.append((x['state'], x['r1'], x['r2'], x['months_counted'], x['lead_15m'], x['t_1h']))
                    except D.Refused as e:
                        out.append('REFUSED ' + str(e).split(':')[0])
                if not big and str(out[0]).startswith('REFUSED V1 HAS R1'):
                    self.assertIn(out[1][0], ('NEEDS MORE MONTHS', 'PASS')); continue      # the one change: v5 decides it, from the same hand-off
                self.assertEqual(out[0], out[1], (n, big, out)); seen += 1
        self.assertEqual(seen, 12)


# ---------------------------------------------------------------- S5 the ledger tool
class S5_Ledger(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp(prefix='v121L_'); self.led = os.path.join(self.t, 'TRIES_LEDGER_V1.tsv')
        shutil.copyfile(REAL_LEDGER, self.led)                                            # a copy: the real ledger is only read
        self.setting = os.path.join(self.t, 'setting.md'); wr(self.setting, 'rule\n')
        self.L = load(os.path.join(LEDGER_DIR, 'ledger_add_v5.py') if OLD else os.path.join(FIX, KIT, 'tools/ledger_add_v7.py'), 'led_%d' % id(self))

    def test_prereg_works_on_the_real_ledger(self):
        aid = self.L.prereg('V121TEST', 'test', self.setting, path=self.led)
        self.assertTrue(aid.startswith('PREREG_V121TEST_')); self.assertEqual(self.L.count('V121TEST', path=self.led), 1)
        self.assertEqual(open(REAL_LEDGER, 'rb').read(), open(self.led, 'rb').read()[:os.path.getsize(REAL_LEDGER)])   # appended only

    def test_check_names_the_bad_row_for_its_owner(self):
        if OLD:
            self.fail('ledger_add_v5 has no check; its reader says only "malformed or duplicate ledger row"')
        rc, lines = self.L.check(self.led); self.assertEqual(rc, 3, lines)
        self.assertTrue(any('line 513 repeats ask_id SCOUT-RECUT of line 512' in x for x in lines), lines)

    def test_own_id_repeated_still_refuses(self):
        aid = self.L.prereg('V121TEST', 'test', self.setting, path=self.led)
        line = [l for l in open(self.led) if l.split('\t')[1:2] == [aid]][0]; wr(self.led, line, 'a')
        with self.assertRaises((ValueError, SystemExit)):
            self.L.rows(self.led)

    def test_short_row_refuses_with_its_line(self):
        if OLD:
            self.fail('v5 names no line')
        wr(self.led, '20261103T000000Z\tSHORT\tX\n', 'a')
        with self.assertRaises(self.L.LedgerError) as c:
            self.L.rows(self.led)
        self.assertIn('line 523', str(c.exception)); self.assertEqual(c.exception.code, 'MALFORMED_LEDGER')

    def test_cli_refuses_in_one_line_never_a_traceback(self):
        w = World(); wr(os.path.join(w.R, 'TRIES_LEDGER_V1.tsv'), open(REAL_LEDGER).read())
        if OLD:
            p = subprocess.run([sys.executable, '-B', os.path.join(LEDGER_DIR, 'ledger_add_v5.py'), 'prereg', 'V121TEST', 'test', self.setting], capture_output=True, text=True,
                               env=dict(os.environ, SCOUT_LEDGER=os.path.join(w.R, 'TRIES_LEDGER_V1.tsv')))
            self.assertEqual(p.returncode, 0, p.stderr[-300:]); return
        tool = os.path.join(w.A, KIT, 'tools/ledger_add_v7.py')
        p = subprocess.run([sys.executable, '-B', tool, '--settings', w.S, 'prereg', 'V121TEST', 'test', self.setting], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr); self.assertIn('WARN', p.stderr); self.assertIn('PREREG_V121TEST_', p.stdout)
        aid = p.stdout.split()[0]
        self.assertEqual(subprocess.run([sys.executable, '-B', tool, '--settings', w.S, 'has', aid], capture_output=True).returncode, 0)
        self.assertEqual(subprocess.run([sys.executable, '-B', tool, '--settings', w.S, 'has', 'NOT_RECORDED'], capture_output=True).returncode, 3)
        for args in (['result', aid, '/nonexistent', 'PASS', self.setting], ['result', aid, self.setting, 'GREAT', self.setting], ['door', 'x'], ['prereg', 'X', 'p', '/nonexistent']):
            p = subprocess.run([sys.executable, '-B', tool, '--settings', w.S] + args, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, (args, p.stdout, p.stderr)); self.assertTrue(p.stderr.startswith('REFUSED'), p.stderr); self.assertNotIn('Traceback', p.stderr)
        wr(os.path.join(w.R, 'TRIES_LEDGER_V1.tsv'), 'bad\trow\n', 'a')
        p = subprocess.run([sys.executable, '-B', tool, '--settings', w.S, 'count', 'X'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2); self.assertIn('REFUSED MALFORMED_LEDGER', p.stderr); self.assertNotIn('Traceback', p.stderr)

    def test_v5_suite_on_the_new_tool(self):
        sys.path.insert(0, LEDGER_DIR)
        try:
            SE = load(os.path.join(LEDGER_DIR, 'ledger_strict_env.py'), 'ledger_strict_env'); T5 = load(os.path.join(LEDGER_DIR, 'test_ledger_add_v5.py'), 't5')
            self.assertTrue(all(SE.run_all(self.L)), SE.run_all(self.L)); self.assertTrue(all(T5.run_w(self.L)))
        finally:
            sys.path.remove(LEDGER_DIR)


if __name__ == '__main__':
    unittest.main(verbosity=2)
