#!/usr/bin/env python3
"""test_firstlook_v1.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK; TEST, NOT REVIEWED): queue_job_v14's KIND FIRSTLOOK, JOB_FIRSTLOOK_V1, fl_lists_v3, fl_receipt_v1 and the
new editions. Seconds, planted worlds, stub tools for the heavy steps; the real chain is the playground job. ALARM_BASE = the installed Alarm (default: this package when it
holds _tools, else ~/volat_release/Alarm/alarm/current).   python3 -B test_firstlook_v1.py"""
import csv, hashlib, json, os, re, shutil, subprocess, sys, tempfile, unittest

H = os.path.dirname(os.path.abspath(__file__)); PKG = os.environ.get('FL_PKG') or os.path.normpath(os.path.join(H, '..', '..', '..', '..', '..'))
BASE = os.environ.get('ALARM_BASE') or (PKG if os.path.isfile(os.path.join(PKG, '_tools', 'settings_v1.py')) else os.path.expanduser('~/volat_release/Alarm/alarm/current'))
KIT = 'Agentic/tree/ALARM_DESIGN/KIT_V5'; RUNT = 'Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools'; FLD = '06_First_look/tree/tools/alarm_first_look'
Q14 = os.path.join(PKG, KIT, 'tools/queue_job_v14.py'); TPL = os.path.join(PKG, KIT, 'jobs/JOB_FIRSTLOOK_V1.job.sh.txt')
LISTS = os.path.join(PKG, FLD, 'fl_lists_v3.py'); REC = os.path.join(PKG, FLD, 'fl_receipt_v1.py'); SETT = os.path.join(PKG, '06_First_look/FIRSTLOOK_SETTINGS_V1.json')
RUN = 'AB1_20261102'; IDEA = 'TESTIDEA'; GRADE = '20260001_GRADE_' + IDEA; MONTH = '20260002_MONTH_' + IDEA
GOOD = [('grade_V1', 0), ('perfire_V1', 0), ('perfire_test_V1', 0), ('perfire_seal_V1', 0), ('end', 0)]
GOODM = GOOD[:-1] + [('month_V1_%s' % m, 0) for m in ('2601', '2602', '2603', '2604')] + [('end', 0)]
FEB = 1771000000      # 13 Feb 2026
s16b = lambda b: hashlib.sha256(b).hexdigest()[:16]
s16 = lambda p: s16b(open(p, 'rb').read())


