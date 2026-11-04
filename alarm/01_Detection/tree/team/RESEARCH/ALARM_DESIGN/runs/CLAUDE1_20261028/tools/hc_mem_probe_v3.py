#!/usr/bin/env python3
"""hc_mem_probe_v3.py (SCOUT, 2 Nov 2026, V1_18_FIXES; why: RESULTS_R5 item 1): hc_mem_probe_v2.py with the limit from the code. The old line said OVER on
rules that ran. The real stop is WORKER_RSS_CAP, read from the detectors COUNT and GRADE run (2 * 1024 ** 3 bytes = 2048 MB; they must agree, else refused).
This probe does not read a worker: a GRADE worker reads more than the probe, so the probe is scaled. Pairs of run SCOUT_20261101 (probe MB -> largest worker MB in
DETECT_RUN.json): 826->1288, 981->1583, 1053->1467, 1121->1583, 1233->1302, 1283->1911 and, on the other try of that same variant, 1283->2066 (job 20265990, REFUSED
WORKER_RSS_CAP 2166620160 bytes; the unchanged requeue 20265994 ran). Worst seen 1.61 worker MB per probe MB. Limit = cap / 1.61 = 1272 probe MB: PASS to there, OVER above.
Seven pairs: a small sample; a rule past 1.61 can still stop at the cap, and COUNT or GRADE then says so. --limit-mb above the cap is refused. The PEAK line also prints
the cap and the worker estimate. Nothing else changed. v2's text follows, read v3 for v2.
hc_mem_probe_v2.py (SCOUT, 1 Nov 2026, ALARM_V1_16; why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md): hc_mem_probe_v1.py
302f8ff36e11acb6 with the hand check hc_defs_v4_to20251231.py (was v2: the same fires, plus --out) writing every fire to a fresh
folder (tempfile, kept, named in the output), and two more lines before PEAK, nothing else:
  WAVES <w> on half B, 20251009..20251016 (<f> fires; fire list <path>)
      waves by the labcore gap rule: a fire more than 1800 s after the previous fire of any coin starts a new wave. These days hold
      the 10 Oct crash: size on a quiet week too (hc_size_v1.py beside this file).
  MB PER INPUT <x> (peak <MB> MB / <k> inputs of the definition)
      k = the keys of the definition's "inputs"; LESSONS_V5 24: about 18 MB per derived input, stay under about 12 inputs.
The PEAK line, the exit codes and the refusals are v1's; a definition without an "inputs" object is refused (rc 2). v1's text follows.
hc_mem_probe_v1.py: the memory check before COUNT in one command: the hand check on half B of the roster for 8 days, its peak memory
against the limit.

Owner: SCOUT (the alarm kit). New tool by SCOUT for the clean release (K7, 30 Oct 2026); it replaces no file. Until now there was only
the rule, done by hand (LEARNINGS_V6 V6-06: "Measure a definition with the helper on half B for 8 days before COUNT"; V6-57: "not one coin-day"). The method is AD1's (runs/AD1_20261029/ideas/FORCEDBREAK/HAND/MEMORY_PROBES.tsv 2df1d65c6c13da0f):
hc_defs as a child process on half B of the roster (26 coins), 20251009 to 20251016 with its own warm-up days, the child's peak resident
memory (ru_maxrss). It calls, imports and reads no old edition.

  python3 -B hc_mem_probe_v1.py --settings <settings file> DEF.json [--limit-mb MB]
Half B: the roster's coins from the middle on, coins[len(coins) // 2:], as the COUNT job splits them (KIT_V5 JOB_COUNT_V6, HB). The
roster is the one COUNT pins (ROSTER_BUILD.json b93de33b2a73a56e), in this Alarm folder's detection tree 01_Detection/tree/ (found by
_tools/settings_v1.alarm_root). The hand check is hc_defs_v2_to20251231.py beside this file, run with this interpreter, the same settings
file (its LAB_DAYS) and N = 0 (no fire lines).
Prints the hand check's lines, then one line:
  PEAK <MB> MB (limit <L> MB; half B <n> coins, 20251009..20251016; roster <sha16>): PASS | OVER
MB = the peak resident memory in mebibytes, rounded; PASS when it is at or under the limit. COUNT's and GRADE's detect workers stop at
WORKER_RSS_CAP.
Exit 0 PASS; 1 OVER; 2 refused (usage, settings, roster, outside an Alarm folder) or the hand check failed (its last lines printed)."""
import ast, hashlib, json, os, resource, subprocess, sys, tempfile

