#!/usr/bin/env python3
"""readings_builder_v1.py (SCO-A150 for SCOUT, 6 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED: never a PASS.
READINGS and FORCED for one alarm and one block, at the fire and at its matched moments, from the lab store through the RELEASED
alarm_context (05_Profile/tree/tools/alarm_context/alarm_context.py, sha16 pinned 38bdf42a6bdae4cb, imported read-only, never edited):
  1. build: alarm_context.build(lab_days, events, subject, level, first, last, out_root, decisions=(0,), code_dir=lab3) for the levels
     EVENT, MARKET, COIN, twice: subject A02 on the alarm's whole fire list (its own history), subject A02_MATCH on the matched moments
     (history = the whole fire list, as the catalog's A02_MATCH rows). The subject is only the part's NAME: each alarm and block gets
     its own playground out root (<out>/ctx_fire, <out>/ctx_match), so no shared store part is written or overwritten.
  2. read: alarm_context.read(root, lab3, subject, first, last, VALUES) -> READINGS.tsv rows (who FIRE or MATCH, coin, t, code
     CTX.<value>, value, known_at = t_decision); FIRE rows must join the block's fires on (coin, whole t) one for one (JOIN_MISSING
     names the count; a fire with no row is listed, never filled).
  3. FORCED.tsv: from CTX forced_log_usd_15m (the FORCED side: lab A1.S08 longs when the push is down, A1.S09 shorts when up) and
     other_log_usd_15m: side -1 long_usd = 10^forced, short_usd = 10^other; side +1 the mirror; known_at = t (decision 0).
Matched moments: the fixed draw of alarm_match draw_v3 (MOMENTS_V3.tsv, EDGES_V3.tsv; PG20261106_alarm_match_lawpath edition).
MATCH rows carry the parent fire's month through EDGES_V3 (fid -> cand_t); a moment is kept once per (coin, t).
  python3 -B readings_builder_v1.py <new out dir> --fires FIRES.tsv --draw <draw dir> --first YYYYMMDD --last YYYYMMDD
      --lab-days <lab_days> --lab3 <lab3 code dir> --release <volat_release root> [--levels EVENT,MARKET,COIN] [--max-days N]
Exit 0 written, 2 REFUSED <CODE>, 3 FAILED."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, datetime as dt, hashlib, importlib.util, json, math, os, time
import numpy as np

AC_REL = os.path.join('Alarm', 'alarm', 'current', '05_Profile', 'tree', 'tools', 'alarm_context', 'alarm_context.py')
AC_PIN = '38bdf42a6bdae4cb'
VALUES = {  # question -> CTX values (catalog names); fixed before any read
    2: ('hour_utc', 'weekday', 'fires_other_60m', 'alarms_all_24h', 'btc_vol_regime', 'market_hot_rank_30d'),
    3: ('move_15m', 'coin_move_15m', 'btc_move_15m', 'basket_move_15m', 'coin_vs_basket_15m', 'coin_with_market_15m', 'one_sided_5m', 'basis_push_bp'),
    4: ('forced_log_usd_15m', 'other_log_usd_15m', 'forced_share_15m', 'oi_chg_10m', 'liq_oi_forced_bp_60s', 'coins_liquidating_z',
        'oi_moved_since_wave'),
    5: ('fills_one_sided', 'volume_one_sided', 'whale_net_5m_usd', 'funding_forced_pays_bp', 'forced_over_taker_15m'),
}
ALL_VALUES = tuple(v for q in sorted(VALUES) for v in VALUES[q])


class Refused(Exception):
    def __init__(self, code, detail=''):
        super().__init__('%s %s' % (code, detail)); self.code = code; self.detail = detail


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def day_of(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def read_tsv(p):
    with open(p) as f:
        return list(csv.DictReader((l for l in f if not l.startswith('#')), delimiter='\t'))


def load_ac(release):
    p = os.path.join(release, AC_REL)
    if not os.path.exists(p):
        raise Refused('NO_RELEASE', p)
    if sha16_file(p) != AC_PIN:
        raise Refused('SOURCE_CHANGED', '%s is %s, pinned %s' % (p, sha16_file(p), AC_PIN))
    sp = importlib.util.spec_from_file_location('alarm_context_pinned_rb', p)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m, p


def write_events(path, rows):
    with open(path, 'w') as f:
        f.write('coin\tt\tside\n')
        for c, t, s in rows:
            f.write('%s\t%s\t%d\n' % (c, repr(float(t)) if float(t) != int(float(t)) else str(int(float(t))), s))


def moments_of(draw, fire_keys):
    """moments (coin, t, side) whose parent fire is in the block (EDGES_V3 fid <-> parent_t); kept once per (coin, t)"""
    E = read_tsv(os.path.join(draw, 'EDGES_V3.tsv'))
    out = {}
    for e in E:
        pk = (e['coin'], int(round(float(e['parent_t']))))
        if pk not in fire_keys:
            continue
        k = (e['coin'], float(e['cand_t']))
        out.setdefault(k, (e['coin'], float(e['cand_t']), int(float(e['side'])), pk[1]))
    return sorted(out.values(), key=lambda x: (x[1], x[0]))


def build(a, ac=None, log=print):
    t0 = time.time()
    if os.path.exists(a.out):
        raise Refused('OUT_EXISTS', a.out)
    F = read_tsv(a.fires)
    if not F or not {'coin', 't', 'side'} <= set(F[0]):
        raise Refused('BAD_INPUT', '%s: header coin t side' % a.fires)
    allf = [(r['coin'], int(float(r['t'])), int(float(r['side']))) for r in F]
    blk = [x for x in allf if a.first <= day_of(x[1]) <= a.last]
    if not blk:
        raise Refused('BAD_INPUT', 'no fire in %s..%s' % (a.first, a.last))
    days = sorted(set(day_of(x[1]) for x in blk))
    last = a.last
    if a.max_days:
        last = days[min(a.max_days, len(days)) - 1]; blk = [x for x in blk if day_of(x[1]) <= last]
    fk = {(c, t): s for c, t, s in blk}
    M = moments_of(a.draw, set(fk)) if a.draw else []
    os.makedirs(a.out)
    fe = os.path.join(a.out, 'EVENTS_FIRES.tsv'); write_events(fe, [(c, t, s) for c, t, s in allf])
    me = os.path.join(a.out, 'EVENTS_MATCH.tsv'); write_events(me, [(c, t, s) for c, t, s, _ in M])
    if ac is None:
        ac, acp = load_ac(a.release)
    else:
        acp = 'planted'
    levels = a.levels.split(',')
    rf, rm = os.path.join(a.out, 'ctx_fire'), os.path.join(a.out, 'ctx_match')
    timing = []
    for lv in levels:
        t1 = time.time(); got = ac.build(a.lab_days, fe, 'A02', lv, a.first, last, rf, (0,), code_dir=a.lab3, log=log)
        timing.append(('FIRE', lv, len(got), round(time.time() - t1, 1)))
        if M:
            t1 = time.time(); got = ac.build(a.lab_days, me, 'A02_MATCH', lv, a.first, last, rm, (0,), code_dir=a.lab3, log=log, hist_path=fe)
            timing.append(('MATCH', lv, len(got), round(time.time() - t1, 1)))
    lvl = {c[2]: c[0] for c in ac.columns()}
    vals = [v for v in ALL_VALUES if lvl.get(v) in levels]
    rows = []; fired = {}; nf = 0
    for who, root, subj in (('FIRE', rf, 'A02'), ('MATCH', rm, 'A02_MATCH')):
        if who == 'MATCH' and not M:
            continue
        o = ac.read(root, a.lab3, subj, a.first, last, vals)
        for i in range(len(o['coin'])):
            c = str(o['coin'][i]); t = float(o['t_alarm'][i]); ka = float(o['t_decision'][i])
            if who == 'FIRE':
                k = (c, int(round(t)))
                if k not in fk:
                    continue                      # a fire outside the block (the whole list is the history)
                t = k[1]; nf += 1; fired[k] = {v: float(o[v][i]) for v in vals}
            for v in vals:
                x = float(o[v][i])
                if math.isfinite(x):
                    rows.append((who, c, t, 'CTX.' + v, x, ka))
    missing = sorted(set(fk) - set(fired))
    with open(os.path.join(a.out, 'READINGS.tsv'), 'w') as f:
        f.write('# READINGS from alarm_context.read (%s, sha16 %s); FIRE = the alarm fires, MATCH = the draw_v3 matched moments; block %s..%s\n'
                % (acp, AC_PIN, a.first, last))
        f.write('who\tcoin\tt\tcode\tvalue\tknown_at\n')
        for r in rows:
            f.write('%s\t%s\t%s\t%s\t%r\t%s\n' % (r[0], r[1], ('%d' % r[2]) if r[0] == 'FIRE' else repr(r[2]), r[3], r[4], repr(r[5])))
    with open(os.path.join(a.out, 'FORCED.tsv'), 'w') as f:
        f.write('# FORCED from CTX forced_log_usd_15m (forced side: longs A1.S08 when side -1, shorts A1.S09 when side +1) and other_log_usd_15m\n')
        f.write('coin\tt\tlong_usd\tshort_usd\tknown_at\n')
        for (c, t), d in sorted(fired.items(), key=lambda x: (x[0][1], x[0][0])):
            fo, ot = d.get('forced_log_usd_15m', np.nan), d.get('other_log_usd_15m', np.nan)
            usd = lambda x: (0.0 if x == 0 else 10 ** x) if math.isfinite(x) else float('nan')   # log 0 = none (the catalog's unit)
            pf, po = usd(fo), usd(ot)
            lo, sh = (pf, po) if fk[(c, t)] == -1 else (po, pf)
            f.write('%s\t%d\t%s\t%s\t%d\n' % (c, t, '' if not math.isfinite(lo) else repr(lo), '' if not math.isfinite(sh) else repr(sh), t))
    mm = {}
    for c, t, s, pt in M:
        mm[(c, t)] = pt
    with open(os.path.join(a.out, 'MATCH_PARENT.tsv'), 'w') as f:
        f.write('coin\tt\tparent_t\n'); [f.write('%s\t%r\t%d\n' % (c, t, pt)) for (c, t), pt in sorted(mm.items(), key=lambda x: x[0][1])]
    notes = {'fires_block': len(blk), 'fires_with_row': nf, 'fires_without_row': len(missing), 'moments': len(M), 'first': a.first,
             'last': last, 'values': vals, 'timing': timing, 'seconds': round(time.time() - t0, 1), 'alarm_context': acp,
             'alarm_context_sha16': AC_PIN, 'fires_sha16': sha16_file(a.fires),
             'draw_moments_sha16': sha16_file(os.path.join(a.draw, 'EDGES_V3.tsv')) if a.draw else ''}
    json.dump(notes, open(os.path.join(a.out, 'READINGS_NOTES.json'), 'w'), indent=1, sort_keys=True)
    log('READINGS fires %d with row %d without %d moments %d rows %d seconds %.1f' % (len(blk), nf, len(missing), len(M), len(rows), time.time() - t0))
    return notes


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--fires', required=True); ap.add_argument('--draw', default='')
    ap.add_argument('--first', required=True); ap.add_argument('--last', required=True)
    ap.add_argument('--lab-days', default='<DATA_ROOT>/lab_days'); ap.add_argument('--lab3', required=True)
    ap.add_argument('--release', required=True); ap.add_argument('--levels', default='EVENT,MARKET,COIN')
    ap.add_argument('--max-days', type=int, default=0)
    a = ap.parse_args(argv)
    try:
        build(a); return 0
    except Refused as e:
        print('REFUSED', e.code, e.detail); return 2
    except Exception as e:
        import traceback; traceback.print_exc(); print('FAILED', repr(e)); return 3


if __name__ == '__main__':
    sys.exit(main())
