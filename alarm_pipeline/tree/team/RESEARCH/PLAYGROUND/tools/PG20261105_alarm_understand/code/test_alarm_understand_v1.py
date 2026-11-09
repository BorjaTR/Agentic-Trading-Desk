#!/usr/bin/env python3
"""test_alarm_understand_v1.py (SCO-A9 for SCOUT, 5 Nov 2026, playground PG20261105_alarm_understand). TEST, NOT REVIEWED.
The spec's unit tests U1 to U8 (team/RESEARCH/LEAD/ALARM_UNDERSTANDING_TOOL_20261105/SPEC_ALARM_UNDERSTANDING_V1.md 62d2aa9a779274f5,
section Tests), written BEFORE the tool, on planted synthetic data only, each in seconds. No market data, no lab day, no store is read:
only the release code the tool reuses (imported read-only, its pins checked by the tool) and the release metric tables (status words).
Run:  python3 -B test_alarm_understand_v1.py [U1 U2 ...]      (all when none named)
Env:  AU_TOOL = the tool file to test (default: alarm_understand_v1.py beside this file; a mutant copy for the mutant runs)
      AU_SCRATCH = where planted inputs and test cards go (default: ../scratch, kept, never removed)
Exit 0 all passed, 1 a test failed."""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, importlib.util, json, os, subprocess, time, traceback
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.environ.get('AU_TOOL') or os.path.join(HERE, 'alarm_understand_v1.py')
SCRATCH = os.environ.get('AU_SCRATCH') or os.path.join(os.path.dirname(HERE), 'scratch')
_spec = importlib.util.spec_from_file_location('alarm_understand_under_test', TOOL)
AU = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AU)

WORDS = ('STRONG', 'WEAK', 'OPINION', 'NOT_ANSWERED')
ALARM = 'PLANT_A'
DEF = {'id': 'PLANT_A', 'family': 'PLANT', 'version': '1',
       'claim': {'one_line': 'planted: a dump with long liquidations, faded', 'side_meaning': 'the move: +1 up, -1 down',
                 'type': 'PREDICT'},
       'inputs': {'ll': {'op': 'raw', 'code': 'A1.S08'}, 'hloi': {'op': 'raw', 'code': 'E2.S06'}},
       'conditions': [{'name': 'planted coin move in its own top 1 pct', 'role': 'claim'},
                      {'name': 'planted long liquidations above own p90', 'role': 'claim'}],
       'truth': [{'name': 'chasers_flushed_60m'}], 'primary': 'chasers_flushed_60m'}
NULL_CODES = ('CTX.A02.hour_utc', 'CTX.A02.fires_other_60m', 'CTX.A02.alarms_all_24h',
              'EPI.A02.run_pct', 'EPI.A02.pre_move_pct', 'CTX.A02.btc_move_15m',
              'A1.S08', 'EPI.A02.forced_usd_log', 'CTX.A02.coins_liquidating_z',
              'CTX.A02.fills_one_sided', 'CTX.A02.whale_net_5m_usd', 'CTX.A02.funding_forced_pays_bp')
PROVEN = {c: {'status': 'PROVEN'} for c in NULL_CODES + ('E2.S06',)}
_STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_%d' % os.getpid()
_R = None


def T(day, sec=0):
    """the UTC second of day YYYYMMDD plus sec"""
    d = dt.datetime.strptime(str(day), '%Y%m%d').replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp()) + int(sec)


def rel():
    global _R
    if _R is None:
        _R = AU.release()
    return _R


def ctx(block='SEPDEC', traps=PROVEN, cards=None):
    return AU.make_context(rel(), ALARM, block, DEF, traps=traps, cards=cards or {})


def bundle(fires, readings=(), forced=(), money=(), labels=None):
    return dict(fires=list(fires), readings=list(readings), forced=list(forced), money=list(money), labels=dict(labels or {}))


def money_row(coin, t, side, net=0.0, edge=0.0, g15=0.0, g1h=0.0, g4h=0.0):
    return dict(coin=coin, t=t, side=side, exit='HOLD_1h', fade_gross_15m=g15, fade_gross_1h=g1h, fade_gross_4h=g4h, net=net,
                edge_tough=edge)


def reading(who, coin, t, code, value, known_at=None):
    return dict(who=who, coin=coin, t=t, code=code, value=value, known_at=t if known_at is None else known_at)


def row(card, q):
    return [r for r in card['rows'] if r['q'] == q][0]


def table(card, name):
    cols, rows = card['tables'][name]
    return [dict(zip(cols, r)) for r in rows]


