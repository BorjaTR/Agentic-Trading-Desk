"""[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file test_i2g_v3_real.py 13adf272fce06a17 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
test_i2g_v3_2_real.py (idea_to_grade V3.1, ALARMLIB seat, 25 Oct 2026): real-input checks of idea_to_grade V3 on the Mac (BUILD months only;
lab_days PRICE read through lab3, nothing written outside the scratch folder; the real tries ledger is never written: a scratch ledger holds
the test's PREREG row).
  cd <this folder>; nice -n 10 <PYTHON> -B -m pytest -q -p no:cacheprovider test_i2g_v3_2_real.py
  R0 V2.3.1 is untouched: its files still equal its pins
  R1 COMPATIBILITY: V3 --compat-v2 --delay-s 6 reproduces V2.3.1's files on the same events (labelled a compatibility check, not proof)
  R2 V3 on the same events (delay 0.5 s, a frozen universe built from a wider list): as-of controls re-derived independently, the tough
     moments re-derived from the prices, the fill moved by the delay to the bin an independent oracle names, frozen weights read
  R3 GENERIC: another alarm (fresh detection of a different definition), other coins, other days: a complete, verified run
  R4 no PREREG ask id in the ledger: refused before staging
  V3.1 (review REVIEW_IDEA_TO_GRADE_V3_INDEP):
  R5 F4 two opposite-side events in one second on real prices: each parent row carries the 15 min move signed by its own side
  R6 F3 a second run on an ask that already admitted a complete run is refused (LEDGER_ASK_USED); every run here is TEST (scratch ledger)
  R7 F5 an alarm id outside the registry, and an event list that is not the universe source without --events-subset, are refused
  R8 F2 the real frozen universe passes the row-by-row check; its alarms are the registry ids
Each run has its own PREREG ask whose idea is the run's alarm id and whose days are the run's --first/--last (a scratch ledger and a
scratch registry beside it; the real ones are only read)."""
import csv, datetime as dt, json, os, subprocess, sys
import numpy as np
import pytest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import i2g_engine as E2
import i2g_rules_v1_2 as RU

PY = '<PYTHON>'
SCR = '<SCRATCH>/work_ALARMLIB/i2g_v3/tests'
FIX = '<SCRATCH>/work_LEAD/i2g/grade/fixture/full3_detect_v2'
IDEA = '<LAB_REPO>/forensics/team/OUTSIDE/CODE2/fresh_grading_t2_v1/BN_OI_CONTRACTION_1PCT_10M_T2_V1.json'
ROSTER = ('<LAB_REPO>/forensics/team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/'
          'ROSTER_BUILD.json')
LAB = '<DATA_ROOT>/lab_days'
RW = '20250901:20260228'                                  # the research window of these tests: a run setting, BUILD months only
US = 1_000_000
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S')


