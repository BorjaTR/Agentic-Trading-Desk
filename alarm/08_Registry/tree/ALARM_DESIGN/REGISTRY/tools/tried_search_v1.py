#!/usr/bin/env python3
"""tried_search_v1.py (SCOUT, 3 Nov 2026; playground PG20261103_tried_search, then ALARM_V1_21_10): step 1 of the alarm loop, was it tried?
Why: desk trial 2 (DESKA02, CLOSEOUT) and trial 1 (DESKA01, WINDFALL) both ran COUNT, GRADE and TRUE on an idea that was already in the
registry (AD2_OIFLUSH_OF1, AD7_PAYERWIN_PW1), and SCOUTR12's DELEVHOUR was only found by novelty after the GRADE. Two trial agents and
PROCESS asked for a copy search before COUNT. Reads files only; writes nothing; runs no job; reads no market data.

  python3 -B <INSTALL>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/tried_search_v1.py --settings <S> [--def <DEF.json>]
      [--self <RUN>_<IDEA>] [--n <hits per source, default 8>] [<word> ...]

What it reads (RESEARCH_ROOT of the settings file): ALARM_DESIGN/REGISTRY/ALARM_REGISTRY_V1.tsv (every decided alarm, its def_rel),
ALARM_DESIGN/runs/IDEAS_CLAIMED/<RUN>_<IDEA>.txt (every claim, also after the registry's build stamp) with the definitions of that idea
in ALARM_DESIGN/runs/<RUN>/ideas/<IDEA>/defs/*.json, and PROCESS/2_ALARMS/TRIED_ALARMS_V1.tsv (every logged try).

1. Words: each row of the three sources holding at least one word, most words first (loop_find --any's rule), the top --n per source,
   each with WHY: which word was found in which field. A word matches a whole token of the text (a token is letters, digits and dots,
   so E2.S04 is one token); a word of 4 or more letters also matches a token it starts (funding finds fundings). With --def, the
   definition's metric codes are words too, and count twice.
2. Definition (--def): every registry and claimed definition is compared with yours, as structure, never by input names:
   each condition becomes one line, lhs cmp rhs, with every input name replaced by what it computes (op and settings, all the way down
   to the raw codes and the price); a < or <= line is turned round to > or >=; 'a - b > 0' reads 'a > b'; add and mul sort their two
   sides; samesign and oppsign sort theirs. The fire side is its input's line times its sign.
     COPY  the same set of condition lines (an event list a line reads counts by its file and days), the same fire side and timing (grid_s,
           onset, refractory_s, with the detector's defaults: onset true, refractory 0): the same rule, whatever its names, order or id;
           numbers compared at full precision
     NEAR  the same lines and side with other timing; the same lines with the other fire side; or the same metric codes and the same lines with other numbers (a threshold,
           a window, a percentile); or one rule is the other plus condition lines (same fire side; the smaller one reads a metric
           code, not only the price); or the same metric codes and at
           least half of the lines equal. NEAR lines print closest kind first, in that order
   At most 6 NEAR lines are printed (then 'DEF NEAR <n> more not printed'). Other definitions sharing a code are printed as SHARES
   (the 3 with most shared lines), never a verdict.
   VERDICT DEF COPY | NEAR | NEW, before any COUNT. A COPY is a reason not to COUNT it as new: change the idea, or run it as a named copy.
   VERDICT DEF INCOMPLETE when no COPY or NEAR was found but some definition could not be read (or none was read): the paths are
   printed and the idea is not proven new. A COPY or NEAR found is kept when others are unreadable (DEF UNREADABLE line).
   The comparison base block (matched moments, its seed) and event lists no condition or fire side reads (the truth label's, the base's)
   choose no fire: a difference there is printed, never a verdict.
   Without --def: VERDICT WORDS ONLY.
--self <RUN>_<IDEA> leaves out that idea's own claim, definitions and registry rows; the --def file itself is always left out.
Exit 0 (any verdict), 2 refused: no --settings, no word and no --def, a --def that is not a JSON definition with inputs and conditions,
a registry without its columns, an --n that is not a whole number 1 to 50. A registry or claimed definition that does not parse is
skipped and counted on the first line (defs unreadable N).
Code reuse: the settings, package and path helpers are novelty_v4's (beside this file; imported, not copied); the word rule is
loop_find's --any (research-learning-loop). TEST, NOT REVIEWED.
"""
import csv, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOV = os.environ.get('TRIED_SEARCH_NOVELTY') or os.path.join(HERE, 'novelty_v4.py')   # the env: playground only (the tool outside a package)
sys.path.insert(0, os.path.dirname(os.path.abspath(NOV)))
import novelty_v4 as N  # noqa: E402

