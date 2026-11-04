"""fl_read_v11.py (SCOUT 30 Oct 2026, tools/alarm_first_look; the owner 08:30 Berlin: ALARM FIRST LOOK). TEST, NOT REVIEWED.
Edition 11 = edition 10 (below) + the fires' waves are the grade's (made by mk_v11.py from fl_read_v10.py). The owner, 30 Oct 2026
21:11 Berlin: "30 minutes" (one wave length for every tool, ALARM_PIPELINE_V1 D3). A fire more than GRADE_WAVE_S = 1800 s after the
previous fire (any coin) starts a wave, computed by labcore's waves (team/RESEARCH/tools/labcore/waves.py, THE ONE wave module), the
same waves make_random_v3 weighs the random by (each grade wave's random sums to 1). Before, the fires were in md_v1's 15 min waves
while the random counted 30 min waves (review B S5). Given ids (edition 10) still replace them.
Edition 10 (fl_read_v10.py, SCOUT 30 Oct 2026):
Edition 10 = edition 9 (below) + Look takes the fires' wave ids (made by mk_v10.py from fl_read_v9.py). Look(..., wid=None) keeps
md_v1's waves, so every real reading is unchanged; given ids (one non-negative integer a fire) replace them, and this file still makes
each wave's month and day (its first fire's). For the ladder (fair_v3.py): review B (30 Oct 2026) found its made-up fires formed their
own waves; with wid each keeps its real fire's wave.
Edition 9 (fl_read_v9.py, SCOUT 30 Oct 2026):
Edition 9 = edition 8 (below) + Jan-Apr CONFIRMS what Sep-Dec found (made by mk_v9.py from fl_read_v8.py). The owner, 30 Oct 2026
19:21 Berlin, "Okay" to testing it: FDA2APR's side beat random in 8 of 8 months but missed Jan-Apr's z 2. In Jan-Apr a bar passes
at z >= CONFIRM_Z_MIN = 1 (3 of 4 months, BROAD and COUNT as before); Sep-Dec keeps z >= NET_Z_MIN = 2. PERIODS9 holds each period
with its z line; bar8 and verdict8 take z_min (default NET_Z_MIN = edition 8). RULE_9 in FL_RULE9.tsv beside RULE_8 (FL_RULE8.tsv
unchanged, one writer for both). The ladder fair_v2.py proves the z lines on made-up alarms.
Edition 8 (fl_read_v8.py, SCOUT 30 Oct 2026):
Edition 8 = edition 7 (below) + two bars (made by mk_v8.py from fl_read_v7.py). The owner, 30 Oct 2026 17:40 Berlin: "can be that
one alarm has one of both right? maybe we should have more than one bar and a way of proving that we keep the edges and remove what
has no edge"; 17:44 "okay build it". An alarm passes on either bar; the label names which (RULE_8: SIZE+SIDE, SIZE, SIDE; NEEDS MORE
MONTHS (<bars>) when a bar passes Sep-Dec only; NOT PASS). Each bar passes a period when ALL hold:
 - SIZE (when): edition 7's MOVES: on busy fires, price moves 4c either way within 1 h more often than at equally busy random moments
   (match7: the band pairs of the normal move and the last hour's range); NOT RUN without the BZ tables;
 - SIDE (which way): edition 6's direction: on every fire with a cost, the lean's 1 h race (+1 offer first, -1 heat first, 0
   neither) minus its wave month's random (pre-fire moments out, weighted), as Look.net_test reads it (side8);
 and, for each bar, from its per-fire excess (stats7): STEADY (the wave mean above 0 in at least MONTHS_MIN = 3 of the 4 months, a
 month with fewer than BUSY_WAVES_MIN = 10 waves THIN; z >= NET_Z_MIN = 2, waves clustered by day plus the random's error), BROAD
 (above 0 without the 2 coins that add most, and without the 5 best days), COUNT (WAVES_MIN = 30 waves with a 1 h value, all fires,
 every month). A bar passes when it passes Sep-Dec AND Jan-Apr. fair_v1.py runs both bars on made-up alarms (no edge; planted edges)
 to show how often each lets a no-edge alarm through and how often it catches a planted one.
Edition 7 (fl_read_v7.py, SCOUT 30 Oct 2026):
Edition 7 = edition 6 (below) + the alarm's criteria the owner agreed on 30 Oct 2026 Berlin (made by mk_v7.py from fl_read_v6.py):
15:44 "the alarm has to be valid for both" (follow or fade: the side is the strategy's call); 16:00 the criteria; 16:05-16:06 on
busy fires only, "okay, let's do that". An alarm marks WHEN: on the four design months (and, beside, the same frozen rule on the four
forward months: AGAIN) it passes when ALL hold:
 - MOVES: on busy fires (the coin's normal 15 min move >= BUSY_MIN_C = 1.12c, known at the fire), price moves 4c either way within
   1 h (the 4c race decided within 60 min: OBH4_60M is +1 or -1) more often than at equally busy random moments. Equally busy: the
   busy random moments (pre-fire moments out, the random's weights) in the same band pair: the normal move in c cut in thirds
   (NORM_Q) and the last hour's range in normal moves cut at REC_Q (7 bands, the top one the busiest 1 pct); the bands are the
   period's busy random's own (weighted, the four months pooled). A fire is priced by its own month's random in its band pair,
   or, when that is thinner than CELL_MIN_NEFF = 20 (effective count), by the four months' random in that band pair (fallback);
   a fire busier or calmer than every random moment of the period (either value) is unmatched (outside: no equally busy random).
   The random moments are matched to the fires' coins and hours by construction (the grade's
   random). Both values come from busy_v1.py (BZ tables): the normal move is alarm_profile's own (busy_v1 proves it on the fires).
   Per fire: hit minus the band pair's random share; per wave the mean over its matched busy fires; a fire whose band pair is
   thinner than 20 even over the four months is unmatched (counted);
 - STEADY: the wave mean above 0 in at least MONTHS_MIN = 3 of the 4 months (a month with fewer than BUSY_WAVES_MIN = 10 matched
   busy waves is THIN: not judged, it cannot count), and over the four months together z >= NET_Z_MIN = 2 (waves clustered by day,
   plus the random's error per band pair);
 - BROAD: the four months' wave mean stays above 0 without the 2 coins that add most to it, and without its 5 best days;
 - COUNT: at least WAVES_MIN = 30 waves (all fires, with a 1 h value) in every month.
 Beside, never a rule: the lean (edition 6's direction: offer-first minus heat-first against the random, its months and z), the same
 MOVES matched on the normal move only (how much the last hour explains), the matched share, and how equal the busyness is after
 matching (recent_ratio, normal_ratio: the matched fires' mean last-hour range and normal move over their band pairs' random mean; 1 =
 equal; above 1: the fires sit busier inside their bands), the share priced by the four months' random (fallback_share) and the
 share outside (outside_share). No loss check (15:18: heat is a loss
 only once a strategy picks a side). The overall RULE_7: PASS = Sep-Dec PASS and Jan-Apr PASS; NEEDS MORE MONTHS = Sep-Dec PASS only;
 NOT PASS = Sep-Dec not PASS; NOT RUN without both BZ tables (or a BZ table built from another list, or not joining one to one).
 A BZ folder inside a finished job's receipts (its STAGES.tsv ends 0) is read.
Edition 6 (fl_read_v6.py, SCOUT 30 Oct 2026):
Edition 6 = edition 5 (below) + the PASS rule the owner agreed on 30 Oct 14:58 Berlin: "direction every month, money only when
busy" (made by mk_v6.py from fl_read_v5.py). On the four design months (and, beside, the same frozen rule on the four forward
months) an alarm passes when ALL hold:
 - DIRECTION, all fires: offer-first minus heat-first beats the month's random (pre-fire moments out) in at least MONTHS_MIN = 3
   of the 4 months, and over the four months together z >= NET_Z_MIN = 2 (waves clustered by day);
 - MONEY, busy fires only (the coin's normal 15 min move >= BUSY_MIN_C = 1.12c, known at the fire): the median offer at 1 h
   >= OFFER_MIN_C = 4c in at least 3 of the 4 months;
 - NO LOSS: no month where the busy fires' edge (offer minus heat at 1 h) is below the month's random edge;
 - SPREAD: on the busy fires' edge above random, the top 2 coins, top 5 waves and best 5 days are each under half;
 - COUNT: at least WAVES_MIN = 30 waves (all fires) in every month.
 A month with fewer than BUSY_WAVES_MIN = 10 busy waves is THIN: not judged for money or loss (it cannot count as a money month).
 Without the AP file (no normal move, so no busy filter) the rule is NOT RUN. The edition 5 verdict (FIRST_LOOK) stays beside.
Edition 5 (fl_read_v5.py, SCOUT 30 Oct 2026):
Edition 5 = edition 4 (below) + the reviews of 30 Oct (F, G, I) and the owner's 12:46 "okay" (made by mk_v5.py from fl_read_v4.py):
 - rule 2's second leg is a test across waves (reviewer G S1, S2; the owner's yes): a month passes it when its offer-first minus
   heat-first (per wave: +1 offer first, -1 heat first, 0 neither, at 1 h) is above the month's random (> 0) AND the same over the
   month's whole period (Sep-Dec or Jan-Apr) is at least NET_Z_MIN = 2 standard errors above the random; the random here leaves out the
   moments in the hour before a same-coin fire of the alarm (they see the next fire's burst); the error: the waves' values clustered by
   day (the alarm) plus each month's random by its effective count (Kish), weighted by the month's waves. The 5-point leg is gone; the
   full-random number (net_first_vs_random_pts) stays printed beside;
 - the busy filter's cut is BUSY_MIN_C = 1.12c, set on single fires the way this reader applies it (studies/busy_cut_v1.py,
   results/BUSY_CUT_20261030T114941Z: 1.1136 rounded up, so every design month keeps a 4c median offer);
 - PUSH / NO PUSH (reviewers I MUST 1, G S4): the share of design waves whose run went the side's way (run_pct > 0, per wave the mean of
   its fires) is at least PUSH_SHARE_MIN = 0.8; random sides give about 0.6; the median run in normal moves stays beside;
 - refused (G M1, protocol R11): a receipts folder whose STAGES.tsv has no "end 0" line (a job still writing); the output is written
   into <out>.part and renamed at the end; a refused run removes its own .part folder, so it publishes no number (F S3, rule R8);
 - beside, never a rule: the months whose random covers under 0.8 of the grade's waves are named (F S2; G S3: September, where the
   grade could not match the fires of 10-16 Sep);
 - docs (F S1): a PERFIRE that differs from TARGETS_FL only makes the race NOT RUN (it is not a refusal).
Edition 4 = edition 3 (below) + two changes the owner asked for on 30 Oct (made by mk_v4.py from fl_read_v3.py):
 - rule 2's second leg (the owner 11:28 "yes, okay"): offer-first minus heat-first (at 1 h, per wave, the mean of +1 offer first, -1 heat
   first, 0 neither) beats the month's random by 5 points or more (NET_MIN), in place of "the lean offer comes first more often than
   random": that leg was passed by the zero-edge controls SYN0A and SYN0B in 8 of 8 design months, because fires sit in busier
   moments where both levels are touched more; the offer-first shares stay printed beside;
 - the busy filter beside each alarm (the owner 11:51 "We should include it next to each alarm"): the same PASS rule on the fires whose
   coin's normal 15 min move (alarm_profile's normal_move_pct: the median absolute 15 min move over the 24 h ending 1 h before the
   fire, known at the fire) is at least BUSY_MIN_C = 1.17c; the random stays the month's whole random; NOT RUN without the AP file.
   1.17 = the edge chosen on Sep-Dec, all real alarms pooled, by studies/why_months_v2.py (WHY_THRESHOLDS.tsv 1.1687, rounded).
Edition 3 of the reader = fl_read_v2.py + the two reviews of 30 Oct (reviewer C: FAIL, 3 MUST; reviewer D: PASS, 4 SHOULD):
 - every item by month (C MUST 1): the windows table, both sides' speeds and the random's, the concentration shares, and the results
   without DASH, VVV, ZEC and without the top 5 waves are written for each month as well as Sep-Dec and Jan-Apr;
 - item 1 both ways and honest (C MUST 3): the move spent from alarm_profile edition 2.2 in its two run-end modes, AP_<code>.tsv (the push
   still going at the fire: the run end in its last 60 s) and APH_<code>.tsv (the hour's extreme: the run net of a pullback, with the
   giveback); PUSH or NO PUSH: an alarm whose median run (per wave, design months) is under one normal 15 min move did not fire on a
   price push (its side means something else, e.g. the funding sign): its move spent is not a move;
 - beside the rule, never a rule: the random's coverage of the grade's waves by month (flag under 0.8, D S1); the share of the random's
   weight sitting in the hour before a same-coin fire of the same alarm, and the result without those moments (D S2); fires dropped per
   month (no cost row; no 1 h outcome) (C S2, D S3); the race NOT RUN with its reason when the PERFIRE is missing or changed (C S5);
 - refusals (C S4, D S4): the A and R tables must hold exactly the batch lists' (coin, t, side); every random row has its weight and no
   weight is left over; the lists, weights and PERFIRE must match TARGETS_FL's sha16s; the coin's c must equal the outcome tool's own
   unit__c on every fire; an AP file that does not join the fires one to one, or holds a fire twice, makes only the move NOT RUN;
 - names (C S3, D N8): waves_all (every wave of the month) and waves_1h (waves with a 1 h value: the >= 30 rule counts these).
Everything else is v2's code: the PASS rule (the owner's words), waves (md_v1, 900 s, a wave's month and day are its first fire's; edition 11:
labcore's, 1800 s), costs.
Choices the owner did not specify, written here: the month edge is the mean over waves of (offer - heat at 1 h); the concentration shares
are of the design edge above that month's random (they pass 1 when the total is small); a month holds only when both rule 1 and rule 2
hold; the 30-waves rule counts design months only; the random's weights count 30 min grade waves, the fires 15 min waves (edition 11:
30 min, the same waves); speed is timed
from the outcome tool's entry bar (about 6-9 s after the fire).
  python3 -B fl_read_v3.py <TARGETS_FL.tsv> <ALARM_DESIGN dir> <COSTS_PER_COIN_V1.tsv> <out dir (new)> <receipts dir> [<receipts dir> ...]
  (receipts dirs: the FLOUT parts (A<code>.tsv.gz, R<code>.tsv.gz) and the APROF22 parts (AP_<code>.tsv, APH_<code>.tsv); one file per
  code and kind)"""
