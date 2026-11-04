"""test_kit5_tools_v2.py (SCOUT helper K2, 30 Oct 2026; TEST, NOT REVIEWED): the clean editions decide_v2.py, decide_forward_v2.py,
audit_run_v3.py, board_line_v2.py (KIT_V5) and idea_time_v2.py (KIT_V6), on a sandbox: an Alarm package built in a new temporary folder
(this package's _tools/settings_v1.py, its settings example with BOARD, the five tools, queue_job_v5.py (decide_v2 reads its run budget) and the two run tools they run)
and a settings file whose keys point at sandbox data outside that package (RESEARCH_ROOT, BOARD, RUNNER_QUEUES). Each tool must take
every data path from the settings file and run code only from inside its own package (CLEAN_RELEASE_V1 section 6). Where edition 1 sits
next to edition 2 in this tree, the same input must give edition 1's lines, rows and exit codes: only the paths changed.
No market data, no network; every test removes its own temporary folder; nothing is written inside an Alarm folder.
  python3 -B <Alarm>/Agentic/tree/ALARM_DESIGN/KIT_V5/tests/test_kit5_tools_v2.py      (from an Alarm package: it needs _tools/settings_v1.py)
Planted bugs: mutants_v2.py, next to this file."""
import contextlib
import datetime
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings

sys.dont_write_bytecode = True        # loading a tool must never write a cache inside a package
HERE = os.path.dirname(os.path.abspath(__file__))
AD = os.path.dirname(os.path.dirname(HERE))            # this tree's ALARM_DESIGN folder (KIT_V5/tests is two levels below)
TREE = ('Agentic', 'tree', 'ALARM_DESIGN')             # where ALARM_DESIGN sits inside an Alarm package
NEW = {'D': 'KIT_V5/tools/decide_v2.py', 'F': 'KIT_V5/tools/decide_forward_v2.py', 'A': 'KIT_V5/tools/audit_run_v3.py',
       'B': 'KIT_V5/tools/board_line_v2.py', 'I': 'KIT_V6/tools/idea_time_v2.py'}
OLD = {'D': 'KIT_V5/tools/decide_v1.py', 'F': 'KIT_V5/tools/decide_forward_v1.py', 'A': 'KIT_V5/tools/audit_run_v2.py',
       'B': 'KIT_V5/tools/board_line_v1.py', 'I': 'KIT_V6/tools/idea_time_v1.py'}
SUPPORT = ('KIT_V5/tools/queue_job_v5.py', 'runs/CLAUDE1_20261028/tools/reg_append_v1.py', 'runs/CLAUDE1_20261028/tools/read_stratentry_v1.py')
RUNTAG = 'AD1_20261029'
NOW = datetime.datetime(2026, 10, 29, 14, 0, tzinfo=datetime.timezone.utc)
HDR = {
    'VARIANTS': ['utc', 'idea', 'V', 'lean', 'def_rel', 'def_sha16', 'prereg_rel', 'prereg_sha16', 'reason'],
    'FORECASTS': ['utc', 'idea', 'V', 'scope', 'gap15_lo', 'gap15_hi', 'gap1h_lo', 'gap1h_hi', 'file_rel', 'file_sha16', 'note'],
    'RUNS': ['utc_queued', 'job', 'job_sha16', 'kind', 'idea', 'variants', 'queue', 'prereg_rel', 'prereg_sha16', 'writes_mb', 'mem_mb', 'minutes',
             'template_sha16', 'from_job', 'receipts_rel'],
    'DECISIONS': ['utc', 'idea', 'V', 'state', 'label_rule', 'r1', 'r2', 'months_counted', 'months_passing', 'waves', 'lead_15m', 't_15m', 'lead_1h',
                  't_1h', 'gate_handoff', 'clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'grade_job', 'entry_job',
                  'sources', 'note'],
    'POSTMORTEMS': ['utc', 'idea', 'V', 'job', 'scope', 'forecast', 'result', 'result_file', 'result_sha16', 'why', 'unexplained'],
    'LEARNINGS_PROPOSED': ['utc', 'id', 'kind', 'section', 'change', 'evidence_file', 'evidence_sha16', 'scope', 'status'],
    'PROBLEMS': ['utc', 'kind', 'where', 'what_is_wrong', 'evidence', 'severity', 'action', 'proposed_fix', 'reported_to_lead'],
    'TOOLS_BUILT': ['utc', 'tool_rel', 'sha16', 'range', 'test_rel', 'test_sha16', 'why'],
}
SPEC = {'P': ('PASS', 'PASS', 4, 'PASS'), 'N': ('PASS', 'no', 4, 'PASS'), 'S': ('no', 'no', 4, 'PASS'), 'I': ('no', 'no', 2, 'PASS'),
        'G': ('no', 'no', 4, 'GATE_FAIL')}      # first letter of a variant: R1, R2, counted months, hand-off gate (as the kit's sandbox)


