#!/usr/bin/env python3
"""test_menu_gate_v1.py (SCOUT, 3 Nov 2026; playground PG20261103_menu_gate; TEST, NOT REVIEWED): the menu gate at SEAL (menu_gate_v1,
queue_job_v16, decide_v6). Seconds; planted worlds in temp folders (the World of test_v1_21_fixes.py, loaded from the install, never
copied); the real METRIC_MENU_V2.tsv and the real true_gate_v1 reader of the install; the real DESKA04 sealed definition, card, reason
and TRUE label frozen in data_menu_gate_v1/; no market data; the install is only read.

  python3 -B test_menu_gate_v1.py               (expected: every test passes)
  MENU_FIX=<folder>                             the folder holding the three new tools (default: KIT_V5/tools of this package); the
                                                mutants set it to a mutant copy
  ALARM_BASE=<an installed Alarm package>       the package the world copies from (default: the one holding this file)
Classes: G the gate (planted CAUTION refused, its exception passes and is recorded, a PROVEN CLOCK code passes, ...), Q the queue,
D the decision, REAL the DESKA04 seal, KEEP what must stay equal (FDAOI-first: v15's job text and decide_v5's output and row)."""
import hashlib, importlib.util, json, os, re, shutil, subprocess, sys, tempfile, unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
INSTALL = os.environ.get('ALARM_BASE') or PKG
KIT = 'Agentic/tree/ALARM_DESIGN/KIT_V5'
FIX = os.environ.get('MENU_FIX') or os.path.join(PKG, KIT, 'tools')
DATA = os.path.join(HERE, 'data_menu_gate_v1')
MENU = os.path.join(INSTALL, KIT, 'METRIC_MENU_V2.tsv')
TG1 = os.path.join(INSTALL, '03_Grading/tree/tools/true_gate/true_gate_v1.py')
NEW = ('menu_gate_v1.py', 'queue_job_v16.py', 'decide_v6.py')
s16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
dg = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


V121 = load(os.path.join(INSTALL, KIT, 'tests/test_v1_21_fixes.py'), 'v121_world')
RUN, IDEA, GRADE, wr = V121.RUN, V121.IDEA, V121.GRADE, V121.wr
MG = load(os.path.join(FIX, 'menu_gate_v1.py'), 'mg_t')
READER = MG.Reader(TG1)                              # the install's pinned reader, passed explicitly (no environment variable can)


def dfn(*codes, extra=None):
    """a definition reading these codes (one raw input and one condition each), window Sep 2025 to Apr 2026"""
    d = {'window': {'first': '20250901', 'last': '20260430'}, 'grid_s': 60,
         'inputs': {'x%d' % i: {'op': 'raw', 'code': c} for i, c in enumerate(codes)},
         'conditions': [{'name': 'c%d' % i, 'lhs': 'x%d' % i, 'cmp': '>', 'rhs': 0, 'role': 'claim'} for i in range(len(codes))],
         'fire': {'onset': True, 'refractory_s': 1800, 'side': {'input': 'x0', 'sign': 1}}}
    d.update(extra or {})
    return d


def label(code):
    lab = {'kind': 'metric_test', 'code': code, 'when': 'present', 'end_s': 3600, 'test': 'falling', 'change': 'pct', 'thr': 0.5, 'max_age_s': 300}
    return lab, dict(lab, test='rising')


