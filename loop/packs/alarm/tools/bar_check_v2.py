#!/usr/bin/env python3
"""bar_check_v2.py (SCO-A182 for SCOUT; PLAYGROUND, TEST). The ONE computation of the PROOF_RULES_V2 bars (34192fee92adf4f5) and of the
SERIES_V2.tsv rows they read: both use the same ASSESS.tsv parser, so a SERIES_V2 number and a bar number are never computed two ways.
  bars  --series SERIES_V2.tsv [--config SERIES_V2_CONFIG.json]      B1 to B4 (B5 is a person's check), the kill rule; exit 0, 3 on MISMATCH
  bars  --block L12,C06,... | <file of ids> [--reasoning A.tsv,B.tsv] [--heldout-same k]   C216, PROOF_RUNS_V1 section 3: only the
        block's RUN rows; halves by block order among memory runs; B1, B2a-c, B3a-d, B4 each with measure, value, bar; exact permutation
        over C(n_L + n_C, n_C) splits (210 for 6 vs 4); B3c reads blind-scoring result files, B3d takes the orchestrator's count only
  row   --runf <run folder> --series SERIES_V2.tsv [--config F] [--write]   the RUN row of one run from its ASSESS.tsv (curator V2)
  look  --run-id L03 --series F --by-month a,b,c,d --t-pooled x --receipt "<file sha16>" [--write]   the LOOK row (SCOUT, after the one look)
Bars as PROOF_RULES_V2 says (runs = SERIES_V2 rows kind RUN, the measured block; numbers re-read from each run's ASSESS.tsv):
 B1 5 consecutive runs (either arm, by utc_launch) with hand 0, tool_stops 0, blindfold 0 (ASSESS B1_CLEAN) and reproducible (every
    number of every item in both ASSESS.tsv and ASSESS_REPRO.tsv equal; ASSESSOR and TIME rows excluded; no REPRO file = not shown).
 B2 arm L runs 1-10: (a) best round beats round 1 at 15 min (best_round > 1 and best_lead15 > r1_lead15) in at least 6 of 10;
    (b) mean best margin over the yardstick, L6-10 minus L1-5, at least 2; (c) mean forecast abs error L6-10 below L1-5, and the
    predicted better state matches the state split tool's in at least 6 of 10 (READING: the rule's words "6 of 10 L runs 6-10" cannot
    hold for 5 runs; computed over L runs 1-10, the best round's match; the L6-10 count is printed beside it; NA counts as no).
 B3 over the block (at least 10 runs per arm): mean margin L minus C at least 2, AND mean repeated mistakes (M1) L below C, AND a
    one-sided permutation test of the margin difference across runs (labels L/C shuffled; exact when at most 200,000 splits, else
    100,000 random splits with seed 20261107) at p below 0.10.
 B4 at least 3 runs with rediscovery no (wave overlap below 50 with any earlier alarm) whose LOOK row beats the yardstick's look figure
    month by month in at least 3 of 4 months with pooled t at least 2 (yardstick.look_lead15_by_month in the orchestrator-only file named by config yardstick_sepmar_file, C225; null: PENDING).
 KILL after 10 L runs: B2(b) and B3 both fail -> the learning design is changed (PROOF_RULES_V2 kill rule).
A run whose best round was not graded (MISSING) has no margin: it is left out of the margin means and counted in the line."""
import argparse, csv, itertools, json, os, random, re, shutil, sys
from datetime import datetime, timezone
LSD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # C90: the series folder on any host (was a VM-only ~/mnt path)
COLS = ['kind', 'run_id', 'arm', 'n', 'task', 'utc_launch', 'utc_row', 'idea_best', 'best_round', 'r1_lead15', 'best_lead15', 'yard_lead15',
        'best_margin', 'best_months_pass', 'best_t15', 'fc_mean_abs_err', 'fc_best_state_match', 'M1_repeat', 'hand', 'tool_stops',
        'blindfold', 'repro', 'clean', 'novelty_max_overlap', 'rediscovery', 'look_lead15_by_month', 'look_t_pooled', 'runf', 'receipts']
NUM = re.compile(r'[-+]?\d+(?:\.\d+)?')
VM_RX = re.compile(r'^/sessions/[^/]+/mnt/')


def host_path(p, series=None):
    """C90 (M043): SERIES_V2 rows L01-L05 hold VM paths (/sessions/<id>/mnt/<path under the home>) and L06 on hold paths relative to the
    series folder; both resolve to this host's run folder."""
    if VM_RX.match(p):
        return os.path.join(os.path.expanduser('~'), VM_RX.sub('', p))
    if not os.path.isabs(p) and series:
        return os.path.join(os.path.dirname(os.path.abspath(series)), p)
    return p


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def tsv(p):
    return list(csv.DictReader(open(p, newline='', encoding='utf-8'), delimiter='\t')) if os.path.isfile(p) else []


