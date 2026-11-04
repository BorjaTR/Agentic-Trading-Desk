"""acceptance_v3.py: the SMALLEST real-input checks of event_outcomes VERSION 3 (STRATEGY/LEAD builder, 25 Oct 2026; owner 11:46Z:
"small tests to prove things"). Real lab_days / research_days, Sep 2025 - Jan 2026 only, never a February read; writes only <out>.
  python3 acceptance_v3.py <out_dir> [check ...]      checks: oracle112 factory8 boundary5 stamps oneday faults
Each check writes <out>/<check>.json and prints one line. Independent expected answers come from the A51 review's frozen files
(expected.json b41991339ef05e90, full_factory_money.json, factory_comparison.json, stamp_traces.json); this script never recomputes them."""
import csv, json, os, shutil, subprocess, sys, time
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import event_outcomes as EO                                            # noqa: E402
F = EO.FORENSICS; CODE = os.path.join(F, 'team', 'LAB3', 'code'); LAB = '<DATA_ROOT>/lab_days'
A51 = '<SCRATCH>/work_OX_A51/outcomes_review_v1'
EVENTS = '<SCRATCH>/work_LEAD/ed2/epg/A02P_EPG_INPUT.tsv'
V3 = os.path.join(HERE, 'OUTCOMES_CORE_V3.json'); WINDOW = ('20250901', '20260131')     # the owner's authorized window for this repair


def _events(out, name, rows):
    p = os.path.join(out, name); open(p, 'w').write('coin\tt\tside\n' + ''.join('%s\t%d\t%d\n' % r for r in rows)); return p


def _a02p(day_lo, day_hi):
    with open(EVENTS) as f:
        R = list(csv.DictReader(f, delimiter='\t'))
    return [(r['coin'], int(r['t']), int(r['side'])) for r in R if day_lo <= EO.day_of(int(r['t']) * EO.US) <= day_hi]


def _run(n, ev, st, subj, first, last, out, **kw):
    return EO.run(n, LAB, CODE, ev, st, subj, first, last, out, run_window=WINDOW, log=lambda *a: None, **kw)


def oracle112(out):
    """the A51 review's 112 independently frozen values (4 coins x 7 kinds x 2 units x 2 directions, 13 Oct) against the successor"""
    exp = json.load(open(os.path.join(A51, 'expected.json'))); os_ = json.load(open(os.path.join(A51, 'oracle_settings.json')))
    s = dict(name='A51_ORACLE_V3', entry=os_['entry'], directions=os_['directions'], labels=os_['labels'],
             cost=dict(table=os_['cost']['table'], sha16='ff157578098a2f47', gap_pct=os_['cost']['gap_pct'], fallback='unknown'))
    st = os.path.join(out, 'oracle_settings_v3.json'); json.dump(s, open(st, 'w'), indent=1)
    ev = os.path.join(out, 'events_small.tsv'); shutil.copy(os.path.join(A51, 'events_small.tsv'), ev)
    m = _run(1, ev, st, 'A51O', '20251013', '20251013', os.path.join(out, 'oracle_run'))
    r = EO.read(os.path.join(out, 'oracle_run'), CODE, 'A51O'); bad = []; mutated = None
    for x in exp:
        c = r[x['column']]; i = [k for k in range(len(c['coin'])) if c['coin'][k] == x['coin'] and c['as_of_us'][k] == x['t'] * EO.US][0]
        v = c['value'][i]; ok_v = (x['value'] is None and not np.isfinite(v)) or (x['value'] is not None and abs(v - x['value']) <= 1e-10)
        if not (ok_v and c['known_at_us'][i] == x['known_at_us'] and c['reason'][i] == x['reason']):
            bad.append(dict(x, actual=v, actual_reason=c['reason'][i], actual_known=int(c['known_at_us'][i])))
        if mutated is None and x['value'] is not None:
            mutated = abs(v + 1 - x['value']) > 1e-10                         # a corrupted answer must be caught
    return dict(expected=len(exp), differences=bad, corrupted_answer_detected=bool(mutated), run_release=m['frozen']['release'],
                code_sha16=EO.ids.sha16_file(EO.__file__))


