"""test_fairness_bar_v2_review03 (TEST1, 23 Oct 2026, PAPER; ASK STRATEGY-130408): one planted case per fairness_bar MUST of SKEPTIC
REVIEW 03 (03-09 to 03-14, + SHOULD 03-19) as SCOUT ruled them in README V1.5 section 1h, against fairness_bar_v2.py through its public
calls (bar with planted tries and receipts; read_receipt; families_of; sr_star_flips). Mutants: run_teeth_v2_review03.py.
  cd tools/fairness_bar/tests && TMPDIR=<SCRATCH>/work_TEST1/tmp /usr/sbin/taskpolicy -b nice -n 10 \\
    <PYTHON> -m pytest -q test_fairness_bar_v2_review03.py      (FB_DIR=<copy> for a planted copy)"""
import datetime as _dt, importlib, os, sys
import numpy as np
import pytest

TESTS = os.path.dirname(os.path.abspath(__file__))
FB_DIR = os.environ.get('FB_DIR') or os.path.dirname(TESTS)
sys.path.insert(0, FB_DIR)
for k in ('fairness_bar_v2', 'fairness_bar', 'make_families_v2'):
    sys.modules.pop(k, None)
V2 = importlib.import_module('fairness_bar_v2')
FAM = os.path.join(os.path.dirname(TESTS), 'FAMILIES_V2.tsv')
FAST = dict(flips=300, day_boot=300, families_path=FAM)
T0 = 1760097600                                                      # 2025-10-10 12:00:00 UTC
WAVES_SHA = V2.ids.sha16_file(os.path.join(V2.TOOLS, 'labcore', 'waves.py'))   # the receipt names the wave module it came from


def receipt(tmp, name, vals, gap=3600, fires_per=1, days=None, dup=False, shuffle=False, bad_n=False):
    lines = ['# wave_module_sha16=%s' % WAVES_SHA, 'wave_id\tvalue\tmonth\tday\tn_fires\tfires']
    rows = []
    on_day = {}
    for i, v in enumerate(vals):                              # D11-02 (BUILD2 patch): a wave's day and month ARE its first fire's UTC date
        if days is not None:                                  # waves of one day 2000 s apart (over the 1800 s wave gap), in order
            k = on_day[days[i]] = on_day.get(days[i], -1) + 1
            t = int(_dt.datetime.strptime(days[i], '%Y%m%d').replace(tzinfo=_dt.timezone.utc).timestamp()) + 2000 * k
        else:
            t = T0 + i * gap
        f = ';'.join('BTC@%d' % (t + 60 * j) for j in range(fires_per))
        d = _dt.datetime.fromtimestamp(t, _dt.timezone.utc).strftime('%Y%m%d')
        rows.append('%s	%s	%s	%s	%d	%s' % ('w0' if (dup and i == 1) else 'w%d' % i, 'nan' if v is None else '%.6f' % v, d[:6], d,
                                                    fires_per + (1 if bad_n and i == 0 else 0), f))
    if shuffle:
        rows[0], rows[1] = rows[1], rows[0]
    p = tmp / name
    p.write_text('\n'.join(lines + rows) + '\n')
    return str(p)


def tries(*texts, pre='ask-pre'):
    out = [dict(try_utc='20261022T090000Z', text='PREREG A02P money block S2_ONESIDED', source='ledger', status='PREREG', ask_id=pre)]
    for i, t in enumerate(texts):
        out.append(dict(try_utc='20261022T1%d0000Z' % i, text=t, source='ledger', status='OK', ask_id='ask-%d' % i))
    return out


def good(n=120, mu=0.8, seed=1):
    return list(np.random.default_rng(seed).normal(mu, 1, n))


