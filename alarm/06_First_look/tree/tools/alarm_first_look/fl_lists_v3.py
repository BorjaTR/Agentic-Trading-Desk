"""fl_lists_v3.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK; TEST, NOT REVIEWED): the two lists of ONE variant from its own PERFIRE, for KIND FIRSTLOOK.
fl_lists_v2.py's rows and file formats; what differs: one variant (no MD batch), the window is an argument (no date in the code), the fires are
checked against the job's own fire list when given, and bad rows are refused, not skipped.
  python3 -B fl_lists_v3.py <PERFIRE.tsv> <V> <lean> <alarm id> <first YYYYMMDD> <last YYYYMMDD> <H> <out dir (new)> [--fires <list.tsv>] [--code <code>]
Kind A rows are the fires, kind R the grade's 3 matched random moments with their weights w. Rows outside first..last are dropped and counted.
<code> names the files and defaults to V. perfire in TARGETS_FL.tsv is relative to H (fl_read joins it to H).
Writes <out>/A_<code>_EVENTS.tsv, R_<code>_EVENTS.tsv, R_<code>_W.tsv, TARGETS_FL.tsv, BUILD.txt. Exit 0 done, 2 refused (nothing published)."""
import calendar, csv, datetime as dt, hashlib, math, os, re, sys

NAME = re.compile(r'^[A-Za-z0-9]+$')
s16 = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


class Refused(Exception):
    pass


def day_t(d):
    try:
        return calendar.timegm(dt.datetime.strptime(d, '%Y%m%d').timetuple())
    except (ValueError, TypeError):
        raise Refused('BAD DATE %r' % (d,))


def read_perfire(path, t0, t1):
    A, R, out = [], [], 0
    with open(path) as f:
        rd = csv.DictReader(f, delimiter='\t')
        miss = [k for k in ('kind', 'coin', 't', 'side', 'w') if k not in (rd.fieldnames or [])]
        if miss:
            raise Refused('PERFIRE COLUMNS MISSING %s' % miss)
        for x in rd:
            try:
                t, side = int(x['t']), int(x['side'])
            except (ValueError, TypeError):
                raise Refused('BAD ROW t=%r side=%r' % (x['t'], x['side']))
            if side not in (-1, 0, 1):
                raise Refused('BAD SIDE %r' % x['side'])
            if not t0 <= t < t1:
                out += 1; continue
            if x['kind'] == 'A':
                A.append((x['coin'], t, side))
            elif x['kind'] == 'R':
                try:
                    w = float(x['w'])
                except (ValueError, TypeError):
                    raise Refused('BAD WEIGHT %r' % x['w'])
                if not math.isfinite(w) or w < 0:
                    raise Refused('BAD WEIGHT %r' % x['w'])
                R.append((x['coin'], t, side, x['w']))
    return A, R, out


def check_fires(A, fires):
    with open(fires) as f:
        want = set((x['coin'], int(x['t']), int(x['side'])) for x in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    if set(A) != want:
        raise Refused('A ROWS DIFFER FROM THE FIRE LIST: %d vs %d' % (len(set(A)), len(want)))


def main(pf, V, lean, aid, first, last, H, OUT, fires=None, code=None):
    code = code or V
    if not NAME.match(code) or not NAME.match(V):
        raise Refused('BAD NAME %r %r' % (V, code))
    if lean not in ('FADE', 'FOLLOW'):
        raise Refused('BAD LEAN %r' % lean)
    t0, t1 = day_t(first), day_t(last) + 86400
    if t1 <= t0:
        raise Refused('FIRST AFTER LAST %s %s' % (first, last))
    if os.path.exists(OUT):
        raise Refused('OUT EXISTS %s' % OUT)
    if not os.path.isfile(pf):
        raise Refused('NO PERFIRE %s' % pf)
    A, R, out = read_perfire(pf, t0, t1)
    if fires:
        check_fires(A, fires)
    if not A:
        raise Refused('NO FIRES IN %s TO %s' % (first, last))
    if not R:
        raise Refused('NO RANDOM ROWS IN %s TO %s' % (first, last))
    for name, L in (('A', A), ('R', R)):
        ids = [(e[0].upper(), e[1]) for e in L]
        if len(set(ids)) != len(ids):
            raise Refused('REPEATED IDENTITY %s' % name)
    A.sort(key=lambda e: (e[1], e[0])); R.sort(key=lambda e: (e[1], e[0]))
    os.makedirs(OUT)
    pa, pr, pw = (os.path.join(OUT, n) for n in ('A_%s_EVENTS.tsv' % code, 'R_%s_EVENTS.tsv' % code, 'R_%s_W.tsv' % code))
    with open(pa, 'x') as f:
        f.write('coin\tt\tside\ttrigger\n' + ''.join('%s\t%d\t%d\tFLA%s\n' % (c, t, s, code) for c, t, s in A))
    with open(pr, 'x') as f:
        f.write('coin\tt\tside\ttrigger\n' + ''.join('%s\t%d\t%d\tFLR%s\n' % (c, t, s, code) for c, t, s, _ in R))
    with open(pw, 'x') as f:
        f.write('coin\tt\tw\n' + ''.join('%s\t%d\t%s\n' % (c, t, w) for c, t, _, w in R))
    with open(os.path.join(OUT, 'TARGETS_FL.tsv'), 'x') as f:
        f.write('code\talarm_ids\tV\tlean\tperfire\tperfire_sha16\tn_A\tn_R\tdropped_outside\tA_sha16\tR_sha16\tW_sha16\n')
        f.write('\t'.join([code, aid, V, lean, os.path.relpath(pf, H), s16(pf), str(len(A)), str(len(R)), str(out), s16(pa), s16(pr), s16(pw)]) + '\n')
    with open(os.path.join(OUT, 'BUILD.txt'), 'x') as f:
        f.write('fl_lists_v3.py %s | perfire %s | window %d <= t < %d | fires %d, random %d, outside %d | fire list %s\n' % (
            s16(os.path.abspath(__file__)), s16(pf), t0, t1, len(A), len(R), out, s16(fires) if fires else '-'))
    print('LISTS %s fires %d random %d outside %d' % (code, len(A), len(R), out))


def cli(a):
    pos, kw, i = [], {}, 0
    while i < len(a):
        if a[i] in ('--fires', '--code'):
            if i + 1 >= len(a):
                raise Refused('%s NEEDS A VALUE' % a[i])
            kw[a[i][2:]] = a[i + 1]; i += 2
        else:
            pos.append(a[i]); i += 1
    if len(pos) != 8:
        raise Refused('USAGE fl_lists_v3.py <PERFIRE> <V> <lean> <alarm id> <first> <last> <H> <out> [--fires <list>] [--code <code>]')
    main(*pos, **kw)


if __name__ == '__main__':
    try:
        cli(sys.argv[1:])
    except Refused as e:
        print('REFUSED %s' % e)
        sys.exit(2)
