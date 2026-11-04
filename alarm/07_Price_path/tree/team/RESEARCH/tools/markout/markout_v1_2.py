"""markout_v1_2.py: markout_v1_1.py with the grader found beside it. Owner STRATEGY. New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only").
Old file: markout_v1_1.py 3239e4685080894e, never edited. Changed, only where things are: the grader's folders are found from this file
(<team>/RESEARCH/tools/idea_to_grade and i2g_v3_3 beside its markout folder, no longer one machine's path) and its engine is
i2g_engine_rel1 (the same functions: prices, fill, known end, exit walk); every gate, value, refusal and output is markout_v1_1.py's
(RECEIPT.json keeps tool 'markout_v1_1', the format; its tool_sha16 is this file's). A run of the rel1 chain (pins
I2G_PINS_V3_2_S6_REL1.json) is graded as an S6 run, as before. The rest of this text is markout_v1_1.py's.
markout_v1_1.py (STRATEGY, 29 Oct 2026; v1_1 = v1 + runs made by plain idea_to_grade V3.2: gate A grades the saved values with
the run's OWN grade function (i2g_grade3_v3_2 when the run's pins are I2G_PINS_V3_2.json; the V3.4 vector path when they are a speed
twin S3..S6), and gate A2 checks the V3.4 path (= V3.2.1, used for every wait) against the run's table on every row V3.2.1's NO_COST
fix cannot touch (all but the RR net rows). Everything else is markout_v1's.
markout_v1.py (STRATEGY, 29 Oct 2026; home team/RESEARCH/tools/markout; TEST, NOT REVIEWED): the MARKOUT CURVE of a graded alarm
from LATER ENTRIES. It takes one idea_to_grade V3.2 run (the grader: every fire, its matched calm moments, its same-move moments, the
frozen wave weights, the code it ran with) and measures every saved moment again with the entry at  alarm + WAIT + the run's execution
delay (2 s), with the grader's OWN functions (prices i2g_engine.CoinPrices, the BED taker fill fill_v2, i2g_rules_fast_v3.path_values_walk:
the returns at 10 s .. 4 h and the fixed exit grid, taker and resting), then grades each wait with the grader's OWN table code (V3.4's
vector path, as the run did). Fires and their baselines are shifted by the same wait, so every edge stays like for like.
Gates (the tool stops before any table if one fails):
  A  the run's saved values (measurements/VALUES3.npy) re-graded from the rebuilt inputs give the run's grade3/TABLE.tsv, text-equal;
  B  at wait 0 the re-measured values equal the saved values bit for bit (NaN where NaN).
Refusals: every file of the run's code (RUN.json code_sha16) must still have its sha16; the run's research window must end on or before
settings allowed_last (Mar-May 2026 never); waits in [0, max_wait_s]; at most max_workers processes.
  python3 markout_v1.py run --run GRADER_RUN_DIR --settings settings/SETTINGS_V1.json --out NEW_DIR [--waits 0,60,...] [--workers 3]
                            [--split-day 20251101] [--coins A,B (tests)]
Writes NEW_DIR: GATES.json, TABLE_W<wait>.tsv (the grader's table at that wait), HALVES_W<wait>.tsv (the same per half when
--split-day), CURVE.tsv (returns at the six horizons, TT, every cost, PARENT / CALM_EDGE / TOUGH_EDGE, every wait, slice and half),
VALUES3_W<wait>.npy (per observation row, in the run's OBSERVATIONS order: reusable for bins of a metric), RECEIPT.json.
Exit 0 done; 2 REFUSED <CODE>; 4 a gate failed (GATES.json says which)."""
import argparse, csv, datetime as dt, hashlib, json, os, sys, time
import numpy as np

csv.field_size_limit(10 ** 9)
US = 1_000_000
TOOLS = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))   # <team>/RESEARCH/tools: this file is in tools/markout
I2G = TOOLS + '/idea_to_grade'
V34 = TOOLS + '/i2g_v3_3'
DIRECTIONS = ('FOLLOW', 'FADE')
HORIZON_MEASURES = ('ret_10s', 'ret_1m', 'ret_5m', 'ret_15m', 'ret_1h', 'ret_4h')
CURVE_STATS = ('PARENT', 'CALM_EDGE', 'TOUGH_EDGE')
NEED_SETTINGS = ('waits_s', 'max_wait_s', 'max_workers', 'allowed_last', 'split_day')


