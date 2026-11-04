#!/usr/bin/env python3
"""t_by_month_v1.py (SCOUT, 2 Nov 2026, V1_18_FIXES; why: RESULTS_R5 item 6, decide_v3 has no t by month). Lead and day-clustered t per month, per
horizon, from one of:
  --wave-leads F  tab file with columns wave, day (YYYYMMDD), lead (points) and optionally horizon: the exact wave leads, when you have them.
  --perfire F --lean FADE|FOLLOW [--edges EDGES.tsv]  a GRADE's PERFIRE_<V>.tsv (WORK folder): spa_family's approximation, random by month, since PERFIRE
                  has no fire-to-draw link. --edges (gradeL_<V>_v1/matches/EDGES.tsv) keeps only fires with a drawn moment, as lead_null does.
  --real F        REAL_<V>.tsv (HANDOFF/REAL_SEALED): shown beside as real_lead, real_waves; alone it prints lead and waves with no t (REAL holds no spread).
The t: mean of the month's wave leads / SE, SE^2 = G/(G-1) * sum over days (sum of (d - lead))^2 / N^2, the formula of lead_null_v1_1 inside the month; under
2 days, no t. A month's waves are few: read t as a sign of spread, never as a pass (the pass rule stays decide_v4's pooled t).
Rows after --last (default 20251231; a fire at or after 23:00 of that day, as lead_null) are dropped and counted; a later month in REAL is not shown.
Reads files only, writes nothing. No numpy needed. Exit 0; 2 refused.
  $PY -B t_by_month_v1.py --perfire <W>/PERFIRE_V1.tsv --lean FADE --edges <W>/gradeL_V1_v1/matches/EDGES.tsv --real <REAL_V1.tsv>"""
import argparse, calendar, csv, math, os, sys, time

HORIZONS = ('15m', '1h')


class Refused(Exception):
    pass


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float('nan')


def table(path):
    if not os.path.isfile(path):
        raise Refused('NO FILE %s' % path)
    with open(path, newline='') as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')
        return list(rd.fieldnames or []), list(rd)


def month_stats(rows):
    """rows: [(wave lead, day)] -> lead, se, t, days"""
    N = len(rows)
    lead = sum(v for v, _ in rows) / N
    g = {}
    for v, d in rows:
        g[d] = g.get(d, 0.0) + v - lead
    G = len(g)
    if G < 2:
        return lead, float('nan'), float('nan'), G
    se = math.sqrt(G / (G - 1.0) * sum(x * x for x in g.values())) / N
    t = lead / se if se else float('nan')
    return lead, se, t, G


def read_wave_leads(path, h, last):
    head, rows = table(path)
    for c in ('wave', 'day', 'lead'):
        if c not in head:
            raise Refused('%s: NO %s COLUMN (got %s)' % (path, c, head))
    out, late = [], 0
    for row in rows:
        if h and row.get('horizon') not in (None, h):
            continue
        d, v = row['day'], num(row['lead'])
        if not (len(d) == 8 and d.isdigit()) or not math.isfinite(v):
            raise Refused('%s: BAD ROW %s' % (path, row))
        if d > last:
            late += 1; continue
        out.append((v, d))
    return out, late


def read_edges(path):
    head, rows = table(path)
    if 'fid' not in head or 'own' not in head:
        raise Refused('%s: NOT AN EDGES FILE (got %s)' % (path, head))
    keep = set()
    for r in rows:
        if not r['own']:
            keep.add(r['fid'])
    return keep


