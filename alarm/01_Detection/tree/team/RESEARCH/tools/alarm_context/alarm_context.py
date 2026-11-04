"""RESEARCH tools/alarm_context (QUANT, 21 Oct 2026; DRAFT, reviewer SCOUT; built to RESEARCH/KNOWLEDGE/TOOL_DESIGN_V1.md).
QUESTION: what was happening around each alarm, at the moment we would decide? Three parts, chosen by a setting: EVENT (the alarm itself),
MARKET (the whole market, BTC first), COIN (the alarm's coin). One tool, one catalog (CTX_CATALOG_V1.tsv, generated from the block
docstrings in context_blocks.py); the reader takes any values of any part. DESCRIBES ONLY: no outcomes in any part.
UNIT: one row = one alarm x one decision time (the setting DECISIONS, minutes after the alarm, default 0 = at the alarm). as_of_us = the
alarm time (which alarm), known_at_us = the decision time; every value is known at known_at (lab values at the last minute end <= it;
alarm-history questions read only alarms strictly before the alarm).
OUTPUT, THE ONE FORMAT: lab3.write.write_part to a research root (default <DATA_ROOT>/research_days; the writer creates it),
part CTX.<SUBJECT>.<LEVEL> (e.g. CTX.A02.MARKET), ROWS kind, codes CTX.<SUBJECT>.<column>. A value not known: no bits, reason NOT_KNOWN.
GENERATED ONCE: each alarm day is built from its own lab days only (EVENT: D-1..last decision day; MARKET and COIN: 30 days before too, for
the 7-day and 30-day questions), the WHOLE alarm list, the tables its level uses; seal (settings) and sources (sha16 of the alarm list,
this code, the catalog, the tables, every lab index read) go into the part's index; a day whose part has the same seal and sources is left
as it is (UP TO DATE). SEALED (from 1 Jan 2026; December 2025 was sealed until the owner opened it 22:06 Berlin 21 Oct): refused when
building and reading; the blocks never see a sealed day:
its lab days look unbuilt to the reader and its minutes are NaN on every timeline, its alarms leave the history, and a decision time that
falls on a sealed day is not written (SCOUT review 17:54Z, MUST 1 and 2). The DAY AFTER a sealed period (1 Jan 2026) is sealed for lab reads
and alarm days too: the lab's own 24 h windows carry the sealed day into it (SCOUT re-review 18:14Z).
  python3 alarm_context.py build <lab_days> <lab3 code dir> <EVENTS tsv> <subject> <level> <first day> <last day> [out root] [decisions min, comma]
                                [history EVENTS tsv: the alarm list, for a subject whose rows are not alarms (A02_MATCH)]
  python3 alarm_context.py show  <out root> <lab3 code dir> <subject> <first day> <last day> [values, comma]   (prints; writes nothing)
  python3 alarm_context.py catalog                                                                           (regenerates the catalog)"""
import csv, datetime as dt, hashlib, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'alarms'))
import context_blocks as CB

TOOL = 'alarm_context'; VERSION = 1
OUT_ROOT = '<DATA_ROOT>/research_days'
CATALOG = os.path.join(HERE, 'CTX_CATALOG_V1.tsv')
TYPES = os.path.join(HERE, 'COIN_TYPES_V1.tsv')
COSTS = os.path.normpath(os.path.join(HERE, '..', '..', 'QUANT', 'receipts', 'COSTS_PER_COIN_V4.tsv'))
SUBJECTS = ('A02', 'A02N', 'A02_MATCH', 'A02N_MATCH', 'DWAVE', 'DWAVE_MATCH', 'EXH', 'EXH_MATCH', 'A01', 'A01_MATCH', 'DHL', 'DHL_MATCH', 'P3V2', 'P3V2_MATCH', 'P6', 'P6_MATCH', 'B6', 'B6_MATCH', 'N6V3', 'N6V3_MATCH', 'A02P_MATCHV3')   # QUANT-162137: the draw V3 moments of the A02P parents; the row lists this catalog names (night 21 Oct: alarm #2 candidates of EDGE_METHOD_V2) (A02_MATCH: matched random moments of the A02
                                                        # alarms, fire_path_v1's draw, read with the ALARMS as history); a new one = + catalog
