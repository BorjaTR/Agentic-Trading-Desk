"""test_v27_candidate.py (ctxprof_shared, 25 Oct 2026): labcore V2_7 CANDIDATE modules selection, runs, cache. Seconds, no market value
read: selection reads the A02P event list and the canonical roster metadata (PRICE index hashes); runs and cache use planted folders and
a planted lab3 root written by lab3.write (no store is written).
  S  selection: every kind on one real day; refusals by code; membership not syntax; empty = explicit success; identity changes;
     the selected list keeps declarations and rows byte for byte; event_situations' interface (resolve_selection)
  R  runs.check_stage teeth: a missing, extra, partial, aside or wrong-content part, two seals, two source pins, a pin not frozen, a lab
     index changed during the run; plan_identity has no out_root; replay_diff ignores only the named telemetry
  C  cache identity: every identity field changes the key; a rewritten source part is never served from the cache (and the mutant
     without a source vintage serves the stale value); entity, clock, settings and dates; bounded eviction; output seals stay apart
Run: cd team/RESEARCH/tools/labcore/tests && python3 -B -m pytest -q test_v27_candidate.py"""
import json, os, shutil, sys, time
import numpy as np
import pytest

TOOLS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))
F = os.path.realpath(os.path.join(TOOLS, '..', '..', '..'))
CODE = os.path.join(F, 'team', 'LAB3', 'code')
sys.path.insert(0, TOOLS); sys.path.insert(0, CODE)
from labcore.v2_7 import selection as S, runs, cache as K  # noqa: E402

LIST = '<SCRATCH>/work_LEAD/ctxprof_fix2/shared/lists/A02P_EPG_INPUT_DECLARED_V1.tsv'
RAW_LIST = '<SCRATCH>/work_LEAD/ed2/epg/A02P_EPG_INPUT.tsv'
SCRATCH = '<SCRATCH>/work_LEAD/ctxprof_fix2/shared/tests_tmp'
DAY = '20251016'


@pytest.fixture
def box(request):
    p = os.path.join(SCRATCH, 'u_%s_%s' % (request.node.name, time.strftime('%H%M%S%f')))
    os.makedirs(p)
    return p


class Law:
    """a planted law: refuses the days named"""
    def __init__(self, refused=()):
        self.refused = set(refused)

    def research_refusal(self, day):
        return 'PLANTED SEAL' if str(day) in self.refused else None


# ------------------------------------------------------------------------------------------------------------------ S selection
@pytest.mark.parametrize('sel,events', [('list', 69), ('all', 69), ('coin:BTC', 4), ('coins:BTC,ETH', 9), ('roster', 64), ('coin:CAKE', 0)])
def test_S1_every_kind_one_day(sel, events):
    s = S.select(LIST, DAY, DAY, sel, subject='A02P', law=Law())
    assert s['coverage']['observed']['events'] == events == len(s['rows'])
    assert s['status'] == ('EMPTY_SELECTED_POPULATION' if events == 0 else 'SELECTED')
    assert sum(s['coverage']['excluded_in_range'].values()) + events == s['coverage']['list']['rows_in_range'] == 69
    if events:
        assert s['coverage']['source_states']['counts'] == {'IN_SOURCE': events}


def test_S2_roster_member_rule_is_dated():
    s = S.select(LIST, DAY, DAY, 'roster', subject='A02P', law=Law())
    wk = s['coverage']['requested']['roster_of_record']['files']
    assert list(wk) == ['ROSTER_20251013.csv']
    out = [r for r in S.read_list(LIST)['rows'] if r[4] == DAY and r[0] not in {x[0] for x in s['rows']}]
    assert s['coverage']['excluded_in_range'] == {'NOT_A_MEMBER_THAT_DAY': len(out)} and len(out) == 5
    import csv
    members = {r['coin'] for r in csv.DictReader(l for l in open(os.path.join(S.WEEKLY_DIR, 'ROSTER_20251013.csv')) if not l.startswith('#'))}
    assert all(r[2] not in members for r in out) and all(r[2] in members for r in s['rows'])


def test_S3_week_without_roster_is_typed_gap_and_alias_is_declared():
    s = S.select(LIST, '20250915', '20250915', 'roster', subject='A02P', law=Law())
    assert s['status'] == 'EMPTY_SELECTED_POPULATION' and s['coverage']['requested']['group_gaps'] == [('20250915', '20250915')]
    assert set(s['coverage']['excluded_in_range']) == {'GROUP_NOT_EFFECTIVE'}
    a = S.select(LIST, '20251001', '20251001', 'roster', subject='A02P', law=Law())   # week of 29 Sep: the receipt's alias to 6 Oct
    assert a['coverage']['requested']['roster_of_record']['aliases_used'] == {'20250929': '20251006'} and a['rows']


