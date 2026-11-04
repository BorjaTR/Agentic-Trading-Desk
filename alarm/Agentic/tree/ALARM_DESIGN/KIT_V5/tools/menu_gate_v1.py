#!/usr/bin/env python3
"""menu_gate_v1.py (SCOUT, 3 Nov 2026; playground PG20261103_menu_gate; TEST, NOT REVIEWED). The SEAL check of the metric menu.

Why: desk trial 4 (DESKA04_20261103) sealed and graded a definition reading E1.S04 (CAUTION) and E1.S09 (UNPROVEN), both pickable NO
in KIT_V5/METRIC_MENU_V2.tsv, and nothing refused them. At SEAL a definition, or a TRUE label, that reads a code whose menu row is
pickable NO is refused, unless the sealed card has a named exception line for that code with its reason, and the VARIANTS row names it:

    MENU EXCEPTION <code>: <reason, at least 12 characters>          (a line of the card, CARD_<IDEA>.md)
    ... MENU EXCEPTION <code> ...                                     (in the reason column of the variant's VARIANTS row)

What a definition reads is the TRUE gate's own reader (true_gate_v1.collect_reads: every code under inputs, conditions, fire, base and
mirror; an unknown op is refused); what a label reads is true_gate_v1.label_codes on the claim's label and mirror, plus its activity code.
The reader is the package's own true_gate_v1.py, its bytes pinned (TG1_SHA) and checked before use; only its four reader definitions
(KNOWN_OPS, Refused, collect_reads, label_codes) are taken from its source, so the heavy imports of the TRUE gate are not loaded. No
environment variable can point the gate at another reader or menu (GPT V12115-TOOL item 1); tests pass one explicitly to gate().
Nothing here changes what any alarm fires on: the detector, its own trap table and every job template are untouched; this only refuses
a seal (queue_job_v16 calls gate() before it fills any job) and prints (decide_v6 prints the exceptions on the decision).
A code with no menu row is printed NOT ON MENU and not refused (the detector's own trap table still decides what it can read).

  python3 -B menu_gate_v1.py check <definition.json> <card.md> [--claim <TRUE claim.json>] [--reason '<VARIANTS reason text>']
        at SEAL, before or after the VARIANTS row: prints one line per code read, each exception, and the reason text the VARIANTS row
        needs; exit 0 OK, 2 REFUSED <CODE>: <why>. Without --reason the VARIANTS record is not checked (the row is not written yet).
Library: gate(def_path, card_path, claim_path=None, reason=None, menu=None, reader=None) -> result dict, raises Refused (every malformed
definition, claim or card shape is a Refused, never another exception); lines(result, name) -> printed lines."""
import ast, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.realpath(__file__))
PKG = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))   # the Alarm folder that holds this file
MENU = os.path.join(PKG, 'Agentic/tree/ALARM_DESIGN/KIT_V5/METRIC_MENU_V2.tsv')
MENU_SHA = '97a967bd24b34757'      # METRIC_MENU_V2.tsv of ALARM_V1_21_8 to V1_21_13 (build_metric_menu_v3.py, LAB4 LEDGER_20261103T135456Z)
TG1 = os.path.join(PKG, '03_Grading/tree/tools/true_gate/true_gate_v1.py')
TG1_SHA = '9cef10e960700d6b'      # true_gate_v1.py of ALARM_V1_20 to V1_21_15 (a JUDGE file of the desk fence)
TG1_NAMES = ('KNOWN_OPS', 'Refused', 'collect_reads', 'label_codes')
EXC = re.compile(r'^[ \t>*-]*MENU EXCEPTION[ \t]+([A-Za-z0-9_.]+)[ \t]*:[ \t]*(.*?)[ \t]*$', re.M)
REC = re.compile(r'MENU EXCEPTION[ \t]+([A-Za-z0-9_.]+)')
MIN_REASON = 12


class Refused(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, '%s: %s' % (code, why)); self.code = code; self.why = why


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


class Reader:
    """the four reader definitions of a pinned true_gate_v1.py, executed from its own source (never copied, never edited)"""
    def __init__(self, path=TG1, want=TG1_SHA):
        if not os.path.isfile(path):
            raise Refused('NO_READER', 'no %s' % path)
        src = open(path, 'rb').read()
        if hashlib.sha256(src).hexdigest()[:16] != want:
            raise Refused('READER_CHANGED', '%s is %s, this gate reads %s' % (path, hashlib.sha256(src).hexdigest()[:16], want))
        tree = ast.parse(src, path); keep = []
        for n in tree.body:
            names = [t.id for t in n.targets if isinstance(t, ast.Name)] if isinstance(n, ast.Assign) else [getattr(n, 'name', None)]
            if any(x in TG1_NAMES for x in names):
                keep.append(n)
        got = sorted({getattr(n, 'name', None) or n.targets[0].id for n in keep})
        if got != sorted(TG1_NAMES):
            raise Refused('READER_CHANGED', '%s holds %s, not %s' % (path, got, sorted(TG1_NAMES)))
        ns = {'__name__': 'true_gate_v1_reader'}
        exec(compile(ast.Module(body=keep, type_ignores=[]), path, 'exec'), ns)
        self.collect_reads, self.label_codes, self.Refused = ns['collect_reads'], ns['label_codes'], ns['Refused']