LEVELS = ('EVENT', 'MARKET', 'COIN')
BEFORE = {'EVENT': 1, 'MARKET': 31, 'COIN': 31}        # lab days read before the alarm day (30 days of history + the day before)
TABLES = {'EVENT': (), 'MARKET': (), 'COIN': ('costs', 'types')}
SEALED = (('20260601', '99991231', 'June 2026 onward: BLIND (the owner 23 Oct 06:01Z: research uses Sep 2025 to May 2026; = lab3/law.py)'),)   # LAB1 23 Oct; was 20260101 on
# December 2025 UNSEALED by the owner (22:06 Berlin 21 Oct: "you can unseal december ... we just use it as OOS for each idea tested on
# september to november"; 23:09: "You can use december data as well"). Out-of-sample discipline: QUANT/NIGHT_PLAN_20261021.md (find on
# Sep-Oct, November checked blind by SCOUT, December only for frozen candidates, every look counted). January 2026 onward sealed here.
# The sealing machinery stays tested: the tests seal December again for themselves (TEST_SEALED in test_alarm_context.py).
CAT_COLS = ('code', 'store', 'clock', 'exact_k', 'scope', 'meaning', 'unit', 'level', 'block')
NOT_KNOWN = 'NOT_KNOWN'
ROWCOLS = ('day', 'as_of_us', 'known_at_us', 'value_kind', 'value_bits', 'value_txt', 'empty_reason', 'stale')
# OX-SKEPTIC P09-01 (historical veto): a current source-use prohibition overrides every stored part this reader serves, old or new. These
# values always read NaN through read() (row keys kept), whatever a stored part holds; the reason is public here. Rebuilding is not needed.
DISABLED = {'wall_%s_log_%s' % (side, width): 'SOURCE_USE_PROHIBITED: lab A6 is WITHDRAWN (its card bars any analysis; OX-DATA P04-01)'
            for side in ('ahead', 'behind') for width in ('1pct', '2pct', '3pct')}


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def sealed(day):
    for lo, hi, why in SEALED:
        if lo <= str(day) <= hi:
            return why
    return None


def sealed_read(day):
    """a day whose LAB values may hold a sealed day: the sealed days themselves and the day after each (the lab codes this tool reads look
    back at most 24 h or the prior day: C1.S14, C4.S05, NAUTILUS 1440-candle bands and channels, D2.S05 / D3.S17 24 h z, C11.S08 prior
    day, C10 legs from 00:00 D-1; SCOUT re-review 18:14Z). Lab values of these days are never read and their alarm days are refused."""
    return sealed(day) or (('the day after a sealed day (%s): the lab\'s 24 h windows reach into it' % shift(str(day), -1))
                           if sealed(shift(str(day), -1)) else None)


def code_name(subject, col):
    return 'CTX.%s.%s' % (subject, col)


def part_name(subject, level):
    return 'CTX.%s.%s' % (subject, level)


def columns(level=None):
    """[(level, block, column, meaning, unit)]; a column name is unique across the levels (it is the code)"""
    cols = CB.doc_columns((level,) if level else LEVELS); names = [c[2] for c in CB.doc_columns(LEVELS)]
    if len(set(names)) != len(names):
        raise ValueError('a column named twice across the levels: %s' % sorted({n for n in names if names.count(n) > 1}))
    return cols


def catalog_text(subjects=SUBJECTS):
    lines = ['# CTX_CATALOG_V1: generated by alarm_context.py catalog from context_blocks.py docstrings; METRICS_V1 columns + meaning, unit, level, block',
             '\t'.join(CAT_COLS)]
    for s in subjects:
        for lv, bl, col, mean, unit in columns():
            lines.append('\t'.join([code_name(s, col), 'ROWS', 'event', '0', 'coin', mean, unit, lv, bl]))
    return '\n'.join(lines) + '\n'


def utc_day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def shift(d, k):
    return (dt.datetime.strptime(d, '%Y%m%d') + dt.timedelta(days=k)).strftime('%Y%m%d')


def load_events(path):
    """every alarm with side != 0: {coin, t, side, S = |S|} as arrays in file order; a (coin, t) twice is refused"""
    with open(path) as f:
        rows = list(csv.DictReader(f, delimiter='\t'))
        if any(not np.isfinite(float(r['side'])) or float(r['side']) not in (-1, 0, 1) for r in rows):
            raise ValueError('event side must be exactly -1, 0 or +1')
        R = [r for r in rows if float(r['side']) != 0]
    ev = dict(coin=np.array([r['coin'] for r in R]), t=np.array([float(r['t']) for r in R]),
              side=np.array([int(float(r['side'])) for r in R]), S=np.abs(np.array([float(r.get('S', '') or 'nan') for r in R])))
    # S is the alarm's SIZE: |S| (SCOUT review 21:49Z: P3V2's Lee-Mykland L and N6V3's minute return are signed; the side is the side column)
    keys = list(zip(ev['coin'].tolist(), np.round(ev['t'] * 1e6).astype(np.int64).tolist()))
    if len(set(keys)) != len(keys):
        raise ValueError('%s: an alarm (coin, t) listed twice: refused' % path)
    return ev


