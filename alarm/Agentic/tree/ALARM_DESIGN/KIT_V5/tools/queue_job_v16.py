#!/usr/bin/env python3
"""queue_job_v16.py (SCOUT, 3 Nov 2026; playground PG20261103_menu_gate; TEST, NOT REVIEWED): queue_job_v15.py f8833ce0e60ca874, loaded
byte for byte from beside this file and run as it is, plus the menu gate at SEAL, nothing else.
  queue_job_v16.py --settings S <RUN> <KIND> <IDEA> <ITEMS> [the options of queue_job_v15.py]
After every check of queue_job_v15 passed for a sealed variant (every kind but COUNT: GRADE, TRUE, ENTRY, MONTH, FIRSTLOOK) and before
any job is filled or a number claimed, menu_gate_v1.gate reads the variant's sealed definition (VARIANTS def_rel), its sealed card
(prereg_rel) and its VARIANTS reason, and for TRUE the claim given (for GRADE every ideas/<IDEA>/TRUE_<V>_*.json already written):
a code read whose KIT_V5/METRIC_MENU_V2.tsv row is pickable NO is refused (REFUSED: MENU GATE <V>: MENU_NOT_PICKABLE ...) unless the card
has the line "MENU EXCEPTION <code>: <reason>" and the VARIANTS reason names "MENU EXCEPTION <code>". The gate prints its lines
(MENU GATE, MENU EXCEPTION, MENU NOTE) before queue_job_v15's own output. COUNT is not gated (no seal yet; menu_gate_v1.py check is the
SEAL-time command). Why: desk trial 4 sealed E1.S04 (CAUTION) and E1.S09 (UNPROVEN) and nothing refused them.
FDAOI-first: queue_job_v15, its templates and every job it writes are unchanged; for a variant the gate admits, the job text is
queue_job_v15's byte for byte (test_menu_gate_v1 KEEP); the gate only adds a refusal before any job exists."""
import hashlib, importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
V15, V15_SHA = os.path.join(HERE, 'queue_job_v15.py'), 'f8833ce0e60ca874'
MG_PATH = os.path.join(HERE, 'menu_gate_v1.py')
GATED = ('GRADE', 'TRUE', 'ENTRY', 'MONTH', 'FIRSTLOOK')


def _sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def _load(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


if not os.path.isfile(V15) or _sha16(V15) != V15_SHA:
    print('REFUSED: queue_job_v15.py MISSING OR CHANGED beside %s (want %s): this queue runs that one exact edition' % (__file__, V15_SHA), file=sys.stderr)
    raise SystemExit(2)
Q = _load(V15, 'queue_job_v15')
MG = _load(MG_PATH, 'menu_gate_v1')
Q.NEXT_HINTS = Q.NEXT_HINTS + (
    ('MENU GATE', 'a code your definition or TRUE label reads is pickable NO on Agentic/tree/ALARM_DESIGN/KIT_V5/METRIC_MENU_V2.tsv: pick a pickable YES code '
                  '(a new definition is a new variant), or write on the card "MENU EXCEPTION <code>: <why>" and seal a VARIANTS row whose reason names '
                  '"MENU EXCEPTION <code>"; check first with menu_gate_v1.py check (cards/menu_gate_v1.md)'),)
_plan15 = Q.plan


def claims_of(run, kind, idea, v, items):
    if kind == 'TRUE':
        return [os.path.join(run, items.split('=', 1)[1])]
    if kind == 'GRADE':
        d = os.path.join(run, 'ideas', idea)
        return sorted(os.path.join(d, n) for n in (os.listdir(d) if os.path.isdir(d) else ()) if n.startswith('TRUE_%s_' % v) and n.endswith('.json'))
    return []


def plan(run, kind, idea, items, from_job, forward_only=False):
    """queue_job_v15.plan unchanged, then the menu gate on each sealed variant it admitted"""
    res = _plan15(run, kind, idea, items, from_job, forward_only)
    if kind not in GATED:
        return res
    vs = res[1]
    var = Q.read_reg(run, 'VARIANTS')
    for v in vs:
        r = Q.latest(var, idea=idea, V=v)
        if r is None:
            raise Q.Refused('MENU GATE %s: NOT IN VARIANTS' % v)
        dp, cp = os.path.join(run, r['def_rel']), os.path.join(run, r['prereg_rel'])
        for c in (claims_of(run, kind, idea, v, items) or [None]):
            try:
                g = MG.gate(dp, cp, c, r.get('reason', ''))
            except MG.Refused as e:
                raise Q.Refused('MENU GATE %s: %s%s' % (v, e, '' if c is None else ' (claim %s)' % os.path.relpath(c, run)))
            for l in MG.lines(g, '%s %s%s' % (idea, v, '' if c is None else ' + ' + os.path.basename(c))):
                print(l)
    return res


Q.plan = plan

if __name__ == '__main__':
    try:
        sys.exit(Q.main(sys.argv[1:]))
    except Q.Refused as e:
        m = str(e).replace('USAGE queue_job_v15.py', 'USAGE queue_job_v16.py')
        print('REFUSED: %s' % m, file=sys.stderr)
        if Q.next_hint(m):
            print('NEXT: %s' % Q.next_hint(m), file=sys.stderr)
        sys.exit(2)