def package_of(d):
    """the Alarm package holding d: the nearest parent with _tools/settings_v1.py and settings/ (None outside a package)"""
    while not (os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')) and os.path.isdir(os.path.join(d, 'settings'))):
        if os.path.dirname(d) == d:
            return None
        d = os.path.dirname(d)
    return d


ALARM = package_of(HERE)
FIX = os.path.join(ALARM or '', 'Agentic', 'tree', 'fixtures', 'kit5_test')    # the DP2 markout files (SCOUT's kit5_test fixtures)
HAVE_OLD = all(os.path.isfile(os.path.join(AD, p)) for p in OLD.values())


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as f:
        f.write(s)


_n = [0]


def load(path):
    """a tool as a fresh module from its file, never registered in sys.modules (each package and test gets its own)"""
    _n[0] += 1
    spec = importlib.util.spec_from_file_location('k2tool_%d' % _n[0], path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def call(m, argv):
    """a tool's main(argv) as its command runs it: (exit code, stdout, stderr); Refused is exit 2 with 'REFUSED: ...' on stderr
    (the __main__ block of decide, decide_forward and board_line), SystemExit its own code (audit)"""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), warnings.catch_warnings():
        warnings.simplefilter('ignore')       # as on the command line (edition 1's unclosed files warn only under unittest)
        try:
            rc = m.main(list(argv))
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
            if e.code is not None and not isinstance(e.code, int):
                print(e.code, file=sys.stderr)
        except Exception as e:
            if not (hasattr(m, 'Refused') and isinstance(e, m.Refused)):
                raise
            print('REFUSED: %s' % e, file=sys.stderr)
            rc = 2
    return rc, out.getvalue(), err.getvalue()


def cli(path, argv, cwd):
    r = subprocess.run([sys.executable, '-B', path] + list(argv), capture_output=True, text=True, cwd=cwd, timeout=120)
    return r.returncode, r.stdout, r.stderr


def rows(run, name):
    with open(os.path.join(run, 'registers', name + '.tsv')) as f:
        lines = [l.rstrip('\n') for l in f if l.strip() and not l.startswith('#')]
    h, out = lines[0].split('\t'), []
    for l in lines[1:]:
        x = l.split('\t')
        assert len(x) == len(h), (name, l)
        out.append(dict(zip(h, x)))
    return out


def snapshot(top):
    out = {}
    for d, ds, fs in os.walk(top):
        out.update({os.path.relpath(os.path.join(d, x), top) + '/': 'dir' for x in ds})
        out.update({os.path.relpath(os.path.join(d, f), top): sha16(os.path.join(d, f)) for f in fs})
    return out


class Box:
    """root/Alarm: the sandbox package; root/data: RESEARCH/ALARM_DESIGN (runs, IDEAS_CLAIMED), hb, runner (Q_V1..Q_V21, IN and RUN);
    root/SETTINGS_TEST.env: every key of the package's example, the three data keys set, the rest empty"""

    def __init__(self, root, extra_key=None):
        self.root, self.alarm, self.data = root, os.path.join(root, 'Alarm'), os.path.join(root, 'data')
        os.makedirs(os.path.join(self.alarm, '_tools'))
        os.makedirs(os.path.join(self.alarm, 'settings'))
        shutil.copyfile(os.path.join(ALARM, '_tools', 'settings_v1.py'), os.path.join(self.alarm, '_tools', 'settings_v1.py'))
        with open(os.path.join(ALARM, 'settings', 'SETTINGS_EXAMPLE.env')) as f:
            ex = f.read()
        if not re.search(r'(?m)^BOARD=', ex):
            ex += '# BOARD: the team board folder (hb)\nBOARD=\n'
        if extra_key:
            ex += '%s=\n' % extra_key
        w(os.path.join(self.alarm, 'settings', 'SETTINGS_EXAMPLE.env'), ex)
        self.keys = [l.split('=', 1)[0] for l in ex.splitlines() if re.match(r'^[A-Z][A-Z0-9_]*=', l)]
        for rel in list(NEW.values()) + list(SUPPORT):
            dst = self.tree(rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(AD, rel), dst)
        self.T1 = self.tree('runs/CLAUDE1_20261028/tools')
        self.H, self.hb, self.runner = os.path.join(self.data, 'RESEARCH', 'ALARM_DESIGN'), os.path.join(self.data, 'hb'), os.path.join(self.data, 'runner')
        os.makedirs(os.path.join(self.H, 'runs', 'IDEAS_CLAIMED'))
        os.makedirs(self.hb)
        for i in range(1, 22):
            for s in ('IN', 'RUN'):
                os.makedirs(os.path.join(self.runner, 'Q_V%d' % i, s))
        self.vals = {'RESEARCH_ROOT': os.path.join(self.data, 'RESEARCH'), 'BOARD': self.hb, 'RUNNER_QUEUES': self.runner}
        self.settings = self.write_settings()

    def tree(self, rel):
        return os.path.join(self.alarm, *(TREE + tuple(rel.split('/'))))

    def write_settings(self, name='SETTINGS_TEST.env', **over):
        vals = dict(self.vals, **over)
        p = os.path.join(self.root, name)
        w(p, '# sandbox settings\n' + ''.join('%s=%s\n' % (k, vals.get(k, '')) for k in self.keys))
        return p

    def tool(self, k):
        return load(self.tree(NEW[k]))

    def run(self, runtag=RUNTAG):
        r = os.path.join(self.H, 'runs', runtag)
        for n, h in HDR.items():
            w(os.path.join(r, 'registers', n + '.tsv'), '\t'.join(h) + '\n')
        return r

    def row(self, run, name, d):
        """one register row written as reg_append_v1.py writes it, with the stamp the test chooses (the timing checks are exact)"""
        with open(os.path.join(run, 'registers', name + '.tsv'), 'a') as f:
            f.write('\t'.join(str(d.get(k, '')) for k in HDR[name]) + '\n')

    def idea(self, run, idea, vs, lean='FADE', utc='2026-10-29T13:00:00Z'):
        w(os.path.join(self.H, 'runs', 'IDEAS_CLAIMED', '%s_%s.txt' % (os.path.basename(run), idea)), 'claimed\n')
        pr = 'ideas/%s/PREREG_%s.md' % (idea, idea)
        w(os.path.join(run, pr), 'prereg\n')
        for v in vs:
            d = 'ideas/%s/defs/%s.json' % (idea, v)
            w(os.path.join(run, d), json.dumps({'id': v}))
            self.row(run, 'VARIANTS', {'utc': utc, 'idea': idea, 'V': v, 'lean': lean, 'def_rel': d, 'def_sha16': sha16(os.path.join(run, d)),
                                       'prereg_rel': pr, 'prereg_sha16': sha16(os.path.join(run, pr)), 'reason': 'first'})
        return pr

    def job(self, run, kind, idea, vs, job, utc, writes=3600, from_job='-'):
        pr = 'ideas/%s/PREREG_%s.md' % (idea, idea)
        self.row(run, 'RUNS', {'utc_queued': utc, 'job': 'jobs/%s.job.sh' % job.replace('_', '_judge_%s_' % os.path.basename(run).split('_')[0], 1),
                               'job_sha16': '0' * 16, 'kind': kind, 'idea': idea, 'variants': ','.join(vs), 'queue': 'Q_V1', 'prereg_rel': pr,
                               'prereg_sha16': sha16(os.path.join(run, pr)), 'writes_mb': writes, 'mem_mb': 4000, 'minutes': 20,
                               'template_sha16': '0' * 16, 'from_job': from_job, 'receipts_rel': 'receipts/' + job})

    def grade(self, run, gj, vs, fires=3640, t0='2026-10-29T13:10:00Z', t1='2026-10-29T13:20:00Z'):
        """GRADE receipts as the job writes them; a variant with FAIL in its name failed its grade (rc 4, no hand-off row)"""
        d = os.path.join(run, 'receipts', gj)
        st, summ, fl = ['stage\trc\tseconds\tutc\tnote', 'start\t0\t0\t%s\tx' % t0], ['# summary', 'V\tlean\tstatus\tgate\twaves\tmonths_counted_any'], []
        for v in vs:
            if 'FAIL' in v:
                st.append('grade_%s\t4\t1\t%s\tfailed' % (v, t1))
                continue
            r1, r2, cnt, gate = SPEC[v[0]]
            st.append('grade_%s\t0\t1\t%s\tchain' % (v, t1))
            summ.append('%s\tFADE\tOK\t%s\t1223\t%d' % (v, gate, cnt))
            w(os.path.join(d, 'HANDOFF', 'REAL_SEALED', 'REAL_RULES_%s.tsv' % v),
              '# rules\nkey\tvalue\nR1\t%s\nR2\t%s\ncounted\t%d\nneed\t3\npassing\t%d\n' % (r1, r2, cnt, 4 if r1 == 'PASS' else 1))
            w(os.path.join(d, 'HANDOFF', 'REAL_SEALED', 'REAL_%s.tsv' % v),
              '# real\nhorizon\twaves\tdays\tlead\tse\tt\n15m\t1223\t105\t3.6297\t1.8999\t1.9105\n1h\t1223\t105\t7.4680\t2.0252\t3.6875\n')
            fl.append('%s\t%d\t%s\tSCRATCH/%s_FIRES_V1_LIST.tsv' % (v, fires, '0' * 16, v))
        st += ['handoff\t0\t1\t%s\tx' % t1, 'end\t%d\t0\t%s\tdone' % (4 if any('FAIL' in v for v in vs) else 0, t1)]
        w(os.path.join(d, 'STAGES.tsv'), '\n'.join(st) + '\n')
        w(os.path.join(d, 'HANDOFF', 'SUMMARY.tsv'), '\n'.join(summ) + '\n')
        w(os.path.join(d, 'FIRES.tsv'), '\n'.join(fl) + '\n')
        w(os.path.join(d, 'DISK.tsv'), 'du_mb_W\t10\nfree_mb_end\t70000\n')
        return gj

    def entry(self, run, ej, vs, t0='2026-10-29T13:25:00Z', t1='2026-10-29T13:28:00Z'):
        d = os.path.join(run, 'receipts', ej)
        st = ['stage\trc\tseconds\tutc\tnote', 'start\t0\t0\t%s\tx' % t0]
        for v in vs:
            st.append('markout_%s\t0\t1\t%s\tDONE' % (v, t1))
            for x in ('CURVE.tsv', 'GATES.json', 'TABLE_W0.tsv'):
                p = os.path.join(d, v, 'MARKOUT', x)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                shutil.copyfile(os.path.join(FIX, 'DP2_' + x), p)
        w(os.path.join(d, 'STAGES.tsv'), '\n'.join(st + ['end\t0\t0\t%s\tdone' % t1]) + '\n')
        return ej

    def month(self, run, mj, v, verdicts=('HELD', 'HELD', 'STRONGER', 'HELD')):
        d = os.path.join(run, 'receipts', mj)
        st = ['stage\trc\tseconds\tutc\tnote', 'start\t0\t0\t2026-10-29T13:40:00Z\tx', 'grade_%s\t0\t1\t2026-10-29T13:45:00Z\tchain' % v]
        for m, vd in zip(('2601', '2602', '2603', '2604'), verdicts):
            st.append('month_%s_%s\t0\t0\t2026-10-29T13:45:00Z\t  VERDICT %s' % (v, m, vd))
            w(os.path.join(d, 'MONTH_READ_%s_%s.txt' % (v, m)), '%s month %s lean FOLLOW: fires 400 waves 120\n  15m  a 30.7 r 23.9 gap +6.8 | other '
              'side gap +3.7\n  1h   a 36.1 r 30.7 gap +5.4 | other side gap -1.5\n  VERDICT %s\n' % (v, m, vd))
        w(os.path.join(d, 'STAGES.tsv'), '\n'.join(st + ['end\t0\t0\t2026-10-29T13:46:00Z\tdone']) + '\n')
        return mj


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='k2v2_')
        self.box = Box(os.path.join(self.tmp, 'one'))
        self.run = self.box.run()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)                    # a working folder outside every package: no tool may need one
        self.s = ['--settings', self.box.settings]

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmp)

    def decided_run(self):
        """one idea graded (S1, P1), P1's ENTRY, both decided by decide_v2.py's own computation (rows stamped 13:30), post-mortems,
        findings and a START line on the board: a run every audit check passes"""
        b, r = self.box, self.run
        b.idea(r, 'FLOWX', ['S1', 'P1'])
        gj, ej = '20260001_GRADE_FLOWX', '20260002_ENTRY_FLOWX'
        b.job(r, 'GRADE', 'FLOWX', ['S1', 'P1'], gj, '2026-10-29T13:05:00Z')
        b.grade(r, gj, ['S1', 'P1'])
        b.job(r, 'ENTRY', 'FLOWX', ['P1'], ej, '2026-10-29T13:22:00Z', writes=1000, from_job=gj)
        b.entry(r, ej, ['P1'])
        D = b.tool('D')
        D.configure(b.settings)
        for v, e in (('S1', None), ('P1', ej)):
            d = D.decide(r, 'FLOWX', v, gj, e)
            b.row(r, 'DECISIONS', dict({k: str(d.get(k, '')) for k in D.COLS}, utc='2026-10-29T13:30:00Z'))
            b.row(r, 'POSTMORTEMS', {'utc': '2026-10-29T13:35:00Z', 'idea': 'FLOWX', 'V': v, 'job': gj, 'scope': 'SEPDEC', 'forecast': 'f',
                                     'result': d['state'], 'result_file': 'x', 'result_sha16': 'x', 'why': 'w', 'unexplained': 'none'})
        w(os.path.join(r, 'ideas', 'FLOWX', 'FINDINGS_FLOWX.md'), 'findings\n')
        w(os.path.join(b.hb, 'AD1.txt'), '2026-10-29T12:55:00Z AD1 START run started with KIT_V5\n2026-10-29T12:58:00Z AD1 CLAIM FLOWX: a flow idea\n'
          '2026-10-29T14:00:00Z AD1 DONE run finished, see REPORT.md\n')
        return gj, ej

    def forward(self):
        """a STOP parent S1 (written by decide_v2.py --write), its forward-only side S1R and a plain variant S1Y, S1R's MONTH receipts"""
        b, r = self.box, self.run
        b.idea(r, 'FWDX', ['S1'])
        gj = b.grade(r, '20260010_GRADE_FWDX', ['S1'])
        rc, out, err = call(b.tool('D'), self.s + [RUNTAG, 'FWDX', 'S1', '--grade', gj, '--write'])
        self.assertIn('FWDX S1: STOP', out, err)
        v1 = rows(r, 'VARIANTS')[-1]
        for v, lean, why in (('S1R', 'FOLLOW', 'FORWARD ONLY OF S1: the other side won Sep-Dec'), ('S1Y', 'FOLLOW', 'a plain variant')):
            b.row(r, 'VARIANTS', dict(v1, utc='2026-10-29T13:31:00Z', V=v, lean=lean, reason=why))
        return gj, b.month(r, '20260011_MONTH_FWDX', 'S1R')


