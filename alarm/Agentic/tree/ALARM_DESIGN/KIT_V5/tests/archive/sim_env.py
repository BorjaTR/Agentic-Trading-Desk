"""sim_env.py: builds a sandbox that mirrors the Mac and VM trees for KIT_V5 tests (stub tools, fake runner, fake allocator)."""
import os, sys, json, hashlib, shutil, stat, textwrap

KIT5 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL = '<VM_UPLOADS>/uploads/dev/_scratch_scout/kit5_test'
HDR = {
 'VARIANTS': ['utc', 'idea', 'V', 'lean', 'def_rel', 'def_sha16', 'prereg_rel', 'prereg_sha16', 'reason'],
 'FORECASTS': ['utc', 'idea', 'V', 'scope', 'gap15_lo', 'gap15_hi', 'gap1h_lo', 'gap1h_hi', 'file_rel', 'file_sha16', 'note'],
 'RUNS': ['utc_queued', 'job', 'job_sha16', 'kind', 'idea', 'variants', 'queue', 'prereg_rel', 'prereg_sha16', 'writes_mb', 'mem_mb', 'minutes', 'template_sha16', 'from_job', 'receipts_rel'],
 'DECISIONS': ['utc', 'idea', 'V', 'state', 'label_rule', 'r1', 'r2', 'months_counted', 'months_passing', 'waves', 'lead_15m', 't_15m', 'lead_1h', 't_1h', 'gate_handoff', 'clear', 'clear_at', 'price_gate', 'tough_15m', 'tough_1h', 'money_tt', 'money_rr', 'grade_job', 'entry_job', 'sources', 'note'],
 'POSTMORTEMS': ['utc', 'idea', 'V', 'job', 'scope', 'forecast', 'result', 'result_file', 'result_sha16', 'why', 'unexplained'],
 'LEARNINGS_PROPOSED': ['utc', 'id', 'kind', 'section', 'change', 'evidence_file', 'evidence_sha16', 'scope', 'status'],
 'PROBLEMS': ['utc', 'kind', 'where', 'what_is_wrong', 'evidence', 'severity', 'action', 'proposed_fix', 'reported_to_lead'],
 'TOOLS_BUILT': ['utc', 'tool_rel', 'sha16', 'range', 'test_rel', 'test_sha16', 'why'],
}

def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]

def w(p, s, mode=0o644):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w').write(s); os.chmod(p, mode)

