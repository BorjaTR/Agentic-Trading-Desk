#!/usr/bin/env python3
"""test_def_template_v4.py: DEF_TEMPLATE_V4.json parses in detect_v2 (and in detect, as the hand check runs it) with the COUNT job's metric
gate, is blank, and every field, op and cmp is explained in DEF_TEMPLATE_V4.md; the doc's rules hold (window, size lines, side and lean,
its code table current byte for byte, the gate's tables, the market op); planted bugs must be refused. Seconds; no lab data is read.

Owner: SCOUT (the alarm kit). New by SCOUT helper K13 for release ALARM_V1_3 (31 Oct 2026); old file test_def_template_v3.py
58001d7542383e64 (beside it), untouched. It imports detect_v2, detect and the engines from this Alarm folder's detection tree
(01_Detection/tree, found by _tools/settings_v1.alarm_root) and sets the gate's tables to the ones inside it. Run it inside an Alarm folder:
  python3 -B test_def_template_v4.py   -> TESTS PASS, PLANTED n of n refused, RULES n of n caught; exit 0 only when all three hold"""
import copy, hashlib, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, 'DEF_TEMPLATE_V4.json')
DOC = os.path.join(HERE, 'DEF_TEMPLATE_V4.md')
COUNT_GATE = (('METRICS_V1', ('team/LAB3/METRICS_V1.tsv',)),                       # JOB_COUNT_V6 line 11, hc_defs_v2 lines 31-34
              ('METRIC_TRAPS', ('team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv',)),
              ('CATALOGS', ('team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv',
                            'team/LAB3/METRICS_HL_ADD_V1.tsv', 'team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv')))
READER_GATE = (('METRICS_V1', ('team/LAB3/METRICS_V1.tsv',)),                      # metric_brief_v2 lines 30-33 (the step-2 reader)
               ('METRIC_TRAPS', ('team/LAB3/LAB4/proposals/metric_traps/METRIC_TRAPS_V3.tsv',)),
               ('CATALOGS', ('team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv')))


def alarm_folder():
    d = HERE
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('REFUSED: run this test inside an Alarm folder (no _tools/settings_v1.py above %s)' % HERE)
        d = os.path.dirname(d)
    sys.path.insert(0, os.path.join(d, '_tools'))
    import settings_v1
    sys.path.pop(0)
    return settings_v1.alarm_root(__file__)


AL = alarm_folder()
F = os.path.join(AL, '01_Detection', 'tree')
sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools', 'idea_to_grade'))
import detect_v2 as DT                                                 # noqa: E402  (detect, edition 2: its engine is alarm_design_v3)
import detect as DT1                                                   # noqa: E402  (DETECT_V1: the hand check's parser, HC line 92)
from labcore import briefs                                             # noqa: E402  (the gate both call)


def gate(tables):
    """point the metric gate at tables inside this Alarm folder; briefs keeps its tables once read, so they are dropped first"""
    for key, rels in tables:
        paths = [os.path.join(F, *r.split('/')) for r in rels]
        missing = [p for p in paths if not os.path.isfile(p)]
        if missing:
            raise SystemExit('REFUSED: MISSING TABLE %s' % missing)
        os.environ[key] = ':'.join(paths)
    briefs._TABLES.clear()


def parse(d, mod=DT):
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'D.json')
        with open(p, 'w') as f:
            json.dump(d, f)
        return mod.load_definition(p)


def keys_of(d):
    out = set(d) | set(d['claim']) | set(d['window']) | set(d['fire']) | set(d['fire']['side'])
    for c in d['conditions'] + d['truth']:
        out |= set(c)
    for s in d['inputs'].values():
        out |= set(s)
    return out


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


# ---------------------------------------------------------------- the doc's rules, as checks (each also runs on planted copies)
def window_rule(d):
    w = d['window']; return w['first'] == '20250901' and w['last'] == '20260430' and w['first'] <= '20250910' and w['last'] < '20260501'


def no_fixed_size_line(d):
    """the blank's numeric sides are 0 only (a sign test): a size test is an own_pct line (F25)"""
    nums = [c[k] for c in d['conditions'] for k in ('lhs', 'rhs') if not isinstance(c[k], str)]
    return all(n == 0 for n in nums)


def side_rules_stated(doc):
    return "fire.side is the event's direction" in doc and 'Never fold the lean into the side' in doc and '`lean` column' in doc


