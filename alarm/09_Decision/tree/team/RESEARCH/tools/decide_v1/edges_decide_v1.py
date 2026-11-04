"""edges_decide_v1.py (DECIDE seat, 26 Oct 2026): test T1 of the lean workflow (volat-step3-test-producer): every case of
EDGES_DECIDE_V1.tsv (the card's part 4 as data) through the tool's rules, each answer exact. The case's values, push side, day and
variant are planted on one base rulebook and safety file (below, made up: ALARM_X, fields ctx.SPREAD, prof.SHAPE, ctx.RANGE).
expect is action|slot|reason|detail|trade_side (|entry|exit|size when given), or REFUSED (a run-stopping word), or RULEBOOK_REFUSED (the rulebook check refuses).
Every row of the file must run, and every setting of SETTINGS_DECIDE_V1.tsv that the rules hold (S01-S08) must be a target somewhere.
  python3 -B edges_decide_v1.py  -> one line per case, exit 1 on any failure"""
import copy, csv, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import decide_rules_v1 as DR

EV = {'source': 'x', 'sha16': '0123456789abcdef', 'cell': 'planted'}
TOOLS = {'entry': {'grader:TT', 'grader:RT'}, 'exit': {'grader:X1'}}
RS = ['UNKNOWN*', 'NO_HISTORY']


def base():
    return {'schema': 'DECIDE_RULEBOOK_V1', 'alarm_id': 'ALARM_X', 'version': 1,
            'side': {'value': 'FADE', 'status': 'CANDIDATE', 'evidence': dict(EV), 'mechanism': 'planted'},
            'skip_rules': [{'id': 'S1', 'field': 'ctx.SPREAD', 'states': ['TIGHT', 'ABOUT', 'WIDE'], 'reasons': list(RS), 'skip_if': ['TIGHT'],
                            'status': 'CANDIDATE', 'mechanism': 'planted', 'evidence': dict(EV)},
                           {'id': 'S2', 'field': 'prof.SHAPE', 'states': ['UP', 'FLAT', 'DOWN'], 'reasons': list(RS), 'skip_if': ['DOWN'],
                            'status': 'FROZEN', 'mechanism': 'planted', 'evidence': dict(EV)}],
            'entry': {'value': 'UNSET', 'status': 'DEFAULT'}, 'exit': {'value': 'UNSET', 'status': 'DEFAULT'}, 'size': {'value': 1, 'status': 'DEFAULT'}}


def plant(variant):
    rb = base(); sf = {'schema': 'DECIDE_SAFETY_V1', 'status': 'PLANTED', 'off_days': [], 'off_states': []}; mode = 'research'
    for v in [x for x in variant.split(';') if x and x != '-']:
        k, _, val = v.partition('=')
        if v == 'default':
            rb = {'schema': 'DECIDE_RULEBOOK_V1', 'alarm_id': '*', 'version': 1, 'side': {'value': 'UNSET', 'status': 'DEFAULT'}, 'skip_rules': [],
                  'entry': {'value': 'UNSET', 'status': 'DEFAULT'}, 'exit': {'value': 'UNSET', 'status': 'DEFAULT'}, 'size': {'value': 1, 'status': 'DEFAULT'}}
        elif k == 'mode': mode = val
        elif k == 'off_days': sf['off_days'] = [val]
        elif k == 'off_state': sf['off_states'] = [{'id': val, 'field': 'ctx.RANGE', 'states': ['LOW', 'MID', 'HIGH'], 'reasons': list(RS), 'off_if': ['HIGH']}]
        elif k == 'side': rb['side'] = {'value': val, 'status': 'DEFAULT'} if val == 'UNSET' else dict(rb['side'], value=val)
        elif k == 'side.status': rb['side']['status'] = val
        elif k == 'entry': rb['entry'] = {'value': val, 'status': 'CANDIDATE', 'evidence': dict(EV)}
        elif k == 'exit': rb['exit'] = {'value': val, 'status': 'CANDIDATE', 'evidence': dict(EV)}
        elif k == 'size': rb['size'] = {'value': float(val) if '.' in val else int(val), 'status': 'DEFAULT'}
        elif k == 'lines': rb['skip_rules'] = [dict(rb['skip_rules'][0], id='S%d' % i) for i in range(int(val))]
        elif k.startswith('S1.'):
            f = k[3:]; ln = rb['skip_rules'][0]
            if val == 'MISSING': ln.pop(f)
            elif f == 'skip_if' and val == 'ALL': ln['skip_if'] = list(ln['states'])
            elif f in ('states',): ln['states'] = val.split(',')
            else: ln[f] = val
        else:
            raise SystemExit('unknown variant %r' % v)
    return rb, sf, mode


def main():
    rows = list(csv.DictReader(open(os.path.join(HERE, 'EDGES_DECIDE_V1.tsv')), delimiter='\t'))
    settings = [r['setting'] for r in csv.DictReader(open(os.path.join(HERE, 'SETTINGS_DECIDE_V1.tsv')), delimiter='\t')]
    bad = 0; seen = set()
    for r in rows:
        seen |= set(r['targets'].split(';'))
        rb, sf, mode = plant(r['variant'])
        vals = dict(x.split('=', 1) for x in r['values'].split(';') if x)
        try:
            DR.check_rulebook(rb, 'ALARM_X', TOOLS); DR.check_safety(sf)
        except DR.RuleError as e:
            got = 'RULEBOOK_REFUSED'
        else:
            try:
                d = DR.decide(vals, int(r['push_side']), r['day'], rb, sf, mode)
                got = '%s|%s|%s|%s|%s' % (d['action'], d['slot'], d['reason'], d['detail'], d['trade_side'])
                if r['expect'].count('|') > 4:
                    got += '|%s|%s|%s' % (d['entry'], d['exit'], d['size'])
            except DR.RuleError:
                got = 'REFUSED'
        ok = got == r['expect']; bad += not ok
        print('%s %s %s%s' % ('PASS' if ok else 'FAIL', r['case'], r['title'], '' if ok else '  expected %s got %s' % (r['expect'], got)))
    lost = [s for s in settings[:8] if s not in seen]
    if lost:
        bad += 1; print('FAIL settings never targeted: %s' % lost)
    print('T1 DECIDE: %d cases, %d failed%s' % (len(rows), bad, ' PASS' if not bad else ''))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
