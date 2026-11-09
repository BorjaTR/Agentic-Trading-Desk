#!/usr/bin/env python3
"""compare_ab_v1.py (SCO-A162R): run a vs run b of the E2E matrix. Per case: steps_done, stop code, verdict from E2E_RESULT.tsv, and every
STEP json's numbers present in either run, with the run identity aside (job ids, queues, status files, seconds, op, adoption words, run
paths, task names, card paths). Prints SAME/DIFF lines and 'SAME <k> of <n>'; exit 0 when all same.  python3 compare_ab_v1.py <a> <b> <out.tsv>"""
import sys, os, json, re
a, b, out = sys.argv[1:4]
DROP = ('job', 'job_num', 'queue', 'status_file', 'seconds', 'job_tag', 'receipts', 'file', 'card', 'index', 'card_sha16', 'line', 'cards_dir',
        'card_tsv', 'card_md', 'mechanism_json', 'id', 'row', 'op', 'opdone', 'adopted', 'refusal', 'file_log', 'decide_file', 'true_row_path', 'twin',
        'fire_list', 'mode')
VOL = re.compile(r'E2E-[A-Z0-9_]+-[0-9]+|2027[0-9]{4}|/Users/\S+|/sessions/\S+|/Volumes/\S+')
def res(d):
    R = {}
    for l in open(os.path.join(d, 'E2E_RESULT.tsv')).read().splitlines()[1:]:
        x = l.split('\t'); R[x[0]] = (x[1], x[2].split(':')[0], x[7] if len(x) > 7 else '-')
    return R
def norm(p):
    n = json.load(open(p)).get('numbers', {})
    for k in DROP:
        n.pop(k, None)
    return VOL.sub('X', json.dumps(n, sort_keys=True))
A, Bq = res(a), res(b); L = []; same = tot = 0
for c in sorted(set(A) | set(Bq)):
    tot += 1; ok = A.get(c) == Bq.get(c); same += ok
    L.append('%s\t%s\tRESULT\t%s\t%s' % ('SAME' if ok else 'DIFF', c, A.get(c), Bq.get(c)))
    fa = sorted(x for x in os.listdir(os.path.join(a, c)) if x.startswith('STEP_')) if os.path.isdir(os.path.join(a, c)) else []
    fb = sorted(x for x in os.listdir(os.path.join(b, c)) if x.startswith('STEP_')) if os.path.isdir(os.path.join(b, c)) else []
    for s in sorted(set(fa) | set(fb)):
        tot += 1
        va = norm(os.path.join(a, c, s)) if s in fa else 'MISSING'; vb = norm(os.path.join(b, c, s)) if s in fb else 'MISSING'
        ok = va == vb; same += ok
        L.append('%s\t%s\t%s\t%s\t%s' % ('SAME' if ok else 'DIFF', c, s, '' if ok else va[:300], '' if ok else vb[:300]))
open(out, 'w').write('\n'.join(L) + '\n')
for l in L:
    if l.startswith('DIFF'):
        print(l[:400])
print('SAME %d of %d' % (same, tot))
sys.exit(0 if same == tot else 1)
