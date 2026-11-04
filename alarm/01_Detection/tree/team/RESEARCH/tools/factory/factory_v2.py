"""factory_v2.py (BUILD3, taking over from BUILD4, 23 Oct 2026; ASK STRATEGY-210500; owner STRATEGY) = factory_v1 e90cce41 + STRATEGY's
rulings of 20:58:51Z on BUILD4's four choices and the re-nest:
  (1) SIDE: FADE = -push_side, FOLLOW = +push_side (LONGS -1, SHORTS +1): kept, now proven by a SIGN plant (a down push fades with a BUY).
  (2) WAVE VALUE: SKIP / UNDECIDED book 0, NOPRICE NaN, a wave = mean over its resolved fires: kept.
  (3) CLEARS = fairness_bar_v2 PASS AND a by-wave mean above EVERY rival: NO_TRADE, FADE-all, FOLLOW-all, and now MATCHED: the same card
      on its alarms' matched moments (alarm_match V3_4, NOOWN edges, PREREG 'matched' {path, sha16}): every parent fire the card trades is
      replaced by its matched candidates (same side relative to the parent's push, same entry delay, exit row and cost), the parent's value =
      the edge-weighted mean of its candidates' net, booked in the parent's wave. A card whose matched twin cannot be priced on a wave
      loses that wave from the comparison (counted). RANDOM_DELAY (T08 section 6) is owed only for TRIGGERED entries; factory_v2 takes
      fixed-delay taker entries only and refuses any other kind (a triggered entry needs T08's RANDOM_DELAY side file first).
  (4) COST: the cost of record, costs V3_5 (team/LAYERS/tools/costs_v2/costs_v3.py Costs.trade_cost: fee + book + gap + funding on the
      entry notional, bp); funding from the HL settled hourly store (read_month of hl_funding_pull_v1); a traded fire whose funding is
      missing keeps its fee + book + gap, is counted FUNDING_MISSING, and caps the verdict at INCOMPLETE (never filled).
  RE-NEST: labcore V2_4, exit_engine V1_4 (frozen manifest with exits_schema_sha16), fairness_bar V2_3; the fire list of record for A02P is
  A02P_EVENTS_SEPFEB_V3 6d24c9b7 (read with alarm_profile.load_alarms: that list has no onset_t column, so it is refused until its reader
  takes it; asked of its owner). No real-data money run is made by this edition's tests.
  LAB1 21:19:21Z MUSTs (V1 -> V2 of the release):
  (M1) LIMITS: each card's trades are replayed IN TIME ORDER (decision time, then fire id) through T13's research entry cap
       (entry_cap_fill) and T09's risk limits (replay: check() with the YES rows, one desk); a capped or refused entry is a MISSED row
       (status 6, net 0 like a fire not taken, its would-be path kept, its reason in MISSED_<card>.tsv), never dropped. The PREREG names
       'limits' = {t09: {path, sha16}, t13: {path, sha16}} (modules exposing load_settings/replay and entry_cap_fill) or
       {deferred: <STRATEGY ruling, with its stamp>}; neither = refused. The MATCHED twin's moments pass the same entry cap (a capped
       moment books 0); the desk replay is the card's own (a weighted twin has no single desk). STRATEGY 21:22:39Z ruled the replay
       DEFERRED for BUILD research runs only while T09 / T13 are not built: every trade then carries open_at_entry and coin_open_usd, every
       result row and the sheet say 'risk limits not replayed'; no CHECK look and no paper use until run 0 is replayed through them.
  (M2) SECONDS: a fire's time and an edge's parent time must be whole seconds (the stored second); a fraction on either side is refused,
       so the two never meet through different rounding (QUANT 21:12:38Z floor/round fault).
  (M3) UNITS: a matched moment's stop and target use THAT moment's own unit, known at or before its own decision (matched_units_fn,
       join guard); a moment without its unit is dropped from its parent's mean and counted (matched_nounit).
factory_v1.py (BUILD4, 23 Oct 2026; ASK STRATEGY-141639; design README.md b009d107e9a4565d, research RESEARCH_FACTORY.md a2e75cf2,
plan LEAD/STRATEGY_FACTORY_V1.md 9ab91f54; owner STRATEGY/LEAD, tester TEST1, panel QUANT + SCOUT + LAB1). PAPER: nothing trades.
THE STRATEGY FACTORY, stations 6 and 7: a frozen batch of strategy cards of ONE alarm family, every card run the same way on BUILD months,
by wave, after full cost, against the rivals, and the T02 fairness bar computed with EVERY card of the batch counted as a try.
  generate <prereg.json>   validate the batch PREREG, expand it into cards (freeze_judge V2 schema + the factory's situation, decision side
                           and entry), write cards/<batch_sha16>/ whole, one ledger PREREG row per card (ledger_add_v6, typed
                           STRATEGY_MONEY, the batch family); refuses a batch over its stated card budget. -> batch_sha16
  run <batch_sha16>        every card and rival: eligible fires (BUILD months, EMBARGO across the window end), situation and decision
                           (join guard on every input), entry at the first 3 s bar starting at or after fire + delay, exit through
                           exit_engine.run_frozen, cost through labcore.costs, waves through labcore.waves, the bar through fairness_bar_v2;
                           writes TRADES.<card> parts (lab3.write), one per-wave receipt per card, BATCH_<sha16>.tsv, a RESULT ledger row.
  sheet <batch_sha16>      SHEET_<sha16>.md: the plain-words page for the owner.
SET LIST (imported, never copied): labcore ids, gates (windows, window_of, outcome_allowed, month_last_day), waves (waves, by_wave),
lookahead (join_guard), costs (cost_c), briefs (refuse_inputs), jobgate (gate_wait); exit_engine_v1 (row_sha16, load_exits, run_frozen,
bars, census); fairness_bar_v2 (bar); ledger_add_v6 (prereg, result); alarm_profile (load_alarms, read).
NEW COMPUTATION here, and only this: the per-card trade assembly (which fires trade, which side, the entry bar) and the batch receipt.
BUILD4 CHOICES pending STRATEGY's ruling (asked on hb/BUILD4): (1) side: FADE = -push_side, FOLLOW = +push_side (push_side LONGS = -1);
(2) a fire the card SKIPS or cannot decide (UNDECIDED) books 0 in its wave, a NOPRICE trade is NaN; a wave's value = the mean over its
resolved fires (NaN only when none is resolved: UNRESOLVED for T02); (3) CLEARS = the T02 bar PASS AND a by-wave mean above every rival's
on the same waves; (4) cost without funding (labcore.costs V1) caps every verdict at INCOMPLETE until costs V2 lands."""
import csv, datetime, io, json, os, sys, zlib
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.dirname(HERE)
FORENSICS = os.path.realpath(os.path.join(TOOLS, '..', '..', '..'))
for p in (TOOLS, os.path.join(TOOLS, 'exit_engine'), os.path.join(TOOLS, 'fairness_bar'), os.path.join(TOOLS, 'ledger'),
          os.path.join(TOOLS, 'alarm_profile')):
    if p not in sys.path:
        sys.path.insert(0, p)
from labcore import ids, gates, waves as LW, lookahead, costs, briefs, jobgate   # noqa: E402
COSTS_DIR = os.path.join(FORENSICS, 'team', 'LAYERS', 'tools', 'costs_v2')
FUND_DIR = os.path.join(FORENSICS, 'team', 'LAYERS', 'tools', 'hl_funding_pull_v1')
for p in (COSTS_DIR, FUND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)
import costs_v3 as CV                                                         # noqa: E402  (costs V3_5, the cost of record)
import exit_engine_v1 as XE                                                   # noqa: E402
import fairness_bar_v2 as FB                                                  # noqa: E402
import ledger_add_v6 as LG                                                    # noqa: E402

