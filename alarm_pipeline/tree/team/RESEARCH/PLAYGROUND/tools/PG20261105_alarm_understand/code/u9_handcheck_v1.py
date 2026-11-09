#!/usr/bin/env python3
"""u9_handcheck_v1.py (SCO-A136, 6 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED.
U9 hand check (spec test 9, on the GRADE job in reach): 3 fires (the first, the middle and the last of the GRADE's own fire list) printed
beside the GRADE's own rows (the fire list row, the PERFIRE A row) and the bundle's and the card's rows for the same (coin, t), so a
person can compare them by eye. Prints MATCH or DIFF per field; exit 0 when the bundle's coin, t, side equal the GRADE's for all 3,
1 otherwise. Wave fields are printed, not compared: PERFIRE's wave is labcore waves 1800 s, the card's is build_clusters (30 min gap,
4 h span), two different rules (a DIFF there is information, not a failure). Runs inside a runner job only (real receipts).
  python3 -B u9_handcheck_v1.py <runner root> <GRADE job id> <bundle dir> <card dir>"""
import sys
sys.dont_write_bytecode = True
import importlib.util, os

HERE = os.path.dirname(os.path.realpath(__file__))


def rows(p):
    L = [l.rstrip('\n').split('\t') for l in open(p) if l.strip() and not l.startswith('#')]
    return [dict(zip(L[0], r)) for r in L[1:]]


def main(argv):
    runner, job, bundle, card = argv
    sp = importlib.util.spec_from_file_location('bb', os.path.join(HERE, 'bundle_builder_v1.py'))
    BB = importlib.util.module_from_spec(sp); sp.loader.exec_module(BB)
    J = BB.find_job(runner, job); G = BB.grade_fires(J)
    lst = rows(G['list']); pf = {(r['coin'], int(float(r['t']))): r for r in rows(G['perfire']) if r['kind'] == 'A'}
    bf = {(r['coin'], int(r['t'])): r for r in rows(os.path.join(bundle, 'FIRES.tsv'))}
    cf = {(r['coin'], int(r['t'])): r for r in rows(os.path.join(card, 'T_FIRES.tsv'))}
    print('U9 hand check: job %s (%s); list %s; perfire %s (seal %s); bundle %s; card %s' % (
        job, J['name'], G['list'], G['perfire'], G['perfire_sha16'], bundle, card))
    bad = 0
    for i in sorted({0, len(lst) // 2, len(lst) - 1}):
        L = lst[i]; k = (L['coin'], int(float(L['t'])))
        P = pf.get(k, {}); B = bf.get(k, {}); C = cf.get(k, {})
        print('\nfire %d of %d: coin %s t %d' % (i + 1, len(lst), k[0], k[1]))
        print('  GRADE list   : %s' % '  '.join('%s=%s' % kv for kv in L.items()))
        print('  GRADE PERFIRE: %s' % '  '.join('%s=%s' % kv for kv in P.items()))
        print('  bundle FIRES : %s' % '  '.join('%s=%s' % kv for kv in B.items()))
        print('  card T_FIRES : %s' % '  '.join('%s=%s' % kv for kv in C.items()))
        for f, a, b in (('coin', L['coin'], B.get('coin')), ('t', str(int(float(L['t']))), B.get('t')),
                        ('side', str(int(float(L['side']))), B.get('side')), ('perfire side', P.get('side'), B.get('side')),
                        ('card side', C.get('side'), B.get('side'))):
            ok = a == b; bad += not ok
            print('  %-13s %s (%s vs %s)' % (f, 'MATCH' if ok else 'DIFF', a, b))
        print('  wave (info)  : PERFIRE wave %s size %s | card wave %s size %s month %s' % (
            P.get('wave'), P.get('wave_size'), C.get('wave'), C.get('wave_size'), C.get('month')))
    print('\nRESULT U9 %s: %d field differences on coin, t, side' % ('PASS' if bad == 0 else 'FAIL', bad))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