def wr(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(t)


STUB = r"""#!/usr/bin/env python3
import os, sys, gzip
name = os.path.basename(__file__)[:-3]; a = sys.argv[1:]
open(os.environ['STUB_LOG'], 'a').write(name + ' ' + ' '.join(a[:1]) + '\n')
if os.environ.get('STUB_FAIL') == name:
    print('planted failure'); sys.exit(9)
if name == 'busy':
    if a[0] == 'build':
        os.makedirs(a[3]); open(a[3] + '/BUSY_V1.json', 'w').write('{}')
        for x in a[4:]:
            gzip.open(a[3] + '/BZ_%s.tsv.gz' % x.split('=')[1], 'wt').write('x')
    else:
        open(a[1], 'w').write('ok')
elif name == 'outcomes':
    os.makedirs(a[9]); open(a[9] + '/RUN_MANIFEST.json', 'w').write('{}')
elif name == 'export':
    open(a[4], 'w').write('x')
elif name == 'extract':
    gzip.open(a[2], 'wt').write('x')
elif name == 'profile':
    if a[0] == 'build':
        os.makedirs(a[7])
    else:
        open(a[6], 'w').write('x')
elif name in ('reader', 'reader12'):
    os.makedirs(a[3]); aid = open(a[0]).read().split('\n')[1].split('\t')[1]
    lab = os.environ.get('STUB_LABEL', 'NEEDS MORE MONTHS (SIZE)')
    if name == 'reader12':
        if not os.path.isfile(a[a.index('--bar') + 1] + '/BAR_V1.json'):
            print('no bar tables'); sys.exit(8)
        open(a[3] + '/FL_RULE12.tsv', 'w').write('alarm_id\tcode\tRULE_12\tRULE_9\tSIZE_SepDec\tSIZE_SepDec_z\n%s\tX\t%s\tNOT PASS\tPASS\t2.5\n' % (aid, lab))
    else:
        open(a[3] + '/FL_RULE9.tsv', 'w').write('alarm_id\tcode\tRULE_9\tSIZE_SepDec\tSIZE_SepDec_z\n%s\tX\t%s\tPASS\t2.5\n' % (aid, lab))
elif name == 'bar':
    os.makedirs(a[5]); open(a[5] + '/BAR_V1.json', 'w').write('{}')
print(name, 'done')
"""


class World:
    def __init__(self):
        self.t = tempfile.mkdtemp(prefix='fl19_')
        self.A = os.path.join(self.t, 'Alarm'); self.D = os.path.join(self.t, 'data')
        for rel in ('_tools/settings_v1.py', 'settings/SETTINGS_EXAMPLE.env', RUNT + '/reg_append_v1.py', KIT + '/jobs/JOB_COUNT_V7.job.sh.txt', KIT + '/jobs/JOB_ENTRY_V7.job.sh.txt'):
            os.makedirs(os.path.dirname(os.path.join(self.A, rel)), exist_ok=True); shutil.copyfile(os.path.join(BASE, rel), os.path.join(self.A, rel))
        for n in ('JOB_GRADE_V14', 'JOB_MONTH_V14'):
            shutil.copyfile(os.path.join(PKG, KIT, 'jobs', n + '.job.sh.txt'), os.path.join(self.A, KIT, 'jobs', n + '.job.sh.txt'))
        os.makedirs(os.path.join(self.A, KIT, 'tools')); shutil.copyfile(Q14, os.path.join(self.A, KIT, 'tools/queue_job_v14.py'))
        shutil.copyfile(TPL, os.path.join(self.A, KIT, 'jobs/JOB_FIRSTLOOK_V1.job.sh.txt'))
        self.tools = {}
        for k in ('outcomes', 'export', 'extract', 'profile', 'busy', 'reader', 'reader12', 'bar'):
            rel = FLD + '/%s.py' % k; wr(os.path.join(self.A, rel), STUB); self.tools[k] = rel
        for k, p in (('lists', LISTS), ('receipt', REC)):
            rel = FLD + '/' + os.path.basename(p); shutil.copyfile(p, os.path.join(self.A, rel)); self.tools[k] = rel
        for k in ('outcome_settings', 'costs'):
            rel = FLD + '/%s.txt' % k; wr(os.path.join(self.A, rel), k); self.tools[k] = rel
        self.sett = {'tools': {k: {'rel': v, 'sha16': s16(os.path.join(self.A, v))} for k, v in self.tools.items() if k not in ('reader', 'reader12', 'bar')},
                     'readers': {'v11': {'rel': self.tools['reader'], 'sha16': s16(os.path.join(self.A, self.tools['reader'])), 'rule_file': 'FL_RULE9.tsv', 'label_column': 'RULE_9', 'extra_args': []},
                                 'v12': {'rel': self.tools['reader12'], 'sha16': s16(os.path.join(self.A, self.tools['reader12'])), 'rule_file': 'FL_RULE12.tsv', 'label_column': 'RULE_12', 'extra_args': [], 'mem_mb': 3035,
                                         'bar_tool': {'rel': self.tools['bar'], 'sha16': s16(os.path.join(self.A, self.tools['bar']))}}}, 'default_reader': 'v11',
                     'pins': [], 'labels': ['BEST_1M', 'OBH4_60M'],
                     'months': {'run_first': '20250901', 'first': '20250910', 'design_last': '20251231', 'full_last': '20260430'}}
        self.write_sett()
        R = os.path.join(self.D, 'research'); self.Rn = os.path.join(R, 'ALARM_DESIGN/runs', RUN); self.SC = os.path.join(self.D, 'scratch'); self.QU = os.path.join(self.D, 'q')
        for q in range(1, 22):
            for x in ('IN', 'RUN'):
                os.makedirs(os.path.join(self.QU, 'Q_V%d' % q, x))
        os.makedirs(self.SC)
        self.alloc = os.path.join(self.D, 'alloc.py'); wr(self.alloc, 'import os\np=%r\nn=int(open(p).read()) if os.path.exists(p) else 20269000\nopen(p,"w").write(str(n+1))\nprint(n)\n' % (self.alloc + '.n'))
        for k in ('lab', 'store'):
            os.makedirs(os.path.join(self.D, k))
        self.gate = os.path.join(self.D, 'gate.txt'); wr(self.gate, 'RUN\n')
        keys = [l.split('=')[0] for l in open(os.path.join(self.A, 'settings/SETTINGS_EXAMPLE.env')) if re.match(r'[A-Z]', l)]
        vals = dict(PYTHON=sys.executable, LAB_DAYS=os.path.join(self.D, 'lab'), RESEARCH_STORE=os.path.join(self.D, 'store'), SCRATCH=self.SC, RESEARCH_ROOT=R,
                    RUNNER_QUEUES=self.QU, RUNNER_ALLOC=self.alloc, FEED_GATE=self.gate)
        self.S = os.path.join(self.D, 'S.env'); wr(self.S, ''.join('%s=%s\n' % (k, vals.get(k, '')) for k in keys))
        src = os.path.join(BASE, KIT, 'runs/TEMPLATE_V4/registers')
        os.makedirs(os.path.join(self.Rn, 'registers'))
        for f in os.listdir(src):
            shutil.copyfile(os.path.join(src, f), os.path.join(self.Rn, 'registers', f))
        wr(os.path.join(self.Rn, '..', 'IDEAS_CLAIMED', '%s_%s.txt' % (RUN, IDEA)), 'claim\n')
        wr(os.path.join(self.Rn, 'ideas', IDEA, 'defs/V1.json'), json.dumps({'window': {'first': '20250901', 'last': '20260430'}}))
        wr(os.path.join(self.Rn, 'ideas', IDEA, 'CARD_%s.md' % IDEA), 'card\n')
        h = [l for l in open(os.path.join(self.Rn, 'registers/VARIANTS.tsv')).read().split('\n') if l and not l.startswith('#')][0].split('\t')
        row = dict(utc='x', idea=IDEA, V='V1', lean='FADE', def_rel='ideas/%s/defs/V1.json' % IDEA, def_sha16=s16(os.path.join(self.Rn, 'ideas', IDEA, 'defs/V1.json')),
                   prereg_rel='ideas/%s/CARD_%s.md' % (IDEA, IDEA), prereg_sha16=s16(os.path.join(self.Rn, 'ideas', IDEA, 'CARD_%s.md' % IDEA)), reason='r')
        with open(os.path.join(self.Rn, 'registers/VARIANTS.tsv'), 'a') as f:
            f.write('\t'.join(row.get(k, '') for k in h) + '\n')
        self.var = row; self.reg_job('GRADE', GRADE, '-'); self.receipts(GRADE); self.scratch(GRADE, self.perfire(), self.fires()); self.bind(GRADE)

    def write_sett(self):
        wr(os.path.join(self.A, '06_First_look/FIRSTLOOK_SETTINGS_V1.json'), json.dumps(self.sett, indent=1))

    def perfire(self, month=False):
        rows = ['kind\tcoin\tt\tday\tmonth\thour\tside\twave\tw\twave_size\tc',
                'A\tBTC\t1760000000\td\tm\th\t1\t0\t1\t1\t0.1', 'A\tETH\t1760003000\td\tm\th\t-1\t1\t1\t1\t0.1',
                'R\tSOL\t1760000100\td\tm\th\t1\t0\t0.5\t1\t0.1', 'R\tXRP\t1760000200\td\tm\th\t1\t0\t0.5\t1\t0.1']
        if month:
            rows += ['A\tBTC\t1770000000\td\tm\th\t1\t2\t1\t1\t0.1', 'R\tSOL\t1770000100\td\tm\th\t1\t2\t1\t1\t0.1']
        return '\n'.join(rows) + '\n'

    def fires(self, month=False):
        rows = ['coin\tt\tside', 'BTC\t1760000000\t1', 'ETH\t1760003000\t-1'] + (['BTC\t1770000000\t1'] if month else [])
        return '\n'.join(rows) + '\n'

    def receipts(self, job, stages=None):
        d = os.path.join(self.Rn, 'receipts', job); rows = (GOODM if '_MONTH_' in job else GOOD) if stages is None else stages
        wr(os.path.join(d, 'STAGES.tsv'), 'stage\trc\tseconds\tutc\tnote\n' + ''.join('%s\t%d\t1\tu\tn\n' % r for r in rows))
        return d

    def scratch(self, job, pf, fl):
        d = os.path.join(self.SC, 'work_' + RUN, job); wr(os.path.join(d, 'PERFIRE_V1.tsv'), pf); wr(os.path.join(d, 'V1_FIRES_V1_LIST.tsv'), fl)

    def month(self, grade=GRADE):
        self.reg_job('MONTH', MONTH, grade); self.receipts(MONTH); self.scratch(MONTH, self.perfire(True), self.fires(True)); self.bind(MONTH)

    def reg_job(self, kind, job, from_job, variants='V1', text=None):
        """the job's own RUNS row and twin, as the queue writes them"""
        n = job.split('_')[0]; name = '%s_judge_AB1_%s_%s.job.sh' % (n, kind, IDEA); wr(os.path.join(self.Rn, 'jobs', name), text if text is not None else 'VS=(%s)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(%s)\n' % (' '.join(variants.split(',')), ' '.join([self.var['def_rel']] * len(variants.split(','))), ' '.join([self.var['def_sha16']] * len(variants.split(','))), ' '.join([self.var['lean']] * len(variants.split(',')))))
        h = [l for l in open(os.path.join(self.Rn, 'registers/RUNS.tsv')).read().split('\n') if l and not l.startswith('#')][0].split('\t')
        row = dict(utc_queued='x', job='jobs/' + name, job_sha16=s16(os.path.join(self.Rn, 'jobs', name)), kind=kind, idea=IDEA, variants=variants, queue='Q_V1', prereg_rel=self.var['prereg_rel'], prereg_sha16=self.var['prereg_sha16'],
                   writes_mb='1', mem_mb='1', minutes='1', template_sha16='x', from_job=from_job, receipts_rel='receipts/' + job)
        with open(os.path.join(self.Rn, 'registers/RUNS.tsv'), 'a') as f:
            f.write('\t'.join(row.get(k, '') for k in h) + '\n')

    def bind(self, job, v='V1', seal=True):
        """what the finished job leaves in its receipts, from the scratch files as they are now: the log, the fire list's record, the seal, SHA16.txt"""
        d = os.path.join(self.Rn, 'receipts', job); w = os.path.join(self.SC, 'work_' + RUN, job); pf = os.path.join(w, 'PERFIRE_%s.tsv' % v); fl = os.path.join(w, '%s_FIRES_V1_LIST.tsv' % v)
        rows = [l.split('\t') for l in open(pf).read().split('\n')[1:] if l]; ts = [int(x[2]) for x in rows]; nA = sum(x[0] == 'A' for x in rows); nR = sum(x[0] == 'R' for x in rows)
        wr(os.path.join(d, 'perfire_%s.log' % v), 'WROTE %s %d alarm rows %d random rows\n' % (pf, nA, nR))
        nf = len(open(fl).read().split('\n')) - 2
        if '_MONTH_' in job:
            shutil.copyfile(fl, os.path.join(d, '%s_FIRES_V1_LIST.tsv' % v))
        else:
            wr(os.path.join(d, 'FIRES.tsv'), '%s\t%d\t%s\t%s\n' % (v, nf, s16(fl), fl))
        if seal:
            wr(os.path.join(d, 'PERFIRE_SEAL.tsv'), '%s\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n' % (v, s16(pf), nA, nR, min(ts), max(ts), len(rows), job))
        elif os.path.exists(os.path.join(d, 'PERFIRE_SEAL.tsv')):
            os.rename(os.path.join(d, 'PERFIRE_SEAL.tsv'), os.path.join(d, 'x_old_seal'))
        self.sha16_file(d)

    def sha16_file(self, d):
        wr(os.path.join(d, 'SHA16.txt'), ''.join('%s  %s\n' % (hashlib.sha256(open(os.path.join(d, x), 'rb').read()).hexdigest(), x) for x in sorted(os.listdir(d)) if x.endswith('.tsv') or x.endswith('.txt') and x != 'SHA16.txt'))

    def source(self, body, fires, job=GRADE):
        """a planted source its own job really wrote: scratch and evidence agree"""
        self.scratch(job, body, fires); self.bind(job)

    def q(self, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(self.A, KIT, 'tools/queue_job_v14.py'), '--settings', self.S] + list(a), capture_output=True, text=True)

    def fl(self, *a):
        return self.q(RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', GRADE, *a)

    def job_text(self, *a):
        r = self.fl('--dry', *a); assert r.returncode == 0, r.stdout + r.stderr
        return r.stdout[r.stdout.index('# JOB '):r.stdout.index('DRY RUN OK')]

    def only_job(self):
        return [os.path.join(self.QU, 'Q_V1/IN', x) for x in os.listdir(os.path.join(self.QU, 'Q_V1/IN')) if x.endswith('.job.sh')][-1]

    def bash(self, job, env=None):
        e = dict(os.environ, STUB_LOG=os.path.join(self.D, 'stub.log')); e.update(env or {})
        return subprocess.run(['bash', job], capture_output=True, text=True, env=e)

    def queue_and_run(self, *a, env=None):
        r = self.fl(*a); assert r.returncode == 0, r.stdout + r.stderr
        job = self.only_job(); p = self.bash(job, env)
        os.rename(job, job + '.ran')
        n = re.search(r'/(\d+)_judge', job).group(1)
        return p, os.path.join(self.Rn, 'receipts', '%s_FIRSTLOOK_%s' % (n, IDEA))

    def runs(self):
        return list(csv.DictReader((l for l in open(os.path.join(self.Rn, 'registers/RUNS.tsv')) if not l.startswith('#')), delimiter='\t'))


def stages(dv):
    return [l.split('\t')[:2] for l in open(os.path.join(dv, 'STAGES.tsv')).read().split('\n')[1:] if l]


class T01Dry(unittest.TestCase):
    def test_dry_fills_and_claims_nothing(self):
        w = World(); b = w.job_text()
        self.assertNotIn('@@', b); self.assertNotIn('/mnt', b); self.assertNotIn('expanduser', b)
        self.assertIn('PFSRC=%s' % os.path.join(w.SC, 'work_' + RUN, GRADE, 'PERFIRE_V1.tsv'), b)
        self.assertEqual(subprocess.run(['bash', '-n'], input=b, text=True).returncode, 0)
        self.assertFalse(os.path.exists(w.alloc + '.n')); self.assertEqual(os.listdir(os.path.join(w.QU, 'Q_V1', 'IN')), []); self.assertEqual([r['kind'] for r in w.runs()], ['GRADE'])

    def test_dry_checks_lines(self):
        r = World().fl('--dry')
        for k in ('grade receipts', 'perfire', 'reader'):
            self.assertRegex(r.stdout, r'DRY CHECK %s: OK' % k)

    def test_dry_names_each_missing(self):
        r = World().q(RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', '20269999_GRADE_' + IDEA, '--dry')
        self.assertEqual(r.returncode, 2); self.assertRegex(r.stdout, r'DRY CHECK grade receipts: MISSING'); self.assertRegex(r.stdout, r'DRY CHECK perfire: MISSING'); self.assertIn('NEXT:', r.stdout)


class T02Refusals(unittest.TestCase):
    def ref(self, r, want):
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn(want, r.stderr)

    def test_no_from_job(self):
        self.ref(World().q(RUN, 'FIRSTLOOK', IDEA, 'V1'), 'NEEDS --from-job')

    def test_month_as_from_job(self):
        self.ref(World().q(RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', MONTH), 'NEEDS --from-job')

    def test_no_receipts(self):
        self.ref(World().q(RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', '20269999_GRADE_' + IDEA), 'NO RECEIPTS')

    def test_grade_unfinished(self):
        w = World(); w.receipts(GRADE, [('grade_V1', 0)]); self.ref(w.fl(), 'NOT FINISHED')

    def test_grade_failed_for_v(self):
        w = World(); w.receipts(GRADE, [('grade_V1', 3), ('perfire_V1', 0), ('perfire_test_V1', 0), ('end', 3)]); self.ref(w.fl(), 'NO GOOD GRADE')

    def test_perfire_stage_failed(self):
        w = World(); w.receipts(GRADE, [('grade_V1', 0), ('perfire_V1', 1), ('perfire_test_V1', 0), ('end', 1)]); self.ref(w.fl(), 'NO GOOD GRADE')

    def test_perfire_test_stage_missing(self):
        w = World(); w.receipts(GRADE, [('grade_V1', 0), ('perfire_V1', 0), ('end', 0)]); self.ref(w.fl(), 'NO GOOD GRADE')

    def test_two_variants(self):
        w = World(); h = open(os.path.join(w.Rn, 'registers/VARIANTS.tsv')).read().rstrip('\n').split('\n')[-1]
        open(os.path.join(w.Rn, 'registers/VARIANTS.tsv'), 'a').write(h.replace('\tV1\t', '\tV2\t') + '\n')
        self.ref(w.q(RUN, 'FIRSTLOOK', IDEA, 'V1,V2', '--from-job', GRADE), 'ONE VARIANT')

    def test_unsealed_variant(self):
        self.ref(World().q(RUN, 'FIRSTLOOK', IDEA, 'V9', '--from-job', GRADE), 'NOT IN VARIANTS')

    def test_long_name(self):
        w = World(); n = 'V' * 21; h = open(os.path.join(w.Rn, 'registers/VARIANTS.tsv')).read().rstrip('\n').split('\n')[-1]
        open(os.path.join(w.Rn, 'registers/VARIANTS.tsv'), 'a').write(h.replace('\tV1\t', '\t%s\t' % n) + '\n')
        self.ref(w.q(RUN, 'FIRSTLOOK', IDEA, n, '--from-job', GRADE), 'NAME TOO LONG')

    def test_perfire_gone_names_the_sweep(self):
        w = World(); pf = os.path.join(w.SC, 'work_' + RUN, GRADE); os.rename(pf, pf + '_swept')
        r = w.fl(); self.ref(r, 'NO PERFIRE'); self.assertIn('NEXT:', r.stderr); self.assertIn('DSK', r.stderr)

    def test_perfire_without_random(self):
        w = World(); w.source('kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t1\t1\n', 'coin\tt\tside\nBTC\t1760000000\t1\n'); self.ref(w.fl(), 'PERFIRE HAS')

    def test_month_job_on_other_kind(self):
        self.ref(World().q(RUN, 'GRADE', IDEA, 'V1', '--month-job', MONTH), '--month-job IS ONLY FOR FIRSTLOOK')

    def test_month_job_bad_name(self):
        self.ref(World().fl('--month-job', GRADE), '--month-job MUST BE')

    def test_month_job_no_receipts(self):
        self.ref(World().fl('--month-job', MONTH), 'NO RECEIPTS')

    def test_month_job_no_good_stage(self):
        w = World(); w.receipts(MONTH, [('grade_V1', 1), ('end', 1)]); self.ref(w.fl('--month-job', MONTH), 'NO GOOD MONTH')

    def test_again_same_mode(self):
        w = World(); p, dv = w.queue_and_run(); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.ref(w.fl(), 'ALREADY LOOKED')

    def test_failed_look_may_run_again(self):
        w = World(); p, dv = w.queue_and_run(env={'STUB_FAIL': 'reader'}); self.assertNotEqual(p.returncode, 0)
        self.assertEqual(w.fl('--dry').returncode, 0)

    def test_full_after_sepdec_allowed(self):
        w = World(); p, dv = w.queue_and_run(); self.assertEqual(p.returncode, 0); w.month()
        self.assertEqual(w.fl('--month-job', MONTH, '--dry').returncode, 0)


class T03Perfire(unittest.TestCase):
    def test_receipts_copy_wins_over_scratch(self):
        w = World(); wr(os.path.join(w.Rn, 'receipts', GRADE, 'PERFIRE_V1.tsv'), w.perfire())
        self.assertIn('PFSRC=%s' % os.path.join(w.Rn, 'receipts', GRADE, 'PERFIRE_V1.tsv'), w.job_text())

    def test_job_names_the_runners_scratch_not_this_machines(self):
        w = World(); j = os.path.join(w.D, 'J.env'); wr(j, open(w.S).read().replace('SCRATCH=%s' % w.SC, 'SCRATCH=/runner/scratch'))
        r = w.fl('--dry', '--job-settings', j); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('PFSRC=/runner/scratch/work_%s/%s/PERFIRE_V1.tsv' % (RUN, GRADE), r.stdout)

    def test_sha_pinned(self):
        w = World(); self.assertIn('PFSHA=%s' % s16b(w.perfire().encode()), w.job_text())

    def test_fires_list_given(self):
        w = World(); self.assertIn('--fires %s' % os.path.join(w.SC, 'work_' + RUN, GRADE, 'V1_FIRES_V1_LIST.tsv'), w.job_text())


class T04Modes(unittest.TestCase):
    def test_sepdec_never_opens_january(self):
        b = World().job_text()
        self.assertIn('MODE=SEPDEC', b); self.assertIn('LAST=20251231', b); self.assertIn('RWIN=20250901:20251231', b); self.assertNotIn('20260430', b)

    def test_full(self):
        w = World(); w.month(); b = w.job_text('--month-job', MONTH)
        self.assertIn('MODE=FULL', b); self.assertIn('LAST=20260430', b); self.assertIn('RWIN=20250901:20260430', b)
        self.assertIn('PFSRC=%s' % os.path.join(w.SC, 'work_' + RUN, MONTH, 'PERFIRE_V1.tsv'), b)

    def test_sizes_from_counts(self):
        r = World().fl('--dry'); m = int(re.search(r'declared minutes: (\d+)', r.stdout).group(1)); self.assertTrue(10 <= m <= 59); self.assertNotIn('OVER 60', r.stdout)

    def test_over_60_names_it(self):
        w = World(); nf = 25000; rows = ['kind\tcoin\tt\tside\tw'] + ['A\tC%d\t1760000000\t1\t1' % i for i in range(25000)] + ['R\tC%d\t1760000000\t1\t1' % i for i in range(90000)]
        w.source('\n'.join(rows) + '\n', 'coin\tt\tside\n' + ''.join('C%d\t1760000000\t1\n' % i for i in range(nf)))
        r = w.fl('--dry'); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn('NOTE: OVER 60 DECLARED MINUTES', r.stdout)

    def test_too_big_for_the_run_budget_is_refused(self):
        w = World(); nf = 30000; rows = ['kind\tcoin\tt\tside\tw'] + ['A\tC%d\t1760000000\t1\t1' % i for i in range(30000)] + ['R\tC%d\t1760000000\t1\t1' % i for i in range(150000)]
        w.source('\n'.join(rows) + '\n', 'coin\tt\tside\n' + ''.join('C%d\t1760000000\t1\n' % i for i in range(nf)))
        r = w.fl('--dry'); self.assertEqual(r.returncode, 2); self.assertIn('DISK BUDGET', r.stderr)


class T05ReaderSetting(unittest.TestCase):
    def test_swap_to_edition_12_by_settings_only(self):
        w = World(); w.sett['default_reader'] = 'v12'; w.write_sett()
        p, dv = w.queue_and_run(env={'STUB_LABEL': 'NOT PASS'})
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(os.path.isfile(os.path.join(dv, 'FL_RULE12_ROW.tsv')))
        log = open(os.path.join(w.D, 'stub.log')).read(); self.assertIn('reader12', log); self.assertNotIn('reader ', log)

    def bad(self, change, want='FIRSTLOOK SETTINGS'):
        w = World(); change(w.sett); w.write_sett(); r = w.fl(); self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn(want, r.stderr)

    def test_wrong_sha(self):
        self.bad(lambda s: s['readers']['v11'].update(sha16='0' * 16))

    def test_reader_outside_part(self):
        self.bad(lambda s: s['readers']['v11'].update(rel='_tools/settings_v1.py', sha16=s16(os.path.join(BASE, '_tools/settings_v1.py'))))

    def test_dotdot(self):
        self.bad(lambda s: s['readers']['v11'].update(rel=FLD + '/../../../../x.py'))

    def test_dotdot_to_a_true_file(self):
        self.bad(lambda s: s['tools']['busy'].update(rel=FLD + '/../alarm_first_look/busy.py'))

    def test_missing_tool(self):
        self.bad(lambda s: s['tools'].pop('busy'))

    def test_unknown_tool(self):
        self.bad(lambda s: s['tools'].update(extra={'rel': 'x', 'sha16': 'y'}))

    def test_unsafe_extra_arg(self):
        self.bad(lambda s: s['readers']['v11'].update(extra_args=['; x']))

    def test_months_past_april(self):
        self.bad(lambda s: s['months'].update(full_last='20260531'))

    def test_tool_changed_after_settings(self):
        w = World(); wr(os.path.join(w.A, w.tools['busy']), 'changed'); r = w.fl(); self.assertEqual(r.returncode, 2); self.assertIn('FIRSTLOOK SETTINGS', r.stderr)


class T06Queue(unittest.TestCase):
    def test_real_queue_writes_twin_row_in(self):
        w = World(); r = w.fl(); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertRegex(r.stdout, r'QUEUED Q_V1 20269000 20269000_judge_AB1_FIRSTLOOK_TESTIDEA.job.sh')
        self.assertEqual(w.runs()[-1]['kind'], 'FIRSTLOOK'); self.assertEqual(w.runs()[-1]['from_job'], GRADE)
        self.assertTrue(os.path.isfile(os.path.join(w.QU, 'Q_V1/IN/20269000_judge_AB1_FIRSTLOOK_TESTIDEA.job.sh')))

    def test_from_job_records_the_month_job(self):
        w = World(); w.month(); self.assertEqual(w.fl('--month-job', MONTH).returncode, 0); self.assertEqual(w.runs()[-1]['from_job'], MONTH)

    def test_template_pinned(self):
        w = World(); open(os.path.join(w.A, KIT, 'jobs/JOB_FIRSTLOOK_V1.job.sh.txt'), 'a').write('# x\n')
        r = w.fl(); self.assertEqual(r.returncode, 2); self.assertIn('TEMPLATE CHANGED', r.stderr)

    def test_other_kinds_as_v12(self):
        src = open(Q14).read()
        for k, sha, name in (('COUNT', '9acb9c0c2b241320', 'JOB_COUNT_V7'), ('GRADE', s16(os.path.join(PKG, KIT, 'jobs/JOB_GRADE_V14.job.sh.txt')), 'JOB_GRADE_V14'), ('MONTH', s16(os.path.join(PKG, KIT, 'jobs/JOB_MONTH_V14.job.sh.txt')), 'JOB_MONTH_V14'), ('ENTRY', 'fdc51e1f114f4906', 'JOB_ENTRY_V7')):
            self.assertIn("'%s': '%s'" % (k, sha), src); self.assertIn("'%s': '%s.job.sh.txt'" % (k, name), src)
        self.assertIn("MONTHS = ('2601', '2602', '2603', '2604')", src)

    def test_count_still_dry(self):
        w = World(); r = w.q(RUN, 'COUNT', IDEA, 'V1=ideas/%s/defs/V1.json' % IDEA, '--dry'); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn('DRY RUN OK', r.stdout)


class T07Chain(unittest.TestCase):
    def test_all_stages_in_order_and_receipts(self):
        w = World(); p, dv = w.queue_and_run(); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        want = ['start', 'perfire_copy', 'lists', 'busy', 'om_A', 'export_A', 'extract_A', 'om_R', 'export_R', 'extract_R', 'ap_g', 'apx_g', 'ap_h', 'apx_h', 'prove', 'reader', 'receipt', 'end']
        self.assertEqual([s for s, _ in stages(dv)], want); self.assertTrue(all(r == '0' for _, r in stages(dv)))
        for f in ('PERFIRE_V1.tsv', 'FL_RULE9_ROW.tsv', 'FIRST_LOOK.md', 'PEAKS.tsv', 'DISK.tsv', 'SHA16.txt', 'FL/FL_RULE9.tsv', 'inputs/TARGETS_FL.tsv', 'outcomes/STAGES.tsv', 'profile/STAGES.tsv', 'busy/STAGES.tsv'):
            self.assertTrue(os.path.isfile(os.path.join(dv, f)), f)
        self.assertEqual(open(os.path.join(dv, 'PERFIRE_V1.tsv')).read(), w.perfire())
        self.assertIn('NEEDS MORE MONTHS', open(os.path.join(dv, 'FIRST_LOOK.md')).read())

    def test_reader_sees_finished_folders(self):
        w = World(); p, dv = w.queue_and_run()
        for d in ('outcomes', 'profile', 'busy'):
            self.assertTrue(any(x.split('\t')[1:3] == ['end', '0'] for x in open(os.path.join(dv, d, 'STAGES.tsv')).read().split('\n') if x), d)

    def test_failure_stops_before_the_reader(self):
        for step in ('busy', 'outcomes', 'export', 'extract', 'profile'):
            w = World(); p, dv = w.queue_and_run(env={'STUB_FAIL': step})
            self.assertNotEqual(p.returncode, 0, step); self.assertNotIn('reader', open(os.path.join(w.D, 'stub.log')).read(), step)
            self.assertFalse(os.path.exists(os.path.join(dv, 'FIRST_LOOK.md')))
            self.assertEqual(stages(dv)[-1][0], 'end'); self.assertNotEqual(stages(dv)[-1][1], '0')

    def test_perfire_changed_after_queue(self):
        w = World(); w.fl(); open(os.path.join(w.SC, 'work_' + RUN, GRADE, 'PERFIRE_V1.tsv'), 'a').write('A\tX\t1760000001\td\tm\th\t1\t0\t1\t1\t0.1\n')
        p = w.bash(w.only_job()); self.assertEqual(p.returncode, 3); self.assertFalse(os.path.exists(os.path.join(w.D, 'stub.log')))

    def test_tool_changed_after_queue(self):
        w = World(); w.fl(); open(os.path.join(w.A, w.tools['receipt']), 'a').write('# x\n'); self.assertEqual(w.bash(w.only_job()).returncode, 3)

    def test_gate_file_missing(self):
        w = World(); w.fl(); os.rename(w.gate, w.gate + '.x'); self.assertEqual(w.bash(w.only_job()).returncode, 8)

    def test_sepdec_with_a_pass_label_is_a_fault(self):
        w = World(); p, dv = w.queue_and_run(env={'STUB_LABEL': 'SIZE+SIDE'}); self.assertEqual(p.returncode, 3); self.assertFalse(os.path.exists(os.path.join(dv, 'FIRST_LOOK.md')))

    def test_receipt_gets_the_source(self):
        w = World(); self.assertIn('--source SEALED %s PFSHA_X' % GRADE, w.job_text().replace('$PFSHA', 'PFSHA_X'))

    def test_no_forbidden_word_in_template(self):
        self.assertIsNone(re.search(r'(?<![A-Za-z0-9_])(rm|dd|git|sudo|sleep|timeout|alarm)(?![A-Za-z0-9_])', open(TPL).read()))


class T08Lists(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='fl19l_'); self.pf = os.path.join(self.d, 'P.tsv'); self.out = os.path.join(self.d, 'o')
        wr(self.pf, 'kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t1\t1\nR\tSOL\t1760000100\t1\t0.5\nA\tETH\t1770000000\t1\t1\nR\tSOL\t1770000100\t1\t0.5\n')

    def run_(self, pf=None, first='20250910', last='20260430', *more):
        return subprocess.run([sys.executable, '-B', LISTS, pf or self.pf, 'V1', 'FADE', 'I_V1', first, last, self.d, self.out] + list(more), capture_output=True, text=True)

    def target(self):
        return next(csv.DictReader(open(self.out + '/TARGETS_FL.tsv'), delimiter='\t'))

    def test_window_drops_and_counts(self):
        r = self.run_(last='20251231'); self.assertEqual(r.returncode, 0, r.stdout); t = self.target(); self.assertEqual((t['n_A'], t['n_R'], t['dropped_outside']), ('1', '1', '2'))

    def test_last_day_is_whole(self):
        wr(self.pf, 'kind\tcoin\tt\tside\tw\nA\tBTC\t1767225599\t1\t1\nR\tSOL\t1767225598\t1\t0.5\nA\tETH\t1767225600\t1\t1\n')
        self.run_(last='20251231'); t = self.target(); self.assertEqual(t['n_A'], '1'); self.assertEqual(t['dropped_outside'], '1')

    def test_perfire_relative_and_sha(self):
        self.run_(); t = self.target(); self.assertEqual(t['perfire'], 'P.tsv'); self.assertEqual(t['perfire_sha16'], s16(self.pf))

    def test_refuses(self):
        for name, body in (('twice', 'kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t1\t1\nA\tbtc\t1760000000\t1\t1\nR\tS\t1760000100\t1\t1\n'),
                           ('side', 'kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t2\t1\nR\tS\t1760000100\t1\t1\n'),
                           ('w', 'kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t1\t1\nR\tS\t1760000100\t1\tnan\n'),
                           ('neg', 'kind\tcoin\tt\tside\tw\nA\tBTC\t1760000000\t1\t1\nR\tS\t1760000100\t1\t-1\n'),
                           ('col', 'kind\tcoin\tt\tside\nA\tBTC\t1760000000\t1\n'),
                           ('nofire', 'kind\tcoin\tt\tside\tw\nR\tS\t1760000100\t1\t1\n'),
                           ('norandom', 'kind\tcoin\tt\tside\tw\nA\tS\t1760000100\t1\t1\n')):
            p = os.path.join(self.d, name + '.tsv'); wr(p, body); r = self.run_(pf=p); self.assertEqual(r.returncode, 2, name + r.stdout); self.assertIn('REFUSED', r.stdout); self.assertFalse(os.path.exists(self.out), name)

    def test_bad_dates(self):
        self.assertEqual(self.run_(first='20251301').returncode, 2); r = self.run_(first='20260101', last='20251231'); self.assertEqual(r.returncode, 2); self.assertIn('FIRST AFTER LAST', r.stdout)

    def test_fires_checked(self):
        f = os.path.join(self.d, 'F.tsv'); wr(f, 'coin\tt\tside\nBTC\t1760000000\t1\n')
        self.assertEqual(self.run_(None, '20250910', '20251231', '--fires', f).returncode, 0)
        wr(f, 'coin\tt\tside\nBTC\t1760000000\t-1\n'); self.out += '2'
        r = self.run_(None, '20250910', '20251231', '--fires', f); self.assertEqual(r.returncode, 2); self.assertIn('FIRE LIST', r.stdout)

    def test_out_exists(self):
        os.makedirs(self.out); self.assertEqual(self.run_().returncode, 2)

    def test_real_T12_bytes_equal_fl_lists_v2(self):
        pf = os.environ.get('FL_STORED_PERFIRE')
        if not pf:
            self.skipTest('FL_STORED_PERFIRE not set (a check on the stored FB5: the proof job sets it)')
        o = os.path.join(self.d, 'real')
        r = subprocess.run([sys.executable, '-B', LISTS, pf, 'FB5', 'FADE', 'AD1_FORCEDBREAK_FB5', '20250910', '20260430', self.d, o, '--code', 'T12'], capture_output=True, text=True); self.assertEqual(r.returncode, 0, r.stdout)
        for f in ('A_T12_EVENTS.tsv', 'R_T12_EVENTS.tsv', 'R_T12_W.tsv'):
            self.assertEqual(s16(o + '/' + f), s16(os.environ['FL_STORED_LISTS'] + '/' + f), f)


class T09Receipt(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix='fl19r_'); self.o = self.d + '/FL'; self.v = self.d + '/v'; os.makedirs(self.o); os.makedirs(self.v)

    def go(self, body, mode='FULL'):
        wr(self.o + '/FL_RULE9.tsv', body); return subprocess.run([sys.executable, '-B', REC, self.o, 'FL_RULE9.tsv', 'RULE_9', 'I_V1', mode, self.v], capture_output=True, text=True)

    def test_row_copied(self):
        r = self.go('alarm_id\tRULE_9\nI_V1\tSIZE+SIDE\n'); self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(open(self.v + '/FL_RULE9_ROW.tsv').read(), 'alarm_id\tRULE_9\nI_V1\tSIZE+SIDE\n'); self.assertIn('RULE_9 = SIZE+SIDE', open(self.v + '/FIRST_LOOK.md').read())

    def test_refuses(self):
        for b in ('alarm_id\tX\nI_V1\ty\n', 'alarm_id\tRULE_9\nOTHER\tSIZE\n', 'alarm_id\tRULE_9\n', 'alarm_id\tRULE_9\nI_V1\tSIZE\nJ\tSIZE\n', 'alarm_id\tRULE_9\nI_V1\tNOT RUN\n'):
            r = self.go(b); self.assertEqual(r.returncode, 2, b); self.assertFalse(os.path.exists(self.v + '/FIRST_LOOK.md'))

    def test_sepdec_labels(self):
        self.assertEqual(self.go('alarm_id\tRULE_9\nI_V1\tNEEDS MORE MONTHS (SIZE)\n', 'SEPDEC').returncode, 0)

    def test_sepdec_not_pass(self):
        self.assertEqual(self.go('alarm_id\tRULE_9\nI_V1\tNOT PASS\n', 'SEPDEC').returncode, 0)

    def test_sepdec_refuses_a_pass(self):
        for lab in ('SIZE', 'SIDE', 'SIZE+SIDE'):
            d = tempfile.mkdtemp(prefix='fl19r_'); os.makedirs(d + '/FL'); os.makedirs(d + '/v'); wr(d + '/FL/FL_RULE9.tsv', 'alarm_id\tRULE_9\nI_V1\t%s\n' % lab)
            self.assertEqual(subprocess.run([sys.executable, '-B', REC, d + '/FL', 'FL_RULE9.tsv', 'RULE_9', 'I_V1', 'SEPDEC', d + '/v'], capture_output=True).returncode, 3, lab)

    def test_explains_the_two_passes(self):
        self.go('alarm_id\tRULE_9\nI_V1\tSIZE\n'); self.assertIn('decide_v3', open(self.v + '/FIRST_LOOK.md').read())


class T11Source(unittest.TestCase):
    """GPT HOLD 1 (09:57:42Z): the source of a look is bound to its job, its digest and its period, before anything is copied"""
    def ref(self, r, want):
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn(want, r.stderr); self.assertFalse(os.path.exists(os.path.join(os.path.dirname(self.w.alloc), 'alloc.py.n')))

    def setUp(self):
        self.w = World()

    def sc(self, job=GRADE, n='PERFIRE_V1.tsv'):
        return os.path.join(self.w.SC, 'work_' + RUN, job, n)

    def rc(self, n, job=GRADE):
        return os.path.join(self.w.Rn, 'receipts', job, n)

    # the hold's two cases
    def test_hold_mutated_grade_with_feb_rows(self):
        w = self.w; w.scratch(GRADE, w.perfire(True), w.fires()); self.ref(w.fl('--dry'), 'SOURCE')

    def test_hold_month_failed_january_no_runs_row(self):
        w = self.w; w.receipts(MONTH, GOOD[:-1] + [('month_V1_2601', 9), ('end', 9)]); w.scratch(MONTH, w.perfire(True), w.fires(True)); self.ref(w.fl('--dry', '--month-job', MONTH), 'NO GOOD MONTH')

    # the period, on the job's own evidence: a source its job really wrote with outside rows
    def test_grade_with_feb_row_even_when_sealed(self):
        w = self.w; w.source(w.perfire(True), w.fires(True)); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    def test_grade_feb_random_row_only(self):
        w = self.w; w.source(w.perfire() + 'R\tSOL\t%d\td\tm\th\t1\t2\t1\t1\t0.1\n' % FEB, w.fires()); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    def test_grade_first_second_of_january_out_last_of_december_in(self):
        w = self.w; w.source(w.perfire() + 'R\tSOL\t1767225599\td\tm\th\t1\t2\t1\t1\t0.1\n', w.fires()); self.assertEqual(w.fl('--dry').returncode, 0)
        w.source(w.perfire() + 'R\tSOL\t1767225600\td\tm\th\t1\t2\t1\t1\t0.1\n', w.fires()); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    def test_row_before_the_run(self):
        w = self.w; w.source(w.perfire() + 'R\tSOL\t1756684799\td\tm\th\t1\t2\t1\t1\t0.1\n', w.fires()); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    def test_full_with_may_row(self):
        w = self.w; w.month(); w.source(w.perfire(True) + 'R\tSOL\t1777593600\td\tm\th\t1\t2\t1\t1\t0.1\n', w.fires(True), MONTH); self.ref(w.fl('--month-job', MONTH), 'OUTSIDE THE PERIOD')

    def test_nothing_copied_or_claimed_on_refusal(self):
        w = self.w; w.source(w.perfire(True), w.fires(True)); r = w.fl(); self.assertEqual(r.returncode, 2); self.assertEqual(os.listdir(os.path.join(w.QU, 'Q_V1/IN')), []); self.assertFalse(os.path.exists(w.alloc + '.n'))
        self.assertEqual(w.runs()[-1]['kind'], 'GRADE')

    def test_bad_time_and_kind(self):
        w = self.w; w.source(w.perfire(), w.fires()); open(self.sc(), 'a').write('R\tSOL\tsoon\td\tm\th\t1\t2\t1\t1\t0.1\n')
        # bind by hand: the file itself is what is wrong
        self.ref(w.fl(), 'SOURCE')
        w2 = World(); self.w = w2; body = w2.perfire() + 'Z\tSOL\t1760000300\td\tm\th\t1\t2\t1\t1\t0.1\n'; w2.source(body, w2.fires()); self.ref(w2.fl(), 'SOURCE KIND')

    # the digest
    def test_same_count_swap_inside_the_period_caught_by_the_seal(self):
        w = self.w; b = w.perfire().replace('R\tXRP\t1760000200', 'R\tDOGE\t1760000200'); w.scratch(GRADE, b, w.fires()); self.ref(w.fl(), 'SOURCE DIGEST')

    def test_seal_of_another_job(self):
        w = self.w; p = self.rc('PERFIRE_SEAL.tsv'); wr(p, open(p).read().replace(GRADE, MONTH)); w.sha16_file(os.path.dirname(p)); self.ref(w.fl(), 'SOURCE SEAL')

    def test_seal_scope_disagrees(self):
        w = self.w; p = self.rc('PERFIRE_SEAL.tsv'); x = open(p).read().split('\t'); x[2] = '99'; wr(p, '\t'.join(x)); w.sha16_file(os.path.dirname(p)); self.ref(w.fl(), 'SOURCE SEAL')

    def test_seal_time_scope_disagrees(self):
        w = self.w; p = self.rc('PERFIRE_SEAL.tsv'); x = open(p).read().split('\t'); x[5] = str(int(x[5]) + 1); wr(p, '\t'.join(x)); w.sha16_file(os.path.dirname(p)); self.ref(w.fl(), 'SOURCE SEAL')

    def test_seal_edited_after_the_job(self):
        w = self.w; p = self.rc('PERFIRE_SEAL.tsv'); wr(p, open(p).read() + 'V9\tx\t1\t1\t1\t1\t2\t%s\n' % GRADE); self.ref(w.fl(), 'SOURCE SEAL')

    def test_two_seal_rows_of_the_variant(self):
        w = self.w; p = self.rc('PERFIRE_SEAL.tsv'); wr(p, open(p).read() * 2); w.sha16_file(os.path.dirname(p)); self.ref(w.fl(), 'SOURCE SEAL')

    def test_two_copies_differ(self):
        w = self.w; wr(self.rc('PERFIRE_V1.tsv'), w.perfire() + 'R\tSOL\t1760000300\td\tm\th\t1\t0\t1\t1\t0.1\n'); self.ref(w.fl(), 'SOURCE TWO COPIES')

    def test_sha16_record_of_an_older_receipts_copy(self):
        w = self.w; shutil.copyfile(self.sc(), self.rc('PERFIRE_V1.tsv')); os.rename(self.sc(), self.sc() + '.gone'); w.bind_after = None
        os.rename(self.rc('PERFIRE_SEAL.tsv'), self.rc('x_seal')); w.receipts(GRADE, [x for x in GOOD if not x[0].startswith('perfire_seal')]); w.sha16_file(os.path.dirname(self.rc('x'))); self.assertEqual(w.fl('--dry').returncode, 0)
        self.assertIn('--source RECEIPT_SHA16', w.job_text())
        wr(self.rc('PERFIRE_V1.tsv'), w.perfire().replace('XRP', 'DOGE')); self.ref(w.fl(), 'SOURCE DIGEST')

    # jobs before the seal
    def old(self):
        self.w.receipts(GRADE, [x for x in GOOD if not x[0].startswith('perfire_seal')]); self.w.bind(GRADE, seal=False)

    def test_no_seal_refused_without_the_flag(self):
        self.old(); r = self.w.fl(); self.ref(r, 'NO SOURCE SEAL'); self.assertIn('NEXT:', r.stderr)

    def test_no_seal_with_flag_says_so_on_the_job_and_page(self):
        self.old(); b = self.w.job_text('--unsealed-source'); self.assertIn('--source UNSEALED %s' % GRADE, b)
        p, dv = self.w.queue_and_run('--unsealed-source'); self.assertEqual(p.returncode, 0, p.stdout + p.stderr); self.assertIn('UNSEALED', open(os.path.join(dv, 'FIRST_LOOK.md')).read())

    def test_flag_never_beats_a_seal(self):
        w = self.w; w.scratch(GRADE, w.perfire().replace('XRP', 'DOGE'), w.fires()); self.ref(w.fl('--unsealed-source'), 'SOURCE DIGEST')
        self.assertIn('--source SEALED', World().job_text('--unsealed-source'))

    def test_flag_only_for_firstlook(self):
        self.ref(self.w.q(RUN, 'COUNT', IDEA, 'V1=ideas/%s/defs/V1.json' % IDEA, '--unsealed-source'), '--unsealed-source IS ONLY FOR FIRSTLOOK')

    def test_unsealed_still_checks_the_period(self):
        w = self.w; w.scratch(GRADE, w.perfire(True), w.fires(True)); self.old(); self.ref(w.fl('--unsealed-source'), 'OUTSIDE THE PERIOD')

    def test_unsealed_counts_against_the_log(self):
        w = self.w; self.old(); w.scratch(GRADE, w.perfire() + 'R\tSOL\t1760000300\td\tm\th\t1\t0\t1\t1\t0.1\n', w.fires()); self.ref(w.fl('--unsealed-source'), 'SOURCE LOG')

    def test_unsealed_log_of_another_job(self):
        w = self.w; self.old(); p = self.rc('perfire_V1.log'); wr(p, open(p).read().replace(GRADE, '20260009_GRADE_' + IDEA)); self.ref(w.fl('--unsealed-source'), 'SOURCE LOG')

    def test_unsealed_no_log(self):
        w = self.w; self.old(); os.rename(self.rc('perfire_V1.log'), self.rc('x_log')); self.ref(w.fl('--unsealed-source'), 'SOURCE LOG')

    # the fire list
    def test_fire_list_changed(self):
        w = self.w; open(self.sc(n='V1_FIRES_V1_LIST.tsv'), 'a').write('XRP\t1760000500\t1\n'); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def test_fire_list_no_record(self):
        w = self.w; os.rename(self.rc('FIRES.tsv'), self.rc('x_fires')); w.sha16_file(os.path.dirname(self.rc('x'))); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def old_month_no_list_record(self):
        w = self.w; w.month(); w.receipts(MONTH, [x for x in GOODM if not x[0].startswith('perfire_seal')]); w.bind(MONTH, seal=False); os.rename(self.rc('V1_FIRES_V1_LIST.tsv', MONTH), self.rc('x_list', MONTH)); w.sha16_file(os.path.dirname(self.rc('x', MONTH)))

    def test_old_job_with_no_list_record_still_compares_the_list(self):
        w = self.w; self.old_month_no_list_record(); self.assertEqual(w.fl('--dry', '--unsealed-source', '--month-job', MONTH).returncode, 0)
        wr(self.sc(MONTH, 'V1_FIRES_V1_LIST.tsv'), 'coin\tt\tside\nBTC\t1760000000\t1\n'); self.ref(w.fl('--unsealed-source', '--month-job', MONTH), 'SOURCE FIRE LIST')

    def test_old_job_with_no_list_at_all(self):
        w = self.w; self.old_month_no_list_record(); os.rename(self.sc(MONTH, 'V1_FIRES_V1_LIST.tsv'), self.sc(MONTH, 'x')); self.assertEqual(w.fl('--dry', '--unsealed-source', '--month-job', MONTH).returncode, 0)

    def test_old_job_with_a_record_and_a_changed_list(self):
        w = self.w; self.old(); open(self.sc(n='V1_FIRES_V1_LIST.tsv'), 'a').write('XRP\t1760000500\t1\n'); self.ref(w.fl('--unsealed-source'), 'SOURCE FIRE LIST')

    def test_fire_list_same_rows_other_bytes(self):
        w = self.w; p = self.sc(n='V1_FIRES_V1_LIST.tsv'); x = open(p).read().split('\n'); wr(p, '\n'.join([x[0], x[2], x[1]] + x[3:])); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def test_sealed_job_no_record_and_list_gone(self):
        w = self.w; os.rename(self.rc('FIRES.tsv'), self.rc('x_fires')); w.sha16_file(os.path.dirname(self.rc('x'))); os.rename(self.sc(n='V1_FIRES_V1_LIST.tsv'), self.sc(n='x')); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def test_fire_list_gone(self):
        w = self.w; os.rename(self.sc(n='V1_FIRES_V1_LIST.tsv'), self.sc(n='x')); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def test_fires_differ_from_the_list(self):
        w = self.w; w.source(w.perfire().replace('A\tETH\t1760003000', 'A\tADA\t1760003000'), w.fires()); self.ref(w.fl(), 'SOURCE FIRE LIST')

    def test_month_list_recorded_in_sha16(self):
        w = self.w; w.month(); self.assertEqual(w.fl('--dry', '--month-job', MONTH).returncode, 0)
        open(self.rc('V1_FIRES_V1_LIST.tsv', MONTH), 'a').write('XRP\t1760000500\t1\n'); self.ref(w.fl('--month-job', MONTH), 'SOURCE FIRE LIST')

    # the job
    def test_grade_not_in_runs(self):
        w = self.w; p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x)); self.ref(w.fl(), 'SOURCE NOT IN RUNS')

    def test_month_no_runs_row(self):
        w = self.w; w.receipts(MONTH); w.scratch(MONTH, w.perfire(True), w.fires(True)); w.bind(MONTH); self.ref(w.fl('--month-job', MONTH), 'SOURCE NOT IN RUNS')

    def test_month_from_another_grade(self):
        w = self.w; w.month('20260009_GRADE_' + IDEA); self.ref(w.fl('--month-job', MONTH), 'SOURCE MONTH')

    def test_month_of_another_variant(self):
        w = self.w; w.reg_job('MONTH', MONTH, GRADE, 'V2'); w.receipts(MONTH); w.scratch(MONTH, w.perfire(True), w.fires(True)); w.bind(MONTH); self.ref(w.fl('--month-job', MONTH), 'SOURCE JOB')

    def test_job_twin_changed(self):
        w = self.w; p = os.path.join(w.Rn, 'jobs', '20260001_judge_AB1_GRADE_%s.job.sh' % IDEA); open(p, 'a').write('# x\n'); self.ref(w.fl(), 'SOURCE JOB')

    def test_job_of_another_definition(self):
        w = World(); self.w = w; p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x)); w.reg_job('GRADE', GRADE, '-', text='DSHAS=(other)\n'); self.ref(w.fl(), 'SOURCE JOB')

    def test_prereg_differs(self):
        w = self.w; p = os.path.join(w.Rn, 'registers/RUNS.tsv'); t = open(p).read(); wr(p, t.replace(w.var['prereg_sha16'], 'deadbeef', 1)); self.ref(w.fl(), 'SOURCE JOB')

    # months
    def bad_month(self, st, want='NO GOOD MONTH'):
        w = self.w; w.month(); w.receipts(MONTH, st); self.ref(w.fl('--month-job', MONTH), want)

    def test_each_month_must_pass(self):
        for m in ('2601', '2602', '2603', '2604'):
            self.w = World(); self.bad_month([x if x[0] != 'month_V1_' + m else (x[0], 3) for x in GOODM[:-1]] + [('end', 3)])

    def test_a_month_stage_missing(self):
        self.bad_month([x for x in GOODM if x[0] != 'month_V1_2604'])

    def test_end_failed_with_no_named_stage(self):
        self.bad_month(GOODM[:-1] + [('end', 3)], 'FAILED STAGE')

    def test_other_stage_of_this_variant_failed(self):
        self.bad_month(GOODM[:-1] + [('conditions_V1_1h', 3), ('end', 3)], 'FAILED STAGE')

    def test_other_variants_failure_is_not_this_ones(self):
        w = self.w; w.month(); w.receipts(MONTH, GOODM[:-1] + [('grade_V2', 3), ('end', 3)]); self.assertEqual(w.fl('--dry', '--month-job', MONTH).returncode, 2)
        p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if MONTH not in x)); w.reg_job('MONTH', MONTH, GRADE, 'V1,V2'); self.assertEqual(w.fl('--dry', '--month-job', MONTH).returncode, 0)

    def test_grade_seal_stage_failed(self):
        w = self.w; w.receipts(GRADE, [('grade_V1', 0), ('perfire_V1', 0), ('perfire_test_V1', 0), ('perfire_seal_V1', 1), ('end', 1)]); self.ref(w.fl(), 'FAILED STAGE')

    # the two new templates
    def seal_fn(self, name):
        t = open(os.path.join(PKG, KIT, 'jobs', name)).read(); return re.search(r'^seal\(\)\{.*$', t, re.M).group(0)

    def test_template_seal_writes_what_the_queue_reads(self):
        w = self.w; w.source(w.perfire() + 'R\tSOL\t1760000300\td\tm\th\t1\t0\t1\t1\t0.1\n', w.fires()); d = tempfile.mkdtemp(prefix='fl19s_'); shutil.copyfile(self.sc(), d + '/PERFIRE_V1.tsv'); want = open(self.rc('PERFIRE_SEAL.tsv')).read()
        for n in ('JOB_GRADE_V14.job.sh.txt', 'JOB_MONTH_V14.job.sh.txt'):
            s = d + '/DV_' + n; os.makedirs(s); r = subprocess.run(['bash', '-c', 'W=%s; DV=%s; J=%s\n%s\nseal V1' % (d, s, GRADE, self.seal_fn(n))], capture_output=True, text=True); self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(open(s + '/PERFIRE_SEAL.tsv').read(), want)

    def test_templates_change_nothing_else(self):
        for k, a in (('GRADE', '  [ "$r" = 0 ] && { seal $V; st perfire_seal_$V $? 0 ""; }\n'), ('MONTH', '    if [ $r -eq 0 ]; then seal $V; st perfire_seal_$V $? 0 ""; fi\n')):
            n = open(os.path.join(PKG, KIT, 'jobs/JOB_%s_V14.job.sh.txt' % k)).read(); o = open(os.path.join(BASE, KIT, 'jobs/JOB_%s_V13.job.sh.txt' % k)).read(); self.assertEqual(n.count(a), 1)
            strip = lambda t: t.split('\n', 1)[1]
            self.assertEqual(strip(n).replace(a, '').replace(self.seal_fn('JOB_%s_V14.job.sh.txt' % k) + '\n', ''), strip(o))

    def test_templates_pass_the_queue_words(self):
        for k in ('GRADE', 'MONTH'):
            self.assertIsNone(re.search(r'(?<![A-Za-z0-9_])(rm|dd|git|sudo|sleep|timeout)(?![A-Za-z0-9_])', self.seal_fn('JOB_%s_V14.job.sh.txt' % k)))