VERSION = 'factory_v2'
LAB3_CODE = os.path.join(FORENSICS, 'team', 'LAB3', 'code')
RIVALS = ('NO_TRADE', 'ALARM_ONLY_FADE', 'ALARM_ONLY_FOLLOW')
SIDES = ('FADE', 'FOLLOW', 'SKIP')
OPS = {'>=': np.greater_equal, '>': np.greater, '<=': np.less_equal, '<': np.less, '==': np.equal}
GAP_S = 1800
US = 1_000_000
STATUS = {'TRADE': 0, 'SKIP': 1, 'UNDECIDED': 2, 'NOPRICE': 3, 'EMBARGO': 4, 'NOCOST': 5, 'MISSED': 6}
VERDICT_LEDGER = {'CLEARS': 'PASS', 'FAILS': 'FAIL', 'INCOMPLETE': 'UNSURE', 'UNRELIABLE': 'UNSURE'}
TRADE_FIELDS = (('status', 'STATUS code: 0 TRADE 1 SKIP 2 UNDECIDED 3 NOPRICE 4 EMBARGO 5 NOCOST 6 MISSED (T13 cap or T09 refusal)', 'code'),
                ('side', 'traded side: +1 long, -1 short, 0 no trade', 'sign'),
                ('wave', 'wave id (labcore.waves, gap 1800 s, over the eligible fires of the batch)', 'id'),
                ('entry_us', 'entry bar end time (first 3 s bar starting at or after fire + delay)', 'us'),
                ('entry_px', 'entry price: that bar close (Binance 3 s bins, a model price)', 'px'),
                ('exit_us', 'exit bar end time (exit_engine); -1 when NOPRICE', 'us'),
                ('ret_pct', 'gross return of the trade, signed by side', 'pct'),
                ('cost_pct', 'full cost of the trade: fee + book + gap + funding (costs V3_5), pct of the entry notional', 'pct'),
                ('funding_ok', '1 funding priced, 0 FUNDING_MISSING (fee + book + gap only; verdict capped at INCOMPLETE)', 'code'),
                ('net_pct', 'ret_pct - cost_pct; 0 for SKIP, UNDECIDED and MISSED; NaN for NOPRICE', 'pct'),
                ('path_clean', '1 CLEAN, 0 PATH_UNCERTAIN, -1 UNRESOLVED (exit_engine path_evidence_status)', 'code'),
                ('open_at_entry', "the card's trades still open at this trade's entry (entries before it, exits after it), this one excluded", 'count'),
                ('coin_open_usd', "the card's open notional on this coin at this trade's entry, this one excluded (USD)", 'usd'))
NOT_REPLAYED = 'risk limits not replayed'


