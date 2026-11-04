#!/usr/bin/env python3
"""hc_defs_v2_to20251231.py: the hand check of an alarm definition, run from this Alarm folder only.

Owner: SCOUT (the alarm kit's hand-check helper; edition 1 by the run CLAUDE1_20261028, 29 Oct 2026). New edition by SCOUT for the clean
release (K7, 30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release folder only"). Old file:
team/RESEARCH/ALARM_DESIGN/runs/CLAUDE1_20261028/tools/hc_defs_v1_to20251231.py edc444f943ea155c, untouched. This edition calls,
imports and reads no old edition. TEST, NOT REVIEWED.

What it does (as edition 1; IDEA_TO_ALARM_V3 step 6): parse a definition with detect.load_definition (the metric gate: STOP, CAUTION and
UNPROVEN codes refused) and evaluate it with the engine's own Ctx and find_fires on a few coins and days, printing the first N fires with
the inputs named. No outcome is read. Reads lab days only from FIRST to LAST (warm-up days before FIRST are read for own_pct history,
never before SUPPORT_FIRST); refuses any day outside 20250910..20251231. Coins are the PRICE index names (BTC, not BTCUSDT; V6-14).

  python3 -B hc_defs_v2_to20251231.py --settings <settings file> DEF.json FIRST_DAY LAST_DAY COIN,COIN N INPUT,INPUT
Its memory before COUNT (half B, 8 days, at most 732 MB): hc_mem_probe_v1.py beside this file.

What changed from edition 1 (nothing else; its output is byte for byte the same):
  - the lab days are the settings file's LAB_DAYS (the settings file named on the command line); edition 1's optional LAB_ROOT and
    FORENSICS_ROOT arguments and its Mac defaults are gone;
  - the code (detect, the engine, lab3) and the metric gate's tables are read only inside the Alarm folder that holds this file (found by
    _tools/settings_v1.alarm_root), in its detection tree 01_Detection/tree/ (the dev tree's layout). The gate tables are edition 1's,
    the COUNT job's (KIT_V5 JOB_COUNT_V6): METRICS_V1, METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1, and the catalogues CTX, EPI,
    METRICS_HL_ADD_V1 and METRICS_HL_OWNER_CLEARED_LOOP2_V1; a missing one is refused;
  - Python packages: numpy, pyarrow and scipy (the engine's max ops), as settings/PYTHON_PACKAGES.txt lists them.
Exit 0 done; 1 edition 1's stops (USAGE, OUTSIDE_WINDOW, a refused definition); 2 refused here (settings, a missing table, outside an
Alarm folder)."""
import sys, os, datetime as dt
import numpy as np
FIRST = '20250910'; LAST = '20251231'; SUPPORT_FIRST = '20250820'
DETECTION_TREE = ('01_Detection', 'tree')
GATE = (('METRICS_V1', ('team/LAB3/METRICS_V1.tsv',)),
        ('METRIC_TRAPS', ('team/RESEARCH/LEAD/loop2/defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv',)),
        ('CATALOGS', ('team/RESEARCH/tools/alarm_context/CTX_CATALOG_V1.tsv', 'team/RESEARCH/tools/alarm_profile/EPI_CATALOG_V1.tsv',
                      'team/LAB3/METRICS_HL_ADD_V1.tsv', 'team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv')))
USAGE = 'USAGE hc_defs_v2_to20251231.py --settings SETTINGS DEF.json FIRST LAST COINS N INPUTS'


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


def detection_tree(start, S):
    """<Alarm>/01_Detection/tree of the Alarm folder that holds `start` (settings_v1.alarm_root)"""
    return os.path.join(S.alarm_root(start), *DETECTION_TREE)


def gate_env(F):
    """{METRICS_V1, METRIC_TRAPS, CATALOGS}: the metric gate's tables inside the detection tree F; a missing one is refused"""
    env, miss = {}, []
    for key, rels in GATE:
        paths = [os.path.join(F, *r.split('/')) for r in rels]
        miss += [p for p in paths if not os.path.isfile(p)]
        env[key] = ':'.join(paths)
    if miss:
        raise Refused('MISSING TABLE %s (the Alarm folder must hold it)' % ', '.join(miss))
    return env


def main(a):
    settings = None
    if len(a) >= 2 and a[0] == '--settings':
        settings, a = a[1], a[2:]
    if settings is None or len(a) != 6: raise SystemExit(USAGE)
    path, first, last, coins, nmax, show = a
    if not (FIRST <= first <= last <= LAST): raise SystemExit('OUTSIDE_WINDOW %s..%s (this tool reads %s..%s only)' % (first, last, FIRST, LAST))
    try:
        S = settings_module(__file__)
    except Refused as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    try:
        lab = S.get(settings, 'LAB_DAYS')
        F = detection_tree(__file__, S)
        env = gate_env(F)
    except (Refused, S.Refused) as e:
        print('REFUSED %s' % e, file=sys.stderr); return 2
    os.environ.update(env)
    sys.path.insert(0, os.path.join(F, 'team', 'RESEARCH', 'tools', 'idea_to_grade')); import detect as DT
    A = DT.engine(); src = A.LabSource(lab_root=lab, code_dir=os.path.join(F, 'team', 'LAB3', 'code'))
    d, info = DT.load_definition(path)
    print('PARSE OK', info['id'], info['sha16'], 'path', info['execution_path'], 'briefs', info['briefs'])
    keep = A.keep_days(d); hist = {}; last_fire = {}; n = 0; per = {}
    day = max(A.shift(first, -(keep + 1)), SUPPORT_FIRST)
    while day <= last:
        if not (SUPPORT_FIRST <= day <= LAST): raise SystemExit('OUTSIDE_WINDOW %s' % day)
        try: pc = set(src.coins(day))
        except Exception: pc = set()
        cs = [c for c in coins.split(',') if c in pc]
        if cs:
            ctx = A.Ctx(d, src, day, cs, hist); ctx.read_last = day
            fl, sh, cl, kn, side = A.find_fires(ctx, last_fire if day >= first else {})
            if day >= first:
                for i, r in fl:
                    n += 1; per[cs[i]] = per.get(cs[i], 0) + 1
                    if n <= int(nmax):
                        t = dt.datetime.fromtimestamp(ctx.t[r], dt.timezone.utc).strftime('%Y-%m-%d %H:%M')
                        vals = {k: (round(float(ctx.get(k)[i, r]), 6) if np.isfinite(ctx.get(k)[i, r]) else None) for k in show.split(',')}
                        print('FIRE', cs[i], t, 'side', int(side[i, r]), vals)
            ctx.push_hist(keep)
        day = A.shift(day, 1)
    days = (dt.datetime.strptime(last, '%Y%m%d') - dt.datetime.strptime(first, '%Y%m%d')).days + 1
    print('fires', n, 'per coin', per, 'fires a coin-day %.2f' % (n / max(1, days * len(coins.split(',')))))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