def code_table_current(doc):
    """every row | TAG | `path` | sha16 | names a file of this Alarm folder with that sha16, and every TAG cited in the text is in it"""
    rows = re.findall(r'^\| ([A-Z0-9]+) \| `([^`]+)` \| ([0-9a-f]{16}) \|$', doc, re.M)
    if len(rows) < 10:
        return False, 'only %d table rows' % len(rows)
    bad = [(t, p) for t, p, h in rows if not os.path.isfile(os.path.join(AL, p)) or sha16(os.path.join(AL, p)) != h]
    tags = {t for t, p, h in rows}
    cited = set(re.findall(r'\(([A-Z][A-Z0-9]+) (?:header )?lines? \d', doc)) | set(re.findall(r'; ([A-Z][A-Z0-9]+) lines? \d', doc))
    unknown = sorted(cited - tags - {'R7'})
    return not bad and not unknown, 'stale %s; tags not in the table %s' % (bad, unknown)


def tests():
    ok = []
    d = json.load(open(TEMPLATE)); doc = open(DOC).read()
    gate(COUNT_GATE)
    for name, mod in (('t_parses_in_detect_v2_with_the_count_gate', DT), ('t_parses_in_detect_as_the_hand_check', DT1)):
        try:
            x, info = mod.load_definition(TEMPLATE)
            good = (info['id'] == 'REPLACE_ID' and info['execution_path'] == 'BASE'
                    and {c: b['flag'] for c, b in info['briefs'].items()} == {'A1.S08': 'OK'})
        except Exception as e:
            good = False; print('    %s: %s' % (name, e))
        ok.append((name, good))
    try:
        DT.engine().load_def(TEMPLATE); good = DT.engine().__file__.endswith('alarm_design_v3.py')
    except Exception as e:
        good = False; print('    load_def error: %s' % e)
    ok.append(('t_parses_in_the_engine_alarm_design_v3', good))
    texts = [d['id'], d['family'], d['claim']['one_line'], d['claim']['side_meaning'], d['claim']['note']] + [c['name'] for c in d['conditions']]
    ok.append(('t_blank_every_text_says_replace', all('REPLACE' in t for t in texts)))
    undocumented = sorted(k for k in keys_of(d) if '`%s`' % k not in doc)
    ok.append(('t_every_field_explained', not undocumented))
    if undocumented:
        print('    not in the doc: %s' % undocumented)
    ops = sorted(o for o in DT.OP_FIELDS if '`%s`' % o not in doc)
    ok.append(('t_every_detect_v2_op_explained', not ops))
    ok.append(('t_every_cmp_explained', all('`%s`' % c in doc for c in DT.engine().CMPS)))
    h = d.get('_header', '').lower()
    ok.append(('t_header', 'owner scout' in h and 'def_template_v3.json 1afcc5d78c8d0a06' in h and 'new edition by scout helper k13' in h))
    ok.append(('t_window_first_20250901_last_20260430', window_rule(d)))
    ok.append(('t_no_fixed_size_line', no_fixed_size_line(d)))
    ok.append(('t_side_and_lean_rules_stated', side_rules_stated(doc)))
    good, why = code_table_current(doc)
    ok.append(('t_code_table_current', good))
    if not good:
        print('    %s' % why)
    hl = ('X1.HLFLOWX.S08', 'X1.HLFLOWX.S09')
    gate(COUNT_GATE)
    count_flags = {c: briefs.brief(c)['flag'] for c in hl + ('A1.S08',)}
    gate(READER_GATE)
    reader = {}
    for c in hl + ('A1.S08',):
        try:
            reader[c] = briefs.brief(c)['flag']
        except briefs.MetricRefused:
            reader[c] = 'REFUSED'
    print('    gate flags: COUNT tables %s; the step-2 reader tables %s' % (count_flags, reader))
    ok.append(('t_count_gate_admits_the_owner_cleared_hl_codes', all(count_flags[c] == 'OK' for c in hl + ('A1.S08',))))
    ok.append(('t_reader_tables_do_not', all(reader[c] == 'REFUSED' for c in hl) and reader['A1.S08'] == 'OK'))
    gate(COUNT_GATE)
    m = copy.deepcopy(d); m['inputs']['x'] = {'op': 'market', 'code': 'Z2.S02'}
    try:
        x, info = parse(m)
        good = info['market_codes'] == ['Z2.S02'] and info['raw_codes'] == [] and info['briefs']['Z2.S02']['flag'] == 'OK'
    except Exception as e:
        good = False; print('    market example: %s' % e)
    ok.append(('t_market_op_parses_with_the_count_gate', good))
    return ok


