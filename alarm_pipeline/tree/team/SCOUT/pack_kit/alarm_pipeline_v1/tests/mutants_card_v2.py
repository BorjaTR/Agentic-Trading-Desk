#!/usr/bin/env python3
"""mutants_card_v2.py (SCO-A170, V1_3_2): planted faults on the changed lines of card_v2.py (hypothesis at CLAIM from the meta json).
Each mutant is a copy under <scratch>/mc2_<id>/ (kept, never deleted) with one edit; the whole test_card_v2.py suite runs on it with
CARD_V2_UNDER_TEST; KILLED = the named test prints FAIL. The unpatched copy must pass every test first.
  python3 -B mutants_card_v2.py [scratch dir (default tests/mutants)]"""
import sys
sys.dont_write_bytecode = True
import os, subprocess, time

T = os.path.dirname(os.path.realpath(__file__)); HERE = os.path.dirname(T)
M = [('mc01_old_order', "share, claim_hypothesis(meta)),", "share, M.get('hypothesis', meta.get('hypothesis', '-'))),", 'c5_claim_from_meta_not_null_result'),
     ('mc02_result_json', "share, claim_hypothesis(meta)),", "share, claim_hypothesis(M)),", 'c6_claim_never_the_result'),
     ('mc03_no_none_guard', "    return '-' if h is None or str(h).strip() == '' else str(h)", "    return str(h)", 'c7_no_claim_value_is_dash'),
     ('mc04_result_fallback', "    h = meta.get('hypothesis')\n", "    h = meta.get('hypothesis') or 'FORCED_OUT'\n", 'c7_no_claim_value_is_dash')]


def run(tool):
    ac = os.environ.get('CARD_V1_ALARM_CARDS', os.path.realpath(os.path.join(HERE, '..', '..', '..', 'RESEARCH', 'PLAYGROUND', 'tools',
                                                                'PG20261105_alarm_understand', 'code', 'alarm_cards_v1.py')))
    env = dict(os.environ, CARD_V2_UNDER_TEST=tool, CARD_V1_ALARM_CARDS=ac)   # a mutant copy lives elsewhere: pin the real side_hits
    return subprocess.run([sys.executable, '-B', os.path.join(T, 'test_card_v2.py')], env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, universal_newlines=True, timeout=120).stdout


def main(a):
    sd = a[0] if a else os.path.join(T, 'mutants')
    src = open(os.path.join(HERE, 'card_v2.py')).read()
    base = run(os.path.join(HERE, 'card_v2.py'))
    if 'RESULT 7 of 7' not in base:
        print('UNPATCHED NOT GREEN\n' + base); return 1
    print('UNPATCHED GREEN 7 of 7')
    killed = n = 0
    for mid, old, new, test in M:
        d = os.path.join(sd, 'mc2_%s_%d_%d' % (mid, os.getpid(), time.time_ns())); os.makedirs(d)
        n += 1
        if src.count(old) != 1:
            print('NOT_APPLIED %s: pattern found %d times' % (mid, src.count(old))); continue
        p = os.path.join(d, 'card_v2.py'); open(p, 'w').write(src.replace(old, new))
        out = run(p)
        ran = all(('PASS ' + c) in out for c in ('c1_version_column_v2', 'c2_eight_columns_kept', 'c4_v1_json_version'))
        k = ('FAIL ' + test) in out and ran   # the untouched tests still pass: the copy itself ran
        killed += k
        print('%s %s by %s' % ('KILLED' if k else 'SURVIVED', mid, test))
    print('MUTANTS %d of %d killed' % (killed, n))
    return 0 if killed == n else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
