"""RESEARCH tools/fairness_bar v2 (T02; owner SCOUT, built by BUILD2 23 Oct 2026; ASK STRATEGY-130408, SKEPTIC REVIEW 03). PAPER ONLY.
= fairness_bar.py ec7d8033 (v1, kept) with README V1.5 section 1h (SCOUT's rulings on SKEPTIC 03-10 to 03-14, 03-18, 03-19):
  03-10 ONE classifier: make_families_v2.family_of_all (case-insensitive, every matching family counts) on FAMILIES_V2.tsv; bar() builds the
        census ITSELF from the ledgers (no caller list of tries, no caller family: the families come from the result's PREREG row);
        while the census holds UNMAPPED tries the verdict is INCOMPLETE (they are listed), never PASS.
  03-11 the per-wave receipt carries each wave's fires (column fires = 'coin@t_unix_s;...'); bar() RECOUNTS the waves from the fire times
        with labcore.waves and refuses duplicate wave ids, a fire in two waves, waves out of time order, n_fires unequal to its fires, or
        a recount that does not give the receipt's waves. A module sha16 alone proves nothing.
  03-12 multiplicity is never optional: the roster = every counted try of the family; tries without a p-value (no per-wave receipt) are
        taken as the most significant competitors, so the result's p is Bonferroni x tries_counted until the roster is complete, then Holm;
        the line says which ('HOLM (roster complete)' / 'BONFERRONI (k p-values missing)').
  03-13 SR* (the luck bar): the 95th percentile of the MAXIMUM per-wave Sharpe over the family's tries with receipts (the result included)
        under JOINT whole-wave sign flips (one sign per wave id, shared by every try: x and -x are two choices); tries without a receipt
        enter the formula SR* (Bailey and Lopez de Prado, independent: the conservative side); the LARGER SR* is used.
  03-14 every wave of the receipt is ELIGIBLE; a wave without a finite value is UNRESOLVED (counted, printed, never dropped); over 5 pct
        unresolved = INCOMPLETE; the bar is recomputed with unresolved waves set to the worst observed wave, printed beside.
  03-18 two modes from the ledger links, never a caller time: AT_REGISTRATION (tries stamped before the result's PREREG row) and CURRENT
        (every try up to the newest ledger row, the batch included); the verdict uses CURRENT; AT_REGISTRATION is printed beside.
  03-19 beside the whole-wave bootstrap, a whole-DAY block bootstrap: the verdict uses the more conservative t (mean / the larger se).
Reused, never copied: fairness_bar v1's read_tries (the census readers), dsr, sr_star, holm, waves_needed, utc_key; labcore waves, ids.
  bar(result_receipt_path, prereg_ask_id, settings=None, tries=None (tests only: planted ledgers), roster=None, now_utc=None) -> dict"""
import math, os, re, sys
import datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
TOOLS = os.path.realpath(os.path.join(HERE, '..'))
for p in (TOOLS, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)
from labcore import ids, waves as LW                  # noqa: E402  (the ONE wave module)
import fairness_bar as V1                             # noqa: E402  (readers and formulas, version 1, not copied)
import make_families_v2 as MF                         # noqa: E402  (the ONE classifier, SCOUT)

DEFAULT_SETTINGS = dict(V1.DEFAULT_SETTINGS, flips=2000, day_boot=2000, unresolved_max=0.05, sr_star_pct=95.0,
                        families_path=os.path.join(HERE, 'FAMILIES_V2.tsv'))


def family_rows(path):
    """FAMILIES_V2.tsv -> [(pattern, source, family, why)] in file order (the table make_families_v2 wrote)"""
    out = []; head = None
    for l in open(path, encoding='utf-8'):
        if l.startswith('#') or not l.strip():
            continue
        f = l.rstrip('\n').split('\t')
        if head is None:
            head = f; continue
        r = dict(zip(head, f)); out.append((r['pattern'], r['source'], r['family'], r.get('why', '')))
    return out


def families_of(t, rows, exempt):
    if '_typed_families' in t:                                                   # OUTSIDE A30-F02 (Rule 2): typed rows are authoritative
        known = {r[2] for r in rows}
        if not t.get('_typed_source_sha16') or any(f not in known for f in t['_typed_families']):
            raise ValueError('typed family is not in the approved map: refused')
        fams = list(t['_typed_families'])
        if t.get('_typed_legacy_parent'):                                          # an untyped legacy parent: its name families are inherited
            pid, ptext = t['_typed_legacy_parent']
            fams += [f for f in MF.family_of_all(ptext, 'ledger', rows, try_id=pid, exempt=exempt) if f != 'UNMAPPED']
        return list(dict.fromkeys(fams))
    return MF.family_of_all(t.get('text', ''), t['source'], rows, try_id=t.get('ask_id'), exempt=exempt)