class T1Contract(Base):
    def test_every_path_comes_from_the_settings_file_or_the_package(self):
        b = self.box
        D, F, A, B, I = (b.tool(k) for k in 'DFABI')
        for m in (D, F, A, B, I):
            m.configure(b.settings)
        self.assertEqual((D.CFG['H'], D.CFG['REG'], D.CFG['RSE']),
                         (b.H, os.path.join(b.T1, 'reg_append_v1.py'), os.path.join(b.T1, 'read_stratentry_v1.py')))
        self.assertEqual((F.CFG['H'], F.CFG['REG']), (b.H, os.path.join(b.T1, 'reg_append_v1.py')))
        self.assertEqual((A.CFG['H'], A.CFG['HB'], A.CFG['RUNNER'], A.CFG['SETTINGS'], A.CFG['DECIDE']),
                         (b.H, b.hb, b.runner, b.settings, b.tree('KIT_V5/tools/decide_v2.py')))
        self.assertEqual(B.CFG['HB'], b.hb)
        self.assertEqual((I.H, I.HB), (b.H, b.hb))

    def test_settings_file_is_required(self):
        for k, args in (('D', [RUNTAG, 'X', 'V1', '--grade', '1_GRADE_X']), ('F', [RUNTAG, 'X', 'V1', '--month', '1_MONTH_X']),
                        ('B', [RUNTAG, 'NOTE', 'a line long enough']), ('I', [RUNTAG])):
            rc, out, err = call(self.box.tool(k), args)
            self.assertEqual((rc, out), (2, ''), k)
            self.assertIn('REFUSED: --settings <file> IS REQUIRED', err, k)
        rc, out, err = call(self.box.tool('A'), [RUNTAG])
        self.assertEqual(rc, 1)
        self.assertIn('USAGE audit_run_v3.py --settings <settings file> RUN [--write]', err)

    def test_refused_settings_files(self):
        b = self.box
        cases = [(os.path.join(self.tmp, 'NO_SUCH.env'), 'NO SETTINGS FILE'),
                 (b.write_settings('S_EMPTY.env', RESEARCH_ROOT=''), 'EMPTY RESEARCH_ROOT'),
                 (b.write_settings('S_INSIDE.env', RESEARCH_ROOT=os.path.join(b.alarm, 'data')), 'DATA INSIDE ALARM RESEARCH_ROOT')]
        for s, why in cases:
            for k, args in (('D', [RUNTAG, 'X', 'V1', '--grade', '1_GRADE_X']), ('F', [RUNTAG, 'X', 'V1', '--month', '1_MONTH_X']), ('I', [RUNTAG])):
                rc, out, err = call(b.tool(k), ['--settings', s] + args)
                self.assertEqual(rc, 2, (k, why))
                self.assertIn('REFUSED: SETTINGS: ', err, k)
                self.assertIn(why, err, k)
            rc, out, err = call(b.tool('A'), ['--settings', s, RUNTAG])
            self.assertEqual(rc, 1)
            self.assertIn(why, err)
        s = b.write_settings('S_NOBOARD.env', BOARD='')
        for k, args in (('B', [RUNTAG, 'NOTE', 'a line long enough']), ('I', [RUNTAG])):
            rc, out, err = call(b.tool(k), ['--settings', s] + args)
            self.assertEqual(rc, 2, k)
            self.assertIn('EMPTY BOARD', err, k)
        rc, out, err = call(b.tool('A'), ['--settings', s, RUNTAG])
        self.assertEqual(rc, 1)
        self.assertIn('EMPTY BOARD', err)

    def test_a_tool_outside_an_alarm_package_is_refused(self):
        loose = os.path.join(self.tmp, 'loose')
        os.makedirs(loose)
        for k, args in (('D', [RUNTAG, 'X', 'V1', '--grade', '1_GRADE_X']), ('B', [RUNTAG, 'NOTE', 'a line long enough']), ('I', [RUNTAG])):
            p = os.path.join(loose, os.path.basename(NEW[k]))
            shutil.copyfile(self.box.tree(NEW[k]), p)
            rc, out, err = call(load(p), self.s + args)
            self.assertEqual(rc, 2, k)
            self.assertIn('NOT INSIDE AN ALARM PACKAGE', err, k)

    def test_each_tool_reads_the_settings_reader_of_its_own_package(self):
        other = Box(os.path.join(self.tmp, 'two'), extra_key='ONLY_IN_TWO')
        D1, D2 = self.box.tool('D'), other.tool('D')
        D1.configure(self.box.settings)
        D2.configure(other.settings)
        self.assertTrue(D1.CFG['REG'].startswith(self.box.alarm + os.sep))
        self.assertTrue(D2.CFG['REG'].startswith(other.alarm + os.sep))
        with self.assertRaises(D1.Refused) as cm:
            D1.configure(other.settings)                  # package one's reader does not know package two's key
        self.assertIn('UNKNOWN KEYS ONLY_IN_TWO', str(cm.exception))

    def test_nothing_is_written_inside_the_package(self):
        b, r = self.box, self.run
        before = snapshot(b.alarm)
        gj, ej = self.decided_run()
        self.assertEqual(call(b.tool('D'), self.s + [RUNTAG, 'FLOWX', 'S1', '--grade', gj])[0], 0)
        self.assertEqual(call(b.tool('B'), self.s + [RUNTAG, 'NOTE', 'a note with its file x.tsv'])[0], 0)
        self.assertEqual(call(b.tool('A'), self.s + [RUNTAG, '--write'])[0], 0)
        self.assertEqual(call(b.tool('I'), self.s + [RUNTAG, '--now', '2026-10-29T14:00:00Z'])[0], 0)
        self.assertEqual(snapshot(b.alarm), before)
        self.assertEqual(len(os.listdir(os.path.join(r, 'audit'))), 1)


