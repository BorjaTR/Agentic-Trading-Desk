"""tests_decide_v1.py (DECIDE seat, 26 Oct 2026): pure and planted-file tests of decision tool V1, seconds, stdlib only.
  python3 -B tests_decide_v1.py            -> one line per test, exit 1 on any failure
The planted alarm, coins and days below are made up (ALARM_X, AAA, BBB); the generic test refuses any real alarm, coin or date in the code."""
import ast, copy, csv, hashlib, json, os, re, shutil, sys, tempfile
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import decide_rules_v1 as DR
import decide_v1 as DV

EV = {'source': 'loop/REPORT.md', 'sha16': 'abadbc3ed66fd23e', 'cell': 'planted cell'}   # sha16 of the planted file 'planted evidence'
GRADER_PY = "ENTRIES = ('TT', 'RT')\nEXITS = ('X1', 'X2')\n"                              # the planted lab tool's code
def _h(b):
    return hashlib.sha256(b.encode()).hexdigest()[:16]
RELEASE = json.dumps({'files': {'grader.py': _h(GRADER_PY)}})
LT = {'schema': 'DECIDE_LAB_TOOLS_V1',
      'entry': {'grader': {'release': 'R.json', 'sha16': _h(RELEASE), 'ids': ['TT', 'RT']}},
      'exit': {'grader': {'release': 'R.json', 'sha16': _h(RELEASE), 'ids': ['X1', 'X2']}}}
RS = ['UNKNOWN*', 'NO_HISTORY', 'NOT_LISTED', 'OWN_TRIGGER*']                              # the planted libraries' declared reasons
TOOLS = DR.check_lab_tools(LT)


def rulebook(**kw):
    rb = {'schema': 'DECIDE_RULEBOOK_V1', 'alarm_id': 'ALARM_X', 'version': 1,
          'side': {'value': 'FADE', 'status': 'CANDIDATE', 'evidence': dict(EV)},
          'skip_rules': [{'id': 'S1', 'field': 'ctx.SPREAD', 'states': ['TIGHT', 'ABOUT', 'WIDE'], 'reasons': list(RS), 'skip_if': ['TIGHT'],
                          'status': 'CANDIDATE', 'mechanism': 'planted', 'evidence': dict(EV)},
                         {'id': 'S2', 'field': 'prof.SHAPE', 'states': ['UP', 'FLAT', 'DOWN'], 'reasons': list(RS), 'skip_if': ['DOWN'],
                          'status': 'FROZEN', 'mechanism': 'planted', 'evidence': dict(EV)}],
          'entry': {'value': 'grader:RT', 'status': 'CANDIDATE', 'evidence': dict(EV)},
          'exit': {'value': 'UNSET', 'status': 'DEFAULT'}, 'size': {'value': 1, 'status': 'DEFAULT'}}
    rb.update(kw)
    return rb


def safety(**kw):
    s = {'schema': 'DECIDE_SAFETY_V1', 'status': 'EMPTY_PLACEHOLDER', 'set_by': None, 'off_days': [], 'off_states': [], 'kill_limits': {}}
    s.update(kw)
    return s


GOOD = {'ctx.SPREAD': 'ABOUT', 'prof.SHAPE': 'UP', 'pmm.K2': 'YES'}
T = []


def test(f):
    T.append(f)
    return f


def refused(fn, *a):
    try:
        fn(*a)
    except (DR.RuleError, DV.Refused):
        return True
    return False


@test
def take_when_no_line_true():
    d = DR.decide(dict(GOOD), 1, '20000101', DR.check_rulebook(rulebook(), 'ALARM_X', TOOLS), safety(), 'research')
    assert (d['action'], d['slot'], d['reason'], d['trade_side'], d['entry'], d['exit'], d['size']) == ('TAKE', 4, 'NO_SKIP_LINE_TRUE', -1, 'grader:RT', 'UNSET', 1), d


@test
def fade_and_follow_sides():
    rb = rulebook(); assert DR.decide(dict(GOOD), -1, '20000101', rb, safety(), 'research')['trade_side'] == 1
    rb['side']['value'] = 'FOLLOW'; assert DR.decide(dict(GOOD), -1, '20000101', rb, safety(), 'research')['trade_side'] == -1
    rb['side'] = {'value': 'UNSET', 'status': 'DEFAULT'}; assert DR.decide(dict(GOOD), 1, '20000101', rb, safety(), 'research')['trade_side'] == 0


@test
def first_true_line_decides():
    v = dict(GOOD, **{'ctx.SPREAD': 'TIGHT', 'prof.SHAPE': 'DOWN'})
    d = DR.decide(v, 1, '20000101', rulebook(), safety(), 'research')
    assert (d['action'], d['slot'], d['reason'], d['detail']) == ('SKIP', 4, 'SKIP_RULE', 'S1:ctx.SPREAD=TIGHT'), d
    v['ctx.SPREAD'] = 'WIDE'
    assert DR.decide(v, 1, '20000101', rulebook(), safety(), 'research')['detail'] == 'S2:prof.SHAPE=DOWN'


@test
def bad_data_only_for_used_fields():
    v = dict(GOOD, **{'pmm.K2': 'UNKNOWN:HOLE'})
    assert DR.decide(v, 1, '20000101', rulebook(), safety(), 'research')['action'] == 'TAKE'
    for bad in ('UNKNOWN:HOLE', 'NO_HISTORY', DR.NO_CARD_ROW, DR.NO_VALUE, 'NOT_LISTED', 'OWN_TRIGGER|UP'):
        v = dict(GOOD, **{'prof.SHAPE': bad})
        d = DR.decide(v, 1, '20000101', rulebook(), safety(), 'research')
        assert (d['action'], d['slot'], d['reason'], d['detail']) == ('SKIP', 1, 'BAD_DATA', 'prof.SHAPE=%s' % bad), d
    v = dict(GOOD); del v['ctx.SPREAD']
    assert DR.decide(v, 1, '20000101', rulebook(), safety(), 'research')['detail'] == 'ctx.SPREAD=NO_CARD_ROW'
    for undeclared in ('NO_SUCH', 'NOT_HISTORY', 'TIGHTISH'):                              # neither a state nor a declared reason
        assert refused(DR.decide, dict(GOOD, **{'ctx.SPREAD': undeclared}), 1, '20000101', rulebook(), safety(), 'research'), undeclared