@pytest.mark.parametrize('sel,first,last,code', [('coin:XYZ', DAY, DAY, 'UNKNOWN_COIN'), ('coins:BTC,', DAY, DAY, 'MALFORMED_COINS'),
                                                 ('coin:BTC', DAY, '20251015', 'REVERSED_RANGE'), ('coin:BTC', '20251301', '20251301', 'MALFORMED_DATE'),
                                                 ('group:X', DAY, DAY, 'BAD_SELECTION'), ('nonsense', DAY, DAY, 'BAD_SELECTION')])
def test_S4_refusals_by_code(sel, first, last, code):
    with pytest.raises(S.SelectionRefused) as e:
        S.select(LIST, first, last, sel, subject='A02P', law=Law())
    assert e.value.code == code


def test_S5_law_refusal_before_anything(box):
    with pytest.raises(S.SelectionRefused) as e:
        S.select(LIST, '20251015', DAY, 'coin:BTC', law=Law({DAY}))
    assert e.value.code == 'SEALED_REQUEST'


def test_S6_membership_not_syntax_and_unknown_group(box):
    gf = os.path.join(box, 'g.tsv'); open(gf, 'w').write('group\tcoin\nPAIR\tBTC\nPAIR\tETH\n')   # a group file naming an unknown coin is refused whole (below)
    assert S.select(LIST, DAY, DAY, 'group:PAIR', group_file=gf, law=Law())['coverage']['observed']['events'] == 9
    for g, code in (('BAD', 'UNKNOWN_COIN'), ('NOPE', 'UNKNOWN_GROUP')):
        gf2 = gf if g != 'BAD' else os.path.join(box, 'g2.tsv')
        if g == 'BAD':
            open(gf2, 'w').write('group\tcoin\nBAD\tBTCX\n')
        with pytest.raises(S.SelectionRefused) as e:
            S.select(LIST, DAY, DAY, 'group:%s' % g, group_file=gf2, law=Law())
        assert e.value.code == code
    s = S.select(LIST, DAY, DAY, 'coin:CAKE', law=Law())                 # a roster-of-record coin the lab never held: valid, empty
    assert s['status'] == 'EMPTY_SELECTED_POPULATION' and 'CAKE' in s['coverage']['requested']['canonical_roster']['added_members']


def test_S7_dated_json_group(box):
    gf = os.path.join(box, 'g.json')
    json.dump({'schema_version': 1, 'version': 'T1', 'timezone': 'UTC', 'groups': {'D': [{'first': '20251016', 'last': '20251016', 'coins': ['BTC']},
                                                                                        {'first': '20251017', 'last': '20251017', 'coins': ['ETH']}]}}, open(gf, 'w'))
    s = S.select(LIST, '20251016', '20251017', 'group:D', group_file=gf, law=Law())
    got = {(r[2], r[4]) for r in s['rows']}
    assert got and all((c, d) in (('BTC', '20251016'), ('ETH', '20251017')) for c, d in got)
    with pytest.raises(S.SelectionRefused) as e:
        S.resolve_selection({'coin': np.array(['BTC']), 't': np.array([1760572800.0])}, group='D', group_file=gf, first='20251016',
                            last='20251017', law=Law())
    assert e.value.code == 'DATED_GROUP'


def test_S8_identity_changes_and_selected_file(box):
    a = S.select(LIST, DAY, DAY, 'coin:BTC', law=Law()); b = S.select(LIST, DAY, DAY, 'coin:ETH', law=Law())
    c = S.select(RAW_LIST, DAY, DAY, 'coin:BTC', law=Law()); d = S.select(LIST, DAY, '20251017', 'coin:BTC', law=Law())
    assert len({a['cache_key'], b['cache_key'], c['cache_key'], d['cache_key']}) == 4
    assert S.select(LIST, DAY, DAY, 'coin:BTC', law=Law())['cache_key'] == a['cache_key']
    p = os.path.join(box, 'sel.tsv'); open(p, 'w').write(S.selected_text(a))
    txt = open(p).read(); src = open(LIST).read().splitlines(keepends=True)
    assert txt.startswith('# side_means: forced_liquidation\n# history_coverage: 20250912..20260228\n')
    assert all(l in src for l in txt.splitlines(keepends=True))           # every row byte-equal to a row of the list
    assert len(txt.splitlines()) == 2 + 1 + 4