class World(V121.World):
    """the V1_21 world, the three new tools and the real menu beside queue_job_v15 and decide_v5, a run sealed on a chosen definition"""
    def __init__(self):
        V121.World.__init__(self)
        for n in NEW:
            shutil.copyfile(os.path.join(FIX, n), os.path.join(self.A, KIT, 'tools', n))
        shutil.copyfile(MENU, os.path.join(self.A, KIT, 'METRIC_MENU_V2.tsv'))
        self.TG1 = os.path.join(self.A, '03_Grading/tree/tools/true_gate/true_gate_v1.py')

    def plant(self, d, card_extra='', reason='r', lab_code='E2.S02'):
        """plant_run of the V1_21 world with this definition, card lines, VARIANTS reason and TRUE label code"""
        V121.LABEL, V121.MIRROR = label(lab_code)
        self.plant_run()
        shutil.copyfile(TG1, self.TG1)                   # the real reader in place of the world's stub (pinned in the TRUE job like the stub was)
        dfp = os.path.join(self.Rn, 'ideas', IDEA, 'defs/V1.json'); os.rename(dfp, dfp + '.planted_aside'); wr(dfp, json.dumps(d))
        card = os.path.join(self.Rn, 'ideas', IDEA, 'CARD_%s.md' % IDEA)
        wr(card, 'card\n1b `true_label=%s true_mirror=%s`\n%s' % (dg(V121.LABEL), dg(V121.MIRROR), card_extra))
        reg = os.path.join(self.Rn, 'registers/VARIANTS.tsv'); t = open(reg).read().split('\n')
        self.var = dict(self.var, def_sha16=s16(dfp), prereg_sha16=s16(card), reason=reason)
        h = t[0].split('\t'); t[1] = '\t'.join(str(self.var.get(k, '-')) for k in h); open(reg, 'w').write('\n'.join(t))
        tw = [l for l in os.listdir(os.path.join(self.Rn, 'jobs'))][0]; p = os.path.join(self.Rn, 'jobs', tw)
        tw = open(p).read().replace('DSHAS=(%s)' % self.claim['def_sha16'], 'DSHAS=(%s)' % s16(dfp)); open(p, 'w').write(tw)
        reg = os.path.join(self.Rn, 'registers/RUNS.tsv'); t = open(reg).read().split('\n'); h = t[0].split('\t')
        row = dict(zip(h, t[1].split('\t'))); row.update(job_sha16=s16(p), prereg_sha16=s16(card)); t[1] = '\t'.join(row[k] for k in h); open(reg, 'w').write('\n'.join(t))
        self.claim.update(def_sha16=s16(dfp), label=V121.LABEL, mirror=V121.MIRROR, activity={'code': lab_code, 'mode': 'level', 'max_age_s': 300})
        self.write_claim()
        return self

    def q(self, tool, *a):
        p = os.path.join(self.A, KIT, 'tools', tool)
        return subprocess.run([sys.executable, '-B', p, '--settings', self.S, RUN, 'TRUE', IDEA, 'V1=' + self.claim_rel, '--from-job', GRADE] + list(a), capture_output=True, text=True)


def gate(d, card='card\n', reason=None, claim=None):
    t = tempfile.mkdtemp(prefix='mg_'); dp, cp = os.path.join(t, 'V1.json'), os.path.join(t, 'CARD.md')
    wr(dp, json.dumps(d)); wr(cp, card); clp = None
    if claim is not None:
        clp = os.path.join(t, 'claim.json'); wr(clp, json.dumps(claim))
    return MG.gate(dp, cp, clp, reason, menu=MG.read_menu(MENU), reader=READER)


def menu_row(code):
    return MG.read_menu(MENU)[code]