def kv(value):
    """'lead15 12.36 waves 633 word PASS' -> {'lead15': '12.36', ...}"""
    t = (value or '').replace(';', ' ').split()
    d = {}
    for i in range(len(t) - 1):          # C99: every token maps to the next one (first wins), so free text inside a value
        d.setdefault(t[i], t[i + 1])     # ('100 (by DEF nesting ...) rediscovery yes') no longer shifts the pairs
    return d


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def assess(path):
    rows = tsv(path)
    return {r['item']: r.get('value', '') for r in rows if r.get('item')}


def run_numbers(runf):
    """every number a SERIES_V2 RUN row and the bars need, from the run's ASSESS.tsv (one parser)"""
    A = assess(os.path.join(runf, 'ASSESS.tsv'))
    if not A:
        return None
    m8, m9, m11, m12, m13, b1 = (kv(A.get(k)) for k in ('M8_YARD', 'M9_WITHIN', 'M11_FORECAST', 'M12_NOVELTY', 'M13_ARM', 'B1_CLEAN'))
    m1 = NUM.findall(A.get('M1', ''))
    rounds = {}
    for k in sorted(x for x in A if re.fullmatch(r'M11_FORECAST_R\d+[A-Z]*', x)):   # C110: R3B, R3P ... count too (C02 had R3B)
        rounds[k[len('M11_FORECAST_'):]] = kv(A.get(k))
    br = re.fullmatch(r'R?(\d)', m8.get('best_round') or '')     # C99: 'R1' (L10) and '1' both mean round 1
    best = int(br.group(1)) if br else None
    if (m8.get('best_round') or '').upper().startswith('R3P'):
        # C67: the placebo R3P is never the run's best alarm; best = the better of R1 and R3 (from M7 rows), margin against the same yardstick
        c = [(k, kv(A.get('M7_R%d' % k))) for k in (1, 3)]
        c = [(k, m) for k, m in c if f(m.get('lead15')) is not None]
        if c:
            k, m = max(c, key=lambda x: f(x[1].get('lead15'))); y = f(m8.get('yard15'))
            m8 = dict(m8, best_lead15=m.get('lead15'), best_months_pass=m.get('months_pass'), best_t15=m.get('t15'),
                      margin=('%.2f' % (f(m.get('lead15')) - y)) if y is not None else None)
            best = k
    return {'arm': m13.get('arm'), 'run_id': m13.get('run_id'), 'task': m13.get('task'), 'utc_launch': m13.get('launch_utc'),
            'best_round': best, 'r1_lead15': f(m9.get('r1_lead15')), 'best_lead15': f(m8.get('best_lead15')), 'yard_lead15': f(m8.get('yard15')),
            'best_margin': f(m8.get('margin')), 'best_months_pass': f(m8.get('best_months_pass')), 'best_t15': f(m8.get('best_t15')),
            'fc_mean_abs_err': f(m11.get('mean_abs_err')), 'fc_best_state_match': m11.get('best_round_state_match', 'NA'),
            'M1_repeat': f(m1[0]) if m1 else None, 'hand': f(b1.get('hand')), 'tool_stops': f(b1.get('tool_stops')),
            'blindfold': f(b1.get('blindfold')), 'novelty_max_overlap': f(m12.get('max_overlap_pct')), 'rediscovery': m12.get('rediscovery'),
            'rounds': rounds}


def repro(runf):
    a, b = assess(os.path.join(runf, 'ASSESS.tsv')), assess(os.path.join(runf, 'ASSESS_REPRO.tsv'))
    if not b:
        return 'NOT_RUN', []
    diff = [k for k in a if k not in ('ASSESSOR', 'TIME') and (k not in b or NUM.findall(a[k]) != NUM.findall(b[k]))]
    return ('yes' if not diff else 'no'), diff


def check_forecast_math(n):
    """abs_err of each round = |pred - actual| (to 0.01), mean_abs_err = mean of them: the assessor's typing is checked here"""
    errs, bad = [], []
    for k, r in n['rounds'].items():
        p, x, e = f(r.get('pred_lead15')), f(r.get('actual_lead15')), f(r.get('abs_err'))
        if p is None or x is None:
            continue
        if e is None or abs(abs(p - x) - e) > 0.011:
            bad.append('%s abs_err %s != |%s - %s|' % (k, r.get('abs_err'), p, x))
        errs.append(abs(p - x))
    if errs and n['fc_mean_abs_err'] is not None and abs(sum(errs) / len(errs) - n['fc_mean_abs_err']) > 0.011:
        bad.append('mean_abs_err %s != %.4f' % (n['fc_mean_abs_err'], sum(errs) / len(errs)))
    if n['best_lead15'] is not None and n['yard_lead15'] is not None and n['best_margin'] is not None and \
            abs(n['best_lead15'] - n['yard_lead15'] - n['best_margin']) > 0.011:
        bad.append('margin %s != %s - %s' % (n['best_margin'], n['best_lead15'], n['yard_lead15']))
    return bad


