#!/usr/bin/env python3
"""mutants_mechanism_v2.py (SCO-A154): one mutant per rule of mechanism_v2.py; each mutant is a copy under tests/mutants/mv2_<id>/ (kept,
never deleted) with one edit, run against the one test that names the rule. KILLED = that test fails.
  python3 -B mutants_mechanism_v2.py [first last]   (1-based, inclusive)"""
import sys
sys.dont_write_bytecode = True
import os, shutil, subprocess, time

T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
M = [('mu01_side_lean', "(lean == legs['side'][0] and f['side'] == legs['side'][1])", "(f['side'] == legs['side'][1])", 't09'),
     ('mu02_side_dir', "(lean == legs['side'][0] and f['side'] == legs['side'][1])", "(lean == legs['side'][0])", 't17'),
     ('mu03_liq_q', "and p.get('q') == spec[2]", "", 't13'),
     ('mu04_liq_code', "r.get('code') == spec[0] and p.get('op')", "p.get('op')", 't17'),
     ('mu05_oi_standin', "if r.get('who') != 'FIRE' or r.get('code') != OI_CODE:", "if r.get('who') != 'FIRE' or r.get('code') not in (OI_CODE, 'CTX.oi_chg_10m'):", 't07'),
     ('mu06_asof_context', "and float(r['known_at']) <= t:\n                        onset", ":\n                        onset", 't03'),
     ('mu07_after_read', "if (r.get('after') or '').strip() != '0':", "if False:", 't02'),
     ('mu08_once', "            if k in seen:\n                dup += 1; continue", "            if False:\n                dup += 1; continue", 't04'),
     ('mu09_threshold_ge', "S[m]['share'] >= thr]", "S[m]['share'] > thr]", 't04'),
     ('mu10_unknown_as_fail', "            st['liq'] = 'hold' if (src['liq'] and det) else 'unknown'", "            st['liq'] = 'hold' if (src['liq'] and det) else 'fail'", 't05'),
     ('mu11_def_bound', "def_ok = bs is not None and bs == ds", "def_ok = True", 't10'),
     ('mu12_map_pin', "    if sha16(a.map) != MAP_PIN:", "    if False:", 't11'),
     ('mu13_candidate', "        return dict(mechanism='CANDIDATE',", "        return dict(mechanism='NONE',", 't12'),
     ('mu14_asof_readings', "if v == v and float(r['known_at']) <= t:", "if v == v:", 't14'),
     ('mu15_window', "            if not (a.first <= day(t) <= a.last):\n                continue", "            if False:\n                continue", 't15'),
     ('mu17_unknown_best', "        u = max(und, key=lambda m: (S[m]['share'], S[m]['upper'], m))", "        u = best", 't05'),
     ('mu16_map_threshold', "                thr = float(m.group(1))", "                thr = 0.5", 't16'),
     # V1_3_3 (SCO-A172): the kitq binding
     ('mu18_kitq_off', "            bs, konset, kwhy = kitq_binding(a.bundle)", "            konset, kwhy = set(), None", 't18'),
     ('mu19_kitq_onsets_dropped', "        onset |= konset\n", "", 't18'),
     ('mu20_kitq_sha_unchecked', "        if not os.path.isfile(r['path']) or sha16(r['path']) != r['sha16']:", "        if not os.path.isfile(r['path']):", 't19'),
     ('mu21_kitq_onset_eq', "            if int(float(r['onset_t'])) == t:", "            if True:", 't22'),
     ('mu22_kitq_given_list', "    if not defs[i].endswith('.json'):", "    if False:", 't21'),
     ('mu23_kitq_pin_line', " or 'ck $RD/${DEFS[$i]} ${DSHAS[$i]}' not in text:", ":", 't24'),
     ('mu24_kitq_variant', "    i = vs.index(m.group(1))", "    i = 0", 't26'),
     ('mu25_kitq_list_sha', "    for r in (jr, lr):", "    for r in (jr,):", 't20')]


def main(a):
    lo, hi = (int(a[0]), int(a[1])) if len(a) == 2 else (1, len(M))
    killed = n = 0
    for mid, old, new, test in M[lo - 1:hi]:
        d = os.path.join(T, 'mutants', 'mv2_' + mid)
        if os.path.exists(d):
            d = d + '_%d_%d' % (os.getpid(), time.time_ns())
        os.makedirs(d)
        src = open(os.path.join(HERE, 'mechanism_v2.py')).read()
        n += 1
        if src.count(old) != 1:
            print('NOT_APPLIED %s: pattern found %d times' % (mid, src.count(old))); continue
        open(os.path.join(d, 'mechanism_v2.py'), 'w').write(src.replace(old, new))
        env = dict(os.environ, MECH_V2_UNDER_TEST=os.path.join(d, 'mechanism_v2.py'))
        r = subprocess.run([sys.executable, '-B', os.path.join(T, 'test_mechanism_v2.py'), test], env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, universal_newlines=True, timeout=50)
        k = 'RESULT 0 of 1' in r.stdout
        killed += k
        print('%s %s by %s' % ('KILLED' if k else 'SURVIVED', mid, test))
    print('MUTANTS %d of %d killed' % (killed, n))
    return 0 if killed == n else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
