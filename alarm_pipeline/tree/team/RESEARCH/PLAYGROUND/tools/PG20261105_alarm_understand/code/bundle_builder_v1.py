#!/usr/bin/env python3
"""bundle_builder_v1.py (SCO-A136 for SCOUT, 6 Nov 2026; playground PG20261105_alarm_understand). TEST, NOT REVIEWED: never a PASS.
The JOIN bundle builder that alarm_understand V1 left NOT BUILT (README "Not built" 1): from one finished GRADE job it writes the bundle
alarm_understand_v1.py card reads (README "Inputs"): FIRES.tsv, and READINGS.tsv, FORCED.tsv, MONEY.tsv when their source is given, plus
BUNDLE_SOURCES.tsv (every input with its sha16) and BUNDLE_NOTES.md (what is absent and why). A JOINER: no metric, no grade, no rule.
  python3 -B alarm_understand_v1.py bundle <new out dir> --from-job <GRADE job id> --runner <runner root> --alarm <id> --block <B>
      [--variant V1] [--true-row TRUE_ROW.tsv --def-sha16 <s>]
      [--ctx <research root> <subject> [--ctx-match <subject>] --ctx-values a,b --lab3 <lab3 code dir>]   alarm_context.read()
      [--epi <research root> <subject> [--epi-values a,b] --lab3 <dir>]                                 alarm_profile_v2_3.read()
      [--gg-run <group_and_grade run> --gg-tools <idea_to_grade dir> --gg-costs <costs tsv> --money-exit <exit> --lean FADE|FOLLOW]
                                                                                                           grouper_v1_10.Data
SOURCES AND JOINS (each checked; any missing or mismatched input: exit 2 REFUSED <CODE>, nothing written; never a guessed join):
  job       <runner>/Q_*/DONE/<id>_*.job.sh, exactly one (NO_JOB, JOB_AMBIGUOUS); its status file <runner>/Q_*/logs/<name>.status says
            exit=0 (NO_STATUS, JOB_NOT_OK); a kitq GRADE job: its TITLE names JOB_GRADE_V and it writes DV=$RD/receipts/$J with one RD=
            and one J= (NOT_A_GRADE_JOB); the receipts' STAGES.tsv ends rc 0 (GRADE_NOT_DONE).
  fires     the receipts' FIRES.tsv row of the variant (V, n, sha16, path of <V>_FIRES_V1_LIST.tsv): the list must exist (NO_INPUT), carry
            that sha16 (SOURCE_CHANGED) and n rows (JOIN_MISMATCH), header coin t side, whole-second t, side +1 or -1, no (coin, t) twice
            (BAD_INPUT). PERFIRE_<V>.tsv beside it must carry the sha16 of PERFIRE_SEAL.tsv (SOURCE_CHANGED), the seal must name this job's
            J and its A and R row counts must hold, and its A rows must be the list's (coin, t, side), one for one (JOIN_MISMATCH).
  closed    the block is checked first (alarm_understand check_block: BLOCK_CLOSED, BAD_BLOCK; nothing read); a listed fire on a day
            lab3 law.py refuses (or the card's closed days) is dropped and counted, never copied.
  readings  alarm_context.read(root, lab3, subject, block first, block last, values): FIRE rows join the bundle's fires in the block
            on (coin, t_alarm) exactly: a fire without a row JOIN_MISSING, a row without a fire JOIN_EXTRA; code CTX.<subject>.<value>,
            known_at = t_decision (> t: AFTER, column after = 1). --ctx-match rows are MATCH rows written under the fire subject's code
            name (CTX.A02_MATCH as CTX.A02, README Inputs). A NaN value is no reading. alarm_profile_v2_3.read --epi-values the same, code
            EPI.<subject>.<value>, known_at = its known_at_us.
  forced    alarm_profile_v2_3 forced_usd_log and other_usd_log (episode_blocks.py line 17: the FORCED side is A1.S02 when side +1,
            A1.S01 when side -1; METRICS A1.S01 long, A1.S02 short): side -1 long = 10^forced, short = 10^other; side +1 the mirror;
            other_usd_log 0 = none (the catalog's unit) -> 0; NaN stays empty. Same exact join as the readings.
  money     grouper_v1_10.Data(run, tools, costs, an empty cards file): its parents (coin, t, side) must be the block's fires one for one
            (JOIN_MISSING, JOIN_EXTRA; same (coin, t) with another side JOIN_SIDE); fade_gross_15m/1h/4h = P[HOLD_<h>, FADE, GROSS],
            net = P[<exit>, <lean>, HONEST], edge_tough = net minus its tough mean; the exit must be in P (BAD_ARGS). All money is AFTER.
            A kitq GRADE is a race grade (OUTCOMES_MENU_ALARM_V1: reach, races, best, worst; no return per fire): MONEY stays absent
            and BUNDLE_SOURCES says why.
  true row  --true-row (true_gate TRUE_ROW.tsv): its def_sha16 must equal --def-sha16 (SOURCE_CHANGED; no --def-sha16: BAD_ARGS) and its
            perfire_sha16 the GRADE's PERFIRE seal (JOIN_MISMATCH); copied into the bundle as TRUE_ROW.tsv.
  dims      Q2 DIMS_V2 (classification_tool DIMENSIONS.tsv): NOT BUILT (its keys are words, READINGS.value is a number for the percentile
            against matched moments, and the spec fixes no word-to-number rule): --dims is REFUSED NOT_BUILT.
FROM A RESULTS STORE (SCO-A146, 6 Nov 2026): `--from-gg <run>` in place of --from-job --runner. <run> is an idea_to_grade V3.2 results
store run folder, the store group_and_grade grades on (RUN.json, grading/PARENTS.tsv; e.g. i2g_v3_2/full_ALM_PG_FDAOI_SD_N20267354/run).
  python3 -B alarm_understand_v1.py bundle <new out dir> --from-gg <run> --gg-alarm-id <RUN.json alarm_id> --def-sha16 <DEF sha16>
      --alarm <id> --block <B> --gg-tools <idea_to_grade dir> --gg-costs <costs tsv> --money-exit <exit> --lean FADE|FOLLOW
  store     RUN.json and grading/PARENTS.tsv exist (NO_INPUT); RUN.json is json with event_list {path, sha16} and selection first/last
            (BAD_INPUT); its alarm_id equals --gg-alarm-id and its counts.parents the PARENTS rows (JOIN_MISMATCH); its
            alarm.definition_sha16 equals --def-sha16 (SOURCE_CHANGED); the block lies inside first..last (BAD_ARGS). A group_and_grade
            output folder (RUN_ARGS.tsv, no RUN.json) is REFUSED NOT_BUILT naming the store it graded (its CARDS labels are words).
  fire list the event list RUN.json names exists (NO_INPUT) with that sha16 (SOURCE_CHANGED), header coin t side, no identity twice.
  fires     PARENTS.tsv rows (the graded fires; idea_to_grade_rel1.py line 795): coin, whole t, side +1 or -1, no (coin, t) twice,
            known_at_us a whole number after t (money is known only after the fire; BAD_INPUT); each parent's (coin, t, side) is a row
            of the event list (JOIN_EXTRA) and its event_id is sha256(event_list sha16|coin|t|side)[:16] (idea_to_grade_v3_2_rel1.py
            line 204; JOIN_MISMATCH). Listed fires the store did not grade are counted in BUNDLE_NOTES, never copied.
  money     grouper_v1_10.Data on the same store: its keys must be the PARENTS rows one for one, in order (JOIN_MISMATCH); the money
            columns as above, plus known_at (PARENTS known_at_us, seconds rounded up) and after (known_at > t: always 1).
  context   CONTEXT.tsv: every other column of the fire, kept as text with its clock: event list columns (onset_t, trigger, ...) known
            at t (after 0: the detection writes its row at t); PARENTS columns (wave_id, census_status, edges) known at known_at_us
            (after 1: waves and matched controls use later moments). Not READINGS: no matched comparison exists for them.
  not built with --from-gg: --true-row (it binds a kitq PERFIRE seal), --ctx and --epi (no subject for these alarms): NOT_BUILT.
Exit 0 written, 2 REFUSED <CODE>, 3 FAILED."""
import sys
sys.dont_write_bytecode = True
import argparse, csv, glob, hashlib, importlib, importlib.util, json, math, os, re
import numpy as np