def fmt(x):
    if x is None:
        return 'MISSING'
    if isinstance(x, float):
        return ('%.4f' % x).rstrip('0').rstrip('.') if x != int(x) else str(int(x))
    return str(x)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else None


def perm_p(L, C, seed=20261107, exact_max=200000, draws=100000):
    """one-sided p of mean(L) - mean(C) under random relabelling of the pooled runs"""
    allv = L + C; nL = len(L); obs = mean(L) - mean(C); tot = sum(allv)
    ncomb = 1
    for i in range(nL):
        ncomb = ncomb * (len(allv) - i) // (i + 1)
    ge = 0
    if ncomb <= exact_max:
        for idx in itertools.combinations(range(len(allv)), nL):
            sL = sum(allv[i] for i in idx)
            if sL / nL - (tot - sL) / len(C) >= obs - 1e-12:
                ge += 1
        return ge / ncomb, 'exact %d splits' % ncomb
    rng = random.Random(seed)
    for _ in range(draws):
        s = rng.sample(allv, len(allv)); sL = sum(s[:nL])
        if sL / nL - (tot - sL) / len(C) >= obs - 1e-12:
            ge += 1
    return (ge + 1) / (draws + 1), 'random %d splits seed %d' % (draws, seed)


def load_cfg(p):
    return json.load(open(p, encoding='utf-8')) if p and os.path.isfile(p) else {}


def sepmar_look(cfg):
    """C225: the pooled Sep-Mar yardstick (window includes held-out Feb-Mar) lives in an orchestrator-only file named by config
    yardstick_sepmar_file (@FR@ = the forensics folder above the series folder); B4, an orchestrator look, reads look_lead15_by_month only"""
    fr = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(LSD))))
    p = ((cfg.get('yardstick_sepmar_file') or {}).get('path') or '').replace('@FR@', fr)
    return (json.load(open(p, encoding='utf-8')).get('yardstick') or {}).get('look_lead15_by_month') if p and os.path.isfile(p) else None


def load_runs(runs, series):
    """C216: the one loader of RUN rows for bars and bars --block (numbers re-read from each run's ASSESS.tsv, row vs ASSESS checked)"""
    mism, R = [], []
    for r in runs:
        runf = host_path(r['runf'], series)
        n = run_numbers(runf)
        if n is None:
            mism.append('%s: no ASSESS.tsv in %s' % (r['run_id'], runf)); continue
        n['repro'], n['repro_diff'] = repro(runf)
        n['clean'] = 'yes' if (n['hand'] == 0 and n['tool_stops'] == 0 and n['blindfold'] == 0 and n['repro'] == 'yes') else 'no'
        n['n'] = int(r['n']); n['row'] = r; n['runf'] = runf
        for k in ('best_round', 'r1_lead15', 'best_lead15', 'best_margin', 'fc_mean_abs_err', 'fc_best_state_match', 'M1_repeat', 'hand',
                  'tool_stops', 'blindfold', 'novelty_max_overlap', 'rediscovery'):
            if fmt(n[k]) != fmt(f(r.get(k)) if f(r.get(k)) is not None else r.get(k) if r.get(k) not in ('', None) else None):
                mism.append('%s %s: SERIES_V2 %s, ASSESS %s' % (r['run_id'], k, r.get(k), fmt(n[k])))
        for b in check_forecast_math(n):
            mism.append('%s %s' % (r['run_id'], b))
        R.append(n)
    return R, mism


