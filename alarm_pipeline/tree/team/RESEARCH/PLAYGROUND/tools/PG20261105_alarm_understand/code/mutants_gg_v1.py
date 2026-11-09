#!/usr/bin/env python3
"""mutants_gg_v1.py (SCO-A146, 6 Nov 2026): one mutant per refusal and per join rule of the --from-gg code of bundle_builder_v1.py
(at least one per refusal it raises). Each mutant is one exact text change (it must occur exactly once) written as a copy under
../mutants/gg_<stamp>/; the test it must fail (test_bundle_gg_v1.py) is run on the copy (BB_TOOL). KILLED = that test fails.
The builder itself is never edited.  Usage: python3 -B mutants_gg_v1.py [first last]"""
import sys
sys.dont_write_bytecode = True
import datetime as dt, hashlib, os, subprocess

HERE = os.path.dirname(os.path.realpath(__file__))
TOOL = os.path.join(HERE, 'bundle_builder_v1.py')
TEST = os.path.join(HERE, 'test_bundle_gg_v1.py')
MUTANTS = (
    ('G01_BAD_ARGS_one_source', 'B13', "    if bool(a.from_job) == bool(a.from_gg):", "    if False:"),
    ('G02_BAD_ARGS_runner', 'B13', "    if not a.runner:\n", "    if False:\n"),
    ('G03_NOT_BUILT_true_row', 'B13', "    if a.true_row:\n        raise Refused('NOT_BUILT'", "    if False:\n        raise Refused('NOT_BUILT'"),
    ('G04_NOT_BUILT_ctx', 'B13', "    if a.ctx or a.epi or a.ctx_match:", "    if False:"),
    ('G05_BAD_ARGS_gg_run', 'B13', "    if a.gg_run:\n        raise Refused('BAD_ARGS', '--gg-run with", "    if False:\n        raise Refused('BAD_ARGS', '--gg-run with"),
    ('G06_BAD_ARGS_money', 'B13', "    if not all((a.gg_tools, a.gg_costs, a.money_exit, a.lean)):", "    if False:"),
    ('G07_BAD_ARGS_def', 'B13', "    if not a.def_sha16:\n        raise Refused('BAD_ARGS', '--from-gg", "    if False:\n        raise Refused('BAD_ARGS', '--from-gg"),
    ('G08_BAD_ARGS_alarm_id', 'B13', "    if not a.gg_alarm_id:", "    if False:"),
    ('G09_BAD_ARGS_window', 'B13', "    if not (S['first'] <= first and last <= S['last']):", "    if False:"),
    ('G10_NOT_BUILT_gg_out', 'B13', "    if os.path.isfile(ra) and not os.path.isfile(rj):", "    if False:"),
    ('G11_NO_INPUT_run', 'B11', "    for p in (rj, pp):\n        if not os.path.isfile(p):", "    for p in (rj, pp):\n        if False:"),
    ('G12_BAD_INPUT_json', 'B11', "    except ValueError as e:\n        raise Refused('BAD_INPUT', '%s is not json", "    except KeyError as e:\n        raise Refused('BAD_INPUT', '%s is not json"),
    ('G13_BAD_INPUT_event_list', 'B11', "    if not isinstance(el, dict) or not el.get('path') or not el.get('sha16'):", "    if el is None and False:"),
    ('G14_JOIN_alarm_id', 'B11', "    if body.get('alarm_id') != alarm_id:", "    if False:"),
    ('G15_SOURCE_CHANGED_def', 'B11', "    if ds != def_sha16:", "    if False:"),
    ('G16_NO_INPUT_event_list', 'B11', "    if not os.path.isfile(ev):", "    if False:"),
    ('G17_SOURCE_CHANGED_event_list', 'B11', "    if sha16_file(ev) != esha:", "    if False:"),
    ('G18_JOIN_counts', 'B11', "    if cnt is not None and int(cnt) != len(parents):", "    if False:"),
    ('G19_BAD_INPUT_side', 'B12', "        if s not in (-1, 1):", "        if s not in (-1, 0, 1):"),
    ('G20_BAD_INPUT_twice', 'B12', "        if (c, t) in seen_p:", "        if False:"),
    ('G21_BAD_INPUT_known_at', 'B12', "        if ka <= t:", "        if ka < t:"),
    ('G22_BAD_INPUT_columns', 'B12', "    need = {'coin', 't', 'side', 'event_id', 'known_at_us'}", "    need = {'coin', 't', 'side', 'event_id'}"),
    ('G23_JOIN_EXTRA_parent', 'B12', "        if (c, t, s) not in evk:", "        if False:"),
    ('G24_JOIN_event_id', 'B12', "        if r['event_id'] != want:", "        if False:"),
    ('G25_JOIN_data_keys', 'B12', "    if gk != pk:", "    if set(gk) - set(pk):"),
    ('G26_JOIN_data_order', 'B12', "    if gk != pk:", "    if sorted(gk) != sorted(pk):"),
    ('G27_known_at_kept', 'B10', "                      float(X[i] - Tt[i]), ka, int(ka > t)))", "                      float(X[i] - Tt[i]), t, int(ka > t)))"),
    ('G28_after_marked', 'B10', "            ctxr.append((c, t, 'PARENTS', col, p['row'][col], ka, int(ka > t)))", "            ctxr.append((c, t, 'PARENTS', col, p['row'][col], ka, 0))"),
    ('G29_event_ctx_clock', 'B10', "            ctxr.append((c, t, 'EVENT_LIST', col, er[col], t, 0))", "            ctxr.append((c, t, 'EVENT_LIST', col, er[col], p['ka'], 0))"),
    ('G30_ctx_skip', 'B10', "GG_CTX_SKIP = {'coin', 't', 'side', 'event_id', 'parent_id', 'day', 'known_at_us', 'row_follow', 'row_fade'}", "GG_CTX_SKIP = {'coin', 't', 'side'}"),
    ('G31_money_lean', 'B10', "    key = (str(a.money_exit), a.lean, 'HONEST')", "    key = (str(a.money_exit), 'FOLLOW', 'HONEST')"),
    ('G32_closed_drop', 'B14', "        if bool(A.closed_reason(A.day_of(t), R.LAW.research_refusal, closed_from)):", "        if False:"),
    ('G33_BLOCK_CLOSED_first', 'B14', "    first, last, _m = A.check_block(a.block, R.LAW.research_refusal, closed_from)", "    first, last, _m = A.block_span(a.block)"),
    ('G34_not_graded_count', 'B10', "    not_graded = sum(1 for k in evk if k not in pk and first <= AU().day_of(k[1]) <= last)", "    not_graded = 0"),
    ('G35_block_count', 'B14', "    block_n = sum(1 for c, t, s in fires if first <= A.day_of(t) <= last)", "    block_n = len(fires)"),
)


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def main(argv):
    lo, hi = (int(argv[0]), int(argv[1])) if len(argv) == 2 else (1, len(MUTANTS))
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = os.path.join(os.path.dirname(HERE), 'mutants', 'gg_%s_%d_%d' % (stamp, lo, hi))
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