def perfire_leads(path, lean, h, edges, last):
    """wave leads from PERFIRE: per fire 100 * ((lean - other) - month random (lean - other)); per wave the mean; the day of its first fire"""
    if lean not in ('FADE', 'FOLLOW'):
        raise Refused('--perfire NEEDS --lean FADE OR FOLLOW')
    head, rows = table(path)
    other = 'FOLLOW' if lean == 'FADE' else 'FADE'
    A, O = '%s %s' % (lean, h), '%s %s' % (other, h)
    for c in ('kind', 't', 'day', 'month', 'wave', 'w', A, O):
        if c not in head:
            raise Refused('%s: NO %s COLUMN' % (path, c))
    y, m, d = int(last[:4]), int(last[4:6]), int(last[6:])
    cut = calendar.timegm((y, m, d, 23, 0, 0))
    rnd = [r for r in rows if r['kind'] == 'R' and int(r['t']) < cut]
    al = sorted((r for r in rows if r['kind'] == 'A'), key=lambda r: int(r['t']))
    late = sum(1 for r in al if int(r['t']) >= cut)
    al = [r for r in al if int(r['t']) < cut]
    if edges is not None:
        al = [r for r in al if r['coin'] + '_' + r['t'] in edges]
    s, n = {}, {}
    for r in rnd:
        a, o, w = num(r[A]), num(r[O]), num(r['w'])
        if math.isfinite(a) and math.isfinite(o) and w > 0:
            s[r['month']] = s.get(r['month'], 0.0) + w * (a - o); n[r['month']] = n.get(r['month'], 0.0) + w
    rb = {m_: s[m_] / n[m_] for m_ in s}
    wv = {}
    for r in al:
        a, o = num(r[A]), num(r[O])
        if math.isfinite(a) and math.isfinite(o) and r['month'] in rb:
            wv.setdefault(r['wave'], ([], r['day']))[0].append(100.0 * (a - o - rb[r['month']]))
    return [(sum(v) / len(v), d_) for v, d_ in wv.values()], late


def read_real(path, h, last):
    """{month: (lead, waves)} for horizon h; months after last left out"""
    head, rows = table(path)
    out = {}
    for row in rows:
        if row.get('horizon') != h:
            continue
        for c in head:
            if c.startswith('lead_'):
                m = c[5:]
                if m > last[2:6]:
                    continue
                out[m] = (row[c], row.get('waves_' + m, '-'))
    return out


def real_pooled_t(path, h):
    for row in table(path)[1]:
        if row.get('horizon') == h:
            return row.get('t')
    return None


def f(x):
    return '-' if x != x else '%.4f' % x


def report(h, leads, real):
    months = {}
    for v, d in leads:
        months.setdefault(d[2:6], []).append((v, d))
    out = []
    for m in sorted(set(months) | set(real)):
        rl, rw = real.get(m, ('-', '-'))
        if m in months:
            lead, se, t, G = month_stats(months[m])
            out.append((h, m, len(months[m]), G, f(lead), f(se), f(t), rl, rw))
        else:
            out.append((h, m, '-', '-', '-', '-', '-', rl, rw))
    if leads:
        lead, se, t, G = month_stats(leads)
        out.append((h, 'ALL', len(leads), G, f(lead), f(se), f(t), '-', '-'))
    return out


def main(a=None):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--wave-leads'); ap.add_argument('--perfire'); ap.add_argument('--lean'); ap.add_argument('--edges'); ap.add_argument('--real')
    ap.add_argument('--horizon', choices=HORIZONS); ap.add_argument('--last', default='20251231')
    o = ap.parse_args(a)
    try:
        time.strptime(o.last, '%Y%m%d')
    except ValueError:
        raise Refused('--last %r IS NOT A DAY' % o.last)
    if bool(o.wave_leads) + bool(o.perfire) > 1 or not (o.wave_leads or o.perfire or o.real):
        raise Refused('GIVE ONE OF --wave-leads, --perfire; --real beside it or alone')
    edges = read_edges(o.edges) if o.edges else None
    print('# t_by_month_v1 source: %s; last %s; t is day-clustered inside the month' % (
        'wave leads %s' % o.wave_leads if o.wave_leads else 'PERFIRE %s (approx: random by month, not the exact d_w)%s' % (o.perfire, ', edges kept' if edges is not None else '') if o.perfire else 'REAL only: no t, REAL holds no spread', o.last))
    print('horizon\tmonth\twaves\tdays\tlead\tse\tt\treal_lead\treal_waves')
    for h in ((o.horizon,) if o.horizon else HORIZONS):
        real = read_real(o.real, h, o.last) if o.real else {}
        leads, late = [], 0
        if o.wave_leads:
            leads, late = read_wave_leads(o.wave_leads, h, o.last)
        elif o.perfire:
            leads, late = perfire_leads(o.perfire, o.lean, h, edges, o.last)
        for row in report(h, leads, real):
            print('\t'.join(str(x) for x in row))
        rt = real_pooled_t(o.real, h) if o.real else None
        if rt is not None and leads:
            print('# %s pooled t here %s, REAL %s: from PERFIRE the t reads high (random by month has less spread than the exact draws); only REAL decides' % (h, f(month_stats(leads)[2]), rt))
        print('# %s dropped after %s: %d' % (h, o.last, late))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Refused, ValueError, KeyError) as e:
        print('REFUSED: %s' % e, file=sys.stderr)
        sys.exit(2)
