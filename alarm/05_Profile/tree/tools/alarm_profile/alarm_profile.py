"""RESEARCH tools/alarm_profile (QUANT, 22 Oct 2026; reviewer SCOUT; built to the research-tool-design skill).
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
OUT_ROOT = '<DATA_ROOT>/research_days'
CATALOG = os.path.join(HERE, 'EPI_CATALOG_V1.tsv')
PROFILES = os.path.join(HERE, 'PROFILES_V1.tsv')
PROOFS = os.path.join(HERE, 'PROOFS_V1.tsv')
RESULTS = os.path.join(HERE, 'PROOF_RESULTS_V1.tsv')
CTX_INPUTS = os.path.join(HERE, 'CTX_INPUTS_V1.tsv')
CTX_DIR = os.path.normpath(os.path.join(HERE, '..', 'alarm_context'))
SUBJECTS = {'A02': ('D0', 'A02'), 'A02_1': ('D1', None), 'A02N': ('N0', None)}   # subject -> (candidate in the alarm list, the CTX subject or None); A02N: no growth (ALARM_DEFINITION_V4, the owner 18:12 Berlin 22 Oct)
SEALED = (('20260601', '99991231', 'June 2026 onward: BLIND (the owner 23 Oct 06:01Z: research uses Sep 2025 to May 2026; = lab3/law.py)'),)   # LAB1 23 Oct; was 20260101 on
DAYS_ROWS, DAYS_PRICE, DAYS_TOTALS = 1, 2, 8                         # lab days read before the alarm day: 5 s rows and OI, prices, daily totals
CODES = {'long': 'A1.S01', 'short': 'A1.S02', 'oi': 'E2.S02', 'oi_carried': 'E2.S03'}
HL_ROOT = '<SCRATCH>/work_SCOUT/hl_fills_npz_dev'
HL_DIRS = tuple(os.path.join(HL_ROOT, d) for d in ('01', '02', '03', 'd3_01', 'd3_02', 'd3_03', 'd3_04', 'd3_05'))   # SCOUT's hl_fills_v1, 12 Sep - 26 Oct 2025
HL_NAME = {'PEPE': 'kPEPE', 'BONK': 'kBONK', 'SHIB': 'kSHIB'}       # the lab's 1000-coin contracts are Hyperliquid's k-coins (same price scale)
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')
NOT_KNOWN = 'NOT_KNOWN'
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')
CODE_FILES = ('alarm_profile.py', 'episode_blocks.py', 'EPI_CATALOG_V1.tsv', os.path.join('..', 'alarms', 'a01_onset_v2.py'),
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


def load_alarms(path, candidate=None):
    """the alarms (coin, t, side, onset_t) of one candidate (when the list has a 'candidate' column); a (coin, t) twice is refused"""
    with open(path) as f:
        R = [r for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t')]
    if candidate is not None and R and 'candidate' in R[0]:
        R = [r for r in R if r['candidate'] == candidate]
    R = [r for r in R if int(float(r['side'])) != 0]
    ev = dict(coin=np.array([r['coin'] for r in R]), t=np.array([int(float(r['t'])) for r in R], np.int64),
              side=np.array([int(float(r['side'])) for r in R], int), onset_t=np.array([int(float(r['onset_t'])) for r in R], np.int64))
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


def chunk_eps(src, day, ev, idx, coins, used):
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
        yield EB.Ep(coin, t, t0, side, T5, A[fz][k], A[ot][k], te, px, daily, oi_t, O['oi'][k], O['oi_carried'][k], hl=HLC[coin])


def day_values(src, day, ev):
    """{column: (n,) float} of the day's alarms (ev), coins read CHUNK at a time, each alarm's Ep used and dropped -> (cols, sources)"""
    names = [c[2] for c in columns()]; n = len(ev['t']); cols = {k: np.full(n, np.nan) for k in names}; used = {}
    coins = sorted(set(ev['coin'].tolist()))
    for c0 in range(0, len(coins), CHUNK):
        part = coins[c0:c0 + CHUNK]; sel = set(part)
        idx = [i for i in np.argsort(np.asarray(ev['coin']), kind='stable').tolist() if ev['coin'][i] in sel]
        for i, e in zip(idx, chunk_eps(src, day, ev, idx, part, used)):
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


def build(lab_root, alarms_path, subject, first, last, out_root=OUT_ROOT, code_dir=None, src=None, write=None, load_catalog=None,
          log=print, table=None):
    """build every alarm day first..last of the subject -> {day: 'WRITTEN' | 'UP TO DATE' | 'REFUSED'}"""
    if subject not in SUBJECTS:
        raise ValueError('subject %r is not in the catalog (%s)' % (subject, ', '.join(SUBJECTS)))
    if write is None or load_catalog is None:
        sys.path.insert(0, code_dir)
        from lab3 import write as LW
        write = write or LW.write_part; load_catalog = load_catalog or LW.load_catalog
    if open(CATALOG).read() != catalog_text():
        raise ValueError('EPI_CATALOG_V1.tsv differs from the blocks: run "alarm_profile.py catalog" first')
    cand = SUBJECTS[subject][0]; ev = load_alarms(alarms_path, cand)
    src = src or LabSource(lab_root, code_dir, table=table)
    cat = load_catalog(CATALOG); seal = settings(subject, cand, lab_root, getattr(src, 'hl_dirs', HL_DIRS))
    fixed = {'alarms:%s' % os.path.basename(alarms_path): sha16_file(alarms_path)}
    for f in CODE_FILES:
        fixed['code:%s' % os.path.basename(f)] = sha16_file(os.path.join(HERE, f))
    days = np.array([utc_day(t) for t in ev['t']]); done = {}; part = part_name(subject)
    for day in sorted(set(d for d in days.tolist() if first <= d <= last)):
        if sealed_read(day, table):
            done[day] = 'REFUSED'; log('DAY %s %s REFUSED: %s' % (day, part, sealed_read(day, table))); continue
        sel = days == day; e = {k: v[sel] for k, v in ev.items()}
        n_skip = len(src.skipped); cols, used = day_values(src, day, e)
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
    ctx_subject = SUBJECTS[subject][1]
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


def main(a):
    if a[0] == 'catalog':
        txt = catalog_text(); open(CATALOG + '.tmp', 'w').write(txt); os.replace(CATALOG + '.tmp', CATALOG); print('CATALOG', sha16_file(CATALOG))
    elif a[0] == 'build':
        lab, code_dir, alp, subj, first, last = a[1:7]; out = a[7] if len(a) > 7 else OUT_ROOT
        got = build(lab, alp, subj, first, last, out, code_dir=code_dir)
        print('BUILD %s days %d written %d up to date %d refused %d' % (subj, len(got), sum(v == 'WRITTEN' for v in got.values()),
              sum(v == 'UP TO DATE' for v in got.values()), sum(v == 'REFUSED' for v in got.values())))
    elif a[0] == 'show':
        show(*a[1:7])
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
