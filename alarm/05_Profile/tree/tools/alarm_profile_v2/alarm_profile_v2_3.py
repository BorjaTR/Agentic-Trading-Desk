# alarm_profile_v2_3.py (SCOUT 2 Nov 2026, V1_19_FIRSTLOOK): alarm_profile_v2_2.py with only OUT_ROOT and HL_ROOT from the environment (settings keys) and its own file name in CODE_FILES; EDITION stays 2.2, the values are the same.
"""RESEARCH tools/alarm_profile_v2/alarm_profile_v2_2.py = alarm_profile EDITION 2.2, GENERIC (SCOUT 30 Oct 2026). TEST, NOT REVIEWED.
EDITION 2.2 = edition 2.1 (withdrawn) + reviewer E's fixes (30 Oct): (1) with no onset the run end is a named choice, never a hidden one:
build(..., run_end_mode='alarm') searches the last 60 s (the onset window, fixed: a liquidation print never moves it: the push still going
at the alarm, edition 2's reading without its print) and run_end_mode='hour' the hour before the alarm (the hour's extreme: a move that
peaked and pulled back, edition 2.1's reading); the seal names the mode; build a list in both modes to see both; (2) pre_move_pct and
pre_speed_pct_min join the burst-span values NOT_KNOWN on a row with no onset (with no onset there is no 'before the burst'); (3) every
subject needs its own out root: the shared research store is refused for A02 too (edition 1 keeps A02's live parts), by real path, by
same folder, and a root that already holds another subject's parts is refused; (4) export, given the alarm list, refuses a list that is
not the one the subject was built from (its sha16 in the build's sources) and refuses a row that list does not hold, so onset_rule is
never guessed. Edition 2.1's docstring follows unchanged.
RESEARCH tools/alarm_profile_v2/alarm_profile_v2_1.py = alarm_profile EDITION 2.1, GENERIC (SCOUT 30 Oct 2026). TEST, NOT REVIEWED.
EDITION 2.1 = edition 2 (alarm_profile_v2.py, RELEASE_profile_V2_0) + 3 changes for GENERIC subjects only (A02, A02_1, A02N unchanged):
(1) QUANT's review item 1 (30 Oct 08:35:54Z): a generic burst starts at the onset's own 5 s row, never at a liquidation print, so unrelated
liquidations no longer move the run end, split, speed, size or oi spans (GenericEp.burst_rows); (2) QUANT's item 2: size_vs_bar and
growth read A01's liquidation bar: NOT_KNOWN for a generic subject; (3) SCOUT's finding on the first real generic run (T18, AD4
SETTLEBACK V3: 32 pct of fires run_pct <= 0): on a row with no onset (onset = the alarm) the run end is the price extreme in the push
direction over the RUN_LOOK_GENERIC_S (1 h) before the alarm, not over its last 60 s, so an alarm that fires after a pullback no longer
restarts its run at the pullback (GenericEp.run_end); on such a row every value over the burst span (the alarm's own 5 s row) is
NOT_KNOWN (BURST_SPAN). Edition 2's docstring follows unchanged.
RESEARCH tools/alarm_profile_v2 = alarm_profile EDITION 2, GENERIC (SCOUT 30 Oct 2026; the owner 08:50-08:53 Berlin: "make it generic ...
a new release of the tool, the old one can continue running ... a second folder with the new edition"). TEST, NOT REVIEWED.
EDITION 2 = edition 1 (tools/alarm_profile/alarm_profile.py, QUANT, RELEASE_profile_V1_8, frozen and still running for A02) byte for
byte except: (1) any subject name of capitals, digits and _ (up to 24) is accepted besides A02, A02_1 and A02N: a GENERIC subject has
no candidate filter and no context subject; (2) a generic subject's list may omit onset_t or leave it blank: the onset is then the alarm
itself (onset_t = t); the count is in the seal; (3) a generic subject is never written to the shared research store (OUT_ROOT): its out
root is required, and its catalog is generated for that subject into the out root (EPI_CATALOG_<SUBJECT>.tsv, checked on every build);
(4) the proof, profile and context tables are read from edition 1's folder (same values, same cards); (5) a new command 'export' writes
the values of every alarm as one TSV (given the alarm list: its onset rule per row, 'list' or 't'); (6) QUANT's design for any alarm
(tools/alarm_profile/DESIGN_GENERIC_V1.md section 2, 30 Oct 07:40Z): for a generic subject the blocks shape and hyperliquid are NOT_KNOWN
(they mean something only when liquidations are the trigger) and, on a row whose onset is the alarm itself, the values anchored on the
onset (burst_move_pct, forced_share, burst_s, onset_to_alarm_s, burst_speed_pct_min, speed_ratio, burst_speed_vs_normal) are NOT_KNOWN,
never 0. The episode logic (episode_blocks.py, VERSION 3) is edition 1's, copied unchanged. Edition 1's docstring follows unchanged.
RESEARCH tools/alarm_profile (QUANT, 22 Oct 2026; reviewer SCOUT; built to the research-tool-design skill).
QUESTION: what did each liquidation alarm's episode look like at the alarm, so it can be compared with other liquidations (the move from
where it really started, the speed, the liquidations' size against the coin's normal, their shape, the other side, the open positions)?
And PROFILES: named groupings over every value of this tool AND the 125 context values (tools/alarm_context), chosen by a text file
(PROFILES_V1.tsv), so the owner can group the metrics as he wants (13:08 Berlin) without computing anything again.
PROOF (the owner 13:13 Berlin: "we prove it means what it says"): every value of this tool has a proof card (PROOFS_V1.tsv: its claim,
the proofs it must pass, each pass line, written before any run); PROOF_RESULTS_V1.tsv holds the results with their receipts; the profile
view prints each value's status (PROVEN, or OPEN naming what is missing). Context values show their own evidence (CTX_INPUTS_V1.tsv: the
lab codes they read and METRICS_V1's status of each).
UNIT: one row = one alarm, known at the alarm (as_of_us = known_at_us = the alarm). DESCRIBES ONLY: no outcome after the alarm in any part.
OUTPUT, THE ONE FORMAT: lab3.write.write_part to the research root, part EPI.<SUBJECT> (ROWS kind), codes EPI.<SUBJECT>.<column>, the
catalog EPI_CATALOG_V1.tsv generated from episode_blocks.py docstrings. A value not known: no bits, reason NOT_KNOWN.
GENERATED ONCE: seal (settings) and sources (sha16 of the alarm list, the code, the catalog, every lab index read) in the part's index; a
day with the same seal and sources is left as it is (UP TO DATE). SEALED: from 1 Jan 2026 never built or read (the tests seal December).
  python3 alarm_profile.py build <lab_days> <lab3 code dir> <alarms tsv> <subject> <first> <last> [out root]
  python3 alarm_profile.py show  <out root> <lab3 code dir> <subject> <first> <last> [values, comma]           (prints; writes nothing)
  python3 alarm_profile.py profile <out root> <lab3 code dir> <subject> <first> <last> <PROFILE> [<coin> <t>]  (prints; writes nothing)
  python3 alarm_profile.py profiles | status [metrics tsv]                                                    (prints)
  python3 alarm_profile.py catalog                                                                            (regenerates the catalog)"""