import csv, gzip, hashlib, json, math, os, re, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'money_direction'))
import md_v1 as M   # noqa: E402  months, costs, the gz table reader (edition 11: not its waves)
sys.path.append(os.path.dirname(HERE))                    # team/RESEARCH/tools, for labcore
from labcore import waves as WV   # noqa: E402  edition 11: THE ONE wave module (the grade's waves)

VERSION = 'fl_read_v11'
WINDOWS = (1, 2, 3, 5, 10, 15, 20, 30, 60, 90, 120, 180)
OFFER_MIN_C = 4.0          # median offer within 1 h
EDGE_MIN_C = 2.0           # offer minus heat beats random by
NET_Z_MIN = 2.0            # or offer-first minus heat-first above random in the month and 2+ errors over its period (owner 30 Oct 12:46)
CONFIRM_Z_MIN = 1.0        # edition 9: Jan-Apr confirms a bar that Sep-Dec found at z >= 1 (owner 30 Oct 19:21 Berlin)
BUSY_MIN_C = 1.12          # the busy filter beside each alarm: the coin's normal 15 min move in c (the owner 30 Oct 11:51; busy_cut_v1)
PUSH_SHARE_MIN = 0.8       # PUSH when at least this share of design waves ran the side's way (run_pct > 0)
TOL = 1e-12                # the two bars above are met at equality despite float rounding
MONTHS_MIN = 3
SHARE_MAX = 0.5            # top 2 coins, top 5 waves, best 5 days: each under half
WAVES_MIN = 30
BUSY_WAVES_MIN = 10       # rule of 30 Oct: a month with fewer busy waves is THIN (not judged for money or loss)
NORM_Q = (1 / 3.0, 2 / 3.0)   # edition 7: the month's busy random's normal move (c units) cut in thirds (weighted)
REC_Q = (0.5, 0.8, 0.9, 0.95, 0.98, 0.99)   # edition 7: its last hour's range (normal moves) cut at these shares: 7 bands, the top the busiest 1 pct
CELL_MIN_NEFF = 20.0         # edition 7: a band pair prices a fire only when its random's effective count is at least this
HIT_H = 60                   # edition 7: price moves 4c either way within 60 min (the 4c race decided)
PTS_TOL = 1e-9               # edition 7: a mean within 1e-9 points of 0 is 0 (float rounding), never above it
BZ_COLS = ('normal_move_pct', 'range60_pct', 'move15_pct')   # busy_v1.py's values
EXCLUDE = ('DASH', 'VVV', 'ZEC')
RACE = ('5m', '15m', '1h')
AP_RE = re.compile(r'^(AP|APH)_([A-Za-z0-9]+)\.tsv$')
AP_COLS = ('run_pct', 'run_age_min', 'run_capped', 'giveback_pct', 'normal_move_pct', 'run_norm')
PUSH_MIN_NORM = 1.0        # median run (normal 15 min moves) under 1: NO PUSH
COVER_MIN = 0.8            # the random's weight per grade wave in a month: flagged under this
PRE_FIRE_S = 3600          # a random moment with a same-coin fire of the alarm within the next hour
GRADE_WAVE_S = 1800        # edition 11: a fire more than 30 min after the previous one (any coin) starts a wave (the grade's; owner 30 Oct 21:11)
C_TOL = 1e-9
PERIODS = tuple((m, (m,)) for m in M.DESIGN + M.FORWARD) + (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD))
PERIODS9 = (('Sep-Dec', M.DESIGN, NET_Z_MIN), ('Jan-Apr', M.FORWARD, CONFIRM_Z_MIN))   # edition 9: the two bars' periods and z lines
s16 = M.s16


def other(lean):
    return 'FOLLOW' if lean == 'FADE' else 'FADE'


def wmean(x, w):
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    return float((x[ok] * w[ok]).sum() / w[ok].sum()) if ok.any() else np.nan


def wmedian(x, w):
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    if not ok.any():
        return np.nan
    o = np.argsort(x[ok], kind='stable'); xs, ws = x[ok][o], w[ok][o]; cw = np.cumsum(ws)
    return float(xs[np.searchsorted(cw, 0.5 * cw[-1])])


def pre_fire_mask(A, R, s=PRE_FIRE_S):
    """True for every random row (coin, t) with a fire of the same coin in (t, t + s]"""
    out = np.zeros(len(R['t']), bool); by = {}
    for c, t in zip(A['coin'], A['t']):
        by.setdefault(str(c), []).append(int(t))
    by = {c: np.sort(np.array(v, np.int64)) for c, v in by.items()}
    for i, (c, t) in enumerate(zip(R['coin'], R['t'])):
        f = by.get(str(c))
        if f is not None:
            j = np.searchsorted(f, int(t), side='right')
            out[i] = j < len(f) and f[j] <= int(t) + s
    return out


