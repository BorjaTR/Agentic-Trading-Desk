"""run_parallel_rel1.py: new edition by SCOUT K12 for the clean release (31 Oct 2026; TEST, NOT REVIEWED). Old file: run_parallel.py
c48230fb71f55090, never edited. Changed, nothing else: the Outcomes workers run event_outcomes/event_outcomes_rel1.py (EO); the gate
run_lab waits on (Profile, Context) is the environment FEED_GATE (feed_gate_wait: it must be set, unset is refused NO_FEED_GATE; empty =
no gate), never labcore.jobgate's built-in dev-tree GATE. The rest of this text is run_parallel.py's.
run_parallel.py: run Profile (event_profile), Context (alarm_context ed2), Outcomes (event_outcomes) or Cause (event_cause) over a date
range in N processes at once (each at ABSOLUTE nice 10, one numeric thread), then check the WHOLE run before anyone can read it.
  python3 run_parallel.py <N> profile <lab_root> <lab3 code> <alarms.tsv> <settings.json> <SUBJECT> <first> <last> <out_root> [options]
  python3 run_parallel.py <N> context <lab_root> <lab3 code> <EVENTS.tsv> <SUBJECT> <LEVELS comma> <first> <last> <out_root> [options]
      [--decisions 0,15] [--history <alarm list tsv>]                       (context only: the child's decision minutes and history list)
  python3 run_parallel.py <N> cause <lab_root> <lab3 code> <events.tsv> <settings.json> <SUBJECT> <first> <last> <out_root> [event_cause options]
  python3 run_parallel.py <N> outcomes <lab_root> <lab3 code> <events.tsv> <settings.json> <SUBJECT> <first> <last> <out_root> [event_outcomes run options]
PROFILE AND CONTEXT (A46R REL-01, ctxprof_shared 25 Oct 2026: K2, K3, C1, C2, C5, C6):
  options  --select list | coin:X | coins:A,B | all | group:NAME | roster   (default list = every row of the list inside the dates)
           --group-file F      (for group:NAME: the shared resolver's dated JSON, or a tsv group/sector + coin)
           --resume            (finish a kept attempt of the SAME plan: its whole parts are kept, the rest is recomputed)
           --window FIRST..LAST (the caller's read window, e.g. the research months; first..last must lie inside it; passed to the tool:
                                Profile --window FIRST,LAST, Context --window FIRST..LAST)
  1 SELECTION (labcore.v2_7.selection, the one shared selector): every requested day must pass lab3/law.py; a coin must be in the canonical
    roster (membership, not syntax); a valid selection with no event is an explicit success (EMPTY_SELECTED_POPULATION) with its coverage.
    A filtered selection writes _selection/SELECTED_<list> (the list's '#' lines, header and the chosen rows byte-equal); Context then
    reads its alarm history from the whole list, so a history count never depends on the selection.
  2 PLAN: the tools' own preflights (Profile 'check', Context 'preflight' per level; no data value read, nothing written); every expected day-part with its coins and row count; the code, list and settings
    pins frozen before any worker starts; RUN_PLAN.json (no out_root, no time: the run identity).
  3 STAGE: <out_root>.pending_<pid>_<stamp> (labcore.v2_7.runs = event_decisions/run_manifest_candidate stage / commit / abort, imported, not
    copied). An existing complete out_root of the same plan is UP TO DATE (exit 0); any other existing out_root is refused.
  4 WORKERS: contiguous day chunks balanced by event count, levels x chunks for Context, at most N at once; the parent waits for each
    with wait4 (its exit status and its own peak memory). A failed worker stops the others; the stage is kept as <out_root>.failed_<stamp>
    with FAILED.json and NO manifest: an interrupted run never looks complete.
  5 CHECK (labcore.v2_7.runs.check_stage): every expected day-part whole, its coins and rows, one seal per part kind, every fixed source pin
    equal across parts and to the frozen pin, every lab index read unchanged on disk, no partial write; code, lists and settings
    unchanged since the plan. Log lines are never counted.
  6 COMMIT: RUN_MANIFEST.json last (requested and observed coverage, source states, pins, terminal exit status; time per phase and each
    process's own peak memory in 'telemetry', GB = 10^9 bytes). Consumers adopt only a committed run (labcore.v2_7.runs.adopt).
  Logs go to <out_root>.logs/<run id>/. Exit 0 = committed (or UP TO DATE); 2 = refused before work; 1 = failed, nothing published.
CAUSE (event_cause V3/V4, R07, cause_fixer): the parent PLANS (event_cause.py plan: the whole preflight, RUN_PLAN.json; a refusal stops here
with nothing computed), runs N shards (event_cause.py build ... --shard K/N), and only when every shard exited 0 runs event_cause.py
commit, which checks every planned day and event and the source vintages and then writes RUN_COMMIT.json. Unchanged by this version.
OUTCOMES (event_outcomes V3, outcomes_fixer's request 25 Oct): the public command delegates to `event_outcomes.py run <N> ...` (which
freezes, stages, checks and commits the whole run with RM.verify_committed); inside that run's stage (out_root = <root>.pending_<pid>_<stamp>
holding RUN_FROZEN.json) this branch is its worker launcher: contiguous day chunks balanced by events per day, at absolute nice 10. Completion is proven by event_outcomes'
verify_stage and commit, never by counting WRITTEN log lines."""
import csv, datetime as dt, json, os, re, resource, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.dirname(HERE)
EP = os.path.join(HERE, 'event_profile.py')
CTX = os.path.join(HERE, '..', 'alarm_context', 'alarm_context_ed2.py')   # edition 2 candidate; the released alarm_context.py stays pinned
EC = os.path.join(HERE, '..', 'event_cause', 'event_cause.py')
EO = os.path.join(HERE, '..', 'event_outcomes', 'event_outcomes_rel1.py')   # K12 rel1: the workers run the rel1 edition
PY = sys.executable
GB = 1e9
CODE = {'profile': {'code:event_profile.py': EP, 'code:clock_series.py': os.path.join(HERE, 'clock_series.py')},
        'context': {'code:alarm_context_ed2.py': CTX, 'code:context_blocks_ed2.py': os.path.join(HERE, '..', 'alarm_context', 'context_blocks_ed2.py'),
                    'code:alarm_view_v1.py': os.path.join(HERE, '..', 'alarms', 'alarm_view_v1.py')}}
