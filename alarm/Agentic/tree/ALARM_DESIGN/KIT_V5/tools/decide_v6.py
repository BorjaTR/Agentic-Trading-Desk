#!/usr/bin/env python3
"""decide_v6.py (SCOUT, 3 Nov 2026; playground PG20261103_menu_gate; TEST, NOT REVIEWED): decide_v5.py b8f41087b550dc5f, loaded byte for
byte from beside this file and run as it is, plus the menu exceptions printed on the decision, nothing else.
  decide_v6.py --settings S RUN IDEA V --grade <GRADE JOB> [--entry <ENTRY JOB> | --entry-too-big] [--write]
decide_v5 prints its DECISION and SOURCES lines (and with --write appends its DECISIONS row, the same bytes); then this prints the menu
gate of the variant's sealed definition, card and VARIANTS reason (and of each ideas/<IDEA>/TRUE_<V>_*.json): 'MENU GATE ... OK',
one 'MENU EXCEPTION <code> (<status>): <reason>' line per named exception, or 'MENU GATE <V>: REFUSED ...' when the sealed variant
would not pass the gate today (a variant sealed before the gate, or a malformed claim: its Refused code). Print only: the state, the row
and the exit code are decide_v5's. The menu lines are made BEFORE decide_v5 runs (it may write its DECISIONS row), and any fault in them
is a printed diagnostic, never an exit (GPT V12115-TOOL item 2).
FDAOI-first: no rule, number or row changes (test_menu_gate_v1 KEEP: decide_v5's output is a byte prefix of this one's)."""
import hashlib, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V5, V5_SHA = os.path.join(HERE, 'decide_v5.py'), 'b8f41087b550dc5f'


def _sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _load(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def menu_lines(run, idea, v):
    MG = _load(os.path.join(HERE, 'menu_gate_v1.py'), 'menu_gate_v1_d6')
    rows = [r for r in D.tsv(os.path.join(run, 'registers', 'VARIANTS.tsv')) if r.get('idea') == idea and r.get('V') == v]
    if not rows:
        return ['MENU GATE %s: NO VARIANTS ROW' % v]
    r = rows[-1]; d = os.path.join(run, 'ideas', idea)
    claims = sorted(os.path.join(d, n) for n in (os.listdir(d) if os.path.isdir(d) else ()) if n.startswith('TRUE_%s_' % v) and n.endswith('.json'))
    out = []
    for c in (claims or [None]):
        name = '%s %s%s' % (idea, v, '' if c is None else ' + ' + os.path.basename(c))
        try:
            out += MG.lines(MG.gate(os.path.join(run, r['def_rel']), os.path.join(run, r['prereg_rel']), c, r.get('reason', '')), name)
        except MG.Refused as e:
            out.append('MENU GATE %s: REFUSED %s (printed only; the decision above stands)' % (name, e))
    return out


def safe_menu_lines(argv):
    """the menu lines for decide_v5's arguments, made before decide_v5 runs; never raises"""
    try:
        a = [x for x in argv if x not in ('--write', '--entry-too-big')]
        opt = {}
        for k in ('--grade', '--entry', '--settings'):
            if k in a:
                i = a.index(k); opt[k] = a[i + 1] if i + 1 < len(a) else None; del a[i:i + 2]
        if len(a) != 3 or not opt.get('--settings') or not D.RUNTAG.match(a[0]):
            return []                                        # decide_v5 refuses these arguments itself
        D.configure(opt['--settings'])
        return menu_lines(os.path.join(D.CFG['H'], 'runs', a[0]), a[1], a[2])
    except Exception as e:                                   # a diagnostic, never an exit of the decision
        return ['MENU GATE: NOT READ (%s %s; printed only; the decision stands)' % (type(e).__name__, str(e)[:200])]


if not os.path.isfile(V5) or _sha16(V5) != V5_SHA:
    print('REFUSED: decide_v5.py MISSING OR CHANGED beside %s (want %s)' % (__file__, V5_SHA), file=sys.stderr)
    raise SystemExit(2)
D = _load(V5, 'decide_v5')

if __name__ == '__main__':
    lines = safe_menu_lines(sys.argv[1:])
    try:
        rc = D.main(sys.argv[1:])
    except D.Refused as e:
        print('REFUSED: %s' % str(e).replace('USAGE decide_v5.py', 'USAGE decide_v6.py'), file=sys.stderr)
        sys.exit(2)
    for l in lines:
        print(l)
    sys.exit(rc)