@test
def declared_states_not_spelling():
    """review 26 Oct, blocking: a real state that starts with NOT_ or NO_ is a state when the line declares it; nothing is told by spelling"""
    yday = {'id': 'S3', 'field': 'ctx.YDAY', 'states': ['BROKEN_PUSH', 'BROKEN_OTHER', 'NOT_BROKEN_TODAY'], 'reasons': ['UNKNOWN*'],
            'skip_if': ['BROKEN_PUSH'], 'status': 'CANDIDATE', 'mechanism': 'planted', 'evidence': dict(EV)}
    p5b = {'id': 'S4', 'field': 'prof.P5B', 'states': ['OPENERS', 'CLOSERS', 'NO_FORCED_FLOW'], 'reasons': ['NOT_LISTED'],
           'skip_if': ['OPENERS'], 'status': 'CANDIDATE', 'mechanism': 'planted', 'evidence': dict(EV)}
    prt = {'id': 'S5', 'field': 'ctx.PRINTING', 'states': ['PRINTING', 'NOT_PRINTING'], 'reasons': [],
           'skip_if': ['PRINTING'], 'status': 'CANDIDATE', 'mechanism': 'planted', 'evidence': dict(EV)}
    rb = DR.check_rulebook(rulebook(skip_rules=[yday, p5b, prt]), 'ALARM_X', TOOLS)
    v = {'ctx.YDAY': 'NOT_BROKEN_TODAY', 'prof.P5B': 'NO_FORCED_FLOW', 'ctx.PRINTING': 'NOT_PRINTING'}
    assert DR.decide(dict(v), 1, '20000101', rb, safety(), 'research')['action'] == 'TAKE'
    d = DR.decide(dict(v, **{'ctx.YDAY': 'UNKNOWN:HOLE'}), 1, '20000101', rb, safety(), 'research')
    assert (d['reason'], d['detail']) == ('BAD_DATA', 'ctx.YDAY=UNKNOWN:HOLE'), d
    assert refused(DR.decide, dict(v, **{'ctx.PRINTING': 'UNKNOWN:HOLE'}), 1, '20000101', rb, safety(), 'research')   # no reason declared
    assert DR.kind_of('NOT_BROKEN_TODAY', yday['states'], yday['reasons']) == 'STATE'
    assert DR.kind_of('UNKNOWN:EMPTY', yday['states'], yday['reasons']) == 'REASON'
    assert DR.kind_of('NOT_READY', yday['states'], yday['reasons']) == 'UNDECLARED'
    assert DR.kind_of(DR.NO_CARD_ROW, [], []) == 'MISSING_ROW' and DR.kind_of(DR.NO_VALUE, [], []) == 'EMPTY'


@test
def data_gate_before_regime_gate():
    sf = safety(off_days=['20000101'])
    v = dict(GOOD, **{'ctx.SPREAD': 'UNKNOWN:HOLE'})
    assert DR.decide(v, 1, '20000101', rulebook(), sf, 'research')['reason'] == 'BAD_DATA'
    assert DR.decide(dict(GOOD), 1, '20000101', rulebook(), sf, 'research')['reason'] == 'OFF_STATE'
    assert DR.decide(dict(GOOD), 1, '20000102', rulebook(), sf, 'research')['action'] == 'TAKE'


@test
def regime_gate_off_state():
    sf = DR.check_safety(safety(off_states=[{'id': 'O1', 'field': 'ctx.RANGE', 'states': ['LOW', 'MID', 'HIGH'], 'reasons': ['NO_HISTORY'],
                                             'off_if': ['HIGH']}]))
    d = DR.decide(dict(GOOD, **{'ctx.RANGE': 'HIGH', 'ctx.SPREAD': 'TIGHT'}), 1, '20000101', rulebook(), sf, 'research')
    assert (d['slot'], d['reason'], d['detail']) == (2, 'OFF_STATE', 'O1:ctx.RANGE=HIGH'), d
    assert DR.decide(dict(GOOD, **{'ctx.RANGE': 'MID'}), 1, '20000101', rulebook(), sf, 'research')['action'] == 'TAKE'
    assert DR.decide(dict(GOOD, **{'ctx.RANGE': 'NO_HISTORY'}), 1, '20000101', rulebook(), sf, 'research')['reason'] == 'BAD_DATA'


@test
def empty_safety_switches_nothing_off():
    sf = DR.check_safety(safety())
    assert DR.used_fields(rulebook(), sf, 'research') == {'ctx.SPREAD': (('TIGHT', 'ABOUT', 'WIDE'), tuple(RS)),
                                                          'prof.SHAPE': (('UP', 'FLAT', 'DOWN'), tuple(RS))}


@test
def paper_mode_uses_frozen_only():
    v = dict(GOOD, **{'ctx.SPREAD': 'TIGHT'})
    rb = rulebook(); rb['side']['status'] = 'FROZEN'
    assert DR.decide(v, 1, '20000101', rb, safety(), 'paper')['action'] == 'TAKE'      # S1 is CANDIDATE: not in paper
    v['ctx.SPREAD'] = 'UNKNOWN:HOLE'
    assert DR.decide(v, 1, '20000101', rb, safety(), 'paper')['action'] == 'TAKE'      # an inactive line's field never blocks
    rb['side']['status'] = 'CANDIDATE'
    assert DR.decide(dict(GOOD), 1, '20000101', rb, safety(), 'paper')['reason'] == 'SIDE_NOT_ACTIVE'


