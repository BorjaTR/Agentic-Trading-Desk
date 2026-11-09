#!/usr/bin/env python3
"""mech_cards_run_v1.py (SCO-A150 for SCOUT, 6 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED: never a PASS.
THE ONE COMMAND per mechanism (a runner job on real data): for every row of the alarm-list config it (1) uses the fixed draw named in
the row or runs the released alarm_match draw_v3 (PG20261106_alarm_match_lawpath edition, bytes unchanged) on the block's fires,
(2) runs readings_builder_v1 (released alarm_context build + read, playground out roots), rows in parallel, then (3) writes the final
config and runs alarm_cards_v1 -> <out>/ALARM_CARDS_<MECHANISM>.tsv and .md.
  python3 -B mech_cards_run_v1.py <new out dir> --mechanism <NAME> --config <ALARMS_<NAME>.tsv> --grades <GRADES.tsv>
      [--lab-days D] [--release R] [--edition E] [--jobs 4] [--cards-only <dir of a finished run>]  (cards-only: seconds, stored readings)
CONFIG columns: alarm, block, bundle, fires_list (the event list draw_v3 reads), draw (a draw dir, or NEW), def, def_sha16, grade_key.
Draw days: SEPDEC 20250918..20251231 (job 20270151's PRICE coverage: no PRICE part before 9 Sep 2025, first parent 9 days later),
JANMAR 20260101..20260331. Exit 0 written, 2 REFUSED, 3 FAILED, 5 a step failed (named in RUN_STEPS.tsv)."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, datetime as dt, os, subprocess, time

HERE = os.path.dirname(os.path.realpath(__file__))
DRAW_DAYS = {'SEPDEC': ('20250918', '20251231'), 'JANMAR': ('20260101', '20260331')}
BLOCKS = {'SEPDEC': ('20250910', '20251231'), 'JANMAR': ('20260101', '20260331')}


def day_of(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--mechanism', required=True)
    ap.add_argument('--config', required=True); ap.add_argument('--grades', default='')
    ap.add_argument('--lab-days', default='<DATA_ROOT>/lab_days'); ap.add_argument('--release', default='<RELEASE_ROOT>')
    ap.add_argument('--edition', default=os.path.join(HERE, '..', '..', 'PG20261106_alarm_match_lawpath', 'edition', '07_Price_path'))
    ap.add_argument('--jobs', type=int, default=4); ap.add_argument('--cards-only', default='')
    a = ap.parse_args(argv)
    t0 = time.time(); py = sys.executable
    os.makedirs(a.out, exist_ok=bool(a.cards_only))
    rows = list(csv.DictReader((l for l in open(a.config) if not l.startswith('#')), delimiter='\t'))
    lab3 = os.path.join(a.release, 'Alarm', 'alarm', 'current', '_vendor', 'LAB3_code')
    steps = []; final = []
    src = a.cards_only or a.out
    procs = []
    for r in rows:
        tag = '%s_%s' % (r['alarm'], r['block']); rd = os.path.join(src, 'RD_' + tag)
        final.append(dict(alarm=r['alarm'], block=r['block'], bundle=r['bundle'], readings=rd, def_=r['def'], def_sha16=r['def_sha16'],
                          grade_key=r['grade_key']))
        if a.cards_only:
            continue
        draw = r['draw']
        if draw == 'NEW':
            first, last = DRAW_DAYS[r['block']]; draw = os.path.join(a.out, 'draw_' + tag)
            par = os.path.join(a.out, 'PARENTS_%s.tsv' % tag)
            L = open(r['fires_list']).read().splitlines(); hdr = L[0].split('\t'); it = hdr.index('t')
            keep = [l for l in L[1:] if l and BLOCKS[r['block']][0] <= day_of(l.split('\t')[it]) <= BLOCKS[r['block']][1]]
            open(par, 'w').write('\n'.join([L[0]] + keep) + '\n')
            t1 = time.time()
            rc = subprocess.call([py, '-B', os.path.join(a.edition, 'tree', 'tools', 'alarm_match', 'draw_v3.py'), par, par, a.lab_days, draw, first, last],
                                 stdout=open(os.path.join(a.out, 'DRAW_%s.txt' % tag), 'w'), stderr=subprocess.STDOUT)
            steps.append((tag, 'draw', rc, round(time.time() - t1, 1), '%d parents %s..%s' % (len(keep), first, last)))
            if rc != 0:
                draw = ''
        cmd = [py, '-B', os.path.join(HERE, 'readings_builder_v1.py'), rd, '--fires', os.path.join(r['bundle'], 'FIRES.tsv'),
               '--first', BLOCKS[r['block']][0], '--last', BLOCKS[r['block']][1], '--lab-days', a.lab_days, '--lab3', lab3, '--release', a.release]
        if draw:
            cmd += ['--draw', draw]
        while len([p for p in procs if p[1].poll() is None]) >= a.jobs:
            time.sleep(2)
        procs.append((tag, subprocess.Popen(cmd, stdout=open(os.path.join(a.out, 'READINGS_%s.txt' % tag), 'w'), stderr=subprocess.STDOUT), time.time()))
    for tag, p, ts in procs:
        rc = p.wait(); steps.append((tag, 'readings', rc, round(time.time() - ts, 1), ''))
    cfg = os.path.join(a.out, 'CONFIG_FINAL_%s.tsv' % a.mechanism)
    with open(cfg, 'w') as f:
        f.write('alarm\tblock\tbundle\treadings\tdef\tdef_sha16\tgrade_key\n')
        for x in final:
            f.write('\t'.join((x['alarm'], x['block'], x['bundle'], x['readings'] if os.path.isdir(x['readings']) else '-', x['def_'], x['def_sha16'],
                               x['grade_key'])) + '\n')
    t1 = time.time()
    rc = subprocess.call([py, '-B', os.path.join(HERE, 'alarm_cards_v1.py'), a.out, '--mechanism', a.mechanism, '--config', cfg]
                         + (['--grades', a.grades] if a.grades else []),
                         stdout=open(os.path.join(a.out, 'CARDS_%s.txt' % a.mechanism), 'w'), stderr=subprocess.STDOUT)
    steps.append(('ALL', 'cards', rc, round(time.time() - t1, 1), ''))
    with open(os.path.join(a.out, 'RUN_STEPS%s.tsv' % ('_CARDS_ONLY' if a.cards_only else '')), 'w') as f:
        f.write('tag\tstep\trc\tseconds\tnote\n'); [f.write('\t'.join(str(v) for v in s) + '\n') for s in steps]
    print('STEPS', steps); print('WALL %.1f s' % (time.time() - t0))
    return 0 if all(s[2] == 0 for s in steps) else 5


if __name__ == '__main__':
    sys.exit(main())
