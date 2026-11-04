"""test_kit5_tools.py: tests of queue_job_v4.py, decide_v1.py and board_line_v1.py on a sandbox (sim_env.py), including a simulated run of
every filled job template with stub tools. Each refusal test asserts its own message (LEARNINGS_V5 V5-36)."""
import os, sys, json, shutil, tempfile, unittest, importlib.util, datetime, io, contextlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); KIT5 = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sim_env as S

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(KIT5, 'tools', name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

RUNTAG = 'AD1_20261029'

class Base(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='k5sim_')
        self.env = S.build(self.root)
        self.run = S.new_run(self.env, RUNTAG)
        self.Q = load('queue_job_v4'); self.D = load('decide_v1'); self.B = load('board_line_v1')
        e = self.env
        self.Q.CFG.update({'H': e['H'], 'RUNNER': e['runner'], 'ALLOC': [sys.executable, '-B', e['alloc']], 'WDB': e['wdb'],
                           'REG': os.path.join(e['T1'], 'reg_append_v1.py'), 'free_mb': lambda: 200000,
                           'now': lambda: datetime.datetime(2026, 10, 29, 14, 0, tzinfo=datetime.timezone.utc)})
        for k in ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'CLEAN'):
            self.Q.TEMPLATE_SHA[k] = S.sha16(os.path.join(e['H'], 'KIT_V5/jobs/JOB_%s_V5.job.sh.txt' % k))
        self.D.CFG.update({'H': e['H'], 'REG': os.path.join(e['T1'], 'reg_append_v1.py'), 'RSE': os.path.join(e['T1'], 'read_stratentry_v1.py')})
        self.B.CFG.update({'HB': e['hb'], 'now': lambda: datetime.datetime(2026, 10, 29, 14, 1, 2, tzinfo=datetime.timezone.utc)})
        os.makedirs(e['hb'], exist_ok=True)

    def claim(self, idea):
        S.w(os.path.join(self.env['H'], 'runs/IDEAS_CLAIMED/%s_%s.txt' % (RUNTAG, idea)), 'claimed\n')

    def idea(self, idea, vs, lean='FADE', prereg_text='prereg v1\n'):
        self.claim(idea)
        pr = 'ideas/%s/PREREG_%s.md' % (idea, idea); S.w(os.path.join(self.run, pr), prereg_text)
        S.w(os.path.join(self.run, 'ideas/%s/ALARM_CARD.md' % idea), 'card\n')
        for v in vs:
            d = 'ideas/%s/defs/%s.json' % (idea, v); S.w(os.path.join(self.run, d), json.dumps({'id': v, 'window': {'first': '20250901', 'last': '20260531'}}))
            self.reg('VARIANTS', {'idea': idea, 'V': v, 'lean': lean, 'def_rel': d, 'def_sha16': S.sha16(os.path.join(self.run, d)),
                                  'prereg_rel': pr, 'prereg_sha16': S.sha16(os.path.join(self.run, pr)), 'reason': 'first'})

    def reg(self, name, row):
        r = subprocess.run([sys.executable, '-B', os.path.join(self.env['T1'], 'reg_append_v1.py'), self.run, name, '-'], input=json.dumps(row), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def q(self, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.Q.main(list(a))
        return buf.getvalue()

    def refused(self, mod, args, text):
        with self.assertRaises(mod.Refused) as cm:
            with contextlib.redirect_stdout(io.StringIO()):
                mod.main(list(args))
        self.assertIn(text, str(cm.exception))

    def twin(self, out):
        line = [l for l in out.splitlines() if l.startswith('QUEUED')][0]
        return os.path.join(self.run, line.split(' twin ')[1].split(' ')[0])

    def unqueue(self):
        """the fake runner 'finishes' every queued job (moved out of IN) so budgets free up"""
        for i in range(1, 22):
            d = os.path.join(self.env['runner'], 'Q_V%d' % i, 'IN')
            for f in os.listdir(d):
                os.rename(os.path.join(d, f), os.path.join(self.root, f + '.done'))

class TestQueue(Base):
    def test_count_queues_and_runs(self):
        self.claim('FLOWX'); d = 'ideas/FLOWX/defs/C1.json'; S.w(os.path.join(self.run, d), '{"id": "C1", "window": {"first": "20250901", "last": "20260531"}}')
        out = self.q(RUNTAG, 'COUNT', 'FLOWX', 'C1=' + d)
        tw = self.twin(out); body = open(tw).read()
        self.assertNotIn('@@', body); self.assertIn('VS=(C1)', body); self.assertIn('# WRITES_MB: 300', body)
        self.assertTrue(os.path.isfile(os.path.join(self.env['runner'], 'Q_V1/IN', os.path.basename(tw))))
        runs = open(os.path.join(self.run, 'registers/RUNS.tsv')).read().splitlines()
        self.assertEqual(len(runs), 2); self.assertIn('\tCOUNT\tFLOWX\tC1\tQ_V1\t', runs[1])
        r = S.run_job(self.env, tw); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dv = os.path.join(self.run, 'receipts', '%s_COUNT_FLOWX' % os.path.basename(tw).split('_')[0])
        st = open(os.path.join(dv, 'STAGES.tsv')).read()
        self.assertIn('count_C1\t0', st); self.assertIn('\nend\t0', st)
        c = open(os.path.join(dv, 'COUNT_C1.tsv')).read()
        self.assertIn('ALL\t80\t60\t', c)        # 40 stub fires a half; B 1000 s after A (same wave) or 3000 s (new wave)
        self.assertIn('# months with 30 or more waves', c)

    def test_unclaimed_refused(self):
        self.refused(self.Q, [RUNTAG, 'COUNT', 'NOPE', 'C1=ideas/NOPE/defs/C1.json'], 'IDEA NOT CLAIMED')

    def test_bad_names_refused(self):
        self.refused(self.Q, [RUNTAG, 'GRADE', 'flowx', 'V1'], 'BAD IDEA NAME')
        self.claim('FLOWX'); self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'v1'], 'BAD NAME')
        self.refused(self.Q, ['ad1_x', 'GRADE', 'FLOWX', 'V1'], 'BAD RUN TAG')

    def test_short_window_refused(self):
        self.claim('WINX'); d = 'ideas/WINX/defs/W1.json'; S.w(os.path.join(self.run, d), '{"id": "W1", "window": {"first": "20250901", "last": "20251231"}}')
        self.refused(self.Q, [RUNTAG, 'COUNT', 'WINX', 'W1=' + d], 'DEFINITION WINDOW OF W1')

    def test_grade_needs_variants_row(self):
        self.claim('FLOWX'); self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'NOT IN VARIANTS')

    def test_grade_changed_definition_refused(self):
        self.idea('FLOWX', ['V1']); S.w(os.path.join(self.run, 'ideas/FLOWX/defs/V1.json'), '{"id": "changed", "window": {"first": "20250901", "last": "20260531"}}')
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'CHANGED SINCE VARIANTS')

    def test_grade_try_budget_and_no_regrade(self):
        self.idea('FLOWX', ['V1', 'V2', 'V3', 'V4'])
        self.q(RUNTAG, 'GRADE', 'FLOWX', 'V1,V2'); self.unqueue()
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'ALREADY GRADED')
        self.q(RUNTAG, 'GRADE', 'FLOWX', 'V3'); self.unqueue()
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V4'], 'TRY BUDGET')

    def test_job_budget_and_behind(self):
        self.idea('AAA', ['V1']); self.idea('BBB', ['V1']); self.idea('CCC', ['V1']); self.idea('DDD', ['V1'])
        self.q(RUNTAG, 'GRADE', 'AAA', 'V1'); self.q(RUNTAG, 'GRADE', 'BBB', 'V1')
        self.refused(self.Q, [RUNTAG, 'GRADE', 'CCC', 'V1'], 'JOB BUDGET')
        self.refused(self.Q, [RUNTAG, 'GRADE', 'CCC', 'V1', '--behind', '--queue', 'Q_V9'], 'NO JOB OF YOURS TO WAIT BEHIND')
        out = self.q(RUNTAG, 'GRADE', 'CCC', 'V1', '--behind'); self.assertIn('QUEUED Q_V1', out)      # behind its own job, never an empty queue
        self.refused(self.Q, [RUNTAG, 'GRADE', 'DDD', 'V1', '--behind', '--queue', 'Q_V1'], 'JOB BUDGET')

    def test_busy_queue(self):
        S.w(os.path.join(self.env['runner'], 'Q_V1/RUN/20260001_judge_DSK_x.job.sh'), '# other\n')
        self.idea('FLOWX', ['V1'])
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1', '--queue', 'Q_V1'], 'BUSY QUEUE')
        out = self.q(RUNTAG, 'GRADE', 'FLOWX', 'V1'); self.assertIn('QUEUED Q_V2', out)

    def test_quiet_window(self):
        self.idea('FLOWX', ['V1'])
        self.Q.CFG['now'] = lambda: datetime.datetime(2026, 10, 29, 23, 25, tzinfo=datetime.timezone.utc)
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'QUIET WINDOW')
        self.Q.CFG['now'] = lambda: datetime.datetime(2026, 10, 30, 0, 10, tzinfo=datetime.timezone.utc)
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'QUIET WINDOW')

    def test_long_job_before_quiet_window(self):
        self.idea('LATEQ', ['V1', 'V2'])
        self.Q.CFG['now'] = lambda: datetime.datetime(2026, 10, 29, 22, 50, tzinfo=datetime.timezone.utc)
        self.refused(self.Q, [RUNTAG, 'GRADE', 'LATEQ', 'V1,V2'], 'would run into 23:30Z')
        self.Q.CFG['now'] = lambda: datetime.datetime(2026, 10, 29, 22, 40, tzinfo=datetime.timezone.utc)
        self.assertIn('QUEUED', self.q(RUNTAG, 'GRADE', 'LATEQ', 'V1'))

    def test_disk(self):
        self.idea('FLOWX', ['V1']); self.Q.CFG['free_mb'] = lambda: 61000
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'DISK: SCRATCH_DISK free 61000 MB')

    def test_wdblack_not_visible_is_a_note(self):
        self.idea('NOWDB', ['V1']); self.Q.CFG['free_mb'] = lambda: None
        out = self.q(RUNTAG, 'GRADE', 'NOWDB', 'V1'); self.assertIn('SCRATCH_DISK is not visible here', out); self.assertIn('QUEUED', out)

    def test_template_changed(self):
        self.idea('FLOWX', ['V1']); self.Q.TEMPLATE_SHA['GRADE'] = '0000000000000000'
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'TEMPLATE CHANGED')

    def test_registration_failure_queues_nothing(self):
        self.idea('FLOWX', ['V1'])
        p = os.path.join(self.run, 'registers/RUNS.tsv'); open(p, 'w').write('bad\theader\n')
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FLOWX', 'V1'], 'RUNS ROW FAILED, NOTHING QUEUED')
        self.assertEqual(os.listdir(os.path.join(self.env['runner'], 'Q_V1/IN')), [])

    def test_dry_run_claims_nothing(self):
        self.idea('FLOWX', ['V1'])
        out = self.q(RUNTAG, 'GRADE', 'FLOWX', 'V1', '--dry')
        self.assertIn('DRY RUN OK', out); self.assertFalse(os.path.exists(os.path.join(self.root, 'alloc.n')))
        self.assertEqual(open(os.path.join(self.run, 'registers/RUNS.tsv')).read().count('\n'), 1)

