"""i2g_grade.py (i2g_grader for STRATEGY/LEAD, 25 Oct 2026): GRADING of idea_to_grade: the outside grading report's semantics, imported.
For each cohort (direction FOLLOW / FADE x offer 0.2 .. 2.0 pct x horizon 15, 30, 60, 120, 240 min = 190 cohorts) and each month slice (ALL and
every calendar month of the parents):
  - the stamps (reach within H, heat before the offer) from alarm_stamp.stamps, on the 55 STAMP fields of every observation;
  - the summary from the outside chain's comparison kernel, imported unchanged (OUTSIDE DEV2 .../performance/fast_compare.Prepared over
    DEV1/opportunity_compare_v1/compare.py): STANDALONE (every parent, frozen global wave weights: each wave counts once), PAIRED (parents
    with a known reach whose every eligible control is known) against their matched controls (inherited parent mass x normalized edge
    weight), reach probability, reach gap, exact weighted quantiles (0.5, 0.75, 0.9) of heat-before-offer (hb), seconds to the offer
    (offer_s) and seconds from the alarm to the offer (alarm_offer_s), coverage and unknown masses. It describes OPPORTUNITY, never profit.
The per-parent detail (status, parent reach, control reach, paired gap) of the ALL slice is kept as arrays (the month slices hold the same
per-parent values); the long per-cohort lists of the outside JSON (parent rows, ids, masses) are not repeated 1,330 times.
Workers keep one prepared comparison per (direction, month) for the life of the process (the outside batch_grade did the same per batch)."""
import importlib.util, json, math, os, sys, time
sys.dont_write_bytecode = True
import numpy as np

DEV = '<LAB_REPO>/forensics/team/OUTSIDE/COORD/development'
FAST = DEV + '/DEV2/a02p_chain_v1/full_population/performance/fast_compare.py'
REF = DEV + '/DEV1/opportunity_compare_v1/compare.py'
PINS = {FAST: 'eec15093614540d5', REF: '594a7bc354a323b1'}
QUANTILES = (.5, .75, .9)
DETAIL_KEYS = ('parents',)                                   # dropped from the published per-slice summary (kept as arrays)


def _load(path, name):
    import i2g_engine as E
    return E.load_path(path, name)


class G:
    loaded = False

    @classmethod
    def load(cls):
        if not cls.loaded:
            import i2g_engine as E
            k = E.K.load()
            for p, want in PINS.items():
                if E.sha16(p) != want:
                    raise ValueError('KERNEL_DRIFT %s' % p)
            cls.F = _load(FAST, 'i2g_fast_compare'); cls.ref = _load(REF, 'i2g_existing_full_compare'); cls.S = k.S
            cls.prepared = {}; cls.inputs = None; cls.matrix = None
            cls.loaded = True
        return cls


def _prepared(inputs, direction):
    """[(month, parent index array, edge index array, fast_compare.Prepared)] for one direction, built once per process"""
    g = G.load(); key = (inputs['run_key'], direction)
    if key not in g.prepared:
        d = inputs['directions'][direction]; out = []
        n = len(inputs['pids'])
        for month, pi in inputs['month_ix']:
            pi = np.asarray(pi, np.int64); sel = np.zeros(n, bool); sel[pi] = True
            ei = np.flatnonzero(sel[d['edge_parent']])
            ids = [inputs['pids'][i] for i in pi]; ep = [inputs['pids'][i] for i in d['edge_parent'][ei]]
            ci = [d['control_ids'][i] for i in ei]
            out.append((month, pi, ei, g.F.Prepared(ids, inputs['waves'], ep, ci, d['weights'][ei], g.ref)))
        g.prepared = {k: v for k, v in g.prepared.items() if k[0] == inputs['run_key']}
        g.prepared[key] = out
    return g.prepared[key]


