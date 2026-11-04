#!/usr/bin/env python3
"""fake_detect.py (SCOUT 29 Oct 2026; for tests/test_month_parts_v1.py only): stands in for detect_aw1.py. Takes the same arguments,
refuses an existing --out (as detect does), writes EVENTS.tsv with per-coin rows (rows of a coin never depend on the other coins),
in DESCENDING coin order inside the part (so the merge order is the chain's sort, not the input), and ARGS.txt with its arguments;
with FAKE_FAIL_COIN in its coins it writes its rows and then exits 2, as a refused detect."""
import sys, os, json
a = sys.argv[1:]; o = {a[i]: a[i + 1] for i in range(0, len(a) - 1, 2)}
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
open(os.path.join(out, 'ARGS.txt'), 'w').write(' '.join(a) + '\n')
if os.environ.get('FAKE_FAIL_COIN') in coins:             # a detect that wrote rows and then refused
    print('REFUSED WORKER_RSS_CAP: fake'); sys.exit(2)