import csv, datetime as dt, hashlib, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import episode_blocks as EB                                          # noqa: E402

TOOL = 'alarm_profile'; VERSION = 3                     # 2 (22 Oct 12:4xZ): the run start's search ends at the run end; 3: the PAUSE rule (the owner's 'no progress, 30 min')
EDITION = '2.2'                                         # edition 2.2: the no-onset run end a named mode ('alarm' 60 s or 'hour')
V1_DIR = os.path.normpath(os.path.join(HERE, '..', 'alarm_profile'))   # edition 1: its proof, profile and context tables are read from there
GENERIC_RE = __import__('re').compile(r'^[A-Z][A-Z0-9_]{0,23}$')
OUT_ROOT = os.environ.get('RESEARCH_STORE') or os.path.join(HERE, 'NO_RESEARCH_STORE_SET')   # V1_19: the settings key RESEARCH_STORE; only ever refused as an out root
CATALOG = os.path.join(HERE, 'EPI_CATALOG_V1.tsv')
PROFILES = os.path.join(V1_DIR, 'PROFILES_V1.tsv')
PROOFS = os.path.join(V1_DIR, 'PROOFS_V1.tsv')
RESULTS = os.path.join(V1_DIR, 'PROOF_RESULTS_V1.tsv')
CTX_INPUTS = os.path.join(V1_DIR, 'CTX_INPUTS_V1.tsv')
CTX_DIR = os.path.normpath(os.path.join(HERE, '..', 'alarm_context'))
SUBJECTS = {'A02': ('D0', 'A02'), 'A02_1': ('D1', None), 'A02N': ('N0', None)}   # subject -> (candidate in the alarm list, the CTX subject or None); A02N: no growth (ALARM_DEFINITION_V4, the owner 18:12 Berlin 22 Oct)
SEALED = (('20260601', '99991231', 'June 2026 onward: BLIND (the owner 23 Oct 06:01Z: research uses Sep 2025 to May 2026; = lab3/law.py)'),)   # LAB1 23 Oct; was 20260101 on
DAYS_ROWS, DAYS_PRICE, DAYS_TOTALS = 1, 2, 8                         # lab days read before the alarm day: 5 s rows and OI, prices, daily totals
CODES = {'long': 'A1.S01', 'short': 'A1.S02', 'oi': 'E2.S02', 'oi_carried': 'E2.S03'}
HL_ROOT = os.environ.get('HL_FILLS') or os.path.join(HERE, 'NO_HL_FILLS_SET')   # V1_19: the settings key HL_FILLS; a generic subject never reads it
HL_DIRS = tuple(os.path.join(HL_ROOT, d) for d in ('01', '02', '03', 'd3_01', 'd3_02', 'd3_03', 'd3_04', 'd3_05'))   # SCOUT's hl_fills_v1, 12 Sep - 26 Oct 2025
HL_NAME = {'PEPE': 'kPEPE', 'BONK': 'kBONK', 'SHIB': 'kSHIB'}       # the lab's 1000-coin contracts are Hyperliquid's k-coins (same price scale)
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')
NOT_KNOWN = 'NOT_KNOWN'
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')
CODE_FILES = ('alarm_profile_v2_3.py', 'episode_blocks.py', 'EPI_CATALOG_V1.tsv', os.path.join('..', 'alarms', 'a01_onset_v2.py'),
              os.path.join('..', 'alarms', 'a02_climax_v3.py'))


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def day0(d):
    return int(dt.datetime.strptime(d, '%Y%m%d').replace(tzinfo=dt.timezone.utc).timestamp())


def utc_day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def sealed(day, table=None):
    for lo, hi, why in (SEALED if table is None else table):
        if lo <= str(day) <= hi:
            return why
    return None


def sealed_read(day, table=None):
    """a sealed day, or the day after one (the lab's own 24 h windows reach into it): its lab values are never read"""
    return sealed(day, table) or (('the day after a sealed day (%s)' % shift(str(day), -1)) if sealed(shift(str(day), -1), table) else None)


def code_name(subject, col):
    return 'EPI.%s.%s' % (subject, col)


def part_name(subject):
    return 'EPI.%s' % subject


def columns():
    cols = EB.doc_columns(); names = [c[2] for c in cols]
    if len(set(names)) != len(names):
        raise ValueError('a column named twice: %s' % sorted({n for n in names if names.count(n) > 1}))
    return cols


def catalog_text(subjects=tuple(SUBJECTS)):
    lines = ['# EPI_CATALOG_V1: generated by alarm_profile.py catalog from episode_blocks.py docstrings; METRICS_V1 columns + meaning, unit, level, block',
             '\t'.join(CAT_COLS)]
    for s in subjects:
        for lv, bl, col, mean, unit in columns():
            lines.append('\t'.join([code_name(s, col), 'ROWS', 'event', '0', 'coin', mean, unit, lv, bl]))
    return '\n'.join(lines) + '\n'


def subject_info(subject):
    """edition 2: (candidate, CTX subject, generic) of a subject: the catalogued three as edition 1, any other name of capitals, digits and _
    (up to 24) generic (no candidate filter, no context); anything else refused"""
    if subject in SUBJECTS:
        return SUBJECTS[subject][0], SUBJECTS[subject][1], False
    if not GENERIC_RE.match(str(subject)):
        raise ValueError('subject %r: capitals, digits and _ only (up to 24), or one of %s' % (subject, ', '.join(SUBJECTS)))
    return None, None, True


