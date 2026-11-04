"""mutants_v1.py: each mutant breaks one guard; the test suite must fail on every one (run from the scratchpad)."""
import os, shutil, subprocess, sys, tempfile
K = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
M = [
 ('tools/queue_job_v4.py', "if len(tries) > 3:", "if len(tries) > 99:"),
 ('tools/queue_job_v4.py', "if kind != 'CLEAN' and len(mine) >= limit:", "if False:"),
 ('tools/queue_job_v4.py', "if rr.returncode != 0 or 'RUNS' not in rr.stdout:", "if False:"),
 ('tools/queue_job_v4.py', "if hm >= 2320 or hm < 15:", "if hm >= 2330:"),
 ('tools/queue_job_v4.py', "if fm < CFG['MIN_FREE_MB'] + wmb:", "if fm < CFG['MIN_FREE_MB']:"),
 ('tools/queue_job_v4.py', "if rules.get('R1') != 'PASS':", "if False:"),
 ('tools/queue_job_v4.py', "if kind != 'CLEAN' and not os.path.isfile(claim):", "if False:"),
 ('tools/queue_job_v4.py', "if now.hour * 60 + now.minute + mins > 23 * 60 + 30 and hm >= 15:", "if False:"),
 ('tools/queue_job_v4.py', "if sha16(os.path.join(run, rel)) != fr.get('file_sha16'):", "if False:"),
 ('tools/decide_v1.py', "elif rules.get('R1') != 'PASS':", "elif rules.get('R2') != 'PASS':"),
 ('tools/decide_v1.py', "if srow.get('gate') != 'PASS':", "if False:"),
 ('tools/decide_v1.py', "int(num(rules.get('counted')) if rules.get('counted') else 0) < 3", "int(num(rules.get('counted')) if rules.get('counted') else 0) < 2"),
 ('tools/board_line_v1.py', "if len(line) >= LIMIT:", "if False:"),
 ('jobs/JOB_GRADE_V5.job.sh.txt', '[ $f -lt 60000 ]; then st disk_$V 7', '[ $f -lt 6 ]; then st disk_$V 7'),
 ('jobs/JOB_GRADE_V5.job.sh.txt', 'ck $RD/@@PREREG_REL@@ @@PREREG_SHA@@', 'true'),
 ('jobs/JOB_COUNT_V5.job.sh.txt', 't-prev>1800', 't-prev>18000'),
 ('tools/audit_run_v2.py', "if str(d.get(k, '')) != r.get(k, ''):", "if False:"),
 ('tools/clean_scratch_v1.py', "if not (ok_chain or ok_run):", "if False:"),
 ('tools/clean_scratch_v1.py', "if want and sha16(src) != want:", "if False:"),
 ('tools/clean_scratch_v1.py', "r = copy_keep(src, dst)", "r = 'skipped'"),
 ('tools/queue_job_v4.py', "if used + wmb > CFG['RUN_BUDGET_MB']:", "if False:"),
 ('tools/queue_job_v4.py', "if j in pending:", "if False:"),
 ('tools/queue_job_v4.py', "if miss:\n                raise Refused('%s: NOT DECIDED YET %s (decide_v1.py --write first)' % (j, miss))", "if False:\n                pass"),
 ('tools/queue_job_v4.py', "if not (str(w.get('first', '99999999')) <= '20250910' and str(w.get('last', '0')) >= '20260430'):", "if False:"),
 ('tools/audit_run_v2.py', "if lag > 20:", "if lag > 2000:"),
 ('tools/queue_job_v4.py', "        elif not js:\n            return c\n", "        if not js:\n            return c\n"),
 ('tools/queue_job_v4.py', "    return all(any(x[0] == s and len(x) > 1 and x[1] == '0' for x in rows) for s in need)", "    return True"),
 ('tools/queue_job_v4.py', "    if not receipts_rel or not os.path.isfile(p):\n        return None", "    if not receipts_rel or not os.path.isfile(p):\n        return False"),
 ('tools/queue_job_v4.py', "if v not in dec and stage_ok(run, r.get('receipts_rel'), v, 'GRADE') is not False]", "if v not in dec and stage_ok(run, r.get('receipts_rel'), v, 'GRADE') is not None]"),
 ('tools/audit_run_v2.py', " and not (n == 'RUNS' and r.get('kind') == 'CLEAN')", ""),
 ('tools/queue_job_v4.py', "max(1000, 300 * int(math.ceil", "max(2000, 1000 * int(math.ceil"),
 ('tools/board_line_v1.py', "            except FileExistsError:\n                k += 1", "            except ZeroDivisionError:\n                k += 1"),
 ('tools/audit_run_v2.py', "if 'does not exist' in t.lower():", "if False:"),
 ('tools/audit_run_v2.py', "if lim and used > lim:", "if False:"),
 ('tools/audit_run_v2.py', "if not (prob and stuck):", "if False:"),
 ('tools/audit_run_v2.py', "if not os.path.isfile(p) or sha16(p) != r.get('prereg_sha16'):", "if False:"),
]
bad = 0
for i, (f, a, b) in enumerate(M):
    d = tempfile.mkdtemp(prefix='k5mut_'); shutil.copytree(K, os.path.join(d, 'kit5'))
    p = os.path.join(d, 'kit5', f); s = open(p).read()
    assert s.count(a) == 1, (f, a)
    open(p, 'w').write(s.replace(a, b))
    r = subprocess.run([sys.executable, '-W', 'ignore', '-B', os.path.join(d, 'kit5/tests/test_kit5_tools.py')], capture_output=True, text=True, timeout=600)
    caught = r.returncode != 0
    bad += not caught
    print('mutant %2d %-32s %s' % (i + 1, f, 'CAUGHT' if caught else 'MISSED  <-- ' + a))
print('missed', bad, 'of', len(M))
