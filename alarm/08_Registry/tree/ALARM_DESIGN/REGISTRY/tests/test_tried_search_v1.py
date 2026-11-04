#!/usr/bin/env python3
"""test_tried_search_v1.py (SCOUT, 3 Nov 2026): tried_search_v1 through its command, on a planted RESEARCH_ROOT built from the frozen
fixtures in data_tried_search_v1/ (real definitions, registry rows and claims of 3 Nov 2026; no dev tree read). The planted copies are the
three known ones, renamed and turned round so only the structure is equal: CLOSEOUT (DESKA02) = AD2_OIFLUSH_OF1, WINDFALL (DESKA01) =
AD7_PAYERWIN_PW1, DELEVHOUR = SCOUTR12_20261103's try (claimed, not in the registry). A planted new idea must read NEW; mutants of the
definitions must read NEAR. TOOL_UNDER_TEST names the tool file (mutants_tried_search_v1.py sets it); ALARM_BASE names the Alarm folder
whose settings/SETTINGS_EXAMPLE.env gives the keys (default: the folder above this file that holds settings/)."""
import copy, json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.environ.get('TOOL_UNDER_TEST') or os.path.join(HERE, '..', 'tools', 'tried_search_v1.py')
DATA = os.path.join(HERE, 'data_tried_search_v1')


def alarm_base():
    if os.environ.get('ALARM_BASE'):
        return os.environ['ALARM_BASE']
    d = HERE
    while not os.path.isfile(os.path.join(d, 'settings', 'SETTINGS_EXAMPLE.env')):
        if os.path.dirname(d) == d:
            raise SystemExit('no Alarm folder above %s: set ALARM_BASE' % HERE)
        d = os.path.dirname(d)
    return d


def fx(n):
    with open(os.path.join(DATA, n)) as f:
        return f.read()


def disguise(d):
    """the same rule, other names: every input renamed, conditions in the other order, 'x - y > 0' written 'x > y', '<=' turned round,
    a new id and claim"""
    d = copy.deepcopy(d)
    ren = {k: 'q_%s_%d' % (k[::-1], i) for i, k in enumerate(d['inputs'])}
    R = lambda x: ren.get(x, x) if isinstance(x, str) else x
    inp = {}
    for k, v in d['inputs'].items():
        inp[ren[k]] = {a: R(b) if a != 'op' else b for a, b in v.items()}
    conds = []
    for c in reversed(d['conditions']):
        c = dict(c, lhs=R(c['lhs']), rhs=R(c['rhs']), name='renamed')
        lv = inp.get(c['lhs'])
        if c['cmp'] in ('>', '>=') and c['rhs'] == 0 and lv and lv['op'] == 'sub':
            c = dict(c, lhs=lv['a'], rhs=lv['b'])
        elif c['cmp'] == '<=':
            c = dict(c, lhs=c['rhs'], rhs=c['lhs'], cmp='>=')
        conds.append(c)
    for v in inp.values():
        if v.get('op') in ('add', 'mul') and 'a' in v and 'b' in v:
            v['a'], v['b'] = v['b'], v['a']
    d['inputs'] = dict(reversed(list(inp.items())))
    d['conditions'] = conds
    d['fire'] = dict(d['fire'], side=dict(d['fire']['side'], input=R(d['fire']['side']['input'])))
    d['id'] = 'PLANTED'
    d['claim'] = {'one_line': 'planted'}
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); r = self.t.name; self.r = r
        h = self.h = os.path.join(r, 'ALARM_DESIGN')
        keys = [l.split('=', 1)[0] for l in open(os.path.join(alarm_base(), 'settings', 'SETTINGS_EXAMPLE.env')) if '=' in l and not l.lstrip().startswith('#')]
        self.S = os.path.join(r, 'S.env')
        self.w(self.S, ''.join('%s=%s\n' % (k, r if k == 'RESEARCH_ROOT' else '') for k in keys))
        self.w(os.path.join(h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), fx('ALARM_REGISTRY_ROWS.tsv'))
        for rel, n in (('runs/AD2_20261029/ideas/OIFLUSH/defs/OF1.json', 'AD2_OIFLUSH_OF1.json'), ('runs/AD2_20261029/ideas/OIBUILD/defs/OB1.json', 'AD2_OIBUILD_OB1.json'),
                       ('runs/AD7_20261029/ideas/PAYERWIN/defs/PW1.json', 'AD7_PAYERWIN_PW1.json'),
                       ('runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json', 'SCOUTR12_DELEVHOUR_V1.json')):
            self.w(os.path.join(h, rel), fx(n))
        for c in ('SCOUTR12_20261103_DELEVHOUR', 'AD7_20261029_PAYERWIN', 'AD2_20261029_OIFLUSH'):
            self.w(os.path.join(h, 'runs', 'IDEAS_CLAIMED', c + '.txt'), fx('CLAIM_%s.txt' % c))
        self.w(os.path.join(r, 'PROCESS', '2_ALARMS', 'TRIED_ALARMS_V1.tsv'), fx('TRIED_ALARMS_ROWS.tsv'))

    def tearDown(self):
        self.t.cleanup()

    def w(self, p, t):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w') as f:
            f.write(t)
        return p

    def plant(self, d, n='PLANT.json'):
        return self.w(os.path.join(self.r, 'mine', n), json.dumps(d, indent=1))

    def run_(self, *a):
        p = subprocess.run([sys.executable, '-B', TOOL, '--settings', self.S] + list(a), capture_output=True, text=True)
        return p.returncode, p.stdout, p.stderr

    def verdict(self, out):
        v = [l for l in out.splitlines() if l.startswith('VERDICT')]
        self.assertEqual(len(v), 1, out)
        return v[0]

    def j(self, n):
        return json.loads(fx(n))