GENERIC_OFF = ('shape', 'hyperliquid')                 # QUANT DESIGN_GENERIC_V1 s.2: only meaningful when liquidations are the trigger
SINCE_ONSET = ('burst_move_pct', 'forced_share', 'burst_s', 'onset_to_alarm_s', 'burst_speed_pct_min', 'speed_ratio', 'burst_speed_vs_normal')
GENERIC_OFF_VALUES = ('size_vs_bar', 'growth')          # edition 2.1 (QUANT 08:35:54Z item 2): they read A01's liquidation bar
BURST_SPAN = SINCE_ONSET + ('max_move_60s_pct', 'forced_usd_log', 'peak15_usd_log', 'peak60_usd_log', 'size_vs_week', 'other_usd_log',
                            'other_share', 'oi_chg_burst_pct', 'burst_vs_oi_bp',
                            'pre_move_pct', 'pre_speed_pct_min')   # with no onset the burst is the alarm's own 5 s row (2.2: + 'before the burst')
RUN_END_MODES = {'alarm': 60, 'hour': 3600}             # edition 2.2, no onset: the run end is searched over the last 60 s ('alarm': the onset
                                                        # window, fixed) or the hour before the alarm ('hour': the hour's extreme)


class GenericEp(EB.Ep):
    """edition 2.1, the episode of a GENERIC subject's alarm (A02, A02_1 and A02N keep EB.Ep): (1) the burst starts at the onset's own 5 s
    row, never at a liquidation print (QUANT 08:35:54Z item 1); (2) the run end: edition 1's rule (the price extreme since the burst start,
    the latest on ties, the alarm itself when the alarm's close is that extreme) when the onset is given; with no onset (onset = the alarm)
    the extreme is searched over the RUN_END_MODES[run_end_mode] seconds before the alarm (2.2: 'alarm' 60 s, 'hour' 3600 s)"""
    def __init__(self, *a, onset_given=True, run_end_mode='alarm', **k):
        super().__init__(*a, **k); self.onset_given = bool(onset_given)
        if run_end_mode not in RUN_END_MODES:
            raise ValueError('run_end_mode %r: one of %s' % (run_end_mode, sorted(RUN_END_MODES)))
        self.run_end_mode = run_end_mode

    def burst_rows(self):
        if 'br' not in self._c:
            self._c['br'] = (self.k0, float(self.T5 + EB.STEP * self.k0 - EB.STEP))
        return self._c['br']

    def run_end(self):
        if 'end' not in self._c:
            w0 = self.burst_rows()[1] if self.onset_given else float(self.t - RUN_END_MODES[self.run_end_mode])
            k = (self.te_us > int(round(w0 * 1_000_000))) & (self.px > 0)
            ts = np.concatenate(([w0], self.te_us[k] / 1e6)); xs = np.concatenate(([self.x(w0)], self.sgn * np.log(self.px[k])))
            ok = np.isfinite(xs); xt = self.x(self.t); out = (float(self.t), xt)
            if ok.any():
                m = float(np.max(xs[ok])); i = int(np.flatnonzero(ok & (xs == m))[-1])
                if not (np.isfinite(xt) and xt >= m):
                    out = (float(ts[i]), m)
            self._c['end'] = out
        return self._c['end']


def blank_generic(cols, e):
    """edition 2, generic subjects: the GENERIC_OFF blocks NOT_KNOWN on every row; the onset-anchored values NOT_KNOWN where the onset is the
    alarm itself (no onset given)"""
    off = {c[2] for c in columns() if c[1] in GENERIC_OFF}
    fb = ~np.asarray(e['onset_given'], bool)
    for k in cols:
        if k in off or k in GENERIC_OFF_VALUES:                      # edition 2.1: + size_vs_bar, growth on every generic row
            cols[k][:] = np.nan
        elif k in BURST_SPAN:                                        # edition 2.1: every burst-span value on a row with no onset
            cols[k][fb] = np.nan
    return cols


