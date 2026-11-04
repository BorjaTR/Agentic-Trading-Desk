#!/usr/bin/env python3
"""read_stratentry_v1.py (SCOUT, run CLAUDE1_20261028, 29 Oct 2026; TEST, NOT REVIEWED). Proof step 2: can the alarms the hand-off
keeps enter the strategy stage? Applies ideas/STRATENTRY/PREREG_STRATENTRY_V1.md to the text receipts of the S0 + S2 runs:
per version, STRATEGY's S2 gate as written (GATE), SCOUT's strict reading (CLEAR), the edge beyond same-move moments (TOUGH, reported),
money after our cost (reported) and the markout's own gates (PACKAGE); then lines L1 to L4 and the verdict.
Reads only text files on dev (no market data, no SCRATCH_DISK); writes nothing.
  python3 -B tools/read_stratentry_v1.py ideas/STRATENTRY/STRATENTRY_INPUTS_V1.tsv receipts/STRATENTRY_R1
Per version V it reads <receipts>/<V>/MARKOUT/CURVE.tsv, GATES.json and TABLE_W0.tsv; a missing file is MISSING (a miss, never a pass).
GATE  (PROCESS_V6 S2, STRATEGY): PASS when at some wait (0, 60, 300 s) and horizon (10 s .. 4 h) the lean side's CALM_EDGE before
      cost (GROSS, scheme TT, slice ALL) has its mean above 0 in H1 AND in H2 (the same cell); else STOP.
CLEAR (SCOUT): at wait 0, at 15 min or at 1 h: the Sep-Dec 95 pct range is above 0 (lo > 0) AND the mean is above 0 in H1 and in H2."""
import csv, json, math, os, sys

WAITS = (0, 60, 300)
HORIZONS = ('ret_10s', 'ret_1m', 'ret_5m', 'ret_15m', 'ret_1h', 'ret_4h')
CLEAR_H = ('ret_15m', 'ret_1h')
GROUPS = ('KEPT', 'STOPPED', 'CONTROL_NULL', 'CONTROL_PLANTED')
csv.field_size_limit(10 ** 9)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float('nan')


def pos(x):
    """strictly above 0; NaN is never above 0"""
    return x == x and x > 0


def read_inputs(path):
    rows = []
    with open(path) as f:
        lines = [l for l in f if not l.startswith('#')]
    for x in csv.DictReader(lines, delimiter='\t'):
        if x['group'] not in GROUPS:
            raise SystemExit('BAD GROUP %s %s' % (x['V'], x['group']))
        if x['lean'] not in ('FADE', 'FOLLOW'):
            raise SystemExit('BAD LEAN %s %s' % (x['V'], x['lean']))
        rows.append(x)
    return rows


def load_curve(path):
    """{(wait, part, direction, measure, stat, cost): (mean, lo, hi, parents)}, slice ALL and scheme TT only"""
    out = {}
    with open(path) as f:
        for x in csv.DictReader(f, delimiter='\t'):
            if x['slice'] != 'ALL' or x['scheme'] != 'TT':
                continue
            w = int(round(num(x['wait_s'])))
            out[(w, x['part'], x['direction'], x['measure'], x['stat'], x['cost'])] = (num(x['mean']), num(x['lo']), num(x['hi']), x['parents'])
    return out


def load_table(path):
    """{(direction, measure, scheme, cost, stat): (mean, lo, hi, parents)}, slice ALL only"""
    out = {}
    with open(path) as f:
        for x in csv.DictReader(f, delimiter='\t'):
            if x['slice'] != 'ALL':
                continue
            out[(x['direction'], x['measure'], x['scheme'], x['cost'], x['stat'])] = (num(x['mean']), num(x['lo']), num(x['hi']), x['parents'])
    return out


def gate(c, lean):
    """STRATEGY's S2 gate: the cells (wait, horizon) whose CALM_EDGE GROSS mean is above 0 in both halves"""
    cells, seen = [], 0
    for w in WAITS:
        for h in HORIZONS:
            a = c.get((w, 'H1', lean, h, 'CALM_EDGE', 'GROSS'))
            b = c.get((w, 'H2', lean, h, 'CALM_EDGE', 'GROSS'))
            if a is None or b is None:
                continue
            seen += 1
            if pos(a[0]) and pos(b[0]):
                cells.append((w, h, a[0], b[0]))
    if seen == 0:
        return 'MISSING', cells, seen
    return ('PASS' if cells else 'STOP'), cells, seen