def test_S9_situations_interface():
    ev = {'coin': np.array(['BTC', 'ETH', 'SOL']), 't': np.array([1760572800.0 + 60, 1760572800.0 + 120, 1760572800.0 + 180])}
    got, rec = S.resolve_selection(ev, coins='BTC,ETH', law=Law())
    assert got == {'BTC', 'ETH'} and rec['kind'] == 'coins' and rec['status'] == 'SELECTED'
    got, rec = S.resolve_selection(ev, coins='ALL', law=Law())
    assert got is None and rec['kind'] == 'all'
    got, rec = S.resolve_selection(ev, coins='CAKE', law=Law())
    assert got == {'CAKE'} and rec['status'] == 'EMPTY_SELECTED_POPULATION'
    with pytest.raises(S.SelectionRefused) as e:
        S.resolve_selection(ev, coins='XYZ', law=Law())
    assert e.value.code == 'UNKNOWN_COIN'


def test_S10_roster_document_pinned(box):
    p = os.path.join(box, 'R.json'); shutil.copy(S.ROSTER_DOC, p)
    with open(p, 'a') as f:
        f.write(' ')
    with pytest.raises(S.SelectionRefused) as e:
        S.select(LIST, DAY, DAY, 'coin:BTC', roster_doc=p, law=Law())
    assert e.value.code == 'ROSTER_DOC_CHANGED'


# ------------------------------------------------------------------------------------------------------------------ R runs
def plant(root, day, part, coins, rows, seal='S', sources=None, extra=None):
    d = os.path.join(root, 'day=%s' % day, part); os.makedirs(d)
    ix = {'coins': coins, 'seal': seal, 'sources': dict({'code:x.py': 'a' * 16}, **(sources or {})),
          'readings': {'%s.c' % part: {'kind': 'ROWS', 'shape': [rows]}}, 'built_utc': '2026-10-25T00:00:00Z'}
    ix.update(extra or {})
    json.dump(ix, open(os.path.join(d, 'index.json'), 'w'))
    open(os.path.join(d, 'REASONS.txt'), 'w').write('""\n"NOT_KNOWN"\n')


def good(box):
    root = os.path.join(box, 'stage'); lab = os.path.join(box, 'lab'); os.makedirs(os.path.join(lab, 'day=20251016', 'PRICE'))
    li = os.path.join(lab, 'day=20251016', 'PRICE', 'index.json'); open(li, 'w').write('{"coins": ["BTC"]}')
    pin = {'lab:day=20251016/PRICE': runs.sha16_file(li)}
    plant(root, DAY, 'EPG.T', ['BTC', 'ETH'], 3, sources=pin); plant(root, '20251017', 'EPG.T', ['BTC'], 1, sources=pin)
    exp = {(DAY, 'EPG.T'): {'coins': ['BTC', 'ETH'], 'rows': 3}, ('20251017', 'EPG.T'): {'coins': ['BTC'], 'rows': 1}}
    return root, lab, exp


def test_R1_check_stage_passes_and_reports(box):
    root, lab, exp = good(box)
    r = runs.check_stage(root, exp, {'code:x.py': 'a' * 16}, lab_root=lab)
    assert set(r['parts']) == {'day=%s/EPG.T/index.json' % DAY, 'day=20251017/EPG.T/index.json'}
    assert r['observed']['rows'] == {'EPG.T': 4} and r['observed']['reasons'] == {'EPG.T': ['NOT_KNOWN']} and r['pins']['lab_indexes'] == 1


@pytest.mark.parametrize('mutation,code', [
    ('missing', 'PART_MISSING'), ('extra', 'UNEXPECTED_PART'), ('partial', 'PARTIAL_WRITE'), ('aside', 'ASIDE_IN_RUN'),
    ('noindex', 'PARTIAL_WRITE'), ('rows', 'PART_CONTENT'), ('coins', 'PART_CONTENT'), ('seal', 'SEALS_DISAGREE'),
    ('pins', 'SOURCE_PINS_DISAGREE'), ('frozen', 'SOURCE_PIN_NOT_FROZEN'), ('lab', 'SOURCE_CHANGED_DURING_RUN'),
    ('foreign', 'UNEXPECTED_PART')])
