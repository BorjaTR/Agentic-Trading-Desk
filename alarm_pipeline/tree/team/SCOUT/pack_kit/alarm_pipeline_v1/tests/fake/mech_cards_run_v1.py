#!/usr/bin/env python3
"""FAKE own-shell tools for the pipeline tests (planted world only); the tool is argv[1] (the file name this is linked as)."""
import json, os, re, shutil, sys
W = os.environ['FAKE_WORLD']; F = json.load(open(os.path.join(W, 'FAKE.json')))
tool = os.path.basename(sys.argv[0]).replace('.py', ''); a = sys.argv[1:]
rc = F.get('rc', {}).get(tool, 0)
if tool == 'tried_search_v1':
    print('VERDICT NEW DEF' if '--def' in a else 'VERDICT WORDS ONLY'); print('  hit A01'); sys.exit(rc)
if tool == 'menu_gate_v1':
    print(F.get('menu', 'MENU GATE V1.json: OK, 2 codes read')); sys.exit(rc)
if tool == 'decide_v6':
    print(F['decide']); print('SOURCES grade %s: SUMMARY x' % a[a.index('--grade') + 1])
    if '--write' in a:
        print('WRITTEN now DECISIONS')
    sys.exit(rc)
if tool == 'claim_fill_v1':
    c = a[a.index('--claim') + 1]; g = a[a.index('--grade') + 1]
    s = open(os.path.join(g, 'PERFIRE_SEAL.tsv')).read().split()[1]
    j = json.load(open(c)); j['perfire_sha16'] = F.get('fill_sha', s)
    json.dump(j, open(c, 'w'), indent=1, sort_keys=True); print('FILLED perfire_sha16 %s' % s); sys.exit(rc)
if tool == 'add_row':
    reg = a[0]; kv = dict(x.split('=', 1) for x in a[1:])
    h = open(reg).readline().rstrip('\n').split('\t')
    open(reg, 'a').write('\t'.join(kv.get(k, '') for k in h) + '\n'); print('added %s to %s' % (kv['id'], reg)); sys.exit(rc)
if tool == 'reg_append_v1':
    rd = a[0]; open(os.path.join(rd, 'registers', 'VARIANTS.tsv'), 'a').write(F['variants_row'] + '\n'); print('VARIANTS appended'); sys.exit(rc)
if tool == 'job_alloc':
    c = os.path.join(W, 'counter'); n = int(open(c).read()) + 1 if os.path.exists(c) else 30000001
    open(c, 'w').write(str(n)); print(n); sys.exit(rc)
if tool == 'alarm_understand_v1':
    out = a[1]; os.makedirs(out)
    shutil.copyfile(os.path.join(W, 'fix', 'CARD', 'FIRES.tsv'), os.path.join(out, 'FIRES.tsv')); print('BUNDLE ok'); sys.exit(rc)
if tool == 'mech_cards_run_v1':
    out = a[0]; m = a[a.index('--mechanism') + 1]; os.makedirs(out)
    shutil.copytree(os.path.join(W, 'fix', 'CARD', 'RD'), os.path.join(out, 'RD_%s_SEPDEC' % m))
    shutil.copytree(os.path.join(W, 'fix', 'CARD', 'RD'), os.path.join(out, 'RD_%s_SEPMAR' % m))   # SCO-A179: the SEPMAR block of ALARM_PIPELINE_V1_4
    for ext in ('tsv', 'md'):
        t = open(os.path.join(W, 'fix', 'CARD', 'CARDS.' + ext)).read().replace('@ALARM@', m)
        open(os.path.join(out, 'ALARM_CARDS_%s.%s' % (m, ext)), 'w').write(t)
    print('STEPS ok'); sys.exit(rc)
print('fake: unknown tool %s' % tool); sys.exit(2)