def cmd_bars(a):
    if a.block:
        return cmd_bars_block(a)
    cfg = load_cfg(a.config)
    rows = tsv(a.series)
    runs = sorted([r for r in rows if r.get('kind') == 'RUN'], key=lambda r: (r.get('utc_launch', ''), r.get('run_id', '')))
    looks = {r['run_id']: r for r in rows if r.get('kind') == 'LOOK'}
    R, mism = load_runs(runs, a.series)
    out = []
    # B1
    best, cur, streak = [], [], []
    for n in R:
        if n['clean'] == 'yes':
            cur.append(n['row']['run_id'])
            if len(cur) > len(best):
                best = list(cur)
        else:
            cur = []
    b1 = len(best) >= 5
    out.append('B1 %s: longest clean streak %d (%s); runs not clean: %s' % ('PASS' if b1 else 'FAIL' if len(R) >= 5 else 'PENDING', len(best),
               ','.join(best) or '-', ', '.join('%s(hand %s stops %s blind %s repro %s)' % (n['row']['run_id'], fmt(n['hand']), fmt(n['tool_stops']),
               fmt(n['blindfold']), n['repro']) for n in R if n['clean'] != 'yes') or 'none'))
    Ls = sorted([n for n in R if n['arm'] == 'L'], key=lambda n: n['n']); Cs = [n for n in R if n['arm'] == 'C']
    L10 = Ls[:10]; first, last = [n for n in L10 if n['n'] <= 5], [n for n in L10 if 6 <= n['n'] <= 10]
    full = len(L10) >= 10
    a_cnt = sum(1 for n in L10 if n['best_round'] and n['best_round'] > 1 and n['best_lead15'] is not None and n['r1_lead15'] is not None
                and n['best_lead15'] > n['r1_lead15'])
    a_ok = a_cnt >= 6
    m1, m2 = mean([n['best_margin'] for n in first]), mean([n['best_margin'] for n in last])
    b_ok = m1 is not None and m2 is not None and m2 - m1 >= 2
    e1, e2 = mean([n['fc_mean_abs_err'] for n in first]), mean([n['fc_mean_abs_err'] for n in last])
    s_all = sum(1 for n in L10 if n['fc_best_state_match'] == 'yes'); s_late = sum(1 for n in last if n['fc_best_state_match'] == 'yes')
    c_ok = e1 is not None and e2 is not None and e2 < e1 and s_all >= 6
    word = lambda ok: ('PASS' if ok else 'FAIL') if full else 'PENDING'
    out.append('B2 %s: L runs %d of 10 needed' % (word(a_ok and b_ok and c_ok), len(L10)))
    out.append('  B2a %s: best round beats round 1 at 15 min in %d of %d L runs (needs 6 of 10)' % (word(a_ok), a_cnt, len(L10)))
    out.append('  B2b %s: mean best margin L6-10 %s minus L1-5 %s = %s (needs >= 2; margins left out: %d)' % (word(b_ok), fmt(m2), fmt(m1),
               fmt(m2 - m1) if (m1 is not None and m2 is not None) else 'MISSING', sum(1 for n in L10 if n['best_margin'] is None)))
    out.append('  B2c %s: mean forecast abs error L6-10 %s vs L1-5 %s (below needed); better state match %d of %d L runs 1-10 (needs 6; READING, the rule says "6 of 10 L runs 6-10"); L6-10 alone %d of %d' % (
        word(c_ok), fmt(e2), fmt(e1), s_all, len(L10), s_late, len(last)))
    # B3
    mL = [n['best_margin'] for n in R if n['arm'] == 'L' and n['best_margin'] is not None]
    mC = [n['best_margin'] for n in Cs if n['best_margin'] is not None]
    rL, rC = mean([n['M1_repeat'] for n in R if n['arm'] == 'L']), mean([n['M1_repeat'] for n in Cs])
    full3 = sum(1 for n in R if n['arm'] == 'L') >= 10 and len(Cs) >= 10
    if mL and mC:
        p, how = perm_p(mL, mC); d = mean(mL) - mean(mC)
    else:
        p, how, d = None, 'no margins', None
    b3 = d is not None and d >= 2 and rL is not None and rC is not None and rL < rC and p is not None and p < 0.10
    out.append('B3 %s: mean margin L %s (n %d) minus C %s (n %d) = %s (needs >= 2); repeated mistakes per run L %s vs C %s (L fewer needed); permutation p %s (%s; needs < 0.10)' % (
        ('PASS' if b3 else 'FAIL') if full3 else 'PENDING', fmt(mean(mL)), len(mL), fmt(mean(mC)), len(mC), fmt(d), fmt(rL), fmt(rC),
        ('%.6g' % p) if p is not None else 'MISSING', how))
    # B4
    yl = sepmar_look(cfg)   # C225
    if not yl:
        out.append('B4 PENDING NO_YARDSTICK_LOOK: config yardstick.look_lead15_by_month is not filled; LOOK rows %d' % len(looks))
        b4 = False
    else:
        q = []
        for n in R:
            lk = looks.get(n['row']['run_id'])
            if n['rediscovery'] != 'no' or not lk:
                continue
            bm = [f(x) for x in lk['look_lead15_by_month'].split(',')]
            beats = sum(1 for x, y in zip(bm, yl) if x is not None and x > y)
            t = f(lk['look_t_pooled'])
            if beats >= 3 and t is not None and t >= 2:
                q.append((n['row']['run_id'], beats, t, n['novelty_max_overlap']))
        b4 = len(q) >= 3
        out.append('B4 %s: distinct alarms holding on the look window %d (needs 3): %s; then the single best is opened once on the never-seen window by the owner' % (
            'PASS' if b4 else 'FAIL' if full3 else 'PENDING', len(q), ', '.join('%s %d/4 t %s overlap %s' % (r, b, fmt(t), fmt(o)) for r, b, t, o in q) or 'none'))
    out.append('B5 NOT COMPUTED: a fresh agent in a fresh account repeats one run from the released documents, and the outside reviewer passes the method')
    kill = len(Ls) >= 10 and len(Cs) >= 10 and not b_ok and not b3
    out.append('KILL_RULE %s' % ('TRIGGER: after 10 L runs B2(b) and B3 both fail; change the learning design (pro-practice-first plan), new block' if kill else 'no'))
    out.append('BAR %s (B1 to B4 by this tool; B5 by people)' % ('PASS' if (b1 and full and a_ok and b_ok and c_ok and b3 and b4) else 'NOT YET'))
    for m in mism:
        out.append('MISMATCH ' + m)
    print('\n'.join(out))
    return 3 if mism else 0


