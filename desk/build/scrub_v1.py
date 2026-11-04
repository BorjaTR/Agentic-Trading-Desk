#!/usr/bin/env python3
"""scrub_v1.py: how alarm/ was made from the released Alarm package (edition ALARM_V1_21_16 since 3 Nov 2026; the first slice used ALARM_V1_21_1).

  python3 -B desk/build/scrub_v1.py <release folder> <alarm folder> [--write]

1. Every text file of <alarm folder> (already copied from the release by copy_v1.py with the exclusions of EXCLUDES.tsv) is rewritten with the
   RULES below: machine paths, disk names, machine names and VM mounts of the lab that built the release become placeholders
   (<LAB_TREE>, <DATA_ROOT>, <SCRATCH>, ...). A placeholder is never a real folder, so a tool that still has such a default refuses
   or finds nothing instead of reading the lab's disks.
2. Pins are kept true: a file whose bytes changed has a new sha256; every other file that names the old sha16 (16 hex) or the old
   full sha256 gets the new one (pages, .md, keep the release's numbers as records: two pages that name each other never settle),
   and this repeats until nothing changes (pins form a chain: a template pins a table, the queue pins
   the template). So every `ck <file> <sha16>` and every pin table still matches the bytes in this repo.
3. PIN_MAP.tsv (file, release sha16, repo sha16) is written beside this script: the record of every changed file.
No file is deleted; only files inside <alarm folder> are written; --write is needed to write anything (else a dry report).
The patterns are spelled out here on purpose: this file is the one place that names them (desk/PATH_ALLOW.tsv lists it)."""
import hashlib, os, re, sys

# 3 Nov 2026 (ALARM_V1_21_16 copy): the '<LAB_TREE>' rule is gone, so the lab tree reads '<LAB_REPO>/forensics' and pin records that
# split paths at '/forensics/' still parse; the '~/mnt', '$HOME/mnt' and '/mnt/dev' rules are gone: they name no person or machine, and
# the path checkers' own tests plant exactly those texts.
RULES = [
    (r'/Users/borja/dev/TradingPlatform_repo/volat-agent', '<LAB_REPO>'),
    (r'/Users/borja/dev/TradingPlatform_repo', '<LAB_REPO_ROOT>'),
    (r'/Users/borja/dev/TradingPlatform/volat-agent', '<RUNNER_TREE>'),
    (r'/Users/borja/dev/venvs/analyst/bin/python3', '<PYTHON>'),
    (r'/Users/borja/dev/venvs/analyst', '<VENV>'),
    (r'/Users/borja/volat_store', '<DATA_ROOT>'),
    (r'/Users/borja/volat_release', '<RELEASE_ROOT>'),
    (r'/Users/borja/Documents/GitHub/Trading', '<PUBLIC_COPY>'),
    (r'/Users/borja/dev', '<DEV>'),
    (r'/Users/borja', '<HOME>'),
    (r'/Volumes/WDBLACK/judge_scratch', '<SCRATCH>'),
    (r'/Volumes/WDBLACK', '<SCRATCH_DISK>'),
    (r'/Volumes/SEAGATE8', '<ARCHIVE_DISK>'),
    (r'/Volumes/Expansion', '<ARCHIVE_DISK2>'),
    (r'/Volumes/[A-Za-z0-9_]+', '<DISK>'),
    (r'/sessions/rcw-[a-z0-9]+', '<VM_SESSION>'),
    (r'/home/claude', '<VM_HOME>'),
    (r'/mnt/user-data', '<VM_UPLOADS>'),
    (r'/mnt/project-files', '<VM_PROJECT>'),
    (r'SETTINGS_MAC_MINI', 'SETTINGS_LOCAL'),
    (r'[Mm]ac [Mm]ini', 'lab machine'),
    (r'\bWDBLACK\b', 'SCRATCH_DISK'),
    (r'\bSEAGATE8\b', 'ARCHIVE_DISK'),
    (r'borja', 'owner'),
    (r'Borja', 'the owner'),
]
COMPILED = [(re.compile(a), b) for a, b in RULES]
HEX16 = re.compile(r'(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])')
HEX64 = re.compile(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')


def scrub_text(t):
    for rx, rep in COMPILED:
        t = rx.sub(rep, t)
    return t


def sha(b):
    return hashlib.sha256(b).hexdigest()


def files(root):
    out = []
    for d, _, fs in os.walk(root):
        for f in fs:
            out.append(os.path.join(d, f))
    return sorted(out)


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    rel_root, root = argv[0], argv[1]; write = '--write' in argv
    texts = {p: open(p, encoding='utf-8').read() for p in files(root)}
    orig = {p: sha(t.encode()) for p, t in texts.items()}
    new = {p: scrub_text(t) for p, t in texts.items()}
    hist = {p: {orig[p]} for p in new}                     # every sha a file had: a pin may name any of them
    for it in range(60):
        cur = {p: sha(t.encode()) for p, t in new.items()}
        m64 = {}
        for p in new:
            for h in hist[p]:
                if h != cur[p]:
                    m64[h] = cur[p]
        m16 = {a[:16]: b[:16] for a, b in m64.items()}
        changed = 0
        for p, t in new.items():
            if p.endswith('.md'):                         # pages are records: they keep the release's sha16 (a page pinning a page cycles)
                continue
            t2 = HEX64.sub(lambda m: m64.get(m.group(0), m.group(0)), t)
            t2 = HEX16.sub(lambda m: m16.get(m.group(0), m.group(0)), t2)
            if t2 != t:
                new[p] = t2; changed += 1
        for p in new:
            hist[p].add(cur[p])
        if not changed:
            break
    final = {p: sha(t.encode()) for p, t in new.items()}
    rows = [(os.path.relpath(p, root), sha(texts[p].encode())[:16], final[p][:16]) for p in sorted(new) if new[p] != texts[p]]
    print('rounds %d, files changed %d of %d' % (it + 1, len(rows), len(new)))
    if write:
        for p in new:
            if new[p] != texts[p]:
                with open(p, 'w', encoding='utf-8') as f:
                    f.write(new[p])
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, 'PIN_MAP.tsv'), 'w') as f:
            f.write('# PIN_MAP.tsv (scrub_v1.py): every file of alarm/ whose bytes differ from the release %s\n' % os.path.basename(os.path.abspath(rel_root)))
            f.write('file\trelease_sha16\trepo_sha16\n')
            for r in rows:
                f.write('\t'.join(r) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
