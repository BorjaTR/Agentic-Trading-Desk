"""fl_receipt_v1.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK; TEST, NOT REVIEWED): the end of a KIND FIRSTLOOK job: one row out of the reader's rule table
and one page for the agent. The table and its label column come from FIRSTLOOK_SETTINGS (the reader is a setting, so an edition 12 can swap in).
  python3 -B fl_receipt_v1.py <reader out dir> <rule file> <label column> <alarm id> <FULL|SEPDEC> <receipts dir> [--source <SEALED|RECEIPT_SHA16|UNSEALED> <job> <sha16>]
Writes <receipts>/<rule stem>_ROW.tsv (the header and the one row) and FIRST_LOOK.md. Exit 0 done, 2 refused (nothing written), 3 the label cannot be true.
A SEPDEC look has read no Jan-Apr outcome, so its label can only be NEEDS MORE MONTHS or NOT PASS: any other label is a fault of the chain.
Edition 12's table must hold edition 11's label too: the page shows both (GPT 10:30:53Z: labels are retrospective; a new label never replaces an old one nor becomes a reason for choosing an alarm)."""
import csv, hashlib, os, sys

s16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
SEPDEC_OK = ('NOT PASS', 'NEEDS MORE MONTHS')


class Refused(Exception):
    pass


def main(out, rule, col, aid, mode, dv, source=None):
    if mode not in ('FULL', 'SEPDEC'):
        raise Refused('MODE %r: FULL or SEPDEC' % mode)
    p = os.path.join(out, rule)
    if not os.path.isfile(p):
        raise Refused('NO RULE TABLE %s' % p)
    with open(p) as f:
        lines = f.read().split('\n')
    hdr = lines[0].split('\t')
    if col not in hdr or 'alarm_id' not in hdr:
        raise Refused('NO COLUMN %s OR alarm_id IN %s' % (col, rule))
    if col == 'RULE_12' and 'RULE_9' not in hdr:
        raise Refused('NO RULE_9 BESIDE RULE_12 IN %s: edition 11\'s label stays beside' % rule)
    rows = [l for l in lines[1:] if l]
    hit = [l for l in rows if l.split('\t')[hdr.index('alarm_id')] == aid]
    if len(rows) != 1 or len(hit) != 1:
        raise Refused('%s HOLDS %d ROWS, %d OF %s: one expected' % (rule, len(rows), len(hit), aid))
    d = dict(zip(hdr, hit[0].split('\t'))); lab = d[col]
    if lab == 'NOT RUN' or not lab:
        raise Refused('THE READER DID NOT RUN THE VARIANT: %s=%r' % (col, lab))
    if mode == 'SEPDEC' and not lab.startswith(SEPDEC_OK):
        print('FAULT a Sep-Dec look reads %s=%s' % (col, lab))
        return 3
    stem = rule[:-4] if rule.endswith('.tsv') else rule
    pr, pm = os.path.join(dv, stem + '_ROW.tsv'), os.path.join(dv, 'FIRST_LOOK.md')
    if os.path.exists(pr) or os.path.exists(pm):
        raise Refused('RECEIPT EXISTS %s' % dv)
    with open(pr, 'x') as f:
        f.write(lines[0] + '\n' + hit[0] + '\n')
    g = lambda k: d.get(k, '-') or '-'
    page = ['# First look of %s: %s = %s' % (aid, col, lab), '',
            'Months read: %s.' % ('Sep 2025 to Apr 2026' if mode == 'FULL' else 'Sep-Dec 2025 only; Jan-Apr not read, so NEEDS MORE MONTHS is the best this look can say'),
            'Table: %s %s, row %s.' % (rule, s16(p), stem + '_ROW.tsv')]
    if source:
        page.append('Source: %s, PERFIRE %s, %s.%s' % (source[1], source[2], source[0], ' The job left no record of this digest, so the source is not authenticated: it was pinned when the look was queued, not when its job ended.' if source[0] == 'UNSEALED' else ''))
    if col == 'RULE_12':
        page.append('Beside: RULE_9 (edition 11) = %s. Both labels are retrospective: RULE_12 uses the bar known then, on a busy population from the October 2026 table; it replaces no earlier label, is no reason an alarm was chosen, and is no strategy return.' % d['RULE_9'])
    page += ['',
            '| bar | period | pass | months | z | points | why not |', '|---|---|---|---|---|---|---|']
    for b, what in (('SIZE', "moves the moment's own B either way within 1 h" if col == 'RULE_12' else 'moves 4c either way within 1 h'), ('SIDE', 'lean wins the 1 h race')):
        for per in ('SepDec', 'JanApr'):
            k = '%s_%s' % (b, per)
            page.append('| %s (%s) | %s | %s | %s | %s | %s | %s |' % (b, what, per, g(k), g(k + '_months'), g(k + '_z'), g(k + '_pts'), g(k + '_fail')))
    page += ['', 'SIZE and SIDE are first look bars against equally busy random moments, not the +2c race of decide_v3 (R1, R2): read cards/first_look.md.', '']
    with open(pm, 'x') as f:
        f.write('\n'.join(page))
    print('FIRST LOOK %s %s %s=%s' % (aid, mode, col, lab))
    return 0


if __name__ == '__main__':
    try:
        a = sys.argv[1:]; src = None
        if len(a) == 10 and a[6] == '--source' and a[7] in ('SEALED', 'RECEIPT_SHA16', 'UNSEALED'):
            src = a[7:]; a = a[:6]
        if len(a) != 6:
            raise Refused('USAGE fl_receipt_v1.py <out> <rule file> <label column> <alarm id> <FULL|SEPDEC> <receipts> [--source <SEALED|RECEIPT_SHA16|UNSEALED> <job> <sha16>]')
        sys.exit(main(*a, source=src))
    except Refused as e:
        print('REFUSED %s' % e)
        sys.exit(2)