class T12Page(unittest.TestCase):
    """GPT HOLD 2 (10:30:53Z): edition 11's label stays beside edition 12's, and both read as retrospective"""
    def go(self, body, col='RULE_12', rule='FL_RULE12.tsv', extra=()):
        d = tempfile.mkdtemp(prefix='fl19p_'); os.makedirs(d + '/FL'); os.makedirs(d + '/v'); wr(d + '/FL/' + rule, body)
        r = subprocess.run([sys.executable, '-B', REC, d + '/FL', rule, col, 'I_V1', 'FULL', d + '/v'] + list(extra), capture_output=True, text=True); self.assertEqual(r.returncode, 0, r.stdout)
        return open(d + '/v/FIRST_LOOK.md').read()

    def test_v11_label_beside_v12(self):
        p = self.go('alarm_id\tRULE_12\tRULE_9\nI_V1\tSIZE+SIDE\tSIDE\n'); self.assertIn('RULE_12 = SIZE+SIDE', p); self.assertIn('RULE_9 (edition 11) = SIDE', p); self.assertIn('retrospective', p); self.assertIn("moment's own B", p)

    def test_v12_without_v11_column_refused(self):
        d = tempfile.mkdtemp(prefix='fl19p_'); os.makedirs(d + '/FL'); os.makedirs(d + '/v'); wr(d + '/FL/FL_RULE12.tsv', 'alarm_id\tRULE_12\nI_V1\tSIZE\n')
        r = subprocess.run([sys.executable, '-B', REC, d + '/FL', 'FL_RULE12.tsv', 'RULE_12', 'I_V1', 'FULL', d + '/v'], capture_output=True, text=True); self.assertEqual(r.returncode, 2); self.assertIn('RULE_9', r.stdout); self.assertFalse(os.path.exists(d + '/v/FIRST_LOOK.md'))

    def test_v11_page_has_no_beside_line(self):
        p = self.go('alarm_id\tRULE_9\nI_V1\tSIZE\n', 'RULE_9', 'FL_RULE9.tsv'); self.assertNotIn('edition 11) =', p); self.assertIn('moves 4c', p)

    def test_source_line(self):
        p = self.go('alarm_id\tRULE_9\nI_V1\tSIZE\n', 'RULE_9', 'FL_RULE9.tsv', ('--source', 'SEALED', 'J1', 'abc')); self.assertIn('Source: J1, PERFIRE abc, SEALED', p)
        p = self.go('alarm_id\tRULE_9\nI_V1\tSIZE\n', 'RULE_9', 'FL_RULE9.tsv', ('--source', 'UNSEALED', 'J1', 'abc')); self.assertIn('not authenticated', p)