class G_Gate(unittest.TestCase):
    def test_menu_rows_the_tests_rely_on(self):
        self.assertEqual((menu_row('E1.S04')['menu_status'], menu_row('E1.S04')['pickable']), ('CAUTION', 'NO'))
        self.assertEqual((menu_row('E1.S09')['menu_status'], menu_row('E1.S09')['pickable']), ('UNPROVEN', 'NO'))
        self.assertEqual((menu_row('E1.S01')['kind'], menu_row('E1.S01')['menu_status'], menu_row('E1.S01')['pickable']), ('CLOCK', 'PROVEN', 'YES'))

    def test_a_planted_caution_code_is_refused(self):
        with self.assertRaises(MG.Refused) as c:
            gate(dfn('E1.S01', 'E1.S04'))
        self.assertEqual(c.exception.code, 'MENU_NOT_PICKABLE'); self.assertIn('E1.S04 (CAUTION', str(c.exception))

    def test_the_same_code_with_an_exception_passes_and_is_recorded(self):
        card = 'card\n- MENU EXCEPTION E1.S04: the idea scales the paid rate by the coin interval\n'
        g = gate(dfn('E1.S01', 'E1.S04'), card, reason='as given; MENU EXCEPTION E1.S04')
        self.assertEqual(g['excepted'], {'E1.S04': ('CAUTION', 'the idea scales the paid rate by the coin interval')})
        self.assertIn('MENU EXCEPTION E1.S04 (CAUTION): the idea scales the paid rate by the coin interval', MG.lines(g, 'X V1'))
        self.assertTrue(g['recorded_checked'])

    def test_an_exception_not_recorded_in_variants_is_refused(self):
        card = 'MENU EXCEPTION E1.S04: the idea scales the paid rate by the coin interval\n'
        with self.assertRaises(MG.Refused) as c:
            gate(dfn('E1.S04'), card, reason='as given')
        self.assertEqual(c.exception.code, 'MENU_EXCEPTION_NOT_RECORDED')
        gate(dfn('E1.S04'), card)                                       # before the VARIANTS row (no reason): not asked yet

    def test_a_proven_clock_code_passes(self):
        g = gate(dfn('E1.S01'), reason='r'); self.assertEqual(g['codes'], [('E1.S01', 'definition', 'PROVEN', 'YES')]); self.assertEqual(g['excepted'], {})

    def test_every_pickable_no_status_is_refused(self):
        m = MG.read_menu(MENU)
        for st in ('CAUTION', 'UNPROVEN'):
            code = sorted(c for c, r in m.items() if r['menu_status'] == st and r['pickable'] == 'NO')[0]
            with self.assertRaises(MG.Refused):
                gate(dfn(code))

    def test_a_reason_is_needed_and_one_line_per_code(self):
        for card in ('MENU EXCEPTION E1.S04: short\n', 'MENU EXCEPTION E1.S04:\n',
                     'MENU EXCEPTION E1.S04: a long enough reason here\nMENU EXCEPTION E1.S04: a second long enough reason\n'):
            with self.assertRaises(MG.Refused) as c:
                gate(dfn('E1.S04'), card)
            self.assertEqual(c.exception.code, 'BAD_EXCEPTION', card)

    def test_an_exception_for_another_code_does_not_cover(self):
        with self.assertRaises(MG.Refused) as c:
            gate(dfn('E1.S09'), 'MENU EXCEPTION E1.S04: the idea scales the paid rate\n', reason='MENU EXCEPTION E1.S04')
        self.assertIn('E1.S09', str(c.exception))

    def test_every_place_a_definition_reads_counts(self):
        base = dfn('E1.S01')
        for extra in ({'inputs': dict(base['inputs'], m={'op': 'market', 'code': 'E1.S04'})},
                      {'mirror': {'E1.S04': '-'}}, {'mirror': {'E1.S01': 'E1.S09'}}):
            with self.assertRaises(MG.Refused, msg=extra):
                gate(dfn('E1.S01', extra=extra))

    def test_an_unknown_op_is_refused(self):
        d = dfn('E1.S01'); d['inputs']['z'] = {'op': 'magic', 'of': 'x0'}
        with self.assertRaises(MG.Refused) as c:
            gate(d)
        self.assertEqual(c.exception.code, 'UNREADABLE_DEF')

    def test_a_true_label_on_a_pickable_no_code_is_refused(self):
        lab, mir = label('E2.S01')
        with self.assertRaises(MG.Refused) as c:
            gate(dfn('E1.S01'), claim={'label': lab, 'mirror': mir, 'activity': {'code': 'E2.S01'}})
        self.assertIn('read by the label', str(c.exception))
        lab, mir = label('E2.S02')
        g = gate(dfn('E1.S01'), claim={'label': lab, 'mirror': mir, 'activity': {'code': 'E2.S02'}})
        self.assertIn(('E2.S02', 'label', 'PROVEN', 'YES'), g['codes'])

    def test_a_threshold_code_and_code_by_side_count(self):
        lab = {'kind': 'metric_test', 'code_by_side': {'1': 'E2.S02', '-1': 'E2.S01'}, 'when': 'present', 'end_s': 60, 'test': '>=', 'thr': 1, 'max_age_s': 60}
        with self.assertRaises(MG.Refused):
            gate(dfn('E1.S01'), claim={'label': lab, 'mirror': lab})
        lab = {'kind': 'metric_test', 'code': 'E2.S02', 'when': 'present', 'end_s': 60, 'test': '>=', 'thr_code': {'code': 'E2.S03', 'scale': 1}, 'max_age_s': 60}
        with self.assertRaises(MG.Refused):
            gate(dfn('E1.S01'), claim={'label': lab, 'mirror': lab})

    def test_a_code_off_the_menu_is_a_note(self):
        g = gate(dfn('E1.S01', 'ZZ.S99'), reason='r'); self.assertEqual(g['not_on_menu'], ['ZZ.S99'])
        self.assertTrue(any(l.startswith('MENU NOTE ZZ.S99: NOT ON MENU') for l in MG.lines(g, 'x')))

    def test_a_changed_menu_is_refused(self):
        t = tempfile.mkdtemp(prefix='mgm_'); p = os.path.join(t, 'M.tsv'); wr(p, open(MENU).read().replace('\tCAUTION\tNO\t', '\tPROVEN\tYES\t', 1))
        with self.assertRaises(MG.Refused) as c:
            MG.read_menu(p)
        self.assertEqual(c.exception.code, 'MENU_CHANGED')
        self.assertEqual(s16(MENU), MG.MENU_SHA)

    def test_the_seal_time_command(self):
        t = tempfile.mkdtemp(prefix='mgc_'); dp, cp = os.path.join(t, 'V1.json'), os.path.join(t, 'CARD.md')
        wr(dp, json.dumps(dfn('E1.S04'))); wr(cp, 'card\n')
        w = World(); shutil.copyfile(TG1, w.TG1); tool = os.path.join(w.A, KIT, 'tools/menu_gate_v1.py')
        r = subprocess.run([sys.executable, '-B', tool, 'check', dp, cp], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn('REFUSED MENU_NOT_PICKABLE', r.stderr); self.assertNotIn('Traceback', r.stderr)
        wr(cp, 'card\nMENU EXCEPTION E1.S04: the idea needs the interval in hours\n')
        r = subprocess.run([sys.executable, '-B', tool, 'check', dp, cp], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn('VARIANTS reason must name: MENU EXCEPTION E1.S04', r.stdout)


    def test_malformed_shapes_are_refusals_never_tracebacks(self):
        for claim in ([], {'label': []}, {'label': {'code_by_side': [1]}}, {'label': {'code': 3, 'kind': 'metric_test'}}, {'activity': 'E2.S02'}):
            with self.assertRaises(MG.Refused, msg=claim) as c:
                gate(dfn('E1.S01'), claim=claim)
            self.assertEqual(c.exception.code, 'UNREADABLE_CLAIM', claim)
        for d in ([], {'inputs': {'x': {'op': 'raw', 'code': 5}}}):
            with self.assertRaises(MG.Refused, msg=d) as c:
                gate(d)
            self.assertEqual(c.exception.code, 'UNREADABLE_DEF', d)
        with self.assertRaises(MG.Refused):
            gate(dfn('E1.S01'), reason=['MENU EXCEPTION E1.S04'])

    def test_a_changed_reader_is_refused(self):
        t = tempfile.mkdtemp(prefix='mgr_'); p = os.path.join(t, 'true_gate_v1.py'); wr(p, open(TG1).read() + '\n# changed\n')
        with self.assertRaises(MG.Refused) as c:
            MG.Reader(p)
        self.assertEqual(c.exception.code, 'READER_CHANGED'); self.assertEqual(s16(TG1), MG.TG1_SHA)


class Q_Queue(unittest.TestCase):
    def test_an_inherited_reader_or_package_setting_is_ignored(self):
        w = World().plant(dfn('E1.S01', 'E1.S04'))                                    # GPT V12115-TOOL item 1, on the public queue
        fake = os.path.join(w.t, 'fake_tg.py'); wr(fake, 'def collect_reads(d):\n    return {"codes": set()}\ndef label_codes(l):\n    return set()\n')
        env = dict(os.environ, MENU_GATE_TG=fake, MENU_GATE_PKG=w.t)
        p = os.path.join(w.A, KIT, 'tools', 'queue_job_v16.py')
        r = subprocess.run([sys.executable, '-B', p, '--settings', w.S, RUN, 'TRUE', IDEA, 'V1=' + w.claim_rel, '--from-job', GRADE, '--dry'], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn('MENU_NOT_PICKABLE: E1.S04', r.stderr)
        self.assertNotIn('os.environ', open(os.path.join(FIX, 'menu_gate_v1.py')).read())

    def test_a_changed_reader_in_the_package_refuses_the_queue(self):
        w = World().plant(dfn('E1.S01')); open(w.TG1, 'a').write('\n# changed\n')
        r = w.q('queue_job_v16.py', '--dry'); self.assertEqual(r.returncode, 2); self.assertIn('MENU GATE V1: READER_CHANGED', r.stderr)

    def test_a_malformed_claim_refuses_grade_cleanly(self):
        w = World().plant(dfn('E1.S01')); wr(os.path.join(w.Rn, 'ideas', IDEA, 'TRUE_V1_extra.json'), '[]')
        Q = load(os.path.join(w.A, KIT, 'tools/queue_job_v16.py'), 'q16_bad_%d' % id(self))
        Q._plan15 = lambda run, kind, idea, items, fj, fo=False: ('AB1', ['V1'], '', {}, {})
        with self.assertRaises(Q.Q.Refused) as c:
            Q.plan(w.Rn, 'GRADE', IDEA, 'V1', None)
        self.assertIn('UNREADABLE_CLAIM', str(c.exception))

    def test_a_sealed_caution_code_is_refused_before_any_job(self):
        w = World().plant(dfn('E1.S01', 'E1.S04'))
        for a in (('--dry',), ()):
            r = w.q('queue_job_v16.py', *a); self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            self.assertIn('REFUSED: MENU GATE V1: MENU_NOT_PICKABLE: E1.S04 (CAUTION', r.stderr); self.assertIn('NEXT: a code your definition', r.stderr)
        self.assertEqual([x for x in w.rows('RUNS') if x['kind'] == 'TRUE'], []); self.assertEqual(os.listdir(os.path.join(w.Rn, 'jobs')), [os.listdir(os.path.join(w.Rn, 'jobs'))[0]])
        self.assertFalse(os.path.exists(w.alloc + '.n'))                                   # no number claimed

    def test_with_its_exception_it_queues_and_prints_it(self):
        w = World().plant(dfn('E1.S01', 'E1.S04'), 'MENU EXCEPTION E1.S04: the idea scales the paid rate by the interval\n', 'as given; MENU EXCEPTION E1.S04')
        r = w.q('queue_job_v16.py'); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('MENU EXCEPTION E1.S04 (CAUTION): the idea scales the paid rate by the interval', r.stdout); self.assertIn('QUEUED', r.stdout)
        self.assertEqual(len([x for x in w.rows('RUNS') if x['kind'] == 'TRUE']), 1)

    def test_a_pickable_no_true_label_is_refused(self):
        w = World().plant(dfn('E1.S01'), lab_code='E2.S05')
        r = w.q('queue_job_v16.py', '--dry'); self.assertEqual(r.returncode, 2); self.assertIn('read by the label', r.stderr); self.assertIn('(claim ideas/', r.stderr)

    def test_a_proven_clock_code_queues(self):
        w = World().plant(dfn('E1.S01'))
        r = w.q('queue_job_v16.py', '--dry'); self.assertEqual(r.returncode, 0, r.stderr); self.assertIn('MENU GATE %s V1 + TRUE_V1_HLOIFALL.json: OK' % IDEA, r.stdout)

    def test_grade_reads_the_claims_written_and_count_is_not_gated(self):
        w = World().plant(dfn('E1.S01'), lab_code='E2.S05')
        Q = load(os.path.join(w.A, KIT, 'tools/queue_job_v16.py'), 'q16_unit_%d' % id(self))
        Q._plan15 = lambda run, kind, idea, items, fj, fo=False: ('AB1', ['V1'], '', {}, {})
        with self.assertRaises(Q.Q.Refused) as c:
            Q.plan(w.Rn, 'GRADE', IDEA, 'V1', None)
        self.assertIn('read by the label', str(c.exception))
        w2 = World().plant(dfn('E1.S04'))
        self.assertEqual(Q.plan(w2.Rn, 'COUNT', IDEA, 'V1=x', None)[1], ['V1'])          # COUNT: no seal yet, not gated
        with self.assertRaises(Q.Q.Refused):
            Q.plan(w2.Rn, 'ENTRY', IDEA, 'V1', None)

    def test_a_changed_v15_is_refused(self):
        w = World().plant(dfn('E1.S01')); p = os.path.join(w.A, KIT, 'tools/queue_job_v15.py'); open(p, 'a').write('\n# changed\n')
        r = w.q('queue_job_v16.py', '--dry'); self.assertEqual(r.returncode, 2); self.assertIn('queue_job_v15.py MISSING OR CHANGED', r.stderr)

    def test_usage_names_v16(self):
        w = World(); r = subprocess.run([sys.executable, '-B', os.path.join(w.A, KIT, 'tools/queue_job_v16.py'), '--settings', w.S], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2); self.assertIn('USAGE queue_job_v16.py', r.stderr)


def plant_decide(w):
    g = os.path.join(w.Rn, 'receipts', GRADE)
    wr(os.path.join(g, 'HANDOFF/SUMMARY.tsv'), 'V\tstatus\tgate\twaves\nV1\tOK\tPASS\t100\n')
    wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_RULES_V1.tsv'), 'key\tvalue\n' + ''.join('%s\t%s\n' % kv for kv in V121.NMM.items()))
    wr(os.path.join(g, 'HANDOFF/REAL_SEALED/REAL_V1.tsv'), 'horizon\tlead\tt\n15m\t4\t1.8\n1h\t3\t1.5\n')


class D_Decision(unittest.TestCase):
    def dec(self, w, tool, *a):
        return subprocess.run([sys.executable, '-B', os.path.join(w.A, KIT, 'tools', tool), '--settings', w.S, RUN, IDEA, 'V1', '--grade', GRADE] + list(a), capture_output=True, text=True)

    def test_the_exception_is_printed_on_the_decision(self):
        w = World().plant(dfn('E1.S01', 'E1.S04'), 'MENU EXCEPTION E1.S04: the idea scales the paid rate by the interval\n', 'as given; MENU EXCEPTION E1.S04'); plant_decide(w)
        r = self.dec(w, 'decide_v6.py'); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('DECISION %s V1: NEEDS MORE MONTHS' % IDEA, r.stdout); self.assertIn('MENU EXCEPTION E1.S04 (CAUTION): the idea scales', r.stdout)

    def test_a_variant_sealed_before_the_gate_is_printed_refused_state_unchanged(self):
        w = World().plant(dfn('E1.S04')); plant_decide(w)
        r = self.dec(w, 'decide_v6.py'); self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('NEEDS MORE MONTHS', r.stdout); self.assertRegex(r.stdout, r'MENU GATE \S+ V1[^\n]*: REFUSED MENU_NOT_PICKABLE[^\n]*printed only')

    def test_refusals_stay_decide_v5s(self):
        w = World().plant(dfn('E1.S01'))
        for tool in ('decide_v5.py', 'decide_v6.py'):
            r = subprocess.run([sys.executable, '-B', os.path.join(w.A, KIT, 'tools', tool), '--settings', w.S, RUN, IDEA, 'V1', '--grade', 'bad'], capture_output=True, text=True)
            self.assertEqual(r.returncode, 2); self.assertIn('REFUSED: --grade MUST BE A GRADE JOB', r.stderr); self.assertNotIn('Traceback', r.stderr)


    def test_a_changed_v5_is_refused(self):
        w = World().plant(dfn('E1.S01')); plant_decide(w); open(os.path.join(w.A, KIT, 'tools/decide_v5.py'), 'a').write('\n# changed\n')
        r = self.dec(w, 'decide_v6.py'); self.assertEqual(r.returncode, 2); self.assertIn('decide_v5.py MISSING OR CHANGED', r.stderr)


    def test_a_malformed_claim_prints_and_writes_one_row(self):
        w = World().plant(dfn('E1.S01')); plant_decide(w); wr(os.path.join(w.Rn, 'ideas', IDEA, 'TRUE_V1_extra.json'), '[]')   # GPT V12115-TOOL item 2
        r = self.dec(w, 'decide_v6.py', '--write'); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertNotIn('Traceback', r.stderr)
        self.assertIn('WRITTEN', r.stdout); self.assertRegex(r.stdout, r'MENU GATE \S+ V1 \+ TRUE_V1_extra.json: REFUSED UNREADABLE_CLAIM[^\n]*printed only')
        self.assertEqual(len(w.rows('DECISIONS')), 1)
        r = self.dec(w, 'decide_v6.py', '--write'); self.assertEqual(r.returncode, 2); self.assertIn('ALREADY IN DECISIONS', r.stderr)
        self.assertEqual(len(w.rows('DECISIONS')), 1)

    def test_a_fault_in_the_menu_lines_never_fails_a_written_decision(self):
        w = World().plant(dfn('E1.S01')); plant_decide(w); mg = os.path.join(w.A, KIT, 'tools/menu_gate_v1.py'); os.rename(mg, mg + '.aside')
        r = self.dec(w, 'decide_v6.py', '--write'); self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertNotIn('Traceback', r.stderr)
        self.assertIn('WRITTEN', r.stdout); self.assertIn('MENU GATE: NOT READ (FileNotFoundError', r.stdout); self.assertEqual(len(w.rows('DECISIONS')), 1)

    def test_the_menu_lines_are_made_before_decide_v5_runs(self):
        w = World().plant(dfn('E1.S01')); plant_decide(w)
        D6 = load(os.path.join(w.A, KIT, 'tools/decide_v6.py'), 'd6_order_%d' % id(self)); calls = []
        real = D6.menu_lines; D6.menu_lines = lambda *a: (calls.append(len(w.rows('DECISIONS'))), real(*a))[1]
        D6.safe_menu_lines(['--settings', w.S, RUN, IDEA, 'V1', '--grade', GRADE, '--write'])
        self.assertEqual(calls, [0])
        D6.menu_lines = lambda *a: 1 / 0
        self.assertTrue(D6.safe_menu_lines(['--settings', w.S, RUN, IDEA, 'V1', '--grade', GRADE])[0].startswith('MENU GATE: NOT READ (ZeroDivisionError'))


class REAL_Deska04(unittest.TestCase):
    """the real seal of desk trial 4 (DESKA04_20261103 SIGNFLIP V1, frozen): refused today; refused again for its TRUE label"""
    def test_the_deska04_definition_is_refused(self):
        dp, cp = os.path.join(DATA, 'DESKA04_SIGNFLIP_V1.json'), os.path.join(DATA, 'DESKA04_CARD_SIGNFLIP.md')
        self.assertEqual((s16(dp), s16(cp)), ('ba27ffd4a95e1339', '5427e9f473b4469a'))
        reason = open(os.path.join(DATA, 'DESKA04_VARIANTS_REASON.txt')).read().strip()
        with self.assertRaises(MG.Refused) as c:
            MG.gate(dp, cp, None, reason, menu=MG.read_menu(MENU), reader=READER)
        self.assertEqual(c.exception.code, 'MENU_NOT_PICKABLE'); self.assertIn('E1.S04 (CAUTION', str(c.exception))

    def test_with_both_exceptions_it_passes_but_its_label_does_not(self):
        dp = os.path.join(DATA, 'DESKA04_SIGNFLIP_V1.json'); t = tempfile.mkdtemp(prefix='mgr_'); cp = os.path.join(t, 'CARD.md')
        wr(cp, open(os.path.join(DATA, 'DESKA04_CARD_SIGNFLIP.md')).read() + '\nMENU EXCEPTION E1.S04: the paid rate is scaled by the coin interval\n'
           'MENU EXCEPTION E1.S09: the idea is the rate paid at the last settle\n')
        why = 'as given; MENU EXCEPTION E1.S04; MENU EXCEPTION E1.S09'
        g = MG.gate(dp, cp, None, why, menu=MG.read_menu(MENU), reader=READER); self.assertEqual(sorted(g['excepted']), ['E1.S04', 'E1.S09'])
        with self.assertRaises(MG.Refused) as c:
            MG.gate(dp, cp, os.path.join(DATA, 'DESKA04_TRUE_V1_OIFALL.json'), why, menu=MG.read_menu(MENU), reader=READER)
        self.assertIn('E2.S01 (UNPROVEN, read by the label', str(c.exception))


class KEEP_Fdaoi(unittest.TestCase):
    """FDAOI-first: for a variant the gate admits, the queue's job is queue_job_v15's byte for byte, and decide_v5's output and row stand"""
    def test_queue_job_text_equal_v15(self):
        for ex in ((dfn('E1.S01'), '', 'r'), (dfn('E1.S01', 'E1.S04'), 'MENU EXCEPTION E1.S04: the idea needs the interval\n', 'MENU EXCEPTION E1.S04')):
            w = World().plant(*ex)
            a = w.q('queue_job_v15.py', '--dry'); b = w.q('queue_job_v16.py', '--dry')
            self.assertEqual(a.returncode, 0, a.stderr); self.assertEqual(b.returncode, 0, b.stderr)
            self.assertEqual(a.stdout, '\n'.join(l for l in b.stdout.split('\n') if not l.startswith('MENU ')))
            self.assertTrue(any(l.startswith('MENU GATE') for l in b.stdout.split('\n')))

    def test_queued_job_equal_v15(self):
        out = []
        for tool in ('queue_job_v15.py', 'queue_job_v16.py'):
            w = World().plant(dfn('E1.S01')); r = w.q(tool); self.assertEqual(r.returncode, 0, r.stderr)
            x = [x for x in w.rows('RUNS') if x['kind'] == 'TRUE'][0]
            job = re.sub(r'(?m)^CSHA=[0-9a-f]{16}$', 'CSHA=@', open(os.path.join(w.Rn, x['job'])).read().replace(w.t, '@T'))   # named: the claim holds the world's temp path
            out.append((job, {k: v for k, v in x.items() if k not in ('utc_queued', 'job_sha16')}))
        self.assertEqual(out[0], out[1]); self.assertIn('CSHA=@', out[0][0])

    def test_decide_output_and_row_equal_v5(self):
        outs = []
        for tool in ('decide_v5.py', 'decide_v6.py'):
            w = World().plant(dfn('E1.S01')); plant_decide(w)
            r = D_Decision.dec(None, w, tool, '--write'); self.assertEqual(r.returncode, 0, r.stderr)
            row = [{k: v for k, v in x.items() if k != 'utc'} for x in w.rows('DECISIONS')]
            outs.append((re.sub(r'(?m)^WRITTEN \S+Z ', 'WRITTEN @ ', r.stdout), row))   # the clock stamp may cross a second between the two runs (flaky in ALARM_V1_21_16; clean repo fix, SCOUT 3 Nov 22:5xZ)
        self.assertTrue(outs[1][0].startswith(outs[0][0]), outs); self.assertEqual(outs[0][1], outs[1][1])
        self.assertTrue(all(l.startswith('MENU ') for l in outs[1][0][len(outs[0][0]):].strip().split('\n')))

    def test_the_wrapped_tools_and_reader_are_the_installed_bytes(self):
        Q = load(os.path.join(World().A, KIT, 'tools/queue_job_v16.py'), 'q16_keep')
        self.assertEqual(s16(Q.V15), '6ad73bed39b150e8'); self.assertEqual(Q.V15_SHA, '6ad73bed39b150e8')
        src = open(os.path.join(FIX, 'menu_gate_v1.py')).read()
        self.assertNotIn('def collect_reads', src); self.assertNotIn('def label_codes', src)          # the TRUE gate's reader, imported, not copied
        for n in NEW:                                                                              # no detection, grading or template file is opened for writing
            t = open(os.path.join(FIX, n)).read()
            self.assertNotRegex(t, r"open\([^)]*,\s*'(w|a|x)b?'"); self.assertNotIn('JOB_', re.sub(r'#.*', '', t).replace('JOB_PATHS', ''))


if __name__ == '__main__':
    unittest.main(verbosity=1)