def test_R2_check_stage_teeth(box, mutation, code):
    root, lab, exp = good(box); frozen = {'code:x.py': 'a' * 16}
    d1 = os.path.join(root, 'day=%s' % DAY)
    if mutation == 'missing':
        exp[('20251018', 'EPG.T')] = {'coins': ['BTC'], 'rows': 1}
    elif mutation == 'extra':
        del exp[('20251017', 'EPG.T')]
    elif mutation == 'partial':
        os.makedirs(os.path.join(d1, 'EPG.T.tmp_20251025T000000Z'))
    elif mutation == 'aside':
        os.makedirs(os.path.join(d1, 'EPG.T.aside_20251025T000000Z'))
    elif mutation == 'noindex':
        os.remove(os.path.join(root, 'day=20251017', 'EPG.T', 'index.json'))
    elif mutation == 'rows':
        exp[(DAY, 'EPG.T')]['rows'] = 4
    elif mutation == 'coins':
        exp[(DAY, 'EPG.T')]['coins'] = ['BTC']
    elif mutation == 'seal':
        shutil.rmtree(os.path.join(root, 'day=20251017')); plant(root, '20251017', 'EPG.T', ['BTC'], 1, seal='OTHER')
    elif mutation == 'pins':
        shutil.rmtree(os.path.join(root, 'day=20251017')); plant(root, '20251017', 'EPG.T', ['BTC'], 1, sources={'settings:s.json': 'b' * 16})
        p = os.path.join(d1, 'EPG.T', 'index.json'); ix = json.load(open(p)); ix['sources']['settings:s.json'] = 'c' * 16; json.dump(ix, open(p, 'w'))
    elif mutation == 'frozen':
        frozen = {'code:x.py': 'f' * 16}
    elif mutation == 'lab':
        open(os.path.join(lab, 'day=20251016', 'PRICE', 'index.json'), 'w').write('{"coins": ["BTC", "ETH"]}')
    elif mutation == 'foreign':
        os.makedirs(os.path.join(d1, 'OTHER.PART'))
    with pytest.raises(runs.RunRefused) as e:
        runs.check_stage(root, exp, frozen, lab_root=lab, prefixes=('EPG.T',))
    assert e.value.code == code


def test_R3_plan_identity_and_replay_telemetry(box):
    with pytest.raises(ValueError):
        runs.plan_identity({'out_root': '/x'})
    assert runs.plan_identity({'a': 1, 'b': [1, 2]}) == runs.plan_identity({'b': [1, 2], 'a': 1})
    a, _, _ = good(box); b = os.path.join(box, 'b'); shutil.copytree(a, b)
    json.dump({'committed_utc': 'X', 'run_id': '1', 'telemetry': {'wall_s': 1}, 'parts': {'p': '1'}, 'seals': {'k': 's'}},
              open(os.path.join(a, 'RUN_MANIFEST.json'), 'w'))
    json.dump({'committed_utc': 'Y', 'run_id': '2', 'telemetry': {'wall_s': 2}, 'parts': {'p': '2'}, 'seals': {'k': 's'}},
              open(os.path.join(b, 'RUN_MANIFEST.json'), 'w'))
    p = os.path.join(b, 'day=%s' % DAY, 'EPG.T', 'index.json'); ix = json.load(open(p)); ix['built_utc'] = 'later'; json.dump(ix, open(p, 'w'))
    assert runs.replay_diff(a, b) == []                                   # only named telemetry differs
    ix['seal'] = 'changed'; json.dump(ix, open(p, 'w'))
    assert runs.replay_diff(a, b) == ['day=%s/EPG.T/index.json differs' % DAY]
    json.dump({'committed_utc': 'Y', 'run_id': '2', 'telemetry': {}, 'parts': {'q': '2'}, 'seals': {'k': 's'}}, open(os.path.join(b, 'RUN_MANIFEST.json'), 'w'))
    assert 'RUN_MANIFEST.json differs' in runs.replay_diff(a, b)          # a different part SET is never telemetry


# ------------------------------------------------------------------------------------------------------------------ C cache identity
def ident(**kw):
    x = dict(kind='clock_day', code='T.C', entity=['BTC'], dates=[DAY], clock_s=60, settings_sha16=None, source_vintage=())
    x.update(kw)
    return x


def test_C1_every_field_changes_the_key():
    base = K.key(ident())
    for f, v in (('kind', 'other'), ('code', 'T.D'), ('entity', ['ETH']), ('dates', ['20251017']), ('clock_s', 300),
                 ('settings_sha16', 'a' * 16), ('source_vintage', (('p', 1, 2, 3),))):
        assert K.key(ident(**{f: v})) != base, f
    for bad in (dict(ident(), extra=1), {k: v for k, v in ident().items() if k != 'clock_s'}):
        with pytest.raises(ValueError):
            K.key(bad)