def census_v2(tries, rows, exempt, upto_utc, before=False):
    """{family: [tries]} of the tries stamped at or before upto_utc (strictly before when before=True), every matching family; UNMAPPED
    listed as its own family"""
    out = {}
    for t in tries:
        if (t['try_utc'] >= upto_utc) if before else (t['try_utc'] > upto_utc):
            continue
        for f in families_of(t, rows, exempt):
            out.setdefault(f, []).append(t)
    return out


# ---------------------------------------------------------------- the receipt and its waves (03-11, 03-14)
def read_receipt(path, gap_s=1800):
    """the per-wave receipt: wave_id, value, month, day, n_fires, fires ('coin@t_unix_s;...'); the waves are RECOUNTED from the fires"""
    text = open(path, encoding='utf-8').read()
    want = ids.sha16_file(os.path.join(TOOLS, 'labcore', 'waves.py'))          # C04-02 / LAB4 M1: the receipt names the wave module
    m = re.search(r'^# wave_module_sha16=([0-9a-f]{16})$', text, re.M)
    if not m or m.group(1) != want:
        raise ValueError('%s: wave_module_sha16 %s, labcore.waves is %s: refused (C04-02; the waves are also recounted below)' % (
            path, m.group(1) if m else 'missing', want))
    rows = [l.rstrip('\n').split('\t') for l in text.splitlines() if l.strip() and not l.startswith('#')]
    head, body = rows[0], rows[1:]
    need = ('wave_id', 'value', 'month', 'day', 'n_fires', 'fires')
    miss = [h for h in need if h not in head]
    if miss:
        raise ValueError('%s: columns %s missing: refused (03-11: each wave carries its fires)' % (path, miss))
    ix = {h: head.index(h) for h in need}
    W = []
    for i, r in enumerate(body, 2):
        if len(r) != len(head):
            raise ValueError('%s line %d: %d fields, header %d: refused' % (path, i, len(r), len(head)))
        fires = []
        for x in [x for x in r[ix['fires']].split(';') if x]:
            c, t = x.rsplit('@', 1); fires.append((c, float(t)))
        v = r[ix['value']].strip()
        W.append(dict(wave_id=r[ix['wave_id']], value=float(v) if v not in ('', 'nan', 'NaN', 'NA') else float('nan'),
                      month=r[ix['month']], day=r[ix['day']], n_fires=int(r[ix['n_fires']]), fires=fires))
    wid = [w['wave_id'] for w in W]
    if len(wid) != len(set(wid)):
        raise ValueError('%s: a wave id twice: refused (03-11)' % path)
    for w in W:
        times = [t for _, t in w['fires']]
        if not np.isfinite(times).all() or times != sorted(times):
            raise ValueError('%s: nonfinite or unsorted fire times inside wave %s: refused' % (path, w['wave_id']))
        if w['n_fires'] != len(w['fires']):
            raise ValueError('%s wave %s: n_fires %d, fires listed %d: refused (03-11)' % (path, w['wave_id'], w['n_fires'], len(w['fires'])))
        if not w['fires']:
            raise ValueError('%s wave %s: no fires: refused (03-11)' % (path, w['wave_id']))
    keys = [(c, t) for w in W for c, t in w['fires']]
    if len(keys) != len(set(keys)):
        raise ValueError('%s: a fire in two waves (or twice): refused (03-11)' % path)
    starts = [min(t for _, t in w['fires']) for w in W]
    # The day-block inference uses the UTC day of the wave's first fire.
    # Metadata cannot invent independent days or a different scoring month.
    for w, start in zip(W, starts):
        day = dt.datetime.fromtimestamp(start, dt.timezone.utc).strftime('%Y%m%d')
        if w['day'] != day or w['month'] != day[:6]:
            raise ValueError('%s: receipt day/month differs from the first fire UTC date: refused' % path)

    if any(b < a for a, b in zip(starts, starts[1:])):
        raise ValueError('%s: waves are not in time order: refused (03-11)' % path)
    owner = np.array([k for k, w in enumerate(W) for _ in w['fires']]); tt = np.array([t for w in W for _, t in w['fires']])
    re_w = LW.waves(tt, gap_s)
    pairs = set(zip(owner.tolist(), re_w.tolist()))
    if len(pairs) != len(W) or len({a for a, _ in pairs}) != len(W) or len({b for _, b in pairs}) != len(W):
        raise ValueError('%s: the receipt has %d waves, labcore.waves recounts %d from its fires (gap %d s): refused (03-11)' % (
            path, len(W), len(set(re_w.tolist())), gap_s))
    return W


