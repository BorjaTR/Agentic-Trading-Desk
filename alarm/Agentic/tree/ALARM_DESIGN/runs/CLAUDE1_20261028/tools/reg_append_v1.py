# reg_append_v1.py (CLAUDE1_20261028, 28 Oct 2026). TEST, NOT REVIEWED. Reads no market data (registers only; no date range).
# Appends ONE row to a run register, append-only, the utc stamp taken from the clock inside this call (L9).
# Usage: python3 -B reg_append_v1.py <RUN_DIR> <REGISTER e.g. THOUGHTS> <FIELDS.json | ->   (a JSON object: column -> text)
# Rules: the register file must exist with a header; every key must be a header column; the first column (utc...) is filled from
# the clock and must not be given; values may not hold a tab, a newline or an em dash; unknown keys or an empty row are refused.
# Missing columns are written empty. Prints the stamp. Never rewrites the file (opens in append mode only).
import sys, os, json, datetime
def main(a):
    if len(a) != 3:
        raise SystemExit('USAGE reg_append_v1.py RUN_DIR REGISTER FIELDS.json|-')
    run, reg, src = a
    p = os.path.join(run, 'registers', reg + '.tsv')
    if not os.path.isfile(p):
        raise SystemExit('NO REGISTER ' + p)
    with open(p) as f:
        hdr = f.readline().rstrip('\n').split('\t')
    if not hdr or not hdr[0].startswith('utc'):
        raise SystemExit('BAD HEADER ' + p)
    txt = sys.stdin.read() if src == '-' else open(src).read()
    d = json.loads(txt)
    if not isinstance(d, dict) or not d:
        raise SystemExit('EMPTY ROW')
    bad = [k for k in d if k not in hdr]
    if bad:
        raise SystemExit('UNKNOWN COLUMNS %s; header %s' % (bad, hdr))
    if hdr[0] in d:
        raise SystemExit('THE STAMP COMES FROM THE CLOCK: do not give ' + hdr[0])
    for k, v in d.items():
        v = str(v)
        if '\t' in v or '\n' in v or '\r' in v:
            raise SystemExit('TAB OR NEWLINE IN ' + k)
        if '—' in v:
            raise SystemExit('EM DASH IN ' + k)
    with open(p, 'rb') as f:
        f.seek(0, 2)
        n = f.tell()
        if n:
            f.seek(n - 1)
            last = f.read(1)
        else:
            last = b'\n'
    st = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    row = [st] + [str(d.get(k, '')) for k in hdr[1:]]
    with open(p, 'a') as f:
        if last != b'\n':
            f.write('\n')
        f.write('\t'.join(row) + '\n')
    print(st, reg)
if __name__ == '__main__':
    main(sys.argv[1:])