@test
def failed_lines_never_decide():
    rb = rulebook(); rb['skip_rules'][0]['status'] = 'FAILED'
    assert DR.decide(dict(GOOD, **{'ctx.SPREAD': 'TIGHT'}), 1, '20000101', rb, safety(), 'research')['action'] == 'TAKE'


@test
def push_side_zero_is_bad_data():
    d = DR.decide(dict(GOOD), 0, '20000101', rulebook(), safety(), 'research')
    assert (d['slot'], d['reason'], d['detail']) == (1, 'BAD_DATA', 'push_side=0'), d
    d = DR.decide(dict(GOOD), 0, '20000101', rulebook(), safety(off_days=['20000101']), 'paper')     # slot 1 comes before slots 2 and 3
    assert (d['slot'], d['reason']) == (1, 'BAD_DATA'), d


@test
def rulebook_refusals():
    def bad(mut):
        rb = rulebook(); mut(rb); return refused(DR.check_rulebook, rb, 'ALARM_X', TOOLS)
    assert refused(DR.check_rulebook, rulebook(), 'ALARM_Y', TOOLS)                       # another alarm's rulebook
    assert not refused(DR.check_rulebook, rulebook(alarm_id='*'), 'ALARM_Y', TOOLS)      # the default fits any alarm
    assert bad(lambda r: r.update(extra=1))
    assert bad(lambda r: r['skip_rules'][0].pop('evidence'))
    assert bad(lambda r: r['skip_rules'][0]['evidence'].update(sha16='xyz'))
    assert bad(lambda r: r['skip_rules'][0].update(mechanism=''))
    assert bad(lambda r: r['skip_rules'][0].update(skip_if=['NOPE']))
    assert bad(lambda r: r['skip_rules'][0].update(skip_if=['TIGHT', 'ABOUT', 'WIDE']))
    assert bad(lambda r: r['skip_rules'][0].update(states=['TIGHT', 'UNKNOWN:HOLE']))                    # a state that is a declared reason
    assert bad(lambda r: r['skip_rules'][0].pop('reasons'))                                             # reasons must be declared
    assert bad(lambda r: r['skip_rules'][0].update(reasons=['NO_CARD_ROW']))                            # the tool's own words
    assert bad(lambda r: r['skip_rules'][0].update(reasons=['*']))
    assert bad(lambda r: r['skip_rules'][0].update(reasons='UNKNOWN*'))
    assert not bad(lambda r: r['skip_rules'][0].update(states=['TIGHT', 'NOT_TIGHT'], skip_if=['TIGHT']))   # NOT_ is just letters
    assert bad(lambda r: r['skip_rules'][0].update(field='SPREAD'))
    assert bad(lambda r: r['skip_rules'][1].update(id='S1'))
    assert bad(lambda r: r['skip_rules'][0].update(status='DEFAULT'))
    assert bad(lambda r: r['side'].update(value='BOTH'))
    assert bad(lambda r: r['side'].pop('evidence'))
    assert bad(lambda r: r['entry'].update(value='grader:RR'))                            # not a listed lab tool id
    assert bad(lambda r: r['entry'].update(value='RT'))
    assert bad(lambda r: r['exit'].update(value='made_up:X1'))
    assert bad(lambda r: r['size'].update(value=0))
    assert bad(lambda r: r['size'].update(value=True))
    assert bad(lambda r: r.update(schema='OTHER'))
    four = [dict(rulebook()['skip_rules'][0], id='S%d' % i) for i in range(4)]
    assert bad(lambda r: r.update(skip_rules=four))
    three = four[:3] + [dict(four[3], status='FAILED')]
    assert not bad(lambda r: r.update(skip_rules=three))                                    # FAILED lines do not count


@test
def lab_tools_refusals():
    def bad(mut):
        lt = copy.deepcopy(LT); mut(lt); return refused(DR.check_lab_tools, lt)
    assert bad(lambda l: l['entry']['grader'].update(sha16='short'))
    assert bad(lambda l: l['entry']['grader'].update(release=''))
    assert bad(lambda l: l['exit']['grader'].update(ids=[]))
    assert bad(lambda l: l.update(exit={}))
    assert bad(lambda l: l['entry'].update({'a:b': l['entry']['grader']}))
    assert TOOLS == {'entry': {'grader:TT', 'grader:RT'}, 'exit': {'grader:X1', 'grader:X2'}}


@test
def safety_refusals():
    assert refused(DR.check_safety, safety(off_days=['2000-01-01']))
    assert refused(DR.check_safety, safety(extra=1))
    assert refused(DR.check_safety, safety(off_states=[{'id': 'O1', 'field': 'ctx.R', 'states': ['A', 'B'], 'reasons': [], 'off_if': ['A', 'B']}]))
    assert refused(DR.check_safety, safety(off_states=[{'id': 'O1', 'field': 'ctx.R', 'states': ['A', 'B'], 'off_if': ['A']}]))   # no reasons
    assert refused(DR.used_fields, rulebook(), safety(off_states=[{'id': 'O1', 'field': 'ctx.SPREAD', 'states': ['TIGHT', 'WIDE'],
                                                                     'reasons': list(RS), 'off_if': ['WIDE']}]), 'research')
    assert refused(DR.used_fields, rulebook(), safety(off_states=[{'id': 'O1', 'field': 'ctx.SPREAD', 'states': ['TIGHT', 'ABOUT', 'WIDE'],
                                                                     'reasons': ['NO_HISTORY'], 'off_if': ['WIDE']}]), 'research')


