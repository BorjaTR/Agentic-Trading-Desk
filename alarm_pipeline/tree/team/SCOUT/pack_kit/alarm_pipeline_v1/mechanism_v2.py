#!/usr/bin/env python3
"""mechanism_v2.py (SCO-A154 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED; successor of mechanism_v1, which stays as it is; real
data: a runner job only). Classifies ONE alarm to ONE id of MECHANISM_MAP_V1.md (sha16 2f1131b39bd554a5, pinned: REFUSED MAP_CHANGED
otherwise), NONE, UNKNOWN or CANDIDATE, from the as-of share of its fires where the map row's membership rule holds at the fire second.
  python3 -B mechanism_v2.py <out MECHANISM.json> --bundle <BUNDLE dir: FIRES.tsv, BUNDLE_SOURCES.tsv, CONTEXT.tsv> --def DEF.json
      --first YYYYMMDD --last YYYYMMDD --lean FADE|FOLLOW --map MECHANISM_MAP_V1.md [--readings <RD dir: READINGS.tsv>]
      [--card-tsv ALARM_CARDS_<X>.tsv --card-alarm <alarm>] [--hypothesis <map id>]
WHY V2: mechanism_v1 read stand-ins (CTX.oi_chg_10m = Binance open interest, lab E2.S04; the forced side over a matched-moment p90), not
the map's codes. V2 reads each rule from the map text itself and accepts only the map's own codes.
RULES, FIXED BEFORE ANY RUN (6 Nov 2026):
  MAP RULE   each '## Mechanisms' row's membership column is split on ' AND '; each clause must parse as one leg, or the row has no
             machine rule (printed, share not computed); 'not defined yet' is no rule. Legs: side '<FADE|FOLLOW> of a <down|up> move';
             liq 'Binance <long|short> liquidations [over <m> min] above [the coin's] own p<q>' (long = A1.S08, short = A1.S09: the map's
             'A1.S08 family' and the DEF names); oi 'Hyperliquid open interest falling [over the last <m> min]' (E2.S06, a 10 min change).
  THRESHOLD  the number after 'share >=' in the map's 'How an alarm joins a mechanism' section (0.90 there: STRATEGY proposal, SCOUT may
             set it, open item O1). No number there: the best id is labelled CANDIDATE with its share, never a number of ours.
  AS OF      a leg holds or fails at the fire second only from (a) a READINGS row who FIRE, code E2.S06, known_at <= t (oi leg; < 0 holds),
             or (b) the alarm's own detector: the DEF has a condition equal to the leg (same raw code, same 900 s sum when the map names a
             window, own_pct with the same q, '>' 0; or raw E2.S06 '<' 0), the DEF sha16 is the definition_sha16 the bundle's STORE_RUN
             row binds, and the fire has a CONTEXT row EVENT_LIST onset_t = t with after 0 and known_at <= t (the detector fired on that
             second, so every DEF condition held). Rows with after 1 (PARENTS, AFTER) are never read. Side: the fire's own side and lean.
             Anything else is UNKNOWN (never a fail). Stand-in codes (CTX.*) are never read.
  KITQ       V1_3_3 (SCO-A172, 7 Nov 2026): a bundle built --from-job from a kitq GRADE job (pipeline step 17) has no STORE_RUN row and
             no CONTEXT.tsv (bundle_builder_v1 writes both only --from-gg), so (b) was never met (learning series runs 1-3: def_bound
             false, 0 onsets, liq and oi UNKNOWN). With no STORE_RUN row, (b) is read from the bundle's own JOB and FIRE_LIST rows
             instead, each file still carrying its row's sha16: the job binds the DEF when it has exactly one VS=(..), DEFS=(..),
             DSHAS=(..), checks them before its chain (ck $RD/${DEFS[$i]} ${DSHAS[$i]}), and the list's variant (<V>_FIRES_V1_LIST.tsv)
             has a .json DEF (a detector run, not a given list) whose DSHAS entry is the DEF sha16; the list is the detector's EVENTS.tsv,
             so a fire is a detector onset when its row has onset_t = t (known at t: the detection writes its row at t). binding in the
             output names which way (STORE_RUN, KITQ_GRADE_JOB or none).
  ONCE       a fire is (coin, t) inside first..last; a fire listed again (another wave or row) counts once.
  SHARE      per id: holds / fires (a fire holds when every leg holds; fails when one leg fails; else unknown); upper = (holds+unknown)/fires.
  CHOICE     ids with share >= threshold are members: one member is the id (several: the largest share); no member but an id whose upper
             reaches the threshold: UNKNOWN; else NONE. Every share and the map's open items are printed.
Exit 0 written, 2 REFUSED, 3 FAILED."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, datetime as dt, hashlib, json, os, re

MAP_PIN = '2f1131b39bd554a5'
LIQ_CODE = {'long': 'A1.S08', 'short': 'A1.S09'}
OI_CODE = 'E2.S06'


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def day(t):
    return dt.datetime.fromtimestamp(float(t), dt.timezone.utc).strftime('%Y%m%d')


def rows(p):
    return list(csv.DictReader((l for l in open(p) if not l.startswith('#')), delimiter='\t'))


# ---------------------------------------------------------------- the map
def parse_clause(c):
    c = re.sub(r'\s*\([^)]*\)', '', c).strip()
    m = re.fullmatch(r'side (FADE|FOLLOW) of an? (down|up) move', c)
    if m:
        return 'side', (m.group(1), -1 if m.group(2) == 'down' else 1)
    m = re.fullmatch(r"Binance (long|short) liquidations (?:over (\d+) min )?above (?:the coin's )?own p(\d+)", c)
    if m:
        return 'liq', (LIQ_CODE[m.group(1)], int(m.group(2)) if m.group(2) else None, int(m.group(3)))
    m = re.fullmatch(r'Hyperliquid open interest falling(?: over the last (\d+) min)?', c)
    if m:
        return 'oi', (OI_CODE, '<', int(m.group(1)) if m.group(1) else None)
    return None, c


def parse_map(text):
    """returns ({id: {side, liq, oi} or None}, threshold or None, [open items])"""
    R, sec, opn, thr = {}, '', [], None
    for l in text.splitlines():
        if l.startswith('## '):
            sec = l[3:].strip(); continue
        if sec.startswith('How an alarm joins'):
            m = re.search(r'share >= ([0-9]*\.?[0-9]+)', l)
            if m and thr is None:
                thr = float(m.group(1))
        if sec == 'Mechanisms' and l.startswith('| ') and not l.startswith('| id ') and not l.startswith('|---'):
            cells = [x.strip() for x in l.strip().strip('|').split('|')]
            mid, rule = cells[0], cells[2]
            if 'not defined yet' in rule:
                R[mid] = None; continue
            legs, bad = {}, []
            for c in rule.split(' AND '):
                k, v = parse_clause(c)
                if k is None or k in legs:
                    bad.append(v)
                else:
                    legs[k] = v
            R[mid] = legs if not bad and set(legs) == {'side', 'liq', 'oi'} else dict(unparsed=bad or ['legs %s' % sorted(legs)])
        if sec == 'Open' and l.startswith('- '):
            opn.append(l[2:].strip())
    return R, thr, opn


# ---------------------------------------------------------------- the DEF
def def_has(D, leg, spec):
    """the DEF holds a condition equal to the map leg (exact codes, window, q)"""
    I = D.get('inputs', {})
    for c in D.get('conditions', []):
        x = I.get(c.get('lhs'), {})
        if leg == 'oi':
            if x.get('op') == 'raw' and x.get('code') == spec[0] and c.get('cmp') == '<' and c.get('rhs') == 0 and spec[2] in (None, 10):
                return True
        if leg == 'liq':
            if x.get('op') != 'sub' or c.get('cmp') != '>' or c.get('rhs') != 0:
                continue
            s, p = I.get(x.get('a'), {}), I.get(x.get('b'), {})
            r = I.get(s.get('of'), {})
            if (s.get('op') == 'sum' and r.get('op') == 'raw' and r.get('code') == spec[0] and p.get('op') == 'own_pct'
                    and p.get('of') == x.get('a') and p.get('q') == spec[2] and (spec[1] is None or s.get('w_s') == spec[1] * 60)):
                return True
    return False


def bound_sha(bundle):
    p = os.path.join(bundle, 'BUNDLE_SOURCES.tsv')
    if not os.path.isfile(p):
        return None
    for r in rows(p):
        if r.get('role') == 'STORE_RUN':
            m = re.search(r'definition_sha16 ([0-9a-f]{16})', r.get('note') or '')
            if m:
                return m.group(1)
    return None


def kitq_binding(bundle):
    """V1_3_3 (SCO-A172): -> (DEF sha16 the kitq GRADE job binds for the list's variant or None, {(coin, t) detector onsets}, why)"""
    p = os.path.join(bundle, 'BUNDLE_SOURCES.tsv')
    if not os.path.isfile(p):
        return None, set(), 'no BUNDLE_SOURCES.tsv'
    S = {}
    for r in rows(p):
        if r.get('role') in ('JOB', 'FIRE_LIST'):
            S.setdefault(r['role'], []).append(r)
    if len(S.get('JOB', [])) != 1 or len(S.get('FIRE_LIST', [])) != 1:
        return None, set(), 'not one JOB and one FIRE_LIST row'
    jr, lr = S['JOB'][0], S['FIRE_LIST'][0]
    for r in (jr, lr):
        if not os.path.isfile(r['path']) or sha16(r['path']) != r['sha16']:
            return None, set(), '%s %s missing or changed' % (r['role'], r['path'])
    onset = set()
    for r in rows(lr['path']):
        try:
            t = int(float(r['t']))
            if int(float(r['onset_t'])) == t:
                onset.add((r['coin'], t))
        except (KeyError, TypeError, ValueError):
            continue
    text = open(jr['path']).read()
    A = {k: re.findall(r'(?m)^%s=\(([^)]*)\)' % k, text) for k in ('VS', 'DEFS', 'DSHAS')}
    if any(len(v) != 1 for v in A.values()) or 'ck $RD/${DEFS[$i]} ${DSHAS[$i]}' not in text:
        return None, onset, 'the job does not pin one VS, DEFS, DSHAS before its chain'
    vs, defs, dshas = (A[k][0].split() for k in ('VS', 'DEFS', 'DSHAS'))
    m = re.fullmatch(r'(.+)_FIRES_V1_LIST\.tsv', os.path.basename(lr['path']))
    if not m or m.group(1) not in vs or not (len(vs) == len(defs) == len(dshas)):
        return None, onset, 'the list variant is not one of the job VS'
    i = vs.index(m.group(1))
    if not defs[i].endswith('.json'):
        return None, onset, 'the variant DEF %s is a given list, not a detector run' % defs[i]
    return dshas[i], onset, 'kitq GRADE job %s pins %s for %s' % (os.path.basename(jr['path']), dshas[i], m.group(1))


# ---------------------------------------------------------------- the share
def classify(fires, onset, readings, D, def_ok, R, lean):
    out = {}
    for mid, legs in R.items():
        if legs is None:
            out[mid] = dict(share=None, note='no membership rule in the map'); continue
        if 'unparsed' in legs:
            out[mid] = dict(share=None, note='membership rule not machine-read: %s' % '; '.join(legs['unparsed'])); continue
        src = {'liq': def_ok and def_has(D, 'liq', legs['liq']), 'oi': def_ok and def_has(D, 'oi', legs['oi'])}
        cnt = dict(hold=0, fail=0, unknown=0); lc = {k: dict(hold=0, fail=0, unknown=0) for k in ('side', 'liq', 'oi')}
        months = {}
        for f in fires:
            key = (f['coin'], f['t'])
            st = {}
            st['side'] = ('unknown' if f['side'] is None else
                          'hold' if (lean == legs['side'][0] and f['side'] == legs['side'][1]) else 'fail')
            det = key in onset
            st['liq'] = 'hold' if (src['liq'] and det) else 'unknown'
            rv = readings.get((key, legs['oi'][0])) if legs['oi'][2] in (None, 10) else None
            if rv is not None:
                st['oi'] = 'hold' if rv < 0 else 'fail'
            else:
                st['oi'] = 'hold' if (src['oi'] and det) else 'unknown'
            for k, v in st.items():
                lc[k][v] += 1
            w = 'fail' if 'fail' in st.values() else 'hold' if all(v == 'hold' for v in st.values()) else 'unknown'
            cnt[w] += 1
            mo = months.setdefault(day(f['t'])[:6], dict(fires=0, holds=0)); mo['fires'] += 1; mo['holds'] += w == 'hold'
        n = len(fires)
        r4 = lambda x: round(x / n, 4) if n else None
        out[mid] = dict(share=r4(cnt['hold']), upper=r4(cnt['hold'] + cnt['unknown']), unknown_share=r4(cnt['unknown']), fires=n,
                        holds=cnt['hold'], fails=cnt['fail'], unknown=cnt['unknown'],
                        legs={k: {s: r4(v) for s, v in d.items()} for k, d in lc.items()},
                        sources=dict(side='fire side and lean', liq='DEF condition at the detector fire second' if src['liq'] else 'none',
                                     oi=('DEF condition at the detector fire second' if src['oi'] else 'none') + '; READINGS E2.S06 as of t'),
                        months={k: dict(v, share=round(v['holds'] / v['fires'], 4)) for k, v in sorted(months.items())},
                        rule=legs)
    return out


def decide(S, thr):
    ids = [m for m in S if S[m].get('share') is not None]
    if not ids:
        return dict(mechanism='UNKNOWN', share=None, best_id=None, why='no id with a rule')
    best = max(ids, key=lambda m: (S[m]['share'], m))
    if thr is None:
        return dict(mechanism='CANDIDATE', candidate_id=best, share=S[best]['share'], best_id=best, why='the map names no threshold')
    if all(S[m].get('fires', 1) == 0 for m in ids):
        return dict(mechanism='UNKNOWN', share=None, best_id=best, why='no fires in the block')
    mem = [m for m in ids if S[m]['share'] >= thr]
    if mem:
        m = max(mem, key=lambda x: (S[x]['share'], x))
        return dict(mechanism=m, share=S[m]['share'], best_id=m, members=sorted(mem), why='share >= threshold')
    und = [m for m in ids if S[m].get('upper') is not None and S[m]['upper'] >= thr]
    if und:
        u = max(und, key=lambda m: (S[m]['share'], S[m]['upper'], m))
        return dict(mechanism='UNKNOWN', share=S[u]['share'], best_id=u, undecided=sorted(und),
                    why='no member; unknown fires could reach the threshold for %s' % ','.join(sorted(und)))
    return dict(mechanism='NONE', share=S[best]['share'], best_id=best, why='every upper bound below the threshold')


def card_rows(path, alarm):
    q = {}
    if path and os.path.isfile(path):
        for r in rows(path):
            if r['alarm'] == alarm and r['q'] in ('Q3', 'Q4'):
                q[r['q']] = dict(answer=r['answer'], strength=r['strength'])
    return q


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('out'); ap.add_argument('--bundle', required=True); ap.add_argument('--def', dest='defp', required=True)
    ap.add_argument('--first', required=True); ap.add_argument('--last', required=True); ap.add_argument('--lean', required=True)
    ap.add_argument('--map', required=True); ap.add_argument('--readings', default='')
    ap.add_argument('--card-tsv', default=''); ap.add_argument('--card-alarm', default=''); ap.add_argument('--hypothesis', default='')
    a = ap.parse_args(argv)
    if sha16(a.map) != MAP_PIN:
        print('REFUSED MAP_CHANGED: %s is %s, rules are for %s' % (a.map, sha16(a.map), MAP_PIN)); return 2
    if os.path.exists(a.out):
        print('REFUSED EXISTS: %s' % a.out); return 2
    if a.lean not in ('FADE', 'FOLLOW'):
        print('REFUSED BAD_LEAN: %s' % a.lean); return 2
    fp = os.path.join(a.bundle, 'FIRES.tsv')
    for q in (fp, a.defp):
        if not os.path.isfile(q):
            print('REFUSED NO_FILE: %s' % q); return 2
    try:
        R, thr, opn = parse_map(open(a.map).read())
        D = json.load(open(a.defp)); ds = sha16(a.defp); bs = bound_sha(a.bundle)
        binding = 'STORE_RUN' if bs is not None else None
        konset, kwhy = set(), None
        if bs is None:
            bs, konset, kwhy = kitq_binding(a.bundle)
            binding = 'KITQ_GRADE_JOB' if bs is not None else None
        def_ok = bs is not None and bs == ds
        seen, fires, dup = set(), [], 0
        for f in rows(fp):
            t = int(float(f['t']))
            if not (a.first <= day(t) <= a.last):
                continue
            k = (f['coin'], t)
            if k in seen:
                dup += 1; continue
            seen.add(k)
            s = (f.get('side') or '').strip()
            fires.append(dict(coin=f['coin'], t=t, side=int(float(s)) if s not in ('', 'nan', 'NA') else None))
        onset, after_n = set(), 0
        cp = os.path.join(a.bundle, 'CONTEXT.tsv')
        if os.path.isfile(cp):
            for r in rows(cp):
                if (r.get('after') or '').strip() != '0':
                    after_n += 1; continue
                if r.get('source') == 'EVENT_LIST' and r.get('column') == 'onset_t':
                    t = int(float(r['t']))
                    if int(float(r['value'])) == t and float(r['known_at']) <= t:
                        onset.add((r['coin'], t))
        onset |= konset
        readings = {}
        rp = os.path.join(a.readings, 'READINGS.tsv') if a.readings else ''
        if rp and os.path.isfile(rp):
            for r in rows(rp):
                if r.get('who') != 'FIRE' or r.get('code') != OI_CODE:
                    continue
                t = int(float(r['t']))
                try:
                    v = float(r['value'])
                except ValueError:
                    continue
                if v == v and float(r['known_at']) <= t:
                    readings[((r['coin'], t), OI_CODE)] = v
        S = classify(fires, onset, readings, D, def_ok, R, a.lean)
        d = decide(S, thr)
    except Exception as e:
        print('FAILED %s: %s' % (type(e).__name__, e)); return 3
    q = card_rows(a.card_tsv, a.card_alarm)
    res = dict(d, threshold=thr, threshold_source='map section How an alarm joins a mechanism (STRATEGY proposal; SCOUT may set it; open O1)'
               if thr is not None else 'none in the map', shares=S, open_items=opn, map=a.map, map_sha16=MAP_PIN, def_file=a.defp, def_sha16=ds,
               def_bound=def_ok, bundle_definition_sha16=bs, binding=binding, kitq_note=kwhy, bundle=a.bundle, fires_file=fp, fires_sha16=sha16(fp),
               context_sha16=sha16(cp) if os.path.isfile(cp) else None, readings=rp or None, readings_sha16=sha16(rp) if rp and os.path.isfile(rp) else None,
               fires_in_block=len(fires), duplicates_dropped=dup, detector_onsets_asof=len(onset & seen), after_rows_ignored=after_n,
               window='%s..%s' % (a.first, a.last), lean=a.lean, q3=q.get('Q3', {}), q4=q.get('Q4', {}), hypothesis=a.hypothesis or None,
               tool='mechanism_v2.py', rule='as-of share of fires where the map membership rule holds at the fire second (mechanism_v2 docstring)')
    json.dump(res, open(a.out, 'x'), indent=1, sort_keys=True)
    for m in sorted(S):
        v = S[m]
        if v.get('share') is None:
            print('SHARE %s None (%s)' % (m, v.get('note')))
        else:
            print('SHARE %s %s upper %s unknown %s fires %d legs %s' % (m, v['share'], v['upper'], v['unknown_share'], v['fires'],
                  ' '.join('%s=%s/%s/%s' % (k, l['hold'], l['fail'], l['unknown']) for k, l in sorted(v['legs'].items()))))
    print('THRESHOLD %s (%s)' % (thr, res['threshold_source']))
    for o in opn:
        print('OPEN %s' % o)
    print('MECHANISM %s share %s (best %s; %d fires, %d duplicates dropped; DEF %s bound %s; map %s): %s' % (
        d['mechanism'], d.get('share'), d.get('best_id'), len(fires), dup, ds, def_ok, MAP_PIN, d.get('why')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
