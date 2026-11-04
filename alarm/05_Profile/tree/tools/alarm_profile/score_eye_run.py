"""tools/alarm_profile: score SCOUT's P4_EYE_RUN answers against the key (QUANT 22 Oct 2026). The key (EYE_RUN_KEY.tsv: chart, coin, t,
group FRESH, or CHANGED = MOVED: alarms whose run start the new rule moved) is read only here, after the answers are filed. NO and UNSURE
are not YES. Lines (PROOFS_V1 P4_EYE_RUN):
  v3   (J471130 sample): YES on >= 11 of the 12 FRESH charts and >= 3 of the 4 CHANGED ones
  v3b  (the owner 15:3x Berlin, set before the draw): 12 FRESH charts, YES on >= 9 and NO on <= 1
Writes the result rows (value, proof, result, receipt, utc) for the 10 values that rest on the run start.
  python3 -B score_eye_run.py <answers tsv: chart, answer, note> <key tsv> <receipt text> <out rows tsv> <line: v3 | v3b>"""
import csv, datetime as dt, sys
VALUES = ('run_pct', 'run_norm', 'run_age_min', 'run_capped', 'pre_move_pct', 'forced_share', 'giveback_pct', 'giveback_share',
          'pre_speed_pct_min', 'speed_ratio')
GROUP = {'FRESH': 'FRESH', 'CHANGED': 'MOVED', 'MOVED': 'MOVED'}


def rows(p):
    return csv.DictReader((l for l in open(p) if not l.startswith('#')), delimiter='\t')      # '#' lines are notes


def main(answers, key, receipt, out, line):
    a = {int(r['chart']): r['answer'].strip().upper() for r in rows(answers)}
    k = {int(r['chart']): r for r in rows(key)}
    miss = sorted(set(k) - set(a))
    if miss:
        raise SystemExit('answers missing for charts %s: nothing scored' % miss)
    n = {g: {'YES': 0, 'NO': 0, 'UNSURE': 0, 'ALL': 0} for g in ('FRESH', 'MOVED')}
    for c, r in sorted(k.items()):
        g = n[GROUP[r['group']]]; g['ALL'] += 1; g[a[c] if a[c] in ('YES', 'NO') else 'UNSURE'] += 1
        print('chart %2d %-6s %-6s %-6s %s' % (c, r['coin'], GROUP[r['group']], a[c], r['t']))
    F, M = n['FRESH'], n['MOVED']
    if line == 'v3':
        ok = F['ALL'] == 12 and F['YES'] >= 11 and M['ALL'] == 4 and M['YES'] >= 3
    elif line == 'v3b':
        ok = F['ALL'] == 12 and M['ALL'] == 0 and F['YES'] >= 9 and F['NO'] <= 1
    else:
        raise SystemExit('unknown line %s' % line)
    res = 'PASS' if ok else 'FAIL'
    txt = 'FRESH %d of %d YES, %d UNSURE, %d NO; MOVED %d of %d YES' % (F['YES'], F['ALL'], F['UNSURE'], F['NO'], M['YES'], M['ALL'])
    print('P4 EYE RUN line %s: %s: %s' % (line, txt, res))
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(out, 'x') as f:
        f.write('value\tproof\tresult\treceipt\tutc\n')
        for v in VALUES:
            f.write('%s\tP4_EYE_RUN\t%s\t%s, line %s: %s\t%s\n' % (v, res, receipt, line, txt, now))
    return res


if __name__ == '__main__':
    main(*sys.argv[1:6])