HERE = os.path.dirname(os.path.realpath(__file__))
EDITION = 'bundle_builder V1 (playground PG20261105_alarm_understand, SCO-A136 6 Nov 2026, TEST, NOT REVIEWED: never a PASS)'
_AU = None
PF = os.path.join('Alarm', 'alarm', 'current', '05_Profile', 'tree', 'tools')
BUILDER_PINS = ((PF + '/alarm_context/alarm_context.py', '38bdf42a6bdae4cb'),
                (PF + '/alarm_profile_v2/alarm_profile_v2_3.py', 'cfcc853f2f994ebe'))
RACE_GRADE_WHY = ('a kitq GRADE is a race grade (OUTCOMES_MENU_ALARM_V1: reach, races, best, worst): no gross or net return per fire, '
                  'so MONEY is absent; give --gg-run for a group_and_grade run')
DIMS_WHY = ('Q2 DIMS_V2 NOT BUILT: classification_tool DIMENSIONS.tsv keys are words (DATA_DICTIONARY bf02da4147d065bf), READINGS.value '
            'is a number for the percentile against matched moments, and the spec fixes no word-to-number rule')


def AU():
    """alarm_understand_v1.py beside this file (its Refused, release pins, law check and closed days)"""
    global _AU
    if _AU is None:
        au = os.environ.get('AU_TOOL') or os.path.join(HERE, 'alarm_understand_v1.py')      # a mutant copy of this file runs elsewhere
        sp = importlib.util.spec_from_file_location('alarm_understand_for_bundle', au)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _AU = m
    return _AU


def Refused(code, detail=''):
    return AU().Refused(code, detail)


def sha16_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def parse(argv):
    ap = argparse.ArgumentParser(prog='alarm_understand_v1.py bundle')
    ap.add_argument('cmd', choices=['bundle'])
    ap.add_argument('out')
    ap.add_argument('--from-job'); ap.add_argument('--runner')
    ap.add_argument('--from-gg'); ap.add_argument('--gg-alarm-id')                                   # SCO-A146: a results store
    ap.add_argument('--alarm', required=True); ap.add_argument('--block', required=True)
    ap.add_argument('--variant'); ap.add_argument('--card-closed-from', type=int, default=None)
    ap.add_argument('--true-row'); ap.add_argument('--def-sha16')
    ap.add_argument('--ctx', nargs=2, metavar=('ROOT', 'SUBJECT')); ap.add_argument('--ctx-match'); ap.add_argument('--ctx-values')
    ap.add_argument('--epi', nargs=2, metavar=('ROOT', 'SUBJECT')); ap.add_argument('--epi-values')
    ap.add_argument('--lab3')
    ap.add_argument('--gg-run'); ap.add_argument('--gg-tools'); ap.add_argument('--gg-costs'); ap.add_argument('--money-exit')
    ap.add_argument('--lean', choices=['FADE', 'FOLLOW'])
    ap.add_argument('--dims')
    return ap.parse_args(argv)


# ---------------------------------------------------------------------------------------------------- the GRADE job and its receipts
def read_rows(p, header=True):
    with open(p, newline='') as f:
        L = [l.rstrip('\n').split('\t') for l in f if l.strip() and not l.startswith('#')]
    if not header:
        return L
    return [dict(zip(L[0], r)) for r in L[1:]] if L else []


