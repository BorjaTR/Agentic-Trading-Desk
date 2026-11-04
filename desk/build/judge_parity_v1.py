#!/usr/bin/env python3
"""judge_parity_v1.py: prove the judge in alarm/ is the released judge.

  python3 -B desk/build/judge_parity_v1.py <release folder> [<alarm folder>] [--out <PARITY.tsv>]

For every judge module named in JUDGE below, and every .py file it loads by name (a quoted '<name>.py' that exists beside it or under
the package root, or an 'import <name>' of a file beside it), followed to the end, each file of alarm/ is compared with the same path of
the release:
  IDENTICAL      the bytes are equal
  SAME_AFTER_SCRUB  the repo bytes equal scrub_v1.scrub_text(release text): only the path and name replacements, no pin changed
  SAME_AFTER_SCRUB_AND_PINS  as above plus sha16 pins re-pointed by scrub_v1: each pin release>repo listed and each is a row of
                 PIN_MAP.tsv (the pinned file's own release and repo sha16), composed with PIN_MAP_V2.tsv when fix_pins_v2.py
                 ran (release sha16 > final repo sha16), else DIFFERENT
  DIFFERENT      anything else (fails)
Exit 0 when no file is DIFFERENT and every named judge module exists; 3 otherwise."""
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_v1  # noqa: E402

