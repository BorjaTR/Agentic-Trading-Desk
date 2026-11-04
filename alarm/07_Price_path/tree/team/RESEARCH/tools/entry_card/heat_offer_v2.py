"""SCOUT heat_offer_v2 (21 Oct 2026; DRAFT, reviewer QUANT; tests test_heat_offer_v2.py first) = v1 with DECISION TIMES: the owner 14:19
Berlin: "The decision after the alarm can come anytime". --waits w1,w2,... (seconds after the alarm, default 0): each fire gives one entry
per wait, decided at t + w, executed after the EXECUTION DELAY (--delay, 6 s; 3 to 6 s is what is possible); each entry is tagged kind
W<w> (split K_W<w>:...) and carries move_wait_pct = the move in our side from the alarm to the decision (last close at or before each).
v1's text follows (its "lag" is v2's execution delay).
SCOUT heat_offer_v1 (21 Oct 2026; DRAFT, reviewer QUANT; tests test_heat_offer_v1.py written first). The entry card tool's LADDER step.
The owner 14:14 Berlin: "the important yardstick is heat before offer and then the trail and what percentage hits a certain offer before
each heat"; "we should stop using profit at 60". So no fixed-time profit here: per entry, when each offer level and each heat level is first
touched, and the MATRIX: for offer o and heat h, the share of entries that reach +o BEFORE they reach -h.
ENTRY  t_dec = t (the EVENTS row's time: the alarm, or a later decision time if the events file says so) + lag (6 s, the owner 13:57);
       side = FADE (-side of the row) or FOLLOW; the fill = BED fill_v2.fill(pv, t_dec, side, 'taker') on the lab's 3 s Binance bins
       (Hyperliquid prices not yet: hl_minutes_dev); not FILLED: kept and counted, never in the matrix.
LADDER BED ladder (ladder_v6, else ladder_v2): levels 0.1 to 2.5 pct of price (25), offer on the bin's hi (long) or lo (short), heat the
       other side, first touch times within the hold (default 3,600 s); a bin that crosses both counts HEAT FIRST (BED D11).
MATRIX share(o, h) = entries with offer o touched and (heat h never touched or touched strictly later) / filled entries. reach(o) = offer o
       touched at all; hit(h) = heat h touched at all. Splits: ALL, NO1011OCT, SEPOCT (to 31 Oct), NOVDEC, cost group (COSTS_PER_COIN_V3:
       cheap, middle, thin), and the EVENTS 'kind' column when present (FIRE vs MATCH).
TRAIL  booking, beside the yardstick: for each trail T (0.2, 0.3, 0.5 pct), BED trailing(): out when the price falls T below the best offer so
       far (anchor from 0, heat first); booked r = anchor - T in pct at the touch, else the close at the hold's end; net = r - the coin's
       round trip cost (COSTS_PER_COIN_V3 ALL, pct). An estimate: the exit fill after the touch slips more in a crash (BED fill_after_touch
       is the next version).
USE  python3 -B heat_offer_v1.py <lab_days> <lab3 code> <bed e_fill> <bed e_ladder> <costs tsv> <events tsv> <out dir (new)> <first YYYYMMDD>
     <last YYYYMMDD> [--lag 6] [--act FADE|FOLLOW] [--hold 3600] [--coins C1,C2]
WRITES (mode x) ROWS.tsv (one row an entry: coin, t, day, kind, side, group, cost_pct, status, t_fill, px_fill, o_<L> and h_<L> = seconds
     after the fill of the first touch or -1, trail_<T>_r, trail_<T>_net), MATRIX.tsv (split, offer, heat, n, share), REACH.tsv (split, level,
     n, reach, hit), TRAIL.tsv (split, trail, n, mean net, median net, share net > 0), all in PERCENT OF PRICE."""
import argparse, csv, datetime as dt, math, os, sys, time
import numpy as np

US = 1_000_000
LEVELS = [round(0.1 * k, 1) for k in range(1, 26)]
TRAILS = (0.2, 0.3, 0.5)
UTC = dt.timezone.utc


def ymd(t):
    return dt.datetime.fromtimestamp(float(t), UTC).strftime('%Y%m%d')


def read_costs(path):
    cost, grp = {}, {}
    for r in csv.DictReader((l for l in open(path) if not l.startswith('#')), delimiter='\t'):
        if r['hour_utc'] == 'ALL':
            v = float(r['cost_bp']); cost[r['coin']] = v / 100.0 if math.isfinite(v) else float('nan'); grp[r['coin']] = r['group'] if math.isfinite(v) else 'nocost'
    return cost, grp