def newdir(name):
    d = os.path.join(SCRATCH, _STAMP, name)
    os.makedirs(d)
    return d


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def refused(code, fn, *a, **k):
    try:
        fn(*a, **k)
    except AU.Refused as e:
        assert e.code == code, 'refused %s, expected %s (%s)' % (e.code, code, e)
        return e
    raise AssertionError('not refused, expected REFUSED %s' % code)


def cli(*args):
    return subprocess.run([sys.executable, '-B', TOOL] + [str(a) for a in args], capture_output=True, text=True, timeout=100)


def card_rows(text):
    out = []
    for line in text.splitlines():
        if line.startswith('| Q') and line[3:4].isdigit():
            out.append([c.strip() for c in line.strip().strip('|').split('|')])
    return out


def write_def(d):
    p = os.path.join(d, 'DEF_PLANT_A.json')
    json.dump(DEF, open(p, 'x'), indent=1)
    return p, sha16(p)


# ------------------------------------------------------------------------------------------------------------------ U1
def test_U1():
    """no data: 8 rows, words in the set; REFUSED BLOCK_CLOSED on a planted closed day (nothing read); REFUSED SOURCE_CHANGED on a
    wrong sha16; a STOP code refused"""
    # (a) no data, through the command line: 8 rows, every word in the set
    d = newdir('u1_bundle')
    open(os.path.join(d, 'FIRES.tsv'), 'x').write('alarm_id\tcoin\tt\tside\n')
    defp, dsha = write_def(d)
    out = os.path.join(newdir('u1_out'), 'card')
    p = cli('card', out, '--alarm', ALARM, '--def', defp, '--def-sha16', dsha, '--block', 'SEPDEC', '--bundle', d)
    assert p.returncode == 0, 'card rc %d: %s %s' % (p.returncode, p.stdout, p.stderr)
    rows = card_rows(open(os.path.join(out, 'ALARM_CARD.md')).read())
    assert [r[0] for r in rows] == ['Q%d' % i for i in range(1, 9)], rows
    assert all(r[-1] in WORDS for r in rows), [r[-1] for r in rows]
    assert all(r[-1] in ('NOT_ANSWERED', 'OPINION') for r in rows), [r[-1] for r in rows]
    # (b) BLOCK_CLOSED: a planted closed day inside SEPDEC; the law's June onward; the card's August onward. Nothing read: the DEF
    # and the bundle of the command-line runs do not exist, so any read would fail with another code
    planted = lambda day: 'PLANTED CLOSED DAY' if day == 20251015 else None
    refused('BLOCK_CLOSED', AU.check_block, 'SEPDEC', planted)
    refused('BLOCK_CLOSED', AU.check_block, '202510', planted)
    AU.check_block('202511', planted)
    AU.check_block('SEPDEC', lambda day: None)
    for blk in ('202606', '202608', 'MAYJUL'):
        p = cli('card', os.path.join(SCRATCH, _STAMP, 'never_' + blk), '--alarm', ALARM, '--def', '/nonexistent/DEF.json',
                '--def-sha16', '0' * 16, '--block', blk, '--bundle', '/nonexistent/bundle')
        assert p.returncode == 2 and 'REFUSED BLOCK_CLOSED' in p.stdout + p.stderr, (blk, p.returncode, p.stdout, p.stderr)
        assert not os.path.exists(os.path.join(SCRATCH, _STAMP, 'never_' + blk))
    # (c) SOURCE_CHANGED: a wrong pinned sha16 of a reused release file; a wrong DEF sha16
    root = AU.release_root()
    relp, good = AU.PINS[0]
    refused('SOURCE_CHANGED', AU.verify_pins, root, [(relp, '0' * 16)])
    AU.verify_pins(root, [(relp, good)])
    out2 = os.path.join(newdir('u1_out2'), 'card')
    p = cli('card', out2, '--alarm', ALARM, '--def', defp, '--def-sha16', '0' * 16, '--block', 'SEPDEC', '--bundle', d)
    assert p.returncode == 2 and 'REFUSED SOURCE_CHANGED' in p.stdout + p.stderr, (p.returncode, p.stdout, p.stderr)
    # (d) a STOP code is refused, an unproven code is capped
    traps = {'X9.S01': {'status': 'DO NOT USE: planted'}, 'X9.S02': {'status': 'PROVEN'}}
    refused('STOP_CODE', AU.code_status, ['X9.S01', 'X9.S02'], traps, rel())
    assert AU.code_status(['X9.S02', 'X9.S03'], traps, rel()) == {'X9.S02': 'PROVEN', 'X9.S03': 'UNPROVEN'}
    f = (ALARM, 'C1', T(20250915, 3600), -1)
    b = bundle([f], readings=[reading('FIRE', 'C1', f[2], 'X9.S01', 1.0), reading('MATCH', 'C2', f[2] - 999, 'X9.S01', 0.0)])
    refused('STOP_CODE', AU.build_card, b, ctx(traps=dict(PROVEN, **traps)))