_TG = []


def tg():
    """the package's pinned reader, loaded once"""
    if not _TG:
        _TG.append(Reader())
    return _TG[0]


def read_menu(path=MENU, want=MENU_SHA):
    """code -> its row (menu_status, pickable, kind, ...); '#' lines are notes; the file must be the pinned one"""
    if not os.path.isfile(path):
        raise Refused('NO_MENU', 'no %s' % path)
    if want and sha16(path) != want:
        raise Refused('MENU_CHANGED', '%s is %s, this gate reads %s: a new menu is a new gate edition' % (path, sha16(path), want))
    rows = [l.rstrip('\n').split('\t') for l in open(path) if l.strip() and not l.startswith('#')]
    if not rows or rows[0][:1] != ['code'] or 'pickable' not in rows[0] or 'menu_status' not in rows[0]:
        raise Refused('BAD_MENU', 'no header with code, menu_status and pickable in %s' % path)
    h = rows[0]; out = {}
    for r in rows[1:]:
        d = dict(zip(h, r))
        if d.get('code') in out:
            raise Refused('BAD_MENU', 'code %s twice in %s' % (d.get('code'), path))
        if d.get('pickable') not in ('YES', 'NO'):
            raise Refused('BAD_MENU', 'code %s pickable %r' % (d.get('code'), d.get('pickable')))
        out[d['code']] = d
    return out


def card_exceptions(text):
    """the card's named exceptions: code -> reason; a repeated code or a short reason is refused"""
    out = {}
    for code, why in EXC.findall(text):
        if code in out:
            raise Refused('BAD_EXCEPTION', 'MENU EXCEPTION %s twice on the card: one line per code' % code)
        if len(why.strip()) < MIN_REASON:
            raise Refused('BAD_EXCEPTION', 'MENU EXCEPTION %s has no reason (%r): write why this code is needed, at least %d characters' % (code, why, MIN_REASON))
        out[code] = why.strip()
    return out


def _codes(x, where, path):
    if not isinstance(x, (set, list, tuple)) or not all(isinstance(c, str) and c for c in x):
        raise Refused('UNREADABLE_%s' % where, '%s: codes are not names: %r' % (path, x))
    return set(x)


def def_codes(def_path, T):
    try:
        d = json.load(open(def_path))
    except (OSError, ValueError) as e:
        raise Refused('UNREADABLE_DEF', '%s: %s' % (def_path, e))
    if not isinstance(d, dict):
        raise Refused('UNREADABLE_DEF', '%s: a definition is a JSON object, not %s' % (def_path, type(d).__name__))
    bad = []

    def walk(x):                                 # the reader skips a code that is not text; here it is refused, not read as nothing
        if isinstance(x, dict):
            bad.extend(v for k, v in x.items() if k == 'code' and not (isinstance(v, str) and v))
            [walk(v) for v in x.values()]
        elif isinstance(x, list):
            [walk(v) for v in x]
    walk(d)
    if bad:
        raise Refused('UNREADABLE_DEF', '%s: a code that is not a name: %r' % (def_path, bad[:3]))
    try:
        return _codes(T.collect_reads(d)['codes'], 'DEF', def_path)
    except Refused:
        raise
    except T.Refused as e:
        raise Refused('UNREADABLE_DEF', '%s: %s' % (def_path, e))
    except Exception as e:                       # a malformed shape the reader cannot walk: refused, never a traceback
        raise Refused('UNREADABLE_DEF', '%s: %s %s' % (def_path, type(e).__name__, e))