class Refused(Exception):
    def __init__(self, code, why=''):
        Exception.__init__(self, '%s: %s' % (code, why)); self.code = code


def sha16(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def read_tsv(path):
    with open(path) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def day_of_us(t_us):
    return dt.datetime.fromtimestamp(int(t_us) // US, dt.timezone.utc).strftime('%Y%m%d')


def default_parent_id(coin, t, side):
    """i2g_rules_v1_2.parent_id's text: coin, second, signed side"""
    return '%s_%d_%+d' % (coin, int(t), int(side))


# ------------------------------------------------------------------------------------------------ 1 checks
def check_code(code_sha16, sha=sha16):
    """every file the run's code list names must still have its sha16 -> [] or the changed / missing files"""
    bad = []
    for p, h in sorted(code_sha16.items()):
        if not os.path.isfile(p):
            bad.append('%s MISSING' % p)
        elif sha(p) != h:
            bad.append('%s %s now %s' % (p, h, sha(p)))
    return bad


def parse_waits(text, max_wait_s):
    try:
        w = [int(x) for x in str(text).split(',') if x.strip() != '']
    except ValueError:
        raise Refused('BAD_WAITS', text)
    if not w or len(set(w)) != len(w) or any(x < 0 or x > max_wait_s for x in w):
        raise Refused('BAD_WAITS', '%s (each in 0..%d, no repeats)' % (text, max_wait_s))
    return sorted(w)


# ------------------------------------------------------------------------------------------------ 2 the grader's inputs, rebuilt from files
def rebuild_inputs(run, parent_id=default_parent_id, ms_us=None):
    """the grade3 inputs of idea_to_grade_v3_2.aggregate (V3 identity, as-of eligibility), from the run's saved files:
    parents (sorted by clock, coin, side), row_ids, calm / calm_v2 [(row, weight)], tough [row], weights, clusters, row_coin, and the
    observation rows themselves. ms_us: i2g_engine.ms_us (the matcher's control clock in us)."""
    if ms_us is None:                     # i2g_engine.ms_us's rule: the draw time rounded to the millisecond, in us
        ms_us = lambda x: (lambda a, b: int(a) * US + int(b) * 1000)(*format(float(x), '.3f').split('.'))
    obs = []
    for r in read_tsv(os.path.join(run, 'measurements', 'OBSERVATIONS.tsv')):
        obs.append((int(r['row']), r['kind'], r['coin'], int(r['as_of_us']), int(r['side']), r['direction']))
    if [o[0] for o in obs] != list(range(len(obs))):
        raise Refused('OBSERVATION_ORDER', 'rows are not 0 .. n-1 in order')
    key = {(k, c, t, s, d): i for i, k, c, t, s, d in obs}
    if len(key) != len(obs):
        raise Refused('OBSERVATION_DUPLICATE', run)
    ident = sorted({(t, c, s) for _, k, c, t, s, _ in obs if k == 'parent'})
    W = {r['parent_id']: r for r in read_tsv(os.path.join(run, 'grade3', 'WEIGHTS.tsv'))}
    edges = {}
    for e in read_tsv(os.path.join(run, 'matches', 'EDGES.tsv')):
        edges.setdefault(e['fid'], []).append(e)
    tough = {}
    for g in read_tsv(os.path.join(run, 'matches', 'TOUGH.tsv')):
        tough.setdefault(g['parent_id'], []).append(int(g['tough_t']))
    parents, weights, clusters = [], [], []
    calm = {d: [] for d in DIRECTIONS}; calm_v2 = {d: [] for d in DIRECTIONS}; trows = {d: [] for d in DIRECTIONS}
    for t, c, s in ident:
        pid = parent_id(c, t // US, s)
        if pid not in W:
            raise Refused('NO_WEIGHT', pid)
        try:
            p = {'id': pid, 'coin': c, 'as_of_us': t, 'side': s, 'day': day_of_us(t), 'row_ids': {d: key[('parent', c, t, s, d)] for d in DIRECTIONS}}
        except KeyError as x:
            raise Refused('NO_PARENT_ROW', '%s %s' % (pid, x))
        parents.append(p); weights.append(float(W[pid]['weight'])); clusters.append(W[pid]['cluster_id'])
        for d in DIRECTIONS:
            calm[d].append([]); calm_v2[d].append([]); trows[d].append([])
        for e in edges.get(pid, []):
            if e['own_v2'] == '' or e['asof'] == '':
                ct = ms_us(e['cand_t'])
                for d in DIRECTIONS:
                    q = key.get(('control', c, ct, s, d))
                    if q is None:
                        raise Refused('NO_CONTROL_ROW', '%s %s' % (pid, e['cand_t']))
                    if e['own'] == '':
                        calm[d][-1].append((q, float(e['weight'])))
                    if e['own_v2'] == '':
                        calm_v2[d][-1].append((q, float(e['weight'])))
        for g in tough.get(pid, []):
            for d in DIRECTIONS:
                q = key.get(('tough', c, g * US, s, d))
                if q is None:
                    raise Refused('NO_TOUGH_ROW', '%s %d' % (pid, g))
                trows[d][-1].append(q)
    return dict(obs=obs, parents=parents, weights=weights, clusters=clusters, calm=calm, calm_v2=calm_v2, tough=trows,
                row_coin=[o[2] for o in obs])


# ------------------------------------------------------------------------------------------------ 3 the measurement schedule
def measure_rows(rows, waits, delay_s, measure, n3, m15):
    """rows: [(row, kind, t_us, side, direction)] of ONE coin; measure(t_clock_us, t_dec_us, traded) -> (V3 row, unsigned 15 min move),
    with t_clock = the moment + wait (the decision) and t_dec = t_clock + the execution delay. As the grader's fill_rows: one measurement
    per (clock, traded side), the traded side flipped for FADE, move15 signed by each row's own parent side.
    -> {wait: (row ids, values array len(rows) x n3)}"""
    out = {}
    ids = np.asarray([r[0] for r in rows], np.int64)
    for w in waits:
        V = np.full((len(rows), n3), np.nan); memo = {}
        for i, (row, kind, t_us, side, d) in enumerate(rows):
            traded = -side if d == 'FADE' else side
            eff = (t_us, traded)
            if eff not in memo:
                t_clock = t_us + int(w) * US
                memo[eff] = measure(t_clock, t_clock + int(round(float(delay_s) * US)), traded)
            row3, mv0 = memo[eff]
            V[i] = row3; V[i, m15] = side * mv0
        out[w] = (ids, V)
    return out


def coin_task(task):
    """one coin, every wait: the grader's own price view, taker fill, known end and path walk (i2g_engine_v3_2_s6.coin_job's measure)"""
    for p in (I2G,):
        if p not in sys.path:
            sys.path.insert(0, p)
    import i2g_engine_rel1 as E2
    import i2g_rules_v1_2 as RU
    import i2g_rules_fast_v3 as RF
    k = E2.K.load()
    names3 = RU.value_names(); n3 = len(names3); m15 = names3.index('move15_pct')
    prices = E2.CoinPrices(task['lab_root'], task['coin'], tuple(task['window']))
    by_day = {}
    for r in task['rows']:
        by_day.setdefault(E2.day_of(r[2] // US), []).append(r)
    res = {w: ([], []) for w in task['waits']}
    for day in sorted(by_day):
        pv, loaded = prices.view(day); tes = pv.te / 1e6

        def measure(t_clock, t_dec, traded, pv=pv, loaded=loaded, tes=tes):
            mv, rv = RU.asof_features(tes, pv.px, [t_clock / US])
            f = k.FV.fill(pv, t_dec, traded, 'taker')
            taker = (f.status, getattr(f, 'i', None), getattr(f, 't_us', None), getattr(f, 'px', None))
            kend = RU.known_end_us(loaded, (f.t_us if f.status == 'FILLED' else t_dec), E2.day_of, E2.shift, k.D._day_start)
            row3 = RF.path_values_walk(pv.tl, pv.px, pv.hi, pv.lo, taker, t_dec, traded, kend, np.nan, float(rv[0]), task['c_pct'])
            return row3, float(mv[0])
        got = measure_rows(by_day[day], task['waits'], task['delay_s'], measure, n3, m15)
        for w, (ids, V) in got.items():
            res[w][0].append(ids); res[w][1].append(V)
    prices.recheck()
    return {'coin': task['coin'], 'res': {w: (np.concatenate(a), np.concatenate(b)) for w, (a, b) in res.items()}, 'reads': prices.reads}


# ------------------------------------------------------------------------------------------------ 4 gates
def values_diff(a, b):
    """cells where a and b differ: NaN pattern or bits of the finite values"""
    a = np.asarray(a, float); b = np.asarray(b, float)
    if a.shape != b.shape:
        return -1
    na, nb = np.isnan(a), np.isnan(b)
    same = (na == nb) & (na | (a.view(np.uint64) == b.view(np.uint64)))
    return int((~same).sum())


def table_text(rows, fmt):
    return ['\t'.join(fmt(x) for x in r) for r in rows]


def table_diff(lines, path):
    with open(path) as f:
        have = [l.rstrip('\n') for l in f][1:]
    if len(have) != len(lines):
        return abs(len(have) - len(lines)) + sum(1 for a, b in zip(have, lines) if a != b)
    return sum(1 for a, b in zip(have, lines) if a != b)


# ------------------------------------------------------------------------------------------------ 5 the curve
def curve_rows(wait, part, rows):
    """the markout rows of one table: the six horizon returns, TT, every cost, PARENT / CALM_EDGE / TOUGH_EDGE"""
    out = []
    for r in rows:
        sl, d, meas, sch, cost, st = r[:6]
        if meas in HORIZON_MEASURES and sch == 'TT' and st in CURVE_STATS:
            out.append((wait, part, sl) + tuple(r[1:]))
    return out


# ------------------------------------------------------------------------------------------------ 6 run
def grader(inp, names3, legs):
    """the run's own grade3 path (idea_to_grade_v3_2_s3.grade_v34): V3.4 Step A once per value set, Step B for any grouping"""
    if V34 not in sys.path:
        sys.path.append(V34)
    import i2g_v3_4_vectors as VA
    import i2g_v3_4_grade as GB

    def grade(V3, gid=None, n_groups=1, slices=None):
        A = VA.parent_vectors(inp['parents'], names3, V3, inp['row_coin'], inp['calm'], inp['calm_v2'], inp['tough'], legs)
        g = np.zeros(len(inp['parents']), np.int64) if gid is None else np.asarray(gid, np.int64)
        return GB.grade_groups(A, g, n_groups, [p['day'] for p in inp['parents']], inp['weights'], inp['clusters'], slices)
    return grade


def grade_kind(R):
    """'v34' when the run's grade3 came from V3.4's vector path (the speed twins S3..S6 pins), 'v32' for plain V3.2 pins"""
    name = os.path.basename(R.get('pins_file', {}).get('path', ''))
    return 'v34' if any(x in name for x in ('_S3', '_S4', '_S5', '_S6')) else 'v32'


def table_diff_except(lines, path, skip):
    """(rows differing outside skip, rows differing inside skip); skip(fields) -> True for a row V3.2.1's fix may change"""
    with open(path) as f:
        have = [l.rstrip('\n') for l in f][1:]
    if len(have) != len(lines):
        return abs(len(have) - len(lines)) + 1, 0
    out = inside = 0
    for a, b in zip(have, lines):
        if a != b:
            if skip(a.split('\t')):
                inside += 1
            else:
                out += 1
    return out, inside


def run(a):
    t0 = time.time()
    if os.path.exists(a.out):
        raise Refused('OUT_EXISTS', a.out)
    S = json.load(open(a.settings)); miss = [k for k in NEED_SETTINGS if k not in S]
    if miss:
        raise Refused('BAD_SETTINGS', ','.join(miss))
    waits = parse_waits(a.waits if a.waits else ','.join(str(x) for x in S['waits_s']), int(S['max_wait_s']))
    workers = int(a.workers or S['max_workers'])
    if workers < 1 or workers > int(S['max_workers']):
        raise Refused('BAD_WORKERS', '%d (1..%d)' % (workers, S['max_workers']))
    need = ['RUN.json', 'measurements/OBSERVATIONS.tsv', 'measurements/VALUES3.npy', 'measurements/NAMES3.json', 'matches/EDGES.tsv',
            'matches/TOUGH.tsv', 'grade3/WEIGHTS.tsv', 'grade3/TABLE.tsv']
    lost = [n for n in need if not os.path.isfile(os.path.join(a.run, n))]
    if lost:
        raise Refused('RUN_INCOMPLETE', ','.join(lost))
    R = json.load(open(os.path.join(a.run, 'RUN.json')))
    win = R['selection']['research_window']
    if win[1] > S['allowed_last']:
        raise Refused('WINDOW_NOT_ALLOWED', 'run window %s..%s, allowed to %s' % (win[0], win[1], S['allowed_last']))
    bad = check_code(R['code_sha16'])
    if bad:
        raise Refused('CODE_CHANGED', '%d files, first %s' % (len(bad), bad[0]))
    cs = R['settings']['costs']
    if sha16(cs['path']) != cs['sha16']:
        raise Refused('COSTS_CHANGED', cs['path'])
    delay_s = float(R['settings']['measure']['execution_delay_s'])
    if I2G not in sys.path:
        sys.path.insert(0, I2G)
    import i2g_engine_rel1 as E2
    import i2g_rules_v1_2 as RU
    names3 = RU.value_names()
    if names3 != json.load(open(os.path.join(a.run, 'measurements', 'NAMES3.json'))):
        raise Refused('NAMES3_CHANGED', a.run)
    inp = rebuild_inputs(a.run, RU.parent_id, E2.ms_us)
    coins = list(R['selection']['coins'])
    costs = RU.read_costs(cs['path'])
    cost_bp = {c: (costs[c][0] if c in costs else float('nan')) for c in coins}    # idea_to_grade_v3_2.cost_split
    legs = {cn: {c: RU.cost_legs(cost_bp[c], gap, cs['maker_fee_bp']) for c in coins} for cn, gap in cs['gaps_pct'].items()}
    c_pct = {c: RU.coin_cost_pct(cost_bp[c], cs['gaps_pct']['HONEST']) for c in coins}
    grade = grader(inp, names3, legs)
    import i2g_grade3_v3_2_1 as G3
    os.makedirs(a.out)
    gates = {}
    # gate A: the saved values give the run's table
    V0 = np.load(os.path.join(a.run, 'measurements', 'VALUES3.npy'))
    kind = grade_kind(R); TAB = os.path.join(a.run, 'grade3', 'TABLE.tsv')
    if kind == 'v34':
        tA = table_text(grade(V0)[0], G3.fmt); dA = table_diff(tA, TAB)
        gates['A_regrade_saved_values'] = dict(rows=len(tA), differing=dA, ok=dA == 0, grade='V3.4 path (the run\'s own)')
    else:
        import i2g_grade3_v3_2 as G32
        rA = G32.grade(inp['parents'], names3, V0, inp['row_coin'], inp['calm'], inp['calm_v2'], inp['tough'], inp['weights'], inp['clusters'], legs)
        tA = table_text(rA, G3.fmt); dA = table_diff(tA, TAB)
        gates['A_regrade_saved_values'] = dict(rows=len(tA), differing=dA, ok=dA == 0, grade='i2g_grade3_v3_2 (the run\'s own)')
        t2 = table_text(grade(V0)[0], G3.fmt)
        d2, d2rr = table_diff_except(t2, TAB, lambda f: len(f) > 4 and f[3] == 'RR' and f[4] != 'GROSS')
        gates['A2_v34_path_equals_run_outside_RR_net'] = dict(rows=len(t2), differing=d2, rr_net_rows_differing=d2rr, ok=d2 == 0)
        dA = dA + d2
    if dA:
        json.dump(gates, open(os.path.join(a.out, 'GATES.json'), 'w'), indent=1); return 4, gates
    # measure every wait
    sel = set(a.coins.split(',')) if a.coins else None
    tasks = []
    for c in coins:
        rows = [(i, k, t, s, d) for i, k, cc, t, s, d in inp['obs'] if cc == c]
        if rows and (sel is None or c in sel):
            tasks.append(dict(coin=c, rows=rows, waits=waits, delay_s=delay_s, lab_root=R['sources']['lab_root'], window=win, c_pct=c_pct[c]))
    n3 = len(names3); Vw = {w: np.full((len(inp['obs']), n3), np.nan) for w in waits}; done = np.zeros(len(inp['obs']), bool); reads = 0
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('spawn')) as pool:
        for r in pool.map(coin_task, sorted(tasks, key=lambda t: -len(t['rows']))):
            reads += r['reads']
            for w, (ids, V) in r['res'].items():
                Vw[w][ids] = V
                done[ids] = True
    measured = int(done.sum())
    if sel is None and measured != len(inp['obs']):
        raise Refused('OBSERVATION_COUNT', '%d of %d rows measured' % (measured, len(inp['obs'])))
    # gate B: wait 0 equals the saved values
    if 0 in waits:
        m = done
        dB = values_diff(Vw[0][m], V0[m])
        gates['B_wait0_equals_saved'] = dict(rows=int(m.sum()), cells=int(m.sum()) * n3, differing=dB, ok=dB == 0)
        if dB:
            json.dump(gates, open(os.path.join(a.out, 'GATES.json'), 'w'), indent=1)
            np.save(os.path.join(a.out, 'VALUES3_W0_FAILED.npy'), Vw[0]); return 4, gates
    else:
        gates['B_wait0_equals_saved'] = dict(ok=None, why='wait 0 not asked')
    json.dump(gates, open(os.path.join(a.out, 'GATES.json'), 'w'), indent=1)
    # tables
    split = a.split_day or S['split_day']
    half = [0 if p['day'] < split else 1 for p in inp['parents']] if split else None
    head = '\t'.join(G3.COLS) + '\n'; curve = []
    for w in waits:
        rows = grade(Vw[w])[0]
        with open(os.path.join(a.out, 'TABLE_W%d.tsv' % w), 'x') as f:
            f.write(head + '\n'.join(table_text(rows, G3.fmt)) + '\n')
        curve += curve_rows(w, 'ALL', rows)
        if half is not None:
            hs = grade(Vw[w], half, 2, slices=('ALL',))
            with open(os.path.join(a.out, 'HALVES_W%d.tsv' % w), 'x') as f:
                f.write('half\t' + head)
                for h, rr in enumerate(hs):
                    for line in table_text(rr, G3.fmt):
                        f.write('H%d\t%s\n' % (h + 1, line))
            for h, rr in enumerate(hs):
                curve += curve_rows(w, 'H%d' % (h + 1), rr)
        np.save(os.path.join(a.out, 'VALUES3_W%d.npy' % w), Vw[w])
    with open(os.path.join(a.out, 'CURVE.tsv'), 'x') as f:
        f.write('wait_s\tpart\tslice\tdirection\tmeasure\tscheme\tcost\tstat\tmean\tlo\thi\tparents\tclusters\n')
        for r in curve:
            f.write('\t'.join(G3.fmt(x) for x in r) + '\n')
    rec = dict(tool='markout_v1_1', grade_kind=grade_kind(R), tool_sha16=sha16(os.path.abspath(__file__)), settings=a.settings, settings_sha16=sha16(a.settings),
               run=a.run, run_id=R.get('run_id'), run_window=win, delay_s=delay_s, waits_s=waits, split_day=split, coins=len(tasks),
               observations=len(inp['obs']), measured=measured, parents=len(inp['parents']), price_reads=reads, gates=gates,
               code_checked=len(R['code_sha16']), seconds=round(time.time() - t0, 1),
               note='a moment and its baselines are all measured from moment + wait + the run delay; the as-of 5 min volatility of the exit '
                    'grid is read at moment + wait (known at the decision); everything else is the grader\'s code unchanged')
    json.dump(rec, open(os.path.join(a.out, 'RECEIPT.json'), 'w'), indent=1)
    return 0, gates


def main(argv):
    p = argparse.ArgumentParser(); p.add_argument('cmd', choices=['run'])
    p.add_argument('--run', required=True); p.add_argument('--settings', required=True); p.add_argument('--out', required=True)
    p.add_argument('--waits', default=''); p.add_argument('--workers', type=int, default=0); p.add_argument('--split-day', default='')
    p.add_argument('--coins', default='')
    a = p.parse_args(argv)
    try:
        rc, gates = run(a)
    except Refused as e:
        print('REFUSED %s' % e); return 2
    print('%s gates %s -> %s' % ('DONE' if rc == 0 else 'GATE FAILED', json.dumps(gates), a.out)); return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