# ------------------------------------------------------------------------------------------------------------------ U2
def test_U2():
    """planted fires at 0, 10, 50 min, 5 h and a 4 h chain: wave sizes equal build_clusters and group_and_grade's wave count, exactly"""
    t0 = T(20250915)
    times = [0, 600, 3000, 18000] + [36000 + 1200 * k for k in range(16)]
    fires = [(ALARM, 'C%d' % (i % 4), t0 + s, -1) for i, s in enumerate(times)]
    card = AU.build_card(bundle(fires), ctx())
    tw = table(card, 'T_WAVES')
    sizes = [r['size'] for r in tw]
    assert sizes == [2, 1, 1, 13, 3], sizes
    assert [r['flag'] for r in tw][-1] == 'CHAIN_SPLIT', tw[-1]
    R = rel()
    U = R.RU.build_clusters(fires)
    by = {}
    for r in U:
        by.setdefault(r[5], []).append(r)
    assert sizes == [len(by[c]) for c in sorted(by, key=lambda c: min(x[2] for x in by[c]))]
    tf = table(card, 'T_FIRES')
    assert sorted((r['parent_id'], r['wave'], r['wave_size']) for r in tf) == sorted((r[4], r[5], r[7]) for r in U)

    class D:
        pass
    ids = sorted(set(r['wave'] for r in tf))
    D.cl = np.array([ids.index(r['wave']) for r in tf])
    D.month = np.array([r['month'] for r in tf])
    waves, per = R.GG.size(D, np.arange(len(tf)))
    assert waves == len(tw) == 5, (waves, len(tw))
    when = {(r['kind'], r['key']): r['waves'] for r in table(card, 'T_WHEN')}
    assert [when.get(('month', m), 0) for m in R.GG.MONTHS] == per, (when, per)


# ------------------------------------------------------------------------------------------------------------------ U3
def test_U3():
    """10 planted events, one +100, nine -1: top1_share 100/91, net_ex_top1 -9, Q7 says carried by one event"""
    fires = [(ALARM, 'C%d' % i, T(20250915 + i, 43200), -1) for i in range(10)]
    nets = [100.0] + [-1.0] * 9
    money = [money_row(f[1], f[2], f[3], net=n) for f, n in zip(fires, nets)]
    card = AU.build_card(bundle(fires, money=money), ctx())
    a = [r for r in table(card, 'T_CONC') if r['slice'] == 'ALL'][0]
    assert a['waves'] == 10, a
    assert abs(a['top1_share'] - 100.0 / 91.0) < 1e-12, a
    assert abs(a['top5_share'] - 96.0 / 91.0) < 1e-12, a
    assert abs(a['net_ex_top1'] - (-9.0)) < 1e-12, a
    q7 = row(card, 7)
    assert 'carried by one event' in q7['answer'], q7
    # the same events with no big one: not carried by one event
    money2 = [money_row(f[1], f[2], f[3], net=1.0) for f in fires]
    q7b = row(AU.build_card(bundle(fires, money=money2), ctx()), 7)
    assert 'carried by one event' not in q7b['answer'], q7b


# ------------------------------------------------------------------------------------------------------------------ U4
def _u4(lone, wave):
    fires, money = [], []
    for d in range(40):
        day = int((dt.date(2025, 9, 12) + dt.timedelta(days=d)).strftime('%Y%m%d'))
        f = (ALARM, 'L%02d' % d, T(day, 3600), -1)
        fires.append(f); money.append(money_row(f[1], f[2], f[3], net=lone))
        for j in range(3):
            g = (ALARM, 'W%d' % j, T(day, 43200 + 300 * j), -1)
            fires.append(g); money.append(money_row(g[1], g[2], g[3], net=wave))
    return AU.build_card(bundle(fires, money=money), ctx())


def test_U4():
    """lone fires -1, waves of 3 +1: T_SINGLE exact; swapping the planted values flips Q8"""
    card = _u4(-1.0, 1.0)
    ts = {(r['size_bucket'], r['breadth']): r for r in table(card, 'T_SINGLE') if r['slice'] == 'ALL'}
    one, three = ts[('1', '1coin')], ts[('2-5', 'multi')]
    assert (one['waves'], one['fires']) == (40, 40) and abs(one['net'] + 1.0) < 1e-12, one
    assert (three['waves'], three['fires']) == (40, 120) and abs(three['net'] - 1.0) < 1e-12, three
    assert not any(r['waves'] for k, r in ts.items() if k not in (('1', '1coin'), ('2-5', 'multi'))), ts
    q8 = row(card, 8)
    assert q8['answer'].startswith('lone fires pay less'), q8
    q8s = row(_u4(1.0, -1.0), 8)
    assert q8s['answer'].startswith('lone fires pay more'), q8s