class T13Hold3(unittest.TestCase):
    """GPT HOLD d7f4868861ae2366 (ALARM_V1_19_1), and --reader"""
    def ref(self, r, want):
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn(want, r.stderr)

    def rc(self, w, n, job=GRADE):
        return os.path.join(w.Rn, 'receipts', job, n)

    def sc(self, w, job=GRADE):
        return os.path.join(w.SC, 'work_' + RUN, job, 'PERFIRE_V1.tsv')

    def module(self, w):
        import importlib.util
        spec = importlib.util.spec_from_file_location('q14_t', os.path.join(w.A, KIT, 'tools/queue_job_v14.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

    # 1 the source
    def test_the_digest_validated_is_the_digest_in_the_job(self):
        w = World(); Q = self.module(w); orig = Q.fl_count; pf = self.sc(w); first = s16(pf)

        def later(*a, **k):
            n = orig(*a, **k); open(pf, 'a').write('R\tDOGE\t%d\td\tm\th\t1\t9\t1\t1\t0.1\n' % FEB); return n
        Q.fl_count = later
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(Q.main(['--settings', w.S, RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', GRADE]), 0)
        job = w.only_job(); self.assertIn('PFSHA=%s' % first, open(job).read())
        p = w.bash(job); self.assertEqual(p.returncode, 3, p.stdout + p.stderr)
        d = [x for x in os.listdir(os.path.join(w.Rn, 'receipts')) if 'FIRSTLOOK' in x][0]; self.assertFalse(os.path.exists(os.path.join(w.Rn, 'receipts', d, 'PERFIRE_V1.tsv')))

    def test_the_digest_comes_from_the_bytes_scanned(self):
        w = World(); Q = self.module(w); orig = Q.fl_scan; pf = self.sc(w); first = s16(pf)

        def later(*a, **k):
            n = orig(*a, **k); open(pf, 'a').write('R\tDOGE\t%d\td\tm\th\t1\t9\t1\t1\t0.1\n' % FEB); return n
        Q.fl_scan = later
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(Q.main(['--settings', w.S, RUN, 'FIRSTLOOK', IDEA, 'V1', '--from-job', GRADE]), 0)
        self.assertIn('PFSHA=%s' % first, open(w.only_job()).read())

    def test_the_runs_row_names_another_variant(self):
        w = World(); p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x))
        w.reg_job('GRADE', GRADE, '-', 'V2', text='VS=(V1)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(FADE)\n' % (w.var['def_rel'], w.var['def_sha16'])); self.ref(w.fl('--dry'), 'DID NOT RUN')

    def test_a_sealed_row_before_the_looks_first_day(self):
        w = World(); w.source(w.perfire() + 'R\tDOGE\t1756771200\td\tm\th\t1\t0\t0.5\t1\t0.1\n', w.fires()); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    def test_first_second_of_the_look_is_in(self):
        w = World(); w.source(w.perfire() + 'R\tDOGE\t1757462400\td\tm\th\t1\t0\t0.5\t1\t0.1\n', w.fires()); self.assertEqual(w.fl('--dry').returncode, 0)
        w = World(); w.source(w.perfire() + 'R\tDOGE\t1757462399\td\tm\th\t1\t0\t0.5\t1\t0.1\n', w.fires()); self.ref(w.fl(), 'OUTSIDE THE PERIOD')

    # 2 the seal
    def lose(self, keep_stage=False, keep_sha=False):
        w = World(); d = os.path.dirname(self.rc(w, 'x')); os.rename(self.rc(w, 'PERFIRE_SEAL.tsv'), os.path.join(d, 'x_lost'))
        if not keep_stage:
            w.receipts(GRADE, [x for x in GOOD if not x[0].startswith('perfire_seal')])
        if not keep_sha:
            w.sha16_file(d)
        return w

    def test_lost_seal_the_digest_list_says_it_existed(self):
        self.ref(self.lose(keep_sha=True).fl('--dry', '--unsealed-source'), 'SOURCE SEAL LOST')

    def test_lost_seal_the_stage_says_it_existed(self):
        self.ref(self.lose(keep_stage=True).fl('--dry', '--unsealed-source'), 'SOURCE SEAL LOST')

    def test_lost_seal_the_template_says_it_existed(self):
        w = self.lose(); p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x)); w.reg_job('GRADE', GRADE, '-')
        t = open(p).read(); wr(p, t.replace('\tx\t-\treceipts/' + GRADE, '\t%s\t-\treceipts/%s' % (re.search(r"'GRADE': '([0-9a-f]+)'", open(Q14).read()).group(1), GRADE)))
        self.assertIn(re.search(r"'GRADE': '([0-9a-f]+)'", open(Q14).read()).group(1), open(p).read()); self.ref(w.fl('--dry', '--unsealed-source'), 'SOURCE SEAL LOST')

    def test_lost_seal_the_twin_says_it_existed(self):
        w = self.lose(); p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x))
        w.reg_job('GRADE', GRADE, '-', text='VS=(V1)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(FADE)\nseal PERFIRE_SEAL.tsv\n' % (w.var['def_rel'], w.var['def_sha16'])); self.ref(w.fl('--dry', '--unsealed-source'), 'SOURCE SEAL LOST')

    def test_a_job_that_never_had_one_still_takes_the_flag(self):
        w = self.lose(); self.ref(w.fl('--dry'), 'NO SOURCE SEAL'); self.assertEqual(w.fl('--dry', '--unsealed-source').returncode, 0)

    # 3 the variant
    def twin(self, **k):
        w = World(); a = dict(VS='V1', DEFS=w.var['def_rel'], DSHAS=w.var['def_sha16'], LEANS='FADE'); a.update(k)
        p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if GRADE not in x))
        w.reg_job('GRADE', GRADE, '-', text=''.join('%s=(%s)\n' % (n, a[n]) for n in a if a[n] is not None)); return w

    def test_the_twin_as_the_queue_writes_it(self):
        self.assertEqual(self.twin().fl('--dry').returncode, 0)

    def test_grade_ran_the_other_lean(self):
        self.ref(self.twin(LEANS='FOLLOW').fl('--dry'), 'SOURCE LEAN')

    def test_no_lean_recorded(self):
        self.ref(self.twin(LEANS=None).fl('--dry'), 'SOURCE LEAN')

    def test_another_definition_file_same_digest_elsewhere(self):
        self.ref(self.twin(DEFS='ideas/%s/defs/V2.json' % IDEA).fl('--dry'), 'SOURCE JOB')

    def test_digest_pinned_for_another_variant(self):
        w = World(); self.ref(self.twin(VS='V0 V1', DEFS=w.var['def_rel'] + ' ' + w.var['def_rel'], DSHAS='%s other' % w.var['def_sha16'], LEANS='FADE FADE').fl('--dry'), 'SOURCE JOB')

    def test_lean_of_this_variant_not_of_another(self):
        w = World(); self.ref(self.twin(VS='V0 V1', DEFS=w.var['def_rel'] + ' ' + w.var['def_rel'], DSHAS=w.var['def_sha16'] + ' ' + w.var['def_sha16'], LEANS='FADE FOLLOW').fl('--dry'), 'SOURCE LEAN')

    def test_newest_variants_row_with_another_lean(self):
        w = World(); r = dict(w.var, lean='FOLLOW'); r.pop('utc')
        a = subprocess.run([sys.executable, '-B', os.path.join(w.A, RUNT, 'reg_append_v1.py'), w.Rn, 'VARIANTS', '-'], input=json.dumps(r), capture_output=True, text=True); self.assertEqual(a.returncode, 0, a.stderr)
        self.ref(w.fl('--dry'), 'SOURCE LEAN')

    def test_month_is_bound_too(self):
        w = World(); w.month(); p = os.path.join(w.Rn, 'registers/RUNS.tsv'); l = open(p).read().split('\n'); wr(p, '\n'.join(x for x in l if MONTH not in x))
        w.reg_job('MONTH', MONTH, GRADE, text='VS=(V1)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(FOLLOW)\n' % (w.var['def_rel'], w.var['def_sha16'])); self.ref(w.fl('--dry', '--month-job', MONTH), 'SOURCE LEAN')

    # --reader
    def test_default_is_edition_11(self):
        b = World().job_text(); self.assertIn('READER=$AL/%s/reader.py' % FLD, b); self.assertNotIn(' bar ', b.replace('# JOB', '')); self.assertNotIn('--bar', b); self.assertEqual(json.load(open(SETT))['default_reader'], 'v11')

    def test_v12_builds_its_bars_inside_the_job_before_the_reader(self):
        w = World(); b = w.job_text('--reader', 'v12'); self.assertIn('--bar $DV/BAR', b); self.assertIn('ck $AL/%s/bar.py' % FLD, b); self.assertIn('MEM_MB: 3035', b)
        self.assertRegex(b, r'(?s)one bar .*build \$LAB \$CODE \$FIRST \$LAST \$DV/BAR \$LA=A_\$C \$LR=R_\$C\none reader')
        p, dv = w.queue_and_run('--reader', 'v12'); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn('Beside: RULE_9', open(os.path.join(dv, 'FIRST_LOOK.md')).read()); self.assertTrue(os.path.isfile(os.path.join(dv, 'FL_RULE12_ROW.tsv'))); self.assertEqual(os.path.isfile(os.path.join(dv, 'BAR/BAR_V1.json')), True)
        self.assertIn('BAR/BAR_V1.json', open(os.path.join(dv, 'SHA16.txt')).read())
        st = [x[0] for x in stages(dv)]; self.assertLess(st.index('bar'), st.index('reader'))

    def test_v12_bar_failure_stops_before_the_reader(self):
        p, dv = World().queue_and_run('--reader', 'v12', env={'STUB_FAIL': 'bar'}); self.assertNotEqual(p.returncode, 0); self.assertNotIn('reader', [x[0] for x in stages(dv)])

    def test_unknown_reader(self):
        r = World().fl('--reader', 'v9'); self.ref(r, "READER 'v9'"); self.assertIn('NEXT:', r.stderr)

    def test_reader_only_for_firstlook(self):
        self.ref(World().q(RUN, 'COUNT', IDEA, 'V1=ideas/%s/defs/V1.json' % IDEA, '--reader', 'v12'), '--reader IS ONLY FOR FIRSTLOOK')

    def test_v12_beside_v11_but_never_itself_twice(self):
        w = World(); p, _ = w.queue_and_run(); self.assertEqual(p.returncode, 0); p, _ = w.queue_and_run('--reader', 'v12'); self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.ref(w.fl('--reader', 'v12'), 'ALREADY LOOKED'); self.ref(w.fl(), 'ALREADY LOOKED')

    def test_v12_bar_tool_changed(self):
        w = World(); wr(os.path.join(w.A, w.tools['bar']), 'changed'); self.ref(w.fl(), 'FIRSTLOOK SETTINGS')


