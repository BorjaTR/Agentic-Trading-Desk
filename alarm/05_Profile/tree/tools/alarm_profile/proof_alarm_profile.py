"""tools/alarm_profile PROOF RUN (QUANT 22 Oct 2026; the owner 13:13 Berlin: "we prove it means what it says"). After the build, it runs
the proofs of PROOFS_V1.tsv that need real data and writes one result row per (value, proof) to <out>/PROOF_RESULTS_RUN.tsv (value, proof,
result, receipt, utc), the numbers to <out>/PROOF_REPORT.txt, and the eye-check samples. No outcome after any alarm is read.
  P2_TWIN          every built alarm: the values READ BACK from research_days (alarm_profile.read, the one format) against episode_twin.twin
                   on inputs loaded HERE by a loader written apart from the builder's (per coin; daily totals by math.fsum)
  P3_PRICE_RECORD  12 alarms (seed 22102026, 3 a month, 10-11 Oct out, Binance 1m klines present for D-2..D): the lab's minute-end
                   closes against the kline closes over the 24 h before; the run start and run move from each record (minute ends)
  P4_OI_LINE       open interest fell during the burst in >= 60 pct; Spearman(burst_vs_oi_bp, -oi_chg_burst_pct) > 0, shuffle p < 0.01
  P4_HL_LINE       for forced_usd_log and size_vs_week: the share of alarms with a same-side Hyperliquid liquidation in the burst, top
                   quarter minus bottom quarter of the value > 0, within-day shuffle p < 0.01 (10,000 shuffles)
  P4_HL_SIGN       where Hyperliquid liquidated anyone in the burst, the forced side holds more dollars in >= 70 pct
  EYE samples      EYE_RUN_SAMPLE.tsv, v3 (22 Oct): 16 charts in a drawn order, 12 fresh (seed 22102030, 3 a month) and 4 of the
                   alarms whose run start v3 moved from v1 (seed 22102031), none of the 12 SCOUT judged in J471128 (SEEN_V1); which is
                   which kept apart in EYE_RUN_KEY.tsv; EYE_WAVES_SAMPLE.tsv (seed 22102027, with onset_t; the tool's count kept apart in
                   EYE_WAVES_KEY.tsv)
  REGRESSION       the run values against a02_run_start_v1's rows (q_471127): how many v3 moved (the bounce and the pause rules), the
                   normal move equal on every alarm (or FAIL)
  P2B INPUTS       P2B_INPUTS.npz: the raw inputs of 24 alarms (seed 22102032, 6 a month) for a FRESH blind reader who sees only the README;
                   the tool's values for them kept apart in P2B_KEY.tsv
  (P3 computes the run start on minute ends the same way for both records: it tests the price record, not the run end)
  JOIN             how many alarms have CTX.A02 rows at decision 0 (the profiles' join)
  python3 -B proof_alarm_profile.py <lab_days> <lab3 code dir> <alarms tsv> <out root> <out dir> <klines root> <run_start tsv> <receipt>"""
import csv, datetime as dt, io, math, os, sys, zipfile
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import alarm_profile as AP
import episode_blocks as EB
import episode_twin as TW

SEED_RUN, SEED_WAVES, NPERM = 22102026, 22102027, 10000
SEED_EYE2, SEED_FIX = 22102030, 22102031                             # the v3 eye check: fresh draw, and alarms whose start v3 moved from v1
SEED_P2B = 22102032                                                  # the 24 alarms for a fresh blind reader (6 a month)
SEEN_V1 = {('BTC', 1757999210), ('ETH', 1758712470), ('SHIB', 1758751160), ('AVAX', 1760560530), ('SOL', 1761228915), ('SOL', 1761923420),
           ('ETH', 1762139655), ('OP', 1762183920), ('LTC', 1763175670), ('APT', 1764952965), ('ATOM', 1766078190), ('ENA', 1767199410)}