def planted():
    """bugs planted in the template: each must be refused by detect_v2's parser and admission"""
    d = json.load(open(TEMPLATE)); out = []

    def bug(name, f):
        x = copy.deepcopy(d); f(x); out.append((name, x))
    bug('no primary', lambda x: x.pop('primary'))
    bug('grid_s 7', lambda x: x.update(grid_s=7))
    bug('grid_s over a day', lambda x: x.update(grid_s=86405))
    bug('unknown op', lambda x: x['inputs']['move'].update(op='avg'))
    bug('role other', lambda x: x['conditions'][0].update(role='other'))
    bug('no claim condition', lambda x: [c.update(role='shared') for c in x['conditions']])
    bug('cmp ==', lambda x: x['conditions'][0].update(cmp='=='))
    bug('label before t', lambda x: x['truth'][0].update(start_s=-60))
    bug('side sign 2', lambda x: x['fire']['side'].update(sign=2))
    bug('refractory 1.5 s', lambda x: x['fire'].update(refractory_s=1.5))
    bug('unknown code', lambda x: x['inputs']['x'].update(code='NOPE.S01'))
    bug('market without code', lambda x: x['inputs']['x'].pop('code'))
    bug('window day of 7 digits', lambda x: x['window'].update(last='2026043'))
    bug('claim type GUESS', lambda x: x['claim'].update(type='GUESS'))
    bug('lhs names no input', lambda x: x['conditions'][0].update(lhs='nothing'))
    bug('own_pct without q', lambda x: x['inputs']['x_top'].pop('q'))
    bug('own_pct q 101', lambda x: x['inputs']['x_top'].update(q=101))
    bug('an input reads itself', lambda x: x['inputs']['move'].update(of='move'))
    return out


def rules_planted():
    """bugs the doc's rules must catch (the parser accepts each of them): -> [(name, caught)]"""
    d = json.load(open(TEMPLATE)); doc = open(DOC).read(); out = []
    x = copy.deepcopy(d); x['window']['last'] = '20260531'; out.append(('window last 20260531 (V3)', not window_rule(x)))
    x = copy.deepcopy(d); x['window']['first'] = '20250911'; out.append(('window first after 10 Sep', not window_rule(x)))
    x = copy.deepcopy(d); x['conditions'].append({'name': 'REPLACE floor', 'lhs': 'x', 'cmp': '>=', 'rhs': 25000, 'role': 'claim'})
    out.append(('a fixed 25,000 USD size line', not no_fixed_size_line(x)))
    out.append(('the side rule cut', not side_rules_stated(doc.replace("fire.side is the event's direction", 'fire.side'))))
    row = re.search(r'^\| ENG \| `[^`]+` \| ([0-9a-f]{16}) \|$', doc, re.M).group(1)
    out.append(('a stale sha16 in the code table', not code_table_current(doc.replace(row, '0' * 16))[0]))
    out.append(('a cited tag missing from the table', not code_table_current(doc + '\n(ZZ line 1)\n')[0]))
    return out


def main():
    res = tests()
    for n, v in res:
        print('%s %s' % ('PASS' if v else 'FAIL', n))
    fails = [n for n, v in res if not v]
    print('TESTS %s (%d of %d pass)' % ('PASS' if not fails else 'FAIL', len(res) - len(fails), len(res)))
    gate(COUNT_GATE)
    refused = 0; bugs = planted()
    for name, x in bugs:
        try:
            parse(x); r = False; why = 'ACCEPTED'
        except DT.Refusal as e:
            r = True; why = e.code
        refused += r
        print('PLANTED %s: %s (%s)' % (name, 'REFUSED' if r else 'NOT REFUSED', why))
    print('PLANTED %d of %d refused' % (refused, len(bugs)))
    rp = rules_planted()
    for name, c in rp:
        print('RULE %s: %s' % (name, 'CAUGHT' if c else 'MISSED'))
    caught = sum(c for _, c in rp)
    print('RULES %d of %d caught' % (caught, len(rp)))
    sys.exit(0 if not fails and refused == len(bugs) and caught == len(rp) else 1)


if __name__ == '__main__':
    main()