class Look:
    def __init__(self, A, R, wR, costs, lean, perfire=None, drop_coins=(), drop_waves=(), ap=None, aph=None, drop_R=None, keep_A=None, pre_R=None,
                 wid=None):
        if lean not in ('FADE', 'FOLLOW'):
            raise M.Refused('LEAN %s' % lean)
        self.lean, self.oth = lean, other(lean)
        for T in (A, R):
            if len(T['t']) and int(T['t'].max()) >= M.T1:
                raise M.Refused('MAY ROW')
        self.A, self.R = A, R
        cA = np.array([costs.get(c, np.nan) for c in A['coin']], float) / 100 + M.GAP_PCT
        cR = np.array([costs.get(c, np.nan) for c in R['coin']], float) / 100 + M.GAP_PCT
        self.cA, self.cR = cA, cR
        self.bpA = np.array([costs.get(c, np.nan) for c in A['coin']], float)
        n = len(A['t'])
        self.wid = WV.waves(A['t'], GRADE_WAVE_S) if wid is None else np.asarray(wid, int)   # edition 11: the grade's waves; edition 10: ids given
        if self.wid.shape != (n,) or (n and int(self.wid.min()) < 0):
            raise M.Refused('WAVE IDS NOT ALIGNED TO THE FIRES')
        first = np.full(self.wid.max() + 1 if n else 0, np.iinfo(np.int64).max, np.int64); np.minimum.at(first, self.wid, A['t'])
        mo, dy = M.months_days(first); self.wmonth, self.wday = mo[self.wid], dy[self.wid]
        self.fmonth, self.fday = M.months_days(A['t'])
        self.rmonth, _ = M.months_days(R['t'])
        dc = np.isin(A['coin'].astype(str), list(drop_coins)) if drop_coins else np.zeros(n, bool)
        self.useA = np.isfinite(cA) & ~dc & ~np.isin(self.wid, list(drop_waves))
        self.preR = np.zeros(len(R['t']), bool) if pre_R is None else np.asarray(pre_R, bool)
        if len(self.preR) != len(R['t']):
            raise M.Refused('PRE-FIRE MASK NOT ALIGNED TO THE RANDOM')
        self._pz = {}
        if keep_A is not None:
            if len(keep_A) != n:
                raise M.Refused('KEEP MASK NOT ALIGNED TO THE FIRES')
            self.useA &= np.asarray(keep_A, bool)
        drc = np.isin(R['coin'].astype(str), list(drop_coins)) if drop_coins else np.zeros(len(R['t']), bool)
        self.wR = np.asarray(wR, float)
        self.useR = np.isfinite(cR) & np.isfinite(self.wR) & ~drc
        if drop_R is not None:
            self.useR &= ~np.asarray(drop_R, bool)
        self.perfire = perfire
        for x in (ap, aph):
            if x is not None and any(len(x[k]) != n for k in AP_COLS):
                raise M.Refused('AP NOT ALIGNED TO THE FIRES')
        self.ap = {'AP': ap, 'APH': aph}

    def first_index(self, waves):
        """one fire index of each wave id (every fire of a wave shares its month and day)"""
        if not hasattr(self, '_fi'):
            fi = np.full(self.wid.max() + 1 if len(self.wid) else 0, -1, int); fi[self.wid[::-1]] = np.arange(len(self.wid))[::-1]; self._fi = fi
        return self._fi[np.asarray(waves, int)]

    def first(self, T, name):
        v = T[name]; return np.where(np.isfinite(v), (v == 1).astype(float), np.nan)

    def net(self, T, name):
        """+1 offer first, -1 heat first, 0 neither (NaN when not known)"""
        v = T[name]; return np.where(np.isfinite(v), (v == 1).astype(float) - (v == -1).astype(float), np.nan)

    def series(self, h, side):
        """offer, heat, edge (c units) and offer-first flag at window h for one side, on A and on R"""
        out = {}
        for k, T, c in (('A', self.A, self.cA), ('R', self.R, self.cR)):
            off = T['BEST_%dM__%s' % (h, side)] / c; heat = T['WORST_%dM__%s' % (h, side)] / c
            out[k] = {'offer': off, 'heat': heat, 'edge': off - heat, 'first': self.first(T, 'OBH4_%dM__%s' % (h, side))}
        return out

    def waves(self, x, months):
        u, v, n = M.per_wave(x, self.wid, self.useA & np.isin(self.wmonth, months))
        return u, v

    def rnd(self, x, months):
        m = self.useR & np.isin(self.rmonth, months)
        return wmean(np.where(m, x, np.nan), self.wR)

    def rnd_median(self, x, months):
        m = self.useR & np.isin(self.rmonth, months)
        return wmedian(np.where(m, x, np.nan), self.wR)

    # ---- the second leg: offer-first minus heat-first against the random without the pre-fire moments, and its error
    def rnd_nopre(self, x, m):
        """(weighted mean, its squared error) of x over month m's random moments, the pre-fire ones left out; the error from Kish's
        effective count"""
        sel = self.useR & (self.rmonth == m) & ~self.preR & np.isfinite(x) & np.isfinite(self.wR) & (self.wR > 0)
        if not sel.any():
            return np.nan, np.nan
        w, v = self.wR[sel], x[sel]; mu = float((w * v).sum() / w.sum())
        var = float((w * (v - mu) ** 2).sum() / w.sum()); neff = float(w.sum() ** 2 / (w ** 2).sum())
        return mu, var / neff

    def net_test(self, months):
        """over the waves of `months`: the mean of (wave net - its month's random net, pre-fire moments out) in points, its error (waves
        clustered by day; each month's random error weighted by the month's share of waves) and z = mean / error"""
        ob = 'OBH4_60M__%s' % self.lean; xr = self.net(self.R, ob)
        u, v = self.waves(self.net(self.A, ob), months)
        if not len(u):
            return {'net_vs_random_pts': np.nan, 'se_pts': np.nan, 'z': np.nan, 'waves': 0, 'days': 0}
        fi = self.first_index(u); wm, wd = self.wmonth[fi], self.wday[fi]
        rm = {m: self.rnd_nopre(xr, m) for m in sorted(set(wm.tolist()))}
        x = v - np.array([rm[m][0] for m in wm]); ok = np.isfinite(x); x, wm, wd = x[ok], wm[ok], wd[ok]; N = len(x)
        if not N:
            return {'net_vs_random_pts': np.nan, 'se_pts': np.nan, 'z': np.nan, 'waves': 0, 'days': 0}
        mean = float(x.mean()); du, dinv = np.unique(wd, return_inverse=True); s = np.bincount(dinv, weights=x - mean)
        se2 = float((s ** 2).sum()) / N ** 2 + sum((float(np.sum(wm == m)) / N) ** 2 * rm[m][1] for m in sorted(set(wm.tolist())))
        se = math.sqrt(se2) if se2 > 0 else np.nan
        return {'net_vs_random_pts': 100 * mean, 'se_pts': 100 * se if np.isfinite(se) else np.nan,
                'z': mean / se if np.isfinite(se) and se > 0 else np.nan, 'waves': N, 'days': len(du)}

    def period_z(self, months):
        """z of the period the months belong to (Sep-Dec or Jan-Apr; the months themselves when they span both)"""
        p = M.DESIGN if all(m in M.DESIGN for m in months) else (M.FORWARD if all(m in M.FORWARD for m in months) else tuple(months))
        if p not in self._pz:
            self._pz[p] = self.net_test(p)['z']
        return self._pz[p]

    # ---- the month test at 1 h
    def month_test(self, months):
        S = self.series(60, self.lean)
        u, off = self.waves(S['A']['offer'], months); _, edge = self.waves(S['A']['edge'], months); _, fst = self.waves(S['A']['first'], months)
        r_edge = self.rnd(S['R']['edge'], months); r_first = self.rnd(S['R']['first'], months)
        ob = 'OBH4_60M__%s' % self.lean; _, net = self.waves(self.net(self.A, ob), months); r_net = self.rnd(self.net(self.R, ob), months)
        nt = float(net.mean()) if len(net) else np.nan; dn = nt - r_net if np.isfinite(nt) and np.isfinite(r_net) else np.nan
        nm = self.net_test(months)['net_vs_random_pts']; pz = self.period_z(months)
        med = float(np.median(off)) if len(off) else np.nan
        e = (float(edge.mean()) - r_edge) if len(edge) else np.nan
        f = float(fst.mean()) if len(fst) else np.nan
        p1 = bool(np.isfinite(med) and med >= OFFER_MIN_C)
        p2 = bool((np.isfinite(e) and e >= EDGE_MIN_C - TOL) or (np.isfinite(nm) and nm > 0 and np.isfinite(pz) and pz >= NET_Z_MIN - TOL))
        return {'waves_1h': len(u), 'offer_1h_median_c': med, 'random_offer_1h_median_c': self.rnd_median(S['R']['offer'], months),
                'edge_1h_vs_random_c': e, 'edge_1h_c': float(edge.mean()) if len(edge) else np.nan,
                'random_edge_1h_c': r_edge, 'first_1h_share': f, 'random_first_1h_share': r_first, 'net_first_1h': nt,
                'random_net_first_1h': r_net, 'net_first_vs_random_pts': 100 * dn if np.isfinite(dn) else np.nan,
                'net_vs_random_nopre_pts': nm, 'period_net_z': pz, 'offer_ok': p1, 'beats_random': p2,
                'holds': p1 and p2}

    def edge_parts(self, months):
        """the edge per wave (offer minus heat at 1 h, minus its month's random) over months, its total and the three concentration shares"""
        S = self.series(60, self.lean)
        rm = {m: self.rnd(S['R']['edge'], (m,)) for m in months}
        x = S['A']['edge'] - np.array([rm.get(m, np.nan) for m in self.wmonth])
        ok = self.useA & np.isin(self.wmonth, months) & np.isfinite(x)
        if not ok.any():
            return {'total': 0.0, 'top2_coins_share': np.nan, 'top5_waves_share': np.nan, 'best5_days_share': np.nan, 'top5_waves': [], 'top2_coins': []}
        uw, inv = np.unique(self.wid[ok], return_inverse=True); nf = np.bincount(inv); wv = np.bincount(inv, weights=x[ok]) / nf
        contrib = x[ok] / nf[inv]; total = float(wv.sum())
        cu, cinv = np.unique(self.A['coin'][ok].astype(str), return_inverse=True); cs = np.bincount(cinv, weights=contrib)
        oc = np.argsort(-cs, kind='stable'); ow = np.argsort(-wv, kind='stable')
        wd = self.wday[self.first_index(uw)]
        du, dinv = np.unique(wd, return_inverse=True); ds = np.bincount(dinv, weights=wv)
        sh = lambda part: part / total if total > 0 else np.nan
        return {'total': total, 'top2_coins': [str(cu[i]) for i in oc[:2]], 'top2_coins_share': sh(float(cs[oc[:2]].sum())),
                'top5_waves': [int(uw[i]) for i in ow[:5]], 'top5_waves_share': sh(float(wv[ow[:5]].sum())),
                'best5_days_share': sh(float(np.sort(ds)[::-1][:5].sum()))}

    def verdict(self):
        mon = {m: self.month_test((m,)) for m in M.DESIGN + M.FORWARD}
        held = sum(1 for m in M.DESIGN if mon[m]['holds'])
        ep = self.edge_parts(M.DESIGN)
        why = []
        if held < MONTHS_MIN:
            why.append('MONTHS (%d of 4)' % held)
        if not (ep['total'] > 0 and ep['top2_coins_share'] < SHARE_MAX):
            why.append('COINS')
        if not (ep['total'] > 0 and ep['top5_waves_share'] < SHARE_MAX):
            why.append('WAVES5')
        if not (ep['total'] > 0 and ep['best5_days_share'] < SHARE_MAX):
            why.append('DAYS')
        if min(mon[m]['waves_1h'] for m in M.DESIGN) < WAVES_MIN:
            why.append('COUNT')
        fwd_read = bool(np.isin(self.wmonth, M.FORWARD).any())
        return {'PASS': 'PASS' if not why else 'NOT PASS', 'fail': why, 'months_held_design': held,
                'net_test_design': self.net_test(M.DESIGN), 'net_test_forward': self.net_test(M.FORWARD),
                'months_held_forward': sum(1 for m in M.FORWARD if mon[m]['holds']) if fwd_read else None,
                'months': mon, 'edge_design': ep, 'forward_read': fwd_read}

    # ---- reported items (each by month and by period)
    def windows(self, months):
        rows = []
        for side in (self.lean, self.oth):
            for h in WINDOWS:
                S = self.series(h, side)
                for k in ('offer', 'heat', 'edge'):
                    u, v = self.waves(S['A'][k], months)
                    rows.append((side, h, k, len(u), float(v.mean()) if len(u) else np.nan, float(np.median(v)) if len(u) else np.nan,
                                 self.rnd(S['R'][k], months), self.rnd_median(S['R'][k], months)))
                T = self.A['OBH4_%dM__%s' % (h, side)]; TR = self.R['OBH4_%dM__%s' % (h, side)]
                for lab, val in (('offer_first', 1), ('heat_first', -1), ('neither', 0)):
                    xa = np.where(np.isfinite(T), (T == val).astype(float), np.nan); xr = np.where(np.isfinite(TR), (TR == val).astype(float), np.nan)
                    u, v = self.waves(xa, months)
                    rows.append((side, h, lab, len(u), float(v.mean()) if len(u) else np.nan, np.nan, self.rnd(xr, months), np.nan))
        return rows

    def speed(self, months):
        out = {}
        for side in (self.lean, self.oth):
            for k, col in (('offer', side), ('heat', other(side))):
                v, t = self.A['REACH4_180M__%s' % col], self.A['REACH4_180M__%s__t' % col]
                tt = np.where(np.isfinite(v) & (v == 1), t, np.nan)
                u, wv = self.waves(tt, months); _, hit = self.waves(np.where(np.isfinite(v), (v == 1).astype(float), np.nan), months)
                rv, rt = self.R['REACH4_180M__%s' % col], self.R['REACH4_180M__%s__t' % col]
                out['%s %s' % (side, k)] = {'median_s': float(np.median(wv)) if len(wv) else np.nan, 'waves_reached_share': float(hit.mean()) if len(hit) else np.nan,
                                            'random_median_s': self.rnd_median(np.where(np.isfinite(rv) & (rv == 1), rt, np.nan), months),
                                            'random_reached_share': self.rnd(np.where(np.isfinite(rv), (rv == 1).astype(float), np.nan), months)}
        return out

    def money(self, months):
        """beside only: per wave, lean side, after our cost; market and waiting (filled only if WORST_1M > 0)"""
        out = {}
        crt = M.REST_PCT + self.bpA / 200 + M.REST_GAP_PCT; w1 = self.A['WORST_1M__' + self.lean]
        for h in (15, 60, 180):
            g = self.A['RET_%dM__%s' % (h, self.lean)]
            for k, x in (('gross_pct', g), ('market_pct', g - self.cA), ('waiting_pct', np.where(np.isfinite(w1) & (w1 > 0), g - crt, np.nan))):
                u, v = self.waves(x, months)
                out['%dm %s' % (h, k)] = float(v.mean()) if len(u) else np.nan
        return out

    def counts(self, m):
        """fires (with a cost), waves (all), days with fires, and the fires dropped: no cost row; no 1 h value"""
        inm = self.fmonth == m
        f = self.useA & inm; u, _ = self.waves(np.zeros(len(self.A['t'])), (m,))
        no_cost = inm & ~np.isfinite(self.cA)
        no_1h = f & ~np.isfinite(self.A['BEST_60M__' + self.lean])
        return {'fires': int(f.sum()), 'waves_all': len(u), 'days_with_fires': len(set(self.fday[f].tolist())),
                'fires_no_cost': int(no_cost.sum()), 'fires_no_cost_coins': sorted(set(self.A['coin'][no_cost].astype(str).tolist())),
                'fires_no_1h': int(no_1h.sum())}

    def coverage(self, m):
        """the random's weight in month m over the grade's waves of the month (PERFIRE A rows); NaN without a PERFIRE"""
        P = self.perfire
        if P is None or 'wave' not in P:
            return np.nan
        sel = (P['kind'] == 'A') & (P['month'] == m[2:]); n = len(set(P['wave'][sel].tolist()))
        w = float(self.wR[self.useR & (self.rmonth == m)].sum())
        return w / n if n else np.nan

    def move(self, months, which='AP'):
        """item 1, the move spent before the fire (alarm_profile edition 2.2; which: AP the push at the fire, APH the hour's extreme): per
        wave the mean over its fires with a known value, then the median over waves; run and giveback in the fire coin's c"""
        P = self.ap.get(which)
        if P is None:
            return None
        inm = self.useA & np.isin(self.wmonth, months)
        out = {'fires': int(inm.sum()), 'fires_known': int((inm & np.isfinite(P['run_pct'])).sum())}
        for k, x in (('run_c', P['run_pct'] / self.cA), ('run_age_min', P['run_age_min']), ('giveback_c', P['giveback_pct'] / self.cA),
                     ('normal_15m_c', P['normal_move_pct'] / self.cA), ('run_norm', P['run_norm'])):
            u, v = self.waves(x, months)
            out[k + '_median'] = float(np.median(v)) if len(u) else np.nan
            if k == 'run_c':
                out['waves_known'] = len(u)
                out['run_c_p25'], out['run_c_p75'] = (float(np.percentile(v, 25)), float(np.percentile(v, 75))) if len(u) else (np.nan, np.nan)
            if k == 'run_norm':
                out['waves_run_1_normal_share'] = float(np.mean(v >= PUSH_MIN_NORM)) if len(u) else np.nan
        u, v = self.waves(P['run_capped'], months)
        out['capped_share'] = float(v.mean()) if len(u) else np.nan
        return out

    def push_share(self):
        """the share of design waves whose run went the side's way (run_pct > 0; per wave the mean over its fires with a known run)"""
        P = self.ap.get('AP')
        if P is None:
            return np.nan
        pos = np.where(np.isfinite(P['run_pct']), (P['run_pct'] > 0).astype(float), np.nan)
        u, v = self.waves(pos, M.DESIGN)
        return float(v.mean()) if len(u) else np.nan

    def push(self):
        """PUSH when at least PUSH_SHARE_MIN of the design waves ran the side's way (random sides give about 0.6)"""
        s = self.push_share()
        if not np.isfinite(s):
            return 'NOT RUN'
        return 'PUSH' if s >= PUSH_SHARE_MIN - TOL else 'NO PUSH'

    def race(self, m):
        """the grade's own race (2c before 1c) by month from PERFIRE: lean and other side, alarm and random, and the LEAD"""
        P = self.perfire
        if P is None:
            return {}
        out = {}
        for h in RACE:
            r = {}
            for k in ('A', 'R'):
                sel = (P['kind'] == k) & (P['month'] == m[2:])
                for s in (self.lean, self.oth):
                    x = P['%s %s' % (s, h)][sel]; w = P['w'][sel]
                    r[(k, s)] = 100 * wmean(x, w)
            out[h] = {'lean_a': r[('A', self.lean)], 'lean_r': r[('R', self.lean)], 'other_a': r[('A', self.oth)], 'other_r': r[('R', self.oth)],
                      'LEAD': (r[('A', self.lean)] - r[('R', self.lean)]) - (r[('A', self.oth)] - r[('R', self.oth)])}
        return out