def factory8(out):
    """the eight real factory trades (both directions of BTC ETH SOL DOGE, 13 Oct): MONEY_T1 = the factory's full net exactly, the SOL
    FADE funding gap never complete; EXIT_T1 = the factory's gross; entries equal"""
    full = json.load(open(os.path.join(A51, 'full_factory_money.json'))); comp = json.load(open(os.path.join(A51, 'factory_comparison.json')))
    ev = os.path.join(out, 'events_small.tsv'); shutil.copy(os.path.join(A51, 'events_small.tsv'), ev)
    m = _run(1, ev, V3, 'A51F', '20251013', '20251013', os.path.join(out, 'factory_run'))
    r = EO.read(os.path.join(out, 'factory_run'), CODE, 'A51F'); rows = []
    for f, g in zip(full, comp):
        def at(col):
            c = r[col]; i = [k for k in range(len(c['coin'])) if c['coin'][k] == f['coin'] and c['as_of_us'][k] == f['t'] * EO.US][0]
            return c['value'][i], c['reason'][i], int(c['known_at_us'][i])
        b = 'MONEY_T1__%s' % f['direction']
        money, why, _ = at(b); gross, _, _ = at(b + '__booked'); pre, _, _ = at(b + '__cost_prefunding'); fok, _, _ = at(b + '__funding_ok')
        fund, fwhy, _ = at(b + '__funding'); exit_v, _, xk = at('EXIT_T1__%s' % f['direction'])
        net_ok = (money == f['factory_net'] and why == '') if f['funding_ok'] == 1 else (np.isnan(money) and why == 'FUNDING_MISSING' and gross - pre == f['factory_net'])
        rows.append(dict(coin=f['coin'], t=f['t'], direction=f['direction'], factory_net=f['factory_net'], money=None if np.isnan(money) else money,
                         reason=why, funding_ok=fok, factory_funding_ok=f['funding_ok'], gross=gross, factory_gross=g['gross'],
                         exit_known_at=xk, factory_exit_us=g['exit_us'], net_equal=bool(net_ok), funding_equal=fok == f['funding_ok'],
                         gross_equal=gross == g['gross'] and exit_v == g['gross'], exit_clock_equal=xk == g['exit_us'],
                         full_cost=None if not np.isfinite(fund) else pre + fund, factory_full_cost=f['full_cost']))
    return dict(trades=rows, all_equal=all(x['net_equal'] and x['funding_equal'] and x['gross_equal'] and x['exit_clock_equal'] for x in rows),
                funding_missing_never_complete=all(x['money'] is None for x in rows if x['factory_funding_ok'] == 0))