def load_tables(costs=COSTS, types=TYPES):
    """{'costs': {(coin, hour or 'ALL'): (cost_bp, tier)}, 'types': {coin: major | alt | meme}}"""
    tier = {'cheap': 1.0, 'middle': 2.0, 'thin': 3.0}; out = {'costs': {}, 'types': {}}
    with open(costs) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            h = r['hour_utc']; out['costs'][(r['coin'], int(h) if h.isdigit() else h)] = (float(r['cost_bp'] or 'nan'), tier.get(r['group'], np.nan))
    with open(types) as f:
        for r in csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'):
            out['types'][r['coin']] = r['class']
    return out


def settings(subject, level, decisions, lab_root):
    return json.dumps({'tool': TOOL, 'version': VERSION, 'subject': subject, 'level': level, 'decisions_min': list(decisions),
                       'lab_root': lab_root, 'lab_days_before': BEFORE[level], 'tables': list(TABLES[level]),
                       'known_at': 'decision time', 'history': "whole alarm list, t' < alarm"}, sort_keys=True)


class LabSrc:
    """what the blocks read, from lab3 through alarm_view_v1.View (one Days reader, recording every lab index it reads)"""
    def __init__(self, V, R, LB, lab_root, code_dir, first, last, coins, before):
        mk = lambda cs, b: V.View(lab_root, code_dir, first, last, cs, before=b, R=R, LB=LB)
        self._short = mk(coins, 1); self.t = self._short.t; self.skipped = self._short.skipped
        self._mk = mk; self._coins = coins; self._before = before; self._v = {}

    def _view(self, key, cs, b):
        if key not in self._v:
            self._v[key] = self._mk(cs, b)
            if self._v[key] is not self._short:
                self._v[key].skipped = self.skipped                  # one list of what could not be read
        return self._v[key]

    def code(self, name):
        return self._short.code(name)

    def prices(self):
        return self._short.prices()

    def market(self, name):
        return self._view('MARKET', ['MARKET'], 1).code(name)[0]

    def btc(self, name):
        return self._view('BTC', ['BTC'], 1).code(name)[0]

    @property
    def long_t(self):
        return self._view('LONG', self._coins, self._before).t

    def long(self, name):
        return self._view('LONG', self._coins, self._before).code(name)

    def long_btc(self, name):
        return self._view('LONG_BTC', ['BTC'], self._before).code(name)[0]


def lab_view(lab_root, code_dir):
    """-> make(first, last, coins, before) -> (src, used); used = {'lab:day=<D>/<part>': sha16 of its index.json} of every lab part read"""
    sys.path.insert(0, code_dir)
    from lab3 import days as LD, bins as LB
    import alarm_view_v1 as V

    shas = {}

    def sha(root, d, part):
        k = (str(d), part)
        if k not in shas:
            shas[k] = LD.sha16_file(os.path.join(root, 'day=%s' % d, part, 'index.json'))
        return shas[k]

    class Rec(LD.Days):                                              # one reader for the whole run: its index cache is shared
        used = {}

        def days(self):                                              # a sealed day looks unbuilt: View never reads it, never carries from it
            return [d for d in super().days() if not sealed_read(d)]

        def block(self, d, part, code, field):
            self.used['lab:day=%s/%s' % (d, part)] = sha(self.root, d, part)
            return super().block(d, part, code, field)

    class RecBins:
        def read_bins(self, R, d, cs):
            out = LB.read_bins(R, d, cs)
            R.used['lab:day=%s/%s' % (d, LB.PART)] = sha(R.root, d, LB.PART)
            return out
    R = Rec(lab_root, 'research'); B = RecBins()

    def make(first, last, coins, before):
        R.used = {}                                                    # this day's lab parts, from scratch
        return LabSrc(V, R, B, lab_root, code_dir, first, last, coins, before), R.used
    return make


def expand(ev, decisions):
    """one row per alarm x decision: t = the decision time, t_alarm = the alarm"""
    k = len(decisions); out = {key: np.repeat(v, k) for key, v in ev.items()}
    out['t_alarm'] = out['t'].copy(); out['t'] = out['t'] + np.tile(np.array(decisions, float) * 60.0, len(ev['t'])); return out


