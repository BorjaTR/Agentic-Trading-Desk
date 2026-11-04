#!/usr/bin/env python3
"""build_families_v1.py (SCOUT playground, TEST, NOT REVIEWED). Writes SOURCE_FAMILIES_V1.tsv: for every code of METRICS_V1 and the
owner-cleared Hyperliquid table, the raw source families it reads, whether it is price-derived, and how sure that is.
status CARD = the family's card names its source stream (the card path and its source line are in the row).
status GUESS = the producer card has no source field: the family is read from the code's own meaning line. Reported, never hidden.
status UNKNOWN = no reviewed card or no source: the gate refuses the code.
Rules are by hand, from the cards: a code with no rule is UNKNOWN (a new code is refused until someone adds it here)."""
import csv, os, re, sys

HERE = os.path.dirname(os.path.realpath(__file__)); REL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))   # the Alarm folder
METRICS = REL + '/01_Detection/tree/team/LAB3/METRICS_V1.tsv'
HL = REL + '/01_Detection/tree/team/RESEARCH/LEAD/loop2/defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv'

# family prefix -> (families, price_derived, status). Source lines read from each card by the census of 2 Nov 2026.
FAM = {
 'A1': ('LIQ_BN', 0, 'CARD'), 'A2': ('LIQ_BN', 0, 'CARD'), 'A4': ('LIQ_BN', 0, 'CARD'),
 'A5': ('LIQ_BN|TRADES_BN', 0, 'CARD'), 'A7': ('OI_BN|LIQ_BN', 0, 'CARD'), 'COIN_C2': ('LIQ_BN|OI_BN', 0, 'CARD'),
 'B1': ('TRADES_BN', 0, 'CARD'), 'B2': ('TRADES_BN', 0, 'CARD'), 'B3': ('TRADES_BN', 0, 'CARD'),
 'C12': ('BOOK_BN', 0, 'CARD'), 'D1': ('BOOK_BN', 0, 'CARD'), 'D3': ('BOOK_BN', 0, 'CARD'), 'D4': ('BOOK_BN', 0, 'CARD'),
 'D2': ('BOOK_BN', 1, 'CARD'), 'D5': ('BOOK_BN', 0, 'CARD'),
 'E1': ('FUNDING_BN', 0, 'CARD'), 'E3': ('MARK_BN', 1, 'CARD'),
 'C1': ('PRICE', 1, 'CARD'), 'C2': ('PRICE', 1, 'CARD'), 'C3': ('PRICE', 1, 'CARD'), 'C4': ('PRICE', 1, 'CARD'), 'C5': ('PRICE', 1, 'CARD'),
 'C6': ('PRICE', 1, 'CARD'), 'C7': ('PRICE', 1, 'CARD'), 'C8': ('PRICE', 1, 'CARD'), 'C9': ('PRICE', 1, 'CARD'), 'C10': ('PRICE', 1, 'CARD'),
 'C11': ('PRICE', 1, 'CARD'), 'C13': ('PRICE', 1, 'CARD'), 'COIN_C3': ('PRICE', 1, 'CARD'), 'NAUTILUS': ('PRICE', 1, 'CARD'),
 'Z1': ('CALENDAR', 0, 'CARD'), 'Z3': ('CALENDAR', 0, 'CARD'), 'Z2': ('NEWS', 0, 'CARD'),
 'X1.LIQX': ('LIQ_BN', 0, 'GUESS'), 'X1.FLOWX': ('TRADES_BN', 0, 'GUESS'), 'X1.BOOKX': ('BOOK_BN', 0, 'GUESS'), 'X1.COST': ('BOOK_BN', 0, 'GUESS'),
 'X1.RETX': ('PRICE', 1, 'GUESS'), 'X1.TIMEX': ('PRICE', 1, 'GUESS'), 'X1.CALX': ('CALENDAR', 0, 'GUESS'),
 'X1.HLFLOWX': ('HL_FILLS', 0, 'GUESS'), 'X1.HLPOSX': ('HL_POS', 0, 'GUESS'), 'X1.HLPOSM': ('HL_POS|HL_FILLS', 0, 'GUESS'),
 'X1.HLLIQX': ('HL_FILLS', 0, 'GUESS'), 'X1.HLPX': ('PRICE', 1, 'GUESS'),
}
# one code differs from its family: the card or meaning line says so
CODE = {
 'E2.S01': ('OI_BN', 0, 'CARD'), 'E2.S02': ('OI_BN', 0, 'CARD'), 'E2.S03': ('OI_BN', 0, 'CARD'), 'E2.S04': ('OI_BN', 0, 'CARD'), 'E2.S07': ('OI_BN', 0, 'CARD'),
 'E2.S05': ('HL_POS', 0, 'CARD'), 'E2.S06': ('HL_POS', 0, 'CARD'),
 'X1.LIQX.S03': ('LIQ_BN|OI_BN', 0, 'GUESS'), 'X1.LIQX.S04': ('LIQ_BN|OI_BN', 0, 'GUESS'),
 'X1.BOOKX.S01': ('BOOK_BN', 1, 'GUESS'), 'X1.BOOKX.S09': ('BOOK_BN', 1, 'GUESS'), 'X1.BOOKX.S10': ('BOOK_BN', 1, 'GUESS'),
 'X1.POSX.S01': ('FUNDING_BN', 0, 'GUESS'), 'X1.POSX.S02': ('FUNDING_HL', 0, 'GUESS'), 'X1.POSX.S03': ('FUNDING_BN', 0, 'GUESS'), 'X1.POSX.S04': ('FUNDING_BN', 0, 'GUESS'),
 'X1.POSX.S05': ('FUNDING_BN|FUNDING_HL', 0, 'GUESS'), 'X1.POSX.S06': ('MARK_BN', 1, 'GUESS'), 'X1.POSX.S07': ('MARK_BN', 1, 'GUESS'), 'X1.POSX.S08': ('MARK_BN', 1, 'GUESS'),
 'X1.POSX.S09': ('OI_BN|TRADES_BN', 0, 'GUESS'), 'X1.POSX.S10': ('OI_BN|TRADES_BN', 0, 'GUESS'), 'X1.POSX.S11': ('OI_BN|PRICE', 1, 'GUESS'),
 'X1.POSX.S12': ('OI_BN', 1, 'GUESS'), 'X1.POSX.S13': ('TOPTRADER_BN', 0, 'GUESS'), 'X1.POSX.S14': ('TRADES_BN', 0, 'GUESS'),
 'X1.VOLX.S01': ('TRADES_BN', 0, 'GUESS'),
}
for i in range(7, 12):
    CODE['X1.HLFLOWX.S%02d' % i] = ('HL_FILLS|HL_POS', 0, 'GUESS')   # opened and closed dollars are Hyperliquid positions moving: the same family as its open interest