def load_perfire(p):
    R = list(csv.DictReader(open(p), delimiter='\t'))
    out = {'kind': np.array([r['kind'] for r in R]), 'month': np.array([r['month'] for r in R]), 'w': np.array([float(r['w']) if r['w'] != '' else np.nan for r in R]),
           'wave': np.array([r.get('wave', '') for r in R]), 't': np.array([int(r['t']) for r in R], np.int64)}
    if len(out['t']) and int(out['t'].max()) >= M.T1:
        raise M.Refused('MAY ROW in %s' % p)
    for s in ('FADE', 'FOLLOW'):
        for h in RACE:
            out['%s %s' % (s, h)] = np.array([float(r['%s %s' % (s, h)]) if r['%s %s' % (s, h)] != '' else np.nan for r in R])
    return out


def load_w(p, R):
    """the random rows' weights joined by (coin, t): refused unless one to one (every random row has one weight, no weight left over)"""
    w = {}
    for r in csv.DictReader(open(p), delimiter='\t'):
        k = (r['coin'], int(r['t']))
        if k in w:
            raise M.Refused('WEIGHT TWICE %s %d' % k)
        w[k] = float(r['w'])
    keys = [(str(c), int(t)) for c, t in zip(R['coin'], R['t'])]
    miss = sum(1 for k in keys if k not in w); extra = len(set(w) - set(keys))
    if miss or extra:
        raise M.Refused('WEIGHTS DO NOT JOIN THE RANDOM ONE TO ONE: %d rows without, %d weights left over (%s)' % (miss, extra, p))
    return np.array([w[k] for k in keys], float)


def load_ap(p, A):
    """alarm_profile's export (coin, t, onset_rule, values; one row per fire) -> (arrays aligned to A by (coin, t), NaN when NOT_KNOWN; the
    join counts); a missing column is refused; a (coin, t) twice is counted, never silently kept"""
    with open(p) as f:
        rd = csv.DictReader(f, delimiter='\t'); rows = list(rd); h = rd.fieldnames or []
    if 'coin' not in h or 't' not in h or any(c not in h for c in AP_COLS):
        raise M.Refused('AP COLUMNS %s' % p)
    d = {}; twice = 0
    for r in rows:
        k = (r['coin'], int(float(r['t'])))
        twice += k in d; d[k] = r
    keys = list(zip([str(c) for c in A['coin']], [int(t) for t in A['t']])); have = set(keys)
    num = lambda s: float(s) if (s or '').strip() != '' else np.nan
    out = {c: np.array([num(d[k][c]) if k in d else np.nan for k in keys], float) for c in AP_COLS}
    return out, {'fires': len(keys), 'ap_rows': len(rows), 'fires_without_row': sum(1 for k in keys if k not in d),
                 'rows_without_fire': sum(1 for k in d if k not in have), 'rows_twice': twice}


def list_keys(p):
    with open(p) as f:
        return {(r['coin'], int(r['t']), int(r['side'])) for r in csv.DictReader(f, delimiter='\t')}


def check_inputs(r, A, R, lists, files):
    """refused unless: the lists, weights (and the PERFIRE, checked by the caller) carry TARGETS_FL's sha16s; the A and R tables hold
    exactly the lists' (coin, t, side)"""
    for k, col in (('A', 'A_sha16'), ('R', 'R_sha16')):
        if s16(lists[k]) != r[col]:
            raise M.Refused('%s LIST CHANGED %s (%s, TARGETS %s)' % (k, lists[k], s16(lists[k]), r[col]))
    if s16(files['W']) != r['W_sha16']:
        raise M.Refused('WEIGHTS CHANGED %s' % files['W'])
    for k, T in (('A', A), ('R', R)):
        got = set(zip([str(c) for c in T['coin']], [int(t) for t in T['t']], [int(s) for s in T['side']]))
        if got != list_keys(lists[k]) or len(got) != len(T['t']):
            raise M.Refused('%s TABLE IS NOT THE LIST %s (%d rows vs %d)' % (k, files[k], len(T['t']), len(list_keys(lists[k]))))


def fnum(x, nd=2):
    return '' if x is None or (isinstance(x, float) and not np.isfinite(x)) else ('%.*f' % (nd, x) if isinstance(x, float) else str(x))


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else round(float(o), 4)
    if isinstance(o, (np.integer, np.bool_)):
        return o.item()
    return o


def move_spent(code, files, A, kind):
    """(arrays or None, the JSON note) of one AP kind"""
    if not files.get(kind):
        return None, 'NOT RUN: no %s_%s.tsv in the receipts given' % (kind, code)
    ap, join = load_ap(files[kind], A)
    if join['fires_without_row'] or join['rows_without_fire'] or join['rows_twice'] or join['ap_rows'] != join['fires']:
        return None, 'NOT RUN: the %s rows do not match the fires one to one %s' % (kind, json.dumps(join, sort_keys=True))
    return ap, {'source': [os.path.basename(files[kind]), s16(files[kind])], 'join': join}


def verdict6(L, B, months):
    """the owner's rule of 30 Oct 14:58 Berlin ("direction every month, money only when busy") over `months` (the four design months, or
    beside the four forward months): direction and count on all fires (L), money, loss and spread on the busy fires (B; None without the
    AP file); see the docstring"""
    rows = {}
    for m in months:
        a = L.month_test((m,)); b = B.month_test((m,)) if B is not None else None
        bw = b['waves_1h'] if b is not None else 0; thin = b is None or bw < BUSY_WAVES_MIN
        n = a['net_vs_random_nopre_pts']
        bo = b['offer_1h_median_c'] if b is not None else np.nan; be = b['edge_1h_vs_random_c'] if b is not None else np.nan
        rows[m] = {'waves': a['waves_1h'], 'net_vs_random_pts': n, 'direction': bool(np.isfinite(n) and n > 0),
                   'busy_waves': bw, 'busy_offer_1h_c': bo, 'busy_edge_vs_random_c': be, 'thin': bool(thin),
                   'money': bool(not thin and np.isfinite(bo) and bo >= OFFER_MIN_C - TOL),
                   'loss': bool(not thin and np.isfinite(be) and be < 0)}
    z = L.net_test(months)['z']
    nd = sum(1 for r in rows.values() if r['direction']); nm = sum(1 for r in rows.values() if r['money'])
    losses = [m for m in months if rows[m]['loss']]
    ep = B.edge_parts(months) if B is not None else None
    why = []
    if B is None:
        why.append('NOT RUN (no AP file: no busy filter)')
    if nd < MONTHS_MIN or not (np.isfinite(z) and z >= NET_Z_MIN - TOL):
        why.append('DIRECTION (%d of 4, z %s)' % (nd, fnum(z)))
    if B is not None and nm < MONTHS_MIN:
        why.append('MONEY (%d of 4)' % nm)
    if losses:
        why.append('LOSS (%s)' % ','.join(m[2:] for m in losses))
    if ep is not None:
        for k, lab in (('top2_coins_share', 'COINS'), ('top5_waves_share', 'WAVES5'), ('best5_days_share', 'DAYS')):
            if not (ep['total'] > 0 and np.isfinite(ep[k]) and ep[k] < SHARE_MAX):
                why.append(lab)
    if min(r['waves'] for r in rows.values()) < WAVES_MIN:
        why.append('COUNT')
    verdict = 'NOT RUN' if B is None else ('PASS' if not why else 'NOT PASS')
    return {'PASS': verdict, 'fail': why, 'direction_months': nd, 'z': z, 'money_months': nm, 'loss_months': losses,
            'thin_months': [m for m in months if rows[m]['thin']], 'months': rows, 'spread_busy': ep}


def wquantiles(x, w, qs):
    """weighted quantiles of x (the first value whose cumulated weight reaches q of the total)"""
    o = np.argsort(x, kind='stable'); xs, ws = x[o], w[o]; cw = np.cumsum(ws)
    return np.array([xs[min(int(np.searchsorted(cw, q * cw[-1])), len(xs) - 1)] for q in qs], float)


def load_bz(p, T):
    """busy_v1's BZ_<list>.tsv.gz -> (arrays aligned to T by (coin, t), NaN when not known; the join counts)"""
    with gzip.open(p, 'rt') as f:
        rd = csv.reader(f, delimiter='\t'); h = next(rd); rows = list(rd)
    if h != ['coin', 't'] + list(BZ_COLS):
        raise M.Refused('BZ HEADER %s' % p)
    d = {}; twice = 0
    for x in rows:
        k = (x[0], int(x[1])); twice += k in d; d[k] = x
    keys = list(zip([str(c) for c in T['coin']], [int(t) for t in T['t']])); have = set(keys)
    num = lambda s: float(s) if s != '' else np.nan
    out = {c: np.array([num(d[k][2 + j]) if k in d else np.nan for k in keys], float) for j, c in enumerate(BZ_COLS)}
    return out, {'rows': len(keys), 'bz_rows': len(rows), 'rows_without_bz': sum(1 for k in keys if k not in d),
                 'bz_without_row': sum(1 for k in d if k not in have), 'twice': twice}