# ------------------------------------------------------------------------------------------------------------------ U5
def test_U5():
    """side -1 with only long liquidations reads longs forced; the mirror side +1 reads shorts; a 1-1 split names no side"""
    for side, lng, sht, want in ((-1, 1e6, 0.0, 'longs'), (1, 0.0, 1e6, 'shorts')):
        f = (ALARM, 'C1', T(20250920, 7200), side)
        fz = [dict(coin='C1', t=f[2], long_usd=lng, short_usd=sht, known_at=f[2])]
        card = AU.build_card(bundle([f], forced=fz), ctx())
        tf = table(card, 'T_FORCED')
        one = [r for r in tf if r['row'] == AU.parent_key(f)][0]
        assert one['forced'] == want and one['agree'] == 'yes', one
        a = [r for r in tf if r['row'] == 'ALL'][0]
        assert a['forced'] == want, a
        assert row(card, 4)['answer'].startswith(want + ' forced'), row(card, 4)
        assert ('forced ' + want) in row(card, 5)['answer'], row(card, 5)
    # a split (one fire long-only, one short-only, both side -1): no side is named (the 2 of 3 rule), Q5 names no payer
    f1, g1 = (ALARM, 'C1', T(20250920, 7200), -1), (ALARM, 'C2', T(20250923, 7200), -1)
    fz = [dict(coin='C1', t=f1[2], long_usd=1e6, short_usd=0.0, known_at=f1[2]),
          dict(coin='C2', t=g1[2], long_usd=0.0, short_usd=1e6, known_at=g1[2])]
    card = AU.build_card(bundle([f1, g1], forced=fz), ctx())
    a = [r for r in table(card, 'T_FORCED') if r['row'] == 'ALL'][0]
    assert a['forced'] == 'mixed', a
    assert row(card, 4)['answer'].startswith('no side'), row(card, 4)
    assert 'forced longs' not in row(card, 5)['answer'] and 'forced shorts' not in row(card, 5)['answer'], row(card, 5)


# ------------------------------------------------------------------------------------------------------------------ U6
def test_U6():
    """move in 4 pct, FADE gross 1h +2 pct: retained 0.50; move 0: empty with ZERO_MOVE"""
    f = (ALARM, 'C1', T(20250922, 3600), -1)
    g = (ALARM, 'C2', T(20250925, 3600), -1)
    rd = [reading('FIRE', 'C1', f[2], 'EPI.A02.run_pct', 4.0), reading('FIRE', 'C2', g[2], 'EPI.A02.run_pct', 0.0)]
    mo = [money_row('C1', f[2], -1, g15=1.0, g1h=2.0, g4h=3.0), money_row('C2', g[2], -1, g1h=2.0)]
    card = AU.build_card(bundle([f, g], readings=rd, money=mo), ctx())
    ti = {r['row']: r for r in table(card, 'T_IMPACT')}
    a = ti[AU.parent_key(f)]
    assert abs(a['retained_1h'] - 0.5) < 1e-12 and abs(a['retained_15m'] - 0.75) < 1e-12 and abs(a['retained_4h'] - 0.25) < 1e-12, a
    b = ti[AU.parent_key(g)]
    assert b['flag'] == 'ZERO_MOVE' and all(np.isnan(b[k]) for k in ('retained_15m', 'retained_1h', 'retained_4h')), b
    assert abs(ti['ALL']['retained_1h'] - 0.5) < 1e-12, ti['ALL']


# ------------------------------------------------------------------------------------------------------------------ U7
def null_bundle(seed, shift_code=None, shift=0.0):
    """fires drawn from the same distribution as the matched moments: every code, every month (the null)"""
    rng = np.random.default_rng(seed)
    lo, hi = T(20250910), T(20251231, 86399 - 7200)
    fires, seen = [], set()
    for st in np.sort(rng.integers(lo, hi, 600)):
        for j in range(int(rng.integers(1, 4))):
            c, t = 'N%02d' % int(rng.integers(0, 30)), int(st) + 600 * j
            if (c, t) in seen:
                continue
            seen.add((c, t)); fires.append((ALARM, c, t, int(rng.choice([-1, 1]))))
    rd, fz, mo = [], [], []
    for (_, c, t, s) in fires:
        for code in NULL_CODES:
            rd.append(reading('FIRE', c, t, code, float(rng.normal()) + (shift if code == shift_code else 0.0)))
            for k in range(2):
                tm = min(hi, max(lo, t - int(rng.integers(3600, 3 * 86400))))
                rd.append(reading('MATCH', 'M%02d' % int(rng.integers(0, 30)), tm, code, float(rng.normal())))
        fz.append(dict(coin=c, t=t, long_usd=float(rng.exponential(1e5)), short_usd=float(rng.exponential(1e5)), known_at=t))
        mo.append(money_row(c, t, s, net=float(rng.normal()), edge=float(rng.normal()), g15=float(rng.normal()),
                            g1h=float(rng.normal()), g4h=float(rng.normal())))
    return bundle(fires, readings=rd, forced=fz, money=mo)