@test
def reason_families():
    assert DR.matches('UNKNOWN:HOLE', ['UNKNOWN*']) and DR.matches('OWN_TRIGGER|UP', ['OWN_TRIGGER*'])
    assert DR.matches('NO_HISTORY', ['NO_HISTORY']) and not DR.matches('NO_HISTORY_X', ['NO_HISTORY'])
    assert not DR.matches('NOT_BROKEN_TODAY', ['NOT_READY*', 'NO_HISTORY*']) and not DR.matches('TIGHT', [])


# ---- planted files: the command end to end ----
def plant(d, ctx_rows, prof_rows, pmm_rows, uni_rows, rb=None, sf=None, src_rows=None, status=True):
    """planted files in the real schemas: a source event list, a universe whose header names it, the three libraries' cards, one release
    record per library naming its files' sha16 (the profile's through a receipt), the evidence, the lab tool release and its code"""
    def tsv(name, head, rows, top=''):
        p = os.path.join(d, name)
        with open(p, 'w', newline='') as f:
            f.write(top)
            w = csv.writer(f, delimiter='\t', lineterminator='\n'); w.writerow(head); [w.writerow(r) for r in rows]
        return p
    def release(name, text):
        p = os.path.join(d, name); open(p, 'w').write(text); return _h(text)
    P = {'root': d}
    if src_rows is None:
        src_rows = [[r[1], r[2], r[3], r[2] - 30, 'TRIG_X', 'e%d' % i] for i, r in enumerate(uni_rows) if r[0] == 'ALARM_X']
    P['src'] = tsv('SRC.tsv', ['coin', 't', 'side', 'onset_t', 'trigger', 'event_id'], src_rows)
    P['universe'] = tsv('U.tsv', ['alarm_id', 'coin', 't', 'side', 'parent_id', 'cluster_id', 'weight', 'cluster_size', 'flag'], uni_rows,
                        top='# planted universe\n# source ALARM_X=%s %s\n' % (P['src'], DV.sha16(P['src'])))
    if status:
        ctx_rows = [r[:5] + [r[5] if len(r) > 5 else 'x', r[6] if len(r) > 6 else 'CANDIDATE'] for r in ctx_rows]
        P['ctx'] = tsv('CTX.tsv', ['registry_id', 'coin', 't', 'side', 'SPREAD', 'OTHER', 'SPREAD__status'], ctx_rows)
    else:
        P['ctx'] = tsv('CTX.tsv', ['registry_id', 'coin', 't', 'side', 'SPREAD', 'OTHER'], [r[:6] for r in ctx_rows])
    P['prof'] = tsv('PROF_a.tsv', ['registry_id', 'coin', 'emission_t', 'side', 'SHAPE'], prof_rows[:1])
    P['prof2'] = tsv('PROF_b.tsv', ['registry_id', 'coin', 'emission_t', 'side', 'SHAPE'], prof_rows[1:])
    P['pmm'] = tsv('PMM.tsv', ['registry_id', 'coin', 'emission_t', 'side', 'K2'], pmm_rows)
    rec = 'planted receipt: %s %s' % (DV.sha16(P['prof']), DV.sha16(P['prof2']))
    rec_sha = release('PROF_RECEIPT.json', rec)
    adm = {'schema': 'DECIDE_ADMITTED_V1', 'libraries': {
        'universe': {'release': 'UREL.json', 'sha16': release('UREL.json', 'planted universe release %s' % DV.sha16(P['universe'])), 'receipts': []},
        'ctx.': {'release': 'CREL.json', 'sha16': release('CREL.json', 'planted context release %s' % DV.sha16(P['ctx'])), 'receipts': []},
        'prof.': {'release': 'PREL.json', 'sha16': release('PREL.json', 'planted profile release, receipt %s' % rec_sha),
                  'receipts': [{'path': os.path.join(d, 'PROF_RECEIPT.json'), 'sha16': rec_sha}]},
        'pmm.': {'release': 'MREL.json', 'sha16': release('MREL.json', 'planted pre-move release %s' % DV.sha16(P['pmm'])), 'receipts': []}},
        'field_status': {'ctx.': {'suffix': '__status', 'admitted': ['CANDIDATE']}}}
    os.makedirs(os.path.join(d, 'loop'), exist_ok=True)
    with open(os.path.join(d, 'loop', 'REPORT.md'), 'w') as f:
        f.write('planted evidence')
    with open(os.path.join(d, 'R.json'), 'w') as f:
        f.write(RELEASE)
    with open(os.path.join(d, 'grader.py'), 'w') as f:
        f.write(GRADER_PY)
    for k, obj in (('rb', rb or rulebook()), ('sf', sf or safety()), ('lt', LT), ('adm', adm)):
        P[k] = os.path.join(d, k + '.json'); json.dump(obj, open(P[k], 'w'))
    return P


def argv(P, out, **kw):
    a = ['--universe', P['universe'], '--alarm-id', 'ALARM_X', '--first', '20000101', '--last', '20000131', '--research-window',
         '20000101:20000131', '--rulebook', P['rb'], '--safety', P['sf'], '--lab-tools', P['lt'], '--admitted', P['adm'], '--mode', 'research',
         '--ctx-cards', P['ctx'], '--prof-cards', P['prof'] + ',' + P['prof2'], '--pmm-cards', P['pmm'], '--root', P['root'], '--out', out]
    for k, v in kw.items():
        i = a.index('--' + k.replace('_', '-')); a[i + 1] = v
    return a


