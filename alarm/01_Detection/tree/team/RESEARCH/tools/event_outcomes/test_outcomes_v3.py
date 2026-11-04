"""Targeted VERSION 3 tests, one block per A51 finding (STRATEGY/LEAD builder, 25 Oct 2026). Planted prices only (a fake price source in
the canonical reader's place); the real-input checks are in acceptance_v3.py. python3 -m pytest -q -p no:cacheprovider test_outcomes_v3.py
Each test names the finding it proves. The reviewed code 2017ed1cc2e4c6dd fails these by construction (it has no run window, no row
embargo, no evidence / funding columns, no stage or manifest); its behaviour on the same cases is recorded in A51_ANSWERS_V3.md."""
import json, math, os, sys
import numpy as np
import pytest
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import event_outcomes as EO
REAL_SOURCE = EO.PriceSource
F = EO.FORENSICS; CODE = os.path.join(F, 'team', 'LAB3', 'code')
T0 = 1760486400                                   # 2025-10-15 00:00:00 UTC (a multiple of 3 s): first grid bar F + 9 s
COST = {'table': 'team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv', 'sha16': 'ff157578098a2f47', 'gap_pct': 0.144}
EXITS = {'path': 'team/RESEARCH/tools/exit_engine/EXITS_V1.tsv', 'sha16': 'db575a2fcb179798'}


class FakeSrc:
    """the canonical PriceSource's interface over planted bars: flat 100 unless plant(te_rel_s) says otherwise; records every read"""
    reads = []

    def __init__(self, lab_root, code_dir, pins=None):
        self.pins = pins; self.pc = type('PC', (), {'reads': 0, 'mem': {}})()

    def state(self, coin, day):
        return FakeSrc.states.get((coin, day), 'LISTED')

    def bars(self, coin, t0, t1):
        FakeSrc.reads.append((coin, t0, t1))
        te = np.arange(t0, t1 + 1, EO.BAR_US, dtype=np.int64); c = np.full(len(te), 100.0); h = c.copy(); l = c.copy()
        FakeSrc.plant(te, c, h, l)
        return te, c, h, l

    def drop_before(self, day):
        pass


@pytest.fixture
def lab(monkeypatch, tmp_path):
    FakeSrc.reads = []; FakeSrc.states = {}; FakeSrc.plant = staticmethod(lambda te, c, h, l: None)
    monkeypatch.setattr(EO, 'PriceSource', FakeSrc)
    monkeypatch.setattr(EO.ES, 'read_inputs', lambda s, *a, **k: {u: np.full(len(a[4]), 1.0) for u in s['inputs']})
    return tmp_path


def settings(tmp, labels, **kw):
    s = dict(name='T3', entry={'delay_s': 6, 'gap_s': 60}, directions=['LONG', 'SHORT'], labels=labels, **kw)
    p = tmp / ('s%d.json' % len(list(tmp.glob('s*.json')))); p.write_text(json.dumps(s)); return str(p)


def events(tmp, rows):
    p = tmp / ('e%d.tsv' % len(list(tmp.glob('e*.tsv')))); p.write_text('coin\tt\tside\n' + ''.join('%s\t%s\t%s\n' % r for r in rows)); return str(p)


def build(tmp, ev, st, first='20251015', last='20251015', window=('20251015', '20251015'), **kw):
    out = str(tmp / 'out'); EO.build('lab', CODE, ev, st, 'T3', first, last, out, run_window=window, log=lambda *a: None, gate=False, **kw)
    return EO_read_raw(out)


