"""BUILD3's plant tests for factory_v2 (= BUILD4's 7 for v1, carried over, + STRATEGY's 20:58:51Z rulings: a SIGN plant, the MATCHED rival,
the cost of record with funding, and a mutant per new guard). Seconds; temp roots on SCRATCH_DISK; never the real ledger or the research store;
no real-data money run. Run: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 tests/test_factory_v2.py"""
import csv, json, os, sys, tempfile, importlib
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
FACT = os.environ.get('FACTORY_DIR') or os.path.dirname(HERE)
sys.path.insert(0, FACT)
FV = importlib.import_module(os.environ.get('FACTORY_MOD', 'factory_v2'))
import fairness_bar as FB1                                            # noqa: E402
from labcore import ids                                               # noqa: E402

TMP = '<SCRATCH>/work_BUILD3/tmp_factory' if os.path.isdir('<SCRATCH>') else None
if TMP:
    os.makedirs(TMP, exist_ok=True)
EXITS = os.path.join(FV.TOOLS, 'exit_engine', 'EXITS_V1.tsv')
SETTINGS = 'team/LAYERS/tools/costs_v2/settings/COSTS_SETTINGS_V1.json'
RECORD = 'team/LAYERS/tools/costs_v2/receipts/COSTS_OF_RECORD_V1.tsv'
US = FV.US
R = []
LIMITS_SRC = """# planted T09 + T13 for the factory tests (NOT the real tools): open_max positions at once on one desk; coins in CAP_COINS capped
ORDER = []
CAP_COINS = %r
OPEN_MAX = %d
NAME = 'plant'
def load_settings():
    return {'open_max': OPEN_MAX}
def replay(decisions, settings):
    rows = []; open_ = []; ORDER.append([])
    for d in decisions:
        t = d['ctx']['t_us']; ORDER[-1].append((t, d['intent']['fire_id']))
        open_ = [x for x in open_ if x > t]
        if len(open_) >= settings['open_max']:
            rows.append({'result': 'REFUSE', 'code': 'L04'}); continue
        rows.append({'result': 'PASS', 'code': ''}); open_.append(d['ctx']['exit_us'])
    return rows
def entry_cap_fill(side, p_signal, t_signal, latency_s, settings, prices):
    te, c = prices(t_signal, t_signal + 30 * 1000000)
    if not (p_signal == p_signal) or not len(te):
        return ('MISSED', 'NOPRICE')
    return ('MISSED', 'CAP') if COIN[0] in CAP_COINS else ('FILL', float(c[0]))
COIN = ['']
"""