def write_planted(lab, value, code='T.C'):
    from lab3 import write as LW
    t0 = 1760572800 * 1_000_000                                            # 20251016 00:00 UTC
    rows = {'day': [int(DAY)] * 2, 'as_of_us': [t0, t0 + 60_000_000], 'known_at_us': [t0, t0 + 60_000_000], 'value_kind': [1, 1],
            'value_bits': [int(np.array([value], '<f8').view('<u8')[0])] * 2, 'value_txt': [None, None], 'empty_reason': ['', ''], 'stale': [0, 0]}
    LW.write_part(lab, int(DAY), 'TPART', {code: {'step': 60, 'kind': 'NUMBER', 'rows': {'BTC': rows, 'ETH': rows}}}, ['BTC', 'ETH'],
                  catalog={code: {'kind': 'CLOCK', 'clock': 60, 'exact_k': False, 'scope': 'coin'}}, sources={'planted': 'a' * 16}, seal='P')


def test_C2_rewritten_source_never_served_and_the_mutant_is(box):
    from lab3 import days as LD
    sys.path.insert(0, os.path.join(TOOLS, 'event_profile'))
    import clock_series as CS
    lab = os.path.join(box, 'lab'); write_planted(lab, 1.0)
    C = K.IdentityCache(); M = K.IdentityCache()
    def read():
        return CS.read_day_typed(LD.Days(lab, 'research'), 'T.C', DAY, ['BTC'], 60)
    def vint():
        dd = os.path.join(lab, 'day=%s' % DAY)
        return K.vintage(os.path.join(dd, p, 'index.json') for p in LD.Days(lab, 'research').parts(DAY))
    v1 = C.get(ident(source_vintage=vint()), read)['v'][0].max()
    assert v1 == 1.0 and C.get(ident(source_vintage=vint()), read)['v'][0].max() == 1.0 and C.stats()['hits'] == 1
    M.get(ident(), read)                                                    # the mutant: no source vintage in its identity
    write_planted(lab, 2.0)                                                 # the source part is rewritten (lab3 puts the old one aside)
    assert C.get(ident(source_vintage=vint()), read)['v'][0].max() == 2.0 and C.stats()['misses'] == 2
    assert M.get(ident(), read)['v'][0].max() == 1.0                           # the mutant serves the stale value: the field is what protects


def test_C3_entity_clock_settings_dates_and_bound(box):
    from lab3 import days as LD
    sys.path.insert(0, os.path.join(TOOLS, 'event_profile'))
    import clock_series as CS
    lab = os.path.join(box, 'lab'); write_planted(lab, 3.0); C = K.IdentityCache(max_items=2); n = []
    def read(coins):
        n.append(1); return CS.read_day_typed(LD.Days(lab, 'research'), 'T.C', DAY, coins, 60)
    a = C.get(ident(entity=['BTC', 'ETH']), lambda: read(['BTC', 'ETH']))
    b = C.get(ident(entity=['ETH']), lambda: read(['ETH']))
    assert a['v'].shape[0] == 2 and b['v'].shape[0] == 1 and len(n) == 2   # a 2-coin read is never served as a 1-coin read
    with pytest.raises(ValueError):                                         # a 300 s request is its own key and the reader refuses it
        C.get(ident(clock_s=300), lambda: CS.read_day_typed(LD.Days(lab, 'research'), 'T.C', DAY, ['BTC'], 300))
    C.get(ident(entity=['BTC', 'ETH'], settings_sha16='b' * 16), lambda: read(['BTC', 'ETH']))
    assert len(n) == 3 and C.stats()['evictions'] >= 1 and C.stats()['items'] == 2
    C.drop(lambda i: i['settings_sha16'] is not None)
    assert C.stats()['items'] == 1


def test_C4_output_seal_is_not_cache_identity(box):
    """rewriting an OUTPUT part (another root, another seal) never touches an input cache entry; rewriting the INPUT does"""
    from lab3 import days as LD
    sys.path.insert(0, os.path.join(TOOLS, 'event_profile'))
    import clock_series as CS
    lab = os.path.join(box, 'lab'); out = os.path.join(box, 'out'); write_planted(lab, 4.0); write_planted(out, 9.0)
    C = K.IdentityCache()
    vint = lambda: K.vintage([os.path.join(lab, 'day=%s' % DAY, 'TPART', 'index.json')])
    rd = lambda: CS.read_day_typed(LD.Days(lab, 'research'), 'T.C', DAY, ['BTC'], 60)
    C.get(ident(source_vintage=vint()), rd); write_planted(out, 10.0)        # a new output seal and sources: the input is unchanged
    C.get(ident(source_vintage=vint()), rd)
    assert C.stats() == {'hits': 1, 'misses': 1, 'evictions': 0, 'items': 1}


