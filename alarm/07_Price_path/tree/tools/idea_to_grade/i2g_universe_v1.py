"""i2g_universe_v1.py (idea_to_grade V3, ALARMLIB seat, 25 Oct 2026): writes ONE frozen cluster universe from whole fire lists, before any
grading run reads it. Each alarm's fires are clustered on their own (i2g_rules_v1.build_clusters: 30 min gap, 4 h span split and flagged,
weight 1 / cluster size); clusters never mix two alarms. Every grading run of these alarms (any coin, month or filter slice) reads the
weights from this file instead of rebuilding them. Never reads a price or an outcome.
  python3 -B i2g_universe_v1.py <new universe.tsv> ALARM_ID=<fire list .tsv (coin, t, side)> [ALARM_ID=<list> ...]"""
import csv, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import i2g_rules_v1 as RU


def sha16(p):
    import hashlib
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def read_fires(path):
    with open(path) as f:
        rows = list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))
    out = []
    for r in rows:
        s = int(r['side'])
        if s not in (-1, 1):
            raise RU.Refused('EVENT_SIDE', '%s: side %r' % (path, r['side']))
        out.append((r['coin'], int(r['t']), s))
    return out


def main(out, specs):
    if os.path.exists(out):
        raise SystemExit('REFUSED: %s exists (a universe is never overwritten)' % out)
    fires, sources = [], []
    for spec in specs:
        if '=' not in spec:
            raise SystemExit('REFUSED: give ALARM_ID=<fire list>, got %r' % spec)
        aid, path = spec.split('=', 1)
        fires += [(aid, c, t, s) for c, t, s in read_fires(path)]
        sources.append(('%s=%s' % (aid, os.path.abspath(path)), sha16(path)))
    rows = RU.build_clusters(fires)
    RU.write_universe(out, rows, sources)
    print('UNIVERSE %s %s: %d fires, %d clusters, %d chain splits' % (out, sha16(out), len(rows), len({r[5] for r in rows}),
                                                                    len({r[5] for r in rows if r[8] == 'CHAIN_SPLIT'})))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
