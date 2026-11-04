"""test_detect_v2.py: the tests of idea_to_grade/detect_v2.py. Owner STRATEGY/LEAD (i2g_detector's tests). New edition by SCOUT for the
clean release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release folder only"). Old file: test_detect.py
ef3b5e9a5d1c189e (the tests of detect.py 5ced7c1a40356a7f), never edited, never read here. Its tests are here as written, against
detect_v2, except where the old contract is the subject: the import; K5's pinned names (detect_v2.py, alarm_design_v3.py); K1/K6's
commands name --lab-root (now required; every refusal there comes before any read); the hard kill starts detect_v2.py with --lab-root;
the REAL tests read the lab days from LAB_DAYS in the environment (the settings key; for this test process: run()'s default lab_root),
and are skipped without it (they also read the outside team's committed outputs, which only the dev tree has). The tests of the new path
code (--gate, --lab-root) are at the end. Run it in its own process:
  cd <this folder> && python3 -B -m pytest -q -p no:cacheprovider test_detect_v2.py      (LAB_DAYS=<lab days> for the REAL tests)
The rest of this text is test_detect.py's: test_detect.py (i2g_detector for STRATEGY/LEAD, 25 Oct 2026): small proofs of
idea_to_grade/detect.py (research-tool-testing V1.11).
Run: cd team/RESEARCH/tools/idea_to_grade && PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 nice -n 10 python3 -B -m pytest -q -p no:cacheprovider test_detect.py
PLANTED (exact answers by hand, a fake lab3 reader with the real index/field schema): threshold boundary, onset, unknown predecessor,
quality gates e/a/o/k, a fire at 23:59 and the next day's 00:00 onset from D-1's data, refractory across chunk boundaries, NOT_LISTED,
NOT_BUILT, HOLE census, GRID == the engine's own BASE path.
REAL (the lab store, small): the outside committed outputs decoded HERE with the standard library (never through detect.py): BN_OI 3 coins x
3 days vs the outside full-period VIEW; the three outside clock ideas (flow 5 s, book 30 s with a constant side, funding 60 s with k) vs
their events.tsv and masks; GRID == BASE; serial == 2 processes; selectors (one coin, a set, a named group, all) and refusals; the roster
census (NOT_LISTED PRICE cells); look-ahead: a huge value planted after T changes no event at or before T (labcore future_plant_check)
and a run ending a day earlier gives the same events (prefix by day)."""
import base64, csv, glob, gzip, inspect, json, os, sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import detect_v2 as DT                                                   # noqa: E402
from labcore import lookahead as LK                                      # noqa: E402
from lab3 import days as LD                                              # noqa: E402

F = DT.F_ROOT
OUT = F / 'team' / 'OUTSIDE'
DEF_OI = OUT / 'CODE2' / 'fresh_grading_t2_v1' / 'BN_OI_CONTRACTION_1PCT_10M_T2_V1.json'
ROSTER = OUT / 'COORD' / 'development' / 'DEV2' / 'a02p_chain_v1' / 'full_population' / 'ROSTER_BUILD.json'
VIEW3 = OUT / 'COORD' / 'development' / 'grading_bridge_v1' / 'new_oi_full3_parallel_v1' / 'detection' / 'VIEW.json'
SMALL = OUT / 'COORD' / 'development' / 'DEV2' / 'graded_input_preparation_v1'
SECTORS = F / 'team' / 'RESEARCH' / 'tools' / 'cause_label' / 'SECTORS_V1.tsv'
W = '20250901:20260228'                                                     # the caller's research window (BUILD months)
LAB_DAYS = os.environ.get('LAB_DAYS', '')        # the REAL tests' lab days: the settings key LAB_DAYS, given in the environment


@pytest.fixture(autouse=True)
def _lab_days_of_real_tests(request, monkeypatch):
    """the REAL tests (and the hard kill) read the lab days: LAB_DAYS as run()'s default lab_root in this test process; skipped without it"""
    if 'real' in request.node.name or 'hard_kill' in request.node.name:
        if not LAB_DAYS:
            pytest.skip('REAL: needs LAB_DAYS (the settings key) and the outside outputs of the dev tree')
        names = list(inspect.signature(DT.run).parameters); d = list(DT.run.__defaults__)
        d[names[-len(d):].index('lab_root')] = LAB_DAYS
        monkeypatch.setattr(DT.run, '__defaults__', tuple(d))
    yield


def rows(p):
    with open(p) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def events(run_json):
    return [(r['coin'], int(r['t']), int(r['side'])) for r in rows(Path(run_json).parent / 'EVENTS.tsv')]


def cells(run_json):
    return {(r['coin'], r['day']): r for r in rows(Path(run_json).parent / 'COVERAGE.tsv')}


# ================================================================= PLANTED: a fake lab3 reader (real schema, hand-made values)
NotBuilt = LD.NotBuilt                                                   # lab3's own absence class (clock_series.is_absence checks the class)


D1, D2, D3, D4 = '20251101', '20251102', '20251103', '20251104'
COINS = ['XX', 'YY', 'ZZ']
N = 1440


def day0(d):
    return DT.engine().day0(d)


class FakeDays:
    """E2.S04 at 60 s (fields v, a, e, o, k) built on D1..D3 (D4: PRICE built, BASE not built; D0 and earlier: nothing built)"""

    def __init__(self):
        self.v, self.q = {}, {}
        for d in (D1, D2, D3):
            v = np.zeros((3, N)); v[2] = np.nan                         # ZZ: never a value (HOLE)
            e = np.zeros((3, N), np.uint8); a = np.zeros((3, N), np.int32); o = np.zeros((3, N), np.int64)
            k = np.broadcast_to((day0(d) + 60 * np.arange(N, dtype=np.int64)) * 1_000_000, (3, N)).copy()
            self.v[d] = v; self.q[d] = {'e': e, 'a': a, 'o': o, 'k': k}
        v, q = self.v[D1], self.q[D1]
        for coin in (0, 1):                                              # XX and YY share day 1
            v[coin, 100] = -1.0                                          # equal to the threshold: not < -1, no fire
            v[coin, 200] = -1.0001; v[coin, 201] = -2                    # fire at 200 (onset), none at 201
            v[coin, 300] = np.nan; v[coin, 301] = -2; v[coin, 302] = -2  # unknown, then no onset after an unknown step
            v[coin, 400] = -2; q['e'][coin, 400] = 1; v[coin, 401] = -2  # e != 0: unknown
            v[coin, 500] = -2; q['k'][coin, 500] += 1; v[coin, 501] = -2  # known 1 us after its column time: unknown
            v[coin, 700] = -2; q['a'][coin, 700] = -1; v[coin, 701] = -2  # a < 0: unknown
            v[coin, 800] = -2; q['o'][coin, 800] = -1; v[coin, 801] = -2  # o < 0: unknown
            v[coin, 600] = -2; v[coin, 605] = -2; v[coin, 611] = -2      # three onsets (refractory 600 s drops 605)
            v[coin, 1439] = -2                                           # 23:59 fire
        self.v[D2][0, 2] = -3; self.v[D2][0, 0] = -2                    # XX: 00:00 continues 23:59 (no onset), 00:02 fires
        self.v[D2][1, :] = -2                                            # YY: day 2 all true but PRICE does not list YY
        self.v[D3][0, 0] = -2                                            # XX: 00:00 onset from D2's 23:59 (0, known)
        self.v[D3][1, 5] = -2                                            # YY: 00:05 onset

    def index(self, day, part):
        if part == 'PRICE':
            if day not in (D1, D2, D3, D4):
                raise NotBuilt(day)
            return {'coins': ['XX', 'ZZ'] if day == D2 else list(COINS), '_sha16': 'price' + day}
        if part != 'BASE' or day not in self.v:
            raise NotBuilt(day)
        return {'coins': list(COINS), '_sha16': 'base' + day,
                'readings': {'E2.S04': {'kind': 'CLOCK', 'step': 60, 'files': {f: 'x' for f in 'vaeok'}, 'shape': [3, N]}}}

    def part_of(self, code, day):
        if code != 'E2.S04' or day not in self.v:
            raise NotBuilt('%s %s' % (code, day))
        return 'BASE'

    def step(self, code, day):
        return 60

    def read(self, code, field, days, coins):
        d = days[0]; src = self.v[d] if field == 'v' else self.q[d][field]
        out = np.full((1, len(coins), N), LD.ABSENT[field], LD.DTYPE[field])
        for i, c in enumerate(coins):
            if c in COINS:
                out[0, i] = src[COINS.index(c)]
        return out