class PlantedCopies(Base):
    def test_closeout_is_a_copy_of_oiflush(self):
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('DESKA02_CLOSEOUT_V1.json'))))
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF COPY of AD2_OIFLUSH_OF1 (registry)'), out)

    def test_windfall_is_a_copy_of_payerwin(self):
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('DESKA01_WINDFALL_V1.json'))))
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF COPY of AD7_PAYERWIN_PW1 (registry)'), out)

    def test_delevhour_is_a_copy_of_the_claimed_try(self):
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('SCOUTR12_DELEVHOUR_V1.json'))))
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF COPY of SCOUTR12_20261103_DELEVHOUR (claim)'), out)

    def test_the_raw_known_copies_too(self):
        for n, want in (('DESKA02_CLOSEOUT_V1.json', 'AD2_OIFLUSH_OF1'), ('DESKA01_WINDFALL_V1.json', 'AD7_PAYERWIN_PW1')):
            rc, out, err = self.run_('--def', self.plant(self.j(n), n))
            self.assertIn('VERDICT DEF COPY of %s' % want, out)

    def test_self_leaves_out_the_own_claim(self):
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('SCOUTR12_DELEVHOUR_V1.json'))), '--self', 'SCOUTR12_20261103_DELEVHOUR')
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEW'), out)

    def test_the_def_file_itself_is_left_out(self):
        p = os.path.join(self.h, 'runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json')
        rc, out, err = self.run_('--def', p)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEW'), out)


