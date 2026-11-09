#!/usr/bin/env python3
"""test_mechanism_v2.py (SCO-A154 for SCOUT, 6 Nov 2026; PLAYGROUND, TEST, NOT REVIEWED): the smallest tests of mechanism_v2.py, written
before the tool (red on tests/stub_mechanism_v2.py, then green). Fake bundles only, never real data; the real MECHANISM_MAP_V1.md is read
(read-only, pinned). Scratch: tests/scratch/mv2_<test>_<pid>/ (kept, never deleted).
  python3 -B test_mechanism_v2.py [t01 t02 ...]     (env MECH_V2_UNDER_TEST = the tool file; default ../mechanism_v2.py)"""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, os, subprocess, time

T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
TOOL = os.environ.get('MECH_V2_UNDER_TEST', os.path.join(HERE, 'mechanism_v2.py'))
FR = os.path.realpath(os.path.join(HERE, '..', '..', '..', '..'))
MAP = os.path.join(FR, 'team', 'RESEARCH', 'LEAD', 'MECHANISM_20261106', 'MECHANISM_MAP_V1.md')
T0 = 1758000000          # a fire second inside 20250910..20251231


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def legs_def(code='A1.S08', q=90, w=900, oi=True, liq=True, up=False):
    inp = {'px': {'op': 'price'}, 'sgn': {'op': 'sign', 'of': 'px'}, 'll': {'op': 'raw', 'code': code},
           'll15': {'op': 'sum', 'of': 'll', 'w_s': w}, 'll_p': {'op': 'own_pct', 'of': 'll15', 'q': q},
           'exll': {'op': 'sub', 'a': 'll15', 'b': 'll_p'}, 'hloi': {'op': 'raw', 'code': 'E2.S06'}}
    cond = [{'name': 'move', 'lhs': 'sgn', 'cmp': '>' if up else '<', 'rhs': 0, 'role': 'claim'}]
    if liq:
        cond.append({'name': 'liq', 'lhs': 'exll', 'cmp': '>', 'rhs': 0, 'role': 'claim'})
    if oi:
        cond.append({'name': 'hl oi fell', 'lhs': 'hloi', 'cmp': '<', 'rhs': 0, 'role': 'claim'})
    return {'id': 'FAKE', 'claim': {'one_line': 'fake: fade'}, 'inputs': inp, 'conditions': cond}


