# test_alarm_profile_ed1_1.py: new edition by SCOUT for the clean release (30 Oct 2026; the owner 23:07 Berlin: "All alarm tools should work from the release
# folder only"). Owner QUANT. Old file: test_alarm_profile.py 5e22427c38f8c76c, never edited. Changed: runs against alarm_profile_ed1_1, alarm_context_ed1_1, profile_split_ed1_1 and mutants_alarm_profile_ed1_1 (the imports); class PathsFromCaller tests the new path code. Every other test is the old one, unchanged.
"""tests for tools/alarm_profile (QUANT 22 Oct 2026). PROOF P1 (planted, the answer known by hand) for every value, the mirror (a push
down reads as a push up), known-at (1e12 after the alarm changes nothing), the second computation (episode_twin) equal on planted and
random episodes, the run start cases of a02_run_start_v1, the catalog, the profiles and proof cards, and the one format (lab3.write /
lab3.days): build, read back, generated once (UP TO DATE), the same sha16s twice, sealed days refused, memory.
  python3 -B test_alarm_profile.py [lab3 code dir]      (the one-format tests need lab3 and pyarrow; they are skipped without them)"""
import datetime as dt, json, math, os, sys, tempfile, tracemalloc, unittest
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__)); sys.path.insert(0, HERE)
import episode_blocks as EB
import episode_twin as TW
import alarm_profile_ed1_1 as AP

LAB3 = sys.argv.pop(1) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.environ.get('LAB3_CODE', '')
NAN = float('nan')


