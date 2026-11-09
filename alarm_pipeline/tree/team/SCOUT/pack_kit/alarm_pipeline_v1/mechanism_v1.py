#!/usr/bin/env python3
"""mechanism_v1.py (SCO-A153 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; alarm_pipeline_v1 step 17/18; real data: a runner job
only). Classifies ONE alarm to ONE id of MECHANISM_MAP_V1.md (sha16 2f1131b39bd554a5, pinned: REFUSED MAP_CHANGED otherwise) or NONE, from
the as-of share of its fires where the map row's membership rule holds at the fire second (map: 'A member needs that share >= 0.90').
  python3 -B mechanism_v1.py <out MECHANISM.json> --readings <RD dir: READINGS.tsv> --fires FIRES.tsv --first YYYYMMDD --last YYYYMMDD
      --lean FADE|FOLLOW --map MECHANISM_MAP_V1.md [--card-tsv ALARM_CARDS_<X>.tsv --card-alarm <alarm>]
RULES, FIXED BEFORE ANY RUN (6 Nov 2026, from the map's membership column, CTX names of readings_builder_v1):
  AS OF      only FIRE readings with known_at <= t; a fire without a reading does not hold (counted as missing, coverage printed).
  FORCED_OUT        lean FADE AND down push (fire side -1) AND CTX.forced_log_usd_15m (the forced side: longs on a down push, lab
                    A1.S08) above the coin's own p90 AND CTX.oi_chg_10m < 0 (open interest falling over the last 10 min).
  FORCED_OUT_SHORTS lean FADE AND up push (side +1) AND the forced side (shorts, A1.S09) above its own p90 AND CTX.oi_chg_10m < 0.
  CROWDED_LATE      no rule in the map ('not defined yet'): never a member, share not computed.
  OWN p90    the 90th percentile of the coin's matched moments (MATCH rows of the same code: the coin's own no-alarm moments, +-7 days,
             draw_v3); a coin with under 20 matched values takes the pooled matched p90 of the block (named in the json). This is a proxy
             for the map's 'coin's own p90' (the map does not fix the reference set).
  CHOICE     the id with the largest share when that share >= 0.90, else NONE (the largest share is still printed).
The card's Q3 and Q4 rows (answer and strength) are copied beside the shares. Exit 0 written, 2 REFUSED, 3 FAILED.
LEGS (added 2026-11-06 after the first real run, job 20270189, where the map's own members FDAOI and FDAOIV read 0.51 and 0.55: the
rule, the reference set and the threshold are unchanged; only the share of each leg is printed beside the share, so the failing leg is
named): side (the push the row needs), liq (forced side above the own p90), oi (open interest falling), each over the fires."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, datetime as dt, hashlib, json, os

MAP_PIN = '2f1131b39bd554a5'
THRESHOLD = 0.90
MIN_OWN = 20
RULES = {'FORCED_OUT': -1, 'FORCED_OUT_SHORTS': +1}
UNDEFINED = ('CROWDED_LATE',)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def rows(p):
    return list(csv.DictReader((l for l in open(p) if not l.startswith('#')), delimiter='\t'))


def p90(v):
    v = sorted(v)
    if not v:
        return None
    k = 0.9 * (len(v) - 1); i = int(k)
    return v[i] if i + 1 >= len(v) else v[i] + (v[i + 1] - v[i]) * (k - i)


def classify(fires, readings, lean):
    fire_v = {}; match_v = {}
    for r in readings:
        if r['code'] not in ('CTX.forced_log_usd_15m', 'CTX.oi_chg_10m'):
            continue
        try:
            v = float(r['value'])
        except ValueError:
            continue
        if v != v:
            continue
        key = (r['coin'], int(float(r['t'])))
        if r['who'] == 'FIRE':
            if float(r['known_at']) <= float(r['t']):
                fire_v[(key, r['code'])] = v
        elif r['who'] == 'MATCH' and r['code'] == 'CTX.forced_log_usd_15m':
            match_v.setdefault(r['coin'], []).append(v)
    pooled = p90([x for v in match_v.values() for x in v])
    own = {c: (p90(v) if len(v) >= MIN_OWN else pooled) for c, v in match_v.items()}
    pooled_coins = sorted(c for c, v in match_v.items() if len(v) < MIN_OWN)
    out = {}
    for mid, side in RULES.items():
        hold = miss = 0; legs = dict(side=0, liq=0, oi=0)
        for f in fires:
            key = (f['coin'], int(float(f['t'])))
            fl = fire_v.get((key, 'CTX.forced_log_usd_15m')); oi = fire_v.get((key, 'CTX.oi_chg_10m'))
            if fl is None or oi is None:
                miss += 1; continue
            ref = own.get(f['coin'], pooled)
            legs['side'] += int(lean == 'FADE' and int(float(f['side'])) == side)
            legs['liq'] += int(ref is not None and fl > ref)
            legs['oi'] += int(oi < 0)
            if lean == 'FADE' and int(float(f['side'])) == side and ref is not None and fl > ref and oi < 0:
                hold += 1
        n = len(fires)
        out[mid] = dict(share=round(hold / n, 4) if n else None, fires=n, holds=hold, missing=miss,
                        legs={k: (round(v / n, 4) if n else None) for k, v in legs.items()},
                        coverage=round((n - miss) / n, 4) if n else None)
    for mid in UNDEFINED:
        out[mid] = dict(share=None, note='no membership rule in the map')
    return out, dict(pooled_p90=pooled, coins_on_pooled=pooled_coins, coins=len(match_v))


def card_rows(path, alarm):
    q = {}
    if path and os.path.isfile(path):
        for r in rows(path):
            if r['alarm'] == alarm and r['q'] in ('Q3', 'Q4'):
                q[r['q']] = dict(answer=r['answer'], strength=r['strength'])
    return q


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--readings', required=True); ap.add_argument('--fires', required=True)
    ap.add_argument('--first', required=True); ap.add_argument('--last', required=True); ap.add_argument('--lean', required=True)
    ap.add_argument('--map', required=True); ap.add_argument('--card-tsv', default=''); ap.add_argument('--card-alarm', default='')
    a = ap.parse_args(argv)
    if sha16(a.map) != MAP_PIN:
        print('REFUSED MAP_CHANGED: %s is %s, rules are for %s' % (a.map, sha16(a.map), MAP_PIN)); return 2
    if os.path.exists(a.out):
        print('REFUSED EXISTS: %s' % a.out); return 2
    rp = os.path.join(a.readings, 'READINGS.tsv')
    if not os.path.isfile(rp):
        print('REFUSED NO_READINGS: %s' % rp); return 2
    fires = [f for f in rows(a.fires) if a.first <= day(f['t']) <= a.last]
    shares, ref = classify(fires, rows(rp), a.lean)
    best = max((m for m in RULES), key=lambda m: shares[m]['share'] if shares[m]['share'] is not None else -1)
    bs = shares[best]['share']
    chosen = best if bs is not None and bs >= THRESHOLD else 'NONE'
    q = card_rows(a.card_tsv, a.card_alarm)
    res = dict(mechanism=chosen, share=bs, best_id=best, threshold=THRESHOLD, shares=shares, reference=ref, map=a.map, map_sha16=MAP_PIN,
               readings=rp, readings_sha16=sha16(rp), fires_file=a.fires, fires_sha16=sha16(a.fires), fires_in_block=len(fires),
               window='%s..%s' % (a.first, a.last), lean=a.lean, q3=q.get('Q3', {}), q4=q.get('Q4', {}),
               rule='as-of share of fires where the map membership rule holds at the fire second (mechanism_v1 docstring)')
    json.dump(res, open(a.out, 'x'), indent=1, sort_keys=True)
    print('MECHANISM %s share %s (best %s; %d fires; map %s)' % (chosen, bs, best, len(fires), MAP_PIN))
    return 0


if __name__ == '__main__':
    sys.exit(main())