def world(name, fires, ctx='asof', defj=None, bind=True, readings=None, extra_ctx=()):
    """fires: list of (coin, t, side); ctx: 'asof' | 'after' | 'late' | 'none' (EVENT_LIST onset rows)"""
    W = os.path.join(T, 'scratch', 'mv2_%s_%d_%d' % (name, os.getpid(), time.time_ns())); os.makedirs(W)
    B = os.path.join(W, 'BUNDLE'); os.makedirs(B)
    dp = os.path.join(W, 'DEF.json'); json.dump(defj if defj is not None else legs_def(), open(dp, 'w'), indent=1)
    ds = sha16(dp) if bind else '0000000000000000'
    open(os.path.join(B, 'BUNDLE_SOURCES.tsv'), 'w').write('# fake bundle\nrole\tpath\tsha16\trows\tnote\n'
        'STORE_RUN\t/fake/RUN.json\taaaaaaaaaaaaaaaa\t\talarm_id FAKE; definition_sha16 %s; window 20250910..20251231\n' % ds)
    open(os.path.join(B, 'FIRES.tsv'), 'w').write('# fake\nalarm_id\tcoin\tt\tside\n' + ''.join('FAKE\t%s\t%d\t%s\n' % f for f in fires))
    rows = []
    for c, t, s in fires:
        if ctx == 'asof':
            rows.append((c, t, 'EVENT_LIST', 'onset_t', t, t, 0))
        elif ctx == 'after':
            rows.append((c, t, 'EVENT_LIST', 'onset_t', t, t, 1))
        elif ctx == 'late':
            rows.append((c, t, 'EVENT_LIST', 'onset_t', t, t + 60, 0))
        rows.append((c, t, 'PARENTS', 'wave_id', 0, t + 86400, 1))
    rows += list(extra_ctx)
    if ctx != 'none':
        open(os.path.join(B, 'CONTEXT.tsv'), 'w').write('# fake\ncoin\tt\tsource\tcolumn\tvalue\tknown_at\tafter\n' +
                                                        ''.join('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % r for r in rows))
    rd = None
    if readings is not None:
        rd = os.path.join(W, 'RD'); os.makedirs(rd)
        open(os.path.join(rd, 'READINGS.tsv'), 'w').write('# fake\nwho\tcoin\tt\tcode\tvalue\tknown_at\n' +
                                                          ''.join('%s\t%s\t%s\t%s\t%s\t%s\n' % r for r in readings))
    return W, B, dp, rd


def run(W, B, dp, rd=None, lean='FADE', mp=MAP, first='20250910', last='20251231'):
    out = os.path.join(W, 'MECHANISM.json')
    cmd = [sys.executable, '-B', TOOL, out, '--bundle', B, '--def', dp, '--first', first, '--last', last, '--lean', lean, '--map', mp]
    if rd:
        cmd += ['--readings', rd]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, timeout=40)
    M = json.load(open(out)) if os.path.isfile(out) else None
    return r.returncode, r.stdout, M


def down(n, coin='AAA', t0=T0):
    return [(coin, t0 + 3600 * i, -1) for i in range(n)]


def up(n, coin='BBB', t0=T0):
    return [(coin, t0 + 3600 * i, 1) for i in range(n)]


def mod():
    spec = importlib.util.spec_from_file_location('mech_v2_ut', TOOL)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------- tests
def t01_member_down():
    W, B, dp, rd = world('t01', down(10))
    rc, out, M = run(W, B, dp)
    assert rc == 0, out
    assert M['mechanism'] == 'FORCED_OUT' and M['shares']['FORCED_OUT']['share'] == 1.0, M['shares']
    assert M['shares']['FORCED_OUT_SHORTS']['share'] == 0.0, M['shares']['FORCED_OUT_SHORTS']
    assert M['shares']['CROWDED_LATE']['share'] is None
    assert 'O1' in out and 'FORCED_OUT_SHORTS' in out, out


def t02_after_ignored():
    W, B, dp, rd = world('t02', down(10), ctx='after')
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', (out, M and M['mechanism'])
    assert M['shares']['FORCED_OUT']['unknown_share'] == 1.0 and M['after_rows_ignored'] >= 10, M['shares']['FORCED_OUT']


def t03_asof_late_proof():
    W, B, dp, rd = world('t03', down(10), ctx='late')
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', M and M['mechanism']


def t04_once_per_wave():
    f = down(9) + [('CCC', T0 + 50000, 1)] * 5          # the up fire is listed in 5 waves: counted once
    W, B, dp, rd = world('t04', f)
    rc, out, M = run(W, B, dp)
    assert rc == 0, out
    S = M['shares']['FORCED_OUT']
    assert S['fires'] == 10 and S['holds'] == 9 and M['duplicates_dropped'] == 4, S
    assert M['mechanism'] == 'FORCED_OUT' and S['share'] == 0.9, (M['mechanism'], S)   # 0.9 >= 0.90: a member


def t05_missing_reading_unknown():
    W, B, dp, rd = world('t05', down(10), defj=legs_def(oi=False, liq=False))
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', M and M['mechanism']
    L = M['shares']['FORCED_OUT']['legs']
    assert L['liq']['unknown'] == 1.0 and L['oi']['unknown'] == 1.0 and L['side']['hold'] == 1.0, L
    assert M['best_id'] == 'FORCED_OUT' and M['undecided'] == ['FORCED_OUT'], (M['best_id'], M.get('undecided'))


def t06_reading_fails_none():
    f = down(10)
    rdg = [('FIRE', c, t, 'E2.S06', 0.5, t) for c, t, s in f]
    W, B, dp, rd = world('t06', f, defj=legs_def(oi=False, liq=False), readings=rdg)
    rc, out, M = run(W, B, dp, rd)
    assert rc == 0 and M['mechanism'] == 'NONE', (out, M and M['mechanism'])
    assert M['shares']['FORCED_OUT']['legs']['oi']['fail'] == 1.0


def t07_standin_codes_refused():
    f = down(10)
    rdg = [('FIRE', c, t, 'CTX.oi_chg_10m', -1.0, t) for c, t, s in f] + [('FIRE', c, t, 'CTX.forced_log_usd_15m', 9.0, t) for c, t, s in f]
    W, B, dp, rd = world('t07', f, defj=legs_def(oi=False), readings=rdg)     # liq proven by the DEF; only the oi leg is open
    rc, out, M = run(W, B, dp, rd)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', M and M['mechanism']
    assert M['shares']['FORCED_OUT']['legs']['oi']['unknown'] == 1.0, M['shares']['FORCED_OUT']['legs']


def t08_shorts_up():
    W, B, dp, rd = world('t08', up(10), defj=legs_def(code='A1.S09', up=True))
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'FORCED_OUT_SHORTS', (out, M and M['mechanism'])
    assert M['shares']['FORCED_OUT']['share'] == 0.0


def t09_follow_lean():
    W, B, dp, rd = world('t09', down(10))
    rc, out, M = run(W, B, dp, lean='FOLLOW')
    assert rc == 0 and M['mechanism'] == 'NONE', M and M['mechanism']


def t10_def_not_bound():
    W, B, dp, rd = world('t10', down(10), bind=False)
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN' and M['def_bound'] is False, M and (M['mechanism'], M['def_bound'])


def t11_map_pin():
    W, B, dp, rd = world('t11', down(10))
    mp = os.path.join(W, 'MAP.md'); open(mp, 'w').write(open(MAP).read() + '\n')
    rc, out, M = run(W, B, dp, mp=mp)
    assert rc == 2 and 'REFUSED MAP_CHANGED' in out and M is None, out


def t12_no_threshold_candidate():
    m = mod()
    S = {'FORCED_OUT': dict(share=0.95, upper=0.95, fires=20), 'FORCED_OUT_SHORTS': dict(share=0.0, upper=0.0, fires=20),
         'CROWDED_LATE': dict(share=None)}
    d = m.decide(S, None)
    assert d['mechanism'] == 'CANDIDATE' and d['candidate_id'] == 'FORCED_OUT' and d['share'] == 0.95, d
    d2 = m.decide(S, 0.90)
    assert d2['mechanism'] == 'FORCED_OUT', d2


def t13_liq_pct_exact():
    W, B, dp, rd = world('t13', down(10), defj=legs_def(q=95))
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN' and M['shares']['FORCED_OUT']['legs']['liq']['unknown'] == 1.0, M and M['mechanism']


def t14_reading_asof():
    f = down(10)
    rdg = [('FIRE', c, t, 'E2.S06', 0.5, t + 60) for c, t, s in f]      # known after the fire: not a reading at the fire second
    W, B, dp, rd = world('t14', f, defj=legs_def(oi=False, liq=False), readings=rdg)
    rc, out, M = run(W, B, dp, rd)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', M and M['mechanism']


def t15_window():
    f = down(10) + [('DDD', 1767312000 + 3600 * i, 1) for i in range(30)]   # up fires after the block: outside, not counted
    W, B, dp, rd = world('t15', f)
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['fires_in_block'] == 10 and M['mechanism'] == 'FORCED_OUT', M and (M['fires_in_block'], M['mechanism'])


def t16_parse_real_map():
    m = mod()
    R, thr, opn = m.parse_map(open(MAP).read())
    assert thr == 0.90, thr
    fo = R['FORCED_OUT']; fs = R['FORCED_OUT_SHORTS']
    assert fo['side'] == ('FADE', -1) and fo['liq'] == ('A1.S08', 15, 90) and fo['oi'] == ('E2.S06', '<', 10), fo
    assert fs['side'] == ('FADE', 1) and fs['liq'] == ('A1.S09', None, 90) and fs['oi'] == ('E2.S06', '<', None), fs
    assert R['CROWDED_LATE'] is None and any(o.startswith('O1') for o in opn), (R['CROWDED_LATE'], opn)


def t17_liq_code_exact():
    W, B, dp, rd = world('t17', down(10), defj=legs_def(code='A1.S09'))
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['mechanism'] == 'UNKNOWN', M and M['mechanism']
    assert M['shares']['FORCED_OUT_SHORTS']['legs']['side']['fail'] == 1.0, M['shares']['FORCED_OUT_SHORTS']   # down fires, up row


# ---------------------------------------------------------------- V1_3_3 (SCO-A172): a bundle built --from-job (kitq GRADE)
def world_kitq(name, fires, defj=None, dsha=None, def_name='defs/V1.json', onset_shift=0, touch_job=False, touch_list=False,
               variant='V1', pin_line=True):
    """the real step 17 layout (run_3 card_job_20270523/BUNDLE): BUNDLE_SOURCES has JOB and FIRE_LIST rows, no STORE_RUN, no CONTEXT.tsv;
    the GRADE job pins the DEF (VS, DEFS, DSHAS, ck before the chain); the list is detect_gm1 EVENTS.tsv (coin t side onset_t trigger
    event_id)"""
    W = os.path.join(T, 'scratch', 'mv2k_%s_%d_%d' % (name, os.getpid(), time.time_ns())); os.makedirs(W)
    B = os.path.join(W, 'BUNDLE'); os.makedirs(B)
    dp = os.path.join(W, 'DEF.json'); json.dump(defj if defj is not None else legs_def(), open(dp, 'w'), indent=1)
    ds = (dsha or '{ds}').format(ds=sha16(dp))
    jp = os.path.join(W, '9999_judge_SCOUT_GRADE_FAKE.job.sh')
    open(jp, 'w').write('# JOB fake\n# TITLE: 9999_SCOUT_GRADE_FAKE -- (KIT_V5 JOB_GRADE_V14)\nset -u\nRD=%s; J=9999_GRADE_FAKE\n'
                        'W=%s/w; DV=$RD/receipts/$J\nVS=(%s)\nDEFS=(%s)\nDSHAS=(%s)\nLEANS=(FADE)\n%s' % (
                            W, W, variant, def_name, ds,
                            'for i in "${!VS[@]}"; do ck $RD/${DEFS[$i]} ${DSHAS[$i]}; done\n' if pin_line else ''))
    lp = os.path.join(W, 'V1_FIRES_V1_LIST.tsv')
    open(lp, 'w').write('coin\tt\tside\tonset_t\ttrigger\tevent_id\n' +
                        ''.join('%s\t%d\t%d\t%d\tclaim\te%d\n' % (c, t, s, t + onset_shift, i) for i, (c, t, s) in enumerate(fires)))
    js, ls_ = sha16(jp), sha16(lp)
    if touch_job:
        open(jp, 'a').write('# edited after the bundle\n')
    if touch_list:
        open(lp, 'a').write('ZZZ\t%d\t-1\t%d\tclaim\tez\n' % (T0 + 7, T0 + 7))
    open(os.path.join(B, 'BUNDLE_SOURCES.tsv'), 'w').write(
        '# fake bundle from a kitq GRADE job\nrole\tpath\tsha16\trows\tnote\n'
        'JOB\t%s\t%s\t\trunner job file\nJOB_STATUS\t/fake/x.status\tbbbbbbbbbbbbbbbb\t\texit=0\n'
        'FIRE_LIST\t%s\t%s\t%d\tthe grade input (coin t side)\n'
        'MONEY\t\t\t0\ta kitq GRADE is a race grade\n' % (jp, js, lp, ls_, len(fires)))
    open(os.path.join(B, 'FIRES.tsv'), 'w').write('# fake\nalarm_id\tcoin\tt\tside\n' + ''.join('FAKE\t%s\t%d\t%s\n' % f for f in fires))
    return W, B, dp, None


def t18_kitq_bound():
    """the run_3 defect: legs equal to the map, bundle from a kitq GRADE job: old code UNKNOWN (def_bound false, 0 onsets)"""
    W, B, dp, rd = world_kitq('t18', down(10))
    rc, out, M = run(W, B, dp)
    assert rc == 0, out
    assert M['def_bound'] is True and M['detector_onsets_asof'] == 10, (M['def_bound'], M['detector_onsets_asof'])
    assert M['mechanism'] == 'FORCED_OUT' and M['shares']['FORCED_OUT']['share'] == 1.0, (M['mechanism'], M['shares']['FORCED_OUT'])
    L = M['shares']['FORCED_OUT']['legs']
    assert L['liq']['hold'] == 1.0 and L['oi']['hold'] == 1.0, L
    assert M.get('binding') == 'KITQ_GRADE_JOB', M.get('binding')


def t19_kitq_job_changed():
    W, B, dp, rd = world_kitq('t19', down(10), touch_job=True)
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is False and M['mechanism'] == 'UNKNOWN', (out, M and M['def_bound'])


def t20_kitq_list_changed():
    W, B, dp, rd = world_kitq('t20', down(10), touch_list=True)
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['detector_onsets_asof'] == 0 and M['mechanism'] == 'UNKNOWN', (out, M and M['detector_onsets_asof'])


def t21_kitq_given_list_not_detector():
    W, B, dp, rd = world_kitq('t21', down(10), def_name='lists/V1.tsv')     # a given list: no detector ran on the DEF
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is False and M['mechanism'] == 'UNKNOWN', (out, M and M['def_bound'])


def t22_kitq_onset_not_t():
    W, B, dp, rd = world_kitq('t22', down(10), onset_shift=-60)
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['detector_onsets_asof'] == 0 and M['mechanism'] == 'UNKNOWN', (out, M and M['detector_onsets_asof'])


def t23_kitq_other_def():
    W, B, dp, rd = world_kitq('t23', down(10), dsha='1111111111111111')
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is False and M['bundle_definition_sha16'] == '1111111111111111', (out, M and M['def_bound'])
    assert M['mechanism'] == 'UNKNOWN', M['mechanism']


def t24_kitq_no_pin_line():
    W, B, dp, rd = world_kitq('t24', down(10), pin_line=False)       # the job never checked the DEF before the chain
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is False, (out, M and M['def_bound'])


def t25_kitq_other_variant():
    W, B, dp, rd = world_kitq('t25', down(10), variant='V2')          # the list is V1's, the job pins V2 only
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is False, (out, M and M['def_bound'])


def t26_kitq_two_variants():
    """the job grades V2 then V1: the list's variant V1 is the second entry; its DSHAS entry binds the DEF"""
    W, B, dp, rd = world_kitq('t26', down(10), variant='V2 V1', def_name='defs/V2.json defs/V1.json', dsha='1111111111111111 {ds}')
    rc, out, M = run(W, B, dp)
    assert rc == 0 and M['def_bound'] is True and M['mechanism'] == 'FORCED_OUT', (out, M and M['def_bound'])


TESTS = [(k, v) for k, v in sorted(globals().items()) if k[:1] == 't' and k[1:3].isdigit()]


def main(a):
    sel = [(k, f) for k, f in TESTS if not a or k.split('_')[0] in a]
    ok = 0
    for k, f in sel:
        try:
            f(); ok += 1; print('PASS', k)
        except Exception as e:
            print('FAIL', k, type(e).__name__, str(e)[:300])
    print('RESULT %d of %d (tool %s)' % (ok, len(sel), TOOL))
    return 0 if ok == len(sel) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