def day0(d):
    return int(dt.datetime.strptime(d, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())


D = '20251015'; P = '20251014'; T5 = day0(P); T = day0(D) + 43200; T0 = T - 120


def lp_of(s, t=T, after=False, bounce=False, pause=False):
    """the planted push-signed log price (relative to 100) at time s: a +-0.1 pct zigzag (15 min halves) to 10 h before the alarm, a
    3 min spike to +1 pct, flat 0 from t - 35820 s, the run from t - 3000 s (+0.06 pct a minute), the burst from t - 150 s (+0.3 pct a
    minute) to t - 30 s, a giveback of 0.1 pct to the alarm (1 pct with bounce=True: more than h = 0.6 pct); after the alarm flat (or
    +-5 when after=True). pause=True: the run rises to 0.6 pct at t - 2400 s, creeps 0.01 pct to t - 360 s (34 min, no progress of a
    normal move), then pushes to the burst start's 2.85 pct in 210 s"""
    if s > t:
        return (5.0 if int(s) % 2 else -5.0) if after else 0.0335
    if s < t - 36000:
        m = math.floor((s - (t - 90000 + 450)) / 900.0)
        return 0.001 if m % 2 == 0 else -0.001
    if s < t - 35820:
        return 0.010
    if s < t - 3000:
        return 0.0
    if s < t - 150:
        if pause and s >= t - 2400:
            return 0.006 + 0.0001 * (s - (t - 2400)) / 2040.0 if s < t - 360 else 0.0061 + 0.0224 * (s - (t - 360)) / 210.0
        return 0.0006 * (s - (t - 3000)) / 60.0
    if s < t - 30:
        return 0.0285 + 0.003 * (s - (t - 150)) / 60.0
    return 0.0345 - (0.010 if bounce else 0.001) * (s - (t - 30)) / 30.0


def planted(side=+1, after=False, hl=True, bounce=False, pause=False):
    """the raw inputs of one planted alarm (the Ep / twin arguments)"""
    k0 = (T0 - T5) // 5; kt = (T - T5) // 5; k1 = k0 - 5; n = 2 * 17280
    xf = np.zeros(n); xo = np.zeros(n)
    for k, v in ((k0 - 5, 10000), (k0 - 4, 5000), (k0, 15000), (k0 + 6, 40000), (k0 + 7, 30000), (k0 + 8, 20000), (k0 + 14, 50000),
                 (k1 - 100, 2500), (k1 - 721, 500)):
        xf[k] = v
    xo[k0 + 2] = 3000; xo[k0 + 20] = 7000
    if after:
        xf[kt + 1:] = 1e12; xo[kt + 1:] = 1e12
    tp0 = day0('20251013'); te = np.arange(tp0 + 3, T + 601, 3, dtype=np.int64)
    px = np.array([100.0 * math.exp(side * lp_of(float(s), after=after, bounce=bounce, pause=pause)) for s in te])
    daily = {'20251007': (9e9, 1.0), '20251008': (100000.0, 1.0), '20251009': (200000.0, 1.0), '20251010': (300000.0, 1.0),
             '20251011': (400000.0, 1.0), '20251012': (500000.0, 1.0), '20251013': (600000.0, 1.0), '20251014': (700000.0, 0.5)}
    oi_t = T5 + 60.0 * np.arange(2 * 1440); oi_v = np.full(len(oi_t), 1e6); oi_c = np.zeros(len(oi_t))
    for dt_s, v in ((-120, 990000.0), (-60, 985000.0), (0, 980000.0)):
        oi_v[oi_t == T + dt_s] = v
    if after:
        oi_v[oi_t > T] = 1.0
    tb = T - 150; H = None
    if hl:
        lt = [tb + 10, tb + 50, tb - 100, tb + 20, tb - 500]; usd = [1000.0, 2000.0, 500.0, 300.0, 7.0]; sd = [side, side, side, -side, side]
        if after:
            lt.append(T + 5); usd.append(1e9); sd.append(side)
        H = dict(days={'20251014', '20251015'}, lt=np.array(lt, float), usd=np.array(usd), side=np.array(sd, float))
    return ('SOL', T, T0, side, T5, xf, xo, te * 1_000_000, px, daily, oi_t, oi_v, oi_c, H)


def ep_values(args):
    return {k: float(v[0]) for k, v in EB.run([EB.Ep(*args[:13], hl=args[13])]).items()}


def twin_values(args):
    return TW.twin(*args[:13], hl=args[13])


def expected(side=+1):
    ext = 0.0345; xs = 0.0018; xt = 0.0335; xb = 0.0285
    return dict(
        normal_move_pct=0.2, run_pct=(xt - xs) * 100, run_norm=(xt - xs) * 100 / 0.2, run_age_min=47.0, run_capped=0.0,
        pre_move_pct=(xb - xs) * 100, burst_move_pct=(xt - xb) * 100, forced_share=(xt - xb) / (xt - xs),
        giveback_pct=(ext - xt) * 100, giveback_share=(ext - xt) / (ext - xs),
        burst_s=150.0, onset_to_alarm_s=120.0, burst_speed_pct_min=0.2, pre_speed_pct_min=0.06, speed_ratio=0.2 / 0.06,
        burst_speed_vs_normal=15.0, max_move_60s_pct=0.3,
        forced_usd_log=math.log10(170000), peak15_usd_log=math.log10(90000), peak60_usd_log=math.log10(140000), size_vs_bar=7.0,
        size_vs_week=170000 / 350000.0, growth=140000 / 30000.0, pre_forced_usd_log=math.log10(2500),
        peak_s=70.0, peak_to_alarm_s=80.0, n_flushes=2.0, active_share=7 / 30.0, top5s_share=50000 / 170000.0,
        other_usd_log=4.0, other_share=10000 / 180000.0,
        oi_chg_burst_pct=-2.0, burst_vs_oi_bp=170000 / (1e6 * 100 * math.exp(side * xb)) * 1e4,
        hl_forced_usd_log=math.log10(3000), hl_other_usd_log=math.log10(300), hl_lead_s=100.0)


def same(a, b, tol=1e-9):
    return (math.isnan(a) and math.isnan(b)) or (not math.isnan(a) and not math.isnan(b) and abs(a - b) <= tol * max(1.0, abs(a)))


class Planted(unittest.TestCase):
    def check(self, got, want, tol=1e-9):
        bad = {k: (got.get(k), w) for k, w in want.items() if not same(got.get(k, NAN), w, tol)}
        self.assertEqual(bad, {})
        self.assertEqual(sorted(got), sorted(want), 'a value without its planted answer')

    def test_push_up(self):
        self.check(ep_values(planted(+1)), expected(+1))

    def test_push_down_mirror(self):
        self.check(ep_values(planted(-1)), expected(-1))

    def test_known_at(self):
        a = ep_values(planted(+1)); b = ep_values(planted(+1, after=True))
        self.assertEqual({k: v for k, v in a.items() if not same(v, b[k], 0)}, {})

    def test_cut_keeps_nothing_after_the_alarm(self):
        a = planted(+1, after=True); e = EB.Ep(*a[:13], hl=a[13])
        self.assertEqual(len(e.xf), e.kt + 1); self.assertEqual(len(e.xo), e.kt + 1)
        self.assertLess(np.nanmax(e.xf), 1e12); self.assertLess(np.nanmax(e.xo), 1e12)
        self.assertLessEqual(int(e.te_us.max()), T * 1_000_000); self.assertLessEqual(float(e.oi_t.max()), T)
        self.assertLessEqual(float(e.hl['lt'].max()), T)
        self.assertEqual(e.T5 + 5 * e.kt, T); self.assertEqual(e.T5 + 5 * e.k0, T0)

    def test_twin_planted(self):
        for side in (+1, -1):
            self.check(twin_values(planted(side)), expected(side))
            self.check(twin_values(planted(side, after=True)), expected(side))

    def test_no_print_in_the_onset_window(self):
        a = list(planted()); xf = a[5].copy(); k0 = (T0 - T5) // 5
        xf[k0 - 11:k0 + 1] = 0.0; xf[k0] = 0.0; a[5] = xf
        v = ep_values(a)
        for k in ('burst_s', 'forced_usd_log', 'burst_move_pct', 'oi_chg_burst_pct', 'hl_forced_usd_log', 'active_share'):
            self.assertTrue(math.isnan(v[k]), k)
        self.assertEqual(v['onset_to_alarm_s'], 120.0)
        self.assertEqual({k: x for k, x in v.items() if not same(x, twin_values(a)[k])}, {})

    def test_hole_in_the_burst(self):
        a = list(planted()); xf = a[5].copy(); k0 = (T0 - T5) // 5; xf[k0 + 10] = NAN; a[5] = xf
        v = ep_values(a)
        self.assertTrue(math.isnan(v['forced_usd_log'])); self.assertTrue(math.isnan(v['top5s_share']))
        self.assertAlmostEqual(v['peak15_usd_log'], math.log10(90000), places=12)      # the peaks skip windows with the hole
        self.assertEqual({k: x for k, x in v.items() if not same(x, twin_values(a)[k])}, {})

    def test_week_needs_five_days(self):
        a = list(planted()); dl = dict(a[9]); dl['20251008'] = (1.0, 0.5); dl['20251009'] = (1.0, 0.5); a[9] = dl
        self.assertTrue(math.isnan(ep_values(a)['size_vs_week']))

    def test_oi_carried_or_one_minute(self):
        a = list(planted()); c = a[12].copy(); c[a[10] == T] = 1.0; a[12] = c
        v = ep_values(a); self.assertTrue(math.isnan(v['oi_chg_burst_pct'])); self.assertFalse(math.isnan(v['burst_vs_oi_bp']))
        a = list(planted()); keep = a[10] <= T - 180; a[10], a[11], a[12] = a[10][keep], a[11][keep], a[12][keep]
        self.assertTrue(math.isnan(ep_values(a)['oi_chg_burst_pct']))

    def test_hl_not_covered(self):
        a = list(planted()); h = dict(a[13]); h['days'] = {'20251015'}; a[13] = h       # the 3 min before the burst is on D: covered
        self.assertFalse(math.isnan(ep_values(a)['hl_forced_usd_log']))
        h = dict(a[13]); h['days'] = {'20251014'}; a[13] = h
        v = ep_values(a); self.assertTrue(math.isnan(v['hl_forced_usd_log'])); self.assertTrue(math.isnan(v['hl_lead_s']))
        self.assertTrue(math.isnan(ep_values(planted(hl=False))['hl_other_usd_log']))

    def test_bounce_after_the_extreme(self):
        """run start v2: a bounce of 1 pct (more than h = 0.6 pct) between the extreme (t - 30 s) and the alarm does not restart the run.
        By hand: the start stays where the move began (t - 2820 s, 47 min, x 0.0018), the run end is the extreme bin (t - 30, x 0.0345),
        the alarm's x is 0.0245, the burst start's 0.0285. (v1 restarted the run at the alarm: run 0, age 0, giveback 0.)"""
        ext, xs, xt, xb = 0.0345, 0.0018, 0.0245, 0.0285
        want = dict(run_pct=(xt - xs) * 100, run_norm=(xt - xs) * 100 / 0.2, run_age_min=47.0, run_capped=0.0,
                    pre_move_pct=(xb - xs) * 100, burst_move_pct=(xt - xb) * 100, forced_share=(xt - xb) / (xt - xs),
                    giveback_pct=(ext - xt) * 100, giveback_share=(ext - xt) / (ext - xs), pre_speed_pct_min=0.06,
                    burst_speed_pct_min=(xt - xb) * 100 / 2.5, speed_ratio=(xt - xb) * 100 / 2.5 / 0.06)
        for side in (+1, -1):
            a = planted(side, bounce=True); v = ep_values(a); w = twin_values(a)
            self.assertEqual({k: (v[k], x) for k, x in want.items() if not same(v[k], x)}, {})
            self.assertEqual({k: (v[k], w[k]) for k in v if not same(v[k], w[k])}, {})
            e = EB.Ep(*a[:13], hl=a[13]); self.assertEqual(e.run_end()[0], float(T - 30))
        e = EB.Ep(*planted(+1)[:13]); self.assertEqual(e.run_end()[0], float(T - 30))     # the 0.1 pct giveback: same end, same start as v1

    def test_run_end_is_the_alarm_without_giveback(self):
        a = list(planted()); te = a[7] // 1_000_000; px = a[8].copy()
        px[(te > T - 30) & (te <= T)] = 100.0 * math.exp(0.0345); a[8] = px          # flat at the extreme to the alarm: the latest is the alarm
        e = EB.Ep(*a[:13], hl=a[13]); self.assertEqual(e.run_end()[0], float(T))
        v = ep_values(a); w = twin_values(a)
        self.assertEqual({k: (v[k], w[k]) for k in v if not same(v[k], w[k])}, {})
        self.assertAlmostEqual(v['giveback_pct'], 0.0, places=12); self.assertEqual(v['run_age_min'], 47.0)

    def test_run_end_latest_on_ties(self):
        """two closes at the extreme (t - 120 s and t - 30 s) with a dip of 0.8 pct (more than h) between, then the bounce: the run end
        is the LATER one, so the dip is a turn and the run starts at its bottom (t - 60 s, 1 min); the earlier one would hide it (47 min)"""
        a = list(planted(bounce=True)); te = a[7] // 1_000_000; px = a[8].copy()
        px[te == T - 120] = 100.0 * math.exp(0.0345); px[(te > T - 120) & (te <= T - 60)] = 100.0 * math.exp(0.0265); a[8] = px
        e = EB.Ep(*a[:13], hl=a[13]); self.assertEqual(e.run_end()[0], float(T - 30))
        v = ep_values(a); w = twin_values(a)
        self.assertEqual(v['run_age_min'], 1.0)
        self.assertEqual({k: (v[k], w[k]) for k in v if not same(v[k], w[k])}, {})

    def test_run_end_from_the_burst_start(self):
        """the extreme counts from the burst start (t - 150 s), not the onset (t - 120 s): a spike to x 0.0425 at t - 129 s is the run
        end, so the later dip (0.8 pct, t - 120 to t - 60) comes after it and the run keeps its 47 min (giveback 1.8 pct); counted from
        the onset the dip would be a turn (1 min)"""
        a = list(planted(bounce=True)); te = a[7] // 1_000_000; px = a[8].copy(); E = lambda v: 100.0 * math.exp(v)
        px[te == T - 129] = E(0.0425); px[(te > T - 129) & (te <= T - 120)] = E(0.0345); px[(te > T - 120) & (te <= T - 60)] = E(0.0265)
        a[8] = px
        e = EB.Ep(*a[:13], hl=a[13]); self.assertEqual(e.run_end()[0], float(T - 129))
        v = ep_values(a); w = twin_values(a)
        self.assertEqual(v['run_age_min'], 47.0); self.assertAlmostEqual(v['giveback_pct'], (0.0425 - 0.0245) * 100, places=9)
        self.assertEqual({k: (v[k], w[k]) for k in v if not same(v[k], w[k])}, {})


    def test_pause_moves_the_start_to_the_final_push(self):
        """v3 PAUSE, by hand: swing start t - 2820 s (x 0.0018); progress at t - 2580 (0.0042 > 0.0018 + 0.002); then no close above
        0.0062 until t - 300 (0.0125): 2280 s >= 1800, a pause from t - 2580 to t - 360; its lowest 0.0042, the last point within one
        normal move of it is t - 360 (0.0061): the run starts 6 min before the alarm (the swing rule said 47)"""
        xs, xt, xb, ext = 0.0061, 0.0335, 0.0285, 0.0345
        want = dict(run_pct=(xt - xs) * 100, run_norm=(xt - xs) * 100 / 0.2, run_age_min=6.0, run_capped=0.0, pre_move_pct=(xb - xs) * 100,
                    burst_move_pct=(xt - xb) * 100, forced_share=(xt - xb) / (xt - xs), giveback_pct=(ext - xt) * 100,
                    giveback_share=(ext - xt) / (ext - xs), pre_speed_pct_min=(xb - xs) * 100 / 3.5, burst_speed_pct_min=0.2,
                    speed_ratio=0.2 / ((xb - xs) * 100 / 3.5))
        for side in (+1, -1):
            a = planted(side, pause=True); v = ep_values(a); w = twin_values(a)
            self.assertEqual({k: (v[k], x) for k, x in want.items() if not same(v[k], x)}, {})
            self.assertEqual({k: (v[k], w[k]) for k in v if not same(v[k], w[k])}, {})

    def test_pause_start_cases(self):
        f = EB.pause_start; ts = 60.0 * np.arange(8)
        self.assertEqual(f(ts, np.array([0.0, 2, 4, 6, 8, 10, 12, 14]), 0, 1.0, 1800), (0, False))       # progress every minute
        self.assertEqual(f(ts, np.array([0.0, 2, 2, 2, 2, 2, 2, 9]), 0, 1.0, 240), (6, True))           # 2 .. 2 for 5 min, then 9
        self.assertEqual(f(ts, np.array([0.0, 2, 1, 2, 1, 2, 1, 9]), 0, 1.0, 240), (6, True))           # the LAST low of the pause
        self.assertEqual(f(ts, np.array([0.0, 2, 2, 2, 5, 5, 5, 5]), 0, 1.0, 180), (7, True))           # the LAST pause, still going
        self.assertEqual(f(ts, np.array([0.0, np.nan, 2, 2, 2, 2, 9, 9]), 0, 1.0, 240), (5, True))       # holes are skipped


class RunStart(unittest.TestCase):
    """a02_run_start_v1's cases (the definition moved here unchanged)"""
    def test_cases(self):
        f = EB.run_start_index
        self.assertEqual(f(np.arange(11.0), 2.0), (0, False))
        self.assertEqual(f(np.array([-5.0, 0, 5, 4, 3, 2, 4, 8]), 2.0), (5, True))
        self.assertEqual(f(np.array([0.0, 4.0, 2.0, 6.0]), 2.0), (2, True))
        self.assertEqual(f(np.array([0.0, 5, 4, 8]), 2.0), (0, False))
        self.assertEqual(f(np.array([0.0, 1, -3, 5]), 2.0), (2, True))
        self.assertEqual(f(np.array([0.0, 6, 4, 2, 0, -1, 4]), 2.0), (5, True))
        x = np.array([0.0, -0.5, 0.0, -0.5, -0.4, 0.0, 3.0])
        self.assertEqual(f(x, 2.0, 0.2), (4, False)); self.assertEqual(f(x, 2.0, 0.0), (3, False))
        self.assertEqual(f(np.array([np.nan, 0.0, 5, np.nan, 2, 4]), 2.0), (4, True))


def random_episode(rng):
    """a random alarm: random-walk prices (3 s bins, 3 days), random liquidation rows with holes, a random burst, random OI and Hyperliquid fills"""
    side = int(rng.choice([-1, 1])); n = 2 * 17280; kt = 17280 + int(rng.integers(900, 17000)); k0 = kt - int(rng.integers(0, 200))
    t = T5 + 5 * kt; t0 = T5 + 5 * k0
    xf = np.where(rng.random(n) < 0.03, rng.exponential(3000, n), 0.0); xo = np.where(rng.random(n) < 0.02, rng.exponential(2000, n), 0.0)
    xf[k0 - 11:k0 + 1] += np.where(rng.random(12) < 0.4, rng.exponential(30000, 12), 0.0)
    xf[k0:kt + 1] += np.where(rng.random(kt - k0 + 1) < 0.3, rng.exponential(40000, kt - k0 + 1), 0.0)
    for x in (xf, xo):
        x[rng.random(n) < 0.002] = np.nan
    tp0 = day0('20251013'); te = np.arange(tp0 + 3, t + 1201, 3, dtype=np.int64)
    steps = rng.normal(0, 0.0004, len(te)); steps[rng.random(len(te)) < 0.0005] *= 40
    px = 50.0 * np.exp(np.cumsum(steps)); px[rng.random(len(te)) < 0.001] = 0.0
    keep = rng.random(len(te)) > 0.05; te, px = te[keep], px[keep]
    days = ['202510%02d' % d for d in range(5, 15)]
    daily = {d: (float(rng.exponential(5e5)), float(rng.choice([1.0, 0.95, 0.5]))) for d in days}
    oi_t = T5 + 60.0 * np.arange(2 * 1440); oi_v = 1e6 * np.exp(np.cumsum(rng.normal(0, 0.001, len(oi_t))))
    oi_v[rng.random(len(oi_t)) < 0.01] = np.nan; oi_c = (rng.random(len(oi_t)) < 0.1).astype(float)
    m = int(rng.integers(0, 40)); lt = t - rng.uniform(-600, 1200, m)
    H = dict(days=set(rng.choice(['20251014', '20251015'], size=int(rng.integers(1, 3)), replace=False).tolist()),
             lt=lt, usd=rng.exponential(1000, m), side=rng.choice([-1.0, 1.0], m)) if rng.random() < 0.8 else None
    return ('X', t, t0, side, T5, xf, xo, te * 1_000_000, px, daily, oi_t, oi_v, oi_c, H)


class TwinRandom(unittest.TestCase):
    def test_random_episodes(self):
        rng = np.random.default_rng(22102026); bad = []; known = {}
        for i in range(40):
            a = random_episode(rng); e = ep_values(a); w = twin_values(a)
            self.assertEqual(sorted(e), sorted(w))
            for k in e:
                known[k] = known.get(k, 0) + (not math.isnan(e[k]))
                if not same(e[k], w[k]):
                    bad.append((i, k, e[k], w[k]))
        self.assertEqual(bad, [])
        self.assertEqual(sorted(k for k, v in known.items() if v == 0), [], 'a value never known on 40 random episodes: the test would not see it')


class CatalogProfilesProofs(unittest.TestCase):
    def test_catalog_file(self):
        self.assertEqual(open(AP.CATALOG).read(), AP.catalog_text())

    def test_run_names_only_catalog_columns(self):
        self.assertEqual(sorted(ep_values(planted())), sorted(c[2] for c in AP.columns()))

    def test_profiles(self):
        self.assertEqual(AP.check_profiles(), [])

    def test_ctx_inputs(self):
        import inspect
        sys.path.insert(0, AP.CTX_DIR); sys.path.insert(0, os.path.join(AP.CTX_DIR, '..', 'alarms'))
        import context_blocks as CB
        src = {(lv, nm): inspect.getsource(f) for lv, nm, f in CB.BLOCKS}
        rows = AP._tsv(AP.CTX_INPUTS); ctx = {c[2]: c for c in AP.ctx_columns()}
        self.assertEqual(sorted(r['value'] for r in rows), sorted(ctx))
        for r in rows:
            lv, bl = ctx[r['value']][0], ctx[r['value']][1]
            self.assertEqual((r['level'], r['block']), (lv, bl), r['value'])
            for code in [x for x in r['inputs'].split(',') if x and x not in ('LIST', 'PRICE', 'TABLE:costs', 'TABLE:types')]:
                self.assertIn("'%s'" % code, src[(lv, bl)], '%s: %s is not read by its block' % (r['value'], code))

    def test_split_counts(self):
        """split: met, unknown (any input of the rule unknown), the cross of the first rule with the others; CTX values joined by alarm"""
        d = tempfile.mkdtemp(); rp = os.path.join(d, 'rules.tsv')
        open(rp, 'w').write('# rules\nname\trule\tmeaning\nF\t(forced_share >= 0.5) & (burst_move_pct > 0)\tforced\n'
                            'M\talts_with_push_15m >= 0.6\tmarket\n')
        t = np.array([day0('20251001'), day0('20251002'), day0('20251101'), day0('20251102')], float) + 60.0
        epi = {'coin': np.array(['A', 'B', 'C', 'D']), 't_alarm': t, 'forced_share': np.array([0.6, 0.2, np.nan, 0.9]),
               'burst_move_pct': np.array([0.5, 0.5, 0.5, -0.1])}
        ctx = {'coin': np.array(['A', 'B', 'C', 'D']), 't_alarm': t, 't_decision': t, 'alts_with_push_15m': np.array([0.7, 0.9, 0.1, np.nan])}
        import profile_split_ed1_1 as PS
        out = []; res = PS.split(None, None, 'A02', '20250901', '20251231', rp, epi=epi, ctx=ctx, log=out.append)
        self.assertEqual(res['F'][0].tolist(), [True, False, False, False]); self.assertEqual(res['F'][1].tolist(), [False, False, True, False])
        self.assertEqual(res['M'][0].tolist(), [True, True, False, False]); self.assertEqual(res['M'][1].tolist(), [False, False, False, True])
        cross = [l for l in out if l.startswith('CROSS')][0]
        self.assertIn('both     1', cross); self.assertIn('F only     0', cross); self.assertIn('M only     1', cross); self.assertIn('known both 2', cross)

    def test_every_mutant_applies(self):
        """each planted bug's text is in its file exactly once (J471130: one stale text was NOT APPLIED, so it tested nothing)"""
        import mutants_alarm_profile_ed1_1 as MU
        bad = [(i, what, open(os.path.join(HERE, f)).read().count(old)) for i, (f, what, old, new) in enumerate(MU.MUTANTS, 1)
               if open(os.path.join(HERE, f)).read().count(old) != 1]
        self.assertEqual(bad, [])

    def test_proof_cards(self):
        allrows = AP._tsv(AP.PROOFS); names = {c[2] for c in AP.columns()}
        rows = [r for r in allrows if not r['value'].startswith('CTX.')]; ctx = [r for r in allrows if r['value'].startswith('CTX.')]
        known = {'P1_PLANT', 'P2_TWIN', 'P2B_BLIND', 'P3_PRICE_RECORD', 'P4_EYE_RUN', 'P4_EYE_WAVES', 'P4_OI_LINE', 'P4_HL_LINE', 'P4_HL_SIGN'}
        self.assertEqual({r['value'] for r in rows}, names)
        self.assertEqual({r['proof'] for r in rows} - known, set())
        sys.path.insert(0, os.path.join(HERE, '..', 'alarm_context')); import alarm_context_ed1_1 as ACX           # A09: context output cards
        self.assertEqual({r['value'][4:] for r in ctx} - {c[2] for c in ACX.columns()}, set())
        self.assertEqual({r['proof'] for r in ctx} - {'O1_PLANT', 'O2_P09_MATCH'}, set())
        for v in names:
            got = {r['proof'] for r in rows if r['value'] == v}
            self.assertTrue({'P1_PLANT', 'P2_TWIN'} <= got, v)

    def test_status_open_until_results(self):
        st = AP.proof_status(None, results=os.devnull)
        self.assertTrue(all(st[('EPI', c[2])][0] == 'OPEN' for c in AP.columns()))


# ---------------------------------------------------------------- the one format
TEST_SEALED = (('20251201', '20251231', 'sealed for the test'),)


class FakeSource:
    """the planted inputs served by day, as LabSource serves the lab: 5 s rows A1.S01 / A1.S02 (the forced side's rows where the
    planted alarm pushed), minute OI, PRICE bins, daily totals and Hyperliquid fills"""
    def __init__(self, alarms, table=None):
        self.alarms = alarms; self.table = table; self.skipped = []; self.hl_dirs = ('fake',)
        self.reads = []

    def _ep(self, coin, day=None):
        for a in self.alarms:                                        # one alarm a coin: the coin's whole history is its planted one
            if a['coin'] == coin:
                return a
        return None

    def rows(self, code, d, coins, steps):
        self.reads.append((code, d))
        out = np.zeros((len(coins), steps))
        for i, c in enumerate(coins):
            a = self._ep(c, d)
            if a is None:
                continue
            args = a['args']; base = day0(d); t5 = args[4]
            if code in ('A1.S01', 'A1.S02'):
                forced = 'A1.S02' if a['side'] > 0 else 'A1.S01'; x = args[5] if code == forced else args[6]
                k = (base - t5) // 5
                if 0 <= k < len(x):
                    seg = x[k:k + steps]; out[i, :len(seg)] = seg
            elif code == 'E2.S02':
                m = (base - t5) // 60
                if 0 <= m < len(args[11]):
                    seg = args[11][m:m + steps]; out[i, :len(seg)] = seg
            elif code == 'E2.S03':
                m = (base - t5) // 60
                if 0 <= m < len(args[12]):
                    seg = args[12][m:m + steps]; out[i, :len(seg)] = seg
        return out, {'lab:day=%s/BASE' % d: '%016x' % (abs(hash((code, d))) % (1 << 60))}

    def prices(self, d, coins):
        out = {}
        for c in coins:
            a = self._ep(c, d)
            if a is not None:
                te, px = a['args'][7], a['args'][8]; b = day0(d) * 1_000_000; k = (te > b) & (te <= b + 86400 * 1_000_000)
                out[c] = (te[k], px[k])
        return out, {'lab:day=%s/PRICE' % d: '00000000000000a1'}

    def totals(self, d, coins):
        out = {}
        for c in coins:
            a = self._ep(c)
            v = a['args'][9].get(d, (0.0, 0.0)) if a else (0.0, 0.0)
            out[c] = (v[0], v[1], v[0], v[1]) if a else (0.0, 0.0, 0.0, 0.0)
        return out, {}

    def hl(self, coin, days):
        a = self._ep(coin)
        return (a['args'][13] if a else None), {'hl:HLF_%s.npz' % coin: '00000000000000b2'}


def fake_alarms(n_days=2, per_day=2, first='20251115'):
    out = []
    for j in range(n_days):
        d = AP.shift(first, j); shift_s = day0(d) - day0(D)
        for i in range(per_day):
            side = 1 if (i + j) % 2 == 0 else -1; coin = 'C%s%03d' % (d[4:], i)
            a = list(planted(side))
            a[0] = coin; a[1] = T + shift_s; a[2] = T0 + shift_s; a[4] = T5 + shift_s
            a[7] = a[7] + shift_s * 1_000_000; a[10] = a[10] + shift_s
            a[9] = {AP.shift(k, (day0(d) - day0(D)) // 86400): v for k, v in a[9].items()}
            h = dict(a[13]); h['lt'] = h['lt'] + shift_s; h['days'] = {AP.shift(x, (day0(d) - day0(D)) // 86400) for x in h['days']}; a[13] = h
            out.append(dict(coin=coin, t=a[1], side=side, onset_t=a[2], args=tuple(a)))
    return out


def write_alarms(path, alarms):
    with open(path, 'w') as f:
        f.write('candidate\tcoin\tt\tside\tonset_t\n')
        for a in alarms:
            f.write('D0\t%s\t%d\t%d\t%d\n' % (a['coin'], a['t'], a['side'], a['onset_t']))


@unittest.skipUnless(LAB3 and os.path.isdir(os.path.join(LAB3, 'lab3')), 'lab3 code dir not given')
class OneFormat(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, LAB3)
        from lab3 import write as LW, days as LD
        self.LW, self.LD = LW, LD; self.tmp = tempfile.TemporaryDirectory(); self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def build(self, root, alarms, table=None, first='20250101', last='20261231'):
        p = os.path.join(self.d, 'ALARMS.tsv'); write_alarms(p, alarms)
        return AP.build('lab', p, 'A02', first, last, root, src=FakeSource(alarms, table), write=self.LW.write_part,
                        load_catalog=self.LW.load_catalog, log=lambda *a: None, table=table)

    def test_build_read_back_and_once(self):
        al = fake_alarms(); root = os.path.join(self.d, 'r1')
        got = self.build(root, al); self.assertEqual(set(got.values()), {'WRITTEN'})
        x = AP.read(root, LAB3, 'A02', '20250101', '20261231', days_reader=self.LD.Days(root, 'research'))
        self.assertEqual(len(x['coin']), len(al))
        want = expected(+1)
        for i in range(len(al)):
            side = [a['side'] for a in al if a['coin'] == x['coin'][i] and abs(a['t'] - x['t_alarm'][i]) < 0.5][0]
            w = expected(side)
            for k, v in w.items():
                self.assertTrue(same(float(x[k][i]), v), (k, x[k][i], v))
        self.assertEqual(set(self.build(root, al).values()), {'UP TO DATE'})
        self.assertTrue(want)
        k = AP.read(root, LAB3, 'A02', '20250101', '20261231', days_reader=self.LD.Days(root, 'research'), with_known_at=True)
        self.assertTrue(np.all(k['known_at'] >= k['t_alarm']) and np.allclose(k['known_at'], k['t_alarm']))   # EPI is known at the alarm
        self.assertNotIn('known_at', x)

    def test_same_sha16_twice(self):
        al = fake_alarms(); r1, r2 = os.path.join(self.d, 'a'), os.path.join(self.d, 'b')
        self.build(r1, al); self.build(r2, al)
        for day in sorted(n for n in os.listdir(r1) if n.startswith('day=')):
            with open(os.path.join(r1, day, 'EPI.A02', 'index.json')) as f1, open(os.path.join(r2, day, 'EPI.A02', 'index.json')) as f2:
                i1 = json.load(f1); i2 = json.load(f2)
            self.assertEqual({c: r['files'] for c, r in i1['readings'].items()}, {c: r['files'] for c, r in i2['readings'].items()})
            self.assertEqual((i1['seal'], i1['sources']), (i2['seal'], i2['sources']))

    def test_sealed_days(self):
        al = fake_alarms(n_days=3, first='20251130')                 # 30 Nov, 1 Dec, 2 Dec
        root = os.path.join(self.d, 's')
        got = self.build(root, al, table=TEST_SEALED)
        self.assertEqual(got, {'20251130': 'WRITTEN', '20251201': 'REFUSED', '20251202': 'REFUSED'})
        al2 = fake_alarms(n_days=1, first='20260101')
        self.assertEqual(self.build(os.path.join(self.d, 's2'), al2, table=TEST_SEALED), {'20260101': 'REFUSED'})   # the day after
        open_root = os.path.join(self.d, 'o'); self.build(open_root, fake_alarms(n_days=1, first='20251203'))
        with self.assertRaises(PermissionError):
            AP.read(open_root, LAB3, 'A02', '20251101', '20251231', days_reader=self.LD.Days(open_root, 'research'), table=TEST_SEALED)

    def test_memory(self):
        al = []
        for j in range(4):
            for a in fake_alarms(n_days=1, per_day=100, first=AP.shift('20251101', j)):
                al.append(a)
        tracemalloc.start(); self.build(os.path.join(self.d, 'm'), al); peak = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
        self.assertLess(peak, 300 * 2 ** 20, 'peak %.0f MB' % (peak / 2 ** 20))



class PathsFromCaller(unittest.TestCase):
    """the new path code (SCOUT, clean release): the research root and the Hyperliquid fills root come from the caller"""

    def test_no_machine_default(self):
        for k in ('OUT_ROOT', 'HL_ROOT', 'HL_DIRS'):
            self.assertNotIn(k, vars(AP))
        for bad in (None, ''):
            with self.assertRaisesRegex(ValueError, 'OUT_ROOT_REQUIRED'):
                AP.build('lab', 'no_alarms.tsv', 'A02', '20251015', '20251015', bad, src=object())

    def test_fills_folders_from_the_root(self):
        for none in (None, '', '-'):
            self.assertEqual(AP.hl_dirs_of(none), ())
        names = ('01', '02', '03', 'd3_01', 'd3_02', 'd3_03', 'd3_04', 'd3_05')
        self.assertEqual(AP.hl_dirs_of('FILLS'), tuple(os.path.join('FILLS', n) for n in names))

    def test_build_hands_the_fills_to_the_source_and_names_this_edition(self):
        d = tempfile.mkdtemp(); p = os.path.join(d, 'ALARMS.tsv'); write_alarms(p, fake_alarms()); seen = []

        class Stop(Exception):
            pass

        def fake_source(lab_root, code_dir, table=None, hl_dirs=()):
            seen.append(hl_dirs); raise Stop()
        real = AP.LabSource; AP.LabSource = fake_source
        try:
            with self.assertRaises(Stop):
                AP.build('lab', p, 'A02', '20250101', '20261231', d, write=lambda *a, **k: None, load_catalog=lambda p: None,
                         log=lambda *a: None, hl_root='FILLS')
        finally:
            AP.LabSource = real
        self.assertEqual(seen, [AP.hl_dirs_of('FILLS')])
        self.assertEqual(AP.CODE_FILES[0], 'alarm_profile_ed1_1.py')
        self.assertTrue(os.path.isfile(os.path.join(AP.HERE, AP.CODE_FILES[0])))

    def test_profile_reads_the_context_through_this_edition(self):
        sys.path.insert(0, AP.CTX_DIR); import alarm_context_ed1_1 as ACN
        name = next(k for k, v in AP.load_profiles().items() if any(tool == 'CTX' for _, tool, _, _ in v))

        class Stop(Exception):
            pass

        def stop(*a, **k):
            raise Stop()
        real = ACN.read; ACN.read = stop
        try:
            with self.assertRaises(Stop):
                AP.profile(tempfile.mkdtemp(), 'CODE', 'A02', '20251015', '20251015', name, epi={'coin': []}, log=lambda *a: None)
        finally:
            ACN.read = real

    def test_command_needs_the_out_root_and_the_fills_root(self):
        for n in (7, 8):
            with self.assertRaisesRegex(SystemExit, 'hl fills root'):
                AP.main(['build', 'LAB', 'CODE', 'A.tsv', 'A02', '20251015', '20251015', 'OUT'][:n])
        seen = []
        real = AP.build; AP.build = lambda *a, **k: seen.append((a, k)) or {}
        try:
            AP.main(['build', 'LAB', 'CODE', 'A.tsv', 'A02', '20251015', '20251016', 'OUT', '-'])
        finally:
            AP.build = real
        self.assertEqual(seen[0][0], ('LAB', 'A.tsv', 'A02', '20251015', '20251016', 'OUT')); self.assertEqual(seen[0][1]['hl_root'], '-')

if __name__ == '__main__':
    unittest.main()
