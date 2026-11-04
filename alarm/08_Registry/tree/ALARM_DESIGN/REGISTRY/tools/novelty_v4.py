#!/usr/bin/env python3
"""novelty_v4.py (SCOUT, 2 Nov 2026, V1_18_FIXES; why: RESULTS_R5 item 4, RESULTS_R6): novelty_v3.py plus --show by a fire list path, for alarms the registry does
not hold (school runs). --show X: X with a / or ending .tsv is a fire list (a relative one under ALARM_DESIGN of the settings); else an alarm_id, as v3. --show-lean FADE|FOLLOW
gives that list's lean (default: --lean). A shown list is only printed: it never enters the verdict or the nearest lines. A receipts FIRES.tsv is a pointer, refused: give the path
in its last column. v3's text follows.
novelty_v3.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): novelty_v2.py
4f8b9d4888ca5c79 plus two things, nothing else:
  - NEAR also when a registry alarm's waves near minus its baseline is 40 points or more (EXCESS_AT; the owner 1 Nov 2026 09:12 Berlin, the
    tool fixes). The baseline is the chance level of 'waves near' (event coincidence analysis, Donges et al. 2016: a coincidence rate is
    read against its expected rate); the excess is observed minus expected (the jitter-based synchrony index). Each nearest line prints
    'excess <points> pts'. COPY, NEW SIDE and MIRROR are v2's, checked first, in v2's order.
  - --show <alarm_id> prints one more line, 'show:', the same measures for that registry alarm (named as the nearest lines name it),
    wherever it ranks: the named sibling (LESSONS_V5 25). An alarm_id that has no fire list in the registry is refused (rc 2).
The usage: novelty_v3.py --settings S FIRE_LIST.tsv --lean FADE|FOLLOW [--registry REG] [--self SEAT_IDEA] [--show ALARM_ID].
v2's text follows; where it says novelty_v2 read novelty_v3.
novelty_v2.py (SCOUT for ALARM_DESIGN KIT_V6, 30 Oct 2026; TEST, NOT REVIEWED): novelty_v1.py for the Alarm release folder. Is a fire
list a new alarm, a copy of one in the alarm registry, or a known trigger given a side? Reads files only; writes nothing.

  python3 -B <Alarm>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/novelty_v2.py --settings <settings file> <FIRE_LIST.tsv>
      --lean FADE|FOLLOW [--registry <ALARM_REGISTRY.tsv>] [--self <SEAT>_<IDEA>]

What changed from novelty_v1 (CLEAN_RELEASE_V1 section 6; the owner 30 Oct 2026 22:21 Berlin: "Let's make sure everything can run from
the release folder"): only where it finds code and data. --settings (required) names this machine's settings file, read by the settings
reader of the Alarm package that holds this file (its _tools/settings_v1.py: code comes only from that package). The data root is
RESEARCH_ROOT/ALARM_DESIGN of the settings file (v1: --h, by default the folder that held REGISTRY/tools/; --h is gone). A relative
FIRE_LIST or --registry is read under RESEARCH_ROOT/ALARM_DESIGN from any working folder (v1: under the working folder, which its usage
set to ALARM_DESIGN); the printed lines name them as given, as v1 did. The measures, the verdicts and the printed lines are v1's. Also
refused with rc 2: no --settings (or twice), a settings file the reader refuses, an empty RESEARCH_ROOT, this file outside an Alarm
package. The functions under 'the Alarm package and the settings' serve the four registry tools (registry_build_v2, scoreboard_v2 and
index_v2 import them from here).

FIRE_LIST is a tab file with the columns coin and t (whole epoch seconds) and, when the alarm has one, side (the move's sign, 1 or -1),
as a GRADE job writes <V>_FIRES_V1_LIST.tsv (CLEAN keeps it in RUN/receipts/<GRADE job>/). The trading side of a fire is its move side
times -1 for FADE, times 1 for FOLLOW. --registry defaults to REGISTRY/ALARM_REGISTRY_V1.tsv under RESEARCH_ROOT/ALARM_DESIGN
(of the settings file). --self <SEAT>_<IDEA> leaves out that idea's own rows. SYNTHETIC rows are never compared.
Against every registry alarm with a fire list on dev (column fire_list_rel, relative to the ALARM_DESIGN root) it measures:
  same fires   the share of this list's fires (coin and t equal) that are that alarm's fires
  same side    the share of this list's fires that are that alarm's fires with the same trading side (only when both have a side)
  other side   the share that are that alarm's fires with the other trading side (its mirror)
  waves near   the share of this list's waves with a fire of that alarm inside [wave start - 1800 s, wave end + 1800 s]; a wave: a fire
               more than 1800 s after the previous fire of any coin starts a new one (the labcore.waves gap rule)
  baseline     the share of that alarm's span (first to last fire) within 1800 s of one of its fires: what 'waves near' reads for a
               list with no link to it
Rows with the same fires and lean are one group, named by its PASS row (else its first row in the registry). Verdict, in this order:
COPY (same side 50 pct or more of a sided alarm), NEW SIDE (same fires 50 pct or more of a trigger with no side: a desk trigger),
MIRROR (other side 50 pct or more), NEAR (any of these 40 pct or more), NEW (all under 40 pct; the owner 30 Oct 2026 06:20 Berlin: "if it
doesn't overlap 40% or more to me it counts as new"; 20 pct before). Without --lean the side cannot be
told: same fires stand in for same side and the verdict says so. Refused with rc 2: a file without coin and t columns, a file without
fire rows, a t or side that is not a whole number, a registry without its columns, a lean other than FADE or FOLLOW.
"""
import sys, os, csv, bisect, hashlib

