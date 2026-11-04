#!/usr/bin/env python3
"""local_alloc.py: the job number allocator of local mode (stands in for a shared runner's allocator; standard Python only).

  python3 -B desk/local_alloc.py claim <RUN_SEAT> 1      prints one new job number (an integer), exit 0
  python3 -B desk/local_alloc.py list                    prints every number claimed so far

The numbers live in DESK_ALLOC_STATE (a TSV file the desk command sets: <OUTPUT_ROOT>/local_runner/ALLOC.tsv), one row per claim,
taken under an exclusive file lock, so two shells never get the same number. The first number is 1001. Without DESK_ALLOC_STATE it
refuses (exit 2): run jobs through `desk.py job`, which sets it."""
import datetime, fcntl, os, sys


def main(argv):
    st = os.environ.get('DESK_ALLOC_STATE', '')
    if not st or not os.path.isabs(st):
        print('REFUSED: DESK_ALLOC_STATE is not set (run jobs through desk/desk.py job)', file=sys.stderr)
        return 2
    if argv[:1] == ['list']:
        if os.path.isfile(st):
            sys.stdout.write(open(st).read())
        return 0
    if len(argv) != 3 or argv[0] != 'claim' or argv[2] != '1':
        print('usage: local_alloc.py claim <SEAT> 1 | list', file=sys.stderr)
        return 2
    os.makedirs(os.path.dirname(st), exist_ok=True)
    with open(st, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        rows = [l.split('\t') for l in f.read().splitlines() if l and not l.startswith('number')]
        n = max([int(r[0]) for r in rows] + [1000]) + 1
        if not rows:
            f.write('number\tseat\tutc\n')
        f.write('%d\t%s\t%s\n' % (n, argv[1], datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')))
        f.flush(); os.fsync(f.fileno())
        fcntl.flock(f, fcntl.LOCK_UN)
    print(n)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