def busy_of(code, r, files, A, R):
    """(busy_v1's arrays of the fires and the random, aligned to A and R, or None; the JSON note): NOT RUN without both BZ tables, without
    BUSY_V1.json beside them, when that manifest names another list than TARGETS_FL's (sha16), or when a table does not join one to one"""
    if not files.get('BZA') or not files.get('BZR'):
        return None, 'NOT RUN: no BZ_A_%s and BZ_R_%s tables in the receipts given' % (code, code)
    mp = os.path.join(os.path.dirname(files['BZA']), 'BUSY_V1.json')
    if not os.path.isfile(mp) or os.path.dirname(files['BZR']) != os.path.dirname(files['BZA']):
        return None, 'NOT RUN: no BUSY_V1.json beside BZ_A_%s and BZ_R_%s' % (code, code)
    with open(mp) as f:
        man = json.load(f)
    note = {'manifest': [mp, s16(mp)], 'version': man.get('version')}
    for k, col in (('A', 'A_sha16'), ('R', 'R_sha16')):
        e = (man.get('lists') or {}).get('%s_%s' % (k, code))
        if e is None or e['list'][1] != r[col]:
            return None, 'NOT RUN: busy_v1 built %s_%s from another list (%s, TARGETS %s)' % (k, code, e['list'][1] if e else None, r[col])
    out = {}
    for k, T in (('A', A), ('R', R)):
        x, j = load_bz(files['BZ' + k], T)
        if j['rows_without_bz'] or j['bz_without_row'] or j['twice']:
            return None, 'NOT RUN: BZ_%s_%s does not join the %s rows one to one %s' % (k, code, k, json.dumps(j, sort_keys=True))
        out[k] = x; note['join_' + k] = j
    return out, note


def hit4(T, lean):
    """1 when price moved 4c either way within HIT_H minutes (the 4c race decided), 0 when not, NaN when not known"""
    v = T['OBH4_%dM__%s' % (HIT_H, lean)]
    return np.where(np.isfinite(v), (np.abs(v) == 1).astype(float), np.nan)


def bands(xn, xr, ne, re_):
    """the band pair: normal-move band (0-2) x recent band (0-3); the normal band alone when re_ is None"""
    ni = np.searchsorted(ne, xn, side='right')
    return ni if re_ is None else ni * (len(re_) + 1) + np.searchsorted(re_, xr, side='right')


def match7(L, bz, months, recent=True):
    """edition 7, MOVES per fire, over `months` (a period): each busy fire's 4c hit minus the hit share (weighted) of the busy random moments
    in the same band pair (pre-fire moments out). The bands are the period's busy random's own (weighted): the normal move in c cut in thirds
    (NORM_Q) and, with recent, the last hour's range in normal moves cut at REC_Q. A fire is priced by its own month's random in its band
    pair when that random's effective count is at least CELL_MIN_NEFF, else by the period's random in the same band pair (fallback), else it
    is unmatched; a fire busier (or calmer) than every random moment of the period, on either value, is unmatched (outside). -> per fire:
    busy, ok (busy with a hit and its values), matched, e (hit - expected), p (expected), hit, key (its pricing cell, -1 unmatched),
    fallback, outside; the cells' p variance and effective count; the fires' values and their cells' random means (for the ratios)"""
    A, R = bz['A'], bz['R']
    nA = A['normal_move_pct'] / L.cA; nR = R['normal_move_pct'] / L.cR
    with np.errstate(divide='ignore', invalid='ignore'):
        rA = A['range60_pct'] / A['normal_move_pct']; rR = R['range60_pct'] / R['normal_move_pct']
    hA = hit4(L.A, L.lean); hR = hit4(L.R, L.lean)
    busy = L.useA & np.isfinite(nA) & (nA >= BUSY_MIN_C - TOL)
    ok = busy & np.isfinite(hA) & (np.isfinite(rA) if recent else True)
    n = len(L.A['t']); e = np.full(n, np.nan); p = np.full(n, np.nan); key = np.full(n, -1, int); keys, kvar, kneff = [], [], []
    ncell = np.full(n, np.nan); rcell = np.full(n, np.nan); fb = np.zeros(n, bool); outside = np.zeros(n, bool)
    out = {'busy': busy, 'ok': ok, 'matched': key >= 0, 'e': e, 'p': p, 'hit': hA, 'key': key, 'keys': keys, 'kvar': np.array(kvar, float),
           'kneff': np.array(kneff, float), 'nA': nA, 'rA': rA, 'ncell': ncell, 'rcell': rcell, 'fallback': fb, 'outside': outside}
    pool = L.useR & np.isin(L.rmonth, months) & ~L.preR & np.isfinite(hR) & np.isfinite(nR) & (nR >= BUSY_MIN_C - TOL) & (L.wR > 0)
    if recent:
        pool &= np.isfinite(rR)
    fi = np.flatnonzero(ok & np.isin(L.fmonth, months))
    if not pool.any() or not len(fi):
        return out
    w = L.wR[pool]; hh = hR[pool]; xn = nR[pool]; xr = rR[pool]; rm = L.rmonth[pool]
    ne = wquantiles(xn, w, NORM_Q); re_ = wquantiles(xr, w, REC_Q) if recent else None
    cr = bands(xn, xr, ne, re_); ca = bands(nA[fi], rA[fi], ne, re_)
    ins = (nA[fi] >= xn.min()) & (nA[fi] <= xn.max())
    if recent:
        ins &= (rA[fi] >= xr.min()) & (rA[fi] <= xr.max())
    outside[fi[~ins]] = True

    def cell(k):
        ww = w[k]; W = float(ww.sum()); pc = float((ww * hh[k]).sum() / W); neff = W ** 2 / float((ww ** 2).sum())
        return (pc, float((ww * (hh[k] - pc) ** 2).sum() / W) / neff, neff, float((ww * xn[k]).sum() / W),
                float((ww * xr[k]).sum() / W) if recent else np.nan)
    idx = {}
    for c in np.unique(ca[ins]):
        jc = fi[ins & (ca == c)]; kp = cr == c
        for m in sorted(set(L.fmonth[jc].tolist())):
            j = jc[L.fmonth[jc] == m]; km = kp & (rm == m); st = cell(km) if km.any() else None; src = (m, int(c)); f = False
            if st is None or st[2] < CELL_MIN_NEFF - TOL:
                st = cell(kp) if kp.any() else None; src = ('period', int(c)); f = True
                if st is None or st[2] < CELL_MIN_NEFF - TOL:
                    continue
            if src not in idx:
                idx[src] = len(keys); keys.append(src); kvar.append(st[1]); kneff.append(st[2])
            p[j] = st[0]; e[j] = hA[j] - st[0]; key[j] = idx[src]; ncell[j] = st[3]; rcell[j] = st[4]; fb[j] = f
    out.update({'matched': key >= 0, 'kvar': np.array(kvar, float), 'kneff': np.array(kneff, float)})
    return out


def stats7(L, X, months, drop_coins=(), drop_days=()):
    """over the waves of `months` (a wave's month and day: its first fire's): per wave the mean of e over its matched busy fires -> the mean
    (points), its error (waves clustered by day, plus each band pair's random error weighted by its share of the waves), z, waves, the
    per-month means (waves, alarm hit share, expected share, excess), each coin's part of the sum and each day's"""
    sel = X['matched'] & np.isin(L.wmonth, months)
    if drop_coins:
        sel &= ~np.isin(L.A['coin'].astype(str), list(drop_coins))
    if drop_days:
        sel &= ~np.isin(L.wday, list(drop_days))
    out = {'waves': 0, 'mean_pts': np.nan, 'se_pts': np.nan, 'z': np.nan, 'months': {}, 'coin_parts': {}, 'day_parts': {}}
    if not sel.any():
        return out
    u, inv = np.unique(L.wid[sel], return_inverse=True); nw = np.bincount(inv)
    xw = np.bincount(inv, weights=X['e'][sel]) / nw; hw = np.bincount(inv, weights=X['hit'][sel]) / nw; pw = np.bincount(inv, weights=X['p'][sel]) / nw
    N = len(u); mean = float(xw.mean()); fi = L.first_index(u); wd, wm = L.wday[fi], L.wmonth[fi]
    du, dinv = np.unique(wd, return_inverse=True); s = np.bincount(dinv, weights=xw - mean)
    ak = np.bincount(X['key'][sel], weights=1.0 / nw[inv], minlength=len(X['keys'])) / N
    se2 = float((s ** 2).sum()) / N ** 2 + (float((ak ** 2 * X['kvar']).sum()) if len(X['keys']) else 0.0)
    se = math.sqrt(se2) if se2 > 0 else np.nan
    cu, cinv = np.unique(L.A['coin'][sel].astype(str), return_inverse=True); cs = np.bincount(cinv, weights=X['e'][sel] / nw[inv])
    out.update({'waves': N, 'mean_pts': 100 * mean, 'se_pts': 100 * se if np.isfinite(se) else np.nan,
                'z': mean / se if np.isfinite(se) and se > 0 else np.nan,
                'coin_parts': {str(c): float(v) for c, v in zip(cu, cs)}, 'day_parts': {str(d): float(v) for d, v in zip(du, np.bincount(dinv, weights=xw))}})
    for m in months:
        k = wm == m
        out['months'][m] = {'waves': int(k.sum()), 'alarm_hit_share': float(hw[k].mean()) if k.any() else np.nan,
                            'expected_hit_share': float(pw[k].mean()) if k.any() else np.nan, 'excess_pts': 100 * float(xw[k].mean()) if k.any() else np.nan}
    return out


def verdict7(L, bz, months):
    """the owner's criteria of 30 Oct 16:00-16:06 Berlin over `months` (the four design months, or beside the four forward months); see the
    docstring. bz: busy_v1's arrays {'A': ..., 'R': ...} aligned to the fires and the random, or None (NOT RUN)"""
    rows = {}
    for m in months:
        a = L.month_test((m,)); n = a['net_vs_random_nopre_pts']
        rows[m] = {'waves': a['waves_1h'], 'lean_net_pts': n, 'lean_dir': bool(np.isfinite(n) and n > 0)}
    lean = {'months': sum(1 for x in rows.values() if x['lean_dir']), 'z': L.net_test(months)['z']}
    count = min(x['waves'] for x in rows.values()) >= WAVES_MIN
    if bz is None:
        return {'PASS': 'NOT RUN', 'fail': ['NOT RUN (no busyness for the random: BZ tables)'], 'months': rows, 'lean': lean}
    X = match7(L, bz, months, True); X0 = match7(L, bz, months, False)
    S = stats7(L, X, months); S0 = stats7(L, X0, months)
    inm = np.isin(L.wmonth, months); nb = int((X['busy'] & inm).sum()); nok = int((X['ok'] & inm).sum()); nmt = int((X['matched'] & inm).sum())
    mt = X['matched'] & inm
    ratio = lambda a, b: float(a[mt].mean() / b[mt].mean()) if mt.any() and b[mt].mean() > 0 else np.nan
    for m in months:
        t = S['months'].get(m) or {'waves': 0, 'alarm_hit_share': np.nan, 'expected_hit_share': np.nan, 'excess_pts': np.nan}
        fm = L.wmonth == m
        rows[m].update({'busy_fires': int((X['busy'] & fm).sum()), 'busy_fires_matched': int((X['matched'] & fm).sum()), 'busy_waves': t['waves'],
                        'thin': t['waves'] < BUSY_WAVES_MIN, 'alarm_hit_share': t['alarm_hit_share'], 'expected_hit_share': t['expected_hit_share'],
                        'excess_pts': t['excess_pts'], 'normal_only_excess_pts': (S0['months'].get(m) or {}).get('excess_pts', np.nan)})
        rows[m]['moves'] = bool(not rows[m]['thin'] and np.isfinite(t['excess_pts']) and t['excess_pts'] > PTS_TOL)
    nmv = sum(1 for m in months if rows[m]['moves'])
    top2 = [c for c, v in sorted(S['coin_parts'].items(), key=lambda kv: (-kv[1], kv[0]))[:2]]
    best5 = [d for d, v in sorted(S['day_parts'].items(), key=lambda kv: (-kv[1], kv[0]))[:5]]
    Sc = stats7(L, X, months, drop_coins=top2); Sd = stats7(L, X, months, drop_days=best5)
    why = []
    if nmv < MONTHS_MIN or not (np.isfinite(S['z']) and S['z'] >= NET_Z_MIN - TOL):
        why.append('MOVES (%d of 4, z %s)' % (nmv, fnum(S['z'])))
    if not (np.isfinite(Sc['mean_pts']) and Sc['mean_pts'] > PTS_TOL):
        why.append('COINS (without %s: %s pts)' % (','.join(top2) or '-', fnum(Sc['mean_pts'])))
    if not (np.isfinite(Sd['mean_pts']) and Sd['mean_pts'] > PTS_TOL):
        why.append('DAYS (without the best 5: %s pts)' % fnum(Sd['mean_pts']))
    if not count:
        why.append('COUNT')
    return {'PASS': 'PASS' if not why else 'NOT PASS', 'fail': why, 'moves_months': nmv, 'z': S['z'], 'excess_pts': S['mean_pts'], 'se_pts': S['se_pts'],
            'waves': S['waves'], 'without_top2_coins_pts': Sc['mean_pts'], 'top2_coins': top2, 'without_best5_days_pts': Sd['mean_pts'], 'best5_days': best5,
            'busy_fires': nb, 'busy_fires_known': nok, 'busy_fires_matched': nmt, 'matched_share': nmt / nok if nok else np.nan,
            'recent_ratio': ratio(X['rA'], X['rcell']), 'normal_ratio': ratio(X['nA'], X['ncell']),
            'fallback_share': float((X['fallback'] & mt).sum() / nmt) if nmt else np.nan, 'outside_share': float((X['outside'] & inm).sum() / nok) if nok else np.nan,
            'thin_months': [m for m in months if rows[m]['thin']], 'normal_only': {'z': S0['z'], 'excess_pts': S0['mean_pts']},
            'lean': lean, 'months': rows}