def day_rows(day, e, cols, subject):
    """{code: {'step': 'event', 'kind': 'NUMBER', 'rows': {coin: ROWS}}} of one day; rows by coin in (alarm, decision) order"""
    coins = sorted(set(e['coin'].tolist())); out = {}
    a_us = np.round(e['t_alarm'] * 1e6).astype(np.int64); k_us = np.round(e['t'] * 1e6).astype(np.int64)
    order = {coin: [i for i in np.lexsort((k_us, a_us)).tolist() if e['coin'][i] == coin] for coin in coins}
    for col, x in cols.items():
        rows = {}
        for coin in coins:
            r = {k: [] for k in ROWCOLS}
            for i in order[coin]:
                v = float(x[i]); ok = np.isfinite(v)
                r['day'].append(int(day)); r['as_of_us'].append(int(a_us[i])); r['known_at_us'].append(int(k_us[i])); r['value_kind'].append(1)
                r['value_bits'].append(int(np.array([v], '<f8').view('<u8')[0]) if ok else None)
                r['value_txt'].append(None); r['empty_reason'].append('' if ok else NOT_KNOWN); r['stale'].append(0)
            rows[coin] = r
        out[code_name(subject, col)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rows}
    return coins, out


def build(lab_root, events_path, subject, level, first, last, out_root=OUT_ROOT, decisions=(0,), make_view=None, code_dir=None,
          write=None, load_catalog=None, costs=COSTS, types=TYPES, log=print, hist_path=None):
    """build every alarm day first..last of one level; -> {day: 'WRITTEN' | 'UP TO DATE' | 'REFUSED'}"""
    if subject not in SUBJECTS:
        raise ValueError('subject %r is not in the catalog (%s)' % (subject, ', '.join(SUBJECTS)))
    if level not in LEVELS:
        raise ValueError('level %r: one of %s' % (level, ', '.join(LEVELS)))
    decisions = tuple(sorted(set(float(d) for d in decisions)))
    if not decisions or min(decisions) < 0:
        raise ValueError('decisions %r: minutes at or after the alarm' % (decisions,))
    if write is None or load_catalog is None:
        sys.path.insert(0, code_dir)
        from lab3 import write as LW
        write = write or LW.write_part; load_catalog = load_catalog or LW.load_catalog
    if open(CATALOG).read() != catalog_text():
        raise ValueError('CTX_CATALOG_V1.tsv differs from the blocks: run "alarm_context.py catalog" first')
    make_view = make_view or lab_view(lab_root, code_dir)
    cat = load_catalog(CATALOG); seal = settings(subject, level, decisions, lab_root)
    ev = load_events(events_path)
    he = ev if hist_path is None else load_events(hist_path)           # the alarm history: the rows themselves, or (matched moments) the alarms
    keep = np.array([not sealed(utc_day(t)) for t in he['t']], bool)
    hist = {k: he[k][keep] for k in ('coin', 't', 'S')}                # a sealed day's alarms are never anyone's history
    fixed = {'events:%s' % os.path.basename(events_path): sha16_file(events_path)}
    if hist_path is not None:
        fixed['history:%s' % os.path.basename(hist_path)] = sha16_file(hist_path)
    for f in ('alarm_context.py', 'context_blocks.py', 'CTX_CATALOG_V1.tsv', os.path.join('..', 'alarms', 'alarm_view_v1.py')):
        fixed['code:%s' % os.path.basename(f)] = sha16_file(os.path.join(HERE, f))
    tables = None
    if TABLES[level]:
        tables = load_tables(costs, types)
        for nm, p in (('costs', costs), ('types', types)):
            if nm in TABLES[level]:
                fixed['table:%s' % os.path.basename(p)] = sha16_file(p)
    days = np.array([utc_day(t) for t in ev['t']]); done = {}; part = part_name(subject, level)
    for day in sorted(set(d for d in days.tolist() if first <= d <= last)):
        if sealed_read(day):
            done[day] = 'REFUSED'; log('DAY %s %s REFUSED: %s' % (day, part, sealed_read(day))); continue
        sel = days == day; e = expand({k: v[sel] for k, v in ev.items()}, decisions)
        ok = np.array([not sealed_read(utc_day(t)) for t in e['t']], bool)
        if not ok.all():
            log('DAY %s %s: %d decision rows fall on a sealed day: not written' % (day, part_name(subject, level), int((~ok).sum())))
            e = {k: v[ok] for k, v in e.items()}
            if not len(e['t']):
                done[day] = 'REFUSED'; continue
        coins = sorted(set(e['coin'].tolist())); last_day = utc_day(e['t'].max())
        src, used = make_view(day, last_day, coins, BEFORE[level])
        ctx = CB.Ctx(e, src, coins, src.t, hist=hist, tables=tables, sealed=sealed_read); cols = CB.run(ctx, (level,))
        sources = dict(fixed); sources.update(used)
        ixp = os.path.join(out_root, 'day=%s' % day, part, 'index.json')
        if os.path.exists(ixp):
            old = json.load(open(ixp))
            if old.get('seal') == seal and old.get('sources') == sources:
                done[day] = 'UP TO DATE'; log('DAY %s %s rows %d UP TO DATE' % (day, part, ctx.n)); continue
        cs, codes = day_rows(day, e, cols, subject)
        write(out_root, int(day), part, codes, cs, catalog=cat, sources=sources, seal=seal)
        fin = np.mean([np.isfinite(v).mean() for v in cols.values()]) if cols else 0.0
        done[day] = 'WRITTEN'
        log('DAY %s %s rows %d coins %d codes %d finite %.3f lab parts read %d skipped %d WRITTEN' % (
            day, part, ctx.n, len(cs), len(codes), fin, len(used), len(getattr(src, 'skipped', []))))
    return done