REG_NEED = ('alarm_id', 'kind', 'run', 'idea', 'V', 'state', 'one_line', 'def_rel')
REG_FIELDS = ('alarm_id', 'idea', 'one_line', 'do_not', 'findings', 'family')
TRIED_FIELDS = ('id', 'run', 'what_tried', 'expected', 'actual', 'why', 'closest_existing', 'gaps', 'improve', 'next_action')
STOP = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'and', 'or', 'is', 'it', 'by', 'for', 'with', 'its', 'own', 'min', 'pct', 'then'}
TOK = re.compile(r'[a-z0-9]+(?:\.[a-z0-9]+)*')
SYM = {'add', 'mul', 'samesign', 'oppsign'}


class Refused(Exception):
    pass


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


# ---------------------------------------------------------------- the definition as structure
def num(x):
    return repr(float(x))   # full precision (GPT V12110-TOOL item 1): 0.0002 and 0.00020000001 are different thresholds


def canon(d):
    """-> dict(lines: set of condition lines, skel: the lines with numbers masked, side, codes, refractory) of a definition dict"""
    inp = d.get('inputs')
    conds = d.get('conditions')
    if not isinstance(inp, dict) or not isinstance(conds, list) or not conds:
        raise Refused('BAD_DEF: no inputs or no conditions')
    codes, refs = set(), set()

    def expr(x, depth=0):
        if depth > 60:
            raise Refused('BAD_DEF: inputs refer to each other in a loop')
        if isinstance(x, bool):
            return ('$', str(x))
        if isinstance(x, (int, float)):
            return ('#', num(x))
        if isinstance(x, str) and x in inp:
            v = inp[x]
            if not isinstance(v, dict):
                return ('$', str(v))
            op = str(v.get('op'))
            if op == 'price':
                codes.add('price')
            kv = []
            for k in sorted(v):
                if k == 'op':
                    continue
                if k == 'code' and isinstance(v[k], str):
                    codes.add(v[k])
                if k == 'events' and isinstance(v[k], str):   # an event list the rule reads: its file and days, not its name (GPT V12112-TOOL)
                    ev = d.get('events') if isinstance(d.get('events'), dict) else {}
                    cv = d.get('events_cover') if isinstance(d.get('events_cover'), dict) else {}
                    refs.add(v[k])
                    kv.append((k, ('$', json.dumps({'list': ev.get(v[k]), 'cover': cv.get(v[k])}, sort_keys=True))))
                    continue
                kv.append((k, expr(v[k], depth + 1)))
            if op in SYM and {k for k, _ in kv} >= {'a', 'b'}:
                a, b = dict(kv)['a'], dict(kv)['b']
                a, b = sorted((a, b), key=text)
                kv = [(k, a if k == 'a' else b if k == 'b' else e) for k, e in kv]
            return (op, tuple(kv))
        if isinstance(x, list):
            return ('[]', tuple(expr(y, depth + 1) for y in x))
        if isinstance(x, dict):
            return ('{}', tuple((k, expr(x[k], depth + 1)) for k in sorted(x)))
        return ('$', str(x))

    lines, skel = set(), set()
    for c in conds:
        if not isinstance(c, dict) or 'lhs' not in c or 'rhs' not in c or 'cmp' not in c:
            raise Refused('BAD_DEF: a condition without lhs, cmp and rhs')
        L, R, op = expr(c['lhs']), expr(c['rhs']), str(c['cmp'])
        if op in ('<', '<='):
            L, R, op = R, L, {'<': '>', '<=': '>='}[op]
        if op in ('samesign', 'oppsign', '==', '!='):
            L, R = sorted((L, R), key=text)
        zero = ('#', num(0))
        if R == zero and L[0] == 'sub':
            L, R = dict(L[1])['a'], dict(L[1])['b']
        elif L == zero and R[0] == 'sub':
            L, R = dict(R[1])['b'], dict(R[1])['a']
        lines.add('%s %s %s' % (text(L), op, text(R)))
        skel.add('%s %s %s' % (text(L, True), op, text(R, True)))
    f = d.get('fire') if isinstance(d.get('fire'), dict) else {}
    s = f.get('side') if isinstance(f.get('side'), dict) else {}
    side = '%s x %s' % (text(expr(s.get('input'))), s.get('sign', 1)) if s.get('input') is not None else 'none'
    # event lists: only those an input of the conditions or the fire side reads count (inside expr above); a list read only by the truth
    # label or the comparison base chooses no fire (alarm_design_v3 L379, L600-603, L635): its difference is printed apart
    # the timing the detector uses to pick the fires (alarm_design_v3 find_fires: grid_s, onset default true, refractory_s default 0)
    timing = 'grid_s %s, onset %s, refractory_s %s' % (d.get('grid_s'), bool(f.get('onset', True)), f.get('refractory_s', 0))
    # the comparison base (matched moments, its seed) never chooses a fire (GPT V12111-TOOL): kept apart, reported, never a verdict
    # only what chooses no fire: the comparison base and the event lists no condition or fire side reads (GPT V12113-TOOL item 1)
    ev = d.get('events') if isinstance(d.get('events'), dict) else {}
    cv = d.get('events_cover') if isinstance(d.get('events_cover'), dict) else {}
    cmpbase = json.dumps({'base': d.get('base') or {}, 'unused_events': {n: [ev.get(n), cv.get(n)] for n in sorted(set(ev) - refs)}}, sort_keys=True)
    return {'lines': lines, 'skel': skel, 'side': side, 'codes': codes, 'timing': timing, 'base': cmpbase}