OUT_DAYS = ('20251010', '20251011')
SYM = {'PEPE': '1000PEPEUSDT', 'BONK': '1000BONKUSDT', 'SHIB': '1000SHIBUSDT'}


def utc_day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def same(a, b, tol=1e-9):
    return (math.isnan(a) and math.isnan(b)) or (not math.isnan(a) and not math.isnan(b) and abs(a - b) <= tol * max(1.0, abs(a)))


class Loader:
    """the twin's inputs, loaded apart from alarm_profile.LabSource: per coin and day; daily totals by math.fsum over the known rows"""
    def __init__(self, lab_root, code_dir):
        sys.path.insert(0, code_dir)
        from lab3 import days as LD, bins as LB
        self.R = LD.Days(lab_root, 'research'); self.LB = LB; self.cache = {}
        self.hl = {}
        for d in AP.HL_DIRS:
            for n in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
                if n.startswith('HLF_') and n.endswith('.npz'):
                    self.hl[tuple(n[4:-4].rsplit('_', 1))] = os.path.join(d, n)

    def code(self, code, day, coin, steps):
        key = (code, day)
        if key not in self.cache:                                   # the whole day block once, every coin of its part
            try:
                coins = list(self.R.index(day, self.R.part_of(code, day))['coins'])
                a = np.asarray(self.R.read(code, 'v', [day], coins)[0], float); self.cache[key] = {c: a[i] for i, c in enumerate(coins)}
            except (LookupError, OSError):
                self.cache[key] = {}
        v = self.cache[key].get(coin)
        return v if v is not None else np.full(steps, np.nan)

    def prices(self, day, coin):
        key = ('PX', day, coin)
        if key not in self.cache:
            try:
                off, b = self.LB.read_bins(self.R, day, [coin]); te = np.asarray(b['te'][off[0]:off[1]], np.int64); px = np.asarray(b['px'][off[0]:off[1]], float)
            except (LookupError, OSError):
                te, px = np.zeros(0, np.int64), np.zeros(0)
            self.cache[key] = (te, px)
        return self.cache[key]

    def total(self, day, coin, code):
        key = ('TOT', day, coin, code)
        if key not in self.cache:
            v = self.code(code, day, coin, 17280); ok = [float(x) for x in v.tolist() if x == x]
            self.cache[key] = (math.fsum(ok), len(ok) / 17280.0)
        return self.cache[key]

    def hl_fills(self, coin, days):
        name = AP.HL_NAME.get(coin, coin); cov = set(); lt, usd, sd = [], [], []
        for d in days:
            p = self.hl.get((name, d))
            if p is None:
                continue
            with np.load(p) as z:
                if len(z['t']) == 0:
                    continue
                cov.add(d); k = z['lself'] == 1
                lt += (z['lt'][k] / 1000.0).tolist(); usd += (z['lpx'][k] * z['lsz'][k]).tolist(); sd += z['lside'][k].tolist()
        return dict(days=cov, lt=np.array(lt), usd=np.array(usd), side=np.array(sd)) if cov else None

    def args(self, coin, t, t0, side):
        D = utc_day(t); P = AP.shift(D, -1); T5 = AP.day0(P)
        f_code, o_code = ('A1.S02', 'A1.S01') if side > 0 else ('A1.S01', 'A1.S02')
        xf = np.concatenate([self.code(f_code, d, coin, 17280) for d in (P, D)]); xo = np.concatenate([self.code(o_code, d, coin, 17280) for d in (P, D)])
        te = np.concatenate([self.prices(d, coin)[0] for d in (AP.shift(D, -2), P, D)]); px = np.concatenate([self.prices(d, coin)[1] for d in (AP.shift(D, -2), P, D)])
        o = np.argsort(te, kind='stable'); te, px = te[o], px[o]
        daily = {AP.shift(D, -j): self.total(AP.shift(D, -j), coin, f_code) for j in range(1, 9)}
        oi_t = np.array([AP.day0(d) + 60.0 * m for d in (P, D) for m in range(1440)])
        oi_v = np.concatenate([self.code('E2.S02', d, coin, 1440) for d in (P, D)]); oi_c = np.concatenate([self.code('E2.S03', d, coin, 1440) for d in (P, D)])
        return (coin, t, t0, side, T5, xf, xo, te, px, daily, oi_t, oi_v, oi_c, self.hl_fills(coin, (P, D)))

    def drop_day(self, keep_from):
        for k in [k for k in self.cache if k[1] < keep_from]:
            del self.cache[k]


