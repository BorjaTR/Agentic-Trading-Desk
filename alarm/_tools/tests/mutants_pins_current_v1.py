#!/usr/bin/env python3
"""mutants_pins_current_v1.py (SCOUT, 31 Oct 2026): planted bugs in test_pins_current_v1.py; its --self-test must fail on each.
  python3 -B mutants_pins_current_v1.py      (exit 0: the clean copy passes and every mutant is killed)"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MUTANTS = [
    ('a retired token never stale', "if t in retired and t not in own.get(r, ()):", "if False:"),
    ('a full sha256 not seen', "TOK = re.compile(rb'(?<![0-9a-f])[0-9a-f]{16}')", "TOK = re.compile(rb'\\b[0-9a-f]{16}\\b')"),
    ('docs scanned', "if r in kept or (r.endswith('.md') and r not in check_md):", "if r in kept:"),
    ('kept files scanned', "if r in kept or (r.endswith('.md') and r not in check_md):", "if r.endswith('.md') and r not in check_md:"),
    ('nothing retired', "            if old != new:\n", "            if False:\n"),
    ('a REPIN file not checked', "        if got != new:\n", "        if False:\n"),
    ('lineage not allowed', "                    own.setdefault(rel(part, rp), set()).add(old)", "                    pass"),
    ('CHECK docs skipped', "            check_md.add(rel(part, rp))", "            pass"),
    ('SOURCES role scanned', "                data = b'\\n'.join((ln.split(b'\\t') + [b'', b'', b''])[2] for ln in data.split(b'\\n'))", "                pass"),
    ('SOURCES not scanned', "            if f == 'MANIFEST.tsv':", "            if f in ('MANIFEST.tsv', 'SOURCES.tsv'):"),
]


def run(path):
    r = subprocess.run([sys.executable, '-B', path, '--self-test'], capture_output=True, text=True)
    return r.returncode, (r.stdout.strip().splitlines() or [''])[-1]


def main():
    src = open(os.path.join(HERE, 'test_pins_current_v1.py')).read()
    d = tempfile.mkdtemp(prefix='pinsmut_')
    p = os.path.join(d, 'test_pins_current_v1.py')
    with open(p, 'w') as f:
        f.write(src)
    rc, last = run(p)
    print('%s  the clean copy (%s)' % ('OK    ' if rc == 0 else 'BROKEN', last))
    alive = 0 if rc == 0 else 1
    for name, old, new in MUTANTS:
        if src.count(old) != 1:
            print('MUTANT TEXT NOT FOUND ONCE: %s' % name); alive += 1; continue
        with open(p, 'w') as f:
            f.write(src.replace(old, new))
        rc, last = run(p)
        print('%s  %s (%s)' % ('KILLED' if rc != 0 else 'ALIVE ', name, last))
        alive += rc == 0
    shutil.rmtree(d, ignore_errors=True)
    print('PLANTED BUGS %d of %d killed' % (len(MUTANTS) - (alive if alive <= len(MUTANTS) else len(MUTANTS)), len(MUTANTS)))
    return 1 if alive else 0


if __name__ == '__main__':
    sys.exit(main())