class TestFlow(Base):
    def grade(self, idea, vs):
        self.idea(idea, vs)
        out = self.q(RUNTAG, 'GRADE', idea, ','.join(vs)); tw = self.twin(out)
        r = S.run_job(self.env, tw); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.unqueue()
        return os.path.basename(tw).split('_')[0] + '_GRADE_' + idea

    def test_grade_entry_decide_month(self):
        gj = self.grade('FLOWX', ['P1', 'N1', 'S1'])
        dv = os.path.join(self.run, 'receipts', gj); st = open(os.path.join(dv, 'STAGES.tsv')).read()
        for x in ('grade_P1\t0', 'perfire_P1\t0', 'handoff\t0', '\nend\t0'):
            self.assertIn(x, st)
        self.assertTrue(os.path.isfile(os.path.join(dv, 'HANDOFF/REAL_SEALED/REAL_RULES_P1.tsv')))
        self.assertEqual(len(open(os.path.join(dv, 'FIRES.tsv')).read().splitlines()), 3)
        # STOP needs no entry; R1 variants need it
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'FLOWX', 'S1', '--grade', gj, '--write'])
        self.assertIn('FLOWX S1: STOP', out.getvalue())
        self.refused(self.D, [RUNTAG, 'FLOWX', 'P1', '--grade', gj], 'run its ENTRY job first')
        self.refused(self.Q, [RUNTAG, 'ENTRY', 'FLOWX', 'S1', '--from-job', gj], 'NOT PASS: no ENTRY job')
        oe = self.q(RUNTAG, 'ENTRY', 'FLOWX', 'P1,N1', '--from-job', gj); te = self.twin(oe)
        self.assertIn('SRCS=(<SCRATCH>/work_%s/%s/P1_FIRES_V1_LIST.tsv' % (RUNTAG, gj), open(te).read())
        r = S.run_job(self.env, te); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.unqueue()
        ej = os.path.basename(te).split('_')[0] + '_ENTRY_FLOWX'
        est = open(os.path.join(self.run, 'receipts', ej, 'STAGES.tsv')).read()
        self.assertIn('markout_P1\t0', est); self.assertIn('store_N1\t0', est)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'FLOWX', 'P1', '--grade', gj, '--entry', ej, '--write'])
            self.D.main([RUNTAG, 'FLOWX', 'N1', '--grade', gj, '--entry', ej, '--write'])
        o = out.getvalue()
        self.assertIn('FLOWX P1: PASS', o); self.assertIn('FLOWX N1: NEEDS MORE MONTHS', o); self.assertIn('CLEAR CLEAR', o)
        self.assertIn('LEAD 15m +3.63 (t +1.91) 1h +7.47 (t +3.69)', o)
        self.refused(self.D, [RUNTAG, 'FLOWX', 'P1', '--grade', gj, '--entry', ej, '--write'], 'ALREADY IN DECISIONS')
        dec = open(os.path.join(self.run, 'registers/DECISIONS.tsv')).read().splitlines()
        self.assertEqual(len(dec), 4); self.assertEqual(len(dec[1].split('\t')), len(S.HDR['DECISIONS']))
        # forward months: forecasts sealed first
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FLOWX', 'P1', '--from-job', gj], 'NO SEALED FORECAST FOR 2601')
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FLOWX', 'S1', '--from-job', gj], 'NO PASS OR NEEDS MORE MONTHS DECISION')
        fc = 'ideas/FLOWX/FORECAST_FLOWX_P1.md'; S.w(os.path.join(self.run, fc), 'forecast\n')
        for m in ('2601', '2602', '2603', '2604'):
            self.reg('FORECASTS', {'idea': 'FLOWX', 'V': 'P1', 'scope': m, 'gap15_lo': '1', 'gap15_hi': '9', 'gap1h_lo': '2', 'gap1h_hi': '12',
                                   'file_rel': fc, 'file_sha16': S.sha16(os.path.join(self.run, fc)), 'note': 'x'})
        S.w(os.path.join(self.run, fc), 'forecast edited after sealing\n')
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FLOWX', 'P1', '--from-job', gj], 'FORECAST FILE CHANGED SINCE SEALED')
        S.w(os.path.join(self.run, fc), 'forecast\n')
        om = self.q(RUNTAG, 'MONTH', 'FLOWX', 'P1', '--from-job', gj); tm = self.twin(om)
        self.assertIn('P1_2603) echo 1:9,2:12;;', open(tm).read())
        r = S.run_job(self.env, tm); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        mj = os.path.basename(tm).split('_')[0] + '_MONTH_FLOWX'
        mst = open(os.path.join(self.run, 'receipts', mj, 'STAGES.tsv')).read()
        self.assertIn('month_P1_2604\t0', mst); self.assertIn('VERDICT HELD ranges 1:9,2:12', mst)
        self.unqueue(); S.w(os.path.join(self.run, fc), 'forecast changed\n')
        # a changed forecast file is refused (it is not re-run anyway)
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FLOWX', 'P1', '--from-job', gj], 'ALREADY MONTH-GRADED')

    def test_entry_size_from_measured(self):
        gj = self.grade('BIGX', ['P1'])
        fp = os.path.join(self.run, 'receipts', gj, 'FIRES.tsv')
        x = open(fp).read().rstrip('\n').split('\t'); x[1] = '17101'; open(fp, 'w').write('\t'.join(x) + '\n')
        out = self.q(RUNTAG, 'ENTRY', 'BIGX', 'P1', '--from-job', gj, '--dry')
        self.assertIn('WRITES_MB 5400', out)
        self.Q.CFG['RUN_BUDGET_MB'] = 5000
        self.refused(self.Q, [RUNTAG, 'ENTRY', 'BIGX', 'P1', '--from-job', gj, '--dry'], 'DISK BUDGET')

    def test_forward_only(self):
        gj = self.grade('FWDX', ['S1'])
        F = load('decide_forward_v1'); F.CFG.update({'H': self.env['H'], 'REG': os.path.join(self.env['T1'], 'reg_append_v1.py')})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'FWDX', 'S1', '--grade', gj, '--write'])
        self.assertIn('FWDX S1: STOP', out.getvalue())
        s1 = [l.split('\t') for l in open(os.path.join(self.run, 'registers/VARIANTS.tsv')).read().splitlines()]
        hdr = s1[0]; row = dict(zip(hdr, [x for x in s1 if x[1:3] == ['FWDX', 'S1']][-1]))
        card = 'ideas/FWDX/CARD_FWDX_FWD.md'; S.w(os.path.join(self.run, card), 'forward-only card\n')
        def var(v, lean, reason):
            self.reg('VARIANTS', {'idea': 'FWDX', 'V': v, 'lean': lean, 'def_rel': row['def_rel'], 'def_sha16': row['def_sha16'],
                                  'prereg_rel': card, 'prereg_sha16': S.sha16(os.path.join(self.run, card)), 'reason': reason})
        var('S1R', 'FOLLOW', 'FORWARD ONLY OF S1: the other side won Sep-Dec')
        var('S1X', 'FADE', 'FORWARD ONLY OF S1: same side')
        var('S1Y', 'FOLLOW', 'a plain variant')
        fc = 'ideas/FWDX/FORECAST_FWDX_S1R.md'; S.w(os.path.join(self.run, fc), 'forecast\n')
        for v in ('S1R', 'S1X', 'S1Y'):
            for m in ('2601', '2602', '2603', '2604'):
                self.reg('FORECASTS', {'idea': 'FWDX', 'V': v, 'scope': m, 'gap15_lo': '0', 'gap15_hi': '9', 'gap1h_lo': '0', 'gap1h_hi': '9',
                                       'file_rel': fc, 'file_sha16': S.sha16(os.path.join(self.run, fc)), 'note': 'x'})
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FWDX', 'S1R', '--from-job', gj], 'NO PASS OR NEEDS MORE MONTHS DECISION')
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FWDX', 'S1R', '--forward-only'], 'ONLY FOR MONTH')
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FWDX', 'S1X', '--from-job', gj, '--forward-only'], 'SAME LEAN AS S1')
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FWDX', 'S1Y', '--from-job', gj, '--forward-only'], 'MUST START "FORWARD ONLY OF')
        self.refused(self.Q, [RUNTAG, 'MONTH', 'FWDX', 'S1', '--from-job', gj, '--forward-only'], 'ALREADY DECIDED')
        om = self.q(RUNTAG, 'MONTH', 'FWDX', 'S1R', '--from-job', gj, '--forward-only'); tm = self.twin(om)
        self.assertIn('LEANS=(FOLLOW)', open(tm).read())
        r = S.run_job(self.env, tm); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.unqueue()
        mj = os.path.basename(tm).split('_')[0] + '_MONTH_FWDX'
        with self.assertRaises(F.Refused) as cm:
            F.decide(self.run, 'FWDX', 'S1Y', mj)
        self.assertIn('NOT A FORWARD-ONLY VARIANT', str(cm.exception))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            F.main([RUNTAG, 'FWDX', 'S1R', '--month', mj, '--write'])
        o = out.getvalue()
        self.assertIn('FWDX S1R: FORWARD PASS | months read 4, holding 4', o)
        self.assertIn('WRITTEN', o)
        d = [l.split('\t') for l in open(os.path.join(self.run, 'registers/DECISIONS.tsv')).read().splitlines()]
        last = dict(zip(d[0], d[-1]))
        self.assertEqual((last['V'], last['state'], last['grade_job']), ('S1R', 'FORWARD PASS', gj))
        # one month read failing turns it INVALID; a month under 30 waves is NO READ
        md = os.path.join(self.run, 'receipts', mj)
        S.w(os.path.join(md, 'MONTH_READ_S1R_2602.txt'), 'S1R month 2602\n  VERDICT NO READ under 30 waves\n')
        S.w(os.path.join(md, 'MONTH_READ_S1R_2603.txt'), 'S1R month 2603\n  VERDICT WEAKER\n')
        self.assertEqual(F.decide(self.run, 'FWDX', 'S1R', mj)['state'], 'FORWARD STOP')        # 2 hold of 3 read
        S.w(os.path.join(md, 'MONTH_READ_S1R_2604.txt'), 'S1R month 2604\n  VERDICT NO READ under 30 waves\n')
        self.assertEqual(F.decide(self.run, 'FWDX', 'S1R', mj)['state'], 'INSUFFICIENT')        # 2 read
        os.remove(os.path.join(md, 'MONTH_READ_S1R_2601.txt'))
        self.assertEqual(F.decide(self.run, 'FWDX', 'S1R', mj)['state'], 'INVALID')

    def test_no_entry_when_too_big(self):
        gj = self.grade('BIGY', ['P1', 'S1'])
        fp = os.path.join(self.run, 'receipts', gj, 'FIRES.tsv')
        rows = [l.rstrip('\n').split('\t') for l in open(fp)]
        def fires(n):
            for x in rows:
                if x[0] == 'P1':
                    x[1] = str(n)
            open(fp, 'w').write(''.join('\t'.join(x) + '\n' for x in rows))
        self.D.CFG['RUN_BUDGET_MB'] = 10000
        fires(17101)                                                     # 5,400 MB: the ENTRY fits, so it must run
        self.refused(self.D, [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry-too-big'], 'ITS ENTRY FITS (5400 MB for 17101 fires, budget 10000 MB)')
        self.refused(self.D, [RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry', '1_ENTRY_BIGY', '--entry-too-big'], 'TOGETHER')
        self.refused(self.D, [RUNTAG, 'BIGY', 'S1', '--grade', gj, '--entry-too-big'], 'ONLY FOR A VARIANT WITH R1')
        fires(40308)                                                     # 12,300 MB: over the budget
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'BIGY', 'P1', '--grade', gj, '--entry-too-big', '--write'])
            self.D.main([RUNTAG, 'BIGY', 'S1', '--grade', gj, '--write'])
        o = out.getvalue()
        self.assertIn('BIGY P1: NO ENTRY', o); self.assertIn('12300 MB for 40308 fires, over the 10000 MB run budget', o)
        dec = [l.split('\t') for l in open(os.path.join(self.run, 'registers/DECISIONS.tsv')).read().splitlines()[1:]]
        st = {x[2]: x[3] for x in dec}
        self.assertEqual(st.get('P1'), 'NO ENTRY'); self.assertEqual(st.get('S1'), 'STOP')
        self.assertIn('QUEUED', self.q(RUNTAG, 'CLEAN', 'BIGY', gj))               # every variant has a row: the GRADE job can be cleaned
        self.refused(self.Q, [RUNTAG, 'MONTH', 'BIGY', 'P1', '--from-job', gj], 'NO PASS OR NEEDS MORE MONTHS DECISION')

    def test_invalid_and_insufficient(self):
        gj = self.grade('GATEX', ['G1', 'I1'])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'GATEX', 'G1', '--grade', gj]); self.D.main([RUNTAG, 'GATEX', 'I1', '--grade', gj])
        self.assertIn('GATEX G1: INVALID', out.getvalue()); self.assertIn('gate GATE_FAIL', out.getvalue())
        self.assertIn('GATEX I1: INSUFFICIENT', out.getvalue())

    def test_failed_grade_is_invalid_and_no_handoff_row(self):
        gj = self.grade('FAILX', ['P1', 'PFAIL'])
        st = open(os.path.join(self.run, 'receipts', gj, 'STAGES.tsv')).read()
        self.assertIn('grade_PFAIL\t4', st)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.D.main([RUNTAG, 'FAILX', 'PFAIL', '--grade', gj])
        self.assertIn('FAILX PFAIL: INVALID', out.getvalue())

    def test_failed_variant_runs_again(self):
        gj = self.grade('FAILY', ['P1', 'PFAIL'])
        self.assertIn('grade_PFAIL\t4', open(os.path.join(self.run, 'receipts', gj, 'STAGES.tsv')).read())
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FAILY', 'P1'], 'ALREADY GRADED')
        out = self.q(RUNTAG, 'GRADE', 'FAILY', 'PFAIL'); self.assertIn('QUEUED', out)
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FAILY', 'PFAIL'], 'ALREADY GRADED')      # queued again: it counts until it ends
        self.unqueue()
        self.refused(self.Q, [RUNTAG, 'GRADE', 'FAILY', 'PFAIL'], 'ALREADY GRADED')      # never ran, no receipts: still counts

    def test_disk_guard_in_job(self):
        self.idea('DISKX', ['P1'])
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'DISKX', 'P1'))
        r = S.run_job(self.env, tw, {'FREE_MB': '50000'}); self.assertEqual(r.returncode, 7)
        st = open(os.path.join(self.run, 'receipts', os.path.basename(tw).split('_')[0] + '_GRADE_DISKX', 'STAGES.tsv')).read()
        self.assertIn('disk_P1\t7', st); self.assertIn('under 60000: stopped', st); self.assertIn('\nend\t7', st)

    def test_pin_change_stops_job(self):
        self.idea('PINX', ['P1'])
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'PINX', 'P1'))
        S.w(os.path.join(self.run, 'ideas/PINX/PREREG_PINX.md'), 'edited after queueing\n')
        r = S.run_job(self.env, tw); self.assertEqual(r.returncode, 3)
        st = open(os.path.join(self.run, 'receipts', os.path.basename(tw).split('_')[0] + '_GRADE_PINX', 'STAGES.tsv')).read()
        self.assertIn('SHA CHANGED', st)

