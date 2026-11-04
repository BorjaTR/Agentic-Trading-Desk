#!/usr/bin/env python3
"""test_pins_current_v1.py (SCOUT, 31 Oct 2026; ALARM_V1_10, SCOUT's condition 2 of 14:25:39Z to BUILD5's re-pin): no file of the
Alarm folder still names a retired sha16. A release that re-pins lists in PINS_<release>.tsv (from the re-pin tool's REPIN.tsv) every
file whose bytes changed (kind SOURCE: a changed source; REPIN: a file whose pins were re-written) with its old and new sha16, and the
files kept as history (kind KEPT: they may name old sha16s). The test reads every file of the Alarm folder as bytes and fails on any
16-hex token (also the first 16 of a longer hex run, a full sha256) equal to a retired sha16 in a file not listed KEPT, and on any
REPIN file whose sha16 is not its new one. Not stale: a file naming its OWN old sha16 (its lineage, e.g. 'a new edition of
<sha16>'), the docs (*.md) unless a row of kind CHECK names one (a .md a test reads as a code table, e.g. DEF_TEMPLATE_V4.md), and the
free text of the sync's own lists: in a SOURCES.tsv only the sha16 column (the 3rd) is a pin, and a MANIFEST.tsv holds no pin (paths
and roles).
The lesson: a stale pin failed ALARM_V1_9's proof job (J20265254).
  python3 -B test_pins_current_v1.py <Alarm folder> <PINS tsv>     exit 0 PINS CURRENT, 1 stale or not re-pinned, 2 bad input
  python3 -B test_pins_current_v1.py --self-test                    planted trees: every case caught, exit 0
PINS tsv: kind (SOURCE, REPIN, KEPT, CHECK), part, repo_path, old, new (part ROOT: repo_path is from the Alarm folder; a SOURCE row
with part and path '-' has no lineage file)."""
import hashlib
import os
import re
import sys
import tempfile

TOK = re.compile(rb'(?<![0-9a-f])[0-9a-f]{16}')


def s16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def rel(part, rp):
    return rp if part == 'ROOT' else part + '/' + rp


def load(pins):
    rows = [ln.rstrip('\n').split('\t') for ln in open(pins) if ln.strip() and not ln.startswith('#')]
    if not rows or rows[0][:5] != ['kind', 'part', 'repo_path', 'old', 'new']:
        raise ValueError('PINS HEADER %s' % (rows[0] if rows else 'EMPTY'))
    retired, repin, kept, own, check_md = {}, {}, set(), {}, set()
    for r in rows[1:]:
        if len(r) < 5:
            raise ValueError('PINS ROW %s' % r)
        kind, part, rp, old, new = r[:5]
        if kind in ('SOURCE', 'REPIN'):
            if old != new:
                retired.setdefault(old, '%s %s -> %s' % (kind, rel(part, rp), new))
                if rp != '-':
                    own.setdefault(rel(part, rp), set()).add(old)
            if kind == 'REPIN':
                repin[rel(part, rp)] = new
        elif kind == 'KEPT':
            kept.add(rel(part, rp))
        elif kind == 'CHECK':
            check_md.add(rel(part, rp))
        else:
            raise ValueError('PINS KIND %s' % kind)
    return retired, repin, kept, own, check_md


def check(alarm, retired, repin, kept, own=None, check_md=None):
    own, check_md = own or {}, check_md or set()
    bad, n = [], 0
    for d, ds, fs in os.walk(alarm):
        ds[:] = sorted(x for x in ds if x != '__pycache__')
        for f in sorted(fs):
            p = os.path.join(d, f)
            r = os.path.relpath(p, alarm)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            n += 1
            if r in kept or (r.endswith('.md') and r not in check_md):
                continue
            if f == 'MANIFEST.tsv':
                continue                                     # paths and roles: no pin
            with open(p, 'rb') as fh:
                data = fh.read()
            if f == 'SOURCES.tsv':                           # the sha16 column only; the role text is free text
                data = b'\n'.join((ln.split(b'\t') + [b'', b'', b''])[2] for ln in data.split(b'\n'))
            for m in TOK.finditer(data):
                t = m.group().decode()
                if t in retired and t not in own.get(r, ()):
                    bad.append('STALE %s names %s (%s)' % (r, t, retired[t]))
    for r, new in sorted(repin.items()):
        p = os.path.join(alarm, r)
        got = s16(p) if os.path.isfile(p) else 'MISSING'
        if got != new:
            bad.append('NOT RE-PINNED %s is %s, PINS names %s' % (r, got, new))
    return n, bad


def run(alarm, pins):
    retired, repin, kept, own, check_md = load(pins)
    n, bad = check(alarm, retired, repin, kept, own, check_md)
    for b in bad[:50]:
        print(b)
    print('%s: %d files read, %d retired sha16s, %d re-pinned files, %d kept as history, %d problems'
          % ('PINS CURRENT' if not bad else 'PINS STALE', n, len(retired), len(repin), len(kept), len(bad)))
    return 0 if not bad else 1


