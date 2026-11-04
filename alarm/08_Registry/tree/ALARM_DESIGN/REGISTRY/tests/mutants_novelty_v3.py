#!/usr/bin/env python3
"""mutants_novelty_v3.py (SCOUT, 1 Nov 2026, ALARM_V1_16): planted faults in novelty_v3.py; test_novelty_v3.py must fail on each and pass
on the unpatched copy. Copies into a fresh temp folder (never deletes; the folder is printed). python3 -B mutants_novelty_v3.py"""
import os, shutil, subprocess, sys, tempfile

H = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(H, '..', 'tools')
MUTANTS = [
    ('EXCESS_AT 0.50', 'EXCESS_AT = 0.40', 'EXCESS_AT = 0.50'),
    ('excess = near', "return m['near'] - m['base']", "return m['near']"),
    ('no excess rule', "    if ex is not None and excess(ex[2]) >= EXCESS_AT:", "    if False:"),
    ('show takes the first', "if rep.get('alarm_id') == alarm_id or name.split(' ')[0] == alarm_id:", "if True:"),
    ('show by name only', "if rep.get('alarm_id') == alarm_id or name.split(' ')[0] == alarm_id:", "if name == alarm_id:"),
    ('line drops excess', "'excess %s pts'", "''[:0] + '%s'[:0]"),
    ('excess before copy', "    for v, what in (('COPY',", "    if res and excess(max(res, key=lambda x: excess(x[2]))[2]) >= EXCESS_AT:\n        return 'NEAR', 'x', res\n    for v, what in (('COPY',"),
]


def run(d):
    e = dict(os.environ, NOVELTY_TOOLS=d)
    return subprocess.run([sys.executable, '-B', os.path.join(H, 'test_novelty_v3.py')], env=e, capture_output=True, text=True).returncode


def main():
    base = tempfile.mkdtemp(prefix='mut_novelty_v3_')
    src = open(os.path.join(TOOLS, 'novelty_v3.py')).read()
    ok = os.path.join(base, 'clean'); os.makedirs(ok)
    for f in ('novelty_v2.py', 'novelty_v3.py'):
        shutil.copy(os.path.join(TOOLS, f), ok)
    bad = 0
    rc = run(ok)
    print('clean copy: %s' % ('PASS' if rc == 0 else 'FAIL rc %d' % rc)); bad += rc != 0
    for i, (name, a, b) in enumerate(MUTANTS):
        if src.count(a) != 1:
            print('MUTANT %s: anchor found %d times' % (name, src.count(a))); bad += 1; continue
        d = os.path.join(base, 'm%d' % i); os.makedirs(d)
        shutil.copy(os.path.join(TOOLS, 'novelty_v2.py'), d)
        open(os.path.join(d, 'novelty_v3.py'), 'w').write(src.replace(a, b))
        rc = run(d)
        print('MUTANT %-24s %s' % (name, 'CAUGHT' if rc != 0 else 'SURVIVED')); bad += rc == 0
    print('MUTANTS %d, problems %d (temp %s)' % (len(MUTANTS), bad, base))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
