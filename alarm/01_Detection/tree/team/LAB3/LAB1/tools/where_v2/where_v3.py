#!/usr/bin/env python3
"""where_v3.py: find a metric or value code by its code, its name or words of its meaning, in the metric tables of this Alarm folder only.

Owner: LAB1 (the map's owner; where_v2 was built by the FIND thread, 23 Oct 2026). New edition by SCOUT for the clean release (K7, 30 Oct
2026; the owner 23:07 Berlin: "All alarm tools should work from the release folder only"; agents must "know instantly how to use each tool
and where everything is and all metrics"). Old file: team/LAB3/LAB1/tools/where_v2/where_v2.py e6509fad2142c917, untouched: it stays the
dev tree's team-map finder. This edition calls, imports and reads no old edition.

  python3 -B where_v3.py <code, name or words> [--kind metric|code] [--n 5] [--safe] [--settings <settings file>]
    --kind      metric: METRICS_V1 (the LAB.* readings too: LAB_READINGS_MEANING_V1 is their card), the HL candidates, and the rows of
                the register METRICS_V2 that both lack; code: the value catalogues CTX, EPI, STAMP, FEED and LIVELAYER
    --n         hits to print (default 5)
    --safe      as where_v2 (it leaves out register rows; this edition has none)
    --settings  optional: checked by _tools/settings_v1.py (this tool reads no data)
  Then read every code before using it: metric_brief_v2.py <CODE> (01_Detection/tree/team/RESEARCH/LEAD/skills/reading-metrics/scripts).

Each hit prints, as where_v2: [kind] code | owner | from <table>; the card's or the table's path; what it is; how to read it. A metric
the register METRICS_V2 marks DROPPED (register_status) says DROPPED after its code; a card not inside this Alarm folder says GONE TODAY.
Kept from where_v2: the records of kinds metric and code, the search (words, score, order, one hit per code) and the print of a hit.
What changed:
  - the tables are read only inside the Alarm folder that holds this file (found by _tools/settings_v1.alarm_root), in its detection tree
    01_Detection/tree/ (the dev tree's layout); paths print under that tree; a missing table is refused (exit 2), never skipped;
  - new: the register METRICS_V2 (its DROPPED rows, and the 12 HL readings METRICS_V1 and the candidates lack);
  - the team map's kinds (seat, producer, tool, skill, doc, data, guide, map, register) and --check stay in where_v2: they read the
    team's folders, which are not in the release;
  - NOT FOUND names the tables searched.
Read only. Exit 0 found; 1 NOT FOUND; 2 refused."""
import csv, os, re, sys

DETECTION_TREE = ('01_Detection', 'tree')
METRICS = 'LAB3/METRICS_V1.tsv'                                   # under the tree's team/ folder, as where_v2 wrote them
CANDIDATES = 'LAB3/METRICS_HL_CANDIDATE_V2.tsv'
CATALOGS = ('LAB3/METRICS_V1.tsv', 'RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv',
            'RESEARCH/tools/alarm_stamp/STAMP_CATALOG_V1.tsv', 'FEED/CATALOG_V1.tsv', 'LIVELAYER/CATALOG_V1.tsv')
REGISTER = 'LAB3/METRICS_V2.tsv'
TABLES = (METRICS, CANDIDATES) + CATALOGS[1:] + (REGISTER,)
KIND_RANK = {'seat': 0, 'producer': 1, 'tool': 2, 'guide': 3, 'data': 4, 'metric': 4, 'code': 5, 'skill': 6, 'doc': 7, 'map': 8, 'register': 9}
STOP = set('a an and any are at by do does each every file files folder for from give how in is it its me of on or the this to what where which who with'.split())
ROOT_CUT = re.compile(r'^(?:\S*?/)?volat-agent/forensics/')       # where_v2 cut the dev tree's root (written in its code) before a path


class Refused(Exception):
    pass


