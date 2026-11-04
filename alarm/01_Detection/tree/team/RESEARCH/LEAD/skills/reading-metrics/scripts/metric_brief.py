"""metric_brief: print how to read each metric, from its card.

ONE source per fact (LAB1 23 Oct): status, never_read_as, read_it_as and empty_means come from LAB4's METRIC_TRAPS_V3.tsv (every METRICS_V1 entry, 23 Oct 14:17Z);
meaning, unit, scope, step, window, days and card path from METRICS_V1 (and the CTX / EPI catalogues for alarm values).

Usage: python3 metric_brief.py C2.S04 A1.S01 ...      (exact codes)
       python3 metric_brief.py --grep "basket"         (search code, name, meaning)
       python3 metric_brief.py --family B1             (every code of a family)
Read only. Paths can be overridden by the env vars METRICS_V1, METRIC_TRAPS, CATALOGS (colon separated) for tests.
"""
import argparse, csv, os

F = '<LAB_REPO>/forensics'
METRICS = os.environ.get('METRICS_V1', f'{F}/team/LAB3/METRICS_V1.tsv')
TRAPS = os.environ.get('METRIC_TRAPS', f'{F}/team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv')
CATALOGS = [p for p in os.environ.get('CATALOGS', f'{F}/team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv:'
                                                   f'{F}/team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv').split(':') if p]
CARD_FIELDS = [('meaning', 'MEANS'), ('unit_text', 'UNIT'), ('unit', 'UNIT'), ('scope_text', 'SCOPE'), ('step', 'STEP'),
               ('window', 'WINDOW'), ('use_may', 'MAY USE'), ('first', 'FIRST DAY'), ('last', 'LAST DAY'), ('card', 'CARD')]
TRAP_FIELDS = [('empty_means', 'EMPTY MEANS'), ('never_read_as', 'NEVER READ AS'), ('read_it_as', 'READ IT AS')]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('codes', nargs='*')
    ap.add_argument('--grep')
    ap.add_argument('--family')
    a = ap.parse_args()
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
            out.append(f'== {c}: NOT FOUND in METRICS_V1, METRIC_TRAPS_V3 or the CTX / EPI catalogues: find it with where_v2 before using it')
        else:
            out += brief(cards.get(c), traps.get(c), c)
    print('\n'.join(out) if out else 'nothing matched')


if __name__ == '__main__':
    main()
