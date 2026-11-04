# busy_v2.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK): busy_v1.py with only the profile edition 2.3 at its package place; VERSION stays busy_v1, the values are the same.
"""busy_v1.py (SCOUT 30 Oct 2026, tools/alarm_first_look). TEST, NOT REVIEWED.
How busy the market was at any moment, side-free, known at the moment: for the fires AND the random moments of the first look, so an
alarm's moves are judged against random moments that were just as busy. The owner, the owner, 30 Oct 2026 Berlin: 16:00 "the alarm's
criteria ... price moves 4c within 1 h more often than at equally busy random moments" (equally busy: the same coin, the same hour, the
same normal and recent movement); 16:05-16:06 on busy fires only, "okay, let's do that".
For every moment (coin, t) of one or more lists, three values (log-pct):
 - normal_move_pct: the coin's normal 15 min move, alarm_profile's own definition AND code, reused unchanged (episode_blocks.Ep.normal):
   the median absolute 15 min log move over [t - 25 h, t - 1 h] (96 moves, at least 48 known); the same prices as alarm_profile edition
   2.2 (its LabSource: the lab's 3 s price bins, the 2 lab days before the moment's day and that day; a bin older than 60 s is no price,
   Ep.closes); `prove` checks it equals alarm_profile's normal_move_pct on the fires (AP_<code>.tsv);
 - range60_pct: the last hour's range: the highest minus the lowest log close on the 1 min grid over [t - 60 min, t] (61 closes, at
   least RANGE_MIN = 31 known);
 - move15_pct: the last 15 min's move: |log close(t) - log close(t - 15 min)|.
KNOWN AT the moment: the prices are cut at t exactly as Ep cuts them (nothing after t). The list's side is never read (side-free). A
moment at or after 1 May 2026 is refused (never read); a (coin, t) twice in one list is refused; a moment shared by several lists is
computed once.
  python3 -B busy_v1.py build <lab_days> <lab3 code dir> <out dir (new)> <list.tsv>=<name> [<list.tsv>=<name> ...]
      one BZ_<name>.tsv.gz per list (coin, t, normal_move_pct, range60_pct, move15_pct; the list's order) and BUSY_V1.json (inputs and
      code sha16s, counts, the lab days not read)
  python3 -B busy_v1.py prove <out.tsv (new)> <BZ_<name>.tsv.gz>=<AP_<code>.tsv> [...]
      the fires' normal move against alarm_profile's: rows joined, both known, max |difference|, rows over 1e-9, known in one only
Exit 0 done (prove: every pair equal), 2 refused, 3 prove found a difference."""
import csv, gzip, hashlib, json, os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AP2 = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '05_Profile', 'tree', 'tools', 'alarm_profile_v2'))   # V1_19: the Alarm package's place
sys.path.insert(0, AP2)
import alarm_profile_v2_3 as AP                                       # noqa: E402  the price source, DAYS_PRICE, CHUNK, the day helpers
import episode_blocks as EB                                           # noqa: E402  Ep.closes and Ep.normal: the price rule and the normal move

VERSION = 'busy_v1'
T1 = 1777593600                    # 2026-05-01T00:00:00Z: never read at or after (= md_v1.T1)
RANGE_S, RANGE_STEP_S, RANGE_MIN = 3600, 60, 31
MOVE_S = 900
COLS = ('normal_move_pct', 'range60_pct', 'move15_pct')
PROVE_TOL = 1e-9
NAN = float('nan')


class Refused(Exception):
    pass