class T10Editions(unittest.TestCase):
    PATHS = re.compile(r'/Users/|/Volumes/|/mnt/|expanduser|~/')

    def code_lines(self, p):
        t = open(p).read(); m = re.match(r'(#![^\n]*\n)?(#[^\n]*\n)*\s*""".*?"""', t, re.S)
        return t[m.end():] if m else t

    def test_no_machine_path_in_code(self):
        for rel in (FLD + '/fl_lists_v3.py', FLD + '/fl_receipt_v1.py', FLD + '/busy_v2.py', FLD + '/night_export_v4.py', FLD + '/fl_extract_v1.py', '05_Profile/tree/tools/alarm_profile_v2/alarm_profile_v2_3.py'):
            self.assertIsNone(self.PATHS.search(self.code_lines(os.path.join(PKG, rel))), rel)

    def test_settings_shas_true(self):
        s = json.load(open(SETT))
        for k, e in list(s['tools'].items()) + list(s['readers'].items()) + [(x['rel'], x) for x in s['pins']] + [('bar', s['readers']['v12']['bar_tool'])] + [(x['rel'], x) for x in s['readers']['v12']['pins']]:
            p = os.path.join(PKG, e['rel']) if os.path.isfile(os.path.join(PKG, e['rel'])) else os.path.join(BASE, e['rel'])
            self.assertEqual(s16(p), e['sha16'], k)

    def test_template_sha_in_queue(self):
        self.assertIn("'FIRSTLOOK': '%s'" % s16(TPL), open(Q14).read())

    def test_profile_store_is_a_setting(self):
        t = open(os.path.join(PKG, '05_Profile/tree/tools/alarm_profile_v2/alarm_profile_v2_3.py')).read()
        self.assertIn("os.environ.get('RESEARCH_STORE')", t); self.assertNotIn("('alarm_profile_v2_2.py',", t)


if __name__ == '__main__':
    unittest.main(verbosity=1)
