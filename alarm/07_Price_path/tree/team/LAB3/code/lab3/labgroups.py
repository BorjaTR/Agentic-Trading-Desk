"""lab3/labgroups.py (LAB2, 19 Oct 2026; kanban 4.41). Standard Python only (rows.py reads it in the VM). The LAB kind's groups:
LAB = the lab's own readings as lab_v2 holds them (days/<D>/lab_LAB.tsv, kanban 4.8); LABTOP = the 4 codes split from the 2 text
readings '<COIN> <dollars>' (LAB1 21:16:50Z: over the grid's 32,767 words), days/<D>/lab_LABTOP.tsv, added to built days later with
nothing of LAB moved or rebuilt (the x1 way). Tests: tests/test_lab_top_split_v1.py."""
GROUPS = ('LAB', 'LABTOP')
TOP_SPLIT = ('other_coins_long_top', 'other_coins_short_top')
DERIVED = {b + s: (b, s[1:]) for b in TOP_SPLIT for s in ('_coin', '_usd')}    # name -> (text reading, 'coin' or 'usd')

def lab_group(code):
    """LAB.<name> -> 'LABTOP' for a split code, else 'LAB'"""
    return 'LABTOP' if code[4:] in DERIVED else 'LAB'

def codes_of(group):
    """the codes a group always holds when given no list: LABTOP its 4 split codes; LAB has none fixed (the catalog's)"""
    if group not in GROUPS:
        raise ValueError('a LAB group is LAB or LABTOP, not %r' % (group,))
    return sorted('LAB.' + n for n in DERIVED) if group == 'LABTOP' else []