def find_job(runner, job_id):
    if not re.fullmatch(r'\d{4,12}', str(job_id)):
        raise Refused('BAD_ARGS', '--from-job %r: the runner id (digits)' % job_id)
    hits = sorted(glob.glob(os.path.join(runner, 'Q_*', 'DONE', '%s_*.job.sh' % job_id)))
    if not hits:
        raise Refused('NO_JOB', 'no %s/Q_*/DONE/%s_*.job.sh' % (runner, job_id))
    if len(hits) > 1:
        raise Refused('JOB_AMBIGUOUS', ' '.join(hits))
    jf = hits[0]; name = os.path.basename(jf)[:-len('.job.sh')]
    stp = os.path.join(os.path.dirname(os.path.dirname(jf)), 'logs', name + '.status')
    if not os.path.isfile(stp):
        raise Refused('NO_STATUS', stp)
    st = dict(l.rstrip('\n').split('=', 1) for l in open(stp) if '=' in l)
    if st.get('exit') != '0':
        raise Refused('JOB_NOT_OK', '%s exit=%s' % (stp, st.get('exit')))
    text = open(jf).read()
    title = [l for l in text.splitlines() if l.startswith('# TITLE:')]
    rd = re.findall(r'(?<![A-Za-z0-9_])RD=([^\s;]+)', text); jn = re.findall(r'(?<![A-Za-z0-9_$])J=([^\s;]+)', text)
    if not (title and 'JOB_GRADE_V' in title[0]) or len(set(rd)) != 1 or len(set(jn)) != 1 or 'DV=$RD/receipts/$J' not in text:
        raise Refused('NOT_A_GRADE_JOB', '%s: no kitq GRADE layout (TITLE JOB_GRADE_V, one RD=, one J=, DV=$RD/receipts/$J)' % jf)
    return dict(job=jf, job_sha16=sha16_file(jf), status=stp, status_sha16=sha16_file(stp), name=name, J=jn[0],
                dv=os.path.join(rd[0], 'receipts', jn[0]))


def grade_fires(J, variant=None):
    """-> dict(fires [(coin, t, side)], list, perfire, seal sha16, srcs)"""
    dv = J['dv']
    stg = os.path.join(dv, 'STAGES.tsv')
    if not os.path.isfile(stg):
        raise Refused('NO_INPUT', stg)
    ends = [r for r in read_rows(stg) if r.get('stage') == 'end']
    if not ends or ends[-1].get('rc') != '0':
        raise Refused('GRADE_NOT_DONE', '%s end rc %s' % (stg, ends[-1].get('rc') if ends else 'missing'))
    fl = os.path.join(dv, 'FIRES.tsv'); sl = os.path.join(dv, 'PERFIRE_SEAL.tsv')
    for p in (fl, sl):
        if not os.path.isfile(p):
            raise Refused('NO_INPUT', p)
    F = read_rows(fl, header=False); SL = read_rows(sl, header=False)
    vs = sorted({r[0] for r in F})
    if variant is None:
        if len(vs) != 1:
            raise Refused('BAD_ARGS', '%s holds variants %s: give --variant' % (fl, vs))
        variant = vs[0]
    fr = [r for r in F if r[0] == variant]; sr = [r for r in SL if r[0] == variant]
    if len(fr) != 1 or len(sr) != 1 or len(fr[0]) < 4 or len(sr[0]) < 8:
        raise Refused('JOIN_MISMATCH', 'variant %s: %d FIRES rows, %d PERFIRE_SEAL rows (one each expected)' % (variant, len(fr), len(sr)))
    _, n, lsha, lst = fr[0][:4]
    _, psha, nA, nR, _, _, ntot, sj = sr[0][:8]
    if sj != J['J']:
        raise Refused('JOIN_MISMATCH', 'PERFIRE_SEAL names job %s, not %s' % (sj, J['J']))
    if not os.path.isfile(lst):
        raise Refused('NO_INPUT', 'fire list %s' % lst)
    if sha16_file(lst) != lsha:
        raise Refused('SOURCE_CHANGED', 'fire list %s is %s, the receipt says %s' % (lst, sha16_file(lst), lsha))
    pf = os.path.join(os.path.dirname(lst), 'PERFIRE_%s.tsv' % variant)
    if not os.path.isfile(pf):
        raise Refused('NO_INPUT', pf)
    if sha16_file(pf) != psha:
        raise Refused('SOURCE_CHANGED', 'PERFIRE %s is %s, the seal says %s' % (pf, sha16_file(pf), psha))
    L = read_rows(lst, header=False)
    if not L or L[0][:3] != ['coin', 't', 'side']:
        raise Refused('BAD_INPUT', '%s header %s: coin t side first' % (lst, L[0][:3] if L else None))
    fires, seen = [], set()
    for r in L[1:]:
        c, t, s = r[0], num_int(r[1], lst), num_int(r[2], lst)
        if s not in (1, -1):
            raise Refused('BAD_INPUT', '%s: side %r of %s %s (+1 or -1)' % (lst, r[2], c, r[1]))
        if (c, t) in seen:
            raise Refused('BAD_INPUT', '%s: (%s, %d) twice' % (lst, c, t))
        seen.add((c, t)); fires.append((c, t, s))
    if len(fires) != int(n):
        raise Refused('JOIN_MISMATCH', '%s holds %d fires, the receipt says %s' % (lst, len(fires), n))
    P = read_rows(pf)
    A = sorted((r['coin'], num_int(r['t'], pf), num_int(r['side'], pf)) for r in P if r.get('kind') == 'A')
    nr = sum(1 for r in P if r.get('kind') == 'R')
    if len(A) != int(nA) or nr != int(nR) or len(P) != int(ntot):
        raise Refused('JOIN_MISMATCH', 'PERFIRE %s: %d A, %d R, %d rows; the seal says %s, %s, %s' % (pf, len(A), nr, len(P), nA, nR, ntot))
    if A != sorted(fires):
        d = len(set(A) ^ set(fires))
        raise Refused('JOIN_MISMATCH', 'PERFIRE A rows are not the fire list one for one (%d keys differ)' % d)
    srcs = [('JOB', J['job'], J['job_sha16'], '', 'runner job file'), ('JOB_STATUS', J['status'], J['status_sha16'], '', 'exit=0'),
            ('STAGES', stg, sha16_file(stg), '', 'end rc 0'), ('RECEIPT_FIRES', fl, sha16_file(fl), len(F), ''),
            ('PERFIRE_SEAL', sl, sha16_file(sl), len(SL), 'names %s' % sj),
            ('FIRE_LIST', lst, lsha, len(fires), 'the grade input (coin t side)'),
            ('PERFIRE', pf, psha, len(P), '%s A rows equal the list; %s R rows' % (nA, nR))]
    return dict(fires=fires, variant=variant, list=lst, perfire=pf, perfire_sha16=psha, srcs=srcs)