STUB_CHAIN = r'''#!/bin/bash
V=$1; DEF=$2; W=$3; mkdir -p $W
case "$V" in *FAIL*) printf 'step\trc\nlist\t0\ndone\t4\n' > $W/STATUS_$V.tsv; exit 4;; esac
printf 'step\trc\tseconds\tout\tutc\nlist\t0\t0\tx\tu\ndone\t0\t0\tx\tu\n' > $W/STATUS_$V.tsv
echo "CARD $V lean $LEAN" > $W/CARD_$V.txt; printf 'key\tvalue\na\t1\n' > $W/SUM_$V.tsv; echo "inputs $DEF" > $W/INPUTS_$V.txt; echo menu > $W/MENU_${V}_om.txt
printf 'coin\tt\tside\nBTC\t1757500000\t1\nETH\t1757503000\t-1\nSOL\t1760000000\t1\n' > $W/${V}_FIRES_V1_LIST.tsv
exit 0
'''
STUB_PERFIRE = 'import sys,os\nW,V=sys.argv[1:3]\nopen(os.path.join(W,"PERFIRE_%s.tsv"%V),"w").write("kind\\tday\\n")\n'
STUB_OK = 'print("OK all tests passed")\n'
STUB_LEADNULL = r'''import sys, os, csv
a = sys.argv[1:]; mf = a[a.index('--manifest') + 1]; out = a[a.index('--out') + 1]
os.makedirs(out); os.makedirs(os.path.join(out, 'REAL_SEALED'))
rows = list(csv.DictReader(open(mf), delimiter='\t'))
S = open(os.path.join(out, 'SUMMARY.tsv'), 'x'); S.write('# stub SUMMARY\nV\tlean\tstatus\tgate\twaves\tmonths_counted_any\n')
for r in rows:
    V = r['V']; k = V[0]
    r1, r2, cnt = {'P': ('PASS', 'PASS', 4), 'N': ('PASS', 'no', 4), 'S': ('no', 'no', 4), 'I': ('no', 'no', 2)}.get(k, ('no', 'no', 4))
    gate = 'GATE_FAIL' if k == 'G' else 'PASS'
    S.write('%s\t%s\tOK\t%s\t1223\t%d\n' % (V, r['lean'], gate, cnt))
    open(os.path.join(out, 'REAL_SEALED', 'REAL_RULES_%s.tsv' % V), 'x').write('# stub\nkey\tvalue\nR1\t%s\nR2\t%s\ncounted\t%d\nneed\t3\npassing\t%d\n' % (r1, r2, cnt, 4 if r1 == 'PASS' else 1))
    open(os.path.join(out, 'REAL_SEALED', 'REAL_%s.tsv' % V), 'x').write('# stub\nhorizon\twaves\tdays\tlead\tse\tt\n15m\t1223\t105\t3.6297\t1.8999\t1.9105\n1h\t1223\t105\t7.4680\t2.0252\t3.6875\n')
    open(os.path.join(out, 'RESULTS_%s.tsv' % V), 'x').write('# stub\n')
S.close(); print('stub lead_null done')
'''
STUB_DETECT = r'''import sys, os
a = sys.argv[1:]; out = a[a.index('--out') + 1]; coins = a[a.index('--coins') + 1].split(',')
os.makedirs(out)
rows = []
half_a = 'BTC' in coins
for i in range(40):
    t = 1757462400 + i * 7200 * 7 + (0 if half_a else (1000 if i % 2 == 0 else 3000))
    rows.append('%s\t%d\t1' % (coins[i % len(coins)], t))
open(os.path.join(out, 'EVENTS.tsv'), 'w').write('# stub detect\ncoin\tt\tside\n' + '\n'.join(rows) + '\n')
print('stub detect done', len(rows))
'''
STUB_STORE = r'''#!/bin/bash
AID=$1; FIRST=$2; LAST=$3; EV=$4; EVSHA=$5; RDEF=$6; RCARD=$7; RFAM=$8
[ -f "$F/$RDEF" ] || { echo "NO DEF $F/$RDEF"; exit 2; }
[ -f "$F/$RCARD" ] || { echo "NO CARD $F/$RCARD"; exit 2; }
C=$WDB/judge_scratch/work_TOOLTRIAL/chain/${AID}_${FIRST}_${LAST}_STAMP1; D=$WDB/judge_scratch/work_ALARMLIB/i2g_v3_2/full_${AID}_${FIRST}_${LAST}_STAMP1
mkdir -p $C $D/run; echo '{}' > $D/run/RUN.json; echo u > $D/UNIVERSE.tsv
printf 'step\trc\tseconds\tout\ngrader_store\t0\t1\t%s\n' $D/run > $C/STATUS.tsv; echo store ok
'''
STUB_MARKOUT = r'''import sys, os, shutil
a = sys.argv[1:]; out = a[a.index('--out') + 1]; os.makedirs(out)
R = os.environ['SIM_REAL']
for x in ('CURVE.tsv', 'GATES.json', 'TABLE_W0.tsv'):
    shutil.copy(os.path.join(R, 'DP2_' + x), os.path.join(out, x))
print('stub markout done')
'''
STUB_MONTHREAD = 'import sys\nprint("%s month %s"%(sys.argv[2],sys.argv[3]))\nprint("  VERDICT HELD ranges", sys.argv[6] if len(sys.argv)>6 else "none")\n'