GAP = 1800
COPY_AT = 0.50
NEAR_AT = 0.40   # the owner 30 Oct 06:20 Berlin (was 0.20)
EXCESS_AT = 0.40   # v3: waves near minus baseline (the owner 1 Nov 09:12 Berlin)
LEAN = {'FADE': -1, 'FOLLOW': 1}
REG_NEED = ('alarm_id', 'seat', 'idea', 'kind', 'state', 'lean', 'fire_list_rel')


class Refused(Exception):
    pass


def sha16(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def load_fires(path):
    """-> the fires as a sorted list of (t, coin, move side or None)"""
    if not os.path.isfile(path):
        raise Refused('NO FILE %s' % path)
    with open(path, newline='') as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        if not rd.fieldnames or 'coin' not in rd.fieldnames or 't' not in rd.fieldnames:
            raise Refused('%s: NO coin AND t COLUMNS (got %s)' % (path, rd.fieldnames))
        has_side = 'side' in rd.fieldnames
        out = []
        for i, r in enumerate(rd, 2):
            t = (r.get('t') or '').strip()
            if not t.isdigit():
                raise Refused('%s line %d: t %r IS NOT A WHOLE NUMBER' % (path, i, t))
            s = None
            if has_side:
                x = (r.get('side') or '').strip()
                if x not in ('1', '-1', '+1'):
                    raise Refused('%s line %d: side %r IS NOT 1 OR -1' % (path, i, x))
                s = int(x)
            out.append((int(t), (r.get('coin') or '').strip(), s))
    if not out:
        raise Refused('%s: NO FIRE ROWS' % path)
    return sorted(out, key=lambda x: (x[0], x[1], x[2] or 0))


def fingerprint(fires):
    """sha16 of the coin, t and move side set: two lists with the same fires (other columns aside) share it"""
    h = hashlib.sha256()
    for t, c, s in fires:
        h.update(('%s\t%d\t%s\n' % (c, t, s)).encode())
    return h.hexdigest()[:16]


def waves(fires):
    """-> [[first t, last t], ...]: a fire more than GAP s after the previous fire of any coin starts a new wave"""
    w = []
    prev = None
    for f in fires:
        t = f[0]
        if prev is None or t - prev > GAP:
            w.append([t, t])
        else:
            w[-1][1] = t
        prev = t
    return w


def baseline(times):
    """the share of [first, last] within GAP s of one of the times (sorted)"""
    lo, hi = times[0], times[-1]
    if hi <= lo:
        return 0.0
    cov, cur = 0, None
    for t in times:
        a, b = max(lo, t - GAP), min(hi, t + GAP)
        if cur is not None and a <= cur[1]:
            cur[1] = max(cur[1], b)
        else:
            if cur is not None:
                cov += cur[1] - cur[0]
            cur = [a, b]
    cov += cur[1] - cur[0]
    return cov / float(hi - lo)


def excess(m):
    """v3: waves near minus its baseline (the chance level), as a share"""
    return m['near'] - m['base']


def line(label, name, rep, m):
    """v3: one measures line (v2's nearest line plus the excess)"""
    return ('%s: %s (%s, %s, lean %s): same fires %s pct, same side %s pct, other side %s pct; waves near %s pct (its baseline %s pct); '
            'excess %s pts' % (label, name, rep.get('kind'), rep.get('state'), rep.get('lean'), pct(m['same']), pct(m['same_side']),
                               pct(m['other_side']), pct(m['near']), pct(m['base']), pct(excess(m))))


def show_line(res, alarm_id):
    """v3 --show: the line of the group whose representative or name is alarm_id; Refused when none"""
    for name, rep, m in res:
        if rep.get('alarm_id') == alarm_id or name.split(' ')[0] == alarm_id:
            return line('show', name, rep, m)
    raise Refused('SHOW %s: NO SUCH ALARM WITH A FIRE LIST IN THE REGISTRY (after --self); for one the registry does not hold, give its fire list path' % alarm_id)


def is_list_path(x):
    """--show names a fire list, not an alarm_id"""
    return '/' in x or x.endswith('.tsv')


def show_list_line(path, name, new, new_lean, show_lean):
    """v4 --show <fire list>: the same measures for a list the registry does not hold"""
    m = compare(new, new_lean, load_fires(path), show_lean)
    return line('show', name, {'kind': 'LIST', 'state': '-', 'lean': show_lean}, m)


def sided(lean):
    return lean in LEAN


def compare(new, new_lean, other, other_lean):
    """-> dict(same, same_side, other_side, near, base); same_side and other_side are None when a side cannot be told"""
    om = {}
    for t, c, s in other:
        om.setdefault((c, t), set()).add(s)
    n = float(len(new))
    same = ss = os_ = 0
    tell = sided(new_lean) and sided(other_lean)
    for t, c, s in new:
        if (c, t) not in om:
            continue
        same += 1
        if tell and s is not None and None not in om[(c, t)]:
            mine = s * LEAN[new_lean]
            theirs = {x * LEAN[other_lean] for x in om[(c, t)]}
            if mine in theirs:
                ss += 1
            else:
                os_ += 1
    ot = [f[0] for f in other]
    nw = waves(new)
    near = 0
    for a, b in nw:
        i = bisect.bisect_left(ot, a - GAP)
        if i < len(ot) and ot[i] <= b + GAP:
            near += 1
    return {'same': same / n, 'same_side': ss / n if tell else None, 'other_side': os_ / n if tell else None,
            'near': near / float(len(nw)), 'base': baseline(ot)}


def group_rows(rows):
    """rows with 'fires' (registry order) -> [(name, representative row)], one per fire set and lean"""
    by, order = {}, []
    for i, r in enumerate(rows):
        k = (fingerprint(r['fires']), r.get('lean', '-'))
        if k not in by:
            by[k] = []
            order.append(k)
        by[k].append((i, r))
    out = []
    for k in order:
        g = sorted(by[k], key=lambda x: (x[1].get('state') != 'PASS', x[0]))
        rep = g[0][1]
        out.append((rep['alarm_id'] + (' (+%d with the same fires and lean)' % (len(g) - 1) if len(g) > 1 else ''), rep))
    return out


def judge(new, new_lean, rows):
    """-> (verdict, basis text, [(name, row, measures)] nearest first)"""
    res = []
    for name, rep in group_rows(rows):
        res.append((name, rep, compare(new, new_lean, rep['fires'], rep.get('lean', '-'))))
    res.sort(key=lambda x: (-x[2]['same'], -(x[2]['near'] - x[2]['base']), x[0]))
    tell = sided(new_lean)
    best = {'COPY': (0.0, None), 'NEW SIDE': (0.0, None), 'MIRROR': (0.0, None)}
    for name, rep, m in res:
        if not sided(rep.get('lean', '-')):
            if m['same'] > best['NEW SIDE'][0]:
                best['NEW SIDE'] = (m['same'], name)
        else:
            cs = m['same_side'] if tell else m['same']
            if cs > best['COPY'][0]:
                best['COPY'] = (cs, name)
            if tell and m['other_side'] > best['MIRROR'][0]:
                best['MIRROR'] = (m['other_side'], name)
    note = '' if tell else ' (no lean given: same fires stand in for same side)'
    for v, what in (('COPY', 'same fires with the same side'), ('NEW SIDE', 'fires of a trigger with no side'),
                    ('MIRROR', 'same fires with the other side')):
        s, name = best[v]
        if s >= COPY_AT:
            return v, '%s of %s: %.1f pct %s%s' % (v, name, 100 * s, what, note), res
    top = max(best.items(), key=lambda kv: kv[1][0])
    if top[1][0] >= NEAR_AT:
        return 'NEAR', 'NEAR %s: %.1f pct (%s)%s' % (top[1][1], 100 * top[1][0], top[0], note), res
    ex = max(res, key=lambda x: excess(x[2])) if res else None   # ties: the nearest (res is nearest first)
    if ex is not None and excess(ex[2]) >= EXCESS_AT:
        return 'NEAR', 'NEAR %s: waves near %.1f pct over its baseline %.1f pct, excess %.1f pts (40 or more)%s' % (
            ex[0], 100 * ex[2]['near'], 100 * ex[2]['base'], 100 * excess(ex[2]), note), res
    return 'NEW', 'NEW: every overlap under %d pct and every excess under %d pts%s' % (int(100 * NEAR_AT), int(100 * EXCESS_AT), note), res


def load_registry(path, h):
    """-> registry rows (registry order) that have a fire list on dev and are not SYNTHETIC, each with 'fires' loaded"""
    if not os.path.isfile(path):
        raise Refused('NO REGISTRY %s' % path)
    with open(path, newline='') as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        miss = [c for c in REG_NEED if c not in (rd.fieldnames or [])]
        if miss:
            raise Refused('REGISTRY %s LACKS COLUMNS %s' % (path, miss))
        rows = list(rd)
    out = []
    for r in rows:
        rel = r.get('fire_list_rel') or '-'
        if r.get('kind') == 'SYNTHETIC' or rel == '-' or not os.path.isfile(os.path.join(h, rel)):
            continue
        r = dict(r)
        r['fires'] = load_fires(os.path.join(h, rel))
        out.append(r)
    return out


def pct(x):
    return '-' if x is None else '%.1f' % (100 * x)


# ---------------------------------------------------------------- the Alarm package and the settings (the four registry tools share these)
def package(start):
    """-> (the Alarm folder that holds the file start, its settings reader settings_v1). The reader is the package's own
    _tools/settings_v1.py, found from start upwards, so code comes only from the package; refused outside an Alarm package."""
    d = os.path.dirname(os.path.abspath(start))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM PACKAGE %s (the registry tools run from the Alarm release folder)' % start)
        d = os.path.dirname(d)
    if os.path.join(d, '_tools') not in sys.path:
        sys.path.insert(0, os.path.join(d, '_tools'))
    import settings_v1 as S
    try:
        alarm = S.alarm_root(start)
    except S.Refused as e:
        raise Refused(str(e))
    if os.path.realpath(os.path.dirname(os.path.abspath(S.__file__))) != os.path.realpath(os.path.join(alarm, '_tools')):
        raise Refused('SETTINGS READER %s IS NOT THE ONE OF THE ALARM PACKAGE %s' % (S.__file__, alarm))
    return alarm, S


def take_settings(a):
    """removes '--settings <file>' from the argument list a and returns the file; refused when it is missing, twice or has no value"""
    if a.count('--settings') != 1:
        raise Refused('--settings <file> IS NEEDED ONCE: the settings file of this machine (Alarm/settings/SETTINGS_<MACHINE>.env)')
    i = a.index('--settings')
    if i + 1 >= len(a):
        raise Refused('--settings NEEDS A VALUE')
    f = a[i + 1]
    del a[i:i + 2]
    return f


def settings(path, start, keys=('RESEARCH_ROOT',)):
    """-> (the Alarm folder, its settings reader, {key: value} for the keys named): each key must be set in the settings file path"""
    alarm, S = package(start)
    try:
        return alarm, S, {k: S.get(path, k) for k in keys}
    except S.Refused as e:
        raise Refused('SETTINGS %s' % e)


def design_root(research_root):
    """RESEARCH_ROOT/ALARM_DESIGN: the registry, the runs and their fire lists (settings/README.md: RESEARCH_ROOT holds ALARM_DESIGN)"""
    return os.path.join(research_root, 'ALARM_DESIGN')


def under(path, base):
    """a path named on the command line: as given when absolute, else under base (ALARM_DESIGN of the settings), never the working folder"""
    return path if os.path.isabs(path) else os.path.join(base, path)


def outside(path, alarm, S):
    """path (a file or folder to write) when it lies outside the Alarm package; refused inside it (only data lives outside the package,
    and an install is read-only)"""
    if S.inside(path, alarm):
        raise Refused('WRITES INSIDE THE ALARM PACKAGE %s (data lives outside it, where the settings file says)' % path)
    return path


def main(argv):
    a = list(argv)
    sf = take_settings(a)
    opts = {}
    for k in ('--registry', '--self', '--lean', '--show', '--show-lean'):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % k)
            opts[k] = a[i + 1]
            del a[i:i + 2]
    if len(a) != 1:
        raise Refused('USAGE novelty_v3.py --settings SETTINGS FIRE_LIST.tsv --lean FADE|FOLLOW [--registry REG] [--self SEAT_IDEA] [--show ALARM_ID or FIRE_LIST [--show-lean FADE|FOLLOW]]')
    lean = opts.get('--lean', '-')
    if lean != '-' and lean not in LEAN:
        raise Refused('LEAN %r: FADE or FOLLOW' % lean)
    if '--show-lean' in opts and ('--show' not in opts or not is_list_path(opts['--show'])):
        raise Refused('--show-lean IS ONLY FOR --show <fire list path>')
    if opts.get('--show-lean', 'FADE') not in LEAN:
        raise Refused('SHOW LEAN %r: FADE or FOLLOW' % opts['--show-lean'])
    h = design_root(settings(sf, __file__)[2]['RESEARCH_ROOT'])
    reg = opts.get('--registry') or os.path.join(h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv')
    fl = under(a[0], h)
    new = load_fires(fl)
    rows = load_registry(under(reg, h), h)
    if '--self' in opts:
        rows = [r for r in rows if '%s_%s' % (r['seat'], r['idea']) != opts['--self']]
    v, basis, res = judge(new, lean, rows)
    print('NOVELTY %s (sha16 %s), lean %s: %d fires, %d waves; against %d registry alarms (%s sha16 %s)'
          % (a[0], sha16(fl), lean, len(new), len(waves(new)), len(rows), reg, sha16(under(reg, h))))
    sl = None
    if '--show' in opts and is_list_path(opts['--show']):
        show_lean = opts.get('--show-lean', lean)
        fl2 = under(opts['--show'], h)
        sl = show_list_line(fl2, opts['--show'], new, lean, show_lean)
    elif '--show' in opts:
        sl = show_line(res, opts['--show'])
    for i, (name, rep, m) in enumerate(res[:3], 1):
        print(line('nearest %d' % i, name, rep, m))
    if sl:
        print(sl)
    print('VERDICT %s' % basis)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
