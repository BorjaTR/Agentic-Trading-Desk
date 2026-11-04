#!/usr/bin/env python3
"""metric_brief_v2.py: print how to read each metric, from its card, with the tables of this Alarm folder only.

Owner: LEAD (the reading-metrics skill). New edition by SCOUT for the clean release (K7, 30 Oct 2026; the owner 23:07 Berlin: "All alarm
tools should work from the release folder only"). Old file: team/RESEARCH/LEAD/skills/reading-metrics/scripts/metric_brief.py
e566e6279ae34d60. That file stays current and untouched: labcore.briefs (labcore V2_7, pinned) calls it for detect's metric gate.
This edition calls, imports and reads no old edition.

ONE source per fact (LAB1 23 Oct): status, never_read_as, read_it_as and empty_means come from LAB4's METRIC_TRAPS_V3.tsv (every
METRICS_V1 entry, 23 Oct 14:17Z); meaning, unit, scope, step, window, days and card path from METRICS_V1 (and the CTX / EPI catalogues
for alarm values).

Usage (metric_brief.py's three ways of asking, unchanged):
  python3 -B metric_brief_v2.py C2.S04 A1.S01 ...      exact codes
  python3 -B metric_brief_v2.py --grep "basket"         search code, name, meaning
  python3 -B metric_brief_v2.py --family B1             every code of a family
  ... [--settings <settings file>]                      optional: checked by _tools/settings_v1.py (this tool reads no data)
What changed from metric_brief.py (each brief is byte for byte the same):
  - the four tables are read only inside the Alarm folder that holds this file (found by _tools/settings_v1.alarm_root), in its
    detection tree 01_Detection/tree/ (the dev tree's layout, as the kit's jobs read it): team/LAB3/METRICS_V1.tsv,
    team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv, team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv and
    team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv. No dev default; the variables METRICS_V1, METRIC_TRAPS and CATALOGS are not read;
  - a missing table is refused (exit 2, MISSING TABLE): metric_brief.py printed NOT FOUND for every code with exit 0 (LEARNINGS_V6 V6-04);
  - outside an Alarm folder it refuses (exit 2);
  - NOT FOUND points to where_v3.py, this Alarm folder's metric finder (where_v2 is not in the release).
Read only. Exit 0 printed; 2 refused."""
import argparse, csv, os, sys

DETECTION_TREE = ('01_Detection', 'tree')
TABLES = (('METRICS_V1', 'team/LAB3/METRICS_V1.tsv'),
          ('METRIC_TRAPS', 'team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv'),
          ('CATALOGS', 'team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv'),
          ('CATALOGS', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv'))
FINDER = '01_Detection/tree/team/LAB3/LAB1/tools/where_v2/where_v3.py'
CARD_FIELDS = [('meaning', 'MEANS'), ('unit_text', 'UNIT'), ('unit', 'UNIT'), ('scope_text', 'SCOPE'), ('step', 'STEP'),
               ('window', 'WINDOW'), ('use_may', 'MAY USE'), ('first', 'FIRST DAY'), ('last', 'LAST DAY'), ('card', 'CARD')]
TRAP_FIELDS = [('empty_means', 'EMPTY MEANS'), ('never_read_as', 'NEVER READ AS'), ('read_it_as', 'READ IT AS')]


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


def tables(tree):
    """(METRICS, TRAPS, CATALOGS) inside the detection tree; a missing one is refused, never read as empty"""
    paths = [(k, os.path.join(tree, *p.split('/'))) for k, p in TABLES]
    miss = ['%s %s' % (k, p) for k, p in paths if not os.path.isfile(p)]
    if miss:
        raise Refused('MISSING TABLE %s (the Alarm folder must hold it)' % '; '.join(miss))
    return paths[0][1], paths[1][1], [p for k, p in paths[2:]]


def rows(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def flag(status):
    s = (status or '').upper()
    if s.startswith('DO NOT USE') or s.startswith('WITHDRAWN'):
        return f'STOP: {status}: never use it'
    if s.startswith('NAME MISLEADS'):
        return f'RULE: {status}: the name misleads, read it only by the rule below'
    if 'MEANING NOT YET TESTED' in s:
        return f'CAUTION: {status}: a described reading only, never the basis of a claim'
    if s.startswith('NOT YET CHECKED'):
        return f'CAUTION: {status}: not yet checked by LAB4'
    if s.startswith('PROVEN'):
        return ''
    return f'CAUTION: {status or "NO STATUS"}: not a known proven status, treat as unproven'


def brief(card, trap, code):
    out = [f'== {code}  {(card or {}).get("card_name") or (trap or {}).get("name") or ""}']
    if trap:
        f = flag(trap.get('status'))
        if f:
            out.append('   ' + f)
        out.append(f'   STATUS: {trap.get("status") or "?"}')
    else:
        out.append('   STATUS: not in METRIC_TRAPS_V3 (no LAB4 row): read the card itself before using it')
    shown = set()
    for k, label in CARD_FIELDS:
        v = ((card or {}).get(k) or '').strip()
        if v and label not in shown:
            shown.add(label)
            out.append(f'   {label}: {v}')
    for k, label in TRAP_FIELDS:
        v = ((trap or {}).get(k) or '').strip()
        if v:
            out.append(f'   {label}: {v}')
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('codes', nargs='*')
    ap.add_argument('--grep')
    ap.add_argument('--family')
    ap.add_argument('--settings')
    a = ap.parse_args(argv)
    try:
        S = settings_module(__file__)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr)
        return 2
    try:
        if a.settings:
            S.load(a.settings)
        METRICS, TRAPS, CATALOGS = tables(detection_tree(__file__, S))
    except (Refused, S.Refused) as e:
        print('REFUSED %s' % e, file=sys.stderr)
        return 2
    cards = {r['code']: r for r in rows(METRICS)}
    for p in CATALOGS:
        for r in rows(p):
            cards.setdefault(r['code'], r)
    traps = {r['code']: r for r in rows(TRAPS)}
    allcodes = list(dict.fromkeys(list(cards) + list(traps)))
    pick = []
    if a.codes:
        pick += a.codes
    if a.family:
        pick += [c for c in allcodes if c.split('.')[0] == a.family or c.startswith(a.family + '.')]
    if a.grep:
        g = a.grep.lower()
        pick += [c for c in allcodes if g in (c + ' ' + (cards.get(c, {}).get('card_name') or '') + ' '
                                              + (cards.get(c, {}).get('meaning') or '')).lower()]
    out = []
    for c in dict.fromkeys(pick):
        if c not in cards and c not in traps:
            out.append(f'== {c}: NOT FOUND in METRICS_V1, METRIC_TRAPS_V3 or the CTX / EPI catalogues: find it with where_v3 ({FINDER}) before using it')
        else:
            out += brief(cards.get(c), traps.get(c), c)
    print('\n'.join(out) if out else 'nothing matched')
    return 0


if __name__ == '__main__':
    sys.exit(main())