# ---------------------------------------------------------------- small helpers
def _write_whole(path, data):
    """tmp + fsync + os.replace (TOOL_DESIGN 5a)"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(data if isinstance(data, bytes) else data.encode()); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)


def _canon(obj):
    return json.dumps(obj, sort_keys=True, indent=1)


def _path(p):
    return p if os.path.isabs(p) else os.path.join(FORENSICS, p)


def _now(cfg):
    return cfg.get('now_utc') or LG.now_utc(cfg.get('clock'))


def _day_start_us(day):
    return int(np.datetime64('%s-%s-%sT00:00:00' % (day[:4], day[4:6], day[6:8]), 'us').astype(np.int64))


def _utc_day(t_us):
    return np.datetime_as_string(np.asarray(t_us, np.int64).astype('datetime64[us]'), unit='D').astype('U10')


# ---------------------------------------------------------------- generate
def validate(P, cfg):
    """every refusal before a card is written; -> the briefs of the inputs"""
    for k in ('batch_id', 'family', 'alarm', 'fire_list', 'months', 'budget_cards', 'decisions', 'entries', 'exits', 'cost', 'rivals',
              'windows_sha16', 'bars', 'judge_window', 'regime', 'judges'):
        if P.get(k) in (None, '', []):
            raise ValueError('PREREG lacks %s: refused' % k)
    if P['family'] not in LG.known_families(cfg.get('families_path')):
        raise ValueError('family %r is not a FAMILIES_V2 family: refused' % P['family'])
    wins = gates.windows(cfg.get('windows'))
    for m in P['months']:
        if gates.window_of(m, wins) != 'BUILD':
            raise ValueError('month %s is in the %s window: the factory runs BUILD months only: refused' % (m, gates.window_of(m, wins)))
    fl = P['fire_list']
    if ids.sha16_file(_path(fl['path'])) != fl.get('sha16'):
        raise ValueError('fire list %s is not the frozen sha16 %s: refused' % (fl['path'], fl.get('sha16')))
    miss = [r for r in RIVALS if r not in P['rivals']]
    if miss:
        raise ValueError('rivals %s missing: every batch runs NO_TRADE, ALARM_ONLY_FADE and ALARM_ONLY_FOLLOW: refused' % miss)
    for d in P['decisions']:
        if d.get('side') not in SIDES:
            raise ValueError('decision %s: side %r not in %s: refused' % (d.get('id'), d.get('side'), SIDES))
    for e in P['entries']:
        if e.get('kind') != 'taker' or float(e.get('delay_s', -1)) < 0:
            raise ValueError('entry %s: taker with delay_s >= 0 only (a triggered entry needs T08 RANDOM_DELAY first): refused' % e.get('id'))
    ex_path = _path(P['exits_path'])
    for x in P['exits']:
        if XE.row_sha16(ex_path, x['exit_id']) != x.get('exit_row_sha16'):
            raise ValueError('exit row %s is not the frozen sha16 %s: refused' % (x['exit_id'], x.get('exit_row_sha16')))
    c = P['cost']
    for k in ('settings', 'record'):
        if ids.sha16_file(_path(c[k])) != c.get(k + '_sha16'):
            raise ValueError('cost %s %s is not the frozen sha16 %s: refused' % (k, c[k], c.get(k + '_sha16')))
    m = P.get('matched') or {}
    if not m.get('path') or ids.sha16_file(_path(m['path'])) != m.get('sha16'):
        raise ValueError('matched moments (alarm_match NOOWN edges) missing or not the frozen sha16: every batch runs the MATCHED rival: refused')
    L = P.get('limits') or {}
    if not (str(L.get('deferred') or '').strip() or all(isinstance(L.get(k), dict) and L[k].get('path') for k in ('t09', 't13'))):
        raise ValueError('limits missing: name T09 + T13 modules {path, sha16} or a STRATEGY deferral ruling (LAB1 21:19:21Z MUST 1): refused')
    for k in ('t09', 't13'):
        if isinstance(L.get(k), dict) and ids.sha16_file(_path(L[k]['path'])) != L[k].get('sha16'):
            raise ValueError('limits %s %s is not the frozen sha16: refused' % (k, L[k]['path']))
    codes = [i['code'] for i in P.get('inputs') or []]
    used = sorted({r['code'] for s in P.get('situations') or [] for r in s.get('rules') or []})
    if set(used) - set(codes):
        raise ValueError('situation rules read %s, not declared inputs: refused' % sorted(set(used) - set(codes)))
    for i in P.get('inputs') or []:
        if i.get('known_at_after_decision_s') is None or not (i.get('brief') or '').strip():
            raise ValueError('input %s: brief and known_at_after_decision_s required: refused' % i.get('code'))
    k_us = np.array([int(round(float(i.get('known_at_after_decision_s') or 0) * US)) for i in P.get('inputs') or []], np.int64)
    lookahead.join_guard(k_us, np.zeros(len(k_us), np.int64), 'PREREG inputs')
    return (cfg.get('refuse_inputs') or briefs.refuse_inputs)(codes, used)


def expand(P):
    """the cards of the batch, in a fixed order: rivals first, then situations x decisions x entries x exits"""
    base = {k: P[k] for k in ('family', 'alarm', 'fire_list', 'months', 'windows_sha16', 'bars', 'judge_window', 'regime', 'judges')}
    base.update(cost_basis='costs_v3 (costs V3_5)', cost_settings=P['cost']['settings'], cost_settings_sha16=P['cost']['settings_sha16'],
                cost_table=P['cost']['record'], cost_sha16=P['cost']['record_sha16'], matched=P['matched'], limits=P['limits'], exits_path=P['exits_path'],
                unit_subject=P.get('unit_subject', ''), batch_id=P['batch_id'], factory=VERSION)
    e0 = P['entries'][0]
    out = []
    for r in RIVALS:
        side = {'NO_TRADE': 'SKIP', 'ALARM_ONLY_FADE': 'FADE', 'ALARM_ONLY_FOLLOW': 'FOLLOW'}[r]
        for x in P['exits']:
            out.append(dict(base, card_id='%s.%s.%s' % (P['batch_id'], r, x['exit_id']), rival=r, situation={'id': 'ALL', 'rules': []},
                            decisions=[{'id': r, 'side': side, 'inputs': [], 'line': '%s on every eligible fire' % r}], inputs=[],
                            entry=e0, exit_id=x['exit_id'], exit_row_sha16=x['exit_row_sha16']))
            if r == 'NO_TRADE':
                break                                                          # NO_TRADE is one card whatever the exits
    sits = P.get('situations') or [{'id': 'ALL', 'rules': []}]
    ins = {i['code']: i for i in P.get('inputs') or []}
    for s in sits:
        for d in P['decisions']:
            for e in P['entries']:
                for x in P['exits']:
                    codes = sorted({r['code'] for r in s.get('rules') or []} | set(d.get('inputs') or []))
                    dec = dict(d, inputs=codes)
                    out.append(dict(base, card_id='%s.%s.%s.%s.%s' % (P['batch_id'], s['id'], d['id'], e['id'], x['exit_id']), rival='',
                                    situation=s, decisions=[dec], inputs=[ins[c] for c in codes], entry=e, exit_id=x['exit_id'],
                                    exit_row_sha16=x['exit_row_sha16']))
    return out


def dependency_inventory():
    """{realpath: sha16} of every code file the factory runs on (labcore, exit_engine, fairness_bar v1+v2, the classifier, the ledger,
    alarm_profile, this module): frozen at generate, checked at run, handed to exit_engine.run_frozen (its dependency_sha16)"""
    import labcore, make_families_v2, alarm_profile
    lc = os.path.dirname(os.path.realpath(labcore.__file__))
    files = sorted(os.path.join(lc, f) for f in os.listdir(lc) if f.endswith('.py'))
    files += [os.path.realpath(m.__file__) for m in (XE, FB, FB.V1, make_families_v2, LG, alarm_profile, CV)]
    files.append(os.path.join(FUND_DIR, 'hl_funding_pull_v1.py'))
    files.append(os.path.realpath(__file__))
    return {f: ids.sha16_file(f) for f in sorted(set(files))}


def batch_sha16(card_shas):
    return ids.sha16_text('\n'.join(card_shas))


def generate(prereg_path, cfg):
    P = json.load(open(prereg_path))
    validate(P, cfg)
    cards = expand(P)
    if len(cards) > int(P['budget_cards']):
        raise ValueError('batch %s: %d cards, budget %d: refused' % (P['batch_id'], len(cards), int(P['budget_cards'])))
    texts = [_canon(c) for c in cards]; shas = [ids.sha16_text(t) for t in texts]
    bsha = batch_sha16(shas)
    d = os.path.join(cfg['root'], 'cards', bsha)
    if os.path.exists(os.path.join(d, 'BATCH.json')):
        raise ValueError('batch %s already generated: never overwritten (a change is a new batch)' % bsha)
    for t, s in zip(texts, shas):
        _write_whole(os.path.join(d, '%s.json' % s), t)
    prereg_copy = os.path.join(d, 'PREREG.json'); _write_whole(prereg_copy, open(prereg_path, 'rb').read())
    rows = []
    days_from = P['months'][0] + '01'; days_to = gates.month_last_day(P['months'][-1])
    for c, s in zip(cards, shas):
        aid = LG.prereg('%s-F%s' % (P['family'], s), 'FACTORY %s %s' % (bsha, c['card_id']), os.path.join(d, '%s.json' % s), days_from,
                        days_to, path=cfg['ledger'], clock=cfg.get('clock'), ttype='STRATEGY_MONEY', family=P['family'],
                        types_path=cfg.get('types_path'), families_path=cfg.get('families_path'))
        rows.append(dict(card_sha16=s, card_id=c['card_id'], rival=c['rival'], prereg_ask_id=aid))
    man = dict(batch_sha16=bsha, batch_id=P['batch_id'], family=P['family'], prereg_sha16=ids.sha16_file(prereg_copy), cards=rows,
               factory_sha16=ids.sha16_file(os.path.abspath(__file__)), dependency_sha16=dependency_inventory())
    _write_whole(os.path.join(d, 'BATCH.json'), _canon(man))
    return bsha


# ---------------------------------------------------------------- run: the readers (injectable for planted tests)
def default_bars(cfg):
    cache = cfg.get('price_cache')
    if cache is None:
        from labcore import prices
        cache = cfg['price_cache'] = prices.PriceCache(cfg['lab_root'], 'research')
    return lambda coin, t0, t1: XE.bars(cfg['lab_root'], coin, t0, t1, cache=cache)


def default_values(cfg, subject):
    """{code: (value[], known_at_us[])} for EPI.<subject>.<col> codes, aligned to the fires, through alarm_profile.read"""
    import alarm_profile as AP

    def get(codes, fires, first, last):
        cols = [c.split('.', 2)[2] for c in codes]
        bad = [c for c in codes if not c.startswith('EPI.%s.' % subject)]
        if bad:
            raise ValueError('inputs %s: only EPI.%s.* is read in factory_v1 (other stores: a version 2 with their readers)' % (bad, subject))
        r = AP.read(cfg['research_root'], LAB3_CODE, subject, first, last, values=cols)
        key = {(c, int(a)): i for i, (c, a) in enumerate(zip(r['coin'], np.asarray(r['t_alarm'], np.int64)))}
        idx = np.array([key.get((c, int(t)), -1) for c, t in zip(fires['coin'], fires['t'])])
        out = {}
        for code, col in zip(codes, cols):
            v = np.where(idx >= 0, np.asarray(r[col], float)[np.maximum(idx, 0)], np.nan)
            k = np.where(idx >= 0, np.asarray(r['known_at_us'], np.int64)[np.maximum(idx, 0)], -1)
            out[code] = (v, k)
        return out
    return get


def _fires(card, cfg):
    import alarm_profile as AP
    p = _path(card['fire_list']['path'])
    with open(p) as f:
        frac = [r['t'] for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t') if float(r['t']) != int(float(r['t']))]
    if frac:
        raise ValueError('fire list %s: %d fire times are not whole seconds (e.g. %s): one rounding with the edges: refused' % (p, len(frac), frac[0]))
    ev = (cfg.get('load_fires') or AP.load_alarms)(p)
    return {'coin': np.asarray(ev['coin']), 't': np.asarray(ev['t'], np.int64), 'push_side': np.asarray(ev['side'], int)}


# ---------------------------------------------------------------- run: one card
def eligible(fires, months, wins, horizon_s):
    """-> status array: -1 out of the batch months; EMBARGO when fire + horizon ends past the fire's window's last day; else TRADE (to be
    decided)"""
    days = _utc_day(fires['t'] * US); mon = np.array([d[:4] + d[5:7] for d in days])
    st = np.full(len(days), -1, int)
    inb = np.isin(mon, months); st[inb] = STATUS['TRADE']
    for i in np.nonzero(inb)[0]:
        w = gates.window_of(mon[i], wins)
        last = [x for x in wins if x[0] == w][0][2]
        end_us = _day_start_us(str(last)) + 86_400 * US
        if fires['t'][i] * US + int(horizon_s * US) >= end_us:
            st[i] = STATUS['EMBARGO']
    return st


def decide(card, fires, sel, values):
    """-> side per fire (+1 / -1 / 0) and status (TRADE, SKIP, UNDECIDED) for the selected fires; join guard on every input"""
    n = len(fires['t']); side = np.zeros(n, int); st = np.full(n, STATUS['TRADE'], int)
    dec_us = fires['t'] * US + int(float(card['entry']['delay_s']) * US)
    ok = sel.copy()
    for r in card['situation'].get('rules') or []:
        v, k = values[r['code']]
        lookahead.join_guard(k[sel & (k >= 0)], dec_us[sel & (k >= 0)], card['card_id'] + ' ' + r['code'])
        und = sel & (~np.isfinite(v) | (k < 0))
        st[und] = STATUS['UNDECIDED']
        hit = np.zeros(n, bool); fin = np.isfinite(v)
        hit[fin] = OPS[r['op']](v[fin], float(r['value']))
        ok &= hit | und
    d = card['decisions'][0]['side']
    sgn = {'FADE': -1, 'FOLLOW': 1, 'SKIP': 0}[d]
    side[sel] = sgn * fires['push_side'][sel]
    st[sel & ~ok & (st != STATUS['UNDECIDED'])] = STATUS['SKIP']
    if d == 'SKIP':
        st[sel & (st == STATUS['TRADE'])] = STATUS['SKIP']
    side[st != STATUS['TRADE']] = 0
    return side, st


ENTRY_MAX_LATE_S = 60                                                                    # an entry more than 60 s after t0 is NOPRICE


def entry_clock(t_fire_us, delay_s):
    """THE entry rule's clock (exported for Outcomes and the exit tool, LAB1 25 Oct): t_dec = fire + delay (us, the delay cut to the us);
    t0 = the end of the first 3 s bar that starts at or after t_dec (bar (t0 - 3 s, t0]) -> (t_dec, t0)"""
    t_dec = int(t_fire_us) + int(float(delay_s) * US)
    return t_dec, ((t_dec + XE.BAR_US - 1) // XE.BAR_US) * XE.BAR_US + XE.BAR_US


def entry_bar(c, h, l, max_late_s=ENTRY_MAX_LATE_S):
    """THE entry rule's bar: the index of the first bar from t0 with finite close, high and low, at most max_late_s after t0; None = NOPRICE"""
    ok = np.nonzero(np.isfinite(c) & np.isfinite(h) & np.isfinite(l))[0]
    ok = ok[ok * XE.BAR_US <= max_late_s * US]
    return int(ok[0]) if len(ok) else None


