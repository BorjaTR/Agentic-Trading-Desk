"""decide_loop_read_v1.py (DECIDE seat, 26 Oct 2026): reads the four GRADED idea_to_grade V3.1 runs of the decision tool's outcome loop and
applies the bar written in DECIDE_LOOP_PREREG_V1.md, with no choice left to the reader. It computes no outcome itself: every number is a
row of a run's grade3/TABLE.tsv (FADE rows; TOUGH_EDGE = the trade minus the tough baseline, PARENT = net per trade, pct).
VALUED = TAKE + SKIPRULE (the fires whose used field has a reading); BADDATA is described apart and never changes a choice.
  python3 -B decide_loop_read_v1.py <settings json> <VALUED run> <TAKE run> <SKIPRULE run> <BADDATA run> <new out folder>
     -> DECIDE_LOOP_CELLS_V1.tsv, DECIDE_LOOP_VERDICT_V1.md"""
import hashlib, json, os, sys

GROUPS = ('VALUED', 'TAKE', 'SKIPRULE', 'BADDATA')

def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def load_table(run, direction):
    L = [l.rstrip('\n').split('\t') for l in open(os.path.join(run, 'grade3', 'TABLE.tsv'))]
    h = L[0]; t = {}
    for r in L[1:]:
        d = dict(zip(h, r))
        if d['direction'] != direction:
            continue
        f = lambda v: float(v) if v not in ('', 'nan', 'NaN') else float('nan')
        t[(d['slice'], d['measure'], d['scheme'], d['cost'], d['stat'])] = (f(d['mean']), f(d['lo']), f(d['hi']), int(d['parents'] or 0), int(d['clusters'] or 0))
    return t

def check_run(run, want_events_sha, alarm):
    b = json.load(open(os.path.join(run, 'RUN.json')))
    bad = []
    if b.get('run_class') != 'GRADED': bad.append('run_class %s' % b.get('run_class'))
    if b.get('status') != 'COMPLETE': bad.append('status %s' % b.get('status'))
    if b.get('alarm_id') != alarm: bad.append('alarm %s' % b.get('alarm_id'))
    if (b.get('event_list') or {}).get('sha16') != want_events_sha: bad.append('events %s not %s' % ((b.get('event_list') or {}).get('sha16'), want_events_sha))
    return bad, b

def ok(x):
    return x == x  # not NaN