def num_int(x, where):
    try:
        v = float(x)
    except (TypeError, ValueError):
        raise Refused('BAD_INPUT', '%s: %r is not a number' % (where, x))
    if not math.isfinite(v) or v != int(v):
        raise Refused('BAD_INPUT', '%s: %r is not a whole number' % (where, x))
    return int(v)


# ---------------------------------------------------------------------------------------------------- readers (release code, pinned)
def verify_builder_pins():
    root = AU().release_root()
    got = AU().verify_pins(root, BUILDER_PINS)
    return root, got


def _load(path, name):
    folder = os.path.dirname(path)
    sys.path.insert(0, folder)
    try:
        sp = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    finally:
        if folder in sys.path:
            sys.path.remove(folder)
    return m


def real_readers():
    root, _ = verify_builder_pins()
    def ctx(out_root, code_dir, subject, first, last, values):
        AC = _load(os.path.join(root, BUILDER_PINS[0][0]), 'alarm_context_pinned')
        return AC.read(out_root, code_dir, subject, str(first), str(last), values)
    def epi(out_root, code_dir, subject, first, last, values):
        EP = _load(os.path.join(root, BUILDER_PINS[1][0]), 'alarm_profile_v2_3_pinned')
        return EP.read(out_root, code_dir, subject, str(first), str(last), values)
    def gg(run, tools, costs):
        R = AU().release()
        empty = os.path.join(OUT_TMP[0], '_GG_CARDS_EMPTY.tsv')
        if not os.path.exists(empty):
            open(empty, 'x').write('coin\tt\tside\n')
        a = AU().NS(tools=tools, run=run, costs=costs, cards=empty)
        return R.GG.Data(a)
    return dict(ctx=ctx, epi=epi, gg=gg)


OUT_TMP = ['']


def keyed(o, where):
    """reader output -> [(coin, t_alarm int)] with whole-second checks"""
    coins = [str(c) for c in o['coin']]
    ts = [num_int(x, where + ' t_alarm') for x in np.asarray(o['t_alarm'], float)]
    return list(zip(coins, ts))


def exact_join(keys, fire_set, where):
    ks = set(keys)
    miss = fire_set - ks; extra = ks - fire_set
    if miss:
        raise Refused('JOIN_MISSING', '%s: %d fires of the block have no row (e.g. %s)' % (where, len(miss), sorted(miss)[0]))
    if extra:
        raise Refused('JOIN_EXTRA', '%s: %d rows match no fire of the block (e.g. %s)' % (where, len(extra), sorted(extra)[0]))


def fmt(v):
    if v is None:
        return ''
    if isinstance(v, (float, np.floating)):
        return '' if not np.isfinite(v) else repr(float(v))
    return str(v)