def overall7(d, w):
    """RULE_7 from the Sep-Dec and Jan-Apr verdicts"""
    if d['PASS'] == 'NOT RUN':
        return 'NOT RUN'
    if d['PASS'] != 'PASS':
        return 'NOT PASS'
    return 'PASS' if w['PASS'] == 'PASS' else 'NEEDS MORE MONTHS'


def counts8(L, months):
    """waves with a 1 h value (all fires) per month: the COUNT rule's numbers (month_test's waves_1h, without its other work)"""
    off = L.series(60, L.lean)['A']['offer']
    return {m: len(L.waves(off, (m,))[0]) for m in months}


def side8(L, months, net=None, net_R=None):
    """edition 8, the SIDE bar per fire: the fire's lean race at 1 h (+1 offer first, -1 heat first, 0 neither) minus its wave month's
    random (pre-fire moments out, weighted: Look.rnd_nopre); `net` and `net_R` replace the fires' and the random's races (the ladder's
    made-up sides). Every fire with a cost and a value counts (edition 6's direction is not filtered on busyness). -> the X of stats7 (one
    key a month: the month random's error)"""
    ob = 'OBH4_60M__%s' % L.lean; xr = L.net(L.R, ob) if net_R is None else np.asarray(net_R, float)
    xa = L.net(L.A, ob) if net is None else np.asarray(net, float)
    n = len(L.A['t']); e = np.full(n, np.nan); p = np.full(n, np.nan); key = np.full(n, -1, int); keys, kvar = [], []
    ok = L.useA & np.isfinite(xa)
    for m in months:
        j = np.flatnonzero(ok & (L.wmonth == m))
        if not len(j):
            continue
        mu, v = L.rnd_nopre(xr, m)
        if not np.isfinite(mu):
            continue
        p[j] = mu; e[j] = xa[j] - mu; key[j] = len(keys); keys.append((m, 'side')); kvar.append(float(v) if np.isfinite(v) else 0.0)
    return {'busy': ok, 'ok': ok, 'matched': key >= 0, 'e': e, 'p': p, 'hit': xa, 'key': key, 'keys': keys,
            'kvar': np.array(kvar, float), 'kneff': np.full(len(keys), np.nan)}


def bar8(L, X, months, counts, label, z_min=NET_Z_MIN):
    """one bar over `months` from its per-fire excess X (stats7): STEADY, BROAD, COUNT (see the docstring) -> PASS / NOT PASS and why"""
    S = stats7(L, X, months); rows = {}
    for m in months:
        t = S['months'].get(m) or {'waves': 0, 'excess_pts': np.nan, 'alarm_hit_share': np.nan, 'expected_hit_share': np.nan}
        thin = t['waves'] < BUSY_WAVES_MIN
        rows[m] = {'waves': t['waves'], 'thin': thin, 'excess_pts': t['excess_pts'], 'alarm': t['alarm_hit_share'], 'expected': t['expected_hit_share'],
                   'holds': bool(not thin and np.isfinite(t['excess_pts']) and t['excess_pts'] > PTS_TOL), 'waves_1h': counts[m]}
    nh = sum(1 for m in months if rows[m]['holds'])
    top2 = [c for c, v in sorted(S['coin_parts'].items(), key=lambda kv: (-kv[1], kv[0]))[:2]]
    best5 = [d for d, v in sorted(S['day_parts'].items(), key=lambda kv: (-kv[1], kv[0]))[:5]]
    Sc = stats7(L, X, months, drop_coins=top2); Sd = stats7(L, X, months, drop_days=best5)
    why = []
    if nh < MONTHS_MIN or not (np.isfinite(S['z']) and S['z'] >= z_min - TOL):          # edition 9: the period's z line
        why.append('%s (%d of 4, z %s)' % (label, nh, fnum(S['z'])))
    if not (np.isfinite(Sc['mean_pts']) and Sc['mean_pts'] > PTS_TOL):
        why.append('COINS (without %s: %s pts)' % (','.join(top2) or '-', fnum(Sc['mean_pts'])))
    if not (np.isfinite(Sd['mean_pts']) and Sd['mean_pts'] > PTS_TOL):
        why.append('DAYS (without the best 5: %s pts)' % fnum(Sd['mean_pts']))
    if min(counts[m] for m in months) < WAVES_MIN:
        why.append('COUNT')
    return {'PASS': 'PASS' if not why else 'NOT PASS', 'fail': why, 'z_min': z_min, 'months_holding': nh, 'z': S['z'], 'excess_pts': S['mean_pts'], 'se_pts': S['se_pts'],
            'waves': S['waves'], 'without_top2_coins_pts': Sc['mean_pts'], 'top2_coins': top2, 'without_best5_days_pts': Sd['mean_pts'],
            'thin_months': [m for m in months if rows[m]['thin']], 'months': rows}


def verdict8(L, bz, months, counts=None, net=None, net_R=None, z_min=NET_Z_MIN):
    """edition 8 over `months`: {'SIZE': edition 7's MOVES as a bar (NOT RUN without bz), 'SIDE': the direction as a bar}"""
    counts = counts or counts8(L, months)
    size = bar8(L, match7(L, bz, months, True), months, counts, 'SIZE', z_min) if bz is not None else {'PASS': 'NOT RUN', 'fail': ['NOT RUN (no BZ tables)']}
    return {'SIZE': size, 'SIDE': bar8(L, side8(L, months, net, net_R), months, counts, 'SIDE', z_min)}


def overall8(d, w):
    """RULE_8 from the Sep-Dec (d) and Jan-Apr (w) verdict8: the bars passing both periods ('SIZE+SIDE', 'SIZE', 'SIDE'); else
    'NEEDS MORE MONTHS (<the bars passing Sep-Dec>)'; else 'NOT PASS'"""
    both = [b for b in ('SIZE', 'SIDE') if d[b]['PASS'] == 'PASS' and w[b]['PASS'] == 'PASS']
    if both:
        return '+'.join(both)
    sd = [b for b in ('SIZE', 'SIDE') if d[b]['PASS'] == 'PASS']
    return 'NEEDS MORE MONTHS (%s)' % '+'.join(sd) if sd else 'NOT PASS'


