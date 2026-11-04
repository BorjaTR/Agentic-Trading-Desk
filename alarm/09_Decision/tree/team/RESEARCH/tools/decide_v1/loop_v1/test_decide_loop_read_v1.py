"""test_decide_loop_read_v1.py (DECIDE seat, 26 Oct 2026): planted tables for decide_loop_read_v1.py. Each test plants four runs whose
TABLE.tsv rows are set by hand, so the right verdict is known, then checks the reader's cells and verdict.
  python3 -B test_decide_loop_read_v1.py <new scratch folder>"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, 'DECIDE_LOOP_SETTINGS_V1.json')))
SHA = dict(S['events_sha16'])
MONTHS = ['202509', '202510', '202511', '202512']

def plant(root, g, edge, net, stress, month_edge=None, cls='GRADED', parents=None, sha=None):
    d = os.path.join(root, g); os.makedirs(os.path.join(d, 'grade3'))
    json.dump({'run_class': cls, 'status': 'COMPLETE', 'alarm_id': S['alarm_id'], 'event_list': {'sha16': sha or SHA[g]},
               'counts': {'parents': parents or S['groups'][g]['fires']}, 'ledger': {'ask_id': 'PREREG_X_' + g}}, open(d + '/RUN.json', 'w'))
    L = ['slice\tdirection\tmeasure\tscheme\tcost\tstat\tmean\tlo\thi\tparents\tclusters']
    for s, m in S['cells_choosable'] + S['cells_described_only']:
        for sl in ['ALL'] + MONTHS:
            e = edge if sl == 'ALL' else (month_edge or {}).get(sl, edge)
            L.append('%s\tFADE\t%s\t%s\tHONEST\tTOUGH_EDGE\t%g\t%g\t%g\t100\t50' % (sl, m, s, e[0], e[1], e[2]))
            L.append('%s\tFOLLOW\t%s\t%s\tHONEST\tTOUGH_EDGE\t9\t9\t9\t100\t50' % (sl, m, s))
            L.append('%s\tFADE\t%s\t%s\tHONEST\tPARENT\t%g\t0\t0\t100\t50' % (sl, m, s, net))
            L.append('%s\tFADE\t%s\t%s\tSTRESS\tPARENT\t%g\t0\t0\t100\t50' % (sl, m, s, stress))
    open(d + '/grade3/TABLE.tsv', 'w').write('\n'.join(L) + '\n')
    return d

def run(root, out='out'):
    a = [sys.executable, '-B', os.path.join(HERE, 'decide_loop_read_v1.py'), os.path.join(HERE, 'DECIDE_LOOP_SETTINGS_V1.json')] + \
        [os.path.join(root, g) for g in ('VALUED', 'TAKE', 'SKIPRULE', 'BADDATA')] + [os.path.join(root, out)]
    p = subprocess.run(a, capture_output=True, text=True)
    cells = None
    if p.returncode == 0:
        L = [l.split('\t') for l in open(os.path.join(root, out, 'DECIDE_LOOP_CELLS_V1.tsv')).read().split('\n') if l]
        cells = [dict(zip(L[0], r)) for r in L[1:]]
    return p, cells

def fresh(base, name):
    r = os.path.join(base, name); os.makedirs(r); return r  # a new folder per test: nothing is deleted

def main(base):
    res = []
    def t(name, cond):
        res.append(('PASS ' if cond else 'FAIL ') + name)
    # 1 a clean pass: TAKE clearly better than SKIP every month, pays at both costs
    r = fresh(base, 't1')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), 0.02, 0.01); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.06, 0.03)
    plant(r, 'SKIPRULE', (-0.10, -0.20, 0.00), -0.1, -0.2); plant(r, 'BADDATA', (0.0, -0.1, 0.1), 0, 0)
    p, c = run(r)
    t('t1 clean case: every choosable cell passes S1', p.returncode == 0 and all(x['S1_ok'] == 'True' for x in c if x['choosable'] == 'True'))
    t('t1 verdict says S1 PASSES', 'S1 PASSES' in open(r + '/out/DECIDE_LOOP_VERDICT_V1.md').read())
    t('t1 FOLLOW rows are never read', p.returncode == 0 and all(x['TAKE_edge'] == '0.1' for x in c))
    # 2 intervals overlap: c fails
    r = fresh(base, 't2')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), 0.02, 0.01); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.06, 0.03)
    plant(r, 'SKIPRULE', (0.0, -0.1, 0.06), -0.1, -0.2); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
    p, c = run(r)
    t('t2 overlapping intervals fail c', p.returncode == 0 and all(x['S1_ok'] == 'False' and 'c:' in x['why_not'] for x in c))
    t('t2 verdict falls back to taking every valued fire', 'S1 FAILS in every cell' in open(r + '/out/DECIDE_LOOP_VERDICT_V1.md').read())
    # 3 one month reversed: d fails
    r = fresh(base, 't3')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), 0.02, 0.01); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.06, 0.03, month_edge={'202511': (-0.3, -0.4, -0.2)})
    plant(r, 'SKIPRULE', (-0.10, -0.20, 0.00), -0.1, -0.2); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
    p, c = run(r)
    t('t3 one month reversed fails d', p.returncode == 0 and all('d:months 3 of 4' in x['why_not'] for x in c))
    # 4 stress cost loses: b fails
    r = fresh(base, 't4')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), 0.02, -0.01); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.06, -0.001)
    plant(r, 'SKIPRULE', (-0.10, -0.20, 0.00), -0.1, -0.2); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
    p, c = run(r)
    t('t4 stress loss fails b and nothing pays', p.returncode == 0 and all('b:' in x['why_not'] for x in c) and 'NOTHING PAYS' in open(r + '/out/DECIDE_LOOP_VERDICT_V1.md').read())
    # 5 half the effect does not pay: VALUED loses, TAKE barely wins
    r = fresh(base, 't5')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), -0.05, -0.06); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.02, 0.01)
    plant(r, 'SKIPRULE', (-0.10, -0.20, 0.00), -0.1, -0.2); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
    p, c = run(r)
    t('t5 half effect fails e', p.returncode == 0 and all('e:' in x['why_not'] for x in c))
    # 6 refusals: a TEST run, a wrong event list, a wrong parent count, an existing out folder
    for i, (name, kw) in enumerate((('TEST run', {'cls': 'TEST'}), ('wrong events', {'sha': 'ffffffffffffffff'}), ('wrong count', {'parents': 7}))):
        r = fresh(base, 't6%d' % i)
        plant(r, 'VALUED', (0, 0, 0), 0, 0); plant(r, 'TAKE', (0, 0, 0), 0, 0, **kw); plant(r, 'SKIPRULE', (0, 0, 0), 0, 0); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
        p, c = run(r)
        t('t6 refuses a %s' % name, p.returncode != 0 and 'REFUSED' in p.stderr)
    r = fresh(base, 't7')
    for g in ('VALUED', 'TAKE', 'SKIPRULE', 'BADDATA'):
        plant(r, g, (0, 0, 0), 0, 0)
    os.makedirs(r + '/out'); p, c = run(r)
    t('t7 refuses an existing out folder', p.returncode != 0 and 'REFUSED' in p.stderr)
    # 8 the choice is the highest TAKE edge lower bound among passing cells
    r = fresh(base, 't8')
    plant(r, 'VALUED', (0.05, 0.01, 0.09), 0.02, 0.01); plant(r, 'TAKE', (0.10, 0.05, 0.15), 0.06, 0.03)
    plant(r, 'SKIPRULE', (-0.10, -0.20, 0.00), -0.1, -0.2); plant(r, 'BADDATA', (0, 0, 0), 0, 0)
    tb = r + '/TAKE/grade3/TABLE.tsv'; L = open(tb).read().split('\n')
    L = [l.replace('\t0.1\t0.05\t0.15\t', '\t0.2\t0.08\t0.3\t') if l.startswith('ALL\tFADE\tC4C2_4h\tRR\tHONEST\tTOUGH_EDGE') else l for l in L]
    L = [l.replace('\t0.1\t0.05\t0.15\t', '\t0.5\t0.09\t0.9\t') if l.startswith('ALL\tFADE\tret_4h\tTT\tHONEST\tTOUGH_EDGE') else l for l in L]
    open(tb, 'w').write('\n'.join(L)); p, c = run(r)
    v = open(r + '/out/DECIDE_LOOP_VERDICT_V1.md').read() if p.returncode == 0 else ''
    t('t8 chooses RR C4C2_4h, never a described-only cell', 'Chosen setting RR C4C2_4h' in v)
    print('\n'.join(res)); print('%d tests, %d failed' % (len(res), sum(1 for x in res if x.startswith('FAIL'))))
    return any(x.startswith('FAIL') for x in res)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