def boundary5(out):
    """the five January 31 boundary events (support past the authorized window) plus the three latest that fit: every identity kept,
    only the labels that could need February are EMBARGO_SUPPORT, and not one February file is opened (in-process recorder over the
    canonical price cache and the funding reader)"""
    rows = sorted(_a02p('20260131', '20260131'), key=lambda r: r[1])[-8:]
    ev = _events(out, 'events_boundary.tsv', rows)
    from labcore import prices
    import factory_v2                                                    # noqa: F401  (puts the funding reader on the path)
    import hl_funding_pull_v1 as HF
    sys.path.insert(0, CODE)
    from lab3 import days as LD
    seen = {'price_days': set(), 'funding_months': set(), 'index_days': set()}
    real_day, real_month, real_index = prices.PriceCache._day, HF.read_month, LD.Days.index
    prices.PriceCache._day = lambda self, coin, day: (seen['price_days'].add(str(day)), real_day(self, coin, day))[1]
    HF.read_month = lambda store, coin, m: (seen['funding_months'].add(m), real_month(store, coin, m))[1]
    LD.Days.index = lambda self, day, part: (seen['index_days'].add(str(day)), real_index(self, day, part))[1]
    try:
        m = _run(0, ev, V3, 'A51B', '20260131', '20260131', os.path.join(out, 'boundary_run'), check_release=False)
    finally:
        prices.PriceCache._day, HF.read_month, LD.Days.index = real_day, real_month, real_index
    r = EO.read(os.path.join(out, 'boundary_run'), CODE, 'A51B'); ids_ = list(zip(r['entry__px']['coin'], r['entry__px']['as_of_us'] // EO.US))
    per = {}
    for i, (coin, t) in enumerate(ids_):
        emb = sorted(c for c in r if r[c]['reason'][i] == 'EMBARGO_SUPPORT')
        per['%s %d' % (coin, t)] = dict(utc=time.strftime('%H:%M:%S', time.gmtime(t)), embargoed_columns=len(emb),
                                        embargoed_labels=sorted({c.split('__')[0] for c in emb}), computed_columns=sum(1 for c in r if r[c]['reason'][i] == ''))
    return dict(requested=len(rows), published=len(ids_), identities_equal=sorted(ids_) == sorted((c, t) for c, t, _ in rows),
                events=per, boundary_events=sum(1 for v in per.values() if v['embargoed_columns']),
                february_price_days_opened=sorted(d for d in seen['price_days'] if d >= '20260201'),
                february_index_days_opened=sorted(d for d in seen['index_days'] if d >= '20260201'),
                february_funding_months_opened=sorted(m_ for m_ in seen['funding_months'] if m_ >= '202602'),
                price_days_opened=sorted(seen['price_days']), frozen_price_days=sorted(m['frozen']['inputs']['PRICE']))


def stamps(out):
    """the A51 stamp counterexamples on real paths (stamp-aligned entry: the fill bar and stored fill price): NEAR 2.5 pct FOLLOW was hit
    51 s late by the ratio rule (5091 s); ICP 2.4 pct is the documented horizon-origin case (bar end +14400 s vs the stamp's fill clock)"""
    tr = json.load(open(os.path.join(A51, 'stamp_traces.json'))); res = []
    pc = EO.prices.PriceCache(LAB, 'research', CODE)
    for x in tr:
        start = ((x['t'] + 6 + 2) // 3) * 3 + 3
        te, c, h, l = EO.XE.bars(LAB, x['coin'], start * EO.US, (start + 15000) * EO.US, cache=pc)
        e = int(np.searchsorted(te, int(round(x['fill_s'] * 1e6))))
        fill_px = _stamp_fill(x); side = 1 if x['price_threshold'] > fill_px else -1
        lab = dict(name='X', kind='reach', target=x['target_pct'], horizon_min=240, unit='pct')
        v, t, why = EO.label_path(lab, c, h, l, e, fill_px, side, 1.0, 60, te=te)
        res.append(dict(coin=x['coin'], t=x['t'], side=side, fill_px=fill_px, target_pct=x['target_pct'], stamp_seconds=x['stored_seconds'], reviewed_code_seconds=x['new_seconds'],
                        successor_reach=v, successor_seconds=None if not np.isfinite(t) else t, reason=why,
                        entry_bar_end_s=int(te[e]) / 1e6, first_price_level_hit_s=x['first_price_level_hit_s']))
    return dict(cases=res)


def _stamp_fill(x):
    """the stored STAMP fill price (alarm_stamp.read, the review's stamp source) for a trace row"""
    sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools', 'alarm_stamp'))
    import alarm_stamp as ST
    d = EO.day_of(x['t'] * EO.US)
    for direction in ('FOLLOW', 'FADE'):
        s = ST.read('<DATA_ROOT>/research_days', CODE, 'A02N', direction, d, d)
        for i in range(len(s['coin'])):
            if s['coin'][i] == x['coin'] and int(round(s['t_alarm'][i])) == x['t'] and abs(s['t_decision'][i] - s['t_alarm'][i]) < .5:
                fill = x['t'] + 6 + float(s['fill_wait_s'][i])
                if abs(fill - x['fill_s']) < 1e-3:
                    return float(s['fill_px'][i])
    raise LookupError('stamp row of %s %s not found' % (x['coin'], x['t']))


def oneday(out):
    """one real busy day pair through the real launcher: 1 vs 2 workers byte-identical deterministic payload, wall and memory, a downstream
    grading read, and the per-column unit / reason / clock audit"""
    rows = _a02p('20251013', '20251014'); ev = _events(out, 'events_oneday.tsv', rows); res = {'events': len(rows)}
    for n in (1, 2):
        t = time.time(); m = _run(n, ev, V3, 'A51D', '20251013', '20251014', os.path.join(out, 'oneday_w%d' % n))
        res['w%d' % n] = dict(wall_s=round(time.time() - t, 2), tree_peak_rss_gb=round(m['terminal']['tree_peak_rss_bytes'] / 1e9, 3),
                              cells=m['coverage']['cells'], release=m['frozen']['release'])
    res['equal_1_vs_2'] = _payload_equal(os.path.join(out, 'oneday_w1'), os.path.join(out, 'oneday_w2'))
    res['audit'] = audit(os.path.join(out, 'oneday_w1'), 'A51D', os.path.join(out, 'COLUMN_AUDIT_V3.tsv'))
    res['downstream'] = downstream(os.path.join(out, 'oneday_w1'), 'A51D')
    return res


def _payload_equal(a, b):
    """every committed file byte-identical, except index.json's named telemetry (built_utc)"""
    diff = []; n = 0
    for root, _, files in os.walk(a):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), a)
            if not rel.startswith('day='):
                continue
            n += 1; x, y = open(os.path.join(a, rel), 'rb').read(), open(os.path.join(b, rel), 'rb').read()
            if f == 'index.json':
                x, y = (json.dumps({k: v for k, v in json.loads(z).items() if k != 'built_utc'}, sort_keys=True) for z in (x, y))
            if x != y:
                diff.append(rel)
    return dict(files=n, differing=diff[:10], equal=not diff, telemetry_excluded=['index.json built_utc'])


def audit(root, subj, tsv):
    """per column: catalog unit, kind, values, reasons, and the clock rule checked on every row"""
    r = EO.read(root, CODE, subj); s = EO.load_settings(V3); spec = {c['col']: c for c in EO.column_specs(s)}
    ent = {(c, a): a + int(round(v * EO.US)) if np.isfinite(v) else None for c, a, v in zip(r['entry__s']['coin'], r['entry__s']['as_of_us'], r['entry__s']['value'])}
    delay = int(s['entry']['delay_s'] * EO.US); lines = ['column\tunit\tkind\tvalues\treasons\tclock_rule\tclock_violations']; total_bad = 0
    for col, x in r.items():
        c = spec[col]; bad = 0; rule = ''
        for k in range(len(x['coin'])):
            a = int(x['as_of_us'][k]); kat = int(x['known_at_us'][k]); w = x['reason'][k]; e = ent[(x['coin'][k], a)]
            g0 = ((a + delay + EO.BAR_US - 1) // EO.BAR_US) * EO.BAR_US + EO.BAR_US; span = EO.span_us(s, c['label']) if c['label'] else 0
            if c['role'] in ('entry_px', 'entry_s'):
                rule = 'entry bar end; NO_ENTRY: first bar + 60 s'; want = e if e is not None else g0 + 60 * EO.US
            elif c['role'] in ('unit', 'unit_fallback'):
                rule = 'F (c); stored known_at, never after the decision (nm)'; want = None; bad += not (kat <= a + delay)
            elif w.split(':')[0] in ('NO_DIRECTION', 'NO_UNIT'):
                rule = 'decision'; want = a + delay
            elif c['label']['kind'] in EO.PATH_KINDS and not w.split(':')[0] in ('NO_PATH', 'NOT_LISTED', 'NOT_BUILT', 'EMBARGO_SUPPORT', 'NO_ENTRY', 'NO_COIN'):
                rule = 'exit bar end = entry + __t'; tcol = r['%s__%s__t' % (c['label']['name'], c['dir'])]; want = e + int(round(tcol['value'][k] * EO.US))
            else:
                rule = 'entry bar end + window (no entry: first bar + 60 s + window)'; want = (e if e is not None else g0 + 60 * EO.US) + span
            if want is not None:
                bad += kat != want
        vals = sum(1 for w in x['reason'] if w == ''); rs = {}
        for w in x['reason']:
            if w:
                rs[w] = rs.get(w, 0) + 1
        total_bad += bad
        lines.append('\t'.join([col, x['unit'], x['kind'], str(vals), ' '.join('%s:%d' % z for z in sorted(rs.items())) or '-', rule, str(bad)]))
    open(tsv, 'w').write('\n'.join(lines) + '\n')
    return dict(columns=len(r), clock_violations=total_bad, units=sorted({x['unit'] for x in r.values()}), tsv=tsv)


def downstream(root, subj):
    """a grading-style consumer of a COMMITTED run (the grading step itself is not built): by-wave means of the money of record per
    direction over complete, CLEAN trades only, with every non-value counted by its reason (never imputed 0), units checked"""
    from labcore import waves
    r = EO.read(root, CODE, subj, ['MONEY_T1__FADE', 'MONEY_T1__FOLLOW', 'MONEY_T1__FADE__funding_ok', 'MONEY_T1__FOLLOW__path_evidence_status'])
    out = {}
    for d in ('FADE', 'FOLLOW'):
        x = r['MONEY_T1__%s' % d]; assert x['unit'] == 'pct' and x['kind'] == 'number'
        assert (x['known_at_us'] >= x['as_of_us']).all()
        w = waves.waves(x['as_of_us'] / 1e6, 1800); v = x['value']; ok = np.isfinite(v)
        wm = [np.mean(v[(w == k) & ok]) for k in np.unique(w[ok])]
        rs = {}
        for z in x['reason']:
            if z:
                rs[z] = rs.get(z, 0) + 1
        out[d] = dict(events=len(v), complete_values=int(ok.sum()), waves=len(np.unique(w)), waves_with_value=len(wm),
                      by_wave_mean_pct=float(np.mean(wm)) if wm else None, not_values_by_reason=rs)
    return out


def faults(out):
    """fault injection on two real days through the real launcher: a worker dies after its first day (no commit, kept as .failed_);
    the launcher is interrupted after the first day (no commit); the same request restarts and commits; a committed run is preserved
    when another run asks for its root; a consumer refuses every non-committed folder"""
    rows = _a02p('20251013', '20251014'); ev = _events(out, 'events_faults.tsv', rows); root = os.path.join(out, 'faults_run'); res = {}
    os.environ[EO.FAULT_ENV] = 'fail_after:20251013'
    try:
        _run(2, ev, V3, 'A51X', '20251013', '20251014', root)
        res['worker_fault'] = 'NOT REFUSED'
    except EO.Refused as e:
        res['worker_fault'] = dict(refused=e.code, committed=os.path.exists(root))
    finally:
        del os.environ[EO.FAULT_ENV]
    os.environ[EO.FAULT_ENV] = 'hold_after:20251013'                       # deterministic: the worker of day 1 waits, the run is interrupted
    try:
        _run(2, ev, V3, 'A51X', '20251013', '20251014', root, fail_after_day=1)
        res['interrupt'] = 'NOT REFUSED'
    except EO.Refused as e:
        res['interrupt'] = dict(refused=e.code, committed=os.path.exists(root))
    finally:
        del os.environ[EO.FAULT_ENV]
    kept = sorted(p for p in os.listdir(out) if p.startswith('faults_run.failed_'))
    refusals = []
    for k in kept:
        try:
            EO.read(os.path.join(out, k), CODE, 'A51X'); refusals.append('READ')
        except EO.Refused as e:
            refusals.append(e.code)
    res['kept_failed_folders'] = dict(folders=kept, consumer=refusals)
    m = _run(2, ev, V3, 'A51X', '20251013', '20251014', root); res['restart'] = dict(status=m['status'], cells=m['coverage']['cells'])
    before = EO.ids.sha16_file(os.path.join(root, 'RUN_MANIFEST.json'))
    other = os.path.join(out, 'faults_other.json'); s = json.load(open(V3)); s['labels'] = s['labels'][2:4]; json.dump(s, open(other, 'w'))
    try:
        _run(2, ev, other, 'A51X', '20251013', '20251014', root); res['preserve'] = 'NOT REFUSED'
    except EO.Refused as e:
        res['preserve'] = dict(refused=e.code, manifest_unchanged=EO.ids.sha16_file(os.path.join(root, 'RUN_MANIFEST.json')) == before)
    res['up_to_date'] = _run(2, ev, V3, 'A51X', '20251013', '20251014', root)['run_id'] == m['run_id']
    return res


def listing(out):
    """C3: the lab's date-effective roster on real days: ASTER before its first PRICE day (19 Sep) and LIT before 23 Dec are NO_COIN, a
    day not built (5 Sep) is NOT_BUILT, the same coins after listing are labelled, and the one real source hole of the Sep-Jan A02P list
    (FIL 10 Oct 21:14:25, a hole 363 s after the entry) is PATH_GAP on the windows that reach it and a value on the 5 min window; every
    requested identity is published"""
    rows = [('ASTER', 1757937600, 1), ('LIT', 1766232000, 1), ('BTC', 1757073600, 1), ('ASTER', 1758283200, 1), ('LIT', 1766491200, 1)]
    fil = [r for r in _a02p('20251010', '20251010') if r[0] == 'FIL' and r[1] == 1760130865]
    ev = _events(out, 'events_listing.tsv', rows + fil)
    m = _run(1, ev, V3, 'A51L', '20250905', '20251223', os.path.join(out, 'listing_run'))
    r = EO.read(os.path.join(out, 'listing_run'), CODE, 'A51L'); res = {}
    for i, (coin, a) in enumerate(zip(r['entry__px']['coin'], r['entry__px']['as_of_us'] // EO.US)):
        res['%s %d' % (coin, a)] = {c: (r[c]['reason'][i] or 'VALUE') for c in ('entry__px', 'RET_5M__FOLLOW', 'RET_60M__FOLLOW', 'REACH_4C_240M__FOLLOW', 'unit__c')}
    return dict(requested=len(rows + fil), published=len(r['entry__px']['coin']), cases=res, frozen_price_days=len(m['frozen']['inputs']['PRICE']))


def prefix(out):
    """H2: labcore.lookahead on real paths through the tool's own compute(): prefix_check (data cut at t: every row known by t equal),
    future_plant_check (a huge price planted after t changes no row known by t), a mutant that claims RET_60M early must be caught,
    and the exit engine's join guard refuses a unit known after the entry"""
    from labcore import lookahead
    rows = sorted(_a02p('20251013', '20251013'), key=lambda r: r[1])[:12]
    s = EO.load_settings(V3); mods = EO.load_deps(s, {}, CODE); inv = EO.inventory([EO.RUN_PARALLEL]); frozen = EO.frozen_exit(s, inv)
    pc = EO.prices.PriceCache(LAB, 'research', CODE); res = []

    class DataSrc:
        def __init__(self, d):
            self.d = d; self.pc = type('PC', (), {'reads': 0, 'mem': {}})()
        def state(self, coin, day):
            return 'LISTED'
        def bars(self, coin, t0, t1):
            te = np.arange(t0, t1 + 1, EO.BAR_US, dtype=np.int64); c, h, l = (np.full(len(te), np.nan) for _ in range(3))
            k = (self.d['te_us'] - t0) // EO.BAR_US; on = (k >= 0) & (k < len(te))
            c[k[on]] = self.d['px'][on]; h[k[on]] = self.d['hi'][on]; l[k[on]] = self.d['lo'][on]
            return te, c, h, l
        def drop_before(self, day):
            pass
    for coin, t, side in rows:
        ev = _events(out, 'prefix_%s_%d.tsv' % (coin, t), [(coin, t, side)])
        P = EO.plan(ev, s, 'A51P', '20251013', '20251013', WINDOW); U = EO.read_units(P, s, mods, CODE, '<DATA_ROOT>/research_days', {}, 'A51P')
        E = P['events'][0]; p = pc.path(coin, E['g0'] - 1, E['read_end'])
        data = {'te_us': np.asarray(p['te_us'], np.int64), 'px': p['px'], 'hi': p['hi'], 'lo': p['lo'], 'known_at_us': np.asarray(p['te_us'], np.int64)}

        def fn(d, mutant=False):
            vals, why, kat, _ = EO.compute(P, s, DataSrc(d), U, mods, frozen, log=lambda *a: None, gate=False)
            out_rows = []
            for c in vals:
                v = vals[c][0]; k_ = int(kat[c][0])
                if mutant and c == 'RET_60M__FOLLOW':
                    k_ = int(kat['entry__px'][0])                            # the mutant: a 60 min label claimed at the entry
                out_rows.append({'col': c, 'v': (v if isinstance(v, str) else (repr(float(v)) if np.isfinite(v) else 'nan')), 'why': why[c][0], 'known_at_us': k_})
            return out_rows
        ent = int(fn(data)[[x['col'] for x in fn(data)].index('entry__px')]['known_at_us'])
        cuts = [ent, ent + 300 * EO.US, ent + 3600 * EO.US, ent + 4 * 3600 * EO.US]
        plant = lambda d, t_: {k: (np.where(d['te_us'] > t_, 1e9 if k == 'hi' else (1e-9 if k == 'lo' else 5e8), v) if k in ('px', 'hi', 'lo') else v) for k, v in d.items()}
        pre = [len(lookahead.prefix_check(fn, data, int(c_))) for c_ in cuts]
        fut = [len(lookahead.future_plant_check(fn, data, plant, int(c_))) for c_ in cuts]
        mut = len(lookahead.prefix_check(lambda d: fn(d, mutant=True), data, int(cuts[1])))
        res.append(dict(coin=coin, t=t, prefix_diffs=pre, future_plant_diffs=fut, mutant_caught=mut > 0))
    try:
        row = EO.load_settings(V3)['_exits']['EXIT_T1']; c = np.full(4000, 100.0)
        EO.XE.run_frozen(c, c, c, [0], [100.0], [1], row, frozen['EXIT_T1'], units={'known_at_us': np.array([EO.BAR_US + 1]), 'nm': np.array([1.0])}, t0_us=0)
        guard = 'NOT REFUSED'
    except ValueError as e:
        guard = 'REFUSED: %s' % str(e)[:120]
    return dict(events=len(res), cases=res, all_prefix_pass=all(sum(x['prefix_diffs']) == 0 and sum(x['future_plant_diffs']) == 0 for x in res),
                all_mutants_caught=all(x['mutant_caught'] for x in res), join_guard=guard)


def selector(out):
    """C1 / C2 small real: --coins BTC,ETH on two real days, ALL, and a changed date range; an unknown coin and a group are refused"""
    rows = _a02p('20251013', '20251014'); ev = _events(out, 'events_selector.tsv', rows); res = {}
    for name, kw, lo, hi in (('btc_eth', dict(coins='BTC,ETH'), '20251013', '20251014'), ('all', dict(coins='ALL'), '20251013', '20251014'),
                             ('btc_eth_day14', dict(coins='BTC,ETH'), '20251014', '20251014')):
        m = EO.run(1, LAB, CODE, ev, V3, 'A51S', lo, hi, os.path.join(out, 'sel_' + name), run_window=WINDOW, log=lambda *a: None, **kw)
        r = EO.read(os.path.join(out, 'sel_' + name), CODE, 'A51S', ['entry__px'])
        res[name] = dict(selector=m['selection']['selector'], events=m['coverage']['events'], coins=sorted(set(r['entry__px']['coin'])),
                         expected=sum(1 for c, t, _ in rows if lo <= EO.day_of(t * EO.US) <= hi and (name == 'all' or c in ('BTC', 'ETH'))))
    for name, kw in (('unknown', dict(coins='NOTACOIN')), ('group', dict(group='MAJORS', group_file=ev))):
        try:
            EO.run(1, LAB, CODE, ev, V3, 'A51S', '20251013', '20251014', os.path.join(out, 'sel_' + name), run_window=WINDOW, log=lambda *a: None, **kw)
            res[name] = 'NOT REFUSED'
        except EO.Refused as e:
            res[name] = e.code
    return res


def month(out):
    """E2 / E4 / K3 small: one real month (October, 1,714 events) through the real launcher at 1 and 8 workers (workers nice 10 from
    run_parallel, the caller at normal priority): wall by phase, tree memory, byte-identical deterministic payload"""
    rows = _a02p('20251001', '20251031'); ev = _events(out, 'events_month.tsv', rows); res = {'events': len(rows)}
    for n in (1, 8):
        t = time.time(); m = _run(n, ev, V3, 'A51M', '20251001', '20251031', os.path.join(out, 'month_w%d' % n))
        res['w%d' % n] = dict(wall_s=round(time.time() - t, 2), phases=m['terminal']['phases'], tree_peak_rss_gb=round(m['terminal']['tree_peak_rss_bytes'] / 1e9, 3),
                              cells=m['coverage']['cells'])
    res['equal_1_vs_8'] = _payload_equal(os.path.join(out, 'month_w1'), os.path.join(out, 'month_w8'))
    return res


CHECKS = dict(oracle112=oracle112, factory8=factory8, boundary5=boundary5, stamps=stamps, oneday=oneday, faults=faults, listing=listing,
              prefix=prefix, selector=selector, month=month)


def main(a):
    out = a[0]; os.makedirs(out, exist_ok=True)
    assert open(os.path.join(F, 'team', 'FEED', 'stops', 'BACKFILL_GATE.txt')).readline().strip() == 'RUN', 'recorder gate is not RUN'
    for name in (a[1:] or list(CHECKS)):
        t = time.time(); r = CHECKS[name](out); r['wall_s'] = round(time.time() - t, 2)
        json.dump(r, open(os.path.join(out, '%s.json' % name), 'w'), indent=1, sort_keys=True, default=lambda z: z.item() if hasattr(z, 'item') else str(z))
        print(name, json.dumps(r, default=str)[:600])


if __name__ == '__main__':
    main(sys.argv[1:])