def text(e, mask=False):
    k, v = e
    if k == '#':
        return '#' if mask else v
    if k == '$':
        return repr(v)
    if k == '[]':
        return '[%s]' % ','.join(text(x, mask) for x in v)
    if k == '{}':
        return '{%s}' % ','.join('%s=%s' % (a, text(b, mask)) for a, b in v)
    return '%s(%s)' % (k, ','.join('%s=%s' % (a, text(b, mask)) for a, b in v))


def compare(mine, other):
    """-> (verdict COPY|NEAR|SHARES|None, why text, strength: 0 the closest kind of NEAR .. 3, equal line count)"""
    a, b = mine['lines'], other['lines']
    eq = len(a & b)
    same_codes = mine['codes'] == other['codes']
    side_eq = mine['side'] == other['side']
    base = '%d of %d condition lines equal (theirs %d); codes %s %s; fire side %s' % (
        eq, len(a), len(b), 'equal' if same_codes else 'shared', ','.join(sorted(mine['codes'] & other['codes'])) or 'none',
        'equal' if side_eq else 'other')
    if mine['base'] != other['base']:
        base += '; comparison base or unused event lists differ (fires unchanged): %s vs %s' % (mine['base'][:80], other['base'][:80])
    time_eq = mine['timing'] == other['timing']
    if not time_eq:
        base += '; timing %s vs %s' % (mine['timing'], other['timing'])
    if a == b and side_eq and time_eq:
        return 'COPY', base, 0, eq
    if a == b and side_eq:
        return 'NEAR', base + ' (the same rule with other timing: grid, onset or refractory)', 0, eq
    if a == b:
        return 'NEAR', base + ' (the same rule with the other fire side)', 0, eq
    if same_codes and side_eq and mine['skel'] == other['skel']:
        return 'NEAR', base + ' (the same lines with other numbers)', 1, eq
    small = mine if len(a) < len(b) else other
    if side_eq and (a < b or b < a) and small['codes'] - {'price'}:
        return 'NEAR', base + ' (one rule is the other plus %d condition lines)' % abs(len(a) - len(b)), 2, eq
    if same_codes and (mine['skel'] == other['skel'] or eq * 2 >= max(len(a), len(b))):
        why = ' (the same lines with other numbers)' if mine['skel'] == other['skel'] else ' (half or more of the lines equal)'
        return 'NEAR', base + why, 3, eq
    if mine['codes'] & other['codes'] - {'price'}:
        return 'SHARES', base, 4, eq
    return None, base, 4, eq


def load_def(p):
    try:
        with open(p) as f:
            return canon(json.load(f))
    except (OSError, ValueError, Refused, TypeError, AttributeError, KeyError):
        return None


# ---------------------------------------------------------------- the sources
def tsv_rows(p):
    with open(p, newline='', errors='replace') as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        return list(rd.fieldnames or []), [r for r in rd]