def settings_module(start):
    """_tools/settings_v1.py of the Alarm folder that holds `start` (the nearest parent folder that has it), imported"""
    d = os.path.dirname(os.path.abspath(start))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM FOLDER %s (run the copy inside the Alarm folder)' % os.path.abspath(start))
        d = os.path.dirname(d)
    sys.path.insert(0, os.path.join(d, '_tools'))
    try:
        import settings_v1
    finally:
        sys.path.pop(0)
    return settings_v1


def detection_tree(start, S):
    """<Alarm>/01_Detection/tree of the Alarm folder that holds `start` (settings_v1.alarm_root)"""
    return os.path.join(S.alarm_root(start), *DETECTION_TREE)


def check_tables(tree):
    miss = [t for t in TABLES if not os.path.isfile(os.path.join(tree, 'team', *t.split('/')))]
    if miss:
        raise Refused('MISSING TABLE %s under %s (the Alarm folder must hold it)' % (', '.join('team/' + t for t in miss), tree))


def rel(p):
    """a path as the team writes it: relative to the forensics root (the detection tree here); trailing sha16 dropped"""
    p = (p or '').strip()
    if not p or p == '-': return ''
    t = p.split()
    if len(t) >= 2 and re.fullmatch(r'[0-9a-f]{8,16}', t[-1]): p = ' '.join(t[:-1])
    m = ROOT_CUT.match(p)
    if m: return p[m.end():]
    if p.startswith('F/'): return p[2:]
    return p


def on_disk(p, tree):
    r = rel(p)
    if not r or '<' in r or '*' in r: return None                 # a pattern, not a file: not checkable
    return os.path.exists(r if r.startswith('/') else os.path.join(tree, r))


def tsv(path):
    for l in open(path, errors='replace'):
        l = l.rstrip('\n')
        if l.strip(): yield l


def records(tree):
    """every findable code: (kind, name, path, what, doc, owner, source); and the codes the register marks DROPPED"""
    T = os.path.join(tree, 'team')
    R = []
    add = lambda *a: R.append(a)
    mrows = [l.split('\t') for l in tsv(os.path.join(T, METRICS)) if not l.startswith('#')]
    h = mrows[0]; ix = {k: h.index(k) for k in h}
    for r in mrows[1:]:
        r += [''] * (len(h) - len(r))
        add('metric', r[0], rel(r[ix['card']].split(';')[0].split()[0]) if r[ix['card']].strip() else '',
            '%s | %s | unit %s | store %s' % (r[ix['short']], r[ix['meaning']], r[ix['unit']], r[ix['store']]),
            'read: %s' % r[ix['read_as']][:200], 'LAB1 (METRICS_V1); proof LAB4', 'team/LAB3/METRICS_V1.tsv')
    # Owner-requested discovery of unsigned HL candidates (where_v2): not adoption, not approval
    with open(os.path.join(T, CANDIDATES)) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            add('metric', r['code'], rel(r['card']),
                'UNSIGNED CANDIDATE | %s | unit %s | output %s' % (r['meaning'], r['unit'], r['store']),
                r['read_as'], 'OX-DATA; independent approval pending', 'team/' + CANDIDATES)
    # value codes of the other catalogues
    for c in CATALOGS[1:]:
        p = os.path.join(T, c)
        rows = [l.split('\t') for l in tsv(p) if not l.startswith('#')]
        hh = rows[0]; mi = hh.index('meaning') if 'meaning' in hh else 1
        for r in rows[1:]:
            name = r[0] if 'code' in hh[:1] else '%s.%s' % (r[0], r[hh.index('column')]) if 'column' in hh else r[0]
            add('code', name, 'team/' + c, r[mi] if len(r) > mi else '', 'team/' + os.path.dirname(c) + '/README.md', '-', 'team/' + c)
    # new: the register METRICS_V2 (LAYERS): the rows METRICS_V1 and the candidates lack, and the DROPPED codes
    known = {x[1] for x in R if x[0] == 'metric'}
    vrows = [l.split('\t') for l in tsv(os.path.join(T, REGISTER)) if not l.startswith('#')]
    h = vrows[0]; ix = {k: h.index(k) for k in h}; dropped = set()
    for r in vrows[1:]:
        r += [''] * (len(h) - len(r))
        if r[ix['register_status']].strip() == 'DROPPED':
            dropped.add(r[0])
        if r[0] in known:
            continue
        add('metric', r[0], rel(r[ix['card']].split(';')[0].split()[0]) if r[ix['card']].strip() else '',
            '%s | %s | unit %s | store %s' % (r[ix['short']], r[ix['meaning']], r[ix['unit']], r[ix['store']]),
            'read: %s' % r[ix['read_as']][:200], 'LAYERS (METRICS_V2 register)', 'team/' + REGISTER)
    return R, dropped


