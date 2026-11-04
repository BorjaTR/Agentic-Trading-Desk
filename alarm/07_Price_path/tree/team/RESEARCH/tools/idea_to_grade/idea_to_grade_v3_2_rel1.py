"""idea_to_grade_v3_2_rel1.py: Owner STRATEGY/LEAD (the grader thread). New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only"). Old file: idea_to_grade_v3_2.py (V3.2) a124c3c5e23200c8, never edited. Changed: it imports idea_to_grade_rel1 (F found from the file);
--lab-root is required (the settings key LAB_DAYS); --gate gives the feed's stop gate (the settings key FEED_GATE; empty or not given:
no gate); --research-root (the settings key RESEARCH_ROOT) holds the team's tries ledger TRIES_LEDGER_V1.tsv and alarm registry
LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv (the defaults of --ledger and --registry; a run is GRADED only on those two, as before;
set_research_root() for an importer); the cost table of record is the copy in the tree (F/team/RESEARCH/QUANT/receipts); the default
--pins is I2G_PINS_V3_2_REL1.json (paths relative to F); the detector detect_v2, the engines and grading their rel1 editions.
VERSION, RUN_SCHEMA and every output's format are idea_to_grade_v3_2.py's.
rel1 = release edition 1: the files of one chain that run from the Alarm release folder (code found relative to this file, in the
team/ layout of the dev tree; data from arguments); no value, rule, seal or output format changes.
The rest of this text is idea_to_grade_v3_2.py's.
[V3.2, 26 Oct 2026: a NEW name for the signed V3.1 file idea_to_grade_v3.py e8e751917a208fd4 (kept unchanged; exit engine ED3 imports i2g_rules_v1). Changes: the two blockers of REVIEW_IDEA_TO_GRADE_V3_1_EXT_V1 (net FILL_SHARE without NO_COST parents; a resting entry whose decision price is older than MAX_STALE_S is NO_PRICE) and the V3.2 file names.]
idea_to_grade_v3_2.py (ALARMLIB seat, 25 Oct 2026; owner: "move the useful fixes into the existing alarm grading tool ... keep it generic,
for any alarm, any coin, any day range") — idea_to_grade V3, the same one public command as V2.3.1 with the alarm-library fixes inside:
  - matched controls AS-OF: a control is dropped only when an alarm or parent of its coin lies in [t - 4 h, t]; never by a later alarm
    (V2's rule stays beside it as a labelled sensitivity);
  - every event counted once, through a FROZEN cluster universe (--universe, i2g_universe_v1.py): weights fixed before any slice;
  - event identity = coin, second and side (two opposite-side fires in one second are two events);
  - the TOUGH baseline: same-coin moments with a similar signed 15 min move and 5 min volatility, measured by the same path;
  - one fixed grid: returns at 10 s .. 4 h, eight fixed exits, three entry types, costs per coin at the honest and stress gap;
  - --delay-s (the execution delay) is a setting, no longer the constant 6 s;
  - a run needs an open PREREG ask id of the tries ledger (--ledger-ask), named in RUN.json.
V3.1 (the six fixes of REVIEW_IDEA_TO_GRADE_V3_INDEP): a price across a feed hole is unknown (F1); the universe and the cost table are
checked and their sha16 frozen at admission, rechecked before commit (F2); the ask must register this alarm id and these days and admits
ONE complete run (F3); the 15 min move is signed per row (F4); --alarm-id must be a registry id bound to the definition or to the
universe's source list (F5); the shared rules are one copy, alarm_contract_v1.py (F6). A run on a scratch ledger or registry, without a
universe, in compatibility mode or on a reused detection is labelled TEST (RUN.json run_class, REPORT3 line 1).
V2.3.1 (idea_to_grade.py and its modules) is imported unchanged and still runs on its own pins. --compat-v2 reproduces V2.3.1's files
(V2 eligibility, V2 ids, V2 waves, no tough pool) next to the V3 columns: the compatibility check.

  PY=<PYTHON>; T=<forensics>/team/RESEARCH/tools/idea_to_grade
  nice -n 10 $PY -B $T/idea_to_grade_v3_2.py --events <list> --events-sha16 <sha> | --idea <definition.json>  --roster <ROSTER_BUILD.json>
        --coins A,B | --group NAME --group-file F  --first YYYYMMDD --last YYYYMMDD --research-window FIRST:LAST --out <new folder>
        --delay-s <seconds> --ledger-ask <PREREG ask id> --alarm-id <registry id> --universe <U.tsv> [--events-subset] [--workers 2]
No alarm, coin or date is held in this code: every one of them is the caller's."""
import argparse, hashlib, json, os, pickle, resource, sys, time, traceback
import datetime as dt
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np
import idea_to_grade_rel1 as I2
import i2g_rules_v1_2 as RU

F = I2.F; TOOLS = I2.TOOLS; US = I2.US; DIRECTIONS = I2.DIRECTIONS; MAX_WORKERS = I2.MAX_WORKERS; THREADS = I2.THREADS
Refused = I2.Refused; sha16 = I2.sha16; day_of_us = I2.day_of_us
VERSION = 'I2G_V3_2'
RUN_SCHEMA = 'I2G_RUN_V3_2'
PINS_FILE = os.path.join(HERE, 'I2G_PINS_V3_2_REL1.json')         # this edition's pins (paths relative to the tree root F)
LEDGER = REGISTRY = None                                         # the team's tries ledger and alarm registry: set_research_root(--research-root)
LEDGER_REL = 'TRIES_LEDGER_V1.tsv'                               # under RESEARCH_ROOT (the settings key)
REGISTRY_REL = 'LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv'     # under RESEARCH_ROOT
COSTS = F + '/team/RESEARCH/QUANT/receipts/COSTS_PER_COIN_V1.tsv'


def set_research_root(root):
    """the canonical tries ledger and alarm registry (the defaults of --ledger and --registry; run_class: GRADED only on them) under
    the research root (--research-root: the settings key RESEARCH_ROOT)"""
    global LEDGER, REGISTRY
    LEDGER = os.path.join(root, LEDGER_REL); REGISTRY = os.path.join(root, REGISTRY_REL)


GAPS = {'HONEST': 0.032, 'STRESS': 0.144}                       # the settings gap (pct round trip): SKILL_REFERENCE_V2 9.2
MAKER_FEE_BP = 1.5                                              # a resting leg's fee (bp); the cost table's fee_bp 9 = two 4.5 bp taker legs
REQUIRED_FILES = I2.REQUIRED_FILES + ('matches/TOUGH.tsv', 'matches/TOUGH_CENSUS.tsv', 'measurements/VALUES3.npy', 'measurements/NAMES3.json',
                                      'grade3/TABLE.tsv', 'grade3/WEIGHTS.tsv', 'grade3/REPORT3.md', 'grade3/NO_COST.tsv')
DETECT_FILES = I2.DETECT_FILES


def warm():
    I2.warm()
    import i2g_engine_v3_2_rel1, i2g_grade3_v3_2                         # noqa: F401 (executed files are pinned)
    return i2g_engine_v3_2_rel1