class TestAudit(TestFlow):
    def audit(self, minutes_later=5):
        A = load('audit_run_v2')
        A.CFG.update({'H': self.env['H'], 'HB': self.env['hb'], 'RUNNER': self.env['runner'], 'DECIDE': os.path.join(KIT5, 'tools', 'decide_v1.py'),
                      'DECIDE_CFG': {'REG': os.path.join(self.env['T1'], 'reg_append_v1.py'), 'RSE': os.path.join(self.env['T1'], 'read_stratentry_v1.py')},
                      'now': lambda: datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes_later)})
        au = A.Audit(RUNTAG); lines, nfail = au.runall()
        return {x[0]: x for x in au.res}, '\n'.join(lines)

    def decided_run(self):
        gj = self.grade('FLOWX', ['S1'])
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'FLOWX', 'S1', '--grade', gj, '--write'])
            self.B.main([RUNTAG, 'START', 'run started with KIT_V5'])
        self.reg('POSTMORTEMS', {'idea': 'FLOWX', 'V': 'S1', 'job': gj, 'scope': 'SEPDEC', 'forecast': 'R1 yes', 'result': 'STOP',
                                 'result_file': 'receipts/%s/HANDOFF/SUMMARY.tsv' % gj, 'result_sha16': 'x', 'why': 'y', 'unexplained': 'none'})
        S.w(os.path.join(self.run, 'ideas/FLOWX/FINDINGS_FLOWX.md'), 'STOP\n')
        return gj

    def test_clean_run_passes(self):
        self.decided_run()
        res, txt = self.audit()
        self.assertEqual([k for k, x in res.items() if x[2] == 'FAIL'], [], txt)

    def test_clean_label_is_not_an_idea_a2(self):
        gj = self.decided_run()
        out = self.q(RUNTAG, 'CLEAN', 'GIVEN', gj); self.assertIn('QUEUED', out)
        self.assertFalse(os.path.isfile(os.path.join(self.env['H'], 'runs/IDEAS_CLAIMED/%s_GIVEN.txt' % RUNTAG)))
        res, txt = self.audit(); self.assertEqual(res['A2'][2], 'PASS', txt)

    def test_tampered_decision_fails_a6(self):
        self.decided_run()
        p = os.path.join(self.run, 'registers/DECISIONS.tsv'); t = open(p).read()
        open(p, 'w').write(t.replace('\tSTOP\t', '\tPASS\t', 1))
        res, txt = self.audit(); self.assertEqual(res['A6'][2], 'FAIL', txt); self.assertIn('state is', txt)

    def test_unread_job_fails_a7(self):
        self.idea('LATEX', ['S1'])
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'LATEX', 'S1')); S.run_job(self.env, tw)
        res, txt = self.audit(minutes_later=45); self.assertEqual(res['A7'][2], 'FAIL', txt); self.assertIn('NOT READ', txt)

    def test_disk_over_declared_fails_a8(self):
        gj = self.decided_run()
        p = os.path.join(self.run, 'receipts', gj, 'DISK.tsv'); open(p, 'w').write('du_mb_W\t99999\nfree_mb_end\t1\n')
        res, txt = self.audit(); self.assertEqual(res['A8'][2], 'FAIL', txt)

    def test_words_board_claim_jobs(self):
        self.decided_run()
        S.w(os.path.join(self.run, 'ideas/FLOWX/IDEA_CARD.md'), 'the reading does not exist\n')
        with open(os.path.join(self.env['hb'], 'AD1.txt'), 'a') as f:
            f.write('2026-10-29T14:00:00Z AD1 NOTE ' + 'x' * 600 + '\n')
        S.w(os.path.join(self.run, 'jobs/20260001_judge_AD1_GRADE_HAND.job.sh'), '# made by hand\n')
        os.rename(os.path.join(self.env['H'], 'runs/IDEAS_CLAIMED/%s_FLOWX.txt' % RUNTAG), os.path.join(self.root, 'claim.moved'))
        res, txt = self.audit()
        for k in ('A2', 'A11', 'A12', 'A16'):
            self.assertEqual(res[k][2], 'FAIL', k + txt)

    def test_stuck_needs_problem_and_board(self):
        self.idea('STUCKX', ['PFAIL1', 'PFAIL2'])
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'STUCKX', 'PFAIL1')); S.run_job(self.env, tw); self.unqueue()
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'STUCKX', 'PFAIL2')); S.run_job(self.env, tw); self.unqueue()
        res, txt = self.audit(); self.assertEqual(res['A13'][2], 'FAIL', txt)
        self.reg('PROBLEMS', {'kind': 'TOOL', 'where': 'STUCKX grade', 'what_is_wrong': 'failed twice', 'evidence': 'x', 'severity': 'HIGH',
                              'action': 'stopped', 'proposed_fix': 'y', 'reported_to_lead': 'yes'})
        with contextlib.redirect_stdout(io.StringIO()):
            self.B.main([RUNTAG, 'STUCK', 'STUCKX grade failed twice, see PROBLEMS'])
        res, txt = self.audit(); self.assertEqual(res['A13'][2], 'PASS', txt)

    def test_budget_and_sealed(self):
        self.idea('SEALX', ['S1'])
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'SEALX', 'S1'))
        S.w(os.path.join(self.run, 'ideas/SEALX/PREREG_SEALX.md'), 'edited after the job\n')
        res, txt = self.audit(); self.assertEqual(res['A3'][2], 'FAIL', txt)