def clear(c, lean):
    """SCOUT's strict reading: wait 0, 15 min or 1 h, lo > 0 over Sep-Dec and the mean above 0 in both halves"""
    hits, seen = [], 0
    for h in CLEAR_H:
        al = c.get((0, 'ALL', lean, h, 'CALM_EDGE', 'GROSS'))
        a = c.get((0, 'H1', lean, h, 'CALM_EDGE', 'GROSS'))
        b = c.get((0, 'H2', lean, h, 'CALM_EDGE', 'GROSS'))
        if al is None or a is None or b is None:
            continue
        seen += 1
        if pos(al[1]) and pos(a[0]) and pos(b[0]):
            hits.append(h)
    if seen == 0:
        return 'MISSING', hits
    return ('CLEAR' if hits else 'NOT CLEAR'), hits


def package(gpath):
    """the markout's own gates: A and B must be there and ok; A2 (v1_1) ok when present"""
    if not os.path.isfile(gpath):
        return False, 'GATES MISSING'
    g = json.load(open(gpath))
    a = g.get('A_regrade_saved_values', {}).get('ok')
    b = g.get('B_wait0_equals_saved', {}).get('ok')
    a2 = g.get('A2_v34_path_equals_run_outside_RR_net', {}).get('ok', True)
    ok = a is True and b is True and a2 is True
    return ok, 'A %s B %s%s' % (a, b, '' if 'A2_v34_path_equals_run_outside_RR_net' not in g else ' A2 %s' % a2)


def fmt(t):
    if t is None:
        return 'n/a'
    m, lo, hi = t[0], t[1], t[2]
    if m != m:
        return 'nan'
    return '%+.3f [%+.3f, %+.3f]' % (m, lo, hi)


def read_version(rec, root):
    V, lean = rec['V'], rec['lean']
    d = os.path.join(root, V, 'MARKOUT')
    cp, gp, tp = os.path.join(d, 'CURVE.tsv'), os.path.join(d, 'GATES.json'), os.path.join(d, 'TABLE_W0.tsv')
    out = dict(V=V, group=rec['group'], handoff=rec['handoff_sepdec'], lean=lean)
    out['package_ok'], out['package'] = package(gp)
    if not os.path.isfile(cp):
        out.update(gate='MISSING', gate_cells=[], gate_seen=0, clear='MISSING', clear_hits=[], package_ok=False)
        return out
    c = load_curve(cp)
    out['gate'], out['gate_cells'], out['gate_seen'] = gate(c, lean)
    out['clear'], out['clear_hits'] = clear(c, lean)
    for h in CLEAR_H:
        out['edge_' + h] = c.get((0, 'ALL', lean, h, 'CALM_EDGE', 'GROSS'))
        out['h1_' + h] = c.get((0, 'H1', lean, h, 'CALM_EDGE', 'GROSS'))
        out['h2_' + h] = c.get((0, 'H2', lean, h, 'CALM_EDGE', 'GROSS'))
        out['tough_' + h] = c.get((0, 'ALL', lean, h, 'TOUGH_EDGE', 'GROSS'))
    p = c.get((0, 'ALL', lean, 'ret_1h', 'PARENT', 'GROSS'))
    out['parents'] = p[3] if p else 'n/a'
    if os.path.isfile(tp):
        t = load_table(tp)
        out['money_TT'] = t.get((lean, 'V2_1h', 'TT', 'HONEST', 'PARENT'))
        out['money_RR'] = t.get((lean, 'V2_1h', 'RR', 'HONEST', 'PARENT'))
    else:
        out['money_TT'] = out['money_RR'] = None
    return out