class NewAndNear(Base):
    def new_idea(self):
        d = self.j('AD7_PAYERWIN_PW1.json')
        d['inputs'] = {'m': {'op': 'market', 'code': 'E2.S07'}, 'mh': {'op': 'sum', 'of': 'm', 'w_s': 1800}, 'f': {'op': 'raw', 'code': 'X9.Z99'},
                       'fp': {'op': 'own_pct', 'of': 'f', 'q': 99}, 's': {'op': 'sign', 'of': 'f'}}
        d['conditions'] = [{'name': 'n', 'lhs': 'f', 'cmp': '>', 'rhs': 'fp', 'role': 'claim'}, {'name': 'n', 'lhs': 'mh', 'cmp': '<', 'rhs': 0, 'role': 'claim'}]
        d['fire']['side']['input'] = 's'
        return d

    def test_planted_new_idea_is_new(self):
        rc, out, err = self.run_('--def', self.plant(self.new_idea()))
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEW'), out)
        self.assertNotIn('DEF COPY', out); self.assertNotIn('DEF NEAR', out)

    def test_other_percentile_is_near(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json'))
        for v in d['inputs'].values():
            if v.get('op') == 'own_pct' and v.get('q') == 1:
                v['q'] = 5
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEAR AD2_OIFLUSH_OF1 (registry)'), out)
        self.assertIn('the same lines with other numbers', out)

    def test_other_fire_side_is_near(self):
        d = disguise(self.j('DESKA01_WINDFALL_V1.json'))
        d['fire']['side']['sign'] = -1
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEAR AD7_PAYERWIN_PW1'), out)
        self.assertIn('other fire side', out)

    def test_one_more_filter_is_near(self):
        d = self.j('DESKA02_CLOSEOUT_V1.json')
        d['inputs']['f'] = {'op': 'raw', 'code': 'E1.S01'}
        d['conditions'].append({'name': 'extra', 'lhs': 'f', 'cmp': '>', 'rhs': 0.0001, 'role': 'claim'})
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEAR AD2_OIFLUSH_OF1'), out)
        self.assertIn('plus 1 condition lines', out)

    def test_half_the_lines_is_near(self):
        d = self.j('DESKA02_CLOSEOUT_V1.json')
        d['conditions'][1] = {'name': 'other', 'lhs': 'oi10', 'cmp': '<', 'rhs': -0.5, 'role': 'claim'}
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertIn('VERDICT DEF NEAR', out)
        self.assertIn('half or more of the lines equal', out)

    def test_price_only_rule_is_not_near(self):
        d = self.j('DESKA02_CLOSEOUT_V1.json')
        d['conditions'] = d['conditions'][:1]
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEW'), out)

    def test_other_grid_is_near_not_copy(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); d['grid_s'] = 5
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEAR AD2_OIFLUSH_OF1'), out); self.assertIn('other timing', out)

    def test_other_refractory_is_near_not_copy(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); d['fire']['refractory_s'] += 600
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF NEAR AD2_OIFLUSH_OF1'), out)

    def test_onset_off_is_near_and_defaults_count(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); d['fire']['onset'] = False
        self.assertIn('VERDICT DEF NEAR AD2_OIFLUSH_OF1', self.run_('--def', self.plant(d))[1])
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); del d['fire']['onset']   # the detector's default is onset true: still a COPY
        self.assertIn('VERDICT DEF COPY of AD2_OIFLUSH_OF1', self.run_('--def', self.plant(d, 'P2.json'))[1])

    def test_the_comparison_base_does_not_choose_fires(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); d['base'] = {'seed': 23102026}   # the released default seed (GPT V12111-TOOL)
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertIn('VERDICT DEF COPY of AD2_OIFLUSH_OF1', out); self.assertIn('differ (fires unchanged)', out)
        d['grid_s'] = 5   # the control beside it: a real fire change is still NEAR
        self.assertIn('VERDICT DEF NEAR AD2_OIFLUSH_OF1', self.run_('--def', self.plant(d, 'P2.json'))[1])

    def test_an_unused_or_truth_only_event_list_keeps_the_copy(self):
        d = disguise(self.j('DESKA02_CLOSEOUT_V1.json')); d['events'] = {'liq': 'lists/LIQ_V1.tsv'}; d['events_cover'] = {'liq': ['20250910', '20251231']}
        self.assertIn('VERDICT DEF COPY of AD2_OIFLUSH_OF1', self.run_('--def', self.plant(d))[1])
        d['truth'] = [{'name': 't', 'kind': 'events', 'events': 'liq'}]   # read by the truth label only
        self.assertIn('VERDICT DEF COPY of AD2_OIFLUSH_OF1', self.run_('--def', self.plant(d, 'P2.json'))[1])

    def test_a_trigger_event_list_is_part_of_the_rule(self):
        base = self.j('DESKA02_CLOSEOUT_V1.json')
        base['events'] = {'liq': 'lists/LIQ_V1.tsv'}; base['events_cover'] = {'liq': ['20250910', '20251231']}
        base['inputs']['ls'] = {'op': 'ev_since', 'events': 'liq', 'w_s': 600}
        base['conditions'].append({'name': 'a liquidation event in 10 min', 'lhs': 'ls', 'cmp': '<=', 'rhs': 600, 'role': 'claim'})
        self.w(os.path.join(self.h, 'runs/AD2_20261029/ideas/OIFLUSH/defs/OF9.json'), json.dumps(base))   # a claimed definition with the list
        same = copy.deepcopy(base); same['events'] = {'renamed': 'lists/LIQ_V1.tsv'}; same['events_cover'] = {'renamed': ['20250910', '20251231']}
        same['inputs']['ls']['events'] = 'renamed'   # the same file and days under another name: still a COPY
        self.assertIn('VERDICT DEF COPY of AD2_20261029_OIFLUSH', self.run_('--def', self.plant(same))[1])
        other = copy.deepcopy(base); other['events'] = {'liq': 'lists/LIQ_V2.tsv'}   # another list the trigger reads: NEAR
        out = self.run_('--def', self.plant(other, 'P2.json'))[1]
        oline = [l for l in out.splitlines() if l.startswith('DEF NEAR AD2_20261029_OIFLUSH') and 'OF9.json' in l]
        self.assertTrue(oline and 'fires unchanged' not in oline[0], out)   # a trigger list change is not 'fires unchanged' (V12113 item 1)
        self.assertNotIn('VERDICT DEF COPY', out); self.assertRegex(self.verdict(out), r'^VERDICT DEF NEAR .*AD2_20261029_OIFLUSH \(claim\)')

    def test_threshold_at_full_precision(self):
        d = disguise(self.j('DESKA01_WINDFALL_V1.json'))
        for c in d['conditions']:
            if c['rhs'] == 0.0002:
                c['rhs'] = 0.00020000000001
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertNotIn('VERDICT DEF COPY', out); self.assertIn('VERDICT DEF NEAR AD7_PAYERWIN_PW1', out)

    def test_other_code_is_not_a_copy(self):
        d = self.j('DESKA02_CLOSEOUT_V1.json')
        d['inputs']['oi10']['code'] = 'E2.S05'
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertNotIn('VERDICT DEF COPY', out)

    def test_other_window_is_not_a_copy(self):
        d = self.j('DESKA02_CLOSEOUT_V1.json')
        d['inputs']['d10']['w_s'] = 900
        rc, out, err = self.run_('--def', self.plant(d))
        self.assertNotIn('VERDICT DEF COPY', out)
        self.assertIn('VERDICT DEF NEAR', out)