class TestClean(TestFlow):
    def pm(self, idea, v, job):
        self.reg('POSTMORTEMS', {'idea': idea, 'V': v, 'job': job, 'scope': 'X', 'forecast': 'f', 'result': 'r', 'result_file': 'x',
                                 'result_sha16': 'x', 'why': 'w', 'unexplained': 'none'})

    def test_clean_after_decisions_keeps_proof(self):
        gj = self.grade('CLNX', ['P1', 'S1'])
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'CLNX', 'S1', '--grade', gj, '--write'])
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'CLNX', gj], 'NOT DECIDED YET')
        te = self.twin(self.q(RUNTAG, 'ENTRY', 'CLNX', 'P1', '--from-job', gj))
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'CLNX', gj], 'STILL NEEDED')
        r = S.run_job(self.env, te); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.unqueue()
        ej = os.path.basename(te).split('_')[0] + '_ENTRY_CLNX'
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'CLNX', 'P1', '--grade', gj, '--entry', ej, '--write'])
        w = os.path.join(self.env['wdb'], 'judge_scratch/work_%s/%s' % (RUNTAG, gj)); self.assertTrue(os.path.isdir(w))
        chain = os.path.join(self.env['wdb'], 'judge_scratch/work_TOOLTRIAL/chain/ALM_AD1_P1_SD_20250910_20251231_STAMP1'); self.assertTrue(os.path.isdir(chain))
        tc = self.twin(self.q(RUNTAG, 'CLEAN', 'CLNX', '%s,%s' % (gj, ej)))
        r = S.run_job(self.env, tc); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.unqueue()
        self.assertFalse(os.path.exists(w)); self.assertTrue(os.path.isdir(chain))     # store places are protected: left for DSK
        dg = os.path.join(self.run, 'receipts', gj)
        for v in ('P1', 'S1'):
            fl = os.path.join(dg, '%s_FIRES_V1_LIST.tsv' % v); self.assertTrue(os.path.isfile(fl))
        self.assertTrue(os.path.isfile(os.path.join(dg, 'CLEANED_BY.txt')))
        cj = os.path.basename(tc).split('_')[0] + '_CLEAN_CLNX'
        cl = open(os.path.join(self.run, 'receipts', cj, 'CLEANED.tsv')).read()
        self.assertIn('REMOVED', cl); self.assertIn('LEFT FOR DSK', cl)
        full = os.path.join(self.env['wdb'], 'judge_scratch/work_ALARMLIB/i2g_v3_2/full_ALM_AD1_P1_SD_20250910_20251231_STAMP1')
        self.assertTrue(os.path.isdir(full)); self.assertIn(full + '\t', cl); self.assertIn(chain + '\t', cl)
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'CLNX', gj], 'IS ALREADY CLEANED')
        A = load('audit_run_v2')
        A.CFG.update({'H': self.env['H'], 'HB': self.env['hb'], 'RUNNER': self.env['runner'], 'DECIDE': os.path.join(KIT5, 'tools', 'decide_v1.py'),
                      'DECIDE_CFG': {'REG': os.path.join(self.env['T1'], 'reg_append_v1.py'), 'RSE': os.path.join(self.env['T1'], 'read_stratentry_v1.py')}})
        au = A.Audit(RUNTAG); au.runall(); res = {x[0]: x for x in au.res}
        self.assertEqual(res['A17'][2], 'PASS', res['A17']); self.assertEqual(res['A6'][2], 'PASS', res['A6'])

    def test_count_needs_postmortem_and_foreign_store_refused(self):
        self.claim('CNTX'); d = 'ideas/CNTX/defs/C1.json'
        S.w(os.path.join(self.run, d), json.dumps({'id': 'C1', 'window': {'first': '20250901', 'last': '20260531'}}))
        tw = self.twin(self.q(RUNTAG, 'COUNT', 'CNTX', 'C1=' + d)); S.run_job(self.env, tw); self.unqueue()
        cj = os.path.basename(tw).split('_')[0] + '_COUNT_CNTX'
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'CNTX', cj], 'NO POSTMORTEMS ROW')
        self.pm('CNTX', 'C1', cj)
        out = self.q(RUNTAG, 'CLEAN', 'CNTX', cj); self.assertIn('QUEUED', out)
        # a store place that is not ours is refused by the tool inside the job: nothing removed
        gj = self.grade('FORX', ['P1'])
        te = self.twin(self.q(RUNTAG, 'ENTRY', 'FORX', 'P1', '--from-job', gj)); S.run_job(self.env, te); self.unqueue()
        ej = os.path.basename(te).split('_')[0] + '_ENTRY_FORX'
        sp = os.path.join(self.run, 'receipts', ej, 'P1/STORE_PLACES.tsv'); t = open(sp).read()
        open(sp, 'w').write(t.replace('ALM_AD1_P1_SD', 'ALM_DSK_P1_SD'))
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'FORX', 'P1', '--grade', gj, '--entry', ej, '--write'])
        tc = self.twin(self.q(RUNTAG, 'CLEAN', 'FORX', ej))
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'FORX', ej], 'ALREADY IN A QUEUED CLEAN JOB')
        r = S.run_job(self.env, tc); self.unqueue()
        cj2 = os.path.basename(tc).split('_')[0] + '_CLEAN_FORX'
        st = open(os.path.join(self.run, 'receipts', cj2, 'STAGES.tsv')).read()
        self.assertIn('dry\t2', st); self.assertIn('STORE PLACE NOT OURS', open(os.path.join(self.run, 'receipts', cj2, 'DRY.txt')).read())
        self.assertTrue(os.path.isdir(os.path.join(self.env['wdb'], 'judge_scratch/work_%s/%s' % (RUNTAG, ej))))
        open(sp, 'w').write(t)                                         # the row repaired: a failed CLEAN may be queued again
        self.assertIn('QUEUED', self.q(RUNTAG, 'CLEAN', 'FORX', ej))

    def test_clean_a_failed_job(self):
        gj = self.grade('FAILC', ['S1', 'PFAIL'])
        self.refused(self.Q, [RUNTAG, 'CLEAN', 'FAILC', gj], "NOT DECIDED YET ['S1']")       # the good variant must be decided first
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'FAILC', 'S1', '--grade', gj, '--write'])
        out = self.q(RUNTAG, 'CLEAN', 'FAILC', gj); self.assertIn('QUEUED', out)            # PFAIL failed: nothing to decide
        g2 = self.grade('FAILD', ['PFAIL'])
        self.unqueue()
        out = self.q(RUNTAG, 'CLEAN', 'FAILD', g2); self.assertIn('QUEUED', out)            # only failed variants

    def test_changed_fire_list_blocks_clean(self):
        gj = self.grade('CHGX', ['S1'])
        with contextlib.redirect_stdout(io.StringIO()):
            self.D.main([RUNTAG, 'CHGX', 'S1', '--grade', gj, '--write'])
        fl = os.path.join(self.env['wdb'], 'judge_scratch/work_%s/%s/S1_FIRES_V1_LIST.tsv' % (RUNTAG, gj))
        with open(fl, 'a') as f:
            f.write('XRP\t1760000001\t1\n')
        tc = self.twin(self.q(RUNTAG, 'CLEAN', 'CHGX', gj)); S.run_job(self.env, tc)
        cj = os.path.basename(tc).split('_')[0] + '_CLEAN_CHGX'
        self.assertIn('FIRE LIST CHANGED', open(os.path.join(self.run, 'receipts', cj, 'DRY.txt')).read())
        self.assertTrue(os.path.isfile(fl))

    def test_disk_budget(self):
        self.Q.CFG['RUN_BUDGET_MB'] = 5000
        self.idea('BUDX', ['P1', 'P2', 'P3'])
        self.refused(self.Q, [RUNTAG, 'GRADE', 'BUDX', 'P1,P2,P3'], 'DISK BUDGET')
        tw = self.twin(self.q(RUNTAG, 'GRADE', 'BUDX', 'P1,P2'))      # 3,600 MB declared while it runs
        self.unqueue()
        self.refused(self.Q, [RUNTAG, 'GRADE', 'BUDX', 'P3'], 'DISK BUDGET')
        S.run_job(self.env, tw)                                          # finished: measured du (tiny) replaces the declaration
        out = self.q(RUNTAG, 'GRADE', 'BUDX', 'P3'); self.assertIn('QUEUED', out)