RID = re.compile(r'^[LC]\d+$')
HREP = re.compile(r'failures_log[_ ]repeats\s+(\d+)', re.I)


def parse_block(spec):
    """C216: '--block L12,C06,...' or a file holding the ids (comma, space or newline separated), in block order"""
    txt = open(spec, encoding='utf-8').read() if os.path.isfile(spec) else spec
    ids = [x for x in re.split(r'[\s,]+', txt.strip()) if x]
    bad = [x for x in ids if not RID.match(x)]
    if not ids or bad or len(set(ids)) != len(ids):
        return None, 'ids must be L<n>/C<n>, at least one, no repeats (bad: %s)' % (','.join(bad) or 'repeat or empty')
    return ids, None


def hunter_repeats(runf):
    """C216: M1_HUNTER failures_log_repeats of a run (both spellings the assessors used); None when the item has no count"""
    m = HREP.search(assess(os.path.join(runf, 'ASSESS.tsv')).get('M1_HUNTER', ''))
    return float(m.group(1)) if m else None


def read_reasoning(spec):
    """C216: B3c scores, from blind-scoring result files after unblinding (the series rows hold no reasoning column).
    Each file: a 'run_id' (or 'run') column and either a 'reasoning' column (points of 16) or agreement_v1 scorer rows
    (run, item, points; TOTAL and MESSY rows skipped, the item points summed). Several files (comma list) = one per scorer: mean."""
    per = {}
    for p in [x for x in spec.split(',') if x]:
        rows = tsv(p); got = {}
        for r in rows:
            rid = r.get('run_id') or r.get('run')
            if not rid:
                continue
            if 'reasoning' in r:
                if f(r['reasoning']) is not None:
                    got[rid] = f(r['reasoning'])
            elif (r.get('item') or '').upper() not in ('TOTAL', 'MESSY') and f(r.get('points')) is not None:
                got[rid] = got.get(rid, 0.0) + f(r['points'])
        for rid, v in got.items():
            per.setdefault(rid, []).append(v)
    return {k: sum(v) / len(v) for k, v in per.items()}


def p_text(p, how):
    return ('%.6g' % p) if p is not None else 'MISSING', how