DETECTION_TREE = ('01_Detection', 'tree')
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
DAYS = ('20251009', '20251016')
CAP_FILES = ('team/RESEARCH/tools/alarm_process/detect_aw1.py', 'team/RESEARCH/tools/idea_to_grade/detect_v2.py', 'team/RESEARCH/tools/idea_to_grade/detect_gm1.py')
WORKER_PER_PROBE = 1.61   # worst of 7 pairs, run SCOUT_20261101: 2066 MB worker at 1283 MB probe (see the header)
HAND_CHECK = 'hc_defs_v4_to20251231.py'
GAP = 1800
USAGE = 'USAGE hc_mem_probe_v3.py --settings SETTINGS DEF.json [--limit-mb MB]'


class Refused(Exception):
    pass


def settings_module(start):
    """_tools/settings_v1.py of the Alarm folder that holds `start` (the nearest parent folder that has it), imported"""
    d = os.path.dirname(os.path.abspath(start))
    while not os.path.isfile(os.path.join(d, '_tools', 'settings_v1.py')):
        if os.path.dirname(d) == d:
            raise Refused('NOT INSIDE AN ALARM FOLDER %s (run the copy inside the Alarm folder)' % os.path.abspath(start))
        d = os.path.dirname(d)
    sys.path.insert(0, os.path.join(d, '_tools'))
    try:
        import settings_v1
    finally:
        sys.path.pop(0)
    return settings_v1


def half_b(coins):
    """the COUNT job's second half (HB): from the middle on"""
    return coins[len(coins) // 2:]


def peak_mb(ru_maxrss, platform=sys.platform):
    """ru_maxrss in mebibytes: macOS counts bytes, Linux kilobytes"""
    return ru_maxrss / (1024.0 * 1024.0) if platform == 'darwin' else ru_maxrss / 1024.0


def waves(times):
    """the number of waves in fire times (any order): a fire more than GAP s after the previous one starts a new wave"""
    n, prev = 0, None
    for t in sorted(times):
        if prev is None or t - prev > GAP:
            n += 1
        prev = t
    return n


def read_fire_times(path):
    """the t column of a hc_defs --out file (coin, t, side)"""
    with open(path) as f:
        head = f.readline().rstrip('\n').split('\t')
        i = head.index('t')
        return [int(l.rstrip('\n').split('\t')[i]) for l in f if l.strip()]


def n_inputs(defn):
    """the number of the definition's inputs (keys of its "inputs" object)"""
    try:
        d = json.load(open(defn))
    except (OSError, ValueError) as e:
        raise Refused('DEFINITION UNREADABLE %s: %s' % (defn, e))
    if not isinstance(d, dict) or not isinstance(d.get('inputs'), dict) or not d['inputs']:
        raise Refused('DEFINITION %s HAS NO "inputs" OBJECT' % defn)
    return len(d['inputs'])


def cap_of_file(path):
    """WORKER_RSS_CAP of a detector: the top-level constant, parsed, never imported; numbers with * and ** only"""
    tree = ast.parse(open(path).read())
    def val(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, int):
            return n.value
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult):
            return val(n.left) * val(n.right)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow):
            return val(n.left) ** val(n.right)
        raise Refused('WORKER_RSS_CAP IN %s IS NOT A PLAIN NUMBER' % path)
    for s in tree.body:
        if isinstance(s, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'WORKER_RSS_CAP' for x in s.targets):
            return val(s.value)
    raise Refused('NO WORKER_RSS_CAP IN %s' % path)