# ------------------------------------------------------------------------------------------------------------------ registry (L11 for v2_7)
def test_G1_functions_v2_registry_true():
    """FUNCTIONS_V2.tsv = every FUNCTIONS_V1 row unchanged + one row per public function of labcore/v2_7, sha16 = sha16 of its source"""
    import hashlib, inspect
    lc = os.path.join(TOOLS, 'labcore')
    v1 = [l for l in open(os.path.join(lc, 'FUNCTIONS_V1.tsv'), encoding='utf-8') if l.strip()]
    v2 = [l for l in open(os.path.join(lc, 'FUNCTIONS_V2.tsv'), encoding='utf-8') if l.strip()]
    assert [l.rstrip('\n') for l in v2[:len(v1)]] == [l.rstrip('\n') for l in v1]
    hdr = v2[0].rstrip('\n').split('\t'); new = [l.rstrip('\n').split('\t') for l in v2[len(v1):]]
    reg = {(r[hdr.index('module')], r[hdr.index('function')]): r[hdr.index('sha16')] for r in new}
    have = {}
    from labcore.v2_7 import series as SR, rows as RW, quality as QY
    for m in (S, runs, K, SR, RW, QY):
        for n, f in inspect.getmembers(m, lambda x: inspect.isfunction(x) or inspect.isclass(x)):
            if f.__module__ == m.__name__ and not n.startswith('_'):
                have[(m.__name__, n)] = hashlib.sha256(inspect.getsource(f).encode()).hexdigest()[:16]
    missing = sorted(set(have) - set(reg))
    wrong = sorted(k for k in set(have) & set(reg) if have[k] != reg[k])
    assert not missing and not wrong, (missing, wrong)
    for (mod, n), sha in reg.items():                                      # re-exports: named, and their source sha16 true
        m = {S.__name__: S, runs.__name__: runs, K.__name__: K, SR.__name__: SR, RW.__name__: RW, QY.__name__: QY}[mod]
        assert hashlib.sha256(inspect.getsource(getattr(m, n)).encode()).hexdigest()[:16] == sha, n


# ------------------------------------------------------------------------------------------------------------------ phase B
def test_B1_series_is_clock_series_by_reexport():
    """labcore.v2_7.series re-exports event_profile/clock_series.py (no rewrite): the SAME objects, one module per process"""
    from labcore.v2_7 import series
    sys.path.insert(0, os.path.join(TOOLS, 'event_profile'))
    import clock_series as CS
    assert series.CS is CS and series.read_day_typed is CS.read_day_typed and series.ClockSeries is CS.ClockSeries
    assert series.parts_holding is CS.parts_holding and series.STATE_WORD is CS.STATE_WORD
    assert os.path.realpath(series.CS_PATH) == os.path.realpath(CS.__file__)


def test_B2_series_reads_a_planted_day_typed(box):
    """the re-exported reader on a planted lab3 root: a built day is read; a day no part names is NOT_BUILT from metadata"""
    from lab3 import days as LD
    from labcore.v2_7 import series
    lab = os.path.join(box, 'lab'); write_planted(lab, 5.0)
    R = LD.Days(lab, 'research')
    x = series.read_day_typed(R, 'T.C', DAY, ['BTC'], 60)
    assert x['built'] and x['v'][0].max() == 5.0
    y = series.read_day_typed(R, 'T.C', '20251017', ['BTC'], 60)
    assert not y['built'] and y['v'] is None


def test_B3_fixed_canon_rows_nan_vs_number():
    """labcore/_rows.py (V2_6, pinned) raises TypeError on NaN vs a number in one column; v2_7.rows sorts it; rows without NaN/None
    keep exactly the V2_6 order"""
    from labcore import _rows as old
    from labcore.v2_7 import rows as new
    cols = {'a': np.array([1.0, np.nan, 2.0]), 'b': np.array([1, 1, 1])}
    with pytest.raises(TypeError):
        old.canon_rows(cols)
    got = new.canon_rows(cols)
    assert len(got) == 3 and got[-1][0][1] == ('fnan', 0)
    plain = {'a': np.array([3.0, -1.0, 2.5, 0.0]), 'b': np.array([2, 1, 3, 4]), 'c': np.array(['x', 'y', 'z', 'w'], object)}
    assert new.canon_rows(plain) == old.canon_rows(plain)
    assert new.canon_rows({'a': np.array([None, 'x'], object)})                # None beside a value: no TypeError either