T0 = 946684800    # 2000-01-01 00:00:00 UTC, planted
UNI = [['ALARM_X', 'AAA', T0 + 60, 1, 'p1', 'c1', 0.5, 2, ''], ['ALARM_X', 'BBB', T0 + 120, -1, 'p2', 'c1', 0.5, 2, ''],
       ['ALARM_X', 'AAA', T0 + 9000, -1, 'p3', 'c2', 1.0, 1, ''], ['ALARM_Y', 'AAA', T0 + 60, 1, 'q', 'q', 1, 1, '']]
CTX = [['ALARM_X', 'AAA', T0 + 60, 1, 'TIGHT'], ['ALARM_X', 'BBB', T0 + 120, -1, 'ABOUT'], ['ALARM_X', 'AAA', T0 + 9000, -1, 'UNKNOWN:HOLE'],
       ['ALARM_Y', 'AAA', T0 + 60, 1, 'UNDECLARED_WORD_IGNORED']]
PROF = [['ALARM_X', 'AAA', T0 + 60, 1, 'UP'], ['ALARM_X', 'BBB', T0 + 120, -1, 'FLAT'], ['ALARM_X', 'AAA', T0 + 9000, -1, 'UP']]
PMM = [['ALARM_X', 'AAA', T0 + 60, 1, 'YES']]


def planted(d, **kw):
    os.makedirs(d, exist_ok=True)
    return plant(d, kw.get('ctx', CTX), kw.get('prof', PROF), kw.get('pmm', PMM), kw.get('uni', UNI), kw.get('rb'), kw.get('sf'),
                 kw.get('src'), kw.get('status', True))


def read_out(out, name):
    with open(os.path.join(out, name)) as f:
        return list(csv.DictReader(f, delimiter='\t'))


def code_of(a):
    """run the command as the shell would and return the refusal code (or 'OK'); a traceback fails the test"""
    import io, contextlib
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            rc = DV.main(a)
        except SystemExit as e:
            rc = e.code
    e = err.getvalue()
    assert 'Traceback' not in e, e
    if rc == 0:
        return 'OK'
    assert rc == 2 and (e.startswith('REFUSED ') or e.startswith('usage:')), (rc, e)
    return e.split()[1].rstrip(':') if e.startswith('REFUSED ') else 'USAGE'


def io_err(a):
    import io, contextlib
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        try:
            DV.main(a)
        except SystemExit:
            pass
    return err.getvalue()


@test
def planted_run_end_to_end():
    d = tempfile.mkdtemp()
    try:
        P = planted(d); out = os.path.join(d, 'out')
        assert code_of(argv(P, out)) == 'OK'
        rows = read_out(out, 'DECISIONS.tsv')
        for n, head in (('DECISIONS.tsv', DV.DECISIONS_HEAD), ('TAKE_EVENTS.tsv', DV.EVENTS_HEAD), ('SKIP_EVENTS.tsv', DV.EVENTS_HEAD),
                        ('VALUE_COUNTS.tsv', DV.VALUE_COUNTS_HEAD)):
            assert open(os.path.join(out, n)).readline().rstrip('\n').split('\t') == head, n     # fixed headers (pipeline contract)
        assert DV.DECISIONS_HEAD[:4] == DV.EVENTS_HEAD[:4] == ['alarm_id', 'coin', 't', 'side']
        assert rows[0]['used_values'] == 'ctx.SPREAD=TIGHT;prof.SHAPE=UP' and rows[0]['side'] == '1'
        assert [(r['coin'], r['t'], r['action'], r['reason'], r['detail']) for r in rows] == [
            ('AAA', str(T0 + 60), 'SKIP', 'SKIP_RULE', 'S1:ctx.SPREAD=TIGHT'),
            ('BBB', str(T0 + 120), 'TAKE', 'NO_SKIP_LINE_TRUE', ''),
            ('AAA', str(T0 + 9000), 'SKIP', 'BAD_DATA', 'ctx.SPREAD=UNKNOWN:HOLE')], rows
        assert rows[1]['trade_side'] == '1' and rows[1]['card_pmm'] == 'MISSING' and rows[0]['card_pmm'] == 'FOUND'
        take = read_out(out, 'TAKE_EVENTS.tsv'); skip = read_out(out, 'SKIP_EVENTS.tsv')
        # kit row 10: the event identity is copied from the source list unchanged (onset_t, trigger, event_id)
        assert [(r['alarm_id'], r['coin'], r['t'], r['side'], r['onset_t'], r['trigger'], r['event_id']) for r in take] == [
            ('ALARM_X', 'BBB', str(T0 + 120), '-1', str(T0 + 90), 'TRIG_X', 'e1')], take
        assert len(skip) == 2
        run = json.load(open(os.path.join(out, 'RUN.json')))
        assert run['fires'] == 3 and run['tally']['TAKE|4|NO_SKIP_LINE_TRUE'] == {'fires': 1, 'weight': 0.5}
        assert run['missing_card_rows'] == {'ctx.': 0, 'prof.': 0, 'pmm.': 2}
        assert set(run['timing_s']) == {'admission', 'read', 'compute', 'write'}
        kinds = {(r['field'], r['value']): r['kind'] for r in read_out(out, 'VALUE_COUNTS.tsv')}
        assert kinds[('ctx.SPREAD', 'UNKNOWN:HOLE')] == 'REASON' and kinds[('ctx.SPREAD', 'TIGHT')] == 'STATE'
        assert code_of(argv(P, out)) == 'OUT_EXISTS'
        out2 = os.path.join(d, 'out2'); assert code_of(argv(P, out2)) == 'OK'
        for n in DV.OUTPUTS:
            assert DV.sha16(os.path.join(out, n)) == DV.sha16(os.path.join(out2, n)), n  # same bytes
    finally:
        shutil.rmtree(d)