def search(R, q, kind=None, n=8):
    ql = q.lower().strip()
    words = [w for w in re.split(r"[\s,?'\"]+", ql) if w and w not in STOP] or [ql]
    need = max(1, (len(words) + 1) // 2)
    out = []
    for r in R:
        if kind and r[0] != kind: continue
        name, path, what = r[1].lower(), r[2].lower(), r[3].lower()
        s = 0
        if name == ql or name.split(': ', 1)[-1] == ql or os.path.basename(path.rstrip('/')) == ql: s += 1000 if r[0] != 'data' else 400
        elif ql in name: s += 300
        elif ql in path: s += 150
        hits = sum(1 for w in words if w in name or w in path or w in what)
        if hits < need and s == 0: continue
        s += 30 * hits + 20 * sum(1 for w in words if w in name) + 5 * sum(1 for w in words if w in path)
        if r[0] not in ('map', 'register') and any(w == name or w == name.split('.')[-1] for w in words): s += 200       # a word IS the thing's name (B1, POSX, LAB4)
        if len(words) > 1 and s < 1000 and r[0] in ('metric', 'code', 'register'): s -= 40   # a phrase asks for a thing, not one value
        s -= KIND_RANK.get(r[0], 9)
        out.append((s, r))
    out.sort(key=lambda x: (-x[0], KIND_RANK.get(x[1][0], 9), x[1][1]))
    res, seen = [], set()
    for _, r in out:
        k = (r[0], r[2] or r[1]) if r[0] not in ('metric', 'code') else (r[0], r[1])
        if k in seen: continue
        seen.add(k); seen.add((r[0], r[2].rstrip('/')))
        res.append(r)
        if len(res) == n: break
    return res


def main(a):
    if '--check' in a:
        print('REFUSED --check is where_v2 (the team map, in the dev tree); where_v3 finds codes in the metric tables only', file=sys.stderr)
        return 2
    kind = a[a.index('--kind') + 1] if '--kind' in a else None
    n = int(a[a.index('--n') + 1]) if '--n' in a else 5
    settings = a[a.index('--settings') + 1] if '--settings' in a else None
    q = ' '.join(x for i, x in enumerate(a) if not x.startswith('--') and (i == 0 or a[i - 1] not in ('--kind', '--n', '--settings')))
    if not q: print(__doc__); return 2
    try:
        S = settings_module(__file__)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    try:
        if settings: S.load(settings)
        tree = detection_tree(__file__, S)
        check_tables(tree)
    except (Refused, S.Refused) as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    R, dropped = records(tree)
    res = search(R, q, kind, n)
    safe = '--safe' in a                                  # for a reviewer under a no-results rule: no register rows (none here)
    if safe: res = [r for r in search(R, q, kind, n * 4) if r[0] != 'register'][:n]
    if not res:
        print('NOT FOUND: "%s" in the metric tables of this Alarm folder (%s). Try other words or --kind; post FOR LAB1 on your board '
              'if it should be there.' % (q, ', '.join('team/' + t for t in TABLES))); return 1
    for r in res:
        p = r[2]; full = p if (not p or p.startswith('/')) else os.path.join(tree, p)
        gone = '   GONE TODAY (not on disk now; the source is older than today)' if p and on_disk(p, tree) is False else ''
        drop = '   DROPPED (register METRICS_V2: not in force)' if r[0] == 'metric' and r[1] in dropped else ''
        what, doc = (r[3][:300], r[4][:300])
        print('[%s] %s  | owner %s | from %s\n   %s\n   %s\n   doc: %s' % (r[0], r[1] + gone + drop, r[5], r[6], full, what, doc))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