def limits_module(d, cap_coins=(), open_max=99):
    """a planted limits module file (pinned in the PREREG by sha16) and the loaded object; COIN is set by the prices callable's coin"""
    import importlib.util
    p = os.path.join(d, 'LIMITS_PLANT.py'); open(p, 'w').write(LIMITS_SRC % (tuple(cap_coins), open_max))
    spec = importlib.util.spec_from_file_location('limits_plant_%d' % len(R), p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return p, m


def T(name, ok, info=''):
    R.append(bool(ok)); print('%s %s %s' % ('PASS' if ok else 'FAIL', name, '' if ok else info))


class FakeCosts:
    """planted cost of record: fee 9 + book 10 + gap 14.4 bp; funding 2 bp a trade, or missing on the coins named"""
    def __init__(self, missing=()):
        self.missing = set(missing)

    def trade_cost(self, coin, side, t_in, t_out, size):
        miss = coin[0] in self.missing
        return dict(fee_bp=np.array([9.0]), book_bp=np.array([10.0]), gap_bp=np.array([14.4]),
                    total_bp=np.array([np.nan if miss else 35.4]), reason=np.array(['FUNDING_MISSING' if miss else ''], object))


def fires_plant(n=60, seed=1):
    """n fires on BTC/ETH/SOL over Oct-Nov 2025, about one a day (one wave each), push side alternating (even k: -1, a down push)"""
    rng = np.random.default_rng(seed)
    t0 = int(np.datetime64('2025-10-01T01:00:00', 's').astype(np.int64))
    t = t0 + np.arange(n) * 86400 + rng.integers(0, 600, n)
    coin = np.array(['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])[np.arange(n) % 3]
    side = np.where(np.arange(n) % 2 == 0, -1, 1)
    return {'coin': coin, 't': t.astype(np.int64), 'side': side, 'onset_t': t.astype(np.int64)}


def bars_plant(fires, edge_pct, only_side=None, near_s=3600, everywhere=False):
    """3 s paths: after a FIRE (within near_s) a drift of edge_pct against the push (a fade edge); far from fires (the matched moments) a
    null path, unless everywhere=True (the matched moments then carry the same edge: the MATCHED rival must stop the card)"""
    by = {}
    for c, t, s in zip(fires['coin'], fires['t'], fires['side']):
        by.setdefault(c, []).append((int(t) * US, int(s)))

    def fn(coin, t0, t1):
        te = np.arange(t0, t1 + 1, 3 * US, dtype=np.int64)
        tf, s = min(by[coin], key=lambda x: abs(x[0] - t0))
        rng = np.random.default_rng(int(t0 // US) % 2**32)
        steps = rng.normal(0, 0.0004, len(te)); k = np.arange(len(te))
        near = everywhere or abs(t0 - tf) <= near_s * US
        e = edge_pct if near and (only_side is None or s == only_side) else 0.0
        drift = -s * e / 100.0 * np.minimum(k / 600.0, 1.0)
        px = 100.0 * (1 + drift + np.cumsum(steps) * 0.2)
        return te, px, px * 1.0002, px * 0.9998
    return fn


def units_plant(codes, fires, first, last):
    return {c: (np.full(len(fires['t']), 1.0), fires['t'] * US) for c in codes}


def write_edges(path, fires):
    """two matched moments per parent, 12 h and 13 h after it (far from every fire), weight 1/2 each (alarm_match NOOWN form)"""
    with open(path, 'w') as f:
        f.write('fid\tcoin\tparent_t\tcand_t\tside\tweight\tdraw_index\town\n')
        for c, t, s in zip(fires['coin'], fires['t'], fires['side']):
            for k, dtc in enumerate((43200, 46800)):
                f.write('%s_%d\t%s\t%d.0\t%d.0\t%d\t0.5\t%d\t\n' % (c, t, c, t, t + dtc, s, k))


def prereg(fl_path, edges_path):
    return {'batch_id': 'T0', 'family': 'A02P', 'alarm': 'A02P', 'unit_subject': 'A02N',
            'fire_list': {'path': fl_path, 'sha16': ids.sha16_file(fl_path)}, 'months': ['202510', '202511'], 'budget_cards': 10,
            'inputs': [], 'situations': [], 'decisions': [{'id': 'FADE', 'side': 'FADE', 'inputs': [], 'line': 'fade'}],
            'entries': [{'id': 'E6', 'kind': 'taker', 'delay_s': 6}], 'exits_path': EXITS,
            'exits': [{'exit_id': 'EXIT_T1', 'exit_row_sha16': FV.XE.row_sha16(EXITS, 'EXIT_T1')}],
            'cost': {'settings': SETTINGS, 'settings_sha16': ids.sha16_file(FV._path(SETTINGS)), 'record': RECORD,
                     'record_sha16': ids.sha16_file(FV._path(RECORD))},
            'matched': {'path': edges_path, 'sha16': ids.sha16_file(edges_path)},
            'rivals': list(FV.RIVALS), 'windows_sha16': 'x', 'bars': {'min_mean_pct': 0.0}, 'judge_window': 'CHECK',
            'regime': {'kind': 'both'}, 'judges': [{'seat': 'A', 'code_sha16': 'a'}, {'seat': 'B', 'code_sha16': 'b'}]}


class Lim:
    """the planted limits as the factory's limits object: the cap sees the coin through the prices callable's closure"""
    def __init__(self, m):
        self.m = m; self.NAME = 'plant'; self.load_settings = m.load_settings; self.replay = m.replay

    def entry_cap_fill(self, side, ps, t, lat, st, prices):
        self.m.COIN[0] = prices.__closure__[1].cell_contents if prices.__closure__ else ''
        return self.m.entry_cap_fill(side, ps, t, lat, st, prices)


def setup(edge, P_edit=None, mod=None, cap_coins=(), open_max=99, **bars_kw):
    M = mod or FV
    d = tempfile.mkdtemp(prefix='fac2_', dir=TMP)
    lp, lm = limits_module(d, cap_coins, open_max)
    led = os.path.join(d, 'LEDGER.tsv'); open(led, 'w').write('\t'.join(M.LG.COLS) + '\n')
    fires = fires_plant(); fl = os.path.join(d, 'FIRES.tsv')
    with open(fl, 'w') as f:
        f.write('coin\tt\tside\tonset_t\n')
        for r in zip(fires['coin'], fires['t'], fires['side'], fires['onset_t']):
            f.write('%s\t%d\t%d\t%d\n' % r)
    ed = os.path.join(d, 'EDGES.tsv'); write_edges(ed, fires)
    P = prereg(fl, ed)
    P['limits'] = {'t09': {'path': lp, 'sha16': ids.sha16_file(lp)}, 't13': {'path': lp, 'sha16': ids.sha16_file(lp)}}
    if P_edit:
        P_edit(P)
    pp = os.path.join(d, 'PREREG.json'); json.dump(P, open(pp, 'w'))
    cfg = dict(root=d, ledger=led, types_path=os.path.join(d, 'TYPES.tsv'), research_root=os.path.join(d, 'research'),
               bars_fn=bars_plant(fires, edge, **bars_kw), values_fn=units_plant, units_fn=units_plant, skip_gate=True,
               costs_obj=FakeCosts(), refuse_inputs=lambda a, b: {}, tries_fn=lambda: FB1.read_tries({'ledger': led, 'types': os.path.join(d, 'TYPES.tsv')}),
               bar_settings={'flips': 200, 'day_boot': 200}, no_trades_write=True, limits_obj=Lim(lm),
               matched_units_fn=lambda codes, mo, f, l: {c: (np.full(len(mo['t']), 1.0), (mo['t'] * US).astype(np.int64)) for c in codes})
    cfg['_lim'] = lm
    return d, pp, cfg


def rows(bp):
    return {r['card_id']: r for r in csv.DictReader((l for l in open(bp) if not l.startswith('#')), delimiter='\t')}


def run_batch(edge, P_edit=None, cfg_edit=None, mod=None, **bars_kw):
    M = mod or FV
    d, pp, cfg = setup(edge, P_edit, mod=M, **bars_kw)
    if cfg_edit:
        cfg_edit(cfg)
    b = M.generate(pp, cfg)
    return d, b, cfg, M.run(b, cfg, log=lambda *a: None)


def t_refusals():
    d, pp, cfg = setup(0.0)
    bad = []
    for edit, word in ((lambda P: P['months'].append('202603'), 'BUILD months only'),
                       (lambda P: P['rivals'].remove('NO_TRADE'), 'rivals'),
                       (lambda P: P['exits'][0].__setitem__('exit_row_sha16', '0' * 16), 'exit row'),
                       (lambda P: P['fire_list'].__setitem__('sha16', '0' * 16), 'fire list'),
                       (lambda P: P.__setitem__('budget_cards', 2), 'budget'),
                       (lambda P: P['matched'].__setitem__('sha16', '0' * 16), 'MATCHED'),
                       (lambda P: P['cost'].__setitem__('record_sha16', '0' * 16), 'cost record'),
                       (lambda P: P['entries'].append({'id': 'TRIG', 'kind': 'trigger', 'delay_s': 0}), 'RANDOM_DELAY'),
                       (lambda P: P.pop('limits'), 'limits missing'),
                       (lambda P: P['limits']['t09'].__setitem__('sha16', '0' * 16), 'limits t09')):
        P = json.load(open(pp)); edit(P); q = pp + '.bad'; json.dump(P, open(q, 'w'))
        try:
            FV.generate(q, cfg); bad.append('not refused: ' + word)
        except ValueError as x:
            if word not in str(x):
                bad.append((word, str(x)))
    T('F1 refusals: BUILD months, rivals, exit row, fire list, budget, MATCHED edges, cost record, a triggered entry, limits missing or moved', not bad, bad)


def t_edge_null_and_sign():
    d, b, cfg, bp = run_batch(4.0)
    Rr = rows(bp)
    fade = float(Rr['T0.ALARM_ONLY_FADE.EXIT_T1']['net_per_trade']); fol = float(Rr['T0.ALARM_ONLY_FOLLOW.EXIT_T1']['net_per_trade'])
    T('F2 a fade edge reads + for FADE and - for FOLLOW; NO_TRADE books 0', fade > 0 > fol and float(Rr['T0.NO_TRADE.EXIT_T1']['net_per_wave']) == 0.0,
      (fade, fol))
    d0, b0, cfg0, bp0 = run_batch(0.0)
    c0 = [r for r in rows(bp0).values() if r['rival'] == '-'][0]
    T('F3 the null never clears', c0['verdict'] != 'CLEARS', c0)


def t_sign_plant(mod=None):
    """SIGN plant (ruling 1): a DOWN push (push_side -1, longs forced) is faded with a BUY (+1); an UP push with a SELL"""
    M = mod or FV
    fires = {'coin': np.array(['BTCUSDT', 'ETHUSDT']), 't': np.array([0, 10], np.int64), 'push_side': np.array([-1, 1])}
    card = {'card_id': 'x', 'entry': {'delay_s': 6}, 'situation': {'rules': []}, 'decisions': [{'side': 'FADE'}]}
    side, st = M.decide(card, fires, np.array([True, True]), {})
    card['decisions'][0]['side'] = 'FOLLOW'; side2, _ = M.decide(card, fires, np.array([True, True]), {})
    return list(side) == [1, -1] and list(side2) == [-1, 1], (list(side), list(side2))


def t_determinism_rerun_change():
    _, _, _, a = run_batch(4.0); _, _, _, b = run_batch(4.0)
    strip = lambda p: [l.split('\t', 1)[1] for l in open(p) if not l.startswith('#')]
    T('F5 determinism: two runs, the same receipt', strip(a) == strip(b))
    d, b, cfg, bp = run_batch(4.0)
    try:
        FV.run(b, cfg, log=lambda *x: None); ok = False
    except PermissionError as x:
        ok = 'one run per batch' in str(x)
    T('F6 a second run of a batch is refused', ok)
    d, pp, cfg = setup(4.0); b = FV.generate(pp, cfg)
    man = json.load(open(os.path.join(d, 'cards', b, 'BATCH.json'))); p = os.path.join(d, 'cards', b, '%s.json' % man['cards'][1]['card_sha16'])
    c = json.load(open(p)); c['entry']['delay_s'] = 0; open(p, 'w').write(FV._canon(c))
    try:
        FV.run(b, cfg, log=lambda *x: None); ok = False
    except ValueError as x:
        ok = 'changed' in str(x)
    T('F7 a card changed after generate is refused', ok)


def t_lookahead():
    late = lambda codes, fires, f, l: {c: (np.full(len(fires['t']), 1.0), fires['t'] * US + 60 * US) for c in codes}
    d, pp, cfg = setup(4.0, lambda P: P.update(inputs=[{'code': 'EPI.A02N.x', 'use': 'situation', 'brief': 'b', 'known_at_after_decision_s': 0}],
                                                situations=[{'id': 'S1', 'rules': [{'code': 'EPI.A02N.x', 'op': '>=', 'value': 0}]}]))
    cfg['values_fn'] = late; b = FV.generate(pp, cfg)
    try:
        FV.run(b, cfg, log=lambda *x: None); ok = False
    except Exception as x:
        ok = 'known' in str(x).lower() or 'lookahead' in type(x).__name__.lower()
    T('F8 the join guard refuses a value known 60 s after the decision', ok)


SITS = [{'id': 'DOWN', 'rules': [{'code': 'EPI.A02N.x', 'op': '>=', 'value': 1}]}, {'id': 'UP', 'rules': [{'code': 'EPI.A02N.x', 'op': '<', 'value': 1}]}]
INS = [{'code': 'EPI.A02N.x', 'use': 'situation', 'brief': 'b', 'known_at_after_decision_s': 0}]


def vals(codes, fires, f, l):
    return {c: ((fires['push_side'] == -1).astype(float), fires['t'] * US) for c in codes}


def planted_clear(mod=None, everywhere=False, missing=(), cfg_edit=None, P_more=None, keep=None, **kw):
    M = mod or FV
    d, pp, cfg = setup(4.0, lambda P: (P.update(inputs=INS, situations=SITS), P_more and P_more(P)), mod=M, only_side=-1, everywhere=everywhere, **kw)
    cfg['values_fn'] = vals; cfg['costs_obj'] = FakeCosts(missing)
    if cfg_edit:
        cfg_edit(cfg)
    b = M.generate(pp, cfg)
    bp = M.run(b, cfg, log=lambda *x: None)
    if keep is not None:
        keep.update(d=d, b=b, cfg=cfg, bp=bp)
    return rows(bp)


def t_planted_clear_and_matched():
    Rr = planted_clear()
    dn, up = Rr['T0.DOWN.FADE.E6.EXIT_T1'], Rr['T0.UP.FADE.E6.EXIT_T1']
    T('F9 the planted edge clears (DOWN beats NO_TRADE, FADE-all, FOLLOW-all and its MATCHED twin, bar PASS); its mirror UP does not',
      dn['verdict'] == 'CLEARS' and up['verdict'] != 'CLEARS', (dn['verdict'], dn['bar_verdict'], dn['matched_net_per_wave'], up['verdict']))
    T('F10 every card of the batch is a counted try (3 rivals + 2 cards): the MATCHED twin is a rival, never a try', 'tries 5' in dn['bar_line'], dn['bar_line'])
    Rm = planted_clear(everywhere=True)
    dm = Rm['T0.DOWN.FADE.E6.EXIT_T1']
    T('F11 MATCHED rival: when the matched moments carry the same edge, the card adds nothing and does NOT clear', dm['verdict'] != 'CLEARS'
      and dm['beats_rivals'] == '0', (dm['verdict'], dm['net_per_wave'], dm['matched_net_per_wave'], dm['matched_gain_lo']))
    Rf = planted_clear(missing=('BTCUSDT',))
    df = Rf['T0.DOWN.FADE.E6.EXIT_T1']
    T('F12 funding missing on a traded coin caps the verdict at INCOMPLETE and is counted', df['verdict'] == 'INCOMPLETE' and int(df['funding_missing']) > 0,
      (df['verdict'], df['funding_missing']))
    return dn


def t_seconds():
    """MUST 2: whole seconds on both sides, so floor and round never meet"""
    def frac_edges(P):
        t = open(P['matched']['path']).read().replace('.0\t', '.6\t', 1); open(P['matched']['path'], 'w').write(t)
        P['matched']['sha16'] = ids.sha16_file(P['matched']['path'])
    try:
        run_batch(4.0, frac_edges); ok = False
    except ValueError as x:
        ok = 'whole second' in str(x)
    T('F13 an edge parent_t with a fraction (x.6 s) is refused', ok)
    def frac_fires(P):
        L = open(P['fire_list']['path']).read().split('\n'); a = L[1].split('\t'); a[1] += '.4'; L[1] = '\t'.join(a)
        open(P['fire_list']['path'], 'w').write('\n'.join(L)); P['fire_list']['sha16'] = ids.sha16_file(P['fire_list']['path'])
    try:
        run_batch(4.0, frac_fires); ok = False
    except ValueError as x:
        ok = 'whole seconds' in str(x)
    T('F14 a fire time with a fraction (x.4 s) is refused', ok)


def own_units(v, late_s=0):
    return lambda codes, mo, f, l: {c: (np.full(len(mo['t']), v), (mo['t'] * US).astype(np.int64) + late_s * US) for c in codes}


def t_units(mod=None):
    """MUST 3: the matched moments trade on their own unit"""
    M = mod or FV
    a = planted_clear(mod=M, everywhere=True, cfg_edit=lambda c: c.update(matched_units_fn=own_units(1.0)))['T0.DOWN.FADE.E6.EXIT_T1']
    b = planted_clear(mod=M, everywhere=True, cfg_edit=lambda c: c.update(matched_units_fn=own_units(0.2)))['T0.DOWN.FADE.E6.EXIT_T1']
    return a['matched_net_per_wave'] != b['matched_net_per_wave'] and a['net_per_wave'] == b['net_per_wave'], (a['matched_net_per_wave'], b['matched_net_per_wave'])


def t_units_guards():
    try:
        planted_clear(cfg_edit=lambda c: c.update(matched_units_fn=own_units(1.0, late_s=60))); ok = False
    except Exception as x:
        ok = 'known' in str(x).lower() or 'lookahead' in type(x).__name__.lower()
    T('F16 a matched moment unit known 60 s after the moment decision is refused', ok)
    try:
        planted_clear(cfg_edit=lambda c: c.pop('matched_units_fn')); ok = False
    except ValueError as x:
        ok = 'MUST 3' in str(x)
    T('F17 a unit exit without a moment unit reader is refused', ok)
    r = planted_clear(cfg_edit=lambda c: c.update(matched_units_fn=own_units(np.nan)))['T0.DOWN.FADE.E6.EXIT_T1']
    T('F18 moments without their unit are dropped and counted, the twin then unpriced and the card not clear', int(r['matched_nounit']) > 0
      and r['verdict'] != 'CLEARS', (r['matched_nounit'], r['verdict']))


def t_limits(mod=None, open_max=1):
    """MUST 1: time-order replay through T13's cap and T09's desk; capped and refused entries are MISSED with reason, never dropped"""
    M = mod or FV
    K = {}
    Rr = planted_clear(mod=M, cap_coins=('ETHUSDT',), open_max=open_max, keep=K)
    r = Rr['T0.ALARM_ONLY_FADE.EXIT_T1']
    order = K['cfg']['_lim'].ORDER
    mp = os.path.join(K['d'], 'runs', K['b'], 'MISSED_%s.tsv' % r['card_sha16'])
    mrows = list(csv.DictReader(open(mp), delimiter='\t'))
    return r, order, mrows


def t_limits_tests():
    r, order, mrows = t_limits()
    T('F19 capped entries are MISSED with reason T13_CAP, counted beside the trades', int(r['missed']) > 0 and 'T13_CAP' in r['missed_reasons']
      and any(m['reason'] == 'T13_CAP' and m['coin'] == 'ETHUSDT' for m in mrows), (r['missed'], r['missed_reasons']))
    T('F21 the desk sees each card\'s decisions in time order', len(order) > 1 and all(len(o) > 1 and o == sorted(o) for o in order if o), [o[:2] for o in order[:2]])
    r0, _, m0 = t_limits(open_max=0)
    T('F20 T09 refusals (no open position allowed) are MISSED rows with code T09_L04, would-be path kept, no trade left', 'T09_L04' in r0['missed_reasons']
      and r0['trades'] == '0' and all(m['would_be_ret_pct'] != 'nan' for m in m0 if m['reason'] == 'T09_L04'), (r0['missed_reasons'], r0['trades']))
    K = {}
    Rd = planted_clear(P_more=lambda P: P.__setitem__('limits', {'deferred': 'STRATEGY TEST ruling 2026-10-23T00:00:00Z'}),
                       cfg_edit=lambda c: c.pop('limits_obj'), keep=K)
    T('F22 a STRATEGY deferral runs without limits and the batch says so', 'LIMITS DEFERRED (STRATEGY TEST' in open(K['bp']).readline()
      and Rd['T0.DOWN.FADE.E6.EXIT_T1']['missed'] == '0', open(K['bp']).readline()[:120])
    sp = open(FV.sheet(K['b'], K['cfg'])).read()
    T('F24 deferred: every result row and the sheet say risk limits not replayed; the most open at once is on every row',
      all(r['limits'] == 'risk limits not replayed' and r['max_open_at_entry'] != '' for r in Rd.values()) and 'risk limits not replayed' in sp,
      [(r['limits'], r['max_open_at_entry']) for r in Rd.values()])
    ok, info = t_open_book()
    T('F25 open trades at entry and the coin open notional: four planted trades, one closed before the last entry', ok, info)
    K = {}
    Rp = planted_clear(cap_coins=('ETHUSDT',), cfg_edit=lambda c: c.pop('limits_obj'), keep=K)
    T('F23 the pinned limits modules load from their PREREG paths (sha16 checked) when none is injected', 'LIMITS T09 ' in open(K['bp']).readline(),
      open(K['bp']).readline()[:160])


def t_open_book(mod=None):
    M = mod or FV
    fires = {'coin': np.array(['BTCUSDT', 'BTCUSDT', 'ETHUSDT', 'BTCUSDT', 'BTCUSDT']), 't': np.array([0, 10, 20, 500, 30], np.int64)}
    col = {'status': np.array([0, 0, 0, 1, 0]), 'entry_us': np.array([0, 100, 150, -1, 250], np.int64) * US,
           'exit_us': np.array([200, 300, 400, -1, 450], np.int64) * US}
    M.open_book(fires, col, 10000.0)
    got = (col['open_at_entry'][[0, 1, 2, 4]].tolist(), col['coin_open_usd'][[0, 1, 2, 4]].tolist(), bool(np.isnan(col['open_at_entry'][3])))
    return got == ([0, 1, 2, 2], [0.0, 10000.0, 0.0, 10000.0], True), got


def mutant(old, new):
    src = open(os.path.join(FACT, 'factory_v2.py')).read()
    assert src.count(old) == 1, old
    md = tempfile.mkdtemp(prefix='fac2m_', dir=TMP); open(os.path.join(md, 'factory_v2_mut.py'), 'w').write(src.replace(old, new))
    sys.path.insert(0, md); m = importlib.import_module('factory_v2_mut'); sys.path.pop(0); sys.modules.pop('factory_v2_mut')
    for k, v in vars(FV).items():                                     # the mutant resolves every home path from the real home
        if k.isupper() and isinstance(v, str) and getattr(m, k, None) != v:
            setattr(m, k, v)
    return m


def t_mutants():
    m1 = mutant("sgn = {'FADE': -1, 'FOLLOW': 1, 'SKIP': 0}[d]", "sgn = {'FADE': 1, 'FOLLOW': -1, 'SKIP': 0}[d]")
    T('M1 mutant (FADE = +push) fails the SIGN plant', not t_sign_plant(m1)[0])
    m2 = mutant("            mwm[s] = wave_means_of(matched_twin(c, fires, cols[s], cfg, units, C, edges, L, mst[s]), cols[s]['status'], cols[s]['wave'])",
                "            pass")
    d2 = planted_clear(mod=m2, everywhere=True)['T0.DOWN.FADE.E6.EXIT_T1']
    T('M2 mutant (MATCHED rival dropped) lets the card clear where F11 stops it', d2['verdict'] == 'CLEARS', d2['verdict'])
    m3 = mutant("    if why == 'FUNDING_MISSING':\n        return (float(c['fee_bp'][0]) + float(c['book_bp'][0]) + float(c['gap_bp'][0])) / 100.0, 0",
                "    if why == 'FUNDING_MISSING':\n        return (float(c['fee_bp'][0]) + float(c['book_bp'][0]) + float(c['gap_bp'][0])) / 100.0, 1")
    d3 = planted_clear(mod=m3, missing=('BTCUSDT',))['T0.DOWN.FADE.E6.EXIT_T1']
    T('M3 mutant (missing funding counted as priced) escapes INCOMPLETE, failing F12', d3['verdict'] != 'INCOMPLETE', d3['verdict'])
    m4 = mutant("        if not ok.any() or not matched_lo > 0:", "        if not ok.any() or a[ok].mean() <= b[ok].mean():")
    d4 = [planted_clear(mod=m4, everywhere=True)['T0.DOWN.FADE.E6.EXIT_T1']['verdict']]
    T('M4 mutant (twin beaten on the raw mean, not the paired wave bound) lets the equal-edge card clear', 'CLEARS' in d4, d4)
    m5 = mutant("    if not m.get('path') or ids.sha16_file(_path(m['path'])) != m.get('sha16'):", "    if not m.get('path'):")
    d5, pp5, cfg5 = setup(0.0, lambda P: P['matched'].__setitem__('sha16', '0' * 16), mod=m5)
    try:
        m5.generate(pp5, cfg5); ok5 = True
    except ValueError:
        ok5 = False
    T('M5 mutant (MATCHED edges sha unchecked) accepts a wrong edges file, failing F1', ok5)
    m6 = mutant("            r = trade(card, fires, i, col['side'][i], bars_fn, X, frozen, units, C, size, t_override=ct, unit_override=uo)",
                "            r = trade(card, fires, i, col['side'][i], bars_fn, X, frozen, units, C, size, t_override=ct)")
    T('M6 mutant (moments on the FIRE unit) fails F15', not t_units(m6)[0])
    m7 = mutant("    order = sorted(np.nonzero(st == STATUS['TRADE'])[0], key=lambda i: (int(col['t_dec'][i]), fid[i]))",
                "    order = sorted(np.nonzero(st == STATUS['TRADE'])[0], key=lambda i: fid[i])")
    _, o7, _ = t_limits(m7)
    T('M7 mutant (decisions by fire id, not time) fails F21', any(o != sorted(o) for o in o7), [o[:2] for o in o7[:2]])
    m8 = mutant("        st[i] = STATUS['MISSED']; col['net_pct'][i] = 0.0", "        pass")
    r8, _, _ = t_limits(m8)
    T('M8 mutant (refused entries kept as trades) fails F19', int(r8['missed']) == 0, r8['missed'])
    m9 = mutant("        op = (ent < ent[j]) & (ext > ent[j]) | ((ent == ent[j]) & (np.arange(len(ix)) < j) & (ext > ent[j]))",
                "        op = (ent < ent[j])")
    T('M9 mutant (closed trades counted as open) fails F25', not t_open_book(m9)[0], t_open_book(m9)[1])


if __name__ == '__main__':
    t_refusals(); t_edge_null_and_sign(); t_seconds()
    ok, info = t_units(); T('F15 a matched moment trades on its OWN unit (its stop and target move with it), the card on the fire unit', ok, info)
    t_units_guards(); t_limits_tests()
    ok, info = t_sign_plant(); T('F4 SIGN plant: a down push fades with a BUY, follows with a SELL', ok, info)
    t_determinism_rerun_change(); t_lookahead(); t_planted_clear_and_matched(); t_mutants()
    print('FACTORY V2 TESTS %d of %d' % (sum(R), len(R))); sys.exit(0 if all(R) else 1)