@test
def planted_refusals_with_codes():
    """kit rows 1, 2, 7, 10 and 11: every bad input refuses with its code, exit 2, no traceback, nothing written"""
    d = tempfile.mkdtemp()
    try:
        P = planted(os.path.join(d, 'a'))
        cases = [('BAD_DATE', P, {'last': '20000132'}), ('BAD_DATE', P, {'research_window': '20000101:20001301'}),
                 ('OUTSIDE_WINDOW', P, {'first': '20000115', 'last': '20000110'}), ('OUTSIDE_WINDOW', P, {'last': '20000201'}),
                 ('RULEBOOK_INVALID', P, {'alarm_id': 'ALARM_Z'}), ('BAD_INPUT_FILE', P, {'ctx_cards': os.path.join(d, 'nope.tsv')})]
        P1 = dict(P, rb=os.path.join(d, 'rb_any.json')); json.dump(rulebook(alarm_id='*'), open(P1['rb'], 'w'))
        cases.append(('NO_SOURCE_LIST', P1, {'alarm_id': 'ALARM_Z'}))
        def variant(name, **kw):
            return planted(os.path.join(d, name), **kw)
        cases.append(('UNDECLARED_VALUE', variant('b', ctx=[['ALARM_X', 'AAA', T0 + 60, 1, 'TIGHTISH']] + CTX[1:3]), {}))
        cases.append(('DUPLICATE_FIRE', variant('c', prof=[PROF[0], PROF[0]] + PROF[1:]), {}))
        rb = rulebook(); rb['skip_rules'][0]['field'] = 'ctx.NOT_A_COLUMN'
        cases.append(('FIELD_NOT_IN_CARDS', variant('e', rb=rb), {}))
        P5 = variant('f'); open(os.path.join(P5['root'], 'loop', 'REPORT.md'), 'w').write('changed after the rulebook was written')
        cases.append(('PIN_MISMATCH', P5, {}))                                                         # evidence changed
        P6 = variant('g'); os.remove(os.path.join(P6['root'], 'R.json'))
        cases.append(('PIN_MISMATCH', P6, {}))                                                         # lab tool release missing
        P7 = variant('h'); lt = copy.deepcopy(LT); lt['exit']['grader']['ids'] = ['X1', 'X3']; json.dump(lt, open(P7['lt'], 'w'))
        rb = rulebook(); rb['exit'] = {'value': 'grader:X3', 'status': 'CANDIDATE', 'evidence': dict(EV)}; json.dump(rb, open(P7['rb'], 'w'))
        cases.append(('LAB_ID_UNKNOWN', P7, {}))
        P8 = variant('i'); open(os.path.join(P8['root'], 'grader.py'), 'a').write('# changed\n')
        cases.append(('PIN_MISMATCH', P8, {}))                                                         # release code changed
        rb = rulebook(); rb['skip_rules'][0]['states'] = ['TIGHT', 'WIDE']; rb['skip_rules'][0]['reasons'] = ['UNKNOWN*']
        cases.append(('UNDECLARED_VALUE', variant('j', rb=rb), {}))                                   # ABOUT undeclared: refused, not BAD_DATA
        cases.append(('SELECTION_NOT_COVERED', variant('k', ctx=CTX[:2]), {}))                        # a used field with no card row
        cases.append(('CARD_MALFORMED', variant('l', ctx=CTX[:2] + [['ALARM_X', 'AAA', T0 + 9000, -1, '']]), {}))
        cases.append(('FIELD_NOT_ADMITTED', variant('m', ctx=CTX[:2] + [['ALARM_X', 'AAA', T0 + 9000, -1, 'WIDE', 'x', 'NOT_PROVEN']]), {}))
        cases.append(('FIELD_NOT_ADMITTED', variant('n', status=False), {}))                          # the declared status column is absent
        Pb = variant('v'); open(os.path.join(Pb['root'], 'CREL.json'), 'a').write(' edited')         # a release record changed
        cases.append(('PIN_MISMATCH', Pb, {}))
        Pc = variant('w'); open(os.path.join(Pc['root'], 'PROF_RECEIPT.json'), 'a').write(' edited')  # a receipt changed
        cases.append(('PIN_MISMATCH', Pc, {}))
        P9 = variant('o'); open(P9['ctx'], 'a').write('ALARM_Y\tBBB\t1\t1\tWIDE\tx\tCANDIDATE\n')     # changed after its release
        cases.append(('NOT_ADMITTED', P9, {}))
        Pa = variant('p'); open(Pa['src'], 'a').write('ZZZ\t1\t1\t\tT\tz\n')                            # source list not at its named sha16
        cases.append(('PIN_MISMATCH', Pa, {}))
        cases.append(('SOURCE_MISMATCH', variant('q', src=[['AAA', T0 + 60, 1, T0, 'TRIG_X', 'e0']]), {}))
        bad_t = [r[:] for r in UNI]; bad_t[0][2] = '%d.5' % (T0 + 60)
        cases.append(('NOT_WHOLE', variant('r', uni=bad_t, src=[]), {}))
        bad_s = [r[:] for r in UNI]; bad_s[0][3] = '1.5'
        cases.append(('NOT_WHOLE', variant('s', uni=bad_s, src=[]), {}))
        bad_w = [r[:] for r in UNI]; bad_w[0][6] = 'inf'
        cases.append(('BAD_WEIGHT', variant('t', uni=bad_w), {}))
        bad_side = [r[:] for r in UNI]; bad_side[0][3] = 2
        cases.append(('BAD_SIDE', variant('u', uni=bad_side, src=[]), {}))
        for n, (want, PP, kw) in enumerate(cases):
            out = os.path.join(d, 'o%d' % n)
            got = code_of(argv(PP, out, **kw))
            assert got == want, (n, want, got)
            assert not os.path.exists(out), (n, 'an output folder was written')
        Pn = variant('x', status=False)                       # refused at the header, before any row is read, and says so
        msg = io_err(argv(Pn, os.path.join(d, 'ox')))
        assert msg.startswith('REFUSED FIELD_NOT_ADMITTED') and 'has no status column' in msg, msg
    finally:
        shutil.rmtree(d)


