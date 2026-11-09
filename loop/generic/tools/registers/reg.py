#!/usr/bin/env python3
"""reg.py (SCOUT 2026-11-08, the owner 07:41Z "log all of this in some register"): the one writer of the two drill registers.
  python3 -B reg.py drill  k=v ...   append one row to DRILL_RUNS.tsv   (one row per drill run: one agent, one arm, one snapshot)
  python3 -B reg.py improve k=v ...  append one row to IMPROVEMENTS.tsv (one row per process change, with the drill that found it and the drill that verified it)
  python3 -B reg.py mess k=v ...    append one row to MESSY.tsv (a contradiction, stale or unclear line any agent reported; fixed_in = the C id)
  python3 -B reg.py score k=v ...    append one score of one process part to SCORES.tsv (part_id from PARTS.tsv)
  python3 -B reg.py ledger part_id=P01 file=<path> change_id=C47 what=... found_by=... verified_by=...
                                     append one change of one file to LEDGER.tsv; sha16_before (last row of that file) and sha16_after (now) are filled
  python3 -B reg.py baseline [who=SEAT]  C218: a new seat's first ledger rows: one BASELINE row per PARTS.tsv file with no row yet;
                                     refuses (writes nothing) while any PARTS.tsv file is missing. {NAME} in a files cell = env LL_<NAME>
  python3 -B reg.py ledger-check     every file of every part in PARTS.tsv: FLAG when its bytes differ from its last LEDGER row (an unlogged change) or it has no row
  python3 -B reg.py scorecard        latest score per part
  python3 -B reg.py view [out.tsv]   the unified ledger: one row per part (level, score, drills, drill runs, median minutes, last change, open reports)
  python3 -B reg.py audit            drill LOOP_AUDIT: unverified ledger changes, proposals adopted without drills, open reports, ledger-check
  python3 -B reg.py history P01      every event of one part (scores, changes, drill runs, reports, proposals), oldest first
  python3 -B reg.py proposal k=v ... append one proposal (or its next status, prop_id P001b ...) to PROPOSALS.tsv (PROCESS_IMPROVEMENT_V1.md)
  python3 -B reg.py import-report <file> --from <id>   load an agent's REPORT block (drills_v2/REPORT_TEMPLATE_V1.md) into MESSY and PROPOSALS
  python3 -B reg.py check            every row has every field; every improvement's found_by and verified_by name a drill_id in DRILL_RUNS
Unknown or missing fields are refused; utc is filled when empty. Rows are never edited: a correction is a new row with note 'corrects <id>'."""
import csv, datetime, hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
COLS = {'mess': ['mess_id', 'utc', 'found_by', 'file', 'line_quoted', 'kind', 'fix', 'fixed_in', 'status'],
        'drill': ['run_id', 'utc', 'drill_id', 'part', 'question', 'snapshot', 'arm', 'agent', 'score', 'max', 'pass', 'minutes', 'tool_calls', 'finding', 'files'],
        'improve': ['imp_id', 'utc', 'part', 'problem', 'evidence', 'change', 'files', 'found_by', 'before', 'after', 'verified_by', 'status'],
        'score': ['score_id', 'utc', 'part_id', 'score', 'max', 'status', 'good', 'improve', 'evidence'],
        'ledger': ['led_id', 'utc', 'part_id', 'file', 'sha16_before', 'sha16_after', 'change_id', 'what', 'found_by', 'verified_by'],
        'proposal': ['prop_id', 'utc', 'from_agent', 'part_id', 'change', 'expected', 'evidence', 'status', 'checked_by', 'check_note', 'drill_before', 'drill_after', 'change_id', 'ledger_id']}