def run_code(r, H, costs, files, lists, out):
    code = r['code']; A = M.load_table(files['A']); R = M.load_table(files['R'])
    check_inputs(r, A, R, lists, files)
    wR = load_w(files['W'], R)
    pf = os.path.join(H, r['perfire']); P = None
    if not os.path.exists(pf):
        race_note = 'RACE NOT RUN: no PERFIRE at %s' % r['perfire']
    elif s16(pf) != r['perfire_sha16']:
        race_note = 'RACE NOT RUN: PERFIRE changed (%s, TARGETS %s)' % (s16(pf), r['perfire_sha16'])
    else:
        P = load_perfire(pf); race_note = 'from %s %s' % (r['perfire'], r['perfire_sha16'])
    ap, ap_note = move_spent(code, files, A, 'AP'); aph, aph_note = move_spent(code, files, A, 'APH')
    pre = pre_fire_mask(A, R)
    L = Look(A, R, wR, costs, r['lean'], P, ap=ap, aph=aph, pre_R=pre)
    cmax = float(np.nanmax(np.abs(L.cA - A['unit__c']))) if np.isfinite(A['unit__c']).any() else 0.0
    if cmax > C_TOL:
        raise M.Refused('c DIFFERS FROM THE OUTCOME TOOL\'S unit__c by %.3g (%s)' % (cmax, code))
    V = L.verdict()
    busy_note, keep = 'NOT RUN: no AP_%s.tsv (the normal move comes from it)' % code, None
    if ap is not None:
        busy = ap['normal_move_pct'] / L.cA; keep = np.isfinite(busy) & (busy >= BUSY_MIN_C - TOL)
        busy_note = {'min_c': BUSY_MIN_C, 'fires_kept': int(keep.sum()), 'fires': int(len(keep)), 'fires_without_normal_move': int((~np.isfinite(busy)).sum())}
    variants = {'without_DASH_VVV_ZEC': Look(A, R, wR, costs, r['lean'], None, drop_coins=EXCLUDE, pre_R=pre),
                'without_top5_waves': Look(A, R, wR, costs, r['lean'], None, drop_waves=V['edge_design']['top5_waves'], pre_R=pre),
                'without_prefire_random': Look(A, R, wR, costs, r['lean'], None, drop_R=pre, pre_R=pre)}
    if keep is not None:
        variants['busy_only'] = Look(A, R, wR, costs, r['lean'], None, keep_A=keep, pre_R=pre)
    VV = {k: x.verdict() for k, x in variants.items()}
    R30 = {p: verdict6(L, variants.get('busy_only'), ms) for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD))}
    bz, bz_note = busy_of(code, r, files, A, R)
    R7 = {p: verdict7(L, bz, ms) for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD))}
    R7['RULE_7'] = overall7(R7['Sep-Dec'], R7['Jan-Apr'])
    R8 = {p: verdict8(L, bz, ms) for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD))}
    R8['RULE_8'] = overall8(R8['Sep-Dec'], R8['Jan-Apr'])
    R9 = {p: verdict8(L, bz, ms, z_min=zm) for p, ms, zm in PERIODS9}
    R9['RULE_9'] = overall8(R9['Sep-Dec'], R9['Jan-Apr'])
    for k in ('AP', 'APH'):
        note = ap_note if k == 'AP' else aph_note
        if isinstance(note, dict):
            note.update({p: L.move(ms, k) for p, ms in PERIODS})
    res = {'version': VERSION, 'code': code, 'alarm_ids': r['alarm_ids'].split(','), 'V': r['V'], 'lean': r['lean'],
           'inputs': {k: [os.path.basename(p), s16(p)] for k, p in list(files.items()) + [('A list', lists['A']), ('R list', lists['R'])] if p},
           'race': race_note, 'c_vs_tool_max_abs_diff_pct': cmax, 'verdict': V, 'rule_30oct': R30, 'rule_7': R7, 'rule_8': R8, 'rule_9': R9, 'busy_v1': bz_note,
           'busy_filter': busy_note if not isinstance(busy_note, dict) else dict(busy_note, waves_kept_share={p: (
               sum(VV['busy_only']['months'][m]['waves_1h'] for m in ms) / max(sum(V['months'][m]['waves_1h'] for m in ms), 1)) for p, ms in PERIODS[-2:]}),
           'variants': {k: {'PASS': v['PASS'], 'fail': v['fail'], 'months_held_design': v['months_held_design'],
                            'months_held_forward': v['months_held_forward'], 'edge_total': v['edge_design']['total'],
                            'net_z_design': v['net_test_design']['z'],
                            'months_holding': [m for m in M.DESIGN + M.FORWARD if v['months'][m]['holds']]} for k, v in VV.items()},
           'prefire_random_weight_share': {p: (float(wR[L.useR & np.isin(L.rmonth, ms) & pre].sum() / max(wR[L.useR & np.isin(L.rmonth, ms)].sum(), 1e-12)))
                                           for p, ms in PERIODS},
           'random_cover': {m: L.coverage(m) for m in M.DESIGN + M.FORWARD}, 'cover_min_flag': COVER_MIN,
           'random_cover_flagged_months': [m for m in M.DESIGN + M.FORWARD if np.isfinite(L.coverage(m)) and L.coverage(m) < COVER_MIN],
           'net_test': {'Sep-Dec': V['net_test_design'], 'Jan-Apr': V['net_test_forward']},
           'push_share': L.push_share(), 'push': L.push(), 'move_spent_push_at_fire': ap_note, 'move_spent_hour_peak': aph_note,
           'speed': {p: L.speed(ms) for p, ms in PERIODS}, 'money_beside': {p: L.money(ms) for p, ms in PERIODS},
           'shares': {p: L.edge_parts(ms) for p, ms in PERIODS}, 'counts': {m: L.counts(m) for m in M.DESIGN + M.FORWARD},
           'choices': 'see the docstrings of fl_read_v5.py and fl_read_v3.py (edge mean over waves, shares of the edge above the month random, holds = both rules, '
                      '30 waves on design months with a 1 h value, random waves 30 min, fire waves 30 min (edition 11; 15 min before), speed from the entry bar)'}
    with open(os.path.join(out, 'FL_%s.json' % code), 'x') as f:
        json.dump(clean(res), f, indent=1, sort_keys=True)
    sk = [(s, k) for s in (L.lean, L.oth) for k in ('offer', 'heat')]
    with open(os.path.join(out, 'FL_%s_MONTHS.tsv' % code), 'x') as f:
        cols = ['month', 'fires', 'fires_no_cost', 'fires_no_1h', 'waves_all', 'waves_1h', 'days_with_fires', 'random_cover', 'prefire_random_share',
                'move_run_c', 'move_age_min', 'move_giveback_c', 'move_run_norm', 'hour_run_c', 'hour_age_min', 'hour_giveback_c',
                'offer_1h_median_c', 'random_offer_1h_median_c', 'edge_1h_c', 'random_edge_1h_c', 'edge_1h_vs_random_c',
                'first_1h_share', 'random_first_1h_share', 'net_vs_random_pts', 'net_vs_random_nopre_pts', 'period_net_z', 'random_cover_flag',
                'offer_ok', 'beats_random', 'holds',
                'holds_without_DASH_VVV_ZEC', 'holds_without_top5_waves', 'holds_without_prefire_random',
                'top2_coins_share', 'top2_coins', 'top5_waves_share', 'best5_days_share'] + \
               ['race_%s_%s' % (h, k) for h in RACE for k in ('lean_a', 'lean_r', 'other_a', 'other_r', 'LEAD')] + \
               ['speed_%s_%s_s' % (('lean' if s == L.lean else 'other'), k) for s, k in sk] + \
               ['random_speed_%s_%s_s' % (('lean' if s == L.lean else 'other'), k) for s, k in sk] + \
               ['money_%s' % k for k in ('15m_market', '1h_market', '1h_waiting', '3h_market')]
        f.write('\t'.join(cols) + '\n')
        for m in M.DESIGN + M.FORWARD:
            t = V['months'][m]; c = res['counts'][m]; rc = L.race(m); sp = res['speed'][m]; mo = res['money_beside'][m]; sh = res['shares'][m]
            mv = L.move((m,), 'AP') or {}; mh = L.move((m,), 'APH') or {}
            row = [m, c['fires'], c['fires_no_cost'], c['fires_no_1h'], c['waves_all'], t['waves_1h'], c['days_with_fires'], fnum(res['random_cover'][m]),
                   fnum(res['prefire_random_weight_share'][m], 3),
                   fnum(mv.get('run_c_median')), fnum(mv.get('run_age_min_median'), 0), fnum(mv.get('giveback_c_median')), fnum(mv.get('run_norm_median')),
                   fnum(mh.get('run_c_median')), fnum(mh.get('run_age_min_median'), 0), fnum(mh.get('giveback_c_median')),
                   fnum(t['offer_1h_median_c']), fnum(t['random_offer_1h_median_c']), fnum(t['edge_1h_c']), fnum(t['random_edge_1h_c']),
                   fnum(t['edge_1h_vs_random_c']), fnum(t['first_1h_share'], 3), fnum(t['random_first_1h_share'], 3),
                   fnum(t['net_first_vs_random_pts'], 1), fnum(t['net_vs_random_nopre_pts'], 1), fnum(t['period_net_z']),
                   int(m in res['random_cover_flagged_months']), int(t['offer_ok']), int(t['beats_random']),
                   int(t['holds'])] + [int(VV[k]['months'][m]['holds']) for k in ('without_DASH_VVV_ZEC', 'without_top5_waves', 'without_prefire_random')] + \
                  [fnum(sh['top2_coins_share']), ','.join(sh['top2_coins']), fnum(sh['top5_waves_share']), fnum(sh['best5_days_share'])]
            row += [fnum(rc[h][k], 1) if rc else 'NOT RUN' for h in RACE for k in ('lean_a', 'lean_r', 'other_a', 'other_r', 'LEAD')]
            row += [fnum(sp['%s %s' % (s, k)]['median_s'], 0) for s, k in sk] + [fnum(sp['%s %s' % (s, k)]['random_median_s'], 0) for s, k in sk]
            row += [fnum(mo['15m market_pct'], 3), fnum(mo['60m market_pct'], 3), fnum(mo['60m waiting_pct'], 3), fnum(mo['180m market_pct'], 3)]
            f.write('\t'.join(str(x) for x in row) + '\n')
    with open(os.path.join(out, 'FL_%s_RULE8.tsv' % code), 'x') as f:
        f.write('period\tmonth\tbar\twaves\tthin\talarm\texpected\texcess_pts\tholds\twaves_1h\n')
        for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD)):
            for b in ('SIZE', 'SIDE'):
                if 'months' not in R8[p][b]:
                    continue
                for m in ms:
                    t = R8[p][b]['months'][m]
                    f.write('%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%d\t%d\n' % (p, m, b, t['waves'], t['thin'], fnum(t['alarm'], 3), fnum(t['expected'], 3),
                                                                     fnum(t['excess_pts'], 1), t['holds'], t['waves_1h']))
    with open(os.path.join(out, 'FL_%s_RULE7.tsv' % code), 'x') as f:
        c7 = ['period', 'month', 'waves_1h', 'busy_fires', 'busy_fires_matched', 'busy_waves', 'thin', 'alarm_hit_share', 'expected_hit_share',
              'excess_pts', 'moves', 'normal_only_excess_pts', 'lean_net_pts', 'lean_dir']
        f.write('\t'.join(c7) + '\n')
        for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD)):
            for m in ms:
                t = R7[p]['months'][m]; g = lambda k, nd=2: fnum(t.get(k), nd) if k in t else ''
                f.write('\t'.join(str(x) for x in [p, m, t['waves'], g('busy_fires'), g('busy_fires_matched'), g('busy_waves'),
                                                   int(t['thin']) if 'thin' in t else '', g('alarm_hit_share', 3), g('expected_hit_share', 3),
                                                   g('excess_pts', 1), int(t['moves']) if 'moves' in t else '', g('normal_only_excess_pts', 1),
                                                   fnum(t['lean_net_pts'], 1), int(t['lean_dir'])]) + '\n')
    with open(os.path.join(out, 'FL_%s_RULE30.tsv' % code), 'x') as f:
        f.write('period\tmonth\twaves\tnet_vs_random_pts\tdirection\tbusy_waves\tbusy_offer_1h_c\tbusy_edge_vs_random_c\tthin\tmoney\tloss\n')
        for p, ms in (('Sep-Dec', M.DESIGN), ('Jan-Apr', M.FORWARD)):
            for m in ms:
                t = R30[p]['months'][m]
                f.write('%s\t%s\t%d\t%s\t%d\t%d\t%s\t%s\t%d\t%d\t%d\n' % (p, m, t['waves'], fnum(t['net_vs_random_pts'], 1), t['direction'], t['busy_waves'],
                        fnum(t['busy_offer_1h_c']), fnum(t['busy_edge_vs_random_c']), t['thin'], t['money'], t['loss']))
    with open(os.path.join(out, 'FL_%s_WINDOWS.tsv' % code), 'x') as f:
        f.write('period\tside\twindow_min\tmeasure\twaves\talarm_mean\talarm_median\trandom_mean\trandom_median\n')
        for pn, ms in PERIODS:
            for side, h, k, n, mean, med, rm, rmed in L.windows(ms):
                f.write('%s\t%s\t%d\t%s\t%d\t%s\t%s\t%s\t%s\n' % (pn, side, h, k, n, fnum(mean, 3), fnum(med, 3), fnum(rm, 3), fnum(rmed, 3)))
    return res


def job_finished(d):
    """a receipts folder is read only when its STAGES.tsv holds an 'end' stage with rc 0 (the job is over)"""
    p = os.path.join(d, 'STAGES.tsv')
    if not os.path.isfile(p):
        return False
    with open(p) as f:
        return any(len(x) >= 3 and x[1] == 'end' and x[2] == '0' for x in (l.rstrip('\n').split('\t') for l in f))


def main(targets, H, costs_path, out, *rdirs):
    if os.path.exists(out) or os.path.exists(out + '.part'):
        raise M.Refused('OUT EXISTS %s' % out)
    for d in rdirs:
        if not (job_finished(d) or (os.path.basename(os.path.normpath(d)) == 'BZ' and job_finished(os.path.dirname(os.path.normpath(d))))):
            raise M.Refused('JOB NOT FINISHED %s (its STAGES.tsv has no "end 0" line)' % d)
    part = out + '.part'
    try:
        write_all(targets, H, costs_path, part, *rdirs)
    except BaseException:
        if os.path.isdir(part):
            shutil.rmtree(part)          # this run's own unfinished folder: a refused run publishes no number
        raise
    os.rename(part, out)


