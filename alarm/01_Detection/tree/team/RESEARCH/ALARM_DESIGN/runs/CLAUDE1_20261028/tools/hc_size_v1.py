#!/usr/bin/env python3
"""hc_size_v1.py: how many waves will an alarm definition give a month, before COUNT, in one command.

Owner: SCOUT (the alarm kit). New tool, 1 Nov 2026, ALARM_V1_16; it replaces no file. why: team/RESEARCH/plans/PLAN_SCOUT_TOOLS_V1_16_20261101.md
(the owner 1 Nov 2026 09:12 Berlin, the tool fixes; LESSONS_V5 22-24: agents sized on the probe days, which hold the 10 Oct crash, and
SQUEEZEBACK came out INSUFFICIENT with 24 and 35 waves in quiet months). It runs the hand check hc_defs_v4_to20251231.py beside this file
(this interpreter, the same settings file) on the FULL roster (the one COUNT pins, ROSTER_BUILD.json b93de33b2a73a56e, in this Alarm
folder's detection tree) for two 8-day weeks, one child process each, with --out, N = 0:
  QUIET  20251110..20251117   an ordinary week
  PROBE  20251009..20251016   the memory probe's week (hc_mem_probe), with the 10 Oct crash
and counts waves by the labcore gap rule (a fire more than 1800 s after the previous fire of any coin starts a new wave).

  python3 -B hc_size_v1.py --settings <settings file> DEF.json
Prints the hand check's last line for each week, then:
  SIZE <WEEK> <first>..<last>: <f> fires, <w> waves, <c> coins with a fire; <m> waves a month (w x 30 / 8); peak <MB> MB; fire list <path>
  ...
  HINT ...    when the quiet week gives under 30 waves a month (COUNT calls a month with under 30 waves INSUFFICIENT), and one line with
              the bar of LESSONS_V5 23 (opinion): about 250 to 300 waves a month (1,000 to 1,200 over Sep-Dec) for a pooled t of 3 at
              LEAD +8.
The fire lists and the hand checks' logs (HC_<WEEK>.log) are kept in a fresh folder (tempfile), named in the output, for novelty_v3 (an indication only: 16 days).
Reads no outcome. Writes only the two fire lists and the two logs. Exit 0 done; 2 refused (usage, settings, roster, outside an Alarm folder, a
definition that is not JSON) or a hand check failed (its last lines printed)."""
import hashlib, json, os, subprocess, sys, tempfile

DETECTION_TREE = ('01_Detection', 'tree')
ROSTER = 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'
WEEKS = (('QUIET', '20251110', '20251117'), ('PROBE', '20251009', '20251016'))
DAYS_A_WEEK = 8
GAP = 1800
UNDER = 30
HAND_CHECK = 'hc_defs_v4_to20251231.py'
USAGE = 'USAGE hc_size_v1.py --settings SETTINGS DEF.json'


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


def parse(a):
    if len(a) != 3 or a[0] != '--settings':
        raise Refused(USAGE)
    return a[1], a[2]


def read_fires(path):
    """-> [(coin, t)] of a hc_defs --out file (columns coin, t, side)"""
    with open(path) as f:
        head = f.readline().rstrip('\n').split('\t')
        ic, it = head.index('coin'), head.index('t')
        return [(x[ic], int(x[it])) for x in (l.rstrip('\n').split('\t') for l in f if l.strip())]


def waves(times):
    """the number of waves in fire times (any order): a fire more than GAP s after the previous one starts a new wave"""
    n, prev = 0, None
    for t in sorted(times):
        if prev is None or t - prev > GAP:
            n += 1
        prev = t
    return n


def a_month(w):
    """waves a month from the waves of one 8-day week"""
    return w * 30.0 / DAYS_A_WEEK


def peak_mb(ru_maxrss, platform=sys.platform):
    """ru_maxrss in mebibytes: macOS counts bytes, Linux kilobytes"""
    return ru_maxrss / (1024.0 * 1024.0) if platform == 'darwin' else ru_maxrss / 1024.0


def run_child(cmd, log):
    """-> (rc, stdout and stderr text, peak MB of this child alone: os.wait4's own rusage). The child writes to log ('x')."""
    with open(log, 'x') as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)
        _, status, ru = os.wait4(p.pid, 0)
    p.returncode = os.waitstatus_to_exitcode(status)
    return p.returncode, open(log).read(), int(round(peak_mb(ru.ru_maxrss)))


def hints(quiet_month):
    out = []
    if quiet_month < UNDER:
        out.append('HINT UNDER %d WAVES A MONTH ON THE QUIET WEEK (%.1f): COUNT calls a month with under %d waves INSUFFICIENT; '
                   'widen the rule or pick a busier trigger (LESSONS_V5 22)' % (UNDER, quiet_month, UNDER))
    out.append('HINT the bar (LESSONS_V5 23, opinion): about 250 to 300 waves a month (1,000 to 1,200 over Sep-Dec) for a pooled t of 3 at LEAD +8')
    return out


def main(a):
    try:
        settings, defn = parse(a)
        S = settings_module(__file__)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    try:
        S.load(settings)
        try:
            json.load(open(defn))
        except (OSError, ValueError) as e:
            raise Refused('DEFINITION UNREADABLE %s: %s' % (defn, e))
        roster = os.path.join(S.alarm_root(__file__), *DETECTION_TREE, *ROSTER.split('/'))
        if not os.path.isfile(roster):
            raise Refused('NO ROSTER %s (the Alarm folder must hold it)' % roster)
        raw = open(roster, 'rb').read()
        coins = json.loads(raw)['coins']
        hc = os.path.join(os.path.dirname(os.path.abspath(__file__)), HAND_CHECK)
        if not os.path.isfile(hc):
            raise Refused('NO HAND CHECK %s' % hc)
    except (Refused, S.Refused, ValueError, KeyError) as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    out_dir = tempfile.mkdtemp(prefix='hc_size_')
    print('ROSTER %d coins (sha16 %s); fire lists in %s' % (len(coins), hashlib.sha256(raw).hexdigest()[:16], out_dir))
    quiet = None
    for name, first, last in WEEKS:
        fl = os.path.join(out_dir, 'FIRES_%s.tsv' % name)
        cmd = [sys.executable, '-B', hc, '--settings', settings, '--out', fl, defn, first, last, ','.join(coins), '0', 'NONE']
        rc, out, mb = run_child(cmd, os.path.join(out_dir, 'HC_%s.log' % name))
        if rc != 0:
            tail = out.strip().split('\n')[-8:]
            print('\n'.join(tail), file=sys.stderr)
            print('REFUSED HAND CHECK FAILED ON %s rc %d (peak %d MB before it stopped)' % (name, rc, mb), file=sys.stderr)
            return 2
        last_line = [l for l in out.split('\n') if l.startswith('fires ')]
        if last_line:
            print('%s: %s' % (name, last_line[-1]))
        fires = read_fires(fl)
        w = waves([t for _, t in fires])
        if name == 'QUIET':
            quiet = a_month(w)
        print('SIZE %s %s..%s: %d fires, %d waves, %d coins with a fire; %.1f waves a month (w x 30 / %d); peak %d MB; fire list %s'
              % (name, first, last, len(fires), w, len({c for c, _ in fires}), a_month(w), DAYS_A_WEEK, mb, fl))
    print('\n'.join(hints(quiet)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
