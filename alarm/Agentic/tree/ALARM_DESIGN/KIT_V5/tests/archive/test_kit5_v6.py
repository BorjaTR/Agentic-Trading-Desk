"""test_kit5_v6.py (SCOUT, 30 Oct 2026; TEST, NOT REVIEWED): tests of queue_job_v5.py, JOB_COUNT_V6, JOB_CLEAN_V6 and clean_scratch_v2.py:
the KIT_V5 queue and its COUNT and CLEAN jobs run from the Alarm package (CLEAN_RELEASE_V1, task K1). Each test builds a sandbox: an Alarm
package laid out like the install (.../Alarm/alarm/<RELEASE>), holding copies of this package's settings reader and example, the kit's new
files and the register writer, with a stub detect.py and stub tables in 01_Detection's tree; and outside it the data its settings file
names (research root, runner queues, scratch, lab days, board, a fake job number allocator). A filled job runs with bash in the sandbox as
it is, except three things: the scratch disk's free space (df), the sha16 pins of the stub files, and the clock (a planted `date` that says
23:30Z, inside the old quiet window: the owner removed it 30 Oct 2026 23:32 Berlin, so no job may stop or be refused there).
Each refusal test asserts its own message.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_kit5_v6.py     (from an Alarm package; temp folders only, removed after)
"""
import contextlib, datetime, hashlib, importlib.util, io, json, os, re, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT5 = os.path.dirname(HERE)                                                   # <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5
PKG = os.path.normpath(os.path.join(KIT5, '..', '..', '..', '..'))             # <Alarm>
REG = os.path.join(os.path.dirname(KIT5), 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py')
REGS = os.path.join(KIT5, 'runs', 'TEMPLATE_V3', 'registers')              # the KIT_V5 register headers: the run template's own files
HDR = {f[:-4]: open(os.path.join(REGS, f)).readline().rstrip('\n').split('\t') for f in sorted(os.listdir(REGS)) if f.endswith('.tsv')}

KIT = ('Agentic', 'tree', 'ALARM_DESIGN', 'KIT_V5')
DET = ('01_Detection', 'tree')
RUNTAG = 'AD1_20261029'
NOW = datetime.datetime(2026, 10, 29, 14, 0, tzinfo=datetime.timezone.utc)
# JOB_COUNT_V6's pins: the file in 01_Detection's tree -> the sha16 the template pins (the real file's); the sandbox holds stubs instead
PINS = {
    'team/RESEARCH/tools/idea_to_grade/detect_v2.py': '97a822a20e08088d',
    'team/RESEARCH/tools/alarm_design/alarm_design_v3.py': '4852c9c0f8fbf175',
    'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json': 'b93de33b2a73a56e',
    'team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv': '5383a6bfe4d62680',
    'team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv': 'f413906feb40c0b4',
    'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv': 'd133fea9c7935857',
    'team/LAB3/METRICS_HL_ADD_V1.tsv': 'd81727de54e5a5db',
    'team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv': 'f19ccfbf08c9a5b4',
    'team/LAB3/METRICS_V1.tsv': 'c2335f86987c5045',
}
STUB_DETECT = r'''import sys, os, json
a = sys.argv[1:]; out = a[a.index('--out') + 1]; coins = a[a.index('--coins') + 1].split(',')
os.makedirs(out)
json.dump({'argv': a, 'cwd': os.getcwd(), 'python': sys.executable, 'script': os.path.abspath(__file__),
           'env': {k: os.environ.get(k) for k in ('METRICS_V1', 'METRIC_TRAPS', 'CATALOGS')}}, open(os.path.join(out, 'ARGS.json'), 'w'))
rows = []
half_a = 'BTC' in coins
for i in range(40):
    t = 1757462400 + i * 7200 * 7 + (0 if half_a else (1000 if i % 2 == 0 else 3000))
    rows.append('%s\t%d\t1' % (coins[i % len(coins)], t))
open(os.path.join(out, 'EVENTS.tsv'), 'w').write('# stub detect\ncoin\tt\tside\n' + '\n'.join(rows) + '\n')
print('stub detect done', len(rows))
'''
STUB_ALLOC = ('import os, sys\np = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alloc.n")\n'
              'n = int(open(p).read()) if os.path.exists(p) else 20269000\nn += 1\nopen(p, "w").write(str(n))\nprint(n)\n')
SYSTEM = ('/dev/null', '/dev/stderr')
ABS = re.compile(r'(?<![\w.$@)\]/-])/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]*[A-Za-z0-9_-]')     # an absolute path in a job's text


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def w(p, s, mode=0o644):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(s)
    os.chmod(p, mode)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def under(p, root):
    return p == root or p.startswith(root.rstrip(os.sep) + os.sep)


class Base(unittest.TestCase):
    def setUp(self):
        if not os.path.isfile(os.path.join(PKG, '_tools', 'settings_v1.py')):
            raise RuntimeError('run these tests from an Alarm package: no _tools/settings_v1.py at %s' % PKG)
        self.root = os.path.realpath(tempfile.mkdtemp(prefix='k6sim_'))
        self.P = os.path.join(self.root, 'volat_release', 'Alarm', 'alarm', 'R1')     # the sandbox package, laid out like the install
        self.D = os.path.join(self.root, 'data')                                        # its data, outside it
        self.package()
        self.vals = self.data()
        self.settings = self.write_settings(self.vals)
        self.Q = load('queue_job_v5_k6sim', os.path.join(self.P, *KIT, 'tools', 'queue_job_v5.py'))
        self.Q.CFG.update({'free_mb': lambda: 200000, 'now': lambda: NOW})
        self.run = self.new_run(RUNTAG)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def package(self):
        def cp(src, *dst):
            d = os.path.join(self.P, *dst)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copyfile(src, d)
        cp(os.path.join(PKG, '_tools', 'settings_v1.py'), '_tools', 'settings_v1.py')
        cp(os.path.join(PKG, 'settings', 'SETTINGS_EXAMPLE.env'), 'settings', 'SETTINGS_EXAMPLE.env')
        for sub, n in (('tools', 'queue_job_v5.py'), ('tools', 'clean_scratch_v2.py'), ('jobs', 'JOB_COUNT_V6.job.sh.txt'),
                       ('jobs', 'JOB_CLEAN_V6.job.sh.txt')):
            cp(os.path.join(KIT5, sub, n), *(KIT + (sub, n)))
        cp(REG, 'Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py')
        self.shamap = {}
        for rel, real in PINS.items():
            p = os.path.join(self.P, *(DET + tuple(rel.split('/'))))
            body = STUB_DETECT if rel.endswith('.py') else json.dumps({'coins': ['BTC', 'ETH', 'SOL', 'XRP']}) if rel.endswith('.json') else 'stub %s\n' % rel
            w(p, body)
            self.shamap[real] = sha16(p)

    def data(self):
        D = self.D
        v = {'PYTHON': os.path.join(D, 'venv', 'bin', 'python3'), 'LAB_DAYS': os.path.join(D, 'lab_days'), 'SCRATCH': os.path.join(D, 'scratch'),
             'RESEARCH_ROOT': os.path.join(D, 'research'), 'RUNNER_QUEUES': os.path.join(D, 'runner'),
             'RUNNER_ALLOC': os.path.join(D, 'alloc', 'job_alloc.py'), 'BOARD': os.path.join(D, 'hb'),
             'FEED_GATE': os.path.join(D, 'feed', 'stops', 'BACKFILL_GATE.txt')}
        for k in ('LAB_DAYS', 'SCRATCH', 'BOARD'):
            os.makedirs(v[k])
        for i in range(1, 22):
            for s in ('IN', 'RUN'):
                os.makedirs(os.path.join(v['RUNNER_QUEUES'], 'Q_V%d' % i, s))
        w(v['RUNNER_ALLOC'], STUB_ALLOC)
        os.makedirs(os.path.dirname(v['PYTHON']))
        os.symlink(sys.executable, v['PYTHON'])                  # this machine's interpreter, under a name only the settings give
        os.makedirs(os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', 'IDEAS_CLAIMED'))
        return v

    def write_settings(self, vals, extra='', name='SETTINGS_SIM.env'):
        keys = load('settings_v1_k6sim', os.path.join(self.P, '_tools', 'settings_v1.py')).keys()
        p = os.path.join(self.root, name)
        w(p, '# the sandbox machine\n' + ''.join('%s=%s\n' % (k, vals.get(k, '')) for k in keys) + extra)
        return p

    def new_run(self, runtag):
        run = os.path.join(self.vals['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', runtag)
        for n, h in HDR.items():
            w(os.path.join(run, 'registers', n + '.tsv'), '\t'.join(h) + '\n')
        return run

    def claim(self, idea):
        w(os.path.join(self.vals['RESEARCH_ROOT'], 'ALARM_DESIGN', 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUNTAG, idea)), 'claimed\n')

    def count_def(self, idea, v='C1', last='20260531'):
        self.claim(idea)
        d = 'ideas/%s/defs/%s.json' % (idea, v)
        w(os.path.join(self.run, d), json.dumps({'id': v, 'window': {'first': '20250901', 'last': last}}))
        return '%s=%s' % (v, d)

    def reg(self, name, row):
        r = subprocess.run([sys.executable, '-B', REG, self.run, name, '-'], input=json.dumps(row), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def q(self, *a, settings=None):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.Q.main(['--settings', settings or self.settings] + list(a))
        return buf.getvalue()

    def refused(self, args, text, settings=None):
        with self.assertRaises(self.Q.Refused) as cm:
            with contextlib.redirect_stdout(io.StringIO()):
                self.Q.main(['--settings', settings or self.settings] + list(args))
        self.assertIn(text, str(cm.exception))

    def twin(self, out):
        line = [l for l in out.splitlines() if l.startswith('QUEUED')][0]
        return os.path.join(self.run, line.split(' twin ')[1].split(' ')[0])

    def unqueue(self):
        """the fake runner 'finishes' every queued job (moved out of IN), so budgets free up"""
        for i in range(1, 22):
            d = os.path.join(self.vals['RUNNER_QUEUES'], 'Q_V%d' % i, 'IN')
            for f in os.listdir(d):
                os.rename(os.path.join(d, f), os.path.join(self.root, f + '.done'))

    def run_job(self, twin, free_mb='200000', hhmm='2330', scratch=None):
        """bash runs the filled job as it is, except the scratch disk's free space, the pins of the stubs and the clock: a planted `date`
        first on PATH answers <hhmm> to +%H%M (23:30Z by default: the old quiet window, where no job may stop any more)"""
        s = open(twin).read()
        df = 'df -m %s |' % (scratch or self.vals['SCRATCH'])
        self.assertEqual(s.count(df), 1, 'the job reads the free space of SCRATCH, once')
        s = s.replace(df, "printf 'Filesystem\\nx x x %s\\n' |" % free_mb)
        for real, stub in self.shamap.items():
            s = s.replace(' ' + real, ' ' + stub)
        p = os.path.join(self.root, 'sim', os.path.basename(twin) + '.sim.sh')
        w(p, s)
        bin_ = os.path.join(self.root, 'sim', 'bin')
        w(os.path.join(bin_, 'date'), '#!/bin/bash\nfor a in "$@"; do [ "$a" = "+%%H%%M" ] && { echo %s; exit 0; }; done\nexec %s "$@"\n'
          % (hhmm, shutil.which('date')), 0o755)
        env = dict(os.environ, PATH=bin_ + os.pathsep + os.environ.get('PATH', ''))
        return subprocess.run(['bash', p], capture_output=True, text=True, cwd=self.root, stdin=subprocess.DEVNULL, env=env)

    def stray_paths(self, body):
        """absolute paths in a filled job that are neither inside the sandbox package nor under a settings key's data"""
        v = self.vals
        roots = [self.P, v['RESEARCH_ROOT'], v['SCRATCH'], v['LAB_DAYS']] + ([v['FEED_GATE']] if v.get('FEED_GATE') else [])
        return [p for p in ABS.findall(body) if p not in SYSTEM and p != os.path.normpath(v['PYTHON']) and not any(under(p, r) for r in roots)]

    def runner_settings(self, base, release=True):
        """queueing on this machine for another one (the job runner's): its paths live under <base>; returns (--settings, --job-settings,
        the runner's paths). The queue's file is this machine's, with RUNNER_RELEASE = the runner's release when <release>"""
        V = {'PYTHON': os.path.join(base, 'venv', 'bin', 'python3'), 'LAB_DAYS': os.path.join(base, 'lab_days'),
             'SCRATCH': os.path.join(base, 'scratch'), 'RESEARCH_ROOT': os.path.join(base, 'research'),
             'RUNNER_QUEUES': os.path.join(base, 'runner'), 'RUNNER_ALLOC': os.path.join(base, 'alloc', 'job_alloc.py'),
             'BOARD': os.path.join(base, 'hb'), 'RELEASE': os.path.join(base, 'volat_release', 'Alarm', 'alarm', 'current')}
        js = self.write_settings(V, name='SETTINGS_RUNNER.env')
        qs = self.write_settings(dict(self.vals, RUNNER_RELEASE=V['RELEASE']) if release else self.vals, name='SETTINGS_QUEUE.env')
        return qs, js, V

    def runner_machine(self):
        """the runner's machine made real: its release a copy of the package (same bytes, another folder), its research root and scratch
        this machine's folders under the runner's names (one folder, two names, as the VM sees the Mac's), its own lab days and python"""
        qs, js, V = self.runner_settings(os.path.join(self.root, 'runner_machine'))
        shutil.copytree(self.P, V['RELEASE'])
        os.makedirs(V['LAB_DAYS'])
        os.makedirs(os.path.dirname(V['PYTHON']))
        os.symlink(sys.executable, V['PYTHON'])
        os.symlink(self.vals['RESEARCH_ROOT'], V['RESEARCH_ROOT'])
        os.symlink(self.vals['SCRATCH'], V['SCRATCH'])
        return qs, js, V

    def entry_fixture(self, idea='ENTX', gj='20269001_GRADE_ENTX'):
        """a variant P1 whose GRADE job <gj> ended with hand-off R1 PASS: everything an ENTRY plan reads but its fire list"""
        self.claim(idea)
        pr = 'ideas/%s/PREREG_%s.md' % (idea, idea)
        w(os.path.join(self.run, pr), 'prereg\n')
        w(os.path.join(self.run, 'ideas', idea, 'ALARM_CARD.md'), 'card\n')
        d = 'ideas/%s/defs/P1.json' % idea
        w(os.path.join(self.run, d), json.dumps({'id': 'P1', 'window': {'first': '20250901', 'last': '20260531'}}))
        self.reg('VARIANTS', {'idea': idea, 'V': 'P1', 'lean': 'FADE', 'def_rel': d, 'def_sha16': sha16(os.path.join(self.run, d)),
                              'prereg_rel': pr, 'prereg_sha16': sha16(os.path.join(self.run, pr)), 'reason': 'first'})
        gd = os.path.join(self.run, 'receipts', gj)
        w(os.path.join(gd, 'STAGES.tsv'), 'stage\trc\tseconds\tutc\tnote\nend\t0\t0\tu\tx\n')
        w(os.path.join(gd, 'HANDOFF', 'REAL_SEALED', 'REAL_RULES_P1.tsv'), 'key\tvalue\nR1\tPASS\n')
        return idea, gj, gd

    def fire_list_at(self, gd, path):
        w(os.path.join(gd, 'FIRES.tsv'), 'P1\t5042\t0123456789abcdef\t%s\n' % path)

    def snapshot(self):
        out = {}
        for d, ds, fs in os.walk(self.root):
            for x in ds + fs:
                st = os.lstat(os.path.join(d, x))
                out[os.path.join(d, x)] = (st.st_size, st.st_mtime_ns)
        return out


class TestSettings(Base):
    def test_the_settings_file_is_required(self):
        with self.assertRaises(self.Q.Refused) as cm:
            with contextlib.redirect_stdout(io.StringIO()):
                self.Q.main([RUNTAG, 'COUNT', 'CNTX', self.count_def('CNTX')])
        self.assertIn('--settings <file> IS REQUIRED', str(cm.exception))

    def test_the_packages_reader_refuses_a_bad_file(self):
        it = self.count_def('CNTX')
        self.refused([RUNTAG, 'COUNT', 'CNTX', it], 'SETTINGS: UNKNOWN KEYS NOT_A_KEY',
                     settings=self.write_settings(self.vals, extra='NOT_A_KEY=%s\n' % self.D, name='S1.env'))
        self.refused([RUNTAG, 'COUNT', 'CNTX', it], 'SETTINGS: NO SETTINGS FILE', settings=os.path.join(self.root, 'none.env'))
        self.refused([RUNTAG, 'COUNT', 'CNTX', it], 'SETTINGS: DATA INSIDE ALARM SCRATCH',
                     settings=self.write_settings(dict(self.vals, SCRATCH=os.path.join(self.P, 'scratch')), name='S2.env'))

    def test_a_key_the_tool_needs_must_be_set(self):
        it = self.count_def('CNTX')
        for k in ('RUNNER_ALLOC', 'LAB_DAYS'):
            self.refused([RUNTAG, 'COUNT', 'CNTX', it], 'SETTINGS KEY %s IS EMPTY' % k,
                         settings=self.write_settings(dict(self.vals, **{k: ''}), name='S_%s.env' % k))

    def test_a_path_going_into_a_job_line_must_be_plain(self):
        it = self.count_def('CNTX')
        for i, bad in enumerate((';touch_x', ' x', '$(id)')):
            self.refused([RUNTAG, 'COUNT', 'CNTX', it, '--dry'], 'UNSAFE PATH SCRATCH',
                         settings=self.write_settings(dict(self.vals, SCRATCH=self.vals['SCRATCH'] + bad), name='S%d.env' % i))

    def test_code_from_the_package_data_from_the_settings(self):
        Q, v = self.Q, self.vals
        self.assertEqual(Q.ALARM, self.P)
        self.assertEqual(Q.CFG['KIT'], os.path.join(self.P, *KIT))
        self.assertEqual(Q.CFG['REG'], os.path.join(self.P, 'Agentic', 'tree', 'ALARM_DESIGN', 'runs', 'CLAUDE1_20261028', 'tools', 'reg_append_v1.py'))
        paths = Q.use_settings(self.settings)
        self.assertEqual(paths, {'@@ALARM@@': self.P, '@@PYTHON@@': os.path.normpath(v['PYTHON']), '@@RESEARCH_ROOT@@': v['RESEARCH_ROOT'],
                                 '@@SCRATCH@@': v['SCRATCH'], '@@LAB_DAYS@@': v['LAB_DAYS'], '@@FEED_GATE@@': v['FEED_GATE']})
        self.assertEqual((Q.CFG['H'], Q.CFG['RUNNER'], Q.CFG['WDB'], Q.CFG['JOB_SCRATCH'], Q.CFG['ALLOC'][-1]),
                         (os.path.join(v['RESEARCH_ROOT'], 'ALARM_DESIGN'), v['RUNNER_QUEUES'], v['SCRATCH'], v['SCRATCH'], v['RUNNER_ALLOC']))


class TestShipped(unittest.TestCase):
    def test_the_kit_pins_its_own_files(self):
        Q = load('queue_job_v5_shipped', os.path.join(KIT5, 'tools', 'queue_job_v5.py'))
        self.assertEqual(sorted(Q.TEMPLATE_SHA), ['CLEAN', 'COUNT', 'ENTRY', 'GRADE', 'MONTH'])
        self.assertEqual(sorted(Q.TEMPLATE_NAME), sorted(Q.TEMPLATE_SHA))
        self.assertEqual(Q.TEMPLATE_NAME['GRADE'], 'JOB_GRADE_V7.job.sh.txt')          # round 7: the V6 GRADE was refused (SCOUT K12)
        self.assertEqual(Q.TEMPLATE_NAME['MONTH'], 'JOB_MONTH_V7.job.sh.txt')          # and the V6 MONTH, with the same old grader
        for k in ('COUNT', 'CLEAN', 'GRADE', 'MONTH', 'ENTRY'):
            self.assertEqual(Q.TEMPLATE_SHA[k], sha16(os.path.join(KIT5, 'jobs', Q.TEMPLATE_NAME[k])), k)
        self.assertEqual(Q.CFG['REG_SHA'], sha16(REG))
        clean = open(os.path.join(KIT5, 'jobs', 'JOB_CLEAN_V6.job.sh.txt')).read()
        self.assertIn('ck $K5/tools/clean_scratch_v2.py %s\n' % sha16(os.path.join(KIT5, 'tools', 'clean_scratch_v2.py')), clean)
        count = open(os.path.join(KIT5, 'jobs', 'JOB_COUNT_V6.job.sh.txt')).read()
        self.assertEqual(len(re.findall(r'\bck \S+ [0-9a-f]{16}\b', count)), len(PINS))
        for real in PINS.values():
            self.assertEqual(count.count(' %s' % real), 1, real)

    def test_the_new_files_name_no_machine_path(self):
        MP = load('machine_paths_v2_k6', os.path.join(PKG, '_tools', 'machine_paths_v2.py'))
        files = [os.path.join(KIT5, 'tools', 'queue_job_v5.py'), os.path.join(KIT5, 'tools', 'clean_scratch_v2.py'),
                 os.path.join(KIT5, 'jobs', 'JOB_COUNT_V6.job.sh.txt'), os.path.join(KIT5, 'jobs', 'JOB_CLEAN_V6.job.sh.txt'),
                 os.path.join(HERE, 'test_kit5_v6.py'), os.path.join(HERE, 'mutants_v6.py')]
        self.assertEqual([(os.path.basename(f),) + r for f in files for r in MP.file_rows(f) if r[2] == 'CODE'], [])


class TestKinds(Base):
    def test_a_kind_without_a_template_pin_is_not_clean_yet(self):
        keep = self.Q.TEMPLATE_SHA.pop('ENTRY')                  # every kind has a V6 template now (ENTRY: SCOUT K6, 31 Oct)
        try:
            self.refused([RUNTAG, 'ENTRY', 'FLOWX', 'V1', '--from-job', '20269001_GRADE_FLOWX'], 'NOT CLEAN YET: ENTRY')
        finally:
            self.Q.TEMPLATE_SHA['ENTRY'] = keep

    def test_an_entry_fire_list_must_lie_in_its_grade_jobs_scratch(self):
        Q = self.Q
        Q.use_settings(self.settings)
        idea, gj, gd = self.entry_fixture()
        inside = os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, gj, 'P1_FIRES_V1_LIST.tsv')
        self.fire_list_at(gd, inside)
        self.assertIn('SRCS=(%s)' % inside, Q.plan(self.run, 'ENTRY', idea, 'P1', gj)[2])
        for elsewhere in (os.path.join(self.vals['LAB_DAYS'], 'work_%s' % RUNTAG, gj, 'P1_FIRES_V1_LIST.tsv'),
                          os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, gj + 'X', 'P1_FIRES_V1_LIST.tsv')):
            self.fire_list_at(gd, elsewhere)
            with self.assertRaises(Q.Refused) as cm:
                Q.plan(self.run, 'ENTRY', idea, 'P1', gj)
            self.assertIn('FIRE LIST OUTSIDE THE GRADE JOB', str(cm.exception))


class TestCount(Base):
    def test_a_dry_run_claims_and_writes_nothing(self):
        it = self.count_def('CNTX')
        old, tempfile.tempdir = tempfile.tempdir, os.path.join(self.root, 'tmp')
        os.makedirs(tempfile.tempdir)
        before = self.snapshot()
        try:
            out = self.q(RUNTAG, 'COUNT', 'CNTX', it, '--dry')
        finally:
            tempfile.tempdir = old
        self.assertIn('DRY RUN OK: %s COUNT CNTX C1 on Q_V1; WRITES_MB 300' % RUNTAG, out)
        self.assertNotIn('@@', out)
        self.assertEqual(self.stray_paths(out), [])
        self.assertEqual(self.snapshot(), before)

    def test_the_filled_job_names_code_in_the_package_and_data_under_the_keys(self):
        v = self.vals
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'CNTX', self.count_def('CNTX')))
        body = open(tw).read()
        self.assertNotIn('@@', body)
        self.assertIn('\nAL=%s; F=$AL/01_Detection/tree; R=$F/team/RESEARCH; PY=%s\n' % (self.P, os.path.normpath(v['PYTHON'])), body)
        self.assertIn('\nRD=%s/ALARM_DESIGN/runs/%s; ' % (v['RESEARCH_ROOT'], RUNTAG), body)
        self.assertIn(' W=%s/work_%s/$J; ' % (v['SCRATCH'], RUNTAG), body)
        self.assertIn(' --lab-root %s --gate=%s --out ' % (v['LAB_DAYS'], v['FEED_GATE']), body)
        self.assertIn('\ncd $AL\n', body)
        self.assertIn('\nexport METRICS_V1=$F/team/LAB3/METRICS_V1.tsv METRIC_TRAPS=', body)
        head = body.split('\n')[1]
        self.assertTrue(head.startswith('# WRITES %s/work_%s/' % (v['SCRATCH'], RUNTAG)), head)
        self.assertIn(' and %s/ALARM_DESIGN/runs/%s/receipts/' % (v['RESEARCH_ROOT'], RUNTAG), head)
        self.assertEqual(self.stray_paths(body), [])
        self.assertEqual(sha16(os.path.join(v['RUNNER_QUEUES'], 'Q_V1', 'IN', os.path.basename(tw))), sha16(tw))
        runs = open(os.path.join(self.run, 'registers', 'RUNS.tsv')).read().splitlines()
        self.assertEqual(len(runs), 2)
        self.assertIn('\tCOUNT\tCNTX\tC1\tQ_V1\t', runs[1])
        self.assertIn('\t%s\t' % self.Q.TEMPLATE_SHA['COUNT'], runs[1])
        n = os.path.basename(tw).split('_')[0]
        self.assertEqual(open(os.path.join(os.path.dirname(v['RUNNER_ALLOC']), 'alloc.n')).read(), n)    # the allocator the settings name

    def test_the_feed_gate_comes_from_the_job_settings(self):
        # an empty FEED_GATE is no gate (detect_v2 --gate=); a gate path must be plain like every job path
        subs = self.Q.use_settings(self.write_settings(dict(self.vals, FEED_GATE=''), name='S_NOGATE.env'))
        self.assertEqual(subs['@@FEED_GATE@@'], '')
        self.assertEqual(self.Q.use_settings(self.settings)['@@FEED_GATE@@'], self.vals['FEED_GATE'])
        with self.assertRaises(self.Q.Refused):
            self.Q.use_settings(self.write_settings(dict(self.vals, FEED_GATE=self.vals['FEED_GATE'] + ' x'), name='S_BADGATE.env'))

    def test_the_count_job_runs_detect_from_the_package(self):
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'CNTX', self.count_def('CNTX')))
        r = self.run_job(tw)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        J = os.path.basename(tw).split('_')[0] + '_COUNT_CNTX'
        dv = os.path.join(self.run, 'receipts', J)
        st = open(os.path.join(dv, 'STAGES.tsv')).read()
        self.assertIn('count_C1\t0', st)
        self.assertIn('\nend\t0', st)
        self.assertNotIn('quiet', st)                # run at a planted 23:30Z: no job stops in the old quiet window
        c = open(os.path.join(dv, 'COUNT_C1.tsv')).read()
        self.assertIn('ALL\t80\t60\t', c)          # 40 stub fires a half; B 1000 s after A (same wave) or 3000 s (new wave)
        self.assertIn('KIT_V5 JOB_COUNT_V6', c)
        self.assertTrue(os.path.isfile(os.path.join(dv, 'SHA16.txt')))
        det = os.path.join(self.P, *DET)
        for hv in ('A', 'B'):
            a = json.load(open(os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, J, 'det_C1_%s' % hv, 'ARGS.json')))
            self.assertEqual(a['argv'][a['argv'].index('--lab-root') + 1], self.vals['LAB_DAYS'])
            self.assertIn('--gate=%s' % self.vals['FEED_GATE'], a['argv'])                  # the runner's feed gate (FEED_GATE)
            self.assertEqual(a['cwd'], self.P)
            self.assertEqual(a['python'], self.vals['PYTHON'])
            self.assertEqual(a['script'], os.path.join(det, 'team', 'RESEARCH', 'tools', 'idea_to_grade', 'detect_v2.py'))
            tables = [a['env']['METRICS_V1'], a['env']['METRIC_TRAPS']] + a['env']['CATALOGS'].split(':')
            self.assertEqual(len(tables), 6)
            self.assertEqual([x for x in tables if not (under(x, det) and os.path.isfile(x))], [])

    def test_a_changed_table_stops_the_job(self):
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'PINX', self.count_def('PINX')))
        p = os.path.join(self.P, *(DET + ('team', 'OUTSIDE', 'COORD', 'development', 'DEV2', 'a02p_chain_v1', 'full_population', 'ROSTER_BUILD.json')))
        w(p, json.dumps({'coins': ['BTC']}))
        r = self.run_job(tw)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        st = open(os.path.join(self.run, 'receipts', os.path.basename(tw).split('_')[0] + '_COUNT_PINX', 'STAGES.tsv')).read()
        self.assertIn('SHA CHANGED %s' % p, st)

    def test_disk_floor_in_the_job_and_no_quiet_window(self):
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'DSKX', self.count_def('DSKX')))
        r = self.run_job(tw, free_mb='50000')
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        st = open(os.path.join(self.run, 'receipts', os.path.basename(tw).split('_')[0] + '_COUNT_DSKX', 'STAGES.tsv')).read()
        self.assertIn('disk_C1\t7', st)
        self.assertIn('under 60000: stopped', st)
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'QUIX', self.count_def('QUIX')))
        self.assertNotIn('QUIET', open(tw).read())
        r = self.run_job(tw, hhmm='0010')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        st = open(os.path.join(self.run, 'receipts', os.path.basename(tw).split('_')[0] + '_COUNT_QUIX', 'STAGES.tsv')).read()
        self.assertIn('count_C1\t0', st)
        self.assertNotIn('quiet', st)

    def test_the_install_path_is_no_command_but_a_word_in_the_job_is(self):
        self.assertIn(os.sep + 'alarm' + os.sep, self.P)          # laid out like the install: .../Alarm/alarm/<RELEASE>
        it = self.count_def('WRDX')
        self.assertIn('DRY RUN OK', self.q(RUNTAG, 'COUNT', 'WRDX', it, '--dry'))
        tpl = os.path.join(self.P, *(KIT + ('jobs', 'JOB_COUNT_V6.job.sh.txt')))
        s = open(tpl).read()
        for word in ('sleep', 'rm'):
            w(tpl, s.replace('set -u\n', 'set -u\n%s x\n' % word, 1))
            self.Q.TEMPLATE_SHA['COUNT'] = sha16(tpl)
            self.refused([RUNTAG, 'COUNT', 'WRDX', it, '--dry'], 'REFUSED WORD %r' % word)

    def test_the_template_and_the_register_writer_come_from_the_package_pinned(self):
        it = self.count_def('TPLX')
        tpl = os.path.join(self.P, *(KIT + ('jobs', 'JOB_COUNT_V6.job.sh.txt')))
        keep = self.Q.TEMPLATE_SHA['COUNT']
        self.Q.TEMPLATE_SHA['COUNT'] = '0' * 16
        self.refused([RUNTAG, 'COUNT', 'TPLX', it, '--dry'], 'TEMPLATE CHANGED %s' % tpl)
        self.Q.TEMPLATE_SHA['COUNT'] = keep
        reg = self.Q.CFG['REG']
        with open(reg, 'a') as f:
            f.write('# changed\n')
        self.refused([RUNTAG, 'COUNT', 'TPLX', it, '--dry'], 'reg_append_v1.py MISSING OR CHANGED %s' % reg)
        s = open(tpl).read()
        w(tpl, s.replace('set -u\n', 'set -u\n# @@NOPE@@\n', 1))
        self.Q.TEMPLATE_SHA['COUNT'] = sha16(tpl)
        self.Q.CFG['REG_SHA'] = sha16(reg)
        self.refused([RUNTAG, 'COUNT', 'TPLX', it, '--dry'], "PLACEHOLDERS LEFT ['@@NOPE@@']")