def grade_task(task):
    """task: inputs_path (pickle written by the orchestrator), values_path (VALUES.npy), direction, horizon, offers
    -> {'cohorts': [{direction, offer_pct, horizon_min, profiles: [{month, summary}]}], 'audit': {cohort name: arrays}, timings}"""
    import pickle
    t0 = time.perf_counter(); g = G.load()
    if g.inputs is None or g.inputs['run_key'] != task['run_key']:
        with open(task['inputs_path'], 'rb') as f:
            g.inputs = pickle.load(f)
        g.matrix = np.load(task['values_path'], mmap_mode='r')
    inputs = g.inputs; direction = task['direction']; horizon = task['horizon']; offers = task['offers']
    d = inputs['directions'][direction]
    a = np.asarray(g.matrix[d['ids']], dtype='<f8'); names = inputs['names']
    x = {nm: a[:, i] for i, nm in enumerate(names)}; x['coin'] = d['coins']
    t1 = time.perf_counter()
    prepared = _prepared(inputs, direction)
    t2 = time.perf_counter()
    stamps = g.S.stamps(x, offers=offers, horizons=[horizon])
    delay = d['delay']
    out = []; audit = {}
    for offer in offers:
        name = '%s_%02d_%03d' % (direction, round(offer * 10), horizon)
        reach = stamps['reach_%g_%dm' % (offer, horizon)]; hb = stamps['hb_%g_%dm' % (offer, horizon)]
        offer_s = np.where(reach == 1, x['ot_%02d' % round(offer * 10)], np.nan); alarm_s = offer_s + delay + x['fill_wait_s']
        profiles = []
        for month, pi, ei, prep in prepared:
            pr = d['parents'][pi]; ci = d['controls'][ei]
            summary = prep.summarize(reach[pr], {'hb': hb[pr], 'offer_s': offer_s[pr], 'alarm_offer_s': alarm_s[pr]}, reach[ci],
                                     {'hb': hb[ci], 'offer_s': offer_s[ci], 'alarm_offer_s': alarm_s[ci]}, quantiles=QUANTILES, detail=False)
            profiles.append({'month': month, 'direction': direction, 'offer_pct': offer, 'horizon_min': horizon, 'summary': summary})
            if month == 'ALL':
                la = prep.last_audit
                kk = np.packbits(np.isfinite(np.asarray(reach[ci], float))).tobytes()
                audit[name] = {'status': np.asarray(la['status'], 'u1'), 'parent_reach': np.asarray(la['parent_reach'], float),
                               'control_reach': np.asarray(la['control_reach'], float), 'paired_reach_gap': np.asarray(la['paired_reach_gap'], float),
                               'unknown_eligible_mass': np.asarray(prep.known_cache[kk][1], float)}
            # retain only the last exact mask preparation (outside batch_grade's rule): different masks are never conflated
            cur = bytes.fromhex(prep.last_audit['paired_membership_key']); prep.paired_cache = {cur: prep.paired_cache[cur]}
            if len(prep.known_cache) > 1:
                last = next(reversed(prep.known_cache)); prep.known_cache = {last: prep.known_cache[last]}
        out.append({'name': name, 'direction': direction, 'offer_pct': offer, 'horizon_min': horizon, 'profiles': profiles})
    t3 = time.perf_counter()
    import resource
    import i2g_engine as E
    return {'cohorts': out, 'audit': audit, 'pid': os.getpid(), 'ru_maxrss': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'modules': E.process_modules(),
            'seconds': {'load': t1 - t0, 'prepare': t2 - t1, 'summaries': t3 - t2, 'total': t3 - t0}}


def static_parent_detail(inputs, direction):
    """the cohort-independent per-parent columns of the outside detail rows: eligible edges, eligible mass (ALL slice)"""
    d = inputs['directions'][direction]; n = len(inputs['pids'])
    counts = np.bincount(d['edge_parent'], minlength=n)
    mass = np.zeros(n)
    groups = [[] for _ in range(n)]
    for j, i in enumerate(d['edge_parent']):
        groups[i].append(float(d['weights'][j]))
    for i, g in enumerate(groups):
        mass[i] = math.fsum(g)
    return counts, mass
