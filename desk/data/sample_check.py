#!/usr/bin/env python3
"""sample_check.py: the desk's fixed test sample of one-format data (owner decision 3 Nov 2026 21:34Z: V1 tests run on the lab's own
one-format data, read-only, a small fixed sample of days and coins named in a manifest; no download).

  python3 -B desk/data/sample_check.py <lab_days folder> [--manifest desk/data/SAMPLE_MANIFEST_V1.tsv]
  python3 -B desk/data/sample_check.py <lab_days folder> --make <day,day> <coin,coin> <part,part>   (writes the manifest, once)

The manifest names each day, part and coin of the sample and the sha16 of that part's index.json (the index pins every payload block of
the part through the lab3 reader). check: every listed index.json exists under <lab_days>/day=<D>/<part>/ with that sha16, and every
listed coin is in that index's coins (coins '-' = a part with no coin list, e.g. PCT's market tables). Reads only index files; writes nothing (except --make, which refuses an existing manifest).
Exit 0 SAMPLE OK, 3 a file missing or changed, 2 refused."""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEF = os.path.join(HERE, 'SAMPLE_MANIFEST_V1.tsv')


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def make(lab, days, coins, parts, out):
    if os.path.exists(out):
        print('REFUSED: %s exists' % out); return 2
    rows = []
    for d in days:
        for p in parts:
            ix = os.path.join(lab, 'day=%s' % d, p, 'index.json')
            got = json.load(open(ix)).get('coins')
            miss = [c for c in coins if got is not None and c not in got]
            if miss:
                print('REFUSED: %s %s lacks %s' % (d, p, miss)); return 2
            rows.append((d, p, ','.join(coins) if got is not None else '-', sha16(ix)))
    with open(out, 'x') as f:
        f.write('# SAMPLE_MANIFEST_V1: the desk test sample (days 2025 only), one row a day and part; sha16 = that part\'s index.json\nday\tpart\tcoins\tindex_sha16\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print('WROTE %s: %d rows' % (out, len(rows))); return 0


def check(lab, man):
    bad = 0; n = 0
    for line in open(man):
        if line.startswith('#') or line.startswith('day\t') or not line.strip():
            continue
        d, p, coins, want = line.rstrip('\n').split('\t'); n += 1
        if not d.startswith('2025'):
            print('REFUSED: %s: the sample holds 2025 days only' % d); return 2
        ix = os.path.join(lab, 'day=%s' % d, p, 'index.json')
        if not os.path.isfile(ix):
            print('MISSING %s' % ix); bad += 1; continue
        if sha16(ix) != want:
            print('CHANGED %s (want %s, have %s)' % (ix, want, sha16(ix))); bad += 1; continue
        miss = [] if coins == '-' else [c for c in coins.split(',') if c not in json.load(open(ix)).get('coins', [])]
        if miss:
            print('COINS MISSING %s %s' % (ix, miss)); bad += 1
    print('SAMPLE %s: %d rows, %d bad (%s)' % ('OK' if not bad else 'FAILED', n, bad, lab))
    return 0 if not bad else 3


def main(a):
    if not a:
        print(__doc__); return 2
    lab = a[0]
    man = a[a.index('--manifest') + 1] if '--manifest' in a else DEF
    if '--make' in a:
        i = a.index('--make')
        return make(lab, a[i + 1].split(','), a[i + 2].split(','), a[i + 3].split(','), man)
    return check(lab, man)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