@test
def finished_run_is_tamper_evident():
    """kit rows 3 and 11: verify_run(), the one check every consumer calls, refuses an edited, extra, missing or uncommitted file"""
    d = tempfile.mkdtemp()
    try:
        P = planted(d); out = os.path.join(d, 'out')
        assert code_of(argv(P, out)) == 'OK' and DV.verify_run(out)['fires'] == 3
        assert code_of(['--verify', out]) == 'OK'
        def broken(name, how):
            c = os.path.join(d, name); shutil.copytree(out, c); how(c); return c
        for name, how, want in (
                ('edit', lambda c: open(os.path.join(c, 'TAKE_EVENTS.tsv'), 'a').write('ALARM_X\tCCC\t1\t1\t\t\t\n'), 'RUN_CHANGED_AFTER_COMMIT'),
                ('stray', lambda c: open(os.path.join(c, 'EXTRA.tsv'), 'w').write('x'), 'RUN_CHANGED_AFTER_COMMIT'),
                ('gone', lambda c: os.remove(os.path.join(c, 'SKIP_EVENTS.tsv')), 'RUN_CHANGED_AFTER_COMMIT'),
                ('nocommit', lambda c: os.remove(os.path.join(c, 'RUN.json')), 'RUN_NOT_COMMITTED')):
            assert code_of(['--verify', broken(name, how)]) == want, name
    finally:
        shutil.rmtree(d)


@test
def input_changed_during_the_run_refuses():
    """kit row 4: a configured file changed after admission refuses the run; the unchanged case still commits"""
    d = tempfile.mkdtemp()
    try:
        P = planted(d)
        real = DV.read_cards
        def sneaky(paths, prefix, alarm_id):
            if prefix == 'pmm.':
                open(P['rb'], 'a').write(' ')                          # the rulebook changes while the cards are read
            return real(paths, prefix, alarm_id)
        DV.read_cards = sneaky
        try:
            assert code_of(argv(P, os.path.join(d, 'o1'))) == 'INPUT_CHANGED'
        finally:
            DV.read_cards = real
        assert not os.path.exists(os.path.join(d, 'o1'))
        assert code_of(argv(P, os.path.join(d, 'o2'))) == 'OK'
    finally:
        shutil.rmtree(d)


@test
def selection_and_source_list_preflight():
    """kit rows 7 and 10: an empty selection, a source list with the wrong columns but the right sha16, an event twice in the source
    list, a changed trigger or onset (the source list then differs from the sha16 the universe names); blank metadata passes unchanged"""
    d = tempfile.mkdtemp()
    try:
        P = planted(os.path.join(d, 'a'))
        assert code_of(argv(P, os.path.join(d, 'o1'), first='20000120', last='20000131')) == 'NO_FIRES'
        def resource(P, lines):
            open(P['src'], 'w').write(''.join(l + '\n' for l in lines))
            u = open(P['universe']).read().split('\n'); u[1] = '# source ALARM_X=%s %s' % (P['src'], DV.sha16(P['src']))
            open(P['universe'], 'w').write('\n'.join(u))
            rec = json.load(open(P['adm'])); rp = os.path.join(P['root'], 'UREL.json')
            open(rp, 'w').write('planted universe release %s' % DV.sha16(P['universe'])); rec['libraries']['universe']['sha16'] = DV.sha16(rp)
            json.dump(rec, open(P['adm'], 'w'))
            return P
        rows = ['AAA\t%d\t1\t%d\tTRIG_X\te0' % (T0 + 60, T0 + 30), 'BBB\t%d\t-1\t%d\tTRIG_X\te1' % (T0 + 120, T0 + 90),
                'AAA\t%d\t-1\t%d\tTRIG_X\te2' % (T0 + 9000, T0 + 8970)]
        Pb = resource(planted(os.path.join(d, 'b')), ['coin\tt\tside\tonset_t\tevent_id'] + [r.replace('TRIG_X\t', '') for r in rows])
        assert code_of(argv(Pb, os.path.join(d, 'o2'))) == 'MISSING_COLUMNS'
        Pc = resource(planted(os.path.join(d, 'c')), ['coin\tt\tside\tonset_t\ttrigger\tevent_id'] + rows + rows[1:2])
        assert code_of(argv(Pc, os.path.join(d, 'o3'))) == 'DUPLICATE_FIRE'
        for name, edit in (('e', lambda t: t.replace('TRIG_X\te1', 'OTHER\te1')), ('f', lambda t: t.replace('%d\tTRIG_X\te1' % (T0 + 90), '%d\tTRIG_X\te1' % (T0 - 480)))):
            Pe = planted(os.path.join(d, name)); open(Pe['src'], 'w').write(edit(open(Pe['src']).read()))
            assert code_of(argv(Pe, os.path.join(d, 'o' + name))) == 'PIN_MISMATCH', name
        Pg = resource(planted(os.path.join(d, 'g')), ['coin\tt\tside\tonset_t\ttrigger\tevent_id', rows[0], 'BBB\t%d\t-1\t\t\t' % (T0 + 120), rows[2]])
        out = os.path.join(d, 'o4'); assert code_of(argv(Pg, out)) == 'OK'
        take = read_out(out, 'TAKE_EVENTS.tsv')
        assert [(r['onset_t'], r['trigger'], r['event_id']) for r in take] == [('', '', '')], take    # blank stays blank, never filled in
    finally:
        shutil.rmtree(d)