def before(o_t, h_t):
    """offer reached strictly before heat (same bin = heat first); -1 = never"""
    return o_t >= 0 and (h_t < 0 or o_t < h_t)


def matrix(rows):
    """rows: dicts with o (list of 25 touch times, -1 never) and h -> {(o, h): share} and reach, hit lists"""
    n = len(rows)
    if n == 0:
        return 0, {}, [], []
    O = np.array([r['o'] for r in rows], np.int64); H = np.array([r['h'] for r in rows], np.int64)
    m = {}
    for i, lo in enumerate(LEVELS):
        oi = O[:, i]
        for j, lh in enumerate(LEVELS):
            hj = H[:, j]
            m[(lo, lh)] = float(np.mean((oi >= 0) & ((hj < 0) | (oi < hj))))
    reach = [float(np.mean(O[:, i] >= 0)) for i in range(len(LEVELS))]
    hit = [float(np.mean(H[:, i] >= 0)) for i in range(len(LEVELS))]
    return n, m, reach, hit


def splits(r):
    out = ['ALL', 'G_' + r['group']]
    if r['day'] not in ('20251010', '20251011'):
        out.append('NO1011OCT')
    out.append('SEPOCT' if r['day'] <= '20251031' else 'NOVDEC')
    if r.get('kind'):
        out = out + ['K_' + r['kind'] + ':' + s for s in list(out)]
    return out


def px_at(pv, t_us):
    j = int(np.searchsorted(pv.tl, t_us, 'right')) - 1
    return float(pv.px[j]) if j >= 0 else float('nan')