class _R:
    """a planted Days-like reader for roster_unknown: day -> PRICE coins (None = no PRICE part); opens are recorded"""
    def __init__(self, idx):
        self.idx = idx; self.opened = []

    def all_days(self):
        return sorted(self.idx)

    def parts(self, d):
        return ['PRICE'] if self.idx[d] is not None else []

    def index(self, d, part):
        self.opened.append(d); return {'coins': self.idx[d]}


def _old_roster_unknown():
    """the function as context_fix2 wrote it (alarm_context_ed2.py 0d70516ee7b5ea5a twin), its 'sealed' = law.research_refusal"""
    import ast, glob
    tw = sorted(glob.glob(os.path.join(TOOLS, 'alarm_context', 'alarm_context_ed2.py.pre_ctxprof_shared_*')))[0]
    tree = ast.parse(open(tw).read()); fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'roster_unknown')
    ns = {'sealed': lambda d, law: law.research_refusal(str(d))}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), tw, 'exec'), ns)
    return ns['roster_unknown']


def test_B4_roster_unknown_registered_unchanged():
    """the shared roster_unknown (registered from Context's rule) answers and opens exactly like Context's own (frozen 0d70516e; its import
    switch waits for LAB1) on planted readers, and never opens an outside-window or sealed day"""
    old = _old_roster_unknown()
    idx = {'20251010': ['BTC', 'ETH'], '20251011': None, '20251012': ['BTC', 'SOL'], '20251013': ['ADA'], '20251014': ['BTC']}
    law = Law({'20251013'}); out = lambda d: d < '20251011'
    for coins, last, ev in ((['BTC'], '20251014', ['20251014']), (['SOL', 'ETH'], '20251014', ['20251012']), (['ADA', 'XYZ'], '20251014', []),
                            (['ETH'], '20251012', ['20251012'])):
        a, b = _R(idx), _R(idx)
        assert S.roster_unknown(a, coins, last, ev, law, out) == old(b, coins, last, ev, law, out)
        assert a.opened == b.opened and '20251013' not in a.opened and '20251010' not in a.opened
    sys.path.insert(0, os.path.join(TOOLS, 'alarm_context'))
    import alarm_context_ed2 as AC                                                     # Context's live (frozen) copy: the same answers
    for coins, ev in ((['ETH', 'XYZ'], []), (['SOL'], ['20251012']), (['BTC', 'ADA'], ['20251014'])):
        a, b = _R(idx), _R(idx)
        assert S.roster_unknown(a, coins, '20251014', ev, law, out) == AC.roster_unknown(b, coins, '20251014', ev, law, out)
        assert a.opened == b.opened


# ------------------------------------------------------------------------------------------------------------------ S3 window first
class NoRead:
    """a Days-like store holding 20251014 and 20251015 (the Cause R2-03 fixture shape): index() of a day outside the allowed days fails"""
    def __init__(self, allowed, days=('20251014', '20251015'), coins=None):
        self.allowed = set(allowed); self._days = list(days); self.opened = []; self.coins = coins or {d: ['BTC'] for d in days}

    def days(self):
        return list(self._days)

    def parts(self, d):
        return ['PRICE'] if d in self._days else []

    def index(self, d, part):
        self.opened.append(d)
        assert d in self.allowed, 'ATTEMPTED_OUTSIDE_CALLER_WINDOW ' + d
        return {'coins': self.coins[d]}


@pytest.mark.parametrize('window,first,last,code', [(('20251015', '20251015'), '20251015', '20251016', 'SELECTION_OUTSIDE_WINDOW'),
                                                    ('20251015..20251015', '20251014', '20251015', 'SELECTION_OUTSIDE_WINDOW'),
                                                    ('20251015,20251014', '20251015', '20251015', 'BAD_WINDOW'),
                                                    ('20251015..2025101', '20251015', '20251015', 'BAD_WINDOW'),
                                                    (('20251301', '20251302'), '20251015', '20251015', 'BAD_WINDOW')])
def test_W1_check_window_refuses_before_reading(window, first, last, code):
    with pytest.raises(S.SelectionRefused) as e:
        S.check_window(first, last, window)
    assert e.value.code == code
    assert S.check_window('20251015', '20251015', '20251015..20251015') == ('20251015', '20251015', ('20251015', '20251015'))
    assert S.check_window('2025-10-15', '20251015', None) == ('20251015', '20251015', None)