def sh(p):
    import hashlib
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def fixture_events(coins=None):
    with open(os.path.join(FIX, 'EVENTS.tsv')) as f:
        return [r for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t') if coins is None or r['coin'] in coins]


@pytest.fixture(scope='module')
def env():
    os.makedirs(SCR, exist_ok=True)
    d = os.path.join(SCR, 'run_' + STAMP); os.makedirs(d)
    pins = os.path.join(d, 'I2G_PINS_V3_DEV.json')
    r = subprocess.run([PY, '-B', os.path.join(HERE, 'release_pins_v3_2.py'), pins], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    ledger = os.path.join(d, 'LEDGER_TEST.tsv'); ask = lambda name: 'PREREG_I2GV31TEST_%s_%s' % (name, STAMP)
    asks = [('compat', 'FIXALARM', '20251002', '20251020'), ('asof', 'FIXALARM', '20251002', '20251020'),
            ('generic', 'BNOI_T2', '20251020', '20251116'), ('opp', 'FIXALARM', '20251002', '20251020'),
            ('nope', 'ALM_NOPE', '20251002', '20251020'), ('mism', 'FIXALARM', '20251002', '20251020')]
    with open(ledger, 'w') as f:
        f.write('# scratch ledger of test_i2g_v3_2_real.py\ntry_utc\task_id\tidea\tpurpose\tkind\tdays_from\tdays_to\tsetting_sha16\tstatus\n')
        for name, idea, d0, d1 in asks:
            f.write('%s\t%s\t%s\ttest\tPREREG\t%s\t%s\t\tPREREG\n' % (STAMP, ask(name), idea, d0, d1))
    registry = os.path.join(d, 'REGISTRY_TEST.tsv')
    with open(registry, 'w') as f:
        f.write('# scratch registry of test_i2g_v3_2_real.py\nregistry_id\tcard\tversion\tdefinition\tdefinition_sha16\tfamily\n'
                'FIXALARM\t-\t1\t-\t-\tfixture\nBNOI_T2\t-\t1\t%s\t%s\tfixture\n' % (IDEA, sh(IDEA)))
    ev = [r for r in fixture_events({'BTC'}) if '20251010' <= E2.day_of(int(r['t'])) <= '20251020'][:4]
    small = os.path.join(d, 'events_small.tsv')
    with open(small, 'w') as f:
        f.write('coin\tt\tside\n' + ''.join('%s\t%s\t%s\n' % (r['coin'], r['t'], r['side']) for r in ev))
    wide = os.path.join(d, 'events_wide.tsv')                # the universe's source: the whole fixture list (three coins, every day)
    with open(wide, 'w') as f:
        f.write('coin\tt\tside\n' + ''.join('%s\t%s\t%s\n' % (r['coin'], r['t'], r['side']) for r in fixture_events()))
    uni = os.path.join(d, 'UNIVERSE_TEST.tsv')
    r = subprocess.run([PY, '-B', os.path.join(HERE, 'i2g_universe_v1.py'), uni, 'FIXALARM=' + wide], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    opp = os.path.join(d, 'events_opposite.tsv')             # F4: one fixture second, both sides
    with open(opp, 'w') as f:
        f.write('coin\tt\tside\n%s\t%s\t1\n%s\t%s\t-1\n' % (ev[0]['coin'], ev[0]['t'], ev[0]['coin'], ev[0]['t']))
    return dict(d=d, pins=pins, ledger=ledger, ask=ask, small=small, ev=ev, uni=uni, registry=registry, opp=opp)


def v3(env, *args, check=True):
    cmd = ['nice', '-n', '10', PY, '-B', os.path.join(HERE, 'idea_to_grade_v3_2.py')] + list(args) + \
          ['--pins', env['pins'], '--ledger', env['ledger'], '--registry', env['registry'], '--workers', '1']
    r = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    if check and r.returncode != 0:
        raise AssertionError(r.stderr[-3000:])
    return r


def small_args(env, out):
    return ['--events', env['small'], '--events-sha16', sh(env['small']), '--roster', ROSTER, '--coins', 'BTC', '--first', '20251002',
            '--last', '20251020', '--research-window', RW, '--out', out]


@pytest.fixture(scope='module')
def v2_run(env):
    out = os.path.join(env['d'], 'v2')
    r = subprocess.run(['nice', '-n', '10', PY, '-B', os.path.join(HERE, 'idea_to_grade.py')] + small_args(env, out) +
                       ['--workers', '1', '--pins', os.path.join(HERE, 'I2G_PINS_V2.json')], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-3000:]
    return out


@pytest.fixture(scope='module')
def compat_run(env):
    out = os.path.join(env['d'], 'v3_compat')
    v3(env, *small_args(env, out), '--delay-s', '6', '--compat-v2', '--alarm-id', 'FIXALARM', '--ledger-ask', env['ask']('compat'))
    return out


@pytest.fixture(scope='module')
def asof_run(env):
    out = os.path.join(env['d'], 'v3_asof')
    v3(env, *small_args(env, out), '--delay-s', '0.5', '--universe', env['uni'], '--alarm-id', 'FIXALARM', '--events-subset',
       '--ledger-ask', env['ask']('asof'))
    return out


def tsv(p):
    with open(p) as f:
        return list(csv.DictReader(f, delimiter='\t'))


# ---------------------------------------------------------------------------------------------------- R0
def test_R0_v2_release_untouched():
    pins = json.load(open(os.path.join(HERE, 'I2G_PINS_V2.json')))['pins']
    assert all(sh(q) == h for q, h in pins.items())


# ---------------------------------------------------------------------------------------------------- R1 compatibility
def test_R1_compat_v2_reproduces_v2_files(v2_run, compat_run):
    same = ['matches/CENSUS.tsv', 'matches/BALANCE.tsv', 'matches/COMPARISON_COVERAGE.json', 'matches/UNAVAILABLE.json',
            'measurements/OBSERVATIONS.tsv', 'measurements/VALUES.npy', 'measurements/NAMES.json', 'measurements/REASONS.json',
            'grading/COHORTS.json', 'grading/PARENTS.tsv', 'grading/GRADED_EDGES.tsv']
    diff = [f for f in same if sh(os.path.join(v2_run, f)) != sh(os.path.join(compat_run, f))]
    assert diff == []
    e2 = [r[:8] for r in csv.reader(open(os.path.join(v2_run, 'matches', 'EDGES.tsv')), delimiter='\t')]
    e3 = [r[:8] for r in csv.reader(open(os.path.join(compat_run, 'matches', 'EDGES.tsv')), delimiter='\t')]
    assert e2 == e3
    r2 = open(os.path.join(v2_run, 'grading', 'REPORT.md')).read().split('\n'); r3 = open(os.path.join(compat_run, 'grading', 'REPORT.md')).read().split('\n')
    assert r2[1:] == r3[1:] and 'I2G_V3' in r3[0]
    with np.load(os.path.join(v2_run, 'grading', 'PARENT_DETAIL.npz')) as a, np.load(os.path.join(compat_run, 'grading', 'PARENT_DETAIL.npz')) as b:
        assert sorted(a.files) == sorted(b.files)
        for k in a.files:
            assert np.array_equal(a[k], b[k], equal_nan=a[k].dtype.kind == 'f'), k


# ---------------------------------------------------------------------------------------------------- R2 V3 on the same events
def test_R2_run_verifies_and_ids_carry_the_side(env, asof_run):
    import idea_to_grade_v3_2 as I3
    I3.verify_run(asof_run)
    body = json.load(open(os.path.join(asof_run, 'RUN.json')))
    assert body['run_schema'] == 'I2G_RUN_V3_2' and body['ledger']['ask_id'] == env['ask']('asof') and body['run_class'] == 'TEST'
    assert body['alarm']['events_binding'] == 'DECLARED_SUBSET' and body['alarm']['universe_source'][1] == RU.Universe.read(env['uni']).sources['FIXALARM'][1]
    assert os.path.exists(body['ledger']['claim'])
    assert open(os.path.join(asof_run, 'grade3', 'REPORT3.md')).readline().startswith('# idea_to_grade I2G_V3_2 TEST')
    assert body['settings']['measure']['execution_delay_s'] == 0.5 and body['counts']['parents'] == 4
    P = tsv(os.path.join(asof_run, 'grading', 'PARENTS.tsv'))
    assert all(p['parent_id'].endswith(('_+1', '_-1')) for p in P)


def test_R2_controls_are_as_of_eligible_by_an_independent_rule(env, asof_run):
    busy = sorted(int(r['t']) for r in env['ev'])                      # the run's exclusions: its own events (the list's coin)
    E = tsv(os.path.join(asof_run, 'matches', 'EDGES.tsv'))
    kept_by_v3_only = 0
    for e in E:
        ct = float(e['cand_t'])
        want = '' if not any(ct - 14400 <= b <= ct for b in busy) else 'ASOF_BUSY'
        assert e['asof'] == want and e['own'] == e['asof']
        kept_by_v3_only += e['own_v2'] != '' and e['asof'] == ''
    print('controls kept by V3 that V2 dropped:', kept_by_v3_only)


def _bins(coin, t, days=(-1, 0, 1)):
    """the coin's 3 s bins around t, read straight from lab_days through lab3 (te, tl, px, hi, lo)"""
    p = E2.CoinPrices(LAB, coin, tuple(RW.split(':'))); d = E2.day_of(t); parts = []
    for k in days:
        x = p.raw(E2.shift(d, k))
        if x is not None:
            parts.append(x)
    return {f: np.concatenate([q[f] for q in parts]) for f in ('te', 'tl', 'px', 'hi', 'lo')}


def _move_rv(b, t):
    """an independent reading: plain loops over the bins that ended at or before t"""
    te = b['te'] / 1e6; px = b['px']
    idx = [i for i in range(len(te)) if te[i] <= t and np.isfinite(px[i]) and px[i] > 0]
    i = idx[-1]; j = [q for q in idx if te[q] <= t - 900][-1]
    win = [q for q in idx if te[q] > t - 300]
    lr = [np.log(px[q] / px[idx[idx.index(q) - 1]]) for q in win if idx.index(q) > 0]
    return 100 * (px[i] / px[j] - 1), 100 * np.sqrt(sum(x * x for x in lr))


def test_R2_tough_moments_rederived_from_prices(env, asof_run):
    T = tsv(os.path.join(asof_run, 'matches', 'TOUGH.tsv')); C = {r['parent_id']: r for r in tsv(os.path.join(asof_run, 'matches', 'TOUGH_CENSUS.tsv'))}
    assert T, 'no tough moment drawn'
    busy = sorted(int(r['t']) for r in env['ev'])
    costs = RU.read_costs('<LAB_REPO>/forensics/team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv')
    checked = 0
    for r in T[:6]:
        pid = r['parent_id']; coin, t, side = pid.split('_')[0], int(pid.split('_')[1]), int(pid.split('_')[2]); g = float(r['tough_t'])
        assert not any(g - 14400 <= b <= g for b in busy)                # as-of eligible
        mp, rp = _move_rv(_bins(coin, t), t); mg, rg = _move_rv(_bins(coin, int(g)), g)
        assert abs(float(C[pid]['move15_pct']) - mp) < 1e-9 and abs(float(C[pid]['rv5_pct']) - rp) < 1e-9
        c = RU.coin_cost_pct(costs[coin][0], 0.032)
        assert abs(side * mg - side * mp) <= max(0.5 * c, 0.25 * abs(mp)) + 1e-12
        assert 0.8 * rp - 1e-12 <= rg <= 1.25 * rp + 1e-12
        checked += 1
    assert checked >= 1


def test_R2_delay_moves_the_fill_to_the_oracle_bin(env, asof_run, compat_run):
    """the taker fill = the first 3 s close whose last trade is after alarm + delay + 3 s (fill_v2), re-derived from the bins"""
    def fills(run):
        O = tsv(os.path.join(run, 'measurements', 'OBSERVATIONS.tsv')); V = np.load(os.path.join(run, 'measurements', 'VALUES.npy'))
        names = json.load(open(os.path.join(run, 'measurements', 'NAMES.json')))
        out = {}
        for o in O:
            if o['kind'] == 'parent' and o['direction'] == 'FOLLOW':
                i = int(o['row']); out[(o['coin'], int(o['as_of_us']))] = (V[i, names.index('filled')], V[i, names.index('fill_wait_s')],
                                                                           V[i, names.index('fill_px')], int(o['known_at_us']) - int(o['as_of_us']))
        return out
    a, b = fills(asof_run), fills(compat_run)
    assert set(a) == set(b)
    moved = 0
    for (coin, t_us), (f05, w05, p05, k05) in a.items():
        f6, w6, p6, k6 = b[(coin, t_us)]
        assert k6 - k05 == 5_500_000                                    # known_at follows the delay
        bins = _bins(coin, t_us // US)
        for delay, f, w, p in ((0.5, f05, w05, p05), (6.0, f6, w6, p6)):
            if f != 1:
                continue
            x = t_us + int(delay * US) + 3 * US
            i = int(np.searchsorted(bins['tl'], x, 'right'))
            assert abs(p - bins['px'][i]) < 1e-12 and abs((t_us + int(delay * US) + w * US) - bins['tl'][i]) < 2
        moved += f05 == 1 and f6 == 1 and (t_us + 0.5 * US + w05 * US) < (t_us + 6 * US + w6 * US)
    assert moved >= 1


def test_R2_weights_are_the_frozen_universe(env, asof_run):
    U = RU.Universe.read(env['uni']); W = tsv(os.path.join(asof_run, 'grade3', 'WEIGHTS.tsv'))
    for w in W:
        cid, wt, flag = U.by[('FIXALARM', w['parent_id'])]
        assert w['cluster_id'] == cid and abs(float(w['weight']) - wt) < 1e-12
    T = tsv(os.path.join(asof_run, 'grade3', 'TABLE.tsv'))
    assert {r['measure'] for r in T} >= {'ret_10s', 'ret_4h', 'V1_15m', 'C4C2_4h'} and {r['scheme'] for r in T} == {'TT', 'RT', 'RR'}


# ---------------------------------------------------------------------------------------------------- R3 generic
def test_R3_another_alarm_other_coins_other_days(env):
    out = os.path.join(env['d'], 'v3_generic')
    v3(env, '--idea', IDEA, '--roster', ROSTER, '--coins', 'ETH,XRP', '--first', '20251020', '--last', '20251116', '--research-window', RW,
       '--out', out, '--delay-s', '2', '--alarm-id', 'BNOI_T2', '--ledger-ask', env['ask']('generic'))
    import idea_to_grade_v3_2 as I3
    I3.verify_run(out)
    body = json.load(open(os.path.join(out, 'RUN.json')))
    assert body['detection'] == 'FRESH' and body['alarm_id'] == 'BNOI_T2' and sorted(body['selection']['coins']) == ['ETH', 'XRP']
    assert body['alarm']['definition_sha16'] == sh(IDEA) and body['run_class'] == 'TEST' 
    assert body['selection']['first'] == '20251020' and body['counts']['parents'] >= 1
    assert 'RUN_LOCAL' in body['settings']['grade']['weights']
    print('generic run: %d parents, %d tough covered' % (body['counts']['parents'], body['counts']['tough_covered']))


# ---------------------------------------------------------------------------------------------------- R4 ledger
def test_R4_unknown_ledger_ask_is_refused_before_staging(env):
    out = os.path.join(env['d'], 'v3_noledger')
    r = v3(env, *small_args(env, out), '--delay-s', '6', '--alarm-id', 'FIXALARM', '--ledger-ask', 'PREREG_NOT_REGISTERED', check=False)
    assert r.returncode == 2 and 'LEDGER_ASK_UNKNOWN' in r.stderr and not os.path.exists(out)


# ---------------------------------------------------------------------------------------------------- R5 F4
def test_R5_opposite_sides_in_one_second_keep_their_own_move_sign(env):
    out = os.path.join(env['d'], 'v3_opposite')
    v3(env, '--events', env['opp'], '--events-sha16', sh(env['opp']), '--roster', ROSTER, '--coins', 'BTC', '--first', '20251002',
       '--last', '20251020', '--research-window', RW, '--out', out, '--delay-s', '0.5', '--alarm-id', 'FIXALARM', '--ledger-ask', env['ask']('opp'))
    O = tsv(os.path.join(out, 'measurements', 'OBSERVATIONS.tsv')); V = np.load(os.path.join(out, 'measurements', 'VALUES3.npy'))
    m15 = json.load(open(os.path.join(out, 'measurements', 'NAMES3.json'))).index('move15_pct')
    t = int(env['ev'][0]['t']); mp, _ = _move_rv(_bins(env['ev'][0]['coin'], t), t)          # the unsigned move, re-derived
    got = {}
    for o in O:
        if o['kind'] == 'parent':
            got.setdefault(int(o['side']), set()).add(float(V[int(o['row']), m15]))
    assert set(got) == {1, -1} and abs(mp) > 0
    for side, vals in got.items():                                                              # FOLLOW and FADE rows of each parent
        assert len(vals) == 1 and abs(vals.pop() - side * mp) < 1e-9, (side, got, mp)


# ---------------------------------------------------------------------------------------------------- R6 F3
def test_R6_one_ask_admits_one_complete_run(env, asof_run):
    out = os.path.join(env['d'], 'v3_asof_again')
    r = v3(env, *small_args(env, out), '--delay-s', '0.5', '--universe', env['uni'], '--alarm-id', 'FIXALARM', '--events-subset',
           '--ledger-ask', env['ask']('asof'), check=False)
    assert r.returncode == 2 and 'LEDGER_ASK_USED' in r.stderr and not os.path.exists(out)


# ---------------------------------------------------------------------------------------------------- R7 F5
def test_R7_alarm_id_outside_the_registry_or_unbound_list_is_refused(env):
    out = os.path.join(env['d'], 'v3_nope')
    r = v3(env, *small_args(env, out), '--delay-s', '0.5', '--alarm-id', 'ALM_NOPE', '--ledger-ask', env['ask']('nope'), check=False)
    assert r.returncode == 2 and 'ALARM_ID_UNKNOWN' in r.stderr and not os.path.exists(out)
    out = os.path.join(env['d'], 'v3_mism')
    r = v3(env, *small_args(env, out), '--delay-s', '0.5', '--universe', env['uni'], '--alarm-id', 'FIXALARM', '--ledger-ask', env['ask']('mism'),
           check=False)
    assert r.returncode == 2 and 'ALARM_EVENTS_MISMATCH' in r.stderr and not os.path.exists(out)


# ---------------------------------------------------------------------------------------------------- R8 F2
def test_R8_the_real_frozen_universe_passes_the_row_check():
    F = '<LAB_REPO>/forensics/team/RESEARCH/LIBRARY/'
    U = RU.Universe.read(F + 'UNIVERSE_ALARMS_V1.tsv'); reg = RU.read_registry(F + 'alarm_library/ALARM_REGISTRY_V1.tsv')
    assert len(U.rows) == 18740 and set(U.sources) == set(reg)
    assert len({r[5] for r in U.rows}) == 4819