class T2Decide(Base):
    def test_stop_pass_and_rows(self):
        b, r = self.box, self.run
        b.idea(r, 'FLOWX', ['P1', 'N1', 'S1'])
        gj = b.grade(r, '20260001_GRADE_FLOWX', ['P1', 'N1', 'S1'])
        D = b.tool('D')
        rc, out, err = call(D, self.s + [RUNTAG, 'FLOWX', 'S1', '--grade', gj, '--write'])
        self.assertEqual(rc, 0, err)
        self.assertIn('DECISION FLOWX S1: STOP', out)
        self.assertIn('WRITTEN', out)
        rc, out, err = call(D, self.s + [RUNTAG, 'FLOWX', 'P1', '--grade', gj])
        self.assertEqual(rc, 2)
        self.assertIn('run its ENTRY job first', err)
        ej = b.entry(r, '20260002_ENTRY_FLOWX', ['P1', 'N1'])
        rc, out, err = call(D, self.s + [RUNTAG, 'FLOWX', 'P1', '--grade', gj, '--entry', ej, '--write'])
        self.assertEqual(rc, 0, err)
        self.assertIn('DECISION FLOWX P1: PASS', out)
        self.assertIn('CLEAR CLEAR', out)
        self.assertIn('LEAD 15m +3.63 (t +1.91) 1h +7.47 (t +3.69)', out)
        rc, out, err = call(D, self.s + [RUNTAG, 'FLOWX', 'N1', '--grade', gj, '--entry', ej])
        self.assertIn('DECISION FLOWX N1: NEEDS MORE MONTHS', out)
        rc, out, err = call(D, self.s + [RUNTAG, 'FLOWX', 'P1', '--grade', gj, '--entry', ej, '--write'])
        self.assertEqual(rc, 2)
        self.assertIn('ALREADY IN DECISIONS', err)
        dec = rows(r, 'DECISIONS')
        self.assertEqual([(x['V'], x['state'], x['grade_job'], x['entry_job']) for x in dec], [('S1', 'STOP', gj, '-'), ('P1', 'PASS', gj, ej)])
        d = D.decide(r, 'FLOWX', 'P1', gj, ej)
        self.assertEqual({k: dec[1][k] for k in D.COLS}, {k: str(d.get(k, '')) for k in D.COLS})

    def test_invalid_insufficient_failed(self):
        b, r = self.box, self.run
        b.idea(r, 'GATEX', ['G1', 'I1', 'PFAIL'])
        gj = b.grade(r, '20260003_GRADE_GATEX', ['G1', 'I1', 'PFAIL'])
        for v, want in (('G1', 'GATEX G1: INVALID'), ('I1', 'GATEX I1: INSUFFICIENT'), ('PFAIL', 'GATEX PFAIL: INVALID')):
            rc, out, err = call(b.tool('D'), self.s + [RUNTAG, 'GATEX', v, '--grade', gj])
            self.assertEqual(rc, 0, err)
            self.assertIn(want, out)
            if v == 'G1':
                self.assertIn('gate GATE_FAIL', out)

    def test_no_entry_uses_the_run_budget_next_to_the_tool(self):
        b, r = self.box, self.run
        b.idea(r, 'BIGY', ['P1', 'S1'])
        gj = b.grade(r, '20260004_GRADE_BIGY', ['P1', 'S1'], fires=17101)
        D = b.tool('D')
        rc, out, err = call(D, self.s + [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry-too-big'])
        self.assertEqual(rc, 2)
        self.assertIn('ITS ENTRY FITS (5400 MB for 17101 fires, budget 10000 MB)', err)
        self.assertIn('TOGETHER', call(D, self.s + [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry', '1_ENTRY_BIGY', '--entry-too-big'])[2])
        self.assertIn('ONLY FOR A VARIANT WITH R1', call(D, self.s + [RUNTAG, 'BIGY', 'S1', '--grade', gj, '--entry-too-big'])[2])
        b.grade(r, gj, ['P1', 'S1'], fires=40308)
        rc, out, err = call(D, self.s + [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry-too-big', '--write'])
        self.assertEqual(rc, 0, err)
        self.assertIn('BIGY P1: NO ENTRY', out)
        self.assertIn('12300 MB for 40308 fires, over the 10000 MB run budget', out)
        q = b.tree('KIT_V5/tools/queue_job_v5.py')            # the package's own copy is the one read
        with open(q) as f:
            src = f.read()
        w(q, src.replace("'RUN_BUDGET_MB': 10000,", "'RUN_BUDGET_MB': 20000,", 1))
        rc, out, err = call(b.tool('D'), self.s + [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry-too-big'])
        self.assertIn('ITS ENTRY FITS (12300 MB for 40308 fires, budget 20000 MB)', err)

    def test_pins_are_checked_inside_the_package(self):
        b, r = self.box, self.run
        b.idea(r, 'PINX', ['P1', 'S1'])
        gj = b.grade(r, '20260005_GRADE_PINX', ['P1', 'S1'])
        ej = b.entry(r, '20260006_ENTRY_PINX', ['P1'])
        with open(os.path.join(b.T1, 'read_stratentry_v1.py'), 'a') as f:
            f.write('# changed\n')
        rc, out, err = call(b.tool('D'), self.s + [RUNTAG, 'PINX', 'P1', '--grade', gj, '--entry', ej])
        self.assertEqual(rc, 2)
        self.assertIn('read_stratentry_v1.py CHANGED', err)
        with open(os.path.join(b.T1, 'reg_append_v1.py'), 'a') as f:
            f.write('# changed\n')
        rc, out, err = call(b.tool('D'), self.s + [RUNTAG, 'PINX', 'S1', '--grade', gj, '--write'])
        self.assertEqual(rc, 2)
        self.assertIn('reg_append_v1.py CHANGED', err)
        self.assertEqual(rows(r, 'DECISIONS'), [])


class T3Forward(Base):
    def test_forward_pass_written_then_stop_insufficient_invalid(self):
        b, r = self.box, self.run
        gj, mj = self.forward()
        F = b.tool('F')
        rc, out, err = call(F, self.s + [RUNTAG, 'FWDX', 'S1R', '--month', mj, '--write'])
        self.assertEqual(rc, 0, err)
        self.assertIn('DECISION FWDX S1R: FORWARD PASS | months read 4, holding 4', out)
        self.assertIn('WRITTEN', out)
        last = rows(r, 'DECISIONS')[-1]
        self.assertEqual((last['V'], last['state'], last['grade_job']), ('S1R', 'FORWARD PASS', gj))
        self.assertIn('ALREADY IN DECISIONS', call(F, self.s + [RUNTAG, 'FWDX', 'S1R', '--month', mj, '--write'])[2])
        self.assertIn('NOT A FORWARD-ONLY VARIANT', call(F, self.s + [RUNTAG, 'FWDX', 'S1Y', '--month', mj])[2])
        md = os.path.join(r, 'receipts', mj)
        w(os.path.join(md, 'MONTH_READ_S1R_2602.txt'), 'S1R month 2602\n  VERDICT NO READ under 30 waves\n')
        w(os.path.join(md, 'MONTH_READ_S1R_2603.txt'), 'S1R month 2603\n  VERDICT WEAKER\n')
        self.assertEqual(F.decide(r, 'FWDX', 'S1R', mj)['state'], 'FORWARD STOP')        # 2 hold of 3 read
        w(os.path.join(md, 'MONTH_READ_S1R_2604.txt'), 'S1R month 2604\n  VERDICT NO READ under 30 waves\n')
        self.assertEqual(F.decide(r, 'FWDX', 'S1R', mj)['state'], 'INSUFFICIENT')        # 2 read
        os.remove(os.path.join(md, 'MONTH_READ_S1R_2601.txt'))
        self.assertEqual(F.decide(r, 'FWDX', 'S1R', mj)['state'], 'INVALID')

    def test_register_writer_pin_inside_the_package(self):
        b, r = self.box, self.run
        gj, mj = self.forward()
        with open(os.path.join(b.T1, 'reg_append_v1.py'), 'a') as f:
            f.write('# changed\n')
        rc, out, err = call(b.tool('F'), self.s + [RUNTAG, 'FWDX', 'S1R', '--month', mj, '--write'])
        self.assertEqual(rc, 2)
        self.assertIn('reg_append_v1.py CHANGED', err)
        self.assertEqual([x['V'] for x in rows(r, 'DECISIONS')], ['S1'])


class T4Audit(Base):
    def audit(self, settings=None, minutes=5):
        A = self.box.tool('A')
        A.configure(settings or self.box.settings)
        A.CFG['now'] = lambda: NOW + datetime.timedelta(minutes=minutes)
        au = A.Audit(RUNTAG)
        lines, nfail = au.runall()
        return {x[0]: x for x in au.res}, '\n'.join(lines)

    def test_clean_run_passes_every_check(self):
        self.decided_run()
        res, txt = self.audit()
        self.assertTrue(txt.startswith('AUDIT AD1_20261029 (audit_run_v3.py, 2026-10-29T14:05:00Z). TEST, NOT REVIEWED.\n'), txt)
        self.assertIn('SCORE 17 PASS, 0 WARN, 0 FAIL', txt)

    def test_a6_recomputes_through_decide_v2_in_the_package(self):
        self.decided_run()
        p = os.path.join(self.run, 'registers', 'DECISIONS.tsv')
        with open(p) as f:
            t = f.read()
        w(p, t.replace('\tFLOWX\tP1\tPASS\t', '\tFLOWX\tP1\tNEEDS MORE MONTHS\t', 1))
        res, txt = self.audit()
        self.assertEqual(res['A6'][2], 'FAIL', txt)
        self.assertIn("FLOWX P1: state is 'NEEDS MORE MONTHS', receipts say 'PASS'", txt)

    def test_a6_forward_only_rows(self):
        self.decided_run()
        gj, mj = self.forward()
        F = self.box.tool('F')
        d = F.decide(self.run, 'FWDX', 'S1R', mj)
        self.box.row(self.run, 'DECISIONS', dict({k: str(d.get(k, '')) for k in F.COLS}, utc='2026-10-29T13:50:00Z'))
        res, txt = self.audit()
        self.assertEqual(res['A6'][2], 'PASS', txt)
        self.box.row(self.run, 'DECISIONS', dict({k: str(d.get(k, '')) for k in F.COLS}, utc='2026-10-29T13:51:00Z', months_passing='3'))
        res, txt = self.audit()
        self.assertIn("FWDX S1R: months_passing is '3', receipts say '4'", txt)

    def test_the_board_is_read_from_BOARD(self):
        self.decided_run()
        empty = os.path.join(self.box.data, 'another_board')
        os.makedirs(empty)
        res, txt = self.audit(self.box.write_settings('S_BOARD2.env', BOARD=empty))
        self.assertEqual(res['A11'][2], 'FAIL', txt)
        self.assertIn('no START line on hb/AD1.txt', txt)

    def test_the_queues_are_read_from_RUNNER_QUEUES(self):
        self.decided_run()
        w(os.path.join(self.box.runner, 'Q_V3', 'IN', '20269999_judge_AD1_GRADE_HAND.job.sh'), '# made by hand\n')
        res, txt = self.audit()
        self.assertEqual(res['A16'][2], 'FAIL', txt)
        self.assertIn('Q_V3/IN/20269999_judge_AD1_GRADE_HAND.job.sh not made by queue_job_v5.py', txt)
        res, txt = self.audit(self.box.write_settings('S_NOQ.env', RUNNER_QUEUES=''))
        self.assertEqual(res['A16'][2], 'PASS', txt)             # no runner on this machine: the queues are not read

    def test_unread_job_and_stuck_idea(self):
        self.decided_run()
        b, r = self.box, self.run
        b.idea(r, 'STUCKX', ['PFAIL1', 'PFAIL2'])
        for n, v in ((20260020, 'PFAIL1'), (20260021, 'PFAIL2')):
            b.job(r, 'GRADE', 'STUCKX', [v], '%d_GRADE_STUCKX' % n, '2026-10-29T13:06:00Z')
            b.grade(r, '%d_GRADE_STUCKX' % n, [v])
        res, txt = self.audit(minutes=45)
        self.assertEqual(res['A7'][2], 'FAIL', txt)
        self.assertIn('20260020_GRADE_STUCKX: NOT READ 85 min after its end', txt)
        self.assertEqual(res['A13'][2], 'FAIL', txt)
        b.row(r, 'PROBLEMS', {'utc': '2026-10-29T13:40:00Z', 'kind': 'TOOL', 'where': 'STUCKX grade', 'what_is_wrong': 'failed twice', 'evidence': 'x',
                              'severity': 'HIGH', 'action': 'stopped', 'proposed_fix': 'y', 'reported_to_lead': 'yes'})
        with open(os.path.join(b.hb, 'AD1.txt'), 'a') as f:
            f.write('2026-10-29T13:41:00Z AD1 STUCK STUCKX grade failed twice, see PROBLEMS\n')
        res, txt = self.audit()
        self.assertEqual(res['A13'][2], 'PASS', txt)

    def test_write_puts_the_audit_in_the_run(self):
        self.decided_run()
        A = self.box.tool('A')
        A.CFG['now'] = lambda: NOW
        rc, out, err = call(A, self.s + [RUNTAG, '--write'])
        p = os.path.join(self.run, 'audit', 'AUDIT_20261029T140000Z.txt')
        self.assertEqual(rc, 0, err)
        self.assertIn('WRITTEN %s %s' % (p, sha16(p)), out)
        with open(p) as f:
            self.assertEqual(f.read(), out.split('WRITTEN')[0])


class T5Board(Base):
    def post(self, *args):
        B = self.box.tool('B')
        B.CFG['now'] = lambda: datetime.datetime(2026, 10, 29, 14, 1, 2, tzinfo=datetime.timezone.utc)
        return call(B, self.s + list(args))

    def test_post_and_twin_in_BOARD(self):
        p = os.path.join(self.box.hb, 'AD1.txt')
        w(p, 'old line\n')
        rc, out, err = self.post(RUNTAG, 'START', 'run started, kit KIT_V5 skill alarm-design-v5')
        line = '2026-10-29T14:01:02Z AD1 START run started, kit KIT_V5 skill alarm-design-v5'
        self.assertEqual((rc, out, err), (0, 'POSTED %s %d chars\n' % (p, len(line)), ''))
        with open(p) as f:
            self.assertEqual(f.read(), 'old line\n' + line + '\n')
        with open(p + '.pre_%s_20261029T140102Z' % RUNTAG) as f:
            self.assertEqual(f.read(), 'old line\n')

    def test_new_board_then_two_lines_in_one_second(self):
        p = os.path.join(self.box.hb, 'AD1.txt')
        self.assertEqual(self.post(RUNTAG, 'NOTE', 'first line of this second')[0], 0)
        self.assertEqual(self.post(RUNTAG, 'NOTE', 'second line of this second')[0], 0)
        self.assertEqual(self.post(RUNTAG, 'NOTE', 'third line of this second')[0], 0)
        with open(p) as f:
            self.assertEqual(f.read().count('AD1 NOTE'), 3)
        self.assertTrue(os.path.isfile(p + '.pre_%s_20261029T140102Z' % RUNTAG))
        self.assertTrue(os.path.isfile(p + '.pre_%s_20261029T140102Z_2' % RUNTAG))
        self.assertEqual(sorted(os.listdir(self.box.hb)), ['AD1.txt', 'AD1.txt.pre_%s_20261029T140102Z' % RUNTAG, 'AD1.txt.pre_%s_20261029T140102Z_2' % RUNTAG])

    def test_refusals(self):
        for args, why in (([RUNTAG, 'HELLO', 'some text here'], 'KIND'), ([RUNTAG, 'NOTE', 'x' * 560], 'LINE IS 590 CHARACTERS'),
                          ([RUNTAG, 'NOTE', 'a — b long enough'], 'EM DASH'), ([RUNTAG, 'NOTE', 'short'], 'TOO SHORT'),
                          ([RUNTAG, 'NOTE', 'a\ttab in the text'], 'TAB OR NEWLINE'), (['ad1_x', 'NOTE', 'some text here'], 'BAD RUN TAG')):
            rc, out, err = self.post(*args)
            self.assertEqual(rc, 2, why)
            self.assertIn(why, err)
        self.assertEqual(os.listdir(self.box.hb), [])


class T6IdeaTime(Base):
    def test_table_from_the_settings_file(self):
        gj, ej = self.decided_run()
        rc, out, err = call(self.box.tool('I'), self.s + [RUNTAG, '--launch', 'AD1=2026-10-29T12:50:00Z', '--now', '2026-10-29T14:30:00Z'])
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.splitlines()[0], '== AD1_20261029  launch 2026-10-29 12:50:00  START 2026-10-29 12:55:00  DONE 2026-10-29 14:00:00')
        self.assertIn('FLOWX\t12:58:00Z\t7\t-\t-\t10\t2\t3\t2\t32\tS1 STOP,P1 PASS', out)
        self.assertIn('seat AD1: launch to first claim 8 min; no job running 81 pct, one 19 pct, two or more 0 pct of 70 min; first own PASS after 40 min', out)

    def test_no_run_prints_the_usage(self):
        rc, out, err = call(self.box.tool('I'), self.s)
        self.assertEqual(rc, 2)
        self.assertIn('idea_time_v2.py --settings <settings file> <RUN>', out)


def v5(x):
    """edition 1's text with the queue tool it names moved on to queue_job_v5.py: the one intended difference (the owner 30 Oct 23:54
    Berlin: past editions go to archive/, so no current tool may name queue_job_v4.py)"""
    if isinstance(x, str):
        return x.replace('queue_job_v4.py', 'queue_job_v5.py')
    if isinstance(x, tuple):
        return tuple(v5(y) for y in x)
    return x


@unittest.skipUnless(HAVE_OLD, 'edition 1 is not next to edition 2 in this tree')
class T7SameAsEdition1(Base):
    """edition 1 from this tree, pointed at the sandbox through its CFG (the only way it can be pointed anywhere), against edition 2
    through the settings file: the same input gives the same lines, rows and exit codes"""

    def old(self, k):
        b, m = self.box, load(os.path.join(AD, OLD[k]))
        reg, rse = os.path.join(b.T1, 'reg_append_v1.py'), os.path.join(b.T1, 'read_stratentry_v1.py')
        if k == 'D':
            m.CFG.update({'H': b.H, 'REG': reg, 'RSE': rse})
        elif k == 'F':
            m.CFG.update({'H': b.H, 'REG': reg})
        elif k == 'A':
            m.CFG.update({'H': b.H, 'HB': b.hb, 'RUNNER': b.runner, 'DECIDE_CFG': {'REG': reg, 'RSE': rse}})
        elif k == 'B':
            m.CFG['HB'] = b.hb
        else:
            m.F, m.H = b.data, b.H                 # edition 1 reads <F>/hb and <H>/runs
        return m

    def test_decide(self):
        b, r = self.box, self.run
        b.idea(r, 'FLOWX', ['P1', 'N1', 'S1', 'G1', 'I1', 'PFAIL'])
        gj = b.grade(r, '20260001_GRADE_FLOWX', ['P1', 'N1', 'S1', 'G1', 'I1', 'PFAIL'], fires=17101)
        ej = b.entry(r, '20260002_ENTRY_FLOWX', ['P1', 'N1'])
        D1, D2 = self.old('D'), b.tool('D')
        D2.configure(b.settings)
        for v, extra in (('S1', []), ('G1', []), ('I1', []), ('PFAIL', []), ('P1', ['--entry', ej]), ('N1', ['--entry', ej]), ('P1', []),
                         ('P1', ['--entry-too-big']), ('S1', ['--entry-too-big']), ('S1', ['--entry', ej]), ('ZZ', [])):
            args = [RUNTAG, 'FLOWX', v, '--grade', gj] + extra
            self.assertEqual(v5(call(D1, args)), call(D2, self.s + args), (v, extra))
            if v != 'ZZ' and not (v == 'P1' and not extra[:1] == ['--entry']):
                try:
                    want = D1.decide(r, 'FLOWX', v, gj, ej if '--entry' in extra else None, '--entry-too-big' in extra)
                except D1.Refused as e:
                    want = 'REFUSED %s' % e
                try:
                    got = D2.decide(r, 'FLOWX', v, gj, ej if '--entry' in extra else None, '--entry-too-big' in extra)
                except D2.Refused as e:
                    got = 'REFUSED %s' % e
                self.assertEqual(v5(want), got, v)

    def test_decide_write_same_row(self):
        b = self.box
        runs = {}
        for tag, m, pre in (('AD1_20261029', self.old('D'), []), ('AD2_20261029', b.tool('D'), self.s)):
            r = b.run(tag) if tag != RUNTAG else self.run
            b.idea(r, 'FLOWX', ['P1'])
            gj = b.grade(r, '20260001_GRADE_FLOWX', ['P1'])
            ej = b.entry(r, '20260002_ENTRY_FLOWX', ['P1'])
            rc, out, err = call(m, pre + [tag, 'FLOWX', 'P1', '--grade', gj, '--entry', ej, '--write'])
            self.assertEqual(rc, 0, err)
            runs[tag] = (re.sub(r'WRITTEN \S+ DECISIONS', 'WRITTEN <stamp> DECISIONS', out), [dict(x, utc='') for x in rows(r, 'DECISIONS')])
        self.assertEqual(runs['AD1_20261029'], runs['AD2_20261029'])

    def test_decide_forward(self):
        b, r = self.box, self.run
        gj, mj = self.forward()
        F1, F2 = self.old('F'), b.tool('F')
        for v, m in (('S1R', mj), ('S1Y', mj), ('S1R', '1_GRADE_FWDX'), ('S1', mj)):
            self.assertEqual(call(F1, [RUNTAG, 'FWDX', v, '--month', m]), call(F2, self.s + [RUNTAG, 'FWDX', v, '--month', m]), v)
        self.assertEqual(F1.decide(r, 'FWDX', 'S1R', mj), F2.decide(r, 'FWDX', 'S1R', mj))

    def test_audit(self):
        self.decided_run()
        gj, mj = self.forward()
        b, r = self.box, self.run
        b.idea(r, 'STUCKX', ['PFAIL1'])
        b.job(r, 'GRADE', 'STUCKX', ['PFAIL1'], '20260020_GRADE_STUCKX', '2026-10-29T13:06:00Z')
        b.grade(r, '20260020_GRADE_STUCKX', ['PFAIL1'])
        w(os.path.join(b.runner, 'Q_V3', 'IN', '20269999_judge_AD1_GRADE_HAND.job.sh'), '# made by hand\n')
        w(os.path.join(r, 'ideas', 'FLOWX', 'IDEA_CARD.md'), 'the reading does not exist\n')
        out = []
        for A, pre in ((self.old('A'), []), (b.tool('A'), self.s)):
            A.CFG['now'] = lambda: NOW + datetime.timedelta(minutes=45)
            out.append(call(A, pre + [RUNTAG]))
        (rc1, o1, e1), (rc2, o2, e2) = out
        self.assertEqual(v5((rc1, e1)), (rc2, e2))
        self.assertIn('FAIL', o2)
        l1, l2 = v5(o1).splitlines(), o2.splitlines()
        self.assertEqual(l1[0].replace('(audit_run_v2.py, ', '(audit_run_v3.py, '), l2[0])
        self.assertEqual(l1[1:], l2[1:])

    def test_board_line(self):
        b = self.box
        res = []
        for k, m, pre in (('one', self.old('B'), []), ('two', b.tool('B'), None)):
            hb = os.path.join(b.data, 'hb_' + k)
            w(os.path.join(hb, 'AD1.txt'), '2026-10-29T12:00:00Z AD1 START old line\n')
            if pre is None:
                pre = ['--settings', b.write_settings('S_%s.env' % k, BOARD=hb)]
            else:
                m.CFG['HB'] = hb
            m.CFG['now'] = lambda: datetime.datetime(2026, 10, 29, 14, 1, 2, tzinfo=datetime.timezone.utc)
            got = [call(m, pre + [RUNTAG, 'NOTE', 'a note with its file x.tsv']), call(m, pre + [RUNTAG, 'NOTE', 'another note, same second']),
                   call(m, pre + [RUNTAG, 'NOTE', 'short'])]
            got = [(rc, o.replace(hb, '<BOARD>'), e) for rc, o, e in got]
            res.append((got, snapshot(hb)))
        self.assertEqual(res[0], res[1])

    def test_idea_time(self):
        self.decided_run()
        args = [RUNTAG, 'AD9_20261029', '--launch', 'AD1=2026-10-29T12:50:00Z', '--launch', 'AD9=2026-10-29T12:00:00Z', '--now', '2026-10-29T14:30:00Z']
        self.assertEqual(call(self.old('I'), args), call(self.box.tool('I'), self.s + args))


class T8Commands(Base):
    """the five tools as commands, from a working folder outside the package"""

    def test_commands(self):
        b = self.box
        gj, ej = self.decided_run()
        rc, out, err = cli(b.tree(NEW['D']), self.s + [RUNTAG, 'FLOWX', 'P1', '--grade', gj, '--entry', ej], self.tmp)
        self.assertEqual((rc, err), (0, ''))
        self.assertIn('DECISION FLOWX P1: PASS', out)
        rc, out, err = cli(b.tree(NEW['D']), [RUNTAG, 'FLOWX', 'S1', '--grade', gj], self.tmp)
        self.assertEqual((rc, out), (2, ''))
        self.assertEqual(err, 'REFUSED: --settings <file> IS REQUIRED: the settings file of this machine (<Alarm>/settings/SETTINGS_<MACHINE>.env)\n')
        rc, out, err = cli(b.tree(NEW['A']), self.s + [RUNTAG], self.tmp)
        self.assertEqual((rc, err), (0, ''))
        self.assertIn('A6   SOURCED     PASS', out)
        rc, out, err = cli(b.tree(NEW['A']), [RUNTAG], self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn('USAGE audit_run_v3.py --settings', err)
        rc, out, err = cli(b.tree(NEW['B']), self.s + [RUNTAG, 'NOTE', 'a note with its file x.tsv'], self.tmp)
        self.assertEqual((rc, err), (0, ''))
        self.assertTrue(out.startswith('POSTED %s ' % os.path.join(b.hb, 'AD1.txt')), out)
        rc, out, err = cli(b.tree(NEW['I']), self.s + [RUNTAG, '--now', '2026-10-29T14:30:00Z'], self.tmp)
        self.assertEqual((rc, err), (0, ''))
        self.assertIn('== AD1_20261029  launch 2026-10-29 12:55:00', out)
        rc, out, err = cli(b.tree(NEW['I']), [RUNTAG], self.tmp)
        self.assertEqual(rc, 2)
        self.assertIn('REFUSED: --settings <file> IS REQUIRED', err)
        gj2, mj = self.forward()
        rc, out, err = cli(b.tree(NEW['F']), self.s + [RUNTAG, 'FWDX', 'S1R', '--month', mj], self.tmp)
        self.assertEqual((rc, err), (0, ''))
        self.assertIn('DECISION FWDX S1R: FORWARD PASS', out)


if __name__ == '__main__':
    if ALARM is None:
        print('RUN FROM AN ALARM PACKAGE: no _tools/settings_v1.py above %s' % HERE, file=sys.stderr)
        sys.exit(2)
    unittest.main(verbosity=1, warnings='ignore')    # as on the command line: edition 1's unclosed files are kept as they were
