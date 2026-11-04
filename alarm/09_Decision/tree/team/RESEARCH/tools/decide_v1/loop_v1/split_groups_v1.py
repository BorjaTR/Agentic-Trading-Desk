"""split_groups_v1.py (DECIDE seat, 26 Oct 2026): the outcome loop of decision tool V1 grades each decision group on its own. From one
decision run it writes four event lists, copying the event rows of TAKE_EVENTS.tsv and SKIP_EVENTS.tsv unchanged, in DECISIONS.tsv order:
  TAKE (no skip line true), SKIPRULE (a skip line true), BADDATA (the data gate), VALUED = TAKE + SKIPRULE (every fire whose used fields
  hold a reading: the fair base to compare TAKE and SKIPRULE against; BADDATA is reported apart).
It first calls decide_v1.verify_run() on the run folder (the run must be committed and unchanged since, kit rows 3 and 11).
It refuses when the groups do not add up to the decision rows or an event is not where DECISIONS.tsv puts it.
  python3 -B split_groups_v1.py <decision run folder> <new out folder>  -> TAKE_, SKIPRULE_, BADDATA_, VALUED_EVENTS.tsv, SPLIT.json"""
import datetime as dt, hashlib, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
import decide_v1 as DV

def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def table(p):
    L = [l.rstrip('\n') for l in open(p) if l.strip()]
    return L[0], [dict(zip(L[0].split('\t'), l.split('\t'))) for l in L[1:]], L[1:]

GROUPS = {'TAKE': ('NO_SKIP_LINE_TRUE',), 'SKIPRULE': ('SKIP_RULE',), 'BADDATA': ('BAD_DATA',), 'VALUED': ('NO_SKIP_LINE_TRUE', 'SKIP_RULE')}

def main(run, out):
    if os.path.exists(out):
        sys.exit('REFUSED: out folder exists')
    try:
        run_rec = DV.verify_run(run)
    except DV.Refused as e:
        sys.exit('REFUSED %s' % e)
    _, dec, _ = table(os.path.join(run, 'DECISIONS.tsv'))
    key = lambda r: (r['alarm_id'], r['coin'], r['t'], r['side'])
    reason = {key(r): r['reason'] for r in dec}
    if len(reason) != len(dec):
        sys.exit('REFUSED: a fire is twice in DECISIONS.tsv')
    ev = {}; head = None
    for n, want in (('TAKE_EVENTS.tsv', 'TAKE'), ('SKIP_EVENTS.tsv', 'SKIP')):
        h, rows, raw = table(os.path.join(run, n))
        if head not in (None, h):
            sys.exit('REFUSED: the two event lists have different headers')
        head = h
        for r, l in zip(rows, raw):
            k = key(r)
            if k not in reason or (reason[k] == 'NO_SKIP_LINE_TRUE') != (want == 'TAKE') or k in ev:
                sys.exit('REFUSED: event %s is not where DECISIONS.tsv puts it' % (k,))
            ev[k] = l
    if set(ev) != set(reason):
        sys.exit('REFUSED: %d decision rows, %d events' % (len(reason), len(ev)))
    other = sorted({r['reason'] for r in dec} - {'NO_SKIP_LINE_TRUE', 'SKIP_RULE', 'BAD_DATA'})
    os.makedirs(out)
    rec = {'schema': 'DECIDE_LOOP_SPLIT_V2', 'run': run, 'run_verified': True, 'run_tool_sha16': run_rec.get('tool_sha16'), 'decisions_sha16': sha16(os.path.join(run, 'DECISIONS.tsv')),
           'take_events_sha16': sha16(os.path.join(run, 'TAKE_EVENTS.tsv')), 'skip_events_sha16': sha16(os.path.join(run, 'SKIP_EVENTS.tsv')),
           'other_reasons_not_graded': other, 'groups': {}}
    for g, rs in GROUPS.items():
        rows = [r for r in dec if r['reason'] in rs]
        p = os.path.join(out, '%s_EVENTS.tsv' % g)
        open(p, 'w').write('\n'.join([head] + [ev[key(r)] for r in rows]) + '\n')
        days = sorted(dt.datetime.fromtimestamp(int(r['t']), dt.timezone.utc).strftime('%Y%m%d') for r in rows)
        rec['groups'][g] = {'fires': len(rows), 'first_day': days[0] if days else '', 'last_day': days[-1] if days else '', 'sha16': sha16(p)}
    if rec['groups']['VALUED']['fires'] != rec['groups']['TAKE']['fires'] + rec['groups']['SKIPRULE']['fires']:
        sys.exit('REFUSED: VALUED is not TAKE + SKIPRULE')
    json.dump(rec, open(os.path.join(out, 'SPLIT.json'), 'w'), indent=1)
    print(json.dumps(rec['groups']))

if __name__ == '__main__':
    main(*sys.argv[1:3])