FILE = {'drill': 'DRILL_RUNS.tsv', 'improve': 'IMPROVEMENTS.tsv', 'mess': 'MESSY.tsv', 'score': 'SCORES.tsv', 'ledger': 'LEDGER.tsv', 'proposal': 'PROPOSALS.tsv'}
PROP_STATUS = ('PROPOSED', 'CHECKED', 'REJECTED', 'DRILLED', 'ADOPTED', 'NOT_ADOPTED')   # PROCESS_IMPROVEMENT_V1.md; a status change is a new row with the same prop_id + suffix
STATUS = ('PROVEN', 'WORKS', 'WEAK', 'NOT_MEASURED')
SERIES = os.environ.get('LL_SEAT_ROOT', os.path.dirname(os.path.dirname(HERE)))   # RC2: {SEAT_ROOT}, where relative part files resolve (default as in the source: two folders up)
def regdir():   # RC2: {REGISTERS}, the seat's register folder: env LL_REGISTERS, else beside reg.py as in the source (read at each call, so a test may move HERE)
    return os.environ.get('LL_REGISTERS', HERE)
def parts():
    return list(csv.DictReader(open(os.path.join(regdir(), 'PARTS.tsv')), delimiter='\t'))
def fpath(f):
    f = re.sub(r'\{([A-Z_]+)\}', lambda m: os.environ.get('LL_' + m.group(1), m.group(0)), f)   # C218: {GENERIC}, {PACK}, {SKILLS}, {SEAT_ROOT} ... = env LL_<NAME>; unset stays literal (MISSING)
    f = os.path.expanduser(f); return f if os.path.isabs(f) else os.path.join(SERIES, f)
def sha16(f):
    p = fpath(f); return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else 'MISSING'
def last_sha(f):
    r = [x for x in rows('ledger') if x['file'] == f]; return r[-1]['sha16_after'] if r else '-'
def ledger(kv):
    pid = {p['part_id'] for p in parts()}
    if kv.get('part_id') not in pid: sys.exit('REFUSED unknown part_id %s' % kv.get('part_id'))
    f = kv.get('file', '')
    if sha16(f) == 'MISSING': sys.exit('REFUSED no such file %s' % f)
    kv['sha16_before'] = last_sha(f); kv['sha16_after'] = sha16(f)
    if kv['sha16_before'] == kv['sha16_after']: sys.exit('REFUSED no change since the last ledger row of %s' % f)
    kv.setdefault('led_id', 'G%04d' % (len(rows('ledger')) + 1)); add('ledger', kv)
def baseline(kv):
    """C218 (review B6): a new seat's first ledger rows. One BASELINE row per PARTS.tsv file that has no ledger row yet.
    Refuses and writes nothing while any PARTS.tsv file is missing: point each files cell at the seat's own copy first."""
    bad = [k for k in kv if k not in ('who', 'utc')]
    if bad: sys.exit('REFUSED unknown fields %s' % bad)
    have = {r['file'] for r in rows('ledger')}; todo, miss, seen = [], [], set()
    for p in parts():
        for f in [x for x in p['files'].split(',') if x]:
            if f in have or f in seen: continue
            seen.add(f); (miss if sha16(f) == 'MISSING' else todo).append((p['part_id'], f))
    for pid, f in miss: print('MISSING', pid, f, '->', fpath(f))
    if miss:
        print('REFUSED BASELINE_MISSING files %d: point these PARTS.tsv files cells at the seat\'s own copies (or set LL_<NAME> for {NAME}), then rerun' % len(miss)); return 2
    for pid, f in todo:
        ledger({'part_id': pid, 'file': f, 'change_id': 'BASELINE', 'what': 'baseline: the file as it stands when this seat ledger started',
                'found_by': kv.get('who') or 'seat start', 'verified_by': 'ledger-check', 'utc': kv.get('utc', '')})
    print('BASELINE rows %d' % len(todo)); return 0
def ledger_check():
    flags = 0; n = 0
    for p in parts():
        for f in [x for x in p['files'].split(',') if x]:
            n += 1; now, last = sha16(f), last_sha(f)
            if last == '-': print('FLAG NO_BASELINE', p['part_id'], f); flags += 1
            elif now != last: print('FLAG CHANGED_WITHOUT_LEDGER_ROW', p['part_id'], f, 'ledger', last, 'now', now); flags += 1
    print('LEDGER_CHECK %s files %d flags %d' % ('PASS' if not flags else 'FLAG', n, flags)); return 1 if flags else 0