LEVELS = ('EVENT', 'MARKET', 'COIN')
F = os.path.realpath(os.path.join(TOOLS, '..', '..', '..'))
SEARCH = {'profile': [HERE], 'context': [os.path.join(TOOLS, 'alarm_context')]}
SEARCH_ALL = [TOOLS, os.path.join(TOOLS, 'alarms'), os.path.join(F, 'team', 'LAB3', 'code', 'lab3'), os.path.join(F, 'team', 'LAB3'),
              os.path.join(F, 'team', 'LAB3', 'LAB4', 'proposals', 'metric_traps'), os.path.join(F, 'team', 'RESEARCH', 'LEAD', 'skills',
              'reading-metrics', 'scripts'), os.path.join(F, 'team', 'RESEARCH', 'QUANT', 'receipts')]


def recheck_pins(tool, fixed, files):
    """K5: every fixed source pin the parts name ('code:', 'law:', 'brief:', 'registry:', 'table:', lists, settings, catalog) against the
    file on disk now. files: {pin key: path} the run knows exactly (lists, settings, catalog); others are found by name in the tool's
    folder and the shared folders (the first that exists). -> (checked, changed [key], unresolved [key])"""
    checked, changed, unresolved = 0, [], []
    for k, v in sorted(fixed.items()):
        if k.startswith('lab:'):
            continue
        p = files.get(k)
        if p is None:
            rel = k.split(':', 1)[1]
            p = next((os.path.join(d, rel) for d in SEARCH[tool] + SEARCH_ALL if os.path.isfile(os.path.join(d, rel))), None)
        if p is None:
            unresolved.append(k); continue
        checked += 1
        if _sha16(p) != v:
            changed.append(k)
    return checked, changed, unresolved


def alarm_days(path, first, last):
    return sorted(alarm_day_counts(path, first, last))


def alarm_day_counts(path, first, last):
    """{UTC day: events of the list that day} for the days first..last"""
    out = {}
    with open(path) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            d = dt.datetime.fromtimestamp(int(float(r['t'])), dt.timezone.utc).strftime('%Y%m%d')
            if first <= d <= last:
                out[d] = out.get(d, 0) + 1
    return out