def _worker_init():
    I2._worker_init()
    import i2g_engine_v3_2_rel1, i2g_rules_v1_2                       # noqa: F401
    import i2g_engine_rel1 as E2
    E2.process_modules(refresh=True)


def admit_v3(a, coins):
    """the V3 settings, checked before staging: ledger ask (this alarm id and these days, not yet used), delay, registry and alarm id,
    costs for every selected coin, universe (checked row by row). The sha16 of every input file read here is frozen now (recheck_frozen
    before commit) -> (PREREG row, costs, universe or None, frozen {name: (path, sha16)}, registry row, binding, run class)"""
    frozen = {}
    def freeze(name, path):
        frozen[name] = (os.path.abspath(path), sha16(path))
    pre = RU.ledger_check(a.ledger, a.ledger_ask, idea=a.alarm_id, first=a.first, last=a.last)
    if not (a.delay_s >= 0 and a.delay_s == a.delay_s and a.delay_s < 3600):
        raise Refused('DELAY', '--delay-s %r' % a.delay_s)
    try:
        freeze('costs', a.costs); costs = RU.read_costs(a.costs)
    except (OSError, KeyError, ValueError) as e:
        raise Refused('COSTS_FILE', str(e))
    freeze('registry', a.registry); reg = RU.read_registry(a.registry)
    uni = None
    if a.universe:
        try:
            freeze('universe', a.universe); uni = RU.Universe.read(a.universe)
        except (OSError, ValueError) as e:
            if isinstance(e, RU.Refused):
                raise
            raise Refused('UNIVERSE_FORMAT', str(e))
    row, binding = RU.alarm_check(reg, a.alarm_id, definition_sha16=sha16(a.idea) if a.idea else None,
                                  events_sha16=a.events_sha16 if a.events else None, universe=uni, events_subset=a.events_subset)
    if a.events_subset and binding != 'DECLARED_SUBSET':
        raise Refused('EVENTS_SUBSET', '--events-subset is for an event list graded with a universe that is not its source list')
    test = run_class(a)
    if test == 'GRADED' and uni is None:
        raise Refused('UNIVERSE_REQUIRED', 'a graded run reads its weights from a frozen universe (--universe); without one the run is TEST only')
    return pre, costs, uni, frozen, row, binding, test


def cost_split(coins, costs):
    """-> (the coins without a cost of record, sorted; {coin: cost_bp, NaN for those}). A NaN cost makes every net value and every cost-unit
    exit of the coin unknown, so its parents count in the GROSS rows only; nothing is refused"""
    return sorted(set(coins) - set(costs)), {c: (costs[c][0] if c in costs else float('nan')) for c in coins}


def run_class(a):
    """'GRADED' only on the canonical ledger and registry, with a universe, without compatibility mode or a reused detection"""
    canon = bool(LEDGER and REGISTRY) and os.path.realpath(a.ledger) == os.path.realpath(LEDGER) and os.path.realpath(a.registry) == os.path.realpath(REGISTRY)
    return 'GRADED' if canon and a.universe and not a.compat_v2 and not a.detect_run else 'TEST'


def recheck_frozen(frozen):
    """every input file frozen at admission must still have its sha16 (F2) -> refuse <NAME>_CHANGED"""
    for name, (path, h) in sorted(frozen.items()):
        try:
            now = sha16(path)
        except OSError:
            now = None
        if now != h:
            raise Refused('%s_CHANGED' % name.upper(), '%s changed during the run (%s -> %s)' % (path, h, now))


def load_events_v3(path):
    """the event list, checked row by row exactly as V2.3.1's strict loader (event_profile.load_alarms: coin, whole t > 0, side -1/0/+1
    (blank = 0), onset_t blank or a whole time <= t) but with the V3 event identity: coin (without case), second AND side. A buy and a sell
    of one coin in one second are two events; the same coin, second and side twice is refused. A bad row is refused by line, never skipped."""
    import csv, re
    ep = os.path.realpath(os.path.join(HERE, '..', 'event_profile'))          # the same file V2.3.1 loads from TOOLS
    if ep not in sys.path:
        sys.path.insert(0, ep)
    import event_profile as EP
    with open(path) as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        R = list(rd); fields = rd.fieldnames or []
    if R and not {'coin', 't'} <= set(fields):
        raise ValueError('%s: the columns coin and t are required (got %s): refused' % (path, fields))
    coin, t, side, onset, trig = [], [], [], [], []; seen = {}
    for n, r in enumerate(R, start=2):
        c = (r.get('coin') or '').strip()
        if not c or not re.fullmatch(r'[A-Za-z0-9_]+', c):
            raise ValueError('%s line %d: coin %r: refused' % (path, n, r.get('coin')))
        tt = EP._whole(r.get('t'), 't', path, n)
        if tt <= 0 or tt * US >= 2 ** 63:
            raise ValueError('%s line %d: t %d: refused' % (path, n, tt))
        sd = 0 if (r.get('side') or '').strip() == '' else EP._whole(r.get('side'), 'side', path, n)
        if sd not in EP.SIDES:
            raise ValueError('%s line %d: side %r must be -1, 0 or +1: refused' % (path, n, r.get('side')))
        key = (c.upper(), tt, sd)
        if key in seen:
            raise ValueError('%s line %d: duplicate event identity (coin %s, t %d, side %+d), first on line %d: refused'
                             % (path, n, c, tt, sd, seen[key]))
        seen[key] = n
        given = (r.get('onset_t') or '').strip() != ''
        ot = EP._whole(r.get('onset_t'), 'onset_t', path, n) if given else -1
        if given and not 0 < ot <= tt:
            raise ValueError('%s: an onset after its alarm (line %d): refused' % (path, n))
        coin.append(c); t.append(tt); side.append(sd); onset.append(ot); trig.append((r.get('trigger') or '').strip())
    return dict(coin=np.array(coin), t=np.array(t, np.int64), side=np.array(side, int), onset_t=np.array(onset, np.int64),
                trigger=np.array(trig))


def event_list_prepare(a):
    """V2.3.1's event list input (idea_to_grade.event_list_prepare) with the V3 loader (load_events_v3: identity coin, second and side);
    every other check is V2.3.1's -> the selected rows"""
    import detect_v2 as detect
    src = os.path.abspath(a.events)
    if not os.path.isfile(src):
        raise Refused('EVENT_LIST_MISSING', src)
    if sha16(src) != a.events_sha16:
        raise Refused('EVENT_LIST_SHA', '%s is %s, pinned %s' % (src, sha16(src), a.events_sha16))
    roster, roster_sha = detect.load_roster(a.roster)
    coins_arg = a.coins if a.coins is not None else (None if a.group else 'ALL')
    chosen, selection = detect.select_coins(roster, coins_arg, a.group, a.group_file)
    try:
        ev = load_events_v3(src)
    except ValueError as e:
        raise Refused('EVENT_LIST_INVALID', str(e)[:500])
    rows = []; outside = other = side0 = 0
    for c, t, sd, ot, tr in zip(ev['coin'], ev['t'], ev['side'], ev['onset_t'], ev['trigger']):
        d = day_of_us(int(t) * US)
        if c not in chosen:
            other += 1; continue
        if not a.first <= d <= a.last:
            outside += 1; continue
        if int(sd) == 0:
            side0 += 1; continue
        eid = hashlib.sha256(('%s|%s|%d|%d' % (a.events_sha16, c, int(t), int(sd))).encode()).hexdigest()[:16]
        rows.append((str(c), int(t), int(sd), int(ot) if int(ot) > 0 else '', str(tr), eid))
    if side0:
        raise Refused('EVENT_SIDE', '%d selected events have side 0; this release grades side -1 / +1 events only' % side0)
    rows.sort(key=lambda x: (x[1], x[0], x[2]))
    return {'src': src, 'rows': rows, 'chosen': chosen, 'selection': selection, 'roster_sha': roster_sha, 'n': int(len(ev['t'])),
            'other': other, 'outside': outside}