def read(out_root, code_dir, subject, first, last, values=None, days_reader=None):
    """-> {'coin', 't_alarm', 't_decision', <value>...}: the chosen values (any part; default all of the built parts) of every row
    first..last, read back through lab3.days (purpose research), joined on (coin, alarm, decision); a row a part lacks reads NaN"""
    if days_reader is None:
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        days_reader = LD.Days(out_root, 'research')
    lvl = {c[2]: c[0] for c in columns()}
    values = list(values) if values else [c[2] for c in columns()]
    bad = [v for v in values if v not in lvl]
    if bad:
        raise ValueError('values not in the catalog: %s' % bad)
    keys = {}; vals = {v: {} for v in values}
    for day in days_reader.days():
        if not first <= day <= last:
            continue
        if sealed(day):
            raise PermissionError('%s: %s: refused' % (day, sealed(day)))
        for v in values:
            part = part_name(subject, lvl[v])
            if part not in days_reader.parts(day):
                continue
            coins = days_reader.index(day, part)['coins']; r = days_reader.rows(code_name(subject, v), day, coins)
            for coin in coins:
                for b, a, k in zip(r[coin]['value_bits'], r[coin]['as_of_us'], r[coin]['known_at_us']):
                    key = (coin, a, k)
                    if key in vals[v]:
                        raise ValueError('duplicate context row key: %r' % (key,))
                    keys[key] = True
                    vals[v][key] = np.array([b], '<u8').view('<f8')[0] if b is not None else np.nan
    order = sorted(keys, key=lambda x: (x[1], x[0], x[2]))
    out = {'coin': np.array([k[0] for k in order]), 't_alarm': np.array([k[1] / 1e6 for k in order]), 't_decision': np.array([k[2] / 1e6 for k in order])}
    for v in values:
        out[v] = np.array([vals[v].get(k, np.nan) for k in order], float)
        if v in DISABLED:                                              # P09-01: the veto holds for stored parts built before the ban
            out[v][:] = np.nan
    return out


def show(out_root, code_dir, subject, first, last, values=None):
    x = read(out_root, code_dir, subject, first, last, values.split(',') if values else None); n = len(x['coin']); print('ROWS %d' % n)
    for k, v in x.items():
        if k in ('coin', 't_alarm', 't_decision'):
            continue
        f = np.isfinite(v); print('%-28s finite %.3f median %s' % (k, f.mean() if n else 0, '%.4g' % np.median(v[f]) if f.any() else 'nan'))


def main(a):
    if a[0] == 'catalog':
        txt = catalog_text(); open(CATALOG + '.tmp', 'w').write(txt); os.replace(CATALOG + '.tmp', CATALOG); print('CATALOG', sha16_file(CATALOG))
    elif a[0] == 'build':
        lab, code_dir, evp, subj, level, first, last = a[1:8]; out = a[8] if len(a) > 8 else OUT_ROOT
        dec = tuple(float(x) for x in a[9].split(',')) if len(a) > 9 else (0,)
        got = build(lab, evp, subj, level, first, last, out, dec, code_dir=code_dir, hist_path=a[10] if len(a) > 10 else None)
        print('BUILD %s days %d written %d up to date %d refused %d' % (level, len(got), sum(v == 'WRITTEN' for v in got.values()),
              sum(v == 'UP TO DATE' for v in got.values()), sum(v == 'REFUSED' for v in got.values())))
    elif a[0] == 'show':
        show(*a[1:7])
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
