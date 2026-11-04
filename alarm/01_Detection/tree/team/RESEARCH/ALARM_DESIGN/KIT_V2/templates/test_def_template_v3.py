#!/usr/bin/env python3
"""test_def_template_v3.py: DEF_TEMPLATE_V3.json parses in detect with the COUNT job's metric gate, is blank, and every field and op is
explained in DEF_TEMPLATE_V3.md; planted bugs in the template must be refused. Seconds; no lab data is read.

Owner: SCOUT (the alarm kit). New by SCOUT for the clean release (K7, 30 Oct 2026); DEF_TEMPLATE_V2 had no test. It imports detect and
the engine from this Alarm folder's detection tree (01_Detection/tree, found by _tools/settings_v1.alarm_root) and sets the gate's tables
to the ones inside it (the COUNT job's). It runs no old edition. Run it from inside an Alarm folder:
  python3 -B test_def_template_v3.py      -> TESTS PASS, then PLANTED n of n refused; exit 0 only when both hold"""
import copy, json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, 'DEF_TEMPLATE_V3.json')
DOC = os.path.join(HERE, 'DEF_TEMPLATE_V3.md')
GATE = (('METRICS_V1', ('team/LAB3/METRICS_V1.tsv',)),
        ('METRIC_TRAPS', ('team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv',)),
        ('CATALOGS', ('team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv',
                      'team/LAB3/METRICS_HL_ADD_V1.tsv', 'team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv')))


def detection_tree():
    d = HERE
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise SystemExit('REFUSED: run this test inside an Alarm folder (no _tools/settings_v1.py above %s)' % HERE)
        d = os.path.dirname(d)
    sys.path.insert(0, os.path.join(d, '_tools'))
    import settings_v1
    sys.path.pop(0)
    return os.path.join(settings_v1.alarm_root(__file__), '01_Detection', 'tree')


F = detection_tree()
for key, rels in GATE:
    paths = [os.path.join(F, *r.split('/')) for r in rels]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        raise SystemExit('REFUSED: MISSING TABLE %s' % missing)
    os.environ[key] = ':'.join(paths)
sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools', 'idea_to_grade'))
import detect as DT                                                    # noqa: E402  (the released detector, DETECT_V1)


def parse(d):
    with tempfile.TemporaryDirectory() as tmp:
        p = os.path.join(tmp, 'D.json')
        with open(p, 'w') as f:
            json.dump(d, f)
        return DT.load_definition(p)


def keys_of(d):
    out = set(d) | set(d['claim']) | set(d['window']) | set(d['fire']) | set(d['fire']['side'])
    for c in d['conditions'] + d['truth']:
        out |= set(c)
    for s in d['inputs'].values():
        out |= set(s)
    return out


def tests():
    ok = []
    d = json.load(open(TEMPLATE)); doc = open(DOC).read()
    try:
        x, info = DT.load_definition(TEMPLATE)
        good = (info['id'] == 'REPLACE_ID' and info['execution_path'] == 'BASE'
                and {c: b['flag'] for c, b in info['briefs'].items()} == {'A1.S08': 'OK'})
    except Exception as e:
        good = False; print('    parse error: %s' % e)
    ok.append(('t_parses_in_detect_with_the_count_gate', good))
    try:
        DT.engine().load_def(TEMPLATE); good = True
    except Exception as e:
        good = False; print('    load_def error: %s' % e)
    ok.append(('t_parses_in_the_engine', good))
    texts = [d['id'], d['family'], d['claim']['one_line'], d['claim']['side_meaning'], d['claim']['note']] + [c['name'] for c in d['conditions']]
    ok.append(('t_blank_every_text_says_replace', all('REPLACE' in t for t in texts)))
    undocumented = sorted(k for k in keys_of(d) if '`%s`' % k not in doc)
    ok.append(('t_every_field_explained', not undocumented))
    if undocumented:
        print('    not in the doc: %s' % undocumented)
    ops = sorted(o for o in DT.OP_FIELDS if '`%s`' % o not in doc)
    ok.append(('t_every_detect_op_explained', not ops))
    if ops:
        print('    ops not in the doc: %s' % ops)
    ok.append(('t_every_cmp_explained', all('`%s`' % c in doc for c in DT.engine().CMPS)))
    h = d.get('_header', '').lower()
    ok.append(('t_header', 'owner scout' in h and 'def_template_v2.json 3a0b5e15a769c257' in h and 'new edition by scout for the clean release' in h))
    return ok


def planted():
    """bugs planted in the template: each must be refused by detect's parser"""
    d = json.load(open(TEMPLATE)); out = []

    def bug(name, f):
        x = copy.deepcopy(d); f(x); out.append((name, x))
    bug('no primary', lambda x: x.pop('primary'))
    bug('grid_s 7', lambda x: x.update(grid_s=7))
    bug('unknown op', lambda x: x['inputs']['move'].update(op='avg'))
    bug('role other', lambda x: x['conditions'][0].update(role='other'))
    bug('no claim condition', lambda x: [c.update(role='shared') for c in x['conditions']])
    bug('label before t', lambda x: x['truth'][0].update(start_s=-60))
    bug('side sign 2', lambda x: x['fire']['side'].update(sign=2))
    bug('unknown code', lambda x: x['inputs']['x'].update(code='NOPE.S01'))
    bug('window day of 7 digits', lambda x: x['window'].update(last='2026053'))
    bug('claim type GUESS', lambda x: x['claim'].update(type='GUESS'))
    bug('lhs names no input', lambda x: x['conditions'][0].update(lhs='nothing'))
    bug('own_pct without q', lambda x: x['inputs']['x_top'].pop('q'))
    bug('an input reads itself', lambda x: x['inputs']['move'].update(of='move'))
    return out


def main():
    res = tests()
    for n, v in res:
        print('%s %s' % ('PASS' if v else 'FAIL', n))
    fails = [n for n, v in res if not v]
    print('TESTS %s (%d of %d pass)' % ('PASS' if not fails else 'FAIL', len(res) - len(fails), len(res)))
    refused = 0; bugs = planted()
    for name, x in bugs:
        try:
            parse(x); r = False; why = 'ACCEPTED'
        except DT.Refusal as e:
            r = True; why = e.code
        refused += r
        print('PLANTED %s: %s (%s)' % (name, 'REFUSED' if r else 'NOT REFUSED', why))
    print('PLANTED %d of %d refused' % (refused, len(bugs)))
    sys.exit(0 if not fails and refused == len(bugs) else 1)


if __name__ == '__main__':
    main()