def scorecard():
    last = {}
    for r in rows('score'): last[r['part_id']] = r
    for p in parts():
        r = last.get(p['part_id'])
        print('%s\t%s\t%s\t%s\t%s' % (p['part_id'], p.get('category', ''), p['name'], ('%s/%s' % (r['score'], r['max'])) if r else '-', r['status'] if r else 'NOT_SCORED'))
    # roll-up by category (the owner 09:12Z): counts per status and the weakest part (order: NOT_SCORED, NOT_MEASURED, WEAK, WORKS, PROVEN)
    rank = {'NOT_SCORED': 0, 'NOT_MEASURED': 1, 'WEAK': 2, 'WORKS': 3, 'PROVEN': 4}; cats = {}
    for p in parts():
        st = last[p['part_id']]['status'] if p['part_id'] in last else 'NOT_SCORED'
        cats.setdefault(p.get('category', ''), []).append((rank[st], st, p['part_id'], p['name']))
    print('CATEGORY\tparts\tPROVEN\tWORKS\tWEAK\tNOT_MEASURED\tweakest')
    for c, v in sorted(cats.items()):
        n = lambda k: sum(1 for x in v if x[1] == k)
        w = min(v); print('%s\t%d\t%d\t%d\t%d\t%d\t%s %s (%s)' % (c, len(v), n('PROVEN'), n('WORKS'), n('WEAK'), n('NOT_MEASURED') + n('NOT_SCORED'), w[2], w[3], w[1]))
    return 0
def rows(kind):
    p = os.path.join(regdir(), FILE[kind])
    return list(csv.DictReader(open(p), delimiter='\t')) if os.path.exists(p) else []
def add(kind, kv):
    cols = COLS[kind]; bad = [k for k in kv if k not in cols]
    if bad: sys.exit('REFUSED unknown fields %s' % bad)
    kv.setdefault('utc', ''); kv['utc'] = kv['utc'] or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    miss = [c for c in cols if c not in kv]
    if miss: sys.exit('REFUSED missing fields %s' % miss)
    idk = cols[0]
    if any(r[idk] == kv[idk] for r in rows(kind)): sys.exit('REFUSED duplicate %s %s' % (idk, kv[idk]))
    if kind == 'proposal' and kv['status'] not in PROP_STATUS: sys.exit('REFUSED status must be one of %s' % (PROP_STATUS,))
    if kind == 'score':
        if kv['status'] not in STATUS: sys.exit('REFUSED status must be one of %s' % (STATUS,))
        if kv['part_id'] not in {p['part_id'] for p in parts()}: sys.exit('REFUSED unknown part_id %s' % kv['part_id'])
    for v in kv.values():
        if '\t' in v or '\n' in v: sys.exit('REFUSED tab or newline in a value')
    p = os.path.join(regdir(), FILE[kind]); new = not os.path.exists(p)
    with open(p, 'a') as f:
        if new: f.write('\t'.join(cols) + '\n')
        f.write('\t'.join(kv[c] for c in cols) + '\n')
    print('ADDED', kind, kv[idk])
def check():
    d = rows('drill'); ids = {r['drill_id'] for r in d}; errs = 0
    for k in COLS:
        for r in rows(k):
            if any(r.get(c) is None for c in COLS[k]): print('SHORT ROW', k, r.get(COLS[k][0])); errs += 1
    for r in rows('improve'):
        for f in ('found_by', 'verified_by'):
            for x in [x for x in r[f].split(',') if x and x != 'none']:
                if x not in ids: print('UNKNOWN DRILL', r['imp_id'], f, x); errs += 1
    print('CHECK %s drill runs %d improvements %d' % ('PASS' if not errs else 'FAIL', len(d), len(rows('improve'))))
    return 1 if errs else 0