def load_alarms(path, candidate=None, onset_fallback=False):
    """the alarms (coin, t, side, onset_t) of one candidate (when the list has a 'candidate' column); a (coin, t) twice is refused.
    Edition 2: with onset_fallback (generic subjects) a missing or blank onset_t is the alarm itself (t), onset_given False on that row;
    load_alarms.onset_fallback counts them"""
    with open(path) as f:
        R = [r for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')]
    if candidate is not None and R and 'candidate' in R[0]:
        R = [r for r in R if r['candidate'] == candidate]
    R = [r for r in R if int(float(r['side'])) != 0]
    fb = 0; given = [True] * len(R)
    if onset_fallback:
        for j, r in enumerate(R):
            if (r.get('onset_t') or '').strip() == '':
                r['onset_t'] = r['t']; fb += 1; given[j] = False
    ev = dict(coin=np.array([r['coin'] for r in R]), t=np.array([int(float(r['t'])) for r in R], np.int64),
              side=np.array([int(float(r['side'])) for r in R], int), onset_t=np.array([int(float(r['onset_t'])) for r in R], np.int64),
              onset_given=np.array(given, bool))
    load_alarms.onset_fallback = fb
    keys = list(zip(ev['coin'].tolist(), ev['t'].tolist()))
    if len(set(keys)) != len(keys):
        raise ValueError('%s: an alarm (coin, t) listed twice: refused' % path)
    if (ev['onset_t'] > ev['t']).any():
        raise ValueError('%s: an onset after its alarm: refused' % path)
    return ev


def settings(subject, candidate, lab_root, hl_dirs=HL_DIRS):
    return json.dumps({'tool': TOOL, 'version': VERSION, 'subject': subject, 'candidate': candidate, 'lab_root': lab_root,
                       'hl_dirs': list(hl_dirs), 'hl_names': HL_NAME,
                       'known_at': 'the alarm', 'decisions_min': [0], 'codes': CODES,
                       'lab_days_before': {'rows_oi': DAYS_ROWS, 'prices': DAYS_PRICE, 'daily_totals': DAYS_TOTALS},
                       'episode': EB.SETTINGS}, sort_keys=True)


class LabSource:
    """what the builder reads, from lab3 through one Days reader (purpose research): 5 s rows and minute codes of a day (NaN arrays for a
    day not built or sealed, listed in skipped), prices of a day, daily forced totals (cached; pure), and the sha16 of every lab index"""
    def __init__(self, lab_root, code_dir, R=None, LB=None, table=None, hl_dirs=HL_DIRS):
        self.hl_files = {}
        for d in hl_dirs:                                            # {(hl coin, day): path}; a file in two folders is refused
            for n in (sorted(os.listdir(d)) if os.path.isdir(d) else []):
                if n.startswith('HLF_') and n.endswith('.npz'):
                    key = tuple(n[4:-4].rsplit('_', 1))
                    if key in self.hl_files:
                        raise ValueError('Hyperliquid file %s in two folders: refused' % n)
                    self.hl_files[key] = os.path.join(d, n)
        if R is None or LB is None:
            sys.path.insert(0, code_dir)
            from lab3 import days as LD, bins as LBm
            R = R or LD.Days(lab_root, 'research'); LB = LB or LBm
        self.R = R; self.LB = LB; self.root = lab_root; self.table = table; self.skipped = []; self._tot = {}; self._sha = {}
        self.hl_dirs = tuple(hl_dirs)

    def _sha_of(self, d, part):
        k = (d, part)
        if k not in self._sha:
            self._sha[k] = sha16_file(os.path.join(self.root, 'day=%s' % d, part, 'index.json'))
        return self._sha[k]

    def rows(self, code, d, coins, steps):
        """(coins, steps) values of a CLOCK code on day d; NaN when the day is sealed or not built; -> (array, {source: sha16})"""
        if sealed_read(d, self.table):
            self.skipped.append((d, code, 'SEALED')); return np.full((len(coins), steps), np.nan), {}
        try:
            a = np.asarray(self.R.read(code, 'v', [d], coins)[0], float)
            pt = self.R.part_of(code, d)
            return a, {'lab:day=%s/%s' % (d, pt): self._sha_of(d, pt)}
        except (LookupError, OSError) as e:
            self.skipped.append((d, code, type(e).__name__)); return np.full((len(coins), steps), np.nan), {}

    def prices(self, d, coins):
        """{coin: (te_us, px)} of day d (empty for a sealed or unbuilt day) -> (dict, {source: sha16})"""
        if sealed_read(d, self.table):
            self.skipped.append((d, 'PRICE', 'SEALED')); return {}, {}
        try:
            off, b = self.LB.read_bins(self.R, d, coins)
        except (LookupError, OSError) as e:
            self.skipped.append((d, 'PRICE', type(e).__name__)); return {}, {}
        out = {c: (np.asarray(b['te'][off[i]:off[i + 1]], np.int64), np.asarray(b['px'][off[i]:off[i + 1]], float)) for i, c in enumerate(coins)}
        return out, {'lab:day=%s/%s' % (d, self.LB.PART): self._sha_of(d, self.LB.PART)}

    def hl(self, coin, days):
        """Hyperliquid liquidations of the coin over days (the liquidated accounts' rows: SCOUT's HLF lself = 1) -> (None or dict, sources).
        A day counts as covered when its file exists and holds trades (a coin with no Hyperliquid market has an empty file)."""
        name = HL_NAME.get(coin, coin); cov = set(); lt, usd, sd = [], [], []; src = {}
        for d in days:
            p = self.hl_files.get((name, d))
            if p is None or sealed_read(d, self.table):
                continue
            with np.load(p, allow_pickle=False) as z:
                z = {k: z[k] for k in z.files}                       # load once (the L47 rule)
            src['hl:%s' % os.path.basename(p)] = sha16_file(p)
            if len(z['t']) == 0:
                continue
            cov.add(d); k = z['lself'] == 1
            lt.append(z['lt'][k] / 1000.0); usd.append(z['lpx'][k] * z['lsz'][k]); sd.append(z['lside'][k])
        if not cov:
            return None, src
        return dict(days=cov, lt=np.concatenate(lt), usd=np.concatenate(usd), side=np.concatenate(sd)), src

    def totals(self, d, coins):
        """{coin: (long USD, long share known, short USD, short share known)} of whole day d -> (dict, sources)"""
        need = [c for c in coins if (d, c) not in self._tot]; src = {}
        if need:
            a, s1 = self.rows(CODES['long'], d, need, 86400 // EB.STEP); b, s2 = self.rows(CODES['short'], d, need, 86400 // EB.STEP)
            for i, c in enumerate(need):
                fa, fb = np.isfinite(a[i]), np.isfinite(b[i])
                self._tot[(d, c)] = (float(a[i][fa].sum()), float(fa.mean()), float(b[i][fb].sum()), float(fb.mean()), {**s1, **s2})
        for c in coins:
            src.update(self._tot[(d, c)][4])
        return {c: self._tot[(d, c)][:4] for c in coins}, src


CHUNK = 16                                                           # coins read at once (memory: the L47 rule)


def chunk_eps(src, day, ev, idx, coins, used, generic=False, run_end_mode='alarm'):
    """the Ep of the alarms idx (all on day, coins = their coins), one at a time; the chunk's lab arrays are read once; used gets every source"""
    P = shift(day, -DAYS_ROWS); n5 = 86400 // EB.STEP; A = {}; O = {}
    for nm in ('long', 'short'):
        parts = []
        for d in (P, day):
            a, s = src.rows(CODES[nm], d, coins, n5); parts.append(a); used.update(s)
        A[nm] = np.concatenate(parts, axis=1)
    for nm in ('oi', 'oi_carried'):
        parts = []
        for d in (P, day):
            a, s = src.rows(CODES[nm], d, coins, 1440); parts.append(a); used.update(s)
        O[nm] = np.concatenate(parts, axis=1)
    oi_t = np.concatenate([day0(d) + 60.0 * np.arange(1440) for d in (P, day)])
    PX = {c: [] for c in coins}
    for d in [shift(day, -k) for k in range(DAYS_PRICE, -1, -1)]:
        p, s = src.prices(d, coins); used.update(s)
        for c in coins:
            if c in p:
                PX[c].append(p[c])
    TOT = {}
    for d in [shift(day, -k) for k in range(DAYS_TOTALS, 0, -1)]:
        tt, s = src.totals(d, coins); used.update(s); TOT[d] = tt
    HLC = {}
    for c in coins:
        HLC[c], s = src.hl(c, (P, day)); used.update(s)
    ci = {c: i for i, c in enumerate(coins)}; T5 = day0(P); last = {}
    for i in idx:
        coin, t, side, t0 = ev['coin'][i], int(ev['t'][i]), int(ev['side'][i]), int(ev['onset_t'][i])
        if coin not in last:                                         # the coin's prices, once (sorted by bin end)
            te = np.concatenate([q[0] for q in PX[coin]]) if PX[coin] else np.zeros(0, np.int64)
            px = np.concatenate([q[1] for q in PX[coin]]) if PX[coin] else np.zeros(0)
            o = np.argsort(te, kind='mergesort'); last = {coin: (te[o], px[o])}
        te, px = last[coin]; k = ci[coin]; fz = 'short' if side > 0 else 'long'; ot = 'long' if side > 0 else 'short'
        daily = {d: ((TOT[d][coin][2], TOT[d][coin][3]) if side > 0 else (TOT[d][coin][0], TOT[d][coin][1])) for d in TOT}
        if generic:                                                  # edition 2.1: the generic episode, its onset given or not
            yield GenericEp(coin, t, t0, side, T5, A[fz][k], A[ot][k], te, px, daily, oi_t, O['oi'][k], O['oi_carried'][k], hl=HLC[coin],
                            onset_given=bool(ev['onset_given'][i]), run_end_mode=run_end_mode)
        else:
            yield EB.Ep(coin, t, t0, side, T5, A[fz][k], A[ot][k], te, px, daily, oi_t, O['oi'][k], O['oi_carried'][k], hl=HLC[coin])


def day_values(src, day, ev, generic=False, run_end_mode='alarm'):
    """{column: (n,) float} of the day's alarms (ev), coins read CHUNK at a time, each alarm's Ep used and dropped -> (cols, sources)"""
    names = [c[2] for c in columns()]; n = len(ev['t']); cols = {k: np.full(n, np.nan) for k in names}; used = {}
    coins = sorted(set(ev['coin'].tolist()))
    for c0 in range(0, len(coins), CHUNK):
        part = coins[c0:c0 + CHUNK]; sel = set(part)
        idx = [i for i in np.argsort(np.asarray(ev['coin']), kind='stable').tolist() if ev['coin'][i] in sel]
        for i, e in zip(idx, chunk_eps(src, day, ev, idx, part, used, generic, run_end_mode)):
            for k, v in EB.run_one(e).items():
                cols[k][i] = v
    return cols, used


def day_rows(day, ev, cols, subject):
    """{code: {'step': 'event', 'kind': 'NUMBER', 'rows': {coin: ROWS}}} of one day; rows by coin in alarm order"""
    coins = sorted(set(ev['coin'].tolist())); out = {}
    a_us = np.asarray(ev['t'], np.int64) * 1_000_000
    order = {coin: [i for i in np.argsort(a_us, kind='stable').tolist() if ev['coin'][i] == coin] for coin in coins}
    for col, x in cols.items():
        rows = {}
        for coin in coins:
            r = {k: [] for k in ROWCOLS}
            for i in order[coin]:
                v = float(x[i]); ok = np.isfinite(v)
                r['day'].append(int(day)); r['as_of_us'].append(int(a_us[i])); r['known_at_us'].append(int(a_us[i])); r['value_kind'].append(1)
                r['value_bits'].append(int(np.array([v], '<f8').view('<u8')[0]) if ok else None)
                r['value_txt'].append(None); r['empty_reason'].append('' if ok else NOT_KNOWN); r['stale'].append(0)
            rows[coin] = r
        out[code_name(subject, col)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rows}
    return coins, out


def store_check(out_root, subject):
    """edition 2.2 (reviewer E, SHOULD 4 and 6): every subject needs its own out root: refused when none, when it is the shared research
    store (same real path, or the same folder), or when it already holds another subject's EPI parts (its first 5 days looked at)"""
    if not out_root:
        raise ValueError('%s: give a private out root (never the shared research store %s)' % (subject, OUT_ROOT))
    if os.path.realpath(out_root) == os.path.realpath(OUT_ROOT) or (os.path.isdir(out_root) and os.path.isdir(OUT_ROOT) and os.path.samefile(out_root, OUT_ROOT)):
        raise ValueError('%s: %s is the shared research store: refused (A02 runs edition 1 there)' % (subject, out_root))
    if os.path.isdir(out_root):
        own = part_name(subject)
        for d in sorted(n for n in os.listdir(out_root) if n.startswith('day='))[:5]:
            other = sorted(p for p in os.listdir(os.path.join(out_root, d)) if p.startswith('EPI.') and p != own)
            if other:
                raise ValueError('%s: %s holds another subject (%s): refused' % (subject, out_root, other[0]))


def build(lab_root, alarms_path, subject, first, last, out_root=None, code_dir=None, src=None, write=None, load_catalog=None,
          log=print, table=None, run_end_mode='alarm'):
    """build every alarm day first..last of the subject -> {day: 'WRITTEN' | 'UP TO DATE' | 'REFUSED'}"""
    cand, _, generic = subject_info(subject)
    if run_end_mode not in RUN_END_MODES:
        raise ValueError('run_end_mode %r: one of %s' % (run_end_mode, sorted(RUN_END_MODES)))
    store_check(out_root, subject)
    if write is None or load_catalog is None:
        sys.path.insert(0, code_dir)
        from lab3 import write as LW
        write = write or LW.write_part; load_catalog = load_catalog or LW.load_catalog
    if open(CATALOG).read() != catalog_text():
        raise ValueError('EPI_CATALOG_V1.tsv differs from the blocks: run "alarm_profile.py catalog" first')
    catp = CATALOG
    if generic:
        catp = os.path.join(out_root, 'EPI_CATALOG_%s.tsv' % subject); txt = catalog_text((subject,))
        if os.path.exists(catp):
            if open(catp).read() != txt:
                raise ValueError('%s differs from the blocks for %s: refused' % (catp, subject))
        else:
            os.makedirs(out_root, exist_ok=True)
            with open(catp + '.part', 'x') as fh:
                fh.write(txt)
            os.replace(catp + '.part', catp)
    ev = load_alarms(alarms_path, cand, onset_fallback=generic)
    src = src or LabSource(lab_root, code_dir, table=table)
    cat = load_catalog(catp); seal = settings(subject, cand, lab_root, getattr(src, 'hl_dirs', HL_DIRS))
    if generic:
        seal = json.dumps(dict(json.loads(seal), edition=EDITION, onset_fallback=int(load_alarms.onset_fallback),
                               blocks_off=list(GENERIC_OFF), values_off=list(GENERIC_OFF_VALUES),
                               since_onset_off_without_onset=list(BURST_SPAN), burst_start='the onset row',
                               run_end_generic=run_end_mode, run_look_generic_s=RUN_END_MODES[run_end_mode]), sort_keys=True)
    fixed = {'alarms:%s' % os.path.basename(alarms_path): sha16_file(alarms_path)}
    for f in CODE_FILES:
        fixed['code:%s' % os.path.basename(f)] = sha16_file(os.path.join(HERE, f))
    days = np.array([utc_day(t) for t in ev['t']]); done = {}; part = part_name(subject)
    for day in sorted(set(d for d in days.tolist() if first <= d <= last)):
        if sealed_read(day, table):
            done[day] = 'REFUSED'; log('DAY %s %s REFUSED: %s' % (day, part, sealed_read(day, table))); continue
        sel = days == day; e = {k: v[sel] for k, v in ev.items()}
        n_skip = len(src.skipped); cols, used = day_values(src, day, e, generic, run_end_mode)
        if generic:
            cols = blank_generic(cols, e)
        sources = dict(fixed); sources.update(used)
        ixp = os.path.join(out_root, 'day=%s' % day, part, 'index.json')
        if os.path.exists(ixp):
            with open(ixp) as fh:
                old = json.load(fh)
            if old.get('seal') == seal and old.get('sources') == sources:
                done[day] = 'UP TO DATE'; log('DAY %s %s rows %d UP TO DATE' % (day, part, len(e['t']))); continue
        cs, codes = day_rows(day, e, cols, subject)
        write(out_root, int(day), part, codes, cs, catalog=cat, sources=sources, seal=seal)
        fin = float(np.mean([np.isfinite(v).mean() for v in cols.values()])) if cols else 0.0
        done[day] = 'WRITTEN'
        log('DAY %s %s rows %d coins %d codes %d finite %.3f lab parts %d skipped %d WRITTEN' % (
            day, part, len(e['t']), len(cs), len(codes), fin, len(used), len(src.skipped) - n_skip))
    return done


def read(out_root, code_dir, subject, first, last, values=None, days_reader=None, table=None, with_known_at=False):
    """-> {'coin', 't_alarm', <value>..., 'known_at_us'}: the chosen values (default all) of every alarm first..last, read back through lab3.days
    (purpose research); a sealed day is refused. 'known_at_us' (always, int64 us; D03-01) = the latest stored known_at of the values read;
    with_known_at: also 'known_at', the same clock in seconds (kept for cause_label and older callers)"""
    if days_reader is None:
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        days_reader = LD.Days(out_root, 'research')
    names = [c[2] for c in columns()]; values = list(values) if values else names
    bad = [v for v in values if v not in names]
    if bad:
        raise ValueError('values not in the catalog: %s' % bad)
    keys = {}; vals = {v: {} for v in values}; part = part_name(subject); ka = {}
    for day in days_reader.days():
        if not first <= day <= last:
            continue
        if sealed(day, table):
            raise PermissionError('%s: %s: refused' % (day, sealed(day, table)))
        if part not in days_reader.parts(day):
            continue
        coins = days_reader.index(day, part)['coins']
        for v in values:
            r = days_reader.rows(code_name(subject, v), day, coins)
            for coin in coins:
                for b, a, k in zip(r[coin]['value_bits'], r[coin]['as_of_us'], r[coin]['known_at_us']):
                    key = (coin, a); keys[key] = True; ka[key] = max(ka.get(key, k), k)
                    vals[v][key] = np.array([b], '<u8').view('<f8')[0] if b is not None else np.nan
    order = sorted(keys, key=lambda x: (x[1], x[0]))
    out = {'coin': np.array([k[0] for k in order]), 't_alarm': np.array([k[1] / 1e6 for k in order])}
    for v in values:
        out[v] = np.array([vals[v].get(k, np.nan) for k in order], float)
    out['known_at_us'] = np.array([ka[k] for k in order], dtype=np.int64)
    if with_known_at:
        out['known_at'] = np.array([ka[k] / 1e6 for k in order])
    return out


# ---------------------------------------------------------------- profiles and proof status (read only; nothing is written)
def _tsv(path):
    with open(path) as f:
        return [{k: (v or '') for k, v in r.items()} for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')]


def ctx_columns():
    """[(level, block, column, meaning, unit)] of the context tool, from its catalog (subject A02)"""
    out = []
    for r in _tsv(os.path.join(CTX_DIR, 'CTX_CATALOG_V1.tsv')):
        if r['code'].startswith('CTX.A02.'):
            out.append((r['level'], r['block'], r['code'][len('CTX.A02.'):], r['meaning'], r['unit']))
    return out


def load_profiles(path=PROFILES):
    """{profile: [(group, tool, value, why)]} in file order; ALL = every value of both tools"""
    prof = {}
    for r in _tsv(path):
        prof.setdefault(r['profile'], []).append((r['group'], r['tool'], r['value'], r['why']))
    allp = [(lv.lower(), 'EPI', c, '') for lv, _, c, _, _ in columns()] + [(lv.lower(), 'CTX', c, '') for lv, _, c, _, _ in ctx_columns()]
    prof['ALL'] = allp
    return prof


def check_profiles(path=PROFILES):
    """-> list of problems: a value not in its tool's catalog, a value twice in one profile, an EPI value in no profile"""
    epi = {c[2] for c in columns()}; ctx = {c[2] for c in ctx_columns()}; bad = []; seen_epi = set()
    for name, items in load_profiles(path).items():
        if name == 'ALL':
            continue
        vs = [(tool, v) for _, tool, v, _ in items]
        for tool, v in vs:
            if tool not in ('EPI', 'CTX'):
                bad.append('%s: tool %r' % (name, tool))
            elif v not in (epi if tool == 'EPI' else ctx):
                bad.append('%s: %s %s is not in its catalog' % (name, tool, v))
            if tool == 'EPI':
                seen_epi.add(v)
        dup = sorted({x for x in vs if vs.count(x) > 1})
        if dup:
            bad.append('%s: twice %s' % (name, dup))
    for v in sorted(epi - seen_epi):
        bad.append('EPI %s is in no profile' % v)
    return bad


def metrics_status(path):
    """{lab code: (comp_status, meaning_status)} from METRICS_V1.tsv"""
    return {r['code']: (r.get('comp_status', ''), r.get('meaning_status', '')) for r in _tsv(path)}


MEANING_OK = ('DEFINED', 'CARD_SIGNED')


PROOF_SCOPE_KEYS = ('output_release_sha16', 'definition_sha16', 'input_vintage_sha16', 'subject', 'proof_plan_sha16')


def proof_status(metrics_path=None, proofs=PROOFS, results=RESULTS, ctx_inputs=CTX_INPUTS, expected_scope=None):
    """{(tool, value): (status, detail)}. EPI: PROVEN when every proof its card declares has a PASS result; else OPEN naming the rest.
    CTX: PROVEN when every lab code it reads is RELIABLE and DEFINED or CARD_SIGNED in METRICS_V1, PRICE when the price record check
    (P3 PRICE_RECORD) passed, LIST always (arithmetic on the alarm list, tested in alarm_context), TABLE:types (a hand list); OPEN
    otherwise (TABLE:costs: today's costs applied to the past)."""
    # Scope must come from the inspected output/run manifest, never inferred from PASS rows.
    # Legacy/unscoped receipts remain available as history but cannot certify this output.
    scopes = expected_scope or {}
    # Expected plan identity must come from the inspected output's frozen scope.
    import hashlib
    with open(proofs, 'rb') as stream:
        plan_sha16 = hashlib.sha256(stream.read()).hexdigest()[:16]
    res = {}
    for r in (_tsv(results) if os.path.exists(results) else []):
        want = scopes.get(r['value'], {})
        if want.get('proof_plan_sha16') != plan_sha16:
            continue
        if not all(want.get(k) and r.get(k) == want[k] for k in PROOF_SCOPE_KEYS):
            continue
        key = (r['value'], r['proof'])
        # An unresolved FAIL cannot disappear because a later CSV row says PASS.
        if res.get(key) == 'FAIL' or r.get('result') == 'FAIL':
            res[key] = 'FAIL'
        elif r.get('result') == 'PASS':
            res[key] = 'PASS'
    out = {}
    card = {}
    for r in _tsv(proofs):
        card.setdefault(r['value'], []).append(r['proof'])
    for _, _, c, _, _ in columns():
        need = card.get(c, [])
        miss = [p for p in need if res.get((c, p)) != 'PASS']
        failed = [p for p in need if res.get((c, p)) == 'FAIL']
        if not need:
            out[('EPI', c)] = ('OPEN', 'no proof card')
        elif failed:
            out[('EPI', c)] = ('FAILED', 'failed: ' + ', '.join(failed))
        else:
            out[('EPI', c)] = ('PROVEN', ', '.join(need)) if not miss else ('OPEN', 'pending: ' + ', '.join(miss))
    ms = metrics_status(metrics_path) if metrics_path and os.path.exists(metrics_path) else {}
    price_ok = res.get(('PRICE', 'P3_PRICE_RECORD')) == 'PASS'
    for r in _tsv(ctx_inputs):
        why = []
        for x in [s for s in (r['inputs'] + ',' + r['upstream']).split(',') if s]:
            if x == 'LIST' or x == 'TABLE:types':
                continue
            if x == 'PRICE':
                if not price_ok:
                    why.append('PRICE record check pending')
                continue
            if x == 'TABLE:costs':
                why.append('costs: today\'s table applied to the past'); continue
            st = ms.get(x)
            if st is None:
                why.append('%s: no METRICS_V1 row read' % x)
            elif st[0] != 'RELIABLE' or st[1] not in MEANING_OK:
                why.append('%s %s/%s' % (x, st[0], st[1]))
        own = card.get('CTX.' + r['value'], [])
        if not own:
            why.append('no context-output proof card')
        elif any(res.get(('CTX.' + r['value'], p)) == 'FAIL' for p in own):
            out[('CTX', r['value'])] = ('FAILED', 'context-output proof failed')
            continue
        elif any(res.get(('CTX.' + r['value'], p)) != 'PASS' for p in own):
            why.append('context-output proof pending')
        out[('CTX', r['value'])] = ('PROVEN', 'lab inputs ' + (r['inputs'] or '-')) if not why else ('OPEN', '; '.join(why))
    return out


def _join(epi, ctx):
    """rows of epi (coin, t_alarm) with ctx values at decision 0 joined on (coin, alarm)"""
    if ctx is None:
        return {}
    k = {(c, int(round(t * 1e6))): i for i, (c, t, td) in enumerate(zip(ctx['coin'], ctx['t_alarm'], ctx['t_decision'])) if abs(td - t) < 1e-6}
    idx = np.array([k.get((c, int(round(t * 1e6))), -1) for c, t in zip(epi['coin'], epi['t_alarm'])], int)
    out = {}
    for v, a in ctx.items():
        if v in ('coin', 't_alarm', 't_decision'):
            continue
        out[v] = np.where(idx >= 0, np.asarray(a, float)[np.maximum(idx, 0)], np.nan) if len(a) else np.full(len(idx), np.nan)
    return out


def profile(out_root, code_dir, subject, first, last, name, coin=None, t=None, metrics_path=None, epi=None, ctx=None, log=print):
    """print a profile: per group and value its tool, status, how many alarms know it, quartiles and unit; with (coin, t) one alarm's
    values and where each sits among the alarms shown (percentile; descriptive, not known at the alarm). Writes nothing."""
    prof = load_profiles()
    if name not in prof:
        raise ValueError('profile %r: one of %s' % (name, ', '.join(prof)))
    items = prof[name]; meta = {('EPI', c[2]): c for c in columns()}; meta.update({('CTX', c[2]): c for c in ctx_columns()})
    st = proof_status(metrics_path, results=os.environ.get('ALARM_PROFILE_RESULTS') or RESULTS)
    if epi is None:
        epi = read(out_root, code_dir, subject, first, last)
    ctx_subject = subject_info(subject)[1]
    if ctx is None and ctx_subject and any(tool == 'CTX' for _, tool, _, _ in items):
        sys.path.insert(0, CTX_DIR)
        import alarm_context as AC
        want = [v for _, tool, v, _ in items if tool == 'CTX']
        ctx = AC.read(out_root, code_dir, ctx_subject, first, last, values=want)
    cj = _join(epi, ctx)
    n = len(epi['coin']); row = None
    if coin is not None:
        hit = [i for i in range(n) if epi['coin'][i] == coin and abs(epi['t_alarm'][i] - float(t)) < 0.5]
        if not hit:
            raise ValueError('alarm %s %s not among the %d rows read' % (coin, t, n))
        row = hit[0]
    log('PROFILE %s  subject %s  %s..%s  alarms %d%s' % (name, subject, first, last, n, '' if row is None else '  alarm %s %s' % (coin, t)))
    group = None
    for g, tool, v, why in items:
        if g != group:
            group = g; log('[%s]' % g)
        x = epi.get(v) if tool == 'EPI' else cj.get(v)
        unit = meta[(tool, v)][4]; s, d = st.get((tool, v), ('OPEN', 'no status'))
        if x is None:
            log('  %-28s %s %-7s not read' % (v, tool, s)); continue
        f = np.isfinite(x); q = np.percentile(x[f], [25, 50, 75]) if f.any() else [np.nan] * 3
        if row is None:
            log('  %-28s %s %-7s known %5d  q25 %9.4g  q50 %9.4g  q75 %9.4g  [%s]  %s' % (v, tool, s, int(f.sum()), q[0], q[1], q[2], unit, d))
        else:
            xv = x[row]; pc = 100.0 * np.mean(x[f] <= xv) if f.any() and np.isfinite(xv) else np.nan
            log('  %-28s %s %-7s this %9.4g  pct %5.1f  (q50 %9.4g)  [%s]' % (v, tool, s, xv, pc, q[1], unit))
    return epi, cj


def show(out_root, code_dir, subject, first, last, values=None):
    x = read(out_root, code_dir, subject, first, last, values.split(',') if values else None); n = len(x['coin']); print('ROWS %d' % n)
    for k, v in x.items():
        if k in ('coin', 't_alarm', 'known_at_us'):                    # known_at_us: the row clock (D03-01), not a value
            continue
        f = np.isfinite(v); print('%-24s finite %.3f median %s' % (k, f.mean() if n else 0, '%.4g' % np.median(v[f]) if f.any() else 'nan'))


def export(out_root, code_dir, subject, first, last, outp, values=None, alarms=None):
    """edition 2: every alarm's values (default all) as one TSV: coin, t (the alarm, whole seconds), [onset_rule 'list' or 't' when the
    alarm list is given], the values; refuses an existing file"""
    if os.path.exists(outp):
        raise ValueError('EXISTS %s' % outp)
    x = read(out_root, code_dir, subject, first, last, values.split(',') if values else None)
    names = [k for k in x if k not in ('coin', 't_alarm', 'known_at_us')]
    rule = None
    if alarms:
        built = built_list_sha(out_root, subject, os.path.basename(alarms))
        if built != sha16_file(alarms):
            raise ValueError('%s is not the list %s was built from (built %s, given %s): refused' % (alarms, subject, built, sha16_file(alarms)))
        ev = load_alarms(alarms, subject_info(subject)[0], onset_fallback=True)
        rule = {(str(c), int(t)): ('list' if g else 't') for c, t, g in zip(ev['coin'], ev['t'], ev['onset_given'])}
        miss = [k for k in zip((str(c) for c in x['coin']), (int(round(v)) for v in x['t_alarm'])) if k not in rule]
        if miss:
            raise ValueError('%d stored alarms are not in %s (first %s): refused' % (len(miss), alarms, miss[0]))
    with open(outp + '.part', 'x') as f:
        f.write('\t'.join(['coin', 't'] + (['onset_rule'] if rule else []) + names) + '\n')
        for i in range(len(x['coin'])):
            k = (str(x['coin'][i]), int(round(x['t_alarm'][i])))
            f.write('\t'.join([k[0], str(k[1])] + ([rule[k]] if rule else []) +
                              ['' if not np.isfinite(x[n][i]) else repr(float(x[n][i])) for n in names]) + '\n')
    os.replace(outp + '.part', outp)
    print('EXPORT %s rows %d values %d -> %s %s' % (subject, len(x['coin']), len(names), outp, sha16_file(outp)))


def built_list_sha(out_root, subject, name):
    """edition 2.2: the sha16 of the alarm list <name> recorded in the build's sources (the first day of the subject), or None"""
    for d in sorted(n for n in os.listdir(out_root) if n.startswith('day=')):
        ixp = os.path.join(out_root, d, part_name(subject), 'index.json')
        if os.path.exists(ixp):
            with open(ixp) as fh:
                return json.load(fh).get('sources', {}).get('alarms:%s' % name)
    return None


def main(a):
    if a[0] == 'catalog':
        txt = catalog_text(); open(CATALOG + '.tmp', 'w').write(txt); os.replace(CATALOG + '.tmp', CATALOG); print('CATALOG', sha16_file(CATALOG))
    elif a[0] == 'build':
        lab, code_dir, alp, subj, first, last = a[1:7]; out = a[7] if len(a) > 7 else None; mode = a[8] if len(a) > 8 else 'alarm'
        got = build(lab, alp, subj, first, last, out, code_dir=code_dir, run_end_mode=mode)
        print('BUILD %s days %d written %d up to date %d refused %d' % (subj, len(got), sum(v == 'WRITTEN' for v in got.values()),
              sum(v == 'UP TO DATE' for v in got.values()), sum(v == 'REFUSED' for v in got.values())))
    elif a[0] == 'show':
        show(*a[1:7])
    elif a[0] == 'export':
        export(*a[1:9])
    elif a[0] == 'profile':
        out, code_dir, subj, first, last, name = a[1:7]
        profile(out, code_dir, subj, first, last, name, *(a[7:9] if len(a) >= 9 else (None, None)),
                metrics_path=os.environ.get('LAB3_METRICS'))
    elif a[0] == 'profiles':
        for k, v in load_profiles().items():
            print('%-14s %3d values' % (k, len(v)))
        print('PROBLEMS', check_profiles() or 'none')
    elif a[0] == 'status':
        st = proof_status(a[1] if len(a) > 1 else os.environ.get('LAB3_METRICS'), results=os.environ.get('ALARM_PROFILE_RESULTS') or RESULTS)
        for (tool, v), (s, d) in sorted(st.items()):
            print('%s\t%s\t%s\t%s' % (tool, v, s, d))
        print('PROVEN %d OPEN %d FAILED %d' % tuple(sum(1 for x in st.values() if x[0] == k) for k in ('PROVEN', 'OPEN', 'FAILED')))
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