def write_all(targets, H, costs_path, out, *rdirs):
    costs = M.load_costs(costs_path); T = list(csv.DictReader(open(targets), delimiter='\t')); idir = os.path.dirname(targets)
    found = {}
    for d in rdirs:
        for fn in os.listdir(d):
            ma = AP_RE.match(fn)
            k = fn[:-7] if fn.endswith('.tsv.gz') else ('%s_%s' % (ma.group(1), ma.group(2)) if ma else None)
            if k is None:
                continue
            if k in found:
                raise M.Refused('TWO FILES FOR %s' % k)
            found[k] = os.path.join(d, fn)
    os.makedirs(out); rows = []
    for r in T:
        c = r['code']
        files = {'A': found.get('A' + c), 'R': found.get('R' + c), 'W': os.path.join(idir, 'R_%s_W.tsv' % c), 'AP': found.get('AP_' + c), 'APH': found.get('APH_' + c), 'BZA': found.get('BZ_A_' + c), 'BZR': found.get('BZ_R_' + c)}
        lists = {'A': os.path.join(idir, 'A_%s_EVENTS.tsv' % c), 'R': os.path.join(idir, 'R_%s_EVENTS.tsv' % c)}
        if not files['A'] or not files['R']:
            rows.append((r, None)); continue
        rows.append((r, run_code(r, H, costs, files, lists, out)))
    MV = ('run_c_median', 'run_age_min_median', 'giveback_c_median', 'run_norm_median')
    cols = ['alarm_id', 'code', 'V', 'lean', 'FIRST_LOOK', 'fail', 'months_held_design', 'months_held_forward', 'top2_coins_share', 'top2_coins',
            'top5_waves_share', 'best5_days_share', 'without_DASH_VVV_ZEC', 'without_top5_waves', 'without_prefire_random', 'prefire_random_share_SepDec',
            'random_cover_min_SepDec', 'random_cover_flagged', 'net_z_SepDec', 'net_z_JanApr', 'race', 'PUSH', 'push_share', 'busy_FIRST_LOOK', 'busy_fail', 'busy_held_design', 'busy_held_forward', 'busy_months',
            'busy_waves_kept_SepDec', 'busy_waves_kept_JanApr'] + \
           ['%s_%s_%s' % (kind, p, k) for kind in ('move', 'hour') for p in ('SepDec', 'JanApr') for k in ('run_c', 'age_min', 'giveback_c', 'run_norm')] + \
           ['%s_%s' % (m[2:], k) for m in M.DESIGN + M.FORWARD for k in ('waves_1h', 'offer1h_c', 'rnd_offer1h_c', 'edge_vs_rnd_c', 'first', 'rnd_first',
                                                                     'net_vs_rnd_pts', 'net_nopre_pts', 'holds')]
    with open(os.path.join(out, 'FL_SUMMARY.tsv'), 'x') as f:
        f.write('\t'.join(cols) + '\n')
        for r, res in rows:
            for aid in r['alarm_ids'].split(','):
                if res is None:
                    f.write('\t'.join([aid, r['code'], r['V'], r['lean'], 'NOT RUN'] + [''] * (len(cols) - 5)) + '\n'); continue
                V = res['verdict']; e = V['edge_design']; vv = res['variants']
                vals = [aid, r['code'], r['V'], r['lean'], V['PASS'], ','.join(V['fail']) or '-', V['months_held_design'], fnum(V['months_held_forward']),
                        fnum(e['top2_coins_share']), ','.join(e['top2_coins']), fnum(e['top5_waves_share']), fnum(e['best5_days_share'])]
                vals += ['%s %d of 4' % (vv[k]['PASS'], vv[k]['months_held_design']) for k in ('without_DASH_VVV_ZEC', 'without_top5_waves', 'without_prefire_random')]
                cov = [res['random_cover'][m] for m in M.DESIGN if res['random_cover'][m] is not None and np.isfinite(res['random_cover'][m])]
                vals += [fnum(res['prefire_random_weight_share']['Sep-Dec'], 3), fnum(min(cov)) if cov else '',
                         ','.join(m[2:] for m in res['random_cover_flagged_months']) or '-',
                         fnum(res['net_test']['Sep-Dec']['z']), fnum(res['net_test']['Jan-Apr']['z']),
                         'OK' if res['race'].startswith('from') else res['race'][:40], res['push'], fnum(res['push_share'], 3)]
                bv = vv.get('busy_only'); bn = res['busy_filter']
                vals += ([bv['PASS'], ','.join(bv['fail']) or '-', bv['months_held_design'], fnum(bv['months_held_forward']),
                          ','.join(m[2:] for m in bv['months_holding']) or '-', fnum(bn['waves_kept_share']['Sep-Dec'], 3),
                          fnum(bn['waves_kept_share']['Jan-Apr'], 3)] if bv else ['NOT RUN', bn[:60], '', '', '', '', ''])
                for kind, note in (('move', res['move_spent_push_at_fire']), ('hour', res['move_spent_hour_peak'])):
                    for p in ('Sep-Dec', 'Jan-Apr'):
                        mv = (note.get(p) or {}) if isinstance(note, dict) else {}
                        vals += [fnum(mv.get(k), 0 if k == 'run_age_min_median' else 2) if mv else ('NOT RUN' if k == MV[0] else '') for k in MV]
                for m in M.DESIGN + M.FORWARD:
                    t = V['months'][m]
                    vals += [t['waves_1h'], fnum(t['offer_1h_median_c']), fnum(t['random_offer_1h_median_c']), fnum(t['edge_1h_vs_random_c']),
                             fnum(t['first_1h_share'], 3), fnum(t['random_first_1h_share'], 3), fnum(t['net_first_vs_random_pts'], 1),
                             fnum(t['net_vs_random_nopre_pts'], 1), int(t['holds'])]
                f.write('\t'.join(str(x) for x in vals) + '\n')
    c30 = ['alarm_id', 'code', 'V', 'lean', 'RULE_30OCT', 'fail', 'direction_months', 'z', 'money_months', 'loss_months', 'thin_months',
           'busy_top2_coins_share', 'busy_top5_waves_share', 'busy_best5_days_share', 'FIRST_LOOK_v5',
           'fwd_RULE_30OCT', 'fwd_fail', 'fwd_direction_months', 'fwd_z', 'fwd_money_months', 'fwd_loss_months', 'fwd_thin_months'] + \
          ['%s_%s' % (m[2:], k) for m in M.DESIGN + M.FORWARD for k in ('dir', 'money', 'loss')]
    with open(os.path.join(out, 'FL_RULE30.tsv'), 'x') as f:
        f.write('\t'.join(c30) + '\n')
        for r, res in rows:
            for aid in r['alarm_ids'].split(','):
                if res is None:
                    f.write('\t'.join([aid, r['code'], r['V'], r['lean'], 'NOT RUN'] + [''] * (len(c30) - 5)) + '\n'); continue
                d, w = res['rule_30oct']['Sep-Dec'], res['rule_30oct']['Jan-Apr']; sp = d['spread_busy'] or {}
                mm = lambda ms: ','.join(m[2:] for m in ms) or '-'
                vals = [aid, r['code'], r['V'], r['lean'], d['PASS'], '; '.join(d['fail']) or '-', d['direction_months'], fnum(d['z']), d['money_months'],
                        mm(d['loss_months']), mm(d['thin_months']), fnum(sp.get('top2_coins_share')), fnum(sp.get('top5_waves_share')),
                        fnum(sp.get('best5_days_share')), res['verdict']['PASS'],
                        w['PASS'], '; '.join(w['fail']) or '-', w['direction_months'], fnum(w['z']), w['money_months'], mm(w['loss_months']), mm(w['thin_months'])]
                for m in M.DESIGN + M.FORWARD:
                    t = (d if m in M.DESIGN else w)['months'][m]
                    vals += [int(t['direction']), '-' if t['thin'] else int(t['money']), '-' if t['thin'] else int(t['loss'])]
                f.write('\t'.join(str(x) for x in vals) + '\n')
    print('FL_SUMMARY %s (%d codes, %d run)' % (s16(os.path.join(out, 'FL_SUMMARY.tsv')), len(rows), sum(1 for _, x in rows if x)))
    print('FL_RULE30 %s' % s16(os.path.join(out, 'FL_RULE30.tsv')))
    c7 = ['alarm_id', 'code', 'V', 'lean', 'RULE_7', 'SepDec', 'fail', 'moves_months', 'z', 'excess_pts', 'without_top2_coins_pts', 'top2_coins',
          'without_best5_days_pts', 'busy_fires', 'matched_share', 'recent_ratio', 'normal_ratio', 'thin_months', 'normal_only_z', 'lean_months', 'lean_z',
          'JanApr', 'fwd_fail', 'fwd_moves_months', 'fwd_z', 'fwd_excess_pts', 'fwd_without_top2_coins_pts', 'fwd_without_best5_days_pts',
          'fwd_matched_share', 'fwd_recent_ratio', 'fwd_normal_ratio', 'fwd_thin_months', 'fwd_normal_only_z', 'fwd_lean_months', 'fwd_lean_z', 'RULE_30OCT'] + \
         ['%s_excess_pts' % m[2:] for m in M.DESIGN + M.FORWARD]
    with open(os.path.join(out, 'FL_RULE7.tsv'), 'x') as f:
        f.write('\t'.join(c7) + '\n')
        for r, res in rows:
            for aid in r['alarm_ids'].split(','):
                if res is None:
                    f.write('\t'.join([aid, r['code'], r['V'], r['lean'], 'NOT RUN'] + [''] * (len(c7) - 5)) + '\n'); continue
                q = res['rule_7']; vals = [aid, r['code'], r['V'], r['lean'], q['RULE_7']]
                for p in ('Sep-Dec', 'Jan-Apr'):
                    d = q[p]; run = d['PASS'] != 'NOT RUN'; g = (lambda k, nd=2: fnum(d.get(k), nd)) if run else (lambda k, nd=2: '')
                    mm = ','.join(m[2:] for m in d.get('thin_months', [])) or '-'
                    if p == 'Sep-Dec':
                        vals += [d['PASS'], '; '.join(d['fail']) or '-', d.get('moves_months', ''), g('z'), g('excess_pts', 1), g('without_top2_coins_pts', 1),
                                 ','.join(d.get('top2_coins', [])) or '-', g('without_best5_days_pts', 1), d.get('busy_fires', ''), g('matched_share', 3),
                                 g('recent_ratio'), g('normal_ratio'), mm if run else '', fnum(d['normal_only']['z']) if run else '', d['lean']['months'], fnum(d['lean']['z'])]
                    else:
                        vals += [d['PASS'], '; '.join(d['fail']) or '-', d.get('moves_months', ''), g('z'), g('excess_pts', 1), g('without_top2_coins_pts', 1),
                                 g('without_best5_days_pts', 1), g('matched_share', 3), g('recent_ratio'), g('normal_ratio'), mm if run else '',
                                 fnum(d['normal_only']['z']) if run else '',
                                 d['lean']['months'], fnum(d['lean']['z'])]
                vals.append(res['rule_30oct']['Sep-Dec']['PASS'])
                for m in M.DESIGN + M.FORWARD:
                    t = q['Sep-Dec' if m in M.DESIGN else 'Jan-Apr']['months'][m]
                    vals.append(fnum(t.get('excess_pts'), 1) if 'excess_pts' in t else '')
                f.write('\t'.join(str(x) for x in vals) + '\n')
    print('FL_RULE7 %s' % s16(os.path.join(out, 'FL_RULE7.tsv')))
    for key, beside in (('rule_8', 'rule_7'), ('rule_9', 'rule_8')):        # edition 9: RULE_9 beside RULE_8, one writer
        lab, blab = key.upper(), beside.upper(); fn = 'FL_%s.tsv' % lab.replace('_', '')
        c8 = ['alarm_id', 'code', 'V', 'lean', lab]
        for p in ('SepDec', 'JanApr'):
            for b in ('SIZE', 'SIDE'):
                c8 += ['%s_%s' % (b, p), '%s_%s_fail' % (b, p), '%s_%s_months' % (b, p), '%s_%s_z' % (b, p), '%s_%s_pts' % (b, p)]
        c8 += [blab]
        with open(os.path.join(out, fn), 'x') as f:
            f.write('\t'.join(c8) + '\n')
            for r, res in rows:
                for aid in r['alarm_ids'].split(','):
                    if res is None:
                        f.write('\t'.join([aid, r['code'], r['V'], r['lean'], 'NOT RUN'] + [''] * (len(c8) - 5)) + '\n'); continue
                    q = res[key]; vals = [aid, r['code'], r['V'], r['lean'], q[lab]]
                    for p in ('Sep-Dec', 'Jan-Apr'):
                        for b in ('SIZE', 'SIDE'):
                            d = q[p][b]
                            vals += [d['PASS'], '; '.join(d['fail']) or '-', d.get('months_holding', ''), fnum(d.get('z')), fnum(d.get('excess_pts'), 1)]
                    vals.append(res[beside][blab])
                    f.write('\t'.join(str(x) for x in vals) + '\n')
        print('%s %s' % (fn[:-4], s16(os.path.join(out, fn))))


if __name__ == '__main__':
    try:
        main(*sys.argv[1:])
    except M.Refused as e:
        print('REFUSED %s' % e); sys.exit(2)
