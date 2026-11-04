#!/usr/bin/env python3
"""fake_detect_v2.py (SCOUT K12, 31 Oct 2026; for tests/test_month_parts_v1_2.py only): fake_detect.py (SCOUT 29 Oct) for the chain
v2_2_2, whose detect call has one more word, --gate=<FEED_GATE> (one word, empty for no gate): that word is taken out before the
argument pairs are read and written first in ARGS.txt; everything else is fake_detect.py's: it stands in for detect_aw1_rel1.py, refuses
an existing --out, writes EVENTS.tsv with per-coin rows in DESCENDING coin order inside the part, and with FAKE_FAIL_COIN in its coins
it writes its rows and then exits 2, as a refused detect."""
import sys, os, json
a0 = sys.argv[1:]
gate = [x for x in a0 if x.startswith('--gate=')]
a = [x for x in a0 if not x.startswith('--gate=')]
if len(gate) != 1:
    print('REFUSED GATE_WORD %s' % gate); sys.exit(2)
o = {a[i]: a[i + 1] for i in range(0, len(a) - 1, 2)}
out = o['--out']
if os.path.exists(out):
    print('REFUSED OUTPUT_EXISTS'); sys.exit(2)
roster = json.load(open(o['--roster']))['coins']
coins = roster if o['--coins'] == 'ALL' else o['--coins'].split(',')
if any(c not in roster for c in coins):
    print('REFUSED UNKNOWN_COIN'); sys.exit(2)
os.makedirs(out)
rows = []
for c in coins:
    j = roster.index(c)
    for t in (900 + 100 * (j % 3), 2000 + 50 * (j % 2)):     # 900, 1000, 1100: 3 and 4 digits, so a text sort differs
        rows.append('%s\t%d\t%d\t%d\tfake\tid%s%d' % (c, t, 1 if j % 2 == 0 else -1, t, c, t))
rows.sort(reverse=True)
open(os.path.join(out, 'EVENTS.tsv'), 'w').write('# fake detect part starting %s\n# selection %s\ncoin\tt\tside\tt0\ttrigger\tevent_id\n' % (coins[0], ','.join(coins)) + ''.join(r + '\n' for r in rows))
open(os.path.join(out, 'ARGS.txt'), 'w').write(gate[0] + ' ' + ' '.join(a) + '\n')
if os.environ.get('FAKE_FAIL_COIN') in coins:             # a detect that wrote rows and then refused
    print('REFUSED WORKER_RSS_CAP: fake'); sys.exit(2)