def worker_cap(tree):
    """the cap in bytes: every detector the jobs run must hold the same one"""
    caps = {}
    for rel in CAP_FILES:
        p = os.path.join(tree, *rel.split('/'))
        if not os.path.isfile(p):
            raise Refused('NO DETECTOR %s (the Alarm folder must hold it)' % p)
        caps[rel] = cap_of_file(p)
    if len(set(caps.values())) != 1:
        raise Refused('WORKER_RSS_CAP DISAGREE: %s' % caps)
    return caps[CAP_FILES[0]]


def limit_from_cap(cap_bytes):
    """the probe MB at which the worst worker seen reaches the cap"""
    return int(cap_bytes / (1024.0 * 1024.0) / WORKER_PER_PROBE)


def worker_estimate(mb):
    return int(round(mb * WORKER_PER_PROBE))


def verdict(mb, limit):
    return 'PASS' if mb <= limit else 'OVER'


def parse(a):
    settings, limit, rest = None, None, []
    i = 0
    while i < len(a):
        if a[i] in ('--settings', '--limit-mb') and i + 1 < len(a):
            if a[i] == '--settings':
                settings = a[i + 1]
            else:
                if not a[i + 1].isdigit() or int(a[i + 1]) <= 0:
                    raise Refused('--limit-mb must be a whole number of MB above 0: %r' % a[i + 1])
                limit = int(a[i + 1])
            i += 2
        else:
            rest.append(a[i]); i += 1
    if settings is None or len(rest) != 1:
        raise Refused(USAGE)
    return settings, rest[0], limit


def main(a):
    try:
        settings, defn, limit = parse(a)
        S = settings_module(__file__)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    try:
        S.load(settings)
        roster = os.path.join(S.alarm_root(__file__), *DETECTION_TREE, *ROSTER.split('/'))
        if not os.path.isfile(roster):
            raise Refused('NO ROSTER %s (the Alarm folder must hold it)' % roster)
        raw = open(roster, 'rb').read()
        coins = half_b(json.loads(raw)['coins'])
        hc = os.path.join(os.path.dirname(os.path.abspath(__file__)), HAND_CHECK)
        if not os.path.isfile(hc):
            raise Refused('NO HAND CHECK %s' % hc)
        k = n_inputs(defn)
        cap = worker_cap(os.path.join(S.alarm_root(__file__), *DETECTION_TREE))
        cap_mb = int(cap / (1024 * 1024))
        if limit is not None and limit > cap_mb:
            raise Refused('--limit-mb %d IS ABOVE WORKER_RSS_CAP %d MB' % (limit, cap_mb))
        limit = limit_from_cap(cap) if limit is None else limit
    except (Refused, S.Refused, ValueError, KeyError) as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    fl = os.path.join(tempfile.mkdtemp(prefix='hc_mem_probe_'), 'FIRES.tsv')
    cmd = [sys.executable, '-B', hc, '--settings', settings, '--out', fl, defn, DAYS[0], DAYS[1], ','.join(coins), '0', 'NONE']
    p = subprocess.run(cmd, capture_output=True, text=True)
    mb = int(round(peak_mb(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)))
    if p.stdout.strip():
        print(p.stdout.rstrip('\n'))
    if p.returncode != 0:
        tail = (p.stdout + p.stderr).strip().split('\n')[-8:]
        print('\n'.join(tail), file=sys.stderr)
        print('REFUSED HAND CHECK FAILED rc %d (peak %d MB before it stopped)' % (p.returncode, mb), file=sys.stderr)
        return 2
    v = verdict(mb, limit)
    ts = read_fire_times(fl)
    print('WAVES %d on half B, %s..%s (%d fires; fire list %s)' % (waves(ts), DAYS[0], DAYS[1], len(ts), fl))
    print('MB PER INPUT %.1f (peak %d MB / %d inputs of the definition)' % (mb / float(k), mb, k))
    print('PEAK %d MB (limit %d MB; WORKER_RSS_CAP %d MB, worker estimate %d MB at %.2f per probe MB; half B %d coins, %s..%s; roster %s): %s'
          % (mb, limit, cap_mb, worker_estimate(mb), WORKER_PER_PROBE, len(coins), DAYS[0], DAYS[1], hashlib.sha256(raw).hexdigest()[:16], v))
    return 0 if v == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