def ranks(a):
    """average ranks (ties share their mean rank)"""
    a = np.asarray(a, float); o = np.argsort(a, kind='mergesort'); s = a[o]; r = np.empty(len(a)); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        r[o[i:j + 1]] = 0.5 * (i + j); i = j + 1
    return r


def corr(ra, rb):
    return float(np.corrcoef(ra, rb)[0, 1])


def kline_closes(root, coin, days):
    """{minute end (s): close} from Binance's 1m kline zips (data.binance.vision layout)"""
    sym = SYM.get(coin, coin + 'USDT'); out = {}
    for d in days:
        p = os.path.join(root, sym, '%s-1m-%s-%s-%s.zip' % (sym, d[:4], d[4:6], d[6:]))
        if not os.path.exists(p):
            return None
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                for row in csv.reader(io.TextIOWrapper(z.open(name))):
                    if not row or not row[0].strip().isdigit():
                        continue
                    ot = int(row[0]); ot = ot // 1000 if ot > 10 ** 14 else ot      # ms (or us in later files)
                    out[ot // 1000 + 60] = float(row[4])
    return out


def run_on_minutes(closes_at, tm, sgn):
    """the run start and run move on minute-end closes (both records the same way) -> (start time, run pct) or (nan, nan)"""
    g = np.array([closes_at(tm - 90000 + 900 * j) for j in range(97)], float); m = np.abs(np.diff(np.log(g))); m = m[np.isfinite(m)]
    if len(m) < 48:
        return NAN, NAN
    nm = float(np.median(m)); grid = np.array([tm - 86400 + 60 * k for k in range(1441)], float)
    c = np.array([closes_at(s) for s in grid], float); x = sgn * np.log(c)
    if not np.isfinite(x[-1]):
        return NAN, NAN
    i0, _ = EB.run_start_index(x, max(3 * nm, 0.001), nm)
    return float(grid[i0]), float((x[-1] - x[i0]) * 100)


NAN = float('nan')


def main(lab_root, code_dir, alarms_path, out_root, out_dir, klines_root, run_start_path, receipt):
    os.makedirs(out_dir, exist_ok=True); now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ev = AP.load_alarms(alarms_path, AP.SUBJECTS['A02'][0]); res = []; rep = []
    x = AP.read(out_root, code_dir, 'A02', '20250901', '20251231')
    names = [c[2] for c in AP.columns()]; n = len(x['coin'])
    key = {(c, int(round(t))): i for i, (c, t) in enumerate(zip(x['coin'], x['t_alarm']))}
    order = sorted(range(len(ev['t'])), key=lambda i: (int(ev['t'][i]), ev['coin'][i]))
    evk = {(ev['coin'][i], int(ev['t'][i])): i for i in range(len(ev['t']))}
    rep.append('BUILT ROWS %d of %d alarms in the list' % (n, len(ev['t'])))
    # ---- P2: the twin on every alarm
    L = Loader(lab_root, code_dir); bad = {k: 0 for k in names}; cmp_n = {k: 0 for k in names}; worst = {}; last_day = None
    at_ext = np.zeros(n, bool)                                       # the alarm's close is the extreme since the burst start (run end = alarm)
    for i in order:
        coin, t, side, t0 = ev['coin'][i], int(ev['t'][i]), int(ev['side'][i]), int(ev['onset_t'][i])
        j = key.get((coin, t))
        if j is None:
            continue
        d = utc_day(t)
        if d != last_day:
            L.drop_day(AP.shift(d, -9)); last_day = d
        a = L.args(coin, t, t0, side); w = TW.twin(*a[:13], hl=a[13])
        te_, px_ = a[7], a[8]; bs = float(x['burst_s'][j]); w0 = t - bs if bs == bs else t0 - 60.0
        q = int(np.searchsorted(te_, int(round(w0 * 1e6)), 'right')) - 1; hi_ = int(np.searchsorted(te_, t * 1_000_000, 'right'))
        seg = [side * math.log(v) for v in px_[max(q, 0):hi_].tolist() if v > 0] if q >= 0 else [side * math.log(v) for v in px_[:hi_].tolist() if v > 0]
        at_ext[j] = bool(seg) and px_[hi_ - 1] > 0 and side * math.log(px_[hi_ - 1]) >= max(seg)
        for k in names:
            a = float(x[k][j]); cmp_n[k] += 1
            if not same(a, w[k]):
                bad[k] += 1; worst.setdefault(k, (coin, t, a, w[k]))
    for k in names:
        ok = bad[k] == 0 and cmp_n[k] == n and n > 0
        res.append((k, 'P2_TWIN', 'PASS' if ok else 'FAIL'))
        rep.append('P2 %-24s compared %5d differ %d%s' % (k, cmp_n[k], bad[k], '' if k not in worst else '  first %s' % (worst[k],)))
    # ---- P3: another price record
    rng = np.random.default_rng(SEED_RUN); picked = []
    for mo in ('09', '10', '11', '12'):
        pool = [i for i in order if utc_day(ev['t'][i])[4:6] == mo and utc_day(ev['t'][i]) not in OUT_DAYS and (ev['coin'][i], int(ev['t'][i])) in key]
        rng.shuffle(pool); got = 0
        for i in pool:
            if got == 3:
                break
            coin, t = ev['coin'][i], int(ev['t'][i]); D = utc_day(t)
            kl = kline_closes(klines_root, coin, [AP.shift(D, -2), AP.shift(D, -1), D])
            if kl is None:
                continue
            picked.append((i, kl)); got += 1
    p3_ok = 0; minutes_ok = []
    for i, kl in picked:
        coin, t, side = ev['coin'][i], int(ev['t'][i]), int(ev['side'][i]); tm = (t // 60) * 60
        a = L.args(coin, t, int(ev['onset_t'][i]), side); te, px = a[7], a[8]
        lab_at = lambda s: (lambda k: float(px[k]) if k >= 0 and px[k] > 0 else NAN)(int(np.searchsorted(te, int(s * 1e6), 'right')) - 1)
        kl_at = lambda s: kl.get(int(s), NAN)
        ms = [tm - 60 * k for k in range(1441)]; pairs = [(lab_at(s), kl_at(s)) for s in ms]
        good = [abs(p / q - 1) <= 1e-4 for p, q in pairs if p == p and q == q]; share = float(np.mean(good)) if good else 0.0
        s1, r1 = run_on_minutes(lab_at, tm, side); s2, r2 = run_on_minutes(kl_at, tm, side)
        agree = share >= 0.99 and abs(s1 - s2) <= 120 and abs(r1 - r2) <= 0.05
        p3_ok += agree; minutes_ok.append(share)
        rep.append('P3 %s %d minutes within 1 bp %.4f (of %d) | start lab %s klines %s | run lab %.4f klines %.4f | %s' % (
            coin, t, share, len(good), s1, s2, r1, r2, 'AGREE' if agree else 'DIFFER'))
    p3 = 'PASS' if len(picked) == 12 and p3_ok >= 11 else 'FAIL'
    rep.append('P3 PRICE RECORD %d of %d agree: %s' % (p3_ok, len(picked), p3))
    res.append(('PRICE', 'P3_PRICE_RECORD', p3))
    for r in AP._tsv(AP.PROOFS):
        if r['proof'] == 'P3_PRICE_RECORD':
            res.append((r['value'], 'P3_PRICE_RECORD', p3))
    # ---- P4 lines (inputs known at the alarm only)
    o = x['oi_chg_burst_pct']; b = x['burst_vs_oi_bp']; k = np.isfinite(o) & np.isfinite(b)
    if k.sum() < 40:
        k = np.zeros(len(o), bool)                                   # too few: the line cannot pass
    fell = float(np.mean(o[k] < 0)) if k.any() else NAN; rb, ro = ranks(b[k]), ranks(-o[k]); rho = corr(rb, ro) if k.sum() > 2 else NAN
    prng = np.random.default_rng(SEED_RUN); hits = 0
    for _ in range(NPERM if k.sum() > 2 else 0):
        hits += corr(rb, prng.permutation(ro)) >= rho
    p = (1 + hits) / (1 + NPERM); oi = 'PASS' if k.sum() >= 40 and fell >= 0.60 and rho > 0 and p < 0.01 else 'FAIL'
    rep.append('P4 OI LINE alarms %d: OI fell in %.3f; Spearman %.3f, shuffle p %.4f: %s' % (int(k.sum()), fell, rho, p, oi))
    res.append(('forced_usd_log', 'P4_OI_LINE', oi))
    hf = x['hl_forced_usd_log']; ho = x['hl_other_usd_log']; days = np.array([utc_day(t) for t in x['t_alarm']])
    for v in ('forced_usd_log', 'size_vs_week'):
        val = x[v]; k = np.isfinite(hf) & np.isfinite(val); I = (hf[k] > 0).astype(float); vv = val[k]; dd = days[k]
        if k.sum() < 40:
            rep.append('P4 HL LINE %s: only %d alarms with both known: FAIL (too few to judge)' % (v, int(k.sum()))); res.append((v, 'P4_HL_LINE', 'FAIL')); continue
        q25, q75 = np.percentile(vv, [25, 75]); top = vv >= q75; bot = vv <= q25
        stat = float(I[top].mean() - I[bot].mean()); prng = np.random.default_rng(SEED_RUN); hits = 0
        groups = [np.flatnonzero(dd == u) for u in np.unique(dd)]
        for _ in range(NPERM):
            J = I.copy()
            for g in groups:
                J[g] = J[prng.permutation(g)]
            hits += (J[top].mean() - J[bot].mean()) >= stat
        p = (1 + hits) / (1 + NPERM); ok = 'PASS' if stat > 0 and p < 0.01 else 'FAIL'
        rep.append('P4 HL LINE %s: alarms %d, same-side Hyperliquid liquidation in the burst: top quarter %.3f, bottom %.3f, all %.3f; within-day shuffle p %.4f: %s' % (
            v, int(k.sum()), I[top].mean(), I[bot].mean(), I.mean(), p, ok))
        res.append((v, 'P4_HL_LINE', ok))
    k = np.isfinite(hf) & np.isfinite(ho) & ((hf > 0) | (ho > 0)); share = float(np.mean(hf[k] > ho[k])) if k.any() else NAN
    sg = 'PASS' if k.sum() >= 40 and share >= 0.70 else 'FAIL'
    rep.append('P4 HL SIGN alarms with any Hyperliquid liquidation in the burst %d: the forced side holds more dollars in %.3f: %s' % (int(k.sum()), share, sg))
    res += [('hl_forced_usd_log', 'P4_HL_SIGN', sg), ('hl_other_usd_log', 'P4_HL_SIGN', sg)]
    # ---- eye samples (drawn, not chosen)
    def draw(seed, need, skip=()):
        g = np.random.default_rng(seed); out = []
        for mo in ('09', '10', '11', '12'):
            pool = [j for j in range(n) if utc_day(x['t_alarm'][j])[4:6] == mo and utc_day(x['t_alarm'][j]) not in OUT_DAYS and all(np.isfinite(x[c][j]) for c in need)
                    and (x['coin'][j], int(round(x['t_alarm'][j]))) not in skip]
            out += [pool[q] for q in g.choice(len(pool), size=min(3, len(pool)), replace=False)]
        return out
    # ---- regression against a02_run_start_v1 (q_471127): how many v3 moved (bounce: later run end; pause: later start); normal move equal
    with open(run_start_path) as fh:
        rr = [r for r in csv.DictReader(fh, delimiter='\t') if r['def'] == 'A02M']
    m = 0; unchanged = 0; changed = []; chg_at_ext = 0; n_at_ext = 0; norm_eq = 0; old = {}
    for r in rr:
        j = key.get((r['coin'], int(r['t'])))
        if j is None or r['run_pct'] == '':
            continue
        m += 1; n_at_ext += bool(at_ext[j]); norm_eq += abs(float(r['norm_pct']) - x['normal_move_pct'][j]) <= 6e-5
        eq = (abs(float(r['run_pct']) - x['run_pct'][j]) <= 6e-5 and abs(float(r['age_min']) - x['run_age_min'][j]) <= 6e-5
              and x['run_capped'][j] == x['run_capped'][j] and int(r['capped']) == int(x['run_capped'][j]))
        if eq:
            unchanged += 1
        else:
            changed.append(j); chg_at_ext += bool(at_ext[j]); old[j] = (float(r['run_pct']), float(r['age_min']))
    reg = 'PASS' if m == n and norm_eq == m else 'FAIL'
    rep.append('REGRESSION vs q_471127 (v1; A02M rows known in both %d): unchanged %d, moved by v3 %d (of them %d where the alarm\'s close is the '
               'extreme since the burst start: pause only); normal move equal %d: %s' % (m, unchanged, len(changed), chg_at_ext, norm_eq, reg))
    if changed:
        c = np.array(changed); o1 = np.array([old[j][0] for j in changed]); a1 = np.array([old[j][1] for j in changed]); a3 = x['run_age_min'][c]
        rep.append('MOVED BY V3 %d alarms: start later (shorter run) %d, earlier (the v1 bounce restarts) %d; run_age_min median v1 %.1f -> v3 %.1f; '
                   'run_pct median v1 %.3f -> v3 %.3f; v1 age <= 1 min in %d' % (len(c), int(np.sum(a3 < a1)), int(np.sum(a3 > a1)), np.median(a1),
                                                                             np.nanmedian(a3), np.median(o1), np.nanmedian(x['run_pct'][c]), int(np.sum(a1 <= 1))))
        allc = np.ones(n, bool); allc[c] = False
        rep.append('V3 ALL ALARMS run_age_min q25 %.1f q50 %.1f q75 %.1f; run_pct q25 %.3f q50 %.3f q75 %.3f; run_capped share %.3f' % tuple(
            list(np.nanpercentile(x['run_age_min'], [25, 50, 75])) + list(np.nanpercentile(x['run_pct'], [25, 50, 75])) + [float(np.nanmean(x['run_capped']))]))
    # ---- the v3 eye check: 12 fresh (3 a month) and 4 whose start v3 moved from v1, in a drawn order; which is which kept apart
    seen = {kk for kk in SEEN_V1}
    fresh = [j for j in draw(SEED_EYE2, ('run_age_min', 'burst_s'), skip=seen)]
    pool = [j for j in changed if (x['coin'][j], int(round(x['t_alarm'][j]))) not in seen and j not in fresh
            and np.isfinite(x['run_age_min'][j]) and np.isfinite(x['burst_s'][j])]
    g = np.random.default_rng(SEED_FIX); fix = [pool[q] for q in g.choice(len(pool), size=min(4, len(pool)), replace=False)] if pool else []
    panels = [(j, 'FRESH') for j in fresh] + [(j, 'CHANGED') for j in fix]
    panels = [panels[q] for q in np.random.default_rng(SEED_EYE2).permutation(len(panels))]
    with open(os.path.join(out_dir, 'EYE_RUN_SAMPLE.tsv'), 'x') as fh, open(os.path.join(out_dir, 'EYE_RUN_KEY.tsv'), 'x') as fk:
        fh.write('chart\tcoin\tt\tside\tminute\tx_pct\tstart_t\tburst_t\tonset_t\n'); fk.write('chart\tcoin\tt\tgroup\trun_age_min\trun_pct\n')
        for c_i, (j, grp) in enumerate(panels, 1):
            coin, t = x['coin'][j], int(round(x['t_alarm'][j])); i = evk[(coin, t)]
            side = int(ev['side'][i]); a = L.args(coin, t, int(ev['onset_t'][i]), side); te, px = a[7], a[8]
            st = t - x['run_age_min'][j] * 60; bt = t - x['burst_s'][j]; ot = t - x['onset_to_alarm_s'][j]
            for mm in range(1441):
                s_ = t - 86400 + 60 * mm; q = int(np.searchsorted(te, int(s_ * 1e6), 'right')) - 1
                xv = side * math.log(px[q]) * 100 if q >= 0 and px[q] > 0 else NAN
                fh.write('%d\t%s\t%d\t%d\t%d\t%.5f\t%d\t%d\t%d\n' % (c_i, coin, t, side, s_, xv, st, bt, ot))
            fk.write('%d\t%s\t%d\t%s\t%.1f\t%.4f\n' % (c_i, coin, t, grp, x['run_age_min'][j], x['run_pct'][j]))
    rep.append('EYE RUN v3 sample: %d fresh (seed %d), %d moved (seed %d, of %d moved not seen), none of the 12 SCOUT judged in J471128' % (
        len(fresh), SEED_EYE2, len(fix), SEED_FIX, len(pool)))
    with open(os.path.join(out_dir, 'EYE_WAVES_SAMPLE.tsv'), 'x') as fh, open(os.path.join(out_dir, 'EYE_WAVES_KEY.tsv'), 'x') as fk:
        fh.write('chart\tcoin\tt\tside\tonset_t\trow_end\tforced_usd\n'); fk.write('chart\tcoin\tt\tn_flushes\n')
        for c_i, j in enumerate(draw(SEED_WAVES, ('n_flushes', 'burst_s')), 1):
            coin, t = x['coin'][j], int(round(x['t_alarm'][j])); i = evk[(coin, t)]
            side = int(ev['side'][i]); t0 = int(ev['onset_t'][i]); a = L.args(coin, t, t0, side); T5 = a[4]; xf = a[5]
            for k5 in range((t0 - 120 - T5) // 5, (t - T5) // 5 + 1):
                fh.write('%d\t%s\t%d\t%d\t%d\t%d\t%.2f\n' % (c_i, coin, t, side, t0, T5 + 5 * k5, xf[k5]))
            fk.write('%d\t%s\t%d\t%d\n' % (c_i, coin, t, int(x['n_flushes'][j])))
    # ---- P2B inputs for a FRESH blind reader (sees only the README): 24 alarms, 6 a month, the raw inputs as the twin gets them
    g = np.random.default_rng(SEED_P2B); pick = []
    for mo in ('09', '10', '11', '12'):
        pool = [j for j in range(n) if utc_day(x['t_alarm'][j])[4:6] == mo and utc_day(x['t_alarm'][j]) not in OUT_DAYS]
        pick += [pool[q] for q in g.choice(len(pool), size=min(6, len(pool)), replace=False)]
    Z = {}; meta = []
    for i_, j in enumerate(pick):
        coin, t = x['coin'][j], int(round(x['t_alarm'][j])); i = evk[(coin, t)]; side = int(ev['side'][i]); t0 = int(ev['onset_t'][i])
        a = L.args(coin, t, t0, side); te, px = a[7], a[8]; k = (te >= (t - 26 * 3600) * 1_000_000) & (te <= (t + 600) * 1_000_000)
        Z['%d_xf' % i_] = a[5]; Z['%d_xo' % i_] = a[6]; Z['%d_te_us' % i_] = te[k]; Z['%d_px' % i_] = px[k]
        Z['%d_oi_t' % i_] = a[10]; Z['%d_oi_v' % i_] = a[11]; Z['%d_oi_c' % i_] = a[12]
        dd = sorted(a[9]); Z['%d_daily_day' % i_] = np.array(dd); Z['%d_daily_usd' % i_] = np.array([a[9][d][0] for d in dd])
        Z['%d_daily_known_share' % i_] = np.array([a[9][d][1] for d in dd])
        H = a[13]
        if H is not None:
            Z['%d_hl_days' % i_] = np.array(sorted(H['days'])); Z['%d_hl_lt_s' % i_] = H['lt']; Z['%d_hl_usd' % i_] = H['usd']; Z['%d_hl_side' % i_] = H['side']
        meta.append((i_, coin, t, t0, side, a[4], 'yes' if H is not None else 'no', x['run_pct'][j], x['forced_usd_log'][j], x['n_flushes'][j]))
    np.savez_compressed(os.path.join(out_dir, 'P2B_INPUTS.npz'), **Z)
    with open(os.path.join(out_dir, 'P2B_ALARMS.tsv'), 'x') as fh, open(os.path.join(out_dir, 'P2B_KEY.tsv'), 'x') as fk:
        fh.write('i\tcoin\tt_alarm\tonset_t\tside\tT5_row0_end\thl_file\n'); fk.write('i\tcoin\tt_alarm\trun_pct\tforced_usd_log\tn_flushes\n')
        for i_, coin, t, t0, side, T5, hl, r1, r2, r3 in meta:
            fh.write('%d\t%s\t%d\t%d\t%d\t%d\t%s\n' % (i_, coin, t, t0, side, T5, hl)); fk.write('%d\t%s\t%d\t%.17g\t%.17g\t%.17g\n' % (i_, coin, t, float(r1), float(r2), float(r3)))
    rep.append('P2B INPUTS %d alarms (seed %d) for a fresh blind reader; the tool\'s values kept apart in P2B_KEY.tsv' % (len(pick), SEED_P2B))
    sys.path.insert(0, AP.CTX_DIR)
    import alarm_context as AC
    try:
        cx = AC.read(out_root, code_dir, 'A02', '20250901', '20251231', values=['burst_log_usd'])
        ck = {(c, int(round(t))) for c, t, td in zip(cx['coin'], cx['t_alarm'], cx['t_decision']) if abs(td - t) < 1e-6}
        rep.append('JOIN EPI.A02 alarms with CTX.A02 rows at decision 0: %d of %d' % (sum(1 for kk in key if kk in ck), n))
    except Exception as e:
        rep.append('JOIN not read: %s %s' % (type(e).__name__, str(e)[:200]))
    with open(os.path.join(out_dir, 'PROOF_RESULTS_RUN.tsv'), 'x') as fh:
        fh.write('value\tproof\tresult\treceipt\tutc\n')
        for v, pf, r in res:
            fh.write('%s\t%s\t%s\t%s\t%s\n' % (v, pf, r, receipt, now))
    with open(os.path.join(out_dir, 'PROOF_REPORT.txt'), 'x') as fh:
        fh.write('\n'.join(rep) + '\n')
    print('\n'.join(rep))
    print('RESULTS', {r: sum(1 for _, _, q in res if q == r) for r in ('PASS', 'FAIL')})


if __name__ == '__main__':
    main(*sys.argv[1:9])