class TestV4ChecksKept(Base):
    def test_claim_window_and_disk(self):
        self.refused([RUNTAG, 'COUNT', 'NOPE', 'C1=ideas/NOPE/defs/C1.json'], 'IDEA NOT CLAIMED')
        self.refused([RUNTAG, 'COUNT', 'WINX', self.count_def('WINX', last='20251231')], 'DEFINITION WINDOW OF C1')
        it = self.count_def('QWX')
        self.Q.CFG['free_mb'] = lambda: 60200
        self.refused([RUNTAG, 'COUNT', 'QWX', it], 'DISK: SCRATCH_DISK free 60200 MB')

    def test_job_budget_and_busy_queue(self):
        w(os.path.join(self.vals['RUNNER_QUEUES'], 'Q_V1', 'RUN', '20260001_judge_DSK_x.job.sh'), '# other\n')
        self.assertIn('QUEUED Q_V2', self.q(RUNTAG, 'COUNT', 'AAA', self.count_def('AAA')))
        self.assertIn('QUEUED Q_V3', self.q(RUNTAG, 'COUNT', 'BBB', self.count_def('BBB')))
        self.refused([RUNTAG, 'COUNT', 'CCC', self.count_def('CCC')], 'JOB BUDGET')

    def test_a_failed_runs_row_queues_nothing(self):
        it = self.count_def('RUNX')
        w(os.path.join(self.run, 'registers', 'RUNS.tsv'), 'bad\theader\n')
        self.refused([RUNTAG, 'COUNT', 'RUNX', it], 'RUNS ROW FAILED, NOTHING QUEUED')
        self.assertEqual(os.listdir(os.path.join(self.vals['RUNNER_QUEUES'], 'Q_V1', 'IN')), [])

    def test_free_space_is_read_on_the_scratch_key(self):
        it = self.count_def('NOWDB')
        p = self.write_settings(dict(self.vals, SCRATCH=os.path.join(self.D, 'no_scratch')), name='S_noscratch.env')
        self.Q.CFG['free_mb'] = None
        out = self.q(RUNTAG, 'COUNT', 'NOWDB', it, '--dry', settings=p)
        self.assertIn('SCRATCH_DISK is not visible here', out)
        self.assertIn('DRY RUN OK', out)