def test_U7():
    """null: fires drawn from matched moments, 20 seeds: T_WHERE percentiles 40-60, at most 1 STRONG word in 20 (kill rule: STRONG
    words on nulls = fix the word rule, never tune on FDAOI). Control (not counted): one code shifted by 1.5 sd must read STRONG."""
    c = ctx()
    strong, measured = [], 0
    for seed in range(20):
        card = AU.build_card(null_bundle(seed), c)
        for r in table(card, 'T_WHERE'):
            if r['slice'] == 'ALL' and r['tag'] == 'ASOF':
                assert 40.0 <= r['fire_pct'] <= 60.0, (seed, r)
        for r in card['rows']:
            if r['word'] == 'STRONG':
                strong.append((seed, r['q'], r['answer']))
            measured += r['word'] == 'WEAK'
    assert measured >= 20 * 5, measured
    assert len(strong) <= 1, strong
    ctl = AU.build_card(null_bundle(99, shift_code='CTX.A02.btc_move_15m', shift=1.5), c)
    assert row(ctl, 3)['word'] == 'STRONG', row(ctl, 3)
    print('   U7 STRONG words on 20 nulls: %d of %d; control Q3: %s' % (len(strong), 20 * 8, row(ctl, 3)['word']))


# ------------------------------------------------------------------------------------------------------------------ U8
def test_U8():
    """look-ahead: a huge value planted after t changes no Q1-Q5 number (readings, forced liquidations and money after the fire)"""
    base = null_bundle(7)
    labels = dict(true_verdict='UNSURE', rule9='SIZE', family_tag='FORCED_LIQUIDATION')
    base['labels'] = labels
    c = ctx()
    card0 = AU.build_card(base, c)
    late = dict(base)
    late['readings'] = list(base['readings'])
    late['forced'] = list(base['forced'])
    for (_, coin, t, s) in base['fires']:
        for code in NULL_CODES:
            late['readings'].append(reading('FIRE', coin, t, code, 1e12, known_at=t + 3600))
            late['readings'].append(reading('MATCH', coin, t + 5, code, -1e12, known_at=t + 3605))
        late['forced'].append(dict(coin=coin, t=t, long_usd=1e15 if s > 0 else 0.0, short_usd=1e15 if s < 0 else 0.0, known_at=t + 60))
    late['money'] = [dict(m, net=m['net'] * 1e9, edge_tough=1e9, fade_gross_1h=1e9) for m in base['money']]
    card1 = AU.build_card(late, c)
    for q in (1, 2, 3, 4, 5):
        a, b = row(card0, q), row(card1, q)
        assert (a['answer'], a['numbers'], a['word']) == (b['answer'], b['numbers'], b['word']), (q, a, b)
    assert any(r['tag'] == 'AFTER' for r in table(card1, 'T_WHERE')), 'no AFTER row'
    assert row(card0, 6)['numbers'] != row(card1, 6)['numbers'], 'the planted values were not read at all'


TESTS = [('U%d' % i, globals()['test_U%d' % i]) for i in range(1, 9)]


def main(argv):
    pick = [t for t in TESTS if not argv or t[0] in argv]
    print('TOOL %s sha16 %s' % (TOOL, sha16(TOOL)))
    print('TEST %s sha16 %s' % (os.path.realpath(__file__), sha16(os.path.realpath(__file__))))
    passed = 0
    for name, fn in pick:
        t = time.time()
        try:
            fn()
            passed += 1
            print('PASS %s (%.1f s) %s' % (name, time.time() - t, fn.__doc__.split('\n')[0]))
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)[-1]
            print('FAIL %s (%.1f s) %s: %s at line %d' % (name, time.time() - t, type(e).__name__, str(e)[:600], tb.lineno))
    print('PASSED %d of %d' % (passed, len(pick)))
    return 0 if passed == len(pick) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