# ---------------------------------------------------------------- statistics (03-12, 03-13, 03-19)
def sharpe(v):
    v = v[np.isfinite(v)]
    if len(v) < 2:
        return 0.0
    sd = v.std(ddof=1)
    return float(v.mean() / sd) if sd > 0 else 0.0


def sr_star_flips(series, universe, flips, pct, seed):
    """series: [ {wave_id: value} ] of the family's tries with receipts (the result first); one random sign per wave id of the universe,
    shared by every try; -> the pct-th percentile of max Sharpe over the tries"""
    if isinstance(flips, (bool, np.bool_)) or not isinstance(flips, (int, np.integer)) or flips < 1 or not 0 < pct < 100:
        raise ValueError('flips must be a positive integer and the percentile inside (0, 100): got %r, %r (C04-03)' % (flips, pct))
    rng = np.random.default_rng(seed); u = {w: i for i, w in enumerate(universe)}
    mats = []
    for s in series:
        idx = np.array([u[w] for w in s], int); val = np.array([s[w] for w in s], float); ok = np.isfinite(val)
        mats.append((idx[ok], val[ok]))
    best = np.empty(flips)
    for b in range(flips):
        sign = rng.choice((-1.0, 1.0), len(universe))
        best[b] = max(sharpe(val * sign[idx]) for idx, val in mats)
    return float(np.percentile(best, pct))


def block_t(v, days, rng, B):
    """t with the se of a whole-wave bootstrap and of a whole-day block bootstrap; -> (t_wave_boot, t_day_block)"""
    v = np.asarray(v, float); m = v.mean(); n = len(v)
    se_w = np.std([v[rng.integers(0, n, n)].mean() for _ in range(B)])
    ud, inv = np.unique(np.asarray(days), return_inverse=True); k = len(ud)
    groups = [v[inv == j] for j in range(k)]
    se_d = np.std([np.concatenate([groups[j] for j in rng.integers(0, k, k)]).mean() for _ in range(B)])
    return (float(m / se_w) if se_w > 0 else 0.0), (float(m / se_d) if se_d > 0 else 0.0)


def _p_one_sided(t, T):
    from scipy import stats
    return float(stats.t.sf(t, max(T - 1, 1)))


def _score(vals, days, n_counted, series, universe, p_roster, s):
    """the bar on finite values: SR* = max(formula on n_counted, joint-flip luck bar); t = the more conservative of iid, wave and day-block"""
    T = len(vals); sr = sharpe(vals); skew, kurt = V1._moments(vals)
    s_formula = V1.sr_star(max(n_counted, 1), 1.0 / T if T else 1.0)
    s_flip = sr_star_flips(series, universe, s['flips'], s['sr_star_pct'], s['seed']) if series else 0.0
    s0 = max(s_formula, s_flip)
    den = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    den = math.sqrt(den) if den > 1e-12 else 1e-6
    from scipy import stats
    dsr_p = float(stats.norm.cdf((sr - s0) * math.sqrt(max(T - 1, 0)) / den))
    rng = np.random.default_rng(s['seed'])
    t_iid = sr * math.sqrt(T)
    t_w, t_d = block_t(vals, days, rng, s['day_boot']) if T >= 2 else (0.0, 0.0)
    t_cons = min(t_iid, t_w, t_d)
    p = _p_one_sided(t_cons, T)
    missing = sum(1 for x in p_roster if x is None)
    if not p_roster:
        adj = float(min(1.0, p * max(n_counted, 1))); mult = 'ONE TRY (no other try in the family)' if n_counted <= 1 else 'BONFERRONI (%d tries, no roster)' % n_counted
    elif missing == 0:
        adj = float(V1.holm(list(p_roster) + [p])[-1]); mult = 'HOLM (roster complete)'
    else:
        adj = float(min(1.0, p * max(n_counted, 1))); mult = 'BONFERRONI (%d p-values missing)' % missing
    return dict(waves=T, sr_wave=sr, skew=skew, kurt_pearson=kurt, sr_star=s0, sr_star_formula=s_formula, sr_star_flips=s_flip,
                dsr_p=dsr_p, t_iid=t_iid, t_wave_boot=t_w, t_day_block=t_d, t_used=t_cons, p_used=p, adj_p=adj, multiplicity=mult)