def EO_read_raw(out):
    """the written parts through the canonical lab3 reader (no manifest: a worker's view)"""
    sys.path.insert(0, CODE)
    from lab3 import days as LD
    R = LD.Days(out, 'research'); res = {}
    for d in R.days():
        for pt in R.parts(d):
            for code in R.index(d, pt)['readings']:
                rr = R.rows(code, d, R.index(d, pt)['coins'])
                for coin, x in rr.items():
                    for k in range(len(x['as_of_us'])):
                        res.setdefault(code.split('.', 2)[2], {})[(coin, x['as_of_us'][k] // EO.US)] = dict(
                            kind=x['value_kind'][k], v=(None if x['value_bits'][k] is None else float(np.array([x['value_bits'][k]], '<u8').view('<f8')[0])),
                            txt=x['value_txt'][k], why=x['empty_reason'][k], known=x['known_at_us'][k])
    return res


RET5 = dict(name='RET5', kind='return', horizon_min=5, unit='pct')
REACH = dict(name='REACH1', kind='reach', target=1, horizon_min=5, unit='pct')


# ---------------------------------------------------------------- A51-01 clocks
def test_a51_01_label_clock_is_entry_plus_window_and_horizons_are_whole_bars(lab):
    out = build(lab, events(lab, [('BTC', T0, 1)]), settings(lab, [RET5, REACH]))
    ent = (T0 + 9) * EO.US
    assert out['entry__px'][('BTC', T0)]['known'] == ent and out['entry__s'][('BTC', T0)]['v'] == 9.0
    for c in ('RET5__LONG', 'REACH1__LONG', 'REACH1__LONG__t'):
        assert out[c][('BTC', T0)]['known'] == ent + 300 * EO.US
    with pytest.raises(ValueError, match='whole number of 3 s bars'):
        EO.load_settings(settings(lab, [dict(RET5, horizon_min=5 / 60)]))


# ---------------------------------------------------------------- A51-02 missing paths
def test_a51_02_settled_vs_interior_hole_vs_short_tail():
    c = np.full(40, 100.0); h = c.copy(); l = c.copy()
    for a in (c, h, l):
        a[10:35] = np.nan                                              # a 75 s hole from bar 10, the path ends at bar 39
    reach = dict(name='X', kind='reach', target=1, horizon_min=3, unit='pct')     # 60 bars: the path is short
    assert EO.label_path(reach, c, h, l, 0, 100, 1, 1)[2] == 'PATH_GAP'            # undecided before an interior hole
    h[5] = 101.0
    assert EO.label_path(reach, c, h, l, 0, 100, 1, 1)[:2] == (1.0, 15)           # settled before the hole: kept
    c2 = np.full(30, 100.0)
    assert EO.label_path(reach, c2, c2.copy(), c2.copy(), 0, 100, 1, 1)[2] == 'NO_PATH'   # a clean but short path: NO_PATH, not PATH_GAP


def test_a51_02_listing_states_are_named_not_conflated(lab):
    ev = events(lab, [('AAA', T0, 1), ('BBB', T0 + 86400 - 600, 1)])
    FakeSrc.states = {('AAA', '20251015'): 'NO_COIN', ('BBB', '20251016'): 'NO_COIN'}
    out = build(lab, ev, settings(lab, [RET5, dict(RET5, name='RET60', horizon_min=60)]), last='20251015', window=('20251015', '20251016'))
    assert {out[c][('AAA', T0)]['why'] for c in out} == {'NO_COIN'}
    b = ('BBB', T0 + 86400 - 600)
    assert out['RET5__LONG'][b]['why'] == '' and out['RET60__LONG'][b]['why'] == 'NOT_LISTED'
    assert all(t1 < EO.day_start_us('20251016') for _, _, t1 in FakeSrc.reads)                     # an unlisted day is never read


def test_a51_02_cost_fallback_is_unknown_not_a_median(lab):
    lab_c = dict(name='R2C', kind='reach', target=2, horizon_min=5, unit='c')
    out = build(lab, events(lab, [('ZZZNOTACOIN', T0, 1), ('BTC', T0, 1)]), settings(lab, [lab_c], cost=dict(COST, fallback='unknown')))
    z = ('ZZZNOTACOIN', T0)
    assert out['unit__c_fallback'][z]['v'] == 1.0 and out['unit__c'][z]['why'] == 'NO_UNIT:COST_FALLBACK'
    assert out['R2C__LONG'][z]['why'] == 'NO_UNIT:COST_FALLBACK' and out['R2C__LONG'][('BTC', T0)]['kind'] == 1


# ---------------------------------------------------------------- A51-03 inclusive price levels
def test_a51_03_short_exact_level_touch_like_near():
    p0 = 2.96; lv = p0 * (1 - 0.025)
    c = np.full(200, p0); h = c.copy(); l = c.copy(); l[30] = lv
    assert -(l[30] / p0 - 1) * 100 < 2.5                                    # the old ratio rule misses this exact touch
    x = dict(name='X', kind='reach', target=2.5, horizon_min=5, unit='pct')
    assert EO.label_path(x, c, h, l, 0, p0, -1, 1)[:2] == (1.0, 90)


# ---------------------------------------------------------------- A51-04 authorization and embargo
def test_a51_04_per_label_embargo_keeps_the_row_and_never_reads_past_the_window(lab):
    late = T0 + 21 * 3600
    out = build(lab, events(lab, [('BTC', late, 1)]), settings(lab, [RET5, dict(RET5, name='RET240', horizon_min=240)]))
    k = ('BTC', late)
    assert out['RET5__LONG'][k]['kind'] == 1 and out['RET240__LONG'][k]['why'] == 'EMBARGO_SUPPORT'
    assert out['RET240__LONG'][k]['known'] == (late + 9) * EO.US + 240 * 60 * EO.US
    assert FakeSrc.reads and all(t1 < EO.day_start_us('20251016') for _, _, t1 in FakeSrc.reads)


def test_a51_04_canonical_authorization_refuses_before_any_read(lab):
    class DenyOct:
        @staticmethod
        def research_refusal(day):
            return 'FABRICATED DENIAL' if str(day).startswith('202510') else None
    with pytest.raises(EO.Refused, match='OUTCOME_REFUSED'):
        build(lab, events(lab, [('BTC', T0, 1)]), settings(lab, [RET5]), law=DenyOct)
    with pytest.raises(EO.Refused, match='NO_RUN_WINDOW'):
        build(lab, events(lab, [('BTC', T0, 1)]), settings(lab, [RET5]), window=None)
    with pytest.raises(EO.Refused, match='SELECTION_OUTSIDE_WINDOW'):
        build(lab, events(lab, [('BTC', T0, 1)]), settings(lab, [RET5]), window=('20251001', '20251014'))
    assert FakeSrc.reads == []


# ---------------------------------------------------------------- A51-05 exit evidence and companions
def _exit_settings(lab, kind='exit', **kw):
    return settings(lab, [dict(name='X1', kind=kind, exit_id='EXIT_T1')], exits=EXITS, cost=COST, units={'nm': 'EPG:NM'}, **kw)


def test_a51_05_uncertain_path_is_never_a_clean_value(lab):
    def plant(te, c, h, l):
        for a in (c, h, l):
            a[30:60] = np.nan                                              # a 90 s hole inside the hold of a stop / trail row
    FakeSrc.plant = staticmethod(plant)
    out = build(lab, events(lab, [('BTC', T0, 1)]), _exit_settings(lab), epg_root='synthetic')
    k = ('BTC', T0)
    assert out['X1__LONG'][k]['why'] == 'PATH_UNCERTAIN' and out['X1__LONG__path_evidence_status'][k]['txt'] == 'PATH_UNCERTAIN'
    assert out['X1__LONG__hole_bars'][k]['v'] == 30.0 and out['X1__LONG__booked'][k]['kind'] == 1
    assert out['X1__LONG__how'][k]['txt'] == 'time' and out['X1__LONG'][k]['known'] == out['X1__LONG__t'][k]['known'] == (T0 + 9 + 10800) * EO.US


def test_a51_05_unresolved_exit_companions_share_reason_and_clock(lab):
    def plant(te, c, h, l):
        for a in (c, h, l):
            a[3600] = np.nan                                               # the time-limit bar (entry bar 0 + 3600) has no trade: NOPRICE
    FakeSrc.plant = staticmethod(plant)
    out = build(lab, events(lab, [('BTC', T0, 1)]), _exit_settings(lab), epg_root='synthetic')
    k = ('BTC', T0); cols = [c for c in out if c.startswith('X1__LONG')]
    assert len(cols) == 6 and {out[c][k]['why'] for c in cols} == {'NO_PATH'}
    assert {out[c][k]['known'] for c in cols} == {(T0 + 9 + 10800) * EO.US}


def test_a51_05_exit_rows_needing_unbound_inputs_are_refused_before_reads(lab):
    with pytest.raises(ValueError, match='monitor / extreme'):
        EO.load_settings(settings(lab, [dict(name='F1', kind='exit', exit_id='FADE_F1')], exits=EXITS, cost=COST, units={'nm': 'EPG:NM'}))


# ---------------------------------------------------------------- A51-06 money of record
class FakeCosts:
    def __init__(self, missing=False, nocost=False):
        self.missing, self.nocost = missing, nocost

    def trade_cost(self, coin, side, t_in, t_out, size):
        fee, book, gap = (np.nan,) * 3 if self.nocost else (9.0, 2.0, 14.4)
        f = np.nan if self.missing else 0.5 * float(side[0])
        why = 'NO_COST' if self.nocost else ('FUNDING_MISSING' if self.missing else '')
        return dict(fee_bp=np.array([fee]), book_bp=np.array([book]), gap_bp=np.array([gap]), funding_bp=np.array([f]),
                    total_bp=np.array([fee + book + gap + f]), reason=np.array([why], object))


@pytest.mark.parametrize('case', ['complete', 'missing', 'nocost'])
def test_a51_06_money_full_is_the_factory_money_and_never_complete_without_funding(lab, monkeypatch, case):
    import factory_v2 as FX2
    C = FakeCosts(missing=case == 'missing', nocost=case == 'nocost'); monkeypatch.setattr(FX2, 'costs_of', lambda card, cfg: C)
    money = dict(cost_settings={'path': 'team/LAYERS/tools/costs_v2/settings/COSTS_SETTINGS_V1.json', 'sha16': 'd1fd6b14c80717f8'}, size_usd=10000)
    out = build(lab, events(lab, [('BTC', T0, 1)]), _exit_settings(lab, kind='money_full', money=money), epg_root='synthetic')
    k = ('BTC', T0); b = out['X1__LONG__booked'][k]['v']; xu = out['X1__LONG'][k]['known']
    cpct, fok = FX2.trade_cost(C, 'BTC', 1, (T0 + 9) * EO.US, xu, 10000)
    if case == 'complete':
        assert out['X1__LONG'][k]['v'] == b - cpct and out['X1__LONG__funding_ok'][k]['v'] == 1.0
    if case == 'missing':
        assert out['X1__LONG'][k]['why'] == 'FUNDING_MISSING' and out['X1__LONG__funding_ok'][k]['v'] == 0.0 == fok
        assert b - out['X1__LONG__cost_prefunding'][k]['v'] == b - cpct           # the factory's partial net, honestly named
    if case == 'nocost':
        assert out['X1__LONG'][k]['why'] == 'NO_COST' and out['X1__LONG__cost_prefunding'][k]['why'] == 'NO_COST'


def test_a51_06_static_cost_money_is_retired_by_name(lab):
    with pytest.raises(ValueError, match='retired'):
        EO.load_settings(os.path.join(HERE, 'OUTCOMES_CORE_V2.json'))


# ---------------------------------------------------------------- A51-07 input contract, catalog, pins, atomic publication
@pytest.mark.parametrize('bad', [[('BTC', T0, 1), ('btc', T0, 1)], [('BTC', '%d.5' % T0, 1)], [('BTC', T0, 2)], [('B-TC', T0, 1)]])
def test_a51_07_invalid_event_lists_refused_before_any_read(lab, bad):
    with pytest.raises(EO.Refused, match='INVALID_EVENT_LIST'):
        build(lab, events(lab, bad), settings(lab, [RET5]))
    assert FakeSrc.reads == []


def test_a51_07_catalog_units_are_real_and_columns_never_collide(lab):
    s = EO.load_settings(os.path.join(HERE, 'OUTCOMES_CORE_V3.json'))
    units = {c['unit'] for c in EO.column_specs(s)}
    assert units <= {'price', 'seconds', 'pct', 'c', 'nm', 'flag', 'sign', 'count', 'word'} and 'number' not in units
    with pytest.raises(ValueError, match='label names'):
        EO.load_settings(settings(lab, [dict(RET5, name='RET5__LONG')]))


def _run(lab, ev, st, out, **kw):
    return EO.run(0, str(lab / 'lab'), CODE, ev, st, 'T3', '20251015', '20251015', str(out), run_window=('20251015', '20251015'),
                  check_release=False, log=lambda *a: None, **kw)


def test_a51_07_atomic_run_commit_consumer_refusals_and_rerun(lab):
    ev = events(lab, [('BTC', T0, 1), ('ETH', T0 + 60, -1)]); st = settings(lab, [RET5, REACH]); out = lab / 'run'
    m = _run(lab, ev, st, out)
    assert m['status'] == 'COMPLETE' and m['coverage']['events'] == 2 and m['coverage']['cells'] == 2 * len(EO.column_specs(EO.load_settings(st)))
    r = EO.read(str(out), CODE, 'T3')
    assert list(r['RET5__LONG']['coin']) == ['BTC', 'ETH'] and r['RET5__LONG']['unit'] == 'pct'
    assert _run(lab, ev, st, out)['run_id'] == m['run_id']                       # identical rerun: UP TO DATE, nothing written
    with pytest.raises(EO.Refused, match='OUTPUT_EXISTS'):
        _run(lab, ev, settings(lab, [RET5]), out)                              # another run never overwrites a committed one
    os.makedirs(str(out / 'day=20251016' / 'OUT.T3'))
    with pytest.raises(EO.Refused, match='RUN_NOT_COMMITTED'):
        EO.read(str(out), CODE, 'T3')                                          # a mixed root (an uncommitted part beside it) is refused


def test_a51_07_failed_and_interrupted_runs_are_never_consumable(lab):
    ev = events(lab, [('BTC', T0, 1)]); st = settings(lab, [RET5]); out = lab / 'run2'
    def boom(stage):
        raise RuntimeError('interrupted after the freeze')
    with pytest.raises(RuntimeError):
        _run(lab, ev, st, out, hooks={'before_commit': boom})
    assert not out.exists()
    failed = [p for p in lab.iterdir() if p.name.startswith('run2.failed_')]
    assert len(failed) == 1 and (failed[0] / 'FAILED.json').exists()
    with pytest.raises(EO.Refused, match='RUN_NOT_COMMITTED'):
        EO.read(str(failed[0]), CODE, 'T3')
    assert _run(lab, ev, st, out)['status'] == 'COMPLETE'                       # the restart of the same request commits


@pytest.mark.parametrize('what', ['settings', 'code'])
def test_a51_07_a_change_after_the_freeze_refuses_before_reading(lab, what):
    ev = events(lab, [('BTC', T0, 1)]); st = settings(lab, [RET5]); out = lab / ('run_' + what)
    def tamper(stage):
        p = os.path.join(stage, EO.FROZEN); h = json.load(open(p))
        if what == 'settings':
            open(st, 'a').write(' ')                                       # the settings file changes after the freeze
        else:
            k = sorted(h['frozen']['inventory'])[0]; h['frozen']['inventory'][k] = '0' * 16   # the frozen code differs from the code run
            json.dump(h, open(p, 'w'))
    with pytest.raises(EO.Refused, match='INPUT_CHANGED|CODE_CHANGED'):
        _run(lab, ev, st, out, hooks={'after_freeze': tamper})
    assert FakeSrc.reads == [] and not out.exists()


def test_a51_07_a_price_partition_changed_after_the_freeze_is_refused_before_its_bins():
    src = REAL_SOURCE.__new__(REAL_SOURCE)
    src.pins = {'20251015': 'aaaaaaaaaaaaaaaa'}; src.seen = {}; src.listed = {}
    src.pc = type('PC', (), {'R': type('R', (), {'index': staticmethod(lambda d, p: {'_sha16': 'bbbbbbbbbbbbbbbb', 'coins': ['BTC']})})()})()
    with pytest.raises(EO.Refused, match='INPUT_CHANGED'):
        src.state('BTC', '20251015')


def test_a51_07_zero_event_selection_commits_an_empty_run(lab):
    ev = events(lab, [('BTC', T0 + 5 * 86400, 1)]); out = lab / 'empty'
    m = _run(lab, ev, settings(lab, [RET5]), out)
    assert m['status'] == 'COMPLETE' and m['coverage']['events'] == 0 and m['parts'] == {} and FakeSrc.reads == []


# ---------------------------------------------------------------- A51R (re-review V2) fixes
def _custom_cost(lab):
    p = lab / 'cost.tsv'; p.write_bytes(open(os.path.join(F, COST['table']), 'rb').read()); return p


def _bump(p, coin='BTC', col=4, by=10.0):
    rows = p.read_text().splitlines()
    for i, line in enumerate(rows):
        if line.startswith(coin + '\t'):
            f = line.split('\t'); f[col] = str(float(f[col]) + by); rows[i] = '\t'.join(f)
    p.write_text('\n'.join(rows) + '\n')


def test_a51r_01_unchanged_custom_cost_table_commits(lab):
    cost = _custom_cost(lab)
    st = settings(lab, [dict(name='RETC', kind='return', horizon_min=3, unit='c')], cost=dict(table=str(cost), sha16=EO.ids.sha16_file(str(cost)), gap_pct=0.144))
    m = _run(lab, events(lab, [('BTC', T0, 1)]), st, lab / 'ok')
    assert m['status'] == 'COMPLETE' and m['frozen']['config']['cost_table']['sha16'] == EO.ids.sha16_file(str(cost))


@pytest.mark.parametrize('when', ['after_freeze', 'before_commit'])
def test_a51r_01_custom_cost_table_change_refused_and_never_published(lab, when):
    cost = _custom_cost(lab)
    st = settings(lab, [dict(name='RETC', kind='return', horizon_min=3, unit='c')], cost=dict(table=str(cost), sha16=EO.ids.sha16_file(str(cost)), gap_pct=0.144))
    with pytest.raises(EO.Refused, match='INPUT_CHANGED'):
        _run(lab, events(lab, [('BTC', T0, 1)]), st, lab / 'drift', hooks={when: lambda stage: _bump(cost)})
    assert not (lab / 'drift').exists() and [p for p in lab.iterdir() if p.name.startswith('drift.failed_')]
    if when == 'after_freeze':
        assert FakeSrc.reads == []                                           # refused before the worker read anything


def test_a51r_01_exits_registry_and_cost_settings_tables_are_pinned(lab, monkeypatch):
    import factory_v2 as FX2, shutil
    monkeypatch.setattr(FX2, 'costs_of', lambda card, cfg: FakeCosts())
    ex = lab / 'EXITS.tsv'; shutil.copy(os.path.join(F, EXITS['path']), str(ex))
    S = json.load(open(os.path.join(F, 'team/LAYERS/tools/costs_v2/settings/COSTS_SETTINGS_V1.json')))
    for k in ('table_v1', 'table_v4'):
        q = lab / ('%s.tsv' % k); shutil.copy(os.path.join(F, S[k]['path']), str(q)); S[k]['path'] = str(q)
    cs = lab / 'cs.json'; cs.write_text(json.dumps(S))
    money = dict(cost_settings={'path': str(cs), 'sha16': EO.ids.sha16_file(str(cs))}, size_usd=10000)
    st = settings(lab, [dict(name='M1', kind='money_full', exit_id='EXIT_T1')], exits={'path': str(ex), 'sha16': EO.ids.sha16_file(str(ex))},
                  cost=COST, units={'nm': 'EPG:NM'}, money=money)
    conf = EO.preflight(str(lab / 'lab'), CODE, events(lab, [('BTC', T0, 1)]), st, 'T3', '20251015', '20251015', ('20251015', '20251015'),
                        roots={'EPG': str(lab)}, check_release=False)[2]['config']
    assert {'settings', 'events', 'law', 'windows', 'cost_table', 'exits', 'cost_settings', 'cost_settings:table_v1', 'cost_settings:table_v4'} <= set(conf)
    for target in (ex, lab / 'table_v4.tsv'):
        before = target.read_bytes(); target.write_bytes(before + b'\n')
        with pytest.raises(EO.Refused, match='INPUT_CHANGED'):
            EO.check_config(conf, 'test')
        target.write_bytes(before)
    EO.check_config(conf, 'test')


def test_a51r_06_fee_book_gap_are_separate_columns(lab, monkeypatch):
    import factory_v2 as FX2
    monkeypatch.setattr(FX2, 'costs_of', lambda card, cfg: FakeCosts())
    money = dict(cost_settings={'path': 'team/LAYERS/tools/costs_v2/settings/COSTS_SETTINGS_V1.json', 'sha16': 'd1fd6b14c80717f8'}, size_usd=10000)
    out = build(lab, events(lab, [('BTC', T0, 1)]), _exit_settings(lab, kind='money_full', money=money), epg_root='synthetic')
    k = ('BTC', T0); g = lambda c: out['X1__LONG__' + c][k]['v']
    assert (g('fee'), g('book'), g('gap')) == (9.0 / 100, 2.0 / 100, 14.4 / 100) and abs(g('fee') + g('book') + g('gap') - g('cost_prefunding')) < 1e-12


def test_c1_coin_selector_filters_validates_and_refuses_groups(lab, monkeypatch):
    monkeypatch.setattr(EO, 'roster_of', lambda *a: ({'BTC', 'ETH', 'DOGE'}, {}))
    ev = events(lab, [('BTC', T0, 1), ('ETH', T0 + 60, -1)]); st = settings(lab, [RET5])
    m = _run(lab, ev, st, lab / 'sel', coins='BTC')
    assert m['selection']['selector'] == {'kind': 'coins', 'coins': ['BTC']} and m['coverage']['events'] == 1
    assert _run(lab, ev, st, lab / 'sel_empty', coins='DOGE')['coverage']['events'] == 0          # on the roster, no event: an empty success
    with pytest.raises(EO.Refused, match='UNKNOWN_COIN'):
        _run(lab, ev, st, lab / 'sel_bad', coins='NOPE')
    with pytest.raises(EO.Refused, match='SELECTOR_NOT_RELEASED'):
        _run(lab, ev, st, lab / 'sel_grp', group='MAJORS', group_file=str(lab / 'g.tsv'))


def test_a51r_event_loader_equals_event_profile_contract(tmp_path):
    """Outcomes no longer imports event_profile (A51R fix check 3); its strict loader must equal event_profile.load_alarms on the real
    A02P list and refuse the same malformed lists"""
    sys.path.insert(0, os.path.join(EO.TOOLS, 'event_profile'))
    import event_profile as EP
    real = '<SCRATCH>/work_LEAD/ed2/epg/A02P_EPG_INPUT.tsv'
    if os.path.exists(real):
        a, b = EO.load_events(real), EP.load_alarms(real)
        assert set(a) == set(b) and all(np.array_equal(a[k], b[k]) for k in a) and len(a['t']) == 8158
    for rows in (['BTC\t%d\t1' % T0, 'btc\t%d\t1' % T0], ['BTC\t%d.5\t1' % T0], ['BTC\t1760486400.0000001\t1'], ['BTC\t%d\t2' % T0],
                 ['B-TC\t%d\t1' % T0], ['BTC\tnan\t1'], ['BTC\t-5\t1']):
        p = tmp_path / 'bad.tsv'; p.write_text('coin\tt\tside\n' + '\n'.join(rows) + '\n')
        with pytest.raises(EO.Refused, match='INVALID_EVENT_LIST'):
            EO.load_events(str(p))
        with pytest.raises(ValueError):
            EP.load_alarms(str(p))
    p = tmp_path / 'ok.tsv'; p.write_text('coin\tt\tside\tonset_t\nBTC\t%d\t\t%d\nETH\t%d.0\t-1\t\n' % (T0, T0 - 5, T0 + 3))
    a, b = EO.load_events(str(p)), EP.load_alarms(str(p))
    assert all(np.array_equal(a[k], b[k]) for k in ('coin', 't', 'side', 'onset_t'))