class Words(Base):
    def test_words_find_payerwin_first_with_why(self):
        rc, out, err = self.run_('funding', 'windfall', 'payers')
        self.assertEqual(rc, 0, err)
        r1 = [l for l in out.splitlines() if l.strip().startswith('R1 ')]
        self.assertTrue(r1 and 'AD7_PAYERWIN_PW1' in r1[0], out)
        self.assertIn('funding in one_line', r1[0])
        self.assertTrue(any(l.strip().startswith('C1 AD7_20261029_PAYERWIN') for l in out.splitlines()), out)
        self.assertTrue(self.verdict(out).startswith('VERDICT WORDS ONLY'))

    def test_tried_rows_are_searched(self):
        rc, out, err = self.run_('latejoin')
        self.assertIn('T1 SCOUT_20261102_B', out)

    def test_a_word_matches_tokens_not_inside_words(self):
        rc, out, err = self.run_('oi')
        self.assertIn('REGISTRY', out)
        rc2, out2, err2 = self.run_('nt')
        self.assertIn('REGISTRY 0 rows', out2)

    def test_a_long_word_matches_a_longer_token(self):
        rc, out, err = self.run_('fund')
        self.assertIn('AD7_PAYERWIN_PW1', out)

    def test_def_codes_are_words(self):
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('DESKA01_WINDFALL_V1.json'))))
        self.assertIn('words e1.s01', out)
        self.assertRegex(out, r'e1\.s01 in [a-z_,]*codes')
        self.assertRegex(out, r'R1 AD7_PAYERWIN_PW1 .*e1\.s01 in one_line')   # a code is one token of the text, dots and all

    def test_unreadable_possible_copy_is_incomplete_not_new(self):
        self.w(os.path.join(self.h, 'runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json'), '{broken')   # the only copy, unreadable
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('SCOUTR12_DELEVHOUR_V1.json'))))
        self.assertEqual(rc, 0, err)
        v = self.verdict(out); self.assertTrue(v.startswith('VERDICT DEF INCOMPLETE: 1 definitions'), out)
        self.assertIn('runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json', v)

    def test_no_readable_definition_is_incomplete(self):
        for rel in ('runs/AD2_20261029/ideas/OIFLUSH/defs/OF1.json', 'runs/AD2_20261029/ideas/OIBUILD/defs/OB1.json',
                    'runs/AD7_20261029/ideas/PAYERWIN/defs/PW1.json', 'runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json'):
            self.w(os.path.join(self.h, rel), 'not json')
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('DESKA02_CLOSEOUT_V1.json'))))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF INCOMPLETE: 4 definitions'), out)

    def test_a_copy_is_kept_when_another_is_unreadable(self):
        self.w(os.path.join(self.h, 'runs/SCOUTR12_20261103/ideas/DELEVHOUR/defs/V1.json'), '{broken')
        rc, out, err = self.run_('--def', self.plant(disguise(self.j('DESKA02_CLOSEOUT_V1.json'))))
        self.assertTrue(self.verdict(out).startswith('VERDICT DEF COPY of AD2_OIFLUSH_OF1'), out); self.assertIn('DEF UNREADABLE 1', out)

    def test_unreadable_claimed_def_is_counted(self):
        self.w(os.path.join(self.h, 'runs/AD7_20261029/ideas/PAYERWIN/defs/BROKEN.json'), '{not json')
        rc, out, err = self.run_('funding')
        self.assertEqual(rc, 0, err)
        self.assertIn('defs unreadable 1', out)