def main(settings, valued_run, take_run, skip_run, bad_run, out):
    if os.path.exists(out):
        sys.exit('REFUSED: out folder exists')
    S = json.load(open(settings)); B = S['bar']; d = S['direction']
    runs = dict(zip(GROUPS, (valued_run, take_run, skip_run, bad_run)))
    want = {g: S['events_sha16'][g] for g in GROUPS}
    refs = []
    for g in GROUPS:
        bad, b = check_run(runs[g], want[g], S['alarm_id'])
        if bad:
            sys.exit('REFUSED: %s run %s: %s' % (g, runs[g], '; '.join(bad)))
        n = b['counts']['parents']
        if n != S['groups'][g]['fires']:
            sys.exit('REFUSED: %s run has %d parents, the settings say %d' % (g, n, S['groups'][g]['fires']))
        refs.append('%s: %s (ask %s, TABLE %s)' % (g, runs[g], b['ledger']['ask_id'], sha16(os.path.join(runs[g], 'grade3', 'TABLE.tsv'))))
    T = {g: load_table(runs[g], d) for g in GROUPS}
    months = sorted({k[0] for k in T['VALUED'] if k[0] != 'ALL'})
    E, N, C1, C2 = B['edge_stat'], B['net_stat'], B['cost_main'], B['cost_check']
    def v(g, sl, m, s, c, st):
        return T[g].get((sl, m, s, c, st), (float('nan'),) * 3 + (0, 0))
    rows = []; head = ['scheme', 'measure', 'choosable', 'side_ok', 'S1_ok', 'pays_take', 'pays_all', 'why_not',
                       'VALUED_edge', 'VALUED_edge_lo', 'TAKE_edge', 'TAKE_edge_lo', 'TAKE_edge_hi', 'SKIP_edge', 'SKIP_edge_hi', 'BAD_edge',
                       'VALUED_net', 'TAKE_net', 'SKIP_net', 'BAD_net', 'VALUED_net_stress', 'TAKE_net_stress', 'months_take_gt_skip', 'months_compared',
                       'TAKE_waves', 'SKIP_waves', 'fill_share', 'missed_tt']
    cells = [(s, m, True) for s, m in S['cells_choosable']] + [(s, m, False) for s, m in S['cells_described_only']]
    for s, m, choos in cells:
        ae = v('VALUED', 'ALL', m, s, C1, E); te = v('TAKE', 'ALL', m, s, C1, E); se = v('SKIPRULE', 'ALL', m, s, C1, E); be = v('BADDATA', 'ALL', m, s, C1, E)
        an = v('VALUED', 'ALL', m, s, C1, N)[0]; tn = v('TAKE', 'ALL', m, s, C1, N)[0]; sn = v('SKIPRULE', 'ALL', m, s, C1, N)[0]; bn = v('BADDATA', 'ALL', m, s, C1, N)[0]
        ans = v('VALUED', 'ALL', m, s, C2, N)[0]; tns = v('TAKE', 'ALL', m, s, C2, N)[0]
        mc = mg = 0
        for mo in months:
            a, b_ = v('TAKE', mo, m, s, C1, E), v('SKIPRULE', mo, m, s, C1, E)
            if a[4] >= B['min_waves_month'] and b_[4] >= B['min_waves_month'] and ok(a[0]) and ok(b_[0]):
                mc += 1; mg += a[0] > b_[0]
        h = B['half_effect']
        why = []
        side_ok = ok(ae[1]) and ae[1] > 0
        pays_all = side_ok and ok(an) and an > 0 and ok(ans) and ans > 0
        if not (ok(te[1]) and te[1] > 0): why.append('a:TAKE edge lo<=0')
        if not (ok(tn) and tn > 0 and ok(tns) and tns > 0): why.append('b:TAKE net<=0 honest or stress')
        if not (ok(se[2]) and ok(te[1]) and se[2] < te[1]): why.append('c:SKIP edge hi>=TAKE edge lo')
        if not (mc >= 2 and mg == mc): why.append('d:months %d of %d' % (mg, mc))
        if not (ok(an) and ok(tn) and an + h * (tn - an) > 0 and ok(ans) and ok(tns) and ans + h * (tns - ans) > 0): why.append('e:half effect does not pay')
        s1 = not why
        pays_take = not [w for w in why if w[0] in 'abe']
        fs = v('TAKE', 'ALL', m, s, C1, 'FILL_SHARE')[0]; mt = v('TAKE', 'ALL', m, s, C1, 'MISSED_TT')[0]
        rows.append([s, m, choos, side_ok, s1, pays_take, pays_all, ' '.join(why) or '-', ae[0], ae[1], te[0], te[1], te[2], se[0], se[2], be[0],
                     an, tn, sn, bn, ans, tns, mg, mc, te[4], se[4], fs, mt])
    os.makedirs(out)
    fmt = lambda x: ('%.6g' % x) if isinstance(x, float) else str(x)
    open(os.path.join(out, 'DECIDE_LOOP_CELLS_V1.tsv'), 'w').write('\n'.join(['\t'.join(head)] + ['\t'.join(fmt(x) for x in r) for r in rows]) + '\n')
    R = [dict(zip(head, r)) for r in rows]; ch = [r for r in R if r['choosable']]
    s1 = [r for r in ch if r['S1_ok']]; pa = [r for r in ch if r['pays_all']]
    key = lambda r: r['TAKE_edge_lo']
    if s1:
        best = max(s1, key=key); verdict = 'S1 PASSES. Chosen setting %s %s (the highest TAKE edge lower bound of the %d passing cells).' % (best['scheme'], best['measure'], len(s1))
    elif pa:
        best = max(pa, key=lambda r: r['VALUED_edge_lo']); verdict = 'S1 FAILS in every cell. Taking every valued fire pays in %d cells; best %s %s by the VALUED edge lower bound.' % (len(pa), best['scheme'], best['measure'])
    else:
        best = None; verdict = 'NOTHING PAYS: S1 fails in every cell and taking every valued fire does not pay after cost in any cell. Entry and exit stay UNSET.'
    tt = {r['measure']: r for r in R if r['scheme'] == 'TT'}
    P1 = [r for r in ch if r['scheme'] == 'TT']; p1 = sum(1 for r in P1 if ok(r['VALUED_edge']) and r['VALUED_edge'] > 0)
    p2 = sum(1 for r in ch if ok(r['SKIP_edge']) and ok(r['TAKE_edge']) and r['SKIP_edge'] < r['TAKE_edge'])
    rest = [r for r in ch if r['scheme'] in ('RT', 'RR') and r['measure'] in tt]
    p3a = sum(1 for r in rest if ok(r['TAKE_net']) and ok(tt[r['measure']]['TAKE_net']) and r['TAKE_net'] > tt[r['measure']]['TAKE_net'])
    p3b = sum(1 for r in rest if ok(r['missed_tt']) and ok(tt[r['measure']]['TAKE_net']) and r['missed_tt'] > tt[r['measure']]['TAKE_net'])
    p4 = 0; p4n = 0
    for s in ('TT', 'RT', 'RR'):
        for a, b_ in (('V1_1h', 'V1_4h'), ('V2_1h', 'V2_4h'), ('C2C1_1h', 'C4C2_4h')):
            x = [r for r in ch if r['scheme'] == s and r['measure'] == a]; y = [r for r in ch if r['scheme'] == s and r['measure'] == b_]
            if x and y and ok(x[0]['TAKE_net_stress']) and ok(y[0]['TAKE_net_stress']):
                p4n += 1; p4 += y[0]['TAKE_net_stress'] > x[0]['TAKE_net_stress']
    md = ['# Decision tool V1 outcome loop, ALM_M_V1 (written by decide_loop_read_v1.py)', '', '**Verdict.** ' + verdict, '',
          'Runs (all GRADED, FADE rows, honest cost unless named):'] + ['- ' + x for x in refs] + ['',
          '| entry | exit | S1 | TAKE pays | VALUED pays | why not | VALUED edge [lo] | TAKE edge [lo, hi] | SKIP edge [hi] | BAD edge | TAKE net | TAKE net stress | months |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in ch:
        md.append('|%s|%s|%s|%s|%s|%s|%s [%s]|%s [%s, %s]|%s [%s]|%s|%s|%s|%d of %d|' % (r['scheme'], r['measure'], 'PASS' if r['S1_ok'] else 'fail', 'yes' if r['pays_take'] else 'no',
                  'yes' if r['pays_all'] else 'no', r['why_not'], *(fmt(r[k]) for k in ('VALUED_edge', 'VALUED_edge_lo', 'TAKE_edge', 'TAKE_edge_lo', 'TAKE_edge_hi', 'SKIP_edge', 'SKIP_edge_hi', 'BAD_edge', 'TAKE_net', 'TAKE_net_stress')), r['months_take_gt_skip'], r['months_compared']))
    md += ['', 'Predictions (scored as written in the PREREG):',
           '- P1 FADE beats the tough baseline on all valued fires, TT: %d of %d cells.' % (p1, len(P1)),
           '- P2 the skipped TIGHTER group is worse than TAKE: %d of %d cells.' % (p2, len(ch)),
           '- P3a resting entries net more than TT on the same exit: %d of %d; P3b the missed resting fills, taken TT, net more than TT on all TAKE fires: %d of %d.' % (p3a, len(rest), p3b, len(rest)),
           '- P4 at stress cost the 4 h exit nets more than its 1 h twin: %d of %d pairs.' % (p4, p4n),
           '', 'Described only (never chosen): ' + ', '.join('%s %s TAKE edge %s' % (r['scheme'], r['measure'], fmt(r['TAKE_edge'])) for r in R if not r['choosable']),
           '', 'This describes stored paths after the fires against the tough baseline on Sep-Dec 2025. It is not live parity. Jan-Feb is looked at once, later, only for the chosen setting.']
    open(os.path.join(out, 'DECIDE_LOOP_VERDICT_V1.md'), 'w').write('\n'.join(md) + '\n')
    print('\n'.join(md[:3]))

if __name__ == '__main__':
    main(*sys.argv[1:7])