def registry(h, self_ri):
    p = os.path.join(h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv')
    if not os.path.isfile(p):
        raise Refused('NO REGISTRY %s' % p)
    cols, rows = tsv_rows(p)
    miss = [c for c in REG_NEED if c not in cols]
    if miss:
        raise Refused('REGISTRY %s LACKS COLUMNS %s' % (p, miss))
    out = []
    for r in rows:
        if self_ri and (r.get('run'), r.get('idea')) == self_ri:
            continue
        rel = r.get('def_rel') or '-'
        out.append({'src': 'registry', 'name': r['alarm_id'], 'tag': '%s %s, run %s' % (r.get('kind'), r.get('state'), r.get('run')),
                    'fields': {k: r.get(k) or '' for k in REG_FIELDS}, 'defs': [] if rel in ('-', '') else [os.path.join(h, rel)]})
    return p, out


def split_claim(h, stem):
    """<RUN>_<IDEA> -> (RUN, IDEA): the longest RUN prefix that is a run folder, else SEAT_DATE"""
    parts = stem.split('_')
    for k in range(len(parts) - 1, 1, -1):
        if os.path.isdir(os.path.join(h, 'runs', '_'.join(parts[:k]))):
            return '_'.join(parts[:k]), '_'.join(parts[k:])
    return '_'.join(parts[:2]), '_'.join(parts[2:])


def claims(h, self_ri):
    out = []
    d = os.path.join(h, 'runs', 'IDEAS_CLAIMED')
    for p in sorted(glob.glob(os.path.join(d, '*.txt'))):
        if '.pre_' in p:
            continue
        stem = os.path.basename(p)[:-4]
        run, idea = split_claim(h, stem)
        if self_ri and (run, idea) == self_ri:
            continue
        defs = sorted(x for x in glob.glob(os.path.join(h, 'runs', run, 'ideas', idea, 'defs', '*.json')) if '.pre_' not in x)
        out.append({'src': 'claim', 'name': stem, 'tag': 'claimed, run %s' % run,
                    'fields': {'name': stem.replace('_', ' '), 'text': open(p, errors='replace').read()}, 'defs': defs})
    return d, out


def tried(research_root, self_ri):
    p = os.path.join(research_root, 'PROCESS', '2_ALARMS', 'TRIED_ALARMS_V1.tsv')
    if not os.path.isfile(p):
        return p, []
    out = []
    for r in tsv_rows(p)[1]:
        if self_ri and r.get('run') == self_ri[0] and self_ri[1].lower() in (r.get('id') or '').lower():
            continue
        out.append({'src': 'tried', 'name': r.get('id') or '?', 'tag': '%s, run %s' % (r.get('verdict'), r.get('run')),
                    'fields': {k: r.get(k) or '' for k in TRIED_FIELDS}, 'defs': []})
    return p, out


# ---------------------------------------------------------------- the words
def tokens(s):
    return set(TOK.findall((s or '').lower()))


def found(term, toks):
    return term in toks or (len(term) >= 4 and any(t.startswith(term) for t in toks))


def score(row, terms, codes):
    why, sc = [], 0
    toks = {k: tokens(v) for k, v in row['fields'].items()}
    if row.get('codes'):
        toks['codes'] = {c.lower() for c in row['codes']}
    for t in terms:
        where = [k for k, v in toks.items() if found(t, v)]
        if where:
            w = 2 if t in codes else 1
            sc += w
            why.append('%s in %s' % (t, ','.join(where)))
    return sc, why


def main(argv):
    a = list(argv)
    sf = N.take_settings(a)
    opts = {}
    for k in ('--def', '--self', '--n'):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % k)
            opts[k] = a[i + 1]
            del a[i:i + 2]
    try:
        n = int(opts.get('--n', '8'))
    except ValueError:
        n = 0
    if not 1 <= n <= 50:
        raise Refused('--n %r: a whole number 1 to 50' % opts.get('--n'))
    words = [w.lower() for w in a]
    if any(w.startswith('--') for w in words):
        raise Refused('UNKNOWN OPTION %s' % [w for w in words if w.startswith('--')])
    if not words and '--def' not in opts:
        raise Refused('GIVE WORDS OF THE IDEA, OR --def <DEF.json>, OR BOTH')
    self_ri = None
    if '--self' in opts:
        s = opts['--self'].split('_')
        if len(s) < 3:
            raise Refused('--self %r: <RUN>_<IDEA>, e.g. DESKA02_20261103_CLOSEOUT' % opts['--self'])
    rr = N.settings(sf, N.__file__)[2]['RESEARCH_ROOT']
    h = N.design_root(rr)
    if '--self' in opts:
        self_ri = split_claim(h, opts['--self'])
    mine, dp = None, None
    if '--def' in opts:
        dp = N.under(opts['--def'], h)
        if not os.path.isfile(dp):
            raise Refused('NO DEF FILE %s' % dp)
        try:
            with open(dp) as f:
                mine = canon(json.load(f))
        except ValueError as e:
            raise Refused('BAD_DEF: %s is not JSON (%s)' % (dp, e))
    rp, reg = registry(h, self_ri)
    cp, cl = claims(h, self_ri)
    tp, tr = tried(rr, self_ri)
    unread, cache, unread_paths = 0, {}, []
    for row in reg + cl:
        row['codes'] = set()
        row['canon'] = []
        for p in row['defs']:
            if dp and os.path.realpath(p) == os.path.realpath(dp):
                continue
            if p not in cache:
                cache[p] = load_def(p) if os.path.isfile(p) else None
                unread += cache[p] is None
                if cache[p] is None:
                    unread_paths.append(os.path.relpath(p, h))
            if cache[p] is not None:
                row['canon'].append((p, cache[p]))
                row['codes'] |= cache[p]['codes'] - {'price'}
    codes = {c.lower() for c in (mine['codes'] - {'price'})} if mine else set()
    terms = [w for w in dict.fromkeys(words + sorted(codes)) if w not in STOP and len(w) >= 2]
    print('TRIED_SEARCH words %s%s: registry %s (sha16 %s, %d rows), claims %s (%d), tried %s (%s, %d rows); defs read %d, defs unreadable %d'
          % (','.join(terms) or 'none', (' def %s (sha16 %s, codes %s)' % (opts['--def'], sha16(dp), ','.join(sorted(mine['codes'])))) if mine else '',
             rp, sha16(rp), len(reg), cp, len(cl), tp, sha16(tp) if os.path.isfile(tp) else 'missing', len(tr),
             sum(v is not None for v in cache.values()), unread))
    for label, rows in (('REGISTRY', reg), ('CLAIMS', cl), ('TRIED', tr)):
        hits = []
        for r in rows:
            sc, why = score(r, terms, codes)
            if sc:
                hits.append((-sc, r['name'], r, why))
        hits.sort(key=lambda x: (x[0], x[1]))
        print('%s %d rows with a word%s' % (label, len(hits), (', top %d' % n) if len(hits) > n else ''))
        for i, (sc, name, r, why) in enumerate(hits[:n], 1):
            print('  %s%d %s (%s) words %d: %s' % (label[0], i, name, r['tag'], -sc, '; '.join(why)))
    if not mine:
        print('VERDICT WORDS ONLY: read the hits; before COUNT give --def <your DEF.json> for the definition check')
        return 0
    found_ = []
    for r in reg + cl:
        for p, c in r['canon']:
            v, why, k, eq = compare(mine, c)
            if v:
                found_.append((v, r, p, why, eq, k))
    order = {'COPY': 0, 'NEAR': 1, 'SHARES': 2}
    found_.sort(key=lambda x: (order[x[0]], x[5], -x[4], x[1]['src'] != 'registry', x[1]['name'], x[2]))
    shown = {'COPY': 0, 'NEAR': 0, 'SHARES': 0}
    for v, r, p, why, eq, k in found_:
        shown[v] += 1
        if shown[v] > {'COPY': 50, 'NEAR': 6, 'SHARES': 3}[v]:
            continue
        print('DEF %s %s (%s %s; def %s sha16 %s): %s' % (v, r['name'], r['src'], r['tag'], os.path.relpath(p, h), sha16(p), why))
    copies = [x for x in found_ if x[0] == 'COPY']
    nears = [x for x in found_ if x[0] == 'NEAR']
    names = lambda xs: ', '.join(dict.fromkeys('%s (%s)' % (x[1]['name'], x[1]['src']) for x in xs))
    if shown['NEAR'] > 6:
        print('DEF NEAR %d more not printed' % (shown['NEAR'] - 6))
    if unread_paths and (copies or nears):
        print('DEF UNREADABLE %d definitions not compared: %s' % (len(unread_paths), ', '.join(unread_paths[:10])))
    if copies:
        print('VERDICT DEF COPY of %s: the same rule; do not COUNT it as a new idea: change it, or run it as a named copy' % names(copies))
    elif nears:
        print('VERDICT DEF NEAR %s: say on the card what differs and why it is a new try, before COUNT' % names(nears))
    elif unread_paths or not any(v is not None for v in cache.values()):
        print('VERDICT DEF INCOMPLETE: %d definitions could not be read and none of the %d read is a COPY or NEAR: not proven new; read these '
              'by hand or fix them: %s' % (len(unread_paths), sum(v is not None for v in cache.values()), ', '.join(unread_paths[:10]) or 'no definition to compare'))
    else:
        print('VERDICT DEF NEW: no registry or claimed definition has the same condition lines; novelty on the fire list (step 9) still decides')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except (Refused, N.Refused) as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