def claim_codes(claim_path, T):
    try:
        c = json.load(open(claim_path))
    except (OSError, ValueError) as e:
        raise Refused('UNREADABLE_CLAIM', '%s: %s' % (claim_path, e))
    if not isinstance(c, dict):
        raise Refused('UNREADABLE_CLAIM', '%s: a claim is a JSON object, not %s' % (claim_path, type(c).__name__))
    out = set()
    try:
        for k in ('label', 'mirror'):
            if k in c:
                if not isinstance(c[k], dict):
                    raise Refused('UNREADABLE_CLAIM', '%s: %s is not an object' % (claim_path, k))
                if 'code_by_side' in c[k] and not isinstance(c[k]['code_by_side'], dict):
                    raise Refused('UNREADABLE_CLAIM', '%s: %s.code_by_side is not an object' % (claim_path, k))
                out |= _codes(T.label_codes(c[k]), 'CLAIM', claim_path)
        if 'activity' in c:
            a = c['activity']
            if not isinstance(a, dict) or not isinstance(a.get('code'), str):
                raise Refused('UNREADABLE_CLAIM', '%s: activity needs a code' % claim_path)
            out.add(a['code'])
    except Refused:
        raise
    except Exception as e:
        raise Refused('UNREADABLE_CLAIM', '%s: %s %s' % (claim_path, type(e).__name__, e))
    return out


def gate(def_path, card_path, claim_path=None, reason=None, menu=None, reader=None):
    """the check; raises Refused at the first code that is pickable NO with no named exception (or, with a reason, not recorded).
    menu and reader default to the package's pinned ones; a test passes its own explicitly"""
    menu = read_menu() if menu is None else menu
    T = tg() if reader is None else reader
    if not isinstance(reason, (str, type(None))):
        raise Refused('BAD_REASON', 'the VARIANTS reason is not text: %r' % (reason,))
    try:
        card = open(card_path).read()
    except (OSError, ValueError) as e:
        raise Refused('NO_CARD', '%s: %s' % (card_path, e))
    exc = card_exceptions(card)
    dc = def_codes(def_path, T); lc = claim_codes(claim_path, T) if claim_path else set()
    rec = set(REC.findall(reason or ''))
    res = {'codes': [], 'excepted': {}, 'not_on_menu': [], 'unused_exceptions': [], 'recorded_checked': reason is not None}
    for code in sorted(dc | lc):
        where = '+'.join(w for w, s in (('definition', dc), ('label', lc)) if code in s)
        row = menu.get(code)
        if row is None:
            res['not_on_menu'].append(code); res['codes'].append((code, where, 'NOT ON MENU', '-')); continue
        res['codes'].append((code, where, row['menu_status'], row['pickable']))
        if row['pickable'] == 'YES':
            continue
        if code not in exc:
            raise Refused('MENU_NOT_PICKABLE', '%s (%s, read by the %s) is pickable NO on METRIC_MENU_V2: pick a pickable YES code, or write on the card '
                          'the line "MENU EXCEPTION %s: <why this code is needed>" and name "MENU EXCEPTION %s" in the VARIANTS reason' % (code, row['menu_status'], where, code, code))
        if reason is not None and code not in rec:
            raise Refused('MENU_EXCEPTION_NOT_RECORDED', 'the card names MENU EXCEPTION %s, the VARIANTS reason %r does not: the exception is recorded in the VARIANTS row (a new row is a new seal)' % (code, reason))
        res['excepted'][code] = (row['menu_status'], exc[code])
    res['unused_exceptions'] = sorted(c for c in exc if c not in res['excepted'])
    return res


def lines(res, name):
    out = ['MENU GATE %s: OK, %d codes read: %s' % (name, len(res['codes']), ', '.join('%s %s pickable %s (%s)' % (c, s, p, w) for c, w, s, p in res['codes']) or 'none')]
    for c, (s, why) in sorted(res['excepted'].items()):
        out.append('MENU EXCEPTION %s (%s): %s' % (c, s, why))
    for c in res['not_on_menu']:
        out.append('MENU NOTE %s: NOT ON MENU (no METRIC_MENU_V2 row; the detector\'s trap table decides)' % c)
    for c in res['unused_exceptions']:
        out.append('MENU NOTE %s: a card exception for a code this seal does not need' % c)
    return out


def main(a):
    a = list(a); opt = {'--claim': None, '--reason': None}
    for k in list(opt):
        if k in a:
            i = a.index(k)
            if i + 1 >= len(a):
                raise Refused('USAGE', '%s needs a value' % k)
            opt[k] = a[i + 1]; del a[i:i + 2]
    if len(a) != 3 or a[0] != 'check':
        raise Refused('USAGE', 'menu_gate_v1.py check <definition.json> <card.md> [--claim <TRUE claim.json>] [--reason <VARIANTS reason>]')
    res = gate(a[1], a[2], opt['--claim'], opt['--reason'])
    for l in lines(res, os.path.basename(a[1])):
        print(l)
    if res['excepted'] and opt['--reason'] is None:
        print('VARIANTS reason must name: %s' % '; '.join('MENU EXCEPTION %s' % c for c in sorted(res['excepted'])))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr)
        sys.exit(2)
