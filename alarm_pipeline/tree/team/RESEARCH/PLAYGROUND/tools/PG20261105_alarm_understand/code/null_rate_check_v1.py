#!/usr/bin/env python3
"""null_rate_check_v1.py (SCO-A9, 5 Nov 2026): the U7 null (test_alarm_understand_v1.null_bundle) on seeds the test never uses, to see
the STRONG rate of the fixed word rule on fresh nulls. Planted data only. Usage: python3 -B null_rate_check_v1.py <first seed> <count>"""
import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import test_alarm_understand_v1 as TT

first, count = int(sys.argv[1]), int(sys.argv[2])
c = TT.ctx(); strong = []; cards = 0; zmax = []
for seed in range(first, first + count):
    card = TT.AU.build_card(TT.null_bundle(seed), c); cards += 1
    zs = [abs(r['z']) for r in TT.table(card, 'T_WHERE') if r['slice'] == 'ALL' and r['tag'] == 'ASOF' and r['z'] == r['z']]
    zmax.append(max(zs))
    strong += [(seed, r['q']) for r in card['rows'] if r['word'] == 'STRONG']
print('seeds %d..%d: STRONG words %d of %d (cards with one: %d of %d); z_crit %.2f; largest |z| of a card: median %.2f, max %.2f'
      % (first, first + count - 1, len(strong), cards * 8, len({s for s, q in strong}), cards, card['meta']['z_crit'],
         sorted(zmax)[len(zmax) // 2], max(zmax)), strong)
