#!/usr/bin/env python3
"""mutants_bundle_v1.py (SCO-A136, 6 Nov 2026): one mutant per refusal and per join rule of bundle_builder_v1.py (at least one per
refusal code). Each mutant is one exact text change (it must occur exactly once) written as a copy under ../mutants/bundle_<stamp>/;
the test it must fail is run on the copy (BB_TOOL). KILLED = that test fails. The builder itself is never edited.
Usage: python3 -B mutants_bundle_v1.py [first last]   (1-based mutant numbers; all when none)"""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, os, subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.join(HERE, 'bundle_builder_v1.py')
TEST = os.path.join(HERE, 'test_bundle_v1.py')
MUTANTS = (
    ('K01_NO_JOB', 'B2', "    if not hits:\n        raise Refused('NO_JOB'", "    if False:\n        raise Refused('NO_JOB'"),
    ('K02_BAD_ARGS_jobid', 'B2', "r'\\d{4,12}'", "r'\\w{4,12}'"),
    ('K03_JOB_AMBIGUOUS', 'B2', "    if len(hits) > 1:", "    if len(hits) > 9:"),
    ('K04_NO_STATUS', 'B2', "    if not os.path.isfile(stp):\n        raise Refused('NO_STATUS'", "    if False:\n        raise Refused('NO_STATUS'"),
    ('K05_JOB_NOT_OK', 'B2', "if st.get('exit') != '0':", "if st.get('exit') == 'never':"),
    ('K06_NOT_A_GRADE_title', 'B2', "if not (title and 'JOB_GRADE_V' in title[0])", "if not (title and 'JOB_' in title[0])"),
    ('K07_NOT_A_GRADE_dv', 'B2', "or 'DV=$RD/receipts/$J' not in text:", "or 'DV=' not in text:"),
    ('K08_GRADE_NOT_DONE', 'B2', "if not ends or ends[-1].get('rc') != '0':", "if not ends:"),
    ('K09_SOURCE_CHANGED_list', 'B3', "    if sha16_file(lst) != lsha:", "    if False:"),
    ('K10_SOURCE_CHANGED_perfire', 'B3', "    if sha16_file(pf) != psha:", "    if False:"),
    ('K11_JOIN_seal_job', 'B3', "    if sj != J['J']:", "    if False:"),
    ('K12_JOIN_A_rows', 'B3', "    if A != sorted(fires):", "    if len(A) != len(fires):"),
    ('K13_JOIN_A_side', 'B3', "    if A != sorted(fires):", "    if [x[:2] for x in A] != [x[:2] for x in sorted(fires)]:"),
    ('K14_JOIN_count', 'B3', "    if len(fires) != int(n):", "    if False:"),
    ('K15_BAD_INPUT_header', 'B3', "if not L or L[0][:3] != ['coin', 't', 'side']:", "if not L:"),
    ('K16_BAD_INPUT_twice', 'B3', "        if (c, t) in seen:", "        if False:"),
    ('K17_BAD_INPUT_side', 'B3', "        if s not in (1, -1):", "        if s not in (1, -1, 0):"),
    ('K18_NO_INPUT_list', 'B3', "    if not os.path.isfile(lst):\n        raise Refused('NO_INPUT'", "    if False:\n        raise Refused('NO_INPUT'"),
    ('K19_OUT_EXISTS', 'B3', "    if os.path.exists(a.out):\n        raise Refused('OUT_EXISTS'", "    if False:\n        raise Refused('OUT_EXISTS'"),
    ('K20_JOIN_MISSING', 'B4', "    if miss:\n", "    if False:\n"),
    ('K21_JOIN_EXTRA', 'B4', "    if extra:\n", "    if False:\n"),
    ('K22_BAD_INPUT_frac_t', 'B4', "    if not math.isfinite(v) or v != int(v):", "    if not math.isfinite(v):"),
    ('K23_BAD_ARGS_lab3', 'B4', "    if (a.ctx or a.epi) and not a.lab3:", "    if False:"),
    ('K24_AFTER_flag', 'B4', "[(w, c, t, code, v, k, int(k > t))", "[(w, c, t, code, v, k, int(k > t + 3600))"),
    ('K25_match_code_name', 'B4', "readings.append(('MATCH', c, t, 'CTX.%s.%s' % (subj, v), x, td[i]))", "readings.append(('MATCH', c, t, 'CTX.%s.%s' % (a.ctx_match, v), x, td[i]))"),
    ('K26_block_span', 'B4', "o = readers['ctx'](root, a.lab3, subj, first, last, vals)", "o = readers['ctx'](root, a.lab3, subj, 20250901, last, vals)"),
    ('K27_forced_side', 'B5', "lg, sh = (fu, ou) if side_of[(c, t)] == -1 else (ou, fu)", "lg, sh = (fu, ou) if side_of[(c, t)] == 1 else (ou, fu)"),
    ('K28_other_zero_none', 'B5', "ou = (0.0 if ov == 0 else 10.0 ** ov)", "ou = (10.0 ** ov)"),
    ('K29_JOIN_SIDE', 'B6', "        if bad:\n            raise Refused('JOIN_SIDE'", "        if False:\n            raise Refused('JOIN_SIDE'"),
    ('K30_BAD_ARGS_exit', 'B6', "        if key not in D.P:", "        if key is None:"),
    ('K31_money_net_lean', 'B6', "key = (a.money_exit, a.lean, 'HONEST')", "key = (a.money_exit, 'FADE', 'HONEST')"),
    ('K32_money_edge', 'B6', "float(X[i] - Tt[i])))", "float(Tt[i])))"),
    ('K33_closed_drop', 'B7', "        if A.closed_reason(A.day_of(t), R.LAW.research_refusal, closed_from):", "        if False:"),
    ('K34_BLOCK_CLOSED_first', 'B7', "    first, last, months = A.check_block(a.block, R.LAW.research_refusal, closed_from)", "    first, last, months = A.block_span(a.block)"),
    ('K35_TRUE_perfire', 'B8', "        if T[0].get('perfire_sha16') != G['perfire_sha16']:", "        if False:"),
    ('K36_TRUE_def', 'B8', "        if T[0].get('def_sha16') != a.def_sha16:", "        if False:"),
    ('K37_BAD_ARGS_true_def', 'B8', "    if a.true_row and not a.def_sha16:", "    if False:"),
    ('K38_NOT_BUILT_dims', 'B8', "    if a.dims:\n        raise Refused('NOT_BUILT'", "    if False:\n        raise Refused('NOT_BUILT'"),
    ('K39_cli_refused_rc', 'B9', "            return 2\n        print('FAILED", "            return 0\n        print('FAILED"),
)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def main(argv):
    lo, hi = (int(argv[0]), int(argv[1])) if len(argv) == 2 else (1, len(MUTANTS))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = os.path.join(os.path.dirname(HERE), 'mutants', 'bundle_%s_%d_%d' % (stamp, lo, hi))
    os.makedirs(out)
    src = open(TOOL).read()
    print('date -u %s; builder %s sha16 %s; test sha16 %s; mutants %d..%d of %d' % (stamp, TOOL, sha16(TOOL), sha16(TEST), lo, hi, len(MUTANTS)))
    base = subprocess.run([sys.executable, '-B', TEST], capture_output=True, text=True, timeout=300)
    print('BASELINE (unmutated) rc %d: %s' % (base.returncode, base.stdout.strip().splitlines()[-1]))
    killed = tried = 0
    for k, (name, test, old, new) in enumerate(MUTANTS, 1):
        if not lo <= k <= hi:
            continue
        tried += 1
        if src.count(old) != 1:
            print('%s NOT APPLIED: the text occurs %d times' % (name, src.count(old)))
            continue
        p = os.path.join(out, name + '.py')
        open(p, 'x').write(src.replace(old, new))
        env = dict(os.environ, BB_TOOL=p, AU_TOOL=os.path.join(HERE, 'alarm_understand_v1.py'))
        r = subprocess.run([sys.executable, '-B', TEST, test], capture_output=True, text=True, timeout=300, env=env)
        fail = [l for l in r.stdout.splitlines() if l.startswith('FAIL')]
        ok = r.returncode != 0 and bool(fail)
        killed += ok
        print('%s %s by %s: %s' % (name, 'KILLED' if ok else 'SURVIVED', test, (fail[0] if fail else (r.stdout.strip().splitlines() or ['no output: ' + r.stderr.strip()[-160:]])[-1])[:260]))
    print('RESULT %d of %d mutants killed (baseline rc %d)' % (killed, tried, base.returncode))
    return 0 if killed == tried and base.returncode == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