def cmd_bars_block(a):
    """C216 (PROOF_RUNS_V1 section 3): only the RUN rows whose run_id is in the block count; halves by block order among the memory
    runs (first half early, last half late; an odd middle run is in neither half); exact permutation over C(n_L + n_C, n_C) splits."""
    ids, err = parse_block(a.block)
    if ids is None:
        print('REFUSED BAD_BLOCK %s' % err); return 2
    cfg = load_cfg(a.config)
    rows = tsv(a.series)
    allrun = [r for r in rows if r.get('kind') == 'RUN']
    looks = {r['run_id']: r for r in rows if r.get('kind') == 'LOOK'}
    pos = {x: i for i, x in enumerate(ids)}
    inb = sorted([r for r in allrun if r.get('run_id') in pos], key=lambda r: pos[r['run_id']])
    R, mism = load_runs(inb, a.series)
    seen = {}
    for n in R:
        rid = n['row']['run_id']
        if rid in seen:
            mism.append('%s: more than one RUN row in the series' % rid); continue
        if n['arm'] != rid[0] or n['row'].get('arm') != rid[0]:
            mism.append('%s: arm SERIES_V2 %s, ASSESS %s, block id says %s' % (rid, n['row'].get('arm'), n['arm'], rid[0]))
        seen[rid] = n
    Lb, Cb = [x for x in ids if x[0] == 'L'], [x for x in ids if x[0] == 'C']
    h = len(Lb) // 2
    early, late = Lb[:h], Lb[len(Lb) - h:]
    missing = [x for x in ids if x not in seen]
    complete = not missing
    reas = read_reasoning(a.reasoning) if a.reasoning else None
    out = ['BLOCK %s | rows found %d of %d (missing: %s) | memory %d, control %d | early %s, late %s | RUN rows outside the block ignored: %d' % (
        ','.join(ids), len(seen), len(ids), ','.join(missing) or 'none', len(Lb), len(Cb), ','.join(early) or '-', ','.join(late) or '-',
        len(allrun) - len(inb))]
    word = lambda ok, ready=complete: ('PASS' if ok else 'FAIL') if ready else 'PENDING'
    need60 = lambda k: (6 * k + 9) // 10                     # 60 pct of k, rounded up (PROOF_RULES_V2 rules share)
    get = lambda xs, k: [seen[x][k] if x in seen else None for x in xs]

    def line(bar, ok, measure, value, rule, note=''):
        out.append('%s %s | measure: %s | value: %s | bar: %s%s' % (bar, ok, measure, value, rule, (' | ' + note) if note else ''))

    # B1 (block order; a run with no row breaks the streak)
    best, cur = [], []
    for x in ids:
        if x in seen and seen[x]['clean'] == 'yes':
            cur.append(x); best = list(cur) if len(cur) > len(best) else best
        else:
            cur = []
    notc = ['%s(hand %s stops %s blind %s repro %s)' % (x, fmt(seen[x]['hand']), fmt(seen[x]['tool_stops']), fmt(seen[x]['blindfold']),
            seen[x]['repro']) for x in ids if x in seen and seen[x]['clean'] != 'yes']
    line('B1', 'PASS' if len(best) >= 5 else word(False), 'longest run of block runs in a row with hand 0, tool stops 0, blindfold 0, REPRO equal',
         '%d (%s); not clean: %s' % (len(best), ','.join(best) or '-', ', '.join(notc) or 'none'), '5 in a row')
    # B2a
    L = [seen[x] for x in Lb if x in seen]
    a_cnt = sum(1 for n in L if n['best_round'] and n['best_round'] > 1 and n['best_lead15'] is not None and n['r1_lead15'] is not None
                and n['best_lead15'] > n['r1_lead15'])
    line('B2a', word(a_cnt >= need60(len(Lb))), 'memory runs whose best round beats R1 at 15 min (best_round above 1, best_lead15 above r1_lead15)',
         '%d of %d' % (a_cnt, len(Lb)), 'at least %d of %d' % (need60(len(Lb)), len(Lb)))
    # B2b
    m1, m2 = mean(get(early, 'best_margin')), mean(get(late, 'best_margin'))
    d2b = (m2 - m1) if (m1 is not None and m2 is not None) else None
    ok = d2b is not None and d2b >= 2
    line('B2b', word(ok), 'mean best margin late %s minus early %s' % ('-'.join(late[:1] + late[-1:]), '-'.join(early[:1] + early[-1:])),
         '%s minus %s = %s (margins left out: %d)' % (fmt(m2), fmt(m1), fmt(d2b), sum(1 for v in get(early + late, 'best_margin') if v is None)),
         'at least +2', 'reading, not proof (3 vs 3 runs, weak power)' if ok else 'a fail alone is not a kill')
    # B2c
    e1, e2 = mean(get(early, 'fc_mean_abs_err')), mean(get(late, 'fc_mean_abs_err'))
    s_late = sum(1 for v in get(late, 'fc_best_state_match') if v == 'yes')
    ok = e1 is not None and e2 is not None and e2 < e1 and s_late >= need60(len(late))
    line('B2c', word(ok), 'mean forecast abs error late vs early; late memory runs whose better state matches the state split tool',
         'error %s vs %s; matches %d of %d (NA counts as no)' % (fmt(e2), fmt(e1), s_late, len(late)),
         'late error below early, and at least %d of %d matches' % (need60(len(late)), len(late)))
    # B3a
    mL = [v for v in get(Lb, 'best_margin') if v is not None]; mC = [v for v in get(Cb, 'best_margin') if v is not None]
    if mL and mC:
        p, how = perm_p(mL, mC); d = mean(mL) - mean(mC)
    else:
        p, how, d = None, 'no margins', None
    ok = d is not None and d >= 2 and p is not None and p < 0.10
    line('B3a', word(ok), 'mean best margin memory minus control, one-sided exact permutation p (share of relabellings with a difference as large or larger)',
         '%s (n %d) minus %s (n %d) = %s; p %s (%s)' % (fmt(mean(mL)), len(mL), fmt(mean(mC)), len(mC), fmt(d), *p_text(p, how)),
         'at least +2 and p below 0.10')
    # B3b
    rL, rC = mean(get(Lb, 'M1_repeat')), mean(get(Cb, 'M1_repeat'))
    hr = {x: hunter_repeats(seen[x]['runf']) if x in seen else None for x in early + late}
    h1, h2 = mean([hr[x] for x in early]), mean([hr[x] for x in late])
    ok = rL is not None and rC is not None and rL < rC and h1 is not None and h2 is not None and h2 <= h1
    line('B3b', word(ok), 'mean M1_repeat per run memory vs control; mean hunter repeats (M1_HUNTER failures_log_repeats) late vs early',
         'M1 %s vs %s; hunter %s vs %s (runs with no count: %d)' % (fmt(rL), fmt(rC), fmt(h2), fmt(h1), sum(1 for v in hr.values() if v is None)),
         'memory M1 below control, and late hunter repeats not above early')
    # B3c
    if reas is None:
        line('B3c', 'PENDING', 'blind reasoning score of 16 (REASONING_QUALITY_V3), memory mean, memory minus control, permutation p',
             'NO_REASONING_FILE (give --reasoning <blind-scoring result file(s)> after C09)', 'memory mean at least 11, difference at least +2, p below 0.10')
    else:
        qL = [reas[x] for x in Lb if x in reas]; qC = [reas[x] for x in Cb if x in reas]
        if qL and qC:
            p, how = perm_p(qL, qC); d = mean(qL) - mean(qC)
        else:
            p, how, d = None, 'no scores', None
        ok = d is not None and mean(qL) >= 11 and d >= 2 and p is not None and p < 0.10
        line('B3c', word(ok, complete and len(qL) == len(Lb) and len(qC) == len(Cb)), 'blind reasoning score of 16 (from the --reasoning file, not the series rows)',
             'memory %s (n %d) minus control %s (n %d) = %s; p %s (%s)' % (fmt(mean(qL)), len(qL), fmt(mean(qC)), len(qC), fmt(d), *p_text(p, how)),
             'memory mean at least 11, difference at least +2, p below 0.10', 'scorer agreement at least 0.80 is checked by agreement_v1, not here')
    # B3d: never computed from files here (held-out receipts stay with the orchestrator); only the count comes in
    need = (2 * len(Lb) + 2) // 3
    if a.heldout_same is None:
        line('B3d', 'NOT COMPUTED', 'memory best rounds whose Feb-Mar sign equals the design sign (orchestrator, HELDOUT.md receipts)',
             'no count given (--heldout-same <k>; this tool never reads held-out files)', 'at least %d of %d' % (need, len(Lb)), 'hold check, not proof')
    else:
        line('B3d', word(a.heldout_same >= need), 'memory best rounds whose Feb-Mar sign equals the design sign (count from the orchestrator)',
             '%d of %d' % (a.heldout_same, len(Lb)), 'at least %d of %d' % (need, len(Lb)), 'hold check, not proof (4 of 6 or more on a coin flip: 34 pct)')
    # B4 (LOOK rows of the block's memory runs only)
    yl = sepmar_look(cfg)   # C225
    if not yl:
        out.append('B4 PENDING NO_YARDSTICK_LOOK: config yardstick.look_lead15_by_month is not filled; LOOK rows of block memory runs %d' % sum(1 for x in Lb if x in looks))
    else:
        q = []
        for x in Lb:
            lk = looks.get(x)
            if x not in seen or seen[x]['rediscovery'] != 'no' or not lk:
                continue
            bm = [f(v) for v in lk['look_lead15_by_month'].split(',')]
            beats = sum(1 for v, y in zip(bm, yl) if v is not None and v > y); t = f(lk['look_t_pooled'])
            if beats >= 3 and t is not None and t >= 2:
                q.append('%s %d/4 t %s' % (x, beats, fmt(t)))
        line('B4', word(len(q) >= 3), 'distinct memory best rounds (rediscovery no) beating the yardstick look figure in at least 3 of 4 months, pooled t at least 2',
             '%d: %s' % (len(q), ', '.join(q) or 'none'), 'at least 3')
    out.append('B5 NOT COMPUTED: a fresh agent in a fresh account repeats one block run from the released documents, and the outside reviewer passes the method')
    b2b_fail = [l for l in out if l.startswith('B2b ')][0].startswith('B2b FAIL'); b3a_fail = [l for l in out if l.startswith('B3a ')][0].startswith('B3a FAIL')
    out.append('KILL_RULE %s' % ('TRIGGER: B2b and B3a both fail; change the learning design (pro-practice-first plan), new block' if (complete and b2b_fail and b3a_fail)
               else 'no' if complete else 'PENDING (block not complete)'))
    for m in mism:
        out.append('MISMATCH ' + m)
    print('\n'.join(out))
    return 3 if mism else 0