def test_W2_cause_r2_03_shape_never_opens_the_day_before():
    """Cause R2-03: a noon event, caller window 20251015..20251015, a store that also holds 20251014. The window-first scan opens only
    20251015; the old rule (every day up to last, the predecessor included) opens 20251014 and is refused by the NoRead store"""
    R = NoRead(allowed={'20251015'})
    coins, read = S.roster_universe(R, '20251015', window=('20251015', '20251015'), law=Law())
    assert read == ['20251015'] and R.opened == ['20251015'] and coins == {'BTC'}
    with pytest.raises(AssertionError, match='ATTEMPTED_OUTSIDE_CALLER_WINDOW 20251014'):
        S.roster_universe(NoRead(allowed={'20251015'}), '20251015', law=Law())        # failing-before: no window = the old scan
    R = NoRead(allowed={'20251015'}, coins={'20251014': ['ETH'], '20251015': ['BTC']})
    assert S.roster_unknown(R, ['BTC', 'ETH'], '20251015', ['20251015'], Law(), window=('20251015', '20251015')) == ['ETH']
    assert R.opened == ['20251015']                                         # ETH lives only on the day before: unknown, never read there
    with pytest.raises(S.SelectionRefused) as e:
        S.roster_unknown(NoRead(allowed=set()), ['BTC'], '20251015', ['20251014'], Law(), window=('20251015', '20251015'))
    assert e.value.code == 'SELECTION_OUTSIDE_WINDOW'


@pytest.mark.parametrize('sel', ['coin:BTC', 'coins:BTC,ETH', 'all', 'list'])
def test_W3_outcomes_a51r2_01_shape_refuses_before_any_read(monkeypatch, sel):
    """Outcomes A51R2-01: request 20251015..20251016 with caller window 20251015 only: SELECTION_OUTSIDE_WINDOW before the list, the
    roster of record, the canonical roster or any PRICE index is opened, for every selector"""
    seen = []
    for name in ('read_list', 'weekly_roster', 'roster_document', 'sha256_file'):
        monkeypatch.setattr(S, name, lambda *a, _n=name, **k: seen.append(_n) or (_ for _ in ()).throw(AssertionError('READ ' + _n)))
    with pytest.raises(S.SelectionRefused) as e:
        S.select(LIST, '20251015', '20251016', sel, subject='A02P', law=Law(), window=('20251015', '20251015'))
    assert e.value.code == 'SELECTION_OUTSIDE_WINDOW' and seen == []
    with pytest.raises(S.SelectionRefused) as e:
        S.resolve_selection({'coin': np.array(['BTC']), 't': np.array([1760572800.0])}, coins='BTC', law=Law(), window='20251015..20251015')
    assert e.value.code == 'SELECTION_OUTSIDE_WINDOW' and seen == []          # 1760572800 = 20251016 00:00 UTC: outside


def test_W4_inside_window_opens_only_window_days(monkeypatch):
    """a request inside the window: the canonical roster's PRICE index pins are rechecked for requested days only, and a roster-of-record
    week stamped before the window is not opened (its days GROUP_NOT_EFFECTIVE)"""
    opened = []; real = S.sha256_file
    monkeypatch.setattr(S, 'sha256_file', lambda p: opened.append(p) or real(p))
    s = S.select(LIST, '20251015', '20251016', 'roster', subject='A02P', law=Law(), window=('20251015', '20251016'))
    days = sorted({p.split('day=', 1)[1][:8] for p in opened if 'day=' in p})
    assert days == ['20251015', '20251016'] and s['request']['window'] == ['20251015', '20251016']
    info = s['coverage']['requested']['roster_of_record']
    assert info['weeks_outside_window'] == ['20251013'] and info['files'] == {}           # its Monday 13 Oct is before the window
    assert s['coverage']['requested']['group_gaps'] == [('20251015', '20251016')] and s['status'] == 'EMPTY_SELECTED_POPULATION'
    t = S.select(LIST, '20251015', '20251016', 'roster', subject='A02P', law=Law(), window=('20251013', '20251016'))
    assert list(t['coverage']['requested']['roster_of_record']['files']) == ['ROSTER_20251013.csv'] and t['rows']


def test_W5_real_store_one_day_window(monkeypatch):
    """the real lab_days PRICE indexes (Oct 2025, research-readable): a one-day window opens that day's index only"""
    from lab3 import days as LD
    seen = []; real = LD.Days.index
    monkeypatch.setattr(LD.Days, 'index', lambda self, d, part: seen.append((str(d), part)) or real(self, d, part))
    coins, read = S.roster_universe(LD.Days('<DATA_ROOT>/lab_days', 'research'), '20251015', window=('20251015', '20251015'))
    assert read == ['20251015'] and seen == [('20251015', 'PRICE')] and 'BTC' in coins
