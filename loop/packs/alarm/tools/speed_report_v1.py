#!/usr/bin/env python3
"""speed_report_v1.py (SCOUT 2026-11-08; drill SPEED for part P34; why: team/RESEARCH/plans/PLAN_PROCESS_QUALITY_SYSTEM_20261108.md,
the owner 09:19Z "speed should be in the scorecard"). Reads only logs that already exist:
  runs: runs_v2/<run>/ops/LAUNCH_UTC.txt (launch) and the first line of work/RESULT_<run>.md ("DONE <utc>") -> run minutes; MAC_JOBS rows
  drills: drills_v2/registers/DRILL_RUNS.tsv minutes per drill_id -> median per drill and per part (PARTS.tsv drills + DRILLS.tsv parts)
  steps (C230, L11 K41): per run, launch -> R1 seal (R0) and each round from its first sealed FORECASTS utc to the next round's (R3 and R3P sealed together: one step), the last to DONE
Targets (PROCESS_IMPROVEMENT and the Process quality system doc): run <= 40 min, round <= 10 min, drill <= 5 min.
C230: a drill, part or step with no numeric minutes prints "no data" (was a crash: no median for empty data, L11).
Writes --out TSV (kind, id, n, median_min, target_min, within) and prints a summary.  python3 -B speed_report_v1.py --out <tsv> [--runs L07,L08,L09] [--root <series folder>]"""
import argparse, csv, glob, os, re, statistics, sys
from datetime import datetime
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE); REG = os.path.join(S, 'drills_v2', 'registers')
T_RUN, T_DRILL, T_ROUND = 40.0, 5.0, 10.0

def med(v):   # C230: None for no data (statistics.median raises on [])
    return statistics.median(v) if v else None

def mrow(kind, k, v, target, note):
    md = med(v)
    if md is None: return (kind, k, 0, 'no data', target, '-', note)
    return (kind, k, len(v), round(md, 1), target, 'yes' if md <= target else 'no', note)

def utc(s):
    return datetime.strptime(s[:20], '%Y-%m-%dT%H:%M:%SZ')

def run_minutes(run):
    d = os.path.join(S, 'runs_v2', run)
    try:
        start = utc(open(os.path.join(d, 'ops', 'LAUNCH_UTC.txt')).read().strip())
        res = sorted(glob.glob(os.path.join(d, 'work', 'RESULT_*.md')))
        m = re.match(r'DONE (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)', open(res[-1]).readline()) if res else None
        if not m: return None, 'no DONE line'
        mins = (utc(m.group(1)) - start).total_seconds() / 60
        return mins, ('includes a stop over 60 min: not hunter time' if mins > 300 else '')
    except (OSError, ValueError, IndexError) as e:
        return None, 'missing %s' % e.__class__.__name__

def step_minutes(run):
    """C230: [(step, minutes or None)]: R0 = launch to the first sealed row; each round = its first seal to the next distinct seal, the last to DONE"""
    d = os.path.join(S, 'runs_v2', run); out = []
    try: start = utc(open(os.path.join(d, 'ops', 'LAUNCH_UTC.txt')).read().strip())
    except (OSError, ValueError): start = None
    seal = {}
    try:
        for r in csv.reader(open(os.path.join(d, 'work', 'FORECASTS.tsv')), delimiter='\t'):
            if len(r) > 1 and r[0] and not r[0].startswith('#') and r[0] != 'round':
                try: seal.setdefault(r[1][:20], []).append(r[0])
                except ValueError: pass
    except OSError: pass
    res = sorted(glob.glob(os.path.join(d, 'work', 'RESULT_*.md'))); done = None
    if res:
        m = re.match(r'DONE (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)', open(res[-1]).readline())
        done = utc(m.group(1)) if m else None
    ts = []
    for u in sorted(seal):
        try: ts.append((utc(u), '/'.join(dict.fromkeys(seal[u]))))
        except ValueError: pass
    if not ts: return [('rounds', None)]
    out.append(('R0 (launch to R1 seal)', (ts[0][0] - start).total_seconds() / 60 if start else None))
    for i, (t0, name) in enumerate(ts):
        t1 = ts[i + 1][0] if i + 1 < len(ts) else done
        out.append((name, (t1 - t0).total_seconds() / 60 if t1 else None))
    return out

