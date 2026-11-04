"""alarm_stamp_ed1_1.py: edition 1 of alarm_stamp on alarm_context_ed1_1, the out root from the caller. Owner QUANT. New edition by SCOUT for the clean release (K6, 31 Oct 2026; the owner 30 Oct 2026 23:07 Berlin: "All alarm tools should work from the
release folder only").
Old file: alarm_stamp.py 5dfc98dd92bbecf4, never edited. Changed, only where things are: it imports alarm_context_ed1_1 (alarm_context
edition 1.1, ab5d915138cb1f01: no machine default), never alarm_context.py; no machine default for the out root (alarm_stamp.py took
alarm_context's /Users path): build() and the build command refuse without one (OUT_ROOT_REQUIRED; the settings key RESEARCH_STORE);
the code identity in a part's sources names this file and alarm_context_ed1_1.py. Every field, value, seal and catalog line is
alarm_stamp.py's; TOOL and VERSION are unchanged. The catalog is STAMP_CATALOG_V1_1.tsv: STAMP_CATALOG_V1.tsv with only its first line,
a comment no reader parses (lab3.write.load_catalog skips '#' lines), naming this edition as its generator: the same codes, and no current
file names the past edition. Commands: python3 alarm_stamp_ed1_1.py with alarm_stamp.py's arguments, the out root
required. The rest of this text is alarm_stamp.py's.
RESEARCH tools/alarm_stamp (QUANT, 21 Oct 2026; DRAFT, reviewer SCOUT; built to RESEARCH/KNOWLEDGE/TOOL_DESIGN_V2.md).
QUESTION: after each alarm, entered at a decision time, how much HEAT came before each OFFER? (the owner 18:50 Berlin: "classify every
trade by how much heat they get before ... 0.2, 0.3 ... 2%", "stamp each alarm by what they give over 15m to 4h"). An OUTCOME tool: it
holds no context; tools/alarm_context holds the context; the two meet only when read together, on (coin, alarm, decision).
UNIT: one row = one alarm x one decision time (setting DECISIONS, minutes after the alarm) x one direction (part setting: FADE = against the
alarm's push, FOLLOW = with it). The entry and the path are SCOUT's heat_offer_v2.entry_row unchanged (BED fill_v2 taker fill after the
execution delay; BED ladder_v6 first touches of 25 levels 0.1 .. 2.5 pct within the hold; a bin that crosses both counts HEAT FIRST).
STORED (the raw measurement, once): filled, fill_wait_s, move_wait_pct, known_s, fill_px (how many seconds of the path after the fill are known: the
hold, or less when the prices stop at a sealed or unbuilt day), ot_01 .. ot_25 / ht_01 .. ht_25 = seconds from the fill to the first touch
of offer / heat 0.1 .. 2.5 pct (empty NOT_REACHED = not within the known path; empty with the fill status when not filled).
STAMPS (derived on read, any offers and horizons, stamps()): hb = the heat before offer o within H minutes = the largest heat level first
touched at or before the offer's first touch (0 = no heat at 0.1 first); reach = the offer came within H; both NaN when the path is not
known that far (known_s < H) and the offer had not come.
KEYS: as_of_us = the alarm; known_at_us = decision + delay + 60 s (the fill's longest wait) + hold: the moment the whole outcome is known,
so no as-of reader can take it for context. read() gives t_alarm and t_decision back (t_decision = known_at - that offset, from the seal).
OUTPUT, THE ONE FORMAT: lab3.write.write_part to the research root, part STAMP.<SUBJECT>.<FADE|FOLLOW>, ROWS kind, codes
STAMP.<SUBJECT>.<FADE|FOLLOW>.<name> in STAMP_CATALOG_V1.tsv. GENERATED ONCE (seal = settings; sources = the alarm list, this code, SCOUT's and BED's
code, every lab bins index read). SEALED days (alarm_context.SEALED: December 2025, from 10 Mar 2026): never read (no prices from them, a
path stops before them), alarm days and decision times on them not written.
  python3 alarm_stamp.py build <lab_days> <lab3 code> <bed e_fill> <bed e_ladder> <EVENTS tsv> A02 <FADE|FOLLOW> <first> <last> [out root] [decisions min]
  python3 alarm_stamp.py show  <out root> <lab3 code> A02 <FADE|FOLLOW> <first> <last>          (prints the stamp table; writes nothing)
  python3 alarm_stamp.py catalog"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(TOOLS, 'alarm_context')); sys.path.insert(0, os.path.join(TOOLS, 'entry_card'))
import alarm_context_ed1_1 as AC                                                  # sealed days, events, day helpers: one definition
import heat_offer_v2 as HO                                                       # SCOUT's entry and ladder step, unchanged

TOOL = 'alarm_stamp'; VERSION = 1
OUT_ROOT = None                                                                  # no machine default: the caller gives it (the settings key RESEARCH_STORE)
CATALOG = os.path.join(HERE, 'STAMP_CATALOG_V1_1.tsv')                          # STAMP_CATALOG_V1's codes; line 1 names this edition
SUBJECTS = ('A02', 'A02_MATCH', 'A02N', 'A02N_MATCH', 'DWAVE', 'DWAVE_MATCH', 'EXH', 'EXH_MATCH', 'A01', 'A01_MATCH', 'DHL', 'DHL_MATCH', 'P3V2', 'P3V2_MATCH', 'P6', 'P6_MATCH', 'B6', 'B6_MATCH', 'N6V3', 'N6V3_MATCH', 'A02P_MATCHV3', 'A02N_MATCHV3', 'A01_MATCHV3')                                                 # A02_MATCH: the matched random moments
DIRECTIONS = ('FADE', 'FOLLOW')
LEVELS = list(HO.LEVELS)                                                         # 0.1 .. 2.5 pct, 25
DELAY_S = 6.0                                                                    # the execution delay (the owner 13:57)
HOLD_S = 14400                                                                   # 4 h: the longest horizon of the stamps
MAX_WAIT_S = 60                                                                  # BED fill_v2's max wait for a fill
OFFERS = [round(0.1 * i, 1) for i in range(2, 21)]                               # 0.2 .. 2.0, the owner's list
HORIZONS = (15, 30, 60, 120, 240)                                                # minutes
NOT_REACHED = 'NOT_REACHED'
FIELDS = [('filled', '1 = the entry filled (BED fill_v2 taker), 0 = not (the reason says why: STALE, NO_FILL, GAP, NO_DATA, NO_PRICES)', 'flag'),
          ('fill_wait_s', 'seconds from the decision + execution delay to the fill', 's'),
          ('move_wait_pct', 'the move in the entry side from the alarm to the decision (last close at or before each)', 'pct'),
          ('known_s', 'seconds of the path after the fill that are known (the hold, or less when prices stop at a sealed or unbuilt day)', 's'),
          ('fill_px', 'the fill price (BED fill_v2: the first close after decision + delay + 3 s); the fill time = decision + 6 s + fill_wait_s', 'price')] + \
         [('ot_%02d' % round(L * 10), 'seconds from the fill to the first touch of OFFER +%.1f pct (empty NOT_REACHED: not within the known path)' % L, 's')
          for L in LEVELS] + \
         [('ht_%02d' % round(L * 10), 'seconds from the fill to the first touch of HEAT -%.1f pct (empty NOT_REACHED: not within the known path)' % L, 's')
          for L in LEVELS]
NAMES = [f[0] for f in FIELDS]


def code_name(subject, direction, name):
    """one code per subject x direction x value: lab3's reader refuses a code that two parts of one day hold (J36476: FADE and FOLLOW
    shared names and every read was refused as Duplicate)"""
    return 'STAMP.%s.%s.%s' % (subject, direction, name)


def part_name(subject, direction):
    return 'STAMP.%s.%s' % (subject, direction)


def catalog_text(subjects=SUBJECTS):
    lines = ['# STAMP_CATALOG_V1_1: the codes of STAMP_CATALOG_V1, generated by alarm_stamp_ed1_1.py catalog; METRICS_V1 columns + meaning, unit, level, block',
             '\t'.join(AC.CAT_COLS)]
    for s in subjects:
        for d in DIRECTIONS:
            for nm, mean, unit in FIELDS:
                lines.append('\t'.join([code_name(s, d, nm), 'ROWS', 'event', '0', 'coin', '%s: %s' % (d, mean), unit, 'OUTCOME', 'heat_offer']))
    return '\n'.join(lines) + '\n'


def offset_s(delay=DELAY_S, hold=HOLD_S):
    """known_at - decision, seconds"""
    if not np.isfinite(delay) or not np.isfinite(hold) or delay < 0 or hold <= 0:
        raise ValueError('delay must be nonnegative and hold positive and finite')
    return delay + MAX_WAIT_S + hold


def settings(subject, direction, decisions, lab_root, delay, hold):
    return json.dumps({'tool': TOOL, 'version': VERSION, 'subject': subject, 'direction': direction, 'decisions_min': list(decisions),
                       'execution_delay_s': delay, 'hold_s': hold, 'known_at_offset_s': offset_s(delay, hold), 'lab_root': lab_root,
                       'entry': 'heat_offer_v2.entry_row (BED fill_v2 taker, ladder_v6)', 'levels_pct': LEVELS}, sort_keys=True)


def known_end_us(loaded, t_from_us):
    """the end of the contiguous run of loaded days that holds t_from: 00:00 of the first day after it that is not loaded (sealed or
    unbuilt); None if every day to the end of `loaded` is loaded (the caller loads enough days)"""
    d = AC.utc_day(t_from_us / 1e6)
    while d in loaded:
        d = AC.shift(d, 1)
    return int(AC.dt.datetime.strptime(d, '%Y%m%d').replace(tzinfo=AC.dt.timezone.utc).timestamp()) * 1_000_000


def one_entry(pv, FV, LD, loaded, t_alarm, side, direction, wait_s, delay, hold):
    """-> {name: (value or None, reason)} of one alarm x decision x direction"""
    r = HO.entry_row(pv, FV, LD, t_alarm, side, delay, direction, hold, wait_s)
    out = {'move_wait_pct': (r.get('move_wait_pct'), '')}
    if r['status'] != 'FILLED':
        out['filled'] = (0.0, r['status'])
        for nm in NAMES:
            if nm not in out:
                out[nm] = (None, r['status'])
        return out
    t_dec_us = int(round(float(t_alarm) * 1e6)) + int(round(wait_s * 1e6)) + int(round(delay * 1e6))
    known = min(float(hold), (known_end_us(loaded, r['t_fill']) - r['t_fill']) / 1e6)
    out.update(filled=(1.0, ''), fill_wait_s=((r['t_fill'] - t_dec_us) / 1e6, ''), known_s=(known, ''), fill_px=(float(r['px_fill']), ''))
    for k, L in enumerate(LEVELS):
        for key, nm in (('o', 'ot_%02d'), ('h', 'ht_%02d')):
            s = r[key][k]
            out[nm % round(L * 10)] = (float(s), '') if 0 <= s <= known else (None, NOT_REACHED)
    return out


def stamps(x, offers=OFFERS, horizons=HORIZONS):
    """x = read() output -> {'reach_<o>_<H>m': 1/0/NaN, 'hb_<o>_<H>m': heat before the offer or NaN, 'hw_<H>m': the largest heat within H or
    NaN}; NaN = not filled, or the path not known to H and the answer not yet decided"""
    n = len(x['coin']); out = {}; known = x['known_s']; filled = x['filled'] == 1
    for nm in NAMES:
        if nm.startswith(('ot_', 'ht_')):
            a = np.asarray(x[nm])
            if np.any(np.isfinite(a) & ((a < 0) | ~np.isfinite(known) | (a > known))):
                raise ValueError('touch outside the observed path: ' + nm)
    if any(not np.isfinite(o) or not any(np.isclose(o, L, atol=1e-10, rtol=0) for L in LEVELS) for o in offers):
        raise ValueError('offer must be an exact stored ladder level')
    H_t = np.stack([x['ht_%02d' % round(L * 10)] for L in LEVELS], 1)            # (n, 25) seconds or NaN
    for H in horizons:
        lim = H * 60.0; full = filled & (known >= lim)
        within = np.where(np.isfinite(H_t), H_t <= lim, False)
        hw = np.where(within.any(1), np.array(LEVELS)[np.argmax(np.where(within, np.arange(25), -1), 1)], 0.0)
        out['hw_%dm' % H] = np.where(full, hw, np.nan)
        for o in offers:
            to = x['ot_%02d' % round(o * 10)]; got = np.isfinite(to) & (to <= lim) & filled
            reach = np.where(got, 1.0, np.where(full, 0.0, np.nan))
            before = np.where(np.isfinite(H_t), H_t <= np.where(np.isfinite(to), to, -1.0)[:, None], False)
            hb = np.where(before.any(1), np.array(LEVELS)[np.argmax(np.where(before, np.arange(25), -1), 1)], 0.0)
            out['reach_%g_%dm' % (o, H)] = reach; out['hb_%g_%dm' % (o, H)] = np.where(got, hb, np.nan)
    return out


def lab_prices(lab_root, code_dir, efill):
    """-> load(coin, days) -> (PriceView, loaded days, used {'lab:day=<D>/<bins part>': sha16}); sealed days are never read"""
    sys.path.insert(0, code_dir); sys.path.insert(0, efill)
    from lab3 import days as LD, bins as LB
    import fill_v2 as FV
    R = LD.Days(lab_root, 'research'); have = {d for d in R.days() if not AC.sealed(d)}; shas = {}

    def load(coin, days):
        parts = {k: [] for k in ('te', 'tl', 'px', 'hi', 'lo')}; loaded = set(); used = {}
        for d in days:
            if d not in have:
                continue
            off, arr = LB.read_bins(R, d, [coin]); loaded.add(d)
            if d not in shas:
                shas[d] = LD.sha16_file(os.path.join(lab_root, 'day=%s' % d, LB.PART, 'index.json'))
            used['lab:day=%s/%s' % (d, LB.PART)] = shas[d]
            for k in parts:
                parts[k].append(arr[k][off[0]:off[1]])
        if not parts['tl']:
            return FV.PriceView.empty(coin), loaded, used
        return FV.PriceView(coin, *[np.concatenate(parts[k]) for k in ('te', 'tl', 'px', 'hi', 'lo')]), loaded, used
    return load


def day_rows(day, rows, subject, direction, delay, hold):
    """rows: [(coin, t_alarm, t_decision, {name: (value, reason)})] -> codes for write_part"""
    coins = sorted({r[0] for r in rows}); off = offset_s(delay, hold); out = {}
    key = lambda r: (int(round(r[1] * 1e6)), int(round((r[2] + off) * 1e6)))
    by = {c: sorted([r for r in rows if r[0] == c], key=key) for c in coins}
    for nm in NAMES:
        rr = {}
        for c in coins:
            col = {k: [] for k in AC.ROWCOLS}
            for r in by[c]:
                a, k = key(r); v, why = r[3][nm]; ok = v is not None and np.isfinite(v)
                col['day'].append(int(day)); col['as_of_us'].append(a); col['known_at_us'].append(k); col['value_kind'].append(1)
                col['value_bits'].append(int(np.array([v], '<f8').view('<u8')[0]) if ok else None); col['value_txt'].append(None)
                col['empty_reason'].append('' if ok else (why or AC.NOT_KNOWN)); col['stale'].append(0)
            rr[c] = col
        out[code_name(subject, direction, nm)] = {'step': 'event', 'kind': 'NUMBER', 'rows': rr}
    return coins, out


def build(lab_root, code_dir, efill, eladder, events_path, subject, direction, first, last, out_root=OUT_ROOT, decisions=(0,), delay=DELAY_S,
          hold=HOLD_S, load=None, FV=None, LD=None, write=None, load_catalog=None, log=print):
    """-> {day: 'WRITTEN' | 'UP TO DATE' | 'REFUSED'}"""
    if not out_root:
        raise ValueError('OUT_ROOT_REQUIRED: give the research root (the settings key RESEARCH_STORE); no machine default')
    if subject not in SUBJECTS or direction not in DIRECTIONS:
        raise ValueError('subject %r / direction %r' % (subject, direction))
    decisions = tuple(sorted(set(float(d) for d in decisions)))
    if not decisions or min(decisions) < 0:
        raise ValueError('decisions %r: minutes at or after the alarm' % (decisions,))
    if open(CATALOG).read() != catalog_text():
        raise ValueError('STAMP_CATALOG_V1_1.tsv differs from the code: run "alarm_stamp_ed1_1.py catalog" first')
    if FV is None or LD is None:
        sys.path.insert(0, efill); sys.path.insert(0, eladder)
        import fill_v2 as FV
        import ladder_v6 as LD
    if write is None or load_catalog is None:
        sys.path.insert(0, code_dir)
        from lab3 import write as LW
        write = write or LW.write_part; load_catalog = load_catalog or LW.load_catalog
    load = load or lab_prices(lab_root, code_dir, efill)
    cat = load_catalog(CATALOG); seal = settings(subject, direction, decisions, lab_root, delay, hold)
    fixed = {'events:%s' % os.path.basename(events_path): AC.sha16_file(events_path)}
    for p in (os.path.join(HERE, 'alarm_stamp_ed1_1.py'), CATALOG, os.path.join(TOOLS, 'alarm_context', 'alarm_context_ed1_1.py'),
              os.path.join(TOOLS, 'entry_card', 'heat_offer_v2.py'), FV.__file__, LD.__file__):
        fixed['code:%s' % os.path.basename(p)] = AC.sha16_file(p)
    if hasattr(LD, '__file__') and os.path.exists(os.path.join(os.path.dirname(LD.__file__), 'ladder_v2.py')):
        fixed['code:ladder_v2.py'] = AC.sha16_file(os.path.join(os.path.dirname(LD.__file__), 'ladder_v2.py'))
    ev = AC.load_events(events_path); days = np.array([AC.utc_day(t) for t in ev['t']]); done = {}; part = part_name(subject, direction)
    for day in sorted(set(d for d in days.tolist() if first <= d <= last)):
        if AC.sealed_read(day):                                         # as alarm_context: 1 Jan too, so every stamp row has its context row
            done[day] = 'REFUSED'; log('DAY %s %s REFUSED: %s' % (day, part, AC.sealed_read(day))); continue
        sel = np.where(days == day)[0]; rows = []; sources = dict(fixed); dropped = 0
        for coin in sorted(set(ev['coin'][sel].tolist())):
            idx = [i for i in sel.tolist() if ev['coin'][i] == coin]
            t_hi = max(ev['t'][i] for i in idx) + 60 * max(decisions) + delay + MAX_WAIT_S + hold + 600
            need = []; d = AC.shift(day, -1)
            while d <= AC.utc_day(t_hi):
                if not AC.sealed(d):                                     # a sealed day's prices are never asked for
                    need.append(d)
                d = AC.shift(d, 1)
            pv, loaded, used = load(coin, need); sources.update(used)
            for i in idx:
                for w in decisions:
                    td = float(ev['t'][i]) + 60.0 * w
                    if AC.sealed(AC.utc_day(td)):
                        dropped += 1; continue
                    rows.append((coin, float(ev['t'][i]), td, one_entry(pv, FV, LD, loaded, float(ev['t'][i]), int(ev['side'][i]), direction, 60.0 * w, delay, hold)))
        if dropped:
            log('DAY %s %s: %d decision rows fall on a sealed day: not written' % (day, part, dropped))
        if not rows:
            done[day] = 'REFUSED'; continue
        ixp = os.path.join(out_root, 'day=%s' % day, part, 'index.json')
        if os.path.exists(ixp):
            old = json.load(open(ixp))
            if old.get('seal') == seal and old.get('sources') == sources:
                done[day] = 'UP TO DATE'; log('DAY %s %s rows %d UP TO DATE' % (day, part, len(rows))); continue
        cs, codes = day_rows(day, rows, subject, direction, delay, hold)
        write(out_root, int(day), part, codes, cs, catalog=cat, sources=sources, seal=seal)
        nf = sum(1 for r in rows if r[3]['filled'][0] == 1.0); done[day] = 'WRITTEN'
        log('DAY %s %s rows %d filled %d lab parts read %d WRITTEN' % (day, part, len(rows), nf, len(sources) - len(fixed)))
    return done


def read(out_root, code_dir, subject, direction, first, last, days_reader=None):
    """-> {'coin', 't_alarm', 't_decision', <every stored name>} read back through lab3.days (purpose research); sealed days refused"""
    if days_reader is None:
        sys.path.insert(0, code_dir)
        from lab3 import days as LD
        days_reader = LD.Days(out_root, 'research')
    part = part_name(subject, direction); acc = {'coin': [], 't_alarm': [], 't_decision': []}; acc.update({n: [] for n in NAMES})
    for day in days_reader.days():
        if not first <= day <= last:
            continue
        if AC.sealed(day):
            raise PermissionError('%s: %s: refused' % (day, AC.sealed(day)))
        if part not in days_reader.parts(day):
            continue
        ix = days_reader.index(day, part); off = json.loads(ix['seal'])['known_at_offset_s']; coins = ix['coins']; base = None
        for nm in NAMES:
            r = days_reader.rows(code_name(subject, direction, nm), day, coins); keys = []; vals = []
            for c in coins:
                for b, a, k in zip(r[c]['value_bits'], r[c]['as_of_us'], r[c]['known_at_us']):
                    keys.append((c, a, k)); vals.append(np.array([b], '<u8').view('<f8')[0] if b is not None else np.nan)
            if base is None:
                base = keys; acc['coin'] += [k[0] for k in keys]; acc['t_alarm'] += [k[1] / 1e6 for k in keys]
                acc['t_decision'] += [k[2] / 1e6 - off for k in keys]
            elif keys != base:
                raise ValueError('%s %s: rows of %s not in the order of the first code' % (day, part, nm))
            acc[nm] += vals
    return {k: np.array(v) for k, v in acc.items()}


def bracket(x, offer, stop, H, cost_pct=None):
    """one target / stop pair within H minutes, from the stored touches (no new prices): per row WIN = offer first touched within H and
    before the stop (same second = stop first, the ladder's rule), LOSS = stop touched within H at or before the offer, OPEN = neither within
    H (its booking needs the price at H, not stored: reported apart, never guessed), NaN = not filled or the path not known to H.
    -> dict(win, loss, open (share of the known rows), n, net_closed = mean of +offer / -stop - cost over WIN and LOSS rows only,
    net_open0 = the mean over all known rows with OPEN booked at 0 - cost: an opinion, labelled so)"""
    lim = H * 60.0; to = x['ot_%02d' % round(offer * 10)]; th = x['ht_%02d' % round(stop * 10)]
    ok = (x['filled'] == 1) & ((x['known_s'] >= lim) | (np.isfinite(to) & (to <= lim)) | (np.isfinite(th) & (th <= lim)))
    t_o = np.where(np.isfinite(to) & (to <= lim), to, np.inf); t_h = np.where(np.isfinite(th) & (th <= lim), th, np.inf)
    win = ok & (t_o < t_h); loss = ok & np.isfinite(t_h) & (t_h <= t_o); opn = ok & ~win & ~loss
    c = np.zeros(len(to)) if cost_pct is None else np.asarray(cost_pct, float)
    pnl = np.where(win, offer, np.where(loss, -stop, 0.0)) - c; n = int(ok.sum()); closed = win | loss
    return dict(n=n, win=win.sum() / max(n, 1), loss=loss.sum() / max(n, 1), open=opn.sum() / max(n, 1),
                net_closed=float(np.mean(pnl[closed & np.isfinite(pnl)])) if closed.any() else np.nan,
                net_open0=float(np.mean(pnl[ok & np.isfinite(pnl)])) if n else np.nan)


def join(ctx, stp):
    """-> (i_ctx, i_stamp): the rows of alarm_context.read() and of read() that are the same (coin, alarm, decision), to the millisecond"""
    key = lambda x, i: (x['coin'][i], int(round(x['t_alarm'][i] * 1e3)), int(round(x['t_decision'][i] * 1e3)))
    pos = {key(stp, j): j for j in range(len(stp['coin']))}; a, b = [], []
    for i in range(len(ctx['coin'])):
        j = pos.get(key(ctx, i))
        if j is not None:
            a.append(i); b.append(j)
    return np.array(a, int), np.array(b, int)


def show(out_root, code_dir, subject, direction, first, last):
    x = read(out_root, code_dir, subject, direction, first, last); s = stamps(x); n = len(x['coin'])
    print('ROWS %d filled %d  (%s %s)' % (n, int(np.nansum(x['filled'] == 1)), subject, direction))
    print('offer  horizon  reached  heat-before median / p75 / p90 (of those that reached)')
    for H in HORIZONS:
        for o in OFFERS:
            r = s['reach_%g_%dm' % (o, H)]; hb = s['hb_%g_%dm' % (o, H)]; k = np.isfinite(r); g = np.isfinite(hb)
            q = np.percentile(hb[g], [50, 75, 90]) if g.any() else [np.nan] * 3
            print('%4.1f  %4d  %.3f (n %d)  %.1f / %.1f / %.1f' % (o, H, np.nanmean(r) if k.any() else np.nan, int(k.sum()), q[0], q[1], q[2]))


def main(a):
    if a[0] == 'catalog':
        txt = catalog_text(); open(CATALOG + '.tmp', 'w').write(txt); os.replace(CATALOG + '.tmp', CATALOG); print('CATALOG', AC.sha16_file(CATALOG))
    elif a[0] == 'build':
        lab, code_dir, efill, eladder, evp, subj, direction, first, last = a[1:10]; out = a[10] if len(a) > 10 else OUT_ROOT
        dec = tuple(float(x) for x in a[11].split(',')) if len(a) > 11 else (0,)
        got = build(lab, code_dir, efill, eladder, evp, subj, direction, first, last, out, dec)
        print('BUILD %s days %d written %d up to date %d refused %d' % (direction, len(got), sum(v == 'WRITTEN' for v in got.values()),
              sum(v == 'UP TO DATE' for v in got.values()), sum(v == 'REFUSED' for v in got.values())))
    elif a[0] == 'show':
        show(*a[1:7])
    else:
        raise SystemExit(__doc__)


if __name__ == '__main__':
    main(sys.argv[1:])
