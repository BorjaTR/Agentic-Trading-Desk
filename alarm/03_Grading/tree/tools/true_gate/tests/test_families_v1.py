#!/usr/bin/env python3
"""the family table rebuilds from the package's own metric tables, equal to the shipped file; planted rows: a code with no rule is UNKNOWN, a twin takes its base's family; the examples the rule rests on hold."""
import filecmp, importlib.util, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(HERE, '..')
sp = importlib.util.spec_from_file_location('bf', os.path.join(T, 'build_families_v1.py')); B = importlib.util.module_from_spec(sp); sp.loader.exec_module(B)
d = tempfile.mkdtemp(); p = os.path.join(d, 'S.tsv'); B.main(p)
assert filecmp.cmp(p, os.path.join(T, 'SOURCE_FAMILIES_V1.tsv'), shallow=False), 'the shipped table differs from a rebuild'
assert B.classify('NO.SUCH')[2] == 'UNKNOWN'; assert B.classify('A6.S01')[2] == 'UNKNOWN'
assert B.classify('E2.S02.any_age_off')[0] == B.classify('E2.S02')[0] == B.classify('E2.S04')[0] == 'OI_BN'
assert 'LIQ_BN' in B.classify('X1.LIQX.S01')[0] and B.classify('A1.S01')[0] == 'LIQ_BN'
assert B.classify('C2.S06')[1] == 1 and B.classify('E3.S01')[1] == 1
assert B.classify('E2.S06')[0] == 'HL_POS' and 'HL_POS' in B.classify('X1.HLFLOWX.S09')[0] and B.classify('X1.HLPOSX.S01')[0] == 'HL_POS'
assert not B.classify('B1.S03')[1]
print('PASS families')