class TestBoard(Base):
    def test_post_and_twin(self):
        p = os.path.join(self.env['hb'], 'AD1.txt'); S.w(p, 'old line\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.B.main([RUNTAG, 'START', 'run started, kit KIT_V5 skill alarm-design-v5'])
        self.assertTrue(open(p).read().endswith('2026-10-29T14:01:02Z AD1 START run started, kit KIT_V5 skill alarm-design-v5\n'))
        self.assertTrue(os.path.isfile(p + '.pre_%s_20261029T140102Z' % RUNTAG))

    def test_two_lines_in_one_second(self):
        p = os.path.join(self.env['hb'], 'AD1.txt'); S.w(p, 'old line\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.B.main([RUNTAG, 'NOTE', 'first line of this second'])
            self.B.main([RUNTAG, 'NOTE', 'second line of this second'])
        body = open(p).read()
        self.assertIn('AD1 NOTE first line of this second', body); self.assertIn('AD1 NOTE second line of this second', body)
        self.assertTrue(os.path.isfile(p + '.pre_%s_20261029T140102Z' % RUNTAG)); self.assertTrue(os.path.isfile(p + '.pre_%s_20261029T140102Z_2' % RUNTAG))

    def test_refusals(self):
        self.refused(self.B, [RUNTAG, 'HELLO', 'some text here'], 'KIND')
        self.refused(self.B, [RUNTAG, 'NOTE', 'x' * 560], 'CHARACTERS')
        self.refused(self.B, [RUNTAG, 'NOTE', 'a \u2014 b long enough'], 'EM DASH')
        self.refused(self.B, [RUNTAG, 'NOTE', 'short'], 'TOO SHORT')

if __name__ == '__main__':
    unittest.main(verbosity=1)