def trade(card, fires, i, side, bars_fn, row, frozen, units, C, size_usd, t_override=None, coin_override=None, unit_override=None):
    """one trade: entry at the first 3 s bar starting at or after fire + delay, exit through exit_engine.run_frozen. t_override = a matched
    moment's time in seconds (fractions kept to the microsecond); unit_override = (value, known_at_us) of THAT moment's own unit"""
    t_fire_us = int(fires['t'][i]) * US if t_override is None else int(round(float(t_override) * US))
    coin = fires['coin'][i] if coin_override is None else coin_override
    t_dec, t0 = entry_clock(t_fire_us, card['entry']['delay_s'])                      # the exported entry rule (LAB1 25 Oct)
    span = int((float(row['time_limit_min']) * 60 + 600) * US)
    te, c, h, l = bars_fn(coin, t0, t0 + span)
    e = entry_bar(c, h, l)
    if e is None:
        return None
    if unit_override is not None:
        u = {'known_at_us': np.array([unit_override[1]], np.int64)}
        if row['unit'] != 'pct':
            u[row['unit']] = np.array([unit_override[0]], float)
    else:
        u = {'known_at_us': np.array([units['known_at_us'][i]], np.int64)}
        if row['unit'] != 'pct':
            u[row['unit']] = np.array([units[row['unit']][i]], float)
    o = XE.run_frozen(c, h, l, [e], [c[e]], [int(side)], row, frozen, units=u, t0_us=int(te[0]), signal_us=[t_dec])
    if str(o['kind'][0]) == 'noprice':
        return dict(kind='noprice')
    cpct, fok = trade_cost(C, coin, side, int(o['entry_us'][0]), int(o['exit_us'][0]), size_usd)
    return dict(entry_us=int(o['entry_us'][0]), entry_px=float(c[e]), exit_us=int(o['exit_us'][0]), ret_pct=float(o['ret_pct'][0]), t_dec=t_dec,
                cost_pct=cpct, funding_ok=fok, evidence=str(o['path_evidence_status'][0]), kind=str(o['kind'][0]))


def run_card(card, fires, wave, base_status, cfg, values, units, C):
    """-> per-fire columns of one card"""
    n = len(fires['t']); sel = base_status == STATUS['TRADE']
    side, st = decide(card, fires, sel, values)
    st = np.where(base_status == STATUS['EMBARGO'], STATUS['EMBARGO'], np.where(base_status < 0, -1, st))
    X = load_exits_row(card, cfg)
    frozen = frozen_of(card, cfg)
    size = float(json.load(open(_path(card['cost_settings'])))['size_usd']) if cfg.get('costs_obj') is None else float(cfg.get('size_usd', 10000))
    col = {k: np.full(n, np.nan) for k in ('entry_px', 'ret_pct', 'cost_pct', 'net_pct', 'path_clean', 'funding_ok')}
    col['entry_us'] = np.full(n, -1, np.int64); col['exit_us'] = np.full(n, -1, np.int64)
    col['t_dec'] = fires['t'] * US + int(float(card['entry']['delay_s']) * US)
    bars_fn = cfg.get('bars_fn') or default_bars(cfg)
    for i in np.nonzero(st == STATUS['TRADE'])[0]:
        r = trade(card, fires, i, side[i], bars_fn, X, frozen, units, C, size)
        if r is None or r['kind'] == 'noprice':
            st[i] = STATUS['NOPRICE']; side[i] = 0; col['path_clean'][i] = -1
            continue
        if not np.isfinite(r['cost_pct']):
            st[i] = STATUS['NOCOST']; side[i] = 0; col['path_clean'][i] = -1
            continue
        col['funding_ok'][i] = r['funding_ok']
        col['entry_us'][i], col['entry_px'][i], col['exit_us'][i] = r['entry_us'], r['entry_px'], r['exit_us']
        col['ret_pct'][i], col['cost_pct'][i] = r['ret_pct'], r['cost_pct']; col['net_pct'][i] = r['ret_pct'] - r['cost_pct']
        col['path_clean'][i] = {'CLEAN': 1, 'PATH_UNCERTAIN': 0}.get(r['evidence'], -1)
    col['net_pct'][(st == STATUS['SKIP']) | (st == STATUS['UNDECIDED'])] = 0.0
    col['status'] = st; col['side'] = side; col['wave'] = wave
    return col


