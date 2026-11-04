"""test_markout_v1_2.py: test_markout_v1_1.py (5ff4d0940bc1646c, never edited) on markout_v1_2, with checks of its new lines. Owner
STRATEGY. New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Changed: it imports markout_v1_2; it runs markout_v1's 43 units
from test_markout_v1_2_base.py (test_markout_v1.py on markout_v1_2) in place of test_markout_v1.py; three new checks: the grader's
folders are found beside the markout folder (and hold the rel1 engine and V3.4's grade), the engine imported is i2g_engine_rel1, and a
rel1 S6 run is graded as an S6 run. The rest of this text is test_markout_v1_1.py's.
test_markout_v1_1.py: hand answers for markout_v1_1's new parts (which grade made the run's table; the table check outside the
RR net rows) and markout_v1's 43 units run on v1_1 (the shared code is unchanged).  python3 test_markout_v1_1.py WORKDIR"""
import os, runpy, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import markout_v1_2 as M

W = sys.argv[1]; os.makedirs(W, exist_ok=True); ok = fail = 0


def check(name, cond):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1; print('FAIL', name)


check('plain V3.2 pins -> v32', M.grade_kind({'pins_file': {'path': '/x/I2G_PINS_V3_2.json'}}) == 'v32')
check('speed twin S6 pins -> v34', M.grade_kind({'pins_file': {'path': '/x/I2G_PINS_V3_2_S6.json'}}) == 'v34' and
      M.grade_kind({'pins_file': {'path': '/x/I2G_PINS_V3_2_S3.json'}}) == 'v34')
check('no pins -> v32', M.grade_kind({}) == 'v32')
check('rel1: a run of the rel1 S6 chain -> v34, the plain rel1 V3.2 -> v32', M.grade_kind({'pins_file': {'path': '/x/I2G_PINS_V3_2_S6_REL1.json'}}) == 'v34' and
      M.grade_kind({'pins_file': {'path': '/x/I2G_PINS_V3_2_REL1.json'}}) == 'v32')
check('rel1: the grader folders beside the markout folder', M.I2G == os.path.realpath(os.path.join(HERE, '..', 'idea_to_grade')) and
      M.V34 == os.path.realpath(os.path.join(HERE, '..', 'i2g_v3_3')) and os.path.isfile(os.path.join(M.I2G, 'i2g_engine_rel1.py')) and
      os.path.isfile(os.path.join(M.V34, 'i2g_v3_4_grade.py')))
_src = open(M.__file__).read()
check('rel1: the engine imported is i2g_engine_rel1 (twice), never i2g_engine', _src.count('import i2g_engine_rel1 as E2') == 2 and
      'import i2g_engine as' not in _src and '/Users/' not in _src.split('import argparse', 1)[1])   # machine-path-ok: test data, the check that no Mac path is left
tp = os.path.join(W, 'T.tsv')
open(tp, 'w').write('slice\tdirection\tmeasure\tscheme\tcost\tstat\tmean\n' + 'ALL\tFADE\tV1_1h\tTT\tSTRESS\tPARENT\t0.1\n'
                    + 'ALL\tFADE\tV1_1h\tRR\tSTRESS\tPARENT\t0.2\n' + 'ALL\tFADE\tV1_1h\tRR\tGROSS\tPARENT\t0.3\n')
rr = lambda f: len(f) > 4 and f[3] == 'RR' and f[4] != 'GROSS'
check('equal: (0, 0)', M.table_diff_except(['ALL\tFADE\tV1_1h\tTT\tSTRESS\tPARENT\t0.1', 'ALL\tFADE\tV1_1h\tRR\tSTRESS\tPARENT\t0.2',
                                             'ALL\tFADE\tV1_1h\tRR\tGROSS\tPARENT\t0.3'], tp, rr) == (0, 0))
check('an RR net row may differ: (0, 1)', M.table_diff_except(['ALL\tFADE\tV1_1h\tTT\tSTRESS\tPARENT\t0.1', 'ALL\tFADE\tV1_1h\tRR\tSTRESS\tPARENT\t9',
                                                                'ALL\tFADE\tV1_1h\tRR\tGROSS\tPARENT\t0.3'], tp, rr) == (0, 1))
check('a TT or an RR GROSS row may not: (2, 0)', M.table_diff_except(['ALL\tFADE\tV1_1h\tTT\tSTRESS\tPARENT\t9', 'ALL\tFADE\tV1_1h\tRR\tSTRESS\tPARENT\t0.2',
                                                                       'ALL\tFADE\tV1_1h\tRR\tGROSS\tPARENT\t9'], tp, rr) == (2, 0))
check('a missing row fails', M.table_diff_except(['x'], tp, rr)[0] > 0)
# markout_v1's own 43 units on v1_2 (test_markout_v1_2_base.py imports markout_v1_2)
saved = sys.argv[:]; sys.argv = ['test_markout_v1_2_base.py', os.path.join(W, 'v1')]
try:
    runpy.run_path(os.path.join(HERE, 'test_markout_v1_2_base.py'), run_name='__main__'); code = 0
except SystemExit as e:
    code = e.code
sys.argv = saved
check('markout_v1 units pass on v1_2', code == 0)
print('UNITS %d PASS %d FAIL' % (ok, fail)); sys.exit(1 if fail else 0)