def build(root):
    """root/dev = <DEV> and $HOME/mnt/dev; root/WDB = <SCRATCH_DISK>; returns paths and the sha map stub->real"""
    dev = os.path.join(root, 'dev'); wdb = os.path.join(root, 'WDB')
    FR = os.path.join(dev, 'TradingPlatform_repo/volat-agent/forensics'); FV = os.path.join(dev, 'TradingPlatform/volat-agent/forensics')
    R = os.path.join(FR, 'team/RESEARCH'); H = os.path.join(R, 'ALARM_DESIGN'); T1 = os.path.join(H, 'runs/CLAUDE1_20261028/tools')
    AP = os.path.join(R, 'tools/alarm_process'); L2 = os.path.join(R, 'LEAD/loop2'); TL = os.path.join(R, 'tools'); X = os.path.join(R, 'tools/markout')
    os.makedirs(wdb, exist_ok=True)
    py = os.path.join(dev, 'venvs/analyst/bin/python3'); os.makedirs(os.path.dirname(py), exist_ok=True)
    if not os.path.exists(py): os.symlink(sys.executable, py)
    shamap = {}
    def tool(path, body, real, mode=0o644):
        w(path, body, mode); shamap[real] = sha16(path)
    tool(os.path.join(AP, 'alarm_grade_chain_v2_0_to20251231.sh'), STUB_CHAIN, '94273faf1e927ddc', 0o755)
    tool(os.path.join(AP, 'alarm_grade_chain_v2_1_to20260430.sh'), STUB_CHAIN.replace('#!/bin/bash', '#!/bin/bash\n# v2_1'), '99e8a229617cb2e2', 0o755)
    tool(os.path.join(R, 'tools/month_parts/alarm_grade_chain_v2_2_to20260430.sh'), STUB_CHAIN.replace('#!/bin/bash', '#!/bin/bash\n# v2_2 (26 coin parts; PARTS from the env)'), 'fc167d9273d172ab', 0o755)
    tool(os.path.join(AP, 'alarm_card_v1_2.py'), '# card 1_2\n', 'c3172f94e389cadb'); tool(os.path.join(AP, 'alarm_card_v1_3.py'), '# card 1_3\n', 'a616c4378a02852b')
    tool(os.path.join(T1, 'perfire_v1_to20260430.py'), STUB_PERFIRE, '59a865d0127d1482'); tool(os.path.join(T1, 'test_perfire_v1.py'), STUB_OK, '12996df3af189030')
    tool(os.path.join(T1, 'lead_null_v1_to20251231.py'), STUB_LEADNULL, '63fe4fbdd283a777')
    tool(os.path.join(T1, 'month_read_v3.py'), STUB_MONTHREAD, 'b3480cfd670b28f4'); tool(os.path.join(T1, 'conditions_v1.py'), 'print("conditions stub")\n', '2f4aaebe1f259278')
    tool(os.path.join(T1, 'split_v1.py'), '# split stub\n', 'e481ca008c72d6f5')
    tool(os.path.join(T1, 'run_alarm_store_v10_3_noladder.sh'), STUB_STORE, '887dc80bbf72f655', 0o755)
    tool(os.path.join(X, 'markout_v1_1.py'), STUB_MARKOUT, '3239e4685080894e'); tool(os.path.join(X, 'test_markout_v1_1.py'), STUB_OK, '5ff4d0940bc1646c')
    tool(os.path.join(X, 'test_markout_v1.py'), STUB_OK, 'dd91de15f8e5e824'); tool(os.path.join(X, 'settings/SETTINGS_V1.json'), '{}\n', '495b6e45b8fa7a81')
    tool(os.path.join(TL, 'idea_to_grade/detect.py'), STUB_DETECT, '5ced7c1a40356a7f')
    tool(os.path.join(FR, 'team/OUTSIDE/COORD/development/DEV2/a02p_chain_v1/full_population/ROSTER_BUILD.json'), json.dumps({'coins': ['BTC', 'ETH', 'SOL', 'XRP']}), 'b93de33b2a73a56e')
    tool(os.path.join(L2, 'defs/METRIC_TRAPS_PLUS_HL_OWNER_LOOP2_V1.tsv'), 'x\n', '5383a6bfe4d62680')
    tool(os.path.join(TL, 'alarm_context/CTX_CATALOG_V1.tsv'), 'x\n', 'f413906feb40c0b4'); tool(os.path.join(TL, 'alarm_profile/EPI_CATALOG_V1.tsv'), 'x\n', 'd133fea9c7935857')
    tool(os.path.join(FR, 'team/LAB3/METRICS_HL_ADD_V1.tsv'), 'x\n', 'd81727de54e5a5db'); tool(os.path.join(L2, 'defs/METRICS_HL_OWNER_CLEARED_LOOP2_V1.tsv'), 'x\n', 'f19ccfbf08c9a5b4')
    for f in ('reg_append_v1.py', 'read_stratentry_v1.py'):
        os.makedirs(T1, exist_ok=True); shutil.copy(os.path.join(REAL, f), os.path.join(T1, f))
    for k in ('COUNT', 'GRADE', 'ENTRY', 'MONTH', 'CLEAN'):
        d = os.path.join(H, 'KIT_V5/jobs'); os.makedirs(d, exist_ok=True)
        shutil.copy(os.path.join(KIT5, 'jobs', 'JOB_%s_V5.job.sh.txt' % k), d)
    d = os.path.join(H, 'KIT_V5/tools'); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(KIT5, 'tools', 'clean_scratch_v1.py'), d)
    runner = os.path.join(FV, 'orch1_20260817/runner')
    for i in range(1, 22):
        for s in ('IN', 'RUN'):
            os.makedirs(os.path.join(runner, 'Q_V%d' % i, s), exist_ok=True)
    alloc = os.path.join(root, 'alloc.py')
    w(alloc, 'import sys,os\np=os.path.join(os.path.dirname(os.path.abspath(__file__)),"alloc.n")\nn=int(open(p).read()) if os.path.exists(p) else 20269000\nn+=1\nopen(p,"w").write(str(n))\nprint(n)\n')
    os.makedirs(os.path.join(H, 'runs/IDEAS_CLAIMED'), exist_ok=True)
    return dict(dev=dev, wdb=wdb, FR=FR, FV=FV, H=H, T1=T1, runner=runner, alloc=alloc, shamap=shamap, hb=os.path.join(FR, 'hb'))