for i in range(2, 22):
    CODE['X1.VOLX.S%02d' % i] = ('DVOL', 1, 'GUESS') if i in (7, 8, 9) else ('PRICE', 1, 'GUESS')


def base(code):
    """E2.S02.any_age_off, A7.S05.coverage -> their base code"""
    m = re.match(r'^(.*?\.S\d+)(\..*)?$', code)
    return m.group(1) if m else code


def classify(code):
    b = base(code)
    if b in CODE:
        return CODE[b]
    pre = b.split('.S')[0] if '.S' in b else b
    return FAM.get(pre, ('UNKNOWN', 0, 'UNKNOWN'))


def rows():
    seen = {}
    for path in (METRICS, HL):
        for r in csv.DictReader((l for l in open(path) if not l.startswith('#')), delimiter='\t'):
            seen.setdefault(r['code'], r)
    return seen


def main(out):
    n = {}
    with open(out + '.part', 'w') as f:
        f.write('code\tfamilies\tprice_derived\tstatus\tcard\tmeaning\n')
        for code, r in sorted(rows().items()):
            fam, px, st = classify(code)
            n[st] = n.get(st, 0) + 1
            mean = (r.get('meaning') or '')[:90].replace('\t', ' ')
            card = r.get('card', ''); card = card[card.index('team/'):] if 'team/' in card else card
            f.write('\t'.join([code, fam, str(px), st, card, mean]) + '\n')
    os.replace(out + '.part', out)
    print('WROTE', out, n)


if __name__ == '__main__':
    main(sys.argv[1])
