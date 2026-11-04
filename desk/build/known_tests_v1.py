#!/usr/bin/env python3
"""known_tests_v1.py: write the KNOWN reasons of desk/build/KNOWN_TESTS.tsv into alarm/_tools/TESTS.tsv (column 7), and empty the view of a
row marked drop_view. Every row of KNOWN_TESTS.tsv must match exactly one TESTS.tsv row (by its test path), else it refuses and writes
nothing. Run after copy_v1.py and scrub_v1.py.   python3 -B desk/build/known_tests_v1.py [<alarm folder>]"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(a):
    alarm = a[0] if a else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'alarm')
    p = os.path.join(alarm, '_tools', 'TESTS.tsv')
    known = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'KNOWN_TESTS.tsv')) if not l.startswith('#') and not l.startswith('test\t') and l.strip()]
    lines = open(p).read().split('\n')
    for test, reason, drop in known:
        hits = [i for i, l in enumerate(lines) if not l.startswith('#') and len(l.split('\t')) > 1 and l.split('\t')[1] == test]
        if len(hits) != 1:
            print('REFUSED: %s matches %d rows' % (test, len(hits))); return 2
        f = lines[hits[0]].split('\t') + [''] * 7
        f = f[:max(7, len(lines[hits[0]].split('\t')))]
        f[6] = reason
        if drop == 'yes':
            f[4] = ''
        lines[hits[0]] = '\t'.join(f)
    open(p + '.tmp', 'w').write('\n'.join(lines)); os.replace(p + '.tmp', p)
    print('KNOWN written: %d rows of %s' % (len(known), p)); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