def view(out=None):
    """the unified ledger view (C54; PLAN_PROCESS_QUALITY_SYSTEM_20261108.md): one row per part, everything keyed on its id"""
    import statistics
    drills = list(csv.DictReader(open(os.path.join(regdir(), 'DRILLS.tsv')), delimiter='\t')) if os.path.exists(os.path.join(regdir(), 'DRILLS.tsv')) else []
    runs = rows('drill'); led = rows('ledger'); mess = rows('mess'); props = rows('proposal'); last = {}
    for r in rows('score'): last[r['part_id']] = r
    cols = ['part_id', 'category', 'name', 'level', 'score', 'drills', 'drill_runs', 'median_min', 'last_change', 'changes', 'open_messy', 'open_proposals']
    lines = ['\t'.join(cols)]
    for p in parts():
        pid = p['part_id']; files = [f for f in p['files'].split(',') if f]
        dl = sorted({d['drill_id'] for d in drills if pid in d['parts'].split(',')} | {x for x in p['drills'].split(',') if x and x != 'none'})
        dr = [r for r in runs if r['drill_id'] in dl]
        mins = [float(r['minutes']) for r in dr if r['minutes'].replace('.', '', 1).isdigit()]
        lc = [r for r in led if r['part_id'] == pid and r['change_id'] != 'BASELINE']
        lm = {}
        for r in mess: lm[r['mess_id'].rstrip('abcdefghijklmnopqrstuvwxyzL')] = r      # the latest row of each report id wins
        om = [r for r in lm.values() if r['status'] not in ('fixed', 'not_current') and any(f in r['file'] for f in files)]
        latest_prop = {}
        for r in props: latest_prop[r['prop_id'].rstrip('abcdefgh')] = r
        op = [r for r in latest_prop.values() if r['part_id'] == pid and r['status'] not in ('ADOPTED', 'REJECTED', 'NOT_ADOPTED')]
        sc = last.get(pid)
        lines.append('\t'.join([pid, p.get('category', ''), p['name'], sc['status'] if sc else 'NOT_SCORED', ('%s/%s' % (sc['score'], sc['max'])) if sc else '-',
                                 ','.join(dl) or '-', str(len(dr)), ('%.1f' % statistics.median(mins)) if mins else '-',
                                 (lc[-1]['utc'][:16] + ' ' + lc[-1]['change_id']) if lc else '-', str(len(lc)), str(len(om)), str(len(op))]))
    text = '\n'.join(lines) + '\n'
    if out: open(out, 'w').write(text)
    sys.stdout.write(text); return 0
def history(pid):
    """every event of one part, oldest first"""
    ev = []
    p = [x for x in parts() if x['part_id'] == pid]
    if not p: sys.exit('REFUSED unknown part_id %s' % pid)
    files = [f for f in p[0]['files'].split(',') if f]; dl = {x for x in p[0]['drills'].split(',') if x}
    for r in rows('score'):
        if r['part_id'] == pid: ev.append((r['utc'], 'SCORE', '%s/%s %s: %s' % (r['score'], r['max'], r['status'], r['improve'])))
    for r in rows('ledger'):
        if r['part_id'] == pid: ev.append((r['utc'], 'CHANGE', '%s %s %s -> %s: %s' % (r['change_id'], r['file'], r['sha16_before'], r['sha16_after'], r['what'])))
    for r in rows('drill'):
        if r['drill_id'] in dl: ev.append((r['utc'], 'DRILL', '%s %s/%s %s min: %s' % (r['run_id'], r['score'], r['max'], r['minutes'], r['finding'])))
    for r in rows('mess'):
        if any(f in r['file'] for f in files): ev.append((r['utc'], 'REPORT', '%s %s %s: %s' % (r['mess_id'], r['kind'], r['status'], r['line_quoted'])))
    for r in rows('proposal'):
        if r['part_id'] == pid: ev.append((r['utc'], 'PROPOSAL', '%s %s: %s' % (r['prop_id'], r['status'], r['change'])))
    print('HISTORY %s %s (%s)' % (pid, p[0]['name'], p[0].get('category', '')))
    for e in sorted(ev): print('\t'.join(e)[:400])
    return 0

def _t(u):
    return datetime.datetime.strptime(u, '%Y-%m-%dT%H:%M:%SZ')
