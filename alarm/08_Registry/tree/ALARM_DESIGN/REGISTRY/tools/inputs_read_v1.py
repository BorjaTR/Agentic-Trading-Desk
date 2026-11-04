#!/usr/bin/env python3
"""inputs_read_v1.py (SCOUT, 31 Oct 2026; TEST, NOT REVIEWED): which metric codes the registry's alarms read, and which readable codes
no alarm reads yet. Round 7 (AD20 and AD19, 31 Oct): the idea step took 6.8 of 17 and 10.5 of 22 minutes, because no list said which
inputs no alarm reads (team/SCOUT/R7_FIXES_V1.tsv F05 and F14).

  python3 -B <Alarm>/08_Registry/tree/ALARM_DESIGN/REGISTRY/tools/inputs_read_v1.py --settings <settings file>
      [--registry REGISTRY/ALARM_REGISTRY_V1.tsv] [--tags REGISTRY/FAMILY_TAGS_V1.tsv]
      [--out REGISTRY/INPUTS_READ_V1.tsv] [--page REGISTRY/INPUTS_READ_V1.md]
  (a relative path is under RESEARCH_ROOT/ALARM_DESIGN of the settings file, from any working folder)

What it reads: the registry (each alarm's definition at def_rel under ALARM_DESIGN, checked against its def_sha16; a definition that
is missing, changed since the decision or no JSON is counted and skipped, never read as reading nothing), the family tags (SCOUT's
classification, an opinion), and the metric tables of the Alarm folder that holds this file (01_Detection/tree: METRICS_V1.tsv and the
two catalogues for each code's card, LAB4's METRIC_TRAPS_V3.tsv for its status), through metric_brief_v2.py (its tables and its flag
words: a STOP or CAUTION code is refused in a decision line by the detector's admission).
A code is read by an alarm when an input of its definition names it (an input with a code: raw, market, ...).
Flags: OK (a PROVEN status: metric_brief_v2 prints no flag), RULE, CAUTION, STOP (metric_brief_v2's first word), NO ROW (no LAB4
status row: the detector refuses it as UNPROVEN), NOT IN TABLES (a code a definition reads that no table holds).
What it writes (only outside the Alarm folder; a twin <file>.pre_SCOUT_<UTC> first when the file exists):
  --out   one row per code (columns COLS below): its flag and status, its card's unit, scope, step and short name, how many alarms read
          it, their states (the scoreboard's words PASS, NEEDS MORE MONTHS, STOP; else the registry's state), their families, how many
          of them are FOUND (scoreboard_v2.verdict) and the alarms (id=state)
  --page  per idea family, the codes its alarms read and the OK codes nobody reads in the same groups; then per group, the OK codes no
          alarm reads (a group is the part before the code's station: A1.S01 -> A1, X1.LIQX.S01 -> X1.LIQX, A1.S07.grid_off -> A1)
Refused with rc 2: no --settings, a settings file the reader refuses, an empty RESEARCH_ROOT, an output inside the Alarm folder, this
file outside an Alarm folder, a missing metric table or metric_brief_v2.py. A wrong argument: rc 1 with the usage."""
import csv
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import novelty_v2 as NV     # noqa: E402  (the Alarm package and the settings, shared by the registry tools)
import scoreboard_v2 as SB  # noqa: E402  (state_of and verdict: the scoreboard's PASS, NEEDS MORE MONTHS, STOP and FOUND)

MB_REL = ('01_Detection', 'tree', 'team', 'RESEARCH', 'LEAD', 'skills', 'reading-metrics', 'scripts', 'metric_brief_v2.py')
COLS = ('code', 'group', 'flag', 'status', 'unit', 'scope', 'step_s', 'short', 'alarms_n', 'states', 'families', 'found', 'alarms')
OPTS = {'--registry': 'REGISTRY/ALARM_REGISTRY_V1.tsv', '--tags': 'REGISTRY/FAMILY_TAGS_V1.tsv', '--out': 'REGISTRY/INPUTS_READ_V1.tsv',
        '--page': 'REGISTRY/INPUTS_READ_V1.md'}
