"""tests for messy_triage_v1.py (C171): a planted register and series folder; each class must come out exactly once."""
import os, subprocess, sys, tempfile, csv
HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(HERE, 'messy_triage_v1.py')
def test():
    d = tempfile.mkdtemp(prefix='triage_', dir=os.environ.get('LL_TEST_TMP', '<SCRATCH_DISK>/tmp_SCOUT')); reg = os.path.join(d, 'reg'); ser = os.path.join(d, 'ser')
    os.makedirs(reg); os.makedirs(os.path.join(ser, 'lean_v1'))
    open(os.path.join(ser, 'lean_v1', 'HUNTER_RULES_V2.md'), 'w').write('R2 split plan: cut at the wave first-fire median.\nOther text.\n')
    cols = ['mess_id', 'utc', 'found_by', 'file', 'line_quoted', 'kind', 'fix', 'fixed_in', 'status']
    rows = [['M1', 'u', 'a', '-', 'x', 'missing', 'f', '-', 'open'],
            ['M2', 'u', 'a', 'drills_v2/GOLDEN/K1/key/KEY.md', '"some key words here"', 'unclear', 'f', '-', 'open'],
            ['M3', 'u', 'a', 'BASE/RUN_PROMPT.md', '"old stale line words"', 'stale', 'f', '-', 'open'],
            ['M4', 'u', 'a', 'drills_v2/GOLDEN/K1/NEW/HUNTER_RULES.md', '"cut at the wave first-fire median"', 'unclear', 'f', '-', 'open'],
            ['M5', 'u', 'a', 'lean_v1/HUNTER_RULES_V2.md', '"a sentence that was removed later"', 'unclear', 'f', '-', 'open'],
            ['M6', 'u', 'a', 'lean_v1/HUNTER_RULES_V2.md', '"short"', 'unclear', 'f', '-', 'open'],
            ['M7', 'u', 'a', 'lean_v1/HUNTER_RULES_V2.md', '"cut at the wave first-fire median"', 'unclear', 'f', '-', 'fixed'],
            ['M8', 'u', 'a', 'not/here.md', '"a line in a file that is not there"', 'stale', 'f', '-', 'open']]   # C218 B3
    with open(os.path.join(reg, 'MESSY.tsv'), 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n'); w.writerow(cols); w.writerows(rows)
    p = subprocess.run([sys.executable, '-B', T, '--registers', reg, '--series', ser], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    got = {r['mess_id']: r['class'] for r in csv.DictReader(open(os.path.join(reg, 'MESSY_TRIAGE.tsv')), delimiter='\t')}
    assert got == {'M1': 'NO_FILE', 'M2': 'DRILL_MATERIAL', 'M3': 'REPLACED_FILE', 'M4': 'QUOTE_PRESENT', 'M5': 'QUOTE_GONE', 'M6': 'NO_QUOTE', 'M8': 'NO_LIVE_FILE'}, got
    assert 'TRIAGE open 7' in p.stdout, p.stdout
    import shutil; shutil.rmtree(d); print('PASS 8 planted lines (7 open, 1 fixed skipped)')
if __name__ == '__main__':
    test()
