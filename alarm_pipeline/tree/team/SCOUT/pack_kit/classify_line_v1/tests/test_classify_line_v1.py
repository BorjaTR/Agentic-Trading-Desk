#!/usr/bin/env python3
# test_classify_line_v1.py (SCO-A137, SCOUT 2026-11-06): smallest cases of classify_line_v1.py (the CLASSIFY card line from the kit's own
# receipts: decide_v6 DECIDE_V1.txt, the TRUE job's TRUE_ROW.tsv, the novelty_v5 relwait output, optional FIRST_LOOK.md and COUNT_V1.tsv),
# written before the tool (red first). Planted receipts in the kit's shapes; every word comes from a planted file.
# Usage: python3 -B test_classify_line_v1.py [<tool path>] [<work dir>]; exit 0 when all pass.
import os, sys, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'classify_line_v1.py')
W = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'work', 'r_%s_%d' % (time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()), os.getpid()))
os.makedirs(W)
def run(*a):
    p = subprocess.run([sys.executable, '-B', TOOL] + list(a), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout
def wr(n, t):
    p = os.path.join(W, n)
    with open(p, 'w') as f: f.write(t)
    return p
DEC = 'DECISION TESTIDEA V1: STOP | R1 no R2 no | LEAD 15m +3.15 | waves 720, months counted 4 passing 2 | R1 missed: passing 2 of 4 counted (need 3)\nSOURCES grade 20270124_GRADE_TESTIDEA\nrc=0\n'
TR = 'id\tverdict\tfires\tidea\tV\tdef_sha16\nTESTIDEA_V1_OICLOSED10\tNOT SUPPORTED\t100\tTESTIDEA\tV1\t420cbf6a0db2e405\n'
NOV = 'NOVELTY /x/V1_FIRES_V1_LIST.tsv (sha16 3d76823e297e0e0e), lean FADE: 10 fires\nnearest 1: A (OWN)\nVERDICT NEW: every overlap under 40 pct\nBRIDGE END rc 0\n'
FL = '# First look of TESTIDEA_V1: RULE_9 = NEEDS MORE MONTHS (SIZE)\n\nMonths read: Sep-Dec 2025 only.\n'
CNT = '# COUNT V1 (planted)\nmonth\tfires\twaves\tmax_fires_in_a_wave\n2509\t1\t31\t50\n2510\t1\t40\t51\n2511\t1\t30\t93\n2512\t1\t35\t51\nALL\t4\t136\t93\n# months with 30 or more waves: 4 of 4\n'
def base(tag, dec=DEC, tr=TR, nov=NOV):
    return ['--idea', 'TESTIDEA', '--v', 'V1', '--lean', 'FADE', '--claim-kind', 'SIDE', '--decide', wr('DECIDE_%s.txt' % tag, dec),
            '--true-row', wr('TRUE_ROW_%s.tsv' % tag, tr), '--novelty', wr('RELWAIT_NOVELTY_%s.txt' % tag, nov), '--open', 'why 2511 fails']
CASES = []
def case(f): CASES.append(f); return f
@case
def t01_line_from_three_receipts():
    rc, o = run(*base('a'))
    assert rc == 0, (rc, o)
    l = [x for x in o.split('\n') if x.startswith('CLASSIFY ')]
    assert len(l) == 1, o
    l = l[0]
    for w in ('CLASSIFY TESTIDEA V1 FADE:', 'race STOP (decide_v6: R1 missed: passing 2 of 4 counted (need 3))', 'TRUE NOT SUPPORTED (TESTIDEA_V1_OICLOSED10, true_gate_v3)',
              'novelty NEW (novelty_v5)', 'first look not run', 'claim SIDE (FADE)', 'open: why 2511 fails'):
        assert w in l, (w, l)
    assert 'SOURCES decide ' in o and 'true_row ' in o and 'novelty ' in o, o
@case
def t02_with_first_look_and_count():
    a = base('b') + ['--firstlook', wr('FIRST_LOOK_b.md', FL), '--count', wr('COUNT_V1_b.tsv', CNT)]
    rc, o = run(*a)
    assert rc == 0, (rc, o)
    assert 'first look NEEDS MORE MONTHS (SIZE) (first_look RULE_9)' in o, o
    assert 'COUNT max_fires_in_a_wave by month: 2509 50, 2510 51, 2511 93, 2512 51' in o, o
@case
def t03_no_decision_line_refused():
    rc, o = run(*base('c', dec='nothing here\n'))
    assert rc == 3 and 'REFUSED NO_DECISION' in o, (rc, o)
@case
def t04_decision_of_another_idea_refused():
    rc, o = run(*base('d', dec=DEC.replace('DECISION TESTIDEA V1', 'DECISION OTHER V1')))
    assert rc == 3 and 'REFUSED NO_DECISION' in o, (rc, o)
@case
def t05_race_word_not_a_kit_word_refused():
    rc, o = run(*base('e', dec=DEC.replace(': STOP |', ': GREAT |')))
    assert rc == 3 and 'REFUSED BAD_WORD' in o, (rc, o)
@case
def t06_true_row_of_another_variant_refused():
    rc, o = run(*base('f', tr=TR.replace('\tTESTIDEA\tV1\t', '\tTESTIDEA\tV2\t')))
    assert rc == 3 and 'REFUSED TRUE_MISMATCH' in o, (rc, o)
@case
def t07_true_row_two_rows_refused():
    rc, o = run(*base('g', tr=TR + TR.split('\n')[1] + '\n'))
    assert rc == 3 and 'REFUSED TRUE_MISMATCH' in o, (rc, o)
@case
def t08_true_word_not_a_kit_word_refused():
    rc, o = run(*base('h', tr=TR.replace('NOT SUPPORTED', 'MAYBE')))
    assert rc == 3 and 'REFUSED BAD_WORD' in o, (rc, o)
@case
def t09_no_verdict_refused():
    rc, o = run(*base('i', nov='NOVELTY x\nBRIDGE END rc 0\n'))
    assert rc == 3 and 'REFUSED NO_VERDICT' in o, (rc, o)
@case
def t10_two_verdicts_refused():
    rc, o = run(*base('j', nov=NOV + 'VERDICT COPY: x\n'))
    assert rc == 3 and 'REFUSED NO_VERDICT' in o, (rc, o)
@case
def t11_new_side_word_kept_whole():
    rc, o = run(*base('k', nov=NOV.replace('VERDICT NEW:', 'VERDICT NEW SIDE:')))
    assert rc == 0 and 'novelty NEW SIDE (novelty_v5)' in o, (rc, o)
@case
def t12_first_look_of_another_alarm_refused():
    a = base('l') + ['--firstlook', wr('FIRST_LOOK_l.md', FL.replace('TESTIDEA_V1', 'OTHER_V1'))]
    rc, o = run(*a)
    assert rc == 3 and 'REFUSED FL_MISMATCH' in o, (rc, o)
@case
def t13_missing_file_refused():
    a = base('m'); a[a.index('--novelty') + 1] = os.path.join(W, 'none.txt')
    rc, o = run(*a)
    assert rc == 3 and 'REFUSED NO_FILE' in o, (rc, o)
@case
def t14_count_without_month_column_refused():
    a = base('n') + ['--count', wr('COUNT_V1_n.tsv', '# c\nfires\twaves\n1\t2\n')]
    rc, o = run(*a)
    assert rc == 3 and 'REFUSED BAD_COUNT' in o, (rc, o)
@case
def t15_bad_lean_usage():
    a = base('o'); a[a.index('--lean') + 1] = 'UP'
    rc, o = run(*a)
    assert rc == 2 and 'USAGE' in o, (rc, o)
@case
def t16_two_decision_lines_refused():
    rc, o = run(*base('p', dec=DEC + DEC.split('\n')[0] + '\n'))
    assert rc == 3 and 'REFUSED NO_DECISION' in o, (rc, o)
def main():
    ok = 0
    for f in CASES:
        try: f(); ok += 1; print('OK %s' % f.__name__)
        except Exception as e: print('FAIL %s: %r' % (f.__name__, e))
    print('TESTS %d of %d (tool %s)' % (ok, len(CASES), TOOL)); return 0 if ok == len(CASES) else 1
if __name__ == '__main__': sys.exit(main())