class TestRunnerMachine(Base):
    """queueing on this machine (the VM) for the job runner's (the Mac): --job-settings and RUNNER_RELEASE (SCOUT 30 Oct 22:2xZ)"""

    def test_the_queue_reads_this_machine_and_fills_the_job_with_the_runners_paths(self):
        qs, js, V = self.runner_settings(os.path.join(self.root, 'not_here'))       # the runner's paths do not exist on this machine
        out = self.q(RUNTAG, 'COUNT', 'RUNX', self.count_def('RUNX'), '--job-settings', js, settings=qs)
        tw = self.twin(out)
        body = open(tw).read()
        self.assertIn('\nAL=%s; F=$AL/01_Detection/tree; R=$F/team/RESEARCH; PY=%s\n' % (V['RELEASE'], V['PYTHON']), body)
        self.assertIn('\nRD=%s/ALARM_DESIGN/runs/%s; ' % (V['RESEARCH_ROOT'], RUNTAG), body)
        self.assertIn(' W=%s/work_%s/$J; ' % (V['SCRATCH'], RUNTAG), body)
        self.assertIn('df -m %s |' % V['SCRATCH'], body)
        self.assertIn(' --lab-root %s --gate=%s --out ' % (V['LAB_DAYS'], V.get('FEED_GATE', '')), body)       # the runner's gate
        roots = [V['RELEASE'], V['RESEARCH_ROOT'], V['SCRATCH'], V['LAB_DAYS']]
        self.assertEqual([p for p in ABS.findall(body) if p not in SYSTEM and p != V['PYTHON'] and not any(under(p, r) for r in roots)], [])
        for k in ('RESEARCH_ROOT', 'SCRATCH', 'LAB_DAYS', 'PYTHON'):
            self.assertNotIn(self.vals[k], body, k)                                 # no path of the queueing machine in the job
        self.assertNotIn(self.P, body)
        self.assertEqual(sha16(os.path.join(self.vals['RUNNER_QUEUES'], 'Q_V1', 'IN', os.path.basename(tw))), sha16(tw))
        self.assertEqual(open(os.path.join(os.path.dirname(self.vals['RUNNER_ALLOC']), 'alloc.n')).read(), os.path.basename(tw).split('_')[0])

    def test_a_job_queued_for_the_runner_runs_there(self):
        qs, js, V = self.runner_machine()
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'RUNY', self.count_def('RUNY'), '--job-settings', js, settings=qs))
        r = self.run_job(tw, scratch=V['SCRATCH'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        J = os.path.basename(tw).split('_')[0] + '_COUNT_RUNY'
        self.assertIn('ALL\t80\t60\t', open(os.path.join(self.run, 'receipts', J, 'COUNT_C1.tsv')).read())
        rel = os.path.join(V['RELEASE'], *DET)
        for hv in ('A', 'B'):
            a = json.load(open(os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, J, 'det_C1_%s' % hv, 'ARGS.json')))
            self.assertEqual((a['cwd'], a['python']), (V['RELEASE'], V['PYTHON']))
            self.assertEqual(a['argv'][a['argv'].index('--lab-root') + 1], V['LAB_DAYS'])
            self.assertEqual(a['script'], os.path.join(rel, 'team', 'RESEARCH', 'tools', 'idea_to_grade', 'detect_v2.py'))
            tables = [a['env']['METRICS_V1'], a['env']['METRIC_TRAPS']] + a['env']['CATALOGS'].split(':')
            self.assertEqual([x for x in tables if not under(x, rel)], [])
        self.unqueue()
        self.reg('POSTMORTEMS', {'idea': 'RUNY', 'V': 'C1', 'job': J, 'scope': 'X', 'forecast': 'f', 'result': 'r', 'result_file': 'x',
                                 'result_sha16': 'x', 'why': 'w', 'unexplained': 'none'})
        tc = self.twin(self.q(RUNTAG, 'CLEAN', 'RUNY', J, '--job-settings', js, settings=qs))
        body = open(tc).read()
        self.assertIn('\nAL=%s; PY=%s\n' % (V['RELEASE'], V['PYTHON']), body)
        self.assertEqual(body.count(' --scratch %s --' % V['SCRATCH']), 2)
        r = self.run_job(tc, scratch=V['SCRATCH'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, J)))

    def test_runner_release_is_read_from_this_machines_settings_only(self):
        qs, js, V = self.runner_settings(os.path.join(self.root, 'not_here'), release=False)
        js = self.write_settings(dict(V, RUNNER_RELEASE=V['RELEASE']), name='SETTINGS_RUNNER_WITH_RELEASE.env')
        out = self.q(RUNTAG, 'COUNT', 'RELX', self.count_def('RELX'), '--job-settings', js, '--dry', settings=qs)
        self.assertIn('\nAL=%s; ' % self.P, out)                                  # empty here: the queue's own Alarm folder
        self.assertNotIn(V['RELEASE'], out)

    def test_each_file_gives_the_keys_it_must(self):
        qs, js, V = self.runner_settings(os.path.join(self.root, 'not_here'))
        it = self.count_def('KEYX')
        self.refused([RUNTAG, 'COUNT', 'KEYX', it, '--dry', '--job-settings', os.path.join(self.root, 'none.env')], 'JOB SETTINGS: NO SETTINGS FILE', settings=qs)
        for k in ('PYTHON', 'SCRATCH'):
            bad = self.write_settings(dict(V, **{k: ''}), name='SETTINGS_RUNNER_NO_%s.env' % k)
            self.refused([RUNTAG, 'COUNT', 'KEYX', it, '--dry', '--job-settings', bad], 'JOB SETTINGS KEY %s IS EMPTY' % k, settings=qs)
        lean = self.write_settings(dict(self.vals, RUNNER_RELEASE=V['RELEASE'], PYTHON='', LAB_DAYS=''), name='SETTINGS_QUEUE_LEAN.env')
        self.assertIn('DRY RUN OK', self.q(RUNTAG, 'COUNT', 'KEYX', it, '--dry', '--job-settings', js, settings=lean))
        self.refused([RUNTAG, 'COUNT', 'KEYX', it, '--dry'], 'SETTINGS KEY PYTHON IS EMPTY', settings=lean)
        spaced = self.write_settings(dict(self.vals, RUNNER_RELEASE=V['RELEASE'] + ' x'), name='SETTINGS_QUEUE_SPACED.env')
        self.refused([RUNTAG, 'COUNT', 'KEYX', it, '--dry', '--job-settings', js], 'UNSAFE PATH ALARM', settings=spaced)

    def test_an_entry_fire_list_must_lie_in_the_runners_scratch(self):
        qs, js, V = self.runner_settings(os.path.join(self.root, 'not_here'))
        self.Q.use_settings(qs, js)
        idea, gj, gd = self.entry_fixture()
        runners = os.path.join(V['SCRATCH'], 'work_%s' % RUNTAG, gj, 'P1_FIRES_V1_LIST.tsv')
        self.fire_list_at(gd, runners)
        self.assertIn('SRCS=(%s)' % runners, self.Q.plan(self.run, 'ENTRY', idea, 'P1', gj)[2])
        self.fire_list_at(gd, os.path.join(self.vals['SCRATCH'], 'work_%s' % RUNTAG, gj, 'P1_FIRES_V1_LIST.tsv'))
        with self.assertRaises(self.Q.Refused) as cm:
            self.Q.plan(self.run, 'ENTRY', idea, 'P1', gj)
        self.assertIn('FIRE LIST OUTSIDE THE GRADE JOB', str(cm.exception))

    def test_free_space_is_read_on_this_machines_scratch(self):
        qs = self.write_settings(dict(self.vals, SCRATCH=os.path.join(self.D, 'no_scratch')), name='SETTINGS_QUEUE_NOSCRATCH.env')
        self.Q.CFG['free_mb'] = None
        out = self.q(RUNTAG, 'COUNT', 'FREX', self.count_def('FREX'), '--dry', '--job-settings', self.settings, settings=qs)
        self.assertIn('SCRATCH_DISK is not visible here', out)
        self.assertIn(' W=%s/work_%s/$J; ' % (self.vals['SCRATCH'], RUNTAG), out)
        self.assertIn('DRY RUN OK', out)