def chunks(days, n):
    k = max(1, -(-len(days) // n))
    return [days[i:i + k] for i in range(0, len(days), k)]


def balanced(days, weight, n):
    """contiguous chunks of days (in order) with about equal summed weight, at most n"""
    if not days:
        return []
    tot = float(sum(weight[d] for d in days)); out = [[]]; acc = 0.0
    for d in days:
        if out[-1] and acc >= tot * len(out) / n and len(out) < n:
            out.append([])
        out[-1].append(d); acc += weight[d]
    return out


def runs_of(days, done):
    """maximal runs of consecutive (in list order) days not yet done"""
    out, cur = [], []
    for d in days:
        if d in done:
            if cur:
                out.append(cur); cur = []
        else:
            cur.append(d)
    if cur:
        out.append(cur)
    return out


def nice10():
    """absolute nice 10 for a worker: never lower an inherited higher nice, never add 10 to it"""
    try:
        os.setpriority(os.PRIO_PROCESS, 0, max(10, os.getpriority(os.PRIO_PROCESS, 0)))
    except OSError:
        pass


def env1():
    return dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', VECLIB_MAXIMUM_THREADS='1',
                NUMEXPR_NUM_THREADS='1')


def maxrss_bytes(ru):
    return int(ru.ru_maxrss) * (1 if sys.platform == 'darwin' else 1024)


class Refusal(Exception):
    def __init__(self, code, msg):
        super().__init__('%s: %s' % (code, msg)); self.code = code


def feed_gate_wait(jobgate, log):
    """K12 rel1: run_lab's gate is the environment FEED_GATE (the settings key): it must be set (unset: refused NO_FEED_GATE, never the
    built-in team path of labcore.jobgate); empty = no gate; a gate file: labcore.jobgate.gate_wait(gate=FEED_GATE), as before"""
    if 'FEED_GATE' not in os.environ:
        raise Refusal('NO_FEED_GATE', 'set FEED_GATE to the feed stop gate file (the settings key FEED_GATE), or to empty for no gate')
    g = os.environ['FEED_GATE']
    return jobgate.gate_wait(gate=g, log=log) if g else 0


def _opts(a, allowed):
    """positional arguments and --options (a flag without a value: --resume)"""
    pos, opt = [], {}; i = 0
    while i < len(a):
        if a[i].startswith('--'):
            k = a[i][2:]
            if k not in allowed:
                raise Refusal('BAD_OPTION', '--%s (allowed: %s)' % (k, ', '.join('--' + x for x in sorted(allowed))))
            if allowed[k] is None:
                opt[k] = True; i += 1
            else:
                if i + 1 >= len(a):
                    raise Refusal('BAD_OPTION', '--%s needs a value' % k)
                opt[k] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    return pos, opt


def launch(cmds, n, logdir, env, tag, pidfile=None):
    """run the commands, at most n at once, each at absolute nice 10; wait4 gives each its exit status and own peak memory.
    -> [dict(cmd, rc, wall_s, peak_rss_gb, log)]; on the first failure the others are stopped and Refusal('WORKER_FAILED') raised"""
    pending = list(enumerate(cmds)); live = {}; done = []
    try:
        while pending or live:
            while pending and len(live) < n:
                k, c = pending.pop(0); lp = os.path.join(logdir, '%s_%d.log' % (tag, k)); lg = open(lp, 'w')
                p = subprocess.Popen(c, stdout=lg, stderr=subprocess.STDOUT, env=env, preexec_fn=nice10)
                live[p.pid] = (p, c, lg, lp, time.time())
                if pidfile:                                       # every worker pid of this attempt: a resume refuses while one lives
                    old = json.load(open(pidfile)) if os.path.isfile(pidfile) else []
                    tmp = pidfile + '.tmp'; open(tmp, 'w').write(json.dumps(old + [p.pid])); os.replace(tmp, pidfile)
            time.sleep(0.05)
            for pid in list(live):
                got, status, ru = os.wait4(pid, os.WNOHANG)
                if got == 0:
                    continue
                p, c, lg, lp, t0 = live.pop(pid); lg.close(); rc = os.waitstatus_to_exitcode(status); p.returncode = rc
                done.append(dict(cmd=c, rc=rc, wall_s=round(time.time() - t0, 3), peak_rss_gb=round(maxrss_bytes(ru) / GB, 4), log=lp))
                if rc != 0:
                    raise Refusal('WORKER_FAILED', 'rc %d: %s (log %s): %s' % (rc, ' '.join(c[2:4] + c[-4:]), lp,
                                                                              open(lp).read()[-400:].replace('\n', ' | ')))
    finally:
        for pid, (p, c, lg, lp, t0) in live.items():                       # stop the other chunks: no half-run is ever published
            try:
                p.terminate()
            except OSError:
                pass
        for pid, (p, c, lg, lp, t0) in list(live.items()):
            try:
                _, status, ru = os.wait4(pid, 0)
                done.append(dict(cmd=c, rc=os.waitstatus_to_exitcode(status), wall_s=round(time.time() - t0, 3),
                                 peak_rss_gb=round(maxrss_bytes(ru) / GB, 4), log=lp, stopped=True))
            except ChildProcessError:
                pass
            lg.close()
    return done


def fold_profile_reports(rdir, expect):
    """the Profile workers' run reports (--report, one per chunk, kept in <out_root>.logs/reports_<plan>/ across attempts) folded into the
    run's observed coverage: events and coins per day, never-read support days, and per series the points by state, the days not built
    or never read, the events with a (complete) window and the normal support (min, max). A day reported twice: the newest report.
    A report that contradicts the parts (events of a day) refuses; a day without a report is listed, never assumed."""
    days, rep_of = {}, {}
    files = sorted((os.path.getmtime(os.path.join(rdir, f)), f) for f in os.listdir(rdir) if f.endswith('.json')) if os.path.isdir(rdir) else []
    reps = {}
    for _, f in files:
        r = json.load(open(os.path.join(rdir, f))); reps[f] = r
        for d, x in (r.get('days') or {}).items():
            days[d] = x; rep_of[d] = f
    want = {d: x for (d, _), x in expect.items()}
    bad = [d for d in want if d in days and days[d].get('events') != want[d]['rows']]
    if bad:
        raise Refusal('REPORT_CONTRADICTS_PARTS', 'days %s: the worker report counts other events than the parts hold' % bad[:5])
    used = sorted(set(rep_of[d] for d in want if d in rep_of))
    series, sealed, outside = {}, {}, {}
    for f in used:
        r = reps[f]; sealed.update(r.get('sealed_support_days') or {}); outside.update(r.get('outside_window_support_days') or {})
        for code, x in (r.get('series') or {}).items():
            y = series.setdefault(code, dict(entity=x.get('entity'), clock=x.get('clock'), points={}, not_built_days=set(),
                                             never_read_days=set(), events_with_window=0, events_complete_window=0, normal_steps_min=None,
                                             normal_steps_max=None, normal_unavailable_events={}))
            for k, v in (x.get('points') or {}).items():
                y['points'][k] = y['points'].get(k, 0) + v
            y['not_built_days'].update(x.get('not_built_days') or []); y['never_read_days'].update(x.get('never_read_days') or [])
            y['events_with_window'] += x.get('events_with_window') or 0; y['events_complete_window'] += x.get('events_complete_window') or 0
            ns = x.get('normal_steps_observed')
            if ns:
                y['normal_steps_min'] = ns['min'] if y['normal_steps_min'] is None else min(y['normal_steps_min'], ns['min'])
                y['normal_steps_max'] = ns['max'] if y['normal_steps_max'] is None else max(y['normal_steps_max'], ns['max'])
            for k, v in (x.get('normal_unavailable_events') or {}).items():
                y['normal_unavailable_events'][k] = y['normal_unavailable_events'].get(k, 0) + v
    for y in series.values():
        y['not_built_days'] = sorted(y['not_built_days']); y['never_read_days'] = sorted(y['never_read_days'])
        y['points'] = dict(sorted(y['points'].items()))
    missing = sorted(d for d in want if d not in days)
    return dict(kind='profile run reports', complete=not missing, days_without_report=missing,
                events_reported=sum(days[d]['events'] for d in want if d in days), sealed_support_days=dict(sorted(sealed.items())),
                outside_window_support_days=dict(sorted(outside.items())), series=dict(sorted(series.items())))


def fold_context_receipts(stage, expect, rows=None, decisions=None, plans=None):
    """Context's per part-day coverage receipts (CTX_RECEIPTS_ED2/<part>/day=<D>.json, published with the run), checked against the run
    (context_fix2's request 1) and folded per part kind. Per expected part-day: the receipt exists and loads whole; its rows equal the
    part's rows; its keys_sha16 equals the keys this run selected (coin:as_of_us:known_at_us of every selected row x decision, computed
    here from the selection, not from Context); its seal_sha16 and sources_sha16 equal the part index's; its content_sha16 equals
    alarm_context_ed2.content_sha16 of the written part. Any difference refuses RECEIPT_CONTRADICTS_PARTS; a missing receipt refuses
    RECEIPT_MISSING. plans: the per-level preflight plans; for an unfiltered list their census keys_sha16 must equal the run's keys."""
    base = os.path.join(stage, 'CTX_RECEIPTS_ED2')
    if not os.path.isdir(base):
        if expect:
            raise Refusal('RECEIPT_MISSING', '%s: this Context version writes receipts, none found' % base)
        return dict(kind='context receipts', complete=True, by_part={})
    import importlib.util, numpy as np
    spec = importlib.util.spec_from_file_location('alarm_context_ed2_for_receipts', CTX); AC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(AC)
    want_keys = {}
    if rows is not None:
        dec = sorted(set(float(x) for x in (decisions or '0').split(',')))
        for _, _, coin, t, day in rows:
            a = int(np.round(np.float64(t) * 1e6))
            for dm in dec:
                want_keys.setdefault(day, []).append('%s:%d:%d' % (coin, a, int(np.round((np.float64(t) + dm * 60.0) * 1e6))))
    out, bad, missing = {}, [], []
    for (d, part), x in sorted(expect.items()):
        p = os.path.join(base, part, 'day=%s.json' % d)
        if not os.path.isfile(p):
            missing.append('%s %s' % (part, d)); continue
        r = json.load(open(p)); ix = json.load(open(os.path.join(stage, 'day=%s' % d, part, 'index.json')))
        why = []
        if r.get('rows') != x['rows'] or r.get('day') != d or r.get('part') != part:
            why.append('rows/day/part')
        if d in want_keys and r.get('keys_sha16') != AC.sha16_text('\n'.join(sorted(want_keys[d]))):
            why.append('keys')
        if r.get('seal_sha16') != AC.sha16_text(ix.get('seal') or ''):
            why.append('seal')
        if r.get('sources_sha16') != AC.sha16_text(json.dumps(ix.get('sources'), sort_keys=True)):
            why.append('sources')
        if r.get('content_sha16') != AC.content_sha16(stage, d, part):
            why.append('content')
        if why:
            bad.append('%s %s (%s)' % (part, d, ','.join(why))); continue
        y = out.setdefault(part, dict(day_parts=0, rows=0, cells=0, empty_cells=0, empty_reasons={}))
        y['day_parts'] += 1; y['rows'] += r['rows']; y['cells'] += r.get('cells', 0); y['empty_cells'] += r.get('empty_cells', 0)
        for k, v in (r.get('empty_reasons') or {}).items():
            y['empty_reasons'][k] = y['empty_reasons'].get(k, 0) + v
    if missing:
        raise Refusal('RECEIPT_MISSING', '%d part-days have no receipt, e.g. %s' % (len(missing), missing[:5]))
    if bad:
        raise Refusal('RECEIPT_CONTRADICTS_PARTS', '%s' % bad[:5])
    census = {}
    if plans:
        allk = AC.sha16_text('\n'.join(sorted(k for v in want_keys.values() for k in v))) if want_keys else None
        for lv, pl in sorted(plans.items()):
            cs = pl.get('census') or {}
            census[lv] = dict(run_id=pl.get('run_id'), rows=cs.get('rows'), keys_sha16=cs.get('keys_sha16'),
                              equals_run_keys=(cs.get('keys_sha16') == allk) if allk else None)
            if census[lv]['equals_run_keys'] is False:
                raise Refusal('RECEIPT_CONTRADICTS_PARTS', 'the %s preflight census keys %s are not the run keys %s' % (lv, cs.get('keys_sha16'), allk))
    for y in out.values():
        y['empty_reasons'] = dict(sorted(y['empty_reasons'].items()))
    return dict(kind='context receipts', complete=True, by_part=out, preflight_census=census)


def _sha16(p):
    from labcore.v2_7 import runs
    return runs.sha16_file(p)


def _wrapper_pin():
    """TESTS ONLY: RUN_PARALLEL_CHILD_WRAP names a fault-injection wrapper run in front of every Profile/Context worker; its sha16 enters
    the plan (a wrapped run is never the identity of a real one, never UP TO DATE for it) -> {path, sha16} or None"""
    w = os.environ.get('RUN_PARALLEL_CHILD_WRAP')
    return dict(path=os.path.abspath(w), sha16=_sha16(w)) if w else None


def plan_lab(tool, n, a):
    """PROFILE / CONTEXT: selection, preflight, expected parts and frozen pins -> (plan, context dict); nothing written"""
    sys.path.insert(0, TOOLS)
    from labcore.v2_7 import selection as S, runs
    if tool == 'profile':
        pos, opt = _opts(a, {'select': 1, 'group-file': 1, 'resume': None, 'verify': None, 'window': 1})
        if len(pos) != 8:
            raise Refusal('BAD_ARGUMENTS', __doc__)
        lab, code, lst, settings, subj, first, last, out = pos; levels = None; dec = None; hist = None
    else:
        pos, opt = _opts(a, {'select': 1, 'group-file': 1, 'resume': None, 'verify': None, 'decisions': 1, 'history': 1, 'window': 1})
        if len(pos) != 8:
            raise Refusal('BAD_ARGUMENTS', __doc__)
        lab, code, lst, subj, levels, first, last, out = pos; settings = None
        levels = levels.split(',')
        if not levels or any(lv not in LEVELS for lv in levels) or len(set(levels)) != len(levels):
            raise Refusal('BAD_LEVELS', '%s: a comma list of %s' % (','.join(levels), ', '.join(LEVELS)))
        dec = opt.get('decisions'); hist = opt.get('history')
        if dec is not None:
            try:
                dd = [float(x) for x in dec.split(',')]
            except ValueError:
                raise Refusal('BAD_DECISIONS', dec)
            if not dd or min(dd) < 0:
                raise Refusal('BAD_DECISIONS', dec)
    if not 1 <= n <= 8:
        raise Refusal('WORKERS', '1 to 8 workers (the team process budget), got %d' % n)
    if not re.fullmatch(r'[A-Z0-9_]+', subj or ''):
        raise Refusal('BAD_SUBJECT', '%r: capital letters, digits and _' % (subj,))
    for p in [lst, settings, hist, opt.get('group-file')]:
        if p is not None and not os.path.isfile(p):
            raise Refusal('MISSING_INPUT', p)
    win = None
    if opt.get('window'):
        m = re.fullmatch(r'(\d{8})\.\.(\d{8})', opt['window'])
        try:
            win = (m.group(1), m.group(2)) if m else None
            win = win if win and dt.datetime.strptime(win[0], '%Y%m%d') <= dt.datetime.strptime(win[1], '%Y%m%d') else None
        except ValueError:
            win = None
        if win is None:
            raise Refusal('BAD_WINDOW', '--window %r: FIRST..LAST, real UTC days, FIRST <= LAST' % opt['window'])
        if not (re.fullmatch(r'\d{8}', first or '') and re.fullmatch(r'\d{8}', last or '') and win[0] <= first <= last <= win[1]):
            raise Refusal('OUTSIDE_WINDOW', 'the requested %s..%s is not inside the caller window %s..%s' % (first, last, win[0], win[1]))
    T = {}; t0 = time.time()
    try:
        sel = S.select(lst, first, last, opt.get('select', 'list'), group_file=opt.get('group-file'), subject=subj, window=win)   # S3
    except S.SelectionRefused as e:
        raise Refusal('SELECTION_' + e.code, str(e))
    T['selection_s'] = time.time() - t0
    first, last = sel['request']['first'], sel['request']['last']
    filtered = sel['request']['kind'] != 'list'
    child_list_name = ('SELECTED_' + os.path.basename(lst)) if filtered else os.path.basename(lst)
    t0 = time.time()
    wtail = {'profile': ['--window', '%s,%s' % win] if win else [], 'context': ['--window', '%s..%s' % win] if win else []}[tool]
    plans = {}
    ctail = ([dec or '0'] + ([hist] if hist else [])) if tool == 'context' and (dec or hist) else []
    if sel['rows']:                                                  # the tools' own preflights: no data value read, nothing written
        if tool == 'profile':
            pcs = [[PY, '-B', EP, 'check', lst, settings, subj, first, last] + wtail]
        else:
            pcs = [[PY, '-B', CTX, 'preflight', lab, code, lst, subj, lv, first, last, os.path.abspath(out)] + ctail + wtail for lv in levels]
        ps = [subprocess.Popen(pc, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env1(), preexec_fn=nice10) for pc in pcs]
        for lv, p in zip(levels or ['profile'], ps):
            txt, err = p.communicate()
            if p.returncode != 0:
                raise Refusal('PREFLIGHT', (txt + err)[-800:])
            if tool == 'context':
                try:
                    plans[lv] = json.loads(txt)
                except ValueError:
                    raise Refusal('PREFLIGHT', 'the %s preflight printed no plan: %s' % (lv, txt[-300:]))
    T['preflight_s'] = time.time() - t0
    by_day = {}
    for _, _, c, _, d in sel['rows']:
        by_day.setdefault(d, []).append(c)
    ndec = len(set(float(x) for x in dec.split(','))) if dec else 1
    if tool == 'profile':
        expect = {(d, 'EPG.%s' % subj): {'coins': sorted(set(cs)), 'rows': len(cs)} for d, cs in by_day.items()}
    else:
        expect = {(d, 'CTX.%s.%s' % (subj, lv)): {'coins': sorted(set(cs)), 'rows': len(cs) * ndec} for d, cs in by_day.items() for lv in levels}
    lk = 'alarms:' if tool == 'profile' else 'events:'
    frozen_files = dict(CODE[tool]); frozen_files['list'] = lst
    if settings:
        frozen_files['settings:%s' % os.path.basename(settings)] = settings
    if hist:
        frozen_files['history:%s' % os.path.basename(hist)] = hist
    elif tool == 'context' and filtered:
        frozen_files['history:%s' % os.path.basename(lst)] = lst          # the whole list stays the alarm history
    from labcore.v2_7 import cache as K
    for nm, p in (('dispatcher', os.path.realpath(__file__)), ('labcore:runs.py', runs.__file__), ('labcore:selection.py', S.__file__),
                  ('labcore:cache.py', K.__file__), ('labcore:run_manifest_candidate.py', runs.RM_PATH),
                  ('labcore:population.py', S.RESOLVER_PATH), ('labcore:event_selection.py', S.EVSEL_PATH),
                  ('labcore:ROSTER_WEEK_ALIASES_V1.json', S.ALIASES), ('labcore:ROSTER_BUILD.json', S.ROSTER_DOC)):
        frozen_files[nm] = p
    frozen = {k: _sha16(p) for k, p in sorted(frozen_files.items())}
    part_pins = {k: v for k, v in frozen.items() if k != 'list' and k != 'dispatcher' and not k.startswith('labcore:')}
    sel_view = S.manifest_view(sel)
    plan = dict(schema='RUN_PLAN_V1', tool=tool, dispatcher=_sha16(os.path.realpath(__file__)),
                labcore={'runs.py': _sha16(runs.__file__), 'selection.py': _sha16(S.__file__)},
                args=dict(lab_root=os.path.abspath(lab), code_dir=os.path.abspath(code), list=os.path.abspath(lst),
                          settings=os.path.abspath(settings) if settings else None, subject=subj, levels=levels, decisions=dec,
                          history=os.path.abspath(hist) if hist else None, first=first, last=last, select=opt.get('select', 'list'),
                          group_file=os.path.abspath(opt['group-file']) if opt.get('group-file') else None, window=opt.get('window')),
                selection=sel_view, child_list=child_list_name, child_wrapper=_wrapper_pin(),
                expected=[[d, p, x['coins'], x['rows']] for (d, p), x in sorted(expect.items())],
                frozen=frozen, runtime=dict(python=sys.version.split()[0], interpreter=PY))
    ctx = dict(tool=tool, n=n, out=os.path.abspath(out), lab=lab, code=code, lst=lst, settings=settings, subj=subj, levels=levels,
               dec=dec, hist=hist, wtail=wtail, plans=plans, sel=sel, filtered=filtered, child_list_name=child_list_name, expect=expect, frozen_files=frozen_files,
               frozen=frozen, part_pins=part_pins, lk=lk, by_day=by_day, opt=opt, T=T)
    return plan, ctx


def run_lab(tool, n, a):
    t_start = time.time(); started = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    sys.path.insert(0, TOOLS)
    from labcore import jobgate
    from labcore.v2_7 import runs
    now = dt.datetime.now(dt.timezone.utc).time()
    if now >= dt.time(23, 30) or now < dt.time(0, 15):
        raise Refusal('QUIET_WINDOW', 'no numeric work 23:30-00:15 UTC')
    t0 = time.time(); waited = feed_gate_wait(jobgate, log=lambda s: print(s, flush=True)); t_gate = time.time() - t0
    plan, c = plan_lab(tool, n, a)
    T = c['T']; T['gate_s'] = t_gate
    t0 = time.time()
    psha = runs.plan_identity(plan); out = c['out']; expect = c['expect']
    if os.path.lexists(out):
        pre = 'EPG.' if tool == 'profile' else 'CTX.'
        try:
            m = runs.verify_committed(out, runs.MANIFEST, pre, c['code'])        # K4: the ONE shared check (every byte, every block)
        except (runs.RunRefused, ValueError, OSError) as e:
            raise Refusal('OUTPUT_EXISTS', '%s exists and is not a complete, intact run (%s): never overwritten' % (out, e))
        known = dict(c['frozen_files'], **{'catalog:%s' % f: os.path.join(out, f) for f in os.listdir(out) if 'CATALOG' in f})
        known['%s%s' % (c['lk'], c['child_list_name'])] = os.path.join(out, '_selection', c['child_list_name']) if c['filtered'] else c['lst']
        _, chg, _ = recheck_pins(tool, m.get('pins', {}).get('fixed', {}), known)
        if m.get('plan_sha16') == psha and not chg:
            print('UP TO DATE %s (plan %s, %d day-parts, every committed byte and pin rechecked)' % (out, psha, len(m['parts']))); return 0
        if chg:
            raise Refusal('OUTPUT_EXISTS', '%s: its inputs changed since the commit (%s): not up to date, never overwritten' % (out, chg[:5]))
        raise Refusal('OUTPUT_EXISTS', '%s holds another complete run (plan %s, this plan %s): choose a new out_root' % (out, m.get('plan_sha16'), psha))
    kept, moved = set(), []
    old = runs.find_resumable(out, psha) if c['opt'].get('resume') else None
    if c['opt'].get('resume') and old is None:
        raise Refusal('RESUME_NOTHING', 'no kept attempt of this plan (%s) beside %s' % (psha, out))
    if old:
        logbase = out + '.logs'; os.makedirs(logbase, exist_ok=True)
        aside = os.path.join(logbase, '_to_delete_resume_%s' % dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        stage, kept, moved = runs.adopt_for_resume(old, out, expect, c['part_pins'], aside)
    else:
        stage = runs.stage(out)
    run_id = os.path.basename(stage).split('.pending_', 1)[1]
    logdir = os.path.join(out + '.logs', run_id); os.makedirs(logdir, exist_ok=True)
    T['stage_s'] = time.time() - t0
    rows_done = []
    def stop(signum, frame):
        raise Refusal('INTERRUPTED', 'signal %d' % signum)
    old_term = signal.signal(signal.SIGTERM, stop)
    try:
        t0 = time.time()
        pp = os.path.join(stage, runs.PLAN)
        if os.path.exists(pp):
            if runs.plan_identity(json.load(open(pp))) != psha:
                raise Refusal('RESUME_PLAN_DIFFERS', pp)
        else:
            runs.write_json_atomic(pp, plan)
        lst = c['lst']; hist = c['hist']
        if c['filtered']:
            os.makedirs(os.path.join(stage, '_selection'), exist_ok=True)
            child_list = os.path.join(stage, '_selection', c['child_list_name'])
            if not os.path.exists(child_list):
                from labcore.v2_7 import selection as S
                tmp = '%s.tmp_%d' % (child_list, os.getpid())
                with open(tmp, 'x') as fh:
                    fh.write(S.selected_text(c['sel'])); fh.flush(); os.fsync(fh.fileno())
                os.replace(tmp, child_list)
            if c['tool'] == 'context' and not hist:
                hist = lst
        else:
            child_list = lst
        csha = runs.sha16_file(child_list)
        c['part_pins']['%s%s' % (c['lk'], os.path.basename(child_list))] = csha
        if c['by_day']:                                          # FORMAT.json once, before any worker: lab3.write._format (the canonical
            sys.path.insert(0, c['code'])                         # writer's own function, called, not copied) races when two workers
            from lab3 import write as LW                          # start on a fresh root (FileExistsError on FORMAT.json.tmp): LAB1 request
            LW._format(stage)
        rdir = os.path.join(out + '.logs', 'reports_%s' % psha)   # Profile run reports, kept across attempts of this plan
        os.makedirs(rdir, exist_ok=True)
        weight = {d: len(cs) for d, cs in c['by_day'].items()}; days = sorted(c['by_day'])
        cmds = []
        if c['tool'] == 'profile':
            todo = [d for d in days if (d, 'EPG.%s' % c['subj']) not in kept]
            for run in runs_of(days, set(days) - set(todo)):
                for ch in balanced(run, weight, max(1, round(c['n'] * len(run) / max(1, len(todo))))):
                    cmds.append([PY, '-B', EP, 'build', c['lab'], c['code'], child_list, c['settings'], c['subj'], ch[0], ch[-1], stage]
                                + c['wtail'] + ['--report', os.path.join(rdir, 'profile_%s_%s.json' % (ch[0], ch[-1]))])
        else:
            tail = []
            if c['dec'] or hist:
                tail = [c['dec'] or '0'] + ([hist] if hist else [])
            for lv in c['levels']:
                todo = [d for d in days if (d, 'CTX.%s.%s' % (c['subj'], lv)) not in kept]
                for run in runs_of(days, set(days) - set(todo)):
                    for ch in balanced(run, weight, max(1, round(c['n'] * len(run) / max(1, len(todo))))):
                        cmds.append([PY, '-B', CTX, 'build', c['lab'], c['code'], child_list, c['subj'], lv, ch[0], ch[-1], stage] + tail + c['wtail'])
        if plan['child_wrapper']:
            cmds = [[PY, '-B', plan['child_wrapper']['path']] + cm for cm in cmds]
        T['plan_write_s'] = time.time() - t0
        t0 = time.time()
        rows_done = launch(cmds, c['n'], logdir, env1(), c['tool'], pidfile=os.path.join(logdir, runs.WORKERS))
        T['workers_s'] = time.time() - t0
        t0 = time.time()
        now_f = {k: runs.sha16_file(p) for k, p in c['frozen_files'].items()}
        changed = sorted(k for k in now_f if now_f[k] != c['frozen'][k])
        if changed:
            raise Refusal('CODE_OR_INPUT_CHANGED', 'changed during the run: %s' % changed)
        prefixes = ('EPG.%s' % c['subj'],) if c['tool'] == 'profile' else tuple('CTX.%s.%s' % (c['subj'], lv) for lv in c['levels'])
        chk = runs.check_stage(stage, expect, c['part_pins'], lab_root=c['lab'], prefixes=prefixes)
        known = dict(c['frozen_files'], **{'%s%s' % (c['lk'], os.path.basename(child_list)): child_list},
                     **{'catalog:%s' % f: os.path.join(stage, f) for f in os.listdir(stage) if 'CATALOG' in f})
        n_pins, chg, unres = recheck_pins(c['tool'], chk['pins']['fixed'], known)
        if chg:
            raise Refusal('CODE_OR_INPUT_CHANGED', 'pins named by the parts changed during the run: %s' % chg)
        chk['pins'].update(rechecked=n_pins, unresolved=unres)
        tool_cov = (fold_profile_reports(rdir, expect) if c['tool'] == 'profile' else
                    fold_context_receipts(stage, expect, c['sel']['rows'], c['dec'], None if c['filtered'] else c['plans']))
        if c['tool'] == 'context':
            for lv, pl in c['plans'].items():
                with open(os.path.join(logdir, 'PREFLIGHT_%s.json' % lv), 'w') as fh:
                    json.dump(pl, fh, indent=1, sort_keys=True)
        T['check_s'] = time.time() - t0
        sel = c['sel']; cov = sel['coverage']
        files = runs.top_files(stage)
        body = dict(run_id=run_id, tool=c['tool'], plan_sha16=psha, parts=chk['parts'], files=files,
                    selection=dict(status=sel['status'], cache_key=sel['cache_key'], request=sel['request'], identity=sel['identity']),
                    coverage=dict(requested=cov['requested'], list=cov['list'], excluded_in_range=cov['excluded_in_range'],
                                  observed=dict(cov['observed'], day_parts=chk['observed']['day_parts'], rows=chk['observed']['rows']),
                                  empty_selection=sel['status'] == 'EMPTY_SELECTED_POPULATION', source_states=cov['source_states'],
                                  reasons_written=chk['observed']['reasons'], member_coverage=cov['member_coverage'], tool_reports=tool_cov),
                    pins=dict(chk['pins'], frozen=c['frozen'], child_list=csha), seals=chk['seals'],
                    terminal=dict(exit_status=0, worker_exit=sorted({r['rc'] for r in rows_done})))
        t0 = time.time()
        par = maxrss_bytes(resource.getrusage(resource.RUSAGE_SELF))
        body['telemetry'] = dict(started_utc=started, out_root=out, logs=logdir, gate_waited_s=waited, wall_s=None, phases_s=None,
                                 resumed_parts=len(kept), workers_run=len(rows_done),
                                 parent_peak_rss_gb=round(par / GB, 4), workers=[dict(r, cmd=' '.join(r['cmd'][2:5] + r['cmd'][-4:]))
                                                                                 for r in rows_done],
                                 workers_peak_rss_gb_max=max([r['peak_rss_gb'] for r in rows_done] or [0.0]),
                                 workers_peak_rss_gb_sum=round(sum(r['peak_rss_gb'] for r in rows_done), 4), moved_aside=moved,
                                 gb='10^9 bytes; each process its own peak (wait4 ru_maxrss), not a simultaneous sum')
        body['telemetry']['phases_s'] = {k: round(v, 3) for k, v in sorted(T.items())}
        body['telemetry']['wall_s'] = round(time.time() - t_start, 3)
        cov_coins = sorted(set(cov['requested']['members']) | set(cov['observed']['coins']))   # the selection's coins (S1 coverage)
        m = runs.commit(stage, out, runs.MANIFEST, body, window=(sel['request']['first'], sel['request']['last']), coins=cov_coins)
        t_commit = time.time() - t0
        if c['opt'].get('verify'):
            t0 = time.time(); runs.verify_committed(out, runs.MANIFEST, prefixes[0] if len(prefixes) == 1 else None, c['code'])
            t_verify = time.time() - t0
        else:
            t_verify = None
        with open(os.path.join(logdir, 'TERMINAL.json'), 'w') as f:            # after-commit telemetry (the manifest is final)
            json.dump(dict(commit_s=round(t_commit, 3), verify_s=t_verify, wall_s=round(time.time() - t_start, 3), status='COMMITTED'), f)
        print('COMMITTED %s %s: %s, events %d, day-parts %d, workers %d, wall %.1f s (phases %s; commit %.2f s), parent %.3f GB, workers max %.3f GB'
              % (c['tool'], out, sel['status'], cov['observed']['events'], len(chk['parts']), len(rows_done), time.time() - t_start,
                 body['telemetry']['phases_s'], t_commit, par / GB, body['telemetry']['workers_peak_rss_gb_max']))
        return 0
    except BaseException as e:
        if isinstance(e, Refusal):
            e.after_stage = True                                  # refused after the stage opened: exit 1 (failed), never 2
        kept_as = runs.abort(stage, out, '%s: %s' % (type(e).__name__, e)) if os.path.isdir(stage) else None
        with open(os.path.join(logdir, 'TERMINAL.json'), 'w') as f:
            json.dump(dict(status='FAILED', error=str(e)[:2000], kept_as=kept_as, workers=[dict(r, cmd=' '.join(r['cmd'][2:5])) for r in rows_done]), f)
        print('FAILED %s: %s (kept as %s; no manifest: never consumable)' % (out, e, kept_as), flush=True)
        raise
    finally:
        signal.signal(signal.SIGTERM, old_term)


def run_cause(n, a):
    lab, code, events, settings, subj, first, last, out = a[2:10]; extra = a[10:]
    env = env1()
    if not 1 <= n <= 8:
        raise SystemExit('REFUSED: 1 to 8 cause workers (the team process budget), got %d' % n)
    base = [lab, code, events, settings, subj, first, last, out] + extra
    logdir = os.path.realpath(out) + '.logs'; os.makedirs(logdir, exist_ok=True)
    t0 = time.time()
    with open(os.path.join(logdir, 'plan.log'), 'w') as log:
        rc = subprocess.call([PY, '-B', EC, 'plan'] + base, stdout=log, stderr=subprocess.STDOUT, env=env, preexec_fn=nice10)
    if rc != 0:
        sys.stdout.write(open(os.path.join(logdir, 'plan.log')).read())
        raise SystemExit('REFUSED rc %d: the plan was refused; nothing computed (%s/plan.log)' % (rc, logdir))
    cmds = [[PY, '-B', EC, 'build'] + base + ['--shard', '%d/%d' % (k, n)] for k in range(n)]
    plan_s = time.time() - t0
    t0 = time.time(); procs = []; logs = []; pending = list(cmds)
    while pending or procs:
        while pending and len(procs) < n:
            c = pending.pop(0)
            log = open(os.path.join(logdir, 'shard_%d.log' % len(logs)), 'w')
            logs.append(log.name); procs.append((subprocess.Popen(c, stdout=log, stderr=subprocess.STDOUT, env=env, preexec_fn=nice10), c))
        time.sleep(0.2)
        still = []
        for p, c in procs:
            if p.poll() is None:
                still.append((p, c))
            elif p.returncode != 0:
                for q, _ in procs:                                # stop the other chunks: no half-run left behind
                    if q.poll() is None:
                        q.terminate()
                for q, _ in procs:
                    q.wait()
                raise SystemExit('FAILED rc %d: %s%s' % (p.returncode, ' '.join(c), ' (no COMMIT: the run is not complete)'))
        procs = still
    t1 = time.time()
    with open(os.path.join(logdir, 'commit.log'), 'w') as log:
        rc = subprocess.call([PY, '-B', EC, 'commit', out], stdout=log, stderr=subprocess.STDOUT, env=env, preexec_fn=nice10)
    sys.stdout.write(open(os.path.join(logdir, 'commit.log')).read())
    print('PARALLEL cause processes %d shards %d plan %.1f s shards %.1f s commit %.1f s wall %.1f s' % (
        n, len(cmds), plan_s, t1 - t0, time.time() - t1, time.time() - t0 + plan_s))
    if rc != 0:
        raise SystemExit('INCOMPLETE: COMMIT refused rc %d (%s/commit.log)' % (rc, logdir))


def outcomes_stage(out):
    """True when out is the staging folder an event_outcomes run opened (<root>.pending_<pid>_<stamp> holding RUN_FROZEN.json)"""
    return bool(re.search(r'\.pending_\d+_\d{8}T\d{6}\d*Z$', os.path.basename(os.path.abspath(out)))) and \
        os.path.isfile(os.path.join(out, 'RUN_FROZEN.json'))


def run_outcomes(n, a):
    lab, code, events, settings, subj, first, last, out = a[2:10]; extra = a[10:]
    if not 1 <= n <= 8:
        raise SystemExit('REFUSED: 1 to 8 outcomes workers (the team process budget), got %d' % n)
    if not outcomes_stage(out):                                   # the public command: the whole checked run is event_outcomes' own
        cmd = [PY, '-B', EO, 'run', str(n), lab, code, events, settings, subj, first, last, out] + extra
        return subprocess.call(cmd, env=env1(), preexec_fn=nice10)
    if extra:
        raise SystemExit('REFUSED: worker mode (inside %s) takes no options: %s' % (out, extra))
    w = alarm_day_counts(events, first, last)                     # worker mode: day chunks inside the stage event_outcomes opened,
    cmds = [[PY, '-B', EO, 'build', lab, code, events, settings, subj, c[0], c[-1], out]   # contiguous, balanced by events per day
            for c in balanced(sorted(w), w, n)]
    t0 = time.time()
    try:
        done = launch(cmds, n, out, env1(), 'parallel')
    except Refusal as e:
        raise SystemExit('FAILED %s (no commit: event_outcomes keeps the stage as failed)' % e)
    print('PARALLEL outcomes workers %d commands %d days %d exited 0, wall %.1f s, peak memory per worker max %.3f GB (completion is '
          'checked by event_outcomes verify_stage and commit, not by log lines)' % (n, len(cmds), len(w), time.time() - t0,
                                                                                   max([r['peak_rss_gb'] for r in done] or [0.0])))
    return 0


def main(a):
    if len(a) < 2 or not a[0].isdigit():
        raise SystemExit(__doc__)
    n, tool = int(a[0]), a[1]
    if tool == 'cause':
        return run_cause(n, a)
    if tool == 'outcomes':
        return run_outcomes(n, a)
    if tool in ('profile', 'context'):
        try:
            return run_lab(tool, n, a[2:])
        except Refusal as e:
            print('REFUSED %s' % e, file=sys.stderr, flush=True)
            return 1 if getattr(e, 'after_stage', False) or e.code in ('WORKER_FAILED', 'INTERRUPTED', 'CODE_OR_INPUT_CHANGED') else 2
        except Exception as e:                                       # labcore.runs refusals and anything else: nothing published
            code = getattr(e, 'code', type(e).__name__)
            print('FAILED %s: %s' % (code, e), file=sys.stderr, flush=True)
            return 1
    raise SystemExit(__doc__)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