def lines(R):
    kept = [r for r in R if r['group'] == 'KEPT']
    nul = {r['V']: r for r in R if r['group'] == 'CONTROL_NULL'}
    pla = {r['V']: r for r in R if r['group'] == 'CONTROL_PLANTED'}
    n_k = len(kept)
    n_gate = sum(r['gate'] == 'PASS' for r in kept)
    n_clear = sum(r['clear'] == 'CLEAR' for r in kept)
    L = {}
    L['L1'] = all(r['package_ok'] for r in kept) and n_k == 9
    L['L2'] = n_gate >= 8
    L['L3'] = n_clear >= 7
    null_clear = [v for v, r in nul.items() if r['clear'] == 'CLEAR']
    null_missing = [v for v, r in nul.items() if r['clear'] == 'MISSING'] + [v for v in ('SYN0A', 'SYN0B') if v not in nul]
    planted_bad = [v for v, r in pla.items() if r['clear'] != 'CLEAR']
    planted_missing = [v for v, r in pla.items() if r['clear'] == 'MISSING'] + [v for v in ('SYN10',) if v not in pla]
    L['L4'] = not null_clear and not null_missing and not planted_bad and not planted_missing
    if planted_bad and not planted_missing:
        verdict = 'INVALID (the planted control is not CLEAR: the side plumbing is broken; fix and rerun, read nothing)'
    elif n_gate < 6 or null_clear:
        verdict = 'FAILS'
    elif all(L.values()):
        verdict = 'WORKS'
    else:
        verdict = 'INCONCLUSIVE (missed: %s)' % ', '.join(k for k in sorted(L) if not L[k])
    return L, verdict, dict(kept=n_k, gate=n_gate, clear=n_clear, null_clear=null_clear, null_missing=null_missing,
                            planted_bad=planted_bad, planted_missing=planted_missing)


def main(a):
    if len(a) != 2:
        raise SystemExit('USAGE read_stratentry_v1.py INPUTS.tsv RECEIPTS_DIR')
    R = [read_version(x, a[1]) for x in read_inputs(a[0])]
    print('PROOF STEP 2 (PREREG_STRATENTRY_V1): lean side, before cost (GROSS), against calm moments, market in and out (TT), pct a trade')
    print('V\tgroup\thandoff\tlean\tfires\tGATE (cells of 18)\tCLEAR\tedge 15m wait0 Sep-Dec [95 pct]\tH1 / H2\tedge 1h wait0 Sep-Dec [95 pct]\tH1 / H2\t'
          'TOUGH 15m\tTOUGH 1h\tmoney V2_1h TT HONEST\tmoney V2_1h RR HONEST\tmarkout gates')
    for r in R:
        cols = [r['V'], r['group'], r['handoff'], r['lean'], str(r.get('parents', 'n/a')),
                '%s (%d of %d)' % (r['gate'], len(r['gate_cells']), r['gate_seen']), r['clear'] + ('' if not r['clear_hits'] else ' ' + ','.join(r['clear_hits']))]
        for h in CLEAR_H:
            e, a1, a2 = r.get('edge_' + h), r.get('h1_' + h), r.get('h2_' + h)
            cols += [fmt(e), '%s / %s' % ('n/a' if a1 is None else '%+.3f' % a1[0], 'n/a' if a2 is None else '%+.3f' % a2[0])]
        cols += [fmt(r.get('tough_ret_15m')), fmt(r.get('tough_ret_1h')), fmt(r.get('money_TT')), fmt(r.get('money_RR')),
                 ('OK ' if r['package_ok'] else 'NOT OK ') + r['package']]
        print('\t'.join(cols))
    L, verdict, n = lines(R)
    st = [r for r in R if r['group'] == 'STOPPED']
    print('L1 PACKAGE (every kept version: S2 markout gates A and B passed): %s (%d kept versions read)' % ('HOLDS' if L['L1'] else 'MISSED', n['kept']))
    print('L2 ENTRY (at least 8 of 9 kept pass GATE): %s (%d of %d)' % ('HOLDS' if L['L2'] else 'MISSED', n['gate'], n['kept']))
    print('L3 CLEAR (at least 7 of 9 kept are CLEAR): %s (%d of %d)' % ('HOLDS' if L['L3'] else 'MISSED', n['clear'], n['kept']))
    print('L4 NOT FOOLED (SYN0A, SYN0B not CLEAR; SYN10 CLEAR): %s (no-skill CLEAR: %s; missing: %s; planted not CLEAR: %s)' % (
        'HOLDS' if L['L4'] else 'MISSED', ','.join(n['null_clear']) or 'none', ','.join(n['null_missing'] + n['planted_missing']) or 'none',
        ','.join(n['planted_bad']) or 'none'))
    print('REPORTED: stopped versions GATE PASS %d of %d, CLEAR %d of %d; no-skill controls GATE PASS %d of %d' % (
        sum(r['gate'] == 'PASS' for r in st), len(st), sum(r['clear'] == 'CLEAR' for r in st), len(st),
        sum(r['gate'] == 'PASS' for r in R if r['group'] == 'CONTROL_NULL'), sum(1 for r in R if r['group'] == 'CONTROL_NULL')))
    print('STEP 2 VERDICT (PREREG_STRATENTRY_V1 lines): %s' % verdict)
    return R, L, verdict


if __name__ == '__main__':
    main(sys.argv[1:])