def main(argv=None):
    global S, REG
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--runs', default=''); ap.add_argument('--root', default='')
    a = ap.parse_args(argv); rows = []
    if a.root: S = os.path.abspath(a.root); REG = os.path.join(S, 'drills_v2', 'registers')
    runs = a.runs.split(',') if a.runs else sorted(os.path.basename(p) for p in glob.glob(os.path.join(S, 'runs_v2', '[LC][0-9][0-9]')))
    for r in runs:
        m, note = run_minutes(r)
        if m is not None: rows.append(('run', r, 1, round(m, 1), T_RUN, 'yes' if m <= T_RUN else 'no', note))
        for st, sm in step_minutes(r):
            rows.append(mrow('step', '%s:%s' % (r, st), [sm] if sm is not None else [], T_ROUND, ''))
    dr = list(csv.DictReader(open(os.path.join(REG, 'DRILL_RUNS.tsv')), delimiter='\t'))
    by = {}
    for r in dr:
        v = by.setdefault(r['drill_id'], [])   # C230: a drill with only non-numeric minutes keeps [] -> 'no data' (L11 crash)
        try: v.append(float(r['minutes']))
        except (ValueError, TypeError): pass
    for k, v in sorted(by.items()):
        rows.append(mrow('drill', k, v, T_DRILL, ''))
    parts = list(csv.DictReader(open(os.path.join(REG, 'PARTS.tsv')), delimiter='\t'))
    dcat = list(csv.DictReader(open(os.path.join(REG, 'DRILLS.tsv')), delimiter='\t')) if os.path.exists(os.path.join(REG, 'DRILLS.tsv')) else []
    for p in parts:
        ids = {x for x in p['drills'].split(',') if x} | {d['drill_id'] for d in dcat if p['part_id'] in d['parts'].split(',')}
        v = [x for k in ids for x in by.get(k, [])]
        if ids: rows.append(mrow('part', p['part_id'], v, T_DRILL, p['name']))
    with open(a.out, 'w') as f:
        f.write('kind\tid\tn\tmedian_min\ttarget_min\twithin\tnote\n')
        for r in rows: f.write('\t'.join(str(x) for x in r) + '\n')
    rr = [r for r in rows if r[0] == 'run' and not r[6]]
    print('RUNS %s' % ' '.join('%s %.1f min (%s)' % (r[1], r[3], 'ok' if r[5] == 'yes' else 'over') for r in rows if r[0] == 'run'))
    print('DRILLS %d, within 5 min %d; PARTS with drill minutes %d, within %d' % (
        sum(1 for r in rows if r[0] == 'drill'), sum(1 for r in rows if r[0] == 'drill' and r[5] == 'yes'),
        sum(1 for r in rows if r[0] == 'part'), sum(1 for r in rows if r[0] == 'part' and r[5] == 'yes')))
    if rr: print('RUN median (clean runs) %.1f min, target %.0f' % (statistics.median([r[3] for r in rr]), T_RUN))
    st = [r for r in rows if r[0] == 'step']
    if st: print('STEPS %s' % '; '.join('%s %s' % (r[1], r[3] if r[3] == 'no data' else '%.1f min (%s)' % (r[3], 'ok' if r[5] == 'yes' else 'over')) for r in st))
    nd = [r[1] for r in rows if r[3] == 'no data']
    if nd: print('NO DATA %d: %s' % (len(nd), ' '.join(nd)))
    print('WROTE', a.out); return 0

if __name__ == '__main__':
    sys.exit(main())