USAGE = ('inputs_read_v1.py --settings <settings file> [--registry REGISTRY/ALARM_REGISTRY_V1.tsv] [--tags REGISTRY/FAMILY_TAGS_V1.tsv] '
         '[--out REGISTRY/INPUTS_READ_V1.tsv] [--page REGISTRY/INPUTS_READ_V1.md]   (a relative path is under RESEARCH_ROOT/ALARM_DESIGN)')


def sha16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def table(p):
    with open(p) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def cell(v):
    return ' '.join(str(v).split()) or '-'


def brief_module(alarm):
    """metric_brief_v2.py of this Alarm folder, imported by its path: its tables and its flag words"""
    p = os.path.join(alarm, *MB_REL)
    if not os.path.isfile(p):
        raise NV.Refused('MISSING %s (the Alarm folder must hold metric_brief_v2.py)' % p)
    sp = importlib.util.spec_from_file_location('metric_brief_v2_for_inputs_read', p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def metric_tables(MB, alarm):
    """(cards {code: row}, traps {code: row}, [(label, path, sha16)]) from the Alarm folder's detection tree"""
    try:
        metrics, traps, catalogs = MB.tables(os.path.join(alarm, *MB.DETECTION_TREE))
    except MB.Refused as e:
        raise NV.Refused(str(e))
    cards = {r['code']: r for r in MB.rows(metrics)}
    for p in catalogs:
        for r in MB.rows(p):
            cards.setdefault(r['code'], r)
    used = [(os.path.basename(p), p, sha16(p)) for p in [metrics, traps] + list(catalogs)]
    return cards, {r['code']: r for r in MB.rows(traps)}, used


def flag_word(MB, trap):
    """OK, RULE, CAUTION or STOP (metric_brief_v2.flag's first word; no flag = a PROVEN status = OK), NO ROW without a LAB4 row"""
    if trap is None:
        return 'NO ROW'
    f = MB.flag(trap.get('status'))
    return f.split(':', 1)[0].strip() if f else 'OK'


def group(code):
    """the parts before the code's station (S and digits): A1.S01 -> A1, X1.LIQX.S01 -> X1.LIQX, a setting A1.S07.grid_off -> A1;
    a code with no station: without its last part (LAB.coin_long_5s -> LAB)"""
    parts = code.split('.')
    for i, p in enumerate(parts):
        if i and re.fullmatch(r'S[0-9]+', p):
            return '.'.join(parts[:i])
    return code.rsplit('.', 1)[0] if '.' in code else code


def codes_of(d):
    """the metric codes the inputs of a definition name (an input with a code: raw, market, ...), sorted"""
    ins = d.get('inputs') if isinstance(d, dict) else None
    if not isinstance(ins, dict):
        return []
    return sorted({v['code'].strip() for v in ins.values() if isinstance(v, dict) and isinstance(v.get('code'), str) and v['code'].strip()})


def read_defs(reg, design):
    """-> ({alarm_id: codes} for each alarm whose definition is there with its recorded sha16, {why: [alarm_id]} for the others:
    none (no definition: desk triggers), missing, changed (sha16 not the recorded one), unreadable (no JSON))"""
    got, skip = {}, {'none': [], 'missing': [], 'changed': [], 'unreadable': []}
    for r in reg:
        a, rel, want = r['alarm_id'], (r.get('def_rel') or '').strip(), (r.get('def_sha16') or '').strip()
        if rel in ('', '-'):
            skip['none'].append(a)
            continue
        p = os.path.join(design, rel)
        if not os.path.isfile(p):
            skip['missing'].append(a)
            continue
        if want not in ('', '-') and sha16(p) != want:
            skip['changed'].append(a)
            continue
        try:
            with open(p) as f:
                d = json.load(f)
        except ValueError:
            skip['unreadable'].append(a)
            continue
        got[a] = codes_of(d)
    return got, skip


def state(r):
    return SB.state_of(r) or cell(r.get('state') or '-')


def build(reg, tags, defs, cards, traps, MB):
    """the rows of --out: one per code of the tables, and one per code a definition reads that no table holds"""
    fam = {t['alarm_id']: t['family'] for t in tags}
    by = {}
    for r in reg:
        for c in defs.get(r['alarm_id'], ()):
            by.setdefault(c, []).append(r)
    out = []
    for c in sorted(set(cards) | set(traps) | set(by)):
        card, trap, rs = cards.get(c) or {}, traps.get(c), by.get(c, [])
        st = {}
        for r in rs:
            st[state(r)] = st.get(state(r), 0) + 1
        out.append({'code': c, 'group': group(c),
                    'flag': flag_word(MB, trap) if (c in cards or c in traps) else 'NOT IN TABLES',
                    'status': cell((trap or {}).get('status') or '-'), 'unit': cell(card.get('unit') or '-'),
                    'scope': cell(card.get('scope') or '-'), 'step_s': cell(card.get('step_s') or '-'),
                    'short': cell(card.get('short') or card.get('card_name') or (trap or {}).get('name') or '-'),
                    'alarms_n': len(rs), 'states': '; '.join('%s %d' % (k, st[k]) for k in sorted(st)) or '-',
                    'families': ', '.join(sorted({fam[r['alarm_id']] for r in rs if r['alarm_id'] in fam})) or '-',
                    'found': sum(1 for r in rs if SB.verdict(r) == 'FOUND'),
                    'alarms': ', '.join(sorted('%s=%s' % (r['alarm_id'], state(r)) for r in rs)) or '-'})
    return out


def unread(rows, groups=None):
    """{group: [OK codes no alarm reads]} (in the groups named, or all)"""
    g = {}
    for r in rows:
        if r['flag'] == 'OK' and r['alarms_n'] == 0 and (groups is None or r['group'] in groups):
            g.setdefault(r['group'], []).append(r['code'])
    return g


def render(rows, reg, tags, defs, skip, src):
    """the page: per idea family, then the unread OK codes per group"""
    byc = {r['code']: r for r in rows}
    regd = {r['alarm_id']: r for r in reg}
    fams = {}
    for t in tags:
        if t['alarm_id'] in regd:
            fams.setdefault(t['family'], []).append(regd[t['alarm_id']])
    tagged = {t['alarm_id'] for t in tags}
    n_ok = sum(1 for r in rows if r['flag'] == 'OK')
    n_ok_read = sum(1 for r in rows if r['flag'] == 'OK' and r['alarms_n'])
    L = ['# INPUTS READ V1: which metric codes the alarms read, and the OK codes no alarm reads yet',
         '', 'inputs_read_v1.py, %s. TEST, NOT REVIEWED. Read it at step 1 (IDEA) with SCOREBOARD.md: a new idea reads an OK code no '
             'alarm reads, or its card says why a code its family already reads gives a new moment.' % dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
         '', 'Sources: %s.' % '; '.join('%s %s' % (lab, s) for lab, s in src),
         'Alarms: %d in the registry; %d definitions read; skipped: %s.' % (
             len(reg), len(defs), '; '.join('%s %d%s' % (k, len(v), (' (%s)' % ', '.join(sorted(v))) if v and k != 'none' else '')
                                             for k, v in skip.items())),
         'Codes: %d in the tables; OK %d, of which %d read by an alarm and %d by none; flags: OK = a PROVEN status; RULE, CAUTION, STOP as '
         'metric_brief_v2 prints them (the detector refuses STOP and CAUTION in a decision line); NO ROW = no LAB4 status (refused as '
         'UNPROVEN). Families are SCOUT\'s classification (FAMILY_TAGS_V1.tsv), an opinion.' % (
             sum(1 for r in rows if r['flag'] != 'NOT IN TABLES'), n_ok, n_ok_read, n_ok - n_ok_read), '']
    L.append('## By idea family')
    for f in sorted(fams):
        rs = fams[f]
        st = {}
        for r in rs:
            st[state(r)] = st.get(state(r), 0) + 1
        found = sum(1 for r in rs if SB.verdict(r) == 'FOUND')
        read = {}
        for r in rs:
            for c in defs.get(r['alarm_id'], ()):
                read.setdefault(c, []).append(r)
        L.append('### %s: %d alarms (%s), FOUND %d' % (f, len(rs), '; '.join('%s %d' % (k, st[k]) for k in sorted(st)), found))
        if read:
            L.append('- codes its alarms read: ' + '; '.join(
                '%s %s (%s)' % (c, byc[c]['flag'], ', '.join(sorted('%s=%s' % (r['alarm_id'], state(r)) for r in read[c]))) for c in sorted(read)))
            u = unread(rows, {group(c) for c in read})
            L.append('- OK codes no alarm reads, in the same groups: ' + ('; '.join(
                '%s: %s' % (g, ', '.join('%s %s' % (c, byc[c]['short']) for c in u[g])) for g in sorted(u)) or 'none'))
        else:
            L.append('- no definition read (desk triggers, or skipped above)')
    un = sorted(a for a in defs if a not in tagged)
    if un:
        L.append('### untagged: %d alarms with a definition (%s)' % (len(un), ', '.join(un)))
    L += ['', '## OK codes no alarm reads, by group (details in the --out table)']
    allg = {}
    for r in rows:
        if r['flag'] == 'OK':
            allg.setdefault(r['group'], []).append(r)
    u = unread(rows)
    for g in sorted(allg):
        if g in u:
            L.append('- %s (%d of %d OK unread): %s' % (g, len(u[g]), len(allg[g]), ', '.join(u[g])))
    return '\n'.join(L) + '\n'


def write(path, text):
    """a twin <path>.pre_SCOUT_<UTC> first when path exists, then path"""
    if os.path.exists(path):
        twin = '%s.pre_SCOUT_%s' % (path, dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'))
        with open(path, 'rb') as f, open(twin, 'xb') as g:
            g.write(f.read())
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w') as f:
        f.write(text)


def main(a):
    a = list(a)
    sf = NV.take_settings(a)
    o = dict(OPTS)
    i = 0
    while i < len(a):
        if a[i] in o and i + 1 < len(a):
            o[a[i]] = a[i + 1]
            i += 2
        else:
            raise SystemExit('USAGE: ' + USAGE)
    alarm, S, s = NV.settings(sf, __file__)                       # refused when RESEARCH_ROOT is empty (settings_v1.get)
    design = NV.design_root(s['RESEARCH_ROOT'])
    p = {k: NV.under(v, design) for k, v in o.items()}
    out, page = NV.outside(p['--out'], alarm, S), NV.outside(p['--page'], alarm, S)
    MB = brief_module(alarm)
    cards, traps, used = metric_tables(MB, alarm)
    reg, tags = table(p['--registry']), table(p['--tags'])
    defs, skip = read_defs(reg, design)
    rows = build(reg, tags, defs, cards, traps, MB)
    src = ([('inputs_read_v1.py', sha16(os.path.abspath(__file__))), (o['--registry'], sha16(p['--registry'])),
            (o['--tags'], sha16(p['--tags']))] + [(lab, s16) for lab, _, s16 in used])
    write(out, '# INPUTS_READ_V1 (inputs_read_v1.py, %s; sources: %s)\n' % (
        dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), '; '.join('%s %s' % x for x in src))
          + '\t'.join(COLS) + '\n' + ''.join('\t'.join(cell(r[c]) for c in COLS) + '\n' for r in rows))
    write(page, render(rows, reg, tags, defs, skip, src))
    print('WROTE %s %s codes %d read %d; WROTE %s %s' % (o['--out'], sha16(out), len(rows), sum(1 for r in rows if r['alarms_n']),
                                                        o['--page'], sha16(page)))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except NV.Refused as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