class Refusals(Base):
    def rc(self, *a):
        rc, out, err = self.run_(*a)
        self.assertEqual(rc, 2, out + err); self.assertIn('REFUSED', err)
        return err

    def test_nothing_to_search(self):
        self.assertIn('GIVE WORDS', self.rc())

    def test_bad_def(self):
        self.assertIn('BAD_DEF', self.rc('--def', self.w(os.path.join(self.r, 'x.json'), '{oops')))
        self.assertIn('BAD_DEF', self.rc('--def', self.w(os.path.join(self.r, 'y.json'), '{"inputs": {}, "conditions": []}')))

    def test_no_def_file(self):
        self.assertIn('NO DEF FILE', self.rc('--def', os.path.join(self.r, 'none.json')))

    def test_bad_n(self):
        self.assertIn('--n', self.rc('x', '--n', '0'))
        self.assertIn('--n', self.rc('x', '--n', 'two'))

    def test_registry_without_columns(self):
        self.w(os.path.join(self.h, 'REGISTRY', 'ALARM_REGISTRY_V1.tsv'), 'alarm_id\tkind\nA\tOWN\n')
        self.assertIn('LACKS COLUMNS', self.rc('x'))

    def test_no_settings(self):
        p = subprocess.run([sys.executable, '-B', TOOL, 'funding'], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2); self.assertIn('--settings', p.stderr)

    def test_bad_self_and_unknown_option(self):
        self.assertIn('--self', self.rc('x', '--self', 'NOUNDERSCORE'))
        self.assertIn('UNKNOWN OPTION', self.rc('x', '--lean'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
