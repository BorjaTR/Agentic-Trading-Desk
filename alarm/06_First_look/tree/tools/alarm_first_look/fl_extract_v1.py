"""fl_extract_v1.py (SCOUT 30 Oct 2026, tools/alarm_first_look; md_extract_v1.py of tools/money_direction widened). TEST, NOT REVIEWED.
Keeps the named label columns of one wide outcome table (night_export_v3.py of an event_outcomes_aw1 run), their seconds for the timed
kinds (OBH, REACH), the tool's own c per event (unit__c), and joins the event list's side:
  python3 -B fl_extract_v1.py <X_wide.tsv> <events.tsv> <out.tsv.gz> <LABEL,LABEL,...>
Out columns: coin, t, side, unit__c, then per label L and direction D in (FADE, FOLLOW): L__D, L__D__why, and L__D__t for OBH / REACH.
Refuses (exit 2, nothing written): an existing out file; an event missing from the table or a row missing from the list; a repeated
(coin, t); as_of_us not a whole second; any time at or after 1 May 2026 00:00Z; a missing column; a bad label name."""
import csv, gzip, os, re, sys

DIRS = ('FADE', 'FOLLOW')
T1 = 1777593600


def refuse(why):
    print('REFUSED ' + why)
    sys.exit(2)


def main(xp, ep, outp, labels):
    if os.path.exists(outp) or os.path.exists(outp + '.part'):
        refuse('OUTPUT EXISTS %s' % outp)
    labels = labels.split(',')
    if not labels or len(set(labels)) != len(labels) or not all(re.fullmatch(r'(RET|BEST|WORST|OBH4|REACH4)_[0-9]+M', l) for l in labels):
        refuse('BAD LABELS %s' % labels)
    ev = {}
    with open(ep) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            k = (r['coin'], int(r['t']))
            if k in ev:
                refuse('REPEATED EVENT %s %d' % k)
            if k[1] >= T1:
                refuse('MAY EVENT %s %d' % k)
            ev[k] = int(r['side'])
    cols = []
    for l in labels:
        for d in DIRS:
            cols += [l + '__' + d, l + '__' + d + '__why'] + ([l + '__' + d + '__t'] if l.startswith(('OBH', 'REACH')) else [])
    want = ['unit__c'] + cols
    rows = {}
    with open(xp) as f:
        rd = csv.reader(f, delimiter='\t'); h = next(rd); ix = {c: i for i, c in enumerate(h)}
        for c in ['coin', 'as_of_us'] + want:
            if c not in ix:
                refuse('MISSING COLUMN %s' % c)
        for r in rd:
            us = int(r[ix['as_of_us']])
            if us % 1000000:
                refuse('AS_OF_US NOT A WHOLE SECOND %s %d' % (r[ix['coin']], us))
            k = (r[ix['coin']], us // 1000000)
            if k in rows:
                refuse('REPEATED ROW %s %d' % k)
            if k[1] >= T1:
                refuse('MAY ROW %s %d' % k)
            rows[k] = [r[ix[c]] for c in want]
    miss = [k for k in ev if k not in rows]; extra = [k for k in rows if k not in ev]
    if miss or extra:
        refuse('LIST AND TABLE DIFFER: %d events without a row, %d rows without an event' % (len(miss), len(extra)))
    keys = sorted(ev, key=lambda k: (k[1], k[0]))
    with gzip.open(outp + '.part', 'wt') as g:
        g.write('\t'.join(['coin', 't', 'side'] + want) + '\n')
        for k in keys:
            g.write('\t'.join([k[0], str(k[1]), str(ev[k])] + rows[k]) + '\n')
    os.rename(outp + '.part', outp)
    filled = sum(1 for k in keys if rows[k][want.index(labels[0] + '__FADE')] != '')
    print('events %d | %s__FADE values %d | columns %d -> %s' % (len(keys), labels[0], filled, len(want) + 3, outp))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        refuse('USAGE fl_extract_v1.py <X_wide.tsv> <events.tsv> <out.tsv.gz> <LABELS>')
    main(*sys.argv[1:5])