def unverified(led, drills):
    """C89 (AUD1_a): a drill row closes a ledger row only if it STARTED after the change (start = utc minus minutes; a row is logged at
    its end) and its finding says 'verifies <G id or C id>', or it is a LOOP_AUDIT row that says 'superseded <G id>' (the flagged text
    was replaced by a later change, which stays open itself until verified). Ids match whole words (C8 never matches C87)."""
    import re
    ev = []
    for d in drills:
        try: st = _t(d['utc']) - datetime.timedelta(minutes=float(d.get('minutes') or 0))
        except ValueError: continue
        ids = set(re.findall(r'verifies ((?:[CG]\d+[a-z]?(?:[ ,]+(?:and )?)?)+)', d['finding']))
        v = set(x for g in ids for x in re.findall(r'[CG]\d+[a-z]?', g))
        sup = set(re.findall(r'superseded (G\d+)', d['finding'])) if d['drill_id'] == 'LOOP_AUDIT' else set()
        ev.append((st, v, sup))
    out = []
    for r in led:
        if not (r['verified_by'].startswith(('none', 'pending')) or r['verified_by'] in ('', '-')): continue
        lt = _t(r['utc'])
        if any(r['led_id'] in sup for st, v, sup in ev): continue
        if any(st > lt and (r['led_id'] in v or r['change_id'] in v) for st, v, sup in ev): continue
        out.append(r)
    return out

KINDS_MESSY = ('contradiction', 'two_readings', 'stale', 'missing', 'unclear')
def parse_report(text):
    """C130 (the owner 12:02Z "a template ... so all of them report in the same way"): the REPORT block of drills_v2/REPORT_TEMPLATE_V1.md.
    Returns (items, errors); items are (list, fields). Every list (MESSY, WASTE, PROPOSE) must have lines or a NONE line."""
    lines = text.splitlines()
    try: i = max(k for k, l in enumerate(lines) if l.strip() == '## REPORT')
    except ValueError: return [], ['NO_REPORT_BLOCK (a line "## REPORT")']
    items, errs, seen = [], [], set()
    want = {'MESSY': 6, 'WASTE': 4, 'PROPOSE': 7, 'NONE': 2}
    for n, l in enumerate(lines[i + 1:], i + 2):
        if l.strip().startswith('```') or not l.strip(): continue
        if l.startswith('## '): break
        f = [x.strip().replace('\t', ' ') for x in l.split(' | ')]   # C137: a tab inside a field stopped add() halfway (not all or nothing)
        if f[0] not in want: errs.append('line %d: unknown list %r' % (n, f[0])); continue
        if len(f) != want[f[0]]: errs.append('line %d: %s needs %d fields, has %d' % (n, f[0], want[f[0]], len(f))); continue
        if any(not x for x in f): errs.append('line %d: empty field' % n); continue
        if f[0] == 'MESSY' and f[1] not in KINDS_MESSY: errs.append('line %d: kind %r not one of %s' % (n, f[1], ', '.join(KINDS_MESSY))); continue
        if f[0] == 'WASTE':
            try: float(f[1])
            except ValueError: errs.append('line %d: minutes %r is not a number' % (n, f[1])); continue
        if f[0] == 'NONE' and f[1] not in ('MESSY', 'WASTE', 'PROPOSE'): errs.append('line %d: NONE names %r' % (n, f[1])); continue
        seen.add(f[1] if f[0] == 'NONE' else f[0]); items.append((f[0], f))
    for k in ('MESSY', 'WASTE', 'PROPOSE'):
        if k not in seen: errs.append('list %s missing (write its lines or NONE | %s)' % (k, k))
    if sum(1 for k, _ in items if k == 'PROPOSE') > 1: errs.append('more than one PROPOSE line')
    return items, errs