def align_receipt_waves(receipts, gap_s):
    """One shared partition from all declared fires; labels are not identities.
    Refuse a cohort that would merge multiple separately valued waves of one try:
    its values must be rebuilt to the shared unit with an explicit aggregation rule.
    """
    fires = sorted({(coin, t) for rows in receipts for w in rows for coin, t in w['fires']}, key=lambda x: (x[1], x[0]))
    groups = LW.waves(np.array([t for _, t in fires]), gap_s)
    key = {f: int(g) for f, g in zip(fires, groups)}
    out = []
    for rows in receipts:
        seen = set(); aligned = []
        for w in rows:
            ids = {key[f] for f in w['fires']}
            if len(ids) != 1 or next(iter(ids)) in seen:
                raise ValueError('receipt values are not on the shared wave partition: rebuild/refuse')
            group = next(iter(ids)); seen.add(group)
            aligned.append(dict(w, wave_id='shared_%012d' % group))
        out.append(aligned)
    return out


def _audit_sha(value):
    import hashlib, json
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()[:16]


def _bar_one(result_receipt_path, prereg_ask_id, settings=None, tries=None, roster=None, now_utc=None, family=None):
    """the fairness bar of one result, census built here (03-10, 03-18); tries= only for planted ledgers in tests; roster = {ask_id:
    per-wave receipt path} of the family's tries that have one (others are missing p-values)"""
    s = dict(DEFAULT_SETTINGS, **(settings or {}))
    rows = family_rows(s['families_path']); exempt = MF.exempt_ids()
    tries = V1.read_tries() if tries is None else tries
    pre = [t for t in tries if t.get('ask_id') == prereg_ask_id]
    if len(pre) != 1:
        raise ValueError('PREREG %s: %d ledger tries carry it (exactly one needed): refused (03-18)' % (prereg_ask_id, len(pre)))
    pre = pre[0]; fams = [f for f in families_of(pre, rows, exempt) if f != 'UNMAPPED']
    if not fams:
        raise ValueError('PREREG %s maps to no family: refused (03-10)' % prereg_ask_id)
    newest = max(t['try_utc'] for t in tries); now_utc = max(now_utc or newest, newest)   # C04-01: CURRENT is never backdated
    cur = census_v2(tries, rows, exempt, now_utc); reg = census_v2(tries, rows, exempt, pre['try_utc'], before=True)
    W = read_receipt(result_receipt_path, s['gap_s'])
    counted = {f: len(cur.get(f, [])) for f in fams}; fam = family or max(fams, key=lambda f: counted[f])
    if fam not in fams:
        raise ValueError('family is not one of the result families: refused')
    other = {}
    for t in cur.get(fam, []):
        rp = (roster or {}).get(t.get('ask_id'))
        if t is not pre and rp:
            other[t['ask_id']] = read_receipt(rp, s['gap_s'])
    aligned = align_receipt_waves([W] + list(other.values()), s['gap_s'])
    W = aligned[0]
    other = dict(zip(other, aligned[1:]))
    vals_all = np.array([w['value'] for w in W]); ok = np.isfinite(vals_all); n_unres = int((~ok).sum())
    vals = vals_all[ok]; days = [w['day'] for w, k in zip(W, ok) if k]
    result_series = {w['wave_id']: w['value'] for w in W}
    universe = sorted({w['wave_id'] for w in W}); series = [result_series]; p_roster = []
    for t in cur.get(fam, []):
        if t is pre:
            continue
        rp = (roster or {}).get(t.get('ask_id'))
        if rp:
            tw = other[t['ask_id']]; ts = {w['wave_id']: w['value'] for w in tw}; series.append(ts)
            universe = sorted(set(universe) | set(ts)); v = np.array([x for x in ts.values() if np.isfinite(x)])
            p_roster.append(_p_one_sided(sharpe(v) * math.sqrt(len(v)), len(v)) if len(v) > 1 else 1.0)
        else:
            p_roster.append(None)
    n_cur = counted[fam]; n_reg = len(reg.get(fam, []))
    sc = _score(vals, days, n_cur, series, universe, p_roster, s)
    worst = vals_all.copy(); worst[~ok] = np.nanmin(vals_all) if ok.any() else 0.0
    sc_worst = _score(worst, [w['day'] for w in W], n_cur, [{w['wave_id']: x for w, x in zip(W, worst)}] + series[1:], universe, p_roster, s)
    sc_reg = _score(vals, days, max(n_reg, 1), series, universe, p_roster[:max(n_reg - 1, 0)], s)
    unmapped = cur.get('UNMAPPED', [])
    share = n_unres / float(len(W)) if W else 1.0
    if unmapped or share > s['unresolved_max']:
        verdict = 'INCOMPLETE'
    elif sc['waves'] < s['min_waves']:
        verdict = 'UNRELIABLE'
    else:
        verdict = 'PASS' if (sc['dsr_p'] >= s['dsr_bar'] and sc['t_used'] >= s['t_bar'] and sc['adj_p'] < s['holm_alpha']) else 'FAIL'
    r = dict(sc, family=fam, families=fams, mode='CURRENT', tries_counted=n_cur, tries_at_registration=n_reg, eligible_waves=len(W),
             unresolved_waves=n_unres, unresolved_share=share, unmapped=len(unmapped), verdict=verdict,
             worst_case=dict(dsr_p=sc_worst['dsr_p'], t_used=sc_worst['t_used'], adj_p=sc_worst['adj_p']),
             at_registration=dict(dsr_p=sc_reg['dsr_p'], adj_p=sc_reg['adj_p'], tries=n_reg),
             result_sha16=ids.sha16_file(result_receipt_path), prereg_ask_id=prereg_ask_id, prereg_utc=pre['try_utc'], census_upto=now_utc,
             known_at_utc=now_utc, wave_module_sha16=ids.sha16_file(os.path.join(TOOLS, 'labcore', 'waves.py')))
    r['line'] = ('FAIR BAR %s (CURRENT): tries %d (at registration %d), waves %d eligible / %d unresolved, SR/wave %.3f, SR* %.3f '
                 '(formula %.3f, flips %.3f), DSR %.3f, t %.2f (iid %.2f, wave %.2f, day %.2f; bar %.1f), %s p %.4f, worst-case DSR %.3f, '
                 'UNMAPPED %d, %s' % (fam, n_cur, n_reg, len(W), n_unres, sc['sr_wave'], sc['sr_star'], sc['sr_star_formula'],
                                      sc['sr_star_flips'], sc['dsr_p'], sc['t_used'], sc['t_iid'], sc['t_wave_boot'], sc['t_day_block'],
                                      s['t_bar'], sc['multiplicity'], sc['adj_p'], sc_worst['dsr_p'], len(unmapped), verdict))
    partition = {}
    for receipt_rows in [W] + list(other.values()):
        for wave in receipt_rows:
            partition.setdefault(wave['wave_id'], set()).update(wave['fires'])
    receipt_hashes = {prereg_ask_id: ids.sha16_file(result_receipt_path)}
    for try_id in other:
        receipt_hashes[try_id] = ids.sha16_file(roster[try_id])
    r['evidence'] = dict(
        schema='FAIRNESS_INPUT_IDENTITY_V1',
        census_sha16=_audit_sha(sorted(tries, key=lambda t: (t['source'], t['ask_id']))),
        typed_source_sha16s=sorted({t['_typed_source_sha16'] for t in tries if t.get('_typed_source_sha16')}),
        typing_cut_sha16s=sorted({t['_legacy_by_cut'] for t in tries if t.get('_legacy_by_cut')}),     # A36-F01 migration record
        family_map_sha16=ids.sha16_file(s['families_path']),
        settings_sha16=_audit_sha(s),
        roster_sha16s=receipt_hashes,
        shared_partition_sha16=_audit_sha([(k, sorted(v)) for k, v in sorted(partition.items())]))
    return r


