#!/usr/bin/env python3
"""test_sepmar_kinds_v1.py (SCOUT SCO-A179, 7 Nov 2026; the owner 7 Nov 08:54 "yes", 09:13 Berlin "I allow the months"): the Sep-Mar kinds of
ALARM_V1_22_0, read from the package's own files, no data: GRADE = the MONTH chain stopped at 20260331 with the Sep-Mar hand-off, MONTH =
2601-2603 (no April), COUNT = detect_gm1 MONTH to 20260331, TRUE = true_gate_v4, FIRSTLOOK months to 20260331, the definition window rule,
the window table (BUILD to 20260731, BLIND from 20260801) and the law (research to 20260331). Every test is red on ALARM_V1_21_16_6.
  python3 -B test_sepmar_kinds_v1.py [<Alarm folder>]     (default: the package that holds this file)"""
import ast, hashlib, importlib.util, json, os, re, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
AL = sys.argv.pop(1) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
K = os.path.join(AL, 'Agentic/tree/ALARM_DESIGN/KIT_V5'); T = os.path.join(AL, 'Agentic/tree/ALARM_DESIGN/runs/CLAUDE1_20261028/tools')
Q = os.path.join(K, 'tools/queue_job_v15.py')


def s16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def body(name):
    """a template's text below its header line (the header tells history and may name old days)"""
    return open(os.path.join(K, 'jobs', name)).read().split('\n', 1)[1]


def qsrc():
    return open(Q).read()


def qfunc(name, **glb):
    """one function of queue_job_v15, compiled alone (the module reads settings at import)"""
    tree = ast.parse(qsrc()); fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name][0]
    g = dict(glb); exec(compile(ast.Module(body=[fn], type_ignores=[]), Q, 'exec'), g); return g[name]


class Refused(Exception):
    pass