def self_test():
    old1, old2, new1 = 'aaaa1111bbbb2222', 'cccc3333dddd4444', 'eeee5555ffff6666'
    ok = tot = 0

    def case(name, files, pins, want_rc, want_text=''):
        nonlocal ok, tot
        tot += 1
        d = tempfile.mkdtemp(prefix='pins_')
        al = os.path.join(d, 'Alarm')
        for r, txt in files.items():
            p = os.path.join(al, r)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w') as f:
                f.write(txt)
        pf = os.path.join(d, 'PINS.tsv')
        rows = [(k, pt, rp, o, (s16(os.path.join(al, rel(pt, rp))) if nw == '@' else nw)) for k, pt, rp, o, nw in pins]
        with open(pf, 'w') as f:
            f.write('kind\tpart\trepo_path\told\tnew\n' + ''.join('\t'.join(x) + '\n' for x in rows))
        retired, repin, kept, own, check_md = load(pf)
        n, bad = check(al, retired, repin, kept, own, check_md)
        rc = 0 if not bad else 1
        good = rc == want_rc and (not want_text or any(want_text in b for b in bad))
        ok += good
        print('%s %s (rc %d%s)' % ('PASS' if good else 'FAIL', name, rc, '; ' + bad[0] if bad else ''))

    rp = [('REPIN', 'P1', 'r.sh', old2, '@')]
    case('a clean tree', {'P1/r.sh': 'ck x %s\n' % new1, 'ROOT.md': 'nothing\n'}, rp, 0)
    case('a stale token in a code file', {'P1/r.sh': 'ck x\n', 'P1/c.py': "PIN = '%s'\n" % old1},
         rp + [('SOURCE', '-', '-', old1, new1)], 1, 'STALE P1/c.py')
    case('a stale full sha256', {'P1/r.sh': 'ck x\n', 'P1/b.json': '{"sha256": "%s%s"}\n' % (old2, '0' * 48)}, rp, 1, 'STALE P1/b.json')
    case('a kept history file may name it', {'P1/r.sh': 'ck x\n', 'P1/HISTORY.tsv': 'was\t%s\n' % old2}, rp + [('KEPT', 'P1', 'HISTORY.tsv', '-', '-')], 0)
    case('a ROOT kept file', {'P1/r.sh': 'ck x\n', 'RELEASE.json': '{"was": "%s"}\n' % old2}, rp + [('KEPT', 'ROOT', 'RELEASE.json', '-', '-')], 0)
    case('a longer hex run is not the token', {'P1/r.sh': 'ck x\n', 'P1/h.txt': 'f%s\n' % old2}, rp, 0)
    case('a REPIN file not re-pinned', {'P1/r.sh': 'ck old\n'}, [('REPIN', 'P1', 'r.sh', old2, new1)], 1, 'NOT RE-PINNED P1/r.sh')
    case('a file may name its own old sha16', {'P1/r.sh': 'a new edition of %s\n' % old2}, rp, 0)
    case('a doc is not scanned', {'P1/r.sh': 'ck x\n', 'P1/README.md': 'pin %s\n' % old2}, rp, 0)
    case('a CHECK doc is scanned', {'P1/r.sh': 'ck x\n', 'P1/T.md': '| D | %s |\n' % old2}, rp + [('CHECK', 'P1', 'T.md', '-', '-')], 1, 'STALE P1/T.md')
    case('a SOURCES role text may name it', {'P1/r.sh': 'ck x\n', 'P1/SOURCES.tsv': 'repo_path\tdev_path\tsha16\tbytes\trole\nr.sh\td/r.sh\t%s\t5\twas %s\n' % (new1, old2)}, rp, 0)
    case('a SOURCES sha16 column is a pin', {'P1/r.sh': 'ck x\n', 'P1/SOURCES.tsv': 'repo_path\tdev_path\tsha16\nr.sh\td/r.sh\t%s\n' % old2}, rp, 1, 'STALE P1/SOURCES.tsv')
    case('a MANIFEST role holds no pin', {'P1/r.sh': 'ck x\n', 'P1/MANIFEST.tsv': 'repo_path\tdev_path\trole\nr.sh\td/r.sh\tpins %s\n' % old2}, rp, 0)
    case('a REPIN file missing', {'P1/x.sh': 'x\n'}, [('REPIN', 'P1', 'r.sh', old2, new1)], 1, 'MISSING')
    print('SELF-TEST %d of %d' % (ok, tot))
    return 0 if ok == tot else 1


def main(a):
    if a == ['--self-test']:
        return self_test()
    if len(a) != 2 or not os.path.isdir(a[0]) or not os.path.isfile(a[1]):
        print(__doc__)
        return 2
    try:
        return run(a[0], a[1])
    except ValueError as e:
        print('REFUSED %s' % e)
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