JUDGE = [
    ('decide_v5', 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v5.py'),
    ('decide_v6', 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/decide_v6.py'),
    ('audit_run_v5', 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/audit_run_v5.py'),
    ('true_gate_v3', '03_Grading/tree/tools/true_gate/true_gate_v3.py'),
    ('menu_gate_v1', 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/menu_gate_v1.py'),
    ('tried_search_v1', '08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py'),
    ('wave_gap_v1', 'Agentic/tree/ALARM_DESIGN/KIT_V5/tools/wave_gap_v1.py'),
    ('waves', '01_Detection/tree/team/RESEARCH/tools/labcore/waves.py'),
    ('waves', '06_First_look/tree/tools/labcore/waves.py'),
    ('waves', '07_Price_path/tree/team/RESEARCH/tools/labcore/waves.py'),
    ('waves', '07_Price_path/tree/tools/labcore/waves.py'),
    ('gates', '01_Detection/tree/team/RESEARCH/tools/labcore/gates.py'),
    ('gates', '07_Price_path/tree/team/RESEARCH/tools/labcore/gates.py'),
    ('gates', '07_Price_path/tree/tools/labcore/gates.py'),
    ('jobgate', '01_Detection/tree/team/RESEARCH/tools/labcore/jobgate.py'),
    ('jobgate', '07_Price_path/tree/team/RESEARCH/tools/labcore/jobgate.py'),
    ('jobgate', '07_Price_path/tree/tools/labcore/jobgate.py'),
    ('law', '01_Detection/tree/team/LAB3/code/lab3/law.py'),
    ('law', '07_Price_path/tree/team/LAB3/code/lab3/law.py'),
    ('law', '_vendor/LAB3_code/lab3/law.py'),
]
QPY = re.compile(r"['\"]([A-Za-z0-9_./-]+\.py)['\"]")
IMP = re.compile(r'^\s*(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)', re.M)
HEX16 = re.compile(r'(?<![0-9a-f])[0-9a-f]{16}(?![0-9a-f])')


BYNAME = {}


def by_name(alarm, n):
    """a bare file name loaded through a settings path (e.g. <Alarm>/_tools/settings_v1.py): the one file of that name in the package,
    fixtures and archive left out; none or several = not followed (listed as UNRESOLVED)"""
    if not BYNAME:
        for d, _, fs in os.walk(alarm):
            for f in fs:
                r = os.path.relpath(os.path.join(d, f), alarm)
                if '/fixtures/' not in '/' + r and '/archive/' not in '/' + r:
                    BYNAME.setdefault(f, []).append(r)
    c = BYNAME.get(os.path.basename(n), [])
    return c[0] if len(c) == 1 else None


def loads(alarm, rp):
    d = os.path.dirname(rp); out = set(); t = open(os.path.join(alarm, rp), encoding='utf-8').read()
    for m in QPY.finditer(t):
        n = m.group(1)
        for c in (os.path.normpath(os.path.join(d, n)), os.path.normpath(n), by_name(alarm, n)):
            if c and os.path.isfile(os.path.join(alarm, c)):
                out.add(c); break
    for m in IMP.finditer(t):
        c = os.path.join(d, m.group(1) + '.py')
        if os.path.isfile(os.path.join(alarm, c)):
            out.add(c)
    out.discard(rp)
    return out


def verdict(rel, alarm, rp):
    a = os.path.join(rel, rp); b = os.path.join(alarm, rp)
    if not os.path.isfile(a):
        return 'NOT_IN_RELEASE', ''
    ra, rb = open(a, 'rb').read(), open(b, 'rb').read()
    if ra == rb:
        return 'IDENTICAL', ''
    sa = scrub_v1.scrub_text(ra.decode('utf-8'))
    if sa.encode() == rb:
        return 'SAME_AFTER_SCRUB', ''
    pins = []
    la, lb = sa.split('\n'), rb.decode('utf-8').split('\n')
    if len(la) == len(lb):
        ok = True
        for x, y in zip(la, lb):
            if x != y:
                if HEX16.sub('#', x) != HEX16.sub('#', y):
                    ok = False; break
                pins += ['%s>%s' % (p, q) for p, q in zip(HEX16.findall(x), HEX16.findall(y)) if p != q]
        if ok:
            return 'SAME_AFTER_SCRUB_AND_PINS', ' '.join(pins)
    return 'DIFFERENT', ''


def main(argv):
    if not argv:
        print(__doc__); return 2
    rel = os.path.abspath(argv[0])
    alarm = os.path.abspath(argv[1]) if len(argv) > 1 and not argv[1].startswith('--') else os.path.join(os.path.dirname(os.path.dirname(HERE)), 'alarm')
    out = argv[argv.index('--out') + 1] if '--out' in argv else None
    m1 = {}                                       # file -> (release sha16, repo sha16 after scrub_v1)
    for line in open(os.path.join(HERE, 'PIN_MAP.tsv'), encoding='utf-8'):
        f = line.rstrip('\n').split('\t')
        if len(f) == 3 and not line.startswith('#') and f[0] != 'file':
            m1[f[0]] = (f[1], f[2])
    m2 = {}                                       # file -> (sha16 before the first fix step, after the last), the fix steps in order
    for step in ('PIN_MAP_V2.tsv', 'PIN_MAP_V3.tsv'):
        p2 = os.path.join(HERE, step)
        if not os.path.isfile(p2):
            continue
        for line in open(p2, encoding='utf-8'):
            f = line.rstrip('\n').split('\t')
            if len(f) == 4 and not line.startswith('#') and f[0] != 'file':
                m2[f[0]] = (m2[f[0]][0] if f[0] in m2 else f[1], f[2])
    pinmap = set()                                # release sha16 > final repo sha16, per file, through both steps
    for fn in set(m1) | set(m2):
        if fn in m2 and m2[fn][0] == '-':
            rp = os.path.join(rel, fn)
            if not os.path.isfile(rp):
                continue
            r0 = hashlib.sha256(open(rp, 'rb').read()).hexdigest()[:16]
        else:
            r0 = m1[fn][0] if fn in m1 else m2[fn][0]
        pinmap.add('%s>%s' % (r0, m2[fn][1] if fn in m2 else m1[fn][1]))
    rows = []; seen = {}; todo = []; bad = 0
    for name, rp in JUDGE:
        if not os.path.isfile(os.path.join(alarm, rp)):
            rows.append((name, rp, 'MISSING', '', '', '')); bad += 1; continue
        todo.append((name, rp, 'named'))
    while todo:
        name, rp, why = todo.pop(0)
        if rp in seen:
            continue
        seen[rp] = 1
        v, pins = verdict(rel, alarm, rp)
        sh = hashlib.sha256(open(os.path.join(alarm, rp), 'rb').read()).hexdigest()[:16]
        shr = hashlib.sha256(open(os.path.join(rel, rp), 'rb').read()).hexdigest()[:16] if os.path.isfile(os.path.join(rel, rp)) else ''
        stray = [x for x in pins.split() if x not in pinmap]
        if stray:
            v = 'DIFFERENT'; pins = 'pin not in PIN_MAP: ' + ' '.join(stray)
        rows.append((name, rp, v, shr, sh, (pins + '; ' if pins else '') + why))
        bad += v in ('DIFFERENT', 'NOT_IN_RELEASE')
        for c in sorted(loads(alarm, rp)):
            todo.append((name, c, 'loaded by ' + os.path.basename(rp)))
    lines = ['judge\tfile\tverdict\trelease_sha16\trepo_sha16\tnote']
    lines += ['\t'.join(r) for r in rows]
    if out:
        with open(out, 'x') as f:
            f.write('# judge_parity_v1.py: %s vs alarm/\n' % os.path.basename(rel) + '\n'.join(lines) + '\n')
    print('\n'.join(lines))
    cnt = {}
    for r in rows:
        cnt[r[2]] = cnt.get(r[2], 0) + 1
    print('JUDGE PARITY %s: %d files %s' % ('OK' if not bad else 'FAILED', len(rows), cnt))
    return 0 if not bad else 3


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