# ---------------------------------------------------------------------------------------------------- build
def build(a, readers=None):
    """-> dict(out, fires, closed_dropped, written {name: sha16}); refuses before writing anything"""
    A = AU()
    if os.path.exists(a.out):
        raise Refused('OUT_EXISTS', a.out)
    if a.dims:
        raise Refused('NOT_BUILT', DIMS_WHY)
    if bool(a.from_job) == bool(a.from_gg):
        raise Refused('BAD_ARGS', 'give exactly one fire source: --from-job <kitq GRADE job id> or --from-gg <results store run folder>')
    if a.from_gg:
        return build_gg(a, readers)
    if not a.runner:
        raise Refused('BAD_ARGS', '--from-job needs --runner')
    if a.true_row and not a.def_sha16:
        raise Refused('BAD_ARGS', '--true-row needs --def-sha16 (the DEF it must bind)')
    if (a.ctx or a.epi) and not a.lab3:
        raise Refused('BAD_ARGS', '--ctx and --epi need --lab3 (the lab3 code dir their readers import)')
    if a.ctx and not a.ctx_values:
        raise Refused('BAD_ARGS', '--ctx needs --ctx-values (the readings are named, never all by default)')
    if a.ctx_match and not a.ctx:
        raise Refused('BAD_ARGS', '--ctx-match needs --ctx')
    gg_args = (a.gg_run, a.gg_tools, a.gg_costs, a.money_exit, a.lean)
    if any(gg_args) and not all(gg_args):
        raise Refused('BAD_ARGS', '--gg-run needs --gg-tools, --gg-costs, --money-exit and --lean')
    R = A.release()
    closed_from = a.card_closed_from if a.card_closed_from is not None else A.CARD_CLOSED_FROM
    if closed_from > A.CARD_CLOSED_FROM:
        raise Refused('BAD_ARGS', '--card-closed-from may only move earlier than %d' % A.CARD_CLOSED_FROM)
    first, last, months = A.check_block(a.block, R.LAW.research_refusal, closed_from)      # BLOCK_CLOSED / BAD_BLOCK: nothing read
    J = find_job(a.runner, a.from_job)
    G = grade_fires(J, a.variant)
    srcs = list(G['srcs'])
    open_f, dropped = [], 0
    for c, t, s in G['fires']:
        if A.closed_reason(A.day_of(t), R.LAW.research_refusal, closed_from):
            dropped += 1
        else:
            open_f.append((c, t, s))
    side_of = {(c, t): s for c, t, s in open_f}
    block_set = {(c, t) for c, t, s in open_f if first <= A.day_of(t) <= last}
    readers = readers or {}
    need_real = [k for k, on in (('ctx', a.ctx), ('epi', a.epi), ('gg', a.gg_run)) if on and k not in readers]
    if need_real:
        OUT_TMP[0] = os.path.dirname(os.path.realpath(a.out))
        rr = real_readers()
        for k in need_real:
            readers[k] = rr[k]
    readings, forced, money = [], [], []
    notes = []
    # ---- alarm_context
    if a.ctx:
        root, subj = a.ctx
        vals = [v for v in a.ctx_values.split(',') if v]
        o = readers['ctx'](root, a.lab3, subj, first, last, vals)
        ks = keyed(o, 'alarm_context %s' % subj)
        exact_join(set(ks), block_set, 'alarm_context %s' % subj)
        td = [num_int(x, 'alarm_context t_decision') for x in np.asarray(o['t_decision'], float)]
        for i, (c, t) in enumerate(ks):
            for v in vals:
                x = float(o[v][i])
                if np.isfinite(x):
                    readings.append(('FIRE', c, t, 'CTX.%s.%s' % (subj, v), x, td[i]))
        srcs.append(('CTX', '%s %s' % (root, subj), '', len(ks), 'alarm_context.read %s..%s values %s' % (first, last, ','.join(vals))))
        if a.ctx_match:
            o = readers['ctx'](root, a.lab3, a.ctx_match, first, last, vals)
            km = keyed(o, 'alarm_context %s' % a.ctx_match)
            td = [num_int(x, 'alarm_context t_decision') for x in np.asarray(o['t_decision'], float)]
            for i, (c, t) in enumerate(km):
                for v in vals:
                    x = float(o[v][i])
                    if np.isfinite(x):
                        readings.append(('MATCH', c, t, 'CTX.%s.%s' % (subj, v), x, td[i]))
            srcs.append(('CTX_MATCH', '%s %s' % (root, a.ctx_match), '', len(km), 'matched moments, written under CTX.%s' % subj))
    # ---- alarm_profile_v2_3
    if a.epi:
        root, subj = a.epi
        ev = [v for v in (a.epi_values or '').split(',') if v]
        o = readers['epi'](root, a.lab3, subj, first, last, sorted(set(ev) | {'forced_usd_log', 'other_usd_log'}))
        ks = keyed(o, 'alarm_profile_v2_3 %s' % subj)
        exact_join(set(ks), block_set, 'alarm_profile_v2_3 %s' % subj)
        ka = [-(-int(x) // 1000000) for x in np.asarray(o['known_at_us'], dtype=np.int64)]   # seconds, rounded up: never earlier
        for i, (c, t) in enumerate(ks):
            fv, ov = float(o['forced_usd_log'][i]), float(o['other_usd_log'][i])
            fu = 10.0 ** fv if np.isfinite(fv) else float('nan')
            ou = (0.0 if ov == 0 else 10.0 ** ov) if np.isfinite(ov) else float('nan')
            lg, sh = (fu, ou) if side_of[(c, t)] == -1 else (ou, fu)
            forced.append((c, t, lg, sh, ka[i]))
            for v in ev:
                x = float(o[v][i])
                if np.isfinite(x):
                    readings.append(('FIRE', c, t, 'EPI.%s.%s' % (subj, v), x, ka[i]))
        srcs.append(('EPI', '%s %s' % (root, subj), '', len(ks), 'alarm_profile_v2_3.read %s..%s; forced side by episode_blocks line 17' % (first, last)))
    # ---- group_and_grade money
    if a.gg_run:
        D = readers['gg'](a.gg_run, a.gg_tools, a.gg_costs)
        gk = [(str(c), num_int(t, 'grouper Data keys'), num_int(s, 'grouper Data keys')) for c, t, s in D.keys]
        bykey = {}
        for i, (c, t, s) in enumerate(gk):
            if (c, t) in bykey:
                raise Refused('BAD_INPUT', 'grouper Data: (%s, %d) twice' % (c, t))
            bykey[(c, t)] = (i, s)
        exact_join(set(bykey), block_set, 'grouper_v1_10.Data %s' % a.gg_run)
        bad = [(c, t) for (c, t), (i, s) in bykey.items() if s != side_of[(c, t)]]
        if bad:
            raise Refused('JOIN_SIDE', 'grouper Data: %d parents carry another side than the fire list (e.g. %s)' % (len(bad), sorted(bad)[0]))
        key = (a.money_exit, a.lean, 'HONEST')
        if key not in D.P:
            raise Refused('BAD_ARGS', 'exit %s with lean %s is not in the grade (HONEST)' % (a.money_exit, a.lean))
        X, Tt = D.P[key]
        gross = {h: D.P[('HOLD_%s' % h, 'FADE', 'GROSS')][0] for h in ('15m', '1h', '4h')}
        for (c, t), (i, s) in sorted(bykey.items(), key=lambda kv: kv[1][0]):
            money.append((c, t, s, a.money_exit, float(gross['15m'][i]), float(gross['1h'][i]), float(gross['4h'][i]), float(X[i]),
                          float(X[i] - Tt[i])))
        srcs.append(('MONEY', a.gg_run, '', len(money), 'grouper_v1_10.Data: FADE GROSS HOLD 15m/1h/4h; %s %s HONEST net and tough edge' % (a.money_exit, a.lean)))
    else:
        srcs.append(('MONEY', '', '', 0, RACE_GRADE_WHY))
        notes.append('- MONEY absent: ' + RACE_GRADE_WHY + '. Q6, Q7 and Q8 read NOT_ANSWERED on this bundle.')
    if not a.ctx:
        notes.append('- READINGS (alarm_context) absent: no --ctx given (a CTX part must exist for this alarm\'s own fires; '
                     'alarm_context SUBJECTS name the built subjects).')
    if not a.epi:
        notes.append('- FORCED and EPI readings absent: no --epi given (alarm_profile_v2_3 SUBJECTS name the built subjects).')
    notes.append('- ' + DIMS_WHY + '.')
    # ---- true row
    tr_text = None
    if a.true_row:
        if not os.path.isfile(a.true_row):
            raise Refused('NO_INPUT', a.true_row)
        T = read_rows(a.true_row)
        if len(T) != 1 or 'verdict' not in T[0]:
            raise Refused('BAD_INPUT', '%s: one row with verdict expected' % a.true_row)
        if T[0].get('def_sha16') != a.def_sha16:
            raise Refused('SOURCE_CHANGED', 'TRUE_ROW binds def %s, not %s' % (T[0].get('def_sha16'), a.def_sha16))
        if T[0].get('perfire_sha16') != G['perfire_sha16']:
            raise Refused('JOIN_MISMATCH', 'TRUE_ROW binds perfire %s, the GRADE seal is %s' % (T[0].get('perfire_sha16'), G['perfire_sha16']))
        tr_text = open(a.true_row).read()
        srcs.append(('TRUE_ROW', a.true_row, sha16_file(a.true_row), 1, 'def and perfire sha16 checked'))
    # ---- write (nothing was written before this line)
    os.makedirs(a.out)
    head = '# bundle of %s from GRADE job %s (%s), variant %s, block %s; %s\n' % (a.alarm, a.from_job, J['name'], G['variant'], a.block, EDITION)
    written = {}

    def put(name, cols, rws):
        p = os.path.join(a.out, name)
        with open(p, 'x') as f:
            f.write(head + '\t'.join(cols) + '\n')
            for r in rws:
                f.write('\t'.join(fmt(v) for v in r) + '\n')
        written[name] = sha16_file(p)
    put('FIRES.tsv', ('alarm_id', 'coin', 't', 'side'), [(a.alarm, c, t, s) for c, t, s in open_f])
    if a.ctx or a.epi:
        put('READINGS.tsv', ('who', 'coin', 't', 'code', 'value', 'known_at', 'after'),
            [(w, c, t, code, v, k, int(k > t)) for w, c, t, code, v, k in readings])
    if a.epi:
        put('FORCED.tsv', ('coin', 't', 'long_usd', 'short_usd', 'known_at', 'after'), [r + (int(r[4] > r[1]),) for r in forced])
    if a.gg_run:
        put('MONEY.tsv', ('coin', 't', 'side', 'exit', 'fade_gross_15m', 'fade_gross_1h', 'fade_gross_4h', 'net', 'edge_tough', 'after'),
            [r + (1,) for r in money])
    if tr_text is not None:
        p = os.path.join(a.out, 'TRUE_ROW.tsv')
        with open(p, 'x') as f:
            f.write(tr_text)
        written['TRUE_ROW.tsv'] = sha16_file(p)
    pins = A.verify_pins(R.root, BUILDER_PINS) if (a.ctx or a.epi) else []
    rows = srcs + [('release pin', os.path.join(R.root, r), s, '', 'checked') for r, s in list(R.pins) + list(pins)]
    rows += [('builder', os.path.realpath(__file__), sha16_file(os.path.realpath(__file__)), '', EDITION)]
    rows += [('closed', '', '', dropped, 'listed fires on closed days dropped (lab3 law.py; card closed from %d)' % closed_from)]
    put('BUNDLE_SOURCES.tsv', ('role', 'path', 'sha16', 'rows', 'note'), rows)
    p = os.path.join(a.out, 'BUNDLE_NOTES.md')
    with open(p, 'x') as f:
        f.write('# BUNDLE_NOTES %s, GRADE job %s, block %s\n\n- fires: %d listed, %d on closed days dropped, %d kept; %d in the block.\n%s\n'
                '- status: playground result, TEST, NOT REVIEWED: never a PASS.\n' % (
                    a.alarm, a.from_job, a.block, len(G['fires']), dropped, len(open_f), len(block_set), '\n'.join(notes)))
    written['BUNDLE_NOTES.md'] = sha16_file(p)
    return dict(out=a.out, fires=len(open_f), closed_dropped=dropped, block_fires=len(block_set), written=written,
                readings=len(readings), forced=len(forced), money=len(money))


# ---------------------------------------------------------------------------------------------------- SCO-A146: --from-gg (a results store)
GG_CTX_SKIP = {'coin', 't', 'side', 'event_id', 'parent_id', 'day', 'known_at_us', 'row_follow', 'row_fade'}


def store_fires(run, alarm_id, def_sha16):
    """an idea_to_grade V3.2 results store run folder -> dict(parents [dict coin t side ka row], ev {(c,t,s): row}, first, last,
    not_graded, srcs); every check of the module docstring ('FROM A RESULTS STORE'); nothing written"""
    rj = os.path.join(run, 'RUN.json'); pp = os.path.join(run, 'grading', 'PARENTS.tsv')
    ra = os.path.join(run, 'RUN_ARGS.tsv')
    if os.path.isfile(ra) and not os.path.isfile(rj):
        st = [l.rstrip('\n').split('\t', 1)[1] for l in open(ra) if l.startswith('store\t')]
        raise Refused('NOT_BUILT', '%s is a group_and_grade output folder (RUN_ARGS.tsv): its context CARDS labels are words and no join '
                      'rule is written; give the results store it graded: %s' % (run, ' '.join(st) or 'none named'))
    for p in (rj, pp):
        if not os.path.isfile(p):
            raise Refused('NO_INPUT', p)
    try:
        body = json.load(open(rj))
    except ValueError as e:
        raise Refused('BAD_INPUT', '%s is not json: %s' % (rj, e))
    el = body.get('event_list') if isinstance(body, dict) else None
    if not isinstance(el, dict) or not el.get('path') or not el.get('sha16'):
        raise Refused('BAD_INPUT', '%s: no event_list path and sha16' % rj)
    if body.get('alarm_id') != alarm_id:
        raise Refused('JOIN_MISMATCH', '%s alarm_id %r, not --gg-alarm-id %r' % (rj, body.get('alarm_id'), alarm_id))
    ds = (body.get('alarm') or {}).get('definition_sha16')
    if ds != def_sha16:
        raise Refused('SOURCE_CHANGED', '%s binds definition %s, not --def-sha16 %s' % (rj, ds, def_sha16))
    try:
        sel = body['selection']; first, last = int(str(sel['first'])), int(str(sel['last']))
    except (KeyError, TypeError, ValueError) as e:
        raise Refused('BAD_INPUT', '%s: selection first/last: %s' % (rj, e))
    ev, esha = el['path'], el['sha16']
    if not os.path.isfile(ev):
        raise Refused('NO_INPUT', 'event list %s' % ev)
    if sha16_file(ev) != esha:
        raise Refused('SOURCE_CHANGED', 'event list %s is %s, RUN.json says %s' % (ev, sha16_file(ev), esha))
    E = read_rows(ev)
    if not E or not {'coin', 't', 'side'} <= set(E[0]):
        raise Refused('BAD_INPUT', '%s: header coin t side' % ev)
    evk = {}
    for r in E:
        k = (r['coin'], num_int(r['t'], ev), num_int(r['side'], ev))
        if k in evk:
            raise Refused('BAD_INPUT', '%s: %s twice' % (ev, k))
        evk[k] = r
    P = read_rows(pp)
    need = {'coin', 't', 'side', 'event_id', 'known_at_us'}
    if not P or not need <= set(P[0]):
        raise Refused('BAD_INPUT', '%s: columns %s needed' % (pp, ' '.join(sorted(need))))
    parents, seen_p = [], set()
    for r in P:
        c, t, s = r['coin'], num_int(r['t'], pp + ' t'), num_int(r['side'], pp + ' side')
        if s not in (-1, 1):
            raise Refused('BAD_INPUT', '%s: side %r of %s %d (+1 or -1)' % (pp, r['side'], c, t))
        if (c, t) in seen_p:
            raise Refused('BAD_INPUT', '%s: (%s, %d) twice' % (pp, c, t))
        seen_p.add((c, t))
        ka = -(-num_int(r['known_at_us'], pp + ' known_at_us') // 1000000)            # seconds, rounded up: never earlier
        if ka <= t:
            raise Refused('BAD_INPUT', '%s: %s %d known_at %d is not after the fire (money is known after it)' % (pp, c, t, ka))
        if (c, t, s) not in evk:
            raise Refused('JOIN_EXTRA', '%s: parent (%s, %d, %d) is not a row of the event list %s' % (pp, c, t, s, ev))
        want = hashlib.sha256(('%s|%s|%d|%d' % (esha, c, t, s)).encode()).hexdigest()[:16]
        if r['event_id'] != want:
            raise Refused('JOIN_MISMATCH', '%s: %s %d event_id %s, the event list gives %s' % (pp, c, t, r['event_id'], want))
        parents.append(dict(coin=c, t=t, side=s, ka=ka, row=r))
    cnt = (body.get('counts') or {}).get('parents')
    if cnt is not None and int(cnt) != len(parents):
        raise Refused('JOIN_MISMATCH', '%s counts %s parents, PARENTS.tsv holds %d' % (rj, cnt, len(parents)))
    pk = {(p['coin'], p['t'], p['side']) for p in parents}
    not_graded = sum(1 for k in evk if k not in pk and first <= AU().day_of(k[1]) <= last)
    delay = ((body.get('settings') or {}).get('measure') or {}).get('execution_delay_s')
    srcs = [('STORE_RUN', rj, sha16_file(rj), '', 'alarm_id %s; definition_sha16 %s; window %d..%d; entry delay %s s' % (
                alarm_id, ds, first, last, delay)),
            ('STORE_PARENTS', pp, sha16_file(pp), len(parents), 'the graded fires; known_at_us kept'),
            ('EVENT_LIST', ev, esha, len(evk), 'RUN.json event_list sha16 checked; %d listed fires in the window not graded' % not_graded)]
    return dict(parents=parents, ev=evk, first=first, last=last, not_graded=not_graded, srcs=srcs, run=run, delay=delay)


def real_gg(out):
    OUT_TMP[0] = os.path.dirname(os.path.realpath(out))
    def gg(run, tools, costs):
        R = AU().release()
        empty = os.path.join(OUT_TMP[0], '_GG_CARDS_EMPTY.tsv')
        if not os.path.exists(empty):
            open(empty, 'x').write('coin\tt\tside\n')
        return R.GG.Data(AU().NS(tools=tools, run=run, costs=costs, cards=empty))
    return gg


def build_gg(a, readers=None):
    """--from-gg: FIRES, MONEY and CONTEXT from one results store; refuses before writing anything"""
    A = AU()
    if a.true_row:
        raise Refused('NOT_BUILT', '--true-row with --from-gg: a true_gate row binds a kitq PERFIRE seal; a results store has none')
    if a.ctx or a.epi or a.ctx_match:
        raise Refused('NOT_BUILT', '--ctx/--epi with --from-gg: no CTX or EPI subject exists for these alarms (alarm_context, '
                      'alarm_profile_v2_3 SUBJECTS); no join written')
    if a.gg_run:
        raise Refused('BAD_ARGS', '--gg-run with --from-gg: the money comes from the same store')
    if not all((a.gg_tools, a.gg_costs, a.money_exit, a.lean)):
        raise Refused('BAD_ARGS', '--from-gg needs --gg-tools, --gg-costs, --money-exit and --lean (the money of the same store)')
    if not a.def_sha16:
        raise Refused('BAD_ARGS', '--from-gg needs --def-sha16 (RUN.json alarm.definition_sha16 must equal it)')
    if not a.gg_alarm_id:
        raise Refused('BAD_ARGS', '--from-gg needs --gg-alarm-id (RUN.json alarm_id must equal it)')
    R = A.release()
    closed_from = a.card_closed_from if a.card_closed_from is not None else A.CARD_CLOSED_FROM
    if closed_from > A.CARD_CLOSED_FROM:
        raise Refused('BAD_ARGS', '--card-closed-from may only move earlier than %d' % A.CARD_CLOSED_FROM)
    first, last, _m = A.check_block(a.block, R.LAW.research_refusal, closed_from)      # BLOCK_CLOSED / BAD_BLOCK: nothing read
    S = store_fires(a.from_gg, a.gg_alarm_id, a.def_sha16)
    if not (S['first'] <= first and last <= S['last']):
        raise Refused('BAD_ARGS', 'block %s (%d..%d) is not inside the store window %d..%d' % (a.block, first, last, S['first'], S['last']))
    readers = dict(readers or {})
    if 'gg' not in readers:
        readers['gg'] = real_gg(a.out)
    D = readers['gg'](S['run'], a.gg_tools, a.gg_costs)
    gk = [(str(c), num_int(t, 'grouper Data keys'), num_int(s, 'grouper Data keys')) for c, t, s in D.keys]
    pk = [(p['coin'], p['t'], p['side']) for p in S['parents']]
    if gk != pk:
        d = len(set(gk) ^ set(pk))
        raise Refused('JOIN_MISMATCH', 'grouper Data keys are not the PARENTS rows one for one in order (%d of %d, %d keys differ)' % (
            len(gk), len(pk), d))
    key = (str(a.money_exit), a.lean, 'HONEST')
    if key not in D.P:
        raise Refused('BAD_ARGS', 'exit %s with lean %s is not in the grade (HONEST)' % (a.money_exit, a.lean))
    X, Tt = D.P[key]
    gross = {h: D.P[('HOLD_%s' % h, 'FADE', 'GROSS')][0] for h in ('15m', '1h', '4h')}
    fires, money, ctxr, dropped = [], [], [], 0
    for i, p in enumerate(S['parents']):
        c, t, s, ka = p['coin'], p['t'], p['side'], p['ka']
        if bool(A.closed_reason(A.day_of(t), R.LAW.research_refusal, closed_from)):
            dropped += 1
            continue
        fires.append((c, t, s))
        money.append((c, t, s, a.money_exit, float(gross['15m'][i]), float(gross['1h'][i]), float(gross['4h'][i]), float(X[i]),
                      float(X[i] - Tt[i]), ka, int(ka > t)))
        er = S['ev'][(c, t, s)]
        for col in [k for k in er if k not in GG_CTX_SKIP]:
            ctxr.append((c, t, 'EVENT_LIST', col, er[col], t, 0))
        for col in [k for k in p['row'] if k not in GG_CTX_SKIP]:
            ctxr.append((c, t, 'PARENTS', col, p['row'][col], ka, int(ka > t)))
    block_n = sum(1 for c, t, s in fires if first <= A.day_of(t) <= last)
    srcs = list(S['srcs'])
    srcs.append(('MONEY', S['run'], '', len(money), 'grouper_v1_10.Data: FADE GROSS HOLD 15m/1h/4h; %s %s HONEST net and tough edge; '
                 'known_at from PARENTS' % (a.money_exit, a.lean)))
    os.makedirs(a.out)
    head = '# bundle of %s from results store %s, block %s; %s\n' % (a.alarm, S['run'], a.block, EDITION)
    written = {}

    def put(name, cols, rws):
        p = os.path.join(a.out, name)
        with open(p, 'x') as f:
            f.write(head + '\t'.join(cols) + '\n')
            for r in rws:
                f.write('\t'.join(fmt(v) for v in r) + '\n')
        written[name] = sha16_file(p)
    put('FIRES.tsv', ('alarm_id', 'coin', 't', 'side'), [(a.alarm, c, t, s) for c, t, s in fires])
    put('MONEY.tsv', ('coin', 't', 'side', 'exit', 'fade_gross_15m', 'fade_gross_1h', 'fade_gross_4h', 'net', 'edge_tough', 'known_at',
                      'after'), money)
    put('CONTEXT.tsv', ('coin', 't', 'source', 'column', 'value', 'known_at', 'after'), ctxr)
    rows = srcs + [('release pin', os.path.join(R.root, r), s, '', 'checked') for r, s in list(R.pins)]
    rows += [('builder', os.path.realpath(__file__), sha16_file(os.path.realpath(__file__)), '', EDITION)]
    rows += [('closed', '', '', dropped, 'graded fires on closed days dropped (lab3 law.py; card closed from %d)' % closed_from)]
    put('BUNDLE_SOURCES.tsv', ('role', 'path', 'sha16', 'rows', 'note'), rows)
    p = os.path.join(a.out, 'BUNDLE_NOTES.md')
    with open(p, 'x') as f:
        f.write('# BUNDLE_NOTES %s, results store %s, block %s\n\n- fires: %d graded parents, %d on closed days dropped, %d kept; %d in '
                'the block; %d listed fires not graded (window %d..%d), never copied.\n- MONEY: %s %s HONEST net per fire, FADE gross at '
                '15m/1h/4h, known_at kept (PARENTS known_at_us), all AFTER.\n- CONTEXT.tsv: the fire list and PARENTS columns as text with '
                'their clock (event list columns known at t; PARENTS columns at known_at, AFTER); no matched comparison, so not READINGS.\n'
                '- READINGS, FORCED absent: no CTX or EPI subject for this alarm. TRUE_ROW absent: no true_gate row binds this store.\n'
                '- %s.\n- status: playground result, TEST, NOT REVIEWED: never a PASS.\n' % (
                    a.alarm, S['run'], a.block, len(S['parents']), dropped, len(fires), block_n, S['not_graded'], S['first'], S['last'],
                    a.money_exit, a.lean, DIMS_WHY))
    written['BUNDLE_NOTES.md'] = sha16_file(p)
    return dict(out=a.out, fires=len(fires), closed_dropped=dropped, block_fires=block_n, written=written, readings=0, forced=0,
                money=len(money), context=len(ctxr))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != 'bundle':
        argv = ['bundle'] + argv
    a = parse(argv)
    try:
        r = build(a)
        print('BUNDLE %s: fires %d (closed dropped %d, in block %d), readings %d, forced %d, money %d; %s' % (
            r['out'], r['fires'], r['closed_dropped'], r['block_fires'], r['readings'], r['forced'], r['money'],
            ' '.join('%s %s' % kv for kv in sorted(r['written'].items()))))
        return 0
    except Exception as e:
        if hasattr(e, 'code') and isinstance(getattr(e, 'code'), str):
            print('REFUSED %s: %s' % (e.code, getattr(e, 'detail', '')))
            return 2
        print('FAILED %s: %s' % (type(e).__name__, e))
        return 3


if __name__ == '__main__':
    sys.exit(main())