def planted_def(tmp_path, refractory):
    d = json.loads(DEF_OI.read_text()); d['fire']['refractory_s'] = refractory
    d['window'] = {'first': '20250901', 'last': '20260228'}; d['id'] = 'PLANTED_R%d' % refractory
    p = tmp_path / ('planted_r%d.json' % refractory); p.write_text(json.dumps(d)); return p


@pytest.fixture
def fake_roster(tmp_path):
    p = tmp_path / 'roster.tsv'; p.write_text('coin\n' + '\n'.join(COINS) + '\n'); return p


def expected_fires(refractory):
    x = [(D1, c) for c in (200, 600, 605, 611, 1439)] + [(D2, 2), (D3, 0)]
    y = [(D1, c) for c in (200, 600, 605, 611, 1439)] + [(D3, 5)]
    if refractory == 600:
        x = [(D1, c) for c in (200, 600, 611, 1439)] + [(D3, 0)]      # 605: 5 min after 600; D2 00:02: 3 min after D1 23:59
        y = [(D1, c) for c in (200, 600, 611, 1439)] + [(D3, 5)]
    return sorted([('XX', day0(d) + 60 * c, -1) for d, c in x] + [('YY', day0(d) + 60 * c, -1) for d, c in y])


EXPECTED_CELLS = {  # (coin, day): (status, reason, slots, known_slots, predecessor_known, full_known)
    ('XX', D1): ('PRESENT', '', '1440', '1435', '0', '0'), ('YY', D1): ('PRESENT', '', '1440', '1435', '0', '0'),
    ('ZZ', D1): ('HOLE', 'no known slot', '1440', '0', '0', '0'),
    ('XX', D2): ('PRESENT', '', '1440', '1440', '1', '1'), ('YY', D2): ('NOT_LISTED', 'PRICE', '', '', '', '0'),
    ('ZZ', D2): ('HOLE', 'no known slot', '1440', '0', '0', '0'),
    ('XX', D3): ('PRESENT', '', '1440', '1440', '1', '1'), ('YY', D3): ('PRESENT', '', '1440', '1440', '1', '1'),
    ('ZZ', D3): ('HOLE', 'no known slot', '1440', '0', '0', '0'),
    ('XX', D4): ('NOT_BUILT', 'E2.S04', '1440', '0', '1', '0'), ('YY', D4): ('NOT_BUILT', 'E2.S04', '1440', '0', '1', '0'),
    ('ZZ', D4): ('NOT_BUILT', 'E2.S04', '1440', '0', '0', '0')}


@pytest.mark.parametrize('refractory,workers,path', [(0, 1, None), (600, 1, None), (600, 4, None), (0, 4, 'BASE'), (600, 4, 'BASE')])
def test_planted_exact(tmp_path, fake_roster, refractory, workers, path):
    """hand answers: every fire, every coin-day status and knownness; 4 workers = 4 one-day chunks (refractory merged across them);
    BASE = the engine's own Ctx/find_fires on its 5 s clock gives the same answer as the GRID path"""
    p = DT.run(planted_def(tmp_path, refractory), D1, D4, tmp_path / 'run', fake_roster, research_window=W, workers=workers, _reader=FakeDays(), _path=path)
    assert sorted(events(p)) == expected_fires(refractory)
    got = {k: (r['status'], r['reason'], r['slots'], r['known_slots'], r['predecessor_known'], r['full_known']) for k, r in cells(p).items()}
    assert got == EXPECTED_CELLS
    m = json.loads(Path(p).read_text())
    assert m['status'] == 'COMPLETE' and m['test_hooks'] and m['events'] == len(expected_fires(refractory))
    assert m['execution_path'] == (path or 'GRID') and m['side'] == {'input': 'metric', 'sign': 1} and m['grid_s'] == 60
    ev = rows(Path(p).parent / 'EVENTS.tsv')
    assert all(r['onset_t'] == r['t'] and r['trigger'] == 'E2.S04' and len(r['event_id']) == 16 for r in ev)


def test_planted_checker_catches_a_wrong_answer(tmp_path, fake_roster):
    """the comparison is not vacuous: one planted value moved makes the hand answer fail"""
    fk = FakeDays(); fk.v[D1][0, 200] = -1.0                           # now equal to the threshold: the 200 fire must vanish
    p = DT.run(planted_def(tmp_path, 0), D1, D4, tmp_path / 'run', fake_roster, research_window=W, workers=1, _reader=fk)
    assert sorted(events(p)) != expected_fires(0)
    assert ('XX', day0(D1) + 200 * 60, -1) not in events(p)


