#!/usr/bin/env python3
"""hc_mem_probe_v1.py: the memory check before COUNT in one command: the hand check on half B of the roster for 8 days, its peak memory
against 732 MB.

Owner: SCOUT (the alarm kit). New tool by SCOUT for the clean release (K7, 30 Oct 2026); it replaces no file. Until now there was only
the rule, done by hand (LEARNINGS_V6 V6-06: "Measure a definition with the helper on half B for 8 days before COUNT; keep it at or under
732 MB"; V6-57: "not one coin-day"). The method is AD1's (runs/AD1_20261029/ideas/FORCEDBREAK/HAND/MEMORY_PROBES.tsv 2df1d65c6c13da0f):
hc_defs as a child process on half B of the roster (26 coins), 20251009 to 20251016 with its own warm-up days, the child's peak resident
memory (ru_maxrss). It calls, imports and reads no old edition.

  python3 -B hc_mem_probe_v1.py --settings <settings file> DEF.json [--limit-mb 732]
Half B: the roster's coins from the middle on, coins[len(coins) // 2:], as the COUNT job splits them (KIT_V5 JOB_COUNT_V6, HB). The
roster is the one COUNT pins (ROSTER_BUILD.json b93de33b2a73a56e), in this Alarm folder's detection tree 01_Detection/tree/ (found by
_tools/settings_v1.alarm_root). The hand check is hc_defs_v2_to20251231.py beside this file, run with this interpreter, the same settings
file (its LAB_DAYS) and N = 0 (no fire lines).
Prints the hand check's lines, then one line:
  PEAK <MB> MB (limit <L> MB; half B <n> coins, 20251009..20251016; roster <sha16>): PASS | OVER
MB = the peak resident memory in mebibytes, rounded; PASS when it is at or under the limit. COUNT's detect workers stop at 2 GiB
(WORKER_RSS_CAP); 732 MB is the largest hand-check peak whose COUNT passed (GB1, V6-06).
Exit 0 PASS; 1 OVER; 2 refused (usage, settings, roster, outside an Alarm folder) or the hand check failed (its last lines printed)."""
import hashlib, json, os, resource, subprocess, sys

DETECTION_TREE = ('01_Detection', 'tree')
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
DAYS = ('20251009', '20251016')
LIMIT_MB = 732
HAND_CHECK = 'hc_defs_v2_to20251231.py'
USAGE = 'USAGE hc_mem_probe_v1.py --settings SETTINGS DEF.json [--limit-mb 732]'


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


def verdict(mb, limit):
    return 'PASS' if mb <= limit else 'OVER'


def parse(a):
    settings, limit, rest = None, LIMIT_MB, []
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
    except (Refused, S.Refused, ValueError, KeyError) as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    cmd = [sys.executable, '-B', hc, '--settings', settings, defn, DAYS[0], DAYS[1], ','.join(coins), '0', 'NONE']
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
    print('PEAK %d MB (limit %d MB; half B %d coins, %s..%s; roster %s): %s'
          % (mb, limit, len(coins), DAYS[0], DAYS[1], hashlib.sha256(raw).hexdigest()[:16], v))
    return 0 if v == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
