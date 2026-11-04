#!/usr/bin/env python3
"""sync_from_dev_v1.py (SCOUT 30 Oct 2026; the owner 09:52 Berlin: "every tool we build should be copied here ... prove that they can run
only from their Alarm folder"). Copies the files a part of the alarm pipeline needs from the team's dev tree into this repository,
byte for byte, and writes what it copied, with sha16s, so anyone can check that the repository copy is the dev tree's file.

  python3 -B sync_from_dev_v1.py <dev forensics root> <part folder> [--check]
    <dev forensics root>  e.g. <LAB_REPO>/forensics
    <part folder>         e.g. Alarm/05_Profile (holds MANIFEST.tsv)
    --check               copies nothing: prints SAME / DIFFERS / MISSING for every row; exit 1 if any row is not SAME

MANIFEST.tsv (written by hand, one row per file): repo_path (relative to the part folder), dev_path (relative to the dev forensics
root), role. Every row is copied (a changed dev file replaces the repository copy: git keeps the history); a dev file that is missing
stops the run before anything is copied. SOURCES.tsv (written by this script): repo_path, dev_path, sha16, bytes, role."""
import csv, hashlib, os, shutil, sys


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def rows(part):
    with open(os.path.join(part, 'MANIFEST.tsv')) as f:
        R = [r for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')]
    seen = set()
    for r in R:
        rp = r['repo_path']
        if os.path.isabs(rp) or '..' in rp.split('/') or rp in seen:
            raise SystemExit('BAD OR REPEATED repo_path %r' % rp)
        seen.add(rp)
    return R


def main(dev, part, check=False):
    R = rows(part)
    miss = [r['dev_path'] for r in R if not os.path.isfile(os.path.join(dev, r['dev_path']))]
    if miss:
        raise SystemExit('MISSING IN DEV (nothing copied): %s' % ', '.join(miss))
    bad = 0; out = []
    for r in R:
        src = os.path.join(dev, r['dev_path']); dst = os.path.join(part, r['repo_path'])
        state = 'MISSING' if not os.path.isfile(dst) else ('SAME' if sha16(dst) == sha16(src) else 'DIFFERS')
        if check:
            bad += state != 'SAME'; print('%-8s %s' % (state, r['repo_path'])); continue
        if state != 'SAME':
            os.makedirs(os.path.dirname(dst) or '.', exist_ok=True); shutil.copyfile(src, dst)
            if sha16(dst) != sha16(src):
                raise SystemExit('COPY CHANGED THE BYTES %s' % dst)
            print('COPIED   %s' % r['repo_path'])
        out.append((r['repo_path'], r['dev_path'], sha16(dst), os.path.getsize(dst), r.get('role', '')))
    if check:
        print('rows %d, not same %d' % (len(R), bad)); return 1 if bad else 0
    with open(os.path.join(part, 'SOURCES.tsv'), 'w') as f:
        f.write('repo_path\tdev_path\tsha16\tbytes\trole\n')
        f.write(''.join('%s\t%s\t%s\t%d\t%s\n' % o for o in out))
    print('SOURCES.tsv %s (%d files)' % (sha16(os.path.join(part, 'SOURCES.tsv')), len(out)))
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) not in (2, 3) or (len(a) == 3 and a[2] != '--check'):
        raise SystemExit(__doc__.split('\n\n')[1])
    sys.exit(main(a[0], a[1], len(a) == 3))