class TestNoQuietWindow(Base):
    """the owner 30 Oct 2026 23:31-23:32 Berlin: "All jobs can be queued. Please do not stop queueing jobs": the quiet window is removed"""

    def test_jobs_are_queued_in_the_old_quiet_window(self):
        one = self.count_def('QWX')
        three = ','.join(self.count_def('QWY', v) for v in ('C1', 'C2', 'C3'))            # 30 declared minutes
        for (hh, mm), idea, items in (((23, 30), 'QWX', one), ((0, 10), 'QWX', one), ((23, 20), 'QWY', three), ((23, 5), 'QWY', three)):
            self.Q.CFG['now'] = lambda hh=hh, mm=mm: datetime.datetime(2026, 10, 29, hh, mm, tzinfo=datetime.timezone.utc)
            out = self.q(RUNTAG, 'COUNT', idea, items)
            self.assertIn('QUEUED Q_V1', out, (hh, mm))
            self.assertNotIn('QUIET', open(self.twin(out)).read())
            self.unqueue()


class TestClean(Base):
    def test_the_clean_job_removes_the_scratch_under_the_key(self):
        v = self.vals
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'CLNX', self.count_def('CLNX')))
        r = self.run_job(tw)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cj = os.path.basename(tw).split('_')[0] + '_COUNT_CLNX'
        W = os.path.join(v['SCRATCH'], 'work_%s' % RUNTAG, cj)
        self.assertTrue(os.path.isdir(W))
        self.refused([RUNTAG, 'CLEAN', 'CLNX', cj], 'IS STILL QUEUED OR RUNNING')
        self.unqueue()
        self.refused([RUNTAG, 'CLEAN', 'CLNX', cj], 'NO POSTMORTEMS ROW NAMES IT')
        self.reg('POSTMORTEMS', {'idea': 'CLNX', 'V': 'C1', 'job': cj, 'scope': 'X', 'forecast': 'f', 'result': 'r', 'result_file': 'x',
                                 'result_sha16': 'x', 'why': 'w', 'unexplained': 'none'})
        tc = self.twin(self.q(RUNTAG, 'CLEAN', 'CLNX', cj))
        body = open(tc).read()
        self.assertIn('\nAL=%s; PY=%s\n' % (self.P, os.path.normpath(v['PYTHON'])), body)
        self.assertIn(' K5=$AL/Agentic/tree/ALARM_DESIGN/KIT_V5; ', body)
        self.assertEqual(body.count(' --scratch %s --' % v['SCRATCH']), 2)
        self.assertEqual(self.stray_paths(body), [])
        r = self.run_job(tc)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse(os.path.exists(W))
        k = os.path.basename(tc).split('_')[0] + '_CLEAN_CLNX'
        cl = open(os.path.join(self.run, 'receipts', k, 'CLEANED.tsv')).read()
        self.assertIn('\t%s\t' % W, cl)
        self.assertIn('\tREMOVED\n', cl)
        self.assertTrue(os.path.isfile(os.path.join(self.run, 'receipts', cj, 'CLEANED_BY.txt')))
        self.unqueue()
        self.refused([RUNTAG, 'CLEAN', 'CLNX', cj], 'IS ALREADY CLEANED')


