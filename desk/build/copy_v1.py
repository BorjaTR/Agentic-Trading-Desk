#!/usr/bin/env python3
"""copy_v1.py: copy the released Alarm package into alarm/, leaving out what EXCLUDES.tsv names.

  python3 -B desk/build/copy_v1.py <release folder> <new alarm folder>

The new folder must not exist (nothing is overwritten). Every file of the release is either copied byte for byte (cp -p semantics)
(made writable by its owner: the install is read-only) or listed in EXCLUDED.tsv (path, pattern, category) beside this script. Then run scrub_v1.py on the new folder."""
import fnmatch, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rules():
    out = []
    for line in open(os.path.join(HERE, 'EXCLUDES.tsv'), encoding='utf-8'):
        if line.startswith('#') or line.startswith('pattern\t') or not line.strip():
            continue
        pat, cat, why = line.rstrip('\n').split('\t')
        out.append((pat, cat, why))
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__); return 2
    rel, dst = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if os.path.exists(dst):
        print('REFUSED: %s exists' % dst); return 2
    rs = rules(); kept = 0; gone = []
    used = {r[0]: 0 for r in rs}
    for d, _, fs in os.walk(rel):
        for f in sorted(fs):
            src = os.path.join(d, f); rp = os.path.relpath(src, rel)
            hit = next((r for r in rs if fnmatch.fnmatch(rp, r[0])), None)
            if hit:
                gone.append((rp, hit[0], hit[1])); used[hit[0]] += 1; continue
            os.makedirs(os.path.join(dst, os.path.dirname(rp)), exist_ok=True)
            shutil.copy2(src, os.path.join(dst, rp)); kept += 1
            os.chmod(os.path.join(dst, rp), os.stat(src).st_mode | 0o200)   # the install is read-only; the copy is ours to scrub
    with open(os.path.join(HERE, 'EXCLUDED.tsv'), 'w', encoding='utf-8') as fo:
        fo.write('# EXCLUDED.tsv (copy_v1.py): every file of %s left out of alarm/\npath\tpattern\tcategory\n' % os.path.basename(rel))
        for g in sorted(gone):
            fo.write('\t'.join(g) + '\n')
    unused = [p for p, n in used.items() if n == 0]
    print('COPIED %d files, EXCLUDED %d, rules unused: %s' % (kept, len(gone), unused or 'none'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