# ---------------------------------------------------------------- run: T13 entry cap and T09 limits (LAB1 21:19:21Z MUST 1)
def limits_of(card, cfg):
    """-> (object with load_settings(), replay(decisions, settings) [T09] and entry_cap_fill(...) [T13], or None when deferred, the
    receipt line). cfg['limits_obj'] is injectable (tests); else the PREREG's pinned modules, sha16 rechecked."""
    L = card['limits']
    if str(L.get('deferred') or '').strip():
        return None, 'LIMITS DEFERRED (%s)' % L['deferred']
    if cfg.get('limits_obj') is not None:
        return cfg['limits_obj'], 'LIMITS injected %s' % getattr(cfg['limits_obj'], 'NAME', type(cfg['limits_obj']).__name__)
    import importlib.util
    mods = {}
    for k in ('t09', 't13'):
        p = _path(L[k]['path'])
        if ids.sha16_file(p) != L[k]['sha16']:
            raise ValueError('limits %s %s changed since generate: refused' % (k, p))
        spec = importlib.util.spec_from_file_location('factory_limits_%s' % k, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        mods[k] = m

    class _L:
        load_settings = staticmethod(mods['t09'].load_settings); replay = staticmethod(mods['t09'].replay)
        entry_cap_fill = staticmethod(mods['t13'].entry_cap_fill)
        cap_settings = staticmethod(getattr(mods['t13'], 'load_settings', lambda: {}))
    return _L, 'LIMITS T09 %s + T13 %s' % (L['t09']['sha16'], L['t13']['sha16'])


def signal_px(bars_fn, coin, t_us):
    """the price known at the fire: the close of the last 3 s bar ending at or before t_us (NaN when none in the 60 s before)"""
    t1 = (int(t_us) // XE.BAR_US) * XE.BAR_US
    te, c, _, _ = bars_fn(coin, t1 - 60 * US, t1)
    ok = np.nonzero((te <= t_us) & np.isfinite(c))[0]
    return float(c[ok[-1]]) if len(ok) else float('nan')


def prices_of(bars_fn, coin):
    def fn(t0_us, t1_us):
        te, c, _, _ = bars_fn(coin, int(t0_us), int(t1_us))
        return te, c
    return fn


def cap_entry(L, card, coin, side, fire_us, bars_fn, settings):
    """T13 for one entry -> (True, '') filled or (False, reason) MISSED"""
    ps = signal_px(bars_fn, coin, fire_us)
    r = L.entry_cap_fill(int(side), ps, int(fire_us), float(card['entry']['delay_s']), settings, prices_of(bars_fn, coin))
    return (True, '') if r[0] == 'FILL' else (False, 'T13_%s' % r[1])


def apply_limits(card, fires, col, cfg, L, size_usd):
    """MUST 1: the card's trades in time order (decision time, then fire id) through T13's cap, then T09's replay on ONE desk; every capped
    or refused entry becomes MISSED (net 0, would-be path kept) with its reason. -> {fire index: reason}"""
    if L is None:
        return {}
    bars_fn = cfg.get('bars_fn') or default_bars(cfg); st = col['status']
    fid = np.array(['%s_%d' % (c, t) for c, t in zip(fires['coin'], fires['t'])])
    order = sorted(np.nonzero(st == STATUS['TRADE'])[0], key=lambda i: (int(col['t_dec'][i]), fid[i]))
    cap_s = L.cap_settings() if hasattr(L, 'cap_settings') else {}
    s9 = L.load_settings(); missed = {}; dec = []
    for i in order:
        ok, why = cap_entry(L, card, str(fires['coin'][i]), col['side'][i], int(fires['t'][i]) * US, bars_fn, cap_s)
        if not ok:
            missed[i] = why; continue
        ps = signal_px(bars_fn, str(fires['coin'][i]), int(fires['t'][i]) * US)
        ctx = dict(t_us=int(col['t_dec'][i]), exit_us=int(col['exit_us'][i]), fire_px=(ps, int(fires['t'][i]) * US),
                   ref_mid=(ps, int(fires['t'][i]) * US), fires=[(fid[i], int(fires['t'][i]) * US, int(fires['t'][i]) * US)])
        if cfg.get('limits_ctx_fn'):
            ctx.update(cfg['limits_ctx_fn'](str(fires['coin'][i]), int(col['t_dec'][i])))
        intent = dict(card=card['card_id'], version=VERSION, fire_id=fid[i], coin=str(fires['coin'][i]), side=int(col['side'][i]),
                      notional_usd=size_usd, margin_usd=size_usd, limit_px=ps, t_signal_us=int(fires['t'][i]) * US, leg='entry', attempt=1)
        dec.append((i, dict(intent=intent, ctx=ctx, fill_px=float(col['entry_px'][i]))))
    rows = L.replay([d for _, d in dec], s9) if dec else []
    if len(rows) != len(dec):
        raise ValueError('T09 replay returned %d rows for %d decisions: refused' % (len(rows), len(dec)))
    for (i, _), r in zip(dec, rows):
        if r['result'] != 'PASS':
            missed[i] = 'T09_%s' % (r.get('code') or 'REFUSE')
    for i in missed:
        st[i] = STATUS['MISSED']; col['net_pct'][i] = 0.0
    return missed


def open_book(fires, col, size_usd):
    """per traded fire: the card's other trades open at its entry, and their notional on the same coin (STRATEGY 21:22:39Z deferral)"""
    n = len(fires['t']); col['open_at_entry'] = np.full(n, np.nan); col['coin_open_usd'] = np.full(n, np.nan)
    ix = np.nonzero(col['status'] == STATUS['TRADE'])[0]
    ent, ext = col['entry_us'][ix], col['exit_us'][ix]
    for j, i in enumerate(ix):
        op = (ent < ent[j]) & (ext > ent[j]) | ((ent == ent[j]) & (np.arange(len(ix)) < j) & (ext > ent[j]))
        col['open_at_entry'][i] = int(op.sum())
        col['coin_open_usd'][i] = float(size_usd * (op & (fires['coin'][ix] == fires['coin'][i])).sum())


def missed_receipt(fires, col, missed, path):
    L = ['\t'.join(('coin', 't', 'side', 'reason', 'would_be_ret_pct', 'would_be_cost_pct'))]
    for i in sorted(missed, key=lambda i: (int(col['t_dec'][i]), str(fires['coin'][i]))):
        L.append('\t'.join((str(fires['coin'][i]), str(int(fires['t'][i])), str(int(col['side'][i])), missed[i],
                            repr(float(col['ret_pct'][i])), repr(float(col['cost_pct'][i])))))
    _write_whole(path, '\n'.join(L) + '\n')


def costs_of(card, cfg):
    """the cost of record (costs V3_5): Costs(settings, record from its two pinned tables, funding = the HL hourly store's read_month,
    a missing month = no rows = FUNDING_MISSING); one per run, injectable (cfg 'costs_obj') for planted tests"""
    if cfg.get('costs_obj') is not None:
        return cfg['costs_obj']
    S = json.load(open(_path(card['cost_settings'])))
    rec, _ = CV.make_record(_path(S['table_v1']['path']), _path(S['table_v4']['path']))
    import hl_funding_pull_v1 as HF

    def funding(coin, month):
        try:
            return HF.read_month(S['funding_store'], coin, month)
        except FileNotFoundError:
            return []
    cfg['costs_obj'] = CV.Costs(S, rec, funding)
    return cfg['costs_obj']


def trade_cost(C, coin, side, t_in_us, t_out_us, size_usd):
    """-> (cost_pct, funding_ok): fee + book + gap + funding in pct of the entry notional; funding missing -> fee + book + gap, ok 0;
    no cost row -> NaN"""
    c = C.trade_cost([coin], [int(side)], [int(t_in_us)], [int(t_out_us)], [float(size_usd)])
    tot, why = float(c['total_bp'][0]), str(c['reason'][0])
    if why == 'FUNDING_MISSING':
        return (float(c['fee_bp'][0]) + float(c['book_bp'][0]) + float(c['gap_bp'][0])) / 100.0, 0
    return (tot / 100.0 if np.isfinite(tot) else float('nan')), 1


def frozen_of(card, cfg):
    """exit_engine V1_4's frozen manifest: the exit row, the registry schema (header sha16), the cost table of record, this module's sha16"""
    ep = _path(card['exits_path'])
    with open(ep, encoding='utf-8') as f:
        header = next((l.rstrip('\n') for l in f if not l.startswith('#')), '')
    return dict(exits_path=ep, exit_row_sha16=card['exit_row_sha16'], exits_schema_sha16=ids.sha16_text(header),
                cost_table=_path(card['cost_table']), cost_sha16=card['cost_sha16'], module_sha16=ids.sha16_file(XE.__file__),
                dependency_sha16=cfg['dependency_sha16'])


def load_exits_row(card, cfg):
    return XE.load_exits(_path(card['exits_path']))[card['exit_id']]


def load_edges(card):
    """{(coin, parent_t): [(cand_t, weight)]} from the alarm_match NOOWN edges of record (the PREREG's 'matched', sha16 checked at generate
    and again here); an 'own' row is never read (NOOWN file)"""
    m = card['matched']; p = _path(m['path'])
    if ids.sha16_file(p) != m['sha16']:
        raise ValueError('matched edges %s changed since generate: refused' % p)
    out = {}
    with open(p) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            if (r.get('own') or '').strip():
                continue
            pt = float(r['parent_t'])
            if pt != int(pt):
                raise ValueError('matched edges %s: parent_t %s is not a whole second: one rounding with the fire list: refused' % (p, r['parent_t']))
            out.setdefault((r['coin'], int(pt)), []).append((float(r['cand_t']), float(r['weight'])))
    return out


def matched_units(card, cfg, edges, row):
    """{(coin, cand_t): (unit value, known_at_us)} for every matched moment, from cfg['matched_units_fn'](codes, moments, first, last)
    (moments = {'coin', 't'} at the moments' own times); {} for a pct exit. MUST 3: a moment's unit is its own, never its parent fire's;
    no reader of a moment unit store is bound by default, so a non-pct exit without matched_units_fn is refused."""
    if row['unit'] == 'pct':
        return {}
    fn = cfg.get('matched_units_fn')
    if fn is None:
        raise ValueError('exit unit %r: the matched moments need their own %s known at their own time (LAB1 21:19:21Z MUST 3); no '
                         'matched_units_fn is bound: refused' % (row['unit'], row['unit']))
    keys = sorted({(c, ct) for (c, _), cand in edges.items() for ct, _ in cand})
    mo = {'coin': np.array([k[0] for k in keys]), 't': np.array([k[1] for k in keys], float)}
    days = _utc_day((mo['t'] * US).astype(np.int64)) if keys else []
    code = 'EPI.%s.%s' % (card['unit_subject'], {'nm': 'normal_move_pct'}[row['unit']])
    v, k = fn([code], mo, min(days).replace('-', '') if keys else '0', max(days).replace('-', '') if keys else '0')[code]
    return {key: (float(a), int(b)) for key, a, b in zip(keys, v, k)}


def matched_twin(card, fires, col, cfg, units, C, edges, L=None, stats=None):
    """MATCHED rival (STRATEGY 20:58:51Z ruling 3): the card on its alarms' matched moments. Per fire the card TRADES, its matched candidates
    are traded the same way (same side, entry delay, exit row, cost); the fire's value = the edge-weighted mean net of its priced candidates
    (NaN when none priced or none drawn); a fire the card SKIPS or cannot decide books 0, as in the card. -> per-fire net (the card's waves)"""
    n = len(fires['t']); v = np.full(n, np.nan); st = col['status']
    v[(st == STATUS['SKIP']) | (st == STATUS['UNDECIDED']) | (st == STATUS['MISSED'])] = 0.0
    X = load_exits_row(card, cfg); frozen = frozen_of(card, cfg)
    mu = matched_units(card, cfg, edges, X); stats = {} if stats is None else stats
    stats.setdefault('nounit', 0); stats.setdefault('capped', 0)
    cap_s = L.cap_settings() if L is not None and hasattr(L, 'cap_settings') else {}
    dly = int(float(card['entry']['delay_s']) * US)
    size = float(json.load(open(_path(card['cost_settings'])))['size_usd']) if cfg.get('costs_obj') is None else float(cfg.get('size_usd', 10000))
    bars_fn = cfg.get('bars_fn') or default_bars(cfg)
    for i in np.nonzero(st == STATUS['TRADE'])[0]:
        cand = edges.get((str(fires['coin'][i]), int(fires['t'][i])), [])
        num = den = 0.0
        for ct, w in sorted(cand):
            uo = None
            if X['unit'] != 'pct':
                uv = mu.get((str(fires['coin'][i]), ct))
                if uv is None or not np.isfinite(uv[0]) or uv[1] < 0:
                    stats['nounit'] += 1; continue
                lookahead.join_guard(np.array([uv[1]], np.int64), np.array([int(round(ct * US)) + dly], np.int64),
                                     card['card_id'] + ' matched moment unit')
                uo = uv
            if L is not None:
                ok, _ = cap_entry(L, card, str(fires['coin'][i]), col['side'][i], int(round(ct * US)), bars_fn, cap_s)
                if not ok:
                    stats['capped'] += 1; den += w; continue                       # a capped moment is not taken: it books 0
            r = trade(card, fires, i, col['side'][i], bars_fn, X, frozen, units, C, size, t_override=ct, unit_override=uo)
            if r is None or r.get('kind') == 'noprice' or not np.isfinite(r['cost_pct']):
                continue
            num += w * (r['ret_pct'] - r['cost_pct']); den += w
        if den > 0:
            v[i] = num / den
    return v


def wave_means_of(net, status, wave):
    """{wave id: mean of the resolved values} over the eligible fires (the card's own event set)"""
    m = (status >= 0) & (status != STATUS['EMBARGO']); out = {}
    for wid in sorted(set(wave[m].tolist())):
        x = net[m & (wave == wid)]; x = x[np.isfinite(x)]
        out['W%d' % wid] = float(x.mean()) if len(x) else float('nan')
    return out


# ---------------------------------------------------------------- run: receipts
def wave_receipt(fires, col, path):
    """the per-wave receipt fairness_bar_v2 reads: every eligible fire of the wave listed (the same event set for every card)"""
    m = col['status'] >= 0
    m &= col['status'] != STATUS['EMBARGO']
    L = ['# wave_module_sha16=%s' % ids.sha16_file(LW.__file__),
         '\t'.join(('wave_id', 'value', 'month', 'day', 'n_fires', 'fires'))]
    w = col['wave']
    for wid in sorted(set(w[m].tolist()), key=lambda k: fires['t'][m & (w == k)].min()):
        ix = np.nonzero(m & (w == wid))[0]; ix = ix[np.argsort(fires['t'][ix], kind='mergesort')]
        v = col['net_pct'][ix]; v = v[np.isfinite(v)]
        val = float(v.mean()) if len(v) else float('nan')
        d0 = _utc_day(fires['t'][ix[0]] * US)
        L.append('\t'.join(('W%d' % wid, repr(val), d0[:4] + d0[5:7], d0.replace('-', ''), str(len(ix)),
                            ';'.join('%s@%d' % (fires['coin'][j], fires['t'][j]) for j in ix))))
    _write_whole(path, '\n'.join(L) + '\n')


def wave_means(path):
    W = FB.read_receipt(path)
    return {w['wave_id']: w['value'] for w in W}


def summarise(card, col, bar_r, rivals_wm, own_wm, cost_complete, matched_wm=None):
    st = col['status']
    cnt = {k: int((st == v).sum()) for k, v in STATUS.items()}
    v = np.array([own_wm[k] for k in sorted(own_wm)]); fin = np.isfinite(v)
    mean_w = float(v[fin].mean()) if fin.any() else float('nan')
    rng = np.random.default_rng(20261023)
    bw = LW.by_wave(col['net_pct'][st == STATUS['TRADE']], col['wave'][st == STATUS['TRADE']], None, rng, B=1000)
    beats = True
    for r, wm in sorted(rivals_wm.items()):
        if r == card['rival']:
            continue
        common = sorted(set(wm) & set(own_wm))
        a = np.array([own_wm[k] for k in common]); b = np.array([wm[k] for k in common]); ok = np.isfinite(a) & np.isfinite(b)
        if not ok.any() or a[ok].mean() <= b[ok].mean():
            beats = False
    lost = 0; matched_lo = float('nan')
    if matched_wm is not None and not card['rival'] == 'NO_TRADE':
        common = sorted(set(matched_wm) & set(own_wm))
        a = np.array([own_wm[k] for k in common]); b = np.array([matched_wm[k] for k in common]); ok = np.isfinite(a) & np.isfinite(b)
        lost = int((np.isfinite(a) & ~np.isfinite(b)).sum())
        # paired by wave: the card's gain over its MATCHED twin must hold over whole-wave resamples (90 pct lower bound > 0), so a card
        # equal to its twin never clears on noise (BUILD3 default, named for QUANT + LAB1 review)
        mw = LW.by_wave((a - b)[ok], np.arange(int(ok.sum())), None, np.random.default_rng(20261024), B=1000) if ok.any() else None
        matched_lo = mw['lo'] if mw else float('nan')
        if not ok.any() or not matched_lo > 0:
            beats = False
    if card['rival']:
        verdict = 'RIVAL'
    elif not cost_complete or bar_r['verdict'] == 'INCOMPLETE':
        verdict = 'INCOMPLETE'
    elif bar_r['verdict'] == 'UNRELIABLE':
        verdict = 'UNRELIABLE'
    else:
        verdict = 'CLEARS' if bar_r['verdict'] == 'PASS' and beats else 'FAILS'
    return dict(card_id=card['card_id'], rival=card['rival'] or '-', trades=cnt['TRADE'], skipped=cnt['SKIP'], undecided=cnt['UNDECIDED'],
                noprice=cnt['NOPRICE'], embargo=cnt['EMBARGO'], waves=len(own_wm), traded_waves=bw['waves'],
                net_per_trade=bw['mean'] if bw['n'] else float('nan'), net_per_trade_lo=bw['lo'], net_per_trade_hi=bw['hi'],
                net_per_wave=mean_w, beats_rivals=int(beats), bar_verdict=bar_r['verdict'], bar_line=bar_r['line'], verdict=verdict,
                nocost=cnt['NOCOST'], missed=cnt['MISSED'], funding_missing=int(((st == STATUS['TRADE']) & (col['funding_ok'] == 0)).sum()),
                matched_net_per_wave=(float(np.nanmean([matched_wm[k] for k in matched_wm])) if matched_wm and np.isfinite(list(matched_wm.values())).any() else float('nan')),
                matched_waves_lost=lost, matched_gain_lo=matched_lo)


def months_table(fires, col):
    days = _utc_day(fires['t'] * US); mon = np.array([d[:4] + d[5:7] for d in days]); t = col['status'] == STATUS['TRADE']
    return {m: (int((t & (mon == m)).sum()), float(np.nanmean(col['net_pct'][t & (mon == m)])) if (t & (mon == m)).any() else float('nan'))
            for m in sorted(set(mon[col['status'] >= 0].tolist()))}


def write_trades(card, csha, fires, col, cfg, sources, seal):
    """TRADES.<card_sha16> parts in the research root through lab3.write, one per fire day, rows at the fire (as_of) known at the exit"""
    write = cfg.get('write_part')
    if write is None:
        if LAB3_CODE not in sys.path:
            sys.path.insert(0, LAB3_CODE)
        from lab3 import write as LWR
        write = LWR.write_part
    part = 'TRADES.%s' % csha
    cat = {'%s.%s' % (part, f): {'kind': 'ROWS', 'clock': 'event', 'exact_k': False, 'scope': 'coin'} for f, _, _ in TRADE_FIELDS}
    m = col['status'] >= 0
    days = _utc_day(fires['t'] * US)
    done = []
    for day in sorted(set(days[m].tolist())):
        ix = np.nonzero(m & (days == day))[0]; coins = sorted(set(fires['coin'][ix].tolist())); dd = int(day.replace('-', ''))
        codes = {}
        for f, _, _ in TRADE_FIELDS:
            rows = {}
            for coin in coins:
                jj = ix[fires['coin'][ix] == coin]; jj = jj[np.argsort(fires['t'][jj], kind='mergesort')]
                r = {k: [] for k in ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')}
                for j in jj:
                    v = float(col[f][j]); ok = np.isfinite(v); a = int(fires['t'][j]) * US
                    kn = int(col['exit_us'][j]) if col['exit_us'][j] >= 0 else a + int(float(card['entry']['delay_s']) * US)
                    r['day'].append(dd); r['as_of_us'].append(a); r['known_at_us'].append(max(kn, a)); r['value_kind'].append(1)
                    r['value_bits'].append(int(np.array([v], '<f8').view('<u8')[0]) if ok else None)
                    r['value_txt'].append(None); r['empty_reason'].append('' if ok else 'NOT_KNOWN'); r['stale'].append(0)
                rows[coin] = r
            codes['%s.%s' % (part, f)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rows}
        write(cfg['research_root'], dd, part, codes, coins, catalog=cat, sources=sources, seal=seal)
        done.append(dd)
    return done


def run(bsha, cfg, log=print):
    d = os.path.join(cfg['root'], 'cards', bsha)
    man = json.load(open(os.path.join(d, 'BATCH.json')))
    shas = [r['card_sha16'] for r in man['cards']]
    if batch_sha16(shas) != bsha:
        raise ValueError('batch %s: its card list gives %s: refused' % (bsha, batch_sha16(shas)))
    cards = []
    for s in shas:
        p = os.path.join(d, '%s.json' % s)
        if ids.sha16_text(open(p).read()) != s:
            raise ValueError('card %s changed since generate: refused' % s)
        cards.append(json.load(open(p)))
    now_dep = dependency_inventory()
    moved = sorted(k for k in set(now_dep) | set(man['dependency_sha16']) if now_dep.get(k) != man['dependency_sha16'].get(k))
    if moved:
        raise ValueError('code changed since generate (%s): the batch is void, generate a new one: refused' % ', '.join(map(os.path.basename, moved)))
    cfg = dict(cfg, dependency_sha16=man['dependency_sha16'])
    months = cards[0]['months']
    asks = {r['prereg_ask_id'] for r in man['cards']}
    done = sorted(r['ask_id'] for r in LG.rows(cfg['ledger']) if r.get('kind') == 'RESULT' and r['ask_id'][:-2] in asks)
    if done:
        raise PermissionError('batch %s already has RESULT rows %s: one run per batch, a rerun is a new batch: refused' % (bsha, done[:3]))
    gates.outcome_allowed({'months': months, 'outcome_months': months, 'fit_months': [], 'judge_months': []}, months,
                          ledger=cfg['ledger'], now_utc=_now(cfg), law=cfg.get('law'), wins=gates.windows(cfg.get('windows')))
    if not cfg.get('skip_gate'):
        jobgate.gate_wait(log=log)
    wins = gates.windows(cfg.get('windows'))
    fires = _fires(cards[0], cfg)
    hz = max(float(c['entry']['delay_s']) + float(load_exits_row(c, cfg)['time_limit_min']) * 60 for c in cards)
    base = eligible(fires, months, wins, hz)
    keep = base >= 0
    wave = np.full(len(fires['t']), -1, int)
    el = base == STATUS['TRADE']
    wave[el] = LW.waves(fires['t'][el], GAP_S)
    days = _utc_day(fires['t'][keep] * US)
    first, last = (min(days).replace('-', ''), max(days).replace('-', '')) if keep.any() else ('0', '0')
    codes = sorted({i['code'] for c in cards for i in c['inputs']})
    vfn = cfg.get('values_fn') or default_values(cfg, cards[0]['unit_subject'])
    values = vfn(codes, fires, first, last) if codes else {}
    rows_ = {load_exits_row(c, cfg)['unit'] for c in cards}
    units = {'known_at_us': np.full(len(fires['t']), -1, np.int64)}
    for u in sorted(rows_ - {'pct'}):
        code = 'EPI.%s.%s' % (cards[0]['unit_subject'], {'nm': 'normal_move_pct'}[u])
        v, k = (cfg.get('units_fn') or vfn)([code], fires, first, last)[code]
        units[u] = v; units['known_at_us'] = np.maximum(units['known_at_us'], k)
    C = costs_of(cards[0], cfg); edges = load_edges(cards[0]); L, lim_line = limits_of(cards[0], cfg)
    size = float(json.load(open(_path(cards[0]['cost_settings'])))['size_usd']) if cfg.get('costs_obj') is None else float(cfg.get('size_usd', 10000))
    log('BATCH %s cards %d fires %d eligible %d embargo %d waves %d; cost of record costs V3_5; matched parents with edges %d' % (
        bsha, len(cards), int(keep.sum()), int(el.sum()), int((base == STATUS['EMBARGO']).sum()), len(set(wave[el].tolist())),
        sum(1 for c_, t_ in zip(fires['coin'][el], fires['t'][el]) if (str(c_), int(t_)) in edges)))
    out = os.path.join(cfg['root'], 'runs', bsha); cols = {}; wm = {}; mwm = {}; mst = {}; nmiss = {}
    for c, s in zip(cards, shas):
        cols[s] = run_card(c, fires, wave, base, cfg, values, units, C)
        missed = apply_limits(c, fires, cols[s], cfg, L, size); nmiss[s] = missed; open_book(fires, cols[s], size)
        missed_receipt(fires, cols[s], missed, os.path.join(out, 'MISSED_%s.tsv' % s))
        wave_receipt(fires, cols[s], os.path.join(out, 'WAVES_%s.tsv' % s))
        wm[s] = wave_means(os.path.join(out, 'WAVES_%s.tsv' % s))
        if c['rival'] != 'NO_TRADE':
            mst[s] = {}
            mwm[s] = wave_means_of(matched_twin(c, fires, cols[s], cfg, units, C, edges, L, mst[s]), cols[s]['status'], cols[s]['wave'])
    traded = [cols[s]['status'] == STATUS['TRADE'] for s in shas]
    cost_complete = all(not (t & (cols[s]['funding_ok'] == 0)).any() for t, s in zip(traded, shas))
    rivals_wm = {c['rival']: wm[s] for c, s in zip(cards, shas) if c['rival']}
    ask = {r['card_sha16']: r['prereg_ask_id'] for r in man['cards']}
    tries = cfg.get('tries_fn', lambda: None)()
    roster = {ask[s]: os.path.join(out, 'WAVES_%s.tsv' % s) for s in shas}
    summ = []
    seal = _canon({'factory': VERSION, 'batch': bsha, 'module_sha16': ids.sha16_file(os.path.abspath(__file__))})
    for c, s in zip(cards, shas):
        b = FB.bar(os.path.join(out, 'WAVES_%s.tsv' % s), ask[s], settings=cfg.get('bar_settings'), tries=tries,
                   roster={k: v for k, v in roster.items() if k != ask[s]}, now_utc=_now(cfg))
        r = summarise(c, cols[s], b, rivals_wm, wm[s], cost_complete, mwm.get(s)); r['card_sha16'] = s
        r['missed_reasons'] = ';'.join('%s:%d' % kv for kv in sorted(__import__('collections').Counter(nmiss[s].values()).items())) or '-'
        r['matched_nounit'] = mst.get(s, {}).get('nounit', 0); r['matched_capped'] = mst.get(s, {}).get('capped', 0)
        tr = cols[s]['status'] == STATUS['TRADE']
        r['max_open_at_entry'] = int(np.nanmax(cols[s]['open_at_entry'][tr])) if tr.any() else 0
        r['limits'] = NOT_REPLAYED if L is None else 'replayed (T13 cap, T09 desk)'; summ.append(r)
        r['months'] = json.dumps(months_table(fires, cols[s]), sort_keys=True)
        srcs = {'fire_list': c['fire_list']['sha16'], 'card': s, 'cost_table': c['cost_sha16'], 'exit_row': c['exit_row_sha16']}
        if not cfg.get('no_trades_write'):
            write_trades(c, s, fires, cols[s], cfg, srcs, seal)
        log('CARD %s %s trades %d waves %d net/trade %.4f net/wave %.4f %s -> %s' % (
            s, c['card_id'], r['trades'], r['waves'], r['net_per_trade'], r['net_per_wave'], b['verdict'], r['verdict']))
    heads = ['card_sha16', 'card_id', 'rival', 'trades', 'skipped', 'undecided', 'noprice', 'embargo', 'waves', 'traded_waves',
             'net_per_trade', 'net_per_trade_lo', 'net_per_trade_hi', 'net_per_wave', 'matched_net_per_wave', 'matched_gain_lo', 'matched_waves_lost',
             'beats_rivals', 'nocost', 'funding_missing', 'missed', 'missed_reasons', 'max_open_at_entry', 'limits', 'matched_nounit', 'matched_capped', 'bar_verdict',
             'verdict', 'months', 'bar_line']
    buf = io.StringIO()
    buf.write('# BATCH %s (%s, family %s; factory %s; prereg %s; cost %s; %s)\n' % (
        bsha, man['batch_id'], man['family'], ids.sha16_file(os.path.abspath(__file__)), man['prereg_sha16'],
        'COMPLETE' if cost_complete else 'FUNDING_MISSING (verdicts capped at INCOMPLETE)', lim_line))
    w = csv.writer(buf, delimiter='\t', lineterminator='\n'); w.writerow(heads)
    for r in summ:
        w.writerow([('%.6f' % r[h]) if isinstance(r[h], float) else r[h] for h in heads])
    bp = os.path.join(out, 'BATCH_%s.tsv' % bsha); _write_whole(bp, buf.getvalue())
    if not cfg.get('no_result_rows'):
        for r in summ:
            st = VERDICT_LEDGER.get(r['verdict'], 'UNSURE')
            LG.result(ask[r['card_sha16']], os.path.join(out, 'WAVES_%s.tsv' % r['card_sha16']), st,
                      os.path.join(d, '%s.json' % r['card_sha16']), path=cfg['ledger'], clock=cfg.get('clock'))
    log('END BATCH %s (%s): CLEARS %d of %d cards (rivals %d); receipt %s %s' % (
        bsha, lim_line if L is not None else NOT_REPLAYED, sum(r['verdict'] == 'CLEARS' for r in summ), sum(not c['rival'] for c in cards), sum(bool(c['rival']) for c in cards),
        bp, ids.sha16_file(bp)))
    return bp


# ---------------------------------------------------------------- sheet
def sheet(bsha, cfg):
    bp = os.path.join(cfg['root'], 'runs', bsha, 'BATCH_%s.tsv' % bsha)
    R = list(csv.DictReader((l for l in open(bp) if not l.startswith('#')), delimiter='\t'))
    head = open(bp).readline().strip('# \n')
    cards = [r for r in R if r['rival'] == '-']; riv = [r for r in R if r['rival'] != '-']; ok = [r for r in cards if r['verdict'] == 'CLEARS']
    L = ['# Strategy batch %s' % bsha, '', head, '',
         'Tried: %d strategy cards, against %d rivals (no trade, fade every fire, follow every fire), on BUILD months only, after full cost, '
         'counted by wave.' % (len(cards), len(riv)),
         'Cleared the fairness bar and beat every rival: %d.%s' % (len(ok), ' Nothing is a winner yet.' if not ok else ''), '',
         '| card | trades | missed (limits) | most open at once | net per trade, pct (90 pct interval) | net per wave, pct | verdict |',
         '|---|---|---|---|---|---|---|']
    for r in riv + cards:
        L.append('| %s | %s | %s %s | %s | %s (%s to %s) | %s | %s (%s) |' % (r['card_id'], r['trades'], r['missed'], r['missed_reasons'],
                 r['max_open_at_entry'], r['net_per_trade'], r['net_per_trade_lo'], r['net_per_trade_hi'], r['net_per_wave'], r['verdict'], r['limits']))
    L += ['', '## Per month (trades, mean net pct per trade)']
    for r in riv + cards:
        L.append('- %s: %s' % (r['card_id'], ', '.join('%s %d trades %.3f' % (m, n, v) for m, (n, v) in sorted(json.loads(r['months']).items()))))
    L += ['', 'What this is not: no CHECK or BLIND month was read; prices are Binance 3 s model fills; paper only.']
    p = os.path.join(cfg['root'], 'runs', bsha, 'SHEET_%s.md' % bsha); _write_whole(p, '\n'.join(L) + '\n')
    return p


def main(a):
    cfg = json.load(open(a[a.index('--cfg') + 1])) if '--cfg' in a else {}
    cfg.setdefault('root', os.path.join('<SCRATCH>/work_BUILD4', 'factory'))
    cfg.setdefault('ledger', LG.LEDGER); cfg.setdefault('lab_root', '<DATA_ROOT>/lab_days')
    cfg.setdefault('research_root', '<DATA_ROOT>/research_days')
    if a[0] == 'generate':
        print(generate(a[1], cfg))
    elif a[0] == 'run':
        run(a[1], cfg)
    elif a[0] == 'sheet':
        print(sheet(a[1], cfg))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