@test
def other_alarms_rows_are_not_read():
    d = tempfile.mkdtemp()
    try:
        ctx = CTX[:3] + [['ALARM_Y', 'AAA', T0 + 60, 1, 'ABOUT'], ['ALARM_Y', 'AAA', T0 + 60, 1, 'WIDE']]
        P = planted(d, ctx=ctx)
        assert code_of(argv(P, os.path.join(d, 'out'))) == 'OK'     # a repeat inside another alarm's rows is not this run's business
    finally:
        shutil.rmtree(d)


@test
def planted_coin_filter():
    d = tempfile.mkdtemp()
    try:
        P = planted(d); out = os.path.join(d, 'out')
        assert code_of(argv(P, out) + ['--coins', 'bbb']) == 'OK'
        assert [r['coin'] for r in read_out(out, 'DECISIONS.tsv')] == ['BBB']
    finally:
        shutil.rmtree(d)


FORENSICS = os.environ.get('DECIDE_FORENSICS') or os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))   # tools/decide_v1 -> the root


def real_names():
    """every coin of the frozen universe, and every alarm id, short name, card and definition name of the registry (read, never typed)"""
    lib = os.path.join(FORENSICS, 'team', 'RESEARCH', 'LIBRARY')
    with open(os.path.join(lib, 'UNIVERSE_ALARMS_V1.tsv')) as f:
        uni = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    with open(os.path.join(lib, 'alarm_library', 'ALARM_REGISTRY_V1.tsv')) as f:
        reg = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    coins = {r['coin'].strip().upper() for r in uni}
    words = set()
    for r in reg:
        rid = r['registry_id']; words.add(rid)
        words.add(re.sub(r'^ALM_|_V\d+$', '', rid))                                            # the short name (M, S3W, ...)
        for col in ('card', 'definition'):
            b = os.path.basename(r.get(col) or '')
            b = re.sub(r'\.(md|json)$', '', b); words.add(b); words.add(re.sub(r'_(CARD|DEF)_V\d+$', '', b))
    words.discard('')
    assert len(coins) >= 10 and len(reg) >= 6, (len(coins), len(reg))
    return coins, words


def offences(src, coins, words):
    """every string or number constant in the source that names a real alarm, coin or date"""
    long_words = [w for w in words if len(w) >= 4]; out = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if ('ALM_' in s or re.search(r'(?<!\d)(19|20|21)\d\d(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(?!\d)', s)
                    or re.search(r'\b(19|20|21)\d\d-\d\d-\d\d\b', s) or s.strip() in words or s.strip().upper() in coins
                    or [w for w in long_words if re.search(r'(?<![A-Za-z0-9])%s(?![A-Za-z0-9])' % re.escape(w), s)]):
                out.append(s)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            if 19000101 <= node.value <= 21001231 or 1.0e9 < node.value < 2.2e9:
                out.append(node.value)
        if isinstance(node, (ast.Assign, ast.AnnAssign)):                 # kit row 14: a fixed first or last day under any spelling
            names = [t.id for t in (node.targets if isinstance(node, ast.Assign) else [node.target]) if isinstance(t, ast.Name)]
            if [n for n in names if re.search(r'(FIRST|LAST|START|END|FROM|UNTIL)(_DAY|_DATE|_T)?$', n.upper())] and node.value is not None \
                    and isinstance(node.value, ast.Constant) and node.value.value not in (None, ''):
                out.append(names)
        if isinstance(node, ast.Call):                                    # kit row 14: a date built from constants
            f = node.func; fn = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else '')
            if fn in ('datetime', 'date', 'strptime', 'fromisoformat') and node.args and all(isinstance(x, ast.Constant) for x in node.args):
                out.append(fn)
    return out


@test
def generic_code_no_alarm_coin_or_date():
    """no alarm id, short name, trigger or card name, real coin, date or unix time in the code. Coins come from the frozen universe and the
    alarm names from the registry (so a new coin or alarm is covered); dates are refused as text (YYYYMMDD, YYYY-MM-DD) and as numbers
    (19000101-21001231 and the unix seconds 1.0e9-2.2e9). The tests' planted names are made up."""
    coins, words = real_names()
    for name in ('decide_rules_v1.py', 'decide_v1.py'):
        bad = offences(open(os.path.join(HERE, name)).read(), coins, words)
        assert not bad, (name, bad)


@test
def generic_test_catches_the_review_probes():
    """the probes the review slipped past the old test are caught now, and so are the two it already caught"""
    coins, words = real_names()
    assert 'LIT' in coins and 'IDEA2_M' in words and 'M' in words
    for probe in ('FIRST_DAY = 20250910', "COIN = 'LIT'", "ALARM = 'IDEA2_M'", "X = '2025-09-10'", "Y = 'ALM_' + 'M_V1'",
                  "Z = 'M'", "T = 1757635680", "STUDY_FIRST = 7", "window_end = 'x'", "d = datetime.date(2025, 9, 1)",
                  "d = datetime.strptime('a', '%Y')", "LAST: int = 3"):
        assert offences(probe, coins, words), probe
    assert not offences("A = 'TAKE'\nB = 3\nC = 'ctx.'\nFIRST = None\nd = datetime.strptime(x, '%Y%m%d')", coins, words)


@test
def edges_file_every_case_exact():
    """T1: every case of EDGES_DECIDE_V1.tsv through the rules, exact (edges_decide_v1.py)"""
    import io, contextlib, edges_decide_v1 as E
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = E.main()
    assert rc == 0 and 'PASS' in buf.getvalue().splitlines()[-1], buf.getvalue()[-800:]


def main():
    bad = 0
    for f in T:
        try:
            f(); print('PASS', f.__name__)
        except Exception as e:
            bad += 1; print('FAIL', f.__name__, repr(e)[:300])
    print('%d/%d passed' % (len(T) - bad, len(T)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