def s16(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


class Prices(EB.Ep):
    """the price part of one episode only: the coin's 3 s bins cut at t as EB.Ep cuts them (from KEEP_PRICE_S before t, plus the last bin
    before that; nothing after t). Ep.closes and Ep.normal are EB's own methods, unchanged."""
    def __init__(self, t, te_us, px):
        self.t = int(t); self.sgn = 1; self._c = {}; self.stale_n = 0
        te_us = np.asarray(te_us, np.int64); px = np.asarray(px, float)
        hi = int(np.searchsorted(te_us, self.t * 1_000_000, side='right'))
        first = max(0, int(np.searchsorted(te_us, (self.t - EB.KEEP_PRICE_S) * 1_000_000, side='left')) - 1)
        self.te_us = te_us[first:hi]; self.px = px[first:hi]


def values(e):
    """{normal_move_pct, range60_pct, move15_pct} of one Prices episode (NaN when not known)"""
    nm = e.normal()
    lg = np.log(e.closes(np.arange(e.t - RANGE_S, e.t + 1, RANGE_STEP_S, dtype=float))); ok = np.isfinite(lg)
    rng = float((lg[ok].max() - lg[ok].min()) * 100.0) if ok.sum() >= RANGE_MIN else NAN
    c0, c1 = e.closes(np.array([e.t - MOVE_S, e.t], float))
    mv = float(abs(np.log(c1) - np.log(c0)) * 100.0) if np.isfinite(c0) and np.isfinite(c1) else NAN
    return {'normal_move_pct': nm * 100.0 if np.isfinite(nm) else NAN, 'range60_pct': rng, 'move15_pct': mv}


def day_str(t):
    return np.datetime_as_string(np.asarray(t, np.int64).astype('datetime64[s]').astype('datetime64[D]')).tolist()


def compute(src, coin, t, log=None):
    """values of every moment (coin[i], t[i]), the days in time order; a lab day's prices are read for at most CHUNK coins at once (alarm_
    profile's L47 rule) and kept while a later day still needs them (a day's prices are read once per coin) -> (cols, used sources).
    src: an object with prices(day 'YYYYMMDD', coins) -> ({coin: (te_us, px)}, {source: sha16}) (alarm_profile's LabSource)"""
    coin = np.asarray(coin, dtype=object); t = np.asarray(t, np.int64); n = len(t)
    out = {k: np.full(n, NAN) for k in COLS}; used = {}; cache = {}
    if n == 0:
        return out, used
    if int(t.max()) >= T1:
        raise Refused('MAY MOMENT (at or after 1 May 2026): never read')
    days = np.array([d.replace('-', '') for d in day_str(t)])
    for day in sorted(set(days.tolist())):
        idx = np.flatnonzero(days == day); coins = sorted(set(coin[idx].tolist()))
        need = [AP.shift(day, -k) for k in range(AP.DAYS_PRICE, -1, -1)]
        for key in [k for k in cache if k[0] < need[0]]:
            del cache[key]
        for c0 in range(0, len(coins), AP.CHUNK):
            part = coins[c0:c0 + AP.CHUNK]; PX = {c: [] for c in part}
            for d in need:
                miss = [c for c in part if (d, c) not in cache]
                if miss:
                    p, s = src.prices(d, miss); used.update(s)
                    for c in miss:
                        cache[(d, c)] = p.get(c)
                for c in part:
                    if cache[(d, c)] is not None:
                        PX[c].append(cache[(d, c)])
            for c in part:
                if PX[c]:
                    te = np.concatenate([q[0] for q in PX[c]]).astype(np.int64); px = np.concatenate([q[1] for q in PX[c]]).astype(float)
                    o = np.argsort(te, kind='mergesort'); te, px = te[o], px[o]
                else:
                    te, px = np.zeros(0, np.int64), np.zeros(0)
                for i in idx[coin[idx] == c]:
                    v = values(Prices(t[i], te, px))
                    for k in COLS:
                        out[k][i] = v[k]
        if log:
            log('DAY %s moments %d coins %d' % (day, len(idx), len(coins)))
    return out, used


def load_list(path):
    """(coin, t) of a list (coin and t columns; other columns ignored, the side too); a (coin, t) twice is refused"""
    with open(path) as f:
        rd = csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'); rows = list(rd); h = rd.fieldnames or []
    if 'coin' not in h or 't' not in h:
        raise Refused('LIST COLUMNS %s (needs coin and t)' % path)
    coin = np.array([r['coin'] for r in rows], dtype=object); t = np.array([int(float(r['t'])) for r in rows], np.int64)
    keys = list(zip(coin.tolist(), t.tolist()))
    if len(set(keys)) != len(keys):
        raise Refused('A (coin, t) TWICE in %s' % path)
    if len(t) and int(t.max()) >= T1:
        raise Refused('MAY MOMENT in %s: never read' % path)
    return coin, t


def fmt(x):
    return '' if not np.isfinite(x) else '%.12g' % x


def build(lab_root, code_dir, out, specs, src=None, log=print):
    """specs: [(list path, name)] -> writes BZ_<name>.tsv.gz per list and BUSY_V1.json into out (new); the union of moments computed once"""
    if os.path.exists(out) or os.path.exists(out + '.part'):
        raise Refused('OUT EXISTS %s' % out)
    names = [n for _, n in specs]
    if len(set(names)) != len(names) or any(not n or '/' in n for n in names):
        raise Refused('LIST NAMES %s' % names)
    L = [(p, n) + load_list(p) for p, n in specs]
    keys = {}
    for _, _, coin, t in L:
        for k in zip(coin.tolist(), t.tolist()):
            keys.setdefault(k, len(keys))
    U = list(keys); uc = np.array([k[0] for k in U], dtype=object); ut = np.array([k[1] for k in U], np.int64)
    if src is None:
        src = AP.LabSource(lab_root, code_dir, hl_dirs=())
    cols, used = compute(src, uc, ut, log=log)
    part = out + '.part'; os.makedirs(part)
    try:
        man = {'version': VERSION, 'code': {'busy_v2.py': s16(os.path.abspath(__file__)), 'episode_blocks.py': s16(EB.__file__),
                                            'alarm_profile_v2_3.py': s16(AP.__file__)},
               'settings': {'normal': list(EB.SETTINGS['norm']), 'max_price_age_s': EB.MAX_PRICE_AGE_S, 'keep_price_s': EB.KEEP_PRICE_S,
                            'days_price': AP.DAYS_PRICE, 'range_s': RANGE_S, 'range_step_s': RANGE_STEP_S, 'range_min': RANGE_MIN, 'move_s': MOVE_S},
               'lab_root': lab_root, 'moments': len(U), 'lab_sources_read': len(used),
               'lab_days_not_read': sorted(set('%s %s %s' % x for x in getattr(src, 'skipped', []))), 'lists': {}}
        for p, n, coin, t in L:
            ix = np.array([keys[k] for k in zip(coin.tolist(), t.tolist())], int)
            fp = os.path.join(part, 'BZ_%s.tsv.gz' % n)
            with gzip.open(fp, 'wt') as f:
                f.write('coin\tt\t' + '\t'.join(COLS) + '\n')
                for j, i in enumerate(ix):
                    f.write('%s\t%d\t%s\n' % (coin[j], t[j], '\t'.join(fmt(cols[k][i]) for k in COLS)))
            man['lists'][n] = {'list': [os.path.abspath(p), s16(p)], 'rows': len(t), 'out': ['BZ_%s.tsv.gz' % n, s16(fp)],
                               'not_known': {k: int((~np.isfinite(cols[k][ix])).sum()) if len(ix) else 0 for k in COLS}}
        with open(os.path.join(part, 'BUSY_V1.json'), 'x') as f:
            json.dump(man, f, indent=1, sort_keys=True)
    except BaseException:
        shutil.rmtree(part, ignore_errors=True); raise
    os.rename(part, out)
    return man


def load_bz(path):
    """BZ_<name>.tsv.gz -> {coin, t, normal_move_pct, range60_pct, move15_pct} arrays (NaN when not known)"""
    with gzip.open(path, 'rt') as f:
        rd = csv.reader(f, delimiter='\t'); h = next(rd); rows = list(rd)
    if h != ['coin', 't'] + list(COLS):
        raise Refused('BZ HEADER %s' % path)
    out = {'coin': np.array([r[0] for r in rows], dtype=object), 't': np.array([int(r[1]) for r in rows], np.int64)}
    for j, k in enumerate(COLS):
        out[k] = np.array([float(r[2 + j]) if r[2 + j] != '' else NAN for r in rows], float)
    if len(rows) and int(out['t'].max()) >= T1:
        raise Refused('MAY ROW in %s' % path)
    return out


def prove(outp, pairs):
    """[(BZ path, AP path)] -> rows of (bz, ap, joined, both_known, max_abs_diff, over_tol, known_in_one_only, bz_rows_without_ap); 0 when
    every pair is equal (no row over PROVE_TOL, none known in one only, every BZ row joined), else 3"""
    if os.path.exists(outp):
        raise Refused('OUT EXISTS %s' % outp)
    res = []
    for bzp, app in pairs:
        B = load_bz(bzp); a = {}
        with open(app) as f:
            for r in csv.DictReader(f, delimiter='\t'):
                a[(r['coin'], int(float(r['t'])))] = float(r['normal_move_pct']) if (r.get('normal_move_pct') or '').strip() != '' else NAN
        x = []; y = []; nj = 0
        for c, t, v in zip(B['coin'].tolist(), B['t'].tolist(), B['normal_move_pct']):
            if (c, t) in a:
                nj += 1; x.append(v); y.append(a[(c, t)])
        x = np.array(x, float); y = np.array(y, float); both = np.isfinite(x) & np.isfinite(y); one = np.isfinite(x) ^ np.isfinite(y)
        d = np.abs(x[both] - y[both])
        res.append((os.path.basename(bzp), os.path.basename(app), nj, int(both.sum()), float(d.max()) if len(d) else 0.0,
                    int((d > PROVE_TOL).sum()), int(one.sum()), len(B['t']) - nj))
    with open(outp, 'x') as f:
        f.write('bz\tap\tjoined\tboth_known\tmax_abs_diff_pct\tover_1e-9\tknown_in_one_only\tbz_rows_without_ap\n')
        for r in res:
            f.write('%s\t%s\t%d\t%d\t%.3g\t%d\t%d\t%d\n' % r)
    bad = [r for r in res if r[5] or r[6] or r[7]]
    for r in res:
        print('PROVE %s vs %s: joined %d, both known %d, max |diff| %.3g, over 1e-9 %d, known in one only %d, without AP %d' % r)
    print('PROVE %s: %d of %d pairs equal' % ('OK' if not bad else 'DIFFERENT', len(res) - len(bad), len(res)))
    return 0 if not bad else 3


def main(a):
    if len(a) >= 5 and a[0] == 'build':
        specs = []
        for x in a[4:]:
            if '=' not in x:
                raise Refused('LIST SPEC %s (path=name)' % x)
            p, n = x.rsplit('=', 1); specs.append((p, n))
        man = build(a[1], a[2], a[3], specs)
        print('BUSY %s: %d moments, %d lists, %d lab sources; BUSY_V1.json %s' % (a[3], man['moments'], len(man['lists']), man['lab_sources_read'],
                                                                                 s16(os.path.join(a[3], 'BUSY_V1.json'))))
        return 0
    if len(a) >= 3 and a[0] == 'prove':
        pairs = []
        for x in a[2:]:
            if '=' not in x:
                raise Refused('PAIR SPEC %s (bz=ap)' % x)
            pairs.append(tuple(x.split('=', 1)))
        return prove(a[1], pairs)
    print(__doc__)
    return 2


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print('REFUSED %s' % e)
        sys.exit(2)