class TestCleanScratchV2(Base):
    def setUp(self):
        super().setUp()
        self.C = load('clean_scratch_v2_k6sim', os.path.join(self.P, *(KIT + ('tools', 'clean_scratch_v2.py'))))
        self.S = self.vals['SCRATCH']

    def done(self, j, scratch=True):
        d = os.path.join(self.run, 'receipts', j)
        w(os.path.join(d, 'STAGES.tsv'), 'stage\trc\tseconds\tutc\tnote\nend\t0\t0\tu\tx\n')
        w(os.path.join(d, 'SHA16.txt'), 'x\n')
        Wd = os.path.join(self.S, 'work_%s' % RUNTAG, j)
        if scratch:
            w(os.path.join(Wd, 'x.tsv'), 'x\n')
        return d, Wd

    def cs(self, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.C.main(list(a))
        return buf.getvalue()

    def test_entry_store_places_under_scratch_are_left_for_dsk(self):
        j = '20269001_ENTRY_FLOWX'
        d, Wd = self.done(j)
        chain = os.path.join(self.S, 'work_TOOLTRIAL', 'chain', 'ALM_AD1_P1_SD_20250910_20251231_STAMP1')
        full = os.path.join(self.S, 'work_ALARMLIB', 'i2g_v3_2', 'full_ALM_AD1_P1_SD_20250910_20251231_STAMP1')
        os.makedirs(chain)
        os.makedirs(os.path.join(full, 'run'))
        w(os.path.join(d, 'P1', 'STORE_PLACES.tsv'), 'P1\t%s\nrun\t%s\n' % (chain, os.path.join(full, 'run')))
        out = os.path.join(self.run, 'receipts', '20269002_CLEAN_FLOWX')
        self.assertIn('WOULD REMOVE %s ' % Wd, self.cs(self.run, 'AD1', out, j, '--scratch', self.S, '--dry'))
        self.assertTrue(os.path.isdir(Wd))
        self.cs(self.run, 'AD1', out, j, '--scratch', self.S, '--apply')
        self.assertFalse(os.path.exists(Wd))
        self.assertTrue(os.path.isdir(chain) and os.path.isdir(full))
        cl = open(os.path.join(out, 'CLEANED.tsv')).read()
        self.assertIn('\t%s\t' % chain, cl)
        self.assertIn('\t%s\t' % full, cl)
        self.assertEqual(cl.count('LEFT FOR DSK'), 2)

    def test_a_store_place_not_ours_is_refused(self):
        j = '20269001_ENTRY_FLOWX'
        d, Wd = self.done(j)
        chain = os.path.join(self.S, 'work_TOOLTRIAL', 'chain', 'ALM_DSK_P1_SD_20250910_20251231_STAMP1')
        os.makedirs(chain)
        w(os.path.join(d, 'P1', 'STORE_PLACES.tsv'), 'P1\t%s\n' % chain)
        with self.assertRaises(self.C.Refused) as cm:
            self.cs(self.run, 'AD1', os.path.join(self.root, 'out'), j, '--scratch', self.S, '--apply')
        self.assertIn('STORE PLACE NOT OURS', str(cm.exception))
        self.assertTrue(os.path.isdir(Wd))

    def test_a_job_scratch_that_leaves_the_scratch_folder_is_refused(self):
        j = '20269001_COUNT_FLOWX'
        d, Wd = self.done(j, scratch=False)
        outside = os.path.join(self.root, 'elsewhere')
        os.makedirs(outside)
        os.makedirs(os.path.dirname(Wd))
        os.symlink(outside, Wd)
        with self.assertRaises(self.C.Refused) as cm:
            self.cs(self.run, 'AD1', os.path.join(self.root, 'out'), j, '--scratch', self.S, '--apply')
        self.assertIn('SYMLINK OR RESOLVES OUTSIDE THE SCRATCH FOLDER %s' % self.S, str(cm.exception))
        self.assertTrue(os.path.isdir(outside))

    def test_the_scratch_folder_is_an_argument(self):
        for a in (('--dry',), ('--dry', '--scratch')):
            with self.assertRaises(self.C.Refused) as cm:
                self.cs(self.run, 'AD1', os.path.join(self.root, 'out'), '20269001_COUNT_FLOWX', *a)
            self.assertIn('USAGE', str(cm.exception))


if __name__ == '__main__':
    r = unittest.main(exit=False, verbosity=1).result
    print('TESTS %d, failures %d, errors %d' % (r.testsRun, len(r.failures), len(r.errors)))
    sys.exit(0 if r.wasSuccessful() else 1)