def new_run(env, runtag):
    run = os.path.join(env['H'], 'runs', runtag)
    for n, h in HDR.items():
        w(os.path.join(run, 'registers', n + '.tsv'), '\t'.join(h) + '\n')
    return run

def run_job(env, twin, extra_env=None):
    """execute a filled job with Mac paths mapped into the sandbox; pins re-pointed to the stubs"""
    import subprocess
    s = open(twin).read()
    s = s.replace('<DEV>', env['dev']).replace('<SCRATCH_DISK>', env['wdb'])
    for real, stub in env['shamap'].items():
        s = s.replace(' ' + real, ' ' + stub)
    s = s.replace('df -m %s' % env['wdb'], "printf 'Filesystem\\nx x x %s\\n'" % (extra_env or {}).get('FREE_MB', '200000'))
    p = twin + '.sim.sh'; open(p, 'w').write(s)
    e = dict(os.environ); e['SIM_REAL'] = REAL; e['WDB'] = env['wdb']
    e['F'] = os.path.join(env['dev'], 'TradingPlatform_repo/volat-agent/forensics')
    if extra_env: e.update(extra_env)
    r = subprocess.run(['bash', p], capture_output=True, text=True, env=e)
    import glob
    for fp in glob.glob(os.path.join(env['dev'], 'TradingPlatform_repo/volat-agent/forensics/team/RESEARCH/ALARM_DESIGN/runs/*/receipts/*/FIRES.tsv')):
        t = open(fp).read()
        if env['wdb'] in t:
            open(fp, 'w').write(t.replace(env['wdb'], '<SCRATCH_DISK>'))
    return r