def selected_coins(a):
    import detect_v2 as detect
    if a.events:
        return None
    roster, _ = detect.load_roster(a.roster)
    chosen, _ = detect.select_coins(roster, a.coins if a.coins is not None else (None if a.group else 'ALL'), a.group, a.group_file)
    return chosen


def run(a):
    t_start = time.perf_counter(); phases = {}; started = dt.datetime.now(dt.timezone.utc).isoformat()
    compat = bool(a.compat_v2)
    if not 1 <= a.workers <= MAX_WORKERS:
        raise Refused('WORKERS', '1..%d' % MAX_WORKERS)
    window = tuple(a.research_window.split(':'))
    if len(window) != 2:
        raise Refused('RESEARCH_WINDOW', 'FIRST:LAST, got %r' % a.research_window)
    for d, what in ((window[0], 'research window first'), (window[1], 'research window last'), (a.first, '--first'), (a.last, '--last')):
        I2.strict_day(d, what)
    if not I2.gate_ok():
        raise Refused('GATE_NOT_RUN', I2.GATE)
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise Refused('NICE10_REQUIRED', 'run the command under nice -n 10')
    for kk in THREADS:
        os.environ[kk] = '1'
    out = os.path.abspath(a.out)
    if os.path.lexists(out):
        raise Refused('OUTPUT_EXISTS', '%s exists: a run is published into a new folder only' % out)
    pins = I2.load_pins(a.pins); pins_sha = sha16(a.pins)
    I2.recheck_pins(pins)
    E = warm(); import i2g_grade_rel1 as GR, i2g_grade3_v3_2 as G3, detect_v2 as detect
    H = I2.load_helper()
    I2.check_against_pins(pins, I2.census_modules(), 'the run process')
    I2.check_window(window, a.first, a.last)
    prep = None
    if a.events:
        prep = event_list_prepare(a); coins_sel = list(prep['chosen'])
    elif a.detect_run:
        I2.read_detect(os.path.abspath(a.detect_run), a.allow_fixture); coins_sel = None
    else:
        _, info = detect.load_definition(a.idea)
        for key in ('first', 'last'):
            if key in info.get('window', {}):
                try:
                    I2.strict_day(info['window'][key], 'definition window %s' % key)
                except Refused as e:
                    raise Refused('DEFINITION_WINDOW_MALFORMED', str(e))
        coins_sel = list(selected_coins(a))
    pre, costs, uni, frozen, reg_row, binding, rclass = admit_v3(a, coins_sel or [])
    alarm_id = a.alarm_id
    mem = I2.TreeMemory(int(a.max_rss_gb * 1024 ** 3))
    try:
        pending = H.stage(out)
    except H.RunRefused as e:
        mem.close(); raise Refused(e.code, str(e))
    pool = None
    try:
        phases['admission'] = time.perf_counter() - t_start
        # ---- 1 DETECT (V2.3.1's stage, unchanged)
        t0 = time.perf_counter()
        if a.detect_run:
            det_dir = os.path.abspath(a.detect_run); detection = 'REUSED_FOR_TEST'
        elif a.events:
            det_dir = os.path.join(pending, 'detect'); I2.event_list_write(a, prep, det_dir); detection = 'EVENT_LIST'
        else:
            det_dir = os.path.join(pending, 'detect')
            coins = a.coins if a.coins is not None else (None if a.group else 'ALL')
            try:
                detect.run(a.idea, a.first, a.last, det_dir, a.roster, coins=coins, group=a.group, group_file=a.group_file, workers=a.workers,
                           lab_root=a.lab_root, research_window=window, gate=I2.GATE)
            except detect.Refusal as e:
                raise Refused('DETECT_' + e.code, str(e))
            detection = 'FRESH'
        dm, events, coverage = I2.read_detect(det_dir, a.allow_fixture)
        if dm['first'] != a.first or dm['last'] != a.last:
            raise Refused('DETECT_RANGE', 'detector run %s..%s, asked %s..%s' % (dm['first'], dm['last'], a.first, a.last))
        outside = sorted({x[4:12] for x in dm.get('sources', {}) if x.startswith('day=') and not window[0] <= x[4:12] <= window[1]})
        if outside:
            raise Refused('DETECT_READ_OUTSIDE_WINDOW', 'the detector read days %s outside the research window' % outside[:5])
        if 'code_sha16' in dm and isinstance(dm['code_sha16'], dict):
            I2.check_against_pins(pins, {os.path.realpath(q): h for q, h in dm['code_sha16'].items()}, 'the detector run')
        phases['detect'] = time.perf_counter() - t0
        if mem.over:
            raise Refused('MEMORY_LIMIT', str(mem.over))
        # ---- parents and coin tasks
        t0 = time.perf_counter()
        coins = list(dm['coins']) if 'coins' in dm else list(dm['selection']['coins'])
        no_cost, cost_bp = cost_split(coins, costs)       # a coin without a cost of record is graded before cost only (NO_COST)
        k = E.K.load(); split = k.D.split_from(k.gates.WINDOWS)
        by_coin = {}
        for r in events:
            t = int(r['t']); sd = int(r['side'])
            if sd not in (-1, 1):
                raise Refused('EVENT_SIDE', 'side %r (side-0 events are not graded by this release)' % r['side'])
            by_coin.setdefault(r['coin'], []).append((t, sd, r.get('event_id', '')))
        known = {}
        for r in coverage:
            if r['full_known'] == '1':
                known.setdefault(r['coin'], []).append(r['day'])
        cpct = {c: RU.coin_cost_pct(cost_bp[c], GAPS['HONEST']) for c in coins}
        v3 = {'eligibility': 'v2' if compat else a.eligibility, 'identity': 'v2' if compat else 'side', 'delay_s': float(a.delay_s),
              'tough': not compat, 'asof_before_s': RU.ASOF_BEFORE_S}
        total = sum(len(v) for v in by_coin.values()); size = max(a.min_chunk, -(-total // (4 * a.workers)))
        if a.chunk:
            size = a.chunk
        tasks = []
        for c in coins:
            ps = sorted(by_coin.get(c, []))
            if not ps:
                continue
            parts = {}
            for t, sd, _ in ps:
                parts.setdefault(k.D.part_of(float(t), split), []).append((t, sd))
            for part in sorted(parts, key=lambda x: (x is None, x)):
                if part is None:
                    raise Refused('PARENT_OUTSIDE_SPLIT', '%s has events outside every split part' % c)
                pp = parts[part]
                for j in range(0, len(pp), size):
                    tasks.append(dict(coin=c, order=(part, j // size), parents=pp[j:j + size], alarms=[t for t, _, _ in ps],
                                      known_days=known.get(c, []), lab_root=a.lab_root, window=list(window), split=[list(x) for x in split],
                                      settings=dict(k.D.S0), seed=a.seed, measure=True, v3=dict(v3, c_pct=cpct[c])))
        run_order = sorted(range(len(tasks)), key=lambda i: -len(tasks[i]['parents']))
        phases['plan'] = time.perf_counter() - t0
        # ---- 2+3 MATCH and MEASURE
        t0 = time.perf_counter()
        import multiprocessing as mp
        from concurrent.futures import ProcessPoolExecutor
        pool = ProcessPoolExecutor(max_workers=a.workers, mp_context=mp.get_context('spawn'), initializer=_worker_init)
        futs = {i: pool.submit(E.coin_job, tasks[i]) for i in run_order}
        results = {}
        vintages = dict(dm.get('price_index_sha16', {}))
        for i in run_order:
            try:
                r = futs[i].result()
            except E.SourceChanged as e:
                raise Refused('SOURCE_CHANGED', str(e))
            r['order'] = tasks[i]['order']; results.setdefault(r['coin'], []).append(r)
            for d, h in r['price_vintages'].items():
                if vintages.setdefault(d, h) != h:
                    raise Refused('SOURCE_CHANGED', 'PRICE %s was seen in two states in one run (%s, %s)' % (d, vintages[d], h))
            I2.check_against_pins(pins, r['modules'], 'worker %d' % r['pid'])
            if mem.over:
                raise Refused('MEMORY_LIMIT', str(mem.over))
            if not I2.gate_ok():
                raise Refused('GATE_NOT_RUN', 'the gate left RUN during the run')
        for c in results:
            results[c].sort(key=lambda r: r['order'])
        phases['match_measure'] = time.perf_counter() - t0
        # ---- aggregate
        t0 = time.perf_counter()
        agg = aggregate(coins, events, results, k, split, a.delay_s, compat, uni, alarm_id)
        for sub in ('matches', 'measurements', 'grading'):
            os.makedirs(os.path.join(pending, sub))
        write_matches(pending, agg, k)
        I2.write_measurements(pending, agg)
        np.save(os.path.join(pending, 'measurements', 'VALUES3.npy'), agg['values3'])
        I2._json(os.path.join(pending, 'measurements', 'NAMES3.json'), RU.value_names())
        inputs = grading_inputs(agg, a.delay_s)
        inputs_path = os.path.join(pending, 'grading', 'GRADING_INPUT.pkl')
        with open(inputs_path, 'wb') as f:
            pickle.dump(inputs, f, protocol=5)
        phases['aggregate'] = time.perf_counter() - t0
        # ---- 4 GRADE: V2.3.1's 190 cohorts (the outside kernel), then the V3 tables
        t0 = time.perf_counter()
        S = k.S
        offers = list(S.OFFERS); halves = [offers[:len(offers) // 2], offers[len(offers) // 2:]]
        gtasks = [dict(run_key=inputs['run_key'], inputs_path=inputs_path, values_path=os.path.join(pending, 'measurements', 'VALUES.npy'),
                       direction=d, horizon=h, offers=o) for h in S.HORIZONS[::-1] for d in DIRECTIONS for o in halves]
        gres = [f.result() for f in [pool.submit(GR.grade_task, t) for t in gtasks]]
        for g in gres:
            I2.check_against_pins(pins, g['modules'], 'worker %d' % g['pid'])
        peaks = {}
        for r in [x for v in results.values() for x in v] + gres:
            peaks[r['pid']] = max(peaks.get(r['pid'], 0), r['ru_maxrss'])
        pool.shutdown(wait=True); pool = None
        phases['grade'] = time.perf_counter() - t0
        t0 = time.perf_counter()
        legs = {cn: {c: RU.cost_legs(cost_bp[c], gap, a.maker_fee_bp) for c in coins} for cn, gap in GAPS.items()}
        nc_rows = [(p['id'], p['coin'], 'NO_COST') for p in agg['parents'] if p['coin'] in no_cost]
        table = G3.grade(agg['parents'], RU.value_names(), agg['values3'], [q[1] for q in agg['requests']], agg['calm'], agg['calm_v2'],
                         agg['tough_rows'], agg['weights'], agg['clusters'], legs)
        split_line = chain_split_line(agg, table, G3, legs)
        head = ['# idea_to_grade %s %s: %d parents, alarm id %s (events bound by %s)' % (VERSION, rclass, len(agg['parents']), alarm_id, binding),
                '',
                'Weights: %s. Delay %.3f s. Eligibility %s. Costs %s (gap honest %.3f, stress %.3f pct round trip; resting fee %.2f bp).'
                % (agg['weights_source'], a.delay_s, v3['eligibility'], a.costs, GAPS['HONEST'], GAPS['STRESS'], a.maker_fee_bp),
                split_line,
                'NO_COST: %d parents on %d coins without a cost of record (%s) are graded before cost only: they are in the GROSS rows, '
                'absent from the HONEST and STRESS rows, and listed in grade3/NO_COST.tsv.'
                % (len(nc_rows), len({r[1] for r in nc_rows}), ','.join(sorted({r[1] for r in nc_rows})) or 'none'),
                'Path holes: %d observation rows have at least one value unknown because the feed had no trade for more than %d s.'
                % (int(np.sum(agg['values3'][:, RU.value_names().index('path_holes')] > 0)), RU.MAX_STALE_S),
                'Tough pool: %s of %d parents have at least %d tough moments.' % (agg['tough_covered'], len(agg['parents']), RU.TOUGH['min_n']),
                'Describes what the stored paths did after each event against the baselines; not causality, not a strategy, not live parity.']
        G3.write(os.path.join(pending, 'grade3'), table, agg['weights_rows'], head)
        I2._tsv(os.path.join(pending, 'grade3', 'NO_COST.tsv'), ['parent_id', 'coin', 'reason'], nc_rows)
        phases['grade3'] = time.perf_counter() - t0
        if mem.over:
            raise Refused('MEMORY_LIMIT', str(mem.over))
        # ---- 5 PUBLISH
        t0 = time.perf_counter()
        report = I2.write_grading(pending, agg, inputs, gres, S)
        rp = os.path.join(pending, 'grading', 'REPORT.md'); txt = open(rp).read()   # the V2 writer names its own version in line 1
        with open(rp, 'w') as f:
            f.write(txt.replace('idea_to_grade %s' % I2.VERSION, 'idea_to_grade %s' % VERSION, 1))
        parts = {}
        for root, _, files in os.walk(pending):
            for n in files:
                p = os.path.join(root, n); parts[os.path.relpath(p, pending)] = sha16(p)
        if not I2.gate_ok():
            raise Refused('GATE_NOT_RUN', 'the gate left RUN before publication')
        if a.events and sha16(a.events) != a.events_sha16:
            raise Refused('EVENT_LIST_CHANGED', 'the event list changed during the run')
        if a.idea and sha16(a.idea) != dm['definition']['sha16']:
            raise Refused('IDEA_CHANGED', 'the definition changed during the run')
        I2.recheck_pins(pins, 'CODE_CHANGED')
        changed = [d for d, h in sorted(vintages.items()) if E.price_state(a.lab_root, d) != h]
        if changed:
            raise Refused('SOURCE_CHANGED', 'PRICE changed (or appeared / disappeared) during the run on %s' % changed[:5])
        if sha16(a.pins) != pins_sha:
            raise Refused('CODE_CHANGED', 'the pins file changed during the run')
        RU.ledger_check(a.ledger, a.ledger_ask, idea=alarm_id, first=a.first, last=a.last)   # still open and unused at publication
        recheck_frozen(frozen)
        phases['publish_write'] = time.perf_counter() - t0
        mem.close()
        counts = dict(report['counts'], tough_rows=len(agg['tough']), tough_covered=agg['tough_covered'], table3_rows=len(table),
                      no_cost_parents=len(nc_rows), no_cost_coins=sorted({r[1] for r in nc_rows}))
        body = {
            'tool': 'idea_to_grade', 'version': VERSION, 'run_id': hashlib.sha256(('%s|%s' % (out, started)).encode()).hexdigest()[:16],
            'started_utc': started, 'idea': {'path': os.path.abspath(a.idea), 'sha16': sha16(a.idea)} if a.idea else None,
            'event_list': {'path': os.path.abspath(a.events), 'sha16': a.events_sha16} if a.events else None,
            'run_class': rclass,
            'alarm_id': alarm_id, 'alarm': {'registry': {'path': frozen['registry'][0], 'sha16': frozen['registry'][1]},
                                            'definition_sha16': reg_row.get('definition_sha16'), 'card': reg_row.get('card'),
                                            'events_binding': binding,
                                            'universe_source': list(uni.sources[alarm_id]) if uni is not None else None},
            'ledger': {'path': os.path.abspath(a.ledger), 'ask_id': a.ledger_ask, 'prereg_utc': pre.get('try_utc'),
                       'idea': pre.get('idea'), 'days': [pre.get('days_from'), pre.get('days_to')], 'setting_sha16': pre.get('setting_sha16'),
                       'claim': RU._claim_path(a.ledger, a.ledger_ask)},
            'detection': detection, 'detect_run': {'path': os.path.relpath(det_dir, pending) if det_dir.startswith(pending) else det_dir,
                                                    'status': dm['status'], 'events': dm['events'], 'wall_s': dm.get('wall_s'),
                                                    'kind': dm.get('kind', 'DETECT_RUN')},
            'selection': {'coins': coins, 'group': a.group, 'group_file': a.group_file,
                          'group_file_sha16': sha16(a.group_file) if a.group_file else None, 'first': a.first, 'last': a.last,
                          'research_window': list(window), 'roster': {'path': a.roster, 'sha16': sha16(a.roster)} if a.roster else None,
                          'requested_coin_days': len(coverage), 'present_coin_days': sum(1 for r in coverage if r['status'] == 'PRESENT'),
                          'unavailable_coin_days': [{'coin': r['coin'], 'day': r['day'], 'status': r['status'], 'reason': r.get('reason', '')}
                                                    for r in coverage if r['status'] != 'PRESENT']},
            'settings': {'match': dict(k.D.S0, split=[list(x) for x in split], seed=a.seed), 'v3': dict(v3, compat_v2=compat), 'measure': {
                'names': list(S.NAMES), 'names3': RU.value_names(), 'execution_delay_s': float(a.delay_s), 'hold_s': S.HOLD_S,
                'decision_wait_s': 0, 'directions': list(DIRECTIONS), 'horizons_s': list(RU.HORIZONS_S), 'exits': [list(e) for e in RU.EXITS],
                'resting_wait_s': RU.RESTING_WAIT_S, 'tough': dict(RU.TOUGH), 'asof_before_s': RU.ASOF_BEFORE_S},
                'grade': {'offers': list(S.OFFERS), 'horizons': list(S.HORIZONS), 'wave_gap_s': RU.WAVE_GAP_S, 'wave_max_span_s': RU.WAVE_MAX_SPAN_S,
                          'weights': agg['weights_source']},
                'costs': {'path': frozen['costs'][0], 'sha16': frozen['costs'][1], 'gaps_pct': GAPS, 'maker_fee_bp': a.maker_fee_bp},
                'universe': {'path': frozen['universe'][0], 'sha16': frozen['universe'][1]} if a.universe else None,
                'max_stale_s': RU.MAX_STALE_S},
            'counts': counts, 'report': dict(report['headline'], table3='grade3/REPORT3.md'),
            'run_schema': RUN_SCHEMA, 'sources': {'price_state_by_day': dict(sorted(vintages.items())), 'lab_root': a.lab_root},
            'code_sha16': dict(sorted(pins.items())), 'pins_file': {'path': os.path.abspath(a.pins), 'sha16': pins_sha, 'files': len(pins)},
            'clocks': {'observation_known_at': 'as_of + %s s (delay + 60 s longest fill wait + 4 h hold)' % S.offset_s(float(a.delay_s), S.HOLD_S),
                       'parent_known_at': 'the latest of its own observation, its eligible and sensitivity controls, its tough moments and '
                                          'the coverage of its candidate days'},
            'parts': parts,
            'timing_s': dict(phases, wall_to_commit=time.perf_counter() - t_start),
            'memory': {'tree_peak_sampled_bytes': mem.peak, 'tree_peak_processes': mem.peak_procs, 'samples': mem.samples,
                       'limit_bytes': mem.limit, 'parent_ru_maxrss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       'worker_ru_maxrss_bytes': peaks},
            'workers': {'processes': a.workers, 'start_method': 'spawn', 'nice': os.getpriority(os.PRIO_PROCESS, 0), 'chunk_size': size},
            'not_asserted': 'paths after each event against matched (CALM) and same-move (TOUGH) moments; not causality, not a strategy, '
                            'research only (no live parity); Binance 3 s model prices; costs of record per coin',
        }
        body['body_sha16'] = I2.body_digest(body)
        claim = RU.ledger_claim(a.ledger, a.ledger_ask, {'out': out, 'run_id': body['run_id'], 'body_sha16': body['body_sha16'],
                                                         'alarm_id': alarm_id, 'first': a.first, 'last': a.last, 'run_class': rclass})
        try:
            m = H.commit(pending, out, 'RUN', body)
        except BaseException as e:   # the run did not complete: the ask is not used (the claim is kept, renamed, as the record)
            os.rename(claim, claim + '.failed_%s' % dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
            if isinstance(e, H.RunRefused):
                raise Refused(e.code, str(e))
            raise
        wall = time.perf_counter() - t_start
        print(json.dumps({'status': 'COMPLETE', 'run_class': rclass, 'out': out, 'wall_s': round(wall, 3), 'parents': counts['parents'],
                          'tough_covered': agg['tough_covered'], 'tree_peak_gb': round(mem.peak / 1024 ** 3, 3)}))
        return m
    except BaseException as e:
        try:
            if pool is not None:
                pool.shutdown(wait=False, cancel_futures=True)
        finally:
            mem.close()
            failed = H.abort(pending, out, '%s\n%s' % (repr(e), traceback.format_exc()))
            sys.stderr.write('FAILED %r -> %s\n' % (e, failed))
        raise


def aggregate(coins, events, results, k, split, delay_s, compat, uni, alarm_id):
    """V2.3.1's aggregate (identities, request order, clocks) with the V3 identity, the union of the two control rules' rows, the tough rows,
    the V3 columns and the frozen weights"""
    import i2g_engine_v3_2_rel1 as E
    S = k.S
    pid_of = (lambda c, t, s: '%s_%d' % (c, t)) if compat else (lambda c, t, s: RU.parent_id(c, t, s))
    census, edges, balance, unavailable, tough, tcen = [], [], [], [], [], []
    for c in coins:
        for r in results.get(c, []):
            census += r['census']; edges += r['edges']; balance += r['balance']; unavailable += r['unavailable']
            tough += r.get('tough', []); tcen += r.get('tough_census', [])
    ev_id = {pid_of(r['coin'], int(r['t']), int(r['side'])): r.get('event_id', '') for r in events}
    ident = sorted(((int(r['t']) * US, r['coin'], int(r['side'])) for r in events))
    pids = [pid_of(c, t // US, s) for t, c, s in ident]
    if len(set(pids)) != len(pids):
        raise Refused('PARENT_ID_COLLISION', 'two events share coin, second%s' % ('' if compat else ' and side'))
    cen = {x[0]: x for x in census}
    if set(cen) != set(pids) or len(cen) != len(census):
        raise Refused('CENSUS_POPULATION', 'census %d parents %d' % (len(census), len(pids)))
    # the weights: V2's run waves (compat), the frozen universe, or (no universe given) clusters of this run's own parents, flagged
    if compat:
        wav = k.waves(np.asarray([t / US for t, c, s in ident]), 1800)
        waves = {p: int(w) for p, w in zip(pids, wav)}
        cl_of = {p: 'W%d' % waves[p] for p in pids}; cnt = {}
        for p in pids:
            cnt[cl_of[p]] = cnt.get(cl_of[p], 0) + 1
        wt = {p: 1.0 / cnt[cl_of[p]] for p in pids}; flag = {p: '' for p in pids}
        source = 'V2 run waves (compatibility: rebuilt for this selection)'
    else:
        if uni is not None:
            got = uni.subgroup(alarm_id, pids); source = 'frozen universe %s (alarm id %s)' % (uni.name, alarm_id); src_u = uni
        else:
            rows = RU.build_clusters([(alarm_id, c, t // US, s) for t, c, s in ident])
            got = {r[4]: (r[5], r[6], r[8]) for r in rows}; src_u = RU.Universe(rows, 'RUN_LOCAL')
            source = 'RUN_LOCAL clusters of this selection (no --universe: a different selection rebuilds them; TEST only)'
        cl_of = {p: got[p][0] for p in pids}; wt = {p: got[p][1] for p in pids}; flag = {p: got[p][2] for p in pids}
        merged = src_u.merged_clusters(alarm_id)
        ids = {c: i for i, c in enumerate(sorted(set(cl_of.values())))}
        waves = {p: ids[cl_of[p]] for p in pids}
    raw_by = {}
    for e in edges:
        raw_by.setdefault(e[0], []).append(e)
    tough_by = {}
    for pid, g in tough:
        tough_by.setdefault(pid, []).append(g)
    lookup = {}; requests = []; plan_edges = []; parents = []
    def obs(kind, coin, t, side, d):
        key = (kind, coin, t, side, d)
        if key not in lookup:
            lookup[key] = len(requests); requests.append(key)
        return lookup[key]
    calm = {d: [] for d in DIRECTIONS}; calm_v2 = {d: [] for d in DIRECTIONS}; tough_rows = {d: [] for d in DIRECTIONS}
    for i, ((t, c, s), pid) in enumerate(zip(ident, pids)):
        original = raw_by.get(pid, []); eligible = [e for e in original if e[7] == '']
        cr = cen[pid]
        if len(original) != int(cr[4]):
            raise Refused('INCOMPLETE_EDGES', pid)
        p = {'id': pid, 'event_id': ev_id.get(pid, ''), 'coin': c, 'as_of_us': t, 'side': s, 'day': day_of_us(t), 'wave_id': waves[pid],
             'census_status': cr[5], 'original_draw_edges': len(original), 'eligible_edges': len(eligible),
             'rule_excluded_edges': len(original) - len(eligible), 'cov0': cr[6], 'row_ids': {}}
        for d in DIRECTIONS:
            p['row_ids'][d] = obs('parent', c, t, s, d)
        parents.append(p)
        for e in eligible:
            ct = E.ms_us(e[3]); w = float(e[5])
            for d in DIRECTIONS:
                plan_edges.append((i, obs('control', c, ct, s, d), w, d, int(e[6])))
        for d in DIRECTIONS:
            calm[d].append([]); calm_v2[d].append([]); tough_rows[d].append([])
        if not compat:
            for e in original:
                if e[8] == '' or e[9] == '':
                    ct = E.ms_us(e[3])
                    for d in DIRECTIONS:
                        q = obs('control', c, ct, s, d)
                        if e[7] == '':
                            calm[d][-1].append((q, float(e[5])))
                        if e[8] == '':
                            calm_v2[d][-1].append((q, float(e[5])))
            for g in tough_by.get(pid, []):
                for d in DIRECTIONS:
                    tough_rows[d][-1].append(obs('tough', c, int(round(g)) * US, s, d))
        else:
            for e in eligible:
                for d in DIRECTIONS:
                    q = lookup[('control', c, E.ms_us(e[3]), s, d)]
                    calm[d][-1].append((q, float(e[5]))); calm_v2[d][-1].append((q, float(e[5])))
    names = list(S.NAMES); V = np.full((len(requests), len(names)), np.nan); reasons = {}; done = np.zeros(len(requests), bool)
    V3 = np.full((len(requests), len(RU.value_names())), np.nan)
    for c in coins:
        for r in results.get(c, []):
            for j, (kind, t, s, d) in enumerate(r['obs']):
                q = lookup.get((kind, c, t, s, d))
                if q is None:
                    raise Refused('OBSERVATION_IDENTITY', '%s %s' % (c, (kind, t, s, d)))
                if done[q]:
                    same = (np.array_equal(np.isnan(V[q]), np.isnan(r['values'][j])) and
                            np.array_equal(np.nan_to_num(V[q]).view(np.uint64), np.nan_to_num(r['values'][j]).view(np.uint64)) and
                            np.array_equal(np.isnan(V3[q]), np.isnan(r['values3'][j])) and
                            np.array_equal(np.nan_to_num(V3[q]).view(np.uint64), np.nan_to_num(r['values3'][j]).view(np.uint64)))
                    if not same or reasons.get(str(q), {}) != r['reasons'].get(j, {}):
                        raise Refused('OBSERVATION_CONFLICT', '%s %s' % (c, (kind, t, s, d)))
                    continue
                V[q] = r['values'][j]; V3[q] = r['values3'][j]; done[q] = True
                if j in r['reasons']:
                    reasons[str(q)] = r['reasons'][j]
    if not done.all():
        raise Refused('OBSERVATION_COUNT', '%d of %d requested rows measured' % (int(done.sum()), len(requests)))
    off = int(round(S.offset_s(float(delay_s), S.HOLD_S) * US)); unav = {u['fid']: u['known_at_us'] for u in unavailable}
    bounds = {n: (x, y) for n, x, y in split}
    for i, p in enumerate(parents):
        t = p['as_of_us']; ka = t + off
        if p['census_status'] == 'COMPARISON_UNAVAILABLE':
            ka = max(ka, unav[p['id']])
        elif p['census_status'] in ('MATCHED', 'NO_ELIGIBLE'):
            part = k.D.part_of(t / US, split); last = min(bounds[part][1], E.shift(p['day'], int(k.D.S0['days'])))
            ka = max(ka, int(k.D._day_start(E.shift(last, 1))) * US)
            ka = max([ka] + [E.ms_us(e[3]) + off for e in raw_by.get(p['id'], []) if e[7] == '' or (not compat and e[8] == '')])
        ka = max([ka] + [requests[q][2] + off for q in tough_rows['FOLLOW'][i]])
        p['known_at_us'] = ka
    months = sorted({p['day'][:6] for p in parents})
    coverage = {}
    for month in ['ALL'] + months:
        sel = [p for p in parents if month == 'ALL' or p['day'][:6] == month]
        counts = {s: sum(p['census_status'] == s for p in sel) for s in sorted({p['census_status'] for p in sel})}
        coverage[month] = {'full_parent_count': len(sel), 'census_status_counts': counts,
                           'comparison_unavailable_parents': counts.get('COMPARISON_UNAVAILABLE', 0), 'matched_parents': counts.get('MATCHED', 0),
                           'interpretation': 'Comparisons describe supported matched parents only; standalone measurements retain every parent.'}
    covered = sum(1 for i in range(len(parents)) if len(tough_rows['FOLLOW'][i]) >= RU.TOUGH['min_n'])
    cl_merged = [cl_of[p] for p in pids] if compat else [merged[cl_of[p]] for p in pids]
    return dict(parents=parents, pids=pids, waves=waves, requests=requests, edges=plan_edges, raw_edges=edges, census=census,
                balance=balance, unavailable=unavailable, values=V, values3=V3, reasons=reasons, names=names, months=months, coverage=coverage,
                offset_us=off, calm=calm, calm_v2=calm_v2, tough_rows=tough_rows, tough=tough, tough_census=tcen, tough_covered=covered,
                weights=[wt[p] for p in pids], clusters=[cl_of[p] for p in pids], clusters_merged=cl_merged, weights_source=source,
                weights_rows=[(p, cl_of[p], wt[p], flag[p]) for p in pids])


def chain_split_line(agg, table, G3, legs):
    """the chain-split sensitivity (OX-DATA point 7): the ALL rows again with every split chain merged back into one cluster for the
    interval (weights unchanged) -> one REPORT3 line"""
    moved = [i for i, (a, b) in enumerate(zip(agg['clusters'], agg['clusters_merged'])) if a != b]
    if not moved:
        return 'Chain-split sensitivity: no parent of this run sits in a split chain (nothing to merge).'
    n_chains = len({agg['clusters_merged'][i] for i in moved})
    again = G3.grade(agg['parents'], RU.value_names(), agg['values3'], [q[1] for q in agg['requests']], agg['calm'], agg['calm_v2'],
                     agg['tough_rows'], agg['weights'], agg['clusters_merged'], legs, slices=('ALL',))
    base = {r[:6]: r for r in table if r[0] == 'ALL'}; ch = []
    for r in again:
        b = base[r[:6]]
        if np.isfinite(b[7]) and np.isfinite(b[8]) and np.isfinite(r[7]) and np.isfinite(r[8]) and b[8] > b[7]:
            ch.append(abs((r[8] - r[7]) / (b[8] - b[7]) - 1.0) * 100.0)
    return ('Chain-split sensitivity: %d parents sit in %d split chains; merged back into one cluster each for the interval, the 95%% '
            'half-width of the %d ALL rows with an interval changes by at most %.2f%% (median %.2f%%).'
            % (len(moved), n_chains, len(ch), max(ch) if ch else 0.0, float(np.median(ch)) if ch else 0.0))


def write_matches(pending, agg, k):
    d = os.path.join(pending, 'matches')
    I2._tsv(os.path.join(d, 'CENSUS.tsv'), ['fid', 'coin', 't', 'side', 'matches', 'status', 'cov0'], agg['census'])
    I2._tsv(os.path.join(d, 'EDGES.tsv'), ['fid', 'coin', 'parent_t', 'cand_t', 'side', 'weight', 'draw_index', 'own', 'own_v2', 'asof'],
            agg['raw_edges'])
    bal = k.D.balance([(m, kd, float(c), float(w), o) for m, kd, c, w, o in agg['balance']])
    I2._tsv(os.path.join(d, 'BALANCE.tsv'), ['month', 'parents_with_cov', 'matched', 'unmatched', 'smd_before', 'smd_after', 'median_cov_unmatched',
                                             'median_cov_matched', 'matches', 'share_before_30m', 'share_within_h'],
            [tuple('%.4f' % x if isinstance(x, float) else x for x in r) for r in bal])
    I2._json(os.path.join(d, 'COMPARISON_COVERAGE.json'), agg['coverage'])
    I2._json(os.path.join(d, 'UNAVAILABLE.json'), agg['unavailable'])
    I2._tsv(os.path.join(d, 'TOUGH.tsv'), ['parent_id', 'tough_t'], [(p, '%.0f' % g) for p, g in agg['tough']])
    I2._tsv(os.path.join(d, 'TOUGH_CENSUS.tsv'), ['parent_id', 'status', 'pool', 'chosen', 'move15_pct', 'rv5_pct'],
            [(p, st, n, ch, repr(float(mv)), repr(float(rv))) for p, st, n, ch, mv, rv in agg['tough_census']])


def grading_inputs(agg, delay_s):
    """V2.3.1's grading inputs with the run's delay"""
    req = agg['requests']; n = len(req); pids = agg['pids']; parents = agg['parents']
    dirs = {}
    for d in DIRECTIONS:
        ids = np.asarray([i for i, q in enumerate(req) if q[4] == d], np.int64)
        local = np.full(n, -1, np.int64); local[ids] = np.arange(len(ids))
        es = [e for e in agg['edges'] if e[3] == d]
        dirs[d] = {'ids': ids, 'coins': np.asarray([req[i][1] for i in ids]), 'delay': np.full(len(ids), 0.0 + float(delay_s)),
                   'parents': local[np.asarray([p['row_ids'][d] for p in parents], np.int64)],
                   'edge_parent': np.asarray([e[0] for e in es], np.int64), 'control_ids': ['control:' + str(e[1]) for e in es],
                   'controls': local[np.asarray([e[1] for e in es], np.int64)], 'weights': np.asarray([e[2] for e in es], float)}
    month_ix = [('ALL', np.arange(len(parents), dtype=np.int64))] + \
               [(m, np.asarray([i for i, p in enumerate(parents) if p['day'][:6] == m], np.int64)) for m in agg['months']]
    key = hashlib.sha256(json.dumps([pids, [len(dirs[d]['ids']) for d in DIRECTIONS], [len(dirs[d]['weights']) for d in DIRECTIONS]]).encode()).hexdigest()[:16]
    return {'run_key': key, 'pids': pids, 'waves': agg['waves'], 'directions': dirs, 'month_ix': month_ix, 'names': agg['names']}


def verify_run(out):
    """V2.3.1's verify_run for the V3 schema and inventory"""
    p = os.path.join(out, 'RUN.json')
    if not os.path.isdir(out) or not os.path.isfile(p):
        raise Refused('RUN_NOT_PUBLISHED', '%s has no RUN.json' % out)
    try:
        disk = json.load(open(p))
    except ValueError as e:
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: RUN.json unreadable: %s' % (out, e))
    if disk.get('status') != 'COMPLETE' or disk.get('exit_status') != 0:
        raise Refused('RUN_INCOMPLETE', '%s: status %r' % (out, disk.get('status')))
    if disk.get('body_sha16') != I2.body_digest(disk):
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: the RUN.json body changed since the commit' % out)
    if disk.get('run_schema') != RUN_SCHEMA:
        raise Refused('RUN_SCHEMA', '%s: run schema %r, this reader reads %s' % (out, disk.get('run_schema'), RUN_SCHEMA))
    parts = disk.get('parts') if isinstance(disk.get('parts'), dict) else {}
    want = set(REQUIRED_FILES) | (set() if disk.get('detection') == 'REUSED_FOR_TEST' else set(DETECT_FILES))
    if set(parts) != want:
        raise Refused('RUN_INVENTORY', '%s: missing %s, extra %s' % (out, sorted(want - set(parts))[:5], sorted(set(parts) - want)[:5]))
    on_disk = set()
    for root, _, files in os.walk(out):
        for n in files:
            on_disk.add(os.path.relpath(os.path.join(root, n), out))
    on_disk.discard('RUN.json')
    added, missing = sorted(on_disk - set(parts)), sorted(set(parts) - on_disk)
    if added or missing:
        raise Refused('RUN_CHANGED_AFTER_COMMIT', '%s: files added %s, missing %s' % (out, added[:5], missing[:5]))
    I2.check_consistency(out, disk)
    rows3 = np.load(os.path.join(out, 'measurements', 'VALUES3.npy'), mmap_mode='r').shape[0]
    if rows3 != disk['counts'].get('observations'):
        raise Refused('RUN_INCONSISTENT', '%s: VALUES3 rows %d, observations %s' % (out, rows3, disk['counts'].get('observations')))
    H = I2.load_helper()
    try:
        return H.load_complete(out, 'RUN')
    except H.RunRefused as e:
        raise Refused(e.code, str(e))


def parser():
    p = argparse.ArgumentParser(description='idea_to_grade V3: idea or event list -> detection -> controls (as-of) and tough moments -> '
                                            'measurements -> V2 cohorts + V3 tables -> RUN.json')
    p.add_argument('--idea'); p.add_argument('--events'); p.add_argument('--events-sha16')
    p.add_argument('--roster'); p.add_argument('--coins'); p.add_argument('--group'); p.add_argument('--group-file')
    p.add_argument('--first', required=True); p.add_argument('--last', required=True); p.add_argument('--research-window', required=True)
    p.add_argument('--out', required=True); p.add_argument('--workers', type=int, default=2); p.add_argument('--max-rss-gb', type=float, default=16.0)
    p.add_argument('--lab-root', required=True, help='the lab days (the settings key LAB_DAYS)'); p.add_argument('--seed', type=int, default=20261023)
    p.add_argument('--gate', default=None, help="the feed's stop gate file (the settings key FEED_GATE); empty or not given: no gate")
    p.add_argument('--research-root', required=True, help='the research data (the settings key RESEARCH_ROOT): the tries ledger and the alarm registry')
    p.add_argument('--min-chunk', type=int, default=50); p.add_argument('--chunk', type=int, default=0)
    p.add_argument('--detect-run'); p.add_argument('--allow-fixture', action='store_true')
    p.add_argument('--pins', default=PINS_FILE)
    p.add_argument('--delay-s', type=float, required=True, help='the execution delay, seconds (measured live values, or 6 to compare with V2)')
    p.add_argument('--ledger-ask', required=True, help='the PREREG ask id of this try in the tries ledger (ledger_add_v6.py prereg ...)')
    p.add_argument('--ledger', default=None, help='the tries ledger (default RESEARCH_ROOT/TRIES_LEDGER_V1.tsv)')
    p.add_argument('--costs', default=COSTS); p.add_argument('--maker-fee-bp', type=float, default=MAKER_FEE_BP)
    p.add_argument('--universe', help='the frozen cluster universe (i2g_universe_v1.py); without it: RUN_LOCAL clusters, flagged')
    p.add_argument('--alarm-id', required=True, help='the registry id of the alarm (ALARM_REGISTRY_V1); the PREREG row must name it')
    p.add_argument('--registry', default=None, help='the alarm registry (default RESEARCH_ROOT/LIBRARY/alarm_library/ALARM_REGISTRY_V1.tsv; '
                                                    'another file than the canonical one makes the run TEST)')
    p.add_argument('--events-subset', action='store_true', help='the event list is a declared slice of the universe source list of the alarm')
    p.add_argument('--eligibility', choices=('asof', 'v2'), default='asof')
    p.add_argument('--compat-v2', action='store_true', help='COMPATIBILITY CHECK: V2 eligibility, ids and waves, no tough pool')
    return p


def main(argv=None):
    p = parser(); a = p.parse_args(argv)
    set_research_root(a.research_root); I2.set_gate(a.gate)
    a.ledger = a.ledger or LEDGER; a.registry = a.registry or REGISTRY
    if a.events and not a.events_sha16:
        p.error('--events needs --events-sha16 (the list is pinned)')
    if sum(bool(x) for x in (a.idea, a.events, a.detect_run)) != 1:
        p.error('give exactly one input: --idea, --events or --detect-run (tests only)')
    if not a.detect_run and not a.roster:
        p.error('--roster is required')
    import detect_v2 as detect
    try:
        run(a)
    except Refused as e:
        sys.stderr.write('REFUSED %s\n' % e); sys.exit(2)
    except RU.Refused as e:
        sys.stderr.write('REFUSED %s\n' % e); sys.exit(2)
    except detect.Refusal as e:
        sys.stderr.write('REFUSED DETECT_%s\n' % e); sys.exit(2)


if __name__ == '__main__':
    main()