class Kinds(unittest.TestCase):
    def test_k01_templates_pinned_by_their_bytes(self):
        src = qsrc()
        for k, n in (('COUNT', 'JOB_COUNT_V8'), ('GRADE', 'JOB_GRADE_V15'), ('MONTH', 'JOB_MONTH_V15'), ('TRUE', 'JOB_TRUE_V2')):
            p = os.path.join(K, 'jobs', n + '.job.sh.txt')
            self.assertIn("'%s': '%s'" % (k, s16(p)), src, k); self.assertIn("'%s': '%s.job.sh.txt'" % (k, n), src, k)

    def test_k02_months_no_april(self):
        self.assertIn("MONTHS = ('2601', '2602', '2603')", qsrc()); self.assertNotIn("'2604')", qsrc().split('MONTHS = ', 1)[1].split('\n', 1)[0])

    def test_k03_grade_is_sep_mar(self):
        b = body('JOB_GRADE_V15.job.sh.txt')
        self.assertIn('bash $MP/alarm_grade_chain_v2_2_7_to20260331.sh $V $D $W', b)
        self.assertIn('perfire $F $T/perfire_v1_1_to20260331.py', b); self.assertIn('handoff $F $T/lead_null_v1_1_sepmar_to20260331.py', b)
        for old in ('20251231', '20260430', 'v2_0_7', 'v2_0_10'):
            self.assertNotIn(old, b, old)
        for rel, p in (('alarm_grade_chain_v2_2_7_to20260331.sh', os.path.join(AL, '03_Grading/tree/tools/month_parts/alarm_grade_chain_v2_2_7_to20260331.sh')),
                       ('perfire_v1_1_to20260331.py', os.path.join(T, 'perfire_v1_1_to20260331.py')), ('lead_null_v1_1_sepmar_to20260331.py', os.path.join(T, 'lead_null_v1_1_sepmar_to20260331.py'))):
            self.assertRegex(b, re.escape(rel) + ' ' + s16(p), rel)

    def test_k04_month_kind_no_april(self):
        b = body('JOB_MONTH_V15.job.sh.txt')
        self.assertIn('for M in 2601 2602 2603; do', b)
        for old in ('2604', '20260430'):
            self.assertNotIn(old, b, old)

    def test_k05_count_on_detect_gm1_to_march(self):
        b = body('JOB_COUNT_V8.job.sh.txt')
        self.assertIn('FIRST=20250910; LAST=20260331', b); self.assertIn('detect_gm1.py --windows MONTH --definition', b)
        self.assertRegex(b, r'detect_gm1\.py ' + s16(os.path.join(AL, '01_Detection/tree/team/RESEARCH/tools/idea_to_grade/detect_gm1.py')))
        self.assertIn('1775001600', b); self.assertIn('of 7;', b); self.assertNotIn('detect_v2', b)

    def test_k06_true_on_v4(self):
        b = body('JOB_TRUE_V2.job.sh.txt')
        self.assertIn('true_gate_v4.py check $CL', b); self.assertIn('true_gate_v4.py run $CL $OUT', b); self.assertNotIn('true_gate_v3.py', b)
        self.assertIn("'true_gate_v4.py')", qsrc())
        g = open(os.path.join(AL, '03_Grading/tree/tools/true_gate/true_gate_v4.py')).read()
        self.assertIn("FIRST_ALLOWED, LAST_ALLOWED = '20250910', '20260331'", g)

    def test_k07_hardcoded_last_days(self):
        self.assertIn("FIRST, LAST = '20250910', '20260331'", open(os.path.join(T, 'perfire_v1_1_to20260331.py')).read())
        ln = open(os.path.join(T, 'lead_null_v1_1_sepmar_to20260331.py')).read()
        self.assertIn("FIRST, LAST = '20250910', '20260331'", ln); self.assertIn("GATE_MONTHS = ('2509', '2510', '2511', '2512', '2601', '2602', '2603')", ln)
        self.assertIn('FIRST=20250910; LAST=20260331   #', open(os.path.join(AL, '03_Grading/tree/tools/month_parts/alarm_grade_chain_v2_2_7_to20260331.sh')).read())

    def test_k08_definition_window(self):
        cw = qfunc('check_window', json=json, Refused=Refused)
        d = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'sepmar_k08_%d' % os.getpid()); os.makedirs(d, exist_ok=True)
        def w(last, first='20250901'):
            p = os.path.join(d, 'D_%s.json' % last); json.dump({'window': {'first': first, 'last': last}}, open(p, 'w')); return p
        cw(w('20260331'), 'V'); cw(w('20260430'), 'V')
        with self.assertRaises(Refused):
            cw(w('20260330'), 'V')
        with self.assertRaises(Refused):
            cw(w('20260331', first='20250911'), 'V')

    def test_k09_firstlook_months(self):
        s = json.load(open(os.path.join(AL, '06_First_look/FIRSTLOOK_SETTINGS_V1.json')))['months']
        self.assertEqual((s['first'], s['design_last'], s['full_last']), ('20250910', '20260331', '20260331'))
        self.assertIn("m['full_last'] > '20260331'", qsrc())

    def test_k10_window_table_and_law(self):
        rows = [l.split('\t') for l in open(os.path.join(AL, '01_Detection/tree/team/RESEARCH/tools/alarm_process/WINDOWS_ALARM_V1.tsv')).read().split('\n')[1:] if l]
        self.assertEqual([(r[0], r[1], r[2]) for r in rows], [('BUILD', '20250901', '20260731'), ('BLIND', '20260801', 'open_ended')])
        sha = s16(os.path.join(AL, '01_Detection/tree/team/RESEARCH/tools/alarm_process/WINDOWS_ALARM_V1.tsv'))
        for rel in ('idea_to_grade/detect_gm1.py', 'idea_to_grade/idea_to_grade_gm1.py', 'event_outcomes/event_outcomes_gm2.py'):
            self.assertIn("WINDOWS_ALARM_SHA16 = '%s'" % sha, open(os.path.join(AL, '01_Detection/tree/team/RESEARCH/tools', rel)).read(), rel)
        sp = importlib.util.spec_from_file_location('law_k10', os.path.join(AL, '_vendor/LAB3_code/lab3/law.py')); L = importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
        self.assertIsNone(L.research_refusal(20260331)); self.assertIsNotNone(L.research_refusal(20260401)); self.assertIsNotNone(L.research_refusal(20260801))
        for rel in ('01_Detection/tree/team/LAB3/code/lab3/law.py', '07_Price_path/tree/team/LAB3/code/lab3/law.py'):
            self.assertEqual(s16(os.path.join(AL, rel)), s16(os.path.join(AL, '_vendor/LAB3_code/lab3/law.py')), rel)


if __name__ == '__main__':
    unittest.main(verbosity=2)