def test_V09_no_exemption_by_words():
    """03-09: 'A02P money placebo' is an A02P try (a word cannot exempt it); a tool-smoke row counts in its family unless exempted by id"""
    rows = V2.family_rows(FAM)
    f = V2.families_of(dict(text='A02P money placebo', source='ledger', ask_id='x'), rows, V2.MF.exempt_ids())
    assert 'A02P' in f and 'LABEL_CHECK' not in f, f
    g = V2.families_of(dict(text='tool-smoke A02P money run', source='ledger', ask_id='y'), rows, V2.MF.exempt_ids())
    assert 'A02P' in g and 'TOOL_CHECK' not in g, g


def test_V10_one_classifier_case_blind_and_unmapped_blocks(tmp_path):
    """03-10: lower-case 'a02p' is A02P; while the census holds an UNMAPPED try the verdict is INCOMPLETE (never PASS)"""
    rows = V2.family_rows(FAM)
    assert 'A02P' in V2.families_of(dict(text='a02p bucket proof', source='ledger', ask_id='z'), rows, V2.MF.exempt_ids())
    r = receipt(tmp_path, 'r.tsv', good())
    ok = V2.bar(r, 'ask-pre', settings=FAST, tries=tries())
    assert ok['verdict'] in ('PASS', 'FAIL')
    inc = V2.bar(r, 'ask-pre', settings=FAST, tries=tries('zebra crossing idea with no family'))
    assert inc['verdict'] == 'INCOMPLETE' and inc['unmapped'] == 1


@pytest.mark.parametrize('kw', [dict(dup=True), dict(shuffle=True), dict(bad_n=True), dict(gap=600)])
def test_V11_waves_recounted_from_fires(tmp_path, kw):
    """03-11: duplicate wave ids, waves out of time order, n_fires unequal to its fires, and waves the recount would merge (fires 10 min
    apart with a 30 min gap) are each refused"""
    with pytest.raises(ValueError):
        V2.read_receipt(receipt(tmp_path, 'r.tsv', good(30), **kw))
    assert len(V2.read_receipt(receipt(tmp_path, 'ok.tsv', good(30)))) == 30


def test_V12_multiplicity_never_optional(tmp_path):
    """03-12: with 4 counted tries and no p-values the result's p is multiplied by the count (BONFERRONI), never left raw"""
    r = receipt(tmp_path, 'r.tsv', good(60, 0.35))
    one = V2.bar(r, 'ask-pre', settings=FAST, tries=tries())
    four = V2.bar(r, 'ask-pre', settings=FAST, tries=tries('A02P try a', 'A02P try b', 'A02P try c'))
    assert four['tries_counted'] == 4 and 'BONFERRONI' in four['multiplicity']
    assert abs(four['adj_p'] - min(1.0, four['p_used'] * 4)) < 1e-12 and four['adj_p'] >= one['adj_p']


def test_V13_opposite_directions_are_two_choices():
    """03-13: x and -x are two choices: their luck bar is higher than x alone; two identical tries give the same bar as one"""
    rng = np.random.default_rng(3)
    x = {'w%d' % i: float(v) for i, v in enumerate(rng.normal(0, 1, 80))}
    nx = {k: -v for k, v in x.items()}
    u = sorted(x)
    a = V2.sr_star_flips([x], u, 400, 95.0, 7)
    b = V2.sr_star_flips([x, nx], u, 400, 95.0, 7)
    c = V2.sr_star_flips([x, dict(x)], u, 400, 95.0, 7)
    assert b > a + 1e-6 and abs(c - a) < 1e-9


def test_V14_missing_values_unresolved_never_dropped(tmp_path):
    """03-14: a wave with no value is UNRESOLVED (counted, printed); over 5 pct unresolved the verdict is INCOMPLETE; the worst case is
    printed beside"""
    v = good(100)
    for i in range(0, 100, 10):
        v[i] = None
    r = V2.bar(receipt(tmp_path, 'r.tsv', v), 'ask-pre', settings=FAST, tries=tries())
    assert r['eligible_waves'] == 100 and r['unresolved_waves'] == 10 and r['verdict'] == 'INCOMPLETE'
    assert 'worst-case' in r['line'] and r['worst_case']['dsr_p'] <= r['dsr_p'] + 1e-12