def test_refusals(tmp_path, fake_roster):
    d = planted_def(tmp_path, 0)
    with pytest.raises(DT.Refusal, match='WORKERS'):
        DT.run(d, D1, D1, tmp_path / 'a', fake_roster, research_window=W, workers=9, _reader=FakeDays())
    with pytest.raises(DT.Refusal, match='UNKNOWN_COIN'):
        DT.run(d, D1, D1, tmp_path / 'b', fake_roster, coins='XX,QQ', research_window=W, workers=1, _reader=FakeDays())
    with pytest.raises(DT.Refusal, match='BAD_DAYS'):
        DT.run(d, D2, D1, tmp_path / 'c', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    (tmp_path / 'exists').mkdir()
    with pytest.raises(DT.Refusal, match='OUTPUT_EXISTS'):
        DT.run(d, D1, D1, tmp_path / 'exists', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    w = json.loads(d.read_text()); w['window'] = {'first': D2, 'last': D3}; (tmp_path / 'w.json').write_text(json.dumps(w))
    with pytest.raises(DT.Refusal, match='DEFINITION_WINDOW'):
        DT.run(tmp_path / 'w.json', D1, D1, tmp_path / 'e', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    bad = json.loads(d.read_text()); bad['inputs']['metric']['op'] = 'teleport'; (tmp_path / 'bad.json').write_text(json.dumps(bad))
    with pytest.raises(DT.Refusal, match='UNSUPPORTED_OP'):
        DT.run(tmp_path / 'bad.json', D1, D1, tmp_path / 'f', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    nf = json.loads(d.read_text()); nf['conditions'][0]['rhs'] = 'nothing'; (tmp_path / 'nf.json').write_text(json.dumps(nf))
    with pytest.raises(DT.Refusal, match='UNKNOWN_INPUT'):
        DT.run(tmp_path / 'nf.json', D1, D1, tmp_path / 'g', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    assert not any((tmp_path / x).exists() for x in 'abcefg')               # a refusal commits nothing


# ================================================================= REAL: the lab store, small
def outside_view():
    e = json.load(open(VIEW3)); return json.loads(gzip.decompress(base64.b85decode(e['payload_base85'])))


def test_real_oi_three_coins_vs_outside_view(tmp_path):
    """BN_OI (E2.S04, 60 s) BTC/ETH/SOL 20251010..20251012 (a busy stretch) vs the outside committed full-period VIEW, decoded here"""
    first, last = '20251010', '20251012'
    p = DT.run(DEF_OI, first, last, tmp_path / 'run', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1)
    v = outside_view()
    want = sorted((c, int(t), int(s)) for c, t, s, d in v['events'] if first <= d <= last)
    assert len(want) >= 10 and sorted(events(p)) == want
    oc = {(c['coin'], c['day']): (str(c['known_slots']), str((c['predecessor'] >> 3) & 1)) for c in v['cells'] if first <= c['day'] <= last}
    assert {k: (r['known_slots'], r['predecessor_known']) for k, r in cells(p).items()} == oc


@pytest.mark.parametrize('case,coins,first,last', [('flow_parent_first_day_v1', 'ETH', '20250924', '20250924'),
                                                   ('book_first_declared_case_v1', 'BTC,ETH', '20251015', '20251016'),
                                                   ('funding_first_declared_case_v1', 'BTC,ETH,SOL', '20260115', '20260116')])
def test_real_other_clocks_vs_outside(tmp_path, case, coins, first, last):
    """three outside ideas on other metrics and clocks (B1.S09 5 s; C12.S02 30 s, constant side, 2 unknown slots; E1.S01 60 s with k):
    every event and every coin-day's knownness equal to their committed events.tsv and masks"""
    p = DT.run(SMALL / case / 'definition.json', first, last, tmp_path / 'run', ROSTER, coins=coins, research_window=W, workers=1)
    want = sorted((r['coin'], int(r['t']), int(r['side'])) for r in rows(SMALL / case / 'events.tsv'))
    assert sorted(events(p)) == want
    got = cells(p)
    for mp in glob.glob(str(SMALL / case / 'masks_*.tsv')):
        R = rows(mp); dd, coin = R[0]['day'], R[0]['coin']; d0 = day0(dd)
        assert int(got[(coin, dd)]['known_slots']) == sum(int(r['known']) for r in R if int(r['t']) >= d0)
        assert int(got[(coin, dd)]['predecessor_known']) == max(int(r['known']) for r in R if int(r['t']) < d0)


def test_real_grid_equals_base_and_parallel_equals_serial(tmp_path):
    """the GRID path equals the engine's own BASE path on a real day; 2 real worker processes equal one serial run"""
    a = DT.run(DEF_OI, '20251010', '20251010', tmp_path / 'grid', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1)
    b = DT.run(DEF_OI, '20251010', '20251010', tmp_path / 'base', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1, _path='BASE')
    assert events(a) == events(b) and len(events(a)) > 0 and cells(a) == cells(b)
    s = DT.run(DEF_OI, '20251009', '20251012', tmp_path / 'serial', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1)
    q = DT.run(DEF_OI, '20251009', '20251012', tmp_path / 'par', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=2)
    assert events(s) == events(q) and cells(s) == cells(q)
    m = json.loads(Path(q).read_text())
    assert m['workers']['processes'] == 2 and m['workers']['nice'] and min(m['workers']['nice']) >= 10
    for n in ('EVENTS.tsv', 'COVERAGE.tsv'):
        assert (Path(s).parent / n).read_text() == (Path(q).parent / n).read_text()


def test_real_selectors_and_census(tmp_path):
    """one coin, a set, a named group (SECTORS_V1 PRIVACY), all coins on one real day: each is the matching slice of the all-coin run;
    the census holds every requested coin-day; LIT and ASTER (not yet in PRICE on 20250912) are NOT_LISTED PRICE, never dropped"""
    day = '20250912'
    al = DT.run(DEF_OI, day, day, tmp_path / 'all', ROSTER, coins='ALL', research_window=W, workers=1)
    roster = json.loads(ROSTER.read_text())['coins']
    ca = cells(al); ea = events(al)
    assert set(ca) == {(c, day) for c in roster}
    assert ca[('LIT', day)]['status'] == 'NOT_LISTED' and ca[('LIT', day)]['reason'] == 'PRICE'
    assert ca[('ASTER', day)]['status'] == 'NOT_LISTED'
    one = DT.run(DEF_OI, day, day, tmp_path / 'one', ROSTER, coins='BTC', research_window=W, workers=1)
    assert events(one) == [e for e in ea if e[0] == 'BTC'] and set(cells(one)) == {('BTC', day)}
    st = DT.run(DEF_OI, day, day, tmp_path / 'set', ROSTER, coins='SOL,BTC', research_window=W, workers=1)
    assert events(st) == [e for e in ea if e[0] in ('BTC', 'SOL')]
    g = DT.run(DEF_OI, day, day, tmp_path / 'grp', ROSTER, coins=None, group='PRIVACY', group_file=SECTORS, research_window=W, workers=1)
    mg = json.loads(Path(g).read_text())
    assert mg['selection']['kind'] == 'group' and set(mg['coins']) == {'XMR', 'ZEC', 'DASH'}
    assert events(g) == [e for e in ea if e[0] in ('XMR', 'ZEC', 'DASH')]
    with pytest.raises(DT.Refusal, match='UNKNOWN_GROUP'):
        DT.run(DEF_OI, day, day, tmp_path / 'g2', ROSTER, coins=None, group='NOPE', group_file=SECTORS, research_window=W, workers=1)
    with pytest.raises(DT.Refusal, match='BAD_SELECTION'):
        DT.run(DEF_OI, day, day, tmp_path / 'g3', ROSTER, coins='BTC', group='PRIVACY', group_file=SECTORS, research_window=W, workers=1)


class PlantDays:
    """the real lab3 reader, with every stored value AFTER plant_us replaced by a huge one (-1e9 / +1e9 alternating by column: the OI rule
    turns on and off at every step, so the plant adds many fires after plant_us)"""

    def __init__(self, plant_us):
        self.R = LD.Days(LAB_DAYS, 'research'); self.plant_us = plant_us

    def __getattr__(self, k):
        return getattr(self.R, k)

    def read(self, code, field, days, coins):
        x = self.R.read(code, field, days, coins)
        if field == 'v' and self.plant_us is not None:
            step = int(self.R.step(code, days[0]))
            t = (day0(days[0]) + step * np.arange(x.shape[2], dtype=np.int64)) * 1_000_000
            x = np.array(x, copy=True); j = np.arange(x.shape[2])
            x[:, :, (t > self.plant_us) & (j % 2 == 0)] = -1e9; x[:, :, (t > self.plant_us) & (j % 2 == 1)] = 1e9
        return x


def test_real_future_plant_and_prefix(tmp_path):
    """look-ahead (labcore.lookahead.future_plant_check): a huge value planted just after T (20251010 12:00Z) changes no event at or
    before T, while it does add events after T; prefix by day: a run ending 20251010 gives the same 20251010 events"""
    n = {'k': 0}

    def fn(data):
        n['k'] += 1
        p = DT.run(DEF_OI, '20251010', '20251011', tmp_path / ('r%d' % n['k']), ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1,
                   _reader=PlantDays(data['plant_us']))
        ev = events(p)
        return {'coin': np.array([e[0] for e in ev]), 't': np.array([e[1] for e in ev], np.int64), 'side': np.array([e[2] for e in ev]),
                'known_at_us': np.array([e[1] for e in ev], np.int64) * 1_000_000}
    T = (day0('20251010') + 12 * 3600) * 1_000_000
    assert LK.future_plant_check(fn, {'plant_us': None}, lambda d, t: dict(d, plant_us=t), T) == []
    full, planted = fn({'plant_us': None}), fn({'plant_us': T})
    assert len(planted['t']) > len(full['t'])                            # the plant was real: it adds fires after T
    assert set(map(tuple, zip(planted['coin'], planted['t']))) >= {(c, t) for c, t in zip(full['coin'], full['t']) if t * 1_000_000 <= T}
    short = DT.run(DEF_OI, '20251010', '20251010', tmp_path / 'short', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1)
    lo, hi = day0('20251010'), day0('20251011')
    assert events(short) == [e for e in zip(full['coin'], full['t'].tolist(), full['side'].tolist()) if lo <= e[1] < hi]


@pytest.mark.parametrize('extra,cond', [({'chg': {'op': 'change', 'of': 'metric', 'w_s': 3600}}, {'lhs': 'chg', 'cmp': '<', 'rhs': -1.5}),
                                        ({'p05': {'op': 'trail_pct', 'of': 'metric', 'w_s': 86400, 'q': 5}},
                                         {'lhs': 'metric', 'cmp': '<', 'rhs': 'p05'})])
def test_real_window_ops_serial_equals_chunked(tmp_path, extra, cond):
    """BASE path ops the outside never ran (a 1 h change; a trailing 1-day 5th percentile kept across days): 3 one-day-plus chunks in
    3 processes equal one serial run (warm-up days rebuild the percentile history; D-1 beside each day), and both have fires"""
    d = json.loads(DEF_OI.read_text()); d['inputs'].update(extra); d['id'] = 'WINDOW_' + list(extra)[0]
    d['conditions'] = [d['conditions'][0], dict(cond, name='window op', role='claim')]
    p = tmp_path / 'w.json'; p.write_text(json.dumps(d))
    s = DT.run(p, '20251009', '20251011', tmp_path / 'serial', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=1)
    q = DT.run(p, '20251009', '20251011', tmp_path / 'par', ROSTER, coins='BTC,ETH,SOL', research_window=W, workers=3)
    ms = json.loads(Path(s).read_text())
    assert ms['execution_path'] == 'BASE' and len(events(s)) > 0
    assert events(s) == events(q) and cells(s) == cells(q)


# ================================================================= percentile history across chunks: entries, never calendar days
class FakeStore:
    """a fake lab3 reader with the real schema over many days: PRICE lists `price[day]`; BASE holds E2.S04 (60 s; v, a, e, o) on
    base_days; values[(coin, day)] (1440,) else NaN"""

    def __init__(self, price, values, base_days, coins):
        self.price, self.values, self.base, self.coins = price, values, set(base_days), list(coins)

    def index(self, day, part):
        if part == 'PRICE' and day in self.price:
            return {'coins': list(self.price[day]), '_sha16': 'p' + day}
        if part == 'BASE' and day in self.base:
            return {'coins': self.coins, '_sha16': 'b' + day,
                    'readings': {'E2.S04': {'kind': 'CLOCK', 'step': 60, 'files': {f: 'x' for f in 'vaeo'}}}}
        raise NotBuilt('%s %s' % (part, day))

    def part_of(self, code, day):
        if code != 'E2.S04' or day not in self.base:
            raise NotBuilt('%s %s' % (code, day))
        return 'BASE'

    def step(self, code, day):
        return 60

    def read(self, code, field, days, coins):
        out = np.full((1, len(coins), N), LD.ABSENT[field], LD.DTYPE[field])
        for i, c in enumerate(coins):
            if c in self.coins:
                out[0, i] = self.values.get((c, days[0]), np.full(N, np.nan)) if field == 'v' else 0
        return out


def gap_store():
    """XX is listed on A and A+1, then NOT listed for 16 days (inside the 15-day own-band warm-up), then from C = A+18; YY every day.
    XX's own band on C comes only from A and A+1: a chunk starting at C must rebuild those two entries, not 15 calendar days"""
    A = DT.engine()
    days = A.days_between('20251016', '20251120')
    ramp = 1 + 0.01 * np.arange(N)
    price, values = {}, {}
    for k, d in enumerate(days):
        price[d] = ['YY'] if d < '20251101' else ['XX', 'YY'] if d in ('20251101', '20251102') or d >= '20251119' else ['YY']
        values[('YY', d)] = ramp.copy(); values[('XX', d)] = np.full(N, 10.0)
    values[('XX', '20251101')] = ramp.copy(); values[('XX', '20251102')] = ramp.copy()
    values[('XX', '20251119')][100] = 0.5; values[('XX', '20251120')][200] = 0.5; values[('YY', '20251106')][300] = 0.2
    return FakeStore(price, values, days, ['XX', 'YY'])


def own_band_def(tmp_path):
    d = json.loads(DEF_OI.read_text()); d['id'] = 'OWN_BAND_TEST'; d['window'] = {'first': '20250901', 'last': '20260228'}
    d['inputs']['band'] = {'op': 'own_pct', 'of': 'metric', 'q': 5}
    d['conditions'] = [{'name': 'below its own 5th percentile', 'lhs': 'metric', 'cmp': '<', 'rhs': 'band', 'role': 'claim'}]
    p = tmp_path / 'own_band.json'; p.write_text(json.dumps(d)); return p


def test_planted_history_gap_chunked_equals_serial(tmp_path):
    """the hand answer: XX fires on C (00:01:40 is col 100) and C+1 (col 200) from the band of A and A+1, YY on A+5 (col 300).
    8 chunks (one starts exactly at C) equal one serial run; a run that STARTS at C (calendar warm-up only) misses XX's fires, which is
    what a calendar-day chunk warm-up would have done"""
    p = own_band_def(tmp_path)
    want = sorted([('XX', day0('20251119') + 6000, 1), ('XX', day0('20251120') + 12000, 1), ('YY', day0('20251106') + 18000, 1)])
    s = DT.run(p, '20251101', '20251120', tmp_path / 's', fake_coins(tmp_path), research_window=W, workers=1, _reader=gap_store())
    q = DT.run(p, '20251101', '20251120', tmp_path / 'q', fake_coins(tmp_path), research_window=W, workers=8, _reader=gap_store())
    assert sorted(events(s)) == want and sorted(events(q)) == want and cells(s) == cells(q)
    mq = json.loads(Path(q).read_text())
    assert mq['parallel']['mode'] == 'CHUNKED_ENTRY_WARMUP' and mq['parallel']['chunks'] == 7
    starts = {c['first']: c['warm'] for c in mq['workers']['chunks']}
    assert starts['20251119']['mode'] == 'ENTRIES' and starts['20251119']['coin_days'] == 2 + 14     # XX: A, A+1; YY: 14 days
    late = DT.run(p, '20251119', '20251120', tmp_path / 'late', fake_coins(tmp_path), research_window=W, workers=1, _reader=gap_store())
    assert [e for e in events(late) if e[0] == 'XX'] == []


def fake_coins(tmp_path):
    p = tmp_path / 'roster_xy.tsv'
    if not p.exists():
        p.write_text('coin\nXX\nYY\n')
    return p


def test_planted_nested_history_runs_serial(tmp_path):
    """a history source that itself depends on history cannot be rebuilt chunk by chunk: one process, said in DETECT_RUN.json"""
    d = json.loads(own_band_def(tmp_path).read_text())
    d['inputs']['dev'] = {'op': 'sub', 'a': 'metric', 'b': 'band'}
    d['inputs']['band2'] = {'op': 'own_pct', 'of': 'dev', 'q': 5}
    d['conditions'].append({'name': 'nested', 'lhs': 'dev', 'cmp': '<', 'rhs': 'band2', 'role': 'shared'})
    p = tmp_path / 'nested.json'; p.write_text(json.dumps(d))
    r = DT.run(p, '20251101', '20251110', tmp_path / 'n', fake_coins(tmp_path), research_window=W, workers=8, _reader=gap_store())
    m = json.loads(Path(r).read_text())
    assert m['parallel']['mode'] == 'SERIAL_FORCED' and m['parallel']['chunks'] == 1 and m['parallel']['reason']


def test_real_percentile_lit_aster_serial_equals_8_processes(tmp_path):
    """an own-band percentile rule on LIT and ASTER (listed late: 20251223 and 20250919) and BTC, 20250912..20251231: 8 real processes
    (entry warm-up) equal one serial run, every event and every coin-day"""
    d = json.loads(own_band_def(tmp_path).read_text())
    d['conditions'] = [{'name': 'OI drop', 'lhs': 'metric', 'cmp': '<', 'rhs': -1, 'role': 'claim'},
                       {'name': 'below its own 2nd percentile', 'lhs': 'metric', 'cmp': '<', 'rhs': 'band', 'role': 'claim'}]
    d['inputs']['band']['q'] = 2
    p = tmp_path / 'real_band.json'; p.write_text(json.dumps(d))
    s = DT.run(p, '20250912', '20251231', tmp_path / 's', ROSTER, coins='LIT,ASTER,BTC', research_window=W, workers=1)
    q = DT.run(p, '20250912', '20251231', tmp_path / 'q', ROSTER, coins='LIT,ASTER,BTC', research_window=W, workers=8)
    es = events(s)
    assert {e[0] for e in es} == {'LIT', 'ASTER', 'BTC'}
    assert es == events(q) and cells(s) == cells(q)
    mq = json.loads(Path(q).read_text())
    assert mq['parallel']['mode'] == 'CHUNKED_ENTRY_WARMUP' and mq['workers']['processes'] == 8


# ================================================================= guards (i2g_check REVIEW_DETECT_V1: C4/N1/N4, K1/K6, K4, K5, hard kill)
class Recorder:
    """a reader proxy that records every day it is asked to open (index, part_of, read, step), then asks the real one"""
    POS = {'index': 0, 'part_of': 1, 'step': 1, 'read': 2, 'reasons': 1}

    def __init__(self, R):
        self.R = R; self.days = set()

    def __getattr__(self, k):
        f = getattr(self.R, k)
        if k not in self.POS:
            return f

        def g(*a, **kw):
            x = a[self.POS[k]]
            self.days.update(x if isinstance(x, list) else [x])
            return f(*a, **kw)
        return g


def test_research_window_required_and_nothing_outside_opened(tmp_path, fake_roster):
    """C4/N1/N4: no window = REFUSED; a CHECK month or a day outside the window is refused BEFORE any read (the recorder stays empty,
    also for a definition whose own window runs to May); with the window starting on the first day, D-1 is never opened and the first
    00:00 step's predecessor is UNKNOWN"""
    d = json.loads(planted_def(tmp_path, 0).read_text()); d['window'] = {'first': '20250901', 'last': '20260531'}
    p = tmp_path / 'to_may.json'; p.write_text(json.dumps(d))
    rec = Recorder(FakeDays())
    with pytest.raises(DT.Refusal, match='RESEARCH_WINDOW_REQUIRED'):
        DT.run(p, D1, D1, tmp_path / 'a', fake_roster, workers=1, _reader=rec)
    with pytest.raises(DT.Refusal, match='SELECTION_OUTSIDE_WINDOW'):
        DT.run(p, '20260301', '20260301', tmp_path / 'b', fake_roster, research_window=W, workers=1, _reader=rec)
    with pytest.raises(DT.Refusal, match='RESEARCH_WINDOW_NOT_BUILD'):
        DT.run(p, '20260301', '20260301', tmp_path / 'c', fake_roster, research_window='20250901:20260331', workers=1, _reader=rec)
    with pytest.raises(DT.Refusal, match='RESEARCH_WINDOW'):
        DT.run(p, D1, D1, tmp_path / 'd', fake_roster, research_window='2025091:20260228', workers=1, _reader=rec)
    assert rec.days == set() and not any((tmp_path / x).exists() for x in 'abcd')
    r = DT.run(p, D2, D4, tmp_path / 'e', fake_roster, research_window=D2 + ':' + D4, workers=1, _reader=rec)
    assert rec.days and min(rec.days) == D2 and max(rec.days) <= D4               # D1 (D2's predecessor day) never opened
    m = json.loads(Path(r).read_text())
    assert m['research_window'] == {'first': D2, 'last': D4, 'days_never_opened': [D1]}
    assert cells(r)[('XX', D2)]['predecessor_known'] == '0' and cells(r)[('XX', D2)]['full_known'] == '0'
    assert ('XX', day0(D2) + 120, -1) in events(r)                                 # 00:02 still fires (00:01 known false)


def test_real_window_start_predecessor_unknown(tmp_path):
    """the same on the real store: window starting 20251010, BTC's 20251009 is never opened, 20251010's predecessor is UNKNOWN"""
    rec = Recorder(LD.Days(LAB_DAYS, 'research'))
    r = DT.run(DEF_OI, '20251010', '20251010', tmp_path / 'r', ROSTER, coins='BTC', research_window='20251010:20251031', workers=1,
               _reader=rec)
    assert min(rec.days) == '20251010' and cells(r)[('BTC', '20251010')]['predecessor_known'] == '0'
    assert all(t > day0('20251010') for c, t, s in events(r))


def test_malformed_inputs_refuse_with_codes(tmp_path, capsys):
    """K1/K6: a malformed roster JSON and a definition window '2025091' are REFUSED <CODE>, exit 2, nothing written"""
    bad = tmp_path / 'bad_roster.json'; bad.write_text('{"coins": ["BTC", ')
    rc = DT.main(['--definition', str(DEF_OI), '--roster', str(bad), '--coins', 'BTC', '--first', '20251010', '--last', '20251010',
                  '--research-window', W, '--out', str(tmp_path / 'o1'), '--workers', '1',
                  '--lab-root', str(tmp_path / 'lab_days_never_opened')])
    assert rc == 2 and 'REFUSED ROSTER_INVALID' in capsys.readouterr().err and not (tmp_path / 'o1').exists()
    d = json.loads(DEF_OI.read_text()); d['window'] = {'first': '2025091', 'last': '20260228'}
    p = tmp_path / 'w7.json'; p.write_text(json.dumps(d))
    rc = DT.main(['--definition', str(p), '--roster', str(ROSTER), '--coins', 'BTC', '--first', '20251010', '--last', '20251010',
                  '--research-window', W, '--out', str(tmp_path / 'o2'), '--workers', '1',
                  '--lab-root', str(tmp_path / 'lab_days_never_opened')])
    assert rc == 2 and 'REFUSED DEFINITION_INVALID' in capsys.readouterr().err and not (tmp_path / 'o2').exists()
    rc = DT.main(['--definition', str(DEF_OI), '--roster', str(ROSTER), '--coins', 'BTC', '--first', '20251010', '--last', '20251010',
                  '--out', str(tmp_path / 'o3'), '--workers', '1',
                  '--lab-root', str(tmp_path / 'lab_days_never_opened')])
    assert rc == 2 and 'REFUSED RESEARCH_WINDOW_REQUIRED' in capsys.readouterr().err and not (tmp_path / 'o3').exists()


def test_read_run_refuses_tampering(tmp_path, fake_roster):
    """K4: a committed run reads back; a missing EVENTS.tsv, an added file, an edited manifest or an edited EVENTS.tsv are REFUSED"""
    import shutil
    r = Path(DT.run(planted_def(tmp_path, 0), D1, D4, tmp_path / 'run', fake_roster, research_window=W, workers=1, _reader=FakeDays())).parent
    assert DT.read_run(r)['status'] == 'COMPLETE'
    cases = {}
    for k in ('missing', 'extra', 'manifest', 'events'):
        c = tmp_path / k; shutil.copytree(r, c); cases[k] = c
    os.rename(cases['missing'] / 'EVENTS.tsv', tmp_path / 'moved_EVENTS.tsv')          # gone from the run folder (moved, not deleted)
    (cases['extra'] / 'NOTE.txt').write_text('added after the commit\n')
    m = json.loads((cases['manifest'] / 'DETECT_RUN.json').read_text()); m['events'] = 999999
    (cases['manifest'] / 'DETECT_RUN.json').write_text(json.dumps(m))
    with open(cases['events'] / 'EVENTS.tsv', 'a') as f:
        f.write('XX\t1762000000\t-1\t1762000000\tE2.S04\tffffffffffffffff\n')
    for k, code in (('missing', 'FILE_MISSING'), ('extra', 'EXTRA_FILE'), ('manifest', 'MANIFEST_CHANGED'), ('events', 'FILE_CHANGED')):
        with pytest.raises(DT.Refusal, match=code):
            DT.read_run(cases[k])


def test_code_identity_pinned_and_change_refused(tmp_path, fake_roster, monkeypatch):
    """K5: every loaded module of the tree is pinned (engine, onset_band_v6, matched_controls_v1, lab3 bins/days/law, clock_series,
    event_profile, labcore); a module that changes between admission and commit refuses the run"""
    r = DT.run(planted_def(tmp_path, 0), D1, D2, tmp_path / 'ok', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    pins = json.loads(Path(r).read_text())['code_sha16']
    for name in ('alarm_design_v3.py', 'onset_band_v6.py', 'matched_controls_v1.py', 'lab3/bins.py', 'lab3/days.py', 'lab3/law.py',
                 'clock_series.py', 'event_profile.py', 'labcore/briefs.py', 'labcore/gates.py', 'idea_to_grade/detect_v2.py'):
        assert any(k.endswith(name) for k in pins), name
    real = DT.module_pins; n = {'k': 0}

    def drifting():
        n['k'] += 1; x = real()
        if n['k'] > 1:
            x[str(DT.ENGINE_PATH)] = '0000000000000000'
        return x
    monkeypatch.setattr(DT, 'module_pins', drifting)
    with pytest.raises(DT.Refusal, match='CODE_CHANGED_DURING_RUN'):
        DT.run(planted_def(tmp_path, 0), D1, D2, tmp_path / 'drift', fake_roster, research_window=W, workers=1, _reader=FakeDays())


def test_hard_kill_leaves_nothing_running(tmp_path):
    """a SIGKILL of the detect process (2 real workers held by the test hook) stops its workers and the multiprocessing helper within a
    few seconds: nothing keeps running outside the slot claim"""
    import signal, subprocess, time as tm
    hold = tmp_path / 'hold'; hold.mkdir()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1')
    env[DT.TEST_HOLD_ENV] = '60:%s' % hold
    pr = subprocess.Popen([sys.executable, '-B', str(HERE / 'detect_v2.py'), '--definition', str(DEF_OI), '--roster', str(ROSTER),
                           '--coins', 'BTC,ETH', '--first', '20251010', '--last', '20251011', '--research-window', W,
                           '--out', str(tmp_path / 'run'), '--workers', '2', '--lab-root', LAB_DAYS], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = tm.time()
    while len(list(hold.glob('worker_*.pid'))) < 2 and tm.time() - t0 < 30:
        tm.sleep(0.1)
    workers = [int(x.read_text()) for x in hold.glob('worker_*.pid')]
    kids = [int(x) for x in subprocess.run(['/usr/bin/pgrep', '-P', str(pr.pid)], capture_output=True, text=True).stdout.split()]
    assert len(workers) == 2 and set(workers) <= set(kids)
    os.kill(pr.pid, signal.SIGKILL); pr.wait()

    def alive(pid):
        try:
            os.kill(pid, 0); return True
        except ProcessLookupError:
            return False
    t1 = tm.time()
    while any(alive(x) for x in kids) and tm.time() - t1 < 10:
        tm.sleep(0.1)
    assert not any(alive(x) for x in kids), [x for x in kids if alive(x)]
    assert not (tmp_path / 'run' / 'DETECT_RUN.json').exists()


def test_refusal_keeps_its_code_across_processes():
    """a Refusal raised in a worker reaches the caller with the same code (i2g_grader maps e.code to DETECT_<CODE>)"""
    import pickle
    e = pickle.loads(pickle.dumps(DT.Refusal('SOURCE_CHANGED_DURING_RUN', 'day=20251010/BASE')))
    assert e.code == 'SOURCE_CHANGED_DURING_RUN' and str(e) == 'SOURCE_CHANGED_DURING_RUN: day=20251010/BASE'


# ================================================================= outside review A53 (detect.py c536f0bc): F2 grid, F3 schema, F4 operands
def a53_clean():
    f = FakeDays()
    for dd in f.v:
        f.v[dd][:] = 0
        for fld in ('e', 'a', 'o'):
            f.q[dd][fld][:] = 0
        f.q[dd]['k'][:] = (day0(dd) + 60 * np.arange(N)) * 1_000_000
    return f


def test_grid_70_grid_equals_base_and_keeps_every_step(tmp_path, fake_roster):
    """A53-F2: a 70 s grid (does not divide the day) decides at every D0 + k x 70 < D0 + 86400 (1235 steps, the last 23:59:40) with the
    predecessor of 00:00 at D0 - 70 s from D-1's data, on BOTH paths (GRID = the engine's own BASE rows)"""
    d = json.loads(planted_def(tmp_path, 0).read_text()); d['grid_s'] = 70
    p = tmp_path / 'g70.json'; p.write_text(json.dumps(d))
    f = a53_clean()
    f.v[D1][0, 700] = -2                       # XX: minute 700 -> the 42000 s step fires
    f.v[D1][0, 1438] = -2                      # XX: minute 1438 -> the 86310 s step fires (86380 s reads minute 1439 = 0)
    f.v[D2][0, 0] = -2                         # XX: D2 00:00 true, but its predecessor D2 - 70 s = D1 86330 s (minute 1438) is true: no onset
    f.v[D1][1, 1439] = -2                      # YY: only the day's last step, 86380 s = 23:59:40, sees minute 1439: it must fire
    g = DT.run(p, D1, D2, tmp_path / 'grid', fake_roster, research_window=W, workers=1, _reader=f)
    b = DT.run(p, D1, D2, tmp_path / 'base', fake_roster, research_window=W, workers=1, _reader=f, _path='BASE')
    want = sorted([('XX', day0(D1) + 42000, -1), ('XX', day0(D1) + 86310, -1), ('YY', day0(D1) + 86380, -1)])
    assert sorted(events(g)) == want and sorted(events(b)) == want
    assert cells(g) == cells(b) and cells(g)[('XX', D1)]['slots'] == '1235'


def test_read_run_requires_exact_files_even_with_a_recomputed_self_hash(tmp_path, fake_roster):
    """A53-F3: a manifest whose COVERAGE pin is removed (file moved out) and whose self-hash is recomputed is REFUSED RUN_SCHEMA; so is
    {status: COMPLETE, files: {}}"""
    r = Path(DT.run(planted_def(tmp_path, 0), D1, D1, tmp_path / 'run', fake_roster, research_window=W, workers=1, _reader=FakeDays()))
    m = json.loads(r.read_text()); m['files'].pop('COVERAGE.tsv'); m['manifest_sha16'] = DT.manifest_sha16(m)
    r.write_text(json.dumps(m)); os.rename(r.parent / 'COVERAGE.tsv', tmp_path / 'moved_COVERAGE.tsv')
    with pytest.raises(DT.Refusal, match='RUN_SCHEMA'):
        DT.read_run(r.parent)
    e = tmp_path / 'empty'; e.mkdir(); (e / 'DETECT_RUN.json').write_text(json.dumps({'status': 'COMPLETE', 'files': {}}))
    with pytest.raises(DT.Refusal, match='RUN_SCHEMA'):
        DT.read_run(e)


@pytest.mark.parametrize('inputs,code', [({'broken': {'op': 'neg', 'of': 'NOT_BOUND'}}, 'UNKNOWN_INPUT'),
                                         ({'broken': {'op': 'sum', 'of': 'metric'}}, 'OP_FIELD_MISSING'),
                                         ({'broken': {'op': 'change', 'of': 'metric', 'w_s': float('nan')}}, 'OP_FIELD_INVALID'),
                                         ({'broken': {'op': 'neg', 'of': 'loop'}, 'loop': {'op': 'abs', 'of': 'broken'}}, 'INPUT_CYCLE')])
def test_operands_inside_inputs_refused_before_any_read(tmp_path, fake_roster, inputs, code):
    """A53-F4: every operand and op field inside the input expressions is checked (and cycles refused) before any read or output folder"""
    d = json.loads(planted_def(tmp_path, 0).read_text()); d['inputs'].update(inputs); d['conditions'][0]['lhs'] = 'broken'
    p = tmp_path / 'op.json'; p.write_text(json.dumps(d))
    rec = Recorder(FakeDays())
    with pytest.raises(DT.Refusal, match=code):
        DT.run(p, D1, D1, tmp_path / 'run', fake_roster, research_window=W, workers=1, _reader=rec)
    assert rec.days == set() and not (tmp_path / 'run').exists()


# ================================================================= NEW EDITION (SCOUT, 30 Oct 2026): the gate and the lab days
def gate_file(tmp_path, text, name):
    p = tmp_path / name; p.write_text(text); return str(p)


def same_files(a, b):
    return all((Path(a).parent / n).read_bytes() == (Path(b).parent / n).read_bytes() for n in ('EVENTS.tsv', 'COVERAGE.tsv'))


class FlipGate(Recorder):
    """a planted reader that writes PAUSE into the gate file at its first read (a gate that leaves RUN during the run)"""
    def __init__(self, R, gate):
        super().__init__(R); self.gate = gate

    def __getattr__(self, k):
        if k == 'read':
            Path(self.gate).write_text('PAUSE\n')
        return super().__getattr__(k)


def test_no_gate_never_reads_the_built_in_gate(tmp_path, fake_roster, monkeypatch):
    """gate None or '': no gate at all; labcore.jobgate's built-in gate (pointed here at a PAUSE file) is never read; a RUN gate file
    gives the same EVENTS.tsv and COVERAGE.tsv byte for byte; the answer is the hand answer"""
    from labcore import jobgate
    pause = gate_file(tmp_path, 'PAUSE\n', 'built_in_gate.txt')
    monkeypatch.setattr(jobgate, 'GATE', pause)
    monkeypatch.setattr(jobgate.state, '__defaults__', (pause,))
    runs = {k: DT.run(planted_def(tmp_path, 0), D1, D4, tmp_path / k, fake_roster, research_window=W, workers=1, _reader=FakeDays(), gate=g)
            for k, g in (('none', None), ('empty', ''), ('run', gate_file(tmp_path, 'RUN\n', 'gate.txt')))}
    assert sorted(events(runs['none'])) == expected_fires(0)
    assert same_files(runs['none'], runs['empty']) and same_files(runs['none'], runs['run'])
    r = DT.run(planted_def(tmp_path, 0), D1, D1, tmp_path / 'default', fake_roster, research_window=W, workers=1, _reader=FakeDays())
    assert Path(r).is_file()                                            # gate not given: runs although the built-in gate reads PAUSE


def test_gate_not_run_refuses_before_any_read_or_output(tmp_path, fake_roster):
    """a gate file whose first line is not RUN (PAUSE, a missing file, an empty file, another word) is REFUSED GATE_NOT_RUN before any
    read or output, as detect.py read the team's gate (labcore.jobgate.state); ' run ' reads RUN"""
    cases = (('pause', gate_file(tmp_path, 'PAUSE\n', 'p.txt')), ('missing', str(tmp_path / 'no_such_gate.txt')),
             ('blank', gate_file(tmp_path, '', 'b.txt')), ('other', gate_file(tmp_path, 'GO\nRUN\n', 'o.txt')))
    for k, g in cases:
        rec = Recorder(FakeDays())
        with pytest.raises(DT.Refusal, match='GATE_NOT_RUN'):
            DT.run(planted_def(tmp_path, 0), D1, D2, tmp_path / k, fake_roster, research_window=W, workers=1, _reader=rec, gate=g)
        assert rec.days == set() and not (tmp_path / k).exists(), k
    r = DT.run(planted_def(tmp_path, 0), D1, D2, tmp_path / 'lower', fake_roster, research_window=W, workers=1, _reader=FakeDays(),
               gate=gate_file(tmp_path, ' run \n', 'l.txt'))
    assert Path(r).is_file()


def test_gate_read_again_in_every_worker_and_before_the_commit(tmp_path, fake_roster):
    """the gate is read at the start, at each chunk's start and before the commit: PAUSE written during chunk 1 (4 one-day chunks, in
    this process with a planted reader) refuses chunk 2; PAUSE during a one-chunk run refuses the commit; nothing is committed"""
    g = gate_file(tmp_path, 'RUN\n', 'g1.txt')
    with pytest.raises(DT.Refusal, match='GATE_NOT_RUN: BACKFILL_GATE first line is not RUN'):
        DT.run(planted_def(tmp_path, 0), D1, D4, tmp_path / 'w', fake_roster, research_window=W, workers=4, _reader=FlipGate(FakeDays(), g),
               gate=g)
    assert not (tmp_path / 'w' / 'DETECT_RUN.json').exists()
    g = gate_file(tmp_path, 'RUN\n', 'g2.txt')
    with pytest.raises(DT.Refusal, match='GATE_NOT_RUN: the gate left RUN during the run'):
        DT.run(planted_def(tmp_path, 0), D1, D1, tmp_path / 'c', fake_roster, research_window=W, workers=1, _reader=FlipGate(FakeDays(), g),
               gate=g)
    assert not (tmp_path / 'c' / 'DETECT_RUN.json').exists()


def test_lab_root_required_no_machine_default(tmp_path, fake_roster):
    """run() without lab_root (None or '') and without a test reader is REFUSED LAB_ROOT_REQUIRED before any read or output; the module
    keeps no lab path of its own"""
    for k, lr in (('none', None), ('empty', '')):
        with pytest.raises(DT.Refusal, match='LAB_ROOT_REQUIRED'):
            DT.run(planted_def(tmp_path, 0), D1, D1, tmp_path / k, fake_roster, research_window=W, workers=1, lab_root=lr)
        assert not (tmp_path / k).exists()
    assert inspect.signature(DT.run).parameters['lab_root'].default is None and 'LAB_ROOT' not in vars(DT)
    r = DT.run(planted_def(tmp_path, 0), D1, D1, tmp_path / 'given', fake_roster, research_window=W, workers=1, _reader=FakeDays(),
               lab_root='LAB_DAYS_DIR')
    assert json.loads(Path(r).read_text())['lab_root'] == 'LAB_DAYS_DIR'


def test_command_requires_lab_root_and_passes_gate(tmp_path, monkeypatch, capsys):
    """the command: no --lab-root = argparse refusal, exit 2; --lab-root and --gate reach run() unchanged ('--gate=' is the empty gate,
    no --gate is None); a PAUSE gate refuses GATE_NOT_RUN, exit 2, before any read"""
    base = ['--definition', str(DEF_OI), '--roster', str(ROSTER), '--coins', 'BTC', '--first', '20251010', '--last', '20251010',
            '--research-window', W, '--out', str(tmp_path / 'o'), '--workers', '1']
    with pytest.raises(SystemExit) as e:
        DT.main(base)
    err = capsys.readouterr().err
    assert e.value.code == 2 and 'required' in err and '--lab-root' in err and not (tmp_path / 'o').exists()
    pause = gate_file(tmp_path, 'PAUSE\n', 'pause.txt')
    rc = DT.main(base + ['--lab-root', str(tmp_path / 'lab_days_never_opened'), '--gate', pause])
    assert rc == 2 and 'REFUSED GATE_NOT_RUN' in capsys.readouterr().err and not (tmp_path / 'o').exists()
    seen = []

    def fake_run(*a, **kw):
        seen.append(kw); raise DT.Refusal('STOPPED_BY_TEST')
    monkeypatch.setattr(DT, 'run', fake_run)
    for extra in (['--gate', 'FEED_GATE_FILE'], ['--gate='], []):
        assert DT.main(base + ['--lab-root', 'LAB_DAYS_DIR'] + extra) == 2
    assert [(k['lab_root'], k['gate']) for k in seen] == [('LAB_DAYS_DIR', 'FEED_GATE_FILE'), ('LAB_DAYS_DIR', ''), ('LAB_DAYS_DIR', None)]