def entry_row(pv, FV, LD, t, sd, lag, act, hold_s, wait_s=0):
    """t = the alarm (s); the decision at t + wait_s; the order after the execution delay lag"""
    side = -sd if act == 'FADE' else sd
    t_al = int(round(float(t) * US)); t_dc = t_al + int(round(wait_s * US))
    tdec = t_dc + int(round(lag * US))
    f = FV.fill(pv, tdec, side, 'taker')
    pa, pd = px_at(pv, t_al), px_at(pv, t_dc)
    r = dict(side=side, status=f.status, t_fill=f.t_us, px_fill=f.px, wait_s=wait_s,
             move_wait_pct=side * 100.0 * (pd / pa - 1.0) if (pa == pa and pd == pd and pa > 0) else float('nan'))
    if f.status != 'FILLED':
        return r
    L = LD.ladder(pv, f, side, hold_s)
    ot = np.asarray(L['offer_t'], np.int64); ht = np.asarray(L['heat_t'], np.int64)
    r['o'] = [int((x - f.t_us) // US) if x >= 0 else -1 for x in ot]
    r['h'] = [int((x - f.t_us) // US) if x >= 0 else -1 for x in ht]
    r['end'] = bool(L.get('end', False))
    for T in TRAILS:
        tr = LD.trailing(pv, f, side, T, hold_s)
        if tr['touch_t'] >= 0:
            r['trail_%g' % T] = tr['anchor'] - T
        else:
            j = int(np.searchsorted(pv.tl, f.t_us + hold_s * US, 'right')) - 1
            r['trail_%g' % T] = side * 100.0 * (pv.px[j] / f.px - 1.0) if j > f.i else 0.0
    return r


def write_tables(out, rows):
    filled = [r for r in rows if r['status'] == 'FILLED']
    groups = {}
    for r in filled:
        for s in splits(r):
            groups.setdefault(s, []).append(r)
    with open(os.path.join(out, 'MATRIX.tsv'), 'x') as fm, open(os.path.join(out, 'REACH.tsv'), 'x') as fr, open(os.path.join(out, 'TRAIL.tsv'), 'x') as ft:
        fm.write('split\toffer_pct\theat_pct\tn\tshare_offer_before_heat\n'); fr.write('split\tlevel_pct\tn\treach_offer\thit_heat\n')
        ft.write('split\ttrail_pct\tn\tnet_mean_pct\tnet_median_pct\tshare_net_pos\n')
        for s in sorted(groups):
            n, m, reach, hit = matrix(groups[s])
            for (lo, lh), v in sorted(m.items()):
                fm.write('%s\t%.1f\t%.1f\t%d\t%.4f\n' % (s, lo, lh, n, v))
            for i, L in enumerate(LEVELS):
                fr.write('%s\t%.1f\t%d\t%.4f\t%.4f\n' % (s, L, n, reach[i], hit[i]))
            for T in TRAILS:
                net = np.array([r['trail_%g' % T] - r['cost_pct'] for r in groups[s] if math.isfinite(r['cost_pct'])])
                if len(net):
                    ft.write('%s\t%.1f\t%d\t%.4f\t%.4f\t%.4f\n' % (s, T, len(net), net.mean(), np.median(net), np.mean(net > 0)))
    return groups


def main(argv=None):
    p = argparse.ArgumentParser()
    for x in ('root', 'code', 'efill', 'eladder', 'costs', 'events', 'out', 'first', 'last'):
        p.add_argument(x)
    p.add_argument('--lag', '--delay', dest='lag', type=float, default=6.0); p.add_argument('--act', default='FADE', choices=('FADE', 'FOLLOW'))
    p.add_argument('--hold', type=int, default=3600); p.add_argument('--coins', default=''); p.add_argument('--waits', default='0')
    o = p.parse_args(argv)
    sys.path.insert(0, o.code); sys.path.insert(0, o.efill); sys.path.insert(0, o.eladder)
    from lab3 import days as LDY, bins as LB
    import fill_v2 as FV
    try:
        import ladder_v6 as LD
    except Exception:
        import ladder_v2 as LD
    cost, grp = read_costs(o.costs)
    R = LDY.Days(o.root, 'research'); have = set(R.days()); os.makedirs(o.out, exist_ok=False)
    EV = {}
    for r in csv.DictReader(open(o.events), delimiter='\t'):
        t = float(r['t'])
        if o.first <= ymd(t) <= o.last and int(float(r['side'])) != 0:
            EV.setdefault(r['coin'], []).append((t, int(float(r['side'])), r.get('kind', '')))
    print('HEAT_OFFER v2 waits %s s, execution delay %.1f s, act %s, hold %d s, coins %d, ladder %s' % (o.waits, o.lag, o.act, o.hold, len(EV), LD.__name__), flush=True)
    rows = []
    for coin in (o.coins.split(',') if o.coins else sorted(EV)):
        t0 = time.time(); fires = sorted(EV.get(coin, []))
        WT = [int(x) for x in o.waits.split(',')]
        days = sorted({ymd(t + w) for t, _, _ in fires for w in WT} | {ymd(t + w + o.hold + 600) for t, _, _ in fires for w in WT} | {ymd(t - 86400) for t, _, _ in fires})
        parts = {k: [] for k in ('te', 'tl', 'px', 'hi', 'lo')}
        for d in days:
            if d not in have:
                continue
            try:
                off, arr = LB.read_bins(R, d, [coin])
            except Exception as e:
                print('LAB %s %s: %s' % (coin, d, e), flush=True); continue
            for k in parts:
                parts[k].append(arr[k][off[0]:off[1]])
        base = dict(coin=coin, group=grp.get(coin, 'nocost'), cost_pct=cost.get(coin, float('nan')))
        if not parts['tl']:
            for t, sd, kd in fires:
                rows.append(dict(base, t=t, day=ymd(t), kind=kd, side=0, status='NO_PRICES'))  # one row a fire (no waits without prices)
            print('NOPX %s' % coin, flush=True); continue
        pv = FV.PriceView(coin, *[np.concatenate(parts[k]) for k in ('te', 'tl', 'px', 'hi', 'lo')])
        for t, sd, kd in fires:
            for w in WT:
                r = entry_row(pv, FV, LD, t, sd, o.lag, o.act, o.hold, w)
                r.update(base, t=t, day=ymd(t), kind=(kd + '_' if kd else '') + 'W%d' % w); rows.append(r)
        print('COIN %s entries %d (%.1f s)' % (coin, len(fires), time.time() - t0), flush=True)
    cols = ['coin', 't', 'day', 'kind', 'side', 'group', 'cost_pct', 'status', 't_fill', 'px_fill', 'wait_s', 'move_wait_pct'] + ['o_%.1f' % L for L in LEVELS] + \
           ['h_%.1f' % L for L in LEVELS] + ['trail_%g' % T for T in TRAILS]
    with open(os.path.join(o.out, 'ROWS.tsv'), 'x') as f:
        f.write('\t'.join(cols) + '\n')
        for r in rows:
            v = [r.get(c, '') for c in cols[:12]] + (r['o'] + r['h'] if 'o' in r else [''] * 50) + [r.get('trail_%g' % T, '') for T in TRAILS]
            f.write('\t'.join(('%.6g' % x) if isinstance(x, float) else str(x) for x in v) + '\n')
    st = {}
    for r in rows:
        st[r['status']] = st.get(r['status'], 0) + 1
    write_tables(o.out, rows)
    print('ENTRIES %d by status %s' % (len(rows), ' '.join('%s %d' % kv for kv in sorted(st.items()))), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