def twin_append(path, line):
    if os.path.isfile(path):
        shutil.copy2(path, path + '.pre_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(line + '\n')


def cmd_row(a):
    n = run_numbers(a.runf)
    if n is None:
        print('REFUSED NO_ASSESS %s' % a.runf); return 2
    rows = tsv(a.series)
    old = [r for r in rows if r.get('kind') == 'RUN' and r.get('run_id') == n['run_id']]
    if old and not a.replace:
        print('REFUSED ROW_EXISTS %s' % n['run_id']); return 2
    if a.replace and not old:
        print('REFUSED NO_ROW_TO_REPLACE %s' % n['run_id']); return 2
    rp, diff = repro(a.runf)
    clean = 'yes' if (n['hand'] == 0 and n['tool_stops'] == 0 and n['blindfold'] == 0 and rp == 'yes') else 'no'
    idea = 'none'
    if n['best_round']:
        import glob
        pats = {1: ('pipe_r1', 'pipe'), 2: ('pipe_r2',), 3: ('pipe_r3',)}[n['best_round']]     # C99: lean runs name R1's pipe pipe_r1
        cands = []
        for pat in pats:
            cands = cands or sorted([d for d in glob.glob(os.path.join(a.runf, pat + '*')) if re.match(r'^%s\d*$' % pat, os.path.basename(d))])
        if cands:
            try:
                idea = json.load(open(os.path.join(cands[-1], 'INPUT.json'))).get('idea', 'none')
            except (OSError, ValueError):
                idea = 'unknown'
    bad = check_forecast_math(n)
    if bad:
        print('REFUSED ASSESS_MATH %s' % '; '.join(bad)); return 2
    import hashlib
    sh = hashlib.sha256(open(os.path.join(a.runf, 'ASSESS.tsv'), 'rb').read()).hexdigest()[:16]
    rid = n['run_id'] or os.path.basename(a.runf)
    vals = {'kind': 'RUN', 'run_id': rid, 'arm': n['arm'], 'n': str(int(rid[1:])), 'task': n['task'], 'utc_launch': n['utc_launch'],
            'utc_row': now(), 'idea_best': idea, 'repro': rp, 'clean': clean, 'look_lead15_by_month': 'none', 'look_t_pooled': 'none',
            'runf': a.runf, 'receipts': 'ASSESS.tsv %s' % sh}
    for k in ('best_round', 'r1_lead15', 'best_lead15', 'yard_lead15', 'best_margin', 'best_months_pass', 'best_t15', 'fc_mean_abs_err',
              'fc_best_state_match', 'M1_repeat', 'hand', 'tool_stops', 'blindfold', 'novelty_max_overlap', 'rediscovery'):
        vals[k] = fmt(n[k])
    line = '\t'.join(vals[c] for c in COLS)
    print('ROW ' + line)
    if a.write and old:                  # C99: --replace keeps the old row in SERIES_V2_REPLACED.tsv with the reason, then rewrites the series
        if not a.reason:
            print('REFUSED NO_REASON (--replace needs --reason)'); return 2
        hist = os.path.join(os.path.dirname(os.path.abspath(a.series)), 'SERIES_V2_REPLACED.tsv')
        new_hist = not os.path.isfile(hist)
        with open(hist, 'a', encoding='utf-8') as fh:
            if new_hist: fh.write('utc_replaced\treason\t' + '\t'.join(COLS) + '\n')
            for r in old: fh.write(now() + '\t' + a.reason + '\t' + '\t'.join(r.get(c, '') for c in COLS) + '\n')
        shutil.copy2(a.series, a.series + '.pre_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        keep = [l for l in open(a.series, encoding='utf-8').read().splitlines(True) if l.split('\t')[:2] != ['RUN', n['run_id']]]
        with open(a.series, 'w', encoding='utf-8') as fh:
            fh.write(''.join(keep).rstrip('\n') + '\n' + line + '\n')
        print('REPLACED %s (old row in %s)' % (n['run_id'], hist)); return 0
    if a.write:
        twin_append(a.series, line); print('WRITTEN %s' % a.series)
    return 0


def cmd_look(a):
    rows = tsv(a.series)
    if not any(r.get('kind') == 'RUN' and r.get('run_id') == a.run_id for r in rows):
        print('REFUSED NO_RUN_ROW %s' % a.run_id); return 2
    if any(r.get('kind') == 'LOOK' and r.get('run_id') == a.run_id for r in rows):
        print('REFUSED LOOK_EXISTS %s (one look only)' % a.run_id); return 2
    bm = a.by_month.split(',')
    if len(bm) != 4 or any(f(x) is None for x in bm) or f(a.t_pooled) is None:
        print('REFUSED BAD_LOOK need 4 monthly numbers and a pooled t'); return 2
    run = [r for r in rows if r.get('kind') == 'RUN' and r.get('run_id') == a.run_id][0]
    vals = {c: 'none' for c in COLS}
    vals.update({'kind': 'LOOK', 'run_id': a.run_id, 'arm': run['arm'], 'n': run['n'], 'task': run['task'], 'utc_launch': run['utc_launch'],
                 'utc_row': now(), 'idea_best': run['idea_best'], 'look_lead15_by_month': ','.join(bm), 'look_t_pooled': a.t_pooled,
                 'runf': run['runf'], 'receipts': a.receipt})
    line = '\t'.join(vals[c] for c in COLS)
    print('ROW ' + line)
    if a.write:
        twin_append(a.series, line); print('WRITTEN %s' % a.series)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['bars', 'row', 'look'])
    ap.add_argument('--series', default=LSD + '/SERIES_V2.tsv'); ap.add_argument('--config', default=LSD + '/SERIES_V2_CONFIG.json')
    ap.add_argument('--runf'); ap.add_argument('--write', action='store_true'); ap.add_argument('--replace', action='store_true'); ap.add_argument('--reason')
    ap.add_argument('--run-id'); ap.add_argument('--by-month'); ap.add_argument('--t-pooled'); ap.add_argument('--receipt', default='none')
    ap.add_argument('--block'); ap.add_argument('--reasoning'); ap.add_argument('--heldout-same', type=int)   # C216 (bars --block only)
    a = ap.parse_args()
    if a.cmd == 'row' and not a.runf:
        print('REFUSED USAGE --runf'); return 2
    if a.cmd == 'look' and not (a.run_id and a.by_month and a.t_pooled):
        print('REFUSED USAGE --run-id --by-month --t-pooled'); return 2
    return {'bars': cmd_bars, 'row': cmd_row, 'look': cmd_look}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