def bar(result_receipt_path, prereg_ask_id, settings=None, tries=None, roster=None, now_utc=None):
    """Every matching family must clear its own full bar; freeze one census for this call."""
    tries = V1.read_tries() if tries is None else tries
    first = _bar_one(result_receipt_path, prereg_ask_id, settings, tries, roster, now_utc)
    if len(first['families']) == 1:
        return first
    all_results = {first['family']: first}
    for fam in first['families']:
        if fam not in all_results:
            all_results[fam] = _bar_one(result_receipt_path, prereg_ask_id, settings, tries, roster, now_utc, family=fam)
    r = dict(first)
    r['family_results'] = all_results
    r['sr_star'] = max(x['sr_star'] for x in all_results.values())
    r['dsr_p'] = min(x['dsr_p'] for x in all_results.values())
    r['adj_p'] = max(x['adj_p'] for x in all_results.values())
    verdicts = {x['verdict'] for x in all_results.values()}
    r['verdict'] = ('INCOMPLETE' if 'INCOMPLETE' in verdicts else
                    'UNRELIABLE' if 'UNRELIABLE' in verdicts else
                    'PASS' if verdicts == {'PASS'} else 'FAIL')
    r['family'] = 'ALL_MATCHING'
    r['line'] = 'FAIR BAR ALL_MATCHING: ' + '; '.join(x['line'] for x in all_results.values())
    return r