def import_report(path, src):
    """reg.py import-report <file> --from <id>: loads a REPORT block into MESSY.tsv (MESSY and WASTE lines) and PROPOSALS.tsv; all or nothing"""
    items, errs = parse_report(open(path, encoding='utf-8').read())
    if errs:
        for e in errs: print('REFUSED', e)
        return 2
    if any(r['found_by'] == src for r in rows('mess')) or any(r['from_agent'] == src for r in rows('proposal')):
        print('REFUSED ALREADY_IMPORTED from %s' % src); return 2
    def nxt(kind, pre):
        ids = [int(re.sub(r'[^0-9]', '', r[COLS[kind][0]].rstrip('abcdefghijklmnopqrstuvwxyzL'))) for r in rows(kind) if re.match(pre + r'\d+', r[COLS[kind][0]])]
        return pre + '%03d' % (max(ids or [0]) + 1)
    n_m = n_w = n_p = 0
    for k, f in items:
        if k == 'MESSY':
            add('mess', {'mess_id': nxt('mess', 'M'), 'found_by': src, 'file': f[2], 'line_quoted': f[3].strip('"'), 'kind': f[1], 'fix': 'A: %s; B: %s' % (f[4], f[5]), 'fixed_in': 'open', 'status': 'open'}); n_m += 1
        elif k == 'WASTE':
            add('mess', {'mess_id': nxt('mess', 'M'), 'found_by': src, 'file': '-', 'line_quoted': '%s min: %s' % (f[1], f[2]), 'kind': 'waste', 'fix': f[3], 'fixed_in': 'open', 'status': 'open'}); n_w += 1
        elif k == 'PROPOSE':
            add('proposal', {'prop_id': nxt('proposal', 'PR'), 'from_agent': src, 'part_id': f[1], 'change': '%s: %s' % (f[2], f[3]), 'expected': f[4], 'evidence': f[6], 'status': 'PROPOSED', 'checked_by': '-', 'check_note': 'drill: ' + f[5], 'drill_before': '-', 'drill_after': '-', 'change_id': '-', 'ledger_id': '-'}); n_p += 1
    print('IMPORTED %s: messy %d, waste %d, propose %d' % (src, n_m, n_w, n_p)); return 0

def audit():
    """drill LOOP_AUDIT (P29, P25, P13; C63): is the improvement loop followed? Prints counts and FLAG lines; exit 0 always (a report)."""
    led = [r for r in rows('ledger') if r['change_id'] != 'BASELINE']
    unver = unverified(led, rows('drill'))
    lp = {}
    for r in rows('proposal'): lp[r['prop_id'].rstrip('abcdefgh')] = r
    adopted = [r for r in lp.values() if r['status'] == 'ADOPTED']
    nodrill = [r for r in adopted if r['drill_before'] in ('', '-') or r['drill_after'] in ('', '-')]
    lm = {}
    for r in rows('mess'): lm[r['mess_id'].rstrip('abcdefghijklmnopqrstuvwxyzL')] = r
    openm = [r for r in lm.values() if r['status'] not in ('fixed', 'not_current')]
    print('AUDIT ledger changes %d, verified %d, unverified %d (%.0f pct)' % (len(led), len(led) - len(unver), len(unver), 100.0 * len(unver) / max(1, len(led))))
    for r in (unver if '--all' in sys.argv else unver[-15:]): print('FLAG UNVERIFIED', r['led_id'], r['part_id'], r['change_id'], r['file'], r['verified_by'])
    print('AUDIT proposals %d: %s; adopted without a drill before and after: %d' % (len(lp), ', '.join('%s %s' % (k, v['status']) for k, v in sorted(lp.items())), len(nodrill)))
    print('AUDIT reports (MESSY ids) %d, open %d: %s' % (len(lm), len(openm), ', '.join(r['mess_id'] for r in openm)))
    ledger_check(); return 0

if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    if sys.argv[1] == 'check': sys.exit(check())
    if sys.argv[1] == 'ledger-check': sys.exit(ledger_check())
    if sys.argv[1] == 'baseline': sys.exit(baseline(dict(a.split('=', 1) for a in sys.argv[2:])))
    if sys.argv[1] == 'scorecard': sys.exit(scorecard())
    if sys.argv[1] == 'view': sys.exit(view(sys.argv[2] if len(sys.argv) > 2 else None))
    if sys.argv[1] == 'history': sys.exit(history(sys.argv[2]))
    if sys.argv[1] == 'audit': sys.exit(audit())
    if sys.argv[1] == 'import-report':
        if len(sys.argv) != 5 or sys.argv[3] != '--from': sys.exit('usage: reg.py import-report <file> --from <id>')
        sys.exit(import_report(sys.argv[2], sys.argv[4]))
    kv = dict(a.split('=', 1) for a in sys.argv[2:])
    if sys.argv[1] == 'ledger': ledger(kv)
    else: add(sys.argv[1], kv)