def test_V19_persistent_waves_do_not_pass(tmp_path):
    """03-19 (SHOULD): 60 waves that are 4 days of 15 near-copies (one event a day) pass every per-wave test but must not PASS: the
    day-block t is the one that sees 4 events, not 60"""
    rng = np.random.default_rng(5)
    base = [0.0, 0.5, 1.5, 2.0]
    vals = [float(base[i // 15] + 0.001 * rng.normal()) for i in range(60)]
    days = ['202510%02d' % (1 + i // 15) for i in range(60)]
    r = V2.bar(receipt(tmp_path, 'r.tsv', vals, days=days), 'ask-pre', settings=FAST, tries=tries())
    assert r['t_iid'] >= 3 and r['t_day_block'] < 3, (r['t_iid'], r['t_day_block'])
    assert r['verdict'] != 'PASS'


# ---------------------------------------------------------------- OUTSIDE D11 (REVIEW_D11 a52e9cd6; ASK STRATEGY-144116)
def raw_receipt(tmp, name, rows):
    p = tmp / name
    p.write_text('\n'.join(['# wave_module_sha16=%s' % WAVES_SHA, 'wave_id\tvalue\tmonth\tday\tn_fires\tfires'] + rows) + '\n')
    return str(p)


def test_D11_01_every_matching_family_scored():
    """D11-01: a PREREG matching two families (A02P and DWAVE) is scored against EACH; the verdict is PASS only if every family passes,
    SR* is the strictest (largest) of them, every family's evidence is kept"""
    import tempfile, pathlib
    tmp = pathlib.Path(tempfile.mkdtemp(dir=os.environ.get('TMPDIR')))
    r = receipt(tmp, 'r.tsv', good(120, 0.8))
    tr = tries('A02P try a', 'A02P try b', 'A02P try c', 'DWAVE try d')
    tr[0]['text'] = 'PREREG A02P D-WAVE money block'
    out = V2.bar(r, 'ask-pre', settings=FAST, tries=tr)
    fr = out.get('family_results') or {}
    assert {'A02P', 'DWAVE'} <= set(fr), sorted(fr)
    assert out['sr_star'] == max(x['sr_star'] for x in fr.values())
    assert (out['verdict'] == 'PASS') == all(x['verdict'] == 'PASS' for x in fr.values())


def test_D11_02_day_label_must_be_the_first_fire_date(tmp_path):
    """D11-02: a receipt whose day (or month) label is not its first fire's UTC date is refused (labels cannot invent independent days)"""
    t = T0
    good_row = 'w0\t0.5\t202510\t20251010\t1\tBTC@%d' % t
    assert len(V2.read_receipt(raw_receipt(tmp_path, 'ok.tsv', [good_row]))) == 1
    for bad in ('w0\t0.5\t202510\t20251011\t1\tBTC@%d' % t, 'w0\t0.5\t202511\t20251010\t1\tBTC@%d' % t):
        with pytest.raises(ValueError):
            V2.read_receipt(raw_receipt(tmp_path, 'bad.tsv', [bad]))


def test_D11_03_unsorted_fire_times_inside_a_wave_refused(tmp_path):
    """D11-03: a wave listing t+10 then t is refused; t then t+10 is read"""
    ok = 'w0\t0.5\t202510\t20251010\t2\tBTC@%d;ETH@%d' % (T0, T0 + 10)
    bad = 'w0\t0.5\t202510\t20251010\t2\tBTC@%d;ETH@%d' % (T0 + 10, T0)
    assert len(V2.read_receipt(raw_receipt(tmp_path, 'ok.tsv', [ok]))) == 1
    with pytest.raises(ValueError):
        V2.read_receipt(raw_receipt(tmp_path, 'bad.tsv', [bad]))
