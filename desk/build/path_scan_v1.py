#!/usr/bin/env python3
"""path_scan_v1.py: the clean repo holds no trace of the lab that built it.

  python3 -B desk/build/path_scan_v1.py [<repo folder>] [--allow <PATH_ALLOW.tsv>] [--show N]

Every text file of the repo (out/ and data/ are outputs, .twins/ the never-shipped copies and .git/ the git metadata, never scanned; .DS_Store,
*.pre_* copies (ignored by .gitignore, never shipped) and desk/PATH_ALLOW.tsv itself are skipped) is searched, line by line, for:
  OWNER      the owner's name, any case
  USER_PATH  a home folder /Users/<name> (a placeholder such as <HOME> never matches)
  MACHINE    the lab's machine and disk names (mac mini, the scratch and archive disk names, 'Expansion' with a capital E)
  HOST       an internal host name or address: <name>.local / .lan / .internal / .ts.net, tailscale, 10.x, 192.168.x, 172.16-31.x
  SEAT_REQ   a lab seat named as something the user must do or have: a board path hb/..., 'ask <SEAT>', a SEAT(S)= list
Each hit is allowed only when a row of PATH_ALLOW.tsv (default desk/PATH_ALLOW.tsv) names its file (fnmatch, '*' crosses '/'),
its kind and a text the line holds, with a reason. A row that allows nothing is reported (an allow list must not rot).
Exit 0 clean (every hit allowed, every row used), 3 a hit not allowed or a row unused, 2 refused."""
import fnmatch, os, re, sys

SEATS = r'(?:LAB[1-4]|SCOUT|QUANT|DSK|LEAD|STRATEGY|LAYERS|LIVE[45]|BUILD[1-5]|TEST[12]|UI|FIND|CONDUCTOR|RELEASE|EDGE[12]|BED|TREE|ALARMLIB)'
KINDS = [
    ('OWNER', re.compile(r'(?i)borja')),
    ('USER_PATH', re.compile(r'/Users/[A-Za-z0-9_.-]+')),
    ('MACHINE', re.compile(r'(?i)mac[ _-]?mini|WDBLACK|SEAGATE|/Volumes/Expansion|(?-i:\bExpansion\b)')),
    ('HOST', re.compile(r'(?i)\b[a-z0-9-]+\.(?:local|lan|internal|ts\.net)\b(?<!threading\.local)|tailscale|\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b|\b192\.168\.\d{1,3}\.\d{1,3}\b|\b172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}\b')),
    ('SEAT_REQ', re.compile(r'\bhb/|\bask (?:the )?' + SEATS + r'\b|\bSEATS? ?=')),
]
SKIP_DIRS = ('out', 'data', '.twins', '.git')        # .twins: the build's own copies before each edit, never shipped; .git: git's own metadata
ALLOW_REL = os.path.join('desk', 'PATH_ALLOW.tsv')   # the allow list quotes the texts it allows: it is not scanned itself


def allow_rows(path):
    rows = []
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        if line.startswith('#') or line.startswith('file\t') or not line.strip():
            continue
        f = line.rstrip('\n').split('\t')
        if len(f) != 4 or not all(f[i].strip() for i in (0, 1, 3)):
            raise SystemExit('REFUSED: %s line %d: 4 columns file, kind, text, reason; only text may be empty (any line)' % (path, n))
        if f[1] not in [k for k, _ in KINDS]:
            raise SystemExit('REFUSED: %s line %d: unknown kind %s' % (path, n, f[1]))
        rows.append({'file': f[0], 'kind': f[1], 'text': f[2], 'reason': f[3], 'used': 0, 'line': n})
    return rows


def scan(repo, rows):
    bad = []; ok = 0; files = 0
    for d, ds, fs in os.walk(repo):
        if d == repo:
            ds[:] = [x for x in ds if x not in SKIP_DIRS]
        ds.sort()
        for f in sorted(fs):
            p = os.path.join(d, f); rp = os.path.relpath(p, repo)
            if f == '.DS_Store' or rp == ALLOW_REL or '.pre_' in f:     # *.pre_*: edit copies, ignored by .gitignore
                continue
            try:
                text = open(p, encoding='utf-8').read()
            except UnicodeDecodeError:
                text = open(p, encoding='latin-1').read()
            files += 1
            for i, line in enumerate(text.split('\n'), 1):
                for kind, rx in KINDS:
                    for m in rx.finditer(line):
                        hit = next((r for r in rows if r['kind'] == kind and fnmatch.fnmatch(rp, r['file']) and r['text'] in line), None)
                        if hit:
                            hit['used'] += 1; ok += 1
                        else:
                            bad.append((rp, i, kind, m.group(0), line.strip()[:160]))
    return files, ok, bad


def main(argv):
    repo = os.path.abspath(argv[0]) if argv and not argv[0].startswith('--') else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    allow = argv[argv.index('--allow') + 1] if '--allow' in argv else os.path.join(repo, 'desk', 'PATH_ALLOW.tsv')
    show = int(argv[argv.index('--show') + 1]) if '--show' in argv else 40
    if not os.path.isfile(allow):
        print('REFUSED: no allow list %s' % allow); return 2
    rows = allow_rows(allow)
    files, ok, bad = scan(repo, rows)
    unused = [r for r in rows if not r['used']]
    by = {}
    for b in bad:
        by[b[2]] = by.get(b[2], 0) + 1
    for b in bad[:show]:
        print('HIT %s:%d %s %r | %s' % b)
    for r in unused:
        print('UNUSED ALLOW line %d: %s %s %r' % (r['line'], r['file'], r['kind'], r['text']))
    print('PATH SCAN %s: %d files, %d hits allowed by %d rows, %d not allowed %s, %d rows unused' % (
        'CLEAN' if not bad and not unused else 'FAILED', files, ok, len(rows), len(bad), by or '', len(unused)))
    return 0 if not bad and not unused else 3


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
